#!/usr/bin/env python3
"""Prove checks/brand_reasons.py fails a brand decision without its reason.

Each case breaks a copy of this repository (checks/_copy.py) - the brand's
source - and requires the check to fail in the words of the case, or, for the
case that must not fire, to pass.

  fails   a colour whose `why` was emptied
          a typeface with no `role`
          a colour that is the same as one nobody defined
          a colour that says both `same_as` and `value`
          the icon with its why emptied
          the icon in a colour nobody defined
          the icon on a ground no contrast pair holds
          the idea removed
  passes  the brand as it is

Usage:  python3 checks/brand_reasons_proof.py
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _copy                                                       # noqa: E402

_copy.fresh()
from wherefore.prove import Edit, check, report                   # noqa: E402

CHECK = "checks/brand_reasons.py"
TOKENS = "brand/tokens.json"
PASS = "every colour, typeface and radius says what it is for and why"


def tokens(p, change):
    doc = json.loads(p.read_text(encoding="utf-8"))
    change(doc)
    p.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    r = []
    with Edit(TOKENS) as p:
        tokens(p, lambda d: d["color"]["accent"].update(why=""))
        check(r, "a colour with its why emptied", CHECK, True, ["color.accent has no `why`"])
    with Edit(TOKENS) as p:
        tokens(p, lambda d: d["type"]["mono"].pop("role"))
        check(r, "a typeface with no role", CHECK, True, ["type.mono has no `role`"])
    with Edit(TOKENS) as p:
        tokens(p, lambda d: d["color"]["on-accent"].update(same_as="paper"))
        check(r, "the same as a colour nobody defined", CHECK, True,
              ["color.on-accent is the same as 'paper', which brand/tokens.json does not define"])
    with Edit(TOKENS) as p:
        tokens(p, lambda d: d["color"]["on-accent"].update(value="#0B0C0E"))
        check(r, "a colour said twice over", CHECK, True,
              ["color.on-accent says both `same_as` and `value`"])
    with Edit(TOKENS) as p:
        tokens(p, lambda d: d["icon"].update(why=" "))
        check(r, "the icon with its why emptied", CHECK, True, ["icon has no `why`"])
    with Edit(TOKENS) as p:
        tokens(p, lambda d: d["icon"].update(color="lime"))
        check(r, "the icon in a colour nobody defined", CHECK, True,
              ["icon.color is 'lime', which brand/tokens.json does not define"])
    with Edit(TOKENS) as p:
        tokens(p, lambda d: d["icon"].update(on="accent"))
        check(r, "the icon on a ground no pair holds", CHECK, True,
              ["the icon sets accent on accent, which is not a pair checks/contrast.py holds"])
    with Edit(TOKENS) as p:
        tokens(p, lambda d: d.pop("idea"))
        check(r, "the idea removed", CHECK, True, ["the brand has no `idea`"])
    check(r, "the brand as it is", CHECK, False, [PASS])
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
