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

THE ONE PAGE THAT RUNS A SCRIPT IS THE PENDULUM'S OWN. Beside the case study's
heading stands the pendulum's interactive model: cases/pendulum/model.html, a
byte-for-byte copy of the file the pendulum's home page embeds, taken
at the commit case.model.taken names. It is written to site/pendulum/ with a
few lines that frame it - the view, and a swing to start it moving - and shown
in a sandboxed frame: the frame may run its script and nothing else, cannot
reach this page, and is the only path the headers let run one. This page still
runs none. Like the counts, it is a dated snapshot; unlike them, it is
watched - its captured group names the pendulum's public home page as its
upstream, and `wherefore check upstream` fails the deploy when the pendulum's
model has moved, until it is copied again. checks/model_turns.py drags it, at
a phone's width, and requires it to turn.

THE CHANGELOG IS THE RELEASE'S OWN. site/changelog/ lists every release the
pinned engine has cut - its version, its date, its title and sentence, and a
picture of it working, which is what that release printed when it was run -
from the releases.json it ships. Nothing here types a release. Under each are
the features it brought, in this site's own words from `does`, so a feature
with no words stops the build on this page as on the first. A release newer
than the pin is not here until the pin moves to it; a feature whose release the
engine does not list, or a newest release that is not the one pinned, stops it.

THE CASE STUDY'S COUNTS ARE A DATED SNAPSHOT. facts/pendulum.json holds
the pendulum's proofs, parts, print plates and the release they were
counted at, counted once at the commit it names; nothing reads the pendulum's
repository. Its public /release.json is read, by `wherefore check upstream`:
when it names another release than the snapshot's, the build fails until the
counts are taken again.
Each stat names its count by `of`, and a count the copy does not have stops the
build. That part's account of itself names the copy on a `from` line of its own.

A NULL IS A FACT NOT DECIDED YET. With no domain the page names no canonical
address, with no contact it offers no address to write to, with no install
line it says Wherefore is not public yet, and with no quote the case study
quotes no one. Each appears when its fact does.

Run from gen/, as wherefore.json says, after brand.py. Writes site/index.html,
site/page.css, site/_headers, the features page, site/features/index.html, the
changelog, site/changelog/index.html, the framed model, site/pendulum/index.html, and
the framed plate, site/pendulum/plate/index.html.
The map, site/map/index.html, is the engine's: `wherefore graph` run as a
generator of its own (wherefore.json), which the gate runs like any command
and `wherefore graph` itself credits rather than runs.
"""
import json
import re
import shutil
import string
from importlib.resources import files

import wherefore
from kit import FACTS, PENDULUM, ROADMAP, ROOT, SITE, banner, colours, esc, head, status

ENGINE = f"wherefore {wherefore.__version__}"
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December")
ASKED = []          # what the part being rendered asked the engine for
MODEL = ROOT / "cases/pendulum/model.html"
MODEL_PAGE = "pendulum/"
# The site's own map, written by `wherefore graph` run as a generator (wherefore.json):
# every source, the scripts that read it, and every file they make, in the
# brand's own colours (--theme site/brand/map.css, which gen/brand.py writes
# from the tokens). The engine's page, with the engine's script in it, so its
# path is served a policy that lets its own script run and load the brand's
# fonts, like the model's.
MAP_PAGE = "map/"
# What frames the pendulum's model on this site, appended after its source -
# which has no closing tags, so it is appended to, never edited. A three-quarter
# view drawn back far enough, with the pivot high, that the whole swing stays in
# a small frame; the arms in the pose the home page shows; then, the moment the
# frame scrolls into view, a swing from it with a kick (owner, 5 November 2026:
# a big spin, so it looks interesting when a visitor reaches it). The kick is
# the two arms' starting speeds in radians a second (doubled at the owner's word, 5 November); at these the outer arm
# turns over several times in its first seconds. The frame is lazy, so it may
# load long before it is seen, and the observer holds the kick until it is;
# a browser without one kicks on load. A visitor who asks for less motion
# gets the pose alone.
KICK = (12, 28)
FRAMING = f"""
<style>html,body{{overflow:hidden}}</style>
<script>
addEventListener('load', function () {{
  var still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var posed = CP.go({{view: {{yaw: 30, pitch: -14, fov: 30, tx: 0, ty: -100, app: 580}}, pose: 'house', dur: 1}});
  if (still) return;
  var kicked = false;
  function kick() {{
    if (kicked) return;
    kicked = true;
    posed.then(function () {{ return CP.swing({{kick: [{KICK[0]}, {KICK[1]}]}}); }});
  }}
  if (!('IntersectionObserver' in window)) return kick();
  var seen = new IntersectionObserver(function (entries) {{
    if (entries.some(function (e) {{ return e.isIntersecting; }})) {{ seen.disconnect(); kick(); }}
  }}, {{threshold: 0.5}});
  seen.observe(document.body);
}});
</script>
"""


def engine(name, since="0.1.1"):
    """One of the engine's own data files, from the release this runs under."""
    data = files("wherefore") / name
    if not data.is_file():
        raise SystemExit(f"the pinned engine, {ENGINE}, has no {name}: "
                         f"the site needs {since} or later - move requirements-engine.txt")
    return json.loads(data.read_text(encoding="utf-8"))


COMMANDS = engine("commands.json")["commands"]
# What the engine does, as the release says it. Every one must be on the page.
FEATURES = engine("features.json", since="0.4.0")["features"]
from wherefore import docs as wherefore_docs   # noqa: E402 - the docs the pinned release ships


def version():
    ASKED.append("version")
    return wherefore.__version__


def release_meta():
    """The pinned release's distribution name and licence, from its installed metadata - never typed."""
    import importlib.metadata as md
    meta = md.metadata("wherefore-build")
    licence = meta.get("License-Expression") or meta.get("License")
    if not licence:
        raise SystemExit(f"{ENGINE} declares no licence in its metadata, and the page says which one it is under")
    ASKED.append("licence")
    return meta["Name"], licence


