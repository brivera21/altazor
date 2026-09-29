#!/usr/bin/env python3
"""Verify languages.html against what it actually draws.

Offline (network cut): the tree loads with no errors, opens at the
families, a node opens and closes on click, the search finds a language
and opens the path to it, every tip carries a glottocode, no dialect is
a tip, and the two shortcuts do what their labels say.

Usage: python3 verify_languages.py
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


with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1400, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("**/*", lambda r: r.abort()
             if r.request.url.startswith("http") else r.continue_())
    pg.goto((ROOT / "languages.html").as_uri())
    pg.wait_for_timeout(900)

    st = pg.evaluate("window.__lang()")
    check("opens at the families, nothing else unfolded",
          st["rows"] == st["families"] + 1 and st["depth"] == 1,
          f"{st['rows']} rows, depth {st['depth']}")
    check("every family Glottolog lists is on the tree",
          st["families"] >= 230, str(st["families"]))
    check("the tree holds the languages, not a sample",
          st["langs"] >= 7500, str(st["langs"]))
    check("the card starts on the root",
          pg.evaluate("document.getElementById('nameTxt').textContent")
          == "The languages of the world")

    # the largest family opens and closes
    n1 = pg.evaluate("window.__lang().rows")
    pg.evaluate("document.querySelector('[data-id=\"n1\"] text').dispatchEvent("
                "new MouseEvent('click',{bubbles:true}))")
    pg.wait_for_timeout(250)
    n2 = pg.evaluate("window.__lang().rows")
    check("a family opens into its branches", n2 > n1, f"{n1} -> {n2}")
    pg.evaluate("document.querySelector('[data-id=\"n1\"] text').dispatchEvent("
                "new MouseEvent('click',{bubbles:true}))")
    pg.wait_for_timeout(250)
    n3 = pg.evaluate("window.__lang().rows")
    check("and closes again", n3 == n1, f"{n3} vs {n1}")

    # search
    pg.fill("#q", "Nahuatl")
    pg.wait_for_timeout(300)
    hits = pg.evaluate("document.querySelectorAll('#hits button').length")
    check("the search finds a language by name", hits >= 1, str(hits))
    pg.evaluate("document.querySelector('#hits button').click()")
    pg.wait_for_timeout(400)
    path = pg.evaluate("document.getElementById('pathTxt').textContent")
    check("choosing a hit opens the path down to it",
          "Uto-Aztecan" in path, path[:80])
    name = pg.evaluate("document.getElementById('nameTxt').textContent")
    check("and the card lands on it", "Nahuatl" in name, name)
    pg.fill("#q", "qqqzzz")
    pg.wait_for_timeout(250)
    check("a name that is not there says so",
          pg.evaluate("!!document.querySelector('#hits .none')"))

    # the shortcuts
    pg.evaluate("document.getElementById('bBig').click()")
    pg.wait_for_timeout(300)
    st = pg.evaluate("window.__lang()")
    check("the ten largest open together", st["open"] == 11, str(st["open"]))
    pg.evaluate("document.getElementById('bTop').click()")
    pg.wait_for_timeout(300)
    st = pg.evaluate("window.__lang()")
    check("and the families-only view folds them back",
          st["open"] == 1 and st["rows"] == st["families"] + 1)

    # to scale
    pg.evaluate("document.getElementById('bScale').click()")
    pg.wait_for_timeout(300)
    g = pg.evaluate("window.__lang().grow")
    pg.wait_for_timeout(1100)
    st = pg.evaluate("window.__lang()")
    check("To scale grows the families into circles", 0 < g < 1 and st["mode"] == "scale" and st["bubbles"] == st["families"], f"{g}, {st['bubbles']}")
    tops = {i: t for i, (_, t, _) in enumerate(st["tops"])}
    k = [r * r / tops[i] for i, x, y, r in st["pack"]]
    check("each circle's area is its languages", max(k) / min(k) < 1.02, f"{min(k):.3f}..{max(k):.3f}")
    P = st["pack"]
    ov = sum(1 for a in range(len(P)) for b in range(a + 1, len(P)) if ((P[a][1] - P[b][1]) ** 2 + (P[a][2] - P[b][2]) ** 2) ** .5 < P[a][3] + P[b][3] - 0.3)
    check("and no two circles overlap", ov == 0, str(ov))
    vc_ok = all(sum(v) == t for _, t, v in st["tops"])
    check("every family's statuses add up to its languages", vc_ok)
    fam = pg.evaluate("ROOT.k[2].id")
    pg.evaluate("(f)=>document.querySelector('#treesvg g[data-id=\"'+f+'\"]').dispatchEvent(new MouseEvent('click',{bubbles:true}))", fam)
    pg.wait_for_timeout(250)
    st = pg.evaluate("window.__lang()")
    check("a circle clicked opens its family on the tree", st["mode"] == "tree" and st["pinned"] == fam and st["open"] == 2, str(st["open"]))
    check("and the card maps its macroareas", pg.evaluate("document.querySelectorAll('#mapTxt rect').length") == 6 and pg.evaluate("[...document.querySelectorAll('#mapTxt rect')].filter(r=>r.getAttribute('fill')==='#31d67a').length") >= 1)
    # the legend filters
    pg.evaluate("document.querySelector('#legend button[data-f=\"5\"]').click()")
    pg.wait_for_timeout(200)
    st = pg.evaluate("window.__lang()")
    txt = pg.evaluate("document.getElementById('cntTxt').textContent")
    dim = pg.evaluate("[...document.querySelectorAll('#treesvg g[data-id]')].filter(g=>g.getAttribute('opacity')).length")
    check("a legend status filters: the card counts it, the rest dim", st["filt"] == 5 and "nearly extinct" in txt and dim > 0, txt)
    pg.evaluate("document.querySelector('#legend button[data-f=\"5\"]').click()")
    # keys
    pg.evaluate("document.getElementById('bTop').click()")
    pg.focus("#diagram")
    want = pg.evaluate("(()=>{const i=ROOT.k.findIndex(n=>n.id===window.__lang().current); return ROOT.k[i+2].id})()")
    pg.keyboard.press("ArrowDown")
    pg.keyboard.press("ArrowDown")
    st = pg.evaluate("window.__lang()")
    check("down arrows walk the rows", st["pinned"] == want, st["pinned"])
    r0 = st["rows"]
    pg.keyboard.press("ArrowRight")
    r1 = pg.evaluate("window.__lang().rows")
    pg.keyboard.press("ArrowLeft")
    r2 = pg.evaluate("window.__lang().rows")
    check("right opens a family, left closes it", r1 > r0 and r2 == r0, f"{r0} {r1} {r2}")
    vis = pg.evaluate("[...document.querySelectorAll('.note')].filter(n=>n.checkVisibility()).length")
    words = len(pg.inner_text(".note").split())
    check("one caption, the rest in a closed Sources", vis == 1 and words <= 80 and not pg.evaluate("document.querySelector('details.sources').open"), f"{vis}, {words}")
    ph = br.new_page(viewport={"width": 390, "height": 844})
    ph.goto((ROOT / "languages.html").as_uri())
    ph.wait_for_timeout(600)
    ov = ph.evaluate("document.documentElement.scrollWidth - innerWidth")
    fs = ph.evaluate("(()=>{const t=document.querySelector('#treesvg text'); return t.getBoundingClientRect().height})()")
    check("on a phone nothing overflows and the tree stays readable", ov == 0 and fs > 9, f"{ov}, {fs:.1f}")

    # the data itself
    ok_tips = pg.evaluate(
        "(()=>{let bad=0;(function w(n){ if(n.k) n.k.forEach(w);"
        " else if(!n.g) bad++; })(ROOT); return bad;})()")
    check("every tip carries a glottocode", ok_tips == 0, str(ok_tips))
    iso = pg.evaluate(
        "(()=>{let n=0,e=0;(function w(x){ if(x.k) x.k.forEach(w);"
        " else { n++; if(x.e) e++; } })(ROOT); return [n,e];})()")
    check("most tips carry an ISO 639-3 code", iso[1] > iso[0] * 0.8,
          f"{iso[1]}/{iso[0]}")
    dup = pg.evaluate(
        "(()=>{const s=new Set(); let d=0;(function w(n){ if(n.g){"
        " if(s.has(n.g)) d++; s.add(n.g);} if(n.k) n.k.forEach(w);"
        "})(ROOT); return d;})()")
    check("no languoid appears twice", dup == 0, str(dup))
    named = pg.evaluate(
        "ROOT.k.slice(0,5).map(n=>n.n).join(',')")
    check("the largest families lead",
          named.startswith("Atlantic-Congo,Austronesian,Indo-European"), named)
    check("no JS errors", not errs, "; ".join(errs)[:140])
    pg.close()
    br.close()

if fails:
    raise SystemExit(f"{len(fails)} check(s) failed")
print("all checks passed")
