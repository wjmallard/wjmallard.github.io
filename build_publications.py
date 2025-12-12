#!/usr/bin/env python3
"""Generate publications.html from publications.md (the single source of truth).

No third-party dependencies. Mirrors build_portfolio.py: the chip bar, the jump
nav, and the entries are all derived from one file, so they cannot drift.

Two things this page does that Google Scholar structurally cannot:
  * bold my name in a full author list, and
  * say where in that list it falls (first author vs. #14 of 18).

Run:  python3 build_publications.py   (or ./build.sh)
"""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "publications.md"
OUT = ROOT / "publications.html"

META_KEYS = ("authors", "venue", "year", "detail", "doi", "era", "themes",
             "slug", "role", "page", "link", "note")

# Author lists longer than this are elided down to: first three, me, and the
# senior author. The full list stays in publications.md.
MAX_AUTHORS = 12
LEAD_AUTHORS = 3

ELLIPSIS = "&hellip;"


# ---------------------------------------------------------------------------
# Inline rendering: `code` and [text](url) — same grammar as build_portfolio.py
# ---------------------------------------------------------------------------

def inline(text: str) -> str:
    spans: list[str] = []

    def stash(m: re.Match) -> str:
        spans.append(m.group(1))
        return f"\x00{len(spans) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)
    text = esc(text)  # escape + em-dash; code spans are stashed, so they stay literal
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"\x00(\d+)\x00",
                  lambda m: f"<code>{html.escape(spans[int(m.group(1))], quote=False)}</code>",
                  text)
    return text


def esc(text: str) -> str:
    # Escape for HTML, then render the author's "--" as a real em-dash. The
    # replace must follow html.escape, or the '&' would itself become '&amp;'.
    return html.escape(text, quote=False).replace("--", "&mdash;")


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


# ---------------------------------------------------------------------------
# Parse publications.md
# ---------------------------------------------------------------------------

def parse(src: str):
    cfg = {"subtitle": "", "scholar": "", "me": ""}
    metrics: list[tuple[str, str]] = []   # (label, value)
    themes: list[tuple[str, str]] = []    # (key, label)
    eras: list[tuple[str, str]] = []      # (key, label)
    sections: list[dict] = []
    cur_sec: dict | None = None
    cur_pub: dict | None = None

    def flush_pub():
        nonlocal cur_pub
        if cur_pub is not None:
            cur_sec["pubs"].append(cur_pub)
        cur_pub = None

    for raw in src.splitlines():
        s = raw.strip()
        if not s or s.startswith("# "):
            continue
        if s.startswith("@subtitle:"):
            cfg["subtitle"] = s[len("@subtitle:"):].strip()
            continue
        if s.startswith("@scholar:"):
            cfg["scholar"] = s[len("@scholar:"):].strip()
            continue
        if s.startswith("@me:"):
            cfg["me"] = s[len("@me:"):].strip()
            continue
        if s.startswith("@metric:"):
            lbl, _, val = s[len("@metric:"):].partition("|")
            metrics.append((lbl.strip(), val.strip()))
            continue
        if s.startswith("@theme "):
            parts = [p.strip() for p in s[len("@theme "):].split("|")]
            themes.append((parts[0], parts[1]))
            continue
        if s.startswith("@era "):
            parts = [p.strip() for p in s[len("@era "):].split("|")]
            eras.append((parts[0], parts[1]))
            continue
        if s.startswith("## "):
            flush_pub()
            cur_sec = {"name": s[3:].strip(), "pubs": []}
            sections.append(cur_sec)
            continue
        if s.startswith("### "):
            flush_pub()
            cur_pub = {"title": s[4:].strip(), "authors": "", "venue": "", "year": "",
                       "detail": "", "doi": None, "era": None, "themes": [],
                       "slug": None, "role": None, "page": None, "links": [], "note": None}
            continue

        m = re.match(r"(\w+):\s*(.*)$", s)
        if cur_pub is not None and m and m.group(1) in META_KEYS:
            k, v = m.group(1), m.group(2).strip()
            if k == "themes":
                cur_pub["themes"] = [t.strip() for t in v.split(",") if t.strip()]
            elif k == "link":
                lbl, _, url = v.partition("|")
                cur_pub["links"].append((lbl.strip(), url.strip()))
            else:
                cur_pub[k] = v
        elif cur_pub is not None:
            # A wrapped authors: line folds back into the author list.
            cur_pub["authors"] = f'{cur_pub["authors"]} {s}'.strip()

    flush_pub()
    return cfg, metrics, themes, eras, sections


