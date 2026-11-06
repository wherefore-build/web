"""Every feature, in motion: a short clip for each feature the pinned engine ships, compiled from the facts.

A CLIP IS A PAGE. For each feature the engine ships, this writes one HTML
page whose motion is CSS: the version, who asked, the command run and what
it printed, what the feature does drawn in this site's own numbers, the
claim, and the address. Every word is a fact: the engine's features,
releases and docs, the roadmap's ledger, and this company's own words in
facts/company.json (`does.claim`). Nothing is written for the clip. The page
plays in any frame it is shown in, portrait or landscape, because every size
is a share of the frame; the features page and the changelog play it on
each card, and gen/motion_render.py steps it frame by frame into a video by
setting `--t` on a page marked `still`, which pauses every animation at that
second. A viewer who asks for less motion sees the claim, still.

THIS IS THE SITE'S, NOT THE ENGINE'S (owner, 6 November 2026). The engine's
generic concepts are sources, generators, the gate, checks and proofs; a clip
template is one company's generator, like the pendulum's renders are the
pendulum's. What the engine supplies is what it already ships for every
page here: the features, the releases, the docs' examples. The pictures a
mechanism scene draws are filled from this corpus - its own file counts,
pages, sources and ledger - read the way the gate and the scan read them.

WHAT HOLDS IT: checks/motion_reads.py (every clip's length and reading
speed, the command typed is one the CLI has, every printed line is one the
engine prints, the page carries every word), checks/motion_for_every_feature.py
(every feature has its clip and the pages play it) and checks/motion_fits.py
(every clip fits both frames at every scene). Each has its proof.

Writes site/motion/<id>/index.html and motion/<id>/storyboard.json; the
storyboards sit out of site/ because they quote what a command printed,
and the palette check reads site/.
"""
import collections
import html
import json
import math
import os
import pathlib
import re
import subprocess
import sys
from importlib.resources import files

import wherefore
from wherefore import docs as wherefore_docs
from kit import FACTS, ROADMAP, ROOT, SITE, esc

ELIDED = "…"
CLAIM_WORDS = 12
WORDS_PER_SECOND = 3.0           # a headline
CAPTION_WORDS_PER_SECOND = 2.5   # a caption under a picture
PRINTED_WORDS_PER_SECOND = 3.5   # printed lines are scanned, not read
TYPE_SECONDS = 0.055             # a character typed
WORKING_SECONDS = 0.9            # the dots between a command and its output
MIN_SECONDS = 16.0
MAX_SECONDS = 40.0
LINE_WORDS = 14                  # an output line longer than this is cut at a clause, with … to say so
ANSWER_LINES = 4
ANSWER_WORDS = 28
TYPED_LINE = 28                  # characters of a typed command per line, in a portrait frame
PAGES_SHOWN = 8
OUT = SITE / "motion"
BOARDS = ROOT / "motion"
CSS = SITE / "brand.css"
ICON = SITE / "brand/icon.svg"
INSTALL = "pip install wherefore-build"
KINDS = ("compare", "hold", "sort", "handover")
# Which picture each feature's mechanism scene draws: values compared across
# places; a fact held across pages; files sorted; a request handed over. A
# feature the engine adds without a line here stops the build.
MECHANISM = {"scan": "compare", "scan2": "compare", "scan-read": "compare", "drift": "compare",
             "reach": "hold", "retired": "hold", "claims": "hold", "published": "hold", "upstream": "hold", "palette": "hold",
             "gate": "sort", "build": "sort", "graph": "sort", "proofs": "sort", "hook": "sort",
             "report": "handover", "pins": "handover", "skill": "handover", "docs": "handover", "start": "handover",
             "motion": "handover"}


def engine(name):
    data = files("wherefore") / name
    if not data.is_file():
        raise SystemExit(f"the pinned engine, wherefore {wherefore.__version__}, has no {name}")
    return json.loads(data.read_text(encoding="utf-8"))


FEATURES = engine("features.json")["features"]
RELEASES = {r["version"]: r for r in engine("releases.json")["releases"]}
COMMANDS = engine("commands.json")["commands"]


def words(text):
    return len(text.split())


