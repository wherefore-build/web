#!/usr/bin/env python3
"""The engine this site pins is never left behind the newest release for long.

The site describes the release requirements-engine.txt pins, and a release
reaches it only when the pin moves. Nothing made it move: the pin watch
(.github/workflows/wherefore-pin.yml) opens a pull request for each release,
and the one for 0.24.0 sat open from 7 November while 0.24.1 to 0.27.0 shipped,
with every check green (owner, 23 November 2026). So this reads every release
from PyPI, with the day it was published, and fails once a release newer than
the pin has been out for more than GRACE_DAYS, naming each release the site is
missing and how to take it.

It passes, naming the newest release, when the pin is the newest, or when
every newer release is still inside the grace. A release PyPI holds only as a
pre-release (dev, a, b, rc) or yanked is not one a site should pin, so it is
not counted.

WHEN IT CANNOT READ PyPI, IT FAILS, saying so. A check that passes because it
could not look says nothing; and the job it runs in installs the engine from
PyPI first, so an index that cannot be read has already stopped the job.

Usage:  python3 checks/pin_fresh.py [--index FILE] [--today YYYY-MM-DD]

  --index FILE   read the release history from FILE, a stand-in shaped like
                 PyPI's JSON API, instead of PyPI (for the proof: no network)
  --today DATE   judge as if today were DATE (UTC), instead of today
"""
import argparse
import datetime
import json
import pathlib
import re
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PIN_FILE = ROOT / "requirements-engine.txt"
PACKAGE = "wherefore-build"
INDEX = f"https://pypi.org/pypi/{PACKAGE}/json"
# THREE DAYS: long enough for the pin watch, which asks PyPI every few hours,
# to open its pull request and for the owner to test its preview on a phone
# and merge it; short enough that the site never again describes a product
# four releases old for a fortnight.
GRACE_DAYS = 3
TRIES = 3            # a refused or dropped connection is asked again, twice, before the check fails
FINAL = re.compile(r"^(\d+(?:\.\d+)*)(?:\.post(\d+))?$")


def key(version):
    """A final release's order, or None for a pre-release: 0.27.0 < 0.27.0.post1 < 0.27.1."""
    m = FINAL.match(version)
    if not m:
        return None
    nums = tuple(int(n) for n in m.group(1).split("."))
    nums += (0,) * (6 - len(nums))
    return nums + (int(m.group(2) or -1),)


def pinned():
    text = PIN_FILE.read_text(encoding="utf-8")
    m = re.search(rf"^\s*{re.escape(PACKAGE)}\s*==\s*([^\s#;]+)", text, re.M)
    if not m:
        raise SystemExit(f"::error::{PIN_FILE.name} pins no `{PACKAGE}==VERSION`: there is no pin to judge")
    return m.group(1)


def read_index(path):
    """PyPI's JSON for the package, from `path` or from PyPI; raises on anything it cannot read."""
    if path:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    last = None
    for attempt in range(TRIES):
        try:
            req = urllib.request.Request(INDEX, headers={"Accept": "application/json", "User-Agent": "pin-fresh-check"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:                                   # noqa: BLE001 - every way it fails is one answer
            last = e
            if attempt + 1 < TRIES:
                time.sleep(2 * (attempt + 1))
    raise last


def releases(doc):
    """{version: the day it was published}, final releases only, yanked ones left out."""
    out = {}
    for version, files in doc["releases"].items():
        if key(version) is None or not files or all(f.get("yanked") for f in files):
            continue
        out[version] = min(datetime.datetime.fromisoformat(f["upload_time_iso_8601"].replace("Z", "+00:00"))
                           for f in files if not f.get("yanked")).date()
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--index", help="a stand-in for PyPI's JSON, read instead of PyPI")
    ap.add_argument("--today", help="judge as if today were this day, YYYY-MM-DD (UTC)")
    a = ap.parse_args(argv)
    today = (datetime.date.fromisoformat(a.today) if a.today
             else datetime.datetime.now(datetime.timezone.utc).date())
    pin = pinned()
    where = a.index or INDEX
    try:
        published = releases(read_index(a.index))
        published = {v: d for v, d in published.items() if d <= today}     # a day judged from sees no later release
    except Exception as e:                                       # noqa: BLE001
        print(f"::error::could not read the index at {where} ({type(e).__name__}: {e}), so whether the pin, "
              f"{pin}, is behind is not known. This fails rather than pass without looking: run it again once "
              f"the index answers")
        return 1
    if key(pin) is None:
        print(f"::error::{PIN_FILE.name} pins {PACKAGE}=={pin}, a pre-release: a site pins a final release")
        return 1
    if not published:
        print(f"::error::{where} lists no final release of {PACKAGE}")
        return 1
    if pin not in published:
        print(f"::error::{PIN_FILE.name} pins {PACKAGE}=={pin}, which {where} does not list as a release")
        return 1
    newest = max(published, key=key)
    missing = sorted((v for v in published if key(v) > key(pin)), key=key)
    if not missing:
        print(f"ok   the pin, {pin}, is the newest release of {PACKAGE} (published {published[pin]})")
        return 0
    late = [v for v in missing if (today - published[v]).days > GRACE_DAYS]

    def line(v):
        age = (today - published[v]).days
        return f"   {v}  published {published[v]}, {age} day{'' if age == 1 else 's'} ago"
    if not late:
        print(f"ok   the pin is {pin}; the newest release, {newest}, was published {published[newest]}, "
              f"inside the {GRACE_DAYS}-day grace. Newer than the pin:")
        for v in missing:
            print(line(v))
        print(f"This fails from {published[missing[0]] + datetime.timedelta(days=GRACE_DAYS + 1)}: take the pin "
              f"watch's pull request (branch `engine/{newest}`) or move the pin before then")
        return 0
    print(f"::error::the site pins {PACKAGE}=={pin}, and {len(missing)} newer "
          f"release{'' if len(missing) == 1 else 's'} {'is' if len(missing) == 1 else 'are'} out, "
          f"the first more than {GRACE_DAYS} days ago. The site is missing:")
    for v in missing:
        print(line(v))
    print(f"\nThe newest is {newest}. Take the pin watch's pull request (branch `engine/{newest}`), "
          f"or move the pin in {PIN_FILE.name} to {PACKAGE}=={newest}, rebuild, and describe what it ships.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
