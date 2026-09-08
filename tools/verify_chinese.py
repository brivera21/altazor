#!/usr/bin/env python3
"""Check chinese.html: the arithmetic, the dictionary and the drawing.

The claims on this page are all arithmetic on a frequency list, so they
can be checked against the list rather than taken on trust: the shares
sum to the cumulative column, the cumulative column ends where it should,
the curve read off the chart matches the table, and the headline coverage
figures in the copy match the data.

Usage: python3 verify_chinese.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "tools" / "data" / "chinese.json").read_text())
PAGE = ROOT / "chinese.html"
fails, notes = [], []


def ck(ok, msg):
    (notes if ok else fails).append(msg)


CH, WD = D["chars"], D["words"]
print(f"  {len(CH)} characters and {len(WD)} words in the grid, "
      f"{D['nchar']} and {D['nword']} counted")

# --- the arithmetic ------------------------------------------------------
for name, rows in (("characters", CH), ("words", WD)):
    ck(all(rows[i][4] <= rows[i + 1][4] + 1e-9 for i in range(len(rows) - 1)),
       f"{name}: the cumulative column never falls")
    ck(all(rows[i][3] >= rows[i + 1][3] - 1e-9 for i in range(len(rows) - 1)),
       f"{name}: the list is in order of frequency")
    run = 0.0
    worst = 0.0
    for r in rows:
        run += r[3]
        worst = max(worst, abs(run - r[4]))
    ck(worst < 0.06,
       f"{name}: the shares add up to the cumulative column, off by at most "
       f"{worst:.3f} points")
    ck(all(r[1] and r[2] for r in rows),
       f"{name}: every entry has pinyin and a gloss")
    ck(all(re.fullmatch(r"[一-鿿]+", r[0]) for r in rows),
       f"{name}: every entry is written in Han characters")

ck(all(len(r[0]) == 1 for r in CH), "the character grid holds single characters")
ck(any(len(r[0]) > 1 for r in WD), "the word grid holds multi-character words")
ck(len({r[0] for r in CH}) == len(CH), "no character appears twice")
ck(len({r[0] for r in WD}) == len(WD), "no word appears twice")

# --- the curves ----------------------------------------------------------
for key, rows in (("ccurve", CH), ("wcurve", WD)):
    c = D[key]
    ck(c[0][0] == 1, f"{key}: starts at rank 1")
    ck(all(c[i][0] < c[i + 1][0] for i in range(len(c) - 1)),
       f"{key}: ranks increase")
    ck(all(c[i][1] <= c[i + 1][1] + 1e-9 for i in range(len(c) - 1)),
       f"{key}: coverage never falls")
    ck(99.0 <= c[-1][1] <= 100.001,
       f"{key}: ends at {c[-1][1]:.2f} per cent")
    # the curve and the table are the same numbers
    at = {r: v for r, v in c}
    off = max((abs(at[r] - rows[r - 1][4]) for r in at if r <= len(rows)),
              default=0)
    ck(off < 0.02, f"{key}: the curve matches the table, off by at most "
                   f"{off:.4f} points")

ck(D["scurve"][-1][1] > 99.0, "the spoken curve ends at 100 per cent")
# dialogue leans on fewer characters than writing does, at every depth
lean = all(next(v for r, v in D["scurve"] if r >= k)
           >= next(v for r, v in D["ccurve"] if r >= k)
           for k in (10, 100, 500, 1000))
ck(lean, "dialogue concentrates on fewer characters than writing at every "
         "depth, which is what the comparison view claims")

# --- the copy matches the data -------------------------------------------
html = PAGE.read_text(encoding="utf-8")
marks = dict(D["marks"]["c"])
for rank, said in ((100, "41.8"), (1000, "89.1"), (2500, "98.5")):
    ck(abs(marks[rank] - float(said)) < 0.05,
       f"the copy's {said} per cent at {rank} characters matches the data "
       f"({marks[rank]})")
    ck(said in html, f"the page states {said} per cent")
ck("—" not in re.sub(r"<script[\s\S]*?</script>", "", html),
   "no em dash in the page copy")
for word in ("Jun Da", "OpenSubtitles", "CC-CEDICT", "Unihan"):
    ck(word in html, f"the page names its source: {word}")

# --- the page ------------------------------------------------------------
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("playwright is required for the rendering checks")
    sys.exit(2)

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1240, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_timeout(700)
    for view, btn, n in (("char", "#vChar", len(CH)), ("word", "#vWord", len(WD))):
        pg.click(btn)
        pg.wait_for_timeout(350)
        tiles = pg.eval_on_selector_all("#grid .t", "es=>es.length")
        ck(tiles == n, f"{view}: {tiles} tiles drawn")
        ck(pg.eval_on_selector_all("#curve svg path", "es=>es.length") >= 1,
           f"{view}: the curve is drawn")
        # the slider dims what it drops and the readout agrees
        pg.eval_on_selector("#rank", "e=>{e.value=500;"
                            "e.dispatchEvent(new Event('input'))}")
        pg.wait_for_timeout(300)
        lit = pg.eval_on_selector_all("#grid .t:not(.past)", "es=>es.length")
        ck(lit == 500, f"{view}: the slider lights exactly 500 tiles ({lit})")
        said = pg.inner_text("#rankTxt")
        want = (WD if view == "word" else CH)[499][4]
        m = re.search(r"([\d.]+)%", said)
        ck(m and abs(float(m.group(1)) - want) < 0.06,
           f"{view}: the readout says {said!r}, the table says {want}")
        pg.eval_on_selector("#rank", "e=>{e.value=e.max;"
                            "e.dispatchEvent(new Event('input'))}")
        pg.wait_for_timeout(200)

    pg.click("#vBoth")
    pg.wait_for_timeout(400)
    ck(pg.eval_on_selector("#rankWrap", "e=>getComputedStyle(e).display")
       == "none", "the rank slider is put away where it means nothing")
    heads = pg.eval_on_selector_all("#grid .gh", "es=>es.map(e=>e.textContent)")
    ck(len(heads) == 2, f"the comparison view labels both groups: {heads}")
    first = pg.eval_on_selector("#grid .t", "e=>e.dataset.i")
    pg.hover("#grid .t")
    pg.wait_for_timeout(200)
    body = pg.inner_text("#rowsTxt")
    ck("Rank in writing" in body and "Rank in dialogue" in body,
       "the card gives both ranks in the comparison view")

    pg.click("#vChar")
    pg.wait_for_timeout(300)
    pg.fill("#q", "water")
    pg.wait_for_timeout(300)
    found = pg.eval_on_selector_all("#grid .t", "es=>es.length")
    ck(0 < found < len(CH), f"searching a gloss narrows the grid to {found}")
    pg.fill("#q", "")
    pg.wait_for_timeout(250)
    pg.hover("#grid .t")
    pg.wait_for_timeout(200)
    ck(pg.inner_text("#bigTxt") == CH[0][0],
       "hovering the first tile names the commonest character")
    ck(not errs, f"no script errors ({errs[:1]})")
    br.close()

for n in notes:
    print("  ok  ", n)
if fails:
    print()
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print(f"\n{len(notes)} checks passed")
