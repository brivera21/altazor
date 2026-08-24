#!/usr/bin/env python3
"""Generate energy.html, Energy: the forms and the flows between them.

A ring of the nine forms energy takes, joined by arrows for the processes
that turn one into another. Hovering a form gives its formula and how physics
measures it; hovering an arrow gives the process and an everyday example.
Clicking a form keeps only its own arrows lit. Thermal energy sits at the
bottom as the sink every real conversion leaks into, which is the second law
seen as a picture.

Usage: python3 build_energy.py
"""

import json
import math
from pathlib import Path

OUT = Path(__file__).parent.parent / "energy.html"

# key, label, color, formula, card text
FORMS = [
    ("kin", "Kinetic", "#ff5c4d", "E = ½mv²",
     "The energy of motion. Physics measures it from mass and speed, and it "
     "was the first form to get a formula, in the collisions studied by "
     "Huygens and Leibniz."),
    ("grav", "Gravitational", "#ffb02e", "E = mgh",
     "The energy of height. Lifting a mass stores it, and near Earth's "
     "surface it grows by weight times height. On the scale of orbits the "
     "formula bends into Newton's, but the bookkeeping is the same."),
    ("ela", "Elastic", "#e6c86e", "E = ½kx²",
     "The energy of a stretched or squeezed thing. A spring stores the work "
     "done against its stiffness and gives it back on release."),
    ("chem", "Chemical", "#31d67a", "bond energies",
     "The energy of electrons bound in molecules. A reaction rearranges the "
     "bonds, and the difference between old and new is what a fire, a "
     "battery or a muscle spends."),
    ("elec", "Electrical", "#58a6ff", "E = qV",
     "The energy of charges pushed through a field. A charge crossing a "
     "volt gains one joule per coulomb; currents carry it along wires with "
     "almost nothing lost."),
    ("rad", "Radiant", "#b48cf2", "E = hf",
     "The energy of light. It travels as electromagnetic waves and is "
     "absorbed in packets, each photon carrying Planck's constant times its "
     "frequency."),
    ("nuc", "Nuclear", "#d1548e", "binding energy",
     "The energy that holds nuclei together. Splitting heavy nuclei or "
     "fusing light ones releases about a million times more per atom than "
     "any chemical bond."),
    ("mass", "Rest mass", "#f28cb0", "E = mc²",
     "Matter itself, read as energy. The conversion rate is the speed of "
     "light squared, which is why a gram is worth twenty-five million "
     "kilowatt hours."),
    ("th", "Thermal", "#c9814b", "E = ³⁄₂NkT",
     "The random motion of atoms, kinetic energy too disordered to see. "
     "Temperature measures its average per particle, and every real process "
     "leaks some energy here."),
]

# from, to, process, card text
FLOWS = [
    ("grav", "kin", "Falling",
     "A dropped mass trades height for speed. Meters of height become "
     "meters per second, by the square root."),
    ("kin", "grav", "Climbing",
     "A thrown ball or a hiker converts motion back into height, until "
     "gravity has taken all of it."),
    ("ela", "kin", "Release",
     "A bowstring or a spring gives back its stored work as motion."),
    ("kin", "ela", "Impact",
     "A bouncing ball squeezes on landing, parking its motion in the "
     "squeeze for a few milliseconds."),
    ("chem", "kin", "Muscle",
     "Muscle burns sugar bonds into contraction. About a quarter of the "
     "bond energy becomes motion; the rest leaves as body heat."),
    ("chem", "th", "Combustion",
     "Fire rearranges fuel and oxygen into tighter bonds and hands the "
     "difference to the flame's heat and light."),
    ("chem", "elec", "Battery",
     "A battery lets its reaction run only through the outside wire, so "
     "the bond energy leaves as current."),
    ("elec", "chem", "Charging",
     "Driving the current backwards runs the reaction uphill and stores "
     "the energy in bonds again."),
    ("elec", "kin", "Motor",
     "A current in a magnetic field pushes; motors turn most of what they "
     "draw into torque."),
    ("kin", "elec", "Generator",
     "Spinning a coil in a magnetic field pushes charges along the wire. "
     "Nearly every watt on the grid passes through this arrow."),
    ("elec", "th", "Resistance",
     "Charges bumping through a conductor heat it. A toaster is this "
     "arrow and nothing else."),
    ("elec", "rad", "Lamp",
     "An LED drops each charge across a junction and emits the energy as "
     "a photon."),
    ("rad", "chem", "Photosynthesis",
     "Leaves catch photons and park the energy in sugar bonds. Every fuel "
     "with a biological past started on this arrow."),
    ("rad", "th", "Absorption",
     "Sunlight on a dark surface becomes the random jostling of its "
     "atoms. Most of Earth's warmth arrives on this arrow."),
    ("th", "rad", "Glow",
     "Everything warm radiates. A stove coil glows red, a body glows in "
     "the infrared, the Earth glows back to space."),
    ("th", "kin", "Heat engine",
     "Heat flowing from hot to cold can be made to push a piston on the "
     "way. Carnot showed the toll: only a fraction converts, set by the "
     "two temperatures."),
    ("nuc", "th", "Fission and fusion",
     "A reactor splits uranium, the Sun fuses hydrogen; the binding "
     "energy difference arrives as heat."),
    ("mass", "nuc", "Mass defect",
     "A nucleus weighs less than its parts. That missing sliver of rest "
     "mass is the binding energy nuclear processes spend."),
    ("mass", "rad", "Annihilation",
     "Matter meeting antimatter converts entirely into photons, the only "
     "process that cashes rest mass in full."),
]

