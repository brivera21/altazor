#!/usr/bin/env python3
"""Verify temperature.html against what the page actually draws.

Offline (network cut): five views, each drawing its own thing; the bands
of the span meet with no gap and cover the whole documented range; the
labels are pushed apart rather than piled up; the daily curve is low
before dawn and high in the late afternoon and swings about half a
degree; the sites disagree by more than that; fever chases a moving set
point while hyperthermia climbs past a still one; the four routes out
add to a hundred; and the unit buttons convert a point on the scale and
a gap between two points differently, which is the arithmetic the page
is teaching. No JS errors.

Usage: python3 verify_temperature.py
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
import temperature_data as D                          # noqa: E402

PAGE = Path(__file__).parent.parent / "temperature.html"
fails = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name
          + (f"  [{detail}]" if detail and not ok else ""))
    if not ok:
        fails.append(name)


VIEWS = [("vRange", "range"), ("vDay", "day"), ("vSite", "site"),
         ("vFever", "fever"), ("vHeat", "heat"), ("vFine", "fine"),
         ("vHelp", "help")]

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1400, "height": 1200})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("**/*", lambda r: r.abort()
             if r.request.url.startswith("http") else r.continue_())
    pg.goto(PAGE.as_uri())
    pg.wait_for_timeout(600)

    st = pg.evaluate("window.__temp()")
    check("the page opens on the whole span", st["view"] == "range")
    check("in Celsius", st["unit"] == "C")

    # --- the span
    check("the bands meet with no gap between them", st["zonesJoin"])
    check("and cover everything from the coldest survival to the hottest",
          st["span"][0] <= 11.8 and st["span"][1] >= 46.5, str(st["span"]))
    check("every band is drawn", st["zones"] == len(D.ZONES),
          str(st["zones"]))
    check("and every mark", st["marks"] == len(D.MARKS), str(st["marks"]))
    # the labels are pushed apart, not piled on each other
    ys = pg.evaluate(
        "[...document.querySelectorAll('#tsvg [data-m] text')]"
        ".map(t=>+t.getAttribute('y')).sort((a,b)=>a-b)")
    pairs = [b - a for a, b in zip(ys, ys[1:])]
    check("no two mark labels land on the same line",
          all(d == 0 or d >= 13 for d in pairs), str(sorted(set(pairs))[:5]))
    # and each still points at the temperature it means
    lead = pg.evaluate(
        "(()=>{const g=[...document.querySelectorAll('#tsvg [data-m]')];"
        "return g.map(x=>+x.querySelector('circle').getAttribute('cy'));})()")
    want = pg.evaluate("D.marks.map(m=>yOf(m.t))")
    check("every mark still sits at its own height",
          all(abs(a - b) < 0.6 for a, b in zip(lead, want)))

    # --- the column is a person, not a bar
    check("the span is drawn in the shape of a body",
          pg.evaluate("!!document.querySelector('#tsvg clipPath#bodyClip')"))
    halves = pg.evaluate(
        "document.querySelectorAll('#tsvg clipPath#bodyClip path').length")
    check("built from a half profile and its mirror", halves == 2, str(halves))
    check("the bands are cut to that shape rather than left square",
          pg.evaluate("[...document.querySelectorAll('#tsvg g[clip-path]')]"
                      ".some(g=>g.querySelectorAll('rect').length"
                      ">=D.zones.length)"))
    check("and the outline is stroked with no seam down the middle",
          pg.evaluate("[...document.querySelectorAll('#tsvg path')]"
                      ".filter(p=>p.getAttribute('fill')==='none'"
                      "&&p.getAttribute('stroke')==='#e6e6e6').length") == 2)
    # a person is taller than they are wide, and the head is at the hot end
    box = pg.evaluate(
        "(()=>{const p=document.querySelector('#tsvg clipPath#bodyClip path');"
        "const b=p.getBBox();return [b.x,b.y,b.width,b.height];})()")
    check("the figure is at least three times as tall as half of it is wide",
          box[3] > 3 * box[2], f"{box[3]:.0f} tall, {box[2]:.0f} wide")
    check("it fills the whole scale, feet to head",
          abs(box[1] - 44) < 8 and abs(box[1] + box[3] - 524) < 12,
          f"top {box[1]:.0f}, bottom {box[1]+box[3]:.0f}")
    # the head is narrow and the shoulders are wide, which is how it reads
    hw = pg.evaluate("(()=>{const H=RG.bot-RG.top;"
                     "return {head:0.045*H, sh:0.092*H, hand:0.120*H};})()")
    check("the head is narrower than the shoulders",
          hw["head"] < hw["sh"] < hw["hand"], str(hw))

    # --- a day
    pg.click("#vDay")
    pg.wait_for_timeout(250)
    st = pg.evaluate("window.__temp()")
    check("the day view draws the day", st["view"] == "day")
    check("lowest before dawn, highest in the late afternoon",
          st["dayLow"] < st["dayHigh"],
          f'{st["dayLow"]} vs {st["dayHigh"]}')
    swing = st["dayHigh"] - st["dayLow"]
    check("and the whole swing is about half a degree",
          0.45 <= swing <= 0.55, f"{swing:.2f}")
    lo = pg.evaluate("dayT(D.day.nadir)")
    check("the low lands on the nadir the source gives",
          all(lo <= pg.evaluate(f"dayT({h})") + 1e-9 for h in range(0, 24)),
          str(lo))

    # --- where it is taken
    pg.click("#vSite")
    pg.wait_for_timeout(250)
    check("a row for each site",
          pg.evaluate("document.querySelectorAll('#tsvg [data-s]').length")
          == len(D.SITES))
    spread = pg.evaluate("Math.max(...D.sites.map(s=>s.m))"
                         "-Math.min(...D.sites.map(s=>s.m))")
    check("the sites disagree by more than the daily swing",
          spread > swing, f"{spread:.2f} vs {swing:.2f}")
    check("the rectum reads higher than the armpit",
          pg.evaluate("D.sites.find(s=>s.n==='Rectal').m"
                      ">D.sites.find(s=>s.n==='Axillary').m"))
    check("and the peripheral spread is on the page too",
          pg.evaluate("!!document.querySelector('#tsvg [data-p]')"))

    # --- fever against hyperthermia
    pg.click("#vFever")
    pg.wait_for_timeout(250)
    st = pg.evaluate("window.__temp()")
    check("early in a fever the body is still chasing the set point",
          st["chase"])
    check("in the middle it has caught it", st["caught"])
    check("and at the end it is shedding heat above it", st["shed"])
    check("the four phases are all drawn",
          pg.evaluate("document.querySelectorAll('#tsvg [data-f]').length")
          == len(D.FEVER["phases"]))
    check("hyperthermia climbs past a set point that never moves",
          pg.evaluate("illT(20)>D.ill.base+3 && illT(0)===D.ill.base"))

    # --- heat in and heat out
    pg.click("#vHeat")
    pg.wait_for_timeout(250)
    check("the routes out add to a hundred", st["routeSum"] == 100,
          str(st["routeSum"]))
    check("a bar for each route",
          pg.evaluate("document.querySelectorAll('#tsvg [data-r]').length")
          == len(D.ROUTES))
    check("radiation is the largest at rest",
          pg.evaluate("D.routes[0].n==='Radiation' && "
                      "D.routes.every(r=>r.p<=D.routes[0].p)"))
    check("the sweat ceiling follows from the latent heat",
          abs(pg.evaluate("2*D.power.evap_w_per_lh")
              - 2 * D.POWER["latent"] * 1000 / 3600) < 5)
    check("hard effort makes an order of magnitude more heat than rest",
          pg.evaluate("D.power.hard/D.power.rest>=10"))
    check("and the dry routes reverse above skin temperature",
          pg.evaluate("document.querySelectorAll('#tsvg [data-x]').length")
          == 2)

    # --- degree by degree, and what a degree costs
    pg.click("#vFine")
    pg.wait_for_timeout(280)
    cells = pg.evaluate("document.querySelectorAll('#tsvg [data-c]').length")
    check("the fine scale is hoverable a quarter degree at a time",
          cells == round((43 - 36) / 0.25), str(cells))
    check("and it runs from an ordinary morning to past survival",
          pg.evaluate("FN.lo<=36 && FN.hi>=43"))
    check("both scales are on the ruler at once",
          pg.evaluate("[...document.querySelectorAll('#tsvg text')]"
                      ".some(t=>t.textContent==='97°F')")
          and pg.evaluate("[...document.querySelectorAll('#tsvg text')]"
                          ".some(t=>t.textContent==='37°C')"))
    check("a degree costs about a tenth again of the resting metabolism",
          abs(pg.evaluate("metPct(38)-metPct(37)") - D.COST["met"]) < 0.01)
    check("and the band around it holds the range the studies give",
          pg.evaluate("metPct(40,D.cost.met_lo)<metPct(40)"
                      "&&metPct(40)<metPct(40,D.cost.met_hi)"))
    check("the pulse climbs faster in a child than in an adult",
          pg.evaluate("bpm(41,D.cost.hr_child)>bpm(41)"))
    check("every line that matters is drawn",
          pg.evaluate("document.querySelectorAll('#tsvg [data-L]').length")
          == len(D.LINES))
    check("including the heat stroke line at 40",
          pg.evaluate("D.lines.some(l=>Math.abs(l.t-40)<1e-9)"))

    # --- if someone collapses: the number is not what decides
    pg.click("#vHelp")
    pg.wait_for_timeout(280)
    check("the alert row is split into bands",
          pg.evaluate("document.querySelectorAll('#tsvg [data-b]').length")
          == len(D.FINE))
    check("and the unresponsive row is one block, red the whole way",
          pg.evaluate("document.querySelectorAll('#tsvg [data-u]').length")
          == 1)
    wide = pg.evaluate(
        "(()=>{const r=document.querySelector('#tsvg [data-u] rect');"
        "return +r.getAttribute('width');})()")
    check("it spans the whole scale, not part of it", wide >= 770, str(wide))
    # the cooling clock, and the arithmetic behind every bar
    check("a bar for each way of cooling",
          pg.evaluate("document.querySelectorAll('#tsvg [data-k]').length")
          == len(D.COOLING))
    drop = D.COOL_FROM - D.COOL_TO
    for n, r, _c, _e, _b in D.COOLING:
        mins = drop / r
        inside = mins <= D.COOL_TARGET
        check(f"{n[:34]} takes {round(mins)} minutes, "
              f"{'inside' if inside else 'past'} the target",
              abs(pg.evaluate(f"(D.coolfrom-D.coolto)/{r}") - mins) < 0.01)
    fast = [n for n, r, *_ in D.COOLING if drop / r <= D.COOL_TARGET]
    slow = [n for n, r, *_ in D.COOLING if drop / r > 1.8 * D.COOL_TARGET]
    check("the three active methods clear thirty minutes", len(fast) == 3,
          str(fast))
    check("and ice packs alone take nearly twice as long as the target",
          "Ice packs to the neck, armpits and groin" in slow, str(slow))
    check("immersion clears it in half the time doing nothing would need "
          "just to start",
          drop / D.COOLING[0][1] * 2 < drop / D.COOLING[-1][1])
    check("immersion is the fastest there is",
          pg.evaluate("D.cooling[0].r===Math.max(...D.cooling.map(m=>m.r))"))
    check("and doing nothing is the line the others have to beat",
          pg.evaluate("D.cooling[D.cooling.length-1].r"
                      "===Math.min(...D.cooling.map(m=>m.r))"))
    # the sequence, and the things that must not happen
    check("the bystander steps are all on the page",
          pg.evaluate("document.querySelectorAll('#tsvg [data-a]').length")
          == len(D.ACTIONS))
    steps = pg.evaluate("D.actions.map(a=>a.n)")
    check("and they start with the call and end with what never happens",
          steps[0] == "Call" and steps[-1] == "Never", str(steps))
    txt = pg.evaluate("document.getElementById('tsvg').textContent")
    check("the bathtub warning is on the picture, not just in a card",
          "bathtub" in txt, txt[:80])
    check("telling a fever from heat stroke is on the page too",
          pg.evaluate("document.querySelectorAll('#tsvg [data-t]').length")
          == len(D.TELL))
    check("with the fallback when it cannot be told",
          "the safe reading is heat stroke" in txt)
    # the cards behind the two rows
    pg.evaluate("document.querySelector('[data-u]')"
                ".dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(150)
    card = pg.evaluate("document.querySelector('.card').textContent")
    check("the unresponsive card says the number does not downgrade the call",
          "downgrade" in card, card[:120])
    pg.evaluate("document.querySelector('[data-a=\"4\"]')"
                ".dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(150)
    card = pg.evaluate("document.querySelector('.card').textContent")
    check("and the last step rules out antipyretics and anything by mouth",
          "paracetamol" in card and "mouth" in card, card[:120])

    # --- the units, which are the other half of the lesson
    pg.click("#vRange")
    pg.wait_for_timeout(200)
    for btn, unit, at37, rise in [("#uC", "C", "37.0°C", "1.0°C"),
                                  ("#uF", "F", "98.6°F", "1.8°F"),
                                  ("#uK", "K", "310.15 K", "1.0 K")]:
        pg.click(btn)
        pg.wait_for_timeout(200)
        st = pg.evaluate("window.__temp()")
        d = 2 if unit == "K" else 1
        got = pg.evaluate(f"fmt(37,{d})")
        check(f"a body reads {at37}", got == at37, got)
        check(f"and a rise of one Celsius degree reads {rise}",
              st["rise1"] == rise, st["rise1"])
    pg.click("#uC")
    pg.wait_for_timeout(200)

    # every view still draws something the reader can point at
    for btn, name in VIEWS:
        pg.click("#" + btn)
        pg.wait_for_timeout(220)
        st = pg.evaluate("window.__temp()")
        check(f"the {name} view has something to hover",
              st["nodes"] >= 2, str(st["nodes"]))

    # --- both scales on every figure, without pressing anything
    pg.click("#vRange")
    pg.click("#uC")
    pg.wait_for_timeout(220)
    check("a temperature in Celsius carries its Fahrenheit too",
          pg.evaluate("pair(37)") == "37.0°C · 98.6°F", pg.evaluate("pair(37)"))
    pg.click("#uF")
    pg.wait_for_timeout(200)
    check("and the other way round",
          pg.evaluate("pair(37)") == "98.6°F · 37.0°C", pg.evaluate("pair(37)"))
    pg.click("#uC")
    pg.wait_for_timeout(200)
    pg.evaluate("document.querySelector('[data-m=\"5\"]')"
                ".dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(150)
    when = pg.evaluate("document.getElementById('whenTxt').textContent")
    check("the cards carry both scales", "°C" in when and "°F" in when, when)

    html = PAGE.read_text(encoding="utf-8")
    check("no em dashes", "—" not in html)
    check("the page links back to the library", 'href="library.html"' in html)
    for doi in ["10.1093/ofid/ofz032", "10.1136/bmj.j5468",
                "10.1056/NEJMra1114208", "10.1093/ejcts/ezaa159",
                "10.1056/NEJMra011089", "10.1177/1073858418760481",
                "10.4085/1062-6050-50.9.07", "10.1016/j.wem.2018.10.004",
                "10.1016/j.resuscitation.2020.01.007",
                "10.3390/medicina56110589", "10.4085/1062-6050-45.5.439",
                "10.1186/cc5910"]:
        check(f"cites {doi}", doi in html)
    check("and says the hottest survival is a record, not a case report",
          "Guinness" in html)
    check("the page says the collapse view does not replace the emergency call",
          "does not replace the emergency number" in html)
    check("and owns up to how soft the cooling evidence is",
          "no randomised trial" in html.lower()
          or "There is no" in html and "randomised trial" in html)

    check("no JS errors", not errs, "; ".join(errs)[:140])
    br.close()

if fails:
    raise SystemExit(f"{len(fails)} check(s) failed")
print("all checks passed")
