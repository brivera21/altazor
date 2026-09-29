#!/usr/bin/env python3
"""Generate languages.html: the tree of the world's languages.

One collapsible cladogram over Glottolog's classification, from the root
through 238 families to every language it lists. A family opens into its
branches; a search box finds a language and opens the path down to it.

Data: tools/data/languages.json (build_languages_data.py).

Usage: python3 build_languages.py
"""

import json
import math
import apa
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = Path(__file__).parent / "data"

CAPTION = ("Every language Glottolog classifies, 8,170 of them, as one tree of "
           "descent. A family opens into its branches and those into "
           "languages, each tip colored by how endangered it is; the bar on "
           "a family's row is the same count for everything under it. To "
           "scale, the families become circles sized by their languages.")

NOTE1 = ("The tree is Glottolog's classification, which admits a relation "
         "only where the regular sound correspondences have been shown. "
         "Deeper groupings that circulate in the literature, Altaic, "
         "Nostratic, Amerind among them, are not in it.")

NOTE2 = ("A node holding branches opens and closes when clicked, and the "
         "one under the cursor fills the card. Tips are languages, not "
         "dialects, and a language here is a lineage rather than a state "
         "or a script: Hindi and Urdu part, Chinese does not hold together. "
         "A tip's color is Glottolog's endangerment status, green through "
         "red to the gray of a language no longer spoken. Sign languages, "
         "pidgins, mixed and designed languages sit apart, since their "
         "history is not descent from a parent.")

REFS = [
    ("https://glottolog.org",
     "The classification the tree draws, and the endangerment status on "
     "every tip."),
    ("https://github.com/glottolog/glottolog-cldf",
     "The release the data was taken from, CC-BY 4.0."),
    ("https://iso639-3.sil.org/",
     "The three-letter codes beside the languages."),
]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Languages · Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; --hl:#31d67a; }
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
h1 { margin:0 0 10px; font-size:26px; }
.bar { display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-bottom:12px; }
.bar input { background:#0d0d0d; color:var(--text); border:1px solid var(--line);
  border-radius:999px; padding:7px 14px; font-size:13.5px; width:250px; }
.bar input:focus { outline:none; border-color:var(--accent); }
.bar button { background:transparent; color:var(--text); border:1px solid var(--line);
  border-radius:999px; padding:6px 14px; font-size:13px; cursor:pointer; }
.bar button:hover { border-color:var(--accent); color:var(--accent); }
#legend { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:10px;
  color:var(--muted); font-size:12px; align-items:center; }
#legend button { display:flex; gap:5px; align-items:center; background:transparent; color:var(--muted);
  border:1px solid transparent; border-radius:999px; padding:2px 9px; font-size:12px; cursor:pointer; font-family:inherit; }
#legend button:hover { color:var(--text); border-color:var(--line); }
#legend button.on { color:var(--text); border-color:var(--accent); background:#0d1a2b; }
.bar button.on { background:var(--accent); color:#0b1a2b; border-color:var(--accent); font-weight:600; }
#diagram:focus { outline:none; }
#diagram:focus-visible { border-color:#3d444d; }
#mapTxt svg { display:block; margin-top:10px; }
details.sources { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
details.sources summary { cursor:pointer; }
details.sources summary:hover { color:var(--text); }
details.sources .note { border-top:none; padding-top:0; margin-top:10px; }
#legend i { width:9px; height:9px; border-radius:50%; display:inline-block; }
#hits { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:10px; }
#hits button { background:#0d0d0d; color:var(--accent); border:1px solid var(--line);
  border-radius:999px; padding:4px 11px; font-size:12.5px; cursor:pointer; }
#hits button:hover { border-color:var(--accent); }
#hits .none { color:var(--muted); font-size:12.5px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; max-height:78vh; overflow-y:auto;
  border:1px solid var(--line); border-radius:12px; background:#151515; }
#diagram svg { width:100%; height:auto; display:block; user-select:none; }
.side { flex:0 0 300px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:16px; }
#nameTxt { font-weight:700; font-size:17px; }
#cntTxt { color:var(--hl); font-size:13px; margin-top:2px; }
#bodyTxt { color:var(--muted); font-size:13.5px; line-height:1.55; margin-top:8px; }
#pathTxt { color:var(--muted); font-size:12.5px; margin-top:10px; }
#srcTxt { color:var(--muted); font-size:12px; margin-top:10px;
  border-top:1px solid var(--line); padding-top:8px; }