keys = {k for k, *_ in FORMS}
for a, b, *_ in FLOWS:
    assert a in keys and b in keys, (a, b)

# thermal sits at the center, the sink every arrow can reach; the ring is
# ordered so that every remaining arrow joins neighbors or near neighbors
order = ["rad", "chem", "elec", "kin", "grav", "ela", "mass", "nuc"]
assert set(order) | {"th"} == keys
CX, CY, R = 430, 385, 305
pos = {"th": (CX, CY)}
for i, k in enumerate(order):
    a = -math.pi / 2 + i * 2 * math.pi / len(order)
    pos[k] = (round(CX + R * math.cos(a), 1), round(CY + R * math.sin(a), 1))

forms_js = json.dumps(
    [{"k": k, "l": l, "c": c, "f": f, "b": b,
      "x": pos[k][0], "y": pos[k][1]}
     for k, l, c, f, b in FORMS], separators=(",", ":"), ensure_ascii=False)
flows_js = json.dumps(
    [{"a": a, "b": b, "n": n, "t": t} for a, b, n, t in FLOWS],
    separators=(",", ":"), ensure_ascii=False)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Energy · Altazor</title>
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
nav.site a { color:var(--muted); text-decoration:none; font-size:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 12px; font-size:26px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; }
#diagram svg { width:100%; height:auto; display:block; user-select:none; }
.side { flex:0 0 300px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:16px; }
#kindTxt { font-size:12px; letter-spacing:.08em; text-transform:uppercase;
  color:var(--muted); }
