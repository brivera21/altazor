#!/usr/bin/env python3
"""Checks armor-of-god.html, the novel's solar system in 2500.

  the build    rebuilding from solar-system.html and the layer gives the page
               as it stands, byte for byte
  the base     every check the Library diagram passes, run on this page
  the layer    no script errors; the legend's five holders and the second
               legend's five icons; a 2500 block in the panel of every body
               that has one; Psyche and Hygiea in the belt at their distances;
               the Sails between the Sun and Mercury on the lenient line and at
               0.1 au at true scale, with 40 Lighthouses; the Hollows, 100 of
               them inside the belt; the Cyclers' loop from inside Earth's
               orbit to past Mars, with its three Cyclers; the Sun zone, the
               Gate, the Lines, the Hollows, the Cyclers and each holder open
               their own panels
  the panel    the Earth-Moon panel opens with Earth, and from the tag under
               Earth; it shows the three cored worlds, all three Prairie pairs,
               the Roads, Cumbre, the Counterweight, the Moon, Lagrange and
               Yongle; its distances are to scale and L4 and L5 sit 60 degrees
               either side of the Moon
  the text     what the 2500 blocks and the panel say carries no years, no em
               dashes and nothing dropped from the canon, and none of the terms
               kept off the site. That list is not kept here: pass its path in
               AOG_HIDDEN to run that part.

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
# this page ends at the Kuiper belt: no Eris, Sedna, heliopause or Oort cloud
for x, y in ((',\n              "XIII. HELIOPAUSE", "XIV. OORT CLOUD"]', ']'),
             (',\n            "Oort Cloud": (2000, 100000)}', '}'),
             (',\n             "Eris": (67.69, 1163, "2,326"), "Sedna": (506, 500, "1,000")}', '}')):
    assert base.count(x) == 1, x
    base = base.replace(x, y)
i = base.index("    pg.evaluate(\"()=>document.querySelector('.chip[data-name=\\\"Heliopause\\\"]').click()\")")
j = base.index("    pg.click(\"#scaleBtn\")\n    pg.wait_for_timeout(1500)\n    print(\"  ok   the Trojans", i)
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
    check(a["icons"] == 6, "the second legend: a heading and five icons")
    check(a["lights"] == 40, "40 Lighthouses among the Sails")
    bx0, bx1 = a["belt"]
    check(len(a["hollows"]) == 100 and all(bx0 <= x <= bx1 for x, y in a["hollows"]), "the Hollows: 100, all inside the belt")
    cy = a["cyclers"]
    check(cy["a"] < cy["earth"] and cy["mars"] < cy["b"] < bx0 + (bx1 - bx0) * 0.2,
          "the Cyclers' loop runs from just inside Earth's orbit to past Mars's")
    check([c[0] for c in cy["at"]] == ["Ellis", "Galveston", "Angel"], "the three Cyclers on the loop")
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
    a = pg.evaluate("()=>__dbg.aog")
    hx, hy = a["hollowsLabel"]
    click_open(hx + 20, hy - 3, "The Hollows", "a click on the Hollows' label")
    a = pg.evaluate("()=>__dbg.aog")
    n, x, y = a["cyclers"]["at"][1]
    click_open(x, y, "The Cyclers", f"a click on {n}")
    # the Earth tag opens Earth and its panel
    a = pg.evaluate("()=>__dbg.aog")
    check(len(a["earthTag"]) == 1, "the tag under Earth is drawn")
    pg.mouse.click(*a["earthTag"][0])
    pg.wait_for_timeout(1500)
    nm = pg.evaluate("()=>document.querySelector('#iName').textContent")
    a = pg.evaluate("()=>__dbg.aog")
    check(nm == "Earth" and a["em"], "the tag under Earth opens Earth, with the Earth-Moon panel")
    if a["em"]:
        want = {"Armstrong", "Penglai", "The Pearl", "A Prairie pair in Armstrong's orbit", "Two Prairie pairs near the Pearl",
                "The Roads", "Cumbre", "The Counterweight", "The Moon", "The Quarry", "Lagrange", "Yongle", "The elevator"}
        check(want <= set(a["em"]), f"the panel shows {sorted(want - set(a['em'])) or 'everything'}")
        g = a["emGeo"]
        import math
        d = lambda p: math.hypot(p[0] - g["earth"][0], p[1] - g["earth"][1])
        ang = lambda p: math.degrees(math.atan2(-(p[1] - g["earth"][1]), p[0] - g["earth"][0])) % 360
        check(abs(d(g["moon"]) / d(g["arm"]) - 384400 / 116000) < 0.01, "the panel: the Moon and Armstrong at their true distances")
        check(abs(d(g["l4"]) - d(g["moon"])) < 0.5 and abs(d(g["l5"]) - d(g["moon"])) < 0.5
              and abs((ang(g["l4"]) - ang(g["moon"])) % 360 - 60) < 0.5 and abs((ang(g["moon"]) - ang(g["l5"])) % 360 - 60) < 0.5,
              "the panel: L4 60 degrees ahead of the Moon, L5 60 degrees behind, on its orbit")
        st = g["strip"]
        r = lambda x: (x - st["earth"]) / st["re"] * 6371
        check(abs(r(st["cumbre"]) - 42164) < 60 and abs(r(st["cw"]) - 106371) < 60 and abs(st["arm"] / st["re"] * 6371 - 116000) < 60,
              "the panel, enlarged: Cumbre at 35,786 km up, the Counterweight at 100,000, Armstrong 116,000 km out")
        texts.extend(a["emTips"])
    pg.click("#emClose")
    pg.wait_for_timeout(300)
    check(pg.evaluate("()=>document.getElementById('em').hidden"), "the panel closes")
    pg.click("#aog .aog-em")
    pg.wait_for_timeout(300)
    check(not pg.evaluate("()=>document.getElementById('em').hidden"), "the button in Earth's block opens it again")
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(1300)
    check(pg.evaluate("()=>document.getElementById('em').hidden"), "it closes when Earth is let go")
    for k, nm in (("l5", "The United Reaches"), ("ind", "Independent"), ("tied", "Tied to the US-led bloc"),
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
gone = [t for t in ("Presidio", "Terraria", "Arcadia", "Kranz Station", "Lancaster Station", "cored station", "Amun",
                    "University-class", "Campus-class", "Sprawl-class", "biomass", "L5 nation", "Machine-core")
        if t.lower() in (blob + (ROOT / "tools" / "armor_of_god_2500.js").read_text(encoding="utf-8")).lower()]
check(not gone, f"nothing dropped from the canon is left {gone}")
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
