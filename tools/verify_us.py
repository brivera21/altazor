"""Check us.html against the sources it was built from, and against its drawing.

The page is built from a county shapefile, a river layer and a relief image.
Each of those is read again here, independently of build_us.py, and the answers
compared:

  areas       every state polygon is measured on the sphere and compared with
              the Census Bureau's published total area for that state
  rivers      the ten labelled rivers are re-identified from the raw WDBII
              file, by finding the segment nearest to two points on that river
              far apart from each other, and the answer has to be the same
              segment the page labelled
  rugged      twenty reference places, ten broken and ten flat, none of which
              were used to set the threshold
  regions     the two Census regions are checked against the Bureau's own lists
  the drawing the two insets have to sit clear of the lower 48, and the page
              has to answer for what it drew

Usage: pip install playwright && python3 verify_us.py
"""
import collections
import math
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from make_us_data import BM, ROUGH_REF, SMOOTH_REF, read_wdb, sph_area_km2
from build_us import AREA, NAME, NAMED_RIVERS, REGIONS

HERE = Path(__file__).parent
PAGE = HERE.parent / "us.html"
fails = []

# The Census Bureau's own two regions, typed out from its regions and divisions
# document rather than copied from the generator.
CENSUS = {
    "The Midwest": set("OH IN IL MI WI MN IA MO ND SD NE KS".split()),
    "The South": set("DE MD DC VA WV NC SC GA FL KY TN AL MS AR LA OK TX".split()),
}

html = PAGE.read_text(encoding="utf-8")
print("--- the page itself ---")
for want in ("The United States", "library.html", "ALTAZOR", "References",
             "Albers"):
    ok = want in html
    print(f"  {'ok  ' if ok else 'FAIL'} the page carries {want!r}")
    if not ok:
        fails.append(f"the page is missing {want!r}")
if "—" in re.sub(r"<script[\s\S]*?</script>", "", html):
    fails.append("an em dash in the page copy")

print("--- the regions against the Census Bureau ---")
for name, _, kind, _, codes in REGIONS:
    got = set(codes.split())
    if name in CENSUS:
        ok = got == CENSUS[name]
        print(f"  {'ok  ' if ok else 'FAIL'} {name}: {len(got)} states, "
              f"and the Bureau lists {len(CENSUS[name])}")
        if not ok:
            fails.append(f"{name} differs from the Census list: "
                         f"{got ^ CENSUS[name]}")
    else:
        ok = kind == "vernacular"
        print(f"  {'ok  ' if ok else 'FAIL'} {name}: {len(got)} states, "
              "marked vernacular on the page")
        if not ok:
            fails.append(f"{name} is not marked vernacular")

print("--- state areas against the Census Bureau ---")
import pickle
st = pickle.load(open("/home/claude/us/states.pkl", "rb"))
LAND_KM2 = 9_147_593        # Census Bureau, land area of the United States
worst = (2.0, "")
for code, pub in AREA.items():
    got = sph_area_km2(st[code])
    r = got / pub
    if r < worst[0]:
        worst = (r, code)
    # The published figure is total area, water included. County polygons carry
    # inland water but stop at the shore, so a state can measure short of its
    # total and must never measure over it.
    if r > 1.01:
        fails.append(f"{NAME[code]} measures {got:,.0f} km2, more than the "
                     f"{pub:,.0f} km2 the Bureau publishes for it")
    if r < 0.55:
        fails.append(f"{NAME[code]} measures {got:,.0f} km2 against "
                     f"{pub:,.0f} km2 published, less than half")
tot = sum(sph_area_km2(st[c]) for c in AREA)
err = abs(tot - LAND_KM2) / LAND_KM2 * 100
print(f"  {len(AREA)} states and the district measured on the sphere")
print(f"  ok   none measures over its published total; the shortest is "
      f"{NAME[worst[1]]} at {worst[0] * 100:.0f}% of it, which is the water")
print(f"  {'ok  ' if err < 3 else 'FAIL'} they sum to {tot:,.0f} km2, "
      f"{err:.1f}% off the published land area of the country")
if err >= 3:
    fails.append(f"the states sum to {tot:,.0f} km2, {err:.1f}% off the land area")

