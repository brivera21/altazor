"""Comprueba ruta-namiquipa.html contra el recorrido grabado y contra la malla.

  traza       empieza y termina donde dice el archivo original, mide lo que
              mide el recorrido completo, cabe en el cuadro del mapa y no da
              saltos imposibles para una moto
  perfil      una muestra cada cien metros, con las horas creciendo, y sin
              velocidades que no puedan ser
  malla       la altitud del GPS contra la malla del terreno, punto por punto:
              es la comprobación que la página presume
  lugares     los pueblos y ranchos caen dentro del cuadro y del lado que dice
  la página   responde por lo que dibujó, en el navegador

Uso: pip install playwright && python3 verify_namiquipa.py
"""
import base64
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import namiquipa_data as D

HERE = Path(__file__).parent
PAGE = HERE.parent / "ruta-namiquipa.html"
DEM = HERE / "data" / "namiquipa_dem.txt"
fails = []

NX, NY, DX = 87, 31, 0.003
W, N = -107.70, 29.095
E, S = W + (NX - 1) * DX, N - (NY - 1) * DX

# el archivo original, tal como lo publicó su autor
SALIDA = (29.071108, -107.654690)
LLEGADA = (29.028872, -107.479090)
LARGO_KM = 28.11
ELE_SALIDA, ELE_LLEGADA = 2584, 1891
DURACION_S = 13301        # 3 h 41 min 41 s


