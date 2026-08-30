#!/usr/bin/env python3
"""Generate us-states.html: every state by population, largest to smallest,
with its share of the country and its change since the 2020 census.

Figures are Census Bureau Vintage 2025 population estimates for July 1, 2025,
with the April 1, 2020 estimates base as the starting point. The District of
Columbia is counted in the national total but listed separately, since it is
not a state.

Usage: python3 build_usstates.py
"""

import json
from pathlib import Path

OUT = Path(__file__).parent.parent / "us-states.html"
USMAP = json.loads((Path(__file__).parent / "data" / "usmap.json").read_text())

SNAPSHOT = "August 14, 2026"
US_POP = 341_784_857          # 50 states plus DC, July 1, 2025

# name, USPS code (for the flag), 2020 base, 2025 estimate
ROWS = [
    ("California",     "ca", 39_555_703, 39_355_309),
    ("Texas",          "tx", 29_149_498, 31_709_821),
    ("Florida",        "fl", 21_538_207, 23_462_518),
    ("New York",       "ny", 20_203_696, 20_002_427),
    ("Pennsylvania",   "pa", 13_002_753, 13_059_432),
    ("Illinois",       "il", 12_821_741, 12_719_141),
    ("Ohio",           "oh", 11_799_445, 11_900_510),
    ("Georgia",        "ga", 10_713_861, 11_302_748),
    ("North Carolina", "nc", 10_441_392, 11_197_968),
    ("Michigan",       "mi", 10_079_362, 10_127_884),
    ("New Jersey",     "nj",  9_289_024,  9_548_215),
    ("Virginia",       "va",  8_631_419,  8_880_107),
    ("Washington",     "wa",  7_707_519,  8_001_020),
    ("Arizona",        "az",  7_158_104,  7_623_818),
    ("Tennessee",      "tn",  6_912_319,  7_315_076),
    ("Massachusetts",  "ma",  7_033_112,  7_154_084),
    ("Indiana",        "in",  6_786_605,  6_973_333),
    ("Missouri",       "mo",  6_154_913,  6_270_541),
    ("Maryland",       "md",  6_181_640,  6_265_347),
    ("Colorado",       "co",  5_775_326,  6_012_561),
    ("Wisconsin",      "wi",  5_894_323,  5_972_787),
    ("Minnesota",      "mn",  5_706_733,  5_830_405),
    ("South Carolina", "sc",  5_118_250,  5_570_274),
    ("Alabama",        "al",  5_025_437,  5_193_088),
    ("Louisiana",      "la",  4_657_894,  4_618_189),
    ("Kentucky",       "ky",  4_506_287,  4_606_864),
    ("Oregon",         "or",  4_237_282,  4_273_586),
    ("Oklahoma",       "ok",  3_959_354,  4_123_288),
    ("Connecticut",    "ct",  3_607_750,  3_688_496),
    ("Utah",           "ut",  3_271_601,  3_538_904),
    ("Nevada",         "nv",  3_105_593,  3_282_188),
    ("Iowa",           "ia",  3_190_582,  3_238_387),
    ("Arkansas",       "ar",  3_011_530,  3_114_791),
    ("Kansas",         "ks",  2_937_986,  2_977_220),
    ("Mississippi",    "ms",  2_961_264,  2_954_160),
    ("New Mexico",     "nm",  2_117_492,  2_125_498),
    ("Idaho",          "id",  1_839_123,  2_029_733),
    ("Nebraska",       "ne",  1_961_980,  2_018_006),
    ("West Virginia",  "wv",  1_793_759,  1_766_147),
    ("Hawaii",         "hi",  1_455_267,  1_432_820),
    ("New Hampshire",  "nh",  1_377_573,  1_415_342),
    ("Maine",          "me",  1_363_218,  1_414_874),
    ("Montana",        "mt",  1_084_221,  1_144_694),
    ("Rhode Island",   "ri",  1_097_357,  1_114_521),
    ("Delaware",       "de",    989_950,  1_059_952),
    ("South Dakota",   "sd",    886_656,    935_094),
    ("North Dakota",   "nd",    779_136,    799_358),
    ("Alaska",         "ak",    733_383,    737_270),
    ("Vermont",        "vt",    643_077,    644_663),
    ("Wyoming",        "wy",    576_872,    588_753),
]

