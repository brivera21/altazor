#!/usr/bin/env python3
"""Generate us.html, The United States.

An Albers equal area map of the lower 48, with Alaska and Hawaii in the two
lower corners on their own Albers cones. Equal area is the point: on this
projection Texas is to Montana as it is on the ground, which a Mercator map
gets badly wrong the further north it goes. The three frames do not share a
scale, and the page says so.

Four layers over the states:

  rivers          WDBII at full resolution, clipped to the country. The layer
                  carries no names, so a river is named only where one course in
                  the layer passes within fifteen kilometres of a town on that
                  river and the next course is four times further off;
                  verify_us.py redoes that test.
  rugged ground   the local roughness of Natural Earth's relief raster, the
                  method make_sierras.py uses for northern Mexico. It is a
                  measure of broken country, not a published boundary of any
                  named range.
  the five broad regions, as outlines rather than fills, because they overlap
                  and no line between them is official. Two of the five are the
                  Census Bureau's own regions and can be cited; the other three
                  are vernacular and the page says which is which.

Usage: python3 build_us.py      (needs /home/claude/us/*.pkl)
"""

import json
import math
import pickle
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union


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


OUT = Path(__file__).parent.parent / "us.html"
DATA = Path("/home/claude/us")

# Land and water area, km2, US Census Bureau 2020 gazetteer state totals.
AREA = {
    "AK": 1723337, "TX": 695662, "CA": 423967, "MT": 380831, "NM": 314917,
    "AZ": 295234, "NV": 286380, "CO": 269601, "OR": 254799, "WY": 253335,
    "MI": 250487, "MN": 225163, "UT": 219882, "ID": 216443, "KS": 213100,
    "NE": 200330, "SD": 199729, "WA": 184661, "ND": 183108, "OK": 181037,
    "MO": 180540, "FL": 170312, "WI": 169635, "GA": 153910, "IL": 149995,
    "IA": 145746, "NY": 141297, "NC": 139391, "AR": 137732, "AL": 135767,
    "LA": 135659, "MS": 125438, "PA": 119280, "OH": 116098, "VA": 110787,
    "TN": 109153, "KY": 104656, "IN": 94326, "ME": 91633, "SC": 82933,
    "WV": 62756, "MD": 32131, "HI": 28313, "MA": 27336, "VT": 24906,
    "NH": 24214, "NJ": 22591, "CT": 14357, "DE": 6446, "RI": 4001,
    "DC": 177,
}
NAME = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida",
    "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky",
    "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
    "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming",
}

# Two of these are the Census Bureau's own regions, from its regions and
# divisions of the United States. The other three are vernacular: they have no
# official boundary, they overlap the Census regions and each other, and where
# they stop is a matter of who is asked. The page says which is which.
# The Census Bureau's own four regions and nine divisions, typed from its
# regions and divisions document. Every state and the district belongs to
# exactly one of each, so these are drawn as fills.
#
# Colour carries the region and lightness carries the division inside it, and
# every area is also written on the map, which is what keeps the four hues
# apart for a reader who cannot separate them by colour alone.
CENSUS_REGIONS = [
    ("Northeast", "#3692ca", "ME NH VT MA RI CT NY NJ PA"),
    ("Midwest", "#bd7634", "OH IN IL MI WI MN IA MO ND SD NE KS"),
    ("South", "#b16dac",
     "DE MD DC VA WV NC SC GA FL KY TN AL MS AR LA OK TX"),
    ("West", "#4d9d61", "MT ID WY CO NM AZ UT NV WA OR CA AK HI"),
]

CENSUS_DIVISIONS = [
    ("New England", "Northeast", "#6dbbef", "ME NH VT MA RI CT"),
    ("Middle Atlantic", "Northeast", "#006aa0", "NY NJ PA"),
    ("East North Central", "Midwest", "#e3a068", "OH IN IL MI WI"),
    ("West North Central", "Midwest", "#934f00", "MN IA MO ND SD NE KS"),
    ("South Atlantic", "South", "#d898d2", "DE MD DC VA WV NC SC GA FL"),
    ("East South Central", "South", "#b16dac", "KY TN AL MS"),
    ("West South Central", "South", "#884784", "AR LA OK TX"),
    ("Mountain", "West", "#7dc48c", "MT ID WY CO NM AZ UT NV"),
    ("Pacific", "West", "#21753c", "WA OR CA AK HI"),
]

