"""Check the moons drawn on solar-system.html.

  the data     every named moon has a radius, an orbital distance, a
               discovery and a note; each planet's list runs outward; the
               figures match the NASA planetary satellite fact sheet
  the drawing  the moons appear beside a planet seen up close and only then,
               each at the planet's own drawn scale in both size and
               distance; the ones past the edge are listed there; the
               pointer over a moon names its finder; the panel of numbers
               sits on the left, under the title and above the control bar
"""
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
PLANET_R = {"Earth": 6371.0, "Mars": 3389.5, "Jupiter": 69911, "Saturn": 58232,
            "Uranus": 25362, "Neptune": 24622}

print("--- the data ---")
src = PAGE.read_text(encoding="utf-8")
body = re.search(r"const MOONS = \{[\s\S]*?\n  \};", src)
check(body is not None, "the page carries a moon table")
ns = {}
for m in re.finditer(r'(\w+): \[\n((?:\s+\{[\s\S]*?\},\n)+)\s*\]', body.group(0)):
    got = []
    for r in re.finditer(r'\{ n:"(.*?)", r:([\d.]+), a:(\d+), d:"(.*?)",\s*t:"(.*?)" \}',
                         m.group(2), re.S):
        got.append({"n": r.group(1), "r": float(r.group(2)), "a": int(r.group(3)),
                    "d": r.group(4), "t": r.group(5)})
    ns[m.group(1)] = got
check(set(ns) == set(PLANET_R), f"six planets carry named moons: {sorted(ns)}")
check(sum(len(v) for v in ns.values()) == 26,
      f"{sum(len(v) for v in ns.values())} named moons in all")
for planet, ms in sorted(ns.items()):
    check(all(mo["n"] and mo["r"] > 0 and mo["a"] > 0 and mo["d"] and mo["t"] for mo in ms),
          f"{planet}: every moon is complete")
    check(all(ms[i]["a"] > ms[i - 1]["a"] for i in range(1, len(ms))),
          f"{planet}: listed outward from the planet", str([mo["a"] for mo in ms]))
allm = {mo["n"]: mo for v in ns.values() for mo in v}
worst = max((abs(allm[n]["r"] - r) / r, n) for n, r in KNOWN_R.items() if n in allm)
check(all(n in allm for n in KNOWN_R) and worst[0] < 1e-6,
      f"every mean radius matches the fact sheet (worst {worst[1]}, off by {worst[0]:.1e})")
worst = max((abs(allm[n]["a"] - a) / a, n) for n, a in KNOWN_A.items() if n in allm)
check(worst[0] < 1e-6,
      f"and every orbital distance does too (worst {worst[1]}, off by {worst[0]:.1e})")
big = max(allm.values(), key=lambda mo: mo["r"])
check(big["n"] == "Ganymede" and "Mercury" in big["t"],
      f"the largest moon listed is {big['n']}, and its note says it outsizes Mercury")

print("--- the drawing ---")
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

    def open_on(name, wait=1600):
        pg.evaluate("(n)=>[...document.querySelectorAll('.chip')]"
                    ".find(c=>c.dataset.name===n).click()", name)
        pg.wait_for_timeout(wait)
        return pg.evaluate("()=>window.__dbg.moons")

    check(open_on("Mercury") is None, "nothing drawn beside a planet without moons")
    st = open_on("Jupiter")
    check(st and st["of"] == "Jupiter", "the moons appear beside Jupiter seen up close")
    names = [mo["n"] for mo in st["moons"]]
    check(names == [mo["n"] for mo in ns["Jupiter"]], f"all five, outward: {names}")

    def geometry_holds(st, planet):
        # size and distance both on the planet's own drawn scale
        s = st["Rd"] / PLANET_R[planet]
        worst = 0.0
        for mo, ref in zip(st["moons"], ns[planet]):
            want_x = st["x0"] + ref["a"] * s
            want_r = max(ref["r"] * s, 1.2)
            worst = max(worst, abs(mo["x"] - want_x) / max(1, ref["a"] * s),
                        abs(mo["r"] - want_r) / want_r)
        return abs(st["scale"] - s) / s < 1e-9 and worst < 1e-6, worst

    ok, worst = geometry_holds(st, "Jupiter")
    check(ok, f"each moon sits at its true distance and true size on that scale "
              f"(worst {worst:.1e} out)")
    io, cal = st["moons"][1], st["moons"][4]
    ratio = (cal["x"] - st["x0"]) / (io["x"] - st["x0"])
    check(abs(ratio - 1882700 / 421800) < 1e-6,
          f"Callisto sits {ratio:.3f} times as far out as Io, as the figures say")
    check(st["moons"][3]["r"] > st["moons"][1]["r"] > st["moons"][0]["r"],
          "Ganymede is drawn larger than Io, and Io larger than Amalthea")
    on_screen = [mo["n"] for mo in st["moons"] if mo["x"] - mo["r"] <= 1400 + 4]
    check(st["beyond"] == [n for n in names if n not in on_screen],
          f"the moons past the right edge are listed there: {st['beyond']}")
    check(st["ghosting"] is True,
          "on the lenient layout the neighbours step back while the moons show")

    # the pointer over a moon names its finder
    target = next(mo for mo in st["moons"] if 40 < mo["x"] < 1360)
    pg.mouse.move(target["x"], st["y0"])
    pg.wait_for_timeout(300)
    st2 = pg.evaluate("()=>window.__dbg.moons")
    check(st2["hover"] == names.index(target["n"]),
          f"the pointer over {target['n']} picks it out (hover {st2['hover']})")
    pg.mouse.move(700, 60)

    # pulled back far enough, the moons go and the neighbours return
    pg.evaluate("()=>{const c=document.getElementById('space');"
                "for(let i=0;i<12;i++) c.dispatchEvent(new WheelEvent('wheel',"
                "{deltaY:240,clientX:700,clientY:450,bubbles:true}));}")
    pg.wait_for_timeout(900)
    check(pg.evaluate("()=>window.__dbg.moons") is None,
          "zooming out past the close-up hides them again")

    # at true scale the same drawing needs no ghosting
    pg.click("#scaleBtn")
    pg.wait_for_timeout(1800)
    st = open_on("Saturn")
    ok, worst = geometry_holds(st, "Saturn")
    check(st and st["of"] == "Saturn" and ok,
          f"at true scale Saturn's nine hold the same geometry (worst {worst:.1e})")
    check(st["ghosting"] is False, "and nothing needs to step back there")
    check("Phoebe" in st["beyond"] and "Iapetus" in st["beyond"],
          f"Phoebe and Iapetus are off the edge and say so: {st['beyond']}")
    pg.click("#scaleBtn")
    pg.wait_for_timeout(1500)

    # the panel of numbers takes the left, under the title, above the bar
    open_on("Saturn")
    box = pg.evaluate("""()=>{const r=i=>document.getElementById(i).getBoundingClientRect();
      const f=r('info');return {l:f.left,t:f.top,b:f.bottom,hb:r('hud').bottom,
        ct:r('controls').top,w:innerWidth};}""")
    check(box["l"] < box["w"] / 2, f"the panel of numbers sits on the left ({box['l']:.0f}px in)")
    check(box["t"] >= box["hb"] - 0.5,
          f"under the title ({box['t']:.0f} against {box['hb']:.0f})")
    check(box["b"] <= box["ct"] + 0.5,
          f"and above the control bar ({box['b']:.0f} against {box['ct']:.0f})")
    check(not errs, "no script errors", "; ".join(errs))
    br.close()

print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("everything squares")
