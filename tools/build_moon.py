#!/usr/bin/env python3
"""Generate moon.html, The Month: The Moon's Loop.

The companion to The Year: Earth's Loop. That page turns one circle into a
helix; this one is about the two lengths a month can have, and about the shape
the Moon actually traces through space.

Two views over one clock:

  Around the Earth. The Earth-Moon system at true scale, which is the first
  surprise: sixty Earths fit in the gap. The Moon runs its orbit while three
  rays are drawn from Earth, one to a fixed star, one to the Sun now, and one
  to where the Sun was when the clock started. The star ray comes back around
  in 27.32 days; the Sun has moved on by then, so the same phase takes 29.53.

  Around the Sun. The path the Moon traces in space rather than relative to
  Earth. At true scale it is indistinguishable from Earth's own path, and it
  never loops backward: the Moon's 1.02 km/s around Earth is small against
  Earth's 29.8 km/s around the Sun. A slider exaggerates the Moon's distance,
  and the path keeps its outward curve until the exaggeration reaches the ratio
  of those two speeds, 29.1, where cusps appear. Past that it loops.

Positions come from the truncated ELP series in Meeus, Astronomical Algorithms,
chapter 47, with the solar longitude from chapter 25 and the illuminated
fraction from chapter 48. The tables live in moon_terms.py and are written into
the page, so the page and verify_moon.py compute from the same numbers.
Accuracy against pyephem over 2020 to 2030: illuminated fraction within 0.26
percentage points, distance within 25 km, phase times within about 3 minutes.

Usage: python3 build_moon.py
"""

import json
import math
from pathlib import Path

from moon_terms import LR, B

OUT = Path(__file__).parent.parent / "moon.html"

SYNODIC = 29.530589      # days, new moon to new moon
SIDEREAL = 27.321662     # days, back to the same star
ANOMALISTIC = 27.554550  # days, perigee to perigee
DRACONIC = 27.212221     # days, node to node
YEAR = 365.256363        # sidereal year

# The near side never turns away, so its features sit at fixed places on the
# disc. Each sea is listed by the patch of the Moon it actually covers, in
# selenographic latitude and longitude, and projected below the way the Moon is
# really seen: orthographic, north up, east to the right. Projecting the edges
# rather than the centre is what matters near the limb, where a degree of
# longitude is worth almost nothing: it is why Oceanus Procellarum is squeezed
# into a tall band along the western edge and Crisium into a small oval on the
# eastern one. The bounds are read off the standard near-side map to the
# nearest degree or so, so this is a likeness rather than an atlas, but nothing
# about the arrangement is invented.
#
#     name, latitude and longitude of the centre, half extent in each
MARIA_LL = [
    ("Oceanus Procellarum", 20.0, -52.5, 25.0, 32.5),
    ("Mare Imbrium", 33.0, -16.0, 15.0, 16.0),
    ("Mare Frigoris", 55.5, -10.0, 7.5, 50.0),
    ("Mare Serenitatis", 28.0, 18.0, 11.0, 12.0),
    ("Mare Tranquillitatis", 8.5, 31.5, 12.5, 13.5),
    ("Mare Crisium", 17.0, 59.5, 6.0, 10.5),
    ("Mare Fecunditatis", -7.5, 51.5, 13.5, 10.5),
    ("Mare Nectaris", -15.5, 35.5, 6.5, 7.5),
    ("Mare Nubium", -21.0, -16.0, 11.0, 11.0),
    ("Mare Cognitum", -10.0, -21.5, 6.0, 7.5),
    ("Mare Insularum", 7.5, -31.0, 9.5, 11.0),
    ("Mare Humorum", -24.5, -39.0, 6.5, 7.0),
    ("Mare Vaporum", 13.5, 3.5, 5.5, 7.5),
    ("Sinus Aestuum", 11.0, -9.0, 7.0, 6.0),
    ("Sinus Medii", 0.0, 1.5, 4.0, 4.5),
    ("Plato", 51.6, -9.3, 1.7, 2.8),
]
#     name, latitude, longitude, diameter in km, ray system
CRATERS_LL = [
    ("Tycho", -43.3, -11.4, 86, 1),
    ("Copernicus", 9.6, -20.1, 93, 1),
    ("Kepler", 8.1, -38.0, 32, 1),
    ("Aristarchus", 23.7, -47.4, 40, 1),
]
MOON_R = 1737.4          # km, which turns a crater's width into a fraction


def _project(lat, lon):
    """Where a place on the near side falls on the disc, orthographically."""
    la, lo = math.radians(lat), math.radians(lon)
    return math.cos(la) * math.sin(lo), -math.sin(la)


MARIA = []
for _nm, _la, _lo, _dla, _dlo in MARIA_LL:
    _xw, _ = _project(_la, _lo - _dlo)
    _xe, _ = _project(_la, _lo + _dlo)
    _, _yn = _project(_la + _dla, _lo)
    _, _ys = _project(_la - _dla, _lo)
    _x, _rx = (_xw + _xe) / 2, abs(_xe - _xw) / 2
    _y, _ry = (_yn + _ys) / 2, abs(_ys - _yn) / 2
    # near the limb a north-south feature leans, because the meridians converge
    _rot = -math.radians(_lo) * math.sin(math.radians(_la)) * 0.9
    MARIA.append((round(_x, 3), round(_y, 3), round(_rx, 3),
                  round(_ry, 3), round(_rot, 3), _nm))

