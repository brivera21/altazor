#!/usr/bin/env python3
"""Generate light.html, Light: the spectrum, and the glow of a hot body.

Two views. The spectrum: eighteen decades of wavelength on one log line, the
seven bands, twenty marks from annihilation gamma rays to AM radio, a strip
showing which wavelengths reach the ground, and the visible octave opened out
below in its own colors. A marker drags along the line and the card works
out frequency, photon energy and the temperature a body would need to peak
there. A hot body: Planck's curve for any temperature from the microwave
background to the hottest stars, on log-log axes where every curve is the
same shape slid along Wien's line, with the visible band shaded, the share
of the power that is light, and the color the eye would see.

Data: tools/light_data.py.

Usage: python3 build_light.py
"""

import json
from pathlib import Path

import apa
from light_data import BANDS, MARKS, WINDOWS, BODIES, REFS

OUT = Path(__file__).parent.parent / "light.html"

NOTE1 = ("Light is one thing across eighteen decades of wavelength, from "
         "gamma rays shorter than a nucleus to radio waves longer than a "
         "street, and the eye sees less than one octave of it, the sliver "
         "where the Sun's output peaks and the air is clear. The line runs "
         "from short to long; each mark is a photon that turns up somewhere "
         "in daily life or in the sky, and the strip beneath shows which "
         "wavelengths make it to the ground.")

NOTE2 = ("Everything warm glows, and the second view draws that glow for "
         "any temperature between the sky's background at 2.7 kelvin and a "
         "star at forty thousand. The curve keeps its shape and slides up "
         "and to the left as the body heats; the peak crosses the visible "
         "band near the Sun's temperature, and the swatch gives the color "
         "an eye would see, from ember red through white to a blue that "
         "stops changing.")

METHOD = ("Frequency is c over wavelength, photon energy is hc over "
          "wavelength, and the temperature on the card is Wien's constant "
          "over wavelength, all from CODATA 2018. The hot-body curves are "
          "Planck's law per unit wavelength; per unit frequency the peaks "
          "fall elsewhere, which is why the Sun peaks in the green here and "
          "in the infrared on a frequency plot. The share of power in the "
          "visible band is the curve integrated from 380 to 750 nm over "
          "sigma T to the fourth. Colors come from the CIE 1931 matching "
          "functions in the analytic fit of Wyman, Sloan and Shirley, "
          "converted to sRGB with brightness set aside, so the swatch shows "
          "hue only; below the Draper point, about 800 K, a body does not "
          "glow visibly and the swatch is dark. The ground strip is the "
          "atmosphere's opacity curve reduced to its windows.")


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


bands = [{"k": k, "n": n, "a": a, "b": b, "c": c, "t": t} for k, n, a, b, c, t in BANDS]
marks = [{"k": k, "n": n, "m": m, "what": w, "b": b, "s": s} for k, n, m, w, b, s in MARKS]
windows = [{"a": a, "b": b, "n": n} for a, b, n in WINDOWS]
bodies = [{"k": k, "n": n, "T": T, "b": b, "s": s} for k, n, T, b, s in BODIES]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Light &middot; Altazor</title>
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
.side { flex:0 0 300px; position:sticky; top:16px; }
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
  <nav class="site"><a href="library.html">&larr; Library &middot; The Universe</a><a href="energy.html">Energy</a><a href="matter.html">Matter</a><a href="stars.html">Stars</a></nav>
</header>
<h1>Light</h1>
<div class="bar" id="views"><button data-v="spectrum" class="on">The spectrum</button><button data-v="body">A hot body</button></div>
<div class="controls" id="specCtl">
  <label>the marker</label><output id="specOut"></output>
  <span class="presets" id="jumps"></span>
</div>
<div class="controls" id="bodyCtl" hidden>
  <label for="temp">temperature</label>
  <input type="range" id="temp" min="435" max="4700" step="1" value="3761">
  <output id="tempOut">5,772 K</output>
  <span class="presets" id="bodies"></span>
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
const BANDS=__BANDS__, MARKS=__MARKS__, WIN=__WIN__, BODIES=__BODIES__;
const c=299792458, h=6.62607015e-34, kB=1.380649e-23, eV=1.602176634e-19, bW=2.897771955e-3, sig=5.670374419e-8;
const W=980;
const el=document.getElementById('diagram');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
let view='spectrum', lam=5.02e-7, T=5772, hot=null;

