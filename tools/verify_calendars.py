"""Check calendars.html against its data, an independent calendar library,
and its drawing.

  the data     the year and month are the 2000 means; twelve months fall
               10.88 days short; 235 months miss 19 years by two hours;
               every calendar's common year adds up to what its kind
               should; the mean years are right against their rules
  the sums     the page's Gregorian, Julian, Hebrew, tabular Islamic and
               Maya conversions agree with the convertdate library and
               with hand-checked landmarks over a thousand days spread
               across six thousand years, both directions
  the drawing  the lunar ring starts where the arithmetic says after n
               years in both modes; the bars end at their year lengths;
               the markers drag and the card follows; no label overlaps
"""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "/tmp/claude-0/-home-claude/f95ea291-68fe-5058-9839-3897087404c1/scratchpad/cd_check")
from calendars_data import SKY, CALENDARS, TZOLKIN, HAAB, HEBREW_MONTHS, ISLAMIC_MONTHS, MAYA_CORRELATION

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "calendars.html"
fails = []


def check(ok, msg, extra=""):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}" + (f"  [{extra}]" if extra and not ok else ""))
    if not ok:
        fails.append(msg)


Y, M = SKY["tropical_year"], SKY["synodic_month"]
print("--- the data ---")
check(abs(Y - 365.24219) < 1e-9 and abs(M - 29.530589) < 1e-9, "the 2000 means: 365.24219 and 29.530589 days")
check(abs(Y - 12 * M - 10.875) < 0.01, f"twelve months fall {Y - 12 * M:.3f} days short of a year")
check(abs((235 * M - 19 * Y) * 24 - 2.1) < 0.3, f"235 months miss 19 years by {(235 * M - 19 * Y) * 24:.1f} hours")
check(abs(Y / (Y - 12 * M) - 33.6) < 0.1, f"a lunar year comes round in {Y / (Y - 12 * M):.1f} years")
check(abs(SKY["islamic_year"] - 10631 / 30) < 1e-4 and abs(SKY["hebrew_year"] - 235 * (29 + (12 + 793 / 1080) / 24) / 19) < 1e-4, "the tabular Islamic and fixed Hebrew mean years follow from their rules")
check(abs(SKY["gregorian_year"] - 146097 / 400) < 1e-9 and abs((SKY["gregorian_year"] - Y) ** -1) > 3000, f"the Gregorian year gains a day in {1 / (SKY['gregorian_year'] - Y):.0f} years")
for k, n, kind, months, leap, mean, rule, epoch, b, alive in CALENDARS:
    days = sum(d for _, d in months)
    want = {"tzolkin": 260, "hebrew": 354, "islamic": 354, "chinese": 354}.get(k, 365)
    check(days == want, f"{n}: a common year of {days} days in {len(months)} months")
check(abs(CALENDARS[0][5] - 365.2425) < 1e-9 and CALENDARS[1][5] == 365.25 and CALENDARS[4][5] == 365 and CALENDARS[9][5] == SKY["islamic_year"] and CALENDARS[8][5] == SKY["hebrew_year"], "the mean years match the rules")
check(len(TZOLKIN) == 20 and len(HAAB) == 19 and HAAB[-1] == "Wayeb\'" and len(HEBREW_MONTHS) == 13 and len(ISLAMIC_MONTHS) == 12 and MAYA_CORRELATION == 584283, "twenty day names, nineteen Haab months, thirteen Hebrew, twelve Islamic, the GMT correlation")

