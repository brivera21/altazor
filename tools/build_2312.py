#!/usr/bin/env python3
"""Generate solar-system-2312.html, The Solar System of 2312.

The real solar system under Kim Stanley Robinson's 2312: the planets on a
log-scaled orbit map with the novel's places marked, each with a card
saying what the book puts there and what is actually there. A toggle
draws Swan Er Hong's journey through the book in order.

Orbit radii are JPL/NASA semi-major axes; the radial scale is
logarithmic, the note says so, and planet positions along their orbits
are spread for legibility, not ephemeris positions.

Usage: python3 build_2312.py
"""

import json
import math
from pathlib import Path

OUT = Path(__file__).parent.parent / "solar-system-2312.html"

# name, semi-major axis (AU), angle deg (spread for legibility), kind
# kind: 'novel' = the novel puts something here, 'quiet' = drawn muted
BODIES = [
    ("Mercury", 0.387, 205, "novel"),
    ("Venus", 0.723, 335, "novel"),
    ("Earth", 1.000, 45, "novel"),
    ("Mars", 1.524, 130, "novel"),
    ("Vesta", 2.36, 255, "novel"),
    ("Ceres", 2.77, 285, "novel"),
    ("Jupiter", 5.203, 65, "novel"),
    ("Saturn", 9.537, 160, "novel"),
    ("Uranus", 19.19, 320, "quiet"),
    ("Neptune", 30.07, 20, "quiet"),
    ("Pluto", 39.5, 100, "novel"),
]

# body -> (marker title, book text, real text)
PLACES = {
    "Mercury": ("Terminator",
        "The planet's one city rides giant tracks that circle Mercury, "
        "staying just ahead of sunrise; the day side's heat expands the "
        "rails behind it and pushes the city west at walking pace, one lap "
        "every 176 days. Sunwalkers hike ahead of the dawn for the "
        "spectacle. Midway through the book an engineered meteorite swarm "
        "destroys the city, and Swan and Wahram walk out through a utility "
        "tunnel beneath the tracks.",
        "Mercury's slow turn makes the conceit work: its solar day is 176 "
        "Earth days, so at the equator the sunrise line advances at about "
        "3.6 km/h, and slower toward the poles, genuinely outwalkable. No "
        "engineering study of thermal-expansion track propulsion exists, "
        "but a 2026 rover concept proposes permanently tracking the "
        "terminator at just these speeds, citing the novel."),
    "Venus": ("The sunshield",
        "Venus cools behind a great parasol while tented cities rise and a "
        "faction argues for spinning the planet up with asteroid impacts. "
        "The book's climax foils an attack meant to drop the shield.",
        "Venus today runs 467 degrees Celsius under 93 bars of carbon "
        "dioxide. A sunshade at the Sun-Venus L1 point is real literature: "
        "Paul Birch worked out fast terraforming schemes in 1991, and "
        "space-sunshade optics were studied for Earth by Angel in 2006."),
    "Earth": ("The drowned coasts",
        "Eleven billion people on a climate-wracked planet of hundreds of "
        "ministates; Manhattan is a new Venice, boats in the avenues. In "
        "the book's great set piece, thousands of terraria airdrop their "
        "preserved animals back onto the continents, the Reanimation.",
        "The flooded-city premise extends a real curve: satellite "
        "altimetry has watched global mean sea level rise accelerate from "
        "about 2 to more than 4 millimeters a year since 1993."),
    "Mars": ("A finished Mars",
        "The Mars trilogy's project stands complete here: a terraformed, "
        "politically independent world that has retired from everyone "
        "else's quarrels. The book ends with a wedding on Olympus Mons.",
        "Olympus Mons is real and remains the solar system's largest "
        "volcano, about 22 km above the datum. The terraforming itself "
        "stays fiction: Mars holds a thin carbon dioxide atmosphere near "
        "six millibars."),
    "Vesta": ("The terraria",
        "Most large asteroids have been hollowed out, spun up, and lit "
        "inside: thousands of rolling countryside worlds serving as "
        "wilderness arks, farms and ferries. Swan designed them; the "
        "investigation tours the Vesta zone.",
        "Vesta is the belt's second most massive body, a differentiated "
        "protoplanet the Dawn probe orbited in 2011. Real studies of spun "
        "asteroid habitats find the catch the novel skips: many asteroids "
        "are loose rubble piles that would need containment to spin at "
        "living gravity."),
    "Ceres": ("The belt's port",
        "Ceres anchors the asteroid economy the terraria trade through, "
        "part of the loose league of space settlements the book calls the "
        "Mondragon Accord.",
        "Ceres is the belt's one dwarf planet, 476 km in radius and "
        "perhaps a quarter water by mass; Dawn orbited it in 2015 and "
        "found brine deposits in Occator crater."),
    "Jupiter": ("Io's qube lab",
        "On volcanic Io, the researcher Wang Wei runs one of the system's "
        "most powerful qubes, the quantum computers whose humanoid "
        "descendants drive the book's conspiracy; his station is attacked "
        "during the investigation.",
        "Io is the most volcanically active world known, kneaded by tidal "
        "heating from Jupiter and the resonance with Europa and Ganymede; "
        "hundreds of volcanoes resurface it continuously."),
    "Saturn": ("Titan and the league",
        "The Saturn system runs its own politics as the Saturnian League; "
        "Wahram is a Titan diplomat, terraforming has begun under Titan's "
        "haze, and between crises the pair go bodysurfing on ring ice.",
        "Titan really is the one moon with a thick atmosphere, nitrogen "
        "and methane at one and a half Earth pressures, with methane "
        "rain, rivers and cold seas mapped by Cassini. Nearby Iapetus "
        "keeps its real two-tone paint job, one hemisphere dark as coal."),
    "Pluto": ("The exile",
        "The story ends at Pluto and Charon, where the rogue humanoid "
        "qubes and their maker are gathered and expelled from the solar "
        "system aboard a starship named Nix.",
        "Pluto has five known moons, and Nix is really one of them. New "
        "Horizons flew past in 2015 and found a geologically young "
        "nitrogen-ice heart, Sputnik Planitia."),
}

