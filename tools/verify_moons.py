"""Check the moons panel on solar-system.html.

  the data     every named moon has a radius, an orbital distance, a
               discovery and a note; the list is ordered by distance; the
               named moons never outnumber the planet's recognized count;
               the sizes match the published figures
  the panel    it opens only on a planet with moons seen up close, closes on
               zooming back out, draws the planet and its moons on one scale,
               and puts each moon on the log distance strip where its own
               figure says it belongs
"""
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "solar-system.html"
fails = []


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg + (f" [{extra}]" if extra else ""))


# the published figures, entered again here from the NASA planetary satellite
# fact sheet so the page is checked against something other than itself
KNOWN_R = {"The Moon": 1737.4, "Phobos": 11.27, "Deimos": 6.2, "Io": 1821.6,
           "Europa": 1560.8, "Ganymede": 2634.1, "Callisto": 2410.3,
           "Titan": 2574.7, "Rhea": 763.8, "Iapetus": 734.5, "Dione": 561.4,
           "Tethys": 531.1, "Enceladus": 252.1, "Mimas": 198.2,
           "Triton": 1353.4, "Titania": 788.4, "Oberon": 761.4,
           "Umbriel": 584.7, "Ariel": 578.9, "Miranda": 235.8}
KNOWN_A = {"The Moon": 384400, "Phobos": 9376, "Deimos": 23463, "Io": 421800,
           "Ganymede": 1070400, "Callisto": 1882700, "Titan": 1221870,
           "Triton": 354759, "Iapetus": 3560840, "Phoebe": 12947780}

