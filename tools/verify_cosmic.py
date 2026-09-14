#!/usr/bin/env python3
"""Verify cosmic-timeline.html against what the page actually draws.

Offline (network cut): thirteen milestones in order from the Big Bang to
Christianity, each with a date, a card and a live source; thirteen
strands of detail beneath them, in order, every mark reachable and
named; the four scales place the same events differently and each is the
arithmetic it claims, with the Sun landing on the middle of its own
scale and nowhere near it on the others; the strand chips hide and show
their rows; the corrections are on the page; no JS errors.

Usage: python3 verify_cosmic.py
"""
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from bighistory import DETAIL, FIXED, STRANDS        # noqa: E402
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
    pg = br.new_page(viewport={"width": 1400, "height": 1400})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("**/*", lambda r: r.abort()
             if r.request.url.startswith("http") else r.continue_())
    pg.goto(PAGE.as_uri())
    pg.wait_for_timeout(600)

    st = pg.evaluate("window.__cosmic()")
    check("thirteen milestones", st["events"] == len(EVENTS),
          str(st["events"]))
    check("in order from the Big Bang to now", st["ordered"])
    check("every milestone carries a date, a card and a source",
          st["sourced"])
    marks = pg.evaluate("document.querySelectorAll('#tsvg [data-i]').length")
    check("a mark for each on the line", marks == len(EVENTS), str(marks))

    names = pg.evaluate("EV.map(e=>e.n)")
    for want in ["The Big Bang", "The first stars", "The Milky Way",
                 "The Sun", "The Earth", "Life", "Many cells",
                 "The first nervous systems", "Mammals", "Primates",
                 "Homo sapiens", "Christianity"]:
        check(f"{want} is on the line", want in names)

    ok = pg.evaluate("EV.every(e=>Math.abs((NOW-e.t)-e.age)<1)")
    check("years after the Big Bang match years before now", ok)
    bb = pg.evaluate("EV[0].t")
    check("the line starts at 13.8 billion years", abs(bb - 13.8e9) < 1e6,
          str(bb))

    # --- the detail carried over from the notebook
    check("the detail is all there", st["detail"] == len(DETAIL),
          str(st["detail"]))
    check("and runs oldest first", st["detOrdered"])
    check("thirteen strands", st["strands"] == len(STRANDS),
          str(st["strands"]))
    check("a row for each strand", st["rows"] == len(STRANDS),
          str(st["rows"]))
    named = pg.evaluate("DET.every(d=>d.n&&d.n.length>2&&d.t>0)")
    check("every detail mark is named and dated", named)
    keys = pg.evaluate("(()=>{const s=new Set(ST.map(x=>x.k));"
                       "return DET.every(d=>s.has(d.k));})()")
    check("and sits in a strand the legend carries", keys)
    dots = st["dots"]
    check("nearly every mark lands inside the plot",
          dots > len(DETAIL) * 0.97, f"{dots} of {len(DETAIL)}")
    span_ok = pg.evaluate("DET[0].t>1e10 && DET[DET.length-1].t<10")
    check("the detail runs from before the first stars to this decade",
          span_ok)

    # --- the four scales
    def xs():
        return pg.evaluate("EV.map(e=>Math.round(X(e.t)))")

    back = xs()
    pg.click("#bFwd")
    pg.wait_for_timeout(200)
    fwd = xs()
    pg.click("#bSun")
    pg.wait_for_timeout(200)
    sun = xs()
    sunst = pg.evaluate("window.__cosmic()")
    pg.click("#bLin")
    pg.wait_for_timeout(200)
    even = xs()
    check("the four scales place the events differently",
          len({tuple(back), tuple(fwd), tuple(sun), tuple(even)}) == 4)
    for nm, v in [("back", back), ("forward", fwd), ("sun", sun),
                  ("even", even)]:
        check(f"the {nm} scale runs left to right in time",
              all(a <= b for a, b in zip(v, v[1:])))

    # the Sun scale does what its name says
    check("the Sun sits on the middle of its own scale",
          abs(sunst["sunX"] - sunst["midX"]) <= 1,
          f'{sunst["sunX"]} vs {sunst["midX"]}')
    i_sun = names.index("The Sun")
    check("and nowhere near the middle on the even scale",
          abs(even[i_sun] - sunst["midX"]) > 100,
          f'{even[i_sun]} vs {sunst["midX"]}')
    check("the Big Bang sits at the far left of the Sun scale", sun[0] <= 113,
          str(sun[0]))
    check("and half the line is the time before the Sun",
          400 < sun[i_sun] - sun[0] < 440, str(sun[i_sun] - sun[0]))
    # the nine billion years before the Sun get half the width here, where
    # the default scale gives them a twentieth
    check("which the back scale crushes into a corner",
          back[i_sun] - back[0] < 60, str(back[i_sun] - back[0]))
    # and everything since the Sun still has room, unlike the even scale
    i_hs = names.index("Homo sapiens")
    check("the Sun scale keeps the human marks apart",
          sun[-1] - sun[i_hs] > 60, str(sun[-1] - sun[i_hs]))
    check("where the even scale puts them on one spot",
          even[-1] - even[i_hs] < 3, str(even[-1] - even[i_hs]))
    # every strand still reaches the plot on the Sun scale
    pg.click("#bSun")
    pg.wait_for_timeout(200)
    perrow = pg.evaluate(
        "(()=>{const o={};for(const d of DET){const x=X(d.t);"
        "if(x>=111&&x<=967) o[d.k]=(o[d.k]||0)+1;}return o;})()")
    check("and every strand still lands on it",
          len(perrow) == len(STRANDS) and min(perrow.values()) >= 5,
          str(sorted(perrow.items())))
    pg.click("#bLin")
    pg.wait_for_timeout(150)

    # the even scale is what it says: distance proportional to time
    i_life = names.index("Life")
    got = (even[i_life] - even[i_sun]) / (even[-1] - even[0])
    want = (EVENTS[i_sun]["t"] - EVENTS[i_life]["t"]) / 13.8e9
    check("the even scale is proportional to time", abs(got - want) < 0.02,
          f"{got:.3f} vs {want:.3f}")
    late = even[names.index("Mammals")]
    check("on the even scale everything after the mammals is one place",
          even[-1] - late < 20, str(even[-1] - late))
    pg.click("#bBack")
    pg.wait_for_timeout(200)
    check("the log scale spreads them out",
          back[-1] - back[names.index("Mammals")] > 200,
          str(back[-1] - back[names.index("Mammals")]))

    # --- the clock is gone
    check("no scrubber", pg.evaluate("!document.getElementById('t')"))
    check("no play button", pg.evaluate("!document.getElementById('bPlay')"))
    check("and nothing on the page still runs a clock",
          "Run the clock" not in PAGE.read_text(encoding="utf-8"))

    # --- the strand chips
    chips = pg.evaluate("document.querySelectorAll('#legend [data-k]').length")
    check("a chip for each strand", chips == len(STRANDS), str(chips))
    before = pg.evaluate("window.__cosmic().dots")
    pg.click('#legend [data-k="art"]')
    pg.wait_for_timeout(200)
    after = pg.evaluate("window.__cosmic()")
    check("switching a strand off drops its marks", after["dots"] < before,
          f'{after["dots"]} vs {before}')
    check("and its row", after["rows"] == len(STRANDS) - 1, str(after["rows"]))
    pg.click('#legend [data-k="art"]')
    pg.wait_for_timeout(200)
    check("switching it back on restores them",
          pg.evaluate("window.__cosmic().dots") == before)

    # --- the cards
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
    # a detail mark reads out as a calendar year where one means anything
    pg.evaluate("showDet(DET.findIndex(d=>d.n.indexOf('Principia')>=0))")
    pg.wait_for_timeout(120)
    when = pg.evaluate("document.getElementById('whenTxt').textContent")
    check("a historical mark carries its calendar year", "1687 CE" in when,
          when)
    pg.evaluate("showDet(DET.findIndex(d=>d.n.indexOf('Hammurabi')>=0))")
    pg.wait_for_timeout(120)
    when = pg.evaluate("document.getElementById('whenTxt').textContent")
    check("and a mark before the common era says so", "1754 BCE" in when,
          when)
    pg.evaluate("showDet(0)")
    pg.wait_for_timeout(120)
    when = pg.evaluate("document.getElementById('whenTxt').textContent")
    check("a deep mark is given in years ago", "billion years ago" in when,
          when)

    # --- what the page owes the notebook
    html = PAGE.read_text(encoding="utf-8")
    for e in EVENTS:
        check(f"cites the source for {e['n']}", e["u2"] in html)
    check("the corrections to the notebook are on the page",
          all(a in html for a, _b, _c in FIXED))
    check("and are outside the description budget",
          '<div class="method">' in html)

    # --- the search, over the milestones and all the detail
    pg.evaluate("()=>{setWin(null);runFind('')}")
    for q, want, first in [("dinosaur", 1, "The earliest dinosaur fossils"),
                           ("empire", 9, None), ("zzzz", 0, None)]:
        pg.fill("#find", q)
        pg.wait_for_timeout(80)
        n = pg.evaluate("()=>hits.length")
        check(f"'{q}' turns up {n} match(es) across the milestones and the detail",
              n == want, pg.evaluate("()=>document.getElementById('findTxt').textContent"))
        if first:
            got = pg.evaluate("()=>hits.map(h=>h[0]==='ev'?EV[h[1]].n:DET[h[1]].n)")
            check("and names it", got[0] == first, str(got))
    # a word start, not any substring: war finds warfare, not toward
    pg.fill("#find", "war")
    pg.wait_for_timeout(80)
    names = pg.evaluate("()=>hits.map(h=>h[0]==='ev'?EV[h[1]].n:DET[h[1]].n)")
    check("the search matches word starts, so nothing here is a 'toward'",
          names and all(any(w.lower().startswith("war")
                            for w in re.split(r"[^A-Za-z0-9]+", n))
                        for n in names), str(names[:3]))
    # matched marks are ringed and the rest fade
    rings = pg.evaluate("""()=>[...document.querySelectorAll('#tsvg circle')]
      .filter(c=>c.getAttribute('stroke')==='#f4efe2').length""")
    check(f"every match is ringed on the line ({rings} of {len(names)})",
          rings == len(names))
    # walking the matches with the return key
    pg.evaluate("()=>{hitAt=-1;step()}")
    a = pg.evaluate("()=>document.getElementById('nameTxt').textContent")
    pg.evaluate("()=>step()")
    b = pg.evaluate("()=>document.getElementById('nameTxt').textContent")
    check("the return key walks from one match to the next",
          a != b and a in names and b in names, f"{a} then {b}")

    # --- the window: a span pulled out of the line rescales it
    pg.fill("#find", "")
    pg.evaluate("()=>setWin(null)")
    # x runs right to left with age on the three backward scales, so
    # compare the width the decade takes, not its sign
    wide = abs(pg.evaluate("()=>X(1e6)-X(1e5)"))
    pg.evaluate("()=>setWin([2e6,5e4])")
    got = pg.evaluate("()=>win")
    check("a span sets the window", got and abs(got[0] - 2e6) < 1, str(got))
    tight = abs(pg.evaluate("()=>X(1e6)-X(1e5)"))
    check(f"and the decade it holds stretches from {wide:.0f}px to {tight:.0f}px",
          tight > wide * 3)
    labs = pg.evaluate("()=>ticksNow().map(t=>t.lab)")
    check(f"the ticks are rebuilt for the span: {labs}",
          len(labs) >= 3 and all(lb.endswith("kyr") or lb.endswith("Myr")
                                 for lb in labs))
    ends = pg.evaluate("""()=>[...document.querySelectorAll('#tsvg text')]
      .slice(0,0).concat([document.getElementById('winTxt').textContent])""")
    check("and the ends of the line say where they are",
          "2.0 million years ago" in ends[0], str(ends))
    off_screen = pg.evaluate(
        "()=>EV.filter(e=>e.t>win[0]||e.t<win[1]).length")
    drawn = pg.evaluate("()=>document.querySelectorAll('#tsvg g[data-i]').length")
    check(f"the {off_screen} milestones outside the window are not drawn",
          drawn == len(EVENTS) - off_screen, f"{drawn} drawn")
    # every scale keeps its own shape inside a window
    for m in ("back", "fwd", "sun", "even"):
        pg.evaluate("(m)=>{setMode(m);setWin([1e9,1e6])}", m)
        n = len(pg.evaluate("()=>ticksNow()"))
        mono = pg.evaluate("""()=>{const t=ticksNow().map(k=>X(k.t));
          return t.every((v,i)=>!i||v>t[i-1]) || t.every((v,i)=>!i||v<t[i-1]);}""")
        check(f"the {m} scale keeps its order inside a window ({n} ticks)",
              n >= 3 and mono)
    pg.evaluate("()=>{setMode('back');setWin(null)}")
    check("and the whole line comes back", pg.evaluate("()=>win") is None)

    check("no JS errors", not errs, "; ".join(errs)[:140])
    br.close()

if fails:
    raise SystemExit(f"{len(fails)} check(s) failed")
print("all checks passed")
