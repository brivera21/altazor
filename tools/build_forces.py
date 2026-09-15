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
from forces_data import FOUR, PLACES, FORCES, REFS

OUT = Path(__file__).parent.parent / "forces.html"

NOTE1 = ("Four forces account for everything that pushes or pulls. Between "
         "two protons the strong force wins inside a femtometer and fades "
         "over the next few; the weak force, strong up close, reaches only "
         "a thousandth of that; electromagnetism and gravity go on forever, "
         "falling with the square of the distance, thirty-six decades "
         "apart. The marker reads all four off at any distance.")

NOTE2 = ("The second line asks how hard things push, in newtons, and it "
         "runs ninety decades: from gravity between the proton and electron "
         "of a hydrogen atom to the Planck force. Everything a hand can feel "
         "is electromagnetism between electrons; gravity shows only at the "
         "two ends, where masses are atoms or worlds; the strong force "
         "appears once, between two quarks, at sixteen metric tons.")

METHOD = ("Electromagnetism and gravity are Coulomb's and Newton's laws for "
          "two protons. The strong and weak forces are drawn as Yukawa "
          "forces, alpha times hbar c over r squared times (1 + r over "
          "lambda) times e to the minus r over lambda, with lambda the reach "
          "set by the carrier's mass: 1.414 fm for the pion, 0.002455 fm for "
          "the W. The couplings are the fine-structure constant 1/137, the "
          "weak coupling alpha over sin squared of the weak mixing angle, "
          "about 1/32, a strong coupling of one at the femtometer scale, and "
          "for gravity G times the proton mass squared over hbar c, "
          "5.9 times 10 to the minus 39. This is the textbook picture; the "
          "true force between nucleons turns repulsive inside half a "
          "femtometer and is already small by three, where the one-pion "
          "tail drawn here still runs on, and the couplings change with "
          "distance. The weights on the second line use 9.81 m per second "
          "squared.")


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


