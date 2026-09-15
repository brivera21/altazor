#!/usr/bin/env python3
"""Generate earth-interior.html, Earth's Interior: a cut through the planet,
and the profiles beneath it.

Two views. A cut: a half-section to scale, seven layers from crust to inner
core, a depth line down to the center with a marker that drags, and a card
that reads density, wave speeds, gravity, pressure and temperature at that
depth, all from PREM. Profiles: the same five quantities against depth, side
by side, with the layer boundaries drawn across them and the marker shared.

Data: tools/earth_interior_data.py.

Usage: python3 build_earth_interior.py
"""

import json
from pathlib import Path

import apa
from earth_interior_data import PREM_RHO, PREM_VP, PREM_VS, GEOTHERM, LAYERS, PLACES, REFS, R_EARTH

OUT = Path(__file__).parent.parent / "earth-interior.html"

NOTE1 = ("The Earth in section, to scale: a crust thinner than a line, a "
         "mantle of slowly flowing rock that is most of the planet, a "
         "liquid iron core and, inside that, a solid one the size of the "
         "Moon. The marker drags down the depth line, and the card reads "
         "off what the rock is doing there: how dense, how hot, how hard "
         "it is being squeezed, and how fast an earthquake's waves would "
         "cross it.")

NOTE2 = ("The profiles put the same five quantities side by side against "
         "depth. Density jumps at the transition zone and nearly doubles "
         "at the core; the shear wave vanishes in the liquid outer core, "
         "which is how the core was known to be liquid before anything "
         "else about it; gravity stays near 10 all the way to the core and "
         "then falls to nothing at the center; pressure climbs to 3.6 "
         "million atmospheres.")

METHOD = ("Density and the two wave speeds are the Preliminary Reference "
          "Earth Model of Dziewonski and Anderson, PREM, evaluated from its "
          "polynomials; mass, gravity and pressure are integrated from the "
          "density on a half-kilometer grid, and the total mass comes out "
          "at 5.973 times 10 to the 24 kg, the center at 364 GPa, as in "
          "PREM. PREM is an average Earth with a 3 km ocean and a 24 km "
          "crust; it puts the transition zone's boundaries at 400 and 670 "
          "km where later work has 410 and 660. Temperature is not in "
          "PREM: the mantle follows Katsura's adiabat, the core-mantle "
          "boundary is set at 4,000 K and the inner core boundary at "
          "Anzellini's 6,230 K, joined by straight lines, and the "
          "uncertainties there are several hundred kelvin. The section is "
          "drawn to scale, so the crust is one pixel.")


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


layers = [{"k": k, "n": n, "top": t, "bot": b, "c": c, "state": st, "what": w, "b": line, "s": s}
          for k, n, t, b, c, st, w, line, s in LAYERS]
places = [{"k": k, "n": n, "d": d, "b": b, "s": s} for k, n, d, b, s in PLACES]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Earth&rsquo;s Interior &middot; Altazor</title>
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
  <nav class="site"><a href="library.html">&larr; Library &middot; Earth</a><a href="earth-history.html">Geological History</a><a href="earth.html">Climate</a><a href="day-night.html">Light Cycle</a></nav>
</header>
<h1>Earth&rsquo;s Interior</h1>
<div class="bar" id="views"><button data-v="cut" class="on">A cut</button><button data-v="profiles">Profiles</button></div>
<div class="controls">
  <label for="depth">depth</label>
  <input type="range" id="depth" min="0" max="6371" step="1" value="1000">
  <output id="depthOut">1,000 km</output>
  <span class="presets" id="places"></span>
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
const RHO=__RHO__, VP=__VP__, VS=__VS__, GEO=__GEO__, LAYERS=__LAYERS__, PLACES=__PLACES__;
const RE=__RE__, G=6.67430e-11, W=980;
const el=document.getElementById('diagram');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
let view='cut', depth=1000, hot=null;

