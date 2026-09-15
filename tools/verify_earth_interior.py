"""Check earth-interior.html against PREM and its drawing.

  the model    the PREM polynomials as transcribed give the published
               landmarks: the Earth's mass, the moment of inertia factor,
               densities and wave speeds at each boundary, gravity at the
               core, the pressure at the core-mantle boundary, the inner
               core boundary and the center, all integrated here on a
               0.1 km grid and compared with PREM's table
  the page     the page's own integration agrees with this one; the card
               reads the right numbers at the presets; layers tile the
               depth from 0 to 6371 km; the geotherm hits its sources
  the drawing  seven layers, the marker on the depth line and across the
               profiles, dragging, hovering a layer, the S wave gone in
               the outer core
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from earth_interior_data import PREM_RHO, PREM_VP, PREM_VS, GEOTHERM, LAYERS, PLACES, R_EARTH as RE

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "earth-interior.html"
fails = []
G = 6.67430e-11


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


def prem(T, r):
    x = r / RE
    for a, b, c in T:
        if a <= r <= b:
            return c[0] + c[1] * x + c[2] * x * x + c[3] * x ** 3
    return 0.0


rho = lambda r: prem(PREM_RHO, r)
vp = lambda r: prem(PREM_VP, r)
vs = lambda r: prem(PREM_VS, r)

# integrate on a 0.1 km grid
N = 63710
dr = RE / N
M = [0.0] * (N + 1)
I = 0.0
for i in range(N):
    rm = (i + 0.5) * dr
    dm = 4 * math.pi * (rm * 1e3) ** 2 * rho(rm) * 1e3 * dr * 1e3
    M[i + 1] = M[i] + dm
    I += 2 / 3 * dm * (rm * 1e3) ** 2
gr = lambda i: G * M[i] / (i * dr * 1e3) ** 2 if i > 0 else 0.0
P = [0.0] * (N + 1)
for i in range(N, 0, -1):
    rm = (i - 0.5) * dr
    P[i - 1] = P[i] + rho(rm) * 1e3 * 0.5 * (gr(i) + gr(i - 1)) * dr * 1e3
idx = lambda r: round(r / dr)
MASS = M[N]

print("--- the model ---")
check(abs(MASS - 5.973e24) / 5.973e24 < 1e-3, f"PREM's Earth weighs {MASS:.4e} kg (5.973e24 published)")
check(abs(I / (MASS * (RE * 1e3) ** 2) - 0.3308) < 5e-4, f"moment of inertia factor {I / (MASS * (RE * 1e3) ** 2):.4f} (0.3308 published)")
check(abs(gr(N) - 9.82) < 0.01, f"surface gravity {gr(N):.3f} m/s^2")
check(abs(gr(idx(3480)) - 10.68) < 0.02, f"gravity at the core-mantle boundary {gr(idx(3480)):.2f} (10.68 published)")
check(abs(P[idx(3480)] / 1e9 - 135.75) < 0.5, f"pressure at the core-mantle boundary {P[idx(3480)] / 1e9:.1f} GPa (135.75)")
check(abs(P[idx(1221.5)] / 1e9 - 328.85) < 0.6, f"at the inner core boundary {P[idx(1221.5)] / 1e9:.1f} GPa (328.85)")
check(abs(P[0] / 1e9 - 363.85) < 0.6, f"at the center {P[0] / 1e9:.1f} GPa (363.85)")
land = [("center", 0, 13.0885, 11.2622, 3.6678), ("inner core boundary, inside", 1221.4999, 12.7636, 11.0283, 3.5043),
        ("inner core boundary, outside", 1221.5001, 12.1663, 10.3557, 0), ("core-mantle boundary, core side", 3479.999, 9.9035, 8.0648, 0),
        ("core-mantle boundary, mantle side", 3480.001, 5.5665, 13.7166, 7.2647), ("670 km, below", 5700.999, 4.3807, 10.7513, 5.9451),
        ("670 km, above", 5701.001, 3.9921, 10.2662, 5.5702), ("400 km, below", 5970.999, 3.7238, 9.1340, 4.9325),
        ("400 km, above", 5971.001, 3.5433, 8.9052, 4.7699), ("the Moho, below", 6346.5999, 3.3808, 8.1106, 4.4910),
        ("the Moho, above", 6346.6001, 2.9, 6.8, 3.9)]
for nm, r, d, p_, s_ in land:
    ok = abs(rho(r) - d) < 0.002 and abs(vp(r) - p_) < 0.002 and abs(vs(r) - s_) < 0.002
    check(ok, f"{nm}: density {rho(r):.4f}, P {vp(r):.4f}, S {vs(r):.4f} km/s", f"expected {d}, {p_}, {s_}")
check(all(vs(r) == 0 for r in (1300, 2000, 3000, 3479)), "no shear wave anywhere in the outer core")
check([l[2] for l in LAYERS][0] == 0 and [l[3] for l in LAYERS][-1] == RE and all(LAYERS[i][3] == LAYERS[i + 1][2] for i in range(len(LAYERS) - 1)),
      "the seven layers tile the depth from 0 to 6,371 km")
geo = dict(GEOTHERM)
check(geo[400] == 1839 and geo[670] == 1994 and geo[5149.5] == 6230 and geo[2891] == 4000, "the geotherm hits Katsura's 1839 and 1994 K, 4,000 K at the core, Anzellini's 6230 K")
check(all(GEOTHERM[i][0] < GEOTHERM[i + 1][0] for i in range(len(GEOTHERM) - 1)), "and its points are in depth order")
pl = {p[0]: p for p in PLACES}
check(pl["cmb"][2] == RE - 3480 and pl["icb"][2] == RE - 1221.5 and abs(pl["moho"][2] - (RE - 6346.6)) < 1e-9 and pl["center"][2] == RE, "the boundary presets sit on PREM's radii")

print("--- the page ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1000})
    errs = []
    pg.on("pageerror", lambda x: errs.append(str(x)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#esvg")

    def st(q=None):
        return pg.evaluate("(q)=>window.__earth(q)", q)

    s = st({"r": 3480.001, "shell": [2891, 5149.5]})
    check(abs(s["mass"] - MASS) / MASS < 2e-4, f"the page's mass {s['mass']:.4e} agrees with the integration here")
    a = s["at"]
    check(abs(a["g"] - gr(idx(3480))) < 0.01 and abs(a["P"] - P[idx(3480)]) / P[idx(3480)] < 2e-3, "and its gravity and pressure at the core-mantle boundary")
    check(abs(s["shell"]["m"] - (M[idx(3480)] - M[idx(1221.5)]) / MASS) < 1e-3 and abs(s["shell"]["m"] - 0.308) < 0.003, f"the outer core is {s['shell']['m'] * 100:.1f}% of the mass")
    check(abs(s["shell"]["v"] - ((3480 ** 3 - 1221.5 ** 3) / RE ** 3)) < 1e-4, f"and {s['shell']['v'] * 100:.1f}% of the volume")
    for r in (0.0, 1000.0, 1221.5, 3000.0, 3480.0, 5000.0, 6000.0, 6371.0):
        a = st({"r": r})["at"]
        i = idx(r)
        ok = abs(a["rho"] - rho(r)) < 1e-6 and abs(a["vp"] - vp(r)) < 1e-6 and abs(a["g"] - gr(i)) < 0.01 and abs(a["P"] - P[i]) <= 1e6 + 2e-3 * P[i]
        check(ok, f"at r = {r:.0f} km the page and this checker agree", str((a, rho(r), gr(i), P[i])))
    check(s["view"] == "cut" and s["layers"] == 7 and s["depth"] == 1000, "opens on the cut, seven layers, marker at 1,000 km")
    check(abs(s["marker"][1] - (370 - 330 + 330 * 1000 / RE)) < 0.6, "the marker sits 1,000 km down the depth line")
    check("the lower mantle" in s["card"] and "4.58 g/cm" in s["card"] and "11.46 km/s" in s["card"] and "6.40 km/s" in s["card"] and "38.6 GPa" in s["card"], "the card at 1,000 km: lower mantle, 4.58 g/cm3, 11.46 and 6.40 km/s, 38.6 GPa")
    pg.click('#places button[data-d="6371"]')
    pg.wait_for_timeout(100)
    s = st()
    check("the center" in s["name"] and "13.09 g/cm" in s["card"] and "0.00 m/s" in s["card"] and "364." in s["card"] and "3.59 million atmospheres" in s["card"], "the center: 13.09 g/cm3, gravity zero, 364 GPa, 3.59 million atmospheres")
    pg.click('#places button[data-d="2891"]')
    pg.wait_for_timeout(100)
    s = st()
    check("core-mantle boundary" in s["name"] and "none: it is liquid" in s["card"] and "9.90 g/cm" in s["card"] and "8.06 km/s" in s["card"] and "about 4,0" in s["card"], "the core-mantle boundary from the core side: liquid, 9.90 g/cm3, 8.06 km/s, about 4,000 K")
    pg.click('#places button[data-d="12.3"]')
    pg.wait_for_timeout(100)
    s = st()
    check("deepest hole" in s["name"] and "the crust" in s["card"] and "2.60 g/cm" in s["card"] and "MPa" in s["card"], "the Kola hole: in the crust at 2.60 g/cm3, pressure in MPa")
    # hover a layer
    pg.evaluate("()=>document.querySelector('#esvg path[data-l=\"outer\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(100)
    s = st()
    check(s["hot"] == "outer" and "the outer core" in s["name"] and "30.8%" in s["card"] and "15.6%" in s["card"] and "liquid metal" in s["card"], "hovering the outer core: 30.8% of the mass, 15.6% of the volume, liquid metal")
    # drag on the disc: a point at radius 165 px from the center is 3185.5 km down
    box = pg.eval_on_selector("#esvg", "e=>{const r=e.getBoundingClientRect(); return {x:r.left,y:r.top,w:r.width,h:r.height,vh:e.viewBox.baseVal.height}}")
    sx = lambda px: box["x"] + px / 980 * box["w"]
    sy = lambda py: box["y"] + py / box["vh"] * box["h"]
    pg.mouse.move(sx(520 - 300), sy(370))
    pg.mouse.down()
    pg.mouse.move(sx(520 - 165), sy(370), steps=4)
    pg.mouse.up()
    pg.wait_for_timeout(100)
    s = st()
    check(abs(s["depth"] - RE * 0.5) < 25, f"dragging across the disc lands the marker at {s['depth']:.0f} km")

    pg.click('#views button[data-v="profiles"]')
    pg.wait_for_timeout(150)
    s = st()
    check(s["view"] == "profiles" and s["marker"] is not None and abs(s["marker"][1] - (40 + s["depth"] / RE * 560)) < 0.6, "the profiles share the marker at the same depth")
    npath = pg.evaluate("()=>document.querySelectorAll('#esvg path').length")
    check(npath == 6, f"six curves: density, P, S, gravity, pressure, temperature ({npath})")
    over = pg.evaluate("()=>{const svg=document.querySelector('#esvg'); let n=0; for(const t of svg.querySelectorAll('text')){ if(t.hasAttribute('transform')) continue; const b=t.getBBox(); if(b.x<0||b.x+b.width>980) n++; } return n;}")
    check(over == 0, "no label runs off the edge", f"{over}")
    # drag vertically in the profiles
    pg.mouse.move(sx(300), sy(40 + 560 * 0.2))
    pg.mouse.down()
    pg.mouse.move(sx(300), sy(40 + 560 * 0.8), steps=4)
    pg.mouse.up()
    pg.wait_for_timeout(100)
    s = st()
    check(abs(s["depth"] - RE * 0.8) < 25 and "the outer core" in s["card"], f"dragging down the profiles lands at {s['depth']:.0f} km, in the outer core")
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
