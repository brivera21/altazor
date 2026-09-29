"""Checks universe.html against its data, its model and its drawing.

  the data     the density parameters make a flat universe and match Planck;
               the baryon and galaxy bars still sum to their censuses
  the model    the page's own arithmetic reproduces the present-day budget,
               the age of the universe, and the two crossovers
  the drawing  the curves cross where the arithmetic says they do, the time
               control moves the bar, and the two censuses fade off the present
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_universe import TOP, BARYONS, GALAXY, OMEGA, H0

ROOT = Path(__file__).resolve().parent.parent
fails = []


def check(ok, msg):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}")
    if not ok:
        fails.append(msg)


print("--- the data ---")
check(abs(sum(OMEGA.values()) - 1.0) < 1e-12,
      f"the density parameters sum to {sum(OMEGA.values()):.12f}, a flat universe")
check(abs(OMEGA["de"] - 0.685) < 0.002, f"dark energy {OMEGA['de']:.4f} against Planck's 0.685")
check(abs(OMEGA["dm"] + OMEGA["ob"] - 0.315) < 0.002,
      f"matter {OMEGA['dm'] + OMEGA['ob']:.4f} against Planck's 0.315")
check(abs(OMEGA["ob"] - 0.0493) < 0.001, f"ordinary matter {OMEGA['ob']:.4f} against Planck's 0.0493")
check(abs(OMEGA["rad"] - 9.15e-5) < 5e-6,
      f"radiation {OMEGA['rad']:.3e}, photons plus three massless neutrino species")
check(abs(H0 - 67.4) < 0.1, f"Hubble constant {H0} km/s/Mpc")
exps = {k: n for k, _l, n, *_r in TOP}
check(exps == {"rad": 4, "dm": 3, "ob": 3, "de": 0},
      f"the dilution exponents are {exps}")
check([d[0] for d in TOP] == ["rad", "dm", "ob", "de"],
      "the top bar reads left to right in the order the components came to rule")
b = sum(p for _k, _l, p, *_r in BARYONS)
check(abs(b - 99.7) < 0.5, f"the baryon census sums to {b}")
check(BARYONS[-1][0] == "gal", "galaxies sit at the right end of the baryon bar")
g = sum(p for _k, _l, p, *_r in GALAXY)
check(abs(g - 99.9) < 0.5, f"the galaxy budget sums to {g}")
s = (ROOT / "universe.html").read_text(encoding="utf-8")
for frag in ["10.1051/0004-6361/201833910", "10.1088/0004-637X/759/1/23",
             "10.1038/s41586-020-2300-2", "fast radio bursts"]:
    check(frag in s, f"the page carries '{frag}'")

# what the arithmetic should give, worked here independently of the page
OM_M = OMEGA["dm"] + OMEGA["ob"]
A_RM = OMEGA["rad"] / OM_M
A_ML = (OM_M / OMEGA["de"]) ** (1 / 3)


def erel(a):
    return math.sqrt(OMEGA["rad"] * a ** -4 + OM_M * a ** -3 + OMEGA["de"])


def age(a, n=4000):
    lo, hi = math.log(1e-14), math.log(a)
    h = (hi - lo) / n
    tot = sum((1 / erel(math.exp(lo + i * h))) *
              (1 if i in (0, n) else (4 if i % 2 else 2)) for i in range(n + 1))
    # 1/H0 in billions of years for H0 in km/s/Mpc
    return tot * h / 3 * (3.0856775814913673e19 / H0) / 3.1557e16


print("--- the model, as the page computes it ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1280, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((ROOT / "universe.html").as_uri())
    pg.wait_for_selector("#uvsvg")

    now = pg.evaluate("()=>shares(1)")
    for k, want in [("de", 68.49), ("dm", 26.57), ("ob", 4.93), ("rad", 0.00915)]:
        check(abs(now[k] - want) < max(0.02, want * 0.01),
              f"today the page puts {k} at {now[k]:.5f}%, wanted about {want}")
    check(abs(sum(now.values()) - 100) < 1e-9,
          f"the four shares sum to {sum(now.values()):.10f}")

    t0 = pg.evaluate("()=>age(1)")
    check(abs(t0 - age(1)) < 0.02 and abs(t0 - 13.79) < 0.05,
          f"the page's age of the universe is {t0:.3f} billion years "
          f"against {age(1):.3f} worked here and 13.797 from Planck")
    # a young universe: 380,000 years at the release of the background
    trec = pg.evaluate("()=>age(1/1091)")
    check(0.00030 < trec < 0.00046,
          f"at redshift 1090 the page gives an age of {trec * 1e9:,.0f} years, "
          "against the 380,000 of the literature")

    arm, aml = pg.evaluate("()=>[A_RM,A_ML]")
    check(abs(arm - A_RM) / A_RM < 1e-9,
          f"radiation equals matter at a scale factor of {arm:.6e}, "
          f"a redshift of {1 / arm - 1:,.0f}")
    check(abs(aml - A_ML) / A_ML < 1e-9,
          f"matter equals dark energy at a scale factor of {aml:.5f}, "
          f"a redshift of {1 / aml - 1:.3f}")
    at = pg.evaluate("(a)=>shares(a)", arm)
    check(abs(at["rad"] - (at["dm"] + at["ob"])) < 1e-6,
          f"at that first crossover radiation is {at['rad']:.4f}% and matter "
          f"{at['dm'] + at['ob']:.4f}%")
    at = pg.evaluate("(a)=>shares(a)", aml)
    check(abs(at["de"] - (at["dm"] + at["ob"])) < 1e-6,
          f"at the second crossover dark energy is {at['de']:.4f}% and matter "
          f"{at['dm'] + at['ob']:.4f}%")
    early = pg.evaluate("()=>shares(1e-6)")
    # Omega_r a^-4 = 9.15e19 against Omega_m a^-3 = 3.15e17, so matter is
    # already a third of a percent at the left edge of the drawing
    check(99.6 < early["rad"] < 99.7,
          f"at the earliest moment drawn radiation holds {early['rad']:.4f}%")
    late = pg.evaluate("()=>shares(10)")
    check(late["de"] > 99.8,
          f"ten times this size, dark energy holds {late['de']:.3f}%")
    # matter never outranks dark matter's fixed companion: the ratio is frozen
    r1 = pg.evaluate("()=>{const s=shares(1e-4);return s.dm/s.ob}")
    r2 = pg.evaluate("()=>{const s=shares(5);return s.dm/s.ob}")
    check(abs(r1 - r2) < 1e-9,
          f"dark and ordinary matter keep one ratio at every moment ({r1:.4f})")

    print("--- the drawing ---")
    n = pg.evaluate("()=>document.querySelectorAll('#uvsvg g[data-k]').length")
    check(n >= 13, f"{n} interactive segments, curves and labels")

    # read the crossover straight off the two polylines, in pixels
    cross = pg.evaluate("""()=>{
      const g=[...document.querySelectorAll('#uvsvg g[data-k]')];
      const pts=k=>{const el=[...document.querySelectorAll('#uvsvg polyline')]
        .find(p=>p.parentNode.getAttribute('data-k')===k&&p.getAttribute('stroke')!=='transparent');
        return el.getAttribute('points').trim().split(/\\s+/).map(s=>s.split(',').map(Number));};
      const r=pts('rad'), m=pts('dm');
      for(let i=1;i<r.length;i++){
        const d0=r[i-1][1]-m[i-1][1], d1=r[i][1]-m[i][1];
        if(d0===0||d0*d1<0){
          const f=d0/(d0-d1);
          return XC(r[i-1][0]+f*(r[i][0]-r[i-1][0]));
        }
      }
      return null;}""")
    want = math.log10(A_RM)
    check(cross is not None and abs(cross - want) < 0.01,
          f"the drawn curves cross at log a = {cross:.4f} against {want:.4f}")

    # the time control moves the top bar
    w0 = pg.evaluate("()=>+document.querySelector('#uvsvg g[data-k=rad] rect').getAttribute('width')")
    pg.evaluate("()=>setLa(-6)")
    w1 = pg.evaluate("()=>+document.querySelector('#uvsvg g[data-k=rad] rect').getAttribute('width')")
    check(w0 < 2 and w1 > 900,
          f"the radiation segment grows from {w0:.2f}px today to {w1:.0f}px at the start")
    ob = pg.evaluate("()=>+document.querySelector('#uvsvg g[data-k=ob] rect').getAttribute('width')")
    check(ob < 1.5, f"and ordinary matter shrinks to a hairline ({ob:.2f}px)")

    rd = pg.evaluate("()=>['rdA','rdZ','rdT','rdAge'].map(i=>document.getElementById(i).textContent)")
    check(all(rd) and rd[0].startswith("1.00×10⁻⁶") and "1.00×10⁶" in rd[1]
          and "2.73×10⁶ K" == rd[2] and rd[3].endswith("days"),
          f"the readouts follow, with no mantissa left above ten: {rd}")
    pg.evaluate("()=>setLa(Math.log10(1/1091))")
    tcmb = pg.evaluate("()=>document.getElementById('rdT').textContent")
    check(tcmb.replace(",", "").split()[0].isdigit()
          and 2900 < float(tcmb.replace(",", "").split()[0]) < 3050,
          f"at the release of the background the page reads {tcmb}, "
          "against the roughly 3000 K of the literature")

    # the two censuses are measurements of today, and say so by fading
    dim = pg.evaluate("""()=>{const g=[...document.querySelectorAll('#uvsvg > g')]
      .find(x=>x.querySelector('g[data-k=miss]'));return g?+g.getAttribute('opacity'):-1}""")
    check(0 < dim < 0.5, f"off the present the baryon census fades to {dim}")
    pg.evaluate("()=>setLa(0)")
    dim = pg.evaluate("""()=>{const g=[...document.querySelectorAll('#uvsvg > g')]
      .find(x=>x.querySelector('g[data-k=miss]'));return g?+g.getAttribute('opacity'):-1}""")
    check(dim == 1, f"and returns to full at the present ({dim})")

    # the buttons
    btns = pg.evaluate("()=>[...document.querySelectorAll('#presets button')].map(b=>b.textContent)")
    check(len(btns) == 7, f"{len(btns)} moments offered: {btns}")
    pg.click("#presets button:nth-child(2)")
    la = pg.evaluate("()=>la")
    check(abs(la - math.log10(A_RM)) < 1e-9,
          f"the equality button lands on log a = {la:.5f}")
    pressed = pg.evaluate("()=>document.querySelector('#presets button[aria-pressed=true]').textContent")
    check(pressed == btns[1], f"and marks itself: '{pressed}'")

    # the slider and the marker
    pg.evaluate("""()=>{const s=document.getElementById('scale');
      s.value=-300;s.dispatchEvent(new Event('input'));}""")
    check(abs(pg.evaluate("()=>la") + 3) < 1e-9, "the slider sets the moment")
    mx = pg.evaluate("""()=>{const l=[...document.querySelectorAll('#uvsvg line')]
      .find(e=>e.getAttribute('stroke')==='#f4efe2');return l?+l.getAttribute('x1'):-1}""")
    check(abs(mx - pg.evaluate("()=>CX(-3)")) < 0.5,
          f"and the marker follows it to x={mx:.1f}")

    # the cards still answer
    card = pg.evaluate("()=>{show('miss');return document.getElementById('pct').textContent"
                       "+' '+document.getElementById('segTxt').textContent}")
    check(card.startswith("29%"), f"the missing-baryons card answers: '{card}'")
    gcard = pg.evaluate("()=>{show('stars');return document.getElementById('pct').textContent"
                        "+' | '+document.getElementById('srcTxt').textContent}")
    check(gcard.startswith("65%") and "galaxy" in gcard,
          f"the living-stars card answers: '{gcard[:70]}'")
    pg.evaluate("()=>{setLa(0);show('de')}")
    dcard = pg.evaluate("()=>document.getElementById('pct').textContent+' | '"
                        "+document.getElementById('atTxt').textContent")
    check(dcard.startswith("68.5%") and "today" in dcard,
          f"the dark energy card reads '{dcard}'")
    pg.evaluate("()=>{setLa(-4);show('de')}")
    dcard = pg.evaluate("()=>document.getElementById('pct').textContent+' | '"
                        "+document.getElementById('atTxt').textContent")
    check("Today it is 68.5%" in dcard,
          f"and off the present it gives both the moment and today: '{dcard}'")

    smbh = pg.evaluate("()=>{const r=document.querySelector('g[data-k=smbh] rect');"
                       "return r?+r.getAttribute('width'):-1}")
    check(0 < smbh < 3, f"Sgr A* drawn as a hairline ({smbh}px)")
    print("--- the controls ---")
    pg.evaluate("()=>{setLa(0);}")
    pg.click("#play")
    pg.wait_for_timeout(1500)
    s1 = pg.evaluate("()=>[la, !!playing, document.getElementById('play').textContent]")
    check(s1[1] and s1[2] == "Pause" and -6 < s1[0] < -4, f"Play starts from the earliest moment and reads Pause (log a = {s1[0]:.2f})")
    pg.click("#play")
    s2 = pg.evaluate("()=>[la, !!playing, document.getElementById('play').textContent]")
    check(not s2[1] and s2[2] == "Play", "a second press stops it")
    pg.evaluate("()=>{setLa(-5.5)}")
    pg.click("#play")
    pg.wait_for_timeout(6600)
    s3 = pg.evaluate("()=>[la, !!playing]")
    check(s3[0] == 0 and not s3[1], f"left to run it stops at today ({s3})")
    # the curves slide to a view against age
    pg.click('#axis button[data-ax="1"]')
    pg.wait_for_timeout(1300)
    ax = pg.evaluate("""()=>{const mk=[...document.querySelectorAll('#uvsvg line')].find(e=>e.getAttribute('stroke')==='#f4efe2');
      return {m, x:+mk.getAttribute('x1'), want:XA(age(1)), agemax:AGEMAX}}""")
    check(ax["m"] == 1 and abs(ax["x"] - ax["want"]) < 0.5, f"against age the marker for today stands at 13.79 of {ax['agemax']:.1f} billion years")
    back = pg.evaluate("()=>{const r=document.getElementById('uvsvg').getBoundingClientRect(); return XM(XA(age(Math.pow(10,-0.3))))}")
    check(abs(back + 0.3) < 0.01, f"and a point on the drawing reads back to its moment ({back:.3f})")
    pg.click('#axis button[data-ax="0"]')
    pg.wait_for_timeout(1300)
    check(pg.evaluate("()=>m") == 0, "and back against size")
    # the sliver folds the bars below, and opens them again
    h0 = pg.evaluate("()=>document.getElementById('uvsvg').viewBox.baseVal.height")
    pg.click("#uvsvg g[data-k=ob] rect")
    pg.wait_for_timeout(900)
    h1 = pg.evaluate("()=>[openB, document.getElementById('uvsvg').viewBox.baseVal.height, !!document.querySelector('#uvsvg g[data-k=miss]')]")
    check(h1[0] == 0 and h1[1] < h0 - 500 and not h1[2], f"a click on the amber sliver folds the census away ({h0:.0f} to {h1[1]:.0f})")
    pg.click("#uvsvg g[data-k=ob] rect")
    pg.wait_for_timeout(900)
    check(pg.evaluate("()=>openB") == 1, "a second click opens it again")
    pg.click("#uvsvg g[data-k=gal] rect")
    pg.wait_for_timeout(900)
    check(pg.evaluate("()=>[openG, !!document.querySelector('#uvsvg g[data-k=stars]')]") == [0, False], "the galaxies segment folds the Milky Way bar")
    pg.click("#uvsvg g[data-k=gal] rect")
    pg.wait_for_timeout(900)
    # the arrow keys step a decade on the slider, a tenth with shift
    pg.evaluate("()=>setLa(0)")
    pg.focus("#scale")
    pg.keyboard.press("ArrowLeft"); pg.keyboard.press("ArrowLeft")
    k1 = pg.evaluate("()=>la")
    pg.keyboard.press("Shift+ArrowRight")
    k2 = pg.evaluate("()=>la")
    check(abs(k1 + 2) < 1e-9 and abs(k2 + 1.9) < 1e-9, f"the arrows step whole decades ({k1}) and a tenth with shift ({k2:.2f})")
    # crossing leaders: the names under each bar keep the order of their segments
    order = pg.evaluate("""()=>[...document.querySelectorAll('#uvsvg path.lead')]
      .map(p=>p.getAttribute('d').replace(/[ML]/g,'').trim().split(/ +/).map(q=>q.split(',').map(Number)))""")
    rows = {}
    for pts in order:
        rows.setdefault(round(pts[0][1]), []).append((pts[0][0], pts[2][0]))
    ok = all(all(a[1] <= b[1] for a, b in zip(sorted(r), sorted(r)[1:])) for r in rows.values())
    check(ok, f"the leaders under the bars never cross ({sum(len(r) for r in rows.values())} names)")
    check(pg.evaluate("()=>{const d=document.querySelector('details.sources'); return !!d && !d.open && d.querySelectorAll('.refs p').length===10}"),
          "one caption shows; the notes, method and ten references sit in a closed Sources details")
    ph = br.new_page(viewport={"width": 390, "height": 844})
    ph.goto((ROOT / "universe.html").as_uri()); ph.wait_for_selector("#uvsvg")
    o = ph.evaluate("()=>({ov:document.documentElement.scrollWidth-innerWidth, w:document.getElementById('uvsvg').getBoundingClientRect().width, card:document.querySelector('.card').getBoundingClientRect().top, svg:document.getElementById('uvsvg').getBoundingClientRect().top})")
    check(o["ov"] == 0 and o["w"] >= 660 and o["card"] < o["svg"], f"at 390 px the drawing is {o['w']:.0f} px wide in a sideways scroll, nothing overflows, the card sits above it")
    check(not errs, f"no script errors ({errs})")
    br.close()

print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("everything squares")
