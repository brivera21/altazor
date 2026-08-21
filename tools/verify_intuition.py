"""Check intuition.html: the mobility counts, and that the board draws them.

The mobility topics are the only ones on the page that assert a number for
every square, so they are the ones worth checking against an independent
count. Each count here is computed a second time, by brute force over the
board, rather than by calling the generator's own helper.

Usage: python3 verify_intuition.py
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
PAGE = HERE.parent / "intuition.html"
FILES = "abcdefgh"
fails = []


def name(f, r):
    return FILES[f] + str(r)


def brute(dirs, blocked=(), slide=True):
    """Independent count: walk every ray from every square."""
    out = {}
    for f in range(8):
        for r in range(1, 9):
            if name(f, r) in blocked:
                continue
            n = 0
            for df, dr in dirs:
                ff, rr = f + df, r + dr
                while 0 <= ff <= 7 and 1 <= rr <= 8 and name(ff, rr) not in blocked:
                    n += 1
                    if not slide:
                        break
                    ff += df
                    rr += dr
            out[name(f, r)] = n
    return out


DIAG = ((1, 1), (1, -1), (-1, 1), (-1, -1))
ORTHO = ((1, 0), (-1, 0), (0, 1), (0, -1))
KNIGHT = ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2))
KING = tuple((df, dr) for df in (-1, 0, 1) for dr in (-1, 0, 1) if df or dr)

EXPECT = {
    "knight": brute(KNIGHT, slide=False),
    "king": brute(KING, slide=False),
    "bishop": brute(DIAG),
    "rook": brute(ORTHO),
    "rookpawn": brute(ORTHO, blocked={"e4"}),
}

# Facts that must hold, stated independently of any code above.
CLAIMS = [
    ("knight", "two in the corner", lambda d: d["a1"] == 2),
    ("knight", "eight in the center", lambda d: d["d4"] == 8),
    ("king", "three in the corner", lambda d: d["a1"] == 3),
    ("king", "eight in the middle", lambda d: d["d4"] == 8),
    ("bishop", "seven in the corner", lambda d: d["a1"] == 7),
    ("bishop", "thirteen on each of the four center squares",
     lambda d: all(d[s] == 13 for s in ("d4", "d5", "e4", "e5"))),
    ("bishop", "rings of 7, 9, 11, 13",
     lambda d: sorted(set(d.values())) == [7, 9, 11, 13]),
    ("bishop", "560 over the whole board", lambda d: sum(d.values()) == 560),
    ("bishop", "never more than 13 of its 32 squares",
     lambda d: max(d.values()) == 13),
    ("rook", "fourteen from every square",
     lambda d: set(d.values()) == {14}),
    ("rook", "896 over the whole board", lambda d: sum(d.values()) == 896),
    ("rookpawn", "e4 itself is not counted", lambda d: "e4" not in d),
    ("rookpawn", "63 squares counted", lambda d: len(d) == 63),
    ("rookpawn", "49 squares are untouched at fourteen",
     lambda d: sum(1 for v in d.values() if v == 14) == 49),
    ("rookpawn", "e1, e2 and e3 are the worst, at nine",
     lambda d: d["e1"] == d["e2"] == d["e3"] == 9),
    ("rookpawn", "in front of the pawn it is ten",
     lambda d: all(d[s] == 10 for s in ("e5", "e6", "e7", "e8"))),
    ("rookpawn", "nothing falls below nine", lambda d: min(d.values()) == 9),
]

print("--- the counts ---")
for topic, claim, test in CLAIMS:
    ok = test(EXPECT[topic])
    print(f"  {'ok  ' if ok else 'FAIL'} {topic:9} {claim}")
    if not ok:
        fails.append(f"{topic}: {claim} does not hold")

print("--- what the page ships ---")
html = PAGE.read_text(encoding="utf-8")
m = re.search(r"const TOPICS\s*=\s*(\[.*?\]);\s*\n", html, re.S)
if not m:
    print("could not find the topic table in the page")
    sys.exit(1)
topics = json.loads(m.group(1))
by_id = {t["id"]: t for t in topics}

for tid, want in EXPECT.items():
    if tid not in by_id:
        fails.append(f"the page has no {tid!r} topic")
        continue
    got = by_id[tid].get("numbers")
    if got != want:
        diff = [k for k in set(got or {}) | set(want) if (got or {}).get(k) != want.get(k)]
        fails.append(f"{tid}: the page disagrees on {len(diff)} squares, "
                     f"first few {sorted(diff)[:6]}")
    else:
        print(f"  ok   {tid:9} {len(got)} squares match the independent count")

if by_id.get("rookpawn", {}).get("pieces", {}).get("e4") != "wP":
    fails.append("rookpawn: no white pawn is drawn on e4")
else:
    print("  ok   rookpawn  a white pawn stands on e4")

order = [t["id"] for t in topics]
for a, b in (("king", "bishop"), ("bishop", "rook"), ("rook", "rookpawn")):
    if a in order and b in order and order.index(a) > order.index(b):
        fails.append(f"{b} comes before {a} in the menu")
print(f"  ok   order      {' then '.join(['knight', 'king', 'bishop', 'rook', 'rookpawn'])}")

try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": 1200, "height": 1200})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(PAGE.resolve().as_uri())
        pg.wait_for_timeout(500)
        for tid in ("bishop", "rook", "rookpawn"):
            i = order.index(tid)
            pg.click(f'.menu button[data-i="{i}"]')
            pg.wait_for_timeout(350)
            got = pg.evaluate("""() => ({
              nums: [...document.querySelectorAll('#numbers text')].map(t=>t.textContent),
              fills: new Set([...document.querySelectorAll('rect.sq')]
                       .map(r=>r.getAttribute('fill'))).size,
              pieces: document.querySelectorAll('#pieces text').length })""")
            want_n = sorted(str(v) for v in EXPECT[tid].values())
            if sorted(got["nums"]) != want_n:
                fails.append(f"{tid}: the board shows {len(got['nums'])} numbers, "
                             f"expected {len(want_n)}")
            if any(f is None or "NaN" in f for f in
                   pg.evaluate("()=>[...document.querySelectorAll('rect.sq')]"
                               ".map(r=>r.getAttribute('fill'))")):
                fails.append(f"{tid}: a square has no usable fill")
            print(f"  ok   {tid:9} draws {len(got['nums'])} numbers in "
                  f"{got['fills']} distinct fills, {got['pieces']} piece(s)")
        if errs:
            fails.append(f"javascript errors: {errs}")
        br.close()
except ImportError:
    print("  playwright not available, skipped the render pass")

print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("all checks pass")