def head(usage):
    """The words of a command's usage a person always types: up to the first
    placeholder or flag. `wherefore gate [--keep]` -> `wherefore gate`."""
    out = []
    for tok in usage.split():
        if tok.startswith(("[", "-")) or tok.upper() == tok and any(c.isalpha() for c in tok):
            break
        out.append(tok)
    return " ".join(out)


def cut(line, limit=LINE_WORDS):
    """A line of at most `limit` words: whole clauses while they fit, then …"""
    if words(line) <= limit:
        return line
    parts = re.split(r"(?<=[.;:])\s+|\s+-\s+", line)
    kept, n = [], 0
    for p in parts:
        if n + words(p) > limit:
            break
        kept.append(p)
        n += words(p)
    text = " ".join(kept).rstrip(".;:") if kept else " ".join(line.split()[:limit])
    return text + ELIDED


def docs_examples():
    out = []
    for _pid, _title, text in wherefore_docs.pages():
        out += wherefore_docs.examples(text)
    return out


def picture(feature, release, examples):
    """(typed, lines): what the clip runs and what it prints, from the release
    picture when it shows this feature's command, else from the docs' example
    of it; (None, []) when the feature has no command to show."""
    shows = (release or {}).get("shows") or {}
    run = shows.get("run", "")
    heads = [head(u) for u in feature.get("commands", [])]
    if run and run.split()[1:2] != ["--version"] and (not heads or any(run.startswith(h) for h in heads)):
        return run, [l for l in shows.get("output", []) if l.strip() and l != ELIDED]
    for h in heads:
        for cmd, lines in examples:
            if cmd == h or cmd.startswith(h + " "):
                return cmd, [l for l in lines if l != ELIDED]
    if heads:
        return heads[0], []
    return None, []


def answer(lines, short=False):
    """At most ANSWER_LINES lines and ANSWER_WORDS words, the last line always,
    each cut at a clause: the result is the point. `short`, when a mechanism
    scene follows: the last line alone."""
    if not lines:
        return []
    last = cut(lines[-1])
    if short:
        return [last]
    kept, n = [last], words(last)
    for l in reversed(lines[:-1]):
        c = cut(l)
        if len(kept) >= ANSWER_LINES or n + words(c) > ANSWER_WORDS:
            break
        kept.insert(0, c)
        n += words(c)
    return kept


def typed_lines(typed):
    """A command in lines of at most TYPED_LINE characters, broken at spaces,
    every line but the last ending in the shell's backslash."""
    ws, lines, cur = typed.split(), [], ""
    for w in ws:
        if cur and len(cur) + 1 + len(w) + 2 > TYPED_LINE:
            lines.append(cur + " \\")
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    lines.append(cur)
    return lines


def seconds(text_words, least, most, rate):
    """Long enough to read at `rate` words a second, in half seconds, within bounds."""
    return max(least, min(most, math.ceil(text_words / rate * 2) / 2))


def texts(scene):
    """Every string a scene shows, in reading order."""
    out = []
    for k in ("name", "version", "eyebrow", "headline", "typed", "text", "caption", "home", "tagline", "install", "url"):
        if scene.get(k):
            out.append(scene[k])
    out += scene.get("lines", [])
    return out


# ── what the mechanism scene is filled with: this corpus's own numbers ──────

def tracked():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True).stdout
    return [p for p in out.split("\0") if p]


