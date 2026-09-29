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
          f"{worst[0] * 111000:.3f} meters on the ground, worst at {worst[1]}")
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
        pg.wait_for_timeout(600)   # the continents slide to the step
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

    print("--- the bar over the column moves the map too ---")
    pg.evaluate("()=>document.getElementById('bAll').click()")
    pg.evaluate("()=>window.scrollTo(0, 0)")     # the bar has to be on screen
    pg.wait_for_timeout(120)
    caja = pg.evaluate("()=>{const r=document.querySelector('#over rect.grab')"
                       ".getBoundingClientRect();return [r.x,r.y+r.height/2,r.width]}")
    dentro = pg.evaluate("([x,y])=>{const e=document.elementFromPoint(x,y);"
                         "return e ? e.getAttribute('class') : null}",
                         [caja[0] + caja[2] * 0.3, caja[1]])
    if dentro != "grab":
        fails.append(f"the bar is covered by {dentro!r} where the drag starts")
    pg.mouse.move(caja[0] + caja[2] * 0.30, caja[1])
    pg.mouse.down()
    pg.wait_for_timeout(120)
    lejos = pg.evaluate("()=>[window.__hist().paleoAge,"
                        "document.getElementById('ageOut').textContent]")
    ok = lejos[0] is None
    print(f"  {'ok  ' if ok else 'FAIL'} a third of the way along the bar is "
          f"older than the model, and the map says so: {lejos[1]!r}")
    if not ok:
        fails.append(f"the bar draws {lejos} where no model reaches")
    visto = []
    for f in (0.85, 0.92, 0.99):
        pg.mouse.move(caja[0] + caja[2] * f, caja[1])
        pg.wait_for_timeout(110)
        visto.append(pg.evaluate("()=>window.__hist().paleoAge"))
    pg.mouse.up()
    ok = all(v is not None for v in visto) and visto == sorted(visto, reverse=True)
    print(f"  {'ok  ' if ok else 'FAIL'} dragging along it walks the map "
          f"forward through {visto}")
    if not ok:
        fails.append(f"dragging the bar gives {visto}")

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

    print("--- between the steps, and the column as one instrument ---")
    def chk(ok, msg, extra=""):
        print(f"  {'ok  ' if ok else 'FAIL'} {msg}")
        if not ok:
            fails.append(msg + (f" [{extra}]" if extra else ""))
    # an interpolated rotation lands between its two steps, and on a step is the step
    q = pg.evaluate("""()=>{ const ll=[10,20], out={};
      for (const a of [140,145,150]) { const q=rotAt('701',a); out[a]=qrot(q,ll[0],ll[1]); }
      const r=poleOf('701',150); out.exact=rotate(ll[0],ll[1],r[1],r[2],r[3]); return out; }""")
    d = lambda a, b: math.hypot(a[0] - b[0], a[1] - b[1])
    chk(d(q["150"], q["exact"]) < 1e-6, "on a step the interpolated rotation is the model's own", f"{q}")
    chk(d(q["140"], q["145"]) < d(q["140"], q["150"]) and d(q["145"], q["150"]) < d(q["140"], q["150"]),
        "halfway between two steps a point lies between its two positions", f"{q}")
    pg.evaluate("()=>{const s=document.getElementById('tage');s.value=20;s.dispatchEvent(new Event('input'))}")
    pg.wait_for_timeout(200)
    mid = pg.evaluate("()=>window.__hist().paleoAge")
    pg.wait_for_timeout(500)
    end = pg.evaluate("()=>window.__hist().paleoAge")
    chk(mid is not None and end is not None and mid != end, f"a slider step slides the continents ({mid} on the way to {end} Ma)")
    ghost = pg.evaluate("document.querySelectorAll('#ghost path').length")
    chk(ghost == 1, "and today's outlines stay dashed underneath")
    out = pg.evaluate("document.getElementById('ageOut').textContent")
    chk("million years ago, the " in out, f"the readout names the unit: {out!r}")
    # the marker drags along the column
    pg.evaluate("()=>window.__zoom('Mesozoic')")
    pg.wait_for_timeout(200)
    pg.evaluate("()=>{document.getElementById('bNow').click()}")
    pg.evaluate("()=>{const s=document.getElementById('tage');s.value=" + str(len(edades) - 1 - sorted(edades).index(200)) + ";s.dispatchEvent(new Event('input'))}")
    pg.wait_for_timeout(700)
    g = pg.evaluate("()=>{const c=document.querySelector('#over circle.nowgrip'); if(!c) return null; const r=c.getBoundingClientRect(); return [r.x+r.width/2, r.y+r.height/2]}")
    chk(g is not None, "the map's marker on the column has a grip")
    if g:
        cb = pg.evaluate("()=>{const r=document.getElementById('col').getBoundingClientRect(); return [r.x, r.width]}")
        win = pg.evaluate("()=>window.__hist().win")
        want = 150
        tx = cb[0] + (54 + (win[0] - want) / (win[0] - win[1]) * (1000 - 108)) / 1000 * cb[1]
        pg.mouse.move(*g); pg.mouse.down(); pg.mouse.move(tx, g[1], steps=6); pg.mouse.up()
        pg.wait_for_timeout(100)
        h = pg.evaluate("()=>window.__hist()")
        chk(abs(h["ageSel"] - want) < 2 and abs(h["paleoAge"] - want) < 2, f"dragging it to 150 Ma draws the world at {h['paleoAge']}")
        out = pg.evaluate("document.getElementById('ageOut').textContent")
        chk("Jurassic" in out, f"and the readout says Jurassic: {out!r}")
    # the wheel zooms the column
    pg.evaluate("()=>document.getElementById('bAll').click()")
    pg.wait_for_timeout(100)
    cb = pg.evaluate("()=>{const r=document.getElementById('col').getBoundingClientRect(); return [r.x+r.width*0.9, r.y+r.height*0.4]}")
    pg.mouse.move(*cb)
    pg.mouse.wheel(0, -600)
    pg.wait_for_timeout(200)
    w = pg.evaluate("()=>window.__hist().win")
    chk(w[0] - w[1] < AGE * 0.6 and not pg.evaluate("document.getElementById('bOut').disabled"), f"the wheel zooms the column in: {w[0]:.0f} to {w[1]:.0f} Ma")
    pg.click("#bOut")
    pg.wait_for_timeout(100)
    w = pg.evaluate("()=>window.__hist().win")
    chk(w[0] >= AGE and w[1] == 0, "and Zoom out takes it back to the whole")
    # the labels of the events never collide
    clash = pg.evaluate("""()=>{const b=[...document.querySelectorAll('#events text')].map(t=>t.getBoundingClientRect()); let n=0;
      for(let i=0;i<b.length;i++) for(let j=i+1;j<b.length;j++) if(b[i].left<b[j].right&&b[j].left<b[i].right&&b[i].top<b[j].bottom&&b[j].top<b[i].bottom) n++; return n;}""")
    chk(clash == 0, f"no two event labels overlap ({clash})")
    vis = pg.evaluate("[...document.querySelectorAll('.notes p')].filter(n=>n.checkVisibility()).length")
    words = len(pg.inner_text(".notes.cap").split())
    chk(vis == 1 and words <= 80 and not pg.evaluate("document.querySelector('details.sources').open"), f"one caption of {words} words, the rest in a closed Sources")
    below = pg.evaluate("document.querySelector('.tiles').getBoundingClientRect().top > document.getElementById('globe').getBoundingClientRect().bottom")
    chk(below, "the column opens the page and the facts sit below the map")
    ph = br.new_page(viewport={"width": 390, "height": 844})
    ph.goto(PAGE.resolve().as_uri()); ph.wait_for_timeout(800)
    ov = ph.evaluate("document.documentElement.scrollWidth - innerWidth")
    chk(ov == 0, f"nothing wider than a phone ({ov} px)")

    if errs:
        fails.append(f"javascript errors: {errs}")
    br.close()

print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("all checks pass")
