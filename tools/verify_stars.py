"""Check stars.html against its data, against physics, and against its drawing.

  the data     every star has a temperature, luminosity and class; the class
               agrees with the temperature; the main sequence rises with mass
  the physics  the radius worked from L and T gives the Sun one solar radius
               and Betelgeuse hundreds; the lifetime scaling gives the Sun ten
               billion years and a forty-sun star about a million; the ends
               by mass are white dwarf, neutron star, black hole
  the drawing  every star sits at its log position; the radius lines are
               where L = R^2 T^4 says; the life slider moves the star; the
               hot end is on the left
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from stars_data import STARS, CLASSES, MAIN_SEQUENCE

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "stars.html"
fails = []


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


def cls(T):
    for c, lo, hi, _ in CLASSES:
        if lo <= T < hi:
            return c
    return "O" if T >= 29000 else "M"


print("--- the data ---")
check(all(s[1] > 0 and s[2] > 0 and s[3] and s[7] for s in STARS), f"{len(STARS)} stars, each with T, L, a class and a line")
# the letter in the published class matches the temperature band
bad = [s[0] for s in STARS if s[3][0] in "OBAFGKM" and s[3][0] != cls(s[1])]
check(not bad, "every published spectral letter agrees with the temperature band", str(bad))
check(all(MAIN_SEQUENCE[i][0] > MAIN_SEQUENCE[i-1][0] and MAIN_SEQUENCE[i][1] > MAIN_SEQUENCE[i-1][1]
          and MAIN_SEQUENCE[i][2] > MAIN_SEQUENCE[i-1][2] for i in range(1, len(MAIN_SEQUENCE))),
      "the main sequence rises in temperature and luminosity with mass")
sun = next(s for s in STARS if s[0] == "the Sun")
check(sun[1] == 5772 and sun[2] == 1.0 and sun[4] == 1.0, "the Sun is 5772 K, 1 L, 1 M")
R = lambda T, L: math.sqrt(L) * (5772 / T) ** 2
check(abs(R(5772, 1) - 1) < 1e-9, "the radius formula gives the Sun one solar radius")
bet = next(s for s in STARS if s[0] == "Betelgeuse")
check(700 < R(bet[1], bet[2]) < 1000, f"and Betelgeuse {R(bet[1], bet[2]):.0f} solar radii, against the published 640 to 900")
sb = next(s for s in STARS if s[0] == "Sirius B")
check(0.005 < R(sb[1], sb[2]) < 0.015, f"and Sirius B {R(sb[1], sb[2]):.4f}, about the Earth's size (0.0092)")

print("--- the drawing and the life ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#hsvg")
    st = pg.evaluate("()=>window.__stars()")
    check(st["mass"] == 1 and abs(st["lifetime"] - 10) < 1e-9, "the page opens on the Sun, with a ten billion year main sequence")
    for m, lo, hi in [(0.2, 200, 2000), (10, 0.01, 0.03), (40, 0.0005, 0.0015)]:
        t = pg.evaluate("(m)=>lifetime(m)", m)
        check(lo < t < hi, f"a {m} sun star lasts {t:.4f} billion years on the main sequence")
    # positions
    pos = pg.evaluate("""()=>[...document.querySelectorAll('#hsvg g[data-i]')].map(g=>{const c=g.querelector?null:g.querySelectorAll('circle')[0];
      return [+c.getAttribute('cx'),+c.getAttribute('cy')];})""")
    LT0, LT1 = math.log10(120000), math.log10(2300)
    X = lambda T: 88 + (math.log10(T) - LT0) / (LT1 - LT0) * 850
    Y = lambda L: 36 + 610 - (math.log10(L) + 5) / 11.5 * 610
    worst = max(max(abs(pos[i][0] - X(s[1])), abs(pos[i][1] - Y(s[2]))) for i, s in enumerate(STARS))
    check(worst < 0.1, f"every star sits at its log position (worst {worst:.3f}px out)")
    check(X(40000) < X(3000), "the hot end is on the left, as Russell drew it")
    # the ends by mass
    ends = {m: pg.evaluate("(m)=>at(m,1.0).phase", m) for m in (0.3, 1, 5, 15, 30)}
    check("helium white dwarf" in ends[0.3] and "planetary nebula" in ends[1] and "planetary nebula" in ends[5],
          "under eight suns the end is a white dwarf")
    check("neutron star" in ends[15] and "black hole" in ends[30],
          "fifteen suns leave a neutron star, thirty a black hole")
    # the Sun's giant stage reaches a few thousand suns and a radius past the Earth's orbit
    tip = pg.evaluate("()=>at(1,0.97)")
    r_tip = R(tip["T"], tip["L"])
    check(1000 < tip["L"] < 5000 and 150 < r_tip < 300,  # Sackmann 1993 gives 166, Schroeder 2008 gives 256
          f"the Sun's red giant tip: {tip['L']:.0f} Suns of light, {r_tip:.0f} solar radii (the Earth's orbit is 215)")
    # the life slider moves the drawn star
    pg.evaluate("()=>setLife(0.5)")
    a = pg.evaluate("()=>{const c=document.querySelector('#hsvg circle[data-now]');return [+c.getAttribute('cx'),+c.getAttribute('cy')];}")
    pg.evaluate("()=>setLife(0.97)")
    b = pg.evaluate("()=>{const c=document.querySelector('#hsvg circle[data-now]');return [+c.getAttribute('cx'),+c.getAttribute('cy')];}")
    check(b[0] > a[0] + 80 and b[1] < a[1] - 150, f"the life slider carries the Sun up and to the right, from {a} to {b}")
    pg.evaluate("()=>{setMass(40);setLife(1.0)}")
    gone = pg.evaluate("()=>document.querySelector('#hsvg circle[data-now]')===null")
    check(gone and "black hole" in pg.evaluate("()=>document.getElementById('numTxt').textContent"),
          "a forty sun star at the end of its life has left the diagram, and the card says black hole")
    # radius lines where physics puts them: on the R = 1 line, L = (T/5772)^4
    pg.evaluate("()=>setMass(1)")
    lines = pg.evaluate("""()=>[...document.querySelectorAll('#hsvg polyline')].filter(p=>p.getAttribute('stroke-dasharray'))
      .map(p=>p.getAttribute('points').trim().split(/\\s+/).map(q=>q.split(',').map(Number)))""")
    def on_line(pts, Rr):
        worst = 0
        for x, y in pts[::20]:
            T = 10 ** (LT0 + (x - 88) / 850 * (LT1 - LT0)); L = 10 ** (-5 + (36 + 610 - y) / 610 * 11.5)
            worst = max(worst, abs(math.log10(L) - math.log10(Rr * Rr * (T / 5772) ** 4)))
        return worst
    Rs = [0.001, 0.01, 0.1, 1, 10, 100, 1000]
    worst = max(on_line(pts, Rs[i]) for i, pts in enumerate(lines))
    check(len(lines) == 7 and worst < 0.02, f"seven radius lines, each where L = R^2 T^4 (worst {worst:.4f} dex)")
    # hovering a star fills the card
    pg.evaluate("()=>document.querySelector('#hsvg g[data-i=\"33\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(100)
    txt = pg.evaluate("()=>document.getElementById('nameTxt').textContent+' | '+document.getElementById('numTxt').textContent")
    check(txt.startswith("Betelgeuse") and "M" in txt and "supergiant" in pg.evaluate("()=>document.getElementById('kindTxt').textContent").lower(),
          f"Betelgeuse's card: '{txt[:80]}'")
    check(not errs, "no script errors", "; ".join(errs))
    br.close()

print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("everything squares")