/* ---- numbers ---- */
function si(v,unit,digits){ // 3 significant figures with a prefix
  const P=[[1e18,'E'],[1e15,'P'],[1e12,'T'],[1e9,'G'],[1e6,'M'],[1e3,'k'],[1,''],[1e-3,'m'],[1e-6,'\\u00b5'],[1e-9,'n'],[1e-12,'p'],[1e-15,'f']];
  for(const [s,p] of P) if(v>=s*0.9995) return sf(v/s,digits||3)+' '+p+unit;
  return v.toExponential(2)+' '+unit;
}
function sf(x,n){ if(x===0) return '0'; const d=Math.max(0,n-1-Math.floor(Math.log10(Math.abs(x)))); return x.toLocaleString('en-US',{minimumFractionDigits:0,maximumFractionDigits:Math.min(d,6)}); }
const fmtK=t=>Math.round(t).toLocaleString('en-US')+' K';
const bandOf=m=>BANDS.find(b=>m>=b.a&&m<b.b)||BANDS[BANDS.length-1];
const windowOf=m=>WIN.find(w=>m>=w.a&&m<=w.b);
function planck(m,t){ const x=h*c/(m*kB*t); return x>700?0:2*h*c*c/Math.pow(m,5)/(Math.exp(x)-1); }
function visShare(t){ // the band 380..750 nm as a share of sigma T^4
  let s=0; const a=3.8e-7,b=7.5e-7,n=400; for(let i=0;i<n;i++){ const m=a+(b-a)*(i+0.5)/n; s+=planck(m,t); } s*=(b-a)/n;
  return s*Math.PI/(sig*Math.pow(t,4)); }
/* the CIE 1931 matching functions, the multi-lobe fit of Wyman, Sloan and Shirley (2013); lambda in nm */
const g=(l,mu,s1,s2)=>{ const s=l<mu?s1:s2; const t=(l-mu)/s; return Math.exp(-0.5*t*t); };
const xbar=l=>1.056*g(l,599.8,37.9,31.0)+0.362*g(l,442.0,16.0,26.7)-0.065*g(l,501.1,20.4,26.2);
const ybar=l=>0.821*g(l,568.8,46.9,40.5)+0.286*g(l,530.9,16.3,31.1);
const zbar=l=>1.217*g(l,437.0,11.8,36.0)+0.681*g(l,459.0,26.0,13.8);
function xyzToRgb(X,Y,Z){ // linear sRGB, negatives desaturated, brightness set aside
  let r=3.2406*X-1.5372*Y-0.4986*Z, gg=-0.9689*X+1.8758*Y+0.0415*Z, b=0.0557*X-0.2040*Y+1.0570*Z;
  const m=Math.min(r,gg,b); if(m<0){ r-=m; gg-=m; b-=m; }
  const mx=Math.max(r,gg,b)||1; return [r/mx,gg/mx,b/mx]; }
const gam=v=>v<=0.0031308?12.92*v:1.055*Math.pow(v,1/2.4)-0.055;
const hex=rgb=>'#'+rgb.map(v=>Math.round(255*Math.max(0,Math.min(1,gam(v)))).toString(16).padStart(2,'0')).join('');
function waveColor(nm){ // hue from the matching functions, faded toward the ends of sight
  const rgb=xyzToRgb(xbar(nm),ybar(nm),zbar(nm));
  const br=Math.min(1,Math.max(xbar(nm),ybar(nm),zbar(nm))/0.6);
  return hex(rgb.map(v=>v*br)); }
function bodyColor(t){ let X=0,Y=0,Z=0; for(let l=380;l<=780;l+=5){ const B=planck(l*1e-9,t); X+=B*xbar(l); Y+=B*ybar(l); Z+=B*zbar(l); }
  const s=X+Y+Z||1; return {hex:hex(xyzToRgb(X/s,Y/s,Z/s)), x:X/s, y:Y/s}; }
function colourWord(t){ return t<798?'no visible glow':t<1500?'a deep red':t<2500?'orange-red':t<3500?'orange':t<5000?'yellow-white':t<6500?'white':t<9000?'blue-white':'a blue-white that no longer changes'; }

