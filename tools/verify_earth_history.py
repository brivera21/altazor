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

PAGE = Path(__file__).parent.parent / "earth-history.html"
AGE = 4567.0
fails = []

html = PAGE.read_text(encoding="utf-8")
print("--- the page itself ---")
for want in ("The History of Earth", "library.html", "ALTAZOR", "References",
             CHART_VERSION, "Cohen"):
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
