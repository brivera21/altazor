"""Terms for the Chess section's new pages, and the terms added to the three
existing terms pages.

Every entry has the shape of the supplied TERMS arrays (name, tagline, fen,
turn, marks, legend, body), so each page is one board and one caption per
term. Two optional keys extend it:

  moves     a game or line from the starting position; the build plays it
            with python-chess and takes the FEN from the result, so an
            illegal move stops the build
  numbers   a count on every square, drawn as a heat map (the piece vision
            topics that moved here from Board Intuition)

Positions with "fen" are composed. Whatever a caption claims about one of
them (a fork, a pin, a mate, a win) is checked by verify_chess_pages.py.

Mark kinds: subject (amber), zone (pale amber), target (red), plan (blue).
"""

FILES = "abcdefgh"


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


def leaper_counts(steps):
    out = {}
    for f in range(8):
        for r in range(1, 9):
            out[sq(f, r)] = sum(1 for df, dr in steps if 0 <= f + df <= 7 and 1 <= r + dr <= 8)
    return out


def ray_counts(dirs, blocked=()):
    out = {}
    for f in range(8):
        for r in range(1, 9):
            if sq(f, r) in blocked:
                continue
            n = 0
            for df, dr in dirs:
                ff, rr = f + df, r + dr
                while 0 <= ff <= 7 and 1 <= rr <= 8 and sq(ff, rr) not in blocked:
                    n += 1
                    ff += df
                    rr += dr
            out[sq(f, r)] = n
    return out


KNIGHT = ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2))
KING = tuple((df, dr) for df in (-1, 0, 1) for dr in (-1, 0, 1) if df or dr)
DIAG = ((1, 1), (1, -1), (-1, 1), (-1, -1))
ORTHO = ((1, 0), (-1, 0), (0, 1), (0, -1))


def marks(**kinds):
    """marks(subject=[...], zone=[...]) -> {square: kind}; later kinds win."""
    out = {}
    for kind in ("zone", "plan", "target", "subject"):
        for s in kinds.get(kind, []):
            out[s] = kind
    return out


EMPTY = "8/8/8/8/8/8/8/8"
HEAT = [["subject", "more squares"], ["zone", "fewer"]]

f7_diags = sorted(set(diag(0, 2, 1, 1) + diag(4, 8, 1, -1) + diag(0, 7, 1, -1)
                      + diag(4, 1, 1, 1)) - {"f2", "f7"})
atk_diags = sorted(set(diag(1, 1, 1, 1) + diag(1, 8, 1, -1)) - {"h7", "h2"})


# ---------------------------------------------------------------- PAWN

PAWN = [
    {"name": "Passed pawn",
     "tagline": "No enemy pawn can stop it on the way to promotion.",
     "fen": "6k1/pp3ppp/8/3P4/8/8/PP3PPP/6K1", "turn": "White to move",
     "marks": marks(subject=["d5"], plan=["d6", "d7", "d8"]),
     "legend": [["subject", "the passed pawn"], ["plan", "its road to d8"]],
     "body": ["No black pawn stands on the c-, d- or e-file in front of it, so nothing "
              "can take it or block it except a piece, and a piece that blockades a "
              "passed pawn is tied to that job."]},
    {"name": "Protected passed pawn",
     "tagline": "A passed pawn with a pawn guarding it.",
     "fen": "6k1/pp3ppp/8/3P4/2P5/8/P4PPP/6K1", "turn": "White to move",
     "marks": marks(subject=["d5"], plan=["c4"]),
     "legend": [["subject", "the passed pawn"], ["plan", "the pawn that guards it"]],
     "body": ["The black king cannot win d5 by attacking it, because c4 takes back. "
              "When the pieces come off, a protected passer ties the enemy king down "
              "while the other king goes shopping."]},
    {"name": "Connected passed pawns",
     "tagline": "Two passed pawns on neighboring files.",
     "fen": "6k1/5ppp/8/2PP4/8/8/5PPP/6K1", "turn": "White to move",
     "marks": marks(subject=["c5", "d5"], plan=["c6", "d6", "c7", "d7"]),
     "legend": [["subject", "the connected pair"], ["plan", "the squares they cover as they go"]],
     "body": ["Each one can guard the square the other advances to, so they walk up "
              "together, and a blockader in front of one is attacked by the other."]},
    {"name": "Outside passed pawn",
     "tagline": "A passed pawn far from the other pawns.",
     "fen": "8/5p1p/4k1p1/8/P7/4K1P1/5P1P/8", "turn": "White to move",
     "marks": marks(subject=["a4"], target=["f7", "g6", "h7"]),
     "legend": [["subject", "the outside passer"], ["target", "what is left behind"]],
     "body": ["The kingside is three pawns each and even. When the black king goes "
              "to stop the a-pawn, the white king walks over and eats the kingside. "
              "In king and pawn endings this is usually the whole game."]},
    {"name": "Backward pawn",
     "tagline": "Left behind by its neighbors, it can no longer be defended by a pawn.",
     "fen": "6k1/pp3ppp/3p4/3Np3/4P3/8/PPP2PPP/3R2K1", "turn": "White to move",
     "marks": marks(target=["d6"], subject=["d5"], zone=["d2", "d3", "d4"]),
     "legend": [["target", "the backward pawn"], ["subject", "the square in front of it"],
                ["zone", "the half-open file behind"]],
     "body": ["No black pawn is left on c7 or e7 to guard d6, and it cannot step "
              "forward because d5 is White's. That makes d5 a permanent home for a "
              "white piece and d6 a fixed target down the file."]},
    {"name": "Isolated pawn",
     "tagline": "No friendly pawn on either neighboring file.",
     "fen": "r2q1rk1/pp2bppp/2n1pn2/8/3P4/2N2N2/PP2BPPP/R2Q1RK1", "turn": "White to move",
     "marks": marks(subject=["d4"], target=["d5"], plan=["c5", "e5"]),
     "legend": [["subject", "the isolated d-pawn"], ["target", "the blockade square"],
                ["plan", "outposts it gives White's knights"]],
     "body": ["Only pieces can defend d4, and Black wants a piece on d5 to stop it. "
              "In return the pawn gives White space, open files and the c5 and e5 "
              "squares, so White looks for an attack before the ending."]},
    {"name": "Doubled pawns",
     "tagline": "Two pawns of the same color on one file.",
     "moves": "e4 e5 Nf3 Nc6 Bb5 a6 Bxc6 dxc6", "turn": "After 4...dxc6, White to move",
     "marks": marks(subject=["c6", "c7"], zone=["f2", "g2", "h2", "e4"]),
     "legend": [["subject", "Black's doubled c-pawns"],
                ["zone", "White's healthy kingside majority"]],
     "body": ["Once the d-pawns come off, White has four pawns against three on the "
              "kingside and can make a passed pawn there. Black's four against three "
              "on the queenside, two of them on the c-file, cannot. In return Black "
              "has the two bishops."]},
    {"name": "Advanced pawn",
     "tagline": "A pawn deep in enemy territory, gaining space.",
     "moves": "e4 e6 d4 d5 e5", "turn": "French Advance, after 3.e5",
     "marks": marks(subject=["e5"], target=["d6", "f6"], plan=["d4"]),
     "legend": [["subject", "the advanced pawn"], ["target", "squares it takes from Black"],
                ["plan", "its base"]],
     "body": ["On e5 the pawn takes f6 from the black knight and d6 from the bishop. "
              "The price is that it has to be held where it stands, and Black spends "
              "the next moves hitting its base with c5."]},
    {"name": "Overextended pawns",
     "tagline": "Pawns pushed further than they can be supported.",
     "moves": "e4 Nf6 e5 Nd5 d4 d6 c4 Nb6 f4",
     "turn": "Alekhine's Defense, Four Pawns Attack, after 5.f4",
     "marks": marks(subject=["c4", "d4", "e5", "f4"], plan=["d6", "b6"]),
     "legend": [["subject", "White's four pawns"], ["plan", "Black's pieces and pawn aimed at them"]],
     "body": ["White holds the whole center with four pawns; Black's whole defense is "
              "the claim that they are overextended. With ...dxe5, ...Nc6 and ...Bg4 "
              "Black attacks them until one needs more defending than White can give."]},
    {"name": "Pawn structure",
     "tagline": "The skeleton the pieces work around.",
     "fen": "6k1/pp3ppp/2p5/3p4/3P4/4P3/PP3PPP/6K1", "turn": "The Carlsbad structure, White to move",
     "marks": marks(subject=["d4", "d5"], plan=["a2", "b2"], target=["c6"]),
     "legend": [["subject", "the central pawns"], ["plan", "White's queenside minority"],
                ["target", "what it aims at"]],
     "body": ["Pawns move slowly and never back, so their layout outlasts most piece "
              "positions and decides where pieces belong. This one comes from the "
              "Queen's Gambit Exchange: White plays on the queenside, Black on the "
              "kingside."]},
    {"name": "Minority attack",
     "tagline": "Fewer pawns attacking more, to leave a weakness behind.",
     "fen": "6k1/pp3ppp/2p5/1P1p4/P2P4/4P3/5PPP/6K1", "turn": "White to move",
     "marks": marks(subject=["a4", "b5"], target=["c6"], plan=["d5"]),
     "legend": [["subject", "White's two queenside pawns"], ["target", "the pawn they hit"],
                ["plan", "the pawn left weak if Black takes"]],
     "body": ["White's two pawns go at Black's three. After bxc6 bxc6 Black has a "
              "backward c-pawn on a half-open file; after ...cxb5 axb5 the d-pawn is "
              "isolated. Either way there is a target for the rest of the game."]},
    {"name": "Pawn race",
     "tagline": "Both sides running passed pawns, counting moves.",
     "fen": "2K5/8/8/P7/5k1p/8/8/8", "turn": "White to move",
     "marks": marks(subject=["a5"], target=["h4"], plan=["b7", "c6", "d5", "e4", "f3", "g2", "h1"]),
     "legend": [["subject", "White's runner"], ["target", "Black's runner"],
                ["plan", "the diagonal from a8 to h1"]],
     "body": ["Each pawn needs three moves and White moves first, so White queens "
              "first. The new queen on a8 also covers h1, and Black's queen is taken "
              "as it appears."]},
    {"name": "Pawn roller",
     "tagline": "Connected pawns advancing side by side.",
     "moves": "d4 Nf6 c4 g6 Nc3 d5 cxd5 Nxd5 e4 Nxc3 bxc3 Bg7",
     "turn": "Grünfeld Exchange, after 6...Bg7",
     "marks": marks(subject=["d4", "e4"], plan=["d5", "e5"]),
     "legend": [["subject", "the central pair"], ["plan", "where they roll next"]],
     "body": ["Side by side, each pawn guards the square the other moves to, so they "
              "push the pieces in front of them back one square at a time. Black's "
              "whole plan is to stop them rolling with ...c5 and pressure on d4."]},
    {"name": "Pawn storm",
     "tagline": "Pawns thrown at the enemy king.",
     "moves": "e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 g6 Be3 Bg7 f3 O-O Qd2 Nc6 g4 Be6 O-O-O Nxd4 Bxd4 Qa5 h4",
     "turn": "Sicilian Dragon, after 12.h4",
     "marks": marks(subject=["g4", "h4"], target=["g6", "h7"], plan=["h5"]),
     "legend": [["subject", "the storming pawns"], ["target", "the king's cover"],
                ["plan", "the next step"]],
     "body": ["With the kings on opposite wings, White can throw the g- and h-pawns "
              "forward without exposing his own king. h4-h5 hits g6 to open the "
              "h-file against the black king."]},
    {"name": "Push",
     "tagline": "A pawn move straight ahead.",
     "moves": "e4 c5 Nf3 d6 d4", "turn": "Open Sicilian, after 3.d4",
     "marks": marks(subject=["d4"], plan=["c5", "e5"], zone=["c3", "e3"]),
     "legend": [["subject", "the pawn just pushed"], ["plan", "squares it now covers"],
                ["zone", "squares it no longer covers"]],
     "body": ["Every push trades squares: on d2 the pawn guarded c3 and e3, on d4 it "
              "guards c5 and e5. A pawn never comes back, so whatever it stops "
              "guarding stays unguarded by it for good."]},
    {"name": "Breakthrough",
     "tagline": "Pawns sacrificed to force one through.",
     "fen": "6k1/ppp5/8/PPP5/8/8/8/6K1", "turn": "White to move",
     "marks": marks(subject=["b5"], plan=["b6"], target=["a7", "b7", "c7"]),
     "legend": [["subject", "the pawn that goes first"], ["plan", "where it goes"],
                ["target", "Black's pawns"]],
     "body": ["|1.b6 axb6 2.c6 bxc6 3.a6, or 1.b6 cxb6 2.a6 bxa6 3.c6",
              "Three against three, and White gives two pawns so the third runs free. "
              "The black king on g8 is too far away to catch it."]},
    {"name": "Underpromotion",
     "tagline": "Promoting to something less than a queen.",
     "fen": "8/2q1P1k1/8/8/8/8/PP6/K7", "turn": "White to move",
     "marks": marks(subject=["e7"], plan=["e8"], target=["g7", "c7"]),
     "legend": [["subject", "the pawn"], ["plan", "the promotion square"],
                ["target", "what a knight on e8 attacks"]],
     "body": ["|1.e8=N+ and 2.Nxc7",
              "A new queen would lose to ...Qc1 mate. A knight gives check and hits "
              "the queen at once. The knight is the only piece whose move a queen "
              "cannot make, which is why most underpromotions are to a knight."]},
]