#srcTxt a { color:var(--accent); }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.refs { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.refs p { margin:0 0 8px; overflow-wrap:anywhere; }
.refs a { color:var(--accent); }
__APACSS__
h2.refh { font-size:15px; margin:26px 0 8px; }
@media (max-width:900px){ .stage{flex-direction:column;} .side{position:static; width:100%;} #diagram{width:100%; flex-basis:auto;} }
@media (max-width:600px){ #diagram{overflow-x:auto;} #diagram svg{min-width:760px;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library &middot; Homo Sapiens</a> <a href="migration.html">Homo Sapiens Migration</a> <a href="hominins.html">Hominins</a></nav>
</header>
<h1>Languages</h1>
<div class="bar">
  <input id="q" type="search" placeholder="Find a language or family" autocomplete="off">
  <button id="bTop">Families only</button>
  <button id="bBig">Open the ten largest</button>
  <button id="bScale">To scale</button>
</div>
<div id="legend"></div>
<div id="hits"></div>
<div class="stage">
  <div id="diagram" tabindex="0"></div>
  <div class="side"><div class="card">
    <div id="nameTxt">A group under the cursor lands here</div>
    <div id="cntTxt"></div>
    <div id="bodyTxt"></div>
    <div id="pathTxt"></div>
    <div id="mapTxt"></div>
    <div id="srcTxt"></div>
  </div></div>
</div>
<p class="note">__CAPTION__</p>
<details class="sources"><summary>Sources</summary>
<p class="note">__NOTE1__</p>
<p class="note">__NOTE2__</p>
<p class="note">__NOTE3__</p>
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</details>
</div>
<script>
const ROOT=__DATA__, PACK=__PACK__, PACKH=__PACKH__;
const el=document.getElementById('diagram');
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
const fmt=x=>x.toLocaleString('en-US');
// Glottolog's Agglomerated Endangerment Status, 1 to 6
const AES=['not endangered','threatened','shifting','moribund',
  'nearly extinct','no longer spoken'];
const AESC=['#31d67a','#ffd24d','#ff9440','#f4713f','#ef5350','#6b7280'];
const vc=n=>n.v?AESC[n.v-1]:'#58a6ff';
// the legend doubles as a filter: a status lights only its own tips
let filt=null;
const CLR=v=>v?AESC[v-1]:'#58a6ff', STN=v=>v?AES[v-1]:'not assessed', ORDER=[1,2,3,4,5,6,0];
function paintLegend(){ document.getElementById('legend').innerHTML=ORDER.map(v=>'<button data-f="'+v+'"'+(filt===v?' class="on"':'')+'><i style="background:'+CLR(v)+'"></i>'+STN(v)+'</button>').join(''); }
paintLegend();
document.getElementById('legend').addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; const v=+b.dataset.f; filt=filt===v?null:v; paintLegend(); render(); show(current); });

// every node gets an id, a parent and the number of languages under it
let idc=0; const byId={}, ALL=[];
(function prep(n,parent){
  n.id='n'+(idc++); n.p=parent; byId[n.id]=n; ALL.push(n);
  if(n.k){ n.k.forEach(c=>prep(c,n)); n.t=n.k.reduce((a,c)=>a+c.t,0); n.vc=[0,0,0,0,0,0,0]; for(const c of n.k) for(let i=0;i<7;i++) n.vc[i]+=c.vc[i]; }
  else { n.t=1; n.vc=[0,0,0,0,0,0,0]; n.vc[n.v||0]=1; }
})(ROOT,null);

