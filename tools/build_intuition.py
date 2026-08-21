#!/usr/bin/env python3
"""Generate intuition.html: Board Intuition, an interactive version of the
"Board intuition trainer" PDF for the Chess section.

One board, 18 topics in three groups (Geography / Piece vision / Endgame
rules). Clicking a topic repaints the board with tiered amber highlights
(smooth CSS transitions), optional piece glyphs, and optional per-square
numbers (mobility heatmaps). Hovering any square shows its coordinate.

Usage: python3 build_intuition.py
"""

import json
from pathlib import Path

OUT = Path(__file__).parent.parent / "intuition.html"

FILES = "abcdefgh"


def sq(f, r):
    return FILES[f] + str(r)


def rank(r):
    return [sq(f, r) for f in range(8)]


def frange(f0, f1, r0, r1):
    return [sq(f, r) for f in range(f0, f1 + 1) for r in range(r0, r1 + 1)]


def diag(f, r, df, dr):
    out = []
    while 0 <= f <= 7 and 1 <= r <= 8:
        out.append(sq(f, r))
        f += df
        r += dr
    return out


def knight_counts():
    out = {}
    for f in range(8):
        for r in range(1, 9):
            n = 0
            for df, dr in ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2),
                           (-2, -1), (-2, 1), (-1, 2)):
                if 0 <= f + df <= 7 and 1 <= r + dr <= 8:
                    n += 1
            out[sq(f, r)] = n
    return out


def king_counts():
    out = {}
    for f in range(8):
        for r in range(1, 9):
            n = 0
            for df in (-1, 0, 1):
                for dr in (-1, 0, 1):
                    if (df or dr) and 0 <= f + df <= 7 and 1 <= r + dr <= 8:
                        n += 1
            out[sq(f, r)] = n
    return out


def ray_counts(dirs, blocked=()):
    """Squares a sliding piece reaches from each square, stopping before any
    square in `blocked`. The blocked squares get no count of their own."""
    out = {}
    for f in range(8):
        for r in range(1, 9):
            if sq(f, r) in blocked:
                continue
            n = 0
            for df, dr in dirs:
                ff, rr = f + df, r + dr
                while 0 <= ff <= 7 and 1 <= rr <= 8 and sq(ff, rr) not in blocked:
                    n += 1
                    ff += df
                    rr += dr
            out[sq(f, r)] = n
    return out


DIAG = ((1, 1), (1, -1), (-1, 1), (-1, -1))
ORTHO = ((1, 0), (-1, 0), (0, 1), (0, -1))
ROOK_PAWN = "e4"          # one white pawn, to cast a shadow across the board


def bishop_counts():
    return ray_counts(DIAG)


def rook_counts():
    return ray_counts(ORTHO)


def rook_counts_blocked():
    return ray_counts(ORTHO, blocked={ROOK_PAWN})


dark_squares = [sq(f, r) for f in range(8) for r in range(1, 9)
                if (f + r) % 2 == 1]

f7_diags = (diag(0, 2, 1, 1) + diag(4, 8, 1, -1) +   # a2-g8, e8-h5
            diag(0, 7, 1, -1) + diag(4, 1, 1, 1))     # a7-g1, e1-h4
f7_diags = sorted(set(f7_diags) - {"f2", "f7"})

long_diags = sorted(set(diag(0, 1, 1, 1) + diag(0, 8, 1, -1)) -
                    {"b2", "g2", "b7", "g7"})

atk_diags = sorted(set(diag(1, 1, 1, 1) + diag(1, 8, 1, -1)) - {"h7", "h2"})

