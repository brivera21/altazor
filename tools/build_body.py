#!/usr/bin/env python3
"""Generate body.html, the systems of the human body.

Every outline of an organ is traced from a mesh. BodyParts3D segmented
one adult male into named anatomical parts, and each part on the figure
is its own mesh projected orthographically and traced at the silhouette.
The body turns in eight steps of forty-five degrees, and each step is a
real projection of the meshes rather than a distortion of the front view.

The nervous system is the exception, and the page says so. That model
carries the brain and the two optic nerves and nothing else, so the cord,
the spinal nerves, the cranial nerves and the two autonomic outflows are
drawn as 3D lines over the traced skeleton, hung on the measured position
of every vertebra and every limb bone in this same body.

The tracing runs in tools/pack_body.py from meshes fetched once, and the
landmark measuring in tools/nervous_data.py. Both outputs are checked in,
so this builder needs neither the network nor the 1.3 GB of meshes.

The numbers beside each system do not come from the model. They come from
the literature, and several of the familiar ones turn out to rest on
nothing measured, which is said where it applies.

Data: tools/body_data.py, tools/nervous_data.py, tools/data/body_paths.json.

Usage: python3 build_body.py
"""

import json
from pathlib import Path

import apa
import body_data as D
import nervous_data as NV

ROOT = Path(__file__).parent.parent
PATHS = json.loads((ROOT / "tools" / "data" / "body_paths.json").read_text())

# hue and saturation per system, and the order the buttons run in
LOOK = {
    "skeletal": (36, 0.28), "muscular": (7, 0.50), "nervous": (288, 0.30),
    "cardiovascular": (354, 0.55), "respiratory": (201, 0.34),
    "digestive": (28, 0.46), "urinary": (44, 0.44), "endocrine": (272, 0.36),
    "lymphoid": (128, 0.34), "reproductive": (322, 0.32),
    "integumentary": (26, 0.20), "sensory": (188, 0.36),
}

NOTE1 = ("Every organ here is traced from a mesh of one segmented adult "
         "male, and the body turns in eight steps, each a real projection "
         "of those meshes. A system button chooses what is drawn, and the "
         "cut puts a plane through the body and drops what lies in front, "
         "so the superficial muscles come away from the deep ones.")

NOTE2 = ("The nerves are the exception. That model has no cord and no "
         "nerves beyond the optic pair, so the nervous system is drawn "
         "over the traced skeleton, hung on the measured position of every "
         "vertebra and limb bone in this body. It is registered to the "
         "bones on screen, and it is not a scan. The model is also male, "
         "and it has no lymph vessels and no nodes.")

METHOD = (
    "How the figure was made. Each part is a separate closed surface in "
    "BodyParts3D, keyed to a term in the Foundational Model of Anatomy. "
    "Every triangle was turned about the body's own vertical axis, "
    "projected, filled by scanline into a raster at between 1.4 and 8 "
    "pixels per millimetre depending on the size of the part, and the "
    "silhouette of that raster traced and reduced to a polygon. What is "
    "drawn is therefore the true outline of the part seen from that "
    "direction, at about a quarter of a millimetre, and not an artist's "
    "reading of it. Four directions are traced and eight are shown: an "
    "orthographic silhouette seen from behind is the same outline mirrored, "
    "so the far half of the turn costs nothing but a reversal of the "
    "stacking order. Parts are stacked at every angle by the depth of "
    "their nearest point, so what covers what on the figure is what covers "
    "what in the body. The 925 parts here are the ones with a mesh in the "
    "database, out of 1,513 named terms.")

NERVENOTE = (
    "How the nerves were made, since they are the one thing here that is "
    "not traced. BodyParts3D has the brain, the fluid spaces in it and the "
    "two optic nerves. It has no spinal cord, no spinal nerves, no cranial "
    "nerves but the second, and no autonomic chain, so those are drawn as "
    "lines in three dimensions and turn with the body like everything "
    "else. They are not freehand. Every one is written against the "
    "measured position of a real part of this same body: a spinal level is "
    "that vertebra's own centroid, the arm nerves run at fractions along "
    "this humerus and this ulna, the cord ends where this first lumbar "
    "vertebra is, and the vagus ends on this heart and this stomach. The "
    "courses follow the standard descriptions in Gray's Anatomy and in "
    "Moore. What that buys is registration against the bones on screen. "
    "What it does not buy is millimetre accuracy for any individual nerve "
    "in any individual person, and nerves vary between people more than "
    "bones do.")

GAPNOTE = ("What the model does not hold. " +
           "; ".join(g[0].upper() + g[1:] for g in D.GAPS) + ".")

