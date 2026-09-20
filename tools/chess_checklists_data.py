#!/usr/bin/env python3
"""Brian's three chess checklists, transcribed from his own sheets.

S.C.O.U.T. is the five-step check before a move. I.M.B.A.L.A.N.C.E.S. is
the ten features to weigh when judging a position. P.L.A.N. is the four
stages of building a middlegame plan.

The wording is his. What his sheets carried under "Memory Trick",
"Remember", "Key Insight" and "Quick Tip for Success" is left out at his
request; nothing else was dropped, and nothing was added.
"""

# ---- S.C.O.U.T. : the move check ----
# key, letter, name, prompt, two questions
SCOUT = [
    ("safety", "S", "Safety", "Is anything of yours loose?",
     ["King safe?", "Pieces protected?"]),
    ("checks", "C", "Checks", "What is forcing?",
     ["Checks available?", "Tactical shots?"]),
    ("opponent", "O", "Opponent", "What did the last move do?",
     ["What did they do?", "What's the threat?"]),
    ("upgrade", "U", "Upgrade", "Can the position be improved?",
     ["Improve position?", "Better activity?"]),
    ("test", "T", "Test", "Does the move survive a reply?",
     ["Their best reply?", "Happy with result?"]),
]

# ---- I.M.B.A.L.A.N.C.E.S. : the ten features ----
# key, letter, name, headline, three questions
IMBALANCES = [
    ("initiative", "I", "Initiative", "Who controls the tempo?",
     ["Are you making threats or defending?",
      "Can you force your opponent to respond?",
      "Who moved last piece to better square?"]),
    ("material", "M", "Material", "Piece count and value",
     ["Count points: Queen=9, Rook=5, Bishop/Knight=3, Pawn=1",
      "Did you trade wisely?",
      "Any hanging pieces?"]),
    ("bishops", "B", "Bishops", "Bishops vs. knights",
     ["Are there many pawns in center (knights better)?",
      "Long open diagonals (bishops better)?",
      "Which pieces fit your position?"]),
    ("activity", "A", "Activity", "How useful are your pieces?",
     ["Are your pieces attacking/defending something?",
      "Can you improve worst-placed piece?",
      "Any pieces doing nothing?"]),
    ("lines", "L", "Lines", "Open files and diagonals",
     ["Can you put rook on open file?",
      "Are your bishops blocked by your pawns?",
      "Who controls the center squares?"]),
    ("attacks", "A", "Attacks", "Who's attacking whom?",
     ["Is enemy king safe (look for weak squares)?",
      "Is your king safe from checks/threats?",
      "Which attack comes first?"]),
    ("numbers", "N", "Numbers", "Pawn quantity and quality",
     ["More pawns on one side of board?",
      "Any passed pawns (no enemy pawns blocking)?",
      "Connected vs scattered pawns?"]),
    ("castling", "C", "Castling", "King safety",
     ["Have both sides castled?",
      "Are pawns in front of king moved?",
      "Can you attack uncastled king?"]),
    ("endgame", "E", "Endgame", "What happens later?",
     ["If pieces get traded, who's better?",
      "Can your king walk to center safely?",
      "Better pawn structure for endgame?"]),
    ("space", "S", "Space", "Territory control",
     ["Do your pawns control more squares?",
      "Can your pieces move freely?",
      "Is opponent's pieces cramped/limited?"]),
]

# ---- P.L.A.N. : the four stages ----
# key, letter, name, lead, how many may be chosen, the options
PLAN = [
    ("pinpoint", "P", "Pinpoint the imbalances",
     "Look for these key imbalances on the board", "many", [
         ("material", "Material", "Hanging/underdefended pieces"),
         ("squares", "Square control", "Weak squares, outposts"),
         ("pawns", "Pawn structure", "Isolated, doubled, weak pawns"),
         ("time", "Time", "Development/tempo advantages"),
         ("king", "King safety", "Exposed king, weak shelter"),
         ("space", "Space", "Territorial control, cramped positions"),
         ("activity", "Piece activity", "Passive pieces, bad bishops"),
     ]),
    ("locate", "L", "Locate where to attack",
     "Choose your battlefield based on the imbalances you pinpointed", "one", [
         ("queenside", "Queenside", "Attack weak pawns, create passed pawns"),
         ("center", "Center", "Fight for key squares, control files"),
         ("kingside", "Kingside", "Target enemy king, pawn storms"),
     ]),
    ("arrange", "A", "Arrange your pieces",
     "Identify the best squares for each piece to support your attack plan", "many", [
         ("outposts", "Outposts", "Pawn-defended squares"),
         ("holes", "Holes", "Weak squares in enemy camp"),
         ("open", "Open files", "Clear verticals for rook activity"),
         ("halfopen", "Half-open files", "Files with only opponent pawns"),
         ("diagonals", "Long diagonals", "Key highways for bishops"),
         ("central", "Central squares", "e4, d4, e5, d5"),
         ("blockade", "Blockade squares", "Stop dangerous pawns"),
         ("advanced", "Advanced squares", "Deep penetration points"),
     ]),
    ("nail", "N", "Nail your move",
     "Based on pinpointed imbalances, chosen attack location, and piece arrangements", "all", [
         ("generate", "Generate", "Checks, captures, threats. Improve worst piece. Advance plan"),
         ("calculate", "Calculate", "Safety check. Replies. Look 2-3 moves ahead. "
                                    "Risk/reward, gains should outweigh losses"),
         ("execute", "Execute", "Commit to calculated decisions, avoid analysis paralysis. "
                                "Re-evaluate after opponent responds"),
     ]),
]

# the two lists that hang off Calculate
RISKS = "Material loss, king exposure, weak squares, tempo waste"
REWARDS = "Material gain, better position, attack chances, initiative"

# the line his sheet carries above the P.L.A.N. stages
PLAN_GOAL = ("Strengthen your position until an opportunity for a concrete "
             "attack presents itself.")
