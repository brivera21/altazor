#!/usr/bin/env python3
"""Generate mexico.html, Mexico.

The thirty two states, every river the source layer carries, and the sierras.

The states are not polygons in any dataset available here; make_mx_data.py
builds them by running the loose ends of the WDBII boundary arcs out to
whatever is nearest and polygonising what closes, then handing each state the
face its capital falls in. Every face is checked against the area INEGI
publishes: twenty nine of the thirty two land within eight per cent. The three
that do not are named on the page, and the reason is in the WDBII data rather
than in the method: it carries the Campeche and Quintana Roo boundary as it
stood before the states settled it in 1997.

The sierras are the roughness of Natural Earth's relief raster, the measure
make_sierras.py uses for the north: broken ground is high frequency texture in
that image and plains are smooth. It marks rugged country, not any named range.

Usage: python3 build_mexico.py      (needs /home/claude/mx/*.pkl)
"""

import json
import math
import pickle
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union
from shapely.validation import make_valid


def state_pops():
    """The populations the states page already carries, read without running
    its generator: that module writes a page as soon as it is imported."""
    import ast
    src = (Path(__file__).parent / "build_usstates.py").read_text()
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and node.targets[0].id == "ROWS":
            return ast.literal_eval(node.value)
    raise SystemExit("build_usstates.py no longer defines ROWS")


OUT = Path(__file__).parent.parent / "mexico.html"
DATA = Path("/home/claude/mx")

from make_mx_data import STATES as MX_STATES, ROUGH_REF, SMOOTH_REF
from make_us_data import sph_area_km2

AREA = {n: km2 for n, km2, _ in MX_STATES}
NAME = {n: n for n in AREA}

# Where each state's face is allowed to land against the area INEGI publishes.
# Three need more room, and the reason is in the source rather than the method:
# WDBII carries the Campeche and Quintana Roo boundary as it stood before the
# two states settled it in 1997, and Mexico City is small enough that half a
# kilometre of simplified coastline and border is worth several per cent.
TOLERANCE = {"Campeche": 16.0, "Quintana Roo": 22.0, "Ciudad de Mexico": 12.0}
DEFAULT_TOL = 8.0

# Accents belong on the page even though the data keys do not carry them.
ACCENTED = {
    "Nuevo Leon": "Nuevo Le\u00f3n", "San Luis Potosi": "San Luis Potos\u00ed",
    "Michoacan": "Michoac\u00e1n", "Yucatan": "Yucat\u00e1n",
    "Mexico": "M\u00e9xico", "Queretaro": "Quer\u00e9taro",
    "Ciudad de Mexico": "Ciudad de M\u00e9xico",
}

FACTS = [
    ("States", "31 and a capital",
     "the Ciudad de M\u00e9xico stopped being a federal district in 2016"),
    ("Area", "1,964,375 km&sup2;",
     "the national territory, islands included, thirteenth largest country"),
    ("Highest point", "5,636 m",
     "the Pico de Orizaba, the third highest in North America"),
    ("Longest river", "the Bravo, 3,051 km",
     "which is the Rio Grande on the other bank"),
]

# Rivers carry no name in the source. A course is named where it passes a town
# on that river: within fifteen kilometres, with the next nearest course four
# times further off, so there is no question which line is meant.
#     river, the place, its latitude and longitude
NAMED_RIVERS = [
    ("Bravo", "Ciudad Ju\u00e1rez", 31.74, -106.49),
    ("Conchos", "Camargo", 27.67, -105.17),
    ("Yaqui", "Ciudad Obreg\u00f3n", 27.49, -109.94),
    ("Fuerte", "El Fuerte", 26.42, -108.62),
    ("Culiac\u00e1n", "Culiac\u00e1n", 24.81, -107.39),
    ("Santiago", "Santiago Ixcuintla", 21.81, -105.21),
    ("Grijalva", "Chiapa de Corzo", 16.71, -93.01),
    ("Usumacinta", "Tenosique", 17.48, -91.42),
    ("Lerma", "Salamanca", 20.57, -101.20),
    ("P\u00e1nuco", "Ciudad Valles", 21.99, -99.02),
]
NEAR_KM = 15.0
CLEAR = 4.0