# ---------------------------------------------------------------------------
# Validation — fail loudly on a typo'd key or a missing field
# ---------------------------------------------------------------------------

def validate(cfg, themes, eras, sections):
    keys = {k for k, _ in themes}
    era_keys = {k for k, _ in eras}
    seen_slugs: dict[str, str] = {}
    for sec in sections:
        for p in sec["pubs"]:
            for field in ("authors", "venue", "year"):
                if not p[field]:
                    raise SystemExit(f"error: {p['title']!r} is missing '{field}:'")
            if not p["year"].isdigit():
                raise SystemExit(f"error: {p['title']!r} has a non-numeric year {p['year']!r}")
            for t in p["themes"]:
                if t not in keys:
                    raise SystemExit(f"error: {p['title']!r} uses unknown theme '{t}'")
            if p["era"] and p["era"] not in era_keys:
                raise SystemExit(f"error: {p['title']!r} uses unknown era '{p['era']}'")
            if p["page"] and not (ROOT / "projects" / p["page"] / "index.md").exists():
                raise SystemExit(
                    f"error: {p['title']!r} links to page {p['page']!r}, "
                    f"but projects/{p['page']}/index.md does not exist"
                )
            sid = p["slug"] or slug(p["title"])
            if sid in seen_slugs:
                raise SystemExit(
                    f"error: {p['title']!r} and {seen_slugs[sid]!r} "
                    f"both resolve to slug {sid!r}"
                )
            seen_slugs[sid] = p["title"]
            # A silently unbolded author list is the one failure mode that still
            # renders fine, so say so rather than letting it through unnoticed.
            if cfg["me"] and cfg["me"] not in p["authors"] and not p["role"]:
                print(f"  warning: {p['title'][:60]!r} — no '{cfg['me']}' in authors:, "
                      f"and no role: to explain why")


# ---------------------------------------------------------------------------
# Authors: split, bold me, elide the long ones
# ---------------------------------------------------------------------------

def split_authors(authors: str) -> list[str]:
    return [a.strip() for a in authors.split(",") if a.strip()]


def my_index(names: list[str], me: str) -> int | None:
    """0-based position of the @me surname, or None if it isn't in the list."""
    for i, name in enumerate(names):
        if me and re.search(rf"\b{re.escape(me)}\b", name):
            return i
    return None


def render_authors(names: list[str], me: str) -> str:
    mine = my_index(names, me)

    def one(i: int) -> str:
        return f"<strong>{esc(names[i])}</strong>" if i == mine else esc(names[i])

    if len(names) <= MAX_AUTHORS:
        return ", ".join(one(i) for i in range(len(names)))

    # Long list: first three, me, and the senior author — each run of dropped
    # names collapses to one ellipsis.
    keep = set(range(LEAD_AUTHORS)) | {len(names) - 1}
    if mine is not None:
        keep.add(mine)

    parts: list[str] = []
    prev = -1
    for i in sorted(keep):
        if i > prev + 1:
            parts.append(ELLIPSIS)
        parts.append(one(i))
        prev = i
    # Join with commas, but never put a comma directly before an ellipsis.
    out = ""
    for i, part in enumerate(parts):
        if i == 0:
            out = part
        elif part == ELLIPSIS or parts[i - 1] == ELLIPSIS:
            out += f" {part}"
        else:
            out += f", {part}"
    return out


