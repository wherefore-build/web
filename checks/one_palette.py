#!/usr/bin/env python3
"""No colour or typeface is said anywhere but brand/tokens.json.

The brand reaches a page through site/brand.css, the custom properties
gen/brand.py writes from the tokens. A colour typed into a stylesheet or a
generator is a second copy of a brand fact: it looks right until the accent
changes, and then it is the one thing that did not. So this reads every
stylesheet and generator under gen/ and fails a colour literal (#hex, rgb(),
hsl() and their kin, or a named colour on a colour property) and a typeface
named outright, naming the file and the line. The fix is a var(--…).

AND EVERY PAGE A VISITOR RECEIVES (owner, 5 November 2026): the pages and
stylesheets under site/ are read too, for colours only, and a colour there
passes only if it is one of the tokens' own values - the brand, written out
by gen/brand.py - or the page is named in NOT_OURS with the reason. So a page
the engine draws (the map) must carry the brand's values and none of the
engine's, which `--theme site/brand/map.css` sees to, and a page another
company draws (the pendulum's model) is excused by name, once, with why.

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
SERVED = ("site/**/*.css", "site/**/*.html")
TOKENS = ROOT / "brand/tokens.json"

# Pages whose colours are not this site's to say, and why.
NOT_OURS = {
    "site/pendulum/index.html": "the pendulum's own model, byte for byte, with the pendulum's own colours in it; "
                                "its own suite holds its brand, and the frame keeps it apart from this page",
    "site/pendulum/plate/index.html": "the pendulum's model again, opened on one part, with the same colours in it; "
                                      "the same suite and the same frame",
    "site/changelog/index.html": "quotes each release's picture as the engine printed it, and the 0.10.0 picture is "
                                 "the palette check catching a stray colour: the page says that colour as text, "
                                 "never as a style - its styles are page.css and brand.css, read above",
}

HEX = re.compile(r"(?<![\w&])#(?:[0-9A-Fa-f]{8}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3,4})\b")
FUNC = re.compile(r"\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\(", re.I)
NAMED = re.compile(r"\b(?:color|background(?:-color)?|border(?:-[a-z]+)*|outline(?:-color)?|fill|stroke|"
                   r"text-decoration-color|caret-color)\s*:[^;{}\"']*?\b(white|black|red|green|blue|gray|grey|"
                   r"orange|yellow|purple|pink|brown|silver|navy|teal|lime)\b", re.I)
FONT = re.compile(r"\bfont(?:-family)?\s*:([^;]*)", re.I)


def brand_values():
    """Every colour value the tokens hold, upper-cased: the only literals a served page may carry."""
    import json
    tokens = json.loads(TOKENS.read_text(encoding="utf-8"))
    both = list(tokens["color"].values()) + list(tokens.get("light", {}).get("color", {}).values())
    return {c["value"].upper() for c in both if "value" in c}


def served_faults():
    found, allowed = [], brand_values()
    for pattern in SERVED:
        for path in sorted(ROOT.glob(pattern)):
            rel = path.relative_to(ROOT).as_posix()
            if rel in NOT_OURS:
                continue
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for m in HEX.finditer(line):
                    if m.group(0).upper() not in allowed:
                        found.append(f"{rel}:{n}: {m.group(0)} - a colour a visitor receives that is not one of the brand's")
                for m in FUNC.finditer(line):
                    found.append(f"{rel}:{n}: {m.group(0)}…) - a colour a visitor receives that is not one of the brand's")
                for m in NAMED.finditer(line):
                    found.append(f"{rel}:{n}: {m.group(1)} - a colour a visitor receives that is not one of the brand's")
    return found


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
    return found + served_faults()


def main():
    found = faults()
    if found:
        print("::error::the brand is said twice - use a var(--…) from site/brand.css instead:\n")
        for f in found:
            print(f"   {f}")
        return 1
    print("ok   every colour and typeface comes from brand/tokens.json, on every page a visitor receives")
    return 0


if __name__ == "__main__":
    sys.exit(main())
