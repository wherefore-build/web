#!/usr/bin/env python3
"""The clips, rendered: each feature's page in motion stepped frame by frame into video.

THE PAGE IS THE CLIP; this is the camera. gen/motion.py writes a page per
feature whose motion is CSS and which, marked `still` with `--t` set, stands
at that second. This opens each page in a browser at the frame's size -
portrait 1080x1920, landscape 1920x1080 - sets `--t` to each frame's time,
screenshots it, and has ffmpeg join the frames: a silent, captioned clip of
the length the storyboard says, the same every time it is rendered from the
same page. A poster, the claim scene's middle frame, comes with it.

NOT A GENERATOR. The clips are not committed: an encoder's bytes are not
stable across versions, and a page the site serves plays the same motion.
The clips workflow (.github/workflows/clips.yml) renders them on request
and keeps them as the run's artifacts, and puts them on the engine's
release when it has a token that may.

    python3 gen/motion_render.py                     every feature, into clips/
    python3 gen/motion_render.py gate scan --out X   named features

Needs: playwright (pip install -r requirements-browser.txt; python3 -m playwright install chromium) and ffmpeg.
"""
import argparse
import functools
import http.server
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import threading

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BOARDS = ROOT / "motion"
FRAMES = {"portrait": (1080, 1920), "landscape": (1920, 1080)}
FPS = 24


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def render(browser, url, board, frame, out, fps):
    w, h = FRAMES[frame]
    n = int(round(board["duration"] * fps))
    frames = pathlib.Path(tempfile.mkdtemp(prefix="wherefore-frames-"))
    try:
        pg = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        pg.goto(f"{url}motion/{board['id']}/index.html", wait_until="load")
        pg.evaluate("document.documentElement.classList.add('still')")
        pg.evaluate("document.fonts.ready")
        for i in range(n):
            pg.evaluate("t => document.documentElement.style.setProperty('--t', t)", round(i / fps, 4))
            pg.screenshot(path=str(frames / f"{i:05d}.jpg"), type="jpeg", quality=88)
        poster = None
        if frame == "portrait":
            claim = next(s for s in board["scenes"] if s["kind"] == "claim")
            pg.evaluate("t => document.documentElement.style.setProperty('--t', t)", (claim["start"] + claim["end"]) / 2)
            poster = out / f"{board['id']}.png"
            pg.screenshot(path=str(poster), type="png")
        pg.close()
        clip = out / f"{board['id']}-{frame}.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(fps), "-i", str(frames / "%05d.jpg"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", str(clip)],
                       check=True)
        return clip, n, poster
    finally:
        shutil.rmtree(frames, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("ids", nargs="*", help="features to render; none means every one")
    ap.add_argument("--out", default="clips", help="where the clips go (default clips/)")
    ap.add_argument("--fps", type=int, default=FPS)
    a = ap.parse_args(argv)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("::error::playwright is not installed: pip install -r requirements-browser.txt && python3 -m playwright install chromium")
        return 1
    boards = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(BOARDS.glob("*/storyboard.json"))]
    if a.ids:
        unknown = sorted(set(a.ids) - {b["id"] for b in boards})
        if unknown:
            print(f"::error::no clip for {', '.join(unknown)}: the build writes one per feature")
            return 1
        boards = [b for b in boards if b["id"] in a.ids]
    out = pathlib.Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(SITE)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            url = f"http://127.0.0.1:{server.server_port}/"
            for b in boards:
                said = []
                for frame in FRAMES:
                    _clip, n, _poster = render(browser, url, b, frame, out, a.fps)
                    said.append(f"{frame} {n} frames")
                print(f"  {b['id']:<12} {b['duration']:>4.1f} s  {', '.join(said)}")
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print(f"wrote {out}: {len(boards)} feature{'s' if len(boards) != 1 else ''}, two clips and a poster each")
    return 0


if __name__ == "__main__":
    sys.exit(main())