# The vernacular areas have no official line, they overlap each other and the
# Census regions, and where they stop depends on who is asked. They stay as
# outlines for that reason.
VERNACULAR = [
    ("East Coast", "#dbe6f0", "the states with an Atlantic shoreline",
     "ME NH MA RI CT NY NJ DE MD VA NC SC GA FL"),
    ("West Coast", "#c9dfd0", "the three states on the Pacific",
     "CA OR WA"),
    ("The Northwest", "#e6ddc9", "the Pacific Northwest as it is usually drawn",
     "WA OR ID"),
]


# The seat of each state's government. Forty nine of the fifty one are
# confirmed against GeoNames at build time, by name and by state. Pierre and
# Montpelier are not in that dataset at all: it carries places over fifteen
# thousand people and those two are the smallest capitals in the country, so
# their coordinates are given here and verify_us.py says which two they are.
CAPITALS = {
    "AL": "Montgomery", "AK": "Juneau", "AZ": "Phoenix", "AR": "Little Rock",
    "CA": "Sacramento", "CO": "Denver", "CT": "Hartford", "DE": "Dover",
    "FL": "Tallahassee", "GA": "Atlanta", "HI": "Honolulu", "ID": "Boise",
    "IL": "Springfield", "IN": "Indianapolis", "IA": "Des Moines",
    "KS": "Topeka", "KY": "Frankfort", "LA": "Baton Rouge", "ME": "Augusta",
    "MD": "Annapolis", "MA": "Boston", "MI": "Lansing", "MN": "Saint Paul",
    "MS": "Jackson", "MO": "Jefferson City", "MT": "Helena", "NE": "Lincoln",
    "NV": "Carson City", "NH": "Concord", "NJ": "Trenton", "NM": "Santa Fe",
    "NY": "Albany", "NC": "Raleigh", "ND": "Bismarck", "OH": "Columbus",
    "OK": "Oklahoma City", "OR": "Salem", "PA": "Harrisburg",
    "RI": "Providence", "SC": "Columbia", "SD": "Pierre", "TN": "Nashville",
    "TX": "Austin", "UT": "Salt Lake City", "VT": "Montpelier",
    "VA": "Richmond", "WA": "Olympia", "WV": "Charleston", "WI": "Madison",
    "WY": "Cheyenne", "DC": "Washington",
}
OFF_THE_LIST = {"SD": (44.3683, -100.3510), "VT": (44.2601, -72.5754)}


def capital_places():
    """Name and position of every capital, checked against GeoNames."""
    import geonamescache
    gc = geonamescache.GeonamesCache()
    us = [c for c in gc.get_cities().values() if c["countrycode"] == "US"]
    out, off = {}, []
    for code, name in CAPITALS.items():
        hit = [c for c in us if c["admin1code"] == code
               and c["name"].lower() == name.lower()]
        if hit:
            c = max(hit, key=lambda c: c["population"])
            out[code] = (name, round(c["latitude"], 4), round(c["longitude"], 4))
        elif code in OFF_THE_LIST:
            out[code] = (name, ) + OFF_THE_LIST[code]
            off.append(name)
        else:
            raise SystemExit(f"{name} does not resolve in {code}")
    print(f"capitals: {len(out) - len(off)} confirmed against GeoNames, "
          f"{len(off)} too small for that dataset ({', '.join(off)})")
    return out

FACTS = [
    ("States", "50 and a district", "and five inhabited territories besides"),
    ("Area", "9,833,520 km&sup2;", "land and inland water, third or fourth "
     "largest depending on how China's borders are counted"),
    ("Highest and lowest", "6,190 m and &minus;86 m",
     "Denali in Alaska, and Badwater Basin in Death Valley"),
    ("Longest river", "the Missouri, 3,767 km",
     "and the Mississippi it joins is only a kilometre shorter"),
]