def scan_shown():
    """What `wherefore scan` printed, as the release that brought it recorded it: the hero's real output."""
    for r in engine("releases.json", since="0.5.0")["releases"]:
        if r["shows"]["run"].startswith("wherefore scan"):
            ASKED.append("releases")
            return r["shows"]
    raise SystemExit(f"{ENGINE} records no release whose picture is a run of `wherefore scan`, and the hero shows one")


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
    `from` line, and a part that reads the case study's snapshot is held by `snapshot`."""
    log, logs = [], [[] for _ in also]
    del ASKED[:]
    html = render(Reading(f, "", log), *(Reading(v, "", l) for (_, v), l in zip(also, logs)))
    facts = list(dict.fromkeys(log))
    commands = list(dict.fromkeys(a[1] for a in ASKED if isinstance(a, tuple)))
    held = (["gate", "reach", "brand"] + (["press"] if "<label" in html else []) + (["engine"] if commands else [])
            + (["snapshot"] if also else []))
    lines = [f'<p><span class="src-k">{esc(inspect["from"])}</span> facts/company.json · '
             f'{esc(fill(inspect["facts"], n=len(facts)))}: {esc(" · ".join(tree(facts)))}</p>']
    for (file, _), read in zip(also, logs):
        read = list(dict.fromkeys(read))
        lines.append(f'<p><span class="src-k">{esc(inspect["from"])}</span> {esc(file)} · '
                     f'{esc(fill(inspect["facts"], n=len(read)))}: {esc(" · ".join(tree(read)))}</p>')
    if ASKED:
        asked = ((["version"] if "version" in ASKED else []) + (["licence"] if "licence" in ASKED else [])
                 + (["releases.json"] if "releases" in ASKED else [])
                 + ([f"commands.json: {', '.join(commands)}"] if commands else []))
        lines.append(f'<p><span class="src-k">{esc(inspect["from"])}</span> {esc(ENGINE)} · '
                     f'{esc(" · ".join(asked))}</p>')
    lines.append(f'<p><span class="src-k">{esc(inspect["held"])}</span> {esc(" · ".join(held))}</p>')
    return html.replace(SRC, f'<div class="src">{"".join(lines)}</div>')


def links(f, home=""):
    """The site's links, in reading order: how it works, the case, why, then what it
    has and will have, what shipped, the docs, the map (owner, 6 November 2026:
    features and roadmap after why and before the changelog)."""
    n = f["nav"]
    return (f'<a href="{home}#how">{esc(n["how"])}</a><a href="{home}#case">{esc(f["case"]["eyebrow"])}</a>'
            f'<a href="{home}#why">{esc(n["why"])}</a><a href="{home}features/">{esc(n["does"])}</a>'
            f'<a href="{home}changelog/">{esc(f["changelog"]["title"])}</a>'
            f'<a href="{home}docs/">{esc(n["docs"])}</a><a href="{home}{MAP_PAGE}">{esc(n["map"])}</a>')


def nav(f, home=""):
    """The site's links. `home` is the way back to the home page from where the nav sits: "" on it."""
    return f'<nav aria-label="The site">{links(f, home)}</nav>'


def topbar(f, home=""):
    """The name, the links, Get started - and on a phone a Menu that opens the links
    (owner, 5 November 2026: they were in the footer only, and nobody found them).
    The menu is a checkbox and its label, no script, as every control here is."""
    n = f["nav"]
    return (f'<div class="wrap"><input class="state menu-state" type="checkbox" id="menu">'
            f'<a class="name" href="{home or "#top"}">{esc(f["company"]["name"])}</a>\n'
            f'<label class="menu-switch" for="menu">{esc(n["menu"])}</label>'
            f'{nav(f, home)}<a class="pill" href="{home}#start">{esc(n["start"])}</a></div>')


def foot_nav(f, home=""):
    """Every page's links again, at the foot, where a phone's header has no room for them."""
    return f'<nav class="foot-nav" aria-label="The site, again">{links(f, home)}</nav>'


def header(f):
    return f'{banner(f)}<header class="top">{topbar(f)}<div class="wrap">{SRC}</div></header>'


