#!/usr/bin/env python3
"""Generate populous-countries.html, the Earth Right Now page: every country
and area the United Nations counts, its share of world population, and how
many people are born and die in it per day.

Each row carries its own paired bars, births above deaths, on one scale shared
by every country, so the balance between the two is visible in place rather
than in a separate chart. One shared scale across 237 rows means most bars are
short: that is the point, and the figure beside each bar carries the value.

Figures live in world_data.py. See its docstring for the retrieval route.

Usage: python3 build_populous.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from world_data import ROWS as SRC, WORLD, FLAG   # noqa: E402

OUT = Path(__file__).parent.parent / "populous-countries.html"

SNAPSHOT = "August 20, 2026"

DAYS = 365.25
C_BIRTH = "#3987e5"   # categorical slot 1, dark step
C_DEATH = "#d55181"   # categorical slot 5, dark step
C_SHARE = "#8a93a3"   # neutral meter fill, not a series hue
C_GAP = "#0ca30c"     # delta text token, not a series hue


def per_day(annual):
    return round(annual / DAYS)


def commas(n):
    return f"{n:,}"


def day_txt(n):
    """A country can average less than one a day. Say so rather than zero."""
    return commas(n) if n else "&lt;1"


def pct_txt(s):
    if s >= 0.1:
        return f"{s:.1f}%"
    if s >= 0.01:
        return f"{s:.2f}%"
    return "&lt;0.01%"


rows = []
for code, name, pop, births, deaths in SRC:
    rows.append(dict(
        code=code, name=name, cc=FLAG[code], pop=pop,
        share=pop / WORLD["pop"] * 100,
        b=per_day(births), d=per_day(deaths),
        net=per_day(births) - per_day(deaths),
    ))

# how many more people than the country one rank below; the last has none
for i, r in enumerate(rows):
    r["gap"] = r["pop"] - rows[i + 1]["pop"] if i + 1 < len(rows) else None

listed = sum(r["pop"] for r in rows)
share_listed = listed / WORLD["pop"] * 100
w_b, w_d = per_day(WORLD["births"]), per_day(WORLD["deaths"])
max_share = max(r["share"] for r in rows)
max_flow = max(max(r["b"], r["d"]) for r in rows)
shrinking = [r for r in rows if r["net"] < 0]
top10 = sum(r["pop"] for r in rows[:10]) / WORLD["pop"] * 100

# ---- the paired bars that live inside each row ----
VW, PLOT = 250, 150      # viewBox width, bar plot width
BH, GAP = 10, 3          # bar height, gap between the pair
VH = 2 + BH + GAP + BH + 2


def flow_svg(r):
    parts = [f'<svg class="flow" viewBox="0 0 {VW} {VH}" xmlns="http://www.w3.org/2000/svg" '
             f'role="img" aria-label="{r["name"]}: {commas(r["b"])} births and '
             f'{commas(r["d"])} deaths per day">']
    for j, (val, color, label) in enumerate(
            ((r["b"], C_BIRTH, "births"), (r["d"], C_DEATH, "deaths"))):
        w = max(2.0, val / max_flow * PLOT)
        y = 2 + j * (BH + GAP)
        parts.append(
            f'<g><title>{commas(val)} {label} per day</title>'
            f'<rect x="0" y="{y}" width="{w:.1f}" height="{BH}" rx="3" fill="{color}"/>'
            f'<rect x="0" y="{y}" width="3" height="{BH}" fill="{color}"/></g>')
        parts.append(f'<text x="{w + 6:.1f}" y="{y + BH - 1.5}" font-size="10.5" '
                     f'fill="#c3c2b7" font-variant-numeric="tabular-nums">{day_txt(val)}</text>')
    parts.append('</svg>')
    return "".join(parts)


HEAD = """<thead><tr>
  <th class="l" colspan="2">Country or area</th>
  <th>Population</th>
  <th class="l">Share of world</th>
  <th class="l">Births and deaths per day</th>
  <th>Net / day</th>
