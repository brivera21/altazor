#!/usr/bin/env python3
"""Generate forces.html, Forces: the four, and how hard things push.

Two views. The four: the strong, electromagnetic, weak and gravitational
forces between two protons, drawn against distance on log-log axes across
nine decades of distance and sixty of force, with the reach of the pion and
the W marked and a marker that reads all four off at any distance. How
hard: one log line of forces in newtons, from gravity inside a hydrogen atom
to the Planck force, each mark colored by which of the four is doing the
pushing.

Data: tools/forces_data.py.

Usage: python3 build_forces.py
"""

import json
from pathlib import Path

import apa
from forces_data import FOUR, PAIRS, PLACES, FORCES, REFS

OUT = Path(__file__).parent.parent / "forces.html"

CAPTION = ("Four forces account for every push and pull. Between two protons "
           "the strong force wins inside a femtometer and fades over the next "
           "few; the weak force reaches a thousandth of that; electromagnetism"
           " and gravity go on forever, thirty-six decades apart. The marker "
           "reads all four at any distance, and the second line asks how hard "
           "things push, in newtons.")

NOTE1 = ("The pair the forces are drawn between can be two protons, an "
         "electron and a proton, or two electrons: electrons feel no strong "
         "force, and gravity between them falls with their masses. The "
         "second line runs ninety decades, from gravity between the proton "
         "and electron of a hydrogen atom to the Planck force, and the "
         "stretch where everyday forces crowd is opened out below it. "
         "Everything a hand can feel is electromagnetism between electrons; "
         "gravity shows only at the two ends, where masses are atoms or "
         "worlds; the strong force appears once, between two quarks, at "
         "sixteen metric tons. A mark clicked on the second line draws its "
         "force as a level across the first, with a ring where each curve "
         "reaches it.")

METHOD = ("Electromagnetism and gravity are Coulomb's and Newton's laws, "
          "gravity's coupling scaled by the two masses for each pair. The "
          "strong and weak forces are drawn as Yukawa forces, alpha times "
          "hbar c over r squared times (1 + r over lambda) times e to the "
          "minus r over lambda, with lambda the reach set by the carrier's "
          "mass: 1.414 fm for the pion, 0.002455 fm for the W. The couplings "
          "are the fine-structure constant 1/137, the weak coupling alpha "
          "over sin squared of the weak mixing angle, about 1/32, a strong "
          "coupling of one at the femtometer scale, and for gravity between "
          "two protons G times the proton mass squared over hbar c, "
          "5.9 times 10 to the minus 39. This is the textbook picture; the "
          "true force between nucleons turns repulsive inside half a "
          "femtometer and is already small by three, where the one-pion "
          "tail drawn here still runs on, and the couplings change with "
          "distance. The weak curve keeps the same schematic coupling for "
          "the pairs with an electron, whose real weak charges differ from "
          "the proton's by factors of order one. The weights on the second "
          "line use 9.81 m per second squared.")


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


four = [{"k": k, "n": n, "c": c, "a": a, "lam": lam, "b": b, "s": s} for k, n, c, a, lam, b, s in FOUR]
places = [{"k": k, "n": n, "m": m, "b": b} for k, n, m, b in PLACES]
pairs = [{"k": k, "n": n, "m1": m1, "m2": m2, "strong": st, "em": em} for k, n, m1, m2, st, em in PAIRS]
forces = [{"k": k, "n": n, "N": N, "f": f, "what": w, "b": b, "s": s} for k, n, N, f, w, b, s in FORCES]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Forces &middot; Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; }
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
h1 { margin:0 0 12px; font-size:26px; }
.toprow { display:flex; gap:10px 26px; flex-wrap:wrap; align-items:center; margin:0 0 12px; }
.toprow .bar, .toprow .controls { margin:0; }
.bar { display:flex; gap:8px; flex-wrap:wrap; margin:0 0 12px; }
.bar button, .presets button { background:var(--panel); color:var(--muted); border:1px solid var(--line);
  border-radius:999px; padding:6px 14px; font-size:13px; cursor:pointer; font-family:inherit; }
