"""Check galaxies.html against its data and against its drawing.

  the data     eleven classes on the fork in Hubble's order; thirteen galaxies
               to scale with the published diameters; the Milky Way's parts
               with their figures; the Local Group members at McConnachie's
               distances
  the drawing  each view renders and answers; sizes are in the ratio of the
               diameters; the Sun is at 8.2 of the Milky Way's 13.4 kpc; the
               arms cross the Sun's line at their measured radii; the map is
               handed the way the north galactic pole sees it
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from galaxies_data import KINDS, SIZES, PARTS, NEIGHBORS, SUN_R

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "galaxies.html"
fails = []


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


print("--- the data ---")
check([k["k"] for k in KINDS] == ["E0", "E3", "E7", "S0", "Sa", "Sb", "Sc", "SBa", "SBb", "SBc", "Irr"],
      "the eleven classes run in Hubble's order along the fork")
check(all(k["def"] and k["ex"] and k["mw"] and k["b"] and k["s"] for k in KINDS),
      "every class is defined, has examples, says where the Milky Way stands, and is sourced")
# the published diameters, entered again here
D = {"mw": 26.8, "m31": 46.6, "m33": 18.7, "lmc": 9.9, "smc": 5.8, "m87": 40.6,
     "ic1101": 123.7, "ngc1300": 33.6, "m104": 15.0, "m51": 23.6, "cena": 18.4, "m101": 51.8, "sgr": 3.0}
bykey = {g["k"]: g for g in SIZES}
check(set(D) == set(bykey), f"{len(SIZES)} galaxies to scale, the Milky Way among them")
check(all(abs(bykey[k]["d"] - d) < 1e-9 for k, d in D.items()), "every diameter matches the figure entered here")
check(bykey["mw"]["c"] == "MW" and "SBbc" in bykey["mw"]["t"], "the Milky Way is drawn as a barred spiral and called SBbc")
check(abs(SUN_R - 8.2) < 1e-9, f"the Sun's distance to the center is {SUN_R} kpc")
arms = [p for p in PARTS if p.get("arm")]
check(len(arms) == 4 and all(3 < a["rSun"] < 15 and 8 < a["pitch"] < 18 for a in arms),
      "four arms, each with a pitch angle and the radius where it crosses the Sun's line")
rs = sorted(a["rSun"] for a in arms)
check(rs[1] < SUN_R < rs[2], f"the Sun sits between two of them ({rs[1]} and {rs[2]} kpc)")
thin = next(p for p in PARTS if p["k"] == "thin")
thick = next(p for p in PARTS if p["k"] == "thick")
check(thin["h"] == 0.3 and thick["h"] == 0.9, "thin disc 300 pc, thick disc 900 pc")
# McConnachie 2012, a sample entered again here
MC = {"lmc": 50, "smc": 62, "sgr": 26, "for": 147, "leo1": 254, "m31": 765, "m33": 840, "wlm": 930}
nb = {g["k"]: g for g in NEIGHBORS}
check(all(nb[k]["d"] == d for k, d in MC.items()), "the Local Group distances match McConnachie for the sample")
check(all(-90 <= g["lat"] <= 90 and 0 <= g["l"] < 360 for g in NEIGHBORS), "every member has a galactic longitude and latitude")
check(all(g["b"] and g["sizeTxt"] and g["group"] for g in NEIGHBORS), "and a size, a group and a line of its own")

print("--- the drawing ---")
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#gsvg")

    def hover(sel):
        # the pointer event itself, on the element: a bounding box center would
        # land on whatever sits under the middle of an arm's arc
        pg.evaluate("(s)=>document.querySelector(s).dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))", sel)
        pg.wait_for_timeout(120)

    def view(v):
        pg.click(f'#views button[data-v="{v}"]')
        pg.wait_for_timeout(150)
        return pg.evaluate("()=>window.__gal()")

    st = view("kinds")
    check(st["marks"] == 13, f"the fork carries eleven classes, the Milky Way's marker and the galaxy that slides along it ({st['marks']} marks)")
    card = pg.evaluate("()=>document.getElementById('nameTxt').textContent+' | '+document.getElementById('numTxt').textContent")
    check("SBbc" in card and "between b and c" in card, f"and opens on the Milky Way's place: '{card[:60]}'")
    hover('#gsvg g[data-k="Sb"]')
    card = pg.evaluate("()=>document.getElementById('nameTxt').textContent+' | '+document.getElementById('numTxt').textContent")
    check("Sb" in card and "Andromeda" in card, f"Sb names Andromeda as its example: '{card[:70]}'")

    st = view("sizes")
    check(st["marks"] == 13, "thirteen galaxies drawn to scale")
    rx = pg.evaluate("""()=>{const r=k=>+document.querySelector('#gsvg g[data-k="'+k+'"] ellipse').getAttribute('rx');
      return {mw:r('mw'), m31:r('m31'), ic:r('ic1101'), smc:r('smc')};}""")
    check(abs(rx["m31"] / rx["mw"] - 46.6 / 26.8) < 0.01,
          f"Andromeda is drawn {rx['m31'] / rx['mw']:.3f} times the Milky Way, as the diameters say")
    check(abs(rx["ic"] / rx["smc"] - 123.7 / 5.8) < 0.05,
          f"and IC 1101 {rx['ic'] / rx['smc']:.1f} times the Small Cloud")
    sun = pg.evaluate("""()=>{const g=document.querySelector('#gsvg g[data-k="mw"]');
      const e=g.querySelector('ellipse'), c=[...g.querySelectorAll('circle')].find(c=>c.getAttribute('fill')==='#ffb02e');
      const m=g.querySelector('g').getAttribute('transform').match(/translate\\(([-\\d.]+),([-\\d.]+)\\)/);
      return {R:+e.getAttribute('rx'), dy:+c.getAttribute('cy')-(+m[2]), q:+e.getAttribute('ry')/+e.getAttribute('rx')};}""")
    check(abs(sun["dy"] / (sun["R"] * sun["q"]) - SUN_R / 13.4) < 0.02,
          f"the Sun sits {sun['dy'] / (sun['R'] * sun['q']):.3f} of the way out, against 8.2 of 13.4 kpc")
    bottom = pg.evaluate("()=>Math.max(...[...document.querySelectorAll('#gsvg text')].map(t=>+t.getAttribute('y')))")
    check(bottom <= 720, f"everything fits the stage (lowest label at y={bottom:.0f})")

    st = view("ours")
    check(st["side"] == "face" and st["marks"] >= 9, "the Milky Way opens face-on with its parts answering")
    geo = pg.evaluate("""()=>{const c=document.querySelector('#gsvg g[data-k="sgra"] circle');
      const s=[...document.querySelectorAll('#gsvg g[data-k="sun"] circle')].find(x=>x.getAttribute('fill')==='#ffb02e');
      const bar=document.querySelector('#gsvg g[data-k="bar"]').getAttribute('transform');
      const out={cx:+c.getAttribute('cx'), cy:+c.getAttribute('cy'), sx:+s.getAttribute('cx'), sy:+s.getAttribute('cy'), bar};
      out.arms={};
      for(const k of ['perseus','sagcar','sctcen','outer']){
        const pts=document.querySelector('#gsvg g[data-k="'+k+'"] polyline').getAttribute('points').trim().split(/\\s+/).map(p=>p.split(',').map(Number));
        // the point nearest to straight below the center
        let best=null;
        for(const [x,y] of pts){ const ang=Math.atan2(y-out.cy,x-out.cx); const d=Math.abs(ang-Math.PI/2);
          if(!best||d<best.d) best={d, r:Math.hypot(x-out.cx,y-out.cy)}; }
        out.arms[k]=best.r/22;
      }
      return out;}""")
    check(abs(geo["sx"] - geo["cx"]) < 0.5 and abs((geo["sy"] - geo["cy"]) / 22 - SUN_R) < 0.01,
          f"the Sun is drawn {((geo['sy'] - geo['cy']) / 22):.2f} kpc straight below the center")
    worst = max(abs(geo["arms"][a["k"]] - a["rSun"]) for a in arms)
    check(worst < 0.15, f"each arm crosses the Sun's line at its measured radius (worst {worst:.2f} kpc out)")
    check("rotate(118)" in geo["bar"], f"the bar's near end points to positive longitude ({geo['bar']})")
    hover('#gsvg g[data-k="perseus"]')
    card = pg.evaluate("()=>document.getElementById('nameTxt').textContent")
    check("Perseus" in card, f"an arm under the cursor names itself: '{card}'")
    pg.click('#sub button[data-s="edge"]')
    pg.wait_for_timeout(1400)
    ry = pg.evaluate("""()=>({thin:+document.querySelector('#gsvg g[data-k="thin"] ellipse').getAttribute('ry'),
      thick:+document.querySelector('#gsvg g[data-k="thick"] ellipse').getAttribute('ry'),
      rx:+document.querySelector('#gsvg g[data-k="thin"] ellipse').getAttribute('rx'),
      gcs:document.querySelectorAll('#gsvg g[data-k="gcs"] circle').length})""")
    check(abs(ry["rx"] / ry["thin"] - 15 / 0.6) < 0.01,
          f"edge-on, the thin disc is {ry['rx'] / ry['thin']:.0f} times as wide as it is thick, its true proportion")
    check(abs(ry["thick"] / ry["thin"] - 3) < 1e-6 and ry["gcs"] == 150,
          f"the thick disc three times the thin, and {ry['gcs']} globular clusters")

    st = view("near")
    check(st["marks"] == 26, "the Local Group: 25 members and the Milky Way")
    pos = pg.evaluate("""()=>{const c=k=>{const e=document.querySelector('#gsvg g[data-k="'+k+'"] circle');
      return [+e.getAttribute('cx'),+e.getAttribute('cy')];};
      return {mw:c('mw'), m31:c('m31'), lmc:c('lmc'), sgr:c('sgr'), m33:c('m33')};}""")
    check(pos["m31"][0] < pos["mw"][0] and pos["lmc"][0] > pos["mw"][0],
          "from the north pole Andromeda (l=121) lies to the left and the Large Cloud (l=280) to the right")
    check(0 < pos["mw"][0] - pos["sgr"][0] < 6 and pos["sgr"][1] < pos["mw"][1],
          "the Sagittarius dwarf (l=5.6) sits toward the center, a hair left of the l=0 line")
    r = lambda k: math.hypot(pos[k][0] - pos["mw"][0], pos[k][1] - pos["mw"][1])
    want = lambda d, lat: (math.log10(d * math.cos(math.radians(lat))) - math.log10(15)) / (math.log10(1500) - math.log10(15)) * 300
    check(abs(r("m31") - want(765, -21.6)) < 0.5 and abs(r("lmc") - want(50, -32.9)) < 0.5,
          f"radii follow the log scale: Andromeda at {r('m31'):.1f}px, the Large Cloud at {r('lmc'):.1f}px")
    check(r("m33") > r("m31"), "Triangulum plots beyond Andromeda")
    hover('#gsvg g[data-k="m33"]')
    card = pg.evaluate("()=>document.getElementById('nameTxt').textContent+' | '+document.getElementById('numTxt').textContent")
    check("Triangulum" in card and "840 kpc" in card, f"a member under the cursor gives its distance: '{card[:70]}'")

    print("--- the moving parts ---")
    # Kinds: one galaxy slides along the fork
    view("kinds")
    def morph(v):
        pg.evaluate("(v)=>{const m=document.getElementById('morph'); m.value=v; m.dispatchEvent(new Event('input',{bubbles:true}))}", v)
        pg.wait_for_timeout(60)
        return pg.evaluate("""()=>{const g=document.querySelector('#gsvg g[data-k="morph"]'); const e=g.querySelector('ellipse');
          return {cls:g.querySelector('text').textContent, rx:+e.getAttribute('rx'), ry:+e.getAttribute('ry'), sel:window.__gal().sel, name:document.getElementById('nameTxt').textContent}}""")
    e0, e7, sa, sc = morph(0), morph(350 - 1), morph(460), morph(1000)
    check(e0["cls"] == "E0" and abs(e0["ry"] / e0["rx"] - 1) < 1e-6, "at the left end it is a round E0")
    check(e7["cls"] == "E7" and abs(e7["ry"] / e7["rx"] - 0.3) < 0.02, f"and flattens to E7, axis ratio {e7['ry'] / e7['rx']:.2f}")
    check(sa["cls"] == "Sa" and sc["cls"] == "Sc" and sc["sel"] == "Sc", "then opens from Sa to Sc, ringing the nearest class on the fork")
    pg.click('#sub [data-bar]'); pg.wait_for_timeout(60)
    check(pg.evaluate("()=>document.querySelector('#gsvg g[data-k=\"morph\"] text').textContent") == "SBc", "with a bar it reads SBc")
    # Sizes: a ghost Milky Way at the same scale, and every galaxy to one size
    view("sizes")
    hover('#gsvg g[data-k="m31"]')
    ghost = pg.evaluate("""()=>{const c=[...document.querySelectorAll('#gsvg circle')].find(c=>c.getAttribute('stroke-dasharray')==='5 4');
      const mw=+document.querySelector('#gsvg g[data-k="mw"] ellipse').getAttribute('rx'); return c?{r:+c.getAttribute('r'), mw}:null}""")
    check(ghost is not None and abs(ghost["r"] - ghost["mw"]) < 0.2, "over Andromeda a ghost of the Milky Way is drawn at its own size")
    pg.click('#sub [data-same]'); pg.wait_for_timeout(1200)
    rx2 = pg.evaluate("""()=>['mw','m31','ic1101','smc'].map(k=>+document.querySelector('#gsvg g[data-k="'+k+'"] ellipse').getAttribute('rx'))""")
    check(max(rx2) - min(rx2) < 0.01 and pg.evaluate("()=>window.__gal().same") == 1, f"all one size sets every disc to {rx2[0]:.0f} px")
    pg.click('#sub [data-same]'); pg.wait_for_timeout(1200)
    # The Milky Way: an orbit of the Sun
    view("ours")
    pg.click('#sub button[data-s="face"]'); pg.wait_for_timeout(1300)
    pg.click('#sub [data-play]'); pg.wait_for_timeout(2300)
    g1 = pg.evaluate("()=>window.__gal()")
    pg.click('#sub [data-play]')
    g1["orbitT"] = pg.evaluate("()=>window.__gal().orbitT")
    sun = pg.evaluate("""()=>{const c=document.querySelector('#gsvg g[data-k="sgra"] circle'); const s=[...document.querySelectorAll('#gsvg g[data-k="sun"] circle')].find(x=>x.getAttribute('fill')==='#ffb02e');
      return [+s.getAttribute('cx')-(+c.getAttribute('cx')), +s.getAttribute('cy')-(+c.getAttribute('cy'))]}""")
    ang = (math.degrees(math.atan2(sun[1], sun[0])) - 90) % 360
    check(g1["playing"] and 40 < g1["orbitT"] < 80 and abs(math.hypot(*sun) / 22 - SUN_R) < 0.02 and abs(ang - g1["orbitT"] / 230 * 360) < 3,
          f"Play runs the Sun clockwise round its 8.2 kpc orbit: {g1['orbitT']:.0f} million years, {ang:.0f} degrees round")
    check(not pg.evaluate("()=>window.__gal().playing"), "and a second press pauses it")
    pg.evaluate("()=>{const t=document.getElementById('tilt'); t.value=450; t.dispatchEvent(new Event('input',{bubbles:true}))}")
    tr = pg.evaluate("()=>{const g=[...document.querySelectorAll('#gsvg > g')].find(g=>(g.getAttribute('transform')||'').includes('scale(1,')); return g?g.getAttribute('transform'):''}")
    check("rotate(45.00)" in tr and "scale(1,0.7071)" in tr, f"halfway, the disc has turned 45 degrees and tipped to cos 45 ({tr[:60]})")
    # Neighbors: the true radius
    view("near")
    pg.click('#sub [data-r="1"]'); pg.wait_for_timeout(1300)
    pos = pg.evaluate("""()=>{const c=k=>{const e=document.querySelector('#gsvg g[data-k="'+k+'"] circle'); return [+e.getAttribute('cx'),+e.getAttribute('cy')];};
      return {mw:c('mw'), m31:c('m31'), lmc:c('lmc')};}""")
    rr = lambda k: math.hypot(pos[k][0] - pos["mw"][0], pos[k][1] - pos["mw"][1])
    check(abs(rr("m31") - 765 * math.cos(math.radians(-21.6)) / 1500 * 300) < 0.5 and rr("lmc") < 12,
          f"to true scale Andromeda sits {rr('m31'):.0f} px out and the Large Cloud {rr('lmc'):.1f} px, nearly on the Milky Way")
    pg.click('#sub [data-r="0"]'); pg.wait_for_timeout(1300)
    names = pg.evaluate("()=>document.querySelectorAll('#gsvg g[data-k] text').length")
    over = pg.evaluate("""()=>{const t=[...document.querySelectorAll('#gsvg g[data-k] text')].map(e=>e.getBBox()); let n=0;
      for(let i=0;i<t.length;i++) for(let j=i+1;j<t.length;j++){ const a=t[i], b=t[j]; if(a.x<b.x+b.width-1&&b.x<a.x+a.width-1&&a.y<b.y+b.height-2&&b.y<a.y+a.height-2) n++; } return n;}""")
    check(names >= 15 and over == 0, f"on the log radius {names} members carry names, none overlapping")
    check(pg.evaluate("()=>{const d=document.querySelector('details.sources'); return !!d && !d.open && !!d.querySelector('.refs')}"),
          "one caption shows; the notes, method and references sit in a closed Sources details")
    ph = br.new_page(viewport={"width": 390, "height": 844})
    ph.goto(PAGE.as_uri()); ph.wait_for_selector("#gsvg")
    o = ph.evaluate("()=>({ov:document.documentElement.scrollWidth-innerWidth, w:document.getElementById('gsvg').getBoundingClientRect().width, card:document.querySelector('.card').getBoundingClientRect().top, svg:document.getElementById('gsvg').getBoundingClientRect().top})")
    check(o["ov"] == 0 and o["w"] >= 660 and o["card"] < o["svg"], f"at 390 px the stage is {o['w']:.0f} px wide in a sideways scroll, nothing overflows, the card sits above it")
    check(not errs, "no script errors", "; ".join(errs))
    br.close()

print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("everything squares")
