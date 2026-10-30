#!/usr/bin/env python3
"""Shoot the icon's PNG from its SVG, for the accounts that take only PNG.

gen/brand.py writes site/brand/icon.svg from brand/tokens.json, with its face
embedded. Drawing that type into pixels takes a browser, and the build does not
run one, so the PNG is captured rather than generated: this opens the SVG in
the pinned browser, at 1024 px square, and writes brand/icon/icon-1024.png.
The gate holds it to what it was shot from - the captured group `icon` in
wherefore.json - and fails it once the SVG moves and it has not been shot again.

Run it after the icon changes, then record the shot:

    python3 brand/shoot_icon.py
    cd gen && python3 brand.py && cd ..
    wherefore gate --restamp icon

and commit the PNG, the regenerated site and wherefore.json together.

Usage:  python3 brand/shoot_icon.py
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
SVG = ROOT / "site/brand/icon.svg"
PNG = ROOT / "brand/icon/icon-1024.png"
SIZE = 1024


def main():
    if not SVG.is_file():
        sys.exit(f"{SVG.relative_to(ROOT)} is not there: run gen/brand.py first")
    PNG.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # The SVG says 512 px square; shot at twice the density, that is SIZE
        # pixels of a vector drawn for them, not 512 scaled up.
        page = browser.new_page(viewport={"width": SIZE // 2, "height": SIZE // 2}, device_scale_factor=2)
        page.goto(SVG.as_uri())
        page.evaluate("document.fonts.ready")
        page.screenshot(path=str(PNG))
        browser.close()
    print(f"shot {PNG.relative_to(ROOT)} from {SVG.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
