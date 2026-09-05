#!/usr/bin/env python3
"""Generate cosmic-timeline.html, from the Big Bang to now.

The span is the problem: 13.8 billion years, and the last mark on it is
a couple of years old. The page draws the line four ways. Logarithmic in
years before now; logarithmic in years since the Big Bang; logarithmic
either side of the Sun's formation, which puts the Sun in the middle and
gives the whole history of the Earth half the width; and even, where
everything after the Sun collapses into the right-hand edge and the
reader sees what the logarithms were hiding.

Named milestones sit above the axis with their dating and their source.
Beneath it, thirteen strands of detail carried across from a Big History
notebook, each date checked before it was used.

Data: tools/cosmic_data.py and tools/bighistory.py.

Usage: python3 build_cosmic.py
"""

import json
from pathlib import Path

import apa
from bighistory import DETAIL, FIXED, STRANDS, Y0
from cosmic_data import EVENTS

ROOT = Path(__file__).parent.parent
NOW = 13.8e9
TSUN = 4.5682e9

rows = []
for e in EVENTS:
    d = dict(e)
    d["age"] = NOW - e["t"]          # years after the Big Bang
    d["m"] = 1
    rows.append(d)

detail = [{"t": t, "n": n, "k": k} for t, n, k in
          sorted(DETAIL, key=lambda x: -x[0])]

events_js = json.dumps(rows, separators=(",", ":"), ensure_ascii=False)
detail_js = json.dumps(detail, separators=(",", ":"), ensure_ascii=False)
strands_js = json.dumps([{"k": k, "n": n, "c": c} for k, n, c in STRANDS],
                        separators=(",", ":"), ensure_ascii=False)

NOTE1 = ("Time runs left to right from the Big Bang, on four scales. Back "
         "from now counts years before the present, so each step right is a "
         "tenth of the time left. Forward from the Big Bang counts years "
         "since it. Sun at the center is the same count stretched so the Sun "
         "sits on the middle, giving the nine billion years before it half "
         "the line. The even scale is one rate throughout, and shows what "
         "the logarithms hide.")

NOTE2 = ("The named milestones above the line carry their dating and its "
         "source, and where a claim is disputed the card says so and gives "
         "the firmer date beside it. Bars are the published uncertainty. The "
         "strands below the line hold the detail, from a Big History "
         "notebook; every date in them was checked against the current "
         "literature, and the ones that had drifted are corrected and listed "
         "under the references.")

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Universe in Time &middot; Altazor</title>
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
h1 { margin:0 0 10px; font-size:26px; }
.bar { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-bottom:10px; }
button { font:inherit; font-size:13.5px; padding:6px 14px; border-radius:999px;
  border:1px solid var(--line); background:#1a1a1a; color:var(--text); cursor:pointer; }
button:hover { border-color:var(--accent); }
button.on { background:var(--accent); border-color:var(--accent); color:#0b0b0b; }
#legend { display:flex; gap:7px; flex-wrap:wrap; margin-bottom:12px; }
#legend button { font-size:11.5px; padding:3px 10px; color:var(--muted);
  display:inline-flex; gap:5px; align-items:center; }
#legend button i { width:8px; height:8px; border-radius:50%; display:inline-block; }
#legend button.off { opacity:.38; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#chart { flex:1 1 640px; min-width:0; }
#chart svg { width:100%; height:auto; display:block; user-select:none; }
.side { flex:0 0 320px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:16px; }
#kindTxt { color:var(--muted); font-size:11.5px; letter-spacing:.09em;
  text-transform:uppercase; }
#nameTxt { font-weight:700; font-size:17px; margin:2px 0 2px; }
#whenTxt { font-size:13.5px; }
#bodyTxt { font-size:13.5px; line-height:1.55; margin-top:9px; }
#realTxt { color:var(--muted); font-size:13px; line-height:1.55; margin-top:10px;
  border-top:1px solid var(--line); padding-top:9px; }
#srcTxt { font-size:12px; margin-top:9px; }
#srcTxt a { color:var(--accent); }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.method { color:var(--muted); font-size:12.5px; margin-top:16px; max-width:760px; }
.method summary { cursor:pointer; color:var(--accent); }
.method table { border-collapse:collapse; margin-top:9px; font-size:12px; }
.method td { padding:3px 12px 3px 0; vertical-align:top; border-top:1px solid var(--line); }
.method td:first-child { color:var(--text); white-space:nowrap; }
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
  <nav class="site"><a href="library.html">&larr; Library &middot; The Universe</a> <a href="universe.html">The Universe</a> <a href="earth-history.html">Geological History</a> <a href="tree-of-life.html">Tree of Life</a></nav>