/* ---- the card ---- */
function card(kind,name,rows,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').innerHTML=name;
  document.getElementById('numTxt').innerHTML=rows.filter(r=>r[1]).map(([k,v])=>'<b>'+esc(k)+'</b> '+v).join('<br>');
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').textContent=src;
}
function photonRows(m){
  const f=c/m, E=h*c/m/eV, tW=bW/m, bd=bandOf(m), w=windowOf(m);
  return [['wavelength',si(m,'m')],['frequency',si(f,'Hz')],['photon energy',E>=1?si(E,'eV'):si(E,'eV')],['a body peaking here',fmtK(tW)],
          ['band',bd.n],['reaches the ground',w?'yes, '+w.n:'no, the air absorbs or reflects it']];
}
function showPoint(m){ const bd=bandOf(m);
  card('A wavelength', si(m,'m'), photonRows(m), bd.t, ''); }
function showMark(k){ const o=MARKS.find(x=>x.k===k); if(!o) return;
  card('A mark on the spectrum', esc(o.n), [['what',esc(o.what)], ...photonRows(o.m)], o.b, o.s); }
function showBody(t){ const col=bodyColor(t), pk=bW/t, share=visShare(t), preset=BODIES.find(b=>Math.abs(b.T-t)/t<0.002);
  card('A hot body', preset?esc(preset.n)+', '+fmtK(t):fmtK(t),
    [['peak wavelength',si(pk,'m')+' ('+bandOf(pk).n+')'],['power from each square meter',si(sig*Math.pow(t,4),'W')],
     ['share of it in the visible',(share*100).toFixed(share<0.01?3:1)+'%'],
     ['color','<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:'+(t<798?'#111':col.hex)+';vertical-align:-1px;border:1px solid #333"></span> '+colourWord(t)]],
    preset?preset.b:'', preset?preset.s:''); }