print("--- the sums ---")
from convertdate import gregorian, julian, hebrew, islamic, mayan
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1340, "height": 1100})
    errs = []
    pg.on("pageerror", lambda x: errs.append(str(x)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_selector("#csvg")

    def st(q=None):
        return pg.evaluate("(q)=>window.__cal(q)", q)

    plain = lambda w: "".join(ch for ch in w.lower() if ch.isalpha()).replace("z", "s")  # spellings of the glottal stop and of Sip/Zip differ between sources
    random.seed(7)
    jdns = [random.randint(300000, 3200000) for _ in range(1000)] + [0, 347998, 584283, 1948440, 2299160, 2299161, 2451545, 2461299]
    bad = {"greg": 0, "jul": 0, "heb": 0, "isl": 0, "lc": 0, "tz": 0, "haab": 0, "dow": 0}
    for J in jdns:
        c = st({"jdn": J})["conv"]
        jd = J - 0.5
        g = gregorian.from_jd(jd)
        if tuple(c["g"]) != tuple(g):
            bad["greg"] += 1
        if tuple(c["j"]) != tuple(julian.from_jd(jd)):
            bad["jul"] += 1
        if tuple(c["h"]) != tuple(hebrew.from_jd(jd)):
            bad["heb"] += 1
        if tuple(c["isl"]) != tuple(islamic.from_jd(jd)):
            bad["isl"] += 1
        if J >= 584283:
            if tuple(c["my"]["lc"]) != tuple(mayan.from_jd(jd)):
                bad["lc"] += 1
            tz = mayan.to_tzolkin(jd)
            if (c["my"]["tz"][0], plain(c["my"]["tz"][1])) != (tz[0], plain(tz[1])):
                bad["tz"] += 1
            hb = mayan.to_haab(jd)
            if (c["my"]["haab"][0], plain(c["my"]["haab"][1])) != (hb[0], plain(hb[1])):
                bad["haab"] += 1
        if c["dow"] != ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][(J) % 7]:
            bad["dow"] += 1
    for k, v in bad.items():
        check(v == 0, f"{k}: agrees with convertdate on all {len(jdns)} days" + (" from the Maya epoch on" if k in ("lc", "tz", "haab") else ""), f"{v} differ")
    c = st({"jdn": 2451545})["conv"]["text"]
    check(c["greg"] == "1 January 2000" and c["jul"] == "19 December 1999" and c["heb"] == "23 Tevet 5760 AM" and c["isl"] == "24 Ramadan 1420 AH" and c["lc"] == "12.19.6.15.2" and c["cr"] == "11 Ik' 10 K'ank'in", "1 January 2000, hand-checked in every calendar")
    c = st({"jdn": 584283})["conv"]["text"]
    check(c["lc"] == "0.0.0.0.0" and c["cr"] == "4 Ajaw 8 Kumk'u" and c["greg"] == "11 August 3114 BC", "the Maya epoch: 0.0.0.0.0, 4 Ajaw 8 Kumk'u, 11 August 3114 BC")
    c = st({"jdn": 1948440})["conv"]["text"]
    check(c["isl"] == "1 Muharram 1 AH" and c["jul"] == "16 July 622", "the Hijra epoch: 1 Muharram 1 AH, 16 July 622 Julian")
    check(st({"h": [1, 7, 1]})["hjdn"] == 347998 and st({"jdn": 347998})["conv"]["text"]["heb"] == "1 Tishrei 1 AM", "the Hebrew epoch: 1 Tishrei 1, Julian day 347998")
    check(st({"jdn": 2299161})["conv"]["text"]["greg"] == "15 October 1582" and st({"jdn": 2299160})["conv"]["text"]["jul"] == "4 October 1582", "the Gregorian reform: 4 October 1582 was followed by 15 October")
    # round trips both ways
    ok = True
    for J in jdns[:300]:
        c = st({"jdn": J})["conv"]
        if st({"g": c["g"]})["jdn"] != J or st({"h": c["h"]})["hjdn"] != J:
            ok = False
    check(ok, "Gregorian and Hebrew dates convert back to the same day number")

    print("--- the drawing ---")
    def overlaps(sel):
        boxes = pg.evaluate("(sel)=>[...document.querySelectorAll(sel)].filter(t=>!t.hasAttribute('transform')).map(t=>{const b=t.getBBox(); return [b.x,b.y,b.width,b.height]})", sel)
        return sum(1 for i in range(len(boxes)) for j in range(i + 1, len(boxes)) if boxes[i][0] < boxes[j][0] + boxes[j][2] and boxes[j][0] < boxes[i][0] + boxes[i][2] and boxes[i][1] < boxes[j][1] + boxes[j][3] and boxes[j][1] < boxes[i][1] + boxes[i][3])

    s = st()
    check(s["view"] == "sky" and s["years"] == 0 and s["mode"] == "moon" and "33.6 years" in s["card"], "opens on the sky, year one, the Moon alone, 33.6 years to come round")
    check(s["moon0"] == s["arc0"], "the first lunar month is drawn where the arithmetic starts it")
    L = st({"years": 5})["lunar"]
    check(abs(L["raw"] + 5 * (Y - 12 * M)) < 1e-6 and abs(L["start"] - (Y - (5 * (Y - 12 * M)) % Y)) < 1e-6, "after five years the lunar year begins 54.4 days earlier")
    L = st({"years": 19, "mode": "both"})["lunar"]
    check(L["leaps"] == 7 and abs(L["raw"] - (235 * M - 19 * Y)) < 1e-6, f"held to the Sun, 19 years bring 7 thirteenth months and a slip of {L['raw'] * 24:.1f} hours")
    # drag round the ring: a quarter turn is about 8 years
    box = pg.eval_on_selector("#csvg", "e=>{const r=e.getBoundingClientRect(); return {x:r.left,y:r.top,w:r.width,h:r.height,vh:e.viewBox.baseVal.height}}")
    sx = lambda px: box["x"] + px / 980 * box["w"]
    sy = lambda py: box["y"] + py / box["vh"] * box["h"]
    pg.mouse.move(sx(470), sy(330 - 250))
    pg.mouse.down()
    pg.mouse.move(sx(470 + 250), sy(330), steps=6)
    pg.mouse.up()
    pg.wait_for_timeout(100)
    s = st()
    check(s["years"] == round(0.25 * Y / (Y - 12 * M)) and f"after {s['years']} years" in s["card"], f"a quarter turn of the ring runs {s['years']} years on and the card follows")
    check(overlaps("#csvg text") == 0, "no two labels overlap on the sky", f"{overlaps('#csvg text')}")
    pg.click('#views button[data-v="cals"]')
    pg.wait_for_timeout(150)
    s = st({"cal": "islamic"})
    check(s["bars"] == len(CALENDARS) and s["cells"] == sum(len(c[3]) for c in CALENDARS), f"{len(CALENDARS)} bars with every month drawn")
    check(abs(s["barEnd"] - s["expect"]) < 0.6, "the Islamic bar ends at 354 days")
    pg.evaluate("()=>document.querySelector('#csvg g[data-month=\"hebrew:5\"]').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(80)
    s = st()
    check(s["name"] == "Adar" and "29" in s["card"] and "day 149" in s["card"], "hovering Adar: 29 days, beginning on day 149")
    pg.evaluate("()=>document.querySelector('#csvg g[data-cal=\"gregorian\"] text').dispatchEvent(new PointerEvent('pointerover',{bubbles:true}))")
    pg.wait_for_timeout(80)
    s = st()
    check(s["name"] == "Gregorian" and "365.2425" in s["card"] and "+0 minutes" in s["card"] or "365.2425 days, +0 minutes" in s["card"], "the Gregorian card: 365.2425 days, within a minute of the Sun")
    check(overlaps("#csvg text") == 0, "no two labels overlap on the bars", f"{overlaps('#csvg text')}")
    pg.click('#views button[data-v="day"]')
    pg.wait_for_timeout(150)
    s = st()
    check(s["view"] == "day" and abs(s["ymark"] - s["yx"]) < 0.6 and abs(s["dmark"] - s["dx"]) < 0.6, "the day view opens with both markers on today")
    DY = {"x": 80, "w": 820, "y0": -3000, "y1": 2300}
    YX = lambda y: DY["x"] + (y - DY["y0"]) / (DY["y1"] - DY["y0"]) * DY["w"]
    pg.mouse.move(sx(s["ymark"]), sy(70))
    pg.mouse.down()
    pg.mouse.move(sx(YX(2000)), sy(70), steps=5)
    pg.mouse.up()
    pg.wait_for_timeout(100)
    s = st()
    check(s["year"] == 2000 and abs(s["ymark"] - YX(2000)) < 0.6, f"dragging the year marker to 2000: {s['year']}")
    DX = lambda d: 80 + (d - 1) / 365 * 820
    pg.mouse.move(sx(s["dmark"]), sy(170))
    pg.mouse.down()
    pg.mouse.move(sx(DX(1)), sy(170), steps=5)
    pg.mouse.up()
    pg.wait_for_timeout(100)
    s = st()
    check(s["doy"] == 1 and "Saturday, 1 January 2000" in s["name"] and "2,451,545" in s["card"] and "23 Tevet 5760" in s["card"] and "12.19.6.15.2" in s["card"], "and the day marker to 1 January: the card reads Saturday, 2,451,545, 23 Tevet 5760, 12.19.6.15.2")
    check(overlaps("#csvg text") == 0, "no two labels overlap on the day view", f"{overlaps('#csvg text')}")
    check(not errs, "no script errors", "; ".join(errs))
    br.close()

print("--- the copy ---")
html = PAGE.read_text()
check("—" not in html, "no em dashes")

print()
if fails:
    print(f"{len(fails)} FAILED:")
    for x in fails:
        print("  -", x)
    sys.exit(1)
print("everything squares")
