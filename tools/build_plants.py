#!/usr/bin/env python3
"""Generate plants.html, Plants: the parts, the light, and the kinds.

Three views. The parts: a flowering plant in outline, roots to flower, with
the water going up and the sugar coming down, each part answering under the
pointer. The light: the visible spectrum with the absorption of chlorophyll a
and b drawn over it, a marker that drags along the wavelengths, and the
photosynthesis equation with its numbers. The kinds: the four groups of land
plants as bars by species count, placed on the timeline of their first
appearance.

Data: tools/plants_data.py.

Usage: python3 build_plants.py
"""

import json
from pathlib import Path

import apa
from plants_data import PARTS, CHLOROPHYLL, PHOTO, KINDS, REFS

OUT = Path(__file__).parent.parent / "plants.html"

NOTE1 = ("A plant is a machine for standing in the light. Roots hold it "
         "and draw water; the stem lifts the leaves and runs two pipelines, "
         "water up and sugar down; the leaves catch light and swap gases "
         "through pores; the flower is for sex and the fruit for travel. "
         "Every part is under the pointer, with what it does and one number "
         "that says how much.")

NOTE2 = ("The second view is the light itself. Chlorophyll takes the blue "
         "and the red and lets the green through, which is why leaves are "
         "the color they are, and what it takes goes into pulling carbon "
         "dioxide and water apart and rebuilding them as sugar, with oxygen "
         "left over: a hundred billion metric tons of carbon a year, half on "
         "land, half in the sea. The third view is who does it: four kinds "
         "of land plant, and when each arrived.")

METHOD = ("The plant is a diagram, not a species. The absorption curves are "
          "drawn as sums of Gaussians at the measured peaks of chlorophyll a "
          "and b in ether, 430 and 662 nm and 453 and 642, with the relative "
          "heights of the published spectra; in a leaf the peaks shift a "
          "few nanometers and other pigments fill in some of the green. The "
          "spectrum's colors come from the CIE matching functions, as on "
          "the Light page. Production is Field and colleagues' 1998 "
          "estimate, still the standard one; species counts are Kew's, "
          "which change with every revision; the dates of first appearance "
          "are the fossil record's and are argued over by tens of millions "
          "of years.")


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


parts = [{"k": k, "n": n, "b": b, "num": num, "s": s} for k, n, b, num, s in PARTS]
kinds = [{"k": k, "n": n, "sp": sp, "ma": ma, "b": b, "s": s} for k, n, sp, ma, b, s in KINDS]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plants &middot; Altazor</title>
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
.bar button { background:var(--panel); color:var(--muted); border:1px solid var(--line);
  border-radius:999px; padding:6px 14px; font-size:13px; cursor:pointer; font-family:inherit; }