/* ---- the spectrum ---- */
const S={L:40,R:940,Y:150,LOG0:-14,LOG1:4};
const SX=m=>S.L+(Math.log10(m)-S.LOG0)/(S.LOG1-S.LOG0)*(S.R-S.L);
const SL=px=>Math.pow(10,S.LOG0+(px-S.L)/(S.R-S.L)*(S.LOG1-S.LOG0));
const V={L:140,R:840,Y:400,a:380,b:750};
const VX=nm=>V.L+(nm-V.a)/(V.b-V.a)*(V.R-V.L);
function lanes(items,minGap){ const rows=[]; const out=[]; for(const it of items){ let r=0; while(rows[r]!==undefined && it.x-rows[r]<minGap) r++; rows[r]=it.x+it.w; out.push({...it,lane:r}); } return out; }
function spectrum(){
  let s='';
  // the bands, as a strip above the line
  for(const b of BANDS){ const x0=SX(b.a), x1=SX(b.b);
    s+='<g data-b="'+b.k+'" style="cursor:pointer"><rect x="'+x0.toFixed(1)+'" y="'+(S.Y-58)+'" width="'+(x1-x0).toFixed(1)+'" height="26" fill="'+b.c+'" opacity="'+(hot===b.k?0.55:0.28)+'" rx="3"/>';
    const lab=b.n, cw=6.3, fits=(x1-x0)>lab.length*cw+8;
    s+='<text x="'+((x0+x1)/2).toFixed(1)+'" y="'+(fits?S.Y-41:S.Y-18)+'" text-anchor="middle" font-size="'+(fits?11:10)+'" fill="'+(fits?'#e6e6e6':b.c)+'">'+esc(fits?lab:lab.replace(' rays','').replace(' light',''))+'</text></g>'; }
  // the line and the decades
  s+='<line x1="'+S.L+'" y1="'+S.Y+'" x2="'+S.R+'" y2="'+S.Y+'" stroke="#8a94a6" stroke-width="1.5"/>';
  const names={'-15':'1 fm','-12':'1 pm','-9':'1 nm','-6':'1 \\u00b5m','-3':'1 mm','0':'1 m','3':'1 km'};
  for(let d=S.LOG0; d<=S.LOG1; d++){ const x=SX(Math.pow(10,d)); const big=(d%3===0);
    s+='<line x1="'+x.toFixed(1)+'" y1="'+(S.Y-(big?7:4))+'" x2="'+x.toFixed(1)+'" y2="'+(S.Y+(big?7:4))+'" stroke="#8a94a6"/>';
    if(big) s+='<text x="'+x.toFixed(1)+'" y="'+(S.Y+22)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">'+(names[String(d)]||('10^'+d+' m'))+'</text>'; }
  // the ground strip: what gets through
  s+='<text x="'+S.L+'" y="'+(S.Y+48)+'" font-size="10.5" fill="#6b7280">reaches the ground</text>';
  s+='<rect x="'+S.L+'" y="'+(S.Y+54)+'" width="'+(S.R-S.L)+'" height="10" fill="#1f1f1f" rx="2"/>';
  for(const w of WIN){ const x0=SX(w.a), x1=SX(w.b); s+='<rect x="'+x0.toFixed(1)+'" y="'+(S.Y+54)+'" width="'+Math.max(1.5,x1-x0).toFixed(1)+'" height="10" fill="#9be564" opacity="0.8" rx="1"><title>'+esc(w.n)+'</title></rect>'; }
  // the marks, in lanes below the strip
  const items=lanes(MARKS.map(o=>({...o,x:SX(o.m),w:o.n.length*5.6+10})).sort((a,b)=>a.x-b.x),0);
  for(const o of items){ const y=S.Y+84+o.lane*17;
    s+='<g data-k="'+o.k+'" style="cursor:pointer"><line x1="'+o.x.toFixed(1)+'" y1="'+(S.Y+8)+'" x2="'+o.x.toFixed(1)+'" y2="'+(y-4)+'" stroke="'+(hot===o.k?'#ffb02e':'#3d444d')+'" stroke-width="'+(hot===o.k?1.5:1)+'"/>';
    s+='<circle cx="'+o.x.toFixed(1)+'" cy="'+(S.Y+8)+'" r="2.6" fill="'+(hot===o.k?'#ffb02e':bandOf(o.m).c)+'"/>';
    s+='<text x="'+(o.x+4).toFixed(1)+'" y="'+(y+4)+'" font-size="10.5" fill="'+(hot===o.k?'#ffb02e':'#9a9a9a')+'">'+esc(o.n)+'</text></g>'; }
  const lanesN=Math.max(...items.map(i=>i.lane))+1, yV=S.Y+84+lanesN*17+40; V.Y=yV;
  // the visible octave opened out
  const vx0=SX(3.8e-7), vx1=SX(7.5e-7);
  s+='<path d="M'+vx0.toFixed(1)+','+(S.Y+3)+' L'+V.L+','+(yV-28)+' L'+V.R+','+(yV-28)+' L'+vx1.toFixed(1)+','+(S.Y+3)+' Z" fill="#f4efe2" opacity="0.06"/>';
  s+='<text x="'+V.L+'" y="'+(yV-34)+'" font-size="11" fill="#9a9a9a">the visible octave, 380 to 750 nm, in its own colors</text>';
  for(let nm=V.a; nm<V.b; nm+=2){ s+='<rect x="'+VX(nm).toFixed(1)+'" y="'+(yV-26)+'" width="'+((V.R-V.L)/((V.b-V.a)/2)+0.6).toFixed(2)+'" height="26" fill="'+waveColor(nm+1)+'"/>'; }
  for(const nm of [400,450,500,550,600,650,700,750]){ const x=VX(nm); s+='<line x1="'+x.toFixed(1)+'" y1="'+yV+'" x2="'+x.toFixed(1)+'" y2="'+(yV+5)+'" stroke="#8a94a6"/><text x="'+x.toFixed(1)+'" y="'+(yV+18)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+nm+'</text>'; }
  s+='<text x="'+VX(380).toFixed(1)+'" y="'+(yV+18)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">380 nm</text>';
  const vis=MARKS.filter(o=>o.m>=3.8e-7&&o.m<=7.5e-7); let vy=yV+36;
  for(const o of vis){ const x=VX(o.m*1e9); s+='<g data-k="'+o.k+'" style="cursor:pointer"><line x1="'+x.toFixed(1)+'" y1="'+(yV-26)+'" x2="'+x.toFixed(1)+'" y2="'+(vy-4)+'" stroke="'+(hot===o.k?'#ffb02e':'#6b7280')+'" stroke-dasharray="2 2"/><text x="'+x.toFixed(1)+'" y="'+(vy+8)+'" text-anchor="middle" font-size="10.5" fill="'+(hot===o.k?'#ffb02e':'#9a9a9a')+'">'+esc(o.n)+'</text></g>'; vy+=0; }
  // the marker
  const mx=SX(lam);
  s+='<g id="marker" style="cursor:ew-resize"><line x1="'+mx.toFixed(1)+'" y1="'+(S.Y-64)+'" x2="'+mx.toFixed(1)+'" y2="'+(S.Y+70)+'" stroke="#ffb02e" stroke-width="1.5"/><circle cx="'+mx.toFixed(1)+'" cy="'+S.Y+'" r="6" fill="#ffb02e" stroke="#121212" stroke-width="1.5"/>';
  s+='<text x="'+mx.toFixed(1)+'" y="'+(S.Y-70)+'" text-anchor="middle" font-size="11.5" font-weight="700" fill="#ffb02e">'+si(lam,'m')+'</text></g>';
  if(lam>=3.8e-7&&lam<=7.5e-7){ const x=VX(lam*1e9); s+='<line x1="'+x.toFixed(1)+'" y1="'+(yV-30)+'" x2="'+x.toFixed(1)+'" y2="'+(yV+4)+'" stroke="#ffb02e" stroke-width="1.5"/>'; }
  return {svg:s, h:vy+40};
}

/* ---- the hot body ---- */
const P={x:84,y:36,w:850,h:520}, PL0=-8, PL1=-2, PB0=-4, PB1=18;   // log10 m, log10 W m^-3 sr^-1
const PX=m=>P.x+(Math.log10(m)-PL0)/(PL1-PL0)*P.w;
const PY=B=>P.y+P.h-(Math.log10(Math.max(B,1e-30))-PB0)/(PB1-PB0)*P.h;
function curve(t,step){ let d=''; let on=false; for(let lg=PL0; lg<=PL1+1e-9; lg+=step||0.01){ const m=Math.pow(10,lg), B=planck(m,t); if(B<=Math.pow(10,PB0)){ on=false; continue; } const x=PX(m), y=PY(B); d+=(on?'L':'M')+x.toFixed(1)+','+y.toFixed(1); on=true; } return d; }
function body(){
  let s='';
  s+='<rect x="'+P.x+'" y="'+P.y+'" width="'+P.w+'" height="'+P.h+'" fill="none" stroke="#2b2b2b"/>';
  // the visible band
  for(let nm=380; nm<750; nm+=5){ const x0=PX(nm*1e-9), x1=PX((nm+5)*1e-9); s+='<rect x="'+x0.toFixed(1)+'" y="'+P.y+'" width="'+(x1-x0+0.4).toFixed(1)+'" height="'+P.h+'" fill="'+waveColor(nm+2)+'" opacity="0.13"/>'; }
  // axes
  for(let lg=PL0; lg<=PL1; lg++){ const x=PX(Math.pow(10,lg)); s+='<line x1="'+x.toFixed(1)+'" y1="'+(P.y+P.h)+'" x2="'+x.toFixed(1)+'" y2="'+(P.y+P.h+6)+'" stroke="#8a94a6"/><text x="'+x.toFixed(1)+'" y="'+(P.y+P.h+20)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">'+si(Math.pow(10,lg),'m')+'</text>'; }
  for(let lg=PB0; lg<=PB1; lg+=2){ const y=PY(Math.pow(10,lg)); s+='<line x1="'+(P.x-6)+'" y1="'+y.toFixed(1)+'" x2="'+P.x+'" y2="'+y.toFixed(1)+'" stroke="#8a94a6"/><text x="'+(P.x-9)+'" y="'+(y+4).toFixed(1)+'" text-anchor="end" font-size="10.5" fill="#9a9a9a">10<tspan dy="-4" font-size="8">'+lg+'</tspan></text>'; }
  s+='<text x="'+(P.x+P.w/2)+'" y="'+(P.y+P.h+40)+'" text-anchor="middle" font-size="11.5" fill="#9a9a9a">wavelength</text>';
  s+='<text transform="translate(16,'+(P.y+P.h/2)+') rotate(-90)" text-anchor="middle" font-size="11.5" fill="#9a9a9a">spectral radiance, W per m\\u00b2 per m per steradian</text>';
  // Wien's line of peaks
  let d=''; for(let lg=PL0; lg<=PL1; lg+=0.05){ const m=Math.pow(10,lg), t=bW/m, B=planck(m,t); const x=PX(m), y=PY(B); if(y<P.y||y>P.y+P.h){ d=d&&d.endsWith(' ')?d:d+' '; continue; } d+=(d===''||d.endsWith(' ')?'M':'L')+x.toFixed(1)+','+y.toFixed(1); }
  s+='<path d="'+d.trim()+'" fill="none" stroke="#6b7280" stroke-dasharray="4 4"/>';
  s+='<text x="'+(PX(8e-4)).toFixed(1)+'" y="'+(P.y+P.h-8)+'" text-anchor="end" font-size="10.5" fill="#6b7280">Wien\\u2019s line, where each curve peaks</text>';
  // the presets as ghosts
  let lastX=-1e9, lastY=0;
  for(const b of BODIES){ if(Math.abs(b.T-T)/T<0.002) continue; s+='<g data-body="'+b.k+'" style="cursor:pointer"><path d="'+curve(b.T,0.02)+'" fill="none" stroke="#3d444d" stroke-width="1"/>';
    const pk=bW/b.T, x=PX(pk); let y=PY(planck(pk,b.T))-4; if(x-lastX<70 && Math.abs(y-lastY)<14) y=lastY-13;   // labels of close bodies step upward
    if(y>P.y+2&&y<P.y+P.h-4) s+='<text x="'+(x+6).toFixed(1)+'" y="'+y.toFixed(1)+'" font-size="10" fill="#6b7280">'+esc(b.n)+'</text>'; lastX=x; lastY=y; s+='</g>'; }
  // the body itself
  const col=bodyColor(T).hex, dark=T<798;
  s+='<path d="'+curve(T)+'" fill="none" stroke="'+(dark?'#e6e6e6':col)+'" stroke-width="2.5"/>';
  const pk=bW/T, py=PY(planck(pk,T));
  if(py>P.y&&py<P.y+P.h) s+='<circle cx="'+PX(pk).toFixed(1)+'" cy="'+py.toFixed(1)+'" r="5" fill="#ffb02e" stroke="#121212" stroke-width="1.5"/><text x="'+PX(pk).toFixed(1)+'" y="'+(py-12).toFixed(1)+'" text-anchor="middle" font-size="11.5" font-weight="700" fill="#ffb02e">'+fmtK(T)+', peak '+si(pk,'m')+'</text>';
  // the swatch
  s+='<circle cx="'+(P.x+P.w-50)+'" cy="'+(P.y+50)+'" r="30" fill="'+(dark?'#161616':col)+'" stroke="#333"/>';
  s+='<text x="'+(P.x+P.w-50)+'" y="'+(P.y+98)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+esc(colourWord(T))+'</text>';
  return {svg:s, h:P.y+P.h+50};
}

/* ---- render and wiring ---- */
function render(){
  const r=view==='spectrum'?spectrum():body();
  el.innerHTML='<svg viewBox="0 0 '+W+' '+r.h+'" xmlns="http://www.w3.org/2000/svg" id="lsvg"><rect width="'+W+'" height="'+r.h+'" fill="#121212"/>'+r.svg+'</svg>';
  document.getElementById('specCtl').hidden=view!=='spectrum'; document.getElementById('bodyCtl').hidden=view!=='body';
  document.getElementById('specOut').textContent=si(lam,'m')+', '+bandOf(lam).n;
  document.getElementById('tempOut').textContent=fmtK(T);
}
function setView(v){ view=v; hot=null; for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on',b.dataset.v===v); render(); if(v==='spectrum') showPoint(lam); else showBody(T); }
function setLam(m){ lam=Math.max(Math.pow(10,S.LOG0),Math.min(Math.pow(10,S.LOG1),m)); render(); showPoint(lam); }
function setT(t){ T=Math.max(2.7,Math.min(50000,t)); document.getElementById('temp').value=Math.round(Math.log10(T)*1000); render(); showBody(T); }
document.getElementById('views').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setView(b.dataset.v); });
document.getElementById('temp').addEventListener('input',e=>{ T=Math.pow(10,+e.target.value/1000); render(); showBody(T); });
document.getElementById('bodies').innerHTML=BODIES.map(b=>'<button type="button" data-t="'+b.T+'">'+esc(b.n)+'</button>').join('');
document.getElementById('bodies').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setT(+b.dataset.t); });
document.getElementById('jumps').innerHTML=MARKS.filter(m=>['annih','cuka','sunpeak','body','cmb','h21','fm'].includes(m.k)).map(m=>'<button type="button" data-k="'+m.k+'">'+esc(m.n)+'</button>').join('');
document.getElementById('jumps').addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; const o=MARKS.find(x=>x.k===b.dataset.k); hot=o.k; setLam(o.m); showMark(o.k); });
// drag on the line
let dragging=false, swallow=false;
const svgX=e=>{ const svg=document.getElementById('lsvg'), r=svg.getBoundingClientRect(); return (e.clientX-r.left)/r.width*W; };
el.addEventListener('pointerdown',e=>{ if(view!=='spectrum') return; const x=svgX(e), svg=document.getElementById('lsvg'), r=svg.getBoundingClientRect(), y=(e.clientY-r.top)/r.height*(svg.viewBox.baseVal.height);
  if(y>S.Y-70&&y<S.Y+72&&x>=S.L-6&&x<=S.R+6&&!e.target.closest('[data-k]')){ dragging=true; swallow=true; hot=null; setLam(SL(x)); e.preventDefault(); } });
