#!/usr/bin/env python3
"""Nothing on the site tells a visitor to install somebody else's package.

`wherefore` on PyPI is another project's (tracelore/wherefore, "Explains WHY
two datasets differ"); this one is published as `wherefore-build`.
The brand is still Wherefore and the command a
person types is still `wherefore`, so those are right wherever they appear.
The one slip that costs a visitor something is an install line that names the
bare `wherefore`: it installs another project's code. This reads every file in
site/ and fails such a line, naming the file and the line.

WHAT IT CANNOT SEE: an install line inside an image, or one written for an
installer it does not know. It knows pip, pipx and uv.

Usage:  python3 checks/install_line.py
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PACKAGE = "wherefore-build"

INSTALL = re.compile(r"\b(?:pip3?\s+install|pipx\s+install|uv\s+(?:pip\s+install|tool\s+install|add))"
                     r"(?:\s+-{1,2}[\w=-]+)*\s+wherefore(?![\w.-])")


def faults():
    found = []
    for path in sorted(SITE.rglob("*")):
        if not path.is_file() or path.suffix in (".woff2", ".png", ".jpg", ".svg"):
            continue
        rel = path.relative_to(ROOT).as_posix()
        for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for m in INSTALL.finditer(line):
                found.append(f"{rel}:{n}: `{m.group(0)}` installs another project; ours is {PACKAGE}")
    return found


def main():
    found = faults()
    if found:
        print("::error::the site tells a visitor to install a package that is not Wherefore:\n")
        for f in found:
            print(f"   {f}")
        return 1
    print(f"ok   every install line on the site names {PACKAGE}, or there is none yet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