# ---------------------------------------------------------------- KNIGHT

KNIGHT_P = [
    {"name": "Knight mobility",
     "tagline": "How many squares a knight attacks from each square.",
     "fen": EMPTY, "turn": "", "numbers": leaper_counts(KNIGHT), "marks": {},
     "legend": HEAT,
     "body": ["Two in the corner, eight in the center. This is why the rim is dim."]},
    {"name": "Outpost territory",
     "tagline": "Where a knight is strongest.",
     "fen": EMPTY, "turn": "",
     "marks": marks(subject=frange(2, 5, 5, 6),
                    zone=sorted(set(rank(5) + rank(6)) - set(frange(2, 5, 5, 6)))),
     "legend": [["subject", "prime outpost squares: c5 to f6"],
                ["zone", "the rest of the 5th and 6th ranks"]],
     "body": ["A knight is strongest on the 5th or 6th rank where no enemy pawn can "
              "chase it away. The c, d, e and f files matter most."]},
]


# ---------------------------------------------------------------- BISHOP

def _rays(fen_sq, dirs, stop=()):
    f, r = FILES.index(fen_sq[0]), int(fen_sq[1])
    out = []
    for df, dr in dirs:
        ff, rr = f + df, r + dr
        while 0 <= ff <= 7 and 1 <= rr <= 8:
            out.append(sq(ff, rr))
            if sq(ff, rr) in stop:
                break
            ff += df
            rr += dr
    return out


_PAIR_OCC = {"g1", "a3", "f2", "g2", "h2", "g8", "a7", "d7", "e7", "f7", "g7", "h7"}

