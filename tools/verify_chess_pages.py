#!/usr/bin/env python3
"""Checks the Chess term pages written from tools/chess_pages_data.py: the
six piece pages, Tactics, Checkmates and Fundamental Terms, and the terms
added to Opening, Middlegame and Endgame Terms.

  the data     every term has the supplied seven fields (numbers allowed on
               the diagram boards), real squares, known mark kinds, a legend
               for every kind it uses, and a caption of 60 words or fewer
  the boards   every position is legal; lines of moves replay; every line
               quoted in a caption replays from its position
  the claims   what each caption says about its position, checked on the
               board: the fork forks, the pin pins, the mate mates, the
               passed pawn is passed, the counts are the counts
  the engine   where a caption says a line wins, draws or mates, Stockfish
               agrees (skipped when Stockfish is not installed)
  the pages    in a browser every term draws its FEN, marks and counts, a1
               dark, no script errors, nothing wider than a phone
  the copy     no em dashes, American spelling, each page listed where it
               belongs, and Board Intuition without its piece vision section
"""

import json
import pathlib
import re
import shutil
import subprocess
import sys

import chess
import chess.engine

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from chess_pages_data import PAGES as DATA, leaper_counts, ray_counts, KNIGHT, KING, DIAG, ORTHO  # noqa: E402
from build_chess_terms import NEW, TERMS_RE  # noqa: E402

FAILS = []


def check(ok, what):
    print(("  ok   " if ok else "  FAIL ") + what)
    if not ok:
        FAILS.append(what)


def page_terms(fname):
    block = TERMS_RE.search((ROOT / fname).read_text(encoding="utf-8")).group(0)
    return json.loads(block[len("const TERMS = "):-1])


FILE_OF = {key: f for f, _t, _s, _d, key in NEW}
FILE_OF.update({k: k for k in DATA if k.endswith(".html")})
KINDS = {"subject", "target", "plan", "zone"}
SQUARES = {f + r for f in "abcdefgh" for r in "12345678"}


def position(term, data_term):
    """The board for a term, with the side to move, or None for a diagram."""
    if "moves" in data_term:
        b = chess.Board()
        for t in data_term["moves"].split():
            b.push_san(t)
        return b
    t = term["turn"]
    if "White to move" in t:
        side = " w"
    elif "Black to move" in t:
        side = " b"
    else:
        return None
    return chess.Board(term["fen"] + side + " - - 0 1")


def _play(b, text):
    for tok in text.split():
        tok = re.sub(r"^\d+\.(\.\.)?", "", tok).strip(",")
        if not tok or tok in ("mate",):
            continue
        b.push_san(tok.replace("!", "").replace("?", ""))
    return b


def replay(board, line):
    """Every alternative in a caption's move line, played from the board.

    "X and Y" means X, then Y whatever the reply: Y is checked against every
    legal reply, and the board returned is after X alone.
    """
    out = []
    for alt in line.split(" or "):
        parts = alt.split(" and ")
        b = _play(board.copy(), parts[0])
        for later in parts[1:]:
            for m in list(b.legal_moves):
                y = b.copy()
                y.push(m)
                _play(y, later)
        out.append(b)
    return out


# ------------------------------------------------------------ the data
print("--- the data ---")
boards = {}
for key, terms in DATA.items():
    fname = FILE_OF[key]
    on_page = {t["name"]: t for t in page_terms(fname)}
    for d in terms:
        t = on_page.get(d["name"])
        check(t is not None, f"{fname} / {d['name']}: on the page")
        if not t:
            continue
        keys = set(t) - {"numbers"}
        check(keys == {"name", "tagline", "fen", "turn", "marks", "legend", "body"},
              f"{fname} / {d['name']}: the seven fields")
        check(all(s in SQUARES for s in t["marks"]) and set(t["marks"].values()) <= KINDS,
              f"{fname} / {d['name']}: marks on real squares, known kinds")
        used = set(t["marks"].values()) | ({"subject", "zone"} & {k for k, _ in t["legend"]} if "numbers" in t else set())
        check({k for k, _ in t["legend"]} == used or ("numbers" in t and {k for k, _ in t["legend"]} <= KINDS),
              f"{fname} / {d['name']}: the legend names exactly the kinds used")
        words = len(" ".join([t["tagline"]] + [p for p in t["body"] if not p.startswith("|")]).split())
        check(words <= 60, f"{fname} / {d['name']}: {words} words, a caption")
        check("—" not in json.dumps(t, ensure_ascii=False), f"{fname} / {d['name']}: no em dashes")
        b = position(t, d)
        if b is not None:
            check(b.board_fen() == t["fen"], f"{fname} / {d['name']}: the page's FEN is the position")
            ok = b.status() in (chess.STATUS_VALID,)
            check(ok, f"{fname} / {d['name']}: a legal position ({b.status()!r})" if not ok else
                  f"{fname} / {d['name']}: a legal position")
            for p in t["body"]:
                if p.startswith("|"):
                    try:
                        replay(b, p[1:])
                        ok = True
                    except ValueError as e:
                        ok = False
                    check(ok, f"{fname} / {d['name']}: {p[1:]} replays")
        boards[d["name"]] = (b, t)