TOPICS = [
 dict(id="reference", g="Geography", t="Reference board",
      c="Corner labels stay readable with pieces on the board. Every topic "
        "that follows repaints this same board.",
      strong=[], soft=[], legend=[]),
 dict(id="ranks", g="Geography", t="Pawn ranks and back ranks",
      c="Every pawn starts on the 2nd or 7th rank. Every piece starts on the "
        "1st or 8th, behind its own pawns.",
      strong=rank(2) + rank(7), soft=rank(1) + rank(8),
      legend=[("s", "2nd and 7th ranks: pawn starting squares"),
              ("w", "1st and 8th ranks: back rank, pieces")]),
 dict(id="center", g="Geography", t="The center",
      c="d4, d5, e4 and e5. Occupying or controlling these four squares gives "
        "pieces the most scope and the shortest routes to both wings.",
      strong=["d4", "d5", "e4", "e5"], soft=[],
      legend=[("s", "the center: d4, d5, e4, e5")]),
 dict(id="extcenter", g="Geography", t="The extended center",
      c="The 16 squares from c3 to f6. Most opening theory is a fight over "
        "this block, either by occupying it or controlling it from afar.",
      strong=["d4", "d5", "e4", "e5"],
      soft=sorted(set(frange(2, 5, 3, 6)) - {"d4", "d5", "e4", "e5"}),
      legend=[("s", "center: d4, d5, e4, e5"),
              ("w", "extended center: c3 to f6")]),
 dict(id="files", g="Geography", t="The d-file and the e-file",
      c="The two center files. Whichever one opens first tends to define the "
        "character of the middlegame.",
      strong=[sq(4, r) for r in range(1, 9)],
      soft=[sq(3, r) for r in range(1, 9)],
      legend=[("s", "e-file: aims at the king's starting square"),
              ("w", "d-file: aims at the queen's starting square")]),
 dict(id="wings", g="Geography", t="Kingside and queenside",
      c="Files a to d are the queenside, e to h the kingside. Castling sends "
        "the king to g1 or c1, and the rook to f1 or d1.",
      strong=["c1", "c8"],
      soft=sorted(set(frange(0, 3, 1, 8)) - {"c1", "c8"}),
      strong2=["g1", "g8"],
      soft2=sorted(set(frange(4, 7, 1, 8)) - {"g1", "g8"}),
      legend=[("s", "queenside castling: the king lands on c1 or c8"),
              ("w", "queenside, files a to d"),
              ("s2", "kingside castling: the king lands on g1 or g8"),
              ("w2", "kingside, files e to h")]),
 dict(id="colors", g="Geography", t="Color complexes",
      c="32 light squares and 32 dark. A bishop never leaves its own color, "
        "so trading one hands the opponent a permanent say over the other "
        "half.",
      strong=dark_squares, soft=[],
      legend=[("s", "the 32 dark squares, a1 through h8")]),
 dict(id="knight", g="Piece vision", t="Knight mobility",
      c="The number of squares a knight attacks from each square. Two in the "
        "corner, eight in the center. This is why the rim is dim.",
      strong=[], soft=[], numbers=knight_counts(), heat=True,
      legend=[("s", "more squares attacked"), ("w", "fewer")]),
 dict(id="king", g="Piece vision", t="King mobility",
      c="Squares a king reaches in one move. Three in the corner, five on an "
        "edge, eight in the middle. Endgame kings belong in the middle.",
      strong=[], soft=[], numbers=king_counts(), heat=True,
      legend=[("s", "more squares reached"), ("w", "fewer")]),
 dict(id="bishop", g="Piece vision", t="Bishop mobility",
      c="The number of squares a bishop attacks from each square. Seven "
        "anywhere on the rim, rising by two with each ring inward to thirteen "
        "on the four center squares. A bishop never changes color, so even at "
        "its best it sees thirteen of the thirty two squares it can ever "
        "reach.",
      strong=[], soft=[], numbers=bishop_counts(), heat=True,
      legend=[("s", "more squares attacked"), ("w", "fewer")]),
 dict(id="rook", g="Piece vision", t="Rook mobility",
      c="Fourteen from every square on the board. The rook is the only piece "
        "whose reach does not change with where it stands, so on an empty "
        "board a1 is worth as much as e5 and the only question is what "
        "stands in the way.",
      strong=[], soft=[], numbers=rook_counts(), heat=True,
      legend=[("s", "fourteen squares, the same from everywhere")]),
 dict(id="rookpawn", g="Piece vision", t="Rook behind its own pawn",
      c="The same board with one white pawn on e4. Off the e-file and the "
        "fourth rank nothing changes. On the cross through the pawn the count "
        "falls to nine or ten, and the three squares behind it, e1 to e3, are "
        "the worst at nine: the file shuts at once and only the rank is left.",
      strong=[], soft=[], numbers=rook_counts_blocked(), heat=True,
      pieces={ROOK_PAWN: "wP"},
      legend=[("s", "more squares reached"), ("w", "fewer"),
              ("blocked", "e4, where the pawn stands")]),
 dict(id="soft", g="Piece vision", t="f2 and f7, the soft squares",
      c="In the starting position these two squares are defended by the king "
        "and nothing else. Most early tactics against beginners aim here.",
      strong=["f2", "f7"], soft=f7_diags,
      legend=[("s", "f2 and f7"),
              ("w", "the diagonals that attack them")]),
 dict(id="longdiag", g="Piece vision", t="The long diagonals",
      c="a1 to h8 and a8 to h1, eight squares each. A fianchettoed bishop on "
        "b2, g2, b7 or g7 rakes one of them end to end. One diagonal runs on "
        "dark squares, the other on light.",
      strong=["b2", "g7"],
      soft=sorted(set(diag(0, 1, 1, 1)) - {"b2", "g7"}),
      strong2=["g2", "b7"],
      soft2=sorted(set(diag(0, 8, 1, -1)) - {"g2", "b7"}),
      legend=[("s", "fianchetto squares on the dark diagonal: b2 and g7"),
              ("w", "the a1 to h8 long diagonal, all dark squares"),
              ("s2", "fianchetto squares on the light diagonal: g2 and b7"),
              ("w2", "the a8 to h1 long diagonal, all light squares")]),
 dict(id="atkdiag", g="Piece vision", t="The attacking diagonals",
      c="b1 to h7 and b8 to h2. A bishop here points straight at the square "
        "in front of a castled king. This is the Greek gift geometry.",
      strong=["h7", "h2"], soft=atk_diags,
      pieces={"d3": "wB", "h7": "bP"},
      legend=[("s", "h7 and h2, the sacrifice squares"),
              ("w", "the diagonals that reach them")]),
 dict(id="outpost", g="Piece vision", t="Outpost territory",
      c="A knight is strongest on the 5th or 6th rank where no enemy pawn "
        "can chase it away. The c, d, e and f files matter most.",
      strong=frange(2, 5, 5, 6),
      soft=sorted(set(rank(5) + rank(6)) - set(frange(2, 5, 5, 6))),
      legend=[("s", "prime outpost squares: c5 to f6"),
              ("w", "the rest of the 5th and 6th ranks")]),
 dict(id="rook7", g="Piece vision", t="Rook on the 7th",
      c="The 7th rank is where a rook attacks pawns that have not moved and "
        "traps the king on its back rank. Two rooks there usually decide the "
        "game.",
      strong=rank(7), soft=rank(8),
      pieces={"d7": "wR", "g8": "bK", "a7": "bP", "b7": "bP", "f7": "bP"},
      legend=[("s", "the 7th rank, where the pawns still sit"),
              ("w", "the 8th rank, where the king is confined")]),
 dict(id="square", g="Endgame rules", t="The rule of the square",
      c="Draw the square whose corners are the pawn and its promotion "
        "square. If the defending king is inside it, or can step inside, it "
        "catches the pawn.",
      strong=frange(2, 5, 5, 8), soft=[],
      pieces={"c5": "wP", "g5": "bK"},
      legend=[("s", "the square of the c5 pawn: c5 to f8")],
      notes=["White to move queens. Black to move plays Kf6, steps inside, "
             "and catches it.",
             "Count from the 3rd rank for a pawn still on its 2nd, since it "
             "can move two."]),
 dict(id="opposition", g="Endgame rules", t="The opposition",
      c="Kings on the same file with one square between them. Whoever is to "
        "move must step aside, so having the opposition means NOT being to "
        "move.",
      strong=["e6"], soft=["d5", "f5", "d6", "f6", "d7", "f7"],
      pieces={"e7": "bK", "e5": "wK"},
      legend=[("s", "the square between them"),
              ("w", "squares the king to move is forced onto")]),
 dict(id="keysquares", g="Endgame rules", t="Key squares",
      c="Occupy one with your king and the pawn promotes, whoever is to "
        "move. For a pawn on the 2nd through 4th rank they sit two ranks "
        "ahead.",
      strong=["d6", "e6", "f6"], soft=[],
      pieces={"e4": "wP"},
      legend=[("s", "key squares for the e4 pawn")],
      notes=["Pawn on the 5th or 6th rank: six key squares, on the two ranks "
             "ahead.",
             "Rook pawns are the exception. An h-pawn has only g7 and g8."]),
 dict(id="wrongbishop", g="Endgame rules", t="The wrong bishop",
      c="A rook pawn plus a bishop that cannot control the promotion square "
        "is a draw. The defending king simply sits in the corner.",
      strong=["h8"], soft=["a8", "a1", "h1"],
      pieces={"h8": "bK", "h5": "wP", "f3": "wB"},
      legend=[("s", "h8 is dark, so a light-squared bishop can never touch "
                    "it"),
              ("w", "the other three corners: a1 dark, a8 and h1 light")],
      notes=["So an h-pawn wants a dark-squared bishop, and an a-pawn a "
             "light-squared one."]),
]

