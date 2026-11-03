#!/usr/bin/env python3
"""The pendulum's model stands beside the case study's heading, and turns under a thumb.

The case study's heading has the pendulum's own interactive model beside it:
a copy of the file its home page embeds, in a frame (gen/site.py). Nothing in
the page's bytes says the model draws, sits where it should at a phone's
width, or does anything when touched - and the company's first client learned,
by thumb, that a control can pass every check and still do nothing when
pressed. So this does what the thumb does, on the site served with the headers
site/_headers gives it.

It fails:

  - a script on the site's own page: the frame is the one place one may run;
  - a frame allowed more than its script (`sandbox` other than `allow-scripts`),
    which would let the model reach the page around it;
  - headers that let a script run anywhere but the model's path, or give the
    model's path no policy of its own;

and, at 390 by 844 with touch, and at 1280 by 900:

  - a frame that is not to the right of the heading, beside it rather than
    below it, and on the screen;
  - a model that draws nothing within a few seconds: inside the frame,
    nothing unlike its commonest colour;
  - a model that stands on a ground other than the one its frame names - the
    brand colour case.model.ground says;
  - a model that does not turn when dragged - by touch on the phone, by a
    mouse on the desktop - with motion reduced, so the swing cannot be
    mistaken for the turn.

WHAT IT CANNOT SEE: Cloudflare's own reading of site/_headers. This reads it
the way Cloudflare documents it - every rule whose path matches adds its
headers, and `! Name` takes off what an earlier rule set - and serves the site
that way; the preview is where the real one can be seen.

Needs Playwright and its Chromium (requirements-browser.txt).

Usage:  python3 checks/model_turns.py
"""
import base64
import functools
import html.parser
import http.server
import pathlib
import re
import sys
import threading
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PHONE = {"width": 390, "height": 844}
DESK = {"width": 1280, "height": 900}
DRAWN = 0.01        # of the frame's pixels, at least, unlike its commonest colour
TURNED = 0.02       # of the frame's pixels, at least, changed by a drag

# Fraction of pixels in picture `a` unlike its commonest colour - a blank frame,
# of any colour, draws nothing - or, with `b`, that differ between the two.
MEASURE = """async ([a, b]) => {
  const load = src => new Promise((ok, no) => { const i = new Image(); i.onload = () => ok(i); i.onerror = no; i.src = src; });
  const px = async src => { const i = await load(src), c = document.createElement('canvas');
    c.width = i.width; c.height = i.height; const g = c.getContext('2d'); g.drawImage(i, 0, 0);
    return g.getImageData(0, 0, i.width, i.height).data; };
  const A = await px(a), B = b ? await px(b) : null;
  let ref = null;
  if (!B) {
    const count = new Map();
    for (let k = 0; k < A.length; k += 4) {
      const key = (A[k] >> 4) << 8 | (A[k + 1] >> 4) << 4 | (A[k + 2] >> 4);
      count.set(key, (count.get(key) || 0) + 1);
    }
    const top = [...count.entries()].sort((x, y) => y[1] - x[1])[0][0];
    ref = [(top >> 8 & 15) * 16 + 8, (top >> 4 & 15) * 16 + 8, (top & 15) * 16 + 8];
  }
  let n = 0;
  for (let k = 0; k < A.length; k += 4) {
    const r = B ? [B[k], B[k + 1], B[k + 2]] : ref;
    if (Math.abs(A[k] - r[0]) + Math.abs(A[k + 1] - r[1]) + Math.abs(A[k + 2] - r[2]) > 48) n++;
  }
  return B ? n / (A.length / 4) : [n / (A.length / 4), ref];
}"""


def rules():
    """[(path pattern, [(name, value or None to take off)])] from site/_headers."""
    out, rule = [], None
    for line in (SITE / "_headers").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        if not line[0].isspace():
            rule = (line.strip(), [])
            out.append(rule)
        elif line.strip().startswith("!"):
            rule[1].append((line.strip()[1:].strip().lower(), None))
        else:
            name, _, value = line.strip().partition(":")
            rule[1].append((name.strip().lower(), value.strip()))
    return out


