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
    cost=D.COST,
    lines=[dict(t=t, n=n, c=c, b=b) for t, n, c, b in D.LINES],
    fine=[dict(lo=a, hi=b, n=n, c=c, b=t) for a, b, n, c, t in D.FINE],
    unresp=D.UNRESPONSIVE,
    cooling=[dict(n=n, r=r, c=c, e=e, b=b) for n, r, c, e, b in D.COOLING],
    coolfrom=D.COOL_FROM, coolto=D.COOL_TO, cooltarget=D.COOL_TARGET,
    actions=[dict(n=n, c=c, b=b) for n, c, b in D.ACTIONS],
    tell=[dict(k=k, f=f, h=h) for k, f, h in D.TELL],
    tellnote=D.TELL_NOTE,
    measured=[dict(t=t, p=pc, s=k, a=aw) for t, pc, k, aw in D.MEASURED],
    msrc={k: dict(n=n, b=b) for k, (n, b) in D.MSRC.items()},
    regimes=[dict(lo=a, hi=b, n=n, c=c, b=t) for a, b, n, c, t in D.REGIMES],
    hrcold=D.HR_COLD,
)


NOTE1 = ("Seven views on one column of degrees. The span is everything a "
         "person has been brought back from, at either end. The day is the "
         "half degree the body actually moves through, and the sites "
         "disagree by more than that. Fever sets a target the body chases, "
         "which is why the chill comes first; hyperthermia moves no target "
         "and is control losing to heat. The last two views run degree by "
         "degree, and then ask what the number does not decide.")

NOTE2 = ("The buttons set the scale and everything moves with it: the "
         "ladder, the marks, the table, and the temperatures written into "
         "the sentences. A point on the scale and a gap between two points "
         "still convert differently, which is why a body at 37 degrees "
         "Celsius is 98.6 Fahrenheit while a rise of one Celsius degree is "
         "1.8 Fahrenheit degrees and exactly one kelvin. The collapse view "
         "follows published guidance and does not replace the emergency "
         "number, which is the first call.")

METHOD = ("What the collapse view rests on, and where it is soft. There is no "
          "randomised trial of any cooling method in human heat stroke with "
          "survival as the endpoint, and there will not be. Every figure "
          "here comes either from laboratory heating of healthy volunteers, "
          "which is not heat stroke, or from uncontrolled case series in "
          "which the treatment was never withheld. The reviewers who grade "
          "this literature call their own strongest cooling recommendation "
          "certain in direction and very low in certainty of evidence, and "
          "the page follows them. Three specifics are worth naming. The "
          "cooling rates for pouring and fanning come from the sports "
          "medicine literature at about half the rate of immersion; a formal "
          "review of the same studies could not tell that method apart from "
          "doing nothing, and both numbers sit in current guidelines. The "
          "stopping point of {38.6} has direct experimental support "
          "from ten volunteers, while authorities place the line anywhere "
          "from {38.0} to {39.4}. And the thirty minute target is an operational "
          "goal grounded in observational series and physiology, not a "
          "measured cliff: no validated model turns a person's temperature "
          "and the time they spent there into a probability. The series "
          "reporting no deaths after fast cooling are drawn from finish line "
          "medical tents and military bases, where the patients were young "
          "and the collapse was witnessed, so they do not transfer to an "
          "elderly person found at home. Whether immersion suits that person "
          "at all is genuinely unresolved: one guideline treats both kinds of "
          "heat stroke the same, one review found immersion poorly tolerated "
          "in the classic form, and a third makes no recommendation. No "
          "guideline body tells a lay rescuer what to do about the airway of "
          "an unresponsive person during immersion, so the line about the "
          "bathtub is a reading of the warnings rather than a quotation of "
          "one.")

MEASURED_NOTE = (
    "The points on the metabolic panel, and why they are points. No "
    "published figure covers this range, and drawing one would mean joining "
    "measurements that come from incompatible states: the shivering peak "
    "needs a person awake and defending their temperature, while everything "
    "below about 33 degrees was measured in someone anaesthetised, paralysed "
    "or on bypass, which is the only reason anyone has been that cold and "
    "measured. So the page plots the measurements and leaves the gaps "
    "empty. The studies, in order down the scale: Zhu (2003), twenty "
    "anaesthetised patients heated to {41.8}; Eyolfson and colleagues (2001, "
    "European Journal of Applied Physiology 84, 100 to 106) on peak "
    "shivering; Flickinger and colleagues (2023, Therapeutic Hypothermia and "
    "Temperature Management), nine sedated volunteers cooled to {33}; "
    "Sharabiani and colleagues (2025, Perfusion), 293 children on bypass; "
    "Hickey and colleagues (1983, Journal of Thoracic and Cardiovascular "
    "Surgery), twelve men at {25.4}; and Diop and colleagues (2024, Journal of "
    "Cardiothoracic and Vascular Anesthesia), twenty-four adults at {18}, the "
    "coldest whole-body measurement of a human there is. Below that there "
    "is nothing. The figures that circulate for 15 and 10 degrees descend "
    "from dogs cooled by Bigelow in 1950 by way of a 1983 review, and "
    "because the rate of change steepens as it gets colder they are "
    "probably too high. One more caution: the percentage-per-degree figures "
    "in this literature differ by a fifth depending on whether the "
    "denominator is the febrile value or the normal one, and this page uses "
    "the febrile one.")

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
.chartcol { flex:1 1 640px; min-width:0; }
#chart { min-width:0; }
/* the figure and the table, one axis, one row height */
#spanpair { display:flex; gap:0; align-items:flex-start; overflow-x:auto; }
#spanpair #chart { flex:0 0 var(--figw); }
#spanpair #chart svg { height:auto; }
/* the pair scrolls as one, so a narrow window never slides the table
   out of step with the figure */
#spanpair #degwrap { flex:1 1 auto; min-width:620px; overflow:visible; }
/* on the paired view the card rides above the pair and follows the
   reader down it, since the table is longer than a screen */
.stage.span { display:flex; flex-direction:column; }
.stage.span .side { order:-1; position:sticky; top:0; z-index:3; width:auto;
  flex:none; margin-bottom:12px; background:var(--bg); padding-bottom:6px; }
.stage.span .card { display:flex; gap:16px; align-items:baseline;
  flex-wrap:wrap; }
.stage.span #kindTxt { flex:0 0 auto; }
.stage.span #nameTxt { margin:0; }
.stage.span #bodyTxt { margin:0; flex:1 1 360px; min-width:0; }
.stage.span #realTxt, .stage.span #srcTxt { display:none; }
#degwrap { overflow-x:auto; }
#degrees { border-collapse:collapse; width:100%; font-size:11.5px;
  font-variant-numeric:tabular-nums; }
#degrees th { text-align:left; color:var(--muted); font-weight:400;
  font-size:11px; letter-spacing:.06em; text-transform:uppercase;
  height:34px; padding:0 10px 8px 0; vertical-align:bottom; }