# Rivers carry no name in the source. A course is labelled where it passes a
# named place on that river: within fifteen kilometres of it, and with the next
# nearest course at least four times further off, so there is no question which
# line is meant. Confluences fail that test and are left unlabelled, which is
# why the Mississippi is named at Memphis and not at Vicksburg.
#     river, the place, its latitude and longitude
NAMED_RIVERS = [
    ("Mississippi", "Memphis", 35.12, -90.05),
    ("Missouri", "Great Falls", 47.50, -111.29),
    ("Ohio", "Louisville", 38.26, -85.76),
    ("Rio Grande", "Albuquerque", 35.10, -106.65),
    ("Colorado", "Moab", 38.57, -109.55),
    ("Columbia", "The Dalles", 45.60, -121.18),
    ("Snake", "Twin Falls", 42.56, -114.47),
    ("Arkansas", "Wichita", 37.69, -97.34),
    ("Tennessee", "Knoxville", 35.96, -83.92),
    ("Red", "Shreveport", 32.51, -93.75),
    ("Platte", "North Platte", 41.13, -100.77),
    ("Hudson", "Albany", 42.65, -73.75),
    ("Sacramento", "Sacramento", 38.58, -121.49),
    ("Yukon", "Galena", 64.73, -156.93),
]
NEAR_KM = 15.0        # how close the course has to pass the place
CLEAR = 4.0           # and how much further off the next course has to be

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


