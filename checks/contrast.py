#!/usr/bin/env python3
"""Every text colour reaches its contrast on every ground it is set on.

brand/tokens.json lists, under `contrast.pairs`, each text colour the pages put
on each ground, with the least it must reach (4.5:1 for body text, WCAG AA).
This computes every one and fails a pair that falls short, naming the ratio and
the minimum, so a token nudged darker for taste cannot quietly make a caption
unreadable. The brand page prints the same ratios, from the same arithmetic
(gen/kit.py).

It also fails a pair that names a colour the tokens do not define, a colour
that is not #RRGGBB, and one that is the `same_as` a colour with no value,
because none of them can be measured. A `same_as` colour is measured as the
colour it names.

WHAT IT CANNOT SEE: a pair a page uses and the tokens do not list. That is the
tokens' to declare; the brand page shows every pair it holds.

Usage:  python3 checks/contrast.py
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gen"))
from kit import contrast                                             # noqa: E402

TOKENS = ROOT / "brand/tokens.json"
HEX = re.compile(r"#[0-9A-Fa-f]{6}")


def faults():
    t = json.loads(TOKENS.read_text(encoding="utf-8"))
    colours, found = {}, []
    for k, c in t["color"].items():
        if "same_as" in c:
            target = t["color"].get(c["same_as"], {})
            if "value" not in target:
                found.append(f"{k} is the same as {c['same_as']}, which brand/tokens.json gives no value")
                continue
            colours[k] = target["value"]
        else:
            colours[k] = c["value"]
    found += [f"{k} is {v!r}, which is not a #RRGGBB colour" for k, v in colours.items()
              if not HEX.fullmatch(v)]
    schemes = {"": colours}
    # The light scheme, `light` in the tokens: the same pairs, on paper.
    if "light" in t:
        light = {}
        for k, c in t["light"]["color"].items():
            if "same_as" in c:
                target = t["light"]["color"].get(c["same_as"], {})
                if "value" not in target:
                    found.append(f"on paper, {k} is the same as {c['same_as']}, which the light scheme gives no value")
                    continue
                light[k] = target["value"]
            else:
                light[k] = c["value"]
        found += [f"on paper, {k} is {v!r}, which is not a #RRGGBB colour" for k, v in light.items()
                  if not HEX.fullmatch(v)]
        schemes["on paper, "] = light
    for where, cs in schemes.items():
        for p in t["contrast"]["pairs"]:
            missing = [n for n in (p["text"], p["on"]) if n not in cs]
            if missing:
                found += [f"{where}a pair names {n}, which brand/tokens.json does not define" for n in missing]
                continue
            if not all(HEX.fullmatch(cs[n]) for n in (p["text"], p["on"])):
                continue
            r = contrast(cs[p["text"]], cs[p["on"]])
            if r + 1e-9 < p["min"]:
                found.append(f"{where}{p['text']} on {p['on']} reaches {r:.2f}:1; it must reach {p['min']:g}:1")
    return found, len(t["contrast"]["pairs"]) * len(schemes)


def main():
    found, n = faults()
    if found:
        print("::error::a text colour is not readable on a ground it is set on:\n")
        for f in found:
            print(f"   {f}")
        return 1
    print(f"ok   every text colour reaches its contrast on every ground it is set on ({n} pairs, on the ground and on paper)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
