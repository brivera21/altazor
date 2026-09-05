#!/usr/bin/env python3
"""Generate temperature.html, human temperature and what temperature is.

Five views on one column of degrees. The whole survivable span, from the
coldest anyone has been rewarmed from to the hottest anyone has walked
away from. The half degree the body actually moves through in a day.
The four everyday sites, which disagree by more than the daily swing.
Fever drawn as a set point the body chases, beside hyperthermia, where
the set point never moves and control is simply losing. And the heat
budget: a hundred watts at rest, fourteen times that up a mountain, and
the four routes it can leave by.

The unit buttons carry the other half of the lesson. A point on the
scale and a difference between two points are not the same conversion,
and the page keeps them apart.

Data: tools/temperature_data.py.

Usage: python3 build_temperature.py
"""

import json
from pathlib import Path

import apa
import temperature_data as D

ROOT = Path(__file__).parent.parent

ZC = {"cold4": "#2b4a8f", "cold3": "#3566bd", "cold2": "#4a87d6",
      "cold1": "#7fb4e8", "low": "#9fb6c4", "norm": "#31d67a",
      "warm1": "#ffd24d", "warm2": "#f0a04b", "warm3": "#e0673f",
      "warm4": "#c02f2f"}

js = dict(
    zones=[dict(lo=a, hi=b, k=k, n=n, b=t, c=ZC[k])
           for a, b, k, n, t in D.ZONES],
    marks=[dict(t=t, n=n, s=s, b=b) for t, n, s, b in D.MARKS],
    day=D.DAY,
    sites=[dict(n=n, m=m, lo=lo, hi=hi, k=k, b=b)
           for n, m, lo, hi, k, b in D.SITES],
    per=D.PERIPHERAL,
    fever=D.FEVER,
    ill=D.HEAT_ILL,
    routes=[dict(n=n, p=p, c=c, b=b) for n, p, c, b in D.ROUTES],
    power=D.POWER,
    scales={k: dict(n=n, s=s, b=b) for k, (n, s, b) in D.SCALES.items()},
)
DATA = json.dumps(js, separators=(",", ":"), ensure_ascii=False)

NOTE1 = ("Five views on one column of degrees. The span is everything a "
         "person has been brought back from, at either end. The day is the "
         "half degree the body actually moves through, and the sites "
         "disagree by more than that, so a reading without its site means "
         "little. Fever sets a target the body then chases, which is why "
         "the chill comes first. Hyperthermia moves no target and is "
         "control losing to heat.")

