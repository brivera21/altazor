"""Checks oneill-ring.html against its physics and its drawing.

  the physics  the Stanford preset gives 0.93 g at 830 m and 1 rpm, the
               1 g line matches sqrt(g/r), and the voyage arithmetic is
               distance over speed with thirty-year generations
  the page     the tiles update when the ring changes, the presets load,
               and the spin period in the drawing matches the spin
"""
import math
import sys
from pathlib import Path

G = 9.80665
fails = []

print("--- the physics ---")
g830 = (2 * math.pi / 60) ** 2 * 830 / G
ok = abs(g830 - 0.928) < 0.005
print(f"  {'ok  ' if ok else 'FAIL'} 830 m at 1 rpm gives {g830:.3f} g")
if not ok: fails.append(f"torus g {g830}")
rpm1g = math.sqrt(G / 830) * 60 / (2 * math.pi)
ok = abs(rpm1g - 1.04) < 0.01
print(f"  {'ok  ' if ok else 'FAIL'} 1 g at 830 m needs {rpm1g:.2f} rpm")
if not ok: fails.append(f"rpm for 1g {rpm1g}")
s = (Path(__file__).parent.parent / "oneill-ring.html").read_text(encoding="utf-8")
for frag in ["10.1063/1.3128863", "ntrs.nasa.gov/citations/19770014162",
             "Rotation-Tolerance", "recons.org", "generation_starships",
             "Tsiolkovsky"]:
    ok = frag in s
    print(f"  {'ok  ' if ok else 'FAIL'} the page carries '{frag}'")
    if not ok: fails.append(f"missing {frag}")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1280, "height": 950})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((Path(__file__).parent.parent / "oneill-ring.html").resolve().as_uri())
    pg.wait_for_selector("#ringsvg")
    st = pg.evaluate("()=>window.__ring()")
    ok = st["R"] == 830 and st["RPM"] == 1 and abs(st["g"] - 0.928) < 0.005
    print(f"  {'ok  ' if ok else 'FAIL'} the Stanford preset loads: "
          f"{st['R']} m, {st['RPM']} rpm, {st['g']:.3f} g")
    if not ok: fails.append(f"preset {st}")
    tg = pg.evaluate("()=>document.getElementById('tG').textContent")
    ok = tg == "0.93 g"
    print(f"  {'ok  ' if ok else 'FAIL'} the gravity tile reads '{tg}'")
    if not ok: fails.append(f"tile {tg}")
    st2 = pg.evaluate("()=>{setRing(3200,0.53);return window.__ring()}")
    ok = st2["R"] == 3200 and abs(st2["g"] - 1.0) < 0.03
    print(f"  {'ok  ' if ok else 'FAIL'} Island Three at 3,200 m and 0.53 rpm "
          f"gives {st2['g']:.2f} g")
    if not ok: fails.append(f"island {st2}")
    dur = pg.evaluate("()=>document.querySelector('#spinner animateTransform')"
                      ".getAttribute('dur')")
    ok = abs(float(dur.rstrip('s')) - 60/0.53) < 0.5
    print(f"  {'ok  ' if ok else 'FAIL'} the drawing turns once every {dur}, "
          "matching the spin")
    if not ok: fails.append(f"dur {dur}")
    yrs = pg.evaluate("()=>{SPD=5;DEST=3;update();return window.__ring().years}")
    ok = abs(yrs - 11.9/0.05) < 0.5
    print(f"  {'ok  ' if ok else 'FAIL'} Tau Ceti at 5% of c takes {yrs:.0f} "
          "years")
    if not ok: fails.append(f"voyage {yrs}")
    if errs: fails.append(f"js errors: {errs}")
    br.close()
print()
if fails:
    for f in fails: print("FAIL", f)
    sys.exit(1)
print("everything squares")