#degrees tbody tr { height:var(--row,32px); }
#degrees thead tr { height:34px; }
#degrees td { padding:1px 10px 1px 0; border-top:1px solid #1e1e1e;
  vertical-align:middle; color:#b9bec6; line-height:1.25; font-size:11.5px; }
#degrees td.w { font-size:11.5px; line-height:1.25; }
#degrees td.w .cw { display:block; }
#degrees td.c { width:78px; }
#degrees td.z { width:124px; font-size:11.5px; }
#degrees td.n { width:86px; text-align:right; }
#degrees tr.key td { color:var(--text); }
#degrees td.c { font-weight:600; color:var(--text); white-space:nowrap; }
#degrees td.f, #degrees td.n { white-space:nowrap; }
#degrees td.z { white-space:nowrap; }
#degrees td.z i { width:8px; height:8px; border-radius:50%; display:inline-block;
  margin-right:6px; }
#degrees td.w { line-height:1.45; }
#degrees td.n.m { color:var(--text); }
#degrees td.n.b, #degrees td.n.n { color:#6b7280; }
#degrees tr:hover td { background:#191919; }
.tkey { color:var(--muted); font-size:11.5px; line-height:1.5; margin:10px 0 0;
  max-width:900px; }
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
.method { color:var(--muted); font-size:12.5px; margin-top:16px; max-width:760px; }
.method summary { cursor:pointer; color:var(--accent); }
.method p { margin:9px 0 0; }
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
  <button id="vFine">Degree by degree</button>
  <button id="vHelp">If someone collapses</button>
  <span class="sp"></span>
  <button id="uC" class="unit on">&deg;C</button>
  <button id="uF" class="unit">&deg;F</button>
  <button id="uK" class="unit">K</button>
</div>
<div class="stage">
  <div class="chartcol">
  <div id="spanpair"><div id="chart"></div><div id="degwrap"></div></div>
  </div>
  <div class="side"><div class="card">
    <div id="kindTxt"></div>
    <div id="nameTxt"></div>
    <div id="whenTxt"></div>
    <div id="bodyTxt"></div>
  </div></div>
</div>
<p class="note cv">__NOTE1__</p>
<p class="note cv" style="border-top:none; padding-top:0;">__NOTE2__</p>
<div class="method"><details><summary>The points on the metabolic panel, and why they are points</summary>
<p class="cv">__MEASURED__</p></details></div>
<div class="method"><details><summary>What the collapse view rests on, and where it is soft</summary>
<p class="cv">__METHOD__</p></details></div>
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
// kelvin needs the two places to say anything the others do not
function fmt(c,d){
  return toU(c).toFixed(d===undefined?(U==='K'?2:1):d)+SYM[U];
}
function gap(c,d){ return (U==='F'?c*9/5:c).toFixed(d===undefined?1:d)
  +(U==='K'?' K':SYM[U]); }
// Every temperature on the page, including the ones written into the
// sentences, is in the one scale the buttons choose. A number authored as
// {38.6} is a temperature; it converts, and keeps the precision it was
// written with, give or take what the unit needs.
function conv(s){
  return String(s).replace(/\{(\d+(?:\.\d+)?)\}/g,(_,n)=>{
    const d = U==='K' ? 2 : (n.indexOf('.')<0 ? (U==='F'?1:0) : 1);
    return fmt(parseFloat(n),d);
  });
}

function card(kind,name,when,body){
  const k=document.getElementById('kindTxt');
  k.textContent=conv(kind); k.style.color='var(--muted)';
  document.getElementById('nameTxt').textContent=conv(name);
  document.getElementById('whenTxt').innerHTML=conv(when||'');
  document.getElementById('bodyTxt').textContent=conv(body||'');
}
function tint(c){ document.getElementById('kindTxt').style.color=c; }

const W=1000, R=34, CELL=0.25;
function svg(h,inner){
  return '<svg viewBox="0 0 '+W+' '+h+'" xmlns="http://www.w3.org/2000/svg" id="tsvg">'
    +'<rect width="'+W+'" height="'+h+'" fill="#121212"/>'+inner+'</svg>';
}
function txt(x,y,s,o){
  o=o||{}; s=conv(s);
  return '<text x="'+x+'" y="'+y+'" font-size="'+(o.fs||11)+'"'
    +' fill="'+(o.fill||'#6b7280')+'"'
    +(o.anchor?' text-anchor="'+o.anchor+'"':'')
    +(o.w?' font-weight="'+o.w+'"':'')
    +(o.stroke?' stroke="#121212" stroke-width="2.6" paint-order="stroke"':'')
    +'>'+s+'</text>';
}

/* ---------------------------------------------------------- the whole span */
// The figure and the table are one drawing on one vertical axis. A degree
// is a row of the table and a slice of the body at the same height, so the
// eye runs across from a sentence to the place on a person it is about.
// Everything follows from ROW: the row height sets the axis, the axis sets
// the figure's height, and the figure's own proportions set its width. The
// table runs hot at the top, because the body does.
// The figure's box holds the axis and nothing else. Whatever height the
// table's header turns out to be is applied to the figure as a margin
// afterwards, measured rather than guessed, so the two never drift.
let ROW=32;                          // a floor; fitRows raises it
const DLO=10, DHI=48, NDEG=DHI-DLO+1;
const RG={lo:DLO-0.5, hi:DHI+0.5, top:0, bot:0, ladder:56};
let SPANW=0;
// the axis is whatever the rows turn out to be, and the figure is sized
// from it: as tall as the table, and as wide as a person that tall
function setAxis(){
  RG.bot=NDEG*ROW;
  RG.h=RG.bot-RG.top;
  // a figure this tall would be this wide, but past a point it would eat
  // the table's width, and a wider figure makes taller rows makes a taller
  // figure. The cap breaks that loop; the figure just gets slimmer.
  RG.hw=Math.min(RG.h/8.4,150);
  RG.sq=RG.hw/(RG.h/8.4);     // how much the cap slims the figure
  RG.cx=RG.ladder+RG.hw;
  SPANW=Math.round(RG.cx+RG.hw+6);
}
setAxis();
function yOf(c){ return RG.bot-(c-RG.lo)/(RG.hi-RG.lo)*RG.h; }

