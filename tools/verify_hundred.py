#!/usr/bin/env python3
"""Verify scifi-hundred.html against what the page actually draws.

Offline (network cut): a hundred books ranked by citation share, the bars
in descending order, the language colours and their counts, the Hugo and
Nebula pips against the site's own award roster, the sorts and filters,
the card's arithmetic, citations, no JS errors. Covers are a view-time
fetch, checked live after publishing instead.

Usage: python3 verify_hundred.py
"""
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from scifi_hundred import BOOKS                      # noqa: E402
from scifi_data import AWARDS                        # noqa: E402

PAGE = Path(__file__).parent.parent / "scifi-hundred.html"
fails = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name
          + (f"  [{detail}]" if detail and not ok else ""))
    if not ok:
        fails.append(name)


def norm(s):
    s = s.lower().replace("’", "'")
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return re.sub(r"^(the|a|an) ", "", s)


with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1400, "height": 1050})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("**/*", lambda r: r.abort()
             if r.request.url.startswith("http") else r.continue_())
    pg.goto(PAGE.as_uri())
    pg.wait_for_timeout(600)

    st = pg.evaluate("window.__hundred()")
    check("a hundred books", st["books"] == 100, str(st["books"]))
    check("ranks run 1 to 100 with no gap", st["ranked"])
    check("the shares never rise as the rank falls", st["ordered"])
    check("all hundred rows drawn", st["rows"] == 100, str(st["rows"]))
    rows = pg.evaluate("document.querySelectorAll('#csvg [data-i]').length")
    check("a row in the chart for each", rows == 100, str(rows))

    # every book's ratio agrees with its percentage
    ok = pg.evaluate("BOOKS.every(b=>b.c>0&&b.c<=b.e"
                     "&&Math.abs(Math.round(100*b.c/b.e)-b.p)<=1)")
    check("every share matches its own citation ratio", ok)

    # the bar length is the share
    bar = pg.evaluate(
        "(()=>{const g=document.querySelectorAll('#csvg [data-i]');"
        "const w=i=>+g[i].querySelectorAll('rect')[1].getAttribute('width');"
        "return [w(0),w(99),BOOKS[0].p,BOOKS[99].p];})()")
    check("the bar is the share, not the rank",
          abs(bar[0] / bar[1] - bar[2] / bar[3]) < 0.02, str(bar))

    # languages
    check("four languages among the hundred", st["langs"] == 4, str(st["langs"]))
    check("ninety-five were written in English", st["english"] == 95,
          str(st["english"]))
    langs = pg.evaluate("[...new Set(BOOKS.map(b=>b.l))].sort().join(',')")
    check("the other five are French, Polish and Russian",
          langs == "en,fr,pl,ru", langs)

    # the award pips agree with the site's own roster
    aw = {}
    for _y, title, _a, hugo, nebula in AWARDS:
        d = aw.setdefault(norm(title), {})
        if hugo:
            d["h"] = hugo
        if nebula:
            d["n"] = nebula
    want = {b[1]: aw.get(norm(b[1]), {}) for b in BOOKS}
    got = pg.evaluate("Object.fromEntries(BOOKS.map(b=>[b.n,"
                      "{h:b.hu||0,n:b.ne||0}]))")
    bad = [t for t, a in want.items()
           if (a.get("h", 0), a.get("n", 0)) != (got[t]["h"], got[t]["n"])]
    check("every Hugo and Nebula pip matches the award roster",
          not bad, ", ".join(bad[:4]))
    check("forty of the hundred hold one", st["awarded"] == 40,
          str(st["awarded"]))

    # the card
    pg.evaluate("show(0)")
    pg.wait_for_timeout(120)
    card = pg.evaluate("document.querySelector('.card').textContent")
    check("the card counts the lists rather than asserting a rank",
          "39 of the 41 lists" in card, card[:90])
    check("and names the awards it holds", "Hugo 1966" in card)
    pg.evaluate("show(39)")
    pg.wait_for_timeout(120)
    card = pg.evaluate("document.querySelector('.card').textContent")
    check("a translated novel says when it first appeared",
          "1961" in card and "Polish" in card, card[:120])
    pg.evaluate("show(4)")
    pg.wait_for_timeout(120)
    card = pg.evaluate("document.querySelector('.card').textContent")
    check("a book with no award says so", "No Hugo or Nebula" in card)

    # sorts and filters
    pg.click("#bYear")
    pg.wait_for_timeout(200)
    yrs = pg.evaluate(
        "[...document.querySelectorAll('#csvg [data-i]')].map(g=>"
        "+g.querySelectorAll('text')[2].textContent)")
    check("by year runs oldest first",
          yrs == sorted(yrs) and yrs[0] == 1818, f"{yrs[:3]}")
    pg.click("#bRank")
    pg.wait_for_timeout(200)
    pg.click("#bAward")
    pg.wait_for_timeout(200)
    st = pg.evaluate("window.__hundred()")
    check("the award filter leaves the forty", st["rows"] == 40, str(st["rows"]))
    pg.click("#bAward")
    pg.wait_for_timeout(150)
    pg.evaluate("document.querySelector('#legend [data-l=\"en\"]').click()")
    pg.wait_for_timeout(200)
    st = pg.evaluate("window.__hundred()")
    check("switching English off leaves the five", st["rows"] == 5,
          str(st["rows"]))
    pg.evaluate("document.querySelector('#legend [data-l=\"en\"]').click()")
    pg.wait_for_timeout(150)
    pg.fill("#q", "Le Guin")
    pg.wait_for_timeout(250)
    st = pg.evaluate("window.__hundred()")
    check("the search finds an author", st["rows"] == 2, str(st["rows"]))
    pg.fill("#q", "zzzqqq")
    pg.wait_for_timeout(200)
    check("a search with nothing in it says so",
          "nothing left" in pg.evaluate("document.querySelector('#csvg')"
                                        ".textContent"))
    pg.fill("#q", "")
    pg.wait_for_timeout(150)

    html = PAGE.read_text(encoding="utf-8")
    for frag in ["classicsofsciencefiction.com/classics-of-science-fiction-list/by-rank/",
                 "classicsofsciencefiction.com/essays/statistics-and-math/",
                 "thehugoawards.org", "nebulas.sfwa.org", "openlibrary.org",
                 "en.wikipedia.org/wiki/Solaris_(novel)"]:
        check(f"cites {frag}", frag in html)

    check("no JS errors", not errs, "; ".join(errs)[:140])
    br.close()

if fails:
    raise SystemExit(f"{len(fails)} check(s) failed")
print("all checks passed")
