"""Check agriculture.html against its data and its drawing.

  the data     twelve centers, each on land in the mask with a name, its
               plants or animals and a story; dates within the Holocene,
               the Fertile Crescent the oldest; twelve crops in order of
               tonnage with a year each, sugarcane above maize above rice
               and wheat; the land shares add to 100; the biomass figures
               are Bar-On's and livestock is fourteen times the wild
  the drawing  the map is painted with land under the centers; each dot
               stands at its coordinates and on the line of time at its
               date; the pointer over a dot gives its card; the bars have
               their lengths; no label overlaps another
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agriculture_data import CENTERS, CROPS, LAND, BIOMASS

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "agriculture.html"
fails = []


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


print("--- the data ---")
check(len(CENTERS) == 12 and all(c[1] and c[7] and (c[5] != "none" or c[6] != "none") for c in CENTERS), "twelve centers, each with a name, something domesticated and a story")
dated = [c for c in CENTERS if c[4] is not None]
check(all(3000 <= c[4] <= 11700 for c in dated) and max(dated, key=lambda c: c[4])[0] == "crescent", "every date lies within the Holocene and the Fertile Crescent is the oldest")
check([c[2] for c in CROPS] == sorted([c[2] for c in CROPS], reverse=True) and [c[0] for c in CROPS][:4] == ["sugarcane", "maize", "rice", "wheat"], "twelve crops in order: sugarcane, maize, rice, wheat first")
check(all(2016 <= c[3] <= 2026 and c[2] > 0 and c[4] and c[5] for c in CROPS), "each crop has a recent year, a grower and a use")
check(LAND["livestock_pct"] + LAND["crops_people_pct"] + LAND["crops_other_pct"] == 100 and 0 < LAND["animal_calories_pct"] < LAND["animal_protein_pct"] < 50, "the farmland shares add to 100; animals give less than half the calories and protein")
b = {x[0]: x[2] for x in BIOMASS}
check(b == {"livestock": 0.1, "humans": 0.06, "wildmammals": 0.007, "poultry": 0.005, "wildbirds": 0.002}, "the biomass figures are Bar-On's")
check(abs(b["livestock"] / b["wildmammals"] - 14.3) < 0.1 and abs(b["poultry"] / b["wildbirds"] - 2.5) < 0.01, "livestock fourteen times the wild mammals, poultry two and a half times the wild birds")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1100})
    errs = []
    pg.on("pageerror", lambda x: errs.append(str(x)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#ocanvas")
    pg.wait_for_function("()=>window.__agri().land")

    def st(q=None):
        return pg.evaluate("(q)=>window.__agri(q)", q)

    def overlaps(sel):
        boxes = pg.evaluate("(sel)=>[...document.querySelectorAll(sel)].filter(t=>!t.hasAttribute('transform')).map(t=>{const b=t.getBBox(); return [b.x,b.y,b.width,b.height]})", sel)
        return sum(1 for i in range(len(boxes)) for j in range(i + 1, len(boxes)) if boxes[i][0] < boxes[j][0] + boxes[j][2] and boxes[j][0] < boxes[i][0] + boxes[i][2] and boxes[i][1] < boxes[j][1] + boxes[j][3] and boxes[j][1] < boxes[i][1] + boxes[i][3])

    s = st()
    check(s["view"] == "origins" and "12" in s["card"] and "Fertile Crescent" in s["card"], "opens on the origins with twelve places")
    MX = lambda lon: (lon + 180) / 360 * 980
    MY = lambda lat: (90 - lat) / 180 * 460
    TX = lambda ya: 60 + (12000 - ya) / 12000 * 860
    ok = True
    landok = True
    for c in CENTERS:
        d = st({"center": c[0]})
        if abs(d["px"][0] - MX(c[2])) > 0.6 or abs(d["px"][1] - MY(c[3])) > 0.6:
            ok = False
        if c[4] is not None and abs(d["tx"] - TX(c[4])) > 0.6:
            ok = False
        # a pixel just outside the dot, in the direction away from the label, should be land
        for dx, dy in ((0, 14), (0, -14), (14, 0), (-14, 0)):
            px = st({"px": [round(MX(c[2]) + dx), round(MY(c[3]) + dy)]})["pixel"]
            if px[0] >= 60:
                break
        else:
            landok = False
    check(ok, "every center's dot stands at its coordinates and at its date on the line of time")
    check(landok, "every center sits on painted land")
    cbox = pg.eval_on_selector("#ocanvas", "e=>{const r=e.getBoundingClientRect(); return {x:r.left,y:r.top,w:r.width,h:r.height,cw:e.width,ch:e.height}}")
    cx = lambda px: cbox["x"] + px / cbox["cw"] * cbox["w"]
    cy = lambda py: cbox["y"] + py / cbox["ch"] * cbox["h"]
    pg.mouse.move(cx(MX(-100)), cy(MY(18)))
    pg.wait_for_timeout(120)
    s = st()
    check(s["hot"] == "mesoamerica" and "Mesoamerica" in s["name"] and "9,000 years ago" in s["card"] and "maize" in s["card"] and "teosinte" in s["body"], "the pointer over Mexico: Mesoamerica, 9,000 years ago, maize, teosinte")
    pg.mouse.move(cx(TX(10500)), cy(520 - 12))
    pg.wait_for_timeout(120)
    s = st()
    check(s["hot"] == "crescent" and "10,500 years ago" in s["card"] and "sheep, goats" in s["card"], "the pointer on the oldest mark of the line of time: the Fertile Crescent")
    pg.mouse.move(cx(MX(38)), cy(MY(9)))
    pg.wait_for_timeout(120)
    s = st()
    check(s["hot"] == "ethiopia" and "no agreed date" in s["card"], "the Ethiopian highlands: no agreed date")
    pg.mouse.click(cx(MX(-100)), cy(MY(18)))
    pg.wait_for_timeout(120)
    pg.mouse.move(cx(MX(0)), cy(MY(-40)))
    pg.wait_for_timeout(120)
    s = st()
    check(s["pin"] == "mesoamerica" and "Mesoamerica" in s["name"], "a click pins Mesoamerica, and its card stays when the pointer leaves")
    px = st({"px": [round(MX(-100)) - 30, round(MY(18)) + 25]})["pixel"]
    check(pg.evaluate("()=>document.getElementById('ocanvas').getContext('2d').getImageData(0,0,980,460).data.length") > 0 and px != [70, 74, 78] and px != [16, 28, 46], "and draws its crops as chips beside the dot", f"{px}")
    pg.focus("#diagram")
    pg.keyboard.press("Escape")
    check(st()["pin"] is None, "Escape lets it go")
    pg.click("#playBtn")
    pg.wait_for_timeout(1500)
    s1 = st()
    pg.wait_for_timeout(3000)
    s2 = st()
    check(pg.inner_text("#playBtn") == "Pause" and s1["tnow"] is not None and s2["tnow"] < s1["tnow"] and s1["shown"] < s2["shown"] < 12, f"Play runs the years down and the places appear: {s1['shown']} at {s1['tnow']:.0f} years ago, {s2['shown']} at {s2['tnow']:.0f}")
    want = min((c for c in CENTERS if c[4] is not None and c[4] >= s2["tnow"]), key=lambda c: c[4])
    check(s2["hot"] == want[0], f"the card follows the latest: {s2['hot']}")
    pg.wait_for_timeout(5200)
    s = st()
    check(s["tnow"] is None and s["shown"] == 12 and pg.inner_text("#playBtn") == "Play the 12,000 years", "and it stops at now with all twelve")
    pg.mouse.move(cx(TX(8500)), cy(520))
    pg.mouse.down()
    pg.mouse.move(cx(TX(7000)), cy(520), steps=4)
    pg.mouse.up()
    s = st()
    check(abs(s["tnow"] - 7000) < 30 and s["shown"] == 7, f"the line of time scrubs: {s['tnow']:.0f} years ago, {s['shown']} places")
    pg.mouse.move(cx(TX(7000)), cy(520))
    pg.mouse.down()
    pg.mouse.move(cx(TX(0) + 8), cy(520), steps=4)
    pg.mouse.up()
    check(st()["tnow"] is None, "and back to now")
    pg.click('#views button[data-v="harvest"]')
    pg.wait_for_timeout(250)
    g = st()["grow"]
    pg.wait_for_timeout(900)
    check(0 < g < 1 and st()["grow"] == 1, f"the bars grow in (a quarter second in: {g:.2f})")
    s = st({"crop": "rice"})
    check(s["view"] == "harvest" and s["bars"] == 12 and abs(s["barw"] - s["expect"]) < 0.6 and "6.6 billion" in s["card"], "the harvest: twelve bars at their lengths, 6.6 billion metric tons together")
    pg.evaluate("()=>document.querySelector('#asvg g[data-crop=\"soy\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(80)
    s = st()
    check(s["name"] == "soybeans" and "353 million metric tons" in s["card"] and "feeds livestock" in s["card"] and "44 kg" in s["card"], "hovering soybeans: 353 million metric tons, feed, 44 kg a person")
    check(overlaps("#asvg text") == 0, "no two labels overlap on the harvest", f"{overlaps('#asvg text')}")
    pg.click('#views button[data-v="land"]')
    pg.wait_for_timeout(150)
    s = st()
    check(s["view"] == "land" and s["bios"] == 5 and "48 million" in s["card"] and "80% of it" in s["card"], "the land view: five biomass bars, 48 million km², 80% for livestock")
    w = pg.evaluate("()=>[...document.querySelectorAll('#asvg g[data-land] rect')].slice(2,5).map(r=>+r.getAttribute('width'))")
    check(abs(w[0] - 820 * 0.80) < 0.6 and abs(w[1] - 820 * 0.16) < 0.6 and abs(w[2] - 820 * 0.04) < 0.6, "the farmland bar splits 80, 16, 4")
    pg.evaluate("()=>document.querySelector('#asvg g[data-bio=\"livestock\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(80)
    s = st()
    check("livestock" in s["name"] and "14.3 times all wild mammals" in s["card"], "hovering livestock: 14.3 times all wild mammals")
    bw = pg.evaluate("()=>[...document.querySelectorAll('#asvg g[data-bio] rect')].map(r=>+r.getAttribute('width'))")
    BX = lambda v: math.log10(v / 0.001) / math.log10(0.2 / 0.001) * 820
    check(all(abs(bw[i] - BX(BIOMASS[i][2])) < 0.6 for i in range(5)), "the biomass bars have their log lengths")
    check(overlaps("#asvg text") == 0, "no two labels overlap on the land view", f"{overlaps('#asvg text')}")
    pg.evaluate("()=>{const r=document.querySelector('#asvg g[data-land=\"livestock\"] rect').getBoundingClientRect(); document.querySelector('#asvg g[data-land=\"livestock\"] rect').dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,clientX:r.left+20,clientY:r.top+10}))}")
    pg.wait_for_timeout(1000)
    s = st()
    w = pg.evaluate("()=>['grazing','feed'].map(k=>+document.querySelector('#asvg g[data-land=\"'+k+'\"] rect').getAttribute('width'))")
    check(s["split"] == 1 and abs(w[0] + w[1] + 4 - 820 * 0.80) < 0.6 and abs(w[0] - (820 * 0.67 - 2)) < 0.6 and "Grazing land" in s["name"], f"a click opens the livestock's land into grazing and feed: {w[0]:.0f} and {w[1]:.0f} px")
    check(overlaps("#asvg text") == 0, "no two labels overlap with it open", f"{overlaps('#asvg text')}")
    check(pg.evaluate("()=>[...document.querySelectorAll('.note')].filter(n=>n.checkVisibility()).length === 1 && !document.querySelector('details.sources').open"), "one caption, the rest in a closed Sources")
    check(len(pg.inner_text(".note").split()) <= 80, f"the caption runs {len(pg.inner_text('.note').split())} words")
    check(not errs, "no script errors", "; ".join(errs))
    ph = br.new_page(viewport={"width": 390, "height": 844})
    ph.goto(PAGE.as_uri())
    ph.wait_for_timeout(400)
    ov = ph.evaluate("document.documentElement.scrollWidth - innerWidth")
    check(ov == 0, f"nothing wider than a phone: {ov} px over")
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