def B(name):
    return boards[name][0].copy()


def T(name):
    return boards[name][1]


def passed(b, s, color):
    f, r = chess.square_file(s), chess.square_rank(s)
    ahead = range(r + 1, 8) if color else range(0, r)
    for ff in (f - 1, f, f + 1):
        if 0 <= ff <= 7:
            for rr in ahead:
                p = b.piece_at(chess.square(ff, rr))
                if p and p.piece_type == chess.PAWN and p.color != color:
                    return False
    return True


def pawns_on(b, color, files):
    return [s for s in b.pieces(chess.PAWN, color) if chess.FILE_NAMES[chess.square_file(s)] in files]


S = chess.parse_square

# ------------------------------------------------------------ the claims
print("--- the claims ---")
b = B("Passed pawn")
check(passed(b, S("d5"), True), "Passed pawn: nothing black on c, d or e ahead of d5")
b = B("Protected passed pawn")
check(passed(b, S("d5"), True) and S("c4") in b.attackers(True, S("d5")), "Protected passed pawn: passed, and c4 guards it")
b = B("Connected passed pawns")
check(passed(b, S("c5"), True) and passed(b, S("d5"), True), "Connected passed pawns: both passed, on neighboring files")
b = B("Outside passed pawn")
check(passed(b, S("a4"), True) and len(b.pieces(chess.PAWN, True)) == len(b.pieces(chess.PAWN, False)) + 1,
      "Outside passed pawn: a4 is passed, and the kingside is level")
b = B("Backward pawn")
check(not [s for s in pawns_on(b, False, "ce") if chess.square_rank(s) >= 5] and b.piece_at(S("d5")) is not None
      and not pawns_on(b, True, "d"), "Backward pawn: no black pawn behind d6 on c or e, d5 occupied, the d-file half-open for White")
b = B("Isolated pawn")
check(not pawns_on(b, True, "ce") and b.piece_at(S("d4")) == chess.Piece(chess.PAWN, True), "Isolated pawn: no white pawn on c or e")
b = B("Doubled pawns")
check(sorted(chess.square_name(s) for s in pawns_on(b, False, "c")) == ["c6", "c7"], "Doubled pawns: two black pawns on the c-file")
b = B("Advanced pawn")
check({S("d6"), S("f6")} <= set(b.attacks(S("e5"))), "Advanced pawn: e5 attacks d6 and f6")
b = B("Minority attack")
x = b.copy(); x.push_san("bxc6"); x.push_san("bxc6")
check(not pawns_on(x, False, "bd") or all(chess.square_rank(s) < 5 for s in pawns_on(x, False, "bd")),
      "Minority attack: after bxc6 bxc6 the c6 pawn has no neighbor behind it")
