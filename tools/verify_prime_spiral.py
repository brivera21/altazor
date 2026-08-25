"""Checks prime-spiral.html against its own geometry and arithmetic.

  the walk     starts at twelve o'clock, moves clockwise, and the mark at
               24 units sits back near the top after one loop outside
  the primes   the amber marks are exactly the primes, twenty of them by 71
  the page     the tiles track the walk and the labels stop at twenty
"""
import sys
from pathlib import Path

fails = []
s = (Path(__file__).parent.parent / "prime-spiral.html").read_text(encoding="utf-8")
print("--- the page text ---")
for frag in ["10.2307/2312588", "numberspiral.com", "twelve o'clock",
             "twenty-four units"]:
    ok = frag in s
    print(f"  {'ok  ' if ok else 'FAIL'} carries '{frag}'")
    if not ok: fails.append(f"missing {frag}")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1100, "height": 950})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((Path(__file__).parent.parent / "prime-spiral.html").resolve().as_uri())
    pg.wait_for_selector("#psvg")
    st = pg.evaluate("()=>window.__spiral()")
    ok = abs(st["start"]["x"] - st["cx"]) < 0.5 and st["start"]["y"] < st["cy"]
    print(f"  {'ok  ' if ok else 'FAIL'} the walk starts at twelve o'clock")
    if not ok: fails.append(f"start {st['start']}")
    ok = st["first"]["x"] > st["cx"] + 1
    print(f"  {'ok  ' if ok else 'FAIL'} the first step goes clockwise, to the "
          "right of twelve")
    if not ok: fails.append(f"first {st['first']}")
    dx = st["loop24"]["x"] - st["cx"]
    dy = st["loop24"]["y"] - st["cy"]
    import math
    ang = math.degrees(math.atan2(dx, -dy)) % 360
    ok = ang < 60 and dy < 0
    print(f"  {'ok  ' if ok else 'FAIL'} after 24 units the path is back near "
          f"the top, {ang:.0f} degrees past twelve, one ring out")
    if not ok: fails.append(f"loop24 at {ang}")
    # run the walk to the end of the default target
    pg.evaluate("()=>{speed=40}")
    pg.wait_for_function("()=>window.__spiral().len>=window.__spiral().target",
                         timeout=30000)
    st = pg.evaluate("()=>window.__spiral()")
    ok = st["marked"] == 20 and st["lastPrime"] == 71
    print(f"  {'ok  ' if ok else 'FAIL'} the default walk marks {st['marked']} "
          f"primes, the last at {st['lastPrime']}")
    if not ok: fails.append(f"marks {st}")
    primes = pg.evaluate(
        "()=>[...document.querySelectorAll('#marks circle')]"
        ".filter(c=>c.getAttribute('fill').includes('prime'))"
        ".map(c=>+c.getAttribute('data-n'))")
    def isp(n):
        return n > 1 and all(n % d for d in range(2, int(n**0.5) + 1))
    expected = [n for n in range(2, 72) if isp(n)]
    ok = primes == expected
    print(f"  {'ok  ' if ok else 'FAIL'} the amber marks are exactly the "
          f"primes through 71 ({len(primes)})")
    if not ok: fails.append(f"primes {primes}")
    nl = pg.evaluate("()=>document.querySelectorAll('#labels text').length")
    ok = nl == 20
    print(f"  {'ok  ' if ok else 'FAIL'} twenty labels ({nl})")
    if not ok: fails.append(f"labels {nl}")
    # keep building extends the target
    t2 = pg.evaluate("()=>{document.getElementById('bMore').click();"
                     "return window.__spiral().target}")
    ok = t2 == 1000
    print(f"  {'ok  ' if ok else 'FAIL'} keep building raises the walk to {t2}")
    if not ok: fails.append(f"target {t2}")
    if errs: fails.append(f"js errors: {errs}")
    br.close()
print()
if fails:
    for f in fails: print("FAIL", f)
    sys.exit(1)
print("everything squares")