BISHOP = [
    {"name": "Bishop mobility",
     "tagline": "How many squares a bishop attacks from each square.",
     "fen": EMPTY, "turn": "", "numbers": ray_counts(DIAG), "marks": {},
     "legend": HEAT,
     "body": ["Seven anywhere on the rim, rising by two with each ring inward to "
              "thirteen on the four center squares. A bishop never changes color, so "
              "even at its best it sees thirteen of the thirty two squares it can "
              "ever reach."]},
    {"name": "The long diagonals",
     "tagline": "a1 to h8 and a8 to h1.",
     "fen": EMPTY, "turn": "",
     "marks": marks(subject=["b2", "g7"], zone=sorted(set(diag(0, 1, 1, 1)) - {"b2", "g7"}),
                    target=["g2", "b7"], plan=sorted(set(diag(0, 8, 1, -1)) - {"g2", "b7"})),
     "legend": [["subject", "fianchetto squares on the dark diagonal"],
                ["zone", "a1 to h8, all dark"],
                ["target", "fianchetto squares on the light diagonal"],
                ["plan", "a8 to h1, all light"]],
     "body": ["Eight squares each. A fianchettoed bishop on b2, g2, b7 or g7 rakes "
              "one of them end to end."]},
    {"name": "The attacking diagonals",
     "tagline": "b1 to h7 and b8 to h2.",
     "fen": "8/7p/8/8/8/3B4/8/8", "turn": "",
     "marks": marks(subject=["h7", "h2"], zone=atk_diags),
     "legend": [["subject", "h7 and h2, the sacrifice squares"],
                ["zone", "the diagonals that reach them"]],
     "body": ["A bishop here points straight at the square in front of a castled "
              "king. This is the geometry of the Greek gift, Bxh7+."]},
    {"name": "Bishop pair",
     "tagline": "Both bishops against bishop and knight, or two knights.",
     "fen": "6k1/p2nbppp/8/8/8/P2B4/1B3PPP/6K1", "turn": "White to move",
     "marks": marks(subject=["d3", "b2"],
                    zone=sorted(set(_rays("d3", DIAG, _PAIR_OCC) + _rays("b2", DIAG, _PAIR_OCC))
                                - {"a3", "g7", "h7"})),
     "legend": [["subject", "the pair"], ["zone", "the squares they reach"]],
     "body": ["Between them the two bishops cover both colors, so nothing can hide "
              "on one. In open positions the pair is worth about half a pawn more than "
              "bishop and knight."]},
    {"name": "Opposite-color bishops",
     "tagline": "One bishop on light squares, the other on dark.",
     "fen": "8/4k1p1/5p2/2b5/2B5/1P3P2/4K1P1/8", "turn": "White to move",
     "marks": marks(subject=["c4"], target=["c5"], plan=["b3"]),
     "legend": [["subject", "White's light-squared bishop"],
                ["target", "Black's dark-squared bishop"], ["plan", "White's extra pawn"]],
     "body": ["A pawn up, White cannot win: the black bishop holds the dark squares "
              "White's pawns must cross, and White's bishop can never contest them. "
              "In the middlegame the same imbalance helps the attacker, whose bishop "
              "has no opposite number."]},
    {"name": "Fianchetto",
     "tagline": "A bishop developed on the long diagonal, behind a knight pawn.",
     "moves": "Nf3 d5 g3 Nf6 Bg2", "turn": "After 3.Bg2",
     "marks": marks(subject=["g2"], zone=["f3", "e4", "d5", "c6", "b7", "a8"],
                    target=["f3", "h3"]),
     "legend": [["subject", "the fianchettoed bishop"],
                ["zone", "its diagonal"], ["target", "the holes if it is ever traded"]],
     "body": ["The g-pawn steps to g3 and the bishop goes to g2, looking down the "
              "whole long diagonal. The weakened f3 and h3 squares are the cost if "
              "that bishop is ever exchanged."]},
    {"name": "Spanish bishop",
     "tagline": "The Ruy Lopez bishop, aimed at f7 from b3 or c2.",
     "moves": "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Be7 Re1 b5 Bb3 d6 c3 O-O h3",
     "turn": "Closed Ruy Lopez, after 9.h3",
     "marks": marks(subject=["b3"], zone=["c4", "d5", "e6"], target=["f7", "g8"]),
     "legend": [["subject", "the Spanish bishop"], ["zone", "its diagonal"],
                ["target", "where it points"]],
     "body": ["It goes b5, a4, b3 and often later c2. It looks idle, but from b3 it "
              "presses along a2-g8 at f7 and the castled king for the whole game, and "
              "Black's plans have to allow for it."]},
    {"name": "Trapped on the edge",
     "tagline": "A bishop that takes the h- or a-pawn can be walled in by one pawn move.",
     "fen": "6k1/pp3ppp/8/8/8/2N3P1/PP3P1b/5K2", "turn": "Black to move",
     "marks": marks(subject=["g3"], zone=["g1"], target=["h2"]),
     "legend": [["target", "the bishop that took on h2"], ["subject", "g3, the pawn that shut it in"],
                ["zone", "g1, its only other square, covered by the king"]],
     "body": ["After g3 the bishop has no way back, and Kg2 wins it. Fischer lost the "
              "first game of his 1972 match with Spassky this way, after 29...Bxh2 30.g3."]},
    {"name": "The a7 pawn grab",
     "tagline": "The same trap on the other wing.",
     "fen": "8/B1k1bppp/1p3n2/8/8/5N2/5PPP/6K1", "turn": "White to move",
     "marks": marks(subject=["b6"], zone=["b8"], target=["a7"]),
     "legend": [["target", "the bishop that took on a7"], ["subject", "b6, the pawn that shut it in"],
                ["zone", "b8, its only other square, covered by the king"]],
     "body": ["The king on c7 guards b8 and comes to b7 to take the bishop. Bxb6+ "
              "gives it back for a single pawn."]},
    {"name": "Noah's Ark trap",
     "tagline": "Pawns chase the Spanish bishop into a box.",
     "moves": "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 d6 d4 b5 Bb3 Nxd4 Nxd4 exd4 Qxd4 c5 Qd5 Be6 Qc6+ Bd7 Qd5 c4",
     "turn": "Ruy Lopez, after 8.Qxd4?? c5 9.Qd5 Be6 10.Qc6+ Bd7 11.Qd5 c4",
     "marks": marks(subject=["b5", "c4"], zone=["a2", "c2", "a4"], target=["b3"]),
     "legend": [["target", "the bishop on b3"], ["subject", "b5 and c4, the pawns that box it in"],
                ["zone", "its other squares: two blocked by its own pawns, a4 covered by b5"]],
     "body": ["Taking on d4 with the queen lets Black gain time on her with ...c5, ...Be6 "
              "and ...c4. The bishop can only take on c4, a piece for a pawn."]},
]


# ---------------------------------------------------------------- ROOK

ROOK = [
    {"name": "Rook mobility",
     "tagline": "Fourteen squares from every square.",
     "fen": EMPTY, "turn": "", "numbers": ray_counts(ORTHO), "marks": {},
     "legend": [["subject", "fourteen squares, the same from everywhere"]],
     "body": ["The rook is the only piece whose reach does not change with where it "
              "stands, so on an empty board a1 is worth as much as e5 and the only "
              "question is what stands in the way."]},
    {"name": "Rook behind its own pawn",
     "tagline": "The same board with one white pawn on e4.",
     "fen": "8/8/8/8/4P3/8/8/8", "turn": "", "numbers": ray_counts(ORTHO, blocked={"e4"}),
     "marks": {}, "legend": HEAT,
     "body": ["Off the e-file and the fourth rank nothing changes. On the cross "
              "through the pawn the count falls to nine or ten, and e1 to e3 are "
              "worst at nine: the file shuts at once and only the rank is left."]},
    {"name": "Rook on the 7th",
     "tagline": "Pawns still at home, and the king trapped behind them.",
     "fen": "6k1/pp1R1p2/8/8/8/8/8/8", "turn": "",
     "marks": marks(subject=rank(7), zone=rank(8)),
     "legend": [["subject", "the 7th rank, where the pawns still sit"],
                ["zone", "the 8th rank, where the king is confined"]],
     "body": ["A rook here attacks pawns that have not moved and keeps the king on "
              "its back rank."]},
    {"name": "Pigs on the 7th",
     "tagline": "Two rooks doubled on the seventh rank.",
     "fen": "2r2rk1/pp1RRppp/8/8/8/8/PP3PPP/6K1", "turn": "White to move",
     "marks": marks(subject=["d7", "e7"], target=["b7", "f7"], zone=["a7", "c7", "g7", "h7"]),
     "legend": [["subject", "the pigs"], ["target", "pawns they attack"], ["zone", "the rest of the rank"]],
     "body": ["Material is level, but the two rooks eat whatever is left on the "
              "seventh and keep the king boxed in, and Black's rooks are busy "
              "defending."]},
    {"name": "Blind pigs",
     "tagline": "Two rooks on the seventh that mate on their own.",
     "fen": "r4rk1/1RR3pp/8/8/8/8/5PPP/6K1", "turn": "White to move",
     "marks": marks(subject=["b7", "c7"], target=["g7", "h7"], zone=["f8"]),
     "legend": [["subject", "the rooks"], ["target", "the pawns they take"],
                ["zone", "the king's own rook, blocking its escape"]],
     "body": ["|1.Rxg7+ Kh8 2.Rxh7+ Kg8 3.Rbg7 mate",
              "The rooks check from g7 and h7 in turn, guarding each other, and the "
              "rook on f8 takes the king's last square. The name is usually traced to "
              "Janowski, for rooks on the seventh that failed to find this."]},
    {"name": "Rook lift",
     "tagline": "A rook climbing a rank to swing across.",
     "fen": "r1bq1rk1/pp2bppp/2n1p3/3p4/3P4/2PBR3/PP3PPP/R2Q2K1", "turn": "White to move",
     "marks": marks(subject=["e3"], plan=["f3", "g3", "h3"], target=["h7"]),
     "legend": [["subject", "the lifted rook"], ["plan", "its road across"], ["target", "where it aims"]],
     "body": ["A rook cannot reach the kingside along the first rank while its own "
              "pawns stand in the way, so it climbs to e3 and swings to g3 or h3, in "
              "front of its pawns and next to the enemy king."]},
    {"name": "Open and half-open files",
     "tagline": "No pawns, or only the opponent's.",
     "fen": "2r3k1/pp3ppp/2p5/8/8/4P3/PP3PPP/2RR2K1", "turn": "White to move",
     "marks": marks(zone=[f"d{r}" for r in range(2, 9)], plan=[f"c{r}" for r in (2, 3, 4, 5)],
                    target=["c6"], subject=["c1", "d1"]),
     "legend": [["subject", "White's rooks"], ["zone", "the d-file, open"],
                ["plan", "the c-file, half-open for White"], ["target", "the pawn at its end"]],
     "body": ["An open file has no pawns on it and lets a rook in. A half-open file "
              "has only the opponent's pawn, and a rook there presses on it, here on "
              "c6."]},
]


# ---------------------------------------------------------------- QUEEN

QUEEN = [
    {"name": "Queen mobility",
     "tagline": "A rook and a bishop in one piece.",
     "fen": EMPTY, "turn": "", "numbers": ray_counts(ORTHO + DIAG), "marks": {},
     "legend": HEAT,
     "body": ["Twenty one from the corner and twenty seven from the four center "
              "squares: the rook's fourteen from everywhere, plus the bishop's seven "
              "to thirteen."]},
]


# ---------------------------------------------------------------- KING

