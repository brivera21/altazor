"""Check endgame-threshold.html: the arithmetic, the three readouts and the copy.

  the sums     from a queen, two rooks and four minors (9, 5, 3) there are
               exactly twelve ways to trade eighteen or more points; the
               totals 19 and 22 each arise twice, and both pairs differ by a
               queen against three minors; 24, 27, 29 and 30 cannot be
               reached; the page's table lists the same twelve rows
  the page     fourteen pieces, seven a side; a click takes a piece off and
               a second click puts it back; the points rule turns at 13,
               the ratio rule at four traded, and the tapered phase counts
               1, 2 and 4 out of 24; the two presets where the rules
               contradict each other, and the queen against three minors
               at nine points each
  the copy     no em dashes, no dependencies, American spellings (by
               americanize.py)
"""
import re
import sys
from collections import Counter
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "endgame-threshold.html"
fails = []


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


print("--- the sums ---")
ways = [(9 * q + 5 * r + 3 * m, q, r, m) for q, r, m in product(range(2), range(3), range(5))]
past = sorted(w for w in ways if w[0] >= 18)
check(len(past) == 12, f"twelve ways to trade eighteen or more of the thirty-one points ({len(past)})")
check(sum(w[0] == 18 for w in past) == 1 and [w for w in past if w[0] == 18][0][1:] == (1, 0, 3), "exactly eighteen has one solution, the queen and three minors")
cnt = Counter(w[0] for w in past)
twins = sorted(t for t, n in cnt.items() if n > 1)
check(twins == [19, 22], f"the totals that repeat are 19 and 22 ({twins})")
ok = True
for t in twins:
    a, b = [w[1:] for w in past if w[0] == t]
    d = tuple(x - y for x, y in zip(a, b))
    if d not in ((1, 0, -3), (-1, 0, 3)):
        ok = False
check(ok, "both repeats differ by a queen against three minors")
gaps = [t for t in range(18, 32) if t not in cnt]
check(gaps == [24, 27, 29, 30], f"the unreachable totals are 24, 27, 29 and 30 ({gaps})")

html = PAGE.read_text(encoding="utf-8")
rows = re.findall(r"<tr[^>]*><td>(.*?)</td><td class=\"n\">(\d+)</td><td>(.*?)</td><td class=\"n\">(\d+)</td></tr>", html)


def parse(cell):
    q = 1 if "Q" in cell else 0
    r = int(re.search(r"(\d?)R", cell).group(1) or 1) if "R" in cell else 0
    m = int(re.search(r"(\d)m", cell).group(1)) if "m" in cell else 0
    return q, r, m


table = sorted((int(t), *parse(a)) for a, t, _, _ in rows)
check(table == past, "the table lists the same twelve rows as this checker")
check(all(int(t) + int(rp) == 31 and parse(a) == tuple(x - y for x, y in zip((1, 2, 4), parse(b))) for a, t, b, rp in rows), "every row's traded and remaining columns are complements adding to 31")
tw = [int(t) for t in re.findall(r'<tr class="twin"><td>.*?</td><td class="n">(\d+)</td>', html)]
check(sorted(tw) == [19, 19, 22, 22], "the four twin rows are marked")

