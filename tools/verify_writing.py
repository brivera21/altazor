"""Check writing.html against its data and its drawing.

  the data     every script has a kind that exists, a place, a story; every
               parent is an earlier script in the list; the roots are the
               independent inventions; Latin's line runs back to the
               Egyptian signs; five letters with five stages each, dated
               in order, each with a drawable path; the sign counts are in
               the right order of magnitude for their kind
  the drawing  every dot stands at its date; every line of descent joins a
               parent's dot to its child's; no label touches another
               label or another dot; hovering a script gives its card and
               its lineage; the letter cells and the bars answer
"""
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from writing_data import TYPES, SCRIPTS, LETTERS, COUNTS

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "writing.html"
fails = []


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


print("--- the data ---")
byk = {s[0]: s for s in SCRIPTS}
check(len(byk) == len(SCRIPTS), f"{len(SCRIPTS)} scripts, no key twice")
check(all(s[4] in TYPES and s[5] and s[6] for s in SCRIPTS), "every script has a kind that exists, a place and a story")
check(all(s[3] is None or (s[3] in byk and byk[s[3]][2] < s[2]) for s in SCRIPTS), "every parent is an earlier script in the list")
roots = [s[0] for s in SCRIPTS if s[3] is None]
check(set(roots) == {"cuneiform", "hieroglyphs", "indus", "lineara", "chinese", "maya", "hangul", "cherokee"}, f"the roots: {', '.join(roots)}")


def chain(k):
    out = []
    while byk[k][3]:
        k = byk[k][3]
        out.append(k)
    return out


check(chain("latin") == ["etruscan", "greek", "phoenician", "protosinaitic", "hieroglyphs"], "Latin runs back through Etruscan, Greek, Phoenician and Proto-Sinaitic to the Egyptian signs")
check(chain("devanagari") == ["brahmi", "aramaic", "phoenician", "protosinaitic", "hieroglyphs"] and chain("arabic")[:2] == ["nabataean", "aramaic"], "Devanagari and Arabic both run back through Aramaic")
check(chain("kana") == ["chinese"] and chain("mongolian")[0] == "syriac", "kana from Chinese; Mongolian from Syriac")


def desc(k):
    return sum(1 + desc(c[0]) for c in SCRIPTS if c[3] == k)


check(desc("hieroglyphs") == len(SCRIPTS) - len(roots) - desc("chinese") - desc("lineara"), f"{desc('hieroglyphs')} scripts descend from the Egyptian signs, all but the other families")
check(len(LETTERS) == 5 and all(len(L[3]) == 5 for L in LETTERS) and [L[1] for L in LETTERS] == ["A", "B", "M", "N", "O"], "five letters, five stages each: A, B, M, N, O")
check(all([st[1] for st in L[3]] == sorted(st[1] for st in L[3]) for L in LETTERS), "the stages of each letter are in date order")
path_ok = re.compile(r"^[MLCZAmlcza0-9,.\- ]+$")
check(all(path_ok.match(st[4]) and st[4].startswith("M") for L in LETTERS for st in L[3]), "every stage has a drawable path")
check(all(c[3] in TYPES and c[2] > 0 for c in COUNTS), "every count has a kind and a number")
kinds = {}
for c in COUNTS:
    kinds.setdefault(c[3], []).append(c[2])
