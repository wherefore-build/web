"""The clip as one SVG that plays wherever an image is shown: the issue it answered, a README, a post.

A CLIP IS A PAGE (gen/motion.py), and a page needs a frame. GitHub shows an
image in a comment but plays no page and no video it does not host, so the
same storyboard is drawn a second way here: an SVG whose motion is SMIL, the
animation that is part of the SVG itself, which a browser plays inside an
<img> with scripts off and nothing loaded from outside. The brand's faces
travel inside the file, as base64, the way the icon carries its own
(gen/brand.py): a reader on GitHub sees the serif and the mono, not whatever
their machine has. The colours are the tokens' values, read here and written
out, as brand.py writes them into brand.css; nothing is typed.

The engine's inbox (corpus/inbox.py in wherefore-build/wherefore) embeds this
file on the issue a feature answered, linking the clip page, so the person
who asked sees what shipped play where they asked for it. Every word, number
and second is the storyboard's: what the page says, this says, in the same
order and at the same time, and checks/motion_reads.py holds that the poster
carries every word the page does.

Writes site/motion/<id>/poster.svg, 1600 by 900, looping.
"""
import base64
import re

from kit import ROOT, TOKENS, colours, esc

W, H = 1600, 900
PAD = 120                 # the margin on every side
COL = W - 2 * PAD         # the column everything sits in
MONO_ADVANCE = 0.6        # the mono face's advance width, in ems: a line's width is exact without measuring
TYPED_LINE = 28           # as gen/motion.py breaks a typed command
OUT_LINE = 50             # characters of a printed line before it wraps, at the terminal's size
FADE = 0.3


def faces():
    """The three faces a poster sets, each as an @font-face carrying its file."""
    want = [("display", "normal"), ("display", "italic"), ("mono", "normal")]
    rules = []
    for role, style in want:
        face = TOKENS["type"][role]
        f = next(x for x in face["faces"] if x["style"] == style and x["weight"] == 400)
        data = base64.b64encode((ROOT / "brand/fonts" / f["file"]).read_bytes()).decode("ascii")
        rules.append(f'@font-face{{font-family:"{face["family"]}";font-style:{style};font-weight:400;'
                     f'src:url(data:font/woff2;base64,{data}) format("woff2")}}')
    return "".join(rules)


def family(role):
    face = TOKENS["type"][role]
    return esc(f'{face["family"]}, {face["fallback"]}')


def wrap(text, limit):
    """Words into lines of at most `limit` characters; a word longer than the limit is its own line."""
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > limit:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        lines.append(cur)
    return lines


def typed_lines(typed):
    ws, lines, cur = typed.split(), [], ""
    for w in ws:
        if cur and len(cur) + 1 + len(w) + 2 > TYPED_LINE:
            lines.append(cur + " \\")
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    lines.append(cur)
    return lines


# ── time ────────────────────────────────────────────────────────────────────

def _k(t, total):
    return f"{max(0.0, min(1.0, t / total)):.5f}"


def animate(attr, points, total, extra=""):
    """One SMIL animation over the whole clip, looping with it: `points` are
    (second, value) in time order; the value holds between them."""
    pts = [(0.0, points[0][1])] + [p for p in points if 0.0 < p[0] < total] + [(total, points[-1][1])]
    values = ";".join(str(v) for _, v in pts)
    times = ";".join(_k(t, total) for t, _ in pts)
    return f'<animate attributeName="{attr}" values="{values}" keyTimes="{times}" dur="{total}s" repeatCount="indefinite"{extra}/>'


def window(start, end, total, fade_in=FADE, fade_out=FADE):
    """A scene's opacity: in at `start`, out at `end`."""
    fade_in, fade_out = max(fade_in, 0.02), max(fade_out, 0.02)
    a, b = start + fade_in, max(start + fade_in, end - fade_out)
    return animate("opacity", [(0, 0), (start, 0), (a, 1), (b, 1), (end, 0)], total)