function halfProfile(){
  const H=RG.h, cx=RG.cx;
  const Y=f=>(RG.top+f*H).toFixed(1), X=d=>(cx+d*H*RG.sq).toFixed(1);
  const C=(a,b,c,d,e,f)=>'C'+X(a)+','+Y(b)+' '+X(c)+','+Y(d)+' '+X(e)+','+Y(f);
  return 'M'+X(0)+','+Y(.006)
    + C(.024,.006, .045,.014, .045,.044)          // skull
    + C(.045,.074, .034,.098, .026,.112)          // temple to jaw
    + C(.024,.120, .023,.126, .023,.138)          // neck
    + C(.050,.144, .084,.156, .092,.198)          // shoulder
    + C(.106,.256, .116,.368, .120,.470)          // outer arm
    + C(.122,.506, .108,.520, .098,.514)          // the hand
    + C(.090,.462, .082,.352, .076,.258)          // inner arm, to the armpit
    + C(.074,.300, .056,.360, .052,.406)          // chest to waist
    + C(.060,.436, .072,.446, .072,.468)          // hip
    + C(.072,.500, .070,.512, .070,.526)          // outer thigh
    + C(.066,.620, .054,.672, .052,.706)          // knee
    + C(.050,.762, .038,.878, .032,.944)          // calf to ankle
    + C(.031,.966, .040,.976, .040,.980)          // the foot
    + 'L'+X(.010)+','+Y(.984)
    + C(.010,.966, .014,.960, .014,.944)          // back up the inside
    + C(.020,.860, .026,.760, .026,.706)
    + C(.026,.640, .018,.580, .000,.530);         // to the crotch
}
function mirror(){ return 'translate('+(2*RG.cx)+',0) scale(-1,1)'; }
function bodyDefs(){
  const h=halfProfile();
  return '<defs><clipPath id="bodyClip" clipPathUnits="userSpaceOnUse">'
    +'<path d="'+h+'Z"/><path d="'+h+'Z" transform="'+mirror()+'"/>'
    +'</clipPath></defs>';
}
function bodyOutline(c,w){
  const h=halfProfile();
  return '<path d="'+h+'" fill="none" stroke="'+c+'" stroke-width="'+w
    +'" stroke-linejoin="round"/>'
    +'<path d="'+h+'" fill="none" stroke="'+c+'" stroke-width="'+w
    +'" stroke-linejoin="round" transform="'+mirror()+'"/>';
}

function drawRange(){
  const W0=RG.cx-RG.hw-8, W1=RG.cx+RG.hw+8;
  const ITEMS=D.marks.map((m,i)=>({t:m.t,k:'m',a:'data-m',i:i}))
    .concat(D.lines.map((L,i)=>({t:L.t,k:'L',a:'data-key',i:i,c:L.c}))
      .filter(L=>!D.marks.some(m=>Math.abs(m.t-L.t)<0.01)));
  let s=bodyDefs();
  s+='<g clip-path="url(#bodyClip)">';
  for(let i=0;i<D.zones.length;i++){
    const z=D.zones[i], y=yOf(z.hi), h=yOf(z.lo)-yOf(z.hi);
    s+='<rect x="'+W0+'" y="'+y.toFixed(1)+'" width="'+(W1-W0)
      +'" height="'+h.toFixed(1)+'" fill="'+z.c+'" fill-opacity="'
      +(hot&&hot.t==='z'&&hot.i===i?1:0.82)+'"/>';
  }
  ITEMS.forEach(it=>{
    const y=yOf(it.t), on=hot&&hot.t===it.k&&hot.i===it.i;
    s+='<path d="M'+W0+','+y.toFixed(1)+' H'+W1+'" stroke="'
      +(it.k==='L'?'#ffffff':'#121212')+'" stroke-width="'+(on?3:1.6)
      +'" stroke-opacity="'+(on?0.95:(it.k==='L'?0.4:0.5))+'"'
      +(it.k==='L'?' stroke-dasharray="4 3"':'')+'/>';
  });
  s+='</g>'+bodyOutline('#e6e6e6',1.6);
  // one hoverable slice of the figure per row of the table, so both halves
  // of the drawing answer to the same pointer
  s+='<g clip-path="url(#bodyClip)">';
  for(let d=DLO;d<=DHI;d++){
    const on=hot&&hot.t==='q'&&hot.i===d;
    s+='<g data-q="'+d+'" style="cursor:pointer"><rect x="'+W0+'" y="'
      +yOf(d+0.5).toFixed(1)+'" width="'+(W1-W0)+'" height="'+ROW
      +'" fill="#ffffff" fill-opacity="'+(on?0.3:0)+'"/></g>';
  }
  s+='</g>';
  // a rule at every degree boundary, carried out to the table's edge, so
  // the eye can see that a row and a slice are the same thing
  for(let d=DLO-1;d<=DHI;d++){
    const y=yOf(d+0.5);
    s+='<path d="M'+RG.ladder+','+y.toFixed(1)+' H'+SPANW
      +'" stroke="#1e1e1e" stroke-width="1"/>';
  }
  // the ladder, one rung per row, reading the degrees the table reads
  for(let d=DLO;d<=DHI;d++){
    const y=yOf(d), lab=(d%2===0)||d===37;
    s+='<path d="M'+(RG.ladder-(lab?9:4))+','+y.toFixed(1)+' H'+RG.ladder
      +'" stroke="#3d444d" stroke-width="1"/>';
    if(lab) s+=txt(RG.ladder-13,y+4,fmt(d,U==='C'?0:U==='K'?2:1),
                   {anchor:'end',fs:11});
  }
  // the marks, as a dot on the edge of the figure at their own height
  ITEMS.forEach(it=>{
    const on=hot&&hot.t===it.k&&hot.i===it.i;
    s+='<g '+it.a+'="'+it.i+'" style="cursor:pointer">'
      +'<circle cx="'+W0+'" cy="'+yOf(it.t).toFixed(1)+'" r="'+(on?5:3.4)
      +'" fill="'+(it.c||'#e6e6e6')+'"/>'
      +'<rect x="'+(W0-12)+'" y="'+(yOf(it.t)-11)+'" width="24" height="22"'
      +' fill="transparent"/></g>';
  });
  el.innerHTML='<svg viewBox="0 0 '+SPANW+' '+RG.bot
    +'" xmlns="http://www.w3.org/2000/svg" id="tsvg" '
    +'preserveAspectRatio="xMinYMin meet">'
    +'<rect width="'+SPANW+'" height="'+RG.bot+'" fill="#121212"/>'
    +s+'</svg>';
}

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


/* ------------------------------------------------------- degree by degree */
const FN={lo:36,hi:43,x0:150,x1:930};
function nx(c){ return FN.x0+(c-FN.lo)/(FN.hi-FN.lo)*(FN.x1-FN.x0); }
function nc(x){ return FN.lo+(x-FN.x0)/(FN.x1-FN.x0)*(FN.hi-FN.lo); }
function metPct(c,k){ return 100+(c-D.cost.base)*(k||D.cost.met); }
function bpm(c,k){ return D.cost.hr_base+(c-D.cost.base)*(k||D.cost.hr); }

