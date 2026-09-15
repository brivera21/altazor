#!/usr/bin/env python3
"""Generate cell.html, The Cell: three cells to one scale, their parts answering.

Four views of one stage. Together sets an animal cell, a plant cell and a
bacterium on one scale, with a red blood cell, a yeast cell, the edge of a
human egg and a virus for company, so the ratio is the first thing seen. The
other three each fill the stage with one cell, its parts drawn to that scale
where they can be and named where they cannot, each answering when touched
with its size, its count and its work.

Data: tools/cell_data.py.

Usage: python3 build_cell.py
"""

import json
from pathlib import Path

import apa
from cell_data import CELLS, PARTS, EXTRAS, FACTS, REFS

OUT = Path(__file__).parent.parent / "cell.html"

NOTE1 = ("Together sets the three cells on one scale: an animal cell fifteen "
         "microns across, a plant cell forty by twenty, and a bacterium two "
         "microns long with a two thousandth of the animal cell's volume, beside a "
         "red blood cell, a yeast, the edge of a human egg and a virus one "
         "pixel wide. Everything alive is built of things in this range, and "
         "a body holds some thirty trillion of them.")

NOTE2 = ("The other three views each fill the stage with one cell, its parts "
         "drawn at that scale where they can be and named where they cannot: "
         "a membrane seven nanometres thick is a line, a ribosome a stipple. "
         "A part under the cursor gives its size, how many the cell has, "
         "what share of the cell it takes, and what it does. Counts are the "
         "round numbers of Cell Biology by the Numbers.")

METHOD = ("A typical animal cell is taken as fifteen microns across, a leaf "
          "mesophyll cell as forty by twenty, E. coli as two by 0.8; real "
          "cells of each kind vary by a factor of two or more around these, "
          "and a liver cell's thousand mitochondria are a hundred in a "
          "smaller cell. Only a handful of the mitochondria, chloroplasts and "
          "lysosomes are drawn, and the ribosomes as a texture; the "
          "bacterium's ribosomes are each drawn, at roughly their size. The "
          "shapes are diagrams of a typical section, not tracings of a "
          "micrograph.")


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


parts = [{"k": k, "cell": c, "n": n, "size": sz, "count": ct, "share": sh, "b": b, "s": s}
         for k, c, n, sz, ct, sh, b, s in PARTS]
cells = [{"k": k, "n": n, "a": a, "b": b, "txt": t} for k, n, a, b, t in CELLS]
extras = [{"k": k, "n": n, "a": a, "b": b, "kind": kind, "txt": t} for k, n, a, b, kind, t in EXTRAS]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Cell &middot; Altazor</title>
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
.bar { display:flex; gap:6px; flex-wrap:wrap; margin:0 0 12px; }
.bar button { background:var(--panel); color:var(--muted); border:1px solid var(--line);
  border-radius:999px; padding:6px 14px; font-size:13.5px; cursor:pointer; font-family:inherit; }