CRATERS = []
for _nm, _la, _lo, _km, _rays in CRATERS_LL:
    _x, _y = _project(_la, _lo)
    CRATERS.append((round(_x, 3), round(_y, 3),
                    round(_km / 2 / MOON_R, 4), _rays, _nm))
MOON_EXAG = 90           # the Moon's orbit, widened so it can be seen at all

MOON_V = 1.022           # km/s around Earth
EARTH_V = 29.78          # km/s around the Sun
CUSP = EARTH_V / MOON_V  # exaggeration at which the heliocentric path cusps

FACTS = [
    ("Synodic month", f"{SYNODIC:.6f} days", "new moon to new moon, the month of phases"),
    ("Sidereal month", f"{SIDEREAL:.6f} days", "back to the same place against the stars"),
    ("Anomalistic month", f"{ANOMALISTIC:.6f} days", "perigee to perigee, which sets the apparent size"),
    ("Draconic month", f"{DRACONIC:.6f} days", "node to node, which decides whether an eclipse can happen"),
]


def main():
    js = {
        "LR": [list(t) for t in LR],
        "B": [list(t) for t in B],
        "SYN": SYNODIC, "SID": SIDEREAL, "ANO": ANOMALISTIC, "DRA": DRACONIC,
        "YEAR": YEAR, "CUSP": round(CUSP, 2),
        "MOONV": MOON_V, "EARTHV": EARTH_V, "EXAG": MOON_EXAG,
        "MARIA": [list(m[:5]) for m in MARIA],
        "CRATERS": [list(c[:4]) for c in CRATERS],
    }
    facts = "\n".join(
        f'<div class="fact"><div class="fn">{n}</div><div class="fv">{v}</div>'
        f'<div class="fd">{d}</div></div>' for n, v, d in FACTS)

    doc = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Month: The Moon's Loop · Altazor</title>