</tr></thead>"""


def tr(i, r):
    bar_w = r["share"] / max_share * 100
    net_txt = ("+" if r["net"] > 0 else "−" if r["net"] < 0 else "") + commas(abs(r["net"]))
    lead = (f' <span class="gap">(+{commas(r["gap"])})</span>'
            if r["gap"] is not None else "")
    return f"""<tr>
  <td class="rank">{i}</td>
  <td class="ct"><span class="cw"><img class="flag" src="https://flagcdn.com/w80/{r['cc']}.png"
      width="30" height="20" alt="Flag of {r['name']}"><span>{r['name']}</span></span></td>
  <td class="num pop">{commas(r['pop'])}{lead}</td>
  <td class="share"><span class="track"><span class="fill" style="width:{bar_w:.1f}%"></span></span><span class="pct">{pct_txt(r['share'])}</span></td>
  <td class="flow">{flow_svg(r)}</td>
  <td class="num">{net_txt}</td>
</tr>"""


def totals(label, block):
    p = sum(r["pop"] for r in block)
    b = sum(r["b"] for r in block)
    d = sum(r["d"] for r in block)
    n = b - d
    sign = "+" if n > 0 else "−"
    return (f'<tr class="total"><td></td><td>{label}</td>'
            f'<td class="num">{commas(p)}</td>'
            f'<td>{p / WORLD["pop"] * 100:.2f}% of the world</td>'
            f'<td>{commas(b)} births, {commas(d)} deaths</td>'
            f'<td class="num">{sign}{commas(abs(n))}</td></tr>')


body = "\n".join(tr(i + 1, r) for i, r in enumerate(rows))
table_all = (f'<table>\n{HEAD}\n<tbody>\n{body}\n'
             f'{totals("All " + str(len(rows)) + " together", rows)}\n'
             f'</tbody>\n</table>')

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Earth Right Now · Altazor</title>
<style>
:root {{ --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff;
        --ink-2:#c3c2b7; --ink-3:#898781;
        --births:{C_BIRTH}; --deaths:{C_DEATH}; --share:{C_SHARE}; }}
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
.stamp {{ color:var(--ink-3); font-size:12.5px; margin:0 0 22px; }}

.tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:14px; }}
.tile {{ background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:14px 16px; }}
.tile .lab {{ color:var(--muted); font-size:12.5px; }}
.tile .val {{ font-size:26px; font-weight:600; margin-top:2px; line-height:1.2; }}
.tile .sub {{ color:var(--ink-3); font-size:12px; margin-top:2px; }}

.legend {{ display:flex; gap:18px; font-size:12.5px; color:var(--ink-2);
  margin:26px 0 0; }}
.legend .sw {{ width:11px; height:11px; border-radius:3px; display:inline-block; margin-right:6px; }}

table {{ width:100%; border-collapse:collapse; margin-top:4px; }}
th {{ text-align:right; font-size:11.5px; letter-spacing:.06em; text-transform:uppercase;
  color:var(--ink-3); font-weight:600; padding:0 10px 8px; border-bottom:1px solid var(--line); }}
th.l {{ text-align:left; }}
td {{ padding:8px 10px; border-bottom:1px solid var(--line); font-size:14px; }}
td.num {{ text-align:right; font-variant-numeric:tabular-nums; color:var(--ink-2); }}
td.rank {{ color:var(--ink-3); width:34px; font-variant-numeric:tabular-nums; }}
td.pop {{ white-space:nowrap; }}
.gap {{ color:{C_GAP}; font-size:12.5px; font-variant-numeric:tabular-nums;
  margin-left:7px; }}
td.ct {{ white-space:nowrap; }}
.cw {{ display:flex; align-items:center; gap:10px; }}
img.flag {{ width:30px; height:20px; object-fit:cover; border-radius:2px;
  box-shadow:0 0 0 1px rgba(255,255,255,.14); display:block; flex:none; }}
td.share {{ width:190px; white-space:nowrap; }}
.track {{ display:inline-block; width:104px; height:9px; background:#242424; border-radius:5px;
  vertical-align:middle; overflow:hidden; }}
.fill {{ display:block; height:100%; background:var(--share); border-radius:0 4px 4px 0; }}
.pct {{ display:inline-block; width:60px; text-align:right; font-variant-numeric:tabular-nums;
  color:var(--ink-2); font-size:13px; margin-left:8px; }}
td.flow {{ width:266px; padding-top:6px; padding-bottom:6px; }}
svg.flow {{ display:block; width:100%; height:auto; }}
svg.flow rect {{ transition:opacity .12s; }}
svg.flow g:hover rect {{ opacity:.72; }}
tr.total td {{ border-bottom:none; color:var(--muted); font-size:13px; padding-top:12px; }}

.note {{ color:var(--muted); font-size:12.5px; max-width:760px; }}
.refs {{ font-size:13px; color:var(--ink-2); max-width:760px; }}
.refs p {{ padding-left:2.2em; text-indent:-2.2em; margin:0 0 .8em; }}
.refs a {{ color:var(--accent); }}
@media (max-width:820px) {{
  td.share, td.flow {{ width:auto; }} .track {{ width:56px; }}
}}
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library</a></nav>
</header>

<h1>Earth Right Now</h1>
<p class="stamp">Snapshot taken {SNAPSHOT}, using United Nations projections for 2026.</p>

<div class="tiles">
  <div class="tile"><div class="lab">World population</div>
    <div class="val">{WORLD['pop']/1e9:.2f} billion</div>
    <div class="sub">{commas(WORLD['pop'])} in 2026</div></div>
  <div class="tile"><div class="lab">Births per day</div>
    <div class="val">{commas(w_b)}</div>
    <div class="sub">worldwide</div></div>
  <div class="tile"><div class="lab">Deaths per day</div>
    <div class="val">{commas(w_d)}</div>
    <div class="sub">worldwide</div></div>
  <div class="tile"><div class="lab">Net growth per day</div>
    <div class="val">+{commas(w_b - w_d)}</div>
    <div class="sub">births minus deaths</div></div>
</div>

<div class="legend">
  <span><span class="sw" style="background:var(--births)"></span>Births per day</span>
  <span><span class="sw" style="background:var(--deaths)"></span>Deaths per day</span>
</div>

<h2>Every country and area</h2>
{table_all}

<h2>Notes</h2>
<p class="note">Every country and area the United Nations counts separately,
{len(rows)} of them, from India down to the Vatican. Population figures are
projections for 2026 under the medium variant, the middle of the range the UN
publishes. Daily figures are the projected births and deaths for the whole year
divided by 365.25, so they describe an average day rather than any particular
one; where that average is below one, the cell says so instead of showing zero.
The ten largest hold {top10:.1f} percent of the world between them.
In {len(shrinking)} of these {len(rows)} places the lower bar is longer, meaning
deaths outnumber births; all of them can still grow through migration, which
these columns do not count. The rows add to {commas(listed)}, which is
{share_listed:.2f} percent of the UN's own world figure. The remainder is a gap
in the source rather than a missing country: the UN's world record is larger
than the sum of the places it lists. Flags are served by
<a href="https://flagcdn.com" style="color:var(--accent)">FlagCDN</a>.</p>

<h2>References</h2>
<div class="refs">
<p>Our World in Data. (2024). <em>Population and demography</em> [Data set]. Based on
United Nations World Population Prospects (2024). Retrieved {SNAPSHOT}, from
<a href="https://ourworldindata.org/population-growth">https://ourworldindata.org/population-growth</a></p>
<p>United Nations, Department of Economic and Social Affairs, Population Division.
(2024). <em>World population prospects 2024: Summary of results</em>
(UN DESA/POP/2024/TR/NO. 9). United Nations.
<a href="https://population.un.org/wpp/">https://population.un.org/wpp/</a></p>
</div>
</div>
</body>
</html>
"""

OUT.write_text(HTML, encoding="utf-8")
print(f"wrote {OUT} ({len(HTML)} bytes): {len(rows)} countries and areas, "
      f"{len(shrinking)} shrinking, listed {listed:,} = {share_listed:.2f}% of the world")
