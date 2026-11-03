#!/usr/bin/env python3
"""The deployed site sends the policies site/_headers says, read the way Cloudflare reads it.

checks/model_turns.py serves the site with site/_headers read the way
Cloudflare documents it - every rule whose path matches adds its headers, and
`! Name` takes off what an earlier rule set - because the checks run before
anything is deployed. This asks the deployed site itself, after the deploy, so
a difference in Cloudflare's reading is caught where it happens: for each path
it requires the Content-Security-Policy the deployed site sends to be exactly
the one the check served, once. Above all, the site's own pages must run no
script and the pendulum's model must be allowed its own.

Usage:  python3 .github/scripts/served_headers.py URL
"""
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "checks"))
from model_turns import rules, served                             # noqa: E402

PATHS = ("/", "/changelog/", "/brand/", "/pendulum/")


def sent(url):
    """Every policy the response to `url` carries, however Cloudflare joined them."""
    req = urllib.request.Request(url, headers={"User-Agent": "wherefore-co CI"})
    with urllib.request.urlopen(req, timeout=30) as r:
        values = r.headers.get_all("Content-Security-Policy") or []
    return [p.strip() for v in values for p in v.split(",") if p.strip()]


def main(base):
    base = base.rstrip("/")
    table, found = rules(), []
    for path in PATHS:
        want = served(path, table).get("content-security-policy", [])
        got = sent(base + path)
        if got != want:
            found.append(f"{path}\n     sent:   {got}\n     wanted: {want}")
    if found:
        print(f"::error::{base} does not send the policies site/_headers says:\n")
        for f in found:
            print(f"   {f}")
        return 1
    print(f"ok   {base} sends each of {', '.join(PATHS)} the one policy site/_headers says: "
          f"no script on the site's own pages, and the pendulum's model its own")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