def gather():
    """{kind: data}, each read the way the gate and the scan read this corpus."""
    from wherefore import config as cfgmod, gate, graph, scan, sources
    cfg = cfgmod.load(ROOT)
    data = {}
    graph.configure(cfg)
    decl = gate.DECL()
    decl.setdefault("authored", {}).setdefault("rules", [])
    decl.setdefault("captured", {}).setdefault("groups", {})
    captured = gate.captured_files(decl)
    rules = decl["authored"]["rules"]
    fs = tracked()
    n_cap = sum(1 for f in fs if f in captured)
    n_auth = sum(1 for f in fs if f not in captured and gate.authored_rule(f, rules))
    data["sort"] = {"files": len(fs), "built": len(fs) - n_cap - n_auth, "authored": n_auth, "captured": n_cap, "left": 0}

    name, src = cfg.source()
    doc = json.loads((ROOT / src["path"]).read_text(encoding="utf-8"))
    pages = sorted(f for f in fs if f.endswith(".html") and f.startswith("site/") and not f.startswith("site/motion/"))
    probes = ((cfg.doc.get("reach") or {}).get("probes") or [])
    probe = max(probes, key=lambda p: len(p.get("files", [])), default=None)

    def label(rel):                      # site/pendulum/plate/index.html -> pendulum/plate/; site/index.html -> /
        parts = rel.split("/")
        inner = parts[1:-1]
        return "/".join(inner) + "/" if inner else ("/" if parts[-1] == "index.html" else parts[-1])
    data["hold"] = {"source": src["path"], "facts": sum(1 for _ in sources.leaves(doc)), "pages": len(pages),
                    "shown": list(dict.fromkeys(label(p) for p in pages))[:PAGES_SHOWN],
                    "probe": {"fact": probe["fact"], "files": len(probe["files"])} if probe else None}

    got = scan.scan([str(SITE)])
    data["compare"] = {"places": ["site"], "stated": got["stated"], "files": got["sources"],
                       "disagree": len(got["disagree"]), "says": [g["says"] for g in got["disagree"][:2]]}

    with_issues = [it for it in ROADMAP["items"] if it.get("issues")]
    data["handover"] = {"issues": sum(len(it["issues"]) for it in with_issues), "items": len(with_issues),
                        "releases": len(RELEASES),
                        "steps": ["an issue", "the plan, on it", "the release", "the note that closes it"]}
    return data


def caption(kind, d):
    """The one line said under the picture; every number is the picture's."""
    if kind == "sort":
        return (f"{d['files']} files tracked: {d['built']} built by a script, {d['authored']} written with a reason, "
                f"{d['captured']} captured and stamped, {d['left']} unaccounted for")
    if kind == "hold":
        probe = (f"; {d['probe']['fact']} alone reaches {d['probe']['files']} "
                 f"{'page' if d['probe']['files'] == 1 else 'pages'}") if d.get("probe") else ""
        return (f"{d['facts']} facts in {d['source']}, and {d['pages']} "
                f"{'page' if d['pages'] == 1 else 'pages'} built from them{probe}")
    if kind == "compare":
        return (f"{d['stated']} values stated across {d['files']} pages in {', '.join(d['places'])}; "
                f"{d['disagree']} disagree")
    if kind == "handover":
        return f"{d['issues']} issues answered by {d['items']} roadmap items across {d['releases']} releases"
    raise ValueError(kind)


EYEBROW = {"compare": "what it compares", "hold": "what it holds", "sort": "what it sorts",
           "handover": "what it hands over"}


# ── the storyboard ──────────────────────────────────────────────────────────

def storyboard(feature, item, examples, mechanics, claim):
    """The scenes of one feature's clip, in time: [{kind, start, end, ...}]."""
    version = feature["since"]
    release = RELEASES.get(version)
    scenes = []

    def add(kind, least, most, rate=WORDS_PER_SECOND, **text):
        start = scenes[-1]["end"] if scenes else 0.0
        sc = dict(kind=kind, start=start, end=0.0, **text)
        sc["end"] = round(start + seconds(sum(words(t) for t in texts(sc)), least, most, rate), 2)
        scenes.append(sc)

    name = FACTS["company"]["name"]
    add("open", 3.0, 3.0, name=name, version=version)
    if item and item.get("issues"):
        eyebrow = f"asked for by {item['asked_by']} · #{', #'.join(u.rsplit('/', 1)[1] for u in item['issues'])}"
    else:
        eyebrow = f"shipped in {version}"
    add("ask", 4.0, 5.5, eyebrow=eyebrow, headline=feature["name"])
    kind = MECHANISM.get(feature["id"])
    if kind is None:
        raise SystemExit(f"the pinned engine ships `{feature['id']}` and gen/motion.py names no mechanism for it: "
                         f"say which picture its clip draws, one of {', '.join(KINDS)}")
    mech = mechanics.get(kind)
    typed, printed = picture(feature, release, examples)
    lines = answer(printed, short=mech is not None)
    if typed:
        # ONE TERMINAL: the command typed, a moment's work, then what it printed
        # (owner, 6 November 2026: no labels - a command is plainly a command).
        typing = 0.5 + TYPE_SECONDS * len(typed) + 0.2 * (len(typed_lines(typed)) - 1)
        shown = typing + (WORKING_SECONDS + 0.45 * (len(lines) - 1) if lines else 0)
        read = seconds(sum(words(l) for l in lines), 2.0, 6.0, PRINTED_WORDS_PER_SECOND) if lines else 1.5
        length = math.ceil((shown + read) * 2) / 2
        add("run", length, length, typed=typed, lines=lines, typing=round(typing, 2))
    elif mech is None:
        more = cut(feature.get("details", "").split(". ")[0].strip().rstrip("."), 24)
        if more:
            add("more", 4.0, 9.0, CAPTION_WORDS_PER_SECOND, eyebrow="what it does", text=more)
    if mech is not None:
        add("mechanism", 5.5, 12.0, CAPTION_WORDS_PER_SECOND, eyebrow=EYEBROW[kind], mechanism=kind, data=mech,
            caption=caption(kind, mech))
    add("claim", 4.0, 4.5, text=claim)
    home = FACTS["company"]["domain"]
    add("close", 6.0, 6.0, home=home, tagline=FACTS["start"]["heading"], install=INSTALL,
        url=f"{home}/features/#{feature['id']}", icon="icon")
    return {"id": feature["id"], "name": feature["name"], "version": version,
            "duration": scenes[-1]["end"], "frames": ["portrait", "landscape"], "scenes": scenes}


