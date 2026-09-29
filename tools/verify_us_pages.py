#!/usr/bin/env python3
"""Check what us.html, us-states.html and us-cities.html do in a browser.

verify_us.py checks us.html against its source data (it needs the builder's
pickles); verify_population_pages.py reads the numbers in the two tables.
This one loads the three pages offline in Chromium and checks what they do:
on us.html the map at the top, Sized by people, two states compared, a
region lifted, the arrow keys and the hint; on the tables the map, the
reordering, the 2020 and 2025 shares, the arrow keys, the baked flags, the
closed Sources and the phone width.

Usage: python3 verify_us_tables.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent.parent
fails = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name
          + (f"  [{detail}]" if detail and not ok else ""))
    if not ok:
        fails.append(name)


def offline(pg):
    pg.route("**/*", lambda r: r.abort()
             if r.request.url.startswith("http") else r.continue_())


def common(pg, errs, rowsel):
    ext = pg.evaluate("[...document.querySelectorAll('img')].filter(i=>/^https?:/.test(i.getAttribute('src'))).length")
    check("no image is fetched from the network", ext == 0, str(ext))
    broken = pg.evaluate("[...document.querySelectorAll('img.flag')].filter(i=>!i.complete||!i.naturalWidth).length")
    check("every flag has drawn", broken == 0, str(broken))
    det = pg.evaluate("[...document.querySelectorAll('details.sources')].map(d=>d.open)")
    check("the notes and references sit in one closed Sources element", det == [False], str(det))
    refs = pg.evaluate("!!document.querySelector('details.sources .refs')")
    check("the references are inside it", refs)
    # the rows slide to a new order, and the order is right
    pg.click("[data-sort=pct]"); pg.wait_for_timeout(1000)
    pcts = pg.evaluate(f"[...document.querySelectorAll('{rowsel}')].map(r=>+r.dataset.pct)")
    check("ordering by growth rate puts the rows in that order",
          pcts == sorted(pcts, reverse=True) and len(pcts) >= 20)
    moving = pg.evaluate(f"[...document.querySelectorAll('{rowsel}')].some(r=>r.style.transform)")
    check("and the rows have come to rest", not moving)
    pg.click("[data-sort=pop]"); pg.wait_for_timeout(1000)
    pops = pg.evaluate(f"[...document.querySelectorAll('{rowsel}')].map(r=>+r.dataset.pop)")
    check("ordering by population restores the ranking", pops == sorted(pops, reverse=True))
    check("no JS errors", not errs, "; ".join(errs)[:120])


with sync_playwright() as pw:
    br = pw.chromium.launch()

    # ---------------- us ----------------
    print("--- us.html ---")
    pg = br.new_page(viewport={"width": 1300, "height": 850})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    offline(pg)
    pg.goto((ROOT / "us.html").as_uri()); pg.wait_for_function("() => !!window.__us")
    top = pg.evaluate("document.getElementById('map').getBoundingClientRect().top")
    check("the map opens at the top, above the facts", top < 220, str(top))
    bottom = pg.evaluate("document.getElementById('bPop').getBoundingClientRect().bottom")
    check("the controls sit right under the map, in the first screen", bottom < 850, str(bottom))
    det = pg.evaluate("[...document.querySelectorAll('details.sources')].map(d=>d.open)")
    check("the notes and references sit in one closed Sources element", det == [False], str(det))
    inref = pg.evaluate("!!document.querySelector('details.sources .refs')&&!!document.querySelector('details.sources .notes')")
    check("and both are inside it", inref)
    caps = pg.evaluate("[...document.querySelectorAll('main > p, .mapcol > p')].filter(p=>p.offsetParent).map(p=>p.textContent.split(/\\s+/).length)")
    check("at most one caption and one hint are visible, each under 80 words",
          len(caps) <= 2 and all(c <= 80 for c in caps), str(caps))
    hint = pg.evaluate("window.__us().hint")
    check("the hint says what the Census regions are and what the rugged ground is",
          "Census regions" in hint and "rugged ground" in hint, hint[:80])
    pg.click("#mVer"); pg.wait_for_timeout(100)
    check("and changes with the mode", "Vernacular" in pg.evaluate("window.__us().hint"))
    pg.click("#mReg"); pg.wait_for_timeout(100)
    ne = pg.evaluate("(()=>{const t=[...document.querySelectorAll('#areas text')].find(t=>t.textContent==='Northeast');"
                     "return t?[+t.getAttribute('x'),+t.getAttribute('y')]:null;})()")
    check("the Northeast name sits offshore, clear of New Jersey", ne == [928, 262], str(ne))
    ilbl = pg.evaluate("[...document.querySelectorAll('#frames text')].map(t=>t.textContent)")
    check("the insets are captioned plainly", ilbl == ["Alaska, own scale", "Hawaii, own scale"], str(ilbl))
    # sized by people
    ks = pg.evaluate("(()=>{const u=window.__us();return {nj:u.k('NJ'),wy:u.k('WY'),ca:u.k('CA'),ak:u.k('AK')};})()")
    check("New Jersey swells and Wyoming and Alaska shrink",
          ks["nj"] > 3 and ks["wy"] < 0.3 and ks["ak"] < 0.3 and 1 < ks["ca"] < 2, str(ks))
    area = pg.evaluate("(()=>{const u=window.__us();const A=c=>GEO[c].A*GEO[c].k**2;"
                       "return (A('NJ')/A('TX'))/(META.NJ.pop/META.TX.pop);})()")
    check("sized by people, a state's area on the page is its population", abs(area - 1) < 1e-6, str(area))
    pg.click("#bPop")
    pg.wait_for_function("window.__us().popT===1", timeout=5000)
    st = pg.evaluate("window.__us()")
    tf = pg.evaluate("document.querySelector('#fills path[data-c=NJ]').getAttribute('transform')")
    check("Sized by people glides every state to its size", st["popOn"] and tf and tf.startswith("matrix(3."), str(tf))
    op = pg.evaluate("getComputedStyle(document.getElementById('rivers')).opacity")
    check("and the rivers and rugged ground step aside", op == "0", op)
    pg.click("#bPop")
    pg.wait_for_function("window.__us().popT===0", timeout=5000)
    tf = pg.evaluate("document.querySelector('#fills path[data-c=NJ]').getAttribute('transform')")
    check("and back to the ground", tf is None, str(tf))
    order = pg.evaluate("[...document.querySelectorAll('#fills path')].map(p=>p.dataset.c).join()")
    check("with the states back in their own order", order == pg.evaluate("ORIG.join()"))
    # two states compared
    pg.evaluate("pick('TX')"); pg.evaluate("pick('AK')"); pg.wait_for_timeout(1200)
    st = pg.evaluate("window.__us()")
    check("a second state clicked is compared with the first", st["sel"] == "TX" and st["cmp"] == "AK" and st["ghost"] == 1,
          f"{st['sel']} {st['cmp']} {st['ghost']}")
    cmp = pg.evaluate("document.getElementById('cmpBox').textContent")
    check("the panel sets their areas, people and densities side by side",
          "695,662" in cmp and "1,723,337" in cmp and "People per km" in cmp, cmp[:80])
    gb = pg.evaluate("(()=>{const b=document.querySelector('#ghost path').getBBox();"
                     "const m=document.querySelector('#ghost path').transform.baseVal.consolidate().matrix;return m.a;})()")
    want = pg.evaluate("window.__us().g('AK')/window.__us().g('TX')")
    check("the ghost of Alaska is drawn at the scale of Texas", abs(gb - want) < 1e-6, f"{gb} {want}")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(100)
    st = pg.evaluate("window.__us()")
    check("Escape lets both go", st["sel"] is None and st["cmp"] is None and st["ghost"] == 0)
    # a region lifted
    pg.evaluate("[...document.querySelectorAll('#areas text')].find(t=>t.textContent==='West').dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    pg.wait_for_timeout(100)
    st = pg.evaluate("window.__us()")
    check("a region's name lifts it and dims the rest", st["focusReg"] == 3 and st["dim"] == 51 - 13, str(st["dim"]))
    nm = pg.evaluate("document.getElementById('selName').textContent")
    check("and the panel sums it up", nm == "West", nm)
    pg.keyboard.press("Escape")
    # arrow keys, only with focus on the map
    pg.focus("#map"); pg.keyboard.press("ArrowRight"); pg.keyboard.press("ArrowRight")
    st = pg.evaluate("window.__us()")
    check("arrow keys walk the states by population when the map has focus",
          st["sel"] == "TX" and st["capital"] == "Austin", f"{st['sel']} {st['capital']}")
    check("and the panel gives the rank", pg.evaluate("document.getElementById('selRank').textContent") == "No. 2 of 50")
    pg.focus("#bRiv"); pg.keyboard.press("ArrowRight")
    check("and not otherwise", pg.evaluate("window.__us().sel") == "TX")
    pg.keyboard.press("Escape")
    check("no JS errors", not errs, "; ".join(errs)[:120])
    pg.close()

    # ---------------- us-states ----------------
    print("--- us-states.html ---")
    pg = br.new_page(viewport={"width": 1300, "height": 850})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    offline(pg)
    pg.goto((ROOT / "us-states.html").as_uri()); pg.wait_for_timeout(300)
    top = pg.evaluate("document.getElementById('usmap').getBoundingClientRect().top")
    check("the map opens in the first screen", top < 300, str(top))
    shaded = pg.evaluate("[...document.querySelectorAll('#usmap path[data-cc]')].filter(p=>getComputedStyle(p).fill!=='rgb(38, 44, 51)').length")
    check("all fifty states and the District are shaded by their change", shaded == 51, str(shaded))
    idaho = pg.evaluate("getComputedStyle(document.querySelector('#usmap path[data-cc=id]')).fill")
    check("Idaho, the fastest grower, carries the strongest blue", idaho == "rgb(57, 135, 229)", idaho)
    hawaii = pg.evaluate("getComputedStyle(document.querySelector('#usmap path[data-cc=hi]')).fill")
    check("Hawaii, the steepest decline, carries the strongest pink", hawaii == "rgb(213, 81, 129)", hawaii)
    pg.hover("#usmap path[data-cc=tx]"); pg.wait_for_timeout(100)
    hl = pg.evaluate("[...document.querySelectorAll('tr.strow.hl')].map(t=>t.dataset.cc)")
    check("hovering a state lights its row", hl == ["tx"], str(hl))
    check("and names it under the map",
          pg.evaluate("document.getElementById('mapcap').textContent").startswith("Texas"))
    pg.click("#usmap path[data-cc=tx]"); pg.wait_for_timeout(100)
    st = pg.evaluate("window.__uss()")
    check("a click on the map fills the tiles", st["sel"] == "tx" and st["tiles"][0] == "31.7 million",
          str(st["tiles"]))
    wy = pg.evaluate("document.querySelector('tr.strow[data-cc=wy]').click(), document.getElementById('v4').textContent")
    check("Wyoming's lead tile reads none, with no dash", wy == "none", wy)
    pg.keyboard.press("Escape")
    # 2020 and 2025
    ca25 = pg.evaluate("document.querySelector('tr.strow[data-cc=ca] .pct').textContent")
    pg.click("[data-yr='2020']"); pg.wait_for_timeout(1200)
    ca20 = pg.evaluate("document.querySelector('tr.strow[data-cc=ca] .pct').textContent")
    pop20 = pg.evaluate("document.querySelector('tr.strow[data-cc=ca] td.pop').firstChild.nodeValue")
    w20 = pg.evaluate("document.querySelector('tr.strow[data-cc=ca] .fill').style.width")
    check("2020 shows the 2020 shares and populations",
          ca25 == "11.51%" and ca20 == "11.93%" and pop20.strip() == "39,555,703" and w20 == "100%",
          f"{ca25} {ca20} {pop20} {w20}")
    gapv = pg.evaluate("getComputedStyle(document.querySelector('tr.strow .gap')).display")
    check("the leads, which are 2025 figures, step aside in 2020", gapv == "none", gapv)
    pg.click("[data-yr='2025']"); pg.wait_for_timeout(1200)
    check("and 2025 brings them back",
          pg.evaluate("document.querySelector('tr.strow[data-cc=ca] .pct').textContent") == "11.51%")
    # arrow keys, only with focus on the table or map
    pg.focus("#tbl"); pg.keyboard.press("ArrowDown"); pg.keyboard.press("ArrowDown")
    check("arrow keys walk the ranking when the table has focus",
          pg.evaluate("window.__uss().sel") == "tx")
    pg.focus("[data-sort=pop]"); pg.keyboard.press("ArrowDown")
    check("and not otherwise", pg.evaluate("window.__uss().sel") == "tx")
    pg.keyboard.press("Escape")
    head = pg.evaluate("document.querySelector('#tbl th .gh').textContent")
    check("the green lead is named in its column header", "lead over next" in head, head)
    common(pg, errs, "#tb tr.strow")
    pg.close()

    # ---------------- us-cities ----------------
    print("--- us-cities.html ---")
    pg = br.new_page(viewport={"width": 1300, "height": 850})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    offline(pg)
    pg.goto((ROOT / "us-cities.html").as_uri()); pg.wait_for_timeout(300)
    st = pg.evaluate("window.__usc()")
    check("twenty dots on the map", st["dots"] == 20, str(st["dots"]))
    check("the six largest are named", st["labels"] == 6, str(st["labels"]))
    inside = pg.evaluate(
        "(()=>{const vb=document.getElementById('cmap').viewBox.baseVal;"
        "return C.every(d=>d.x-d.r>=vb.x&&d.x+d.r<=vb.x+vb.width&&d.y-d.r>=vb.y&&d.y+d.r<=vb.y+vb.height);})()")
    check("every dot is inside the frame", inside)
    # the dots sit in the right part of the country
    order = pg.evaluate("(()=>{const g=n=>C.find(c=>c.n===n);"
                        "return g('Seattle').x<g('Denver').x&&g('Denver').x<g('Chicago').x&&g('Chicago').x<g('New York').x"
                        "&&g('Seattle').y<g('San Diego').y&&g('Chicago').y<g('Houston').y;})()")
    check("Seattle, Denver, Chicago and New York run west to east; Houston is south of Chicago", order)
    area = pg.evaluate("(()=>{const a=C[0],b=C[19];return (a.r*a.r)/(b.r*b.r)/(a.pop/b.pop);})()")
    check("a dot's area is its population", abs(area - 1) < 0.02, str(area))
    pg.hover("tr.crow[data-i='4']"); pg.wait_for_timeout(100)
    lit = pg.evaluate("[...document.querySelectorAll('#cmap .dot.hl')].map(g=>+g.dataset.i)")
    check("hovering a row lights its dot", lit == [4], str(lit))
    check("and names it", "Phoenix" in pg.evaluate("[...document.querySelectorAll('#labs text')].map(t=>t.textContent).join()"))
    pg.click("tr.crow[data-i='4'] td.num"); pg.wait_for_timeout(100)
    st = pg.evaluate("window.__usc()")
    check("a click on a row fills the tiles", st["sel"] == 4 and st["tiles"][0].startswith("1.67"),
          str(st["tiles"]))
    pg.keyboard.press("Escape")
    links = pg.evaluate("[...document.querySelectorAll('tr.crow a')].map(a=>a.getAttribute('href'))")
    check("New York and Los Angeles link to their pages",
          sorted(links) == ["los-angeles.html", "new-york.html"], str(links))
    pg.click("[data-sort=chg]"); pg.wait_for_timeout(1000)
    sub = pg.evaluate("getComputedStyle(document.querySelector('tr.total.sub')).display")
    check("the first-ten subtotal steps aside when the order is not by population", sub == "none", sub)
    pg.click("[data-sort=pop]"); pg.wait_for_timeout(1000)
    nxt = pg.evaluate("document.querySelector('tr.total.sub').nextElementSibling.dataset.i")
    check("and returns after the tenth city", nxt == "10", str(nxt))
    common(pg, errs, "#tb tr.crow")
    pg.close()

    # ---------------- phones ----------------
    for f in ("us.html", "us-states.html", "us-cities.html"):
        ph = br.new_page(viewport={"width": 390, "height": 844})
        offline(ph)
        ph.goto((ROOT / f).as_uri()); ph.wait_for_timeout(300)
        ov = ph.evaluate("document.documentElement.scrollWidth - innerWidth")
        check(f"{f}: no sideways overflow on a phone", ov == 0, str(ov))
        ph.close()
    br.close()

if fails:
    raise SystemExit(f"{len(fails)} check(s) failed")
print("all checks passed")