// the ladder, in both units at once
function ladder(yTop,yBot){
  let s='';
  for(let c=36;c<=43;c+=0.5){
    const x=nx(c), big=Math.abs(c-Math.round(c))<0.01;
    s+='<path d="M'+x.toFixed(1)+','+(yTop-(big?8:4))+' V'+yTop
      +'" stroke="#3d444d" stroke-width="1"/>';
    if(big) s+=txt(x,yTop-13,c.toFixed(0)+'°C',{anchor:'middle',fs:10.5,
                   fill:'#8b93a0'});
  }
  for(let f=97;f<=109;f++){
    const c=(f-32)*5/9;
    if(c<FN.lo||c>FN.hi) continue;
    const x=nx(c);
    s+='<path d="M'+x.toFixed(1)+','+yBot+' v'+(f%2?4:8)+'" stroke="#3d444d" stroke-width="1"/>';
    if(f%2===1) s+=txt(x,yBot+22,f+'°F',{anchor:'middle',fs:10.5,fill:'#8b93a0'});
  }
  return s;
}
// the four lines that matter, staggered so their labels do not touch
function keyLines(yTop,yBot){
  let s='';
  D.lines.forEach((L,i)=>{
    const x=nx(L.t), up=yTop-(i%2?88:56);
    const on=hot&&hot.t==='L'&&hot.i===i;
    s+='<g data-key="'+i+'" style="cursor:pointer">'
      +'<path d="M'+x.toFixed(1)+','+up+' V'+yBot+'" stroke="'+L.c
      +'" stroke-width="1.2" stroke-dasharray="4 3" stroke-opacity="'+(on?1:0.75)+'"/>'
      +txt(x+5,up+9,esc(L.n),{fs:11,fill:on?'#e6e6e6':L.c,stroke:1})
      +txt(x+5,up+21,fmt(L.t),{fs:10,fill:on?'#c8ccd2':'#6b7280',stroke:1})
      +'<rect x="'+(x-6)+'" y="'+(up-4)+'" width="200" height="28" fill="transparent"/>'
      +'</g>';
  });
  return s;
}

function drawFine(){
  const yb=226, hb=40;
  let s=txt(80,34,'a quarter degree at a time, from an ordinary morning to '
      +'the top of what a body survives',{fs:11.5,fill:'#8b93a0'});
  s+=keyLines(yb,yb+hb+352);
  // the bands, and a hoverable cell every quarter degree
  D.fine.forEach((b,i)=>{
    s+='<rect x="'+nx(b.lo).toFixed(1)+'" y="'+yb+'" width="'
      +(nx(b.hi)-nx(b.lo)).toFixed(1)+'" height="'+hb+'" fill="'+b.c
      +'" fill-opacity="0.8"/>';
    const mid=(nx(Math.max(b.lo,FN.lo))+nx(Math.min(b.hi,FN.hi)))/2;
    if(nx(Math.min(b.hi,FN.hi))-nx(Math.max(b.lo,FN.lo))>60)
      s+=txt(mid,yb+25,esc(b.n),{anchor:'middle',fs:12,fill:'#101010',w:600});
  });
  const n=Math.round((FN.hi-FN.lo)/CELL);
  for(let k=0;k<n;k++){
    const c=FN.lo+k*CELL, on=hot&&hot.t==='c'&&hot.i===k;
    s+='<g data-c="'+k+'" style="cursor:pointer">'
      +'<rect x="'+nx(c).toFixed(1)+'" y="'+yb+'" width="'
      +(nx(c+CELL)-nx(c)).toFixed(1)+'" height="'+hb+'" fill="#ffffff" fill-opacity="'
      +(on?0.3:0)+'"/></g>';
  }
  s+=ladder(yb,yb+hb);
  // what each degree costs, drawn as a band because the studies disagree
  const P1={top:yb+hb+64,h:106}, P2={top:yb+hb+206,h:106};
  function costPanel(P,lo,hi,f,lab,unit,col,kids){
    const y=v=>P.top+P.h-(v-lo)/(hi-lo)*P.h;
    let o=txt(80,P.top-14,lab,{fs:11.5,fill:'#c8ccd2'});
    for(let v=lo;v<=hi;v+=(hi-lo)/4){
      o+='<path d="M'+FN.x0+','+y(v).toFixed(1)+' H'+FN.x1
        +'" stroke="#242424" stroke-width="1"/>'
        +txt(FN.x0-10,y(v)+3.6,Math.round(v)+unit,{anchor:'end',fs:10.5});
    }
    let up='',dn='',mid='';
    for(let c=FN.lo;c<=FN.hi;c+=0.1){
      up+=(up?'L':'M')+nx(c).toFixed(1)+','+y(f(c,'hi')).toFixed(1);
      mid+=(mid?'L':'M')+nx(c).toFixed(1)+','+y(f(c)).toFixed(1);
    }
    for(let c=FN.hi;c>=FN.lo;c-=0.1)
      dn+='L'+nx(c).toFixed(1)+','+y(f(c,'lo')).toFixed(1);
    o+='<path d="'+up+dn+'Z" fill="'+col+'" fill-opacity="0.16"/>'
      +'<path d="'+mid+'" fill="none" stroke="'+col+'" stroke-width="2.2"/>';
    if(kids){
      let k='';
      for(let c=FN.lo;c<=FN.hi;c+=0.1)
        k+=(k?'L':'M')+nx(c).toFixed(1)+','+y(kids(c)).toFixed(1);
      o+='<path d="'+k+'" fill="none" stroke="#ffd24d" stroke-width="1.6" stroke-dasharray="5 3"/>'
        +txt(FN.x1-6,y(kids(FN.hi))-8,'a child',{anchor:'end',fs:10.5,
             fill:'#ffd24d',stroke:1});
    }
    return o;
  }
  s+=costPanel(P1,100,180,
    (c,k)=>metPct(c,k==='lo'?D.cost.met_lo:k==='hi'?D.cost.met_hi:D.cost.met),
    'What it costs to run: per cent of the resting metabolic rate','%','#e0673f');
  s+=costPanel(P2,60,140,
    (c,k)=>bpm(c,k==='lo'?D.cost.hr_lo:k==='hi'?D.cost.hr_hi:D.cost.hr),
    'What the heart does: beats a minute, from a resting seventy',' ','#58a6ff',
    c=>bpm(c,D.cost.hr_child));
  el.innerHTML=svg(P2.top+P2.h+46,s);
}

