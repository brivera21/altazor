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

ROOT = Path(__file__).resolve().parent.parent


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


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
  document.getElementById('srcTxt').textContent=src||'';
}
__SCRIPT__
</script>
</body>
</html>
"""

METHOD = ("The wording of every step, feature and stage is Brian Rivera's own, from "
          "the sheets he wrote for himself, and nothing here was added to it. Nothing "
          "is stored between visits, so a run starts empty every time the page is "
          "opened.")

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

IMB_SCRIPT = """
const F=__FACTORS__;
const W=980, ROW=42, TOP=74, CX=640, HALF=290;
const H=TOP+F.length*ROW+30;
let sel=0, side=F.map(()=>0);   // -1 them, 0 level, 1 you

const tally=s=>side.filter(v=>v===s).length;

function draw(){
  let s='<svg id="isvg" viewBox="0 0 '+W+' '+H+'" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Ten features of the position, each weighed toward one side or called level">';
  s+='<text x="0" y="18" font-size="12" fill="#9a9a9a">a row leans to the side it favors; the middle band is level</text>';
  s+='<text x="'+(CX-HALF)+'" y="40" text-anchor="middle" font-size="12" fill="#e0684b">them '+tally(-1)+'</text>';
  s+='<text x="'+CX+'" y="40" text-anchor="middle" font-size="12" fill="#9a9a9a">level '+tally(0)+'</text>';
  s+='<text x="'+(CX+HALF)+'" y="40" text-anchor="middle" font-size="12" fill="#58a6ff">you '+tally(1)+'</text>';
  const net=tally(1)-tally(-1), bw=Math.abs(net)/F.length*HALF;
  s+='<rect x="'+(CX-HALF)+'" y="50" width="'+(HALF*2)+'" height="10" rx="5" fill="#20242a"/>';
  if(net) s+='<rect x="'+(net>0?CX:CX-bw).toFixed(1)+'" y="50" width="'+bw.toFixed(1)+'" height="10" rx="5" fill="'+(net>0?'#58a6ff':'#e0684b')+'"/>';
  s+='<line x1="'+CX+'" y1="46" x2="'+CX+'" y2="64" stroke="#e6e6e6" stroke-width="1.5"/>';
  F.forEach((f,i)=>{
    const y=TOP+i*ROW+ROW/2, on=sel===i, v=side[i];
    s+='<g data-f="'+i+'" style="cursor:pointer">';
    s+='<rect x="0" y="'+(y-ROW/2+3)+'" width="'+W+'" height="'+(ROW-6)+'" rx="7" fill="'+(on?'#1d2531':'transparent')+'"/>';
    s+='<circle cx="22" cy="'+y+'" r="13" fill="#20242a" stroke="'+(on?'#58a6ff':'#2b2b2b')+'"/>';
    s+='<text x="22" y="'+(y+5)+'" text-anchor="middle" font-size="14" font-weight="700" fill="'+(on?'#ffffff':'#c8c8c8')+'">'+f[1]+'</text>';
    s+='<text x="44" y="'+(y+5)+'" font-size="13.5" fill="'+(on?'#ffffff':'#c8c8c8')+'">'+esc(f[2])+'</text>';
    // the track, three zones
    s+='<rect x="'+(CX-HALF)+'" y="'+(y-11)+'" width="'+(HALF-40)+'" height="22" rx="5" fill="#181c22" data-set="-1"/>';
    s+='<rect x="'+(CX-40)+'" y="'+(y-11)+'" width="80" height="22" rx="5" fill="#181c22" data-set="0"/>';
    s+='<rect x="'+(CX+40)+'" y="'+(y-11)+'" width="'+(HALF-40)+'" height="22" rx="5" fill="#181c22" data-set="1"/>';
    if(v===0) s+='<rect x="'+(CX-40)+'" y="'+(y-11)+'" width="80" height="22" rx="5" fill="#2b3139" data-set="0"/>';
    else { const w=HALF-40;
      s+='<rect x="'+(v>0?CX+40:CX-HALF).toFixed(1)+'" y="'+(y-11)+'" width="'+w+'" height="22" rx="5" fill="'+(v>0?'#1d3category':'#000')+'"/>'; }
    s+='<line x1="'+CX+'" y1="'+(y-13)+'" x2="'+CX+'" y2="'+(y+13)+'" stroke="#3d434b"/>';
    s+='</g>';
  });
  s+='</svg>';
  document.getElementById('diagram').innerHTML=s;
}
"""

# the imbalance drawing is finicky enough to be worth writing out plainly
IMB_SCRIPT = """
const F=__FACTORS__;
const W=980, ROW=44, TOP=78, CX=650, HALF=300, MID=44;
const H=TOP+F.length*ROW+26;
let sel=0, side=F.map(()=>0);   // -1 them, 0 level, 1 you
const tally=s=>side.filter(v=>v===s).length;
const COLYOU='#58a6ff', COLTHEM='#e0684b';