def render_badge(p: dict, names: list[str], me: str) -> str:
    """The author-position line — the thing Scholar can't show."""
    if p["role"]:
        return esc(p["role"])
    mine = my_index(names, me)
    if mine is None:
        return ""
    if names[-1].lower().startswith("et al"):
        return f"Author {mine + 1}"
    if len(names) == 1:
        return "Sole author"
    if mine == 0:
        return "First author"
    if mine == len(names) - 1:
        return "Last author"
    return f"Author {mine + 1} of {len(names)}"


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def render_pub(p: dict, order: list[str], me: str) -> str:
    if p["themes"]:
        ordered = [k for k in order if k in p["themes"]]
        attr = f' data-themes="{" ".join(ordered)}"'
    else:
        attr = ""
    era_attr = f' data-era="{p["era"]}"' if p["era"] else ""

    doi_url = f'https://doi.org/{p["doi"]}' if p["doi"] else None
    title = esc(p["title"])
    h3 = f'<a href="{doi_url}">{title}</a>' if doi_url else title

    names = split_authors(p["authors"])
    venue = f'<em>{esc(p["venue"])}</em>'
    if p["detail"]:
        venue += f' {esc(p["detail"])}'

    sid = p["slug"] or slug(p["title"])
    out = [f'        <div class="pub" id="{sid}"{attr}{era_attr}>',
           f'          <div class="pub-head">',
           f'            <h3>{h3}</h3>',
           f'            <span class="pub-year">{esc(p["year"])}</span>',
           f'          </div>',
           f'          <p class="pub-authors">{render_authors(names, me)}</p>',
           f'          <p class="pub-venue">{venue}</p>',
           f'          <div class="meta">']

    badge = render_badge(p, names, me)
    if badge:
        out.append(f'            <span class="pub-role">{badge}</span>')

    # DOI first: it is the canonical reference for the work. Everything after it
    # is supplementary -- my own write-up, then any code/data links.
    links = []
    if doi_url:
        links.append(("DOI", doi_url))
    if p["page"]:
        links.append(("Write-up", f'projects/{p["page"]}/'))
    links += p["links"]
    if links:
        a = "".join(f'<a href="{u}">{esc(l)}</a>' for l, u in links)
        out.append(f'            <div class="links">{a}</div>')
    # note: is deliberately not emitted -- it is a reminder for whoever edits
    # publications.md next (provenance, name spellings, why a field looks odd),
    # and none of that belongs in the shipped page.

    out.append('          </div>')
    out.append('        </div>')
    return "\n".join(out)


def render_section(sec: dict, order: list[str], me: str) -> str:
    # Newest first; file order breaks ties (sorted() is stable).
    pubs = sorted(sec["pubs"], key=lambda p: -int(p["year"]))
    cards = "\n\n".join(render_pub(p, order, me) for p in pubs)
    sid = slug(sec["name"])
    return (f'    <section class="pub-section" id="{sid}">\n'
            f'      <h2 class="s-head"><span class="s-title">{esc(sec["name"])}</span></h2>\n'
            f'      <div class="section-body">\n\n{cards}\n\n      </div>\n'
            f'    </section>')


def render(cfg, metrics, themes, eras, sections) -> str:
    order = [k for k, _ in themes]
    me = cfg["me"]

    def chip_row(dim, label, items):
        row = [f'        <span class="filters-label">{label}</span>',
               f'        <button class="chip active" data-dim="{dim}" data-val="all">All</button>']
        for k, lab in items:
            row.append(f'        <button class="chip" data-dim="{dim}" data-val="{k}">{esc(lab)}</button>')
        return '      <div class="filter-row">\n' + "\n".join(row) + '\n      </div>'

    chips_html = chip_row("era", "Era", eras) + "\n" + chip_row("skill", "Skill", themes)
    sub_html = f'    <div class="sub">{esc(cfg["subtitle"])}</div>' if cfg["subtitle"] else ""

    # Two independent header bits: the optional @metric row, and the Scholar link.
    # The link stands on its own so it stays prominent with no metrics declared.
    head = []
    if metrics:
        items = "".join(
            f'<span class="metric"><span class="m-val">{esc(v)}</span> '
            f'<span class="m-lab">{esc(l)}</span></span>'
            for l, v in metrics
        )
        credit = f'<span class="m-via">via Google Scholar</span>' if cfg["scholar"] else ""
        head.append(f'    <div class="metrics">{items}{credit}</div>')
    if cfg["scholar"]:
        head.append(f'    <a class="scholar-cta" href="{cfg["scholar"]}">'
                    f'<span class="cta-label">Google Scholar profile</span>'
                    f'<span class="cta-arrow">&#8599;</span></a>')
    metrics_html = "\n".join(head)

    sections_html = "\n\n".join(render_section(sec, order, me) for sec in sections)

    nav_items = "\n".join(
        f'        <li><a href="#{slug(sec["name"])}" data-sec="{slug(sec["name"])}">'
        f'{esc(sec["name"])}</a></li>'
        for sec in sections
    )
    nav_html = ('      <nav class="toc">\n'
                '        <div class="toc-label">Contents</div>\n'
                '        <ul>\n'
                f'{nav_items}\n'
                '        </ul>\n'
                '      </nav>')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Publications</title>
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="style.css">
  <style>
{CSS}  </style>
  <script data-goatcounter="https://stats.wjmallard.net/count"
          async src="//stats.wjmallard.net/count.js"></script>