el.addEventListener('pointermove',e=>{ if(dragging) setLam(SL(Math.max(S.L,Math.min(S.R,svgX(e))))); });
window.addEventListener('pointerup',()=>{ dragging=false; });
el.addEventListener('pointerover',e=>{ if(dragging) return; const k=e.target.closest('[data-k]'); if(k){ if(k.getAttribute('data-k')===hot) return; hot=k.getAttribute('data-k'); render(); showMark(hot); return; }
  const b=e.target.closest('[data-b]'); if(b){ const bd=BANDS.find(x=>x.k===b.getAttribute('data-b')); if(bd.k===hot) return; hot=bd.k; render(); card('A band',esc(bd.n),[['from',si(bd.a,'m')],['to',si(bd.b,'m')],['photon energy',si(h*c/bd.b/eV,'eV')+' to '+si(h*c/bd.a/eV,'eV')]],bd.t,''); return; }
  const g=e.target.closest('[data-body]'); if(g){ const bd=BODIES.find(x=>x.k===g.getAttribute('data-body')); showBody(bd.T); } });
el.addEventListener('click',e=>{ if(swallow){ swallow=false; return; } const k=e.target.closest('[data-k]'); if(k){ const o=MARKS.find(x=>x.k===k.getAttribute('data-k')); hot=o.k; setLam(o.m); showMark(o.k); return; }
  const g=e.target.closest('[data-body]'); if(g){ const bd=BODIES.find(x=>x.k===g.getAttribute('data-body')); setT(bd.T); } });

