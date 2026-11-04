#!/usr/bin/env python3
"""Prove checks/questions_turn.py fails questions that do not turn, or do not stop.

Each case breaks the served page in a copy of this repository (checks/_copy.py)
and requires the check to fail in the words of the case, or, for the case that
must not fire, to pass.

  fails   the timer gone: nothing turns
          the first chip checked when the page loads: the turning never starts
          the timer still running after a chip is picked
          the timer running for a visitor who asked for less motion
  passes  the site as it is

Usage:  python3 checks/questions_turn_proof.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _copy                                                       # noqa: E402

_copy.fresh()
from wherefore.prove import Edit, check, report                   # noqa: E402

CHECK = "checks/questions_turn.py"
PAGE = "site/about/index.html"
PASS = "the questions turn by themselves"


def plant(p, before, after):
    text = p.read_text(encoding="utf-8")
    if before not in text:
        raise SystemExit(f"{p.name} no longer holds {before!r} - re-anchor this case")
    p.write_text(text.replace(before, after, 1), encoding="utf-8")


def main():
    r = []
    with Edit(PAGE) as p:
        plant(p, "#ask-auto:checked ~ .ask-panels .ask-panel { animation:", "#ask-auto:checked ~ .ask-panels .nothing { animation:")
        check(r, "the timer gone", CHECK, True, ["did not turn by themselves"])
    with Edit(PAGE) as p:
        plant(p, 'id="ask-auto" checked', 'id="ask-auto"')
        plant(p, 'id="ask-0">', 'id="ask-0" checked>')
        check(r, "the first chip checked on load", CHECK, True, ["did not turn by themselves"])
    with Edit(PAGE) as p:
        plant(p, "#ask-auto:checked ~ .ask-panels .ask-panel { animation:", ".ask-panels .ask-panel { animation:")
        check(r, "the timer still running after a pick", CHECK, True, ["tapping the first chip did not stop"])
    with Edit(PAGE) as p:
        plant(p, "@media (prefers-reduced-motion: no-preference) {", "@media all {")
        check(r, "turning for a visitor who asked for less motion", CHECK, True,
              ["with motion reduced, the questions turned anyway"])
    check(r, "the site as it is", CHECK, False, [PASS])
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
