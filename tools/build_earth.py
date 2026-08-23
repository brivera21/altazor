#!/usr/bin/env python3
"""Generate earth.html: the Earth as continents, with what covers it.

No countries. The land is drawn from real coastlines, split into the seven
conventional continents, and shaded by the main Koppen-Geiger climate group.

Data, all offline:
  GSHHG full coastlines, distributed with basemap-data-hires. Level 1 is land,
  2 lakes, 3 islands inside lakes, 5 the Antarctic ice front. Africa, Eurasia,
  the two Americas and Australia are already separate polygons in that data, so
  no isthmus has to be cut; only Europe and Asia need parting, along the Urals,
  the Ural river, the Kuma-Manych depression and the Turkish straits.
  Koppen-Geiger present-day classification at 1 km, Beck et al. 2018, as
  redistributed in the kgcpy package. Reduced to its five main groups.

The two layers are packed into one grayscale PNG: each byte is
group * 8 + continent, so the page can read climate and continent from a single
image and the whole map costs about 80 KB.

Areas quoted on the page are the published ones, not measured off this raster.
The raster is 1/6 of a degree, which inflates every coastline by roughly half a
pixel; see verify_earth.py, which checks the two against each other.

Usage: python3 build_earth.py      (needs /home/claude/earth/*.npy)
"""

import base64
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image

OUT = Path(__file__).parent.parent / "earth.html"
DATA = Path("/home/claude/earth")

SNAPSHOT = "August 2026"

CONT = ["Africa", "Asia", "Europe", "North America", "South America",
        "Antarctica", "Australia and Oceania"]

# Published areas, km2. CIA World Factbook and standard references.
AREA = {"Asia": 44_579_000, "Africa": 30_370_000, "North America": 24_709_000,
        "South America": 17_840_000, "Antarctica": 14_200_000,
        "Europe": 10_180_000, "Australia and Oceania": 8_600_000}

EARTH_KM2 = 510_072_000
OCEAN_KM2 = 361_132_000
LAND_KM2 = 148_940_000
INLAND_WATER_KM2 = 5_000_000        # lakes and rivers, Verpoorter et al. 2014

# Four hues validated against the ocean tone with the data-viz palette checker
# (all pairs, dark mode): lightness band, chroma floor, normal-vision floor and
# contrast all pass; worst CVD pair is amber against green at 7.9, which is the
# 6-8 band and legal only with secondary encoding. That encoding is the legend,
# the hover readout naming the climate, and the labelled bars in the panel.
# Polar is deliberately outside the categorical band: ice reads as white, and
# lightness alone separates it from all four under every kind of colour vision.
GROUPS = [
    ("A", "Tropical", "#47a566", "Hot all year, and wet enough that "
     "something grows through it"),
    ("B", "Arid", "#b17600", "More water leaves than arrives: deserts and "
     "the steppe around them"),
    ("C", "Temperate", "#a84e7c", "Mild winters, no month averaging below "
     "minus three"),
    ("D", "Continental", "#386bb6", "Warm summers and hard winters, which "
     "needs a landmass to sit in"),
    ("E", "Polar", "#e3ecf5", "No month averaging above ten: tundra and "
     "permanent ice"),
]
C_OCEAN = "#0d1a26"
C_COAST = "#5f7f9c"


def main():
    cid = np.load(DATA / "cid.npy")
    clim = np.load(DATA / "clim.npy")
    H, W = cid.shape
    mix = json.load(open(DATA / "mix.json"))

    packed = (clim.astype(np.uint16) * 8 + cid).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(packed, "L").save(buf, "PNG", optimize=True, compress_level=9)
    png = base64.b64encode(buf.getvalue()).decode()

    wt = np.repeat(np.cos(np.radians(90 - (np.arange(H) + 0.5) * 180 / H))[:, None], W, 1)
    conts = []
    for i, nm in enumerate(CONT, 1):
        conts.append(dict(i=i, n=nm, km2=AREA[nm],
                          share=round(AREA[nm] / LAND_KM2 * 100, 1),
                          mix=mix[nm]["mix"]))
    conts.sort(key=lambda c: -c["km2"])
    world_mix = mix["_all land"]["mix"]

    def pct(x, of):
        return f"{x / of * 100:.1f}"

    legend = "\n".join(
        f'<div class="lg"><span class="sw" style="background:{c}"></span>'
        f'<span><b>{k} {n}</b><br><span class="ld">{d}</span></span></div>'
        for k, n, c, d in GROUPS)

    js = {"png": png, "w": W, "h": H,
          "colors": [c for _, _, c, _ in GROUPS],
          "keys": [f"{k} {n.lower()}" for k, n, _, _ in GROUPS],
          "conts": conts, "world": world_mix,
          "ocean": C_OCEAN, "coast": C_COAST}

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Earth · Altazor</title>
<style>
:root{{color-scheme:dark;
--ink:#e6e6e6; --ink2:#9aa3ad; --ink3:#7d848c;
--bg:#121212; --panel:#171a1d; --line:#2b2f34; --accent:#58a6ff;
--sea:{C_OCEAN};}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);
font:400 16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
main{{max-width:1180px;margin:0 auto;padding:2rem 1.25rem 4rem}}
header.site{{border-top:4px solid var(--accent);padding-top:22px;margin-bottom:26px;
display:flex;align-items:baseline;gap:18px;flex-wrap:wrap}}
.brand{{font-weight:700;font-size:20px;letter-spacing:.1em;text-decoration:none;color:var(--ink)}}
.brand:hover{{color:var(--accent)}}
nav.site a{{color:var(--ink2);text-decoration:none;font-size:14px}}
nav.site a:hover{{color:var(--accent)}}
h1{{font-size:1.7rem;font-weight:600;margin:0 0 .2rem}}
.stamp{{color:var(--ink3);font-size:.82rem;margin:0 0 1.4rem}}