.bar button:hover { color:var(--text); border-color:#3d3d3d; }
.bar button.on { color:#0b0b0b; background:var(--accent); border-color:var(--accent); font-weight:700; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; }
#diagram svg { width:100%; height:auto; display:block; user-select:none; }
.side { flex:0 0 300px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:16px; }
#kindTxt { font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
#nameTxt { font-weight:700; font-size:17px; margin:2px 0 6px; }
#numTxt { font-size:13.5px; line-height:1.55; }
#numTxt b { color:var(--muted); font-weight:400; }
#bodyTxt { color:var(--muted); font-size:13.5px; line-height:1.55; margin-top:9px; }
#srcTxt { color:var(--muted); font-size:12px; margin-top:10px; border-top:1px solid var(--line); padding-top:8px; }
.tiles { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:10px; margin:16px 0 0; max-width:900px; }
.tile { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:11px 14px; }
.tile .k { font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.07em; }
.tile .v { font-size:1.1rem; font-weight:650; margin-top:3px; }
.tile .d { font-size:.76rem; color:var(--muted); margin-top:2px; }
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
  <nav class="site"><a href="library.html">&larr; Library &middot; Life</a><a href="tree-of-life.html">Tree of Life</a><a href="body.html">The Human Body</a><a href="scale.html">Scale</a></nav>
</header>
<h1>The Cell</h1>
<div class="bar" id="views">
  <button data-v="all" class="on">Together, to scale</button>
  <button data-v="animal">An animal cell</button>
  <button data-v="plant">A plant cell</button>
  <button data-v="bacterium">A bacterium</button>
</div>
<div class="stage">
  <div id="diagram"></div>
  <div class="side"><div class="card">
    <div id="kindTxt"></div>
    <div id="nameTxt">A part under the cursor lands here</div>
    <div id="numTxt"></div>
    <div id="bodyTxt"></div>
    <div id="srcTxt"></div>
  </div></div>
</div>
<div class="tiles">__FACTS__</div>
<p class="note">__NOTE1__</p>
<p class="note" style="border-top:none; padding-top:0;">__NOTE2__</p>
<div class="method"><p>__METHOD__</p></div>
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</div>
<script>
const CELLS=__CELLS__, PARTS=__PARTS__, EXTRAS=__EXTRAS__;
const W=980, H=720;
const el=document.getElementById('diagram');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
let view='all', hot=null, seed=5;
function rnd(){ seed=(seed*1103515245+12345)&0x7fffffff; return seed/0x7fffffff; }
const C={membrane:'#cfd6e6', nucleus:'#b48cf2', nucleolus:'#8f5fe0', mito:'#ffb02e', er:'#6ee7f2', golgi:'#f28cb0',
  lyso:'#e0a458', ribo:'#f4efe2', cyto:'#58a6ff', wall:'#9be564', vacuole:'#2f6f8f', chloro:'#31d67a', dna:'#b48cf2', flag:'#cfd6e6'};

/* ---- the card ---- */
function card(kind,name,rows,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').textContent=name;
  document.getElementById('numTxt').innerHTML=rows.filter(r=>r[1]).map(([k,v])=>'<b>'+esc(k)+'</b> '+esc(v)).join('<br>');
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').textContent=src;
}
function showPart(k){
  const p=PARTS.find(x=>x.k===k); if(!p) return;
  const c=CELLS.find(x=>x.k===p.cell);
  card('A part of '+c.n.toLowerCase(), p.n, [['size',p.size],['how many',p.count],['share',p.share]], p.b, p.s);
}
function showCell(k){
  const c=CELLS.find(x=>x.k===k); if(!c){ const e=EXTRAS.find(x=>x.k===k); if(e) card('On the shared scale', e.n, [['size',e.a===e.b?e.a+' microns across':e.a+' by '+e.b+' microns']], e.txt, 'Milo and Phillips 2015'); return; }
  card('A whole cell', c.n, [['size', c.a===c.b?c.a+' microns across':c.a+' by '+c.b+' microns'],
    ['volume', c.k==='animal'?'about 1,800 cubic microns':c.k==='plant'?'about 12,000 cubic microns':'about 1 cubic micron']], c.txt, 'Milo and Phillips 2015');
}

/* ---- pieces ---- */
function mito(x,y,w,h,rot,k){
  // an ellipse with a folded inner membrane
  let s='<g data-k="'+k+'" style="cursor:pointer" transform="translate('+x+','+y+') rotate('+rot+')">';
  s+='<ellipse cx="0" cy="0" rx="'+w/2+'" ry="'+h/2+'" fill="'+C.mito+'" fill-opacity="0.22" stroke="'+C.mito+'" stroke-width="1.4"/>';
  s+='<ellipse cx="0" cy="0" rx="'+(w/2-h*0.18)+'" ry="'+(h/2-h*0.18)+'" fill="none" stroke="'+C.mito+'" stroke-width="1" stroke-opacity="0.8"/>';
  for(let i=-2;i<=2;i++){ const cx=i*w*0.16; s+='<path d="M'+cx+','+(-h*0.32)+' q'+(h*0.12)+','+(h*0.3)+' 0,'+(h*0.6)+'" fill="none" stroke="'+C.mito+'" stroke-width="1" stroke-opacity="0.8"/>'; }
  return s+'</g>';
}
function chloro(x,y,w,h,rot,k){
  let s='<g data-k="'+k+'" style="cursor:pointer" transform="translate('+x+','+y+') rotate('+rot+')">';
  s+='<ellipse cx="0" cy="0" rx="'+w/2+'" ry="'+h/2+'" fill="'+C.chloro+'" fill-opacity="0.28" stroke="'+C.chloro+'" stroke-width="1.4"/>';
  for(let i=-2;i<=2;i++){ const cx=i*w*0.17; for(let j=-1;j<=1;j++) s+='<rect x="'+(cx-w*0.055)+'" y="'+(j*h*0.16-h*0.05)+'" width="'+(w*0.11)+'" height="'+(h*0.1)+'" fill="'+C.chloro+'" fill-opacity="0.85"/>'; }
  return s+'</g>';
}
function ribosomes(cx,cy,r,n,size,k,hollow){
  // a stipple inside a circle, avoiding a hollow circle (the nucleus)
  seed=17; let s='<g data-k="'+k+'" style="cursor:pointer">';
  for(let i=0;i<n;i++){
    const a=rnd()*6.283, d=Math.sqrt(rnd())*r*0.93, x=cx+d*Math.cos(a), y=cy+d*Math.sin(a);
    if(hollow && Math.hypot(x-hollow[0],y-hollow[1])<hollow[2]+4) continue;
    s+='<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="'+size+'" fill="'+C.ribo+'" fill-opacity="0.55"/>';
  }
  return s+'</g>';
}
function scalebar(x,y,px,label){
  return '<line x1="'+x+'" y1="'+y+'" x2="'+(x+px)+'" y2="'+y+'" stroke="#9a9a9a" stroke-width="2"/>'+
    '<text x="'+x+'" y="'+(y-8)+'" font-size="11" fill="#9a9a9a">'+label+'</text>';
}
const hi=k=>hot===k?' filter="url(#glow)"':'';

/* ---- the animal cell ---- */
function animal(){
  const k=38, cx=470, cy=360, R=7.5*k;           // px per micron, 15 microns across
  let s='';
  s+='<g data-k="a_cytosol" style="cursor:pointer"><circle cx="'+cx+'" cy="'+cy+'" r="'+R+'" fill="#1b2230"/></g>';
  s+=ribosomes(cx,cy,R,1400,0.9,'a_ribo',[cx-60,cy-20,3.1*k]);
  // cytoskeleton: microtubules from the centrosome
  let cs='<g data-k="a_cyto" style="cursor:pointer">';
  const ccx=cx+70, ccy=cy+30;
  for(let i=0;i<22;i++){ const a=i/22*6.283, L=R*0.95; const ex=cx+L*Math.cos(a), ey=cy+L*Math.sin(a);
    cs+='<line x1="'+ccx+'" y1="'+ccy+'" x2="'+ex.toFixed(1)+'" y2="'+ey.toFixed(1)+'" stroke="'+C.cyto+'" stroke-opacity="0.16" stroke-width="1"/>'; }
  cs+='<circle cx="'+cx+'" cy="'+cy+'" r="'+(R-6)+'" fill="none" stroke="'+C.cyto+'" stroke-opacity="0.25" stroke-width="3"/></g>';
  s+=cs;
  // ER around the nucleus
  let er='<g data-k="a_er" style="cursor:pointer">';
  for(let i=0;i<4;i++){ const rr=3.1*k+14+i*14; er+='<path d="M'+(cx-60+rr*Math.cos(-0.6))+','+(cy-20+rr*Math.sin(-0.6))+' A'+rr+','+rr+' 0 0 1 '+(cx-60+rr*Math.cos(1.9))+','+(cy-20+rr*Math.sin(1.9))+'" fill="none" stroke="'+C.er+'" stroke-width="'+(i<2?3:2)+'" stroke-opacity="'+(i<2?0.8:0.5)+'"'+(i<2?' stroke-dasharray="2 3"':'')+'/>'; }
  er+='</g>'; s+=er;
  // Golgi: a stack of curved bands
  let g='<g data-k="a_golgi" style="cursor:pointer" transform="translate('+(cx+95)+','+(cy-70)+') rotate(-30)">';
  for(let i=0;i<6;i++) g+='<path d="M-32,'+(i*7-18)+' q32,-12 64,0" fill="none" stroke="'+C.golgi+'" stroke-width="3.5" stroke-linecap="round" stroke-opacity="'+(0.95-i*0.1)+'"/>';
  g+='</g>'; s+=g;
  // mitochondria
  const M=[[cx+120,cy+90,-20],[cx-30,cy+150,30],[cx+150,cy+10,70],[cx-150,cy+110,-50],[cx+40,cy-190,10],[cx-190,cy-60,80],[cx+185,cy+120,40],[cx-110,cy+200,0]];
  for(const [x,y,r] of M) s+=mito(x,y,1.6*k,0.65*k,r,'a_mito');
  // lysosomes and vesicles
  let ly='<g data-k="a_lyso" style="cursor:pointer">';
  for(const [x,y] of [[cx+170,cy-120],[cx+30,cy+210],[cx-200,cy+40],[cx+210,cy+60],[cx-120,cy-170],[cx+90,cy+170]]) ly+='<circle cx="'+x+'" cy="'+y+'" r="'+(0.3*k)+'" fill="'+C.lyso+'" fill-opacity="0.5" stroke="'+C.lyso+'"/>';
  ly+='</g>'; s+=ly;
  let ve='<g data-k="a_vesicle" style="cursor:pointer">'; seed=9;
  for(let i=0;i<26;i++){ const a=rnd()*6.283, d=(0.55+0.4*rnd())*R; ve+='<circle cx="'+(cx+d*Math.cos(a)).toFixed(1)+'" cy="'+(cy+d*Math.sin(a)).toFixed(1)+'" r="'+(1.5+rnd()*1.5).toFixed(1)+'" fill="none" stroke="'+C.membrane+'" stroke-opacity="0.6"/>'; }
  ve+='</g>'; s+=ve;
  // centrosome
  s+='<g data-k="a_centro" style="cursor:pointer"><rect x="'+(ccx-8)+'" y="'+(ccy-2.5)+'" width="16" height="5" fill="'+C.cyto+'"/><rect x="'+(ccx+9)+'" y="'+(ccy-10)+'" width="5" height="16" fill="'+C.cyto+'"/><circle cx="'+ccx+'" cy="'+ccy+'" r="14" fill="transparent"/></g>';
  // nucleus with pores, and the nucleolus
  const nx=cx-60, ny=cy-20, nr=3.1*k;
  s+='<g data-k="a_nucleus" style="cursor:pointer"><circle cx="'+nx+'" cy="'+ny+'" r="'+nr+'" fill="'+C.nucleus+'" fill-opacity="0.22" stroke="'+C.nucleus+'" stroke-width="2"/>'+
     '<circle cx="'+nx+'" cy="'+ny+'" r="'+(nr-5)+'" fill="none" stroke="'+C.nucleus+'" stroke-width="1" stroke-opacity="0.7"/>';
  for(let i=0;i<18;i++){ const a=i/18*6.283; s+='<circle cx="'+(nx+(nr-2.5)*Math.cos(a)).toFixed(1)+'" cy="'+(ny+(nr-2.5)*Math.sin(a)).toFixed(1)+'" r="2.2" fill="#121212" stroke="'+C.nucleus+'" stroke-width="1"/>'; }
  seed=3; for(let i=0;i<90;i++){ const a=rnd()*6.283, d=Math.sqrt(rnd())*(nr-10); s+='<circle cx="'+(nx+d*Math.cos(a)).toFixed(1)+'" cy="'+(ny+d*Math.sin(a)).toFixed(1)+'" r="1.3" fill="'+C.nucleus+'" fill-opacity="0.5"/>'; }
  s+='</g>';
  s+='<g data-k="a_nucleolus" style="cursor:pointer"><circle cx="'+(nx+22)+'" cy="'+(ny+10)+'" r="'+(0.8*k)+'" fill="'+C.nucleolus+'" fill-opacity="0.7"/></g>';
  // the membrane
  s+='<g data-k="a_membrane" style="cursor:pointer"><circle cx="'+cx+'" cy="'+cy+'" r="'+R+'" fill="none" stroke="'+C.membrane+'" stroke-width="2"/><circle cx="'+cx+'" cy="'+cy+'" r="'+R+'" fill="none" stroke="transparent" stroke-width="14"/></g>';
  s+=scalebar(40,H-30,5*k,'5 microns');
  s+='<text x="'+(W-20)+'" y="'+(H-26)+'" text-anchor="end" font-size="11" fill="#6b7280">a typical animal cell, 15 microns across, in section</text>';
  return s;
}

/* ---- the plant cell ---- */
function plant(){
  const k=20, x0=80, y0=140, w=40*k, h=20*k, r=22;
  let s='';
  s+='<g data-k="p_wall" style="cursor:pointer"><rect x="'+(x0-10)+'" y="'+(y0-10)+'" width="'+(w+20)+'" height="'+(h+20)+'" rx="'+(r+8)+'" fill="'+C.wall+'" fill-opacity="0.22" stroke="'+C.wall+'" stroke-width="2"/></g>';
  s+='<g data-k="p_membrane" style="cursor:pointer"><rect x="'+x0+'" y="'+y0+'" width="'+w+'" height="'+h+'" rx="'+r+'" fill="#1b2a22" stroke="'+C.membrane+'" stroke-width="1.6"/></g>';
  // cytoplasm stipple
  seed=21; let st='<g data-k="p_er" style="cursor:pointer">';
  for(let i=0;i<500;i++){ const x=x0+rnd()*w, y=y0+rnd()*h; if(x>x0+90&&x<x0+w-150&&y>y0+55&&y<y0+h-55) continue; st+='<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="0.8" fill="'+C.ribo+'" fill-opacity="0.45"/>'; }
  for(let i=0;i<3;i++) st+='<path d="M'+(x0+130+i*16)+','+(y0+h-20)+' q30,-20 60,0" fill="none" stroke="'+C.er+'" stroke-width="2" stroke-dasharray="2 3" stroke-opacity="0.8"/>';
  for(let i=0;i<5;i++) st+='<path d="M'+(x0+w-130)+','+(y0+90+i*6)+' q24,-8 48,0" fill="none" stroke="'+C.golgi+'" stroke-width="2.6" stroke-opacity="'+(0.9-i*0.12)+'"/>';
  st+='</g>'; s+=st;
  // the vacuole
  s+='<g data-k="p_vacuole" style="cursor:pointer"><rect x="'+(x0+90)+'" y="'+(y0+55)+'" width="'+(w-240)+'" height="'+(h-110)+'" rx="40" fill="'+C.vacuole+'" fill-opacity="0.35" stroke="'+C.vacuole+'" stroke-width="1.5"/>'+
     '<text x="'+(x0+w/2-75)+'" y="'+(y0+h/2+4)+'" text-anchor="middle" font-size="12" fill="#6ea3c0" pointer-events="none">the vacuole, water under pressure</text></g>';
  // chloroplasts along the edges
  const CH=[[x0+60,y0+28,8],[x0+165,y0+26,-6],[x0+270,y0+28,6],[x0+375,y0+26,-8],[x0+480,y0+30,10],[x0+585,y0+34,-12],[x0+700,y0+40,20],
    [x0+110,y0+h-28,-6],[x0+215,y0+h-26,6],[x0+320,y0+h-30,-8],[x0+425,y0+h-26,8],[x0+530,y0+h-30,-10],[x0+38,y0+110,80],[x0+40,y0+215,84],[x0+w-40,y0+130,86]];
  for(const [x,y,ro] of CH) s+=chloro(x,y,5*k,2.3*k,ro,'p_chloro');
  // mitochondria, small
  for(const [x,y,ro] of [[x0+42,y0+300,80],[x0+660,y0+h-45,-20],[x0+660,y0+170,60],[x0+700,y0+250,10],[x0+80,y0+330,40]]) s+=mito(x,y,1.2*k,0.55*k,ro,'p_mito');
  // nucleus pushed to a side
  const nx=x0+w-85, ny=y0+h-90, nr=2.5*k;
  s+='<g data-k="p_nucleus" style="cursor:pointer"><circle cx="'+nx+'" cy="'+ny+'" r="'+nr+'" fill="'+C.nucleus+'" fill-opacity="0.25" stroke="'+C.nucleus+'" stroke-width="2"/><circle cx="'+(nx+10)+'" cy="'+(ny+6)+'" r="'+(0.7*k)+'" fill="'+C.nucleolus+'" fill-opacity="0.7"/></g>';
  // plasmodesmata through the wall
  let pd='<g data-k="p_plasmo" style="cursor:pointer">';
  for(const x of [x0+200,x0+230,x0+560,x0+590]) pd+='<rect x="'+(x-2)+'" y="'+(y0-12)+'" width="4" height="14" fill="'+C.membrane+'"/><rect x="'+(x-2)+'" y="'+(y0+h-2)+'" width="4" height="14" fill="'+C.membrane+'"/><rect x="'+(x-8)+'" y="'+(y0-16)+'" width="16" height="22" fill="transparent"/><rect x="'+(x-8)+'" y="'+(y0+h-6)+'" width="16" height="22" fill="transparent"/>';
  pd+='</g>'; s+=pd;
  s+=scalebar(40,H-30,10*k,'10 microns');
  s+='<text x="'+(W-20)+'" y="'+(H-26)+'" text-anchor="end" font-size="11" fill="#6b7280">a leaf mesophyll cell, 40 by 20 microns, in section</text>';
  return s;
}

/* ---- the bacterium ---- */
function bacterium(){
  const k=290, cx=470, cy=340, L=2.0*k, D=0.8*k;      // px per micron
  let s='';
  // flagella, cut off at the stage edge
  let fl='<g data-k="b_flagellum" style="cursor:pointer">';
  for(const [sx,sy,dir] of [[cx+L/2-20,cy-40,1],[cx+L/2-10,cy+30,1],[cx-L/2+20,cy+60,-1],[cx-L/2+10,cy-50,-1],[cx+L/2-30,cy+90,1]]){
    let d='M'+sx+','+sy; for(let i=1;i<=9;i++){ d+=' q'+(dir*30)+','+(i%2?-28:28)+' '+(dir*60)+',0'; }
    fl+='<path d="'+d+'" fill="none" stroke="'+C.flag+'" stroke-width="5.8" stroke-opacity="0.75" stroke-linecap="round"/>';
  }
  fl+='</g>'; s+=fl;
  // pili
  let pi='<g data-k="b_pili" style="cursor:pointer">'; seed=13;
  for(let i=0;i<60;i++){ const a=rnd()*6.283, px=cx+(L/2-D/2)*Math.cos(a)*(Math.abs(Math.cos(a))>0.5?1:0)+D/2*Math.cos(a), py=cy+D/2*Math.sin(a);
    const len=40+rnd()*90; pi+='<line x1="'+px.toFixed(1)+'" y1="'+py.toFixed(1)+'" x2="'+(px+len*Math.cos(a)).toFixed(1)+'" y2="'+(py+len*Math.sin(a)).toFixed(1)+'" stroke="'+C.membrane+'" stroke-width="1" stroke-opacity="0.35"/>'; }
  pi+='</g>'; s+=pi;
  // envelope: outer membrane, wall, inner membrane, 30 nm in all
  s+='<g data-k="b_envelope" style="cursor:pointer"><rect x="'+(cx-L/2)+'" y="'+(cy-D/2)+'" width="'+L+'" height="'+D+'" rx="'+(D/2)+'" fill="#1e2433" stroke="'+C.membrane+'" stroke-width="2"/>'+
     '<rect x="'+(cx-L/2+4)+'" y="'+(cy-D/2+4)+'" width="'+(L-8)+'" height="'+(D-8)+'" rx="'+(D/2-4)+'" fill="none" stroke="'+C.wall+'" stroke-width="1.5" stroke-opacity="0.8"/>'+
     '<rect x="'+(cx-L/2+8)+'" y="'+(cy-D/2+8)+'" width="'+(L-16)+'" height="'+(D-16)+'" rx="'+(D/2-8)+'" fill="none" stroke="'+C.membrane+'" stroke-width="1.5"/></g>';
  s+='<g data-k="b_cytoplasm" style="cursor:pointer"><rect x="'+(cx-L/2+10)+'" y="'+(cy-D/2+10)+'" width="'+(L-20)+'" height="'+(D-20)+'" rx="'+(D/2-10)+'" fill="transparent"/></g>';
  // ribosomes, each drawn at about 20 nm
  seed=29; let rb='<g data-k="b_ribo" style="cursor:pointer">';
  for(let i=0;i<420;i++){ const x=cx-L/2+14+rnd()*(L-28), y=cy-D/2+14+rnd()*(D-28);
    if(Math.pow((x-cx)/(L/2-14),2)+Math.pow((y-cy)/(D/2-14),2)>1 && Math.abs(x-cx)>L/2-D/2) continue;
    if(Math.abs(x-cx)<L*0.27 && Math.abs(y-cy)<D*0.26 && rnd()<0.75) continue;
    rb+='<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="2.9" fill="'+C.ribo+'" fill-opacity="0.7"/>'; }
  rb+='</g>'; s+=rb;
  // the nucleoid: a folded loop
  seed=41; let d='M'+(cx-L*0.26)+','+cy;
  for(let i=0;i<14;i++){ d+=' q'+(L*0.04)+','+((i%2?-1:1)*D*0.28)+' '+(L*0.04)+',0'; }
  s+='<g data-k="b_nucleoid" style="cursor:pointer"><ellipse cx="'+cx+'" cy="'+cy+'" rx="'+(L*0.3)+'" ry="'+(D*0.32)+'" fill="'+C.dna+'" fill-opacity="0.12"/>'+
     '<path d="'+d+'" fill="none" stroke="'+C.dna+'" stroke-width="2.2" stroke-opacity="0.9"/>'+
     '<path d="M'+(cx-L*0.26)+','+(cy+8)+' q'+(L*0.28)+','+(D*0.3)+' '+(L*0.56)+',-8" fill="none" stroke="'+C.dna+'" stroke-width="2.2" stroke-opacity="0.7"/></g>';
  s+='<g data-k="b_plasmid" style="cursor:pointer"><circle cx="'+(cx+L*0.36)+'" cy="'+(cy-D*0.2)+'" r="9" fill="none" stroke="'+C.dna+'" stroke-width="2"/><circle cx="'+(cx+L*0.36)+'" cy="'+(cy-D*0.2)+'" r="14" fill="transparent"/></g>';
  s+=scalebar(40,H-30,0.5*k,'0.5 microns, 500 nm');
  s+='<text x="'+(W-20)+'" y="'+(H-26)+'" text-anchor="end" font-size="11" fill="#6b7280">E. coli, 2 microns by 0.8; the flagella run on for several cell lengths</text>';
  return s;
}

/* ---- together, on one scale ---- */
function together(){
  const k=11, base=420;                            // px per micron
  let s='';
  // the egg's edge, a great arc
  // the egg's edge, a great arc across the top right corner
  const eggR=60*k, ex=W+eggR-330, ey=-eggR+250;
  s+='<g data-k="egg" style="cursor:pointer"><circle cx="'+ex+'" cy="'+ey+'" r="'+eggR+'" fill="#f4efe2" fill-opacity="0.05" stroke="#f4efe2" stroke-opacity="0.5" stroke-width="2" stroke-dasharray="6 5"/>'+
     '<text x="'+(W-24)+'" y="'+(ey+eggR-16)+'" text-anchor="end" font-size="11.5" fill="#cfd6e6">a human egg cell, 120 microns: its edge, the rest off the stage</text></g>';
  // plant cell
  const pw=40*k, ph=20*k, px=30, py=base-ph/2;
  s+='<g data-k="plant" style="cursor:pointer"><rect x="'+(px-4)+'" y="'+(py-4)+'" width="'+(pw+8)+'" height="'+(ph+8)+'" rx="18" fill="'+C.wall+'" fill-opacity="0.25" stroke="'+C.wall+'" stroke-width="1.5"/>'+
     '<rect x="'+(px+40)+'" y="'+(py+30)+'" width="'+(pw-80)+'" height="'+(ph-60)+'" rx="20" fill="'+C.vacuole+'" fill-opacity="0.35"/>';
  for(let i=0;i<7;i++) s+='<ellipse cx="'+(px+40+i*58)+'" cy="'+(py+16)+'" rx="'+(2.5*k)+'" ry="'+(1.15*k)+'" fill="'+C.chloro+'" fill-opacity="0.5"/><ellipse cx="'+(px+50+i*58)+'" cy="'+(py+ph-16)+'" rx="'+(2.5*k)+'" ry="'+(1.15*k)+'" fill="'+C.chloro+'" fill-opacity="0.5"/>';
  s+='<circle cx="'+(px+pw-45)+'" cy="'+(py+ph-45)+'" r="'+(2.5*k)+'" fill="'+C.nucleus+'" fill-opacity="0.4"/>';
  s+='<text x="'+(px+pw/2)+'" y="'+(py+ph+22)+'" text-anchor="middle" font-size="12" fill="#cfd6e6">a plant cell, 40 by 20 microns</text></g>';
  // animal cell
  const ax=px+pw+110, ar=7.5*k;
  s+='<g data-k="animal" style="cursor:pointer"><circle cx="'+ax+'" cy="'+base+'" r="'+ar+'" fill="#1b2230" stroke="'+C.membrane+'" stroke-width="1.5"/>'+
     '<circle cx="'+(ax-15)+'" cy="'+(base-8)+'" r="'+(3*k)+'" fill="'+C.nucleus+'" fill-opacity="0.35" stroke="'+C.nucleus+'"/>';
  for(const [dx,dy,ro] of [[45,40,20],[-40,50,-30],[50,-40,60],[-55,-35,10]]) s+='<ellipse cx="'+(ax+dx)+'" cy="'+(base+dy)+'" rx="'+(0.8*k)+'" ry="'+(0.33*k)+'" transform="rotate('+ro+' '+(ax+dx)+' '+(base+dy)+')" fill="'+C.mito+'" fill-opacity="0.6"/>';
  s+='<text x="'+ax+'" y="'+(base+ar+22)+'" text-anchor="middle" font-size="12" fill="#cfd6e6">an animal cell, 15 microns</text></g>';
  // red blood cell, seen edge on and face on
  const rx=ax+ar+70;
  s+='<g data-k="rbc" style="cursor:pointer"><circle cx="'+rx+'" cy="'+(base-30)+'" r="'+(3.9*k)+'" fill="#c0392b" fill-opacity="0.55" stroke="#e06060"/><circle cx="'+rx+'" cy="'+(base-30)+'" r="'+(1.6*k)+'" fill="#121212" fill-opacity="0.35"/>'+
     '<rect x="'+(rx-3.9*k)+'" y="'+(base+30)+'" width="'+(7.8*k)+'" height="'+(2*k)+'" rx="'+k+'" fill="#c0392b" fill-opacity="0.55" stroke="#e06060"/>'+
     '<text x="'+rx+'" y="'+(base+80)+'" text-anchor="middle" font-size="12" fill="#cfd6e6">a red blood cell, 7.8</text></g>';
  // yeast
  const yx=rx+85;
  s+='<g data-k="yeast" style="cursor:pointer"><circle cx="'+yx+'" cy="'+(base-10)+'" r="'+(2*k)+'" fill="#e0a458" fill-opacity="0.45" stroke="#e0a458"/><circle cx="'+(yx+16)+'" cy="'+(base-26)+'" r="'+(0.9*k)+'" fill="#e0a458" fill-opacity="0.45" stroke="#e0a458"/>'+
     '<text x="'+yx+'" y="'+(base+50)+'" text-anchor="middle" font-size="12" fill="#cfd6e6">a yeast, 4</text></g>';
  // E. coli and the virus
  const bx=yx+70;
  s+='<g data-k="bacterium" style="cursor:pointer"><rect x="'+(bx-k)+'" y="'+(base-0.4*k)+'" width="'+(2*k)+'" height="'+(0.8*k)+'" rx="'+(0.4*k)+'" fill="'+C.membrane+'" fill-opacity="0.8"/>'+
     '<rect x="'+(bx-20)+'" y="'+(base-16)+'" width="40" height="32" fill="transparent"/>'+
     '<text x="'+bx+'" y="'+(base+74)+'" text-anchor="middle" font-size="12" fill="#cfd6e6">E. coli, 2 by 0.8</text></g>';
  s+='<g data-k="virus" style="cursor:pointer"><rect x="'+(bx+50)+'" y="'+(base-0.5)+'" width="1.1" height="1.1" fill="#f4efe2"/><rect x="'+(bx+38)+'" y="'+(base-12)+'" width="24" height="24" fill="transparent"/>'+
     '<line x1="'+(bx+50)+'" y1="'+(base+6)+'" x2="'+(bx+50)+'" y2="'+(base+26)+'" stroke="#6b7280"/><text x="'+(bx+50)+'" y="'+(base+40)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">a virus, 0.1</text></g>';
  s+=scalebar(40,H-30,10*k,'10 microns');
  s+='<text x="'+(W-20)+'" y="'+(H-26)+'" text-anchor="end" font-size="11" fill="#6b7280">all on one scale; sizes in microns</text>';
  return s;
}

function render(){
  const body= view==='animal'?animal(): view==='plant'?plant(): view==='bacterium'?bacterium(): together();
  el.innerHTML='<svg viewBox="0 0 '+W+' '+H+'" xmlns="http://www.w3.org/2000/svg" id="csvg"><rect width="'+W+'" height="'+H+'" fill="#121212"/>'+body+'</svg>';
  if(hot){ const g=el.querySelector('[data-k="'+hot+'"]'); if(g) g.style.filter='drop-shadow(0 0 6px #58a6ff)'; }
}
el.addEventListener('pointerover',e=>{ const g=e.target.closest('[data-k]'); if(!g) return; hot=g.getAttribute('data-k');
  if(PARTS.find(p=>p.k===hot)) showPart(hot); else showCell(hot); render(); });
el.addEventListener('click',e=>{ const g=e.target.closest('[data-k]'); if(!g) return; const k=g.getAttribute('data-k');
  if(view==='all' && CELLS.find(c=>c.k===k)) setView(k); });
function setView(v){ view=v; hot=null; for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on',b.dataset.v===v); render();
  showCell(v==='all'?'animal':v); if(v==='all') card('Three cells on one scale','Together',[['animal cell','15 microns'],['plant cell','40 by 20 microns'],['bacterium','2 by 0.8 microns']],
    'The bacterium has about a two thousandth of the animal cell\\u2019s volume; the plant cell about nine times it, most of that the vacuole. A click on a cell opens it.','Milo and Phillips 2015'); }
document.getElementById('views').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setView(b.dataset.v); });
setView('all');
window.__cell=()=>({view,hot,parts:PARTS.length,marks:document.querySelectorAll('#csvg [data-k]').length,
  keys:[...new Set([...document.querySelectorAll('#csvg [data-k]')].map(g=>g.getAttribute('data-k')))]});
</script>
</body>
</html>
"""

facts = "\n".join(f'<div class="tile"><div class="k">{k}</div><div class="v">{v}</div><div class="d">{s}</div></div>'
                  for k, v, s in FACTS)
html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__CELLS__", _js(cells)).replace("__PARTS__", _js(parts)).replace("__EXTRAS__", _js(extras))
        .replace("__FACTS__", facts)
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(CELLS)} cells, {len(PARTS)} parts, {len(EXTRAS)} extras")
