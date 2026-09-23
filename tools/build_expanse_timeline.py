#!/usr/bin/env python3
"""Builds expanse-timeline.html: The Expanse by milestone year.

The span runs from about two billion years ago to 2353, and the last four
years hold most of the story, so the axis is broken into four segments with
visible breaks between them: deep time, 2025 to 2150, 2213 to 2341, and 2342
to 2353 drawn about twelve times larger. On a narrow screen the same eras and
badges become a vertical list.

Source badges say what each year rests on. They are drawn as one hue stepped
from bright to dim, in the brief's order from most to least solid, and the
shape carries it too: filled for novels, show and design guide, a ring for the
wiki and fan chronologies, a dashed ring for the one extrapolated date. The
ramp was checked with the dataviz validator as an ordinal ramp on the site's
dark surface.
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import apa
from expanse_timeline_data import (SOURCES, SEGMENTS, ERAS, POWERS, MILESTONES,
                                   GAPS, TAGLINE, INTRO, CLOSING)

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "expanse-timeline.html"
TITLE = "The Expanse: A Timeline by Milestone Year"
RETRIEVED = "September 23, 2026"

# one hue, bright to dim: most solid source to least (validated, ordinal, dark)
RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95"]


def fandom(title, url):
    return (f"{title}. (n.d.). In <i>The Expanse Wiki</i>. "
            f"Retrieved {RETRIEVED}, from {url}")


def untitled(title, site, url):
    return f"<i>{title}</i>. (n.d.). {site}. Retrieved {RETRIEVED}, from {url}"


REFS = apa.render([
    (apa.book("Corey, J. S. A.", 2011, "Leviathan Wakes", "Orbit"),
     "The first novel: 2320, 2336 and the events of 2350."),
    (apa.book("Corey, J. S. A.", 2012, "Caliban's War", "Orbit"),
     "The second: Ganymede, Io and Venus."),
    (apa.book("Corey, J. S. A.", 2013, "Abaddon's Gate", "Orbit"),
     "The third, where this page stops."),
    (apa.book("Corey, J. S. A.", 2015, "The Vital Abyss", "Orbit"),
     "The novella behind the 2342 discovery on Phoebe."),
    ("Corey, J. S. A. (2012). Drive. In J. Strahan (Ed.), <i>Edge of Infinity</i>. Solaris.",
     "The short story of Epstein's flight, and of the plans his wife found."),
    ("<i>The Expanse</i> [TV series]. (2015–2022). Syfy; Amazon Prime Video.",
     "Seasons 1 to 3. Episode numbers are given in the milestone notes."),
    (fandom("Timeline and chronology",
            "https://expanse.fandom.com/wiki/Timeline_and_chronology"),
     "Most of the specific years, and the statement that, save for one date, no "
     "chronology has been confirmed within the series."),
    (fandom("Epstein Drive", "https://expanse.fandom.com/wiki/Epstein_Drive"),
     "About 2213, and the flip at the midpoint."),
    (fandom("Solomon Epstein (Books)",
            "https://expanse.fandom.com/wiki/Solomon_Epstein_(Books)"),
     "Born on Mars; the plans found on his home computer."),
    (fandom("Earth", "https://expanse.fandom.com/wiki/Earth"),
     "31 billion across Earth and its colonies, over half on Basic, the UN as a "
     "parliamentary republic."),
    (f"Caliban's War. (n.d.). In <i>Wikipedia</i>. Retrieved {RETRIEVED}, from "
     "https://en.wikipedia.org/wiki/Caliban%27s_War",
     "The hybrid rockets launched at Mars."),
    (untitled("The Expanse complete timeline explained", "Screen Rant",
              "https://screenrant.com/expanse-timeline-explained/"),
     "Mars past 100 million by 2150, and Avasarala in 2339."),
    (untitled("The Expanse: A personal distress call", "Vissiniti",
              "https://vissiniti.com/the-expanse-a-personal-distress-call/"),
     "The gin label in season 2, episode 5: “since 2307.”"),
])

METHOD = (
    "The axis is broken four ways because one scale cannot hold the span: two "
    "billion years sit in the first segment as a single point, and the last "
    "segment, 2342 to 2353, is drawn about twelve times larger than the one before "
    "it. Each badge says what the year rests on, not where the event is told; the "
    "note under a milestone gives both when they differ. The badges run from "
    "bright to dim and from filled to hollow in the brief's order, most solid "
    "first. A few claims in the brief were checked against its own sources and "
    "corrected: the gin date is the show's, Epstein's plans were on his home "
    "computer, the hybrids were launched at Mars, and the first interval is "
    "about 160 years.")

CSS = """
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; --surface:#0d0d0d; }
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
h1 { margin:0 0 6px; font-size:26px; }
.sub { color:var(--muted); margin:0 0 16px; font-size:15px; }
.controls { display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin:0 0 14px; }
.controls .lab { color:var(--muted); font-size:12.5px; letter-spacing:.06em;
  text-transform:uppercase; margin-right:4px; }