.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(158px,1fr));
gap:10px;margin:0 0 14px}}
.tile{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:11px 14px}}
.tile .k{{font-size:11px;color:var(--ink3);text-transform:uppercase;letter-spacing:.07em}}
.tile .v{{font-size:1.32rem;font-weight:650;margin-top:3px;font-variant-numeric:tabular-nums}}
.tile .v small{{font-size:.78rem;font-weight:400;color:var(--ink2)}}

.stage{{display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap}}
.mapwrap{{flex:1 1 640px;min-width:320px;position:relative}}
canvas{{width:100%;height:auto;display:block;border-radius:10px;
border:1px solid var(--line);background:var(--sea);cursor:crosshair}}
.side{{flex:0 0 302px;max-width:100%}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px}}
.card h2{{font-size:1.02rem;font-weight:600;margin:0 0 2px}}
.card .sub{{font-size:.82rem;color:var(--ink3);margin-bottom:10px}}
.row{{display:flex;justify-content:space-between;font-size:.88rem;padding:3px 0}}
.row span:last-child{{font-variant-numeric:tabular-nums;color:var(--ink2)}}
.bars{{margin-top:12px}}
.bar{{display:grid;grid-template-columns:96px 1fr 46px;align-items:center;
gap:8px;font-size:.8rem;padding:2px 0}}
.bar .t{{color:var(--ink2)}}
.bar .track{{display:block;background:#22262b;border-radius:3px;height:9px;overflow:hidden}}
.bar .fill{{display:block;height:100%;border-radius:3px;min-width:2px}}
.bar .p{{text-align:right;font-variant-numeric:tabular-nums;color:var(--ink2)}}

.controls{{display:flex;gap:.7rem;align-items:center;margin:12px 0 0;flex-wrap:wrap;font-size:.88rem}}
button{{font:inherit;font-size:.85rem;background:none;color:var(--ink);
border:1px solid var(--line);border-radius:999px;padding:5px 13px;cursor:pointer}}
button:hover{{background:#20242a}}
button[aria-pressed="true"]{{border-color:var(--accent);color:var(--accent)}}

.legend{{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));
gap:9px 16px;margin:16px 0 0}}
.lg{{display:flex;gap:9px;align-items:flex-start;font-size:.83rem}}
.sw{{flex:0 0 13px;height:13px;border-radius:3px;margin-top:3px;
border:1px solid rgba(255,255,255,.18)}}
.ld{{color:var(--ink3);font-size:.78rem}}

.notes{{margin-top:2.6rem;border-top:1px solid var(--line);padding-top:1.5rem;
color:var(--ink2);font-size:.95rem;max-width:74ch}}
.notes h2{{font-size:1.05rem;font-weight:400;color:var(--ink);margin:0 0 .6rem}}
.notes p{{margin:0 0 1rem}}
.method{{margin-top:1.5rem;color:var(--ink3);font-size:.88rem;max-width:78ch}}
.method h2{{font-size:.95rem;font-weight:400;color:var(--ink2);margin:0 0 .6rem}}
.method p{{margin:0 0 .9rem}}
.method a{{color:var(--accent)}}
table.mix{{border-collapse:collapse;font-size:.85rem;margin:.4rem 0 1rem;width:100%}}
table.mix th,table.mix td{{text-align:right;padding:3px 8px;border-bottom:1px solid var(--line)}}
table.mix th:first-child,table.mix td:first-child{{text-align:left}}
table.mix th{{color:var(--ink3);font-weight:400}}
table.mix td{{font-variant-numeric:tabular-nums}}
</style>
</head>
<body>
<main>
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library</a></nav>
</header>

<h1>The Earth</h1>
<p class="stamp">Coastlines from GSHHG; climates from Beck and others, 2018.</p>

<div class="tiles">
  <div class="tile"><div class="k">Surface area</div>
    <div class="v">510,072,000 <small>km²</small></div></div>
  <div class="tile"><div class="k">Ocean</div>
    <div class="v">{pct(OCEAN_KM2, EARTH_KM2)}% <small>361,132,000 km²</small></div></div>
  <div class="tile"><div class="k">Land</div>
    <div class="v">{pct(LAND_KM2, EARTH_KM2)}% <small>148,940,000 km²</small></div></div>
  <div class="tile"><div class="k">Lakes and rivers</div>
    <div class="v">{pct(INLAND_WATER_KM2, EARTH_KM2)}% <small>about 5,000,000 km²</small></div></div>
  <div class="tile"><div class="k">Of all water, fresh</div>
    <div class="v">2.5% <small>and 69% of that is ice</small></div></div>
</div>

<div class="stage">
  <div class="mapwrap"><canvas id="map"></canvas></div>
  <div class="side"><div class="card">
    <h2 id="selName">All land</h2>
    <div class="sub" id="selSub">every continent together</div>
    <div class="row"><span>Area</span><span id="selArea"></span></div>
    <div class="row"><span>Share of land</span><span id="selShare"></span></div>
    <div class="row"><span>Share of the surface</span><span id="selSurf"></span></div>
    <div class="bars" id="bars"></div>
  </div></div>
</div>

<div class="controls">
  <button id="bClim" aria-pressed="true">Climate</button>
  <button id="bGrat" aria-pressed="false">Tropics and circles</button>
  <span id="hint" style="color:var(--ink3)">A continent under the cursor fills the panel</span>
</div>

<div class="legend">{legend}</div>

<div class="notes">
<h2>About the map</h2>
<p>Every continent under the cursor fills the panel with its area and the
climates that cover it. The colours are the five main Koppen groups, the
classification that sorts land by what its temperature and rainfall do through
the year rather than by where it sits.</p>
<p>The projection is equirectangular, which keeps latitude and longitude square
and stretches everything toward the poles. Greenland and Antarctica look far
larger here than they are, which is why the areas are given as numbers.</p>
</div>

<div class="method">
<h2>Method and sources</h2>
<p>Coastlines are GSHHG at full resolution, the same shoreline data used for
nautical work, rasterised to a sixth of a degree. Africa, Eurasia, the two
Americas and Australia are separate polygons in that data, so Suez and Panama
need no cutting. Europe and Asia do: they are parted along the Urals, down the
Ural river to the Caspian, across the Kuma-Manych depression to the Black Sea,
and through the Bosphorus. That line is a convention, not a coastline, and so is
the placing of the islands, which follow the usual groupings rather than the
nearest shore.</p>
<p>Climates are the Koppen-Geiger present-day map of Beck and others, 2018, at
one kilometre, reduced to its five main groups by first letter and downsampled
by majority vote. The shares below are area weighted by the cosine of latitude,
so a pixel near the pole counts for what it is worth.</p>
<p>Areas are the published figures rather than measurements off this raster. At
a sixth of a degree every coastline gains about half a pixel, which inflates
small and ragged landmasses; the raster and the published figures agree to
within a few percent for six continents, and Australia with Oceania runs higher
because political tables count Indonesian New Guinea under Asia while an island
belongs to one landmass.</p>
<p>Surface, ocean and land areas: standard references, and the water budget
follows the United States Geological Survey summary of Gleick, 1996. Lake and
river area is from Verpoorter and others, 2014.</p>
</div>
</main>
<script>
const D = {json.dumps(js)};
const cv = document.getElementById('map'), ctx = cv.getContext('2d');
let W = D.w, H = D.h;
let showClim = true, showGrat = false, hover = 0, sel = 0;
let ids = null, base = null;

const img = new Image();
img.onload = () => {{
  const off = document.createElement('canvas');
  off.width = W; off.height = H;
  const o = off.getContext('2d');
  o.drawImage(img, 0, 0);
  const d = o.getImageData(0, 0, W, H).data;
  ids = new Uint8Array(W * H);
  const grp = new Uint8Array(W * H);
  for (let i = 0, p = 0; i < d.length; i += 4, p++) {{
    ids[p] = d[i] & 7;
    grp[p] = d[i] >> 3;
  }}
  base = {{ grp }};
  cv.width = W; cv.height = H;
  paint();
}};
img.src = 'data:image/png;base64,' + D.png;

function rgb(hex) {{
  return [parseInt(hex.slice(1,3),16), parseInt(hex.slice(3,5),16), parseInt(hex.slice(5,7),16)];
}}
const SEA = rgb(D.ocean), COAST = rgb(D.coast);
const CLR = D.colors.map(rgb);
const LANDFLAT = rgb('#5c6672');

function paint() {{
  if (!ids) return;
  const out = ctx.createImageData(W, H), o = out.data;
  const g = base.grp;
  for (let p = 0, i = 0; p < ids.length; p++, i += 4) {{
    let c;
    if (ids[p] === 0) c = SEA;
    else if (showClim && g[p] > 0) c = CLR[g[p] - 1];
    else c = LANDFLAT;
    // the focused continent keeps its exact palette colour, so it still
    // matches the legend; everything else is dimmed instead of it being lit
    let f = (hover && ids[p] !== 0 && ids[p] !== hover) ? 0.48 : 1;
    o[i] = Math.min(255, c[0] * f);
    o[i+1] = Math.min(255, c[1] * f);
    o[i+2] = Math.min(255, c[2] * f);
    o[i+3] = 255;
  }}
  // a one pixel coast, from land pixels that touch water
  for (let y = 1; y < H - 1; y++) {{
    for (let x = 1; x < W - 1; x++) {{
      const p = y * W + x;
      if (!ids[p]) continue;
      if (ids[p-1] && ids[p+1] && ids[p-W] && ids[p+W]) continue;
      const i = p * 4;
      o[i] = COAST[0]; o[i+1] = COAST[1]; o[i+2] = COAST[2];
    }}
  }}
  ctx.putImageData(out, 0, 0);
  if (showGrat) graticule();
}}

function graticule() {{
  ctx.save();
  // the canvas is far wider than it is drawn, so type and strokes are sized
  // from the raster, not in CSS pixels, or the labels come out unreadable
  const u = W / 1000;
  ctx.strokeStyle = 'rgba(255,255,255,0.34)';
  ctx.setLineDash([9 * u, 7 * u]); ctx.lineWidth = 1.6 * u;
  ctx.font = `${{Math.round(11 * u)}}px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`;
  ctx.fillStyle = 'rgba(255,255,255,0.78)';
  for (const [lat, name] of [[66.5634,'Arctic Circle'], [23.4366,'Tropic of Cancer'],
                             [0,'Equator'], [-23.4366,'Tropic of Capricorn'],
                             [-66.5634,'Antarctic Circle']]) {{
    const y = (90 - lat) * H / 180;
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    ctx.fillText(name, 10 * u, y - 6 * u);
  }}
  ctx.restore();
}}

const el = id => document.getElementById(id);
const fmt = n => n.toLocaleString('en-US');

function show(i) {{
  const c = i ? D.conts.find(c => c.i === i) : null;
  const mix = c ? c.mix : D.world;
  el('selName').textContent = c ? c.n : 'All land';
  el('selSub').textContent = c ? 'continent' : 'every continent together';
  el('selArea').textContent = fmt(c ? c.km2 : {LAND_KM2}) + ' km²';
  el('selShare').textContent = (c ? c.share.toFixed(1) : '100.0') + '%';
  el('selSurf').textContent =
    (((c ? c.km2 : {LAND_KM2}) / {EARTH_KM2}) * 100).toFixed(1) + '%';
  el('bars').innerHTML = mix.map((v, k) =>
    `<div class="bar"><span class="t">${{D.keys[k]}}</span>` +
    `<span class="track"><span class="fill" style="width:${{v}}%;` +
    `background:${{D.colors[k]}}"></span></span>` +
    `<span class="p">${{v.toFixed(1)}}%</span></div>`).join('');
}}

function at(ev) {{
  const r = cv.getBoundingClientRect();
  const x = Math.floor((ev.clientX - r.left) / r.width * W);
  const y = Math.floor((ev.clientY - r.top) / r.height * H);
  if (x < 0 || y < 0 || x >= W || y >= H || !ids) return 0;
  return ids[y * W + x];
}}
cv.addEventListener('mousemove', e => {{
  const i = at(e);
  if (i !== hover) {{ hover = i; paint(); show(i || sel); }}
}});
cv.addEventListener('mouseleave', () => {{ hover = 0; paint(); show(sel); }});
cv.addEventListener('click', e => {{ sel = at(e); show(sel || hover); }});
el('bClim').addEventListener('click', () => {{
  showClim = !showClim;
  el('bClim').setAttribute('aria-pressed', showClim);
  paint();
}});
el('bGrat').addEventListener('click', () => {{
  showGrat = !showGrat;
  el('bGrat').setAttribute('aria-pressed', showGrat);
  paint();
}});
show(0);
window.__earth = () => ({{ ids: !!ids, W, H, showClim, showGrat, hover, sel,
  conts: D.conts, world: D.world }});
</script>
</body>
</html>
"""
    OUT.write_text(doc, encoding="utf-8")
    print(f"wrote {OUT} ({len(doc):,} bytes): {W}x{H} raster, "
          f"{len(png)/1024:.0f} KB of base64, {len(conts)} continents")


if __name__ == "__main__":
    main()