/* ------------------------------------------------- if someone collapses */
function drawHelp(){
  const x0=150, x1=930;
  let s='';
  // the thing that actually decides, drawn as two rows of the same scale
  const yA=112, yB=182, hb=44;
  s+=txt(80,64,'the same scale read two ways, by whether the person is '
        +'answering',{fs:11.5,fill:'#8b93a0'});
  D.fine.forEach((b,i)=>{
    const on=hot&&hot.t==='b'&&hot.i===i;
    s+='<g data-b="'+i+'" style="cursor:pointer">'
      +'<rect x="'+nx(b.lo).toFixed(1)+'" y="'+yA+'" width="'
      +(nx(b.hi)-nx(b.lo)).toFixed(1)+'" height="'+hb+'" fill="'+b.c
      +'" fill-opacity="'+(on?1:0.8)+'"/>';
    if(nx(b.hi)-nx(b.lo)>44)
      s+=txt((nx(b.lo)+nx(b.hi))/2,yA+27,esc(b.n),
             {anchor:'middle',fs:12,fill:'#101010',w:600});
    s+='</g>';
  });
  const onU=hot&&hot.t==='u';
  s+='<g data-u="1" style="cursor:pointer">'
    +'<rect x="'+x0+'" y="'+yB+'" width="'+(x1-x0)+'" height="'+hb+'" fill="#c02f2f"'
    +' fill-opacity="'+(onU?1:0.86)+'"/>'
    +txt((x0+x1)/2,yB+27,'Emergency at every temperature on this scale',
         {anchor:'middle',fs:13,fill:'#ffffff',w:600})+'</g>';
  s+=txt(x0-14,yA+27,'Alert and answering',{anchor:'end',fs:12.5,fill:'#c8ccd2'})
    +txt(x0-14,yB+27,'Not answering',{anchor:'end',fs:12.5,fill:'#e6e6e6'});
  s+=ladder(yA,yB+hb);

  // how long each way of cooling takes to cross the 30 minutes
  const cy=yB+hb+92, maxMin=70, sc=(x1-x0-70)/maxMin;
  const drop=D.coolfrom-D.coolto;
  s+=txt(80,cy-30,'How long each way of cooling takes to bring '+fmt(D.coolfrom)
        +' down to '+fmt(D.coolto),{fs:11.5,fill:'#c8ccd2'});
  const tx=x0+D.cooltarget*sc;
  s+='<path d="M'+tx.toFixed(1)+','+(cy-14)+' V'+(cy+D.cooling.length*46-14)
    +'" stroke="#ffd24d" stroke-width="1.6" stroke-dasharray="5 3"/>'
    +txt(tx+6,cy-20,'the '+D.cooltarget+' minutes the target allows',
         {fs:11,fill:'#ffd24d',stroke:1});
  D.cooling.forEach((m,i)=>{
    const mins=drop/m.r, y=cy+i*46, on=hot&&hot.t==='k'&&hot.i===i;
    s+='<g data-k="'+i+'" style="cursor:pointer">'
      +'<rect x="0" y="'+(y-16)+'" width="'+W+'" height="42" fill="#ffffff" fill-opacity="'
      +(on?0.045:0)+'"/>'
      +txt(x0,y-4,esc(m.n),{fs:11,fill:on?'#e6e6e6':'#8b93a0'})
      +'<rect x="'+x0+'" y="'+y+'" width="'+Math.min(mins,maxMin)*sc
      +'" height="16" fill="'+m.c+'" fill-opacity="0.85"/>'
      +txt(x0+Math.min(mins,maxMin)*sc+9,y+13,Math.round(mins)+' min',
           {fs:12,fill:'#c8ccd2',stroke:1})+'</g>';
  });

  // the order it is done in
  const ay=cy+D.cooling.length*46+52, aw=(x1-x0-4*12)/5;
  s+=txt(80,ay-14,'What a bystander does, in order',{fs:11.5,fill:'#c8ccd2'});
  D.actions.forEach((a,i)=>{
    const x=x0+i*(aw+12), on=hot&&hot.t==='a'&&hot.i===i;
    s+='<g data-a="'+i+'" style="cursor:pointer">'
      +'<rect x="'+x.toFixed(1)+'" y="'+ay+'" width="'+aw.toFixed(1)
      +'" height="56" rx="8" fill="'+a.c+'" fill-opacity="'+(on?0.30:0.14)
      +'" stroke="'+a.c+'" stroke-opacity="'+(on?0.9:0.45)+'"/>'
      +txt(x+aw/2,ay+27,(i+1)+'.',{anchor:'middle',fs:10.5,fill:a.c})
      +txt(x+aw/2,ay+44,esc(a.n),{anchor:'middle',fs:13,
           fill:on?'#e6e6e6':'#c8ccd2',w:600})
      +'</g>';
  });

  s+=txt(x0,ay+80,'One person alone does not put an unresponsive body into a '
        +'bathtub. Vomiting is common and the airway comes first.',
        {fs:11.5,fill:'#e0673f'})
    +txt(x0,ay+96,'Immersion needs a second pair of hands whose only job is '
        +'holding the head clear of the water.',{fs:11.5,fill:'#e0673f'});

  // and how to tell which of the two it is
  const ty=ay+146;
  s+=txt(80,ty-14,'Which of the two it is',{fs:11.5,fill:'#c8ccd2'})
    +txt(x0+230,ty+2,'A fever from an infection',{fs:11.5,fill:'#31d67a'})
    +txt(x0+540,ty+2,'Heat stroke',{fs:11.5,fill:'#e0673f'});
  D.tell.forEach((r,i)=>{
    const y=ty+26+i*26;
    s+='<g data-t="'+i+'" style="cursor:pointer">'
      +'<rect x="0" y="'+(y-15)+'" width="'+W+'" height="26" fill="#ffffff" fill-opacity="'
      +(hot&&hot.t==='T'&&hot.i===i?0.05:(i%2?0:0.02))+'"/>'
      +txt(x0+218,y,esc(r.k),{anchor:'end',fs:11.5,fill:'#8b93a0'})
      +txt(x0+230,y,esc(r.f),{fs:11.5,fill:'#c8ccd2'})
      +txt(x0+540,y,esc(r.h),{fs:11.5,fill:'#c8ccd2'})+'</g>';
  });
  const ny=ty+26+D.tell.length*26+18;
  s+='<g data-n="1" style="cursor:pointer">'
    +'<rect x="'+x0+'" y="'+(ny-16)+'" width="'+(x1-x0)+'" height="34" rx="8"'
    +' fill="#c02f2f" fill-opacity="'+(hot&&hot.t==='N'?0.28:0.14)
    +'" stroke="#c02f2f" stroke-opacity="0.5"/>'
    +txt((x0+x1)/2,ny+6,'When it cannot be told apart, the safe reading is '
         +'heat stroke',{anchor:'middle',fs:12.5,fill:'#e6e6e6'})+'</g>';
  el.innerHTML=svg(ny+46,s);
}

/* --------------------------------------------------------------- plumbing */
function renderTable(){
  const w=document.getElementById('degwrap');
  let r='<table id="degrees"><thead><tr><th>'+(U==='K'?'Kelvin':SYM[U].trim())
    +'</th><th>Where it falls</th><th>What is there</th>'
    +'<th>Metabolic rate</th><th>Pulse</th></tr></thead><tbody>';
  for(const d of D.table){
    r+='<tr><td class="c">'+fmt(d.t,U==='C'?0:U==='K'?2:1)+'</td>'
      +'<td class="z"><i style="background:'+d.zc+'"></i>'+esc(d.zn)+'</td>'
      +'<td class="w"><span class="cw">'+esc(conv(d.w))+'</span></td>'
      +'<td class="n '+d.mk+'" title="'+esc(d.mn)+'">'+esc(d.mv)+'</td>'
      +'<td class="n '+d.pk+'">'+esc(d.pv)+'</td></tr>';
  }
  w.innerHTML=r+'</tbody></table><p class="tkey">'+esc(conv(D.tkey))+'</p>';
}
const DRAW={range:drawRange, day:drawDay, site:drawSites, fever:drawFever,
            heat:drawHeat, fine:drawFine, help:drawHelp};
