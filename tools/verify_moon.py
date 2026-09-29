"""Check moon.html against an independent ephemeris and against its own drawing.

The positions on the page are a truncated series, so the question is not whether
they are exact but whether the truncation still earns the numbers printed beside
them. pyephem, which wraps the XEphem astrometry library, is the second opinion:
it shares no code with this page. Illuminated fraction, distance and the times of
new and full moon are all compared against it, over years, by driving the page's
own JavaScript in a browser rather than a copy of it in Python.

Then two checks on the drawing itself. The lit pixels of the Moon disc are
counted and compared with the percentage the panel claims, which is what catches
a terminator drawn inside out. And the heliocentric path is tested for the one
claim the second view makes: that the Moon never moves backward, until the
exaggeration passes the ratio of the two orbital speeds, when it must.

Usage: pip install ephem
       python3 verify_moon.py
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).parent
PAGE = HERE.parent / "moon.html"

SYNODIC = 29.530589
SIDEREAL = 27.321662
ANOMALISTIC = 27.554550
DRACONIC = 27.212221
YEAR = 365.256363
CUSP = 29.78 / 1.022

fails = []

print("--- the month lengths on the page ---")
CLAIMS = [
    ("the synodic month follows from the sidereal one and the year",
     abs(1 / (1 / SIDEREAL - 1 / YEAR) - SYNODIC) < 0.0005),
    ("the phase month is 2.21 days longer than the star month",
     abs((SYNODIC - SIDEREAL) - 2.21) < 0.005),
    ("the Sun moves about a degree a day", abs(360 / YEAR - 0.9856) < 0.0005),
    ("the anomalistic month is the longest of the four",
     ANOMALISTIC > max(SIDEREAL, DRACONIC)),
    ("the draconic month is the shortest",
     DRACONIC < min(SIDEREAL, ANOMALISTIC)),
    ("the path cusps at the ratio of the two orbital speeds",
     abs(CUSP - 29.14) < 0.02),
]
for claim, ok in CLAIMS:
    print(f"  {'ok  ' if ok else 'FAIL'} {claim}")
    if not ok:
        fails.append(claim)

html = PAGE.read_text(encoding="utf-8")
import re
if "—" in re.sub(r"<script[\s\S]*?</script>", "", html):
    fails.append("an em dash in the page copy")
for want in ("The Month: The Moon's Cycle", "library.html", "ALTAZOR"):
    if want not in html:
        fails.append(f"the page is missing {want!r}")
det = re.search(r'<details class="sources"[^>]*>([\s\S]*?)</details>', html)
if not det or " open" in det.group(0)[:40] or "Astronomical algorithms" not in det.group(1) or 'id="noteLong"' not in det.group(1):
    fails.append("the long notes and sources are not in a closed Sources details")
else:
    print("  ok   the long notes and the sources sit in a closed Sources details")
for nm in ("CAP_EARTH", "CAP_SUN"):
    mm = re.search(nm + r"\s*=\s*(?:\(\)\s*=>)?\s*([\s\S]*?);\n", html)
    words = len(re.sub(r'"\s*\+\s*"|" \+ D\.CUSP \+ "', " ", mm.group(1)).split()) if mm else 999
    if words > 80:
        fails.append(f"{nm} runs {words} words")
    else:
        print(f"  ok   {nm.lower()}, the caption, is {words} words")

try:
    import ephem
except ImportError:
    print("\npyephem not installed, so there is nothing to check against")
    sys.exit(1)
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("\nplaywright not installed")
    sys.exit(1)

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1440, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.resolve().as_uri())
    pg.wait_for_timeout(1400)
    pg.click("#playBtn")          # hold the clock still for the checks
    pg.wait_for_timeout(200)

    print("--- the page's own positions against pyephem ---")
    # ten years, every eleven days, computed by the page itself
    jds = [float(ephem.Date("2020/01/01")) + 2415020.0 + n for n in range(0, 3650, 11)]
    got = pg.evaluate("(js) => js.map(j => positions(j))", jds)
    worst_k = worst_d = worst_e = 0.0
    for jd, g in zip(jds, got):
        d = ephem.Date(jd - 2415020.0)
        m = ephem.Moon()
        m.compute(d)
        worst_k = max(worst_k, abs(g["k"] - m.moon_phase) * 100)
        worst_d = max(worst_d, abs(g["dist"] - m.earth_distance * 149597870.7))
        s = ephem.Sun()
        s.compute(d)
        worst_e = max(worst_e, abs(((g["elong"] - math.degrees(float(m.elong))
                                     + 180) % 360) - 180))
    print(f"  {len(jds)} dates over ten years")
    print(f"  ok   illuminated fraction within {worst_k:.2f} points")
    print(f"  ok   distance within {worst_d:.0f} km")
    if worst_k > 0.5:
        fails.append(f"illuminated fraction is off by up to {worst_k:.2f} points")
    if worst_d > 60:
        fails.append(f"distance is off by up to {worst_d:.0f} km")

    print("--- the times of new and full moon ---")
    worst_min = 0.0
    for target, fn, name in [(0, ephem.next_new_moon, "new"),
                             (180, ephem.next_full_moon, "full")]:
        d = ephem.Date("2026/01/01")
        for _ in range(14):
            ref = fn(d)
            d = ref + 1
            mine = pg.evaluate("([j, t]) => nextPhase(j, t)",
                               [float(ref) + 2415020.0 - 2, target])
            err = abs(mine - (float(ref) + 2415020.0)) * 24 * 60
            worst_min = max(worst_min, err)
    print(f"  ok   28 events over two years, worst {worst_min:.1f} minutes out")
    if worst_min > 15:
        fails.append(f"phase times are off by up to {worst_min:.1f} minutes")

    print("--- the Moon drawn against the Moon stated ---")
    MEASURE = """() => {
      const c = document.getElementById('sky'), x = c.getContext('2d');
      const dpr = c.width/window.innerWidth;
      const I = window.__moon.inset, R = I.R, bx = I.x, by = I.y;
      const d = x.getImageData((bx-R)*dpr, (by-R)*dpr, 2*R*dpr, 2*R*dpr).data;
      const w = 2*R*dpr;
      // shadow is #0b0e14, so red 11; the darkest sea is about red 120 and
      // the highlands 200. Anything above 60 is lit ground.
      let lit = 0, tot = 0, left = 0;
      for (let i = 0; i < d.length; i += 4) {
        const p = i/4, px = p % w, py = Math.floor(p/w);
        if (Math.hypot(px - R*dpr, py - R*dpr) > R*dpr - 2) continue;
        tot++;
        if (d[i] > 60) { lit++; if (px < R*dpr) left++; }
      }
      return {k: lit/tot, left: left/(lit || 1)};
    }"""
    seen = []
    for day in (0.0, 3.7, 7.4, 11.1, 14.8, 18.4, 22.1, 25.8):
        pg.evaluate(f"()=>{{const s=document.getElementById('scrub');"
                    f"s.value={day}; s.dispatchEvent(new Event('input'));}}")
        pg.wait_for_timeout(320)
        m = pg.evaluate("()=>window.__moon")
        got = pg.evaluate(MEASURE)
        drawn = got["k"]
        seen.append(m["phase"])
        if abs(drawn - m["k"]) > 0.035:
            fails.append(f"day {day}: the disc is {drawn*100:.0f}% lit but the "
                         f"panel says {m['k']*100:.0f}%")
        # waxing is lit on the right, waning on the left; new and full have no
        # side to speak of, so they are skipped
        side = "left" if got["left"] > 0.5 else "right"
        if 0.03 < m["k"] < 0.97:
            want = "right" if m["elong"] < 180 else "left"
            if side != want:
                fails.append(f"day {day}: {m['phase'].lower()} is lit on the "
                             f"{side}, which is the wrong limb")
        print(f"  ok   day {day:5.1f}  panel {m['k']*100:5.1f}%  "
              f"disc {drawn*100:5.1f}%  lit {side:5}  {m['phase']}")
    order = ["New Moon", "Waxing Crescent", "First Quarter",
             "Waxing Gibbous", "Full Moon", "Waning Gibbous", "Last Quarter",
             "Waning Crescent"]
    for want, got_ in zip(order, seen):
        if want != got_:
            fails.append(f"the month reads {seen}, expected {order}")
            break
    else:
        print("  ok   the month runs through its phases in order")

    print("--- seen from the south ---")
    pg.evaluate("()=>{const s=document.getElementById('scrub');s.value=5;s.dispatchEvent(new Event('input'));}")
    pg.wait_for_timeout(300)
    north = pg.evaluate(MEASURE)
    pg.click("#southBtn")
    pg.wait_for_timeout(300)
    southm = pg.evaluate(MEASURE)
    m = pg.evaluate("()=>window.__moon")
    ok = m["south"] and north["left"] < 0.5 and southm["left"] > 0.5 and abs(north["k"] - southm["k"]) < 0.02
    print(f"  {'ok  ' if ok else 'FAIL'} a waxing crescent lit on the right from the north, on the left from the south, "
          f"{southm['k']*100:.0f}% lit either way")
    if not ok:
        fails.append("the south view does not turn the inset round")
    pg.click("#southBtn")
    pg.wait_for_timeout(200)

    print("--- the Moon dragged round its orbit ---")
    pg.click("#playBtn")
    pg.wait_for_timeout(100)
    m = pg.evaluate("()=>window.__moon")
    mo = m["moonAt"]
    pg.mouse.move(mo["x"], mo["y"])
    pg.mouse.down()
    import math as _m
    want = (m["lam"] + 120) % 360
    tx, ty = mo["ex"] + 60 * _m.cos(_m.radians(want)), mo["ey"] - 60 * _m.sin(_m.radians(want))
    pg.mouse.move(tx, ty, steps=12)
    for _ in range(4):                      # Earth moves on as the clock does; the Moon follows the pointer
        pg.wait_for_timeout(60)
        pg.mouse.move(tx + 0.5, ty, steps=2)
        pg.mouse.move(tx, ty, steps=2)
    pg.mouse.up()
    pg.wait_for_timeout(200)
    m2 = pg.evaluate("()=>window.__moon")
    e2 = m2["moonAt"]
    want = _m.degrees(_m.atan2(-(ty - e2["ey"]), tx - e2["ex"])) % 360
    err = abs(((m2["lam"] - want + 180) % 360) - 180)
    ok = (not m2["playing"]) and err < 1.0
    print(f"  {'ok  ' if ok else 'FAIL'} dragged a third of the way round: the Moon lands within {err:.2f} degrees "
          f"of the pointer and the clock holds")
    if not ok:
        fails.append(f"dragging the Moon lands {err:.1f} degrees off (playing {m2['playing']})")

    print("--- eclipses ---")
    # the eclipses of 2026 to 2028 as NASA's catalogs list them (Espenak)
    KNOWN = [("2026-02-17", "solar"), ("2026-03-03", "total lunar"), ("2026-08-12", "solar"),
             ("2026-08-28", "partial lunar"), ("2027-02-06", "solar"), ("2027-02-20", "penumbral lunar"),
             ("2027-08-02", "solar"), ("2027-08-17", "penumbral lunar"), ("2028-01-12", "partial lunar"),
             ("2028-01-26", "solar"), ("2028-07-06", "partial lunar"), ("2028-07-22", "solar")]
    got = pg.evaluate("""()=>{ const out=[]; let j=2461041.5;
      for(let i=0;i<14;i++){ const e=eclipseFrom(j); out.push([jdToDate(e.jd).toISOString().slice(0,10), e.kind]); j=e.jd+2; }
      return out; }""")
    gotset = {tuple(g) for g in got}
    missing = [k for k in KNOWN if k not in gotset]
    ok = not missing
    print(f"  {'ok  ' if ok else 'FAIL'} the {len(KNOWN)} clear eclipses of 2026 to 2028 all found, with their kinds")
    if not ok:
        fails.append(f"eclipses missed or mistyped: {missing}; the page found {got}")
    # and the page's latitude at those new moons agrees with pyephem's
    worst_b = 0
    for day, kind in KNOWN:
        if kind != "solar":
            continue
        d = ephem.Date(day.replace("-", "/"))
        t = ephem.next_new_moon(ephem.Date(d - 2))
        mm = ephem.Moon(); mm.compute(t)
        ecl = ephem.Ecliptic(mm)
        b = pg.evaluate("(j)=>positions(j).beta", float(t) + 2415020.0)
        worst_b = max(worst_b, abs(b - _m.degrees(float(ecl.lat))))
    ok = worst_b < 0.02
    print(f"  {'ok  ' if ok else 'FAIL'} the Moon's latitude at those new moons within {worst_b*60:.2f} arcminutes of pyephem")
    if not ok:
        fails.append(f"the Moon's latitude is {worst_b:.3f} degrees off pyephem")
    pg.evaluate("()=>{ jd = 2461265.2; }")
    pg.wait_for_timeout(300)
    txt = pg.inner_text("#ecl")
    ok = txt.startswith("solar, now")
    print(f"  {'ok  ' if ok else 'FAIL'} on 12 August 2026 the panel reads '{txt}'")
    if not ok:
        fails.append(f"on the eclipse the panel reads {txt!r}")

    print("--- the readouts against the diagram ---")
    # The counters, the wave and the scale caveat share the top left. The page
    # reports how far right it actually drew them and where the orbit reaches,
    # so an overlap is measured rather than eyeballed at one window size.
    worst = None
    for w, h in [(1920, 1200), (1440, 900), (1280, 800), (1100, 760),
                 (900, 700), (760, 640)]:
        pg.set_viewport_size({"width": w, "height": h})
        pg.wait_for_timeout(420)
        for day in (2.0, 9.0, 16.0, 24.0):
            pg.evaluate("(d)=>{const s=document.getElementById('scrub');"
                        "s.value=d;s.dispatchEvent(new Event('input'));}", day)
            pg.wait_for_timeout(150)
            m = pg.evaluate("()=>window.__moon")
            slack = m["orbitLeft"] - m["colInk"]
            if worst is None or slack < worst[0]:
                worst = (slack, w, h, day)
            if slack < 0:
                fails.append(f"at {w}x{h} on day {day} the readouts run "
                             f"{-slack:.0f}px into the orbit")
        print(f"  {'ok  ' if worst[0] >= 0 else 'FAIL'} {w}x{h}  "
              f"nothing printed within {m['orbitLeft'] - m['colInk']:.0f}px "
              "of the orbit")
    pg.set_viewport_size({"width": 1440, "height": 900})
    pg.wait_for_timeout(420)

    print("--- the diagram against the control bar ---")
    # The bar is fixed to the foot of the window and its height changes with
    # the view, so the diagram has to be sized from a measurement of it. The
    # page reports how far down and right its drawing actually reaches.
    for w, h in [(1920, 1200), (1440, 900), (1280, 800), (1100, 780), (960, 720)]:
        pg.set_viewport_size({"width": w, "height": h})
        pg.wait_for_timeout(450)
        for day in (3.0, 11.0, 19.0, 27.0):
            pg.evaluate("(d)=>{const s=document.getElementById('scrub');"
                        "s.value=d;s.dispatchEvent(new Event('input'));}", day)
            pg.wait_for_timeout(140)
            m = pg.evaluate("()=>window.__moon")
            r = m["reach"]
            under = m["controlsTop"] - r["bottom"]
            beside = m["panelLeft"] - r["right"]
            if under < 0:
                fails.append(f"at {w}x{h} on day {day} the orbit runs "
                             f"{-under:.0f}px into the controls")
            if beside < 0:
                fails.append(f"at {w}x{h} on day {day} the orbit runs "
                             f"{-beside:.0f}px into the readout panel")
        print(f"  {'ok  ' if under >= 0 and beside >= 0 else 'FAIL'} {w}x{h}  "
              f"{under:.0f}px above the controls, {beside:.0f}px left of the panel")
    pg.set_viewport_size({"width": 1440, "height": 900})
    pg.wait_for_timeout(450)

    print("--- a phone ---")
    pg.set_viewport_size({"width": 390, "height": 844})
    pg.wait_for_timeout(500)
    m = pg.evaluate("()=>window.__moon")
    rb = pg.evaluate("()=>document.getElementById('readout').getBoundingClientRect().bottom")
    ct = pg.evaluate("()=>document.getElementById('controls').getBoundingClientRect().top")
    I = m["inset"]
    r = m["reach"]
    ok = (m["narrow"] and m["colTop"] - 20 > rb and m["colInk"] <= 390 and I["x"] + I["R"] < 200 and
          I["y"] + I["R"] < m["colTop"] - 20 and r["bottom"] <= ct and m["orbitLeft"] >= 0 and r["right"] <= 390)
    print(f"  {'ok  ' if ok else 'FAIL'} at 390x844 the column sits under the readout ({m['colTop']:.0f} > {rb:.0f}), "
          f"the inset beside the heading, the orbit between the column and the controls")
    if not ok:
        fails.append(f"the phone layout overlaps: {m['colTop']}, {rb}, {I}, {r}, {ct}")
    ov = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
    if ov:
        fails.append(f"the phone page is {ov}px too wide")
    pg.set_viewport_size({"width": 1440, "height": 900})
    pg.wait_for_timeout(450)

    print("--- the heliocentric path ---")
    pg.click("#viewBtn")
    pg.wait_for_timeout(700)

    # The claim is that the Moon never loops backward, so the test is whether
    # its motion ever reverses against Earth's. Counting curvature sign changes
    # instead measures floating point noise on the near-straight stretches, and
    # a prograde loop does not reverse curvature anyway.
    def backward(exag):
        pg.evaluate(f"()=>{{const s=document.getElementById('exag');"
                    f"s.value={exag}; s.dispatchEvent(new Event('input'));}}")
        pg.wait_for_timeout(700)
        st = pg.evaluate("()=>({m: window.__moon.sunPath, e: window.__moon.earthPath})")
        moon, earth = st["m"], st["e"]
        back = 0
        for i in range(1, len(moon)):
            mx, my = moon[i][0] - moon[i-1][0], moon[i][1] - moon[i-1][1]
            ex, ey = earth[i][0] - earth[i-1][0], earth[i][1] - earth[i-1][1]
            if mx * ex + my * ey < 0:
                back += 1
        return back, len(moon) - 1

    for exag, expect in [(1, "none"), (round(CUSP - 4, 1), "none"),
                         (round(CUSP + 4, 1), "some"), (55, "some")]:
        back, n = backward(exag)
        ok = (back == 0) if expect == "none" else (back >= 3)
        if not ok:
            fails.append(f"at x{exag} the Moon moves backward on {back} of {n} "
                         f"steps, expected {expect}")
        print(f"  {'ok  ' if ok else 'FAIL'} x{exag:<5} backward on {back:3d} "
              f"of {n} steps")
    print(f"  ok   forward the whole way below the cusp at x{CUSP:.2f}, "
          "looping above it")

    if errs:
        fails.append(f"javascript errors: {errs}")
    br.close()

print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("all checks pass")
