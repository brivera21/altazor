#!/usr/bin/env python3
"""Verify solar-system-2312.html against what the page actually draws.

Checks the rendered DOM offline: body and marker counts, the log radial
scale on Mercury and Pluto, the journey toggle, card contents for three
places, muted worlds carrying no novel marker, citations, no JS errors.

Usage: python3 verify_2312.py
"""
import math
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(__file__).parent.parent / "solar-system-2312.html"
fails = []

def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""))
    if not ok: fails.append(name)

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1300, "height": 950})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("**/*", lambda r: r.abort()
             if r.request.url.startswith("http") else r.continue_())
    pg.goto(PAGE.as_uri())
    pg.wait_for_timeout(400)

    st = pg.evaluate("window.__ss2312()")
    check("11 bodies drawn", st["bodies"] == 11, str(st["bodies"]))
    check("9 novel places", st["novel"] == 9, str(st["novel"]))

    # log radial scale endpoints
    rm = pg.evaluate("at['Mercury'].r")
    rp = pg.evaluate("at['Pluto'].r")
    check("Mercury at the inner end of the scale", abs(rm - 62) < 0.2, str(rm))
    check("Pluto at the outer end of the scale", abs(rp - 358) < 0.2, str(rp))
    re_ = pg.evaluate("at['Earth'].r")
    want = 62 + (math.log10(1.0) - math.log10(0.387)) / (
        math.log10(39.5) - math.log10(0.387)) * (358 - 62)
    check("Earth's radius follows the log scale", abs(re_ - want) < 0.6,
          f"{re_} vs {want:.1f}")

    d = pg.evaluate("document.querySelectorAll('#ssvg rect[transform]').length")
    check("9 amber diamonds, none on the quiet worlds", d == 9, str(d))

    pg.evaluate("show('Pluto')")
    card = pg.evaluate("document.querySelector('.card').textContent")
    check("Pluto card pairs Nix the starship with Nix the moon",
          "Nix" in card and "New Horizons" in card)
    pg.evaluate("show('Mercury')")
    card = pg.evaluate("document.querySelector('.card').textContent")
    check("Terminator card carries the terminator speed", "3.6 km/h" in card)
    pg.evaluate("show('Uranus')")
    card = pg.evaluate("document.querySelector('.card').textContent")
    check("a quiet world says the novel passes it by", "passes this world by" in card)

    pg.click("#bJourney")
    pg.wait_for_timeout(200)
    st = pg.evaluate("window.__ss2312()")
    n = pg.evaluate("document.querySelectorAll('#ssvg path[stroke-dasharray=\"7 5\"]').length")
    nums = pg.evaluate("[...document.querySelectorAll('#ssvg text')].filter(t=>/^[1-8]$/.test(t.textContent)).length")
    check("journey toggle draws the route", st["journey"] and n == 1, f"paths={n}")
    check("8 numbered legs", nums == 8, str(nums))

    html = PAGE.read_text(encoding="utf-8")
    for frag in ["kimstanleyrobinson.info/content/2312",
                 "ssd.jpl.nasa.gov", "10.3389/fspas.2021.645363",
                 "10.1073/pnas.0608163103"]:
        check(f"cites {frag}", frag in html)

    check("no JS errors", not errs, "; ".join(errs))
    br.close()

if fails:
    raise SystemExit(f"{len(fails)} check(s) failed")
print("all checks passed")