const INTRO={
  range:['The whole span','The figure and the table are one drawing on one '
    +'axis: a row is a degree, and a degree is a slice of a person at the '
    +'same height. The band the body holds is the green sliver at the ribs.'],
  day:['A day','Core temperature is lowest a couple of hours before waking '
    +'and highest in the late afternoon. The whole swing is about half a '
    +'degree, which is why the hour matters when a reading is judged.'],
  site:['Where it is taken','Four everyday sites, from a meta-analysis of '
    +'7,636 healthy adults. They disagree by more than a degree Celsius '
    +'between the '
    +'rectum and the armpit, which is more than the daily swing.'],
  fever:['Fever','Above, a fever: the set point moves and the body chases it. '
    +'Below, hyperthermia: the set point stays put and heat wins anyway. The '
    +'two look alike on a thermometer and are opposite underneath.'],
  heat:['Heat in, heat out','About a hundred watts at rest, and fourteen '
    +'times that climbing a mountain on a bicycle. Sweat is the only route '
    +'that still works once the room is hotter than the skin.'],
  fine:['Degree by degree','From an ordinary morning to the top of what a '
    +'body survives, a quarter degree at a time, with what each step costs '
    +'the metabolism and the heart. Both scales are on the ruler.'],
  help:['If someone collapses','The temperature does not decide this. '
    +'Whether the person is answering does. The lower row is red the whole '
    +'way across, and that is the point of the picture.'],
};
const VBTN=[['vRange','range'],['vDay','day'],['vSite','site'],
            ['vFever','fever'],['vHeat','heat'],['vFine','fine'],
            ['vHelp','help']];
// the one place the two halves are joined: the figure starts where the
// table's first row starts, to the pixel
function alignAxis(){
  const c=document.getElementById('chart');
  if(view!=='range'){ c.style.marginTop=''; return; }
  const h=document.querySelector('#degrees thead');
  c.style.marginTop = h ? h.getBoundingClientRect().height+'px' : '';
}
// A row that needs a third line makes every row that tall, because a row
// of the table is a degree of the figure and degrees are all the same
// size. Measured, not guessed, so a narrower window or a longer unit
// simply moves everything together.
function fitRows(){
  if(view!=='range') return;
  const rows=[...document.querySelectorAll('#degrees tbody tr')];
  if(!rows.length) return;
  // a cell stretches to its row, so the row cannot be measured from one:
  // the prose is wrapped in a span and that is what gets measured
  const spans=[...document.querySelectorAll('#degrees td.w .cw')];
  if(!spans.length) return;
  const tall=Math.ceil(Math.max(...spans.map(
    x=>x.getBoundingClientRect().height))+7);
  const want=Math.max(32,tall);
  if(want===ROW) return;
  ROW=want; setAxis();
  document.documentElement.style.setProperty('--row',ROW+'px');
  document.documentElement.style.setProperty('--figw',SPANW+'px');
  document.documentElement.style.setProperty('--row',ROW+'px');
  drawRange();
  alignAxis();
}
function render(){
  DRAW[view]();
  if(!hot){ const [n,b]=INTRO[view]; card('',n,'',b); }
  alignAxis(); fitRows();
}
function setView(v){
  view=v; hot=null;
  const span = v==='range';
  document.getElementById('degwrap').hidden = !span;
  document.querySelector('.stage').classList.toggle('span',span);
  document.getElementById('spanpair').style.display = span?'flex':'block';
  // the figure is drawn at one pixel per unit so its degrees land on the
  // table's rows exactly, whatever the page is doing around it
  document.documentElement.style.setProperty('--figw',SPANW+'px');
  document.documentElement.style.setProperty('--row',ROW+'px');
  for(const [id,k] of VBTN) document.getElementById(id).classList.toggle('on',v===k);
  render();
}
function setUnit(u){
  U=u; hot=null;
  for(const [id,k] of [['uC','C'],['uF','F'],['uK','K']])
    document.getElementById(id).classList.toggle('on',u===k);
  DRAW[view]();
  renderTable();
  alignAxis(); fitRows();
  // the prose below the diagram carries temperatures too
  for(const e of document.querySelectorAll('.cv')){
    if(!e.dataset.tpl) e.dataset.tpl=e.innerHTML;
    e.innerHTML=conv(e.dataset.tpl);
  }
  const sc=D.scales[u];
  // 37 converts to a terminating figure in each of the three
  card('The scale',sc.n,'body: '+fmt(37,u==='K'?2:1)
    +' · a rise of one degree Celsius: '+gap(1),sc.b);
}
for(const [id,k] of VBTN) document.getElementById(id).onclick=()=>setView(k);
for(const [id,k] of [['uC','C'],['uF','F'],['uK','K']])
  document.getElementById(id).onclick=()=>setUnit(k);

