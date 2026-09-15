"""Check color.html against its data, against the CIE tables, and against
its drawing.

  the data     four receptors at Bowmaker and Dartnall's peaks; the counts
               are Curcio's; the sRGB primaries and D65 are the standard
               ones; eleven terms in seven stages in Berlin and Kay's order
  the sums     the page's spectral locus lies within 0.02 of the CIE 1931
               table at a dozen wavelengths; the black-body curve passes
               through the tabulated points for 2,856 K (illuminant A) and
               6,504 K (D65) within 0.005; the sRGB primaries' dominant
               wavelengths come out at 611, 549 and 464 nm; the white
               point has none
  the drawing  the curves and swatches answer; the markers drag and the
               cards follow; no label overlaps another
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from color_data import RECEPTORS, COUNTS, SRGB, POINTS, TERMS, STAGES

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "color.html"
fails = []


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


# CIE 1931 2-degree chromaticities of the spectral locus, from the standard table
CIE = {420: (0.1714, 0.0051), 460: (0.1440, 0.0297), 480: (0.0913, 0.1327), 500: (0.0082, 0.5384), 510: (0.0139, 0.7502), 520: (0.0743, 0.8338),
       540: (0.2296, 0.7543), 560: (0.3731, 0.6245), 580: (0.5125, 0.4866), 600: (0.6270, 0.3725), 620: (0.6915, 0.3083), 640: (0.7190, 0.2809), 660: (0.7300, 0.2700)}
print("--- the data ---")
pk = {r[0]: r[2] for r in RECEPTORS}
check(pk == {"s": 420, "m": 534, "l": 564, "rod": 498}, "the receptors peak at 420, 534, 564 and 498 nm")
check(COUNTS["cones"] == 4.6e6 and COUNTS["rods"] == 92e6 and COUNTS["fovea_per_mm2"] == 199000, "4.6 million cones, 92 million rods, 199,000 a square millimeter")
check(SRGB == {"r": (0.64, 0.33), "g": (0.30, 0.60), "b": (0.15, 0.06), "w": (0.3127, 0.3290)}, "the sRGB primaries and D65")
check(len(TERMS) == 11 and [t[0] for t in TERMS] == sorted(t[0] for t in TERMS) and [t[1] for t in TERMS][:3] == ["black", "white", "red"] and TERMS[5][1] == "blue" and TERMS[6][1] == "brown", "eleven terms in order: black and white, red, green and yellow, blue, brown, then the last four")
check(set(STAGES) == set(range(1, 8)), "seven stages")

print("--- the sums ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1100})
    errs = []
    pg.on("pageerror", lambda x: errs.append(str(x)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#csvg")

    def st(q=None):
        return pg.evaluate("(q)=>window.__color(q)", q)

    loc = {p[2]: (p[0], p[1]) for p in st({"locus": list(CIE)})["locus"]}
    worst = max(math.hypot(loc[nm][0] - CIE[nm][0], loc[nm][1] - CIE[nm][1]) for nm in CIE)
    check(worst < 0.02, f"the spectral locus lies within {worst:.4f} of the CIE table at {len(CIE)} wavelengths")
    a = st({"T": 2856})["planck"]
    d65 = st({"T": 6504})["planck"]
    check(math.hypot(a[0] - 0.4476, a[1] - 0.4074) < 0.005 and math.hypot(d65[0] - 0.3135, d65[1] - 0.3237) < 0.005, f"the black-body curve passes illuminant A ({a[0]:.4f}, {a[1]:.4f}) and 6,504 K ({d65[0]:.4f}, {d65[1]:.4f})")
    r, g, b = (st({"xy": list(SRGB[k])}) for k in ("r", "g", "b"))
    check(abs(r["dom"]["nm"] - 611) < 2 and abs(g["dom"]["nm"] - 549) < 2 and abs(b["dom"]["nm"] - 464) < 3, f"the primaries' dominant wavelengths: {r['dom']['nm']:.0f}, {g['dom']['nm']:.0f}, {b['dom']['nm']:.0f} nm")
    check(r["inside"] and g["inside"] and b["inside"] and r["hex"] == "#ff0000" and g["hex"] == "#00ff00" and b["hex"] == "#0000ff", "the primaries sit on the triangle and come out pure red, green and blue")
    w = st({"xy": list(SRGB["w"])})
    check(w["dom"] is None and w["hex"] == "#ffffff", "the white point has no dominant wavelength and comes out white")
    p = st({"xy": [0.45, 0.2]})
    check(p["dom"]["purple"] and 495 < p["dom"]["comp"] < 510 and not p["inside"], "a purple below the white point reports the complement of a green near 500 nm and lies outside the triangle")
    check(not st({"xy": [0.05, 0.1]})["inHorse"] and st({"xy": [0.3, 0.3]})["inHorse"], "the horseshoe test: (0.05, 0.1) is outside, (0.3, 0.3) inside")
    resp = st({"nm": 534})["resp"]
    check(abs(resp[1] - 1) < 1e-9 and resp[0] < 0.01 and 0.7 < resp[2] < 0.9, "at 534 nm the M cone is at its peak, S near zero, L between 70 and 90 percent")

    print("--- the drawing ---")
    def overlaps(sel):
        boxes = pg.evaluate("(sel)=>[...document.querySelectorAll(sel)].filter(t=>!t.hasAttribute('transform')).map(t=>{const b=t.getBBox(); return [b.x,b.y,b.width,b.height]})", sel)
        return sum(1 for i in range(len(boxes)) for j in range(i + 1, len(boxes)) if boxes[i][0] < boxes[j][0] + boxes[j][2] and boxes[j][0] < boxes[i][0] + boxes[i][2] and boxes[i][1] < boxes[j][1] + boxes[j][3] and boxes[j][1] < boxes[i][1] + boxes[i][3])

    s = st()
    check(s["view"] == "eye" and s["curves"] == 4 and s["lam"] == 550 and "4.6 million" in s["card"], "opens on the eye: four curves, the marker at 550 nm")
    E = {"x": 80, "w": 820, "a": 380, "b": 750}
    EX = lambda nm: E["x"] + (nm - E["a"]) / (E["b"] - E["a"]) * E["w"]
    box = pg.eval_on_selector("#csvg", "e=>{const r=e.getBoundingClientRect(); return {x:r.left,y:r.top,w:r.width,h:r.height,vh:e.viewBox.baseVal.height}}")
    sx = lambda px: box["x"] + px / 980 * box["w"]
    sy = lambda py: box["y"] + py / box["vh"] * box["h"]
    pg.mouse.move(sx(EX(550)), sy(200))
    pg.mouse.down()
    pg.mouse.move(sx(EX(620)), sy(200), steps=5)
    pg.mouse.up()
    pg.wait_for_timeout(100)
    s = st()
    check(abs(s["lam"] - 620) <= 1 and abs(s["marker"] - EX(s["lam"])) < 0.6 and "red" in s["name"] and "red or orange" in s["body"], f"dragging the marker to {s['lam']} nm: the card reads red, L well ahead of M")
    pg.evaluate("()=>document.querySelector('#csvg path[data-rec=\"rod\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(80)
    s = st()
    check(s["name"] == "rods" and "92 million" in s["card"] and "498 nm" in s["card"], "hovering the rods: 498 nm, 92 million")
    check(overlaps("#csvg text") == 0, "no two labels overlap on the eye", f"{overlaps('#csvg text')}")
    pg.click('#views button[data-v="gamut"]')
    pg.wait_for_timeout(700)
    s = st()
    check(s["view"] == "gamut" and pg.evaluate("()=>!!document.querySelector('#gcanvas')") and "this is white" in s["card"], "the gamut view opens on the white point")
    P = {"x0": 100, "y0": 600, "s": 640}
    PX = lambda x: P["x0"] + x * P["s"]
    PY = lambda y: P["y0"] - y * P["s"]
    cbox = pg.eval_on_selector("#gcanvas", "e=>{const r=e.getBoundingClientRect(); return {x:r.left,y:r.top,w:r.width,h:r.height}}")
    cx = lambda px: cbox["x"] + px / 980 * cbox["w"]
    cy = lambda py: cbox["y"] + py / 640 * cbox["h"]
    pg.mouse.move(cx(PX(0.3127)), cy(PY(0.329)))
    pg.mouse.down()
    pg.mouse.move(cx(PX(0.60)), cy(PY(0.35)), steps=5)
    pg.mouse.up()
    pg.wait_for_timeout(200)
    s = st()
    check(abs(s["mk"]["x"] - 0.60) < 0.003 and abs(s["mk"]["y"] - 0.35) < 0.003 and "x = 0.600" in s["name"] and "nm, orange" in s["card"] and "inside the sRGB triangle" in s["card"], "dragging the marker to (0.60, 0.35): an orange inside the triangle")
    pg.mouse.move(cx(PX(0.60)), cy(PY(0.35)))
    pg.mouse.down()
    pg.mouse.move(cx(PX(0.10)), cy(PY(0.70)), steps=5)
    pg.mouse.up()
    pg.wait_for_timeout(200)
    s = st()
    check(abs(s["mk"]["x"] - 0.10) < 0.003 and "outside the triangle" in s["card"] and "green" in s["card"], "and to (0.10, 0.70): a green no screen can show")
    pg.mouse.move(cx(PX(0.10)), cy(PY(0.70)))
    pg.mouse.down()
    pg.mouse.move(cx(PX(0.75)), cy(PY(0.75)), steps=5)
    pg.mouse.up()
    pg.wait_for_timeout(200)
    s = st()
    check(s["mk"]["x"] < 0.75 and st({"xy": [s["mk"]["x"], s["mk"]["y"]]})["inHorse"], "a drag out of the horseshoe stops the marker at its edge")
    pg.click('#views button[data-v="names"]')
    pg.wait_for_timeout(150)
    s = st()
    check(s["view"] == "names" and s["swatches"] == 11, "the names view: eleven swatches")
    pg.evaluate("()=>document.querySelector('#csvg g[data-term=\"5\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(80)
    s = st()
    check("blue" in s["name"] and "stage 5 of 7" in s["card"] and "grue" in s["body"], "hovering blue: stage 5, grue")
    pg.evaluate("()=>document.querySelector('#csvg g[data-stage=\"1\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(80)
    s = st()
    check("two terms" in s["name"] and "Dani" in s["card"], "hovering stage I: two terms, the Dani")
    check(overlaps("#csvg text") == 0, "no two labels overlap in the names view", f"{overlaps('#csvg text')}")
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
