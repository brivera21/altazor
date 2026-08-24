"""Checks matter.html against its data and against its drawing.

  the data     118 elements once each, on the standard grid, every family
               known, IUPAC spellings, photographs where they exist
  the page     draws the grid, the legend filters, and the card answers
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
ok = (names[13] == "Aluminium" and names[16] == "Sulfur"
      and names[55] == "Caesium" and names[118] == "Oganesson")
print(f"  {'ok  ' if ok else 'FAIL'} IUPAC spellings: Aluminium, Sulfur, Caesium")
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
    if errs: fails.append(f"js errors: {errs}")
    br.close()
print()
if fails:
    for f in fails: print("FAIL", f)
    sys.exit(1)
print("everything squares")