def arrive(at, total, over=0.25, attr="opacity"):
    """An element's opacity: nothing until `at`, then in over `over` seconds, then held."""
    return animate(attr, [(0, 0), (at, 0), (at + over, 1)], total)


def grow(at, to, total, over=0.35):
    return animate("width", [(0, 0), (at, 0), (at + over, to)], total)


# ── text ────────────────────────────────────────────────────────────────────

def mono(x, y, text, size, fill, anchor="start", extra=""):
    """A mono line whose width is pinned to the face's advance, so the layout
    holds even where the face did not load."""
    n = len(text)
    width = round(n * size * MONO_ADVANCE, 1)
    pos = f'x="{x}"' if anchor == "start" else f'x="{x}" text-anchor="{anchor}"'
    return (f'<text {pos} y="{y}" font-family="{family("mono")}" font-size="{size}" fill="{fill}" '
            f'textLength="{width}" lengthAdjust="spacingAndGlyphs" xml:space="preserve"{extra}>{esc(text)}</text>')


def serif(x, y, text, size, fill, italic=False, extra=""):
    style = ' font-style="italic"' if italic else ""
    return f'<text x="{x}" y="{y}" font-family="{family("display")}" font-size="{size}" fill="{fill}"{style}{extra}>{esc(text)}</text>'


def staggered_words(x, y, lines, size, fill, t0, step, total, italic=False):
    """Lines of serif text whose words arrive one after another, `step` apart from `t0`."""
    out, j = [], 0
    for li, line in enumerate(lines):
        spans = []
        for w in line.split():
            spans.append(f'<tspan fill-opacity="0">{esc(w)}{arrive(t0 + step * j, total, attr="fill-opacity")}</tspan>')
            j += 1
        style = ' font-style="italic"' if italic else ""
        out.append(f'<text x="{x}" y="{y + li * size * 1.1:.1f}" font-family="{family("display")}" font-size="{size}" '
                   f'fill="{fill}"{style} xml:space="preserve">{" ".join(spans)}</text>')
    return "".join(out)


# ── the scenes ──────────────────────────────────────────────────────────────

def scene_open(sc, total, c):
    size = 190
    letters = []
    for j, ch in enumerate(sc["name"]):
        letters.append(f'<tspan fill-opacity="0">{esc(ch)}{arrive(sc["start"] + 0.3 + 0.06 * j, total, attr="fill-opacity")}</tspan>')
    t1 = sc["start"] + 0.3 + 0.06 * len(sc["name"]) + 0.4
    ver = sc["version"]
    vw = round(len(ver) * 40 * MONO_ADVANCE + 56, 1)
    y = H / 2 + 20
    return (f'<text x="{PAD}" y="{y}" font-family="{family("display")}" font-size="{size}" fill="{c["ink"]}" '
            f'letter-spacing="-3">{"".join(letters)}</text>'
            f'<g opacity="0">{arrive(t1, total)}'
            f'<rect x="{PAD}" y="{y + 50}" width="{vw}" height="72" rx="36" fill="{c["accent"]}"/>'
            f'{mono(PAD + vw / 2, y + 98, ver, 40, c["on-accent"], anchor="middle")}</g>')


def scene_ask(sc, total, c):
    lines = wrap(sc["headline"], 26)
    size = 118 if len(lines) <= 2 else 96
    block = 50 + 40 + len(lines) * size * 1.05
    y = (H - block) / 2 + 30
    out = [mono(PAD, y, sc["eyebrow"], 30, c["muted"], extra=' letter-spacing="2"')]
    for li, line in enumerate(lines):
        out.append(serif(PAD, y + 40 + (li + 1) * size * 1.05 - size * 0.12, line, size, c["ink"]))
    return "".join(out)


