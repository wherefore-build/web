#!/usr/bin/env python3
"""Every clip fits both frames at every scene, and every scene shows its words.

A CLIP IS A PAGE PLAYED IN A FRAME, portrait on a phone and on the feature's
card, landscape on the release. Its words are sized to the frame, so what
can go wrong is a headline that runs off a narrow frame, a terminal that
spills below a short one, or a scene whose window never opens. This pauses
each clip (`html.still`, `--t` set) at the middle of every scene, in a
portrait frame and a landscape one, and fails:

  SPILLS   the page is wider or taller than the frame, or a shown element's
           box leaves it
  BLANK    at a scene's middle nothing of it is visible

The frames are half of 1080x1920 and 1920x1080; every size in a clip is a
share of the frame, so half the frame judges the same layout at half the cost.

Usage:  python3 checks/motion_fits.py
"""
import functools
import http.server
import json
import pathlib
import sys
import threading

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
CLIPS = SITE / "motion"
BOARDS = ROOT / "motion"            # the storyboards, as data, kept out of site/
FRAMES = {"portrait": (540, 960), "landscape": (960, 540)}
SHOWN = """() => {
  const W = innerWidth, H = innerHeight, out = {spill: [], shown: 0};
  if (document.documentElement.scrollWidth > W || document.documentElement.scrollHeight > H)
    out.spill.push(`the page is ${document.documentElement.scrollWidth}x${document.documentElement.scrollHeight} in a ${W}x${H} frame`);
  for (const sc of document.querySelectorAll('.scene')) {
    if (parseFloat(getComputedStyle(sc).opacity) < 0.5) continue;
    for (const el of sc.querySelectorAll('*')) {
      if (!el.textContent.trim()) continue;
      const r = el.getBoundingClientRect();
      if (!r.width || !r.height) continue;
      out.shown += 1;
      if (r.left < 0 || r.top < 0 || r.right > W + 0.5 || r.bottom > H + 0.5)
        out.spill.push(`<${el.tagName.toLowerCase()} class="${el.className}"> "${el.textContent.trim().slice(0, 40)}" at ${Math.round(r.left)},${Math.round(r.top)} to ${Math.round(r.right)},${Math.round(r.bottom)}`);
    }
  }
  return out;
}"""


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def faults(browser, url):
    found = []
    for board_path in sorted(BOARDS.glob("*/storyboard.json")):
        board = json.loads(board_path.read_text(encoding="utf-8"))
        fid = board["id"]
        for frame, (w, h) in FRAMES.items():
            page = browser.new_page(viewport={"width": w, "height": h})
            page.goto(f"{url}motion/{fid}/index.html", wait_until="load")
            page.evaluate("document.documentElement.classList.add('still')")
            page.evaluate("document.fonts.ready")
            for sc in board["scenes"]:
                t = (sc["start"] + sc["end"]) / 2
                page.evaluate("t => document.documentElement.style.setProperty('--t', t)", t)
                got = page.evaluate(SHOWN)
                for s in got["spill"]:
                    found.append(f"SPILLS   {fid} {frame} at {t:.1f} s ({sc['kind']}): {s}")
                if not got["shown"]:
                    found.append(f"BLANK    {fid} {frame} at {t:.1f} s ({sc['kind']}): nothing of the scene is visible")
            page.close()
    return found


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("::error::playwright is not installed: pip install -r requirements-browser.txt && python3 -m playwright install chromium")
        return 1
    if not CLIPS.is_dir() or not BOARDS.is_dir():
        print("::error::site/motion/ or motion/ is not there: the build writes the clips and their storyboards")
        return 1
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(SITE)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            found = faults(browser, f"http://127.0.0.1:{server.server_port}/")
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    n = len(list(BOARDS.glob("*/storyboard.json")))
    if found:
        print("::error::a clip does not fit its frame, or a scene shows nothing:\n")
        for f in found:
            print(f"   {f}")
        return 1
    print(f"ok   every one of the {n} clips fits a portrait frame and a landscape one at the middle of every scene, "
          f"and every scene shows its words")
    return 0


if __name__ == "__main__":
    sys.exit(main())
