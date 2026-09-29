#!/usr/bin/env python3
"""Check orbit-sine.html, The Year: Earth's Cycle.

The page is hand-built. The checks: it opens partway between the pole and the
side with a year already traced; the view buttons swing the view over a second
rather than jump; the dates the clock prints and the equinoxes and solstices it
marks agree with pyephem; a click on the trace takes the clock back to that
moment while a drag turns the view; To scale shrinks the Sun to its true size
against the orbit; the copy keeps to one caption with the rest in a closed
Sources details; and the phone view fits.

Usage: python3 tools/verify_orbit_sine.py
"""
import re
import sys
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "orbit-sine.html"
fails = []


def check(ok, msg, detail=""):
    print(("  ok   " if ok else "  FAIL ") + msg + (f"  [{detail}]" if detail and not ok else ""))
    if not ok:
        fails.append(msg)


html = PAGE.read_text(encoding="utf-8")
print("--- the copy ---")
check("—" not in html, "no em dashes")
cap = re.search(r'<div id="note">([\s\S]*?)</div>', html)
nw = len(re.sub(r"<[^>]+>", " ", cap.group(1)).split()) if cap else 999
check(nw <= 80, f"one caption, {nw} words")
det = re.search(r'<details class="sources"[^>]*>([\s\S]*?)</details>', html)
check(det and " open" not in det.group(0)[:45] and "Meeus" in det.group(1) and "Naval Observatory" in det.group(1)
      and "Note on accuracy" not in html, "the accuracy note, the method and the references sit in a closed Sources details")
check("px/yr" not in html and "Year spacing" in html and "Years of trace" in html, "the controls speak of years, not pixels")

try:
    import ephem
except ImportError:
    ephem = None
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1300, "height": 850})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_timeout(250)
    o = pg.evaluate("window.__orbit")
    print("--- the opening ---")
    check(abs(o["tilt"] - 35) < 0.5 and o["simYears"] >= 1 and o["tracePast"] == 5,
          f"opens at {o['tilt']:.0f} degrees with {o['simYears']:.2f} years run and 5 years of trace kept")
    check(o["date"].endswith("2027") and o["simYears"] < 1.6, f"and the date reads {o['date']}, a year and a little after the March equinox of 2026")

    print("--- the view buttons ---")
    pg.click("#viewBtn")
    pg.wait_for_timeout(420)
    mid = pg.evaluate("window.__orbit.tilt")
    pg.wait_for_timeout(900)
    end = pg.evaluate("window.__orbit.tilt")
    check(2 < mid < 33 and end < 0.01, f"Pole view swings the view over a second ({mid:.1f} degrees at 0.4 s, {end:.1f} at the end)")
    pg.click("#sideBtn")
    pg.wait_for_timeout(420)
    mid = pg.evaluate("window.__orbit.tilt")
    pg.wait_for_timeout(900)
    end = pg.evaluate("window.__orbit.tilt")
    check(10 < mid < 88 and abs(end - 90) < 0.01, f"Side view the same way ({mid:.1f} at 0.4 s, {end:.1f} at the end)")

    print("--- the calendar ---")
    pg.evaluate("window.__orbitSet({play:false})")
    ev = {"June solstice": 92.74, "September equinox": 186.39, "December solstice": 276.25, "March equinox": 365.2422}
    want = {}
    if ephem:
        d = ephem.next_equinox("2026/1/1")
        t0 = float(d)
        s1 = ephem.next_solstice(d); e1 = ephem.next_equinox(s1); w1 = ephem.next_solstice(e1); m2 = ephem.next_equinox(w1)
        for name, t in [("June solstice", s1), ("September equinox", e1), ("December solstice", w1), ("March equinox", m2)]:
            want[name] = (t.datetime(), float(t) - t0)
        check(abs(ephem.Date(d).datetime().hour * 60 + ephem.Date(d).datetime().minute - (14 * 60 + 46)) <= 1,
              f"the clock starts at the March equinox of 2026, {ephem.Date(d)} UT by pyephem")
    for name, days in ev.items():
        pg.evaluate("(y)=>window.__orbitSet({years:y})", days / 365.2422)
        pg.wait_for_timeout(80)
        o = pg.evaluate("window.__orbit")
        if name in want:
            dt, dd = want[name]
            wd = dt.strftime("%B ") + str(dt.day) + ", " + str(dt.year)
            check(abs(dd - days) < 0.05 and o["date"] == wd and name in o["event"],
                  f"the {name}: {days} days in, the page prints {o['date']} and names it; pyephem has {dt:%Y-%m-%d %H:%M}",
                  f"{o['date']} / {o['event']} / {dd:.2f}")
    check(len(o["events"]) == 4, "four marks for the equinoxes and solstices")

    print("--- a click on the trace ---")
    pg.evaluate("window.__orbitSet({years:3.3})")
    pg.click("#viewBtn"); pg.wait_for_timeout(50)
    pg.evaluate("document.getElementById('tilt').value=60; document.getElementById('tilt').dispatchEvent(new Event('input'))")
    pg.wait_for_timeout(120)
    p = pg.evaluate("window.__orbitPos(1.25)")
    pg.mouse.click(p["x"], p["y"])
    pg.wait_for_timeout(120)
    o = pg.evaluate("window.__orbit")
    check(abs(o["simYears"] - 2.05) < 0.03 and not o["playing"], f"a click 1.25 years back on the trace sets the clock to {o['simYears']:.3f} years and holds it")
    t0 = o["tilt"]
    pg.mouse.move(300, 300); pg.mouse.down(); pg.mouse.move(360, 300, steps=6); pg.mouse.up()
    pg.wait_for_timeout(100)
    o2 = pg.evaluate("window.__orbit")
    check(o2["tilt"] > t0 + 10 and abs(o2["simYears"] - o["simYears"]) < 1e-9, f"a drag turns the view ({t0:.0f} to {o2['tilt']:.0f} degrees) and leaves the clock alone")

    print("--- to scale ---")
    pg.click("#scaleBtn")
    pg.wait_for_timeout(400)
    mid = pg.evaluate("window.__orbit.sunR")
    pg.wait_for_timeout(1000)
    o = pg.evaluate("window.__orbit")
    true_r = pg.evaluate("Math.min(innerWidth, innerHeight)*0.36") * o["viewScale"] * 695700 / 149597870.7
    check(o["scaleK"] == 1 and abs(o["sunR"] - max(0.8, true_r)) < 0.01 and o["sunR"] < mid < 26,
          f"To scale shrinks the Sun over a second to {o['sunR']:.2f} px, 0.47% of the orbit's radius")
    pg.click("#scaleBtn")
    pg.wait_for_timeout(1300)
    check(pg.evaluate("window.__orbit.sunR") == 26, "and back")
    check(not errs, "no script errors", "; ".join(errs))

    print("--- a phone ---")
    ph = br.new_page(viewport={"width": 390, "height": 844})
    ph.on("pageerror", lambda e: errs.append(str(e)))
    ph.goto(PAGE.as_uri())
    ph.wait_for_timeout(300)
    ov = ph.evaluate("document.documentElement.scrollWidth - innerWidth")
    btn = ph.evaluate("Math.max(...[...document.querySelectorAll('button')].map(b=>b.getBoundingClientRect().right))")
    o = ph.evaluate("window.__orbit")
    check(ov == 0 and btn <= 390 and o["earth"]["y"] < o["ctrlTop"], f"at 390 px nothing runs off the side (buttons end at {btn:.0f}) and the orbit sits above the controls")
    br.close()

print()
if fails:
    print(f"{len(fails)} FAILED:")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("everything squares")
