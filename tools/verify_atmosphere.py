"""Check atmosphere.html against the 1976 Standard Atmosphere and its drawing.

  the model    the page's temperature, pressure and density agree with an
               independent hydrostatic integration of the seven lapse-rate
               layers at every kilometre to 86 km, and with the published
               table at the layer bases; the anchors above 86 km fall with
               height and sit within a factor of two of a hydrostatic
               integration through the thermosphere with the mean molecular
               mass falling as the table says; half the air is below 5.5 km
  the words    the marks are in height order and inside 0 to 600 km; dry
               air sums to one; carbon dioxide is 425 ppm
  the drawing  four layers tile 0 to 600 km; the marker on the column and
               across the profiles; dragging; the presets; the card's
               boiling point at Everest and the Armstrong limit; the gases
               answer
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from atmosphere_data import LAYERS_76, UPPER, LAYERS, MARKS, GASES, WATER, P0, G0, R_AIR

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "atmosphere.html"
fails = []
RE = 6356.766


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


# an independent integration: dp/dh = -g0 p / (R T) on a 10 m grid in geopotential height
def T76(h):
    i = len(LAYERS_76) - 1
    while i > 0 and h < LAYERS_76[i][0]:
        i -= 1
    hb, Tb, L = LAYERS_76[i]
    return Tb + L * (h - hb)


def integrate(hmax=86.0, dh=0.01):
    p, h, out = P0, 0.0, {0.0: P0}
    n = int(round(hmax / dh))
    for k in range(n):
        h0 = k * dh
        T1, T2 = T76(h0), T76(h0 + dh)
        # exact step for a linear T across the step
        if abs(T2 - T1) < 1e-12:
            p *= math.exp(-G0 * dh * 1000 / (R_AIR * T1))
        else:
            L = (T2 - T1) / dh
            p *= (T1 / T2) ** (G0 * 1000 / (R_AIR * L))
        out[round(h0 + dh, 6)] = p
    return out


PH = integrate()
geopot = lambda z: RE * z / (RE + z)


def mine(z):
    h = geopot(z)
    key = round(round(h / 0.01) * 0.01, 6)
    T = T76(h)
    return T, PH[key], PH[key] / (R_AIR * T)


print("--- the model ---")
# the published table at the layer bases (geometric km: T K, p Pa)
table = [(0, 288.15, 101325), (11, 216.77, 22700), (20, 216.65, 5529), (32, 228.49, 889.06), (47, 269.68, 115.85), (51, 270.65, 70.458), (71, 216.85, 4.4795), (86, 186.95, 0.37338)]
for z, T, p in table:
    t, pp, _ = mine(z)
    check(abs(t - T) < 0.05 and abs(pp / p - 1) < 3e-3, f"at {z} km the integration here gives {t:.2f} K and {pp:.5g} Pa (table {T}, {p})")
up = sorted(UPPER)
check(all(up[i][2] > up[i + 1][2] and up[i][3] > up[i + 1][3] and up[i][1] <= up[i + 1][1] + 1e-9 for i in range(len(up) - 1)), "above 86 km pressure and density fall and temperature does not")
# hydrostatic through the thermosphere with the table's molecular mass and temperature
p = up[0][2]
ok = True
for i in range(len(up) - 1):
    z0, T0, _, _, M0 = up[i]
    z1, T1, p1, _, M1 = up[i + 1]
    n = 200
    for k in range(n):
        f = (k + 0.5) / n
        z = z0 + (z1 - z0) * f
        T = T0 + (T1 - T0) * f
        M = (M0 + (M1 - M0) * f) * 1e-3
        g = G0 * (RE / (RE + z)) ** 2
        p *= math.exp(-M * g / (8.31432 * T) * (z1 - z0) * 1000 / n)
    ok = ok and 0.5 < p / p1 < 2.0
    print(f"    {z1} km: hydrostatic {p:.2e} Pa, table {p1:.2e}")
    p = p1
check(ok, "the anchors above 86 km are hydrostatic within a factor of two, given the table's temperatures and molecular masses")
half = next(z for z in [i / 100 for i in range(0, 8600)] if mine(z)[1] / P0 < 0.5)
check(abs(half - 5.5) < 0.1, f"half the air lies below {half:.2f} km")
h99 = next(z for z in [i / 100 for i in range(0, 8600)] if mine(z)[1] / P0 < 0.01)
check(abs(h99 - 31.1) < 0.3, f"ninety-nine percent below {h99:.1f} km")
check(abs(P0 / G0 / 1000 - 10.33) < 0.01, "the column weighs 10.3 tonnes on a square metre")

print("--- the words ---")
check(all(MARKS[i][2] < MARKS[i + 1][2] for i in range(len(MARKS) - 1)) and 0 < MARKS[0][2] and MARKS[-1][2] <= 600, f"{len(MARKS)} marks in height order, 0 to 600 km")
check([l[2] for l in LAYERS] == [0, 11, 47, 86] and LAYERS[-1][3] == 600, "four layers tiling 0 to 600 km")
dry = sum(g[2] for g in GASES)
check(abs(dry - 1) < 3e-4, f"dry air sums to {dry:.5f}")
co2 = next(g for g in GASES if g[0] == "carbon dioxide")
check(abs(co2[2] - 425e-6) < 1e-6, "carbon dioxide at 425 ppm")
check(GASES[0][2] > GASES[1][2] > GASES[2][2] > GASES[3][2], "nitrogen, oxygen, argon, carbon dioxide in falling order")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1000})
    errs = []
    pg.on("pageerror", lambda x: errs.append(str(x)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#asvg")

    def st(q=None):
        return pg.evaluate("(q)=>window.__atm(q)", q)

    worst = 0
    for z in range(0, 87):
        a = st({"z": z})["at"]
        T, p, rho = mine(z)
        worst = max(worst, abs(a["T"] - T), abs(a["p"] / p - 1), abs(a["rho"] / rho - 1))
    check(worst < 3e-3, f"the page agrees with the integration here at every kilometre to 86 km (worst {worst:.2e})")
    a = st({"z": 0})["at"]
    check(abs(a["c"] - 340.3) < 0.2 and abs(a["boil"] - 100) < 0.2, f"at sea level sound goes {a['c']:.1f} m/s and water boils at {a['boil']:.1f} C")
    a = st({"z": 8.85})["at"]
    check(abs(a["boil"] - 71) < 1.5 and 0.30 < a["p"] / P0 < 0.34, f"on Everest water boils at {a['boil']:.0f} C under {a['p'] / P0 * 100:.0f}% of the pressure")
    a = st({"z": 19})["at"]
    check(abs(a["boil"] - 37) < 1.5 and abs(a["p"] - 6300) < 300, f"at the Armstrong limit it boils at {a['boil']:.0f} C, body temperature, under {a['p'] / 1000:.1f} kPa")
    s = st()
    check(s["view"] == "up" and s["z"] == 0 and abs(s["half"] - half) < 0.05 and abs(s["h99"] - h99) < 0.1, "opens at the ground; the page's half and 99% heights agree")
    check("1,013.3 hPa" in s["card"] and "15 °C" in s["card"] and "the troposphere" in s["card"], "the card at the ground: 1,013.3 hPa, 15 C, troposphere")
    pg.click('#marks button[data-k="everest"]')
    pg.wait_for_timeout(100)
    s = st()
    check(abs(s["z"] - 8.85) < 1e-6 and "Everest" in s["name"] and "31%" in s["card"] and "69%" in s["card"] and "70 °C" in s["card"] and "-42 °C" in s["card"], "the Everest preset: 31% of the air above, 69% below, water boils at 70 C, minus 42 C")
    check(abs(s["marker"] - st({"YZ": 8.85})["yz"]) < 0.6, "the marker sits at Everest's height")
    pg.click('#marks button[data-k="iss"]')
    pg.wait_for_timeout(100)
    s = st()
    check(s["z"] == 420 and "thermosphere" in s["card"] and "10<sup>-6</sup> Pa" in pg.inner_html("#numTxt") and "space station" in s["name"], "the station preset: 420 km, thermosphere, a millionth of a pascal")
    # drag down the column
    box = pg.eval_on_selector("#asvg", "e=>{const r=e.getBoundingClientRect(); return {x:r.left,y:r.top,w:r.width,h:r.height,vh:e.viewBox.baseVal.height}}")
    sx = lambda px: box["x"] + px / 980 * box["w"]
    sy = lambda py: box["y"] + py / box["vh"] * box["h"]
    pg.mouse.move(sx(150), sy(630 - 468 * 0.25))
    pg.mouse.down()
    pg.mouse.move(sx(150), sy(630 - 468 * 0.5), steps=4)
    pg.mouse.up()
    pg.wait_for_timeout(100)
    s = st()
    check(abs(s["z"] - 60) < 2 and "the stratosphere" in s["card"] or "the mesosphere" in s["card"], f"dragging lands the marker at {s['z']:.0f} km")
    pg.evaluate("()=>document.querySelector('#asvg g[data-l=\"strato\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(100)
    s = st()
    check("the stratosphere" in s["name"] and "11 km to 47 km" in s["card"] and "% of the air" in s["card"], "hovering the stratosphere: 11 to 47 km and its share of the air")
    strat = (mine(11)[1] - mine(47)[1]) / P0 * 100
    check(f"{strat:.1f}%" in s["card"], f"which is {strat:.1f}%")
    pg.click('#views button[data-v="made"]')
    pg.wait_for_timeout(150)
    s = st()
    check(s["view"] == "made" and "99.03%" in s["card"], "the composition view: nitrogen and oxygen are 99.03%")
    pg.evaluate("()=>document.querySelector('#asvg g[data-g=\"3\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(100)
    s = st()
    check("carbon dioxide" in s["name"] and "425 parts per million" in s["card"], "hovering carbon dioxide: 425 parts per million")
    pg.evaluate("()=>document.querySelector('#asvg g[data-g=\"w\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(100)
    check("water vapour" in st()["name"], "and water vapour answers")
    over = pg.evaluate("()=>{const svg=document.querySelector('#asvg'); let n=0; for(const t of svg.querySelectorAll('text')){ if(t.hasAttribute('transform')) continue; const b=t.getBBox(); if(b.x<0||b.x+b.width>980) n++; } return n;}")
    check(over == 0, "no label runs off the edge", f"{over}")
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
