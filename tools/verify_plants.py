"""Check plants.html against its data and its drawing.

  the data     six parts, each with a story, a number and a source; the
               chlorophyll peaks at the measured maxima, and the curves
               drawn from them peak there and dip in the green; the
               photosynthesis figures (2,870 kJ, 104.9 Pg with land and sea
               adding up); the kinds in order of appearance, flowering
               plants nine tenths of species
  the drawing  six parts answer; the marker drags along the spectrum and
               the card reads the absorption there; the equation answers;
               the kinds' bars stand at their dates with heights on the log
               scale; no label overlaps another
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from plants_data import PARTS, CHLOROPHYLL, PHOTO, KINDS

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "plants.html"
fails = []


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


def absorb(k, nm):
    return sum(h * math.exp(-0.5 * ((nm - mu) / s) ** 2) for mu, s, h in CHLOROPHYLL[k]["peaks"])


print("--- the data ---")
check(len(PARTS) == 6 and all(p[1] and p[2] and p[3] and p[4] for p in PARTS), "six parts, each with a story, a number and a source")
check([p[0] for p, _ in [(CHLOROPHYLL["a"]["peaks"][0], 0), (CHLOROPHYLL["a"]["peaks"][1], 0)]] == [430, 662] and [p[0] for p in CHLOROPHYLL["b"]["peaks"]] == [453, 642],
      "chlorophyll a peaks at 430 and 662 nm, b at 453 and 642")
grid = range(380, 751)
pk_a = max(grid, key=lambda nm: absorb("a", nm))
check(pk_a == 430 and absorb("a", 662) > absorb("a", 600) and absorb("a", 550) < 0.02, f"the drawn a curve peaks at {pk_a} nm and is near zero at 550")
check(absorb("a", 662) > absorb("b", 642) and absorb("b", 453) < absorb("a", 430), "a is the stronger pigment at both ends, as in the published spectra")
check(all(absorb("a", nm) + absorb("b", nm) < 0.1 for nm in range(520, 580)), "both curves are below a tenth of their peaks across the green")
check(PHOTO["energy_kj"] == 2870 and abs(PHOTO["npp_land"] + PHOTO["npp_ocean"] - PHOTO["npp_pg"]) < 0.05, "2,870 kJ a mole; land and sea production add up to 104.9")
check([k[3] for k in KINDS] == sorted([k[3] for k in KINDS], reverse=True), "the kinds are in order of appearance")
tot = sum(k[2] for k in KINDS)
fl = next(k for k in KINDS if k[0] == "flower")
check(0.88 < fl[2] / tot < 0.95, f"flowering plants are {fl[2] / tot * 100:.0f}% of species")
check(all(k[3] < 500 and k[3] > 100 for k in KINDS), "every kind appeared between 500 and 100 million years ago")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1000})
    errs = []
    pg.on("pageerror", lambda x: errs.append(str(x)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#psvg")

    def st(q=None):
        return pg.evaluate("(q)=>window.__plants(q)", q)

    s = st()
    check(s["view"] == "parts" and s["parts"] == 6, "opens on the plant with six parts")
    for k, nm, word in [("root", "the roots", "10,000 km"), ("leaf", "the leaf", "square millimeter"), ("flower", "the flower", "nine tenths"), ("chloroplast", "the chloroplasts", "tens to a hundred")]:
        pg.evaluate(f"()=>document.querySelector('#psvg g[data-part=\"{k}\"]').dispatchEvent(new PointerEvent('pointerover',{{bubbles:true}}))")
        pg.wait_for_timeout(80)
        s = st()
        check(s["name"] == nm and word in s["card"], f"hovering {nm}: {word}")
    pg.click('#views button[data-v="light"]')
    pg.wait_for_timeout(150)
    s = st({"nm": 550})
    check(s["view"] == "light" and s["lam"] == 550 and "0% of its strongest" in s["card"] and "looks green" in s["card"], "the light view opens at 550 nm: nothing absorbed, and the reason leaves look green")
    check(abs(s["abs"][0] - absorb("a", 550)) < 1e-9, "the page's absorption agrees with this checker")
    L = {"x": 80, "w": 820, "a": 380, "b": 750}
    LX = lambda nm: L["x"] + (nm - L["a"]) / (L["b"] - L["a"]) * L["w"]
    box = pg.eval_on_selector("#psvg", "e=>{const r=e.getBoundingClientRect(); return {x:r.left,y:r.top,w:r.width,h:r.height,vh:e.viewBox.baseVal.height}}")
    sx = lambda px: box["x"] + px / 980 * box["w"]
    sy = lambda py: box["y"] + py / box["vh"] * box["h"]
    pg.mouse.move(sx(LX(500)), sy(200))
    pg.mouse.down()
    pg.mouse.move(sx(LX(662)), sy(200), steps=4)
    pg.mouse.up()
    pg.wait_for_timeout(100)
    s = st()
    check(abs(s["lam"] - 662) <= 1 and abs(s["marker"] - LX(s["lam"])) < 0.6 and "red" in s["name"] and ("80% of its strongest" in s["card"] or "79% of its strongest" in s["card"]), f"dragging to the red peak: {s['lam']} nm, chlorophyll a at 80% of its blue peak, the card says red")
    pg.evaluate("()=>document.querySelector('#psvg g[data-photo]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(80)
    s = st()
    check("2,870 kJ" in s["card"] and "104.9 billion metric tons" in s["card"] and "CO" in s["name"], "the equation's card: 2,870 kJ, 104.9 billion metric tons a year")
    pg.click('#views button[data-v="kinds"]')
    pg.wait_for_timeout(150)
    s = st()
    check(s["kinds"] == 4 and "402,100" in s["card"] and "92% of them" in s["card"], "the kinds view: four bars, 402,100 species, 92% flowering")
    bars = pg.evaluate("()=>[...document.querySelectorAll('#psvg g[data-kind] rect')].map(r=>[+r.getAttribute('x')+22, +r.getAttribute('height')])")
    TX = lambda ma: 90 + (500 - ma) / 500 * 810
    maxsp = max(k[2] for k in KINDS)
    ok = all(abs(b[0] - TX(k[3])) < 0.6 and abs(b[1] - math.log10(k[2]) / math.log10(maxsp) * 240) < 0.6 for b, k in zip(bars, KINDS))
    check(ok, "each bar stands at its date with its height on the log scale")
    boxes = pg.evaluate("()=>[...document.querySelectorAll('#psvg g[data-kind] text')].map(t=>{const b=t.getBBox(); return [b.x,b.y,b.width,b.height]})")
    clash = sum(1 for i in range(len(boxes)) for j in range(i + 1, len(boxes)) if boxes[i][0] < boxes[j][0] + boxes[j][2] and boxes[j][0] < boxes[i][0] + boxes[i][2] and boxes[i][1] < boxes[j][1] + boxes[j][3] and boxes[j][1] < boxes[i][1] + boxes[i][3])
    check(clash == 0, "no two labels overlap", f"{clash}")
    pg.evaluate("()=>document.querySelector('#psvg g[data-kind=\"conifer\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(80)
    s = st()
    check("conifers" in s["name"] and "1,100" in s["card"] and "385 million" in s["card"], "hovering the conifers: 1,100 species, 385 million years")
    check(not errs, "no script errors", "; ".join(errs))

    # the sunlight: water slows with the light, sugar keeps moving, and the card says why
    pa = br.new_page(viewport={"width": 1300, "height": 850})
    pa.on("pageerror", lambda x: errs.append(str(x)))
    pa.goto(PAGE.as_uri()); pa.wait_for_selector("#psvg")
    def speeds():
        a0 = pa.evaluate("()=>window.__plants()"); pa.wait_for_timeout(500); a1 = pa.evaluate("()=>window.__plants()")
        return (a1["xPh"] - a0["xPh"]) % 1, (a1["pPh"] - a0["pPh"]) % 1
    day = speeds()
    pa.evaluate("()=>{const s=document.getElementById('sun'); s.value=0; s.dispatchEvent(new Event('input'));}")
    night = speeds()
    rd, rn = day[0] / day[1], night[0] / night[1]
    check(rd > 1.2 and rn < 0.35 and night[1] > 0.1 and "Night" in pa.inner_text("#nameTxt") and "starch" in pa.inner_text("#numTxt"),
          f"at night the water slows against the sugar ({rd:.2f} to {rn:.2f} times its pace) and the sugar keeps moving, from starch")
    check("respiration" in pa.evaluate("()=>document.getElementById('psvg').textContent"), "and the gas labels turn to respiration")
    # through a leaf: a second strip, dark at the chlorophyll peaks, bright in the green
    pa.click('#views button[data-v="light"]'); pa.click("#leafBtn"); pa.wait_for_timeout(1000)
    t = {nm: pa.evaluate(f"()=>window.__plants({{nm:{nm}}}).trans") for nm in (430, 550, 662)}
    check(pa.evaluate("()=>window.__plants().leaf") == 1 and t[430] < 0.15 and t[550] > 0.95 and t[662] < 0.45,
          f"through a leaf: the lower strip passes {t[550]:.2f} at 550 nm, {t[430]:.2f} at 430 and {t[662]:.2f} at 662")
    # the arrivals: a line of time sweeps and the bars rise as it passes, then all stand
    pa.click('#views button[data-v="kinds"]'); pa.click("#growBtn"); pa.wait_for_timeout(1800)
    mid = pa.evaluate("()=>({g:window.__plants().grow, run:window.__plants().growing, bars:[...document.querySelectorAll('#psvg g[data-kind] rect')].length, btn:document.getElementById('growBtn').textContent})")
    check(mid["run"] and 200 < mid["g"] < 470 and 0 < mid["bars"] < 4 and mid["btn"] == "Pause",
          f"Play the arrivals sweeps the line ({mid['g']:.0f} Ma) with only the kinds already arrived standing ({mid['bars']})")
    pa.wait_for_timeout(4200)
    check(pa.evaluate("()=>window.__plants().grow") is None and pa.evaluate("()=>document.querySelectorAll('#psvg g[data-kind] rect').length") == 4,
          "and it stops at today with all four standing")
    check(pa.evaluate("()=>{const d=document.querySelector('details.sources'); return !!d && !d.open && !!d.querySelector('.refs');}"),
          "the notes and references sit inside a closed Sources")
    pa.set_viewport_size({"width": 390, "height": 844}); pa.wait_for_timeout(150)
    check(pa.evaluate("()=>document.documentElement.scrollWidth - innerWidth") == 0, "nothing overflows a 390px screen")
    check(not errs, "no script errors in the new controls", "; ".join(errs))
    br.close()

print("--- the copy ---")
html = PAGE.read_text()
check("—" not in html, "no em dashes")

print()
if fails:
    print(f"{len(fails)} FAILED:")
    for x in fails:
        print("  -", x)
    sys.exit(1)
print("everything squares")
