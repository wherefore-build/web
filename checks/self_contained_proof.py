#!/usr/bin/env python3
"""Prove checks/self_contained.py fails a page that loads from elsewhere or links to nothing.

Each case breaks a copy of this repository (checks/_copy.py) and requires the
check to fail in the words of the case, or - for the cases that must not fire -
to pass.

  fails   a stylesheet from a font host
          a background picture from another host, in the page's style
          a link to a section that does not exist
          a picture that is not in the site
  passes  a link to a page elsewhere, and an address to write to
          the site as it is

Usage:  python3 checks/self_contained_proof.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _copy                                                       # noqa: E402

_copy.fresh()
from wherefore.prove import Edit, check, report                   # noqa: E402

CHECK = "checks/self_contained.py"
PAGE = "site/index.html"
PASS = "every link on it goes somewhere"


def plant(p, before, after):
    text = p.read_text(encoding="utf-8")
    if before not in text:
        raise SystemExit(f"{PAGE} no longer holds {before!r} - re-anchor this case")
    p.write_text(text.replace(before, after, 1), encoding="utf-8")


def main():
    r = []
    with Edit(PAGE) as p:
        plant(p, "</head>", '<link rel="stylesheet" href="https://fonts.example.com/css?family=Inter">\n</head>')
        check(r, "a stylesheet from a font host", CHECK, True,
              [f"{PAGE}:", 'href="https://fonts.example.com/css?family=Inter"', "loads from outside the site"])
    with Edit(PAGE) as p:
        plant(p, "</style>", "body { background: url(https://cdn.example.com/paper.png); }\n</style>")
        check(r, "a background picture from another host, in the style", CHECK, True,
              ['url()="https://cdn.example.com/paper.png"', "loads from outside the site"])
    with Edit(PAGE) as p:
        plant(p, 'href="#how"', 'href="#hwo"')
        check(r, "a link to a section that does not exist", CHECK, True,
              ['href="#hwo"', "names nothing on the page"])
    with Edit(PAGE) as p:
        plant(p, "</main>", '<img src="hero.png" alt="">\n</main>')
        check(r, "a picture that is not in the site", CHECK, True,
              ['src="hero.png"', "is not a file in site/"])
    with Edit(PAGE) as p:
        plant(p, "</main>", '<p><a href="https://github.com/">elsewhere</a> '
                            '<a href="mailto:someone@example.com">write</a></p>\n</main>')
        check(r, "a link elsewhere and an address - must not fire", CHECK, False, [PASS])
    check(r, "the site as it is", CHECK, False, [PASS])
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