// closed nodes keep their branches folded away; the root and its
// children start open so the families are the first thing on screen
const open=new Set([ROOT.id]);

// an indented tree: every open node keeps its own row, its branches
// below it and one step to the right
const RS=23, PADT=16, PADB=16, PADL=16, PADR=340, IND=20, W=1010, BARX=780, BARW=190;
let rows=[], maxd=0;
function layout(){
  rows=[]; maxd=0;
  (function walk(n,d){
    n.depth=d; n.y=PADT+RS*(rows.length+0.5); rows.push(n);
    maxd=Math.max(maxd,d);
    if(n.k&&open.has(n.id)) n.k.forEach(c=>walk(c,d+1));
  })(ROOT,0);
  return PADT+PADB+RS*rows.length;
}
const X=d=>PADL+d*IND;

function draw(n){
  const x=X(n.depth), isOpen=n.k&&open.has(n.id), leaf=!n.k;
  let s='';
  if(isOpen){
    const x1=X(n.depth+1), last=n.k[n.k.length-1];
    s+='<path d="M'+x+','+(n.y+7)+' V'+last.y+'" fill="none" stroke="#3d444d" stroke-width="1.3"/>';
    for(const c of n.k)
      s+='<path d="M'+x+','+c.y+' H'+(x1-6)+'" fill="none" stroke="#3d444d" stroke-width="1.3"/>';
  }
  const col=leaf?'#c9d1d9':(isOpen?'#9a9a9a':'#e6e6e6');
  const dim=filt!=null&&(leaf?(n.v||0)!==filt:!n.vc[filt]);
  s+='<g data-id="'+n.id+'" style="cursor:'+(leaf?'default':'pointer')+'"'+(dim?' opacity="0.28"':'')+'>'
    +(n.id===pinned?'<circle cx="'+x+'" cy="'+n.y+'" r="9" fill="none" stroke="var(--accent)" stroke-width="1.5"/>':'')
    +'<rect x="'+(x-10)+'" y="'+(n.y-11)+'" width="'+(W-PADL-x)+'" height="'+RS+'" fill="'+(n.id===pinned?'#1d2126':'transparent')+'"/>'
    // a branch is a square, a language a circle, so the vitality
    // colors below belong to the tips alone
    +(leaf
      ? '<circle cx="'+x+'" cy="'+n.y+'" r="4" fill="'+vc(n)+'" stroke="'+vc(n)+'" stroke-width="1.5"/>'
      : '<rect x="'+(x-4.5)+'" y="'+(n.y-4.5)+'" width="9" height="9" rx="1.5" fill="'+(isOpen?'#151515':'#8b949e')+'" stroke="#8b949e" stroke-width="1.5"/>')
    +'<text x="'+(x+11)+'" y="'+(n.y+4.5)+'" font-size="'+(leaf?12.5:13)+'" font-weight="'+(leaf?400:600)+'" fill="'+col+'">'+esc(n.n)
    +(leaf?(n.e?' <tspan fill="#6b7280" font-size="10.5">'+esc(n.e)+'</tspan>':'')
          :' <tspan fill="#6b7280" font-size="11" font-weight="400">'+fmt(n.t)+(filt!=null?', '+fmt(n.vc[filt])+' '+STN(filt):'')+'</tspan>')
    +'</text>'+(!leaf&&x+11+(n.n.length+8+(filt!=null?20:0))*7<BARX-12?vbar(n):'')+'</g>';
  if(isOpen) for(const c of n.k) s+=draw(c);
  return s;
}
// a family's languages by status, as one stacked bar
function vbar(n){ let s='', x=BARX; for(const v of ORDER){ const w=n.vc[v]/n.t*BARW; if(w<=0) continue; s+='<rect x="'+x.toFixed(1)+'" y="'+(n.y-4)+'" width="'+w.toFixed(1)+'" height="8" fill="'+CLR(v)+'"'+(filt!=null&&filt!==v?' opacity="0.18"':'')+'/>'; x+=w; } return s; }
let mode='tree', grow=1;
const RM=matchMedia('(prefers-reduced-motion: reduce)').matches;
const ease=k=>k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2;
function pie(cx,cy,r,n){ if(r<1.5) return '<circle cx="'+cx+'" cy="'+cy+'" r="'+r.toFixed(2)+'" fill="'+CLR(ORDER.find(v=>n.vc[v]))+'"/>'; let a=-Math.PI/2, s=''; for(const v of ORDER){ const f=n.vc[v]/n.t; if(!f) continue; const op=filt!=null&&filt!==v?0.15:0.9;
    if(f>0.9999){ s+='<circle cx="'+cx+'" cy="'+cy+'" r="'+r.toFixed(2)+'" fill="'+CLR(v)+'" opacity="'+op+'"/>'; break; }
    const b=a+f*2*Math.PI, L=f>0.5?1:0; s+='<path d="M'+cx+','+cy+' L'+(cx+r*Math.cos(a)).toFixed(2)+','+(cy+r*Math.sin(a)).toFixed(2)+' A'+r.toFixed(2)+','+r.toFixed(2)+' 0 '+L+' 1 '+(cx+r*Math.cos(b)).toFixed(2)+','+(cy+r*Math.sin(b)).toFixed(2)+' Z" fill="'+CLR(v)+'" opacity="'+op+'"/>'; a=b; }
  return s; }
