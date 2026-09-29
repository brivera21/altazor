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
    # the disputed descents read apart from the rest
    dis = pg.evaluate("()=>[...document.querySelectorAll('#wsvg path[data-disputed]')].map(p=>[p.getAttribute('stroke'),p.getAttribute('stroke-dasharray')])")
    check(len(dis) == 2 and all(d[1] == "2 5" for d in dis), f"the two disputed lines are dotted ({dis})")
    # a click pins a script's line; a second click or Escape lets go
    pg.evaluate("()=>{hot=null; render(); showTree();}")
    pg.click('#wsvg g[data-script="latin"] circle')
    pg.mouse.move(5, 5)
    pg.wait_for_timeout(80)
    s = st()
    bright = pg.evaluate("()=>[...document.querySelectorAll('#wsvg path[fill=\"none\"]')].filter(p=>p.getAttribute('stroke')==='#e6e6e6').length")
    check(s["pinned"] == "latin" and s["name"] == "Latin" and bright == len(chain("latin")), f"Latin, clicked, stays lit with its line back to Egypt ({bright} lines) after the pointer leaves")
    pg.keyboard.press("Escape")
    check(st()["pinned"] is None and "Where writing came from" in st()["name"], "Escape lets it go")
    # a kind in the key lights every script of that kind
    pg.hover('#legend span[data-t="abjad"]')
    pg.wait_for_timeout(80)
    ops = pg.evaluate("()=>[...document.querySelectorAll('#wsvg g[data-script]')].map(g=>[g.getAttribute('data-script'),g.getAttribute('opacity')])")
    abj = {k for k, n, y, p_, t, *_ in SCRIPTS if t == "abjad"}
    check(st()["kind"] == "abjad" and all((o == "1") == (k in abj) for k, o in ops), f"the abjads in the key light the {len(abj)} abjads and dim the rest")
    pg.mouse.move(5, 5)
    pg.wait_for_timeout(80)
    check(st()["kind"] is None, "and let go when the pointer leaves the key")
    # the year: scripts appear at their first inscription
    pg.evaluate("()=>{const r=document.getElementById('year'); r.value=-1000; r.dispatchEvent(new Event('input'))}")
    s = st()
    seen = [k for k, n, y, *_ in SCRIPTS if y <= -1000]
    nedges = sum(1 for k, n, y, p_, *_ in SCRIPTS if p_ and y <= -1000)
    ed = len(st({"edges": True})["edges"])
    check(s["dots"] == len(seen) and ed == nedges and f"{len(seen)} scripts" in pg.inner_text("#yearOut"),
          f"at 1000 BC: {len(seen)} scripts and {nedges} lines of descent drawn")
    pg.evaluate("()=>setYear(2030)")
    pg.click("#yPlay")
    pg.wait_for_timeout(700)
    s = st()
    check(s["playing"]["year"] and -3400 < s["year"] < -2000 and pg.inner_text("#yPlay") == "Pause", f"Play runs the year from 3400 BC (at {s['year']:.0f}), the button reads Pause")
    pg.wait_for_function("()=>!window.__writing().playing.year", timeout=15000)
    s = st()
    check(s["year"] == 2030 and s["dots"] == len(SCRIPTS) and pg.inner_text("#yPlay") == "Play", "and stops at today with every script drawn")
    s = hover('#wsvg g[data-script="hangul"]')
    check("invented from nothing" in pg.inner_text("#kindTxt").lower() and "1443" in s["card"] and "no earlier script" in s["card"], "Hangul: invented from nothing, 1443")
    pg.click('#views button[data-v="letters"]')
    pg.wait_for_timeout(150)
    s = st()
    check(s["view"] == "letters" and s["cells"] == 25, "the letters view: 25 cells")
    s = hover('#wsvg g[data-cell="a:2"]')
    check("aleph" in s["name"] and "phoenician, 1000 bc" in pg.inner_text("#kindTxt").lower() and "turned on its side" in s["body"], "the Phoenician aleph's cell answers")
    # the letters in between: every stroke resampled to one point count; at a whole stage the drawing is that stage's
    def morph_box(k, m):
        return pg.evaluate("""([k,m])=>{ setMorph(m); const ps=[...document.querySelectorAll('#wsvg g.mg[data-morph="'+k+'"] path')];
          let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9; for(const p of ps){ const b=p.getBBox(); x0=Math.min(x0,b.x); y0=Math.min(y0,b.y); x1=Math.max(x1,b.x+b.width); y1=Math.max(y1,b.y+b.height); }
          return {box:[x0,y0,x1,y1], counts:ps.map(p=>p.getAttribute('d').split('L').length)}; }""", [k, m])
    def cell_box(k, i):
        return pg.evaluate("""([k,i])=>{ const b=document.querySelector('#wsvg g[data-cell="'+k+':'+i+'"] path').getBBox(); return [b.x,b.y,b.x+b.width,b.y+b.height]; }""", [k, i])
    ok, bad = True, []
    for L in LETTERS:
        for i in range(5):
            mb = morph_box(L[0], i)
            cb = cell_box(L[0], i)
            if not all(abs(a - b) < 1.0 for a, b in zip(mb["box"], cb)) or any(c != 48 for c in mb["counts"]):
                ok = False
                bad.append(f"{L[0]}{i}")
    check(ok, "at each whole stage the drawing in between is that stage's letter, every stroke 48 points", ", ".join(bad))
    mid = morph_box("a", 1.5)
    check(mid["box"] != cell_box("a", 1) and mid["box"] != cell_box("a", 2) and all(c == 48 for c in mid["counts"]), "halfway from 'alp to 'aleph it is neither")
    pg.evaluate("()=>setMorph(0)")
    pg.click("#mPlay")
    pg.wait_for_timeout(500)
    s = st()
    check(s["playing"]["morph"] and 0 < s["morph"] < 1 and pg.inner_text("#mPlay") == "Pause", f"Play carries the letters on (at stage {s['morph'] + 1:.2f}), the button reads Pause")
    pg.wait_for_function("()=>!window.__writing().playing.morph", timeout=10000)
    check(st()["morph"] == 4 and pg.inner_text("#mPlay") == "Play" and "Latin" in pg.inner_text("#morphOut"), "and stops at the Latin letters")
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