def _mate_shade(pieces):
    """Shading for one frame of the two-bishop mate, computed from the
    position.

    soft  = dark-squared bishop's squares (4 diagonal rays, blocked)
    g2    = light-squared bishop's squares
    chk   = the black king's square when a bishop ray hits it
    wk    = squares the white king covers
    bk    = squares the black king can legally move to (green; excludes
            squares attacked by a bishop — x-raying through the king —
            or covered by the white king)
    """
    occ = {p[2]: p[1] for p in pieces}
    pos = {p[0]: p[2] for p in pieces}
    soft, g2, chk, attacked = [], [], [], set()
    for _key, typ, s in pieces:
        if typ != "wB":
            continue
        f, r = FILES.index(s[0]), int(s[1])
        out = soft if (f + r) % 2 == 1 else g2
        for df, dr in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            nf, nr = f + df, r + dr
            behind_king = False
            while 0 <= nf <= 7 and 1 <= nr <= 8:
                s2 = sq(nf, nr)
                attacked.add(s2)
                if not behind_king:
                    if s2 in occ:
                        if occ[s2] == "bK":
                            out.append(s2)
                            chk.append(s2)
                            behind_king = True  # x-ray for legality only
                            nf += df
                            nr += dr
                            continue
                        attacked.discard(s2)  # blocked by a white piece
                        break
                    out.append(s2)
                else:
                    break  # one square past the king is enough here
                nf += df
                nr += dr
    kf, kr = FILES.index(pos["wK"][0]), int(pos["wK"][1])
    wk = [sq(kf + df, kr + dr)
          for df in (-1, 0, 1) for dr in (-1, 0, 1)
          if (df or dr) and 0 <= kf + df <= 7 and 1 <= kr + dr <= 8]
    bf, br = FILES.index(pos["bK"][0]), int(pos["bK"][1])
    bk = [s2 for df in (-1, 0, 1) for dr in (-1, 0, 1)
          if (df or dr) and 0 <= bf + df <= 7 and 1 <= br + dr <= 8
          for s2 in [sq(bf + df, br + dr)]
          if s2 not in occ and s2 not in attacked and s2 not in wk]
    return soft, g2, chk, wk, bk


