#!/usr/bin/env python3
"""Checks the three Chess terms pages.

  the arrays    each page's TERMS array is byte for byte the one supplied, and
                every term has its seven fields, real squares and known marks
  the positions each FEN is a legal diagram, and the move sequences quoted in
                the text are legal from it. This only reports. The analysis
                was verified before it arrived and is not to be edited here.
  the boards    in a browser, every term of every page draws the pieces its FEN
                says, on the squares it says, with a1 dark and h1 light
  the copy      no em dashes, nothing loaded from outside, American spelling
"""

import pathlib
import re
import subprocess
import sys

import chess

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from build_chess_terms import PAGES, UPLOADS, TERMS_RE  # noqa: E402

FAILS = []


def check(ok, what):
    print(("  ok   " if ok else "  FAIL ") + what)
    if not ok:
        FAILS.append(what)


def js_array(block):
    """The TERMS array as Python data. It is written as strict JSON."""
    import json
    return json.loads(block[len("const TERMS = "):-1])


GLYPH = {"k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟"}
SQUARES = {f + r for f in "abcdefgh" for r in "12345678"}


def side_of(turn):
    t = turn.lower()
    if "either side" in t:
        return None
    if "white to move" in t:
        return chess.WHITE
    if "black to move" in t:
        return chess.BLACK
    return "?"


def play(fen, side, line):
    """Replay a line of SAN from a diagram. Returns the board, or the move
    that would not play."""
    b = chess.Board(fen + (" w" if side else " b") + " - - 0 1")
    for tok in re.sub(r"\d+\.(\.\.)?", " ", line).split():
        try:
            b.push_san(tok)
        except ValueError:
            return tok
    return b


terms = {}
print("--- the arrays ---")
for fname, title, section, desc, upload in PAGES:
    built = TERMS_RE.search((ROOT / fname).read_text(encoding="utf-8")).group(0)
    given = TERMS_RE.search((UPLOADS / upload).read_text(encoding="utf-8")).group(0)
    check(built == given, f"{fname}: TERMS array identical to the one supplied ({len(given):,} chars)")
    arr = js_array(built)
    terms[fname] = arr
    for t in arr:
        keys = {"name", "tagline", "fen", "turn", "marks", "legend", "body"}
        check(set(t) == keys, f"{fname} / {t.get('name')}: the seven fields, nothing more")
        check(all(s in SQUARES for s in t["marks"]), f"{fname} / {t['name']}: every mark is a real square")
        kinds = set(t["marks"].values())
        check(kinds <= {"subject", "target", "plan"}, f"{fname} / {t['name']}: marks are subject, target or plan")
        check({k for k, _ in t["legend"]} == kinds, f"{fname} / {t['name']}: legend names exactly the marks used")

print("--- the positions (report only) ---")
for fname, arr in terms.items():
    for t in arr:
        side = side_of(t["turn"])
        sides = [chess.WHITE, chess.BLACK] if side is None else [side]
        for s in sides:
            b = chess.Board(t["fen"] + (" w" if s else " b") + " - - 0 1")
            status = b.status()
            ok = status in (chess.STATUS_VALID, chess.STATUS_BAD_CASTLING_RIGHTS)
            check(ok, f"{t['name']}: legal diagram with {'White' if s else 'Black'} to move"
                      + ("" if ok else f" ({status!r})"))

# the lines the text quotes, played from the diagrams
EG = {t["name"]: t for t in terms["endgame-terms.html"]}
MG = {t["name"]: t for t in terms["middlegame-terms.html"]}
z = EG["Mutual zugzwang"]["fen"]
end = play(z, chess.WHITE, "1.Kf5 Kf7 2.e5 Ke7 3.e6 Ke8 4.Kf6 Kf8 5.e7+ Ke8 6.Ke6")
check(isinstance(end, chess.Board) and end.is_stalemate(),
      "Mutual zugzwang: 1.Kf5 Kf7 2.e5 Ke7 3.e6 Ke8 4.Kf6 Kf8 5.e7+ Ke8 6.Ke6 is legal and ends in stalemate")
for line in ("1.Kd5 Kd7", "1.Kf5 Kf7"):
    check(isinstance(play(z, chess.WHITE, line), chess.Board), f"Mutual zugzwang: {line} is legal")
bk = chess.Board(z + " b - - 0 1")
got = sorted(chess.square_name(m.to_square) for m in bk.legal_moves)
check(got == ["d7", "d8", "e8", "f7", "f8"],
      f"Mutual zugzwang: with Black to move his king has exactly d7, d8, e8, f7, f8 (found {', '.join(got)})")
