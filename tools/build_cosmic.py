#!/usr/bin/env python3
"""Generate cosmic-timeline.html, from the Big Bang to now.

The span is the problem: 13.8 billion years, and the last mark on it is
two thousand years old, a ten-millionth of the whole. The page draws the
line twice. Logarithmic in years before now, where every event has room
and the recent ones spread out; and linear, where they collapse into the
right-hand edge and the reader sees what the log scale was hiding.

A scrubber runs the clock forward from the Big Bang, so events arrive in
order rather than sitting there all at once.

Data: tools/cosmic_data.py.

Usage: python3 build_cosmic.py
"""

import json
import math
from pathlib import Path

from cosmic_data import EVENTS, KINDS

ROOT = Path(__file__).parent.parent
NOW = 13.8e9

rows = []
for e in EVENTS:
    d = dict(e)
    d["age"] = NOW - e["t"]          # years after the Big Bang
    rows.append(d)

events_js = json.dumps(rows, separators=(",", ":"), ensure_ascii=False)
kinds_js = json.dumps([{"k": k, "n": n, "c": c} for k, n, c in KINDS],
                      separators=(",", ":"))

NOTE1 = ("Time runs left to right from the Big Bang, on three scales. Back "
         "from now counts years before the present, so each step right is a "
         "tenth of the time left and the recent marks spread out. Forward "
         "from the Big Bang counts years since it, which opens up the first "
         "stars and closes everything after the Sun into the edge. The even "
         "scale is the same events at one rate, and shows what both "
         "logarithms hide.")

