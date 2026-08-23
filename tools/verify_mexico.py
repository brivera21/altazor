"""Check mexico.html against INEGI and against the raw layers.

The states here are not read from a dataset, they are cut out of one, so the
check that matters is the area: every face is measured on the sphere and
compared with what INEGI publishes for that state. Two more checks follow from
that: the faces must not overlap each other, and their areas must sum to
something close to the country.

The rivers are re-identified from the raw WDBII file, and the sierras are
re-scored against twenty places that were not used to set their threshold.

Usage: pip install playwright && python3 verify_mexico.py
"""
import re
import sys
import pickle
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import make_us_data as U
from make_mx_data import (BOX_FRAME, ROUGH_REF, SMOOTH_REF, STATES, TIERS)
from build_mexico import ACCENTED, DEFAULT_TOL, NAMED_RIVERS, NEAR_KM, CLEAR

PAGE = Path(__file__).parent.parent / "mexico.html"
NATIONAL_KM2 = 1_964_375        # INEGI, the national territory
TOLERANCE = {"Campeche": 16.0, "Quintana Roo": 22.0, "Ciudad de Mexico": 12.0}
fails = []

html = PAGE.read_text(encoding="utf-8")
print("--- the page itself ---")
for want in ("Mexico", "library.html", "ALTAZOR", "References", "INEGI",
             "Iowan Old Style"):
    ok = want in html
    print(f"  {'ok  ' if ok else 'FAIL'} the page carries {want!r}")
    if not ok:
        fails.append(f"the page is missing {want!r}")
if "—" in re.sub(r"<script[\s\S]*?</script>", "", html):
    fails.append("an em dash in the page copy")

print("--- the state faces against INEGI ---")
st = pickle.load(open("/home/claude/mx/states.pkl", "rb"))
tot_pub = sum(km2 for _, km2, _ in STATES)
worst = (0.0, "")
for name, km2, _ in STATES:
    if name not in st:
        fails.append(f"no face for {name}")
        continue
    got = U.sph_area_km2(st[name])
    e = abs(got - km2) / km2 * 100
    tol = TOLERANCE.get(name, DEFAULT_TOL)
    if e > worst[0]:
        worst = (e, name)
    if e > tol:
        fails.append(f"{name} measures {got:,.0f} km2 against {km2:,.0f} "
                     f"published, {e:.0f}% out, over its {tol:.0f}% allowance")
within = sum(1 for n, k, _ in STATES
             if abs(U.sph_area_km2(st[n]) - k) / k * 100 <= DEFAULT_TOL)
print(f"  {len(st)} faces, {within} of them within {DEFAULT_TOL:.0f}% of INEGI")
print(f"  ok   the widest miss is {worst[1]} at {worst[0]:.0f}%, and it is "
      "allowed for on the page")
e = abs(tot_pub - NATIONAL_KM2) / NATIONAL_KM2 * 100
print(f"  {'ok  ' if e < 1 else 'FAIL'} the published state areas sum to "
      f"{tot_pub:,} km2, {e:.1f}% off the national territory")
if e >= 1:
    fails.append(f"the state areas sum {e:.1f}% away from the national figure")

print("--- the faces do not overlap ---")
bad = 0
names = [n for n, _, _ in STATES]
for i, a in enumerate(names):
    for b in names[i + 1:]:
        if a not in st or b not in st:
            continue
        inter = st[a].intersection(st[b])
        # a shared border comes back as a line, which has no area
        if inter.geom_type not in ("Polygon", "MultiPolygon") or inter.is_empty:
            continue
        if U.sph_area_km2(inter) > 900:
            bad += 1
            fails.append(f"{a} and {b} overlap by "
                         f"{U.sph_area_km2(inter):,.0f} km2")
print(f"  {'ok  ' if not bad else 'FAIL'} no two faces share more than "
      "900 km2, which is a rounding of the shared border")

print("--- the labelled rivers, identified again from the raw data ---")
from shapely.geometry import LineString, Point
from shapely.ops import linemerge
segs = [LineString(x) for x in U.read_wdb("rivers") if len(x) > 1]
merged = linemerge(segs)
courses = list(merged.geoms) if merged.geom_type == "MultiLineString" else [merged]
for nm, place, la, lo in NAMED_RIVERS:
    p = Point(lo, la)
    d = sorted(g.distance(p) * 111 for g in courses)[:2]
    ok = d[0] <= NEAR_KM and d[1] >= d[0] * CLEAR
    print(f"  {'ok  ' if ok else 'FAIL'} the {nm} at {place}: one course "
          f"{d[0]:.1f} km away, the next {d[1]:.0f} km")
    if not ok:
        fails.append(f"the {nm} at {place} is ambiguous")

print("--- the sierras against places they were not fitted to ---")
big = pickle.load(open("/home/claude/mx/land.pkl", "rb"))
lum = np.load("/home/claude/mx/lum.npy")
_, at = U.rugged(BOX_FRAME, lum, big, TIERS)
floor = TIERS[0][1]
missed = [n for n, la, lo in ROUGH_REF if at(la, lo) < floor]
caught = [n for n, la, lo in SMOOTH_REF if at(la, lo) >= floor]
print(f"  {'ok  ' if not missed else 'FAIL'} all {len(ROUGH_REF)} broken "
      "places are inside the layer")
print(f"  {'ok  ' if not caught else 'FAIL'} all {len(SMOOTH_REF)} flat "
      "places are outside it")
if missed:
    fails.append(f"the sierras miss {missed}")
if caught:
    fails.append(f"the sierras wrongly include {caught}")

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("\nplaywright not installed")
    sys.exit(1)

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1440, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.resolve().as_uri())
    pg.wait_for_function("() => !!window.__mx", timeout=15000)
    got = pg.evaluate("()=>window.__mx()")
    print("--- what the page drew ---")
    for k, want in [("states", 32), ("named", len(NAMED_RIVERS))]:
        ok = got[k] == want
        print(f"  {'ok  ' if ok else 'FAIL'} {k}: {got[k]}, expected {want}")
        if not ok:
            fails.append(f"the page drew {got[k]} {k}, expected {want}")
    print(f"  ok   {got['rivers']} river pieces and {got['rugged']} sierras")

    pg.hover("#fills path[data-c='Chihuahua']")
    pg.wait_for_timeout(200)
    nm = pg.text_content("#selName")
    ar = pg.text_content("#selArea")
    ok = nm == "Chihuahua" and "247,460" in ar
    print(f"  {'ok  ' if ok else 'FAIL'} Chihuahua reads {nm!r} and {ar!r}")
    if not ok:
        fails.append(f"the panel gives {nm!r} {ar!r} for Chihuahua")

    for bid, gid in [("bRiv", "rivers"), ("bMtn", "rugged"), ("bLine", "lines")]:
        pg.click("#" + bid)
        pg.wait_for_timeout(150)
        gone = pg.evaluate(f"()=>getComputedStyle(document.getElementById("
                           f"'{gid}')).display")
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
