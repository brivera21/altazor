#!/usr/bin/env python3
"""Check what populous-countries.html does in a browser.

The static checks (ranks, leads, totals, flags) live in
verify_population_pages.py. This one opens the page and checks the parts
that move: the counters run from the moment the page opens at each place's
average second; a row answers the pointer and a click pins it; the heads
sort the table and the totals row stays last; the chosen country stays in
the card for comparison; the shares fold from one stacked bar into a
treemap whose areas are the populations; the notes sit in a closed
details; nothing is wider than a phone. No script errors.

Usage: python3 verify_populous.py
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from world_data import ROWS, WORLD  # noqa: E402

PAGE = Path(__file__).parent.parent / "populous-countries.html"
fails = []
SEC = 365.25 * 86400


def check(ok, name, detail=""):
    print(("ok   " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""))
    if not ok:
        fails.append(name)


with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1300, "height": 850})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("**/*", lambda r: r.abort()
             if r.request.url.startswith("http") else r.continue_())
    pg.goto(PAGE.as_uri())
    pg.wait_for_timeout(2500)

    # ---- the counters
    st = pg.evaluate("window.__pop()")
    born = int(pg.inner_text("#tBirths").split(" ")[0].replace(",", ""))
    want = WORLD["births"] / SEC * st["secs"]
    check(abs(born - want) < WORLD["births"] / SEC * 0.6 + 1,
          f"the births tile counts {born} after {st['secs']:.1f} s, the world's average second",
          f"{born} vs {want:.1f}")
    pop = int(pg.inner_text("#tPop").split(" ")[0].replace(",", ""))
    check(pop > WORLD["pop"], "the world tile has grown since the page opened", str(pop))
    pg.wait_for_timeout(1200)
    born2 = int(pg.inner_text("#tBirths").split(" ")[0].replace(",", ""))
    check(born2 > born, "and it keeps counting", f"{born} then {born2}")

    # ---- a row answers the pointer, a click pins it
    pg.hover("#tbl tbody tr[data-i='1'] td.ct")
    pg.wait_for_timeout(200)
    card = pg.inner_text("#card")
    check(ROWS[1][1] in card and "born" in card, f"hovering a row puts {ROWS[1][1]} in the card", card[:80])
    pg.click("#tbl tbody tr[data-i='2'] td.ct")
    pg.mouse.move(5, 5)
    pg.wait_for_timeout(250)
    card = pg.inner_text("#card")
    check(ROWS[2][1] in card and "PINNED" in card.upper(), "a click pins it and the card keeps it", card[:80])
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(200)
    check(pg.evaluate("window.__pop().pin") == -1 and "The world" in pg.inner_text("#card"),
          "Escape lets it go and the card returns to the world")

    # ---- the heads sort the table
    def order():
        return pg.evaluate("window.__pop().order")
    pg.click("button.sort[data-k='name']")
    pg.wait_for_timeout(900)
    o = order()
    names = [ROWS[i][1] for i in o]
    check(names == sorted(names, key=lambda n: n.lower()) or names[0] < names[-1],
          f"the name head sorts from {names[0]} to {names[-1]}")
    check(pg.evaluate("window.__pop().lastIsTotal"), "the totals row stays last")
    check(pg.evaluate("document.getElementById('tbl').classList.contains('resorted')"),
          "and the leads to the next row are hidden while the order is not by size")
    pg.click("button.sort[data-k='net']")
    pg.wait_for_timeout(900)
    o = order()
    nets = [ROWS[i][3] - ROWS[i][4] for i in o]
    check(all(a >= b for a, b in zip(nets, nets[1:])), "the net head sorts by growth, largest first")
    pg.click("button.sort[data-k='net']")
    pg.wait_for_timeout(900)
    o = order()
    check(ROWS[o[0]][3] - ROWS[o[0]][4] == min(nets), "a second click turns it round",
          ROWS[o[0]][1])
    pg.click("button.sort[data-k='ratio']")
    pg.wait_for_timeout(900)
    o = order()
    rat = [ROWS[i][4] / ROWS[i][3] for i in o]
    check(all(a >= b - 1e-12 for a, b in zip(rat, rat[1:])),
          f"the births and deaths head sorts by deaths over births, {ROWS[o[0]][1]} first")
    pg.click("button.sort[data-k='pop']")
    pg.wait_for_timeout(900)
    check(order() == list(range(len(ROWS))), "the population head restores the ranking")
    check(not pg.evaluate("document.getElementById('tbl').classList.contains('resorted')"),
          "and the leads come back")

    # ---- a country for comparison
    i_mx = next(i for i, r in enumerate(ROWS) if r[1] == "Mexico")
    pg.select_option("#home", str(i_mx))
    pg.hover("#tbl tbody tr[data-i='0'] td.ct")
    pg.wait_for_timeout(250)
    card = pg.inner_text("#card")
    k = ROWS[0][2] / ROWS[i_mx][2]
    kt = f"{round(k):,}" if k >= 10 else f"{k:.1f}"
    check("Mexico" in card and f"{kt} times as many people as Mexico" in card,
          "a chosen country stays in the card, with the ratio to the hovered one", card[-120:])
    check(pg.evaluate(f"document.querySelector(\"#tbl tr[data-i='{i_mx}']\").classList.contains('home')"),
          "and its row is marked in the table")

    # ---- the shares as areas
    pg.click("#bTree")
    pg.wait_for_timeout(250)
    st = pg.evaluate("window.__pop()")
    check(st["treeOn"] and 0 < st["fold"] < 1, f"the fold is under way after 0.25 s ({st['fold']:.2f})")
    pg.wait_for_timeout(1100)
    st = pg.evaluate("window.__pop()")
    check(st["fold"] == 1 and st["rects"] == len(ROWS), f"and done a second later, {st['rects']} areas")
    # the layout itself, before the drawn rectangles round it to two places
    areas = pg.evaluate("window.__tree.map(b=>b[2]*b[3])")
    tot = sum(areas)
    listed = sum(r[2] for r in ROWS)
    worst = max(abs(a / tot - r[2] / listed) for a, r in zip(areas, ROWS))
    check(worst < 1e-6 and abs(tot - 1000 * 560) < 1, "every area is its population's share",
          f"worst {worst:.2e}, total {tot:.1f}")
    boxes = pg.evaluate("window.__tree")
    over = sum(1 for x, y, w, h in boxes if x < -0.01 or y < -0.01
               or x + w > 1000.01 or y + h > 560.01)
    check(over == 0, "and none leaves the frame", str(over))
    pg.hover("#tree rect[data-i='3']")
    pg.wait_for_timeout(200)
    check(ROWS[3][1] in pg.inner_text("#card"), "an area answers the pointer like its row")
    pg.click("#bTree")
    pg.wait_for_timeout(1400)
    check(pg.evaluate("document.getElementById('tree').hidden"), "and folds away again")

    check(pg.evaluate("(()=>{const d=document.querySelector('details.sources');"
                      "return d&&!d.open&&d.textContent.includes('References');})()"),
          "the notes and references sit in a closed details")
    check(not errs, "no script errors", "; ".join(errs)[:200])

    ph = br.new_page(viewport={"width": 390, "height": 844})
    ph.route("**/*", lambda r: r.abort()
             if r.request.url.startswith("http") else r.continue_())
    ph.goto(PAGE.as_uri())
    ph.wait_for_timeout(400)
    over = ph.evaluate("document.documentElement.scrollWidth-innerWidth")
    check(over == 0, "nothing is wider than a 390 px screen", str(over))
    ph.close()
    br.close()

if fails:
    raise SystemExit(f"{len(fails)} check(s) failed")
print("all checks pass")
