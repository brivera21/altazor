#!/usr/bin/env python3
"""Generate universe.html, The Universe: what the cosmos is made of.

Two stacked bars joined by a wedge. The top bar is the present-day energy
budget from Planck 2018 VI; the thin sliver of ordinary matter opens into a
second bar carrying the baryon census of Shull, Smith and Danforth (2012),
with the once-missing share drawn hatched and its card telling how fast radio
bursts found it in 2020. Hovering or tapping a segment fills the side card.

Usage: python3 build_universe.py
"""

import json
import apa
from pathlib import Path

OUT = Path(__file__).parent.parent / "universe.html"

# (key, label, percent, color, hatched, card title, card text, source line)
TOP = [
    ("de", "Energía oscura" if False else "Dark energy", 68.5, "#b48cf2", False,
     "Dark energy",
     "The component that accelerates the expansion of the universe. It enters "
     "the equations as a constant energy of space itself, and nothing beyond "
     "that constancy has been measured about it.",
     "Planck 2018 VI, baseline model"),
    ("dm", "Dark matter", 26.4, "#58a6ff", False,
     "Dark matter",
     "Matter that gravitates but neither emits nor absorbs light. It holds "
     "galaxies and clusters together and shapes the cosmic web; every attempt "
     "to detect a particle of it has so far come back empty.",
     "Planck 2018 VI, baseline model"),
    ("ob", "Ordinary matter", 4.9, "#ffb02e", False,
     "Ordinary matter",
     "Everything made of atoms: every star, planet, gas cloud and living "
     "thing. The bar below opens this sliver into where those atoms actually "
     "are.",
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

assert abs(sum(p for *_x, p, _c, _h, _t, _b, _s in
               [(k, l, p, c, h, t, b, s) for k, l, p, c, h, t, b, s in TOP]) - 99.8) < 0.5
assert abs(sum(p for _k, _l, p, *_r in BARYONS) - 99.7) < 0.5
assert abs(sum(p for _k, _l, p, *_r in GALAXY) - 99.9) < 0.5
assert BARYONS[-1][0] == "gal", "Galaxies must sit at the right end"

def _js(rows):
    return json.dumps([{"k": k, "l": l, "p": p, "c": c, "h": h,
                        "t": t, "b": b, "s": s}
                       for k, l, p, c, h, t, b, s in rows],
                      separators=(",", ":"))

top_js, bar_js, gal_js = _js(TOP), _js(BARYONS), _js(GALAXY)

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
<div class="stage">
  <div id="diagram"></div>
  <div class="side"><div class="card">
    <div id="pct"></div>
    <div id="segTxt">Hover a segment</div>
    <div id="bodyTxt"></div>
    <div id="srcTxt"></div>
  </div></div>
</div>
<p class="note">The top bar is everything there is, by present-day energy
content. Ordinary matter, the thin amber sliver, opens below into where its
atoms actually sit, and the galaxies segment opens in turn into what one
large galaxy is made of, with the Milky Way as the exemplar. A segment under
the cursor fills the card.</p>
<p class="note">Photons of the microwave background add about five
thousandths of a percent and the known neutrino mass roughly a tenth of a
percent; both are too thin to draw. The bottom bar counts only ordinary
matter: the galaxy as a whole sits in a dark matter halo that outweighs
everything drawn there by more than ten to one.</p>
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
const W=980,H=850;
const T={x:20,y:60,w:940,h:110}, B={x:20,y:330,w:940,h:110},
      G={x:20,y:640,w:940,h:110};

const el=document.getElementById('diagram');
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
let sel=null;

function seg(row,d,x,w,i,list){
  const dash=d.h?' stroke-dasharray="5 4"':'';
  const op=(sel===null||sel===d.k)?1:0.35;
  let s=`<g data-k="${d.k}" style="cursor:default" opacity="${op}">
    <rect x="${x}" y="${row.y}" width="${Math.max(w,1.2)}" height="${row.h}" rx="4"
      fill="${d.c}" fill-opacity="${d.h?0.35:0.85}" stroke="${d.c}" stroke-width="1.4"${dash}/>`;
  if(w>90) s+=`<text x="${x+w/2}" y="${row.y+row.h/2-4}" text-anchor="middle"
      font-size="14.5" font-weight="700" fill="#0b0b0b" pointer-events="none">${esc(d.l)}</text>
    <text x="${x+w/2}" y="${row.y+row.h/2+16}" text-anchor="middle" font-size="13"
      fill="#0b0b0b" pointer-events="none">${d.p}%</text>`;
  else if(w>34) s+=`<text x="${x+w/2}" y="${row.y+row.h/2+5}" text-anchor="middle"
      font-size="12.5" font-weight="700" fill="#0b0b0b" pointer-events="none">${d.p}%</text>`;
  s+='</g>';
  return s;
}
function lanes(row,list){
  // labels under a bar for its narrow segments, each dropped to the first
  // lane where it fits
  let s='', x=row.x; const ends=[];
  const tot=list.reduce((a,d)=>a+d.p,0);
  for(const d of list){
    const w=d.p/tot*row.w;
    if(w<=90){
      const tw=d.l.length*6.4+10;
      const lx=Math.min(row.x+row.w-tw/2,Math.max(row.x+tw/2,x+w/2));
      let lane=0;
      while(lane<ends.length && ends[lane]>lx-tw/2) lane++;
      ends[lane]=lx+tw/2+10;
      const ly=row.y+row.h+22+lane*19;
      s+=`<g data-k="${d.k}" style="cursor:default">
        <line x1="${x+w/2}" y1="${row.y+row.h+2}" x2="${lx}" y2="${ly-11}" stroke="${d.c}" stroke-width="1" opacity="0.7"/>
        <text x="${lx}" y="${ly}" text-anchor="middle" font-size="12" fill="${d.c}">${esc(d.l)}</text></g>`;
    }
    x+=w;
  }
  return s;
}
function render(){
  let s=`<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" id="uvsvg">`;
  s+=`<rect width="${W}" height="${H}" fill="#121212"/>`;
  s+=`<text x="${T.x}" y="${T.y-18}" font-size="14" fill="#9a9a9a">Everything, by energy content today</text>`;
  s+=`<text x="${B.x}" y="${B.y-18}" font-size="14" fill="#9a9a9a">The ordinary matter alone, atom by atom</text>`;
  s+=`<text x="${G.x}" y="${G.y-18}" font-size="14" fill="#9a9a9a">The ordinary matter of one large galaxy, the Milky Way</text>`;
  // the wedge from the sliver to the second bar
  const obw=TOP[2].p/100*T.w, obx=T.x+(TOP[0].p+TOP[1].p)/100*T.w;
  s+=`<path d="M${obx},${T.y+T.h} L${obx+obw},${T.y+T.h} L${B.x+B.w},${B.y} L${B.x},${B.y} Z"
    fill="#ffb02e" fill-opacity="0.07" stroke="#ffb02e" stroke-opacity="0.35" stroke-width="1"/>`;
  // the wedge from the galaxies segment, at the right end, to the third bar
  const btot=BAR.reduce((a,d)=>a+d.p,0);
  const gw=BAR[BAR.length-1].p/btot*B.w, gx=B.x+B.w-gw;
  s+=`<path d="M${gx},${B.y+B.h} L${gx+gw},${B.y+B.h} L${G.x+G.w},${G.y} L${G.x},${G.y} Z"
    fill="#31d67a" fill-opacity="0.07" stroke="#31d67a" stroke-opacity="0.35" stroke-width="1"/>`;
  let x=T.x;
  for(const d of TOP){ const w=d.p/100*T.w; s+=seg(T,d,x,w); x+=w; }
  x=B.x;
  for(const d of BAR){ const w=d.p/btot*B.w; s+=seg(B,d,x,w); x+=w; }
  x=G.x;
  const gtot=GAL.reduce((a,d)=>a+d.p,0);
  for(const d of GAL){ const w=d.p/gtot*G.w; s+=seg(G,d,x,w); x+=w; }
  s+=lanes(B,BAR)+lanes(G,GAL);
  s+='</svg>';
  el.innerHTML=s;
}
function show(k){
  const d=TOP.find(t=>t.k===k)||BAR.find(t=>t.k===k)||GAL.find(t=>t.k===k);
  if(!d) return;
  document.getElementById('pct').textContent=d.p+'%';
  document.getElementById('pct').style.color=d.c;
  document.getElementById('segTxt').textContent=d.t;
  document.getElementById('bodyTxt').textContent=d.b;
  document.getElementById('srcTxt').textContent=
    d.s+(TOP.includes(d)?' \\u00b7 share of everything'
        :BAR.includes(d)?' \\u00b7 share of the ordinary matter'
        :' \\u00b7 share of the galaxy\\u2019s ordinary matter');
}
el.addEventListener('pointerover',e=>{
  const g=e.target.closest('[data-k]');
  if(g){ show(g.getAttribute('data-k')); }
});
el.addEventListener('click',e=>{
  const g=e.target.closest('[data-k]');
  sel = g ? (sel===g.getAttribute('data-k')?null:g.getAttribute('data-k')) : null;
  render();
  if(g) show(g.getAttribute('data-k'));
});
render();
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
