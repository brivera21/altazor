"""Check light.html against its data and its drawing.

  the data     seven bands that tile the line with no gaps; every mark inside
               a band and sourced; windows in order; bodies rising in
               temperature
  the physics  Planck's law, Wien's peaks, Stefan-Boltzmann and the share of
               a body's power in the visible band, each worked here and
               compared with the page; the matching-function fit peaks where
               the CIE curves peak; the Sun's colour sits on the Planckian
               locus; 6500 K is close to daylight white
  the drawing  marks and windows land at their log positions; the marker
               drags; hovering and the presets fill the card; the hot-body
               curve peaks on Wien's line; the visible band is shaded
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from light_data import BANDS, MARKS, WINDOWS, BODIES

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "light.html"
fails = []

c, h, k, eV, b_w, sig = 299792458.0, 6.62607015e-34, 1.380649e-23, 1.602176634e-19, 2.897771955e-3, 5.670374419e-8


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


def planck(lam, T):
    x = h * c / (lam * k * T)
    return 0.0 if x > 700 else 2 * h * c * c / lam ** 5 / math.expm1(x)


def vis_share(T, n=4000):
    a, b = 380e-9, 750e-9
    s = sum(planck(a + (b - a) * (i + 0.5) / n, T) for i in range(n)) * (b - a) / n
    return s * math.pi / (sig * T ** 4)


def total_check(T, n=20000):
    """The whole curve integrated over a log grid should give sigma T^4 / pi."""
    lo, hi = math.log(1e-9), math.log(1e-1)
    s = 0.0
    for i in range(n):
        u = lo + (hi - lo) * (i + 0.5) / n
        lam = math.exp(u)
        s += planck(lam, T) * lam * (hi - lo) / n
    return s * math.pi / (sig * T ** 4)


print("--- the data ---")
check([b[2] for b in BANDS][1:] == [b[3] for b in BANDS][:-1], "the seven bands tile the line, each starting where the last ends")
check(BANDS[0][2] == 1e-14 and BANDS[-1][3] == 1e4, "from 10 fm to 10 km")
vis = next(b for b in BANDS if b[0] == "visible")
check(vis[2] == 3.8e-7 and vis[3] == 7.5e-7, "the visible band is 380 to 750 nm")
check(all(BANDS[0][2] <= m[2] <= BANDS[-1][3] and m[5] for m in MARKS), f"{len(MARKS)} marks, each on the line and sourced")
check(all(WINDOWS[i][1] < WINDOWS[i + 1][0] for i in range(len(WINDOWS) - 1)), "the windows are in order and do not overlap")
check(all(BODIES[i][2] < BODIES[i + 1][2] for i in range(len(BODIES) - 1)), "the bodies rise in temperature")
check(abs(total_check(5772) - 1) < 2e-3, f"Planck integrated over all wavelengths gives sigma T^4 ({total_check(5772):.4f} of it)")
sun_share = vis_share(5772)
check(0.40 < sun_share < 0.46, f"the Sun puts {sun_share * 100:.1f}% of its power into 380 to 750 nm")
check(abs(b_w / 5772 - 5.02e-7) < 1e-9, "Wien: the Sun peaks at 502 nm")
check(abs(b_w / 2.72548 - 1.063e-3) < 2e-6, "the microwave background peaks at 1.063 mm")
check(abs(b_w / 310 - 9.35e-6) < 2e-8, "a person peaks at 9.35 microns")
# the marks' own claims
mk = {m[0]: m for m in MARKS}
check(abs(h * c / mk["annih"][2] / eV - 511e3) / 511e3 < 1e-3, "annihilation photons carry 511 keV")
check(abs(c / mk["h21"][2] - 1420e6) / 1420e6 < 2e-3, "21 cm is 1420 MHz")
check(abs(c / mk["oven"][2] - 2.45e9) / 2.45e9 < 2e-3, "12.2 cm is 2.45 GHz")
check(abs(c / mk["fm"][2] - 1e8) / 1e8 < 1e-3 and abs(c / mk["am"][2] - 1e6) / 1e6 < 1e-3, "FM at 100 MHz, AM at 1 MHz")
check(abs(b_w / 310 - mk["body"][2]) / mk["body"][2] < 0.01, "a person's glow mark sits at the 310 K peak")
check(abs(b_w / 2.72548 - mk["cmb"][2]) / mk["cmb"][2] < 0.002, "the background's mark sits at the 2.725 K peak")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#lsvg")

    def st(q=None):
        return pg.evaluate("(q)=>{const o=window.__light(q); delete o.planck; delete o.visShare; delete o.colour; delete o.wave; delete o.cmf; delete o.SX; delete o.PX; delete o.PY; return o;}", q)

    s = st({"planck": [5.02e-7, 5772], "share": 5772, "colour": 5772})
    check(s["view"] == "spectrum" and abs(s["lam"] - 5.02e-7) < 1e-12, "opens on the spectrum with the marker at the Sun's peak")
    check(abs(s["pv"] / planck(5.02e-7, 5772) - 1) < 1e-9, "the page's Planck agrees with the one here")
    check(abs(s["sv"] - sun_share) < 2e-3, f"and its visible share for the Sun ({s['sv'] * 100:.1f}%)")
    x, y = s["cv"]["x"], s["cv"]["y"]
    check(abs(x - 0.3260) < 0.006 and abs(y - 0.3350) < 0.006, f"the Sun's chromaticity ({x:.4f}, {y:.4f}) sits on the Planckian locus near (0.326, 0.335)")
    s65 = st({"colour": 6504})
    check(abs(s65["cv"]["x"] - 0.3135) < 0.006 and abs(s65["cv"]["y"] - 0.3237) < 0.006, f"6504 K gives ({s65['cv']['x']:.4f}, {s65['cv']['y']:.4f}), the daylight white point's black body")
    # the matching-function fit
    cm = st({"cmf": 555})["cmfv"]
    check(abs(cm[1] - 1.0) < 0.02, f"y-bar peaks near 1 at 555 nm ({cm[1]:.3f})")
    cm = st({"cmf": 445})["cmfv"]
    check(1.5 < cm[2] < 1.9, f"z-bar near its 1.78 peak at 445 nm ({cm[2]:.2f})")
    cm = st({"cmf": 600})["cmfv"]
    check(1.0 < cm[0] < 1.12, f"x-bar near its 1.06 peak at 600 nm ({cm[0]:.2f})")
    wv = {nm: st({"wave": nm})["wv"] for nm in (450, 530, 590, 650)}
    rgb = lambda hx: tuple(int(hx[i:i + 2], 16) for i in (1, 3, 5))
    check(rgb(wv[450])[2] > rgb(wv[450])[0] and rgb(wv[530])[1] > max(rgb(wv[530])[0], rgb(wv[530])[2]) and rgb(wv[650])[0] > 3 * rgb(wv[650])[1],
          f"450 nm is blue {wv[450]}, 530 green {wv[530]}, 650 red {wv[650]}")
    # positions
    L, R, LOG0, LOG1 = 40, 940, -14, 4
    SX = lambda m: L + (math.log10(m) - LOG0) / (LOG1 - LOG0) * (R - L)
    check(abs(s["marker"] - SX(5.02e-7)) < 0.6, "the marker sits at the log position of 502 nm")
    wins = sorted(s["windows"])
    want = sorted([(SX(a), SX(b) - SX(a)) for a, b, _ in WINDOWS])
    check(len(wins) == len(want) and all(abs(w[0] - v[0]) < 0.6 for w, v in zip(wins, want)), "the seven windows are drawn at their wavelengths")
    check("597 THz" in s["card"] and "2.47 eV" in s["card"] and "5,772 K" in s["card"], "the card: 597 THz, 2.47 eV, a body at 5,772 K")
    # hover a mark and press a preset
    pg.evaluate("()=>document.querySelector('#lsvg g[data-k=\"h21\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(100)
    check("1.42 GHz" in pg.inner_text("#numTxt") and "hydrogen line" in pg.inner_text("#nameTxt"), "hovering the 21 cm mark: 1.42 GHz on the card")
    pg.click('#jumps button[data-k="fm"]')
    pg.wait_for_timeout(100)
    s = st()
    check(abs(s["lam"] - 3.0) < 1e-9 and abs(s["marker"] - SX(3.0)) < 0.6 and "no, the air" not in s["card"] and "radio window" in s["card"], "the FM preset moves the marker to 3 m, inside the radio window")
    # drag the marker
    box = pg.eval_on_selector("#lsvg", "e=>{const r=e.getBoundingClientRect(); return {x:r.left,y:r.top,w:r.width,h:r.height, vh:e.viewBox.baseVal.height}}")
    sx = lambda px: box["x"] + px / 980 * box["w"]
    sy = lambda py: box["y"] + py / box["vh"] * box["h"]
    pg.mouse.move(sx(SX(1e-9)), sy(150))
    pg.mouse.down()
    pg.mouse.move(sx(SX(1e-5)), sy(150), steps=5)
    pg.mouse.up()
    pg.wait_for_timeout(100)
    s = st()
    check(abs(math.log10(s["lam"]) + 5) < 0.02 and "infrared" in s["card"], f"dragging the marker lands it at {s['lam']:.3g} m, in the infrared")
    check("thermal infrared window" in s["card"], "and 10 microns reaches the ground through the thermal window")

    pg.click('#views button[data-v="body"]')
    pg.wait_for_timeout(150)
    s = st()
    check(s["view"] == "body" and abs(s["T"] - 5772) < 1 and "43.8%" in s["card"] and "502 nm" in s["card"], "the hot-body view opens on the Sun: peak 502 nm, 43.8% visible")
    # the curve peaks where Wien says, read off the drawn path
    pk = pg.evaluate("""()=>{const p=[...document.querySelectorAll('#lsvg path')].find(p=>p.getAttribute('stroke-width')==='2.5');
      const pts=p.getAttribute('d').slice(1).split(/[ML]/).map(s=>s.split(',').map(Number)); let best=pts[0]; for(const q of pts) if(q[1]<best[1]) best=q;
      const o=window.__light(); return {x:best[0], y:best[1], wx:o.PX(2.897771955e-3/5772), wy:o.PY(o.planck(2.897771955e-3/5772,5772))};}""")
    check(abs(pk["x"] - pk["wx"]) < 3 and abs(pk["y"] - pk["wy"]) < 1.5, "the drawn Sun curve peaks at Wien's wavelength")
    pg.click('#bodies button[data-t="310"]')
    pg.wait_for_timeout(100)
    s = st()
    check(abs(s["T"] - 310) < 0.5 and "9.35" in s["card"] and "no visible glow" in s["card"] and "524 W" in s["card"], "a person: peak 9.35 microns, 524 W per square metre, no visible glow")
    pg.click('#bodies button[data-t="40000"]')
    pg.wait_for_timeout(100)
    s = st({"share": 40000})
    check("72.4 nm" in s["card"] and abs(s["sv"] - vis_share(40000)) < 2e-3, f"Zeta Puppis: peak 72.4 nm, {s['sv'] * 100:.1f}% visible")
    pg.evaluate("()=>{const s=document.getElementById('temp'); s.value=Math.round(Math.log10(2700)*1000); s.dispatchEvent(new Event('input'));}")
    pg.wait_for_timeout(100)
    s = st({"colour": 2700})
    r, g_, b_ = rgb(s["cv"]["hex"])
    check(r > g_ > b_ and "tungsten" in pg.inner_text("#nameTxt"), f"a tungsten bulb at 2700 K is orange {s['cv']['hex']} and the card names it")
    shaded = pg.evaluate("()=>[...document.querySelectorAll('#lsvg rect[opacity=\"0.13\"]')].length")
    check(shaded == 74, f"the visible band is shaded in {shaded} slices")
    check(not errs, "no script errors", "; ".join(errs))
    br.close()

print("--- the copy ---")
html = PAGE.read_text()
check("—" not in html, "no em dashes")

print()
if fails:
    print(f"{len(fails)} FAILED:")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("everything squares")
