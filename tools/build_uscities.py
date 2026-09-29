#!/usr/bin/env python3
"""Generate us-cities.html: the twenty most populous cities in the United
States, their share of the country, and how much each has grown or shrunk
since the 2020 census.

Figures are Census Bureau Vintage 2025 population estimates for July 1, 2025,
with the April 1, 2020 estimates base as the starting point.

Usage: python3 build_uscities.py
"""

import json
import math
import apa
from pathlib import Path

OUT = Path(__file__).parent.parent / "us-cities.html"

SNAPSHOT = "August 14, 2026"
US_POP = 341_784_857          # 50 states plus DC, July 1, 2025

# name, state, USPS code (for the flag), 2020 base, 2025 estimate
ROWS = [
    ("New York",      "New York",       "ny", 8_805_594, 8_584_629),
    ("Los Angeles",   "California",     "ca", 3_899_342, 3_869_089),
    ("Chicago",       "Illinois",       "il", 2_748_333, 2_731_585),
    ("Houston",       "Texas",          "tx", 2_299_649, 2_397_315),
    ("Phoenix",       "Arizona",        "az", 1_608_349, 1_665_481),
    ("Philadelphia",  "Pennsylvania",   "pa", 1_603_800, 1_574_281),
    ("San Antonio",   "Texas",          "tx", 1_433_348, 1_548_422),
    ("San Diego",     "California",     "ca", 1_384_481, 1_406_106),
    ("Dallas",        "Texas",          "tx", 1_304_341, 1_329_491),
    ("Fort Worth",    "Texas",          "tx",   918_892, 1_028_117),
    ("Jacksonville",  "Florida",        "fl",   949_607, 1_017_689),
    ("Austin",        "Texas",          "tx",   958_151, 1_002_632),
    ("San Jose",      "California",     "ca", 1_013_321,   989_814),
    ("Charlotte",     "North Carolina", "nc",   874_708,   964_784),
    ("Columbus",      "Ohio",           "oh",   906_215,   938_396),
    ("Indianapolis",  "Indiana",        "in",   887_647,   901_116),
    ("San Francisco", "California",     "ca",   878_550,   826_079),
    ("Seattle",       "Washington",     "wa",   737_103,   784_777),
    ("Denver",        "Colorado",       "co",   715_509,   740_613),
    ("Nashville",     "Tennessee",      "tn",   689_449,   721_074),
]

# the city just past the end of the list, so row twenty also has a lead
NEXT_UP = ("Oklahoma City", 719_849)

C_UP = "#3987e5"      # categorical slot 1, dark step: growth
C_DOWN = "#d55181"    # categorical slot 5, dark step: decline
C_SHARE = "#8a93a3"   # neutral meter fill, not a series hue
C_GAP = "#0ca30c"     # delta text token, not a series hue


def commas(n):
    return f"{n:,}"


rows = []
for name, state, cc, base, pop in ROWS:
    rows.append(dict(name=name, state=state, cc=cc, base=base, pop=pop,
                     chg=pop - base, pct=(pop - base) / base * 100,
                     share=pop / US_POP * 100))

for i, r in enumerate(rows):
    below = rows[i + 1]["pop"] if i + 1 < len(rows) else NEXT_UP[1]
    r["gap"] = r["pop"] - below

first10, next10 = rows[:10], rows[10:]
share10 = sum(r["pop"] for r in first10) / US_POP * 100
share20 = sum(r["pop"] for r in rows) / US_POP * 100
max_share = max(r["share"] for r in rows)
PCT_MAX = 12.0        # symmetric scale for the change bars

# ---- the diverging change bar that lives inside each row ----
VW, ZERO, ARM, BH = 250, 118, 88, 11
VH = 20


