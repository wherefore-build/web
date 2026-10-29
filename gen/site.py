#!/usr/bin/env python3
"""site/: the company's site, from facts/company.json and the engine it pins.

What the page says about the company is facts/company.json's. What it says
about the product - its version, and the commands it names - is the engine's
own, read from the installed release that requirements-engine.txt pins: a
command the page names must be one that release has, or the build stops. So a
release that renames a command fails this page until the facts follow it, and
a version moves on the page by being pinned, never by being retyped. Nothing
here types a fact; what is here is layout. The look is the brand's: every page
links site/brand.css, which gen/brand.py writes from brand/tokens.json, and
site/page.css, gen/page.css served as it is.

ONE NUMBER, ONCE. The demo's before and after, its count of assets and how
many of them are generated are said once - the numbers in `demo`, the length
of its list - and every line that mentions one names it as `{before}`,
`{after}`, `{total}` and the rest, which fill() fills. A name fill() does not
know stops the build.

NO SCRIPT. The demo's three steps and the questions beside it are radio
buttons and their labels, and gen/page.css shows what the checked one selects.
So they work under a policy that runs no script at all (site/_headers), and
checks/controls_press.py presses every one of them, cold, at a phone's width.

STATUS. site.status is "draft" or "launched", and nothing else: an unknown
status stops the build. A draft says so in a banner across the page and asks
not to be indexed, both in the page and in the headers Cloudflare serves with
it (site/_headers). Launching is the owner's decision, and it is one word in
the facts.

A NULL IS A FACT NOT DECIDED YET. With no domain the page names no canonical
address, with no contact it offers no address to write to and says the pilot
is not open, and with no terms it states none. Each appears when its fact does.

Run from gen/, as wherefore.json says, after brand.py. Writes site/index.html,
site/page.css and site/_headers.
"""
import json
import shutil
import string
from importlib.resources import files

import wherefore
from kit import FACTS, ROOT, SITE, banner, esc, head, status

VERSION = wherefore.__version__


def engine(name):
    """One of the engine's own data files, from the release this runs under."""
    data = files("wherefore") / name
    if not data.is_file():
        raise SystemExit(f"the pinned engine, wherefore {VERSION}, has no {name}: "
                         f"the site needs 0.1.1 or later - move requirements-engine.txt")
    return json.loads(data.read_text(encoding="utf-8"))


COMMANDS = engine("commands.json")["commands"]


def command(usage):
    """A command the page names, refused unless the pinned release has it."""
    for c in COMMANDS:
        if c["usage"] == usage or c["usage"].startswith(usage + " "):
            return usage
    raise SystemExit(f"the page names `{usage}`, which wherefore {VERSION} does not have: "
                     f"its commands are {', '.join(c['usage'] for c in COMMANDS)}")


def num(v):
    return f"{v:g}" if isinstance(v, float) else str(v)


def fill(text, **values):
    """A line from the facts, with each `{name}` in it filled; an unknown name stops the build."""
    names = [n for _, n, _, _ in string.Formatter().parse(text) if n is not None]
    unknown = [n for n in names if n not in values]
    if unknown:
        raise SystemExit(f"{text!r} names {{{unknown[0]}}}, which is not one of "
                         f"{', '.join('{' + k + '}' for k in values)}")
    return text.format(**{k: num(v) for k, v in values.items()})


def said(words):
    """`a`, `a and b`, `a, b and c` - each in code."""
    codes = [f"<code>{esc(w)}</code>" for w in words]
    return codes[0] if len(codes) == 1 else ", ".join(codes[:-1]) + " and " + codes[-1]


def at(*stages):
    """The classes that show an element only at these steps of the demo."""
    return "at " + " ".join(f"at{s}" for s in stages)


