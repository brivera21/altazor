#!/usr/bin/env python3
"""Checks armor-of-god.html, the novel's solar system in 2500.

  the build    rebuilding from solar-system.html and the layer gives the page
               as it stands, byte for byte
  the base     every check the Library diagram passes, run on this page
  the layer    no script errors; the legend's five holders; a 2500 block in
               the panel of every body that has one; Psyche and Hygiea in the
               belt at their distances; the Sails between the Sun and Mercury
               on the lenient line and at 0.1 au at true scale; the Sun zone,
               the Gate, the Lines and each holder open their own panels
  the text     what the 2500 blocks say carries no years and no em dashes,
               and none of the terms kept off the site. That list is not kept
               here: pass its path in AOG_HIDDEN to run that part.

Usage: AOG_HIDDEN=/path/to/list python3 tools/verify_armor_of_god.py
"""

import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "armor-of-god.html"
FAILS = []


def check(ok, what):
    print(("  ok   " if ok else "  FAIL ") + what)
    if not ok:
        FAILS.append(what)


print("--- the build ---")
before = PAGE.read_bytes()
subprocess.run([sys.executable, str(ROOT / "tools" / "build_armor_of_god.py")], check=True, capture_output=True)
check(PAGE.read_bytes() == before, "the page is what the builder makes")

print("--- the base ---")
base = (ROOT / "tools" / "verify_solar_system.py").read_text(encoding="utf-8")
base = base.replace('/ "solar-system.html"', '/ "armor-of-god.html"')
# this page draws no size ghost on the Sun or the planets, so the checks of
# that ghost become one check that it is absent
i = base.index("    WANT_GHOST = {")
j = base.index("    labels = pg.evaluate(", i)
base = base[:i] + """    for name in ("Sun", "Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"):
        pg.click(f'.chip[data-name="{name}"]')
        pg.wait_for_timeout(1500)
        if pg.evaluate("()=>__dbg.ghost"):
            fails.append(f"{name}: a size ghost is drawn")
    print("  ok   no body is drawn to scale against the Sun or the planets")
    pg.click('.chip[data-name="Jupiter"]')
    pg.wait_for_timeout(1500)
""" + base[j:]
i = base.index("    # the ghost can be Jupiter")
j = base.index("    # the new neighbors", i)
base = base[:i] + base[j:]
# this page adds Psyche and Hygiea to the belt
for x, y in (('"Pallas": (2.772, 256, "512"), "Pluto"',
              '"Pallas": (2.772, 256, "512"), "Psyche": (2.924, 111, "222"), "Hygiea": (3.142, 216.5, "433"), "Pluto"'),
             ('"Pallas": (BELT_IN, BELT_OUT), "Pluto"',
              '"Pallas": (BELT_IN, BELT_OUT), "Psyche": (BELT_IN, BELT_OUT), "Hygiea": (BELT_IN, BELT_OUT), "Pluto"')):
    assert base.count(x) == 1, x
    base = base.replace(x, y)
tmp = ROOT / "tools" / "_verify_aog_base.py"
tmp.write_text(base, encoding="utf-8")
try:
    r = subprocess.run([sys.executable, str(tmp)], capture_output=True, text=True, cwd=ROOT / "tools")
finally:
    tmp.unlink()
tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:]
check(r.returncode == 0, f"the Library diagram's checks pass here too ({tail})")
if r.returncode:
    print("\n".join(l for l in r.stdout.splitlines() if l.startswith("FAIL")))

print("--- the layer ---")
from playwright.sync_api import sync_playwright  # noqa: E402

