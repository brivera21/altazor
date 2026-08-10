#!/usr/bin/env python3
"""Build script for Altazor.

Reads markdown files from posts/, generates one HTML page per post,
an index.html, and an RSS feed (feed.xml).

Usage:
    python3 build.py

Requires: pip install markdown
"""

import html
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import markdown

# Edit these two lines once the GitHub repo exists.
SITE_URL = "https://brivera21.github.io/altazor"
SITE_TITLE = "Altazor"
SITE_DESCRIPTION = "Short pieces of writing and diagrams."

ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "posts"

CSS = """
:root {
  --text: #1a1a1a;
  --muted: #6b6b6b;
  --bg: #ffffff;
  --rule: #e4e4e4;
  --link: #1a1a1a;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 1.05rem;
  line-height: 1.65;
}
main {
  max-width: 40rem;
  margin: 0 auto;
  padding: 3rem 1.25rem 5rem;
}
header.site {
  margin-bottom: 3rem;
}
header.site a {
  font-family: Helvetica, Arial, sans-serif;
  font-weight: 700;
  font-size: 1rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  text-decoration: none;
  color: var(--text);
}
h1 {
  font-size: 1.7rem;
  line-height: 1.25;
  margin: 0 0 0.35rem;
}
h2 { font-size: 1.25rem; margin-top: 2.2rem; }
h3 { font-size: 1.05rem; margin-top: 1.8rem; }
a { color: var(--link); }
time, .date {
  font-family: Helvetica, Arial, sans-serif;
  font-size: 0.82rem;
  color: var(--muted);
}
article.post-body { margin-top: 2rem; }
ul.post-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
ul.post-list li {
  padding: 1.1rem 0;
  border-bottom: 1px solid var(--rule);
}
ul.post-list li:first-child { border-top: 1px solid var(--rule); }
ul.post-list a {
  font-size: 1.15rem;
  text-decoration: none;
}
ul.post-list a:hover { text-decoration: underline; }
ul.post-list .date { display: block; margin-top: 0.2rem; }
figure { margin: 2rem 0; text-align: center; }
figure svg { max-width: 100%; height: auto; }
figcaption {
  font-family: Helvetica, Arial, sans-serif;
  font-size: 0.82rem;
  color: var(--muted);
  margin-top: 0.6rem;
}
img { max-width: 100%; }
code {
  font-family: Menlo, Consolas, monospace;
  font-size: 0.88em;
  background: #f4f4f4;
  padding: 0.1em 0.3em;
  border-radius: 3px;
}
pre {
  background: #f4f4f4;
  padding: 1rem;
  overflow-x: auto;
  border-radius: 4px;
}
pre code { background: none; padding: 0; }
blockquote {
  margin: 1.5rem 0;
  padding-left: 1rem;
  border-left: 3px solid var(--rule);
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
  margin-top: 4rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--rule);
  font-family: Helvetica, Arial, sans-serif;
  font-size: 0.82rem;
  color: var(--muted);
}
footer.site a { color: var(--muted); }
"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="alternate" type="application/rss+xml" title="{site_title}" href="{root}feed.xml">
<style>{css}</style>
</head>
<body>
<main>
<header class="site"><a href="{root}">{site_title}</a></header>
{content}
<footer class="site"><a href="{root}feed.xml">RSS</a></footer>
</main>
</body>
</html>
"""


def parse_post(path):
    """Parse a markdown file with title/date frontmatter."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        raise ValueError(f"{path.name}: missing frontmatter (--- title/date ---)")
    meta = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip().lower()] = value.strip().strip('"')
    if "title" not in meta or "date" not in meta:
        raise ValueError(f"{path.name}: frontmatter needs both title and date")
    body = text[match.end():]
    return {
        "slug": path.stem,
        "title": meta["title"],
        "date": datetime.strptime(meta["date"], "%Y-%m-%d"),
        "html": markdown.markdown(body, extensions=["extra"]),
    }


def build():
    posts = sorted(
        (parse_post(p) for p in POSTS_DIR.glob("*.md")),
        key=lambda p: p["date"],
        reverse=True,
    )

    # Post pages, flat layout: one <slug>.html per post at the site root.
    for post in posts:
        content = (
            f"<article>\n<h1>{html.escape(post['title'])}</h1>\n"
            f"<time datetime=\"{post['date']:%Y-%m-%d}\">{post['date']:%B %-d, %Y}</time>\n"
            f"<div class=\"post-body\">\n{post['html']}\n</div>\n</article>"
        )
        page = PAGE_TEMPLATE.format(
            title=f"{post['title']} · {SITE_TITLE}",
            site_title=SITE_TITLE,
            root="./",
            css=CSS,
            content=content,
        )
        (ROOT / f"{post['slug']}.html").write_text(page, encoding="utf-8")

    # Index.
    items = "\n".join(
        f"<li><a href=\"{p['slug']}.html\">{html.escape(p['title'])}</a>"
        f"<time class=\"date\" datetime=\"{p['date']:%Y-%m-%d}\">{p['date']:%B %-d, %Y}</time></li>"
        for p in posts
    )
    index_content = f"<ul class=\"post-list\">\n{items}\n</ul>"
    index_page = PAGE_TEMPLATE.format(
        title=SITE_TITLE,
        site_title=SITE_TITLE,
        root="./",
        css=CSS,
        content=index_content,
    )
    (ROOT / "index.html").write_text(index_page, encoding="utf-8")

    # RSS feed.
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
<title>{html.escape(SITE_TITLE)}</title>
<link>{SITE_URL}</link>
<description>{html.escape(SITE_DESCRIPTION)}</description>
<lastBuildDate>{now}</lastBuildDate>
{rss_items}
</channel>
</rss>
"""
    (ROOT / "feed.xml").write_text(feed, encoding="utf-8")

    print(f"Built {len(posts)} post(s), index.html, feed.xml")


if __name__ == "__main__":
    build()
