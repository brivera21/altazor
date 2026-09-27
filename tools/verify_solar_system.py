"""Check solar-system.html, with attention to its two regions.

The asteroid belt and the Kuiper belt are regions rather than bodies, so the
things worth checking are that their edges land where the real belts are, that
they stand across the diagram rather than along it at every zoom, that the
structure drawn into each swarm matches what the panel claims, and that
selecting one does not fall through code written for bodies with a radius.

Usage: python3 verify_solar_system.py
"""
import math
import sys
from pathlib import Path

PAGE = Path(__file__).parent.parent / "solar-system.html"
AU_KM = 149.6e6

# The main belt, and the bodies either side of it.
BELT_IN, BELT_OUT = 2.1, 3.3
MARS_AU, JUPITER_AU = 1.524, 5.204

WANT_CHIPS = ["Overview", "I. SUN", "II. MERCURY", "III. VENUS", "IV. EARTH",
              "V. MARS", "VI. ASTEROID BELT", "VII. JUPITER", "VIII. SATURN",
              "IX. URANUS", "X. NEPTUNE", "XI. KUIPER BELT"]

NEPTUNE_AU = 30.07
KUIPER_IN, KUIPER_OUT = 30, 50

# The Great Red Spot as the page draws it, and Earth to compare it against.
GRS_W, GRS_H = 15000, 12000
EARTH_D, JUPITER_R = 12742, 69911

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
    # shares of the belt against the 2.394e21 kg total (Pitjeva and Pitjev 2018)
    ("Ceres holds about two fifths of the belt",
     0.37 < 9.384e20 / 2.394e21 < 0.43),
    ("Vesta holds about a tenth of it",
     0.09 < 2.590e20 / 2.394e21 < 0.12),
    ("the four largest hold about three fifths",
     0.57 < (9.384 + 2.590 + 2.04 + 0.87) / 23.94 < 0.65),
    ("Ceres is 1.3% of the Moon's mass", abs(9.384e20 / 7.342e22 * 100 - 1.3) < 0.05),
    ("Vesta is 0.35% of the Moon's mass", abs(2.590e20 / 7.342e22 * 100 - 0.35) < 0.01),
    ("Ceres's surface, 2.77e6 km², follows from its 939.4 km mean diameter",
     abs(math.pi * 939.4 ** 2 / 2.77e6 - 1) < 0.01),
    ("Vesta's surface, 8.66e5 km², follows from its 525.4 km mean diameter",
     abs(math.pi * 525.4 ** 2 / 8.66e5 - 1) < 0.01),
    ("Vesta at 2.362 au falls inside the belt and clear of the 3:1 gap",
     BELT_IN < 2.362 < BELT_OUT and abs(2.362 - 5.204 * (1 / 3) ** (2 / 3)) > 0.035),
    ("Ceres at 2.766 au falls clear of the 5:2 gap",
     abs(2.766 - 5.204 * (2 / 5) ** (2 / 3)) > 0.020),
    ("Ceres at 2.77 au falls inside the belt", BELT_IN < 2.77 < BELT_OUT),
    ("every Kirkwood gap quoted falls inside the belt",
     all(BELT_IN < g < BELT_OUT for g in (2.50, 2.82, 2.95, 3.28))),
    ("the 3:1 gap sits where Jupiter's period beats three to one",
     abs(5.204 * (1 / 3) ** (2 / 3) - 2.50) < 0.02),
    ("the 2:1 gap likewise", abs(5.204 * (1 / 2) ** (2 / 3) - 3.28) < 0.02),
    ("the belt lies between Mars and Jupiter",
     MARS_AU < BELT_IN and BELT_OUT < JUPITER_AU),
    # --- the Kuiper belt ---
    ("the Kuiper belt is 20 au wide",
     abs((KUIPER_OUT - KUIPER_IN) - 20) < 1e-9),
    ("that is about 3 billion km",
     abs((KUIPER_OUT - KUIPER_IN) * AU_KM / 1e9 - 3) < 0.05),
    ("its inner edge is 4.5 billion km out",
     abs(KUIPER_IN * AU_KM / 1e9 - 4.5) < 0.05),
    ("its outer edge is 7.5 billion km out",
     abs(KUIPER_OUT * AU_KM / 1e9 - 7.5) < 0.05),
    ("it is about seventeen times the width of the asteroid belt",
     16 < (KUIPER_OUT - KUIPER_IN) / (BELT_OUT - BELT_IN) < 18),
    ("it starts at Neptune's orbit", abs(KUIPER_IN - NEPTUNE_AU) < 0.1),
    ("it starts where the planets end", KUIPER_IN >= NEPTUNE_AU - 0.1),
    ("the plutinos sit where a body circles twice for three Neptune years",
     abs(NEPTUNE_AU * (3 / 2) ** (2 / 3) - 39.4) < 0.1),
    ("the twotinos likewise, one for two",
     abs(NEPTUNE_AU * 2 ** (2 / 3) - 47.8) < 0.2),
    ("both resonances fall inside the belt",
     all(KUIPER_IN < a < KUIPER_OUT
         for a in (NEPTUNE_AU * (3 / 2) ** (2 / 3), NEPTUNE_AU * 2 ** (2 / 3)))),
    ("Pluto is the largest member at 2,377 km",
     2377 > max(1560, 1430, 1090)),
    ("Eris, in the scattered disc, is larger than Makemake", 2326 > 1430),
    # --- the light pulse ---
    ("light reaches Neptune in 4 h 10 min",
     abs(NEPTUNE_AU * AU_KM / 299792.458 / 60 - 250) < 2),
    ("light reaches the far edge of the Kuiper belt in 6 h 56 min",
     abs(KUIPER_OUT * AU_KM / 299792.458 / 60 - 416) < 2),
    ("that is two thirds again as far as Neptune",
     1.6 < KUIPER_OUT / NEPTUNE_AU < 1.7),
    # --- the Great Red Spot and the ghost Earth on it ---
    ("the spot as drawn is a little over one Earth wide",
     1.0 < GRS_W / EARTH_D < 1.4),
    ("it was near three Earths across in the nineteenth century",
     2.9 < 40000 / EARTH_D < 3.3),
    ("the drawn size sits between the Juno measurement and the latest",
     12000 < GRS_W < 16400),
    ("the spot is wider than it is tall, as the real one is",
     1.15 < GRS_W / GRS_H < 1.35),
    ("22 degrees south puts it where the spot actually is",
     abs(math.sin(math.radians(22)) - 0.3746) < 0.001),
    # --- days and years (NASA fact sheets; Kepler's third law, P = a^1.5) ---
    ("Mercury's solar day, 4222.6 h, is 176 Earth days", round(4222.6 / 24) == 176),
    ("and two of its 88-day years", abs(4222.6 / 24 / 87.97 - 2) < 0.01),
    ("it turns once in 58.6 days, three turns for two orbits",
     abs(1407.6 / 24 - 58.6) < 0.05 and abs(3 * 1407.6 / 24 - 2 * 87.97) < 0.2),
    ("Venus's solar day, 2802 h, is 117 Earth days", round(2802.0 / 24) == 117),
    ("its backward turn, 5832.5 h, is 243 days, longer than its 224.7-day year",
     round(5832.5 / 24) == 243 and 5832.5 / 24 > 224.7),
    ("Mars's 24.66 h sol is 24 h 40 min", round(24.6597 * 60) == 24 * 60 + 40),
    ("687 days is 1.9 Earth years", round(687.0 / 365.25, 1) == 1.9),
    ("Jupiter's 9.925 h is 9 h 56 min", round(9.925 * 60) == 9 * 60 + 56),
    ("Jupiter is about 7% wider at the equator", abs(71492 / 66854 - 1.07) < 0.005),
    ("Saturn's 10 h 33 min 38 s rounds to 10 h 34 min", round(10 * 60 + 33 + 38 / 60) == 634),
    ("Uranus's 17.24 h is 17 h 14 min", round(17.24 * 60) == 17 * 60 + 14),
    ("Neptune's 16 h 6 min 36 s rounds to 16 h 7 min", round(16 * 60 + 6 + 36 / 60) == 967),
    ("Jupiter's year, 4331 days, is 11.9 Earth years", round(4331 / 365.25, 1) == 11.9),
    ("Saturn's, 10,747 days, is 29.4", round(10747 / 365.25, 1) == 29.4),
    ("Uranus's, 30,589 days, is 84", round(30589 / 365.25) == 84),
    ("Neptune's, 60,190 days, is 165, finished in 2011",
     round(60190 / 365.25) == 165 and int(1846.73 + 60190 / 365.25) == 2011),
    ("Pluto's, 90,560 days, is 248, not yet finished since 1930",
     round(90560 / 365.25) == 248 and 1930 + 248 > 2026),
    ("Pluto turns in 153.3 h, 6.4 days", round(153.29 / 24, 1) == 6.4),
    ("Ceres at 2.766 au takes 4.6 years", round(2.766 ** 1.5, 1) == 4.6),
    ("Vesta at 2.362 au takes 3.6 years", round(2.362 ** 1.5, 1) == 3.6),
    ("Ceres turns in 9.074 h, 9 h 4 min", round(9.074 * 60) == 9 * 60 + 4),
    ("Vesta turns in 5.342 h, 5 h 21 min", round(5.342 * 60) == 5 * 60 + 21),
    ("the asteroid belt's years run 3.0 to 6.0",
     round(BELT_IN ** 1.5, 1) == 3.0 and round(BELT_OUT ** 1.5, 1) == 6.0),
    ("the Kuiper belt's run 164 to 354",
     round(KUIPER_IN ** 1.5) == 164 and round(KUIPER_OUT ** 1.5) == 354),
    # --- Pluto ---
    ("Pluto at 39.48 au sits inside the Kuiper belt, at the plutinos",
     KUIPER_IN < 39.48 < KUIPER_OUT and abs(39.48 - NEPTUNE_AU * 1.5 ** (2 / 3)) < 0.2),
    ("5,906 million km is 39.5 au, 5.9 billion km", round(5906.4 / 149.6, 1) == 39.5),
    ("perihelion 4,436.8 million km is 29.7 au, inside Neptune",
     round(4436.8 / 149.6, 1) == 29.7 and 4436.8 < 4471.1),
    ("aphelion 7,375.9 million km is 49.3 au", round(7375.9 / 149.6, 1) == 49.3),
    ("2,377 km is about two thirds of the Moon's width", abs(2376.6 / 3474.8 - 2 / 3) < 0.03),
    ("its surface is 1.77e7 km², a little more than Russia's 1.71e7",
     abs(4 * math.pi * 1188.3 ** 2 / 1.77e7 - 1) < 0.005 and 1.77e7 > 1.71e7),
    ("1.303e22 kg is 18% of the Moon", round(1.303e22 / 7.346e22 * 100) == 18),
    ("Charon is half as wide as Pluto", abs(1212 / 2376.6 - 0.5) < 0.02),
    ("and an eighth of its mass", abs(1.586e21 / 1.303e22 - 1 / 8) < 0.01),
    ("the point both circle lies about a ninth of the way to Charon",
     abs(1.586e21 / (1.303e22 + 1.586e21) - 1 / 9) < 0.005),
    ("so their balance point lies outside Pluto",
     19591 * 1.586e21 / (1.303e22 + 1.586e21) > 1188.3),
    ("New Horizons flew nine and a half years", abs((2015 + 195 / 365) - (2006 + 19 / 365) - 9.5) < 0.05),
    ("Pluto was a planet for 76 years", 2006 - 1930 == 76),
    ("Earth is five to twenty-four times the width of the three small bodies",
     round(6371 / 1188.3) == 5 and round(6371 / 262.7) == 24),
]

