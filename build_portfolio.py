#!/usr/bin/env python3
"""Generate portfolio.html from portfolio.md (the single source of truth).

No third-party dependencies. The chip bar and the project sections are both
derived from one file, so they cannot drift.

Run:  python3 build_portfolio.py   (or ./build.sh)
"""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "portfolio.md"
OUT = ROOT / "portfolio.html"

META_KEYS = ("slug", "era", "themes", "tagline", "date", "tech", "repo", "page", "link", "shot", "figure", "note")


# ---------------------------------------------------------------------------
# Inline rendering: `code` and [text](url)
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


def esc_date(text: str) -> str:
    # In a date tag every hyphen is a range separator, so render it as an en-dash
    # ("2012-2013" -> "2012&ndash;2013"). Scoped to date tags, so hyphens elsewhere
    # (tail-core, z-ring, URLs) are untouched. Runs after escape so '&' is intact.
    return html.escape(text, quote=False).replace("-", "&ndash;")


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


# ---------------------------------------------------------------------------
# Parse portfolio.md
# ---------------------------------------------------------------------------

def parse(src: str):
    subtitle = ""
    themes: list[tuple[str, str]] = []   # (key, label)
    eras: list[tuple[str, str]] = []     # (key, label)
    sections: list[dict] = []
    cur_sec: dict | None = None
    cur_proj: dict | None = None
    desc: list[str] = []

    def flush_proj():
        nonlocal cur_proj
        if cur_proj is not None:
            cur_proj["desc"] = " ".join(desc).strip()
            cur_sec["projects"].append(cur_proj)
        cur_proj = None

    for raw in src.splitlines():
        s = raw.strip()
        if not s or s.startswith("# "):
            continue
        if s.startswith("@subtitle:"):
            subtitle = s[len("@subtitle:"):].strip()
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
            flush_proj()
            name = s[3:].partition("|")[0].strip()
            cur_sec = {"name": name, "projects": []}
            sections.append(cur_sec)
            continue
        if s.startswith("### "):
            flush_proj()
            cur_proj = {"title": s[4:].strip(), "slug": None, "era": None, "themes": [],
                        "tagline": "", "date": "", "tech": [], "repo": None,
                        "page": None, "links": [], "shot": None, "figure": None, "note": None}
            desc = []
            continue

        m = re.match(r"(\w+):\s*(.*)$", s)
        if cur_proj is not None and m and m.group(1) in META_KEYS:
            k, v = m.group(1), m.group(2).strip()
            if k == "themes":
                cur_proj["themes"] = [t.strip() for t in v.split(",") if t.strip()]
            elif k == "slug":
                cur_proj["slug"] = v
            elif k == "era":
                cur_proj["era"] = v
            elif k == "tagline":
                cur_proj["tagline"] = v
            elif k == "date":
                cur_proj["date"] = v
            elif k == "tech":
                cur_proj["tech"] = [t.strip() for t in v.split(",") if t.strip()]
            elif k == "repo":
                cur_proj["repo"] = v
            elif k == "page":
                cur_proj["page"] = v
            elif k == "link":
                lbl, _, url = v.partition("|")
                cur_proj["links"].append((lbl.strip(), url.strip()))
            elif k == "shot":
                cur_proj["shot"] = v
            elif k == "figure":
                cur_proj["figure"] = v
            elif k == "note":
                cur_proj["note"] = v
        elif cur_proj is not None:
            desc.append(s)

    flush_proj()
    return subtitle, themes, eras, sections


# ---------------------------------------------------------------------------
# Validation — fail loudly on a typo'd theme key
# ---------------------------------------------------------------------------