</header>
<h1>The Universe in Time</h1>
<div class="bar">
  <button id="bBack" class="on">Back from now</button>
  <button id="bFwd">Forward from the Big Bang</button>
  <button id="bSun">Sun at the center</button>
  <button id="bLin">Even scale</button>
</div>
<div id="legend"></div>
<div class="stage">
  <div id="chart"></div>
  <div class="side"><div class="card">
    <div id="kindTxt"></div>
    <div id="nameTxt">A mark under the cursor lands here</div>
    <div id="whenTxt"></div>
    <div id="bodyTxt"></div>
    <div id="realTxt"></div>
    <div id="srcTxt"></div>
  </div></div>
</div>
<p class="note">__NOTE1__</p>
<p class="note" style="border-top:none; padding-top:0;">__NOTE2__</p>
<div class="method"><details><summary>What the notebook said, and what the line says now</summary>
__FIXED__
</details></div>
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</div>
<script>
const EV=__EVENTS__, DET=__DETAIL__, ST=__STRANDS__;
const NOW=13.8e9, TSUN=4.5682e9, Y0=__Y0__;
const el=document.getElementById('chart');
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
const COL={}, SNAME={};
for(const s of ST){ COL[s.k]=s.c; SNAME[s.k]=s.n; }
const off=new Set();          // strands the reader has switched off
let mode='back', cur=0, curDet=-1;
const TMIN=2;   // the line stops two years back, where the last marks are

// how a span of years reads out loud
function span(y){
  if(y>=1e9) return (y/1e9).toFixed(y>=1e10?1:2)+' billion years';
  if(y>=1e6) return (y/1e6).toFixed(y>=1e8?0:1)+' million years';
  if(y>=1e3) return Math.round(y/1e3)+' thousand years';
  return Math.round(y)+' years';
}
function ago(t){ return t<1e4 ? Math.round(t).toLocaleString('en-US')+' years ago'
  : span(t)+' ago'; }
// a calendar year, where the mark is recent enough for one to mean
// anything. Y0-t is the astronomical year, which has a zero; the era
// notation does not, so a year at or below zero counts back from 1 BCE.
function cal(t){
  const y=Math.round(Y0-t);
  return y>0 ? y+' CE' : (1-y)+' BCE';
}
function whenTxt(t){ return t<13000 ? cal(t)+' \\u00b7 '+ago(t) : ago(t); }
// the age of the universe at the mark, worth saying only while the two
// numbers still differ: after the first hundred million years it rounds
// to the full 13.8 billion for everything
function sinceTxt(t){
  return t>=1e8 ? ' \\u00b7 '+span(NOW-t)+' after the Big Bang' : '';
}

const W=1000, L=112, R=34, TOP=34, LANEH=28, ROWH=22, GAP=48;
const LMIN=Math.log10(TMIN), LMAX=Math.log10(NOW), LSUN=Math.log10(TSUN);
let AXIS=200, H=600;

function X(t){
  const w=W-L-R;
  if(mode==='even') return L+(1-t/NOW)*w;
  if(mode==='fwd'){                       // log years since the Big Bang
    return L+Math.log10(Math.max(1,NOW-t))/Math.log10(NOW)*w;
  }
  if(mode==='sun'){
    // still log years before now, but broken at the Sun and stretched so
    // the Sun lands on the middle: half the line for the nine billion
    // years before it, half for the four and a half billion since
    const C=L+w*0.5, v=Math.log10(Math.max(TMIN,t));
    if(v>=LSUN) return L+(LMAX-v)/(LMAX-LSUN)*(C-L);
    return C+(LSUN-v)/(LSUN-LMIN)*(W-R-C);
  }
  const v=Math.log10(Math.max(TMIN,t));   // log years before now
  return L+(LMAX-v)/(LMAX-LMIN)*w;
}
const TICKS={
  back:[1e10,1e9,1e8,1e7,1e6,1e5,1e4,1e3,1e2,1e1],
  fwd:[1,1e3,1e6,1e9,1e10],
  // billions on the stretched arm, every other decade on the other
  sun:[12e9,10e9,8e9,6e9,TSUN,1e8,1e6,1e4,1e2],
  even:[12e9,10e9,8e9,6e9,4e9,2e9,0]};