check(not pawns_on(x, True, "c"), "Minority attack: and the c-file is half-open for White")
x = b.copy(); x.push_san("bxc6") if False else None
x = b.copy(); x.turn = chess.BLACK; x.push_san("cxb5"); x.push_san("axb5")
check(not pawns_on(x, False, "ce"), "Minority attack: after ...cxb5 axb5 the d-pawn is isolated")
b = B("Pawn race")
(x,) = replay(b, "1.a6 h3 2.a7 h2 3.a8=Q h1=Q")
check(S("h1") in x.attacks(S("a8")) and x.turn == chess.WHITE, "Pawn race: both queen, and the new queen on a8 hits h1")
b = B("Pawn roller")
check(b.piece_at(S("d4")) == b.piece_at(S("e4")) == chess.Piece(chess.PAWN, True), "Pawn roller: d4 and e4 side by side")
b = B("Pawn storm")
check(chess.square_file(b.king(True)) <= 2 and chess.square_file(b.king(False)) >= 6, "Pawn storm: kings on opposite wings")
b = B("Push")
check(set(b.attacks(S("d4"))) == {S("c5"), S("e5")}, "Push: d4 covers c5 and e5")
b = B("Breakthrough")
x1, x2 = replay(b, "1.b6 axb6 2.c6 bxc6 3.a6 or 1.b6 cxb6 2.a6 bxa6 3.c6")
check(all(len(x.pieces(chess.PAWN, True)) == 1 and passed(x, next(iter(x.pieces(chess.PAWN, True))), True) for x in (x1, x2)),
      "Breakthrough: either way one white pawn is left, and it is passed")
b = B("Underpromotion")
x = b.copy(); x.push_san("e8=N+")
check(x.is_check() and S("c7") in x.attacks(S("e8")), "Underpromotion: e8=N gives check and attacks the queen")
x = b.copy(); x.push_san("e8=Q"); x.push_san("Qc1#")
check(x.is_checkmate(), "Underpromotion: e8=Q allows ...Qc1 mate")

counts = {"Knight mobility": leaper_counts(KNIGHT), "King mobility": leaper_counts(KING),
          "Bishop mobility": ray_counts(DIAG), "Rook mobility": ray_counts(ORTHO),
          "Queen mobility": ray_counts(ORTHO + DIAG), "Rook behind its own pawn": ray_counts(ORTHO, blocked={"e4"})}


def brute(steps, slide, blocked=()):
    out = {}
    for s in chess.SQUARES:
        name = chess.square_name(s)
        if name in blocked:
            continue
        n = 0
        for df, dr in steps:
            f, r = chess.square_file(s) + df, chess.square_rank(s) + dr
            while 0 <= f <= 7 and 0 <= r <= 7 and chess.square_name(chess.square(f, r)) not in blocked:
                n += 1
                if not slide:
                    break
                f += df
                r += dr
        out[name] = n
    return out


want = {"Knight mobility": brute(KNIGHT, False), "King mobility": brute(KING, False),
        "Bishop mobility": brute(DIAG, True), "Rook mobility": brute(ORTHO, True),
        "Queen mobility": brute(ORTHO + DIAG, True), "Rook behind its own pawn": brute(ORTHO, True, {"e4"})}
for name, w in want.items():
    check(T(name)["numbers"] == w, f"{name}: every square's count matches an independent count")
check(want["Knight mobility"]["a1"] == 2 and want["Knight mobility"]["d4"] == 8, "Knight mobility: two in the corner, eight in the center")
check(want["King mobility"]["a1"] == 3 and want["King mobility"]["a4"] == 5 and want["King mobility"]["d4"] == 8, "King mobility: three, five, eight")
check(want["Bishop mobility"]["a4"] == 7 and all(want["Bishop mobility"][s] == 13 for s in ("d4", "d5", "e4", "e5")),
      "Bishop mobility: seven on the rim, thirteen in the center")
check(set(want["Rook mobility"].values()) == {14}, "Rook mobility: fourteen everywhere")
check(want["Queen mobility"]["a1"] == 21 and want["Queen mobility"]["d4"] == 27, "Queen mobility: twenty one and twenty seven")
rp = want["Rook behind its own pawn"]
check(all(rp[s] == 9 for s in ("e1", "e2", "e3")) and min(rp.values()) == 9, "Rook behind its own pawn: e1 to e3 worst, at nine")

b = B("Bishop pair")
wb = list(b.pieces(chess.BISHOP, True))
check(len(wb) == 2 and (chess.square_file(wb[0]) + chess.square_rank(wb[0])) % 2 != (chess.square_file(wb[1]) + chess.square_rank(wb[1])) % 2
      and len(b.pieces(chess.BISHOP, False)) == 1 and len(b.pieces(chess.KNIGHT, False)) == 1,
      "Bishop pair: two white bishops on both colors against bishop and knight")
