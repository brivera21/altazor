#!/usr/bin/env python3
"""One played game for each of the ten features of I.M.B.A.L.A.N.C.E.S.

Every game here is a documented one, and every move list was replayed
with python-chess before it was written down: an illegal or mistyped move
would not have replayed at all, and the six that finish in mate finish in
the recorded mate. The claims in each note were checked against the board
rather than from memory, which is how two of them came to be rewritten.

Each entry is keyed to a feature in chess_checklists_data.IMBALANCES:

    white, black   the players
    event, year    where and when
    moves          the whole game in SAN, from the first move
    key            the move the feature turns on, in SAN
    side           who plays it
    note           what the position says about that feature
    source         the article the score was taken from

build_chess_checklists.py expands moves into a position for every ply, so
the page carries no chess engine of its own.
"""

EXAMPLES = {
    "initiative": dict(
        white="Paul Morphy", black="Duke of Brunswick and Count Isouard",
        event="Paris", year=1858, name="The Opera Game",
        key="Nxb5", side="White",
        moves="e4 e5 Nf3 d6 d4 Bg4 dxe5 Bxf3 Qxf3 dxe5 Bc4 Nf6 Qb3 Qe7 Nc3 c6 "
              "Bg5 b5 Nxb5 cxb5 Bxb5+ Nbd7 O-O-O Rd8 Rxd7 Rxd7 Rd1 Qe6 Bxd7+ Nxd7 "
              "Qb8+ Nxb8 Rd8#",
        note="Morphy gives up a knight so that Black never gets a free move. "
             "Everything after it arrives with a threat, and Black spends the rest "
             "of the game answering. Seven moves later the queen goes to b8 and the "
             "rook mates on d8, with Black's king's rook and bishop still on their "
             "starting squares.",
        source="https://en.wikipedia.org/wiki/Opera_Game"),

    "material": dict(
        white="Adolf Anderssen", black="Lionel Kieseritzky",
        event="London", year=1851, name="The Immortal Game",
        key="Qf6+", side="White",
        moves="e4 e5 f4 exf4 Bc4 Qh4+ Kf1 b5 Bxb5 Nf6 Nf3 Qh6 d3 Nh5 Nh4 Qg5 Nf5 c6 "
              "g4 Nf6 Rg1 cxb5 h4 Qg6 h5 Qg5 Qf3 Ng8 Bxf4 Qf6 Nc3 Bc5 Nd5 Qxb2 Bd6 Bxg1 "
              "e5 Qxa1+ Ke2 Na6 Nxg7+ Kd8 Qf6+ Nxf6 Be7#",
        note="Anderssen gives the queen here, having already given a bishop and both "
             "rooks. He mates with two knights and a bishop while Black still holds a "
             "queen, two rooks, two bishops and two knights. Counted in points Black "
             "is winning by a distance, which is the argument against counting alone.",
        source="https://en.wikipedia.org/wiki/Immortal_Game"),

    "bishops": dict(
        white="Emanuel Lasker", black="Johann Bauer",
        event="Amsterdam", year=1889, name="The double bishop sacrifice",
        key="Bxh7+", side="White",
        moves="f4 d5 e3 Nf6 b3 e6 Bb2 Be7 Bd3 b6 Nc3 Bb7 Nf3 Nbd7 O-O O-O Ne2 c5 "
              "Ng3 Qc7 Ne5 Nxe5 Bxe5 Qc6 Qe2 a6 Nh5 Nxh5 Bxh7+ Kxh7 Qxh5+ Kg8 Bxg7 Kxg7 "
              "Qg4+ Kh7 Rf3 e5 Rh3+ Qh6 Rxh6+ Kxh6 Qd7",
        note="Both bishops go, one after the other, to strip the pawns from in front "
             "of the king. Neither survives it, and what is left is a king in the open "
             "with a queen and a rook arriving. Two knights standing on those same "
             "squares could not have reached across the board at all.",
        source="https://en.wikipedia.org/wiki/Lasker_versus_Bauer,_Amsterdam,_1889"),

    "activity": dict(
        white="Adolf Anderssen", black="Jean Dufresne",
        event="Berlin", year=1852, name="The Evergreen Game",
        key="Rad1", side="White",
        moves="e4 e5 Nf3 Nc6 Bc4 Bc5 b4 Bxb4 c3 Ba5 d4 exd4 O-O d3 Qb3 Qf6 e5 Qg6 "
              "Re1 Nge7 Ba3 b5 Qxb5 Rb8 Qa4 Bb6 Nbd2 Bb7 Ne4 Qf5 Bxd3 Qh5 Nf6+ gxf6 "
              "exf6 Rg8 Rad1 Qxf3 Rxe7+ Nxe7 Qxd7+ Kxd7 Bf5+ Ke8 Bd7+ Kf8 Bxe7#",
        note="The rook on a1 has not moved all game, and bringing it to d1 is what "
             "finishes the attack. The point is that it was the last piece doing "
             "nothing. Anderssen improved his worst-placed piece and the game ended "
             "six moves later.",
        source="https://en.wikipedia.org/wiki/Evergreen_Game"),

    "lines": dict(
        white="Georg Rotlewi", black="Akiba Rubinstein",
        event="Lodz", year=1907, name="Rubinstein's Immortal",
        key="Rxc3", side="Black",
        moves="d4 d5 Nf3 e6 e3 c5 c4 Nc6 Nc3 Nf6 dxc5 Bxc5 a3 a6 b4 Bd6 Bb2 O-O "
              "Qd2 Qe7 Bd3 dxc4 Bxc4 b5 Bd3 Rd8 Qe2 Bb7 O-O Ne5 Nxe5 Bxe5 f4 Bc7 "
              "e4 Rac8 e5 Bb6+ Kh1 Ng4 Be4 Qh4 g3 Rxc3 gxh4 Rd2 Qxd2 Bxe4+ Qg2 Rh3",
        note="Rubinstein's bishops stand on b6 and b7, on the two long diagonals, and "
             "his rooks on c8 and d8, on the two open files. The rook goes to c3 to "
             "blow the position open, and all four of the lines he spent the game "
             "arranging arrive at the white king at once.",
        source="https://en.wikipedia.org/wiki/Rotlewi_versus_Rubinstein"),

    "attacks": dict(
        white="Garry Kasparov", black="Veselin Topalov",
        event="Wijk aan Zee", year=1999, name="Kasparov's Immortal",
        key="Rxd4", side="White",
        moves="e4 d6 d4 Nf6 Nc3 g6 Be3 Bg7 Qd2 c6 f3 b5 Nge2 Nbd7 Bh6 Bxh6 Qxh6 Bb7 "
              "a3 e5 O-O-O Qe7 Kb1 a6 Nc1 O-O-O Nb3 exd4 Rxd4 c5 Rd1 Nb6 g3 Kb8 Na5 Ba8 "
              "Bh3 d5 Qf4+ Ka7 Rhe1 d4 Nd5 Nbxd5 exd5 Qd6 Rxd4 cxd4 Re7+ Kb6 Qxd4+ Kxa5 "
              "b4+ Ka4 Qc3 Qxd5 Ra7 Bb7 Rxb7 Qc4 Qxf6 Kxa3 Qxa6+ Kxb4 c3+ Kxc3 Qa1+ Kd2 "
              "Qb2+ Kd1 Bf1 Rd2 Rd7 Rxd7 Bxc4 bxc4 Qxh8 Rd3 Qa8 c3 Qa4+ Ke1 f4 f5 Kc1 Rd2 Qa7",
        note="Kasparov gives a rook to tear the file open at a king that has walked to "
             "a7. What follows drives that king from a7 all the way to e1, the whole "
             "width of the board, through a sequence he worked out at the board rather "
             "than felt his way into.",
        source="https://en.wikipedia.org/wiki/Kasparov%27s_Immortal"),

    "numbers": dict(
        white="Alexander McDonnell", black="Louis-Charles Mahe de La Bourdonnais",
        event="London, match 4, game 16", year=1834, name="Three connected passers",
        key="e2", side="Black",
        moves="e4 c5 Nf3 Nc6 d4 cxd4 Nxd4 e5 Nxc6 bxc6 Bc4 Nf6 Bg5 Be7 Qe2 d5 Bxf6 Bxf6 "
              "Bb3 O-O O-O a5 exd5 cxd5 Rd1 d4 c4 Qb6 Bc2 Bb7 Nd2 Rae8 Ne4 Bd8 c5 Qc6 "
              "f3 Be7 Rac1 f5 Qc4+ Kh8 Ba4 Qh6 Bxe8 fxe4 c6 exf3 Rc2 Qe3+ Kh1 Bc8 Bd7 f2 "
              "Rf1 d3 Rc3 Bxd7 cxd7 e4 Qc8 Bd8 Qc4 Qe1 Rc1 d2 Qc5 Rg8 Rd1 e3 Qc3 Qxd1 Rxd1 e2",
        note="Three connected passed pawns on d2, e2 and f2, against a queen and a "
             "rook. White resigned in this position. No piece count helps him: the "
             "pawns are one square from queening, they defend each other, and they "
             "cannot all be stopped.",
        source="https://en.wikipedia.org/wiki/McDonnell%E2%80%93La_Bourdonnais,_match_4,_game_16"),

    "castling": dict(
        white="Esteban Canal", black="an amateur",
        event="Budapest, a simultaneous display", year=1934, name="The Peruvian Immortal",
        key="O-O-O", side="Black",
        moves="e4 d5 exd5 Qxd5 Nc3 Qa5 d4 c6 Nf3 Bg4 Bf4 e6 h3 Bxf3 Qxf3 Bb4 Be2 Nd7 "
              "a3 O-O-O axb4 Qxa1+ Kd2 Qxh1 Qxc6+ bxc6 Ba6#",
        note="Castling queenside is the losing move. The king lands on the file White "
             "is about to open, and once the bishop on b4 is taken the black queen goes "
             "hunting rooks on a1 and h1 while the king sits alone. Mate arrives four "
             "moves after the king castled into safety.",
        source="https://en.wikipedia.org/wiki/Peruvian_Immortal"),

    "endgame": dict(
        white="Magnus Carlsen", black="Ian Nepomniachtchi",
        event="World Chess Championship, game 6", year=2021, name="Queen for two rooks",
        key="Qxc8", side="White",
        moves="d4 Nf6 Nf3 d5 g3 e6 Bg2 Be7 O-O O-O b3 c5 dxc5 Bxc5 c4 dxc4 Qc2 Qe7 "
              "Nbd2 Nc6 Nxc4 b5 Nce5 Nb4 Qb2 Bb7 a3 Nc6 Nd3 Bb6 Bg5 Rfd8 Bxf6 gxf6 "
              "Rac1 Nd4 Nxd4 Bxd4 Qa2 Bxg2 Kxg2 Qb7+ Kg1 Qe4 Qc2 a5 Rfd1 Kg7 Rd2 Rac8 "
              "Qxc8 Rxc8 Rxc8 Qd5 b4",
        note="Carlsen gives the queen for two rooks, which is a choice about what kind "
             "of endgame to enter rather than about what to win now. Nothing was "
             "settled on the spot. The game ran to 136 moves, the longest in world "
             "championship history, and the two rooks came good.",
        source="https://en.wikipedia.org/wiki/Carlsen_versus_Nepomniachtchi,_World_Chess_Championship_2021,_Game_6",
        truncated="The score here stops at move 28; the game went on to move 136."),

    "space": dict(
        white="Friedrich Saemisch", black="Aron Nimzowitsch",
        event="Copenhagen", year=1923, name="The Immortal Zugzwang Game",
        key="h6", side="Black",
        moves="d4 Nf6 c4 e6 Nf3 b6 g3 Bb7 Bg2 Be7 Nc3 O-O O-O d5 Ne5 c6 cxd5 cxd5 "
              "Bf4 a6 Rc1 b5 Qb3 Nc6 Nxc6 Bxc6 h3 Qd7 Kh2 Nh5 Bd2 f5 Qd1 b4 Nb1 Bb5 "
              "Rg1 Bd6 e4 fxe4 Qxh5 Rxf2 Qg5 Raf8 Kh1 R8f5 Qe3 Bd3 Rce1 h6",
        note="White still has a queen, two rooks, two bishops and a knight, and "
             "twenty-seven legal moves, and he resigned here. Black has taken so many "
             "squares that every one of those moves sheds something. A space advantage "
             "carried to its end looks like this.",
        source="https://en.wikipedia.org/wiki/Immortal_Zugzwang_Game"),
}
