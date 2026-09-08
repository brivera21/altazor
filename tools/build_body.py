#!/usr/bin/env python3
"""Generate body.html, the systems of the human body.

Every outline is traced from a mesh. BodyParts3D segmented one adult male
into named anatomical parts, and each part here is its own mesh projected
to an anterior orthographic view and traced at the silhouette. Nothing on
the figure is drawn by hand, and nothing is drawn from a photograph.

The tracing runs in tools/pack_body.py, from meshes fetched once. Its
output, tools/data/body_paths.json, is checked in so this builder needs
neither the network nor the 1.3 GB of meshes.

The numbers beside each system do not come from the model. They come from
the literature, and several of the familiar ones turn out to rest on
nothing measured, which is said where it applies.

Data: tools/body_data.py, tools/data/body_paths.json.

Usage: python3 build_body.py
"""

import json
from pathlib import Path

import apa
import body_data as D

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

NOTE1 = ("Every outline here is traced from a mesh. BodyParts3D cut one "
         "adult male into named parts, and each part on the figure is its "
         "own mesh, projected to a front view and traced at its edge. "
         "Nothing is drawn by hand or from a photograph. The buttons choose "
         "a system, and the cut puts a plane through the body and drops "
         "everything in front of it, so the superficial muscles come away "
         "from the ones underneath.")

NOTE2 = ("The model is one body, and it carries that body's gaps. It has no "
         "lymph vessels and no nodes, no spinal cord and no peripheral "
         "nerves beyond the two optic nerves, and it is male. The counts "
         "beside each system come from the literature instead, where four "
         "of the most repeated figures turn out to have no measurement "
         "behind them at all.")

METHOD = (
    "How the figure was made. Each part is a separate closed surface in "
    "BodyParts3D, keyed to a term in the Foundational Model of Anatomy. "
    "Every triangle was projected along the front to back axis, filled by "
    "scanline into a raster at between 1.4 and 8 pixels per millimetre "
    "depending on the size of the part, and the silhouette of that raster "
    "traced and reduced to a polygon. What is drawn is therefore the true "
    "outline of the part as seen from directly in front, at about a "
    "quarter of a millimetre, and not an artist's reading of it. Parts are "
    "stacked by the depth of their frontmost point, so what covers what on "
    "the figure is what covers what in the body. The 925 parts here are "
    "the ones with a mesh in the database, out of 1,513 named terms.")

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
<div class="bar2">
  <label>Cut from the front <input type="range" id="depth" min="0" max="100"
  value="100"> <span id="depthTxt"></span></label>
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
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</div>
<script>
const P=__PATHS__, S=__SYS__, F=__FACTS__, N=__NOTES__, W=__WHOLE__;
const LOOK=__LOOK__;
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

// [fma, name, system, median depth, front depth, area, rings]
const PARTS=P.parts.map(p=>({fma:p[0],name:p[1],sys:p[2],d:p[3],f:p[4],
  a:p[5],d2:p[6].map(decode).join('')}));
const BY={all:PARTS};
PARTS.forEach(p=>(BY[p.sys]=BY[p.sys]||[]).push(p));
const SKIN=PARTS.filter(p=>p.name==='skin');

let cur=S[0][0], cut=1, pinned=null, hot=null;
const HOME=[BOX[0]-8, BOX[1]-8, BOX[2]-BOX[0]+16, BOX[3]-BOX[1]+16];
let VB=HOME.slice();

function hsv(h,s,v){
  h=((h%360)+360)%360/60; const c=v*s, x=c*(1-Math.abs(h%2-1)), m=v-c;
  const t=[[c,x,0],[x,c,0],[0,c,x],[0,x,c],[x,0,c],[c,0,x]][Math.floor(h)%6];
  return 'rgb('+t.map(u=>Math.round((u+m)*255)).join(',')+')';
}
function jitter(fma){ let h=0; for(const c of fma) h=(h*31+c.charCodeAt(0))%997;
  return h/997; }

function shade(p, lo, hi){
  const [h,s]=LOOK[p.sys], j=jitter(p.fma);
  const t=(p.f-lo)/Math.max(1e-9,hi-lo);
  const v=Math.max(0.2,Math.min(0.98,0.93-0.44*t+0.06*(j-0.5)));
  return [hsv(h+14*(j-0.5),s,v), hsv(h+14*(j-0.5),s,v*0.4)];
}

function visible(){
  let ps=(BY[cur]||[]).slice();
  if(!ps.length) return ps;
  const fs=ps.map(p=>p.f), lo=Math.min(...fs), hi=Math.max(...fs);
  // the slider takes the front off: at the top every part is in, and
  // lower down the superficial ones come away first
  const line=lo+(hi-lo)*(1-cut)-0.001;
  ps=ps.filter(p=>p.f>=line);
  ps.sort((a,b)=>b.f-a.f);           // back first, front last
  return ps;
}

