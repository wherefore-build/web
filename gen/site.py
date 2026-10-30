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

HOW THIS PAGE IS BUILT, ON THE PAGE. Each part of the page is rendered through
a view of the facts that writes down every fact it reads (Reading), and every
command and version it asks the engine for. What was read becomes that part's
`from` line, and the checks that hold it its `held by` line - so the page's
account of itself is the record of what built it, not a second description
that could drift from it. A switch shows them; they are in the page either way.

NO SCRIPT. The switch, the demo's three steps and the questions beside it are
checkboxes, radio buttons and their labels, and gen/page.css shows what is
checked. So they work under a policy that runs no script at all
(site/_headers), and checks/controls_press.py presses every one of them, cold,
at a phone's width.

STATUS. site.status is "draft" or "launched", and nothing else: an unknown
status stops the build. A draft says so in a banner across the page and asks
not to be indexed, both in the page and in the headers Cloudflare serves with
it (site/_headers). Launching is the owner's decision, and it is one word in
the facts.

THE CASE STUDY'S COUNTS ARE THE PENDULUM'S. facts/pendulum.json is a copy of
the counts chaotic-pendulums-co makes of itself - its proofs, its parts, its
print plates and the release they were counted at - captured by
.github/workflows/case-study.yml, which opens a pull request when they move.
Each stat names its count by `of`, and a count the copy does not have stops the
build. That part's account of itself names the copy on a `from` line of its own.

A NULL IS A FACT NOT DECIDED YET. With no domain the page names no canonical
address, with no contact it offers no address to write to, with no install
line it says Wherefore is not public yet, and with no quote the case study
quotes no one. Each appears when its fact does.

Run from gen/, as wherefore.json says, after brand.py. Writes site/index.html,
site/page.css and site/_headers.
"""
import json
import re
import shutil
import string
from importlib.resources import files

import wherefore
from kit import FACTS, PENDULUM, ROOT, SITE, banner, esc, head, status

ENGINE = f"wherefore {wherefore.__version__}"
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December")
ASKED = []          # what the part being rendered asked the engine for


def engine(name):
    """One of the engine's own data files, from the release this runs under."""
    data = files("wherefore") / name
    if not data.is_file():
        raise SystemExit(f"the pinned engine, {ENGINE}, has no {name}: "
                         f"the site needs 0.1.1 or later - move requirements-engine.txt")
    return json.loads(data.read_text(encoding="utf-8"))


COMMANDS = engine("commands.json")["commands"]


def version():
    ASKED.append("version")
    return wherefore.__version__


def entry(usage):
    """The pinned release's own entry for a command the page names; refused if it has none."""
    for c in COMMANDS:
        if c["usage"] == usage or c["usage"].startswith(usage + " "):
            ASKED.append(("command", usage))
            return c
    raise SystemExit(f"the page names `{usage}`, which {ENGINE} does not have: "
                     f"its commands are {', '.join(c['usage'] for c in COMMANDS)}")


def command(usage):
    """A command the page names, refused unless the pinned release has it."""
    entry(usage)
    return usage


class Reading:
    """The facts, or a part of them, writing down the path of every value read through it."""

    def __init__(self, value, path, log):
        self._value, self._path, self._log = value, path, log

    def __getitem__(self, key):
        v = self._value[key]
        path = f"{self._path}.{key}" if self._path else str(key)
        if isinstance(v, (dict, list)):
            return Reading(v, path, self._log)
        self._log.append(path)
        return v

    def get(self, key, default=None):
        return self[key] if key in self._value else default

    def __contains__(self, key):
        return key in self._value

    def __len__(self):
        return len(self._value)

    def __iter__(self):
        if isinstance(self._value, list):
            return (self[i] for i in range(len(self._value)))
        return iter(self._value)

    def __bool__(self):
        return bool(self._value)


def tree(paths):
    """`a.b`, `a.c`, `d` -> `a.{b, c} · d`; a list's items are `[]`."""
    root = {}
    for p in paths:
        node = root
        for part in re.sub(r"\.\d+(?=\.|$)", "[]", p).replace("[]", ".[]").split("."):
            node = node.setdefault(part, {})

    def say(name, node):
        if not node:
            return name
        if list(node) == ["[]"]:
            return say(name + "[]", node["[]"])
        kids = [say(k, v) for k, v in node.items()]
        return f"{name}.{kids[0]}" if len(kids) == 1 else f"{name}.{{{', '.join(kids)}}}"
    return [say(k, v) for k, v in root.items()]


