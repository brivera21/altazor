#!/usr/bin/env python3
"""Generate energy.html, Energy: the forms and the flows between them.

A ring of the nine forms energy takes, joined by arrows for the processes
that turn one into another. Hovering a form gives its formula and how physics
measures it; hovering an arrow gives the process and an everyday example.
Clicking a form keeps only its own arrows lit. Thermal energy sits at the
center as the sink every real conversion leaks into, which is the second law
seen as a picture.

An amount of energy set above the ring is solved through every formula at
once, so one joule count reads as a speed, a height, a stretch, a mass of
sugar, a charge, a count of photons, a count of fissions, a rest mass and a
temperature rise, all at the same time.

Usage: python3 build_energy.py
"""

import json
import math
import apa
from pathlib import Path

OUT = Path(__file__).parent.parent / "energy.html"

# CODATA 2022 for the constants, the SI brochure for standard gravity, the
# Atwater factor for carbohydrate, Ma and others (2013) for the recoverable
# energy of a uranium-235 fission.
CONST = {
    "m_ref": 1.0,            # kilogram, the test mass for speed and height
    "g": 9.80665,            # metres per second squared, standard gravity
    "k_spring": 100.0,       # newtons per metre, a firm hand spring
    "sugar": 17.0e3,         # joules per gram of carbohydrate
    "volt": 1.5,             # volts, one alkaline cell
    "h": 6.62607015e-34,     # joule seconds
    "c": 2.99792458e8,       # metres per second
    "green": 550e-9,         # metres, the middle of the visible band
    "fission": 3.2436e-11,   # joules, 202.5 MeV recovered per fission
    "R": 8.31446261815324,   # joules per mole kelvin
}

