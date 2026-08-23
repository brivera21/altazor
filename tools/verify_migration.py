"""Check migration.html against the data it is drawn from.

sapiens_data.py validates itself first: the dates run in order, every point
date sits inside its own published range, no region is peopled before the
oldest African fossil, the eighteen must-be-older-than pairs hold, and the
continental figures reconcile with the world series. That runs here before
anything is asked of the page.

Then the page. The clock is driven to a set of dates and asked what it shows:
how many sites are up, what the world population reads, whether the continental
split is drawn at all. Each site has to appear at its own date and not before,
which is checked one site at a time. The one entry the data marks refuted has
to be absent altogether.

Usage: pip install playwright && python3 verify_migration.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sapiens_data as S
from build_migration import CONT_FROM, CONTINENTS

PAGE = Path(__file__).parent.parent / "migration.html"
fails = []

print("--- the data checks itself ---")
try:
    S.validate()
    print("  ok   sapiens_data.py passes its own consistency checks")
except AssertionError as e:
    print(f"  FAIL {e}")
    fails.append(f"the data does not validate: {e}")

html = PAGE.read_text(encoding="utf-8")
print("--- the page itself ---")
for want in ("Homo Sapiens Migration", "library.html", "ALTAZOR", "References",
             "Jebel Irhoud", "logarithmic"):
    ok = want in html
    print(f"  {'ok  ' if ok else 'FAIL'} the page carries {want!r}")
    if not ok:
        fails.append(f"the page is missing {want!r}")
if "—" in re.sub(r"<script[\s\S]*?</script>", "", html):
    fails.append("an em dash in the page copy")

refuted = [a for a in S.ARRIVALS if a[5] == "refuted"]
for a in refuted:
    ok = a[4] not in html
    print(f"  {'ok  ' if ok else 'FAIL'} {a[4]}, which the data marks refuted, "
          "is not on the page")
    if not ok:
        fails.append(f"the refuted site {a[4]} is on the page")

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("\nplaywright not installed")
    sys.exit(1)

live = sorted((a for a in S.ARRIVALS if a[5] != "refuted"), key=lambda a: -a[3])

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1440, "height": 1100})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.resolve().as_uri())
    pg.wait_for_function("() => !!window.__mig", timeout=15000)
    st = pg.evaluate("()=>window.__mig()")
    print("--- what the page carries ---")
    ok = st["sites"] == len(live) and st["links"] == len(live) - 1
    print(f"  {'ok  ' if ok else 'FAIL'} {st['sites']} sites and {st['links']} "
          f"links, for {len(live)} sites the data does not refute")
    if not ok:
        fails.append(f"the page carries {st['sites']} sites, {st['links']} links")

    print("--- the clock reaches both ends ---")
    a = pg.evaluate("()=>window.__setP(0)")
    b = pg.evaluate("()=>window.__setP(1)")
    ok = a >= 299000 and b <= 0
    print(f"  {'ok  ' if ok else 'FAIL'} it runs {a:,.0f} years ago to "
          f"{'the present' if b <= 0 else f'{b:,.0f} years ago'}")
    if not ok:
        fails.append(f"the clock runs {a} to {b}")

    print("--- every site appears at its own date ---")
    bad = 0
    for name, la, lo, t, site, conf, note in live:
        pg.evaluate("(t)=>window.__setYbp(t)", t + max(1, t * 0.02))
        before = pg.evaluate("()=>window.__mig().here")
        pg.evaluate("(t)=>window.__setYbp(t)", max(-76, t - max(1, t * 0.02)))
        after = pg.evaluate("()=>window.__mig().here")
        if after <= before:
            bad += 1
            fails.append(f"{site} does not appear when the clock passes {t}")
    print(f"  {'ok  ' if not bad else 'FAIL'} all {len(live)} sites come up as "
          "the clock passes their date, and none before")

    print("--- the population against the series ---")
    worst = (0.0, 0)
    for t, pop, _ in S.POPULATION_CENSUS:
        pg.evaluate("(t)=>window.__setYbp(t)", t)
        got = pg.evaluate("()=>window.__mig().world")
        e = abs(got - pop) / pop * 100
        if e > worst[0]:
            worst = (e, t)
    print(f"  {'ok  ' if worst[0] < 0.5 else 'FAIL'} the page matches all "
          f"{len(S.POPULATION_CENSUS)} published totals, worst "
          f"{worst[0]:.2f}% at {worst[1]:,} years ago")
    if worst[0] >= 0.5:
        fails.append(f"the population is {worst[0]:.1f}% out at {worst[1]}")

    print("--- the boxes at the top follow the slider ---")
    leer = ("()=>['tWhen','tWhenSub','tPop','tSites','tCont']"
            ".map(i=>document.getElementById(i).textContent)")
    visto = []
    for v in (0, 300, 600, 900, 1000):
        pg.evaluate("(v)=>{const s=document.getElementById('t');s.value=v;"
                    "s.dispatchEvent(new Event('input'))}", v)
        pg.wait_for_timeout(90)
        visto.append(pg.evaluate(leer))
    ok = len({tuple(v) for v in visto}) == len(visto)
    print(f"  {'ok  ' if ok else 'FAIL'} five places on the slider give five "
          "different sets of boxes")
    if not ok:
        fails.append(f"the boxes repeat themselves: {visto}")
    # el año y la población de las casillas son los mismos que los del tablero
    for v in (150, 500, 850):
        pg.evaluate("(v)=>{const s=document.getElementById('t');s.value=v;"
                    "s.dispatchEvent(new Event('input'))}", v)
        pg.wait_for_timeout(90)
        a = pg.evaluate("()=>[document.getElementById('tWhen').textContent,"
                        "document.getElementById('tPop').textContent,"
                        "document.getElementById('tout').textContent,"
                        "document.getElementById('pop').textContent]")
        ok = a[0] == a[2] and a[1] == a[3]
        print(f"  {'ok  ' if ok else 'FAIL'} at {a[0]} the box reads {a[1]} and "
              f"the panel {a[3]}")
        if not ok:
            fails.append(f"the top box and the panel disagree: {a}")
    # y el número de sitios alcanzados crece con el tiempo, nunca al revés
    n = []
    for v in (0, 250, 500, 750, 1000):
        pg.evaluate("(v)=>{const s=document.getElementById('t');s.value=v;"
                    "s.dispatchEvent(new Event('input'))}", v)
        pg.wait_for_timeout(70)
        n.append(int(pg.evaluate("()=>document.getElementById('tSites')"
                                 ".textContent.split(' ')[0].replace(',','')")))
    ok = n == sorted(n) and n[-1] == len(live)
    print(f"  {'ok  ' if ok else 'FAIL'} the count of sites reached goes {n} and "
          f"ends at the {len(live)} the page follows")
    if not ok:
        fails.append(f"the count of sites reached goes {n}")

    print("--- the continental split is only drawn where it is evidence ---")
    for t, want in [(300000, False), (20000, False), (CONT_FROM + 500, False),
                    (CONT_FROM - 500, True), (0, True)]:
        pg.evaluate("(t)=>window.__setYbp(t)", t)
        got = pg.evaluate("()=>window.__mig().cont") is not None
        ok = got == want
        print(f"  {'ok  ' if ok else 'FAIL'} at {t:,} years ago the split is "
              f"{'drawn' if got else 'withheld'}")
        if not ok:
            fails.append(f"at {t} the continental split is "
                         f"{'drawn' if got else 'withheld'}, expected otherwise")

    pg.evaluate("()=>window.__setYbp(0)")
    cont = pg.evaluate("()=>window.__mig().cont")
    world = pg.evaluate("()=>window.__mig().world")
    e = abs(sum(cont) - world) / world * 100
    ok = e < 3
    print(f"  {'ok  ' if ok else 'FAIL'} the continents sum to within {e:.1f}% "
          "of the world total")
    if not ok:
        fails.append(f"the continents sum {e:.1f}% away from the world total")

    for bid, key in [("bLinks", "showLinks"), ("bLabels", "showLabels")]:
        before = pg.evaluate(f"()=>window.__mig().{key}")
        pg.click("#" + bid)
        pg.wait_for_timeout(150)
        after = pg.evaluate(f"()=>window.__mig().{key}")
        ok = before != after
        print(f"  {'ok  ' if ok else 'FAIL'} {bid} turns {key} off")
        if not ok:
            fails.append(f"{bid} does not change {key}")
        pg.click("#" + bid)

    if errs:
        fails.append(f"javascript errors: {errs}")
    br.close()

print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("all checks pass")