# counted in the national total, listed on its own because it is not a state
DC = ("District of Columbia", "dc", 689_544, 693_645)

C_UP = "#3987e5"      # categorical slot 1, dark step: growth
C_DOWN = "#d55181"    # categorical slot 5, dark step: decline
C_SHARE = "#8a93a3"   # neutral meter fill, not a series hue
C_GAP = "#0ca30c"     # delta text token, not a series hue


def commas(n):
    return f"{n:,}"


def _star(cx, cy, r):
    """Five-pointed star, point up."""
    import math
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rad = r if k % 2 == 0 else r * 0.382
        pts.append(f"{cx + rad * math.cos(a):.2f},{cy + rad * math.sin(a):.2f}")
    return " ".join(pts)


# flagcdn has no District of Columbia flag, so draw it: three stars over two bars
DC_FLAG = (
    '<svg class="flag" viewBox="0 0 19 10" width="30" height="20" '
    'role="img" aria-label="Flag of the District of Columbia">'
    '<rect width="19" height="10" fill="#fff"/>'
    + "".join(f'<polygon points="{_star(cx, 2.35, 1.35)}" fill="#c8102e"/>'
              for cx in (5.7, 9.5, 13.3))
    + '<rect x="0" y="4.55" width="19" height="1.5" fill="#c8102e"/>'
      '<rect x="0" y="7.0" width="19" height="1.5" fill="#c8102e"/>'
      '</svg>')


def mk(name, cc, base, pop):
    return dict(name=name, cc=cc, base=base, pop=pop, chg=pop - base,
                pct=(pop - base) / base * 100, share=pop / US_POP * 100)


rows = [mk(*r) for r in ROWS]
dc = mk(*DC)

# lead over the state one rank below; the last state has nothing below it
for i, r in enumerate(rows):
    r["gap"] = r["pop"] - rows[i + 1]["pop"] if i + 1 < len(rows) else None

max_share = max(r["share"] for r in rows)
PCT_MAX = 11.0        # symmetric scale for the change bars
grew = [r for r in rows if r["chg"] > 0]
shrank = [r for r in rows if r["chg"] < 0]
fastest = max(rows, key=lambda r: r["pct"])
steepest = min(rows, key=lambda r: r["pct"])

# ---- the diverging change bar that lives inside each row ----
VW, ZERO, ARM, BH = 250, 118, 88, 11
VH = 20


def chg_svg(r):
    w = min(abs(r["pct"]) / PCT_MAX, 1.0) * ARM
    grow = r["chg"] > 0
    color = C_UP if grow else C_DOWN
    x = ZERO if grow else ZERO - w
    lbl = f'{"+" if grow else "−"}{abs(r["pct"]):.1f}%'
    tx = (ZERO + w + 6) if grow else (ZERO - w - 6)
    anchor = "start" if grow else "end"
    return (
        f'<svg class="chg" viewBox="0 0 {VW} {VH}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{r["name"]}: {lbl} since 2020">'
        f'<line x1="{ZERO}" y1="1" x2="{ZERO}" y2="{VH-1}" stroke="#383835"/>'
        f'<g><title>{commas(abs(r["chg"]))} people '
        f'{"gained" if grow else "lost"} since 2020, {lbl}</title>'
        f'<rect x="{x:.1f}" y="4" width="{max(2.0, w):.1f}" height="{BH}" rx="3" fill="{color}"/>'
        f'<rect x="{ZERO - (0 if grow else 3):.1f}" y="4" width="3" height="{BH}" fill="{color}"/></g>'
        f'<text x="{tx:.1f}" y="{4 + BH - 1.5}" text-anchor="{anchor}" font-size="10.5" '
        f'fill="#c3c2b7" font-variant-numeric="tabular-nums">{lbl}</text>'
        f'</svg>')


HEAD = """<thead><tr>
  <th class="l" colspan="2">State</th>
  <th>Population</th>
  <th class="l">Share of the U.S.</th>
  <th class="l">Change since 2020</th>
  <th>People</th>
</tr></thead>"""


