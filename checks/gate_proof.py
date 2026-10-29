#!/usr/bin/env python3
"""Prove the gate fails this company's corpus when it should.

The gate that judges this repository is the engine release it pins, and this
proves it is not just running but catching: each case breaks a copy of the
repository (checks/_copy.py) the way the site could plausibly go wrong, and
requires the gate to fail in the words of the case.

  fails   the page edited by hand, instead of the facts
          the headline changed in the facts, the page not regenerated
          the site launched in the facts, and neither the page nor its
            headers regenerated - the banner and the noindex would stay up
          a launch status nobody has defined
          the accent changed in the brand, its stylesheet and page not
            regenerated
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


def main():
    r = []
    with Edit("site/index.html") as p:
        p.write_text(p.read_text(encoding="utf-8").replace(
            "<em>compiled.</em>", "<em>shipped.</em>", 1), encoding="utf-8")
        gate(r, "the page edited by hand, instead of the facts", True, [PAGE])

    with Edit("facts/company.json") as p:
        facts(p, lambda d: d["hero"].update(headline_end="shipped."))
        gate(r, "the headline changed in the facts, the page not regenerated", True, [PAGE])

    with Edit("facts/company.json") as p:
        facts(p, lambda d: d["site"].update(status="launched"))
        gate(r, "launched in the facts, the page and its headers not regenerated", True,
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
