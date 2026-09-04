#!/usr/bin/env python3
"""Verify cosmic-timeline.html against what the page actually draws.

Offline (network cut): thirteen events in order from the Big Bang to
Christianity, each with a date, a card and a live source; the three
scales place the same events differently and each is the arithmetic it
claims; the clock hides what has not happened yet; no JS errors.

Usage: python3 verify_cosmic.py
"""
import math
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from cosmic_data import EVENTS                       # noqa: E402

PAGE = Path(__file__).parent.parent / "cosmic-timeline.html"
fails = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name
          + (f"  [{detail}]" if detail and not ok else ""))
    if not ok:
        fails.append(name)


with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1400, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("**/*", lambda r: r.abort()
             if r.request.url.startswith("http") else r.continue_())
    pg.goto(PAGE.as_uri())
    pg.wait_for_timeout(500)

    st = pg.evaluate("window.__cosmic()")
    check("thirteen events", st["events"] == len(EVENTS), str(st["events"]))
    check("in order from the Big Bang to now", st["ordered"])
    check("every event carries a date, a card and a source", st["sourced"])
    marks = pg.evaluate("document.querySelectorAll('#tsvg [data-i]').length")
    check("a mark for each on the line", marks == len(EVENTS), str(marks))

    names = pg.evaluate("EV.map(e=>e.n)")
    for want in ["The Big Bang", "The first stars", "The Milky Way",
                 "The Sun", "The Earth", "Life", "Many cells",
                 "The first nervous systems", "Mammals", "Primates",
                 "Homo sapiens", "Christianity"]:
        check(f"{want} is on the line", want in names)

    # the ages agree with the dates
    ok = pg.evaluate("EV.every(e=>Math.abs((NOW-e.t)-e.age)<1)")
    check("years after the Big Bang match years before now", ok)
    bb = pg.evaluate("EV[0].t")
    check("the line starts at 13.8 billion years", abs(bb - 13.8e9) < 1e6,
          str(bb))
    chr_ = pg.evaluate("EV[EV.length-1].t")
    check("and ends within the last two thousand years", chr_ < 2100,
          str(chr_))

    # the three scales
    def xs():
        return pg.evaluate("EV.map(e=>Math.round(X(e.t)))")
    back = xs()
    pg.click("#bFwd")
    pg.wait_for_timeout(200)
    fwd = xs()
    pg.click("#bLin")
    pg.wait_for_timeout(200)
    even = xs()
    check("the three scales place the events differently",
          back != fwd and fwd != even and back != even)
    check("every scale runs left to right in time",
          all(a <= b for a, b in zip(back, back[1:]))
          and all(a <= b for a, b in zip(fwd, fwd[1:]))
          and all(a <= b for a, b in zip(even, even[1:])))
    # the even scale is what it says: distance proportional to time
    i_sun = names.index("The Sun")
    i_life = names.index("Life")
    got = (even[i_life] - even[i_sun]) / (even[-1] - even[0])
    want = (EVENTS[i_sun]["t"] - EVENTS[i_life]["t"]) / 13.8e9
    check("the even scale is proportional to time", abs(got - want) < 0.02,
          f"{got:.3f} vs {want:.3f}")
    # the even scale crushes the recent events, which is its point
    late = even[names.index("Mammals")]
    check("on the even scale everything after the mammals is one place",
          even[-1] - late < 20, str(even[-1] - late))
    # the log scale gives them room
    pg.click("#bBack")
    pg.wait_for_timeout(200)
    check("the log scale spreads them out",
          back[-1] - back[names.index("Mammals")] > 200,
          str(back[-1] - back[names.index("Mammals")]))

    # the clock
    pg.eval_on_selector("#t", "el=>{el.value=0;"
                        "el.dispatchEvent(new Event('input'))}")
    pg.wait_for_timeout(200)
    st = pg.evaluate("window.__cosmic()")
    check("at the first year only the Big Bang has happened",
          st["visible"] == 1, str(st["visible"]))
    pg.eval_on_selector("#t", "el=>{el.value=1000;"
                        "el.dispatchEvent(new Event('input'))}")
    pg.wait_for_timeout(200)
    st = pg.evaluate("window.__cosmic()")
    check("and at the end all of them have", st["visible"] == len(EVENTS),
          str(st["visible"]))
    txt = pg.evaluate("document.getElementById('clock').textContent")
    check("the clock says where it is", "13.8 billion" in txt, txt)

    # the card
    pg.evaluate("show(EV.findIndex(e=>e.n==='Life'))")
    pg.wait_for_timeout(120)
    card = pg.evaluate("document.querySelector('.card').textContent")
    check("a disputed claim says so and gives the firmer date",
          "disputed" in card and "3.48" in card, card[:110])
    link = pg.evaluate("document.querySelector('#srcTxt a').href")
    check("and links its source", link.startswith("https://"), link)
    pg.evaluate("show(EV.findIndex(e=>e.n==='Christianity'))")
    pg.wait_for_timeout(120)
    card = pg.evaluate("document.querySelector('.card').textContent")
    check("the last mark is dated by scholarship, not by faith",
          "AD 33" in card and "Nicaea" in card, card[:110])

    html = PAGE.read_text(encoding="utf-8")
    for e in EVENTS:
        check(f"cites the source for {e['n']}", e["u2"] in html)

    check("no JS errors", not errs, "; ".join(errs)[:140])
    br.close()

if fails:
    raise SystemExit(f"{len(fails)} check(s) failed")
print("all checks passed")
