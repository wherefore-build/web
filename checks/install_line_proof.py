#!/usr/bin/env python3
"""Prove checks/install_line.py fails an install line that names another project.

Each case breaks a copy of this repository (checks/_copy.py) - the page a
visitor receives - and requires the check to fail in the words of the case,
or, for the cases that must not fire, to pass.

  fails   `pip install wherefore` on the page
          `pipx install wherefore`, and `uv tool install wherefore`
  passes  `pip install wherefore-build`, and the command `wherefore gate`
          the site as it is

Usage:  python3 checks/install_line_proof.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _copy                                                       # noqa: E402

_copy.fresh()
from wherefore.prove import Edit, check, report                   # noqa: E402

CHECK = "checks/install_line.py"
PAGE = "site/index.html"
SAID = "installs another project; ours is wherefore-build"
PASS = "every install line on the site names wherefore-build"


def plant(p, line):
    text = p.read_text(encoding="utf-8")
    if "</main>" not in text:
        raise SystemExit(f"{PAGE} no longer holds </main> - re-anchor this case")
    p.write_text(text.replace("</main>", f"<p><code>{line}</code></p>\n</main>", 1), encoding="utf-8")


def main():
    r = []
    with Edit(PAGE) as p:
        plant(p, "pip install wherefore")
        check(r, "pip install wherefore", CHECK, True, [f"{PAGE}:", "`pip install wherefore`", SAID])
    with Edit(PAGE) as p:
        plant(p, "pipx install wherefore")
        plant(p, "uv tool install wherefore")
        check(r, "pipx and uv, naming the bare wherefore", CHECK, True,
              ["`pipx install wherefore`", "`uv tool install wherefore`"])
    with Edit(PAGE) as p:
        plant(p, "pip install wherefore-build")
        plant(p, "wherefore gate")
        check(r, "the right package, and a command - must not fire", CHECK, False, [PASS])
    check(r, "the site as it is", CHECK, False, [PASS])
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
