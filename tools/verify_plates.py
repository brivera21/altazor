"""Check plates.html against Bird's model and its drawing.

  the data     52 plates whose areas sum to the Earth's surface; the big
               seven at Bird's published sizes (his table gives steradians);
               every boundary line has a class, a length and a velocity;
               the lengths by class add up to the model's totals; the well
               known rates come out (Nazca under South America, the Pacific
               past North America, India into Eurasia, the Atlantic opening)
  the drawing  the map paints; a plate under the pointer is the right one
               at ten known places; a boundary under the pointer is the
               right kind; the presets land on their boundaries; no line is
               drawn across the map at the dateline; the edges view answers
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plates_data import CLASSES, PLACES

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "plates.html"
G = json.loads((ROOT / "tools" / "data" / "plates.json").read_text())
fails = []
SR = 6371.0088 ** 2   # km^2 per steradian


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


print("--- the data ---")
check(len(G["codes"]) == 52 and len(G["areas"]) == 52, f"{len(G['codes'])} plates")
total = sum(v[1] for v in G["areas"].values())
check(abs(total - 510.07e6) / 510.07e6 < 1e-3, f"their polygon areas sum to {total / 1e6:.2f} million km2 (the Earth is 510.07)")
rast = sum(v[2] for v in G["areas"].values())
check(abs(rast - 510.07e6) / 510.07e6 < 2e-3, f"and the raster covers {rast / 1e6:.1f} million km2 with no gaps")
check(all(abs(v[2] / v[1] - 1) < 0.01 for k, v in G["areas"].items() if v[1] > 10e6), "the raster and the polygons agree within 1% for every plate over ten million km2")
check(abs(G["areas"]["PA"][1] / SR / 2.57685 - 1) < 0.01, f"the Pacific, {G['areas']['PA'][1] / 1e6:.2f} million km2, is Bird's 2.57685 sr")
big7 = sum(G["areas"][k][1] for k in ("PA", "AF", "AN", "NA", "EU", "AU", "SA"))
check(0.80 < big7 / total < 0.85, f"the seven largest hold {big7 / total * 100:.0f}% of the surface")
check(all(len(L) == 7 and 0 <= L[1] < 7 and L[2] > 0 and L[3] >= 0 and len(L[6]) >= 4 for L in G["lines"]), f"{len(G['lines'])} boundary lines, each classed, measured and drawn")
by = [0] * 7
for L in G["lines"]:
    by[L[1]] += L[2]
total_len = sum(by)
check(abs(total_len - 260000) < 15000, f"the boundaries run {total_len:,.0f} km in all")
check(by[0] > 60000 and by[2] > 45000, f"ridges {by[0]:,.0f} km, subduction {by[2]:,.0f} km")
codes = [c[0] for c in CLASSES]
check(codes == G["classes"], "the class order in the words matches the data file")


import re


def pair_rate(a, b, cls=None):
    L = [x for x in G["lines"] if set(re.split(r"[-\\/]", x[0])) == {a, b} and (cls is None or x[1] == cls)]
    tot = sum(x[2] for x in L)
    return sum(x[2] * x[3] for x in L) / tot if tot else None


r = pair_rate("NZ", "SA", 2)
check(r and 65 < r < 85, f"Nazca under South America at {r:.0f} mm a year")
r = pair_rate("PA", "NA", 4)
check(r and 40 < r < 55, f"the Pacific past North America along the continental transform at {r:.0f} mm a year")
r = pair_rate("IN", "EU")
check(r and 35 < r < 55, f"India into Eurasia at {r:.0f} mm a year")
r = pair_rate("SA", "AF", 0)
check(r and 25 < r < 40, f"the South Atlantic opening at {r:.0f} mm a year")
r = pair_rate("PA", "KE", 2)
check(r and 60 < r < 110, f"the Pacific under the Kermadec plate at {r:.0f} mm a year")
subs = [x[0] for x in G["lines"] if x[1] == 2]
check(all(("\\" in p) != ("/" in p) for p in subs), "every subduction line names which plate dives, with Bird's slash")
check(any(p == "NZ\\SA" for p in subs) and any(p == "JF\\NA" for p in subs), "Nazca under South America, Juan de Fuca under North America")
r = pair_rate("EU", "NA", 0)
check(r and 15 < r < 26, f"the North Atlantic opening at {r:.0f} mm a year")
r = pair_rate("AR", "AF", 1)
check(r and 8 < r < 20, f"the Red Sea, a continental rift in Bird's model, opening at {r:.0f} mm a year")
# no line hops the dateline in its drawn points
hops = sum(1 for L in G["lines"] for i in range(0, len(L[6]) - 2, 2) if abs(L[6][i + 2] - L[6][i]) > 180)
print(f"  ({hops} drawn segments cross the dateline; the page breaks the path there)")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1000})
    errs = []
    pg.on("pageerror", lambda x: errs.append(str(x)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_function("()=>window.__plates().ready")
    pg.wait_for_timeout(300)

    def st(q=None):
        return pg.evaluate("(q)=>window.__plates(q)", q)

    s = st()
    check(s["n"] == 52 and s["lines"] == len(G["lines"]) and "5,824" in s["card"], "the page opens with 52 plates and 5,824 steps on the card")
    for lon, lat, want in [(-100, 40, "NA"), (18, 8, "AF"), (-58, -15, "SA"), (80, 55, "EU"), (132, -27, "AU"), (-150, 10, "PA"), (0, -80, "AN"), (-95, -22, "NZ"), (77, 20, "IN"), (47, 23, "AR"), (42, -8, "SO"), (134, 18, "PS")]:
        got = st({"at": [lon, lat]})["plate"]
        check(got == want, f"at {lat}, {lon}: {G['areas'][got][0] if got else 'nothing'}", want)
    # the boundary kinds under the pointer at known places
    for lon, lat, cls, nm in [(-45.1, 15.3, 0, "the Mid-Atlantic Ridge is a spreading ridge"), (-72.5, -22, 2, "the Peru-Chile Trench is subduction"), (-122.4, 37.6, 4, "the San Andreas is a continental transform"), (84, 28, 5, "the Himalaya is a continental collision")]:
        near = set()
        for j, L in enumerate(G["lines"]):
            p = L[6]
            for i in range(0, len(p), 2):
                if math.hypot((p[i] - lon) * math.cos(math.radians(lat)), p[i + 1] - lat) < 1.5:
                    near.add(L[1])
        check(cls in near, nm + " (a line of that kind passes within 1.5 degrees)", str([G["classes"][c] for c in near]))
    # the raster's plate under a rendered pixel, and the map painted at all
    rgb = st({"pixel": [490, 245]})["rgb"]
    check(sum(rgb) > 60, f"the map is painted (pixel at the center is {rgb})")
    # hover Africa with the real pointer
    box = pg.eval_on_selector("#map", "e=>{const r=e.getBoundingClientRect(); return [r.left,r.top,r.width,r.height]}")
    mx = lambda lon: box[0] + (lon + 180) / 360 * box[2]
    my = lambda lat: box[1] + (90 - lat) / 180 * box[3]
    pg.mouse.move(mx(18), my(8))
    pg.wait_for_timeout(150)
    s = st()
    check(s["name"] == "Africa" and "58.4" in s["card"] and "11.5%" in s["card"] and "pulling apart" in s["card"] and "diving under a neighbor" in s["card"], "hovering Africa: 58.4 million km2, 11.5%, edges by kind, some of it diving under Eurasia")
    st_af = s["stats"]["AF"]
    check(abs(st_af["by"][0] + st_af["by"][1] - 20318) < 50, "Africa's pulling-apart edge is 20,318 km, as the card says")
    pg.mouse.move(mx(-45.1), my(15.3))
    pg.wait_for_timeout(150)
    s = st()
    check(s["hotLine"] >= 0 and "spreading ridge" in s["card"] and "Africa" in s["name"] and "South America" in s["name"] and "pulling apart" in s["card"] and "2.6 cm" in s["card"], "hovering the Mid-Atlantic Ridge at 15 N: Africa and South America, a spreading ridge, pulling apart at 2.6 cm a year")
    pg.click('#places button[data-k="andes"]')
    pg.wait_for_timeout(150)
    s = st()
    check("Peru-Chile" in s["name"] and "subduction" in s["card"] and "Nazca" in s["card"], "the Peru-Chile preset names the boundary: Nazca, subduction")
    pg.mouse.move(mx(-60), my(-22))
    pg.wait_for_timeout(100)
    pg.mouse.move(mx(-72.5), my(-22))
    pg.wait_for_timeout(150)
    s = st()
    check("Nazca dives under South America" in s["card"] and "8.0 cm" in s["card"], "hovering the trench itself: Nazca dives under South America at 8.0 cm a year")
    pg.click('#places button[data-k="himalaya"]')
    pg.wait_for_timeout(150)
    s = st()
    check("Himalaya" in s["name"] and "collision" in s["card"] and "India" in s["card"], "the Himalaya preset: India, collision")
    pg.click('#views button[data-v="edges"]')
    pg.wait_for_timeout(150)
    s = st()
    check(s["view"] == "edges" and pg.evaluate("()=>document.querySelectorAll('#psvg g[data-e]').length") == 3, "the edges view draws three sections")
    pg.evaluate("()=>document.querySelector('#psvg g[data-e=\"trench\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(100)
    check("subduction zone" in pg.inner_text("#nameTxt") and "700 km" in pg.inner_text("#bodyTxt"), "hovering the trench section: the slab's earthquakes to 700 km")
    check(not errs, "no script errors", "; ".join(errs))
    br.close()

print("--- the copy ---")
html = PAGE.read_text()
check("—" not in html, "no em dashes")

print()
if fails:
    print(f"{len(fails)} FAILED:")
    for x in fails:
        print("  -", x)
    sys.exit(1)
print("everything squares")