four = [{"k": k, "n": n, "c": c, "a": a, "lam": lam, "b": b, "s": s} for k, n, c, a, lam, b, s in FOUR]
places = [{"k": k, "n": n, "m": m, "b": b} for k, n, m, b in PLACES]
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
.presets { display:flex; gap:6px; flex-wrap:wrap; }
.presets button { padding:5px 11px; font-size:12.5px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; }
#diagram svg { width:100%; height:auto; display:block; user-select:none; }
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
.method { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.refs { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.refs p { margin:0 0 8px; overflow-wrap:anywhere; }
.refs a { color:var(--accent); }
__APACSS__
h2.refh { font-size:15px; margin:26px 0 8px; }
@media (max-width:900px){ .stage{flex-direction:column;} .side{position:static; width:100%;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library &middot; The Universe</a><a href="energy.html">Energy</a><a href="matter.html">Matter</a><a href="light.html">Light</a></nav>
</header>
<h1>Forces</h1>
<div class="bar" id="views"><button data-v="four" class="on">The four</button><button data-v="line">How hard</button></div>
<div class="controls" id="fourCtl">
  <label for="dist">distance</label>
  <input type="range" id="dist" min="-1900" max="-1000" step="1" value="-1500">
  <output id="distOut">1 fm</output>
  <span class="presets" id="places"></span>
</div>
<div class="controls" id="lineCtl" hidden>
  <label>the marks</label>
  <span class="presets" id="jumps"></span>
</div>
<div class="stage">
  <div id="diagram"></div>
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
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</div>
<script>
const FOUR=__FOUR__, PLACES=__PLACES__, FORCES=__FORCES__;
const hbarc=3.1615267734e-26;                     // J m, CODATA 2018
const g0=9.80665;
const W=980;
const el=document.getElementById('diagram');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
let view='four', r=1e-15, hot=null;

/* ---- numbers ---- */
function sf(x,n){ if(x===0) return '0'; const d=Math.max(0,n-1-Math.floor(Math.log10(Math.abs(x)))); return x.toLocaleString('en-US',{minimumFractionDigits:0,maximumFractionDigits:Math.min(d,6)}); }
function si(v,unit){ const P=[[1e24,'Y'],[1e21,'Z'],[1e18,'E'],[1e15,'P'],[1e12,'T'],[1e9,'G'],[1e6,'M'],[1e3,'k'],[1,''],[1e-3,'m'],[1e-6,'\\u00b5'],[1e-9,'n'],[1e-12,'p'],[1e-15,'f'],[1e-18,'a'],[1e-21,'z'],[1e-24,'y']];
  for(const [s,p] of P) if(v>=s*0.9995) return sf(v/s,3)+' '+p+unit; return sci(v)+' '+unit; }
function sci(v){ if(v===0) return '0'; const e=Math.floor(Math.log10(v)), m=v/Math.pow(10,e); return sf(m,3)+'\\u00d710<sup>'+e+'</sup>'; }
function fm(m){ return m>=1e-12?si(m,'m'):sf(m/1e-15,3)+' fm'; }
function force(f,rr){ // newtons between two protons
  const base=f.a*hbarc/(rr*rr); if(f.lam==null) return base; const u=rr/f.lam; return base*(1+u)*Math.exp(-u); }
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
  const rows=FOUR.map(f=>{ const v=force(f,rr); const rel=v/em; if(v<1e-46) return [f.n,'below 10<sup>-46</sup> N, nothing to speak of']; if(f.k==='em') return [f.n, si(v,'N')];
    return [f.n, si(v,'N')+' <span style="color:#9a9a9a">('+(rel>=1?big(rel)+'\\u00d7':'1/'+big(1/rel))+' of electromagnetism)</span>']; });
  const strongest=FOUR.reduce((a,f)=>force(f,rr)>force(a,rr)?f:a,FOUR[0]);
  const pl=PLACES.reduce((a,p)=>Math.abs(Math.log10(p.m/rr))<Math.abs(Math.log10(a.m/rr))?p:a,PLACES[0]);
  card('Two protons apart by', fm(rr), rows, 'The strongest here is '+strongest.n+'. '+(Math.abs(Math.log10(pl.m/rr))<0.15?'This is about '+pl.n+': '+pl.b+'.':''), '');
}
function showFour(k){ const f=FOUR.find(x=>x.k===k); if(!f) return;
  card('One of the four', esc(f.n), [['coupling', f.a>=0.01?'1/'+sf(1/f.a,3):sci(f.a)],['reach', f.lam==null?'no limit':fm(f.lam)],['at 1 fm', force(f,1e-15)<1e-46?'below 10<sup>-46</sup> N, nothing to speak of':si(force(f,1e-15),'N')]], f.b, f.s); }
function showForce(k){ const o=FORCES.find(x=>x.k===k); if(!o) return; const f=FOUR.find(x=>x.k===o.f);
  card('A force', esc(o.n), [['what',esc(o.what)],['size',si(o.N,'N')],['in plain terms',weightWords(o.N)||''],['which of the four',f.n]], o.b, o.s); }

/* ---- the four ---- */
const P={x:84,y:36,w:850,h:520}, XL0=-19, XL1=-10, YL0=-46, YL1=14;
const PX=m=>P.x+(Math.log10(m)-XL0)/(XL1-XL0)*P.w;
const PY=N=>P.y+P.h-(Math.log10(Math.max(N,1e-300))-YL0)/(YL1-YL0)*P.h;
function four(){
  let s='<rect x="'+P.x+'" y="'+P.y+'" width="'+P.w+'" height="'+P.h+'" fill="none" stroke="#2b2b2b"/>';
  for(let lg=XL0; lg<=XL1; lg++){ const x=PX(Math.pow(10,lg)); s+='<line x1="'+x.toFixed(1)+'" y1="'+(P.y+P.h)+'" x2="'+x.toFixed(1)+'" y2="'+(P.y+P.h+6)+'" stroke="#8a94a6"/><text x="'+x.toFixed(1)+'" y="'+(P.y+P.h+20)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">'+(lg>=-12?si(Math.pow(10,lg),'m'):sf(Math.pow(10,lg+15),1)+' fm')+'</text>'; }
  for(let lg=YL0; lg<=YL1; lg+=10){ const y=PY(Math.pow(10,lg)); s+='<line x1="'+(P.x-6)+'" y1="'+y.toFixed(1)+'" x2="'+P.x+'" y2="'+y.toFixed(1)+'" stroke="#8a94a6"/><text x="'+(P.x-9)+'" y="'+(y+4).toFixed(1)+'" text-anchor="end" font-size="10.5" fill="#9a9a9a">10<tspan dy="-4" font-size="8">'+lg+'</tspan></text>'; }
  s+='<text x="'+(P.x+P.w/2)+'" y="'+(P.y+P.h+40)+'" text-anchor="middle" font-size="11.5" fill="#9a9a9a">distance between two protons</text>';
  s+='<text transform="translate(16,'+(P.y+P.h/2)+') rotate(-90)" text-anchor="middle" font-size="11.5" fill="#9a9a9a">force, newtons</text>';
  for(const p of PLACES){ const x=PX(p.m); s+='<line x1="'+x.toFixed(1)+'" y1="'+P.y+'" x2="'+x.toFixed(1)+'" y2="'+(P.y+P.h)+'" stroke="#2b2b2b" stroke-dasharray="3 4"/><text x="'+(x-4).toFixed(1)+'" y="'+(P.y+12)+'" text-anchor="end" font-size="10" fill="#6b7280" transform="rotate(-90 '+(x-4).toFixed(1)+' '+(P.y+12)+')">'+esc(p.n)+'</text>'; }
  for(const f of FOUR){ let d='', on=false; for(let lg=XL0; lg<=XL1+1e-9; lg+=0.01){ const m=Math.pow(10,lg), N=force(f,m); if(N<Math.pow(10,YL0)){ on=false; continue; } d+=(on?'L':'M')+PX(m).toFixed(1)+','+PY(N).toFixed(1); on=true; }
    s+='<g data-f="'+f.k+'" style="cursor:pointer"><path d="'+d+'" fill="none" stroke="'+f.c+'" stroke-width="'+(hot===f.k?3:2)+'" opacity="'+(hot&&hot!==f.k?0.45:1)+'"/></g>'; }
  // labels at the right edge for the two long-range forces, and at the peak for the short ones
  for(const f of FOUR){ let x,y,anchor='end'; if(f.lam==null){ x=P.x+P.w-6; y=PY(force(f,1e-10))-6; } else { const m=f.lam*3; x=PX(m)+8; y=PY(force(f,m))+4; anchor='start'; }
    s+='<text x="'+x.toFixed(1)+'" y="'+y.toFixed(1)+'" text-anchor="'+anchor+'" font-size="11.5" font-weight="600" fill="'+f.c+'">'+esc(f.n)+'</text>'; }
  const mx=PX(r);
  s+='<g id="marker" style="cursor:ew-resize"><line x1="'+mx.toFixed(1)+'" y1="'+P.y+'" x2="'+mx.toFixed(1)+'" y2="'+(P.y+P.h)+'" stroke="#e6e6e6" stroke-width="1.2" opacity="0.8"/>';
  for(const f of FOUR){ const N=force(f,r); if(N>=Math.pow(10,YL0)) s+='<circle cx="'+mx.toFixed(1)+'" cy="'+PY(N).toFixed(1)+'" r="5" fill="'+f.c+'" stroke="#121212" stroke-width="1.5"/>'; }
  s+='<text x="'+mx.toFixed(1)+'" y="'+(P.y+P.h-6)+'" text-anchor="middle" font-size="11" font-weight="700" fill="#e6e6e6">'+fm(r)+'</text></g>';
  return {svg:s, h:P.y+P.h+50};
}

/* ---- how hard ---- */
const S={L:40,R:940,Y:120,LOG0:-48,LOG1:45};
const SX=N=>S.L+(Math.log10(N)-S.LOG0)/(S.LOG1-S.LOG0)*(S.R-S.L);
function lanes(items,minGap){ const rows=[]; const out=[]; for(const it of items){ let q=0; while(rows[q]!==undefined && it.x-rows[q]<minGap) q++; rows[q]=it.x+it.w; out.push({...it,lane:q}); } return out; }
function line(){
  let s='';
  s+='<line x1="'+S.L+'" y1="'+S.Y+'" x2="'+S.R+'" y2="'+S.Y+'" stroke="#8a94a6" stroke-width="1.5"/>';
  for(let d=S.LOG0; d<=S.LOG1; d++){ const x=SX(Math.pow(10,d)); const big=(d%10===0);
    s+='<line x1="'+x.toFixed(1)+'" y1="'+(S.Y-(big?7:3))+'" x2="'+x.toFixed(1)+'" y2="'+(S.Y+(big?7:3))+'" stroke="#8a94a6"/>';
    if(big) s+='<text x="'+x.toFixed(1)+'" y="'+(S.Y+22)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">10<tspan dy="-4" font-size="8">'+d+'</tspan><tspan dy="4"> N</tspan></text>'; }
  s+='<text x="'+S.L+'" y="'+(S.Y-70)+'" font-size="11" fill="#9a9a9a">ninety-three decades of force; the color says which of the four is pushing</text>';
  let lx=S.L; for(const f of FOUR){ if(f.k==='weak') continue; s+='<rect x="'+lx+'" y="'+(S.Y-58)+'" width="10" height="10" fill="'+f.c+'" rx="2"/><text x="'+(lx+14)+'" y="'+(S.Y-49)+'" font-size="10.5" fill="#9a9a9a">'+esc(f.n)+'</text>'; lx+=f.n.length*6.2+30; }
  const items=lanes(FORCES.map(o=>({...o,x:SX(o.N),w:o.n.length*5.7+10})).sort((a,b)=>a.x-b.x),0);
  let maxLane=0;
  for(const o of items){ const f=FOUR.find(x=>x.k===o.f), y=S.Y+44+o.lane*17; maxLane=Math.max(maxLane,o.lane);
    s+='<g data-k="'+o.k+'" style="cursor:pointer"><line x1="'+o.x.toFixed(1)+'" y1="'+(S.Y+8)+'" x2="'+o.x.toFixed(1)+'" y2="'+(y-4)+'" stroke="'+(hot===o.k?'#e6e6e6':'#3d444d')+'"/>';
    s+='<circle cx="'+o.x.toFixed(1)+'" cy="'+S.Y+'" r="'+(hot===o.k?6:4.5)+'" fill="'+f.c+'" stroke="#121212" stroke-width="1.5"/>';
    const flip=o.x+o.w>W-10;
    s+='<text x="'+(o.x+(flip?-4:4)).toFixed(1)+'" y="'+(y+4)+'" text-anchor="'+(flip?'end':'start')+'" font-size="10.5" fill="'+(hot===o.k?'#e6e6e6':'#9a9a9a')+'">'+esc(o.n)+'</text></g>'; }
  return {svg:s, h:S.Y+44+(maxLane+1)*17+30};
}

/* ---- render and wiring ---- */
function render(){
  const q=view==='four'?four():line();
  el.innerHTML='<svg viewBox="0 0 '+W+' '+q.h+'" xmlns="http://www.w3.org/2000/svg" id="fsvg"><rect width="'+W+'" height="'+q.h+'" fill="#121212"/>'+q.svg+'</svg>';
  document.getElementById('fourCtl').hidden=view!=='four'; document.getElementById('lineCtl').hidden=view!=='line';
  document.getElementById('distOut').textContent=fm(r);
}
function setView(v){ view=v; hot=null; for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on',b.dataset.v===v); render(); if(v==='four') showDist(r); else showForce('person'); }
function setR(m){ r=Math.max(Math.pow(10,XL0),Math.min(Math.pow(10,XL1),m)); document.getElementById('dist').value=Math.round(Math.log10(r)*100); render(); showDist(r); }
document.getElementById('views').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setView(b.dataset.v); });
document.getElementById('dist').addEventListener('input',e=>{ r=Math.pow(10,+e.target.value/100); render(); showDist(r); });
document.getElementById('places').innerHTML=PLACES.map(p=>'<button type="button" data-m="'+p.m+'">'+esc(p.n)+'</button>').join('');
document.getElementById('places').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setR(+b.dataset.m); });
document.getElementById('jumps').innerHTML=FORCES.filter(o=>['hgrav','hydrogen','apple','quarks','sun','planck'].includes(o.k)).map(o=>'<button type="button" data-k="'+o.k+'">'+esc(o.n)+'</button>').join('');
document.getElementById('jumps').addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; hot=b.dataset.k; render(); showForce(hot); });
let dragging=false;
const svgPt=e=>{ const svg=document.getElementById('fsvg'), b=svg.getBoundingClientRect(); return [(e.clientX-b.left)/b.width*W,(e.clientY-b.top)/b.height*svg.viewBox.baseVal.height]; };
el.addEventListener('pointerdown',e=>{ if(view!=='four') return; const [x,y]=svgPt(e); if(x>=P.x&&x<=P.x+P.w&&y>=P.y&&y<=P.y+P.h){ dragging=true; setR(Math.pow(10,XL0+(x-P.x)/P.w*(XL1-XL0))); e.preventDefault(); } });
el.addEventListener('pointermove',e=>{ if(!dragging) return; const [x]=svgPt(e); setR(Math.pow(10,XL0+Math.max(0,Math.min(1,(x-P.x)/P.w))*(XL1-XL0))); });
window.addEventListener('pointerup',()=>{ dragging=false; });
el.addEventListener('pointerover',e=>{ if(dragging) return; const k=e.target.closest('[data-k]'); if(k){ if(k.getAttribute('data-k')===hot) return; hot=k.getAttribute('data-k'); render(); showForce(hot); return; }
  const f=e.target.closest('[data-f]'); if(f){ if(f.getAttribute('data-f')===hot) return; hot=f.getAttribute('data-f'); render(); showFour(hot); } });