def demo(d):
    """The ripple: one fact, every asset that states it, and the three steps of changing it."""
    hand = [a for a in d["assets"] if a.get("by_hand")]
    if len(hand) != 1:
        raise SystemExit(f"demo.assets has {len(hand)} written by hand: the demo's third step fixes exactly one")
    hand_name = hand[0]["name"].lower()
    counts = dict(before=d["before"], after=d["after"], total=len(d["assets"]),
                  rebuilt=len(d["assets"]) - 1, hand=hand_name)
    if len(d["stages"]) != 3 or len(d["said"]) != 3:
        raise SystemExit("demo.stages and demo.said each have three lines: today, the change, the fix")
    b = d["badges"]

    inputs = "\n".join(f'<input class="state" type="radio" name="stage" id="stage-{i}"'
                       + (" checked" if i == 0 else "") + ">" for i in range(3))
    steps = "\n".join(
        f'<label class="step step-{i}" for="stage-{i}"><span class="step-n">{i + 1}</span> '
        f'{esc(fill(s, **counts))}</label>' for i, s in enumerate(d["stages"]))
    lines = "".join(
        f'<span class="{at(i)} said-{kind}">{esc(fill(s, **counts))}</span>'
        for i, (s, kind) in enumerate(zip(d["said"], ("plain", "fail", "pass"))))

    tiles = []
    for i, a in enumerate(d["assets"]):
        if a.get("by_hand"):
            badges = (f'<span class="badge {at(0)}">{esc(b["live"])}</span>'
                      f'<span class="badge badge-fail {at(1)}">{esc(b["caught"])}</span>'
                      f'<span class="badge badge-pass {at(2)}">{esc(b["fixed"])}</span>')
            says = (f'<span class="{at(0, 1)}">{esc(fill(a["says"], seats=d["before"]))}</span>'
                    f'<span class="{at(2)}">{esc(fill(a["says"], seats=d["after"]))}</span>')
            kind = "tile-hand"
        else:
            badges = (f'<span class="badge {at(0)}">{esc(b["live"])}</span>'
                      f'<span class="badge badge-pass {at(1, 2)}">{esc(b["rebuilt"])}</span>')
            says = (f'<span class="{at(0)}">{esc(fill(a["says"], seats=d["before"]))}</span>'
                    f'<span class="{at(1, 2)}">{esc(fill(a["says"], seats=d["after"]))}</span>')
            kind = "tile-gen"
        tiles.append(f'<li class="tile {kind}" style="--i: {i}"><p class="tile-top">'
                     f'<span class="tile-name">{esc(a["name"])}</span>{badges}</p>'
                     f'<p class="tile-says">{says}</p><p class="tile-made">{esc(a["made"])}</p></li>')

    return f"""<div class="demo" role="group" aria-labelledby="demo-label">
{inputs}
<div class="demo-head">
<p class="demo-label" id="demo-label">{esc(d["label"])}</p>
<p class="demo-source"><span class="demo-source-name">{esc(d["source"])}</span> <code>{esc(d["fact"])} = <b class="{at(0)}">{num(d["before"])}</b><b class="{at(1, 2)}">{num(d["after"])}</b></code></p>
</div>
<div class="stepper">
{steps}
</div>
<p class="demo-said">{lines}</p>
<ul class="tiles">
{chr(10).join(tiles)}
</ul>
<p class="demo-note">{esc(d["note"])} {said(command(c) for c in d["checks"])}.</p>
</div>"""


def asks(w, d):
    """Wherefore art thou, …? - one tab per asset, and its answer."""
    values = dict(fact=d["fact"], before=d["before"], after=d["after"])
    out = []
    for i, a in enumerate(w["asks"]):
        name = fill(a["name"], **values)
        title = esc(fill(w["ask"], name="\x00")).replace("\x00", f"<em>{esc(name)}</em>")
        out.append(
            f'<input class="state" type="radio" name="ask" id="ask-{i}"' + (" checked" if i == 0 else "") + ">\n"
            f'<label class="tab" for="ask-{i}">{esc(a["tab"])}</label>\n'
            f'<div class="ask-panel"><h2>{title}</h2><dl class="answer">'
            f'<div class="answer-from"><dt>{esc(w["built_from"])}</dt><dd><code>{esc(fill(a["from"], **values))}</code></dd></div>'
            f'<div class="answer-because"><dt>{esc(w["because"])}</dt><dd>{esc(a["because"])}</dd></div>'
            f'</dl></div>')
    return "\n".join(out)


def roadmap(s):
    labels = s["labels"]
    items = []
    for it in s["items"]:
        if it["state"] not in labels:
            raise SystemExit(f"status item {it['text']!r} is {it['state']!r}, which status.labels does not name")
        items.append(f'<li class="road-{esc(it["state"])}"><span class="chip">{esc(labels[it["state"]])}</span> '
                     f'{esc(fill(it["text"], version=VERSION))}</li>')
    return "\n".join(items)


