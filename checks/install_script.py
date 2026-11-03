#!/usr/bin/env python3
"""The one-line installer installs the pinned release, whichever tool is there.

site/install.sh is what `curl -fsSL https://wherefore.sh | sh` runs, and the
gate holds it to gen/install.py. This holds what it DOES: it is run, under
`sh`, with a PATH that holds only stand-ins - a fake uv, pipx or Python that
writes down how it was called - so every path through it is exercised without
a network or touching this machine. It fails:

  - a script `sh -n` cannot parse;
  - any path that installs a package other than the pinned release's own
    (`wherefore-build`: `wherefore` on PyPI is another project's);
  - uv not preferred when it is there, then pipx, then Python's pip;
  - a Python older than the release needs, accepted rather than refused;
  - no Python and no installer, not refused in words;
  - the next steps not named.

WHAT IT CANNOT SEE: the real uv, pipx and PyPI. Whether the package installs
from PyPI is the release's to prove, once it is published there.

Usage:  python3 checks/install_script.py
"""
import importlib.metadata
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "site/install.sh"
DIST = "wherefore-build"

# A stand-in writes its name and arguments to $CALLS, and the fake installed
# command answers --version, so the script's last step can find it.
STAND_IN = """#!/bin/sh
printf '%s %s\\n' "$(basename "$0")" "$*" >> "$CALLS"
"""
FAKE_PYTHON = """#!/bin/sh
printf '%s %s\\n' "$(basename "$0")" "$*" >> "$CALLS"
case "$1" in
  -c) exit $PY_OLD ;;
  -V) echo "Python 3.8.10" ;;
esac
"""


def run(tools, old_python=False):
    """(exit code, output, calls) of the script with only `tools` on PATH."""
    with tempfile.TemporaryDirectory(prefix="wherefore-install-") as d:
        bin_ = pathlib.Path(d) / "bin"
        bin_.mkdir()
        for name in ("sh", "printf", "basename", "cat"):
            found = shutil.which(name)
            if found:
                (bin_ / name).symlink_to(found)
        for tool in tools:
            body = FAKE_PYTHON if tool.startswith("python") else STAND_IN
            (bin_ / tool).write_text(body, encoding="utf-8")
            (bin_ / tool).chmod(0o755)
        calls = pathlib.Path(d) / "calls"
        calls.touch()
        env = {"PATH": str(bin_), "CALLS": str(calls), "PY_OLD": "1" if old_python else "0", "HOME": d}
        r = subprocess.run([str(bin_ / "sh"), str(SCRIPT)], env=env, capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr, calls.read_text(encoding="utf-8").splitlines()


def faults():
    if not SCRIPT.is_file():
        return [f"{SCRIPT.relative_to(ROOT)} is not there: gen/install.py writes it"]
    found = []
    r = subprocess.run(["sh", "-n", str(SCRIPT)], capture_output=True, text=True)
    if r.returncode:
        return [f"sh cannot parse {SCRIPT.relative_to(ROOT)}: {r.stderr.strip()}"]
    name = importlib.metadata.metadata(DIST)["Name"]

    def installs(calls, tool):
        return [c for c in calls if c.split()[0] == tool and " install " in f" {c} "]

    cases = [
        ("uv and pipx and Python are all there", ["uv", "pipx", "python3", "wherefore"], "uv"),
        ("pipx and Python are there", ["pipx", "python3", "wherefore"], "pipx"),
        ("only Python is there", ["python3", "wherefore"], "python3"),
    ]
    for what, tools, by in cases:
        code, out, calls = run(tools)
        done = installs(calls, by)
        others = [c for c in calls if c.split()[0] in ("uv", "pipx", "python3") and c.split()[0] != by
                  and " install " in f" {c} "]
        if code:
            found.append(f"when {what}, the script failed ({code}):\n{out}")
        elif not done:
            found.append(f"when {what}, {by} installed nothing; the calls were {calls}")
        elif others:
            found.append(f"when {what}, it installed with {others[0].split()[0]} as well as {by}")
        elif not all(c.split()[-1] == name for c in done):
            found.append(f"when {what}, it installed {done[0].split()[-1]!r}, not {name!r}")
        if not code and ("scan" not in out or "init" not in out):
            found.append(f"when {what}, it did not name the next steps:\n{out}")

    code, out, calls = run(["python3", "wherefore"], old_python=True)
    if code == 0 or any(" install " in f" {c} " for c in calls):
        found.append(f"a Python older than {name} needs was accepted, not refused:\n{out}")
    elif "needs Python" not in out:
        found.append(f"a Python too old was refused, but not in words:\n{out}")

    code, out, calls = run([])
    if code == 0:
        found.append("with no uv, pipx or Python, the script said it succeeded")
    elif "no Python here" not in out:
        found.append(f"with nothing to install with, it failed without saying why:\n{out}")
    return found


def main():
    found = faults()
    if found:
        print("::error::the installer does not do what it says:\n")
        for f in found:
            print(f"   {f}")
        return 1
    print("ok   the installer installs the pinned release with uv, then pipx, then pip, "
          "refuses an old Python and an empty machine in words, and names the next steps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