texts = []
with sync_playwright() as p:
    br = p.chromium.launch()
    pg = br.new_page(viewport={"width": 1440, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("https://**", lambda r: r.abort())
    pg.goto(PAGE.resolve().as_uri())
    pg.wait_for_timeout(1200)
    a = pg.evaluate("()=>__dbg.aog")
    check(a["legend"] == 6, "the legend: a heading and five holders")
    check(a["sunEdge"] < a["sails"] < a["zone"][0] < a["zone"][1] < a["mercury"],
          "lenient: the Sails, then the stations, between the Sun's edge and Mercury")
    small = {b["name"]: b for b in pg.evaluate("()=>__dbg.small")}
    belt = pg.evaluate("()=>__dbg.belt")
    order = [small[n]["sx"] for n in ("Vesta", "Ceres", "Psyche", "Hygiea")]
    check(order == sorted(order) and belt["xIn"] <= small["Vesta"]["x"] and small["Hygiea"]["x"] <= belt["xOut"],
          "Vesta, Ceres, Psyche and Hygiea in order, inside the belt")
    check(abs(small["Psyche"]["trueX"] / small["Ceres"]["trueX"] - 2.924 / 2.766) < 1e-9
          and abs(small["Hygiea"]["trueX"] / small["Ceres"]["trueX"] - 3.142 / 2.766) < 1e-9,
          "true scale: Psyche at 2.924 au and Hygiea at 3.142 au")

    # every body's panel
    for name in ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Asteroid Belt"]:
        pg.click(f'.chip[data-name="{name}"]')
        pg.wait_for_timeout(700)
        shown = pg.evaluate("()=>!document.getElementById('aog').hidden && document.querySelectorAll('#aog .aog-held').length")
        check(bool(shown), f"{name}: the panel carries who holds it in 2500")
        texts.append(pg.evaluate("()=>document.getElementById('aog').innerText"))
    pg.click('.chip:text-is("Overview")')
    pg.wait_for_timeout(1500)

    def click_open(x, y, want, what):
        pg.mouse.click(x, y)
        pg.wait_for_timeout(900)
        nm = pg.evaluate("()=>document.querySelector('#iName').textContent")
        dl = pg.evaluate("()=>document.querySelector('#info dl').style.display")
        check(nm == want and dl == "none", f"{what} opens {want!r}, without the real-body rows")
        texts.append(pg.evaluate("()=>document.getElementById('aog').innerText"))
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(1300)

    a = pg.evaluate("()=>__dbg.aog")
    click_open(a["sails"], 300, "The Sun Zone", "a click on the Sails")
    a = pg.evaluate("()=>__dbg.aog")
    click_open(a["gate"][0], a["gate"][1], "The Gate", "a click on the Gate")
    a = pg.evaluate("()=>__dbg.aog")
    click_open((a["lines"]["a"] + a["lines"]["b"]) / 2, a["lines"]["y"], "The Lines", "a click on the Lines")
    for name in ("Ceres", "Vesta", "Psyche", "Hygiea"):
        b = {x["name"]: x for x in pg.evaluate("()=>__dbg.small")}[name]
        pg.mouse.click(b["sx"], b["y"])
        pg.wait_for_timeout(900)
        nm = pg.evaluate("()=>document.querySelector('#iName').textContent")
        shown = pg.evaluate("()=>!document.getElementById('aog').hidden")
        check(nm == name and shown, f"{name}: a click opens its panel, with its 2500 block")
        texts.append(pg.evaluate("()=>document.getElementById('aog').innerText"))
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(1300)
    for k, nm in (("l5", "The L5 nation"), ("ind", "Independent"), ("tied", "Tied to the US-led bloc"),
                  ("earth", "Held from Earth"), ("none", "No one, or a treaty")):
        pg.click(f'#aogLegend button[data-k="{k}"]')
        pg.wait_for_timeout(500)
        got = pg.evaluate("()=>document.querySelector('#iName').textContent")
        on = pg.evaluate(f"()=>document.querySelector('#aogLegend button[data-k=\"{k}\"]').classList.contains('on')")
        check(got == nm and on, f"the legend opens {nm!r} and marks it")
        texts.append(pg.evaluate("()=>document.getElementById('aog').innerText"))
    pg.keyboard.press("Escape")
    # true scale: the Sails at a tenth of an au
    pg.click("#scaleBtn")
    pg.wait_for_timeout(2600)
    a = pg.evaluate("()=>__dbg.aog")
    sun = pg.evaluate("()=>__dbg.extra.sunX")
    cer = pg.evaluate("()=>__dbg.extra.ceresX")
    check(abs((a["sails"] - sun) / (cer - sun) - 0.1 / 2.766) < 0.002, "true scale: the Sails at 0.1 au")
    check(not errs, f"no script errors {errs}")
    br.close()

print("--- the text ---")
blob = "\n".join(texts)
years = sorted(set(re.findall(r"\b(1[4-9]\d\d|2[0-6]\d\d)\b", blob)) - {"2500"})
check(not years, f"the 2500 blocks carry no years {years}")
check("—" not in blob, "no em dashes in the 2500 blocks")
layer = (ROOT / "tools" / "armor_of_god_2500.js").read_text(encoding="utf-8")
check("—" not in layer, "no em dashes in the layer")
hidden = os.environ.get("AOG_HIDDEN")
if hidden and pathlib.Path(hidden).exists():
    terms = [t.strip() for t in pathlib.Path(hidden).read_text(encoding="utf-8").splitlines()
             if t.strip() and not t.startswith("#")]
    # names the author has chosen to keep, which the list would otherwise catch
    keep = {"lowell", "lancaster"}
    files = {f: (ROOT / f).read_text(encoding="utf-8") for f in
             ("tools/armor_of_god_2500.js", "tools/build_armor_of_god.py", "tools/verify_armor_of_god.py")}
    files["the panels"] = blob
    hits = []
    for t in terms:
        if t.lower() in keep:
            continue
        pat = re.compile(r"(?<![\w])" + re.escape(t) + r"(?![\w])", re.I)
        for f, s in files.items():
            if pat.search(s):
                hits.append((t, f))
    check(not hits, f"none of the {len(terms)} kept-off terms appears" + (f": {hits}" if hits else ""))
else:
    print("  --   the kept-off terms: skipped, no list given")

print()
print("all checks pass" if not FAILS else f"{len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
