#!/usr/bin/env python3
"""Build script for Altazor.

Sources:
    posts/*.md      pieces for the Notes section (title/date frontmatter)
    sections/*.md   body text for Library, Film, Elsewhere (title frontmatter)

Output (flat, upload-ready):
    index.html      landing page with a card per section
    library.html, film.html, notes.html, elsewhere.html
    <slug>.html     one page per post
    feed.xml        RSS for the Notes posts

Usage:
    python3 build.py

Requires: pip install markdown
"""

import html
import re
from datetime import datetime, timezone
from pathlib import Path

import markdown

SITE_URL = "https://brivera21.github.io/altazor"
SITE_TITLE = "Altazor"
SITE_DESCRIPTION = "A collection of different ideas."

ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "posts"
SECTIONS_DIR = ROOT / "sections"

# Landing cards, in order. Notes is generated from posts/; the others
# take their body from sections/<slug>.md.
SECTIONS = [
    {"slug": "library", "title": "Library", "blurb": "Books and reading."},
    {"slug": "film", "title": "Film", "blurb": "Films and watching."},
    {"slug": "notes", "title": "Notes", "blurb": "Short pieces of writing, with an RSS feed."},
    {"slug": "elsewhere", "title": "Elsewhere", "blurb": "Other places to find me."},
]

CSS = """
:root {
  --bg: #121212;
  --panel: #1a1a1a;
  --text: #e6e6e6;
  --muted: #9a9a9a;
  --line: #2b2b2b;
  --accent: #58a6ff;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font: 16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
}
.wrap {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 20px 80px;
}
header.site {
  border-top: 4px solid var(--accent);
  padding-top: 22px;
  margin-bottom: 34px;
  display: flex;
  align-items: baseline;
  gap: 18px;
  flex-wrap: wrap;
}
.brand {
  font-weight: 700;
  font-size: 20px;
  letter-spacing: 0.1em;
  text-decoration: none;
  color: var(--text);
}
.brand:hover { color: var(--accent); }
nav.site { display: flex; gap: 14px; flex-wrap: wrap; }
nav.site a {
  color: var(--muted);
  text-decoration: none;
  font-size: 14px;
}
nav.site a:hover, nav.site a.here { color: var(--accent); }
h1 { margin: 0 0 8px; font-size: 28px; line-height: 1.25; }
.lede { color: var(--muted); max-width: 640px; margin: 6px 0 30px; font-size: 15px; }
a { color: var(--accent); }

/* Landing cards */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}
.card {
  display: block;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 22px 20px 20px;
  text-decoration: none;
  color: var(--text);
  transition: transform 0.15s, border-color 0.15s;
}
.card:hover { transform: translateY(-3px); border-color: var(--accent); }
.card .num {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--accent);
}
.card h3 { margin: 8px 0 7px; font-size: 18px; }
.card p { margin: 0; font-size: 13.5px; color: var(--muted); }

/* Section and article pages */
.section-body, article {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.05rem;
  line-height: 1.7;
  max-width: 40rem;
}
.section-body p, article p { margin: 0 0 1.1rem; }
article h1 { font-family: Georgia, "Times New Roman", serif; }
time, .date {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 13px;
  color: var(--muted);
}
.post-body { margin-top: 1.6rem; }
ul.post-list { list-style: none; padding: 0; margin: 0; max-width: 40rem; }
ul.post-list li { padding: 1rem 0; border-bottom: 1px solid var(--line); }
ul.post-list li:first-child { border-top: 1px solid var(--line); }
ul.post-list a {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.15rem;
  color: var(--text);
  text-decoration: none;
}
ul.post-list a:hover { color: var(--accent); }
ul.post-list .date { display: block; margin-top: 0.2rem; }
figure { margin: 2rem 0; text-align: center; }
figure svg { max-width: 100%; height: auto; }
figcaption { font-size: 13px; color: var(--muted); margin-top: 0.6rem; }
img { max-width: 100%; }
code {
  font-family: Menlo, Consolas, monospace;
  font-size: 0.88em;
  background: var(--panel);
  padding: 0.1em 0.3em;
  border-radius: 3px;
}
pre { background: var(--panel); padding: 1rem; overflow-x: auto; border-radius: 6px; }
pre code { background: none; padding: 0; }
blockquote {
  margin: 1.5rem 0;
  padding-left: 1rem;
  border-left: 3px solid var(--line);
  color: var(--muted);
}
.bilingual { margin: 2rem 0; }
.bilingual .pair {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 1.6rem;
}
.bilingual .pair p { margin: 0 0 1.1rem; }
.bilingual p[lang="en"] { color: var(--muted); }
@media (max-width: 40rem) {
  .bilingual .pair { grid-template-columns: 1fr; }
  .bilingual .pair p { margin-bottom: 0.3rem; }
  .bilingual .pair p[lang="en"] { margin-bottom: 1.1rem; }
}
footer.site {
  margin-top: 60px;
  padding-top: 18px;
  border-top: 1px solid var(--line);
  font-size: 13px;
  color: var(--muted);
}
footer.site a { color: var(--muted); }
footer.site a:hover { color: var(--accent); }
"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="alternate" type="application/rss+xml" title="{site_title} · Notes" href="feed.xml">
<style>{css}</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site">{nav}</nav>
</header>
{content}
<footer class="site">{footer}</footer>
</div>
</body>
</html>
"""