.bar button.on { background:var(--accent); color:#0b1a2b; border-color:var(--accent); font-weight:600; }
.bar button:hover { color:var(--text); border-color:#3d3d3d; }
.bar button.on:hover { color:#0b1a2b; }
.controls { display:flex; align-items:center; gap:12px; flex-wrap:wrap; margin:0 0 12px; min-height:34px; }
.controls label { font-size:13px; color:var(--muted); }
.controls output { font-size:13px; color:var(--text); font-variant-numeric:tabular-nums; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; }
#diagram svg { width:100%; height:auto; display:block; user-select:none; }
.side { flex:0 0 300px; min-width:0; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:16px; overflow-wrap:anywhere; }
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
  <nav class="site"><a href="library.html">&larr; Library &middot; Life</a><a href="cell.html">The Cell</a><a href="tree-of-life.html">Tree of Life</a><a href="light.html">Light</a></nav>
</header>
<h1>Plants</h1>
<div class="bar" id="views"><button data-v="parts" class="on">The parts</button><button data-v="light">The light</button><button data-v="kinds">The kinds</button></div>
<div class="controls" id="lightCtl" hidden><label>the marker</label><output id="lamOut"></output></div>
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
const PARTS=__PARTS__, CHL=__CHL__, PHOTO=__PHOTO__, KINDS=__KINDS__;
const W=980;
const el=document.getElementById('diagram');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
let view='parts', hot=null, lam=550, t0=performance.now();

/* ---- color, as on the Light page ---- */
const g=(l,mu,s1,s2)=>{ const s=l<mu?s1:s2; const t=(l-mu)/s; return Math.exp(-0.5*t*t); };
const xbar=l=>1.056*g(l,599.8,37.9,31.0)+0.362*g(l,442.0,16.0,26.7)-0.065*g(l,501.1,20.4,26.2);
const ybar=l=>0.821*g(l,568.8,46.9,40.5)+0.286*g(l,530.9,16.3,31.1);
const zbar=l=>1.217*g(l,437.0,11.8,36.0)+0.681*g(l,459.0,26.0,13.8);
function xyzToRgb(X,Y,Z){ let r=3.2406*X-1.5372*Y-0.4986*Z, gg=-0.9689*X+1.8758*Y+0.0415*Z, b=0.0557*X-0.2040*Y+1.0570*Z; const m=Math.min(r,gg,b); if(m<0){ r-=m; gg-=m; b-=m; } const mx=Math.max(r,gg,b)||1; return [r/mx,gg/mx,b/mx]; }
const gam=v=>v<=0.0031308?12.92*v:1.055*Math.pow(v,1/2.4)-0.055;
const hex=rgb=>'#'+rgb.map(v=>Math.round(255*Math.max(0,Math.min(1,gam(v)))).toString(16).padStart(2,'0')).join('');
function waveColor(nm){ const rgb=xyzToRgb(xbar(nm),ybar(nm),zbar(nm)); const br=Math.min(1,Math.max(xbar(nm),ybar(nm),zbar(nm))/0.6); return hex(rgb.map(v=>v*br)); }
const absorb=(k,nm)=>CHL[k].peaks.reduce((a,[mu,s,h])=>a+h*Math.exp(-0.5*((nm-mu)/s)**2),0);
const colorName=nm=>nm<450?'violet':nm<495?'blue':nm<570?'green':nm<590?'yellow':nm<620?'orange':'red';

/* ---- the card ---- */
function card(kind,name,rows,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').innerHTML=name;
  document.getElementById('numTxt').innerHTML=rows.filter(r=>r[1]).map(([k,v])=>'<b>'+esc(k)+'</b> '+v).join('<br>');
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').textContent=src;
}
function showPart(k){ const p=PARTS.find(x=>x.k===k); card('A part', esc(p.n), [['one number',esc(p.num)]], p.b, p.s); }
function showPlant(){ card('A flowering plant','Roots to flower',[['parts',PARTS.length]],'Each part under the pointer says what it does. The blue dots are water rising through the xylem; the orange ones are sugar going down through the phloem.','Wikipedia, Plant'); }
function showLam(nm){ const a=absorb('a',nm), b=absorb('b',nm);
  card('Light at', nm+' nm, '+colorName(nm), [['chlorophyll a absorbs',(a*100).toFixed(0)+'% of its strongest, the blue peak'],['chlorophyll b absorbs',(b*100).toFixed(0)+'% of its strongest'],['a leaf',a+b>0.5?'absorbs most of this and uses it':a+b>0.15?'takes some of this':'lets most of this through or bounces it back, which is why it looks green']],
    nm>=495&&nm<570?'Green is the light chlorophyll wants least, so it is the light that comes back out of a leaf and into an eye.':nm<495?'Blue light carries more energy than a photosynthesis step can use; the excess is shed as heat, and the sugar comes out the same as from red.':nm<620?'The gap between the two bands, where other pigments, the carotenoids, catch a little.':'Red light is the most efficient: nearly every red photon a leaf absorbs drives a step.', 'Wikipedia, Chlorophyll'); }
function showPhoto(){ card('Photosynthesis', PHOTO.equation, [['costs',PHOTO.energy_kj.toLocaleString('en-US')+' kJ a mole of sugar, from about 48 photons'],['the biosphere makes',PHOTO.npp_pg+' billion metric tons of carbon a year'],['on land',PHOTO.npp_land+', in the sea '+PHOTO.npp_ocean],['efficiency',PHOTO.efficiency]], 'Six molecules of carbon dioxide from the air and six of water from the roots, taken apart by light and put together as one sugar, with six of oxygen left over. Every calorie anyone eats, and every breath, comes from this line.', 'Field et al. 1998; Zhu et al. 2008; Wikipedia, Photosynthesis'); }
function showKind(k){ const x=KINDS.find(y=>y.k===k); const tot=KINDS.reduce((a,y)=>a+y.sp,0);
  card('A kind of plant', esc(x.n), [['species','about '+x.sp.toLocaleString('en-US')+', '+(x.sp/tot*100).toFixed(x.sp/tot<0.01?1:0)+'% of land plants'],['first appeared','about '+x.ma+' million years ago']], x.b, x.s); }
function showKinds(){ const tot=KINDS.reduce((a,y)=>a+y.sp,0); card('The kinds','Four groups of land plants',[['species in all','about '+tot.toLocaleString('en-US')],['flowering',(KINDS.find(k=>k.k==='flower').sp/tot*100).toFixed(0)+'% of them']],'Each bar is a group; its length is how many species, its place on the line is when it appeared.','Royal Botanic Gardens, Kew 2016; Wikipedia, Plant'); }

/* ---- the parts ---- */
function partsView(now){
  const cx=330, ground=420; let s='';
  s+='<rect x="40" y="'+ground+'" width="600" height="180" fill="#3a2f22" opacity="0.5"/><line x1="40" y1="'+ground+'" x2="640" y2="'+ground+'" stroke="#6b5a45"/>';
  const on=k=>hot===k;
  // roots
  s+='<g data-part="root" style="cursor:pointer">';
  for(const [dx,dy,c1x,c1y] of [[-140,120,-40,60],[-70,150,-20,80],[0,160,0,80],[70,150,20,80],[140,120,40,60],[-100,60,-30,30],[100,70,30,30]]) s+='<path d="M'+cx+','+ground+' Q'+(cx+c1x)+','+(ground+c1y)+' '+(cx+dx)+','+(ground+dy)+'" fill="none" stroke="'+(on('root')?'#e6e6e6':'#a08a6a')+'" stroke-width="'+(Math.abs(dx)<10?5:3)+'" stroke-linecap="round"/>';
  for(let i=0;i<40;i++){ const t=i/40; const dx=-140+280*t, dy=60+90*Math.sin(t*Math.PI)+((i*37)%23); s+='<line x1="'+(cx+dx)+'" y1="'+(ground+dy)+'" x2="'+(cx+dx+((i%2)?6:-6))+'" y2="'+(ground+dy+4)+'" stroke="'+(on('root')?'#e6e6e6':'#a08a6a')+'" stroke-width="1" opacity="0.7"/>'; }
  s+='<text x="'+(cx+170)+'" y="'+(ground+120)+'" font-size="11" fill="#9a9a9a">roots: water and minerals in</text></g>';
  // stem
  s+='<g data-part="stem" style="cursor:pointer"><path d="M'+(cx-9)+','+ground+' L'+(cx-7)+','+(ground-330)+' L'+(cx+7)+','+(ground-330)+' L'+(cx+9)+','+ground+' Z" fill="'+(on('stem')?'#5c8a4a':'#4a7a3a')+'" stroke="'+(on('stem')?'#e6e6e6':'#2f5a26')+'"/>';
  // sap: blue dots up the xylem, orange down the phloem
  const ph=((now-t0)/1200)%1;
  for(let i=0;i<8;i++){ const f=(i/8+ph)%1; s+='<circle cx="'+(cx-3)+'" cy="'+(ground-f*330).toFixed(1)+'" r="2.2" fill="#58a6ff"/><circle cx="'+(cx+3)+'" cy="'+(ground-330+f*330).toFixed(1)+'" r="2.2" fill="#ffb02e"/>'; }
  s+='<text x="'+(cx+20)+'" y="'+(ground-150)+'" font-size="11" fill="#9a9a9a">stem: water up, sugar down</text></g>';
  // leaves
  const leaf=(x,y,dir,k)=>'<path d="M'+x+','+y+' Q'+(x+dir*60)+','+(y-70)+' '+(x+dir*130)+','+(y-40)+' Q'+(x+dir*60)+','+(y-10)+' '+x+','+y+' Z" fill="'+(on(k)?'#8cc86a':'#5aa64a')+'" stroke="'+(on(k)?'#e6e6e6':'#2f5a26')+'"/><path d="M'+x+','+y+' Q'+(x+dir*60)+','+(y-38)+' '+(x+dir*125)+','+(y-40)+'" fill="none" stroke="#2f5a26" stroke-width="1.2"/>';
  s+='<g data-part="leaf" style="cursor:pointer">'+leaf(cx-6,ground-120,-1,'leaf')+leaf(cx+6,ground-200,1,'leaf')+leaf(cx-6,ground-260,-1,'leaf');
  s+='<text x="'+(cx-250)+'" y="'+(ground-190)+'" font-size="11" fill="#9a9a9a">leaf: light in, CO\\u2082 in, water out</text></g>';
  // the chloroplast inset, a magnified cell of the leaf
  s+='<g data-part="chloroplast" style="cursor:pointer"><line x1="'+(cx-60)+'" y1="'+(ground-150)+'" x2="'+(cx-150)+'" y2="'+(ground-40)+'" stroke="#3d444d" stroke-dasharray="3 3"/><circle cx="'+(cx-60)+'" cy="'+(ground-150)+'" r="4" fill="none" stroke="#9a9a9a"/>';
  s+='<rect x="'+(cx-250)+'" y="'+(ground-90)+'" width="130" height="90" rx="10" fill="#1b2a1b" stroke="'+(on('chloroplast')?'#e6e6e6':'#3d5a3d')+'"/>';
  for(const [dx,dy] of [[20,20],[55,18],[95,22],[25,52],[62,58],[100,55],[40,75],[80,78]]) s+='<ellipse cx="'+(cx-250+dx)+'" cy="'+(ground-90+dy)+'" rx="11" ry="7" fill="#5aa64a" stroke="#8cc86a"/>';
  s+='<text x="'+(cx-185)+'" y="'+(ground+14)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">one leaf cell, its chloroplasts</text></g>';
  // flower
  const fy=ground-340;
  s+='<g data-part="flower" style="cursor:pointer">';
  for(let i=0;i<6;i++){ const a=i*Math.PI/3; s+='<ellipse cx="'+(cx+Math.cos(a)*28).toFixed(1)+'" cy="'+(fy+Math.sin(a)*28).toFixed(1)+'" rx="22" ry="13" transform="rotate('+(i*60)+' '+(cx+Math.cos(a)*28).toFixed(1)+' '+(fy+Math.sin(a)*28).toFixed(1)+')" fill="'+(on('flower')?'#ffb8d0':'#f28cb0')+'" stroke="'+(on('flower')?'#e6e6e6':'#b0507a')+'"/>'; }
  for(let i=0;i<6;i++){ const a=i*Math.PI/3+0.5; s+='<line x1="'+cx+'" y1="'+fy+'" x2="'+(cx+Math.cos(a)*14).toFixed(1)+'" y2="'+(fy+Math.sin(a)*14).toFixed(1)+'" stroke="#e6d27a" stroke-width="1.5"/><circle cx="'+(cx+Math.cos(a)*15).toFixed(1)+'" cy="'+(fy+Math.sin(a)*15).toFixed(1)+'" r="2.5" fill="#ffb02e"/>'; }
  s+='<circle cx="'+cx+'" cy="'+fy+'" r="6" fill="#b8e070" stroke="#5aa64a"/>';
  s+='<text x="'+(cx+70)+'" y="'+(fy-40)+'" font-size="11" fill="#9a9a9a">flower: petals, stamens, pistil</text></g>';
  // fruit and seed, on a side branch
  s+='<g data-part="fruit" style="cursor:pointer"><path d="M'+(cx+6)+','+(ground-290)+' Q'+(cx+60)+','+(ground-300)+' '+(cx+90)+','+(ground-270)+'" fill="none" stroke="#4a7a3a" stroke-width="3"/>';
  s+='<ellipse cx="'+(cx+96)+'" cy="'+(ground-250)+'" rx="18" ry="22" fill="'+(on('fruit')?'#ff8c6a':'#e05a3a')+'" stroke="'+(on('fruit')?'#e6e6e6':'#8a3a2a')+'"/><ellipse cx="'+(cx+96)+'" cy="'+(ground-246)+'" rx="4" ry="6" fill="#5a2a1a"/>';
  s+='<text x="'+(cx+125)+'" y="'+(ground-250)+'" font-size="11" fill="#9a9a9a">fruit, with the seed inside</text></g>';
  // sun and gas arrows
  s+='<circle cx="120" cy="70" r="26" fill="#ffb02e" opacity="0.9"/>';
  for(const [x2,y2] of [[cx-100,ground-280],[cx-90,ground-160]]) s+='<line x1="140" y1="86" x2="'+x2+'" y2="'+y2+'" stroke="#ffb02e" stroke-dasharray="4 4" opacity="0.7"/>';
  s+='<text x="90" y="118" font-size="11" fill="#9a9a9a">light</text>';
  s+='<text x="'+(cx+150)+'" y="'+(ground-110)+'" font-size="11" fill="#9a9a9a">CO\\u2082 in \\u2192</text><text x="'+(cx+150)+'" y="'+(ground-94)+'" font-size="11" fill="#9a9a9a">\\u2190 O\\u2082 and water vapor out</text>';
  return {svg:s, h:ground+190};
}

/* ---- the light ---- */
const L={x:80,y:60,w:820,h:300,a:380,b:750};
const LX=nm=>L.x+(nm-L.a)/(L.b-L.a)*L.w;
function lightView(){
  let s='';
  for(let nm=L.a; nm<L.b; nm+=2) s+='<rect x="'+LX(nm).toFixed(1)+'" y="'+(L.y+L.h)+'" width="'+((L.w/((L.b-L.a)/2))+0.6).toFixed(2)+'" height="26" fill="'+waveColor(nm+1)+'"/>';
  s+='<rect x="'+L.x+'" y="'+L.y+'" width="'+L.w+'" height="'+L.h+'" fill="none" stroke="#2b2b2b"/>';
  for(const nm of [400,450,500,550,600,650,700,750]) s+='<text x="'+LX(nm).toFixed(1)+'" y="'+(L.y+L.h+42)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+nm+'</text>';
  s+='<text x="'+(L.x+L.w/2)+'" y="'+(L.y+L.h+60)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">wavelength, nm</text>';
  s+='<text transform="translate(16,'+(L.y+L.h/2)+') rotate(-90)" text-anchor="middle" font-size="11" fill="#9a9a9a">absorption, relative</text>';
  // the green window shaded
  s+='<rect x="'+LX(495).toFixed(1)+'" y="'+L.y+'" width="'+(LX(570)-LX(495)).toFixed(1)+'" height="'+L.h+'" fill="#9be564" opacity="0.06"/><text x="'+LX(532).toFixed(1)+'" y="'+(L.y+18)+'" text-anchor="middle" font-size="10.5" fill="#9be564">the green that gets away</text>';
  for(const k of ['a','b']){ let d=''; for(let nm=L.a; nm<=L.b; nm+=1){ const v=absorb(k,nm); d+=(d?'L':'M')+LX(nm).toFixed(1)+','+(L.y+L.h-v*(L.h-30)).toFixed(1); } s+='<path d="'+d+'" fill="none" stroke="'+CHL[k].color+'" stroke-width="2.2"/>';
    const pk=CHL[k].peaks[0]; s+='<text x="'+(LX(pk[0])+(k==='a'?-8:8)).toFixed(1)+'" y="'+(L.y+L.h-pk[2]*(L.h-30)-8).toFixed(1)+'" text-anchor="'+(k==='a'?'end':'start')+'" font-size="11" fill="'+CHL[k].color+'">chlorophyll '+k+'</text>'; }
  const mx=LX(lam);
  s+='<g id="marker" style="cursor:ew-resize"><line x1="'+mx.toFixed(1)+'" y1="'+L.y+'" x2="'+mx.toFixed(1)+'" y2="'+(L.y+L.h+26)+'" stroke="#ffb02e" stroke-width="1.5"/><circle cx="'+mx.toFixed(1)+'" cy="'+(L.y+L.h-absorb('a',lam)*(L.h-30)).toFixed(1)+'" r="5" fill="#ffb02e" stroke="#121212" stroke-width="1.5"/><text x="'+mx.toFixed(1)+'" y="'+(L.y-8)+'" text-anchor="middle" font-size="11.5" font-weight="700" fill="#ffb02e">'+lam+' nm</text></g>';
  // the equation
  const ey=L.y+L.h+100;
  s+='<g data-photo="1" style="cursor:pointer"><rect x="'+L.x+'" y="'+(ey-30)+'" width="'+L.w+'" height="60" rx="8" fill="#161616" stroke="#2b2b2b"/><text x="'+(L.x+L.w/2)+'" y="'+(ey+6)+'" text-anchor="middle" font-size="18" fill="#e6e6e6">'+esc(PHOTO.equation)+'</text>';
  s+='<text x="'+(L.x+L.w/2)+'" y="'+(ey+50)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">'+PHOTO.energy_kj.toLocaleString('en-US')+' kJ a mole of sugar; '+PHOTO.npp_pg+' billion metric tons of carbon a year across the planet</text></g>';
  return {svg:s, h:ey+70};
}

/* ---- the kinds ---- */
function kindsView(){
  const x0=90, x1=900, y0=100, T0=500, T1=0; const TX=ma=>x0+(T0-ma)/(T0-T1)*(x1-x0); let s='';
  s+='<line x1="'+x0+'" y1="'+(y0+300)+'" x2="'+x1+'" y2="'+(y0+300)+'" stroke="#8a94a6"/>';
  for(const ma of [500,400,300,200,100,0]){ const x=TX(ma); s+='<line x1="'+x.toFixed(1)+'" y1="'+(y0+300)+'" x2="'+x.toFixed(1)+'" y2="'+(y0+306)+'" stroke="#8a94a6"/><text x="'+x.toFixed(1)+'" y="'+(y0+322)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+(ma?ma+' million years ago':'today')+'</text>'; }
  const maxSp=Math.max(...KINDS.map(k=>k.sp)); const BH=240;
  const lanes=[];
  KINDS.forEach((k,i)=>{ const x=TX(k.ma), h=Math.max(3,Math.log10(k.sp)/Math.log10(maxSp)*BH), on=hot===k.k;
    s+='<g data-kind="'+k.k+'" style="cursor:pointer"><rect x="'+(x-22).toFixed(1)+'" y="'+(y0+300-h).toFixed(1)+'" width="44" height="'+h.toFixed(1)+'" rx="4" fill="'+['#9be564','#6ee7f2','#58a6ff','#f28cb0'][i]+'" opacity="'+(on?1:0.8)+'"/>';
    const top=Math.min(...KINDS.filter(j=>Math.abs(TX(j.ma)-x)<150).map(j=>y0+300-Math.max(3,Math.log10(j.sp)/Math.log10(maxSp)*BH)));
    let ly=top-22; while(lanes.some(([lx,l])=>Math.abs(lx-x)<150&&Math.abs(l-ly)<30)) ly-=30; lanes.push([x,ly]);
    if(ly<y0+300-h-22) s+='<line x1="'+x.toFixed(1)+'" y1="'+(ly+10)+'" x2="'+x.toFixed(1)+'" y2="'+(y0+300-h-2).toFixed(1)+'" stroke="#3d444d"/>';
    s+='<text x="'+x.toFixed(1)+'" y="'+ly.toFixed(1)+'" text-anchor="middle" font-size="11.5" fill="'+(on?'#e6e6e6':'#9a9a9a')+'">'+esc(k.n)+'</text><text x="'+x.toFixed(1)+'" y="'+(ly+14).toFixed(1)+'" text-anchor="middle" font-size="10.5" fill="#6b7280">'+k.sp.toLocaleString('en-US')+' species</text></g>'; });
  s+='<text x="'+x0+'" y="'+(y0-10)+'" font-size="11" fill="#9a9a9a">each bar stands where its kind first appears in the rocks; its height is the number of species alive now, on a log scale</text>';
  return {svg:s, h:y0+340};
}

/* ---- render and wiring ---- */
function render(now){ const q=view==='parts'?partsView(now||performance.now()):view==='light'?lightView():kindsView(); el.innerHTML='<svg viewBox="0 0 '+W+' '+q.h+'" xmlns="http://www.w3.org/2000/svg" id="psvg"><rect width="'+W+'" height="'+q.h+'" fill="#121212"/>'+q.svg+'</svg>'; document.getElementById('lightCtl').hidden=view!=='light'; document.getElementById('lamOut').textContent=lam+' nm, '+colorName(lam); }
function setView(v){ view=v; hot=null; for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on',b.dataset.v===v); render(); if(v==='parts') showPlant(); else if(v==='light') showLam(lam); else showKinds(); }
document.getElementById('views').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setView(b.dataset.v); });
(function tick(now){ if(view==='parts') render(now); requestAnimationFrame(tick); })(performance.now());
let dragging=false;
const svgPt=e=>{ const svg=document.getElementById('psvg'), b=svg.getBoundingClientRect(); return [(e.clientX-b.left)/b.width*W,(e.clientY-b.top)/b.height*svg.viewBox.baseVal.height]; };
function setLam(nm){ lam=Math.round(Math.max(L.a,Math.min(L.b,nm))); render(); showLam(lam); }
el.addEventListener('pointerdown',e=>{ if(view!=='light') return; const [x,y]=svgPt(e); if(y>=L.y-20&&y<=L.y+L.h+30&&x>=L.x-6&&x<=L.x+L.w+6){ dragging=true; setLam(L.a+(x-L.x)/L.w*(L.b-L.a)); e.preventDefault(); } });
el.addEventListener('pointermove',e=>{ if(!dragging) return; const [x]=svgPt(e); setLam(L.a+(x-L.x)/L.w*(L.b-L.a)); });
window.addEventListener('pointerup',()=>{ dragging=false; });
el.addEventListener('pointerover',e=>{ if(dragging) return; const p=e.target.closest('[data-part]'); if(p){ const k=p.getAttribute('data-part'); if(k===hot) return; hot=k; showPart(k); return; }
  const k=e.target.closest('[data-kind]'); if(k){ const kk=k.getAttribute('data-kind'); if(kk===hot) return; hot=kk; render(); showKind(kk); return; }
  if(e.target.closest('[data-photo]')) showPhoto(); });
el.addEventListener('pointerleave',()=>{ if(view==='parts'&&hot){ hot=null; showPlant(); } if(view==='kinds'&&hot){ hot=null; render(); showKinds(); } });

render(); showPlant();
window.__plants=(q)=>{ const o={view,hot,lam,card:document.getElementById('numTxt').innerText,name:document.getElementById('nameTxt').innerText,parts:document.querySelectorAll('#psvg g[data-part]').length,kinds:document.querySelectorAll('#psvg g[data-kind]').length,
  marker:(()=>{ const c=document.querySelector('#marker line'); return c?+c.getAttribute('x1'):null; })()};
  if(q&&q.nm!=null){ o.abs=[absorb('a',q.nm),absorb('b',q.nm)]; o.col=waveColor(q.nm); } return o; };
</script>
</body>
</html>
"""

html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__PARTS__", _js(parts)).replace("__CHL__", _js(CHLOROPHYLL)).replace("__PHOTO__", _js(PHOTO)).replace("__KINDS__", _js(kinds))
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(PARTS)} parts, {len(KINDS)} kinds")