<style>
  :root { --text:#e8ecf4; --dim:#8b97ad; --accent:#5ab0ff; --warm:#f2c66b;
          --bg:#05070d; --panel:rgba(10,15,26,0.82); --line:rgba(90,176,255,0.22); }
  * { box-sizing: border-box; }
  html, body { margin:0; height:100%; background:var(--bg); color:var(--text);
    font:400 14px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
    overflow:hidden; }
  canvas { position:fixed; inset:0; width:100%; height:100%; display:block; }
  #hud { position:fixed; top:0; left:0; right:0; padding:18px 22px;
    display:flex; justify-content:space-between; align-items:flex-start;
    gap:18px; pointer-events:none; }
  #hud > * { pointer-events:auto; }
  #sitenav { display:flex; gap:16px; align-items:baseline; margin-bottom:6px; }
  .brand { font-weight:700; letter-spacing:.1em; text-decoration:none; color:var(--text); font-size:17px; }
  .brand:hover { color:var(--accent); }
  #sitenav a:not(.brand) { color:var(--dim); text-decoration:none; font-size:13px; }
  #sitenav a:not(.brand):hover { color:var(--accent); }
  h1 { font-size:19px; font-weight:600; margin:0; }
  #readout { background:var(--panel); border:1px solid var(--line); border-radius:12px;
    padding:12px 16px; min-width:212px; backdrop-filter:blur(7px); }
  .lbl { font-size:10.5px; color:var(--dim); text-transform:uppercase; letter-spacing:.08em; }
  .big { font-size:19px; font-weight:650; font-variant-numeric:tabular-nums; }
  .rr { display:flex; justify-content:space-between; gap:14px; font-size:12.5px; padding:2px 0; }
  .rr span:last-child { font-variant-numeric:tabular-nums; color:var(--dim); }
  #controls { position:fixed; left:0; right:0; bottom:0; padding:14px 22px 18px;
    background:linear-gradient(to top, rgba(5,7,13,0.95), rgba(5,7,13,0)); }
  .row { display:flex; align-items:center; gap:12px; margin:5px 0; flex-wrap:wrap; }
  label { min-width:150px; font-size:12.5px; color:var(--dim); }
  input[type=range] { flex:1; max-width:340px; accent-color:var(--accent); height:20px; }
  .val { font-size:12.5px; font-variant-numeric:tabular-nums; min-width:104px; color:var(--text); }
  button { background:#131d33; color:var(--text); border:1px solid var(--line);
    border-radius:8px; padding:5px 13px; font:inherit; font-size:12.5px; cursor:pointer; }
  button:hover { background:#1c2a48; }
  button[aria-pressed="true"] { border-color:var(--accent); color:var(--accent); }
  #note { margin-top:9px; font-size:11.5px; color:var(--dim); line-height:1.45; max-width:118ch; }
  #facts { display:flex; gap:16px; flex-wrap:wrap; margin-top:8px; }
  .fact { font-size:11.5px; }
  .fn { color:var(--dim); }
  .fv { font-variant-numeric:tabular-nums; color:var(--text); }
  .fd { color:#6c7688; font-size:11px; }
  @media (max-width: 760px) {
    #facts, #note { display:none; }
    label { min-width:104px; }
    #readout { min-width:0; }
  }
</style>
</head>
<body>
<canvas id="sky"></canvas>

<div id="hud">
  <div>
    <div id="sitenav"><a class="brand" href="index.html">ALTAZOR</a><a href="library.html">&larr; Library</a></div>
    <h1>The Month: The Moon's Loop</h1>
  </div>
  <div id="readout">
    <div class="lbl">Phase</div>
    <div class="big" id="phaseName">Full moon</div>
    <div class="rr"><span>Lit</span><span id="lit"></span></div>
    <div class="rr"><span>Age of the moon</span><span id="age"></span></div>
    <div class="rr"><span>Distance</span><span id="dist"></span></div>
    <div class="rr"><span>Apparent size</span><span id="size"></span></div>
    <div class="rr"><span>Date</span><span id="when"></span></div>
    <div class="rr" style="margin-top:6px"><span>Next new</span><span id="nextNew"></span></div>
    <div class="rr"><span>Next full</span><span id="nextFull"></span></div>
  </div>
</div>

<div id="controls">
  <div class="row">
    <label for="speed">Speed</label>
    <input type="range" id="speed" min="0" max="4" step="0.02" value="1.2">
    <div class="val" id="speedVal">1.2 days/s</div>
    <button id="playBtn" aria-pressed="true">Pause</button>
    <button id="nowBtn">Now</button>
  </div>
  <div class="row">
    <label for="scrub">Day of the month</label>
    <input type="range" id="scrub" min="0" max="29.530589" step="0.01" value="0">
    <div class="val" id="scrubVal">0.00 d</div>
    <button id="viewBtn" aria-pressed="false">Around the Sun</button>
  </div>
  <div class="row" id="exagRow" style="display:none">
    <label for="exag">Moon's distance, exaggerated</label>
    <input type="range" id="exag" min="1" max="60" step="0.5" value="1">
    <div class="val" id="exagVal">&times;1, true scale</div>
    <span id="cuspNote" style="font-size:11.5px;color:var(--dim)"></span>
  </div>
  <div id="facts">""" + facts + """</div>
  <div id="note" data-view="earth"></div>
</div>

<script>
const D = __DATA__;
const D2R = Math.PI / 180, R2D = 180 / Math.PI;
const NOTE_EARTH =
  "The Sun holds still, Earth goes round it once a year, and the Moon goes round Earth. "
  + "The pale arc closes after 27.32 days, when the Moon is back at the same star. Earth has moved along its "
  + "orbit by then, so the line to the Sun has swung about 27 degrees, and the Moon needs 2.21 days more to "
  + "catch it. That is the amber arc, and the month everyone counts: 29.53 days. The inset is lit on the right "
  + "while the Moon waxes and on the left while it wanes, which is how it hangs in a northern sky; from the south "
  + "it is the other way round. Its face never turns away, so the markings stay put while the light moves across "
  + "them.";

// ---------- the Moon and the Sun, from Meeus chapters 25, 47 and 48 ----------
function positions(jd) {
  const T = (jd - 2451545.0) / 36525;
  const Lp = 218.3164477 + 481267.88123421*T - 0.0015786*T*T + T**3/538841 - T**4/65194000;
  const Dm = 297.8501921 + 445267.1114034*T - 0.0018819*T*T + T**3/545868 - T**4/113065000;
  const M  = 357.5291092 + 35999.0502909*T - 0.0001536*T*T + T**3/24490000;
  const Mp = 134.9633964 + 477198.8675055*T + 0.0087414*T*T + T**3/69699 - T**4/14712000;
  const F  =  93.2720950 + 483202.0175233*T - 0.0036539*T*T - T**3/3526000 + T**4/863310000;
  const E = 1 - 0.002516*T - 0.0000074*T*T;
  let sl = 0, sr = 0, sb = 0;
  for (const [d, m, mp, f, cl, cr] of D.LR) {
    const a = (d*Dm + m*M + mp*Mp + f*F) * D2R, e = Math.pow(E, Math.abs(m));
    sl += cl*e*Math.sin(a); sr += cr*e*Math.cos(a);
  }
  for (const [d, m, mp, f, cb] of D.B) {
    const a = (d*Dm + m*M + mp*Mp + f*F) * D2R;
    sb += cb*Math.pow(E, Math.abs(m))*Math.sin(a);
  }
  const lam = ((Lp + sl/1e6) % 360 + 360) % 360;
  const beta = sb/1e6;
  const dist = 385000.56 + sr/1000;
  const L0 = 280.46646 + 36000.76983*T + 0.0003032*T*T;
  const Ms = 357.52911 + 35999.05029*T - 0.0001537*T*T;
  const C = (1.914602 - 0.004817*T - 0.000014*T*T)*Math.sin(Ms*D2R)
          + (0.019993 - 0.000101*T)*Math.sin(2*Ms*D2R)
          + 0.000289*Math.sin(3*Ms*D2R);
  const slon = (((L0 + C) % 360) + 360) % 360;
  const ecc = 0.016708634 - 0.000042037*T - 0.0000001267*T*T;
  const v = Ms + C;
  const R = 1.000001018*(1 - ecc*ecc)/(1 + ecc*Math.cos(v*D2R)) * 149597870.7;
  const psi = Math.acos(Math.cos(beta*D2R)*Math.cos((lam - slon)*D2R));
  const i = Math.atan2(R*Math.sin(psi), dist - R*Math.cos(psi));
  return { lam, beta, dist, slon, R,
           k: (1 + Math.cos(i))/2,
           elong: ((lam - slon) % 360 + 360) % 360 };
}

// The four named phases are instants, not stretches, so any window is a
// choice. Four degrees is about a third of a day either side, which is how an
// almanac labels the day a phase falls on.
const NAMED = 4;
function phaseName(e) {
  if (e < NAMED || e > 360 - NAMED) return 'New moon';
  if (Math.abs(e - 90) < NAMED) return 'First quarter';
  if (Math.abs(e - 180) < NAMED) return 'Full moon';
  if (Math.abs(e - 270) < NAMED) return 'Last quarter';
  if (e < 90) return 'Waxing crescent';
  if (e < 180) return 'Waxing gibbous';
  if (e < 270) return 'Waning gibbous';
  return 'Waning crescent';
}

// The next time the elongation passes a target. The elongation only ever
// increases, so the crossing to find is the upward one; testing for any sign
// change instead catches the jump where the difference wraps from +180 to -180
// and returns whichever phase event came first, whatever was asked for.
function nextPhase(jd, target) {
  const f = j => (((positions(j).elong - target + 180) % 360) + 360) % 360 - 180;
  let a = jd, b = jd + 0.5, guard = 0;
  while (!(f(a) < 0 && f(b) >= 0) && guard++ < 90) { a = b; b += 0.5; }
  for (let n = 0; n < 50; n++) {
    const m = (a + b)/2;
    if (f(m) < 0) a = m; else b = m;
  }
  return (a + b)/2;
}

const jdNow = () => Date.now()/86400000 + 2440587.5;
const jdToDate = jd => new Date((jd - 2440587.5)*86400000);
const fmtDate = jd => jdToDate(jd).toISOString().slice(0,16).replace('T',' ') + ' UT';

// ---------- state ----------
const cv = document.getElementById('sky'), ctx = cv.getContext('2d');
let W, H, dpr;
let jd = jdNow();
let jd0 = jd;                    // the clock's start, for the star ray
let at0 = null;                  // and its positions, which only change with it
const start = () => (at0 && at0.jd === jd0) ? at0
  : (at0 = Object.assign({jd: jd0}, positions(jd0)));
let playing = true, speed = 1.2, view = 'earth', exag = 1;
let stars = [];

function resize() {
  dpr = Math.min(window.devicePixelRatio || 1, 2);
  W = window.innerWidth; H = window.innerHeight;
  cv.width = W*dpr; cv.height = H*dpr;
  ctx.setTransform(dpr,0,0,dpr,0,0);
  face = null;                   // the cached near side is dpr-sized
  stars = [];
  for (let i = 0; i < 260; i++)
    stars.push({x: Math.random()*W, y: Math.random()*H,
                r: Math.random()*1.2+0.2, a: Math.random()*0.5+0.12});
}
window.addEventListener('resize', resize);

let face = null;
function moonFace(R) {
  // The near side is the same picture every night, so it is painted once and
  // kept. The seas go down together on their own layer and are blurred as one
  // sheet, which is what makes Procellarum, Imbrium and Frigoris run into each
  // other across the north west the way they do in the sky. Blurring each sea
  // on its own leaves a dozen round spots and the disc reads as a golf ball.
  const px = Math.max(32, Math.round(2*R*dpr));
  if (face && face.px === px) return face.cv;
  const s = px/(2*R);
  const cv2 = document.createElement('canvas');
  cv2.width = cv2.height = px;
  const g = cv2.getContext('2d');
  g.setTransform(s, 0, 0, s, 0, 0);
  g.translate(R, R);
  g.beginPath(); g.arc(0, 0, R, 0, 7); g.clip();

  g.fillStyle = '#c9c6bd';                       // the highlands
  g.beginPath(); g.arc(0, 0, R, 0, 7); g.fill();

  // The seas are laid down as overlapping circles on their own sheet, blurred,
  // then drawn over themselves several times. Compounding the alpha turns the
  // blur's soft halo back into an edge, and where two seas were close enough
  // for their halos to meet the edge closes around both of them. That is what
  // gives a coastline instead of a row of ovals, and it is why Procellarum,
  // Imbrium and Frigoris run together across the north west the way they do in
  // the sky.
  const sea = document.createElement('canvas');
  sea.width = sea.height = px;
  const q = sea.getContext('2d');
  q.setTransform(s, 0, 0, s, 0, 0);
  q.translate(R, R);
  q.fillStyle = '#000';
  // angle round the sea, how far out the lobe sits, how big it is. The reach
  // of each one differs, which is what keeps the outline from closing back
  // into a circle.
  const LOBE = [[0.35, 0.55, 0.45], [1.20, 0.42, 0.42], [2.00, 0.62, 0.36],
                [3.00, 0.38, 0.52], [3.90, 0.52, 0.32], [5.00, 0.46, 0.48]];
  // thresholding a blur puts the edge outside the shape that was drawn, by
  // roughly the blur's own width, so each sea is drawn that much smaller and
  // comes back out the right size
  const grow = R*0.066;
  D.MARIA.forEach(([x, y, rx, ry, rot], i) => {
    q.save();
    q.translate(x*R, y*R); q.rotate(rot);
    q.scale(Math.max(R*0.015, rx*R - grow), Math.max(R*0.015, ry*R - grow));
    // the sea fills the patch it is listed as covering, corners rounded off,
    // rather than an ellipse inscribed in it: two seas listed as touching have
    // to touch
    q.beginPath(); q.roundRect(-0.9, -0.9, 1.8, 1.8, 0.62); q.fill();
    for (const [a2, d, r] of LOBE) {
      const th = a2 + i*0.9;                   // fixed, but no two seas alike
      q.beginPath();
      q.arc(Math.cos(th)*d, Math.sin(th)*d, r, 0, 7);
      q.fill();
    }
    q.restore();
  });

  const coast = document.createElement('canvas');
  coast.width = coast.height = px;
  const w = coast.getContext('2d');
  w.filter = 'blur(' + Math.max(1, R*0.062).toFixed(2) + 'px)';
  w.drawImage(sea, 0, 0);
  w.filter = 'none';
  for (let i = 0; i < 7; i++) w.drawImage(coast, 0, 0);
  w.globalCompositeOperation = 'source-in';   // keep the shape, take the colour
  w.fillStyle = '#6b7280';
  w.fillRect(0, 0, px, px);

  g.save();
  g.filter = 'blur(' + Math.max(0.6, R*0.014).toFixed(2) + 'px)';
  g.drawImage(coast, -R, -R, 2*R, 2*R);
  g.restore();

  // Young craters threw bright material a long way out. At this size the rays
  // are a wash of light rather than the spokes a telescope shows, so that is
  // what gets drawn: a hard spoke pattern reads as a lens flare.
  for (const [x, y, r, rays] of D.CRATERS) {
    if (rays) {
      const reach = R*(0.10 + r*17);
      const halo = g.createRadialGradient(x*R, y*R, r*R, x*R, y*R, reach);
      halo.addColorStop(0, 'rgba(240,238,230,0.30)');
      halo.addColorStop(0.45, 'rgba(240,238,230,0.13)');
      halo.addColorStop(1, 'rgba(240,238,230,0)');
      g.fillStyle = halo;
      g.beginPath(); g.arc(x*R, y*R, reach, 0, 7); g.fill();
    }
    g.fillStyle = 'rgba(240,237,229,0.62)';
    g.beginPath(); g.arc(x*R, y*R, Math.max(0.8, r*R*0.9), 0, 7); g.fill();
  }
  // the limb falls away from the eye, so it darkens
  const lim = g.createRadialGradient(0, 0, R*0.55, 0, 0, R);
  lim.addColorStop(0, 'rgba(0,0,0,0)');
  lim.addColorStop(1, 'rgba(20,22,28,0.45)');
  g.fillStyle = lim;
  g.beginPath(); g.arc(0, 0, R, 0, 7); g.fill();

  face = {px: px, cv: cv2};
  return cv2;
}

function moonDisc(cx, cy, R, k, sunAng, plain) {
  // The face never turns away from us, so it is drawn in one fixed
  // orientation. Only the lighting moves: the lit region is clipped out of the
  // disc and the face painted inside it. Rotating the face along with the Sun
  // would mirror the Moon every time it started to wane.
  ctx.save();
  ctx.translate(cx, cy);
  ctx.fillStyle = '#0b0e14';
  ctx.beginPath(); ctx.arc(0, 0, R, 0, 7); ctx.fill();

  const t = 2*k - 1;
  ctx.save();
  ctx.rotate(sunAng);
  ctx.beginPath();
  ctx.arc(0, 0, R, -Math.PI/2, Math.PI/2, false);
  ctx.ellipse(0, 0, R*Math.abs(t), R, 0, Math.PI/2, -Math.PI/2, t < 0);
  ctx.closePath();
  ctx.restore();
  ctx.clip();

  if (plain || R <= 14) {
    ctx.fillStyle = '#c9c6bd';
    ctx.beginPath(); ctx.arc(0, 0, R, 0, 7); ctx.fill();
  } else {
    ctx.drawImage(moonFace(R), -R, -R, 2*R, 2*R);
  }
  ctx.restore();

  ctx.save(); ctx.translate(cx, cy);
  ctx.strokeStyle = 'rgba(200,214,240,0.30)'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.arc(0, 0, R, 0, 7); ctx.stroke();
  ctx.restore();
}

function drawEarthView(p) {
  // The Sun holds still, Earth goes round it, the Moon goes round Earth. The
  // Moon's orbit is 1/389 of Earth's, which is a hair at any zoom that fits the
  // year in, so it is drawn wider by a stated factor.
  const cx = W*0.5, cy = H*0.55;
  const Rorb = Math.min(W, H)*0.29;
  const rMoon = Rorb*384400/149597870.7*D.EXAG;

  const eAng = (p.slon + 180)*D2R;                 // Earth, seen from the Sun
  const ex = cx + Math.cos(eAng)*Rorb, ey = cy - Math.sin(eAng)*Rorb;
  const mAng = p.lam*D2R;                          // the Moon, seen from Earth
  const mx = ex + Math.cos(mAng)*rMoon, my = ey - Math.sin(mAng)*rMoon;

  // Earth's orbit, and the stretch of it just travelled
  ctx.strokeStyle = 'rgba(90,176,255,0.16)'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.arc(cx, cy, Rorb, 0, 7); ctx.stroke();
  const trailDays = 40;
  const a0 = (positions(jd - trailDays).slon + 180)*D2R;
  ctx.strokeStyle = 'rgba(90,176,255,0.55)'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.arc(cx, cy, Rorb, -a0, -eAng, true); ctx.stroke();

  // the Sun
  const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, Rorb*0.30);
  g.addColorStop(0, 'rgba(255,214,120,0.42)');
  g.addColorStop(0.24, 'rgba(255,180,70,0.10)');
  g.addColorStop(1, 'rgba(255,170,60,0)');
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, Rorb*0.30, 0, 7); ctx.fill();
  ctx.fillStyle = '#ffd257';
  ctx.beginPath(); ctx.arc(cx, cy, 11, 0, 7); ctx.fill();
  label('Sun', cx, cy + 26, 'rgba(242,198,107,0.9)', 'center');

  // the line Earth stands on, which is what the phase is measured against
  ctx.strokeStyle = 'rgba(242,198,107,0.45)'; ctx.setLineDash([5,6]); ctx.lineWidth = 1.2;
  ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(ex, ey); ctx.stroke();
  ctx.setLineDash([]);

  // a fixed direction in space, where the Moon stood when the clock started
  const star0 = start().lam*D2R;
  ctx.strokeStyle = 'rgba(190,205,235,0.42)'; ctx.setLineDash([6,7]); ctx.lineWidth = 1.1;
  ctx.beginPath(); ctx.moveTo(ex, ey);
  ctx.lineTo(ex + Math.cos(star0)*rMoon*2.1, ey - Math.sin(star0)*rMoon*2.1);
  ctx.stroke(); ctx.setLineDash([]);
  label('a fixed star', ex + Math.cos(star0)*rMoon*2.2, ey - Math.sin(star0)*rMoon*2.2 - 5,
        'rgba(190,205,235,0.8)', Math.cos(star0) < 0 ? 'right' : 'left');

  // the Moon's orbit, and the two cycles measured round it
  ctx.strokeStyle = 'rgba(200,214,240,0.22)'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.arc(ex, ey, rMoon, 0, 7); ctx.stroke();

  const sinceStar = ((p.lam - start().lam) % 360 + 360) % 360;
  ctx.strokeStyle = 'rgba(190,205,235,0.65)'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.arc(ex, ey, rMoon*0.62, -star0, -mAng, true); ctx.stroke();
  ctx.strokeStyle = 'rgba(242,198,107,0.75)'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.arc(ex, ey, rMoon*0.84, -(eAng + Math.PI), -mAng, true); ctx.stroke();

  // Earth, then the Moon on top of it
  ctx.fillStyle = '#3d7fd0';
  ctx.beginPath(); ctx.arc(ex, ey, 6.5, 0, 7); ctx.fill();
  ctx.strokeStyle = 'rgba(140,190,255,0.5)'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.arc(ex, ey, 9, 0, 7); ctx.stroke();
  label('Earth', ex, ey + 24, 'rgba(180,205,240,0.92)', 'center');
  moonDisc(mx, my, 6.5, p.k, -(eAng + Math.PI), true);

  // the two months, counted out where they happen
  colR = Math.max(150, Math.min(466, cx - Rorb - 42));
  const lines = [
    ['rgba(190,205,235,0.9)', 'round to the same star',
     (sinceStar/360*D.SID).toFixed(2) + ' of ' + D.SID.toFixed(2) + ' days'],
    ['rgba(242,198,107,0.95)', 'round to the same phase',
     (p.elong/360*D.SYN).toFixed(2) + ' of ' + D.SYN.toFixed(2) + ' days'],
  ];
  lines.forEach(([c, a, b2], i) => {
    const y = 236 + i*20;
    ctx.fillStyle = c;
    ctx.beginPath(); ctx.arc(52, y - 4, 4, 0, 7); ctx.fill();
    label(a, 64, y, 'rgba(160,175,200,0.85)', 'left');
    label(b2, colR, y, c, 'right');
    colInk = Math.max(colInk, colR);
  });
  wrapLabel("Earth's orbit is to scale; the Moon's is drawn " + D.EXAG
            + " times too wide so it can be seen at all",
            46, 292, 'rgba(120,133,155,0.85)', colR - 46, 15);

  wave(p);

  // the same Moon, drawn large enough to have a face
  const bigR = Math.min(96, Math.min(W, H)*0.12);
  const bx = W - bigR - 46, by = H - bigR - 132;
  // Waxing is lit on the right, waning on the left, which is the northern
  // hemisphere's view. The real tilt depends on where you stand.
  moonDisc(bx, by, bigR, p.k, p.elong < 180 ? 0 : Math.PI);
  label('as it looks from Earth', bx, by + bigR + 17, 'rgba(160,175,200,0.8)', 'center');
}

