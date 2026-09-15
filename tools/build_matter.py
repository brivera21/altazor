#!/usr/bin/env python3
"""Generate matter.html, Matter: the periodic table with photographs.

The 118 confirmed elements on the standard 18-column grid, colored by family.
The element under the cursor fills a side card with a photograph of the real
substance, the way the film timelines show posters. Element data comes from
the Periodic-Table-JSON dataset (CC BY-SA 3.0), trimmed at build time to the
fields the page uses; Cesium is respelled Cesium to match IUPAC. Photographs
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
        e["name"] = "Cesium"

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

# The year each element was first isolated or identified, for the scale that
# colors the table by when it was found. The dataset carries who found an
# element but not when, so the years are written out here. Elements known
# since antiquity carry no year and stay gray.
YEAR = {
    15: 1669, 27: 1735, 78: 1735, 28: 1751, 25: 1774, 8: 1774, 17: 1774,
    42: 1778, 52: 1782, 74: 1783, 40: 1789, 92: 1789, 22: 1791, 39: 1794,
    4: 1798, 24: 1797, 41: 1801, 23: 1801, 73: 1802, 46: 1802, 45: 1803,
    76: 1803, 77: 1803, 58: 1803, 19: 1807, 11: 1807, 5: 1808, 20: 1808,
    56: 1808, 38: 1808, 12: 1808, 35: 1826, 3: 1817, 34: 1817, 48: 1817,
    14: 1824, 13: 1825, 90: 1829, 57: 1839, 68: 1843, 65: 1843, 44: 1844,
    55: 1860, 37: 1861, 81: 1861, 49: 1863, 31: 1875, 70: 1878, 67: 1878,
    69: 1879, 62: 1879, 21: 1879, 59: 1885, 60: 1885, 64: 1880, 32: 1886,
    9: 1886, 66: 1886, 2: 1895, 36: 1898, 10: 1898, 54: 1898, 84: 1898,
    88: 1898, 89: 1899, 86: 1900, 63: 1901, 71: 1907, 91: 1913, 72: 1923,
    75: 1925, 43: 1937, 87: 1939, 85: 1940, 93: 1940, 94: 1940, 61: 1945,
    95: 1944, 96: 1944, 97: 1949, 98: 1950, 99: 1952, 100: 1952, 101: 1955,
    102: 1966, 103: 1961, 104: 1964, 105: 1970, 106: 1974, 107: 1981,
    109: 1982, 108: 1984, 111: 1994, 110: 1994, 112: 1996, 114: 1999,
    116: 2000, 118: 2002, 113: 2003, 115: 2003, 117: 2010,
}


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
        # the measured properties the color scales run on. None where the
        # value has never been measured, which the scales leave gray.
        "melt": e.get("melt"), "boil": e.get("boil"),
        "den": e.get("density"),
        "en": e.get("electronegativity_pauling"),
        "ion": (e.get("ionization_energies") or [None])[0],
        "yr": YEAR.get(e["number"]),
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
#scaleTxt { font-size:13px; margin-top:6px; line-height:1.5; font-weight:600; }
#sumTxt { color:var(--muted); font-size:12.5px; margin-top:8px; line-height:1.5; }
#attTxt { color:var(--muted); font-size:10.5px; margin-top:8px; line-height:1.4;
  border-top:1px solid var(--line); padding-top:6px; overflow-wrap:break-word; }
.bar { display:flex; gap:7px; align-items:center; flex-wrap:wrap; margin-bottom:10px; }
.bar button { font:inherit; font-size:13px; padding:5px 12px; border-radius:999px;
  border:1px solid var(--line); background:#1a1a1a; color:var(--text); cursor:pointer; }
.bar button:hover { border-color:var(--accent); }
.bar button.on { background:var(--accent); border-color:var(--accent); color:#0b0b0b; }
.bar2 { display:flex; gap:16px; align-items:center; flex-wrap:wrap;
  margin:0 0 12px; color:var(--muted); font-size:12.5px; }
.bar2[hidden] { display:none; }
.bar2 label { display:flex; gap:9px; align-items:center; }
.bar2 input[type=range] { width:300px; accent-color:var(--accent); }
.bar2 .ticks button { background:none; border:none; color:var(--muted);
  cursor:pointer; font-size:12.5px; padding:0 6px; }
.bar2 .ticks button:hover { color:var(--accent); }
#scale { display:flex; gap:10px; align-items:center; flex-wrap:wrap;
  margin-top:14px; font-size:12.5px; color:var(--muted); }
#scale .ramp { width:190px; height:11px; border-radius:3px; }
#scale .swatch { width:11px; height:11px; border-radius:3px;
  display:inline-block; margin-right:5px; vertical-align:-1px; }
.legend[hidden], #scale[hidden] { display:none; }
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
<div class="bar" id="bar"></div>
<div class="bar2" id="tempbar" hidden>
  <label>Temperature
    <input type="range" id="temp" min="0" max="6000" step="5" value="293">
    <span id="tempTxt"></span></label>
  <span class="ticks" id="ticks"></span>
</div>
<div class="stage">
  <div id="table"></div>
  <div class="side"><div class="card">
    <img id="photo" alt="">
    <div id="elTxt">Hover an element</div>
    <div id="famTxt"></div>
    <div id="factTxt"></div>
    <div id="scaleTxt"></div>
    <div id="sumTxt"></div>
    <div id="attTxt"></div>
  </div></div>
</div>
<div class="legend" id="legend"></div>
<div id="scale" hidden></div>
<p class="note">The 118 confirmed elements. The buttons repaint the table by
a measured property, and periodicity shows itself: density and ionization
energy rise and fall down the rows in step. The temperature scale colors
each element by the state it is in at that temperature, so the table melts
from the bottom up as it rises, and tungsten is the last to go. The element
under the cursor shows a photograph of the real substance.</p>
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
let famSel=null, pinned=null, mode='family', temp=293;

// The scales. Each names the field it reads, how to write a value, and
// whether the eye should run over the logarithm rather than the number:
// density spans four hundredfold and melting points forty, so a linear
// ramp would put almost everything at one end.
const SCALES={
  melt:{k:'melt', l:'Melting point', u:'K', log:false,
        fmt:v=>Math.round(v)+' K',
        none:'never measured, or it turns straight to gas'},
  boil:{k:'boil', l:'Boiling point', u:'K', log:false,
        fmt:v=>Math.round(v)+' K', none:'never measured'},
  den: {k:'den', l:'Density', u:'g/cm3', log:true,
        fmt:v=>(v<1?v.toFixed(3):v.toFixed(2))+' g/cm\u00b3',
        none:'never measured'},
  en:  {k:'en', l:'Electronegativity', u:'', log:false,
        fmt:v=>v.toFixed(2)+' Pauling',
        none:'no accepted value; the noble gases mostly have none'},
  ion: {k:'ion', l:'First ionization', u:'kJ/mol', log:false,
        fmt:v=>Math.round(v)+' kJ/mol', none:'never measured'},
  yr:  {k:'yr', l:'Year found', u:'', log:false,
        fmt:v=>String(v),
        none:'known since antiquity, with no date of discovery'},
};
const RAMP=['#0b3c5d','#1f6f8b','#2fa4a0','#8fd06a','#f0d35a','#f09b28',
            '#e25822','#b3202c'];
const STATE={solid:'#6b8fb5', liquid:'#2fa4a0', gas:'#e0a458',
             unknown:'#3a3a3a'};

function lerpRamp(t){
  t=Math.max(0,Math.min(1,t));
  const x=t*(RAMP.length-1), i=Math.min(RAMP.length-2,Math.floor(x)), f=x-i;
  const hx=c=>[1,3,5].map(j=>parseInt(c.slice(j,j+2),16));
  const a=hx(RAMP[i]), b=hx(RAMP[i+1]);
  return '#'+a.map((v,j)=>Math.round(v+(b[j]-v)*f).toString(16)
    .padStart(2,'0')).join('');
}
function range(sc){
  const vs=ELS.map(e=>e[sc.k]).filter(v=>v!==null&&v!==undefined);
  return [Math.min(...vs), Math.max(...vs)];
}
// where an element stands at a temperature, from its own two points
function stateAt(e,t){
  if(e.melt===null||e.melt===undefined) return 'unknown';
  if(t<e.melt) return 'solid';
  if(e.boil===null||e.boil===undefined) return 'unknown';
  return t<e.boil ? 'liquid' : 'gas';
}
function cellColor(e){
  if(mode==='family') return famColor(e.f);
  if(mode==='state') return STATE[stateAt(e,temp)];
  const sc=SCALES[mode], v=e[sc.k];
  if(v===null||v===undefined) return '#3a3a3a';
  const [lo,hi]=range(sc);
  const t = sc.log
    ? (Math.log10(v)-Math.log10(lo))/(Math.log10(hi)-Math.log10(lo))
    : (v-lo)/(hi-lo);
  return lerpRamp(t);
}

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
      c.style.background=cellColor(e);
      c.innerHTML=`<div class="z">${e.z}</div><div class="sy">${e.s}</div>`;
      grid.appendChild(c);
    }
  }
  paint();
}
function paint(){
  document.querySelectorAll('.cell[data-z]').forEach(c=>{
    const e=ELS.find(x=>x.z==c.dataset.z);
    c.style.background=cellColor(e);
    c.classList.toggle('dim',
      mode==='family' && famSel!==null && e.f!==famSel);
    c.classList.toggle('sel', pinned!==null && e.z===pinned);
  });
  document.querySelectorAll('.legend button').forEach(b=>{
    b.classList.toggle('on', b.dataset.f===famSel);
  });
  document.querySelectorAll('#bar button').forEach(b=>
    b.classList.toggle('on', b.dataset.m===mode));
  document.getElementById('legend').hidden = mode!=='family';
  document.getElementById('tempbar').hidden = mode!=='state';
  legendFor();
  if(pinned!==null) show(pinned);
}

// what the colors mean, rewritten for whichever scale is showing
function legendFor(){
  const box=document.getElementById('scale');
  if(mode==='family'){ box.hidden=true; return; }
  box.hidden=false;
  if(mode==='state'){
    box.innerHTML=Object.entries({solid:'Solid',liquid:'Liquid',gas:'Gas',
      unknown:'Not measured'}).map(([k,l])=>
      `<span><span class="swatch" style="background:${STATE[k]}"></span>${l}</span>`)
      .join('')+
      `<span>at ${temp} K, which is ${(temp-273.15).toFixed(0)} \u00b0C</span>`;
    return;
  }
  const sc=SCALES[mode], [lo,hi]=range(sc);
  const stops=RAMP.map((c,i)=>`${c} ${(i/(RAMP.length-1)*100).toFixed(0)}%`)
    .join(',');
  const miss=ELS.filter(e=>e[sc.k]===null||e[sc.k]===undefined).length;
  box.innerHTML=
    `<span>${sc.fmt(lo)}</span>`+
    `<span class="ramp" style="background:linear-gradient(90deg,${stops})"></span>`+
    `<span>${sc.fmt(hi)}</span>`+
    (sc.log?'<span>on a log scale</span>':'')+
    (miss?`<span><span class="swatch" style="background:#3a3a3a"></span>`+
          `${miss} ${sc.none}</span>`:'');
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
  // what this element is worth on the scale being shown
  const sv=document.getElementById('scaleTxt');
  if(mode==='family'){ sv.textContent=''; }
  else if(mode==='state'){
    const st=stateAt(e,temp);
    sv.textContent = st==='unknown'
      ? 'State at '+temp+' K: not known, the points were never measured'
      : 'At '+temp+' K it is '+st+
        (e.melt!==null&&e.melt!==undefined?', melting at '+Math.round(e.melt)+' K':'')+
        (e.boil!==null&&e.boil!==undefined?' and boiling at '+Math.round(e.boil)+' K':'');
    sv.style.color=STATE[st];
  } else {
    const sc=SCALES[mode], v=e[sc.k];
    sv.textContent = (v===null||v===undefined)
      ? sc.l+': '+sc.none
      : sc.l+': '+sc.fmt(v);
    sv.style.color=(v===null||v===undefined)?'':cellColor(e);
  }
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
// the scale buttons
const MODES=[['family','Family'],['state','State at a temperature'],
  ['melt','Melting point'],['boil','Boiling point'],['den','Density'],
  ['en','Electronegativity'],['ion','First ionization'],['yr','Year found']];
const bar=document.getElementById('bar');
bar.innerHTML=MODES.map(([m,l])=>
  `<button data-m="${m}">${l}</button>`).join('');
bar.addEventListener('click',ev=>{
  const b=ev.target.closest('button[data-m]');
  if(!b) return;
  mode=b.dataset.m;
  if(mode!=='family') famSel=null;
  paint();
});

const tempIn=document.getElementById('temp');
function setTemp(v){
  temp=+v;
  tempIn.value=temp;
  document.getElementById('tempTxt').textContent=
    temp+' K, '+(temp-273.15).toFixed(0)+' \u00b0C';
  paint();
}
tempIn.addEventListener('input',e=>setTemp(e.target.value));
// a few temperatures worth standing at
document.getElementById('ticks').innerHTML=[
  [4,'liquid helium'],[77,'liquid nitrogen'],[273,'ice'],[293,'a room'],
  [373,'boiling water'],[1337,'gold melts'],[3695,'tungsten melts']
].map(([k,l])=>`<button data-k="${k}">${l}</button>`).join('');
document.getElementById('ticks').addEventListener('click',ev=>{
  const b=ev.target.closest('button[data-k]');
  if(b) setTemp(+b.dataset.k);
});
setTemp(293);

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