LICENSE = ("BodyParts3D, copyright The Database Center for Life Science, "
           "licensed under CC Attribution-Share Alike 2.1 Japan. The "
           "outlines on this page are a derived work and carry the same "
           "licence.")

CSS = """
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
  --line:#2b2b2b; --accent:#58a6ff; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica,
  Arial, sans-serif; }
.wrap { max-width:1180px; margin:0 auto; padding:26px 20px 60px; }
header.site { display:flex; justify-content:space-between; align-items:baseline;
  gap:16px; flex-wrap:wrap; margin-bottom:18px; }
.brand { font-weight:700; letter-spacing:.14em; color:var(--text);
  text-decoration:none; font-size:14px; }
.brand:hover { color:var(--accent); }
nav.site a { color:var(--muted); text-decoration:none; font-size:14px;
  margin-right:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 10px; font-size:26px; }
.bar { display:flex; gap:7px; align-items:center; flex-wrap:wrap;
  margin-bottom:10px; }
button { font:inherit; font-size:13px; padding:5px 12px; border-radius:999px;
  border:1px solid var(--line); background:#1a1a1a; color:var(--text);
  cursor:pointer; }
button:hover { border-color:var(--accent); }
button.on { background:var(--accent); border-color:var(--accent);
  color:#0b0b0b; }
.bar2 { display:flex; gap:14px; align-items:center; flex-wrap:wrap;
  margin-bottom:12px; color:var(--muted); font-size:12.5px; }
.bar2 label { display:flex; gap:8px; align-items:center; }
.bar2 label[hidden] { display:none; }
button.step { padding:2px 9px; font-size:14px; line-height:1.1; }
.bar2 input[type=range]#spin { width:130px; }
#subbar { margin-top:-2px; margin-bottom:10px; }
#subbar button { font-size:12.5px; padding:4px 11px; }
.bar2 input[type=range] { width:190px; accent-color:var(--accent); }
.bar2 input[type=search] { font:inherit; font-size:12.5px; padding:4px 10px;
  border-radius:999px; border:1px solid var(--line); background:#151515;
  color:var(--text); width:190px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
.figcol { flex:1 1 520px; min-width:0; }
#fig { width:100%; }
#fig svg { width:100%; height:auto; max-height:min(1150px, calc(100vh - 190px));
  display:block; touch-action:pan-y; cursor:grab; }
#fig svg.drag { cursor:grabbing; }
#fig svg path { cursor:pointer; }
#fig svg path#hl { fill:none; stroke:#fff; stroke-width:2.4px;
  pointer-events:none; }
.side { flex:0 0 330px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line);
  border-radius:12px; padding:15px; }
#kindTxt { color:var(--muted); font-size:11.5px; letter-spacing:.09em;
  text-transform:uppercase; }
#nameTxt { font-weight:700; font-size:17px; margin:2px 0 4px;
  line-height:1.25; }
#bodyTxt { font-size:13.5px; line-height:1.55; }
#bodyTxt .fma { color:var(--muted); font-size:11.5px; margin-top:8px; }
.facts { margin-top:12px; border-top:1px solid var(--line); padding-top:11px; }
.fact { margin-bottom:11px; }
.fact b { display:block; font-size:15px; font-variant-numeric:tabular-nums; }
.fact .lb { color:var(--muted); font-size:11.5px; letter-spacing:.04em;
  text-transform:uppercase; }
.fact .nt { font-size:12.5px; color:#b0b0b0; line-height:1.5; margin-top:3px; }
#list { margin-top:12px; max-height:320px; overflow-y:auto;
  border-top:1px solid var(--line); padding-top:8px; }
#list div { font-size:12.5px; padding:2px 4px; border-radius:5px;
  cursor:pointer; color:#b9bec6; }
#list div:hover, #list div.hi { background:#232a33; color:var(--text); }
#list .cnt { color:var(--muted); font-size:11.5px; padding:0 4px 6px;
  cursor:default; }
#list .cnt:hover { background:none; }
.note { color:var(--muted); font-size:12.5px; margin-top:22px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.method { color:var(--muted); font-size:12.5px; margin-top:14px;
  max-width:760px; }
.method summary { cursor:pointer; color:var(--accent); }
.method p { margin:9px 0 0; }
.refs { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.refs p { margin:0 0 8px; overflow-wrap:anywhere; }
.refs a { color:var(--accent); }
__APACSS__
h2.refh { font-size:15px; margin:26px 0 8px; }
@media (max-width:900px){ .stage{flex-direction:column;}
  .side{position:static; width:100%; flex:none;} }
"""

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Human Body &middot; Altazor</title>
<meta name="description" content="The systems of the human body, every
outline traced from the BodyParts3D meshes of one segmented adult.">
<style>__CSS__</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library &middot; Homo
  Sapiens</a> <a href="temperature.html">Temperature</a>
  <a href="migration.html">Migration</a>
  <a href="hominins.html">Hominins</a></nav>
