"""Checks world-champions.html against its data and against its drawing.

  the data     the reigns tile the axis with no gap or overlap from 1886 to
               the open end, the interregnum sits at 1946-1948, Botvinnik
               reigns three times and Alekhine twice, and one color belongs
               to one champion
  the page     draws every reign, the five bands, the legend, and the card

Usage: python3 verify_champions.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_champions import R, COLORS, NOW

fails = []

print("--- the data ---")
ends = [(a, b if b else NOW) for _n, _c, a, b, *_ in R]
tiled = all(ends[i][1] == ends[i+1][0] for i in range(len(ends)-1))
ok = tiled and ends[0][0] == 1886
print(f"  {'ok  ' if ok else 'FAIL'} the {len(R)} reigns tile the axis from 1886 "
      "with no gap or overlap")
if not ok: fails.append(f"reigns do not tile: {ends}")

gap = [r for r in R if r[8] is None]
ok = len(gap) == 1 and gap[0][2] == 1946 and gap[0][3] == 1948
print(f"  {'ok  ' if ok else 'FAIL'} the interregnum is the one 1946-1948 gap")
if not ok: fails.append(f"interregnum wrong: {gap}")

from collections import Counter
c = Counter(n for n, *_ in R)
ok = c["Mikhail Botvinnik"] == 3 and c["Alexander Alekhine"] == 2 \
     and all(v == 1 for k, v in c.items()
             if k not in ("Mikhail Botvinnik", "Alexander Alekhine"))
print(f"  {'ok  ' if ok else 'FAIL'} Botvinnik reigns three times, Alekhine twice, "
      "everyone else once")
if not ok: fails.append(f"reign counts: {c}")

vals = list(COLORS.values())
ok = len(vals) == len(set(vals))
print(f"  {'ok  ' if ok else 'FAIL'} one color per champion, none repeated")
if not ok: fails.append("repeated colors")

cur = [r for r in R if r[3] is None]
ok = len(cur) == 1 and cur[0][0] == "Gukesh Dommaraju" and cur[0][2] == 2024
print(f"  {'ok  ' if ok else 'FAIL'} the open reign is Gukesh's, from 2024")
if not ok: fails.append(f"current champion: {cur}")

s = (Path(__file__).parent.parent / "world-champions.html").read_text(encoding="utf-8")
for frag in ["Steinitz", "Gukesh", "List_of_world_chess_champions",
             "fide.com", "1937-2025"]:
    ok = frag in s
    print(f"  {'ok  ' if ok else 'FAIL'} the page carries '{frag}'")
    if not ok: fails.append(f"missing '{frag}'")

print("--- the drawing ---")
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("playwright is not installed"); sys.exit(1)
with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1280, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("**wikipedia.org/**", lambda r: r.abort())
    pg.goto((Path(__file__).parent.parent / "world-champions.html").resolve().as_uri())
    pg.wait_for_selector("#tlsvg")
    nr = pg.evaluate("()=>document.querySelectorAll('#tlsvg rect[data-ch]').length")
    ng = pg.evaluate("()=>document.querySelectorAll('#tlsvg g[data-ch]').length")
    ok = nr == 22 and ng == 22
    print(f"  {'ok  ' if ok else 'FAIL'} 22 reign spans and 22 labels ({nr}, {ng})")
    if not ok: fails.append(f"spans {nr}, labels {ng}")
    nb = pg.evaluate("()=>document.querySelectorAll('#tlsvg rect[data-era]').length")
    nl = pg.evaluate("()=>document.getElementById('legend').children.length")
    ok = nb == 5 and nl == 18
    print(f"  {'ok  ' if ok else 'FAIL'} five bands, eighteen champions in the "
          f"legend ({nb}, {nl})")
    if not ok: fails.append(f"bands {nb}, legend {nl}")
    card = pg.evaluate(
        "()=>{showChamp(0);return document.getElementById('chTxt').textContent"
        "+' | '+document.getElementById('reignTxt').textContent}")
    ok = "Steinitz" in card and "1886 to 1894" in card
    print(f"  {'ok  ' if ok else 'FAIL'} the card responds: '{card}'")
    if not ok: fails.append(f"card: {card}")
    card = pg.evaluate(
        "()=>{showChamp(REIGNS.length-1);"
        "return document.getElementById('reignTxt').textContent}")
    ok = "today" in card
    print(f"  {'ok  ' if ok else 'FAIL'} the open reign reads to today: '{card}'")
    if not ok: fails.append(f"open reign: {card}")
    pg.evaluate("()=>{view=clampView(1955,1965);render()}")
    n2 = pg.evaluate("()=>document.querySelectorAll('#tlsvg rect[data-ch]').length")
    ok = 3 <= n2 <= 8
    print(f"  {'ok  ' if ok else 'FAIL'} zooming to the Botvinnik years leaves "
          f"{n2} spans")
    if not ok: fails.append(f"zoom leaves {n2}")
    if errs: fails.append(f"javascript errors: {errs}")
    br.close()

print()
if fails:
    for f in fails: print("FAIL", f)
    sys.exit(1)
print("everything squares")
