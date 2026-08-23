"""Comprueba cabalgata-villista.html contra sus fuentes y contra su dibujo.

  paradas     las quince cabeceras, cada una donde dice GeoNames, en el orden
              que publica el gobierno del estado, y de sur a norte salvo el
              rodeo por Guerrero que el camino obliga
  traza       empieza en Bachíniva y termina en Columbus, pasa por cada parada
              a menos de doscientos metros, no se sale del cuadro y su largo
              cuadra con el kilometraje de las paradas
  perfil      una muestra cada dos kilómetros, la primera en Bachíniva y la
              última en Columbus, dentro de las altitudes que reporta GeoNames
  frontera    Columbus queda del lado de Estados Unidos y Puerto Palomas del
              lado mexicano
  la página   responde por lo que dibujó, en el navegador

Uso: pip install playwright && python3 verify_villista.py
"""
import json
import math
import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import villista_data as V

HERE = Path(__file__).parent
PAGE = HERE.parent / "cabalgata-villista.html"
fails = []

# el orden que publica el gobierno del estado, tecleado aparte
MUNICIPIOS = ["Bachíniva", "Guerrero", "Matachí", "Temósachic", "Madera",
              "Gómez Farías", "Ignacio Zaragoza", "Buenaventura", "Galeana",
              "Nuevo Casas Grandes", "Casas Grandes", "Janos", "Ascensión"]


