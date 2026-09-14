#!/usr/bin/env python3
"""Generate rook-endings.html for the Chess section.

Three rook endings that have been worked out exactly, on the same board
and in the same chrome as the rest of the site. Each position steps
forward and back through a fixed line, by the arrows in the card or by
the arrow keys, and a note appears only on the moves that need one.

The board is the one endgames.html uses: an SVG grid, coordinates in the
corner of every square, solid glyphs inked light or dark, and pieces that
slide when the position changes rather than jumping.

Every line here is replayed through a chess engine by
tools/verify_rook_endings.py, which checks that each move is legal from
the position it is played in, that each check mark matches the board, and
that the notation on the page is the notation the engine produces.

Usage: python3 build_rook_endings.py
"""

import json
from pathlib import Path

OUT = Path(__file__).parent.parent / "rook-endings.html"

POSITIONS = [
    dict(
        name='Philidor',
        cap='White to move, and a draw with either side to move.',
        start={'f5': 'K', 'e5': 'P', 'a7': 'R', 'e8': 'k', 'b6': 'r'},
        moves=[
            dict(san='1.e6', a='e5', b='e6',
                 note='White has nothing else. With the black rook on the sixth rank the white king cannot reach e6, f6 or g6, so the pawn has to go forward, and forward is where the king needed to stand.'),
            dict(san='1…Rb1', a='b6', b='b1',
                 note='Now, and only now, the rook drops to the first rank. Doing this a move early would have let the king in.'),
            dict(san='2.Kg6', a='f5', b='g6',
                 note='The king goes looking for cover.'),
            dict(san='2…Rg1+', a='b1', b='g1'),
            dict(san='3.Kf6', a='g6', b='f6'),
            dict(san='3…Rf1+', a='g1', b='f1'),
            dict(san='4.Ke5', a='f6', b='e5'),
            dict(san='4…Re1+', a='f1', b='e1'),
            dict(san='5.Kd6', a='e5', b='d6'),
            dict(san='5…Rd1+', a='e1', b='d1',
                 note='There is no square where the checks stop. Blocking with the rook does not help either: Black trades, and king and pawn against king with the defending king on e8 is a draw.'),
        ]),
    dict(
        name='Lucena',
        cap='White to move and win.',
        start={'b8': 'K', 'b7': 'P', 'c1': 'R', 'd7': 'k', 'a2': 'r'},
        moves=[
            dict(san='1.Rd1+', a='c1', b='d1',
                 note='First push the king one file further away. Going straight for 1.Kc7 instead runs into checks that never end: 1…Rc2+ 2.Kb6 Rb2+ 3.Ka7 Ra2+ and back again.'),
            dict(san='1…Ke7', a='d7', b='e7'),
            dict(san='2.Rd4', a='d1', b='d4',
                 note='The bridge. It looks like a waiting move and it is the entire win.'),
            dict(san='2…Ra1', a='a2', b='a1',
                 note='Black lines up to check from behind.'),
            dict(san='3.Kc7', a='b8', b='c7'),
            dict(san='3…Rc1+', a='a1', b='c1'),
            dict(san='4.Kb6', a='c7', b='b6'),
            dict(san='4…Rb1+', a='c1', b='b1'),
            dict(san='5.Kc6', a='b6', b='c6'),
            dict(san='5…Rc1+', a='b1', b='c1'),
            dict(san='6.Kb5', a='c6', b='b5',
                 note='The king has walked down into the shadow of its own rook.'),
            dict(san='6…Rb1+', a='c1', b='b1'),
            dict(san='7.Rb4', a='d4', b='b4',
                 note='The rook steps in, protected by the king. The checks are finished and the pawn promotes. Taking on b4 only speeds it up.'),
        ]),
    dict(
        name='Vančura',
        cap='White to move. Black holds the draw.',
        start={'b5': 'K', 'a8': 'R', 'a6': 'P', 'g7': 'k', 'f6': 'r'},
        moves=[
            dict(san='1.Kc5', a='b5', b='c5',
                 note='White would like to walk the king to b7, free the rook from in front of its own pawn, and promote. The black rook does not allow the trip.'),
            dict(san='1…Rf5+', a='f6', b='f5'),
            dict(san='2.Kb6', a='c5', b='b6'),
            dict(san='2…Rf6+', a='f5', b='f6'),
            dict(san='3.Kb7', a='b6', b='b7'),
            dict(san='3…Rf7+', a='f6', b='f7'),
            dict(san='4.Kc6', a='b7', b='c6'),
            dict(san='4…Rf6+', a='f7', b='f6',
                 note='Back on the sixth rank, hitting the pawn again. Nothing has changed and nothing can. Pushing a7 does not help either: the rook swings behind the pawn and checks from there, and the white king still finds no shelter.'),
        ]),
]

