#!/usr/bin/env python3
"""The site reaches nothing outside itself, and every link on it goes somewhere.

Two ways a page can be current with its source - the gate holds that - and
still be wrong to the person reading it:

- IT LOADS SOMETHING FROM ELSEWHERE. A stylesheet, a font, a script or a
  picture fetched from another host changes when that host does, so the page a
  visitor sees is no longer the page that was committed and checked, and every
  visitor is announced to whoever serves it. The site's headers forbid it too
  (site/_headers); this fails it before a browser has to.
- A LINK GOES NOWHERE. A `#how` with no element called `how` is a control that
  does nothing when pressed - found, on the company's first client, by a thumb
  on a phone after every check had passed. A path to a file that is not in the
  site is the same fault one level up.

WHAT PASSES. A link to a page elsewhere (`https://...`) is a place a visitor
chooses to go, not something the page loads, and is not judged. `mailto:` is
the same. Everything the page LOADS - `src`, a stylesheet's `href`, `srcset`,
`poster`, `url(...)` in a style - must be in site/. So must everything a
stylesheet in site/ loads - a font's `url(...)`, an `@import` - resolved from
where that stylesheet sits.

WHAT IT CANNOT SEE: whether a page elsewhere still exists, and anything a
script would build at run time. The site's own pages run none; the one page
that does, the pendulum's framed model, is held to loading nothing by the
policy site/_headers gives its path (checks/model_turns.py).

Usage:  python3 checks/self_contained.py
"""
import html.parser
import pathlib
import re
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

LOADS = {"src", "poster", "data"}
URL_IN_STYLE = re.compile(r"url\(\s*['\"]?([^'\")]+)")
IMPORT = re.compile(r"@import\s+['\"]([^'\"]+)")


class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.refs, self.style, self._in_style = set(), [], [], False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "name" in a:
            self.ids.add(a["name"])
        line = self.getpos()[0]
        for k, v in attrs:
            if v is None:
                continue
            if k in LOADS:
                self.refs.append((line, tag, k, v, "loads"))
            elif k == "srcset":
                for part in v.split(","):
                    if part.strip():
                        self.refs.append((line, tag, k, part.split()[0], "loads"))
            elif k == "href":
                rel = (a.get("rel") or "").split()
                loads = tag == "link" and not {"canonical", "alternate"} & set(rel)
                self.refs.append((line, tag, k, v, "loads" if loads else "links"))
            elif k == "style":
                self.style.append((line, v))
        self._in_style = tag == "style"

    def handle_endtag(self, tag):
        self._in_style = False

    def handle_data(self, data):
        if self._in_style:
            self.style.append((self.getpos()[0], data))


def faults():
    found = []
    pages = sorted(SITE.rglob("*.html"))
    if not pages:
        return [f"{SITE.relative_to(ROOT)}/ holds no page"]
    for path in pages:
        rel = path.relative_to(ROOT).as_posix()
        page = Page()
        page.feed(path.read_text(encoding="utf-8"))
        refs = list(page.refs)
        for line, text in page.style:
            for m in URL_IN_STYLE.finditer(text):
                refs.append((line + text.count("\n", 0, m.start()), "style", "url()", m.group(1), "loads"))
        for line, tag, attr, value, kind in refs:
            said = f'{rel}:{line}: <{tag} {attr}="{value}">'
            u = urllib.parse.urlsplit(value.strip())
            if u.scheme in ("mailto", "tel") and kind == "links":
                continue
            if u.scheme == "data" and kind == "loads":
                continue
            if u.scheme or u.netloc:
                if kind == "loads":
                    found.append(f"{said} loads from outside the site - the page a visitor "
                                 f"sees would change when that host does")
                continue
            if not u.path:
                if u.fragment and u.fragment not in page.ids:
                    found.append(f"{said} names nothing on the page - a link that does nothing "
                                 f"when pressed")
                continue
            target = (SITE / u.path.lstrip("/")) if u.path.startswith("/") else (path.parent / u.path)
            if target.is_dir() or u.path.endswith("/"):
                target = target / "index.html"
            target = target.resolve()
            if SITE.resolve() not in target.parents or not target.is_file():
                found.append(f"{said} is not a file in {SITE.relative_to(ROOT)}/")
    for path in sorted(SITE.rglob("*.css")):
        rel = path.relative_to(ROOT).as_posix()
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for value in [m.group(1) for m in URL_IN_STYLE.finditer(line)] + \
                         [m.group(1) for m in IMPORT.finditer(line)]:
                said = f"{rel}:{n}: url({value})"
                u = urllib.parse.urlsplit(value.strip())
                if u.scheme == "data":
                    continue
                if u.scheme or u.netloc:
                    found.append(f"{said} loads from outside the site - the page a visitor "
                                 f"sees would change when that host does")
                    continue
                target = (SITE / u.path.lstrip("/")) if u.path.startswith("/") else (path.parent / u.path)
                target = target.resolve()
                if SITE.resolve() not in target.parents or not target.is_file():
                    found.append(f"{said} is not a file in {SITE.relative_to(ROOT)}/")
    return found


def main():
    found = faults()
    if found:
        print("::error::the site reaches outside itself, or a link on it goes nowhere:\n")
        for f in found:
            print(f"   {f}")
        return 1
    print(f"ok   every page and stylesheet in {SITE.relative_to(ROOT)}/ loads only what is in it, "
          f"and every link on it goes somewhere")
    return 0


if __name__ == "__main__":
    sys.exit(main())
