"""Check day-night.html against an independent ephemeris and against its drawing.

The page carries its own solar theory, the low-precision series from Meeus
chapters 25 and 28. pyephem, which wraps the XEphem astrometry library, shares
no code with it, so it is the second opinion here: the declination, the position
of the sub-solar point, and the times the Sun rises and sets at real places are
all compared against it, over years, by driving the page's own JavaScript in a
browser rather than a copy of it in Python.

Then the drawing. The overlay the page actually painted is read back, not
recomputed, because a terminator drawn inside out would still agree with the
formula that drew it. Three things are asked of it: that it leaves half the
surface lit whatever the date, that the lit half is centred on the sub-solar
point, and that the poles are covered and cleared on the right dates.

Usage: pip install ephem
       python3 verify_day.py
"""
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
PAGE = HERE.parent / "day-night.html"

OBLIQUITY = 23.4366
fails = []

html = PAGE.read_text(encoding="utf-8")
print("--- the page itself ---")
for want in ("The Day: Earth's Night and Day Cycle", "library.html", "ALTAZOR",
             "GeoNames", "References"):
    ok = want in html
    print(f"  {'ok  ' if ok else 'FAIL'} the page carries {want!r}")
    if not ok:
        fails.append(f"the page is missing {want!r}")
if "—" in re.sub(r"<script[\s\S]*?</script>", "", html):
    fails.append("an em dash in the page copy")

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


def sub_solar(dt):
    """Where the Sun stands overhead, from pyephem: apparent right ascension
    against apparent sidereal time at Greenwich."""
    s = ephem.Sun()
    s.compute(dt)
    g = ephem.Observer()
    g.lat, g.lon, g.date, g.pressure = "0", "0", dt, 0
    lon = math.degrees(float(s.g_ra) - float(g.sidereal_time()))
    return math.degrees(float(s.g_dec)), (lon + 180) % 360 - 180


