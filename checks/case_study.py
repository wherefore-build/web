#!/usr/bin/env python3
"""The case study's counts are a dated snapshot, and every one of them reaches the page.

facts/pendulum.json is the case study's counts - the pendulum's proofs, parts,
print plates and the release they stand at - counted once from
the pendulum's own repository at the commit it names, and gen/site.py reads the case
study's numbers from it. Nothing reads the pendulum again: the owner decided
the two repositories stay apart, since the pendulum may be open-sourced or
split out, and a case study is a dated story anyway. The release this corpus
pins sweeps only the first declared source for reach (`reach` in
wherefore.json), so this does for the snapshot what that does for the facts,
and checks what only a snapshot needs:

  - THE STAMP. `captured` names the repository, the path, the commit (forty
    hex digits), the day (YYYY-MM-DD) and the release mark (sixteen hex
    digits) the pendulum published for the release it was counted at. A copy
    that cannot say where it came from is a typed number with extra steps.
  - THE COUNTS ARE COUNTS. proofs, parts and plates are whole numbers, and the
    pack has a version and an ISO date.
  - EVERY VALUE IS DECIDED. Each is either on the page or named in UNSHOWN
    below with the reason it is not. A count somebody adds to the snapshot
    fails here until they decide whether the page says it.
  - EVERY VALUE ON THE PAGE REACHES IT. Each is moved, one at a time, in a copy
    of this repository (checks/_copy.py); the page is regenerated and must
    differ. A number typed into the facts instead of read from the copy does
    not move, and fails.

WHAT IT CANNOT SEE: whether the snapshot is current with the pendulum - that
is `wherefore check upstream`'s, which reads the pendulum's /release.json and
fails when it names another release than captured.release. This one stays
offline.

Usage:  python3 checks/case_study.py
"""
import json
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _copy                                                       # noqa: E402

ROOT = _copy.ROOT
COPY = "facts/pendulum.json"
PAGE = "site/index.html"

UNSHOWN = {
    "captured.from": "where the copy was read from. The case study links the pendulum's live site; its repository is private",
    "captured.path": "the file the copy was read from, for whoever audits it",
    "captured.commit": "the pendulum commit the copy was read at, for whoever audits it. A visitor is told the release",
    "captured.release": "the mark the pendulum's public site published for that release, which says nothing to a "
                        "visitor: `wherefore check upstream` holds it to the site's /release.json",
    "counts.pack.date": "the day the release was cut. The page says the day the pendulum was counted, captured.on",
    "counts.pack.draft": "the draft open in the pendulum, if any. The counts are quoted at the release a draft stands "
                         "on, counts.pack.version, because a draft is not a pack anybody is handed",
}


def leaves(doc, path=""):
    """Every value in the copy, by dotted path, the note about the file aside."""
    for k, v in doc.items():
        p = f"{path}.{k}" if path else k
        if p == "note":
            continue
        if isinstance(v, dict):
            yield from leaves(v, p)
        else:
            yield p, v


def stamp_faults(doc):
    found = []
    c = doc.get("captured") or {}
    for field in ("from", "path"):
        if not str(c.get(field, "")).strip():
            found.append(f"captured.{field} is missing: the copy does not say where it was read")
    if not re.fullmatch(r"[0-9a-f]{40}", str(c.get("commit", ""))):
        found.append(f"captured.commit is {c.get('commit')!r}, not a commit: the copy does not say what it was read at")
    if not re.fullmatch(r"[0-9a-f]{16}", str(c.get("release", ""))):
        found.append(f"captured.release is {c.get('release')!r}, not a release mark: nothing can tell when the "
                     f"pendulum has cut another release")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(c.get("on", ""))):
        found.append(f"captured.on is {c.get('on')!r}, not a day (YYYY-MM-DD)")
    n = doc.get("counts") or {}
    for field in ("proofs", "parts", "plates"):
        v = n.get(field)
        if not (isinstance(v, int) and not isinstance(v, bool) and v >= 0):
            found.append(f"counts.{field} is {v!r}, not a whole number")
    pack = n.get("pack") or {}
    if not (isinstance(pack.get("version"), int) and not isinstance(pack.get("version"), bool)):
        found.append(f"counts.pack.version is {pack.get('version')!r}, not a release number")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(pack.get("date", ""))):
        found.append(f"counts.pack.date is {pack.get('date')!r}, not a day (YYYY-MM-DD)")
    return found


def nudged(path, v):
    """The value, moved enough that a page reading it must change."""
    if path == "captured.on":
        y, rest = v.split("-", 1)
        return f"{int(y) + 1}-{rest}"
    if isinstance(v, int) and not isinstance(v, bool):
        return v + 1000
    return f"{v} (probe)"


def put(doc, path, value):
    *head, last = path.split(".")
    node = doc
    for k in head:
        node = node[k]
    node[last] = value


def render(root):
    r = subprocess.run([sys.executable, "site.py"], cwd=root / "gen", capture_output=True, text=True)
    return (root / PAGE).read_bytes() if r.returncode == 0 else None


def main():
    doc = json.loads((ROOT / COPY).read_text(encoding="utf-8"))
    found = stamp_faults(doc)
    values = dict(leaves(doc))
    for p in values:
        if p not in UNSHOWN and not p.startswith(("captured.", "counts.")):
            found.append(f"{p} is outside `captured` and `counts`: the snapshot is not shaped as `captured` and `counts`")
    for p in UNSHOWN:
        if p not in values:
            found.append(f"UNSHOWN names {p}, which the copy does not have: an excuse for nothing")
    shown = [p for p in values if p not in UNSHOWN]
    if not found:
        root = _copy.fresh()
        before = render(root)
        if before is None:
            found.append("gen/site.py fails on the copy as it is")
        text = (root / COPY).read_text(encoding="utf-8")
        for p in shown if before is not None else []:
            moved = json.loads(text)
            put(moved, p, nudged(p, values[p]))
            (root / COPY).write_text(json.dumps(moved, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            after = render(root)
            (root / COPY).write_text(text, encoding="utf-8")
            if after is None:
                print(f"  ok   {p:24} {values[p]!r} -> {nudged(p, values[p])!r}   site.py refused")
            elif after == before:
                found.append(f"{p} moved ({values[p]!r} -> {nudged(p, values[p])!r}) and the page did not: it is "
                             f"shown nowhere, or a typed copy is shown in its place. Read it in gen/site.py, or "
                             f"name it in UNSHOWN with the reason")
            else:
                print(f"  ok   {p:24} {values[p]!r} -> {nudged(p, values[p])!r}")
    if found:
        print(f"::error::{COPY}, the pendulum's counts, is not what the case study is built from:\n")
        for f in found:
            print(f"   {f}")
        return 1
    print(f"\nthe copy says where and when it was read, and each of its {len(shown)} values on the page "
          f"reaches it; {len(UNSHOWN)} more are not shown, each for a stated reason")
    return 0


if __name__ == "__main__":
    sys.exit(main())