.src { font:inherit; font-size:13px; padding:5px 12px 5px 9px; border-radius:999px;
  border:1px solid var(--line); background:var(--panel); color:var(--text); cursor:pointer;
  display:inline-flex; align-items:center; gap:7px; }
.src:hover { border-color:var(--accent); }
.src[aria-pressed="false"] { color:#6a6a6a; border-style:dashed; }
.src[aria-pressed="false"] svg { opacity:.35; }
.src svg, .badge svg { width:12px; height:12px; flex:none; }

.stage { display:grid; grid-template-columns:minmax(0,1fr) 340px; gap:22px; align-items:start; }
@media (max-width:1100px){ .stage { grid-template-columns:1fr; } }
#diagram > svg { width:100%; height:auto; display:block; background:var(--surface);
  border:1px solid #333; border-radius:6px; }
#diagram .hit { cursor:pointer; }
#diagram .hit:focus { outline:none; }
#diagram .hit:focus-visible .focus { stroke:var(--accent); stroke-width:2; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:16px 18px; }
.card .era { color:var(--muted); font-size:12px; letter-spacing:.08em; text-transform:uppercase; }
.card .yr { font-size:22px; font-weight:650; margin:4px 0 0; font-variant-numeric:tabular-nums; }
.card .lbl { font-size:15px; margin:2px 0 10px; }
.badge { display:inline-flex; align-items:center; gap:6px; font-size:12.5px; color:var(--text);
  border:1px solid var(--line); border-radius:999px; padding:2px 10px 2px 7px; background:#141414; }
.note { color:var(--muted); font-size:12.5px; margin:6px 0 12px; }
.body p { margin:0 0 11px; font-size:14.5px; color:#d4d4d4; }
.body ol { margin:0 0 11px; padding-left:20px; font-size:14.5px; color:#d4d4d4; }
.body li { margin:0 0 5px; }
.body dl { margin:0; }
.body dt { font-weight:650; font-size:14px; margin:10px 0 2px; }
.body dd { margin:0 0 6px; font-size:14.5px; color:#d4d4d4; }

#tip { position:fixed; pointer-events:none; z-index:10; background:#1f1f1f; border:1px solid #3a3a3a;
  border-radius:6px; padding:6px 9px; font-size:12.5px; max-width:280px; display:none; }
#tip b { font-variant-numeric:tabular-nums; }

.eraPanel { margin-top:22px; border-top:1px solid var(--line); padding-top:18px; }
.eraPanel h2 { font-size:19px; margin:0; }
.eraPanel .span { color:var(--muted); font-size:13.5px; margin:0 0 10px; }
.eraPanel p { max-width:76ch; color:#d4d4d4; margin:0 0 11px; }
.powers { display:grid; grid-template-columns:repeat(3, 1fr); gap:14px; margin:12px 0 14px; }
@media (max-width:900px){ .powers { grid-template-columns:1fr; } }
.power { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:14px 16px; }
.power h3 { margin:0 0 6px; font-size:16px; }
.power dt { color:var(--muted); font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; margin-top:8px; }
.power dd { margin:2px 0 0; font-size:14px; color:#d4d4d4; }
.xfer { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin:12px 0 14px; max-width:820px; }
@media (max-width:640px){ .xfer { grid-template-columns:1fr; } }
.xfer figure { margin:0; background:var(--surface); border:1px solid #333; border-radius:6px; padding:10px 12px; }
.xfer svg { width:100%; height:auto; display:block; }
.xfer figcaption { color:var(--muted); font-size:12.5px; margin-top:6px; }

.gaps { margin-top:26px; border-top:1px solid var(--line); padding-top:18px; }
.gaps svg { width:100%; max-width:980px; height:auto; display:block; }
.gaps p { max-width:76ch; color:#d4d4d4; margin:10px 0 0; }

#vlist { display:none; }
@media (max-width:760px) {
  .stage, .eraPanel { display:none !important; }
  #vlist { display:block; }
}
.vera { border-left:2px solid #333; margin:0 0 6px 6px; padding:0 0 10px 16px; position:relative; }
.vera.brk { border-left-style:dashed; }
.vera h2 { font-size:16px; margin:0; padding-top:8px; }
.vera .span { color:var(--muted); font-size:12.5px; margin:0 0 6px; }
.vitem { margin:0 0 4px; }
.vitem > button { all:unset; box-sizing:border-box; display:grid; grid-template-columns:16px 58px 1fr;
  gap:8px; align-items:start; width:100%; cursor:pointer; padding:6px 0; }
.vitem > button:focus-visible { outline:2px solid var(--accent); outline-offset:2px; }
.vitem .vyr { font-variant-numeric:tabular-nums; font-weight:650; font-size:14px; }
.vitem .vlbl { font-size:14px; }
.vitem .vbody { padding:2px 0 8px 24px; }
.vera details { margin:4px 0 0; }
.vera summary { color:var(--muted); font-size:13px; cursor:pointer; }
.vbreak { color:#6a6a6a; font-size:12px; margin:0 0 6px 22px; font-style:italic; }

.desc { margin-top:30px; border-top:1px solid var(--line); padding-top:16px; }
.desc p { max-width:76ch; color:#c9c9c9; margin:0 0 12px; }
.method, .refs { color:var(--muted); font-size:13.5px; max-width:80ch; }
.refs a { color:var(--accent); overflow-wrap:anywhere; }
.stage > .left { min-width:0; }
.stage .eraPanel { margin-top:18px; }
.method { border-top:1px solid var(--line); margin-top:30px; padding-top:14px; }
.refh { font-size:14px; color:var(--muted); margin:26px 0 8px; letter-spacing:.06em; text-transform:uppercase; }
footer.site { margin-top:50px; padding-top:18px; border-top:1px solid var(--line); font-size:13px; color:var(--muted); }
footer.site a { color:var(--muted); }
footer.site a:hover { color:var(--accent); }
__APACSS__
[hidden] { display:none !important; }
@media (prefers-reduced-motion: reduce) { * { animation:none !important; transition:none !important; } }
"""

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ &middot; Altazor</title>
<meta name="description" content="The Expanse from the ring builders to the opening of the Ring, by milestone year, with what each date rests on.">
<style>__CSS__</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="science-fiction.html">&larr; Science Fiction</a>
  <a href="ksr-2312-timeline.html">The Centuries Before 2312</a>
  <a href="solar-system-2312.html">The Solar System of 2312</a></nav>
</header>
<h1>__TITLE__</h1>
<p class="sub">__TAGLINE__</p>

<div class="controls" id="filters"><span class="lab">Sources</span></div>

<div class="stage">
  <div class="left">
    <div id="diagram"></div>
    <div class="eraPanel diagram-text" id="eraPanel"></div>
  </div>
  <div class="side diagram-text"><div class="card" id="card" aria-live="polite"></div></div>
</div>
<div id="vlist" class="diagram-text"></div>

<div class="gaps diagram-text">
  <div id="gapbar"></div>
  <p>__CLOSING__</p>
</div>

<div class="desc">
__INTRO__
</div>

<div class="method"><p>__METHOD__</p></div>
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>

<footer class="site"><a href="index.html">Altazor</a> &middot; <a href="science-fiction.html">Science Fiction</a></footer>
</div>
<div id="tip"></div>
<script>
const D = __DATA__;
__SCRIPT__
</script>
</body>
</html>
"""

SCRIPT = r"""
const RAMP = D.ramp, SRC = D.sources.map(s => s[0]), SHAPE = Object.fromEntries(D.sources);
const ERA = Object.fromEntries(D.eras.map(e => [e.key, e]));
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const md = s => esc(s).replace(/\*([^*]+)\*/g, '<i>$1</i>');
const plain = s => String(s).replace(/\*/g, '');
const on = new Set(SRC);
let sel = D.milestones.findIndex(m => m.sort === 2213);
const visible = () => D.milestones.map((m, i) => i).filter(i => on.has(D.milestones[i].source));

// ---- markers: shade by source rank, shape by kind ----
function markerSVG(src, r, cx, cy) {
  const c = RAMP[SRC.indexOf(src)], k = SHAPE[src];
  if (k === 'fill') return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${c}" stroke="#0d0d0d" stroke-width="2"/>`;
  const dash = k === 'dash' ? ' stroke-dasharray="2.5 2"' : '';
  return `<circle cx="${cx}" cy="${cy}" r="${r - 1}" fill="#0d0d0d" stroke="${c}" stroke-width="2.4"${dash}/>`;
}
const chip = src => `<svg viewBox="0 0 12 12" aria-hidden="true">${markerSVG(src, 5, 6, 6)}</svg>`;
const badge = src => `<span class="badge">${chip(src)}${esc(src)}</span>`;

function body(parts) {
  return parts.map(p => {
    if (typeof p === 'string') return `<p>${md(p)}</p>`;
    if (p.ol) return '<ol>' + p.ol.map(x => `<li>${md(x)}</li>`).join('') + '</ol>';
    if (p.dl) return '<dl>' + p.dl.map(([t, d]) => `<dt>${md(t)}</dt><dd>${md(d)}</dd>`).join('') + '</dl>';
    return '';
  }).join('');
}

// ---- the broken axis ----
const W = 1000, H = 230, AY = 150;
const SEG = { deep:[24, 84], early:[134, 324], mid:[374, 644], story:[694, 980] };
const RANGE = Object.fromEntries(D.segments.map(s => [s.key, s]));
function xOf(m) {
  const e = ERA[m.era], seg = SEG[e.seg], r = RANGE[e.seg];
  if (e.seg === 'deep') return (seg[0] + seg[1]) / 2;
  return seg[0] + (m.sort - r.a) / (r.b - r.a) * (seg[1] - seg[0]);
}

function drawAxis() {
  const vis = new Set(visible());
  let s = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The Expanse on a broken time axis in four segments">`;
  // segment titles and axis pieces
  for (const g of D.segments) {
    const [a, b] = SEG[g.key];
    s += `<text x="${(a + b) / 2}" y="22" text-anchor="middle" font-size="11.5" fill="#9a9a9a" letter-spacing=".04em">${esc(g.label)}</text>`;
    s += `<line x1="${a - 8}" y1="${AY}" x2="${b + 8}" y2="${AY}" stroke="#555" stroke-width="1.5"/>`;
  }
  // breaks between segments
  const breaks = [[109, 'about 2 billion years'], [349, '63 years'], [669, 'zoom ×12']];
  for (const [x, t] of breaks) {
    s += `<line x1="${x - 7}" y1="${AY + 9}" x2="${x - 1}" y2="${AY - 9}" stroke="#777" stroke-width="1.5"/>`;
    s += `<line x1="${x + 1}" y1="${AY + 9}" x2="${x + 7}" y2="${AY - 9}" stroke="#777" stroke-width="1.5"/>`;
    s += `<text x="${x}" y="${AY + 58}" text-anchor="middle" font-size="10.5" fill="#6f6f6f">${t}</text>`;
  }
  // era bands, labels on up to two rows so they never collide
  const rows = [[], []];
  for (const e of D.eras) {
    const xs = D.milestones.filter(m => m.era === e.key).map(xOf);
    let a = Math.min(...xs) - 12, b = Math.max(...xs) + 12;
    if (e.seg === 'deep') { a = SEG.deep[0]; b = SEG.deep[1]; }
    s += `<rect x="${a}" y="52" width="${b - a}" height="${AY - 40}" rx="4" fill="${D.eras.indexOf(e) % 2 ? '#151a20' : '#12161b'}"/>`;
    const w = e.name.length * 6.2, cx = (a + b) / 2;
    let row = rows.findIndex(r => r.every(([l, rr]) => cx - w / 2 > rr + 6 || cx + w / 2 < l - 6));
    if (row < 0) row = 1;
    rows[row].push([cx - w / 2, cx + w / 2]);
    s += `<text x="${cx}" y="${row ? 64 : 44}" text-anchor="middle" font-size="11" fill="#b9c3cf">${esc(e.name)}</text>`;
    if (row) s += '';
    else s += `<line x1="${cx}" y1="48" x2="${cx}" y2="52" stroke="#3a4450"/>`;
  }
  // milestones: stack markers that sit within 14px of each other
  const placed = [];
  const yearRows = [[], [], []];
  D.milestones.forEach((m, i) => {
    if (!vis.has(i)) return;
    const x = xOf(m);
    let lvl = 0;
    while (placed.some(p => Math.abs(p.x - x) < 14 && p.lvl === lvl)) lvl++;
    placed.push({ x, lvl });
    const y = AY - lvl * 18;
    const yr = m.sort < 0 ? '2 bn years ago' : String(m.sort);
    const w = yr.length * 6.3;
    let r = yearRows.findIndex(rw => rw.every(([l, rr]) => x - w / 2 > rr + 4 || x + w / 2 < l - 4));
    if (r < 0) r = 2;
    yearRows[r].push([x - w / 2, x + w / 2]);
    const sel_ = i === sel;
    s += `<g class="hit" data-i="${i}" tabindex="0" role="button" aria-label="${esc(m.year + ': ' + plain(m.label))}">`;
    s += `<circle class="focus" cx="${x}" cy="${y}" r="12" fill="transparent"/>`;
    if (sel_) s += `<circle cx="${x}" cy="${y}" r="10.5" fill="none" stroke="#e6e6e6" stroke-width="1.6"/>`;
    s += markerSVG(m.source, 6, x, y);
    s += `<text x="${x}" y="${AY + 20 + r * 13}" text-anchor="middle" font-size="11" fill="${sel_ ? '#e6e6e6' : '#8a8a8a'}" font-variant-numeric="tabular-nums">${yr}</text>`;
    s += `</g>`;
  });
  return s + '</svg>';
}

// ---- card, era panel ----
function drawCard() {
  const el = document.getElementById('card');
  if (sel < 0) { el.innerHTML = '<div class="lbl">Every source type is filtered out.</div>'; return; }
  const m = D.milestones[sel], e = ERA[m.era];
  el.innerHTML = `<div class="era">${md(e.name)} &middot; ${esc(e.span)}</div>
    <div class="yr">${esc(m.year)}</div><div class="lbl">${md(m.label)}</div>
    ${badge(m.source)}${m.note ? `<div class="note">${md(m.note)}</div>` : '<div class="note"></div>'}
    <div class="body">${body(m.body)}</div>`;
}
function eraExtras(e) {
  let h = body(e.text.slice(0, 1));
  if (e.extra === 'powers') h += powersHTML();
  if (e.extra === 'transfer') h += xferHTML();
  h += body(e.text.slice(1));
  return h;
}
function drawEra() {
  const el = document.getElementById('eraPanel');
  const e = sel >= 0 ? ERA[D.milestones[sel].era] : null;
  if (!e || (!e.text.length && !e.extra)) { el.hidden = true; el.innerHTML = ''; return; }
  el.hidden = false;
  el.innerHTML = `<h2>${md(e.title)}</h2><p class="span">${esc(e.span)}</p>${eraExtras(e)}`;
  startXfer();
}
function powersHTML() {
  return '<div class="powers">' + D.powers.map(([n, w, l, k]) =>
    `<div class="power"><h3>${esc(n)}</h3><dl><dt>What it is</dt><dd>${esc(w)}</dd>
     <dt>Leverage</dt><dd>${esc(l)}</dd><dt>Weakness</dt><dd>${esc(k)}</dd></dl></div>`).join('') + '</div>';
}

// ---- Hohmann against brachistochrone ----
const HOH_DAYS = D.physics.hohmann_days, BR_DAYS = D.physics.brach_days;
function xferHTML() {
  return `<div class="xfer">
   <figure><svg viewBox="0 0 300 200" class="xf" data-k="h" aria-label="A Hohmann transfer from Earth's orbit to Mars's orbit">
     <circle cx="150" cy="118" r="5" fill="#f0c060"/>
     <circle cx="150" cy="118" r="50" fill="none" stroke="#3a4450" stroke-dasharray="3 3"/>
     <circle cx="150" cy="118" r="76" fill="none" stroke="#3a4450" stroke-dasharray="3 3"/>
     <path class="traj" fill="none" stroke="#5a6472" stroke-width="1.4"/>
     <g class="ship"><path class="flame" d="M-10,0 L-16,-3 L-16,3 Z" fill="#f09b28"/><path d="M-9,-4 L7,0 L-9,4 Z" fill="#e6e6e6"/></g>
     <text x="8" y="18" font-size="12" fill="#e6e6e6" font-weight="600">Before Epstein</text>
     <text class="clock" x="8" y="34" font-size="11.5" fill="#9a9a9a"></text>
     <text class="state" x="8" y="192" font-size="11.5" fill="#9a9a9a"></text>
   </svg><figcaption>Hohmann transfer, Earth to Mars: two short burns and about ${HOH_DAYS} days of coasting in freefall.</figcaption></figure>
   <figure><svg viewBox="0 0 300 200" class="xf" data-k="b" aria-label="A brachistochrone: accelerate to the midpoint, flip, decelerate">
     <circle cx="34" cy="118" r="7" fill="#3987e5"/><text x="34" y="144" text-anchor="middle" font-size="11" fill="#9a9a9a">Earth</text>
     <circle cx="266" cy="118" r="6" fill="#c0603a"/><text x="266" y="144" text-anchor="middle" font-size="11" fill="#9a9a9a">Mars</text>
     <line x1="44" y1="118" x2="256" y2="118" stroke="#5a6472" stroke-width="1.4" stroke-dasharray="4 3"/>
     <line x1="150" y1="104" x2="150" y2="132" stroke="#3a4450"/><text x="150" y="98" text-anchor="middle" font-size="10.5" fill="#6f6f6f">flip</text>
     <g class="ship"><path class="flame" d="M-10,0 L-16,-3 L-16,3 Z" fill="#f09b28"/><path d="M-9,-4 L7,0 L-9,4 Z" fill="#e6e6e6"/></g>
     <text x="8" y="18" font-size="12" fill="#e6e6e6" font-weight="600">Epstein Drive</text>
     <text class="clock" x="8" y="34" font-size="11.5" fill="#9a9a9a"></text>
     <text class="state" x="8" y="192" font-size="11.5" fill="#9a9a9a"></text>
   </svg><figcaption>Brachistochrone across half an AU at a third of a g: about ${BR_DAYS} days, with thrust gravity the whole way but the flip.</figcaption></figure>
  </div>`;
}
// Hohmann: the upper half of the transfer ellipse, timed by Kepler's equation
const R1 = 50, R2 = 76, A = (R1 + R2) / 2, E = (R2 - R1) / (R2 + R1), B = A * Math.sqrt(1 - E * E);
function hohPos(t) {                       // t in [0,1] over the half orbit
  const Mn = Math.PI * t; let En = Mn;
  for (let k = 0; k < 8; k++) En -= (En - E * Math.sin(En) - Mn) / (1 - E * Math.cos(En));
  const x = A * (Math.cos(En) - E), y = B * Math.sin(En);  // focus at the sun, periapsis at +x
  return [150 - x, 118 + y];                               // start on the left, pass under: counterclockwise, seen from above
}
let raf = 0, t0 = 0;
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
function frame(now, fixed) {
  const t = fixed != null ? fixed : ((now - t0) / 7000) % 1;
  for (const svg of document.querySelectorAll('svg.xf')) {
    const ship = svg.querySelector('.ship'), flame = svg.querySelector('.flame');
    const clock = svg.querySelector('.clock'), state = svg.querySelector('.state');
    if (svg.dataset.k === 'h') {
      const tr = svg.querySelector('.traj');
      if (!tr.getAttribute('d')) {
        let d = ''; for (let i = 0; i <= 60; i++) { const [x, y] = hohPos(i / 60); d += (i ? 'L' : 'M') + x.toFixed(1) + ',' + y.toFixed(1); }
        tr.setAttribute('d', d);
      }
      const [x, y] = hohPos(t), [x2, y2] = hohPos(Math.min(1, t + 0.01));
      const ang = Math.atan2(y2 - y, x2 - x) * 180 / Math.PI;
      ship.setAttribute('transform', `translate(${x},${y}) rotate(${ang})`);
      const burn = t < 0.05 || t > 0.95;
      flame.style.display = burn ? '' : 'none';
      clock.textContent = `day ${Math.round(t * HOH_DAYS)} of ${HOH_DAYS}`;
      state.textContent = burn ? 'burning' : 'coasting, weightless';
    } else {
      const s = t < 0.5 ? 2 * t * t : 1 - 2 * (1 - t) * (1 - t);   // constant thrust, flip at the midpoint
      const x = 44 + s * 212, flip = Math.abs(t - 0.5) < 0.025;
      const ang = t < 0.5 ? 0 : 180;
      ship.setAttribute('transform', `translate(${x},118) rotate(${flip ? 90 : ang})`);
      flame.style.display = flip ? 'none' : '';
      clock.textContent = `day ${(t * BR_DAYS).toFixed(1)} of ${BR_DAYS}`;
      state.textContent = flip ? 'flip' : (t < 0.5 ? 'accelerating, a third of a g' : 'decelerating, a third of a g');
    }
  }
  if (fixed == null) raf = requestAnimationFrame(frame);
}
function startXfer() {
  cancelAnimationFrame(raf);
  if (!document.querySelector('svg.xf')) return;
  if (REDUCED) { frame(0, 0.35); return; }
  t0 = performance.now(); raf = requestAnimationFrame(frame);
}

// ---- the gap bar ----
function drawGaps() {
  const G = D.gaps, tot = G.reduce((a, g) => a + (g[1] - g[0]), 0);
  const X0 = 10, WW = 960; let x = X0, s = `<svg viewBox="0 0 1000 96" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Three intervals: about 160 years, about 140 years, and four years">`;
  const shade = ['#2f3a47', '#3a4756', '#f09b28'];
  G.forEach(([a, b, name], i) => {
    const w = Math.max(3, (b - a) / tot * WW);
    s += `<rect x="${x}" y="30" width="${w - 2}" height="22" rx="3" fill="${shade[i]}"/>`;
    const years = i === 2 ? 'four years' : `about ${Math.round((b - a) / 10) * 10} years`;
    const tx = i === 2 ? x + w - 2 : x + (w - 2) / 2, anchor = i === 2 ? 'end' : 'middle';
    s += `<text x="${tx}" y="${i === 2 ? 72 : 22}" text-anchor="${anchor}" font-size="12" fill="#d4d4d4">${esc(name)}: ${years}</text>`;
    s += `<text x="${x}" y="${i === 2 ? 88 : 68}" font-size="10.5" fill="#7c7c7c" text-anchor="${i === 2 ? 'end' : 'start'}">${i === 2 ? '2350 to 2353' : a}</text>`;
    x += w;
  });
  s += `<text x="${X0 + WW - 4}" y="22" text-anchor="end" font-size="10.5" fill="#7c7c7c"></text>`;
  document.getElementById('gapbar').innerHTML = s + '</svg>';
}

// ---- vertical list for narrow screens ----
let vopen = new Set();
function drawList() {
  const vis = new Set(visible());
  let h = '', lastSeg = null;
  for (const e of D.eras) {
    const items = D.milestones.map((m, i) => [m, i]).filter(([m, i]) => m.era === e.key && vis.has(i));
    if (lastSeg && lastSeg !== e.seg) {
      const t = { early: 'about 2 billion years later', mid: '63 years later', story: 'the scale widens' }[e.seg];
      h += `<div class="vbreak">${t}</div>`;
    }
    lastSeg = e.seg;
    h += `<section class="vera"><h2>${md(e.title)}</h2><p class="span">${esc(e.span)}</p>`;
    for (const [m, i] of items) {
      const open = vopen.has(i);
      h += `<div class="vitem"><button type="button" data-v="${i}" aria-expanded="${open}">
        <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true">${markerSVG(m.source, 6, 8, 9)}</svg>
        <span class="vyr">${esc(m.sort < 0 ? '2 bn years ago' : m.year)}</span><span class="vlbl">${md(m.label)}</span></button>`;
      if (open) h += `<div class="vbody">${badge(m.source)}${m.note ? `<div class="note">${md(m.note)}</div>` : ''}<div class="body">${body(m.body)}</div></div>`;
      h += `</div>`;
    }
    if (!items.length) h += `<p class="span">Every date in this era is filtered out.</p>`;
    if (e.text.length || e.extra) h += `<details><summary>The era</summary><div class="body">${eraExtras(e)}</div></details>`;
    h += `</section>`;
  }
  document.getElementById('vlist').innerHTML = h;
}

// ---- filters ----
function drawFilters() {
  const el = document.getElementById('filters');
  el.querySelectorAll('.src').forEach(b => b.remove());
  for (const s of SRC) {
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'src'; b.dataset.s = s;
    b.setAttribute('aria-pressed', on.has(s));
    b.innerHTML = chip(s) + esc(s);
    el.appendChild(b);
  }
}

function render() {
  const vis = visible();
  if (sel < 0 || !vis.includes(sel)) sel = vis.length ? vis.reduce((a, i) => Math.abs(i - sel) < Math.abs(a - sel) ? i : a, vis[0]) : -1;
  document.getElementById('diagram').innerHTML = drawAxis();
  drawCard(); drawEra(); drawList();
  document.querySelectorAll('.src').forEach(b => b.setAttribute('aria-pressed', on.has(b.dataset.s)));
}

// ---- events ----
const tip = document.getElementById('tip');
document.getElementById('diagram').addEventListener('click', ev => {
  const g = ev.target.closest('.hit'); if (!g) return;
  sel = +g.dataset.i; render();
});
document.getElementById('diagram').addEventListener('keydown', ev => {
  const g = ev.target.closest('.hit'); if (!g) return;
  if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); sel = +g.dataset.i; render();
    document.querySelector(`#diagram .hit[data-i="${sel}"]`).focus(); }
});
document.getElementById('diagram').addEventListener('mousemove', ev => {
  const g = ev.target.closest('.hit');
  if (!g) { tip.style.display = 'none'; return; }
  const m = D.milestones[+g.dataset.i];
  tip.innerHTML = `<b>${esc(m.year)}</b><br>${md(m.label)}<br><span style="color:#9a9a9a">${esc(m.source)}</span>`;
  tip.style.display = 'block';
  tip.style.left = Math.min(ev.clientX + 14, innerWidth - 300) + 'px';
  tip.style.top = (ev.clientY + 14) + 'px';
});
document.getElementById('diagram').addEventListener('mouseleave', () => tip.style.display = 'none');
document.getElementById('filters').addEventListener('click', ev => {
  const b = ev.target.closest('.src'); if (!b) return;
  const s = b.dataset.s; on.has(s) ? on.delete(s) : on.add(s); render();
});
document.getElementById('vlist').addEventListener('click', ev => {
  const b = ev.target.closest('button[data-v]'); if (!b) return;
  const i = +b.dataset.v; vopen.has(i) ? vopen.delete(i) : vopen.add(i); drawList();
  document.querySelector(`#vlist button[data-v="${i}"]`).focus();
});
document.getElementById('vlist').addEventListener('toggle', () => startXfer(), true);

// for the verifier
window.__exp = function (q) {
  q = q || {};
  if (q.pick != null) { sel = q.pick; render(); }
  if (q.only) { on.clear(); q.only.forEach(s => on.add(s)); render(); }
  if (q.all) { SRC.forEach(s => on.add(s)); render(); }
  if (q.toggle) { on.has(q.toggle) ? on.delete(q.toggle) : on.add(q.toggle); render(); }
  const card = document.getElementById('card');
  return { sel, count: D.milestones.length,
    markers: document.querySelectorAll('#diagram .hit').length,
    year: card.querySelector('.yr')?.textContent || '',
    label: card.querySelector('.lbl')?.textContent || '',
    badge: card.querySelector('.badge')?.textContent || '',
    body: card.querySelector('.body')?.textContent || '',
    era: document.getElementById('eraPanel').hidden ? null : document.querySelector('#eraPanel h2')?.textContent,
    powers: document.querySelectorAll('#eraPanel .power').length,
    xfer: document.querySelectorAll('#eraPanel svg.xf').length,
    vitems: document.querySelectorAll('#vlist .vitem').length,
    veras: document.querySelectorAll('#vlist .vera').length,
    pressed: [...document.querySelectorAll('.src')].filter(b => b.getAttribute('aria-pressed') === 'true').map(b => b.dataset.s) };
};

drawFilters(); drawGaps(); render();
"""


def physics():
    """The two numbers the transfer diagram prints, computed rather than typed."""
    import math
    AU, DAY = 1.495978707e11, 86400.0
    GM_SUN = 1.32712440018e20
    a = (1.0 + 1.524) / 2 * AU                       # Earth to Mars transfer ellipse
    hohmann = math.pi * math.sqrt(a ** 3 / GM_SUN) / DAY
    acc, dist = 9.80665 / 3, 0.5 * AU                # a third of a g, half an AU
    brach = 2 * math.sqrt(dist / acc) / DAY
    return {"hohmann_days": round(hohmann), "brach_days": round(brach, 1)}


def payload():
    return {
        "ramp": RAMP,
        "sources": SOURCES,
        "segments": [dict(key=k, label=l, a=a, b=b) for k, l, a, b in SEGMENTS],
        "eras": ERAS, "powers": POWERS, "milestones": MILESTONES,
        "gaps": GAPS, "physics": physics(),
    }


def mdh(s):
    """The same *italics* markup the page script uses, for the static text."""
    import html
    import re
    return re.sub(r"\*([^*]+)\*", r"<i>\1</i>", html.escape(s, quote=False))


def main():
    css = CSS.replace("__APACSS__", apa.CSS)
    html_ = (HTML.replace("__CSS__", css)
                 .replace("__TITLE__", TITLE)
                 .replace("__TAGLINE__", mdh(TAGLINE))
                 .replace("__CLOSING__", mdh(CLOSING))
                 .replace("__INTRO__", "\n".join(f"<p>{mdh(p)}</p>" for p in INTRO))
                 .replace("__METHOD__", METHOD)
                 .replace("__REFS__", REFS)
                 .replace("__DATA__", json.dumps(payload(), ensure_ascii=False))
                 .replace("__SCRIPT__", SCRIPT))
    OUT.write_text(html_, encoding="utf-8")
    p = physics()
    print(f"wrote {OUT.name} ({len(html_):,} B): {len(MILESTONES)} milestones, {len(ERAS)} eras; "
          f"Hohmann {p['hohmann_days']} days, brachistochrone {p['brach_days']} days")


if __name__ == "__main__":
    main()
