"""Check scout.html, imbalances.html and plan.html against Brian's sheets.

  the data     five steps of two questions, ten features of three, four
               stages of twenty-one options between them; the letters
               spell S.C.O.U.T., I.M.B.A.L.A.N.C.E.S. and P.L.A.N.; every
               line of wording on the three pages is on his sheets, and
               none of the four headings he asked to drop survives
  the run      a step clears on two yes answers and flags on one no; the
               run moves to the next open step; the verdict follows
  the games    every feature has a played game; every move list replays
               legally from the first move; the key move is made by the side
               the note claims; the four that end in mate end in the mate
               that was recorded; the board draws the right position
  the plan     a battlefield is one at a time, the other stages take as
               many as are chosen, and the sentence is built from them
  the copy     no em dashes, no dependencies, American spelling, and the
               Chess section lists all three
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from chess_checklists_data import SCOUT, IMBALANCES, PLAN, RISKS, REWARDS
from chess_examples_data import EXAMPLES

ROOT = Path(__file__).resolve().parent.parent
PAGES = {"scout": ROOT / "scout.html", "imbalances": ROOT / "imbalances.html",
         "plan": ROOT / "plan.html"}
# the four headings he asked to be left off
DROPPED = ("Memory Trick", "Key Insight", "Quick Tip", "A SCOUT explores",
           "planning a heist", "bad plan is better", "don't move pieces randomly")
fails = []


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


print("--- the data ---")
check("".join(s[1] for s in SCOUT) == "SCOUT", "the five letters spell SCOUT")
check("".join(f[1] for f in IMBALANCES) == "IMBALANCES", "the ten letters spell IMBALANCES")
check("".join(p[1] for p in PLAN) == "PLAN", "the four letters spell PLAN")
check(all(len(s[4]) == 2 for s in SCOUT), "every step has two questions")
check(all(len(f[4]) == 3 for f in IMBALANCES), "every feature has three questions")
check(sum(len(p[5]) for p in PLAN) == 21, f"twenty-one options over the four stages",
      f"{sum(len(p[5]) for p in PLAN)}")
check([len(p[5]) for p in PLAN] == [7, 3, 8, 3], "seven imbalances, three battlefields, eight square types, three final steps",
      f"{[len(p[5]) for p in PLAN]}")
check([p[4] for p in PLAN] == ["many", "one", "many", "all"], "only the battlefield is a single choice")
check(len({s[0] for s in SCOUT}) == 5 and len({f[0] for f in IMBALANCES}) == 10,
      "no two steps or features share a key")
check(IMBALANCES[3][2] == "Activity" and IMBALANCES[5][2] == "Attacks",
      "the two A features are Activity and Attacks, kept apart")

print("--- the games ---")
import chess
check(set(EXAMPLES) == {f[0] for f in IMBALANCES}, "every feature has a game and no game is spare",
      f"{set(EXAMPLES) ^ {f[0] for f in IMBALANCES}}")
mates = []
for k, e in EXAMPLES.items():
    b = chess.Board()
    sans = []
    bad = None
    for t in e["moves"].split():
        try:
            m = b.parse_san(t)
        except Exception as ex:
            bad = f"{t}: {ex}"
            break
        sans.append(b.san(m))
        b.push(m)
    check(bad is None, f"{k}: the whole score replays legally", bad or "")
    if bad:
        continue
    check(e["key"] in sans, f"{k}: the key move {e['key']} is in the score")
    i = sans.index(e["key"])
    check(("White" if i % 2 == 0 else "Black") == e["side"],
          f"{k}: {e['key']} is played by {e['side']}", f"ply {i}")
    check(e["source"].startswith("https://en.wikipedia.org/wiki/"), f"{k}: the score cites where it came from")
    check(len(e["note"].split()) <= 70, f"{k}: its note is short", f"{len(e['note'].split())} words")
    if b.is_checkmate():
        mates.append(k)
check(sorted(mates) == ["activity", "castling", "initiative", "material"],
      "the four games that finish in mate are the four recorded as mates", f"{sorted(mates)}")

print("--- the copy ---")
for name, page in PAGES.items():
    html = page.read_text(encoding="utf-8")
    check("—" not in html, f"{name}: no em dashes")
    check("<script src" not in html and 'rel="stylesheet"' not in html and "@import" not in html,
          f"{name}: no dependencies")
    for d in DROPPED:
        check(d.lower() not in html.lower(), f"{name}: nothing left of “{d}”")
am = subprocess.run([sys.executable, str(ROOT / "tools" / "americanize.py"), "--check"],
                    capture_output=True, text=True).stdout
check(not any(n + ".html" in am for n in PAGES), "americanize.py finds nothing to change")
section = (ROOT / "chess.html").read_text(encoding="utf-8")
check('href="scout.html">S.C.O.U.T.' in section, "the Chess section lists S.C.O.U.T.")
check('href="imbalances.html">I.M.B.A.L.A.N.C.E.S.' in section, "and I.M.B.A.L.A.N.C.E.S.")
check('href="plan.html">P.L.A.N.' in section, "and P.L.A.N.")
cols = re.search(r"<h2>Openings</h2>(.*?)<h2>Middle Games</h2>(.*?)<h2>Endgames</h2>", section, re.S)
check("scout.html" in cols.group(1), "S.C.O.U.T. sits under Openings")
check("imbalances.html" in cols.group(2) and "plan.html" in cols.group(2),
      "the other two sit under Middle Games")

print("--- the run, the balance and the plan ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1100})
    errs = []
    pg.on("pageerror", lambda x: errs.append(str(x)))

    # ---- SCOUT
    pg.goto(PAGES["scout"].as_uri())
    pg.wait_for_selector("#ssvg")

    def sc(q=None):
        return pg.evaluate("(q)=>window.__scout(q)", q)

    s = sc()
    check(s["nodes"] == 5 and s["sel"] == 0 and s["cleared"] == 0, "opens on the first step with nothing answered")
    check(s["buttons"] == 4, "the first step offers a yes and a no for each of its two questions", f"{s['buttons']}")
    check(s["name"] == "Safety" and "1 of 5" in s["kind"], "the first step is Safety")
    sc({"answer": [0, 0, "yes"]})
    s = sc({"answer": [0, 1, "yes"]})
    check(s["states"][0] == "clear" and s["cleared"] == 1, "two yes answers clear a step")
    check(s["sel"] == 1, "and the run moves on to the next open step", f"sel {s['sel']}")
    s = sc({"answer": [1, 0, "no"]})
    check(s["states"][1] == "flag" and s["flagged"] == 1, "a single no flags a step")
    check("rethinking" in s["src"], "and the verdict says the move is worth rethinking", s["src"])
    for i in range(5):
        for j in range(2):
            sc({"answer": [i, j, "yes"]})
    s = sc()
    check(s["cleared"] == 5 and s["flagged"] == 0 and "All five clear" in s["src"],
          "all yes answers clear the whole run", s["src"])
    s = sc({"reset": True})
    check(s["cleared"] == 0 and s["sel"] == 0 and all(v == "open" for v in s["states"]),
          "starting over empties the run")
    for st in SCOUT:
        sc({"select": SCOUT.index(st)})
        got = sc()
        body = pg.eval_on_selector("#numTxt", "e=>e.innerText")
        check(all(q in body for q in st[4]), f"{st[2]}: both of his questions are on the page",
              body[:80])

    # ---- IMBALANCES
    pg.goto(PAGES["imbalances"].as_uri())
    pg.wait_for_selector("#board svg")

    def im(q=None):
        return pg.evaluate("(q)=>window.__imb(q)", q)

    s = im()
    check(s["letters"] == 10, "ten letter buttons, one per feature", f"{s['letters']}")
    check(s["sel"] == "initiative" and s["ply"] == s["keyPly"],
          "opens on Initiative at the move the game turns on")
    check(s["white"] == "Paul Morphy" and s["key"] == "Nxb5", "which is Morphy's knight to b5")
    for k, e in EXAMPLES.items():
        s = im({"pick": k})
        check(s["key"] == e["key"] and s["side"] == e["side"] and s["white"] == e["white"],
              f"{k}: the page shows {e['white']}'s game and {e['key']} by {e['side']}",
              f"{s['white']} / {s['key']} / {s['side']}")
        check(s["moves"] == s["plies"], f"{k}: the whole score is on the page",
              f"{s['moves']} of {s['plies']}")
        check(e["note"][:40] in s["body"], f"{k}: its note is in the card")
        # the drawn board matches the position python-chess computed
        b = chess.Board()
        for t in e["moves"].split()[:s["ply"]]:
            b.push_san(t)
        check(s["fen"] == b.fen().split(" ")[0], f"{k}: the board draws the played position",
              f"{s['fen']} vs {b.fen().split(' ')[0]}")
    # stepping
    s = im({"pick": "initiative"})
    n = s["plies"]
    s = im({"ply": 0})
    check(s["fen"] == chess.Board().fen().split(" ")[0], "ply zero is the starting position")
    s = im({"ply": n})
    b = chess.Board()
    for t in EXAMPLES["initiative"]["moves"].split():
        b.push_san(t)
    check(s["fen"] == b.fen().split(" ")[0] and b.is_checkmate(),
          "the last ply is the final position, and it is mate")
    pg.click("#keyBtn")
    s = im()
    check(s["ply"] == s["keyPly"], "the move button returns to the key position")
    pg.click("#prevBtn")
    check(im()["ply"] == s["keyPly"] - 1, "back steps one ply")
    pg.click("#nextBtn")
    check(im()["ply"] == s["keyPly"], "forward steps one ply")
    check(pg.eval_on_selector_all("#strip .mv.key", "e=>e.length") == 1,
          "the key move is marked once in the score")
    check("wikipedia.org" in pg.eval_on_selector("#srcTxt a", "e=>e.href"),
          "the card links to the article the score came from")

    # ---- PLAN
    pg.goto(PAGES["plan"].as_uri())
    pg.wait_for_selector("#stages")

    def pl(q=None):
        return pg.evaluate("(q)=>window.__plan(q)", q)

    s = pl()
    check(s["stages"] == 4 and s["options"] == 21, "four stages and twenty-one options are drawn",
          f"{s['stages']} / {s['options']}")
    check(s["sentence"] == "Nothing pinpointed yet.", "opens with nothing chosen", s["sentence"])
    pl({"pick": [0, 1]})
    s = pl({"pick": [0, 4]})
    check(s["pick"][0] == [1, 4] and "square control and king safety" in s["sentence"],
          "two imbalances go into the sentence", s["sentence"])
    pl({"pick": [1, 2]})
    s = pl({"pick": [1, 0]})
    check(s["pick"][1] == [0] and "queenside" in s["sentence"] and "kingside" not in s["sentence"],
          "the battlefield replaces itself rather than adding", s["sentence"])
    pl({"pick": [2, 0]})
    s = pl({"pick": [2, 3]})
    check("outposts and half-open files" in s["sentence"], "the square types are listed", s["sentence"])
    for j in range(3):
        pl({"pick": [3, j]})
    s = pl()
    check("the plan is ready" in s["sentence"], "with all three final steps the plan reads as ready",
          s["sentence"])
    body = pg.eval_on_selector("#numTxt", "e=>e.innerText")
    check(RISKS in body and REWARDS in body, "the risks and rewards show on the last stage")
    s = pl({"reset": True})
    check(s["sentence"] == "Nothing pinpointed yet." and all(not a for a in s["pick"]),
          "starting over empties the plan")
    txt = pg.eval_on_selector("#stages", "e=>e.innerText")
    for st in PLAN:
        check(st[2] in txt and st[3] in txt, f"{st[1]}: its name and lead are his")
        for o in st[5]:
            check(o[1] in txt and o[2] in txt, f"{st[1]} / {o[1]}: his wording is on the page")

    check(not errs, "no script errors", "; ".join(errs))
    br.close()

print()
if fails:
    print(f"{len(fails)} FAILED:")
    for x in fails:
        print("  -", x)
    sys.exit(1)
print("everything squares")