b = B("Opposite-color bishops")
wb, bb = next(iter(b.pieces(chess.BISHOP, True))), next(iter(b.pieces(chess.BISHOP, False)))
check((chess.square_file(wb) + chess.square_rank(wb)) % 2 != (chess.square_file(bb) + chess.square_rank(bb)) % 2
      and len(b.pieces(chess.PAWN, True)) == len(b.pieces(chess.PAWN, False)) + 1,
      "Opposite-color bishops: the bishops never meet, and White is a pawn up")
b = B("Fianchetto")
check(b.piece_at(S("g2")) == chess.Piece(chess.BISHOP, True) and b.piece_at(S("g3")) == chess.Piece(chess.PAWN, True),
      "Fianchetto: bishop g2 behind pawn g3")
b = B("Spanish bishop")
check(S("f7") in b.attacks(S("b3")), "Spanish bishop: the bishop on b3 reaches f7")
b = B("Pigs on the 7th")
check(sorted(chess.square_name(s) for s in b.pieces(chess.ROOK, True)) == ["d7", "e7"]
      and len(b.pieces(chess.PAWN, True)) == len(b.pieces(chess.PAWN, False)), "Pigs on the 7th: both rooks on the seventh, material level")
b = B("Blind pigs")
(x,) = replay(b, "1.Rxg7+ Kh8 2.Rxh7+ Kg8 3.Rbg7")
check(x.is_checkmate(), "Blind pigs: the line ends in mate")
b = B("Open and half-open files")
check(not pawns_on(b, True, "d") and not pawns_on(b, False, "d") and not pawns_on(b, True, "c") and pawns_on(b, False, "c"),
      "Open and half-open files: d-file empty, c-file only Black's")
b = B("Flight square")
x = b.copy(); x.push_san("Re8+")
check([x.san(m) for m in x.legal_moves] == ["Kh7"] and not x.is_checkmate(), "Flight square: after Re8+ the king has h7, only")
y = b.copy()
y.remove_piece_at(S("h6"))
y.set_piece_at(S("h7"), chess.Piece(chess.PAWN, chess.BLACK))
y.push_san("Re8+")
check(y.is_checkmate(), "Flight square: with the pawn still on h7, Re8 would be mate")
b = B("King hunt")
check(b.is_checkmate() and b.king(False) == S("g1"), "King hunt: mate, with the black king on g1")
b = B("Triangulation")
(x,) = replay(b, "1.Kd2 Ke6 2.Ke2 Kd5 3.Kd3")
check(x.board_fen() == b.board_fen() and x.turn == chess.BLACK, "Triangulation: the same position, with Black to move")

b = B("Double attack")
x = b.copy(); x.push_san("Qd4")
check({S("b4"), S("h4")} <= set(x.attacks(S("d4"))) and not x.attackers(False, S("b4")) and not x.attackers(False, S("h4")),
      "Double attack: Qd4 hits two undefended pieces")
