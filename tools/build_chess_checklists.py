#!/usr/bin/env python3
"""Generate the three checklist pages of the Chess section from Brian's
own sheets: scout.html, imbalances.html and plan.html.

Each is the checklist turned into something that works rather than
something that is read. S.C.O.U.T. is a five-step run with a yes or no on
every question and a verdict at the end. I.M.B.A.L.A.N.C.E.S. is a
balance chart: each of the ten features is scored toward one side or
called level, and the chart adds them up. P.L.A.N. builds a plan out of
the choices made at its four stages and writes it out as a sentence.

Data: tools/chess_checklists_data.py, which is his wording.

Usage: python3 build_chess_checklists.py
"""

import json
from pathlib import Path

from chess_checklists_data import SCOUT, IMBALANCES, PLAN, RISKS, REWARDS, PLAN_GOAL
from chess_examples_data import EXAMPLES

ROOT = Path(__file__).resolve().parent.parent


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


def games():
    """Replay each example so the page carries positions, not a chess engine.

    A mistyped or illegal move raises here and stops the build, which is the
    point: nothing reaches the board without having been played out first.
    """
    import chess
    out = {}
    for k, e in EXAMPLES.items():
        b = chess.Board()
        fens, sans, frm, to = [b.fen().split(" ")[0]], [], [], []
        for t in e["moves"].split():
            m = b.parse_san(t)
            sans.append(b.san(m))
            frm.append(chess.square_name(m.from_square))
            to.append(chess.square_name(m.to_square))
            b.push(m)
            fens.append(b.fen().split(" ")[0])
        assert e["key"] in sans, (k, e["key"])
        i = sans.index(e["key"])
        assert ("White" if i % 2 == 0 else "Black") == e["side"], (k, e["side"])
        out[k] = {"w": e["white"], "b": e["black"], "ev": e["event"], "y": e["year"],
                  "nm": e["name"], "key": i, "side": e["side"], "note": e["note"],
                  "src": e["source"], "trunc": e.get("truncated", ""),
                  "mate": b.is_checkmate(),
                  "fens": fens, "sans": sans, "frm": frm, "to": to}
    return out


NAV = ('<nav class="site"><a href="chess.html">&larr; Chess</a>'
       '<a href="scout.html">S.C.O.U.T.</a>'
       '<a href="imbalances.html">I.M.B.A.L.A.N.C.E.S.</a>'
       '<a href="plan.html">P.L.A.N.</a>'
       '<a href="intuition.html">Board Intuition</a></nav>')

SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ &middot; Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; --good:#7cc97a; --bad:#e0684b; }
* { box-sizing:border-box; }
[hidden] { display:none !important; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
.wrap { max-width:1320px; margin:0 auto; padding:32px 20px 60px; }
header.site { border-top:4px solid var(--accent); padding-top:22px; margin-bottom:26px;
  display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }
.brand { font-weight:700; font-size:20px; letter-spacing:.1em; text-decoration:none; color:var(--text); }
.brand:hover { color:var(--accent); }
nav.site a { color:var(--muted); text-decoration:none; font-size:14px; margin-right:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 4px; font-size:26px; }
p.sub2 { margin:0 0 14px; color:var(--muted); font-size:14px; }
.controls { display:flex; gap:8px; flex-wrap:wrap; align-items:center; margin:0 0 12px; }
.controls .lab { font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
#letters { display:inline-flex; gap:4px; }
#letters button { min-width:30px; padding:5px 0; font-weight:600; }
#letters button.on { background:var(--accent); color:#0b1a2b; border-color:var(--accent); }
.controls button { background:var(--panel); color:var(--muted); border:1px solid var(--line);
  border-radius:999px; padding:5px 13px; font-size:13px; cursor:pointer; font-family:inherit; }
.controls button:hover { color:var(--text); border-color:#3d3d3d; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; }
#diagram > svg { width:100%; height:auto; display:block; user-select:none; }
.side { flex:0 0 320px; min-width:0; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:16px; overflow-wrap:anywhere; }
#kindTxt { font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
#nameTxt { font-weight:700; font-size:17px; margin:2px 0 8px; }
#numTxt { font-size:13.5px; line-height:1.55; }
#bodyTxt { color:var(--muted); font-size:13.5px; line-height:1.55; margin-top:10px; }
#srcTxt { color:var(--muted); font-size:12px; margin-top:10px; border-top:1px solid var(--line); padding-top:8px; }
#srcTxt a { color:var(--accent); text-decoration:none; border-bottom:1px solid rgba(88,166,255,0.35); }
#srcTxt a:hover { border-bottom-color:var(--accent); }
.q { border-top:1px solid var(--line); padding:9px 0 2px; }
.q:first-child { border-top:none; padding-top:2px; }
.q p { margin:0 0 6px; font-size:13.5px; }
.q .yn { display:flex; gap:6px; }
.q .yn button { flex:1; background:none; color:var(--muted); border:1px solid var(--line);
  border-radius:7px; padding:4px 0; font-size:12.5px; cursor:pointer; font-family:inherit; }
.q .yn button:hover { color:var(--text); }
.q .yn button.yes.on { background:#22331f; border-color:var(--good); color:var(--good); font-weight:600; }
.q .yn button.no.on { background:#331f1c; border-color:var(--bad); color:var(--bad); font-weight:600; }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.method { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
__EXTRACSS__
@media (max-width:900px){ .stage{flex-direction:column;} .side{position:static; width:100%;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  __NAV__
</header>
<h1>__H1__</h1>
<p class="sub2">__TAGLINE__</p>
<div class="controls">__CONTROLS__</div>
<div class="stage">
  <div id="diagram">__DIAGRAM__</div>
  <div class="side"><div class="card">
    <div id="kindTxt"></div>
    <div id="nameTxt"></div>
    <div id="numTxt"></div>
    <div id="bodyTxt"></div>
    <div id="srcTxt"></div>
  </div></div>
</div>
<p class="note">__NOTE1__</p>
<p class="note" style="border-top:none; padding-top:0;">__NOTE2__</p>
<div class="method"><p>__METHOD__</p></div>
</div>
<script>
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
function card(kind,name,rows,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').textContent=name;
  document.getElementById('numTxt').innerHTML=rows;
  document.getElementById('bodyTxt').textContent=body||'';
  document.getElementById('srcTxt').innerHTML=src||'';
}
__SCRIPT__
</script>
</body>
</html>
"""

METHOD = ("The wording of every step, feature and stage comes from a handwritten "
          "checklist, and nothing here was added to it. Nothing is stored between "
          "visits, so a run starts empty every time the page is opened.")

IMB_METHOD = ("The ten features and their questions come from a handwritten checklist. "
              "The games do not. Each was chosen for the feature its key move turns on, "
              "and every score was replayed with a chess library before it reached the "
              "page, so a mistyped or illegal move stops the build rather than drawing a "
              "wrong position. Four of the ten finish in the recorded mate, which checks "
              "the transcription a second way. Each card links to the article its score "
              "was taken from.")

# ------------------------------------------------------------------ SCOUT

SCOUT_CSS = """
.runbar { height:8px; background:#20242a; border-radius:4px; overflow:hidden; margin:14px 0 0; }
.runbar i { display:block; height:100%; background:var(--good); width:0; transition:width .2s; }
"""

SCOUT_SCRIPT = """
const STEPS=__STEPS__;
const W=980, H=250, R=46;
const X=i=>120+i*(740/(STEPS.length-1));
const Y=104;
let sel=0, ans=STEPS.map(s=>s[4].map(()=>null));

const state=i=>{ const a=ans[i];
  if(a.some(v=>v==='no')) return 'flag';
  if(a.every(v=>v==='yes')) return 'clear';
  return 'open'; };
const cleared=()=>ans.filter((_,i)=>state(i)==='clear').length;
const flagged=()=>ans.filter((_,i)=>state(i)==='flag').length;
const answeredAll=()=>ans.every(a=>a.every(v=>v!==null));

function draw(){
  const COL={open:'#3d434b',clear:'#7cc97a',flag:'#e0684b'};
  let s='<svg id="ssvg" viewBox="0 0 '+W+' '+H+'" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The five steps of the check, in order">';
  for(let i=0;i<STEPS.length-1;i++){
    const x1=X(i)+R+8, x2=X(i+1)-R-8;
    s+='<line x1="'+x1.toFixed(1)+'" y1="'+Y+'" x2="'+x2.toFixed(1)+'" y2="'+Y+'" stroke="#2b2b2b" stroke-width="2"/>';
    s+='<path d="M '+(x2-7).toFixed(1)+' '+(Y-5)+' L '+x2.toFixed(1)+' '+Y+' L '+(x2-7).toFixed(1)+' '+(Y+5)+'" fill="none" stroke="#2b2b2b" stroke-width="2"/>';
  }
  STEPS.forEach((st,i)=>{
    const c=COL[state(i)], on=sel===i, x=X(i);
    s+='<g data-step="'+i+'" style="cursor:pointer">';
    s+='<circle cx="'+x.toFixed(1)+'" cy="'+Y+'" r="'+R+'" fill="'+(on?'#1f242b':'#171a1e')+'" stroke="'+c+'" stroke-width="'+(on?3:2)+'"/>';
    s+='<text x="'+x.toFixed(1)+'" y="'+(Y+11)+'" text-anchor="middle" font-size="30" font-weight="700" fill="'+c+'">'+st[1]+'</text>';
    s+='<text x="'+x.toFixed(1)+'" y="'+(Y+R+24)+'" text-anchor="middle" font-size="13.5" fill="'+(on?'#ffffff':'#c8c8c8')+'">'+esc(st[2])+'</text>';
    const a=ans[i], done=a.filter(v=>v!==null).length;
    s+='<text x="'+x.toFixed(1)+'" y="'+(Y+R+42)+'" text-anchor="middle" font-size="11" fill="#7d7d7d">'+done+' of '+a.length+' answered</text>';
    s+='</g>';
  });
  s+='<text x="0" y="26" font-size="12" fill="#9a9a9a">'+cleared()+' of '+STEPS.length+' cleared'+(flagged()?', '+flagged()+' flagged':'')+'</text>';
  s+='</svg>';
  s+='<div class="runbar"><i style="width:'+(cleared()/STEPS.length*100)+'%"></i></div>';
  document.getElementById('diagram').innerHTML=s;
}

function show(){
  const st=STEPS[sel], a=ans[sel];
  let rows='';
  st[4].forEach((q,j)=>{
    rows+='<div class="q"><p>'+esc(q)+'</p><div class="yn">'
      +'<button class="yes'+(a[j]==='yes'?' on':'')+'" data-q="'+j+'" data-v="yes">Yes</button>'
      +'<button class="no'+(a[j]==='no'?' on':'')+'" data-q="'+j+'" data-v="no">No</button></div></div>';
  });
  const v=state(sel);
  const body = v==='clear' ? 'This step is clear.'
    : v==='flag' ? 'A no here is a reason to look for a different move.'
    : st[3];
  card('Step '+(sel+1)+' of '+STEPS.length, st[2], rows, body, verdict());
  draw();
}
function verdict(){
  if(flagged()) return 'Something is flagged; the move is worth rethinking.';
  if(cleared()===STEPS.length) return 'All five clear. The move stands.';
  if(answeredAll()) return 'Every question answered.';
  return cleared()+' of '+STEPS.length+' cleared so far.';
}
document.getElementById('diagram').addEventListener('click',ev=>{
  const g=ev.target.closest('g[data-step]'); if(!g) return;
  sel=+g.dataset.step; show();
});
function answer(i,j,v){
  sel=i;
  ans[i][j] = ans[i][j]===v ? null : v;
  if(state(i)==='clear' && i<STEPS.length-1){
    const nxt=ans.findIndex((_,k)=>k>i && state(k)==='open');
    if(nxt>-1) sel=nxt;
  }
  show();
}
document.getElementById('numTxt').addEventListener('click',ev=>{
  const b=ev.target.closest('button[data-q]'); if(!b) return;
  answer(sel, +b.dataset.q, b.dataset.v);
});
document.getElementById('resetBtn').addEventListener('click',()=>{
  ans=STEPS.map(s=>s[4].map(()=>null)); sel=0; show();
});
show();
window.__scout=function(q){
  if(q&&q.answer){ const [i,j,v]=q.answer; if(ans[i][j]===v) ans[i][j]=null; answer(i,j,v); }
  if(q&&q.select!=null){ sel=q.select; show(); }
  if(q&&q.reset){ ans=STEPS.map(s=>s[4].map(()=>null)); sel=0; show(); }
  return {sel, cleared:cleared(), flagged:flagged(), states:STEPS.map((_,i)=>state(i)),
    kind:document.getElementById('kindTxt').textContent,
    name:document.getElementById('nameTxt').textContent,
    body:document.getElementById('bodyTxt').textContent,
    src:document.getElementById('srcTxt').textContent,
    nodes:document.querySelectorAll('#ssvg g[data-step]').length,
    buttons:document.querySelectorAll('#numTxt button[data-q]').length};
};
"""

# ------------------------------------------------------------- IMBALANCES

IMB_SCRIPT = r"""
const G=__GAMES__, F=__FACTORS__;
const FILES='abcdefgh';
const S=58, M=20, BW=8*S+2*M;
const GLYPH={k:'♚',q:'♛',r:'♜',b:'♝',n:'♞',p:'♟'};
let sel=F[0][0], ply=G[F[0][0]].key+1;      // open on the position after the key move

const g=()=>G[sel];
function board(fen){
  const rows=fen.split('/'); const sq={};
  rows.forEach((row,ri)=>{ let f=0;
    for(const ch of row){
      if(ch>='1'&&ch<='8') f+=+ch;
      else { sq[FILES[f]+(8-ri)]=ch; f++; }
    }});
  return sq;
}
function drawBoard(){
  const gm=g(), sqs=board(gm.fens[ply]);
  const from=ply>0?gm.frm[ply-1]:null, to=ply>0?gm.to[ply-1]:null;
  let s='<svg viewBox="0 0 '+BW+' '+BW+'" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The position after '+
    (ply?esc(gm.sans[ply-1]):'no moves')+'">';
  s+='<rect x="'+(M-4)+'" y="'+(M-4)+'" width="'+(8*S+8)+'" height="'+(8*S+8)+'" rx="6" fill="#0d0d0d" stroke="#333"/>';
  for(let f=0;f<8;f++) for(let r=1;r<=8;r++){
    const x=M+f*S, y=M+(8-r)*S, dark=(f+r)%2===1, name=FILES[f]+r;
    let fill=dark?'#5a6472':'#a9b2be';
    if(name===from) fill=dark?'#6d7a52':'#9aa871';
    if(name===to)   fill=dark?'#85914f':'#b4bf72';
    s+='<rect x="'+x+'" y="'+y+'" width="'+S+'" height="'+S+'" fill="'+fill+'"/>';
    // coordinates on the outside edges only, the way a printed board carries them
    if(f===0) s+='<text x="'+(M-8)+'" y="'+(y+S/2+4)+'" text-anchor="end" font-size="11" fill="#7c7c7c">'+r+'</text>';
    if(r===1) s+='<text x="'+(x+S/2)+'" y="'+(M+8*S+16)+'" text-anchor="middle" font-size="11" fill="#7c7c7c">'+FILES[f]+'</text>';
  }
  for(const name in sqs){
    const c=sqs[name], white=c===c.toUpperCase();
    const f=FILES.indexOf(name[0]), r=+name[1];
    const x=M+f*S+S/2, y=M+(8-r)*S+S/2;
    s+='<text x="'+x+'" y="'+(y+S*0.33)+'" text-anchor="middle" font-size="'+(S*0.86)+
       '" fill="'+(white?'#f6f6f4':'#15181c')+'" stroke="'+(white?'#15181c':'#000')+
       '" stroke-width="1.1" paint-order="stroke">'+GLYPH[c.toLowerCase()]+'</text>';
  }
  return s+'</svg>';
}
function strip(){
  const gm=g(); let s='';
  for(let i=0;i<gm.sans.length;i++){
    if(i%2===0) s+='<span class="no">'+(i/2+1)+'.</span>';
    s+='<span class="mv'+(i===ply-1?' on':'')+(i===gm.key?' key':'')+'" data-ply="'+(i+1)+'">'+esc(gm.sans[i])+'</span>';
  }
  return s;
}
function draw(){
  const gm=g();
  document.getElementById('diagram').innerHTML=
    '<div class="boardwrap"><div id="board">'+drawBoard()+'</div>'+
    '<div class="movecol"><p class="gamehead"><b>'+esc(gm.w)+'</b> versus <b>'+esc(gm.b)+'</b><br>'+
    esc(gm.ev)+', '+gm.y+(gm.nm?'<br>'+esc(gm.nm):'')+'</p>'+
    '<div class="strip" id="strip">'+strip()+'</div></div></div>';
  const on=document.querySelector('#strip .mv.on'); if(on) on.scrollIntoView({block:'nearest'});
  for(const b of document.querySelectorAll('#letters button')) b.classList.toggle('on', b.dataset.f===sel);
}
function show(){
  const gm=g(), f=F.find(x=>x[0]===sel);
  const at=ply-1, played=at>=0?gm.sans[at]:null;
  let rows='<div class="q"><p><b>'+(gm.key%2===0?Math.floor(gm.key/2)+1+'.':Math.floor(gm.key/2)+1+'...')+
    ' '+esc(gm.sans[gm.key])+'</b> is the move, by '+gm.side+'.</p></div>';
  rows+=f[4].map(q=>'<div class="q"><p style="color:#9a9a9a;font-size:12.5px;margin:0">'+esc(q)+'</p></div>').join('');
  if(played && at!==gm.key)
    rows+='<div class="q"><p style="color:#9a9a9a;font-size:12.5px;margin:0">on the board now: '+
      (at%2===0?Math.floor(at/2)+1+'.':Math.floor(at/2)+1+'...')+' '+esc(played)+'</p></div>';
  card(f[1]+' · '+f[2], f[3], rows, gm.note,
    '<a href="'+gm.src+'">'+esc(gm.nm||gm.ev)+'</a>'+(gm.trunc?' · '+esc(gm.trunc):''));
  draw();
}
document.getElementById('letters').innerHTML=F.map(f=>
  '<button type="button" data-f="'+f[0]+'" title="'+esc(f[2]+': '+f[3])+'">'+f[1]+'</button>').join('');
document.getElementById('letters').addEventListener('click',ev=>{
  const b=ev.target.closest('button[data-f]'); if(!b) return;
  sel=b.dataset.f; ply=g().key+1; show();
});
document.getElementById('diagram').addEventListener('click',ev=>{
  const m=ev.target.closest('.mv'); if(!m) return;
  ply=+m.dataset.ply; show();
});
document.getElementById('prevBtn').addEventListener('click',()=>{ if(ply>0){ply--; show();} });
document.getElementById('nextBtn').addEventListener('click',()=>{ if(ply<g().sans.length){ply++; show();} });
document.getElementById('keyBtn').addEventListener('click',()=>{ ply=g().key+1; show(); });
document.addEventListener('keydown',ev=>{
  if(ev.key==='ArrowLeft'&&ply>0){ply--; show();}
  else if(ev.key==='ArrowRight'&&ply<g().sans.length){ply++; show();}
});
show();
window.__imb=function(q){
  if(q&&q.pick){ sel=q.pick; ply=g().key+1; show(); }
  if(q&&q.ply!=null){ ply=q.ply; show(); }
  const gm=g();
  return {sel, ply, keyPly:gm.key+1, plies:gm.sans.length, side:gm.side, key:gm.sans[gm.key],
    white:gm.w, black:gm.b, year:gm.y, fen:gm.fens[ply], mate:gm.mate,
    kind:document.getElementById('kindTxt').textContent,
    name:document.getElementById('nameTxt').textContent,
    card:document.getElementById('numTxt').textContent,
    body:document.getElementById('bodyTxt').textContent,
    src:document.getElementById('srcTxt').textContent,
    letters:document.querySelectorAll('#letters button').length,
    moves:document.querySelectorAll('#strip .mv').length,
    pieces:document.querySelectorAll('#board text').length-64};
};
"""

IMB_CSS = """
.boardwrap { display:flex; gap:18px; align-items:flex-start; flex-wrap:wrap; }
#board { flex:0 0 clamp(300px,48vw,470px); }
#board svg { width:100%; height:auto; display:block; }
.movecol { flex:1 1 220px; min-width:0; }
.gamehead { font-size:12.5px; color:var(--muted); line-height:1.5; margin:0 0 8px; }
.gamehead b { color:var(--text); font-weight:600; }
.strip { max-height:330px; overflow:auto; font-size:13px; line-height:1.75;
  font-variant-numeric:tabular-nums; }
.strip .mv { display:inline-block; padding:0 5px; border-radius:4px; cursor:pointer;
  color:#c8c8c8; }
.strip .mv:hover { color:#ffffff; background:#20242a; }
.strip .mv.on { background:var(--accent); color:#0b1a2b; font-weight:600; }
.strip .mv.key { box-shadow:inset 0 -2px 0 var(--accent); }
.strip .no { color:var(--muted); padding-left:4px; }
"""

PLAN_CSS = """
.grid { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; }
@media (max-width:1050px){ .grid{ grid-template-columns:repeat(2,1fr);} }
@media (max-width:640px){ .grid{ grid-template-columns:1fr;} }
.stg { background:var(--panel); border:1px solid var(--line); border-radius:11px; padding:12px 13px 14px; }
.stg.on { border-color:var(--accent); }
.stg h3 { margin:0 0 2px; font-size:14px; font-weight:600; }
.stg h3 b { color:var(--accent); font-size:17px; margin-right:6px; }
.stg .lead { color:var(--muted); font-size:11.5px; line-height:1.45; margin:0 0 9px; }
.stg .opt { display:block; width:100%; text-align:left; background:none; color:#c8c8c8;
  border:1px solid var(--line); border-radius:7px; padding:5px 8px; margin:0 0 5px;
  font-size:12.5px; cursor:pointer; font-family:inherit; line-height:1.35; }
.stg .opt:hover { color:var(--text); border-color:#3d3d3d; }
.stg .opt.on { background:#1d2c3f; border-color:var(--accent); color:#ffffff; }
.stg .opt i { display:block; font-style:normal; color:var(--muted); font-size:11px; }
.stg .opt.on i { color:#a9c7e8; }
.out { margin-top:16px; background:#151a21; border:1px solid var(--line); border-left:3px solid var(--accent);
  border-radius:10px; padding:13px 15px; }
.out .lab { font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
.out p { margin:4px 0 0; font-size:14.5px; line-height:1.55; }
"""

PLAN_SCRIPT = """
const ST=__STAGES__, RISKS=__RISKS__, REWARDS=__REWARDS__;
let sel=0, pick=ST.map(s=>[]);

function draw(){
  let s='<div class="grid" id="stages">';
  ST.forEach((st,i)=>{
    s+='<div class="stg'+(sel===i?' on':'')+'" data-stage="'+i+'">';
    s+='<h3><b>'+st[1]+'</b>'+esc(st[2])+'</h3><p class="lead">'+esc(st[3])+'</p>';
    st[5].forEach((o,j)=>{
      s+='<button class="opt'+(pick[i].includes(j)?' on':'')+'" data-stage="'+i+'" data-opt="'+j+'">'
        +esc(o[1])+'<i>'+esc(o[2])+'</i></button>';
    });
    s+='</div>';
  });
  s+='</div>';
  s+='<div class="out"><div class="lab">The plan so far</div><p id="planTxt">'+sentence()+'</p></div>';
  document.getElementById('diagram').innerHTML=s;
}
const names=i=>pick[i].map(j=>ST[i][5][j][1]);
function joinList(a){ return a.length<2?a.join(''):a.slice(0,-1).join(', ')+' and '+a[a.length-1]; }
function sentence(){
  const p=names(0), l=names(1), a=names(2), n=names(3);
  if(!p.length&&!l.length&&!a.length&&!n.length) return 'Nothing pinpointed yet.';
  let out='';
  out += p.length ? 'With '+joinList(p).toLowerCase()+' on the board' : 'With the imbalances still unread';
  out += l.length ? ', attack on the '+l[0].toLowerCase() : ', with no battlefield chosen yet';
  out += a.length ? ', arranging pieces around '+joinList(a).toLowerCase() : '';
  out += '.';
  if(n.length===ST[3][5].length) out+=' Generated, calculated and executed: the plan is ready.';
  else if(n.length) out+=' Still to do: '+joinList(ST[3][5].filter((_,j)=>!pick[3].includes(j)).map(o=>o[1].toLowerCase()))+'.';
  return out;
}
function show(){
  let rows='';
  ST.forEach((st,i)=>{
    const chosen=pick[i].map(j=>st[5][j][1]);
    rows+='<div class="q"><p'+(sel===i?' style="color:#ffffff"':'')+'><b>'+st[1]+'</b> '+esc(st[2])+'</p>'
      +'<p style="color:'+(chosen.length?'#58a6ff':'#7d7d7d')+';font-size:12.5px;margin:0">'
      +(chosen.length?esc(joinList(chosen)):'nothing chosen')+'</p></div>';
  });
  if(sel===3) rows+='<div class="q"><p style="color:#9a9a9a;font-size:12.5px;margin:0">'
    +'<b style="color:#e0684b">Risks</b> '+esc(RISKS)+'<br><b style="color:#7cc97a">Rewards</b> '+esc(REWARDS)+'</p></div>';
  const st=ST[sel];
  card('Stage '+(sel+1)+' of '+ST.length, st[2], rows,
    st[4]==='one' ? 'One battlefield at a time.' : st[4]==='all' ? 'All three, in order.' : 'As many as the position shows.',
    pick.reduce((a,b)=>a+b.length,0)+' chosen across the four stages');
  draw();
}
document.getElementById('diagram').addEventListener('click',ev=>{
  const b=ev.target.closest('button[data-opt]');
  if(b){ const i=+b.dataset.stage, j=+b.dataset.opt;
    sel=i;
    if(ST[i][4]==='one') pick[i] = pick[i][0]===j ? [] : [j];
    else pick[i] = pick[i].includes(j) ? pick[i].filter(x=>x!==j) : pick[i].concat(j).sort((a,b)=>a-b);
    show(); return; }
  const d=ev.target.closest('div[data-stage]');
  if(d){ sel=+d.dataset.stage; show(); }
});
document.getElementById('resetBtn').addEventListener('click',()=>{ pick=ST.map(s=>[]); sel=0; show(); });
show();
window.__plan=function(q){
  if(q&&q.pick){ const [i,j]=q.pick; sel=i;
    if(ST[i][4]==='one') pick[i]=[j]; else if(!pick[i].includes(j)) pick[i]=pick[i].concat(j).sort((a,b)=>a-b);
    show(); }
  if(q&&q.select!=null){ sel=q.select; show(); }
  if(q&&q.reset){ pick=ST.map(s=>[]); sel=0; show(); }
  return {sel, pick:pick.map(a=>a.slice()), sentence:sentence(),
    kind:document.getElementById('kindTxt').textContent,
    name:document.getElementById('nameTxt').textContent,
    card:document.getElementById('numTxt').textContent,
    src:document.getElementById('srcTxt').textContent,
    stages:document.querySelectorAll('#stages .stg').length,
    options:document.querySelectorAll('#stages button[data-opt]').length};
};
"""

PAGES = [
    dict(out="scout.html", title="S.C.O.U.T.", h1="S.C.O.U.T.",
         tagline="Five checks, in order, before a move.",
         controls='<span class="lab">A run</span><button id="resetBtn" type="button">Start over</button>',
         extracss=SCOUT_CSS, script=SCOUT_SCRIPT.replace("__STEPS__", _js(SCOUT)),
         note1=("Safety, Checks, Opponent, Upgrade, Test: the five things worth asking "
                "before a move is played, each with two questions and a yes or no. A step "
                "goes green when both of its questions are yes, and red on a single no, "
                "which is the signal to look at a different move."),
         note2=("The run answers as it goes, moving to the next open step as each one "
                "clears, and the strip beneath the flow fills as it does.")),
    dict(out="imbalances.html", title="I.M.B.A.L.A.N.C.E.S.", h1="I.M.B.A.L.A.N.C.E.S.",
         tagline="Ten features of a position, one played game each.",
         controls=('<span class="lab">Feature</span><span id="letters"></span>'
                   '<button id="prevBtn" type="button">&larr;</button>'
                   '<button id="nextBtn" type="button">&rarr;</button>'
                   '<button id="keyBtn" type="button">The move</button>'),
         extracss=IMB_CSS,
         script=(IMB_SCRIPT.replace("__FACTORS__", _js(IMBALANCES))
                 .replace("__GAMES__", _js(games()))),
         note1=("Initiative, Material, Bishops, Activity, Lines, Attacks, Numbers, "
                "Castling, Endgame, Space: ten features of a position, and for each "
                "one a game where that feature decided it. The board opens at the move "
                "the game turns on, with the two squares of that move marked, and the "
                "score beside it steps back and forward through the whole game."),
         note2=("The games run from Morphy in 1858 to Carlsen in 2021, and five of the "
                "ten are called somebody's Immortal, which is what tends to happen when "
                "one idea gets carried all the way to the end of a game."),
         method=IMB_METHOD),
    dict(out="plan.html", title="P.L.A.N.", h1="P.L.A.N.",
         tagline="Always enter the middlegame with a plan.",
         controls='<span class="lab">A plan</span><button id="resetBtn" type="button">Start over</button>',
         extracss=PLAN_CSS,
         script=(PLAN_SCRIPT.replace("__STAGES__", _js(PLAN))
                 .replace("__RISKS__", _js(RISKS)).replace("__REWARDS__", _js(REWARDS))),
         note1=("Pinpoint the imbalances, Locate where to attack, Arrange your pieces, "
                "Nail your move: four stages, each with its own choices. What is chosen "
                "at one stage narrows what makes sense at the next, and the goal through "
                "all four is " + PLAN_GOAL[0].lower() + PLAN_GOAL[1:-1] + "."),
         note2=("The line under the four stages is the plan those choices add up to, "
                "written out, and it rewrites itself with every choice.")),
]


def build():
    for p in PAGES:
        html = (SHELL.replace("__TITLE__", p["title"]).replace("__NAV__", NAV)
                .replace("__H1__", p["h1"]).replace("__TAGLINE__", p["tagline"])
                .replace("__CONTROLS__", p["controls"]).replace("__DIAGRAM__", "")
                .replace("__EXTRACSS__", p["extracss"]).replace("__SCRIPT__", p["script"])
                .replace("__NOTE1__", p["note1"]).replace("__NOTE2__", p["note2"])
                .replace("__METHOD__", p.get("method", METHOD)))
        (ROOT / p["out"]).write_text(html, encoding="utf-8")
        print(f"  {p['out']:22} {len(html):>7,} B")


if __name__ == "__main__":
    print(f"three checklists: {len(SCOUT)} steps, {len(IMBALANCES)} features, "
          f"{len(PLAN)} stages ({sum(len(s[5]) for s in PLAN)} options)")
    build()
