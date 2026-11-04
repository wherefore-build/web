#!/usr/bin/env python3
"""Prove checks/fits_phone.py fails a page wider than a phone, and an icon bigger than its words.

Each case breaks the served stylesheet in a copy of this repository
(checks/_copy.py) and requires the check to fail in the words of the case, or,
for the case that must not fire, to pass. They are the two faults the check
exists for, as they were found:

  fails   the link icon unsized outside a button: it fills its line
          the turning questions unclipped: the page widens as one tips in
  passes  the site as it is

Usage:  python3 checks/fits_phone_proof.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _copy                                                       # noqa: E402

_copy.fresh()
from wherefore.prove import Edit, check, report                   # noqa: E402

CHECK = "checks/fits_phone.py"
CSS = "site/page.css"
PASS = "every page fits a 390 px phone"


def plant(p, before, after):
    text = p.read_text(encoding="utf-8")
    if before not in text:
        raise SystemExit(f"{p.name} no longer holds {before!r} - re-anchor this case")
    p.write_text(text.replace(before, after, 1), encoding="utf-8")


def main():
    r = []
    with Edit(CSS) as p:
        plant(p, ".out { width: 1em; height: 1em; margin-left: 0.25em; vertical-align: -0.125em; }", "")
        check(r, "the link icon unsized outside a button", CHECK, True, ["beside 13 px words"])
    with Edit(CSS) as p:
        plant(p, "margin-top: 0.75rem; overflow-x: clip; }", "margin-top: 0.75rem; }")
        check(r, "the turning questions unclipped", CHECK, True, ["px wide on a 390 px screen, with motion no-preference"])
    check(r, "the site as it is", CHECK, False, [PASS])
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
