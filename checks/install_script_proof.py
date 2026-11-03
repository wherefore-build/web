#!/usr/bin/env python3
"""Prove checks/install_script.py fails an installer that does the wrong thing.

Each case breaks site/install.sh in a copy of this repository (checks/_copy.py)
and requires the check to fail in the words of the case, or, for the case that
must not fire, to pass.

  fails   another project's package installed - the bare `wherefore`
          uv there and not used
          a Python too old for the release, let through
          a script sh cannot parse
  passes  the installer as gen/install.py writes it

Usage:  python3 checks/install_script_proof.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _copy                                                       # noqa: E402

_copy.fresh()
from wherefore.prove import Edit, check, report                   # noqa: E402

CHECK = "checks/install_script.py"
SCRIPT = "site/install.sh"
PASS = "the installer installs the pinned release"


def swap(p, old, new):
    text = p.read_text(encoding="utf-8")
    assert old in text, old
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


def main():
    r = []
    with Edit(SCRIPT) as p:
        swap(p, "PACKAGE=wherefore-build", "PACKAGE=wherefore")
        check(r, "another project's package", CHECK, True, ["installed 'wherefore', not 'wherefore-build'"])
    with Edit(SCRIPT) as p:
        swap(p, "if command -v uv >/dev/null", "if command -v uvx >/dev/null")
        check(r, "uv there and not used", CHECK, True,
              ["when uv and pipx and Python are all there, uv installed nothing"])
    with Edit(SCRIPT) as p:
        swap(p, '|| fail "$PACKAGE needs Python', '|| true # "$PACKAGE needs Python')
        check(r, "a Python too old, let through", CHECK, True, ["was accepted, not refused"])
    with Edit(SCRIPT) as p:
        p.write_text(p.read_text(encoding="utf-8") + "fi\n", encoding="utf-8")
        check(r, "a script sh cannot parse", CHECK, True, ["sh cannot parse"])
    check(r, "the installer as it is", CHECK, False, [PASS])
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