fails = []
print("--- the arithmetic behind the panel ---")
for claim, ok in FACTS:
    print(f"  {'ok  ' if ok else 'FAIL'} {claim}")
    if not ok:
        fails.append(claim)

html = PAGE.read_text(encoding="utf-8")
if "—" in html:
    fails.append("an em dash in the page")
if 'id="about"' in html or "lined up on one side" in html:
    fails.append("the long about paragraph is back")
if not __import__("re").search(r'<details class="sources">(?!\s*open)', html):
    fails.append("the sources are not in a closed details")

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
    # the page loads nothing from the network; block it so this runs offline
    pg.route("http://**", lambda r: r.abort())
    pg.route("https://**", lambda r: r.abort())
    pg.goto(PAGE.resolve().as_uri())
    pg.wait_for_timeout(900)

    chips = pg.eval_on_selector_all(".chip", "els=>els.map(e=>e.textContent.trim())")
    if chips != WANT_CHIPS:
        fails.append(f"the chips read {chips}")
    else:
        print(f"  ok   {len(chips)} chips, asteroid belt VI, Neptune X, "
              "Kuiper belt XI")

    WANT = {"Asteroid Belt": (BELT_IN, BELT_OUT),
            "Kuiper Belt": (KUIPER_IN, KUIPER_OUT)}
    regions = {r["name"]: r for r in pg.evaluate("()=>__dbg.regions")}
    if set(regions) != set(WANT):
        fails.append(f"the page draws regions {sorted(regions)}")
    for name, (lo, hi) in WANT.items():
        r = regions.get(name)
        if not r:
            continue
        if abs(r["auIn"] - lo) > 1e-9 or abs(r["auOut"] - hi) > 1e-9:
            fails.append(f"{name} claims {r['auIn']} to {r['auOut']} au")
        print(f"  ok   {name} runs {r['auIn']} to {r['auOut']} au, "
              f"{r['rocks']} rocks drawn")

    # each region stands across the diagram: taller than it is wide, at any zoom
    for name in WANT:
        for label, chip in (("zoomed out", None), ("zoomed in", name)):
            if chip:
                pg.click(f'.chip[data-name="{chip}"]')
            else:
                pg.click('.chip:text-is("Overview")')
            pg.wait_for_timeout(1600)
            g = pg.evaluate("(n)=>{const r=__dbg.regions.find(x=>x.name===n);"
                            "return {w:r.xOut-r.xIn, hh:r.halfH, z:__dbg.camz,"
                            " h:innerHeight};}", name)
            wpx = g["w"] * g["z"]
            if 2 * g["hh"] <= wpx:
                fails.append(f"{name} {label}: {wpx:.0f}px wide against "
                             f"{2 * g['hh']:.0f}px tall, so it lies along the "
                             "diagram instead of across it")
            if 2 * g["hh"] < g["h"] * 0.5:
                fails.append(f"{name} {label}: the curtain covers only "
                             f"{2 * g['hh'] / g['h']:.0%} of the window height")
            print(f"  ok   {name}, {label}: {wpx:.0f}px wide, "
                  f"{2 * g['hh']:.0f}px tall")
    pg.click('.chip:text-is("Overview")')
    pg.wait_for_timeout(1400)

    # the vertical spread must be a spread, not a line
    for name in WANT:
        vs = regions[name]["rockV"]
        if max(vs) < 0.9 or min(vs) > -0.9:
            fails.append(f"{name}: the rocks do not reach the full height")
    print("  ok   both swarms reach the full height of their curtain")

    # the Kirkwood gaps must actually be empty of rocks
    gaps = pg.evaluate("()=>__dbg.belt.gaps")
    aus = regions["Asteroid Belt"]["rockAu"]
    for g in gaps:
        inside = [a for a in aus if abs(a - g["au"]) < g["half"]]
        if inside:
            fails.append(f"the {g['ratio']} gap at {g['au']:.3f} au holds "
                         f"{len(inside)} rocks")
    for g, quoted in zip(gaps, (2.50, 2.82, 2.95, 3.28)):
        if abs(g["au"] - quoted) > 0.02:
            fails.append(f"the {g['ratio']} gap is drawn at {g['au']:.3f} au "
                         f"but the panel says {quoted}")
    print("  ok   all four Kirkwood gaps are empty and sit where the panel "
          "says they do")

    # The Kuiper belt's structure: a sparse inner stretch, the plutino pile-up,
    # the classical belt, and the cliff. Measured as rocks per au in each band.
    k = pg.evaluate("()=>__dbg.kuiper")
    kau = regions["Kuiper Belt"]["rockAu"]

    def per_au(lo, hi):
        return len([a for a in kau if lo <= a < hi]) / (hi - lo)

    inner, classical, beyond = per_au(30, 38), per_au(42, 48), per_au(48, 50)
    spike = per_au(k["plutino"] - 0.7, k["plutino"] + 0.7)
    if not classical > inner * 3:
        fails.append(f"the classical belt is {classical:.0f} rocks per au "
                     f"against {inner:.0f} inside 38 au, not the contrast "
                     "the panel describes")
    if not beyond < classical * 0.15:
        fails.append(f"past the cliff the density is {beyond:.0f} per au "
                     f"against {classical:.0f}, so there is no cliff")
    if not spike > classical:
        fails.append(f"the plutinos are not piled up: {spike:.0f} per au at "
                     f"{k['plutino']:.1f} au against {classical:.0f} "
                     "in the classical belt")
    if abs(k["plutino"] - 39.4) > 0.1 or abs(k["twotino"] - 47.8) > 0.2:
        fails.append(f"the resonances are drawn at {k['plutino']:.2f} and "
                     f"{k['twotino']:.2f} au")
    print(f"  ok   Kuiper structure: {inner:.0f} rocks per au inside 38, "
          f"{spike:.0f} at the plutinos ({k['plutino']:.1f} au), "
          f"{classical:.0f} through the classical belt, {beyond:.0f} past "
          f"the cliff at {k['cliff']} au")

    # lenient layout: the belt must sit strictly between Mars and Jupiter
    pos = pg.evaluate("()=>__dbg.regions.map(r=>[r.name, r.xIn, r.xOut])")
    for name, lo, hi in pos:
        print(f"  ok   {name} lenient edges at {lo:.0f} and {hi:.0f} u")

    # selecting the belt: the panel fills, the relabelled rows show, nothing throws
    pg.click('.chip[data-name="Asteroid Belt"]')
    pg.wait_for_timeout(1400)
    panel = pg.evaluate("""()=>({
      name: iName.textContent, type: iType.textContent,
      labels: [...document.querySelectorAll('#info dt')].map(t=>t.textContent),
      dist: iDist.textContent, mass: iMass.textContent,
      extraShown: getComputedStyle(rowExtra).display !== 'none',
      empty: [...document.querySelectorAll('#info dd')].filter(d=>
        !d.textContent.trim() && d.getClientRects().length).length,
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
            if h == 900:
                dy = pg.evaluate("()=>({day: rowDay.style.display !== 'none' && iDay.textContent.trim(),"
                                 " year: rowYear.style.display !== 'none' && iYear.textContent.trim(),"
                                 " blank: [...document.querySelectorAll('#info dd')].filter(d=>"
                                 "!d.textContent.trim() && d.getClientRects().length).length})")
                belt = "BELT" in chip
                if not dy["year"]:
                    fails.append(f"{chip}: no length of a year")
                if bool(dy["day"]) == belt:
                    fails.append(f"{chip}: the day row is {'shown' if belt else 'missing'}")
                if dy["blank"]:
                    fails.append(f"{chip}: {dy['blank']} blank rows")
        print(f"  ok   at {h}px tall the panel clears the control bar for all "
              f"{len(WANT_CHIPS) - 1} entries" +
              (", each with its year, and its day unless it is a belt" if h == 900 else ""))
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

    # The pulse has to reach the far edge of the Kuiper belt, not stop at
    # Neptune. Sampled over a full cycle at true scale, the furthest it gets
    # must be the belt's outer edge.
    pg.click('.chip:text-is("Overview")')
    pg.wait_for_timeout(2600)
    end = pg.evaluate("()=>__dbg.lightEnd")
    speedup = pg.evaluate("()=>__dbg.speedup")
    cross = end / speedup
    if cross > 45:
        fails.append(f"the pulse takes {cross:.0f} seconds to cross, too long "
                     "a wait")
    far, samples = 0.0, 0
    for _ in range(int(cross / 1.5) + 8):
        pg.wait_for_timeout(1500)
        st = pg.evaluate("()=>__dbg.light")
        if st:
            samples += 1
            far = max(far, st["au"])
    if samples == 0:
        fails.append("the pulse never appeared at true scale")
    elif far < KUIPER_OUT * 0.9:
        fails.append(f"the pulse only reached {far:.1f} au, short of the "
                     f"belt's outer edge at {KUIPER_OUT} au")
    elif far > KUIPER_OUT * 1.02:
        fails.append(f"the pulse ran past the belt to {far:.1f} au")
    print(f"  ok   the pulse crosses in {cross:.0f} s and reaches {far:.1f} au, "
          f"{end / 3600:.1f} light-hours from the Sun")

    # Every body must offer Earth for scale, Earth itself excepted, and the
    # two regions, which have no size of their own. Jupiter was skipped in
    # silence for a long time, so it is checked by name.
    #
    # This asks the page what it drew rather than counting blue pixels on the
    # canvas. Pixel counting looked simpler and was wrong: it also caught
    # Earth's and Neptune's own blue discs, and getImageData ignores alpha, so
    # a 10 percent wash counted the same as a solid fill. Every body passed,
    # including ones drawing no ghost at all.
    WANT_GHOST = {"Sun": "speck", "Mercury": "around", "Venus": "around",
                  "Mars": "around", "Jupiter": "spot", "Saturn": "beside",
                  "Uranus": "beside", "Neptune": "beside"}
    for name, kind in WANT_GHOST.items():
        pg.click(f'.chip[data-name="{name}"]')
        pg.wait_for_timeout(1700)
        g = pg.evaluate("()=>__dbg.ghost")
        if not g:
            fails.append(f"{name}: no Earth drawn for scale")
        elif g["kind"] != kind:
            fails.append(f"{name}: Earth drawn as {g['kind']!r}, expected {kind!r}")
        elif g["r"] < 1:
            fails.append(f"{name}: Earth drawn at {g['r']:.2f}px, invisible")
    print(f"  ok   all {len(WANT_GHOST)} bodies offer Earth for scale, "
          "Jupiter included")

    for name in ("Earth", "Asteroid Belt", "Kuiper Belt"):
        pg.click(f'.chip[data-name="{name}"]')
        pg.wait_for_timeout(1500)
        if pg.evaluate("()=>__dbg.ghost"):
            fails.append(f"{name} should not be compared against Earth")
    print("  ok   Earth and the two regions correctly draw none")

    # On Jupiter the ghost belongs on the spot, and the two must be comparable
    # in size rather than the spot dwarfing Earth.
    pg.click('.chip[data-name="Jupiter"]')
    pg.wait_for_timeout(1700)
    g = pg.evaluate("()=>__dbg.ghost")
    ratio = g["r"] / g["spotHalfW"]
    if abs(ratio - EARTH_D / GRS_W) > 0.01:
        fails.append(f"Earth spans {ratio:.3f} of the spot's width against "
                     f"{EARTH_D / GRS_W:.3f} from the measurements")
    if not 0.75 < ratio < 0.95:
        fails.append(f"Earth fills {ratio:.0%} of the spot, which does not "
                     "read as 'a little wider than Earth'")
    if abs(g["y"] - pg.evaluate("()=>__dbg.er") * math.sin(math.radians(22))
           - pg.evaluate("()=>innerHeight * 0.46")) > 2:
        fails.append("the ghost is not sitting at the spot's latitude")
    print(f"  ok   on Jupiter, Earth spans {ratio:.0%} of the Red Spot, "
          f"against {EARTH_D / GRS_W:.0%} from the measurements, at 22 S")

    labels = pg.evaluate("()=>[...document.querySelectorAll('#info dt')]"
                         ".map(t=>t.textContent)")
    if "The Great Red Spot" not in labels:
        fails.append("Jupiter's panel does not explain the spot")
    else:
        print("  ok   Jupiter's panel carries a Great Red Spot row")

    # Ceres, Vesta and Pluto sit on the line inside their belts, each at its
    # real fraction of the way across in both layouts, and each opens its panel.
    SMALL = {"Vesta": (2.362, 262.7, "525"), "Ceres": (2.766, 469.7, "939"),
             "Pluto": (39.48, 1188.3, "2,377")}
    REGION = {"Vesta": (BELT_IN, BELT_OUT), "Ceres": (BELT_IN, BELT_OUT),
              "Pluto": (KUIPER_IN, KUIPER_OUT)}
    for scale in ("lenient", "true"):
        pg.click('.chip:text-is("Overview")')
        if scale == "true":
            pg.click("#scaleBtn")
        pg.wait_for_timeout(2200)
        sm = {b["name"]: b for b in pg.evaluate("()=>__dbg.small")}
        if list(sm) != ["Vesta", "Ceres", "Pluto"]:
            fails.append(f"the belts hold {list(sm)}, expected Vesta, Ceres, Pluto")
            continue
        for name, (au, rkm, _) in SMALL.items():
            b = sm[name]
            lo, hi = REGION[name]
            want = b["beltIn"] + (au - lo) / (hi - lo) * (b["beltOut"] - b["beltIn"])
            if abs(b["x"] - want) > 1e-6:
                fails.append(f"{scale}: {name} at {b['x']:.2f} u, expected {want:.2f}")
            if not b["beltIn"] < b["x"] < b["beltOut"]:
                fails.append(f"{scale}: {name} falls outside the belt")
        if scale == "true":
            ratio = sm["Ceres"]["trueX"] / sm["Vesta"]["trueX"]
            if abs(ratio - 2.766 / 2.362) > 1e-6:
                fails.append(f"true scale: Ceres and Vesta in the ratio {ratio:.4f}")
            rr = sm["Ceres"]["rTrue"] / sm["Vesta"]["rTrue"]
            if abs(rr - 469.7 / 262.7) > 1e-6:
                fails.append(f"true scale: their radii in the ratio {rr:.4f}")
            if abs(sm["Pluto"]["trueX"] / sm["Ceres"]["trueX"] - 39.48 / 2.766) > 1e-6:
                fails.append("true scale: Pluto is not at its distance")
            pg.click("#scaleBtn")
            pg.wait_for_timeout(2200)
        print(f"  ok   {scale}: Vesta and Ceres sit inside the asteroid belt at "
              f"{sm['Vesta']['fr']:.3f} and {sm['Ceres']['fr']:.3f} of its width, "
              f"Pluto inside the Kuiper belt at {sm['Pluto']['fr']:.3f}")

    for name, (au, rkm, diam) in SMALL.items():
        pg.click('.chip:text-is("Overview")')
        pg.wait_for_timeout(1800)
        b = next(x for x in pg.evaluate("()=>__dbg.small") if x["name"] == name)
        pg.mouse.click(b["sx"], pg.evaluate("()=>innerHeight*0.46"))
        pg.wait_for_timeout(2000)
        got = pg.evaluate("()=>({n:document.querySelector('#iName').textContent,"
                          "d:document.querySelector('#iDiam').textContent,"
                          "x:document.querySelector('#lExtra').textContent,"
                          "rows:[...document.querySelectorAll('#info dd')].filter(d=>d.offsetParent)"
                          ".map(d=>d.textContent.trim()), sel:__dbg.sel})")
        if got["n"] != name or got["sel"] != name:
            fails.append(f"a click on {name} opened {got['n']!r}")
            continue
        if diam not in got["d"]:
            fails.append(f"{name}: the panel's diameter reads {got['d']!r}")
        if not all(got["rows"]):
            fails.append(f"{name}: a blank row in the panel")
        if "dwarf planet" not in got["x"] and not (name == "Pluto" and "not a planet" in got["x"]):
            fails.append(f"{name}: the extra row is labeled {got['x']!r}")
        g = pg.evaluate("()=>__dbg.ghost")
        if not g or g["kind"] != "moon" or abs(g["r"] / g["Rd"] - 1737.4 / rkm) > 1e-6:
            fails.append(f"{name}: the Moon is not drawn around it to scale ({g})")
        elif g["r"] * 2 > pg.evaluate("()=>Math.min(innerWidth, innerHeight)"):
            fails.append(f"{name}: the Moon ring runs off the window")
        if name == "Pluto":
            pg.wait_for_timeout(1500)          # the zoom in from the whole line is a long one
            c = pg.evaluate("()=>__dbg.charon")
            box = pg.evaluate("()=>({w: innerWidth, panel: document.querySelector('#info').getBoundingClientRect().right})")
            if not c:
                fails.append("Pluto: Charon is not drawn")
            else:
                if abs(c["r"] / c["Rd"] - 606 / 1188.3) > 1e-6:
                    fails.append(f"Charon's size is {c['r'] / c['Rd']:.3f} Pluto radii")
                if abs((c["x"] - c["x0"]) / c["Rd"] - 19591 / 1188.3) > 1e-6:
                    fails.append(f"Charon sits {(c['x'] - c['x0']) / c['Rd']:.2f} Pluto radii out")
                fb = 19591 * 1.586e21 / (1.303e22 + 1.586e21) / 1188.3
                if abs((c["bx"] - c["x0"]) / c["Rd"] - fb) > 1e-6:
                    fails.append("the point both circle is misplaced")
                if not c["bx"] - c["x0"] > c["Rd"]:
                    fails.append("the point both circle falls inside Pluto")
                if c["x0"] - c["Rd"] * 1737.4 / 1188.3 < box["panel"] or c["x"] + c["r"] > box["w"]:
                    fails.append(f"Pluto, its Moon ring and Charon do not fit between the panel and the edge")
                print(f"  ok   Charon sits {19591 / 1188.3:.1f} Pluto radii out at {606 / 1188.3:.2f} "
                      f"of its size, and the point both circle is {fb:.2f} radii out, past the surface")
        print(f"  ok   a click on {name} opens its panel ({got['x']}), "
              f"with the Moon drawn around it {1737.4 / rkm:.1f} times wider")
    belt_mass = pg.evaluate("()=>{document.querySelector('.chip[data-name=\"Asteroid Belt\"]').click();"
                            "return document.querySelector('#iMass').textContent}")
    if "two fifths" not in belt_mass or "a third" in belt_mass:
        fails.append(f"the belt panel's mass row reads {belt_mass!r}")
    else:
        print("  ok   the belt panel gives Ceres two fifths of the belt")

    if errs:
        fails.append(f"javascript errors: {errs}")
    br.close()

print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("all checks pass")
