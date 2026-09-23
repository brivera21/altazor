#!/usr/bin/env python3
"""Checks expanse-timeline.html.

  the data      17 milestones in order, every source a known type, every era
                used, and each correction to the brief in place with the old
                wording gone
  the numbers   the gap bar's intervals and the transfer diagram's day counts
                are computed here and matched against what the page prints
  the page      every milestone opens with its year, label and badge; each
                source filter removes exactly its own markers; the keyboard
                works; the transfer diagram moves, and holds still when the
                reader asks for reduced motion
  the phone     at 390 pixels the same eras and badges as a vertical list,
                nothing wider than the screen
  the copy      no em dashes, nothing loaded from outside, American spelling
"""

import math
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from expanse_timeline_data import (SOURCES, ERAS, MILESTONES, GAPS, CLOSING,  # noqa: E402
                                   INTRO, CORRECTIONS)

PAGE = ROOT / "expanse-timeline.html"
FAILS = []


def check(ok, what):
    print(("  ok   " if ok else "  FAIL ") + what)
    if not ok:
        FAILS.append(what)


def alltext():
    out = [CLOSING, *INTRO]
    for e in ERAS:
        out += e["text"] + [e["title"]]
    for m in MILESTONES:
        out += [m["label"], m["note"]]
        for b in m["body"]:
            if isinstance(b, str):
                out.append(b)
            elif "ol" in b:
                out += b["ol"]
            else:
                out += [t + " " + d for t, d in b["dl"]]
    return "\n".join(out)


print("--- the data ---")
names = [s for s, _ in SOURCES]
check(len(MILESTONES) == 17, f"17 milestones ({len(MILESTONES)})")
check([m["sort"] for m in MILESTONES] == sorted(m["sort"] for m in MILESTONES), "in date order")
check(all(m["source"] in names for m in MILESTONES), "every source is one of the six types")
keys = [e["key"] for e in ERAS]
check(all(m["era"] in keys for m in MILESTONES), "every milestone belongs to a known era")
check(all(any(m["era"] == k for m in MILESTONES) for k in keys), "every era holds a milestone")
check(all(m["body"] for m in MILESTONES), "every milestone has its longer text")
T = alltext()
for gone, why in [("telemetry", "Epstein's design: no telemetry"),
                  ("launched at Earth", "hybrids: not at Earth"),
                  ("vintage", "gin: not a vintage"),
                  ("have surrendered", "Anderson Station: tried to surrender"),
                  ("Both dates have since", "only 2025 has passed"),
                  ("Treat the", "the intro gives no orders"),
                  ("stops instantly", "the Y Que: slowed, not stopped")]:
    check(gone not in T, f"old wording gone ({why})")
for here, why in [("launched at Mars", "hybrids at Mars"),
                  ("home computer", "the plans on his home computer"),
                  ("since 2307", "the gin label"),
                  ("only certain date", "the wiki's one exception")]:
    check(here in T, f"correction in place ({why})")
gin = next(m for m in MILESTONES if m["sort"] == 2307)
check(gin["source"] == "Show", "2307 rests on the show, not the novels")
check(len(CORRECTIONS) >= 10, f"every departure from the brief is listed ({len(CORRECTIONS)})")

print("--- the numbers ---")
g = [b - a for a, b, _ in GAPS]
check(g == [163, 137, 3], f"intervals {g}: 2050 to 2213, 2213 to 2350, 2350 to 2353")
check(not CLOSING, "no closing paragraph: the gap bar carries it")
W = lambda x: len(x.split())
bw = lambda b: sum(W(x) if isinstance(x, str) else sum(W(t) + W(d) for t, d in x["dl"]) for x in b)
check(max(bw(m["body"]) for m in MILESTONES) <= 60, "every milestone is a caption, 60 words or fewer")
check(len(INTRO) == 1 and W(INTRO[0]) <= 60, f"one caption under the diagram ({W(INTRO[0])} words)")
AU, DAY, GM = 1.495978707e11, 86400.0, 1.32712440018e20
hoh = math.pi * math.sqrt(((1 + 1.524) / 2 * AU) ** 3 / GM) / DAY
brach = 2 * math.sqrt(0.5 * AU / (9.80665 / 3)) / DAY
check(abs(hoh - 259) < 1, f"Hohmann, Earth to Mars: {hoh:.1f} days")
check(abs(brach - 3.5) < 0.05, f"brachistochrone, half an AU at a third of a g: {brach:.2f} days")
html = PAGE.read_text(encoding="utf-8")
check('"hohmann_days": 259' in html and '"brach_days": 3.5' in html, "the page carries both numbers")

