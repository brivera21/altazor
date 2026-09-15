#!/usr/bin/env python3
"""Generate plates.html, Plate Tectonics: the plates, their edges, and the
three ways an edge can move.

Two views. The map: the 52 plates of Bird's PB2002 model on an equirectangular
map, land in grey, boundaries coloured by kind, a plate lit under the pointer
with its area, its share of the surface, the lengths of its edges by kind and
its speed against its neighbours; a boundary under the pointer gives the two
plates, the kind and the relative velocity. The edges: three cross-sections
of what happens at a ridge, a trench and a transform.

Data: tools/data/plates.json (geometry, made by make_plates.py) and
tools/plates_data.py (the words).

Usage: python3 build_plates.py
"""

import json
from pathlib import Path

import apa
from plates_data import CLASSES, NOTES, GENERIC, PLACES, REFS

ROOT = Path(__file__).parent.parent
OUT = ROOT / "plates.html"
GEO = json.loads((ROOT / "tools" / "data" / "plates.json").read_text())

NOTE1 = ("The Earth's outer shell is broken into plates that slide over the "
         "soft mantle beneath, a few centimetres a year, about as fast as "
         "fingernails grow. Fifty-two of them in Bird's model, seven of "
         "them holding most of the surface. Every mountain range, trench, "
         "volcano chain and earthquake belt lies along the edges, and the "
         "edges come in three kinds: pulling apart, pushing together, and "
         "sliding past.")

NOTE2 = ("Under the pointer a plate gives its area and its edges by kind; a "
         "boundary gives the two plates and how fast they move against each "
         "other. The second view cuts through the three kinds of edge: a "
         "ridge where mantle rises and freezes into new ocean floor, a "
         "trench where old floor sinks back and the volcanoes stand above "
         "it, and a transform where the plates grind past with nothing "
         "made or lost.")

METHOD = ("The plates and their boundaries are Bird's PB2002 model, a set "
          "of 52 rigid plates whose edges are digitised in 5,824 steps, "
          "each classed as a spreading ridge, continental rift, subduction "
          "zone, oceanic or continental transform, or continental or "
          "oceanic convergence, and each given the relative velocity of the "
          "two plates across it. Areas are measured from the model's "
          "polygons on a sixth-of-a-degree grid weighted by the cosine of "
          "latitude and match Bird's table. A plate's speed against its "
          "neighbours is the mean of its boundary velocities weighted by "
          "length. The map is equirectangular, so the poles are stretched "
          "and Antarctica looks far larger than it is; the areas in the "
          "cards are true. Steps are drawn simplified to a tenth of a degree.")


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


classes = [{"k": k, "n": n, "c": c, "b": b} for k, n, c, b in CLASSES]
places = [{"k": k, "n": n, "lon": lon, "lat": lat, "b": b, "s": s} for k, n, lon, lat, b, s in PLACES]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plate Tectonics &middot; Altazor</title>
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
.presets { display:flex; gap:6px; flex-wrap:wrap; }
.presets button { padding:5px 11px; font-size:12.5px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; position:relative; }
#diagram canvas, #diagram svg { width:100%; height:auto; display:block; user-select:none; }
#map { cursor:crosshair; border-radius:6px; }
.legend { display:flex; gap:14px; flex-wrap:wrap; margin-top:8px; font-size:12px; color:var(--muted); }
.legend span { display:inline-flex; align-items:center; gap:6px; }
.legend i { display:inline-block; width:18px; height:3px; border-radius:2px; }
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
  <nav class="site"><a href="library.html">&larr; Library &middot; Earth</a><a href="earth-interior.html">The Interior</a><a href="earth-history.html">Geological History</a><a href="earth.html">Climate</a></nav>
</header>
<h1>Plate Tectonics</h1>
<div class="bar" id="views"><button data-v="map" class="on">The plates</button><button data-v="edges">The edges</button></div>
<div class="controls" id="mapCtl">
  <label>places</label>
  <span class="presets" id="places"></span>