</header>
<h1>The Human Body</h1>
<div class="bar" id="bar"></div>
<div class="bar" id="subbar" hidden></div>
<div class="bar2">
  <label>Turn <button id="spinL" class="step">&#8592;</button>
  <input type="range" id="spin" min="0" max="7" value="0">
  <button id="spinR" class="step">&#8594;</button>
  <span id="spinTxt"></span></label>
  <label id="cutWrap">Cut from the front <input type="range" id="depth"
  min="0" max="100" value="100"> <span id="depthTxt"></span></label>
  <label><input type="checkbox" id="outline" checked> Body outline</label>
  <label><input type="search" id="q" placeholder="Find a part"></label>
  <button id="home">Whole body</button><span id="zoomTxt"></span>
</div>
<div class="stage">
  <div class="figcol"><div id="fig"></div></div>
  <div class="side"><div class="card">
    <div id="kindTxt"></div>
    <div id="nameTxt"></div>
    <div id="bodyTxt"></div>
    <div class="facts" id="factTxt"></div>
    <div id="list"></div>
  </div></div>
</div>
<p class="note">__NOTE1__</p>
<p class="note" style="border-top:none; padding-top:0;">__NOTE2__</p>
<div class="method"><details><summary>How the outlines were made</summary>
<p>__METHOD__</p><p>__GAPNOTE__</p><p>__LICENSE__</p></details></div>
<div class="method"><details><summary>How the nerves were made</summary>
<p>__NERVENOTE__</p></details></div>
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</div>
<script>
const P=__PATHS__, S=__SYS__, F=__FACTS__, N=__NOTES__, W=__WHOLE__;
const LOOK=__LOOK__, NERVES=__NERVES__, NGROUPS=__NGROUPS__, NBLURB=__NBLURB__;
const SC=P.scale, BOX=P.box;
const NS='http://www.w3.org/2000/svg';
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');

// the rings arrive as signed deltas on a quarter millimetre grid, five
// bits to a character
function decode(s){
  let i=0,px=0,py=0,d='';
  while(i<s.length){
    const v=[];
    for(let k=0;k<2;k++){
      let sh=0,res=0,b;
      do{ b=s.charCodeAt(i++)-63; res|=(b&0x1f)<<sh; sh+=5; }while(b>=0x20);
      v.push((res&1)?~(res>>1):(res>>1));
    }
    px+=v[0]; py+=v[1];
    d+=(d?'L':'M')+(px/SC).toFixed(1)+' '+(py/SC).toFixed(1);
  }
  return d+'Z';
}

// [fma, name, system, [front depth per angle], [area per angle],
//  [rings per angle]]
const PARTS=P.parts.map(p=>({fma:p[0],name:p[1],sys:p[2],fs:p[3],as:p[4],
  ds:p[5].map(rings=>rings.map(decode).join(''))}));
const BY={all:PARTS};
PARTS.forEach(p=>(BY[p.sys]=BY[p.sys]||[]).push(p));
const SKIN=PARTS.filter(p=>p.name==='skin');

// Eight views, four of them traced. The other four are those four seen
// from behind, which for an orthographic silhouette is the same outline
// mirrored left to right with the stacking order reversed.
const NANG=P.angles.length, NVIEW=NANG*2;
const TURN=['From the front','Right three-quarter front','Right side',
            'Right three-quarter back','From the back',
            'Left three-quarter back','Left side','Left three-quarter front'];
function slot(){ return spin % NANG; }
function flipped(){ return spin >= NANG; }
// the far half of the turn is the traced outline mirrored left to right
const MIRROR=/([ML])(-?[\d.]+) (-?[\d.]+)/g;
function mirror(d){
  return d.replace(MIRROR,(m,c,x,y)=>c+(-parseFloat(x)).toFixed(1)+' '+y);
}
function partD(p){
  const i=slot();
  if(!flipped()) return p.ds[i];
  p.dm=p.dm||{};
  if(p.dm[i]===undefined) p.dm[i]=mirror(p.ds[i]);
  return p.dm[i];
}
function partF(p){ return flipped() ? -p.fs[slot()] : p.fs[slot()]; }
function partA(p){ return p.as[slot()]; }