KING_P = [
    {"name": "King mobility",
     "tagline": "Squares a king reaches in one move.",
     "fen": EMPTY, "turn": "", "numbers": leaper_counts(KING), "marks": {},
     "legend": HEAT,
     "body": ["Three in the corner, five on an edge, eight in the middle. Endgame "
              "kings belong in the middle."]},
    {"name": "f2 and f7",
     "tagline": "The soft squares of the starting position.",
     "fen": EMPTY, "turn": "",
     "marks": marks(subject=["f2", "f7"], zone=f7_diags),
     "legend": [["subject", "f2 and f7"], ["zone", "the diagonals that attack them"]],
     "body": ["At the start these two squares are defended by the king and nothing "
              "else. Most early tactics against beginners aim here."]},
    {"name": "Flight square",
     "tagline": "A square the king can escape to.",
     "fen": "6k1/1r3pp1/7p/8/8/8/5PPP/4R1K1", "turn": "White to move",
     "marks": marks(subject=["h7"], plan=["h6"], zone=["e8", "f8"]),
     "legend": [["subject", "the flight square"], ["plan", "the pawn move that made it"],
                ["zone", "the back rank"]],
     "body": ["With the pawn on h6, h7 is free, so Re8+ is only a check: the king "
              "steps to h7. Without it, the same move would be mate on the back rank."]},
    {"name": "King hunt",
     "tagline": "A king driven out and chased across the board.",
     "moves": "d4 e6 Nf3 f5 Nc3 Nf6 Bg5 Be7 Bxf6 Bxf6 e4 fxe4 Nxe4 b6 Ne5 O-O Bd3 Bb7 Qh5 Qe7 "
              "Qxh7+ Kxh7 Nxf6+ Kh6 Neg4+ Kg5 h4+ Kf4 g3+ Kf3 Be2+ Kg2 Rh2+ Kg1 Kd2#",
     "turn": "Edward Lasker against George Thomas, London, 1912, final position",
     "marks": marks(plan=["h7", "h6", "g5", "f4", "f3", "g2"], target=["g1"], subject=["h5"]),
     "legend": [["plan", "the black king's road"], ["target", "where it was mated"],
                ["subject", "where the queen gave itself up"]],
     "body": ["11.Qxh7+ Kxh7 drew the king out of g8, and from h7 it was checked down "
              "the board, square by square, to g1, where 18.Kd2 mated it with a "
              "discovered check."]},
    {"name": "Triangulation",
     "tagline": "Losing a move by walking a triangle.",
     "fen": "8/8/8/1pPk4/1P6/3K4/8/8", "turn": "White to move",
     "marks": marks(subject=["d3"], plan=["d2", "e2"], target=["d5"]),
     "legend": [["subject", "White's king"], ["plan", "the triangle"], ["target", "Black's king"]],
     "body": ["|1.Kd2 Ke6 2.Ke2 Kd5 3.Kd3",
              "With Black to move, the king would have to give ground and White "
              "wins. White hands over the move by walking d3, d2, e2, d3; the black "
              "king has no triangle of its own to answer with."]},
]


# ---------------------------------------------------------------- TACTICS

TACTICS = [
    {"name": "Double attack",
     "tagline": "One move, two threats.",
     "fen": "6k1/pp3ppp/8/8/1b5n/8/PP3PPP/3Q2K1", "turn": "White to move",
     "marks": marks(subject=["d4"], target=["b4", "h4"], plan=["c4", "e4", "f4", "g4"]),
     "legend": [["subject", "where the queen goes"], ["target", "two loose pieces"],
                ["plan", "the rank it attacks along"]],
     "body": ["|1.Qd4",
              "Both black pieces stand on the fourth rank with no defender, and Black "
              "can move only one of them. Loose pieces are what double attacks feed on."]},
    {"name": "Fork",
     "tagline": "One piece attacking two at once.",
     "fen": "r3k2r/pp3ppp/8/1N6/8/8/PPP2PPP/R3K2R", "turn": "White to move",
     "marks": marks(subject=["c7"], target=["e8", "a8"]),
     "legend": [["subject", "the forking square"], ["target", "king and rook"]],
     "body": ["|1.Nc7+ and 2.Nxa8",
              "The knight checks the king and attacks the rook in the same move. The "
              "king must move, and the rook falls."]},
    {"name": "Pin, absolute",
     "tagline": "Pinned to the king, so it may not move at all.",
     "moves": "e4 e5 Nf3 Nc6 Bb5 d6", "turn": "After 3...d6",
     "marks": marks(subject=["b5"], target=["c6"], zone=["d7", "e8"]),
     "legend": [["subject", "the pinning bishop"], ["target", "the pinned knight"],
                ["zone", "the line to the king"]],
     "body": ["After ...d6 the knight stands between the bishop and the king. Moving "
              "it would expose the king to check, so the rules forbid it, and it "
              "cannot recapture on e5 or d4 while the pin lasts."]},
    {"name": "Pin, relative",
     "tagline": "Pinned to a more valuable piece; it may move, at a price.",
     "moves": "d4 d5 c4 e6 Nc3 Nf6 Bg5", "turn": "Queen's Gambit Declined, after 4.Bg5",
     "marks": marks(subject=["g5"], target=["f6"], zone=["e7", "d8"]),
     "legend": [["subject", "the pinning bishop"], ["target", "the pinned knight"],
                ["zone", "the line to the queen"]],
     "body": ["The knight on f6 may legally move, but then Bxd8. The rule allows it; "
              "the material does not. Black usually answers with ...Be7, breaking the "
              "pin."]},
    {"name": "Skewer",
     "tagline": "A pin in reverse: the bigger piece in front.",
     "fen": "4r3/5ppp/2k5/8/8/8/5PPP/3B2K1", "turn": "White to move",
     "marks": marks(subject=["a4"], target=["c6", "e8"], zone=["b5", "d7"]),
     "legend": [["subject", "the skewering check"], ["target", "king in front, rook behind"],
                ["zone", "the line"]],
     "body": ["|1.Ba4+ and 2.Bxe8",
              "The king has to step off the diagonal, and the rook behind it is left "
              "to the bishop."]},
    {"name": "Discovered attack",
     "tagline": "One piece moves and uncovers another's attack.",
     "fen": "4k3/pq1p1ppp/8/8/4N3/8/P4PPP/4R1K1", "turn": "White to move",
     "marks": marks(subject=["e4"], plan=["d6"], target=["e8", "b7"], zone=["e1"]),
     "legend": [["subject", "the piece that moves"], ["plan", "where it goes"],
                ["target", "king and queen"], ["zone", "the rook behind"]],
     "body": ["|1.Nd6+ and 2.Nxb7",
              "The knight steps off the e-file and the rook checks the king. From d6 "
              "the knight gives check too, a double check, and attacks the queen. "
              "Only the king can move, and the queen falls."]},
    {"name": "X-ray",
     "tagline": "A piece acting through another on its line.",
     "fen": "r3r1k1/5ppp/1q6/8/8/8/4QPPP/4R1K1", "turn": "White to move",
     "marks": marks(subject=["e1"], plan=["e2"], target=["e8"]),
     "legend": [["subject", "the rook behind"], ["plan", "the queen in front"],
                ["target", "the square both hit"]],
     "body": ["|1.Qxe8+ Rxe8 2.Rxe8 mate",
              "The rook on e1 stands behind its own queen and still counts as an "
              "attacker of e8. Black guards e8 once, with the rook on a8; White hits "
              "it twice, and the back rank does the rest."]},
    {"name": "Decoy",
     "tagline": "A sacrifice that lures a piece onto a bad square.",
     "fen": "3q2k1/pp3pp1/8/6N1/8/8/PP3PP1/6KR", "turn": "White to move",
     "marks": marks(subject=["h8"], target=["f7", "d8"], plan=["g5"]),
     "legend": [["subject", "the decoy square"], ["target", "where the fork lands"],
                ["plan", "the knight"]],
     "body": ["|1.Rh8+ Kxh8 2.Nxf7+ and 3.Nxd8",
              "The rook check leaves the king one move, onto h8, where the knight "
              "from f7 checks it and hits the queen together. When the lured piece is "
              "the king, this is also called attraction."]},
    {"name": "Deflection",
     "tagline": "Forcing a defender away from what it guards.",
     "moves": "e4 e5 Nf3 d6 d4 exd4 Qxd4 Nc6 Bb5 Bd7 Bxc6 Bxc6 Nc3 Nf6 O-O Be7 Nd5 Bxd5 exd5 O-O "
              "Bg5 c6 c4 cxd5 cxd5 Re8 Rfe1 a5 Re2 Rc8 Rae1 Qd7 Bxf6 Bxf6",
     "turn": "Adams against Torre, as usually published, White to move",
     "marks": marks(subject=["d4"], plan=["g4"], target=["d7", "e8"]),
     "legend": [["subject", "White's queen"], ["plan", "where it goes"],
                ["target", "the two defenders of e8"]],
     "body": ["|18.Qg4 Qb5 19.Qc4 Qd7 20.Qc7 Qb5 21.a4 Qxa4 22.Re4 Qb5 23.Qxb7",
              "Black's queen and rook both guard e8 against Rxe8+. White keeps putting "
              "the queen where taking it would pull a defender off e8; in the game the "
              "black queen was pushed off that duty, and 23.Qxb7 won."]},
    {"name": "Attraction",
     "tagline": "A sacrifice that draws the king onto a square.",
     "moves": "e4 c6 d4 d5 Nc3 dxe4 Nxe4 Nf6 Qd3 e5 dxe5 Qa5+ Bd2 Qxe5 O-O-O Nxe4",
     "turn": "Réti against Tartakower, Vienna, 1910, White to move",
     "marks": marks(subject=["d8"], target=["e8"], plan=["d2", "d1"]),
     "legend": [["subject", "the square the king is drawn to"], ["target", "the king"],
                ["plan", "bishop and rook behind"]],
     "body": ["|9.Qd8+ Kxd8 10.Bg5+ Kc7 11.Bd8 mate",
              "The queen gives itself up on the square next to the king. Once the king "
              "takes on d8, the bishop moves with double check, from itself and from "
              "the rook behind it."]},
    {"name": "Clearance",
     "tagline": "Moving a piece out of the way of another.",
     "fen": "r4rk1/pp3pp1/8/7N/8/3B4/PPP5/1K5Q", "turn": "White to move",
     "marks": marks(subject=["h5"], plan=["h7"], zone=["h2", "h3", "h4", "h6"], target=["f6"]),
     "legend": [["subject", "the piece in the way"], ["target", "where it goes, with check"],
                ["zone", "the line it clears"], ["plan", "the mating square"]],
     "body": ["|1.Nf6+ gxf6 2.Qh7 mate",
              "The knight blocks the queen's file. It leaves with check, so Black has "
              "no time to use the tempo, and the open h-file ends in mate."]},
    {"name": "Overloaded piece",
     "tagline": "One defender, two jobs.",
     "fen": "3q2k1/1p3ppp/bn6/8/8/1Q6/P4PPP/4R1K1", "turn": "White to move",
     "marks": marks(subject=["d8"], target=["b6", "e8"], plan=["b3"]),
     "legend": [["subject", "the overloaded queen"], ["target", "the two things it guards"],
                ["plan", "White's queen"]],
     "body": ["|1.Qxb6",
              "Black's queen guards both the knight and the back rank. If it takes back "
              "on b6, Re8 is mate, so the knight is simply lost."]},
    {"name": "Desperado",
     "tagline": "A piece that gives itself up on purpose.",
     "fen": "7k/4R3/8/8/8/p7/P1q5/K7", "turn": "White to move",
     "marks": marks(subject=["e7"], target=["h8"], zone=["a1", "b1", "b2"]),
     "legend": [["subject", "the desperado rook"], ["target", "the king it checks"],
                ["zone", "White's king, with no move"]],
     "body": ["|1.Rh7+ Kg8 2.Rg7+ Kf8 3.Rf7+",
              "White's king has no move, so if the rook is ever taken it is stalemate. "
              "The rook checks forever, and Black cannot escape it without taking it."]},
    {"name": "Windmill",
     "tagline": "A discovered check that repeats, taking something each time.",
     "moves": "d4 Nf6 Nf3 e6 Bg5 c5 e3 cxd4 exd4 Be7 Nbd2 d6 c3 Nbd7 Bd3 b6 Nc4 Bb7 Qe2 Qc7 "
              "O-O O-O Rfe1 Rfe8 Rad1 Nf8 Bc1 Nd5 Ng5 b5 Na3 b4 cxb4 Nxb4 Qh5 Bxg5 Bxg5 Nxd3 "
              "Rxd3 Qa5 b4 Qf5 Rg3 h6 Nc4 Qd5 Ne3 Qb5 Bf6 Qxh5",
     "turn": "Torre against Lasker, Moscow, 1925, White to move",
     "marks": marks(subject=["g3", "f6"], target=["g7", "f7", "b7"], plan=["h5"]),
     "legend": [["subject", "rook and bishop"], ["target", "what the rook collects"],
                ["plan", "Black's queen, taken at the end"]],
     "body": ["|26.Rxg7+ Kh8 27.Rxf7+ Kg8 28.Rg7+ Kh8 29.Rxb7+ Kg8 30.Rg7+ Kh8 31.Rg5+ Kh7 32.Rxh5",
              "The bishop on f6 holds the king in the corner. Each time the rook leaves "
              "g7 it gives discovered check and takes a piece, then comes back with "
              "check."]},
    {"name": "Zwischenzug",
     "tagline": "An in-between move before the expected one.",
     "moves": "e4 e5 Nf3 Nc6 d4 exd4 Bc4 Nf6 e5 d5 Bb5 Ne4 Nxd4 Bd7 Nxc6 bxc6 Bd3 Bc5 Bxe4",
     "turn": "Lichtenhein against Morphy, New York, 1857, Black to move",
     "marks": marks(subject=["d8"], plan=["h4"], target=["f2"], zone=["e4"]),
     "legend": [["subject", "Black's queen"], ["plan", "where it goes first"],
                ["target", "the mate it threatens"], ["zone", "the bishop still to be taken"]],
     "body": ["|10...Qh4",
              "White has just taken the knight on e4, and ...dxe4 is expected. Morphy "
              "first threatens mate on f2; the bishop cannot retreat to f3 because of "
              "...Qxf2 mate, and it is still taken a move later."]},
]