</head>
<body>
  <div class="wrap">
    <a class="back" href="./">← William Mallard</a>
    <div class="title">Publications</div>
{sub_html}
{metrics_html}

    <div class="filters">
{chips_html}
    </div>

    <div class="filter-status">
      <span class="filter-count"></span>
      <span class="filter-status-text"></span>
      <button class="filter-clear" type="button">show all</button>
    </div>

    <div class="layout">
{nav_html}
      <div class="content">

{sections_html}

      </div>
    </div>

  </div>

  <script>
{JS}  </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Embedded CSS / JS (kept here so the script is self-contained)
# ---------------------------------------------------------------------------

CSS = """\
    html {
      scroll-behavior: smooth;
    }
    .wrap {
      /* Rail geometry lives here so the jump-nav column and anything that has to
         line up with the entry column (the status line) cannot drift apart. Both
         are in rem, not em: em would resolve against each consumer's own
         font-size, and .filter-status sets its own -- which silently shortened
         the indent and left the status line a few px adrift of the entries. */
      --rail: 11rem;
      --rail-gap: 2.5rem;
      max-width: 60em;
      margin: 0 auto;
      padding: 1em 0 14vh;
    }
    .back {
      margin-bottom: 1.25rem;
    }
    .title {
      color: #222;
      font-size: 2.2em;
      font-weight: 600;
      line-height: 1.15;
      margin-bottom: 1rem;
    }
    .sub {
      font-size: 0.85em;
      color: #999;
      margin-bottom: 1.5em;
    }

    /* Scholar-credited metrics line: the one number kept live off-site. */
    .metrics {
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      gap: 0.4em 1.6em;
      margin-bottom: 0.75rem;
      font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 0.8em;
    }
    .metrics .m-val {
      color: #222;
      font-weight: 600;
      font-size: 1.15em;
    }
    .metrics .m-lab {
      color: #999;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 0.85em;
    }
    .metrics .m-via {
      color: #bbb;
      margin-left: auto;
    }

    /* Scholar link: the accent colour and its own line carry it, not a button and
       not weight. The rule sits under the words only, so the out-arrow floats free
       of the underline. */
    .scholar-cta {
      display: inline-flex;
      align-items: baseline;
      gap: 0.35em;
      margin-bottom: 1.5rem;
      font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 0.85em;
      letter-spacing: 0.03em;
      color: #3d5a80;
    }
    .scholar-cta .cta-label {
      border-bottom: 1px solid #c8d5e8;
    }
    .scholar-cta:hover,
    .scholar-cta:focus {
      color: #222;
    }
    .scholar-cta:hover .cta-label,
    .scholar-cta:focus .cta-label {
      border-bottom-color: #222;
    }
    .scholar-cta .cta-arrow {
      font-size: 0.95em;
      line-height: 1;
    }

    /* Filter chips: two rows (era + skill) */
    .filters {
      display: flex;
      flex-direction: column;
      gap: 0.55em;
      padding: 0.85em 1em;
      background: #f4f4f4;
      border: 1px solid #ececec;
      border-radius: 8px;
      margin-bottom: 1rem;
    }
    .filter-row {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.5em;
    }
    .filters-label {
      font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 0.72em;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #999;
      margin-right: 0.3em;
      min-width: 3em;
    }
    .chip {
      font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 0.76em;
      color: #666;
      background: none;
      border: 1px solid #ddd;
      border-radius: 999px;
      padding: 0.3em 0.85em;
      cursor: pointer;
    }
    .chip:hover {
      border-color: #999;
      color: #222;
    }
    .chip.active {
      background: #3d5a80;
      color: #fafafa;
      border-color: #3d5a80;
    }
    /* Always on: carries the entry count. The matched-filter labels and the clear
       button appear only once a filter is active -- on mobile, where the chips
       hide, they are the only filter cue. */
    .filter-status {
      display: flex;
      align-items: baseline;
      flex-wrap: wrap;
      gap: 0.6em;
      /* Indented past the jump-nav rail so it starts at the entry column, not at
         "Contents". */
      margin: 0 0 1rem calc(var(--rail) + var(--rail-gap));
      font-size: 0.85em;
      color: #666;
    }
    .filter-count {
      font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 0.9em;
      letter-spacing: 0.04em;
      color: #999;
    }
    .filter-status-text,
    .filter-clear {
      display: none;
    }
    .filter-status.on .filter-status-text,
    .filter-status.on .filter-clear {
      display: inline;
    }
    .filter-status.on .filter-status-text::before {
      content: "·";
      color: #ccc;
      margin-right: 0.6em;
    }
    .filter-clear {
      font: inherit;
      color: #3d5a80;
      background: none;
      border: none;
      border-bottom: 1px solid currentColor;
      padding: 0;
      cursor: pointer;
    }
    .filter-clear:hover {
      color: #222;
    }

    /* Section body */
    .section-body {
      padding: 0.75em 0 2.25em;
    }

    /* Section jump-nav: left rail on desktop, hidden on mobile */
    .layout {
      display: flex;
      align-items: flex-start;
      gap: var(--rail-gap);
    }
    .toc {
      flex: 0 0 var(--rail);
      /* Flex items default to min-width:auto, which refuses to go narrower than
         the longest unbreakable word -- so a long section name silently widened
         this column past its basis, and hiding sections via the filter changed
         which word was longest, resizing the rail (and with it the entry column)
         on every chip click. min-width:0 makes the basis authoritative. */
      min-width: 0;
      position: sticky;
      top: 2em;
      font-size: 0.9em;
    }
    .toc-label {
      color: #aaa;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 0.85em;
      margin-bottom: 0.8em;
    }
    .toc ul {
      list-style: none;
      margin: 0;
      padding: 0;
      border-left: 1px solid #e6e6e6;
    }
    .toc a {
      display: block;
      /* Belt and braces: with min-width pinned, an over-long name would otherwise
         overhang into the gutter rather than widening the column. */
      overflow-wrap: break-word;
      padding: 0.35em 0 0.35em 1em;
      margin-left: -1px;
      border-left: 1px solid transparent;
      color: #888;
      line-height: 1.3;
      font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }
    .toc a:hover {
      color: #222;
    }
    .toc a.active {
      color: #222;
      border-left-color: #222;
    }
    .content {
      flex: 1 1 auto;
      min-width: 0;
      max-width: 44em;
    }

    .pub-section {
      scroll-margin-top: 1.5em;
    }
    .pub-section .s-head {
      font-weight: normal;
      font-size: 1em;
      display: flex;
      align-items: baseline;
      flex-wrap: wrap;
      gap: 0.2em 0.7em;
      margin: 0 -0.5em;
      padding: 0.25em 0.5em;
      background: #e9eff9;
      border: 1px solid #d5e0f1;
    }
    .pub-section .s-title {
      font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 1.15em;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #000;
    }

    @media (max-width: 720px) {
      .filters,
      .toc {
        display: none;
      }
      .layout {
        display: block;
      }
      .content {
        max-width: none;
      }
      /* No rail to clear once the jump-nav is hidden. */
      .filter-status {
        margin-left: 0;
      }
    }

    .pub {
      padding-bottom: 1em;
      border-bottom: 1px solid #ccc;
      margin-bottom: 1em;
    }
    .pub:last-child,
    .pub.no-divider {
      padding-bottom: 0;
      border-bottom: none;
      margin-bottom: 0;
    }
    .pub-head {
      display: flex;
      align-items: baseline;
      flex-wrap: wrap;
      gap: 0.2em 0.8em;
    }
    .pub h3 {
      color: #222;
      font-size: 1.05em;
      font-weight: 600;
      line-height: 1.35;
      margin: 0 0 0.35em;
      flex: 1 1 20em;
    }
    .pub h3 a {
      color: #222;
    }
    .pub h3 a:hover {
      color: #000;
      text-decoration: underline;
      text-underline-offset: 2px;
      text-decoration-color: #bbb;
    }
    .pub-year {
      margin-left: auto;
      font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 0.78em;
      color: #aaa;
      letter-spacing: 0.03em;
      white-space: nowrap;
    }
    .pub-authors {
      font-size: 0.85em;
      line-height: 1.6;
      color: #666;
      margin: 0 0 0.2em;
    }
    .pub-authors strong {
      color: #222;
      font-weight: 600;
    }
    .pub-venue {
      font-size: 0.85em;
      color: #888;
      margin: 0 0 0.5em;
    }
    .meta {
      display: flex;
      align-items: baseline;
      flex-wrap: wrap;
      gap: 0.2em 1.25em;
      font-size: 0.78em;
      color: #999;
      line-height: 1.9;
    }
    /* The author-position badge — the reason this page exists alongside Scholar. */
    .pub-role {
      font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 0.92em;
      color: #3d5a80;
      letter-spacing: 0.02em;
    }
    .meta .links a {
      color: #444;
      border-bottom: 1px solid #ccc;
    }
    .meta .links a:hover {
      color: #222;
      border-bottom-color: #222;
    }
    .meta .links a:not(:last-child) {
      margin-right: 1.25em;
    }
"""