// the drawn nerves are real 3D lines, so they project straight
function proj(pt){
  const th=spin*(Math.PI*2/NVIEW), ct=Math.cos(th), st=Math.sin(th);
  return [pt[0]*ct-pt[1]*st, -pt[2], pt[0]*st+pt[1]*ct];
}
const NCOLOR={cns:'#d7a7ff', periph:'#8fd0ff', cranial:'#ffd27f',
              symp:'#ff8f8f', para:'#7fe3b0'};

let cur=S[0][0], sub='all', spin=0, cut=1, pinned=null, hot=null;
const HOME=[BOX[0]-8, BOX[1]-8, BOX[2]-BOX[0]+16, BOX[3]-BOX[1]+16];
let VB=HOME.slice();
// screen y is minus the height above the floor, so a band of the body is
// written back to front here
const REGION={
  cranial:[-150,-1610,300,200],
  cns:[-210,-1600,420,780],
  symp:[-230,-1570,460,750],
  para:[-240,-1590,480,840],
};
function fitTo(r){ VB = r ? r.slice() : HOME.slice(); }

function hsv(h,s,v){
  h=((h%360)+360)%360/60; const c=v*s, x=c*(1-Math.abs(h%2-1)), m=v-c;
  const t=[[c,x,0],[x,c,0],[0,c,x],[0,x,c],[x,0,c],[c,0,x]][Math.floor(h)%6];
  return 'rgb('+t.map(u=>Math.round((u+m)*255)).join(',')+')';
}
function jitter(fma){ let h=0; for(const c of fma) h=(h*31+c.charCodeAt(0))%997;
  return h/997; }

function shade(p, lo, hi){
  const [h,s]=LOOK[p.sys], j=jitter(p.fma);
  const t=(partF(p)-lo)/Math.max(1e-9,hi-lo);
  const v=Math.max(0.2,Math.min(0.98,0.93-0.44*t+0.06*(j-0.5)));
  return [hsv(h+14*(j-0.5),s,v), hsv(h+14*(j-0.5),s,v*0.4)];
}

// on the nervous system the meshes are only the brain, and which of them
// belong depends on the part of the system being shown
function meshesFor(){
  if(cur!=='nervous') return (BY[cur]||[]).slice();
  if(sub==='all'||sub==='cns'||sub==='cranial') return BY.nervous.slice();
  return [];                       // the autonomic views are lines only
}

// A drawn nerve floating in an empty outline says nothing. Each view of
// the nervous system gets the bones or the organs it runs against, drawn
// faintly and not clickable, so the reader can see what it is aimed at.
const CONTEXT={
  all:      [/vertebra$/, /^sacrum$/, /^atlas$/, /^axis$/],
  cns:      [/vertebra$/, /^sacrum$/, /^atlas$/, /^axis$/,
             /intervertebral disk/],
  periph:   [/vertebra$/, /^sacrum$/, /^atlas$/, /^axis$/, /^(left|right) (hip bone|clavicle|scapula|humerus|radius|ulna|femur|tibia|fibula)$/,
             / rib$/],
  cranial:  [/^(frontal|occipital|parietal|temporal|sphenoid|nasal|lacrimal|zygomatic|palatine) bone$/,
             /^(left|right) (parietal|temporal|nasal|lacrimal|zygomatic|palatine) bone$/,
             /^ethmoid$/, /^vomer$/, /^mandible$/, /^hyoid bone$/,
             /^(left|right) maxilla$/, /^(left|right) eyeball$/, /^eyeball$/,
             /^ear$/, /^atlas$/, /^axis$/, /tooth$/],
  symp:     [/vertebra$/, /^sacrum$/, /^wall of heart$/, /lobe of lung$/,
             /^stomach$/, /^(left|right) kidney$/,
             /^(left|right) adrenal gland$/, /^colon, nsn$/, /^liver$/],
  para:     [/vertebra$/, /^sacrum$/, /^wall of heart$/, /lobe of lung$/,
             /^stomach$/, /^colon, nsn$/, /^urinary bladder$/,
             /^(left|right) eyeball$/, /^mandible$/, /^rectum$/],
};
function contextFor(){
  if(cur!=='nervous') return [];
  const rx=CONTEXT[sub]||[];
  if(!rx.length) return [];
  return PARTS.filter(p=>p.sys!=='nervous' && rx.some(r=>r.test(p.name)))
              .sort((a,b)=>partF(b)-partF(a));
}

