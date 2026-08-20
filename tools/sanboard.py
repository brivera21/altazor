"""Minimal SAN interpreter for opening lines (no promotions, no pins checked)."""

import re

START = [
    "rnbqkbnr",
    "pppppppp",
    "........",
    "........",
    "........",
    "........",
    "PPPPPPPP",
    "RNBQKBNR",
]


def sq(name):
    """'e4' -> (row, col) with row 0 = rank 8."""
    return 8 - int(name[1]), ord(name[0]) - 97


def piece_moves(board, r, c):
    p = board[r][c].upper()
    out = []
    if p == "N":
        deltas = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in deltas:
            rr, cc = r + dr, c + dc
            if 0 <= rr < 8 and 0 <= cc < 8:
                out.append((rr, cc))
    elif p == "K":
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr or dc:
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < 8 and 0 <= cc < 8:
                        out.append((rr, cc))
    else:
        rays = {
            "B": [(-1, -1), (-1, 1), (1, -1), (1, 1)],
            "R": [(-1, 0), (1, 0), (0, -1), (0, 1)],
            "Q": [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)],
        }[p]
        for dr, dc in rays:
            rr, cc = r + dr, c + dc
            while 0 <= rr < 8 and 0 <= cc < 8:
                out.append((rr, cc))
                if board[rr][cc] != ".":
                    break
                rr, cc = rr + dr, cc + dc
    return out


def apply_san(board, san, white):
    san = san.rstrip("+#")
    if san in ("O-O", "O-O-O"):
        row = 7 if white else 0
        k, r = ("K", "R") if white else ("k", "r")
        if san == "O-O":
            board[row][4], board[row][6] = ".", k
            board[row][7], board[row][5] = ".", r
        else:
            board[row][4], board[row][2] = ".", k
            board[row][0], board[row][3] = ".", r
        return board
    if san[0] in "NBRQK":
        piece, rest = san[0], san[1:].replace("x", "")
        target, disamb = rest[-2:], rest[:-2]
        tr, tc = sq(target)
        want = piece if white else piece.lower()
        cands = []
        for r in range(8):
            for c in range(8):
                if board[r][c] == want and (tr, tc) in piece_moves(board, r, c):
                    cands.append((r, c))
        if disamb:
            if disamb[0].isalpha():
                cands = [(r, c) for r, c in cands if c == ord(disamb[0]) - 97]
            else:
                cands = [(r, c) for r, c in cands if r == 8 - int(disamb[0])]
        if len(cands) != 1:
            raise ValueError(f"ambiguous {san}: {cands}")
        (r, c) = cands[0]
        board[tr][tc] = board[r][c]
        board[r][c] = "."
    else:
        if "x" in san:
            fr_file, target = san[0], san.split("x")[1]
            tr, tc = sq(target)
            fc = ord(fr_file) - 97
            fr = tr + 1 if white else tr - 1
            if board[tr][tc] == ".":
                board[tr + (1 if white else -1)][tc] = "."  # en passant
            board[tr][tc] = "P" if white else "p"
            board[fr][fc] = "."
        else:
            tr, tc = sq(san)
            step = 1 if white else -1
            fr = tr + step
            if board[fr][tc] == ".":
                fr = tr + 2 * step
            board[tr][tc] = board[fr][tc]
            board[fr][tc] = "."
    return board


def board_for_line(line):
    """Line like '1.e4 e5 2.Nf3' -> 64-char board string (rank 8 first)."""
    board = [list(r) for r in START]
    tokens = [re.sub(r"^\d+\.(\.\.)?", "", t) for t in line.split()]
    tokens = [t for t in tokens if t]
    for i, t in enumerate(tokens):
        apply_san(board, t, white=(i % 2 == 0))
    return "".join("".join(r) for r in board)
