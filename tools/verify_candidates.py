#!/usr/bin/env python3
"""Checks candidate-moves.html.

  the chess      the position is the game's, every line is legal, the tree
                 covers every reply Black has in the mating line, 10.Bg5+ is
                 a double check, both branches end in mate, and 9.Qxe4 really
                 leaves nothing guarding e4
  the engine     when Stockfish is installed, each candidate's evaluation is
                 recomputed and must agree with the page's, in sign, in size
                 and in the order of the five
  the research   Gobet's figures as the page draws them
  the page       arrows, board, tree and card at each of the three steps, the
                 keyboard, the charts, the phone, and no script errors
  the copy       no em dashes, nothing loaded from outside, American spelling,
                 and the page is listed under Middle Games
"""

import pathlib
import re
import shutil
import subprocess
import sys

import chess
import chess.engine

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from candidates_data import GAME, CANDIDATES, GOBET  # noqa: E402

PAGE = ROOT / "candidate-moves.html"
FAILS = []


def check(ok, what):
    print(("  ok   " if ok else "  FAIL ") + what)
    if not ok:
        FAILS.append(what)


print("--- the chess ---")
root = chess.Board()
for t in GAME["moves"].split():
    root.push_san(t)
check(root.turn == chess.WHITE and root.fullmove_number == 9, "White to play, move 9")
check(root.piece_at(chess.E4) == chess.Piece(chess.KNIGHT, chess.BLACK),
      "Black's knight has just taken on e4")
b = root.copy()
for t in GAME["played"].split():
    b.push_san(t)
check(True, "the game's own moves, " + GAME["played"] + ", replay")

for c in CANDIDATES:
    for line in c["lines"]:
        b = root.copy()
        try:
            for t in line:
                b.push_san(t)
            ok = True
        except ValueError:
            ok = False
        check(ok, f"{c['san']}: {' '.join(line)} is legal")
        if c["mate"]:
            check(b.is_checkmate(), f"{c['san']}: {' '.join(line)} ends in mate")

b = root.copy()
b.push_san("Qd8+")
replies = sorted(b.san(m) for m in b.legal_moves)
check(replies == ["Kxd8"], f"after 9.Qd8+ Black's only move is Kxd8 ({replies})")
b.push_san("Kxd8")
b.push_san("Bg5+")
check(len(b.checkers()) == 2, "10.Bg5+ checks twice, from the bishop and the rook")
replies = sorted(b.san(m) for m in b.legal_moves)
tree_replies = sorted({line[3] for line in CANDIDATES[0]["lines"]})
check(replies == tree_replies, f"the tree covers every reply to 10.Bg5+ ({replies})")
b = root.copy()
b.push_san("Qxe4")
b.push_san("Qxe4")
check(not b.attackers(chess.WHITE, chess.E4), "after 9.Qxe4 Qxe4 nothing of White's guards e4")

print("--- the research ---")
check([g["cls"] for g in GOBET] == ["Masters", "Experts", "Class A", "Class B"], "four classes, strongest first")
check([g["base"] for g in GOBET] == [3.2, 4.8, 6.5, 4.8], "first moves: 3.2, 4.8, 6.5, 4.8 (Gobet 1998, Table 1)")
check([g["depth"] for g in GOBET] == [5.0, 4.6, 3.7, 2.9], "depth: 5.0, 4.6, 3.7, 2.9 plies")
check(all(a["depth"] > b["depth"] for a, b in zip(GOBET, GOBET[1:])), "depth falls with every class")

print("--- the page ---")
from playwright.sync_api import sync_playwright  # noqa: E402

GLYPH = {"k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟"}


def want_pieces(board):
    return sorted(f"{chess.square_name(s)}:{GLYPH[p.symbol().lower()]}{'w' if p.color else 'b'}"
                  for s, p in board.piece_map().items())


