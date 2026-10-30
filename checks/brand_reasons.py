#!/usr/bin/env python3
"""Every brand decision carries its reason.

The engine refuses an exemption without a `why`; the brand is held to the same
rule. brand/tokens.json is where the brand's facts are said - each colour,
typeface and radius with what it is for (`role`) and why it is what it is
(`why`), and the idea the whole look follows (`idea`) - and the brand page is
built from exactly those words. A token without its reason is a decision
nobody can question, and the page would show a swatch with nothing beside it.
So this fails:

  - a colour, typeface or radius with no `role` or no `why`;
  - a colour that is `same_as` one the tokens do not define, or that says both
    `same_as` and `value` - it is one fact or the other, never both;
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
    return found


def main():
    found = faults()
    if found:
        print("::error::a brand decision is missing its reason, or names nothing:\n")
        for f in found:
            print(f"   {f}")
        return 1
    print("ok   every colour, typeface and radius says what it is for and why, and the brand says its idea")
    return 0


if __name__ == "__main__":
    sys.exit(main())
