#!/usr/bin/env python3
"""Generate atmosphere.html, The Atmosphere: the column of air, and what it
is made of.

Two views. Up: the air from the ground to 600 km, the four layers, the
temperature, pressure and density profiles of the 1976 Standard Atmosphere,
the marks up the column from the tallest building to the Hubble telescope,
and a marker that drags to any altitude while the card reads temperature,
pressure, density, the air above and below, the speed of sound and the
boiling point of water there. Made of: dry air by volume as a bar, the
trace gases opened out on a log scale, and the water vapor beside them.

Data: tools/atmosphere_data.py.

Usage: python3 build_atmosphere.py
"""

import json
import math
from pathlib import Path

import apa
from atmosphere_data import LAYERS_76, UPPER, LAYERS, MARKS, OBJECTS, GASES, WATER, COLUMN, REFS, P0, G0, R_AIR, M_AIR, R_GAS

OUT = Path(__file__).parent.parent / "atmosphere.html"

NOTE1 = ("The air is a thin skin: half of it lies below the height of a "
         "mountain, ninety-nine percent below 30 km, and the whole column "
         "weighs ten metric tons on every square meter. Four layers by "
         "temperature: cooling with height, warming where ozone catches the "
         "ultraviolet, cooling again, then heating to a thousand kelvin in "
         "gas too thin to feel.")

NOTE2 = ("The second view is what the air is made of. Two gases are "
         "nearly all of it, one noble gas is most of the rest, and the "
         "carbon dioxide that sets the planet's temperature is four "
         "hundredths of a percent, so the trace gases get their own line "
         "with a log scale. Water vapor is left out of dry air because it "
         "varies a hundredfold from place to place; on average it is a "
         "quarter of a percent.")

METHOD = ("Temperature to 86 km is the US Standard Atmosphere of 1976: "
          "seven layers, each with a constant lapse rate, from 288.15 K at "
          "sea level. Pressure follows from hydrostatic balance, the "
          "exponential form where the lapse is zero and the power law "
          "elsewhere, with geopotential height converted to geometric; "
          "density is pressure over R T. Above 86 km the model's tables are "
          "interpolated in the log between nine anchors, and the real "
          "thermosphere swings by a factor of ten with the Sun's activity. "
          "The share of the air above a height is its pressure over the "
          "sea-level pressure. The speed of sound is the square root of "
          "gamma R T; the boiling point is the temperature at which the "
          "vapor pressure of water, from the Antoine equation, equals the "
          "air pressure. The column is drawn linear to 120 km and "
          "compressed fivefold above; True scale removes the compression, "
          "one pixel to the kilometer. The balloon rises at 5 meters per "
          "second, the usual rate for a radiosonde, and swells as the "
          "product of the temperature and the inverse pressure, the ideal "
          "gas at the pressure outside, until it bursts at the 35 km of the "
          "mark on the column.")


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


