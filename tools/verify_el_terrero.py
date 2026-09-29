"""Check el-terrero.html in a headless browser.

The page is hand-built (no builder). This exercises what it does: a town
clicked becomes the center of the rings and its card sums the road to El
Terrero; the arrow keys walk the valley chain; Rectas contra carretera bends
every link into an arc as long as its road km; Acercar al valle zooms the
viewBox; the phone layout opens on the valley without overflowing.

Usage: python3 verify_el_terrero.py
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PAGE = Path(__file__).parent.parent / "el-terrero.html"
fails = []


def check(ok, msg):
    print(("  ok   " if ok else "  FAIL ") + msg)
    if not ok:
        fails.append(msg)


html = PAGE.read_text(encoding="utf-8")
check("—" not in html, "no em dash in the page")

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1300, "height": 850})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.resolve().as_uri())
    pg.wait_for_timeout(500)
    s = pg.evaluate("__et()")
    check(s["center"] == "terrero" and s["rings"] == 4, "opens centered on El Terrero with four rings")
    top = pg.evaluate("document.getElementById('map').getBoundingClientRect().top")
    check(top < 300, f"the map starts in the first screen (top {top:.0f}px)")

    # every arc is as long as its road km, and bows to the side it claims
    pg.click("#btn-arc")
    pg.wait_for_timeout(1300)
    res = pg.evaluate("""()=>[...document.querySelectorAll('#g-links path')].map(l=>{
      const g=l._geo, L=l.getTotalLength(), m=l.getPointAtLength(L/2);
      const sag=g.u<1e-3?0:g.len/(2*Math.sin(g.u))*(1-Math.cos(g.u));
      const ex=(g.x1+g.x2)/2+g.nx*sag, ey=(g.y1+g.y2)/2+g.ny*sag;
      return [l.dataset.a+'-'+l.dataset.b, L/(g.len/g.straight), g.km, Math.hypot(m.x-ex,m.y-ey)];})""")
    bad = [r for r in res if abs(r[1] - r[2]) > 0.2 or r[3] > 1.0]
    check(not bad, f"all {len(res)} arcs match their road km and bow outward {bad[:3]}")
    lbl = pg.evaluate("[...document.querySelectorAll('#g-kms text')].map(t=>t.textContent)")
    check(all("→" in t for t in lbl), "the km labels read straight then road km")
    pg.click("#btn-arc")
    pg.wait_for_timeout(1200)
    check(pg.evaluate("__et().arc") == 0, "a second press straightens them again")

    # a click recenters and sums the road to El Terrero
    pg.evaluate("document.querySelector('.node[data-id=cuauhtemoc] .node-hit')"
                ".dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    s = pg.evaluate("__et()")
    cx = pg.evaluate("document.querySelector('.node[data-id=cuauhtemoc] circle.dot').getAttribute('cx')")
    check(s["center"] == "cuauhtemoc" and abs(s["ringCx"] - float(cx)) < 0.01,
          "a click on Cuauhtémoc moves the rings there")
    check("A El Terrero por carretera: 141 km, por Bachíniva, Soto Maynez" in s["tip"],
          "its card sums 81 + 38 + 22 km to El Terrero")
    pg.keyboard.press("Escape")
    check(pg.evaluate("__et().center") == "terrero", "Escape returns the center to El Terrero")

    pg.focus("#map")
    pg.keyboard.press("ArrowUp")
    pg.keyboard.press("ArrowUp")
    check(pg.evaluate("__et().pinned") == "namiquipa", "two presses of ArrowUp walk to Namiquipa")
    pg.keyboard.press("Escape")

    pg.click("#btn-zoom")
    pg.wait_for_timeout(1100)
    vb = pg.evaluate("__et().vb")
    check(vb[2] < 600, f"Acercar al valle zooms the viewBox to {vb[2]:.0f} wide")
    check(not errs, f"no javascript errors {errs}")

    ph = b.new_page(viewport={"width": 390, "height": 844})
    ph.goto(PAGE.resolve().as_uri())
    ph.wait_for_timeout(500)
    ov = ph.evaluate("document.documentElement.scrollWidth - innerWidth")
    check(ov == 0, f"no sideways overflow on a phone ({ov}px)")
    check(ph.evaluate("__et().zoomed"), "the phone opens on the valley")
    b.close()

print()
if fails:
    print(f"{len(fails)} failed")
    sys.exit(1)
print("all checks pass")
