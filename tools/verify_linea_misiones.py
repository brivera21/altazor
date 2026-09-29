#!/usr/bin/env python3
"""Check linea-misiones.html: the year runs the sites, Recorrer plays, the
rebellion chips take the map to their year, a site's card pins, the kinds
filter, and the copy keeps one caption with the rest under Fuentes.

Uso: python3 verify_linea_misiones.py
"""
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(__file__).resolve().parent.parent / "linea-misiones.html"
html = PAGE.read_text(encoding="utf-8")
fails = []


def check(ok, msg):
    print(f"  {'ok  ' if ok else 'FALLA'} {msg}")
    if not ok:
        fails.append(msg)


S = eval(re.search(r"^var S=(.*);$", html, re.M).group(1))
R = eval(re.search(r"^var R=(.*);$", html, re.M).group(1))


def up(s, y):
    return y >= s[3] and not (len(s) > 5 and s[5] <= y < s[6])


print("--- la página ---")
check("—" not in re.sub(r"<script[\s\S]*?</script>", "", html), "sin rayas largas")
with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1300, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_timeout(300)
    st = lambda: pg.evaluate("()=>window.__misiones()")
    check(pg.evaluate("document.querySelector('h1').getBoundingClientRect().top < document.querySelector('figure svg').getBoundingClientRect().top"), "el título va sobre el mapa")
    for y in (1600, 1655, 1680, 1720):
        pg.evaluate("(y)=>{const s=document.getElementById('yr');s.value=y;s.dispatchEvent(new Event('input'))}", y)
        want = sum(1 for s in S if up(s, y))
        check(st()["shown"] == want and pg.inner_text("#count") == str(want), f"en {y} quedan {want} sitios en pie")
    pg.click("#play")
    pg.wait_for_timeout(1200)
    a = st()
    check(a["run"] and 1560 < a["yr"] < 1600 and pg.inner_text("#play") == "Pausa", f"Recorrer arranca en 1560 y avanza: {a['yr']}")
    pg.click("#play")
    check(not st()["run"], "y se detiene")
    i = next(k for k, x in enumerate(R) if x[0] == 1652)
    pg.click(f"#rebs button:nth-of-type({i + 1})")
    s = st()
    check(s["yr"] == 1652 and s["pin"] == R[i][2] and "Aguilar" in s["name"] and "1652" in s["ev"], "el chip de 1652 lleva el mapa a ese año y fija la Villa de Aguilar")
    op = pg.evaluate(f"document.querySelectorAll('#nodes g')[{R[i][2]}].querySelector('circle').getAttribute('opacity')")
    check(op != "0", "y su anillo marca dónde pegó la rebelión")
    pg.keyboard.press("Escape")
    check(st()["pin"] is None, "Escape la suelta")
    pg.evaluate("(y)=>{const s=document.getElementById('yr');s.value=y;s.dispatchEvent(new Event('input'))}", 1720)
    pg.click("#kinds button:nth-of-type(1)")
    s = st()
    check(s["kind"] == "j" and s["dim"] == sum(1 for x in S if x[4] != "j"), f"jesuita apaga a los otros {s['dim']}")
    pg.click("#kinds button:nth-of-type(1)")
    check(st()["dim"] == 0, "y los vuelve a encender")
    check(st()["labels"] >= 7, "los lugares que nombra el texto llevan su nombre en el mapa")
    vis = pg.evaluate("[...document.querySelectorAll('p')].filter(p=>p.checkVisibility()&&!p.closest('.card,.readout')).length")
    check(vis == 2 and not pg.evaluate("document.querySelector('details.sources').open"), "el subtítulo y un pie a la vista; lo demás en Fuentes, cerrado")
    check(len(pg.inner_text(".cap").split()) <= 80, f"el pie tiene {len(pg.inner_text('.cap').split())} palabras")
    check(not errs, "sin errores de javascript")
    ph = br.new_page(viewport={"width": 390, "height": 844})
    ph.goto(PAGE.as_uri())
    ph.wait_for_timeout(300)
    check(ph.evaluate("document.documentElement.scrollWidth - innerWidth") == 0, "nada más ancho que un teléfono")
    br.close()

print()
if fails:
    print(f"{len(fails)} FALLAS")
    sys.exit(1)
print("todo cuadra")
