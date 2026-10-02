#!/usr/bin/env python3
"""Builds the Chess section's term pages: the three supplied terms pages,
and the pages that share their form (the six piece pages, Tactics,
Checkmates and Fundamental Terms).

The first part of this note is about the three supplied pages.

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

The other pages are written from tools/chess_pages_data.py, and so are the
terms added to the three supplied pages: those are merged into each page's
own array by name, after the supplied terms, which stay byte for byte as
they were. An entry given as a line of moves is played here with
python-chess and its FEN taken from the result, so an illegal move stops the
build. Two things the supplied renderer did not do are added for the new
entries, and the supplied terms never use them: a fourth mark color
("zone"), and a count on every square drawn as a heat map ("numbers").
"""

import json
import pathlib
import re
import sys

import chess

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from chess_pages_data import PAGES as DATA  # noqa: E402

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

# the pages written from the data file: file, title, column, description, data key
NEW = [
    ("fundamental-terms.html", "Fundamental Terms", "Fundamentals",
     "Terms that belong to no one phase of the game.", "fundamental"),
    ("pawn.html", "Pawn", "Fundamentals", "The pawn, and the words for what pawns do.", "pawn"),
    ("knight.html", "Knight", "Fundamentals", "Where a knight sees most, and where it belongs.", "knight"),
    ("bishop.html", "Bishop", "Fundamentals", "The bishop's diagonals, and the terms that go with them.", "bishop"),
    ("rook.html", "Rook", "Fundamentals", "The rook's files and ranks, and the terms that go with them.", "rook"),
    ("queen.html", "Queen", "Fundamentals", "How far the queen sees.", "queen"),
    ("king.html", "King", "Fundamentals", "The king in attack, defense and the ending.", "king"),
    ("tactics.html", "Tactics", "Fundamentals", "Double attacks, pins and the rest, each on a position.", "tactics"),
    ("checkmates.html", "Checkmates", "Endgames", "Named mating patterns, each on a position.", "checkmates"),
    ("lessons.html", "Lessons", "Miscellaneous", "Lessons from games, each on the position it turns on.", "lessons"),
]

# which pages share a navigation row
NAV_GROUPS = [
    ["intuition.html", "fundamental-terms.html", "pawn.html", "knight.html", "bishop.html",
     "rook.html", "queen.html", "king.html", "tactics.html"],
    ["opening-terms.html", "middlegame-terms.html", "endgame-terms.html", "checkmates.html"],
    ["lessons.html"],
]
TITLES = {f: t for f, t, *_ in PAGES}
TITLES.update({f: t for f, t, *_ in NEW})
TITLES["intuition.html"] = "Board Intuition"

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
        --subject:#f09b28; --target:#e0684b; --plan:#58a6ff; --zone:#f5d49a; }
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

/* the terms in a column on the left, the board and its caption on the right */
.layout { display:grid; grid-template-columns:220px minmax(0, 1fr); gap:32px; align-items:start; }
.termcol { position:sticky; top:16px; max-height:calc(100vh - 32px); overflow-y:auto; }
.chips { display:flex; flex-direction:column; gap:4px; }
.chip { font:inherit; font-size:13.5px; padding:6px 12px; border-radius:8px; text-align:left;
  border:1px solid var(--line); background:var(--panel); color:var(--text); cursor:pointer; }
