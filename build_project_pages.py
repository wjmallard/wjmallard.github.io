#!/usr/bin/env python3
"""Minimal Markdown -> HTML builder for per-project write-ups.

No third-party dependencies. Each project is a folder under projects/ holding an
index.md (with a small front-matter block) plus its images; this renders the
index.md to a sibling index.html so the whole write-up lives in one place:

    projects/<slug>/index.md   ->   projects/<slug>/index.html
    projects/<slug>/*.png            (images, referenced by bare filename)

The public URL is then /projects/<slug>/. The portfolio.html grid (built
separately by build_portfolio.py) stays the index over these pages.

Front matter (between two --- lines at the very top of the file):

    ---
    title: AlphaFold Contact-Map Clustering
    tagline: AlphaFold ensembles -> binding modes, validated in the lab.
    ---

'title' is required; 'tagline' is optional (rendered as a muted italic line
under the heading).

Supported Markdown mirrors the writing/ builder — headings, paragraphs,
**bold**, *italic*, `code`, [links](url), fenced ``` code blocks, > blockquotes,
- and 1. lists, --- rules — plus images. An image on its own line becomes a
full-width figure with an optional caption drawn from its title text:

    ![alt text](contact-map.png "Caption shown under the image.")
"""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECTS_DIR = ROOT / "projects"

# A line that is nothing but an image -> a block-level <figure>.
IMG_LINE_RE = re.compile(r'^!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)$')
# The same, but found inline within a paragraph (caption ignored there).
IMG_INLINE_RE = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)')


# All shared styling now lives in the site stylesheet (style.css); the per-project
# write-ups add nothing beyond it.


# ---------------------------------------------------------------------------
# Inline markdown: `code`, images, [text](url), **bold**, *italic*
# ---------------------------------------------------------------------------

def render_inline(text: str) -> str:
    # Pull out `code` spans first so their contents are not further processed.
    code_spans: list[str] = []

    def stash_code(m: re.Match) -> str:
        code_spans.append(m.group(1))
        return f"\x00{len(code_spans) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash_code, text)

    text = html.escape(text, quote=False)

    # Images before links: the image syntax is a superset of the link syntax.
    text = IMG_INLINE_RE.sub(
        lambda m: f'<img src="{html.escape(m.group(2), quote=True)}" alt="{m.group(1)}">',
        text,
    )
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                  lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>',
                  text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)([^*]+)\*(?!\*)", r"<em>\1</em>", text)

    def restore_code(m: re.Match) -> str:
        raw = code_spans[int(m.group(1))]
        return f"<code>{html.escape(raw, quote=False)}</code>"

    text = re.sub(r"\x00(\d+)\x00", restore_code, text)
    return text


def render_figure(alt: str, src: str, caption: str | None) -> str:
    parts = [
        "<figure>",
        f'  <img src="{html.escape(src, quote=True)}" alt="{html.escape(alt, quote=True)}">',
    ]
    if caption:
        parts.append(f"  <figcaption>{render_inline(caption)}</figcaption>")
    parts.append("</figure>")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Block markdown
# ---------------------------------------------------------------------------

def render_body(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Blank line
        if not stripped:
            i += 1
            continue

        # HTML comment -> consumed, renders nothing (handy for TODO/scaffold notes)
        if stripped.startswith("<!--"):
            while i < n and "-->" not in lines[i]:
                i += 1
            i += 1  # skip the line carrying the closing -->
            continue

        # Fenced code block
        if stripped.startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(html.escape(lines[i], quote=False))
                i += 1
            i += 1  # skip closing fence
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
            continue

        # Horizontal rule
        if re.fullmatch(r"-{3,}", stripped):
            out.append("<hr>")
            i += 1
            continue

        # Standalone image -> figure
        m = IMG_LINE_RE.match(stripped)
        if m:
            out.append(render_figure(m.group(1), m.group(2), m.group(3)))
            i += 1
            continue

        # Heading
        m = re.match(r"(#{1,6})\s+(.*)", stripped)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{render_inline(m.group(2).strip())}</h{level}>")
            i += 1
            continue

        # Blockquote
        if stripped.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].lstrip())
                i += 1
            out.append("<blockquote>" + render_inline(" ".join(buf)) + "</blockquote>")
            continue

        # Unordered list
        if re.match(r"[-*]\s+", stripped):
            items = _collect_list_items(lines, i, n, r"^[-*]\s+")
            i = items.next_index
            out.append("<ul>" + "".join(f"<li>{render_inline(it)}</li>" for it in items.values) + "</ul>")
            continue

        # Ordered list
        if re.match(r"\d+\.\s+", stripped):
            items = _collect_list_items(lines, i, n, r"^\d+\.\s+")
            i = items.next_index
            out.append("<ol>" + "".join(f"<li>{render_inline(it)}</li>" for it in items.values) + "</ol>")
            continue

        # Paragraph: gather until blank line or a block starter
        buf = []
        while i < n and lines[i].strip() and not _starts_block(lines[i].strip()):
            buf.append(lines[i].strip())
            i += 1
        out.append("<p>" + render_inline(" ".join(buf)) + "</p>")

    return "\n".join(out)