CONUS = Albers(29.5, 45.5, -96, 37.5)
AK = Albers(55, 65, -154, 50)
HI = Albers(8, 18, -157, 13)


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
<title>The United States &middot; Altazor</title>
<style>
:root{color-scheme:dark;
--ink:#e6e6e6; --ink2:#9aa3ad; --ink3:#7d848c;
--bg:#121212; --panel:#171a1d; --line:#2b2f34; --accent:#58a6ff;
--sea:#0d1a26; --land:#39424c; --border:#7d8894; --riv:#5aa6e8;}
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
.mapwrap{flex:1 1 660px;min-width:320px}
svg{width:100%;height:auto;display:block;border-radius:10px;
border:1px solid var(--line);background:var(--sea)}
.side{flex:1 1 250px;min-width:236px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:13px 15px}
.card h2{font-size:1.05rem;font-weight:600;margin:0 0 2px}
.card .sub{font-size:.8rem;color:var(--ink3);margin-bottom:9px}
.row{display:flex;justify-content:space-between;gap:12px;font-size:.87rem;padding:2.5px 0}
.row span:last-child{font-variant-numeric:tabular-nums;color:var(--ink2)}
.inreg{margin-top:9px;font-size:.82rem;color:var(--ink2);line-height:1.5}
.inreg b{color:var(--ink);font-weight:600}

.controls{margin:13px 0 0;display:flex;gap:.55rem;flex-wrap:wrap;align-items:center}
button{font:inherit;font-size:.85rem;background:none;color:var(--ink);
border:1px solid var(--line);border-radius:999px;padding:5px 13px;cursor:pointer}
button:hover{background:#20242a}
button[aria-pressed="true"]{border-color:var(--accent);color:var(--accent)}
.lg{display:inline-flex;align-items:center;gap:7px}
.lg .sw{width:22px;height:3px;border-radius:2px;display:inline-block}
.lg[aria-pressed="false"] .sw{opacity:.25}
.sep{width:1px;height:20px;background:var(--line);margin:0 .3rem}

.state{fill:var(--tint,var(--land));stroke:none;cursor:pointer}
.state:hover{fill:#4c5763}
.state.on{fill:#5b6774}
#lines path{fill:none;stroke:#9aa7b4;stroke-width:.8;
stroke-linejoin:round;pointer-events:none}
#capital circle{fill:#f2c66b;stroke:#0d1a26;stroke-width:1.2;pointer-events:none}
#capital text{fill:#f7dfa8;font-size:10px;font-family:inherit;
paint-order:stroke;stroke:#0d1a26;stroke-width:2.6;pointer-events:none}
/* neighbouring fills leave an anti-aliased hairline where they meet, which
   reads as a ghost of the border; stroking each in its own colour closes it */
svg.bare .state{stroke:var(--land);stroke-width:.9}
svg.bare .state:hover{fill:var(--land)}
svg.bare .state.on{fill:var(--land)}
#labels text{fill:#bcd9f2;font-size:9px;font-family:inherit;
paint-order:stroke;stroke:#0d1a26;stroke-width:2.6;pointer-events:none}
/* over a coloured region the rugged ground reads as texture, not as its own
   layer, so it goes translucent; with the lines off it is the map again */
#rugged path{fill:#6d6455;fill-opacity:.42;stroke:none;pointer-events:none}
#rugged path.high{fill:#8a7c66;fill-opacity:.5}
svg.bare #rugged path{fill-opacity:1}
#rivers path{fill:none;stroke:var(--riv);stroke-width:.7;
stroke-linejoin:round;stroke-linecap:round;pointer-events:none}
#rivers path.named{stroke:#8fd0ff;stroke-width:1.25}
#regions path{fill:none;stroke-width:2.2;stroke-linejoin:round;
pointer-events:none;paint-order:stroke}
#areas text{font-size:11px;font-family:inherit;letter-spacing:.06em;
text-transform:uppercase;text-anchor:middle;pointer-events:none;
paint-order:stroke;stroke:#0d1a26;stroke-width:3;fill:#e8eef5}
.lg .sw{width:22px;height:3px;border-radius:2px;display:inline-block}
.lg.fill .sw{height:11px;border-radius:3px}
.inset{fill:none;stroke:var(--line);stroke-width:1;stroke-dasharray:3 4}
.ilbl{fill:var(--ink3);font-size:11px;font-family:inherit}

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

<h1>The United States</h1>

<div class="tiles">__FACTS__</div>

<div class="stage">
  <div class="mapwrap"><svg id="map" viewBox="0 0 1000 744"
       preserveAspectRatio="xMidYMid meet">
    <g id="fills"></g>
    <g id="rugged"></g>
    <g id="rivers"></g>
    <g id="lines"></g>
    <g id="labels"></g>
    <g id="regions"></g>
    <g id="areas"></g>
    <g id="capital"></g>
    <g id="frames"></g>
  </svg></div>
  <div class="side"><div class="card">
    <h2 id="selName">The lower 48, Alaska and Hawaii</h2>
    <div class="sub" id="selSub">a state under the cursor fills this panel</div>
    <div class="row"><span>Area</span><span id="selArea"></span></div>
    <div class="row"><span>Population</span><span id="selPop"></span></div>
    <div class="row"><span>Share of the country</span><span id="selShare"></span></div>
    <div class="inreg" id="selRegions"></div>
  </div></div>
</div>

<div class="controls">
  <button id="mReg" aria-pressed="true">Census regions</button>
  <button id="mDiv" aria-pressed="false">Census divisions</button>
  <button id="mVer" aria-pressed="false">Vernacular</button>
  <span class="sep"></span>
  <button id="bRiv" aria-pressed="true">Rivers</button>
  <button id="bMtn" aria-pressed="true">Rugged ground</button>
  <button id="bLine" aria-pressed="true">State lines</button>
</div>

<div class="controls" id="legend"></div>

<div class="notes">
<h2>About the map</h2>
<p>The projection is Albers equal area, the one the country is usually drawn
on, so a state covers the share of the page it covers of the ground. Alaska and
Hawaii sit in the corners on cones of their own and at their own scales: Alaska
is a fifth of the country and reaches further west than Hawaii, and drawing all
three to one scale leaves the lower 48 too small to read.</p>
<p>The Census Bureau sorts every state and the district into one of four
regions and one of nine divisions inside them, so both are drawn as fills:
colour for the region, lightness for the division, the name written across the
states. East Coast, West Coast and the Northwest have no official line and
stay as outlines.</p>
<p>Rugged ground comes from a relief image, not an elevation grid, so it marks
broken country rather than any named range, and a river is named only where one
course passes a town on it and nothing else is near. With the lines off, what
is left is the ground.</p>
</div>

<div class="refs">
<h2>References</h2>
<p>United States Census Bureau. (2021). <i>2020 census state population totals
and 2020 gazetteer files</i>. https://www.census.gov/</p>
<p>United States Census Bureau. (2024). <i>Census regions and divisions of the
United States</i>. https://www2.census.gov/geo/pdfs/maps-data/maps/reference/us_regdiv.pdf</p>
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
const fmt = n => n == null ? '--' : n.toLocaleString('en-US');
const META = {};
D.meta.forEach(m => META[m.c] = m);
const TOTAL_KM2 = D.meta.reduce((a, m) => a + (m.km2 || 0), 0);
const TOTAL_POP = D.meta.reduce((a, m) => a + (m.pop || 0), 0);

let hover = null, sel = null;
const GRUPOS = {reg: D.regions, div: D.divisions, vern: D.vern};
let modo = 'reg';
let on = GRUPOS[modo].map(() => true);

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
  p.addEventListener('click', () => { sel = sel === c ? null : c; legend(); paint(); show(); });
}
const gm = el('rugged');
D.rugged.forEach(m => make('path', {d: m.d, class: m.t === 'high' ? 'high' : ''}, gm));
const gr = el('rivers');
const gt = el('labels');
D.rivers.forEach(r => {
  make('path', r.n ? {d: r.d, class: 'named'} : {d: r.d}, gr);
  if (r.n) {
    const t = make('text', {x: r.x, y: r.y - 3,
      transform: `rotate(${r.a} ${r.x} ${r.y})`}, gt);
    t.textContent = r.n;
  }
});
const gg = el('regions');
const vernEls = D.vern.map(r => make('path', {d: r.d, stroke: r.c}, gg));
const ga = el('areas');

