"""Check projections.html against its data, against independent geometry,
and against its drawing.

  the data     nine projections each with a kind, a year and a story;
               Robinson's table is monotonic and ends at 0.5322 and 1;
               the cities sit where they should on the land mask
  the sums     every projection's inverse undoes its forward at a grid of
               points; the equal-area ones give area scale 1 within a
               percent everywhere; Mercator gives sec squared; the plate
               carree gives sec; the Winkel tripel and Robinson lie
               between 1 and 1.15 at 50 degrees; a 1,000 km cap at 60 N
               on Mercator appears about 4.2 times its area and on
               Mollweide once; great-circle and rhumb distances match an
               independent calculation for every route
  the drawing  the map is painted, with land in the Sahara and sea in the
               mid-Atlantic under the pixels; the cap drags and the card
               follows; the stretch marker drags; the routes answer
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from projections_data import R_EARTH, PROJECTIONS, ROBINSON, PLACES, CITIES, ROUTES

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "projections.html"
fails = []


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


D2R = math.pi / 180
print("--- the data ---")
check(len(PROJECTIONS) == 9 and all(p[2] and p[4] and p[5] for p in PROJECTIONS), "nine projections, each with a kind, an author and a story")
check(len(ROBINSON) == 19 and all(ROBINSON[i][1] > ROBINSON[i + 1][1] and ROBINSON[i][2] < ROBINSON[i + 1][2] for i in range(18)) and ROBINSON[-1][1] == 0.5322 and ROBINSON[-1][2] == 1.0, "Robinson's table runs monotonically to 0.5322 and 1.0000")
check(all(-90 <= lat <= 90 for _, lat in PLACES) and [l for _, l in PLACES] == sorted(l for _, l in PLACES), "the places are in order of latitude")
check(all(a in CITIES and b in CITIES for a, b in ROUTES), "every route joins two known cities")


def hav(a, b):
    l1, p1, l2, p2 = a[1] * D2R, a[2] * D2R, b[1] * D2R, b[2] * D2R
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin((l2 - l1) / 2) ** 2
    return 2 * R_EARTH * math.asin(math.sqrt(h))


def rhumb(a, b):
    p1, p2 = a[2] * D2R, b[2] * D2R
    dl = (b[1] - a[1]) * D2R
    if abs(dl) > math.pi:
        dl = dl - 2 * math.pi if dl > 0 else dl + 2 * math.pi
    dpsi = math.log(math.tan(math.pi / 4 + p2 / 2) / math.tan(math.pi / 4 + p1 / 2))
    q = (p2 - p1) / dpsi if abs(dpsi) > 1e-12 else math.cos(p1)
    return R_EARTH * math.sqrt((p2 - p1) ** 2 + q * q * dl * dl)


print("--- the sums ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1100})
    errs = []
    pg.on("pageerror", lambda x: errs.append(str(x)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#mcanvas")
    pg.wait_for_function("()=>window.__proj().land")

    def st(q=None):
        return pg.evaluate("(q)=>window.__proj(q)", q)

    # inverses undo forwards
    for k, *_ in PROJECTIONS:
        worst = 0
        for lon in range(-170, 171, 34):
            for lat in range(-80, 81, 20):
                if k == "ortho" and not (-120 < lon < 60):
                    continue
                r = st({"fwd": [lon, lat], "proj": k})
                if r["fwd"] is None:
                    continue
                if r["inv"] is None:
                    worst = 999
                    continue
                dl = abs((r["inv"][0] - lon + 540) % 360 - 180)
                worst = max(worst, dl, abs(r["inv"][1] - lat))
        check(worst < 1e-3, f"{k}: the inverse undoes the forward to within {worst:.1e} degrees")
    # area scales
    for k in ("gallpeters", "mollweide", "sinusoidal"):
        vals = [st({"scale": [k, l]})["scale"] for l in (0, 20, 40, 60, 80, 89)]
        check(all(abs(v - 1) < 0.01 for v in vals), f"{k} keeps area: scale within 1% of 1 from the Equator to 89 degrees")
    check(all(abs(st({"scale": ["mercator", l]})["scale"] / (1 / math.cos(l * D2R) ** 2) - 1) < 1e-3 for l in (0, 30, 60, 75)), "Mercator's area scale is the secant squared")
    check(all(abs(st({"scale": ["platecarree", l]})["scale"] / (1 / math.cos(l * D2R)) - 1) < 1e-3 for l in (0, 30, 60, 75)), "the plate carree's is the secant")
    w50, r50 = st({"scale": ["winkel", 50]})["scale"], st({"scale": ["robinson", 50]})["scale"]
    check(1.0 < w50 < 1.15 and 1.0 < r50 < 1.15, f"Winkel tripel {w50:.2f} and Robinson {r50:.2f} at 50 degrees, both mild")
    rm = st({"ratio": [0, 60, 1000], "proj": "mercator"})["ratio"]
    ro = st({"ratio": [0, 60, 1000], "proj": "mollweide"})["ratio"]
    rg = st({"ratio": [0, 0, 1000], "proj": "mercator"})["ratio"]
    check(4.0 < rm < 4.4 and abs(ro - 1) < 0.01 and abs(rg - 1) < 0.01, f"a 1,000 km cap at 60 N appears {rm:.2f} times on Mercator, {ro:.3f} on Mollweide, and {rg:.3f} at the Equator")
    ok = True
    for a, b in ROUTES:
        r = st({"route": [a, b]})
        if abs(r["gc"] - hav(CITIES[a], CITIES[b])) > 0.5 or abs(r["rh"] - rhumb(CITIES[a], CITIES[b])) > 0.5:
            ok = False
    check(ok, "great-circle and rhumb distances agree with this checker on every route")
    lt = st({"route": ["london", "tokyo"]})
    check(abs(lt["gc"] - 9559) < 15 and 30 < lt["brg"] < 34, f"London to Tokyo: {lt['gc']:.0f} km on a bearing of {lt['brg']:.0f} degrees")
    lm = st({"land": [[-0.13, 51.5], [-30, 30], [30, 0], [0, -20]]})["isLand"]
    check(lm == [True, False, True, False], "the mask: London and the Congo are land, the mid-Atlantic and the Gulf of Guinea are sea")

    print("--- the drawing ---")
    s = st()
    check(s["view"] == "maps" and s["proj"] == "mercator" and "4.1" in s["card"] and "swollen" in s["card"], "opens on Mercator with the cap at 60 N, 40 W, about 4.2 times its area")
    lon_px = pg.evaluate("()=>{ const c=document.getElementById('mcanvas'); return c.width; }")
    # find the pixel of London and a mid-Atlantic point through the page's own forward
    def px_of(lon, lat):
        return pg.evaluate("([lo,la])=>{ const r=P[proj].fwd(lo*D2R,la*D2R); return toPx(r); }", [lon, lat])
    pl = px_of(10, 22)
    pa = px_of(-35, 40)
    cl = st({"px": [round(pl[0]), round(pl[1])]})["pixel"]
    ca = st({"px": [round(pa[0]), round(pa[1])]})["pixel"]
    check(60 < cl[0] < 100 and ca[0] < 30, "under the pixels, the Sahara is painted as land and the mid-Atlantic as sea")
    cbox = pg.eval_on_selector("#mcanvas", "e=>{const r=e.getBoundingClientRect(); return {x:r.left,y:r.top,w:r.width,h:r.height,cw:e.width,ch:e.height}}")
    cx = lambda px: cbox["x"] + px / cbox["cw"] * cbox["w"]
    cy = lambda py: cbox["y"] + py / cbox["ch"] * cbox["h"]
    pc = px_of(-40, 60)
    pe = px_of(20, 0)
    pg.mouse.move(cx(pc[0]), cy(pc[1]))
    pg.mouse.down()
    pg.mouse.move(cx(pe[0]), cy(pe[1]), steps=6)
    pg.mouse.up()
    pg.wait_for_timeout(200)
    s = st()
    check(abs(s["cap"]["lon"] - 20) < 0.6 and abs(s["cap"]["lat"]) < 0.6 and "1.0" in s["card"] and "which is right" in s["card"], f"dragging the cap to the Equator ({s['cap']['lon']:.1f}, {s['cap']['lat']:.1f}): it appears its true size")
    pg.click('#projs button[data-p="ortho"]')
    pg.wait_for_timeout(300)
    s = st()
    check(s["proj"] == "ortho" and "Hipparchus" in s["card"] and not pg.evaluate("()=>document.getElementById('centreCtl').hidden"), "the orthographic globe shows its center buttons")
    pg.click('#centers button[data-c="pac"]')
    pg.wait_for_timeout(300)
    s = st()
    check(s["center"] == "pac" and "cut by the edge" in s["card"], "turned to the Pacific, the cap at 20 E is over the edge")
    pg.click('#views button[data-v="stretch"]')
    pg.wait_for_timeout(200)
    s = st()
    check(s["view"] == "stretch" and s["curves"] == 6 and abs(s["marker"] - s["sx"]) < 0.6 and "London" in s["name"] and "2.58" in s["card"], "the stretch view opens at 51.5 degrees, London, Mercator 2.58")
    box = pg.eval_on_selector("#psvg", "e=>{const r=e.getBoundingClientRect(); return {x:r.left,y:r.top,w:r.width,h:r.height,vh:e.viewBox.baseVal.height}}")
    sx = lambda px: box["x"] + px / 980 * box["w"]
    sy = lambda py: box["y"] + py / box["vh"] * box["h"]
    SX = lambda l: 80 + l / 90 * 820
    pg.mouse.move(sx(SX(51.5)), sy(300))
    pg.mouse.down()
    pg.mouse.move(sx(SX(60)), sy(300), steps=5)
    pg.mouse.up()
    pg.wait_for_timeout(150)
    s = st()
    check(abs(s["lat"] - 60) < 0.15 and "Oslo" in s["name"] and "4.0" in s["card"], f"dragging the marker to {s['lat']} degrees: Oslo, Mercator 4.0")
    boxes = pg.evaluate("()=>[...document.querySelectorAll('#psvg text')].filter(t=>!t.hasAttribute('transform')).map(t=>{const b=t.getBBox(); return [b.x,b.y,b.width,b.height]})")
    clash = sum(1 for i in range(len(boxes)) for j in range(i + 1, len(boxes)) if boxes[i][0] < boxes[j][0] + boxes[j][2] and boxes[j][0] < boxes[i][0] + boxes[i][2] and boxes[i][1] < boxes[j][1] + boxes[j][3] and boxes[j][1] < boxes[i][1] + boxes[i][3])
    check(clash == 0, "no two labels overlap on the stretch chart", f"{clash}")
    pg.click('#views button[data-v="routes"]')
    pg.wait_for_timeout(400)
    s = st()
    check(s["view"] == "routes" and "London to Tokyo" in s["name"] and "9,559 km" in s["card"] and pg.evaluate("()=>!!document.getElementById('rcanvas')"), "the routes view opens on London to Tokyo, 9,559 km")
    pg.click('#routes button[data-r="3"]')
    pg.wait_for_timeout(400)
    s = st()
    check("Santiago to Sydney" in s["name"] and f"{hav(CITIES['santiago'], CITIES['sydney']):,.0f} km" in s["card"], "Santiago to Sydney answers with its distance")
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