function wave(p) {
  const x0 = 46, x1 = Math.max(x0 + 120, Math.min(W - 46, colR)), y = 150, h = 34;
  colInk = Math.max(colInk, x1 + 22);   // 'new' is centred on the far end
  ctx.strokeStyle = 'rgba(120,150,200,0.25)'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(x0, y + h); ctx.lineTo(x1, y + h); ctx.stroke();
  ctx.beginPath();
  for (let i = 0; i <= 120; i++) {
    const e = i/120*360;
    const k = (1 - Math.cos(e*D2R))/2;
    const px = x0 + (x1 - x0)*i/120, py = y + h - k*h;
    i ? ctx.lineTo(px, py) : ctx.moveTo(px, py);
  }
  ctx.strokeStyle = 'rgba(233,228,214,0.55)'; ctx.lineWidth = 1.6; ctx.stroke();
  const fx = x0 + (x1 - x0)*(p.elong/360);
  ctx.fillStyle = '#e9e4d6';
  ctx.beginPath(); ctx.arc(fx, y + h - p.k*h, 3.4, 0, 7); ctx.fill();
  label('lit fraction through one month', x0, y - 6, 'rgba(160,175,200,0.75)', 'left');
  for (const [f, t] of [[0,'new'],[0.25,'first quarter'],[0.5,'full'],
                        [0.75,'last quarter'],[1,'new']]) {
    const px = x0 + (x1 - x0)*f;
    ctx.strokeStyle = 'rgba(120,150,200,0.18)';
    ctx.beginPath(); ctx.moveTo(px, y); ctx.lineTo(px, y + h); ctx.stroke();
    label(t, px, y + h + 13, 'rgba(140,155,180,0.7)', 'center');
  }
}