NOTE2 = ("The unit buttons change every figure. A point on the scale and a "
         "gap between two points convert differently: a body at 37 degrees "
         "Celsius is at 98.6 Fahrenheit, while a rise of one Celsius degree "
         "is a rise of 1.8 Fahrenheit degrees and of exactly one kelvin. "
         "Kelvin is the one tied to what temperature is, the energy of "
         "molecular motion, through a constant fixed by definition.")

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Human Temperature &middot; Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; --warm:#e0673f; --cool:#4a87d6; }
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
.bar { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-bottom:10px; }
.bar .sp { flex:0 0 18px; }
button { font:inherit; font-size:13.5px; padding:6px 14px; border-radius:999px;
  border:1px solid var(--line); background:#1a1a1a; color:var(--text); cursor:pointer; }
button:hover { border-color:var(--accent); }
button.on { background:var(--accent); border-color:var(--accent); color:#0b0b0b; }
button.unit { padding:6px 12px; font-variant-numeric:tabular-nums; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#chart { flex:1 1 640px; min-width:0; }
#chart svg { width:100%; height:auto; display:block; user-select:none; }
.side { flex:0 0 320px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:16px; }
#kindTxt { color:var(--muted); font-size:11.5px; letter-spacing:.09em;
  text-transform:uppercase; }
#nameTxt { font-weight:700; font-size:17px; margin:2px 0 2px; }
#whenTxt { font-size:14px; font-variant-numeric:tabular-nums; }
#bodyTxt { font-size:13.5px; line-height:1.55; margin-top:9px; }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
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
  <nav class="site"><a href="library.html">&larr; Library &middot; Homo Sapiens</a> <a href="migration.html">Migration</a> <a href="populous-countries.html">Population</a> <a href="hominins.html">Hominins</a></nav>
</header>
<h1>Human Temperature</h1>
<div class="bar">
  <button id="vRange" class="on">The whole span</button>
  <button id="vDay">A day</button>
  <button id="vSite">Where it is taken</button>
  <button id="vFever">Fever</button>
  <button id="vHeat">Heat in, heat out</button>
  <span class="sp"></span>
  <button id="uC" class="unit on">&deg;C</button>
  <button id="uF" class="unit">&deg;F</button>
  <button id="uK" class="unit">K</button>
</div>
<div class="stage">
  <div id="chart"></div>
  <div class="side"><div class="card">
    <div id="kindTxt"></div>
    <div id="nameTxt"></div>
    <div id="whenTxt"></div>
    <div id="bodyTxt"></div>
  </div></div>
</div>
<p class="note">__NOTE1__</p>
<p class="note" style="border-top:none; padding-top:0;">__NOTE2__</p>
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</div>
<script>
const D=__DATA__;
const el=document.getElementById('chart');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
let view='range', U='C', hot=null;

// a point on the scale, and a gap between two points, convert differently
function toU(c){ return U==='F'?c*9/5+32 : U==='K'?c+273.15 : c; }
const SYM={C:'°C', F:'°F', K:' K'};
function fmt(c,d){ return toU(c).toFixed(d===undefined?1:d)+SYM[U]; }
function gap(c,d){ return (U==='F'?c*9/5:c).toFixed(d===undefined?1:d)
  +(U==='K'?' K':SYM[U]); }

function card(kind,name,when,body){
  const k=document.getElementById('kindTxt');
  k.textContent=kind; k.style.color='var(--muted)';
  document.getElementById('nameTxt').textContent=name;
  document.getElementById('whenTxt').innerHTML=when||'';
  document.getElementById('bodyTxt').textContent=body||'';
}
function tint(c){ document.getElementById('kindTxt').style.color=c; }

const W=1000, R=34;
function svg(h,inner){
  return '<svg viewBox="0 0 '+W+' '+h+'" xmlns="http://www.w3.org/2000/svg" id="tsvg">'
    +'<rect width="'+W+'" height="'+h+'" fill="#121212"/>'+inner+'</svg>';
}
function txt(x,y,s,o){
  o=o||{};
  return '<text x="'+x+'" y="'+y+'" font-size="'+(o.fs||11)+'"'
    +' fill="'+(o.fill||'#6b7280')+'"'
    +(o.anchor?' text-anchor="'+o.anchor+'"':'')
    +(o.w?' font-weight="'+o.w+'"':'')
    +(o.stroke?' stroke="#121212" stroke-width="2.6" paint-order="stroke"':'')
    +'>'+s+'</text>';
}

/* ---------------------------------------------------------- the whole span */
const RG={lo:10, hi:48, top:44, bot:524, x0:440, x1:520};
function yOf(c){ return RG.bot-(c-RG.lo)/(RG.hi-RG.lo)*(RG.bot-RG.top); }

// Labels that want the same height get pushed apart, keeping their order,
// and a leader line goes back to where each one really points.
function declash(ys,gap,lo,hi){
  const o=ys.map((y,i)=>({y:y,i:i})).sort((a,b)=>a.y-b.y);
  for(let k=1;k<o.length;k++)
    if(o[k].y-o[k-1].y<gap) o[k].y=o[k-1].y+gap;
  const over=o.length?o[o.length-1].y-hi:0;
  if(over>0) for(const q of o) q.y-=over;
  for(let k=o.length-2;k>=0;k--)
    if(o[k+1].y-o[k].y<gap) o[k].y=o[k+1].y-gap;
  if(o.length&&o[0].y<lo){
    const d=lo-o[0].y;
    for(const q of o) q.y+=d;
  }
  const out=ys.slice();
  for(const q of o) out[q.i]=q.y;
  return out;
}
function leader(x0,y0,x1,y1,c){
  const xm=(x0+x1)/2;
  return '<path d="M'+x0.toFixed(1)+','+y0.toFixed(1)+' H'+xm.toFixed(1)
    +' V'+y1.toFixed(1)+' H'+x1.toFixed(1)+'" fill="none" stroke="'
    +(c||'#4a5058')+'" stroke-width="1"/>';
}

function drawRange(){
  let s='';
  for(let i=0;i<D.zones.length;i++){
    const z=D.zones[i], y=yOf(z.hi), h=yOf(z.lo)-yOf(z.hi);
    s+='<g data-z="'+i+'" style="cursor:pointer">'
      +'<rect x="'+RG.x0+'" y="'+y.toFixed(1)+'" width="'+(RG.x1-RG.x0)
      +'" height="'+h.toFixed(1)+'" fill="'+z.c+'" fill-opacity="'
      +(hot&&hot.t==='z'&&hot.i===i?1:0.8)+'"/></g>';
  }
  // the ladder of degrees, in whatever unit is showing
  for(let c=10;c<=48;c+=2){
    const y=yOf(c);
    s+='<path d="M'+(RG.x0-7)+','+y.toFixed(1)+' h7" stroke="#3d444d" stroke-width="1"/>'
      +txt(RG.x0-11,y+3.6,fmt(c,U==='K'?2:0),{anchor:'end'});
  }
  // the marks, to the left, pushed apart where they crowd
  const mt=D.marks.map(m=>yOf(m.t));
  const ml=declash(mt.slice(),32,RG.top+8,RG.bot);
  D.marks.forEach((m,i)=>{
    const on=hot&&hot.t==='m'&&hot.i===i, LX=RG.x0-72;
    s+='<g data-m="'+i+'" style="cursor:pointer">'
      +leader(RG.x0,mt[i],LX+6,ml[i],on?'#e6e6e6':'#4a5058')
      +'<circle cx="'+RG.x0+'" cy="'+mt[i].toFixed(1)+'" r="'+(on?4.5:3)+'" fill="#e6e6e6"/>'
      +txt(LX,ml[i]-3,esc(m.n),{anchor:'end',fs:11.5,
           fill:on?'#e6e6e6':'#8b93a0',stroke:1})
      +txt(LX,ml[i]+11,fmt(m.t),{anchor:'end',fs:11,
           fill:on?'#c8ccd2':'#5d6672',stroke:1})
      +'<rect x="'+(LX-250)+'" y="'+(ml[i]-16)+'" width="256" height="30" fill="transparent"/>'
      +'</g>';
  });
  // what each band is, to the right, pushed apart the same way
  const zt=D.zones.map(z=>(yOf(z.hi)+yOf(z.lo))/2);
  const zl=declash(zt.slice(),32,RG.top+8,RG.bot);
  D.zones.forEach((z,i)=>{
    const on=hot&&hot.t==='z'&&hot.i===i, RX=RG.x1+64;
    s+='<g data-z="'+i+'" style="cursor:pointer">'
      +leader(RG.x1,zt[i],RX-6,zl[i],on?'#e6e6e6':'#3a4048')
      +txt(RX,zl[i]-3,esc(z.n),{fs:11.5,fill:on?'#e6e6e6':'#8b93a0',stroke:1})
      +txt(RX,zl[i]+11,fmt(z.lo,U==='K'?2:1)+' to '+fmt(z.hi,U==='K'?2:1),
           {fs:10.5,fill:on?'#c8ccd2':'#5d6672',stroke:1})
      +'<rect x="'+(RX-6)+'" y="'+(zl[i]-16)+'" width="270" height="26" fill="transparent"/>'
      +'</g>';
  });
  s+=txt(80,RG.top-18,'the whole span a person has been brought back from, '
        +'and the sliver the body holds',{fs:11.5,fill:'#8b93a0'});
  el.innerHTML=svg(560,s);
}

/* ------------------------------------------------------------------ a day */
const DY={x0:150,x1:940,top:70,bot:470,lo:35.9,hi:38.0};
function dx(h){ return DY.x0+h/24*(DY.x1-DY.x0); }
function dy(c){ return DY.bot-(c-DY.lo)/(DY.hi-DY.lo)*(DY.bot-DY.top); }
function dayT(h){
  return D.day.mean - D.day.amp*Math.cos(2*Math.PI*(h-D.day.nadir)/24);
}
function drawDay(){
  let s='';
  for(let c=36;c<=38;c+=0.5){
    const y=dy(c);
    s+='<path d="M'+DY.x0+','+y.toFixed(1)+' H'+DY.x1
      +'" stroke="#242424" stroke-width="1"/>'
      +txt(DY.x0-10,y+3.6,fmt(c,U==='K'?2:1),{anchor:'end'});
  }
  for(let h=0;h<=24;h+=3){
    const x=dx(h);
    s+='<path d="M'+x.toFixed(1)+','+DY.bot+' v6" stroke="#3d444d" stroke-width="1"/>'
      +txt(x,DY.bot+20,(h<10?'0':'')+h+':00',{anchor:'middle',fs:10.5});
  }
  let p='';
  for(let h=0;h<=24;h+=0.25) p+=(h?'L':'M')+dx(h).toFixed(1)+','+dy(dayT(h)).toFixed(1);
  s+='<path d="'+p+'" fill="none" stroke="#31d67a" stroke-width="2.4"/>';
  // the two cut-offs, each pinned to the hour it was measured for
  [[6,D.day.cut_am,'fever above this at 06:00'],
   [16,D.day.cut_pm,'fever above this at 16:00']].forEach(([h,c,lab])=>{
    const x=dx(h), y=dy(c);
    s+='<path d="M'+(x-70)+','+y.toFixed(1)+' h140" stroke="#f0a04b" stroke-width="1.4" stroke-dasharray="4 3"/>'
      +txt(x,y-8,lab+' · '+fmt(c),{anchor:'middle',fill:'#f0a04b',fs:11,stroke:1});
  });
  [[D.day.nadir,'the daily low'],[18,'the daily high']].forEach(([h,lab])=>{
    const x=dx(h), y=dy(dayT(h));
    s+='<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="4" fill="#31d67a"/>'
      +txt(x,y+(h<12?20:-12),lab+' · '+fmt(dayT(h)),
           {anchor:'middle',fill:'#8b93a0',fs:11,stroke:1});
  });
  // the swing, drawn as the bar it is
  const yl=dy(dayT(D.day.nadir)), yh=dy(dayT(18));
  s+='<path d="M'+(DY.x1+14)+','+yh.toFixed(1)+' V'+yl.toFixed(1)
    +'" stroke="#31d67a" stroke-width="2"/>'
    +txt(DY.x1+14,yh-10,gap(D.day.amp*2),{anchor:'end',fs:11,fill:'#8b93a0'})
    +txt(DY.x1+14,yl+18,'the whole swing',{anchor:'end',fs:11,fill:'#8b93a0'});
  for(let h=0;h<24;h++){
    s+='<g data-h="'+h+'" style="cursor:pointer"><rect x="'+(dx(h)-16)+'" y="'+DY.top
      +'" width="32" height="'+(DY.bot-DY.top)+'" fill="transparent"/>'
      +'<circle cx="'+dx(h).toFixed(1)+'" cy="'+dy(dayT(h)).toFixed(1)+'" r="'
      +(hot&&hot.t==='h'&&hot.i===h?5:2.2)+'" fill="#31d67a"/></g>';
  }
  s+=txt(80,DY.top-24,'one day, in oral readings from healthy young adults',
         {fs:11.5,fill:'#8b93a0'});
  el.innerHTML=svg(520,s);
}

/* ------------------------------------------------------- where it is taken */
const SI={x0:260,x1:930,lo:35.1,hi:38.1,top:90,rowh:64};
function sx(c){ return SI.x0+(c-SI.lo)/(SI.hi-SI.lo)*(SI.x1-SI.x0); }
function drawSites(){
  let s='';
  const bot=SI.top+D.sites.length*SI.rowh+18;
  for(let c=35.5;c<=38.0;c+=0.5){
    const x=sx(c);
    s+='<path d="M'+x.toFixed(1)+','+(SI.top-14)+' V'+bot+'" stroke="#242424" stroke-width="1"/>'
      +txt(x,bot+20,fmt(c,U==='K'?2:1),{anchor:'middle',fs:10.5});
  }
  D.sites.forEach((v,i)=>{
    const y=SI.top+i*SI.rowh+SI.rowh/2;
    const on=hot&&hot.t==='s'&&hot.i===i;
    s+='<g data-s="'+i+'" style="cursor:pointer">'
      +'<rect x="0" y="'+(y-SI.rowh/2)+'" width="'+W+'" height="'+SI.rowh
      +'" fill="#ffffff" fill-opacity="'+(on?0.045:(i%2?0:0.02))+'"/>'
      +'<path d="M'+sx(v.lo).toFixed(1)+','+y+' H'+sx(v.hi).toFixed(1)
      +'" stroke="#58a6ff" stroke-width="'+(on?9:7)+'" stroke-opacity="0.3" stroke-linecap="round"/>'
      +'<circle cx="'+sx(v.m).toFixed(1)+'" cy="'+y+'" r="'+(on?6:4.5)+'" fill="#58a6ff"/>'
      +txt(SI.x0-18,y+4.6,esc(v.n),{anchor:'end',fs:13.5,fill:on?'#e6e6e6':'#c8ccd2'})
      +txt(sx(v.m),y-16,fmt(v.m,2),{anchor:'middle',fs:11.5,fill:'#8b93a0',stroke:1})
      +txt(sx(v.hi)+14,y+4,'from '+v.k+' studies',{fs:10.5})
      +'</g>';
  });
  // how far a forehead or ear reading can sit from a central one
  const y2=bot+58, cx=sx(36.6);
  s+='<g data-p="1" style="cursor:pointer">'
    +'<rect x="0" y="'+(y2-30)+'" width="'+W+'" height="60" fill="transparent"/>'
    +'<path d="M'+(cx+(sx(36.6+D.per.lo)-cx)).toFixed(1)+','+y2+' H'
    +(cx+(sx(36.6+D.per.hi)-cx)).toFixed(1)
    +'" stroke="#e0673f" stroke-width="7" stroke-opacity="0.35" stroke-linecap="round"/>'
    +'<circle cx="'+cx.toFixed(1)+'" cy="'+y2+'" r="4" fill="#e0673f"/>'
    +txt(SI.x0-18,y2+4.6,'A peripheral reading',{anchor:'end',fs:13.5,fill:'#c8ccd2'})
    +txt(cx,y2-16,'can sit anywhere in here, against a central one',
         {anchor:'middle',fs:11,fill:'#e0673f',stroke:1})
    +'</g>';
  s+=txt(80,SI.top-40,'the mean at each site, and the mean give or take two '
        +'standard deviations',{fs:11.5,fill:'#8b93a0'});
  el.innerHTML=svg(y2+56,s);
}

/* ----------------------------------------------------------------- fever */
const FV={x0:150,x1:940,lo:36.2,hi:41.9};
function fx(h){ return FV.x0+h/D.fever.hours*(FV.x1-FV.x0); }
function panel(top,h){
  return {top:top, bot:top+h,
    y:c=>top+h-(c-FV.lo)/(FV.hi-FV.lo)*h};
}
// the set point steps up, holds, and steps back down
function setPoint(h){
  const f=D.fever;
  if(h<f.rise) return f.base;
  if(h<f.rise+1) return f.base+(f.peak-f.base)*(h-f.rise);
  if(h<f.plateau_end) return f.peak;
  if(h<f.plateau_end+2) return f.peak-(f.peak-f.base)*(h-f.plateau_end)/2;
  return f.base;
}
// core chases it, and never quite gets there first
function coreT(h){
  const f=D.fever;
  if(h<f.rise) return f.base;
  if(h<6) return f.base+(f.peak-f.base)*(h-f.rise)/4;
  if(h<f.plateau_end) return f.peak;
  if(h<f.fall_end) return f.peak-(f.peak-f.base)*(h-f.plateau_end)/(f.fall_end-f.plateau_end);
  return f.base;
}
function illT(h){
  const b=D.ill.base, p=D.ill.peak;
  // nothing turns it around on its own: past the plateau it still creeps up
  return h<1 ? b : h<9 ? b+(p-b)*(h-1)/8 : Math.min(42.4,p+(h-9)*0.02);
}
function drawFever(){
  const A=panel(88,222), B=panel(384,222);
  let s='';
  [[A,'Fever: the target moves, and the body chases it',56],
   [B,'Hyperthermia: the target never moves, and control loses',16]]
   .forEach(([P,lab,up])=>{
    for(let c=37;c<=41;c++){
      const y=P.y(c);
      s+='<path d="M'+FV.x0+','+y.toFixed(1)+' H'+FV.x1+'" stroke="#242424" stroke-width="1"/>'
        +txt(FV.x0-10,y+3.6,fmt(c,U==='K'?2:0),{anchor:'end'});
    }
    s+=txt(80,P.top-up,lab,{fs:11.5,fill:'#c8ccd2'});
  });
  for(let h=0;h<=D.fever.hours;h+=6){
    s+='<path d="M'+fx(h).toFixed(1)+','+B.bot+' v6" stroke="#3d444d" stroke-width="1"/>'
      +txt(fx(h),B.bot+20,h+' h',{anchor:'middle',fs:10.5});
  }
  // the gap between target and core is what the person feels: cold while
  // core is under the target, hot while it is over
  function band(cold){
    let a='', b='', out='';
    for(let h=0;h<=D.fever.hours;h+=0.2){
      const c=coreT(h), sp=setPoint(h), inside=cold?(sp-c>0.02):(c-sp>0.02);
      if(inside){
        a+=(a?'L':'M')+fx(h).toFixed(1)+','+A.y(c).toFixed(1);
        b=('L'+fx(h).toFixed(1)+','+A.y(sp).toFixed(1))+b;
      } else if(a){ out+='<path d="'+a+b+'Z" fill="'+(cold?'#4a87d6':'#e0673f')
        +'" fill-opacity="0.2"/>'; a=''; b=''; }
    }
    if(a) out+='<path d="'+a+b+'Z" fill="'+(cold?'#4a87d6':'#e0673f')
      +'" fill-opacity="0.2"/>';
    return out;
  }
  s+=band(true)+band(false);
  let ps='', pc='', pi='';
  for(let h=0;h<=D.fever.hours;h+=0.2){
    ps+=(ps?'L':'M')+fx(h).toFixed(1)+','+A.y(setPoint(h)).toFixed(1);
    pc+=(pc?'L':'M')+fx(h).toFixed(1)+','+A.y(coreT(h)).toFixed(1);
    pi+=(pi?'L':'M')+fx(h).toFixed(1)+','+B.y(illT(h)).toFixed(1);
  }
  s+='<path d="'+ps+'" fill="none" stroke="#ffd24d" stroke-width="2" stroke-dasharray="6 4"/>'
    +'<path d="'+pc+'" fill="none" stroke="#e0673f" stroke-width="2.4"/>'
    +txt(fx(D.fever.hours)-6,A.y(D.fever.peak)-10,'the set point',
         {anchor:'end',fill:'#ffd24d',fs:11,stroke:1})
    +txt(fx(D.fever.hours)-6,A.y(D.fever.base)-10,'core',
         {anchor:'end',fill:'#e0673f',fs:11,stroke:1});
  // hyperthermia: a flat target and a core that climbs past it anyway
  s+='<path d="M'+FV.x0+','+B.y(D.ill.base).toFixed(1)+' H'+FV.x1
    +'" stroke="#ffd24d" stroke-width="2" stroke-dasharray="6 4"/>'
    +'<path d="'+pi+'" fill="none" stroke="#c02f2f" stroke-width="2.4"/>'
    +'<g data-i="1" style="cursor:pointer"><rect x="'+FV.x0+'" y="'+B.top
    +'" width="'+(FV.x1-FV.x0)+'" height="'+(B.bot-B.top)+'" fill="transparent"/></g>'
    +txt(fx(D.fever.hours)-6,B.y(D.ill.base)-10,'the set point, unmoved',
         {anchor:'end',fill:'#ffd24d',fs:11,stroke:1})
    +'<path d="M'+FV.x0+','+B.y(40).toFixed(1)+' H'+FV.x1
    +'" stroke="#c02f2f" stroke-width="1.2" stroke-dasharray="4 3" stroke-opacity="0.7"/>'
    +txt(FV.x0+8,B.y(40)-7,'heat stroke, with the nervous system failing',
         {fill:'#c02f2f',fs:11,stroke:1});
  // the four phases, hung along the top of the fever panel
  D.fever.phases.forEach((p,i)=>{
    const [a,b,n]=p, x=(fx(a)+fx(b))/2;
    const on=hot&&hot.t==='f'&&hot.i===i;
    s+='<g data-f="'+i+'" style="cursor:pointer">'
      +'<rect x="'+fx(a).toFixed(1)+'" y="'+A.top+'" width="'+(fx(b)-fx(a)).toFixed(1)
      +'" height="'+(A.bot-A.top)+'" fill="#ffffff" fill-opacity="'+(on?0.05:0)+'"/>'
      +'<path d="M'+fx(a).toFixed(1)+','+(A.top-6)+' V'+A.bot+'" stroke="#2b2b2b" stroke-width="1"/>'
      +txt(x,A.top-(i%2?38:24),esc(n),{anchor:'middle',fs:11,
           fill:on?'#e6e6e6':'#8b93a0',stroke:1})
      +'</g>';
  });
  el.innerHTML=svg(B.bot+52,s);
}

/* --------------------------------------------------------- heat in and out */
function drawHeat(){
  const P=D.power;
  let s='', x0=150, x1=930;
  // what it leaves by, at rest
  let x=x0, y=96;
  D.routes.forEach((r,i)=>{
    const w=(x1-x0)*r.p/100, on=hot&&hot.t==='r'&&hot.i===i;
    s+='<g data-r="'+i+'" style="cursor:pointer">'
      +'<rect x="'+x.toFixed(1)+'" y="'+y+'" width="'+w.toFixed(1)+'" height="46" fill="'
      +r.c+'" fill-opacity="'+(on?1:0.78)+'"/>'
      +txt(x+w/2,y+28,r.p+'%',{anchor:'middle',fs:14,fill:'#101010',w:600})
      +txt(x+w/2,y+64,esc(r.n),{anchor:'middle',fs:11.5,
           fill:on?'#e6e6e6':'#8b93a0'})+'</g>';
    x+=w;
  });
  s+=txt(x0,y-14,'How the heat leaves, in a room at rest',{fs:11.5,fill:'#c8ccd2'})
    +txt(x1,y-14,'the classic textbook split, for a nude adult in still air',
         {anchor:'end',fs:10.5});
  // how much heat there is to shift
  const sy=262, sc=(x1-x0)/P.peak;
  s+=txt(x0,sy-30,'How much heat there is to shift, in watts',{fs:11.5,fill:'#c8ccd2'});
  [['rest','At rest',P.rest,'#31d67a'],
   ['hard','Up a mountain on a bike',P.hard,'#e0673f'],
   ['peak','At the highest effort ever measured',P.peak,'#c02f2f'],
   ['evap','What two litres of sweat an hour can carry off',
    Math.round(2*P.evap_w_per_lh),'#58a6ff']]
   .forEach(([k,lab,w,c],i)=>{
    const yy=sy+i*54, on=hot&&hot.t==='w'&&hot.i===i;
    s+='<g data-w="'+i+'" style="cursor:pointer">'
      +'<rect x="0" y="'+(yy-10)+'" width="'+W+'" height="48" fill="#ffffff" fill-opacity="'
      +(on?0.045:0)+'"/>'
      +'<rect x="'+x0+'" y="'+yy+'" width="'+(w*sc).toFixed(1)+'" height="18" fill="'+c
      +'" fill-opacity="'+(k==='evap'?0.45:0.85)+'"'
      +(k==='evap'?' stroke="#58a6ff" stroke-dasharray="4 3"':'')+'/>'
      +txt(x0+w*sc+10,yy+14,w.toLocaleString('en-US')+' W',{fs:12.5,fill:'#c8ccd2'})
      +txt(x0,yy-6,esc(lab),{fs:11,fill:on?'#e6e6e6':'#8b93a0'})+'</g>';
  });
  // and the direction the dry routes run, which depends on the room
  const hy=sy+4*54+34;
  [[false,'Cooler than the skin','#4a87d6','out'],
   [true,'Hotter than the skin','#e0673f','in']].forEach(([warm,lab,c,dir],i)=>{
    const cx=x0+140+i*380, on=hot&&hot.t==='x'&&hot.i===i;
    s+='<g data-x="'+i+'" style="cursor:pointer">'
      +'<rect x="'+(cx-150)+'" y="'+(hy-14)+'" width="300" height="132" fill="#ffffff" fill-opacity="'
      +(on?0.045:0.02)+'" rx="8"/>'
      +'<circle cx="'+cx+'" cy="'+(hy+30)+'" r="17" fill="none" stroke="#8b93a0" stroke-width="1.4"/>';
    for(let a=0;a<8;a++){
      const th=a*Math.PI/4, r0=dir==='out'?22:52, r1=dir==='out'?46:26;
      const X0=cx+Math.cos(th)*r0, Y0=hy+30+Math.sin(th)*r0;
      const X1=cx+Math.cos(th)*r1, Y1=hy+30+Math.sin(th)*r1;
      // an arrowhead at the far end, so the direction is on the picture
      const ux=(X1-X0)/Math.hypot(X1-X0,Y1-Y0), uy=(Y1-Y0)/Math.hypot(X1-X0,Y1-Y0);
      const px=-uy*3.4, py=ux*3.4;
      s+='<path d="M'+X0.toFixed(1)+','+Y0.toFixed(1)+' L'+X1.toFixed(1)+','+Y1.toFixed(1)
        +'" stroke="'+c+'" stroke-width="1.6" stroke-opacity="0.85"/>'
        +'<path d="M'+X1.toFixed(1)+','+Y1.toFixed(1)
        +' L'+(X1-ux*7+px).toFixed(1)+','+(Y1-uy*7+py).toFixed(1)
        +' L'+(X1-ux*7-px).toFixed(1)+','+(Y1-uy*7-py).toFixed(1)
        +'Z" fill="'+c+'" fill-opacity="0.85"/>';
    }
    s+=txt(cx,hy+92,esc(lab),{anchor:'middle',fs:11.5,fill:on?'#e6e6e6':'#8b93a0'})
      +txt(cx,hy+108,dir==='out'?'heat leaves':'heat arrives',
           {anchor:'middle',fs:10.5,fill:c})+'</g>';
  });
  s+=txt(x0,hy-24,'Which way radiation and convection run',{fs:11.5,fill:'#c8ccd2'});
  el.innerHTML=svg(hy+140,s);
}

/* --------------------------------------------------------------- plumbing */
const DRAW={range:drawRange, day:drawDay, site:drawSites, fever:drawFever,
            heat:drawHeat};
const INTRO={
  range:['The whole span','From the coldest anyone has been rewarmed from to '
    +'the hottest anyone has walked away from. The band the body actually '
    +'holds is the green sliver in the middle.'],
  day:['A day','Core temperature is lowest a couple of hours before waking '
    +'and highest in the late afternoon. The whole swing is about half a '
    +'degree, which is why the hour matters when a reading is judged.'],
  site:['Where it is taken','Four everyday sites, from a meta-analysis of '
    +'7,636 healthy adults. They disagree by more than a degree between the '
    +'rectum and the armpit, which is more than the daily swing.'],
  fever:['Fever','Above, a fever: the set point moves and the body chases it. '
    +'Below, hyperthermia: the set point stays put and heat wins anyway. The '
    +'two look alike on a thermometer and are opposite underneath.'],
  heat:['Heat in, heat out','About a hundred watts at rest, and fourteen '
    +'times that climbing a mountain on a bicycle. Sweat is the only route '
    +'that still works once the room is hotter than the skin.'],
};
function render(){
  DRAW[view]();
  if(!hot){ const [n,b]=INTRO[view]; card('',n,'',b); }
}
function setView(v){
  view=v; hot=null;
  for(const [id,k] of [['vRange','range'],['vDay','day'],['vSite','site'],
                       ['vFever','fever'],['vHeat','heat']])
    document.getElementById(id).classList.toggle('on',v===k);
  render();
}
function setUnit(u){
  U=u; hot=null;
  for(const [id,k] of [['uC','C'],['uF','F'],['uK','K']])
    document.getElementById(id).classList.toggle('on',u===k);
  DRAW[view]();
  const sc=D.scales[u];
  // 37 converts to a terminating figure in each of the three
  card('The scale',sc.n,'body: '+fmt(37,u==='K'?2:1)
    +' · a rise of one degree Celsius: '+gap(1),sc.b);
}
for(const [id,k] of [['vRange','range'],['vDay','day'],['vSite','site'],
                     ['vFever','fever'],['vHeat','heat']])
  document.getElementById(id).onclick=()=>setView(k);
for(const [id,k] of [['uC','C'],['uF','F'],['uK','K']])
  document.getElementById(id).onclick=()=>setUnit(k);

el.addEventListener('pointerover',ev=>{
  const g=ev.target.closest('[data-z],[data-m],[data-h],[data-s],[data-p],'
    +'[data-f],[data-i],[data-r],[data-w],[data-x]');
  if(!g) return;
  const P=D.power;
  const pick=(a,t)=>{ hot={t:t,i:+g.getAttribute(a)}; };
  if(g.hasAttribute('data-z')){
    pick('data-z','z'); const z=D.zones[hot.i];
    card('A band of the span',z.n,fmt(z.lo)+' to '+fmt(z.hi),z.b); tint(z.c);
  } else if(g.hasAttribute('data-m')){
    pick('data-m','m'); const m=D.marks[hot.i];
    card('A mark on the column',m.n,fmt(m.t),m.b);
  } else if(g.hasAttribute('data-h')){
    pick('data-h','h'); const h=hot.i, t=dayT(h);
    card('One hour of the day',(h<10?'0':'')+h+':00',fmt(t),
      'The curve is a half-degree swing around a mean of '+fmt(D.day.mean)
      +'. Judged against the morning cut-off of '+fmt(D.day.cut_am)
      +' this hour reads '+(t>D.day.cut_am?'high':'normal')
      +'; against the afternoon cut-off of '+fmt(D.day.cut_pm)+' it reads normal.');
  } else if(g.hasAttribute('data-s')){
    pick('data-s','s'); const v=D.sites[hot.i];
    card('A place to put the thermometer',v.n,
      fmt(v.m)+' · '+fmt(v.lo)+' to '+fmt(v.hi),v.b);
  } else if(g.hasAttribute('data-p')){
    hot={t:'p',i:0};
    card('Forehead, ear and the rest','A peripheral reading',
      gap(D.per.lo)+' to +'+gap(D.per.hi)+' against a central one',
      'Pooled across studies, a peripheral thermometer sits anywhere in that '
      +'range against a central one. It catches only '+D.per.sens
      +' percent of fevers, though it rarely calls one that is not there: '
      +D.per.spec+' percent specificity. Forehead scanners are worse still, '
      +'missing about half the fevers in adults.');
  } else if(g.hasAttribute('data-f')){
    pick('data-f','f'); const p=D.fever.phases[hot.i];
    card('A phase of the fever',p[2],'hour '+p[0]+' to '+p[1],p[3]);
  } else if(g.hasAttribute('data-i')){
    hot={t:'i',i:0};
    card('The other way up','Hyperthermia',
      fmt(D.ill.base)+' to '+fmt(D.ill.peak)+', with the set point unmoved',
      D.ill.note);
  } else if(g.hasAttribute('data-r')){
    pick('data-r','r'); const r=D.routes[hot.i];
    card('A route out',r.n,r.p+' percent of the heat lost at rest',r.b);
    tint(r.c);
  } else if(g.hasAttribute('data-w')){
    pick('data-w','w');
    const B=[['At rest',P.rest,'About the draw of an old filament bulb. Every '
        +'watt of it has to leave, or the temperature climbs.'],
      ['Up a mountain on a bike',P.hard,'A 70 kilogram rider on a sustained '
        +'climb makes about this much heat, because only a fifth to a quarter '
        +'of the energy burned becomes movement and the rest is waste heat.'],
      ['At the highest effort ever measured',P.peak,'Twenty-five times the '
        +'resting output. Nothing sheds heat that fast for long, which is why '
        +'efforts like this are short.'],
      ['What sweat can carry off',Math.round(2*P.evap_w_per_lh),
        'Evaporating a litre of sweat takes about '+P.latent+' kilojoules, so '
        +'two litres an hour carries off around '+Math.round(2*P.evap_w_per_lh)
        +' watts. Only evaporated sweat counts. Sweat that drips off has cost '
        +'the body water and bought it nothing, which is why humid heat is '
        +'more dangerous than dry heat at the same temperature.']][hot.i];
    card('Watts',B[0],B[1].toLocaleString('en-US')+' W',B[2]);
  } else if(g.hasAttribute('data-x')){
    pick('data-x','x');
    card('Which way the heat runs',hot.i?'Hotter than the skin':'Cooler than the skin',
      hot.i?'above about '+fmt(P.skin):'below about '+fmt(P.skin),
      hot.i?'Radiation and convection reverse. The room is now heating the '
        +'body, and evaporation is the only route left, which is why still, '
        +'humid air is the dangerous combination.'
        :'Radiation and convection carry heat away from the skin, and do most '
        +'of the work at rest.');
  }
  render();
});

setUnit('C'); setView('range');
window.__temp=()=>({view, unit:U,
  zones:D.zones.length, marks:D.marks.length, sites:D.sites.length,
  routes:D.routes.length, routeSum:D.routes.reduce((a,r)=>a+r.p,0),
  zonesJoin:D.zones.every((z,i)=>!i||Math.abs(z.lo-D.zones[i-1].hi)<1e-9),
  span:[D.zones[0].lo,D.zones[D.zones.length-1].hi],
  nodes:document.querySelectorAll('#tsvg [data-z],#tsvg [data-m],#tsvg [data-h],'
    +'#tsvg [data-s],#tsvg [data-f],#tsvg [data-r],#tsvg [data-w],'
    +'#tsvg [data-x]').length,
  at37:fmt(37), rise1:gap(1),
  dayLow:dayT(D.day.nadir), dayHigh:dayT(18),
  chase:coreT(4)<setPoint(4), caught:Math.abs(coreT(10)-setPoint(10))<0.01,
  shed:coreT(16)>setPoint(16)});
</script>
</body>
</html>
"""


def main():
    A = apa.article
    refs = [
        (A("Geneva, I. I., Cuzzo, B., Fazili, T., &amp; Javaid, W.", 2019,
           "Normal body temperature: A systematic review",
           "Open Forum Infectious Diseases", 6, 4, "ofz032",
           "https://doi.org/10.1093/ofid/ofz032"),
         "The mean and the normal range at each site, from 7,636 healthy "
         "adults, and the spread drawn on the sites view."),
        (A("Mackowiak, P. A., Wasserman, S. S., &amp; Levine, M. M.", 1992,
           "A critical appraisal of 98.6 degrees F, the upper limit of the "
           "normal body temperature, and other legacies of Carl Reinhold "
           "August Wunderlich", "JAMA", 268, 12, "1578-1580",
           "https://doi.org/10.1001/jama.1992.03490120092034"),
         "The daily swing, the two time-of-day fever cut-offs, and the case "
         "against 98.6."),
        (A("Obermeyer, Z., Samra, J. K., &amp; Mullainathan, S.", 2017,
           "Individual differences in normal body temperature: Longitudinal "
           "big data analysis of patient records", "BMJ", 359, None, "j5468",
           "https://doi.org/10.1136/bmj.j5468"),
         "The modern mean of 36.6 degrees, from 243,506 measurements."),
        (A("Protsiv, M., Ley, C., Lankester, J., Hastie, T., &amp; "
           "Parsonnet, J.", 2020,
           "Decreasing human body temperature in the United States since the "
           "Industrial Revolution", "eLife", 9, None, "e49555",
           "https://doi.org/10.7554/eLife.49555"),
         "The claim that the mean has fallen, and the caution on the sites "
         "the older readings were taken from."),
        (A("Niven, D. J., Gaudet, J. E., Laupland, K. B., Mrklas, K. J., "
           "Roberts, D. J., &amp; Stelfox, H. T.", 2015,
           "Accuracy of peripheral thermometers for estimating temperature: "
           "A systematic review and meta-analysis",
           "Annals of Internal Medicine", 163, 10, "768-777",
           "https://doi.org/10.7326/M15-1150"),
         "How far a peripheral thermometer can sit from a central one, and "
         "how many fevers it misses."),
        (A("Blomqvist, A., &amp; Engblom, D.", 2018,
           "Neural mechanisms of inflammation-induced fever",
           "The Neuroscientist", 24, 4, "381-399",
           "https://doi.org/10.1177/1073858418760481"),
         "The set point, the prostaglandin that moves it, and the route from "
         "the preoptic hypothalamus to shivering."),
        (A("Brown, D. J. A., Brugger, H., Boyd, J., &amp; Paal, P.", 2012,
           "Accidental hypothermia", "The New England Journal of Medicine",
           367, 20, "1930-1938", "https://doi.org/10.1056/NEJMra1114208"),
         "The hypothermia bands on the column, and what happens in each."),
        (A("Mroczek, T., Gladki, M., &amp; Skalski, J.", 2020,
           "Successful resuscitation from accidental hypothermia of 11.8 "
           "degrees C: Where is the lower bound for human beings?",
           "European Journal of Cardio-Thoracic Surgery", 58, 5, "1091-1092",
           "https://doi.org/10.1093/ejcts/ezaa159"),
         "The coldest survival on record, and the case behind it."),
        (A("Bouchama, A., &amp; Knochel, J. P.", 2002, "Heat stroke",
           "The New England Journal of Medicine", 346, 25, "1978-1988",
           "https://doi.org/10.1056/NEJMra011089"),
         "The heat stroke threshold, the difference between fever and "
         "hyperthermia, and the temperature at which proteins give way."),
        (A("Periard, J. D., Eijsvogels, T. M. H., &amp; Daanen, H. A. M.",
           2021, "Exercise under heat stress: Thermoregulation, hydration, "
           "performance implications, and mitigation strategies",
           "Physiological Reviews", 101, 4, "1873-1979",
           "https://doi.org/10.1152/physrev.00038.2020"),
         "The heat a hard effort makes, and the point above which the dry "
         "routes start adding heat instead of removing it."),
        (apa.book("Hall, J. E., &amp; Hall, M. E.", 2020,
                  "Guyton and Hall textbook of medical physiology (14th ed.)",
                  "Elsevier"),
         "The classic split between radiation, convection, conduction and "
         "evaporation, and the latent heat of sweat."),
        (apa.web("National Institute of Standards and Technology", 2019,
                 "Kelvin: Present realization", "NIST",
                 "https://www.nist.gov/si-redefinition/kelvin/kelvin-present-realization"),
         "The 2019 definition of the kelvin, by a fixed Boltzmann constant."),
        (apa.wiki("https://en.wikipedia.org/wiki/Anna_B%C3%A5genholm"),
         "The Bagenholm case, the best known adult survival from deep "
         "hypothermia."),
        (apa.web("Guinness World Records", None,
                 "Highest body temperature", "Guinness World Records",
                 "https://www.guinnessworldrecords.com/world-records/67749-highest-body-temperature"),
         "The hottest survival on record. It is a record listing rather than "
         "a published case report, and the page says so."),
    ]
    html = (HTML.replace("__APACSS__", apa.CSS)
            .replace("__DATA__", DATA)
            .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2)
            .replace("__REFS__", apa.render(refs)))
    out = ROOT / "temperature.html"
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({len(html):,} B): {len(D.ZONES)} bands, "
          f"{len(D.MARKS)} marks, {len(D.SITES)} sites, "
          f"{len(D.ROUTES)} routes, {len(refs)} references")


if __name__ == "__main__":
    main()