def claims():
    """`does.claim`: one sentence of at most CLAIM_WORDS words per feature, the
    line its clip ends on. A feature without one, or a line too long to read,
    stops the build - like a feature without words."""
    said = FACTS["does"].get("claim", {})
    out = {}
    for x in FEATURES:
        if x["id"] in FACTS["does"].get("unshown", {}):
            continue
        c = said.get(x["id"], "").strip()
        if not c:
            raise SystemExit(f"the pinned engine ships `{x['id']}` - {x['name']} - and facts/company.json "
                             f"has no does.claim for it: one sentence, at most {CLAIM_WORDS} words, the line its clip ends on")
        if words(c) > CLAIM_WORDS or not re.search(r"[.!?]$", c):
            raise SystemExit(f"does.claim.{x['id']} is {words(c)} words, or not a sentence: a clip reads "
                             f"{CLAIM_WORDS} at most, and ends on a full stop")
        out[x["id"]] = c
    for k in said:
        if k not in {x["id"] for x in FEATURES}:
            raise SystemExit(f"does.claim says something about `{k}`, which the pinned engine does not ship")
    return out


def storyboards():
    items = {it["feature"]: it for it in ROADMAP["items"] if it.get("state") == "shipped" and it.get("feature")}
    ex, mech, said = docs_examples(), gather(), claims()
    return [storyboard(f, items.get(f["id"]), ex, mech, said[f["id"]]) for f in FEATURES if f["id"] in said]


# ── the page ────────────────────────────────────────────────────────────────

def pct(t, total):
    return f"{t / total * 100:.3f}%"


def window(name, start, end, total, fade_in=0.3, fade_out=0.3, rise=False):
    """A scene's window: in at `start`, out at `end`. A cut is a fade of a
    fiftieth, since two keyframes at one instant make the browser ramp from the
    clip's start. `rise` brings the scene up into place as it comes."""
    fade_in, fade_out = max(fade_in, 0.02), max(fade_out, 0.02)
    a, b = start + fade_in, max(start + fade_in, end - fade_out)
    up = ";transform:translateY(4cqmin)" if rise else ""
    flat = ";transform:none" if rise else ""
    return (f"@keyframes {name}{{0%,{pct(start, total)}{{opacity:0{up}}}{pct(a, total)}{{opacity:1{flat}}}"
            f"{pct(b, total)}{{opacity:1{flat}}}{pct(end, total)},100%{{opacity:0{flat}}}}}")


def staggered(prefix, i, parts, t0, step, total, rules, cls="w", tag="span"):
    """`parts` as elements, each arriving `step` after the last from `t0`."""
    out = []
    for j, part in enumerate(parts):
        rules.append(f"@keyframes {prefix}{i}_{j}{{0%,{pct(t0 + step * j, total)}{{opacity:0}}"
                     f"{pct(t0 + step * j + 0.25, total)},100%{{opacity:1}}}}")
        out.append(f'<{tag} class="{cls}" style="animation-name:{prefix}{i}_{j}">{esc(part)}</{tag}>')
    return out