def scene_run(sc, total, c):
    size, lh = 40, 64
    typed = typed_lines(sc["typed"])
    printed = [(w, j == len(sc["lines"]) - 1) for j, l in enumerate(sc["lines"]) for w in wrap(l, OUT_LINE)]
    rows = len(typed) + (1 + len(printed) if sc["lines"] else 0)
    inner = 48
    bh = inner * 2 + rows * lh
    bw = COL
    by = (H - bh) / 2
    x0 = PAD + inner
    out = [f'<rect x="{PAD}" y="{by:.1f}" width="{bw}" height="{bh}" rx="28" fill="{c["surface"]}" stroke="{c["line"]}"/>']
    t0 = sc["start"] + 0.5
    y = by + inner + size
    cid = 0
    for k, part in enumerate(typed):
        prompt = "$ " if k == 0 else "> "
        n = len(part)
        t1 = t0 + n * 0.055
        pw = round(len(prompt) * size * MONO_ADVANCE, 1)
        tw = round(n * size * MONO_ADVANCE, 1)
        cid += 1
        out.append(f'<clipPath id="t{cid}"><rect x="{x0 + pw}" y="{y - size:.1f}" width="0" height="{lh}">'
                   f'{animate("width", [(0, 0), (t0, 0), (t1, tw)], total)}</rect></clipPath>')
        out.append(mono(x0, y, prompt, size, c["muted"]))
        out.append(f'<g clip-path="url(#t{cid})">{mono(x0 + pw, y, part, size, c["ink"])}</g>')
        t0 = t1 + 0.2
        y += lh
    if sc["lines"]:
        t_work, t_out = t0, t0 + 0.9
        dots = "".join(f'<circle cx="{x0 + 12 + 30 * j}" cy="{y - size * 0.35:.1f}" r="8" fill="{c["muted"]}" opacity="0">'
                       f'{arrive(t_work + 0.05 + 0.25 * j, total)}</circle>' for j in range(3))
        out.append(f'<g opacity="0">{animate("opacity", [(0, 0), (t_work, 0), (t_work + 0.05, 1), (t_out, 1), (t_out + 0.05, 0)], total)}{dots}</g>')
        y += lh
        for j, (line, last) in enumerate(printed):
            out.append(f'<g opacity="0">{arrive(t_out + 0.45 * j, total, over=0.15)}'
                       f'{mono(x0, y, line, size, c["accent"] if last else c["ink"])}</g>')
            y += lh
    return "".join(out)


def scene_more(sc, total, c):
    lines = wrap(sc["text"], 30)
    size = 92
    block = 70 + len(lines) * size * 1.1
    y = (H - block) / 2 + 30
    out = [mono(PAD, y, sc["eyebrow"], 30, c["muted"], extra=' letter-spacing="2"')]
    for li, line in enumerate(lines):
        out.append(serif(PAD, y + 70 + li * size * 1.1 + size * 0.75, line, size, c["ink"]))
    return "".join(out)


