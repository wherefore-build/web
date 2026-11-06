"""Markdown to HTML, the little of it the engine's docs use, with no library.

THE DOCS ARE THE ENGINE'S, read from the release the site pins (`wherefore.docs`),
and they are written in the Markdown the skill is written in: headings,
paragraphs, fenced code, bulleted and numbered lists, inline code, emphasis,
links. This renders exactly that and nothing more, so a page that uses more
is a page this site cannot show yet, and says so by rendering it wrong where
a person looks rather than by swallowing it.

Why no library: the site's generators read only what the corpus pins, and a
Markdown library would be a dependency the gate cannot hold to a release.
"""
import html
import re

INLINE = [
    (re.compile(r"`([^`]+)`"), lambda m: f"<code>{html.escape(m.group(1))}</code>"),
    (re.compile(r"\*\*([^*]+)\*\*"), lambda m: f"<strong>{m.group(1)}</strong>"),
    (re.compile(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])"), lambda m: f"<em>{m.group(1)}</em>"),
    (re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)"), lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>'),
    (re.compile(r"(?<![\"'>])(https?://[^\s<)]+)"), lambda m: f'<a href="{m.group(1)}">{m.group(1)}</a>'),
]


def inline(text):
    """Inline code first, and nothing inside it is read again: a backtick span is kept whole."""
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for part in parts:
        if part.startswith("`") and part.endswith("`") and len(part) > 1:
            out.append(f"<code>{html.escape(part[1:-1])}</code>")
            continue
        s = html.escape(part, quote=False)
        for rx, fn in INLINE[1:]:
            s = rx.sub(fn, s)
        out.append(s)
    return "".join(out)


def render(md, shift=0):
    """HTML for `md`; `shift` moves every heading down that many levels, so a
    page's own `# Title` can sit under the site's h1."""
    out, para, lines = [], [], md.splitlines()
    i = 0

    def flush():
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            flush()
            lang = line[3:].strip()
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            body = html.escape("\n".join(lines[i + 1:j]))
            cls = f' class="lang-{html.escape(lang)}"' if lang else ""
            out.append(f"<pre><code{cls}>{body}</code></pre>")
            i = j + 1
            continue
        m = re.match(r"^(#{1,6}) (.+)$", line)
        if m:
            flush()
            level = min(6, len(m.group(1)) + shift)
            text = m.group(2).strip()
            anchor = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
            out.append(f'<h{level} id="{anchor}">{inline(text)}</h{level}>')
            i += 1
            continue
        m = re.match(r"^(\s*)([-*]|\d+\.) (.*)$", line)
        if m:
            flush()
            ordered = m.group(2)[0].isdigit()
            items = []
            while i < len(lines):
                m2 = re.match(r"^(\s*)([-*]|\d+\.) (.*)$", lines[i])
                if not m2:
                    # a continuation line of the last item: indented, not blank
                    if items and lines[i].startswith("  ") and lines[i].strip():
                        items[-1] += " " + lines[i].strip()
                        i += 1
                        continue
                    break
                items.append(m2.group(3).strip())
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(it)}</li>" for it in items) + f"</{tag}>")
            continue
        if line.startswith("> "):
            flush()
            quote = []
            while i < len(lines) and lines[i].startswith("> "):
                quote.append(lines[i][2:])
                i += 1
            out.append(f"<blockquote><p>{inline(' '.join(quote))}</p></blockquote>")
            continue
        if not line.strip():
            flush()
            i += 1
            continue
        para.append(line.strip())
        i += 1
    flush()
    return "\n".join(out)
