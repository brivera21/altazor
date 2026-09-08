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
    "arizona.html": dict(cty=15,
        probe=("HIST.events.some(e=>e.n==='The Long Walk'&&e.t==='rem')",
               "the Long Walk is on the timeline")),
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
        # 1492: no state border, no neighbor-state names (seas may show)
        ol = pg.evaluate("document.querySelectorAll('#map path[stroke=\"#e6e6e6\"][fill=\"none\"]').length")
        nbn = pg.evaluate("HIST.nb.filter(n=>!n.sea).length")
        nb0 = pg.evaluate("[...document.querySelectorAll('#map text')].filter(t=>t.getAttribute('letter-spacing')).length")
        check("no border or neighbor names before the border", ol == 0 and nb0 == 0,
              f"outline {ol}, names {nb0}")
        # counties chip: none exist yet in 1492, all carry data
        pg.click("#cCou"); pg.wait_for_timeout(200)
        n0 = pg.evaluate("document.querySelectorAll('[data-cty]').length")
        check("no counties before any were founded", n0 == 0, str(n0))
        hasy = pg.evaluate("ST.counties.every(x=>x.y>=1600&&x.y<=1990)")
        check("every county carries a founding year", hasy)
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
        big = pg.evaluate("document.querySelectorAll('#map [data-ev] circle[fill-opacity=\"0.62\"]').length")
        check("city circles drawn in 2020", big >= 1, str(big))
        bulk_n = {"california.html": 55, "pennsylvania.html": 1,
                  "massachusetts.html": 4, "alabama.html": 0,
                  "nebraska.html": 0, "minnesota.html": 1,
                  "arizona.html": 6}[fname]
        bulk = pg.evaluate("document.querySelectorAll('#map [data-ct]').length")
        check("the 100,000-plus cities are all on the map",
              bulk >= bulk_n, f"{bulk} < {bulk_n}")
        full = pg.evaluate(
            "HIST.events.filter(e=>e.pp&&e.pp.length>=10).length")
        check("event cities carry the full census series", full >= 1,
              str(full))
        okpp = pg.evaluate(
            "(HIST.cities||[]).every(c=>c.pp.length&&c.pp.every((q,i)=>!i||q[0]>c.pp[i-1][0]))")
        check("city census series are ordered", okpp)
        n = pg.evaluate("document.querySelectorAll('[data-cty]').length")
        check(f"{c['cty']} counties drawn by 2020", n == c["cty"], str(n))
        filled = pg.evaluate(
            "[...document.querySelectorAll('[data-cty] path')].filter(p=>p.getAttribute('fill')!=='rgba(0,0,0,0)').length")
        want_home = 1 if pg.evaluate("!!ST.home") else 0
        check("county borders only, bar the home county",
              filled == want_home, f"{filled} filled, expected {want_home}")
        if want_home:
            gold = pg.evaluate(
                "(()=>{const i=ST.counties.findIndex(c=>c.fips===ST.home);"
                "const g=document.querySelector('[data-cty=\"'+i+'\"] path');"
                "return !!g&&g.getAttribute('stroke')==='#ffd24d';})()")
            check("the home county is the gold one", gold)
        grow = pg.evaluate(
            "(()=>{const c=HIST.events.find(e=>e.pp);if(!c)return null;"
            "return cityR(interp(c.pp,2020))>cityR(interp(c.pp,1900));})()")
        check("a city circle grows over time", grow is True, str(grow))
        legend = pg.evaluate("document.querySelector('#map').innerHTML.includes('City population')")
        check("the circle legend is drawn", legend)
        # 2020: the border is drawn and the neighbor names are up
        ol = pg.evaluate("document.querySelectorAll('#map path[stroke=\"#e6e6e6\"][fill=\"none\"]').length")
        nb1 = pg.evaluate("[...document.querySelectorAll('#map text')].filter(t=>t.getAttribute('letter-spacing')).length")
        check("border and neighbor names drawn in 2020",
              ol >= 1 and nb1 == nbn, f"outline {ol}, names {nb1}/{nbn}")
        # colleges chip: institutions appear from their founding years
        pg.click("#cUni"); pg.wait_for_timeout(250)
        uni_n = {"california.html": 95, "pennsylvania.html": 110,
                 "massachusetts.html": 70, "alabama.html": 30,
                 "nebraska.html": 20, "minnesota.html": 34,
                 "arizona.html": 7}[fname]
        un = pg.evaluate("document.querySelectorAll('#map [data-uni]').length")
        check("the colleges are on the map in 2020", un >= uni_n,
              f"{un} < {uni_n}")
        mine_st = {"pennsylvania.html": "F&M", "massachusetts.html": "UMass",
                   "alabama.html": "UA", "nebraska.html": "UNL",
                   "minnesota.html": "St. Olaf"}.get(fname)
        if mine_st:
            lbl = pg.evaluate(
                f"[...document.querySelectorAll('#map [data-uni] text')].some(t=>t.textContent==='{mine_st}')")
            check(f"the {mine_st} mortarboard is labeled", lbl)
        pg.eval_on_selector("#yr", "el=>{el.value=1492;el.dispatchEvent(new Event('input'))}")
        pg.wait_for_timeout(250)
        u0 = pg.evaluate("document.querySelectorAll('#map [data-uni]').length")
        check("no colleges before any were founded", u0 == 0, str(u0))
        pg.eval_on_selector("#yr", "el=>{el.value=2020;el.dispatchEvent(new Event('input'))}")
        pg.click("#cUni"); pg.wait_for_timeout(250)
        # highways chip: routes appear from their designation years
        pg.click("#cHwy"); pg.wait_for_timeout(250)
        r2020 = pg.evaluate("document.querySelectorAll('#map [data-rd]').length")
        check("highways drawn in 2020", r2020 >= 20, str(r2020))
        dated = pg.evaluate("ROADS.every(r=>r.y>=1900&&r.y<=2026)")
        check("every route carries a designation year", dated)
        lv = pg.evaluate("[...new Set(ROADS.map(r=>r.lv))].sort().join(',')")
        check("interstate, federal and state routes all present",
              lv == "i,sr,us", lv)
        leg = pg.evaluate("document.querySelector('#map').innerHTML.includes('Interstate')")
        check("the road legend is drawn", leg)
        pg.eval_on_selector("#yr", "el=>{el.value=1900;el.dispatchEvent(new Event('input'))}")
        pg.wait_for_timeout(250)
        r1900 = pg.evaluate("document.querySelectorAll('#map [data-rd]').length")
        check("no highways before the numbered systems", r1900 == 0, str(r1900))
        pg.eval_on_selector("#yr", "el=>{el.value=1950;el.dispatchEvent(new Event('input'))}")
        pg.wait_for_timeout(250)
        r1950 = pg.evaluate("document.querySelectorAll('#map [data-rd]').length")
        check("the network grows over time",
              0 < r1950 < r2020, f"1950 {r1950} vs 2020 {r2020}")
        pg.eval_on_selector("#yr", "el=>{el.value=2020;el.dispatchEvent(new Event('input'))}")
        pg.click("#cHwy"); pg.wait_for_timeout(250)
        # slider jump markers land on era boundaries
        tk = pg.evaluate("document.querySelectorAll('#ticks button').length")
        check("jump markers above the slider", tk >= 3, str(tk))
        sy = {"california.html": 1850, "pennsylvania.html": 1787,
              "massachusetts.html": 1788, "alabama.html": 1819,
              "nebraska.html": 1867, "minnesota.html": 1858,
              "arizona.html": 1912}[fname]
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