with sync_playwright() as p:
    br = p.chromium.launch()
    pg = br.new_page(viewport={"width": 1400, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#board .pc")
    s = pg.evaluate("()=>__cand()")
    check(s["step"] == 0 and s["arrows"] == ["check", "check", "capture", "attack", "attack"],
          "step 1: five arrows, two checks, a capture, two attacks")
    check(s["pieces"] == want_pieces(root), "the board draws the position, piece for piece")
    check(s["a1"] and s["h1"], "a1 dark, h1 light")
    check(s["treeNodes"] == 6 and not s["evals"], "the tree shows only the five candidates, no verdicts")
    for i, c in enumerate(CANDIDATES):
        pg.evaluate("i=>__cand({pick:i})", i)
        for _ in range(8):
            pg.keyboard.press("ArrowRight")
        s = pg.evaluate("()=>__cand()")
        b = root.copy()
        for t in c["lines"][0]:
            b.push_san(t)
        check(s["pieces"] == want_pieces(b), f"{c['san']}: stepping through ends on the line's last position")
        check(c["eval"].replace("#3", "mate in 3") in s["card"] or ("mate in" in s["card"] and c["mate"]),
              f"{c['san']}: the card gives the verdict at the end of the line")
    s = pg.evaluate("()=>__cand({step:2})")
    check(len(s["evals"]) == 6 and s["evals"].count("#3") == 2, "step 3: every line ends in its evaluation")
    check(not errs, "no script errors" + (f" ({errs[0]})" if errs else ""))
    bars = pg.evaluate("()=>[...document.querySelectorAll('#cBase .bar')].map(b=>+b.getAttribute('width'))")
    check(len(bars) == 4 and abs(bars[2] / bars[0] - 6.5 / 3.2) < 0.01, "the first-move bars are in proportion")
    pg.close()

    ph = br.new_page(viewport={"width": 390, "height": 900})
    ph.goto(PAGE.as_uri())
    ph.wait_for_selector("#board .pc")
    check(ph.evaluate("document.documentElement.scrollWidth - innerWidth") <= 0, "phone: nothing wider than the screen")
    ph.close()
    br.close()

# the engine runs last: python-chess's engine and Playwright each want the
# event loop, and the browser has to be started first
print("--- the engine ---")
sf = shutil.which("stockfish") or ("/usr/games/stockfish" if pathlib.Path("/usr/games/stockfish").exists() else None)
if not sf:
    print("  (Stockfish not installed, engine checks skipped)")
else:
    eng = chess.engine.SimpleEngine.popen_uci(sf)
    got = {}
    for c in CANDIDATES:
        b = root.copy()
        b.push_san(c["san"])
        sc = eng.analyse(b, chess.engine.Limit(depth=22))["score"].white()
        got[c["san"]] = sc
        if c["mate"]:
            # after 9.Qd8+ it is mate in two more White moves
            ok = sc.is_mate() and sc.mate() == c["mate"] - 1
            check(ok, f"{c['san']}: Stockfish finds mate ({sc})")
        else:
            cp = sc.score()
            ok = cp is not None and abs(cp - c["cp"]) <= 80 and (cp > 0) == (c["cp"] > 0)
            check(ok, f"{c['san']}: Stockfish {cp / 100:+.2f}, page {c['eval']}")
    eng.quit()
    order = sorted(CANDIDATES, key=lambda c: -(10000 if c["mate"] else c["cp"]))
    eorder = sorted(CANDIDATES, key=lambda c: -(10000 if got[c["san"]].is_mate()
                                                 else got[c["san"]].score()))
    check([c["san"] for c in order] == [c["san"] for c in eorder],
          "the five rank the same on the page and in the engine")

print("--- the copy ---")
html = PAGE.read_text(encoding="utf-8")
check("—" not in html, "no em dashes")
check(not re.search(r'<(script|link|img)[^>]+(src|href)="https?:', html), "nothing loaded from outside")
am = subprocess.run([sys.executable, str(ROOT / "tools" / "americanize.py"), "--check", PAGE.name],
                    capture_output=True, text=True, cwd=ROOT).stdout
check("0 files would change" in am, "americanize.py finds nothing to change")
sec = (ROOT / "chess.html").read_text(encoding="utf-8")
col = re.search(r"<h2>Middle Games</h2>(.*?)</div>", sec, re.S).group(1)
check('href="candidate-moves.html">Candidate Moves<' in col, "listed under Middle Games")

print()
print("everything squares" if not FAILS else f"{len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