def chg_svg(r):
    w = min(abs(r["pct"]) / PCT_MAX, 1.0) * ARM
    grew = r["chg"] > 0
    color = C_UP if grew else C_DOWN
    x = ZERO if grew else ZERO - w
    lbl = f'{"+" if grew else "−"}{abs(r["pct"]):.1f}%'
    tx = (ZERO + w + 6) if grew else (ZERO - w - 6)
    anchor = "start" if grew else "end"
    return (
        f'<svg class="chg" viewBox="0 0 {VW} {VH}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{r["name"]}: {lbl} since 2020">'
        f'<line x1="{ZERO}" y1="1" x2="{ZERO}" y2="{VH-1}" stroke="#383835"/>'
        f'<g><title>{commas(abs(r["chg"]))} people '
        f'{"gained" if grew else "lost"} since 2020, {lbl}</title>'
        f'<rect x="{x:.1f}" y="4" width="{max(2.0, w):.1f}" height="{BH}" rx="3" fill="{color}"/>'
        f'<rect x="{ZERO - (0 if grew else 3):.1f}" y="4" width="3" height="{BH}" fill="{color}"/></g>'
        f'<text x="{tx:.1f}" y="{4 + BH - 1.5}" text-anchor="{anchor}" font-size="10.5" '
        f'fill="#c3c2b7" font-variant-numeric="tabular-nums">{lbl}</text>'
        f'</svg>')


# Where each city sits: latitude and longitude of the city center, from
# plotly's us-cities-top-1k dataset (github.com/plotly/datasets), rounded to
# a thousandth of a degree. At the scale of the map a dot is a few pixels,
# so a city center rather than a centroid is enough.
COORDS = {
    "New York": (40.713, -74.006), "Los Angeles": (34.052, -118.244),
    "Chicago": (41.878, -87.630), "Houston": (29.760, -95.370),
    "Phoenix": (33.448, -112.074), "Philadelphia": (39.953, -75.165),
    "San Antonio": (29.424, -98.494), "San Diego": (32.716, -117.161),
    "Dallas": (32.777, -96.797), "Fort Worth": (32.755, -97.331),
    "Jacksonville": (30.332, -81.656), "Austin": (30.267, -97.743),
    "San Jose": (37.338, -121.886), "Charlotte": (35.227, -80.843),
    "Columbus": (39.961, -82.999), "Indianapolis": (39.768, -86.158),
    "San Francisco": (37.775, -122.419), "Seattle": (47.606, -122.332),
    "Denver": (39.739, -104.990), "Nashville": (36.163, -86.782),
}
# the cities with a page of their own on this site
PAGES = {"New York": "new-york.html", "Los Angeles": "los-angeles.html"}

# The state outlines are the small map us-states.html uses (Web Mercator,
# lower 48 fitted to a box). The fit is recovered from the outlines
# themselves: their pixel extents against the extreme longitudes of the
# lower 48 (Cape Alava, -124.73; West Quoddy Head, -66.95) and the extreme
# latitudes (Northwest Angle, 49.38; the Florida Keys, 24.52).
USMAP = json.loads((Path(__file__).parent / "data" / "usmap.json").read_text())
FLAGS = json.loads((Path(__file__).parent / "data" / "state_flags.json").read_text())
_R = 6378137.0


def _mx(lon):
    return _R * math.radians(lon)


def _my(lat):
    return _R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def _extent():
    import re
    xs, ys = [], []
    for k, d in USMAP["paths"].items():
        if k in ("AK", "HI"):
            continue
        for a, b in re.findall(r"(-?[\d.]+),(-?[\d.]+)", d):
            xs.append(float(a)); ys.append(float(b))
    return min(xs), max(xs), min(ys), max(ys)


PX0, PX1, PY0, PY1 = _extent()
K = (PX1 - PX0) / (_mx(-66.95) - _mx(-124.73))
MY_MID = (_my(49.38) + _my(24.52)) / 2


def proj(lat, lon):
    return (PX0 + (_mx(lon) - _mx(-124.73)) * K,
            (PY0 + PY1) / 2 + (MY_MID - _my(lat)) * K)


# a dot's area is its population; the tier colors are the state pages'
def dot_r(pop):
    return 13.0 * math.sqrt(pop / rows[0]["pop"])


def tier(pop):
    return "#ef5350" if pop >= 1e7 else "#ff9440" if pop >= 1e6 else "#ffd24d" if pop >= 1e5 else "#66bb6a"