</div>
<div class="stage">
  <div id="diagram">
    <canvas id="map" width="980" height="490"></canvas>
    <div class="legend" id="legend"></div>
    <div id="edges" hidden></div>
  </div>
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
const G=__GEO__, CLASSES=__CLASSES__, NOTES=__NOTES__, GENERIC=__GENERIC__, PLACES=__PLACES__;
const W=980, H=490, EARTH=510.1e6;
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const cv=document.getElementById('map'), ctx=cv.getContext('2d');
let view='map', ids=null, land=null, hotPlate=0, hotLine=-1, base=null;

/* ---- the plates' numbers ---- */
const code=i=>G.codes[i-1];
const stats={};                                   // per plate: edges by class, mean speed
// a boundary name is 'A-B', or for subduction 'A\\\\B' (A dives under B) and 'A/B' (B dives under A)
const split=pair=>pair.split(/[-\\\\/]/);
const under=pair=>pair.includes('\\\\')?split(pair)[0]:pair.includes('/')?split(pair)[1]:null;
for(const L of G.lines){ const [pair,c,len,v]=L; const u=under(pair); for(const p of split(pair)){ const s=stats[p]||(stats[p]={by:[0,0,0,0,0,0,0],under:0,over:0,L:0,LV:0,fast:null}); s.by[c]+=len; if(c===2){ if(u===p) s.under+=len; else s.over+=len; } s.L+=len; s.LV+=len*v; if(!s.fast||v>s.fast[1]) s.fast=[pair,v,c]; } }
const kindWord=c=>CLASSES[c].n.replace(/^an? /,'');
const grp=c=>c<=1?'pulling apart':c===2?'diving under':c<=4?'sliding past':'colliding';
function showPlate(i){ const k=code(i), [name,area]=G.areas[k], s=stats[k]||{by:[0,0,0,0,0,0,0],L:0,LV:0};
  const kinds=[['pulling apart',s.by[0]+s.by[1]],['diving under a neighbour',s.under||0],['a neighbour diving under it',s.over||0],['sliding past',s.by[3]+s.by[4]],['colliding',s.by[5]+s.by[6]]].filter(x=>x[1]>0).sort((a,b)=>b[1]-a[1]);
  const note=NOTES[k]||GENERIC;
  card('A plate', esc(name), [['area',(area/1e6).toFixed(2)+' million km\\u00b2'],['share of the surface',(area/EARTH*100).toFixed(1)+'%'],['edge',Math.round(s.L).toLocaleString('en-US')+' km'],
    ...kinds.map(([n,l])=>['  '+n, Math.round(l).toLocaleString('en-US')+' km']),
    ['against its neighbours', s.L?(s.LV/s.L/10).toFixed(1)+' cm a year, on average':''],
    ['fastest edge', s.fast?(s.fast[1]/10).toFixed(1)+' cm a year, with '+G.areas[split(s.fast[0]).find(x=>x!==k)][0]:'']], note[0], note[1]); }
function showLine(j){ const [pair,c,len,v,d,e]=G.lines[j]; const [a,b]=split(pair).map(x=>G.areas[x][0]); const u=under(pair);
  const rel=c===2&&u?G.areas[u][0]+' dives under '+G.areas[split(pair).find(x=>x!==u)][0]:Math.abs(d)<2?'sliding past':d>0?'pulling apart':'pushing together';
  card(kindWord(c).replace(/^./,x=>x.toUpperCase()), esc(a)+' and '+esc(b), [['kind',CLASSES[c].n],['relative motion',(v/10).toFixed(1)+' cm a year, '+esc(rel)],['this stretch',Math.round(len).toLocaleString('en-US')+' km'],
    [e<0?'sea floor':'ground', Math.abs(e).toLocaleString('en-US')+' m '+(e<0?'below':'above')+' the sea']], CLASSES[c].b, 'Bird 2003'); }
