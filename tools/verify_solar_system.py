"""Check solar-system.html, with attention to the asteroid belt.

The belt is a region rather than a body, so the things worth checking are that
its edges land where the real belt is, that it sits between Mars and Jupiter in
both layouts, that it is numbered VI with everything past it moved up one, and
that selecting it does not fall through code written for bodies with a radius.

Usage: python3 verify_solar_system.py
"""
import sys
from pathlib import Path

PAGE = Path(__file__).parent.parent / "solar-system.html"
AU_KM = 149.6e6

# The main belt, and the bodies either side of it.
BELT_IN, BELT_OUT = 2.1, 3.3
MARS_AU, JUPITER_AU = 1.524, 5.204

WANT_CHIPS = ["Overview", "I. SUN", "II. MERCURY", "III. VENUS", "IV. EARTH",
              "V. MARS", "VI. ASTEROID BELT", "VII. JUPITER", "VIII. SATURN",
              "IX. URANUS", "X. NEPTUNE"]

# Facts the panel states, each checked against the arithmetic it claims.
FACTS = [
    ("the belt is 1.2 au wide", abs((BELT_OUT - BELT_IN) - 1.2) < 1e-9),
    ("that is about 180 million km",
     abs((BELT_OUT - BELT_IN) * AU_KM / 1e6 - 180) < 4),
    ("the inner edge is 314 million km out",
     abs(BELT_IN * AU_KM / 1e6 - 314) < 1.5),
    ("the outer edge is 494 million km out",
     abs(BELT_OUT * AU_KM / 1e6 - 494) < 1.5),
    ("2.4e21 kg is about 3% of the Moon",
     2.5 < 2.4e21 / 7.342e22 * 100 < 3.5),
    ("2.4e21 kg is about 0.04% of Earth",
     0.035 < 2.4e21 / 5.972e24 * 100 < 0.045),
    ("Ceres holds roughly a third of the belt",
     0.30 < 9.38e20 / 2.4e21 < 0.42),
    ("Ceres at 2.77 au falls inside the belt", BELT_IN < 2.77 < BELT_OUT),
    ("every Kirkwood gap quoted falls inside the belt",
     all(BELT_IN < g < BELT_OUT for g in (2.50, 2.82, 2.95, 3.28))),
    ("the 3:1 gap sits where Jupiter's period beats three to one",
     abs(5.204 * (1 / 3) ** (2 / 3) - 2.50) < 0.02),
    ("the 2:1 gap likewise", abs(5.204 * (1 / 2) ** (2 / 3) - 3.28) < 0.02),
    ("the belt lies between Mars and Jupiter",
     MARS_AU < BELT_IN and BELT_OUT < JUPITER_AU),
]

fails = []
print("--- the arithmetic behind the panel ---")
for claim, ok in FACTS:
    print(f"  {'ok  ' if ok else 'FAIL'} {claim}")
    if not ok:
        fails.append(claim)

html = PAGE.read_text(encoding="utf-8")
if "—" in html.split("<script>")[0]:
    fails.append("an em dash in the page chrome")

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("\nplaywright not available, stopping after the arithmetic")
    sys.exit(1 if fails else 0)