for bm, wm in zip(["Kd7", "Kd8", "Ke8", "Kf7", "Kf8"], ["Kf6", "Ke6", "Ke6", "Kd6", "Ke6"]):
    r = play(z, chess.BLACK, f"1...{bm} 2.{wm}")
    check(isinstance(r, chess.Board), f"Mutual zugzwang: 1...{bm} 2.{wm} is legal")
check(isinstance(play(EG["Two weaknesses"]["fen"], chess.WHITE, "1.h5"), chess.Board),
      "Two weaknesses: h4-h5 is legal")
check(isinstance(play(MG["Outpost"]["fen"], chess.BLACK, "1...Bxd5 2.exd5"), chess.Board),
      "Outpost: 1...Bxd5 2.exd5 is legal")
check(isinstance(play(MG["Hook"]["fen"], chess.WHITE, "1.h5"), chess.Board), "Hook: h4-h5 is legal")
check(isinstance(play(MG["Lever"]["fen"], chess.WHITE, "1.b4"), chess.Board), "Lever: b2-b4 is legal")
check(isinstance(play(MG["Prophylaxis"]["fen"], chess.WHITE, "9.h3"), chess.Board), "Prophylaxis: 9.h3 is legal")

print("--- the boards ---")
from playwright.sync_api import sync_playwright  # noqa: E402
with sync_playwright() as p:
    br = p.chromium.launch()
    for fname, arr in terms.items():
        pg = br.new_page(viewport={"width": 1280, "height": 1000})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto((ROOT / fname).as_uri())
        pg.wait_for_selector("#board .sq")
        for i, t in enumerate(arr):
            s = pg.evaluate("i => window.__terms({pick:i})", i)
            want = sorted(f"{chess.square_name(sq)}:{'w' if pc.color else 'b'}{GLYPH[pc.symbol().lower()]}"
                          for sq, pc in chess.Board(t["fen"] + " w - - 0 1").piece_map().items())
            check(s["squares"] == 64 and s["a1"] == "sq d" and s["h1"] == "sq l",
                  f"{fname} / {t['name']}: 64 squares, a1 dark, h1 light")
            check(sorted(s["pieces"]) == want, f"{fname} / {t['name']}: the board draws the FEN ({len(want)} pieces)")
            check(sorted(s["marks"]) == sorted(f"{k}:{v}" for k, v in t["marks"].items()),
                  f"{fname} / {t['name']}: {len(t['marks'])} marked squares where the array says")
            check(s["legend"] == len(t["legend"]) and s["paras"] == len(t["body"]) and s["selected"] == i,
                  f"{fname} / {t['name']}: legend, {len(t['body'])} paragraphs, its chip lit")
        pg.evaluate("() => window.__terms({pick:0})")
        pg.keyboard.press("ArrowLeft")
        last = pg.evaluate("() => window.__terms()")["current"]
        pg.keyboard.press("ArrowRight")
        first = pg.evaluate("() => window.__terms()")["current"]
        check(last == len(arr) - 1 and first == 0, f"{fname}: the arrow keys wrap both ways")
        check(not errs, f"{fname}: no script errors" + (f" ({errs[0]})" if errs else ""))
        pg.close()
    br.close()

print("--- the copy ---")
for fname, *_ in PAGES:
    h = (ROOT / fname).read_text(encoding="utf-8")
    check("—" not in h, f"{fname}: no em dashes")
    check(not re.search(r'<(script|link|img)[^>]+(src|href)="https?:', h), f"{fname}: nothing loaded from outside")
am = subprocess.run([sys.executable, str(ROOT / "tools" / "americanize.py"), "--check",
                     *[f for f, *_ in PAGES]], capture_output=True, text=True, cwd=ROOT).stdout
check("0 files would change" in am, "americanize.py finds nothing to change")
sec = (ROOT / "chess.html").read_text(encoding="utf-8")
cols = re.search(r"<h2>Openings</h2>(.*?)<h2>Middle Games</h2>(.*?)<h2>Endgames</h2>(.*?)</div>", sec, re.S)
check('href="opening-terms.html">Opening Terms<' in cols.group(1), "Opening Terms sits under Openings")
check('href="middlegame-terms.html">Middlegame Terms<' in cols.group(2), "Middlegame Terms sits under Middle Games")
check('href="endgame-terms.html">Endgame Terms<' in cols.group(3), "Endgame Terms sits under Endgames")

print()
print("everything squares" if not FAILS else f"{len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
