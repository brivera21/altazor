#!/usr/bin/env python3
"""Generate matter.html, Matter: the periodic table with photographs.

The 118 confirmed elements on the standard 18-column grid, colored by family.
The element under the cursor fills a side card with a photograph of the real
substance, the way the film timelines show posters. Element data comes from
the Periodic-Table-JSON dataset (CC BY-SA 3.0), trimmed at build time to the
fields the page uses; Cesium is respelled Caesium to match IUPAC. Photographs
are hotlinked at view time from Wikimedia Commons and images-of-elements.com
with each picture's own attribution shown in the card; none are stored in the
repo. Synthetic elements without a photograph say so.

Usage: python3 build_matter.py
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE.parent / "matter.html"

raw = json.loads((HERE / "periodic_table.json").read_text(encoding="utf-8"))
els = [e for e in raw["elements"] if e["number"] <= 118]
assert len(els) == 118

# IUPAC spelling: the dataset's one deviation
for e in els:
    if e["name"] == "Cesium":
        e["name"] = "Caesium"

FAMILIES = [
    ("alkali metal", "Alkali metals", "#ff5c4d"),
    ("alkaline earth metal", "Alkaline earth metals", "#ffb02e"),
    ("transition metal", "Transition metals", "#58a6ff"),
    ("post-transition metal", "Post-transition metals", "#6ee7f2"),
    ("metalloid", "Metalloids", "#2fc6a6"),
    ("nonmetal", "Nonmetals", "#31d67a"),
    ("noble gas", "Noble gases", "#b48cf2"),
    ("lanthanide", "Lanthanides", "#f28cb0"),
    ("actinide", "Actinides", "#d1548e"),
    ("unknown", "Not yet measured", "#8b93a7"),
]


def family(cat):
    if cat in ("diatomic nonmetal", "polyatomic nonmetal"):
        return "nonmetal"
    if cat.startswith("unknown"):
        return "unknown"
    return cat


for e in els:
    assert family(e["category"]) in {f for f, _l, _c in FAMILIES}, e["category"]

NO_PHOTO = "transactinoid"  # the dataset's placeholder image for synthetics


def entry(e):
    img = e.get("image") or {}
    url = img.get("url") or ""
    if NO_PHOTO in url:
        url, att = "", ""
    else:
        att = (img.get("attribution") or "").replace(
            "Hi-Res Images ofChemical Elements",
            "Hi-Res Images of Chemical Elements")
    summ = (e.get("summary") or "").strip()
    if len(summ) > 300:
        summ = summ[:297].rsplit(" ", 1)[0] + "…"
    return {
        "n": e["name"], "s": e["symbol"], "z": e["number"],
        "f": family(e["category"]), "cat": e["category"],
        "m": round(e["atomic_mass"], 3), "ph": e["phase"],
        "ap": (e.get("appearance") or "").strip(),
        "x": e["xpos"], "y": e["ypos"],
        "img": url, "att": att, "sum": summ,
    }


data = [entry(e) for e in els]
n_photo = sum(1 for d in data if d["img"])
els_js = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
fam_js = json.dumps([{"k": k, "l": l, "c": c} for k, l, c in FAMILIES],
                    separators=(",", ":"))

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Matter · Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
.wrap { max-width:1360px; margin:0 auto; padding:32px 20px 60px; }
header.site { border-top:4px solid var(--accent); padding-top:22px; margin-bottom:26px;
  display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }
.brand { font-weight:700; font-size:20px; letter-spacing:.1em; text-decoration:none; color:var(--text); }
.brand:hover { color:var(--accent); }
nav.site a { color:var(--muted); text-decoration:none; font-size:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 12px; font-size:26px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#table { flex:1 1 700px; min-width:0; display:grid;
  grid-template-columns:repeat(18, 1fr); gap:3px; }
.cell { aspect-ratio:1/1.06; border-radius:5px; border:1px solid transparent;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  cursor:default; padding:1px; min-width:0; }
.cell .z { font-size:9px; line-height:1.1; opacity:0.75; color:#0b0b0b; }
.cell .sy { font-size:15px; font-weight:700; line-height:1.15; color:#0b0b0b; }
.cell.dim { opacity:0.25; }
.cell.sel { outline:2px solid #fff; outline-offset:-1px; }
.gap { border:none; }
.side { flex:0 0 300px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:14px; }
#photo { width:100%; aspect-ratio:4/3; object-fit:cover; background:#101010;
  border-radius:6px; display:block; color:var(--muted); font-size:13px; }
#elTxt { font-weight:700; margin:10px 0 0; font-size:16px; }
#famTxt { font-size:13px; }
#factTxt { color:var(--muted); font-size:13px; margin-top:4px; line-height:1.5; }
#sumTxt { color:var(--muted); font-size:12.5px; margin-top:8px; line-height:1.5; }
#attTxt { color:var(--muted); font-size:10.5px; margin-top:8px; line-height:1.4;
  border-top:1px solid var(--line); padding-top:6px; overflow-wrap:break-word; }
.legend { display:flex; gap:12px; flex-wrap:wrap; margin-top:14px; font-size:12.5px;
  color:var(--muted); }
.legend span.sw { width:11px; height:11px; border-radius:3px; display:inline-block;
  margin-right:5px; }
.legend button { background:none; border:none; color:var(--muted); cursor:pointer;
  font-size:12.5px; padding:0; }
.legend button.on { color:var(--text); }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.note a { color:var(--accent); }
@media (max-width:980px){ .stage{flex-direction:column;} .side{position:static; width:100%;}
  #photo{max-width:300px;} .cell .sy{font-size:11px;} .cell .z{display:none;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library</a></nav>
</header>
<h1>Matter</h1>
<div class="stage">
  <div id="table"></div>
  <div class="side"><div class="card">
    <img id="photo" alt="">
    <div id="elTxt">Hover an element</div>
    <div id="famTxt"></div>
    <div id="factTxt"></div>
    <div id="sumTxt"></div>
    <div id="attTxt"></div>
  </div></div>
</div>
<div class="legend" id="legend"></div>
<p class="note">The 118 confirmed elements, colored by family. The element
under the cursor shows a photograph of the real substance, the way the film
timelines show posters; a family name in the legend lights up its members.
The gap rows pull the lanthanides and actinides out of the main block, as the
printed table does.</p>
<p class="note">Element data comes from the
<a href="https://github.com/Bowserinator/Periodic-Table-JSON">Periodic-Table-JSON</a>
dataset (CC BY-SA 3.0), against the
<a href="https://iupac.org/what-we-do/periodic-table-of-elements/">IUPAC
periodic table</a>. Photographs load at view time from Wikimedia Commons and
<a href="https://images-of-elements.com/">images-of-elements.com</a> (CC BY
3.0), each with its own credit under the card; none are stored on this site.
The heaviest synthetic elements have never existed in visible amounts, so
they have no photograph.</p>
</div>
<script>
const ELS=__ELS__, FAMS=__FAMS__;
const grid=document.getElementById('table');
const byPos={};
for(const e of ELS) byPos[e.y*100+e.x]=e;
let famSel=null, pinned=null;

const famColor=k=>FAMS.find(f=>f.k===k).c;
const famLabel=k=>FAMS.find(f=>f.k===k).l;

function build(){
  grid.innerHTML='';
  for(let y=1;y<=10;y++){
    if(y===8) continue; // the dataset leaves row 8 empty above the pulled-out rows
    for(let x=1;x<=18;x++){
      const e=byPos[y*100+x];
      const c=document.createElement('div');
      if(!e){ c.className='cell gap'; grid.appendChild(c); continue; }
      c.className='cell'; c.dataset.z=e.z;
      c.style.background=famColor(e.f);
      c.innerHTML=`<div class="z">${e.z}</div><div class="sy">${e.s}</div>`;
      grid.appendChild(c);
    }
  }
  paint();
}
function paint(){
  document.querySelectorAll('.cell[data-z]').forEach(c=>{
    const e=ELS.find(x=>x.z==c.dataset.z);
    c.classList.toggle('dim', famSel!==null && e.f!==famSel);
    c.classList.toggle('sel', pinned!==null && e.z===pinned);
  });
  document.querySelectorAll('.legend button').forEach(b=>{
    b.classList.toggle('on', b.dataset.f===famSel);
  });
}
function show(z){
  const e=ELS.find(x=>x.z===z);
  if(!e) return;
  document.getElementById('elTxt').textContent=`${e.n} (${e.s})`;
  const ft=document.getElementById('famTxt');
  ft.textContent=famLabel(e.f); ft.style.color=famColor(e.f);
  const state=e.ph.toLowerCase()+' at room temperature';
  document.getElementById('factTxt').textContent=
    `Element ${e.z} \\u00b7 atomic mass ${e.m} \\u00b7 ${state}`+
    (e.ap?` \\u00b7 ${e.ap}`:'');
  document.getElementById('sumTxt').textContent=e.sum;
  const img=document.getElementById('photo');
  const att=document.getElementById('attTxt');
  if(e.img){
    img.src=e.img; img.alt=`Photograph of ${e.n.toLowerCase()}`;
    att.textContent=e.att;
  } else {
    img.removeAttribute('src');
    img.alt='No photograph: this element has never existed in a visible amount';
    att.textContent='';
  }
}
grid.addEventListener('pointerover',e=>{
  const c=e.target.closest('.cell[data-z]');
  if(c && pinned===null) show(+c.dataset.z);
});
grid.addEventListener('click',e=>{
  const c=e.target.closest('.cell[data-z]');
  if(!c){ pinned=null; paint(); return; }
  const z=+c.dataset.z;
  pinned = pinned===z ? null : z;
  if(pinned!==null) show(z);
  paint();
});
const lg=document.getElementById('legend');
lg.innerHTML=FAMS.map(f=>
  `<span><span class="sw" style="background:${f.c}"></span><button data-f="${f.k}">${f.l}</button></span>`).join('');
lg.addEventListener('click',e=>{
  const b=e.target.closest('button[data-f]');
  if(!b) return;
  famSel = famSel===b.dataset.f ? null : b.dataset.f;
  paint();
});
build();
show(79);
</script>
</body>
</html>
"""

html = HTML.replace("__ELS__", els_js).replace("__FAMS__", fam_js)
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} bytes): {len(data)} elements, "
      f"{n_photo} with a photograph, {len(FAMILIES)} families")
