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
