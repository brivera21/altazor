#!/usr/bin/env python3
"""Generate us-cities.html: the twenty most populous cities in the United
States, their share of the country, and how much each has grown or shrunk
since the 2020 census.

Figures are Census Bureau Vintage 2025 population estimates for July 1, 2025,
with the April 1, 2020 estimates base as the starting point.

Usage: python3 build_uscities.py
"""

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


HEAD = """<thead><tr>
  <th class="l" colspan="2">City</th>
  <th>Population</th>
  <th class="l">Share of the U.S.</th>
  <th class="l">Change since 2020</th>
  <th>People</th>
</tr></thead>"""


def tr(i, r):
    bar_w = r["share"] / max_share * 100
    chg_txt = ("+" if r["chg"] > 0 else "−") + commas(abs(r["chg"]))
    return f"""<tr>
  <td class="rank">{i}</td>
  <td class="ct"><span class="cw"><img class="flag" src="https://flagcdn.com/w80/us-{r['cc']}.png"
      width="30" height="20" alt="Flag of {r['state']}"><span>{r['name']}<span
      class="st">{r['state']}</span></span></span></td>
  <td class="num pop">{commas(r['pop'])} <span class="gap">(+{commas(r['gap'])})</span></td>
  <td class="share"><span class="track"><span class="fill" style="width:{bar_w:.1f}%"></span></span><span class="pct">{r['share']:.2f}%</span></td>
  <td class="chg">{chg_svg(r)}</td>
  <td class="num">{chg_txt}</td>
</tr>"""


def totals(label, block):
    p = sum(r["pop"] for r in block)
    b = sum(r["base"] for r in block)
    c = p - b
    sign = "+" if c > 0 else "−"
    return (f'<tr class="total"><td></td><td>{label}</td>'
            f'<td class="num">{commas(p)}</td>'
            f'<td>{p / US_POP * 100:.1f}% of the country</td>'
            f'<td>{sign}{abs(c / b * 100):.1f}% since 2020</td>'
            f'<td class="num">{sign}{commas(abs(c))}</td></tr>')


def table(block, start, label, total_over=None):
    body = "\n".join(tr(start + i, r) for i, r in enumerate(block))
    return (f'<table>\n{HEAD}\n<tbody>\n{body}\n'
            f'{totals(label, total_over if total_over is not None else block)}\n'
            f'</tbody>\n</table>')


table1 = table(first10, 1, "These ten together")
table2 = table(next10, 11, "All twenty together", total_over=rows)

grew = [r for r in rows if r["chg"] > 0]
shrank = [r for r in rows if r["chg"] < 0]

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
.lede {{ color:var(--muted); font-size:14.5px; margin:0 0 6px; max-width:730px; }}
.stamp {{ color:var(--ink-3); font-size:12.5px; margin:0 0 22px; }}

.tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:14px; }}
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
.st {{ display:block; color:var(--ink-3); font-size:11.5px; line-height:1.1; }}
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
  <nav class="site"><a href="library.html">&larr; Library</a></nav>
</header>

<h1>Most Populous Cities in the United States</h1>
<p class="stamp">Snapshot taken {SNAPSHOT}, using Census Bureau estimates for
July 1, 2025.</p>

<div class="tiles">
  <div class="tile"><div class="lab">U.S. population</div>
    <div class="val">{US_POP/1e6:.1f} million</div>
    <div class="sub">{commas(US_POP)} in 2025</div></div>
  <div class="tile"><div class="lab">Largest city</div>
    <div class="val">{rows[0]['name']}</div>
    <div class="sub">{commas(rows[0]['pop'])} people</div></div>
  <div class="tile"><div class="lab">Fastest growth</div>
    <div class="val">+{max(r['pct'] for r in rows):.1f}%</div>
    <div class="sub">{max(rows, key=lambda r: r['pct'])['name']} since 2020</div></div>
  <div class="tile"><div class="lab">Steepest decline</div>
    <div class="val">−{abs(min(r['pct'] for r in rows)):.1f}%</div>
    <div class="sub">{min(rows, key=lambda r: r['pct'])['name']} since 2020</div></div>
</div>

<div class="legend">
  <span><span class="sw" style="background:var(--up)"></span>Grew since 2020</span>
  <span><span class="sw" style="background:var(--down)"></span>Shrank since 2020</span>
</div>

<h2>The first ten</h2>
{table1}

<h2>The next ten</h2>
{table2}

<h2>How to read this</h2>
<p class="note">The twenty largest cities by population, with each one's share of
the country and how far it has moved since the 2020 census. Growth runs right on
the change bars and decline runs left, on one scale for all twenty. {len(grew)}
of them have grown since 2020 and {len(shrank)} have lost people.</p>
<p class="note">The green figure after a population is how many more people that
city has than the one ranked below it. Nashville is last on the list, so its
comparison is {NEXT_UP[0]} at rank twenty-one.</p>

<h2>Notes</h2>
<p class="note">Populations are Census Bureau estimates for July 1, 2025, and the
comparison year is the April 1, 2020 estimates base. These are city limits, not
metropolitan areas, which is why Phoenix outranks Philadelphia here and why no
figure for New York includes its suburbs. Indianapolis and Nashville are the
consolidated city and county governments minus the towns that stayed separate,
the balance figures the Census Bureau publishes for them. Flags are the state
flags, served by <a href="https://flagcdn.com" style="color:var(--accent)">FlagCDN</a>.</p>

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
</div>
</div>
</body>
</html>
"""

HTML = apa.apa_pass(HTML)
OUT.write_text(HTML, encoding="utf-8")
print(f"wrote {OUT} ({len(HTML)} bytes): {len(rows)} cities, "
      f"{len(grew)} grew, {len(shrank)} shrank")
