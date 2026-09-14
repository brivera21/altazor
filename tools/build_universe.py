#!/usr/bin/env python3
"""Generate universe.html, The Universe: what the cosmos is made of.

A history panel and three stacked bars. The panel draws the share of the
total energy held by radiation, matter and dark energy across seven decades
of the scale factor, from the flat LCDM baseline of Planck 2018 VI; a marker
on it sets the moment, and the top bar is the budget at that moment. The thin
sliver of ordinary matter opens into a second bar carrying the baryon census
of Shull, Smith and Danforth (2012), with the once-missing share drawn
hatched, and the galaxies segment opens into a third bar for the Milky Way.
Hovering or tapping anything fills the side card.

Usage: python3 build_universe.py
"""

import json
import apa
from pathlib import Path

OUT = Path(__file__).parent.parent / "universe.html"

# Flat LCDM baseline, Planck 2018 VI table 2 (TT,TE,EE+lowE+lensing+BAO).
# Radiation is photons, Omega_gamma h^2 = 2.47e-5, plus three neutrino species
# treated as massless, a factor 1.6918 on the photon density. Dark matter here
# carries the massive neutrinos too, which is where they belong today.
H0 = 67.4                  # km/s/Mpc
OMEGA = {"rad": 9.15e-5, "dm": 0.2657, "ob": 0.0493}
OMEGA["de"] = 1.0 - sum(OMEGA.values())

# (key, label, exponent n in rho ~ a^-n, color, hatched, card title, card
#  text, source line)
TOP = [
    ("rad", "Radiation", 4, "#e0564f", False,
     "Radiation",
     "The photons of the microwave background, with neutrinos counted "
     "alongside them. Expansion both spreads the photons out and stretches "
     "each one, so radiation thins by a fourth power and loses ground to "
     "everything else. It ruled the first fifty thousand years.",
     "Planck 2018 VI, baseline model"),
    ("dm", "Dark matter", 3, "#58a6ff", False,
     "Dark matter",
     "Matter that gravitates but neither emits nor absorbs light. It holds "
     "galaxies and clusters together and shapes the cosmic web; every attempt "
     "to detect a particle of it has so far come back empty.",
     "Planck 2018 VI, baseline model"),
    ("ob", "Ordinary matter", 3, "#ffb02e", False,
     "Ordinary matter",
     "Everything made of atoms: every star, planet, gas cloud and living "
     "thing. The bar below opens this sliver into where those atoms actually "
     "are.",
     "Planck 2018 VI, baseline model"),
    ("de", "Dark energy", 0, "#b48cf2", False,
     "Dark energy",
     "The component that accelerates the expansion of the universe. It enters "
     "the equations as a constant energy of space itself, so expansion does "
     "not dilute it, and every other component thins past it in turn.",
     "Planck 2018 VI, baseline model"),
]

BARYONS = [
    ("lya", "Diffuse intergalactic gas", 28, "#ffb02e", False,
     "The diffuse intergalactic medium",
     "Cool photoionized hydrogen strung along the cosmic web, seen as the "
     "Lyman-alpha forest in quasar spectra. About 28 percent of all ordinary "
     "matter, give or take 11.",
     "Shull, Smith and Danforth 2012"),
    ("whim", "Warm-hot intergalactic gas", 25, "#ff8a3d", False,
     "The warm-hot intergalactic medium",
     "Shock-heated gas at a hundred thousand to a million kelvin, traced by "
     "highly ionized oxygen and broad Lyman-alpha absorbers. About 25 percent, "
     "give or take 8.",
     "Shull, Smith and Danforth 2012"),
    ("cgm", "Circumgalactic gas", 5, "#2fc6a6", False,
     "The circumgalactic medium",
     "The gas halo around each galaxy, fuel for future star formation. About "
     "5 percent, give or take 3.",
     "Shull, Smith and Danforth 2012"),
    ("icm", "Cluster gas", 4, "#6ee7f2", False,
     "The intracluster medium",
     "Hot X-ray gas filling groups and clusters of galaxies. About 4 percent, "
     "give or take 1.5.",
     "Shull, Smith and Danforth 2012"),
    ("cold", "Cold gas", 1.7, "#9be564", False,
     "Cold neutral gas",
     "Neutral hydrogen and helium in and around galaxies, the reservoir the "
     "Lyman-alpha forest does not reach. About 1.7 percent, give or take 0.4.",
     "Shull, Smith and Danforth 2012"),
    ("miss", "Found in 2020", 29, "#8b93a7", True,
     "The baryons that went missing",
     "In 2012 about 29 percent of the ordinary matter, give or take 13, had "
     "never been seen in any waveband; simulations placed most of it as even "
     "hotter intergalactic gas, invisible to the surveys. In 2020 the "
     "dispersion of fast radio bursts measured all the ionized gas along "
     "their paths and found the full amount.",
     "Shull 2012; Macquart and others 2020"),
    ("gal", "Galaxies", 7, "#31d67a", False,
     "Stars and gas in galaxies",
     "All the stars and the interstellar gas of all the galaxies: about 7 "
     "percent of the ordinary matter, give or take 2. The bar below opens "
     "this segment into what a large galaxy is made of.",
     "Shull, Smith and Danforth 2012"),
]