function unit(a){
  return a>=1e9?(a/1e9)+' Gyr':a>=1e6?(a/1e6)+' Myr':a>=1e3?(a/1e3)+' kyr':a+' yr';
}
function tickLabel(t){
  if(mode==='fwd') return unit(t);
  if(mode==='sun'&&Math.abs(t-TSUN)<1e4) return 'the Sun';
  if(t===0) return 'now';
  return unit(t);
}
const CAP={back:'years before now, each step a tenth of the rest',
  fwd:'years since the Big Bang, each step ten times the last',
  sun:'years before now, stretched to put the Sun on the middle',
  even:'years before now, on an even scale'};

// pack the milestone labels into lanes so they do not collide
function packLanes(){
  const lanes=[], laneOf={};
  const order=EV.map((e,i)=>({e,i,x:X(e.t)})).sort((a,b)=>a.x-b.x);
  for(const o of order){
    const wide=o.e.n.length*7+26;
    const left=(o.x+wide>W-R)?o.x-wide:o.x;
    let lane=0;
    while(lanes[lane]!==undefined && left<lanes[lane]) lane++;
    lanes[lane]=left+wide;
    laneOf[o.i]=lane;
  }
  return {laneOf, n:lanes.length};
}
// the tallest the milestone block gets on any scale, so it does not jump
let MAXLANE=1;
(function(){ const keep=mode;
  for(const m of ['back','fwd','sun','even']){ mode=m;
    MAXLANE=Math.max(MAXLANE, packLanes().n); }
  mode=keep; })();

function render(){
  const pack=packLanes();
  AXIS=TOP+MAXLANE*LANEH+10;
  const shown=ST.filter(s=>!off.has(s.k));
  const ROW0=AXIS+GAP;
  H=ROW0+shown.length*ROWH+10;
  let s='<svg viewBox="0 0 '+W+' '+H+'" xmlns="http://www.w3.org/2000/svg" id="tsvg">';
  s+='<rect width="'+W+'" height="'+H+'" fill="#121212"/>';

  // the strand rows, and their detail marks
  shown.forEach((st,r)=>{
    const y=ROW0+r*ROWH, mid=y+ROWH/2;
    if(r%2===0) s+='<rect x="'+L+'" y="'+y+'" width="'+(W-L-R)+'" height="'+ROWH
      +'" fill="#ffffff" fill-opacity="0.022"/>';
    s+='<text x="'+(L-9)+'" y="'+(mid+3.6)+'" text-anchor="end" font-size="10.5" '
      +'fill="'+st.c+'" fill-opacity="0.85" data-row="'+st.k
      +'" style="cursor:pointer">'+esc(st.n)+'</text>';
    DET.forEach((d,i)=>{
      if(d.k!==st.k) return;
      const x=X(d.t);
      if(x<L-1||x>W-R+1) return;
      const hot=i===curDet;
      s+='<g data-d="'+i+'" style="cursor:pointer">'
        +'<circle cx="'+x.toFixed(1)+'" cy="'+mid.toFixed(1)+'" r="'+(hot?5:2.9)
        +'" fill="'+st.c+'" fill-opacity="'+(hot?1:0.72)+'"'
        +(hot?' stroke="#e6e6e6" stroke-width="1.2"':'')+'/>'
        +'<rect x="'+(x-5).toFixed(1)+'" y="'+y+'" width="10" height="'+ROWH
        +'" fill="transparent"/></g>';
    });
  });

  // the axis and its ticks
  s+='<path d="M'+L+','+AXIS+' H'+(W-R)+'" stroke="#3d444d" stroke-width="1.4"/>';
  for(const t of TICKS[mode]){
    if(t>NOW||t<0) continue;
    const x=mode==='fwd'
      ? L+Math.log10(Math.max(1,t))/Math.log10(NOW)*(W-L-R) : X(t);
    s+='<path d="M'+x.toFixed(1)+','+(AXIS-5)+' v10" stroke="#3d444d" stroke-width="1.2"/>'
      +'<text x="'+x.toFixed(1)+'" y="'+(AXIS+21)+'" text-anchor="middle" font-size="10.5" fill="#6b7280">'
      +tickLabel(t)+'</text>';
  }
  s+='<text x="'+(W-R)+'" y="'+(AXIS+38)+'" text-anchor="end" font-size="10.5" fill="#6b7280">'
    +CAP[mode]+'</text>';
  s+='<text x="'+L+'" y="20" font-size="11" fill="#6b7280">the Big Bang</text>'
    +'<text x="'+(W-R)+'" y="20" text-anchor="end" font-size="11" fill="#6b7280">now</text>';

  // the milestones, above the line
  EV.forEach((e,i)=>{
    const x=X(e.t);
    const flip=x+e.n.length*7+18>W-R;
    const y=AXIS-16-(MAXLANE-1-pack.laneOf[i])*LANEH;
    const c=COL[e.k]||'#e6e6e6';
    s+='<g data-i="'+i+'" style="cursor:pointer">';
    if(e.u){
      const cl=v=>Math.max(L,Math.min(W-R,v));
      const x0=cl(X(e.t+e.u)), x1=cl(X(Math.max(1,e.t-e.u)));
      s+='<path d="M'+Math.min(x0,x1).toFixed(1)+','+(y-9)+' H'+Math.max(x0,x1).toFixed(1)
        +'" stroke="'+c+'" stroke-width="2.4" stroke-opacity="0.3" stroke-linecap="round"/>';
    }
    s+='<path d="M'+x.toFixed(1)+','+y+' V'+AXIS+'" stroke="'+c+'" stroke-width="1" stroke-opacity="0.45"/>'
      +'<circle cx="'+x.toFixed(1)+'" cy="'+y+'" r="'+(i===cur&&curDet<0?6:4.5)+'" fill="'+c+'" stroke="#121212" stroke-width="1.4"/>'
      // a label that would run off the right edge is set to the left instead
      +'<text x="'+(flip?(x-9):(x+9)).toFixed(1)+'" y="'+(y+4)+'" text-anchor="'+(flip?'end':'start')
      +'" font-size="12" font-weight="'+(i===cur&&curDet<0?700:400)
      +'" fill="#e6e6e6" stroke="#121212" stroke-width="2.6" paint-order="stroke">'+esc(e.n)+'</text>'
      +'<rect x="'+(flip?(x-9-e.n.length*7):(x-9)).toFixed(1)+'" y="'+(y-11)+'" width="'+(e.n.length*7+22)+'" height="22" fill="transparent"/>'
      +'</g>';
  });
  s+='</svg>';
  el.innerHTML=s;
}