LABELED = 6     # the largest few carry their names; the rest name on hover
# where a name sits when the default (right of the dot, left in the east) collides
LPOS = {"New York": "a", "Philadelphia": "b", "Los Angeles": "a"}
dots = []
for i, r in sorted(enumerate(rows), key=lambda t: -t[1]["pop"]):
    x, y = proj(*COORDS[r["name"]])
    r["x"], r["y"] = x, y
    dots.append(
        f'<g class="dot" data-i="{i}"><circle cx="{x:.1f}" cy="{y:.1f}" r="{dot_r(r["pop"]):.1f}" '
        f'fill="{tier(r["pop"])}" fill-opacity="0.72" stroke="#121212" stroke-width="0.8"/>'
        f'<title>{r["name"]}</title></g>')
MAP_PATHS = "".join(f'<path d="{d}"/>' for c, d in USMAP["paths"].items()
                    if c not in ("AK", "HI"))
VB = f"{PX0 - 8:.0f} {PY0 - 8:.0f} {PX1 - PX0 + 16:.0f} {PY1 - PY0 + 16:.0f}"
CITY_JS = json.dumps([dict(n=r["name"], st=r["state"], pop=r["pop"], chg=r["chg"],
                           pct=round(r["pct"], 1), share=round(r["share"], 2),
                           rank=i + 1, gap=r["gap"],
                           nxt=rows[i + 1]["name"] if i + 1 < len(rows) else NEXT_UP[0],
                           x=round(r["x"], 1), y=round(r["y"], 1),
                           r=round(dot_r(r["pop"]), 1), lab=i < LABELED,
                           href=PAGES.get(r["name"]), lp=LPOS.get(r["name"], ""))
                      for i, r in enumerate(rows)], separators=(",", ":"))

HEAD = """<thead><tr>
  <th class="l" colspan="2">City</th>
  <th>Population <span class="gh">(lead over next)</span></th>
  <th class="l">Share of the U.S.</th>
  <th class="l">Change since 2020</th>
  <th>People</th>
</tr></thead>"""


def tr(i, r):
    bar_w = r["share"] / max_share * 100
    chg_txt = ("+" if r["chg"] > 0 else "−") + commas(abs(r["chg"]))
    name = (f'<a href="{PAGES[r["name"]]}">{r["name"]}</a>' if r["name"] in PAGES
            else r["name"])
    return f"""<tr class="crow" data-i="{i - 1}" data-pop="{r['pop']}" data-pct="{r['pct']:.3f}" data-chg="{r['chg']}">
  <td class="rank">{i}</td>
  <td class="ct"><span class="cw"><img class="flag" src="{FLAGS[r['cc']]}"
      width="30" height="20" alt="Flag of {r['state']}"><span>{name}<span
      class="st">{r['state']}</span></span></span></td>
  <td class="num pop">{commas(r['pop'])} <span class="gap">(+{commas(r['gap'])})</span></td>
  <td class="share"><span class="track"><span class="fill" style="width:{bar_w:.1f}%"></span></span><span class="pct">{r['share']:.2f}%</span></td>
  <td class="chg">{chg_svg(r)}</td>
  <td class="num">{chg_txt}</td>
</tr>"""


def totals(label, block, cls="total"):
    p = sum(r["pop"] for r in block)
    b = sum(r["base"] for r in block)
    c = p - b
    sign = "+" if c > 0 else "−"
    return (f'<tr class="{cls}"><td></td><td>{label}</td>'
            f'<td class="num">{commas(p)}</td>'
            f'<td>{p / US_POP * 100:.1f}% of the country</td>'
            f'<td>{sign}{abs(c / b * 100):.1f}% since 2020</td>'
            f'<td class="num">{sign}{commas(abs(c))}</td></tr>')


# one table, so the rows can be reordered; the first ten keep a subtotal
# of their own while the order is by population, and the grand total is
# the last row
body = ("\n".join(tr(1 + i, r) for i, r in enumerate(first10)) + "\n"
        + totals("These ten together", first10, "total sub") + "\n"
        + "\n".join(tr(11 + i, r) for i, r in enumerate(next10)))
