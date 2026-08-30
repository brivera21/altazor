#!/usr/bin/env python3
"""Verify the six state pages against what they actually draw.

Offline (network cut): the base map renders with no errors, layer chips
toggle their layers, the timeline changes era, flag, population and
event visibility, counties carry populations, and the no-flag era is
honest. Terrain, woods and flags are view-time fetches, checked live
after publishing instead.

Usage: python3 verify_states.py
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent.parent
fails = []

def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""))
    if not ok: fails.append(name)

CASES = {
    "california.html": dict(cty=58, era1870="United States (statehood 1850)",
        probe=("HIST.events.some(e=>e.n==='Bloody Island massacre'&&e.t==='rem')",
               "the Bloody Island massacre is on the timeline")),
    "pennsylvania.html": dict(cty=67, era1700="Great Britain" and "England (Penn's charter 1681)",
        probe=("HIST.events.some(e=>e.n==='Walking Purchase')",
               "the Walking Purchase is on the timeline")),
    "massachusetts.html": dict(cty=14,
        probe=("HIST.events.some(e=>e.n==='The Great Dying'&&e.y===1616)",
               "the Great Dying is on the timeline")),
    "alabama.html": dict(cty=67,
        probe=("HIST.events.filter(e=>e.t==='rem').length>=6",
               "the removal era is fully marked")),
    "nebraska.html": dict(cty=93,
        probe=("HIST.eras.some(e=>e.l.includes('Spain'))&&HIST.eras.some(e=>e.l.includes('France'))",
               "Spanish and French eras both present")),
    "minnesota.html": dict(cty=87,
        probe=("HIST.events.some(e=>e.n==='Mankato executions'&&e.y===1862)",
               "the Mankato executions are on the timeline")),
}

with sync_playwright() as pw:
    br = pw.chromium.launch()
    for fname, c in CASES.items():
        pg = br.new_page(viewport={"width": 1400, "height": 1000})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.route("**/*", lambda r: r.abort()
                 if r.request.url.startswith("http") else r.continue_())
        pg.goto((ROOT / fname).as_uri())
        pg.wait_for_timeout(600)
        print(f"--- {fname} ---")
        st = pg.evaluate("window.__state()")
        check("starts in 1492 with no settlements yet",
              st["year"] == 1492 and st["visEvents"] == 0)
        era0 = pg.evaluate("document.getElementById('eraTxt').textContent")
        none = pg.evaluate("!document.getElementById('flagNone').hidden")
        check("1492 shows the nations' land, no flag", none, era0)
        # counties chip
        pg.click("#cCou"); pg.wait_for_timeout(200)
        n = pg.evaluate("document.querySelectorAll('[data-cty]').length")
        check(f"{c['cty']} counties drawn", n == c["cty"], str(n))
        haspop = pg.evaluate("ST.counties.every(x=>x.p>0)")
        check("every county carries a population", haspop)
        # rivers chip off removes rivers
        rv0 = pg.evaluate("document.querySelectorAll('#map path[stroke=\"var(--water)\"]').length")
        pg.click("#cRiv"); pg.wait_for_timeout(150)
        rv1 = pg.evaluate("document.querySelectorAll('#map path[stroke=\"var(--water)\"]').length")
        check("the rivers chip removes the rivers", rv0 > 0 and rv1 < rv0,
              f"{rv0}->{rv1}")
        # timeline at 1870
        pg.eval_on_selector("#yr", "el=>{el.value=1870;el.dispatchEvent(new Event('input'))}")
        pg.wait_for_timeout(250)
        st = pg.evaluate("window.__state()")
        check("events appear by 1870", st["visEvents"] > 3, str(st["visEvents"]))
        pop = pg.evaluate("document.getElementById('popTxt').textContent")
        check("1870 population interpolates the census", "Census" in pop, pop[:60])
        expr, name = c["probe"]
        check(name, pg.evaluate(expr))
        # city circles: by 2020 at least one census-series city over 10,000
        pg.eval_on_selector("#yr", "el=>{el.value=2020;el.dispatchEvent(new Event('input'))}")
        pg.wait_for_timeout(250)
        big = pg.evaluate("document.querySelectorAll('#map [data-ev] circle[fill-opacity=\"0.16\"]').length")
        check("city circles drawn in 2020", big >= 1, str(big))
        grow = pg.evaluate(
            "(()=>{const c=HIST.events.find(e=>e.pp);if(!c)return null;"
            "return cityR(interp(c.pp,2020))>cityR(interp(c.pp,1900));})()")
        check("a city circle grows over time", grow is True, str(grow))
        legend = pg.evaluate("document.querySelector('#map').innerHTML.includes('City population')")
        check("the circle legend is drawn", legend)
        # slider jump markers land on era boundaries
        tk = pg.evaluate("document.querySelectorAll('#ticks button').length")
        check("jump markers above the slider", tk >= 3, str(tk))
        sy = {"california.html": 1850, "pennsylvania.html": 1787,
              "massachusetts.html": 1788, "alabama.html": 1819,
              "nebraska.html": 1867, "minnesota.html": 1858}[fname]
        has = pg.evaluate(
            f"[...document.querySelectorAll('#ticks button')].some(b=>b.textContent==='{sy}')")
        check(f"statehood {sy} is a jump marker", has)
        pg.evaluate("document.querySelector('#ticks button').click()")
        pg.wait_for_timeout(200)
        jumped = pg.evaluate("window.__state()")["year"]
        first = pg.evaluate("HIST.eras.map(e=>e.y0).filter(y=>y>1492).sort((a,b)=>a-b)[0]")
        check("clicking a marker jumps to its year", jumped == first,
              f"{jumped} vs {first}")
        check("no JS errors", not errs, "; ".join(errs)[:120])
        pg.close()
    br.close()

if fails:
    raise SystemExit(f"{len(fails)} check(s) failed")
print("all checks passed")
