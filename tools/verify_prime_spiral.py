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
    # the rings: 12 wears the colors of 2 and of 3, and only those
    rings = pg.evaluate(
        "(n)=>[...document.querySelectorAll(`#marks g[data-n='${n}'] "
        "circle[stroke]`)].map(c=>c.getAttribute('stroke'))", 12)
    own = pg.evaluate(
        "(n)=>[...document.querySelectorAll(`#marks g[data-n='${n}'] "
        "circle[stroke]`)].map(c=>c.getAttribute('stroke'))", 2)
    three = pg.evaluate(
        "(n)=>[...document.querySelectorAll(`#marks g[data-n='${n}'] "
        "circle[stroke]`)].map(c=>c.getAttribute('stroke'))", 3)
    ok = rings == own + three and len(rings) == 2
    print(f"  {'ok  ' if ok else 'FAIL'} 12 wears the rings of 2 and of 3 "
          f"({rings})")
    if not ok: fails.append(f"rings of 12: {rings} vs {own}+{three}")
    r30 = pg.evaluate(
        "(n)=>document.querySelectorAll(`#marks g[data-n='${n}'] "
        "circle[stroke]`).length", 30)
    ok = r30 == 3
    print(f"  {'ok  ' if ok else 'FAIL'} 30 wears three rings, one per prime "
          f"factor ({r30})")
    if not ok: fails.append(f"rings of 30: {r30}")
    fz = pg.evaluate("()=>factorization(60)")
    ok = fz == "2\u00b2 \u00d7 3 \u00d7 5"
    print(f"  {'ok  ' if ok else 'FAIL'} the hover factorization of 60 reads "
          f"'{fz}'")
    if not ok: fails.append(f"factorization {fz!r}")
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
    # the walk runs backwards: the slider to 30 takes every later mark off
    pg.evaluate("()=>{document.getElementById('scrub').value=30;"
                "document.getElementById('scrub').dispatchEvent(new Event('input'))}")
    st = pg.evaluate("()=>window.__spiral()")
    ns = [g["n"] for g in st["groups"]]
    ok = st["len"] == 30 and max(ns) == 30 and st["marked"] == 10 and st["lastPrime"] == 29 and not st["playing"]
    print(f"  {'ok  ' if ok else 'FAIL'} scrubbed back to 30: {len(ns)} marks, "
          f"{st['marked']} primes, the last {st['lastPrime']}, the walk paused")
    if not ok: fails.append(f"scrub {st['len']} {st['marked']} {st['lastPrime']}")
    # a prime clicked lights its multiples and dims the rest
    pg.evaluate("()=>setLit(3)")
    st = pg.evaluate("()=>window.__spiral()")
    lit = {g["n"]: g["o"] for g in st["groups"]}
    ok = st["lit"] == 3 and all((lit[n] == "1") == (n % 3 == 0) for n in lit)
    print(f"  {'ok  ' if ok else 'FAIL'} 3 lit: every third mark bright, the rest dim")
    if not ok: fails.append(f"lit {lit}")
    pg.evaluate("()=>setLit(null)")
    # the hover card sits at the mark
    pg.evaluate("()=>document.querySelector('#marks g[data-n=\"12\"] .hit')"
                ".dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    hv = pg.evaluate("()=>{const h=document.getElementById('hov');"
                     "return {t:h.textContent, on:getComputedStyle(h).display!=='none'}}")
    ok = hv["on"] and hv["t"] == "12 = 2\u00b2 \u00d7 3"
    print(f"  {'ok  ' if ok else 'FAIL'} the card at the mark reads '{hv['t']}'")
    if not ok: fails.append(f"hover card {hv}")
    # the square spiral: 1 at the center, 2 to its right, 3 above that
    pg.evaluate("()=>{mix=1; relayout()}")
    st = pg.evaluate("()=>window.__spiral()")
    u = st["ulam"]
    ok = (u["u1"]["x"] == st["cx"] and u["u1"]["y"] == st["cy"] and u["u2"]["x"] > u["u1"]["x"]
          and u["u3"]["y"] < u["u2"]["y"] and u["u3"]["x"] == u["u2"]["x"]
          and u["u9"]["x"] > u["u1"]["x"] and u["u9"]["y"] > u["u1"]["y"]
          and u["u10"]["x"] > u["u9"]["x"] and u["u25"]["x"] > u["u9"]["x"] and u["u25"]["y"] > u["u9"]["y"])
    print(f"  {'ok  ' if ok else 'FAIL'} Ulam's square: 1 at the center, 2 right, 3 up, "
          "9 and 25 down the diagonal")
    if not ok: fails.append(f"ulam {u}")
    moved = [g for g in st["groups"] if g["n"] == 2][0]["t"]
    ok = moved == f"translate({u['u2']['x']:.1f},{u['u2']['y']:.1f})"
    print(f"  {'ok  ' if ok else 'FAIL'} the mark of 2 moved to its square cell ({moved})")
    if not ok: fails.append(f"moved {moved}")
    pg.evaluate("()=>{mix=0; relayout()}")
    # the wheel takes the view over; a double click gives it back
    pg.evaluate("()=>document.getElementById('psvg').dispatchEvent(new WheelEvent('wheel',{deltaY:-300,clientX:300,clientY:300,bubbles:true,cancelable:true}))")
    st = pg.evaluate("()=>window.__spiral()")
    h1 = st["half"]
    pg.evaluate("()=>document.getElementById('psvg').dispatchEvent(new MouseEvent('dblclick',{bubbles:true}))")
    st2 = pg.evaluate("()=>window.__spiral()")
    ok = st["manual"] and not st2["manual"] and st2["half"] > h1
    print(f"  {'ok  ' if ok else 'FAIL'} the wheel zooms in (half-view {h1:.0f}) and a double click fits again ({st2['half']:.0f})")
    if not ok: fails.append(f"zoom {st['manual']} {h1} {st2['half']}")
    # a jump along the path (the slider to its end) is followed until every mark is in view
    pg.evaluate("()=>{TARGET=CAP; const s=document.getElementById('scrub'); s.max=CAP; s.value=CAP; s.dispatchEvent(new Event('input'))}")
    pg.wait_for_timeout(2500)
    fit = pg.evaluate("()=>{const s=window.__spiral(); let m=0; for(const g of s.groups){const t=g.t.match(/[-\\d.]+/g).map(Number);"
                      " m=Math.max(m,Math.hypot(t[0]-s.cx,t[1]-s.cy));} return [m,s.half]}")
    ok = fit[1] >= fit[0] * 0.97
    print(f"  {'ok  ' if ok else 'FAIL'} scrubbed to the end, the view opens to the outer ring (half-view {fit[1]:.0f}, outermost mark {fit[0]:.0f})")
    if not ok: fails.append(f"fit {fit}")
    pg.evaluate("()=>{const s=document.getElementById('scrub'); s.value=30; s.dispatchEvent(new Event('input'))}")
    pg.wait_for_timeout(300)
    if errs: fails.append(f"js errors: {errs}")
    br.close()
print()
if fails:
    for f in fails: print("FAIL", f)
    sys.exit(1)
print("everything squares")