b = B("Fork")
x = b.copy(); x.push_san("Nc7+")
check(x.is_check() and S("a8") in x.attacks(S("c7")), "Fork: Nc7 checks and hits the rook")
b = B("Pin, absolute")
check(b.is_pinned(chess.BLACK, S("c6")), "Pin, absolute: the knight is pinned to the king")
b = B("Pin, relative")
x = b.copy(); x.remove_piece_at(S("f6"))
check(not b.is_pinned(chess.BLACK, S("f6")) and S("d8") in x.attacks(S("g5")), "Pin, relative: legal to move, and the queen stands behind")
b = B("Skewer")
x = b.copy(); x.push_san("Ba4+")
ok = x.is_check() and all((lambda y: (y.push(m), y.is_legal(y.parse_san("Bxe8")))[1])(x.copy()) for m in x.legal_moves)
check(ok, "Skewer: after Ba4+ every king move leaves Bxe8")
b = B("Discovered attack")
x = b.copy(); x.push_san("Nd6+")
check(len(x.checkers()) == 2 and S("b7") in x.attacks(S("d6")), "Discovered attack: double check, and the knight hits the queen")
b = B("X-ray")
(x,) = replay(b, "1.Qxe8+ Rxe8 2.Rxe8")
check(x.is_checkmate(), "X-ray: the line ends in mate")
b = B("Decoy")
x = b.copy(); x.push_san("Rh8+")
check([x.san(m) for m in x.legal_moves] == ["Kxh8"], "Decoy: after Rh8+ the only move is Kxh8")
x.push_san("Kxh8"); x.push_san("Nxf7+")
check(x.is_check() and S("d8") in x.attacks(S("f7")), "Decoy: then Nxf7 checks and hits the queen")
b = B("Attraction")
(x,) = replay(b, "9.Qd8+ Kxd8 10.Bg5+ Kc7 11.Bd8")
check(x.is_checkmate(), "Attraction: the line ends in mate")
b = B("Clearance")
(x,) = replay(b, "1.Nf6+ gxf6 2.Qh7")
check(x.is_checkmate(), "Clearance: the line ends in mate")
b = B("Overloaded piece")
x = b.copy(); x.push_san("Qxb6"); x.push_san("Qxb6"); x.push_san("Re8+")
check(x.is_checkmate(), "Overloaded piece: if the queen takes back, Re8 is mate")
b = B("Desperado")
check(all(b.piece_at(m.from_square).piece_type == chess.ROOK for m in b.legal_moves), "Desperado: White's only moves are rook moves")
x = b.copy(); x.push_san("Rh7+"); x.push_san("Kxh7")
check(x.is_stalemate(), "Desperado: taking the rook is stalemate")
b = B("Windmill")
(x,) = replay(b, "26.Rxg7+ Kh8 27.Rxf7+ Kg8 28.Rg7+ Kh8 29.Rxb7+ Kg8 30.Rg7+ Kh8 31.Rg5+ Kh7 32.Rxh5")
check(not x.pieces(chess.QUEEN, False) and len(x.pieces(chess.PAWN, False)) < len(b.pieces(chess.PAWN, False)),
      "Windmill: Black's queen and pawns gone by the end")
b = B("Zwischenzug")
x = b.copy(); x.push_san("Qh4")
y = x.copy(); y.push_san("Bf3"); y.push_san("Qxf2#")
check(y.is_checkmate(), "Zwischenzug: after ...Qh4, Bf3 would allow ...Qxf2 mate")
b = B("Scholar's mate")
check(b.is_checkmate(), "Scholar's mate: mate")
b = B("Smothered mate")
(x,) = replay(b, "1.Qg8+ Rxg8 2.Nf7")
check(x.is_checkmate() and all(x.piece_at(s) and x.piece_at(s).color == chess.BLACK for s in (S("g8"), S("g7"), S("h7"))),
      "Smothered mate: mate, the king boxed in by its own pieces")
b = B("Tempo")
check(S("d5") in b.attacks(S("c3")), "Tempo: the knight attacks the queen")
b = B("Domination")
b2 = b.copy(); b2.turn = chess.BLACK
nm = [m for m in b2.legal_moves if m.from_square == S("a8")]
check(nm and all(b2.is_attacked_by(chess.WHITE, m.to_square) for m in nm) and not b.is_attacked_by(chess.WHITE, S("a8")),
      "Domination: every knight move lands on a covered square, and the knight itself is not attacked")
b = B("Illegal move")
x = chess.Board(b.board_fen() + " w K - 0 1")
y = x.copy(); y.remove_piece_at(S("c4"))
check((chess.Move.from_uci("e1g1") not in x.legal_moves and chess.Move.from_uci("e1g1") in y.legal_moves),
      "Illegal move: castling is illegal only because the bishop covers f1")
