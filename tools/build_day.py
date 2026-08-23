#!/usr/bin/env python3
"""Generate day-night.html, The Day: Earth's Night and Day Cycle.

The third of the three clocks. The Year turns one orbit into a helix, The Month
counts the two lengths a month can have, and this one is the shortest turn of
the lot: one rotation, with the shadow sweeping the same map Earth's Climate is
drawn on.

Two controls, and the point of the page is what happens when both move.

  The hour drags the terminator west across the map at fifteen degrees an hour.
  Nothing about its shape changes: it is a great circle, always, and it always
  cuts the globe in half.

  The date tilts it. Earth's axis leans 23.44 degrees out of the plane it
  orbits in, so the sub-solar point runs from that far north in June to that
  far south in December, and the terminator leans with it. In June the shadow
  misses the Arctic entirely and swallows the Antarctic; in December they
  trade. The curve beside the map is the same fact counted in hours.

Positions are the low-precision solar theory from Meeus, Astronomical
Algorithms, chapter 25, with the equation of time from chapter 28. That is
accurate to about a hundredth of a degree over these centuries, which is far
finer than a map at a sixth of a degree can show. verify_day.py checks the
declination, the equation of time and the sunrise and sunset times against
pyephem, which shares no code with it.

The map raster is the one Earth's Climate uses: each byte is climate group
times eight plus continent, from GSHHG coastlines and the Koppen-Geiger map of
Beck and others, 2018.

Usage: python3 build_day.py      (needs /home/claude/earth/*.npy)
"""

import base64
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image

from build_earth import GROUPS, C_OCEAN, C_COAST

OUT = Path(__file__).parent.parent / "day-night.html"
DATA = Path("/home/claude/earth")

OBLIQUITY = 23.4366          # degrees, the tilt that makes the seasons
SIDEREAL_DAY = 23.9344696    # hours, one turn against the stars
SOLAR_DAY = 24.0             # hours, one turn back to the same noon
HORIZON = -0.833             # degrees, refraction plus the Sun's own radius

FACTS = [
    ("Axial tilt", f"{OBLIQUITY}&deg;",
     "which is why the shadow leans, and why there are seasons"),
    ("Sidereal day", f"{SIDEREAL_DAY:.6f} h",
     "one turn against the stars"),
    ("Solar day", "24 h exactly, on average",
     "one turn back to the same noon, which takes about four minutes longer"),
    ("Terminator speed", "1,670 km/h at the equator",
     "the shadow's edge crosses the ground faster than a jet, and stands "
     "still at the poles"),
]


def main():
    cid = np.load(DATA / "cid.npy")
    clim = np.load(DATA / "clim.npy")
    H, W = cid.shape

    packed = (clim.astype(np.uint16) * 8 + cid).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(packed, "L").save(buf, "PNG", optimize=True, compress_level=9)
    png = base64.b64encode(buf.getvalue()).decode()

    js = {"png": png, "w": W, "h": H,
          "colors": [c for _, _, c, _ in GROUPS],
          "ocean": C_OCEAN, "coast": C_COAST,
          "obl": OBLIQUITY, "horizon": HORIZON}

    facts = "\n".join(
        f'<div class="tile"><div class="k">{n}</div>'
        f'<div class="v">{v}</div><div class="d">{d}</div></div>'
        for n, v, d in FACTS)

    legend = "\n".join(
        f'<div class="lg"><span class="sw" style="background:{c}"></span>'
        f'<span>{k} {n.lower()}</span></div>' for k, n, c, _ in GROUPS)

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Day: Earth's Night and Day Cycle &middot; Altazor</title>
<style>
:root{{color-scheme:dark;
--ink:#e6e6e6; --ink2:#9aa3ad; --ink3:#7d848c;
--bg:#121212; --panel:#171a1d; --line:#2b2f34; --accent:#58a6ff;
--sun:#f2c66b; --sea:{C_OCEAN};}}
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

.stage{{display:flex;gap:14px;align-items:flex-start;flex-wrap:wrap}}
.mapwrap{{flex:1 1 620px;min-width:300px;position:relative}}
#map{{width:100%;height:auto;display:block;border-radius:10px;
border:1px solid var(--line);background:var(--sea);cursor:crosshair}}
.curvewrap{{flex:0 0 132px;position:relative}}
#curve{{width:132px;display:block;border-radius:10px;
border:1px solid var(--line);background:var(--panel)}}
.side{{flex:1 1 260px;min-width:240px}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:12px;
padding:13px 15px}}
.card h2{{font-size:1.02rem;font-weight:600;margin:0 0 2px}}
.card .sub{{font-size:.8rem;color:var(--ink3);margin-bottom:9px}}
.row{{display:flex;justify-content:space-between;gap:12px;font-size:.87rem;padding:2.5px 0}}
.row span:last-child{{font-variant-numeric:tabular-nums;color:var(--ink2)}}