function bubbles(){ let s=''; const top=ROOT.k;
  PACK.forEach(([i,x,y,r],j)=>{ const n=top[i]; const k=Math.max(0,Math.min(1,grow*1.6-j/PACK.length*0.6)); const rr=r*ease(k); const on=n.id===pinned||n.id===current&&mode==='scale';
    s+='<g data-id="'+n.id+'" style="cursor:pointer">'+pie(x,y,rr,n)+'<circle cx="'+x+'" cy="'+y+'" r="'+rr.toFixed(2)+'" fill="none" stroke="'+(on?'#ffffff':'#121212')+'" stroke-width="'+(on?2:1)+'"/>';
    if(r>=24&&k>0.8){ const fs=Math.min(14,Math.max(10,r/5)); s+='<text x="'+x+'" y="'+(y-2)+'" text-anchor="middle" font-size="'+fs.toFixed(1)+'" font-weight="600" fill="#ffffff" stroke="#121212" stroke-width="3" paint-order="stroke">'+esc(n.n.length>r/3.6?n.n.slice(0,Math.floor(r/3.6))+'\u2026':n.n)+'</text><text x="'+x+'" y="'+(y+fs)+'" text-anchor="middle" font-size="'+(fs-1).toFixed(1)+'" fill="#e6e6e6" stroke="#121212" stroke-width="3" paint-order="stroke">'+fmt(filt!=null?n.vc[filt]:n.t)+'</text>'; }
    s+='</g>'; });
  s+='<text x="16" y="'+(PACKH-12)+'" font-size="11" fill="#9a9a9a">each family a circle, its area its languages; the wedges are the tree\u2019s colors; the smallest, most of them at the edge, hold two to five</text>';
  return s; }
function render(){
  document.getElementById('bScale').classList.toggle('on',mode==='scale');
  if(mode==='scale'){ el.innerHTML='<svg viewBox="0 0 '+W+' '+PACKH+'" xmlns="http://www.w3.org/2000/svg" id="treesvg">'+bubbles()+'</svg>'; return; }
  const H=layout();
  el.innerHTML='<svg viewBox="0 0 '+W+' '+H+'" xmlns="http://www.w3.org/2000/svg" id="treesvg">'+draw(ROOT)+'</svg>';
}

