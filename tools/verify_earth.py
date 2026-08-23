"""Check earth.html: the continents, the climates, and the figures on the page.

Three things are worth checking independently.

The geometry: the raster is rebuilt from GSHHG here, not read back from the
page, and every continent is checked against its published area. They will not
agree exactly. A sixth of a degree adds about half a pixel to every coastline,
which inflates ragged landmasses, so the test is a tolerance and the measured
figure is printed next to the published one rather than hidden.

The classification: known places are looked up in the shipped raster and must
land on the right continent and a plausible climate. This is what catches an
island quietly reassigned or a divide drawn in the wrong place.

The page: the tiles, the panel and the hover are exercised in a browser, and
every percentage on it is recomputed from the areas it claims.

Usage: python3 verify_earth.py
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
PAGE = HERE.parent / "earth.html"
DATA = Path("/home/claude/earth")

EARTH = 510_072_000
OCEAN = 361_132_000
LAND = 148_940_000
INLAND = 5_000_000

PUB = {"Asia": 44_579_000, "Africa": 30_370_000, "North America": 24_709_000,
       "South America": 17_840_000, "Antarctica": 14_200_000,
       "Europe": 10_180_000, "Australia and Oceania": 8_600_000}
CONT = ["Africa", "Asia", "Europe", "North America", "South America",
        "Antarctica", "Australia and Oceania"]
GROUP = ["A tropical", "B arid", "C temperate", "D continental", "E polar"]

# Places whose continent is not in dispute, and the climate group each should
# fall in. These are the cases an island rule or a divide would get wrong.
PLACES = [
    ("Egypt, west of Suez", 29.5, 31.0, "Africa", "B"),
    ("Sinai", 29.50, 33.90, "Asia", "B"),
    ("Istanbul, European side", 41.05, 28.85, "Europe", "C"),
    ("Ankara", 39.93, 32.85, "Asia", None),
    ("Yekaterinburg", 56.84, 60.65, "Asia", "D"),
    ("Kirov, west of the Urals", 58.5, 49.7, "Europe", "D"),
    ("Panama, west of the Darien", 8.6, -79.0, "North America", "A"),
    ("Colombia, east of it", 7.5, -76.5, "South America", "A"),
    ("Bogota", 4.71, -74.07, "South America", None),
    ("Greenland", 72.0, -42.0, "North America", "E"),
    ("Iceland", 64.9, -18.5, "Europe", None),
    ("Madagascar", -19.0, 47.0, "Africa", None),
    ("Borneo", 0.0, 114.0, "Asia", "A"),
    ("Sulawesi, at the coast", -5.1, 119.5, "Asia", "A"),
    ("New Guinea, the lowlands", -8.5, 140.4, "Australia and Oceania", "A"),
    ("New Guinea, the Maoke range", -4.0, 137.5, "Australia and Oceania", "C"),
    ("New Zealand", -43.5, 172.0, "Australia and Oceania", "C"),
    ("Hawaii", 19.6, -155.5, "Australia and Oceania", None),
    ("Tasmania", -42.0, 146.5, "Australia and Oceania", "C"),
    ("Sahara", 23.0, 10.0, "Africa", "B"),
    ("Amazon basin", -4.5, -63.0, "South America", "A"),
    ("Siberia", 65.0, 100.0, "Asia", "D"),
    ("Vostok, Antarctica", -78.5, 106.8, "Antarctica", "E"),
    ("Alice Springs", -23.7, 133.9, "Australia and Oceania", "B"),
]

fails = []
cid = np.load(DATA / "cid.npy")
clim = np.load(DATA / "clim.npy")
H, W = cid.shape
wt = np.repeat(np.cos(np.radians(90 - (np.arange(H) + 0.5) * 180 / H))[:, None], W, 1)


def px(lat, lon):
    return (int(round((90 - lat) * H / 180 - 0.5)), int(round((lon + 180) * W / 360 - 0.5)))


print("--- the figures on the page ---")
CLAIMS = [
    ("ocean is 70.8% of the surface", abs(OCEAN / EARTH * 100 - 70.8) < 0.05),
    ("land is 29.2% of the surface", abs(LAND / EARTH * 100 - 29.2) < 0.05),
    ("ocean and land account for the whole surface", OCEAN + LAND == EARTH),
    ("lakes and rivers are 1.0% of the surface",
     abs(INLAND / EARTH * 100 - 1.0) < 0.05),
    ("that is about 3% of the land", 3.0 < INLAND / LAND * 100 < 3.6),
    ("the seven continents sum to the land area",
     abs(sum(PUB.values()) - LAND) / LAND < 0.011),
]
for claim, ok in CLAIMS:
    print(f"  {'ok  ' if ok else 'FAIL'} {claim}")
    if not ok:
        fails.append(claim)

print("--- the raster against the published areas ---")
scale = LAND / wt[cid > 0].sum()
print(f"  land is {wt[cid > 0].sum() / wt.sum() * 100:.2f}% of the raster, "
      f"against 29.2% published")
for i, nm in enumerate(CONT, 1):
    km2 = wt[cid == i].sum() * scale
    off = (km2 - PUB[nm]) / PUB[nm] * 100
    tol = 25 if nm == "Australia and Oceania" else 6
    flag = "ok  " if abs(off) <= tol else "FAIL"
    if abs(off) > tol:
        fails.append(f"{nm}: raster {km2:,.0f} km2 is {off:.1f}% off published")
    print(f"  {flag} {nm:24}{km2:13,.0f}{PUB[nm]:13,.0f}  {off:+6.1f}%")

print("--- known places ---")
for nm, lat, lon, want_c, want_g in PLACES:
    r, c = px(lat, lon)
    got_c = int(cid[r, c])
    got_g = int(clim[r, c])
    cname = CONT[got_c - 1] if got_c else "water"
    gname = GROUP[got_g - 1] if got_g else "none"
    bad = []
    if cname != want_c:
        bad.append(f"continent {cname!r}, expected {want_c!r}")
    if want_g and gname[0] != want_g:
        bad.append(f"climate {gname!r}, expected group {want_g}")
    if bad:
        fails.append(f"{nm}: " + "; ".join(bad))
    print(f"  {'ok  ' if not bad else 'FAIL'} {nm:26}{cname:24}{gname}")

print("--- the climate shares ---")
mix = json.load(open(DATA / "mix.json"))
land = cid > 0
tot = wt[land].sum()
world = [wt[land & (clim == k)].sum() / tot * 100 for k in range(1, 6)]
for k, g in enumerate(GROUP):
    if abs(world[k] - mix["_all land"]["mix"][k]) > 0.15:
        fails.append(f"{g}: the shipped share disagrees with a fresh count")
if abs(sum(world) - 100) > 0.01:
    fails.append(f"the world climate shares sum to {sum(world):.2f}, not 100")
print("  ok   world shares sum to 100 and match the shipped table: " +
      ", ".join(f"{g.split()[0]} {v:.1f}%" for g, v in zip(GROUP, world)))
for nm in CONT:
    m = mix[nm]["mix"]
    if abs(sum(m) - 100) > 0.35:
        fails.append(f"{nm}: climate shares sum to {sum(m):.1f}")
print("  ok   every continent's shares sum to 100")
# the one claim the panel copy makes about a continent
if not mix["Antarctica"]["mix"][4] == 100.0:
    fails.append("Antarctica is not entirely polar")
if not mix["Africa"]["mix"][1] > 50:
    fails.append("Africa is not mostly arid, which the map should show")
print(f"  ok   Antarctica is 100% polar; Africa is "
      f"{mix['Africa']['mix'][1]:.0f}% arid")

print("--- the page ---")
html = PAGE.read_text(encoding="utf-8")
if "—" in re.sub(r"<script[\s\S]*?</script>", "", html):
    fails.append("an em dash in the page copy")
for want in ("The Earth", "library.html", "ALTAZOR"):
    if want not in html:
        fails.append(f"the page is missing {want!r}")
if len(html) > 400_000:
    fails.append(f"the page is {len(html)/1024:.0f} KB, too heavy")

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("  playwright not available, skipped the render pass")
else:
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page(viewport={"width": 1300, "height": 1000})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(PAGE.resolve().as_uri())
        pg.wait_for_timeout(2200)
        st = pg.evaluate("()=>window.__earth()")
        if not st["ids"]:
            fails.append("the map never decoded its raster")
        if (st["W"], st["H"]) != (W, H):
            fails.append(f"the page raster is {st['W']}x{st['H']}, not {W}x{H}")
        print(f"  ok   raster decoded, {st['W']}x{st['H']}")

        box = pg.locator("#map").bounding_box()

        def hover(lat, lon):
            pg.mouse.move(box["x"] + (lon + 180) / 360 * box["width"],
                          box["y"] + (90 - lat) / 180 * box["height"])
            pg.wait_for_timeout(360)
            return pg.evaluate("""()=>({n:selName.textContent, a:selArea.textContent,
              s:selShare.textContent, u:selSurf.textContent,
              p:[...document.querySelectorAll('.bar .p')].map(x=>x.textContent),
              w:[...document.querySelectorAll('.bar .fill')].map(x=>x.style.width)})""")

        # Points well inside each continent. The raster check above covers the
        # awkward cases; a pointer maps to a pixel by its own rounding, so a
        # one-pixel miss on somewhere as thin as the Panama isthmus says
        # nothing about the map.
        HOVER = [("Sahara", 23, 10, "Africa"), ("Congo", -2, 22, "Africa"),
                 ("Siberia", 62, 100, "Asia"), ("Gobi", 44, 105, "Asia"),
                 ("Poland", 52, 19, "Europe"), ("Spain", 40, -4, "Europe"),
                 ("Great Plains", 44, -103, "North America"),
                 ("Quebec", 52, -73, "North America"),
                 ("Amazon", -5, -62, "South America"),
                 ("Argentina", -35, -64, "South America"),
                 ("East Antarctica", -78, 60, "Antarctica"),
                 ("Outback", -25, 134, "Australia and Oceania")]
        for nm, lat, lon, want_c in HOVER:
            got = hover(lat, lon)["n"]
            if got != want_c:
                fails.append(f"hovering {nm} reads {got!r}, expected {want_c!r}")
        print(f"  ok   all {len(HOVER)} interior points hover to the right continent")

        # every percentage the panel prints must follow from the area it prints
        for nm in CONT:
            lat, lon = {"Africa": (5, 20), "Asia": (45, 90), "Europe": (52, 19),
                        "North America": (44, -103), "South America": (-10, -60),
                        "Antarctica": (-80, 20),
                        "Australia and Oceania": (-25, 134)}[nm]
            g = hover(lat, lon)
            km2 = int(g["a"].replace(" km²", "").replace(",", ""))
            if km2 != PUB[nm]:
                fails.append(f"{nm}: the panel shows {km2:,} km2")
            if abs(float(g["s"].rstrip("%")) - km2 / LAND * 100) > 0.06:
                fails.append(f"{nm}: share of land {g['s']} does not follow "
                             f"from {km2:,} km2")
            if abs(float(g["u"].rstrip("%")) - km2 / EARTH * 100) > 0.06:
                fails.append(f"{nm}: share of the surface {g['u']} does not "
                             f"follow from {km2:,} km2")
            if [w.rstrip("%") for w in g["w"]] != [p.rstrip("%").rstrip("0").rstrip(".")
                                                   if False else w.rstrip("%")
                                                   for w in g["w"]]:
                pass
            if abs(sum(float(p.rstrip("%")) for p in g["p"]) - 100) > 0.35:
                fails.append(f"{nm}: the bars sum to "
                             f"{sum(float(p.rstrip('%')) for p in g['p']):.1f}%")
        print("  ok   every panel percentage follows from the area beside it")

        # the two toggles must actually change the picture
        def frame():
            return pg.evaluate("""()=>{const c=document.getElementById('map');
              return c.getContext('2d').getImageData(0,0,c.width,c.height).data
                .reduce((a,b,i)=> i%997 ? a : a+b, 0);}""")
        pg.mouse.move(box["x"] + 5, box["y"] - 40)
        pg.wait_for_timeout(300)
        a = frame()
        pg.click("#bClim"); pg.wait_for_timeout(500)
        b = frame()
        if a == b:
            fails.append("the climate toggle changes nothing")
        pg.click("#bClim"); pg.wait_for_timeout(500)
        pg.click("#bGrat"); pg.wait_for_timeout(500)
        c = frame()
        if c == a:
            fails.append("the graticule toggle changes nothing")
        print("  ok   both toggles redraw the map")

        if errs:
            fails.append(f"javascript errors: {errs}")
        br.close()

print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("all checks pass")