function drawSunView(p) {
  // Earth's path and the Moon's, seen from above the ecliptic. Sixty days of
  // orbit is too flat an arc to read, so the window is nearer four months and
  // the arc is sized to fill the frame rather than to any fixed scale.
  colR = Math.min(W - 46, 466);
  const days = 110, span = 360*days/D.YEAR, half = span/2*D2R;
  const Rpx = Math.min(W*0.82/(2*Math.sin(half)), H*0.52/(1 - Math.cos(half)));
  const cx = W*0.5, cy = H*0.26 + Rpx;
  const centre = -Math.PI/2;

  const earthAt = t => {
    const a = centre - half + 2*half*t;
    return [cx + Math.cos(a)*Rpx, cy + Math.sin(a)*Rpx];
  };
  ctx.strokeStyle = 'rgba(90,176,255,0.45)'; ctx.lineWidth = 1.6;
  ctx.beginPath();
  for (let i = 0; i <= 400; i++) {
    const [x, y] = earthAt(i/400);
    i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
  }
  ctx.stroke();

  const off = 384400/149597870.7*Rpx*exag;
  const jdA = jd - days/2, jdB = jd + days/2;
  const moonAt = t => {
    const j = jdA + (jdB - jdA)*t;
    const a = centre - half + 2*half*t;
    const [ex, ey] = earthAt(t);
    const ph = (positions(j).lam - positions(j).slon)*D2R;
    return [ex + Math.cos(a + Math.PI + ph)*off, ey + Math.sin(a + Math.PI + ph)*off];
  };
  // 600 ephemeris points is a lot to redo sixty times a second, and the curve
  // barely moves between frames, so it is rebuilt only when it has to be
  const key = Math.round(jd*4) + ':' + exag + ':' + Math.round(W) + ':' + Math.round(H);
  if (drawSunView.key !== key) {
    drawSunView.key = key;
    drawSunView.path = []; drawSunView.earth = [];
    for (let i = 0; i <= 600; i++) {
      drawSunView.path.push(moonAt(i/600));
      drawSunView.earth.push(earthAt(i/600));
    }
  }
  ctx.strokeStyle = 'rgba(233,228,214,0.92)'; ctx.lineWidth = 1.8;
  ctx.beginPath();
  drawSunView.path.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y));
  ctx.stroke();

  const [ex, ey] = earthAt(0.5);
  const [mx, my] = moonAt(0.5);
  // a short arrow toward the Sun, which is far below the frame
  ctx.strokeStyle = 'rgba(242,198,107,0.45)'; ctx.setLineDash([4,7]); ctx.lineWidth = 1.2;
  ctx.beginPath(); ctx.moveTo(ex, ey); ctx.lineTo(ex, ey + 96); ctx.stroke();
  ctx.setLineDash([]);
  label('to the Sun', ex + 8, ey + 92, 'rgba(242,198,107,0.7)', 'left');

  ctx.fillStyle = '#3d7fd0';
  ctx.beginPath(); ctx.arc(ex, ey, 6, 0, 7); ctx.fill();
  label('Earth', ex - 12, ey - 12, 'rgba(180,205,240,0.9)', 'right');
  ctx.fillStyle = '#e9e4d6';
  ctx.beginPath(); ctx.arc(mx, my, 3.6, 0, 7); ctx.fill();

  const cusping = exag >= D.CUSP;
  document.getElementById('cuspNote').textContent = cusping
    ? 'past ' + D.CUSP + ', the path cusps and then loops'
    : 'still curving away from the Sun the whole way round';
  label(days + ' days of both paths, seen from above the ecliptic. Earth in blue, the Moon in white.',
        46, 140, 'rgba(160,175,200,0.75)', 'left');
}