function visible(){
  let ps=meshesFor();
  if(!ps.length) return ps;
  const fs=ps.map(partF), lo=Math.min(...fs), hi=Math.max(...fs);
  // the slider takes the front off: at the top every part is in, and
  // lower down the superficial ones come away first
  const line=lo+(hi-lo)*(1-cut)-0.001;
  ps=ps.filter(p=>partF(p)>=line);
  ps.sort((a,b)=>partF(b)-partF(a));    // back first, front last
  return ps;
}

// the nerve paths belonging to the view, projected and depth sorted with
// the meshes so a cord behind a vertebra is drawn behind it
function nervesNow(){
  if(cur!=='nervous') return [];
  return NERVES.filter(n=>sub==='all'||n.g===sub).map((n,i)=>{
    const q=n.p.map(proj);
    return {n, i, pts:q, f:Math.min(...q.map(v=>v[2])),
            mid:q.reduce((a,v)=>[a[0]+v[0]/q.length,a[1]+v[1]/q.length],[0,0])};
  }).sort((a,b)=>b.f-a.f);
}

function draw(){
  const ps=visible();
  const all=meshesFor();
  const fs=all.length?all.map(partF):[0,1];
  const lo=Math.min(...fs), hi=Math.max(...fs);
  const svg=document.createElementNS(NS,'svg');
  svg.setAttribute('viewBox',VB.join(' '));
  svg.setAttribute('role','img');
  svg.setAttribute('aria-label','The human body, '+TURN[spin].toLowerCase()
    +', showing the '+cur+' system');
  if(document.getElementById('outline').checked && cur!=='integumentary'){
    for(const s of SKIN){
      const e=document.createElementNS(NS,'path');
      e.setAttribute('d',partD(s)); e.setAttribute('fill','#191919');
      e.setAttribute('stroke','#333'); e.setAttribute('stroke-width','1px');
      e.setAttribute('vector-effect','non-scaling-stroke');
      e.setAttribute('pointer-events','none');
      svg.appendChild(e);
    }
  }
  // the context first, behind everything, and out of the way of the mouse
  for(const p of contextFor()){
    const e=document.createElementNS(NS,'path');
    e.setAttribute('d',partD(p)); e.setAttribute('fill','#202020');
    e.setAttribute('stroke','#343434'); e.setAttribute('stroke-width','0.7px');
    e.setAttribute('vector-effect','non-scaling-stroke');
    e.setAttribute('fill-rule','nonzero');
    e.setAttribute('pointer-events','none');
    svg.appendChild(e);
  }
  // meshes and nerve lines share one depth order
  const nv=nervesNow();
  const items=ps.map(p=>({kind:'m',p,f:partF(p)}))
    .concat(nv.map(x=>({kind:'n',x,f:x.f})))
    .sort((a,b)=>b.f-a.f);
  for(const it of items){
    if(it.kind==='m'){
      const p=it.p;
      const [fill,line]=shade(p,lo,hi);
      const e=document.createElementNS(NS,'path');
      e.setAttribute('d',partD(p)); e.setAttribute('fill',fill);
      e.setAttribute('stroke',line);
      e.setAttribute('stroke-width', partA(p)>4000?'0.9px':'0.6px');
      e.setAttribute('vector-effect','non-scaling-stroke');
      e.setAttribute('fill-rule','nonzero');
      // in the cranial view the skull and the nerves matter more than the
      // brain filling the middle of it
      e.setAttribute('opacity', cur!=='nervous' ? '1'
        : sub==='cranial' ? '0.5' : (sub==='cns'||sub==='all') ? '1' : '0.45');
      e.dataset.fma=p.fma;
      e.addEventListener('pointerenter',()=>{ hot=p; show(p); mark(p.fma); });
      e.addEventListener('click',()=>{ pinned=(pinned&&pinned.fma===p.fma)
        ?null:p; show(p); mark(p.fma); });
      svg.appendChild(e);
    } else {
      const {n,i,pts}=it.x;
      const col=NCOLOR[n.g];
      if(n.k==='ganglion'){
        const e=document.createElementNS(NS,'circle');
        e.setAttribute('cx',pts[0][0].toFixed(1));
        e.setAttribute('cy',pts[0][1].toFixed(1));
        e.setAttribute('r',(n.w/2).toFixed(1));
        e.setAttribute('fill',col); e.setAttribute('stroke','#111');
        e.setAttribute('stroke-width','0.7px');
        e.setAttribute('vector-effect','non-scaling-stroke');
        e.dataset.nv=i;
        e.addEventListener('pointerenter',()=>{ showN(n); markN(i); });
        e.addEventListener('click',()=>{ showN(n); markN(i); });
        svg.appendChild(e);
      } else {
        const d=pts.map((v,k)=>(k?'L':'M')+v[0].toFixed(1)+' '+v[1].toFixed(1))
          .join(' ');
        const e=document.createElementNS(NS,'path');
        e.setAttribute('d',d); e.setAttribute('fill','none');
        e.setAttribute('stroke',col);
        e.setAttribute('stroke-width',n.w.toFixed(1)+'px');
        e.setAttribute('stroke-linecap','round');
        e.setAttribute('stroke-linejoin','round');
        e.setAttribute('vector-effect','non-scaling-stroke');
        e.dataset.nv=i;
        e.addEventListener('pointerenter',()=>{ showN(n); markN(i); });
        e.addEventListener('click',()=>{ showN(n); markN(i); });
        svg.appendChild(e);
        // a fatter invisible line, so a one pixel nerve is still catchable
        const h=document.createElementNS(NS,'path');
        h.setAttribute('d',d); h.setAttribute('fill','none');
        h.setAttribute('stroke','transparent');
        h.setAttribute('stroke-width','7px');
        h.setAttribute('vector-effect','non-scaling-stroke');
        h.addEventListener('pointerenter',()=>{ showN(n); markN(i); });
        h.addEventListener('click',()=>{ showN(n); markN(i); });
        svg.appendChild(h);
      }
    }
  }
  // the outline of whatever is named rides on top, so a part that is
  // covered still lights up without being moved out of its layer
  const hl=document.createElementNS(NS,'path');
  hl.setAttribute('id','hl');
  hl.setAttribute('vector-effect','non-scaling-stroke');
  svg.appendChild(hl);
  svg.addEventListener('pointerleave',()=>{ hot=null; show(pinned); mark(
    pinned&&pinned.fma); });
  wheelpan(svg);
  const fig=document.getElementById('fig');
  fig.textContent=''; fig.appendChild(svg);
  const line=lo+(hi-lo)*(1-cut);
  document.getElementById('spinTxt').textContent=TURN[spin];
  document.getElementById('cutWrap').hidden = !all.length;
  document.getElementById('depthTxt').textContent =
    cut>=1 ? ps.length+' of '+all.length+' parts'
           : ((line-lo)/10).toFixed(1)+' cm in, '+ps.length+' of '+
             all.length+' parts left';
  list(ps, nv);
}

