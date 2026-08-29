"""Checks universe.html against its data and against its drawing.

  the data     the top bar sums to the Planck budget and the baryon bar to
               its census, within rounding
  the page     draws both bars, the wedge, and a card that answers
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_universe import TOP, BARYONS, GALAXY

fails = []
print("--- the data ---")
t = sum(p for _k, _l, p, *_r in TOP)
ok = abs(t - 99.8) < 0.5
print(f"  {'ok  ' if ok else 'FAIL'} the whole budget sums to {t} against "
      "Planck's 68.5 + 26.4 + 4.9")
if not ok: fails.append(f"top sums to {t}")
b = sum(p for _k, _l, p, *_r in BARYONS)
ok = abs(b - 99.7) < 0.5
print(f"  {'ok  ' if ok else 'FAIL'} the baryon census sums to {b}")
if not ok: fails.append(f"baryons sum to {b}")
ok = BARYONS[-1][0] == "gal"
print(f"  {'ok  ' if ok else 'FAIL'} galaxies sit at the right end of the baryon bar")
if not ok: fails.append("galaxies not rightmost")
g = sum(p for _k, _l, p, *_r in GALAXY)
ok = abs(g - 99.9) < 0.5
print(f"  {'ok  ' if ok else 'FAIL'} the galaxy budget sums to {g}")
if not ok: fails.append(f"galaxy sums to {g}")
s = (Path(__file__).parent.parent / "universe.html").read_text(encoding="utf-8")
for frag in ["10.1051/0004-6361/201833910", "10.1088/0004-637X/759/1/23",
             "10.1038/s41586-020-2300-2", "fast radio bursts"]:
    ok = frag in s
    print(f"  {'ok  ' if ok else 'FAIL'} the page carries '{frag}'")
    if not ok: fails.append(f"missing {frag}")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1280, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((Path(__file__).parent.parent / "universe.html").resolve().as_uri())
    pg.wait_for_selector("#uvsvg")
    n = pg.evaluate("()=>document.querySelectorAll('#uvsvg g[data-k]').length")
    ok = n >= 10
    print(f"  {'ok  ' if ok else 'FAIL'} {n} interactive segments and labels")
    if not ok: fails.append(f"{n} segments")
    card = pg.evaluate("()=>{show('miss');return document.getElementById('pct').textContent"
                       "+' '+document.getElementById('segTxt').textContent}")
    ok = card.startswith("29%")
    print(f"  {'ok  ' if ok else 'FAIL'} the missing-baryons card answers: '{card}'")
    if not ok: fails.append(f"card: {card}")
    gcard = pg.evaluate("()=>{show('stars');return document.getElementById('pct').textContent"
                        "+' | '+document.getElementById('srcTxt').textContent}")
    ok = gcard.startswith("65%") and "galaxy" in gcard
    print(f"  {'ok  ' if ok else 'FAIL'} the living-stars card answers: '{gcard[:70]}'")
    if not ok: fails.append(f"galaxy card: {gcard}")
    smbh = pg.evaluate("()=>{const r=document.querySelector('g[data-k=smbh] rect');"
                       "return r?+r.getAttribute('width'):-1}")
    ok = 0 < smbh < 3
    print(f"  {'ok  ' if ok else 'FAIL'} Sgr A* drawn as a hairline ({smbh}px)")
    if not ok: fails.append(f"smbh width {smbh}")
    if errs: fails.append(f"js errors: {errs}")
    br.close()
print()
if fails:
    for f in fails: print("FAIL", f)
    sys.exit(1)
print("everything squares")