def picture(sc, total, c):
    """The mechanism scene's picture, in the column from y=0; returns (svg, height)."""
    kind, d, t0 = sc["mechanism"], sc["data"], sc["start"]
    out = []
    if kind == "sort":
        most = max(d["built"], d["authored"], d["captured"], 1)
        rows = [("built by a script", d["built"], c["accent"]), ("written, with a reason", d["authored"], c["ink"]),
                ("captured, stamped", d["captured"], c["muted"])]
        bx, bw, rh = PAD + 520, 600, 64
        for j, (label, n, tone) in enumerate(rows):
            y = j * rh
            at = t0 + 0.4 + 0.5 * j
            out.append(mono(PAD, y + 40, label, 30, c["muted"]))
            out.append(f'<rect x="{bx}" y="{y + 14}" width="{bw}" height="36" rx="18" fill="{c["surface"]}" stroke="{c["line"]}"/>')
            out.append(f'<rect x="{bx}" y="{y + 14}" width="0" height="36" rx="18" fill="{tone}">{grow(at, round(bw * n / most, 1), total)}</rect>')
            out.append(f'<g opacity="0">{arrive(at, total)}{mono(PAD + COL, y + 42, str(n), 34, c["ink"], anchor="end")}</g>')
        y = 3 * rh
        out.append(f'<g opacity="0">{arrive(t0 + 2.6, total)}{mono(PAD, y + 44, "unaccounted for", 30, c["ink"])}'
                   f'{mono(PAD + COL, y + 48, str(d["left"]), 56, c["accent"], anchor="end")}</g>')
        return "".join(out), 4 * rh + 10
    if kind == "hold":
        cw, ch = 440, 190
        out.append(f'<g opacity="0">{arrive(t0 + 0.3, total)}'
                   f'<rect x="{PAD}" y="0" width="{cw}" height="{ch}" rx="28" fill="{c["surface"]}" stroke="{c["line"]}"/>'
                   f'{mono(PAD + 32, 52, "the source", 26, c["muted"])}'
                   f'{serif(PAD + 32, 108, d["source"], 44, c["ink"])}'
                   f'<g opacity="0">{arrive(t0 + 0.4, total)}{mono(PAD + 32, 158, str(d["facts"]) + " facts", 30, c["ink"])}</g></g>')
        out.append(serif(PAD + cw + 36, ch / 2 + 20, "→", 64, c["muted"]))
        x, y, size, gap = PAD + cw + 120, 0, 26, 14
        xmax = PAD + COL
        shown = list(d["shown"])
        more = d["pages"] - len(shown)
        chips = [(p, c["ink"]) for p in shown] + ([(f"+{more} more", c["muted"])] if more > 0 else [])
        rows = 1
        for j, (label, tone) in enumerate(chips):
            w = round(len(label) * size * MONO_ADVANCE + 40, 1)
            if x + w > xmax:
                x, y = PAD + cw + 120, y + 56
                rows += 1
            out.append(f'<g opacity="0">{arrive(t0 + 1.0 + 0.25 * j, total)}'
                       f'<rect x="{x}" y="{y}" width="{w}" height="44" rx="22" fill="none" stroke="{c["line"]}"/>'
                       f'{mono(x + 20, y + 31, label, size, tone)}</g>')
            x += w + gap
        return "".join(out), max(ch, y + 44)
    if kind == "compare":
        x, pw, ph = PAD, 300, 150
        for j, p in enumerate(d["places"]):
            out.append(f'<g opacity="0">{arrive(t0 + 0.3 + 0.3 * j, total)}'
                       f'<rect x="{x}" y="0" width="{pw}" height="{ph}" rx="28" fill="{c["surface"]}" stroke="{c["line"]}"/>'
                       f'{mono(x + 28, 50, "a place", 26, c["muted"])}{serif(x + 28, 112, p + "/", 48, c["ink"])}</g>')
            x += pw + 24
        tw, th, ty = 460, 250, ph + 30
        tone = c["fail"] if d["disagree"] else c["accent"]
        out.append(f'<g opacity="0">{arrive(t0 + 1.4, total)}'
                   f'<rect x="{PAD}" y="{ty}" width="{tw}" height="{th}" rx="28" fill="{c["surface"]}" stroke="{c["line"]}"/>'
                   f'{serif(PAD + 32, ty + 140, str(d["stated"]), 130, c["ink"])}'
                   f'{mono(PAD + 32, ty + 200, "values stated, " + str(d["files"]) + " pages", 26, c["muted"])}</g>')
        says = "".join(mono(PAD + tw + 64, ty + 236, s, 24, c["fail"]) for s in d.get("says", [])[:1])
        out.append(f'<g opacity="0">{arrive(t0 + 2.6, total)}'
                   f'<rect x="{PAD + tw + 32}" y="{ty}" width="{tw}" height="{th}" rx="28" fill="{c["surface"]}" stroke="{c["line"]}"/>'
                   f'{serif(PAD + tw + 64, ty + 140, str(d["disagree"]), 130, tone)}'
                   f'{mono(PAD + tw + 64, ty + 200, "disagree", 26, c["muted"])}{says}</g>')
        return "".join(out), ty + th
    if kind == "handover":
        step_w = COL / 4
        for j, step in enumerate(d["steps"]):
            x = PAD + j * step_w
            out.append(f'<g opacity="0">{arrive(t0 + 0.4 + 0.7 * j, total)}'
                       f'<circle cx="{x + 22}" cy="22" r="22" fill="{c["accent"]}"/>')
            for li, line in enumerate(wrap(step, 18)):
                out.append(mono(x, 92 + li * 38, line, 28, c["ink"]))
            out.append("</g>")
        return "".join(out), 92 + 38 * 2
    raise ValueError(kind)


