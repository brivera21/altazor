#!/usr/bin/env python3
"""Check intuition.html, Board Intuition.

The mobility heat maps and the rest of the piece vision topics moved to the
piece pages (knight.html to king.html), where verify_chess_pages.py checks
every count against an independent one. What stays here is the geography
of the board and the endgame rules, so this checks that the page carries
exactly those two groups, that each topic draws, and that the page links
to the pages the vision topics went to.

Usage: python3 verify_intuition.py
"""
import json
import re
import sys
from pathlib import Path

PAGE = Path(__file__).parent.parent / "intuition.html"
fails = []


def check(ok, what):
    print(("  ok   " if ok else "  FAIL ") + what)
    if not ok:
        fails.append(what)


html = PAGE.read_text(encoding="utf-8")
m = re.search(r"const TOPICS\s*=\s*(\[.*?\]);\s*\n", html, re.S)
topics = json.loads(m.group(1))
groups = [t["g"] for t in topics]
check(set(groups) == {"Geography", "Endgame rules"}, f"two groups: {sorted(set(groups))}")
check(not any(t.get("numbers") for t in topics), "no mobility counts left on this page")
for f in ("knight.html", "bishop.html", "rook.html", "queen.html", "king.html"):
    check(f'href="{f}"' in html, f"links to {f}")

from playwright.sync_api import sync_playwright  # noqa: E402
with sync_playwright() as p:
    br = p.chromium.launch()
    pg = br.new_page(viewport={"width": 1200, "height": 1200})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.resolve().as_uri())
    pg.wait_for_timeout(500)
    n = pg.evaluate("()=>document.querySelectorAll('.menu button[data-i]').length")
    check(n == len(topics), f"{n} topics in the menu")
    for i in range(n):
        pg.click(f'.menu button[data-i="{i}"]')
        pg.wait_for_timeout(120)
    bad = pg.evaluate("()=>[...document.querySelectorAll('rect.sq')].filter(r=>!r.getAttribute('fill')||r.getAttribute('fill').includes('NaN')).length")
    check(bad == 0, "every square has a usable fill after every topic")
    check(not errs, "no script errors" + (f" ({errs[0]})" if errs else ""))
    br.close()

print()
print("all checks pass" if not fails else f"{len(fails)} failed")
sys.exit(1 if fails else 0)