# The theory behind each position. This is reference material rather than
# a description of the diagram, so it sits in its own block below.
THEORY = [
    ("Philidor, 1777",
     "The defending king stands in front of the pawn and the rook sits on "
     "the sixth rank, which is the third rank counted from the defender's "
     "side. The attacking king cannot cross that rank. Pushing the pawn is "
     "the only way to make progress, and pushing it takes away the shelter "
     "the king was going to need. The rook then drops behind and checks "
     "forever."),
    ("Lucena, 1497",
     "The mirror image. Pawn on the seventh, attacking king in front of it, "
     "defending king cut off. The problem is that the king cannot step aside "
     "without running into checks. The answer is a quiet rook move to the "
     "fourth rank, which does nothing visible and settles everything: the "
     "king walks down toward it and the rook blocks the last check on the "
     "way."),
    ("Vančura, published 1924",
     "Rook pawns break the usual rules, and this is the defense that holds "
     "them. The rook attacks the pawn sideways along the sixth rank rather "
     "than sitting passively in front of it, which keeps checks available. "
     "The king stays on g7 or h7, out of reach of a rook check on the "
     "h-file that would otherwise free the attacking rook from the square "
     "in front of its own pawn."),
]

NOTE1 = ("Rook endings are the most common endings in chess, and nearly all "
         "of them simplify toward a handful of positions that have been "
         "worked out exactly. Three of those are here, each stepping "
         "through one fixed line by the arrows or the arrow keys, with a "
         "note on the moves that need one.")

NOTE2 = ("The usual way of sorting the material is by what is left on the "
         "board: rook against pawns, rook and one pawn against rook, rook "
         "and two pawns against rook, rook and pawns against rook and "
         "pawns, and then double rook endings. The single pawn cases are "
         "the smallest, and they matter out of proportion to how often "
         "they appear, because the bigger positions keep reducing into "
         "them.")

SOON = ("Short side and long side defenses, the f and h pawn pair, and the "
        "four against three on one wing still to come.")

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rook Endings &middot; Altazor</title>
<meta name="description" content="Philidor, Lucena and Vancura, three rook
endings worked out exactly, each steppable move by move.">
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
.brand { font-weight:700; font-size:20px; letter-spacing:.1em; text-decoration:none;
  color:var(--text); }
.brand:hover { color:var(--accent); }
nav.site a { color:var(--muted); text-decoration:none; font-size:14px; margin-right:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 14px; font-size:26px; }
.stage { display:flex; gap:26px; align-items:flex-start; }
.menu { flex:0 0 210px; }
.menu h3 { font-size:11.5px; letter-spacing:.14em; text-transform:uppercase;
  color:var(--muted); margin:0 0 6px; font-weight:600; }
.menu button { display:block; width:100%; text-align:left; background:none;
  border:none; border-left:2px solid transparent; color:var(--muted);
  padding:6px 10px; font-size:14.5px; cursor:pointer; border-radius:0 6px 6px 0; }
