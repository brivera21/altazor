#!/usr/bin/env python3
"""Verify solar-system-2312.html against what the page actually draws.

Checks the rendered DOM offline: the worlds sit on one line in order of
distance on a logarithmic axis, the ten stops of Swan's journey draw as
arcs in sequence, stepping moves through them, every world she lands on
carries a diagram with a scale bar, the cards pair the book with what is
there, the quiet worlds carry no marker, citations, no JS errors.

Usage: python3 verify_2312.py
"""
import math
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(__file__).parent.parent / "solar-system-2312.html"
fails = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name
          + (f"  [{detail}]" if detail and not ok else ""))
    if not ok:
        fails.append(name)


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

    # one line, ordered by distance, on a log axis
    ys = pg.evaluate("[...document.querySelectorAll('#ssvg [data-n] circle')]"
                     ".map(c=>+c.getAttribute('cy'))")
    check("every world sits on the same line", len(set(ys)) == 1, str(set(ys)))
    ordered = pg.evaluate(
        "BODIES.every((b,i)=>!i||(b.a>BODIES[i-1].a)===(b.x>BODIES[i-1].x))")
    check("the line runs outward in order of distance", ordered)
    xm, xe, xp = pg.evaluate("[at['Mercury'].x,at['Earth'].x,at['Pluto'].x]")
    want = xm + (math.log10(1.0) - math.log10(0.387)) / (
        math.log10(39.5) - math.log10(0.387)) * (xp - xm)
    check("Earth's place on the axis follows the log scale",
          abs(xe - want) < 0.6, f"{xe} vs {want:.1f}")

    d = pg.evaluate("document.querySelectorAll('#ssvg [data-n] rect[transform]')"
                    ".length")
    check("9 amber diamonds, none on the quiet worlds", d == 9, str(d))

    # the journey: ten stops as arcs, in sequence
    check("ten stops", st["legs"] == 10, str(st["legs"]))
    check("the jumps are drawn from the start", st["jumps"])
    arcs = pg.evaluate("document.querySelectorAll('#ssvg [data-leg]').length")
    check("a mark for every stop", arcs == 10, str(arcs))
    seq = pg.evaluate("JOURNEY.map(j=>j.n).join(',')")
    check("the order follows the synopsis",
          seq == "Mercury,Jupiter,Earth,Venus,Mercury,Vesta,Saturn,Earth,"
                 "Venus,Mars", seq)
    notes = pg.evaluate("JOURNEY.every(j=>j.w&&j.t&&j.t.length>40)")
    check("every stop says where on the world and what for", notes)

    pg.click("#bNext")
    pg.wait_for_timeout(150)
    st = pg.evaluate("window.__ss2312()")
    check("stepping moves to the next stop",
          st["leg"] == 1 and st["cur"] == "Jupiter", str(st))
    pg.click("#bPrev")
    pg.wait_for_timeout(150)
    check("and back to the one before",
          pg.evaluate("window.__ss2312().leg") == 0)

    # a diagram for every world she lands on
    visited = pg.evaluate("[...new Set(JOURNEY.map(j=>j.n))]")
    have = pg.evaluate("Object.keys(DIA)")
    check("a diagram for every world Swan lands on",
          sorted(visited) == sorted(have), f"{sorted(visited)} vs {sorted(have)}")
    for i in range(10):
        pg.evaluate(f"showLeg({i})")
        pg.wait_for_timeout(60)
        ok = pg.evaluate("!!document.querySelector('#dia svg')")
        bar = pg.evaluate(
            "[...document.querySelectorAll('#dia text')]"
            ".some(t=>/ km$/.test(t.textContent))")
        amber = pg.evaluate(
            "[...document.querySelectorAll('#dia *')]"
            ".some(e=>(e.getAttribute('stroke')||e.getAttribute('fill'))==='#ffb02e')")
        n = pg.evaluate("window.__ss2312().cur")
        check(f"stop {i + 1} ({n}) draws its world, to scale, with the novel "
              f"on it", ok and bar and amber, f"svg={ok} bar={bar} amber={amber}")

    # cards
    pg.evaluate("showBody('Pluto')")
    card = pg.evaluate("document.querySelector('.card').textContent")
    check("Pluto card pairs Nix the starship with Nix the moon",
          "Nix" in card and "New Horizons" in card)
    pg.evaluate("showBody('Uranus')")
    card = pg.evaluate("document.querySelector('.card').textContent")
    check("a quiet world says the novel passes it by",
          "passes this world by" in card)
    pg.evaluate("showLeg(4)")
    card = pg.evaluate("document.querySelector('.card').textContent")
    check("the Mercury return carries the forty-five day walk",
          "forty-five days" in card)

    html = PAGE.read_text(encoding="utf-8")
    for frag in ["kimstanleyrobinson.info/content/2312",
                 "ssd.jpl.nasa.gov", "science.nasa.gov/saturn/moons/iapetus",
                 "10.3389/fspas.2021.645363", "10.1073/pnas.0608163103"]:
        check(f"cites {frag}", frag in html)

    check("no JS errors", not errs, "; ".join(errs))
    br.close()

if fails:
    raise SystemExit(f"{len(fails)} check(s) failed")
print("all checks passed")
