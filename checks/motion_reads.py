#!/usr/bin/env python3
"""Every clip reads: the right length, no scene faster than a reader, a command the CLI has, output the engine prints, every word on the page.

A CLIP IS COMPILED FROM FACTS, so what can go wrong is the compiling. This
reads every storyboard the build wrote (motion/<id>/storyboard.json), the
page beside it (site/motion/<id>/index.html) and the poster (poster.svg, the
same clip as one SVG for the places that show an image), and fails:

  TOO SHORT / TOO LONG   a clip under MIN_SECONDS or over MAX_SECONDS
  TOO FAST               a scene asking more words a second than its kind allows
  NOT A COMMAND          the command run is not one the pinned engine's CLI has
  NEVER PRINTED          a printed line is one no release picture or docs example prints
  CLAIM                  the claim is over twelve words, or not a sentence
  DROPPED                the page, or the poster beside it, lacks a word a scene says

Usage:  python3 checks/motion_reads.py
"""
import html
import json
import pathlib
import re
import sys
from importlib.resources import files

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BOARDS = ROOT / "motion"
MIN_SECONDS, MAX_SECONDS = 16.0, 40.0
CLAIM_WORDS = 12
RATE = {"open": 3.0, "ask": 3.0, "run": 3.5, "more": 2.5, "mechanism": 2.5, "claim": 3.0, "close": 3.0}
ELIDED = "…"


def words(t):
    return len(t.split())


def head(usage):
    out = []
    for tok in usage.split():
        if tok.startswith(("[", "-")) or tok.upper() == tok and any(c.isalpha() for c in tok):
            break
        out.append(tok)
    return " ".join(out)


def texts(sc):
    out = [sc[k] for k in ("name", "version", "eyebrow", "headline", "typed", "text", "caption", "home", "tagline", "install", "url") if sc.get(k)]
    return out + sc.get("lines", [])


def poster_text(svg):
    """What a poster shows, as text: its faces and animations out, and a word
    set a letter at a time (the wordmark's tspans) put back together."""
    svg = re.sub(r"<style>.*?</style>", " ", svg, flags=re.S)
    svg = re.sub(r"<animate [^>]*/>|</?tspan[^>]*>", "", svg)
    return re.sub(r"<[^>]+>", " ", svg)


def printed_lines():
    from wherefore import docs
    out = set()
    for r in json.loads((files("wherefore") / "releases.json").read_text(encoding="utf-8"))["releases"]:
        out.update((r.get("shows") or {}).get("output", []))
    for _p, _t, text in docs.pages():
        for _cmd, lines in docs.examples(text):
            out.update(lines)
    return out


def faults():
    found = []
    heads = {head(c["usage"]) for c in json.loads((files("wherefore") / "commands.json").read_text(encoding="utf-8"))["commands"]}
    printed = printed_lines()
    boards = sorted(BOARDS.glob("*/storyboard.json"))
    for path in boards:
        b = json.loads(path.read_text(encoding="utf-8"))
        fid = b["id"]
        page = SITE / "motion" / fid / "index.html"
        text = page.read_text(encoding="utf-8") if page.is_file() else ""
        svg = page.with_name("poster.svg")
        shown = {"page": text, "poster": poster_text(svg.read_text(encoding="utf-8")) if svg.is_file() else ""}
        if b["duration"] < MIN_SECONDS:
            found.append(f"TOO SHORT      {fid} runs {b['duration']} s; a clip says something in {MIN_SECONDS:.0f}")
        if b["duration"] > MAX_SECONDS:
            found.append(f"TOO LONG       {fid} runs {b['duration']} s; a clip is watched to {MAX_SECONDS:.0f}")
        for sc in b["scenes"]:
            n, d = sum(words(t) for t in texts(sc)), sc["end"] - sc["start"]
            rate = RATE.get(sc["kind"], 3.0)
            if d <= 0 or n / d > rate + 1e-9:
                found.append(f"TOO FAST       {fid}/{sc['kind']}: {n} words in {d:.1f} s is more than {rate} a second")
            if sc["kind"] == "run":
                typed = sc["typed"]
                if not any(typed == h or typed.startswith(h + " ") for h in heads):
                    found.append(f"NOT A COMMAND  {fid} runs `{typed}`, which no command's usage begins")
                for line in sc["lines"]:
                    whole = line[:-1] if line.endswith(ELIDED) else line
                    if not any(p == line or p.startswith(whole) for p in printed):
                        found.append(f"NEVER PRINTED  {fid} shows `{line}`, which nothing the engine replays prints")
            if sc["kind"] == "claim" and (words(sc["text"]) > CLAIM_WORDS or not re.search(r"[.!?]$", sc["text"])):
                found.append(f"CLAIM          {fid}: `{sc['text']}` is over {CLAIM_WORDS} words, or not a sentence")
            for t in texts(sc):
                # typed a line at a time, the claim a word at a time: every word must be on the page,
                # as a word - `accounted` inside `unaccounted` does not count
                for w in t.split():
                    lacks = [where for where, body in shown.items()
                             if not re.search(r"(?<![A-Za-z])" + re.escape(html.escape(w)) + r"(?![A-Za-z])", body)]
                    if lacks:
                        found.append(f"DROPPED        {fid}/{sc['kind']}: the {' and the '.join(lacks)} lacks `{w}`")
                        break
    return found, len(boards)


def main():
    found, n = faults()
    for f in found:
        print(f"::error::{f}")
    if found:
        print(f"\n{len(found)} fault(s): a clip must read")
        return 1
    print(f"ok   every one of the {n} clips runs {MIN_SECONDS:.0f} to {MAX_SECONDS:.0f} s, no scene outruns a reader, "
          f"every command run is one the CLI has, every printed line is one the engine prints, and every word is on the page and its poster")
    return 0


if __name__ == "__main__":
    sys.exit(main())