# label, joules. A spread of twenty-one decades, each one measured.
AMOUNTS = [
    ("an electronvolt", 1.602176634e-19),
    ("a photon of green light", 3.6118e-19),
    ("a heartbeat", 1.0),
    ("an alkaline cell", 1.35e4),
    ("a day of food", 8.8e6),
    ("a litre of petrol", 3.42e7),
    ("a tonne of TNT", 4.184e9),
    ("a magnitude 7 earthquake", 2.0e15),
    ("a hurricane, for a day", 5.2e19),
]

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
const_js = json.dumps(CONST, separators=(",", ":"))
amounts_js = json.dumps([{"l": l, "j": j} for l, j in AMOUNTS],
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
.controls { display:flex; align-items:center; gap:12px; flex-wrap:wrap; margin:0 0 12px; }
.controls label { font-size:13px; color:var(--muted); }
.controls input[type=number] { background:var(--panel); color:var(--text);
  border:1px solid var(--line); border-radius:8px; padding:6px 9px; width:190px;
  font:inherit; font-size:14px; font-variant-numeric:tabular-nums; }
.controls input[type=range] { flex:1 1 260px; min-width:200px; accent-color:var(--accent); height:22px; }
.presets { display:flex; gap:6px; flex-wrap:wrap; margin:0 0 14px; }
.presets button { background:var(--panel); color:var(--muted); border:1px solid var(--line);
  border-radius:999px; padding:5px 11px; font-size:12.5px; cursor:pointer; font-family:inherit; }
.presets button:hover { color:var(--text); border-color:#3d3d3d; }
.presets button[aria-pressed=true] { color:#0b0b0b; background:var(--accent);
  border-color:var(--accent); font-weight:700; }
#solveTxt { font-size:14px; margin:8px 0 2px; font-variant-numeric:tabular-nums; }
#assumeTxt { color:var(--muted); font-size:12px; margin-bottom:8px; }
.method { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
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
<div class="controls">
  <label for="joules">joules</label>
  <input type="number" id="joules" value="1" step="any" min="0">
  <input type="range" id="mag" min="-2100" max="2100" step="1" value="0"
    aria-label="joules, by powers of ten">
</div>
<div class="presets" id="presets"></div>
<div class="stage">
  <div id="diagram"></div>
  <div class="side"><div class="card">
    <div id="kindTxt"></div>
    <div id="nameTxt">Hover a form or an arrow</div>
    <div id="formTxt"></div>
    <div id="solveTxt"></div>
    <div id="assumeTxt"></div>
    <div id="bodyTxt"></div>
  </div></div>
</div>
<p class="note">The nine forms energy takes, and the arrows physics has found
between them. A form or an arrow under the cursor fills the card; a click on
a form keeps only its own arrows lit, and a click on the background lets go.
The total along any chain of arrows never changes, which is the first law.</p>
<p class="note">The amount set above the ring runs through all nine formulas
at once, so the same joules appear as a speed, a height, a stretch of spring,
a mass of sugar, a charge, a count of photons, a count of fissions, a rest
mass and a temperature rise. Four arrows point into thermal energy and only
two lead out, and the one back to motion pays a toll set by the two
temperatures. That one-way traffic is the second law.</p>
<div class="method"><p>Each formula is solved on a stated reference case: a
one kilogram mass for speed and for height, standard gravity at 9.80665
metres per second squared, a spring of 100 newtons per metre, carbohydrate at
the Atwater factor of 17 kilojoules per gram, one alkaline cell at 1.5 volts,
green light at 550 nanometres, 202.5 megaelectronvolts recovered per fission
of uranium-235, and one mole of a monatomic gas. Speed is worked
relativistically, since above roughly a tenth of the speed of light the
half-m-v-squared answer would pass the speed of light; below that the two
agree to better than a percent. The other formulas are given their own
answer at every amount, including amounts far outside the range they were
written for: a height of a hundred million kilometres is what the near
surface formula returns, not a place where it still holds.</p></div>
<h2 class="refh">References</h2>
<div class="refs">
<p>Feynman, R. P., Leighton, R. B., &amp; Sands, M. (1963). Conservation of
energy. In <i>The Feynman lectures on physics</i> (Vol. 1, Ch. 4). Caltech.
<a href="https://www.feynmanlectures.caltech.edu/I_04.html">https://www.feynmanlectures.caltech.edu/I_04.html</a></p>
<p>Bureau International des Poids et Mesures. (2019). <i>The International
System of Units (SI)</i> (9th ed.), where the joule is defined.
<a href="https://www.bipm.org/en/publications/si-brochure">https://www.bipm.org/en/publications/si-brochure</a></p>
<p>Tiesinga, E., Mohr, P. J., Newell, D. B., &amp; Taylor, B. N. (2024). CODATA
recommended values of the fundamental physical constants: 2022. <i>Reviews of
Modern Physics, 96</i>(2), 025002.
<a href="https://doi.org/10.1103/RevModPhys.96.025002">https://doi.org/10.1103/RevModPhys.96.025002</a></p>
<p>Food and Agriculture Organization of the United Nations. (2003). <i>Food
energy: Methods of analysis and conversion factors</i> (FAO Food and Nutrition
Paper 77), where the Atwater factors are set out.
<a href="https://www.fao.org/4/y5022e/y5022e00.htm">https://www.fao.org/4/y5022e/y5022e00.htm</a></p>
<p>Ma, X. B., Zhong, W. L., Wang, L. Z., Chen, Y. X., &amp; Cao, J. (2013).
Improved calculation of the energy release in neutron-induced fission.
<i>Physical Review C, 88</i>(1), 014605.
<a href="https://doi.org/10.1103/PhysRevC.88.014605">https://doi.org/10.1103/PhysRevC.88.014605</a></p>
<p>Choy, G. L., &amp; Boatwright, J. L. (1995). Global patterns of radiated
seismic energy and apparent stress. <i>Journal of Geophysical Research, 100</i>(B9),
18205-18228.
<a href="https://doi.org/10.1029/95JB01969">https://doi.org/10.1029/95JB01969</a></p>
<p>National Oceanic and Atmospheric Administration, Atlantic Oceanographic and
Meteorological Laboratory. (2023). How much energy does a hurricane release?
In <i>Hurricane research division frequently asked questions</i>.
<a href="https://www.aoml.noaa.gov/hrd-faq/">https://www.aoml.noaa.gov/hrd-faq/</a></p>
</div>
</div>
<script>
const FORMS=__FORMS__, FLOWS=__FLOWS__, K=__CONST__, AMOUNTS=__AMOUNTS__;
const W=980,H=770;
let E=1;                                  // the amount on the ring, in joules

/* ---- numbers ---- */
const SUP={'-':'⁻','0':'⁰','1':'¹','2':'²','3':'³',
           '4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'};
const sup=n=>String(n).split('').map(c=>SUP[c]||c).join('');
const PRE=[[24,'Y'],[21,'Z'],[18,'E'],[15,'P'],[12,'T'],[9,'G'],[6,'M'],[3,'k'],
           [0,''],[-3,'m'],[-6,'µ'],[-9,'n'],[-12,'p'],[-15,'f'],[-18,'a'],
           [-21,'z'],[-24,'y']];
function sci(v,dp){
  if(!isFinite(v)) return '∞';
  let e=Math.floor(Math.log10(Math.abs(v))), m=v/Math.pow(10,e);
  const lim=10-0.5*Math.pow(10,-(dp===undefined?2:dp));
  if(Math.abs(m)>=lim){ m/=10; e++; }
  return m.toFixed(dp===undefined?2:dp)+'×10'+sup(e);
}
// a value with an SI prefix where one exists, scientific notation otherwise
function si(v,unit){
  if(v===0) return '0 '+unit;
  const a=Math.abs(v), e3=Math.floor(Math.log10(a)/3)*3;
  const pre=PRE.find(p=>p[0]===e3);
  if(!pre) return sci(v)+' '+unit;
  const m=v/Math.pow(10,e3);
  return (Math.abs(m)>=100?m.toFixed(0):Math.abs(m)>=10?m.toFixed(1):m.toFixed(2))
    +' '+pre[1]+unit;
}
function count(v){ return v>=1e5||v<0.01 ? sci(v) : String(+v.toPrecision(3)); }

/* ---- one amount of energy, solved through every formula ---- */
// each returns [the number, a noun for it, the working, the case assumed]
const SOLVE={
  kin:e=>{        // E = (gamma - 1)mc², rearranged to keep small u exact
    const u=e/(K.m_ref*K.c*K.c);                // gamma minus one
    const beta=Math.sqrt(2*u+u*u)/(1+u);        // v over c
    const gap=(1+u-Math.sqrt(2*u+u*u))/(1+u);   // one minus beta, stably
    const v=beta*K.c;
    const dp=Math.min(12,Math.max(3,Math.ceil(-Math.log10(gap))+2));
    const asC=beta.toFixed(dp)+'c';
    return [beta<0.01?si(v,'m/s'):asC, '',
      beta<0.01 ? 'v = √(2E / m) = '+si(v,'m/s')+', which is '+
          sci(beta*100,2)+'% of the speed of light'
        : 'v = '+asC+', or '+si(v,'m/s')+', short of light by '+sci(gap,2)+' of it',
      'a mass of one kilogram, worked relativistically'];
  },
  grav:e=>{ const h=e/(K.m_ref*K.g);
    return [si(h,'m'), '', 'h = E / mg = '+si(h,'m'),
      'a mass of one kilogram, gravity at 9.80665 m/s²']; },
  ela:e=>{ const x=Math.sqrt(2*e/K.k_spring);
    return [si(x,'m'), '', 'x = √(2E / k) = '+si(x,'m'),
      'a spring of 100 newtons per metre']; },
  chem:e=>{ const m=e/K.sugar;
    return [si(m,'g'), 'of sugar', 'm = E / 17 kJ per gram = '+si(m,'g'),
      'carbohydrate at the Atwater factor']; },
  elec:e=>{ const q=e/K.volt;
    return [si(q,'C'), '', 'q = E / V = '+si(q,'C')+', or '+si(q/3600,'Ah')+
      ' drawn from the cell', 'one alkaline cell at 1.5 volts']; },
  rad:e=>{ const ph=K.h*K.c/K.green, n=e/ph, lam=K.h*K.c/e;
    return [count(n), 'photons', 'N = E λ / hc = '+count(n)+' photons'+
      (e<=1e-14?', and one photon carrying it all would have a wavelength of '
        +si(lam,'m'):''),
      'green light at 550 nanometres']; },
  nuc:e=>{ const n=e/K.fission;
    return [count(n), 'fissions', 'N = E / 202.5 MeV = '+count(n)+
      ' fissions, which is '+si(n*235/6.02214076e23,'g')+' of uranium-235',
      'uranium-235, 202.5 MeV recovered per fission']; },
  mass:e=>{ const m=e/(K.c*K.c)*1000;   // grams, since E/c² is kilograms
    return [si(m,'g'), '', 'm = E / c² = '+si(m,'g'),
      'the full conversion, at the speed of light squared']; },
  th:e=>{ const dT=2*e/(3*K.R);
    return [si(dT,'K'), 'for a mole', 'ΔT = 2E / 3R = '+si(dT,'K')+' for the mole',
      'one mole of a monatomic gas']; },
};
const el=document.getElementById('diagram');
const byK={}; for(const f of FORMS) byK[f.k]=f;
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
let sel=null;

function arc(a,b,off){
  // a gentle curve from node a to node b, trimmed at the node circles
  const A=byK[a], B=byK[b];
  const dx=B.x-A.x, dy=B.y-A.y, d=Math.hypot(dx,dy);
  const ux=dx/d, uy=dy/d;
  const r=56;
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
      <circle cx="${f.x}" cy="${f.y}" r="50" fill="${f.c}"
        fill-opacity="0.16" stroke="${f.c}" stroke-width="${f.k===sel?2.6:1.6}"/>
      <text x="${f.x}" y="${f.y-17}" text-anchor="middle" font-size="12.5"
        font-weight="700" fill="#e6e6e6" pointer-events="none">${esc(f.l)}</text>
      <text x="${f.x}" y="${f.y-2}" text-anchor="middle" font-size="10.5"
        fill="${f.c}" pointer-events="none">${esc(f.f)}</text>
      <text x="${f.x}" y="${f.y+17}" text-anchor="middle" font-size="11.5"
        font-weight="700" fill="#e6e6e6" pointer-events="none"
        data-sol="${f.k}">${esc(SOLVE[f.k](E)[0])}</text>
      <text x="${f.x}" y="${f.y+30}" text-anchor="middle" font-size="9.5"
        fill="${f.c}" pointer-events="none">${esc(SOLVE[f.k](E)[1])}</text></g>`;
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
  const [,, work, assume]=SOLVE[k](E);
  const sv=document.getElementById('solveTxt');
  sv.textContent=work; sv.style.color=f.c;
  document.getElementById('assumeTxt').textContent='for '+si(E,'J')+', '+assume;
  document.getElementById('bodyTxt').textContent=f.b;
}
function showFlow(i){
  const fl=FLOWS[i];
  document.getElementById('kindTxt').textContent=
    byK[fl.a].l+' \\u2192 '+byK[fl.b].l;
  document.getElementById('nameTxt').textContent=fl.n;
  const ft=document.getElementById('formTxt');
  ft.textContent='';
  document.getElementById('solveTxt').textContent='';
  document.getElementById('assumeTxt').textContent='';
  document.getElementById('bodyTxt').textContent=fl.t;
}
el.addEventListener('pointerover',e=>{
  const g=e.target.closest('[data-f]');
  if(g){ card=g.getAttribute('data-f'); showForm(card); return; }
  const a=e.target.closest('[data-fl]');
  if(a){ showFlow(+a.getAttribute('data-fl')); }
});
el.addEventListener('click',e=>{
  const g=e.target.closest('[data-f]');
  if(g){ const k=g.getAttribute('data-f');
    sel = sel===k?null:k; card=k; render(); showForm(k); return; }
  if(e.target.closest('[data-bg]')){ sel=null; render(); }
});
let card='kin';
const EMIN=-21, EMAX=21;
function setE(j,fromBox){
  if(!(j>0)||!isFinite(j)) return;
  E=Math.min(Math.pow(10,EMAX),Math.max(Math.pow(10,EMIN),j));
  const mag=Math.log10(E);
  const sl=document.getElementById('mag');
  if(+sl.value!==Math.round(mag*100)) sl.value=Math.round(mag*100);
  if(!fromBox) document.getElementById('joules').value=
    +E.toPrecision(E>=1e-4&&E<1e15?6:4);
  for(const b of document.querySelectorAll('#presets button'))
    b.setAttribute('aria-pressed',
      Math.abs(Math.log10(+b.dataset.j)-mag)<1e-9?'true':'false');
  render();
  showForm(card);
}
document.getElementById('presets').innerHTML=AMOUNTS.map(
  a=>'<button type="button" data-j="'+a.j+'">'+a.l+'</button>').join('');
document.getElementById('presets').addEventListener('click',e=>{
  const b=e.target.closest('button'); if(b) setE(+b.dataset.j);
});
document.getElementById('mag').addEventListener('input',e=>
  setE(Math.pow(10,+e.target.value/100)));
document.getElementById('joules').addEventListener('input',e=>
  setE(+e.target.value,true));

render();
setE(1);
window.__en=()=>({sel,E,forms:FORMS.length,flows:FLOWS.length});
</script>
</body>
</html>
"""

html = (HTML.replace("__FORMS__", forms_js).replace("__FLOWS__", flows_js)
        .replace("__CONST__", const_js).replace("__AMOUNTS__", amounts_js))
html = apa.css_pass(html)
OUT.write_text(html, encoding="utf-8")
into_th = sum(1 for a, b, *_ in FLOWS if b == "th")
outof_th = sum(1 for a, b, *_ in FLOWS if a == "th")
print(f"wrote {OUT} ({len(html):,} bytes): {len(FORMS)} forms, "
      f"{len(FLOWS)} flows; {into_th} into thermal, {outof_th} out")
