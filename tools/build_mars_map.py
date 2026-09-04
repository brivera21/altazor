#!/usr/bin/env python3
"""Generate red-mars.html, The Mars of Red Mars.

The real planet under the novel: a MOLA-based global image with the canyon
system labeled from the USGS Gazetteer, and the places of Kim Stanley
Robinson's Red Mars marked where the book puts them, each with a card saying
what the book gets right there. The wheel zooms at the cursor, dragging pans,
and a native-resolution strip of Valles Marineris fades in up close.

Usage: python3 build_mars_map.py
"""

import base64
import json
import apa
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE.parent / "red-mars.html"

g64 = base64.b64encode((HERE / "data/mars_global.jpg").read_bytes()).decode()
v64 = base64.b64encode((HERE / "data/mars_vm.jpg").read_bytes()).decode()

W, H = 2400, 1200
def XY(lat, lon_e):
    return (round(((lon_e + 180) % 360) / 360 * W, 1),
            round((90 - lat) / 180 * H, 1))

# the high-res strip covers lat +10..-22, lon 240..332 E
VX0, VY0 = XY(10, 240)
VX1, VY1 = XY(-22, 332)

# where the low-zoom summary label sits, over the canyon cluster
SUMX, SUMY = XY(6.5, 288)

# name, lat, lonE, length km (USGS Gazetteer), note
CANYONS = [
    ("Noctis Labyrinthus", -6.36, 258.81, 1190,
     "The maze of intersecting graben where the canyon system begins, on "
     "the east flank of the Tharsis rise."),
    ("Tithonium Chasma", -4.60, 275.71, 803, ""),
    ("Ius Chasma", -7.29, 275.61, 840, ""),
    ("Echus Chasma", 2.47, 280.04, 391, ""),
    ("Hebes Chasma", -1.07, 283.94, 317,
     "A closed canyon with no outlet, holding a mesa nearly as high as its "
     "own rim."),
    ("Ophir Chasma", -4.00, 287.65, 315, ""),
    ("Candor Chasma", -6.53, 289.22, 811, ""),
    ("Melas Chasma", -10.52, 287.46, 564,
     "The widest and deepest part of the system."),
    ("Coprates Chasma", -13.37, 299.26, 958,
     "The long straight trunk of the system."),
    ("Juventae Chasma", -3.37, 298.61, 305, ""),
    ("Ganges Chasma", -7.96, 312.11, 574, ""),
    ("Capri Chasma", -8.27, 317.93, 1472, ""),
    ("Eos Chasma", -12.15, 320.83, 1306,
     "The eastern outlet, where the canyons give way to the outflow "
     "channels that drained toward Chryse."),
    ("Kasei Valles", 25.14, 297.12, 1580,
     "An outflow channel carved by catastrophic floods, the real precedent "
     "for the novel's aquifer outbursts."),
]

# name, lat, lonE, marker note, book text, what is real
SITES = [
    ("Underhill", 0.2, 286.3,
     "placement approximate",
     "The First Hundred's first settlement, built by Nadia Cherneshevsky "
     "from the landing onward.",
     "The text puts it on the flat plateau northeast of Hebes Chasma, near "
     "Ganges Catena, and the terrain there really is almost perfectly "
     "flat. The book's own map places it a little differently, one of two "
     "such dislocations readers have caught."),
    ("Sheffield", 0.9, 247.04, "",
     "The elevator city on the south rim of Pavonis Mons, and the cable's "
     "anchor until 2061, when the severed cable fell across its domes and "
     "wrapped the equator twice.",
     "Pavonis Mons is real and really is the one great volcano on the "
     "equator, at 1.5 degrees north with its summit about 14 km above "
     "datum: the correct place on the whole planet for an elevator, and "
     "the wrap-twice arithmetic checks out."),
    ("Nicosia", -6.0, 256.5,
     "placement approximate",
     "The first of the tent towns, where the novel opens on festival "
     "night.",
     "East of Tharsis by Noctis Labyrinthus, which fits; its claimed view "
     "of Pavonis Mons does not survive the sightline arithmetic on a "
     "smaller planet."),
    ("Low Point", -42.43, 70.5, "",
     "The mohole sunk at the lowest ground on Mars, drowned in 2061 and "
     "later the heat source under the Hellas Sea.",
     "Hellas really is the deepest basin, its floor about 7 km below "
     "datum, and a future sea there is where the real topography would put "
     "one."),
    ("Burroughs", 10.5, 92.5,
     "placement approximate",
     "The city on the edge of Isidis Planitia that later drowns behind "
     "its own dike.",
     "Isidis is a real impact basin; the text sets the city at one end and "
     "the maps at another, the book's second geographic dislocation."),
    ("Acheron", 38.27, 224.98, "",
     "Vlad and Ursula's biotech lab, where the longevity treatment is "
     "invented.",
     "Acheron Fossae is a real fracture belt on the great escarpment "
     "northwest of Olympus Mons, right where the book puts it."),
    ("Senzeni Na", -40.0, 293.0,
     "placement approximate",
     "The mining mohole in the southern highlands.",
     "Thaumasia is a real highland region south of the canyons, at about "
     "the latitude the book gives."),
    ("The 2061 flood", -13.0, 302.0, "",
     "The revolution's aquifer outbursts sent floods down Valles "
     "Marineris.",
     "Outburst floods carved Mars's real outflow channels, so the "
     "mechanism is genuine; aquifers of the novel's size are doubted by "
     "current evidence, which finds no such confined water under the "
     "InSight site."),
    ("Zygote", -86.0, 15.0, "",
     "Hiroko's hidden colony under the ice of the south pole.",
     "The southern polar cap is real layered ice; the hiding place is the "
     "novel's own invention."),
]