# Swan's journey through the book, in order, as body names
JOURNEY = ["Mercury", "Jupiter", "Earth", "Venus", "Mercury", "Saturn",
           "Venus", "Mars"]

# log radial scale
AMIN, AMAX = 0.387, 39.5
RMIN, RMAX = 62, 358
def R(a):
    t = (math.log10(a) - math.log10(AMIN)) / (math.log10(AMAX) - math.log10(AMIN))
    return round(RMIN + t * (RMAX - RMIN), 1)

CX, CY = 420, 385
bodies_js = json.dumps([
    {"n": n, "a": a, "r": R(a), "th": th, "kind": kind,
     **({"place": PLACES[n][0], "book": PLACES[n][1], "real": PLACES[n][2]}
        if n in PLACES else {})}
    for n, a, th, kind in BODIES], separators=(",", ":"))
journey_js = json.dumps(JOURNEY, separators=(",", ":"))

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Solar System of 2312 · Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; --site:#ffb02e; --orbit:#2e3742; }
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
.stage { display:flex; gap:22px; align-items:flex-start; }
#map { flex:1 1 640px; min-width:0; }
#map svg { width:100%; height:auto; display:block; user-select:none; }
.side { flex:0 0 320px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:16px; }
#kindTxt { color:var(--muted); font-size:11.5px; letter-spacing:.09em;
  text-transform:uppercase; }
#nameTxt { font-weight:700; font-size:17px; margin:2px 0 8px; }
#bookTxt { font-size:13.5px; line-height:1.55; }
#realTxt { color:var(--muted); font-size:13.5px; line-height:1.55; margin-top:10px;
  border-top:1px solid var(--line); padding-top:10px; }
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
  <nav class="site"><a href="science-fiction.html">&larr; Science Fiction</a><a href="red-mars.html">The Mars of Red Mars</a></nav>
</header>
<h1>The Solar System of 2312</h1>
<div class="bar">
  <button id="bJourney">Swan's journey</button>
  <span class="note" style="border:0;margin:0;padding:0">amber marks are the novel's places</span>
</div>
<div class="stage">
  <div id="map"></div>
  <div class="side"><div class="card">
    <div id="kindTxt"></div>
    <div id="nameTxt">A world under the cursor lands here</div>
    <div id="bookTxt"></div>
    <div id="realTxt"></div>
  </div></div>
