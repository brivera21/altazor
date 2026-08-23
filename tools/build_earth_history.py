#!/usr/bin/env python3
"""Generate earth-history.html, The History of Earth.

The geological time scale has a scale problem: the Phanerozoic is the last
twelve per cent of the planet's life and carries nine tenths of the named
units, so a column drawn to one scale is either unreadable at the top or blank
at the bottom. This page answers it by zooming. Five lanes, one for each rank,
and clicking any unit makes it the whole width; the bar across the top keeps
all 4,567 million years in view so the window never gets lost.

The chart is the International Chronostratigraphic Chart, version v2026/06,
with every boundary carrying the uncertainty the chart prints and a mark where
the chart estimates rather than dates it. It is in ics_chart.py, which was read
off the chart itself and cross-checked against the Macrostrat API, and which
validates its own nesting: every unit sits inside its parent, and the children
of a unit tile it with no gap and no overlap.

The events plotted under the lanes each carry the source that dates them, and
the ones the literature disputes say so.

Usage: python3 build_earth_history.py
"""

import json
from pathlib import Path

from ics_chart import CHART, EVENTS, CHART_VERSION, CITATION

OUT = Path(__file__).parent.parent / "earth-history.html"

RANKS = ["eon", "era", "period", "epoch", "age"]

# The page's own colours, keyed to the eon and then to the era inside it. They
# are not the ICS chart's own, which this file does not carry.
ERA_HUE = {
    "Hadean": "#6b3f6e", "Eoarchean": "#8a3f63", "Paleoarchean": "#9a4667",
    "Mesoarchean": "#a94f6a", "Neoarchean": "#b7596e",
    "Paleoproterozoic": "#a85a45", "Mesoproterozoic": "#b06b3f",
    "Neoproterozoic": "#b57f3a",
    "Paleozoic": "#4d7f5e", "Mesozoic": "#3f7f8c", "Cenozoic": "#7f8b3f",
}
EON_HUE = {"Hadean": "#6b3f6e", "Archean": "#9a4667",
           "Proterozoic": "#ad6a40", "Phanerozoic": "#4f7f74"}

AGE_OF_EARTH = 4567.0
# The chart rounds its own base to 4,567 Ma while the oldest solids in the
# Solar System date a shade older, so the drawing runs to 4,568 and the
# arithmetic still uses the chart figure.
SPAN = 4568.0

FACTS = [
    ("Age of the Earth", "4,567 Ma",
     "dated from the oldest solids in the Solar System"),
    ("Oldest intact rock", "4,031 Ma",
     "the Acasta gneiss, which is also where the Archean begins"),
    ("Earliest accepted fossils", "3,480 Ma",
     "stromatolites in the Dresser Formation of Western Australia"),
    ("The chart", f"ICS {CHART_VERSION}",
     "the version this page is drawn from"),
]


def main():
    by = {u[0]: u for u in CHART}
    kids = {}
    for u in CHART:
        if u[2]:
            kids.setdefault(u[2], []).append(u[0])

    def era_of(name):
        cur = name
        while cur:
            if cur in ERA_HUE:
                return ERA_HUE[cur]
            cur = by[cur][2] if cur in by else None
        return "#4f7f74"

    units = []
    for name, rank, parent, a, b, unc, approx in CHART:
        units.append({
            "n": name, "r": RANKS.index(rank), "p": parent,
            "a": a, "b": b, "u": unc, "q": bool(approx),
            "c": EON_HUE[name] if rank == "eon" else era_of(name),
            "k": kids.get(name, []),
        })

    evs = [{"n": n, "a": ma, "r": list(rng) if rng else None,
            "d": desc, "s": src} for n, ma, rng, desc, src in EVENTS]
    evs.sort(key=lambda e: -e["a"])

    js = {"units": units, "events": evs, "age": AGE_OF_EARTH,
          "span": SPAN,
          "ranks": RANKS, "version": CHART_VERSION}
    blob = json.dumps(js, separators=(",", ":"))

    facts = "\n".join(
        f'<div class="tile"><div class="k">{n}</div>'
        f'<div class="v">{v}</div><div class="d">{d}</div></div>'
        for n, v, d in FACTS)

    doc = TEMPLATE.replace("__DATA__", blob).replace("__FACTS__", facts) \
                  .replace("__CITATION__", CITATION)
    OUT.write_text(doc, encoding="utf-8")
    print(f"wrote {OUT} ({len(doc):,} bytes): {len(units)} units of "
          f"{len(RANKS)} ranks, {len(evs)} events, chart {CHART_VERSION}")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The History of Earth &middot; Altazor</title>
