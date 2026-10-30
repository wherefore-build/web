#!/usr/bin/env python3
"""Prove checks/contrast.py fails a text colour that is not readable on its ground.

Each case breaks a copy of this repository (checks/_copy.py) and requires the
check to fail in the words of the case, or - for the case that must not fire -
to pass.

  fails   the muted grey darkened until captions cannot be read on the page
          a pair that names a colour the tokens do not define
          a colour that is not #RRGGBB, which cannot be measured
  passes  the brand as it is

Usage:  python3 checks/contrast_proof.py
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _copy                                                       # noqa: E402

_copy.fresh()
from wherefore.prove import Edit, check, report                   # noqa: E402

CHECK = "checks/contrast.py"
TOKENS = "brand/tokens.json"
PASS = "every text colour reaches its contrast"


def tokens(p, change):
    doc = json.loads(p.read_text(encoding="utf-8"))
    change(doc)
    p.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    r = []
    with Edit(TOKENS) as p:
        tokens(p, lambda d: d["color"]["muted"].update(value="#3A3D44"))
        check(r, "the muted grey darkened past reading", CHECK, True,
              ["muted on ground reaches", "it must reach 4.5:1"])
    with Edit(TOKENS) as p:
        tokens(p, lambda d: d["contrast"]["pairs"].append({"text": "grey", "on": "ground", "min": 4.5}))
        check(r, "a pair naming a colour nobody defined", CHECK, True,
              ["a pair names grey, which brand/tokens.json does not define"])
    with Edit(TOKENS) as p:
        tokens(p, lambda d: d["color"]["accent"].update(value="lime"))
        check(r, "a colour that cannot be measured", CHECK, True,
              ["accent is 'lime', which is not a #RRGGBB colour"])
    check(r, "the brand as it is", CHECK, False, [PASS])
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
