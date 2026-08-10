# Altazor

Personal site for short pieces of writing and diagrams. Static HTML built from markdown, hosted on GitHub Pages.

## Layout

- `posts/` holds the markdown sources, one file per piece, with `title` and `date` frontmatter
- `build.py` turns them into HTML: one flat `<slug>.html` per post, plus `index.html` and `feed.xml`
- Generated files are committed so GitHub Pages can serve them directly

## Adding a piece

1. Create `posts/my-slug.md`:

   ```
   ---
   title: My Title
   date: 2026-08-09
   ---

   Text goes here. Inline SVG works for diagrams.
   ```

2. Rebuild: `python3 build.py` (needs `pip install markdown` once)
3. Commit and push:

   ```
   git add -A
   git commit -m "Add: My Title"
   git push
   ```

## Setup notes

- `SITE_URL` at the top of `build.py` is the published URL, used for RSS feed links
- Live at https://brivera21.github.io/altazor/ (repo brivera21/altazor, Pages from branch `main`, root)
- Publishing follows the same pattern as the Diagram Lab: this folder is the master; upload changed flat files (`index.html`, `<slug>.html`, `feed.xml`) to the repo through GitHub's web upload page, via Claude in Chrome
- `.nojekyll` keeps GitHub from running Jekyll on the output
