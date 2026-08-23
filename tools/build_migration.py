#!/usr/bin/env python3
"""Generate migration.html, Homo Sapiens Migration.

A world map with a clock that runs on a logarithmic scale, from three hundred
thousand years ago to now. Almost nothing about our species is evenly spread
through that span: the first two hundred and eighty thousand years happen in
Africa and leave a handful of sites, and then everything else happens in the
last five per cent of it. A linear slider spends its whole travel on the empty
part. A logarithmic one gives the deep past room and still leaves the last few
centuries a third of the bar.

Three layers move with the clock.

  Sites. Thirty eight places where Homo sapiens is attested, each appearing at
  the date its own evidence gives, with that evidence named. The five debated
  and four contested ones are drawn differently and say what the argument is.
  One entry in the data is marked refuted and is not drawn at all.

  The order of the spread. Each site is joined to the nearest site that was
  already occupied when it was reached. That is a picture of the sequence, not
  of anyone's route: nobody walked those lines, and the real paths are not
  known.

  Population. The world total runs the whole way. The split by continent only
  starts at seven thousand years ago, because the figures before that are a
  model projected backwards rather than evidence, and they say things that
  cannot be true, like more people in the Americas than in Africa at the end of
  the ice age. The page says so instead of drawing them.

The data is in sapiens_data.py, which carries its sources, its ranges and its
arguments, and validates its own consistency.

Usage: python3 build_migration.py      (needs /home/claude/earth/*.npy)
"""

import base64
import io
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

from sapiens_data import (ARRIVALS, POPULATION_BY_CONTINENT,
                          POPULATION_CENSUS, CONTESTED)

OUT = Path(__file__).parent.parent / "migration.html"
DATA = Path("/home/claude/earth")

TERRAIN = ["#0a1e33", "#2f6b34", "#b09055", "#4f8442", "#46693c", "#e2e9ee"]
C_COAST = "#8fa3ae"

# Before this, the continental split is a back-projection and not evidence.
CONT_FROM = 7000
CONTINENTS = ["Africa", "Asia", "Europe", "North America", "South America",
              "Oceania"]
CONT_COLOUR = {"Africa": "#b17600", "Asia": "#47a566", "Europe": "#a84e7c",
               "North America": "#386bb6", "South America": "#7e6bd0",
               "Oceania": "#3fa8a0"}

FACTS = [
    ("Oldest fossils", "315,000 years",
     "Jebel Irhoud in Morocco, which is nowhere near East Africa"),
    ("Out of Africa", "about 50,000 years",
     "the dispersal that left descendants everywhere outside Africa"),
    ("Farming", "about 11,000 years",
     "after which the population curve stops being flat"),
    ("Time scale", "logarithmic",
     "or the first ninety five per cent of the story is one twitch of a slider"),
]


def as_png(a):
    buf = io.BytesIO()
    Image.fromarray(a, "L").save(buf, "PNG", optimize=True, compress_level=9)
    return base64.b64encode(buf.getvalue()).decode()


def great_circle(a, b):
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    d = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) \
        * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * math.asin(min(1, math.sqrt(d)))