table_all = (f'<div class="tscroll" id="tbl" tabindex="0" aria-label="The twenty cities; arrow keys '
             f'walk the list when the table has focus"><table>\n{HEAD}\n<tbody id="tb">\n{body}\n'
             f'{totals("All twenty together", rows)}\n</tbody>\n</table></div>')

grew = [r for r in rows if r["chg"] > 0]
shrank = [r for r in rows if r["chg"] < 0]
fast = max(rows, key=lambda r: r["pct"])
slow = min(rows, key=lambda r: r["pct"])
DEF = [["U.S. population", f"{US_POP/1e6:.1f} million", f"{commas(US_POP)} in 2025"],
       ["Largest city", rows[0]["name"], f"{commas(rows[0]['pop'])} people"],
       ["Fastest growth", f"+{fast['pct']:.1f}%", f"{fast['name']} since 2020"],
       ["Steepest decline", f"−{abs(slow['pct']):.1f}%", f"{slow['name']} since 2020"]]
TILES = "".join(f'<div class="tile"><div class="lab" id="l{k+1}">{a}</div>'
                f'<div class="val" id="v{k+1}">{b}</div><div class="sub" id="s{k+1}">{c}</div></div>'
                for k, (a, b, c) in enumerate(DEF))
KEY = "".join(f'<span><i style="background:{c}"></i>{t}</span>'
              for c, t in (("#ff9440", "a million or more"), ("#ffd24d", "100,000 to a million")))

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Most Populous Cities in the United States · Altazor</title>
<style>
:root {{ --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff;
        --ink-2:#c3c2b7; --ink-3:#898781;
        --up:{C_UP}; --down:{C_DOWN}; --share:{C_SHARE}; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }}
.wrap {{ max-width:1040px; margin:0 auto; padding:32px 20px 70px; }}
header.site {{ border-top:4px solid var(--accent); padding-top:22px; margin-bottom:26px;
  display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }}
.brand {{ font-weight:700; font-size:20px; letter-spacing:.1em; text-decoration:none; color:var(--text); }}
.brand:hover {{ color:var(--accent); }}
nav.site a {{ color:var(--muted); text-decoration:none; font-size:14px; }}
nav.site a:hover {{ color:var(--accent); }}
h1 {{ margin:0 0 6px; font-size:26px; }}
h2 {{ font-size:16px; margin:34px 0 10px; letter-spacing:.02em; }}
.stamp {{ color:var(--ink-3); font-size:12.5px; margin:0 0 18px; }}

.dash {{ display:grid; grid-template-columns:minmax(0,1fr) 400px; gap:14px; align-items:stretch; }}
@media (max-width:900px) {{ .dash {{ grid-template-columns:1fr; }} }}
.mappanel {{ background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:10px 12px 8px; }}
#cmap {{ display:block; width:100%; height:auto; outline:none; }}
#cmap:focus-visible {{ box-shadow:0 0 0 2px var(--accent); border-radius:6px; }}
#cmap path {{ fill:#262c33; stroke:#121212; stroke-width:0.7; }}
#cmap .dot {{ cursor:pointer; }}
#cmap .dot circle {{ transition:fill-opacity .12s; }}
#cmap .dot.hl circle, #cmap .dot.sel circle {{ fill-opacity:1; stroke:#fff; stroke-width:1.4; }}
#cmap text {{ font-size:8.5px; fill:#e6e6e6; stroke:#121212; stroke-width:2.2px; paint-order:stroke;
  pointer-events:none; }}
.mapcap {{ color:var(--ink-2); font-size:12.5px; text-align:center; padding:4px 0 2px; min-height:24px; }}
.mapkey {{ display:flex; flex-wrap:wrap; justify-content:center; gap:4px 14px; font-size:11.5px; color:var(--ink-3); }}
.mapkey i {{ display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:5px; vertical-align:-1px; }}
.tiles {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; align-content:start; }}
.tile {{ background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:14px 16px; min-width:0; }}
.tile .lab {{ color:var(--muted); font-size:12.5px; }}
.tile .val {{ font-size:24px; font-weight:600; margin-top:2px; line-height:1.2; overflow-wrap:anywhere; }}
.tile .sub {{ color:var(--ink-3); font-size:12px; margin-top:2px; }}

