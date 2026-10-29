#!/usr/bin/env python3
"""Every text colour reaches its contrast on every ground it is set on.

brand/tokens.json lists, under `contrast.pairs`, each text colour the pages put
on each ground, with the least it must reach (4.5:1 for body text, WCAG AA).
This computes every one and fails a pair that falls short, naming the ratio and
the minimum, so a token nudged darker for taste cannot quietly make a caption
unreadable. The brand page prints the same ratios, from the same arithmetic
(gen/kit.py).

It also fails a pair that names a colour the tokens do not define, and a colour
that is not #RRGGBB, because neither can be measured.

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
    colours = {k: c["value"] for k, c in t["color"].items()}
    found = [f"{k} is {v!r}, which is not a #RRGGBB colour" for k, v in colours.items()
             if not HEX.fullmatch(v)]
    for p in t["contrast"]["pairs"]:
        missing = [n for n in (p["text"], p["on"]) if n not in colours]
        if missing:
            found += [f"a pair names {n}, which brand/tokens.json does not define" for n in missing]
            continue
        if not all(HEX.fullmatch(colours[n]) for n in (p["text"], p["on"])):
            continue
        r = contrast(colours[p["text"]], colours[p["on"]])
        if r + 1e-9 < p["min"]:
            found.append(f"{p['text']} on {p['on']} reaches {r:.2f}:1; it must reach {p['min']:g}:1")
    return found, len(t["contrast"]["pairs"])


def main():
    found, n = faults()
    if found:
        print("::error::a text colour is not readable on a ground it is set on:\n")
        for f in found:
            print(f"   {f}")
        return 1
    print(f"ok   every text colour reaches its contrast on every ground it is set on ({n} pairs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