def page(f):
    company, site, hero, w, how, rule, pilot = (
        f[k] for k in ("company", "site", "hero", "why", "how", "rule", "pilot"))
    lines = [head(site["title"], hero["lede"], "brand.css"),
             '<link rel="stylesheet" href="page.css">']
    if company["domain"]:
        lines.append(f'<link rel="canonical" href="https://{esc(company["domain"])}/">')

    steps = []
    for i, s in enumerate(how["steps"], 1):
        label = f'<code>{esc(command(s["command"]))}</code>' if "command" in s else esc(s["label"])
        steps.append(f'<li><p class="step-label">{i:02d} · {label}</p>'
                     f'<h3>{esc(s["name"])}</h3><p>{esc(s["text"])}</p></li>')

    if company["contact"]:
        join = (f'<p class="actions"><a class="button" href="mailto:{esc(company["contact"])}">'
                f'{esc(hero["cta"])}</a></p>')
    else:
        join = f'<p class="pilot-closed">{esc(pilot["closed"])}</p>'
    if pilot["terms"]:
        join += f'<p class="pilot-terms">{esc(pilot["terms"])}</p>'

    footer = f'Wherefore {esc(VERSION)} · <a href="brand/">Brand</a>'
    if company["domain"]:
        footer += f' · {esc(company["domain"])}'

    return f"""<!doctype html>
<html lang="en">
<head>
{chr(10).join(lines)}
</head>
<body>
{banner()}<header class="top"><div class="wrap"><a class="name" href="#top">{esc(company["name"])}</a>
<nav aria-label="On this page"><a href="#why">{esc(w["heading"])}</a><a href="#how">{esc(f["nav"]["how"])}</a><a class="pill" href="#pilot">{esc(f["nav"]["pilot"])}</a></nav></div></header>
<main id="top">
<section class="hero"><div class="wrap">
<p class="eyebrow">{esc(hero["eyebrow"])} · Wherefore {esc(VERSION)}</p>
<h1>{esc(hero["headline"])} <em>{esc(hero["headline_end"])}</em></h1>
<p class="lede">{esc(hero["lede"])}</p>
{demo(f["demo"])}
<p class="actions"><a class="button" href="#pilot">{esc(hero["cta"])}</a><a class="button button-quiet" href="#how">{esc(f["nav"]["how"])}</a></p>
</div></section>
<section id="why" class="meaning"><div class="wrap meaning-grid">
<div class="definition">
<p class="eyebrow">{esc(w["heading"])}</p>
<p class="word"><dfn>{esc(w["word"])}</dfn> <span class="part">{esc(w["part"])}</span></p>
<p class="sense">{esc(w["meaning"])}</p>
<p class="juliet">{esc(w["juliet"])}</p>
<p class="answers">{esc(w["rule"])}</p>
</div>
<div class="asks" role="group" aria-label="{esc(w["pick"])}">
{asks(w, f["demo"])}
<p class="ask-note">{esc(w["note"])} <a href="brand/">{esc(w["own"])}</a></p>
</div>
</div></section>
<section id="how"><div class="wrap">
<h2>{esc(how["heading"])}</h2>
<ol class="steps">
{chr(10).join(steps)}
</ol>
<p class="how-note">{esc(how["note"])}</p>
</div></section>
<section class="rule"><div class="wrap rule-grid">
<p class="rule-line">{esc(rule["line"])}<br><em>{esc(rule["end"])}</em></p>
<p class="rule-client">{esc(rule["client"])}</p>
</div></section>
<section id="pilot"><div class="wrap"><div class="pilot">
<p class="pilot-ask">{esc(pilot["ask"])}</p>
<h2>{esc(pilot["heading"])}</h2>
<p class="pilot-text">{esc(pilot["text"])}</p>
{join}
<ul class="road">
{roadmap(f["status"])}
</ul>
</div></div></section>
</main>
<footer><div class="wrap footer-row"><p><span class="footer-name">{esc(company["name"])}</span> · {esc(f["colophon"])}</p><p class="footer-meta">{footer}</p></div></footer>
</body>
</html>
"""


def headers(f):
    """What Cloudflare sends with every file: nothing loads from elsewhere, no
    script runs, and a draft is not indexed."""
    lines = [
        "/*",
        "  Content-Security-Policy: default-src 'none'; style-src 'self' 'unsafe-inline'; font-src 'self'; "
        "img-src 'self' data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
        "  X-Content-Type-Options: nosniff",
        "  Referrer-Policy: no-referrer",
    ]
    if status() == "draft":
        lines.append("  X-Robots-Tag: noindex, nofollow")
    return "\n".join(lines) + "\n"


def main():
    SITE.mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "gen/page.css", SITE / "page.css")
    (SITE / "index.html").write_text(page(FACTS), encoding="utf-8")
    (SITE / "_headers").write_text(headers(FACTS), encoding="utf-8")


if __name__ == "__main__":
    main()
