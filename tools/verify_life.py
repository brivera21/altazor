#!/usr/bin/env python3
"""Verify the four phylogeny pages against what they actually draw.

Checks the rendered DOM offline: tip and node counts, the placement
claims the notes make (eukaryotes beside Asgard, ctenophores first,
whales inside Artiodactyla's card, humans beside Pan), key citations,
and the photo path: with the network cut no image may appear, and a
stubbed thumbnail must draw at its tip and in the card. Then the
engine's states: a branch point folds and unfolds, the arrow keys
travel the tree, a linked tip carries its diagram's address, the
hominins' time layout puts each bar at its dates and a date on the
slider lights the species alive then, the animals' size toggle scales
the dots by count, and nothing overflows a phone screen.

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
        stub="Animals", pin="Fungi", link=("Animals", "animals.html"), start="Life",
        probe=("(() => { const f=(n)=>n.n==='Asgard archaea'?n:(n.k||[]).map(f).find(Boolean);"
               " const a=f(ROOT); return a && a.k && a.k[0].n==='Eukarya'; })()"),
        probe_name="Eukarya branches from the Asgard archaea"),
    "animals.html": dict(tips=17, doi="10.1038/s41586-023-05936-6",
        stub="Mammalia", pin="Porifera", link=("Mammalia", "mammals.html"), start="Animalia",
        probe="ROOT.k[0].n==='Ctenophora'",
        probe_name="the comb jellies branch first"),
    "mammals.html": dict(tips=13, doi="10.1371/journal.pbio.3000494",
        stub="Chiroptera", pin="Chiroptera", link=("Primates", "primates.html"), start="Mammalia",
        probe=("(() => { const f=(n)=>n.n==='Artiodactyla'?n:(n.k||[]).map(f).find(Boolean);"
               " return f(ROOT).b.includes('whales'); })()"),
        probe_name="whales live inside the Artiodactyla card"),
    "primates.html": dict(tips=11, doi="10.1371/journal.pgen.1001342",
        stub="Humans", pin="Gorillas", link=("Humans", "hominins.html"), start="Primates",
        probe=("(() => { const f=(n)=>n.n==='Hominidae'?n:(n.k||[]).map(f).find(Boolean);"
               " const h=f(ROOT); const names=h.k.map(c=>c.n);"
               " return names[names.length-1]==='Humans' &&"
               " names[names.length-2]==='Chimpanzees and bonobos'; })()"),
        probe_name="humans sit beside the chimpanzees and bonobos"),
    "hominins.html": dict(tips=20, doi="10.1038/nature22336",
        stub="Homo sapiens", pin="Homo sapiens", link=None, start="Hominini",
        probe=("(() => { const f=(n)=>n.n==='Sapiens and kin'?n:(n.k||[]).map(f).find(Boolean);"
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
        pg = br.new_page(viewport={"width": 1300, "height": 900}, reduced_motion="reduce")
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
        pin = c["pin"]
        tid = pg.evaluate(f"tips.find(t=>t.n==={pin!r}).id")
        other = pg.evaluate(f"tips.find(t=>t.n!=={pin!r} && !t.href).id")
        pg.click(f'[data-id="{tid}"] text')
        pg.hover(f'[data-id="{other}"] text')
        pg.wait_for_timeout(120)
        held = pg.evaluate("document.getElementById('nameTxt').textContent")
        pg.click(f'[data-id="{tid}"] text')
        pg.hover(f'[data-id="{other}"] text')
        pg.wait_for_timeout(120)
        moved = pg.evaluate("document.getElementById('nameTxt').textContent")
        check("a click pins the card and a second click lets go",
              held.startswith(pin) and not moved.startswith(pin),
              f"held={held} moved={moved}")
        pg.keyboard.press("Escape")
        # the card opens on the page's starting node
        pg.mouse.move(1200, 850); pg.reload(); pg.wait_for_timeout(300)
        opened = pg.evaluate("document.getElementById('nameTxt').textContent")
        check(f"the card opens on {c['start']}", opened.startswith(c["start"]), opened)
        # a branch point folds its subtree and the tips re-space; unfold restores them
        fid = pg.evaluate("ROOT.k.find(k=>k.k).id")
        n_in = pg.evaluate(f"countTips(byId[{fid!r}])")
        pg.click(f'[data-fold="{fid}"]')
        pg.wait_for_timeout(150)
        st2 = pg.evaluate("window.__tree()")
        ys = pg.evaluate("tips.map(t=>t.py)")
        gaps = {round(b - a, 3) for a, b in zip(ys, ys[1:])}
        check("a branch point folds: its tips leave and the rest re-space evenly",
              st2["tips"] == c["tips"] - n_in + 1 and len(gaps) == 1 and st2["folded"] == [fid],
              f"tips={st2['tips']} gaps={gaps} folded={st2['folded']}")
        check("a folded node draws as a tip with a plus and says how many it holds",
              pg.evaluate(f'document.querySelector("[data-fold={fid!r}] path").getAttribute("d").includes("v5.6")')
              and pg.evaluate(f'document.querySelector("[data-id={fid!r}] text").textContent').endswith("tips folded"))
        pg.click("#unfoldBtn")
        pg.wait_for_timeout(150)
        check("unfold all brings every tip back", pg.evaluate("window.__tree().tips") == c["tips"])
        # the arrow keys travel the tree: right into the first branch, down a row, left out
        pg.hover('[data-id="n0"] text')
        pg.focus("#diagram")
        pg.keyboard.press("ArrowRight")
        first = pg.evaluate("document.getElementById('nameTxt').textContent")
        pg.keyboard.press("ArrowDown")
        second = pg.evaluate("document.getElementById('nameTxt').textContent")
        pg.keyboard.press("ArrowLeft")
        back = pg.evaluate("document.getElementById('nameTxt').textContent")
        want_first = pg.evaluate("ROOT.k[0].n")
        check("the arrow keys travel the tree: right into a branch, down a row, left out",
              first.startswith(want_first) and second != first and back != second,
              f"{first} / {second} / {back}")
        pg.keyboard.press("Escape")
        # a linked tip carries its diagram's address and says so on the card
        if c["link"]:
            name, href = c["link"]
            lid = pg.evaluate(f"tips.find(t=>t.n==={name!r}).id")
            got = pg.evaluate(f'document.querySelector("[data-id={lid!r}]").getAttribute("data-href")')
            pg.hover(f'[data-id="{lid}"] text')
            pg.wait_for_timeout(80)
            check(f"a click on {name} opens {href}", got == href
                  and "A click opens it" in pg.evaluate("document.getElementById('bodyTxt').textContent"), str(got))
        # the phone layout: nothing wider than the screen
        pg.set_viewport_size({"width": 390, "height": 844})
        pg.wait_for_timeout(150)
        over = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
        check("nothing overflows a 390px screen", over == 0, str(over))
        pg.set_viewport_size({"width": 1300, "height": 900})
        if fname == "hominins.html":
            pg.click("#timeBtn")
            pg.wait_for_timeout(150)
            st3 = pg.evaluate("window.__tree()")
            xt = lambda ma: 16 + (1010 - 16 - 300) * (1 - ma / 7)
            sap, sah, root = st3["pos"]["Homo sapiens"], st3["pos"]["Sahelanthropus tchadensis"], st3["pos"]["Hominini"]
            check("to time: sapiens runs from 300 ka to now, Sahelanthropus from 7 to 6 Ma, the root at 7 Ma",
                  st3["mode"] == 1 and abs(sap["b"] - xt(0.3)) < 0.5 and abs(sap["e"] - xt(0)) < 0.5
                  and abs(sah["b"] - xt(7)) < 0.5 and abs(sah["e"] - xt(6)) < 0.5 and abs(root["x"] - xt(7)) < 0.5,
                  f"{sap} {sah} {root}")
            homo = st3["pos"]["Homo"]
            check("a clade sits at the oldest fossil of its clade: Homo at habilis's 2.4 Ma",
                  abs(homo["x"] - xt(2.4)) < 0.5, str(homo))
            check("every tip draws a bar in the time layout",
                  pg.evaluate("document.querySelectorAll('#treesvg g[data-id] rect[rx=\"3\"]').length") == c["tips"])
            pg.evaluate("document.getElementById('scrub').value=1500; document.getElementById('scrub').dispatchEvent(new Event('input'))")
            pg.wait_for_timeout(80)
            lit = pg.evaluate("[...document.querySelectorAll('#treesvg g[data-id]')].filter(g=>!g.hasAttribute('opacity')&&!byId[g.dataset.id].k).map(g=>byId[g.dataset.id].n).sort()")
            check("at 1.5 Ma four species stay lit: boisei, robustus, erectus and habilis",
                  lit == ["Homo erectus", "Homo habilis", "Paranthropus boisei", "Paranthropus robustus"]
                  and pg.evaluate("document.getElementById('cntTxt').textContent").startswith("4 species"), str(lit))
            pg.click("#scrubOff")
            pg.click("#timeBtn")
            pg.wait_for_timeout(150)
            st4 = pg.evaluate("window.__tree()")
            check("make to time again gives the cladogram back", st4["mode"] == 0 and st4["scrub"] is None
                  and abs(st4["pos"]["Homo sapiens"]["b"] - st4["pos"]["Homo sapiens"]["e"]) < 0.01)
        if fname in ("mammals.html", "primates.html"):
            # divergence ages: each branching point at its TimeTree median, living tips at now
            mx, ages = {"mammals.html": (190, {"Mammalia": 181.2, "Theria": 159.2, "Placentalia": 97.0}),
                        "primates.html": (90, {"Euarchontoglires": 83.5, "Primates": 71.6, "Hominidae": 15.6})}[fname]
            xt = lambda ma: 16 + (1010 - 16 - 300) * (1 - ma / mx)
            pg.click("#timeBtn")
            pg.wait_for_timeout(150)
            st3 = pg.evaluate("window.__tree()")
            bad = {k: st3["pos"][k]["x"] for k, a in ages.items() if abs(st3["pos"][k]["x"] - xt(a)) > 0.5}
            tipx = {round(pg.evaluate(f"window.__tree().pos[{t!r}].x"), 1) for t in pg.evaluate("tips.map(t=>t.n)")}
            check("to time: branching points sit at their TimeTree ages and every living tip at now",
                  st3["mode"] == 1 and not bad and tipx == {round(xt(0), 1)}, f"bad={bad} tipx={tipx}")
            check("no date slider on a divergence tree", pg.evaluate("document.getElementById('scrubLab').hidden"))
            k0 = next(iter(ages))
            pg.hover('[data-id="' + pg.evaluate(f"Object.values(byId).find(n=>n.n==={k0!r}).id") + '"] text')
            pg.wait_for_timeout(80)
            check(f"the card gives the split age and its source: {k0} ~{ages[k0]:g} Ma, TimeTree",
                  f"split ~{ages[k0]:g} Ma" in pg.evaluate("document.getElementById('cntTxt').textContent")
                  and "TimeTree" in pg.evaluate("document.getElementById('srcTxt').textContent"))
            pg.click("#timeBtn")
            pg.wait_for_timeout(150)
            check("make to time again gives the cladogram back", pg.evaluate("window.__tree().mode") == 0)
            check("cites TimeTree 5 in the sources", "10.1093/molbev/msac174" in (ROOT / fname).read_text(encoding="utf-8"))
        if fname in ("tree-of-life.html", "animals.html"):
            check("no time toggle on an undated tree", pg.evaluate("document.getElementById('timeBtn').hidden"))
        if fname == "animals.html":
            pg.click("#sizeBtn")
            pg.wait_for_timeout(150)
            st3 = pg.evaluate("window.__tree()")
            r = {k: v["r"] for k, v in st3["pos"].items()}
            check("size by species: Arthropoda's dot is the largest, Cephalochordata's near a point, the rest between",
                  st3["sized"] and r["Arthropoda"] == max(r.values()) and r["Cephalochordata"] < 3.5
                  and r["Mollusca"] > r["Nematoda"] > r["Tunicata"] > r["Cephalochordata"], str(r))
            pg.hover('[data-id="' + pg.evaluate("tips.find(t=>t.n==='Arthropoda').id") + '"] text')
            pg.wait_for_timeout(80)
            check("and the card gives the share of all animals: Arthropoda 75%",
                  "75% of described animal species" in pg.evaluate("document.getElementById('cntTxt').textContent"))
            pg.click("#sizeBtn")
            pg.wait_for_timeout(150)
            check("the toggle off restores equal dots",
                  len({round(v["r"], 3) for k, v in pg.evaluate("window.__tree()")["pos"].items() if not pg.evaluate(f"!!byId[Object.values(byId).find(n=>n.n==={k!r}).id].k")}) == 1)
        html = (ROOT / fname).read_text(encoding="utf-8")
        check(f"cites {c['doi']}", c["doi"] in html)
        check("no em dashes", "\u2014" not in html)
        check("credits Wikipedia for the images", "en.wikipedia.org" in html)
        check("no JS errors", not errs, "; ".join(errs))
        pg.close()
    br.close()

if fails:
    raise SystemExit(f"{len(fails)} check(s) failed")
print("all checks passed")