print("--- the page ---")
with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1400, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.resolve().as_uri())
    pg.wait_for_timeout(900)

    chips = pg.eval_on_selector_all(".chip", "els=>els.map(e=>e.textContent.trim())")
    if chips != WANT_CHIPS:
        fails.append(f"the chips read {chips}")
    else:
        print(f"  ok   {len(chips)} chips, the belt is VI and Neptune is X")

    d = pg.evaluate("()=>window.__dbg")
    if abs(d["belt"]["auIn"] - BELT_IN) > 1e-9 or abs(d["belt"]["auOut"] - BELT_OUT) > 1e-9:
        fails.append(f"the belt claims {d['belt']['auIn']} to {d['belt']['auOut']} au")
    print(f"  ok   the belt runs {d['belt']['auIn']} to {d['belt']['auOut']} au, "
          f"{d['belt']['rocks']} rocks drawn")

    # lenient layout: the belt must sit strictly between Mars and Jupiter
    pos = pg.evaluate("""()=>{
      const out={};
      for (const c of document.querySelectorAll('.chip')) out[c.textContent.trim()]=1;
      return {lenIn: __dbg.belt.xIn, lenOut: __dbg.belt.xOut};
    }""")
    print(f"  ok   lenient edges at {pos['lenIn']:.0f} and {pos['lenOut']:.0f} u")

    # selecting the belt: the panel fills, the relabelled rows show, nothing throws
    pg.click('.chip[data-name="Asteroid Belt"]')
    pg.wait_for_timeout(1400)
    panel = pg.evaluate("""()=>({
      name: iName.textContent, type: iType.textContent,
      labels: [...document.querySelectorAll('#info dt')].map(t=>t.textContent),
      dist: iDist.textContent, mass: iMass.textContent,
      extraShown: getComputedStyle(rowExtra).display !== 'none',
      empty: [...document.querySelectorAll('#info dd')].filter(d=>
        !d.textContent.trim() && getComputedStyle(d).display !== 'none').length,
      sel: __dbg.sel, ex: __dbg.ex, er: __dbg.er })""")
    if panel["name"] != "Asteroid Belt":
        fails.append(f"the panel names it {panel['name']!r}")
    for want in ("Width of the belt", "Why there is no planet here",
                 "Largest members", "How empty it is"):
        if want not in panel["labels"]:
            fails.append(f"the panel has no {want!r} row")
    if panel["empty"]:
        fails.append(f"{panel['empty']} visible rows in the panel are blank")
    if panel["ex"] is not None or panel["er"] is not None:
        fails.append("the belt is being treated as a body with a radius")
    print(f"  ok   panel: {panel['name']}, {len(panel['labels'])} rows, "
          f"none blank, own labels in place")

    # The panel must stay inside the window whatever it is showing. Every entry
    # is checked: the belt's is the longest, but it is not the only risk.
    FIT_JS = """() => {
      const i = document.getElementById('info');
      const r = i.getBoundingClientRect();
      const c = document.getElementById('controls').getBoundingClientRect();
      return {bottom: r.bottom, h: window.innerHeight, barTop: c.top,
              overlapsBar: r.bottom > c.top && r.right > c.left && r.left < c.right,
              clipped: i.scrollHeight - i.clientHeight > 1,
              scrollable: getComputedStyle(i).overflowY === 'auto'};
    }"""
    # Checked at two window heights, since the failure only shows in the short one.
    for h in (900, 720):
        pg.set_viewport_size({"width": 1400, "height": h})
        pg.wait_for_timeout(300)
        for chip in WANT_CHIPS[1:]:
            pg.click(f'.chip:text-is("{chip}")')
            pg.wait_for_timeout(240)
            box = pg.evaluate(FIT_JS)
            if box["bottom"] > box["h"] + 1:
                fails.append(f"{chip} at {h}px: the panel runs "
                             f"{box['bottom'] - box['h']:.0f}px past the bottom")
            if box["overlapsBar"]:
                fails.append(f"{chip} at {h}px: the panel runs under the "
                             "control bar")
            if box["clipped"] and not box["scrollable"]:
                fails.append(f"{chip} at {h}px: the panel is cut off and "
                             "cannot be scrolled")
        print(f"  ok   at {h}px tall the panel clears the control bar for all "
              f"{len(WANT_CHIPS) - 1} entries")
    pg.set_viewport_size({"width": 1400, "height": 900})
    pg.wait_for_timeout(300)

    # a body selected after the belt must restore the standard labels
    pg.click('.chip[data-name="Asteroid Belt"]')
    pg.wait_for_timeout(400)
    pg.click('.chip[data-name="Mars"]')
    pg.wait_for_timeout(1200)
    back = pg.evaluate("""()=>({
      labels: [...document.querySelectorAll('#info dt')].map(t=>t.textContent),
      extraShown: getComputedStyle(rowExtra).display !== 'none',
      name: iName.textContent })""")
    for want in ("Diameter", "Surface area", "Moons"):
        if want not in back["labels"]:
            fails.append(f"after Mars the {want!r} label did not come back")
    if back["extraShown"]:
        fails.append("the belt's extra row is still showing on Mars")
    print(f"  ok   {back['name']} restores the standard labels and hides the extra row")

    # true scale: the belt must land at its real distance
    pg.click("#scaleBtn")
    pg.wait_for_timeout(2500)
    t = pg.evaluate("()=>({m:__dbg.m, b:__dbg.belt})")
    ratio_in = t["b"]["trueIn"] / t["b"]["trueOut"]
    if abs(ratio_in - BELT_IN / BELT_OUT) > 1e-6:
        fails.append("at true scale the belt edges are not in the right ratio")
    print(f"  ok   true scale: edges in the ratio {ratio_in:.4f}, "
          f"against {BELT_IN / BELT_OUT:.4f} from the au figures")

    if errs:
        fails.append(f"javascript errors: {errs}")
    br.close()

print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("all checks pass")