/* ---- PREM ---- */
function prem(T,r){ const x=r/RE; for(const [a,b,c] of T){ if(r>=a&&r<=b) return c[0]+c[1]*x+c[2]*x*x+c[3]*x*x*x; } return 0; }
const rho=r=>prem(RHO,r), vp=r=>prem(VP,r), vs=r=>prem(VS,r);
// mass from the center, then gravity, then pressure from the surface, on a half-kilometer grid
const DR=0.5, N=Math.round(RE/DR), M=new Float64Array(N+1), GR=new Float64Array(N+1), PR=new Float64Array(N+1);
for(let i=0;i<N;i++){ const rm=(i+0.5)*DR; M[i+1]=M[i]+4*Math.PI*Math.pow(rm*1e3,2)*rho(rm)*1e3*DR*1e3; }
for(let i=1;i<=N;i++) GR[i]=G*M[i]/Math.pow(i*DR*1e3,2);
for(let i=N;i>0;i--){ const rm=(i-0.5)*DR; PR[i-1]=PR[i]+rho(rm)*1e3*0.5*(GR[i]+GR[i-1])*DR*1e3; }
const massBelow=r=>M[Math.round(r/DR)], gAt=r=>GR[Math.round(r/DR)], pAt=r=>PR[Math.round(r/DR)];
const MASS=M[N];
function temp(d){ for(let i=1;i<GEO.length;i++){ if(d<=GEO[i][0]){ const [d0,t0]=GEO[i-1],[d1,t1]=GEO[i]; return t0+(t1-t0)*(d-d0)/(d1-d0); } } return GEO[GEO.length-1][1]; }
const layerOf=d=>LAYERS.find(l=>d>=l.top&&d<l.bot)||LAYERS[LAYERS.length-1];
const shellMass=(top,bot)=>massBelow(RE-top)-massBelow(RE-bot);
const shellVol=(top,bot)=>Math.pow(RE-top,3)-Math.pow(RE-bot,3);

/* ---- numbers ---- */
const km=d=>Math.round(d).toLocaleString('en-US')+' km';
const f1=x=>x.toLocaleString('en-US',{minimumFractionDigits:1,maximumFractionDigits:1});
const f2=x=>x.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
function pressure(P){ return P<1e9?f1(P/1e6)+' MPa, '+Math.round(P/101325).toLocaleString('en-US')+' atmospheres':f1(P/1e9)+' GPa, '+(P/101325/1e6).toFixed(2)+' million atmospheres'; }

/* ---- the card ---- */
function card(kind,name,rows,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').innerHTML=name;
  document.getElementById('numTxt').innerHTML=rows.filter(r=>r[1]).map(([k,v])=>'<b>'+esc(k)+'</b> '+v).join('<br>');
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').textContent=src;
}
function showDepth(d){ const r=RE-d, L=layerOf(d), s=vs(r);
  const pl=PLACES.find(p=>Math.abs(p.d-d)<=Math.max(1,d*0.002));
  card('At a depth of', km(d)+(pl?', '+esc(pl.n):''),
    [['layer',L.n],['radius from the center',km(r)],['density',f2(rho(r))+' g/cm\\u00b3'],['P wave',f2(vp(r))+' km/s'],['S wave',s>0?f2(s)+' km/s':'none: it is liquid'],
     ['gravity',f2(gAt(r))+' m/s\\u00b2'],['pressure',pressure(pAt(r))],['temperature','about '+Math.round(temp(d)).toLocaleString('en-US')+' K'],
     ['mass beneath',(massBelow(r)/MASS*100).toFixed(1)+'% of the Earth']],
    pl?pl.b:L.b, pl?pl.s:L.s); }
function showLayer(k){ const L=LAYERS.find(x=>x.k===k); if(!L) return; const r0=RE-L.top, r1=RE-L.bot;
  card('A layer', L.n, [['depth',km(L.top)+' to '+km(L.bot)],['thickness',km(L.bot-L.top)],['state',L.state],['made of',esc(L.what)],
    ['density',f2(rho(r0-0.01))+' to '+f2(rho(r1+0.01))+' g/cm\\u00b3'],['share of the volume',(shellVol(L.top,L.bot)/Math.pow(RE,3)*100).toFixed(1)+'%'],['share of the mass',(shellMass(L.top,L.bot)/MASS*100).toFixed(1)+'%'],
    ['temperature','about '+Math.round(temp(L.top+0.01)).toLocaleString('en-US')+' to '+Math.round(temp(L.bot-0.01)).toLocaleString('en-US')+' K']], L.b, L.s); }

