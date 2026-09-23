#!/usr/bin/env python3
"""Puts the three Chess terms pages in the site's clothes.

opening-terms.html, middlegame-terms.html and endgame-terms.html each keep
their content in a TERMS array at the top of the script. That array is the
page: adding a term means adding one object to it, in the HTML itself. So
this script never holds the terms. It lifts each page's array out verbatim,
wraps it in one shared shell, and writes the page back, which is what keeps
the three identical in everything except their terms.

Run it again after editing a TERMS array and the edit survives, because the
array is read from the page it is about to rewrite. The first run reads the
standalone pages as they were supplied, from the uploads folder.

The board renderer is the supplied one, unchanged in what it does: it reads
the FEN directly, and a square is dark when (file + rank) is odd, which puts
a1 on a dark square. Only the colors changed, to the site's board colors.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
UPLOADS = pathlib.Path("/root/.claude/uploads/f95ea291-68fe-5058-9839-3897087404c1")

# file, Library title, section, what the page is, where the supplied copy sits
PAGES = [
    ("opening-terms.html", "Opening Terms", "Openings",
     "Terms from the opening, each on the position that shows it.",
     "7c929225-opening-terms.html"),
    ("middlegame-terms.html", "Middlegame Terms", "Middle Games",
     "Terms from the middlegame, each on the position that shows it.",
     "c8609caf-middlegame-terms.html"),
    ("endgame-terms.html", "Endgame Terms", "Endgames",
     "Terms from the endgame, each on the position that shows it.",
     "ed8cd110-endgame-terms.html"),
]

TERMS_RE = re.compile(r"const TERMS = \[\n.*?\n\];", re.S)


def terms_block(path):
    m = TERMS_RE.search(path.read_text(encoding="utf-8"))
    if not m:
        sys.exit(f"no TERMS array in {path}")
    return m.group(0)


CSS = """
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff;
        --sq-light:#a9b2be; --sq-dark:#5a6472;
        --subject:#f09b28; --target:#e0684b; --plan:#58a6ff; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased; }
.wrap { max-width:1240px; margin:0 auto; padding:32px 20px 60px; }
header.site { border-top:4px solid var(--accent); padding-top:22px; margin-bottom:26px;
  display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }
.brand { font-weight:700; font-size:20px; letter-spacing:.1em; text-decoration:none;
  color:var(--text); }
.brand:hover { color:var(--accent); }
nav.site a { color:var(--muted); text-decoration:none; font-size:14px; margin-right:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 14px; font-size:26px; }

.controls { display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin:0 0 18px; }
.chip { font:inherit; font-size:13.5px; padding:6px 14px; border-radius:999px;
  border:1px solid var(--line); background:var(--panel); color:var(--text); cursor:pointer; }