b = B("Interposing")
x = b.copy(); x.pop()
check(x.is_check() and S("b4") in b.attacks(S("c3")) and not b.is_check(), "Interposing: c3 answers the check and attacks the bishop")
b = B("Blunder")
(x,) = replay(b, "5.Nxf7?? Qxg2 6.Rf1 Qxe4+ 7.Be2 Nf3")
check(x.is_checkmate(), "Blunder: the line ends in mate")
b = B("Brilliant move")
(x,) = replay(b, "9...Kxd8 10.Bg5+ Kc7 11.Bd8")
check(x.is_checkmate(), "Brilliant move: the line ends in mate")
b = B("Hole")
check(not [s for s in pawns_on(b, False, "df") if chess.square_rank(s) >= 5], "Hole: no black pawn left behind e5 on d or f")
b = B("Strong square")
check(b.piece_at(S("e5")) == chess.Piece(chess.KNIGHT, True) and S("d4") in b.attackers(True, S("e5"))
      and not [s for s in pawns_on(b, False, "df") if chess.square_rank(s) >= 5], "Strong square: knight on e5, backed by d4, beyond any black pawn")
b = B("Weakness")
check(not pawns_on(b, False, "b") and all(chess.square_rank(s) < 5 for s in pawns_on(b, False, "d")) and not pawns_on(b, True, "c"),
      "Weakness: nothing can guard c6 with a pawn, and White has the file")
b = B("Tension")
check(S("e5") in b.attacks(S("d4")) and S("d4") in b.attacks(S("e5")), "Tension: d4 and e5 attack each other")
b = B("Blocked position")
check(all(b.piece_at(S(a)) and b.piece_at(S(c)) for a, c in (("d5", "d6"), ("e4", "e5"))), "Blocked position: the center pawns are locked")
b = B("Control of the center")
check(b.piece_at(S("d4")) and b.piece_at(S("e4")), "Control of the center: pawns on d4 and e4")
b = B("Waiting move")
x = b.copy(); x.push_san("h6")
check(x.board_fen() == B("Zugzwang").board_fen(), "Waiting move: 25...h6 leads to the zugzwang position")

# ------------------------------------------------------------ the pages
print("--- the pages ---")
from playwright.sync_api import sync_playwright  # noqa: E402

GLYPH = {"k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟"}
files = sorted(set(FILE_OF.values()))
with sync_playwright() as p:
    br = p.chromium.launch()
    for fname in files:
        pg = br.new_page(viewport={"width": 1280, "height": 1000})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto((ROOT / fname).as_uri())
        pg.wait_for_selector("#board .sq")
        terms = page_terms(fname)
        bad = []
        for i, t in enumerate(terms):
            s = pg.evaluate("i => window.__terms({pick:i})", i)
            want = sorted(f"{chess.square_name(sq)}:{'w' if pc.color else 'b'}{GLYPH[pc.symbol().lower()]}"
                          for sq, pc in chess.Board(t["fen"] + " w - - 0 1").piece_map().items())
            if not (s["squares"] == 64 and s["a1"] == "sq d" and sorted(s["pieces"]) == want
                    and sorted(s["marks"]) == sorted(f"{k}:{v}" for k, v in t["marks"].items())
                    and s["numbers"] == t.get("numbers", {})):
                bad.append(t["name"])
        check(not bad, f"{fname}: all {len(terms)} terms draw their FEN, marks and counts, a1 dark"
              + (f" (not: {', '.join(bad)})" if bad else ""))
        check(not errs, f"{fname}: no script errors" + (f" ({errs[0]})" if errs else ""))
        pg.close()
        ph = br.new_page(viewport={"width": 390, "height": 900})
        ph.goto((ROOT / fname).as_uri())
        ph.wait_for_selector("#board .sq")
        check(ph.evaluate("document.documentElement.scrollWidth - innerWidth") <= 0, f"{fname}: nothing wider than a phone")
        ph.close()
    br.close()

# the engine runs after the browser: python-chess's engine and Playwright
# both want the event loop, and the browser has to start first
# ------------------------------------------------------------ the engine
print("--- the engine ---")
sf = shutil.which("stockfish") or ("/usr/games/stockfish" if pathlib.Path("/usr/games/stockfish").exists() else None)
if not sf:
    print("  (Stockfish not installed, engine checks skipped)")