print("--- the page ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1000, "height": 1200})
    errs = []
    pg.on("pageerror", lambda x: errs.append(str(x)))
    reqs = []
    pg.on("request", lambda r: reqs.append(r.url))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#side-b .pc")

    def st():
        return pg.evaluate("""()=>({
          w: [...document.querySelectorAll('#side-w .pc')].map(b=>!b.classList.contains('gone')),
          b: [...document.querySelectorAll('#side-b .pc')].map(b=>!b.classList.contains('gone')),
          mat: document.getElementById('v-mat').textContent,
          ratio: document.getElementById('v-ratio').textContent,
          points: document.getElementById('x-points').textContent,
          ratioV: document.getElementById('x-ratio').textContent,
          phase: document.getElementById('x-phase').textContent,
          pon: document.getElementById('t-points').classList.contains('on'),
          ron: document.getElementById('t-ratio').classList.contains('on'),
          note: document.getElementById('note').textContent,
          heads: [...document.querySelectorAll('.s-sum')].map(e=>e.textContent),
        })""")

    s = st()
    check(len(s["w"]) == 7 and len(s["b"]) == 7 and all(s["w"]) and all(s["b"]), "fourteen pieces, seven a side, all on the board")
    check(s["mat"] == "31 and 31" and s["ratio"] == "0:7 and 0:7" and s["points"] == "Middlegame" and s["ratioV"] == "Middlegame" and s["phase"] == "0% toward the ending", "opens at 31 points, 0:7 and 0% each side")
    check(s["note"] == "Both sides hold the same material.", "the opening note")
    pg.click("#side-w .pc:nth-child(1)")  # the white queen
    s = st()
    check(not s["w"][0] and s["mat"] == "22 and 31" and s["ratio"] == "1:6 and 0:7" and s["heads"][0] == "2R + 4m, 22 pts" and s["phase"] == "17% toward the ending", "the white queen off: 22 points, 1:6, 2R + 4m, 4 of 24 phase gone")
    check("Black holds 9 points more" in s["note"], "the note: Black holds 9 points more")
    pg.click("#side-w .pc:nth-child(1)")
    s = st()
    check(all(s["w"]) and s["mat"] == "31 and 31", "a second click puts the queen back")
    # points rule turns at 13: 2R + 1m remaining each side
    for c in ("w", "b"):
        for i in (1, 4, 5, 6):  # queen, three minors
            pg.click(f"#side-{c} .pc:nth-child({i})")
    s = st()
    check(s["mat"] == "13 and 13" and s["pon"] and s["points"] == "Endgame" and s["ron"] and s["ratio"] == "4:3 and 4:3", "queen and three minors traded each side: 13 points, 4:3, both rules say endgame")
    check(s["phase"] == "58% toward the ending", "phase: 14 of 24 gone, 58%")
    pg.click("#side-w .pc:nth-child(4)")  # the last white minor back on
    s = st()
    check(s["mat"] == "16 and 13" and not s["pon"] and s["points"] == "Middlegame" and s["ratio"] == "3:4 and 4:3" and not s["ron"], "one minor back: 16 points and 3:4 on one side, both rules say middlegame")
    pg.click('.presets button[data-p="minorsoff"]')
    s = st()
    check(s["mat"] == "19 and 19" and s["ratio"] == "4:3 and 4:3" and not s["pon"] and s["ron"] and "rules disagree" in s["note"] and "heavy" in s["note"], "all minors traded: 19 points, 4:3, the ratio rule alone says endgame")
    pg.click('.presets button[data-p="heavyoff"]')
    s = st()
    check(s["mat"] == "12 and 12" and s["ratio"] == "3:4 and 3:4" and s["pon"] and not s["ron"] and "rules disagree" in s["note"] and "three units" in s["note"], "queen and rooks traded: 12 points, 3:4, the points rule alone says endgame")
    check(s["phase"] == "67% toward the ending", "phase there: 16 of 24 gone, 67%")
    pg.click('.presets button[data-p="qvs3m"]')
    s = st()
    check(s["mat"] == "9 and 9" and s["heads"] == ["Q, 9 pts", "3m, 9 pts"] and s["pon"] and s["ron"] and "level at 9 points" in s["note"] and "queen and the minor piece" in s["note"], "queen against three minors: level at 9, the armies unlike")
    check(s["phase"] == "71% toward the ending", "phase there: 4 + 3 of 24 left, 71%")
    pg.click('.presets button[data-p="rook2m"]')
    s = st()
    check(s["mat"] == "11 and 11" and s["ratio"] == "4:3 and 4:3" and s["phase"] == "67% toward the ending" and s["note"] == "Both sides hold the same material.", "rook and two minors each: 11 points, 4:3")
    pg.click('.presets button[data-p="queensoff"]')
    s = st()
    check(s["mat"] == "22 and 22" and s["ratio"] == "1:6 and 1:6" and s["phase"] == "33% toward the ending", "queens off: 22 points, 1:6, 33%")
    pg.click('.presets button[data-p="start"]')
    s = st()
    check(s["mat"] == "31 and 31" and all(s["w"]) and all(s["b"]), "the starting position restores everything")
    check(all(u.startswith("file:") for u in reqs), "the page loads nothing from the network", "; ".join(u for u in reqs if not u.startswith("file:")))
    check(not errs, "no script errors", "; ".join(errs))
    check(pg.evaluate("()=>document.querySelector('header.site a.brand').textContent") == "ALTAZOR" and pg.evaluate("()=>!!document.querySelector('nav.site a[href=\"chess.html\"]')"), "the site header with the way back to Chess")
    br.close()

print("--- the copy ---")
check("—" not in html, "no em dashes")
check("<script src" not in html and "@import" not in html and 'rel="stylesheet"' not in html, "no dependencies")
check("13 points or less" not in html and "thirteen points or less" in html, "Speelman's rule spelled out in words")
import subprocess
am = subprocess.run([sys.executable, str(ROOT / "tools" / "americanize.py"), "--check"], capture_output=True, text=True).stdout
check("endgame-threshold.html" not in am, "americanize.py finds nothing to change on the page")
check("Endgame preparation" in html and "middle game in chess" in html and "Beyond the basics" in html and "143-145" in html and "53-55" in html, "the sources carry their corrected titles and pages")

print()
if fails:
    print(f"{len(fails)} FAILED:")
    for x in fails:
        print("  -", x)
    sys.exit(1)
print("everything squares")
