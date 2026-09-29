"""Check cell.html against its data and its drawing.

  the data     three cells with sizes; every part named, sized, counted and
               sourced; the volume ratios the notes claim hold
  the drawing  the shared view keeps one scale, cell to cell and to the bar;
               each zoomed view draws every part of its cell once; the parts
               answer; the ribosome in the bacterium is drawn at its size
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cell_data import CELLS, PARTS, EXTRAS

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "cell.html"
fails = []


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


print("--- the data ---")
by = {c[0]: c for c in CELLS}
check(set(by) == {"animal", "plant", "bacterium"}, "three cells")
check(all(p[1] in by and p[2] and p[3] and p[6] and p[7] for p in PARTS),
      f"{len(PARTS)} parts, each on a cell, sized, described and sourced")
va = 4 / 3 * math.pi * (by["animal"][2] / 2) ** 3
vb = math.pi * (by["bacterium"][3] / 2) ** 2 * (by["bacterium"][2] - by["bacterium"][3]) + 4 / 3 * math.pi * (by["bacterium"][3] / 2) ** 3
vp = by["plant"][2] * by["plant"][3] * by["plant"][3]
check(1500 < va / vb < 2500, f"the bacterium has about a two thousandth of the animal cell's volume ({va / vb:.0f})")
check(8 < vp / va < 10, f"the plant cell about nine times it ({vp / va:.1f})")
check(any("2 meters" in p[6] or "two meters" in p[6].lower() for p in PARTS if p[1] == "animal"),
      "the animal nucleus carries two meters of DNA")
check(any("1.6 millimeters" in p[6] for p in PARTS if p[1] == "bacterium"),
      "the bacterium's loop is 1.6 millimeters, 4.6 million bases at 0.34 nm")
check(abs(4.6e6 * 0.34e-9 - 1.6e-3) < 0.05e-3, "which is what 4.6 million bases at 0.34 nm come to")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1000}, reduced_motion="reduce")
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#csvg")

    def view(v):
        pg.click(f'#views button[data-v="{v}"]')
        pg.wait_for_timeout(150)
        return pg.evaluate("()=>window.__cell()")

    st = view("all")
    check(set(st["keys"]) >= {"animal", "plant", "bacterium", "rbc", "yeast", "egg", "virus"}, f"the shared view carries {st['keys']}")
    g = pg.evaluate("""()=>{const q=s=>document.querySelector(s);
      const a=q('#csvg g[data-k="animal"] circle'), p=q('#csvg g[data-k="plant"] rect'), b=q('#csvg g[data-k="bacterium"] rect'),
        r=q('#csvg g[data-k="rbc"] circle'), e=q('#csvg g[data-k="egg"] circle'), bar=[...document.querySelectorAll('#csvg line')].find(l=>l.getAttribute('stroke')==='#9a9a9a');
      return {a:+a.getAttribute('r')*2, p:[+p.getAttribute('width')-8,+p.getAttribute('height')-8], b:[+b.getAttribute('width'),+b.getAttribute('height')],
        r:+r.getAttribute('r')*2, e:+e.getAttribute('r')*2, bar:+bar.getAttribute('x2')-+bar.getAttribute('x1')};}""")
    k = g["bar"] / 10           # px per micron from the scale bar
    worst = max(abs(g["a"] / k - 15), abs(g["p"][0] / k - 40), abs(g["p"][1] / k - 20), abs(g["b"][0] / k - 2), abs(g["b"][1] / k - 0.8), abs(g["r"] / k - 7.8), abs(g["e"] / k - 120))
    check(worst < 0.05, f"everything in the shared view is on the scale bar's scale, {k:.0f} px a micron (worst {worst:.3f} microns out)")
    check(g["e"] / g["b"][0] > 50, f"the egg's edge is drawn {g['e'] / g['b'][0]:.0f} bacteria long")

    for v in ("animal", "plant", "bacterium"):
        st = view(v)
        want = {p[0] for p in PARTS if p[1] == v}
        check(set(st["keys"]) == want, f"the {v} view draws every part of that cell once: {len(want)} parts",
              str(set(st["keys"]) ^ want))
        pg.evaluate("(k)=>document.querySelector('#csvg [data-k=\"'+k+'\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))", sorted(want)[0])
        pg.wait_for_timeout(80)
        name = pg.evaluate("()=>document.getElementById('nameTxt').textContent")
        check(name == next(p[2] for p in PARTS if p[0] == sorted(want)[0]), f"and a part under the cursor answers: '{name}'")

    # the bacterium's ribosomes are drawn at about 20 nm on that view's scale
    view("bacterium")
    rr = pg.evaluate("""()=>{const bar=[...document.querySelectorAll('#csvg line')].find(l=>l.getAttribute('stroke')==='#9a9a9a');
      const k=(+bar.getAttribute('x2')-+bar.getAttribute('x1'))/0.5; const c=document.querySelector('#csvg g[data-k="b_ribo"] circle');
      return {nm:+c.getAttribute('r')*2/k*1000, n:document.querySelectorAll('#csvg g[data-k="b_ribo"] circle').length};}""")
    check(15 < rr["nm"] < 30, f"each drawn ribosome is {rr['nm']:.0f} nm across on the bacterium's scale, {rr['n']} of them in the section")
    # the animal cell's nucleus is about six microns on that view's scale
    view("animal")
    nuc = pg.evaluate("""()=>{const bar=[...document.querySelectorAll('#csvg line')].find(l=>l.getAttribute('stroke')==='#9a9a9a');
      const k=(+bar.getAttribute('x2')-+bar.getAttribute('x1'))/5; const c=document.querySelector('#csvg g[data-k="a_nucleus"] circle');
      const m=document.querySelector('#csvg g[data-k="a_membrane"] circle'); return {nuc:+c.getAttribute('r')*2/k, cell:+m.getAttribute('r')*2/k};}""")
    check(abs(nuc["cell"] - 15) < 0.01 and 5.5 < nuc["nuc"] < 6.5, f"the animal cell is {nuc['cell']:.1f} microns and its nucleus {nuc['nuc']:.1f}")
    # a click on a cell in the shared view opens it
    view("all")
    pg.evaluate("()=>document.querySelector('#csvg g[data-k=\"bacterium\"] rect').dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    pg.wait_for_timeout(120)
    check(pg.evaluate("()=>window.__cell().view") == "bacterium", "a click on the bacterium in the shared view opens it")

    # the ghosts: E. coli beside the animal cell at that view's scale, an animal cell over the plant cell
    view("animal")
    gc = pg.evaluate("""()=>{const bar=[...document.querySelectorAll('#csvg line')].find(l=>l.getAttribute('stroke')==='#9a9a9a');
      const k=(+bar.getAttribute('x2')-+bar.getAttribute('x1'))/5; const r=document.querySelector('#csvg g[data-g="g_coli"] rect');
      return [+r.getAttribute('width')/k, +r.getAttribute('height')/k];}""")
    check(abs(gc[0] - 2) < 0.01 and abs(gc[1] - 0.8) < 0.01, f"a ghost E. coli beside the animal cell is {gc[0]:.1f} by {gc[1]:.1f} microns on its scale")
    pg.evaluate("()=>document.querySelector('#csvg g[data-g=\"g_coli\"] rect').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    check("two thousand" in pg.evaluate("()=>document.getElementById('numTxt').textContent"), "and its card says about two thousand fill the animal cell")
    view("plant")
    ga = pg.evaluate("""()=>{const bar=[...document.querySelectorAll('#csvg line')].find(l=>l.getAttribute('stroke')==='#9a9a9a');
      const k=(+bar.getAttribute('x2')-+bar.getAttribute('x1'))/10; return +document.querySelector('#csvg g[data-g="g_animal"] circle').getAttribute('r')*2/k;}""")
    check(abs(ga - 15) < 0.01, f"a ghost animal cell over the plant cell is {ga:.1f} microns on its scale")
    check("g_animal" in pg.evaluate("()=>window.__cell().ghosts") and view("bacterium") and "g_animal" in pg.evaluate("()=>window.__cell().ghosts"),
          "and the animal cell's edge crosses the bacterium's view")

    # true thickness: the membrane goes to 7 nm on the animal view's scale
    view("animal")
    check(not pg.evaluate("()=>document.getElementById('thinBtn').hidden"), "the true-thickness toggle shows on the animal view")
    pg.click("#thinBtn"); pg.wait_for_timeout(80)
    th = pg.evaluate("""()=>{const bar=[...document.querySelectorAll('#csvg line')].find(l=>l.getAttribute('stroke')==='#9a9a9a');
      const k=(+bar.getAttribute('x2')-+bar.getAttribute('x1'))/5; const m=document.querySelector('#csvg g[data-k="a_membrane"] circle');
      const r=document.querySelector('#csvg g[data-k="a_ribo"] circle'); return {mem:+m.getAttribute('stroke-width')/k*1000, ribo:+r.getAttribute('r')*2/k*1000};}""")
    check(abs(th["mem"] - 7) < 0.2 and abs(th["ribo"] - 25) < 0.5, f"at true thickness the membrane is {th['mem']:.1f} nm and a ribosome {th['ribo']:.0f} nm")
    pg.click("#thinBtn"); pg.wait_for_timeout(80)
    check(pg.evaluate("()=>window.__cell().thin") == 0, "and the toggle off restores the drawn thickness")
    view("bacterium")
    check(pg.evaluate("()=>document.getElementById('thinBtn').hidden"), "the bacterium, already drawn at true size, has no toggle")

    # stepping: the button and the arrow keys walk the parts and fill the card
    view("animal")
    pg.click("#stepBtn"); first = pg.evaluate("()=>window.__cell().hot")
    pg.focus("#diagram"); pg.keyboard.press("ArrowRight"); second = pg.evaluate("()=>window.__cell().hot")
    pg.keyboard.press("ArrowLeft"); back = pg.evaluate("()=>window.__cell().hot")
    want = [p[0] for p in PARTS if p[1] == "animal"]
    check(first == want[0] and second == want[1] and back == want[0]
          and pg.evaluate("()=>document.getElementById('nameTxt').textContent") == PARTS[0][2],
          f"the step button and the arrow keys walk the parts in turn: {first}, {second}, {back}")

    # the page opens on the diagram; the notes and references sit in a closed Sources
    check(pg.evaluate("()=>{const d=document.querySelector('details.sources'); return !!d && !d.open && !!d.querySelector('.refs') && !!d.querySelector('.method');}"),
          "the method and references sit inside a closed Sources")
    check(len(pg.evaluate("()=>[...document.querySelectorAll('.wrap > p.note')].map(p=>p.textContent.split(/\\s+/).length)")) == 1,
          "one caption paragraph outside it")
    check(not errs, "no script errors", "; ".join(errs))

    # the zoom, animated: a click on the bacterium closes the viewBox on it and hands over to its view
    pz = br.new_page(viewport={"width": 1300, "height": 850})
    pz.on("pageerror", lambda e: errs.append(str(e)))
    pz.goto(PAGE.as_uri()); pz.wait_for_selector("#csvg")
    pz.evaluate("()=>document.querySelector('#csvg g[data-k=\"bacterium\"] rect').dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    pz.wait_for_timeout(500)
    mid = pz.evaluate("()=>window.__cell()")
    pz.wait_for_timeout(1100)
    end = pz.evaluate("()=>window.__cell()")
    check(mid["zooming"] and mid["view"] == "all" and 37 < mid["vb"][2] < 980 and end["view"] == "bacterium" and end["vb"][2] == 980,
          f"the zoom tweens the viewBox width from 980 to {980 * 11 / 290:.0f} and hands over to the bacterium (mid {mid['vb'][2]:.0f})")
    pz.click('#views button[data-v="all"]'); pz.wait_for_timeout(1500)
    check(pz.evaluate("()=>window.__cell().view") == "all" and pz.evaluate("()=>window.__cell().vb[2]") == 980, "and Together zooms back out")
    pz.set_viewport_size({"width": 390, "height": 844}); pz.wait_for_timeout(150)
    over = pz.evaluate("()=>document.documentElement.scrollWidth - innerWidth")
    check(over == 0, "nothing overflows a 390px screen", str(over))
    check(not errs, "no script errors while zooming", "; ".join(errs))
    br.close()

print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("everything squares")
