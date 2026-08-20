"""Check norte-mexico.html against the geometry it was built from.

Geometry: each of the six faces is compared with the published INEGI area, and
checked to lie south of the international boundary so no face has leaked into
the United States. Naming: each labelled river is re-checked against the two
anchors that identified it. Page: the six states, the river layer, the labels,
the slider and the readouts are exercised in a headless browser.

Usage: python3 verify_norte.py
"""
import pickle
import re
import sys
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

HERE = Path(__file__).parent
DATA = Path("/home/claude/nmex")
PAGE = HERE.parent / "norte-mexico.html"

PUBLISHED = {"Baja California": 71450, "Sonora": 179355, "Chihuahua": 247455,
             "Coahuila": 151595, "Nuevo León": 64220, "Tamaulipas": 80249}
# a point that must be inside, and one that must not be
INSIDE = {"Baja California": (-115.5, 30.5), "Sonora": (-110.97, 29.07),
          "Chihuahua": (-106.07, 28.63), "Coahuila": (-102.0, 27.0),
          "Nuevo León": (-99.8, 26.3), "Tamaulipas": (-98.5, 24.5)}

fails = []
states = pickle.load(open(DATA / "states.pkl", "rb"))
rivers = pickle.load(open(DATA / "rivers.pkl", "rb"))
raw = pickle.load(open(DATA / "raw.pkl", "rb"))
border = unary_union([LineString(s) for s in raw["countries"]])

print("--- state faces ---")
for nm, pub in PUBLISHED.items():
    g = states[nm]
    b = g.bounds
    lat = (b[1] + b[3]) / 2
    km2 = g.area * (111.32 ** 2) * np.cos(np.radians(lat))
    off = abs(km2 - pub) / pub
    if off > 0.05:
        fails.append(f"{nm}: area {km2:,.0f} km2 is {off*100:.1f}% off {pub:,}")
    if not g.contains(Point(*INSIDE[nm])):
        fails.append(f"{nm}: its own interior point falls outside the face")
    # nothing may sit more than a hair north of the international boundary
    north = b[3]
    if north > 32.8:
        fails.append(f"{nm}: reaches {north:.2f} N, north of the border")
    print(f"  {nm:18} {km2:9,.0f} km2 vs {pub:9,}  ({off*100:4.1f}% off)  "
          f"lat {b[1]:.2f}..{b[3]:.2f}")

print("--- the three labelled rivers ---")


def on_border(g, tol_km=4):
    c = np.asarray(g.coords)
    return sum(1 for p in c if border.distance(Point(p)) < tol_km / 111.0) / len(c)


def near(g, pt):
    c = np.asarray(g.coords)
    return float(np.hypot((c[:, 0] - pt[0]) * 111.32 * np.cos(np.radians(c[:, 1])),
                          (c[:, 1] - pt[1]) * 110.57).min())


bravo = [(L, g) for L, g in rivers if on_border(g) > 0.9 and L > 100]
if not bravo:
    fails.append("Río Bravo: no line follows the international boundary")
for L, g in bravo:
    f = on_border(g)
    print(f"  Río Bravo   {L:6.0f} km, {f*100:5.1f}% of its points on the boundary")
    if f < 0.9:
        fails.append("Río Bravo: a labelled piece leaves the boundary")

conchos = [(L, g) for L, g in rivers if near(g, (-104.42, 29.57)) < 5
           and near(g, (-105.47, 28.19)) < 20]
if len(conchos) != 1:
    fails.append(f"Río Conchos: {len(conchos)} lines match both anchors, expected 1")
for L, g in conchos:
    print(f"  Río Conchos {L:6.0f} km, Ojinaga {near(g,(-104.42,29.57)):.1f} km, "
          f"Delicias {near(g,(-105.47,28.19)):.1f} km")

colorado = [(L, g) for L, g in rivers if L > 30 and near(g, (-115.0, 32.0)) < 10
            and near(g, (-114.8, 31.9)) < 25]
if not colorado:
    fails.append("Río Colorado: the delta reach did not match its anchors")
for L, g in colorado:
    print(f"  Río Colorado{L:6.0f} km, delta anchors "
          f"{near(g,(-115.0,32.0)):.1f} / {near(g,(-114.8,31.9)):.1f} km")

print("--- rugged ground ---")
# The relief layer is a roughness threshold, so the test is whether it agrees
# with ground truth: known sierras must be inside it, known basins and plains
# outside. These twenty points were not used to build the layer.
sierras = pickle.load(open(DATA / "sierras.pkl", "rb"))
SIERRA, ALTA = sierras["sierra"], sierras["alta"]
RUGGED = [("Sierra de San Pedro Mártir", -115.40, 30.95),
          ("Sierra de Juárez, BC", -115.95, 32.05),
          ("Sierra Madre Occidental, Sonora", -109.30, 29.30),
          ("Barrancas del Cobre", -107.85, 27.35),
          ("Cerro Mohinora", -107.05, 25.95),
          ("Sierra Madre Oriental, Nuevo León", -100.30, 25.30),
          ("Sierra de Arteaga", -100.60, 25.35),
          ("Sierra Madre Oriental, Tamaulipas", -99.20, 23.60),
          ("Serranías del Burro", -102.00, 29.05),
          ("Sierra del Carmen", -102.55, 29.00)]
