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
from pathlib import Path

from moon_terms import LR, B

OUT = Path(__file__).parent.parent / "moon.html"

SYNODIC = 29.530589      # days, new moon to new moon
SIDEREAL = 27.321662     # days, back to the same star
ANOMALISTIC = 27.554550  # days, perigee to perigee
DRACONIC = 27.212221     # days, node to node
YEAR = 365.256363        # sidereal year

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
        "MOONV": MOON_V, "EARTHV": EARTH_V,
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
  "The Earth and the Moon are drawn to scale here, distance and sizes together: sixty Earths fit in the gap. "
  + "Three rays leave the Earth. The pale one points at a fixed star, and the Moon comes back to it every 27.32 "
  + "days. The bright one points at the Sun, and it swings about a degree a day, so the Moon needs 2.21 days more "
  + "to catch it and return to the same phase. That is the month everyone counts, 29.53 days. The inset is lit on "
  + "the right while the Moon waxes and on the left while it wanes, which is how it hangs in a northern sky; from "
  + "the south it is the other way round.";

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
  stars = [];
  for (let i = 0; i < 260; i++)
    stars.push({x: Math.random()*W, y: Math.random()*H,
                r: Math.random()*1.2+0.2, a: Math.random()*0.5+0.12});
}
window.addEventListener('resize', resize);

function moonDisc(cx, cy, R, k, sunAng) {
  // the terminator projects to an ellipse; t runs -1 at new to +1 at full
  const t = 2*k - 1;
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(sunAng);
  ctx.fillStyle = '#1d2330';
  ctx.beginPath(); ctx.arc(0,0,R,0,7); ctx.fill();
  ctx.strokeStyle = 'rgba(200,214,240,0.30)'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.arc(0,0,R,0,7); ctx.stroke();
  ctx.fillStyle = '#e9e4d6';
  ctx.beginPath();
  // The lit limb is the half facing the Sun. The terminator closes it: for a
  // gibbous the ellipse must sweep the far side (adding to the half disc), for
  // a crescent it sweeps back across the near side (cutting into it). Getting
  // that direction backwards draws every phase as its own opposite.
  ctx.arc(0, 0, R, -Math.PI/2, Math.PI/2, false);
  ctx.ellipse(0, 0, R*Math.abs(t), R, 0, Math.PI/2, -Math.PI/2, t < 0);
  ctx.closePath(); ctx.fill();
  ctx.restore();
}