el.addEventListener('pointerleave',()=>{ if(view==='four'&&hot){ hot=null; render(); showDist(r); } });

render(); showDist(r);
window.__forces=(q)=>{ const o={view,r,hot,marks:document.querySelectorAll('#fsvg g[data-k]').length,curves:document.querySelectorAll('#fsvg g[data-f] path').length,
  card:document.getElementById('numTxt').innerText, name:document.getElementById('nameTxt').innerText,
  marker:(()=>{ const t=document.querySelector('#marker line'); return t?+t.getAttribute('x1'):null; })(),
  dots:[...document.querySelectorAll('#marker circle')].map(c=>[c.getAttribute('fill'),+c.getAttribute('cy')])};
  if(q&&q.force) o.fv=FOUR.map(f=>force(f,q.force)); if(q&&q.PX!=null) o.px=PX(q.PX); if(q&&q.PY!=null) o.py=PY(q.PY); if(q&&q.SX!=null) o.sx=SX(q.SX);
  if(q&&q.weight!=null) o.wv=weightWords(q.weight); return o; };
</script>
</body>
</html>
"""

html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__FOUR__", _js(four)).replace("__PLACES__", _js(places)).replace("__FORCES__", _js(forces))
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(FOUR)} forces, {len(PLACES)} places, {len(FORCES)} marks")
