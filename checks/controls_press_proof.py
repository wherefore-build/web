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
          the case study's list hidden when it is opened
          the hero's link to Get started pointing at a part the page has not
          Get started landing under the sticky header when the link is pressed
  passes  the site as it is, its case study's list closed until pressed

Usage:  python3 checks/controls_press_proof.py
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _copy                                                       # noqa: E402

_copy.fresh()
from wherefore.prove import Edit, check, report                   # noqa: E402

CHECK = "checks/controls_press.py"
PAGE = "site/index.html"
WHY = "site/why/index.html"        # the questions' tabs, on their own page
CSS = "site/page.css"
PASS = "every control on the site does something a visitor can see"
# The case study's toggle, as the facts word it: the words are the owner's to
# change, and a case that typed them missed when they did.
CASE_MORE = json.loads((pathlib.Path(__file__).resolve().parents[1] / "facts/company.json")
                       .read_text(encoding="utf-8"))["case"]["more"]


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
        check(r, "the switch shows nothing", CHECK, True, ["'Compiled by Wherefore'", "showed nothing new"])
    with Edit(WHY) as p:
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
    with Edit(CSS) as p:
        append(p, ".case-more[open] .case-grid { display: none; }\n")
        check(r, "the case study's list hidden when opened", CHECK, True,
              [f"'{CASE_MORE}'", "showed nothing new"])
    with Edit(PAGE) as p:
        plant(p, '<section id="start">', '<section id="begin">')
        check(r, "the hero's link to a part the page has not", CHECK, True,
              ["'Get started →' points at nothing", "no part of the page is called 'start'"])
    # The header is sticky and 101 px tall on a phone; a section's scroll margin keeps a pressed-for heading clear of it
    with Edit(CSS) as p:
        append(p, "section { scroll-margin-top: 0; }\n")
        check(r, "Get started landing under the sticky header", CHECK, True,
              ["'Get started →' lands 'Your company, compiled.' under the sticky header"])
    # Chromium lays a closed <details>'s content out unseen; counted as showing, it made this press look empty
    check(r, "the site as it is", CHECK, False, [PASS])
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
