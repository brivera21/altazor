#!/usr/bin/env python3
"""Verify the seven city pages against what they actually draw.

Offline (network cut): the base map renders with no errors, the layer
chips toggle their layers, the timeline moves era, population, events,
colleges and highways, the city's own circle grows with its census, and
the home county is the gold one. Terrain, land cover and flags are
view-time fetches, checked live after publishing instead.

Usage: python3 verify_cities.py
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent.parent
fails = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name
          + (f"  [{detail}]" if detail and not ok else ""))
    if not ok:
        fails.append(name)


CASES = {
    "los-angeles.html": dict(
        up="california.html", home="06037", mine=None, mark=1781, roads=20,
        probe=("HIST.events.some(e=>e.n==='The Chinese massacre'&&e.y===1871)",
               "the 1871 massacre is on the timeline")),
    "lancaster.html": dict(
        up="pennsylvania.html", home="42071", mine="F&M", mark=1730, roads=4,
        probe=("HIST.events.some(e=>e.n.includes('Conestoga'))",
               "the Conestoga killings are on the timeline")),
    "amherst.html": dict(
        up="massachusetts.html", home="25015", mine="UMass", mark=1759, roads=4,
        probe=("HIST.nations.some(n=>n.n.includes('Norwottuck'))",
               "the Norwottuck are on the map")),
    "tuscaloosa.html": dict(
        up="alabama.html", home="01125", mine="UA", mark=1819, roads=3,
        probe=("HIST.events.some(e=>e.t==='rem')",
               "the removal era is marked")),
    "omaha.html": dict(
        up="nebraska.html", home="31055", mine=None, mark=1854, roads=4,
        probe=("HIST.nations.some(n=>n.n.includes('Umo'))",
               "the Umonhon are on the map")),
    "northfield.html": dict(
        up="minnesota.html", home="27131", mine="St. Olaf", mark=1855, roads=2,
        probe=("HIST.events.some(e=>e.n.includes('raid')&&e.y===1876)",
               "the 1876 raid is on the timeline")),
    "new-york.html": dict(
        up="us-cities.html", home="36061", mine=None, mark=1624, roads=20,
        probe=("HIST.events.some(e=>e.n==='New Amsterdam'&&e.y===1624)",
               "New Amsterdam is on the timeline")),
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
        none = pg.evaluate("!document.getElementById('flagNone').hidden")
        check("1492 shows the peoples' ground, no flag", none)
        nat = pg.evaluate("document.querySelectorAll('[data-nat]').length")
        check("the peoples of this ground are drawn", nat >= 2, str(nat))
        # counties chip
        pg.click("#cCou")
        pg.wait_for_timeout(200)
        n0 = pg.evaluate("document.querySelectorAll('[data-cty]').length")
        check("no counties before any were founded", n0 == 0, str(n0))
        # the timeline at 2020
        pg.eval_on_selector("#yr", "el=>{el.value=2020;"
                            "el.dispatchEvent(new Event('input'))}")
        pg.wait_for_timeout(300)
        st = pg.evaluate("window.__state()")
        check("events appear by 2020", st["visEvents"] > 4,
              str(st["visEvents"]))
        pop = pg.evaluate("document.getElementById('popTxt').textContent")
        check("the census total is shown", "Census" in pop, pop[:60])
        expr, name = c["probe"]
        check(name, pg.evaluate(expr))
        n = pg.evaluate("document.querySelectorAll('[data-cty]').length")
        check("the counties of the view box are drawn",
              n == len(pg.evaluate("ST.counties")), str(n))
        filled = pg.evaluate(
            "[...document.querySelectorAll('[data-cty] path')]"
            ".filter(p=>p.getAttribute('fill')!=='rgba(0,0,0,0)').length")
        check("county borders only, bar the home county", filled == 1,
              f"{filled} filled")
        gold = pg.evaluate(
            "(()=>{const i=ST.counties.findIndex(c=>c.fips===ST.home);"
            "const g=document.querySelector('[data-cty=\"'+i+'\"] path');"
            "return !!g&&g.getAttribute('stroke')==='#ffd24d';})()")
        check(f"the home county {c['home']} is the gold one",
              gold and pg.evaluate("ST.home") == c["home"])
        # the city's own circle carries its census
        okpp = pg.evaluate(
            "(()=>{const e=HIST.events.find(x=>x.pp);if(!e)return null;"
            "return e.pp.every((q,i)=>!i||q[0]>e.pp[i-1][0]);})()")
        check("the city carries an ordered census series", okpp is True)
        grow = pg.evaluate(
            "(()=>{const e=HIST.events.find(x=>x.pp);if(!e)return null;"
            "return cityR(interp(e.pp,2020))>=cityR(interp(e.pp,1900));})()")
        check("the city's circle grows over time", grow is True, str(grow))
        circ = pg.evaluate(
            "document.querySelectorAll('#map [data-ev] "
            "circle[fill-opacity=\"0.62\"]').length")
        check("the city's circle is drawn in 2020", circ >= 1, str(circ))
        # migration arrows
        mig = pg.evaluate("document.querySelectorAll('#map [data-mig]').length")
        check("the migration waves are drawn", mig >= 2, str(mig))
        okmig = pg.evaluate(
            "(HIST.mig||[]).every(m=>m.y0<m.y1&&m.p>0&&m.note&&m.src)")
        check("every wave carries a span, a size, a note and a source", okmig)
        # colleges
        pg.click("#cUni")
        pg.wait_for_timeout(250)
        un = pg.evaluate("document.querySelectorAll('#map [data-uni]').length")
        check("the colleges are on the map in 2020", un >= 2, str(un))
        if c["mine"]:
            lbl = pg.evaluate(
                "[...document.querySelectorAll('#map [data-uni] text')]"
                f".some(t=>t.textContent==={c['mine']!r})".replace("'", '"'))
            check(f"the {c['mine']} mortarboard is labeled", lbl)
        pg.eval_on_selector("#yr", "el=>{el.value=1492;"
                            "el.dispatchEvent(new Event('input'))}")
        pg.wait_for_timeout(250)
        u0 = pg.evaluate("document.querySelectorAll('#map [data-uni]').length")
        check("no colleges before any were founded", u0 == 0, str(u0))
        pg.eval_on_selector("#yr", "el=>{el.value=2020;"
                            "el.dispatchEvent(new Event('input'))}")
        pg.click("#cUni")
        pg.wait_for_timeout(200)
        # highways
        pg.click("#cHwy")
        pg.wait_for_timeout(250)
        r2020 = pg.evaluate("document.querySelectorAll('#map [data-rd]').length")
        check("highways drawn in 2020", r2020 >= c["roads"],
              f"{r2020} < {c['roads']}")
        dated = pg.evaluate("ROADS.every(r=>r.y>=1900&&r.y<=2026)")
        check("every route carries a designation year", dated)
        pg.eval_on_selector("#yr", "el=>{el.value=1900;"
                            "el.dispatchEvent(new Event('input'))}")
        pg.wait_for_timeout(250)
        r1900 = pg.evaluate("document.querySelectorAll('#map [data-rd]').length")
        check("no highways before the numbered systems", r1900 == 0, str(r1900))
        pg.eval_on_selector("#yr", "el=>{el.value=2020;"
                            "el.dispatchEvent(new Event('input'))}")
        pg.click("#cHwy")
        pg.wait_for_timeout(200)
        # jump markers
        tk = pg.evaluate("document.querySelectorAll('#ticks button').length")
        check("jump markers above the slider", tk >= 3, str(tk))
        has = pg.evaluate("[...document.querySelectorAll('#ticks button')]"
                          f".some(b=>b.textContent==='{c['mark']}')")
        check(f"{c['mark']} is a jump marker", has)
        pg.evaluate("document.querySelector('#ticks button').click()")
        pg.wait_for_timeout(200)
        jumped = pg.evaluate("window.__state()")["year"]
        first = pg.evaluate(
            "HIST.eras.map(e=>e.y0).filter(y=>y>1492).sort((a,b)=>a-b)[0]")
        check("clicking a marker jumps to its year", jumped == first,
              f"{jumped} vs {first}")
        # the page points back to its state
        up = pg.evaluate(
            f"[...document.querySelectorAll('nav.site a')]"
            f".some(a=>a.getAttribute('href')==='{c['up']}')")
        check("the page links back to its state", up)
        check("no JS errors", not errs, "; ".join(errs)[:120])
        pg.close()
    br.close()

if fails:
    raise SystemExit(f"{len(fails)} check(s) failed")
print("all checks passed")
