#!/usr/bin/env python3
"""Every brand decision carries its reason.

The engine refuses an exemption without a `why`; the brand is held to the same
rule. brand/tokens.json is where the brand's facts are said - each colour,
typeface and radius with what it is for (`role`) and why it is what it is
(`why`), the icon with the same two, and the idea the whole look follows
(`idea`) - and the brand page is built from exactly those words. A token without its reason is a decision
nobody can question, and the page would show a swatch with nothing beside it.
So this fails:

  - a colour, typeface or radius with no `role` or no `why`;
  - a colour that is `same_as` one the tokens do not define, or that says both
    `same_as` and `value` - it is one fact or the other, never both;
  - an icon with no `role` or no `why`, set in a colour, on a ground or in a
    face the tokens do not have, or in a colour on a ground that is not one of
    the pairs checks/contrast.py holds - a letter is text, and has to read;
  - a brand with no `idea`.

WHAT IT CANNOT SEE: whether a reason is a good one. That is the owner's to
judge; this only refuses no reason at all.

Usage:  python3 checks/brand_reasons.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOKENS = ROOT / "brand/tokens.json"


def faults():
    t = json.loads(TOKENS.read_text(encoding="utf-8"))
    found = []
    if not str(t.get("idea", "")).strip():
        found.append("the brand has no `idea`: the look follows nothing anyone wrote down")
    for group in ("color", "type", "radius"):
        for name, token in t.get(group, {}).items():
            for field in ("role", "why"):
                if not str(token.get(field, "")).strip():
                    found.append(f"{group}.{name} has no `{field}`")
    for name, c in t.get("color", {}).items():
        if "same_as" in c and "value" in c:
            found.append(f"color.{name} says both `same_as` and `value`: it is one colour or the other")
        elif "same_as" in c and c["same_as"] not in t["color"]:
            found.append(f"color.{name} is the same as {c['same_as']!r}, which brand/tokens.json does not define")
    # The light scheme, paper: it says why it exists, every colour of the brand
    # is in it with why, and nothing is in it that the brand does not have.
    if "light" in t:
        if not str(t["light"].get("why", "")).strip():
            found.append("the light scheme has no `why`")
        if not t["light"].get("contrast", {}).get("pairs"):
            found.append("the light scheme declares no contrast pairs of its own (light.contrast.pairs)")
        light = t["light"].get("color", {})
        for name in t.get("color", {}):
            if name not in light:
                found.append(f"color.{name} has no value on paper: light.color.{name} is missing")
        for name, c in light.items():
            if name not in t.get("color", {}):
                found.append(f"light.color.{name} is a colour the brand does not have")
            if not str(c.get("why", "")).strip():
                found.append(f"light.color.{name} has no `why`")
            if "same_as" in c and "value" in c:
                found.append(f"light.color.{name} says both `same_as` and `value`")
            elif "same_as" in c and c["same_as"] not in light:
                found.append(f"light.color.{name} is the same as {c['same_as']!r}, which the light scheme does not define")
    icon = t.get("icon")
    if icon is not None:
        for field in ("role", "why"):
            if not str(icon.get(field, "")).strip():
                found.append(f"icon has no `{field}`")
        for field in ("color", "on"):
            if icon.get(field) not in t["color"]:
                found.append(f"icon.{field} is {icon.get(field)!r}, which brand/tokens.json does not define")
        face = t["type"].get(icon.get("type"))
        if face is None:
            found.append(f"icon.type is {icon.get('type')!r}, which brand/tokens.json does not define")
        elif not any(f["style"] == icon.get("style") for f in face["faces"]):
            found.append(f"icon.style is {icon.get('style')!r}, a face the {icon['type']} type does not have")
        pairs = {(q["text"], q["on"]) for q in t.get("contrast", {}).get("pairs", [])}
        if (icon.get("color"), icon.get("on")) not in pairs:
            found.append(f"the icon sets {icon.get('color')} on {icon.get('on')}, which is not a pair "
                         f"checks/contrast.py holds")
    return found


def main():
    found = faults()
    if found:
        print("::error::a brand decision is missing its reason, or names nothing:\n")
        for f in found:
            print(f"   {f}")
        return 1
    print("ok   every colour, typeface and radius says what it is for and why, on the ground and on paper, so does the icon, "
          "and the brand says its idea")
    return 0


if __name__ == "__main__":
    sys.exit(main())