canyons_js = json.dumps(
    [{"n": n, "x": XY(la, lo)[0], "y": XY(la, lo)[1], "km": km, "t": t}
     for n, la, lo, km, t in CANYONS], separators=(",", ":"))
sites_js = json.dumps(
    [{"n": n, "x": XY(la, lo)[0], "y": XY(la, lo)[1], "ap": ap,
      "book": b, "real": r}
     for n, la, lo, ap, b, r in SITES], separators=(",", ":"))

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Mars of Red Mars · Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; --canyon:#6ee7f2; --site:#ffb02e; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
.wrap { max-width:1320px; margin:0 auto; padding:32px 20px 60px; }
header.site { border-top:4px solid var(--accent); padding-top:22px; margin-bottom:26px;
  display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }
.brand { font-weight:700; font-size:20px; letter-spacing:.1em; text-decoration:none; color:var(--text); }
.brand:hover { color:var(--accent); }
nav.site a { color:var(--muted); text-decoration:none; font-size:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 12px; font-size:26px; }
.controls { display:flex; gap:8px; flex-wrap:wrap; align-items:center; margin-bottom:10px; }
.controls button { background:var(--panel); border:1px solid var(--line); color:var(--text);
  padding:7px 13px; border-radius:8px; cursor:pointer; font-size:13.5px; }
.controls button:hover { border-color:var(--accent); }
.controls button.on { border-color:var(--accent); color:var(--accent); }
.controls .info { color:var(--muted); font-size:13px; margin-left:6px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#map { flex:1 1 640px; min-width:0; }
#map svg { width:100%; height:auto; display:block; cursor:grab; user-select:none;
  border-radius:8px; }
#map.panning svg { cursor:grabbing; }
.side { flex:0 0 300px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:16px; }
#kindTxt { font-size:11px; letter-spacing:.08em; text-transform:uppercase;
  color:var(--muted); }
#nameTxt { font-weight:700; font-size:16px; margin:2px 0 6px; }
#bookTxt { color:var(--text); font-size:13.5px; line-height:1.5; }
#realTxt { color:var(--muted); font-size:13px; line-height:1.5; margin-top:8px;
  border-top:1px solid var(--line); padding-top:8px; }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.note a { color:var(--accent); }
