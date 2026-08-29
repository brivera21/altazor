#!/usr/bin/env python3
"""Verify the four phylogeny pages against what they actually draw.

Checks the rendered DOM offline: tip and node counts, the placement
claims the notes make (eukaryotes beside Asgard, ctenophores first,
whales inside Artiodactyla's card, humans beside Pan), key citations,
and the photo path: with the network cut no image may appear, and a
stubbed thumbnail must draw at its tip and in the card.

Usage: python3 verify_life.py
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
    "tree-of-life.html": dict(tips=11, doi="10.1038/nmicrobiol.2016.48",
        stub="Humans" and "Animals",
        probe=("(() => { const f=(n)=>n.n==='Asgard archaea'?n:(n.k||[]).map(f).find(Boolean);"
               " const a=f(ROOT); return a && a.k && a.k[0].n==='Eukarya'; })()"),
        probe_name="Eukarya branches from the Asgard archaea"),
    "animals.html": dict(tips=17, doi="10.1038/s41586-023-05936-6",
        stub="Mammalia",
        probe="ROOT.k[0].n==='Ctenophora'",
        probe_name="the comb jellies branch first"),
    "mammals.html": dict(tips=13, doi="10.1371/journal.pbio.3000494",
        stub="Chiroptera",
        probe=("(() => { const f=(n)=>n.n==='Artiodactyla'?n:(n.k||[]).map(f).find(Boolean);"
               " return f(ROOT).b.includes('whales'); })()"),
        probe_name="whales live inside the Artiodactyla card"),
    "primates.html": dict(tips=11, doi="10.1371/journal.pgen.1001342",
        stub="Humans",
        probe=("(() => { const f=(n)=>n.n==='Hominidae'?n:(n.k||[]).map(f).find(Boolean);"
               " const h=f(ROOT); const names=h.k.map(c=>c.n);"
               " return names[names.length-1]==='Humans' &&"
               " names[names.length-2]==='Chimpanzees and bonobos'; })()"),
        probe_name="humans sit beside the chimpanzees and bonobos"),
    "hominins.html": dict(tips=20, doi="10.1038/nature22336",
        stub="Homo sapiens",
        probe=("(() => { const f=(n)=>n.n==='Us and our closest kin'?n:(n.k||[]).map(f).find(Boolean);"
               " const u=f(ROOT); if(!u) return false;"
               " const nd=u.k[0], sap=u.k[1];"
               " return sap.n==='Homo sapiens' && nd.k.length===2 &&"
               " nd.k[0].n==='Homo neanderthalensis' && nd.k[1].n==='Denisovans'; })()"),
        probe_name="sapiens is sister to the Neanderthal-Denisovan pair"),
}
STUB = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' "
        "width='8' height='8'><rect width='8' height='8' fill='green'/></svg>")

with sync_playwright() as pw:
    br = pw.chromium.launch()
    for fname, c in CASES.items():
        pg = br.new_page(viewport={"width": 1300, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.route("**/*", lambda r: r.abort()
                 if r.request.url.startswith("http") else r.continue_())
        pg.goto((ROOT / fname).as_uri())
        pg.wait_for_timeout(500)
        print(f"--- {fname} ---")
        st = pg.evaluate("window.__tree()")
        check(f"{c['tips']} living tips drawn", st["tips"] == c["tips"], str(st["tips"]))
        n = pg.evaluate("document.querySelectorAll('#treesvg g[data-id]').length")
        check("every node interactive", n == st["nodes"], f"{n} vs {st['nodes']}")
        check(c["probe_name"], pg.evaluate(c["probe"]))
        check("offline shows no images, no stand-ins", st["imgs"] == 0
              and pg.evaluate("document.querySelectorAll('#treesvg image').length") == 0)
        every_w = pg.evaluate(
            "(()=>{let bad=0;(function w(n){if(!n.k&&!n.w)bad++;"
            "if(n.k)n.k.forEach(w);})(ROOT);return bad;})()")
        check("every living tip has photo candidates", every_w == 0, str(every_w))
        # stub one thumbnail and re-render: it must draw at the tip and card
        stub = c["stub"]
        drew = pg.evaluate(
            f"(()=>{{IMG[{stub!r}]={STUB!r};render();"
            f"const tip=tips.find(t=>t.n==={stub!r});show(tip.id);"
            "return document.querySelectorAll('#treesvg image').length===1"
            " && document.getElementById('cardImg').style.display==='block';})()")
        check("a stubbed thumbnail draws at its tip and in the card", drew)
        # click pins the card against hover; a second click lets go
        tid = pg.evaluate(f"tips.find(t=>t.n==={c['stub']!r}).id")
        other = pg.evaluate(f"tips.find(t=>t.n!=={c['stub']!r}).id")
        pg.click(f'[data-id="{tid}"]')
        pg.hover(f'[data-id="{other}"]')
        pg.wait_for_timeout(120)
        held = pg.evaluate("document.getElementById('nameTxt').textContent")
        pg.click(f'[data-id="{tid}"]')
        pg.hover(f'[data-id="{other}"]')
        pg.wait_for_timeout(120)
        moved = pg.evaluate("document.getElementById('nameTxt').textContent")
        check("a click pins the card and a second click lets go",
              held == c["stub"] and moved != c["stub"],
              f"held={held} moved={moved}")
        html = (ROOT / fname).read_text(encoding="utf-8")
        check(f"cites {c['doi']}", c["doi"] in html)
        check("credits Wikipedia for the images", "en.wikipedia.org" in html)
        check("no JS errors", not errs, "; ".join(errs))
        pg.close()
    br.close()

if fails:
    raise SystemExit(f"{len(fails)} check(s) failed")
print("all checks passed")