#nameTxt { font-weight:700; font-size:17px; margin:2px 0 2px; }
#formTxt { font-size:15px; margin-bottom:8px; }
#bodyTxt { color:var(--muted); font-size:13.5px; line-height:1.55; }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.note a { color:var(--accent); }
.refs { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.refs p { margin:0 0 8px; }
.refs a { color:var(--accent); }
h2.refh { font-size:15px; margin:26px 0 8px; }
@media (max-width:900px){ .stage{flex-direction:column;} .side{position:static; width:100%;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library</a></nav>
</header>
<h1>Energy</h1>
<div class="stage">
  <div id="diagram"></div>
  <div class="side"><div class="card">
    <div id="kindTxt"></div>
    <div id="nameTxt">Hover a form or an arrow</div>
    <div id="formTxt"></div>
    <div id="bodyTxt"></div>
  </div></div>
</div>
<p class="note">The nine forms energy takes, and the arrows physics has found
between them. A form or an arrow under the cursor fills the card; a click on
a form keeps only its own arrows lit, and a click on the background lets go.
The total along any chain of arrows never changes, which is the first law.</p>
<p class="note">Thermal energy sits at the center for a reason. Four arrows
point into it and only two lead out, and the one that leads back to motion
pays a toll set by the two temperatures. That one-way traffic is the second
law, seen as a picture.</p>
<h2 class="refh">References</h2>
<div class="refs">
<p>Feynman, R. P., Leighton, R. B., &amp; Sands, M. (1963). Conservation of
energy. In <i>The Feynman lectures on physics</i> (Vol. 1, Ch. 4). Caltech.
<a href="https://www.feynmanlectures.caltech.edu/I_04.html">https://www.feynmanlectures.caltech.edu/I_04.html</a></p>
<p>Bureau International des Poids et Mesures. (2019). <i>The International
System of Units (SI)</i> (9th ed.), where the joule is defined.
<a href="https://www.bipm.org/en/publications/si-brochure">https://www.bipm.org/en/publications/si-brochure</a></p>
</div>
</div>
<script>
const FORMS=__FORMS__, FLOWS=__FLOWS__;
const W=980,H=770;
const el=document.getElementById('diagram');
const byK={}; for(const f of FORMS) byK[f.k]=f;
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
let sel=null;

function arc(a,b,off){
  // a gentle curve from node a to node b, trimmed at the node circles
  const A=byK[a], B=byK[b];
  const dx=B.x-A.x, dy=B.y-A.y, d=Math.hypot(dx,dy);
  const ux=dx/d, uy=dy/d;
  const r=46;
  const x1=A.x+ux*r, y1=A.y+uy*r, x2=B.x-ux*r, y2=B.y-uy*r;
  const mx=(x1+x2)/2-uy*off, my=(y1+y2)/2+ux*off;
  // the label rides its own curve, pushed a little further out on the
  // same side, so paired arrows keep their names apart
  const lo=off/2+14;
  const lx=(x1+x2)/2-uy*lo, ly=(y1+y2)/2+ux*lo-4;
  return {x1,y1,x2,y2,mx,my,lx,ly};
}
function render(){
  let s=`<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" id="ensvg">`;
  s+=`<rect width="${W}" height="${H}" fill="#121212" data-bg="1"/>`;
  s+=`<defs>`;
  for(const f of FORMS)
    s+=`<marker id="m-${f.k}" viewBox="0 0 10 10" refX="8" refY="5"
      markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="${f.c}"/></marker>`;
  s+=`</defs>`;
  // the arrows: paired flows get opposite bows so they never overlap
  const pair={};
  for(const fl of FLOWS) pair[fl.a+'>'+fl.b]=true;
  FLOWS.forEach((fl,i)=>{
    const two=pair[fl.b+'>'+fl.a];
    const g=arc(fl.a,fl.b,two?26:14);
    const c=byK[fl.a].c;
    const lit = sel===null || fl.a===sel || fl.b===sel;
    s+=`<g data-fl="${i}" opacity="${lit?1:0.13}" style="cursor:default">
      <path d="M${g.x1},${g.y1} Q${g.mx},${g.my} ${g.x2},${g.y2}"
        fill="none" stroke="${c}" stroke-width="1.7" marker-end="url(#m-${fl.a})"/>
      <path d="M${g.x1},${g.y1} Q${g.mx},${g.my} ${g.x2},${g.y2}"
        fill="none" stroke="#fff" stroke-opacity="0" stroke-width="14"/>
      <text x="${g.lx}" y="${g.ly}"
        text-anchor="middle" font-size="11" fill="${c}"
        pointer-events="none">${esc(fl.n)}</text></g>`;
  });
  // the forms
  for(const f of FORMS){
    const lit = sel===null || f.k===sel ||
      FLOWS.some(fl=>(fl.a===sel&&fl.b===f.k)||(fl.b===sel&&fl.a===f.k));
    s+=`<g data-f="${f.k}" opacity="${lit?1:0.2}" style="cursor:default">
      <circle cx="${f.x}" cy="${f.y}" r="42" fill="${f.c}"
        fill-opacity="0.16" stroke="${f.c}" stroke-width="${f.k===sel?2.6:1.6}"/>
      <text x="${f.x}" y="${f.y-2}" text-anchor="middle" font-size="13.5"
        font-weight="700" fill="#e6e6e6" pointer-events="none">${esc(f.l)}</text>
      <text x="${f.x}" y="${f.y+16}" text-anchor="middle" font-size="11"
        fill="${f.c}" pointer-events="none">${esc(f.f)}</text></g>`;
  }
  s+='</svg>';
  el.innerHTML=s;
}
function showForm(k){
  const f=byK[k];
  document.getElementById('kindTxt').textContent='A form energy takes';
  document.getElementById('nameTxt').textContent=f.l+' energy';
  const ft=document.getElementById('formTxt');
  ft.textContent=f.f; ft.style.color=f.c;
  document.getElementById('bodyTxt').textContent=f.b;
}
function showFlow(i){
  const fl=FLOWS[i];
  document.getElementById('kindTxt').textContent=
    byK[fl.a].l+' \\u2192 '+byK[fl.b].l;
  document.getElementById('nameTxt').textContent=fl.n;
  const ft=document.getElementById('formTxt');
  ft.textContent=''; 
  document.getElementById('bodyTxt').textContent=fl.t;
}
el.addEventListener('pointerover',e=>{
  const g=e.target.closest('[data-f]');
  if(g){ showForm(g.getAttribute('data-f')); return; }
  const a=e.target.closest('[data-fl]');
  if(a){ showFlow(+a.getAttribute('data-fl')); }
});
el.addEventListener('click',e=>{
  const g=e.target.closest('[data-f]');
  if(g){ const k=g.getAttribute('data-f');
    sel = sel===k?null:k; render(); showForm(k); return; }
  if(e.target.closest('[data-bg]')){ sel=null; render(); }
});
render();
showForm('kin');
window.__en=()=>({sel,forms:FORMS.length,flows:FLOWS.length});
</script>
</body>
</html>
"""

html = HTML.replace("__FORMS__", forms_js).replace("__FLOWS__", flows_js)
OUT.write_text(html, encoding="utf-8")
into_th = sum(1 for a, b, *_ in FLOWS if b == "th")
outof_th = sum(1 for a, b, *_ in FLOWS if a == "th")
print(f"wrote {OUT} ({len(html):,} bytes): {len(FORMS)} forms, "
      f"{len(FLOWS)} flows; {into_th} into thermal, {outof_th} out")