function markN(i){
  document.querySelectorAll('#fig [data-nv]').forEach(e=>
    e.setAttribute('opacity', e.dataset.nv===String(i) ? '1' : '0.35'));
  const hl=document.getElementById('hl');
  if(hl) hl.setAttribute('d','');
  document.querySelectorAll('#list div').forEach(e=>
    e.classList.toggle('hi', e.dataset.nv===String(i)));
}

function showN(n){
  document.getElementById('kindTxt').textContent =
    (NGROUPS.find(g=>g[0]===n.g)||['','Nervous'])[1];
  document.getElementById('nameTxt').textContent=n.n;
  document.getElementById('bodyTxt').innerHTML='<div>'+esc(n.t)+'</div>'
    +'<div class="fma">Drawn to standard anatomy over the traced skeleton, '
    +'not traced from a scan.</div>';
}

function mark(fma){
  const hl=document.getElementById('hl');
  const p=fma&&PARTS.find(x=>x.fma===fma);
  if(hl) hl.setAttribute('d', p?partD(p):'');
  document.querySelectorAll('#fig [data-nv]').forEach(e=>
    e.setAttribute('opacity','1'));
  document.querySelectorAll('#list div').forEach(e=>
    e.classList.toggle('hi', e.dataset.fma===fma));
  // move the list, never the page
  const row=document.querySelector('#list div.hi');
  const box=document.getElementById('list');
  if(row){
    const a=row.offsetTop, b=a+row.offsetHeight;
    if(a<box.scrollTop) box.scrollTop=a;
    else if(b>box.scrollTop+box.clientHeight)
      box.scrollTop=b-box.clientHeight;
  }
}