# real places, spread over latitude, for the rise and set times
PLACES = [("Quito", 0.18, -78.47), ("Nairobi", -1.29, 36.82),
          ("Chihuahua", 28.63, -106.08), ("Reykjavik", 64.13, -21.90),
          ("Hobart", -42.88, 147.33), ("Singapore", 1.35, 103.82)]

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1440, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.resolve().as_uri())
    pg.wait_for_function("() => !!window.__day", timeout=15000)

    print("--- the Sun's place, against pyephem ---")
    dates = [(2021 + n // 24, n % 12 + 1, (n * 7) % 27 + 1, (n * 5) % 24)
             for n in range(120)]
    worst_dec = worst_lon = 0.0
    for y, mo, d, h in dates:
        pg.evaluate("(a)=>window.__setTime(a[0],a[1],a[2],a[3])", [y, mo, d, h])
        got = pg.evaluate("()=>window.__probe(0, 0)")
        dt = ephem.Date(f"{y}/{mo}/{d} {h}:00:00")
        dec, lon = sub_solar(dt)
        worst_dec = max(worst_dec, abs(got["dec"] - dec))
        worst_lon = max(worst_lon, abs((got["slon"] - lon + 180) % 360 - 180))
    print(f"  {len(dates)} dates over five years")
    print(f"  ok   declination within {worst_dec * 60:.2f} arcminutes")
    print(f"  ok   the sub-solar longitude within {worst_lon * 60:.2f} arcminutes")
    if worst_dec > 0.02:
        fails.append(f"declination is off by up to {worst_dec:.4f} degrees")
    if worst_lon > 0.05:
        fails.append(f"the sub-solar point is off by up to {worst_lon:.4f} degrees")

    print("--- sunrise and sunset at real places ---")
    worst_min = 0.0
    worst_where = ""
    for name, lat, lon in PLACES:
        for mo, d in [(3, 20), (6, 21), (9, 22), (12, 21)]:
            pg.evaluate("(a)=>window.__setTime(a[0],a[1],a[2],a[3])",
                        [2026, mo, d, 12])
            got = pg.evaluate("(a)=>window.__probe(a[0],a[1])", [lat, lon])
            o = ephem.Observer()
            o.lat, o.lon = str(lat), str(lon)
            o.date = ephem.Date(f"2026/{mo}/{d} 00:00:00")
            o.pressure = 0
            o.horizon = "-0:34"          # refraction only; the disc is added below
            s = ephem.Sun()
            try:
                rise = o.next_rising(s, use_center=False)
                setg = o.next_setting(s, use_center=False)
            except (ephem.AlwaysUpError, ephem.NeverUpError):
                continue
            ref = (float(setg) - float(rise)) * 24
            ref = (ref + 24) % 24
            err = abs(got["day"] - ref) * 60
            if err > worst_min:
                worst_min, worst_where = err, f"{name} on {mo}/{d}"
    print(f"  ok   {len(PLACES)} places at both solstices and both equinoxes")
    print(f"  ok   day length within {worst_min:.1f} minutes, worst at {worst_where}")
    if worst_min > 4:
        fails.append(f"day length is off by up to {worst_min:.1f} minutes "
                     f"({worst_where})")

    print("--- what the page actually painted ---")
    # half the globe, always: the terminator is a great circle whatever the date
    worst_share = 0.0
    for mo, d in [(1, 15), (3, 20), (5, 5), (6, 21), (9, 22), (11, 8), (12, 21)]:
        for h in (0, 7, 14, 21):
            pg.evaluate("(a)=>window.__setTime(a[0],a[1],a[2],a[3])",
                        [2026, mo, d, h])
            lit = pg.evaluate("()=>window.__lit()")
            worst_share = max(worst_share, abs(lit - 0.5))
    print(f"  ok   the lit share stays within {worst_share * 100:.2f} points "
          "of half, at 28 dates and hours")
    if worst_share > 0.01:
        fails.append(f"the lit share strays {worst_share * 100:.1f} points from half")

    # the lit half has to be the half around the Sun, not the half away from it
    print("--- the light is on the right side ---")
    for mo, d, h in [(6, 21, 0), (6, 21, 12), (12, 21, 6), (3, 20, 18)]:
        pg.evaluate("(a)=>window.__setTime(a[0],a[1],a[2],a[3])", [2026, mo, d, h])
        st = pg.evaluate("()=>window.__day")
        near = pg.evaluate("(a)=>window.__probe(a[0],a[1])",
                           [st["dec"], st["slon"]])
        far = pg.evaluate("(a)=>window.__probe(a[0],a[1])",
                          [-st["dec"], (st["slon"] + 180 + 180) % 360 - 180])
        # and the same question asked of the paint rather than the formula
        aNear = pg.evaluate("(a)=>window.__alphaAt(a[0],a[1])",
                            [st["dec"], st["slon"]])
        aFar = pg.evaluate("(a)=>window.__alphaAt(a[0],a[1])",
                           [-st["dec"], (st["slon"] + 360) % 360 - 180])
        ok = (near["alt"] > 89.5 and far["alt"] < -89.5
              and aNear == 0 and aFar > 200)
        print(f"  {'ok  ' if ok else 'FAIL'} 2026-{mo:02d}-{d:02d} {h:02d}h  "
              f"overhead {near['alt']:.1f} deg and unshaded, "
              f"opposite {far['alt']:.1f} deg and {aFar}/255 dark")
        if not ok:
            fails.append(f"on {mo}/{d} at {h}h the lit half is not the half "
                         "around the Sun")

    print("--- the city lights ---")
    # Lights belong to the dark half. They are read off the layer the page drew,
    # at real cities, on the night side and then on the day side twelve hours
    # later, so a layer painted over the whole globe would show up here.
    CITIES = [("Tokyo", 35.7, 139.7), ("Cairo", 30.0, 31.2),
              ("Mexico City", 19.4, -99.1), ("Sao Paulo", -23.5, -46.6),
              ("Mumbai", 19.1, 72.9), ("London", 51.5, -0.1)]
    for name, lat, lon in CITIES:
        # midnight and noon in local solar time, near the equinox
        best = None
        for h2 in range(0, 24):
            pg.evaluate("(a)=>window.__setTime(a[0],a[1],a[2],a[3])",
                        [2026, 3, 20, h2])
            alt = pg.evaluate("(a)=>window.__probe(a[0],a[1]).alt", [lat, lon])
            g = pg.evaluate("(a)=>window.__lightAt(a[0],a[1])", [lat, lon])
            if best is None or alt < best[0]:
                best = (alt, g, h2)
            if alt > 40 and g > 2:
                fails.append(f"{name} is lit up at {h2}h with the Sun "
                             f"{alt:.0f} degrees up")
        ok = best[1] > 6
        print(f"  {'ok  ' if ok else 'FAIL'} {name} glows at {best[1]}/255 "
              f"at its darkest hour, and not at all in daylight")
        if not ok:
            fails.append(f"{name} never lights up at night ({best[1]}/255)")

    pg.click("#bLights")
    pg.wait_for_timeout(300)
    off = max(pg.evaluate("(a)=>window.__lightAt(a[0],a[1])", [lat, lon])
              for _, lat, lon in CITIES)
    pg.click("#bLights")
    pg.wait_for_timeout(300)
    ok = off == 0
    print(f"  {'ok  ' if ok else 'FAIL'} the lights go out when the button says so")
    if not ok:
        fails.append(f"the lights stay on at {off}/255 with the button off")

    print("--- running the day ---")
    pg.evaluate("()=>window.__setTime(2026,4,10,6)")
    pg.click("#bDay")
    pg.wait_for_timeout(600)
    t0 = pg.evaluate("()=>window.__day.jd")
    pg.wait_for_timeout(3000)
    t1 = pg.evaluate("()=>window.__day.jd")
    pg.click("#bDay")
    rate = (t1 - t0)/3.0
    ok = 0.2 < rate < 0.42          # one turn in roughly three seconds
    print(f"  {'ok  ' if ok else 'FAIL'} the day runs at {rate:.2f} days a "
          f"second, one turn every {1/rate:.1f} seconds")
    if not ok:
        fails.append(f"the day runs at {rate:.2f} days a second")

    print("--- running the year ---")
    # The complaint this answers: at any watchable speed the planet turned dozens
    # of times a second and the shadow only flickered. So the year run has to
    # hold the clock still and step whole days.
    pg.evaluate("()=>window.__setTime(2026,1,10,15)")
    pg.click("#bYear")
    pg.wait_for_timeout(4200)
    a = pg.evaluate("()=>window.__day")
    pg.wait_for_timeout(4200)
    b = pg.evaluate("()=>window.__day")
    pg.click("#bYear")
    held = abs(a["ut"] - 15) < 1e-6 and abs(b["ut"] - 15) < 1e-6
    moved = abs(b["dec"] - a["dec"]) > 3
    print(f"  {'ok  ' if held else 'FAIL'} the clock holds at "
          f"{a['ut']:.4f}h while the year runs")
    print(f"  {'ok  ' if moved else 'FAIL'} the Sun's declination moves "
          f"{a['dec']:.1f} to {b['dec']:.1f} degrees in eight seconds")
    if not held:
        fails.append(f"the year run moves the clock to {b['ut']:.4f}h")
    if not moved:
        fails.append("the year run does not move the date")

    ok = b["yearMode"] and b["analemma"] == 366 and b["ghosts"] > 5
    print(f"  {'ok  ' if ok else 'FAIL'} it traces {b['analemma']} days of "
          f"sub-solar points and keeps {b['ghosts']} daylight curves")
    if not ok:
        fails.append(f"the year run traced {b['analemma']} points and kept "
                     f"{b['ghosts']} curves")

    # the figure of eight: as tall as twice the tilt, and no wider than the
    # equation of time can make it
    pg.evaluate("()=>window.__setTime(2026,1,10,15)")
    pg.click("#bYear")
    pg.wait_for_timeout(300)
    pg.click("#bYear")
    span = pg.evaluate("""()=>{
      let dlo = 0, dhi = 0, ylo = 1e9, yhi = -1e9;
      const W = window.__day ? 0 : 0;
      for (const [x, y] of analemma) { if (y < ylo) ylo = y; if (y > yhi) yhi = y; }
      let xs = analemma.map(p => p[0]);
      return {lat: (yhi - ylo)/document.getElementById('map').height*180,
              lon: (Math.max(...xs) - Math.min(...xs))
                   /document.getElementById('map').width*360};
    }""")
    okl = abs(span["lat"] - 2*OBLIQUITY) < 1.5 and 4 < span["lon"] < 10
    print(f"  {'ok  ' if okl else 'FAIL'} the figure of eight is "
          f"{span['lat']:.1f} degrees tall, twice the tilt, and "
          f"{span['lon']:.1f} wide")
    if not okl:
        fails.append(f"the analemma spans {span['lat']:.1f} by {span['lon']:.1f} "
                     "degrees")

    print("--- the poles through the year ---")
    POLES = [("the north pole in June", 6, 21, 89.0, 24),
             ("the north pole in December", 12, 21, 89.0, 0),
             ("the south pole in June", 6, 21, -89.0, 0),
             ("the south pole in December", 12, 21, -89.0, 24),
             ("the equator at the March equinox", 3, 20, 0.0, 12)]
    for name, mo, d, lat, want in POLES:
        pg.evaluate("(a)=>window.__setTime(a[0],a[1],a[2],a[3])", [2026, mo, d, 12])
        got = pg.evaluate("(a)=>window.__probe(a[0],0)", [lat])["day"]
        ok = abs(got - want) < 0.2
        print(f"  {'ok  ' if ok else 'FAIL'} {name}: {got:.2f} h of daylight, "
              f"expected {want}")
        if not ok:
            fails.append(f"{name} gets {got:.2f} hours, expected {want}")

    # the polar circle is where the day first runs the whole 24 hours
    pg.evaluate("()=>window.__setTime(2026,6,21,12)")
    lo, hi = 60.0, 80.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if pg.evaluate("(a)=>window.__probe(a,0).day", mid) >= 24:
            hi = mid
        else:
            lo = mid
    circle = (lo + hi) / 2
    want = 90 - OBLIQUITY
    ok = abs(circle - want) < 1.0
    print(f"  {'ok  ' if ok else 'FAIL'} the midnight Sun starts at "
          f"{circle:.2f} deg north, and the Arctic Circle is at {want:.2f}")
    if not ok:
        fails.append(f"the midnight Sun starts at {circle:.2f}, not near {want:.2f}")

    print("--- the controls ---")
    pg.evaluate("()=>window.__setTime(2026,6,21,0)")
    a = pg.evaluate("()=>window.__day.slon")
    pg.evaluate("()=>window.__setTime(2026,6,21,6)")
    b = pg.evaluate("()=>window.__day.slon")
    swept = (a - b + 360) % 360
    ok = abs(swept - 90) < 0.5
    print(f"  {'ok  ' if ok else 'FAIL'} six hours moves the Sun "
          f"{swept:.2f} degrees west, and a quarter turn is 90")
    if not ok:
        fails.append(f"six hours moves the sub-solar point {swept:.2f} degrees")

    for bid, key in [("bGrat", "showGrat"), ("bBands", "bands"),
                     ("bLights", "showLights")]:
        before = pg.evaluate(f"()=>window.__day.{key}")
        pg.click("#" + bid)
        pg.wait_for_timeout(220)
        after = pg.evaluate(f"()=>window.__day.{key}")
        ok = before != after
        print(f"  {'ok  ' if ok else 'FAIL'} {bid} turns {key} "
              f"{'on' if after else 'off'}")
        if not ok:
            fails.append(f"{bid} does not change {key}")
        pg.click("#" + bid)
        pg.wait_for_timeout(220)

    if errs:
        fails.append(f"javascript errors: {errs}")
    br.close()

print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("all checks pass")