def nav_html(here=None):
    links = []
    for s in SECTIONS:
        cls = ' class="here"' if s["slug"] == here else ""
        links.append(f'<a href="{s["slug"]}.html"{cls}>{s["title"]}</a>')
    return "\n".join(links)


def page(title, content, here=None, footer='<a href="index.html">Altazor</a>'):
    return PAGE_TEMPLATE.format(
        title=title,
        site_title=SITE_TITLE,
        css=CSS,
        nav=nav_html(here),
        content=content,
        footer=footer,
    )


def parse_md(path, required):
    """Parse a markdown file with frontmatter."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        raise ValueError(f"{path.name}: missing frontmatter")
    meta = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip().lower()] = value.strip().strip('"')
    for key in required:
        if key not in meta:
            raise ValueError(f"{path.name}: frontmatter needs {key}")
    body = text[match.end():]
    return meta, markdown.markdown(body, extensions=["extra"])


def build():
    # ---- posts (Notes) ----
    posts = []
    for p in POSTS_DIR.glob("*.md"):
        meta, body_html = parse_md(p, ["title", "date"])
        posts.append({
            "slug": p.stem,
            "title": meta["title"],
            "date": datetime.strptime(meta["date"], "%Y-%m-%d"),
            "html": body_html,
        })
    posts.sort(key=lambda p: p["date"], reverse=True)

    for post in posts:
        content = (
            f"<article>\n<h1>{html.escape(post['title'])}</h1>\n"
            f"<time datetime=\"{post['date']:%Y-%m-%d}\">{post['date']:%B %-d, %Y}</time>\n"
            f"<div class=\"post-body\">\n{post['html']}\n</div>\n</article>"
        )
        (ROOT / f"{post['slug']}.html").write_text(
            page(f"{post['title']} · {SITE_TITLE}", content, here="notes",
                 footer='<a href="notes.html">Notes</a> · <a href="feed.xml">RSS</a>'),
            encoding="utf-8",
        )

    # ---- notes.html ----
    items = "\n".join(
        f"<li><a href=\"{p['slug']}.html\">{html.escape(p['title'])}</a>"
        f"<time class=\"date\" datetime=\"{p['date']:%Y-%m-%d}\">{p['date']:%B %-d, %Y}</time></li>"
        for p in posts
    )
    notes_content = (
        "<h1>Notes</h1>\n"
        "<p class=\"lede\">Short pieces of writing. "
        "Follow along by <a href=\"feed.xml\">RSS</a>.</p>\n"
        f"<ul class=\"post-list\">\n{items}\n</ul>"
    )
    (ROOT / "notes.html").write_text(
        page(f"Notes · {SITE_TITLE}", notes_content, here="notes",
             footer='<a href="feed.xml">RSS</a>'),
        encoding="utf-8",
    )

    # ---- section pages from sections/*.md ----
    for s in SECTIONS:
        if s["slug"] == "notes":
            continue
        meta, body_html = parse_md(SECTIONS_DIR / f"{s['slug']}.md", ["title"])
        content = (
            f"<h1>{html.escape(meta['title'])}</h1>\n"
            f"<div class=\"section-body\">\n{body_html}\n</div>"
        )
        (ROOT / f"{s['slug']}.html").write_text(
            page(f"{meta['title']} · {SITE_TITLE}", content, here=s["slug"]),
            encoding="utf-8",
        )

    # ---- landing ----
    cards = "\n".join(
        f"""<a class="card" href="{s['slug']}.html">
<span class="num">{["I", "II", "III", "IV", "V", "VI"][i]}</span>
<h3>{s['title']}</h3>
<p>{s['blurb']}</p>
</a>"""
        for i, s in enumerate(SECTIONS)
    )
    landing = (
        f"<h1>{SITE_TITLE}</h1>\n"
        f"<p class=\"lede\">{SITE_DESCRIPTION}</p>\n"
        f"<div class=\"grid\">\n{cards}\n</div>"
    )
    (ROOT / "index.html").write_text(
        page(SITE_TITLE, landing, footer='<a href="feed.xml">RSS</a>'),
        encoding="utf-8",
    )

    # ---- RSS (Notes) ----
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    rss_items = "\n".join(
        f"""<item>
<title>{html.escape(p['title'])}</title>
<link>{SITE_URL}/{p['slug']}.html</link>
<guid>{SITE_URL}/{p['slug']}.html</guid>
<pubDate>{p['date'].strftime('%a, %d %b %Y 00:00:00 +0000')}</pubDate>
<description>{html.escape(p['html'])}</description>
</item>"""
        for p in posts
    )
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>{html.escape(SITE_TITLE)} · Notes</title>
<link>{SITE_URL}/notes.html</link>
<description>{html.escape(SITE_DESCRIPTION)}</description>
<lastBuildDate>{now}</lastBuildDate>
{rss_items}
</channel>
</rss>
"""
    (ROOT / "feed.xml").write_text(feed, encoding="utf-8")

    print(f"Built landing, {len(SECTIONS)} sections, {len(posts)} post(s), feed.xml")


if __name__ == "__main__":
    build()