.chip:hover { border-color:var(--accent); }
.chip[aria-selected="true"] { background:var(--accent); border-color:var(--accent);
  color:#0b1a2b; font-weight:600; }
.keys { display:block; color:var(--muted); font-size:12px; margin:12px 2px 0; }
.main { display:flex; flex-wrap:wrap; gap:8px 36px; align-items:flex-start; }

.boardcol { --bs:clamp(260px, 42vw, 500px); flex:0 0 auto; width:calc(1.4em + var(--bs)); }
.board-grid { display:grid;
  grid-template-columns:1.4em var(--bs);
  grid-template-rows:var(--bs) 1.4em;
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
.sq[data-mark="zone"] { color:var(--zone); }
.sq[data-mark="zone"]::after { opacity:.30; }
.heat { position:absolute; inset:0; background:var(--subject); pointer-events:none; }
.num { position:relative; z-index:1; font-size:min(4.2vw, 21px); font-weight:650;
  color:#101316; font-variant-numeric:tabular-nums; }
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
.sw-zone { color:var(--zone); }

.text { flex:1 1 300px; margin:0; max-width:60ch; }
.text h2 { font-size:21px; margin:0 0 2px; font-weight:650; }
.tagline { color:var(--muted); margin:0 0 16px; }
.text p { margin:0 0 14px; color:#d4d4d4; }
.moves { font-variant-numeric:tabular-nums; }
.text ul { margin:-6px 0 14px; padding-left:22px; color:#d4d4d4; }
.text li { margin:0 0 4px; }

footer.site { margin-top:60px; padding-top:18px; border-top:1px solid var(--line);
  font-size:13px; color:var(--muted); }
footer.site a { color:var(--muted); }
footer.site a:hover { color:var(--accent); }
@media (max-width:760px) {
  .layout { grid-template-columns:1fr; gap:18px; }
  .termcol { position:static; max-height:none; }
  .chips { flex-direction:row; flex-wrap:wrap; }
  .chip { border-radius:999px; }
  .boardcol { --bs:min(calc(100vw - 64px), 520px); }
  .text { margin-top:14px; }
}
@media (max-width:520px) {
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
<div class="layout">
<div class="termcol">
  <div class="chips" id="chips" role="tablist" aria-orientation="vertical"></div>
  <span class="keys">Arrow keys step through __NOUN__.</span>
</div>

<div class="main">
<div class="boardcol">
  <div class="board-grid">
    <div class="ranks" id="ranks"></div>
    <div class="board" id="board" role="img" aria-label="The position for the selected __ONE__"></div>
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
</div>
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
      if (term.numbers && term.numbers[name] !== undefined) {
        // a count on the square, and a wash that deepens with it
        const vals = Object.values(term.numbers);
        const lo = Math.min(...vals), hi = Math.max(...vals);
        const heat = document.createElement("div");
        heat.className = "heat";
        heat.style.opacity = (hi === lo ? 0.5 : 0.12 + 0.6 * (term.numbers[name] - lo) / (hi - lo)).toFixed(3);
        sq.appendChild(heat);
        sq.dataset.n = term.numbers[name];
      }
      const p = pieces[name];
      if (p) {
        const span = document.createElement("span");
        span.className = "pc " + (p === p.toUpperCase() ? "w" : "b");
        span.textContent = GLYPH[p.toLowerCase()];
        sq.appendChild(span);
      } else if (sq.dataset.n !== undefined) {
        const n = document.createElement("span");
        n.className = "num";
        n.textContent = sq.dataset.n;
        sq.appendChild(n);
      }
      board.appendChild(sq);
    }
  }
}

function render(index) {
  const term = TERMS[index];
  drawBoard(term);
  document.getElementById("turn").textContent = term.turn;
  document.getElementById("turn").hidden = !term.turn;
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
  let list = null;
  term.body.forEach(par => {
    // lines starting "- " gather into one list
    if (par.startsWith("- ")) {
      if (!list) { list = document.createElement("ul"); body.appendChild(list); }
      const li = document.createElement("li");
      li.textContent = par.slice(2);
      list.appendChild(li);
      return;
    }
    list = null;
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
    numbers: Object.fromEntries(sq.filter(s => s.dataset.n !== undefined).map(s => [s.dataset.sq, +s.dataset.n])),
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
    group = next(g for g in NAV_GROUPS if fname in g)
    return "\n".join(f'  <a href="{f}">{TITLES[f]}</a>' for f in group if f != fname)


def prepare(term):
    """A data entry as a TERMS object: moves played out into a FEN."""
    out = {"name": term["name"], "tagline": term["tagline"]}
    if "moves" in term:
        b = chess.Board()
        for t in term["moves"].split():
            b.push_san(t)
        out["fen"] = b.board_fen()
    else:
        out["fen"] = term["fen"]
    out["turn"] = term["turn"]
    out["marks"] = term["marks"]
    out["legend"] = term["legend"]
    out["body"] = term["body"]
    if "numbers" in term:
        out["numbers"] = term["numbers"]
    return out


def block_of(terms):
    return "const TERMS = " + json.dumps(terms, indent=2, ensure_ascii=False) + ";"


def write(fname, title, section, desc, block):
    html = (HTML.replace("__CSS__", CSS)
                .replace("__TITLE__", title)
                .replace("__DESC__", desc)
                .replace("__SECTION__", section)
                .replace("__NAV__", nav_for(fname))
                .replace("__NOUN__", "the lessons" if fname == "lessons.html" else "the terms")
                .replace("__ONE__", "lesson" if fname == "lessons.html" else "term")
                .replace("__TERMS__", block))
    (ROOT / fname).write_text(html, encoding="utf-8")
    return html


def main():
    for fname, title, section, desc, upload in PAGES:
        page = ROOT / fname
        src = page if page.exists() else UPLOADS / upload
        block = terms_block(src)
        terms = json.loads(block[len("const TERMS = "):-1])
        # the additions, merged by name after whatever the page already holds
        for add in map(prepare, DATA.get(fname, [])):
            at = next((i for i, t in enumerate(terms) if t["name"] == add["name"]), None)
            if at is None:
                terms.append(add)
            else:
                terms[at] = add
        block = block_of(terms)
        html = write(fname, title, section, desc, block)
        print(f"  {fname:24} {len(html):>7,} B   {len(terms)} terms")
    for fname, title, section, desc, key in NEW:
        terms = [prepare(t) for t in DATA[key]]
        html = write(fname, title, section, desc, block_of(terms))
        print(f"  {fname:24} {len(html):>7,} B   {len(terms)} terms")


if __name__ == "__main__":
    main()
