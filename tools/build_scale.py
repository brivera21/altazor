#!/usr/bin/env python3
"""Generate scale.html, Scale: one line from the Planck length to everything.

Sixty-two decades on one log axis, a factor of ten a step, with forty-odd
measured things placed on it, colored by realm. A lens two decades wide
slides along the line, and whatever falls inside it is drawn below as circles
at true proportion, which is the only way anything on a log line can be seen
at its real size against its neighbors. Two things picked in turn give their
ratio. Each thing the site draws elsewhere links to that page.

Data: tools/scale_data.py.

Usage: python3 build_scale.py
"""

import json
from pathlib import Path

import apa
from scale_data import OBJECTS, REALMS, JUMPS, REFS

OUT = Path(__file__).parent.parent / "scale.html"

NOTE1 = ("One line, sixty-two steps, each step a factor of ten, from the "
         "Planck length at the left to the observable universe at the right. "
         "Every mark is a measured thing, colored by realm. A person stands "
         "a little past the middle: thirty-five steps up from the smallest "
         "length that means anything, twenty-seven down from the whole "
         "universe.")

NOTE2 = ("On a log line nothing is drawn at its size, so a lens three decades "
         "wide slides along it, and whatever falls inside is drawn beneath as "
         "circles in true proportion, the largest filling the panel. Two "
         "marks picked in turn give their ratio in the card, as a power of "
         "ten and in plain multiples. Things the site draws elsewhere link "
         "to their pages.")

METHOD = ("Each length is the diameter unless the card says otherwise: a "
          "distance for the gaps between bodies, a height for the mountain and "
          "the tower, a length for the island, the whale and the bacterium. "
          "Constants are CODATA 2018 and the IAU; the rest are the figures "
          "the Wikipedia article for each thing carries, cited one by one, "
          "since those are the numbers a reader meets next. Rounded things "
          "like a grain of sand or a hair are set at the middle of their "
          "published range. The lens draws circles by diameter, so a whale "
          "and a person appear as discs of those widths, not as their "
          "shapes.")


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


objs = [{"k": k, "n": n, "m": m, "r": r, "what": w, "b": b, "s": s, "link": link}
        for k, n, m, r, w, b, s, link in OBJECTS]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Scale &middot; Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
.wrap { max-width:1320px; margin:0 auto; padding:32px 20px 60px; }
header.site { border-top:4px solid var(--accent); padding-top:22px; margin-bottom:26px;
  display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }
.brand { font-weight:700; font-size:20px; letter-spacing:.1em; text-decoration:none; color:var(--text); }
.brand:hover { color:var(--accent); }
nav.site a { color:var(--muted); text-decoration:none; font-size:14px; margin-right:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 12px; font-size:26px; }
.controls { display:flex; align-items:center; gap:12px; flex-wrap:wrap; margin:0 0 12px; }
.controls label { font-size:13px; color:var(--muted); }
.controls input[type=range] { width:160px; accent-color:var(--accent); }
.controls output { font-size:13px; color:var(--text); font-variant-numeric:tabular-nums; }
.controls output small { color:var(--muted); font-size:11.5px; }
.presets { display:flex; gap:6px; flex-wrap:wrap; }
.presets button { background:var(--panel); color:var(--muted); border:1px solid var(--line);
  border-radius:999px; padding:5px 11px; font-size:12.5px; cursor:pointer; font-family:inherit; }