def served(path, table):
    """{header: [values]} for a request to `path`, as Cloudflare documents reading _headers."""
    got = {}
    for pattern, headers in table:
        if re.fullmatch(re.escape(pattern).replace(r"\*", ".*"), path):
            for name, value in headers:
                if value is None:
                    got.pop(name, None)
                else:
                    got.setdefault(name, []).append(value)
    return got


class Frames(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.frames, self.scripts = [], 0

    def handle_starttag(self, tag, attrs):
        if tag == "iframe":
            self.frames.append(dict(attrs))
        elif tag == "script":
            self.scripts += 1


def static_faults():
    found = []
    page = Frames()
    page.feed((SITE / "index.html").read_text(encoding="utf-8"))
    if page.scripts:
        found.append(f"site/index.html has {page.scripts} <script>: the page runs none; only the "
                     f"pendulum's frame may")
    if len(page.frames) != 1:
        found.append(f"site/index.html has {len(page.frames)} frames; the case study has one, the model")
        return found, None
    frame = page.frames[0]
    if (frame.get("sandbox") or "").split() != ["allow-scripts"]:
        found.append(f"the model's frame is sandboxed {frame.get('sandbox')!r}: it may run its script and "
                     f"nothing else - `allow-scripts`, alone")
    src = urllib.parse.urlsplit(frame.get("src", ""))
    model = "/" + src.path.lstrip("/")
    table = rules()
    for path in ("/", "/index.html", "/brand/", "/page.css", model, model + "index.html"):
        policies = served(path, table).get("content-security-policy", [])
        if len(policies) != 1:
            found.append(f"{path} is served {len(policies)} policies; it needs exactly one")
            continue
        scripts = "script-src" in policies[0]
        if path.startswith(model) and not scripts:
            found.append(f"{path} is the model, and its policy lets no script run: it would draw nothing")
        if not path.startswith(model) and scripts:
            found.append(f"{path} is served a policy that lets a script run: only the model's path may")
        if path.startswith(model) and "frame-ancestors 'self'" not in policies[0]:
            found.append(f"{path} may be framed by other sites: its policy needs frame-ancestors 'self'")
    return found, (frame, table)


class Served(http.server.SimpleHTTPRequestHandler):
    table = []

    def end_headers(self):
        for name, values in served(urllib.parse.urlsplit(self.path).path, self.table).items():
            for v in values:
                self.send_header(name, v)
        super().end_headers()

    def log_message(self, *args):
        pass


def serve(table):
    handler = functools.partial(type("H", (Served,), {"table": table}), directory=str(SITE))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def look(browser, base, ground, name, viewport, touch):
    """What is wrong with the model at this size, or None."""
    ctx = browser.new_context(viewport=viewport, is_mobile=touch, has_touch=touch, reduced_motion="reduce")
    try:
        page = ctx.new_page()
        page.goto(base, wait_until="load")
        heading = page.locator("#case h2")
        heading.scroll_into_view_if_needed()
        frame = page.locator("#case iframe")
        frame.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        h, f = heading.bounding_box(), frame.bounding_box()
        if not f or f["width"] < 60 or f["height"] < 60:
            return f"at {name}, the model's frame is not shown, or too small to touch: {f}"
        if f["x"] < h["x"] + h["width"] - 1:
            return (f"at {name}, the model is not to the right of the heading: the heading ends at "
                    f"{h['x'] + h['width']:.0f} px and the model starts at {f['x']:.0f}")
        if f["y"] >= h["y"] + h["height"]:
            return f"at {name}, the model is below the heading, not beside it"
        if f["x"] + f["width"] > viewport["width"] + 1:
            return f"at {name}, the model runs off the right of the screen"
        # The inside of the frame only: its rounded corners show the page's own ground.
        inside = {"x": f["x"] + f["width"] * 0.1, "y": f["y"] + f["height"] * 0.1,
                  "width": f["width"] * 0.8, "height": f["height"] * 0.8}

        def picture():
            return "data:image/png;base64," + base64.b64encode(page.screenshot(clip=inside)).decode()

        judge = browser.new_page()
        drawn, stands = 0.0, None
        for _ in range(30):
            page.wait_for_timeout(500)
            drawn, stands = judge.evaluate(MEASURE, [picture(), None])
            if drawn >= DRAWN:
                break
        if drawn < DRAWN:
            judge.close()
            return f"at {name}, the model drew nothing in 15 seconds: {drawn:.2%} of its frame is unlike its ground"
        want = [int(ground[k:k + 2], 16) for k in (0, 2, 4)]
        if any(abs(a - b) > 12 for a, b in zip(stands, want)):
            judge.close()
            return (f"at {name}, the model stands on rgb{tuple(stands)}, not the ground its frame names, "
                    f"#{ground}")
        page.wait_for_timeout(1500)
        before = picture()
        y = f["y"] + f["height"] * 0.85
        x0, x1 = f["x"] + f["width"] * 0.2, f["x"] + f["width"] * 0.8
        steps = 12
        if touch:
            cdp = ctx.new_cdp_session(page)
            cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x0, "y": y}]})
            for i in range(1, steps + 1):
                cdp.send("Input.dispatchTouchEvent",
                         {"type": "touchMove", "touchPoints": [{"x": x0 + (x1 - x0) * i / steps, "y": y}]})
                page.wait_for_timeout(16)
            cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
        else:
            page.mouse.move(x0, y)
            page.mouse.down()
            for i in range(1, steps + 1):
                page.mouse.move(x0 + (x1 - x0) * i / steps, y)
                page.wait_for_timeout(16)
            page.mouse.up()
        page.wait_for_timeout(800)
        moved_to = frame.bounding_box()
        if abs(moved_to["y"] - f["y"]) > 1 or abs(moved_to["x"] - f["x"]) > 1:
            judge.close()
            how = "a thumb" if touch else "a mouse"
            return f"at {name}, dragging {how} across the model moved the page, not the model"
        after = picture()
        moved = judge.evaluate(MEASURE, [before, after])
        judge.close()
        if moved < TURNED:
            how = "a thumb" if touch else "a mouse"
            return f"at {name}, the model did not turn when {how} dragged across it: {moved:.2%} of it changed"
        return None
    finally:
        ctx.close()