// the wheel zooms about the pointer and a drag moves the figure, both by
// rewriting the viewBox, so the outlines stay vector sharp at any scale
function wheelpan(svg){
  const at=ev=>{
    const r=svg.getBoundingClientRect();
    return [VB[0]+(ev.clientX-r.left)/r.width*VB[2],
            VB[1]+(ev.clientY-r.top)/r.height*VB[3]];
  };
  svg.addEventListener('wheel',ev=>{
    ev.preventDefault();
    const [mx,my]=at(ev);
    const k=Math.exp(ev.deltaY*0.0016);
    const w=Math.min(HOME[2]*1.4, Math.max(HOME[2]/26, VB[2]*k));
    const s=w/VB[2];
    VB=[mx-(mx-VB[0])*s, my-(my-VB[1])*s, VB[2]*s, VB[3]*s];
    svg.setAttribute('viewBox',VB.join(' '));
    zoomTxt();
  },{passive:false});
  let from=null;
  svg.addEventListener('pointerdown',ev=>{
    // a finger scrolls the page; only a mouse drags the figure
    if(ev.pointerType!=='mouse') return;
    from=[at(ev),VB.slice()]; svg.classList.add('drag');
    svg.setPointerCapture(ev.pointerId);
  });
  svg.addEventListener('pointermove',ev=>{
    if(!from) return;
    const r=svg.getBoundingClientRect();
    const [p0,v0]=from;
    const mx=v0[0]+(ev.clientX-r.left)/r.width*v0[2];
    const my=v0[1]+(ev.clientY-r.top)/r.height*v0[3];
    VB=[v0[0]+(p0[0]-mx), v0[1]+(p0[1]-my), v0[2], v0[3]];
    svg.setAttribute('viewBox',VB.join(' '));
  });
  const up=ev=>{ from=null; svg.classList.remove('drag'); };
  svg.addEventListener('pointerup',up);
  svg.addEventListener('pointercancel',up);
}
function zoomTxt(){
  const z=HOME[2]/VB[2];
  document.getElementById('zoomTxt').textContent =
    z>1.02 ? z.toFixed(1)+' times' : '';
}

function sysrow(){ return S.find(s=>s[0]===cur); }

function show(p){
  const row=sysrow();
  const k=document.getElementById('kindTxt');
  const n=document.getElementById('nameTxt');
  const b=document.getElementById('bodyTxt');
  if(!p){
    if(cur==='nervous'){
      k.textContent='Nervous system';
      n.textContent=(NGROUPS.find(g=>g[0]===sub)||['','']) [1];
      b.innerHTML=esc(NBLURB[sub]||'');
      return;
    }
    k.textContent=cur==='all'?'Every system':'System';
    n.textContent=row?row[1]:'Every system';
    b.innerHTML=esc(row?row[2]:'');
    return;
  }
  k.textContent=(sysrow()||['','',''])[1];
  n.textContent=p.name.charAt(0).toUpperCase()+p.name.slice(1);
  const key=Object.keys(N).find(x=>p.name.indexOf(x)>=0);
  b.innerHTML=(key?'<div>'+esc(N[key])+'</div>':'')
    +'<div class="fma">FMA'+esc(p.fma)+
    ' &middot; frontmost point '+((partF(p)-BOXF)/10).toFixed(1)+
    ' cm behind the front, in this view</div>';
}
const BOXF=Math.min(...PARTS.map(p=>Math.min(...p.fs)));

function facts(){
  const f=(cur==='nervous'? (F.nervous||[]) : (F[cur]||[]));
  document.getElementById('factTxt').innerHTML=f.map(x=>
    '<div class="fact"><b>'+esc(x[0])+'</b><span class="lb">'+esc(x[1])+
    '</span><div class="nt">'+esc(x[2])+'</div></div>').join('')
    || '<div class="fact"><div class="nt">No figure on this page is drawn '
       +'from the model itself.</div></div>';
}

function list(ps, nv){
  const q=document.getElementById('q').value.trim().toLowerCase();
  const el=document.getElementById('list');
  let rows=ps.slice().sort((a,b)=>a.name.localeCompare(b.name));
  if(q) rows=rows.filter(p=>p.name.toLowerCase().indexOf(q)>=0);
  let nrows=(nv||[]).slice().sort((a,b)=>a.n.n.localeCompare(b.n.n));
  if(q) nrows=nrows.filter(x=>x.n.n.toLowerCase().indexOf(q)>=0);
  el.innerHTML='<div class="cnt">'+(rows.length+nrows.length)
    +' drawn</div>'+
    nrows.map(x=>'<div data-nv="'+x.i+'">'+esc(x.n.n)+'</div>').join('')+
    rows.map(p=>'<div data-fma="'+esc(p.fma)+'">'+esc(p.name)+'</div>').join('');
  el.querySelectorAll('div[data-nv]').forEach(e=>{
    e.addEventListener('pointerenter',()=>{
      const i=+e.dataset.nv; showN(NERVES[i]); markN(i); });
  });
  el.querySelectorAll('div[data-fma]').forEach(e=>{
    e.addEventListener('pointerenter',()=>{
      const p=PARTS.find(x=>x.fma===e.dataset.fma); show(p); mark(p.fma); });
  });
}