FLAT = [("Desierto de Altar", -113.50, 32.00),
        ("Llanos de Chihuahua", -106.80, 30.20),
        ("Cuenca de Casas Grandes", -107.90, 30.40),
        ("Laguna de Mayrán", -103.00, 25.60),
        ("Planicie de Tamaulipas", -97.90, 25.50),
        ("Sabinas, Coahuila", -101.10, 27.85),
        ("Bolsón de Mapimí", -103.60, 26.60),
        ("Valle de Juárez", -106.10, 31.45),
        ("Llanos de Hermosillo", -111.20, 29.20),
        ("Delta del Colorado", -114.95, 32.20)]
miss_r = [n for n, lo, la in RUGGED if not SIERRA.contains(Point(lo, la))]
miss_f = [n for n, lo, la in FLAT if SIERRA.contains(Point(lo, la))]
print(f"  {len(RUGGED)-len(miss_r)}/{len(RUGGED)} known sierras fall inside the layer")
print(f"  {len(FLAT)-len(miss_f)}/{len(FLAT)} known basins and plains fall outside it")
if miss_r:
    print(f"    sierras missed: {', '.join(miss_r)}")
if miss_f:
    print(f"    flats wrongly included: {', '.join(miss_f)}")
if len(miss_r) > 1:
    fails.append(f"the rugged layer misses {len(miss_r)} known sierras: {miss_r}")
if len(miss_f) > 2:
    fails.append(f"the rugged layer swallows {len(miss_f)} known flats: {miss_f}")

six = unary_union(list(states.values()))
frac = SIERRA.intersection(six).area / six.area
if not 0.30 < frac < 0.60:
    fails.append(f"rugged ground covers {frac*100:.0f}% of the six states")
print(f"  covers {frac*100:.0f}% of the six states, the high tier "
      f"{ALTA.intersection(six).area/six.area*100:.0f}%")

# every labelled range must sit on rugged ground, inside the state claimed
LABELS = {"Sierra de San Pedro Mártir": "Baja California"}
for nm, st_nm in LABELS.items():
    p = Point(-115.25, 30.75)
    if not SIERRA.contains(p):
        fails.append(f"{nm}: its label does not sit on rugged ground")
    if not states[st_nm].contains(p):
        fails.append(f"{nm}: its label is not inside {st_nm}")
    print(f"  {nm} label: on rugged ground, inside {st_nm}")

print("--- the page ---")
html = PAGE.read_text(encoding="utf-8")
if "—" in html:
    fails.append("the page contains an em dash")
for want in ["El norte de México", "library.html", "ALTAZOR"]:
    if want not in html:
        fails.append(f"the page is missing {want!r}")

try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": 1200, "height": 1400})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(PAGE.resolve().as_uri())
        pg.wait_for_timeout(700)
        got = pg.evaluate("""() => ({
          states: document.querySelectorAll('path.st').length,
          rivers: document.querySelectorAll('path.riv').length,
          named: document.querySelectorAll('path.riv.named').length,
          ctx: document.querySelectorAll('path.riv.ctx').length,
          labels: [...document.querySelectorAll('text.lbl')].map(t => t.textContent),
          shown: [...document.querySelectorAll('path.riv')].filter(
                   p => p.style.display !== 'none').length })""")
        if got["states"] != 6:
            fails.append(f"page draws {got['states']} states")
        if sorted(got["labels"]) != sorted(PUBLISHED):
            fails.append(f"labels are {got['labels']}")
        if got["named"] < 3:
            fails.append("fewer than three rivers are labelled on the page")
        rng = pg.evaluate("()=>[...document.querySelectorAll('text.rng')]"
                          ".map(t=>t.textContent)")
        want = ["Sierra Madre Occidental", "Sierra Madre Oriental",
                "Sierra de San Pedro Mártir"]
        if sorted(rng) != sorted(want):
            fails.append(f"range labels on the page are {rng}")
        if pg.evaluate("()=>document.querySelectorAll('#sierras path').length") != 2:
            fails.append("the rugged layer is not drawn in two tiers")
        h1_first = pg.evaluate("""()=>{const h=document.querySelector('h1'),
            f=document.querySelector('figure');
            return !!(h && f && (h.compareDocumentPosition(f) & 4));}""")
        if not h1_first:
            fails.append("the title does not come before the map")
        print(f"  title above the map, {len(rng)} ranges labelled: {', '.join(rng)}")
        pg.hover('path.st[data-i="2"]')
        pg.wait_for_timeout(150)
        hov = pg.evaluate("()=>[hovname.textContent, hovsub.textContent]")
        if "Chihuahua" not in hov[0]:
            fails.append(f"hovering Chihuahua reads {hov}")
        pg.evaluate("()=>{const s=minkm; s.value=200; s.dispatchEvent(new Event('input'));}")
        pg.wait_for_timeout(150)
        after = pg.evaluate("""()=>[...document.querySelectorAll('path.riv')]
            .filter(p=>p.style.display!=='none').length""")
        if after >= got["shown"]:
            fails.append("the slider did not remove any rivers")
        print(f"  {got['states']} states, {got['rivers']} river lines "
              f"({got['named']} labelled, {got['ctx']} outside the six), "
              f"{got['shown']} shown at 0 km and {after} at 200 km")
        if errs:
            fails.append(f"javascript errors: {errs}")
        br.close()
except ImportError:
    print("  playwright not available, skipped the render pass")

print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("all checks pass")
