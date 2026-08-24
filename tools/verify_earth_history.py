"""Check earth-history.html against the chart it is drawn from.

The chart data is checked first on its own terms, without the page: every unit
has to sit inside its parent, the children of a unit have to tile it with no
gap and no overlap, and the whole thing has to run from 4,567 Ma to the
present. Then the page is asked what it drew, and zoomed through several units
to confirm that a click really narrows the window to that unit and that its
children appear in the lane below.

Usage: pip install playwright && python3 verify_earth_history.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ics_chart import CHART, CHART_VERSION, EVENTS
from rotations import ROTATIONS, rotate_point

PAGE = Path(__file__).parent.parent / "earth-history.html"
AGE = 4567.0
fails = []

html = PAGE.read_text(encoding="utf-8")
print("--- the page itself ---")
for want in ("The History of Earth", "library.html", "ALTAZOR", "References",
             CHART_VERSION, "Cohen", "Merdith"):
    ok = want in html
    print(f"  {'ok  ' if ok else 'FAIL'} the page carries {want!r}")
    if not ok:
        fails.append(f"the page is missing {want!r}")
if "—" in re.sub(r"<script[\s\S]*?</script>", "", html):
    fails.append("an em dash in the page copy")

print("--- the chart holds together ---")
by = {u[0]: u for u in CHART}
kids = {}
for u in CHART:
    if u[2]:
        kids.setdefault(u[2], []).append(u)

eons = sorted((u for u in CHART if u[1] == "eon"), key=lambda u: -u[3])
ok = abs(eons[0][3] - AGE) < 1e-9 and abs(eons[-1][4]) < 1e-9
print(f"  {'ok  ' if ok else 'FAIL'} the eons run {eons[0][3]:,.0f} Ma to "
      f"{eons[-1][4]:.0f}")
if not ok:
    fails.append(f"the eons run {eons[0][3]} to {eons[-1][4]}, not {AGE} to 0")

gap = 0
for parent, ch in kids.items():
    ch = sorted(ch, key=lambda u: -u[3])
    p = by[parent]
    if abs(ch[0][3] - p[3]) > 1e-6 or abs(ch[-1][4] - p[4]) > 1e-6:
        gap += 1
        fails.append(f"the children of {parent} do not fill it")
    for a, b in zip(ch, ch[1:]):
        if abs(a[4] - b[3]) > 1e-6:
            gap += 1
            fails.append(f"{a[0]} ends at {a[4]} and {b[0]} begins at {b[3]}")
print(f"  {'ok  ' if not gap else 'FAIL'} the children of all {len(kids)} "
      "parents tile them with no gap and no overlap")

bad = 0
for u in CHART:
    if u[2] and not (by[u[2]][3] + 1e-6 >= u[3] >= u[4] >= by[u[2]][4] - 1e-6):
        bad += 1
        fails.append(f"{u[0]} does not sit inside {u[2]}")
    if u[3] <= u[4]:
        bad += 1
        fails.append(f"{u[0]} begins at {u[3]} and ends at {u[4]}")
print(f"  {'ok  ' if not bad else 'FAIL'} all {len(CHART)} units sit inside "
      "their parent and run older to younger")

bad = 0
for n, ma, rng, _, src in EVENTS:
    if not (0 <= ma <= AGE + 5):   # the oldest solids predate the chart's base
        bad += 1
        fails.append(f"the event {n} is dated {ma} Ma")
    if rng and not (min(rng) - 1e-9 <= ma <= max(rng) + 1e-9):
        bad += 1
        fails.append(f"the event {n} at {ma} is outside its own range {rng}")
    if not src:
        bad += 1
        fails.append(f"the event {n} names no source")
print(f"  {'ok  ' if not bad else 'FAIL'} all {len(EVENTS)} events fall inside "
      "the record, inside their own range, and name a source")

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("\nplaywright not installed")
    sys.exit(1)

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1440, "height": 1100})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.resolve().as_uri())
    pg.wait_for_function("() => !!window.__hist", timeout=15000)
    st = pg.evaluate("()=>window.__hist()")
    print("--- what the page drew ---")
    ok = st["units"] == len(CHART) and st["events"] == len(EVENTS)
    print(f"  {'ok  ' if ok else 'FAIL'} it carries {st['units']} units and "
          f"{st['events']} events")
    if not ok:
        fails.append(f"the page carries {st['units']} units, {st['events']} events")
    ok = AGE <= st["win"][0] <= AGE + 5 and st["win"][1] == 0
    print(f"  {'ok  ' if ok else 'FAIL'} it opens on the whole record")
    if not ok:
        fails.append(f"the page opens on {st['win']}")

    print("--- zooming in ---")
    for name in ["Phanerozoic", "Cenozoic", "Quaternary", "Holocene",
                 "Cretaceous", "Archean"]:
        pg.evaluate("()=>document.getElementById('bAll').click()")
        pg.wait_for_timeout(80)
        win = pg.evaluate("(n)=>window.__zoom(n)", name)
        u = by[name]
        held = (win[0] >= u[3] and win[1] <= u[4]
                and (win[0] - win[1]) < (u[3] - u[4]) * 1.2)
        ch = pg.evaluate("()=>window.__hist().drawn")
        want = len(kids.get(name, []))
        ok = held and ch >= want
        print(f"  {'ok  ' if ok else 'FAIL'} {name}: the window becomes "
              f"{win[0]:,.3f} to {win[1]:,.3f} Ma, and {ch} bands are drawn "
              f"around its {want} children")
        if not ok:
            fails.append(f"zooming to {name} gives {win} and draws {ch} bands")

    import math

    print("--- the reconstruction, against the model's own arithmetic ---")
    # The page turns each plate about a pole by an angle. The same rotation is
    # applied here by rotations.py, whose implementation was itself checked
    # against pygplates, so the page's arithmetic meets a second one rather
    # than only itself.
    PROBE = [(-33.9, 18.4, 701), (40.7, -74.0, 101), (-33.9, 151.2, 801),
             (28.6, 77.2, 501), (55.8, 37.6, 301), (-23.5, -46.6, 201),
             (-77.8, 166.7, 802)]
    worst = (0.0, "")
    n = 0
    for pid, age, plat, plon, ang, _rel in ROTATIONS:
        for la, lo, p2 in PROBE:
            if p2 != pid:
                continue
            n += 1
            got = pg.evaluate("(a)=>window.__rot(a[0],a[1],a[2],a[3])",
                              [la, lo, pid, age])
            want = rotate_point(plat, plon, ang, la, lo)
            # measured as an angle on the sphere: near a pole a longitude
            # difference is worth almost nothing on the ground, and comparing
            # the two coordinates separately would call that a failure
            d = math.degrees(2 * math.asin(min(1, math.sqrt(
                math.sin(math.radians(got[0] - want[0]) / 2) ** 2
                + math.cos(math.radians(got[0])) * math.cos(math.radians(want[0]))
                * math.sin(math.radians(got[1] - want[1]) / 2) ** 2))))
            if d > worst[0]:
                worst = (d, f"plate {pid} at {age} Ma")
    ok = worst[0] < 1e-6
    print(f"  {'ok  ' if ok else 'FAIL'} {n} rotations agree with the page to "
          f"{worst[0] * 111000:.3f} metres on the ground, worst at {worst[1]}")
    if not ok:
        fails.append(f"the page rotates differently by {worst[0]} deg at {worst[1]}")

    print("--- Pangaea is where it should be ---")
    # If the reconstruction works at all, west Africa and the east coast of
    # North America have to be touching in the late Palaeozoic and an ocean
    # apart now. This asks the page, not the model.

    def gc(a, b):
        la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
        h = (math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2)
             * math.sin((lo2 - lo1) / 2) ** 2)
        return 2 * 6371 * math.asin(min(1, math.sqrt(h)))

    MAUR, CHAR = (20.0, -17.0), (32.8, -79.9)
    for age, want in [(0, "an ocean apart"), (280, "touching")]:
        a = pg.evaluate("(a)=>window.__rot(a[0],a[1],701,a[2])",
                        [MAUR[0], MAUR[1], age])
        b = pg.evaluate("(a)=>window.__rot(a[0],a[1],101,a[2])",
                        [CHAR[0], CHAR[1], age])
        d = gc(a, b)
        ok = (d > 5000) if age == 0 else (d < 1800)
        print(f"  {'ok  ' if ok else 'FAIL'} at {age} Ma west Africa and "
              f"Carolina are {d:,.0f} km apart, which is {want}")
        if not ok:
            fails.append(f"at {age} Ma the two coasts are {d:,.0f} km apart")

    print("--- the slider runs the map ---")
    pg.evaluate("()=>document.getElementById('bAll').click()")
    pg.wait_for_timeout(80)
    pasos = pg.evaluate("()=>+document.getElementById('tage').max") + 1
    edades = sorted({r[1] for r in ROTATIONS})
    ok = pasos == len(edades)
    print(f"  {'ok  ' if ok else 'FAIL'} the slider has {pasos} stops and the "
          f"model holds {len(edades)} ages")
    if not ok:
        fails.append(f"the slider has {pasos} stops against {len(edades)} ages")

    visto, formas = [], []
    for v in (0, 8, 16, 24, 32, 40, pasos - 1):
        pg.evaluate("(v)=>{const s=document.getElementById('tage');s.value=v;"
                    "s.dispatchEvent(new Event('input'))}", v)
        pg.wait_for_timeout(90)
        h = pg.evaluate("()=>window.__hist()")
        visto.append(h["ageSel"])
        formas.append(h["plateD"])
        quiere = sorted(edades, reverse=True)[v]
        if h["ageSel"] != quiere or h["paleoAge"] != quiere:
            fails.append(f"stop {v} draws {h['paleoAge']} Ma, expected {quiere}")
    ok = visto == sorted(visto, reverse=True) and len(set(formas)) == len(formas)
    print(f"  {'ok  ' if ok else 'FAIL'} seven stops give the ages {visto} and "
          "seven different maps")
    if not ok:
        fails.append(f"the slider gives {visto} and {len(set(formas))} maps")

    # el botón de correr avanza solo, y el de hoy regresa
    pg.evaluate("()=>{const s=document.getElementById('tage');s.value=0;"
                "s.dispatchEvent(new Event('input'))}")
    pg.click("#bRun")
    pg.wait_for_timeout(1400)
    corriendo = pg.evaluate("()=>window.__hist()")
    pg.click("#bRun")
    pg.wait_for_timeout(80)
    parado = pg.evaluate("()=>window.__hist()")
    ok = corriendo["ageSel"] < 1000 and corriendo["corriendo"] and not parado["corriendo"]
    print(f"  {'ok  ' if ok else 'FAIL'} Run time walks the map forward, to "
          f"{corriendo['ageSel']} Ma in a second and a bit, and stops when told")
    if not ok:
        fails.append(f"Run time gives {corriendo} then {parado}")
    pg.click("#bNow")
    pg.wait_for_timeout(100)
    hoy = pg.evaluate("()=>window.__hist()")
    ok = hoy["ageSel"] == 0 and hoy["paleoAge"] == 0
    print(f"  {'ok  ' if ok else 'FAIL'} the world today button comes back to 0 Ma")
    if not ok:
        fails.append(f"the today button leaves it at {hoy['paleoAge']}")

    # y una banda de la columna le devuelve el mapa a la ventana
    pg.evaluate("(n)=>window.__zoom(n)", "Jurassic")
    pg.wait_for_timeout(120)
    j = pg.evaluate("()=>window.__hist()")
    marca = pg.evaluate("()=>document.querySelectorAll('#over .now').length")
    ok = j["ageSel"] is None and j["paleoAge"] and marca == 1
    print(f"  {'ok  ' if ok else 'FAIL'} a band clicked takes the map back to "
          f"{j['paleoAge']} Ma, and the column marks where that falls")
    if not ok:
        fails.append(f"after a click the map reads {j}, mark {marca}")

    print("--- how far back it draws ---")
    for name, want in [("Cretaceous", True), ("Cryogenian", True),
                       ("Tonian", True), ("Stenian", False),
                       ("Archean", False), ("Hadean", False)]:
        pg.evaluate("()=>document.getElementById('bAll').click()")
        pg.wait_for_timeout(60)
        pg.evaluate("(n)=>window.__zoom(n)", name)
        pg.wait_for_timeout(150)
        st2 = pg.evaluate("()=>window.__hist()")
        drawn = st2["plates"] > 0
        ok = drawn == want
        print(f"  {'ok  ' if ok else 'FAIL'} {name}: "
              + (f"drawn at {st2['paleoAge']} Ma" if drawn else "nothing drawn"))
        if not ok:
            fails.append(f"{name} draws {st2['plates']} plates, expected "
                         f"{'some' if want else 'none'}")

    pg.evaluate("()=>document.getElementById('bAll').click()")
    pg.wait_for_timeout(100)
    st = pg.evaluate("()=>window.__hist()")
    ok = AGE <= st["win"][0] <= AGE + 5 and st["depth"] == 0
    print(f"  {'ok  ' if ok else 'FAIL'} the All of time button puts it back")
    if not ok:
        fails.append("the All of time button does not reset the window")

    if errs:
        fails.append(f"javascript errors: {errs}")
    br.close()

print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("all checks pass")