// Everything in the top left shares one column. Its right edge is set to
// clear whatever the diagram reaches, so no readout is ever printed over an
// orbit, at any window size.
let colR = 466, colInk = 0;
// the furthest right anything in the column was actually drawn, so the
// check can see an overlap rather than trust the intent
function wrapLabel(t, x, y, c, maxW, lineH) {
  ctx.font = '12px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
  const words = t.split(' ');
  let line = '', n = 0;
  for (const w of words) {
    const test = line ? line + ' ' + w : w;
    if (line && ctx.measureText(test).width > maxW) {
      label(line, x, y + n*lineH, c, 'left');
      colInk = Math.max(colInk, x + ctx.measureText(line).width);
      line = w; n++;
    } else line = test;
  }
  if (line) {
    label(line, x, y + n*lineH, c, 'left');
    colInk = Math.max(colInk, x + ctx.measureText(line).width);
    n++;
  }
  return n;
}

function label(t, x, y, c, align) {
  ctx.font = '12px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
  ctx.textAlign = align || 'left';
  ctx.fillStyle = c;
  ctx.fillText(t, x, y);
}

// ---------- readouts ----------
const el = id => document.getElementById(id);
let lastEvent = 0, cachedNew = 0, cachedFull = 0;
function readout(p) {
  el('phaseName').textContent = phaseName(p.elong);
  el('lit').textContent = (p.k*100).toFixed(1) + '%';
  el('age').textContent = (p.elong/360*D.SYN).toFixed(2) + ' d';
  el('dist').textContent = Math.round(p.dist).toLocaleString('en-US') + ' km';
  el('size').textContent = (2*Math.atan(1737.4/p.dist)*R2D*60).toFixed(1) + "'";
  el('when').textContent = fmtDate(jd);
  if (Math.abs(jd - lastEvent) > 0.4) {
    lastEvent = jd;
    cachedNew = nextPhase(jd, 0); cachedFull = nextPhase(jd, 180);
  }
  el('nextNew').textContent = fmtDate(cachedNew);
  el('nextFull').textContent = fmtDate(cachedFull);
  el('scrub').value = (p.elong/360*D.SYN).toFixed(2);
  el('scrubVal').textContent = (p.elong/360*D.SYN).toFixed(2) + ' d';
}