/* ---- the cut ---- */
const C={cx:520,cy:370,R:330};
function cut(){
  let s='';
  const half=(r)=>'M'+C.cx+','+(C.cy-r)+' A'+r+','+r+' 0 0 0 '+C.cx+','+(C.cy+r)+' Z';
  for(const L of LAYERS){ const r=C.R*(RE-L.top)/RE; s+='<path data-l="'+L.k+'" d="'+half(r)+'" fill="'+L.c+'" opacity="'+(hot&&hot!==L.k?0.55:0.9)+'" style="cursor:pointer"/>'; }
  // the crust as a stroke so it can be seen at all
  s+='<path d="M'+C.cx+','+(C.cy-C.R)+' A'+C.R+','+C.R+' 0 0 0 '+C.cx+','+(C.cy+C.R)+'" fill="none" stroke="'+LAYERS[0].c+'" stroke-width="2"/>';
  s+='<line x1="'+C.cx+'" y1="'+(C.cy-C.R)+'" x2="'+C.cx+'" y2="'+(C.cy+C.R)+'" stroke="#121212" stroke-width="2"/>';
  // the depth line: from the surface at the top down to the center
  s+='<line x1="'+C.cx+'" y1="'+(C.cy-C.R)+'" x2="'+C.cx+'" y2="'+C.cy+'" stroke="#e6e6e6" stroke-width="1" opacity="0.5"/>';
  for(const d of [0,1000,2000,3000,4000,5000,6000]){ const y=C.cy-C.R+C.R*d/RE; s+='<line x1="'+(C.cx-4)+'" y1="'+y.toFixed(1)+'" x2="'+(C.cx+4)+'" y2="'+y.toFixed(1)+'" stroke="#e6e6e6" opacity="0.6"/>'; }
  s+='<text x="'+(C.cx-10)+'" y="'+(C.cy+4)+'" text-anchor="end" font-size="10.5" fill="#4a4540">the center, 6,371 km</text>';
  // layer labels down the right, spaced apart
  let lastY=-1e9;
  for(const L of LAYERS){ const mid=(L.top+L.bot)/2, y0=C.cy-C.R+C.R*mid/RE; let y=Math.max(y0,lastY+17); lastY=y;
    s+='<g data-l="'+L.k+'" style="cursor:pointer"><line x1="'+(C.cx+6)+'" y1="'+y0.toFixed(1)+'" x2="'+(C.cx+40)+'" y2="'+y.toFixed(1)+'" stroke="#3d444d"/><circle cx="'+(C.cx+6)+'" cy="'+y0.toFixed(1)+'" r="2" fill="'+L.c+'"/>';
    s+='<text x="'+(C.cx+46)+'" y="'+(y+4).toFixed(1)+'" font-size="12" fill="'+(hot===L.k?'#e6e6e6':L.c)+'">'+L.n+'</text>';
    s+='<text x="'+(C.cx+46)+'" y="'+(y+16).toFixed(1)+'" font-size="10" fill="#6b7280">'+km(L.top)+' to '+km(L.bot)+', '+L.state+'</text></g>'; lastY=y+14; }
  // the marker
  const y=C.cy-C.R+C.R*depth/RE;
  s+='<g id="marker"><circle cx="'+C.cx+'" cy="'+y.toFixed(1)+'" r="6" fill="#ffb02e" stroke="#121212" stroke-width="1.5"/>';
  s+='<text x="'+(C.cx-12)+'" y="'+(y+4).toFixed(1)+'" text-anchor="end" font-size="11.5" font-weight="700" fill="#ffb02e">'+km(depth)+'</text></g>';
  s+='<text x="'+(C.cx-C.R)+'" y="'+(C.cy+C.R+26)+'" font-size="11" fill="#9a9a9a">to scale: 330 pixels to 6,371 km</text>';
  return {svg:s, h:C.cy+C.R+40};
}

/* ---- the profiles ---- */
const PAN=[{k:'rho',n:'density, g/cm\\u00b3',max:14,f:r=>rho(r),c:'#e0a458'},{k:'v',n:'wave speed, km/s',max:14,f:r=>vp(r),f2:r=>vs(r),c:'#58a6ff',c2:'#9be564'},
           {k:'g',n:'gravity, m/s\\u00b2',max:11,f:r=>gAt(r),c:'#f4efe2'},{k:'P',n:'pressure, GPa',max:380,f:r=>pAt(r)/1e9,c:'#f28cb0'},{k:'T',n:'temperature, K',max:7000,f:r=>temp(RE-r),c:'#ffb02e'}];
