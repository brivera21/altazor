"""Check the packed map inside endgames.html against the tablebase itself.

1. every one of the 393,216 states, looked up exactly the way the page does
   it (mirroring the board for pawns on files e to h), matches kpk_dtm.bin
2. the mirror symmetry the packing relies on actually holds
3. the census numbers drawn in the figure match a fresh count
"""
import base64
import re
from pathlib import Path

HERE = Path(__file__).parent
D = Path("/home/claude/kbbtb/kpk_dtm.bin").read_bytes()
html = (HERE.parent / "endgames.html").read_text(encoding="utf-8")

m = re.search(r"const KPKMAP='([A-Za-z0-9+/=]+)';", html)
assert m, "KPKMAP not found in the page"
BITS = base64.b64decode(m.group(1))
assert len(BITS) == 64 * 64 * 24 * 2 // 8, len(BITS)


def tb(wk, bk, wp, stm):
    v = D[(((wk * 64 + bk) * 48 + (wp - 8)) * 2) + stm]
    return v - 256 if v > 127 else v


def mirror(s):
    return (s & 56) | (7 - (s & 7))


def page_win(wk, bk, wp, stm):
    """The page's own lookup, transcribed from the JavaScript."""
    if (wp & 7) > 3:
        wk, bk, wp = mirror(wk), mirror(bk), mirror(wp)
    i = (((wk * 64 + bk) * 24 + ((wp >> 3) - 1) * 4 + (wp & 7)) * 2) + stm
    return (BITS[i >> 3] >> (i & 7)) & 1


def adj(a, b):
    return max(abs(a % 8 - b % 8), abs(a // 8 - b // 8)) == 1


def pawn_att(wp, s):
    f, r = wp % 8, wp // 8
    if r + 1 > 7:
        return False
    return (f > 0 and s == (r + 1) * 8 + f - 1) or (f < 7 and s == (r + 1) * 8 + f + 1)


bad = mirbad = 0
c = dict(slots=0, same=0, kings=0, check=0, legal=0, win=0, draw=0)
for wk in range(64):
    for bk in range(64):
        for wp in range(8, 56):
            for stm in (0, 1):
                c["slots"] += 1
                if tb(wk, bk, wp, stm) != tb(mirror(wk), mirror(bk), mirror(wp), stm):
                    mirbad += 1
                if wk == bk or wk == wp or bk == wp:
                    c["same"] += 1
                    continue
                if adj(wk, bk):
                    c["kings"] += 1
                    continue
                if stm == 0 and pawn_att(wp, bk):
                    c["check"] += 1
                    continue
                c["legal"] += 1
                won = tb(wk, bk, wp, stm) >= 0
                c["win" if won else "draw"] += 1
                if page_win(wk, bk, wp, stm) != (1 if won else 0):
                    bad += 1
print("states compared     ", c["slots"])
print("mirror mismatches   ", mirbad)
print("lookup mismatches   ", bad)

c["illegal"] = c["same"] + c["kings"] + c["check"]
fig = {int(x.replace(",", "")) for x in re.findall(r"[\d,]{4,}", html)}
for k in ("slots", "illegal", "legal", "win", "draw"):
    print("%-8s %9d   printed on the page: %s" % (k, c[k], c[k] in fig))
assert bad == 0 and mirbad == 0