function show(i){
  const e=EV[i]; if(!e) return;
  cur=i; curDet=-1;
  const kt=document.getElementById('kindTxt');
  kt.textContent=SNAME[e.k]||''; kt.style.color=COL[e.k];
  document.getElementById('nameTxt').textContent=e.n;
  document.getElementById('whenTxt').textContent=whenTxt(e.t)+sinceTxt(e.t);
  document.getElementById('bodyTxt').textContent=e.b;
  document.getElementById('realTxt').textContent=e.r;
  document.getElementById('srcTxt').innerHTML=
    '<a href="'+e.u2+'">'+esc(e.s)+'</a>';
  render();
}
function showDet(i){
  const d=DET[i]; if(!d) return;
  curDet=i;
  const kt=document.getElementById('kindTxt');
  kt.textContent=SNAME[d.k]||''; kt.style.color=COL[d.k];
  document.getElementById('nameTxt').textContent=d.n;
  document.getElementById('whenTxt').textContent=whenTxt(d.t)+sinceTxt(d.t);
  document.getElementById('bodyTxt').textContent='';
  document.getElementById('realTxt').textContent='';
  document.getElementById('srcTxt').innerHTML='';
  render();
}

el.addEventListener('pointerover',ev=>{
  const d=ev.target.closest('[data-d]');
  if(d){ showDet(+d.getAttribute('data-d')); return; }
  const g=ev.target.closest('[data-i]');
  if(g) show(+g.getAttribute('data-i'));
});
el.addEventListener('click',ev=>{
  const r=ev.target.closest('[data-row]');
  if(r) toggle(r.getAttribute('data-row'));
});

const legend=document.getElementById('legend');
legend.innerHTML=ST.map(s=>'<button data-k="'+s.k+'"><i style="background:'
  +s.c+'"></i>'+s.n+'</button>').join('');
function toggle(k){
  if(off.has(k)) off.delete(k); else off.add(k);
  legend.querySelector('[data-k="'+k+'"]').classList.toggle('off',off.has(k));
  render();
}
legend.addEventListener('click',ev=>{
  const b=ev.target.closest('[data-k]');
  if(b) toggle(b.getAttribute('data-k'));
});

function setMode(m){
  mode=m; curDet=-1;
  for(const [id,v] of [['bBack','back'],['bFwd','fwd'],['bSun','sun'],
                       ['bLin','even']])
    document.getElementById(id).classList.toggle('on',m===v);
  render();
}
document.getElementById('bBack').onclick=()=>setMode('back');
document.getElementById('bFwd').onclick=()=>setMode('fwd');
document.getElementById('bSun').onclick=()=>setMode('sun');
document.getElementById('bLin').onclick=()=>setMode('even');

