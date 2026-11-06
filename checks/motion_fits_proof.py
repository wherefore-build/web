#!/usr/bin/env python3
"""Prove checks/motion_fits.py fails a clip that spills its frame, and a scene that shows nothing.

Each case breaks a copy of this repository (checks/_copy.py) - one clip's page,
as a visitor receives it - and requires the check to fail in the words of the
case, or, for the case that must not fire, to pass.

  fails   a headline sized past the frame
          a scene whose window never opens
  passes  the site as it is

Usage:  python3 checks/motion_fits_proof.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _copy                                                       # noqa: E402

_copy.fresh()
from wherefore.prove import Edit, check, report                   # noqa: E402

CHECK = "checks/motion_fits.py"
CLIP = "site/motion/published/index.html"
PASS = "every one of the"


def plant(p, before, after):
    text = p.read_text(encoding="utf-8")
    if before not in text:
        raise SystemExit(f"{p.name} no longer holds {before!r} - re-anchor this case")
    p.write_text(text.replace(before, after, 1), encoding="utf-8")


def main():
    r = []
    with Edit(CLIP) as p:
        plant(p, ".big{font:400 11.5cqmin/1.05", ".big{font:400 60cqmin/1.05")
        check(r, "a headline sized past the frame", CHECK, True, ["SPILLS   published portrait", "(ask)"])
    with Edit(CLIP) as p:
        plant(p, 'class="scene ask" style="animation-name:w1"', 'class="scene ask" style="animation-name:none"')
        check(r, "a scene whose window never opens", CHECK, True, ["BLANK    published portrait", "(ask): nothing of the scene is visible"])
    check(r, "the site as it is", CHECK, False, [PASS])
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