def fill(text, **values):
    """A line from the facts, with each `{name}` in it filled; an unknown name stops the build."""
    names = [n for _, n, _, _ in string.Formatter().parse(text) if n is not None]
    unknown = [n for n in names if n not in values]
    if unknown:
        raise SystemExit(f"{text!r} names {{{unknown[0]}}}, which is not one of "
                         f"{', '.join('{' + k + '}' for k in values)}")
    return text.format(**{k: f"{v:g}" if isinstance(v, float) else v for k, v in values.items()})


def said(words):
    """`a`, `a and b`, `a, b and c` - each in code."""
    codes = [f"<code>{esc(w)}</code>" for w in words]
    return codes[0] if len(codes) == 1 else ", ".join(codes[:-1]) + " and " + codes[-1]


def literal(v):
    """A value as its source file writes it: a string in quotes, a number bare."""
    return esc(json.dumps(v, ensure_ascii=False))


def at(*stages):
    """The classes that show an element only at these steps of the demo."""
    return "at " + " ".join(f"at{s}" for s in stages)


SRC = "\x01src\x01"


def part(render, f, inspect, also=()):
    """A part of the page, rendered through a Reading, with its account of itself where it put SRC.

    `also` is any source the part reads beside the facts, as (file, value)
    pairs. Each is read through a Reading of its own and named on its own
    `from` line, and a part that reads the pendulum's copy is held by `feed`."""
    log, logs = [], [[] for _ in also]
    del ASKED[:]
    html = render(Reading(f, "", log), *(Reading(v, "", l) for (_, v), l in zip(also, logs)))
    facts = list(dict.fromkeys(log))
    commands = list(dict.fromkeys(a[1] for a in ASKED if isinstance(a, tuple)))
    held = (["gate", "reach", "brand"] + (["press"] if "<label" in html else []) + (["engine"] if commands else [])
            + (["feed"] if also else []))
    lines = [f'<p><span class="src-k">{esc(inspect["from"])}</span> facts/company.json · '
             f'{esc(fill(inspect["facts"], n=len(facts)))}: {esc(" · ".join(tree(facts)))}</p>']
    for (file, _), read in zip(also, logs):
        read = list(dict.fromkeys(read))
        lines.append(f'<p><span class="src-k">{esc(inspect["from"])}</span> {esc(file)} · '
                     f'{esc(fill(inspect["facts"], n=len(read)))}: {esc(" · ".join(tree(read)))}</p>')
    if ASKED:
        asked = (["version"] if "version" in ASKED else []) + ([f"commands.json: {', '.join(commands)}"] if commands else [])
        lines.append(f'<p><span class="src-k">{esc(inspect["from"])}</span> {esc(ENGINE)} · '
                     f'{esc(" · ".join(asked))}</p>')
    lines.append(f'<p><span class="src-k">{esc(inspect["held"])}</span> {esc(" · ".join(held))}</p>')
    return html.replace(SRC, f'<div class="src">{"".join(lines)}</div>')


def header(f):
    w = f["why"]
    return (f'{banner(f)}<header class="top"><div class="wrap"><a class="name" href="#top">{esc(f["company"]["name"])}</a>\n'
            f'<nav aria-label="On this page"><a href="#why">{esc(w["heading"])}</a><a href="#how">{esc(f["nav"]["how"])}</a>'
            f'<a href="#case">{esc(f["case"]["eyebrow"])}</a><a class="pill" href="#start">{esc(f["nav"]["start"])}</a></nav></div>'
            f'<div class="wrap">{SRC}</div></header>')


def key(f):
    """What the checks named under each part do, shown with them."""
    i = f["inspect"]
    rows = "".join(f'<div><dt>{esc(k)}</dt><dd>{esc(i["checks"][k])}</dd></div>' for k in i["checks"])
    return (f'<div class="src-key"><div class="wrap"><p>{esc(i["intro"])}</p>'
            f'<dl>{rows}</dl></div></div>')