for _t in TOPICS:
    if _t.get("steps"):
        for _st in _t["steps"]:
            (_st["soft"], _st["g2"], _st["chk"], _st["wk"],
             _st["bk"]) = _mate_shade(_st["pieces"])
            _st["strong"] = []

topics_js = json.dumps(TOPICS, separators=(",", ":"), ensure_ascii=False)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Board Intuition · Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff;
        --sq-light:#a9b2be; --sq-dark:#5a6472;
        --hi-strong:#f09b28; --hi-soft:#f8d692; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
.wrap { max-width:1240px; margin:0 auto; padding:32px 20px 60px; }
header.site { border-top:4px solid var(--accent); padding-top:22px; margin-bottom:26px;
  display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }
.brand { font-weight:700; font-size:20px; letter-spacing:.1em; text-decoration:none; color:var(--text); }
.brand:hover { color:var(--accent); }
nav.site a { color:var(--muted); text-decoration:none; font-size:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 6px; font-size:26px; }
.lede { color:var(--muted); font-size:14.5px; margin:0 0 18px; max-width:760px; }
.stage { display:flex; gap:26px; align-items:flex-start; }
.menu { flex:0 0 230px; }
.menu h3 { font-size:11.5px; letter-spacing:.14em; text-transform:uppercase;
  color:var(--muted); margin:18px 0 6px; font-weight:600; }