// the two insets are on their own scales, so they are boxed and labelled
for (const [x, y, w, h, t] of [[6, 514, 338, 226, 'Alaska'],
                               [726, 606, 214, 116, 'Hawaii']]) {
  make('rect', {x, y, width: w, height: h, rx: 6, class: 'inset'}, el('frames'));
  const l = make('text', {x: x + 6, y: y + 14, class: 'ilbl'}, el('frames'));
  l.textContent = t + (t === 'Hawaii' ? ', the eight main islands, ' : ', ')
    + 'not to the same scale';
}

// Every state carries the colour of the group it belongs to, and the name of
// the group is written on the map: the colour says which one, the writing says
// which one it is.
function paint() {
  const grupo = GRUPOS[modo];
  const color = {};
  grupo.forEach((r, i) => { if (on[i]) r.codes.forEach(c => color[c] = r.c); });
  for (const p of gs.children) {
    p.classList.toggle('on', p.getAttribute('data-c') === sel);
    const c = color[p.getAttribute('data-c')];
    if (c && modo !== 'vern' && lines) p.style.setProperty('--tint', c);
    else p.style.removeProperty('--tint');
  }
  vernEls.forEach((e, i) =>
    e.style.display = (modo === 'vern' && on[i] && lines) ? '' : 'none');
  while (ga.firstChild) ga.removeChild(ga.firstChild);
  if (modo === 'vern' || !lines) return;
  grupo.forEach((r, i) => {
    if (!on[i] || !r.lab) return;
    const t = make('text', {x: r.lab[0], y: r.lab[1]}, ga);
    t.textContent = r.n;
  });
}

function legend() {
  const box = el('legend');
  box.innerHTML = '';
  GRUPOS[modo].forEach((r, i) => {
    const b = document.createElement('button');
    b.className = 'lg' + (modo === 'vern' ? '' : ' fill');
    b.setAttribute('aria-pressed', on[i]);
    b.title = r.note;
    b.innerHTML = `<span class="sw" style="background:${r.c}"></span>${r.n}`;
    b.addEventListener('click', () => {
      on[i] = !on[i];
      b.setAttribute('aria-pressed', on[i]);
      if (!lines) setLines(true);   // an area asked for is an area shown
      paint();
    });
    box.appendChild(b);
  });
}

function setModo(m) {
  modo = m;
  on = GRUPOS[m].map(() => true);
  for (const [id, k] of [['mReg', 'reg'], ['mDiv', 'div'], ['mVer', 'vern']])
    el(id).setAttribute('aria-pressed', k === m);
  if (!lines) setLines(true);
  legend();
  paint();
  show();
}
el('mReg').addEventListener('click', () => setModo('reg'));
el('mDiv').addEventListener('click', () => setModo('div'));
el('mVer').addEventListener('click', () => setModo('vern'));

const gcap = el('capital');
function markCapital(m) {
  while (gcap.firstChild) gcap.removeChild(gcap.firstChild);
  if (!m) return;
  make('circle', {cx: m.cx, cy: m.cy, r: 3.4}, gcap);
  const right = m.cx < 820;
  const t = make('text', {x: m.cx + (right ? 7 : -7), y: m.cy + 3.4,
    'text-anchor': right ? 'start' : 'end'}, gcap);
  t.textContent = m.cap;
}