def scene_mechanism(sc, total, c):
    pic, ph = picture(sc, total, c)
    cap = wrap(sc["caption"], 78)
    block = 40 + 48 + ph + 40 + len(cap) * 42
    y = max(60, (H - block) / 2)
    out = [mono(PAD, y, sc["eyebrow"], 30, c["muted"], extra=' letter-spacing="2"'),
           f'<g transform="translate(0 {y + 48:.1f})">{pic}</g>']
    for li, line in enumerate(cap):
        out.append(mono(PAD, y + 48 + ph + 40 + 30 + li * 42, line, 28, c["muted"]))
    return "".join(out)


def scene_claim(sc, total, c):
    lines = wrap(sc["text"], 28)
    size = 104 if len(lines) <= 2 else 88
    y = (H - len(lines) * size * 1.1) / 2 + size * 0.8
    return staggered_words(PAD, y, lines, size, c["ink"], sc["start"] + 0.3, 0.08, total)


def scene_close(sc, total, c):
    t0 = sc["start"] + 0.3
    icon = TOKENS["icon"]
    y = 170
    parts = [
        serif(PAD + 40, y + 120, icon["glyph"], 150, c["accent"], italic=True, extra=' text-anchor="middle"'),
        serif(PAD, y + 300, sc["home"], 150, c["ink"], extra=' letter-spacing="-3"'),
        serif(PAD, y + 380, sc["tagline"], 60, c["muted"], italic=True),
        mono(PAD, y + 470, sc["install"], 40, c["ink"]),
        mono(PAD, y + 530, sc["url"], 34, c["muted"]),
    ]
    return "".join(f'<g opacity="0">{arrive(t0 + 0.4 * j, total)}{p}</g>' for j, p in enumerate(parts))


DRAW = {"open": scene_open, "ask": scene_ask, "run": scene_run, "more": scene_more,
        "mechanism": scene_mechanism, "claim": scene_claim, "close": scene_close}


def poster(board):
    """The clip as one looping SVG, every scene in its window."""
    c = colours()
    total = board["duration"]
    scenes = []
    for sc in board["scenes"]:
        scenes.append(f'<g opacity="0">{window(sc["start"], sc["end"], total)}{DRAW[sc["kind"]](sc, total, c)}</g>')
    title = f"{board['name']} · {board['version']}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n'
            f'<title>{esc(title)}</title>\n'
            f'<desc>{esc(board["name"])}, in motion: {total} seconds, looping. The same clip plays at '
            f'https://wherefore.build/motion/{esc(board["id"])}/</desc>\n'
            f'<style>{faces()}</style>\n'
            f'<rect width="{W}" height="{H}" fill="{c["ground"]}"/>\n'
            + "\n".join(scenes) + "\n</svg>\n")


def words_in(svg):
    """The text a poster shows, for a check that reads it: tags and animation out."""
    return re.sub(r"<[^>]+>", " ", re.sub(r"<style>.*?</style>", " ", svg, flags=re.S))