function showPlace(p){ card('A place', esc(p.n), [['at',Math.abs(p.lat).toFixed(0)+'\\u00b0'+(p.lat<0?'S':'N')+', '+Math.abs(p.lon).toFixed(0)+'\\u00b0'+(p.lon<0?'W':'E')]], p.b, p.s); }
function card(kind,name,rows,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').innerHTML=name;
  document.getElementById('numTxt').innerHTML=rows.filter(r=>r[1]).map(([k,v])=>'<b>'+esc(k)+'</b> '+v).join('<br>');
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').textContent=src;
}

/* ---- the map ---- */
const PAL=['#2a3a4a','#3a2f4a','#2a4438','#4a3a2a','#3f2f2f','#2f3f4f','#3a4430','#44303c'];
const X=lon=>(lon+180)/360*W, Y=lat=>(90-lat)/180*H;
function decode(b64,w,h,cb){ const img=new Image(); img.onload=()=>{ const off=document.createElement('canvas'); off.width=w; off.height=h; const o=off.getContext('2d'); o.drawImage(img,0,0); const d=o.getImageData(0,0,w,h).data; const a=new Uint8Array(w*h); for(let i=0,p=0;i<d.length;i+=4,p++) a[p]=d[i]; cb(a); }; img.src='data:image/png;base64,'+b64; }
function paintBase(){
  const im=ctx.createImageData(W,H), d=im.data;
  for(let y=0;y<H;y++) for(let x=0;x<W;x++){ const gx=Math.floor(x/W*G.W), gy=Math.floor(y/H*G.H), id=ids[gy*G.W+gx];
    const lx=Math.floor(x/W*G.landW), ly=Math.floor(y/H*G.landH), isLand=land[ly*G.landW+lx]>0;
    let col=PAL[id%PAL.length]; let r=parseInt(col.slice(1,3),16), g=parseInt(col.slice(3,5),16), b=parseInt(col.slice(5,7),16);
    if(isLand){ r=Math.round(r*0.55+110*0.45); g=Math.round(g*0.55+110*0.45); b=Math.round(b*0.55+105*0.45); }
    const p=(y*W+x)*4; d[p]=r; d[p+1]=g; d[p+2]=b; d[p+3]=255; }
  base=im;
}
function paint(){
  if(!base) return;
  const im=ctx.createImageData(W,H); im.data.set(base.data);
  if(hotPlate){ const d=im.data; for(let y=0;y<H;y++) for(let x=0;x<W;x++){ const gx=Math.floor(x/W*G.W), gy=Math.floor(y/H*G.H); if(ids[gy*G.W+gx]===hotPlate){ const p=(y*W+x)*4; d[p]=Math.min(255,d[p]+70); d[p+1]=Math.min(255,d[p+1]+60); d[p+2]=Math.min(255,d[p+2]+30); } } }
  ctx.putImageData(im,0,0);
  // graticule
  ctx.strokeStyle='rgba(255,255,255,0.06)'; ctx.lineWidth=1;
  for(let lon=-150;lon<=150;lon+=30){ ctx.beginPath(); ctx.moveTo(X(lon),0); ctx.lineTo(X(lon),H); ctx.stroke(); }
  for(let lat=-60;lat<=60;lat+=30){ ctx.beginPath(); ctx.moveTo(0,Y(lat)); ctx.lineTo(W,Y(lat)); ctx.stroke(); }
  // the boundaries
  G.lines.forEach((L,j)=>{ const [pair,c,len,v,d,e,p]=L; ctx.strokeStyle=CLASSES[c].c; ctx.lineWidth=j===hotLine?4:(c===2?2.2:1.6); ctx.globalAlpha=hotLine>=0&&j!==hotLine?0.45:1;
    ctx.beginPath(); for(let i=0;i<p.length;i+=2){ const x=X(p[i]), y=Y(p[i+1]); if(i===0||Math.abs(p[i]-p[i-2])>180) ctx.moveTo(x,y); else ctx.lineTo(x,y); } ctx.stroke(); });
  ctx.globalAlpha=1;
  // plate names for the large ones
  ctx.font='11px -apple-system,Helvetica,Arial,sans-serif'; ctx.fillStyle='rgba(230,230,230,0.75)'; ctx.textAlign='center';
  for(const [k,lon,lat] of [['PA',-150,10],['NA',-100,45],['SA',-58,-15],['AF',18,8],['EU',80,55],['AU',132,-27],['AN',0,-80],['NZ',-95,-22],['IN',77,20],['AR',47,23],['SO',42,-8],['PS',134,18],['CO',-97,7],['CA',-73,15],['SC',-45,-58],['AM',125,48],['SU',108,3],['OK',150,58],['JF',-129,45]]){ ctx.fillText(G.areas[k][0], X(lon), Y(lat)); }
  ctx.textAlign='start';
}
function plateAt(px,py){ const gx=Math.floor(px/W*G.W), gy=Math.floor(py/H*G.H); return ids?ids[gy*G.W+gx]:0; }
function lineAt(px,py){ let best=-1, bd=6;
  G.lines.forEach((L,j)=>{ const p=L[6]; for(let i=0;i+3<p.length;i+=2){ if(Math.abs(p[i+2]-p[i])>180) continue; const x1=X(p[i]),y1=Y(p[i+1]),x2=X(p[i+2]),y2=Y(p[i+3]); const dx=x2-x1,dy=y2-y1,l2=dx*dx+dy*dy||1; let t=((px-x1)*dx+(py-y1)*dy)/l2; t=Math.max(0,Math.min(1,t)); const d=Math.hypot(px-(x1+t*dx),py-(y1+t*dy)); if(d<bd){ bd=d; best=j; } } });
  return best; }
