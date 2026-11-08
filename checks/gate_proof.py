#!/usr/bin/env python3
"""Prove the gate fails this company's corpus when it should.

The gate that judges this repository is the engine release it pins, and this
proves it is not just running but catching: each case breaks a copy of the
repository (checks/_copy.py) the way the site could plausibly go wrong, and
requires the gate to fail in the words of the case.

  fails   the page edited by hand, instead of the facts
          the headline changed in the facts, the page not regenerated
          the launch status moved in the facts, and neither the page nor its
            headers regenerated - the banner and the noindex would stay up
          a launch status nobody has defined
          the accent changed in the brand, its stylesheet and page not
            regenerated
          the icon changed in the brand and regenerated, and its PNG not
            shot again - the picture on every profile would be the old one
          a feature the pinned release ships, with nothing on the page
            about it - the build stops until the facts describe it
          a new file committed that nothing classifies
  passes  the repository as it is

Usage:  python3 checks/gate_proof.py
"""
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _copy                                                       # noqa: E402

ROOT = _copy.fresh()
from wherefore.prove import Edit, check, report                   # noqa: E402

PASS = "every tracked file is classified"
PAGE = "site/index.html regenerated DIFFERENT from what is committed"
HEADERS = "site/_headers regenerated DIFFERENT from what is committed"


def gate(r, name, fails, words):
    return check(r, name, "-m", fails, words, "wherefore", "gate")


def facts(p, change):
    doc = json.loads(p.read_text(encoding="utf-8"))
    change(doc)
    p.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def regenerate_brand():
    subprocess.run([sys.executable, "brand.py"], cwd=ROOT / "gen", check=True)


def main():
    r = []
    with Edit("site/index.html") as p:
        # Anchored on the heading's tag, not its words: the headline is the
        # owner's to change, and a case that quoted it missed when it did.
        p.write_text(p.read_text(encoding="utf-8").replace(
            "<h1>", "<h1>Edited by hand. ", 1), encoding="utf-8")
        gate(r, "the page edited by hand, instead of the facts", True, [PAGE])

    with Edit("facts/company.json") as p:
        facts(p, lambda d: d["hero"].update(headline_end="shipped."))
        gate(r, "the headline changed in the facts, the page not regenerated", True, [PAGE])

    with Edit("facts/company.json") as p:
        # whichever way the site is, the other way: the banner and the robots header both move
        facts(p, lambda d: d["site"].update(status="draft" if d["site"]["status"] == "launched" else "launched"))
        gate(r, "the launch status moved in the facts, the page and its headers not regenerated", True,
             [PAGE, HEADERS])

    with Edit("facts/company.json") as p:
        facts(p, lambda d: d["site"].update(status="beta"))
        gate(r, "a launch status nobody has defined", True,
             ["site.py failed while the gate ran it", "site.status is 'beta': it is one of draft, launched"])

    with Edit("brand/tokens.json") as p:
        facts(p, lambda d: d["color"]["accent"].update(value="#FF7A3D"))
        gate(r, "the accent changed in the brand, nothing regenerated", True,
             ["site/brand.css regenerated DIFFERENT from what is committed",
              "site/brand/index.html regenerated DIFFERENT from what is committed"])

    try:
        with Edit("brand/tokens.json") as p:
            facts(p, lambda d: d["icon"].update(glyph="W"))
            regenerate_brand()
            gate(r, "the icon changed and regenerated, its PNG not shot again", True,
                 ["what 'icon' was made from has moved", "brand/icon/icon-1024.png"])
    finally:
        regenerate_brand()

    with Edit("facts/company.json") as p:
        facts(p, lambda d: d["does"]["words"].pop("scan"))
        gate(r, "a feature the release ships, and the page says nothing about it", True,
             ["site.py failed while the gate ran it",
              "ships the feature `scan`", "says nothing about it"])

    notes = ROOT / "notes.txt"
    notes.write_text("a file nobody declared\n", encoding="utf-8")
    subprocess.run(["git", "add", "notes.txt"], cwd=ROOT, check=True)
    try:
        gate(r, "a new file committed that nothing classifies", True,
             ["notes.txt is unclassified"])
    finally:
        subprocess.run(["git", "rm", "-q", "--cached", "notes.txt"], cwd=ROOT, check=True)
        notes.unlink()

    gate(r, "the repository as it is", False, [PASS])
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