const PR0={x:90,y:40,w:144,gap:12,h:560};
const DY=d=>PR0.y+d/RE*PR0.h;
function profiles(){
  let s='';
  PAN.forEach((p,i)=>{ const x0=PR0.x+i*(PR0.w+PR0.gap); const X=v=>x0+v/p.max*PR0.w;
    s+='<rect x="'+x0+'" y="'+PR0.y+'" width="'+PR0.w+'" height="'+PR0.h+'" fill="none" stroke="#2b2b2b"/>';
    s+='<text x="'+x0+'" y="'+(PR0.y-10)+'" font-size="11" fill="#9a9a9a">'+p.n+'</text>';
    for(const v of [0,p.max/2,p.max]) s+='<text x="'+X(v).toFixed(1)+'" y="'+(PR0.y+PR0.h+16)+'" text-anchor="middle" font-size="10" fill="#6b7280">'+v+'</text>';
    for(const L of LAYERS){ if(L.top===0) continue; const y=DY(L.top); s+='<line x1="'+x0+'" y1="'+y.toFixed(1)+'" x2="'+(x0+PR0.w)+'" y2="'+y.toFixed(1)+'" stroke="#2b2b2b" stroke-dasharray="3 4"/>'; }
    const draw=(f,c)=>{ let d=''; for(let dd=0; dd<=RE; dd+=2){ const r=RE-dd, v=f(r); d+=(d?'L':'M')+X(v).toFixed(1)+','+DY(dd).toFixed(1); } return '<path d="'+d+'" fill="none" stroke="'+c+'" stroke-width="2"/>'; };
    if(p.f2) s+=draw(p.f2,p.c2); s+=draw(p.f,p.c);
    if(p.f2){ s+='<text x="'+(x0+PR0.w-4)+'" y="'+(PR0.y+PR0.h-30)+'" text-anchor="end" font-size="10.5" fill="'+p.c+'">P</text><text x="'+(x0+PR0.w-4)+'" y="'+(PR0.y+PR0.h-16)+'" text-anchor="end" font-size="10.5" fill="'+p.c2+'">S</text>'; }
    const r=RE-depth, v=p.f(r);
    s+='<circle cx="'+X(v).toFixed(1)+'" cy="'+DY(depth).toFixed(1)+'" r="4.5" fill="#ffb02e" stroke="#121212" stroke-width="1.2"/>';
    if(p.f2&&p.f2(r)>0) s+='<circle cx="'+X(p.f2(r)).toFixed(1)+'" cy="'+DY(depth).toFixed(1)+'" r="4.5" fill="#ffb02e" stroke="#121212" stroke-width="1.2"/>';
  });
  // depth axis and layer names down the left
  for(const d of [0,1000,2000,3000,4000,5000,6000]){ const y=DY(d); s+='<line x1="'+(PR0.x-6)+'" y1="'+y.toFixed(1)+'" x2="'+PR0.x+'" y2="'+y.toFixed(1)+'" stroke="#8a94a6"/><text x="'+(PR0.x-9)+'" y="'+(y+4).toFixed(1)+'" text-anchor="end" font-size="10.5" fill="#9a9a9a">'+d.toLocaleString('en-US')+'</text>'; }
  s+='<text transform="translate(14,'+(PR0.y+PR0.h/2)+') rotate(-90)" text-anchor="middle" font-size="11.5" fill="#9a9a9a">depth, km</text>';
  const xr=PR0.x+PAN.length*(PR0.w+PR0.gap)-PR0.gap;
  for(const L of LAYERS){ if(L.bot-L.top<150) continue; const y=DY((L.top+L.bot)/2); s+='<text x="'+(xr+8)+'" y="'+(y+4).toFixed(1)+'" font-size="10.5" fill="'+L.c+'">'+L.n+'</text>'; }
  const y=DY(depth);
  s+='<g id="marker"><line x1="'+PR0.x+'" y1="'+y.toFixed(1)+'" x2="'+xr+'" y2="'+y.toFixed(1)+'" stroke="#ffb02e" stroke-width="1" opacity="0.7"/><text x="'+(xr+8)+'" y="'+(y-6).toFixed(1)+'" font-size="11" font-weight="700" fill="#ffb02e">'+km(depth)+'</text></g>';
  return {svg:s, h:PR0.y+PR0.h+40};
}