function draw(){
  const ps=visible();
  const all=(BY[cur]||[]);
  const fs=all.map(p=>p.f), lo=Math.min(...fs), hi=Math.max(...fs);
  const svg=document.createElementNS(NS,'svg');
  svg.setAttribute('viewBox',VB.join(' '));
  svg.setAttribute('role','img');
  svg.setAttribute('aria-label','The human body seen from the front, '
    +'showing the '+cur+' system');
  if(document.getElementById('outline').checked && cur!=='integumentary'){
    for(const s of SKIN){
      const e=document.createElementNS(NS,'path');
      e.setAttribute('d',s.d2); e.setAttribute('fill','#191919');
      e.setAttribute('stroke','#333'); e.setAttribute('stroke-width','1px');
      e.setAttribute('vector-effect','non-scaling-stroke');
      e.setAttribute('pointer-events','none');
      svg.appendChild(e);
    }
  }
  for(const p of ps){
    const [fill,line]=shade(p,lo,hi);
    const e=document.createElementNS(NS,'path');
    e.setAttribute('d',p.d2); e.setAttribute('fill',fill);
    e.setAttribute('stroke',line);
    e.setAttribute('stroke-width', p.a>4000?'0.9px':'0.6px');
    e.setAttribute('vector-effect','non-scaling-stroke');
    e.setAttribute('fill-rule','nonzero');
    e.dataset.fma=p.fma;
    e.addEventListener('pointerenter',()=>{ hot=p; show(p); mark(p.fma); });
    e.addEventListener('click',()=>{ pinned=(pinned&&pinned.fma===p.fma)
      ?null:p; show(p); mark(p.fma); });
    svg.appendChild(e);
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
  document.getElementById('depthTxt').textContent =
    cut>=1 ? ps.length+' of '+all.length+' parts'
           : ((line-lo)/10).toFixed(1)+' cm in, '+ps.length+' of '+
             all.length+' parts left';
  list(ps);
}

function mark(fma){
  const hl=document.getElementById('hl');
  const p=fma&&PARTS.find(x=>x.fma===fma);
  if(hl) hl.setAttribute('d', p?p.d2:'');
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
    ' &middot; frontmost point '+((p.f-BOXF)/10).toFixed(1)+
    ' cm behind the front of the body</div>';
}
const BOXF=Math.min(...PARTS.map(p=>p.f));

function facts(){
  const f=F[cur]||[];
  document.getElementById('factTxt').innerHTML=f.map(x=>
    '<div class="fact"><b>'+esc(x[0])+'</b><span class="lb">'+esc(x[1])+
    '</span><div class="nt">'+esc(x[2])+'</div></div>').join('')
    || '<div class="fact"><div class="nt">No figure on this page is drawn '
       +'from the model itself.</div></div>';
}

function list(ps){
  const q=document.getElementById('q').value.trim().toLowerCase();
  const el=document.getElementById('list');
  let rows=ps.slice().sort((a,b)=>a.name.localeCompare(b.name));
  if(q) rows=rows.filter(p=>p.name.toLowerCase().indexOf(q)>=0);
  el.innerHTML='<div class="cnt">'+rows.length+' parts drawn</div>'+
    rows.map(p=>'<div data-fma="'+esc(p.fma)+'">'+esc(p.name)+'</div>').join('');
  el.querySelectorAll('div[data-fma]').forEach(e=>{
    e.addEventListener('pointerenter',()=>{
      const p=PARTS.find(x=>x.fma===e.dataset.fma); show(p); mark(p.fma); });
  });
}

function pick(k){
  cur=k; cut=1; pinned=null;
  document.getElementById('depth').value=100;
  document.querySelectorAll('#bar button').forEach(b=>
    b.classList.toggle('on', b.dataset.k===k));
  draw(); facts(); show(null);
}

const bar=document.getElementById('bar');
for(const [k,label] of S.map(s=>[s[0],s[1]])){
  const b=document.createElement('button');
  b.textContent=label; b.dataset.k=k;
  b.addEventListener('click',()=>pick(k));
  bar.appendChild(b);
}
document.getElementById('depth').addEventListener('input',e=>{
  cut=e.target.value/100; draw(); });
document.getElementById('outline').addEventListener('change',draw);
document.getElementById('home').addEventListener('click',()=>{
  VB=HOME.slice(); draw(); zoomTxt(); });
document.getElementById('q').addEventListener('input',()=>list(visible()));
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
            .replace("__LICENSE__", LICENSE)
            .replace("__REFS__", apa.render(D.REFS))
            .replace("__PATHS__", json.dumps(data, separators=(",", ":")))
            .replace("__SYS__", json.dumps(sysrows, separators=(",", ":")))
            .replace("__FACTS__", json.dumps(facts, separators=(",", ":")))
            .replace("__NOTES__", json.dumps(D.NOTES, separators=(",", ":")))
            .replace("__WHOLE__", json.dumps(D.WHOLE, separators=(",", ":")))
            .replace("__LOOK__", json.dumps(look, separators=(",", ":"))))
    out = ROOT / "body.html"
    out.write_text(html, encoding="utf-8")
    print(f"body.html  {len(PATHS['parts'])} parts, {len(sysrows)} systems, "
          f"{out.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