def demo(d):
    """The ripple: one fact, every asset that states it, and the three steps of changing it."""
    hand = [a for a in d["assets"] if a.get("by_hand")]
    if len(hand) != 1:
        raise SystemExit(f"demo.assets has {len(hand)} written by hand: the demo's third step fixes exactly one")
    counts = dict(before=d["before"], after=d["after"], total=len(d["assets"]),
                  rebuilt=len(d["assets"]) - 1, hand=hand[0]["name"].lower())
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
            says = (f'<span class="{at(0, 1)}">{esc(fill(a["says"], value=d["before"]))}</span>'
                    f'<span class="{at(2)}">{esc(fill(a["says"], value=d["after"]))}</span>')
            kind = "tile-hand"
        else:
            badges = (f'<span class="badge {at(0)}">{esc(b["live"])}</span>'
                      f'<span class="badge badge-pass {at(1, 2)}">{esc(b["rebuilt"])}</span>')
            says = (f'<span class="{at(0)}">{esc(fill(a["says"], value=d["before"]))}</span>'
                    f'<span class="{at(1, 2)}">{esc(fill(a["says"], value=d["after"]))}</span>')
            kind = "tile-gen"
        tiles.append(f'<li class="tile {kind}" style="--i: {i}"><p class="tile-top">'
                     f'<span class="tile-name">{esc(a["name"])}</span>{badges}</p>'
                     f'<p class="tile-says">{says}</p><p class="tile-made">{esc(a["made"])}</p></li>')

    return f"""<div class="demo" role="group" aria-labelledby="demo-label">
{inputs}
<div class="demo-head">
<p class="demo-label" id="demo-label">{esc(d["label"])}</p>
<p class="demo-source"><span class="demo-source-name">{esc(d["source"])}</span> <code>{esc(d["fact"])} = <b class="{at(0)}">{literal(counts["before"])}</b><b class="{at(1, 2)}">{literal(counts["after"])}</b></code></p>
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


W, H = 360, 220    # every panel's drawing, in the units its viewBox gives it


def svg(title, body):
    return (f'<svg class="fork-art" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}">'
            f'{body}</svg>')


def text(x, y, words, cls="art-label", anchor="start"):
    return f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{esc(words)}</text>'


def code_art(c):
    """Your code: one main line; each branch leaves it, passes its tests, and merges back -
    and the branches overlap, as work does."""
    main_y = 162
    out = [f'<path class="art-main" d="M 12 {main_y} H {W - 12}"/>']
    for i, (x, run, up) in enumerate(((22, 112, 84), (104, 120, 116), (214, 120, 80))):
        d = (f"M {x} {main_y} C {x + 22} {main_y} {x + 14} {up} {x + 36} {up} H {x + run - 36} "
             f"C {x + run - 14} {up} {x + run - 22} {main_y} {x + run} {main_y}")
        out.append(f'<path class="art-branch" d="{d}"/>')
        out.append(f'<path class="art-pulse" pathLength="1" style="--d: {i * 0.9}s" d="{d}"/>')
        out.append(f'<circle class="art-ok" cx="{x + run // 2}" cy="{up}" r="5"/>')
        out.append(f'<circle class="art-ok" cx="{x + run}" cy="{main_y}" r="4"/>')
        if i == 0:
            out.append(text(x=x + run // 2, y=up - 12, words=c["tests"], anchor="middle"))
    out.append(text(x=12, y=main_y + 26, words=c["main"]))
    out.append(text(x=W - 12, y=main_y + 26, words=c["ships"], anchor="end"))
    return svg(c["title"], "".join(out))


def drift_art(d):
    """Everything else: one decision copied into every asset, each copy forking again, none coming back."""
    x0, y0 = 22, 110
    rows = (30, 70, 110, 150, 190)
    out, ends = [], []
    for i, y in enumerate(rows):
        a = 108 + (i * 23) % 44          # where this copy forks
        b = 196 + (i * 37) % 52          # and where one of its forks forks again
        out.append(f'<path class="art-drift grow" pathLength="1" style="--d: {i * 0.25}s" '
                   f'd="M {x0} {y0} C {x0 + 30} {y0} {x0 + 26} {y} {x0 + 56} {y} H {a}"/>')
        for k, dy in enumerate((-11, 11)):
            y1 = y + dy
            out.append(f'<path class="art-drift fade-1 grow" pathLength="1" style="--d: {1.2 + i * 0.25 + k * 0.1}s" '
                       f'd="M {a} {y} C {a + 14} {y} {a + 10} {y1} {a + 24} {y1} H {b if k == i % 2 else W - 14}"/>')
            if k == i % 2:
                for j, dz in enumerate((-6, 6)):
                    y2 = y1 + dz
                    out.append(f'<path class="art-drift fade-2 grow" pathLength="1" '
                               f'style="--d: {2.4 + i * 0.25 + j * 0.1}s" '
                               f'd="M {b} {y1} C {b + 10} {y1} {b + 8} {y2} {b + 18} {y2} H {W - 14}"/>')
                    ends.append(y2)
            else:
                ends.append(y1)
    for n, y in enumerate(ends):
        out.append(f'<circle class="{"art-stale" if n % 3 == 1 else "art-end"}" cx="{W - 14}" cy="{y}" r="2.5"/>')
    out.append(f'<circle class="art-node" cx="{x0}" cy="{y0}" r="5"/>')
    out.append(text(x=x0 - 10, y=y0 + 26, words=d["start"]))
    for copy, y in zip(d["copies"], (rows[0] - 14, rows[1] + 26, rows[3] - 14, rows[4] + 24)):
        out.append(text(x=W - 22, y=y, words=copy, cls="art-copy", anchor="end"))
    return svg(d["title"], "".join(out))


def compiled_art(c, assets):
    """With Wherefore: one source, built into every asset, every asset through the gate, then out."""
    x0, y0, gate = 22, 110, 300
    n = len(assets)
    gap = 168 / max(n - 1, 1)
    out = []
    for i, a in enumerate(assets):
        y = round(26 + i * gap)
        d = (f"M {x0} {y0} C {x0 + 30} {y0} {x0 + 26} {y} {x0 + 58} {y} H 258 "
             f"C 284 {y} 278 {y0} {gate} {y0}")
        out.append(f'<path class="art-line" d="{d}"/>')
        out.append(f'<path class="art-pulse art-ripple" pathLength="1" d="{d}"/>')
        out.append(text(x=x0 + 66, y=y - 4, words=a["name"], cls="art-asset"))
    out.append(f'<path class="art-out" d="M {gate} {y0} H {W - 12}"/>')
    out.append(f'<circle class="art-source" cx="{x0}" cy="{y0}" r="6"/>')
    out.append(f'<rect class="art-gate" x="{gate - 12}" y="{y0 - 12}" width="24" height="24" rx="6"/>')
    out.append(f'<path class="art-check" d="M {gate - 5} {y0} l 4 4 l 7 -8"/>')
    out.append(text(x=x0 - 8, y=y0 + 24, words=c["source"]))
    out.append(text(x=gate, y=y0 + 32, words=command("wherefore gate"), anchor="middle"))
    out.append(text(x=W - 12, y=y0 - 10, words=c["ships"], anchor="end"))
    out.append(text(x=x0 + 66, y=H - 4, words=command("wherefore build"), cls="art-label"))
    return svg(c["title"], "".join(out))


def forks(f):
    """The picture: code merges back; everything else forks for good; Wherefore gives it code's shape."""
    k = f["forks"]
    code, drift, done = k["code"], k["drift"], k["compiled"]
    return f"""<div class="forks">
<figure class="fork fork-code"><figcaption class="fork-title">{esc(code["title"])}</figcaption>{code_art(code)}<p class="fork-caption">{esc(code["caption"])}</p></figure>
<figure class="fork fork-drift"><figcaption class="fork-title">{esc(drift["title"])}</figcaption>{drift_art(drift)}<p class="fork-caption">{esc(drift["caption"])}</p><p class="fork-sting">{esc(drift["sting"])}</p></figure>
<figure class="fork fork-compiled"><figcaption class="fork-title">{esc(done["title"])}</figcaption>{compiled_art(done, f["demo"]["assets"])}<p class="fork-caption">{esc(done["caption"])}</p></figure>
</div>"""


