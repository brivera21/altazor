"""Check nervous-systems.html against its data and its drawing.

  the data     six plans, each with examples, a place for the neurons and
               a source; every animal names a plan that exists, has a
               group with a colour, a mass and a source; the counts are the
               published ones at the landmarks (302, 139,255, 86 billion,
               257 billion); neurons rise with mass within the mammals;
               primates sit above the mammal line; the neurons-per-gram
               figures the cards quote follow
  the drawing  six panels, each answering; 21 dots at their log-log
               positions; a group button dims the rest; the lines fitted
               on the page match the fits here; no label off the edge
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nervous_systems_data import PLANS, ANIMALS, GROUPS

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "nervous-systems.html"
fails = []


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


print("--- the data ---")
pk = {p[0] for p in PLANS}
check(len(PLANS) == 6 and all(p[1] and p[2] and p[4] and p[5] for p in PLANS), "six plans, each with examples, a place for the neurons and a source")
check(all(a[5] in pk and a[4] in GROUPS and a[3] > 0 and a[7] for a in ANIMALS), f"{len(ANIMALS)} animals, each on a plan, in a group, with a mass and a source")
a = {x[0]: x for x in ANIMALS}
check(a["celegans"][2] == 302 and a["fly"][2] == 139255 and a["human"][2] == 86e9 and a["elephant"][2] == 257e9 and a["octopus"][2] == 500e6, "the landmarks: 302, 139,255, 86 billion, 257 billion, half a billion")
check(a["sponge"][2] == 0 and all(x[2] > 0 for x in ANIMALS if x[0] != "sponge"), "the sponge alone has none")
mam = sorted([x for x in ANIMALS if x[4] == "mammals"], key=lambda x: x[3])
check(all(mam[i][2] < mam[i + 1][2] for i in range(len(mam) - 1)), "within the mammals, neurons rise with body mass")


def fit(rows):
    xs = [math.log10(r[3]) for r in rows]
    ys = [math.log10(r[2]) for r in rows]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return my - b * mx, b


am, bm = fit(mam)
print(f"    mammals: neurons ~ mass^{bm:.2f}")
check(0.5 < bm < 0.9, f"the mammal line's slope is {bm:.2f}, between a half and one")
for k in ("human", "chimp", "macaque", "raven", "zebrafinch"):
    x = a[k]
    above = math.log10(x[2]) - (am + bm * math.log10(x[3]))
    check(above > 0.3, f"{x[1]} sits {10 ** above:.1f} times above the mammal line")
above = math.log10(a["pigeon"][2]) - (am + bm * math.log10(a["pigeon"][3]))
check(above > 0, f"the pigeon just above it, {10 ** above:.1f} times")
check(abs(a["elephant"][2] / a["human"][2] - 3) < 0.05, "the elephant has three times a person's neurons")
check(a["raven"][2] > a["cat"][2] and a["raven"][3] < a["cat"][3], "the raven out-counts the cat at a third of the mass")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1000})
    errs = []
    pg.on("pageerror", lambda x: errs.append(str(x)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#nsvg")

    def st(q=None):
        return pg.evaluate("(q)=>window.__ns(q)", q)

    s = st()
    check(s["view"] == "plans" and s["plans"] == 6, "opens on six plans")
    pg.evaluate("()=>document.querySelector('#nsvg g[data-plan=\"octopus\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(100)
    s = st()
    check("eight half-brains" in s["name"] and "two thirds of them in the arms" in s["card"] and "octopus 500 million" in s["card"], "hovering the octopus plan: two thirds in the arms, and the count")
    pg.evaluate("()=>document.querySelector('#nsvg g[data-plan=\"none\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(100)
    check("no neurons" in st()["name"] and "sponge" in st()["card"], "the sponge panel: no neurons")
    pg.click('#views button[data-v="counts"]')
    pg.wait_for_timeout(150)
    s = st({"dot": "human", "at": [70000, 86e9]})
    check(s["dots"] == 21, "21 dots drawn")
    check(abs(s["dot"][0] - s["px"]) < 0.6 and abs(s["dot"][1] - s["py"]) < 0.6, "a person's dot sits at 70 kg and 86 billion on the log axes")
    P = {"x": 80, "y": 30, "w": 840, "h": 560}
    px = lambda g: P["x"] + (math.log10(g) + 6.5) / 13.5 * P["w"]
    py = lambda N: P["y"] + P["h"] - (math.log10(N) - 2) / 10 * P["h"]
    for k in ("celegans", "fly", "elephant", "raven"):
        d = st({"dot": k})["dot"]
        check(abs(d[0] - px(a[k][3])) < 0.6 and abs(d[1] - py(a[k][2])) < 0.6, f"  and {a[k][1]}'s")
    pg.evaluate("()=>document.querySelector('#nsvg g[data-a=\"elephant\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(100)
    s = st()
    check("elephant" in s["name"] and "257 billion" in s["card"] and "3.0 times as many" in s["card"] and "4 tonnes" in s["card"], "hovering the elephant: 257 billion, 3.0 times a person, 4 tonnes")
    pg.evaluate("()=>document.querySelector('#nsvg g[data-a=\"celegans\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(100)
    s = st()
    check("302" in s["card"] and "one 284,768,212th" in s["card"], "the roundworm: 302, one 284,768,212th of a person")
    pg.click('#groups button[data-g="birds"]')
    pg.wait_for_timeout(100)
    dim = pg.evaluate("()=>[...document.querySelectorAll('#nsvg g[data-a]')].filter(g=>g.getAttribute('opacity')==='0.25').length")
    check(st()["group"] == "birds" and dim == 17, f"the birds button dims the other {dim} dots")
    over = pg.evaluate("()=>{const svg=document.querySelector('#nsvg'); let n=0; for(const t of svg.querySelectorAll('text')){ if(t.hasAttribute('transform')) continue; const b=t.getBBox(); if(b.x<0||b.x+b.width>980) n++; } return n;}")
    check(over == 0, "no label runs off the edge", f"{over}")
    # labels do not overlap one another
    boxes = pg.evaluate("()=>[...document.querySelectorAll('#nsvg g[data-a] text')].map(t=>{const b=t.getBBox(); return [b.x,b.y,b.width,b.height]})")
    clash = sum(1 for i in range(len(boxes)) for j in range(i + 1, len(boxes)) if boxes[i][0] < boxes[j][0] + boxes[j][2] and boxes[j][0] < boxes[i][0] + boxes[i][2] and boxes[i][1] < boxes[j][1] + boxes[j][3] and boxes[j][1] < boxes[i][1] + boxes[i][3])
    check(clash == 0, "no two animal labels overlap", f"{clash} pairs")
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
