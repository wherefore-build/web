#!/usr/bin/env python3
"""Prove checks/motion_for_every_feature.py fails a feature without its clip, and a card that does not play it.

Each case breaks a copy of this repository (checks/_copy.py) and requires the
check to fail in the words of the case, or, for the case that must not fire,
to pass.

  fails   a feature's clip deleted
          a storyboard that is another feature's
          the features page framing no clip for a feature
          a clip for a feature the release does not ship
  passes  the site as it is

Usage:  python3 checks/motion_for_every_feature_proof.py
"""
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _copy                                                       # noqa: E402

ROOT = _copy.fresh()
from wherefore.prove import Edit, check, report                   # noqa: E402

CHECK = "checks/motion_for_every_feature.py"
PAGE = "site/features/index.html"
PASS = "every one of the"


def plant(p, before, after):
    text = p.read_text(encoding="utf-8")
    if before not in text:
        raise SystemExit(f"{p.name} no longer holds {before!r} - re-anchor this case")
    p.write_text(text.replace(before, after, 1), encoding="utf-8")


def main():
    r = []
    with Edit("site/motion/gate/index.html") as p:
        p.unlink()
        check(r, "a feature's clip deleted", CHECK, True, ["NO CLIP      gate"])
    with Edit("site/motion/gate/storyboard.json") as p:
        plant(p, '"id": "gate"', '"id": "build"')
        check(r, "a storyboard that is another feature's", CHECK, True, ["NOT A CLIP   site/motion/gate/storyboard.json"])
    with Edit(PAGE) as p:
        plant(p, '<iframe src="../motion/reach/index.html"', '<iframe src="../motion/reach/index.htm"')
        check(r, "the features page framing no clip for a feature", CHECK, True, ["NOT PLAYED   the features page frames no clip for reach"])
    stray = ROOT / "site/motion/teleport"
    shutil.copytree(ROOT / "site/motion/gate", stray)
    try:
        check(r, "a clip for a feature the release does not ship", CHECK, True, ["STRAY        site/motion/teleport/"])
    finally:
        shutil.rmtree(stray)
    check(r, "the site as it is", CHECK, False, [PASS])
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