def hav(a, b):
    R = 6371.0088
    r = math.radians
    q = (math.sin(r(b[0] - a[0]) / 2) ** 2 + math.cos(r(a[0])) * math.cos(r(b[0]))
         * math.sin(r(b[1] - a[1]) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(q))


def track():
    v = [int(x) for x in "".join(V.TRACK).split(",")]
    lat, lon = v[0], v[1]
    out = [(lat / 1e5, lon / 1e5)]
    for i in range(2, len(v), 2):
        lat += v[i]
        lon += v[i + 1]
        out.append((lat / 1e5, lon / 1e5))
    return out


print("--- las paradas contra la lista publicada ---")
mun = [s[1] for s in V.STOPS]
ok = mun[:13] == MUNICIPIOS
print(f"  {'ok  ' if ok else 'FALLA'} los trece municipios de Chihuahua van en "
      "el orden que publica el estado")
if not ok:
    fails.append(f"el orden de municipios no cuadra: {mun[:13]}")
ok = V.STOPS[-1][1].endswith("Nuevo México") and V.STOPS[-2][0] == "Puerto Palomas"
print(f"  {'ok  ' if ok else 'FALLA'} después de Ascensión van Puerto Palomas y "
      "Columbus")
if not ok:
    fails.append("el remate no es Puerto Palomas y Columbus")

# de sur a norte, salvo el rodeo a Ciudad Guerrero
bajan = [(a[0], b[0]) for a, b in zip(V.STOPS, V.STOPS[1:]) if b[2] < a[2]]
ok = bajan == [("Bachíniva", "Ciudad Guerrero"),
               ("Nuevo Casas Grandes", "Casas Grandes")]
print(f"  {'ok  ' if ok else 'FALLA'} solo dos tramos van hacia el sur: el "
      "rodeo a Ciudad Guerrero y el brinco de Nuevo Casas Grandes a Casas Grandes")
if not ok:
    fails.append(f"tramos hacia el sur inesperados: {bajan}")

print("--- las coordenadas contra GeoNames ---")
# GeoNames archiva tres de estas cabeceras con otro nombre
ALIAS = {"Ciudad Madera": "Madera", "Ciudad Guerrero": "Vicente Guerrero",
         "Gómez Farías": "Valentín Gómez Farías", "San Buenaventura": "Buenaventura"}
try:
    import geonamescache
    gc = geonamescache.GeonamesCache()
    todas = list(gc.get_cities().values())
    revisadas, otro = 0, []
    for n, m, la, lo, el, pob, _i, _km in V.STOPS:
        if not pob or pob < 15000:
            continue
        revisadas += 1
        busca = ALIAS.get(n, n).lower()
        hit = [c for c in todas
               if c["name"].lower() == busca and hav((la, lo), (c["latitude"], c["longitude"])) < 6]
        if not hit:
            fails.append(f"{n} no aparece en GeoNames donde la página lo pone")
        elif ALIAS.get(n, n) != n:
            otro.append(f"{n} viene como {ALIAS[n]}")
    print(f"  ok   las {revisadas} paradas de más de quince mil habitantes "
          "aparecen en GeoNames a menos de seis kilómetros de donde van aquí")
    print(f"  ok   con otro nombre en el padrón: {', '.join(otro) or 'ninguna'}")
except ImportError:
    print("  geonamescache no está instalado, se salta")

print("--- la traza ---")
pts = track()
largo = sum(hav(pts[i - 1], pts[i]) for i in range(1, len(pts)))
ok = 0.95 < largo / V.STOPS[-1][7] < 1.0
print(f"  {'ok  ' if ok else 'FALLA'} la línea dibujada mide {largo:.0f} km, "
      f"contra {V.STOPS[-1][7]:.0f} km de camino ruteado")
if not ok:
    fails.append(f"la traza mide {largo:.0f} km contra {V.STOPS[-1][7]:.0f}")

lejos = []
for n, m, la, lo, el, pob, i, km in V.STOPS:
    d = hav(pts[i], (la, lo)) * 1000
    if d > 200:
        lejos.append(f"{n} a {d:.0f} m de su nodo")
print(f"  {'ok  ' if not lejos else 'FALLA'} cada parada cae sobre su nodo de "
      "la traza")
if lejos:
    fails.append(f"paradas fuera de la traza: {lejos}")

kms = [s[7] for s in V.STOPS]
ok = kms == sorted(kms) and kms[0] == 0
print(f"  {'ok  ' if ok else 'FALLA'} el kilometraje de las paradas crece "
      "de Bachíniva a Columbus")
if not ok:
    fails.append(f"kilometraje desordenado: {kms}")

# ningún salto absurdo entre puntos seguidos
saltos = [hav(pts[i - 1], pts[i]) for i in range(1, len(pts))]
ok = max(saltos) < 30
print(f"  {'ok  ' if ok else 'FALLA'} el salto más largo entre dos puntos "
      f"seguidos es de {max(saltos):.1f} km")
if not ok:
    fails.append(f"salto de {max(saltos):.1f} km en la traza")

print("--- el perfil ---")
prof = [int(x) for x in "".join(V.PROF).split(",")]
ok = abs(len(prof) - V.STOPS[-1][7] / V.STEP_KM) <= 1
print(f"  {'ok  ' if ok else 'FALLA'} {len(prof)} muestras, una cada "
      f"{V.STEP_KM:.0f} km de los {V.STOPS[-1][7]:.0f} km")
if not ok:
    fails.append(f"el perfil trae {len(prof)} muestras")
for idx, nombre, alt in ((0, V.STOPS[0][0], V.STOPS[0][4]),
                         (-1, V.STOPS[-1][0], V.STOPS[-1][4])):
    d = abs(prof[idx] - alt)
    ok = d < 60
    print(f"  {'ok  ' if ok else 'FALLA'} en {nombre} el perfil marca "
          f"{prof[idx]} m y GeoNames {alt} m")
    if not ok:
        fails.append(f"el perfil en {nombre} difiere {d} m de GeoNames")
ok = max(prof) < 2600 and min(prof) > 1100
print(f"  {'ok  ' if ok else 'FALLA'} el perfil va de {min(prof)} a {max(prof)} m")
if not ok:
    fails.append(f"altitudes fuera de rango: {min(prof)} a {max(prof)}")

print("--- la línea internacional ---")
us = pickle.load(open("/home/claude/us/states.pkl", "rb"))
from shapely.geometry import Point
nm = us["NM"]
col = V.STOPS[-1]
pal = V.STOPS[-2]
ok = nm.contains(Point(col[3], col[2])) and not nm.contains(Point(pal[3], pal[2]))
print(f"  {'ok  ' if ok else 'FALLA'} Columbus queda dentro de Nuevo México y "
      "Puerto Palomas fuera")
if not ok:
    fails.append("la frontera no separa Columbus de Puerto Palomas")

html = PAGE.read_text(encoding="utf-8")
print("--- la página ---")
import re
cuerpo = re.sub(r"<script[\s\S]*?</script>", "", html)
if "—" in cuerpo:
    fails.append("hay una raya larga en el texto de la página")
for want in ("Cabalgata Binacional Villista", "library.html", "ALTAZOR",
             "Referencias", "BRouter"):
    ok = want in html
    print(f"  {'ok  ' if ok else 'FALLA'} la página trae {want!r}")
    if not ok:
        fails.append(f"a la página le falta {want!r}")

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("\nplaywright no está instalado")
    sys.exit(1)

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1280, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.resolve().as_uri())
    pg.wait_for_function("() => !!window.__villista", timeout=15000)
    st = pg.evaluate("()=>window.__villista()")
    print("--- lo que dibujó la página ---")
    for k, want in (("puntos", len(pts)), ("paradas", len(V.STOPS))):
        ok = st[k] == want
        print(f"  {'ok  ' if ok else 'FALLA'} {k}: {st[k]}, esperados {want}")
        if not ok:
            fails.append(f"la página dibujó {st[k]} {k}")
    print(f"  ok   {st['rios']} ríos en el cuadro")

    # el jinete camina y las lecturas lo siguen
    prev = None
    for km in (0, 200, 400, 653.1):
        pg.evaluate("(k)=>{const s=document.getElementById('km');s.value=k;"
                    "s.dispatchEvent(new Event('input'))}", km)
        pg.wait_for_timeout(80)
        s = pg.evaluate("()=>window.__villista()")
        alt = int(s["alt"].split()[0])
        esperado = prof[min(len(prof) - 1, int(round(km / V.STEP_KM)))]
        ok = abs(alt - esperado) < 40
        print(f"  {'ok  ' if ok else 'FALLA'} en el km {km:.0f} la página marca "
              f"{alt} m y el perfil {esperado} m, tramo {s['tramo']!r}")
        if not ok:
            fails.append(f"altitud en el km {km}: página {alt}, perfil {esperado}")
        if prev and s["jinete"] == prev:
            fails.append(f"el jinete no se movió en el km {km}")
        prev = s["jinete"]

    for bid, gid in (("bRel", "relieve"), ("bRio", "rios")):
        pg.click("#" + bid)
        pg.wait_for_timeout(100)
        d = pg.evaluate(f"()=>getComputedStyle(document.getElementById('{gid}')).display")
        pg.click("#" + bid)
        ok = d == "none"
        print(f"  {'ok  ' if ok else 'FALLA'} {bid} apaga su capa")
        if not ok:
            fails.append(f"{bid} no apaga {gid}")
    pg.click("#b1916")
    pg.wait_for_timeout(100)
    n = pg.evaluate("()=>document.querySelectorAll('#hitos text').length")
    vis = pg.evaluate("()=>getComputedStyle(document.getElementById('hitos')).display")
    ok = vis != "none" and n == 6
    print(f"  {'ok  ' if ok else 'FALLA'} 1916 enciende {n} letreros")
    if not ok:
        fails.append(f"la capa de 1916 muestra {n} letreros y display {vis}")

    if errs:
        fails.append(f"errores de javascript: {errs}")
    br.close()

print()
if fails:
    for f in fails:
        print("FALLA", f)
    sys.exit(1)
print("todo cuadra")