cv.addEventListener('pointermove',e=>{ const r=cv.getBoundingClientRect(); const px=(e.clientX-r.left)/r.width*W, py=(e.clientY-r.top)/r.height*H;
  const j=lineAt(px,py), i=j>=0?0:plateAt(px,py); if(j!==hotLine||i!==hotPlate){ hotLine=j; hotPlate=i; paint(); if(j>=0) showLine(j); else if(i) showPlate(i); } });
cv.addEventListener('pointerleave',()=>{ hotLine=-1; hotPlate=0; paint(); });
document.getElementById('legend').innerHTML=CLASSES.map(c=>'<span><i style="background:'+c.c+'"></i>'+esc(c.n.replace(/^an? /,''))+'</span>').join('');
document.getElementById('places').innerHTML=PLACES.map(p=>'<button type="button" data-k="'+p.k+'">'+esc(p.n)+'</button>').join('');
document.getElementById('places').addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; const p=PLACES.find(x=>x.k===b.dataset.k); setView('map'); hotLine=lineAt(X(p.lon),Y(p.lat)); if(hotLine<0){ let bd=1e9; G.lines.forEach((L,j)=>{ const q=L[6]; for(let i=0;i<q.length;i+=2){ const d=Math.hypot(X(q[i])-X(p.lon),Y(q[i+1])-Y(p.lat)); if(d<bd){ bd=d; hotLine=j; } } }); } hotPlate=0; paint(); showPlace(p);
  const L=G.lines[hotLine]; const [a,b2]=split(L[0]).map(x=>G.areas[x][0]); document.getElementById('numTxt').innerHTML+='<br><b>the boundary</b> '+esc(a)+' and '+esc(b2)+', '+esc(CLASSES[L[1]].n)+', '+(L[3]/10).toFixed(1)+' cm a year'; });