def main():
    found, seen = static_faults()
    if seen is not None:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("::error::checks/model_turns.py needs Playwright: "
                  "pip install -r requirements-browser.txt && python3 -m playwright install chromium")
            return 1
        frame, table = seen
        ground = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(frame["src"]).query)).get("bg", "")
        if not re.fullmatch(r"[0-9A-Fa-f]{6}", ground):
            found.append(f"the model's frame names no ground it can be told apart from: {frame['src']!r}")
        else:
            server = serve(table)
            base = f"http://127.0.0.1:{server.server_port}/"
            with sync_playwright() as p:
                browser = p.chromium.launch()
                for name, viewport, touch in ((f"{PHONE['width']} px", PHONE, True),
                                              (f"{DESK['width']} px", DESK, False)):
                    fault = look(browser, base, ground, name, viewport, touch)
                    if fault:
                        found.append(fault)
                browser.close()
            server.shutdown()
    if found:
        print("::error::the pendulum's model is not where it should be, or does not turn:\n")
        for f in found:
            print(f"   {f}")
        return 1
    print(f"ok   the pendulum's model stands to the right of the case study's heading, draws, and turns "
          f"under a thumb at {PHONE['width']} px and a mouse at {DESK['width']} px; the page runs no "
          f"script, and only the model's frame may")
    return 0


if __name__ == "__main__":
    sys.exit(main())