.refs { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.refs p { margin:0 0 8px; }
.refs a { color:var(--accent); }
h2.refh { font-size:15px; margin:26px 0 8px; }
@media (max-width:960px){ .stage{flex-direction:column;} .side{position:static; width:100%;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="science-fiction.html">&larr; Science Fiction</a></nav>
</header>
<h1>The Mars of Red Mars</h1>
<div class="controls">
  <button id="bReset">Whole planet</button>
  <button id="bVM">The canyons</button>
  <button id="bCan" class="on">Canyon names</button>
  <button id="bNov" class="on">The novel's places</button>
  <span class="info" id="info"></span>
</div>
<div class="stage">
  <div id="map"></div>
  <div class="side"><div class="card">
    <div id="kindTxt"></div>
    <div id="nameTxt">A mark under the cursor lands here</div>
    <div id="bookTxt"></div>
    <div id="realTxt"></div>
  </div></div>
</div>
<p class="note">The planet is the real one, MOLA-shaded, and the canyon marks
sit at their USGS Gazetteer coordinates: the Valles Marineris system runs
close to 4,000 km, up to about 9 km deep. Amber marks are the novel's places.
The wheel zooms at the cursor, dragging pans, and past a certain closeness
the canyon country sharpens to full resolution.</p>
<p class="note">The book's geography holds up well: Pavonis Mons really is
the equator's one great mountain, Hellas really is the lowest ground, and
outburst floods really carved the outflow channels. Its liberties are marked
on their cards: a sightline that cannot work, two places whose text and map
disagree, and aquifers larger than the current evidence allows.</p>
<h2 class="refh">References</h2>
<div class="refs">
<p>Gazetteer of Planetary Nomenclature. (2026). <i>Mars feature coordinates</i>.
USGS Astrogeology.
<a href="https://planetarynames.wr.usgs.gov/">https://planetarynames.wr.usgs.gov/</a></p>
<p>NASA. (n.d.). <i>Valles Marineris: The Grand Canyon of Mars</i>.
<a href="https://science.nasa.gov/resource/valles-marineris-the-grand-canyon-of-mars/">https://science.nasa.gov/resource/valles-marineris-the-grand-canyon-of-mars/</a></p>
<p>Robinson, K. S. (1992). <i>Red Mars</i>. Bantam Spectra. Locations follow
the KSR wiki.
<a href="https://www.kimstanleyrobinson.info/">https://www.kimstanleyrobinson.info/</a></p>
<p>Handmer, C. (2022-2023). <i>Mars trilogy technical commentary</i>, the
series auditing the novel's geography.
<a href="https://caseyhandmer.wordpress.com/2022/12/13/mars-trilogy-festival-night/">https://caseyhandmer.wordpress.com/2022/12/13/mars-trilogy-festival-night/</a></p>
<p>Surface image: Solar System Scope (CC BY 4.0), built on NASA MGS MOLA and
Viking data.
<a href="https://www.solarsystemscope.com/textures/">https://www.solarsystemscope.com/textures/</a></p>
</div>
</div>
<script>
const CANYONS=__CANYONS__, SITES=__SITES__;
const W=2400,H=1200;
const VM={x:__VX0__,y:__VY0__,w:__VW__,h:__VH__};
const SUM={x:__SUMX__,y:__SUMY__};
let view={x:0,y:0,w:W,h:H};
let showCan=true, showNov=true;
const el=document.getElementById('map');
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');

function K(){ return view.w/W; }
function render(){
  const k=K(), zoom=1/k;
  const fs=Math.max(7,13*k*2.2), r=Math.max(2.2,5*k*2.2);
  let s=`<svg viewBox="${view.x} ${view.y} ${view.w} ${view.h}"
    xmlns="http://www.w3.org/2000/svg" id="marsvg">`;
  s+=`<image href="data:image/jpeg;base64,__G64__" x="0" y="0"
    width="${W}" height="${H}" preserveAspectRatio="none"/>`;
  if(zoom>2.2)
    s+=`<image href="data:image/jpeg;base64,__V64__" x="${VM.x}" y="${VM.y}"
      width="${VM.w}" height="${VM.h}" preserveAspectRatio="none"
      opacity="${Math.min(1,(zoom-2.2)/0.8)}"/>`;
  const named=zoom>=2;
  if(showCan) for(const c of CANYONS){
    s+=`<g data-c="${esc(c.n)}" style="cursor:default">
      <circle cx="${c.x}" cy="${c.y}" r="${r}" fill="none"
        stroke="var(--canyon)" stroke-width="${Math.max(0.8,1.6*k*2.2)}"/>`;
    if(named)
      s+=`<text x="${c.x}" y="${c.y-r-3*k*2.2}" text-anchor="middle"
        font-size="${fs}" fill="var(--canyon)" stroke="#121212"
        stroke-width="${fs/5}" paint-order="stroke"
        pointer-events="none">${esc(c.n)}</text>`;
    s+='</g>';
  }
  if(showCan&&!named)
    s+=`<text id="vmSummary" x="${SUM.x}" y="${SUM.y}" text-anchor="middle"
      font-size="${fs*1.5}" fill="var(--canyon)" stroke="#121212"
      stroke-width="${fs*1.5/5}" paint-order="stroke" letter-spacing="2"
      pointer-events="none">Valles Marineris</text>`;
  if(showNov) for(const p of SITES){
    s+=`<g data-s="${esc(p.n)}" style="cursor:default">
      <rect x="${p.x-r}" y="${p.y-r}" width="${2*r}" height="${2*r}"
        transform="rotate(45 ${p.x} ${p.y})" fill="var(--site)"
        stroke="#121212" stroke-width="${Math.max(0.6,1*k*2.2)}"/>
      <text x="${p.x}" y="${p.y+r+fs}" text-anchor="middle"
        font-size="${fs}" fill="var(--site)" stroke="#121212"
        stroke-width="${fs/5}" paint-order="stroke"
        pointer-events="none">${esc(p.n)}</text></g>`;
  }
  s+='</svg>';
  el.innerHTML=s;
  document.getElementById('info').textContent=
    zoom<1.05?'the whole planet':('closer by '+zoom.toFixed(1)+'\\u00d7');
}
function clampView(v){
  v.w=Math.min(W,Math.max(W/14,v.w)); v.h=v.w/2;
  v.x=Math.max(0,Math.min(W-v.w,v.x));
  v.y=Math.max(0,Math.min(H-v.h,v.y));
  return v;
}
function hook(){
  const pt=e=>{const r=el.getBoundingClientRect();
    return {x:view.x+(e.clientX-r.left)/r.width*view.w,
            y:view.y+(e.clientY-r.top)/r.height*view.h};};
  el.addEventListener('wheel',e=>{
    e.preventDefault();
    const f=e.deltaY>0?1.18:1/1.18, p=pt(e);
    view=clampView({x:p.x-(p.x-view.x)*f, y:p.y-(p.y-view.y)*f,
      w:view.w*f, h:view.h*f});
    render();
  },{passive:false});
  let drag=null;
  el.addEventListener('pointerdown',e=>{drag={p:pt(e)};el.classList.add('panning');el.setPointerCapture(e.pointerId);});
  el.addEventListener('pointermove',e=>{
    if(!drag) return;
    const p=pt(e);
    view=clampView({x:view.x-(p.x-drag.p.x), y:view.y-(p.y-drag.p.y),
      w:view.w, h:view.h});
    render();
  });
  const up=()=>{drag=null;el.classList.remove('panning');};
  el.addEventListener('pointerup',up); el.addEventListener('pointercancel',up);
  el.addEventListener('pointerover',e=>{
    const c=e.target.closest('[data-c]');
    if(c){ showCanyon(c.getAttribute('data-c')); return; }
    const p=e.target.closest('[data-s]');
    if(p){ showSite(p.getAttribute('data-s')); }
  });
}
function showCanyon(n){
  const c=CANYONS.find(x=>x.n===n);
  document.getElementById('kindTxt').textContent='A real canyon';
  document.getElementById('nameTxt').textContent=c.n;
  document.getElementById('bookTxt').textContent=
    'About '+c.km.toLocaleString('en-US')+' km along its longest reach, by '
    +'the USGS Gazetteer.';
  document.getElementById('realTxt').textContent=c.t;
}
function showSite(n){
  const p=SITES.find(x=>x.n===n);
  document.getElementById('kindTxt').textContent=
    'In the novel'+(p.ap?' \\u00b7 '+p.ap:'');
  document.getElementById('nameTxt').textContent=p.n;
  document.getElementById('bookTxt').textContent=p.book;
  document.getElementById('realTxt').textContent=p.real;
}
document.getElementById('bReset').onclick=()=>{view={x:0,y:0,w:W,h:H};render();};
document.getElementById('bVM').onclick=()=>{
  view=clampView({x:VM.x-40,y:VM.y-40,w:VM.w+80,h:(VM.w+80)/2});render();};
document.getElementById('bCan').onclick=e=>{
  showCan=!showCan;e.target.classList.toggle('on',showCan);render();};
document.getElementById('bNov').onclick=e=>{
  showNov=!showNov;e.target.classList.toggle('on',showNov);render();};
render();
showSite('Sheffield');
hook();
window.__mars=()=>({view,canyons:CANYONS.length,sites:SITES.length,
  zoom:W/view.w,showCan,showNov,named:W/view.w>=2});
</script>
</body>
</html>
"""

html = (HTML.replace("__CANYONS__", canyons_js).replace("__SITES__", sites_js)
        .replace("__VX0__", str(VX0)).replace("__VY0__", str(VY0))
        .replace("__VW__", str(round(VX1 - VX0, 1)))
        .replace("__VH__", str(round(VY1 - VY0, 1)))
        .replace("__SUMX__", str(SUMX)).replace("__SUMY__", str(SUMY))
        .replace("__G64__", g64).replace("__V64__", v64))
html = apa.css_pass(html)
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} bytes): {len(CANYONS)} canyons, "
      f"{len(SITES)} novel sites")