render();
show(0);
window.__cosmic=()=>({events:EV.length, detail:DET.length,
  strands:ST.length, mode, cur, off:off.size,
  sunX:Math.round(X(TSUN)), midX:Math.round(L+(W-L-R)/2),
  ordered:EV.every((e,i)=>!i||e.t<=EV[i-1].t),
  detOrdered:DET.every((d,i)=>!i||d.t<=DET[i-1].t),
  sourced:EV.every(e=>e.s&&e.u2&&e.b&&e.r),
  rows:document.querySelectorAll('[data-row]').length,
  dots:document.querySelectorAll('[data-d]').length,
  spanLog:Math.round(X(EV[EV.length-1].t)-X(EV[0].t))});
</script>
</body>
</html>
"""


def fixed_html():
    tr = "".join(f"<tr><td>{a}</td><td>The notebook: {b}. The line now: "
                 f"{c}.</td></tr>" for a, b, c in FIXED)
    return f"<table>{tr}</table>"


def main():
    refs = []
    for e in EVENTS:
        entry = (apa.article("Planck Collaboration", 2020,
                             "Planck 2018 results. VI. Cosmological parameters",
                             "Astronomy &amp; Astrophysics", 641, None, "A6",
                             "https://doi.org/10.1051/0004-6361/201833910")
                 if e["n"] == "The Big Bang" else
                 apa.web("Space.com", 2025,
                         "Cosmic miracle! James Webb Space Telescope discovers "
                         "the earliest galaxy ever seen", "Space.com", e["u2"])
                 if e["n"] == "The first stars" else
                 apa.wiki(e["u2"]))
        refs.append((entry, f"The date and the wording for {e['n']}."))
    for u, ann in [
        ("https://en.wikipedia.org/wiki/Timeline_of_natural_history",
         "Checking the dates in the cosmos, Earth, life, animals, mammals "
         "and primates strands."),
        ("https://en.wikipedia.org/wiki/Timeline_of_human_prehistory",
         "Checking the dates in the us strand, from the first tools to the "
         "end of the last glacial period."),
        ("https://en.wikipedia.org/wiki/Timeline_of_historic_inventions",
         "Checking the dates in the farming, science and maths strands."),
        ("https://en.wikipedia.org/wiki/Timeline_of_world_history",
         "Checking the dates in the states and empires strand."),
    ]:
        refs.append((apa.wiki(u), ann))
    refs.append((apa.article(
        "Sehasseh, E. M., Fernandez, P., Kuhn, S., Stiner, M., Mentzer, S., "
        "Colarossi, D., Clark, A., Lanoe, F., Pailes, M., Hoffmann, D., "
        "Benson, A., Rhodes, E., Benmansour, M., Laissaoui, A., Ziani, I., "
        "Vidal-Matutano, P., Morales, J., Djellal, Y., Longet, B., ... "
        "Bouzouggar, A.", 2021,
        "Early Middle Stone Age personal ornaments from Bizmoune Cave, "
        "Essaouira, Morocco", "Science Advances", 7, 39, "eabi8620",
        "https://doi.org/10.1126/sciadv.abi8620"),
        "The 142,000 year date for the shell beads in the us strand."))
    refs.append((apa.article(
        "Hu, W., Hao, Z., Du, P., Di Vincenzo, F., Manzi, G., Cui, J., "
        "Fu, Y.-X., Pan, Y.-H., &amp; Li, H.", 2023,
        "Genomic inference of a severe human bottleneck during the Early to "
        "Middle Pleistocene transition", "Science", 381, 6661, "979-984",
        "https://doi.org/10.1126/science.abq7487"),
        "The population bottleneck of about 1,280, and the dispute over it."))
    refs.append((apa.web(
        "Roser, M., Ritchie, H., &amp; Ortiz-Ospina, E.", 2013,
        "World population growth", "Our World in Data",
        "https://ourworldindata.org/world-population-growth"),
        "The world population strand."))
    html = (HTML.replace("__APACSS__", apa.CSS)
            .replace("__EVENTS__", events_js)
            .replace("__DETAIL__", detail_js)
            .replace("__STRANDS__", strands_js)
            .replace("__Y0__", str(Y0))
            .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2)
            .replace("__FIXED__", fixed_html())
            .replace("__REFS__", apa.render(refs)))
    out = ROOT / "cosmic-timeline.html"
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({len(html):,} B): {len(EVENTS)} milestones, "
          f"{len(detail)} detail marks, {len(STRANDS)} strands, "
          f"{len(FIXED)} corrections")


if __name__ == "__main__":
    main()