let current=ROOT.id, pinned=null;
function pathOf(n){ const out=[]; let p=n.p; while(p){ out.unshift(p.n); p=p.p; } return out; }
function show(id){
  const n=byId[id]; if(!n) return;
  current=id;
  document.getElementById('nameTxt').textContent=n.n;
  let cnt;
  if(n.k){
    let gone=0;(function w(x){ if(x.k) x.k.forEach(w); else if(x.v===6) gone++; })(n);
    cnt=fmt(n.t)+(n.t===1?' language':' languages')
      +(gone?', '+fmt(gone)+' no longer spoken':'');
    if(filt!=null) cnt+='; '+fmt(n.vc[filt])+' '+STN(filt)+(n.t?' ('+Math.round(n.vc[filt]/n.t*100)+'%)':'');
  } else cnt=n.v?AES[n.v-1]:'vitality not assessed';
  const ct=document.getElementById('cntTxt');
  ct.textContent=cnt; ct.style.color=n.k?'var(--hl)':vc(n);
  document.getElementById('bodyTxt').textContent=n.b||'';
  const path=pathOf(n);
  document.getElementById('pathTxt').textContent=path.length?path.join(' \\u203a '):'';
  document.getElementById('mapTxt').innerHTML=n.a?areaMap(n.a):'';
  const src=document.getElementById('srcTxt');
  const bits=[];
  if(!n.k&&n.a) bits.push(n.a);
  if(n.e) bits.push('ISO 639-3: '+n.e);
  src.innerHTML=(bits.length?esc(bits.join(' \\u00b7 '))+'<br>':'')
    +(n.g?'<a href="https://glottolog.org/resource/languoid/id/'+n.g+'">Glottolog '+n.g+'</a>':'Glottolog 5.2.1');
}
// Glottolog's six macroareas, laid out roughly where they sit on a map
const AREAS=[['North America',8,6,70,42],['South America',42,52,44,50],['Eurasia',92,4,150,44],['Africa',104,52,56,50],['Papunesia',172,54,52,30],['Australia',192,88,42,20]];
function areaMap(a){ const on=new Set(a.split(';')); let s='<svg viewBox="0 0 268 112" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg">';
  for(const [n,x,y,w,h] of AREAS){ const lit=on.has(n); s+='<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="10" fill="'+(lit?'#31d67a':'#242424')+'" opacity="'+(lit?0.85:1)+'" stroke="#2b2b2b"/><text x="'+(x+w/2)+'" y="'+(y+h/2+3.5)+'" text-anchor="middle" font-size="9.5" fill="'+(lit?'#0b1a2b':'#6b7280')+'">'+n+'</text>'; }
  return s+'</svg>'; }
function openTo(n){ let p=n.p; while(p){ open.add(p.id); p=p.p; } }

el.addEventListener('pointerover',e=>{
  if(pinned) return;
  const g=e.target.closest('[data-id]');
  if(g) show(g.getAttribute('data-id'));
});
el.addEventListener('click',e=>{
  const g=e.target.closest('[data-id]');
  if(mode==='scale'){ if(!g) return; const id=g.getAttribute('data-id'); mode='tree'; open.clear(); open.add(ROOT.id); open.add(id); pinned=id; show(id); render(); const c=el.querySelector('[data-id="'+id+'"] rect'); if(c) c.scrollIntoView({block:'start'}); return; }
  if(!g){ pinned=null; render(); return; }
  const id=g.getAttribute('data-id'), n=byId[id];
  pinned=id; show(id);
  if(n.k){ if(open.has(id)) open.delete(id); else open.add(id); }
  render();
});

