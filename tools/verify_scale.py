"""Check scale.html against its data and against its drawing.

  the data     every length is positive, sourced and placed in a realm; the
               constants match CODATA and the IAU; the line runs from the
               Planck length to the observable universe, in order
  the drawing  marks sit at log position; the lens draws what it holds in
               true proportion; two picks give the right ratio; the jumps land
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from scale_data import OBJECTS, REALMS, JUMPS

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "scale.html"
fails = []


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


print("--- the data ---")
by = {o[0]: o for o in OBJECTS}
check(all(o[2] > 0 and o[3] in REALMS and o[5] and o[6] for o in OBJECTS),
      f"{len(OBJECTS)} things, each with a length, a realm, a line and a source")
check(OBJECTS[0][0] == "planck" and OBJECTS[-1][0] == "universe",
      "the line runs from the Planck length to the observable universe")
check(all(OBJECTS[i][2] > OBJECTS[i - 1][2] for i in range(1, len(OBJECTS))),
      "and every step along it is larger than the last")
check(abs(by["planck"][2] - 1.616255e-35) < 1e-41, "the Planck length is CODATA's 1.616255e-35 m")
check(abs(by["au"][2] - 149597870700) < 1, "the astronomical unit is the IAU's 149,597,870,700 m")
check(abs(by["hydrogen"][2] / 2 - 5.29177e-11) < 2e-13, "the hydrogen atom is two Bohr radii")
check(abs(by["mw"][2] / 3.0857e19 - 26.8) < 0.05, "the Milky Way is 26.8 kpc")
span = math.log10(by["universe"][2] / by["planck"][2])
check(61.5 < span < 62.5, f"the whole line spans {span:.1f} decades")
up = math.log10(by["universe"][2] / by["human"][2]); down = math.log10(by["human"][2] / by["planck"][2])
check(abs(up - down) < 10, f"a person stands {down:.0f} decades above the smallest and {up:.0f} below the largest")
check(all(k in by for k, _ in JUMPS), "every jump lands on a thing on the line")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#ssvg")
    st = pg.evaluate("()=>window.__scale()")
    check(st["n"] == len(OBJECTS), f"{st['n']} things on the page")
    # marks at their log position
    xs = pg.evaluate("""()=>Object.fromEntries([...document.querySelectorAll('#ssvg g[data-k]')]
      .filter(g=>g.querySelector('line')).map(g=>[g.dataset.k,+g.querySelectorAll('circle')[0].getAttribute('cx')]))""")
    L, R, LOG0, LOG1 = 40, 940, -35, 27
    worst = max(abs(xs[k] - (L + (math.log10(o[2]) - LOG0) / (LOG1 - LOG0) * (R - L))) for k, o in by.items())
    check(worst < 0.1, f"every mark sits at its log position (worst {worst:.3f}px out)")
    # the lens opens on a person, and the panel draws what it holds in proportion
    check(st["lensW"] == 3 and abs(st["lensC"] - math.log10(1.7)) < 1e-9 and "human" in st["inside"],
          f"the lens opens three decades wide on a person, holding {st['inside']}")
    pg.click('#jumps button[data-j="earth"]')
    pg.wait_for_timeout(100)
    st = pg.evaluate("()=>window.__scale()")
    want = [k for k, o in by.items() if abs(math.log10(o[2]) - math.log10(by['earth'][2])) <= 1.5]
    check(set(st["inside"]) == set(want), f"around the Earth the lens holds {sorted(st['inside'])}")
    rad = pg.evaluate("""()=>{const out={};for(const g of document.querySelectorAll('#ssvg g[data-k]')){
      if(g.querySelector('line')) continue; out[g.dataset.k]=+g.querySelector('circle').getAttribute('r');} return out;}""")
    drawn = [k for k in want if k in rad]
    big = max(drawn, key=lambda k: by[k][2])
    worst = max(abs(rad[k] / rad[big] - by[k][2] / by[big][2]) for k in drawn if rad[k] > 1)
    check(worst < 0.01, f"the panel draws {len(drawn)} of them in true proportion to {big} (worst {worst:.4f})")
    if "moon" in rad and "earth" in rad:
        check(abs(rad["earth"] / rad["moon"] - 12742 / 3474.8) < 0.02,
              f"the Earth is drawn {rad['earth'] / rad['moon']:.2f} Moons across, against 3.67")
    # two picks give the ratio
    pg.evaluate("()=>{pick('sun');pick('earth')}")
    txt = pg.evaluate("()=>document.getElementById('numTxt').textContent")
    check("109" in txt and "2.04" in txt, f"the Sun against the Earth: '{txt[:120]}'")
    # dragging the lens moves it
    box = pg.locator("#ssvg").bounding_box()
    y = box["y"] + 190 / 720 * box["height"]
    x0 = box["x"] + (40 + (0 - LOG0) / (LOG1 - LOG0) * 900) / 980 * box["width"]
    x1 = box["x"] + (40 + (15 - LOG0) / (LOG1 - LOG0) * 900) / 980 * box["width"]
    pg.mouse.move(x0, y + 30); pg.mouse.down(); pg.mouse.move(x1, y + 30, steps=6); pg.mouse.up()
    st = pg.evaluate("()=>window.__scale()")
    check(abs(st["lensC"] - 15) < 0.3, f"a drag along the line carries the lens to 10^{st['lensC']:.1f} m")
    check("ly" in st["inside"] or "proxima" in st["inside"], f"where it finds {st['inside']}")
    # the card links to the page that draws the thing
    pg.evaluate("()=>{picks=[];showOne(OBJ.find(o=>o.k==='mw'))}")
    link = pg.evaluate("()=>document.querySelector('#srcTxt a')?.getAttribute('href')")
    check(link == "galaxies.html", f"the Milky Way's card links to {link}")
    check(not errs, "no script errors", "; ".join(errs))
    br.close()

print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("everything squares")