print("--- the data ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1400, "height": 950})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    # the page loads nothing from the network; block it so the check is offline
    pg.route("http://**", lambda r: r.abort())
    pg.route("https://**", lambda r: r.abort())
    pg.goto(PAGE.as_uri())
    pg.wait_for_timeout(450)
    check(not errs, "the page runs clean", "; ".join(errs))

    src = PAGE.read_text(encoding="utf-8")
    body = re.search(r"const MOONS = \{[\s\S]*?\n  \};", src)
    check(body is not None, "the page carries a moon table")
    # the table lives inside a module, so it is read out of the source
    ns = {}
    for m in re.finditer(r'(\w+): \[\n((?:\s+\{[\s\S]*?\},\n)+)\s*\]', body.group(0)):
        planet, rows = m.group(1), m.group(2)
        got = []
        for r in re.finditer(r'\{ n:"(.*?)", r:([\d.]+), a:(\d+), d:"(.*?)",\s*t:"(.*?)" \}',
                             rows, re.S):
            got.append({"n": r.group(1), "r": float(r.group(2)),
                        "a": int(r.group(3)), "d": r.group(4), "t": r.group(5)})
        ns[planet] = got
    check(set(ns) == {"Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"},
          f"six planets carry named moons: {sorted(ns)}")
    check("Mercury" not in ns and "Venus" not in ns,
          "and the two that have none are absent from the table")
    total = sum(len(v) for v in ns.values())
    check(total == 26, f"{total} named moons in all")

    for planet, ms in sorted(ns.items()):
        check(all(m["n"] and m["r"] > 0 and m["a"] > 0 and m["d"] and m["t"]
                  for m in ms), f"{planet}: every moon is complete")
        check(all(ms[i]["a"] > ms[i - 1]["a"] for i in range(1, len(ms))),
              f"{planet}: listed outward from the planet",
              str([m["a"] for m in ms]))

    # against the published figures
    worst, worstn = 0.0, None
    allm = {m["n"]: m for v in ns.values() for m in v}
    for n, r in KNOWN_R.items():
        check(n in allm, f"{n} is on the page")
        if n in allm:
            d = abs(allm[n]["r"] - r) / r
            if d > worst:
                worst, worstn = d, n
    check(worst < 1e-6, f"every mean radius matches the fact sheet "
                        f"(worst {worstn}, off by {worst:.2e})")
    worst, worstn = 0.0, None
    for n, a in KNOWN_A.items():
        if n in allm:
            d = abs(allm[n]["a"] - a) / a
            if d > worst:
                worst, worstn = d, n
    check(worst < 1e-6, f"and every orbital distance does too "
                        f"(worst {worstn}, off by {worst:.2e})")
    # Ganymede is the largest moon in the solar system, and the page says so
    big = max(allm.values(), key=lambda m: m["r"])
    check(big["n"] == "Ganymede", f"the largest moon listed is {big['n']}")
    check("larger than Mercury" in big["t"] or "wider than Mercury" in big["t"],
          "and its note says it outsizes Mercury")

    print("--- the panel ---")

    def open_on(name):
        pg.evaluate("(n)=>[...document.querySelectorAll('.chip')]"
                    ".find(c=>c.dataset.name===n).click()", name)
        pg.wait_for_timeout(1500)
        return pg.evaluate("()=>window.__dbg.moons")

    st = open_on("Mercury")
    check(st["open"] is False, "no panel on a planet without moons", str(st))
    st = open_on("Jupiter")
    check(st["open"] and st["of"] == "Jupiter",
          "the panel opens on Jupiter seen up close", str(st))
    rows = pg.evaluate("()=>[...document.querySelectorAll('.mrow b')].map(b=>b.textContent)")
    check(rows == [m["n"] for m in ns["Jupiter"]],
          f"and lists its named moons in order: {rows}")

    # the discs are drawn on one scale with the planet
    geo = pg.evaluate("""()=>{
      const svg=document.getElementById('mStripSvg');
      const cs=[...svg.querySelectorAll('circle')];
      const planet=cs[0];
      const ms=[...svg.querySelectorAll('g[data-moon] circle:first-child')];
      return {planet:+planet.getAttribute('r'),
              moons:ms.map(c=>+c.getAttribute('r'))};}""")
    jr = [m["r"] for m in ns["Jupiter"]]
    s0 = geo["planet"] / 69911
    worst = max(abs(geo["moons"][i] - jr[i] * s0) / (jr[i] * s0)
                for i in range(len(jr)) if jr[i] * s0 > 1)
    check(worst < 0.01,
          f"the planet and its moons share one scale (worst {worst * 100:.2f}% out)")
    check(abs(geo["planet"] / max(geo["moons"]) - 69911 / max(jr)) < 0.02,
          f"Jupiter is drawn {geo['planet'] / max(geo['moons']):.1f} times "
          f"Ganymede's radius, against {69911 / max(jr):.1f} in the figures")

    # the log distance strip puts each moon where its own figure says
    dots = pg.evaluate("""()=>[...document.querySelectorAll('#mOrbit g[data-moon] circle')]
      .map(c=>+c.getAttribute('cx'))""")
    ja = [m["a"] for m in ns["Jupiter"]]
    lo, hi = math.log10(69911), math.log10(max(ja) * 1.3)
    want = [6 + (math.log10(a) - lo) / (hi - lo) * (256 - 12) for a in ja]
    off = max(abs(dots[i] - want[i]) for i in range(len(ja)))
    check(off < 0.2, f"each moon sits at its own distance on the log strip "
                     f"(worst {off:.3f}px out)")

    # clicking a moon pins its note
    pg.click("#mList .mrow:nth-child(4)")
    pg.wait_for_timeout(120)
    st = pg.evaluate("()=>window.__dbg.moons")
    note = pg.evaluate("()=>document.querySelector('.mrow.on p').textContent")
    check(st["hi"] == 3 and "Mercury" in note,
          f"a moon clicked in the list opens its note: '{note[:50]}'")
    ring = pg.evaluate("""()=>[...document.querySelectorAll('#mStripSvg circle')]
      .filter(c=>c.getAttribute('stroke')==='#58a6ff').length""")
    check(ring == 1, "and rings it on the scale drawing")

    # zooming back out closes it again
    pg.evaluate("()=>{const c=document.getElementById('space');"
                "for(let i=0;i<40;i++) c.dispatchEvent(new WheelEvent('wheel',"
                "{deltaY:240,clientX:700,clientY:450,bubbles:true}));}")
    pg.wait_for_timeout(1200)
    st = pg.evaluate("()=>window.__dbg.moons")
    check(st["open"] is False, "and zooming back out closes it", str(st))

    # the panel takes the left column: clear of the title above it, of the
    # control bar below it, and of the panel on the other side
    open_on("Saturn")
    box = pg.evaluate("""()=>{const r=i=>document.getElementById(i).getBoundingClientRect();
      const m=r('moons');return {mt:m.top,mb:m.bottom,ml:m.left,mr:m.right,
        hb:r('hud').bottom, il:r('info').left, ct:r('controls').top, w:innerWidth};}""")
    check(box["ml"] < box["w"] / 2,
          f"the moons sit on the left ({box['ml']:.0f}px in, window {box['w']:.0f})")
    check(box["mt"] >= box["hb"] - 0.5,
          f"clear of the title above it ({box['mt']:.0f} against {box['hb']:.0f})")
    check(box["mr"] <= box["il"] + 0.5,
          f"clear of the panel on the right ({box['mr']:.0f} against {box['il']:.0f})")
    check(box["mb"] <= box["ct"] + 0.5,
          f"and stopping above the control bar ({box['mb']:.0f} against {box['ct']:.0f})")
    # at true scale the scale bar shares that corner, so the panel stops above it
    pg.click("#scaleBtn")
    pg.wait_for_timeout(1800)
    open_on("Saturn")
    box = pg.evaluate("""()=>{const r=i=>document.getElementById(i).getBoundingClientRect();
      const m=r('moons'), s=r('scalebar');
      return {mb:m.bottom, st:s.top, shown:getComputedStyle(
        document.getElementById('scalebar')).display};}""")
    check(box["shown"] != "none" and box["mb"] <= box["st"] + 0.5,
          f"at true scale it stops above the scale bar too "
          f"({box['mb']:.0f} against {box['st']:.0f})")
    pg.click("#scaleBtn")
    pg.wait_for_timeout(1500)
    # too narrow for two columns, it drops below the panel on the right
    pg.set_viewport_size({"width": 600, "height": 900})
    open_on("Saturn")
    box = pg.evaluate("""()=>{const r=i=>document.getElementById(i).getBoundingClientRect();
      const m=r('moons'), f=r('info');return {mt:m.top, ib:f.bottom};}""")
    check(box["mt"] >= box["ib"] - 0.5,
          f"on a narrow window it drops below that panel instead "
          f"({box['mt']:.0f} against {box['ib']:.0f})")
    pg.set_viewport_size({"width": 1400, "height": 950})
    pg.wait_for_timeout(400)

    check(not errs, "no script errors", "; ".join(errs))
    br.close()

print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("everything squares")
