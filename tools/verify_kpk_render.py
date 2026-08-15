"""Render endgames.html in a headless browser and check the placement map.

For a handful of white setups the painted square fills, the dot/dash marks
and the counts in the panel are compared with an independent computation
from kpk_dtm.bin. Then the controls are exercised: the side-to-move toggle,
clicking a square to move a piece, and the arrow keys walking the pawn.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
D = Path("/home/claude/kbbtb/kpk_dtm.bin").read_bytes()
F = "abcdefgh"
WIN = ("#dfa42b", "#b07400")
DRW = ("#4f95ea", "#2f6cb8")
ILL = ("#4b5059", "#33373e")
PIECE = ("#c3cad4", "#7c8494")


def sq(n):
    return F.index(n[0]) + (int(n[1]) - 1) * 8


def nm(s):
    return F[s % 8] + str(s // 8 + 1)


def tb(wk, bk, wp, stm):
    v = D[(((wk * 64 + bk) * 48 + (wp - 8)) * 2) + stm]
    return v - 256 if v > 127 else v


def adj(a, b):
    return max(abs(a % 8 - b % 8), abs(a // 8 - b // 8)) == 1


def pawn_att(wp, s):
    f, r = wp % 8, wp // 8
    if r + 1 > 7:
        return False
    return (f > 0 and s == (r + 1) * 8 + f - 1) or (f < 7 and s == (r + 1) * 8 + f + 1)


def expect(wk, wp, stm):
    """square -> (state, fill) plus the counts the panel should show."""
    out, win, drw, ill = {}, 0, 0, 0
    for s in range(64):
        dark = 1 if ((s % 8) + (s // 8 + 1)) % 2 == 1 else 0
        if s == wk or s == wp:
            out[s] = ("piece", PIECE[dark])
            continue
        if adj(s, wk) or (stm == 0 and pawn_att(wp, s)):
            out[s] = ("ill", ILL[dark])
            ill += 1
            continue
        if tb(wk, s, wp, stm) >= 0:
            out[s] = ("win", WIN[dark])
            win += 1
        else:
            out[s] = ("drw", DRW[dark])
            drw += 1
    return out, win, drw, ill


JS = """() => {
  const out = {fills:{}, marks:{}};
  document.querySelectorAll('rect.sq').forEach(r=>{
    out.fills['ab cdefgh'.replace(' ','')[+r.dataset.f]+r.dataset.r] =
      r.getAttribute('fill').toLowerCase();
  });
  const ng=document.getElementById('numbers');
  out.circles=ng.querySelectorAll('circle').length;
  out.dashes=ng.querySelectorAll('rect').length;
  out.stats=document.getElementById('mapstats').textContent;
  out.pieces=[...document.querySelectorAll('#pieces g')].map(g=>g.dataset.k+':'+
    g.querySelector('text').style.transform);
  out.census=getComputedStyle(document.getElementById('census')).display;
  return out;
}"""

CASES = [("e5", "e4", 0), ("e5", "e4", 1), ("a6", "a5", 0), ("e6", "e5", 0),
         ("c3", "b2", 1), ("h4", "h2", 0), ("d8", "d7", 1), ("b1", "g7", 0)]

fails = 0
with sync_playwright() as p:
    br = p.chromium.launch()
    pg = br.new_page()
    pg.goto((HERE.parent / "endgames.html").resolve().as_uri())
    pg.click(".menu button:text-is('Every placement')")
    for wkn, wpn, stm in CASES:
        wk, wp = sq(wkn), sq(wpn)
        pg.evaluate("([a,b,c])=>{mapWK=a;mapWP=b;mapSTM=c;paint();}", [wk, wp, stm])
        got = pg.evaluate(JS)
        exp, win, drw, ill = expect(wk, wp, stm)
        wrong = [nm(s) for s in range(64)
                 if got["fills"][nm(s)] != exp[s][1]]
        ok = not wrong and got["circles"] == win and got["dashes"] == drw
        ok = ok and f"{win}" in got["stats"] and f"{drw}" in got["stats"]
        ok = ok and got["census"] != "none"
        print("%-4s %-3s %-5s  win %2d draw %2d illegal %2d   %s"
              % ("K" + wkn, wpn, "W" if stm == 0 else "B", win, drw, ill,
                 "ok" if ok else "MISMATCH " + ",".join(wrong[:6])))
        if not ok:
            fails += 1
            print("   marks:", got["circles"], got["dashes"], "|", got["stats"])

    # controls
    pg.evaluate("()=>{mapWK=36;mapWP=28;mapSTM=0;mapPiece='K';paint();}")
    pg.click("#msB")
    s1 = pg.evaluate("()=>[mapSTM, document.getElementById('mapstats').textContent]")
    pg.click("#mpP")
    pg.keyboard.press("ArrowLeft")
    pg.keyboard.press("ArrowDown")
    s2 = pg.evaluate("()=>[mapWP, mapPiece]")
    pg.click("#sq-b7")            # place the pawn by clicking
    s3 = pg.evaluate("()=>mapWP")
    pg.click("#sq-b8")            # rank 8 is not a pawn square: must be ignored
    s4 = pg.evaluate("()=>mapWP")
    pg.click("#mpK")
    pg.click("#sq-h1")
    s5 = pg.evaluate("()=>mapWK")
    checks = [("side to move toggles", s1[0] == 1),
              ("stats redraw", "Black" in s1[1]),
              ("arrow keys walk the pawn", s2[0] == sq("d3") and s2[1] == "P"),
              ("click places the pawn", s3 == sq("b7")),
              ("rank 8 refused", s4 == sq("b7")),
              ("click places the king", s5 == sq("h1"))]
    for label, good in checks:
        print("%-28s %s" % (label, "ok" if good else "FAILED"))
        if not good:
            fails += 1
    pg.screenshot(path="/tmp/kpkmap.png", full_page=True)
    br.close()
print("failures:", fails)