.controls{{margin:14px 0 0;display:flex;flex-direction:column;gap:9px}}
.sl{{display:grid;grid-template-columns:118px 1fr 150px;align-items:center;
gap:11px;font-size:.86rem}}
.sl label{{color:var(--ink2)}}
.sl output{{font-variant-numeric:tabular-nums;color:var(--ink)}}
input[type=range]{{width:100%;accent-color:var(--accent)}}
.btns{{display:flex;gap:.6rem;flex-wrap:wrap;align-items:center;font-size:.88rem}}
button{{font:inherit;font-size:.85rem;background:none;color:var(--ink);
border:1px solid var(--line);border-radius:999px;padding:5px 13px;cursor:pointer}}
button:hover{{background:#20242a}}
button[aria-pressed="true"]{{border-color:var(--accent);color:var(--accent)}}

.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(178px,1fr));
gap:10px;margin:18px 0 0}}
.tile{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:11px 14px}}
.tile .k{{font-size:11px;color:var(--ink3);text-transform:uppercase;letter-spacing:.07em}}
.tile .v{{font-size:1.16rem;font-weight:650;margin-top:3px;font-variant-numeric:tabular-nums}}
.tile .d{{font-size:.78rem;color:var(--ink3);margin-top:2px;line-height:1.45}}

.legend{{display:flex;flex-wrap:wrap;gap:8px 16px;margin:14px 0 0;font-size:.8rem;
color:var(--ink2)}}
.lg{{display:flex;gap:7px;align-items:center}}
.sw{{flex:0 0 12px;height:12px;border-radius:3px;
border:1px solid rgba(255,255,255,.18)}}

.notes{{margin-top:2.6rem;border-top:1px solid var(--line);padding-top:1.5rem;
color:var(--ink2);font-size:.95rem;max-width:74ch}}
.notes h2{{font-size:1.05rem;font-weight:400;color:var(--ink);margin:0 0 .6rem}}
.notes p{{margin:0 0 1rem}}
.refs{{margin-top:1.5rem;color:var(--ink3);font-size:.86rem;max-width:78ch}}
.refs h2{{font-size:.95rem;font-weight:400;color:var(--ink2);margin:0 0 .6rem}}
.refs p{{margin:0 0 .7rem;padding-left:2.2em;text-indent:-2.2em}}
</style>
</head>
<body>
<main>
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library</a></nav>
</header>

<h1>The Day: Earth's Night and Day Cycle</h1>
<p class="stamp">Sun from Meeus, chapters 25 and 28; the map from Earth's Climate.</p>

<div class="stage">
  <div class="mapwrap"><canvas id="map"></canvas></div>
  <div class="curvewrap"><canvas id="curve"></canvas></div>
  <div class="side"><div class="card">
    <h2 id="pName">The sub-solar point</h2>
    <div class="sub" id="pSub">where the Sun is straight overhead</div>
    <div class="row"><span>Latitude</span><span id="pLat"></span></div>
    <div class="row"><span>Longitude</span><span id="pLon"></span></div>
    <div class="row"><span>Sun's height</span><span id="pAlt"></span></div>
    <div class="row"><span>Solar time there</span><span id="pSolar"></span></div>
    <div class="row"><span>Daylight today</span><span id="pDay"></span></div>
    <div class="row"><span>Sunrise, UTC</span><span id="pRise"></span></div>
    <div class="row"><span>Sunset, UTC</span><span id="pSet"></span></div>
  </div></div>
</div>