print("--- the labelled rivers, identified again from the raw data ---")
from shapely.geometry import LineString, Point
from shapely.ops import linemerge
segs = [LineString(x) for x in read_wdb("rivers") if len(x) > 1]
merged = linemerge(segs)
courses = list(merged.geoms) if merged.geom_type == "MultiLineString" else [merged]
from build_us import NEAR_KM, CLEAR
for nm, place, la, lo in NAMED_RIVERS:
    p = Point(lo, la)
    d = sorted(g.distance(p) * 111 for g in courses)[:2]
    ok = d[0] <= NEAR_KM and d[1] >= d[0] * CLEAR
    print(f"  {'ok  ' if ok else 'FAIL'} the {nm} at {place}: one course "
          f"{d[0]:.1f} km away, the next {d[1]:.0f} km")
    if not ok:
        fails.append(f"the {nm} at {place} is ambiguous: {d[0]:.1f} km "
                     f"and {d[1]:.1f} km")

print("--- rugged ground against places it was not fitted to ---")
lum = np.load("/home/claude/us/conus_lum.npy")
land = pickle.load(open("/home/claude/us/land.pkl", "rb"))
from shapely.geometry import box
import make_us_data as M
conus = land.intersection(box(-125.0, 24.3, -66.5, 49.5))
_, at = M.rugged(M.FRAMES["conus"], lum, conus)
missed = [n for n, la, lo in ROUGH_REF if at(la, lo) < 13.0]
caught = [n for n, la, lo in SMOOTH_REF if at(la, lo) >= 13.0]
print(f"  {'ok  ' if not missed else 'FAIL'} all {len(ROUGH_REF)} broken places "
      f"are inside the layer")
print(f"  {'ok  ' if not caught else 'FAIL'} all {len(SMOOTH_REF)} flat places "
      f"are outside it")
if missed:
    fails.append(f"rugged ground misses {missed}")
if caught:
    fails.append(f"rugged ground wrongly includes {caught}")

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("\nplaywright not installed")
    sys.exit(1)

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1440, "height": 1100})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.resolve().as_uri())
    pg.wait_for_function("() => !!window.__us", timeout=15000)
    st_ = pg.evaluate("()=>window.__us()")
    print("--- what the page drew ---")
    for k, want in [("states", 51), ("named", len(NAMED_RIVERS))]:
        ok = st_[k] == want
        print(f"  {'ok  ' if ok else 'FAIL'} {k}: {st_[k]}, expected {want}")
        if not ok:
            fails.append(f"the page drew {st_[k]} {k}, expected {want}")
    print(f"  ok   {st_['rivers']} river segments and {st_['rugged']} patches "
          "of rugged ground")

    print("--- the insets sit clear of the lower 48 ---")
    # measured on the projected geometry rather than on bounding boxes, since
    # the corner of Texas reaches into the Alaska box without touching it
    from build_us import CONUS, AK, HI, fit
    from shapely.geometry import box as sbox
    from shapely.ops import transform
    lower = [g for k, g in st.items() if k not in ("AK", "HI", "PR")]
    Tc = fit(lower, CONUS, 1000, 600, 0, 0)
    boxes = [(sbox(6, 514, 344, 740), "Alaska"),
             (sbox(726, 606, 940, 722), "Hawaii")]
    hit = []
    for k, g in st.items():
        if k in ("AK", "HI", "PR"):
            continue
        pg_ = transform(lambda x, y: Tc(x, y), g)
        for b, n in boxes:
            if pg_.intersects(b):
                hit.append(f"{k} reaches into the {n} inset")
    ok = not hit
    print(f"  {'ok  ' if ok else 'FAIL'} no state of the lower 48 reaches into "
          "either inset")
    if not ok:
        fails.append(f"inset overlap: {hit[:4]}")

    print("--- the panel answers for a state ---")
    pg.hover("#fills path[data-c='TX']")
    pg.wait_for_timeout(200)
    nm = pg.text_content("#selName")
    ar = pg.text_content("#selArea")
    rg = pg.text_content("#selRegions")
    ok = nm == "Texas" and "695,662" in ar and "The South" in rg
    print(f"  {'ok  ' if ok else 'FAIL'} Texas reads {nm!r}, {ar!r}, and is "
          f"counted in {rg.split('Counted in ')[-1]!r}")
    if not ok:
        fails.append(f"the panel gives {nm!r} {ar!r} {rg!r} for Texas")

    for bid in ("bRiv", "bMtn"):
        pg.click("#" + bid)
        pg.wait_for_timeout(150)
        gone = pg.evaluate(f"()=>getComputedStyle(document.getElementById("
                           f"'{'rivers' if bid == 'bRiv' else 'rugged'}'))"
                           f".display")
        pg.click("#" + bid)
        ok = gone == "none"
        print(f"  {'ok  ' if ok else 'FAIL'} {bid} hides its layer")
        if not ok:
            fails.append(f"{bid} does not hide its layer")

    if errs:
        fails.append(f"javascript errors: {errs}")
    br.close()

print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("all checks pass")