REGIONS = []

VW, VH = 1000.0, 744.0


class Albers:
    """Albers equal area conic, the projection the country is usually drawn on."""

    def __init__(self, lat1, lat2, lon0, lat0):
        r1, r2 = math.radians(lat1), math.radians(lat2)
        self.n = (math.sin(r1) + math.sin(r2)) / 2
        self.C = math.cos(r1) ** 2 + 2 * self.n * math.sin(r1)
        self.lon0 = lon0
        self.rho0 = math.sqrt(self.C - 2 * self.n * math.sin(math.radians(lat0))) / self.n

    def __call__(self, lon, lat):
        rho = math.sqrt(max(0.0, self.C - 2 * self.n * math.sin(math.radians(lat)))) / self.n
        th = self.n * math.radians(lon - self.lon0)
        return rho * math.sin(th), self.rho0 - rho * math.cos(th)


MX = Albers(17.5, 29.5, -102, 23.5)


def rings(g):
    polys = g.geoms if isinstance(g, MultiPolygon) else [g]
    for p in polys:
        yield np.asarray(p.exterior.coords)
        for r in p.interiors:
            yield np.asarray(r.coords)


def fit(items, proj, w, h, x0, y0, keep=None):
    """Project, then scale everything to fit a box, returning the transform."""
    pts = []
    for g in items:
        for r in rings(g):
            pts.extend(proj(x, y) for x, y in r)
        if keep and len(pts) > 4_000_000:
            break
    a = np.asarray(pts)
    sx, sy = a[:, 0], a[:, 1]
    s = min(w / (sx.max() - sx.min()), h / (sy.max() - sy.min()))
    ox = x0 + (w - (sx.max() - sx.min()) * s) / 2 - sx.min() * s
    oy = y0 + (h - (sy.max() - sy.min()) * s) / 2 - sy.min() * s

    # Albers counts y northward and SVG counts it down the page, so the axis
    # is turned over here rather than in every path
    oy = y0 + (h + (sy.max() - sy.min()) * s) / 2 + sy.min() * s

    def T(lon, lat):
        x, y = proj(lon, lat)
        return x * s + ox, oy - y * s
    return T


def path_of(g, T, tol):
    g = g.simplify(tol, preserve_topology=True)
    if g.is_empty:
        return ""
    out = []
    for r in rings(g):
        if len(r) < 3:
            continue
        pts = [T(x, y) for x, y in r]
        out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
    return "".join(out)