</div>
<p class="note">The orbits are the real ones, drawn to their JPL semimajor
axes on a logarithmic radial scale so that Mercury and Pluto share one map;
each world sits at an arbitrary point of its orbit, spread for legibility.
Amber diamonds mark where Kim Stanley Robinson's 2312 puts its story, and
each card pairs what the book says with what is actually there. The journey
button traces Swan Er Hong's route through the novel in order.</p>
<h2 class="refh">References</h2>
<div class="refs">
<p>Robinson, K. S. (2012). <i>2312</i>. Orbit. Synopsis and notes:
<a href="https://www.kimstanleyrobinson.info/content/2312">https://www.kimstanleyrobinson.info/content/2312</a></p>
<p>Orbital elements: Jet Propulsion Laboratory, Approximate positions of the
planets.
<a href="https://ssd.jpl.nasa.gov/planets/approx_pos.html">https://ssd.jpl.nasa.gov/planets/approx_pos.html</a>;
small bodies via the JPL Small-Body Database,
<a href="https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html">https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html</a></p>
<p>NASA planetary science pages for each world:
<a href="https://science.nasa.gov/mercury/facts/">Mercury</a>,
<a href="https://science.nasa.gov/venus/venus-facts/">Venus</a>,
<a href="https://science.nasa.gov/mars/facts/">Mars</a>,
<a href="https://science.nasa.gov/dwarf-planets/ceres/facts/">Ceres</a>,
<a href="https://science.nasa.gov/solar-system/asteroids/4-vesta/">Vesta</a>,
<a href="https://science.nasa.gov/jupiter/moons/io/">Io</a>,
<a href="https://science.nasa.gov/saturn/moons/titan/facts/">Titan</a>,
<a href="https://science.nasa.gov/saturn/moons/iapetus/">Iapetus</a>,
<a href="https://science.nasa.gov/dwarf-planets/pluto/facts/">Pluto</a></p>
<p>Sea level: NASA global mean sea level indicator.
<a href="https://sealevel.nasa.gov/understanding-sea-level/key-indicators/global-mean-sea-level/">https://sealevel.nasa.gov/understanding-sea-level/key-indicators/global-mean-sea-level/</a></p>
<p>Birch, P. (1991). Terraforming Venus quickly. <i>Journal of the British
Interplanetary Society, 44</i>, 157-167.
<a href="https://ui.adsabs.harvard.edu/abs/1991JBIS...44..157B">https://ui.adsabs.harvard.edu/abs/1991JBIS...44..157B</a></p>
<p>Angel, R. (2006). Feasibility of cooling the Earth with a cloud of small
spacecraft near the inner Lagrange point (L1). <i>Proceedings of the
National Academy of Sciences, 103</i>(46), 17184-17189.
<a href="https://doi.org/10.1073/pnas.0608163103">https://doi.org/10.1073/pnas.0608163103</a></p>
<p>Miklav&#269;i&#269;, P. M., et al. (2022). Habitat Bennu: Design concepts
for spinning habitats constructed from rubble pile near-Earth asteroids.
<i>Frontiers in Astronomy and Space Sciences, 8</i>, 645363.
<a href="https://doi.org/10.3389/fspas.2021.645363">https://doi.org/10.3389/fspas.2021.645363</a></p>
<p>A Mercury rover on the terminator: Universe Today on the 2026 LPSC
concept.
<a href="https://www.universetoday.com/articles/a-mercury-rover-could-explore-the-planet-by-sticking-to-the-terminator">https://www.universetoday.com/articles/a-mercury-rover-could-explore-the-planet-by-sticking-to-the-terminator</a></p>
</div>
</div>
<script>
const BODIES=__BODIES__, JOURNEY=__JOURNEY__;
const W=840,H=770,CX=420,CY=385;
const el=document.getElementById('map');
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
let journey=false;

