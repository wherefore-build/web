#!/usr/bin/env python3
"""Every control on the site does something a visitor can see, pressed cold, on a phone.

The demo's steps and the questions' tabs are labels for radio buttons, and the
stylesheet shows what the checked one selects. Nothing in the page's bytes says
whether that works: a selector that stopped matching, a label whose control was
renamed, a step hidden at a phone's width or a panel that opens below the fold
all leave a page the gate, the reach and the link check pass. The company's
first client learned this twice by thumb - a control placed where it could not
be found, then the same control doing nothing when pressed, both after a green
suite. So this does what the thumb did.

For every control on every page in site/ - a `<label>`, a `<button>`, a
`<summary>` - it loads the page fresh at 390 by 844 with touch, presses that
one control, and requires that:

  - the control can be pressed there: it is shown, on the page, and nothing
    covers it;
  - it is big enough for a thumb, 44 by 44 pixels at least;
  - a label presses a control that exists, and selects it;
  - something NEW appears on the screen: a line of text that was not showing
    anywhere before. Text that only vanishes, moves, or appears only out of
    sight is a press that did nothing a visitor saw.

Each press starts from a fresh load, so no control is judged on a page another
control already drove. A label for the control that is already selected is
pressed and measured, but has nothing new to show.

WHAT IT CANNOT SEE: whether what appears is RIGHT - that is the facts' and the
gate's - and a change that is only a colour.

Needs Playwright and its Chromium (requirements-browser.txt).

Usage:  python3 checks/controls_press.py
"""
import collections
import functools
import http.server
import pathlib
import sys
import threading

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PHONE = {"width": 390, "height": 844}
THUMB = 44

CONTROLS = "label, button, summary"

# Every rendered run of text, where it sits on the page, and whether it is on the screen.
SEEN = """() => {
  const out = [], vw = innerWidth, vh = innerHeight;
  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = walk.nextNode(); n; n = walk.nextNode()) {
    const t = n.textContent.replace(/\\s+/g, ' ').trim();
    if (!t || getComputedStyle(n.parentElement).visibility === 'hidden') continue;
    const r = document.createRange(); r.selectNodeContents(n);
    const boxes = [...r.getClientRects()].filter(b => b.width > 0 && b.height > 0);
    if (!boxes.length) continue;
    const onScreen = boxes.some(b => b.bottom > 0 && b.top < vh && b.right > 0 && b.left < vw);
    out.push([t, Math.round(boxes[0].left + scrollX), Math.round(boxes[0].top + scrollY), onScreen]);
  }
  return out;
}"""

LIST = """(sel) => [...document.querySelectorAll(sel)].map(c => ({
  tag: c.tagName.toLowerCase(), for: c.tagName === 'LABEL' ? c.htmlFor : null,
  text: c.innerText.replace(/\\s+/g, ' ').trim()
}))"""


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def serve():
    handler = functools.partial(Quiet, directory=str(SITE))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def press(browser, url, index, control):
    """Load `url` cold, press its `index`th control, and say what is wrong with that."""
    ctx = browser.new_context(viewport=PHONE, is_mobile=True, has_touch=True, reduced_motion="reduce")
    try:
        page = ctx.new_page()
        page.goto(url, wait_until="load")
        handle = page.locator(CONTROLS).nth(index)
        name = f"{control['text']!r}"
        target = None
        if control["tag"] == "label":
            if not control["for"]:
                return f"the label {name} is for nothing: it has no `for`"
            target = page.locator(f'[id="{control["for"]}"]')
            if target.count() == 0:
                return f"the label {name} presses nothing: no control is called {control['for']}"
        was = target.is_checked() if target is not None and target.get_attribute("type") in ("radio", "checkbox") else None
        before = collections.Counter(t[0] for t in page.evaluate(SEEN))
        try:
            handle.tap(timeout=3000)
        except Exception as e:                                    # noqa: BLE001 - Playwright's own reasons
            why = str(e).splitlines()[0]
            return f"{name} cannot be pressed at {PHONE['width']} px: {why}"
        box = handle.bounding_box()
        if box and (box["width"] < THUMB or box["height"] < THUMB):
            return (f"{name} is smaller than a thumb at {PHONE['width']} px: "
                    f"{box['width']:.0f} by {box['height']:.0f}, and it must be {THUMB} by {THUMB} at least")
        if was is not None and not target.is_checked():
            return f"pressing {name} did not select the control it is for, {control['for']}"
        if was:
            return None
        page.wait_for_timeout(100)
        after = page.evaluate(SEEN)
        new = collections.Counter(t[0] for t in after) - before
        if not new:
            return f"pressing {name} at {PHONE['width']} px showed nothing new"
        if not any(t[3] for t in after if t[0] in new):
            return (f"pressing {name} at {PHONE['width']} px changed only what is off the screen, "
                    f"starting {next(iter(new))!r}")
        return None
    finally:
        ctx.close()


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("::error::checks/controls_press.py needs Playwright: "
              "pip install -r requirements-browser.txt && python3 -m playwright install chromium")
        return 1
    server = serve()
    base = f"http://127.0.0.1:{server.server_port}/"
    found, pressed = [], 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for path in sorted(SITE.rglob("*.html")):
            rel = path.relative_to(SITE).as_posix()
            url = base + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)
            ctx = browser.new_context(viewport=PHONE, is_mobile=True, has_touch=True)
            page = ctx.new_page()
            page.goto(url, wait_until="load")
            controls = page.evaluate(LIST, CONTROLS)
            ctx.close()
            for i, c in enumerate(controls):
                fault = press(browser, url, i, c)
                pressed += 1
                if fault:
                    found.append(f"site/{rel}: {fault}")
        browser.close()
    server.shutdown()
    if found:
        print(f"::error::a control on the site does not do what a thumb expects, pressed cold at "
              f"{PHONE['width']} px:\n")
        for f in found:
            print(f"   {f}")
        return 1
    print(f"ok   every control on the site does something a visitor can see, pressed cold at "
          f"{PHONE['width']} px ({pressed} pressed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