<div class="controls">
  <div class="sl"><label for="hour">Hour, UTC</label>
    <input type="range" id="hour" min="0" max="1439" step="1" value="0">
    <output id="hourOut"></output></div>
  <div class="sl"><label for="doy">Day of the year</label>
    <input type="range" id="doy" min="0" max="365" step="1" value="0">
    <output id="doyOut"></output></div>
  <div class="btns">
    <button id="bDay">Run the day</button>
    <button id="bYear">Run the year</button>
    <button id="bNow">Now</button>
    <button id="bGrat" aria-pressed="true">Tropics and circles</button>
    <button id="bBands" aria-pressed="false">Twilight bands</button>
    <button id="bClim" aria-pressed="true">Climate colours</button>
  </div>
</div>

<div class="tiles">{facts}</div>

<div class="legend">{legend}</div>

<div class="notes">
<h2>About the map</h2>
<p>The lit half is always a half. The shadow's edge is a great circle, so it
cuts the globe in two whatever the date, and the hour only slides it west at
fifteen degrees an hour. What the date changes is the lean: the axis is tilted
23.44 degrees, so the point with the Sun overhead runs that far north in June
and that far south in December, and the terminator tips over with it.</p>
<p>In June it clears the Arctic entirely and buries the Antarctic; in December
they trade. The curve beside the map is the same thing counted in hours: how
long the Sun stays up at every latitude on the chosen date. It is flat at
twelve hours at the equinoxes and splays open at the solstices, and the
latitude where it first reaches twenty four is the polar circle.</p>
</div>

<div class="refs">
<h2>References</h2>
<p>Beck, H. E., Zimmermann, N. E., McVicar, T. R., Vergopolan, N., Berg, A., &amp;
Wood, E. F. (2018). Present and future Koppen-Geiger climate classification maps
at 1-km resolution. <i>Scientific Data, 5</i>, 180214.</p>
<p>Meeus, J. (1998). <i>Astronomical algorithms</i> (2nd ed.). Willmann-Bell.</p>
<p>Wessel, P., &amp; Smith, W. H. F. (1996). A global, self-consistent,
hierarchical, high-resolution shoreline database. <i>Journal of Geophysical
Research, 101</i>(B4), 8741-8743.</p>
</div>
</main>
<script>
const D = {json.dumps(js)};
const W = D.w, H = D.h;
const OW = 540, OH = 270;              // the shading is smooth, so it is
                                       // computed small and scaled up
const D2R = Math.PI/180, R2D = 180/Math.PI;
const el = id => document.getElementById(id);

const cv = el('map'), ctx = cv.getContext('2d');
const cu = el('curve'), cx2 = cu.getContext('2d');
let ids = null, grp = null, baseCv = null;
let showGrat = true, bands = false, showClim = true;
let runDay = false, runYear = false, hover = null;
let jd = jdNow();

// ---------- the Sun, from Meeus chapters 25 and 28 ----------
const norm = a => ((a % 360) + 360) % 360;

function solar(jdv) {{
  const T = (jdv - 2451545.0)/36525;
  const L0 = norm(280.46646 + 36000.76983*T + 0.0003032*T*T);
  const M = norm(357.52911 + 35999.05029*T - 0.0001537*T*T);
  const e = 0.016708634 - 0.000042037*T - 0.0000001267*T*T;
  const C = (1.914602 - 0.004817*T - 0.000014*T*T)*Math.sin(M*D2R)
          + (0.019993 - 0.000101*T)*Math.sin(2*M*D2R)
          + 0.000289*Math.sin(3*M*D2R);
  const om = 125.04 - 1934.136*T;
  const lam = L0 + C - 0.00569 - 0.00478*Math.sin(om*D2R);   // apparent
  const eps0 = 23 + 26/60 + 21.448/3600
             - (46.8150*T + 0.00059*T*T - 0.001813*T*T*T)/3600;
  const eps = eps0 + 0.00256*Math.cos(om*D2R);
  const dec = Math.asin(Math.sin(eps*D2R)*Math.sin(lam*D2R))*R2D;
  // the equation of time, Meeus 28.3, in minutes of time
  const y = Math.tan(eps/2*D2R)**2;
  const E = y*Math.sin(2*L0*D2R) - 2*e*Math.sin(M*D2R)
          + 4*e*y*Math.sin(M*D2R)*Math.cos(2*L0*D2R)
          - 0.5*y*y*Math.sin(4*L0*D2R) - 1.25*e*e*Math.sin(2*M*D2R);
  const eqt = E*R2D*4;
  const ut = ((jdv + 0.5) % 1)*24;
  // the Sun is overhead where apparent solar time reads noon
  let slon = 15*(12 - ut - eqt/60);
  slon = ((slon + 180) % 360 + 360) % 360 - 180;
  return {{dec, eqt, ut, slon, lam: norm(lam)}};
}}

