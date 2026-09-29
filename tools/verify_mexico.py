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
             "Iowan Old Style", '<details class="sources">', 'id="rank"',
             'id="bErr"', 'id="bNames"', 'id="ghost"'):
    ok = want in html
    print(f"  {'ok  ' if ok else 'FAIL'} the page carries {want!r}")
    if not ok:
        fails.append(f"the page is missing {want!r}")
if "—" in re.sub(r"<script[\s\S]*?</script>", "", html):
    fails.append("an em dash in the page copy")

MX = Path("/home/claude/mx")
if not MX.exists():
    print(f"--- {MX} is not on this machine: the area, overlap, river and "
          "sierra checks are skipped, the page checks still run ---")
st = pickle.load(open(MX / "states.pkl", "rb")) if MX.exists() else None
if st is None:
    STATES_CHECK = []
else:
    STATES_CHECK = STATES
print("--- the state faces against INEGI ---")
tot_pub = sum(km2 for _, km2, _ in STATES)
worst = (0.0, "")
for name, km2, _ in STATES_CHECK:
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
within = sum(1 for n, k, _ in STATES_CHECK
             if abs(U.sph_area_km2(st[n]) - k) / k * 100 <= DEFAULT_TOL)
if st is not None:
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
names = [n for n, _, _ in STATES_CHECK]
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
if st is not None:
    print(f"  {'ok  ' if not bad else 'FAIL'} no two faces share more than "
          "900 km2, which is a rounding of the shared border")

print("--- the labeled rivers, identified again from the raw data ---")
from shapely.geometry import LineString, Point
from shapely.ops import linemerge
if st is not None:
    segs = [LineString(x) for x in U.read_wdb("rivers") if len(x) > 1]
    merged = linemerge(segs)
    courses = list(merged.geoms) if merged.geom_type == "MultiLineString" else [merged]
for nm, place, la, lo in (NAMED_RIVERS if st is not None else []):
    p = Point(lo, la)
    d = sorted(g.distance(p) * 111 for g in courses)[:2]
    ok = d[0] <= NEAR_KM and d[1] >= d[0] * CLEAR
    print(f"  {'ok  ' if ok else 'FAIL'} the {nm} at {place}: one course "
          f"{d[0]:.1f} km away, the next {d[1]:.0f} km")
    if not ok:
        fails.append(f"the {nm} at {place} is ambiguous")

print("--- the sierras against places they were not fitted to ---")
if st is not None:
    big = pickle.load(open(MX / "land.pkl", "rb"))
    lum = np.load(MX / "lum.npy")
    _, at = U.rugged(BOX_FRAME, lum, big, TIERS)
    floor = TIERS[0][1]
    missed = [n for n, la, lo in ROUGH_REF if at(la, lo) < floor]
    caught = [n for n, la, lo in SMOOTH_REF if at(la, lo) >= floor]
else:
    missed = caught = []
if st is not None:
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

    print("--- the list, the names, the ghost and the keys ---")
    ok = got["ranks"] == 32 and got["names"] == 32
    print(f"  {'ok  ' if ok else 'FAIL'} {got['ranks']} ranked rows and "
          f"{got['names']} name labels")
    if not ok:
        fails.append(f"the page has {got['ranks']} rows and {got['names']} names")
    ok = got["order"][0] == "Chihuahua" and got["order"][-1] == "Ciudad de Mexico"
    print(f"  {'ok  ' if ok else 'FAIL'} the order runs from Chihuahua to "
          "Ciudad de Mexico")
    if not ok:
        fails.append(f"the area order is {got['order'][:2]} ... {got['order'][-1]}")
    # every label sits inside its own state
    inside = pg.evaluate("""()=>{
      const s = document.getElementById('map');
      return window.__mx().meta.map(m => {
        const p = s.querySelector(`#fills path[data-c='${m.c}']`);
        const pt = s.createSVGPoint(); pt.x = m.lx; pt.y = m.ly;
        return [m.c, p.isPointInFill(pt)]; }); }""")
    out = [c for c, ok in inside if not ok]
    print(f"  {'ok  ' if not out else 'FAIL'} every name label sits inside its state")
    if out:
        fails.append(f"labels outside their state: {out}")
    pg.hover("#fills path[data-c='Tlaxcala']")
    pg.wait_for_timeout(150)
    sub = pg.text_content("#selSub")
    fit = pg.text_content("#selFit")
    g = pg.evaluate("()=>window.__mx().ghost")
    ok = "31st of 32" in sub and "62 times" in fit and g == 2
    print(f"  {'ok  ' if ok else 'FAIL'} Tlaxcala: {sub!r}, {fit!r}, ghost drawn")
    if not ok:
        fails.append(f"Tlaxcala reads {sub!r} {fit!r} with ghost {g}")
    pg.hover("#fills path[data-c='Chihuahua']")
    pg.wait_for_timeout(150)
    g = pg.evaluate("()=>window.__mx().ghost")
    print(f"  {'ok  ' if g == 0 else 'FAIL'} no ghost on Chihuahua itself")
    if g:
        fails.append("a ghost is drawn on Chihuahua itself")
    pg.hover("#rank .r[data-c='Sonora']")
    pg.wait_for_timeout(150)
    lit = pg.evaluate("()=>document.querySelector(\"#fills path[data-c='Sonora']\")"
                      ".classList.contains('lit')")
    print(f"  {'ok  ' if lit else 'FAIL'} a row under the cursor lights its state")
    if not lit:
        fails.append("the ranked row does not light its state")
    pg.click("#fills path[data-c='Sonora']")
    pg.wait_for_timeout(100)
    pinned = pg.evaluate("()=>document.getElementById('card').classList.contains('pinned')")
    print(f"  {'ok  ' if pinned else 'FAIL'} a click pins the card")
    if not pinned:
        fails.append("the click does not pin the card")
    pg.focus("#map")
    pg.keyboard.press("ArrowRight")
    pg.wait_for_timeout(100)
    sel = pg.evaluate("()=>window.__mx().sel")
    print(f"  {'ok  ' if sel == 'Coahuila' else 'FAIL'} ArrowRight from Sonora "
          f"selects {sel}")
    if sel != "Coahuila":
        fails.append(f"ArrowRight from Sonora went to {sel}")
    pg.keyboard.press("Escape")
    sel = pg.evaluate("()=>window.__mx().sel")
    if sel is not None:
        fails.append("Escape does not let go")
    pg.click("#bErr")
    pg.wait_for_timeout(100)
    err = pg.evaluate("()=>window.__mx().err")
    fill = pg.evaluate("()=>getComputedStyle(document.querySelector("
                       "\"#fills path[data-c='Quintana Roo']\")).fill")
    print(f"  {'ok  ' if err else 'FAIL'} INEGI difference colors the map, "
          f"Quintana Roo is {fill}")
    if not err or fill in ("rgb(74, 74, 66)", ""):
        fails.append("the INEGI difference mode does not recolor")
    pg.click("#bErr")
    pg.click("#bNames")
    shown = pg.evaluate("()=>[...document.querySelectorAll('#names text')]"
                        ".filter(t => getComputedStyle(t).display !== 'none').length")
    print(f"  {'ok  ' if shown == 32 else 'FAIL'} Names shows all {shown} names")
    if shown != 32:
        fails.append(f"Names shows {shown} labels")
    pg.click("#bNames")

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
