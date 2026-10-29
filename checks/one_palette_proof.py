#!/usr/bin/env python3
"""Prove checks/one_palette.py fails a colour or a typeface said outside the tokens.

Each case breaks a copy of this repository (checks/_copy.py) and requires the
check to fail in the words of the case, or - for the cases that must not fire -
to pass.

  fails   a hex colour typed into the stylesheet
          an rgba() colour typed into a generator
          a named colour on a border
          a typeface named outright
  passes  a new rule that takes its colour and face from the brand
          the stylesheets and generators as they are

Usage:  python3 checks/one_palette_proof.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _copy                                                       # noqa: E402

_copy.fresh()
from wherefore.prove import Edit, check, report                   # noqa: E402

CHECK = "checks/one_palette.py"
CSS = "gen/page.css"
SAID = "a colour said outside brand/tokens.json"
PASS = "every colour and typeface comes from brand/tokens.json"


def append(p, text):
    p.write_text(p.read_text(encoding="utf-8") + text, encoding="utf-8")


def main():
    r = []
    with Edit(CSS) as p:
        append(p, ".promo { color: #ff3355; }\n")
        check(r, "a hex colour in the stylesheet", CHECK, True, [f"{CSS}:", "#ff3355", SAID])
    with Edit("gen/site.py") as p:
        append(p, "SHADOW = 'box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4)'\n")
        check(r, "an rgba() colour in a generator", CHECK, True, ["gen/site.py:", "rgba(", SAID])
    with Edit(CSS) as p:
        append(p, ".callout { border: 1px solid white; }\n")
        check(r, "a named colour on a border", CHECK, True, ["white", SAID])
    with Edit(CSS) as p:
        append(p, ".quote { font-family: Georgia, serif; }\n")
        check(r, "a typeface named outright", CHECK, True,
              ["font-family: Georgia, serif", "a typeface said outside brand/tokens.json"])
    with Edit(CSS) as p:
        append(p, ".quote { color: var(--accent); font: italic 400 2rem/1.2 var(--font-display); }\n")
        check(r, "a rule that takes everything from the brand - must not fire", CHECK, False, [PASS])
    check(r, "the stylesheets and generators as they are", CHECK, False, [PASS])
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
