#!/usr/bin/env python3
"""site/: the company's site, from facts/company.json and the engine it pins.

What the page says about the company is facts/company.json's. What it says
about the product - its principles, its commands and its version - is the
engine's own, read from the installed release that requirements-engine.txt
pins. So a release that renames a command or rewords a principle changes this
page by being pinned, never by being retyped, and the gate fails the page until
it is regenerated. Nothing here types a fact; what is here is layout, and the
styles are gen/page.css's.

STATUS. site.status is "draft" or "launched", and nothing else: an unknown
status stops the build. A draft says so in a banner across the page and asks
not to be indexed, both in the page and in the headers Cloudflare Pages serves
with it (site/_headers). Launching is the owner's decision, and it is one word
in the facts.

A NULL IS A FACT NOT DECIDED YET. With no domain the page names no canonical
address, and with no contact it offers no address to write to. Each appears
when its fact does.

Run from gen/, as wherefore.json says. Writes site/index.html and site/_headers.
"""
import html
import json
import pathlib
import re
from importlib.resources import files

import wherefore

ROOT = pathlib.Path(__file__).resolve().parents[1]
FACTS = json.loads((ROOT / "facts/company.json").read_text(encoding="utf-8"))
CSS = (ROOT / "gen/page.css").read_text(encoding="utf-8")
SITE = ROOT / "site"
STATUSES = ("draft", "launched")


def engine(name):
    """One of the engine's own data files, from the release this runs under."""
    data = files("wherefore") / name
    if not data.is_file():
        raise SystemExit(f"the pinned engine, wherefore {wherefore.__version__}, has no {name}: "
                         f"the site needs 0.1.1 or later - move requirements-engine.txt")
    return json.loads(data.read_text(encoding="utf-8"))


def esc(text):
    return html.escape(text, quote=True)


def em(text):
    """Escaped, with the engine's `*word*` emphasis."""
    return re.sub(r"\*([^*\n]+)\*", r"<em>\1</em>", esc(text))


def page(f, principles, commands, version):
    company, site = f["company"], f["site"]
    if site["status"] not in STATUSES:
        raise SystemExit(f"site.status is {site['status']!r}: it is one of {', '.join(STATUSES)}")
    draft = site["status"] == "draft"
    head = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        f"<title>{esc(site['title'])}</title>",
        f'<meta name="description" content="{esc(site["description"])}">',
        '<meta name="color-scheme" content="light dark">',
    ]
    if draft:
        head.append('<meta name="robots" content="noindex, nofollow">')
    if company["domain"]:
        head.append(f'<link rel="canonical" href="https://{esc(company["domain"])}/">')
    head.append(f"<style>\n{CSS}</style>")

    banner = (f'<div class="draft" role="note"><span class="draft-mark">Draft</span> '
              f'{esc(site["draft_banner"])}</div>\n') if draft else ""

    steps = "\n".join(
        f'<li><h3>{esc(s["name"])}</h3><p>{esc(s["text"])}</p></li>' for s in f["how"]["steps"])
    rules = "\n".join(
        f'<li><strong>{em(p["rule"])}</strong>' + (f" {em(p['says'])}" if p["says"] else "") + "</li>"
        for p in principles)
    listing = "\n".join(
        f'<div class="cmd"><dt><code>{esc(c["usage"])}</code></dt><dd>{esc(c["does"])}</dd></div>'
        for c in commands)
    access = f'<p>{esc(f["access"]["text"])} Version {esc(version)}.</p>'
    if company["contact"]:
        access += (f'<p><a class="write" href="mailto:{esc(company["contact"])}">'
                   f'{esc(company["contact"])}</a></p>')

    return f"""<!doctype html>
<html lang="en">
<head>
{chr(10).join(head)}
</head>
<body>
{banner}<header class="top"><div class="wrap"><a class="name" href="#top">{esc(company["name"])}</a>
<nav aria-label="On this page"><a href="#how">How</a><a href="#principles">Principles</a><a href="#interface">Interface</a><a href="#access">Access</a></nav></div></header>
<main id="top">
<section class="hero"><div class="wrap">
<h1>{esc(f["hero"]["headline"])}</h1>
<p class="lede">{esc(f["hero"]["lede"])}</p>
</div></section>
<section id="how"><div class="wrap">
<h2>{esc(f["how"]["heading"])}</h2>
<ol class="steps">
{steps}
</ol>
</div></section>
<section id="principles"><div class="wrap">
<h2>{esc(f["principles"]["heading"])}</h2>
<ol class="principles">
{rules}
</ol>
</div></section>
<section id="client"><div class="wrap">
<h2>{esc(f["client"]["heading"])}</h2>
<blockquote><p>{esc(f["client"]["text"])}</p></blockquote>
</div></section>
<section id="interface"><div class="wrap">
<h2>{esc(f["interface"]["heading"])}</h2>
<p>{esc(f["interface"]["lede"])}</p>
<dl class="terminal">
{listing}
</dl>
</div></section>
<section id="access"><div class="wrap">
<h2>{esc(f["access"]["heading"])}</h2>
{access}
</div></section>
</main>
<footer><div class="wrap"><p>{esc(f["colophon"])} Wherefore {esc(version)}.</p></div></footer>
</body>
</html>
"""


def headers(f):
    """What Cloudflare Pages sends with every file: nothing loads from
    elsewhere, and a draft is not indexed."""
    lines = [
        "/*",
        "  Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; img-src 'self' data:; "
        "base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
        "  X-Content-Type-Options: nosniff",
        "  Referrer-Policy: no-referrer",
    ]
    if f["site"]["status"] == "draft":
        lines.append("  X-Robots-Tag: noindex, nofollow")
    return "\n".join(lines) + "\n"


def main():
    principles = engine("principles.json")["principles"]
    commands = engine("commands.json")["commands"]
    SITE.mkdir(exist_ok=True)
    (SITE / "index.html").write_text(page(FACTS, principles, commands, wherefore.__version__),
                                     encoding="utf-8")
    (SITE / "_headers").write_text(headers(FACTS), encoding="utf-8")


if __name__ == "__main__":
    main()
