#!/usr/bin/env python3
"""Verify red-mars.html against what the page actually draws.

Checks, by driving the built page in a real browser with the network cut:
the projection math on known features, feature counts, the zoom-gated
labels (summary at whole-planet zoom, individual names when close), the
hi-res layer past zoom 2.2, and the side card content for a canyon and a
novel site.

Usage: python3 verify_mars_map.py
"""

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

PAGE = Path(__file__).parent.parent / "red-mars.html"

FAILS = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1280, "height": 860})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", lambda r: r.abort()
                       if r.request.url.startswith("http") else r.continue_())
        await pg.goto(PAGE.as_uri())
        await pg.wait_for_timeout(500)

        st = await pg.evaluate("window.__mars()")
        check("14 canyons in the data", st["canyons"] == 14, str(st["canyons"]))
        check("9 novel sites in the data", st["sites"] == 9, str(st["sites"]))
        check("starts at whole-planet zoom", abs(st["zoom"] - 1) < 1e-9)

        # projection: Sheffield sits at Pavonis Mons, 0.9 N 247.04 E
        xy = await pg.evaluate(
            "(() => { const s = SITES.find(s => s.n === 'Sheffield');"
            " return [s.x, s.y]; })()")
        check("Sheffield x from lon 247.04E",
              abs(xy[0] - ((247.04 + 180) % 360) / 360 * 2400) < 0.15,
              str(xy[0]))
        check("Sheffield y from lat 0.9N",
              abs(xy[1] - (90 - 0.9) / 180 * 1200) < 0.15, str(xy[1]))

        # zoom-gated labels: whole planet shows the one summary label only
        n = await pg.evaluate("document.querySelectorAll('[data-c] text').length")
        summ = await pg.evaluate("!!document.getElementById('vmSummary')")
        check("no individual canyon names at whole-planet zoom", n == 0, str(n))
        check("summary label at whole-planet zoom", summ)
        rings = await pg.evaluate("document.querySelectorAll('[data-c] circle').length")
        check("all 14 canyon rings still drawn", rings == 14, str(rings))

        # the canyons button zooms in: names appear, summary goes
        await pg.click("#bVM")
        await pg.wait_for_timeout(300)
        st = await pg.evaluate("window.__mars()")
        check("canyons button zooms past 2", st["zoom"] >= 2, str(st["zoom"]))
        n = await pg.evaluate("document.querySelectorAll('[data-c] text').length")
        summ = await pg.evaluate("!!document.getElementById('vmSummary')")
        check("all 14 canyon names when close", n == 14, str(n))
        check("summary label gone when close", not summ)
        hires = await pg.evaluate(
            "document.querySelectorAll('#marsvg image').length")
        check("hi-res strip drawn past zoom 2.2", hires == 2, str(hires))

        # card content: hover a canyon, then a novel site
        await pg.evaluate("showCanyon('Melas Chasma')")
        kind = await pg.evaluate("document.getElementById('kindTxt').textContent")
        name = await pg.evaluate("document.getElementById('nameTxt').textContent")
        check("canyon card kind", kind == "A real canyon", kind)
        check("canyon card name", name == "Melas Chasma", name)
        body = await pg.evaluate("document.querySelector('.card').textContent")
        check("Melas card mentions its length", "564" in body)

        await pg.evaluate("showSite('Low Point')")
        body = await pg.evaluate("document.querySelector('.card').textContent")
        check("Low Point card is the Hellas mohole",
              "Hellas" in body and "mohole" in body)

        await pg.evaluate("showSite('Sheffield')")
        body = await pg.evaluate("document.querySelector('.card').textContent")
        check("Sheffield card has Pavonis Mons", "Pavonis Mons" in body)

        # the canyon-names toggle hides all canyon marks
        await pg.click("#bCan")
        await pg.wait_for_timeout(200)
        st = await pg.evaluate("window.__mars()")
        n = await pg.evaluate("document.querySelectorAll('[data-c]').length")
        check("canyon toggle hides canyon marks",
              not st["showCan"] and st["showNov"] and n == 0,
              f"showCan={st['showCan']} marks={n}")

        check("no JS errors", not errs, "; ".join(errs))
        await b.close()

    if FAILS:
        raise SystemExit(f"{len(FAILS)} check(s) failed")
    print("all checks passed")


asyncio.run(main())
