#!/usr/bin/env python3
"""Prove checks/case_study.py fails a case study that is not built from its snapshot of the pendulum's counts.

Each case breaks a copy of this repository (checks/_copy.py) and requires the
check to fail in the words of the case, or, for the case that must not fire, to
pass.

  fails   the release typed into the facts' as-of line instead of read
          a count the pendulum started making that nobody decided about
          the copy's stamp without its commit
          the copy's stamp with a version where its release mark goes
          a count that is not a number
          an excuse in UNSHOWN for a value the copy does not have
  passes  the copy and the page as they are

Usage:  python3 checks/case_study_proof.py
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _copy                                                       # noqa: E402

_copy.fresh()
from wherefore.prove import Edit, check, report                   # noqa: E402

CHECK = "checks/case_study.py"
COPY = "facts/pendulum.json"
PASS = "the copy says where and when it was read"


def change(p, how):
    doc = json.loads(p.read_text(encoding="utf-8"))
    how(doc)
    p.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    r = []
    # The release the snapshot stands at, read rather than typed: a proof that
    # named V83 broke the day the pendulum cut V84.
    v = json.loads(pathlib.Path(_copy.ROOT, COPY).read_text(encoding="utf-8"))["counts"]["pack"]["version"]
    with Edit("facts/company.json") as p:
        text = p.read_text(encoding="utf-8")
        p.write_text(text.replace("at V{version} of the pack", f"at V{v} of the pack", 1), encoding="utf-8")
        check(r, "the release typed into the as-of line", CHECK, True,
              [f"counts.pack.version moved ({v} -> {v + 1000}) and the page did not"])
    with Edit(COPY) as p:
        change(p, lambda d: d["counts"].update(welds=12))
        check(r, "a new count nobody decided about", CHECK, True,
              ["counts.welds moved (12 -> 1012) and the page did not"])
    with Edit(COPY) as p:
        change(p, lambda d: d["captured"].pop("commit"))
        check(r, "the stamp without its commit", CHECK, True,
              ["captured.commit is None, not a commit"])
    with Edit(COPY) as p:
        change(p, lambda d: d["captured"].update(release="V83"))
        check(r, "the stamp with a version where its release mark goes", CHECK, True,
              ["captured.release is 'V83', not a release mark"])
    with Edit(COPY) as p:
        change(p, lambda d: d["counts"].update(parts="nine"))
        check(r, "a count that is not a number", CHECK, True,
              ["counts.parts is 'nine', not a whole number"])
    with Edit(CHECK) as p:
        p.write_text(p.read_text(encoding="utf-8").replace(
            'UNSHOWN = {\n', 'UNSHOWN = {\n    "counts.welds": "no such count",\n', 1), encoding="utf-8")
        check(r, "an excuse for a value the copy does not have", CHECK, True,
              ["UNSHOWN names counts.welds, which the copy does not have"])
    check(r, "the copy and the page as they are", CHECK, False, [PASS])
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