const at={};
for(const b of BODIES){
  const t=b.th*Math.PI/180;
  b.x=CX+b.r*Math.cos(t); b.y=CY-b.r*Math.sin(t);
  at[b.n]=b;
}
function render(){
  let s=`<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" id="ssvg">`;
  s+=`<rect width="${W}" height="${H}" fill="#121212"/>`;
  for(const b of BODIES)
    s+=`<circle cx="${CX}" cy="${CY}" r="${b.r}" fill="none"
      stroke="var(--orbit)" stroke-width="1"/>`;
  // the belt band between Vesta and Ceres
  const rv=at['Vesta'].r, rc=at['Ceres'].r;
  s+=`<circle cx="${CX}" cy="${CY}" r="${(rv+rc)/2}" fill="none"
    stroke="#8b93a7" stroke-opacity="0.25" stroke-width="${rc-rv+10}" stroke-dasharray="1 7"/>`;
  if(journey){
    let d='',prev=null;
    for(const leg of JOURNEY){
      const b=at[leg];
      d+=(prev?`Q${CX},${CY} `:'M')+`${b.x},${b.y} `;
      prev=b;
    }
    s+=`<path d="${d}" fill="none" stroke="#b48cf2" stroke-width="1.6"
      stroke-dasharray="7 5" opacity="0.85"/>`;
    JOURNEY.forEach((leg,i)=>{
      const b=at[leg], k=JOURNEY.slice(0,i).filter(x=>x===leg).length;
      s+=`<text x="${b.x+14}" y="${b.y-10-13*k}" font-size="11"
        fill="#b48cf2">${i+1}</text>`;
    });
  }
  s+=`<circle cx="${CX}" cy="${CY}" r="9" fill="#ffd24d"/>
    <text x="${CX}" y="${CY+26}" text-anchor="middle" font-size="11.5"
    fill="#9a9a9a">Sun</text>`;
  for(const b of BODIES){
    const quiet=b.kind==='quiet';
    const col=quiet?'#4b5563':'var(--accent)';
    s+=`<g data-n="${esc(b.n)}" style="cursor:default">
      <circle cx="${b.x}" cy="${b.y}" r="${quiet?4:5.5}" fill="${col}"/>`;
    if(!quiet)
      s+=`<rect x="${b.x-4.4}" y="${b.y-16.4}" width="8.8" height="8.8"
        transform="rotate(45 ${b.x} ${b.y-12})" fill="var(--site)"
        stroke="#121212" stroke-width="1"/>`;
    s+=`<text x="${b.x}" y="${b.y+21}" text-anchor="middle" font-size="12.5"
      font-weight="${quiet?400:700}" fill="${quiet?'#6b7280':'#e6e6e6'}"
      stroke="#121212" stroke-width="2.6" paint-order="stroke">${esc(b.n)}</text>`;
    if(!quiet)
      s+=`<text x="${b.x}" y="${b.y+36}" text-anchor="middle" font-size="10.5"
        fill="var(--site)" stroke="#121212" stroke-width="2.2"
        paint-order="stroke">${esc(b.place)}</text>`;
    s+='</g>';
  }
  s+='</svg>';
  el.innerHTML=s;
}
function show(n){
  const b=at[n]; if(!b) return;
  const quiet=b.kind==='quiet';
  document.getElementById('kindTxt').textContent=
    quiet?'Off the book\\u2019s map':'In the novel \\u00b7 '+b.n+' \\u00b7 '+b.a+' AU';
  document.getElementById('nameTxt').textContent=quiet?b.n:b.place;
  document.getElementById('bookTxt').textContent=
    quiet?'The novel passes this world by.':b.book;
  document.getElementById('realTxt').textContent=quiet?'':b.real;
}
el.addEventListener('pointerover',e=>{
  const g=e.target.closest('[data-n]');
  if(g) show(g.getAttribute('data-n'));
});
document.getElementById('bJourney').onclick=e=>{
  journey=!journey; e.target.classList.toggle('on',journey); render();
};
render();
show('Mercury');
window.__ss2312=()=>({bodies:BODIES.length,
  novel:BODIES.filter(b=>b.kind==='novel').length, journey,
  legs:JOURNEY.length});
</script>
</body>
</html>
"""

html = HTML.replace("__BODIES__", bodies_js).replace("__JOURNEY__", journey_js)
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} bytes): {len(BODIES)} bodies, "
      f"{len(PLACES)} novel places, {len(JOURNEY)} journey legs")