JS = """\
    // Two-dimensional filter: era (row 1) and skill (row 2), combined with AND.
    // Each row is single-select with its own "All". Sections (and their jump-nav
    // links) left with no visible entry are hidden. An inbound ?era=/?skill=
    // query -- e.g. a link from the Portfolio page -- is applied on load.
    const chips = document.querySelectorAll('.chip');
    const pubs = document.querySelectorAll('.pub');
    const sections = document.querySelectorAll('section.pub-section');
    const navLinks = document.querySelectorAll('.toc a');
    const navLinkFor = id => document.querySelector('.toc a[data-sec="' + id + '"]');
    const statusEl = document.querySelector('.filter-status');
    const statusTextEl = document.querySelector('.filter-status-text');
    const countEl = document.querySelector('.filter-count');
    const chipLabel = (dim, val) => {
      const c = document.querySelector('.chip[data-dim="' + dim + '"][data-val="' + val + '"]');
      return c ? c.textContent : val;
    };

    const active = { era: 'all', skill: 'all' };

    function apply() {
      pubs.forEach(p => {
        const okEra = active.era === 'all' || p.dataset.era === active.era;
        const okSkill = active.skill === 'all'
          || (p.dataset.themes || '').split(' ').includes(active.skill);
        p.style.display = (okEra && okSkill) ? '' : 'none';
      });
      sections.forEach(s => {
        const cards = [...s.querySelectorAll('.pub')];
        const vis = cards.filter(p => p.style.display !== 'none');
        s.style.display = vis.length ? '' : 'none';
        const link = navLinkFor(s.id);
        if (link) link.style.display = vis.length ? '' : 'none';
        // Drop the divider on the last entry still visible in this section.
        cards.forEach(p => p.classList.toggle('no-divider', p === vis[vis.length - 1]));
      });
      // "Showing 29 entries" while everything is visible, "Showing 12 of 29
      // entries" once something is hidden. Counts every entry, not just journal
      // papers: the thesis and the proceedings are in there too.
      const shown = [...pubs].filter(p => p.style.display !== 'none').length;
      const total = pubs.length;
      const noun = total === 1 ? 'entry' : 'entries';
      countEl.textContent = shown === total
        ? `Showing ${total} ${noun}`
        : `Showing ${shown} of ${total} ${noun}`;
      // Reflect the active filter in the status banner (the only cue on mobile).
      const labels = [];
      if (active.era !== 'all') labels.push(chipLabel('era', active.era));
      if (active.skill !== 'all') labels.push(chipLabel('skill', active.skill));
      statusTextEl.textContent = labels.join(' · ');
      statusEl.classList.toggle('on', labels.length > 0);
    }

    function select(dim, val) {
      active[dim] = val;
      chips.forEach(c => {
        if (c.dataset.dim === dim) c.classList.toggle('active', c.dataset.val === val);
      });
      apply();
    }

    chips.forEach(chip => chip.addEventListener('click',
      () => select(chip.dataset.dim, chip.dataset.val)));

    document.querySelector('.filter-clear').addEventListener('click', () => {
      select('era', 'all');
      select('skill', 'all');
    });

    // Apply any ?era=/?skill= filter from the URL on load.
    const params = new URLSearchParams(location.search);
    ['era', 'skill'].forEach(dim => {
      const val = params.get(dim);
      if (val && [...chips].some(c => c.dataset.dim === dim && c.dataset.val === val)) {
        select(dim, val);
      }
    });

    // Scroll-spy: highlight the jump-nav link for the section now in view.
    const spy = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        navLinks.forEach(a => a.classList.remove('active'));
        const link = navLinkFor(entry.target.id);
        if (link) link.classList.add('active');
      });
    }, { rootMargin: '-10% 0px -80% 0px', threshold: 0 });
    sections.forEach(s => spy.observe(s));

    apply();
"""


if __name__ == "__main__":
    cfg, metrics, themes, eras, sections = parse(SRC.read_text(encoding="utf-8"))
    validate(cfg, themes, eras, sections)
    OUT.write_text(render(cfg, metrics, themes, eras, sections), encoding="utf-8")
    n_pubs = sum(len(s["pubs"]) for s in sections)
    print(f"  wrote publications.html —{len(sections)} sections, {n_pubs} publications, "
          f"{len(eras)} eras, {len(themes)} themes")