// how high the Sun stands, in degrees
function altitude(lat, lon, s) {{
  const h = (lon - s.slon)*D2R;
  return Math.asin(Math.sin(lat*D2R)*Math.sin(s.dec*D2R)
                 + Math.cos(lat*D2R)*Math.cos(s.dec*D2R)*Math.cos(h))*R2D;
}}

// hours between sunrise and sunset at a latitude, 0 or 24 inside the circles
function daylight(lat, dec) {{
  const c = (Math.sin(D.horizon*D2R) - Math.sin(lat*D2R)*Math.sin(dec*D2R))
          / (Math.cos(lat*D2R)*Math.cos(dec*D2R));
  if (c >= 1) return 0;
  if (c <= -1) return 24;
  return 2*Math.acos(c)*R2D/15;
}}

const DEG = '\u00b0';
function jdNow() {{ return Date.now()/86400000 + 2440587.5; }}
const midnight = j => Math.floor(j + 0.5) - 0.5;   // the UT day this falls in
const jdToDate = j => new Date((j - 2440587.5)*86400000);
function jdOf(y, m, d, hours) {{
  return Date.UTC(y, m, d)/86400000 + 2440587.5 + hours/24;
}}
const pad = n => String(n).padStart(2, '0');
function hm(h) {{
  if (!isFinite(h)) return '--';
  let t = ((h % 24) + 24) % 24;
  const m = Math.round(t*60);
  return pad(Math.floor(m/60) % 24) + ':' + pad(m % 60);
}}
function dur(h) {{
  if (h <= 0) return 'none, the Sun stays down';
  if (h >= 24) return 'all day, the Sun stays up';
  return Math.floor(h) + ' h ' + pad(Math.round((h % 1)*60)) + ' m';
}}

// ---------- the map ----------
function rgb(hex) {{
  return [parseInt(hex.slice(1,3),16), parseInt(hex.slice(3,5),16),
          parseInt(hex.slice(5,7),16)];
}}
const SEA = rgb(D.ocean), COAST = rgb(D.coast), CLR = D.colors.map(rgb);
const LANDFLAT = rgb('#67727e');

const img = new Image();
img.onload = () => {{
  const off = document.createElement('canvas');
  off.width = W; off.height = H;
  const o = off.getContext('2d');
  o.drawImage(img, 0, 0);
  const d = o.getImageData(0, 0, W, H).data;
  ids = new Uint8Array(W*H); grp = new Uint8Array(W*H);
  for (let i = 0, p = 0; i < d.length; i += 4, p++) {{
    ids[p] = d[i] & 7; grp[p] = d[i] >> 3;
  }}
  cv.width = W; cv.height = H;
  makeBase();
  sizeCurve();
  frame();
}};
img.src = 'data:image/png;base64,' + D.png;

// The daylit map never changes, so it is painted once and the shadow is laid
// over it each frame. Repainting two million pixels of coastline every frame
// would cost more than the shading does.
function makeBase() {{
  baseCv = document.createElement('canvas');
  baseCv.width = W; baseCv.height = H;
  const b = baseCv.getContext('2d');
  const out = b.createImageData(W, H), o = out.data;
  for (let p = 0, i = 0; p < ids.length; p++, i += 4) {{
    const c = ids[p] === 0 ? SEA
            : (showClim && grp[p] > 0) ? CLR[grp[p] - 1] : LANDFLAT;
    o[i] = c[0]; o[i+1] = c[1]; o[i+2] = c[2]; o[i+3] = 255;
  }}
  for (let y = 1; y < H - 1; y++) {{
    for (let x = 1; x < W - 1; x++) {{
      const p = y*W + x;
      if (!ids[p]) continue;
      if (ids[p-1] && ids[p+1] && ids[p-W] && ids[p+W]) continue;
      const i = p*4;
      o[i] = COAST[0]; o[i+1] = COAST[1]; o[i+2] = COAST[2];
    }}
  }}
  b.putImageData(out, 0, 0);
}}