.ctl {{ display:flex; flex-wrap:wrap; gap:8px 18px; align-items:center; margin:4px 0 10px; }}
.ctl .grp {{ display:inline-flex; flex-wrap:wrap; gap:6px; align-items:center; }}
.ctl .gl {{ color:var(--muted); font-size:10.5px; letter-spacing:.09em; text-transform:uppercase; margin-right:4px; }}
.ctl button {{ font:inherit; font-size:13px; padding:4px 12px; border-radius:999px;
  border:1px solid var(--line); background:#1a1a1a; color:var(--muted); cursor:pointer; }}
.ctl button.on {{ color:var(--text); border-color:var(--accent); background:#1c2733; }}
.ctl button:hover {{ border-color:var(--accent); }}
.legend {{ display:inline-flex; gap:14px; font-size:12.5px; color:var(--ink-2); margin-left:auto; }}
.legend .sw {{ width:11px; height:11px; border-radius:3px; display:inline-block; margin-right:6px; vertical-align:-1px; }}

table {{ width:100%; border-collapse:collapse; margin-top:4px; }}
th {{ text-align:right; font-size:11.5px; letter-spacing:.06em; text-transform:uppercase;
  color:var(--ink-3); font-weight:600; padding:0 10px 8px; border-bottom:1px solid var(--line); }}
th.l {{ text-align:left; }}
th .gh {{ color:{C_GAP}; text-transform:none; letter-spacing:0; font-weight:500; }}
td {{ padding:8px 10px; border-bottom:1px solid var(--line); font-size:14px; }}
td.num {{ text-align:right; font-variant-numeric:tabular-nums; color:var(--ink-2); }}
td.rank {{ color:var(--ink-3); width:26px; font-variant-numeric:tabular-nums; }}
td.ct {{ white-space:nowrap; }}
td.ct a {{ color:var(--text); text-decoration:underline; text-decoration-color:var(--accent);
  text-underline-offset:3px; }}
td.ct a:hover {{ color:var(--accent); }}
td.pop {{ white-space:nowrap; }}
.cw {{ display:flex; align-items:center; gap:10px; }}
.st {{ display:block; color:#aaa89f; font-size:12px; line-height:1.15; }}
img.flag {{ width:30px; height:20px; object-fit:cover; border-radius:2px;
  box-shadow:0 0 0 1px rgba(255,255,255,.14); display:block; flex:none; }}
.gap {{ color:{C_GAP}; font-size:12.5px; font-variant-numeric:tabular-nums; margin-left:7px; }}
td.share {{ width:170px; white-space:nowrap; }}
.track {{ display:inline-block; width:96px; height:9px; background:#242424; border-radius:5px;
  vertical-align:middle; overflow:hidden; }}
.fill {{ display:block; height:100%; background:var(--share); border-radius:0 4px 4px 0; }}
.pct {{ display:inline-block; width:46px; text-align:right; font-variant-numeric:tabular-nums;
  color:var(--ink-2); font-size:13px; margin-left:8px; }}
td.chg {{ width:250px; padding-top:6px; padding-bottom:6px; }}
svg.chg {{ display:block; width:100%; height:auto; }}
svg.chg rect {{ transition:opacity .12s; }}
svg.chg g:hover rect {{ opacity:.72; }}
tr.crow {{ cursor:pointer; outline:none; }}
tr.crow:hover td, tr.crow.hl td {{ background:#1e1e1e; }}
tr.crow.sel td {{ background:#20303f; }}
tr.total td {{ border-bottom:none; color:var(--muted); font-size:13px; padding-top:12px; }}
tr.total.sub td {{ border-bottom:1px solid var(--line); padding-bottom:12px; }}
.sorted tr.total.sub {{ display:none; }}
.tscroll {{ outline:none; }}
.tscroll:focus-visible {{ box-shadow:0 0 0 2px var(--accent); border-radius:6px; }}

.note {{ color:var(--muted); font-size:12.5px; max-width:760px; }}
details.sources {{ margin-top:30px; border-top:1px solid var(--line); padding-top:10px; max-width:760px; }}
details.sources > summary {{ cursor:pointer; color:var(--muted); font-size:12.5px; letter-spacing:.06em; text-transform:uppercase; }}
details.sources > summary:hover {{ color:var(--accent); }}
.refs {{ font-size:13px; color:var(--ink-2); max-width:760px; }}
.refs p {{ padding-left:2.2em; text-indent:-2.2em; margin:0 0 .8em; }}
.refs a {{ color:var(--accent); }}
@media (max-width:820px) {{
  td.share, td.chg {{ width:auto; }} .track {{ width:56px; }}
  .tscroll {{ overflow-x:auto; -webkit-overflow-scrolling:touch; }}
}}
@media (max-width:600px) {{
  .tile .val {{ font-size:20px; }} .tiles {{ gap:10px; }} .tile {{ padding:12px 13px; }}
  .ctl button {{ padding:4px 10px; font-size:12.5px; }}
}}
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library</a> &nbsp;·&nbsp;
    <a href="us-states.html">States</a></nav>
</header>

<h1>Most Populous Cities in the United States</h1>
<p class="stamp">Snapshot taken {SNAPSHOT}, using Census Bureau estimates for
July 1, 2025.</p>

<div class="dash">
<div class="mappanel">
  <svg id="cmap" viewBox="{VB}" role="img" tabindex="0"
    aria-label="Map of the twenty largest cities, each dot sized by its population">{MAP_PATHS}<g id="dots">{"".join(dots)}</g><g id="labs"></g></svg>
  <div class="mapcap" id="mapcap">Each dot's area is its city's population</div>
  <div class="mapkey">{KEY}</div>
</div>
<div class="tiles">{TILES}</div>
</div>

<h2>The twenty largest</h2>
<div class="ctl">
  <span class="grp" id="sorts"><span class="gl">Order</span>
    <button data-sort="pop" class="on">Population</button>
    <button data-sort="pct">Growth rate</button>
    <button data-sort="chg">People gained</button></span>
  <span class="legend"><span><span class="sw" style="background:var(--up)"></span>Grew since 2020</span>
  <span><span class="sw" style="background:var(--down)"></span>Shrank since 2020</span></span>
</div>
{table_all}

<h2>How to read this</h2>
<p class="note">The twenty largest cities by population, with each one's share of
the country and its change since the 2020 census. These are city limits, not metro
areas, which is why Phoenix outranks Philadelphia. Growth runs right on the change
bars, decline left, on one scale. {len(grew)} have grown since 2020 and
{len(shrank)} have lost people.</p>

<details class="sources"><summary>Sources</summary>
<h2>Notes</h2>
<p class="note">The green figure after a population is how many more people that
city has than the one ranked below it. Nashville is last on the list, so its
comparison is {NEXT_UP[0]} at rank twenty-one.</p>
<p class="note">Populations are Census Bureau estimates for July 1, 2025, and the
comparison year is the April 1, 2020 estimates base. These are city limits, not
metropolitan areas, which is why Phoenix outranks Philadelphia here and why no
figure for New York includes its suburbs. Indianapolis and Nashville are the
consolidated city and county governments minus the towns that stayed separate,
the balance figures the Census Bureau publishes for them. The flags are the state
flags, baked into the page from the us-state-flags package. On the map each dot
sits on the city center and its area is proportional to the population; the
colors are the population tiers of the state and city pages.</p>

<h2>References</h2>
<div class="refs">
<p>U.S. Census Bureau. (2026). <em>Annual estimates of the resident population
for incorporated places: April 1, 2020 to July 1, 2025</em> (Vintage 2025
population estimates) [Data set]. Retrieved {SNAPSHOT}, from
<a href="https://www.census.gov/programs-surveys/popest.html">https://www.census.gov/programs-surveys/popest.html</a></p>
<p>U.S. Census Bureau. (2026). <em>State population totals and components of
change: 2020 to 2025</em> (Vintage 2025 population estimates) [Data set].
Retrieved {SNAPSHOT}, from
<a href="https://www.census.gov/programs-surveys/popest.html">https://www.census.gov/programs-surveys/popest.html</a></p>
<p>City coordinates: Plotly, us-cities-top-1k [Data set].
<a href="https://github.com/plotly/datasets/blob/master/us-cities-top-1k.csv">https://github.com/plotly/datasets/blob/master/us-cities-top-1k.csv</a></p>
<p>Map outlines: Natural Earth, 50m states and provinces.
<a href="https://www.naturalearthdata.com/">https://www.naturalearthdata.com/</a></p>
<p>State flags: us-state-flags, version 1.0.7 (ISC license), rasterized at 60 by 40 pixels.
<a href="https://www.npmjs.com/package/us-state-flags">https://www.npmjs.com/package/us-state-flags</a></p>
</div>
</details>
</div>
<script>
const C={CITY_JS};
const DEF={json.dumps(DEF, ensure_ascii=False)};
const CAP0="Each dot's area is its city's population";
const REDUCED=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
let sel=null, sortKey='pop';
const map=document.getElementById('cmap'), labs=document.getElementById('labs');
const cap=document.getElementById('mapcap');
const tb=document.getElementById('tb'), tbl=document.getElementById('tbl');
const fmtC=n=>n.toLocaleString('en-US');
const big=n=>n>=1e6?(n/1e6).toFixed(2)+' million':fmtC(n);
const sg=v=>(v>0?'+':'−');
function setTiles(a){{ a.forEach((t,i)=>{{
  document.getElementById('l'+(i+1)).textContent=t[0];
  document.getElementById('v'+(i+1)).textContent=t[1];
  document.getElementById('s'+(i+1)).textContent=t[2]; }}); }}
function capFor(i){{ const d=C[i];
  return d.n+', '+d.st+' · '+fmtC(d.pop)+' · '+sg(d.chg)+Math.abs(d.pct).toFixed(1)+'% since 2020'; }}
// names on the map: the largest few always, and whichever city is lit
function drawLabels(extra){{
  const on=new Set(C.map((d,i)=>d.lab?i:-1).filter(i=>i>=0));
  if(sel!=null) on.add(sel); if(extra!=null) on.add(extra);
  let s='';
  on.forEach(i=>{{ const d=C[i];
    let x, y=d.y+3, an='start';
    if(d.lp==='a'){{ x=d.x; y=d.y-d.r-3; an='middle'; }}
    else if(d.lp==='b'){{ x=d.x; y=d.y+d.r+9; an='middle'; }}
    else if(d.x>400){{ x=d.x-d.r-2.5; an='end'; }}
    else x=d.x+d.r+2.5;
    s+='<text x="'+x.toFixed(1)+'" y="'+y.toFixed(1)+'" text-anchor="'+an+'">'+d.n+'</text>'; }});
  labs.innerHTML=s;
}}
function apply(i){{
  sel=i;
  document.querySelectorAll('#cmap .dot').forEach(g=>g.classList.toggle('sel',+g.dataset.i===i));
  document.querySelectorAll('tr.crow').forEach(t=>t.classList.toggle('sel',+t.dataset.i===i));
  drawLabels(null);
  if(i==null){{ setTiles(DEF); cap.textContent=CAP0; return; }}
  const g=map.querySelector('.dot[data-i="'+i+'"]'); if(g) g.parentNode.appendChild(g);
  const d=C[i];
  setTiles([
    [d.n, big(d.pop), 'No. '+d.rank+' of 20 · '+d.st],
    ['Share of the U.S.', d.share.toFixed(2)+'%', 'of {commas(US_POP)} people'],
    ['Change since 2020', sg(d.chg)+Math.abs(d.pct).toFixed(1)+'%', sg(d.chg)+fmtC(Math.abs(d.chg))+' people'],
    ['Lead over next rank', '+'+fmtC(d.gap), 'over '+d.nxt]]);
  cap.textContent=capFor(i);
}}
function hl(i){{
  document.querySelectorAll('#cmap .dot.hl').forEach(g=>g.classList.remove('hl'));
  document.querySelectorAll('tr.crow.hl').forEach(t=>t.classList.remove('hl'));
  drawLabels(i);
  if(i==null){{ cap.textContent=sel!=null?capFor(sel):CAP0; return; }}
  const g=map.querySelector('.dot[data-i="'+i+'"]'); if(g) g.classList.add('hl');
  const t=document.querySelector('tr.crow[data-i="'+i+'"]'); if(t) t.classList.add('hl');
  cap.textContent=capFor(i);
}}
document.querySelectorAll('tr.crow').forEach(t=>{{
  const i=+t.dataset.i;
  t.addEventListener('click',e=>{{ if(e.target.closest('a')) return; apply(sel===i?null:i); }});
  t.addEventListener('pointerenter',()=>hl(i));
  t.addEventListener('pointerleave',()=>hl(null));
}});
document.querySelectorAll('#cmap .dot').forEach(g=>{{
  const i=+g.dataset.i;
  g.addEventListener('click',()=>apply(sel===i?null:i));
  g.addEventListener('pointerenter',()=>hl(i));
  g.addEventListener('pointerleave',()=>hl(null));
}});
drawLabels(null);

// ---- order: the rows slide to their new places ----
function rowsNow(){{ return [...tb.querySelectorAll('tr.crow')]; }}
function sortBy(key){{
  sortKey=key;
  document.querySelectorAll('#sorts button').forEach(b=>b.classList.toggle('on',b.dataset.sort===key));
  tbl.classList.toggle('sorted',key!=='pop');
  const rs=rowsNow(), sub=tb.querySelector('tr.total.sub'), total=tb.querySelector('tr.total:not(.sub)');
  const top0=new Map(rs.map(r=>[r,r.getBoundingClientRect().top]));
  rs.sort((a,b)=>+b.dataset[key]-+a.dataset[key]);
  rs.forEach(r=>tb.insertBefore(r,total));
  if(key==='pop') tb.insertBefore(sub,rs[10]);
  if(REDUCED) return;
  rs.forEach(r=>{{
    const d=top0.get(r)-r.getBoundingClientRect().top;
    if(!d) return;
    r.style.transition='none'; r.style.transform='translateY('+d+'px)';
  }});
  requestAnimationFrame(()=>requestAnimationFrame(()=>rs.forEach(r=>{{
    if(!r.style.transform) return;
    r.style.transition='transform .8s cubic-bezier(.45,0,.55,1)'; r.style.transform='';
  }})));
}}
document.querySelectorAll('#sorts button').forEach(b=>b.onclick=()=>sortBy(b.dataset.sort));

// ---- arrow keys walk the rows, in the order shown, while the table or map has focus ----
document.addEventListener('keydown',e=>{{
  const a=document.activeElement;
  if(a&&(a.tagName==='INPUT'||a.tagName==='TEXTAREA')) return;
  if(e.key==='Escape'){{ apply(null); return; }}
  if(!(a===tbl||a===map||tbl.contains(a))) return;
  const dn=e.key==='ArrowDown'||e.key==='ArrowRight', up=e.key==='ArrowUp'||e.key==='ArrowLeft';
  if(!dn&&!up) return;
  e.preventDefault();
  const rs=rowsNow();
  let k=rs.findIndex(r=>+r.dataset.i===sel);
  k=k<0?(dn?0:rs.length-1):Math.max(0,Math.min(rs.length-1,k+(dn?1:-1)));
  apply(+rs[k].dataset.i);
  if(a!==map) rs[k].scrollIntoView({{block:'nearest'}});
}});
window.__usc=()=>({{sel, sortKey, tiles:[1,2,3,4].map(i=>document.getElementById('v'+i).textContent),
  dots:document.querySelectorAll('#cmap .dot').length, labels:labs.querySelectorAll('text').length,
  order:rowsNow().map(r=>C[+r.dataset.i].n)}});
</script>
</body>
</html>
"""

HTML = apa.apa_pass(HTML)
OUT.write_text(HTML, encoding="utf-8")
print(f"wrote {OUT} ({len(HTML)} bytes): {len(rows)} cities, "
      f"{len(grew)} grew, {len(shrank)} shrank")
