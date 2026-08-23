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

## The copy rule

Every diagram page opens with the diagram. Nothing above it explains it: a
title, a date stamp, the controls and the nav, and then the thing itself.

The description goes underneath.

- 40 to 80 words per paragraph is the comfortable length, 100 is the ceiling
- the whole description runs 180 words or fewer, usually in one or two paragraphs
- sources, citations and method notes are not description. They go last, in a
  `.refs` or `.method` block, and have no word limit
- third person throughout. The copy says what the page does, not what the
  reader should do: "the wheel zooms", not "scroll to zoom"; "un estado bajo el
  cursor muestra su superficie", not "pasa el cursor sobre un estado". This
  covers hint labels and legends too, not just the paragraphs
- no em dashes in page copy
- no count that will grow

`tools/verify_copy_rule.py` checks all of this in a headless browser, so it
reads the page as rendered rather than as written. Run it after any build.

## Building a diagram page

Each diagram page has a generator in `tools/`, named `build_<page>.py`, which
writes the flat HTML at the repo root. `build.py` only handles the markdown
posts and the section index pages. Rebuild a diagram by running its generator,
then run `tools/verify_copy_rule.py` and whichever `tools/verify_<page>.py`
exists for it.

The page is laid out in this order, top to bottom:

1. the site header, the brand and the link back to the section
2. the `h1`, and nothing else in prose above the diagram
3. the `.tiles` row: a handful of boxes, each a label, a value and a one line
   gloss. Either the constants the diagram is about, which set up what is
   about to move, or the readouts themselves where the diagram has a clock or
   a slider and the reader wants the numbers next to the picture rather than
   under it. A page carries one or the other, not both rows: if the readouts
   are up here, there is no second row of them below the controls. Pages with
   neither skip the row
4. the diagram, then its controls
5. the description, under the copy rule above
6. `References`, in APA, with no word limit

Nothing else goes above the diagram: no source line, no date stamp, no
explanation of what is about to happen.

A canvas page that fills the window rather than sitting in the flow follows the
same order in the overlay: brand and `h1` at the top left, readouts at the top
right, the control bar at the foot, and the description in that bar. Anything
drawn on the canvas is sized off a measurement of that furniture, never off the
window alone, or it ends up printed over the diagram. `verify_<page>.py` should
walk several window sizes and fail when the two collide.

## Setup notes

- `SITE_URL` at the top of `build.py` is the published URL, used for RSS feed links
- Live at https://brivera21.github.io/altazor/ (repo brivera21/altazor, Pages from branch `main`, root)
- Publishing follows the same pattern as the Diagram Lab: this folder is the master; upload changed flat files (`index.html`, `<slug>.html`, `feed.xml`) to the repo through GitHub's web upload page, via Claude in Chrome
- `.nojekyll` keeps GitHub from running Jekyll on the output