const shadeCv = document.createElement('canvas');
shadeCv.width = OW; shadeCv.height = OH;
const shadeCtx = shadeCv.getContext('2d');
const shadeImg = shadeCtx.createImageData(OW, OH);

// The height of the Sun is sin(lat)sin(dec) + cos(lat)cos(dec)cos(hour angle),
// which separates: the latitude terms depend only on the row and the hour
// angle only on the column. So the whole grid is two arrays and a multiply.
const sinLat = new Float64Array(OH), cosLat = new Float64Array(OH);
for (let y = 0; y < OH; y++) {{
  const lat = (90 - (y + 0.5)*180/OH)*D2R;
  sinLat[y] = Math.sin(lat); cosLat[y] = Math.cos(lat);
}}
const cosH = new Float64Array(OW);

function shade(s) {{
  for (let x = 0; x < OW; x++) {{
    const lon = -180 + (x + 0.5)*360/OW;
    cosH[x] = Math.cos((lon - s.slon)*D2R);
  }}
  const sd = Math.sin(s.dec*D2R), cd = Math.cos(s.dec*D2R);
  const d = shadeImg.data;
  for (let y = 0, i = 0; y < OH; y++) {{
    const a = sinLat[y]*sd, b = cosLat[y]*cd;
    for (let x = 0; x < OW; x++, i += 4) {{
      const alt = Math.asin(Math.max(-1, Math.min(1, a + b*cosH[x])))*R2D;
      let v;
      if (alt > 0) v = 0;
      else if (bands) {{
        // civil, nautical and astronomical twilight, as steps
        v = alt > -6 ? 0.30 : alt > -12 ? 0.52 : alt > -18 ? 0.68 : 0.82;
      }} else {{
        v = Math.pow(Math.min(1, -alt/18), 0.75)*0.82;
      }}
      d[i] = 4; d[i+1] = 8; d[i+2] = 17; d[i+3] = Math.round(v*255);
    }}
  }}
  shadeCtx.putImageData(shadeImg, 0, 0);
}}

function draw() {{
  const s = solar(jd);
  ctx.drawImage(baseCv, 0, 0);
  shade(s);
  ctx.imageSmoothingEnabled = true;
  ctx.drawImage(shadeCv, 0, 0, W, H);
  const u = W/1000;

  if (showGrat) {{
    ctx.save();
    ctx.strokeStyle = 'rgba(255,255,255,0.30)';
    ctx.setLineDash([9*u, 7*u]); ctx.lineWidth = 1.5*u;
    ctx.font = Math.round(11*u) + 'px -apple-system, BlinkMacSystemFont, sans-serif';
    ctx.fillStyle = 'rgba(255,255,255,0.72)';
    for (const [lat, name] of [[66.5634, 'Arctic Circle'],
                               [D.obl, 'Tropic of Cancer'], [0, 'Equator'],
                               [-D.obl, 'Tropic of Capricorn'],
                               [-66.5634, 'Antarctic Circle']]) {{
      const y = (90 - lat)*H/180;
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
      ctx.fillText(name, 10*u, y - 6*u);
    }}
    ctx.restore();
  }}

  // where the Sun is straight overhead, and the midnight point opposite it
  const sx = (s.slon + 180)*W/360, sy = (90 - s.dec)*H/180;
  const g = ctx.createRadialGradient(sx, sy, 0, sx, sy, 34*u);
  g.addColorStop(0, 'rgba(255,226,150,0.55)');
  g.addColorStop(1, 'rgba(255,214,120,0)');
  ctx.fillStyle = g;
  ctx.beginPath(); ctx.arc(sx, sy, 34*u, 0, 7); ctx.fill();
  ctx.fillStyle = '#ffd257';
  ctx.beginPath(); ctx.arc(sx, sy, 5.5*u, 0, 7); ctx.fill();
  const ax = ((s.slon + 360) % 360)*W/360, ay = (90 + s.dec)*H/180;
  ctx.strokeStyle = 'rgba(200,214,240,0.5)'; ctx.lineWidth = 1.4*u;
  ctx.beginPath(); ctx.arc(ax, ay, 4.5*u, 0, 7); ctx.stroke();

  if (hover) {{
    const hx = (hover.lon + 180)*W/360, hy = (90 - hover.lat)*H/180;
    ctx.strokeStyle = 'rgba(255,255,255,0.85)'; ctx.lineWidth = 1.6*u;
    ctx.beginPath(); ctx.arc(hx, hy, 6*u, 0, 7); ctx.stroke();
  }}
  return s;
}}

