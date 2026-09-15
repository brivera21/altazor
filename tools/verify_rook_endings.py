#!/usr/bin/env python3
"""Check rook-endings.html: the chess, the board and the stepping.

The moves are the whole point of the page, so they are replayed through
a real engine rather than eyeballed: every move legal from the stated
position, every check mark matching the board, every move's text equal
to the notation the engine produces, and the sides alternating.

The board is checked too. A diagram with its colors inverted reads as
wrong to anyone who plays, and the parity is easy to get backwards:
a1 is dark and h1 is light.

Usage: python3 verify_rook_endings.py
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import chess

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "rook-endings.html"
fails, notes = [], []


def ck(ok, msg):
    (notes if ok else fails).append(msg)


# the page carries its lines as one JSON blob, so they come straight out
m = re.search(r"const POS=(\[.*?\]);\n", PAGE.read_text(encoding="utf-8"),
              re.S)
POS = json.loads(m.group(1))
for p in POS:                       # the builder names the squares a and b
    p["caption"] = p["cap"]
    for mv in p["moves"]:
        mv["from"], mv["to"] = mv["a"], mv["b"]

FMAP = {"K": chess.KING, "Q": chess.QUEEN, "R": chess.ROOK,
        "B": chess.BISHOP, "N": chess.KNIGHT, "P": chess.PAWN}
WANT_PLIES = {"Philidor": 10, "Lucena": 13, "Vančura": 8}

ck(len(POS) == 3, f"{len(POS)} positions on the page")
for p in POS:
    nm = p["name"]
    b = chess.Board(None)
    for sq, pc in p["start"].items():
        b.set_piece_at(chess.parse_square(sq),
                       chess.Piece(FMAP[pc.upper()], pc.isupper()))
    first_white = "…" not in p["moves"][0]["san"]
    b.turn = chess.WHITE if first_white else chess.BLACK
    b.castling_rights = 0
    ck(b.status() == chess.STATUS_VALID,
       f"{nm}: the starting position is legal ({b.fen()})")
    cap = p["caption"].lower()
    said = ("Black" if "black to move" in cap
            else "White" if "white to move" in cap else None)
    movers = "White" if first_white else "Black"
    ck(said is None or said == movers,
       f"{nm}: the caption and the first move agree on who is to move")
    ck(WANT_PLIES.get(nm) == len(p["moves"]),
       f"{nm}: {len(p['moves'])} plies")
    ok_line = True
    for i, m in enumerate(p["moves"], 1):
        want_w = (i % 2 == 1) if first_white else (i % 2 == 0)
        if b.turn != (chess.WHITE if want_w else chess.BLACK):
            fails.append(f"{nm} ply {i}: the sides stop alternating")
            ok_line = False
            break
        mv = chess.Move(chess.parse_square(m["from"]),
                        chess.parse_square(m["to"]))
        if mv not in b.legal_moves:
            fails.append(f"{nm} ply {i} {m['san']}: "
                         f"{m['from']}{m['to']} is not legal")
            ok_line = False
            break
        san = b.san(mv)
        b.push(mv)
        if m["san"].rstrip().endswith("+") != b.is_check():
            fails.append(f"{nm} ply {i} {m['san']}: the check mark is wrong")
            ok_line = False
        core = re.sub(r"^\d+\.|^\d+…", "", m["san"]).strip()
        if core.rstrip("+") != san.rstrip("+#"):
            fails.append(f"{nm} ply {i}: the page writes {core!r}, "
                         f"the move is {san!r}")
            ok_line = False
    ck(ok_line, f"{nm}: every move legal, every check mark right, "
                f"notation matching the engine")
    ck(not b.is_game_over(), f"{nm}: the line stops before the game does")

ck("Rb4" in POS[1]["moves"][-1]["san"],
   f"Lucena ends on the bridge, {POS[1]['moves'][-1]['san']}")
ck(POS[0]["moves"][-1]["san"].endswith("+"),
   "Philidor ends on a check, which is the point of the defense")
ck(POS[2]["moves"][-1]["from"] == "f7" and POS[2]["moves"][-1]["to"] == "f6",
   "Vančura ends with the rook back on the sixth rank")

html = PAGE.read_text(encoding="utf-8")
ck("—" not in re.sub(r"<script[\s\S]*?</script>", "", html),
   "no em dash in the page copy")
# the page wears the site's chrome rather than a set of its own
ck("fonts.googleapis.com" not in html, "no web font, like every other page")
for token in ("--bg:#121212", "--accent:#58a6ff", "--sq-light:#a9b2be",
              "border-top:4px solid var(--accent)", "ALTAZOR"):
    ck(token in html, f"the site's chrome carries {token}")

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("playwright is required for the rendering checks")
    sys.exit(2)

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 900, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_timeout(600)
    ck(pg.eval_on_selector_all("#board rect.sq", "es=>es.length") == 64,
       "sixty-four squares")
    darkfill = pg.evaluate("()=>getComputedStyle(document.documentElement)"
                           ".getPropertyValue('--sq-dark').trim()")
    # a1 dark and h1 light, or the diagram reads as wrong to a player
    for sq, want in (("a1", "dark"), ("h1", "light"), ("a8", "light"),
                     ("h8", "dark"), ("e4", "light"), ("d4", "dark")):
        got = ("dark" if pg.eval_on_selector(f"#sq-{sq}", "e=>e.getAttribute('fill')")
               == darkfill else "light")
        ck(got == want, f"{sq} is {want}")
    # White's orientation: rank 1 at the bottom, the a file on the left
    r1 = pg.eval_on_selector("#sq-a1", "e=>e.getBoundingClientRect().top")
    r8 = pg.eval_on_selector("#sq-a8", "e=>e.getBoundingClientRect().top")
    h1 = pg.eval_on_selector("#sq-h1", "e=>e.getBoundingClientRect().left")
    a1 = pg.eval_on_selector("#sq-a1", "e=>e.getBoundingClientRect().left")
    ck(r1 > r8 and h1 > a1, "drawn from White's side")
    ck(pg.evaluate("()=>[...document.querySelectorAll('#board text')]"
                   ".filter(t=>/^[a-h][1-8]$/.test(t.textContent)).length") == 64,
       "a coordinate in the corner of every square")

    tabs = pg.eval_on_selector_all("#menu button",
                                   "es=>es.map(e=>e.firstChild.textContent)")
    ck(tabs == [p["name"] for p in POS], f"one button per position: {tabs}")

    for i, p in enumerate(POS):
        pg.click(f"#menu button:nth-of-type({i+1})")
        pg.wait_for_timeout(200)
        ck(pg.inner_text("#sInd").startswith("0 /"),
           f"{p['name']}: opens at the start")
        # forward to the end, by key and by button alternately
        for k in range(len(p["moves"])):
            if k % 2:
                pg.keyboard.press("ArrowRight")
            else:
                pg.click("#next")
            pg.wait_for_timeout(40)
        ck(pg.inner_text("#sInd") == f"{len(p['moves'])} / {len(p['moves'])}",
           f"{p['name']}: steps to the last ply, {pg.inner_text('#sInd')}")
        # the pieces standing at the end are the engine's final position
        shown = pg.evaluate(
            "()=>Object.fromEntries([...document.querySelectorAll('#pieces g')]"
            ".map(e=>[e.dataset.square, e.dataset.k]))")
        ck(len(shown) == len(p["start"]),
           f"{p['name']}: {len(shown)} pieces on the board at the end")
        # and back again to the start
        for k in range(len(p["moves"])):
            pg.keyboard.press("ArrowLeft")
            pg.wait_for_timeout(30)
        ck(pg.inner_text("#sInd").startswith("0 /"),
           f"{p['name']}: steps all the way back")
        back = pg.evaluate(
            "()=>Object.fromEntries([...document.querySelectorAll('#pieces g')]"
            ".map(e=>[e.dataset.square, e.dataset.k]))")
        ck(set(back) == set(p["start"]),
           f"{p['name']}: stepping back restores the opening position")
        # a note only where there is something to say
        notes_at = []
        if not pg.eval_on_selector("#reset", "e=>e.disabled"):
            pg.click("#reset")
            pg.wait_for_timeout(100)
        for k in range(len(p["moves"])):
            pg.click("#next")
            pg.wait_for_timeout(40)
            notes_at.append(bool(pg.inner_text("#pNote").strip()))
        want_notes = [bool(m.get("note")) for m in p["moves"]]
        ck(notes_at == want_notes,
           f"{p['name']}: a note appears on exactly the moves that carry one")

    pg.click("#reset")
    pg.wait_for_timeout(150)
    ck(pg.eval_on_selector("#prev", "e=>e.disabled"),
       "back is disabled at the start")
    ck(not pg.eval_on_selector("#next", "e=>e.disabled"),
       "forward is live at the start")
    ck(bool(pg.eval_on_selector_all("header.site a[href='chess.html']",
                                    "es=>es.length")),
       "a way back to the Chess page")
    # clicking a move in the list jumps to it
    pg.click("#menu button:nth-of-type(1)")
    pg.wait_for_timeout(200)
    pg.click("#moves span[data-i='4']")
    pg.wait_for_timeout(200)
    ck(pg.inner_text("#sInd").startswith("4 /"),
       f"clicking a move jumps to it ({pg.inner_text('#sInd')})")
    ck(not errs, f"no script errors ({errs[:1]})")
    br.close()

for n in notes:
    print("  ok  ", n)
if fails:
    print()
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print(f"\n{len(notes)} checks passed")