def main():
    cid = np.load(DATA / "cid.npy")
    clim = np.load(DATA / "clim.npy")
    H, W = cid.shape
    ground = np.where(cid > 0, clim, 0).astype(np.uint8)

    sites = [a for a in ARRIVALS if a[5] != "refuted"]
    sites.sort(key=lambda a: -a[3])
    # Each site is joined to the nearest one already occupied. The order is a
    # fact of the dates; the line between them is not a route.
    links = []
    for i, s in enumerate(sites):
        if i == 0:
            continue
        earlier = sites[:i]
        j = min(range(i), key=lambda k: great_circle(
            (s[1], s[2]), (earlier[k][1], earlier[k][2])))
        links.append({"a": j, "b": i,
                      "km": round(great_circle((s[1], s[2]),
                                               (sites[j][1], sites[j][2])))})

    js = {
        "png": as_png(ground), "w": W, "h": H,
        "terrain": TERRAIN, "coast": C_COAST,
        "sites": [{"n": n, "la": la, "lo": lo, "t": t, "s": site,
                   "c": conf, "d": note} for n, la, lo, t, site, conf, note
                  in sites],
        "links": links,
        "pop": [[t, p] for t, p, _ in POPULATION_CENSUS],
        "popsrc": {str(t): src for t, p, src in POPULATION_CENSUS},
        "cont": [[t, [d[c] for c in CONTINENTS]]
                 for t, d in POPULATION_BY_CONTINENT if t <= CONT_FROM],
        "continents": CONTINENTS,
        "ccolour": [CONT_COLOUR[c] for c in CONTINENTS],
        "contFrom": CONT_FROM,
        "argued": {k: v for k, v in CONTESTED.items()},
    }
    blob = json.dumps(js, separators=(",", ":"))

    facts = "\n".join(          # ya no se usa: las casillas de arriba cambian
        f'<div class="tile"><div class="k">{n}</div>'
        f'<div class="v">{v}</div><div class="d">{d}</div></div>'
        for n, v, d in FACTS)

    doc = TEMPLATE.replace("__DATA__", blob).replace("__FACTS__", facts)
    OUT.write_text(doc, encoding="utf-8")
    print(f"wrote {OUT} ({len(doc):,} bytes): {len(sites)} sites, "
          f"{len(links)} links, {len(js['pop'])} population points, "
          f"{len(js['cont'])} continental snapshots from {CONT_FROM} BP")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Homo Sapiens Migration &middot; Altazor</title>
<style>
:root{color-scheme:dark;
--ink:#e6e6e6; --ink2:#9aa3ad; --ink3:#7d848c;
--bg:#121212; --panel:#171a1d; --line:#2b2f34; --accent:#58a6ff;
--warm:#f2c66b; --sea:#0a1e33;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:400 16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
main{max-width:1180px;margin:0 auto;padding:2rem 1.25rem 4rem}
header.site{border-top:4px solid var(--accent);padding-top:22px;margin-bottom:26px;
display:flex;align-items:baseline;gap:18px;flex-wrap:wrap}
.brand{font-weight:700;font-size:20px;letter-spacing:.1em;text-decoration:none;color:var(--ink)}
.brand:hover{color:var(--accent)}
nav.site a{color:var(--ink2);text-decoration:none;font-size:14px}
nav.site a:hover{color:var(--accent)}
h1{font-size:1.7rem;font-weight:600;margin:0 0 1.1rem}

.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
gap:10px;margin:0 0 16px}
.tile{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:11px 14px}
.tile .k{font-size:11px;color:var(--ink3);text-transform:uppercase;letter-spacing:.07em}
.tile .v{font-size:1.16rem;font-weight:650;margin-top:3px;font-variant-numeric:tabular-nums}
.tile .d{font-size:.78rem;color:var(--ink3);margin-top:2px;line-height:1.45}