.menu button:hover { color:var(--text); background:#1d1d1d; }
.menu button.here { color:var(--text); border-left-color:var(--hi-strong);
  background:#1f1c16; }
.menu button .yr { display:block; font-size:11.5px; color:var(--muted); }
.boardcol { flex:1 1 520px; min-width:0; max-width:620px; }
#board { width:100%; display:block; user-select:none; }
.info { flex:0 0 280px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:16px; }
#pName { font-weight:700; font-size:17px; margin:0 0 4px; }
#pCap { color:var(--muted); font-size:13.5px; line-height:1.55; margin:0 0 12px; }
#stepbar { display:flex; align-items:center; gap:10px; margin:2px 0 10px; }
#stepbar button { background:var(--bg); border:1px solid var(--line); color:var(--text);
  padding:4px 12px; border-radius:7px; cursor:pointer; font-size:13px; }
#stepbar button:hover:not(:disabled) { border-color:var(--hi-strong); }
#stepbar button:disabled { color:#4a4a4a; cursor:default; }
#sInd { color:var(--muted); font-size:12.5px; font-variant-numeric:tabular-nums; }
.moves { display:flex; flex-wrap:wrap; gap:2px 9px; font-size:13.5px;
  margin:0 0 10px; }
.moves span { color:#6d6d6d; cursor:pointer; padding:1px 2px; border-radius:4px; }
.moves span:hover { color:var(--text); }
.moves span.played { color:var(--text); }
.moves span.current { color:var(--hi-strong); font-weight:600; }
#pNote { color:var(--text); font-size:13.5px; line-height:1.55; margin:0;
  border-left:2px solid var(--hi-strong); padding-left:10px; min-height:1.2em; }
#pNote:empty { display:none; }
.note { color:var(--muted); font-size:12.5px; margin-top:24px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.method { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.method summary { cursor:pointer; color:var(--accent); }
.method h3 { font-size:13.5px; color:var(--text); margin:14px 0 4px; }
.method p { margin:0 0 8px; }
rect.sq { transition: fill .3s ease; }
g.pc text { paint-order:stroke; transition: transform .4s ease; }
@media (max-width:980px){
  .stage { flex-wrap:wrap; }
  .menu { flex:1 1 100%; display:flex; flex-wrap:wrap; gap:2px 8px; }
  .menu h3 { width:100%; }
  .menu button { width:auto; border-left:none; border-bottom:2px solid transparent;
    border-radius:6px 6px 0 0; }
  .menu button.here { border-left-color:transparent;
    border-bottom-color:var(--hi-strong); }
  .info { position:static; flex:1 1 100%; }
}
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="chess.html">&larr; Chess</a>
  <a href="endgames.html">Endgames</a>
  <a href="openings.html">Openings</a>
  <a href="intuition.html">Board Intuition</a></nav>
</header>
<h1>Rook Endings</h1>
<div class="stage">
  <div class="menu" id="menu"><h3>Positions</h3></div>
  <div class="boardcol">
    <svg id="board" viewBox="0 0 560 560" xmlns="http://www.w3.org/2000/svg"
      role="img" aria-label="A chessboard showing a rook ending"></svg>
  </div>
  <div class="info"><div class="card">
    <div id="pName"></div>
    <p id="pCap"></p>
    <div id="stepbar">
      <button id="prev" type="button" aria-label="Back">&#9664;</button>
      <span id="sInd"></span>
      <button id="next" type="button" aria-label="Forward">&#9654;</button>
      <button id="reset" type="button">Start over</button>
    </div>
    <div class="moves" id="moves"></div>
    <p id="pNote"></p>
  </div></div>
</div>
<p class="note">__NOTE1__</p>
<p class="note" style="border-top:none; padding-top:0;">__NOTE2__</p>
<p class="note" style="border-top:none; padding-top:0;"><em>__SOON__</em></p>
<div class="method"><details><summary>What each position is</summary>
__THEORY__
</details></div>
</div>
<script>
const POS=__POS__;
const FILESTR='abcdefgh';
const S=64, M=24;                     // square size, margin for coordinates
// one solid glyph set, inked light or dark, so both sides read at any size
const GLYPH={K:'\\u265A',Q:'\\u265B',R:'\\u265C',B:'\\u265D',N:'\\u265E',P:'\\u265F'};
const svg=document.getElementById('board');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
let cur=0, ply=0;

function getCss(v){
  return getComputedStyle(document.documentElement).getPropertyValue(v).trim();
}
// a1 is a dark square, so the parity is odd
function isDark(f,r){ return (f+r)%2===1; }
function baseFill(f,r){ return isDark(f,r)?getCss('--sq-dark'):getCss('--sq-light'); }

function build(){
  let s='';
  s+=`<rect x="${M-4}" y="${M-4}" width="${8*S+8}" height="${8*S+8}" rx="6"
      fill="#0d0d0d" stroke="#333"/>`;
  for(let f=0;f<8;f++) for(let r=1;r<=8;r++){
    const x=M+f*S, y=M+(8-r)*S;
    s+=`<rect class="sq" id="sq-${FILESTR[f]}${r}" x="${x}" y="${y}"
        width="${S}" height="${S}" fill="${baseFill(f,r)}"
        data-square="${FILESTR[f]}${r}"/>`;
  }
  for(let f=0;f<8;f++) for(let r=1;r<=8;r++){
    const x=M+f*S, y=M+(8-r)*S;
    s+=`<text x="${x+5}" y="${y+S-6}" font-size="11.5" font-weight="600"
        fill="rgba(0,0,0,0.45)" pointer-events="none">${FILESTR[f]}${r}</text>`;
  }
  s+='<g id="pieces"></g>';
  svg.innerHTML=s;
}
build();

// the position after n plies, and which squares the last move joined
function stateAt(p,n){
  const s=Object.assign({},p.start);
  let from=null,to=null;
  for(let i=0;i<n;i++){
    const m=p.moves[i];
    delete s[m.b];
    s[m.b]=s[m.a];
    delete s[m.a];
    from=m.a; to=m.b;
  }
  return {sq:s, from:from, to:to};
}

function drawPieces(st){
  const pg=document.getElementById('pieces');
  const seen=new Set();
  // a piece keeps its element as it moves, so the glyph slides instead of
  // blinking from one square to the next
  for(const name in st.sq){
    const pc=st.sq[name];
    const f=FILESTR.indexOf(name[0]), r=+name[1];
    const x=M+f*S+S/2, y=M+(8-r)*S+S/2+16;
    const key=pc+(pc===pc.toUpperCase()?'w':'b');
    let el=pg.querySelector(`g[data-k="${key}"]`);
    if(!el){
      const white=pc===pc.toUpperCase();
      pg.insertAdjacentHTML('beforeend',
        `<g class="pc" data-k="${key}"><text x="0" y="0" text-anchor="middle"
          font-size="46" fill="${white?'#f4efe2':'#141414'}"
          stroke="${white?'#20242c':'#e8e2d2'}" stroke-width="1.6"
          style="transform:translate(${x}px,${y}px)"
          >${GLYPH[pc.toUpperCase()]}</text></g>`);
      el=pg.lastElementChild;
    } else {
      el.querySelector('text').style.transform=`translate(${x}px,${y}px)`;
    }
    el.dataset.square=name;
    seen.add(key);
  }
  [...pg.children].forEach(g=>{ if(!seen.has(g.dataset.k)) g.remove(); });
}

function render(){
  const p=POS[cur], st=stateAt(p,ply);
  for(let f=0;f<8;f++) for(let r=1;r<=8;r++){
    const n=FILESTR[f]+r;
    const el=document.getElementById('sq-'+n);
    const lit = n===st.from || n===st.to;
    el.setAttribute('fill', lit
      ? (isDark(f,r)?'#7a6a3e':'#c8b171')
      : baseFill(f,r));
  }
  drawPieces(st);
  document.getElementById('pName').textContent=p.name;
  document.getElementById('pCap').textContent=p.cap;
  document.getElementById('sInd').textContent=ply+' / '+p.moves.length;
  document.getElementById('prev').disabled = ply===0;
  document.getElementById('next').disabled = ply===p.moves.length;
  document.getElementById('reset').disabled = ply===0;
  document.getElementById('moves').innerHTML=p.moves.map((m,i)=>
    '<span data-i="'+(i+1)+'" class="'+(i+1<ply?'played':i+1===ply?'played current':'')
    +'">'+esc(m.san)+'</span>').join('');
  document.querySelectorAll('#moves span').forEach(el=>{
    el.addEventListener('click',()=>{ ply=+el.dataset.i; render(); });
  });
  const n=ply>0 ? p.moves[ply-1].note : null;
  document.getElementById('pNote').textContent=n||'';
  document.querySelectorAll('#menu button').forEach((b,i)=>
    b.classList.toggle('here', i===cur));
}

const menu=document.getElementById('menu');
POS.forEach(function(p,i){
  const b=document.createElement('button');
  b.type='button';
  b.innerHTML=esc(p.name)+'<span class="yr">'+esc(p.year)+'</span>';
  b.addEventListener('click',function(){ cur=i; ply=0; render(); });
  menu.appendChild(b);
});
document.getElementById('prev').addEventListener('click',()=>{
  if(ply>0){ ply--; render(); } });
document.getElementById('next').addEventListener('click',()=>{
  if(ply<POS[cur].moves.length){ ply++; render(); } });
document.getElementById('reset').addEventListener('click',()=>{
  ply=0; render(); });
document.addEventListener('keydown',function(e){
  if(e.key==='ArrowRight'){ if(ply<POS[cur].moves.length){ ply++; render(); } }
  else if(e.key==='ArrowLeft'){ if(ply>0){ ply--; render(); } }
  else return;
  e.preventDefault();
});
render();
</script>
</body>
</html>
"""

YEARS = {"Philidor": "1777", "Lucena": "1497", "Vančura": "1924"}


def main():
    data = []
    for p in POSITIONS:
        data.append(dict(name=p["name"], year=YEARS[p["name"]], cap=p["cap"],
                         start=p["start"],
                         moves=[dict(san=m["san"], a=m["a"], b=m["b"],
                                     note=m.get("note", ""))
                                for m in p["moves"]]))
    theory = "\n".join(f"<h3>{t}</h3>\n<p>{b}</p>" for t, b in THEORY)
    html = (HTML
            .replace("__NOTE1__", NOTE1)
            .replace("__NOTE2__", NOTE2)
            .replace("__SOON__", SOON)
            .replace("__THEORY__", theory)
            .replace("__POS__", json.dumps(data, ensure_ascii=False,
                                           separators=(",", ":"))))
    OUT.write_text(html, encoding="utf-8")
    print(f"rook-endings.html  {len(data)} positions, "
          f"{sum(len(p['moves']) for p in data)} plies, "
          f"{OUT.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