function drawEarthView(p) {
  const cx = W*0.5, cy = H*0.52;
  // true scale: 384,400 km against Earth's 6,371 km radius
  const orbit = Math.min(W, H)*0.34;
  const kmPerPx = 384400/orbit;
  const rE = 6371/kmPerPx, rM = 1737.4/kmPerPx;
  const rNow = p.dist/kmPerPx;

  const sunAng = (p.slon + 180)*D2R;          // direction from Earth to the Sun
  const sun0 = (start().slon + 180)*D2R;
  const moonAng = (p.lam + 180)*D2R;          // geocentric, drawn from above
  const star0 = (start().lam + 180)*D2R;

  const at = (ang, r) => [cx + Math.cos(ang)*r, cy - Math.sin(ang)*r];

  // the orbit, and the range perigee to apogee
  ctx.strokeStyle = 'rgba(120,150,200,0.13)'; ctx.lineWidth = 1;
  for (const d of [356500, 406700]) {
    ctx.beginPath(); ctx.arc(cx, cy, d/kmPerPx, 0, 7); ctx.stroke();
  }
  ctx.setLineDash([3,5]);
  ctx.strokeStyle = 'rgba(120,150,200,0.30)';
  ctx.beginPath(); ctx.arc(cx, cy, rNow, 0, 7); ctx.stroke();
  ctx.setLineDash([]);

  // the ray to a fixed star, where the Moon stood when the clock started
  const [sx1, sy1] = at(star0, Math.min(W,H)*0.47);
  ctx.strokeStyle = 'rgba(190,205,235,0.45)'; ctx.setLineDash([6,7]); ctx.lineWidth = 1.2;
  ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(sx1, sy1); ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = 'rgba(215,228,250,0.9)';
  ctx.beginPath(); ctx.arc(sx1, sy1, 2.4, 0, 7); ctx.fill();
  label('a fixed star', sx1, sy1 - 12, 'rgba(190,205,235,0.75)', star0 > Math.PI/2 && star0 < 3*Math.PI/2 ? 'right' : 'left');

  // the Sun now, and where it stood when the clock started
  const [ox1, oy1] = at(sun0, Math.min(W,H)*0.44);
  ctx.strokeStyle = 'rgba(242,198,107,0.22)'; ctx.setLineDash([4,6]);
  ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(ox1, oy1); ctx.stroke();
  ctx.setLineDash([]);
  const [ux, uy] = at(sunAng, Math.min(W,H)*0.44);
  ctx.strokeStyle = 'rgba(242,198,107,0.75)'; ctx.lineWidth = 1.6;
  ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(ux, uy); ctx.stroke();
  const g = ctx.createRadialGradient(ux, uy, 0, ux, uy, 26);
  g.addColorStop(0,'rgba(255,214,120,0.95)'); g.addColorStop(1,'rgba(255,190,80,0)');
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(ux, uy, 26, 0, 7); ctx.fill();
  ctx.fillStyle = '#ffd76a'; ctx.beginPath(); ctx.arc(ux, uy, 5, 0, 7); ctx.fill();
  label('to the Sun', ux, uy - 15, 'rgba(242,198,107,0.9)',
        sunAng > Math.PI/2 && sunAng < 3*Math.PI/2 ? 'right' : 'left');

  // how far the Sun has moved since the clock started
  const swept = ((p.slon - start().slon) % 360 + 360) % 360;
  if (swept > 1.2) {
    ctx.strokeStyle = 'rgba(242,198,107,0.5)'; ctx.lineWidth = 1.4;
    ctx.beginPath();
    ctx.arc(cx, cy, Math.min(W,H)*0.40, -sun0, -sunAng, true);
    ctx.stroke();
    const mid = (sun0 + swept*D2R/2);
    const [mx, my] = at(mid, Math.min(W,H)*0.40 + 15);
    label(swept.toFixed(1) + '\\u00b0 of Sun', mx, my, 'rgba(242,198,107,0.85)', 'center');
  }

  // Earth
  ctx.fillStyle = '#3d7fd0';
  ctx.beginPath(); ctx.arc(cx, cy, Math.max(rE, 2), 0, 7); ctx.fill();
  label('Earth', cx, cy + Math.max(rE,2) + 15, 'rgba(180,205,240,0.85)', 'center');

  // the Moon, at true size and true distance
  const [mx2, my2] = at(moonAng, rNow);
  // screen y runs down, so a world direction theta is drawn at -theta; the lit
  // limb has to face the Sun, not away from it
  moonDisc(mx2, my2, Math.max(rM, 2), p.k, -sunAng);
  ctx.strokeStyle = 'rgba(233,228,214,0.5)'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.arc(mx2, my2, Math.max(rM,2) + 5, 0, 7); ctx.stroke();

  // the same Moon, drawn large enough to read
  const bigR = Math.min(96, Math.min(W, H)*0.12);
  const bx = W - bigR - 46, by = H - bigR - 132;
  // Waxing is lit on the right, waning on the left, which is the northern
  // hemisphere's view. The real tilt depends on where you stand and how high
  // the Moon is, so any fixed orientation is a convention.
  moonDisc(bx, by, bigR, p.k, p.elong < 180 ? 0 : Math.PI);
  label('as it looks from Earth', bx, by + bigR + 17, 'rgba(160,175,200,0.8)', 'center');

  // the month as a wave, one synodic period wide
  wave(p);
  scaleBar(kmPerPx);
}

function wave(p) {
  const x0 = 46, x1 = Math.min(W - 46, x0 + 420), y = 150, h = 34;
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

function scaleBar(kmPerPx) {
  const px = 100, km = px*kmPerPx;
  const nice = Math.pow(10, Math.floor(Math.log10(km)));
  const step = (km/nice < 1.5 ? 1 : km/nice < 3.5 ? 2 : km/nice < 7.5 ? 5 : 10)*nice;
  const w = step/kmPerPx;
  const x = 46, y = 232;
  ctx.strokeStyle = 'rgba(160,175,200,0.55)'; ctx.lineWidth = 1.4;
  ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + w, y); ctx.stroke();
  label(step.toLocaleString('en-US') + ' km', x, y - 7, 'rgba(160,175,200,0.8)', 'left');
}

function drawSunView(p) {
  // Earth's path and the Moon's, seen from above the ecliptic. Sixty days of
  // orbit is too flat an arc to read, so the window is nearer four months and
  // the arc is sized to fill the frame rather than to any fixed scale.
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
  const p = positions(jd);
  if (view === 'earth') drawEarthView(p); else drawSunView(p);
  readout(p);
  window.__moon = { jd, view, exag, playing, speed,
                    sunPath: view === 'sun' ? drawSunView.path : null,
                    earthPath: view === 'sun' ? drawSunView.earth : null,
                    k: p.k, elong: p.elong, dist: p.dist, lam: p.lam,
                    slon: p.slon, phase: phaseName(p.elong),
                    nextNew: cachedNew, nextFull: cachedFull };
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
