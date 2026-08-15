"""Pack the king-and-pawn-against-king table into a bitmap for the web page.

Source: kpk_dtm.bin, built by /home/claude/kbbtb/tbkpk_dtm.c (retrograde
level-by-level, so its values are exact plies to promotion). Only the
win/draw bit is needed here.

Only pawns on files a to d are stored. The page mirrors the whole position
left to right for files e to h, which halves the payload.

bit index = (((wk*64 + bk)*24 + wpi)*2) + stm      stm 0 = White to move
wpi       = (rank-2)*4 + file                       file 0..3, rank 2..7
Output: kpk_map.b64 (the bitmap) and kpk_map.json (the census counts).
"""
import base64
import json
from pathlib import Path

SRC = Path("/home/claude/kbbtb/kpk_dtm.bin")
HERE = Path(__file__).parent

D = SRC.read_bytes()


def tb(wk, bk, wp, stm):
    v = D[(((wk * 64 + bk) * 48 + (wp - 8)) * 2) + stm]
    return v - 256 if v > 127 else v


def adj(a, b):
    return max(abs(a % 8 - b % 8), abs(a // 8 - b // 8)) == 1


def pawn_att(wp, s):
    f, r = wp % 8, wp // 8
    if r + 1 > 7:
        return False
    return (f > 0 and s == (r + 1) * 8 + f - 1) or (f < 7 and s == (r + 1) * 8 + f + 1)


NBITS = 64 * 64 * 24 * 2
bits = bytearray(NBITS // 8)
for wk in range(64):
    for bk in range(64):
        for wp in range(8, 56):
            if wp % 8 > 3:
                continue
            wpi = (wp // 8 - 1) * 4 + (wp % 8)
            for stm in (0, 1):
                if wk == bk or wk == wp or bk == wp:
                    continue
                if adj(wk, bk):
                    continue
                if stm == 0 and pawn_att(wp, bk):
                    continue
                if tb(wk, bk, wp, stm) < 0:
                    continue
                i = (((wk * 64 + bk) * 24 + wpi) * 2) + stm
                bits[i >> 3] |= 1 << (i & 7)

(HERE / "kpk_map.b64").write_text(base64.b64encode(bytes(bits)).decode(), encoding="utf-8")

# census over the whole table, both halves of the board
cens = dict(slots=0, same=0, kings=0, check=0, legal=0, win=0, draw=0,
            winW=0, winB=0, drawW=0, drawB=0, legalW=0, legalB=0,
            capture=0, stalemate=0, deepest=0)
for wk in range(64):
    for bk in range(64):
        for wp in range(8, 56):
            for stm in (0, 1):
                cens["slots"] += 1
                if wk == bk or wk == wp or bk == wp:
                    cens["same"] += 1
                    continue
                if adj(wk, bk):
                    cens["kings"] += 1
                    continue
                if stm == 0 and pawn_att(wp, bk):
                    cens["check"] += 1
                    continue
                cens["legal"] += 1
                cens["legalW" if stm == 0 else "legalB"] += 1
                v = tb(wk, bk, wp, stm)
                if v >= 0:
                    cens["win"] += 1
                    cens["winW" if stm == 0 else "winB"] += 1
                    cens["deepest"] = max(cens["deepest"], v)
                else:
                    cens["draw"] += 1
                    cens["drawW" if stm == 0 else "drawB"] += 1
                if stm == 1:
                    moves = 0
                    for df in (-1, 0, 1):
                        for dr in (-1, 0, 1):
                            if not df and not dr:
                                continue
                            f, r = bk % 8 + df, bk // 8 + dr
                            if not (0 <= f < 8 and 0 <= r < 8):
                                continue
                            t = r * 8 + f
                            if adj(t, wk) or pawn_att(wp, t):
                                continue
                            if t == wp:
                                if not adj(wk, wp):
                                    moves += 1
                                    cens["capture"] += 1
                                continue
                            moves += 1
                    if moves == 0:
                        cens["stalemate"] += 1
cens["illegal"] = cens["same"] + cens["kings"] + cens["check"]
(HERE / "kpk_map.json").write_text(json.dumps(cens, indent=1), encoding="utf-8")
print("wrote kpk_map.b64 and kpk_map.json")
print({k: v for k, v in cens.items() if k in
       ("slots", "illegal", "legal", "win", "draw", "stalemate", "deepest")})