# ---------------------------------------------------------------- CHECKMATES

CHECKMATES = [
    {"name": "Scholar's mate",
     "tagline": "Queen and bishop on f7 in four moves.",
     "moves": "e4 e5 Bc4 Nc6 Qh5 Nf6 Qxf7#", "turn": "After 4.Qxf7, mate",
     "marks": marks(subject=["f7"], plan=["c4", "h5"], zone=["e8"]),
     "legend": [["subject", "the mating square"], ["plan", "where queen and bishop came from"],
                ["zone", "the king"]],
     "body": ["f7 is guarded only by the king, and queen and bishop both hit it. 3...g6 "
              "or 3...Qe7 would have stopped it; 3...Nf6 attacked the queen and "
              "ignored the threat."]},
    {"name": "Smothered mate",
     "tagline": "A knight mates a king hemmed in by its own pieces.",
     "fen": "1r5k/6pp/7N/3Q4/8/8/8/K7", "turn": "White to move",
     "marks": marks(subject=["g8"], plan=["f7"], target=["h8"]),
     "legend": [["subject", "the queen sacrifice"], ["plan", "the mating square"],
                ["target", "the king"]],
     "body": ["|1.Qg8+ Rxg8 2.Nf7 mate",
              "The queen gives itself up on g8, and the rook that takes it fills the "
              "king's last square. The knight mates a king that cannot move."]},
]


# ---------------------------------------------------------------- FUNDAMENTAL TERMS

FUNDAMENTAL = [
    {"name": "Tempo",
     "tagline": "One move's worth of time.",
     "moves": "e4 d5 exd5 Qxd5 Nc3", "turn": "Scandinavian, after 3.Nc3",
     "marks": marks(subject=["c3"], target=["d5"]),
     "legend": [["subject", "the developing knight"], ["target", "the queen it attacks"]],
     "body": ["The knight develops and attacks the queen, which has to move again. "
              "White has made a useful move and Black has not: White gains a tempo."]},
    {"name": "Line",
     "tagline": "A file, rank or diagonal; also a sequence of moves.",
     "fen": "6k1/5ppp/8/8/8/2B5/5PPP/R5K1", "turn": "",
     "marks": marks(subject=["a1", "c3"], zone=[f"a{r}" for r in range(2, 9)],
                    plan=["d4", "e5", "f6", "g7", "b2", "b4", "a5", "d2", "e1"]),
     "legend": [["subject", "rook and bishop"], ["zone", "the rook's file"],
                ["plan", "the bishop's diagonals"]],
     "body": ["On the board, a line is any file, rank or diagonal a long-range piece "
              "moves along. In analysis, a line is a sequence of moves from a position, "
              "as in the main line of an opening."]},
    {"name": "Active and passive pieces",
     "tagline": "Pieces that threaten, and pieces that guard.",
     "fen": "r5k1/pR3ppp/8/8/8/8/P4PPP/6K1", "turn": "White to move",
     "marks": marks(subject=["b7"], target=["a8"], plan=["a7", "f7"]),
     "legend": [["subject", "White's active rook"], ["target", "Black's passive rook"],
                ["plan", "pawns the active rook attacks"]],
     "body": ["Material is level. White's rook on the seventh attacks a7 and f7; "
              "Black's rook does nothing but guard a7. An active piece makes threats, "
              "a passive one answers them."]},
    {"name": "Domination",
     "tagline": "Every square a piece could go to is covered.",
     "fen": "n6k/8/8/B7/4K3/8/6P1/8", "turn": "White to move",
     "marks": marks(target=["a8"], plan=["b6", "c7"], subject=["a5"]),
     "legend": [["target", "the dominated knight"], ["plan", "its only moves"],
                ["subject", "the bishop covering both"]],
     "body": ["The knight has two moves, b6 and c7, and the bishop covers both from "
              "one diagonal. Nothing attacks the knight, and still it is out of the "
              "game: any move it makes loses it, so White plays on as if a piece up."]},
    {"name": "Inaccuracy",
     "tagline": "A move that gives away part of an advantage. Marked ?!",
     "moves": "e4 e5 Nf3 Nc6 Bc4 Nf6 Ng5 d5 exd5 Nxd5", "turn": "Two Knights, after 5...Nxd5?!",
     "marks": marks(subject=["d5"], target=["f7"], plan=["g5", "c4"]),
     "legend": [["subject", "the dubious recapture"], ["target", "the square it leaves weak"],
                ["plan", "White's attackers"]],
     "body": ["Taking back on d5 looks natural, but it lets White play Nxf7, the Fried "
              "Liver, or the quieter d4 with a strong attack. 5...Na5 is the main move. "
              "Not a loss, but an edge handed over: an inaccuracy."]},
    {"name": "Blunder",
     "tagline": "A move that throws the game away. Marked ??",
     "moves": "e4 e5 Nf3 Nc6 Bc4 Nd4 Nxe5 Qg5", "turn": "After 4...Qg5, White to move",
     "marks": marks(subject=["e5"], target=["f7", "g2"], plan=["g5"]),
     "legend": [["subject", "White's knight"], ["target", "the bait and what it costs"],
                ["plan", "Black's queen"]],
     "body": ["|5.Nxf7?? Qxg2 6.Rf1 Qxe4+ 7.Be2 Nf3 mate",
              "The knight takes on f7 and forks queen and rook, which looks like it "
              "wins. It loses at once: the queen takes g2 and mates within three moves."]},
    {"name": "Brilliant move",
     "tagline": "A strong, surprising move, often a sacrifice. Marked !!",
     "moves": "e4 c6 d4 d5 Nc3 dxe4 Nxe4 Nf6 Qd3 e5 dxe5 Qa5+ Bd2 Qxe5 O-O-O Nxe4 Qd8+",
     "turn": "Réti against Tartakower, Vienna, 1910, after 9.Qd8+!!",
     "marks": marks(subject=["d8"], plan=["d2", "d1"]),
     "legend": [["subject", "the queen sacrifice"], ["plan", "bishop and rook, waiting"]],
     "body": ["White is a knight down and gives up the queen as well. 9...Kxd8 is forced, "
              "and 10.Bg5+ is double check and mate next move. A brilliant move is "
              "both best and hard to see."]},
    {"name": "Illegal move",
     "tagline": "A move the rules do not allow.",
     "fen": "4k3/8/8/8/2b5/8/8/4K2R", "turn": "White to move",
     "marks": marks(target=["f1"], subject=["c4"], zone=["e1", "g1"]),
     "legend": [["target", "the square the king would cross"], ["subject", "the bishop covering it"],
                ["zone", "king and castling square"]],
     "body": ["Castling here is illegal: the king would pass over f1, which the bishop "
              "attacks. So is any move that leaves one's own king in check, including "
              "moving a piece pinned to the king."]},
    {"name": "Interposing",
     "tagline": "Answering a check by putting something in the way.",
     "moves": "e4 e5 d4 exd4 Qxd4 Nc6 Qe3 Bb4+ c3", "turn": "Center Game, after 5.c3",
     "marks": marks(subject=["c3"], target=["b4"], zone=["d2", "e1"]),
     "legend": [["subject", "the interposed pawn"], ["target", "the checking bishop"],
                ["zone", "the line to the king"]],
     "body": ["There are three answers to a check: move the king, take the checking "
              "piece, or interpose. Here the pawn blocks the diagonal and attacks the "
              "bishop too. Against a knight, interposing is never possible."]},
]