function show() {
  const c = hover || sel;
  const m = c ? META[c] : null;
  markCapital(m);
  el('selName').textContent = m ? m.n : 'The lower 48, Alaska and Hawaii';
  el('selSub').textContent = m
    ? (m.c === 'DC' ? 'the national capital' : 'capital: ' + m.cap)
    : 'capital: Washington, DC';
  el('selArea').textContent = (m ? fmt(m.km2) : fmt(TOTAL_KM2)) + ' km²';
  el('selPop').textContent = m ? fmt(m.pop) : fmt(TOTAL_POP);
  el('selShare').textContent = m
    ? (m.km2 / TOTAL_KM2 * 100).toFixed(1) + '% of the area'
    : 'the fifty states and the district';
  if (!m) {
    el('selRegions').innerHTML = GRUPOS[modo].map(r =>
      `<b>${r.n}</b>: ${r.note}`).join('<br>');
    return;
  }
  const vern = D.vern.filter(r => r.codes.includes(c)).map(r => r.n);
  el('selRegions').innerHTML =
    `Census region <b>${m.reg}</b>, division <b>${m.div}</b>`
    + (vern.length ? '<br>Also called ' + vern.join(', ') : '');
}

el('bRiv').addEventListener('click', () => {
  const v = el('bRiv').getAttribute('aria-pressed') !== 'true';
  el('bRiv').setAttribute('aria-pressed', v);
  gr.style.display = v ? '' : 'none';
  gt.style.display = v ? '' : 'none';
});
el('bMtn').addEventListener('click', () => {
  const v = el('bMtn').getAttribute('aria-pressed') !== 'true';
  el('bMtn').setAttribute('aria-pressed', v);
  gm.style.display = v ? '' : 'none';
});
// With the state lines off the regions go too, since they are made of states,
// and the hover stops lighting one state up: the point is to see the country
// as ground rather than as fifty shapes.
let lines = true;
function setLines(v) {
  lines = v;
  el('bLine').setAttribute('aria-pressed', v);
  gl.style.display = v ? '' : 'none';
  gg.style.display = v ? '' : 'none';
  document.getElementById('map').classList.toggle('bare', !v);
  paint();               // sin líneas tampoco hay colores de región
}
el('bLine').addEventListener('click', () => setLines(!lines));

legend(); paint(); show();
window.__us = () => ({states: Object.keys(D.states).length, lines,
  capital: gcap.querySelector('text') ? gcap.querySelector('text').textContent : null,
  rivers: D.rivers.length, named: D.rivers.filter(r => r.n).length,
  rugged: D.rugged.length, modo,
  grupos: GRUPOS[modo].map(r => r.n),
  areas: document.querySelectorAll('#areas text').length,
  tinte: (c) => {const p = gs.querySelector(`path[data-c="${c}"]`);
    return p ? p.style.getPropertyValue('--tint') : null;},
  totalKm2: TOTAL_KM2, hover, sel, on: on.slice()});
