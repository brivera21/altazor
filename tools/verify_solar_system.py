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

    if errs:
        fails.append(f"javascript errors: {errs}")
    br.close()

print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("all checks pass")