else:
    eng = chess.engine.SimpleEngine.popen_uci(sf)

    def ev(b, secs=1.5):
        return eng.analyse(b, chess.engine.Limit(time=secs))["score"].white()

    def cp(sc):
        return 100000 if sc.is_mate() and sc.mate() > 0 else -100000 if sc.is_mate() else sc.score()

    def after(name, line, secs=1.5):
        (x,) = replay(B(name), line)
        return ev(x, secs)

    for name, line, lo in [("Outside passed pawn", "", 300), ("Pawn race", "1.a6", 300),
                           ("Breakthrough", "1.b6", 300), ("Underpromotion", "1.e8=N+", 300),
                           ("Decoy", "1.Rh8+", 300), ("Double attack", "1.Qd4", 300),
                           ("Fork", "1.Nc7+", 300), ("Skewer", "1.Ba4+", 300),
                           ("Discovered attack", "1.Nd6+", 300), ("Overloaded piece", "1.Qxb6", 300),
                           ("Domination", "", 300),
                           ("Deflection", "18.Qg4 Qb5 19.Qc4 Qd7 20.Qc7 Qb5 21.a4 Qxa4 22.Re4 Qb5 23.Qxb7", 300),
                           ("Triangulation", "", 300)]:
        s = after(name, line) if line else ev(B(name))
        check(cp(s) >= lo, f"{name}: Stockfish has White winning after {line or 'the position'} ({s})")
    x = B("Deflection")
    best = eng.analyse(x, chess.engine.Limit(time=2))["pv"][0]
    check(x.san(best) == "Qg4", f"Deflection: 18.Qg4 is Stockfish's choice too ({x.san(best)})")
    x = B("Triangulation"); x.turn = chess.BLACK
    check(cp(ev(x)) >= 300, "Triangulation: with Black to move it is lost for Black")
    s = ev(B("Opposite-color bishops"), 3)
    check(abs(cp(s)) < 80, f"Opposite-color bishops: a pawn up, and still level ({s})")
    s = after("Desperado", "1.Rh7+")
    check(abs(cp(s)) < 50, f"Desperado: 1.Rh7+ holds the draw ({s})")
    for name in ("X-ray", "Clearance", "Smothered mate", "Blind pigs"):
        s = ev(B(name))
        check(s.is_mate() and s.mate() > 0, f"{name}: Stockfish finds the mate ({s})")
    s = ev(B("Pigs on the 7th"), 3)
    check(cp(s) >= 80, f"Pigs on the 7th: White better with material level ({s})")
    # the inaccuracy: 5...Nxd5 against the main move 5...Na5, from Black's side
    x = B("Inaccuracy"); x.pop()
    y1 = x.copy(); y1.push_san("Na5"); y2 = x.copy(); y2.push_san("Nxd5")
    deep = lambda y: cp(eng.analyse(y, chess.engine.Limit(depth=22))["score"].white())
    d = deep(y2) - deep(y1)
    check(d >= 30, f"Inaccuracy: at depth 22, 5...Nxd5 gives White {d} centipawns more than 5...Na5")
    s = after("Blunder", "5.Nxf7")
    check(cp(s) <= -300, f"Blunder: after 5.Nxf7 Black is winning ({s})")
    # zugzwang: every White move loses
    z = B("Zugzwang")
    worst = max(cp(ev((lambda y: (y.push(m), y)[1])(z.copy()), 0.4)) for m in z.legal_moves)
    check(worst <= -250, f"Zugzwang: every White move leaves Black winning (best for White {worst})")
    eng.quit()

# ------------------------------------------------------------ the copy
print("--- the copy ---")
am = subprocess.run([sys.executable, str(ROOT / "tools" / "americanize.py"), "--check", *files],
                    capture_output=True, text=True, cwd=ROOT).stdout
check("0 files would change" in am, "americanize.py finds nothing to change")
idx = (ROOT / "chess.html").read_text(encoding="utf-8")
fund = re.search(r"<h2>Fundamentals</h2>(.*?)</div>", idx, re.S).group(1)
for f, t, col, *_ in NEW:
    if col == "Fundamentals":
        check(f'href="{f}">{t}<' in fund, f"{t} is listed under Fundamentals")
end = re.search(r"<h2>Endgames</h2>(.*?)</div>", idx, re.S).group(1)
check('href="checkmates.html">Checkmates<' in end, "Checkmates is listed under Endgames")
intu = (ROOT / "intuition.html").read_text(encoding="utf-8")
check('"Piece vision"' not in intu, "Board Intuition no longer carries the piece vision topics")

print()
print("everything squares" if not FAILS else f"{len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