// ---------- how long the Sun is up, latitude by latitude ----------
function sizeCurve() {{
  const h = Math.max(200, Math.round(cv.getBoundingClientRect().height));
  cu.style.height = h + 'px';
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  cu.width = 132*dpr; cu.height = h*dpr;
  cx2.setTransform(dpr, 0, 0, dpr, 0, 0);
}}
window.addEventListener('resize', () => {{ sizeCurve(); frameOnce(); }});

function curve(s) {{
  const w = 132, h = cu.height/(cu.width/132);
  cx2.clearRect(0, 0, w, h);
  cx2.font = '9px -apple-system, BlinkMacSystemFont, sans-serif';
  cx2.strokeStyle = 'rgba(255,255,255,0.10)'; cx2.lineWidth = 1;
  for (const t of [0, 6, 12, 18, 24]) {{
    const x = 8 + t/24*(w - 16);
    cx2.beginPath(); cx2.moveTo(x, 12); cx2.lineTo(x, h - 4); cx2.stroke();
  }}
  cx2.fillStyle = 'rgba(160,175,200,0.75)';
  cx2.textAlign = 'center';
  for (const t of [0, 12, 24]) cx2.fillText(t + 'h', 8 + t/24*(w - 16), 9);
  cx2.beginPath();
  for (let y = 12; y <= h - 4; y++) {{
    const lat = 90 - (y - 12)/(h - 16)*180;
    const x = 8 + daylight(lat, s.dec)/24*(w - 16);
    y === 12 ? cx2.moveTo(x, y) : cx2.lineTo(x, y);
  }}
  cx2.strokeStyle = '#f2c66b'; cx2.lineWidth = 1.8; cx2.stroke();
  if (hover) {{
    const y = 12 + (90 - hover.lat)/180*(h - 16);
    const x = 8 + daylight(hover.lat, s.dec)/24*(w - 16);
    cx2.strokeStyle = 'rgba(255,255,255,0.45)'; cx2.lineWidth = 1;
    cx2.beginPath(); cx2.moveTo(8, y); cx2.lineTo(w - 8, y); cx2.stroke();
    cx2.fillStyle = '#fff';
    cx2.beginPath(); cx2.arc(x, y, 3, 0, 7); cx2.fill();
  }}
}}

// ---------- the panel ----------
function panel(s) {{
  const p = hover || {{lat: s.dec, lon: s.slon}};
  const alt = altitude(p.lat, p.lon, s);
  const len = daylight(p.lat, s.dec);
  const noon = 12 - p.lon/15 - s.eqt/60;
  el('pName').textContent = hover ? 'Under the cursor' : 'The sub-solar point';
  el('pSub').textContent = hover ? 'a place on the map'
                                 : 'where the Sun is straight overhead';
  el('pLat').textContent = Math.abs(p.lat).toFixed(2) + DEG
    + (p.lat >= 0 ? ' N' : ' S');
  el('pLon').textContent = Math.abs(p.lon).toFixed(2) + DEG
    + (p.lon >= 0 ? ' E' : ' W');
  el('pAlt').textContent = alt.toFixed(1) + DEG
    + (alt > 0 ? ' above the horizon' : ' below it');
  el('pSolar').textContent = hm(s.ut + s.eqt/60 + p.lon/15);
  el('pDay').textContent = dur(len);
  el('pRise').textContent = (len <= 0 || len >= 24) ? '--' : hm(noon - len/2);
  el('pSet').textContent = (len <= 0 || len >= 24) ? '--' : hm(noon + len/2);

  const d = jdToDate(jd);
  el('hourOut').textContent = hm(s.ut) + ' UTC';
  el('doyOut').textContent = d.toLocaleDateString('en-US',
    {{month: 'long', day: 'numeric', timeZone: 'UTC'}});
  el('hour').value = Math.round(s.ut*60) % 1440;
  el('doy').value = Math.round(midnight(jd) - jdOf(d.getUTCFullYear(), 0, 1, 0));
}}