/* ---- the edges ---- */
function edges(){
  const P=[{k:'ridge',x:20,n:'pulling apart: a spreading ridge'},{k:'trench',x:340,n:'pushing together: a subduction zone'},{k:'transform',x:660,n:'sliding past: a transform fault'}];
  const y0=60, h=260, w=300; let s='';
  const arrow=(x1,y1,x2,y2,c)=>'<line x1="'+x1+'" y1="'+y1+'" x2="'+x2+'" y2="'+y2+'" stroke="'+c+'" stroke-width="2.5"/><polygon points="'+x2+','+y2+' '+(x2-8*Math.sign(x2-x1||1))+','+(y2-5)+' '+(x2-8*Math.sign(x2-x1||1))+','+(y2+5)+'" fill="'+c+'"/>';
  for(const p of P){ const x=p.x;
    s+='<g data-e="'+p.k+'" style="cursor:pointer"><rect x="'+x+'" y="'+y0+'" width="'+w+'" height="'+h+'" fill="#161616" stroke="#2b2b2b" rx="6"/>';
    s+='<text x="'+(x+10)+'" y="'+(y0-12)+'" font-size="12" fill="#e6e6e6">'+esc(p.n)+'</text>';
    if(p.k==='ridge'){
      s+='<rect x="'+x+'" y="'+(y0+150)+'" width="'+w+'" height="'+(h-150)+'" fill="#b55d2a" opacity="0.5" rx="6"/>';                       // asthenosphere
      s+='<path d="M'+(x+110)+','+(y0+150)+' L'+(x+150)+','+(y0+126)+' L'+(x+190)+','+(y0+150)+' Z" fill="#d9822b" opacity="0.7"/>';   // rising mantle
      s+='<path d="M'+(x+150)+','+(y0+150)+' l-10,20 M'+(x+150)+','+(y0+150)+' l10,20 M'+(x+150)+','+(y0+150)+' l0,26" stroke="#f28cb0" stroke-width="1.5" fill="none" opacity="0.7"/>';
      for(let i=0;i<7;i++){ const dx=4+i*21; s+='<rect x="'+(x+150-dx-21)+'" y="'+(y0+104+i*1.5)+'" width="21" height="'+(26-i*1.5)+'" fill="'+(i%2?'#4a6a8a':'#3a5a7a')+'"/><rect x="'+(x+150+dx)+'" y="'+(y0+104+i*1.5)+'" width="21" height="'+(26-i*1.5)+'" fill="'+(i%2?'#4a6a8a':'#3a5a7a')+'"/>'; }
      s+='<rect x="'+x+'" y="'+(y0+20)+'" width="'+w+'" height="84" fill="#1c2c44" opacity="0.7"/>';                                             // sea
      s+='<path d="M'+(x+146)+','+(y0+130)+' L'+(x+154)+','+(y0+130)+' L'+(x+152)+','+(y0+100)+' L'+(x+148)+','+(y0+100)+' Z" fill="#f28cb0"/>';   // magma
      s+=arrow(x+120,y0+60,x+60,y0+60,'#f28cb0')+arrow(x+180,y0+60,x+240,y0+60,'#f28cb0');
      s+='<text x="'+(x+150)+'" y="'+(y0+240)+'" text-anchor="middle" font-size="10.5" fill="#e6e6e6">mantle rises, melts, and the new floor is youngest at the ridge</text>';
      s+='<text x="'+(x+10)+'" y="'+(y0+100)+'" font-size="9.5" fill="#9a9a9a">old floor</text><text x="'+(x+150)+'" y="'+(y0+92)+'" text-anchor="middle" font-size="9.5" fill="#f28cb0">new</text><text x="'+(x+w-10)+'" y="'+(y0+100)+'" text-anchor="end" font-size="9.5" fill="#9a9a9a">old floor</text>';
    } else if(p.k==='trench'){
      s+='<rect x="'+x+'" y="'+(y0+150)+'" width="'+w+'" height="'+(h-150)+'" fill="#b55d2a" opacity="0.5" rx="6"/>';
      s+='<rect x="'+x+'" y="'+(y0+20)+'" width="150" height="90" fill="#1c2c44" opacity="0.7"/>';                                              // sea
      s+='<path d="M'+x+','+(y0+110)+' L'+(x+150)+','+(y0+118)+' Q'+(x+200)+','+(y0+140)+' '+(x+230)+','+(y0+250)+' L'+(x+205)+','+(y0+255)+' Q'+(x+180)+','+(y0+160)+' '+(x+140)+','+(y0+140)+' L'+x+','+(y0+132)+' Z" fill="#3a5a7a"/>';   // the slab
      s+='<path d="M'+(x+150)+','+(y0+118)+' L'+(x+w)+','+(y0+60)+' L'+(x+w)+','+(y0+150)+' L'+(x+190)+','+(y0+150)+' Z" fill="#6b6b5a"/>';        // continent
      s+='<path d="M'+(x+215)+','+(y0+92)+' l14,-40 l14,40 Z" fill="#8a7a6a"/><path d="M'+(x+229)+','+(y0+52)+' q-4,-16 -8,-30 M'+(x+229)+','+(y0+52)+' q4,-16 10,-28" stroke="#f28cb0" stroke-width="2" fill="none"/>';   // volcano
      s+='<path d="M'+(x+229)+','+(y0+130)+' q0,-40 0,-80" stroke="#f28cb0" stroke-width="2" stroke-dasharray="3 3" fill="none"/>';
      for(const [dx,dy] of [[165,135],[180,150],[192,170],[203,195],[212,220],[172,128],[186,160]]) s+='<circle cx="'+(x+dx)+'" cy="'+(y0+dy)+'" r="2.2" fill="#ffb02e"/>';
      s+=arrow(x+40,y0+90,x+100,y0+90,'#58a6ff')+arrow(x+270,y0+40,x+225,y0+40,'#58a6ff');
      s+='<text x="'+(x+150)+'" y="'+(y0+240)+'" text-anchor="middle" font-size="10.5" fill="#e6e6e6">old floor sinks; water it carries melts the rock above it</text>';
      s+='<text x="'+(x+150)+'" y="'+(y0+108)+'" text-anchor="end" font-size="9.5" fill="#9a9a9a">trench </text><text x="'+(x+240)+'" y="'+(y0+200)+'" font-size="9.5" fill="#ffb02e">earthquakes</text><text x="'+(x+240)+'" y="'+(y0+212)+'" font-size="9.5" fill="#ffb02e">down the slab</text>';
    } else {
      s+='<rect x="'+x+'" y="'+(y0+20)+'" width="'+w+'" height="'+(h-40)+'" fill="#1c2c44" opacity="0.7"/>';                                    // map view of the sea
      s+='<rect x="'+(x+40)+'" y="'+(y0+40)+'" width="14" height="90" fill="#f28cb0" opacity="0.8"/><rect x="'+(x+246)+'" y="'+(y0+110)+'" width="14" height="70" fill="#f28cb0" opacity="0.8"/>';   // two ridge segments
      s+='<line x1="'+(x+47)+'" y1="'+(y0+130)+'" x2="'+(x+253)+'" y2="'+(y0+110)+'" stroke="#ffb02e" stroke-width="3"/>';                      // the transform between them
      s+='<line x1="'+x+'" y1="'+(y0+134)+'" x2="'+(x+47)+'" y2="'+(y0+130)+'" stroke="#ffb02e" stroke-width="1.5" stroke-dasharray="4 4"/><line x1="'+(x+253)+'" y1="'+(y0+110)+'" x2="'+(x+w)+'" y2="'+(y0+106)+'" stroke="#ffb02e" stroke-width="1.5" stroke-dasharray="4 4"/>';
      s+=arrow(x+100,y0+100,x+160,y0+95,'#e6e6e6')+arrow(x+200,y0+145,x+140,y0+150,'#e6e6e6');
      s+='<text x="'+(x+150)+'" y="'+(y0+60)+'" text-anchor="middle" font-size="10" fill="#9a9a9a">seen from above</text>';
      s+='<text x="'+(x+150)+'" y="'+(y0+240)+'" text-anchor="middle" font-size="10.5" fill="#e6e6e6">the plates grind past; nothing is made or lost</text>';
      s+='<text x="'+(x+150)+'" y="'+(y0+196)+'" text-anchor="middle" font-size="9.5" fill="#9a9a9a">between the ridge segments the sides move opposite ways;</text><text x="'+(x+150)+'" y="'+(y0+208)+'" text-anchor="middle" font-size="9.5" fill="#9a9a9a">beyond them, the same way</text>';
    }
    s+='</g>'; }
  return '<svg viewBox="0 0 980 360" xmlns="http://www.w3.org/2000/svg" id="psvg"><rect width="980" height="360" fill="#121212"/>'+s+'</svg>';
}
const EDGE={ridge:['A spreading ridge','The plates part, the pressure on the mantle beneath drops, and it melts. The melt freezes into new crust at the crack, so the sea floor is youngest at the ridge and gets older, colder and deeper away from it: the Atlantic is two and a half centimetres wider every year, and none of its floor is older than 180 million years.', 'Wikipedia, Mid-ocean ridge'],
  trench:['A subduction zone','Old ocean floor is dense enough to sink. It bends down at a trench, the deepest places on the planet, and slides into the mantle at a few centimetres a year, shaking as it goes: the earthquakes trace the slab down to 700 km. Water carried down with it lowers the melting point of the rock above, and a line of volcanoes stands a hundred kilometres or so behind the trench.', 'Wikipedia, Subduction'],
  transform:['A transform fault','Spreading ridges are broken into segments, and between the segments the plates slide past each other along a fault. Nothing is made or destroyed. On land the same motion is the San Andreas, where the two sides jerk past each other in earthquakes every century or so.', 'Wikipedia, Transform fault']};