def hero(f):
    h = f["hero"]
    return f"""<section class="hero"><div class="wrap">
{SRC}
<p class="eyebrow">{esc(h["eyebrow"])} · Wherefore {esc(version())}</p>
<h1>{esc(h["headline"])} <em>{esc(h["headline_end"])}</em></h1>
<p class="lede">{esc(h["lede"])}</p>
{forks(f)}
<p class="actions"><a class="button" href="#start">{esc(f["nav"]["start"])}</a><a class="button button-quiet" href="#how">{esc(f["nav"]["how"])}</a></p>
</div></section>"""


def pains(f):
    """What drift costs, in the words of the teams it costs, and what Wherefore does about it."""
    p = f["pains"]
    items = "".join(f'<li class="pain"><p class="pain-head">{esc(i["pain"])}</p><p class="pain-detail">{esc(i["detail"])}</p></li>'
                    for i in p["items"])
    return f"""<section class="pains"><div class="wrap">
{SRC}
<h2>{esc(p["heading"])}</h2>
<ul class="pain-list">{items}</ul>
<p class="pain-answer">{esc(p["answer"])}</p>
</div></section>"""


def ripple(f):
    return f"""<section id="demo" class="ripple"><div class="wrap">
{SRC}
<h2>{esc(f["demo"]["heading"])}</h2>
{demo(f["demo"])}
</div></section>"""