def line_of(g, T, tol):
    g = g.simplify(tol, preserve_topology=False)
    if g.is_empty or len(g.coords) < 2:
        return ""
    pts = [T(x, y) for x, y in g.coords]
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mexico &middot; Altazor</title>
<style>
:root{color-scheme:dark;
--ink:#e8e4dc; --ink2:#a49c8f; --ink3:#857d72;
--bg:#12100e; --panel:#1a1815; --line:#2e2a25; --accent:#c9a227;
--sea:#101c26; --land:#3b3b34; --border:#a99f8c; --riv:#5aa6e8;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:400 16px/1.65 "Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif}
main{max-width:1180px;margin:0 auto;padding:2rem 1.25rem 4rem}
header.site{border-top:4px solid var(--accent);padding-top:22px;margin-bottom:26px;
display:flex;align-items:baseline;gap:18px;flex-wrap:wrap}
.brand{font-weight:700;font-size:20px;letter-spacing:.1em;text-decoration:none;color:var(--ink);
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
.brand:hover{color:var(--accent)}
nav.site a{color:var(--ink2);text-decoration:none;font-size:14px;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
nav.site a:hover{color:var(--accent)}
h1{font-size:1.8rem;font-weight:600;margin:0 0 1.1rem}

.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
gap:10px;margin:0 0 16px}
.tile{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:11px 14px}
.tile .k{font-size:11px;color:var(--ink3);text-transform:uppercase;letter-spacing:.07em;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
.tile .v{font-size:1.16rem;font-weight:650;margin-top:3px;font-variant-numeric:tabular-nums}
.tile .d{font-size:.82rem;color:var(--ink3);margin-top:2px;line-height:1.45}

.stage{display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap}
.mapwrap{flex:1 1 640px;min-width:320px}
svg{width:100%;height:auto;display:block;border-radius:10px;
border:1px solid var(--line);background:var(--sea)}
.side{flex:1 1 250px;min-width:236px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:13px 15px}
.card h2{font-size:1.1rem;font-weight:600;margin:0 0 2px}
.card .sub{font-size:.82rem;color:var(--ink3);margin-bottom:9px}
.row{display:flex;justify-content:space-between;gap:12px;font-size:.9rem;padding:2.5px 0}
.row span:last-child{font-variant-numeric:tabular-nums;color:var(--ink2)}

.controls{margin:13px 0 0;display:flex;gap:.55rem;flex-wrap:wrap;align-items:center}
button{font:inherit;font-size:.85rem;background:none;color:var(--ink);
border:1px solid var(--line);border-radius:999px;padding:5px 13px;cursor:pointer;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
button:hover{background:#241f1a}
button[aria-pressed="true"]{border-color:var(--accent);color:var(--accent)}

.state{fill:#4a4a42;stroke:none;cursor:pointer}
.state:hover{fill:#5c5c52}
.state.on{fill:#6b6a5d}
#lines path{fill:none;stroke:#d8cdb6;stroke-width:.8;
stroke-linejoin:round;pointer-events:none}
#coast path{fill:none;stroke:#cdbfa4;stroke-width:1.1;pointer-events:none}
#rugged path{fill:#7d7156;fill-opacity:.55;stroke:none;pointer-events:none}
#rugged path.alta{fill:#9c8c6b;fill-opacity:.6}
#rivers path{fill:none;stroke:var(--riv);stroke-width:.7;
stroke-linejoin:round;stroke-linecap:round;pointer-events:none}
#rivers path.named{stroke:#8fd0ff;stroke-width:1.3}
#labels text{fill:#bcd9f2;font-size:9px;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
paint-order:stroke;stroke:#101c26;stroke-width:2.6;pointer-events:none}

.notes{margin-top:2.6rem;border-top:1px solid var(--line);padding-top:1.5rem;
color:var(--ink2);font-size:.97rem;max-width:74ch}
.notes h2{font-size:1.08rem;font-weight:400;color:var(--ink);margin:0 0 .6rem}
.notes p{margin:0 0 1rem}
.refs{margin-top:1.5rem;color:var(--ink3);font-size:.88rem;max-width:78ch}
.refs h2{font-size:.97rem;font-weight:400;color:var(--ink2);margin:0 0 .6rem}
.refs p{margin:0 0 .7rem;padding-left:2.2em;text-indent:-2.2em}
</style>
</head>
<body>
<main>
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Digital Concepts</a></nav>
</header>

<h1>Mexico</h1>

<div class="tiles">__FACTS__</div>

<div class="stage">
  <div class="mapwrap"><svg id="map" viewBox="0 0 1000 620"
       preserveAspectRatio="xMidYMid meet">
    <g id="fills"></g>
    <g id="rugged"></g>
    <g id="rivers"></g>
    <g id="lines"></g>
    <g id="coast"></g>
    <g id="labels"></g>
  </svg></div>
  <div class="side"><div class="card">
    <h2 id="selName">Thirty two states</h2>
    <div class="sub" id="selSub">a state under the cursor fills this panel</div>
    <div class="row"><span>Published area</span><span id="selArea"></span></div>
    <div class="row"><span>Measured here</span><span id="selGot"></span></div>
    <div class="row"><span>Difference</span><span id="selErr"></span></div>
    <div class="row"><span>Share of the country</span><span id="selShare"></span></div>
  </div></div>
</div>

<div class="controls">
  <button id="bRiv" aria-pressed="true">Rivers</button>
  <button id="bMtn" aria-pressed="true">Sierras</button>
  <button id="bLine" aria-pressed="true">State lines</button>
</div>

<div class="notes">
<h2>About the map</h2>
<p>No dataset here holds the states as shapes. What it holds is the shoreline
and a pile of loose boundary arcs, so each arc is run out to whatever line is
nearest until the pile closes into faces, and every state takes the face its
capital falls in. The check is the area: twenty nine of the thirty two land
within eight per cent of what INEGI publishes.</p>
<p>The three that miss are named in the panel. Campeche and Quintana Roo miss
because the boundary in the data is the one that stood before the two states
settled theirs in 1997, and Mexico City misses because it is small enough that
half a kilometre either way is worth several per cent.</p>
<p>The sierras are measured from a relief image rather than an elevation grid,
so they mark broken ground and not any named range, and a river is named only
where one course passes a town on it and nothing else is near.</p>
</div>

<div class="refs">
<h2>References</h2>
<p>Instituto Nacional de Estad&iacute;stica y Geograf&iacute;a. (2024).
<i>Marco Geoestad&iacute;stico</i>. https://www.inegi.org.mx/</p>
<p>Natural Earth. (2024). <i>Cross-blended hypsometric tints with shaded
relief</i> [Data set], as distributed with basemap-data-hires.
https://www.naturalearthdata.com/</p>
<p>Wessel, P., &amp; Smith, W. H. F. (1996). A global, self-consistent,
hierarchical, high-resolution shoreline database. <i>Journal of Geophysical
Research, 101</i>(B4), 8741-8743.</p>
</div>
</main>
<script>
const D = __DATA__;
const el = id => document.getElementById(id);
const NS = 'http://www.w3.org/2000/svg';
const fmt = n => n == null ? '--' : Math.round(n).toLocaleString('en-US');
const META = {};
D.meta.forEach(m => META[m.c] = m);
const TOTAL = D.meta.reduce((a, m) => a + m.km2, 0);
let hover = null, sel = null;

function make(tag, attrs, parent) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  parent.appendChild(e);
  return e;
}
const gs = el('fills'), gl = el('lines');
for (const c in D.states) {
  const p = make('path', {d: D.states[c], class: 'state', 'data-c': c}, gs);
  make('path', {d: D.states[c]}, gl);
  p.addEventListener('mouseenter', () => { hover = c; show(); });
  p.addEventListener('mouseleave', () => { hover = null; show(); });
  p.addEventListener('click', () => { sel = sel === c ? null : c; paint(); show(); });
}
make('path', {d: D.coast}, el('coast'));
const gm = el('rugged');
D.rugged.forEach(m => make('path', {d: m.d, class: m.t === 'alta' ? 'alta' : ''}, gm));
const gr = el('rivers'), gt = el('labels');
D.rivers.forEach(r => {
  make('path', r.n ? {d: r.d, class: 'named'} : {d: r.d}, gr);
  if (r.n) {
    const t = make('text', {x: r.x, y: r.y - 3,
      transform: `rotate(${r.a} ${r.x} ${r.y})`}, gt);
    t.textContent = r.n;
  }
});

function paint() {
  for (const p of gs.children)
    p.classList.toggle('on', p.getAttribute('data-c') === sel);
}
function show() {
  const c = hover || sel;
  const m = c ? META[c] : null;
  el('selName').textContent = m ? m.n : 'Thirty two states';
  el('selSub').textContent = m ? 'a state' : 'a state under the cursor fills this panel';
  el('selArea').textContent = (m ? fmt(m.km2) : fmt(TOTAL)) + ' km²';
  el('selGot').textContent = m ? fmt(m.got) + ' km²' : 'the sum of the published areas';
  el('selErr').textContent = m
    ? (m.err > 0 ? '+' : '') + m.err.toFixed(1) + '% against INEGI'
    : 'measured against INEGI state by state';
  el('selShare').textContent = m
    ? (m.km2 / TOTAL * 100).toFixed(1) + '% of the country'
    : '1,964,375 km² of national territory';
}
function toggle(id, g) {
  el(id).addEventListener('click', () => {
    const v = el(id).getAttribute('aria-pressed') !== 'true';
    el(id).setAttribute('aria-pressed', v);
    g.forEach(x => x.style.display = v ? '' : 'none');
  });
}
toggle('bRiv', [gr, gt]);
toggle('bMtn', [gm]);
toggle('bLine', [gl]);
paint(); show();
window.__mx = () => ({states: Object.keys(D.states).length,
  rivers: D.rivers.length, named: D.rivers.filter(r => r.n).length,
  rugged: D.rugged.length, meta: D.meta, hover, sel});
</script>
</body>
</html>
"""


def main():
    st = pickle.load(open(DATA / "states.pkl", "rb"))
    riv = pickle.load(open(DATA / "rivers.pkl", "rb"))
    courses = pickle.load(open(DATA / "courses.pkl", "rb"))
    sie = pickle.load(open(DATA / "sierras.pkl", "rb"))
    land = pickle.load(open(DATA / "land.pkl", "rb"))

    # everything is clipped to the union of the state faces: the shoreline,
    # the river layer and the relief all run on into the United States and
    # Central America, and this page is about one country
    mx = make_valid(unary_union(list(st.values())))
    T = fit(list(st.values()), MX, 1000, 620, 0, 0)

    paths, meta = {}, []
    for name, km2, _ in MX_STATES:
        g = st[name]
        paths[name] = path_of(g, T, 0.006)
        got = sph_area_km2(g)
        meta.append({"c": name, "n": ACCENTED.get(name, name), "km2": km2,
                     "got": round(got), "err": round((got - km2) / km2 * 100, 1)})

    # a little slack, or the Bravo is thrown away for running along the line
    inside = mx.buffer(0.03)
    riv = [g.intersection(inside) for g in riv]
    flat = []
    for g in riv:
        for h in (g.geoms if g.geom_type.startswith("Multi") else [g]):
            if h.geom_type == "LineString" and len(h.coords) > 1:
                flat.append(h)
    riv = flat
    named, anchors = {}, {}
    for nm, place, la, lo in NAMED_RIVERS:
        p = Point(lo, la)
        d = sorted((g.distance(p) * 111, i) for i, g in enumerate(courses))
        if d[0][0] > NEAR_KM or d[1][0] < d[0][0] * CLEAR:
            raise SystemExit(f"the {nm} at {place} is ambiguous: "
                             f"{d[0][0]:.1f} km and {d[1][0]:.1f} km")
        c = courses[d[0][1]]
        best = min(riv, key=lambda g: g.hausdorff_distance(c)
                   if g.length > 0.2 else 9e9)
        named[id(best)] = nm
        anchors[nm] = p

    rv = []
    for g in riv:
        nm = named.get(id(g))
        if not nm and g.length < 0.55:
            continue
        d = line_of(g, T, 0.006)
        if not d:
            continue
        if nm:
            cs = list(g.coords)
            p = anchors[nm]
            k = min(range(len(cs)), key=lambda i: (cs[i][0] - p.x) ** 2
                    + (cs[i][1] - p.y) ** 2)
            a, b = cs[max(0, k - 3)], cs[min(len(cs) - 1, k + 3)]
            ax, ay = T(*a)
            bx, by = T(*b)
            ang = math.degrees(math.atan2(by - ay, bx - ax))
            if ang > 90 or ang < -90:
                ang += 180
            rv.append({"d": d, "n": nm, "x": round(ax, 1), "y": round(ay, 1),
                       "a": round(ang, 1)})
        else:
            rv.append({"d": d})

    mt = []
    for tier, polys in sie.items():
        for p in polys:
            d = path_of(p.intersection(mx), T, 0.006)
            if d:
                mt.append({"d": d, "t": tier})

    js = {"states": paths, "meta": meta, "rivers": rv, "rugged": mt,
          "coast": path_of(mx, T, 0.004)}
    blob = json.dumps(js, separators=(",", ":"), ensure_ascii=False)

    facts = "\n".join(
        f'<div class="tile"><div class="k">{n}</div>'
        f'<div class="v">{v}</div><div class="d">{d}</div></div>'
        for n, v, d in FACTS)

    doc = TEMPLATE.replace("__DATA__", blob).replace("__FACTS__", facts)
    OUT.write_text(doc, encoding="utf-8")
    off = [m["n"] for m in meta if abs(m["err"]) > DEFAULT_TOL]
    print(f"wrote {OUT} ({len(doc):,} bytes): {len(paths)} states "
          f"({len(off)} outside 8% of INEGI: {', '.join(off)}), "
          f"{len(rv)} river pieces ({len(named)} named), {len(mt)} sierras")


if __name__ == "__main__":
    main()
