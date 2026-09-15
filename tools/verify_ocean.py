"""Check ocean.html against its data and its drawing.

  the data     every current has a name, a warmth, a gyre or none, a source
               and at least three points; every point of every current and
               of the conveyor lies in the sea on the coastline raster;
               warm western boundary currents flow poleward and cold
               eastern ones equatorward; each gyre's currents, taken in
               order round the ring, turn the way the gyre says
  the drawing  the map paints; a current under the pointer is the right
               one at known places; the gyre buttons light their currents;
               the conveyor view answers; no script errors
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ocean_data import CURRENTS, GYRES, CONVEYOR

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "ocean.html"
fails = []


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


print("--- the data ---")
cur = {c[0]: c for c in CURRENTS}
check(all(c[1] and c[2] in ("warm", "cold") and (c[4] is None or c[4] in {g[0] for g in GYRES}) and len(c[3]) >= 3 and c[8] for c in CURRENTS),
      f"{len(CURRENTS)} currents, each named, warm or cold, in a gyre or none, drawn with three points or more, and sourced")
# western boundary currents poleward, eastern ones equatorward
for k, poleward in [("gulf", True), ("kuroshio", True), ("brazil", True), ("agulhas", True), ("eac", True), ("canary", False), ("california", False), ("humboldt", False), ("benguela", False), ("waust", False)]:
    p = cur[k][3]
    d = abs(p[-1][1]) - abs(p[0][1])
    check((d > 0) == poleward, f"{cur[k][1]} flows {'poleward' if d > 0 else 'toward the equator'} and is {cur[k][2]}")
    check((cur[k][2] == "warm") == poleward, f"  and {'warm' if poleward else 'cold'}, as a {'western' if poleward else 'eastern'} boundary current should be")
# the gyres' senses from the order of their currents round the ring
for gk, gn, sense, center, _ in GYRES:
    pts = []
    for c in CURRENTS:
        if c[4] == gk:
            pts += c[3]
    # the winding number about the center
    tot = 0.0
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        a1 = math.atan2(a[1] - center[1], ((a[0] - center[0] + 540) % 360) - 180)
        a2 = math.atan2(b[1] - center[1], ((b[0] - center[0] + 540) % 360) - 180)
        d = a2 - a1
        while d > math.pi:
            d -= 2 * math.pi
        while d < -math.pi:
            d += 2 * math.pi
        tot += d
    turns = tot / (2 * math.pi)
    check((turns < -0.7) == (sense == "clockwise") and abs(turns) > 0.7, f"{gn} winds {turns:+.2f} turns about its center: {sense}")
check(all(g[2] == ("clockwise" if g[3][1] > 0 else "counterclockwise") for g in GYRES), "northern gyres clockwise, southern counterclockwise")
acc = cur["acc"][3]
check(acc[0][0] == -180 and acc[-1][0] == 180 and all(acc[i][0] < acc[i + 1][0] for i in range(len(acc) - 1)) and all(-62 < p[1] < -50 for p in acc),
      "the circumpolar current runs east all the way round between 50 and 62 S")
check(all(abs(p[1]) < 90 and -180 <= p[0] <= 180 for c in CURRENTS for p in c[3]), "every point inside the map")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1000})
    errs = []
    pg.on("pageerror", lambda x: errs.append(str(x)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_function("()=>window.__ocean().ready")
    pg.wait_for_timeout(300)

    def st(q=None):
        return pg.evaluate("(q)=>window.__ocean(q)", q)

    pts = [(c[0], p) for c in CURRENTS for p in c[3]] + [(k, p) for k, v in CONVEYOR.items() for p in v]
    sea = st({"sea": [p for _, p in pts]})["sea"]
    bad = [(k, p) for (k, p), ok in zip(pts, sea) if not ok]
    check(not bad, f"all {len(pts)} points of the currents and the conveyor lie in the sea on the coastline raster", str(bad))
    check(st({"sea": [[20, 10], [-100, 40], [140, -25]]})["sea"] == [False, False, False] and st({"sea": [[0, 0], [-30, 30], [-150, 0]]})["sea"] == [True, True, True], "and the raster knows land from sea at six known places")
    rgb = st({"pixel": [490, 300]})["rgb"]
    check(rgb[2] > rgb[0] and rgb[2] > 20, f"the map is painted, the Atlantic blue ({rgb})")
    for lon, lat, want in [(-74, 35.5, "gulf"), (138, 34, "kuroshio"), (-78, -22, "humboldt"), (-90, -60, "acc"), (31, -33, "agulhas"), (-123, 34, "california")]:
        got = st({"at": [lon, lat]})["near"]
        check(got == want, f"under the pointer at {lat}, {lon}: {cur[got][1] if got else 'nothing'}", want)
    box = pg.eval_on_selector("#map", "e=>{const r=e.getBoundingClientRect(); return [r.left,r.top,r.width,r.height]}")
    mx = lambda lon: box[0] + (lon + 180) / 360 * box[2]
    my = lambda lat: box[1] + (90 - lat) / 180 * box[3]
    pg.mouse.move(mx(-74), my(35.5))
    pg.wait_for_timeout(150)
    s = st()
    check(s["hot"] == "gulf" and "Gulf Stream" in s["name"] and "150 Sv" in s["card"] and "2.5 m/s" in s["card"] and "western side" in s["card"], "hovering the Gulf Stream: 30 and 150 Sv, 2.5 m/s, the western side of its gyre")
    pg.mouse.move(mx(-15), my(30))
    pg.wait_for_timeout(150)
    s = st()
    check(s["hot"] == "canary" and "eastern side" in s["card"] and "flows south" in s["card"], "the Canary Current: the eastern side, flowing south")
    pg.click('#gyres button[data-g="spac"]')
    pg.wait_for_timeout(150)
    s = st()
    check(s["gyre"] == "spac" and "counterclockwise" in s["card"] and "Humboldt" in s["card"] and "East Australian" in s["card"], "the South Pacific gyre button: counterclockwise, Humboldt and East Australian among its currents")
    pg.click('#gyres button[data-g="spac"]')
    pg.wait_for_timeout(100)
    check(st()["gyre"] is None, "pressing it again clears it")
    pg.click('#views button[data-v="conveyor"]')
    pg.wait_for_timeout(200)
    s = st()
    check(s["view"] == "conveyor" and "thousand years" in s["card"] and "15 Sv" in s["card"], "the conveyor view: a thousand-year lap, 15 Sv of sinking")
    rgb = st({"pixel": [int((-160 + 180) / 360 * 980), int((90 - 40) / 180 * 490)]})["rgb"]
    check(rgb[0] > 150 and rgb[0] > rgb[2], f"the rising point in the North Pacific is painted warm ({rgb})")
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