# ---------------------------------------------------------------- existing pages

OPENING_ADD = [
    {"name": "Control of the center",
     "tagline": "Pawns and pieces on or aimed at d4, d5, e4 and e5.",
     "moves": "e4 e5 Nf3 Nc6 d4", "turn": "Scotch Game, after 3.d4",
     "marks": marks(subject=["d4", "e4"], target=["d5", "e5"], plan=["f3", "c6"]),
     "legend": [["subject", "White's center pawns"], ["target", "the other two center squares"],
                ["plan", "knights aimed at the center"]],
     "body": ["Pieces placed in the center reach both wings fastest, so the first moves "
              "of nearly every opening fight for these four squares, by occupying them "
              "or by aiming at them."]},
    {"name": "King pawn opening",
     "tagline": "1.e4.",
     "moves": "e4", "turn": "After 1.e4",
     "marks": marks(subject=["e4"], plan=["d5", "f5"], zone=["f1", "d1"]),
     "legend": [["subject", "the king pawn"], ["plan", "squares it controls"],
                ["zone", "the queen and bishop it frees"]],
     "body": ["The king pawn takes two center squares and opens lines for the queen and "
              "the king's bishop at once. The positions tend to open early and turn on "
              "tactics and development."]},
    {"name": "Queen pawn opening",
     "tagline": "1.d4.",
     "moves": "d4", "turn": "After 1.d4",
     "marks": marks(subject=["d4"], plan=["c5", "e5"], zone=["c1", "d1"]),
     "legend": [["subject", "the queen pawn"], ["plan", "squares it controls"],
                ["zone", "the bishop and queen it frees"]],
     "body": ["Unlike e4, the pawn on d4 is already guarded by the queen. Queen pawn "
              "games tend to be slower and more positional, with c4 often following to "
              "fight for d5."]},
    {"name": "Open and closed games",
     "tagline": "1.e4 e5 is an open game; 1.d4 d5 a closed one.",
     "moves": "e4 e5", "turn": "An open game, after 1...e5",
     "marks": marks(subject=["e4", "e5"]),
     "legend": [["subject", "the king pawns, face to face"]],
     "body": ["The names sort openings by the first moves: open games start 1.e4 e5, "
              "closed games 1.d4 d5. An open position is a different idea, one with open "
              "files and few center pawns, and a closed opening can still produce one."]},
    {"name": "Semi-closed games",
     "tagline": "1.d4 answered by anything but 1...d5.",
     "moves": "d4 Nf6", "turn": "After 1...Nf6",
     "marks": marks(subject=["d4"], target=["f6"], plan=["e4"]),
     "legend": [["subject", "White's queen pawn"], ["target", "Black's knight"],
                ["plan", "the square it stops White taking with a pawn"]],
     "body": ["The Indian defenses start here. Black controls e4 with a piece instead of "
              "meeting d4 with a pawn. The mirror, 1.e4 answered by anything but 1...e5, "
              "is called semi-open."]},
]

MIDDLEGAME_ADD = [
    {"name": "Hole",
     "tagline": "A square no pawn of one's own can guard anymore.",
     "moves": "d4 f5 c4 Nf6 g3 e6 Bg2 d5 Nf3 c6 O-O Bd6 b3 Qe7",
     "turn": "Dutch Stonewall, after 7...Qe7",
     "marks": marks(target=["e5"], subject=["d5", "e6", "f5"]),
     "legend": [["target", "the hole in Black's camp"], ["subject", "the pawns that left it"]],
     "body": ["The d- and f-pawns have both advanced to the fifth rank, and pawns never "
              "go back, so no black pawn can ever attack e5 again. Only pieces can "
              "contest it."]},
    {"name": "Strong square",
     "tagline": "A square one side can use and the other cannot attack with a pawn.",
     "moves": "d4 f5 c4 Nf6 g3 e6 Bg2 d5 Nf3 c6 O-O Bd6 b3 Qe7 Ne5 O-O",
     "turn": "Dutch Stonewall, after 8...O-O",
     "marks": marks(subject=["e5"], plan=["d4"], target=["e6", "c6", "f7"]),
     "legend": [["subject", "the knight on its strong square"], ["plan", "its pawn support"],
                ["target", "what it presses on"]],
     "body": ["Black's hole on e5 is White's strong square. The knight cannot be driven "
              "off by a pawn and is backed by d4; Black's usual answer is to trade it "
              "with ...Nd7 or ...Bxe5."]},
    {"name": "Weakness",
     "tagline": "A pawn or square that can be attacked and is hard to defend.",
     "fen": "2r3k1/p4ppp/2p5/3p4/3P4/4P3/P4PPP/2R3K1", "turn": "White to move",
     "marks": marks(target=["c6"], subject=["c1"], zone=["c2", "c3", "c4", "c5"]),
     "legend": [["target", "the weak pawn"], ["subject", "White's rook"], ["zone", "the half-open file"]],
     "body": ["The c6 pawn cannot be guarded by another pawn and cannot safely advance, "
              "so a piece has to stand guard over it for the rest of the game. That tie "
              "is the real cost of a weakness."]},
    {"name": "Tension",
     "tagline": "Pawns or pieces attacking each other, with neither side taking.",
     "moves": "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Be7 Re1 b5 Bb3 d6 c3 O-O h3 Nb8 d4",
     "turn": "Closed Ruy Lopez, after 10.d4",
     "marks": marks(subject=["d4", "e5"]),
     "legend": [["subject", "the pawns that attack each other"]],
     "body": ["Either side can capture, and neither wants to first. Taking releases the "
              "tension and usually gives the other side something, a free square or an "
              "open file, so keeping it is often the stronger choice."]},
    {"name": "Blocked position",
     "tagline": "Locked pawn chains dividing the board.",
     "fen": "r1bq1rk1/ppp1npbp/3p1np1/3Pp3/2P1P3/2N2N2/PP2BPPP/R1BQ1RK1", "turn": "King's Indian, Mar del Plata, White to move",
     "marks": marks(subject=["d5", "e4", "d6", "e5"], plan=["c4"], target=["f7"]),
     "legend": [["subject", "the locked center"], ["plan", "White's lever, c4-c5"],
                ["target", "Black's lever, f7-f5"]],
     "body": ["No center file can open, so the pieces maneuver behind the lines and the "
              "game turns on pawn breaks on the wings: c4-c5 on the queenside for White, "
              "f7-f5 on the kingside for Black."]},
    {"name": "Counterplay",
     "tagline": "The defending side's own threats.",
     "moves": "e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 g6 Be3 Bg7 f3 O-O Qd2 Nc6 g4 Be6 O-O-O Nxd4 Bxd4 Qa5 h4",
     "turn": "Sicilian Dragon, after 12.h4",
     "marks": marks(subject=["a5", "g7"], target=["a2", "c3"], plan=["c8", "b5"]),
     "legend": [["subject", "Black's attackers"], ["target", "what they aim at"],
                ["plan", "where more are coming from"]],
     "body": ["White's pawns are coming at Black's king. Black answers not by defending "
              "but by attacking the other king, down the c-file and with ...b5, so that "
              "White has to spend moves defending too."]},
]

