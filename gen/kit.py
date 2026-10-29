"""What every generator here shares: the two sources, and how a page starts.

facts/company.json is what the company says; brand/tokens.json is how it
looks. A generator reads both through here, so no two read them differently,
and the brand reaches a page only through site/brand.css - the custom
properties brand.py writes from the tokens - never as a value typed into a
generator or a stylesheet (checks/one_palette.py).
"""
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
FACTS = json.loads((ROOT / "facts/company.json").read_text(encoding="utf-8"))
TOKENS = json.loads((ROOT / "brand/tokens.json").read_text(encoding="utf-8"))
STATUSES = ("draft", "launched")


def esc(text):
    return html.escape(text, quote=True)


def status():
    """site.status, refused unless it is one this site knows how to show."""
    s = FACTS["site"]["status"]
    if s not in STATUSES:
        raise SystemExit(f"site.status is {s!r}: it is one of {', '.join(STATUSES)}")
    return s


def banner():
    """The draft banner, on every page of a draft; nothing once launched."""
    if status() != "draft":
        return ""
    return (f'<div class="draft" role="note"><span class="draft-mark">Draft</span> '
            f'{esc(FACTS["site"]["draft_banner"])}</div>\n')


def head(title, description, css):
    """A page's <head> lines: its title, the draft's noindex, the brand."""
    lines = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        f"<title>{esc(title)}</title>",
        f'<meta name="description" content="{esc(description)}">',
        '<meta name="color-scheme" content="dark">',
    ]
    if status() == "draft":
        lines.append('<meta name="robots" content="noindex, nofollow">')
    lines.append(f'<link rel="stylesheet" href="{css}">')
    return "\n".join(lines)


def luminance(hex_value):
    """WCAG relative luminance of a #RRGGBB colour."""
    h = hex_value.lstrip("#")
    if len(h) != 6:
        raise SystemExit(f"{hex_value!r} is not a #RRGGBB colour")
    def channel(c):
        c = int(c, 16) / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(h[i:i + 2]) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    """WCAG contrast ratio between two #RRGGBB colours, 1 to 21."""
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)