def tr(i, r, rank=True):
    bar_w = r["share"] / max_share * 100
    chg_txt = ("+" if r["chg"] > 0 else "−") + commas(abs(r["chg"]))
    gap = (f' <span class="gap">(+{commas(r["gap"])})</span>'
           if r.get("gap") else "")
    flag = (DC_FLAG if r["cc"] == "dc" else
            f'<img class="flag" src="https://flagcdn.com/w80/us-{r["cc"]}.png"'
            f' width="30" height="20" alt="Flag of {r["name"]}">')
    return f"""<tr class="strow" data-cc="{r['cc']}">
  <td class="rank">{i if rank else ""}</td>
  <td class="ct"><span class="cw">{flag}<span>{r['name']}</span></span></td>
  <td class="num pop">{commas(r['pop'])}{gap}</td>
  <td class="share"><span class="track"><span class="fill" style="width:{bar_w:.1f}%"></span></span><span class="pct">{r['share']:.2f}%</span></td>
  <td class="chg">{chg_svg(r)}</td>
  <td class="num">{chg_txt}</td>
</tr>"""


# ---- per-state data for the dashboard swap, and the little US map ----
for i, r in enumerate(rows):
    r["next"] = rows[i + 1]["name"] if i + 1 < len(rows) else None
DATA = {r["cc"]: dict(n=r["name"], pop=r["pop"], chg=r["chg"],
                      pct=round(r["pct"], 1), share=round(r["share"], 2),
                      rank=i + 1, gap=r.get("gap"), nxt=r["next"])
        for i, r in enumerate(rows)}
DATA["dc"] = dict(n=dc["name"], pop=dc["pop"], chg=dc["chg"],
                  pct=round(dc["pct"], 1), share=round(dc["share"], 2),
                  rank=None, gap=None, nxt=None)
DATA_JS = json.dumps(DATA, separators=(",", ":"))
MAP_PATHS = "".join(f'<path d="{d}" data-cc="{p.lower()}"/>'
                    for p, d in USMAP["paths"].items())

body = "\n".join(tr(i + 1, r) for i, r in enumerate(rows))
p = sum(r["pop"] for r in rows)
b = sum(r["base"] for r in rows)
c = p - b
total_row = (f'<tr class="total"><td></td><td>All fifty together</td>'
             f'<td class="num">{commas(p)}</td>'
             f'<td>{p / US_POP * 100:.1f}% of the country</td>'
             f'<td>+{c / b * 100:.1f}% since 2020</td>'
             f'<td class="num">+{commas(c)}</td></tr>')
table_states = f'<table>\n{HEAD}\n<tbody>\n{body}\n{total_row}\n</tbody>\n</table>'
table_dc = f'<table>\n{HEAD}\n<tbody>\n{tr(0, dc, rank=False)}\n</tbody>\n</table>'

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Every State by Population · Altazor</title>
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
.lede {{ color:var(--muted); font-size:14.5px; margin:0 0 6px; max-width:730px; }}
.stamp {{ color:var(--ink-3); font-size:12.5px; margin:0 0 22px; }}