NOTE2 = ("Each mark carries the dating and its source, and where a claim is "
         "disputed the card says so and gives the firmer, later date beside "
         "it. Bars are the published uncertainty where one is quoted. Three "
         "of these are ranges rather than moments: life, many cells and the "
         "first nervous systems each name the earliest evidence, not the "
         "event.")

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Universe in Time · Altazor</title>
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
.bar { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-bottom:8px; }
button { font:inherit; font-size:13.5px; padding:6px 14px; border-radius:999px;
  border:1px solid var(--line); background:#1a1a1a; color:var(--text); cursor:pointer; }
button:hover { border-color:var(--accent); }
button.on { background:var(--accent); border-color:var(--accent); color:#0b0b0b; }
#clock { color:var(--muted); font-size:12.5px; }
.slider { display:flex; align-items:center; gap:10px; margin:8px 0 12px; }
.slider input { flex:1; accent-color:var(--accent); }
#legend { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:10px;
  color:var(--muted); font-size:12px; align-items:center; }
#legend span { display:flex; gap:5px; align-items:center; }
#legend i { width:9px; height:9px; border-radius:50%; display:inline-block; }
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
.refs { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.refs p { margin:0 0 8px; overflow-wrap:anywhere; }
.refs a { color:var(--accent); }
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
  <button id="bLin">Even scale</button>
  <button id="bPlay">Run the clock</button>
  <span id="clock"></span>
</div>
<div class="slider">
  <input id="t" type="range" min="0" max="1000" value="1000">
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
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</div>
<script>
const EV=__EVENTS__, KINDS=__KINDS__, NOW=13.8e9;
const el=document.getElementById('chart');
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
const COL={}; for(const k of KINDS) COL[k.k]=k.c;
let mode='back', cur=0, playing=null, cut=NOW;  // cut: years after the Big Bang
const TMIN=1e3;   // the line stops a thousand years back, where the marks do

document.getElementById('legend').innerHTML=KINDS.map(k=>
  '<span><i style="background:'+k.c+'"></i>'+k.n+'</span>').join('');

// how a span of years reads out loud
function span(y){
  if(y>=1e9) return (y/1e9).toFixed(y>=1e10?1:2)+' billion years';
  if(y>=1e6) return (y/1e6).toFixed(y>=1e8?0:1)+' million years';
  if(y>=1e3) return Math.round(y/1e3)+' thousand years';
  return Math.round(y)+' years';
}
function ago(t){ return t<1e4 ? Math.round(t).toLocaleString('en-US')+' years ago'
  : span(t)+' ago'; }

const W=1000, H=470, L=52, R=34, TOP=40, BOT=76;
const AXIS=H-BOT;
const LMIN=Math.log10(TMIN), LMAX=Math.log10(NOW);
function X(t){
  const span=W-L-R;
  if(mode==='even') return L+(1-t/NOW)*span;
  if(mode==='fwd'){          // log years since the Big Bang
    const a=Math.max(1,NOW-t);
    return L+Math.log10(a)/Math.log10(NOW)*span;
  }
  const v=Math.log10(Math.max(TMIN,t));   // log years before now
  return L+(LMAX-v)/(LMAX-LMIN)*span;
}
const TICKS={
  back:[1e10,1e9,1e8,1e7,1e6,1e5,1e4,1e3],
  fwd:[1,1e3,1e6,1e9,1e10],
  even:[12e9,10e9,8e9,6e9,4e9,2e9,0]};
function tickLabel(t){
  if(mode==='fwd'){
    const a=t;
    return a>=1e9?(a/1e9)+' Gyr':a>=1e6?(a/1e6)+' Myr':a>=1e3?(a/1e3)+' kyr':a+' yr';
  }
  if(t===0) return 'now';
  return t>=1e9?(t/1e9)+' Gyr':t>=1e6?(t/1e6)+' Myr':t>=1e3?(t/1e3)+' kyr':t+' yr';
}

function render(){
  let s='<svg viewBox="0 0 '+W+' '+H+'" xmlns="http://www.w3.org/2000/svg" id="tsvg">';
  s+='<rect width="'+W+'" height="'+H+'" fill="#121212"/>';
  // the axis and its ticks
  s+='<path d="M'+L+','+AXIS+' H'+(W-R)+'" stroke="#3d444d" stroke-width="1.4"/>';
  for(const t of TICKS[mode]){
    if(t>NOW) continue;
    const x=mode==='fwd'?L+Math.log10(Math.max(1,t))/Math.log10(NOW)*(W-L-R):X(t);
    s+='<path d="M'+x.toFixed(1)+','+(AXIS-5)+' v10" stroke="#3d444d" stroke-width="1.2"/>'
      +'<text x="'+x.toFixed(1)+'" y="'+(AXIS+21)+'" text-anchor="middle" font-size="10.5" fill="#6b7280">'
      +tickLabel(t)+'</text>';
  }
  const CAP={back:'years before now, each step a tenth of the rest',
    fwd:'years since the Big Bang, each step ten times the last',
    even:'years before now, on an even scale'};
  s+='<text x="'+(W-R)+'" y="'+(AXIS+38)+'" text-anchor="end" font-size="10.5" fill="#6b7280">'
    +CAP[mode]+'</text>';
  s+='<text x="'+L+'" y="24" font-size="11" fill="#6b7280">the Big Bang</text>'
    +'<text x="'+(W-R)+'" y="24" text-anchor="end" font-size="11" fill="#6b7280">now</text>';

  // the clock: everything after the cut is dimmed
  const xc=X(Math.max(1,NOW-cut));
  s+='<rect x="'+xc.toFixed(1)+'" y="'+TOP+'" width="'+Math.max(0,W-R-xc).toFixed(1)
    +'" height="'+(AXIS-TOP)+'" fill="#121212" fill-opacity="0.72"/>'
    +'<path d="M'+xc.toFixed(1)+','+TOP+' V'+AXIS+'" stroke="var(--accent)" stroke-width="1.2" stroke-opacity="0.8"/>';

  // the events, stacked so their labels do not collide
  const lanes=[];
  const order=EV.map((e,i)=>({e,i,x:X(e.t)})).sort((a,b)=>a.x-b.x);
  const laneOf={};
  for(const o of order){
    const wide=o.e.n.length*7+26;
    const flip=o.x+wide>W-R;
    const left=flip?o.x-wide:o.x;
    let lane=0;
    while(lanes[lane]!==undefined && left<lanes[lane]) lane++;
    lanes[lane]=left+wide;
    laneOf[o.i]=lane;
  }
  EV.forEach((e,i)=>{
    const x=X(e.t), on=e.t>=NOW-cut;
    const flip=x+e.n.length*7+18>W-R;
    const lane=laneOf[i];
    const y=AXIS-26-lane*30;
    const c=COL[e.k];
    s+='<g data-i="'+i+'" style="cursor:pointer" opacity="'+(on?1:0.18)+'">';
    if(e.u){
      const cl=v=>Math.max(L,Math.min(W-R,v));
      const x0=cl(X(e.t+e.u)), x1=cl(X(Math.max(1,e.t-e.u)));
      s+='<path d="M'+Math.min(x0,x1).toFixed(1)+','+(y-9)+' H'+Math.max(x0,x1).toFixed(1)
        +'" stroke="'+c+'" stroke-width="2.4" stroke-opacity="0.3" stroke-linecap="round"/>';
    }
    s+='<path d="M'+x.toFixed(1)+','+y+' V'+AXIS+'" stroke="'+c+'" stroke-width="1" stroke-opacity="0.45"/>'
      +'<circle cx="'+x.toFixed(1)+'" cy="'+y+'" r="'+(i===cur?6:4.5)+'" fill="'+c+'" stroke="#121212" stroke-width="1.4"/>'
      // a label that would run off the right edge is set to the left instead
      +'<text x="'+(flip?(x-9):(x+9)).toFixed(1)+'" y="'+(y+4)+'" text-anchor="'+(flip?'end':'start')
      +'" font-size="12" font-weight="'+(i===cur?700:400)
      +'" fill="#e6e6e6" stroke="#121212" stroke-width="2.6" paint-order="stroke">'+esc(e.n)+'</text>'
      +'<rect x="'+(flip?(x-9-e.n.length*7):(x-9)).toFixed(1)+'" y="'+(y-11)+'" width="'+(e.n.length*7+22)+'" height="22" fill="transparent"/>'
      +'</g>';
  });
  s+='</svg>';
  el.innerHTML=s;
  document.getElementById('clock').textContent=
    cut>=NOW ? 'the whole 13.8 billion years'
             : span(cut)+' after the Big Bang';
}

function show(i){
  const e=EV[i]; if(!e) return;
  cur=i;
  const kind=KINDS.find(k=>k.k===e.k);
  const kt=document.getElementById('kindTxt');
  kt.textContent=kind?kind.n:''; kt.style.color=COL[e.k];
  document.getElementById('nameTxt').textContent=e.n;
  document.getElementById('whenTxt').textContent=
    ago(e.t)+' \\u00b7 '+span(e.age)+' after the Big Bang';
  document.getElementById('bodyTxt').textContent=e.b;
  document.getElementById('realTxt').textContent=e.r;
  document.getElementById('srcTxt').innerHTML=
    '<a href="'+e.u2+'">'+esc(e.s)+'</a>';
  render();
}

el.addEventListener('pointerover',ev=>{
  const g=ev.target.closest('[data-i]');
  if(g) show(+g.getAttribute('data-i'));
});
const slider=document.getElementById('t');
slider.addEventListener('input',()=>{
  // the slider is logarithmic in time since the Big Bang, so the first
  // stars and the last two thousand years both get travel
  const u=+slider.value/1000;
  cut = u>=1 ? NOW : Math.pow(10, u*Math.log10(NOW));
  render();
});
function setMode(m){
  mode=m;
  document.getElementById('bBack').classList.toggle('on',m==='back');
  document.getElementById('bFwd').classList.toggle('on',m==='fwd');
  document.getElementById('bLin').classList.toggle('on',m==='even');
  render();
}
document.getElementById('bBack').onclick=()=>setMode('back');
document.getElementById('bFwd').onclick=()=>setMode('fwd');
document.getElementById('bLin').onclick=()=>setMode('even');
document.getElementById('bPlay').onclick=e=>{
  if(playing){ clearInterval(playing); playing=null; e.target.classList.remove('on');
    e.target.textContent='Run the clock'; return; }
  e.target.classList.add('on'); e.target.textContent='Stop';
  slider.value=0; slider.dispatchEvent(new Event('input'));
  playing=setInterval(()=>{
    const v=+slider.value+6;
    slider.value=Math.min(1000,v);
    slider.dispatchEvent(new Event('input'));
    if(v>=1000){ clearInterval(playing); playing=null;
      e.target.classList.remove('on'); e.target.textContent='Run the clock'; }
  },40);
};

render();
show(0);
window.__cosmic=()=>({events:EV.length, mode, cur, cut,
  visible:EV.filter(e=>e.t>=NOW-cut).length,
  ordered:EV.every((e,i)=>!i||e.t<=EV[i-1].t),
  sourced:EV.every(e=>e.s&&e.u2&&e.b&&e.r),
  spanLog:Math.round(X(EV[EV.length-1].t)-X(EV[0].t))});
</script>
</body>
</html>
"""


def main():
    refs = ['<p>Every date on the line, with the study behind it:</p>']
    for e in EVENTS:
        refs.append(f'<p>{e["n"]}: {e["s"]}.\n<a href="{e["u2"]}">{e["u2"]}</a></p>')
    html = (HTML.replace("__EVENTS__", events_js).replace("__KINDS__", kinds_js)
            .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2)
            .replace("__REFS__", "\n".join(refs)))
    out = ROOT / "cosmic-timeline.html"
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({len(html):,} B): {len(EVENTS)} events, "
          f"{len(KINDS)} kinds, {NOW/1e9:.1f} Gyr span")


if __name__ == "__main__":
    main()