.stage{display:flex;gap:14px;align-items:flex-start;flex-wrap:wrap}
.mapwrap{flex:1 1 640px;min-width:320px}
#map{width:100%;height:auto;display:block;border-radius:10px;
border:1px solid var(--line);background:var(--sea);cursor:crosshair}
.side{flex:1 1 280px;min-width:262px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;
padding:13px 15px}
.card h2{font-size:1.5rem;font-weight:650;margin:0 0 1px;font-variant-numeric:tabular-nums}
.card .sub{font-size:.8rem;color:var(--ink3);margin-bottom:10px}
.bar{display:grid;grid-template-columns:88px 1fr 74px;align-items:center;
gap:8px;font-size:.79rem;padding:2px 0}
.bar .t{color:var(--ink2)}
.bar .track{display:block;background:#22262b;border-radius:3px;height:9px;overflow:hidden}
.bar .fill{display:block;height:100%;border-radius:3px;min-width:1px}
.bar .p{text-align:right;font-variant-numeric:tabular-nums;color:var(--ink2)}
.note{margin-top:10px;font-size:.8rem;color:var(--ink3);line-height:1.5}
.latest{margin-top:12px;border-top:1px solid var(--line);padding-top:10px;
font-size:.84rem;color:var(--ink2);line-height:1.5}
.latest b{color:var(--ink)}
.tag{font-size:10px;letter-spacing:.07em;text-transform:uppercase;
border:1px solid var(--line);border-radius:999px;padding:1px 7px;margin-left:6px}
.tag.debated{border-color:#b17600;color:#d8a63c}
.tag.contested{border-color:#a84e7c;color:#d munch}
.tag.contested{border-color:#a84e7c;color:#d878a8}

.controls{margin:13px 0 0;display:flex;flex-direction:column;gap:9px}
.sl{display:grid;grid-template-columns:1fr 190px;align-items:center;gap:12px;
font-size:.86rem}
.sl output{font-variant-numeric:tabular-nums;color:var(--ink);text-align:right}
input[type=range]{width:100%;accent-color:var(--accent)}
.btns{display:flex;gap:.6rem;flex-wrap:wrap;align-items:center;font-size:.88rem}
button{font:inherit;font-size:.85rem;background:none;color:var(--ink);
border:1px solid var(--line);border-radius:999px;padding:5px 13px;cursor:pointer}
button:hover{background:#20242a}
button[aria-pressed="true"]{border-color:var(--accent);color:var(--accent)}

.notes{margin-top:2.6rem;border-top:1px solid var(--line);padding-top:1.5rem;
color:var(--ink2);font-size:.95rem;max-width:74ch}
.notes h2{font-size:1.05rem;font-weight:400;color:var(--ink);margin:0 0 .6rem}
.notes p{margin:0 0 1rem}
.refs{margin-top:1.5rem;color:var(--ink3);font-size:.86rem;max-width:78ch}
.refs h2{font-size:.95rem;font-weight:400;color:var(--ink2);margin:0 0 .6rem}
.refs p{margin:0 0 .7rem;padding-left:2.2em;text-indent:-2.2em}
</style>
</head>
<body>
<main>
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library</a></nav>
</header>

<h1>Homo Sapiens Migration</h1>

<div class="tiles">
  <div class="tile"><div class="k">estimated year</div>
    <div class="v" id="tWhen">--</div><div class="d" id="tWhenSub"></div></div>
  <div class="tile"><div class="k">estimated population</div>
    <div class="v" id="tPop">--</div><div class="d" id="tPopSub"></div></div>
  <div class="tile"><div class="k">sites reached</div>
    <div class="v" id="tSites">--</div><div class="d" id="tSitesSub"></div></div>
  <div class="tile"><div class="k">where most people are</div>
    <div class="v" id="tCont">--</div><div class="d" id="tContSub"></div></div>
</div>

<div class="stage">
  <div class="mapwrap"><canvas id="map"></canvas></div>
  <div class="side"><div class="card">
    <h2 id="pop">--</h2>
    <div class="sub" id="popsub">people alive</div>
    <div id="bars"></div>
    <div class="note" id="barnote"></div>
    <div class="latest" id="latest"></div>
  </div></div>
</div>

<div class="controls">
  <div class="sl">
    <input type="range" id="t" min="0" max="1000" step="1" value="0">
    <output id="tout"></output>
  </div>
  <div class="btns">
    <button id="bPlay" aria-pressed="true">Pause</button>
    <button id="bStart">Back to the start</button>
    <button id="bLinks" aria-pressed="true">Order of the spread</button>
    <button id="bLabels" aria-pressed="true">Site names</button>
  </div>
</div>

<div class="notes">
<h2>About the map</h2>
<p>The clock runs on a logarithmic scale because the story is not evenly
spread: most of it happens in the last five per cent of the span, and a linear
slider would spend nearly all its travel on an empty Africa. Each site appears
at the date its own evidence gives, and the ones the literature argues about
are drawn differently and say what the argument is.</p>
<p>The lines join each site to the nearest one already occupied. That shows the
order things happened in, not anyone's route: nobody walked those lines, and
the paths themselves are not known. Sea level was 120 metres lower at the
glacial maximum, which is how Australia and the Americas were reached at all,
and that lower coast is not drawn here.</p>
<p>The world total runs the whole way. The split by continent begins at seven
thousand years ago, because the figures before that are a model run backwards
rather than evidence.</p>
</div>

<div class="refs">
<h2>References</h2>
<p>Goldewijk, K. K., Beusen, A., Doelman, J., &amp; Stehfest, E. (2017).
Anthropogenic land use estimates for the Holocene: HYDE 3.2. <i>Earth System
Science Data, 9</i>(2), 927-953.</p>
<p>Hublin, J.-J., Ben-Ncer, A., Bailey, S. E., Freidline, S. E., Neubauer, S.,
Skinner, M. M., Bergmann, I., Le Cabec, A., Benazzi, S., Harvati, K., &amp;
Gunz, P. (2017). New fossils from Jebel Irhoud, Morocco and the pan-African
origin of Homo sapiens. <i>Nature, 546</i>, 289-292.</p>
<p>United Nations, Department of Economic and Social Affairs, Population
Division. (2024). <i>World population prospects 2024</i>.
https://population.un.org/wpp/</p>
<p>Bennett, M. R., Bustos, D., Pigati, J. S., Springer, K. B., Urban, T. M.,
Holliday, V. T., Reynolds, S. C., Budka, M., Honke, J. S., Hudson, A. M.,
Fenerty, B., Connelly, C., Martinez, P. J., Santucci, V. L., &amp; Odess, D.
(2021). Evidence of humans in North America during the Last Glacial Maximum.
<i>Science, 373</i>(6562), 1528-1531.</p>
</div>
</main>
<script>
const D = __DATA__;
const el = id => document.getElementById(id);
const cv = el('map'), ctx = cv.getContext('2d');
const W = D.w, H = D.h;
let ground = null, baseCv = null;
let playing = true, showLinks = true, showLabels = true;
let p = 0, last = 0, hover = null;

// the clock: logarithmic in years before present, with a hundred years added
// so the scale survives arriving at the present
const T0 = 300000, T1 = -76;                 // AD 2026 on the 1950 datum
const U0 = Math.log10(T0 + 100), U1 = Math.log10(T1 + 100);
const ybpOf = q => Math.pow(10, U0 + (U1 - U0) * q) - 100;
const fmt = n => Math.round(n).toLocaleString('en-US');
function whenLabel(t) {
  if (t >= 12000) return fmt(Math.round(t / 100) * 100) + ' years ago';
  if (t >= 1200) return fmt(Math.round(t / 10) * 10) + ' years ago';
  if (t > 60) return fmt(Math.round(t)) + ' years ago';
  const yr = 1950 - Math.round(t);
  return yr > 0 ? 'AD ' + yr : String(-yr) + ' BC';
}
function bigPop(v) {
  if (v >= 1e9) return (v / 1e9).toFixed(2) + ' billion';
  if (v >= 1e6) return (v / 1e6).toFixed(v >= 1e7 ? 0 : 1) + ' million';
  return fmt(v);
}

// piecewise, straight in the log of the population against the log of the time
function interp(series, t) {
  const s = series;
  if (t >= s[0][0]) return s[0][1];
  if (t <= s[s.length - 1][0]) return s[s.length - 1][1];
  for (let i = 1; i < s.length; i++) {
    if (t >= s[i][0]) {
      const a = s[i - 1], b = s[i];
      const f = (Math.log10(t + 100) - Math.log10(a[0] + 100))
              / (Math.log10(b[0] + 100) - Math.log10(a[0] + 100));
      return Math.pow(10, Math.log10(a[1]) + f * (Math.log10(b[1]) - Math.log10(a[1])));
    }
  }
  return s[s.length - 1][1];
}
function interpCont(t) {
  const s = D.cont;
  if (t >= s[0][0]) return null;
  if (t <= s[s.length - 1][0]) return s[s.length - 1][1];
  for (let i = 1; i < s.length; i++) {
    if (t >= s[i][0]) {
      const a = s[i - 1], b = s[i];
      const f = (Math.log10(t + 100) - Math.log10(a[0] + 100))
              / (Math.log10(b[0] + 100) - Math.log10(a[0] + 100));
      return a[1].map((v, k) => Math.pow(10,
        Math.log10(v) + f * (Math.log10(b[1][k]) - Math.log10(v))));
    }
  }
  return s[s.length - 1][1];
}

function rgb(hex) {
  return [parseInt(hex.slice(1,3),16), parseInt(hex.slice(3,5),16),
          parseInt(hex.slice(5,7),16)];
}
const TERRAIN = D.terrain.map(rgb), COAST = rgb(D.coast);
const img = new Image();
img.onload = () => {
  const off = document.createElement('canvas');
  off.width = W; off.height = H;
  const o = off.getContext('2d');
  o.drawImage(img, 0, 0);
  const d = o.getImageData(0, 0, W, H).data;
  ground = new Uint8Array(W * H);
  for (let i = 0, q = 0; i < d.length; i += 4, q++) ground[q] = d[i];
  cv.width = W; cv.height = H;
  makeBase();
  requestAnimationFrame(frame);
};
img.src = 'data:image/png;base64,' + D.png;

function makeBase() {
  baseCv = document.createElement('canvas');
  baseCv.width = W; baseCv.height = H;
  const b = baseCv.getContext('2d');
  const out = b.createImageData(W, H), o = out.data;
  for (let q = 0, i = 0; q < ground.length; q++, i += 4) {
    const c = TERRAIN[ground[q]];
    const m = ground[q] ? 0.94 + ((q * 2654435761) >>> 28) / 125 : 1;
    // the land is dimmed, so the sites and their lines carry the picture
    const f = ground[q] ? 0.62 : 1;
    o[i] = c[0] * m * f; o[i+1] = c[1] * m * f; o[i+2] = c[2] * m * f;
    o[i+3] = 255;
  }
  for (let y = 1; y < H - 1; y++)
    for (let x = 1; x < W - 1; x++) {
      const q = y * W + x;
      if (!ground[q]) continue;
      if (ground[q-1] && ground[q+1] && ground[q-W] && ground[q+W]) continue;
      const i = q * 4;
      o[i] = (o[i] + COAST[0]) / 2;
      o[i+1] = (o[i+1] + COAST[1]) / 2;
      o[i+2] = (o[i+2] + COAST[2]) / 2;
    }
  b.putImageData(out, 0, 0);
}

const CONF = {secure: '#f2c66b', debated: '#e08b3a', contested: '#d878a8'};
const px = lo => (lo + 180) * W / 360;
const py = la => (90 - la) * H / 180;

function draw() {
  const t = ybpOf(p);
  const u = W / 1000;
  ctx.drawImage(baseCv, 0, 0);
  const here = D.sites.map(s => s.t >= t);

  if (showLinks) {
    ctx.lineCap = 'round';
    for (const L of D.links) {
      if (!here[L.b]) continue;
      const a = D.sites[L.a], b = D.sites[L.b];
      const x1 = px(a.lo), y1 = py(a.la), x2 = px(b.lo), y2 = py(b.la);
      // the shorter way round, so a link does not cross the whole map
      const dx = ((x2 - x1 + W * 1.5) % W) - W / 2;
      const mx = x1 + dx / 2, my = (y1 + y2) / 2 - Math.abs(dx) * 0.12;
      // a link across the date line runs off one edge and back on the other,
      // so it is stroked three times and the frame keeps the piece it needs
      for (const sh of [-W, 0, W]) {
        const g = ctx.createLinearGradient(x1 + sh, y1, x1 + dx + sh, y2);
        g.addColorStop(0, 'rgba(242,198,107,0.14)');
        g.addColorStop(1, 'rgba(242,198,107,0.62)');
        ctx.strokeStyle = g; ctx.lineWidth = 1.7 * u;
        ctx.beginPath();
        ctx.moveTo(x1 + sh, y1);
        ctx.quadraticCurveTo(mx + sh, my, x1 + dx + sh, y2);
        ctx.stroke();
      }
    }
  }

  D.sites.forEach((s, i) => {
    if (!here[i]) return;
    const x = px(s.lo), y = py(s.la);
    const age = Math.max(0, Math.log10(s.t + 100) - Math.log10(t + 100));
    const glow = Math.min(1, 0.25 + age * 1.6);
    const g = ctx.createRadialGradient(x, y, 0, x, y, 26 * u);
    g.addColorStop(0, `rgba(242,198,107,${0.30 * glow})`);
    g.addColorStop(1, 'rgba(242,198,107,0)');
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.arc(x, y, 26 * u, 0, 7); ctx.fill();
    ctx.fillStyle = CONF[s.c] || '#f2c66b';
    ctx.beginPath(); ctx.arc(x, y, (age < 0.02 ? 6 : 3.6) * u, 0, 7); ctx.fill();
    if (s.c !== 'secure') {
      ctx.strokeStyle = 'rgba(255,255,255,0.75)'; ctx.lineWidth = 1.1 * u;
      ctx.beginPath(); ctx.arc(x, y, 6.5 * u, 0, 7); ctx.stroke();
    }
  });

  if (showLabels) {
    ctx.font = `${Math.round(12 * u)}px -apple-system, BlinkMacSystemFont, sans-serif`;
    ctx.textBaseline = 'middle';
    // labels are kept off each other by the box each one would actually
    // occupy, measured, rather than by a guess at how wide a name is
    const put = [];
    D.sites.forEach((s, i) => {
      if (!here[i]) return;
      const x = px(s.lo), y = py(s.la);
      const right = x < W * 0.72;
      const wpx = ctx.measureText(s.s).width + 16 * u;
      const x0 = right ? x : x - wpx, x1b = x0 + wpx;
      const y0 = y - 9 * u, y1b = y + 9 * u;
      if (put.some(q => x0 < q[2] && x1b > q[0] && y0 < q[3] && y1b > q[1]))
        return;
      put.push([x0, y0, x1b, y1b]);
      ctx.textAlign = right ? 'left' : 'right';
      const tx = x + (right ? 10 : -10) * u;
      ctx.lineWidth = 3.4 * u;
      ctx.strokeStyle = 'rgba(6,12,20,0.85)';
      ctx.strokeText(s.s, tx, y);
      ctx.fillStyle = '#eef3f8';
      ctx.fillText(s.s, tx, y);
    });
  }
}

// las casillas de arriba llevan la cuenta del año y de la gente, y cambian
// con el deslizador igual que el mapa
function tiles(t, world, c) {
  el('tWhen').textContent = whenLabel(t);
  // el letrero grande alterna entre años atrás y año del calendario, así que
  // el chico lleva siempre la otra cuenta
  const yr = 1950 - Math.round(t);
  el('tWhenSub').textContent = t > 60
    ? (yr > 0 ? 'about AD ' + fmt(yr) : 'about ' + fmt(-yr) + ' BC')
    : fmt(Math.round(t)) + ' years before 1950';
  el('tPop').textContent = bigPop(world);
  el('tPopSub').textContent = 'people alive, interpolated between the '
    + 'published figures';
  const llegados = D.sites.filter(s => s.t >= t).length;
  el('tSites').textContent = fmt(llegados) + ' of ' + fmt(D.sites.length);
  el('tSitesSub').textContent = llegados
    ? 'of the arrivals this page follows'
    : 'the oldest fossils are 315,000 years old';
  if (!c) {
    el('tCont').textContent = 'not split yet';
    el('tContSub').textContent = 'the split by continent starts at seven '
      + 'thousand years ago';
    return;
  }
  const tot = c.reduce((a, b) => a + b, 0);
  let k = 0;
  c.forEach((v, i) => { if (v > c[k]) k = i; });
  el('tCont').textContent = D.continents[k];
  el('tContSub').textContent = (c[k] / tot * 100).toFixed(0)
    + ' per cent of the people alive';
}

function panel() {
  const t = ybpOf(p);
  el('tout').textContent = whenLabel(t);
  el('t').value = Math.round(p * 1000);
  const world = interp(D.pop, t);
  el('pop').textContent = bigPop(world);
  el('popsub').textContent = 'people alive, ' + whenLabel(t);
  const c = interpCont(t);
  tiles(t, world, c);
  if (!c) {
    el('bars').innerHTML = '';
    el('barnote').textContent = 'The split by continent starts at seven '
      + 'thousand years ago. Before that the published figures are a model run '
      + 'backwards, and they put more people in the Americas than in Africa at '
      + 'the end of the ice age, which cannot be right.';
  } else {
    const tot = c.reduce((a, b) => a + b, 0);
    el('bars').innerHTML = D.continents.map((n, k) =>
      `<div class="bar"><span class="t">${n}</span>` +
      `<span class="track"><span class="fill" style="width:${(c[k] / tot * 100).toFixed(1)}%;` +
      `background:${D.ccolour[k]}"></span></span>` +
      `<span class="p">${bigPop(c[k])}</span></div>`).join('');
    el('barnote').textContent = 'HYDE and the United Nations, interpolated '
      + 'between their published dates.';
  }
  const shown = D.sites.filter(s => s.t >= t);
  const s = shown[shown.length - 1];
  el('latest').innerHTML = s
    ? `<b>${s.s}</b><span class="tag ${s.c}">${s.c}</span><br>${s.n}, `
      + `${whenLabel(s.t)}.<br>${s.d}`
      + (D.argued[s.n] ? `<br><br>${D.argued[s.n]}` : '')
    : 'Nothing yet: the oldest fossils are 315,000 years old.';
}

function frame(now) {
  const dt = last ? Math.min(0.08, (now - last) / 1000) : 0;
  last = now;
  if (playing) {
    p += dt / 46;                       // the whole story in three quarters of a minute
    if (p >= 1) { p = 1; playing = false; el('bPlay').setAttribute('aria-pressed', false);
      el('bPlay').textContent = 'Play'; }
  }
  draw(); panel();
  requestAnimationFrame(frame);
}

el('t').addEventListener('input', e => {
  p = (+e.target.value) / 1000;
  playing = false;
  el('bPlay').setAttribute('aria-pressed', false);
  el('bPlay').textContent = 'Play';
});
el('bPlay').addEventListener('click', () => {
  if (p >= 1) p = 0;
  playing = !playing;
  el('bPlay').setAttribute('aria-pressed', playing);
  el('bPlay').textContent = playing ? 'Pause' : 'Play';
});
el('bStart').addEventListener('click', () => {
  p = 0; playing = true;
  el('bPlay').setAttribute('aria-pressed', true);
  el('bPlay').textContent = 'Pause';
});
el('bLinks').addEventListener('click', () => {
  showLinks = !showLinks;
  el('bLinks').setAttribute('aria-pressed', showLinks);
});
el('bLabels').addEventListener('click', () => {
  showLabels = !showLabels;
  el('bLabels').setAttribute('aria-pressed', showLabels);
});

window.__mig = () => ({p, ybp: ybpOf(p), playing,
  sites: D.sites.length, links: D.links.length,
  here: D.sites.filter(s => s.t >= ybpOf(p)).length,
  world: interp(D.pop, ybpOf(p)), cont: interpCont(ybpOf(p)),
  showLinks, showLabels});
window.__setP = q => { p = q; playing = false; draw(); panel(); return ybpOf(p); };
window.__setYbp = t => {
  p = (Math.log10(t + 100) - U0) / (U1 - U0);
  playing = false; draw(); panel(); return p;
};
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