.dash {{ display:grid; grid-template-columns:minmax(0,1fr) 470px; gap:14px; align-items:stretch; }}
.mappanel {{ background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:10px 12px 4px; }}
#usmap {{ display:block; width:100%; height:auto; }}
#usmap path {{ fill:#262c33; stroke:#121212; stroke-width:0.7; cursor:pointer; transition:fill .12s; }}
#usmap path:hover {{ fill:#39424d; }}
#usmap path.sel {{ fill:var(--accent); }}
.mapcap {{ color:var(--ink-3); font-size:12px; text-align:center; padding:5px 0; }}
tr.strow {{ cursor:pointer; }}
tr.strow:hover td {{ background:#1e1e1e; }}
tr.strow.sel td {{ background:#20303f; }}
@media (max-width:900px) {{ .dash {{ grid-template-columns:1fr; }} }}
.tiles {{ display:grid; grid-template-columns:repeat(2,minmax(150px,1fr)); gap:14px; align-content:start; }}
.tile {{ background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:14px 16px; }}
.tile .lab {{ color:var(--muted); font-size:12.5px; }}
.tile .val {{ font-size:26px; font-weight:600; margin-top:2px; line-height:1.2; }}
.tile .sub {{ color:var(--ink-3); font-size:12px; margin-top:2px; }}

.legend {{ display:flex; gap:18px; font-size:12.5px; color:var(--ink-2); margin:26px 0 0; }}
.legend .sw {{ width:11px; height:11px; border-radius:3px; display:inline-block; margin-right:6px; }}

table {{ width:100%; border-collapse:collapse; margin-top:4px; }}
th {{ text-align:right; font-size:11.5px; letter-spacing:.06em; text-transform:uppercase;
  color:var(--ink-3); font-weight:600; padding:0 10px 8px; border-bottom:1px solid var(--line); }}
th.l {{ text-align:left; }}
td {{ padding:8px 10px; border-bottom:1px solid var(--line); font-size:14px; }}
td.num {{ text-align:right; font-variant-numeric:tabular-nums; color:var(--ink-2); }}
td.rank {{ color:var(--ink-3); width:26px; font-variant-numeric:tabular-nums; }}
td.ct {{ white-space:nowrap; }}
td.pop {{ white-space:nowrap; }}
.cw {{ display:flex; align-items:center; gap:10px; }}
.flag {{ width:30px; height:20px; object-fit:cover; border-radius:2px;
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
tr.total td {{ border-bottom:none; color:var(--muted); font-size:13px; padding-top:12px; }}

.note {{ color:var(--muted); font-size:12.5px; max-width:760px; }}
.refs {{ font-size:13px; color:var(--ink-2); max-width:760px; }}
.refs p {{ padding-left:2.2em; text-indent:-2.2em; margin:0 0 .8em; }}
.refs a {{ color:var(--accent); }}
@media (max-width:820px) {{
  td.share, td.chg {{ width:auto; }} .track {{ width:56px; }}
}}
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library</a> &nbsp;·&nbsp;
    <a href="us-cities.html">Cities</a></nav>
</header>

<h1>Every State by Population</h1>
<p class="stamp">Snapshot taken {SNAPSHOT}, using Census Bureau estimates for
July 1, 2025.</p>

<div class="dash">
<div class="tiles">
  <div class="tile"><div class="lab" id="l1">U.S. population</div>
    <div class="val" id="v1">{US_POP/1e6:.1f} million</div>
    <div class="sub" id="s1">{commas(US_POP)} in 2025</div></div>
  <div class="tile"><div class="lab" id="l2">Largest state</div>
    <div class="val" id="v2">{rows[0]['name']}</div>
    <div class="sub" id="s2">{commas(rows[0]['pop'])} people</div></div>
  <div class="tile"><div class="lab" id="l3">Fastest growth</div>
    <div class="val" id="v3">+{fastest['pct']:.1f}%</div>
    <div class="sub" id="s3">{fastest['name']} since 2020</div></div>
  <div class="tile"><div class="lab" id="l4">Steepest decline</div>
    <div class="val" id="v4">−{abs(steepest['pct']):.1f}%</div>
    <div class="sub" id="s4">{steepest['name']} since 2020</div></div>
</div>
<div class="mappanel">
  <svg id="usmap" viewBox="0 0 {USMAP['w']} {USMAP['h']}" role="img"
    aria-label="Map of the United States; the chosen state is highlighted">{MAP_PATHS}</svg>
  <div class="mapcap" id="mapcap">A state, clicked here or in the table, fills the tiles</div>
</div>
</div>

<div class="legend">
  <span><span class="sw" style="background:var(--up)"></span>Grew since 2020</span>
  <span><span class="sw" style="background:var(--down)"></span>Shrank since 2020</span>
</div>

<h2>The fifty states</h2>
{table_states}

<h2>Not a state</h2>
<p class="note" style="margin-bottom:6px">The District of Columbia is counted in
the national total above but has no rank here.</p>
{table_dc}

<h2>How to read this</h2>
<p class="note">All fifty states from largest to smallest, with each one's share
of the country and how far it has moved since the 2020 census. Growth runs right
on the change bars and decline runs left, on one scale for all fifty.
{len(grew)} states have grown since 2020 and {len(shrank)} have lost people.</p>
<p class="note">The green figure after a population is how many more people that
state has than the one ranked below it. Wyoming has none because nothing is
below it.</p>

<h2>Notes</h2>
<p class="note">Populations are Census Bureau estimates for July 1, 2025, and the
comparison year is the April 1, 2020 estimates base, which is why the 2020 figures
differ slightly from the published census counts. Shares are of the national total
including the District of Columbia. Texas added {commas(rows[1]['chg'])} people
since 2020, more than the entire population of any of the twelve smallest states.
Flags are the state flags, served by
<a href="https://flagcdn.com" style="color:var(--accent)">FlagCDN</a>.</p>

<h2>References</h2>
<div class="refs">
<p>U.S. Census Bureau. (2026). <em>Annual estimates of the resident population
for the United States, regions, states, and Puerto Rico: April 1, 2020 to July 1,
2025</em> (Vintage 2025 population estimates) [Data set]. Retrieved {SNAPSHOT},
from <a href="https://www.census.gov/programs-surveys/popest.html">https://www.census.gov/programs-surveys/popest.html</a></p>
<p>Map outlines: Natural Earth, 50m states and provinces.
<a href="https://www.naturalearthdata.com/">https://www.naturalearthdata.com/</a></p>
</div>
</div>
<script>
const DATA={DATA_JS};
const DEF=[
  ["U.S. population","{US_POP/1e6:.1f} million","{commas(US_POP)} in 2025"],
  ["Largest state","{rows[0]['name']}","{commas(rows[0]['pop'])} people"],
  ["Fastest growth","+{fastest['pct']:.1f}%","{fastest['name']} since 2020"],
  ["Steepest decline","−{abs(steepest['pct']):.1f}%","{steepest['name']} since 2020"]];
let sel=null;
const cap=document.getElementById('mapcap');
const fmtC=n=>n.toLocaleString('en-US');
const big=n=>n>=1e6?(n/1e6).toFixed(1)+' million':fmtC(n);
function setTiles(a){{ a.forEach((t,i)=>{{
  document.getElementById('l'+(i+1)).textContent=t[0];
  document.getElementById('v'+(i+1)).textContent=t[1];
  document.getElementById('s'+(i+1)).textContent=t[2]; }}); }}
function apply(cc){{
  sel=cc;
  document.querySelectorAll('#usmap path').forEach(p=>p.classList.toggle('sel',p.dataset.cc===cc));
  document.querySelectorAll('tr.strow').forEach(t=>t.classList.toggle('sel',t.dataset.cc===cc));
  if(!cc){{ setTiles(DEF); cap.textContent='A state, clicked here or in the table, fills the tiles'; return; }}
  const d=DATA[cc];
  setTiles([
    [d.n, big(d.pop), fmtC(d.pop)+(d.rank?' · No. '+d.rank+' of 50':' · not a state')],
    ["Share of the U.S.", d.share.toFixed(2)+'%', 'of {commas(US_POP)} people'],
    ["Change since 2020", (d.chg>0?'+':'−')+Math.abs(d.pct).toFixed(1)+'%',
     (d.chg>0?'+':'−')+fmtC(Math.abs(d.chg))+' people'],
    d.gap!=null?["Lead over next rank",'+'+fmtC(d.gap),'over '+d.nxt]
      :["Lead over next rank",'—', d.rank?'the smallest state':'listed outside the ranking']]);
  cap.textContent=d.n;
}}
document.querySelectorAll('tr.strow').forEach(t=>t.addEventListener('click',()=>{{
  apply(sel===t.dataset.cc?null:t.dataset.cc); }}));
document.querySelectorAll('#usmap path').forEach(p=>p.addEventListener('click',()=>{{
  if(DATA[p.dataset.cc]) apply(sel===p.dataset.cc?null:p.dataset.cc); }}));
window.__uss=()=>({{sel, tiles:[1,2,3,4].map(i=>document.getElementById('v'+i).textContent),
  mapStates:document.querySelectorAll('#usmap path').length}});
</script>
</body>
</html>
"""

OUT.write_text(HTML, encoding="utf-8")
print(f"wrote {OUT} ({len(HTML)} bytes): {len(rows)} states, "
      f"{len(grew)} grew, {len(shrank)} shrank; "
      f"fastest {fastest['name']} {fastest['pct']:+.2f}%, "
      f"steepest {steepest['name']} {steepest['pct']:+.2f}%")