let last = performance.now();
function frame(t) {
  const dt = Math.min((t - last)/1000, 0.1); last = t;
  if (playing) jd += dt*speed;
  ctx.clearRect(0,0,W,H);
  for (const s of stars) {
    ctx.globalAlpha = s.a; ctx.fillStyle = '#cdd9f0';
    ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, 7); ctx.fill();
  }
  ctx.globalAlpha = 1;
  colInk = 0;
  const p = positions(jd);
  if (view === 'earth') drawEarthView(p); else drawSunView(p);
  readout(p);
  window.__moon = { jd, view, exag, playing, speed,
                    sunPath: view === 'sun' ? drawSunView.path : null,
                    earthPath: view === 'sun' ? drawSunView.earth : null,
                    k: p.k, elong: p.elong, dist: p.dist, lam: p.lam,
                    slon: p.slon, phase: phaseName(p.elong),
                    nextNew: cachedNew, nextFull: cachedFull,
                    colR: colR, colInk: colInk,
                    orbitLeft: view === 'earth'
                      ? W*0.5 - Math.min(W, H)*0.29 : null };
  requestAnimationFrame(frame);
}

el('speed').addEventListener('input', e => {
  speed = +e.target.value;
  el('speedVal').textContent = speed.toFixed(2) + ' days/s';
});
el('playBtn').addEventListener('click', () => {
  playing = !playing;
  el('playBtn').textContent = playing ? 'Pause' : 'Play';
  el('playBtn').setAttribute('aria-pressed', playing);
});
el('nowBtn').addEventListener('click', () => { jd = jdNow(); jd0 = jd; });
el('scrub').addEventListener('input', e => {
  // move to the requested age within the month the clock is in
  const want = +e.target.value/D.SYN*360;
  // the mean rate gets close in one step; a second step lands on it
  for (let n = 0; n < 3; n++) {
    const now = positions(jd).elong;
    jd += (((want - now + 180) % 360 + 360) % 360 - 180)/360*D.SYN;
  }
  playing = false;
  el('playBtn').textContent = 'Play';
  el('playBtn').setAttribute('aria-pressed', false);
});
el('viewBtn').addEventListener('click', () => {
  view = view === 'earth' ? 'sun' : 'earth';
  el('viewBtn').textContent = view === 'earth' ? 'Around the Sun' : 'Around the Earth';
  el('viewBtn').setAttribute('aria-pressed', view === 'sun');
  el('exagRow').style.display = view === 'sun' ? 'flex' : 'none';
  el('note').textContent = view === 'sun'
    ? "This is the path the Moon takes through space, not around the Earth. At true scale it sits on Earth's own "
      + "path and cannot be told apart from it. It never loops backward and never even straightens: the Moon moves "
      + "1.02 km/s around the Earth against Earth's 29.78 km/s around the Sun, so the Sun always wins. The slider "
      + "exaggerates the Moon's distance, and the curve holds until the exaggeration reaches " + D.CUSP
      + ", the ratio of those two speeds, where cusps appear. Past that it loops."
    : NOTE_EARTH;
});
el('exag').addEventListener('input', e => {
  exag = +e.target.value;
  el('exagVal').textContent = exag === 1 ? '\\u00d71, true scale' : '\\u00d7' + exag.toFixed(1);
});
el('note').textContent = NOTE_EARTH;
resize();
requestAnimationFrame(frame);
</script>
</body>
</html>
"""
    doc = doc.replace("__DATA__", json.dumps(js))
    OUT.write_text(doc, encoding="utf-8")
    print(f"wrote {OUT} ({len(doc):,} bytes): {len(LR)} longitude and distance "
          f"terms, {len(B)} latitude terms, cusp at x{CUSP:.2f}")


if __name__ == "__main__":
    main()