render(); showPoint(lam);
window.__light=(q)=>{ const o={view,lam,T,hot,marks:document.querySelectorAll('#lsvg g[data-k]').length,
  planck:(m,t)=>planck(m,t), visShare:t=>visShare(t), color:t=>bodyColor(t), wave:nm=>waveColor(nm),
  cmf:l=>[xbar(l),ybar(l),zbar(l)], SX:m=>SX(m), PX:m=>PX(m), PY:B=>PY(B),
  marker:(()=>{ const c=document.querySelector('#marker circle'); return c?+c.getAttribute('cx'):null; })(),
  windows:[...document.querySelectorAll('#lsvg rect[fill="#9be564"]')].map(r=>[+r.getAttribute('x'),+r.getAttribute('width')]),
  card:document.getElementById('numTxt').innerText};
  if(q&&q.planck) o.pv=planck(q.planck[0],q.planck[1]); if(q&&q.share!=null) o.sv=visShare(q.share); if(q&&q.color!=null) o.cv=bodyColor(q.color); if(q&&q.wave!=null) o.wv=waveColor(q.wave); if(q&&q.cmf!=null) o.cmfv=[xbar(q.cmf),ybar(q.cmf),zbar(q.cmf)];
  return o; };
</script>
</body>
</html>
"""

html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__BANDS__", _js(bands)).replace("__MARKS__", _js(marks)).replace("__WIN__", _js(windows)).replace("__BODIES__", _js(bodies))
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(BANDS)} bands, {len(MARKS)} marks, {len(WINDOWS)} windows, {len(BODIES)} bodies")