def key(f):
    """What the checks named under each part do, shown with them."""
    i = f["inspect"]
    rows = "".join(f'<div><dt>{esc(k)}</dt><dd>{esc(i["checks"][k])}</dd></div>' for k in i["checks"])
    source = f["company"]["source"]
    # The source opens in a new tab, so a visitor reading how the page is built keeps the page (owner).
    link = f' <a target="_blank" rel="noopener" href="{esc(source)}">{esc(i["source"])}{OUT}</a>' if source else ""
    # The map: the whole chain, drawn by the pinned engine from a real run of
    # every generator (MAP_PAGE, a generator in wherefore.json).
    link += f' <a href="{MAP_PAGE}">{esc(i["map"])}</a>'
    return (f'<div class="src-key"><div class="wrap"><p>{esc(i["intro"])}{link}</p>'
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


# The mark for a link that leaves the site: an arrow out of a box, drawn in the
# text's own colour, and silent to a screen reader - the words say where it goes.
OUT = ('<svg class="out" viewBox="0 0 16 16" aria-hidden="true" focusable="false">'
       '<path d="M9 2h5v5M14 2 7.5 8.5M12 9.5V13a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h3.5" '
       'fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')

def hero(f):
    """What it is, why it matters, and the commands that try it on your own site - and on your site and your app together - with real output beside them.

    The headline runs the whole width; under it the lede and the two commands
    take one column and the scan's output the other, once there is room for
    its longest line (gen/page.css, .hero-grid).

    The eyebrow's licence and version, the package pip installs and the scan's
    output are the pinned release's own; the commands are start's, so the hero
    and Get started state them once between them. The second button is the
    engine's public repository, once there is one: company.github."""
    h, st = f["hero"], f["start"]
    name, licence = release_meta()
    first = st["steps"][0]
    run = f'{command(first["command"])} {first.get("args", "")}'.strip()
    # The same scan, pointed at two places at once (owner, 5 November 2026):
    # the output beside it reads a site and an app together, so the command
    # that does that stands under the one-site command, ready to copy.
    also = (f'<code class="cmd"><span class="term-prompt">$</span> {esc(command(first["command"]))} {esc(first["also"])}</code>'
            if first.get("also") else "")
    repo = f["company"]["github"]
    github = (f'<p class="actions"><a class="button button-quiet" href="{esc(repo)}">{esc(f["nav"]["github"])}{OUT}</a></p>'
              if repo else "")
    return f"""<section class="hero"><div class="wrap">
{SRC}
<p class="eyebrow">{esc(h["eyebrow"])} · {esc(licence)} · {esc(version())}</p>
<h1>{esc(h["headline"])} <em>{esc(h["headline_end"])}</em></h1>
<div class="hero-grid">
<div class="hero-copy">
<p class="lede">{esc(h["lede"])}</p>
<p class="try-label">{esc(h["try"])}</p>
<div class="try"><code class="cmd"><span class="term-prompt">$</span> {esc(st["install"])}</code><code class="cmd"><span class="term-prompt">$</span> {esc(run)}</code>{also}</div>
<p class="try-pip">{esc(h["pip"])} <code>pip install {esc(name)}</code></p>
{github}
</div>
<figure class="term hero-term"><pre><code>{terminal(scan_shown(), f["changelog"]["cut"])}</code></pre>
<figcaption>{esc(h["shows"])}</figcaption></figure>
</div>
</div></section>"""


def opening(f):
    """The picture, right after the headline (owner, 5 November 2026): code merges back,
    everything else forks for good, and Wherefore gives everything else code's shape."""
    return f"""<section id="forks" class="opening"><div class="wrap">
{SRC}
<h2>{esc(f["forks"]["heading"])}</h2>
{forks(f)}
</div></section>"""


def ripple(f):
    return f"""<section id="demo" class="ripple"><div class="wrap">
{SRC}
<h2>{esc(f["demo"]["heading"])}</h2>
{demo(f["demo"])}
</div></section>"""


FLIP = 7          # seconds each question stands before the next, while they turn by themselves (owner, 5 November: slower)


def flipping(n):
    """The CSS that turns the questions by themselves, for `n` of them.

    Still no script. A radio with no chip of its own, `ask-auto`, is the one
    checked when the page loads, and while it is, each question stands for FLIP
    seconds - a bar crossing its chip, turning the accent as it goes - then
    flips to the next. `n` is the number of questions: the prompt panel that
    asks a visitor to pick is not in the cycle, or the cycle would show a
    blank turn once round (the owner saw it, 5 November). Hovering holds it. Tapping any chip, the first included,
    checks that chip's radio instead, and the turning stops on its question. A
    visitor who asks for less motion is asked to pick one instead. The
    percentages depend on how many questions there are, so they are written
    here, from the facts, rather than in gen/page.css."""
    slot = 100 / n
    end = f"{slot - 0.01:.2f}"
    shown = "\n".join(f"#ask-{i}:checked ~ .ask-panels .ask-panel-{i} {{ visibility: visible; }}" for i in range(n))
    run = f"{n * FLIP}s calc(var(--i) * {FLIP}s) infinite"
    return f"""<style>
{shown}
#ask-auto:checked ~ .ask-panels .ask-pick {{ visibility: visible; }}
@media (prefers-reduced-motion: no-preference) {{
  #ask-auto:checked ~ .ask-panels .ask-pick {{ visibility: hidden; }}
  #ask-auto:checked ~ .ask-panels .ask-panel:not(.ask-pick) {{ animation: ask-flip {run}; }}
  #ask-auto:checked ~ .tab {{ animation: ask-chip {run}; }}
  #ask-auto:checked ~ .tab::after {{ animation: ask-bar {run}; }}
  .asks:hover .ask-panel, .asks:hover .tab, .asks:hover .tab::after {{ animation-play-state: paused; }}
}}
@keyframes ask-flip {{
  0% {{ visibility: visible; opacity: 0; transform: perspective(40rem) rotateX(-70deg); }}
  {slot * 0.12:.2f}% {{ visibility: visible; opacity: 1; transform: none; }}
  {end}% {{ visibility: visible; opacity: 1; transform: none; }}
  {slot:.2f}%, 100% {{ visibility: hidden; opacity: 0; }}
}}
@keyframes ask-chip {{
  0%, {end}% {{ border-color: var(--accent); }}
  {slot:.2f}%, 100% {{ border-color: var(--line); }}
}}
@keyframes ask-bar {{
  0% {{ transform: scaleX(0); background: var(--muted); }}
  {end}% {{ transform: scaleX(1); background: var(--accent); }}
  {slot:.2f}%, 100% {{ transform: scaleX(0); background: var(--muted); }}
}}
</style>"""


def why(f):
    w, d = f["why"], f["demo"]
    values = dict(fact=d["fact"], before=d["before"], after=d["after"])
    tabs = [f'<input class="state" type="radio" name="ask" id="ask-auto" checked aria-label="{esc(w["pick"])}">']
    panels = [f'<div class="ask-panel ask-pick"><p class="ask-prompt">{esc(w["pick"])}</p></div>']
    for i, a in enumerate(w["asks"]):
        name = fill(a["name"], **values)
        title = esc(fill(w["ask"], name="\x00")).replace("\x00", f"<em>{esc(name)}</em>")
        tabs.append(
            f'<input class="state" type="radio" name="ask" id="ask-{i}">\n'
            f'<label class="tab" for="ask-{i}" style="--i: {i}">{esc(a["tab"])}</label>')
        panels.append(
            f'<div class="ask-panel ask-panel-{i}" style="--i: {i}"><h2>{title}</h2><dl class="answer">'
            f'<div class="answer-from"><dt>{esc(w["built_from"])}</dt><dd><code>{esc(fill(a["from"], **values))}</code></dd></div>'
            f'<div class="answer-because"><dt>{esc(w["because"])}</dt><dd>{esc(a["because"])}</dd></div>'
            f'</dl></div>')
    tabs.append(f'<div class="ask-panels">\n{chr(10).join(panels)}\n</div>\n{flipping(len(w["asks"]))}')
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
<p class="ask-note">{esc(w["note"])}</p>
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
{catches(f)}
</div></section>"""


def catches(f):
    """What else it catches, in one line each: three of the release's features, and the way to every one.
    Under how it works, not a section of its own (owner, 5 November 2026)."""
    d = f["does"]
    byid = {x["id"]: x for x in FEATURES}
    items = []
    for k in d["home"]:
        if k not in byid:
            raise SystemExit(f"does.home names `{k}`, which {ENGINE} does not ship")
        items.append(f'<li><p class="does-name">{esc(byid[k]["name"])}</p><p>{esc(d["short"][k])}</p></li>')
    return (f'<h3 class="catches">{esc(d["home_heading"])}</h3>\n<ul class="does does-three">\n{chr(10).join(items)}\n</ul>\n'
            f'<p class="more-all"><a href="features/">{esc(fill(d["all"], n=len(FEATURES)))}</a></p>')


def releases():
    """Every release the pinned engine has cut, newest first, each with the features it brought."""
    rows = engine("releases.json", since="0.5.0")["releases"]
    cut = [r["version"] for r in rows]
    if not rows or cut[0] != wherefore.__version__:
        raise SystemExit(f"{ENGINE} lists {cut[0] if rows else 'no release'} as its newest release; "
                         f"the changelog starts at the release this site pins")
    for x in FEATURES:
        if x["since"] not in cut:
            raise SystemExit(f"{ENGINE} ships `{x['id']}` since {x['since']}, a release its releases.json "
                             f"does not list: the changelog would leave it out")
    for r in rows:
        for key in ("date", "title", "says", "shows"):
            if not r.get(key):
                raise SystemExit(f"{ENGINE} says nothing of release {r['version']}'s {key}")
    return [(r, [x for x in FEATURES if x["since"] == r["version"]]) for r in rows]


def terminal(shows, cut):
    """What a release printed, as a terminal shows it; a line of just … is lines left out."""
    lines = [f'<span class="term-prompt">$</span> {esc(shows["run"])}']
    for line in shows["output"]:
        lines.append(f'<span class="term-cut" title="{esc(cut)}">…</span>' if line == "…" else esc(line))
    return "\n".join(lines)


def changelog_page(f):
    """site/changelog/index.html: every release, from the engine; each feature in our words."""
    c, company, d = f["changelog"], f["company"], f["does"]
    items = []
    for r, brought in releases():
        v = r["version"]
        arrived = ""
        if brought:
            names = "".join(f'<li><span class="arrived-name">{esc(x["name"])}</span> '
                            f'{esc(d["words"][x["id"]]) if x["id"] in d["words"] else ""}</li>'
                            for x in brought)
            arrived = f'<h3>{esc(c["arrived"])}</h3><ul class="arrived">{names}</ul>'
        # WHAT THE RELEASE ANSWERED, from the engine's ledger (owner, 6 November
        # 2026): a request becomes a feature in a release, so this is where the
        # chain is told - who asked, the issues, and the plan, folded until
        # clicked - and the features page tells it once more from the feature.
        answered = [it for it in ROADMAP["items"]
                    if it["state"] == "shipped" and it.get("since") == v and it.get("issues")]
        if answered:
            rows = []
            for it in answered:
                links = ", ".join(f'<a class="road-issue" href="{esc(u)}">#{esc(u.rsplit("/", 1)[-1])}</a>' for u in it["issues"])
                asked = (f'<span class="road-asked">{esc(d["asked"])} <a href="https://github.com/{esc(it["asked_by"])}">'
                         f'@{esc(it["asked_by"])}</a></span>')
                toggle = (f'<span class="does-toggle"><span class="is-closed">{esc(d["more"])}</span>'
                          f'<span class="is-open">{esc(d["less"])}</span></span>')
                rows.append(f'<li id="road-{esc(it["id"])}"><details class="does-more"><summary><p class="does-name">'
                            f'<span class="arrived-name">{esc(it["name"])}</span> {links} {asked}{toggle}</p>'
                            f'<p>{esc(it["words"])}</p></summary>'
                            f'<p class="does-plan"><span class="road-asked">{esc(d["plan"])}</span> {esc(it["plan"])}</p></details></li>')
            arrived += f'<h3>{esc(c["answered"])}</h3><ul class="arrived answered">{"".join(rows)}</ul>'
        items.append(f"""<li class="release" id="v{esc(v)}">
<div class="release-meta"><p class="release-v"><a href="#v{esc(v)}">{esc(v)}</a></p>
<p class="release-date"><time datetime="{esc(r["date"])}">{esc(long_date(r["date"]))}</time></p></div>
<div class="release-body">
<h2>{esc(r["title"])}</h2>
<p class="release-says">{esc(r["says"])}</p>
<figure class="term"><pre><code>{terminal(r["shows"], c["cut"])}</code></pre>
<figcaption>{esc(c["printed"])}</figcaption></figure>
{arrived}
</div>
</li>""")
    name = company["name"]
    source = (f' · <a target="_blank" rel="noopener" href="{esc(company["source"])}">{esc(f["inspect"]["source"])}{OUT}</a>'
              if company["source"] else "")
    lines = [head(f'{c["title"]} — {name}', c["intro"], "../brand.css"), '<link rel="stylesheet" href="../page.css">']
    if company["domain"]:
        lines.append(f'<link rel="canonical" href="https://{esc(company["domain"])}/changelog/">')
    return f"""<!doctype html>
<html lang="en">
<head>
{chr(10).join(lines)}
</head>
<body>
{banner()}<header class="top">{topbar(f, "../")}</header>
<main id="top">
<section class="log-head"><div class="wrap">
<p class="eyebrow">{esc(c["title"])} · {esc(name)} {esc(wherefore.__version__)}</p>
<h1>{esc(c["heading"])}</h1>
<p class="lede">{esc(c["intro"])}</p>
</div></section>
<section class="log"><div class="wrap">
<ol class="releases">
{chr(10).join(items)}
</ol>
</div></section>
</main>
{sub_footer(f)}
</body>
</html>
"""


def sub_footer(f):
    """The footer of a page one level down: every link, the colophon, the source."""
    company = f["company"]
    name = company["name"]
    source = (f' · <a target="_blank" rel="noopener" href="{esc(company["source"])}">{esc(f["inspect"]["source"])}{OUT}</a>'
              if company["source"] else "")
    return (f'<footer><div class="wrap">{foot_nav(f, "../")}<div class="footer-row"><p><span class="footer-name">{esc(name)}</span>'
            f' · {esc(f["colophon"])}</p>\n<p class="footer-meta"><a href="../">{esc(name)}</a> · <a href="../brand/">Brand</a> · <a href="../{MAP_PAGE}">{esc(f["inspect"]["map_short"])}</a>{source}</p></div></div></footer>')


def sub_page(f, slug, eyebrow, heading, lede, body):
    """A page one level down, in the changelog's shell: the draft banner, the nav, its head, its body."""
    company = f["company"]
    name = company["name"]
    lines = [head(f"{heading} — {name}", lede or heading, "../brand.css"), '<link rel="stylesheet" href="../page.css">']
    if company["domain"]:
        lines.append(f'<link rel="canonical" href="https://{esc(company["domain"])}/{slug}/">')
    lede_html = f'<p class="lede">{esc(lede)}</p>' if lede else ""
    return f"""<!doctype html>
<html lang="en">
<head>
{chr(10).join(lines)}
</head>
<body>
{banner()}<header class="top">{topbar(f, "../")}</header>
<main id="top">
<section class="log-head"><div class="wrap">
<p class="eyebrow">{esc(eyebrow)}</p>
<h1>{esc(heading)}</h1>
{lede_html}
</div></section>
{body.replace(SRC, "")}
</main>
{sub_footer(f)}
</body>
</html>
"""


def docs_pages(f):
    """site/docs/: the docs the pinned engine ships, one page each, the first at /docs/.

    THE DOCS ARE THE ENGINE'S. `wherefore.docs.pages()` hands over every page of
    the release this site pins - start, commands, configuration, checks and
    proofs, reporting - as Markdown, held to the engine's code by its own
    tests. This site renders them (gen/markdown.py) in its shell, with the
    pages listed beside each and the page's own headings under that. The
    heading and the words around them are this site's; every page is the
    engine's, so a release that rewrites a page rewrites it here."""
    from markdown import render
    d = f["docs"]
    pages = wherefore_docs.pages()
    out = {}
    for pid, title, md in pages:
        slug = "docs/" if pid == pages[0][0] else f"docs/{pid}/"
        home = "../" if pid == pages[0][0] else "../../"
        listing = "".join(f'<li{" class=\"here\"" if p == pid else ""}><a href="{home}docs/{"" if p == pages[0][0] else p + "/"}">{esc(t)}</a></li>'
                          for p, t, _ in pages)
        heads = re.findall(r"^## (.+)$", md, re.M)
        on_page = "".join(f'<li><a href="#{re.sub(r"[^a-z0-9]+", "-", h.lower()).strip("-")}">{esc(h)}</a></li>' for h in heads)
        aside = (f'<aside class="docs-nav"><p class="docs-nav-title">{esc(d["pages"])}</p><ul>{listing}</ul>'
                 + (f'<p class="docs-nav-title">{esc(d["on_this_page"])}</p><ul class="docs-on-page">{on_page}</ul>' if on_page else "")
                 + '</aside>')
        body = f'<section class="docs"><div class="wrap docs-grid">{aside}<article class="docs-page">{render(md, shift=1)}</article></div></section>'
        out[slug] = (title, body)
    return out


def docs_page(f, slug, title, body):
    """One docs page in the sub-page shell, one or two levels down."""
    d, company = f["docs"], f["company"]
    depth = slug.count("/")
    up = "../" * depth
    name = company["name"]
    lines = [head(f"{title} · {d['title']} — {name}", d["intro"], f"{up}brand.css"), f'<link rel="stylesheet" href="{up}page.css">']
    if company["domain"]:
        lines.append(f'<link rel="canonical" href="https://{esc(company["domain"])}/{slug}">')
    return f"""<!doctype html>
<html lang="en">
<head>
{chr(10).join(lines)}
</head>
<body>
{banner()}<header class="top">{topbar(f, up)}</header>
<main id="top">
<section class="log-head"><div class="wrap">
<p class="eyebrow">{esc(d["title"])} · {esc(name)} {esc(wherefore.__version__)}</p>
<h1>{esc(d["heading"])}</h1>
<p class="lede">{esc(d["intro"])}</p>
</div></section>
{body}
</main>
{sub_footer(f).replace('href="../', 'href="' + up)}
</body>
</html>
"""


def features_page(f):
    """site/features/index.html: every feature the release ships, tagged with the release it arrived in, then what is next."""
    d = f["does"]
    return sub_page(f, "features", f'{f["nav"]["does"]} · {f["company"]["name"]} {wherefore.__version__}',
                    d["heading"], None, does(f) + planned(f))


def short(usage):
    """`wherefore gate [--keep]` -> `wherefore gate`: the command, without what it takes."""
    return " ".join(w for w in usage.split()
                    if not (w[:1] in "[-." or w.endswith("]") or w.isupper() or "|" in w))


def does(f):
    """Every feature the pinned release ships, in this company's words.

    THE PROMISE, KEPT HERE FIRST. A release that adds a feature this page does not
    describe stops the build until the facts say something about it - words in
    `does.words`, or its name in `does.unshown` with the reason it is left off -
    so nothing the product does can ship without the page telling people. Words
    for a feature the release no longer has stop it too. The name, the release it
    arrived in and the command are the engine's; only the words are ours. The
    features of the newest release that brought any are marked new; every release
    is on the changelog, each feature under the one it arrived in."""
    d = f["does"]
    words, unshown = d["words"], d["unshown"]
    shipped = [x["id"] for x in FEATURES]
    for x in FEATURES:
        if x["id"] not in words and x["id"] not in unshown:
            raise SystemExit(f"{ENGINE} ships the feature `{x['id']}` - {x['name']}, since {x['since']} - "
                             f"and facts/company.json says nothing about it. Give it words in does.words, "
                             f"or name it in does.unshown with the reason")
    for k in list(words) + list(unshown):
        if k not in shipped:
            raise SystemExit(f"does says something about `{k}`, which {ENGINE} does not ship: "
                             f"its features are {', '.join(shipped)}")
    # The newest features: those of the latest release that brought any. A
    # release that only mends what is there leaves the last new ones marked.
    newest = max((x["since"] for x in FEATURES), key=lambda v: tuple(int(n) for n in v.split(".")))
    # WHAT EACH FEATURE ANSWERED: the roadmap's shipped items that name it, with
    # their issues, who asked, and the plan - the engine's ledger, shown whole
    # (owner, 6 November 2026: the chain from a request to what shipped is not
    # to be missed again).
    answered = {}
    for it in ROADMAP["items"]:
        if it["state"] == "shipped" and it.get("issues"):
            answered.setdefault(it["feature"], []).append(it)
    items = []
    for x in FEATURES:
        if x["id"] in unshown:
            unshown[x["id"]]                          # read, so its reason is accounted for
            continue
        new = (f' <span class="chip chip-new">{esc(fill(d["new"], version=newest))}</span>'
               if x["since"] == newest else "")
        cmds = "".join(f'<p class="does-cmd"><code>{esc(command(short(c)))}</code></p>' for c in x.get("commands", []))
        since = f' <span class="chip chip-since">{esc(fill(d["since"], version=x["since"]))}</span>'
        asks = []
        for it in answered.get(x["id"], []):
            links = ", ".join(f'<a class="road-issue" href="{esc(u)}">#{esc(u.rsplit("/", 1)[-1])}</a>' for u in it["issues"])
            asks.append(f'<p class="does-answers"><span class="road-asked">{esc(d["answers"])}</span> {links} '
                        f'<span class="road-asked">{esc(d["asked"])} <a href="https://github.com/{esc(it["asked_by"])}">'
                        f'@{esc(it["asked_by"])}</a> · {esc(fill(d["since"], version=it["since"]))}</span></p>'
                        f'<p class="does-plan"><span class="road-asked">{esc(d["plan"])}</span> {esc(it["plan"])}</p>')
        # The feature opens to its details: the paragraph a person reads when
        # they want more than the line, every command, and what it answered.
        # <details> needs no script, and the page runs none.
        toggle = (f'<span class="does-toggle"><span class="is-closed">{esc(d["more"])}</span>'
                  f'<span class="is-open">{esc(d["less"])}</span></span>')
        # THE FEATURE IN MOTION: its clip, the page the pinned engine wrote into
        # site/motion/, played in a frame on the card - the same facts, in time.
        clip = (f'<figure class="does-motion"><iframe src="../motion/{esc(x["id"])}/index.html" loading="lazy" '
                f'title="{esc(x["name"])}, {esc(d["watch"].lower())}"></iframe>'
                f'<figcaption>{esc(d["watch"])}</figcaption></figure>')
        # The command stays on the closed card (owner, 6 November 2026), the
        # clip opens with the details, in a landscape frame that takes the
        # card's width.
        items.append(f'<li id="{esc(x["id"])}"><details class="does-more"><summary><p class="does-name">{esc(x["name"])}{since}{new}{toggle}</p>'
                     f'<p>{esc(words[x["id"]])}</p>{cmds}</summary>'
                     f'<p class="does-details"><span class="road-asked">{esc(d["open"])}</span> {esc(x["details"])}</p>'
                     f'{"".join(asks)}{clip}</details></li>')
    return f"""<section id="does"><div class="wrap">
<p class="does-intro">{esc(d["intro"])} <a href="../changelog/">{esc(f["changelog"]["link"])}</a></p>
<ul class="does">
{chr(10).join(items)}
</ul>
</div></section>"""


def planned(f):
    """What is next: the engine's own roadmap, from the copy of it this site holds (facts/roadmap.json).

    An item's anchor is road-<id>, so a shipped item and the feature it became
    never share one; the feature's is its own id.

    THE SITE OWNS NO ROADMAP. The engine's sits beside its code, public, where
    the people and agents working on it plan from it; this site keeps a copy,
    byte for byte, and `wherefore check upstream` fails the deploy when the
    engine's file has moved, until the copy is taken again. The heading and
    the labels are this site's words; every item is the engine's. THE ROADMAP
    IS THE INBOX'S LEDGER: an item that answers a request names the issue and
    who asked and carries its plan, and when it ships it stays, marked shipped
    with the release and the feature - told on the changelog, under that
    release, and on the feature it became; here only what is still to come.
    An item the pinned release ships that is not marked shipped stops the
    build, and the engine's own test refuses the same."""
    p = f["planned"]
    shipped = {x["id"]: x for x in FEATURES}
    nxt = []
    for it in ROADMAP["items"]:
        if it["id"] in shipped and it["state"] != "shipped":
            raise SystemExit(f"the roadmap copied in facts/roadmap.json lists `{it['id']}` ({it['name']}) as {it['state']}, "
                             f"and {ENGINE} ships it: take the copy again from the engine, where it is marked shipped")
        if it["state"] == "shipped":
            if it["feature"] not in shipped:
                raise SystemExit(f"roadmap item `{it['id']}` shipped as `{it['feature']}`, which {ENGINE} does not ship")
            continue              # the changelog tells what each release answered; here is what is still to come
        if it["state"] not in p["labels"]:
            raise SystemExit(f"roadmap item `{it['id']}` is {it['state']!r}, which planned.labels does not name")
        # Who asked, when the engine's roadmap says: the person's GitHub login, which the
        # issue they asked in already shows, so the site says nothing the issue does not.
        issues = "".join(f' <a class="road-issue" href="{esc(u)}">#{esc(u.rsplit("/", 1)[-1])}</a>' for u in it.get("issues", []))
        if it.get("asked_by"):
            issues = (f' <span class="road-asked">{esc(p["labels"]["asked"])} '
                      f'<a href="https://github.com/{esc(it["asked_by"])}">@{esc(it["asked_by"])}</a></span>' + issues)
        # An item with a plan opens to it, like a feature to its details (owner,
        # 6 November 2026: compact until clicked); one without is the line alone.
        plan = (f'<p class="does-plan"><span class="road-asked">{esc(p["labels"]["plan"])}</span> {esc(it["plan"])}</p>'
                if it.get("plan") else "")
        toggle = (f'<span class="does-toggle"><span class="is-closed">{esc(f["does"]["more"])}</span>'
                  f'<span class="is-open">{esc(f["does"]["less"])}</span></span>') if plan else ""
        chip = f'<span class="chip chip-{esc(it["state"])}">{esc(p["labels"][it["state"]])}</span>'
        head = f'<p class="does-name">{esc(it["name"])} {chip}{toggle}</p><p>{esc(it["words"])}</p>'
        links = f'<p class="does-answers">{issues}</p>' if issues else ""
        nxt.append(f'<li id="road-{esc(it["id"])}">' + (f'<details class="does-more"><summary>{head}</summary>{links}{plan}</details>'
                                                     if plan else head + links) + '</li>')
    return f"""<section id="next"><div class="wrap">
<h2>{esc(p["heading"])}</h2>
<p class="does-intro">{esc(p["source"])}</p>
<ul class="does">
{chr(10).join(nxt)}
</ul>
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


def ground(name):
    """A brand colour, as the six hex digits the pendulum's model takes for its background."""
    have = colours()
    if name not in have:
        raise SystemExit(f"case.model.ground names {name!r}, which is not a colour in brand/tokens.json. "
                         f"It has: {', '.join(have)}")
    return have[name].lstrip("#")


def model(m):
    """The pendulum's model in a frame that may run its script and nothing else."""
    g = m["ground"]
    return (f'<figure class="case-model"><iframe src="{MODEL_PAGE}?embed=1&amp;bg={ground(g)}" '
            f'title="{esc(m["title"])}" loading="lazy" sandbox="allow-scripts" '
            f'style="background: var(--{esc(g)})"></iframe>'
            f'<figcaption>{esc(m["hint"])}</figcaption></figure>')


# The plate alone: the pendulum's public hero opened on one made part, the
# mounting plate, which the pendulum writes for exactly this frame. Its own
# script hides everything but the part, fits it to the frame and turns it; the
# frame adds only the overflow rule, so no scrollbar ever shows beside it.
PART = ROOT / "cases/pendulum/plate.html"
PART_PAGE = "pendulum/plate/"
PART_FRAMING = "\n<style>html,body{overflow:hidden}</style>\n"


def plate(m):
    """The pendulum's mounting plate in a frame that may run its script and nothing else."""
    g = m["ground"]
    return (f'<figure class="case-part"><iframe src="{PART_PAGE}?bg={ground(g)}" '
            f'title="{esc(m["title"])}" loading="lazy" sandbox="allow-scripts" '
            f'style="background: var(--{esc(g)})"></iframe>'
            f'<figcaption>{esc(m["hint"])}</figcaption></figure>')


def part_page(f):
    """site/pendulum/plate/index.html: the pendulum's plate, byte for byte, and what frames it."""
    t = f["case"]["part"]["taken"]
    said = f'{t["from"]} {t["file"]} at {t["commit"]}, {t["on"]}'
    if "--" in said:
        raise SystemExit(f"case.part.taken cannot be written in a comment: {said!r}")
    return (f"<!doctype html>\n<!-- The pendulum's mounting plate, alone: {said}, copied byte for byte into "
            f"cases/pendulum/plate.html, and framed for the case study by gen/site.py. -->\n"
            f'<html lang="en">\n' + PART.read_text(encoding="utf-8") + PART_FRAMING)


def model_page(f):
    """site/pendulum/index.html: the pendulum's own model, byte for byte, and what frames it."""
    t = f["case"]["model"]["taken"]
    said = f'{t["from"]} {t["file"]} at {t["commit"]}, {t["on"]}'
    if "--" in said:
        raise SystemExit(f"case.model.taken cannot be written in a comment: {said!r}")
    return (f"<!doctype html>\n<!-- The pendulum's own model: {said}, copied byte for byte into "
            f"cases/pendulum/model.html, and framed for the case study by gen/site.py. -->\n"
            f'<html lang="en">\n' + MODEL.read_text(encoding="utf-8") + FRAMING)


def case(f, p):
    c = f["case"]
    made = "".join(f"<li>{esc(m)}</li>" for m in c["made"])
    held = "".join(f"<li>{esc(m)}</li>" for m in c["held"])
    counts = p["counts"]
    stats = "".join(f'<li><span class="stat-n">{counted(counts, s["of"])}</span> {esc(s["what"])}</li>'
                    for s in c["stats"])
    quote = ""
    if c["quote"]:
        quote = (f'<blockquote class="case-quote"><p>{esc(c["quote"]["text"])}</p>'
                 f'<footer>{esc(c["quote"]["by"])}</footer></blockquote>')
    return f"""<section id="case" class="case"><div class="wrap">
{SRC}
<div class="case-head">
<p class="eyebrow">{esc(c["eyebrow"])} · {esc(c["name"])}</p>
<h2>{esc(c["heading"])}</h2>
{model(c["model"])}
<p class="case-text">{esc(c["text"])}</p>
<p class="actions"><a class="button button-quiet" href="{esc(c["url"])}">{esc(c["visit"])}</a></p>
</div>
{quote}
<div class="counts">
<ul class="stats">{stats}</ul>
{plate(c["part"])}
</div>
<details class="case-more"><summary>{esc(c["more"])}</summary>
<div class="case-grid">
<div class="case-col"><h3>{esc(c["made_heading"])}</h3><ul class="case-list">{made}</ul></div>
<div class="case-col"><h3>{esc(c["held_heading"])}</h3><ul class="case-list case-held">{held}</ul></div>
</div>
</details>
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
    """Getting started: install, scan (one place, or a site and an app together), init - in this company's words; the licence and package are the release's."""
    st, h = f["start"], f["hero"]
    name, licence = release_meta()
    lines = [f'<li><code>{esc(st["install"])}</code><span class="does">{esc(h["pip"])} <code>pip install {esc(name)}</code></span></li>']
    for s in st["steps"]:
        run = f'{command(s["command"])} {s.get("args", "")}'.strip()
        # A step with a second form - the scan pointed at a site and an app
        # together (owner, 6 November 2026) - shows it under the first, with
        # its own words, so Get started says both ways the hero does.
        also = (f'<code>{esc(command(s["command"]))} {esc(s["also"])}</code><span class="does">{esc(s["also_says"])}</span>'
                if s.get("also") else "")
        lines.append(f'<li><code>{esc(run)}</code><span class="does">{esc(s["says"])}</span>{also}</li>')
    return f"""<section id="start"><div class="wrap">
{SRC}
<div class="start-box">
<h2>{esc(st["heading"])}</h2>
<p class="start-text">{esc(st["text"])}</p>
<ol class="start-steps">
{chr(10).join(lines)}
</ol>
<p class="start-free">{esc(fill(st["free"], licence=licence))}</p>
</div>
</div></section>"""


def footer(f):
    company = f["company"]
    meta = f'<a href="changelog/">Wherefore {esc(version())}</a> · <a href="brand/">Brand</a> · <a href="{MAP_PAGE}">{esc(f["inspect"]["map_short"])}</a>'
    if company["contact"]:
        meta += f' · <a href="mailto:{esc(company["contact"])}">{esc(company["contact"])}</a>'
    if company["source"]:
        meta += f' · <a target="_blank" rel="noopener" href="{esc(company["source"])}">{esc(f["inspect"]["source"])}{OUT}</a>'
    if company["domain"]:
        meta += f' · {esc(company["domain"])}'
    return (f'<footer><div class="wrap">{SRC}{foot_nav(f)}<div class="footer-row"><p><span class="footer-name">{esc(company["name"])}</span>'
            f' · {esc(f["colophon"])}</p><p class="footer-meta">{meta}</p></div></div></footer>')


def page(f):
    company, site, inspect = f["company"], f["site"], f["inspect"]
    lines = [head(site["title"], f["hero"]["lede"], "brand.css"),
             '<link rel="stylesheet" href="page.css">']
    if company["domain"]:
        lines.append(f'<link rel="canonical" href="https://{esc(company["domain"])}/">')
    parts = {name: part(render, f, inspect, *also) for name, render, *also in (
        ("header", header), ("hero", hero), ("forks", opening), ("demo", ripple), ("how", how),
        ("case", case, (("facts/pendulum.json", PENDULUM),)),
        ("rule", rule), ("why", why), ("start", start), ("footer", footer))}
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
{parts["forks"]}
{parts["demo"]}
{parts["how"]}
{parts["case"]}
{parts["rule"]}
{parts["why"]}
{parts["start"]}
</main>
{parts["footer"]}
<label class="inspect-switch" for="inspect"><span class="switch-track" aria-hidden="true"></span><span class="switch-long">{esc(inspect["toggle"])}</span><span class="switch-short">{esc(inspect["toggle_short"])}</span></label>
</body>
</html>
"""


def headers():
    """What Cloudflare sends with every file: nothing loads from elsewhere, no
    script runs, and a draft is not indexed - but for the pendulum's model,
    which may run its own script, inline, load nothing, and be framed only here."""
    lines = [
        "/*",
        "  Content-Security-Policy: default-src 'none'; style-src 'self' 'unsafe-inline'; font-src 'self'; "
        "img-src 'self' data:; frame-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
        "  X-Content-Type-Options: nosniff",
        "  Referrer-Policy: no-referrer",
    ]
    if status() == "draft":
        lines.append("  X-Robots-Tag: noindex, nofollow")
    # The installer, shown as text to a browser that opens it - "read it
    # before you run it" has to be possible - and run by sh from curl.
    lines += ["", "/install.sh", "  Content-Type: text/plain; charset=utf-8"]
    # The model: the policy above taken off (`!`) and its own put on.
    lines += ["", f"/{MODEL_PAGE}*", "  ! Content-Security-Policy",
              "  Content-Security-Policy: default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
              "img-src data:; font-src data:; base-uri 'none'; form-action 'none'; frame-ancestors 'self'"]
    # The clips: each a page in motion the engine wrote, its style inline and
    # the brand's stylesheet and fonts from this site, no script; framed only
    # here, on the feature's card (owner, 6 November 2026: on a phone the
    # frame showed nothing - the page refused the card under the policy above).
    lines += ["", "/motion/*", "  ! Content-Security-Policy",
              "  Content-Security-Policy: default-src 'none'; style-src 'self' 'unsafe-inline'; font-src 'self'; "
              "base-uri 'none'; form-action 'none'; frame-ancestors 'self'"]
    # The map: the engine's own page, one file with its style and its script
    # inside it, loading nothing; its path may run that script and nothing else.
    lines += ["", f"/{MAP_PAGE}*", "  ! Content-Security-Policy",
              "  Content-Security-Policy: default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
              "font-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"]
    return "\n".join(lines) + "\n"


def main():
    SITE.mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "gen/page.css", SITE / "page.css")
    (SITE / "index.html").write_text(page(FACTS), encoding="utf-8")
    (SITE / "_headers").write_text(headers(), encoding="utf-8")
    (SITE / "changelog").mkdir(exist_ok=True)
    (SITE / "changelog/index.html").write_text(changelog_page(FACTS), encoding="utf-8")
    for slug, (title, body) in docs_pages(FACTS).items():
        (SITE / slug).mkdir(parents=True, exist_ok=True)
        (SITE / slug / "index.html").write_text(docs_page(FACTS, slug, title, body), encoding="utf-8")
    (SITE / "features").mkdir(exist_ok=True)
    (SITE / "features/index.html").write_text(features_page(FACTS), encoding="utf-8")
    (SITE / MODEL_PAGE).mkdir(exist_ok=True)
    (SITE / MODEL_PAGE / "index.html").write_text(model_page(FACTS), encoding="utf-8")
    (SITE / PART_PAGE).mkdir(exist_ok=True)
    (SITE / PART_PAGE / "index.html").write_text(part_page(FACTS), encoding="utf-8")


if __name__ == "__main__":
    main()