def why(f):
    w, d = f["why"], f["demo"]
    values = dict(fact=d["fact"], before=d["before"], after=d["after"])
    tabs = []
    for i, a in enumerate(w["asks"]):
        name = fill(a["name"], **values)
        title = esc(fill(w["ask"], name="\x00")).replace("\x00", f"<em>{esc(name)}</em>")
        tabs.append(
            f'<input class="state" type="radio" name="ask" id="ask-{i}"' + (" checked" if i == 0 else "") + ">\n"
            f'<label class="tab" for="ask-{i}">{esc(a["tab"])}</label>\n'
            f'<div class="ask-panel"><h2>{title}</h2><dl class="answer">'
            f'<div class="answer-from"><dt>{esc(w["built_from"])}</dt><dd><code>{esc(fill(a["from"], **values))}</code></dd></div>'
            f'<div class="answer-because"><dt>{esc(w["because"])}</dt><dd>{esc(a["because"])}</dd></div>'
            f'</dl></div>')
    return f"""<section id="why" class="meaning"><div class="wrap">
{SRC}
<div class="meaning-grid">
<div class="definition">
<p class="eyebrow">{esc(w["heading"])}</p>
<p class="word"><dfn>{esc(w["word"])}</dfn> <span class="part">{esc(w["part"])}</span></p>
<p class="sense">{esc(w["meaning"])}</p>
<p class="juliet">{esc(w["juliet"])}</p>
<p class="answers">{esc(w["rule"])}</p>
</div>
<div class="asks" role="group" aria-label="{esc(w["pick"])}">
{chr(10).join(tabs)}
<p class="ask-note">{esc(w["note"])} <label class="inline-switch" for="inspect">{esc(f["inspect"]["ask"])}</label></p>
</div>
</div>
</div></section>"""


def how(f):
    h = f["how"]
    steps = []
    for i, s in enumerate(h["steps"], 1):
        label = f'<code>{esc(command(s["command"]))}</code>' if "command" in s else esc(s["label"])
        steps.append(f'<li><p class="step-label">{i:02d} · {label}</p>'
                     f'<h3>{esc(s["name"])}</h3><p>{esc(s["text"])}</p></li>')
    return f"""<section id="how"><div class="wrap">
{SRC}
<h2>{esc(h["heading"])}</h2>
<ol class="steps">
{chr(10).join(steps)}
</ol>
<p class="how-note">{esc(h["note"])}</p>
</div></section>"""


def counted(counts, name):
    """One of the pendulum's counts, by the name a stat gives it; one it does not count stops the build."""
    if name not in counts or not isinstance(counts.get(name), int):
        have = ", ".join(k for k in counts if not isinstance(counts.get(k), Reading))
        raise SystemExit(f"case.stats names {name!r}, which facts/pendulum.json does not count. It counts: {have}")
    return counts[name]


def long_date(iso):
    """2026-10-30 -> 30 October 2026, by table: a locale must not decide the page's bytes."""
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} {MONTHS[m - 1]} {y}"


def case(f, p):
    c = f["case"]
    made = "".join(f"<li>{esc(m)}</li>" for m in c["made"])
    held = "".join(f"<li>{esc(m)}</li>" for m in c["held"])
    counts = p["counts"]
    stats = "".join(f'<li><span class="stat-n">{counted(counts, s["of"])}</span> {esc(s["what"])}</li>'
                    for s in c["stats"])
    as_of = fill(c["as_of"], version=counts["pack"]["version"], on=long_date(p["captured"]["on"]))
    quote = ""
    if c["quote"]:
        quote = (f'<blockquote class="case-quote"><p>{esc(c["quote"]["text"])}</p>'
                 f'<footer>{esc(c["quote"]["by"])}</footer></blockquote>')
    return f"""<section id="case" class="case"><div class="wrap">
{SRC}
<p class="eyebrow">{esc(c["eyebrow"])} · {esc(c["name"])}</p>
<h2>{esc(c["heading"])}</h2>
<p class="case-text">{esc(c["text"])}</p>
<p class="actions"><a class="button button-quiet" href="{esc(c["url"])}">{esc(c["visit"])}</a></p>
{quote}
<div class="case-grid">
<div class="case-col"><h3>{esc(c["made_heading"])}</h3><ul class="case-list">{made}</ul></div>
<div class="case-col"><h3>{esc(c["held_heading"])}</h3><ul class="case-list case-held">{held}</ul></div>
</div>
<ul class="stats">{stats}</ul>
<p class="as-of">{esc(as_of)}</p>
</div></section>"""