# The ordinary matter of one large galaxy, with the Milky Way as the
# exemplar: percentages of its baryonic mass, about 6.3e10 solar masses.
# Stars 5e10 (Bland-Hawthorn and Gerhard 2016), remnant share 18 percent of
# stellar mass (Fukugita and Peebles 2004), HI 8e9 (Kalberla and Kerp 2009),
# H2 1.2e9 (Miville-Deschenes and others 2017), helium scaled onto the gas,
# dust about 1e8 (Galliano and others 2018), Sgr A* 4.3e6 (GRAVITY 2022).
GALAXY = [
    ("stars", "Living stars", 65, "#31d67a", False,
     "Living stars",
     "Stars still burning, from red dwarfs to supergiants: about 65 percent "
     "of the Milky Way's ordinary matter, some 40 billion solar masses of "
     "the 50 billion in stars overall.",
     "Bland-Hawthorn and Gerhard 2016; Fukugita and Peebles 2004"),
    ("rem", "Stellar remnants", 14, "#7fd6a8", False,
     "Stellar remnants",
     "Dead stars: white dwarfs hold most of it, with neutron stars and "
     "stellar black holes the rest, about 18 percent of the stellar mass.",
     "Fukugita and Peebles 2004"),
    ("atom", "Atomic gas", 18, "#a3e635", False,
     "Atomic gas",
     "Neutral hydrogen spread through the disk, about 8 billion solar "
     "masses of hydrogen plus its share of helium, the raw reservoir for "
     "star formation.",
     "Kalberla and Kerp 2009"),
    ("mol", "Molecular gas", 2.7, "#d3f261", False,
     "Molecular gas",
     "Cold dense clouds of molecular hydrogen, about 1.2 billion solar "
     "masses plus helium: the part of the gas that actually collapses into "
     "new stars.",
     "Miville-Deschenes, Murray and Lee 2017"),
    ("dust", "Dust", 0.2, "#e8c78f", False,
     "Dust",
     "Grains of silicate and carbon mixed through the gas at about one part "
     "in a hundred: a rounding error by mass, and the reason the Milky Way "
     "has dark lanes.",
     "Galliano, Galametz and Jones 2018"),
    ("smbh", "Central black hole", 0.007, "#8b93a7", False,
     "Sagittarius A*",
     "The supermassive black hole at the center, 4.3 million solar masses: "
     "drawn here as a hairline, because for all its fame it is a hundred "
     "thousandth of the galaxy's ordinary matter.",
     "GRAVITY Collaboration 2022"),
]

assert abs(sum(OMEGA.values()) - 1.0) < 1e-12, "the model is flat"
assert abs(sum(p for _k, _l, p, *_r in BARYONS) - 99.7) < 0.5
assert abs(sum(p for _k, _l, p, *_r in GALAXY) - 99.9) < 0.5
assert BARYONS[-1][0] == "gal", "Galaxies must sit at the right end"

def _js(rows):
    return json.dumps([{"k": k, "l": l, "p": p, "c": c, "h": h,
                        "t": t, "b": b, "s": s}
                       for k, l, p, c, h, t, b, s in rows],
                      separators=(",", ":"))


def _top_js(rows):
    return json.dumps([{"k": k, "l": l, "n": n, "om": OMEGA[k], "c": c,
                        "h": h, "t": t, "b": b, "s": s}
                       for k, l, n, c, h, t, b, s in rows],
                      separators=(",", ":"))


top_js, bar_js, gal_js = _top_js(TOP), _js(BARYONS), _js(GALAXY)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Universe · Altazor</title>
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
h1 { margin:0 0 6px; font-size:26px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; }
#diagram svg { width:100%; height:auto; display:block; user-select:none; }
.side { flex:0 0 300px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:16px; }
#pct { font-size:34px; font-weight:700; }
#segTxt { font-weight:700; margin:2px 0 8px; font-size:15px; }
#bodyTxt { color:var(--muted); font-size:13.5px; line-height:1.55; }
#srcTxt { color:var(--muted); font-size:12px; margin-top:10px;
  border-top:1px solid var(--line); padding-top:8px; }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.note a { color:var(--accent); }
