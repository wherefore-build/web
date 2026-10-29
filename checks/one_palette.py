#!/usr/bin/env python3
"""No colour or typeface is said anywhere but brand/tokens.json.

The brand reaches a page through site/brand.css, the custom properties
gen/brand.py writes from the tokens. A colour typed into a stylesheet or a
generator is a second copy of a brand fact: it looks right until the accent
changes, and then it is the one thing that did not. So this reads every
stylesheet and generator under gen/ and fails a colour literal (#hex, rgb(),
hsl() and their kin, or a named colour on a colour property) and a typeface
named outright, naming the file and the line. The fix is a var(--…).

A typeface whose value a generator interpolates (`font-family: "{face[...]}"`
in gen/brand.py, which writes brand.css from the tokens) is read, not said, and
passes; only a typeface written out is a second copy.

WHAT IT CANNOT SEE: a colour built at run time from parts, a colour inside an
image, and a literal smuggled through an interpolation. None exists here.

Usage:  python3 checks/one_palette.py
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
READ = ("gen/*.css", "gen/*.py")

HEX = re.compile(r"(?<![\w&])#(?:[0-9A-Fa-f]{8}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3,4})\b")
FUNC = re.compile(r"\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\(", re.I)
NAMED = re.compile(r"\b(?:color|background(?:-color)?|border(?:-[a-z]+)*|outline(?:-color)?|fill|stroke|"
                   r"text-decoration-color|caret-color)\s*:[^;{}\"']*?\b(white|black|red|green|blue|gray|grey|"
                   r"orange|yellow|purple|pink|brown|silver|navy|teal|lime)\b", re.I)
FONT = re.compile(r"\bfont(?:-family)?\s*:([^;]*)", re.I)


def faults():
    found = []
    for pattern in READ:
        for path in sorted(ROOT.glob(pattern)):
            rel = path.relative_to(ROOT).as_posix()
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for m in HEX.finditer(line):
                    found.append(f"{rel}:{n}: {m.group(0)} - a colour said outside brand/tokens.json")
                for m in FUNC.finditer(line):
                    found.append(f"{rel}:{n}: {m.group(0)}…) - a colour said outside brand/tokens.json")
                for m in NAMED.finditer(line):
                    found.append(f"{rel}:{n}: {m.group(1)} - a colour said outside brand/tokens.json")
                for m in FONT.finditer(line):
                    value = m.group(1)
                    if "var(--font-" not in value and "{" not in value and value.strip() not in ("inherit", ""):
                        found.append(f"{rel}:{n}: {m.group(0).strip()} - a typeface said outside "
                                     f"brand/tokens.json")
    return found


def main():
    found = faults()
    if found:
        print("::error::the brand is said twice - use a var(--…) from site/brand.css instead:\n")
        for f in found:
            print(f"   {f}")
        return 1
    print("ok   every colour and typeface comes from brand/tokens.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
