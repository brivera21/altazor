"""Check chihuahua.html's own additions in a headless browser.

build_chihuahua.py patches the shared state template (EXTRA); this checks
those patches on the page: the faint border before 1824, tick labels that do
not overlap at desktop or phone width, an era year that glides the slider,
the census sparkline in the card, Play running quickly through the colonial
years, and no sideways overflow on a phone. The terrain tiles and flags load
from the network; the checks do not depend on them.

Usage: python3 verify_chihuahua.py
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PAGE = Path(__file__).parent.parent / "chihuahua.html"
fails = []


def check(ok, msg):
    print(("  ok   " if ok else "  FAIL ") + msg)
    if not ok:
        fails.append(msg)


TICKS = ("[...document.querySelectorAll('#ticks button')].map(b=>{const r=b.getBoundingClientRect();"
         "return [b.textContent,r.left,r.right,r.top,r.bottom]})")


def overlaps(boxes):
    return [(a[0], c[0]) for i, a in enumerate(boxes) for c in boxes[i + 1:]
            if a[1] < c[2] - 1 and c[1] < a[2] - 1 and a[3] < c[4] - 1 and c[3] < a[4] - 1]


check("—" not in PAGE.read_text(encoding="utf-8"), "no em dash in the page")
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1300, "height": 850})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.resolve().as_uri())
    pg.wait_for_timeout(1000)
    check(pg.evaluate("document.querySelectorAll('#map path.ghostline').length") == 1,
          "in 1492 today's border is drawn as a faint dashed frame")
    boxes = pg.evaluate(TICKS)
    check(len(boxes) >= 9 and not overlaps(boxes),
          f"{len(boxes)} era years above the slider, none overlapping {overlaps(boxes)}")
    ends = pg.evaluate("""()=>{const t=document.getElementById('ticks'), W=t.clientWidth;
      return [...t.querySelectorAll('svg.lead line')].map((l,i)=>[+l.getAttribute('x2'),
        (+t.querySelectorAll('button')[i].textContent-1492)/(2025-1492)*W]);}""")
    check(all(abs(a - c) < 0.5 for a, c in ends), "each leader ends at its own year on the slider")

    pg.evaluate("[...document.querySelectorAll('#ticks button')].find(b=>b.textContent==='1910').click()")
    pg.wait_for_timeout(350)
    mid = pg.evaluate("__state().year")
    pg.wait_for_timeout(1200)
    end = pg.evaluate("__state().year")
    check(1492 < mid < 1910 and end == 1910, f"1910 glides the slider there ({mid} on the way, {end} at the end)")
    check(pg.evaluate("document.querySelectorAll('#map path.ghostline').length") == 0,
          "after 1824 the real border replaces the faint one")

    i = pg.evaluate("HIST.events.findIndex(e=>e.pp&&e.pp.length>2)")
    pg.evaluate(f"document.querySelector('[data-ev=\"{i}\"] circle').dispatchEvent("
                "new PointerEvent('pointerover',{bubbles:true}))")
    n = pg.evaluate("document.querySelectorAll('#sparkTxt polyline').length")
    pts = pg.evaluate("document.querySelectorAll('#sparkTxt circle').length")
    want = pg.evaluate(f"HIST.events[{i}].pp.length")
    check(n == 1 and pts == want + 1,
          f"{pg.evaluate('nameTxt.textContent')}: a census sparkline with {want} points and the year marked")

    pg.evaluate("yr.value=1492;yr.dispatchEvent(new Event('input'))")
    pg.click("#bPlay")
    pg.wait_for_timeout(3000)
    y = pg.evaluate("__state().year")
    check(y > 1540 and pg.evaluate("bPlay.textContent") == "Pausa",
          f"Play runs the colonial years quickly: {y} after three seconds, the button reads Pausa")
    pg.click("#bPlay")
    check(not errs, f"no javascript errors {errs}")

    ph = b.new_page(viewport={"width": 390, "height": 844})
    ph.goto(PAGE.resolve().as_uri())
    ph.wait_for_timeout(800)
    ov = ph.evaluate("document.documentElement.scrollWidth - innerWidth")
    check(ov == 0, f"no sideways overflow on a phone ({ov}px)")
    boxes = ph.evaluate(TICKS)
    check(not overlaps(boxes), f"no tick labels overlap on a phone {overlaps(boxes)}")
    b.close()

print()
if fails:
    print(f"{len(fails)} failed")
    sys.exit(1)
print("all checks pass")