.menu h3:first-child { margin-top:0; }
.menu button { display:block; width:100%; text-align:left; background:none;
  border:none; border-left:2px solid transparent; color:var(--muted);
  padding:5px 10px; font-size:14px; cursor:pointer; border-radius:0 6px 6px 0; }
.menu button:hover { color:var(--text); background:#1d1d1d; }
.menu button.here { color:var(--text); border-left-color:var(--hi-strong);
  background:#1f1c16; }
.boardcol { flex:1 1 520px; min-width:0; max-width:620px; }
#board { width:100%; display:block; user-select:none; }
.info { flex:0 0 270px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:16px; }
#tTitle { font-weight:700; font-size:17px; margin:0 0 8px; }
#stepbar { display:flex; align-items:center; gap:10px; margin:2px 0 8px; }
#stepbar button { background:var(--bg); border:1px solid var(--line); color:var(--text);
  padding:4px 12px; border-radius:7px; cursor:pointer; font-size:13px; }
#stepbar button:hover { border-color:var(--hi-strong); }
#sInd { color:var(--muted); font-size:12.5px; }
#stepCap { color:var(--text); font-size:13.5px; line-height:1.55; margin:0 0 12px;
  border-left:2px solid var(--hi-strong); padding-left:10px; }
#tCap { color:var(--muted); font-size:13.5px; line-height:1.55; margin:0 0 12px; }
.legend div { display:flex; gap:8px; align-items:flex-start; font-size:12.5px;
  color:var(--muted); margin-top:6px; }
.legend span.swb { flex:0 0 12px; height:12px; border-radius:3px; margin-top:4px; }
#tNotes { margin:12px 0 0; padding:10px 0 0; border-top:1px solid var(--line);
  font-size:12.5px; color:var(--muted); }
#tNotes p { margin:0 0 6px; }
#sqName { margin-top:12px; padding-top:10px; border-top:1px solid var(--line);
  font-size:13px; color:var(--muted); min-height:1.3em; }
#sqName b { color:var(--hi-strong); font-size:15px; }
.pn { display:flex; gap:8px; margin-top:14px; }
.pn button { background:var(--panel); border:1px solid var(--line); color:var(--text);
  padding:6px 12px; border-radius:8px; cursor:pointer; font-size:13px; }