el.addEventListener('pointerover',ev=>{
  const g=ev.target.closest('[data-z],[data-m],[data-h],[data-s],[data-p],'
    +'[data-f],[data-i],[data-r],[data-w],[data-x],[data-c],[data-key],'
    +'[data-b],[data-u],[data-k],[data-a],[data-t],[data-n],[data-q],'
    +'[data-pt],[data-g]');
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
      fmt(v.m,2)+' · from '+fmt(v.lo,2)+' to '+fmt(v.hi,2),v.b);
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
  } else if(g.hasAttribute('data-q')){
    pick('data-q','q');
    const mid=hot.i;                    // data-q carries the degree itself
    const z=D.zones.find(x=>mid>=x.lo&&mid<x.hi)||D.zones[D.zones.length-1];
    const rg=D.regimes.find(r=>mid>=r.lo&&mid<r.hi);
    let cost;
    if(mid>=37){
      cost='Holding this costs about '+Math.round(metPct(mid)-100)
        +' per cent more oxygen than resting, and the pulse runs near '
        +Math.round(bpm(mid))+'. The climb flattens as it goes: about 9 per '
        +'cent a degree Celsius over the first two, and 4 by the time it '
        +'reaches {41.8}.';
    } else if(mid>=33){
      cost='Shivering starts around 36.8 and can reach almost five times the '
        +'resting rate, about 500 watts, near a core of 35. How hard it works '
        +'depends more on how cold the skin is than on the core.';
    } else if(mid>=18){
      cost='Below about 33 the only measurements come from people "'
        +'anaesthetised or on bypass. At 27 the rate is near half of resting, '
        +'and at 18, the coldest a person has been measured, it is 38 per '
        +'cent. The pulse falls 2.54 beats a minute per degree Celsius.';
    } else {
      cost='No whole-body measurement of a person exists this cold. The '
        +'figures that circulate for 15 and 10 degrees come from dogs cooled '
        +'in 1950, and they are probably too high.';
    }
    card(z.n,fmt(mid),rg?rg.n:'',cost+' '+z.b); tint(z.c);
  } else if(g.hasAttribute('data-pt')){
    pick('data-pt','M'); const m=D.measured[hot.i], src=D.msrc[m.s];
    card('A measurement',src.n,fmt(m.t)+' · '+m.p+' per cent of resting',
      src.b); tint(m.a?'#31d67a':'#58a6ff');
  } else if(g.hasAttribute('data-g')){
    pick('data-g','g'); const r=D.regimes[hot.i];
    card('Who the numbers came from',r.n,fmt(r.lo)+' to '+fmt(r.hi),r.b);
    tint(r.c);
  } else if(g.hasAttribute('data-c')){
    pick('data-c','c');
    const t=FN.lo+hot.i*CELL, mid=t+CELL/2;
    const b=D.fine.find(z=>mid>=z.lo&&mid<z.hi)||D.fine[D.fine.length-1];
    card(b.n,fmt(mid),
      Math.round(metPct(mid))+'% of the resting metabolic rate, somewhere '
      +'between '+Math.round(metPct(mid,D.cost.met_lo))+' and '
      +Math.round(metPct(mid,D.cost.met_hi))+'% · a pulse near '
      +Math.round(bpm(mid))+', or '+Math.round(bpm(mid,D.cost.hr_child))
      +' in a child',
      b.b+' '+(mid>D.cost.base
        ? 'That is '+gap(mid-D.cost.base)+' above a normal 37, and it costs '
          +'about '+Math.round(metPct(mid)-100)+' per cent more oxygen to hold.'
        : 'Below a normal 37, and cheaper to run.'));
    tint(b.c);
  } else if(g.hasAttribute('data-key')){
    pick('data-key','L'); const L=D.lines[hot.i];
    card('A line on the scale',L.n,fmt(L.t),L.b); tint(L.c);
  } else if(g.hasAttribute('data-b')){
    pick('data-b','b'); const b=D.fine[hot.i];
    card('Alert and answering',b.n,fmt(b.lo)+' to '+fmt(b.hi),b.b); tint(b.c);
  } else if(g.hasAttribute('data-u')){
    hot={t:'u',i:0};
    card('Not answering','An emergency, whatever the number','',D.unresp);
    tint('#c02f2f');
  } else if(g.hasAttribute('data-k')){
    pick('data-k','k'); const m=D.cooling[hot.i];
    const mins=(D.coolfrom-D.coolto)/m.r;
    card('A way of cooling',m.n,
      m.r.toFixed(3)+' °C a minute · '+Math.round(mins)+' minutes from '
      +fmt(D.coolfrom)+' to '+fmt(D.coolto)
      +(mins<=D.cooltarget?' · inside the target':' · past the target'),
      m.b+(m.e==='contested'?'' : ''));
    tint(m.c);
  } else if(g.hasAttribute('data-a')){
    pick('data-a','a'); const a=D.actions[hot.i];
    card('Step '+(hot.i+1)+' of '+D.actions.length,a.n,'',a.b); tint(a.c);
  } else if(g.hasAttribute('data-t')){
    pick('data-t','T'); const r=D.tell[hot.i];
    card('Telling them apart',r.k,'',
      'A fever from an infection: '+r.f+'. Heat stroke: '+r.h+'.');
  } else if(g.hasAttribute('data-n')){
    hot={t:'N',i:0};
    card('When it cannot be told','The safe reading is heat stroke','',
      D.tellnote); tint('#c02f2f');
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
    +'#tsvg [data-x],#tsvg [data-c],#tsvg [data-key],#tsvg [data-b],'
    +'#tsvg [data-u],#tsvg [data-k],#tsvg [data-a],#tsvg [data-t]').length,
  at37:fmt(37), rise1:gap(1),
  dayLow:dayT(D.day.nadir), dayHigh:dayT(18),
  chase:coreT(4)<setPoint(4), caught:Math.abs(coreT(10)-setPoint(10))<0.01,
  shed:coreT(16)>setPoint(16)});