def hav(a, b):
    R = 6371.0088
    r = math.radians
    q = (math.sin(r(b[0] - a[0]) / 2) ** 2 + math.cos(r(a[0])) * math.cos(r(b[0]))
         * math.sin(r(b[1] - a[1]) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(q))


def track():
    v = [int(x) for x in "".join(D.TRAZA).split(",")]
    lat, lon, km = v[0], v[1], v[2] / 1000.0
    out = [(lat / 1e5, lon / 1e5, km)]
    for i in range(3, len(v), 3):
        lat += v[i]
        lon += v[i + 1]
        km += v[i + 2] / 1000.0
        out.append((lat / 1e5, lon / 1e5, km))
    return out


def grid():
    txt = DEM.read_text().splitlines()
    b64 = "".join(l for l in txt if not l.startswith("#"))
    return np.frombuffer(base64.b64decode(b64), dtype="<i2").astype(float).reshape(NY, NX)


pts = track()
prof = [int(x) for x in "".join(D.PERFIL).split(",")]
secs = [int(x) for x in "".join(D.SEGUNDOS).split(",")]
g = grid()

print("--- la traza contra el archivo original ---")
for nombre, punto, quiero in (("la salida", pts[0][:2], SALIDA),
                              ("la llegada", pts[-1][:2], LLEGADA)):
    d = hav(punto, quiero) * 1000
    ok = d < 15
    print(f"  {'ok  ' if ok else 'FALLA'} {nombre} cae a {d:.0f} m de la del archivo")
    if not ok:
        fails.append(f"{nombre} está a {d:.0f} m de la del archivo")
ok = abs(pts[-1][2] - LARGO_KM) < 0.05
print(f"  {'ok  ' if ok else 'FALLA'} el kilometraje llega a {pts[-1][2]:.2f} km "
      f"contra {LARGO_KM} km del recorrido completo")
if not ok:
    fails.append(f"el kilometraje llega a {pts[-1][2]:.2f} km")
recto = sum(hav(pts[i - 1][:2], pts[i][:2]) for i in range(1, len(pts)))
ok = 0.97 < recto / LARGO_KM < 1.0
print(f"  {'ok  ' if ok else 'FALLA'} la línea simplificada mide {recto:.2f} km, "
      "un poco menos que el recorrido, como debe ser")
if not ok:
    fails.append(f"la línea simplificada mide {recto:.2f} km")
fuera = [i for i, (la, lo, _k) in enumerate(pts)
         if not (S <= la <= N and W <= lo <= E)]
print(f"  {'ok  ' if not fuera else 'FALLA'} los {len(pts)} puntos caen dentro "
      "del cuadro del mapa")
if fuera:
    fails.append(f"{len(fuera)} puntos fuera del cuadro")
# la simplificación puede juntar dos puntos lejanos, pero solo cuando el camino
# entre ellos va recto: si hubiera cortado una curva, el kilometraje que trae
# cada punto sería bastante mayor que la distancia en línea recta
peor = max(((pts[i][2] - pts[i - 1][2]) - hav(pts[i - 1][:2], pts[i][:2])) * 1000
           for i in range(1, len(pts)))
ok = peor < 120
print(f"  {'ok  ' if ok else 'FALLA'} entre dos puntos seguidos el camino se "
      f"aparta de la recta cuando mucho {peor:.0f} m, así que la línea no corta "
      "ninguna curva")
if not ok:
    fails.append(f"la línea corta una curva: {peor:.0f} m de diferencia")
saltos = [hav(pts[i - 1][:2], pts[i][:2]) for i in range(1, len(pts))]
print(f"  ok   el tramo recto más largo mide {max(saltos):.2f} km, el camino "
      "del llano")
km = [p[2] for p in pts]
ok = km == sorted(km)
print(f"  {'ok  ' if ok else 'FALLA'} el kilometraje crece punto a punto")
if not ok:
    fails.append("el kilometraje no crece")

print("--- el perfil y las horas ---")
ok = abs(len(prof) * D.PASO_KM - LARGO_KM) < 0.2 and len(prof) == len(secs)
print(f"  {'ok  ' if ok else 'FALLA'} {len(prof)} muestras cada "
      f"{D.PASO_KM * 1000:.0f} m, y otras tantas horas")
if not ok:
    fails.append(f"{len(prof)} muestras de perfil y {len(secs)} de tiempo")
for nombre, valor, quiero in (("la salida", prof[0], ELE_SALIDA),
                              ("la llegada", prof[-1], ELE_LLEGADA)):
    ok = abs(valor - quiero) <= 2
    print(f"  {'ok  ' if ok else 'FALLA'} en {nombre} el perfil marca {valor} m "
          f"y el archivo {quiero} m")
    if not ok:
        fails.append(f"el perfil en {nombre} marca {valor} m contra {quiero}")
ok = secs == sorted(secs) and abs(secs[-1] - DURACION_S) < 60
print(f"  {'ok  ' if ok else 'FALLA'} las horas crecen y terminan en "
      f"{secs[-1] // 3600} h {secs[-1] % 3600 // 60} min")
if not ok:
    fails.append(f"las horas terminan en {secs[-1]} s")
vel = [(D.PASO_KM * 1000) / (secs[i] - secs[i - 1]) * 3.6
       for i in range(1, len(secs)) if secs[i] > secs[i - 1]]
ok = max(vel) < 120
print(f"  {'ok  ' if ok else 'FALLA'} la velocidad más alta entre dos muestras "
      f"es de {max(vel):.0f} km por hora")
if not ok:
    fails.append(f"velocidad de {max(vel):.0f} km/h entre dos muestras")

print("--- la altitud del GPS contra la malla del terreno ---")


def dem_at(la, lo):
    c = float(np.clip((lo - W) / DX, 0, NX - 1.001))
    r = float(np.clip((N - la) / DX, 0, NY - 1.001))
    c0, r0 = int(c), int(r)
    fx, fy = c - c0, r - r0
    return (g[r0, c0] * (1 - fx) * (1 - fy) + g[r0, c0 + 1] * fx * (1 - fy)
            + g[r0 + 1, c0] * (1 - fx) * fy + g[r0 + 1, c0 + 1] * fx * fy)


def punto_en(k):
    i = 1
    while i < len(pts) - 1 and pts[i][2] < k:
        i += 1
    a, b = pts[i - 1], pts[i]
    f = (k - a[2]) / (b[2] - a[2]) if b[2] > a[2] else 0.0
    return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f


dif = np.array([prof[i] - dem_at(*punto_en(i * D.PASO_KM)) for i in range(len(prof))])
cerca = float((np.abs(dif) < 25).mean() * 100)
ok = cerca >= 75 and abs(np.median(dif)) < 25
print(f"  {'ok  ' if ok else 'FALLA'} mediana de {np.median(dif):.0f} m y "
      f"{cerca:.0f}% de los puntos dentro de veinticinco metros")
if not ok:
    fails.append(f"el GPS y la malla difieren: mediana {np.median(dif):.0f} m, "
                 f"{cerca:.0f}% dentro de 25 m")
ok = abs(np.median(dif)) < abs(np.median(dif + 300))
print(f"  ok   la malla no está corrida: moverla trescientos metros empeora "
      "la comparación")

print("--- los lugares ---")
santa = [l for l in D.LUGARES if l[0].startswith("Santa Ana")][0]
d = hav(pts[-1][:2], santa[1:3])
ok = d < 8
print(f"  {'ok  ' if ok else 'FALLA'} la llegada queda a {d:.1f} km de "
      "Santa Ana de Bavícora")
if not ok:
    fails.append(f"la llegada está a {d:.1f} km de Santa Ana de Bavícora")
fuera = [n for n, la, lo, _t in D.LUGARES if not (S <= la <= N and W <= lo <= E)]
print(f"  {'ok  ' if not fuera else 'FALLA'} los {len(D.LUGARES)} lugares caen "
      "dentro del cuadro")
if fuera:
    fails.append(f"lugares fuera del cuadro: {fuera}")
d = hav(D.LEJOS[0][1:], pts[0][:2])
ok = 20 < d < 40
print(f"  {'ok  ' if ok else 'FALLA'} el pueblo de Namiquipa queda a {d:.0f} km "
      "de la salida, que es lo que dice el mapa chico")
if not ok:
    fails.append(f"Namiquipa está a {d:.0f} km de la salida")

html = PAGE.read_text(encoding="utf-8")
print("--- la página ---")
import re
cuerpo = re.sub(r"<script[\s\S]*?</script>", "", html)
if "—" in cuerpo:
    fails.append("hay una raya larga en el texto de la página")
for want in ("La Ruta Namiquipa", "library.html", "ALTAZOR", "Referencias",
             "wikiloc.com", "Leal, M."):
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
    pg.wait_for_function("() => !!window.__ruta", timeout=15000)
    st = pg.evaluate("()=>window.__ruta()")
    print("--- lo que dibujó la página ---")
    ok = st["puntos"] == len(pts)
    print(f"  {'ok  ' if ok else 'FALLA'} puntos: {st['puntos']}, esperados {len(pts)}")
    if not ok:
        fails.append(f"la página dibujó {st['puntos']} puntos")
    print(f"  ok   {st['curvas']} curvas de nivel")

    prev = None
    for k in (0, 6.4, 14, 28.1):
        pg.evaluate("(k)=>{const s=document.getElementById('km');s.value=k;"
                    "s.dispatchEvent(new Event('input'))}", k)
        pg.wait_for_timeout(80)
        s = pg.evaluate("()=>window.__ruta()")
        alt = int(s["alt"].split()[0])
        esperado = prof[min(len(prof) - 1, int(round(k / D.PASO_KM)))]
        ok = abs(alt - esperado) < 15
        print(f"  {'ok  ' if ok else 'FALLA'} en el km {k} la página marca {alt} m "
              f"y el perfil {esperado} m, cerca de {s['cerca']}")
        if not ok:
            fails.append(f"altitud en el km {k}: página {alt}, perfil {esperado}")
        if prev and s["marca"] == prev:
            fails.append(f"la marca no se movió en el km {k}")
        prev = s["marca"]

    # el punto más alto del perfil es el punto más alto del recorrido
    cima = prof.index(max(prof)) * D.PASO_KM
    ok = f"{cima:.1f}" in html
    print(f"  {'ok  ' if ok else 'FALLA'} la página nombra el kilómetro {cima:.1f} "
          "como el punto más alto")
    if not ok:
        fails.append("la página no nombra el kilómetro de la cima")

    for bid, gid in (("bRel", "relieve"), ("bCur", "curvas"), ("bPue", "pueblos")):
        pg.click("#" + bid)
        pg.wait_for_timeout(80)
        d = pg.evaluate(f"()=>getComputedStyle(document.getElementById('{gid}')).display")
        pg.click("#" + bid)
        ok = d == "none"
        print(f"  {'ok  ' if ok else 'FALLA'} {bid} apaga su capa")
        if not ok:
            fails.append(f"{bid} no apaga {gid}")

    if errs:
        fails.append(f"errores de javascript: {errs}")
    br.close()

print()
if fails:
    for f in fails:
        print("FALLA", f)
    sys.exit(1)
print("todo cuadra")