.pn button:hover { border-color:var(--accent); }
.note { color:var(--muted); font-size:12.5px; margin-top:22px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
@media (max-width:980px){ .stage{flex-wrap:wrap;} .menu{flex:1 1 100%; display:flex;
  flex-wrap:wrap; gap:2px 10px;} .menu h3{width:100%;} .menu button{width:auto;}
  .info{position:static; flex:1 1 100%;} }
/* board squares */
rect.sq { transition: fill .45s ease; }
g.pc text { paint-order: stroke; transition: transform .55s ease; }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="chess.html">&larr; Chess</a></nav>
</header>
<h1>Board Intuition</h1>
<div class="stage">
  <div class="menu" id="menu"></div>
  <div class="boardcol">
    <svg id="board" viewBox="0 0 560 560" xmlns="http://www.w3.org/2000/svg"></svg>
    <div class="pn">
      <button id="prev">&larr; Previous</button>
      <button id="next">Next &rarr;</button>
    </div>
  </div>
  <div class="info"><div class="card">
    <div id="tTitle"></div>
    <p id="tCap"></p>
    <div id="stepbar" style="display:none">
      <button id="sPrev">&#9664;</button>
      <span id="sInd"></span>
      <button id="sNext">&#9654;</button>
    </div>
    <p id="stepCap" style="display:none"></p>
    <div class="legend" id="tLegend"></div>
    <div id="tNotes" style="display:none"></div>
    <div id="sqName"></div>
  </div></div>
</div>
<p class="note">Diagrams of board geography, drawn on the same reference
board. A topic repaints the highlights, a square under the cursor names
itself, and the buttons or the arrow keys move through the set.</p>
<p class="note">After the Board intuition trainer diagrams. The same reference
board underlies every topic; only the paint changes.</p>
</div>
<script>
const TOPICS=__TOPICS__;
const FILESTR='abcdefgh';
const S=64, M=24;  // square size, margin for coordinates
const GLYPH={K:'\\u265A',Q:'\\u265B',R:'\\u265C',B:'\\u265D',N:'\\u265E',P:'\\u265F'};

const svg=document.getElementById('board');
function sqColor(f,r){ return (f+r)%2===1 ? 'dark':'light'; }
function baseFill(f,r){ return (f+r)%2===1 ? getCss('--sq-dark') : getCss('--sq-light'); }
function getCss(v){ return getComputedStyle(document.documentElement).getPropertyValue(v).trim(); }

// mix two hex colors
function mix(a,b,t){
  const pa=[1,3,5].map(i=>parseInt(a.slice(i,i+2),16));
  const pb=[1,3,5].map(i=>parseInt(b.slice(i,i+2),16));
  return '#'+pa.map((v,i)=>Math.round(v+(pb[i]-v)*t).toString(16).padStart(2,'0')).join('');
}

function build(){
  let s='';
  s+=`<rect x="${M-4}" y="${M-4}" width="${8*S+8}" height="${8*S+8}" rx="6" fill="#0d0d0d" stroke="#333"/>`;
  for(let f=0;f<8;f++) for(let r=1;r<=8;r++){
    const x=M+f*S, y=M+(8-r)*S;
    s+=`<rect class="sq" id="sq-${FILESTR[f]}${r}" x="${x}" y="${y}" width="${S}" height="${S}"
      fill="${baseFill(f,r)}" data-f="${f}" data-r="${r}"/>`;
  }
  // corner coordinate labels inside squares (like the PDF)
  for(let f=0;f<8;f++) for(let r=1;r<=8;r++){
    const x=M+f*S, y=M+(8-r)*S;
    s+=`<text id="lb-${FILESTR[f]}${r}" x="${x+5}" y="${y+S-6}" font-size="11.5"
      font-weight="600" fill="rgba(0,0,0,0.45)" pointer-events="none">${FILESTR[f]}${r}</text>`;
  }
  s+='<g id="numbers"></g><g id="pieces"></g>';
  svg.innerHTML=s;
}
build();

function fillFor(f,r,topic){
  const name=FILESTR[f]+r;
  const dark=(f+r)%2===1;
  if(topic.numbers){
    const n=topic.numbers[name];
    if(n===undefined) return dark?'#4b515a':'#5d646e';   // the blocking piece
    const lo=Math.min(...Object.values(topic.numbers));
    const hi=Math.max(...Object.values(topic.numbers));
    const t=hi===lo ? 0.6 : (n-lo)/(hi-lo);              // a flat count is flat
    const base=dark?getCss('--sq-dark'):getCss('--sq-light');
    // blend toward strong amber by mobility
    return mix(base, dark?'#e08a18':'#f7b449', 0.15+0.85*t);
  }
  if(topic.chk && topic.chk.includes(name))
    return dark ? '#c94435' : '#e8604e';
  if(topic.strong.includes(name))
    return dark ? '#e08a18' : '#f7a833';
  if(topic.strong2 && topic.strong2.includes(name))
    return dark ? '#3579cf' : '#5aa3f2';
  if(topic.bk && topic.bk.includes(name))
    return dark ? '#4f9160' : '#7dc48f';
  if(topic.soft && topic.soft.includes(name))
    return dark ? '#c9a25e' : '#f3d391';
  if(topic.g2 && topic.g2.includes(name))
    return dark ? '#d9962d' : '#f6bd55';
  if(topic.soft2 && topic.soft2.includes(name))
    return dark ? '#5f83b0' : '#a9c8ec';
  if(topic.wk && topic.wk.includes(name))
    return dark ? '#ab8330' : '#e6c46c';
  return dark?getCss('--sq-dark'):getCss('--sq-light');
}

let cur=0, stepIdx=0;
function pieceList(t,st){
  const src=(st&&st.pieces)||t.pieces;
  if(!src) return [];
  if(Array.isArray(src)) return src;               // [[key,type,square],...]
  return Object.entries(src).map(([name,pc])=>[pc+name,pc,name]);
}
function renderPieces(list){
  const pg=document.getElementById('pieces');
  const seen=new Set();
  for(const [key,pc,name] of list){
    seen.add(key);
    const f=FILESTR.indexOf(name[0]), r=+name[1];
    const x=M+f*S+S/2, y=M+(8-r)*S+S/2+16;
    let el=pg.querySelector(`g[data-k="${key}"]`);
    if(!el){
      pg.insertAdjacentHTML('beforeend',
        `<g class="pc" data-k="${key}"><text x="0" y="0" text-anchor="middle"
          font-size="46" fill="${pc[0]==='w'?'#f4efe2':'#141414'}"
          stroke="${pc[0]==='w'?'#20242c':'#e8e2d2'}" stroke-width="1.6"
          style="transform:translate(${x}px,${y}px)">${GLYPH[pc[1]]}</text></g>`);
    } else {
      el.querySelector('text').style.transform=`translate(${x}px,${y}px)`;
    }
  }
  [...pg.children].forEach(g=>{ if(!seen.has(g.dataset.k)) g.remove(); });
}
function paint(){
  const t=TOPICS[cur];
  const st=t.steps ? t.steps[stepIdx] : null;
  const fillsrc=st ? Object.assign({}, t, st) : t;
  for(let f=0;f<8;f++) for(let r=1;r<=8;r++){
    document.getElementById('sq-'+FILESTR[f]+r).setAttribute('fill', fillFor(f,r,fillsrc));
  }
  // numbers
  const ng=document.getElementById('numbers');
  if(t.numbers){
    let s='';
    for(let f=0;f<8;f++) for(let r=1;r<=8;r++){
      const v=t.numbers[FILESTR[f]+r];
      if(v===undefined) continue;
      const x=M+f*S, y=M+(8-r)*S;
      s+=`<text x="${x+S/2}" y="${y+S/2+9}" text-anchor="middle" font-size="26"
        font-weight="700" fill="rgba(0,0,0,0.72)" pointer-events="none">${v}</text>`;
    }
    ng.innerHTML=s;
  } else ng.innerHTML='';
  renderPieces(pieceList(t,st));
  // step bar
  const sb=document.getElementById('stepbar'), sc=document.getElementById('stepCap');
  if(t.steps){
    sb.style.display='flex'; sc.style.display='block';
    document.getElementById('sInd').textContent=(stepIdx+1)+' / '+t.steps.length;
    sc.textContent=st.c||'';
  } else { sb.style.display='none'; sc.style.display='none'; }
  // panel
  document.getElementById('tTitle').textContent=t.t;
  document.getElementById('tCap').textContent=t.c;
  const SW={s:'#f09b28',w:'#f3d391',s2:'#4f9bf0',w2:'#a9c8ec',
            g2:'#f6bd55',wk:'#e6c46c',bk:'#7dc48f',chk:'#e8604e',blocked:'#5d646e'};
  document.getElementById('tLegend').innerHTML=(t.legend||[]).map(([k,txt])=>
    `<div><span class="swb" style="background:${SW[k]||'#f09b28'}"></span><span>${txt}</span></div>`).join('');
  const nt=document.getElementById('tNotes');
  if(t.notes){ nt.style.display='block'; nt.innerHTML=t.notes.map(n=>`<p>${n}</p>`).join(''); }
  else { nt.style.display='none'; }
  document.querySelectorAll('.menu button').forEach(b=>
    b.classList.toggle('here', b.dataset.i==cur));
}
function show(i){
  cur=(i+TOPICS.length)%TOPICS.length;
  stepIdx=0;
  paint();
}
document.getElementById('sPrev').onclick=()=>{
  const t=TOPICS[cur]; if(!t.steps) return;
  stepIdx=(stepIdx-1+t.steps.length)%t.steps.length; paint();
};
document.getElementById('sNext').onclick=()=>{
  const t=TOPICS[cur]; if(!t.steps) return;
  stepIdx=(stepIdx+1)%t.steps.length; paint();
};

// menu
const menu=document.getElementById('menu');
let lastG=null;
TOPICS.forEach((t,i)=>{
  if(t.g!==lastG){ lastG=t.g;
    const h=document.createElement('h3'); h.textContent=t.g; menu.appendChild(h); }
  const b=document.createElement('button');
  b.textContent=t.t; b.dataset.i=i;
  b.onclick=()=>show(i);
  menu.appendChild(b);
});

document.getElementById('prev').onclick=()=>show(cur-1);
document.getElementById('next').onclick=()=>show(cur+1);
document.addEventListener('keydown',e=>{
  const t=TOPICS[cur];
  if(t.steps){
    if(e.key==='ArrowLeft'){ stepIdx=(stepIdx-1+t.steps.length)%t.steps.length; paint(); }
    if(e.key==='ArrowRight'){ stepIdx=(stepIdx+1)%t.steps.length; paint(); }
  } else {
    if(e.key==='ArrowLeft') show(cur-1);
    if(e.key==='ArrowRight') show(cur+1);
  }
});

// hover square name
svg.addEventListener('pointermove',e=>{
  const el=e.target.closest('rect.sq');
  const out=document.getElementById('sqName');
  if(!el){ out.innerHTML=''; return; }
  const name=FILESTR[+el.dataset.f]+el.dataset.r;
  const t0=TOPICS[cur];
  const t=t0.steps ? Object.assign({}, t0, t0.steps[stepIdx]) : t0;
  let tag='';
  if(t.numbers) tag=' \\u00b7 '+t.numbers[name];
  else if(t.chk && t.chk.includes(name)) tag=' \\u00b7 check';
  else if(t.strong.includes(name)) tag=' \\u00b7 highlighted';
  else if(t.strong2 && t.strong2.includes(name)) tag=' \\u00b7 highlighted (blue)';
  else if(t.bk && t.bk.includes(name)) tag=' \\u00b7 open to the black king';
  else if(t.soft && t.soft.includes(name)) tag=t.g2 ? ' \\u00b7 the dark-squared bishop' : ' \\u00b7 highlighted (light)';
  else if(t.g2 && t.g2.includes(name)) tag=' \\u00b7 the light-squared bishop';
  else if(t.soft2 && t.soft2.includes(name)) tag=' \\u00b7 highlighted (light blue)';
  else if(t.wk && t.wk.includes(name)) tag=' \\u00b7 the white king';
  out.innerHTML='<b>'+name+'</b>'+tag;
});
svg.addEventListener('pointerleave',()=>{document.getElementById('sqName').innerHTML='';});

show(0);
</script>
</body>
</html>
"""

html = HTML.replace("__TOPICS__", topics_js)
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html)} bytes): {len(TOPICS)} topics")