.bar button.on { background:var(--accent); color:#0b1a2b; border-color:var(--accent); font-weight:600; }
.bar button:hover, .presets button:hover { color:var(--text); border-color:#3d3d3d; }
.bar button.on:hover { color:#0b1a2b; }
.controls { display:flex; align-items:center; gap:12px; flex-wrap:wrap; margin:0 0 12px; min-height:34px; }
.controls label { font-size:13px; color:var(--muted); }
.controls input[type=range] { width:220px; accent-color:var(--accent); }
.controls output { font-size:13px; color:var(--text); font-variant-numeric:tabular-nums; min-width:70px; }
.controls .play { background:var(--panel); color:var(--text); border:1px solid #3d3d3d; border-radius:8px;
  padding:4px 12px; font-size:12.5px; cursor:pointer; font-family:inherit; min-width:62px; }
.controls .play:hover { border-color:var(--accent); }
.controls .play[aria-pressed=true] { background:var(--accent); color:#0b1a2b; border-color:var(--accent); font-weight:600; }
.presets button.on { background:var(--accent); color:#0b1a2b; border-color:var(--accent); font-weight:600; }
.presets { display:flex; gap:6px; flex-wrap:wrap; }
.presets button { padding:5px 11px; font-size:12.5px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; border-radius:12px; outline:none; }
#diagram:focus-visible { box-shadow:0 0 0 1px var(--accent); }
#diagram svg { width:100%; height:auto; display:block; user-select:none; }
#diagram text.halo { paint-order:stroke; stroke:#121212; stroke-width:3.5px; stroke-linejoin:round; }
.side { flex:0 0 300px; min-width:0; position:sticky; top:16px; }
.card { overflow-wrap:anywhere; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:16px; }
#kindTxt { font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
#nameTxt { font-weight:700; font-size:17px; margin:2px 0 6px; }
#numTxt { font-size:13.5px; line-height:1.55; font-variant-numeric:tabular-nums; }
#numTxt b { color:var(--muted); font-weight:400; }
#bodyTxt { color:var(--muted); font-size:13.5px; line-height:1.55; margin-top:9px; }
#srcTxt { color:var(--muted); font-size:12px; margin-top:10px; border-top:1px solid var(--line); padding-top:8px; }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
details.sources { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
details.sources summary { cursor:pointer; }
details.sources summary:hover { color:var(--text); }
details.sources .note { border-top:none; padding-top:0; margin-top:10px; }
.method { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.refs { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.refs p { margin:0 0 8px; overflow-wrap:anywhere; }
.refs a { color:var(--accent); }
__APACSS__
h2.refh { font-size:15px; margin:26px 0 8px; }
@media (max-width:900px){ .stage{flex-direction:column;} .side{position:static; width:100%; order:-1;}
  #diagram{width:100%; flex-basis:auto;} }
@media (max-width:600px){ #diagram{overflow-x:auto; -webkit-overflow-scrolling:touch;} #diagram svg{min-width:680px;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library &middot; The Universe</a><a href="energy.html">Energy</a><a href="matter.html">Matter</a><a href="light.html">Light</a></nav>
</header>
<h1>Forces</h1>
<div class="toprow"><div class="bar" id="views"><button data-v="four" class="on">The four</button><button data-v="line">How hard</button></div>
<div class="controls" id="pairCtl">
  <label>between</label>
  <span class="presets" id="pairs"></span>
</div></div>
<div class="controls" id="fourCtl">
  <label for="dist">distance</label>
  <input type="range" id="dist" min="-1900" max="-1000" step="1" value="-1500">
  <output id="distOut">1 fm</output>
  <button type="button" class="play" id="play" aria-pressed="false">Play</button>
  <span class="presets" id="places"></span>
</div>
<div class="controls" id="lineCtl" hidden>
  <label>the marker</label><output id="lineOut"></output>
  <span class="presets" id="jumps"></span>
</div>
<div class="stage">
  <div id="diagram" tabindex="0" aria-label="the four forces against distance, or a line of forces in newtons"></div>
  <div class="side"><div class="card">
    <div id="kindTxt"></div>
    <div id="nameTxt"></div>
    <div id="numTxt"></div>
    <div id="bodyTxt"></div>
    <div id="srcTxt"></div>
  </div></div>
</div>
<p class="note">__CAPTION__</p>
<details class="sources"><summary>Sources</summary>
<p class="note">__NOTE1__</p>
<div class="method"><p>__METHOD__</p></div>
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</details>
</div>
<script>
const FOUR=__FOUR__, PAIRS=__PAIRS__, PLACES=__PLACES__, FORCES=__FORCES__;
const hbarc=3.1615267734e-26;                     // J m, CODATA 2018
const g0=9.80665;
const W=980;
const el=document.getElementById('diagram');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const RM=matchMedia('(prefers-reduced-motion: reduce)').matches;
let view='four', r=1e-15, hot=null, pair=PAIRS[0], band=null, n=690;

/* ---- numbers ---- */
function sf(x,n){ if(x===0) return '0'; const d=Math.max(0,n-1-Math.floor(Math.log10(Math.abs(x)))); return x.toLocaleString('en-US',{minimumFractionDigits:0,maximumFractionDigits:Math.min(d,6)}); }
function si(v,unit){ const P=[[1e24,'Y'],[1e21,'Z'],[1e18,'E'],[1e15,'P'],[1e12,'T'],[1e9,'G'],[1e6,'M'],[1e3,'k'],[1,''],[1e-3,'m'],[1e-6,'µ'],[1e-9,'n'],[1e-12,'p'],[1e-15,'f'],[1e-18,'a'],[1e-21,'z'],[1e-24,'y']];
  for(const [s,p] of P) if(v>=s*0.9995) return sf(v/s,3)+' '+p+unit; return sci(v)+' '+unit; }
function sci(v){ if(v===0) return '0'; const e=Math.floor(Math.log10(v)), m=v/Math.pow(10,e); return sf(m,3)+'×10<sup>'+e+'</sup>'; }
function fm(m){ return m>=1e-12?si(m,'m'):sf(m/1e-15,3)+' fm'; }
// the coupling of a force for the pair chosen: gravity scales with the two
// masses, the strong force needs two hadrons, the others keep their coupling
function coupling(f){ if(f.k==='gravity') return f.a*pair.m1*pair.m2; if(f.k==='strong'&&!pair.strong) return 0; return f.a; }
function force(f,rr){ // newtons between the pair
  const a=coupling(f); if(a===0) return 0;
  const base=a*hbarc/(rr*rr); if(f.lam==null) return base; const u=rr/f.lam; return base*(1+u)*Math.exp(-u); }
// the distance at which a force equals N newtons, or null if never in range
function reach(f,N){ const a=coupling(f); if(a===0) return null;
  if(f.lam==null){ const rr=Math.sqrt(a*hbarc/N); return rr>=Math.pow(10,XL0)&&rr<=Math.pow(10,XL1)?rr:null; }
  let lo=XL0, hi=XL1; if(force(f,Math.pow(10,lo))<N||force(f,Math.pow(10,hi))>N) return null;
  for(let i=0;i<60;i++){ const mid=(lo+hi)/2; if(force(f,Math.pow(10,mid))>N) lo=mid; else hi=mid; } return Math.pow(10,(lo+hi)/2); }
function weightWords(N){ const kg=N/g0;
  if(kg<1e-6) return null; if(kg<1e-3) return 'the weight of '+sf(kg*1e6,3)+' milligrams'; if(kg<1) return 'the weight of '+sf(kg*1e3,3)+' grams';
  if(kg<1e3) return 'the weight of '+sf(kg,3)+' kg'; if(kg<1e9) return 'the weight of '+sf(kg/1e3,3)+' metric tons';
  if(kg<1e12) return 'the weight of '+sf(kg/1e9,3)+' million metric tons'; return 'the weight of '+sci(kg)+' kg, on Earth'; }

/* ---- the card ---- */
function card(kind,name,rows,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').innerHTML=name;
  document.getElementById('numTxt').innerHTML=rows.filter(r=>r[1]).map(([k,v])=>'<b>'+esc(k)+'</b> '+v).join('<br>');
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').textContent=src;
}
function showDist(rr){
  const em=force(FOUR.find(f=>f.k==='em'),rr);
  const big=x=>x<1e6?sf(x,3):sci(x);
  const rows=FOUR.map(f=>{ const v=force(f,rr); const rel=v/em;
    if(f.k==='strong'&&!pair.strong) return [f.n,'none: electrons do not feel it'];
    if(v<1e-46) return [f.n,'below 10<sup>-46</sup> N, nothing to speak of']; if(f.k==='em') return [f.n, si(v,'N')+' <span style="color:#9a9a9a">('+pair.em+')</span>'];
    return [f.n, si(v,'N')+' <span style="color:#9a9a9a">('+(rel>=1?big(rel)+'×':'1/'+big(1/rel))+' of electromagnetism)</span>']; });
  const strongest=FOUR.reduce((a,f)=>force(f,rr)>force(a,rr)?f:a,FOUR[0]);
  const pl=PLACES.reduce((a,p)=>Math.abs(Math.log10(p.m/rr))<Math.abs(Math.log10(a.m/rr))?p:a,PLACES[0]);
  card(pair.n.charAt(0).toUpperCase()+pair.n.slice(1)+' apart by', fm(rr), rows,
    'The strongest here is '+strongest.n+'. '+(Math.abs(Math.log10(pl.m/rr))<0.15?'This is about '+pl.n+': '+pl.b+'. ':'')+
    (band?'The level drawn across the plot is '+band.n+', '+si(band.N,'N')+'.':''), '');
}
function showFour(k){ const f=FOUR.find(x=>x.k===k); if(!f) return; const a=coupling(f);
  card('One of the four', esc(f.n), [['coupling', a===0?'none for '+pair.n:a>=0.01?'1/'+sf(1/a,3):sci(a)],['reach', f.lam==null?'no limit':fm(f.lam)],['at 1 fm', force(f,1e-15)<1e-46?'below 10<sup>-46</sup> N, nothing to speak of':si(force(f,1e-15),'N')]], f.b, f.s); }
function showForce(k){ const o=FORCES.find(x=>x.k===k); if(!o) return; const f=FOUR.find(x=>x.k===o.f);
  card('A force', esc(o.n), [['what',esc(o.what)],['size',si(o.N,'N')],['in plain terms',weightWords(o.N)||''],['which of the four',f.n]], o.b, o.s); }
// the marker on the newton line: a force with no name, placed against the marks
function showN(N){ const near=FORCES.reduce((a,o)=>Math.abs(Math.log10(o.N/N))<Math.abs(Math.log10(a.N/N))?o:a,FORCES[0]);
  const ratio=N/near.N, rw=ratio>=1?sf(ratio,2)+' times ':'a '+sf(1/ratio,2)+'th of ';
  card('A force of', si(N,'N'), [['in plain terms',weightWords(N)||'too small to weigh'],['nearest mark',esc(near.n)+', '+si(near.N,'N')+(Math.abs(Math.log10(ratio))<0.02?'':' ('+rw+'it)')]],
    'The marker drags along either line; a click on a mark reads it and draws its force as a level across the four.', ''); }

/* ---- the four ---- */
const P={x:84,y:36,w:850,h:490}, XL0=-19, XL1=-10, YL0=-46, YL1=14;
const PX=m=>P.x+(Math.log10(m)-XL0)/(XL1-XL0)*P.w;
const PY=N=>P.y+P.h-(Math.log10(Math.max(N,1e-300))-YL0)/(YL1-YL0)*P.h;
function four(){
  let s='<rect x="'+P.x+'" y="'+P.y+'" width="'+P.w+'" height="'+P.h+'" fill="none" stroke="#2b2b2b"/>';
  for(let lg=XL0; lg<=XL1; lg++){ const x=PX(Math.pow(10,lg)); s+='<line x1="'+x.toFixed(1)+'" y1="'+(P.y+P.h)+'" x2="'+x.toFixed(1)+'" y2="'+(P.y+P.h+6)+'" stroke="#8a94a6"/><text x="'+x.toFixed(1)+'" y="'+(P.y+P.h+20)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">'+(lg>=-12?si(Math.pow(10,lg),'m'):sf(Math.pow(10,lg+15),1)+' fm')+'</text>'; }
  for(let lg=YL0; lg<=YL1; lg+=10){ const y=PY(Math.pow(10,lg)); s+='<line x1="'+(P.x-6)+'" y1="'+y.toFixed(1)+'" x2="'+P.x+'" y2="'+y.toFixed(1)+'" stroke="#8a94a6"/><text x="'+(P.x-9)+'" y="'+(y+4).toFixed(1)+'" text-anchor="end" font-size="10.5" fill="#9a9a9a">10<tspan dy="-4" font-size="8">'+lg+'</tspan></text>'; }
  s+='<text x="'+(P.x+P.w/2)+'" y="'+(P.y+P.h+40)+'" text-anchor="middle" font-size="11.5" fill="#9a9a9a">distance between '+esc(pair.n)+'</text>';
  s+='<text transform="translate(16,'+(P.y+P.h/2)+') rotate(-90)" text-anchor="middle" font-size="11.5" fill="#9a9a9a">force, newtons</text>';
  // the named distances, their labels stepped down where two sit close
  let lastX=-1e9, lastY=0;
  for(const p of PLACES){ const x=PX(p.m); let y=P.y+12; if(x-lastX<16) y=lastY+115; lastX=x; lastY=y;
    s+='<line x1="'+x.toFixed(1)+'" y1="'+P.y+'" x2="'+x.toFixed(1)+'" y2="'+(P.y+P.h)+'" stroke="#2b2b2b" stroke-dasharray="3 4"/><text class="halo" x="'+(x-4).toFixed(1)+'" y="'+y+'" text-anchor="end" font-size="10.5" fill="#8a94a6" transform="rotate(-90 '+(x-4).toFixed(1)+' '+y+')">'+esc(p.n)+'</text>'; }
  // the level from a mark on the newton line, with a ring where each curve reaches it
  if(band){ const y=PY(band.N); if(y>P.y&&y<P.y+P.h){
    s+='<line x1="'+P.x+'" y1="'+y.toFixed(1)+'" x2="'+(P.x+P.w)+'" y2="'+y.toFixed(1)+'" stroke="#e6e6e6" stroke-dasharray="6 4" opacity="0.6"/>';
    s+='<text class="halo" x="'+(P.x+P.w-6)+'" y="'+(y-5).toFixed(1)+'" text-anchor="end" font-size="10.5" fill="#e6e6e6">'+esc(band.n)+', '+si(band.N,'N')+'</text>';
    for(const f of FOUR){ const rr=reach(f,band.N); if(rr==null) continue; const x=PX(rr);
      s+='<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="6" fill="none" stroke="'+f.c+'" stroke-width="2"/><text class="halo" x="'+x.toFixed(1)+'" y="'+(y+18).toFixed(1)+'" text-anchor="middle" font-size="10" fill="'+f.c+'">'+fm(rr)+'</text>'; } } }
  for(const f of FOUR){ if(coupling(f)===0) continue; let d='', on=false, last=null; for(let lg=XL0; lg<=XL1+1e-9; lg+=0.01){ const m=Math.pow(10,lg), N=force(f,m); if(N<Math.pow(10,YL0)){ on=false; continue; } d+=(on?'L':'M')+PX(m).toFixed(1)+','+PY(N).toFixed(1); on=true; last=m; }
    s+='<g data-f="'+f.k+'" style="cursor:pointer"><path d="'+d+'" fill="none" stroke="'+f.c+'" stroke-width="'+(hot===f.k?3:2)+'" opacity="'+(hot&&hot!==f.k?0.45:1)+'"/><path d="'+d+'" fill="none" stroke="#fff" stroke-opacity="0" stroke-width="12"/></g>';
    // where a short-range force drops off the bottom of the chart, it says so
    if(f.lam!=null&&last!=null&&last<Math.pow(10,XL1)) s+='<text class="halo" x="'+(PX(last)+5).toFixed(1)+'" y="'+(P.y+P.h-8)+'" font-size="9.5" fill="'+f.c+'">below 10<tspan dy="-3" font-size="7">'+YL0+'</tspan><tspan dy="3"> N past '+fm(last)+'</tspan></text>'; }
  // labels at the right edge for the two long-range forces, and beside the drop for the short ones
  for(const f of FOUR){ if(coupling(f)===0) continue; let x,y,anchor='end'; if(f.lam==null){ x=P.x+P.w-6; y=PY(force(f,1e-10))-6; } else { const m=reach(f,1e-20)||f.lam*6; x=PX(m)-7; y=PY(force(f,m))+4; }
    s+='<text class="halo" x="'+x.toFixed(1)+'" y="'+y.toFixed(1)+'" text-anchor="'+anchor+'" font-size="11.5" font-weight="600" fill="'+f.c+'">'+esc(f.n)+'</text>'; }
  const mx=PX(r);
  s+='<g id="marker" style="cursor:ew-resize"><line x1="'+mx.toFixed(1)+'" y1="'+P.y+'" x2="'+mx.toFixed(1)+'" y2="'+(P.y+P.h)+'" stroke="#e6e6e6" stroke-width="1.2" opacity="0.8"/>';
  for(const f of FOUR){ const N=force(f,r); if(N>=Math.pow(10,YL0)) s+='<circle cx="'+mx.toFixed(1)+'" cy="'+PY(N).toFixed(1)+'" r="5" fill="'+f.c+'" stroke="#121212" stroke-width="1.5"/>'; }
  s+='<text class="halo" x="'+mx.toFixed(1)+'" y="'+(P.y-8)+'" text-anchor="middle" font-size="11" font-weight="700" fill="#e6e6e6">'+fm(r)+'</text></g>';
  return {svg:s, h:P.y+P.h+50};
}

/* ---- how hard ---- */
const S={L:40,R:940,Y:120,LOG0:-48,LOG1:45};
const SX=N=>S.L+(Math.log10(N)-S.LOG0)/(S.LOG1-S.LOG0)*(S.R-S.L);
const SN=x=>Math.pow(10,S.LOG0+(x-S.L)/(S.R-S.L)*(S.LOG1-S.LOG0));
// the everyday stretch, opened out on a second line below
const E={L:60,R:920,Y:290,LOG0:-13,LOG1:9};
const EX=N=>E.L+(Math.log10(N)-E.LOG0)/(E.LOG1-E.LOG0)*(E.R-E.L);
const EN=x=>Math.pow(10,E.LOG0+(x-E.L)/(E.R-E.L)*(E.LOG1-E.LOG0));
const inE=N=>Math.log10(N)>=E.LOG0&&Math.log10(N)<=E.LOG1;
function lanes(items,minGap){ const rows=[]; const out=[]; for(const it of items){ let q=0; while(rows[q]!==undefined && it.x-rows[q]<minGap) q++; rows[q]=it.x+it.w; out.push({...it,lane:q}); } return out; }
function dot(o,x,y){ const f=FOUR.find(q=>q.k===o.f);
  return '<circle cx="'+x.toFixed(1)+'" cy="'+y+'" r="11" fill="#fff" fill-opacity="0"/><circle cx="'+x.toFixed(1)+'" cy="'+y+'" r="'+(hot===o.k?6:4.5)+'" fill="'+f.c+'" stroke="#121212" stroke-width="1.5"/>'; }
function line(){
  let s='';
  s+='<line x1="'+S.L+'" y1="'+S.Y+'" x2="'+S.R+'" y2="'+S.Y+'" stroke="#8a94a6" stroke-width="1.5"/>';
  for(let d=S.LOG0; d<=S.LOG1; d++){ const x=SX(Math.pow(10,d)); const big=(d%10===0);
    s+='<line x1="'+x.toFixed(1)+'" y1="'+(S.Y-(big?7:3))+'" x2="'+x.toFixed(1)+'" y2="'+(S.Y+(big?7:3))+'" stroke="#8a94a6"/>';
    if(big) s+='<text x="'+x.toFixed(1)+'" y="'+(S.Y+22)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">10<tspan dy="-4" font-size="8">'+d+'</tspan><tspan dy="4"> N</tspan></text>'; }
  s+='<text x="'+S.L+'" y="'+(S.Y-70)+'" font-size="11" fill="#9a9a9a">ninety-three decades of force; the color says which of the four is pushing</text>';
  let lx=S.L; for(const f of FOUR){ if(f.k==='weak') continue; s+='<rect x="'+lx+'" y="'+(S.Y-58)+'" width="10" height="10" fill="'+f.c+'" rx="2"/><text x="'+(lx+14)+'" y="'+(S.Y-49)+'" font-size="10.5" fill="#9a9a9a">'+esc(f.n)+'</text>'; lx+=f.n.length*6.2+30; }
  // the marks: every one a dot on the long line; the ones outside the
  // everyday stretch are named here, the rest on the opened-out line below
  const outer=lanes(FORCES.filter(o=>!inE(o.N)).map(o=>({...o,x:SX(o.N),w:o.n.length*5.7+10})).sort((a,b)=>a.x-b.x),0);
  for(const o of FORCES.filter(o=>inE(o.N))){ s+='<g data-k="'+o.k+'" style="cursor:pointer">'+dot(o,SX(o.N),S.Y)+'</g>'; }
  for(const o of outer){ const y=S.Y+44+o.lane*17; const flip=o.x+o.w>W-10;
    s+='<g data-k="'+o.k+'" style="cursor:pointer"><line x1="'+o.x.toFixed(1)+'" y1="'+(S.Y+8)+'" x2="'+o.x.toFixed(1)+'" y2="'+(y-4)+'" stroke="'+(hot===o.k?'#e6e6e6':'#3d444d')+'"/>'+dot(o,o.x,S.Y);
    s+='<text x="'+(o.x+(flip?-4:4)).toFixed(1)+'" y="'+(y+4)+'" text-anchor="'+(flip?'end':'start')+'" font-size="10.5" fill="'+(hot===o.k?'#e6e6e6':'#9a9a9a')+'">'+esc(o.n)+'</text></g>'; }
  // the opened-out stretch
  const ex0=SX(Math.pow(10,E.LOG0)), ex1=SX(Math.pow(10,E.LOG1));
  s+='<path d="M'+ex0.toFixed(1)+','+(S.Y+3)+' L'+E.L+','+(E.Y-40)+' L'+E.R+','+(E.Y-40)+' L'+ex1.toFixed(1)+','+(S.Y+3)+' Z" fill="#f4efe2" opacity="0.05"/>';
  s+='<text x="'+E.L+'" y="'+(E.Y-48)+'" font-size="11" fill="#9a9a9a">the everyday stretch, 10<tspan dy="-4" font-size="8">-13</tspan><tspan dy="4"> to 10</tspan><tspan dy="-4" font-size="8">9</tspan><tspan dy="4"> N, opened out</tspan></text>';
  s+='<line x1="'+E.L+'" y1="'+E.Y+'" x2="'+E.R+'" y2="'+E.Y+'" stroke="#8a94a6" stroke-width="1.5"/>';
  for(let d=E.LOG0; d<=E.LOG1; d++){ const x=EX(Math.pow(10,d)); const big=(d%3===0);
    s+='<line x1="'+x.toFixed(1)+'" y1="'+(E.Y-(big?6:3))+'" x2="'+x.toFixed(1)+'" y2="'+(E.Y+(big?6:3))+'" stroke="#8a94a6"/>';
    if(big) s+='<text x="'+x.toFixed(1)+'" y="'+(E.Y+20)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+esc(si(Math.pow(10,d),'N'))+'</text>'; }
  // labels alternate above and below the line, so leaders stay short
  const inner=FORCES.filter(o=>inE(o.N)).map(o=>({...o,x:EX(o.N),w:o.n.length*5.7+10})).sort((a,b)=>a.x-b.x);
  const above=lanes(inner.filter((o,i)=>i%2===1),0), below=lanes(inner.filter((o,i)=>i%2===0),0);
  let maxA=0, maxB=0;
  for(const o of above){ const y=E.Y-30-o.lane*17; maxA=Math.max(maxA,o.lane); const flip=o.x+o.w>W-10;
    s+='<g data-k="'+o.k+'" style="cursor:pointer"><line x1="'+o.x.toFixed(1)+'" y1="'+(E.Y-8)+'" x2="'+o.x.toFixed(1)+'" y2="'+(y+4)+'" stroke="'+(hot===o.k?'#e6e6e6':'#3d444d')+'"/>'+dot(o,o.x,E.Y);
    s+='<text x="'+(o.x+(flip?-4:4)).toFixed(1)+'" y="'+(y+2)+'" text-anchor="'+(flip?'end':'start')+'" font-size="10.5" fill="'+(hot===o.k?'#e6e6e6':'#9a9a9a')+'">'+esc(o.n)+'</text></g>'; }
  for(const o of below){ const y=E.Y+44+o.lane*17; maxB=Math.max(maxB,o.lane); const flip=o.x+o.w>W-10;
    s+='<g data-k="'+o.k+'" style="cursor:pointer"><line x1="'+o.x.toFixed(1)+'" y1="'+(E.Y+8)+'" x2="'+o.x.toFixed(1)+'" y2="'+(y-4)+'" stroke="'+(hot===o.k?'#e6e6e6':'#3d444d')+'"/>'+dot(o,o.x,E.Y);
    s+='<text x="'+(o.x+(flip?-4:4)).toFixed(1)+'" y="'+(y+4)+'" text-anchor="'+(flip?'end':'start')+'" font-size="10.5" fill="'+(hot===o.k?'#e6e6e6':'#9a9a9a')+'">'+esc(o.n)+'</text></g>'; }
  // the marker, on the long line and, when it falls in the stretch, on the opened-out one
  const mx=SX(n);
  s+='<g id="nmark" style="cursor:ew-resize"><line x1="'+mx.toFixed(1)+'" y1="'+(S.Y-14)+'" x2="'+mx.toFixed(1)+'" y2="'+(S.Y+14)+'" stroke="#e6e6e6" stroke-width="1.5"/><circle cx="'+mx.toFixed(1)+'" cy="'+S.Y+'" r="3" fill="#e6e6e6"/>';
  s+='<text class="halo" x="'+mx.toFixed(1)+'" y="'+(S.Y-20)+'" text-anchor="middle" font-size="11" font-weight="700" fill="#e6e6e6">'+esc(si(n,'N'))+'</text>';
  if(inE(n)){ const ex=EX(n); s+='<line x1="'+ex.toFixed(1)+'" y1="'+(E.Y-14)+'" x2="'+ex.toFixed(1)+'" y2="'+(E.Y+14)+'" stroke="#e6e6e6" stroke-width="1.5"/>'; }
  s+='</g>';
  return {svg:s, h:E.Y+44+(maxB+1)*17+30};
}

/* ---- render and wiring ---- */
function render(){
  const q=view==='four'?four():line();
  el.innerHTML='<svg viewBox="0 0 '+W+' '+q.h+'" xmlns="http://www.w3.org/2000/svg" id="fsvg"><rect width="'+W+'" height="'+q.h+'" fill="#121212"/>'+q.svg+'</svg>';
  document.getElementById('fourCtl').hidden=view!=='four'; document.getElementById('pairCtl').hidden=view!=='four'; document.getElementById('lineCtl').hidden=view!=='line';
  document.getElementById('distOut').textContent=fm(r);
  document.getElementById('lineOut').innerHTML=si(n,'N');
  for(const b of document.querySelectorAll('#jumps button')) b.classList.toggle('on',band!==null&&b.dataset.k===band.k);
}
function setView(v){ view=v; hot=null; stopPlay(); for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on',b.dataset.v===v); render(); if(v==='four') showDist(r); else if(band) showForce(band.k); else showN(n); }
function setR(m){ r=Math.max(Math.pow(10,XL0),Math.min(Math.pow(10,XL1),m)); document.getElementById('dist').value=Math.round(Math.log10(r)*100); render(); showDist(r); }
function setN(N){ n=Math.max(Math.pow(10,S.LOG0),Math.min(Math.pow(10,S.LOG1),N)); hot=null; render(); showN(n); }
function setPair(k){ pair=PAIRS.find(p=>p.k===k); for(const b of document.querySelectorAll('#pairs button')) b.classList.toggle('on',b.dataset.k===k); render(); showDist(r); }
document.getElementById('views').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setView(b.dataset.v); });
document.getElementById('dist').addEventListener('input',e=>{ stopPlay(); r=Math.pow(10,+e.target.value/100); render(); showDist(r); });
document.getElementById('places').innerHTML=PLACES.map(p=>'<button type="button" data-m="'+p.m+'">'+esc(p.n)+'</button>').join('');
document.getElementById('places').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b){ stopPlay(); setR(+b.dataset.m); } });
document.getElementById('pairs').innerHTML=PAIRS.map(p=>'<button type="button" data-k="'+p.k+'"'+(p.k===pair.k?' class="on"':'')+'>'+esc(p.n)+'</button>').join('');
document.getElementById('pairs').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setPair(b.dataset.k); });
document.getElementById('jumps').innerHTML=FORCES.filter(o=>['hgrav','hydrogen','apple','quarks','sun','planck'].includes(o.k)).map(o=>'<button type="button" data-k="'+o.k+'">'+esc(o.n)+'</button>').join('');
// a mark clicked, on the line or as a preset, reads it and draws its level across the four; a second click lets go
function pickMark(k){ const o=FORCES.find(x=>x.k===k); band = band&&band.k===k ? null : o; n=o.N; hot=k; render(); showForce(k); }
document.getElementById('jumps').addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; pickMark(b.dataset.k); });
// Play drives the marker outward from the smallest distance, a decade a second
const playBtn=document.getElementById('play');
let playing=null;
function stopPlay(){ if(!playing) return; cancelAnimationFrame(playing.raf); clearTimeout(playing.t); playing=null; playBtn.textContent='Play'; playBtn.setAttribute('aria-pressed','false'); }
playBtn.addEventListener('click',()=>{
  if(playing){ stopPlay(); return; }
  const from = Math.log10(r)>=XL1-0.01 ? XL0 : Math.log10(r);
  playing={raf:0,t:0}; playBtn.textContent='Pause'; playBtn.setAttribute('aria-pressed','true');
  if(RM){ let lg=from; const step=()=>{ if(lg>=XL1){ stopPlay(); return; } lg=Math.min(XL1,Math.floor(lg)+1); setR(Math.pow(10,lg)); playing.t=setTimeout(step,900); }; setR(Math.pow(10,from)); playing.t=setTimeout(step,900); return; }
  const D=1000*(XL1-from), t0=performance.now();
  const tick=now=>{ const u=Math.min(1,(now-t0)/D); setR(Math.pow(10,from+(XL1-from)*u)); if(u<1) playing.raf=requestAnimationFrame(tick); else stopPlay(); };
  playing.raf=requestAnimationFrame(tick);
});
let dragging=null;
const svgPt=e=>{ const svg=document.getElementById('fsvg'), b=svg.getBoundingClientRect(); return [(e.clientX-b.left)/b.width*W,(e.clientY-b.top)/b.height*svg.viewBox.baseVal.height]; };
el.addEventListener('pointerdown',e=>{ const [x,y]=svgPt(e);
  if(view==='four'){ if(x>=P.x&&x<=P.x+P.w&&y>=P.y&&y<=P.y+P.h){ stopPlay(); dragging='r'; setR(Math.pow(10,XL0+(x-P.x)/P.w*(XL1-XL0))); e.preventDefault(); } return; }
  if(e.target.closest('[data-k]')) return;
  if(Math.abs(y-S.Y)<=24&&x>=S.L-6&&x<=S.R+6){ dragging='n'; setN(SN(Math.max(S.L,Math.min(S.R,x)))); e.preventDefault(); }
  else if(Math.abs(y-E.Y)<=24&&x>=E.L-6&&x<=E.R+6){ dragging='e'; setN(EN(Math.max(E.L,Math.min(E.R,x)))); e.preventDefault(); } });
el.addEventListener('pointermove',e=>{ if(!dragging) return; const [x]=svgPt(e);
  if(dragging==='r') setR(Math.pow(10,XL0+Math.max(0,Math.min(1,(x-P.x)/P.w))*(XL1-XL0)));
  else if(dragging==='n') setN(SN(Math.max(S.L,Math.min(S.R,x)))); else setN(EN(Math.max(E.L,Math.min(E.R,x)))); });
window.addEventListener('pointerup',()=>{ dragging=null; });
el.addEventListener('pointerover',e=>{ if(dragging) return; const k=e.target.closest('[data-k]'); if(k){ if(k.getAttribute('data-k')===hot) return; hot=k.getAttribute('data-k'); render(); showForce(hot); return; }
  const f=e.target.closest('[data-f]'); if(f){ if(f.getAttribute('data-f')===hot) return; hot=f.getAttribute('data-f'); render(); showFour(hot); } });
el.addEventListener('pointerleave',()=>{ if(dragging) return; if(view==='four'&&hot){ hot=null; render(); showDist(r); } else if(view==='line'&&hot&&!(band&&band.k===hot)){ hot=null; render(); if(band) showForce(band.k); else showN(n); } });
el.addEventListener('click',e=>{ if(view!=='line') return; const k=e.target.closest('[data-k]'); if(k) pickMark(k.getAttribute('data-k')); });
// the arrow keys step a tenth of a decade, page up and down a whole one, when
// the drawing or the slider has focus; Escape lets go of a mark's level
const KEYS={ArrowRight:0.1,ArrowUp:0.1,ArrowLeft:-0.1,ArrowDown:-0.1,PageUp:1,PageDown:-1};
function nudge(d){ if(view==='four'){ stopPlay(); setR(r*Math.pow(10,d)); } else setN(n*Math.pow(10,d)); }
el.addEventListener('keydown',e=>{ if(e.key==='Escape'&&band){ band=null; hot=null; render(); if(view==='four') showDist(r); else showN(n); return; } if(e.key in KEYS){ e.preventDefault(); nudge(KEYS[e.key]); } });
document.getElementById('dist').addEventListener('keydown',e=>{ if(e.key in KEYS){ e.preventDefault(); nudge(KEYS[e.key]); } });

render(); showDist(r);
window.__forces=(q)=>{ const o={view,r,n,hot,pair:pair.k,band:band&&band.k,playing:!!playing,marks:document.querySelectorAll('#fsvg g[data-k]').length,curves:document.querySelectorAll('#fsvg g[data-f]').length,
  card:document.getElementById('numTxt').innerText, name:document.getElementById('nameTxt').innerText, body:document.getElementById('bodyTxt').innerText,
  marker:(()=>{ const t=document.querySelector('#marker line'); return t?+t.getAttribute('x1'):null; })(),
  nmark:(()=>{ const t=document.querySelector('#nmark line'); return t?+t.getAttribute('x1'):null; })(),
  rings:[...document.querySelectorAll('#fsvg circle[r="6"][fill="none"]')].map(c=>[c.getAttribute('stroke'),+c.getAttribute('cx')]),
  dots:[...document.querySelectorAll('#marker circle')].map(c=>[c.getAttribute('fill'),+c.getAttribute('cy')])};
  if(q&&q.force) o.fv=FOUR.map(f=>force(f,q.force)); if(q&&q.PX!=null) o.px=PX(q.PX); if(q&&q.PY!=null) o.py=PY(q.PY); if(q&&q.SX!=null) o.sx=SX(q.SX); if(q&&q.EX!=null) o.ex=EX(q.EX);
  if(q&&q.weight!=null) o.wv=weightWords(q.weight); if(q&&q.reach) o.rv=FOUR.map(f=>reach(f,q.reach)); return o; };
</script>
</body>
</html>
"""

html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__FOUR__", _js(four)).replace("__PAIRS__", _js(pairs)).replace("__PLACES__", _js(places)).replace("__FORCES__", _js(forces))
        .replace("__CAPTION__", CAPTION).replace("__NOTE1__", NOTE1).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(FOUR)} forces, {len(PAIRS)} pairs, {len(PLACES)} places, {len(FORCES)} marks")