// ---------- the clock ----------
let last = 0;
function frame(now) {{
  const dt = last ? Math.min(0.1, (now - last)/1000) : 0;
  last = now;
  if (runDay) jd += dt*0.6;            // a bit over half a day a second
  if (runYear) jd += dt*24;            // a bit under a month a second
  frameOnce();
  requestAnimationFrame(frame);
}}
function frameOnce() {{
  if (!ids) return;
  const s = draw();
  curve(s);
  panel(s);
  window.__day = {{jd, ut: s.ut, dec: s.dec, eqt: s.eqt, slon: s.slon,
                  runDay, runYear, bands, showGrat, showClim, hover}};
}}

// The share of the surface the shadow leaves alone, read off the overlay that
// was actually drawn rather than recomputed: a terminator drawn inside out
// would still pass a check that asked the formula again. Rows are weighted by
// the cosine of their latitude, since an equirectangular row near the pole
// stands for far less ground than one at the equator.
// what the overlay actually painted at one place, so the check can compare the
// picture with the formula rather than the formula with itself
window.__alphaAt = (lat, lon) => {{
  const x = Math.min(OW - 1, Math.max(0, Math.floor((lon + 180)/360*OW)));
  const y = Math.min(OH - 1, Math.max(0, Math.floor((90 - lat)/180*OH)));
  return shadeImg.data[(y*OW + x)*4 + 3];
}};
window.__lit = () => {{
  const d = shadeImg.data;
  let up = 0, all = 0;
  for (let y = 0, i = 0; y < OH; y++) {{
    const w = Math.cos((90 - (y + 0.5)*180/OH)*D2R);
    for (let x = 0; x < OW; x++, i += 4) {{
      all += w;
      if (d[i+3] === 0) up += w;
    }}
  }}
  return up/all;
}};

// ---------- the controls ----------
function press(id, on) {{ el(id).setAttribute('aria-pressed', on); }}
el('hour').addEventListener('input', e => {{
  jd = midnight(jd) + (+e.target.value)/1440;
  runDay = false; press('bDay', false); frameOnce();
}});
el('doy').addEventListener('input', e => {{
  const d = jdToDate(jd), frac = jd - midnight(jd);
  jd = jdOf(d.getUTCFullYear(), 0, 1 + (+e.target.value), 0) + frac;
  runYear = false; press('bYear', false); frameOnce();
}});
el('bDay').addEventListener('click', () => {{
  runDay = !runDay; runYear = false;
  press('bDay', runDay); press('bYear', false);
}});
el('bYear').addEventListener('click', () => {{
  runYear = !runYear; runDay = false;
  press('bYear', runYear); press('bDay', false);
}});
el('bNow').addEventListener('click', () => {{
  jd = jdNow(); runDay = runYear = false;
  press('bDay', false); press('bYear', false); frameOnce();
}});
el('bGrat').addEventListener('click', () => {{
  showGrat = !showGrat; press('bGrat', showGrat); frameOnce();
}});
el('bBands').addEventListener('click', () => {{
  bands = !bands; press('bBands', bands); frameOnce();
}});
el('bClim').addEventListener('click', () => {{
  showClim = !showClim; press('bClim', showClim); makeBase(); frameOnce();
}});

function at(ev) {{
  const r = cv.getBoundingClientRect();
  const lon = (ev.clientX - r.left)/r.width*360 - 180;
  const lat = 90 - (ev.clientY - r.top)/r.height*180;
  if (lat > 90 || lat < -90) return null;
  return {{lat, lon}};
}}
cv.addEventListener('mousemove', e => {{ hover = at(e); frameOnce(); }});
cv.addEventListener('mouseleave', () => {{ hover = null; frameOnce(); }});
window.__setTime = (y, mo, d, h) => {{
  jd = jdOf(y, mo - 1, d, h); runDay = runYear = false; frameOnce(); return jd;
}};
window.__probe = (lat, lon) => {{
  const s = solar(jd);
  return {{alt: altitude(lat, lon, s), day: daylight(lat, s.dec),
          dec: s.dec, eqt: s.eqt, slon: s.slon}};
}};
</script>
</body>
</html>
"""
    OUT.write_text(doc, encoding="utf-8")
    print(f"wrote {OUT} ({len(doc):,} bytes): {W}x{H} raster, "
          f"{len(png)/1024:.0f} KB of base64, shading at {540}x{270}")


if __name__ == "__main__":
    main()