def picture_html(sc, i, total, rules):
    """The mechanism scene's inner HTML; keyframes for its parts go into `rules`."""
    kind, d, t0 = sc["mechanism"], sc["data"], sc["start"]
    counted = [0]

    def appear(name, at, grow=False):
        a, b = pct(at, total), pct(at + 0.35, total)
        if grow:
            rules.append(f"@keyframes {name}{{0%,{a}{{width:0}}{b},100%{{width:var(--w)}}}}")
        else:
            rules.append(f"@keyframes {name}{{0%,{a}{{opacity:0}}{b},100%{{opacity:1}}}}")

    def count(n, at, cls="num"):
        """A number that climbs to `n` from `at`, over a second; the value is in
        the markup too, for anything that reads rather than watches."""
        counted[0] += 1
        name = f"cnt{i}_{counted[0]}"
        rules.append(f"@keyframes {name}{{0%,{pct(at, total)}{{--n:0}}{pct(at + 1.0, total)},100%{{--n:{n}}}}}")
        return f'<span class="{cls} count" style="--to:{n};animation-name:{name}" data-n="{n}"><span class="sr">{n}</span></span>'

    if kind == "sort":
        most = max(d["built"], d["authored"], d["captured"], 1)
        rows = [("built by a script", d["built"], "accent"), ("written, with a reason", d["authored"], "ink"),
                ("captured, stamped", d["captured"], "muted")]
        out = []
        for j, (label, n, tone) in enumerate(rows):
            appear(f"bar{i}_{j}", t0 + 0.4 + 0.5 * j, grow=True)
            out.append(f'<div class="row"><span class="lab">{esc(label)}</span>'
                       f'<span class="bar"><i class="t-{tone}" style="--w:{100 * n / most:.1f}%;animation-name:bar{i}_{j}"></i></span>'
                       f'{count(n, t0 + 0.4 + 0.5 * j)}</div>')
        appear(f"left{i}", t0 + 2.6)
        out.append(f'<div class="row left" style="animation-name:left{i}"><span class="lab">unaccounted for</span>'
                   f'<span class="bar none"></span><span class="num t-accent">{d["left"]}</span></div>')
        return f'<div class="viz sort">{"".join(out)}</div>'
    if kind == "hold":
        appear(f"src{i}", t0 + 0.3)
        chips = []
        for j, p in enumerate(d["shown"]):
            appear(f"pg{i}_{j}", t0 + 1.0 + 0.25 * j)
            chips.append(f'<span class="chip" style="animation-name:pg{i}_{j}">{esc(p)}</span>')
        more = d["pages"] - len(d["shown"])
        if more > 0:
            appear(f"pgm{i}", t0 + 1.0 + 0.25 * len(d["shown"]))
            chips.append(f'<span class="chip t-muted" style="animation-name:pgm{i}">+{more} more</span>')
        return (f'<div class="viz hold"><div class="card src" style="animation-name:src{i}">'
                f'<span class="lab">the source</span><span class="val">{esc(d["source"])}</span>'
                f'<span class="num">{count(d["facts"], t0 + 0.4)} facts</span></div>'
                f'<div class="arrow">→</div><div class="chips">{"".join(chips)}</div></div>')
    if kind == "compare":
        cards = []
        for j, p in enumerate(d["places"]):
            appear(f"pl{i}_{j}", t0 + 0.3 + 0.3 * j)
            cards.append(f'<div class="card" style="animation-name:pl{i}_{j}"><span class="lab">a place</span>'
                         f'<span class="val">{esc(p)}/</span></div>')
        appear(f"st{i}", t0 + 1.4)
        appear(f"dis{i}", t0 + 2.6)
        tone = "fail" if d["disagree"] else "accent"
        says = "".join(f'<span class="chip t-fail">{esc(s)}</span>' for s in d.get("says", []))
        return (f'<div class="viz compare"><div class="places">{"".join(cards)}</div>'
                f'<div class="card tally" style="animation-name:st{i}">{count(d["stated"], t0 + 1.4, "num big")}'
                f'<span class="lab">values stated, {d["files"]} pages</span></div>'
                f'<div class="card tally t-{tone}" style="animation-name:dis{i}">{count(d["disagree"], t0 + 2.6, "num big")}'
                f'<span class="lab">disagree</span>{says}</div></div>')
    if kind == "handover":
        out = []
        for j, step in enumerate(d["steps"]):
            appear(f"hs{i}_{j}", t0 + 0.4 + 0.7 * j)
            out.append(f'<div class="step" style="animation-name:hs{i}_{j}"><span class="dot"></span><span class="lab">{esc(step)}</span></div>')
        return f'<div class="viz handover">{"".join(out)}</div>'
    raise ValueError(kind)