def validate(themes, eras, sections):
    keys = {k for k, _ in themes}
    era_keys = {k for k, _ in eras}
    seen_slugs: dict[str, str] = {}
    for sec in sections:
        for p in sec["projects"]:
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


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def render_card(p: dict, order: list[str]) -> str:
    if p["themes"]:
        ordered = [k for k in order if k in p["themes"]]
        attr = f' data-themes="{" ".join(ordered)}"'
    else:
        attr = ""
    era_attr = f' data-era="{p["era"]}"' if p["era"] else ""

    if p["page"]:
        h3 = f'<a href="projects/{p["page"]}/">{esc(p["title"])}</a>'
    elif p["repo"]:
        h3 = f'<a href="{p["repo"]}">{esc(p["title"])}</a>'
    else:
        h3 = inline(p["title"])

    sid = p["slug"] or slug(p["title"])
    out = [f'        <div class="project" id="{sid}"{attr}{era_attr}>',
           f'          <div class="proj-head">',
           f'            <h3>{h3}</h3>']
    if p["date"]:
        out.append(f'            <span class="proj-date">{esc_date(p["date"])}</span>')
    out.append('          </div>')
    out.append(f'          <p class="tagline">{esc(p["tagline"])}</p>')
    if p["shot"]:
        out.append(f'          <img class="shot" src="shots/{p["shot"]}" alt="" '
                   f'onerror="this.style.display=\'none\'">')
    out.append(f'          <p>\n            {inline(p["desc"])}\n          </p>')

    if p["figure"]:
        src, _, alt = p["figure"].partition("|")
        out.append(f'          <img class="proj-figure" src="{esc(src.strip())}" '
                   f'alt="{esc(alt.strip())}" onerror="this.style.display=\'none\'">')

    out.append('          <div class="meta">')
    if p["tech"]:
        spans = "".join(f"<span>{esc(t)}</span>" for t in p["tech"])
        out.append(f'            <div class="tags">{spans}</div>')
    links = ([("Source", p["repo"])] if p["repo"] else []) + p["links"]
    if links:
        a = "".join(f'<a href="{u}">{esc(l)}</a>' for l, u in links)
        out.append(f'            <div class="links">{a}</div>')
    if p["note"]:
        out.append(f'            <!-- {p["note"]} -->')
    out.append('          </div>')
    out.append('        </div>')
    return "\n".join(out)


def render_section(sec: dict, order: list[str]) -> str:
    cards = "\n\n".join(render_card(p, order) for p in sec["projects"])
    sid = slug(sec["name"])
    return (f'    <section class="proj-section" id="{sid}">\n'
            f'      <h2 class="s-head"><span class="s-title">{esc(sec["name"])}</span></h2>\n'
            f'      <div class="section-body">\n\n{cards}\n\n      </div>\n'
            f'    </section>')


