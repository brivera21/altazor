#!/usr/bin/env python3
"""Verify the three phylogeny pages against what they actually draw.

Checks topology facts against the rendered DOM: tip and node counts, the
placement claims the notes make (eukaryotes beside Asgard, whales inside
Artiodactyla's card, humans beside Pan), key citations present, no JS
errors offline.

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
        probe=("(() => { const f=(n)=>n.n==='Asgard archaea'?n:(n.k||[]).map(f).find(Boolean);"
               " const a=f(ROOT); return a && a.k && a.k[0].n==='Eukarya'; })()"),
        probe_name="Eukarya branches from the Asgard archaea"),
    "mammals.html": dict(tips=13, doi="10.1371/journal.pbio.3000494",
        probe=("(() => { const f=(n)=>n.n==='Artiodactyla'?n:(n.k||[]).map(f).find(Boolean);"
               " return f(ROOT).b.includes('whales'); })()"),
        probe_name="whales live inside the Artiodactyla card"),
    "primates.html": dict(tips=11, doi="10.1371/journal.pgen.1001342",
        probe=("(() => { const f=(n)=>n.n==='Hominidae'?n:(n.k||[]).map(f).find(Boolean);"
               " const h=f(ROOT); const names=h.k.map(c=>c.n);"
               " return names[names.length-1]==='Humans' &&"
               " names[names.length-2]==='Chimpanzees and bonobos'; })()"),
        probe_name="humans sit beside the chimpanzees and bonobos"),
}

with sync_playwright() as pw:
    br = pw.chromium.launch()
    for fname, c in CASES.items():
        pg = br.new_page(viewport={"width": 1300, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.route("**/*", lambda r: r.abort()
                 if r.request.url.startswith("http") else r.continue_())
        pg.goto((ROOT / fname).as_uri())
        pg.wait_for_timeout(400)
        print(f"--- {fname} ---")
        st = pg.evaluate("window.__tree()")
        check(f"{c['tips']} living tips drawn", st["tips"] == c["tips"], str(st["tips"]))
        n = pg.evaluate("document.querySelectorAll('#treesvg g[data-id]').length")
        check("every node interactive", n == st["nodes"], f"{n} vs {st['nodes']}")
        check(c["probe_name"], pg.evaluate(c["probe"]))
        html = (ROOT / fname).read_text(encoding="utf-8")
        check(f"cites {c['doi']}", c["doi"] in html)
        card = pg.evaluate("(()=>{show('n0');return document.getElementById('nameTxt').textContent})()")
        check("root card answers", len(card) > 2, card)
        check("no JS errors", not errs, "; ".join(errs))
        pg.close()
    br.close()

if fails:
    raise SystemExit(f"{len(fails)} check(s) failed")
print("all checks passed")
