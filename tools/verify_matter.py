"""Checks matter.html against its data and against its drawing.

  the data     118 elements once each, on the standard grid, every family
               known, American spellings, photographs where they exist
  the page     draws the grid, the legend filters, and the card answers
  the controls Play on the temperature and on the year found, the ramp's
               marker and threshold, a family's line in the legend, the
               sources tucked away, and the phone layout
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from build_matter import data, FAMILIES

fails = []
print("--- the data ---")
ok = len(data) == 118 and len({d["z"] for d in data}) == 118
print(f"  {'ok  ' if ok else 'FAIL'} 118 elements, each once")
if not ok: fails.append("element count")
ok = len({(d["x"], d["y"]) for d in data}) == 118
print(f"  {'ok  ' if ok else 'FAIL'} no two elements share a grid cell")
if not ok: fails.append("grid collision")
names = {d["z"]: d["n"] for d in data}
ok = (names[13] == "Aluminum" and names[16] == "Sulfur"
      and names[55] == "Cesium" and names[118] == "Oganesson")
print(f"  {'ok  ' if ok else 'FAIL'} IUPAC spellings: Aluminum, Sulfur, Cesium")
if not ok: fails.append(f"spellings: {names[13]}, {names[16]}, {names[55]}")
n_photo = sum(1 for d in data if d["img"])
ok = n_photo >= 100 and all(
    d["img"].startswith(("https://upload.wikimedia.org/", "https://images-of-elements.com/"))
    for d in data if d["img"])
print(f"  {'ok  ' if ok else 'FAIL'} {n_photo} photographs, all from the two "
      "credited hosts")
if not ok: fails.append("photo hosts")
gold = next(d for d in data if d["z"] == 79)
ok = gold["s"] == "Au" and abs(gold["m"] - 196.967) < 0.01 and gold["f"] == "transition metal"
print(f"  {'ok  ' if ok else 'FAIL'} spot check, gold: {gold['s']}, {gold['m']}")
if not ok: fails.append("gold data")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1280, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("**upload.wikimedia.org/**", lambda r: r.abort())
    pg.route("**images-of-elements.com/**", lambda r: r.abort())
    pg.goto((HERE.parent / "matter.html").resolve().as_uri())
    pg.wait_for_selector("#table .cell")
    n = pg.evaluate("()=>document.querySelectorAll('.cell[data-z]').length")
    ok = n == 118
    print(f"  {'ok  ' if ok else 'FAIL'} 118 cells drawn ({n})")
    if not ok: fails.append(f"{n} cells")
    card = pg.evaluate("()=>{show(26);return document.getElementById('elTxt').textContent}")
    ok = card == "Iron (Fe)"
    print(f"  {'ok  ' if ok else 'FAIL'} the card answers: '{card}'")
    if not ok: fails.append(f"card: {card}")
    dim = pg.evaluate("()=>{famSel='noble gas';paint();"
                      "return document.querySelectorAll('.cell.dim').length}")
    ok = dim == 112
    print(f"  {'ok  ' if ok else 'FAIL'} the noble-gas filter dims {dim} of 118")
    if not ok: fails.append(f"filter dims {dim}")
    og = pg.evaluate("()=>{famSel=null;paint();show(118);"
                     "return document.getElementById('photo').getAttribute('alt')}")
    ok = "never existed in a visible amount" in og
    print(f"  {'ok  ' if ok else 'FAIL'} oganesson says why there is no "
          "photograph")
    if not ok: fails.append(f"og alt: {og}")
    print("--- the controls ---")
    # every family has a line saying why its members behave alike
    lines = pg.evaluate("()=>FAMS.map(f=>f.w.length)")
    ok = len(lines) == len(FAMILIES) and min(lines) > 40
    print(f"  {'ok  ' if ok else 'FAIL'} {len(lines)} families each carry a line in "
          "the legend")
    if not ok: fails.append(f"family lines {lines}")
    note = pg.evaluate("()=>{famSel='noble gas';paint();"
                       "return document.getElementById('famNote').textContent}")
    ok = "full outer shell" in note
    print(f"  {'ok  ' if ok else 'FAIL'} the noble gas line shows on a click: '{note[:50]}'")
    if not ok: fails.append(f"famNote {note}")
    pg.evaluate("()=>{famSel=null;paint()}")
    # the ramp: a marker for the element under the pointer, a drag as a threshold
    pg.click("[data-m=den]")
    pg.hover(".cell[data-z='79']")
    mark = pg.evaluate("()=>{const m=document.getElementById('rampMark');"
                       "return [m.style.display, parseFloat(m.style.left)]}")
    ok = mark[0] == "block" and 85 < mark[1] < 92      # gold, near the dense end
    print(f"  {'ok  ' if ok else 'FAIL'} gold under the pointer marks the ramp at "
          f"{mark[1]:.1f}% of the way to the densest")
    if not ok: fails.append(f"ramp mark {mark}")
    r = pg.evaluate("()=>{const b=document.getElementById('ramp').getBoundingClientRect();"
                    "return [b.x,b.y,b.width,b.height]}")
    pg.mouse.move(r[0] + 3, r[1] + 5); pg.mouse.down()
    pg.mouse.move(r[0] + r[2] * 0.5, r[1] + 5, steps=5); pg.mouse.up()
    st = pg.evaluate("()=>window.__mt()")
    ok = st["thr"] is not None and abs(st["thr"] - 0.5) < 0.03 and st["dim"] == 17
    print(f"  {'ok  ' if ok else 'FAIL'} a drag to the middle of the ramp sets a "
          f"threshold at {st['thr']:.2f} and dims {st['dim']} elements below it")
    if not ok: fails.append(f"threshold {st}")
    pg.mouse.click(r[0] + 30, r[1] + 5)
    ok = pg.evaluate("()=>window.__mt()")["thr"] is None
    print(f"  {'ok  ' if ok else 'FAIL'} a click on the ramp clears it")
    if not ok: fails.append("threshold clear")
    # Play on the year found
    pg.click("[data-m=yr]")
    pg.click("#yplay"); pg.wait_for_timeout(1500)
    st = pg.evaluate("()=>window.__mt()")
    txt = pg.evaluate("()=>document.getElementById('yearTxt').textContent")
    ok = st["yplay"] and st["yearCut"] is not None and 1650 < st["yearCut"] < 2010 \
        and st["off"] > 0 and "known" in txt \
        and pg.evaluate("()=>document.getElementById('yplay').textContent") == "Pause"
    print(f"  {'ok  ' if ok else 'FAIL'} Play on the year found runs: '{txt}', "
          f"{st['off']} elements still to come")
    if not ok: fails.append(f"year play {st} {txt}")
    pg.click("#yplay")
    ok = not pg.evaluate("()=>window.__mt().yplay")
    print(f"  {'ok  ' if ok else 'FAIL'} and a second press pauses it")
    if not ok: fails.append("year pause")
    # Play on the temperature
    pg.click("[data-m=state]")
    pg.click("#tplay"); pg.wait_for_timeout(1500)
    st = pg.evaluate("()=>window.__mt()")
    ok = st["tplay"] and 4 < st["temp"] < 4000 and st["yearCut"] is None \
        and pg.evaluate("()=>document.getElementById('tplay').textContent") == "Pause"
    print(f"  {'ok  ' if ok else 'FAIL'} Play on the temperature sweeps: {st['temp']} K "
          "after 1.5 s, reading Pause")
    if not ok: fails.append(f"temp play {st}")
    pg.click("#tplay")
    ok = not pg.evaluate("()=>window.__mt().tplay")
    print(f"  {'ok  ' if ok else 'FAIL'} and a second press pauses it")
    if not ok: fails.append("temp pause")
    # a pinned card lets go on Escape
    pg.click("[data-m=family]")
    pg.click(".cell[data-z='26']")
    pinned = pg.evaluate("()=>window.__mt().pinned")
    pg.keyboard.press("Escape")
    ok = pinned == 26 and pg.evaluate("()=>window.__mt().pinned") is None
    print(f"  {'ok  ' if ok else 'FAIL'} a click pins iron and Escape lets go")
    if not ok: fails.append(f"pin {pinned}")
    ok = pg.evaluate("()=>{const d=document.querySelector('details.sources');"
                     "return d&&!d.open&&d.textContent.includes('Periodic-Table-JSON')"
                     "&&document.querySelectorAll('p.note').length===2}")
    print(f"  {'ok  ' if ok else 'FAIL'} the data sources sit inside a closed Sources details")
    if not ok: fails.append("sources details")
    ph = br.new_page(viewport={"width": 390, "height": 844})
    ph.route("**upload.wikimedia.org/**", lambda r: r.abort())
    ph.route("**images-of-elements.com/**", lambda r: r.abort())
    ph.goto((HERE.parent / "matter.html").resolve().as_uri())
    ph.wait_for_selector("#table .cell")
    w = ph.evaluate("()=>[document.documentElement.scrollWidth-innerWidth,"
                    "document.querySelector('#table').getBoundingClientRect().height,"
                    "document.querySelector('.card').getBoundingClientRect().top<"
                    "document.querySelector('#table').getBoundingClientRect().top]")
    ok = w[0] == 0 and w[1] < 260 and w[2]
    print(f"  {'ok  ' if ok else 'FAIL'} at 390 px nothing overflows, the table is "
          f"{w[1]:.0f} px tall and the card sits above it")
    if not ok: fails.append(f"phone {w}")
    ph.close()

    if errs: fails.append(f"js errors: {errs}")
    br.close()
print()
if fails:
    for f in fails: print("FAIL", f)
    sys.exit(1)
print("everything squares")
