#!/usr/bin/env python3
"""Every page fits a phone's width, moving or still, and no icon is bigger than the words it follows.

Two faults every other check passed and a phone found at once:

  - the "leaves the site" icon beside a link outside a button had no size, so
    an SVG filled its line's whole width - 358 px beside 13 px words in the
    footer;
  - a question tipping in through perspective projected wider than its
    column, and with motion allowed the whole home page was laid out 433 px
    wide on a 390 px screen.

checks/controls_press.py presses with motion reduced, and
checks/questions_turn.py asks only that the questions turn, so neither could
see them. This loads every page at 390 by 844 with touch, with motion allowed
and with it reduced, opens "how this page is built" where a page has it, and
watches for two turns of the questions. It fails:

  - a page wider than the screen at any moment it watched;
  - a visible link icon (svg.out) wider than one and a half times the size of
    the words around it.

WHAT IT CANNOT SEE: whether anything looks good. That is a person's to judge,
on the preview.

SIDE BY SIDE (owner, 8 November 2026: "I want much faster deploy"). Each page
is watched in a fresh context of its own, with motion allowed and with it
reduced, several at once: watching is waiting, and twenty-two watches of
fifteen seconds and more, one after another, took eleven minutes. Nothing is
carried from one page to the next - the "how it is built" switch is a
checkbox, kept nowhere - so a page watched alone is the page a visitor loads
cold. AT_ONCE bounds how many, so the animations keep their pace on a CI
runner.

Needs Playwright and its Chromium (requirements-browser.txt).

Usage:  python3 checks/fits_phone.py
"""
import asyncio
import functools
import http.server
import pathlib
import sys
import threading

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PHONE = {"width": 390, "height": 844}
PAGES = ["", "why/", "features/", "changelog/", "map/", "docs/", "docs/start/", "docs/commands/", "docs/configuration/", "docs/checks/", "docs/reporting/"]
WATCH = 15.0        # seconds: two turns of the questions (gen/site.py FLIP, 7 s) and one more
EVERY = 0.25
ICON = 1.5          # how many times its words' size an icon may be
AT_ONCE = 6         # pages watched at the same time

ICONS = """() => [...document.querySelectorAll('svg.out')].flatMap(s => {
  const r = s.getBoundingClientRect();
  if (!r.width || !r.height) return [];
  const words = parseFloat(getComputedStyle(s.parentElement).fontSize);
  return [[Math.round(r.width), Math.round(words), s.parentElement.textContent.trim().slice(0, 40)]];
})"""


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


async def watch(page, path, motion, found):
    widest = 0
    for _ in range(int(WATCH / EVERY)):
        await page.wait_for_timeout(int(EVERY * 1000))
        widest = max(widest, await page.evaluate("document.documentElement.scrollWidth"))
    if widest > PHONE["width"]:
        found.append(f"/{path} is {widest} px wide on a {PHONE['width']} px screen, with motion {motion}")
    for width, words, link in await page.evaluate(ICONS):
        if width > ICON * words:
            found.append(f"/{path}: the icon after \"{link}\" is {width} px wide beside {words} px words, "
                         f"with motion {motion}")


async def one(browser, url, path, motion, room, found):
    """One page, cold, in a context of its own: watched, then watched again with how it is built open."""
    async with room:
        ctx = await browser.new_context(viewport=PHONE, is_mobile=True, has_touch=True, reduced_motion=motion)
        try:
            page = await ctx.new_page()
            await page.goto(url + path, wait_until="load")
            await watch(page, path, motion, found)
            switch = page.locator("label.inspect-switch")
            if await switch.count():
                try:
                    await switch.first.tap(timeout=10000)
                except Exception as e:  # a switch a thumb cannot reach is a fault too, and must not hide the rest
                    found.append(f"/{path}: \"how this page is built\" did not open under a tap, "
                                 f"with motion {motion} ({type(e).__name__})")
                else:
                    await watch(page, path + " with how it is built open", motion, found)
        finally:
            await ctx.close()


async def faults(browser, url):
    found = []
    room = asyncio.Semaphore(AT_ONCE)
    await asyncio.gather(*(one(browser, url, path, motion, room, found)
                           for motion in ("no-preference", "reduce") for path in PAGES))
    return sorted(dict.fromkeys(found))


async def run(url):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        try:
            return await faults(browser, url)
        finally:
            await browser.close()


def main():
    try:
        import playwright.async_api  # noqa: F401
    except ImportError:
        print("::error::checks/fits_phone.py needs Playwright: "
              "pip install -r requirements-browser.txt && python3 -m playwright install chromium")
        return 1
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(SITE)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        found = asyncio.run(run(f"http://127.0.0.1:{server.server_port}/"))
    finally:
        server.shutdown()
        server.server_close()
    if found:
        print("::error::a page does not fit a phone, or an icon outgrows its words:\n")
        for f in found:
            print(f"   {f}")
        return 1
    print(f"ok   every page fits a {PHONE['width']} px phone, moving or still and with how it is built open, "
          f"and no icon is bigger than the words it follows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