.refs { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.refs p { margin:0 0 8px; }
.refs a { color:var(--accent); }
h2.refh { font-size:15px; margin:26px 0 8px; }
.controls { display:flex; align-items:center; gap:14px; flex-wrap:wrap;
  margin:0 0 14px; }
.controls input[type=range] { flex:1 1 300px; min-width:220px; accent-color:var(--accent);
  height:22px; }
.rd { display:flex; gap:16px; flex-wrap:wrap; font-size:12.5px; color:var(--muted);
  font-variant-numeric:tabular-nums; }
.rd b { color:var(--text); font-weight:700; }
.presets { display:flex; gap:6px; flex-wrap:wrap; margin:0 0 14px; }
.presets button { background:var(--panel); color:var(--muted); border:1px solid var(--line);
  border-radius:999px; padding:5px 11px; font-size:12.5px; cursor:pointer;
  font-family:inherit; }
.presets button:hover { color:var(--text); border-color:#3d3d3d; }
.presets button[aria-pressed=true] { color:#0b0b0b; background:var(--accent);
  border-color:var(--accent); font-weight:700; }
#atTxt { color:var(--muted); font-size:12.5px; margin-top:8px; }
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
<h1>The Universe</h1>
<div class="controls">
  <input type="range" id="scale" min="-600" max="100" step="1" value="0"
    aria-label="scale factor">
  <div class="rd">
    <span>size <b id="rdA"></b></span>
    <span>redshift <b id="rdZ"></b></span>
    <span>background <b id="rdT"></b></span>
    <span>age <b id="rdAge"></b></span>
  </div>
</div>
<div class="presets" id="presets"></div>
<div class="stage">
  <div id="diagram"></div>
  <div class="side"><div class="card">
    <div id="pct"></div>
    <div id="segTxt">Hover a segment</div>
    <div id="bodyTxt"></div>
    <div id="atTxt"></div>
    <div id="srcTxt"></div>
  </div></div>
</div>
<p class="note">The curves hold the share of all the energy in the universe
carried by radiation, by matter and by dark energy, against the size of the
universe. Radiation thins fastest and lost the lead first; dark energy does
not thin at all, so it takes the lead last. The two crossings are where the
lines meet, and the bar under them is the budget at the moment the marker
sits on.</p>
<p class="note">Below it, the thin amber sliver of ordinary matter opens into
where its atoms actually sit, and the galaxies segment opens in turn into
what one large galaxy is made of, with the Milky Way as the exemplar. Those
two are censuses of the universe as it is now, so they fade when the marker
leaves the present.</p>
<div class="method"><p>Densities follow the flat baseline of Planck 2018 VI:
dark energy 0.685 of the critical density, dark matter 0.266, ordinary matter
0.049, radiation about one part in eleven thousand, with radiation diluting
as the fourth power of the scale factor, matter as the third, and dark energy
constant. Neutrinos are counted with the radiation. They weigh as matter once
the universe cools below their mass, near a redshift of a few hundred, and
carry about a tenth of a percent of the total today, too little to show at
this scale. The range stops at a redshift of a million, late enough that the
radiation is the photons and neutrinos of today with no other species still
in the bath. Age is the integral of d ln a over H, with a Hubble constant of
67.4 kilometres per second per megaparsec, giving 13.79 billion years for the
present. The bottom two bars count only ordinary matter: the galaxy sits in a
dark matter halo that outweighs everything drawn there by more than ten to
one.</p></div>
<h2 class="refh">References</h2>
<div class="refs">
<p>Planck Collaboration. (2020). Planck 2018 results. VI. Cosmological
parameters. <i>Astronomy &amp; Astrophysics, 641</i>, A6.
<a href="https://doi.org/10.1051/0004-6361/201833910">https://doi.org/10.1051/0004-6361/201833910</a></p>
<p>Shull, J. M., Smith, B. D., &amp; Danforth, C. W. (2012). The baryon census
in a multiphase intergalactic medium: 30% of the baryons may still be missing.
<i>The Astrophysical Journal, 759</i>(1), 23.
<a href="https://doi.org/10.1088/0004-637X/759/1/23">https://doi.org/10.1088/0004-637X/759/1/23</a></p>
<p>Macquart, J.-P., Prochaska, J. X., McQuinn, M., Bannister, K. W.,
Bhandari, S., Day, C. K., Deller, A. T., Ekers, R. D., James, C. W.,
Marnoch, L., Os&#322;owski, S., Phillips, C., Ryder, S. D., Scott, D. R.,
Shannon, R. M., &amp; Tejos, N. (2020). A census of baryons in the Universe
from localized fast radio bursts. <i>Nature, 581</i>, 391-395.
<a href="https://doi.org/10.1038/s41586-020-2300-2">https://doi.org/10.1038/s41586-020-2300-2</a></p>
<p>Particle Data Group. (2024). Cosmological parameters. In <i>Review of
particle physics</i>.
<a href="https://pdg.lbl.gov/2024/reviews/rpp2024-rev-cosmological-parameters.pdf">https://pdg.lbl.gov/2024/reviews/rpp2024-rev-cosmological-parameters.pdf</a></p>
<p>Bland-Hawthorn, J., &amp; Gerhard, O. (2016). The galaxy in context:
Structural, kinematic, and integrated properties. <i>Annual Review of
Astronomy and Astrophysics, 54</i>, 529-596.
<a href="https://doi.org/10.1146/annurev-astro-081915-023441">https://doi.org/10.1146/annurev-astro-081915-023441</a></p>
<p>Fukugita, M., &amp; Peebles, P. J. E. (2004). The cosmic energy inventory.
<i>The Astrophysical Journal, 616</i>(2), 643-668.
<a href="https://doi.org/10.1086/425155">https://doi.org/10.1086/425155</a></p>
<p>Kalberla, P. M. W., &amp; Kerp, J. (2009). The Hi distribution of the Milky
Way. <i>Annual Review of Astronomy and Astrophysics, 47</i>, 27-61.
<a href="https://doi.org/10.1146/annurev-astro-082708-101823">https://doi.org/10.1146/annurev-astro-082708-101823</a></p>
<p>Miville-Desch&#234;nes, M.-A., Murray, N., &amp; Lee, E. J. (2017). Physical
properties of molecular clouds for the entire Milky Way disk. <i>The
Astrophysical Journal, 834</i>(1), 57.
<a href="https://doi.org/10.3847/1538-4357/834/1/57">https://doi.org/10.3847/1538-4357/834/1/57</a></p>
<p>Galliano, F., Galametz, M., &amp; Jones, A. P. (2018). The interstellar
dust properties of nearby galaxies. <i>Annual Review of Astronomy and
Astrophysics, 56</i>, 673-713.
<a href="https://doi.org/10.1146/annurev-astro-081817-051900">https://doi.org/10.1146/annurev-astro-081817-051900</a></p>
<p>GRAVITY Collaboration. (2022). Mass distribution in the Galactic Center
based on interferometric astrometry of multiple stellar orbits.
<i>Astronomy &amp; Astrophysics, 657</i>, L12.
<a href="https://doi.org/10.1051/0004-6361/202142465">https://doi.org/10.1051/0004-6361/202142465</a></p>
</div>
</div>
<script>
const TOP=__TOP__, BAR=__BAR__, GAL=__GAL__;
const W=980,H=1180;
const C={x:86,y:70,w:800,h:210},
      T={x:20,y:392,w:940,h:110}, B={x:20,y:662,w:940,h:110},
      G={x:20,y:972,w:940,h:110};
const LOGMIN=-6, LOGMAX=1;          // decades of the scale factor on show
const H0INV=14.5077;                // 1/H0 in billions of years, H0 = 67.4
const TCMB=2.7255;                  // kelvin today

const el=document.getElementById('diagram');
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
const byKey=Object.fromEntries(TOP.map(d=>[d.k,d]));
const OM_M=byKey.dm.om+byKey.ob.om, OM_R=byKey.rad.om, OM_L=byKey.de.om;
let sel=null, la=0;                 // la is log10 of the scale factor

/* ---- the model: a flat three component universe ---- */
function dens(d,a){ return d.om*Math.pow(a,-d.n); }
function shares(a){
  let tot=0; const o={};
  for(const d of TOP){ o[d.k]=dens(d,a); tot+=o[d.k]; }
  for(const k in o) o[k]=o[k]/tot*100;
  return o;
}
function Erel(a){                   // H(a)/H0
  return Math.sqrt(OM_R*Math.pow(a,-4)+OM_M*Math.pow(a,-3)+OM_L);
}
function age(a){                    // billions of years, integral of dlna/H
  const lo=Math.log(1e-14), hi=Math.log(a), n=1200, h=(hi-lo)/n;
  let s=0;
  for(let i=0;i<=n;i++){
    const f=1/Erel(Math.exp(lo+i*h));
    s+=f*(i===0||i===n?1:(i%2?4:2));
  }
  return s*h/3*H0INV;
}
const A_RM=OM_R/OM_M;                       // radiation equals matter
const A_ML=Math.cbrt(OM_M/OM_L);            // matter equals dark energy

/* ---- formatting ---- */
const SUP={'-':'⁻','0':'⁰','1':'¹','2':'²','3':'³',
           '4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'};
const sup=n=>String(n).split('').map(c=>SUP[c]||c).join('');
function sci(v,dp){
  let e=Math.floor(Math.log10(Math.abs(v))), m=v/Math.pow(10,e);
  const lim=10-0.5*Math.pow(10,-(dp||2));
  if(Math.abs(m)>=lim){ m/=10; e++; }
  return m.toFixed(dp===undefined?2:dp)+'×10'+sup(e);
}
function pct(v){
  if(v>=10) return v.toFixed(1)+'%';
  if(v>=1) return v.toFixed(2)+'%';
  if(v>=0.001) return v.toFixed(4).replace(/0+$/,'')+'%';
  return sci(v,1)+'%';
}
function num(v){
  if(v===0) return '0';
  const a=Math.abs(v);
  if(a>=1e4||a<0.01) return sci(v);
  if(a>=100) return v.toFixed(0);
  if(a>=1) return v.toFixed(2);
  return v.toFixed(3);
}
function fmtT(k){
  if(k>=1e6) return num(k)+' K';
  if(k>=1000) return Math.round(k).toLocaleString('en-US')+' K';
  return k.toFixed(k<10?2:0)+' K';
}
function fmtAge(g){
  const yr=g*1e9;
  if(yr<1){
    const sec=yr*3.1557e7;
    if(sec<90) return sec.toFixed(1)+' seconds';
    if(sec<5400) return (sec/60).toFixed(1)+' minutes';
    if(sec<172800) return (sec/3600).toFixed(1)+' hours';
    return (sec/86400).toFixed(1)+' days';
  }
  if(yr<1e3) return yr.toFixed(0)+' years';
  if(yr<1e6) return (yr/1e3).toFixed(1)+' thousand years';
  if(yr<1e9) return (yr/1e6).toFixed(0)+' million years';
  return g.toFixed(2)+' billion years';
}
function fmtZ(z){
  if(z>=1e4) return num(z);
  if(z>=10) return Math.round(z).toLocaleString('en-US');
  if(z>-0.005&&z<0.005) return '0';
  return z.toFixed(2).replace(/\.?0+$/,'');
}

/* ---- the bars ---- */
function seg(row,d,x,w,p){
  const dash=d.h?' stroke-dasharray="5 4"':'';
  const op=(sel===null||sel===d.k)?1:0.35;
  let s='<g data-k="'+d.k+'" style="cursor:default" opacity="'+op+'">'+
    '<rect x="'+x+'" y="'+row.y+'" width="'+Math.max(w,1.2)+'" height="'+row.h+'" rx="4"'+
    ' fill="'+d.c+'" fill-opacity="'+(d.h?0.35:0.85)+'" stroke="'+d.c+'" stroke-width="1.4"'+dash+'/>';
  const lab=typeof p==='number'?pct(p):p+'%';
  if(w>90) s+='<text x="'+(x+w/2)+'" y="'+(row.y+row.h/2-4)+'" text-anchor="middle"'+
      ' font-size="14.5" font-weight="700" fill="#0b0b0b" pointer-events="none">'+esc(d.l)+'</text>'+
    '<text x="'+(x+w/2)+'" y="'+(row.y+row.h/2+16)+'" text-anchor="middle" font-size="13"'+
      ' fill="#0b0b0b" pointer-events="none">'+lab+'</text>';
  else if(w>34) s+='<text x="'+(x+w/2)+'" y="'+(row.y+row.h/2+5)+'" text-anchor="middle"'+
      ' font-size="12.5" font-weight="700" fill="#0b0b0b" pointer-events="none">'+lab+'</text>';
  s+='</g>';
  return s;
}
function lanes(row,list,widths){
  // labels under a bar for its narrow segments, each dropped to the first
  // lane where it fits
  let s='', x=row.x; const ends=[];
  for(let i=0;i<list.length;i++){
    const d=list[i], w=widths[i];
    if(w<=90){
      const tw=d.l.length*6.4+10;
      const lx=Math.min(row.x+row.w-tw/2,Math.max(row.x+tw/2,x+w/2));
      let lane=0;
      while(lane<ends.length && ends[lane]>lx-tw/2) lane++;
      ends[lane]=lx+tw/2+10;
      const ly=row.y+row.h+22+lane*19;
      s+='<g data-k="'+d.k+'" style="cursor:default">'+
        '<line x1="'+(x+w/2)+'" y1="'+(row.y+row.h+2)+'" x2="'+lx+'" y2="'+(ly-11)+
        '" stroke="'+d.c+'" stroke-width="1" opacity="0.7"/>'+
        '<text x="'+lx+'" y="'+ly+'" text-anchor="middle" font-size="12" fill="'+d.c+'">'+
        esc(d.l)+'</text></g>';
    }
    x+=w;
  }
  return s;
}

/* ---- the history panel ---- */
const CX=v=>C.x+(v-LOGMIN)/(LOGMAX-LOGMIN)*C.w;     // log10 a to pixels
const CY=f=>C.y+C.h-f/100*C.h;                       // percent to pixels
const XC=px=>LOGMIN+(px-C.x)/C.w*(LOGMAX-LOGMIN);
const CURVES=[['rad','Radiation','#e0564f'],
              ['mat','Matter','#58a6ff'],
              ['de','Dark energy','#b48cf2']];
function curveShare(k,a){
  const r=OM_R*Math.pow(a,-4), m=OM_M*Math.pow(a,-3), l=OM_L, t=r+m+l;
  return (k==='rad'?r:k==='mat'?m:l)/t*100;
}
function panel(){
  let s='<g>';
  s+='<rect x="'+C.x+'" y="'+C.y+'" width="'+C.w+'" height="'+C.h+
     '" fill="#171717" stroke="#2b2b2b"/>';
  // horizontal grid at 0, 25, 50, 75, 100 percent
  for(const f of [0,25,50,75,100]){
    s+='<line x1="'+C.x+'" y1="'+CY(f)+'" x2="'+(C.x+C.w)+'" y2="'+CY(f)+
       '" stroke="#2b2b2b" stroke-width="1"/>'+
       '<text x="'+(C.x-8)+'" y="'+(CY(f)+4)+'" text-anchor="end" font-size="11" fill="#6f6f6f">'+
       f+'%</text>';
  }
  // decades of the scale factor, labelled underneath by redshift
  for(let e=LOGMIN;e<=LOGMAX;e++){
    const x=CX(e), a=Math.pow(10,e), z=1/a-1;
    s+='<line x1="'+x+'" y1="'+C.y+'" x2="'+x+'" y2="'+(C.y+C.h)+
       '" stroke="#232323" stroke-width="1"/>'+
       '<text x="'+x+'" y="'+(C.y+C.h+16)+'" text-anchor="middle" font-size="11" fill="#6f6f6f">'+
       (e===0?'1':'10'+sup(e))+'</text>'+
       '<text x="'+x+'" y="'+(C.y+C.h+31)+'" text-anchor="middle" font-size="10.5" fill="#565656">'+
       fmtZ(z)+'</text>';
  }
  s+='<text x="'+(C.x+C.w+20)+'" y="'+(C.y+C.h+16)+'" font-size="11" fill="#6f6f6f">size</text>'+
     '<text x="'+(C.x+C.w+20)+'" y="'+(C.y+C.h+31)+'" font-size="10.5" fill="#565656">redshift</text>';
  // the two crossings
  for(const [av,txt] of [[A_RM,'radiation = matter'],[A_ML,'matter = dark energy']]){
    const x=CX(Math.log10(av)), anchor=x>C.x+C.w-150?'end':'start';
    s+='<line x1="'+x+'" y1="'+C.y+'" x2="'+x+'" y2="'+(C.y+C.h)+
       '" stroke="#8a8a8a" stroke-width="1" stroke-dasharray="4 4"/>'+
       '<text x="'+(x+(anchor==='end'?-6:6))+'" y="'+(C.y+14)+'" text-anchor="'+anchor+
       '" font-size="11" fill="#a9a9a9">'+txt+'</text>';
  }
  // the three curves
  const N=700;
  for(const [k,lab,col] of CURVES){
    let pts='';
    for(let i=0;i<=N;i++){
      const lv=LOGMIN+(LOGMAX-LOGMIN)*i/N;
      pts+=CX(lv).toFixed(2)+','+CY(curveShare(k,Math.pow(10,lv))).toFixed(2)+' ';
    }
    const kk=(k==='mat')?'dm':k;
    const op=(sel===null||sel===kk||(k==='mat'&&sel==='ob'))?1:0.3;
    s+='<g data-k="'+kk+'" opacity="'+op+'"><polyline points="'+pts+
       '" fill="none" stroke="'+col+'" stroke-width="2.4" stroke-linejoin="round"/>'+
       '<polyline points="'+pts+'" fill="none" stroke="transparent" stroke-width="14"/></g>';
  }
  // the marker
  const mx=CX(la);
  s+='<line x1="'+mx+'" y1="'+(C.y-8)+'" x2="'+mx+'" y2="'+(C.y+C.h+4)+
     '" stroke="#f4efe2" stroke-width="1.6"/>';
  for(const [k,lab,col] of CURVES){
    s+='<circle cx="'+mx+'" cy="'+CY(curveShare(k,Math.pow(10,la))).toFixed(2)+
       '" r="4" fill="'+col+'" stroke="#121212" stroke-width="1.4"/>';
  }
  // a legend for the curves, on the title line where no curve can reach it
  const items=CURVES.map(c=>[c[1],c[2],c[1].length*6.2+34]);
  let lx=C.x+C.w-items.reduce((t,i)=>t+i[2],0)+18;
  for(const [lab,col,wid] of items){
    s+='<rect x="'+lx+'" y="'+(C.y-22)+'" width="11" height="3" fill="'+col+'"/>'+
       '<text x="'+(lx+16)+'" y="'+(C.y-15)+'" font-size="11.5" fill="'+col+'">'+lab+'</text>';
    lx+=wid;
  }
  s+='</g>';
  return s;
}

/* ---- the whole drawing ---- */
function render(){
  const a=Math.pow(10,la), sh=shares(a), now=Math.abs(la)<1e-9;
  const faded=now?1:0.32;
  let s='<svg viewBox="0 0 '+W+' '+H+'" xmlns="http://www.w3.org/2000/svg" id="uvsvg">';
  s+='<rect width="'+W+'" height="'+H+'" fill="#121212"/>';
  s+='<text x="'+C.x+'" y="'+(C.y-18)+'" font-size="14" fill="#9a9a9a">'+
     'The share of all the energy, across the life of the universe</text>';
  s+='<text x="'+T.x+'" y="'+(T.y-18)+'" font-size="14" fill="#9a9a9a">'+
     'Everything, by energy content '+(now?'today':'when the universe was '+
     num(a)+' times its present size')+'</text>';
  s+='<g opacity="'+faded+'">';
  s+='<text x="'+B.x+'" y="'+(B.y-18)+'" font-size="14" fill="#9a9a9a">'+
     'The ordinary matter alone, atom by atom, as counted today</text>';
  s+='<text x="'+G.x+'" y="'+(G.y-18)+'" font-size="14" fill="#9a9a9a">'+
     'The ordinary matter of one large galaxy, the Milky Way</text>';
  // widths of the top bar at this moment, so the wedge can find the sliver
  const tw=TOP.map(d=>sh[d.k]/100*T.w);
  let obx=T.x; for(let i=0;i<TOP.length;i++){ if(TOP[i].k==='ob') break; obx+=tw[i]; }
  const obw=tw[TOP.findIndex(d=>d.k==='ob')];
  // the wedge from the sliver to the second bar
  s+='<path d="M'+obx+','+(T.y+T.h)+' L'+(obx+obw)+','+(T.y+T.h)+' L'+(B.x+B.w)+','+B.y+
     ' L'+B.x+','+B.y+' Z" fill="#ffb02e" fill-opacity="0.07" stroke="#ffb02e"'+
     ' stroke-opacity="0.35" stroke-width="1"/>';
  // the wedge from the galaxies segment, at the right end, to the third bar
  const btot=BAR.reduce((x,d)=>x+d.p,0);
  const bw=BAR.map(d=>d.p/btot*B.w);
  const gw=bw[bw.length-1], gx=B.x+B.w-gw;
  s+='<path d="M'+gx+','+(B.y+B.h)+' L'+(gx+gw)+','+(B.y+B.h)+' L'+(G.x+G.w)+','+G.y+
     ' L'+G.x+','+G.y+' Z" fill="#31d67a" fill-opacity="0.07" stroke="#31d67a"'+
     ' stroke-opacity="0.35" stroke-width="1"/>';
  let x=B.x;
  for(let i=0;i<BAR.length;i++){ s+=seg(B,BAR[i],x,bw[i],BAR[i].p); x+=bw[i]; }
  const gtot=GAL.reduce((x2,d)=>x2+d.p,0);
  const gws=GAL.map(d=>d.p/gtot*G.w);
  x=G.x;
  for(let i=0;i<GAL.length;i++){ s+=seg(G,GAL[i],x,gws[i],GAL[i].p); x+=gws[i]; }
  s+=lanes(B,BAR,bw)+lanes(G,GAL,gws);
  s+='</g>';
  x=T.x;
  for(let i=0;i<TOP.length;i++){ s+=seg(T,TOP[i],x,tw[i],sh[TOP[i].k]); x+=tw[i]; }
  s+=lanes(T,TOP,tw);
  s+=panel();
  s+='</svg>';
  el.innerHTML=s;
}

/* ---- the card ---- */
function show(k){
  const d=TOP.find(t=>t.k===k)||BAR.find(t=>t.k===k)||GAL.find(t=>t.k===k);
  if(!d) return;
  const inTop=TOP.indexOf(d)>=0;
  const sh=shares(Math.pow(10,la));
  const p=inTop?sh[d.k]:d.p;
  const P=document.getElementById('pct');
  P.textContent=inTop?pct(p):d.p+'%';
  P.style.color=d.c;
  document.getElementById('segTxt').textContent=d.t;
  document.getElementById('bodyTxt').textContent=d.b;
  const at=document.getElementById('atTxt');
  if(inTop){
    const nowsh=shares(1)[d.k];
    at.textContent=Math.abs(la)<1e-9 ? 'share of everything today'
      : 'share of everything when the universe was '+num(Math.pow(10,la))+
        ' times its present size. Today it is '+pct(nowsh)+'.';
  } else at.textContent='';
  document.getElementById('srcTxt').textContent=
    d.s+(inTop?'':BAR.includes(d)?' · share of the ordinary matter'
        :' · share of the galaxy’s ordinary matter');
}
let card=null;
function refresh(){ render(); if(card) show(card); readouts(); }
function readouts(){
  const a=Math.pow(10,la);
  document.getElementById('rdA').textContent=num(a)+(Math.abs(la)<1e-9?' (today)':'');
  document.getElementById('rdZ').textContent=fmtZ(1/a-1);
  document.getElementById('rdT').textContent=fmtT(TCMB/a);
  document.getElementById('rdAge').textContent=fmtAge(age(a));
  const sl=document.getElementById('scale');
  if(+sl.value!==Math.round(la*100)) sl.value=Math.round(la*100);
  for(const b of document.querySelectorAll('#presets button'))
    b.setAttribute('aria-pressed', Math.abs(+b.dataset.la-la)<5e-3 ? 'true':'false');
}
function setLa(v){
  la=Math.min(LOGMAX,Math.max(LOGMIN,v));
  refresh();
}

/* ---- moments worth a button ---- */
const MOMENTS=[
  [LOGMIN,'the earliest here'],
  [Math.log10(A_RM),'radiation and matter equal'],
  [Math.log10(1/1091),'the background is released'],
  [Math.log10(1/21),'the first stars'],
  [Math.log10(A_ML),'matter and dark energy equal'],
  [0,'today'],
  [LOGMAX,'ten times this size'],
];
document.getElementById('presets').innerHTML=MOMENTS.map(
  m=>'<button type="button" data-la="'+m[0]+'">'+m[1]+'</button>').join('');
document.getElementById('presets').addEventListener('click',e=>{
  const b=e.target.closest('button'); if(b) setLa(+b.dataset.la);
});
document.getElementById('scale').addEventListener('input',e=>setLa(+e.target.value/100));

/* ---- pointing at the drawing ---- */
el.addEventListener('pointerover',e=>{
  const g=e.target.closest('[data-k]');
  if(g){ card=g.getAttribute('data-k'); show(card); }
});
el.addEventListener('click',e=>{
  if(swallow){ swallow=false; return; }
  const g=e.target.closest('[data-k]');
  sel = g ? (sel===g.getAttribute('data-k')?null:g.getAttribute('data-k')) : null;
  if(g) card=g.getAttribute('data-k');
  refresh();
});
// dragging across the history panel moves the moment
function fromEvent(e){
  const svg=document.getElementById('uvsvg'), r=svg.getBoundingClientRect();
  const px=(e.clientX-r.left)/r.width*W, py=(e.clientY-r.top)/r.height*H;
  if(py<C.y-16||py>C.y+C.h+8) return null;
  return XC(px);
}
let dragging=false, swallow=false;
el.addEventListener('pointerdown',e=>{
  const v=fromEvent(e);
  if(v===null) return;
  dragging=true; swallow=true; el.setPointerCapture&&el.setPointerCapture(e.pointerId);
  setLa(v); e.preventDefault();
});
el.addEventListener('pointermove',e=>{ if(dragging){ const v=fromEvent(e); if(v!==null) setLa(v); } });
window.addEventListener('pointerup',()=>{ dragging=false; });

card='de';
refresh();
show('de');
</script>
</body>
</html>
"""

html = (HTML.replace("__TOP__", top_js).replace("__BAR__", bar_js)
        .replace("__GAL__", gal_js))
html = apa.css_pass(html)
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} bytes): {len(TOP)} components, "
      f"{len(BARYONS)} baryon phases, {len(GALAXY)} galaxy parts")
