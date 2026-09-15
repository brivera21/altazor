"""Check forces.html against its data and its drawing.

  the data     four forces with couplings and reaches; the marks on the
               newton line each carry a force, a size and a source, and the
               ones that can be worked from constants are
  the physics  Coulomb and Newton between two protons, the Yukawa forces,
               the couplings from CODATA and the PDG, all worked here and
               compared with the page's numbers at several distances; the
               classic ratios (strong over electromagnetism about a hundred
               at 1 fm, electromagnetism over gravity 1.24e36)
  the drawing  the four curves, the marker's dots on them, the presets, the
               marks at their log positions, the card's plain words
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from forces_data import FOUR, PLACES, FORCES

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "forces.html"
fails = []

G, hbar, c, e, eps0 = 6.67430e-11, 1.054571817e-34, 299792458.0, 1.602176634e-19, 8.8541878128e-12
m_p, m_e, a0 = 1.67262192369e-27, 9.1093837015e-31, 5.29177210903e-11
hbarc = hbar * c
alpha = e * e / (4 * math.pi * eps0 * hbarc)
alpha_G = G * m_p * m_p / hbarc
MeV = 1e6 * e
m_W, m_pi, sin2 = 80377 * MeV, 139.57 * MeV, 0.231       # PDG 2024, rounded
lam_W, lam_pi = hbarc / m_W, hbarc / m_pi
k_e = 1 / (4 * math.pi * eps0)


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


def yukawa(a, lam, r):
    u = r / lam
    return a * hbarc / r ** 2 * (1 + u) * math.exp(-u)


print("--- the data ---")
f = {x[0]: x for x in FOUR}
check(list(f) == ["strong", "em", "weak", "gravity"], "the four, in the order strong, electromagnetism, weak, gravity")
check(abs(f["em"][3] - alpha) / alpha < 1e-6, f"the fine-structure constant, 1/{1 / alpha:.3f}")
check(abs(f["gravity"][3] - alpha_G) / alpha_G < 2e-3, f"gravity's coupling G m_p^2 / hbar c = {alpha_G:.3e}")
check(abs(f["weak"][3] - alpha / sin2) / (alpha / sin2) < 0.01, f"the weak coupling alpha / sin^2 theta_W = 1/{sin2 / alpha:.1f}")
check(abs(f["weak"][4] - lam_W) / lam_W < 1e-3, f"the W's reach hbar/(m_W c) = {lam_W * 1e15:.5f} fm")
check(abs(f["strong"][4] - lam_pi) / lam_pi < 1e-3, f"the pion's reach hbar/(m_pi c) = {lam_pi * 1e15:.3f} fm")
check(f["em"][4] is None and f["gravity"][4] is None, "electromagnetism and gravity have no reach limit")
pl = {p[0]: p for p in PLACES}
check(abs(pl["w"][2] - lam_W) / lam_W < 0.01 and abs(pl["pion"][2] - lam_pi) / lam_pi < 0.01 and abs(pl["bohr"][2] - a0) / a0 < 1e-5, "the places: the W's reach, the pion's reach, the Bohr radius")
fo = {x[0]: x for x in FORCES}
check(all(x[3] in f and x[2] > 0 and x[6] for x in FORCES), f"{len(FORCES)} marks, each with a force, a size and a source")
check(all(FORCES[i][2] < FORCES[i + 1][2] for i in range(len(FORCES) - 1)), "the marks rise in size")
# the ones that follow from constants
hg = G * m_p * m_e / a0 ** 2
he = k_e * e * e / a0 ** 2
check(abs(fo["hgrav"][2] - hg) / hg < 0.01, f"gravity in hydrogen {hg:.3e} N")
check(abs(fo["hydrogen"][2] - he) / he < 0.01, f"the electric pull in hydrogen {he:.3e} N")
check(abs(he / hg - 2.27e39) / 2.27e39 < 0.01, f"and their ratio {he / hg:.3e}")
tp = G * 70 * 70 / 1
check(abs(fo["twopeople"][2] - tp) / tp < 0.02, f"two 70 kg people a metre apart {tp:.2e} N")
em = G * 5.9722e24 * 7.346e22 / 3.844e8 ** 2
check(abs(fo["moon"][2] - em) / em < 0.01, f"Earth on Moon {em:.3e} N")
se = G * 1.9885e30 * 5.9722e24 / 1.495978707e11 ** 2
check(abs(fo["sun"][2] - se) / se < 0.01, f"Sun on Earth {se:.3e} N")
pf = c ** 4 / G
check(abs(fo["planck"][2] - pf) / pf < 0.01, f"the Planck force c^4/G {pf:.3e} N")
qq = 1e9 * e / 1e-15
check(abs(fo["quarks"][2] - qq) / qq < 0.01, f"1 GeV per fm is {qq:.2e} N, {qq / 9.80665 / 1000:.1f} tonnes")
check(abs(fo["person"][2] - 70 * 9.80665) / 686 < 0.01 and abs(fo["car"][2] - 1500 * 9.80665) / 14710 < 0.02 and abs(fo["mosquito"][2] - 2.5e-6 * 9.80665) / 2.45e-5 < 0.03,
      "the weights: 70 kg, 1,500 kg, 2.5 mg")
check(fo["croc"][2] == 1.64e4 and fo["bond"][2] == 2.0e-9, "the crocodile's 16.4 kN and the bond's 2.0 nN as published")

print("--- the physics on the page ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1000})
    errs = []
    pg.on("pageerror", lambda x: errs.append(str(x)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#fsvg")

    def st(q=None):
        return pg.evaluate("(q)=>window.__forces(q)", q)

    for r in (1e-18, 2.45e-18, 1e-16, 1e-15, 3e-15, 1e-13, 5.29e-11):
        mine = [yukawa(f["strong"][3], f["strong"][4], r), alpha * hbarc / r ** 2, yukawa(f["weak"][3], f["weak"][4], r), alpha_G * hbarc / r ** 2]
        page = st({"force": r})["fv"]
        ok = all((a == 0 and b < 1e-100) or abs(a / b - 1) < 0.02 for a, b in zip(mine, page))
        check(ok, f"at {r:.3g} m the four agree: " + ", ".join(f"{v:.2e}" for v in page), str(mine))
    p1 = st({"force": 1e-15})["fv"]
    check(100 < p1[0] / p1[1] < 130, f"at 1 fm the strong force is {p1[0] / p1[1]:.0f} times electromagnetism")
    check(abs(p1[1] / p1[3] - 1.24e36) / 1.24e36 < 0.01, f"electromagnetism over gravity is {p1[1] / p1[3]:.3e} at any distance")
    check(p1[2] < 1e-100, "and the weak force is gone at 1 fm")
    p2 = st({"force": 1e-18})["fv"]
    check(p2[2] > p2[1], f"at 0.001 fm the weak force ({p2[2]:.2e} N) beats electromagnetism ({p2[1]:.2e} N)")
    p3 = st({"force": 3e-15})["fv"]
    check(p3[0] / p3[1] < 60 and p3[0] > p3[1], f"at 3 fm the strong force is down to {p3[0] / p3[1]:.0f} times electromagnetism")
    p4 = st({"force": 1.2e-14})["fv"]
    check(p4[0] < p4[1], "and by 12 fm electromagnetism has overtaken the one-pion tail")

    print("--- the drawing ---")
    s = st({"PX": 1e-15, "PY": 230.7})
    check(s["view"] == "four" and s["curves"] == 4 and abs(s["r"] - 1e-15) < 1e-20, "opens on the four with the marker at 1 fm")
    check(abs(s["marker"] - s["px"]) < 0.6, "the marker line stands at 1 fm")
    dots = dict(s["dots"])
    check(abs(dots.get("#ffb02e", 0) - s["py"]) < 1.5, "the electromagnetism dot sits on the curve at 231 N")
    check("#9be564" not in dots and len(dots) == 3, "no dot for the weak force there, it is off the bottom")
    check("26.6 kN" in s["card"] and "115×" in s["card"] and "231 N" in s["card"] and "1.87×10-34 N" in s["card"] and "nothing to speak of" in s["card"],
          "the card: 26.6 kN at 115 times, 231 N, 1.87e-34 N, the weak force nothing to speak of")
    pg.click('#places button[data-m="5.29177e-11"]')
    pg.wait_for_timeout(100)
    s = st()
    check(abs(s["r"] - 5.29177e-11) < 1e-16 and "Bohr radius" in pg.inner_text("#bodyTxt") and len(dict(s["dots"])) == 2, "the Bohr radius preset: only two forces left on the plot")
    pg.evaluate("()=>document.querySelector('#fsvg g[data-f=\"weak\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(100)
    check("the weak force" in pg.inner_text("#nameTxt") and "1/31" in pg.inner_text("#numTxt") and "0.0024" in pg.inner_text("#numTxt") and "nothing to speak of" in pg.inner_text("#numTxt"), "hovering the weak curve: coupling 1/31.6, reach 0.00245 fm, nothing at 1 fm")
    # drag inside the plot
    box = pg.eval_on_selector("#fsvg", "e=>{const r=e.getBoundingClientRect(); return {x:r.left,y:r.top,w:r.width,h:r.height,vh:e.viewBox.baseVal.height}}")
    sx = lambda px: box["x"] + px / 980 * box["w"]
    sy = lambda py: box["y"] + py / box["vh"] * box["h"]
    pg.mouse.move(sx(500), sy(300))
    pg.mouse.down()
    pg.mouse.move(sx(84 + 850 * (2 / 9)), sy(300), steps=4)     # 10^-17 m
    pg.mouse.up()
    pg.wait_for_timeout(100)
    s = st()
    check(abs(math.log10(s["r"]) + 17) < 0.02, f"dragging lands the marker at {s['r']:.2e} m")

    pg.click('#views button[data-v="line"]')
    pg.wait_for_timeout(150)
    s = st({"SX": 690, "weight": 3.5e7})
    check(s["view"] == "line" and s["marks"] == len(FORCES), f"the newton line draws {s['marks']} marks")
    L, R, LOG0, LOG1 = 40, 940, -48, 45
    SX = lambda N: L + (math.log10(N) - LOG0) / (LOG1 - LOG0) * (R - L)
    check(abs(s["sx"] - SX(690)) < 0.6, "690 N lands at its log position")
    check(s["wv"] == "the weight of 3,569 tonnes", f"35 MN reads as {s['wv']}")
    check("a person's weight" in s["name"] and "70.4 kg" in s["card"] and "gravity" in s["card"], "the card opens on a person's weight, 70.4 kg, gravity")
    pg.click('#jumps button[data-k="quarks"]')
    pg.wait_for_timeout(100)
    s = st()
    check("16.3 tonnes" in s["card"] and "the strong force" in s["card"], "the quark string: 16.3 tonnes, the strong force")
    pg.evaluate("()=>document.querySelector('#fsvg g[data-k=\"hgrav\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(100)
    s = st()
    check("gravity inside a hydrogen atom" in s["name"] and "in plain terms" not in s["card"], "hovering the smallest mark: no weight in plain terms for 10^-47 N")
    over = pg.evaluate("()=>{const svg=document.querySelector('#fsvg'); let n=0; for(const t of svg.querySelectorAll('text')){ const b=t.getBBox(); if(b.x<0||b.x+b.width>980) n++; } return n;}")
    check(over == 0, "no label runs off either edge", f"{over}")
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
