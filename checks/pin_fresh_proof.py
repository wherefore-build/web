#!/usr/bin/env python3
"""Prove checks/pin_fresh.py fails a pin left behind, and an index it cannot read.

Each case gives the check a stand-in for PyPI's JSON (`--index`) and a day to
judge from (`--today`), so nothing here touches the network, and requires it
to fail in the words of the case or, for the cases that must not fire, to
pass. The stand-ins are built around the release this copy of the repository
(checks/_copy.py) pins, so a moved pin never stales a case.

  fails   a release newer than the pin, published 4 days ago
          three releases newer than the pin, each named with its day
          an index that is not JSON, and one that is not there
  passes  a release newer than the pin, published yesterday
          the pin is the newest release
          a release candidate newer than the pin, out for a week

Usage:  python3 checks/pin_fresh_proof.py
"""
import datetime
import json
import pathlib
import re
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _copy                                                       # noqa: E402

root = _copy.fresh()
from wherefore.prove import check, report                         # noqa: E402

CHECK = "checks/pin_fresh.py"
TODAY = datetime.date(2026, 11, 23)
PIN = re.search(r"^wherefore-build==(\S+)", (root / "requirements-engine.txt").read_text(encoding="utf-8"), re.M).group(1)
DIR = pathlib.Path(tempfile.mkdtemp(prefix="pin-fresh-"))


def later(n):
    """The pin's version with its minor moved on by n: 0.27.0 -> 0.28.0."""
    parts = [int(x) for x in PIN.split(".")[:3]]
    parts += [0] * (3 - len(parts))
    return f"{parts[0]}.{parts[1] + n}.0"


def index(name, **days_ago):
    """A stand-in for PyPI's JSON: the pin a month old, and each version given, published that many days ago."""
    def files(ago):
        at = datetime.datetime.combine(TODAY - datetime.timedelta(days=ago), datetime.time(12, 0))
        stamp = at.strftime("%Y-%m-%dT%H:%M:%S.000000Z")
        return [{"packagetype": "bdist_wheel", "upload_time_iso_8601": stamp, "yanked": False},
                {"packagetype": "sdist", "upload_time_iso_8601": stamp, "yanked": False}]
    doc = {"info": {"name": "wherefore-build"}, "releases": {PIN: files(30)}}
    for v, ago in days_ago.items():
        doc["releases"][v] = files(ago)
    p = DIR / f"{name}.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    return str(p)


def day(ago):
    return str(TODAY - datetime.timedelta(days=ago))


def main():
    r = []
    on = ("--today", str(TODAY))
    one = later(1)
    check(r, "a release newer than the pin, published 4 days ago", CHECK, True,
          [f"the site pins wherefore-build=={PIN}", f"{one}  published {day(4)}, 4 days ago",
           f"branch `engine/{one}`"],
          "--index", index("four", **{one: 4}), *on)
    a, b, c = later(1), later(2), later(3)
    check(r, "three releases newer than the pin, each named", CHECK, True,
          ["3 newer releases are out", f"{a}  published {day(9)}", f"{b}  published {day(5)}",
           f"{c}  published {day(1)}, 1 day ago", f"The newest is {c}", f"branch `engine/{c}`"],
          "--index", index("three", **{a: 9, b: 5, c: 1}), *on)
    bad = DIR / "garbled.json"
    bad.write_text("<html>502 Bad Gateway</html>", encoding="utf-8")
    check(r, "an index that is not JSON", CHECK, True, ["could not read the index at", str(bad)],
          "--index", str(bad), *on)
    check(r, "an index that is not there", CHECK, True, ["could not read the index at", "FileNotFoundError"],
          "--index", str(DIR / "nowhere.json"), *on)
    check(r, "a release published yesterday - must not fire", CHECK, False,
          [f"the newest release, {one}, was published {day(1)}, inside the 3-day grace", f"branch `engine/{one}`"],
          "--index", index("yesterday", **{one: 1}), *on)
    check(r, "the pin is the newest - must not fire", CHECK, False,
          [f"the pin, {PIN}, is the newest release"],
          "--index", index("newest"), *on)
    check(r, "a release candidate out for a week - must not fire", CHECK, False,
          [f"the pin, {PIN}, is the newest release"],
          "--index", index("rc", **{f"{later(1)}rc1": 7, f"{later(1)}.dev3": 8}), *on)
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