.chip:hover { border-color:var(--accent); }
.chip[aria-selected="true"] { background:var(--accent); border-color:var(--accent);
  color:#0b1a2b; font-weight:600; }
.keys { color:var(--muted); font-size:12.5px; margin-left:6px; }

.boardcol { max-width:560px; }
.board-grid { display:grid;
  grid-template-columns:1.4em min(86vw, 520px);
  grid-template-rows:min(86vw, 520px) 1.4em;
  align-items:center; justify-items:center; }
.ranks, .files { display:grid; width:100%; height:100%; }
.ranks { grid-template-rows:repeat(8, 1fr); }
.files { grid-template-columns:repeat(8, 1fr); grid-column:2; }
.ranks span, .files span { display:flex; align-items:center; justify-content:center;
  font-size:11px; color:#7c7c7c; font-variant-numeric:tabular-nums; }
.board { display:grid; grid-template-columns:repeat(8, 1fr); grid-template-rows:repeat(8, 1fr);
  width:100%; height:100%; border:1px solid #333; border-radius:4px; overflow:hidden; }
.sq { position:relative; display:flex; align-items:center; justify-content:center; }
.sq.l { background:var(--sq-light); }
.sq.d { background:var(--sq-dark); }
.sq[data-mark]::after { content:""; position:absolute; inset:0;
  box-shadow:inset 0 0 0 3px currentColor; background:currentColor; opacity:.38; }
.sq[data-mark="subject"] { color:var(--subject); }
.sq[data-mark="target"] { color:var(--target); }
.sq[data-mark="plan"] { color:var(--plan); }
.pc { position:relative; z-index:1; font-size:min(10vw, 56px); line-height:1; user-select:none; }
.pc.w { color:#f6f6f4; -webkit-text-stroke:1.3px #15181c; text-shadow:0 0 1px #15181c; }
.pc.b { color:#15181c; text-shadow:0 0 2px rgba(255,255,255,.35); }

.turn { font-size:13px; color:var(--muted); margin:10px 0 0 1.4em; }
.legend { display:flex; flex-wrap:wrap; gap:6px 18px; margin:12px 0 0 1.4em; }
.legend div { display:flex; align-items:center; gap:7px; font-size:13px; color:var(--muted); }
.swatch { width:13px; height:13px; border-radius:3px; background:currentColor; opacity:.6;
  box-shadow:inset 0 0 0 2px currentColor; }
.sw-subject { color:var(--subject); }
.sw-target { color:var(--target); }
.sw-plan { color:var(--plan); }

.text { margin:30px 0 0; border-top:1px solid var(--line); padding-top:22px; max-width:72ch; }
.text h2 { font-size:21px; margin:0 0 2px; font-weight:650; }
.tagline { color:var(--muted); margin:0 0 16px; }
.text p { margin:0 0 14px; color:#d4d4d4; }
.moves { font-variant-numeric:tabular-nums; }

footer.site { margin-top:60px; padding-top:18px; border-top:1px solid var(--line);
  font-size:13px; color:var(--muted); }
footer.site a { color:var(--muted); }
footer.site a:hover { color:var(--accent); }
@media (max-width:520px) {
  .board-grid { grid-template-columns:1.2em min(90vw, 520px); grid-template-rows:min(90vw, 520px) 1.2em; }
  .pc.w { -webkit-text-stroke:.8px #15181c; }
}
"""

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ &middot; Altazor</title>
<meta name="description" content="__DESC__">
<style>__CSS__</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="chess.html">&larr; Chess</a>
__NAV__</nav>
</header>
<h1>__TITLE__</h1>
<div class="controls">
  <div class="chips" id="chips" role="tablist" style="display:contents"></div>
  <span class="keys">Arrow keys step through the terms.</span>
</div>

<div class="boardcol">
  <div class="board-grid">
    <div class="ranks" id="ranks"></div>
    <div class="board" id="board" role="img" aria-label="The position for the selected term"></div>
    <div class="files" id="files"></div>
  </div>
  <p class="turn" id="turn"></p>
  <div class="legend" id="legend"></div>
</div>

<div class="text diagram-text">
  <h2 id="name"></h2>
  <p class="tagline" id="tagline"></p>
  <div id="body"></div>
</div>

<footer class="site"><a href="index.html">Altazor</a> &middot; <a href="chess.html">Chess</a> &middot; __SECTION__</footer>
</div>

<script>
__TERMS__

const GLYPH = { k: "\\u265A", q: "\\u265B", r: "\\u265C", b: "\\u265D", n: "\\u265E", p: "\\u265F" };
const FILES = ["a", "b", "c", "d", "e", "f", "g", "h"];

function parseFen(fen) {
  const rows = fen.split(" ")[0].split("/");
  const out = {};
  rows.forEach((row, i) => {
    const rank = 8 - i;
    let file = 0;
    for (const ch of row) {
      if (/\\d/.test(ch)) { file += parseInt(ch, 10); continue; }
      out[FILES[file] + rank] = ch;
      file += 1;
    }
  });
  return out;
}

function drawBoard(term) {
  const pieces = parseFen(term.fen);
  const board = document.getElementById("board");
  board.textContent = "";
  for (let rank = 8; rank >= 1; rank--) {
    for (let f = 0; f < 8; f++) {
      const name = FILES[f] + rank;
      const sq = document.createElement("div");
      sq.className = "sq " + (((f + rank) % 2 === 0) ? "l" : "d");
      sq.dataset.sq = name;
      if (term.marks[name]) sq.dataset.mark = term.marks[name];
      const p = pieces[name];
      if (p) {
        const span = document.createElement("span");
        span.className = "pc " + (p === p.toUpperCase() ? "w" : "b");
        span.textContent = GLYPH[p.toLowerCase()];
        sq.appendChild(span);
      }
      board.appendChild(sq);
    }
  }
}

function render(index) {
  const term = TERMS[index];
  drawBoard(term);
  document.getElementById("turn").textContent = term.turn;
  document.getElementById("name").textContent = term.name;
  document.getElementById("tagline").textContent = term.tagline;

  const legend = document.getElementById("legend");
  legend.textContent = "";
  term.legend.forEach(([kind, label]) => {
    const row = document.createElement("div");
    const sw = document.createElement("span");
    sw.className = "swatch sw-" + kind;
    row.appendChild(sw);
    row.appendChild(document.createTextNode(label));
    legend.appendChild(row);
  });

  const body = document.getElementById("body");
  body.textContent = "";
  term.body.forEach(par => {
    const p = document.createElement("p");
    if (par.startsWith("|")) { p.className = "moves"; p.textContent = par.slice(1); }
    else p.textContent = par;
    body.appendChild(p);
  });

  document.querySelectorAll(".chip").forEach((c, i) => {
    c.setAttribute("aria-selected", i === index ? "true" : "false");
  });
  current = index;
}

const chips = document.getElementById("chips");
TERMS.forEach((t, i) => {
  const b = document.createElement("button");
  b.className = "chip";
  b.type = "button";
  b.setAttribute("role", "tab");
  b.textContent = t.name;
  b.addEventListener("click", () => render(i));
  chips.appendChild(b);
});

const ranks = document.getElementById("ranks");
for (let r = 8; r >= 1; r--) {
  const s = document.createElement("span");
  s.textContent = r;
  ranks.appendChild(s);
}
const filesEl = document.getElementById("files");
FILES.forEach(f => {
  const s = document.createElement("span");
  s.textContent = f;
  filesEl.appendChild(s);
});

let current = 0;
render(0);

document.addEventListener("keydown", e => {
  if (e.key === "ArrowRight") render((current + 1) % TERMS.length);
  if (e.key === "ArrowLeft") render((current - 1 + TERMS.length) % TERMS.length);
});

// for the verifier: pick a term, report what the page is showing
window.__terms = function (q) {
  if (q && Number.isInteger(q.pick)) render(q.pick);
  const sq = [...document.querySelectorAll("#board .sq")];
  return {
    current, count: TERMS.length,
    chips: document.querySelectorAll(".chip").length,
    squares: sq.length,
    a1: document.querySelector('#board .sq[data-sq="a1"]').className,
    h1: document.querySelector('#board .sq[data-sq="h1"]').className,
    pieces: sq.filter(s => s.querySelector(".pc")).map(s => s.dataset.sq + ":" +
      (s.querySelector(".pc").classList.contains("w") ? "w" : "b") + s.querySelector(".pc").textContent),
    marks: sq.filter(s => s.dataset.mark).map(s => s.dataset.sq + ":" + s.dataset.mark),
    legend: document.querySelectorAll("#legend > div").length,
    name: document.getElementById("name").textContent,
    turn: document.getElementById("turn").textContent,
    paras: document.querySelectorAll("#body p").length,
    selected: [...document.querySelectorAll(".chip")].findIndex(c => c.getAttribute("aria-selected") === "true"),
  };
};
</script>
</body>
</html>
"""


def nav_for(fname):
    return "\n".join(f'  <a href="{f}">{t}</a>' for f, t, *_ in PAGES if f != fname)


def main():
    for fname, title, section, desc, upload in PAGES:
        page = ROOT / fname
        src = page if page.exists() else UPLOADS / upload
        block = terms_block(src)
        html = (HTML.replace("__CSS__", CSS)
                    .replace("__TITLE__", title)
                    .replace("__DESC__", desc)
                    .replace("__SECTION__", section)
                    .replace("__NAV__", nav_for(fname))
                    .replace("__TERMS__", block))
        page.write_text(html, encoding="utf-8")
        n = block.count('"name":')
        print(f"  {fname:24} {len(html):>7,} B   {n} term{'s' if n != 1 else ''}   (TERMS read from {src.parent.name}/{src.name})")


if __name__ == "__main__":
    main()