</script>
</body>
</html>
"""


def main():
    st = pickle.load(open(DATA / "states.pkl", "rb"))
    riv = pickle.load(open(DATA / "rivers.pkl", "rb"))
    rug = pickle.load(open(DATA / "rugged.pkl", "rb"))
    pops = {n: (a, b) for n, _, a, b in state_pops()}
    caps = capital_places()

    lower = {k: g for k, g in st.items() if k not in ("AK", "HI", "PR")}
    # the lower 48 fill the frame; the two insets sit in the corners below it
    Tc = fit(lower.values(), CONUS, 1000, 600, 0, 0)
    Ta = fit([st["AK"]], AK, 338, 226, 6, 514)
    # Hawaii County reaches out to Midway, 2,400 km past the eight islands
    # everyone means by Hawaii. The inset is the eight, and says so.
    st["HI"] = st["HI"].intersection(box(-160.6, 18.6, -154.6, 22.4))
    Th = fit([st["HI"]], HI, 214, 116, 726, 606)
    WHERE = {"AK": Ta, "HI": Th}

    def T_of(code):
        return WHERE.get(code, Tc)

    paths, meta = {}, []
    for code, g in sorted(st.items()):
        if code == "PR":
            continue
        T = T_of(code)
        tol = 0.004 if code in WHERE else 0.012
        paths[code] = path_of(g, T, tol)
        p = pops.get(NAME.get(code, ""), (None, None))
        cn, cla, clo = caps[code]
        cx, cy = T(clo, cla)
        reg = next(n for n, _c, cs in CENSUS_REGIONS if code in cs.split())
        div = next(n for n, _r, _c, cs in CENSUS_DIVISIONS if code in cs.split())
        meta.append({"c": code, "n": NAME.get(code, code),
                     "km2": AREA.get(code), "pop": p[1] or p[0],
                     "cap": cn, "cx": round(cx, 1), "cy": round(cy, 1),
                     "reg": reg, "div": div})

    def rotulo(cs):
        """Where the name of a group of states goes on the map.

        Only the lower 48 count: Alaska and Hawaii sit in boxes of their own
        at their own scale, and a label placed across the two would land in
        the ocean."""
        dentro = [c for c in cs if c in st and c not in ("AK", "HI", "PR")]
        if not dentro:
            return None
        u = unary_union([st[c] for c in dentro])
        pt = u.representative_point()
        x, y = T_of("CONUS")(pt.x, pt.y)
        return [round(x, 1), round(y, 1)]

    regiones, divisiones, vern = [], [], []
    for name, colour, codes in CENSUS_REGIONS:
        cs = codes.split()
        regiones.append({"n": name, "c": colour, "codes": cs,
                         "lab": rotulo(cs),
                         "note": f"Census Region, {len(cs)} states"})
    for name, region, colour, codes in CENSUS_DIVISIONS:
        cs = codes.split()
        divisiones.append({"n": name, "c": colour, "codes": cs,
                           "lab": rotulo(cs), "reg": region,
                           "note": f"Census Division, inside the {region}"})
    for name, colour, note, codes in VERNACULAR:
        cs = codes.split()
        d = "".join(path_of(g, T_of(c), 0.02) for c, g in
                    [(c, st[c]) for c in cs if c in st])
        vern.append({"n": name, "c": colour, "codes": cs, "note": note, "d": d})

    # rivers: the long ones, so the map is a river system and not a hairball
    courses = pickle.load(open(DATA / "courses.pkl", "rb"))
    named, anchors = {}, {}
    for nm, place, la, lo in NAMED_RIVERS:
        p = Point(lo, la)
        d = sorted((g.distance(p) * 111, i) for i, g in enumerate(courses))
        if d[0][0] > NEAR_KM or d[1][0] < d[0][0] * CLEAR:
            raise SystemExit(f"the {nm} at {place} is ambiguous: "
                             f"{d[0][0]:.1f} km and {d[1][0]:.1f} km")
        c = courses[d[0][1]]
        # the piece of that course the page actually draws
        best = min(riv, key=lambda g: g.hausdorff_distance(c)
                   if g.length > 0.4 else 9e9)
        named[id(best)] = nm
        anchors[nm] = (p, best)
    rv = []
    for g in riv:
        nm = named.get(id(g))
        if not nm and g.length < 0.85:
            continue
        code = "AK" if g.centroid.x < -130 else "HI" if g.centroid.y < 23 and g.centroid.x < -154 else None
        T = T_of(code or "CONUS")
        d = line_of(g, T, 0.004 if code else 0.012)
        if not d:
            continue
        if nm:
            # the label sits at the place the river was identified by
            cs = list(g.coords)
            p = anchors[nm][0]
            k = min(range(len(cs)), key=lambda i: (cs[i][0] - p.x) ** 2
                    + (cs[i][1] - p.y) ** 2)
            a = cs[max(0, k - 3)]
            b = cs[min(len(cs) - 1, k + 3)]
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
    for tier, polys in rug.items():
        for p in polys:
            d = path_of(p, Tc, 0.01)
            if d:
                mt.append({"d": d, "t": tier})

    js = {"states": paths, "meta": meta,
          "regions": regiones, "divisions": divisiones, "vern": vern,
          "rivers": rv, "rugged": mt, "vw": VW, "vh": VH}
    blob = json.dumps(js, separators=(",", ":"))

    facts = "\n".join(
        f'<div class="tile"><div class="k">{n}</div>'
        f'<div class="v">{v}</div><div class="d">{d}</div></div>'
        for n, v, d in FACTS)
    doc = TEMPLATE.replace("__DATA__", blob).replace("__FACTS__", facts)
    OUT.write_text(doc, encoding="utf-8")
    print(f"wrote {OUT} ({len(doc):,} bytes): {len(paths)} states, "
          f"{len(rv)} river segments ({len(named)} named), "
          f"{len(mt)} patches of rugged ground, "
          f"{len(regiones)} Census regions and {len(divisiones)} divisions")


if __name__ == "__main__":
    main()