ENDGAME_ADD = [
    {"name": "Zugzwang",
     "tagline": "Every move makes things worse, and passing is not allowed.",
     "moves": "d4 Nf6 c4 e6 Nf3 b6 g3 Bb7 Bg2 Be7 Nc3 O-O O-O d5 Ne5 c6 cxd5 cxd5 Bf4 a6 "
              "Rc1 b5 Qb3 Nc6 Nxc6 Bxc6 h3 Qd7 Kh2 Nh5 Bd2 f5 Qd1 b4 Nb1 Bb5 Rg1 Bd6 "
              "e4 fxe4 Qxh5 Rxf2 Qg5 Raf8 Kh1 R8f5 Qe3 Bd3 Rce1 h6",
     "turn": "Sämisch against Nimzowitsch, Copenhagen, 1923, White to move",
     "marks": marks(target=["h1", "e3", "g1", "e1", "d2", "b1"]),
     "legend": [["target", "White's pieces, none with a safe move"]],
     "body": ["White resigned here with nearly all the pieces still on. Any king or "
              "rook move, any queen move and any bishop or knight move loses material "
              "or allows mate. The rare middlegame zugzwang."]},
    {"name": "Waiting move",
     "tagline": "A move that changes nothing but hands over the obligation to move.",
     "moves": "d4 Nf6 c4 e6 Nf3 b6 g3 Bb7 Bg2 Be7 Nc3 O-O O-O d5 Ne5 c6 cxd5 cxd5 Bf4 a6 "
              "Rc1 b5 Qb3 Nc6 Nxc6 Bxc6 h3 Qd7 Kh2 Nh5 Bd2 f5 Qd1 b4 Nb1 Bb5 Rg1 Bd6 "
              "e4 fxe4 Qxh5 Rxf2 Qg5 Raf8 Kh1 R8f5 Qe3 Bd3 Rce1",
     "turn": "Sämisch against Nimzowitsch, 1923, Black to move",
     "marks": marks(subject=["h7"], plan=["h6"]),
     "legend": [["subject", "the pawn that waits"], ["plan", "its one step"]],
     "body": ["|25...h6",
              "Black has nothing to gain by attacking, so he makes a harmless pawn move "
              "and leaves White to move in a position where every move loses."]},
]


# ---------------------------------------------------------------- THE START
# The first two boards on each piece page: that kind of piece on its starting
# squares, both colors, first alone and then in the full starting position,
# with the squares it sees and, in blue, where each most often goes first.
# "Most often" is counted from the 365chess.com Big Database tree the
# Openings page draws (3.9 million games, August 2026), over the first three
# moves each side, which is as deep as that tree goes: of the games in which
# the piece moves that early, the square it goes to most. Rooks, queens and
# kings do not move in the tree; castling kingside is marked for rooks and
# kings, and nothing for queens.

import chess as _chess

_START = _chess.Board()
_KIND = {"pawn": _chess.PAWN, "knight": _chess.KNIGHT, "bishop": _chess.BISHOP,
         "rook": _chess.ROOK, "queen": _chess.QUEEN, "king": _chess.KING}


def _start_boards(kind):
    """(fen of the pieces alone, their squares, what they see alone, what they see in the setup)"""
    pt = _KIND[kind]
    alone = _chess.Board(None)
    homes = []
    for s_ in _START.pieces(pt, _chess.WHITE) | _START.pieces(pt, _chess.BLACK):
        alone.set_piece_at(s_, _START.piece_at(s_))
        homes.append(_chess.square_name(s_))
    seen_alone, seen_full = set(), set()
    for s_ in _START.pieces(pt, _chess.WHITE) | _START.pieces(pt, _chess.BLACK):
        seen_alone |= {_chess.square_name(t) for t in alone.attacks(s_)}
        seen_full |= {_chess.square_name(t) for t in _START.attacks(s_)}
    return alone.board_fen(), sorted(homes), sorted(seen_alone), sorted(seen_full)


_FIRST = {  # where each most often goes first, as described above
    "pawn": ["e4", "d4", "c4", "g3", "b3", "f4", "e6", "d5", "c5", "g6", "b6", "a6", "f5", "h6"],
    "knight": ["f3", "c3", "f6", "c6"],
    "bishop": ["b5", "f4", "g5", "g7", "f5"],
    "rook": ["f1", "f8"],
    "queen": [],
    "king": ["g1", "g8"],
}
_NAMES = {"pawn": "pawns", "knight": "knights", "bishop": "bishops", "rook": "rooks",
          "queen": "queens", "king": "kings"}
_TEXT = {
    "pawn": ("The sixteen pawns alone. A pawn sees the two squares diagonally ahead, "
             "where it captures (one on the rim), so together they cover the whole third and sixth ranks. "
             "Blue is where each most often goes first: e4, d4 and c4 lead for White, "
             "e6, d5 and c5 for Black.",
             "Nothing changes for the pawns in the full setup: they stand in front, so no "
             "piece blocks them, and with the knights they are the only men that can move "
             "on the first move."),
    "knight": ("The four knights alone. Each sees three squares. Blue is where each most "
               "often goes first: f3 and c3 for White, f6 and c6 for Black, nine times in "
               "ten or more when it moves in the first three moves.",
               "The same knights in the full setup. Nothing blocks a knight, so each still "
               "sees its three squares; the one on the second rank holds its own pawn, "
               "which it defends. With the pawns, they are the only men that can move at once."),
    "bishop": ("The four bishops alone. Each sees seven squares along its two diagonals. "
               "Blue is where each most often goes first: b5 for White's light bishop, f4 "
               "and g5 about equally for the dark one, g7 and f5 for Black. Bishops seldom "
               "move this early, so these rest on fewer games.",
               "The same bishops in the full setup. Each sees only the two pawns in front "
               "of it, which it defends, and cannot move until one of them does."),
    "rook": ("The four rooks alone. Each sees fourteen squares, along its rank to the "
             "other rook and along its file to the enemy rook. Blue is where the h-rooks "
             "usually land first: castling kingside, the usual choice, sets them on f1 "
             "and f8.",
             "The same rooks in the full setup. Each sees two squares, the pawn in front "
             "and the knight beside it, and none can move. The first three moves of the "
             "database never move a rook."),
    "queen": ("The two queens alone. Each sees twenty-one squares: its whole first rank, "
              "the file up to the other queen, and both diagonals. No blue here: in the "
              "first three moves the queens almost never move, and no single first square "
              "stands out.",
              "The same queens in the full setup. Each sees five squares, the bishop and "
              "king beside it and the three pawns in front, and cannot move until a pawn "
              "or a piece gets out of its way."),
    "king": ("The two kings alone. Each sees five squares. Blue is where each usually "
             "goes first: castling kingside, the usual choice, moves the king two squares "
             "at once, to g1 or g8.",
             "The same kings in the full setup. The five squares a king sees all hold its "
             "own men. It cannot move until the pieces between it and a rook have gone, "
             "and then it castles."),
}


def _start_entries(kind):
    fen, homes, seen_a, seen_f = _start_boards(kind)
    first = _FIRST[kind]
    leg = [["subject", f"the {_NAMES[kind]}, where they start"], ["zone", "the squares they see"]]
    if first:
        leg.append(["plan", "where each most often goes first"])
    a = {"name": f"The {_NAMES[kind]} alone",
         "tagline": "Their starting squares, with nothing else on the board.",
         "fen": fen, "turn": "",
         "marks": marks(zone=seen_a, plan=first, subject=homes),
         "legend": leg, "body": [_TEXT[kind][0]]}
    f = {"name": f"The {_NAMES[kind]} in the full setup",
         "tagline": "The same squares with every other piece in place.",
         "fen": _START.board_fen(), "turn": "",
         "marks": marks(zone=seen_f, plan=first, subject=homes),
         "legend": leg, "body": [_TEXT[kind][1]]}
    return [a, f]


PAWN[:0] = _start_entries("pawn")
KNIGHT_P[:0] = _start_entries("knight")
BISHOP[:0] = _start_entries("bishop")
ROOK[:0] = _start_entries("rook")
QUEEN[:0] = _start_entries("queen")
KING_P[:0] = _start_entries("king")


