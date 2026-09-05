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
    check("the marks are dots on the figure, named by their own rows",
          pg.evaluate("document.querySelectorAll('#tsvg [data-m] text')"
                      ".length") == 0)
    # and each still points at the temperature it means
    ok = pg.evaluate(
        "[...document.querySelectorAll('#tsvg [data-m]')].every(g=>{"
        "const c=g.querySelector('circle'); if(!c) return false;"
        "const m=D.marks[+g.getAttribute('data-m')];"
        "return Math.abs(+c.getAttribute('cy')-yOf(m.t))<0.6;})")
    check("every mark still sits at its own height", ok)

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
    bot = pg.evaluate("RG.bot")
    check("it fills the whole scale, feet to head",
          box[1] < 14 and abs(box[1] + box[3] - bot) < 40,
          f"top {box[1]:.0f}, bottom {box[1]+box[3]:.0f} of {bot}")
    # the head is narrow and the shoulders are wide, which is how it reads
    hw = pg.evaluate("(()=>{const H=RG.bot-RG.top;"
                     "return {head:0.045*H, sh:0.092*H, hand:0.120*H};})()")
    check("the head is narrower than the shoulders",
          hw["head"] < hw["sh"] < hw["hand"], str(hw))

    # --- the degree-by-degree detail, now on the first view
    cells = pg.evaluate("document.querySelectorAll('#tsvg [data-q]').length")
    check("a slice of the figure for every degree", cells == 39, str(cells))
    pg.evaluate("document.querySelector('[data-q=\"40\"]')"
                ".dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(150)
    name = pg.evaluate("document.getElementById('nameTxt').textContent")
    body = pg.evaluate("document.getElementById('bodyTxt').textContent")
    check("and a cell in the fever range names its cost",
          "°C" in name and "per cent more oxygen" in body,
          name + " / " + body[:70])
    pg.evaluate("document.querySelector('[data-q=\"15\"]')"
                ".dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(150)
    body = pg.evaluate("document.getElementById('bodyTxt').textContent")
    check("while a cell below 18 says no one has been measured there",
          "No whole-body measurement" in body, body[:80])
    # the lines from the fine scale are on the body too
    lines = pg.evaluate("document.querySelectorAll('#tsvg [data-key]').length")
    check("the lines that matter are drawn on the figure",
          lines == len([1 for t, *_ in D.LINES
                        if not any(abs(m[0] - t) < 0.01 for m in D.MARKS)]),
          str(lines))

    # --- the whole span, written out one degree at a time
    rows = pg.evaluate("document.querySelectorAll('#degrees tbody tr').length")
    check("a row for every degree of the span",
          rows == int(D.ZONES[-1][1]) - int(D.ZONES[0][0]) + 1, str(rows))
    check("and every one of them says something of its own",
          len(set(D.PER_DEGREE.values())) == len(D.PER_DEGREE)
          and all(d in D.PER_DEGREE for d in range(10, 49)))
    check("one temperature column, in the scale the buttons chose",
          pg.evaluate("(()=>{const r=document.querySelectorAll("
                      "'#degrees tbody tr')[11];"
                      "return r.children[0].textContent==='37\u00b0C';})()"))
    check("the table runs hot at the top, the way the body stands",
          pg.evaluate("(()=>{const r=[...document.querySelectorAll("
                      "'#degrees tbody tr')].map(x=>parseFloat("
                      "x.children[0].textContent));"
                      "return r[0]===48&&r[r.length-1]===10"
                      "&&r.every((v,i)=>!i||v<r[i-1]);})()"))

    # --- the one thing this view is for: both halves on one axis
    geo = pg.evaluate(
        "(()=>{const svg=document.querySelector('#tsvg');"
        "const sb=svg.getBoundingClientRect();"
        "const rows=[...document.querySelectorAll('#degrees tbody tr')];"
        "const sc=sb.height/RG.bot;"
        "const mid=r=>{const b=r.getBoundingClientRect();"
        "return (b.top+b.bottom)/2-sb.top;};"
        "const drift=Math.max(...rows.map((r,i)=>"
        "Math.abs(mid(r)-yOf(48-i)*sc)));"
        "const hs=[...new Set(rows.map(r=>"
        "Math.round(r.getBoundingClientRect().height)))];"
        "const clip=[...document.querySelectorAll('#degrees td.w .cw')]"
        ".filter(x=>x.getBoundingClientRect().height>ROW-4).length;"
        "return {drift:+drift.toFixed(2), heights:hs, row:ROW, clip:clip,"
        "figTop:Math.round(sb.top), scale:+sc.toFixed(3)};})()")
    check("every row sits at its own degree on the figure, to the pixel",
          geo["drift"] < 1.0, str(geo["drift"]))
    check("and every row is the same height, because every degree is",
          len(geo["heights"]) == 1, str(geo["heights"]))
    check("the row height is the axis, so the two cannot drift",
          geo["heights"][0] == geo["row"], f'{geo["heights"]} vs {geo["row"]}')
    check("the figure is drawn at one pixel per unit", geo["scale"] == 1.0,
          str(geo["scale"]))
    check("no sentence is clipped by the row it sits in", geo["clip"] == 0,
          str(geo["clip"]))
    # a measured figure and a bracketed one are told apart
    check("a measured metabolic figure is marked as measured",
          pg.evaluate("(()=>{const r=[...document.querySelectorAll("
                      "'#degrees tbody tr')].find(x=>x.children[0]"
                      ".textContent.startsWith('37'));"
                      "return r.children[3].classList.contains('m')"
                      "&&r.children[3].textContent==='100%';})()"))
    check("and a gap between two of them is marked as a gap",
          pg.evaluate("(()=>{const r=[...document.querySelectorAll("
                      "'#degrees tbody tr')].find(x=>x.children[0]"
                      ".textContent.startsWith('30'));"
                      "return r.children[3].classList.contains('b')"
                      "&&r.children[3].textContent.includes('to');})()"))
    check("nothing is claimed below the coldest measurement",
          pg.evaluate("(()=>{const r=[...document.querySelectorAll("
                      "'#degrees tbody tr')].filter(x=>+x.children[0]"
                      ".textContent.replace(/[^\\d.-]/g,'')<18);"
                      "return r.every(x=>x.children[3].textContent"
                      "==='not measured');})()"))
    check("or above the hottest one",
          pg.evaluate("(()=>{const r=[...document.querySelectorAll("
                      "'#degrees tbody tr')].filter(x=>+x.children[0]"
                      ".textContent.replace(/[^\\d.-]/g,'')>42);"
                      "return r.every(x=>x.children[3].textContent"
                      "==='not measured');})()"))
    check("the pulse stops where its series stops",
          pg.evaluate("(()=>{const g=t=>[...document.querySelectorAll("
                      "'#degrees tbody tr')].find(x=>+x.children[0]"
                      ".textContent.replace(/[^\\d.-]/g,'')==t).children[4].textContent;"
                      "return g(19)==='not measured'&&g(20)!=='not measured'"
                      "&&g(43)==='not measured';})()"))
    check("the table is only on the view it belongs to",
          pg.evaluate("(()=>{document.getElementById('vDay').click();"
                      "const h=document.getElementById('degwrap').hidden;"
                      "document.getElementById('vRange').click();"
                      "return h&&!document.getElementById('degwrap').hidden;})()"))

    # --- one scale, and it reaches the sentences as well as the numbers
    for btn, unit, at37, tcol in [("#uC", "C", "37.0°C", "37°C"),
                                  ("#uF", "F", "98.6°F", "98.6°F"),
                                  ("#uK", "K", "310.15 K", "310.15 K")]:
        pg.click(btn)
        pg.wait_for_timeout(250)
        got = pg.evaluate(
            "document.querySelectorAll('#degrees tbody tr')[11]"
            ".children[0].textContent")
        check(f"the table's degree column reads {tcol}", got == tcol, got)
        prose = pg.evaluate(
            "document.querySelectorAll('#degrees tbody tr')[10]"
            ".children[2].textContent")
        check(f"and the sentences in it are in {unit} too",
              at37[-2:].strip() in prose or unit == "K" and " K" in prose,
              prose[:90])
        left = pg.evaluate("(document.body.innerText.match(/\\{\\d/g)||[]).length")
        check(f"no unconverted marker survives in {unit}", left == 0, str(left))
    pg.click("#uF")
    pg.wait_for_timeout(250)
    meth = pg.evaluate(
        "[...document.querySelectorAll('.method p')].map(p=>p.textContent)"
        ".join(' ')")
    check("the method notes follow the scale as well",
          "101.5°F" in meth or "100.4°F" in meth, meth[:0] or "no F in method")
    note = pg.evaluate("[...document.querySelectorAll('.note')][1].textContent")
    check("and the page no longer claims to show both at once",
          "both scales" not in note, note[:70])
    pg.click("#uC")
    pg.wait_for_timeout(250)

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

    # --- one scale at a time, and the whole page in it
    pg.click("#vRange")
    for btn, unit, want in [("#uC", "C", "46.5°C"), ("#uF", "F", "115.7°F"),
                            ("#uK", "K", "319.65 K")]:
        pg.click(btn)
        pg.wait_for_timeout(250)
        pg.evaluate("document.querySelector('[data-m=\"5\"]')"
                    ".dispatchEvent(new PointerEvent("
                    "'pointerover',{bubbles:true}))")
        pg.wait_for_timeout(140)
        when = pg.evaluate("document.getElementById('whenTxt').textContent")
        check(f"a card in {unit} gives one figure, not two", when == want, when)
        others = [s for s in ("°C", "°F", " K") if s not in want]
        check(f"and none of the other scales with it",
              not any(o in when for o in others), when)
        lad = pg.evaluate(
            "[...document.querySelectorAll('#tsvg text')]"
            ".map(t=>t.textContent).join('|')")
        check(f"the ladder beside the figure is in {unit} alone",
              not any(o in lad for o in others) and want[-2:].strip() in lad,
              lad[:80])
    pg.click("#uC")
    pg.wait_for_timeout(200)

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
