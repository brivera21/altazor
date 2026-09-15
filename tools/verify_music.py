"""Check music.html against its data and its drawing.

  the data     A0 is 27.5 Hz and C8 4,186 in equal temperament on A440;
               the ranges lie inside the piano and hearing; the just
               ratios give the textbook cents (a fifth 701.96, a major
               third 386.31), twelve fifths overshoot seven octaves by
               23.46 cents; every scale starts on the root, climbs, and
               stays inside the octave
  the drawing  88 keys each at its frequency on the log line; the marker
               drags and the card reads the pitch and its harmonics; the
               interval dots stand at their cents; the scale lights the
               right keys in both octaves; no label overlaps another
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from music_data import A4, SPEED_OF_SOUND, HEARING, PIANO, NOTE_NAMES, RANGES, INTERVALS, SCALES

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "music.html"
fails = []


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


f = lambda m: A4 * 2 ** ((m - 69) / 12)
cents = lambda r: 1200 * math.log2(r)
print("--- the data ---")
check(abs(f(21) - 27.5) < 1e-9 and abs(f(108) - 4186.01) < 0.01 and abs(f(60) - 261.63) < 0.01, "A0 27.5 Hz, middle C 261.63, C8 4,186.01")
check(all(PIANO[0] <= r[3] < r[4] <= PIANO[1] for r in RANGES) and all(HEARING[0] < f(r[3]) and f(r[4]) < HEARING[1] for r in RANGES), "every range lies on the piano and within hearing")
iv = {s: r for s, n, r, b in INTERVALS}
check(abs(cents(3 / 2) - 701.955) < 0.001 and abs(cents(5 / 4) - 386.314) < 0.001 and abs(cents(6 / 5) - 315.641) < 0.001, "a pure fifth is 701.955 cents, a major third 386.314, a minor third 315.641")
check(all(abs(cents(r[0] / r[1]) - 100 * s) < 20 for s, r in iv.items()), "every just ratio lies within 20 cents of its tempered step")
check(abs(12 * cents(3 / 2) - 8400 - 23.460) < 0.001, "twelve fifths overshoot seven octaves by 23.460 cents, the comma")
check(all(st[0] == 0 and st == sorted(st) and len(set(st)) == len(st) and st[-1] < 12 for _, _, _, st, _ in SCALES), "every scale starts on the root, climbs, and stays inside the octave")
sc = {k: st for k, _, _, st, _ in SCALES}
check(sc["major"] == [0, 2, 4, 5, 7, 9, 11] and sorted(sc["minor"]) == sorted((x - 9) % 12 for x in sc["major"]), "the natural minor is the major scale from its sixth degree")
check(sorted(sc["pentamin"]) == sorted((x - 9) % 12 for x in sc["pentamaj"]) and set(sc["pentamaj"]) < set(sc["major"]) and set(sc["blues"]) == set(sc["pentamin"]) | {6}, "the pentatonics are five notes of the major scale; the blues scale adds the flat fifth")
check(len(sc["wholetone"]) == 6 and len(sc["octatonic"]) == 8 and len(sc["chromatic"]) == 12, "six, eight and twelve notes in the symmetrical scales")
modes = {"dorian": 2, "phrygian": 4, "lydian": 5, "mixolydian": 7, "locrian": 11}
check(all(sorted(sc[k]) == sorted((x - d) % 12 for x in sc["major"]) for k, d in modes.items()), "the five modes are the white keys from D, E, F, G and B")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1100})
    errs = []
    pg.on("pageerror", lambda x: errs.append(str(x)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#msvg")

    def st(q=None):
        return pg.evaluate("(q)=>window.__music(q)", q)

    def overlaps(sel):
        boxes = pg.evaluate("(sel)=>[...document.querySelectorAll(sel)].filter(t=>!t.hasAttribute('transform')).map(t=>{const b=t.getBBox(); return [b.x,b.y,b.width,b.height]})", sel)
        return sum(1 for i in range(len(boxes)) for j in range(i + 1, len(boxes)) if boxes[i][0] < boxes[j][0] + boxes[j][2] and boxes[j][0] < boxes[i][0] + boxes[i][2] and boxes[i][1] < boxes[j][1] + boxes[j][3] and boxes[j][1] < boxes[i][1] + boxes[i][3])

    N = {"x": 70, "w": 850, "f0": 20, "f1": 20000}
    FX = lambda hz: N["x"] + math.log(hz / N["f0"]) / math.log(N["f1"] / N["f0"]) * N["w"]
    s = st()
    check(s["view"] == "notes" and s["keys"] == 88 and s["ranges"] == len(RANGES) - 1 and s["freq"] == 440, "opens on the notes: 88 keys, the ranges, the marker at 440 Hz")
    check("440 Hz, A4" in s["name"] and "78.0 cm" in s["card"] and "key 49 of 88" in s["card"] and "2× 880 Hz, A5" in s["card"] and "5× 2,200 Hz, C#7 (-14¢)" in s["card"], "the A440 card: 78 cm, key 49, harmonics with the flat fifth harmonic")
    ok = True
    for m in (21, 60, 69, 108):
        d = st({"midi": m})
        if not (d["keyx"][0] < FX(f(m)) < d["keyx"][1]):
            ok = False
    check(ok, "A0, middle C, A4 and C8 each sit over their frequency on the line")
    box = pg.eval_on_selector("#msvg", "e=>{const r=e.getBoundingClientRect(); return {x:r.left,y:r.top,w:r.width,h:r.height,vh:e.viewBox.baseVal.height}}")
    sx = lambda px: box["x"] + px / 980 * box["w"]
    sy = lambda py: box["y"] + py / box["vh"] * box["h"]
    pg.mouse.move(sx(FX(440)), sy(78))
    pg.mouse.down()
    pg.mouse.move(sx(FX(261.63)), sy(78), steps=6)
    pg.mouse.up()
    pg.wait_for_timeout(100)
    s = st()
    check(abs(s["freq"] - 261.6) < 1 and abs(s["marker"] - FX(s["freq"])) < 0.6 and "C4" in s["name"], f"dragging the marker to middle C: {s['freq']} Hz, the card says C4")
    pg.evaluate("()=>document.querySelector('#msvg g[data-range=\"violin\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(80)
    s = st()
    check(s["name"] == "violin" and "G3 to E7" in s["card"] and "196.0 to 2,637 Hz" in s["card"], "hovering the violin: G3 to E7, 196 to 2,637 Hz")
    check(overlaps("#msvg text") == 0, "no two labels overlap on the notes", f"{overlaps('#msvg text')}")
    pg.click('#views button[data-v="intervals"]')
    pg.wait_for_timeout(150)
    s = st({"interval": 4})
    R = {"cx": 470, "cy": 330, "r": 230}
    pt = lambda r, c: (R["cx"] + r * math.cos(c / 1200 * 2 * math.pi - math.pi / 2), R["cy"] + r * math.sin(c / 1200 * 2 * math.pi - math.pi / 2))
    e, j = pt(R["r"], 400), pt(R["r"] + 30, cents(5 / 4))
    check(abs(s["dots"][0][0] - e[0]) < 0.6 and abs(s["dots"][0][1] - e[1]) < 0.6 and abs(s["dots"][1][0] - j[0]) < 0.6 and abs(s["dots"][1][1] - j[1]) < 0.6, "the major third's two dots stand at 400 and 386.3 cents on the ring")
    pg.evaluate("()=>document.querySelector('#msvg g[data-interval=\"7\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(80)
    s = st()
    check("perfect fifth" in s["name"] and "3:2, 702.0 cents" in s["card"] and "2.0 cents flat" in s["card"], "hovering the fifth: 3:2, 702.0 cents, the piano 2.0 cents flat")
    check(overlaps("#msvg text") == 0, "no two labels overlap on the ring", f"{overlaps('#msvg text')}")
    pg.click('#imodes button[data-m="fifths"]')
    pg.wait_for_timeout(100)
    s = st()
    check(s["imode"] == "fifths" and "23.46 cents" in s["card"] and pg.evaluate("()=>document.querySelectorAll('#msvg g[data-fifth]').length") == 13, "the spiral of twelve fifths, thirteen dots, the comma of 23.46 cents")
    pg.evaluate("()=>document.querySelector('#msvg g[data-fifth=\"12\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(80)
    s = st()
    check("B♯" in s["name"] and "8,423.46" in s["card"] and "23.46 cents sharp" in s["card"], "the twelfth fifth: B sharp, 8,423.46 cents, 23.46 sharp of C")
    pg.click('#views button[data-v="scales"]')
    pg.wait_for_timeout(150)
    s = st()
    want = sorted([60 + x for x in sc["major"]] + [72 + x for x in sc["major"]] + [84])
    check(s["scale"] == "major" and sorted(s["lit"]) == want, "the major scale lights C D E F G A B in both octaves and the top C")
    pg.click('#scales button[data-s="pentamin"]')
    pg.wait_for_timeout(100)
    s = st()
    want = sorted([60 + x for x in sc["pentamin"]] + [72 + x for x in sc["pentamin"]] + [84])
    check(sorted(s["lit"]) == want and "C D# F G A#" in s["card"] and "(5)" in s["card"], "the minor pentatonic lights five notes an octave: C D# F G A#")
    pg.click('#scales button[data-s="wholetone"]')
    pg.wait_for_timeout(100)
    s = st()
    check("2 2 2 2 2 2" in s["card"] and "Debussy" in s["body"], "the whole-tone scale: six whole steps")
    check(overlaps("#msvg text") == 0, "no two labels overlap on the keyboard", f"{overlaps('#msvg text')}")
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
