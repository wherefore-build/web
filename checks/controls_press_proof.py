#!/usr/bin/env python3
"""Prove checks/controls_press.py fails a control a thumb would find broken.

Each case breaks a copy of this repository (checks/_copy.py) - the served page
or its stylesheet, as a visitor receives them - and requires the check to fail
in the words of the case, or, for the case that must not fire, to pass.

  fails   the stylesheet stops showing the step that is pressed
          the switch that shows how the page is built shows nothing
          a tab whose radio button was renamed
          the demo's steps hidden at a phone's width
          the tabs shrunk below a thumb
          an answer that opens below the fold
  passes  the site as it is

Usage:  python3 checks/controls_press_proof.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _copy                                                       # noqa: E402

_copy.fresh()
from wherefore.prove import Edit, check, report                   # noqa: E402

CHECK = "checks/controls_press.py"
PAGE = "site/index.html"
CSS = "site/page.css"
PASS = "every control on the site does something a visitor can see"


def plant(p, before, after):
    text = p.read_text(encoding="utf-8")
    if before not in text:
        raise SystemExit(f"{p.name} no longer holds {before!r} - re-anchor this case")
    p.write_text(text.replace(before, after, 1), encoding="utf-8")


def append(p, text):
    p.write_text(p.read_text(encoding="utf-8") + text, encoding="utf-8")


def main():
    r = []
    with Edit(CSS) as p:
        plant(p, "#stage-0:checked ~ * .at0, #stage-1:checked ~ * .at1, #stage-2:checked ~ * .at2 { display: inline; }",
              "#stage-0:checked ~ * .at0 { display: inline; }")
        check(r, "the step pressed is never shown", CHECK, True, ["pressing", "showed nothing new"])
    with Edit(CSS) as p:
        plant(p, "#inspect:checked ~ * .src { display: block; }\n#inspect:checked ~ main .src-key { display: block; }", "")
        check(r, "the switch shows nothing", CHECK, True, ["'How this page is built'", "showed nothing new"])
    with Edit(PAGE) as p:
        plant(p, 'id="ask-3"', 'id="ask-three"')
        check(r, "a tab whose radio button was renamed", CHECK, True,
              ["presses nothing: no control is called ask-3"])
    with Edit(CSS) as p:
        append(p, "@media (max-width: 40rem) { .stepper { display: none; } }\n")
        check(r, "the demo's steps hidden on a phone", CHECK, True, ["cannot be pressed at 390 px"])
    with Edit(CSS) as p:
        append(p, ".tab { min-height: 0; padding: 0 0.25rem; font-size: 0.625rem; }\n")
        check(r, "the tabs shrunk below a thumb", CHECK, True,
              ["is smaller than a thumb at 390 px", "it must be 44 by 44 at least"])
    with Edit(CSS) as p:
        append(p, ".ask-panel { margin-top: 300vh; }\n")
        check(r, "an answer that opens below the fold", CHECK, True,
              ["changed only what is off the screen"])
    check(r, "the site as it is", CHECK, False, [PASS])
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
