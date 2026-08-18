#!/usr/bin/env python3
"""Generate intuition.html: Board Intuition, an interactive version of the
"Board intuition trainer" PDF for the Chess section.

One board, 18 topics in three groups (Geography / Piece vision / Endgame
rules). Clicking a topic repaints the board with tiered amber highlights
(smooth CSS transitions), optional piece glyphs, and optional per-square
numbers (mobility heatmaps). Hovering any square shows its coordinate.

Usage: python3 build_intuition.py
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE.parent / "endgames.html"

FILES = "abcdefgh"

# The packed king-and-pawn-against-king table, written by make_kpk_map.py.
KPK_MAP = (HERE / "kpk_map.b64").read_text(encoding="utf-8").strip()
KPK_CENSUS = json.loads((HERE / "kpk_map.json").read_text(encoding="utf-8"))


def sq(f, r):
    return FILES[f] + str(r)


def rank(r):
    return [sq(f, r) for f in range(8)]


def frange(f0, f1, r0, r1):
    return [sq(f, r) for f in range(f0, f1 + 1) for r in range(r0, r1 + 1)]


def diag(f, r, df, dr):
    out = []
    while 0 <= f <= 7 and 1 <= r <= 8:
        out.append(sq(f, r))
        f += df
        r += dr
    return out


def knight_counts():
    out = {}
    for f in range(8):
        for r in range(1, 9):
            n = 0
            for df, dr in ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2),
                           (-2, -1), (-2, 1), (-1, 2)):
                if 0 <= f + df <= 7 and 1 <= r + dr <= 8:
                    n += 1
            out[sq(f, r)] = n
    return out


def king_counts():
    out = {}
    for f in range(8):
        for r in range(1, 9):
            n = 0
            for df in (-1, 0, 1):
                for dr in (-1, 0, 1):
                    if (df or dr) and 0 <= f + df <= 7 and 1 <= r + dr <= 8:
                        n += 1
            out[sq(f, r)] = n
    return out


dark_squares = [sq(f, r) for f in range(8) for r in range(1, 9)
                if (f + r) % 2 == 1]

f7_diags = (diag(0, 2, 1, 1) + diag(4, 8, 1, -1) +   # a2-g8, e8-h5
            diag(0, 7, 1, -1) + diag(4, 1, 1, 1))     # a7-g1, e1-h4
f7_diags = sorted(set(f7_diags) - {"f2", "f7"})

long_diags = sorted(set(diag(0, 1, 1, 1) + diag(0, 8, 1, -1)) -
                    {"b2", "g2", "b7", "g7"})

atk_diags = sorted(set(diag(1, 1, 1, 1) + diag(1, 8, 1, -1)) - {"h7", "h2"})

TOPICS = [
 dict(id="kpk", g="Working Backwards", t="King and pawn against king",
      c="The ending everything else reduces to. One pawn decides the game, "
        "and the kings decide the pawn. Three positions here, played out "
        "one move at a time and checked against a solved table of this "
        "ending: the same centre pawn winning and drawing depending only "
        "on whose turn it is, and a rook pawn that cannot be won at all.",
      strong=[], soft=[],
      legend=[("w", "the squares the pawn attacks"),
              ("wk", "squares the white king covers"),
              ("bk", "squares the black king can still move to"),
              ("chk", "check")],
      steps=[
       dict(pieces=[["bK", "bK", "e7"], ["wK", "wK", "e5"], ["PW", "wP", "e4"]],
            sec="Centre pawn: Black to move, White wins",
            jump=True,
            c="White to move would only draw, but it is Black's turn, and in "
              "this ending the side that has to move first is the side that "
              "gives way. That is the opposition: kings a square apart on the "
              "same file, and whoever must move steps aside."),
       dict(pieces=[["bK", "bK", "e8"], ["wK", "wK", "e5"], ["PW", "wP", "e4"]],
            c="1... Ke8. Black steps back. Kd7 loses the same way, to 2. Kf6."),
       dict(pieces=[["bK", "bK", "e8"], ["wK", "wK", "e6"], ["PW", "wP", "e4"]],
            c="2. Ke6. White takes the opposition again, one rank further up. "
              "Note that the pawn has not moved at all yet; the king goes "
              "first."),
       dict(pieces=[["bK", "bK", "f8"], ["wK", "wK", "e6"], ["PW", "wP", "e4"]],
            c="2... Kf8. Forced sideways."),
       dict(pieces=[["bK", "bK", "f8"], ["wK", "wK", "d7"], ["PW", "wP", "e4"]],
            c="3. Kd7. Now the king controls e8, the queening square, and the "
              "pawn is free to run."),
       dict(pieces=[["bK", "bK", "f7"], ["wK", "wK", "d7"], ["PW", "wP", "e4"]],
            c="3... Kf7."),
       dict(pieces=[["bK", "bK", "f7"], ["wK", "wK", "d7"], ["PW", "wP", "e5"]],
            c="4. e5. Only now does the pawn move, with its king already in "
              "front of it."),
       dict(pieces=[["bK", "bK", "f8"], ["wK", "wK", "d7"], ["PW", "wP", "e5"]],
            c="4... Kf8."),
       dict(pieces=[["bK", "bK", "f8"], ["wK", "wK", "d7"], ["PW", "wP", "e6"]],
            c="5. e6."),
       dict(pieces=[["bK", "bK", "g7"], ["wK", "wK", "d7"], ["PW", "wP", "e6"]],
            c="5... Kg7."),
       dict(pieces=[["bK", "bK", "g7"], ["wK", "wK", "d7"], ["PW", "wP", "e7"]],
            c="6. e7. The black king can never reach e8; it is covered by the "
              "white king."),
       dict(pieces=[["bK", "bK", "f7"], ["wK", "wK", "d7"], ["PW", "wP", "e7"]],
            c="6... Kf7."),
       dict(pieces=[["bK", "bK", "f7"], ["wK", "wK", "d7"], ["QN", "wQ", "e8"]],
            c="7. e8 makes a queen, with check. The mate that follows is the "
              "queen mate below."),
       dict(pieces=[["bK", "bK", "e7"], ["wK", "wK", "e5"], ["PW", "wP", "e4"]],
            sec="Centre pawn: White to move, it is a draw",
            jump=True,
            c="The same position, but now it is White to move, and that "
              "reverses the result. White cannot make progress and the game "
              "is drawn."),
       dict(pieces=[["bK", "bK", "e7"], ["wK", "wK", "d5"], ["PW", "wP", "e4"]],
            c="1. Kd5. White steps aside, hoping Black steps wrong."),
       dict(pieces=[["bK", "bK", "d7"], ["wK", "wK", "d5"], ["PW", "wP", "e4"]],
            c="1... Kd7. Black takes the opposition instead, and keeps taking "
              "it."),
       dict(pieces=[["bK", "bK", "d7"], ["wK", "wK", "d5"], ["PW", "wP", "e5"]],
            c="2. e5. The pawn goes on alone, which is what White must avoid."),
       dict(pieces=[["bK", "bK", "e7"], ["wK", "wK", "d5"], ["PW", "wP", "e5"]],
            c="2... Ke7."),
       dict(pieces=[["bK", "bK", "e7"], ["wK", "wK", "d5"], ["PW", "wP", "e6"]],
            c="3. e6. The pawn is now ahead of its king, the losing pattern."),
       dict(pieces=[["bK", "bK", "e8"], ["wK", "wK", "d5"], ["PW", "wP", "e6"]],
            c="3... Ke8. Straight back, never sideways. Kd8 or Kf8 would "
              "lose."),
       dict(pieces=[["bK", "bK", "e8"], ["wK", "wK", "d6"], ["PW", "wP", "e6"]],
            c="4. Kd6. The last try."),
       dict(pieces=[["bK", "bK", "d8"], ["wK", "wK", "d6"], ["PW", "wP", "e6"]],
            c="4... Kd8. The opposition again."),
       dict(pieces=[["bK", "bK", "d8"], ["wK", "wK", "d6"], ["PW", "wP", "e7"]],
            c="5. e7+. Check, and it looks like the pawn is queening."),
       dict(pieces=[["bK", "bK", "e8"], ["wK", "wK", "d6"], ["PW", "wP", "e7"]],
            c="5... Ke8. The king simply stands in front of the pawn."),
       dict(pieces=[["bK", "bK", "e8"], ["wK", "wK", "e6"], ["PW", "wP", "e7"]],
            c="6. Ke6, and Black has no legal move and is not in check. "
              "Stalemate, a draw. This is the ending the pawn walks into "
              "whenever it arrives before its king."),
       dict(pieces=[["bK", "bK", "a8"], ["wK", "wK", "a6"], ["PW", "wP", "a5"]],
            sec="A rook pawn: always a draw from here",
            jump=True,
            c="A rook pawn is a different animal. White has everything: the "
              "king in front of the pawn, on the sixth rank, with the black "
              "king in the corner. Against any other pawn this wins easily. "
              "Here it is a dead draw whoever moves."),
       dict(pieces=[["bK", "bK", "a8"], ["wK", "wK", "b6"], ["PW", "wP", "a5"]],
            c="1. Kb6. The only way to make room for the pawn."),
       dict(pieces=[["bK", "bK", "b8"], ["wK", "wK", "b6"], ["PW", "wP", "a5"]],
            c="1... Kb8."),
       dict(pieces=[["bK", "bK", "b8"], ["wK", "wK", "b6"], ["PW", "wP", "a6"]],
            c="2. a6."),
       dict(pieces=[["bK", "bK", "a8"], ["wK", "wK", "b6"], ["PW", "wP", "a6"]],
            c="2... Ka8. Back to the corner. The black king only needs these "
              "two squares."),
       dict(pieces=[["bK", "bK", "a8"], ["wK", "wK", "b6"], ["PW", "wP", "a7"]],
            c="3. a7, and Black has no legal move and is not in check. "
              "Stalemate again. There is no edge on the other side of the "
              "a-file for the white king to use, so it can never drive the "
              "black king out of the corner."),
      ],
      notes=["Do put the king in front of the pawn and move it first. A "
             "pawn that runs ahead of its king draws at best.",
             "Do take the opposition: kings on the same file with one "
             "square between them, with the other side to move. The side "
             "that has to move gives way.",
             "Do not push the pawn to give check when a quiet king move "
             "wins. Checking the enemy king toward the corner it wants is "
             "how wins turn into stalemates.",
             "Rook pawns, on the a-file and the h-file, are the exception "
             "to all of it. If the defending king reaches the corner, or "
             "even the square beside it, no amount of technique wins.",
             "Every position and every move here was checked against a "
             "table of this ending computed from scratch, so the verdicts "
             "are exact, not rules of thumb."]),
 dict(id="kpkmap", g="Working Backwards", t="Every placement", map=True,
      strong=[],
      c="The whole ending at once. Put the white king and the pawn wherever "
        "you like, choose who is to move, and every square is painted with "
        "the result if the black king stood on it: green where White wins, "
        "red where Black holds. Pick a piece, then click a square to put it "
        "there, or walk it with the arrow keys. The figure under the board "
        "counts the table whole.",
      legend=[("win", "White wins with the black king here"),
              ("drw", "Black holds the draw"),
              ("ill", "the black king cannot stand here")],
      notes=["It opens on the position from the line above: king e5, pawn "
             "e4, White to move. Of the 55 squares left to the black king, "
             "e7 is the only one that draws.",
             "Switch to Black to move and e7 turns green while d7, f7, d8, "
             "e8 and f8 turn red. Black no longer has to be on the "
             "opposition square, only to be able to step onto it.",
             "Pull the pawn back to e3 with White still to move and every "
             "square goes green. The pawn now has a move to spare, so White "
             "can hand the turn back whenever he likes and take the "
             "opposition himself.",
             "Walk the pawn across to the a-file and the corner fills with "
             "red. A rook pawn gives most of the win away.",
             "Counted whole: 393,216 placements, 331,352 of them legal, and "
             "White wins 222,564 of those, a little over two thirds. Every "
             "square here is read from that table, not from a rule."]),
 dict(id="queenmate", g="Checkmates", t="The queen mate",
      c="A queen and king against a bare king, the shortest of the basic "
        "mates. The queen fences off a rank and a file at once; the king "
        "walks in behind the fence. Black plays the tablebase defence. "
        "Mate in 7.",
      strong=[], soft=[],
      legend=[("w", "the queen's squares"),
              ("wk", "squares the white king covers"),
              ("bk", "squares the black king can still move to"),
              ("chk", "check")],
      steps=[
       dict(pieces=[["bK", "bK", "d5"], ["wK", "wK", "c1"],
                    ["QN", "wQ", "e1"]],
            c="The start: Kc1, Qe1, black king on d5. Black plays the "
              "tablebase defence, the reply that delays mate the longest. "
              "Mate in 7."),
       dict(pieces=[["bK", "bK", "d5"], ["wK", "wK", "c1"],
                    ["QN", "wQ", "e7"]],
            c="1. Qe7. One move takes the seventh rank and the e-file at "
              "once. The black king is now shut into a box of twenty-four "
              "squares and can never leave it."),
       dict(pieces=[["bK", "bK", "d4"], ["wK", "wK", "c1"],
                    ["QN", "wQ", "e7"]],
            c="1... Kd4. Black stays as far from the edges as the box "
              "allows."),
       dict(pieces=[["bK", "bK", "d4"], ["wK", "wK", "b2"],
                    ["QN", "wQ", "e7"]],
            c="2. Kb2. The queen holds the box on her own, so the king is "
              "free to walk in. This is the whole method."),
       dict(pieces=[["bK", "bK", "d5"], ["wK", "wK", "b2"],
                    ["QN", "wQ", "e7"]],
            c="2... Kd5. Marking time; the box does not move."),
       dict(pieces=[["bK", "bK", "d5"], ["wK", "wK", "c3"],
                    ["QN", "wQ", "e7"]],
            c="3. Kc3. Closer. Note that White is in no hurry to check: "
              "checks push the king around, the king traps it."),
       dict(pieces=[["bK", "bK", "c6"], ["wK", "wK", "c3"],
                    ["QN", "wQ", "e7"]],
            c="3... Kc6. Black's only move."),
       dict(pieces=[["bK", "bK", "c6"], ["wK", "wK", "c4"],
                    ["QN", "wQ", "e7"]],
            c="4. Kc4. The kings stand in opposition; b5, c5 and d5 are "
              "gone."),
       dict(pieces=[["bK", "bK", "b6"], ["wK", "wK", "c4"],
                    ["QN", "wQ", "e7"]],
            c="4... Kb6. Forced sideways."),
       dict(pieces=[["bK", "bK", "b6"], ["wK", "wK", "c4"],
                    ["QN", "wQ", "d7"]],
            c="5. Qd7. The queen slides one file over and the box shrinks "
              "again: only the a-file and b-file are left."),
       dict(pieces=[["bK", "bK", "a6"], ["wK", "wK", "c4"],
                    ["QN", "wQ", "d7"]],
            c="5... Ka6. Onto the edge. Playing Ka5 instead loses one "
              "move faster."),
       dict(pieces=[["bK", "bK", "a6"], ["wK", "wK", "c5"],
                    ["QN", "wQ", "d7"]],
            c="6. Kc5. Quiet again, and it takes b6, b5 and b4 away. "
              "Black has exactly one square left, so there is no "
              "stalemate."),
       dict(pieces=[["bK", "bK", "a5"], ["wK", "wK", "c5"],
                    ["QN", "wQ", "d7"]],
            c="6... Ka5. Forced."),
       dict(pieces=[["bK", "bK", "a5"], ["wK", "wK", "c5"],
                    ["QN", "wQ", "b5"]],
            c="7. Qb5, mate. The queen steps right beside the king, "
              "guarded by her own king on c5. Every escape square is a "
              "queen square."),
      ],
      notes=["Black's moves come from a computed tablebase of this "
             "ending, so this is the longest resistance possible.",
             "The danger in this ending is stalemate, not difficulty: "
             "keep the king a square until the mate arrives, and prefer "
             "quiet king moves to checks.",
             "Use the arrows or the arrow keys to play through the line "
             "one move at a time."]),
 dict(id="rookmate", g="Checkmates", t="The rook mate",
      c="A rook and king against a bare king. The rook fences a whole "
        "rank or file at a time; the kings fight for the squares in "
        "between. Black plays the tablebase defence. Mate in 14.",
      strong=[], soft=[],
      legend=[("w", "the rook's squares"),
              ("wk", "squares the white king covers"),
              ("bk", "squares the black king can still move to"),
              ("chk", "check")],
      steps=[
       dict(pieces=[["bK", "bK", "d5"], ["wK", "wK", "c1"],
                    ["RK", "wR", "e1"]],
            c="The start: Kc1, Re1, black king on d5. Black plays the "
              "tablebase defence, the reply that delays mate the "
              "longest. Mate in 14."),
       dict(pieces=[["bK", "bK", "d5"], ["wK", "wK", "b2"],
                    ["RK", "wR", "e1"]],
            c="1. Kb2. The rook cannot do it alone; the king sets out "
              "first."),
       dict(pieces=[["bK", "bK", "d4"], ["wK", "wK", "b2"],
                    ["RK", "wR", "e1"]],
            c="1... Kd4. Black holds the centre."),
       dict(pieces=[["bK", "bK", "d4"], ["wK", "wK", "c2"],
                    ["RK", "wR", "e1"]],
            c="2. Kc2."),
       dict(pieces=[["bK", "bK", "c4"], ["wK", "wK", "c2"],
                    ["RK", "wR", "e1"]],
            c="2... Kc4."),
       dict(pieces=[["bK", "bK", "c4"], ["wK", "wK", "c2"],
                    ["RK", "wR", "d1"]],
            c="3. Rd1. The rook fences the whole d-file; the black "
              "king is cut off on the queenside."),
       dict(pieces=[["bK", "bK", "b4"], ["wK", "wK", "c2"],
                    ["RK", "wR", "d1"]],
            c="3... Kb4."),
       dict(pieces=[["bK", "bK", "b4"], ["wK", "wK", "d3"],
                    ["RK", "wR", "d1"]],
            c="4. Kd3. With the fence up, the king walks out to fight "
              "for squares."),
       dict(pieces=[["bK", "bK", "c5"], ["wK", "wK", "d3"],
                    ["RK", "wR", "d1"]],
            c="4... Kc5. Dropping to the third rank instead loses much "
              "faster."),
       dict(pieces=[["bK", "bK", "c5"], ["wK", "wK", "c3"],
                    ["RK", "wR", "d1"]],
            c="5. Kc3. The kings take opposition."),
       dict(pieces=[["bK", "bK", "b5"], ["wK", "wK", "c3"],
                    ["RK", "wR", "d1"]],
            c="5... Kb5."),
       dict(pieces=[["bK", "bK", "b5"], ["wK", "wK", "d4"],
                    ["RK", "wR", "d1"]],
            c="6. Kd4. The king slips forward on the other diagonal; "
              "this zigzag is the heart of the technique."),
       dict(pieces=[["bK", "bK", "c6"], ["wK", "wK", "d4"],
                    ["RK", "wR", "d1"]],
            c="6... Kc6."),
       dict(pieces=[["bK", "bK", "c6"], ["wK", "wK", "c4"],
                    ["RK", "wR", "d1"]],
            c="7. Kc4. Opposition again."),
       dict(pieces=[["bK", "bK", "b6"], ["wK", "wK", "c4"],
                    ["RK", "wR", "d1"]],
            c="7... Kb6."),
       dict(pieces=[["bK", "bK", "b6"], ["wK", "wK", "c4"],
                    ["RK", "wR", "d6"]],
            c="8. Rd6+. The rook joins with check and takes the sixth "
              "rank; the fence turns sideways."),
       dict(pieces=[["bK", "bK", "b7"], ["wK", "wK", "c4"],
                    ["RK", "wR", "d6"]],
            c="8... Kb7. Pushed a rank back."),
       dict(pieces=[["bK", "bK", "b7"], ["wK", "wK", "b5"],
                    ["RK", "wR", "d6"]],
            c="9. Kb5. The king keeps step."),
       dict(pieces=[["bK", "bK", "c7"], ["wK", "wK", "b5"],
                    ["RK", "wR", "d6"]],
            c="9... Kc7. Attacking the rook."),
       dict(pieces=[["bK", "bK", "c7"], ["wK", "wK", "b5"],
                    ["RK", "wR", "d1"]],
            c="10. Rd1. The rook drops to the far end of the file. The "
              "fence is the file, not the rook."),
       dict(pieces=[["bK", "bK", "b7"], ["wK", "wK", "b5"],
                    ["RK", "wR", "d1"]],
            c="10... Kb7."),
       dict(pieces=[["bK", "bK", "b7"], ["wK", "wK", "b5"],
                    ["RK", "wR", "c1"]],
            c="11. Rc1. The fence advances one file; the box shrinks."),
       dict(pieces=[["bK", "bK", "a7"], ["wK", "wK", "b5"],
                    ["RK", "wR", "c1"]],
            c="11... Ka7. Only the a-file and the b-file are left."),
       dict(pieces=[["bK", "bK", "a7"], ["wK", "wK", "c6"],
                    ["RK", "wR", "c1"]],
            c="12. Kc6. The king comes around to take b7."),
       dict(pieces=[["bK", "bK", "a8"], ["wK", "wK", "c6"],
                    ["RK", "wR", "c1"]],
            c="12... Ka8."),
       dict(pieces=[["bK", "bK", "a8"], ["wK", "wK", "c7"],
                    ["RK", "wR", "c1"]],
            c="13. Kc7. Covers b7 and b8; black has the a-file and "
              "nothing else."),
       dict(pieces=[["bK", "bK", "a7"], ["wK", "wK", "c7"],
                    ["RK", "wR", "c1"]],
            c="13... Ka7. Forced."),
       dict(pieces=[["bK", "bK", "a7"], ["wK", "wK", "c7"],
                    ["RK", "wR", "a1"]],
            c="14. Ra1, mate. The rook takes the a-file from the far "
              "end; the king covers b6, b7 and b8."),
      ],
      notes=["Black's moves come from a computed tablebase of this "
             "ending, so this is the longest resistance possible.",
             "Use the arrows or the arrow keys to play through the line "
             "one move at a time."]),
 dict(id="twobishops", g="Checkmates", t="The two-bishop mate",
      c="Two bishops form diagonal fences a king cannot cross. Black is "
        "not scripted: it plays the tablebase defence, the reply that "
        "delays mate the longest. Gold is every square White covers; "
        "green is every square still open to the black king.",
      strong=[], soft=[],
      legend=[("w", "the dark-squared bishop's squares"),
              ("g2", "the light-squared bishop's squares"),
              ("wk", "squares the white king covers"),
              ("bk", "squares the black king can still move to"),
              ("chk", "check")],
      steps=[
       dict(pieces=[["bK", "bK", "d5"], ["wK", "wK", "c1"],
                    ["BL", "wB", "d1"], ["BD", "wB", "e1"]],
            c="The start: Kc1, Bd1, Be1, black king on d5. Black plays the tablebase defence: every reply is the one that delays mate the longest. White aims for a mate away from the corner, which costs one extra move: mate in 17."),
       dict(pieces=[["bK", "bK", "d5"], ["wK", "wK", "d2"],
                    ["BL", "wB", "d1"], ["BD", "wB", "e1"]],
            c="1. Kd2. The king steps up first."),
       dict(pieces=[["bK", "bK", "d4"], ["wK", "wK", "d2"],
                    ["BL", "wB", "d1"], ["BD", "wB", "e1"]],
            c="1... Kd4. All eight replies lose in the same number of moves; black takes the centre."),
       dict(pieces=[["bK", "bK", "d4"], ["wK", "wK", "d2"],
                    ["BL", "wB", "e2"], ["BD", "wB", "e1"]],
            c="2. Be2. The light bishop clears d1 and eyes the f1-a6 diagonal."),
       dict(pieces=[["bK", "bK", "e4"], ["wK", "wK", "d2"],
                    ["BL", "wB", "e2"], ["BD", "wB", "e1"]],
            c="2... Ke4. Black crowds the white pieces."),
       dict(pieces=[["bK", "bK", "e4"], ["wK", "wK", "d2"],
                    ["BL", "wB", "e2"], ["BD", "wB", "g3"]],
            c="3. Bg3. The dark bishop takes the b8-h2 diagonal."),
       dict(pieces=[["bK", "bK", "d5"], ["wK", "wK", "d2"],
                    ["BL", "wB", "e2"], ["BD", "wB", "g3"]],
            c="3... Kd5."),
       dict(pieces=[["bK", "bK", "d5"], ["wK", "wK", "d3"],
                    ["BL", "wB", "e2"], ["BD", "wB", "g3"]],
            c="4. Kd3. The kings face off."),
       dict(pieces=[["bK", "bK", "c5"], ["wK", "wK", "d3"],
                    ["BL", "wB", "e2"], ["BD", "wB", "g3"]],
            c="4... Kc5."),
       dict(pieces=[["bK", "bK", "c5"], ["wK", "wK", "e4"],
                    ["BL", "wB", "e2"], ["BD", "wB", "g3"]],
            c="5. Ke4. The white king starts taking ground."),
       dict(pieces=[["bK", "bK", "c6"], ["wK", "wK", "e4"],
                    ["BL", "wB", "e2"], ["BD", "wB", "g3"]],
            c="5... Kc6."),
       dict(pieces=[["bK", "bK", "c6"], ["wK", "wK", "d4"],
                    ["BL", "wB", "e2"], ["BD", "wB", "g3"]],
            c="6. Kd4."),
       dict(pieces=[["bK", "bK", "b6"], ["wK", "wK", "d4"],
                    ["BL", "wB", "e2"], ["BD", "wB", "g3"]],
            c="6... Kb6."),
       dict(pieces=[["bK", "bK", "b6"], ["wK", "wK", "d5"],
                    ["BL", "wB", "e2"], ["BD", "wB", "g3"]],
            c="7. Kd5. Black is pushed toward the queenside."),
       dict(pieces=[["bK", "bK", "a5"], ["wK", "wK", "d5"],
                    ["BL", "wB", "e2"], ["BD", "wB", "g3"]],
            c="7... Ka5. The tablebase choice; going to a7 instead loses eight moves faster."),
       dict(pieces=[["bK", "bK", "a5"], ["wK", "wK", "d5"],
                    ["BL", "wB", "e2"], ["BD", "wB", "e1"]],
            c="8. Be1+. Check from the back rank."),
       dict(pieces=[["bK", "bK", "b6"], ["wK", "wK", "d5"],
                    ["BL", "wB", "e2"], ["BD", "wB", "e1"]],
            c="8... Kb6. Back up; a4 loses faster."),
       dict(pieces=[["bK", "bK", "b6"], ["wK", "wK", "d6"],
                    ["BL", "wB", "e2"], ["BD", "wB", "e1"]],
            c="9. Kd6."),
       dict(pieces=[["bK", "bK", "b7"], ["wK", "wK", "d6"],
                    ["BL", "wB", "e2"], ["BD", "wB", "e1"]],
            c="9... Kb7."),
       dict(pieces=[["bK", "bK", "b7"], ["wK", "wK", "d6"],
                    ["BL", "wB", "e2"], ["BD", "wB", "a5"]],
            c="10. Ba5. Takes b6 away."),
       dict(pieces=[["bK", "bK", "c8"], ["wK", "wK", "d6"],
                    ["BL", "wB", "e2"], ["BD", "wB", "a5"]],
            c="10... Kc8. The longest defence; heading for a7 falls sooner."),
       dict(pieces=[["bK", "bK", "c8"], ["wK", "wK", "c6"],
                    ["BL", "wB", "e2"], ["BD", "wB", "a5"]],
            c="11. Kc6. Black is down to one reply."),
       dict(pieces=[["bK", "bK", "b8"], ["wK", "wK", "c6"],
                    ["BL", "wB", "e2"], ["BD", "wB", "a5"]],
            c="11... Kb8."),
       dict(pieces=[["bK", "bK", "b8"], ["wK", "wK", "c6"],
                    ["BL", "wB", "f1"], ["BD", "wB", "a5"]],
            c="12. Bf1. The light bishop swings toward the f1-a6 diagonal."),
       dict(pieces=[["bK", "bK", "c8"], ["wK", "wK", "c6"],
                    ["BL", "wB", "f1"], ["BD", "wB", "a5"]],
            c="12... Kc8."),
       dict(pieces=[["bK", "bK", "c8"], ["wK", "wK", "c6"],
                    ["BL", "wB", "h3"], ["BD", "wB", "a5"]],
            c="13. Bh3+. Check along c8-h3."),
       dict(pieces=[["bK", "bK", "b8"], ["wK", "wK", "c6"],
                    ["BL", "wB", "h3"], ["BD", "wB", "a5"]],
            c="13... Kb8. Forced."),
       dict(pieces=[["bK", "bK", "b8"], ["wK", "wK", "b6"],
                    ["BL", "wB", "h3"], ["BD", "wB", "a5"]],
            c="14. Kb6. Now c8 stays covered and the king holds a7 and b7."),
       dict(pieces=[["bK", "bK", "a8"], ["wK", "wK", "b6"],
                    ["BL", "wB", "h3"], ["BD", "wB", "a5"]],
            c="14... Ka8. Forced."),
       dict(pieces=[["bK", "bK", "a8"], ["wK", "wK", "c7"],
                    ["BL", "wB", "h3"], ["BD", "wB", "a5"]],
            c="15. Kc7. A quiet move; black gets one square."),
       dict(pieces=[["bK", "bK", "a7"], ["wK", "wK", "c7"],
                    ["BL", "wB", "h3"], ["BD", "wB", "a5"]],
            c="15... Ka7. Forced."),
       dict(pieces=[["bK", "bK", "a7"], ["wK", "wK", "c7"],
                    ["BL", "wB", "h3"], ["BD", "wB", "b6"]],
            c="16. Bb6+. Check."),
       dict(pieces=[["bK", "bK", "a6"], ["wK", "wK", "c7"],
                    ["BL", "wB", "h3"], ["BD", "wB", "b6"]],
            c="16... Ka6. The corner square a8 was mate in one as well; black steps to the middle of the file."),
       dict(pieces=[["bK", "bK", "a6"], ["wK", "wK", "c7"],
                    ["BL", "wB", "f1"], ["BD", "wB", "b6"]],
            c="17. Bf1, mate. The bishop returns to f1 and the whole f1-a6 diagonal is the check. Bb6 covers a5 and a7, the king covers b7."),
      ],
      notes=["Black's moves come from a computed tablebase of this "
             "ending, so this is the longest resistance possible, not a "
             "scripted defence.",
             "Use the arrows or the arrow keys to play through the line "
             "one move at a time."]),
 dict(id="twobishops2", g="Checkmates", t="The two-bishop mate in the "
      "corner",
      c="The same start, with both sides playing perfectly: White takes "
        "the fastest mate, black delays as long as it can, and the fight "
        "ends in the a1 corner.",
      strong=[], soft=[],
      legend=[("w", "the dark-squared bishop's squares"),
              ("g2", "the light-squared bishop's squares"),
              ("wk", "squares the white king covers"),
              ("bk", "squares the black king can still move to"),
              ("chk", "check")],
      steps=[
       dict(pieces=[["bK", "bK", "d5"], ["wK", "wK", "c1"],
                    ["BL", "wB", "d1"], ["BD", "wB", "e1"]],
            c="The start: Kc1, Bd1, Be1, black king on d5. Both sides play perfectly: White mates as fast as possible, black delays as long as possible. Mate in 16."),
       dict(pieces=[["bK", "bK", "d5"], ["wK", "wK", "d2"],
                    ["BL", "wB", "d1"], ["BD", "wB", "e1"]],
            c="1. Kd2."),
       dict(pieces=[["bK", "bK", "d4"], ["wK", "wK", "d2"],
                    ["BL", "wB", "d1"], ["BD", "wB", "e1"]],
            c="1... Kd4. Every reply loses in 16; black takes the centre."),
       dict(pieces=[["bK", "bK", "d4"], ["wK", "wK", "d2"],
                    ["BL", "wB", "d1"], ["BD", "wB", "g3"]],
            c="2. Bg3. The dark bishop takes the b8-h2 diagonal."),
       dict(pieces=[["bK", "bK", "e4"], ["wK", "wK", "d2"],
                    ["BL", "wB", "d1"], ["BD", "wB", "g3"]],
            c="2... Ke4. Black crowds the bishops rather than retreat."),
       dict(pieces=[["bK", "bK", "e4"], ["wK", "wK", "d2"],
                    ["BL", "wB", "g4"], ["BD", "wB", "g3"]],
            c="3. Bg4. Out of the king's reach, ready for f3."),
       dict(pieces=[["bK", "bK", "d4"], ["wK", "wK", "d2"],
                    ["BL", "wB", "g4"], ["BD", "wB", "g3"]],
            c="3... Kd4."),
       dict(pieces=[["bK", "bK", "d4"], ["wK", "wK", "d2"],
                    ["BL", "wB", "f3"], ["BD", "wB", "g3"]],
            c="4. Bf3. The long diagonal is fenced."),
       dict(pieces=[["bK", "bK", "c4"], ["wK", "wK", "d2"],
                    ["BL", "wB", "f3"], ["BD", "wB", "g3"]],
            c="4... Kc4."),
       dict(pieces=[["bK", "bK", "c4"], ["wK", "wK", "d2"],
                    ["BL", "wB", "f3"], ["BD", "wB", "f2"]],
            c="5. Bf2. The second fence, on a7-g1."),
       dict(pieces=[["bK", "bK", "b5"], ["wK", "wK", "d2"],
                    ["BL", "wB", "f3"], ["BD", "wB", "f2"]],
            c="5... Kb5. b3 and b4 lose faster."),
       dict(pieces=[["bK", "bK", "b5"], ["wK", "wK", "c3"],
                    ["BL", "wB", "f3"], ["BD", "wB", "f2"]],
            c="6. Kc3. The king joins."),
       dict(pieces=[["bK", "bK", "a6"], ["wK", "wK", "c3"],
                    ["BL", "wB", "f3"], ["BD", "wB", "f2"]],
            c="6... Ka6. The best defence runs up the edge on its own; the lower retreats lose faster."),
       dict(pieces=[["bK", "bK", "a6"], ["wK", "wK", "c4"],
                    ["BL", "wB", "f3"], ["BD", "wB", "f2"]],
            c="7. Kc4."),
       dict(pieces=[["bK", "bK", "a5"], ["wK", "wK", "c4"],
                    ["BL", "wB", "f3"], ["BD", "wB", "f2"]],
            c="7... Ka5. Forced."),
       dict(pieces=[["bK", "bK", "a5"], ["wK", "wK", "c4"],
                    ["BL", "wB", "b7"], ["BD", "wB", "f2"]],
            c="8. Bb7. Takes a6."),
       dict(pieces=[["bK", "bK", "a4"], ["wK", "wK", "c4"],
                    ["BL", "wB", "b7"], ["BD", "wB", "f2"]],
            c="8... Ka4. Forced."),
       dict(pieces=[["bK", "bK", "a4"], ["wK", "wK", "c4"],
                    ["BL", "wB", "b7"], ["BD", "wB", "b6"]],
            c="9. Bb6. Takes a5."),
       dict(pieces=[["bK", "bK", "a3"], ["wK", "wK", "c4"],
                    ["BL", "wB", "b7"], ["BD", "wB", "b6"]],
            c="9... Ka3. Forced."),
       dict(pieces=[["bK", "bK", "a3"], ["wK", "wK", "c3"],
                    ["BL", "wB", "b7"], ["BD", "wB", "b6"]],
            c="10. Kc3. Covers b2, b3 and b4."),
       dict(pieces=[["bK", "bK", "a2"], ["wK", "wK", "c3"],
                    ["BL", "wB", "b7"], ["BD", "wB", "b6"]],
            c="10... Ka2."),
       dict(pieces=[["bK", "bK", "a2"], ["wK", "wK", "c3"],
                    ["BL", "wB", "b7"], ["BD", "wB", "e3"]],
            c="11. Be3. Covers c1, so the king cannot slip out along the back rank."),
       dict(pieces=[["bK", "bK", "a3"], ["wK", "wK", "c3"],
                    ["BL", "wB", "b7"], ["BD", "wB", "e3"]],
            c="11... Ka3. Dropping to b1 or a1 at once loses faster."),
       dict(pieces=[["bK", "bK", "a3"], ["wK", "wK", "c3"],
                    ["BL", "wB", "c6"], ["BD", "wB", "e3"]],
            c="12. Bc6. A waiting move on the long diagonal; black must give ground."),
       dict(pieces=[["bK", "bK", "a2"], ["wK", "wK", "c3"],
                    ["BL", "wB", "c6"], ["BD", "wB", "e3"]],
            c="12... Ka2. Forced."),
       dict(pieces=[["bK", "bK", "a2"], ["wK", "wK", "c2"],
                    ["BL", "wB", "c6"], ["BD", "wB", "e3"]],
            c="13. Kc2. Takes b1 and b2."),
       dict(pieces=[["bK", "bK", "a1"], ["wK", "wK", "c2"],
                    ["BL", "wB", "c6"], ["BD", "wB", "e3"]],
            c="13... Ka1. a1 and a3 lose alike; the corner it is."),
       dict(pieces=[["bK", "bK", "a1"], ["wK", "wK", "b3"],
                    ["BL", "wB", "c6"], ["BD", "wB", "e3"]],
            c="14. Kb3. Boxes the king in."),
       dict(pieces=[["bK", "bK", "b1"], ["wK", "wK", "b3"],
                    ["BL", "wB", "c6"], ["BD", "wB", "e3"]],
            c="14... Kb1. Only move."),
       dict(pieces=[["bK", "bK", "b1"], ["wK", "wK", "b3"],
                    ["BL", "wB", "e4"], ["BD", "wB", "e3"]],
            c="15. Be4+. Check on the b1-h7 diagonal."),
       dict(pieces=[["bK", "bK", "a1"], ["wK", "wK", "b3"],
                    ["BL", "wB", "e4"], ["BD", "wB", "e3"]],
            c="15... Ka1. Forced."),
       dict(pieces=[["bK", "bK", "a1"], ["wK", "wK", "b3"],
                    ["BL", "wB", "e4"], ["BD", "wB", "d4"]],
            c="16. Bd4, mate. The long dark diagonal ends the game; Be4 covers b1 and the king covers a2 and b2."),
      ],
      notes=["This is the fastest mate from the starting position against "
             "the tablebase defence. With best play from both sides the "
             "king ends up in the corner.",
             "Use the arrows or the arrow keys to play through the line "
             "one move at a time."]),
]

def _mate_shade(pieces):
    """Shading for one frame of the two-bishop mate, computed from the
    position.

    soft  = dark-squared bishop's squares (4 diagonal rays, blocked)
    g2    = light-squared bishop's squares
    chk   = the black king's square when a bishop ray hits it
    wk    = squares the white king covers
    bk    = squares the black king can legally move to (green; excludes
            squares attacked by a bishop — x-raying through the king —
            or covered by the white king)
    """
    occ = {p[2]: p[1] for p in pieces}
    pos = {p[0]: p[2] for p in pieces}
    soft, g2, chk, attacked = [], [], [], set()
    for _key, typ, s in pieces:
        if typ == "wP":                       # a pawn hits two squares, no rays
            f, r = FILES.index(s[0]), int(s[1])
            for df in (-1, 1):
                if 0 <= f + df <= 7 and r + 1 <= 8:
                    s2 = sq(f + df, r + 1)
                    soft.append(s2)
                    attacked.add(s2)
                    if occ.get(s2) == "bK":
                        chk.append(s2)
            continue
        if typ not in ("wB", "wR", "wQ"):
            continue
        f, r = FILES.index(s[0]), int(s[1])
        if typ == "wR":
            out = soft
            dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))
        elif typ == "wQ":
            out = soft
            dirs = ((1, 0), (-1, 0), (0, 1), (0, -1),
                    (1, 1), (1, -1), (-1, 1), (-1, -1))
        else:
            out = soft if (f + r) % 2 == 1 else g2
            dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))
        for df, dr in dirs:
            nf, nr = f + df, r + dr
            behind_king = False
            while 0 <= nf <= 7 and 1 <= nr <= 8:
                s2 = sq(nf, nr)
                attacked.add(s2)
                if not behind_king:
                    if s2 in occ:
                        if occ[s2] == "bK":
                            out.append(s2)
                            chk.append(s2)
                            behind_king = True  # x-ray for legality only
                            nf += df
                            nr += dr
                            continue
                        attacked.discard(s2)  # blocked by a white piece
                        break
                    out.append(s2)
                else:
                    break  # one square past the king is enough here
                nf += df
                nr += dr
    kf, kr = FILES.index(pos["wK"][0]), int(pos["wK"][1])
    wk = [sq(kf + df, kr + dr)
          for df in (-1, 0, 1) for dr in (-1, 0, 1)
          if (df or dr) and 0 <= kf + df <= 7 and 1 <= kr + dr <= 8]
    bf, br = FILES.index(pos["bK"][0]), int(pos["bK"][1])
    bk = []
    for df in (-1, 0, 1):
        for dr in (-1, 0, 1):
            if not (df or dr):
                continue
            if not (0 <= bf + df <= 7 and 1 <= br + dr <= 8):
                continue
            s2 = sq(bf + df, br + dr)
            if s2 in attacked or s2 in wk:
                continue
            if s2 in occ:
                # taking a white piece is legal only if nothing defends it
                if occ[s2] in ("wK", "bK"):
                    continue
                others = [q for q in pieces if q[2] != s2]
                if s2 in _white_cover(others):
                    continue
            bk.append(s2)
    return soft, g2, chk, wk, bk


def _white_cover(pieces):
    """Every square the given white pieces defend, kings included."""
    out = set()
    occ = {p[2]: p[1] for p in pieces}
    RAYS = {"wR": ((1, 0), (-1, 0), (0, 1), (0, -1)),
            "wB": ((1, 1), (1, -1), (-1, 1), (-1, -1)),
            "wQ": ((1, 0), (-1, 0), (0, 1), (0, -1),
                   (1, 1), (1, -1), (-1, 1), (-1, -1))}
    for _key, typ, s in pieces:
        f, r = FILES.index(s[0]), int(s[1])
        if typ == "wK":
            for df in (-1, 0, 1):
                for dr in (-1, 0, 1):
                    if (df or dr) and 0 <= f + df <= 7 and 1 <= r + dr <= 8:
                        out.add(sq(f + df, r + dr))
        elif typ == "wP":
            for df in (-1, 1):
                if 0 <= f + df <= 7 and r + 1 <= 8:
                    out.add(sq(f + df, r + 1))
        elif typ in RAYS:
            for df, dr in RAYS[typ]:
                nf, nr = f + df, r + dr
                while 0 <= nf <= 7 and 1 <= nr <= 8:
                    s2 = sq(nf, nr)
                    out.add(s2)
                    if s2 in occ:
                        break
                    nf += df
                    nr += dr
    return out


for _t in TOPICS:
    if _t.get("steps"):
        for _st in _t["steps"]:
            (_st["soft"], _st["g2"], _st["chk"], _st["wk"],
             _st["bk"]) = _mate_shade(_st["pieces"])
            _st["strong"] = []

topics_js = json.dumps(TOPICS, separators=(",", ":"), ensure_ascii=False)


def census_svg(c):
    """The whole table as two nested bars: all placements, then the legal ones."""
    x0, W, H = 8, 536, 17
    sc = W / c["slots"]
    w_ill = c["illegal"] * sc
    x_leg = x0 + w_ill + 2
    w_leg = c["legal"] * sc - 2
    w_win = c["win"] * sc
    x_drw = x_leg + w_win + 2
    w_drw = c["draw"] * sc - 2
    n = lambda v: f"{v:,}"
    pc = lambda v, tot: f"{100 * v / tot:.1f}%"
    p = []
    a = p.append
    a('<svg id="census" viewBox="0 0 552 126" width="100%" '
      'xmlns="http://www.w3.org/2000/svg" style="display:none">')
    a('<style>#census .cap{font:600 10px -apple-system,BlinkMacSystemFont,'
      '"Segoe UI",Helvetica,Arial,sans-serif;letter-spacing:.12em;fill:#7d7d7d}'
      '#census .lab{font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",'
      'Helvetica,Arial,sans-serif;fill:#9a9a9a}'
      '#census .num{font:600 12px -apple-system,BlinkMacSystemFont,"Segoe UI",'
      'Helvetica,Arial,sans-serif;fill:#e6e6e6}</style>')
    a(f'<text class="cap" x="{x0}" y="10">EVERY PLACEMENT IN THE TABLE, '
      f'{n(c["slots"])}</text>')
    a(f'<rect x="{x0}" y="18" width="{w_ill:.1f}" height="{H}" rx="3" fill="#3a3f46">'
      f'<title>Not a legal position: {n(c["illegal"])} of {n(c["slots"])} '
      f'({pc(c["illegal"], c["slots"])}). Two pieces on one square {n(c["same"])}, '
      f'kings touching {n(c["kings"])}, Black in check on White\'s turn '
      f'{n(c["check"])}.</title></rect>')
    a(f'<rect x="{x_leg:.1f}" y="18" width="{w_leg:.1f}" height="{H}" rx="3" fill="#6b7078">'
      f'<title>Legal: {n(c["legal"])} ({pc(c["legal"], c["slots"])}). '
      f'White to move {n(c["legalW"])}, Black to move {n(c["legalB"])}.</title></rect>')
    a(f'<text class="lab" x="{x0}" y="50">not legal <tspan class="num">'
      f'{n(c["illegal"])}</tspan></text>')
    a(f'<text class="lab" x="{x_leg + w_leg:.1f}" y="50" text-anchor="end">'
      f'<tspan class="num">{n(c["legal"])}</tspan> legal positions</text>')
    a(f'<text class="cap" x="{x_leg:.1f}" y="80">AND HOW THEY END</text>')
    a(f'<rect x="{x_leg:.1f}" y="88" width="{w_win:.1f}" height="{H}" rx="3" fill="#008300">'
      f'<title>White wins: {n(c["win"])} of {n(c["legal"])} legal positions '
      f'({pc(c["win"], c["legal"])}). White to move {n(c["winW"])}, '
      f'Black to move {n(c["winB"])}.</title></rect>')
    a(f'<rect x="{x_drw:.1f}" y="88" width="{w_drw:.1f}" height="{H}" rx="3" fill="#e66767">'
      f'<title>Drawn: {n(c["draw"])} ({pc(c["draw"], c["legal"])}). '
      f'White to move {n(c["drawW"])}, Black to move {n(c["drawB"])}. '
      f'Black can simply take the pawn in {n(c["capture"])} of them.</title></rect>')
    a(f'<text class="lab" x="{x_leg:.1f}" y="120">White wins <tspan class="num">'
      f'{n(c["win"])}</tspan> {pc(c["win"], c["legal"])}</text>')
    a(f'<text class="lab" x="{x_drw + w_drw:.1f}" y="120" text-anchor="end">'
      f'<tspan class="num">{n(c["draw"])}</tspan> drawn {pc(c["draw"], c["legal"])}'
      '</text>')
    a('</svg>')
    return "".join(p)


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Endgames · Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff;
        --sq-light:#a9b2be; --sq-dark:#5a6472;
        --hi-strong:#f09b28; --hi-soft:#f8d692; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
.wrap { max-width:1240px; margin:0 auto; padding:32px 20px 60px; }
header.site { border-top:4px solid var(--accent); padding-top:22px; margin-bottom:26px;
  display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }
.brand { font-weight:700; font-size:20px; letter-spacing:.1em; text-decoration:none; color:var(--text); }
.brand:hover { color:var(--accent); }
nav.site a { color:var(--muted); text-decoration:none; font-size:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 6px; font-size:26px; }
.lede { color:var(--muted); font-size:14.5px; margin:0 0 18px; max-width:760px; }
.stage { display:flex; gap:26px; align-items:flex-start; }
.menu { flex:0 0 230px; }
.menu h3 { font-size:11.5px; letter-spacing:.14em; text-transform:uppercase;
  color:var(--muted); margin:18px 0 6px; font-weight:600; }
.menu h3:first-child { margin-top:0; }
.menu button { display:block; width:100%; text-align:left; background:none;
  border:none; border-left:2px solid transparent; color:var(--muted);
  padding:5px 10px; font-size:14px; cursor:pointer; border-radius:0 6px 6px 0; }
.menu button:hover { color:var(--text); background:#1d1d1d; }
.menu button.here { color:var(--text); border-left-color:var(--hi-strong);
  background:#1f1c16; }
.boardcol { flex:1 1 520px; min-width:0; max-width:620px; }
#board { width:100%; display:block; user-select:none; }
.info { flex:0 0 270px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:16px; }
#tTitle { font-weight:700; font-size:17px; margin:0 0 8px; }
#stepbar { display:flex; align-items:center; gap:10px; margin:2px 0 8px; }
#stepbar button { background:var(--bg); border:1px solid var(--line); color:var(--text);
  padding:4px 12px; border-radius:7px; cursor:pointer; font-size:13px; }
#stepbar button:hover { border-color:var(--hi-strong); }
#sInd { color:var(--muted); font-size:12.5px; }
#stepSec { color:var(--accent); font-size:10.5px; font-weight:700;
  letter-spacing:.13em; text-transform:uppercase; margin:0 0 5px; }
#stepCap { color:var(--text); font-size:13.5px; line-height:1.55; margin:0 0 12px;
  border-left:2px solid var(--hi-strong); padding-left:10px; }
#tCap { color:var(--muted); font-size:13.5px; line-height:1.55; margin:0 0 12px; }
.legend div { display:flex; gap:8px; align-items:flex-start; font-size:12.5px;
  color:var(--muted); margin-top:6px; }
.legend span.swb { flex:0 0 12px; height:12px; border-radius:3px; margin-top:4px; }
#tNotes { margin:12px 0 0; padding:10px 0 0; border-top:1px solid var(--line);
  font-size:12.5px; color:var(--muted); }
#tNotes p { margin:0 0 6px; }
#sqName { margin-top:12px; padding-top:10px; border-top:1px solid var(--line);
  font-size:13px; color:var(--muted); min-height:1.3em; }
#sqName b { color:var(--hi-strong); font-size:15px; }
.pn { display:flex; gap:8px; margin-top:14px; }
.pn button { background:var(--panel); border:1px solid var(--line); color:var(--text);
  padding:6px 12px; border-radius:8px; cursor:pointer; font-size:13px; }
.pn button:hover { border-color:var(--accent); }
.note { color:var(--muted); font-size:12.5px; margin-top:22px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
@media (max-width:980px){ .stage{flex-wrap:wrap;} .menu{flex:1 1 100%; display:flex;
  flex-wrap:wrap; gap:2px 10px;} .menu h3{width:100%;} .menu button{width:auto;}
  .info{position:static; flex:1 1 100%;} }
/* the placement map */
#mapctl { margin:2px 0 10px; }
.mrow { display:flex; align-items:center; gap:6px; margin-bottom:6px; }
.mrow .mlbl { color:var(--muted); font-size:11px; letter-spacing:.11em;
  text-transform:uppercase; flex:0 0 62px; }
.mbtn { background:var(--bg); border:1px solid var(--line); color:var(--muted);
  padding:3px 9px; border-radius:7px; cursor:pointer; font-size:12.5px; }
.mbtn:hover { color:var(--text); border-color:var(--hi-strong); }
.mbtn.on { color:var(--text); border-color:var(--hi-strong); background:#1f1c16; }
#mapstats { font-size:12.5px; color:var(--muted); line-height:1.5;
  border-top:1px solid var(--line); padding-top:9px; margin-top:2px; }
#mapstats b { color:var(--text); font-weight:600; }
#census { margin-top:14px; }
/* board squares */
rect.sq { transition: fill .45s ease; }
g.pc text { paint-order: stroke; transition: transform .55s ease; }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="chess.html">&larr; Chess</a></nav>
</header>
<h1>Endgames</h1>
<p class="lede">King and pawn against king, then the basic checkmates, played out one move at a time. Black always plays the reply that holds out longest, taken from a solved table of each ending, so every verdict here is exact. Use the arrows or the arrow keys to step through a line, and hover any square to name it. Every placement paints the whole king and pawn table on the board at once.</p>
<div class="stage">
  <div class="menu" id="menu"></div>
  <div class="boardcol">
    <svg id="board" viewBox="0 0 560 560" xmlns="http://www.w3.org/2000/svg"></svg>
    <div class="pn">
      <button id="prev">&larr; Previous</button>
      <button id="next">Next &rarr;</button>
    </div>
    __CENSUS__
  </div>
  <div class="info"><div class="card">
    <div id="tTitle"></div>
    <p id="tCap"></p>
    <div id="mapctl" style="display:none">
      <div class="mrow"><span class="mlbl">Place</span>
        <button class="mbtn on" id="mpK">White king</button>
        <button class="mbtn" id="mpP">Pawn</button></div>
      <div class="mrow"><span class="mlbl">To play</span>
        <button class="mbtn on" id="msW">White</button>
        <button class="mbtn" id="msB">Black</button></div>
      <div id="mapstats"></div>
    </div>
    <div id="stepbar" style="display:none">
      <button id="sPrev">&#9664;</button>
      <span id="sInd"></span>
      <button id="sNext">&#9654;</button>
    </div>
    <div id="stepSec" style="display:none"></div>
    <p id="stepCap" style="display:none"></p>
    <div class="legend" id="tLegend"></div>
    <div id="tNotes" style="display:none"></div>
    <div id="sqName"></div>
  </div></div>
</div>
<p class="note">After the Board intuition trainer diagrams. The same reference
board underlies every topic; only the paint changes.</p>
</div>
<script>
const TOPICS=__TOPICS__;
const KPKMAP='__KPKMAP__';
const FILESTR='abcdefgh';
const S=64, M=24;  // square size, margin for coordinates
const GLYPH={K:'\\u265A',Q:'\\u265B',R:'\\u265C',B:'\\u265D',N:'\\u265E',P:'\\u265F'};

const svg=document.getElementById('board');
function sqColor(f,r){ return (f+r)%2===1 ? 'dark':'light'; }
function baseFill(f,r){ return (f+r)%2===1 ? getCss('--sq-dark') : getCss('--sq-light'); }
function getCss(v){ return getComputedStyle(document.documentElement).getPropertyValue(v).trim(); }

// mix two hex colors
function mix(a,b,t){
  const pa=[1,3,5].map(i=>parseInt(a.slice(i,i+2),16));
  const pb=[1,3,5].map(i=>parseInt(b.slice(i,i+2),16));
  return '#'+pa.map((v,i)=>Math.round(v+(pb[i]-v)*t).toString(16).padStart(2,'0')).join('');
}

function build(){
  let s='';
  s+=`<rect x="${M-4}" y="${M-4}" width="${8*S+8}" height="${8*S+8}" rx="6" fill="#0d0d0d" stroke="#333"/>`;
  for(let f=0;f<8;f++) for(let r=1;r<=8;r++){
    const x=M+f*S, y=M+(8-r)*S;
    s+=`<rect class="sq" id="sq-${FILESTR[f]}${r}" x="${x}" y="${y}" width="${S}" height="${S}"
      fill="${baseFill(f,r)}" data-f="${f}" data-r="${r}"/>`;
  }
  // corner coordinate labels inside squares (like the PDF)
  for(let f=0;f<8;f++) for(let r=1;r<=8;r++){
    const x=M+f*S, y=M+(8-r)*S;
    s+=`<text id="lb-${FILESTR[f]}${r}" x="${x+5}" y="${y+S-6}" font-size="11.5"
      font-weight="600" fill="rgba(0,0,0,0.45)" pointer-events="none">${FILESTR[f]}${r}</text>`;
  }
  s+='<g id="numbers"></g><g id="pieces"></g>';
  svg.innerHTML=s;
}
build();

/* ---- the placement map -------------------------------------------------
   KPKMAP holds one bit per (white king, black king, pawn, side to move) for
   pawns on files a to d: 1 = White wins. Positions with the pawn on e to h
   are the mirror image, so the three squares are flipped before the lookup.
   bit index = (((wk*64 + bk)*24 + wpi)*2) + stm,  wpi = (rank-2)*4 + file  */
let KPKBITS=null;
function kpkBits(){
  if(!KPKBITS){ const s=atob(KPKMAP); KPKBITS=new Uint8Array(s.length);
    for(let i=0;i<s.length;i++) KPKBITS[i]=s.charCodeAt(i); }
  return KPKBITS;
}
function mirror(s){ return (s&56)|(7-(s&7)); }
function adjSq(a,b){
  return Math.max(Math.abs((a&7)-(b&7)),Math.abs((a>>3)-(b>>3)))===1;
}
function pawnHits(wp,s){
  const f=wp&7, r=wp>>3;
  if(r+1>7) return false;
  return (f>0 && s===(r+1)*8+f-1) || (f<7 && s===(r+1)*8+f+1);
}
function kpkWin(wk,bk,wp,stm){
  if((wp&7)>3){ wk=mirror(wk); bk=mirror(bk); wp=mirror(wp); }
  const i=(((wk*64+bk)*24 + ((wp>>3)-1)*4 + (wp&7))*2) + stm;
  return (kpkBits()[i>>3]>>(i&7))&1;
}
/* what the square means with the black king standing on it */
function kpkState(s){
  if(s===mapWK||s===mapWP) return 'piece';
  if(adjSq(s,mapWK)) return 'ill';
  if(mapSTM===0 && pawnHits(mapWP,s)) return 'ill';
  return kpkWin(mapWK,s,mapWP,mapSTM) ? 'win' : 'drw';
}
let mapWK=4*8+4, mapWP=3*8+4, mapSTM=0, mapPiece='K';   // Ke5, e4, White
const MAPFILL={win:['#009a00','#008300'], drw:['#f08585','#e66767'],
               ill:['#4b5059','#33373e'], piece:['#c3cad4','#7c8494']};
// dark fills take light ink and light fills take dark ink, so the square
// names and the dot/dash marks stay readable on every state
const MAPINK={win:'rgba(255,255,255,0.66)', drw:'rgba(0,0,0,0.46)',
              ill:'rgba(255,255,255,0.38)', piece:'rgba(0,0,0,0.45)'};

function fillFor(f,r,topic){
  const name=FILESTR[f]+r;
  const dark=(f+r)%2===1;
  if(topic.map) return MAPFILL[kpkState(f+(r-1)*8)][dark?1:0];
  if(topic.numbers){
    const n=topic.numbers[name];
    const lo=Math.min(...Object.values(topic.numbers));
    const hi=Math.max(...Object.values(topic.numbers));
    const t=(n-lo)/(hi-lo);
    const base=dark?getCss('--sq-dark'):getCss('--sq-light');
    // blend toward strong amber by mobility
    return mix(base, dark?'#e08a18':'#f7b449', 0.15+0.85*t);
  }
  if(topic.chk && topic.chk.includes(name))
    return dark ? '#c94435' : '#e8604e';
  if(topic.strong.includes(name))
    return dark ? '#e08a18' : '#f7a833';
  if(topic.strong2 && topic.strong2.includes(name))
    return dark ? '#3579cf' : '#5aa3f2';
  if(topic.bk && topic.bk.includes(name))
    return dark ? '#4f9160' : '#7dc48f';
  if(topic.soft && topic.soft.includes(name))
    return dark ? '#c9a25e' : '#f3d391';
  if(topic.g2 && topic.g2.includes(name))
    return dark ? '#d9962d' : '#f6bd55';
  if(topic.soft2 && topic.soft2.includes(name))
    return dark ? '#5f83b0' : '#a9c8ec';
  if(topic.wk && topic.wk.includes(name))
    return dark ? '#ab8330' : '#e6c46c';
  return dark?getCss('--sq-dark'):getCss('--sq-light');
}

function sqName(s){ return FILESTR[s&7]+((s>>3)+1); }
/* a dot for a win, a dash for a draw: the verdict does not rest on colour.
   The square's coordinate label is re-inked here too, for the same reason. */
function mapMarks(){
  let s='';
  for(let f=0;f<8;f++) for(let r=1;r<=8;r++){
    const st=kpkState(f+(r-1)*8);
    const lb=document.getElementById('lb-'+FILESTR[f]+r);
    if(lb) lb.setAttribute('fill', MAPINK[st]);
    if(st==='piece') continue;
    const cx=M+f*S+S/2, cy=M+(8-r)*S+S/2;
    if(st==='win')
      s+=`<circle cx="${cx}" cy="${cy}" r="5" fill="${MAPINK.win}" pointer-events="none"/>`;
    else if(st==='drw')
      s+=`<rect x="${cx-6}" y="${cy-1.6}" width="12" height="3.2" rx="1.6"
        fill="${MAPINK.drw}" pointer-events="none"/>`;
  }
  return s;
}
function resetInk(){
  for(let f=0;f<8;f++) for(let r=1;r<=8;r++){
    const lb=document.getElementById('lb-'+FILESTR[f]+r);
    if(lb) lb.setAttribute('fill','rgba(0,0,0,0.45)');
  }
}
function mapStats(){
  let win=0, drw=0, ill=0;
  for(let s=0;s<64;s++){
    const st=kpkState(s);
    if(st==='win') win++; else if(st==='drw') drw++; else if(st==='ill') ill++;
  }
  const legal=win+drw;
  const pct=legal?Math.round(100*win/legal):0;
  return `White king on <b>${sqName(mapWK)}</b>, pawn on <b>${sqName(mapWP)}</b>, `
    + `<b>${mapSTM===0?'White':'Black'}</b> to move.<br>`
    + `Of the <b>${legal}</b> squares the black king may stand on, `
    + `<b>${win}</b> lose and <b>${drw}</b> hold the draw (${pct}% won). `
    + `${ill} squares are not available to it.`;
}
let cur=0, stepIdx=0;
function pieceList(t,st){
  if(t.map) return [['wK','wK',sqName(mapWK)],['PW','wP',sqName(mapWP)]];
  const src=(st&&st.pieces)||t.pieces;
  if(!src) return [];
  if(Array.isArray(src)) return src;               // [[key,type,square],...]
  return Object.entries(src).map(([name,pc])=>[pc+name,pc,name]);
}
function renderPieces(list,jump){
  const pg=document.getElementById('pieces');
  if(jump) pg.innerHTML='';   // new position: place pieces, do not slide them
  const seen=new Set();
  for(const [key,pc,name] of list){
    seen.add(key);
    const f=FILESTR.indexOf(name[0]), r=+name[1];
    const x=M+f*S+S/2, y=M+(8-r)*S+S/2+16;
    let el=pg.querySelector(`g[data-k="${key}"]`);
    if(!el){
      pg.insertAdjacentHTML('beforeend',
        `<g class="pc" data-k="${key}"><text x="0" y="0" text-anchor="middle"
          font-size="46" fill="${pc[0]==='w'?'#f4efe2':'#141414'}"
          stroke="${pc[0]==='w'?'#20242c':'#e8e2d2'}" stroke-width="1.6"
          style="transform:translate(${x}px,${y}px)">${GLYPH[pc[1]]}</text></g>`);
    } else {
      el.querySelector('text').style.transform=`translate(${x}px,${y}px)`;
    }
  }
  [...pg.children].forEach(g=>{ if(!seen.has(g.dataset.k)) g.remove(); });
}
function paint(){
  const t=TOPICS[cur];
  const st=t.steps ? t.steps[stepIdx] : null;
  const fillsrc=st ? Object.assign({}, t, st) : t;
  for(let f=0;f<8;f++) for(let r=1;r<=8;r++){
    document.getElementById('sq-'+FILESTR[f]+r).setAttribute('fill', fillFor(f,r,fillsrc));
  }
  // numbers
  const ng=document.getElementById('numbers');
  if(t.numbers){
    let s='';
    for(let f=0;f<8;f++) for(let r=1;r<=8;r++){
      const x=M+f*S, y=M+(8-r)*S;
      s+=`<text x="${x+S/2}" y="${y+S/2+9}" text-anchor="middle" font-size="26"
        font-weight="700" fill="rgba(0,0,0,0.72)" pointer-events="none">${t.numbers[FILESTR[f]+r]}</text>`;
    }
    ng.innerHTML=s;
  } else if(t.map){ ng.innerHTML=mapMarks(); }
  else ng.innerHTML='';
  if(!t.map) resetInk();
  renderPieces(pieceList(t,st), st && st.jump);
  // the placement map: controls, live counts, and the whole-table figure
  const mc=document.getElementById('mapctl'), cen=document.getElementById('census');
  if(t.map){
    mc.style.display='block'; cen.style.display='block';
    document.getElementById('mapstats').innerHTML=mapStats();
    document.getElementById('mpK').classList.toggle('on', mapPiece==='K');
    document.getElementById('mpP').classList.toggle('on', mapPiece==='P');
    document.getElementById('msW').classList.toggle('on', mapSTM===0);
    document.getElementById('msB').classList.toggle('on', mapSTM===1);
  } else { mc.style.display='none'; cen.style.display='none'; }
  // step bar
  const sb=document.getElementById('stepbar'), sc=document.getElementById('stepCap');
  if(t.steps){
    sb.style.display='flex'; sc.style.display='block';
    document.getElementById('sInd').textContent=(stepIdx+1)+' / '+t.steps.length;
    sc.textContent=st.c||'';
    const ss=document.getElementById('stepSec');
    let sec=''; for(let i=stepIdx;i>=0;i--){ if(t.steps[i].sec){ sec=t.steps[i].sec; break; } }
    if(sec){ ss.textContent=sec; ss.style.display='block'; } else ss.style.display='none';
  } else { sb.style.display='none'; sc.style.display='none';
    document.getElementById('stepSec').style.display='none'; }
  // panel
  document.getElementById('tTitle').textContent=t.t;
  document.getElementById('tCap').textContent=t.c;
  const SW={s:'#f09b28',w:'#f3d391',s2:'#4f9bf0',w2:'#a9c8ec',
            g2:'#f6bd55',wk:'#e6c46c',bk:'#7dc48f',chk:'#e8604e',
            win:'#008300',drw:'#e66767',ill:'#4b5059'};
  document.getElementById('tLegend').innerHTML=(t.legend||[]).map(([k,txt])=>
    `<div><span class="swb" style="background:${SW[k]||'#f09b28'}"></span><span>${txt}</span></div>`).join('');
  const nt=document.getElementById('tNotes');
  if(t.notes){ nt.style.display='block'; nt.innerHTML=t.notes.map(n=>`<p>${n}</p>`).join(''); }
  else { nt.style.display='none'; }
  document.querySelectorAll('.menu button').forEach(b=>
    b.classList.toggle('here', b.dataset.i==cur));
}
function show(i){
  cur=(i+TOPICS.length)%TOPICS.length;
  stepIdx=0;
  paint();
}
document.getElementById('sPrev').onclick=()=>{
  const t=TOPICS[cur]; if(!t.steps) return;
  stepIdx=(stepIdx-1+t.steps.length)%t.steps.length; paint();
};
document.getElementById('sNext').onclick=()=>{
  const t=TOPICS[cur]; if(!t.steps) return;
  stepIdx=(stepIdx+1)%t.steps.length; paint();
};

// menu
const menu=document.getElementById('menu');
let lastG=null;
TOPICS.forEach((t,i)=>{
  if(t.g!==lastG){ lastG=t.g;
    const h=document.createElement('h3'); h.textContent=t.g; menu.appendChild(h); }
  const b=document.createElement('button');
  b.textContent=t.t; b.dataset.i=i;
  b.onclick=()=>show(i);
  menu.appendChild(b);
});

// placement map controls
document.getElementById('mpK').onclick=()=>{ mapPiece='K'; paint(); };
document.getElementById('mpP').onclick=()=>{ mapPiece='P'; paint(); };
document.getElementById('msW').onclick=()=>{ setSTM(0); };
document.getElementById('msB').onclick=()=>{ setSTM(1); };
function setSTM(v){ mapSTM=v; paint(); }
function placeAt(s){
  if(mapPiece==='K'){
    if(s===mapWP) return;
    mapWK=s;
  } else {
    if(s===mapWK) return;
    if((s>>3)<1 || (s>>3)>6) return;    // a pawn lives on ranks 2 to 7
    mapWP=s;
  }
  paint();
}
/* the arrow keys move whichever piece the Place buttons have selected */
function moveSel(df,dr){
  const from = mapPiece==='K' ? mapWK : mapWP;
  const f=(from&7)+df, r=(from>>3)+dr;
  if(f<0||f>7) return;
  if(mapPiece==='P'){                       // a pawn lives on ranks 2 to 7
    if(r<1||r>6) return;
    const s=r*8+f;
    if(s===mapWK) return;
    mapWP=s;
  } else {
    if(r<0||r>7) return;
    const s=r*8+f;
    if(s===mapWP) return;
    mapWK=s;
  }
  paint();
}
svg.addEventListener('click',e=>{
  if(!TOPICS[cur].map) return;
  const el=e.target.closest('rect.sq');
  if(!el) return;
  placeAt(+el.dataset.f + (+el.dataset.r - 1)*8);
});

document.getElementById('prev').onclick=()=>show(cur-1);
document.getElementById('next').onclick=()=>show(cur+1);
document.addEventListener('keydown',e=>{
  const t=TOPICS[cur];
  if(t.map){
    if(e.key==='ArrowLeft'){ moveSel(-1,0); e.preventDefault(); }
    if(e.key==='ArrowRight'){ moveSel(1,0); e.preventDefault(); }
    if(e.key==='ArrowUp'){ moveSel(0,1); e.preventDefault(); }
    if(e.key==='ArrowDown'){ moveSel(0,-1); e.preventDefault(); }
    return;
  }
  if(t.steps){
    if(e.key==='ArrowLeft'){ stepIdx=(stepIdx-1+t.steps.length)%t.steps.length; paint(); }
    if(e.key==='ArrowRight'){ stepIdx=(stepIdx+1)%t.steps.length; paint(); }
  } else {
    if(e.key==='ArrowLeft') show(cur-1);
    if(e.key==='ArrowRight') show(cur+1);
  }
});

// hover square name
svg.addEventListener('pointermove',e=>{
  const el=e.target.closest('rect.sq');
  const out=document.getElementById('sqName');
  if(!el){ out.innerHTML=''; return; }
  const name=FILESTR[+el.dataset.f]+el.dataset.r;
  const t0=TOPICS[cur];
  if(t0.map){
    const s=+el.dataset.f + (+el.dataset.r - 1)*8;
    const st=kpkState(s);
    const TAG={win:' \\u00b7 White wins', drw:' \\u00b7 drawn',
               ill:' \\u00b7 the black king cannot stand here',
               piece:' \\u00b7 occupied'};
    out.innerHTML='<b>'+name+'</b>'+TAG[st];
    return;
  }
  const t=t0.steps ? Object.assign({}, t0, t0.steps[stepIdx]) : t0;
  let tag='';
  if(t.numbers) tag=' \\u00b7 '+t.numbers[name];
  else if(t.chk && t.chk.includes(name)) tag=' \\u00b7 check';
  else if(t.strong.includes(name)) tag=' \\u00b7 highlighted';
  else if(t.strong2 && t.strong2.includes(name)) tag=' \\u00b7 highlighted (blue)';
  else if(t.bk && t.bk.includes(name)) tag=' \\u00b7 open to the black king';
  else if(t.soft && t.soft.includes(name)) tag=t.g2 ? ' \\u00b7 the dark-squared bishop' : ' \\u00b7 highlighted (light)';
  else if(t.g2 && t.g2.includes(name)) tag=' \\u00b7 the light-squared bishop';
  else if(t.soft2 && t.soft2.includes(name)) tag=' \\u00b7 highlighted (light blue)';
  else if(t.wk && t.wk.includes(name)) tag=' \\u00b7 the white king';
  out.innerHTML='<b>'+name+'</b>'+tag;
});
svg.addEventListener('pointerleave',()=>{document.getElementById('sqName').innerHTML='';});

show(0);
</script>
</body>
</html>
"""

html = (HTML.replace("__TOPICS__", topics_js)
            .replace("__KPKMAP__", KPK_MAP)
            .replace("__CENSUS__", census_svg(KPK_CENSUS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html)} bytes): {len(TOPICS)} topics")