check(max(kinds["alpha"] + kinds["abjad"] + kinds["feat"] + kinds["abugida"]) < 60 and min(kinds["syll"]) >= 40 and min(kinds["logo"]) >= 500, "alphabets under sixty signs, syllabaries from forty, word-scripts from hundreds")
check(kinds["logo"] == sorted(kinds["logo"], reverse=True) and COUNTS[0][2] == 3000, "Chinese 3,000 above hieroglyphs above cuneiform")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1100})
    errs = []
    pg.on("pageerror", lambda x: errs.append(str(x)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#wsvg")

    def st(q=None):
        return pg.evaluate("(q)=>window.__writing(q)", q)

    def hover(sel):
        pg.evaluate(f"()=>document.querySelector('{sel}').dispatchEvent(new PointerEvent('pointerover',{{bubbles:true}}))")
        pg.wait_for_timeout(80)
        return st()

    def overlaps(sel):
        boxes = pg.evaluate("(sel)=>[...document.querySelectorAll(sel)].filter(t=>!t.hasAttribute('transform')).map(t=>{const b=t.getBBox(); return [b.x,b.y,b.width,b.height]})", sel)
        return sum(1 for i in range(len(boxes)) for j in range(i + 1, len(boxes)) if boxes[i][0] < boxes[j][0] + boxes[j][2] and boxes[j][0] < boxes[i][0] + boxes[i][2] and boxes[i][1] < boxes[j][1] + boxes[j][3] and boxes[j][1] < boxes[i][1] + boxes[i][3])

    s = st()
    check(s["view"] == "tree" and s["dots"] == len(SCRIPTS), f"opens on the scripts with {len(SCRIPTS)} dots")
    check("8 of them" in s["card"] and f"{desc('hieroglyphs')} of the rest" in s["card"], "the opening card counts the roots and the Egyptian family")
    T = {"x": 40, "w": 900, "y0": -3400, "y1": 2030}
    TX = lambda y: T["x"] + (y - T["y0"]) / (T["y1"] - T["y0"]) * T["w"]
    ok = True
    for k, n, y, *_ in SCRIPTS:
        d = st({"script": k})
        if abs(d["dot"][0] - TX(y)) > 0.6:
            ok = False
    check(ok, "every dot stands at its date on the line of time")
    dots = {k: st({"script": k})["dot"] for k in byk}
    edges = st({"edges": True})["edges"]
    ends = []
    for d in edges:
        m = re.match(r"M([\d.]+),([\d.]+) C[\d., ]+ ([\d.]+),([\d.]+)$", d)
        ends.append((float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))))
    want = {(round(dots[s[3]][0], 1), dots[s[3]][1], round(dots[s[0]][0], 1), dots[s[0]][1]) for s in SCRIPTS if s[3]}
    got = {(round(a, 1), b, round(c, 1), dd) for a, b, c, dd in ends}
    check(len(edges) == len(SCRIPTS) - len(roots) and got == want, f"{len(edges)} lines of descent, each from a parent's dot to its child's")
    check(overlaps("#wsvg g[data-script] text") == 0, "no two script labels overlap", f"{overlaps('#wsvg g[data-script] text')}")
    n = pg.evaluate("""()=>{ const ts=[...document.querySelectorAll('#wsvg g[data-script] text')].map(t=>{const b=t.getBBox(); return [t.parentNode.getAttribute('data-script'),b.x,b.y,b.width,b.height]});
      const cs=[...document.querySelectorAll('#wsvg g[data-script] circle')].map(c=>[c.parentNode.getAttribute('data-script'),+c.getAttribute('cx'),+c.getAttribute('cy')]);
      let n=0; for(const t of ts) for(const c of cs){ if(t[0]===c[0]) continue; if(c[1]>t[1]-7&&c[1]<t[1]+t[3]+7&&c[2]>t[2]-7&&c[2]<t[2]+t[4]+7) n++; } return n; }""")
    check(n == 0, "no label touches another script's dot", f"{n}")
    s = hover('#wsvg g[data-script="aramaic"]')
    check(s["hot"] == "aramaic" and "Aramaic" in s["name"] and "900 BC" in s["card"] and f"{desc('aramaic')} scripts" in s["card"] and "Phoenician, which came from Proto-Sinaitic" in s["card"], "hovering Aramaic: 900 BC, its descendants, its line back")
    bright = pg.evaluate("()=>[...document.querySelectorAll('#wsvg path[fill=\"none\"]')].filter(p=>p.getAttribute('stroke')==='#e6e6e6').length")
    check(bright == desc("aramaic") + len(chain("aramaic")), f"its lineage lights up: {bright} lines, descendants and ancestors")
    s = hover('#wsvg g[data-script="hangul"]')
    check("invented from nothing" in pg.inner_text("#kindTxt").lower() and "1443" in s["card"] and "no earlier script" in s["card"], "Hangul: invented from nothing, 1443")
    pg.click('#views button[data-v="letters"]')
    pg.wait_for_timeout(150)
    s = st()
    check(s["view"] == "letters" and s["cells"] == 25, "the letters view: 25 cells")
    s = hover('#wsvg g[data-cell="a:2"]')
    check("aleph" in s["name"] and "phoenician, 1000 bc" in pg.inner_text("#kindTxt").lower() and "turned on its side" in s["body"], "the Phoenician aleph's cell answers")
    s = hover('#wsvg g[data-letter="b"]')
    check(s["name"].startswith("B, the house") and "bayt" in s["card"], "the letter B's row answers: bayt")
    check(overlaps("#wsvg text") == 0, "no two labels overlap in the letters view", f"{overlaps('#wsvg text')}")
    pg.click('#views button[data-v="counts"]')
    pg.wait_for_timeout(150)
    s = st({"count": "chinese"})
    check(s["view"] == "counts" and s["bars"] == len(COUNTS), f"the signs view: {len(COUNTS)} bars")
    C = {"w": 720, "lo": 10, "hi": 10000}
    check(abs(s["barw"] - math.log10(3000 / C["lo"]) / math.log10(C["hi"] / C["lo"]) * C["w"]) < 0.6, "the Chinese bar has its log-scale length")
    s = hover('#wsvg g[data-count="hangul"]')
    check("24" in s["card"] and "Fourteen consonants" in s["body"] and "featural" in pg.inner_text("#kindTxt").lower(), "the Hangul bar answers: 24, featural")
    check(overlaps("#wsvg text") == 0, "no two labels overlap in the signs view", f"{overlaps('#wsvg text')}")
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