def rule(f):
    r = f["rule"]
    return f"""<section class="rule"><div class="wrap">
{SRC}
<div class="rule-grid">
<p class="rule-line">{esc(r["line"])}<br><em>{esc(r["end"])}</em></p>
<p class="rule-text">{esc(r["text"])}</p>
</div>
</div></section>"""


def start(f):
    """Getting started, by yourself: the install line once there is one, then the release's own commands."""
    st, s = f["start"], f["status"]
    lines = []
    if st["install"]:
        lines.append(f'<li><code>{esc(st["install"])}</code></li>')
    for usage in st["steps"]:
        c = entry(usage)
        lines.append(f'<li><code>{esc(c["usage"])}</code><span class="does">{esc(c["does"])}</span></li>')
    closed = "" if st["install"] else f'<p class="start-closed">{esc(st["closed"])}</p>'
    labels, road = s["labels"], []
    for it in s["items"]:
        state = it["state"]
        if state not in labels:
            raise SystemExit(f"status item {it['text']!r} is {state!r}, which status.labels does not name")
        road.append(f'<li class="road-{esc(state)}"><span class="chip">{esc(labels[state])}</span> '
                    f'{esc(fill(it["text"], version=version()))}</li>')
    return f"""<section id="start"><div class="wrap">
{SRC}
<div class="start-box">
<p class="start-ask">{esc(st["ask"])}</p>
<h2>{esc(st["heading"])}</h2>
<p class="start-text">{esc(st["text"])}</p>
<ol class="start-steps">
{chr(10).join(lines)}
</ol>
{closed}
<ul class="road">
{chr(10).join(road)}
</ul>
</div>
</div></section>"""


def footer(f):
    company = f["company"]
    meta = f'Wherefore {esc(version())} · <a href="brand/">Brand</a>'
    if company["contact"]:
        meta += f' · <a href="mailto:{esc(company["contact"])}">{esc(company["contact"])}</a>'
    if company["domain"]:
        meta += f' · {esc(company["domain"])}'
    return (f'<footer><div class="wrap">{SRC}<div class="footer-row"><p><span class="footer-name">{esc(company["name"])}</span>'
            f' · {esc(f["colophon"])}</p><p class="footer-meta">{meta}</p></div></div></footer>')


def page(f):
    company, site, inspect = f["company"], f["site"], f["inspect"]
    lines = [head(site["title"], f["hero"]["lede"], "brand.css"),
             '<link rel="stylesheet" href="page.css">']
    if company["domain"]:
        lines.append(f'<link rel="canonical" href="https://{esc(company["domain"])}/">')
    parts = {name: part(render, f, inspect, *also) for name, render, *also in (
        ("header", header), ("hero", hero), ("pains", pains), ("demo", ripple), ("why", why), ("how", how),
        ("case", case, (("facts/pendulum.json", PENDULUM),)),
        ("rule", rule), ("start", start), ("footer", footer))}
    return f"""<!doctype html>
<html lang="en">
<head>
{chr(10).join(lines)}
</head>
<body>
<input class="state inspect-state" type="checkbox" id="inspect">
{parts["header"]}
<main id="top">
{key(f)}
{parts["hero"]}
{parts["pains"]}
{parts["demo"]}
{parts["why"]}
{parts["how"]}
{parts["case"]}
{parts["rule"]}
{parts["start"]}
</main>
{parts["footer"]}
<label class="inspect-switch" for="inspect"><span class="switch-track" aria-hidden="true"></span>{esc(inspect["toggle"])}</label>
</body>
</html>
"""


def headers():
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
    (SITE / "_headers").write_text(headers(), encoding="utf-8")


if __name__ == "__main__":
    main()
