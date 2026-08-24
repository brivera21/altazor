"""Comprueba premios-ariel.html contra sus datos y contra su dibujo.

  los datos    setenta ganadoras, ninguna en la suspensión ni en los años
               desiertos, los empates donde tocan, y cada edición cuadra
               con su año
  la página    dibuja todas las ganadoras, las siete bandas y la leyenda

Uso: python3 verify_ariel.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_ariel import FILMS, ERAS

fails = []

def roman(s):
    v = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
    t = 0
    for i, ch in enumerate(s):
        t += v[ch] * (-1 if i+1 < len(s) and v[s[i+1]] > v[ch] else 1)
    return t

print("--- los datos ---")
years = [y for y, *_ in FILMS]
ok = len(FILMS) == 70
print(f"  {'ok  ' if ok else 'FALLA'} setenta películas ganadoras")
if not ok: fails.append(f"{len(FILMS)} películas")

malos = [y for y in years if 1959 <= y <= 1971 or y in (1953, 1983)]
ok = not malos
print(f"  {'ok  ' if ok else 'FALLA'} ninguna cae en la suspensión ni en un año desierto")
if not ok: fails.append(f"años imposibles: {malos}")

from collections import Counter
c = Counter(years)
esperados = {1947: 2, 1972: 2, 1973: 3, 1975: 2, 1978: 2}
for y, n in esperados.items():
    if c[y] != n:
        fails.append(f"{y} tiene {c[y]} ganadoras, no {n}")
extra = [y for y, n in c.items() if n > 1 and y not in esperados]
if extra: fails.append(f"empates no documentados: {extra}")
print(f"  {'ok  ' if not fails else 'FALLA'} los empates: dos ediciones en 1947, "
      "empates en 1972, 1975 y 1978 y el triple de 1973")

# la edición cuadra con el año: I y II en 1947, luego III a XIII hasta 1958,
# y desde 1972 la edición es el año menos 1958
err = []
for y, ed, n, _d in FILMS:
    e = roman(ed)
    if y == 1947:
        okv = e in (1, 2)
    elif y <= 1958:
        okv = e == y - 1945
    else:
        okv = e == y - 1958
    if not okv: err.append(f"{n}: {ed} en {y}")
ok = not err
print(f"  {'ok  ' if ok else 'FALLA'} cada edición cuadra con su año de ceremonia")
if not ok: fails.append(f"ediciones fuera de serie: {err}")

s = (Path(__file__).parent.parent / "premios-ariel.html").read_text(encoding="utf-8")
for frag in ["La barraca", "Sujo", "amacc.org.mx", "Suspensión del premio",
             "desierto en 1953 y en 1983"]:
    ok = frag in s
    print(f"  {'ok  ' if ok else 'FALLA'} la página trae '{frag}'")
    if not ok: fails.append(f"falta '{frag}'")

print("--- el dibujo ---")
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("playwright no está instalado"); sys.exit(1)
with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1280, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("**wikipedia.org/**", lambda r: r.abort())
    pg.goto((Path(__file__).parent.parent / "premios-ariel.html").resolve().as_uri())
    pg.wait_for_selector("#tlsvg")
    n = pg.evaluate("()=>document.querySelectorAll('#tlsvg g[data-f]').length")
    ok = n == 70
    print(f"  {'ok  ' if ok else 'FALLA'} se dibujan las 70 ganadoras ({n})")
    if not ok: fails.append(f"se dibujan {n}")
    nb = pg.evaluate("()=>document.querySelectorAll('#tlsvg rect[data-era]').length")
    nl = pg.evaluate("()=>document.getElementById('legend').children.length")
    ok = nb == 7 and nl == 7
    print(f"  {'ok  ' if ok else 'FALLA'} siete bandas y siete entradas de leyenda ({nb}, {nl})")
    if not ok: fails.append(f"bandas {nb}, leyenda {nl}")
    pg.evaluate("()=>{view=clampView(1970,1982);render()}")
    n2 = pg.evaluate("()=>document.querySelectorAll('#tlsvg g[data-f]').length")
    ok = n2 < 70 and n2 >= 10
    print(f"  {'ok  ' if ok else 'FALLA'} acercarse a los setenta deja {n2} etiquetas")
    if not ok: fails.append(f"zoom deja {n2}")
    card = pg.evaluate("()=>{showFilm(0);return document.getElementById('filmTxt').textContent}")
    ok = card == "La barraca"
    print(f"  {'ok  ' if ok else 'FALLA'} la tarjeta responde: '{card}'")
    if not ok: fails.append(f"tarjeta: {card}")
    if errs: fails.append(f"errores de javascript: {errs}")
    br.close()

print()
if fails:
    for f in fails: print("FALLA", f)
    sys.exit(1)
print("todo cuadra")