layers = [{"k": k, "n": n, "a": a, "b": b, "c": c, "t": t} for k, n, a, b, c, t in LAYERS]
marks = [{"k": k, "n": n, "z": z, "b": b, "s": s} for k, n, z, b, s in MARKS]
objects = [{"k": k, "n": n, "z": z, "f": f, "kind": kind, "b": b, "s": s} for k, n, z, f, kind, b, s in OBJECTS]
gases = [{"n": n, "f": f, "x": x, "b": b} for n, f, x, b in GASES]
water = {"n": WATER[0], "f": WATER[1], "x": WATER[2], "b": WATER[3]}

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Atmosphere &middot; Altazor</title>
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
#scaleBtn, #balloonBtn { color:var(--text); border-color:#3d444d; }
#scaleBtn.on { background:#1b2a3d; color:var(--accent); border-color:var(--accent); }
#balloonBtn.run { background:#2a2214; color:#ffb02e; border-color:#ffb02e; }
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
details.sources { margin-top:14px; max-width:760px; color:var(--muted); font-size:12.5px; }
details.sources > summary { cursor:pointer; font-size:12px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }
details.sources > summary:hover { color:var(--accent); }
details.sources .note { border-top:none; padding-top:0; margin-top:10px; }
__APACSS__
h2.refh { font-size:15px; margin:26px 0 8px; }
@media (max-width:900px){ .stage{flex-direction:column;} #diagram{flex:0 0 auto; width:100%;} .side{position:static; width:100%;} }
@media (max-width:600px){ .stage{flex-direction:column-reverse;} #diagram{overflow-x:auto;} #diagram svg{min-width:700px;} .controls input[type=range]{width:150px;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library &middot; Earth</a><a href="earth-interior.html">The Interior</a><a href="earth.html">Climate</a><a href="light.html">Light</a></nav>
</header>
<h1>The Atmosphere</h1>
<div class="bar" id="views"><button data-v="up" class="on">Up</button><button data-v="made">Made of</button><button type="button" id="scaleBtn" aria-pressed="false">True scale</button><button type="button" id="balloonBtn" aria-pressed="false">Launch a balloon</button></div>
<div class="controls" id="upCtl">
  <label for="alt">height</label>
  <input type="range" id="alt" min="0" max="1000" step="1" value="0">
  <output id="altOut">0 km</output>
  <span class="presets" id="marks"></span>
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
<details class="sources"><summary>Sources</summary>
<p class="note">__NOTE2__</p>
<div class="method"><p>__METHOD__</p></div>
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</details>
</div>
<script>
const L76=__L76__, UPPER=__UPPER__, LAYERS=__LAYERS__, MARKS=__MARKS__, OBJECTS=__OBJECTS__, GASES=__GASES__, WATER=__WATER__, COLUMN=__COLUMN__;
const P0=__P0__, G0=__G0__, RA=__RA__, RE=6356.766, ZTOP=600, W=980;
const el=document.getElementById('diagram');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const RM=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const ease=t=>t<0.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
let view='up', z=0, hot=null;
let sc=0, scaleOn=false, scAnim=0;            // 0: compressed above 120 km; 1: one pixel to the kilometer
const B={t:0,running:false,burst:false,raf:0,last:0,rate:600,v:5,zb:35};   // the balloon: seconds aloft, 5 m/s, bursts at 35 km

/* ---- the standard atmosphere ---- */
const geopot=z=>RE*z/(RE+z);                       // geometric km to geopotential km
const BASE=[]; { let p=P0; for(let i=0;i<L76.length;i++){ const [h,T,L]=L76[i]; BASE.push([h,T,L,p]); if(i+1<L76.length){ const dh=L76[i+1][0]-h; p= L===0?p*Math.exp(-G0*dh*1000/(RA*T)):p*Math.pow(T/(T+L*dh),G0*1000/(RA*L)); } } }
function std(zkm){ // temperature K and pressure Pa at a geometric altitude
  if(zkm<=86){ const h=geopot(zkm); let i=BASE.length-1; while(i>0&&h<BASE[i][0]) i--; const [hb,Tb,L,pb]=BASE[i]; const T=Tb+L*(h-hb); const p=L===0?pb*Math.exp(-G0*(h-hb)*1000/(RA*Tb)):pb*Math.pow(Tb/T,G0*1000/(RA*L)); return {T,p,rho:p/(RA*T)}; }
  let i=0; while(i+1<UPPER.length-1&&zkm>UPPER[i+1][0]) i++; const a=UPPER[i], b=UPPER[i+1]; const f=(zkm-a[0])/(b[0]-a[0]);
  return {T:a[1]+(b[1]-a[1])*f, p:Math.exp(Math.log(a[2])+(Math.log(b[2])-Math.log(a[2]))*f), rho:Math.exp(Math.log(a[3])+(Math.log(b[3])-Math.log(a[3]))*f)}; }
const sound=T=>Math.sqrt(1.4*RA*T);
function boil(p){ // Antoine for water, 1 to 100 C: log10(p mmHg) = 8.07131 - 1730.63/(233.426 + t)
  return 1730.63/(8.07131-Math.log10(p/133.322))-233.426; }
const layerOf=zk=>LAYERS.find(l=>zk>=l.a&&zk<l.b)||LAYERS[LAYERS.length-1];
const f1=x=>x.toLocaleString('en-US',{minimumFractionDigits:1,maximumFractionDigits:1});
const km=zk=>zk<10?f1(zk)+' km':Math.round(zk).toLocaleString('en-US')+' km';
function pres(p){ if(p>=100) return (p/100).toLocaleString('en-US',{maximumFractionDigits:1})+' hPa'; if(p>=0.01) return p.toLocaleString('en-US',{maximumFractionDigits:3})+' Pa'; const e=Math.floor(Math.log10(p)); return (p/Math.pow(10,e)).toFixed(2)+'\\u00d710<sup>'+e+'</sup> Pa'; }
function dens(r){ if(r>=0.01) return r.toFixed(3)+' kg/m\\u00b3'; if(r>=1e-6) return (r*1e3).toPrecision(3)+' g/m\\u00b3'; const e=Math.floor(Math.log10(r)); return (r/Math.pow(10,e)).toFixed(2)+'\\u00d710<sup>'+e+'</sup> kg/m\\u00b3'; }
function share(p){ const s=p/P0; if(s>=0.001) return (s*100).toFixed(s>0.1?0:s>0.01?1:2)+'%'; if(s>=1e-6) return 'a '+(1/s).toLocaleString('en-US',{maximumFractionDigits:0})+'th'; return 'one part in '+(1/s).toExponential(1).replace('e+','\\u00d710^'); }

/* ---- the card ---- */
function card(kind,name,rows,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').innerHTML=name;
  document.getElementById('numTxt').innerHTML=rows.filter(r=>r[1]).map(([k,v])=>'<b>'+esc(k)+'</b> '+v).join('<br>');
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').textContent=src;
}
function showZ(zk){ const s=std(zk), L=layerOf(zk); const m=MARKS.find(x=>Math.abs(x.z-zk)<=Math.max(0.05,zk*0.01)); const tb=boil(s.p);
  card('At a height of', km(zk)+(m?', '+esc(m.n):''), [['layer',L.n],['temperature',Math.round(s.T-273.15)+' \\u00b0C, '+Math.round(s.T)+' K'],['pressure',pres(s.p)],['air above',share(s.p)+' of it'],['air below',s.p/P0>0.9999?'':(100-s.p/P0*100).toFixed(s.p/P0>0.1?0:s.p/P0>0.01?1:s.p/P0>0.001?2:3)+'%'],
    ['density',dens(s.rho)],['speed of sound',zk<=86?Math.round(sound(s.T))+' m/s':''],['water boils at',tb>-40&&zk<=86?Math.round(tb)+' \\u00b0C':''],balloonRow()||['','']], m?m.b:L.t, m?m.s:'US Standard Atmosphere 1976'); }
function showLayer(k){ const L=LAYERS.find(x=>x.k===k); const a=std(L.a), b=std(Math.min(L.b,ZTOP)-0.001);
  card('A layer', L.n, [['from',km(L.a)+' to '+km(L.b)],['temperature',Math.round(a.T-273.15)+' to '+Math.round(b.T-273.15)+' \\u00b0C'],['holds',((a.p-b.p)/P0*100).toFixed(a.p-b.p>P0*0.01?1:3)+'% of the air']], L.t, 'US Standard Atmosphere 1976'); }
function showGas(g){ card('In dry air', esc(g.n)+', '+g.f, [['by volume', g.x>=0.001?(g.x*100).toFixed(g.x>0.1?1:2)+'%':(g.x*1e6).toLocaleString('en-US',{maximumFractionDigits:2})+' parts per million'],['in a breath of half a liter', g.x>=1e-3?(g.x*0.5*1000).toFixed(0)+' ml':(g.x*0.5*1e6).toFixed(g.x>1e-5?0:1)+' \\u00b5l']], g.b, 'Picard et al. 2008; NOAA GML'); }

/* ---- up ---- */
const P={x:70,y:30,w:250,h:600}, ZB=120;                   // the column: linear to 120 km, then compressed
const YZc=zk=>zk<=ZB?P.y+P.h-(zk/ZB)*P.h*0.78:P.y+P.h*0.22-((zk-ZB)/(ZTOP-ZB))*P.h*0.22;
const YZt=zk=>P.y+P.h-zk/ZTOP*P.h;                          // true scale: one pixel to the kilometer
const YZ=zk=>sc<=0?YZc(zk):sc>=1?YZt(zk):(1-sc)*YZc(zk)+sc*YZt(zk);
const ZY=y=>{ let lo=0, hi=ZTOP; for(let i=0;i<40;i++){ const m=(lo+hi)/2; if(YZ(m)>y) lo=m; else hi=m; } return (lo+hi)/2; };
const PR=[{k:'T',n:'temperature, K',x0:100,x1:1000,f:zk=>std(zk).T,c:'#ffb02e',log:false,fmt:v=>Math.round(v)+' K'},{k:'p',n:'pressure, Pa',x0:1e-8,x1:2e5,f:zk=>std(zk).p,c:'#58a6ff',log:true,fmt:v=>pres(v)},{k:'rho',n:'density, kg/m\\u00b3',x0:1e-13,x1:2,f:zk=>std(zk).rho,c:'#9be564',log:true,fmt:v=>dens(v)}];
const PX0=520, PW=130, PG=30;
function up(){
  let s='';
  // the column with its layers
  for(const L of LAYERS){ const y1=YZ(L.a), y0=YZ(Math.min(L.b,ZTOP)); const ty=y1-y0>=17?y0+14:y1-3; s+='<g data-l="'+L.k+'" style="cursor:pointer"><rect x="'+P.x+'" y="'+y0.toFixed(1)+'" width="'+P.w+'" height="'+(y1-y0).toFixed(1)+'" fill="'+L.c+'" opacity="'+(hot===L.k?0.35:0.16)+'"/><text x="'+(P.x+8)+'" y="'+ty.toFixed(1)+'" font-size="11" fill="'+L.c+'">'+L.n+'</text></g>'; }
  s+='<rect x="'+P.x+'" y="'+P.y+'" width="'+P.w+'" height="'+P.h+'" fill="none" stroke="#2b2b2b"/>';
  if(sc<1){ s+='<line x1="'+P.x+'" y1="'+YZ(ZB).toFixed(1)+'" x2="'+(P.x+P.w)+'" y2="'+YZ(ZB).toFixed(1)+'" stroke="#3d444d" stroke-dasharray="4 3" opacity="'+(1-sc).toFixed(2)+'"/><text x="'+(P.x+P.w-6)+'" y="'+(YZ(ZB)-4).toFixed(1)+'" text-anchor="end" font-size="9.5" fill="#6b7280" opacity="'+(1-sc).toFixed(2)+'">compressed above 120 km</text>'; }
  else s+='<text x="'+(P.x+P.w-6)+'" y="'+(P.y+30)+'" text-anchor="end" font-size="9.5" fill="#6b7280">to scale: one pixel to the kilometer</text>';
  const ticks=sc<0.5?[0,20,40,60,80,100,120,200,300,400,500,600]:[0,50,100,150,200,250,300,350,400,450,500,550,600];
  for(const zk of ticks){ const y=YZ(zk); s+='<line x1="'+(P.x-5)+'" y1="'+y.toFixed(1)+'" x2="'+P.x+'" y2="'+y.toFixed(1)+'" stroke="#8a94a6"/><text x="'+(P.x-8)+'" y="'+(y+4).toFixed(1)+'" text-anchor="end" font-size="10.5" fill="#9a9a9a">'+zk+'</text>'; }
  s+='<text transform="translate(16,'+(P.y+P.h/2)+') rotate(-90)" text-anchor="middle" font-size="11.5" fill="#9a9a9a">height, km</text>';
  // the things in the air, each at its height
  s+=objectsSvg();
  // the marks, packed: pushed up off each other, then the pile pulled back down so it hangs around its points
  const sorted=[...MARKS].sort((a,b)=>a.z-b.z), ys=[]; let lastY=1e9;
  for(const m of sorted){ const y0=YZ(m.z); const y=Math.min(y0,lastY-14); ys.push(y); lastY=y; }
  { let lo=P.y+P.h-4; for(let i=0;i<ys.length;i++){ if(ys[i]>lo) ys[i]=lo; lo=ys[i]-14; } }
  sorted.forEach((m,i)=>{ const y0=YZ(m.z), y=ys[i], on=hot===m.k;
    s+='<g data-k="'+m.k+'" style="cursor:pointer"><line x1="'+(P.x+P.w)+'" y1="'+y0.toFixed(1)+'" x2="'+(P.x+P.w+16)+'" y2="'+y.toFixed(1)+'" stroke="'+(on?'#ffb02e':'#3d444d')+'"/><circle cx="'+(P.x+P.w)+'" cy="'+y0.toFixed(1)+'" r="2.5" fill="'+(on?'#ffb02e':'#9a9a9a')+'"/>';
    s+='<text x="'+(P.x+P.w+20)+'" y="'+(y+3.5).toFixed(1)+'" font-size="10.5" fill="'+(on?'#ffb02e':'#9a9a9a')+'">'+esc(m.n)+'</text></g>'; });
  s+=balloonSvg();
  // the profiles
  PR.forEach((p,i)=>{ const x0=PX0+i*(PW+PG); const X=v=>x0+(p.log?(Math.log10(v)-Math.log10(p.x0))/(Math.log10(p.x1)-Math.log10(p.x0)):(v-p.x0)/(p.x1-p.x0))*PW;
    s+='<rect x="'+x0+'" y="'+P.y+'" width="'+PW+'" height="'+P.h+'" fill="none" stroke="#2b2b2b"/><text x="'+x0+'" y="'+(P.y-10)+'" font-size="11" fill="#9a9a9a">'+p.n+'</text>';
    for(const L of LAYERS){ if(L.a===0) continue; const y=YZ(L.a); s+='<line x1="'+x0+'" y1="'+y.toFixed(1)+'" x2="'+(x0+PW)+'" y2="'+y.toFixed(1)+'" stroke="#2b2b2b" stroke-dasharray="3 4"/>'; }
    const ticks=p.log?[p.x0,1e-4,1,1e4].filter(v=>v>=p.x0&&v<=p.x1):[200,600,1000];
    for(const v of ticks){ const x=X(v); s+='<line x1="'+x.toFixed(1)+'" y1="'+(P.y+P.h)+'" x2="'+x.toFixed(1)+'" y2="'+(P.y+P.h+5)+'" stroke="#8a94a6"/><text x="'+x.toFixed(1)+'" y="'+(P.y+P.h+17)+'" text-anchor="'+(x<x0+6?'start':x>x0+PW-6?'end':'middle')+'" font-size="9.5" fill="#6b7280">'+(p.log?'10<tspan dy="-3" font-size="7">'+Math.round(Math.log10(v))+'</tspan>':v)+'</text>'; }
    let d=''; for(let zk=0; zk<=ZTOP; zk+=zk<120?0.5:5){ d+=(d?'L':'M')+X(p.f(zk)).toFixed(1)+','+YZ(zk).toFixed(1); }
    s+='<path d="'+d+'" fill="none" stroke="'+p.c+'" stroke-width="2"/>';
    const vx=X(p.f(z)), vy=YZ(z), left=vx>x0+PW*0.55;
    s+='<circle cx="'+vx.toFixed(1)+'" cy="'+vy.toFixed(1)+'" r="4.5" fill="#ffb02e" stroke="#121212" stroke-width="1.2"/>';
    s+='<text class="val" x="'+(left?vx-8:vx+8).toFixed(1)+'" y="'+(vy<P.y+14?vy+14:vy-7).toFixed(1)+'" text-anchor="'+(left?'end':'start')+'" font-size="9.5" fill="'+p.c+'">'+p.fmt(p.f(z))+'</text>';
    s+='<rect data-p="'+p.k+'" x="'+x0+'" y="'+P.y+'" width="'+PW+'" height="'+P.h+'" fill="transparent" style="cursor:crosshair"/>'; });
  // the marker
  const y=YZ(z);
  s+='<g id="marker" style="cursor:ns-resize"><line x1="'+P.x+'" y1="'+y.toFixed(1)+'" x2="'+(PX0+3*(PW+PG)-PG)+'" y2="'+y.toFixed(1)+'" stroke="#ffb02e" stroke-width="1" opacity="0.6"/><circle cx="'+(P.x+P.w/2)+'" cy="'+y.toFixed(1)+'" r="6" fill="#ffb02e" stroke="#121212" stroke-width="1.5"/>';
  s+='<text x="'+(P.x+P.w/2+12)+'" y="'+(y+4).toFixed(1)+'" font-size="11.5" font-weight="700" fill="#ffb02e">'+km(z)+'</text></g>';
  return {svg:s, h:P.y+P.h+30};
}

/* ---- the balloon: launched from the ground, up at 5 m/s, swelling with the fall in pressure ---- */
function balloonSvg(){
  if(!(B.t>0||B.running)) return '';
  const zk=Math.min(B.zb,B.v*B.t/1000), x=P.x+0.42*P.w, y=YZ(zk), s0=std(0), s1=std(zk);
  const grow=Math.cbrt((s1.T/s0.T)*(s0.p/s1.p)), r=3*grow;      // the ideal gas: volume goes as T over p
  let s='<g id="balloon" pointer-events="none">';
  if(B.burst){ for(let i=0;i<8;i++){ const a=i*Math.PI/4; s+='<line x1="'+(x+Math.cos(a)*r*0.5).toFixed(1)+'" y1="'+(y-r+Math.sin(a)*r*0.5).toFixed(1)+'" x2="'+(x+Math.cos(a)*r*1.3).toFixed(1)+'" y2="'+(y-r+Math.sin(a)*r*1.3).toFixed(1)+'" stroke="#f4efe2" stroke-width="1.2" opacity="0.8"/>'; }
    s+='<text x="'+(x-r*1.5-4).toFixed(1)+'" y="'+(y-r+4).toFixed(1)+'" text-anchor="end" font-size="9.5" fill="#f4efe2">burst at '+km(zk)+'</text>'; }
  else { s+='<circle cx="'+x+'" cy="'+(y-r).toFixed(1)+'" r="'+r.toFixed(1)+'" fill="#f4efe2" fill-opacity="0.85" stroke="#f4efe2" stroke-width="0.8"/><line x1="'+x+'" y1="'+y.toFixed(1)+'" x2="'+x+'" y2="'+(y+6).toFixed(1)+'" stroke="#d8dee8" stroke-width="0.8"/><rect x="'+(x-1.5)+'" y="'+(y+6).toFixed(1)+'" width="3" height="2.5" fill="#d8dee8"/>';
    s+='<text x="'+(x-r-6).toFixed(1)+'" y="'+(y-r+4).toFixed(1)+'" text-anchor="end" font-size="9.5" fill="#f4efe2">'+grow.toFixed(1)+'\u00d7 its launch width</text>'; }
  return s+'</g>';
}
const bmin=t=>{ const m=Math.round(t/60); return m<60?m+' min':Math.floor(m/60)+' h '+String(m%60).padStart(2,'0')+' min'; };
function balloonRow(){ if(!(B.t>0||B.running)) return null; const zk=Math.min(B.zb,B.v*B.t/1000), s0=std(0), s1=std(zk), grow=Math.cbrt((s1.T/s0.T)*(s0.p/s1.p));
  return ['the balloon', B.burst?'burst at '+km(B.zb)+' after '+bmin(B.t)+', '+grow.toFixed(1)+' times its launch width':bmin(B.t)+' after launch, rising at 5 m/s, '+grow.toFixed(1)+' times its launch width']; }
function balloonFrame(now){
  if(!B.running) return;
  const dt=(now-B.last)/1000; B.last=now; B.t=Math.min(B.zb*1000/B.v, B.t+dt*B.rate);
  setZ(B.v*B.t/1000);
  if(B.t>=B.zb*1000/B.v){ B.burst=true; balloonStop(true); return; }
  B.raf=requestAnimationFrame(balloonFrame);
}
function balloonStop(done){ B.running=false; cancelAnimationFrame(B.raf); const b=document.getElementById('balloonBtn');
  b.textContent=done?'Launch a balloon':'Resume the balloon'; b.classList.remove('run'); b.setAttribute('aria-pressed','false'); render(); showZ(z); }
function balloonStart(){ const b=document.getElementById('balloonBtn');
  if(view!=='up') setView('up');
  if(B.burst){ B.t=0; B.burst=false; }
  hot=null;
  if(RM){ B.t=B.zb*1000/B.v; B.burst=true; setZ(B.zb); return; }
  B.running=true; B.last=performance.now(); b.textContent='Pause'; b.classList.add('run'); b.setAttribute('aria-pressed','true'); B.raf=requestAnimationFrame(balloonFrame); }
document.getElementById('balloonBtn').addEventListener('click',()=>{ if(B.running) balloonStop(false); else balloonStart(); });

/* ---- true scale: the compression above 120 km tweens away ---- */
function setScale(on){
  scaleOn=on; const b=document.getElementById('scaleBtn'); b.classList.toggle('on',on); b.setAttribute('aria-pressed',on?'true':'false');
  cancelAnimationFrame(scAnim);
  if(RM){ sc=on?1:0; render(); return; }
  const from=sc, to=on?1:0, t0=performance.now(), dur=900;
  const frame=now=>{ const u=Math.min(1,(now-t0)/dur); sc=from+(to-from)*ease(u); render(); if(u<1) scAnim=requestAnimationFrame(frame); };
  scAnim=requestAnimationFrame(frame);
}
document.getElementById('scaleBtn').addEventListener('click',()=>setScale(!scaleOn));

/* ---- things in the air ---- */
const ICON={
  airliner:'<path d="M-9,0C-9,-1.7 6,-1.9 9,-0.5L9,0.6C6,1.7 -9,1.7 -9,0Z"/><path d="M-9,-0.6L-11,-5L-7.8,-5L-5.2,-1Z"/><path d="M-2.5,0.6L3,0.6L-1,4.2L-3.4,4.2Z"/>',
  concorde:'<path d="M-10,-0.2L7,-0.9L12,0.9L7,0.9L-10,0.8Z"/><path d="M-10,-0.2L-10.8,-5L-7.6,-0.4Z"/><path d="M-7,0.8L4,0.8L-7,3.2Z"/>',
  u2:'<path d="M-9,0C-9,-1.2 6,-1.3 9,-0.2L9,0.4C6,1.2 -9,1.2 -9,0Z"/><path d="M-9,-0.4L-10.5,-4.2L-7.6,-4.2L-5.8,-0.8Z"/><path d="M-6,0.2L6,0.2L6,1L-6,1Z"/>',
  sr71:'<path d="M-11,0.4L7,-0.9L12,0.1L7,1L-11,1.2Z"/><path d="M-9.5,-0.1L-10.5,-3.8L-7.8,-3.8L-6.8,-0.3Z"/><path d="M-7,1L2,1L-7,3Z"/>',
  x15:'<path d="M-7,0L6,-1.2L10,0L6,1.2Z"/><path d="M-7,-0.9L-9,-4.8L-5,-1Z"/><path d="M-7,0.9L-9,4.8L-5,1Z"/>',
  balloon:'<circle cx="0" cy="-5" r="4"/><path d="M0,-1L0,3" fill="none" stroke-width="0.8"/><rect x="-1.2" y="3" width="2.4" height="2"/>',
  station:'<path d="M-11,-0.4L11,-0.4L11,0.4L-11,0.4Z"/><rect x="-11" y="-4.5" width="4" height="9"/><rect x="-5.5" y="-4.5" width="4" height="9"/><rect x="1.5" y="-4.5" width="4" height="9"/><rect x="7" y="-4.5" width="4" height="9"/><rect x="-1.2" y="-1.6" width="2.4" height="3.2"/>',
  telescope:'<rect x="-5" y="-2" width="10" height="4" rx="1"/><rect x="-3" y="-7" width="6" height="4"/><rect x="-3" y="3" width="6" height="4"/>',
  cloud:'<path d="M-12,2C-14,2 -14,-2 -11,-2C-11,-5 -6,-6 -4,-3C-3,-7 4,-7 5,-3C7,-5 11,-4 11,-1C14,-1 14,2 11,2Z"/>'
};
function objectsSvg(){
  let s='';
  for(const o of OBJECTS){
    if(sc>0.5&&o.z<60) continue;                       // at true scale everything below 60 km is a smear; the marks still name them
    const m=o.n?null:MARKS.find(x=>x.k===o.k), key=o.k, on=hot===key;
    const x=P.x+o.f*P.w, y=YZ(o.z), col=on?'#ffb02e':'#d8dee8';
    const attr=(m?'data-k':'data-o')+'="'+key+'" style="cursor:pointer"';
    if(o.kind==='storm'){ // from the cloud base to the anvil at the tropopause
      const yb=YZ(1.5), yt=y, w=16;
      s+='<g '+attr+'><path d="M'+(x-w)+','+yb.toFixed(1)+'C'+(x-w-4)+','+(yb-8).toFixed(1)+' '+(x-w+2)+','+(yt+14).toFixed(1)+' '+(x-8)+','+(yt+5).toFixed(1)+'L'+(x-30)+','+(yt+2).toFixed(1)+'C'+(x-28)+','+(yt-3).toFixed(1)+' '+(x+28)+','+(yt-3).toFixed(1)+' '+(x+34)+','+(yt+2).toFixed(1)+'L'+(x+9)+','+(yt+5).toFixed(1)+'C'+(x+w)+','+(yt+14).toFixed(1)+' '+(x+w+4)+','+(yb-8).toFixed(1)+' '+(x+w)+','+yb.toFixed(1)+'Z" fill="'+col+'" fill-opacity="'+(on?0.6:0.42)+'" stroke="'+col+'" stroke-opacity="0.7" stroke-width="0.8"/></g>';
      continue; }
    if(o.kind==='wisp'){ s+='<g '+attr+'><path d="M'+(x-30)+','+y.toFixed(1)+'q7,-3 14,0t14,0t14,0t14,0" fill="none" stroke="'+(on?'#ffb02e':'#8fd3ff')+'" stroke-width="1.6" opacity="0.8"/><rect x="'+(x-30)+'" y="'+(y-5).toFixed(1)+'" width="56" height="10" fill="transparent"/></g>'; continue; }
    if(o.kind==='meteor'){ s+='<g '+attr+'><path d="M'+(x-14)+','+(y-8).toFixed(1)+'L'+x+','+y.toFixed(1)+'" stroke="'+(on?'#ffb02e':'#ffe7a8')+'" stroke-width="1.4" stroke-linecap="round"/><circle cx="'+x+'" cy="'+y.toFixed(1)+'" r="1.8" fill="'+(on?'#ffb02e':'#fff4d6')+'"/><rect x="'+(x-16)+'" y="'+(y-10).toFixed(1)+'" width="20" height="14" fill="transparent"/></g>'; continue; }
    if(o.kind==='aurora'){ // the green curtain from 100 to 150 km
      const y1=YZ(100), y2=YZ(150); let g='';
      for(let i=0;i<6;i++){ const xx=x-14+i*5.6; g+='<line x1="'+xx.toFixed(1)+'" y1="'+(y1-2*(i%2)).toFixed(1)+'" x2="'+xx.toFixed(1)+'" y2="'+(y2+3*(i%3)).toFixed(1)+'" stroke="'+(on?'#ffb02e':'#5ef08a')+'" stroke-width="2.2" opacity="'+(0.35+0.1*(i%3))+'"/>'; }
      s+='<g '+attr+'>'+g+'<rect x="'+(x-16)+'" y="'+y2.toFixed(1)+'" width="32" height="'+(y1-y2).toFixed(1)+'" fill="transparent"/></g>'; continue; }
    const isc=o.kind==='cloud'?1.1:1;
    s+='<g '+attr+' transform="translate('+x.toFixed(1)+','+y.toFixed(1)+') scale('+isc+')" fill="'+col+'" stroke="none">'+ICON[o.kind]+'<rect x="-12" y="-8" width="24" height="14" fill="transparent"/></g>';
    if(o.n&&o.kind!=='cloud'){ const left=o.f>0.6; s+='<text x="'+(left?x-14:x+14).toFixed(1)+'" y="'+(y+3.5).toFixed(1)+'" text-anchor="'+(left?'end':'start')+'" font-size="9.5" fill="'+(on?'#ffb02e':'#b8c0cc')+'" pointer-events="none">'+esc(o.n.replace(/^the /,''))+'</text>'; }
  }
  return s;
}
function showObj(o){ card('In the air', esc(o.n), [['height',km(o.z)],['pressure there',pres(std(o.z).p)],['temperature',Math.round(std(o.z).T-273.15)+' °C']], o.b.replace(/&aacute;/g,'á'), o.s); }

/* ---- made of ---- */
function made(){
  let s=''; const x0=60, w=860, y0=60, h=70;
  s+='<text x="'+x0+'" y="'+(y0-14)+'" font-size="12" fill="#9a9a9a">dry air by volume</text>';
  let x=x0; const big=GASES.slice(0,3), colors=['#58a6ff','#f28cb0','#9be564','#ffb02e'];
  big.forEach((g,i)=>{ const ww=g.x*w; s+='<g data-g="'+i+'" style="cursor:pointer"><rect x="'+x.toFixed(1)+'" y="'+y0+'" width="'+ww.toFixed(1)+'" height="'+h+'" fill="'+colors[i]+'" opacity="'+(hot==='g'+i?0.95:0.75)+'"/>';
    if(ww>40) s+='<text x="'+(x+ww/2).toFixed(1)+'" y="'+(y0+h/2+5)+'" text-anchor="middle" font-size="13" fill="#0b1a2b" font-weight="600">'+esc(g.n)+' '+(g.x*100).toFixed(g.x>0.1?1:2)+'%</text>'; s+='</g>'; x+=ww; });
  const rest=1-big.reduce((a,g)=>a+g.x,0); s+='<rect x="'+x.toFixed(1)+'" y="'+y0+'" width="'+Math.max(2,rest*w).toFixed(1)+'" height="'+h+'" fill="#ffb02e"/>';
  s+='<text x="'+(x0+w)+'" y="'+(y0+h+16)+'" text-anchor="end" font-size="10.5" fill="#9a9a9a">argon '+(GASES[2].x*100).toFixed(2)+'%, and everything else in the last '+(rest*100).toFixed(2)+'%: the sliver at the right</text>';
  // the trace gases on a log line
  const y1=270; s+='<text x="'+x0+'" y="'+(y1-84)+'" font-size="12" fill="#9a9a9a">the trace gases, parts per million, on a log scale</text>';
  const LX=v=>x0+(Math.log10(v)+1)/(Math.log10(1e6)+1)*w;   // 0.1 ppm to a million
  s+='<line x1="'+x0+'" y1="'+y1+'" x2="'+(x0+w)+'" y2="'+y1+'" stroke="#8a94a6"/>';
  for(const v of [0.1,1,10,100,1000,1e4,1e5,1e6]){ const xx=LX(v); s+='<line x1="'+xx.toFixed(1)+'" y1="'+(y1-4)+'" x2="'+xx.toFixed(1)+'" y2="'+(y1+4)+'" stroke="#8a94a6"/><text x="'+xx.toFixed(1)+'" y="'+(y1+18)+'" text-anchor="middle" font-size="10" fill="#6b7280">'+(v>=1e6?'all of it':v>=1e4?(v/1e4)+'%':v.toLocaleString('en-US'))+'</text>'; }
  let lane=0, lastX=-1e9;
  GASES.forEach((g,i)=>{ const xx=LX(g.x*1e6); if(xx-lastX<70) lane=(lane+1)%3; else lane=0; lastX=xx; const yy=y1-30-lane*22;
    s+='<g data-g="'+i+'" style="cursor:pointer"><line x1="'+xx.toFixed(1)+'" y1="'+y1+'" x2="'+xx.toFixed(1)+'" y2="'+(yy+4)+'" stroke="'+(hot==='g'+i?'#ffb02e':'#3d444d')+'"/><circle cx="'+xx.toFixed(1)+'" cy="'+y1+'" r="4" fill="'+(i<3?colors[i]:'#ffb02e')+'"/><text x="'+xx.toFixed(1)+'" y="'+yy+'" text-anchor="middle" font-size="10.5" fill="'+(hot==='g'+i?'#ffb02e':'#e6e6e6')+'">'+esc(g.n)+'</text></g>'; });
  const wx=LX(WATER.x*1e6); s+='<g data-g="w" style="cursor:pointer"><line x1="'+wx.toFixed(1)+'" y1="'+y1+'" x2="'+wx.toFixed(1)+'" y2="'+(y1+40)+'" stroke="#6ee7f2" stroke-dasharray="3 3"/><circle cx="'+wx.toFixed(1)+'" cy="'+y1+'" r="4" fill="#6ee7f2"/><text x="'+wx.toFixed(1)+'" y="'+(y1+54)+'" text-anchor="middle" font-size="10.5" fill="#6ee7f2">water vapor, on average</text><text x="'+wx.toFixed(1)+'" y="'+(y1+66)+'" text-anchor="middle" font-size="9.5" fill="#6b7280">not part of dry air; from nothing to 4%</text></g>';
  // the column of air
  const y2=390; s+='<text x="'+x0+'" y="'+y2+'" font-size="12" fill="#9a9a9a">the whole column</text>';
  const rows=[['mass of the air',(COLUMN.mass/1e18).toFixed(2)+' \\u00d7 10\\u00b9\\u2078 kg'],['over each square meter',(P0/G0/1000).toFixed(1)+' metric tons'],['water in it',(COLUMN.water/1e15).toFixed(0)+' \\u00d7 10\\u00b9\\u2075 kg, '+(COLUMN.water/COLUMN.mass*100).toFixed(2)+'%'],['half of it below',halfHeight().toFixed(1)+' km'],['ninety percent below',heightAt(0.1).toFixed(0)+' km'],['ninety-nine percent below',heightAt(0.01).toFixed(0)+' km']];
  rows.forEach(([k,v],i)=>{ s+='<text x="'+x0+'" y="'+(y2+24+i*20)+'" font-size="12" fill="#9a9a9a">'+k+'</text><text x="'+(x0+240)+'" y="'+(y2+24+i*20)+'" font-size="12" fill="#e6e6e6">'+v+'</text>'; });
  return {svg:s, h:y2+24+rows.length*20+10};
}
function heightAt(frac){ let lo=0, hi=200; for(let i=0;i<60;i++){ const mid=(lo+hi)/2; if(std(mid).p/P0>frac) lo=mid; else hi=mid; } return (lo+hi)/2; }
function halfHeight(){ return heightAt(0.5); }

/* ---- render and wiring ---- */
function render(){
  const q=view==='up'?up():made();
  el.innerHTML='<svg viewBox="0 0 '+W+' '+q.h+'" xmlns="http://www.w3.org/2000/svg" id="asvg"><rect width="'+W+'" height="'+q.h+'" fill="#121212"/>'+q.svg+'</svg>';
  document.getElementById('upCtl').hidden=view!=='up';
  document.getElementById('altOut').textContent=km(z);
}
const sliderToZ=v=>{ v=v/1000; return v<=0.78?v/0.78*ZB:ZB+(v-0.78)/0.22*(ZTOP-ZB); };
const zToSlider=zk=>Math.round(1000*(zk<=ZB?zk/ZB*0.78:0.78+(zk-ZB)/(ZTOP-ZB)*0.22));
function setZ(zk){ z=Math.max(0,Math.min(ZTOP,zk)); document.getElementById('alt').value=zToSlider(z); render(); showZ(z); }
function setView(v){ view=v; hot=null; for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on',b.dataset.v===v); render(); if(v==='up') showZ(z); else card('Made of','Dry air',[['nitrogen and oxygen',((GASES[0].x+GASES[1].x)*100).toFixed(2)+'%'],['argon',(GASES[2].x*100).toFixed(2)+'%'],['everything else',((1-GASES[0].x-GASES[1].x-GASES[2].x)*100).toFixed(3)+'%']],'A gas under the pointer lands here.','Picard et al. 2008'); }
document.getElementById('views').addEventListener('click',e=>{ const b=e.target.closest('button[data-v]'); if(b) setView(b.dataset.v); });
document.getElementById('alt').addEventListener('input',e=>{ z=sliderToZ(+e.target.value); render(); showZ(z); });
document.getElementById('marks').innerHTML=MARKS.filter(m=>['everest','airliner','armstrong','ozone','karman','iss'].includes(m.k)).map(m=>'<button type="button" data-k="'+m.k+'">'+esc(m.n)+'</button>').join('');
document.getElementById('marks').addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; const m=MARKS.find(x=>x.k===b.dataset.k); hot=m.k; setZ(m.z); });
let dragging=false;
const svgPt=e=>{ const svg=document.getElementById('asvg'), b=svg.getBoundingClientRect(); return [(e.clientX-b.left)/b.width*W,(e.clientY-b.top)/b.height*svg.viewBox.baseVal.height]; };
el.addEventListener('pointerdown',e=>{ if(view!=='up') return; const [x,y]=svgPt(e); if(y>=P.y-6&&y<=P.y+P.h+6&&x>=P.x-10&&!e.target.closest('[data-k]')&&!e.target.closest('[data-o]')){ dragging=true; hot=null; setZ(ZY(Math.max(P.y,Math.min(P.y+P.h,y)))); e.preventDefault(); } });
el.addEventListener('pointermove',e=>{ if(dragging){ const [,y]=svgPt(e); setZ(ZY(Math.max(P.y,Math.min(P.y+P.h,y)))); return; }
  if(view!=='up'||B.running) return; const r=e.target.closest('[data-p]'); if(r){ const [,y]=svgPt(e); const zk=ZY(Math.max(P.y,Math.min(P.y+P.h,y))); if(Math.abs(zk-z)>0.05){ hot=null; setZ(zk); } } });
window.addEventListener('pointerup',()=>{ dragging=false; });
el.addEventListener('pointerover',e=>{ if(dragging||B.running) return; const k=e.target.closest('[data-k]'); if(k){ if(k.getAttribute('data-k')===hot) return; hot=k.getAttribute('data-k'); const m=MARKS.find(x=>x.k===hot); render(); card('A mark on the column', esc(m.n), [['height',km(m.z)],['pressure there',pres(std(m.z).p)],['temperature',Math.round(std(m.z).T-273.15)+' \\u00b0C']], m.b, m.s); return; }
  const ob=e.target.closest('[data-o]'); if(ob){ if(ob.getAttribute('data-o')===hot) return; hot=ob.getAttribute('data-o'); render(); showObj(OBJECTS.find(x=>x.k===hot)); return; }
  const l=e.target.closest('[data-l]'); if(l){ if(l.getAttribute('data-l')===hot) return; hot=l.getAttribute('data-l'); render(); showLayer(hot); return; }
  const g=e.target.closest('[data-g]'); if(g){ const id=g.getAttribute('data-g'); if('g'+id===hot) return; hot='g'+id; render(); showGas(id==='w'?WATER:GASES[+id]); } });

render(); showZ(z);
window.__atm=(q)=>{ const o={view,z,hot,sc,scaleOn,card:document.getElementById('numTxt').innerText,name:document.getElementById('nameTxt').innerText,
  marker:(()=>{ const c=document.querySelector('#marker circle'); return c?+c.getAttribute('cy'):null; })(), half:halfHeight(), h90:heightAt(0.1), h99:heightAt(0.01),
  balloon:{t:B.t,running:B.running,burst:B.burst,z:Math.min(B.zb,B.v*B.t/1000)}, vals:[...document.querySelectorAll('#asvg text.val')].map(t=>t.textContent),
  icons:document.querySelectorAll('#asvg [data-o][transform], #asvg [data-k][transform]').length};
  if(q&&q.z!=null){ const s=std(q.z); o.at={T:s.T,p:s.p,rho:s.rho,c:sound(s.T),boil:boil(s.p)}; } if(q&&q.YZ!=null) o.yz=YZ(q.YZ); return o; };
</script>
</body>
</html>
"""

html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__L76__", _js(LAYERS_76)).replace("__UPPER__", _js(UPPER)).replace("__LAYERS__", _js(layers)).replace("__MARKS__", _js(marks)).replace("__OBJECTS__", _js(objects))
        .replace("__GASES__", _js(gases)).replace("__WATER__", _js(water)).replace("__COLUMN__", _js(COLUMN))
        .replace("__P0__", str(P0)).replace("__G0__", str(G0)).replace("__RA__", str(R_AIR))
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(LAYERS)} layers, {len(MARKS)} marks, {len(GASES)} gases")
