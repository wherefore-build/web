#!/usr/bin/env python3
"""Prove checks/motion_reads.py fails a clip that does not read.

Each case breaks a copy of this repository (checks/_copy.py) - a storyboard
the build wrote, or the page beside it - and requires the check to fail in
the words of the case, or, for the case that must not fire, to pass.

  fails   a scene cut too short for its words
          a command the CLI does not have
          a line the engine never printed
          a claim of too many words
          a page missing a word its scene says
  passes  the site as it is

Usage:  python3 checks/motion_reads_proof.py
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _copy                                                       # noqa: E402

_copy.fresh()
from wherefore.prove import Edit, check, report                   # noqa: E402

CHECK = "checks/motion_reads.py"
BOARD = "motion/gate/storyboard.json"
PAGE = "site/motion/gate/index.html"
PASS = "every one of the"


def edit_board(p, fn):
    b = json.loads(p.read_text(encoding="utf-8"))
    fn(b)
    p.write_text(json.dumps(b, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def scene(b, kind):
    return next(s for s in b["scenes"] if s["kind"] == kind)


def main():
    r = []
    with Edit(BOARD) as p:
        edit_board(p, lambda b: scene(b, "mechanism").__setitem__("end", scene(b, "mechanism")["start"] + 1.0))
        check(r, "a scene cut too short for its words", CHECK, True, ["TOO FAST       gate/mechanism"])
    with Edit(BOARD) as p:
        edit_board(p, lambda b: scene(b, "run").__setitem__("typed", "wherefore teleport"))
        check(r, "a command the CLI does not have", CHECK, True, ["NOT A COMMAND  gate runs `wherefore teleport`"])
    with Edit(BOARD) as p:
        edit_board(p, lambda b: scene(b, "run")["lines"].__setitem__(0, "every file is golden"))
        check(r, "a line the engine never printed", CHECK, True, ["NEVER PRINTED  gate shows `every file is golden`"])
    with Edit(BOARD) as p:
        edit_board(p, lambda b: scene(b, "claim").__setitem__("text", "Every tracked file accounted for and every generated one current and nothing else at all."))
        check(r, "a claim of too many words", CHECK, True, ["CLAIM          gate:"])
    with Edit(PAGE) as p:
        text = p.read_text(encoding="utf-8")
        if ">accounted<" not in text:
            raise SystemExit("the gate's claim no longer sets the word `accounted` - re-anchor this case")
        p.write_text(text.replace(">accounted<", ">counted<", 1), encoding="utf-8")
        check(r, "a page missing a word its scene says", CHECK, True, ["DROPPED        gate/claim: the page lacks `accounted`"])
    check(r, "the site as it is", CHECK, False, [PASS])
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