class _ListItems:
    def __init__(self, values: list[str], next_index: int):
        self.values = values
        self.next_index = next_index


def _collect_list_items(lines: list[str], i: int, n: int, marker: str) -> _ListItems:
    """Gather list items of one type, folding lazy continuation lines into the
    preceding item (a wrapped line in the source stays part of that item)."""
    values: list[str] = []
    while i < n:
        s = lines[i].strip()
        if re.match(marker, s):
            values.append(re.sub(marker, "", s))
            i += 1
        elif s and not _starts_block(s):
            values[-1] += " " + s
            i += 1
        else:
            break
    return _ListItems(values, i)


def _starts_block(stripped: str) -> bool:
    return bool(
        stripped.startswith("```")
        or stripped.startswith("<!--")
        or stripped.startswith(">")
        or re.fullmatch(r"-{3,}", stripped)
        or IMG_LINE_RE.match(stripped)
        or re.match(r"#{1,6}\s+", stripped)
        or re.match(r"[-*]\s+", stripped)
        or re.match(r"\d+\.\s+", stripped)
    )


# ---------------------------------------------------------------------------
# Front matter
# ---------------------------------------------------------------------------

def parse_front_matter(raw: str) -> tuple[dict[str, str], str]:
    if not raw.startswith("---"):
        raise ValueError("missing front matter (file must start with '---')")
    parts = raw.split("---", 2)
    if len(parts) < 3:
        raise ValueError("unterminated front matter")
    meta: dict[str, str] = {}
    for fm_line in parts[1].strip().splitlines():
        if ":" in fm_line:
            key, _, val = fm_line.partition(":")
            meta[key.strip()] = val.strip()
    return meta, parts[2].lstrip("\n")


# ---------------------------------------------------------------------------
# Page template
# ---------------------------------------------------------------------------

def project_page(title: str, tagline: str, body_html: str) -> str:
    tagline_html = (f'      <p class="tagline">{html.escape(tagline)}</p>\n'
                    if tagline else "")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} — William Mallard</title>
  <link rel="icon" href="../../favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../../style.css">
  <script data-goatcounter="https://stats.wjmallard.net/count"
          async src="//stats.wjmallard.net/count.js"></script>
</head>
<body>
  <div class="wrap">
    <a class="back" href="../../portfolio.html">← Portfolio</a>
    <article>
      <h1>{html.escape(title)}</h1>
{tagline_html}{_indent(body_html, 6)}
    </article>
  </div>
</body>
</html>
"""


def _indent(text: str, spaces: int) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line else line for line in text.splitlines())


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build() -> None:
    slugs: list[str] = []

    for md_path in sorted(PROJECTS_DIR.glob("*/index.md")):
        slug = md_path.parent.name
        raw = md_path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(raw)
        if "title" not in meta:
            raise ValueError(f"{md_path}: front matter needs 'title'")
        page = project_page(meta["title"], meta.get("tagline", ""), render_body(body))
        (md_path.parent / "index.html").write_text(page, encoding="utf-8")
        slugs.append(slug)
        print(f"  wrote projects/{slug}/index.html")

    print(f"  ({len(slugs)} project page{'s' if len(slugs) != 1 else ''})")


if __name__ == "__main__":
    build()
