#!/usr/bin/env python3
"""The questions beside "Why Wherefore" turn by themselves, and stop on the one a thumb picks.

The chips under the definition - feature page, demo video, deck - are radio
buttons and their labels, and when nobody has picked one they turn on a timer:
each question stands for a few seconds, a bar crossing its chip, then flips to
the next (gen/site.py, flipping()). Nothing in the page's bytes says a timer
runs, or stops when a chip is tapped, and checks/controls_press.py presses with
motion reduced, where nothing turns. So this watches, at 390 by 844 with touch,
with motion allowed, and fails:

  - questions that do not turn by themselves: the question shown does not
    change within two turns;
  - a tap that does not stop them: after the first chip is tapped - the one
    the turning started on, the hardest to see stop - the question shown is
    not that chip's, or changes again;

and, with motion reduced:

  - questions that turn anyway.

WHAT IT CANNOT SEE: whether the flip looks good. That is a person's to judge,
on the preview.

Needs Playwright and its Chromium (requirements-browser.txt).

Usage:  python3 checks/questions_turn.py
"""
import functools
import http.server
import pathlib
import sys
import threading

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PHONE = {"width": 390, "height": 844}
TURN = 7            # seconds a question stands: gen/site.py FLIP

# The text of the question showing now: the panel that is visible and opaque.
SHOWING = """() => {
  for (const p of document.querySelectorAll('.ask-panel')) {
    const s = getComputedStyle(p);
    if (s.visibility === 'visible' && parseFloat(s.opacity) > 0.5) return p.innerText.split('\\n')[0].trim();
  }
  return null;
}"""


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def watch(page, seconds, every=0.25):
    seen = []
    for _ in range(int(seconds / every)):
        page.wait_for_timeout(int(every * 1000))
        now = page.evaluate(SHOWING)
        if not seen or seen[-1] != now:
            seen.append(now)
    return seen


def faults(browser, url):
    found = []
    ctx = browser.new_context(viewport=PHONE, is_mobile=True, has_touch=True, reduced_motion="no-preference")
    try:
        page = ctx.new_page()
        page.goto(url, wait_until="load")
        page.locator(".asks").scroll_into_view_if_needed()
        turned = watch(page, 2 * TURN + 1)
        if len([q for q in turned if q]) < 2:
            found.append(f"the questions did not turn by themselves in {2 * TURN + 1} seconds: "
                         f"only {turned} showed")
        first = page.locator('label[for="ask-0"]')
        first.tap()
        want = page.evaluate("() => document.querySelector('.ask-panel-0').innerText.split('\\n')[0].trim()")
        after = watch(page, TURN + 2)
        if after != [want]:
            found.append(f"tapping the first chip did not stop the questions on its own: after the tap "
                         f"{after} showed, and only {want!r} should have")
    finally:
        ctx.close()
    ctx = browser.new_context(viewport=PHONE, is_mobile=True, has_touch=True, reduced_motion="reduce")
    try:
        page = ctx.new_page()
        page.goto(url, wait_until="load")
        still = watch(page, TURN + 2)
        if len(still) > 1:
            found.append(f"with motion reduced, the questions turned anyway: {still}")
    finally:
        ctx.close()
    return found


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("::error::checks/questions_turn.py needs Playwright: "
              "pip install -r requirements-browser.txt && python3 -m playwright install chromium")
        return 1
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(SITE)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            # The questions live on the home page, under Why Wherefore, beside the word they answer.
            found = faults(browser, f"http://127.0.0.1:{server.server_port}/")
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    if found:
        print("::error::the questions do not turn, or do not stop, the way a visitor expects:\n")
        for f in found:
            print(f"   {f}")
        return 1
    print(f"ok   the questions turn by themselves every {TURN} seconds, stop on the chip a thumb taps, "
          f"and hold still for a visitor who asks for less motion")
    return 0


if __name__ == "__main__":
    sys.exit(main())
