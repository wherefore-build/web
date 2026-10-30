#!/usr/bin/env python3
"""Read the pendulum's counts at its main, and write facts/pendulum.json if they moved.

chaotic-pendulums-co counts itself into docs/case-study.json - its proofs, its
parts, its print plates and the release they stand at - and the case study is
built from the copy of that file in facts/pendulum.json. This reads the
pendulum's main through the GitHub API: the commit it points at, then the file
at that commit, so the stamp and the counts are one moment. When the counts
differ from the copy's, it writes the copy again, stamped with the commit and
the day that commit was made, and says so; when they do not, it writes nothing,
so a pendulum push that moved no count opens no pull request.

The pendulum is private, so this needs a token that can read it, in
GH_TOKEN (PENDULUM_READ_TOKEN in .github/workflows/case-study.yml).

Prints changed=true or changed=false to $GITHUB_OUTPUT when there is one, and a
line saying what moved.

Usage:  GH_TOKEN=... python3 .github/scripts/case_study.py
"""
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
COPY = ROOT / "facts/pendulum.json"
API = "https://api.github.com"


def get(path, raw=False):
    req = urllib.request.Request(API + path)
    req.add_header("Authorization", "Bearer " + os.environ["GH_TOKEN"])
    req.add_header("Accept", "application/vnd.github.raw+json" if raw else "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        sys.exit(f"::error::GitHub said HTTP {e.code} for {path}. If it is 401 or 403, PENDULUM_READ_TOKEN "
                 f"cannot read the pendulum: README.md, under The case study, says what it needs")


def output(changed, line):
    print(line)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write(f"changed={'true' if changed else 'false'}\n")


def main():
    if not os.environ.get("GH_TOKEN"):
        sys.exit("::error::no GH_TOKEN: this reads a private repository, so it needs PENDULUM_READ_TOKEN")
    copy = json.loads(COPY.read_text(encoding="utf-8"))
    repo, path = copy["captured"]["from"], copy["captured"]["path"]
    head = get(f"/repos/{repo}/commits/main")
    if head is None:
        sys.exit(f"::error::{repo} has no main this token can see")
    sha = head["sha"]
    counts = get(f"/repos/{repo}/contents/{path}?ref={sha}", raw=True)
    if counts is None:
        sys.exit(f"::error::{repo} has no {path} at main ({sha[:8]}): its docs/case_study.py has not "
                 f"reached main, so there is nothing to read yet")
    counts.pop("note", None)
    if counts == copy["counts"]:
        output(False, f"the pendulum's counts at {sha[:8]} are the copy's: nothing to do")
        return 0
    moved = ", ".join(f"{k} {copy['counts'].get(k)!r} -> {v!r}" for k, v in counts.items()
                      if copy["counts"].get(k) != v)
    copy["captured"].update(commit=sha, on=head["commit"]["committer"]["date"][:10])
    copy["counts"] = counts
    COPY.write_text(json.dumps(copy, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    output(True, f"the pendulum's counts moved at {sha[:8]}: {moved}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