.presets button:hover { color:var(--text); border-color:#3d3d3d; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; }
#diagram svg { width:100%; height:auto; display:block; user-select:none; touch-action:pan-y; outline:none; border-radius:10px; }
#diagram svg:focus-visible { box-shadow:0 0 0 1px var(--accent); }
.side { flex:0 0 300px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:16px; }
#kindTxt { font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
#nameTxt { font-weight:700; font-size:17px; margin:2px 0 6px; }
#numTxt { font-size:13.5px; line-height:1.55; font-variant-numeric:tabular-nums; }
#numTxt b { color:var(--muted); font-weight:400; }
#bodyTxt { color:var(--muted); font-size:13.5px; line-height:1.55; margin-top:9px; }
#srcTxt { color:var(--muted); font-size:12px; margin-top:10px; border-top:1px solid var(--line); padding-top:8px; }
#srcTxt a { color:var(--accent); }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
details.sources { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
details.sources summary { cursor:pointer; color:var(--accent); }
details.sources p { margin:9px 0 0; }
.refs { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.refs p { margin:0 0 8px; overflow-wrap:anywhere; }
.refs a { color:var(--accent); }
__APACSS__
h2.refh { font-size:15px; margin:26px 0 8px; }
@media (max-width:900px){ .stage{flex-direction:column;} #diagram{flex:none; width:100%;} .side{position:static; width:100%; flex:none; order:-1;} }
@media (max-width:600px){ #diagram{overflow-x:auto;} #diagram svg{min-width:700px;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library &middot; Abstractions</a><a href="prime-spiral.html">The Prime Spiral</a><a href="universe.html">The Universe</a></nav>
</header>
<h1>Scale</h1>
<div class="controls">
  <label for="lensW">the lens spans</label>
  <input type="range" id="lensW" min="10" max="60" step="1" value="30">
  <output id="lensWOut">1,000&times;</output>
  <span class="presets" id="jumps"></span>
</div>
<div class="stage">
  <div id="diagram"></div>
  <div class="side"><div class="card">
    <div id="kindTxt"></div>
    <div id="nameTxt">A mark under the cursor lands here</div>
    <div id="numTxt"></div>
    <div id="bodyTxt"></div>
    <div id="srcTxt"></div>
  </div></div>
</div>
<p class="note">__NOTE1__</p>
<details class="sources"><summary>Sources</summary>
<p>__NOTE2__</p>
<p>__METHOD__</p>
<div class="refs">__REFS__</div>
</details>
</div>
<script>
const OBJ=__OBJ__, REALM=__REALM__, JUMPS=__JUMPS__;
const W=980, H=720, L=40, R=940, Y=190;          // the line
const LOG0=-35, LOG1=27;                          // decades on show
const PANEL={x:30,y:270,w:920,h:420};             // the lens panel
const el=document.getElementById('diagram');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const X=v=>L+(Math.log10(v)-LOG0)/(LOG1-LOG0)*(R-L);   // meters to pixels
const XL=lg=>L+(lg-LOG0)/(LOG1-LOG0)*(R-L);            // log10 meters to pixels
const LX=px=>LOG0+(px-L)/(R-L)*(LOG1-LOG0);            // pixels to log10 meters
let lensC=Math.log10(1.7), lensW=3.0, picks=[], hot=null;
let ghost=null;                                        // the last lens's largest thing, at the size it had
const REDUCED=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const ease=t=>t<0.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
const inLens=o=>Math.abs(Math.log10(o.m)-lensC)<=lensW/2+1e-9;

/* ---- numbers ---- */
const SUP={'-':'⁻','0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'};
const sup=n=>String(n).split('').map(c=>SUP[c]||c).join('');
function sci(v,dp){ let e=Math.floor(Math.log10(v)), m=v/Math.pow(10,e);
  if(m>=9.995){m/=10;e++;} return m.toFixed(dp===undefined?2:dp)+'×10'+sup(e)+' m'; }
// the unit a person would use for a length of this size
const UNITS=[[1e-12,1e-15,'fm'],[1e-9,1e-12,'pm'],[1e-6,1e-9,'nm'],[1e-3,1e-6,'µm'],[1,1e-3,'mm'],
  [1e3,1,'m'],[1e9,1e3,'km'],[1.495978707e11,1e9,'million km'],[9.4607e15,1.495978707e11,'au'],
  [3.0857e19,9.4607e15,'light years'],[3.0857e22,3.0857e19,'kpc'],[3.0857e25,3.0857e22,'Mpc'],[Infinity,9.4607e24,'billion light years']];
function human(v){
  if(v<1e-16) return sci(v,2);
  for(const [lim,u,name] of UNITS) if(v<lim){
    const q=v/u; const txt=q>=100?Math.round(q).toLocaleString('en-US'):q>=10?q.toFixed(1):q.toFixed(2);
    return txt+' '+name;
  }
}
const nice=v=>v>=1e6?sci(v,1).replace(' m',''):v>=100?Math.round(v).toLocaleString('en-US'):v>=10?v.toFixed(1):v.toFixed(2);

/* ---- the card ---- */
function card(kind,name,rows,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').textContent=name;
  document.getElementById('numTxt').innerHTML=rows.map(([k,v])=>'<b>'+esc(k)+'</b> '+v).join('<br>');
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').innerHTML=src;
}
function showOne(o){
  const rows=[['length', sci(o.m)+', '+human(o.m)], ['which is', esc(o.what)]];
  if(o.k!=='human') rows.push(['against a person', ratioTxt(o.m/1.7)]);
  card(REALM[o.r][1], o.n, rows, o.b,
    esc(o.s)+(o.link?' · <a href="'+o.link+'">drawn on this site</a>':''));
}
function ratioTxt(q){
  const lg=Math.log10(q), big=q>=1?q:1/q;
  return (q>=1?'':'1/')+nice(big)+' as '+(q>=1?'large':'large, that is smaller')+', '+Math.abs(lg).toFixed(1)+' decades '+(q>=1?'up':'down');
}
function showPair(a,b){
  const big=a.m>=b.m?a:b, small=a.m>=b.m?b:a, q=big.m/small.m;
  card('Two marks compared', big.n+' and '+small.n,
    [[big.n, sci(big.m)], [small.n, sci(small.m)],
     ['ratio', nice(q)+' to one, 10^'+Math.log10(q).toFixed(2)],
     ['in steps of ten', Math.round(Math.log10(q))+' decades']],
    'The bigger of the two is '+nice(q)+' times the smaller across. Each decade is one step along the line; '+
    'a thousandfold is three steps.', esc(big.s)+'; '+esc(small.s));
}

/* ---- the line ---- */
function lanes(){
  // labels above the line, each dropped to the first lane where it fits
  const order=[...OBJ].map(o=>({o,x:X(o.m)})).sort((a,b)=>a.x-b.x);
  const ends=[], out={};
  for(const {o,x} of order){
    const w=o.n.length*6.3+10, left=Math.max(L-30,Math.min(R-w+30,x-w/2));
    let lane=0; while(ends[lane]!==undefined && ends[lane]>left) lane++;
    ends[lane]=left+w+8; out[o.k]={lane,lx:left+w/2};
  }
  return out;
}
const LANE=lanes(), NLANE=Math.max(...Object.values(LANE).map(l=>l.lane))+1;
function line(){
  let s='';
  // realm bands, faint, along the axis
  s+='<line x1="'+L+'" y1="'+Y+'" x2="'+R+'" y2="'+Y+'" stroke="#3d444d" stroke-width="2"/>';
  for(let e=LOG0;e<=LOG1;e++){
    const x=XL(e), major=e%5===0;
    s+='<line x1="'+x.toFixed(1)+'" y1="'+(Y-(major?7:4))+'" x2="'+x.toFixed(1)+'" y2="'+(Y+(major?7:4))+'" stroke="#3d444d" stroke-width="1"/>';
    if(major) s+='<text x="'+x.toFixed(1)+'" y="'+(Y+22)+'" text-anchor="middle" font-size="10.5" fill="#6b7280">10'+sup(e)+'</text>';
  }
  // the units people use, under the ticks
  for(const [v,lab] of [[1e-9,'nm'],[1e-6,'µm'],[1e-3,'mm'],[1,'m'],[1e3,'km'],[1.496e11,'au'],[9.46e15,'ly'],[3.086e19,'kpc'],[3.086e22,'Mpc']])
    s+='<text x="'+X(v).toFixed(1)+'" y="'+(Y+36)+'" text-anchor="middle" font-size="10" fill="#565656">'+lab+'</text>';
  // the lens
  const x0=XL(lensC-lensW/2), x1=XL(lensC+lensW/2);
  s+='<rect x="'+x0.toFixed(1)+'" y="'+(Y-16-NLANE*14)+'" width="'+(x1-x0).toFixed(1)+'" height="'+(NLANE*14+34)+
     '" fill="#58a6ff" fill-opacity="0.08" stroke="#58a6ff" stroke-opacity="0.55" stroke-width="1" data-lens="1" style="cursor:ew-resize"/>';
  // the marks and their labels
  for(const o of OBJ){
    const x=X(o.m), {lane,lx}=LANE[o.k], ly=Y-16-lane*14, c=REALM[o.r][0];
    const picked=picks.includes(o.k), isHot=hot===o.k, lit=picked||isHot||inLens(o);
    // only the names inside the lens are bright; the rest wait for the pointer
    s+='<g data-k="'+o.k+'" style="cursor:pointer">';
    s+='<line x1="'+x.toFixed(1)+'" y1="'+(ly+3)+'" x2="'+x.toFixed(1)+'" y2="'+(Y-5)+'" stroke="'+c+'" stroke-opacity="'+(lit?0.5:0.18)+'" stroke-width="1"/>';
    s+='<circle cx="'+x.toFixed(1)+'" cy="'+Y+'" r="'+(picked||isHot?5.5:lit?4:3)+'" fill="'+c+'" fill-opacity="'+(lit?1:0.55)+'" stroke="#121212" stroke-width="1.2"/>';
    if(picked) s+='<circle cx="'+x.toFixed(1)+'" cy="'+Y+'" r="9" fill="none" stroke="#f4efe2" stroke-width="1.2"/>';
    s+='<text x="'+lx.toFixed(1)+'" y="'+ly+'" text-anchor="middle" font-size="10.5" fill="'+(picked||isHot?'#f4efe2':c)+'" opacity="'+(lit?1:0.3)+'">'+esc(o.n)+'</text>';
    s+='<rect x="'+(lx-o.n.length*3.2-4).toFixed(1)+'" y="'+(ly-10)+'" width="'+(o.n.length*6.4+8)+'" height="14" fill="transparent"/>';
    s+='<circle cx="'+x.toFixed(1)+'" cy="'+Y+'" r="9" fill="transparent"/></g>';
  }
  // a bracket between two picks
  if(picks.length===2){
    const a=X(OBJ.find(o=>o.k===picks[0]).m), b=X(OBJ.find(o=>o.k===picks[1]).m);
    s+='<path d="M'+Math.min(a,b).toFixed(1)+','+(Y+48)+' v6 H'+Math.max(a,b).toFixed(1)+' v-6" fill="none" stroke="#f4efe2" stroke-width="1.2"/>';
    const q=Math.abs(Math.log10(OBJ.find(o=>o.k===picks[0]).m/OBJ.find(o=>o.k===picks[1]).m));
    s+='<text x="'+((a+b)/2).toFixed(1)+'" y="'+(Y+68)+'" text-anchor="middle" font-size="11" fill="#f4efe2">'+q.toFixed(1)+' decades apart</text>';
  }
  return s;
}

/* ---- the lens panel: what is inside, at true proportion ---- */
function panel(){
  const lo=Math.pow(10,lensC-lensW/2), hi=Math.pow(10,lensC+lensW/2);
  const inside=OBJ.filter(o=>o.m>=lo&&o.m<=hi).sort((a,b)=>b.m-a.m);
  let s='<rect x="'+PANEL.x+'" y="'+PANEL.y+'" width="'+PANEL.w+'" height="'+PANEL.h+'" fill="#171717" stroke="#2b2b2b" rx="8"/>';
  s+='<text x="'+(PANEL.x+14)+'" y="'+(PANEL.y+22)+'" font-size="12" fill="#9a9a9a">inside the lens, '+sci(lo,1)+' to '+sci(hi,1)+', drawn in true proportion</text>';
  if(!inside.length){
    s+='<text x="'+(PANEL.x+PANEL.w/2)+'" y="'+(PANEL.y+PANEL.h/2)+'" text-anchor="middle" font-size="13" fill="#6b7280">nothing measured on this line falls in the window</text>';
    return s;
  }
  const maxD=Math.min(PANEL.h-110, 330), k=maxD/inside[0].m;    // px per meter
  lastK=k; lastBig=inside[0];
  // lay them out left to right, biggest first, each in a slot of its width plus room for a name
  let x=PANEL.x+24; const cy=PANEL.y+34+maxD/2; let tiny=0, ghostDrawn=false;
  for(const o of inside){
    const d=o.m*k, r=Math.max(d/2,0.6), slot=Math.max(d+28, o.n.length*6.4+24);
    if(x+slot>PANEL.x+PANEL.w-10) break;
    const cx=x+slot/2, c=REALM[o.r][0], isHot=hot===o.k;
    // the ghost: the thing that filled the last lens, dashed, at the size it had then
    if(ghost&&ghost.k===o.k&&Math.abs(ghost.d-d)>2){ const gr=Math.min(ghost.d/2, PANEL.h/2-40);
      s+='<circle cx="'+cx.toFixed(1)+'" cy="'+cy.toFixed(1)+'" r="'+gr.toFixed(1)+'" fill="none" stroke="'+c+'" stroke-opacity="0.45" stroke-dasharray="5 4" stroke-width="1.2"/>';
      s+='<text x="'+cx.toFixed(1)+'" y="'+(cy-gr-6).toFixed(1)+'" text-anchor="middle" font-size="10" fill="'+c+'" opacity="0.7">as drawn a moment ago, '+nice(ghost.d/d)+'\u00d7 this</text>'; ghostDrawn=true; }
    s+='<g data-k="'+o.k+'" style="cursor:pointer">';
    s+='<circle cx="'+cx.toFixed(1)+'" cy="'+cy.toFixed(1)+'" r="'+r.toFixed(2)+'" fill="'+c+'" fill-opacity="'+(isHot?0.95:0.75)+'" stroke="'+(isHot?'#f4efe2':c)+'" stroke-width="1"/>';
    if(d<3){ tiny++; s+='<circle cx="'+cx.toFixed(1)+'" cy="'+cy.toFixed(1)+'" r="6" fill="none" stroke="'+c+'" stroke-opacity="0.5" stroke-dasharray="2 2"/>'; }
    s+='<rect x="'+x.toFixed(1)+'" y="'+(PANEL.y+30)+'" width="'+slot.toFixed(1)+'" height="'+(PANEL.h-40)+'" fill="transparent"/>';
    s+='<text x="'+cx.toFixed(1)+'" y="'+(PANEL.y+34+maxD+26)+'" text-anchor="middle" font-size="11" fill="'+(isHot?'#f4efe2':'#cfd6e6')+'">'+esc(o.n)+'</text>';
    s+='<text x="'+cx.toFixed(1)+'" y="'+(PANEL.y+34+maxD+42)+'" text-anchor="middle" font-size="10" fill="#8a94a6">'+human(o.m)+'</text>';
    if(o!==inside[0]) s+='<text x="'+cx.toFixed(1)+'" y="'+(PANEL.y+34+maxD+57)+'" text-anchor="middle" font-size="10" fill="#6b7280">1/'+nice(inside[0].m/o.m)+' of the largest</text>';
    s+='</g>';
    x+=slot;
  }
  if(ghost&&!ghostDrawn&&inside.every(o=>o.k!==ghost.k)&&Math.abs(Math.log10(ghost.m)-lensC)<lensW/2+1.5){ // it has left the lens: the ghost stands at the left edge
    const gr=Math.min(ghost.d/2, PANEL.h/2-40), gx=PANEL.x+PANEL.w-24-gr, c=REALM[ghost.r][0];
    s+='<circle cx="'+gx.toFixed(1)+'" cy="'+cy.toFixed(1)+'" r="'+gr.toFixed(1)+'" fill="none" stroke="'+c+'" stroke-opacity="0.35" stroke-dasharray="5 4" stroke-width="1.2"/>';
    s+='<text x="'+gx.toFixed(1)+'" y="'+(cy-gr-6).toFixed(1)+'" text-anchor="middle" font-size="10" fill="'+c+'" opacity="0.6">'+esc(ghost.n)+', as drawn a moment ago; now outside the lens</text>'; }
  if(tiny) s+='<text x="'+(PANEL.x+PANEL.w-14)+'" y="'+(PANEL.y+PANEL.h-12)+'" text-anchor="end" font-size="10.5" fill="#6b7280">a dashed ring marks a thing too small to draw at this proportion</text>';
  return s;
}
let lastK=null, lastBig=null;
function remember(){ if(lastK&&lastBig) ghost={k:lastBig.k, n:lastBig.n, r:lastBig.r, m:lastBig.m, d:lastBig.m*lastK}; }

/* ---- render and events ---- */
function render(){
  el.innerHTML='<svg viewBox="0 0 '+W+' '+H+'" xmlns="http://www.w3.org/2000/svg" id="ssvg" tabindex="0" role="img" aria-label="One line from the Planck length to the observable universe">'+
    '<rect width="'+W+'" height="'+H+'" fill="#121212"/>'+
    '<text x="'+L+'" y="30" font-size="14" fill="#9a9a9a">Sixty-two decades, a factor of ten a step. The lens slides.</text>'+
    '<text x="'+R+'" y="30" text-anchor="end" font-size="11.5" fill="#6b7280">two marks clicked in turn give their ratio</text>'+
    line()+panel()+'</svg>';
  document.getElementById('lensWOut').innerHTML=Math.round(Math.pow(10,lensW)).toLocaleString('en-US')+'\u00d7 <small>'+lensW.toFixed(1)+' decades</small>';
}
function pick(k){
  const o=OBJ.find(x=>x.k===k); if(!o) return;
  if(picks.includes(k)) picks=picks.filter(p=>p!==k);
  else { picks.push(k); if(picks.length>2) picks=picks.slice(-2); }
  if(picks.length===2) showPair(OBJ.find(x=>x.k===picks[0]),OBJ.find(x=>x.k===picks[1]));
  else showOne(o);
  render();
}
let dragging=false, swallow=false;
function svgX(e){ const r=document.getElementById('ssvg').getBoundingClientRect(); return (e.clientX-r.left)/r.width*W; }
function svgY(e){ const r=document.getElementById('ssvg').getBoundingClientRect(); return (e.clientY-r.top)/r.height*H; }
el.addEventListener('pointerover',e=>{ const g=e.target.closest('[data-k]'); if(g){ hot=g.getAttribute('data-k'); if(picks.length<2) showOne(OBJ.find(o=>o.k===hot)); render(); } });
el.addEventListener('pointerdown',e=>{
  const y=svgY(e);
  if(e.target.closest('[data-lens]') || (y>Y-20 && y<Y+40 && !e.target.closest('[data-k]'))){
    dragging=true; swallow=true; el.setPointerCapture&&el.setPointerCapture(e.pointerId);
    if(glideId){ cancelAnimationFrame(glideId); glideId=null; }
    remember(); setLens(LX(svgX(e))); e.preventDefault();
  }
});
el.addEventListener('pointermove',e=>{ if(dragging) setLens(LX(svgX(e))); });
window.addEventListener('pointerup',()=>{ dragging=false; });
el.addEventListener('click',e=>{ if(swallow){ swallow=false; return; } const g=e.target.closest('[data-k]'); if(g) pick(g.getAttribute('data-k')); });
function setLens(c){ lensC=Math.max(LOG0+lensW/2,Math.min(LOG1-lensW/2,c)); render(); }
// the lens glides to a new center, the circles beneath growing and shrinking on the way
let glideId=null;
function glide(c,done){ const from=lensC, to=Math.max(LOG0+lensW/2,Math.min(LOG1-lensW/2,c));
  remember();
  if(glideId) cancelAnimationFrame(glideId);
  const dur=REDUCED?0:Math.min(1200,400+120*Math.abs(to-from)), t0=performance.now();
  const run=now=>{ const t=dur?Math.min(1,(now-t0)/dur):1; lensC=from+(to-from)*ease(t); render(); if(t<1) glideId=requestAnimationFrame(run); else { glideId=null; if(done) done(); } };
  run(t0); }
document.getElementById('lensW').addEventListener('input',e=>{ lensW=+e.target.value/10; setLens(lensC); });
document.getElementById('jumps').innerHTML=JUMPS.map(([k,l])=>'<button type="button" data-j="'+k+'">'+l+'</button>').join('');
document.getElementById('jumps').addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return;
  const o=OBJ.find(x=>x.k===b.dataset.j); hot=o.k; if(picks.length<2) showOne(o); glide(Math.log10(o.m)); document.getElementById('ssvg').focus({preventScroll:true}); });
// the wheel over the drawing widens or narrows the lens; the arrow keys step it a decade
el.addEventListener('wheel',e=>{ e.preventDefault(); lensW=Math.max(1,Math.min(6,+(lensW+(e.deltaY>0?0.1:-0.1)).toFixed(1)));
  document.getElementById('lensW').value=Math.round(lensW*10); setLens(lensC); },{passive:false});
el.addEventListener('keydown',e=>{ if(e.target.tagName==='INPUT') return;
  if(e.key==='ArrowLeft'||e.key==='ArrowRight'){ e.preventDefault(); glide(Math.round(lensC)+(e.key==='ArrowRight'?1:-1)); }
  else if(e.key==='ArrowUp'||e.key==='ArrowDown'){ e.preventDefault(); lensW=Math.max(1,Math.min(6,+(lensW+(e.key==='ArrowUp'?0.5:-0.5)).toFixed(1))); document.getElementById('lensW').value=Math.round(lensW*10); setLens(lensC); }
  else if(e.key==='Escape'){ picks=[]; ghost=null; render(); showOne(OBJ.find(o=>o.k===(hot||'human'))); } });

render();
showOne(OBJ.find(o=>o.k==='human'));
window.__scale=()=>({n:OBJ.length, lensC, lensW, picks, hot, ghost, gliding:!!glideId,
  labels:Object.fromEntries([...document.querySelectorAll('#ssvg g[data-k]')].filter(g=>g.querySelector('line')).map(g=>[g.dataset.k,+g.querySelector('text').getAttribute('opacity')])),
  inside:OBJ.filter(o=>Math.log10(o.m)>=lensC-lensW/2&&Math.log10(o.m)<=lensC+lensW/2).map(o=>o.k),
  marks:document.querySelectorAll('#ssvg g[data-k]').length});
</script>
</body>
</html>
"""

html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__OBJ__", _js(objs)).replace("__REALM__", _js(REALMS)).replace("__JUMPS__", _js(JUMPS))
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(OBJECTS)} things across "
      f"{__import__('math').log10(OBJECTS[-1][2]/OBJECTS[0][2]):.0f} decades")
