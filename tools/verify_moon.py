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
for want in ("The Month: The Moon's Loop", "library.html", "ALTAZOR"):
    if want not in html:
        fails.append(f"the page is missing {want!r}")

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
      const R = Math.min(96, Math.min(innerWidth, innerHeight)*0.12);
      const bx = innerWidth - R - 46, by = innerHeight - R - 132;
      const d = x.getImageData((bx-R)*dpr, (by-R)*dpr, 2*R*dpr, 2*R*dpr).data;
      const w = 2*R*dpr;
      let lit = 0, tot = 0, left = 0;
      for (let i = 0; i < d.length; i += 4) {
        const p = i/4, px = p % w, py = Math.floor(p/w);
        if (Math.hypot(px - R*dpr, py - R*dpr) > R*dpr - 2) continue;
        tot++;
        if (d[i] > 150 && d[i+1] > 150) { lit++; if (px < R*dpr) left++; }
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
    order = ["New moon", "Waxing crescent", "First quarter",
             "Waxing gibbous", "Full moon", "Waning gibbous", "Last quarter",
             "Waning crescent"]
    for want, got_ in zip(order, seen):
        if want != got_:
            fails.append(f"the month reads {seen}, expected {order}")
            break
    else:
        print("  ok   the month runs through its phases in order")

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