function draw(){
  const net=tally(1)-tally(-1), bw=Math.abs(net)/F.length*HALF;
  let s='<svg id="isvg" viewBox="0 0 '+W+' '+H+'" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Ten features of the position, each weighed toward one side or called level">';
  s+='<text x="0" y="18" font-size="12" fill="#9a9a9a">each row leans to the side it favors; the middle band is level</text>';
  s+='<text x="'+(CX-HALF+40)+'" y="42" text-anchor="middle" font-size="12" fill="'+COLTHEM+'">them '+tally(-1)+'</text>';
  s+='<text x="'+CX+'" y="42" text-anchor="middle" font-size="12" fill="#9a9a9a">level '+tally(0)+'</text>';
  s+='<text x="'+(CX+HALF-40)+'" y="42" text-anchor="middle" font-size="12" fill="'+COLYOU+'">you '+tally(1)+'</text>';
  s+='<rect x="'+(CX-HALF)+'" y="52" width="'+(HALF*2)+'" height="11" rx="5.5" fill="#20242a"/>';
  if(net) s+='<rect x="'+(net>0?CX:CX-bw).toFixed(1)+'" y="52" width="'+bw.toFixed(1)+'" height="11" rx="5.5" fill="'+(net>0?COLYOU:COLTHEM)+'"/>';
  s+='<line x1="'+CX+'" y1="48" x2="'+CX+'" y2="67" stroke="#e6e6e6" stroke-width="1.5"/>';
  F.forEach((f,i)=>{
    const y=TOP+i*ROW+ROW/2, on=sel===i, v=side[i], w=HALF-MID;
    s+='<g data-f="'+i+'" style="cursor:pointer">';
    s+='<rect x="0" y="'+(y-ROW/2+3)+'" width="'+W+'" height="'+(ROW-6)+'" rx="7" fill="'+(on?'#1d2531':'transparent')+'"/>';
    s+='<circle cx="22" cy="'+y+'" r="13" fill="#20242a" stroke="'+(on?COLYOU:'#2b2b2b')+'"/>';
    s+='<text x="22" y="'+(y+5)+'" text-anchor="middle" font-size="14" font-weight="700" fill="'+(on?'#ffffff':'#c8c8c8')+'">'+f[1]+'</text>';
    s+='<text x="44" y="'+(y+5)+'" font-size="13.5" fill="'+(on?'#ffffff':'#c8c8c8')+'">'+esc(f[2])+'</text>';
    s+='<rect data-set="-1" x="'+(CX-HALF)+'" y="'+(y-12)+'" width="'+w+'" height="24" rx="6" fill="'+(v<0?COLTHEM:'#181c22')+'" opacity="'+(v<0?0.85:1)+'"/>';
    s+='<rect data-set="0" x="'+(CX-MID)+'" y="'+(y-12)+'" width="'+(MID*2)+'" height="24" rx="6" fill="'+(v===0?'#333a44':'#181c22')+'"/>';
    s+='<rect data-set="1" x="'+(CX+MID)+'" y="'+(y-12)+'" width="'+w+'" height="24" rx="6" fill="'+(v>0?COLYOU:'#181c22')+'" opacity="'+(v>0?0.85:1)+'"/>';
    if(v===0) s+='<text x="'+CX+'" y="'+(y+4)+'" text-anchor="middle" font-size="11" fill="#9a9a9a" pointer-events="none">level</text>';
    s+='<line x1="'+CX+'" y1="'+(y-14)+'" x2="'+CX+'" y2="'+(y+14)+'" stroke="#3d434b" pointer-events="none"/>';
    s+='</g>';
  });
  s+='</svg>';
  document.getElementById('diagram').innerHTML=s;
}
function show(){
  const f=F[sel], v=side[sel];
  let rows='';
  f[4].forEach(q=>{ rows+='<div class="q"><p>'+esc(q)+'</p></div>'; });
  rows+='<div class="q"><p style="color:#9a9a9a">this one is '
    +(v>0?'<b style="color:'+COLYOU+'">yours</b>':v<0?'<b style="color:'+COLTHEM+'">theirs</b>':'<b>level</b>')+'</p></div>';
  card(f[1]+' \\u00b7 '+f[2], f[3], rows, '', verdict());
  draw();
}
function joinList(a){ return a.length<2?a.join(''):a.slice(0,-1).join(', ')+' and '+a[a.length-1]; }
function verdict(){
  const y=tally(1), t=tally(-1);
  if(!y&&!t) return 'Nothing weighed yet; all ten sit level.';
  if(y===t) return 'Level overall, '+y+' each way, with '+tally(0)+' still level.';
  const mine=y>t;
  const names=joinList(F.filter((_,i)=>side[i]===(mine?1:-1)).map(f=>f[2]));
  return (mine?'You lead ':'They lead ')+Math.max(y,t)+' to '+Math.min(y,t)+', on '+names+'.';
}
document.getElementById('diagram').addEventListener('click',ev=>{
  const g=ev.target.closest('g[data-f]'); if(!g) return;
  sel=+g.dataset.f;
  const r=ev.target.closest('rect[data-set]');
  if(r) side[sel]=+r.dataset.set;
  show();
});
document.getElementById('resetBtn').addEventListener('click',()=>{ side=F.map(()=>0); sel=0; show(); });
show();
window.__imb=function(q){
  if(q&&q.set){ const [i,v]=q.set; sel=i; side[i]=v; show(); }
  if(q&&q.select!=null){ sel=q.select; show(); }
  if(q&&q.reset){ side=F.map(()=>0); sel=0; show(); }
  return {sel, side:side.slice(), you:tally(1), them:tally(-1), level:tally(0),
    kind:document.getElementById('kindTxt').textContent,
    name:document.getElementById('nameTxt').textContent,
    card:document.getElementById('numTxt').textContent,
    src:document.getElementById('srcTxt').textContent,
    rows:document.querySelectorAll('#isvg g[data-f]').length};
};
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
         tagline="Ten features of a position, weighed one at a time.",
         controls='<span class="lab">A position</span><button id="resetBtn" type="button">Start over</button>',
         extracss="", script=IMB_SCRIPT.replace("__FACTORS__", _js(IMBALANCES)),
         note1=("Initiative, Material, Bishops, Activity, Lines, Attacks, Numbers, "
                "Castling, Endgame, Space: ten things a position can be read for, each "
                "with three questions. A row leans left or right for the side it favors, "
                "or sits in the middle band when it is level."),
         note2=("The bar at the top is the running total of those ten judgments, which "
                "is a reading of the position rather than an engine's number.")),
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
                .replace("__METHOD__", METHOD))
        (ROOT / p["out"]).write_text(html, encoding="utf-8")
        print(f"  {p['out']:22} {len(html):>7,} B")


if __name__ == "__main__":
    print(f"three checklists: {len(SCOUT)} steps, {len(IMBALANCES)} features, "
          f"{len(PLAN)} stages ({sum(len(s[5]) for s in PLAN)} options)")
    build()
