#!/usr/bin/env python3
"""Prove checks/model_turns.py fails a model a thumb would find broken, or a frame that lets too much in.

Each case breaks a copy of this repository (checks/_copy.py) - the served page,
its stylesheet, its headers or the framed model, as a visitor receives them -
and requires the check to fail in the words of the case, or, for the case that
must not fire, to pass.

  fails   the model below the heading at a phone's width, not beside it
          a script on the site's own page
          the frame allowed to reach the page around it
          the model's own policy lets no script run
          a model a drag cannot turn
          a model on a ground its frame did not name
          a model that draws nothing
  passes  the site as it is

Usage:  python3 checks/model_turns_proof.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _copy                                                       # noqa: E402

_copy.fresh()
from wherefore.prove import Edit, check, report                   # noqa: E402

CHECK = "checks/model_turns.py"
PAGE = "site/index.html"
CSS = "site/page.css"
HEADERS = "site/_headers"
MODEL = "site/pendulum/index.html"
PASS = "the pendulum's model stands to the right of the case study's heading"


def plant(p, before, after):
    text = p.read_text(encoding="utf-8")
    if before not in text:
        raise SystemExit(f"{p.name} no longer holds {before!r} - re-anchor this case")
    p.write_text(text.replace(before, after, 1), encoding="utf-8")


def main():
    r = []
    with Edit(CSS) as p:
        plant(p, '"eyebrow eyebrow" "heading model" "text text" "actions actions"',
              '"eyebrow eyebrow" "heading heading" "model model" "text text" "actions actions"')
        check(r, "the model below the heading on a phone", CHECK, True,
              ["at 390 px, the model is not to the right of the heading"])
    with Edit(PAGE) as p:
        plant(p, "</body>", "<script></script>\n</body>")
        check(r, "a script on the site's own page", CHECK, True, ["site/index.html has 1 <script>"])
    with Edit(PAGE) as p:
        plant(p, 'sandbox="allow-scripts"', 'sandbox="allow-scripts allow-same-origin"')
        check(r, "the frame allowed to reach the page", CHECK, True,
              ["the model's frame is sandboxed 'allow-scripts allow-same-origin'"])
    with Edit(HEADERS) as p:
        plant(p, "default-src 'none'; script-src 'unsafe-inline'; ", "default-src 'none'; ")
        check(r, "the model's policy lets no script run", CHECK, True, ["its policy lets no script run"])
    with Edit(MODEL) as p:
        p.write_text(p.read_text(encoding="utf-8") + "<style>canvas{pointer-events:none}</style>\n",
                     encoding="utf-8")
        check(r, "a model a drag cannot turn", CHECK, True,
              ["at 390 px, the model did not turn when a thumb dragged across it"])
    with Edit(MODEL) as p:
        plant(p, "_BGP=_Q.get('bg')", "_BGP=null")
        check(r, "a model on a ground its frame did not name", CHECK, True, ["not the ground its frame names"])
    with Edit(MODEL) as p:
        p.write_text("<!doctype html>\n<title>nothing</title>\n", encoding="utf-8")
        check(r, "a model that draws nothing", CHECK, True, ["the model drew nothing in 15 seconds"])
    check(r, "the site as it is", CHECK, False, [PASS])
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