def page(board, css_rel, icon_rel):
    """One self-contained page: the clip, playing and looping; `html.still`
    with `--t` set pauses it at that second (the renderer's way in)."""
    total = board["duration"]
    rules, body = [], []
    for i, sc in enumerate(board["scenes"]):
        name = f"w{i}"
        rules.append(window(name, sc["start"], sc["end"], total, rise=sc["kind"] == "mechanism"))
        inner = ""
        if sc["kind"] == "open":
            # THE ONE FLOURISH: the wordmark sets itself, a letter at a time,
            # then the version chip stamps in, the way a build goes green.
            letters = staggered("set", i, list(sc["name"]), sc["start"] + 0.3, 0.06, total, rules, cls="l")
            t1 = sc["start"] + 0.3 + 0.06 * len(sc["name"]) + 0.4
            rules.append(f"@keyframes stamp{i}{{0%,{pct(t1, total)}{{opacity:0;transform:scale(1.2)}}"
                         f"{pct(t1 + 0.25, total)},100%{{opacity:1;transform:none}}}}")
            inner = (f'<div class="mark" aria-label="{esc(sc["name"])}">{"".join(letters)}</div>'
                     f'<div class="ver" style="animation-name:stamp{i}">{esc(sc["version"])}</div>')
        elif sc["kind"] == "ask":
            inner = f'<div class="eye">{esc(sc["eyebrow"])}</div><div class="big">{esc(sc["headline"])}</div>'
        elif sc["kind"] == "run":
            # The command typed a line at a time (a long one broken with the
            # shell's backslash), a moment's work shown as three dots, then
            # what it printed, a line at a time.
            parts = typed_lines(sc["typed"])
            t0, lines = sc["start"] + 0.5, []
            for k, part in enumerate(parts):
                n = len(part)
                t1 = t0 + n * TYPE_SECONDS
                rules.append(f"@keyframes type{i}_{k}{{0%,{pct(t0, total)}{{width:0}}{pct(t1, total)},100%{{width:{n}ch}}}}")
                prompt = '<span class="prompt">$ </span>' if k == 0 else '<span class="prompt">&gt; </span>'
                lines.append(f'<code class="ln"><span class="pr">{prompt}</span><span class="typed" style="animation-name:type{i}_{k};'
                             f'animation-timing-function:steps({n})">{esc(part)}</span></code>')
                t0 = t1 + 0.2
            if sc["lines"]:
                # A moment's work: three dots, one after another, on the clip's
                # own clock, so a rendered frame shows them too.
                t_work = t0
                t_out = t_work + WORKING_SECONDS
                rules.append(f"@keyframes work{i}{{0%,{pct(t_work, total)}{{opacity:0}}{pct(t_work + 0.05, total)}{{opacity:1}}"
                             f"{pct(t_out, total)}{{opacity:1}}{pct(t_out + 0.05, total)},100%{{opacity:0}}}}")
                dots = staggered("dot", i, ["", "", ""], t_work + 0.05, 0.25, total, rules, cls="d", tag="i")
                lines.append(f'<code class="ln work" style="animation-name:work{i}">{"".join(dots)}</code>')
                for j, l in enumerate(sc["lines"]):
                    at = t_out + 0.45 * j
                    rules.append(f"@keyframes line{i}_{j}{{0%,{pct(at, total)}{{opacity:0}}{pct(at + 0.15, total)},100%{{opacity:1}}}}")
                    hi = " hi" if j == len(sc["lines"]) - 1 else ""
                    lines.append(f'<code class="ln out{hi}" style="animation-name:line{i}_{j}">{esc(l)}</code>')
            inner = f'<pre class="term">{"".join(lines)}</pre>'
        elif sc["kind"] == "more":
            inner = f'<div class="eye">{esc(sc["eyebrow"])}</div><div class="claim">{esc(sc["text"])}</div>'
        elif sc["kind"] == "mechanism":
            inner = (f'<div class="eye">{esc(sc["eyebrow"])}</div>{picture_html(sc, i, total, rules)}'
                     f'<p class="mech-cap">{esc(sc["caption"])}</p>')
        elif sc["kind"] == "claim":
            inner = f'<div class="claim">{" ".join(staggered("wd", i, sc["text"].split(), sc["start"] + 0.3, 0.08, total, rules))}</div>'
        elif sc["kind"] == "close":
            parts = [f'<img class="icon" src="{esc(icon_rel)}" alt="">',
                     f'<div class="home">{esc(sc["home"])}</div>',
                     f'<div class="tag">{esc(sc["tagline"])}</div>',
                     f'<div class="install">{esc(sc["install"])}</div><div class="url">{esc(sc["url"])}</div>']
            close = staggered("cl", i, [""] * len(parts), sc["start"] + 0.3, 0.4, total, rules, tag="div")
            inner = "".join(c.replace('></div>', f'>{p}</div>') for c, p in zip(close, parts))
        body.append(f'<div class="scene {sc["kind"]}" style="animation-name:{name}">{inner}</div>')
    style = STYLE.replace("@@D@@", str(total)) + "".join(rules)
    title = f"{board['name']} · {board['version']}"
    return (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{esc(title)}</title><meta name="robots" content="noindex"><link rel="stylesheet" href="{esc(css_rel)}">'
            f'<style>{style}</style></head>\n'
            f'<body><div class="frame" data-duration="{total}">{"".join(body)}</div></body></html>\n')


