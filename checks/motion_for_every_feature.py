#!/usr/bin/env python3
"""Every feature the pinned release ships has its clip, and the features page plays it.

THE CLIP IS THE PROMISE IN MOTION. The features page must say something about
every feature or the build stops; since 0.20.0 the engine also writes a clip
for each - a page in motion, site/motion/<id>/ - and the card plays it. A
feature whose clip is missing, or whose card does not frame it, is a feature
people read about and never see. This fails:

  NO CLIP      site/motion/<id>/index.html or motion/<id>/storyboard.json is not there
  NOT PLAYED   the features page frames no clip for a feature it describes
  NOT A CLIP   a storyboard names another feature, or has no scenes
  STRAY        a clip in site/motion/ for a feature the release does not ship

Usage:  python3 checks/motion_for_every_feature.py
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
CLIPS = SITE / "motion"
BOARDS = ROOT / "motion"            # the storyboards, as data, kept out of site/
PAGE = SITE / "features/index.html"
FRAME = re.compile(r'<iframe src="\.\./motion/([a-z0-9-]+)/index\.html"')


def faults():
    from importlib.resources import files
    found = []
    ids = [f["id"] for f in json.loads((files("wherefore") / "features.json").read_text(encoding="utf-8"))["features"]]
    framed = FRAME.findall(PAGE.read_text(encoding="utf-8")) if PAGE.exists() else []
    for fid in ids:
        page, board = CLIPS / fid / "index.html", BOARDS / fid / "storyboard.json"
        if not page.is_file() or not board.is_file():
            found.append(f"NO CLIP      {fid}: site/motion/{fid}/ has no index.html, or motion/{fid}/ no storyboard.json; the build writes them")
            continue
        try:
            b = json.loads(board.read_text(encoding="utf-8"))
        except ValueError:
            b = {}
        if b.get("id") != fid or not b.get("scenes"):
            found.append(f"NOT A CLIP   motion/{fid}/storyboard.json is not {fid}'s storyboard, or has no scenes")
        if fid not in framed:
            found.append(f"NOT PLAYED   the features page frames no clip for {fid}")
    for where in (CLIPS, BOARDS):
        for d in sorted(where.iterdir()) if where.is_dir() else []:
            if d.is_dir() and d.name not in ids:
                found.append(f"STRAY        {d.relative_to(ROOT)}/ is a clip for a feature the pinned release does not ship")
    return found, len(ids)


def main():
    found, n = faults()
    for f in found:
        print(f"::error::{f}")
    if found:
        print(f"\n{len(found)} fault(s): every feature has a clip and the features page plays it")
        return 1
    print(f"ok   every one of the {n} features the pinned release ships has its clip, and the features page plays it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