def render(subtitle, themes, eras, sections) -> str:
    order = [k for k, _ in themes]

    def chip_row(dim, label, items):
        row = [f'        <span class="filters-label">{label}</span>',
               f'        <button class="chip active" data-dim="{dim}" data-val="all">All</button>']
        for k, lab in items:
            row.append(f'        <button class="chip" data-dim="{dim}" data-val="{k}">{esc(lab)}</button>')
        return '      <div class="filter-row">\n' + "\n".join(row) + '\n      </div>'

    chips_html = chip_row("era", "Era", eras) + "\n" + chip_row("skill", "Skill", themes)
    sub_html = f'    <div class="sub">{esc(subtitle)}</div>' if subtitle else ""

    sections_html = "\n\n".join(render_section(sec, order) for sec in sections)

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
  <title>Portfolio</title>
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
    <div class="title">Portfolio</div>
{sub_html}

    <div class="filters">
{chips_html}
    </div>

    <div class="filter-status">
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
    /* Active-filter banner: the only filter cue on mobile, where the chips hide. */
    .filter-status {
      display: none;
      align-items: center;
      gap: 0.6em;
      margin: 0 0 1rem;
      font-size: 0.85em;
      color: #666;
    }
    .filter-status.on {
      display: flex;
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

    /* Section jump-nav: left rail on desktop, sticky top bar on mobile */
    .layout {
      display: flex;
      align-items: flex-start;
      gap: 2.5em;
    }
    .toc {
      /* width pinned in rem so bumping font-size below doesn't widen the column */
      flex: 0 0 8.8rem;
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

    /* Sections (always open — no collapse) */
    .proj-section {
      scroll-margin-top: 1.5em;
    }
    .proj-section .s-head {
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
    .proj-section .s-title {
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
    }

    .project {
      padding-bottom: 1em;
      border-bottom: 1px solid #ccc;
      margin-bottom: 1em;
    }
    .project:last-child,
    .project.no-divider {
      padding-bottom: 0;
      border-bottom: none;
      margin-bottom: 0;
    }
    .project h3 {
      color: #222;
      font-size: 1.15em;
      margin: 0 0 0.2em;
    }
    .project h3 a {
      color: #222;
    }
    .project h3 a:hover {
      color: #000;
      text-decoration: underline;
      text-underline-offset: 2px;
      text-decoration-color: #bbb;
    }
    .proj-head {
      display: flex;
      align-items: baseline;
      flex-wrap: wrap;
      gap: 0.2em 0.8em;
    }
    .proj-date {
      margin-left: auto;
      font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 0.78em;
      color: #aaa;
      letter-spacing: 0.03em;
      white-space: nowrap;
    }
    .project .tagline {
      font-size: 0.85em;
      color: #999;
      font-style: italic;
      margin: 0 0 0.9em;
    }
    .project p {
      line-height: 1.7;
      font-size: 0.9em;
      margin: 0 0 0.9em;
    }
    .shot {
      width: 100%;
      border: 1px solid #eee;
      border-radius: 4px;
      display: block;
      margin: 0 0 0.9em;
    }
    .proj-figure {
      display: block;
      width: 100%;
      height: auto;
      margin: 1.25em 0 0.25em;
    }
    .meta {
      font-size: 0.78em;
      color: #999;
      line-height: 1.9;
    }
    .meta .tags span:not(:last-child)::after {
      content: " · ";
      color: #ccc;
    }
    .meta .links {
      margin-top: 0.1em;
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
    // links) left with no visible card are hidden. An inbound ?era=/?skill= query
    // -- e.g. a link from the About page -- is applied on load.
    const chips = document.querySelectorAll('.chip');
    const projects = document.querySelectorAll('.project');
    const sections = document.querySelectorAll('section.proj-section');
    const navLinks = document.querySelectorAll('.toc a');
    const navLinkFor = id => document.querySelector('.toc a[data-sec="' + id + '"]');
    const statusEl = document.querySelector('.filter-status');
    const statusTextEl = document.querySelector('.filter-status-text');
    const chipLabel = (dim, val) => {
      const c = document.querySelector('.chip[data-dim="' + dim + '"][data-val="' + val + '"]');
      return c ? c.textContent : val;
    };

    const active = { era: 'all', skill: 'all' };

    function apply() {
      projects.forEach(p => {
        const okEra = active.era === 'all' || p.dataset.era === active.era;
        const okSkill = active.skill === 'all'
          || (p.dataset.themes || '').split(' ').includes(active.skill);
        p.style.display = (okEra && okSkill) ? '' : 'none';
      });
      sections.forEach(s => {
        const cards = [...s.querySelectorAll('.project')];
        const vis = cards.filter(p => p.style.display !== 'none');
        s.style.display = vis.length ? '' : 'none';
        const link = navLinkFor(s.id);
        if (link) link.style.display = vis.length ? '' : 'none';
        // Drop the divider on the last card still visible in this section.
        cards.forEach(p => p.classList.toggle('no-divider', p === vis[vis.length - 1]));
      });
      // Reflect the active filter in the status banner (the only cue on mobile).
      const labels = [];
      if (active.era !== 'all') labels.push(chipLabel('era', active.era));
      if (active.skill !== 'all') labels.push(chipLabel('skill', active.skill));
      statusTextEl.textContent = labels.length ? 'Showing: ' + labels.join(' · ') : '';
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
"""


if __name__ == "__main__":
    subtitle, themes, eras, sections = parse(SRC.read_text(encoding="utf-8"))
    validate(themes, eras, sections)
    OUT.write_text(render(subtitle, themes, eras, sections), encoding="utf-8")
    n_proj = sum(len(s["projects"]) for s in sections)
    print(f"  wrote portfolio.html —{len(sections)} sections, {n_proj} projects, "
          f"{len(eras)} eras, {len(themes)} themes")
