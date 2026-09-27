"""Data for candidate-moves.html.

The example is Réti against Tartakower, Vienna, 1910, a casual game played
for a small stake (Edward Winter, "Réti v Tartakower, Vienna, 1910"). The
position is White's ninth move, after 8...Nxe4 took White's knight.

Each candidate is a list of lines, every line a sequence of SAN moves from
that position. The build replays every move with python-chess, so an
illegal or mistyped move stops it. The evaluations are Stockfish 16 at
depth 24, from White's side, in pawns; verify_candidates.py checks them
again when Stockfish is installed.

The research figures are Gobet (1998), Table 1: 48 Swiss players, twelve
per class, thinking aloud.
"""

GAME = {
    "white": "Richard Réti", "black": "Savielly Tartakower",
    "event": "Vienna", "year": 1910,
    "moves": "e4 c6 d4 d5 Nc3 dxe4 Nxe4 Nf6 Qd3 e5 dxe5 Qa5+ Bd2 Qxe5 O-O-O Nxe4",
    "played": "Qd8+ Kxd8 Bg5+",           # Black resigned here (Winter)
    "source": "https://www.chesshistory.com/winter/extra/retitartakower.html",
}

# kind: what makes it a candidate. check, capture, or attack (a move that
# threatens something). Listed forcing moves first, the way the list is made.
CANDIDATES = [
    {"san": "Qd8+", "kind": "check",
     "lines": [["Qd8+", "Kxd8", "Bg5+", "Kc7", "Bd8#"],
               ["Qd8+", "Kxd8", "Bg5+", "Ke8", "Rd8#"]],
     "eval": "#3", "cp": None, "mate": 3,
     "verdict": "Mate. The queen is given up to open the d-file, 10.Bg5+ checks "
                "twice at once, from the bishop and from the rook behind it, and "
                "either king move is mated."},
    {"san": "Qd7+", "kind": "check",
     "lines": [["Qd7+", "Nxd7"]],
     "eval": "−9.7", "cp": -974, "mate": None,
     "verdict": "Three black pieces can take the queen, and nothing follows. White "
                "ends a queen and a knight down."},
    {"san": "Qxe4", "kind": "capture",
     "lines": [["Qxe4", "Qxe4"]],
     "eval": "−5.7", "cp": -565, "mate": None,
     "verdict": "The obvious recapture. Nothing guards e4, so Black's queen takes "
                "back, and White has traded the queen for a knight."},
    {"san": "Bf4", "kind": "attack",
     "lines": [["Bf4", "Qxf4+"]],
     "eval": "−6.7", "cp": -666, "mate": None,
     "verdict": "The bishop attacks the queen, but the queen simply takes it, with "
                "check. White is two pieces down."},
    {"san": "Re1", "kind": "attack",
     "lines": [["Re1", "Bf5", "g4", "Be6", "Rxe4"]],
     "eval": "+0.8", "cp": 75, "mate": None,
     "verdict": "The one quiet move. The rook lines up on the knight, with the "
                "queen and king behind it, and White wins the piece back: material "
                "level, White a little better."},
]

STEPS = [
    ("List", "Before any line is calculated, the moves worth calculating are "
             "written down. Forcing moves come first, for both sides: here two "
             "checks, one capture and two attacks. The recapture 9.Qxe4 looks "
             "automatic and goes on the list with the rest."),
    ("Analyze", "Each candidate is followed once, far enough to judge where it "
                "ends, and then left alone. Going back and forth between two "
                "lines and then playing a third, unchecked, is the habit Kotov "
                "warned against."),
    ("Compare", "Four of the five lose material, the obvious recapture among "
                "them. 9.Qd8+ gives up the queen and mates. Tartakower resigned "
                "after 10.Bg5+; the mates are what he saw coming."),
]

# Gobet (1998), Table 1. Base moves: different first moves considered.
# Depth in plies (half moves). n = 12 per class.
GOBET = [
    {"cls": "Masters", "base": 3.2, "base_sd": 2.7, "depth": 5.0, "depth_sd": 2.3},
    {"cls": "Experts", "base": 4.8, "base_sd": 2.2, "depth": 4.6, "depth_sd": 1.9},
    {"cls": "Class A", "base": 6.5, "base_sd": 2.8, "depth": 3.7, "depth_sd": 2.1},
    {"cls": "Class B", "base": 4.8, "base_sd": 2.9, "depth": 2.9, "depth_sd": 1.1},
]

FINDINGS = [
    ("de Groot, 1946", "Grandmasters and experts looked at about as many moves; the grandmasters' were better."),
    ("Klein and others, 1995", "The first move a skilled player thinks of is usually a good one."),
    ("Campitelli and Gobet, 2004", "Strong players search far more when a position demands it."),
    ("Chessable, 2024", "Told to consider candidate moves, 207 players solved tactics no better."),
]

REFS = [
    ("Campitelli, G., &amp; Gobet, F. (2004). Adaptive expert decision making: "
     "Skilled chess players search more and deeper. <i>ICGA Journal, 27</i>(4), 209-216.",
     "https://doi.org/10.3233/ICG-2004-27403"),
    ("Chessable Science Team. (2024). <i>Candidate moves: When you see a good move, "
     "look for a better one</i> [Research paper]. Chessable.",
     "https://www.chessable.com/blog/wp-content/uploads/2024/04/Candidate-Moves-Research-Paper-final-version-April-15-2024-Chessable-science-team.pdf"),
    ("de Groot, A. D. (1965). <i>Thought and choice in chess</i>. Mouton. "
     "(Original work published 1946)", ""),
    ("Gobet, F. (1998). Chess players' thinking revisited. <i>Swiss Journal of "
     "Psychology, 57</i>, 18-32.",
     "https://www.academia.edu/92473745/Chess_players_thinking_revisited"),
    ("Klein, G., Wolf, S., Militello, L., &amp; Zsambok, C. (1995). Characteristics "
     "of skilled option generation in chess. <i>Organizational Behavior and Human "
     "Decision Processes, 62</i>(1), 63-69.",
     "https://doi.org/10.1006/obhd.1995.1031"),
    ("Kotov, A. (1971). <i>Think like a grandmaster</i> (B. Cafferty, Trans.). Batsford.", ""),
    ("Winter, E. (n.d.). R&eacute;ti v Tartakower, Vienna, 1910. <i>Chess Notes</i>.",
     "https://www.chesshistory.com/winter/extra/retitartakower.html"),
]