/* ---- render and wiring ---- */
function render(){
  const q=view==='cut'?cut():profiles();
  el.innerHTML='<svg viewBox="0 0 '+W+' '+q.h+'" xmlns="http://www.w3.org/2000/svg" id="esvg"><rect width="'+W+'" height="'+q.h+'" fill="#121212"/>'+q.svg+'</svg>';
  document.getElementById('depthOut').textContent=km(depth);
}
function setView(v){ view=v; hot=null; for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on',b.dataset.v===v); render(); showDepth(depth); }
function setDepth(d){ depth=Math.max(0,Math.min(RE,Math.round(d*10)/10)); document.getElementById('depth').value=Math.round(depth); render(); showDepth(depth); }
document.getElementById('views').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setView(b.dataset.v); });
document.getElementById('depth').addEventListener('input',e=>{ depth=+e.target.value; render(); showDepth(depth); });
document.getElementById('places').innerHTML=PLACES.map(p=>'<button type="button" data-d="'+p.d+'">'+esc(p.n)+'</button>').join('');
document.getElementById('places').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setDepth(+b.dataset.d); });
let dragging=false;
const svgPt=e=>{ const svg=document.getElementById('esvg'), b=svg.getBoundingClientRect(); return [(e.clientX-b.left)/b.width*W,(e.clientY-b.top)/b.height*svg.viewBox.baseVal.height]; };
function depthAt(x,y){ if(view==='cut'){ const dx=x-C.cx, dy=y-C.cy, rr=Math.sqrt(dx*dx+dy*dy); return rr<=C.R+8?RE*(1-Math.min(1,rr/C.R)):null; }
  return (y>=PR0.y-8&&y<=PR0.y+PR0.h+8)?RE*Math.max(0,Math.min(1,(y-PR0.y)/PR0.h)):null; }
el.addEventListener('pointerdown',e=>{ const [x,y]=svgPt(e); const d=depthAt(x,y); if(d!=null){ dragging=true; hot=null; setDepth(d); e.preventDefault(); } });
el.addEventListener('pointermove',e=>{ if(!dragging) return; const [x,y]=svgPt(e); const d=depthAt(x,y); if(d!=null) setDepth(d); });
window.addEventListener('pointerup',()=>{ dragging=false; });
el.addEventListener('pointerover',e=>{ if(dragging) return; const g=e.target.closest('[data-l]'); if(g){ const k=g.getAttribute('data-l'); if(k===hot) return; hot=k; render(); showLayer(hot); } });
el.addEventListener('pointerleave',()=>{ if(hot){ hot=null; render(); showDepth(depth); } });

render(); showDepth(depth);
window.__earth=(q)=>{ const o={view,depth,hot,mass:MASS,layers:document.querySelectorAll('#esvg path[data-l]').length,
  card:document.getElementById('numTxt').innerText, name:document.getElementById('nameTxt').innerText,
  marker:(()=>{ const c=document.querySelector('#marker circle, #marker line'); return c?[+(c.getAttribute('cx')||c.getAttribute('x1')),+(c.getAttribute('cy')||c.getAttribute('y1'))]:null; })()};
  if(q&&q.r!=null){ const r=q.r; o.at={rho:rho(r),vp:vp(r),vs:vs(r),g:gAt(r),P:pAt(r),m:massBelow(r),T:temp(RE-r)}; }
  if(q&&q.shell){ o.shell={m:shellMass(q.shell[0],q.shell[1])/MASS, v:shellVol(q.shell[0],q.shell[1])/Math.pow(RE,3)}; }
  return o; };
</script>
</body>
</html>
"""

html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__RHO__", _js(PREM_RHO)).replace("__VP__", _js(PREM_VP)).replace("__VS__", _js(PREM_VS))
        .replace("__GEO__", _js(GEOTHERM)).replace("__LAYERS__", _js(layers)).replace("__PLACES__", _js(places)).replace("__RE__", str(R_EARTH))
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(LAYERS)} layers, {len(PLACES)} places")