// search: the matching languages and families, each opening its own path
const hits=document.getElementById('hits'), q=document.getElementById('q');
const fold=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
function search(){
  const v=fold(q.value.trim());
  hits.innerHTML='';
  if(v.length<2) return;
  const found=ALL.filter(n=>fold(n.n).includes(v)
    ||(n.e&&n.e.toLowerCase()===v)).slice(0,40);
  if(!found.length){ hits.innerHTML='<span class="none">nothing by that name</span>'; return; }
  for(const n of found){
    const b=document.createElement('button');
    b.textContent=n.n+(n.k?' ('+fmt(n.t)+')':'');
    b.onclick=()=>{
      openTo(n); if(n.k) open.add(n.id);
      pinned=n.id; show(n.id); render();
      const c=el.querySelector('[data-id="'+n.id+'"] circle');
      if(c) c.scrollIntoView({block:'center'});
    };
    hits.appendChild(b);
  }
}
q.addEventListener('input',search);
document.getElementById('bTop').onclick=()=>{
  mode='tree'; open.clear(); open.add(ROOT.id); pinned=null; render(); el.scrollTop=0;
};
document.getElementById('bBig').onclick=()=>{
  mode='tree'; open.clear(); open.add(ROOT.id);
  ROOT.k.slice(0,10).forEach(n=>open.add(n.id));
  pinned=null; render(); el.scrollTop=0;
};

let growId=0;
document.getElementById('bScale').onclick=()=>{ if(mode==='scale'){ mode='tree'; render(); return; } mode='scale'; el.scrollTop=0; const id=++growId;
  if(RM){ grow=1; render(); return; } const t0=performance.now(); const f=now=>{ if(id!==growId||mode!=='scale') return; grow=Math.min(1,(now-t0)/1100); render(); if(grow<1) requestAnimationFrame(f); }; grow=0; render(); requestAnimationFrame(f); };
// keys: up and down walk the rows, right opens, left closes or climbs
el.addEventListener('keydown',e=>{ if(mode!=='tree') return; const k=e.key; if(!['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Enter','Escape'].includes(k)) return; e.preventDefault();
  if(k==='Escape'){ pinned=null; render(); return; }
  let n=byId[pinned||current]; let i=rows.indexOf(n); if(i<0){ n=ROOT; i=0; }
  if(k==='ArrowDown'&&i<rows.length-1) n=rows[i+1];
  else if(k==='ArrowUp'&&i>0) n=rows[i-1];
  else if(k==='ArrowRight'&&n.k){ if(!open.has(n.id)) open.add(n.id); else n=n.k[0]; }
  else if(k==='ArrowLeft'){ if(n.k&&open.has(n.id)&&n!==ROOT) open.delete(n.id); else if(n.p) n=n.p; }
  else if(k==='Enter'&&n.k&&n!==ROOT){ if(open.has(n.id)) open.delete(n.id); else open.add(n.id); }
  pinned=n.id; show(n.id); render(); const g=el.querySelector('[data-id="'+n.id+'"]'); if(g){ const b=g.getBoundingClientRect(), eb=el.getBoundingClientRect(); if(b.top<eb.top+10||b.bottom>eb.bottom-10) el.scrollTop+=b.top-eb.top-eb.height/2; } });

render();
show(ROOT.id);
window.__lang=()=>({nodes:ALL.length, langs:ROOT.t, families:ROOT.k.length,
  rows:rows.length, depth:maxd, open:open.size, pinned, current, mode, grow, filt,
  bubbles:mode==='scale'?document.querySelectorAll('#treesvg g[data-id]').length:0, pack:PACK, tops:ROOT.k.map(n=>[n.id,n.t,n.vc])});