print("--- the page ---")
from playwright.sync_api import sync_playwright  # noqa: E402
with sync_playwright() as p:
    br = p.chromium.launch()
    pg = br.new_page(viewport={"width": 1320, "height": 1100})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#diagram .hit")
    s = pg.evaluate("() => window.__exp()")
    check(s["markers"] == 17 and s["year"].startswith("c. 2200"),
          "all 17 markers drawn; opens on the Epstein Drive")
    for i, m in enumerate(MILESTONES):
        s = pg.evaluate("i => window.__exp({pick:i})", i)
        plain = m["label"].replace("*", "")
        check(s["year"] == m["year"] and s["label"] == plain and s["badge"] == m["source"]
              and len(s["body"]) > 20, f"{m['year']}: year, label, {m['source']} badge, text")
    s = pg.evaluate("() => window.__exp({pick:9})")
    check(s["powers"] == 3, "the three-body era shows Earth, Mars and the Belt")
    s = pg.evaluate("() => window.__exp({pick:4})")
    check(s["xfer"] == 2, "the Epstein era shows both transfers")
    a = pg.evaluate("() => document.querySelector('svg.xf[data-k=b] .ship').getAttribute('transform')")
    pg.wait_for_timeout(400)
    b = pg.evaluate("() => document.querySelector('svg.xf[data-k=b] .ship').getAttribute('transform')")
    check(a != b, "the transfer diagram moves")
    for src in names:
        n = sum(m["source"] == src for m in MILESTONES)
        s = pg.evaluate("s => window.__exp({toggle:s})", src)
        check(s["markers"] == 17 - n and src not in s["pressed"], f"filtering out {src} removes its {n}")
        pg.evaluate("s => window.__exp({toggle:s})", src)
    s = pg.evaluate("() => window.__exp({only:['Novels']})")
    check(s["markers"] == sum(m["source"] == "Novels" for m in MILESTONES) and s["badge"] == "Novels",
          "novels only: the card moves to a visible milestone")
    pg.evaluate("() => window.__exp({all:true})")
    pg.focus('#diagram .hit[data-i="0"]')
    pg.keyboard.press("Enter")
    check(pg.evaluate("() => window.__exp()")["sel"] == 0, "Enter on a focused marker opens it")
    bar = pg.evaluate("() => document.querySelector('#gapbar').textContent")
    check("about 160 years" in bar and "about 140 years" in bar and "four years" in bar,
          "the gap bar labels the computed intervals")
    check(pg.evaluate("() => { const d = document.querySelector('details.sources'); "
                      "return !!d && !d.open && !!d.querySelector('.refs') && !!d.querySelector('.method'); }"),
          "sources and method sit behind a closed Sources line")
    check(not errs, "no script errors" + (f" ({errs[0]})" if errs else ""))
    pg.close()

    rm = br.new_context(reduced_motion="reduce", viewport={"width": 1320, "height": 1100}).new_page()
    rm.goto(PAGE.as_uri())
    rm.wait_for_selector("svg.xf")
    a = rm.evaluate("() => document.querySelector('svg.xf[data-k=b] .ship').getAttribute('transform')")
    rm.wait_for_timeout(400)
    b = rm.evaluate("() => document.querySelector('svg.xf[data-k=b] .ship').getAttribute('transform')")
    check(a == b and a, "reduced motion: the diagram holds still")
    rm.close()

    print("--- the phone ---")
    ph = br.new_page(viewport={"width": 390, "height": 900})
    ph.goto(PAGE.as_uri())
    ph.wait_for_selector("#vlist .vitem")
    s = ph.evaluate("() => window.__exp()")
    check(s["veras"] == 8 and s["vitems"] == 17, "eight eras, seventeen milestones, as a list")
    check(ph.evaluate("() => getComputedStyle(document.querySelector('.stage')).display") == "none",
          "the horizontal timeline gives way to the list")
    ph.click('#vlist button[data-v="7"]')
    check(ph.evaluate("() => document.querySelector('#vlist .vbody .badge')?.textContent") == "Show",
          "tapping 2307 opens it with its badge")
    check(ph.evaluate("() => document.documentElement.scrollWidth - innerWidth") <= 0,
          "nothing wider than the screen")
    ph.close()
    br.close()

print("--- the copy ---")
check("—" not in html, "no em dashes")
check(not re.search(r'<(script|link|img)[^>]+(src|href)="https?:', html), "nothing loaded from outside")
am = subprocess.run([sys.executable, str(ROOT / "tools" / "americanize.py"), "--check", PAGE.name],
                    capture_output=True, text=True, cwd=ROOT).stdout
check("0 files would change" in am, "americanize.py finds nothing to change")
sec = (ROOT / "science-fiction.html").read_text(encoding="utf-8")
check('href="expanse-timeline.html">The Expanse: A Timeline by Milestone Year<' in sec,
      "listed in the Science Fiction section")

print()
print("everything squares" if not FAILS else f"{len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