# Every colour and face is the brand's custom property, from site/brand.css;
# nothing here states one (checks/one_palette.py reads site/).
STYLE = """:root{--t:0;--d:@@D@@s}
@property --n{syntax:'<integer>';inherits:true;initial-value:0}
html,body{margin:0;height:100%;overflow:hidden;background:var(--ground);color:var(--ink)}
.frame{position:relative;width:100%;height:100%;container-type:size;font-family:var(--font-body)}
.scene{position:absolute;inset:0;padding:8cqmin 9cqmin;display:flex;flex-direction:column;justify-content:center;gap:3cqmin;opacity:0;animation:var(--d) linear infinite;animation-delay:calc(var(--t) * -1s)}
.scene>*{max-width:120cqmin}
.typed,.ln.out,.ln.work,.work i,.mark .l,.ver,.claim .w,.close .w,.viz .row.left,.viz .bar i,.viz .card,.viz .chip,.viz .step,.viz .count{animation:var(--d) linear infinite;animation-delay:calc(var(--t) * -1s)}
html.still .scene,html.still .typed,html.still .ln.out,html.still .ln.work,html.still .mark .l,html.still .ver,html.still .claim .w,html.still .close .w,html.still .viz .row.left,html.still .viz .bar i,html.still .viz .card,html.still .viz .chip,html.still .viz .step,html.still .viz .count,html.still .work i{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.scene,.typed,.ln.out,.ln.work,.work i,.mark .l,.ver,.claim .w,.close .w,.viz .row.left,.viz .bar i,.viz .card,.viz .chip,.viz .step,.viz .count,.work i{animation:none}.scene{opacity:0}.scene.claim,.mark .l,.ver,.claim .w,.close .w,.viz .row.left,.viz .card,.viz .chip,.viz .step{opacity:1}.viz .bar i{width:var(--w)}.viz .count{--n:var(--to)}}
.mark{font:400 17cqmin/1 var(--font-display);letter-spacing:-0.02em}
.mark .l,.claim .w,.close .w,.ln.out,.ln.work{opacity:0}
.ver{font:500 4cqmin/1 var(--font-mono);color:var(--on-accent);background:var(--accent);padding:1.6cqmin 2.6cqmin;border-radius:999px;align-self:flex-start;opacity:0}
.eye{font:500 3.3cqmin/1.3 var(--font-mono);letter-spacing:0.06em;text-transform:uppercase;color:var(--muted)}
.big{font:400 11.5cqmin/1.05 var(--font-display);text-wrap:balance}
.term{margin:0;font:400 4.2cqmin/1.6 var(--font-mono);background:var(--surface);border:1px solid var(--line);border-radius:3cqmin;padding:4cqmin;display:grid;gap:1.2cqmin;white-space:normal}
.term .ln{display:block;font:400 4.2cqmin/1.6 var(--font-mono);white-space:pre-wrap;overflow-wrap:anywhere}
.term .ln.hi{color:var(--accent)}
.term .pr{color:var(--muted)}
.typed{display:inline-block;white-space:nowrap;overflow:hidden;vertical-align:bottom;width:0;border-right:0.5cqmin solid var(--accent)}
.term .ln.work{height:1.6em;display:flex;align-items:center;gap:1.2cqmin}
.work i{display:block;width:1.4cqmin;height:1.4cqmin;border-radius:50%;background:var(--muted);opacity:0}
.claim{font:400 9.5cqmin/1.1 var(--font-display);text-wrap:balance}
.close .icon{width:14cqmin;height:14cqmin;display:block;margin-bottom:2cqmin}
.home{font:400 12cqmin/1 var(--font-display);letter-spacing:-0.02em}
.tag{font:italic 400 5.2cqmin/1.2 var(--font-display);color:var(--muted)}
.install{font:400 3.8cqmin/1.6 var(--font-mono)}
.url{font:400 3.6cqmin/1.5 var(--font-mono);color:var(--muted)}
.mech-cap{margin:0;font:400 3.4cqmin/1.45 var(--font-body);color:var(--muted);max-width:120cqmin}
.viz{display:grid;gap:2.2cqmin;width:100%;max-width:120cqmin}
.viz .row{display:grid;grid-template-columns:36cqmin 1fr 10cqmin;gap:2cqmin;align-items:center;font:400 3.2cqmin/1.3 var(--font-mono)}
.viz .row.left{opacity:0}
.viz .row.left .lab{color:var(--ink)}
.viz .row.left .num{font-size:5.5cqmin;line-height:1}
.viz .lab{color:var(--muted)}
.viz .num{text-align:right;font-variant-numeric:tabular-nums}
.viz .count::after{counter-reset:n var(--n);content:counter(n)}
.viz .count .sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.viz .bar{display:block;height:3.2cqmin;background:var(--surface);border:1px solid var(--line);border-radius:999px;overflow:hidden}
.viz .bar.none{background:none;border:0}
.viz .bar i{display:block;height:100%;width:0}
.viz .t-accent{background:var(--accent)}.viz .bar .t-ink{background:var(--ink)}.viz .bar .t-muted{background:var(--muted)}
.viz span.t-accent,.viz .card.t-accent .num{background:none;color:var(--accent)}
.viz .card{opacity:0;display:grid;gap:0.8cqmin;padding:3cqmin;border:1px solid var(--line);border-radius:3cqmin;background:var(--surface);font:400 3.2cqmin/1.3 var(--font-mono)}
.viz .card .val{font:400 4.2cqmin/1.2 var(--font-display);color:var(--ink)}
.viz .card .num.big{font:400 10cqmin/1 var(--font-display);text-align:left}
.viz .card.t-fail .num{color:var(--fail)}
.viz.hold{grid-template-columns:auto auto 1fr;align-items:center}
.viz .arrow{font:400 6cqmin/1 var(--font-display);color:var(--muted)}
.viz .chips{display:flex;flex-wrap:wrap;gap:1.4cqmin}
.viz .chip{opacity:0;font:400 2.8cqmin/1.2 var(--font-mono);padding:1.2cqmin 2cqmin;border:1px solid var(--line);border-radius:999px;color:var(--ink)}
.viz .chip.t-muted{color:var(--muted)}.viz .chip.t-fail{color:var(--fail)}
.viz.compare .places{display:flex;gap:2cqmin;flex-wrap:wrap}
.viz.handover{grid-template-columns:repeat(4,1fr);gap:2cqmin}
.viz .step{opacity:0;display:grid;gap:1.6cqmin;justify-items:start;font:400 3cqmin/1.3 var(--font-mono)}
.viz .step .dot{width:4cqmin;height:4cqmin;border-radius:50%;background:var(--accent)}
.viz .step .lab{color:var(--ink)}
"""


def main():
    boards = storyboards()
    for b in boards:
        d = OUT / b["id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(page(b, os.path.relpath(CSS, d), os.path.relpath(ICON, d)), encoding="utf-8")
        j = BOARDS / b["id"]
        j.mkdir(parents=True, exist_ok=True)
        (j / "storyboard.json").write_text(json.dumps(b, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote site/motion/ and motion/: {len(boards)} clips, each a page in motion, played by the frame it is shown in")


if __name__ == "__main__":
    main()