<style>
:root{color-scheme:dark;
--ink:#e6e6e6; --ink2:#9aa3ad; --ink3:#7d848c;
--bg:#121212; --panel:#171a1d; --line:#2b2f34; --accent:#58a6ff;}
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

.stage{display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap}
.colwrap{flex:1 1 660px;min-width:320px}
svg{width:100%;height:auto;display:block;border-radius:10px;
border:1px solid var(--line);background:#0f1216}
.side{flex:1 1 260px;min-width:250px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:13px 15px}
.card h2{font-size:1.08rem;font-weight:600;margin:0 0 2px}
.card .sub{font-size:.8rem;color:var(--ink3);margin-bottom:9px}
.row{display:flex;justify-content:space-between;gap:12px;font-size:.87rem;padding:2.5px 0}
.row span:last-child{font-variant-numeric:tabular-nums;color:var(--ink2)}
.blurb{margin-top:10px;font-size:.84rem;color:var(--ink2);line-height:1.5}
.src{margin-top:6px;font-size:.75rem;color:var(--ink3);line-height:1.45}

.controls{margin:13px 0 0;display:flex;gap:.55rem;flex-wrap:wrap;align-items:center;
font-size:.85rem;color:var(--ink3)}
button{font:inherit;font-size:.85rem;background:none;color:var(--ink);
border:1px solid var(--line);border-radius:999px;padding:5px 13px;cursor:pointer}
button:hover{background:#20242a}
button:disabled{opacity:.4;cursor:default}
button[aria-pressed="true"]{border-color:var(--accent);color:var(--accent)}
#crumb{color:var(--ink2)}
#crumb b{color:var(--ink);font-weight:600}

.unit{cursor:pointer}
.unit rect{stroke:#0f1216;stroke-width:.8}
.unit:hover rect{stroke:#e6e6e6;stroke-width:1.4}
.unit text{fill:#0c0f12;font-size:11px;font-weight:600;pointer-events:none}
.unit text.pale{fill:#f0f3f6}
.lane{fill:#9aa3ad;font-size:10px;letter-spacing:.08em;text-transform:uppercase}
.tick{stroke:#39414a;stroke-width:1}
.ticklbl{fill:#7d848c;font-size:10px;font-variant-numeric:tabular-nums}
.ev{cursor:pointer}
.ev circle{fill:#f2c66b;stroke:#0f1216;stroke-width:1}
.ev:hover circle{fill:#fff}
.ev text{fill:#c7ceda;font-size:10px;pointer-events:none}
#over rect.all{fill:#1b2027;stroke:#2b2f34}
#over rect.win{fill:rgba(88,166,255,.28);stroke:#58a6ff;stroke-width:1}
#over text{fill:#7d848c;font-size:10px}

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

<h1>The History of Earth</h1>

<div class="tiles">__FACTS__</div>

<div class="stage">
  <div class="colwrap"><svg id="col" viewBox="0 0 1000 560"
       preserveAspectRatio="xMidYMid meet">
    <g id="over"></g>
    <g id="lanes"></g>
    <g id="ruler"></g>
    <g id="events"></g>
  </svg></div>
  <div class="side"><div class="card">
    <h2 id="selName">All of time</h2>
    <div class="sub" id="selSub">4,567 million years</div>
    <div class="row"><span>Begins</span><span id="selA"></span></div>
    <div class="row"><span>Ends</span><span id="selB"></span></div>
    <div class="row"><span>Lasts</span><span id="selD"></span></div>
    <div class="row"><span>Share of Earth's life</span><span id="selS"></span></div>
    <div class="blurb" id="selBlurb"></div>
    <div class="src" id="selSrc"></div>
  </div></div>
</div>

<div class="controls">
  <button id="bOut" disabled>Zoom out</button>
  <button id="bAll">All of time</button>
  <span id="crumb"></span>
</div>

<div class="notes">
<h2>About the chart</h2>
<p>Deep time will not sit on one scale. The Phanerozoic, the part with shells
and bones and everything a museum can hang on a wall, is the last eighth of the
planet's life, and nearly every named unit falls inside it. So the column
zooms: any band clicked becomes the whole width, its children fill the lane
below, and the bar along the top keeps all 4,567 million years in view so the
window is never lost.</p>
<p>Boundaries carry the uncertainty the chart prints. A tilde marks the ones
the chart estimates rather than dates, which is most of the Precambrian: those
are round numbers agreed on, not golden spikes driven into a cliff.</p>
<p>The events under the column are dated from the literature and each names its
source. Several are disputed, and those say so rather than picking a side.</p>
</div>

<div class="refs">
<h2>References</h2>
<p>__CITATION__</p>
<p>International Commission on Stratigraphy. (2026). <i>International
chronostratigraphic chart</i> (v2026/06). https://stratigraphy.org/chart</p>
<p>Peters, S. E., Husson, J. M., &amp; Czaplewski, J. (2018). Macrostrat: A
platform for geological data integration and deep-time Earth crust research.
<i>Geochemistry, Geophysics, Geosystems, 19</i>(4), 1393-1409.</p>
</div>
</main>
<script>
const D = __DATA__;
const el = id => document.getElementById(id);
const NS = 'http://www.w3.org/2000/svg';
const BY = {};
D.units.forEach(u => BY[u.n] = u);
const EONS = D.units.filter(u => u.r === 0);

const W = 1000, PAD = 54, TOP = 46, LANE = 30, GAP = 4;
let win = [D.span, 0];         // older first, in Ma
let stack = [];                // what was zoomed through to get here
let hover = null;

const x = ma => PAD + (win[0] - ma) / (win[0] - win[1]) * (W - 2 * PAD);
const fmtMa = v => v >= 1 ? v.toLocaleString('en-US', {maximumFractionDigits: 1})
  : v >= 0.001 ? (v * 1000).toFixed(1) + ' ka'.replace(' ka', '')
  : (v * 1e6).toFixed(0);
function span(v) {
  if (v >= 1) return v.toLocaleString('en-US', {maximumFractionDigits: 2}) + ' Ma';
  if (v >= 0.001) return (v * 1000).toFixed(1) + ' ka';
  return Math.round(v * 1e6).toLocaleString('en-US') + ' years';
}
function make(tag, attrs, parent) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  parent.appendChild(e);
  return e;
}
function clear(g) { while (g.firstChild) g.removeChild(g.firstChild); }
function light(hex) {
  const r = parseInt(hex.slice(1,3),16), g = parseInt(hex.slice(3,5),16),
        b = parseInt(hex.slice(5,7),16);
  return (0.299*r + 0.587*g + 0.114*b) < 128;
}

function draw() {
  const lanes = el('lanes'), ruler = el('ruler'), evg = el('events'),
        over = el('over');
  clear(lanes); clear(ruler); clear(evg); clear(over);

  // the whole of time, with the window marked on it
  const ow = W - 2 * PAD;
  make('rect', {x: PAD, y: 12, width: ow, height: 12, rx: 3, class: 'all'}, over);
  EONS.forEach(u => {
    make('rect', {x: PAD + (D.span - u.a) / D.span * ow, y: 12,
      width: Math.max(1, (u.a - u.b) / D.span * ow), height: 12,
      fill: u.c, 'fill-opacity': .55}, over);
  });
  const wx = PAD + (D.span - win[0]) / D.span * ow;
  const ww = Math.max(2, (win[0] - win[1]) / D.span * ow);
  make('rect', {x: wx, y: 9, width: ww, height: 18, rx: 3, class: 'win'}, over);
  const t = make('text', {x: PAD, y: 38}, over);
  t.textContent = 'all 4,567 million years, with the window shown';

  for (let r = 0; r < D.ranks.length; r++) {
    const y = TOP + 18 + r * (LANE + GAP);
    const lt = make('text', {x: 6, y: y + 20, class: 'lane'}, lanes);
    lt.textContent = D.ranks[r];
    for (const u of D.units) {
      if (u.r !== r || u.a <= win[1] || u.b >= win[0]) continue;
      const a = Math.min(u.a, win[0]), b = Math.max(u.b, win[1]);
      const x0 = x(a), x1 = x(b);
      if (x1 - x0 < 0.7) continue;
      const g = make('g', {class: 'unit'}, lanes);
      make('rect', {x: x0, y, width: x1 - x0, height: LANE, fill: u.c,
        'fill-opacity': .88}, g);
      if (x1 - x0 > 34) {
        const tx = make('text', {x: (x0 + x1) / 2, y: y + 19,
          'text-anchor': 'middle',
          class: light(u.c) ? 'pale' : ''}, g);
        tx.textContent = u.n;
        if (tx.getComputedTextLength && tx.getComputedTextLength() > x1 - x0 - 6)
          tx.textContent = u.n.slice(0, Math.max(1,
            Math.floor((x1 - x0 - 6) / 6.4))) + '…';
      }
      g.addEventListener('mouseenter', () => { hover = u.n; show(); });
      g.addEventListener('mouseleave', () => { hover = null; show(); });
      g.addEventListener('click', () => zoom(u));
    }
  }

  // the ruler, in millions of years before now
  const ry = TOP + 18 + D.ranks.length * (LANE + GAP) + 6;
  const dur = win[0] - win[1];
  const step = niceStep(dur / 7);
  make('line', {x1: PAD, y1: ry, x2: W - PAD, y2: ry, class: 'tick'}, ruler);
  for (let v = Math.ceil(win[1] / step) * step; v <= win[0] + 1e-9; v += step) {
    const px = x(v);
    make('line', {x1: px, y1: ry, x2: px, y2: ry + 5, class: 'tick'}, ruler);
    const lb = make('text', {x: px, y: ry + 17, 'text-anchor': 'middle',
      class: 'ticklbl'}, ruler);
    lb.textContent = v === 0 ? '0'
      : span(v).replace(' Ma', '').replace(' years', '').replace(' ka', '');
  }
  const un = make('text', {x: W - PAD, y: ry + 31, 'text-anchor': 'end',
    class: 'ticklbl'}, ruler);
  un.textContent = dur >= 2 ? 'millions of years ago'
    : dur >= 0.002 ? 'thousands of years ago' : 'years ago';

  // the events that fall in the window
  // Six rows of labels, no more. Nearly every event falls in the last eighth
  // of the record, so at full zoom they would otherwise stack forty deep and
  // bury the column. What will not fit keeps its tick and loses its label,
  // and gets one back as soon as the window is narrow enough.
  const ey = ry + 48, ROWS = 6;
  const rows = new Array(ROWS).fill(null);
  let used = 0, hidden = 0;
  for (const e of D.events) {
    if (e.a > win[0] || e.a < win[1]) continue;
    const px = x(e.a);
    const flip = px > W - PAD - 150;
    let row = -1;
    for (let i = 0; i < ROWS; i++) {
      const r = rows[i];
      if (r == null || (flip ? r - px > 150 : px - r > 150)) { row = i; break; }
    }
    const g = make('g', {class: 'ev'}, evg);
    const yy = ey + (row < 0 ? 0 : row) * 15;
    make('line', {x1: px, y1: ry, x2: px, y2: row < 0 ? ry + 7 : yy,
      stroke: '#3a4450', 'stroke-width': 1}, g);
    make('circle', {cx: px, cy: row < 0 ? ry + 7 : yy, r: row < 0 ? 2 : 3.2}, g);
    if (row >= 0) {
      rows[row] = px;
      used = Math.max(used, row + 1);
      const tx = make('text', {x: px + (flip ? -6 : 6), y: yy + 3.5,
        'text-anchor': flip ? 'end' : 'start'}, g);
      tx.textContent = e.n.length > 34 ? e.n.slice(0, 33) + '…' : e.n;
    } else {
      hidden++;
    }
    g.addEventListener('mouseenter', () => { hover = {e}; show(); });
    g.addEventListener('mouseleave', () => { hover = null; show(); });
  }
  if (hidden) {
    const nt = make('text', {x: W - PAD, y: ey + used * 15 + 14,
      'text-anchor': 'end', class: 'ticklbl'}, evg);
    nt.textContent = hidden + ' more events marked without a label; '
      + 'zooming in gives them their names back';
  }
  el('col').setAttribute('viewBox',
    `0 0 ${W} ${Math.max(300, ey + used * 15 + (hidden ? 26 : 14))}`);
}

function niceStep(raw) {
  const p = Math.pow(10, Math.floor(Math.log10(raw)));
  for (const m of [1, 2, 2.5, 5, 10]) if (raw <= m * p) return m * p;
  return 10 * p;
}

function zoom(u) {
  stack.push(win.slice());
  const pad = (u.a - u.b) * 0.04;
  win = [u.a + pad, Math.max(0, u.b - pad)];
  sel = u.n;
  el('bOut').disabled = false;
  draw(); show();
}
let sel = null;

function crumb() {
  if (!sel) { el('crumb').textContent = ''; return; }
  const chain = [];
  let c = sel;
  while (c) { chain.unshift(c); c = BY[c] ? BY[c].p : null; }
  el('crumb').innerHTML = chain.map((n, i) =>
    i === chain.length - 1 ? `<b>${n}</b>` : n).join(' &rsaquo; ');
}

function show() {
  const h = hover;
  if (h && h.e) {
    const e = h.e;
    el('selName').textContent = e.n;
    el('selSub').textContent = 'an event';
    el('selA').textContent = span(e.a) + ' ago';
    el('selB').textContent = e.r ? span(e.r[0]) + ' to ' + span(e.r[1]) : 'one date';
    el('selD').textContent = '--';
    el('selS').textContent = ((D.age - e.a) / D.age * 100).toFixed(1)
      + '% of the way to now';
    el('selBlurb').textContent = e.d;
    el('selSrc').textContent = 'Source: ' + e.s;
    return;
  }
  const n = (typeof h === 'string' ? h : null) || sel;
  const u = n ? BY[n] : null;
  if (!u) {
    el('selName').textContent = 'All of time';
    el('selSub').textContent = '4,567 million years';
    el('selA').textContent = '4,567 Ma';
    el('selB').textContent = 'now';
    el('selD').textContent = '4,567 Ma';
    el('selS').textContent = '100%';
    el('selBlurb').textContent = 'Any band opens: the eons hold eras, the eras '
      + 'hold periods, and so on down to the ages, which are the finest units '
      + 'the chart names.';
    el('selSrc').textContent = 'Chart ' + D.version;
    crumb();
    return;
  }
  const dur = u.a - u.b;
  el('selName').textContent = u.n;
  el('selSub').textContent = D.ranks[u.r] + (u.p ? ' of the ' + u.p : '');
  el('selA').textContent = (u.q ? '~' : '') + span(u.a)
    + (u.u ? ' ± ' + u.u : '') + ' ago';
  el('selB').textContent = u.b === 0 ? 'now' : span(u.b) + ' ago';
  el('selD').textContent = span(dur);
  el('selS').textContent = (dur / D.age * 100).toFixed(dur / D.age > 0.01 ? 1 : 3) + '%';
  const inside = D.events.filter(e => e.a <= u.a && e.a >= u.b);
  el('selBlurb').innerHTML = (u.k.length
    ? 'Holds ' + u.k.length + ' ' + D.ranks[u.r + 1] + (u.k.length > 1 ? 's' : '')
      + ': ' + u.k.join(', ') + '. '
    : 'The chart names nothing finer inside it. ')
    + (inside.length ? 'Events here: ' + inside.map(e => e.n).join('; ') + '.' : '');
  el('selSrc').textContent = 'Chart ' + D.version
    + (u.q ? '; the base of this unit is estimated, not dated' : '');
  crumb();
}

el('bOut').addEventListener('click', () => {
  if (!stack.length) return;
  win = stack.pop();
  sel = sel && BY[sel] ? BY[sel].p : null;
  el('bOut').disabled = !stack.length;
  draw(); show();
});
el('bAll').addEventListener('click', () => {
  win = [D.span, 0]; stack = []; sel = null;
  el('bOut').disabled = true;
  draw(); show();
});

draw(); show();
window.__hist = () => ({win: win.slice(), sel, depth: stack.length,
  units: D.units.length, events: D.events.length,
  drawn: document.querySelectorAll('#lanes .unit').length,
  shown: document.querySelectorAll('#events .ev').length});
window.__zoom = n => { const u = BY[n]; if (u) zoom(u); return win.slice(); };
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