</script>
</body>
</html>
"""


NOTE3 = ("To scale, each family is a circle whose area is its number of "
         "languages, packed tightly around the largest; isolates, which "
         "are families of one, sit together as one circle, as they do on "
         "the tree, and so do the sign languages, pidgins, mixed and "
         "designed languages outside it. Each circle's wedges are its "
         "languages by status. The small map in the card lights the "
         "macroareas Glottolog places a family or language in.")


def count(n):
    return 1 if "k" not in n else sum(count(c) for c in n["k"])


def pack(sizes, width=1010, height=640):
    """Circles of the given areas, packed greedily, each new one tangent to
    two already placed and as near the middle as it will go, the middle
    measured on a flattened ellipse so the pack is wider than tall."""
    order = sorted(range(len(sizes)), key=lambda i: -sizes[i])
    r = np.sqrt(np.array(sizes, float))
    P = []  # (i, x, y, r)
    xs, ys, rs = [], [], []
    ASP = 1.75
    for i in order:
        ri = r[i]
        if not P:
            P.append((i, 0.0, 0.0, ri)); xs.append(0.0); ys.append(0.0); rs.append(ri); continue
        X, Y, R = np.array(xs), np.array(ys), np.array(rs)
        if len(P) == 1:
            cand = np.array([[X[0] + R[0] + ri, 0.0]])
        else:
            a, b = np.triu_indices(len(P), 1)
            dx, dy = X[b] - X[a], Y[b] - Y[a]
            d = np.hypot(dx, dy)
            ra, rb = R[a] + ri, R[b] + ri
            ok = (d < ra + rb) & (d > np.abs(ra - rb)) & (d > 0)
            a, b, dx, dy, d, ra, rb = a[ok], b[ok], dx[ok], dy[ok], d[ok], ra[ok], rb[ok]
            l = (ra ** 2 - rb ** 2 + d ** 2) / (2 * d)
            h = np.sqrt(np.maximum(ra ** 2 - l ** 2, 0))
            mx, my = X[a] + l * dx / d, Y[a] + l * dy / d
            cand = np.concatenate([np.stack([mx + h * dy / d, my - h * dx / d], 1), np.stack([mx - h * dy / d, my + h * dx / d], 1)])
        gap = np.hypot(cand[:, 0:1] - X[None, :], cand[:, 1:2] - Y[None, :]) - (R[None, :] + ri)
        good = cand[(gap > -1e-6).all(1)]
        if not len(good):
            ang = np.linspace(0, 2 * np.pi, 720, endpoint=False)
            far = max(np.hypot(X, Y) + R) + ri + 1
            good = np.stack([far * np.cos(ang) * ASP, far * np.sin(ang)], 1)
        dist = np.hypot(good[:, 0] / ASP, good[:, 1])
        x, y = good[dist.argmin()]
        P.append((i, float(x), float(y), ri)); xs.append(float(x)); ys.append(float(y)); rs.append(ri)
    minx = min(x - q for _, x, _, q in P); maxx = max(x + q for _, x, _, q in P)
    miny = min(y - q for _, _, y, q in P); maxy = max(y + q for _, _, y, q in P)
    s = min((width - 30) / (maxx - minx), (height - 50) / (maxy - miny))
    ox = (width - s * (maxx - minx)) / 2 - s * minx
    oy = 12 - s * miny
    out = [[i, round(ox + s * x, 1), round(oy + s * y, 1), round(s * q, 2)] for i, x, y, q in P]
    return out, round(s * (maxy - miny) + 50)


def main():
    data = json.loads((DATA / "languages.json").read_text(encoding="utf-8"))
    PACK, PACKH = pack([count(c) for c in data["k"]])
    refs = apa.render([apa.auto(u, ann) for u, ann in REFS])
    html = (HTML.replace("__APACSS__", apa.CSS)
            .replace("__CAPTION__", CAPTION).replace("__NOTE3__", NOTE3)
            .replace("__PACK__", json.dumps(PACK)).replace("__PACKH__", str(PACKH))
            .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2)
            .replace("__REFS__", refs)
            .replace("__DATA__", json.dumps(data, separators=(",", ":"),
                                            ensure_ascii=False)))
    p = ROOT / "languages.html"
    p.write_text(html, encoding="utf-8")

    print(f"wrote {p} ({len(html):,} B): {len(data['k'])} top nodes, "
          f"{count(data):,} languages")


if __name__ == "__main__":
    main()