</script>
</body>
</html>
"""


def _metab(t):
    """Metabolic rate at a whole degree: measured, bracketed, or neither."""
    for ct, pc, key, _aw in D.MEASURED:
        if abs(ct - t) < 0.65:
            return f"{pc}%", D.MSRC[key][0], "m"
    if t < 18:
        return "not measured", "no person has been measured this cold", "n"
    if t > 41.8:
        return "not measured", "nothing above 41.8 has been measured", "n"
    # the shivering peak is a different state, not a point on the same line,
    # so it never brackets anything
    pool = [m for m in D.MEASURED if m[2] != "eyolfson"]
    lo = max([m for m in pool if m[0] < t], key=lambda m: m[0], default=None)
    hi = min([m for m in pool if m[0] > t], key=lambda m: m[0], default=None)
    if lo and hi:
        a, b = sorted((lo[1], hi[1]))
        return f"{a} to {b}%", "between two measurements, not itself one", "b"
    return "not measured", "", "n"


def _pulse(t):
    P = D.PULSE
    if P["cold_lo"] <= t <= P["cold_hi"]:
        return f"{round(P['base'] - (37 - t) * P['cold_slope'])}", "m"
    if P["warm_lo"] <= t <= P["warm_hi"]:
        return f"{round(P['base'] + (t - 37) * P['warm_slope'])}", "m"
    if P["cold_hi"] < t < P["warm_lo"]:
        return f"{round(65 + (t - 35) * 2.5)}", "b"
    return "not measured", "n"


def degree_rows():
    """One row per whole degree, for the page to render in whatever scale
    the reader has chosen."""
    rows = []
    for t in range(int(D.ZONES[-1][1]), int(D.ZONES[0][0]) - 1, -1):
        z = next((z for z in D.ZONES if z[0] <= t < z[1]), D.ZONES[-1])
        mv, mnote, mk = _metab(t)
        pv, pk = _pulse(t)
        rows.append(dict(t=t, zn=z[3], zc=ZC[z[2]],
                         w=D.PER_DEGREE.get(t, z[4]),
                         mv=mv, mn=mnote, mk=mk, pv=pv, pk=pk))
    return rows


TKEY = ("Metabolic rate is a percentage of the resting rate at {37}. A figure "
        "in white is a measurement; a range in grey is the gap between the "
        "two measurements either side of it and is not itself measured. Pulse "
        "is 2.54 beats a minute per degree Celsius below {35}, from 216 people "
        "brought in with hypothermia, and about 8 a degree Celsius above {37}; "
        "between {35} and {37} no series covers it, and the figure there is a "
        "join. Peak shivering, near {35}, reaches 490 per cent and is left "
        "out of the ranges around it because it is a different state, not a "
        "point on the same line.")


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
        (A("Casa, D. J., DeMartini, J. K., Bergeron, M. F., Csillan, D., "
           "Eichner, E. R., Lopez, R. M., Ferrara, M. S., Miller, K. C., "
           "O'Connor, F., Sawka, M. N., &amp; Yeargin, S. W.", 2015,
           "National Athletic Trainers' Association position statement: "
           "Exertional heat illnesses", "Journal of Athletic Training",
           50, 9, "986-1000",
           "https://doi.org/10.4085/1062-6050-50.9.07"),
         "Cool first and transport second, the water temperature for "
         "immersion, and the technique for holding a patient's head clear."),
        (A("Lipman, G. S., Gaudio, F. G., Eifling, K. P., Ellis, M. A., "
           "Otten, E. M., &amp; Grissom, C. K.", 2019,
           "Wilderness Medical Society clinical practice guidelines for the "
           "prevention and treatment of heat illness: 2019 update",
           "Wilderness &amp; Environmental Medicine", 30, 4, "S33-S46",
           "https://doi.org/10.1016/j.wem.2018.10.004"),
         "That cooling is not delayed for a thermometer reading, and the "
         "warning that an unresponsive patient can drown."),
        (A("Douma, M. J., Aves, T., Allan, K. S., Bendall, J. C., "
           "Berry, D. C., Chang, W.-T., Epstein, J., Hood, N., "
           "Singletary, E. M., Zideman, D., &amp; Lin, S.", 2020,
           "First aid cooling techniques for heat stroke and exertional "
           "hyperthermia: A systematic review and meta-analysis",
           "Resuscitation", 148, None, "173-190",
           "https://doi.org/10.1016/j.resuscitation.2020.01.007"),
         "The graded cooling rates, and the finding that evaporative cooling "
         "could not be told apart from doing nothing."),
        (A("Filep, E. M., Murata, Y., Endres, B. D., Kim, G., "
           "Stearns, R. L., &amp; Casa, D. J.", 2020,
           "Exertional heat stroke, modality cooling rate, and survival "
           "outcomes: A systematic review", "Medicina", 56, 11, "589",
           "https://doi.org/10.3390/medicina56110589"),
         "The threshold of 0.15 degrees Celsius a minute separating adequate "
         "cooling "
         "from insufficient, and the outcomes on either side of it."),
        (A("Gagnon, D., Lemire, B. B., Casa, D. J., &amp; Kenny, G. P.", 2010,
           "Cold-water immersion and the treatment of hyperthermia: Using "
           "38.6 degrees C as a safe rectal temperature cooling limit",
           "Journal of Athletic Training", 45, 5, "439-444",
           "https://doi.org/10.4085/1062-6050-45.5.439"),
         "The experiment behind the stopping point, and the overshoot that "
         "follows cooling too far."),
        (A("Bouchama, A., Dehbi, M., &amp; Chaves-Carballo, E.", 2007,
           "Cooling and hemodynamic management in heatstroke: Practical "
           "recommendations", "Critical Care", 11, 3, "R54",
           "https://doi.org/10.1186/cc5910"),
         "That antipyretics have no place here, and the finding that "
         "immersion was poorly tolerated in classic heat stroke."),
        (A("Manthous, C. A., Hall, J. B., Olson, D., Singh, M., "
           "Chatila, W., Pohlman, A., Kushner, R., Schmidt, G. A., "
           "&amp; Wood, L. D.", 1995,
           "Effect of cooling on oxygen consumption in febrile critically "
           "ill patients", "American Journal of Respiratory and Critical "
           "Care Medicine", 151, 1, "10-14",
           "https://doi.org/10.1164/ajrccm.151.1.7812538"),
         "What a degree Celsius of fever costs in oxygen, at the low end of the "
         "band the page draws."),
        (apa.web("National Institute for Health and Care Excellence", 2021,
                 "Fever in under 5s: Assessment and initial management "
                 "(NICE guideline NG143)", "NICE",
                 "https://www.nice.org.uk/guidance/ng143"),
         "That tepid sponging is not recommended for fever, and that "
         "antipyretics treat distress rather than the number."),
        (A("Eyolfson, D. A., Tikuisis, P., Xu, X., Weseen, G., &amp; "
           "Giesbrecht, G. G.", 2001,
           "Measurement and prediction of peak shivering intensity in humans",
           "European Journal of Applied Physiology", 84, 1-2, "100-106",
           "https://doi.org/10.1007/s004210000329"),
         "The shivering peak on the measurement panel: 4.9 times the resting "
         "rate, and the fact that skin drives it more than core does."),
        (A("Pasquier, M., Cools, E., Zafren, K., Carron, P.-N., "
           "Frochaux, V., &amp; Rousson, V.", 2021,
           "Vital signs in accidental hypothermia",
           "High Altitude Medicine &amp; Biology", 22, 2, "142-147",
           "https://doi.org/10.1089/ham.2020.0179"),
         "The pulse in hypothermia, 2.54 beats a minute per degree Celsius, "
         "from 216 "
         "people rather than from convention."),
        (A("Rosomoff, H. L., &amp; Holaday, D. A.", 1954,
           "Cerebral blood flow and cerebral oxygen consumption during "
           "hypothermia", "American Journal of Physiology", 179, 1, "85-88",
           "https://doi.org/10.1152/ajplegacy.1954.179.1.85"),
         "The origin of the figure of six or seven per cent a degree Celsius. "
         "It was "
         "measured in dogs, in the brain, between 37 and 25 degrees, and it "
         "is routinely quoted as a whole-body number, which it is not."),
        (A("Bigelow, W. G., Lindsay, W. K., Harrison, R. C., "
           "Gordon, R. A., &amp; Greenwood, W. F.", 1950,
           "Oxygen transport and utilization in dogs at low body "
           "temperatures", "American Journal of Physiology", 160, 1,
           "125-137", None),
         "The dogs behind the table of percentages that still circulates for "
         "human hypothermia."),
        (apa.web("Guinness World Records", None,
                 "Highest body temperature", "Guinness World Records",
                 "https://www.guinnessworldrecords.com/world-records/67749-highest-body-temperature"),
         "The hottest survival on record. It is a record listing rather than "
         "a published case report, and the page says so."),
    ]
    js["table"] = degree_rows()
    js["tkey"] = TKEY
    data = json.dumps(js, separators=(",", ":"), ensure_ascii=False)
    html = (HTML.replace("__APACSS__", apa.CSS)
            .replace("__DATA__", data)
            .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2)
            .replace("__METHOD__", METHOD)
            .replace("__MEASURED__", MEASURED_NOTE)

            .replace("__REFS__", apa.render(refs)))
    out = ROOT / "temperature.html"
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({len(html):,} B): {len(D.ZONES)} bands, "
          f"{len(D.MARKS)} marks, {len(D.SITES)} sites, "
          f"{len(D.ROUTES)} routes, {len(refs)} references")


if __name__ == "__main__":
    main()
