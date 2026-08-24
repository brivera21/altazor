"""Checks energy.html against its data and against its drawing.

  the data     every flow joins two known forms, the second-law count holds
               (four arrows into thermal, two out), and no flow repeats
  the page     draws nine forms and nineteen arrows, the card answers, and
               clicking a form dims what does not touch it
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_energy import FORMS, FLOWS

fails = []
print("--- the data ---")
keys = {k for k, *_ in FORMS}
ok = len(FORMS) == 9 and len(keys) == 9
print(f"  {'ok  ' if ok else 'FAIL'} nine forms, each once")
if not ok: fails.append("forms")
bad = [(a, b) for a, b, *_ in FLOWS if a not in keys or b not in keys or a == b]
ok = not bad and len({(a, b) for a, b, *_ in FLOWS}) == len(FLOWS)
print(f"  {'ok  ' if ok else 'FAIL'} every flow joins two different known "
      "forms, none repeated")
if not ok: fails.append(f"flows: {bad}")
into = sum(1 for a, b, *_ in FLOWS if b == "th")
out = sum(1 for a, b, *_ in FLOWS if a == "th")
ok = into == 4 and out == 2
print(f"  {'ok  ' if ok else 'FAIL'} the second-law count: {into} into "
      f"thermal, {out} out, as the page says")
if not ok: fails.append(f"thermal {into}/{out}")
s = (Path(__file__).parent.parent / "energy.html").read_text(encoding="utf-8")
for frag in ["feynmanlectures.caltech.edu/I_04", "bipm.org", "E = mc",
             "first law", "second"]:
    ok = frag in s
    print(f"  {'ok  ' if ok else 'FAIL'} the page carries '{frag}'")
    if not ok: fails.append(f"missing {frag}")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1280, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((Path(__file__).parent.parent / "energy.html").resolve().as_uri())
    pg.wait_for_selector("#ensvg")
    st = pg.evaluate("()=>window.__en()")
    nf = pg.evaluate("()=>document.querySelectorAll('#ensvg g[data-f]').length")
    na = pg.evaluate("()=>document.querySelectorAll('#ensvg g[data-fl]').length")
    ok = nf == 9 and na == 19 and st["forms"] == 9 and st["flows"] == 19
    print(f"  {'ok  ' if ok else 'FAIL'} nine forms and nineteen arrows drawn "
          f"({nf}, {na})")
    if not ok: fails.append(f"drawn {nf}/{na}")
    card = pg.evaluate("()=>{showFlow(FLOWS.findIndex(f=>f.n==='Generator'));"
                       "return document.getElementById('kindTxt').textContent"
                       "+' | '+document.getElementById('nameTxt').textContent}")
    ok = card == "Kinetic → Electrical | Generator"
    print(f"  {'ok  ' if ok else 'FAIL'} the arrow card answers: '{card}'")
    if not ok: fails.append(f"card: {card}")
    dim = pg.evaluate("()=>{sel='mass';render();"
                      "return [...document.querySelectorAll('#ensvg g[data-fl]')]"
                      ".filter(g=>+g.getAttribute('opacity')<1).length}")
    ok = dim == 17
    print(f"  {'ok  ' if ok else 'FAIL'} selecting rest mass dims {dim} of 19 "
          "arrows, leaving its two")
    if not ok: fails.append(f"dims {dim}")
    if errs: fails.append(f"js errors: {errs}")
    br.close()
print()
if fails:
    for f in fails: print("FAIL", f)
    sys.exit(1)
print("everything squares")