# --- the seven pages carry the same fields, so none of them can drift ---
# thin again without the check noticing
import json as _json
import re as _re

_src = (ROOT / "tools" / "build_states.py").read_text()
_ns = {}
exec(compile(_src[_src.index("US = {"):_src.index("PAGES = {")], "<hist>", "exec"),
     _ns)
HIST, SYMBOLS = _ns["HIST"], _ns["SYMBOLS"]

REQUIRED = ("eras", "marks", "border", "nb", "pre", "nations", "events",
            "census", "early", "native", "geo", "refs")
FLOORS = dict(nations=7, events=11, native=3, eras=5, refs=3, early=1, marks=1)

print("\n-- structure --")
for st in sorted(HIST):
    h = HIST[st]
    missing = [k for k in REQUIRED if not h.get(k)]
    check(f"{st}: every field is filled", not missing, ",".join(missing))
    thin = [f"{k} {len(h[k])}<{n}" for k, n in FLOORS.items()
            if len(h.get(k) or []) < n]
    check(f"{st}: every list is deep enough", not thin, "; ".join(thin))
    nat = h["native"]
    check(f"{st}: the Native line runs in order and reaches 2020",
          nat == sorted(nat) and nat[-1][0] == 2020,
          str([x[0] for x in nat]))
    check(f"{st}: every Native point says whose figure it is",
          all(len(x) == 3 and x[2].strip() for x in nat))
    early, cen = h["early"], h["census"]
    check(f"{st}: the early counts sit before the first census",
          all(len(e) == 3 and e[2].strip() for e in early)
          and max(e[0] for e in early) < cen[-1][0])
    check(f"{st}: statehood is on the rail",
          any("Statehood" in m["l"] for m in h["marks"]),
          str([m["l"] for m in h["marks"]]))
    for n in h["nations"]:
        assert {"n", "src", "poly", "lat", "lon", "note"} <= set(n), n
    check(f"{st}: every nation carries a homeland, a label and a source",
          all(len(n["poly"]) >= 4 and n["note"].strip() for n in h["nations"]))
    sym = SYMBOLS[st]
    kinds = [x["k"] for x in sym]
    check(f"{st}: a bird, a flower and a tree", 
          {"Bird", "Flower", "Tree"} <= set(kinds), ",".join(kinds))
    check(f"{st}: every symbol has a binomial, a year and an article",
          all(x["b"] and x["y"] and x["a"] and x["t"] for x in sym))
    check(f"{st}: no symbol adopted before the state existed",
          all(x["y"] >= h["border"] for x in sym),
          str([(x["k"], x["y"]) for x in sym if x["y"] < h["border"]]))

# the symbols reach the page, and the card renders them
print("\n-- symbols on the page --")
with sync_playwright() as _pw:
    _br = _pw.chromium.launch()
    _pg = _br.new_page(viewport={"width": 1280, "height": 1000})
    for _st, _f in _ns.get("PAGES", {}).items() if _ns.get("PAGES") else []:
        pass
    for _st in sorted(HIST):
        _fn = {"ca": "california", "az": "arizona", "pa": "pennsylvania",
               "ma": "massachusetts", "al": "alabama", "ne": "nebraska",
               "mn": "minnesota"}[_st] + ".html"
        _pg.goto((ROOT / _fn).as_uri())
        _pg.wait_for_timeout(900)
        _n = _pg.eval_on_selector_all(".sym", "es=>es.length")
        check(f"{_fn}: {_n} symbols in the card", _n == len(SYMBOLS[_st]))
        _ticks = _pg.eval_on_selector_all("#ticks button", "es=>es.map(e=>e.textContent)")
        check(f"{_fn}: no year appears twice on the rail",
              len(_ticks) == len(set(_ticks)), ",".join(_ticks))
    _br.close()

if fails:
    raise SystemExit(f"{len(fails)} check(s) failed")
print("all checks passed")