document.getElementById('edges').innerHTML=edges();
document.getElementById('edges').addEventListener('pointerover',e=>{ const g=e.target.closest('[data-e]'); if(g){ const k=g.getAttribute('data-e'); card('The edges',EDGE[k][0],[],EDGE[k][1],EDGE[k][2]); } });

/* ---- wiring ---- */
function setView(v){ view=v; for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on',b.dataset.v===v);
  document.getElementById('map').hidden=v!=='map'; document.getElementById('legend').hidden=v!=='map'; document.getElementById('mapCtl').hidden=v!=='map'; document.getElementById('edges').hidden=v!=='edges';
  if(v==='edges') card('The edges','Three kinds of boundary',[],'A ridge, a trench and a transform, in section. Each one under the pointer says what happens there.',''); }
document.getElementById('views').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setView(b.dataset.v); });
card('The plates','52 plates, seven of them most of the surface',[['plates',G.codes.length],['boundary steps','5,824'],['spreading ridge',Math.round(G.lines.filter(l=>l[1]===0).reduce((a,l)=>a+l[2],0)).toLocaleString('en-US')+' km'],['subduction',Math.round(G.lines.filter(l=>l[1]===2).reduce((a,l)=>a+l[2],0)).toLocaleString('en-US')+' km']],'A plate or a boundary under the pointer lands here.','Bird 2003');
decode(G.ids,G.W,G.H,a=>{ ids=a; decode(G.land,G.landW,G.landH,b=>{ land=b; paintBase(); paint(); }); });
window.__plates=(q)=>{ const o={view,hotPlate,hotLine,ready:!!base,n:G.codes.length,lines:G.lines.length,card:document.getElementById('numTxt').innerText,name:document.getElementById('nameTxt').innerText,stats};
  if(q&&q.at){ o.plate=code(plateAt(X(q.at[0]),Y(q.at[1]))); o.line=lineAt(X(q.at[0]),Y(q.at[1])); }
  if(q&&q.pixel){ const d=ctx.getImageData(q.pixel[0],q.pixel[1],1,1).data; o.rgb=[d[0],d[1],d[2]]; }
  return o; };
</script>
</body>
</html>
"""

geo = {k: GEO[k] for k in ("W", "H", "landW", "landH", "codes", "areas", "lines", "ids", "land")}
html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__GEO__", _js(geo)).replace("__CLASSES__", _js(classes)).replace("__NOTES__", _js(NOTES)).replace("__GENERIC__", _js(GENERIC)).replace("__PLACES__", _js(places))
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(GEO['codes'])} plates, {len(GEO['lines'])} boundary lines, {len(PLACES)} places")