# ---------------------------------------------------------------- LESSONS
# Lessons from games, in the player's own words, each on the position it
# turns on. The text is supplied and kept as written: it runs past the
# 60-word caption and speaks in the imperative, which the term pages do not.
# A body line starting "- " is a list item; one starting "|" is a move line,
# here the game from the first move.
LESSONS = [
    {"name": "Losing lost material on one's own terms",
     "tagline": "What to do with a pawn or piece that can't be saved.",
     "moves": "e4 e5 Nf3 Nc6 Bc4 Nf6 d3 Bb4+ c3 Ba5 O-O O-O Be3 d5 exd5 Nxd5 Bxd5 Qxd5 "
              "b4 Bb6 c4 Qe6 c5 Nxb4 cxb6 axb6 Nc3 c5 Nb5 Qe7 a3 Nd5 Bd2 Bd7 Nc3 Nf6 Re1",
     "turn": "magodehoz against Altazor21, Chess.com, October 2026, after 19.Re1, Black to move",
     "marks": marks(plan=["d5"], zone=["e2", "e3", "e4", "e6"], subject=["e1", "e7"], target=["e5"]),
     "legend": [["target", "the pawn on e5, already lost"],
                ["subject", "White's rook and Black's queen, on the same file"],
                ["zone", "the e-file the pawn keeps closed"],
                ["plan", "where the knight stood before 18...Nf6"]],
     "body": [
         "Once a pawn or piece can't be saved, stop looking for defenses and choose the way of "
         "losing it that costs the least. A rescue attempt that fails can lose the same material "
         "plus a tempo, an open line, or a weaker position.",
         "Questions to ask when something is lost:",
         "- What will the capturing piece attack afterward?",
         "- Which lines open when it's gone?",
         "- Can I get something back for it (activity, a tempo, a better pawn structure)?",
         "Example: magodehoz vs Altazor21, Chess.com, Oct 2026 (I was Black).",
         "|1. e4 e5 2. Nf3 Nc6 3. Bc4 Nf6 4. d3 Bb4+ 5. c3 Ba5 6. O-O O-O 7. Be3 d5 8. exd5 Nxd5 "
         "9. Bxd5 Qxd5 10. b4 Bb6 11. c4 Qe6 12. c5 Nxb4 13. cxb6 axb6 14. Nc3 c5 15. Nb5 Qe7 "
         "16. a3 Nd5 17. Bd2 Bd7 18. Nc3 Nf6 19. Re1 e4 20. Nxe4 Nxe4 21. Rxe4",
         "After 19.Re1, my e5 pawn was already lost. Stockfish's top six replies for Black all drop "
         "it, to Nxe5 or Bf4xe5, at about +3.6 to +3.9 for White. I played 19...e4, which lost the "
         "same pawn on worse terms (about +4.1): after 20.Nxe4 Nxe4 21.Rxe4, the rook took on e4 and "
         "hit my queen on e7 along the now-open e-file, so White gained a tempo. Letting White take "
         "on e5 would have kept the file closed in front of my queen.",
         "The real error was 18...Nf6. On d5 the knight covered f4 and kept White's bishop out, and "
         "18...Nxc3 19.Bxc3 f6 would have supported e5 with a pawn.",
     ]},
    {"name": "Opening the position is bad for loose pieces",
     "tagline": "What a central pawn break does to loose pieces.",
     "moves": "e4 e5 Nf3 Nc6 Bc4 Nf6 d3 Bb4+ c3 Ba5 O-O O-O Be3",
     "turn": "magodehoz against Altazor21, Chess.com, October 2026, after 7.Be3, Black to move",
     "marks": marks(subject=["b2", "c3"], zone=["d7"], plan=["b6"], target=["a5"]),
     "legend": [["target", "the bishop on a5, loose"],
                ["subject", "the queenside pawns that later hit it with tempo"],
                ["zone", "the d-pawn, about to break with 7...d5"],
                ["plan", "7...Bb6, Stockfish's choice"]],
     "body": [
         "Before a central pawn break, check whether any of your pieces are loose or about to be "
         "hit with tempo, and secure them first.",
         "What opening the position means:",
         "The position opens when pawns come off the board, especially center pawns, because pawns "
         "are what block lines.",
         "- Open file: a file with no pawns on it, so rooks and queens can travel its whole length. "
         "A half-open file has only the opponent's pawn on it.",
         "- Open diagonal: a diagonal no longer blocked by pawns, which frees bishops and the queen.",
         "- Pawn break: a pawn move that offers a pawn exchange, like ...d5 against e4. The break is "
         "the act of opening.",
         "A closed position is the opposite: pawn chains locked against each other (for example White "
         "pawns on d4 and e5 against Black pawns on d5 and e6), so pieces have to maneuver behind "
         "them. Trading pieces does not open a position by itself. Pawn exchanges do.",
         "Example: magodehoz vs Altazor21, Chess.com, Oct 2026 (I was Black).",
         "|1. e4 e5 2. Nf3 Nc6 3. Bc4 Nf6 4. d3 Bb4+ 5. c3 Ba5 6. O-O O-O 7. Be3 d5 8. exd5 Nxd5 "
         "9. Bxd5 Qxd5 10. b4 Bb6 11. c4 Qe6 12. c5",
         "7...d5 was a normal central break, but my bishop on a5 was loose. The exchanges removed "
         "White's e-pawn and my d-pawn, opened the d-file and the long diagonals, and brought my queen "
         "to d5. White's queenside pawns then hit both with tempo: b4 against the bishop, c4 against "
         "the queen, and c5 trapped the bishop on b6. Stockfish: +1.13 for White after 7...d5.",
         "Better was 7...Bb6 (Stockfish about +0.13). The bishop leaves a5 before b4 comes with tempo, "
         "and if 8.Bxb6 axb6, the a-pawn recaptures toward the center and the rook gets the half-open "
         "a-file. The ...d5 break is still available later once the pieces are set up.",
         "John Nunn's shorthand for the underlying idea: \"loose pieces drop off.\"",
     ]},
    {"name": "A threat can be answered with a counter-threat",
     "tagline": "What to look for before retreating an attacked piece.",
     "moves": "e4 e5 Nf3 Nc6 Bc4 Nf6 d3 Bb4+ c3 Ba5 O-O O-O Be3 d5 exd5 Nxd5 Bxd5 Qxd5 b4",
     "turn": "magodehoz against Altazor21, Chess.com, October 2026, after 10.b4, Black to move",
     "marks": marks(subject=["b4"], zone=["f3"], plan=["e4"], target=["a5"]),
     "legend": [["target", "the bishop on a5, attacked"],
                ["subject", "the pawn on b4 that attacks it"],
                ["plan", "10...e4, the counter-threat"],
                ["zone", "the knight on f3 it attacks"]],
     "body": [
         "When a piece is attacked, the obvious move is to retreat it. Before doing that, look for a "
         "move that creates a threat of your own. If your threat is equal or bigger, your opponent "
         "has to answer it first, and the original threat often loses its force.",
         "Example: magodehoz vs Altazor21, move 10.",
         "After 10.b4, White attacked my bishop on a5. I retreated with 10...Bb6, and White followed "
         "with c4 and c5 to hit my queen and then trap the bishop (Stockfish: +2.00 for White).",
         "The better move was 10...e4, attacking the knight on f3:",
         "- If 11.dxe4, the d-file opens and Black trades queens with 11...Qxd1 12.Rxd1, then saves "
         "the bishop with 12...Bb6. With the queens off, White's c4 no longer comes with tempo, so "
         "the trap doesn't work. Black gives up a pawn but keeps the bishop (Stockfish: about +0.8).",
         "- If 11.bxa5, Black takes the knight with 11...exf3, so the bishop is not lost for nothing.",
         "When the counter-threat is played in place of the expected reply, it's also called a "
         "zwischenzug (in-between move).",
     ]},
    {"name": "The center sets where the game is fought",
     "tagline": "A locked center sends the fight to the wings; an open one keeps it in the middle.",
     "moves": "d4 Nf6 c4 g6 Nc3 Bg7 e4 d6 f3 O-O Be3 e5 d5 Nh5 Qd2 f5 O-O-O",
     "turn": "King's Indian, Sämisch, after 9.O-O-O: castled on opposite sides, Black to move",
     "marks": marks(zone=["d5", "e4", "d6", "e5"], subject=["c1", "g8"], plan=["g4", "h4", "b5"]),
     "legend": [["zone", "the locked center"],
                ["subject", "the kings, castled on opposite sides"],
                ["plan", "where the wing pawns go: g4 and h4 for White, b5 for Black"]],
     "body": [
         "The more locked the center, the more viable opposite-side castling and wing attacks "
         "become, and the more open the center, the more the game is fought over central files "
         "and quick development.",
     ]},
]

PAGES = {
    "pawn": PAWN, "knight": KNIGHT_P, "bishop": BISHOP, "rook": ROOK,
    "queen": QUEEN, "king": KING_P, "tactics": TACTICS, "checkmates": CHECKMATES,
    "fundamental": FUNDAMENTAL, "lessons": LESSONS,
    "opening-terms.html": OPENING_ADD, "middlegame-terms.html": MIDDLEGAME_ADD,
    "endgame-terms.html": ENDGAME_ADD,
}
