"""Check brain.html against its data and its drawing.

  the data     twelve regions outside and thirteen inside, each with a
               story, a number and a source; the cell counts add up to the
               86 billion; the masses of the parts add to the whole; the
               masses by age rise to a peak near twenty and fall after,
               men above women throughout, a quarter of the peak at birth
               and nine tenths by three
  the drawing  every region is under the pointer where its label says it
               is; hovering gives its card; the marker drags along the
               years and the card reads the mass there; no label overlaps
               another; no script errors
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from brain_data import WHOLE, OUTSIDE, INSIDE, GROWTH

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "brain.html"
fails = []


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


print("--- the data ---")
check(len(OUTSIDE) == 12 and all(all(p) for p in OUTSIDE), "twelve regions outside, each with a story, a number and a source")
check(len(INSIDE) == 13 and all(all(p) for p in INSIDE), "thirteen regions inside, likewise")
check(len({p[0] for p in OUTSIDE}) == 12 and len({p[0] for p in INSIDE}) == 13, "no two regions share a key")
n = WHOLE["cortex_neurons"] + WHOLE["cerebellum_neurons"] + WHOLE["rest_neurons"]
check(abs(n - WHOLE["neurons"]) / WHOLE["neurons"] < 0.01, f"16 + 69 + 0.7 billion neurons is {n / 1e9:.1f} billion, within 1% of 86")
check(WHOLE["cortex_mass_pct"] + WHOLE["cerebellum_mass_pct"] + WHOLE["rest_mass_pct"] == 100, "the parts' masses add to the whole")
check(abs(WHOLE["cerebellum_neurons"] / WHOLE["neurons"] - 0.8) < 0.01, "four fifths of the neurons are in the cerebellum")
ages = [g[0] for g in GROWTH]
check(ages == sorted(ages) and all(g[1] > g[2] for g in GROWTH), "ages in order, men's brains heavier at every age")
pk = max(g[1] for g in GROWTH)
ipk = [g[1] for g in GROWTH].index(pk)
check(GROWTH[ipk][0] == 20 and all(GROWTH[i][1] < GROWTH[i + 1][1] for i in range(ipk)) and all(GROWTH[i][1] > GROWTH[i + 1][1] for i in range(ipk, len(GROWTH) - 1)), "the mass rises to a peak at twenty and falls after")
check(0.24 < GROWTH[0][1] / pk < 0.28, f"at birth {GROWTH[0][1] / pk * 100:.0f}% of the peak, about a quarter")
g3 = next(g for g in GROWTH if g[0] == 3)
check(0.85 < g3[1] / pk < 0.92 and g3[1] / GROWTH[0][1] > 3.3, f"by three {g3[1] / pk * 100:.0f}% of the peak, and {g3[1] / GROWTH[0][1]:.1f} times the birth mass")
check(0.88 < GROWTH[-1][1] / pk < 0.92, f"in the mid eighties {(1 - GROWTH[-1][1] / pk) * 100:.0f}% below the peak, about a tenth")
check(WHOLE["fibres_km_m"] == 176000 and WHOLE["fibres_km_f"] == 149000, "Marner's fibre lengths, 176,000 and 149,000 km")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1000})
    errs = []
    pg.on("pageerror", lambda x: errs.append(str(x)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#bsvg")

    def st(q=None):
        return pg.evaluate("(q)=>window.__brain(q)", q)

    def hover(k):
        pg.evaluate(f"()=>document.querySelector('#bsvg [data-region=\"{k}\"]').dispatchEvent(new PointerEvent('pointerover',{{bubbles:true}}))")
        pg.wait_for_timeout(80)
        return st()

    def no_overlap(sel):
        boxes = pg.evaluate("(sel)=>[...document.querySelectorAll(sel)].filter(t=>!t.hasAttribute('transform')).map(t=>{const b=t.getBBox(); return [b.x,b.y,b.width,b.height]})", sel)
        return sum(1 for i in range(len(boxes)) for j in range(i + 1, len(boxes)) if boxes[i][0] < boxes[j][0] + boxes[j][2] and boxes[j][0] < boxes[i][0] + boxes[i][2] and boxes[i][1] < boxes[j][1] + boxes[j][3] and boxes[j][1] < boxes[i][1] + boxes[i][3])

    s = st()
    check(s["view"] == "outside" and sorted(s["regions"]) == sorted(p[0] for p in OUTSIDE), "opens on the outside with all twelve regions drawn")
    check("1,400 g" in s["card"] and "176,000 km" in s["card"] and "86 billion" in s["card"], "the whole-organ card: 1,400 g, 176,000 km, 86 billion")
    probes = {"frontal": (300, 250), "parietal": (600, 200), "temporal": (450, 420), "occipital": (770, 250), "cerebellum": (700, 520), "brainstem": (580, 560),
              "motor": (472, 202), "sensory": (498, 202), "broca": (355, 318), "wernicke": (600, 340), "auditory": (470, 356), "visual": (762, 340)}
    for k, p in probes.items():
        at = st({"probe": list(p)})["at"]
        check(at == k, f"the pointer at {p} finds {k}", f"found {at}")
    s = hover("temporal")
    check(s["hot"] == "temporal" and "temporal lobe" in s["name"] and "hippocampus" in s["body"] and "Temporal lobe" in pg.inner_text("#srcTxt"), "hovering the temporal lobe: its card and source")
    s = hover("cerebellum")
    check("69 billion" in s["card"], "the cerebellum's number: 69 billion")
    check(no_overlap("#bsvg text") == 0, "no two labels overlap outside", f"{no_overlap('#bsvg text')}")
    pg.click('#views button[data-v="inside"]')
    pg.wait_for_timeout(150)
    s = st()
    check(s["view"] == "inside" and sorted(s["regions"]) == sorted(p[0] for p in INSIDE), "the inside view draws all thirteen regions")
    check("82% of the mass" in s["card"] and "under a billion" in s["card"], "the inside card: 82% of the mass, under a billion neurons outside cortex and cerebellum")
    for k, p in {"thalamus": (515, 300), "callosum": (500, 212), "cingulate": (500, 178), "hypothalamus": (500, 352), "pituitary": (492, 398), "basal": (436, 292),
                 "midbrain": (570, 364), "pons": (575, 425), "medulla": (575, 500), "cord": (580, 590), "cerebellum": (740, 470), "amygdala": (474, 430), "hippocampus": (590, 380)}.items():
        at = st({"probe": list(p)})["at"]
        check(at == k, f"the pointer at {p} finds {k}", f"found {at}")
    s = hover("callosum")
    check("200 million" in s["card"], "the corpus callosum: 200 million axons")
    s = hover("hippocampus")
    check("H. M." in s["body"] and "taxi" in s["card"], "the hippocampus: H. M. and the taxi drivers")
    check(no_overlap("#bsvg text") == 0, "no two labels overlap inside", f"{no_overlap('#bsvg text')}")
    pg.click('#views button[data-v="growth"]')
    pg.wait_for_timeout(150)
    s = st({"age": 20})
    check(s["view"] == "growth" and s["age"] == 20 and abs(s["marker"] - s["gx"]) < 0.6 and "1,450 g, 100%" in s["card"], "the lifetime view opens at twenty, the peak, 1,450 g")
    G = {"x": 90, "w": 820, "amax": 90}
    GX = lambda a: G["x"] + math.sqrt(a / G["amax"]) * G["w"]
    box = pg.eval_on_selector("#bsvg", "e=>{const r=e.getBoundingClientRect(); return {x:r.left,y:r.top,w:r.width,h:r.height,vh:e.viewBox.baseVal.height}}")
    sx = lambda px: box["x"] + px / 980 * box["w"]
    sy = lambda py: box["y"] + py / box["vh"] * box["h"]
    pg.mouse.move(sx(GX(20)), sy(300))
    pg.mouse.down()
    pg.mouse.move(sx(GX(3)), sy(300), steps=5)
    pg.mouse.up()
    pg.wait_for_timeout(100)
    s = st()
    check(s["age"] == 3 and abs(s["marker"] - GX(3)) < 0.6 and "1,270 g, 88%" in s["card"] and "1,090 g" in s["card"] and "quadrupled" in s["body"], f"dragging to three years: {s['age']}, 1,270 g, 88% of the peak, and the note on quadrupling")
    s = st({"age": 40})
    m40 = 1450 + (1370 - 1450) * (40 - 20) / (58 - 20)
    check(abs(s["m"] - m40) < 1e-9, f"the page interpolates the same as this checker at forty: {m40:.1f} g")
    check(no_overlap("#bsvg text") == 0, "no two labels overlap on the chart", f"{no_overlap('#bsvg text')}")
    check(not errs, "no script errors", "; ".join(errs))
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
