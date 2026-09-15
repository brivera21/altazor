"""Check numbers.html against its data and its drawing.

  the data     seven systems, each with base, place value, zero, when, reach,
               note and source; presets inside the input's range
  the writers  every number from 1 to 9999 written by the page agrees with an
               independent conversion here: Roman (with the bar past 3999),
               Chinese (the rule for the empty place and the leading ten),
               Maya base twenty, Babylonian base sixty with its empty place,
               Egyptian counts by power of ten, tally by fives
  the marks    what is drawn matches what is read: dots and bars, chevrons
               and wedges, strokes, tally lines
  the line     ten sits half way along read logarithmically, a tenth read
               linearly, and in between at the blend; the rows answer
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from numbers_data import SYSTEMS, PRESETS, LINE, REFS

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "numbers.html"
fails = []


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


# ---- independent conversions ----
def roman(n):
    T = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
         (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for v, c in T:
        while n >= v:
            out += c
            n -= v
    return out


def roman_read(n):
    if n < 4000:
        return roman(n)
    return roman(n // 1000) + " with a bar, ×1000, then " + (roman(n % 1000) or "nothing")


def chinese(n):
    D = "零一二三四五六七八九"
    P = ["千", "百", "十", ""]
    digits = [int(c) for c in f"{n:04d}"]
    out, pending_zero, started = "", False, False
    for i, c in enumerate(digits):
        if c == 0:
            if started:
                pending_zero = True
            continue
        if pending_zero:
            out += "零"
            pending_zero = False
        if not (c == 1 and P[i] == "十" and not started):   # 十 to 十九 without the leading 一
            out += D[c]
        out += P[i]
        started = True
    return out


def digits(n, base):
    d = []
    while True:
        d.append(n % base)
        n //= base
        if n == 0:
            break
    return d[::-1]


def parse_places(read):
    """'5 × 20^2 + 1 × 20 + 6  (...)' -> [5, 1, 6]"""
    head = read.split("  (")[0]
    return [int(t.split(" ×")[0].strip()) for t in head.split(" + ")]


print("--- the data ---")
ks = [s[0] for s in SYSTEMS]
check(ks == ["tally", "egypt", "babylon", "roman", "chinese", "maya", "arabic"], f"seven systems in order: {', '.join(ks)}")
check(all(len(s) == 9 and all(s) for s in SYSTEMS),
      "each with base, place value, zero, when and where, reach, a note and a source")
check(all(1 <= p <= 9999 for p in PRESETS) and PRESETS == sorted(PRESETS), f"presets {PRESETS} inside 1..9999, rising")
check(len(LINE) == 2 and all(len(c) == 4 and all(c) for c in LINE), "two line cards, each with a note and a source")
check(len(REFS) >= 6, f"{len(REFS)} references")
check(chinese(2026) == "二千零二十六" and chinese(10) == "十" and chinese(110) == "一百一十" and chinese(1001) == "一千零一"
      and chinese(2010) == "二千零一十" and chinese(1000) == "一千", "the Chinese rule here: 二千零二十六, 十, 一百一十, 一千零一, 二千零一十")
check(roman(1999) == "MCMXCIX" and roman(3999) == "MMMCMXCIX" and roman(4) == "IV", "the Roman rule here: MCMXCIX, MMMCMXCIX, IV")

print("--- the writers ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#nsvg")

    # every number, in one call, so the sweep is cheap
    allw = pg.evaluate("()=>{const o={}; for(let m=1;m<=9999;m++) o[m]=window.__num(m); return o;}")
    bad = {k: [] for k in ks}
    for m in range(1, 10000):
        w, mk = allw[str(m)]["write"], allw[str(m)]["marks"]
        if w["roman"] != roman_read(m):
            bad["roman"].append((m, w["roman"]))
        if w["chinese"].split(":")[0] != chinese(m):
            bad["chinese"].append((m, w["chinese"]))
        d20 = digits(m, 20)
        if parse_places(w["maya"]) != d20:
            bad["maya"].append((m, w["maya"]))
        elif mk["maya"]["circles"] != sum(v % 5 for v in d20) or mk["maya"]["rects"] != sum(v // 5 for v in d20) \
                or mk["maya"]["ellipses"] != d20.count(0) or mk["maya"]["h"] != 56 * len(d20):
            bad["maya"].append((m, "marks", mk["maya"]))
        d60 = digits(m, 60)
        if parse_places(w["babylon"]) != d60:
            bad["babylon"].append((m, w["babylon"]))
        elif mk["babylon"]["chevrons"] != sum(v // 10 for v in d60) \
                or mk["babylon"]["paths"] - mk["babylon"]["chevrons"] != sum(v % 10 for v in d60) \
                or mk["babylon"]["rects"] != d60.count(0):
            bad["babylon"].append((m, "marks", mk["babylon"]))
        dd = [int(c) for c in str(m)]
        want = [f"{c} {nm}" for c, nm in zip([int(c) for c in f"{m:04d}"], ["lotus flowers", "coils of rope", "heel bones", "strokes"]) if c]
        if w["egypt"] != ", ".join(want):
            bad["egypt"].append((m, w["egypt"]))
        elif mk["egypt"]["paths"] + mk["egypt"]["lines"] != sum(dd):
            bad["egypt"].append((m, "marks", mk["egypt"]))
        g, r = divmod(m, 5)
        shown = min(g, 40)
        lines = shown * 5 + (r if g <= 40 else 0)
        if not w["tally"].startswith(f"{g} group{'' if g == 1 else 's'} of five" + (f" and {r}" if r else "")) or mk["tally"]["lines"] != lines:
            bad["tally"].append((m, w["tally"], mk["tally"]))
        names = ["thousands", "hundreds", "tens", "ones"][4 - len(dd):]
        if w["arabic"] != ", ".join(f"{c} {nm}" for c, nm in zip(dd, names)):
            bad["arabic"].append((m, w["arabic"]))
    for k in ks:
        check(not bad[k], f"{k}: all 9,999 numbers agree with the conversion here" + ("" if not bad[k] else f", {len(bad[k])} differ"),
              str(bad[k][:3]))
    check(allw["2026"]["write"]["roman"] == "MMXXVI" and allw["4096"]["write"]["roman"].startswith("IV with a bar"),
          "2026 is MMXXVI; 4096 is IV under a bar, then XCVI")
    check(allw["60"]["write"]["babylon"].startswith("1 × 60 + 0") and "empty place" in allw["60"]["write"]["babylon"],
          "60 in Babylonian is one wedge and an empty place")
    check(allw["20"]["write"]["maya"].startswith("1 × 20 + 0") and "shell" in allw["20"]["write"]["maya"],
          "20 in Maya is a dot over a shell")
    check(allw["2026"]["write"]["chinese"].startswith("二千零二十六"), "2026 in Chinese is 二千零二十六")
    check(allw["7"]["marks"]["tally"]["lines"] == 7 and allw["7"]["write"]["tally"].startswith("1 group of five and 2"), "7 tallies: one group of five and two, seven lines")

    print("--- the drawing ---")
    st = pg.evaluate("()=>window.__num()")
    check(st["view"] == "written" and st["n"] == 2026, "opens on 2026, written")
    rows = pg.evaluate("()=>[...document.querySelectorAll('#nsvg g[data-k]')].map(g=>g.dataset.k)")
    check(rows == ks, f"seven rows drawn: {', '.join(rows)}")
    vb = pg.evaluate("()=>document.querySelector('#nsvg').getAttribute('viewBox').split(' ').map(Number)")
    # nothing drawn past the right edge
    over = pg.evaluate("""()=>{const svg=document.querySelector('#nsvg'); const W=svg.viewBox.baseVal.width; let n=0;
      for(const e of svg.querySelectorAll('line,circle,rect,path,text')){ const b=e.getBBox(); if(b.x+b.width>W+1 && e.tagName!=='rect') n++; } return n;}""")
    check(over == 0, "nothing drawn past the right edge", f"{over} elements")
    # hovering a row names it on the card
    pg.evaluate("()=>{const g=document.querySelector('#nsvg g[data-k=\"maya\"]'); g.dispatchEvent(new PointerEvent('pointerover',{bubbles:true}));}")
    pg.wait_for_timeout(100)
    check(pg.inner_text("#nameTxt") == "Maya numerals" and "5 × 20^2" in pg.inner_text("#numTxt"), "hovering the Maya row puts it on the card with its reading")
    # a preset
    pg.click('#presets button[data-p="365"]')
    pg.wait_for_timeout(100)
    st = pg.evaluate("()=>window.__num()")
    check(st["n"] == 365 and pg.input_value("#num") == "365" and "CCCLXV" in pg.text_content("#nsvg"), "the 365 preset rewrites the rows: CCCLXV")
    # tally overflow message for a big number
    pg.fill("#num", "9999")
    pg.wait_for_timeout(100)
    check("more marks" in pg.text_content("#nsvg") and "9,799 more marks" in pg.text_content("#nsvg"), "9999 tallies: 200 drawn and 9,799 more marks")

    print("--- the line ---")
    pg.click('#views button[data-v="line"]')
    pg.fill("#num", "10")
    pg.wait_for_timeout(100)
    L, R = 70, 980 - 70

    def marker():
        return pg.evaluate("()=>window.__num()")["marker"]

    def frac():
        return (marker() - L) / (R - L)

    check(abs(frac() - 0.5) < 0.002, f"read logarithmically, 10 sits at {frac() * 100:.1f}% of the line")
    check("50.0% of the way along" in pg.inner_text("#numTxt"), "and the card says 50.0%")
    pg.evaluate("()=>{const s=document.getElementById('blend'); s.value=100; s.dispatchEvent(new Event('input'));}")
    pg.wait_for_timeout(100)
    check(abs(frac() - 0.1) < 0.002, f"read linearly, at {frac() * 100:.1f}%")
    check("fully linear" in pg.inner_text("#numTxt"), "the card says fully linear")
    pg.evaluate("()=>{const s=document.getElementById('blend'); s.value=50; s.dispatchEvent(new Event('input'));}")
    pg.wait_for_timeout(100)
    check(abs(frac() - 0.3) < 0.002, f"half and half, at {frac() * 100:.1f}%")
    check("50% log, 50% linear" in pg.inner_text("#numTxt"), "the card names the blend")
    ticks = pg.evaluate("()=>[...document.querySelectorAll('#nsvg text')].map(t=>t.textContent)")
    check("ten sits 30% of the way along" in ticks, "the tell-tale line reads 30%")
    pg.fill("#num", "365")
    pg.wait_for_timeout(100)
    check(marker() is None and "off this line" in pg.text_content("#nsvg"), "365 is off a line to 100, and the page says so")
    check(not errs, "no script errors", "; ".join(errs))
    br.close()

print("--- the copy ---")
html = PAGE.read_text()
check("—" not in html, "no em dashes")
check("__" not in re.sub(r"<script.*?</script>", "", html, flags=re.S), "no placeholders left")

print()
if fails:
    print(f"{len(fails)} FAILED:")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("all checks passed")