function pick(k){
  cur=k; cut=1; pinned=null;
  if(k!=='nervous') sub='all';
  document.getElementById('depth').value=100;
  document.querySelectorAll('#bar button').forEach(b=>
    b.classList.toggle('on', b.dataset.k===k));
  const sb=document.getElementById('subbar');
  sb.hidden = (k!=='nervous');
  if(k==='nervous'){ fitTo(REGION[sub]); subButtons(); }
  else fitTo(null);
  draw(); facts(); show(null);
}

function subButtons(){
  const sb=document.getElementById('subbar');
  sb.textContent='';
  for(const [g,label] of NGROUPS){
    const b=document.createElement('button');
    b.textContent=label; b.dataset.g=g;
    b.classList.toggle('on', g===sub);
    b.addEventListener('click',()=>{ sub=g; pinned=null;
      fitTo(REGION[g]); subButtons(); draw(); zoomTxt(); show(null); });
    sb.appendChild(b);
  }
}

function setSpin(v){
  spin=((v%NVIEW)+NVIEW)%NVIEW;
  document.getElementById('spin').value=spin;
  draw(); if(pinned) { show(pinned); mark(pinned.fma); }
}

const bar=document.getElementById('bar');
for(const [k,label] of S.map(s=>[s[0],s[1]])){
  const b=document.createElement('button');
  b.textContent=label; b.dataset.k=k;
  b.addEventListener('click',()=>pick(k));
  bar.appendChild(b);
}
document.getElementById('spin').max=NVIEW-1;
document.getElementById('spin').addEventListener('input',e=>
  setSpin(+e.target.value));
document.getElementById('spinL').addEventListener('click',()=>setSpin(spin-1));
document.getElementById('spinR').addEventListener('click',()=>setSpin(spin+1));
document.getElementById('depth').addEventListener('input',e=>{
  cut=e.target.value/100; draw(); });
document.getElementById('outline').addEventListener('change',draw);
document.getElementById('home').addEventListener('click',()=>{
  VB=HOME.slice(); draw(); zoomTxt(); });
document.getElementById('q').addEventListener('input',()=>
  list(visible(), nervesNow()));
pick(S[0][0]);
</script>
</body>
</html>
"""


def main():
    counts = {}
    for p in PATHS["parts"]:
        counts[p[2]] = counts.get(p[2], 0) + 1
    sysrows = [[k, f"{lab}", blurb] for k, lab, blurb in D.SYSTEMS
               if counts.get(k)]
    sysrows.append(["all", "Everything", (
        "Every part the model holds, stacked by depth. The skin is drawn "
        "first and everything else sits inside it, so what shows is what a "
        "front view of the whole body would show.")])
    data = PATHS
    look = dict(LOOK)
    facts = dict(D.FACTS)
    facts["all"] = D.WHOLE

    html = (HTML
            .replace("__CSS__", CSS.replace("__APACSS__", apa.CSS))
            .replace("__NOTE1__", NOTE1)
            .replace("__NOTE2__", NOTE2)
            .replace("__METHOD__", METHOD)
            .replace("__GAPNOTE__", GAPNOTE)
            .replace("__NERVENOTE__", NERVENOTE)
            .replace("__LICENSE__", LICENSE)
            .replace("__REFS__", apa.render(D.REFS))
            .replace("__PATHS__", json.dumps(data, separators=(",", ":")))
            .replace("__SYS__", json.dumps(sysrows, separators=(",", ":")))
            .replace("__FACTS__", json.dumps(facts, separators=(",", ":")))
            .replace("__NOTES__", json.dumps(D.NOTES, separators=(",", ":")))
            .replace("__WHOLE__", json.dumps(D.WHOLE, separators=(",", ":")))
            .replace("__LOOK__", json.dumps(look, separators=(",", ":")))
            .replace("__NERVES__", json.dumps(NV.NERVES,
                                              separators=(",", ":")))
            .replace("__NGROUPS__", json.dumps(NV.GROUPS,
                                               separators=(",", ":")))
            .replace("__NBLURB__", json.dumps(NV.BLURB,
                                              separators=(",", ":"))))
    out = ROOT / "body.html"
    out.write_text(html, encoding="utf-8")
    print(f"body.html  {len(PATHS['parts'])} parts x "
          f"{len(PATHS['angles'])} traced angles, {len(sysrows)} systems, "
          f"{len(NV.NERVES)} nerve paths, {out.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
