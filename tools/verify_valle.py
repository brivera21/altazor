"""Comprueba valle-santa-maria.html contra sus datos y contra su dibujo.

  malla       la altitud de dieciséis lugares contra la que trae el gacetero
              de GeoNames, que sale de otro modelo de elevación, y la de tres
              pueblos contra la altitud publicada del censo
  el río      corre hacia el norte y va perdiendo altura; el perfil de la
              página es el mismo que sale de la malla
  caminos     las tres clases y nada más, todo dentro del cuadro
  lugares     todos dentro del cuadro, y las cuatro cifras de población son
              las mismas que lleva el-terrero.html
  la página   responde por lo que dibujó, en el navegador

Uso: pip install playwright && python3 verify_valle.py
"""
import base64
import math
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
PAGE = HERE.parent / "valle-santa-maria.html"
DEM = HERE / "data" / "valle_dem.txt"
OSM = HERE / "data" / "valle_osm.txt"
fails = []

W, E, S, N = -107.58, -107.22, 29.05, 29.40
NX, NY, DX = 241, 234, 0.0015

# Altitud según el gacetero de GeoNames, consultado por el buscador de
# Open-Meteo. Viene de otro modelo de elevación que el de la página.
GEONAMES = {
    "El Terrero": 1853, "El Molino": 1848, "Namiquipa": 1835, "El Oso": 1930,
    "Arroyo de Encinos": 1924, "El Pacífico": 1864, "Oriente": 1854,
    "Armera": 1832, "La Guajolota": 1962, "Granja de Pinos": 1989,
    "Los Cerritos de Abajo": 1890, "Santa Gertrudis de Abajo": 1952,
    "Rancho de Gracia": 1809, "Rancho Peña Rajada": 1811,
    "Granja Casavantes": 1903, "Santa Gertrudis de Arriba": 1999,
    "Rancho el Pedregal": 1815,
}
# Altitud y población publicadas, tecleadas aparte de el-terrero.html
PUBLICADO = {"Namiquipa": (1842, 1723), "El Terrero": (1854, 2752),
             "El Molino": (1848, 2272), "Independencia (Cologachi)": (1951, 920)}


def hav(a, b):
    R = 6371.0088
    r = math.radians
    q = (math.sin(r(b[0] - a[0]) / 2) ** 2 + math.cos(r(a[0])) * math.cos(r(b[0]))
         * math.sin(r(b[1] - a[1]) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(q))


def malla():
    txt = DEM.read_text().splitlines()
    cab = [l for l in txt if l.startswith("#")]
    b64 = "".join(l for l in txt if not l.startswith("#"))
    g = np.frombuffer(base64.b64decode(b64), dtype="<i2").astype(float)
    return g.reshape(NY, NX), cab


def leer_osm():
    lug, cam, agua = [], [], []
    for line in OSM.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        c = line.split("\t")
        if c[0] == "L":
            lug.append(dict(n=c[1], t=c[2], la=float(c[3]), lo=float(c[4])))
        else:
            v = [int(x) for x in c[3].split(",")]
            lon, lat = v[0], v[1]
            pts = [(lon / 1e5, lat / 1e5)]
            for i in range(2, len(v), 2):
                lon += v[i]
                lat += v[i + 1]
                pts.append((lon / 1e5, lat / 1e5))
            (cam if c[0] == "C" else agua).append(dict(c=c[1], n=c[2] or None, g=pts))
    return lug, cam, agua


g, cab = malla()
lug, cam, agua = leer_osm()
print("--- los archivos de datos ---")
ok = g.shape == (NY, NX) and f"NX={NX}" in " ".join(cab)
print(f"  {'ok  ' if ok else 'FALLA'} la malla es de {g.shape[1]} por {g.shape[0]}, "
      f"de {g.min():.0f} a {g.max():.0f} m")
if not ok:
    fails.append(f"la malla mide {g.shape}")
print(f"  ok   {len(lug)} lugares, {len(cam)} caminos y {len(agua)} corrientes")


def altura(la, lo):
    c = float(np.clip((lo - W) / DX, 0, NX - 1.001))
    r = float(np.clip((N - la) / DX, 0, NY - 1.001))
    c0, r0 = int(c), int(r)
    fx, fy = c - c0, r - r0
    return (g[r0, c0] * (1 - fx) * (1 - fy) + g[r0, c0 + 1] * fx * (1 - fy)
            + g[r0 + 1, c0] * (1 - fx) * fy + g[r0 + 1, c0 + 1] * fx * fy)


print("--- la malla contra otras altitudes ---")
dif, faltan = [], []
for l in lug:
    if l["n"] in GEONAMES:
        dif.append(altura(l["la"], l["lo"]) - GEONAMES[l["n"]])
dif = np.array(dif)
ok = len(dif) >= 15 and abs(np.median(dif)) < 20 and (np.abs(dif) < 40).mean() >= 0.8
print(f"  {'ok  ' if ok else 'FALLA'} contra GeoNames, en {len(dif)} lugares: "
      f"mediana {np.median(dif):+.0f} m y {(np.abs(dif) < 40).mean() * 100:.0f}% "
      "dentro de cuarenta metros")
if not ok:
    fails.append(f"la malla difiere de GeoNames: mediana {np.median(dif):+.0f} m")
for n, (alt, _pob) in PUBLICADO.items():
    p = next((x for x in lug if x["n"] == n), None)
    if not p:
        fails.append(f"{n} no está en los datos")
        continue
    d = altura(p["la"], p["lo"]) - alt
    ok = abs(d) < 30
    print(f"  {'ok  ' if ok else 'FALLA'} en {n} la malla marca "
          f"{altura(p['la'], p['lo']):.0f} m y lo publicado son {alt} m")
    if not ok:
        fails.append(f"en {n} la malla marca {altura(p['la'], p['lo']):.0f} m contra {alt}")

print("--- el río ---")
rio = []
for a in sorted([a for a in agua if a["c"] == "river"], key=lambda a: a["g"][0][1]):
    for p in a["g"]:
        if not rio or p != rio[-1]:
            rio.append(p)
rio = [(lo, la) for lo, la in rio if S <= la <= N and W <= lo <= E]
km, acc = [0.0], 0.0
for i in range(1, len(rio)):
    acc += hav((rio[i - 1][1], rio[i - 1][0]), (rio[i][1], rio[i][0]))
    km.append(acc)
alt = np.array([altura(la, lo) for lo, la in rio])
ok = rio[0][1] < rio[-1][1]
print(f"  {'ok  ' if ok else 'FALLA'} entra por el sur en {rio[0][1]:.3f} y sale "
      f"por el norte en {rio[-1][1]:.3f}")
if not ok:
    fails.append("el río no va de sur a norte")
ok = alt[0] > alt[-1] and 20 < alt[0] - alt[-1] < 400
print(f"  {'ok  ' if ok else 'FALLA'} baja de {alt[0]:.0f} a {alt[-1]:.0f} m "
      f"en {acc:.0f} km")
if not ok:
    fails.append(f"el río va de {alt[0]:.0f} a {alt[-1]:.0f} m")
# la pendiente media, y ninguna subida grande contra corriente
subidas = np.diff(alt)
ok = subidas.max() < 40
print(f"  {'ok  ' if ok else 'FALLA'} la subida más grande entre dos puntos "
      f"seguidos es de {subidas.max():.0f} m, ruido de la malla")
if not ok:
    fails.append(f"el río sube {subidas.max():.0f} m en un tramo")

print("--- caminos, agua y lugares ---")
clases = {c["c"] for c in cam}
ok = clases == {"carretera", "brecha", "calle"}
print(f"  {'ok  ' if ok else 'FALLA'} las clases de camino son {sorted(clases)}")
if not ok:
    fails.append(f"clases de camino inesperadas: {clases}")
# Overpass entrega el trazo completo de todo camino que toque el cuadro, así
# que unos cuantos siguen de largo hacia afuera y el mapa los corta. Lo que sí
# tiene que cumplirse es que cada trazo pase por dentro y que ninguno se vaya
# lejísimos.
sin_tocar = [c for c in cam + agua
             if not any(S <= la <= N and W <= lo <= E for lo, la in c["g"])]
print(f"  {'ok  ' if not sin_tocar else 'FALLA'} los {len(cam) + len(agua)} trazos "
      "pasan por dentro del cuadro")
if sin_tocar:
    fails.append(f"{len(sin_tocar)} trazos no tocan el cuadro")
salida = max(max(max(S - la, la - N, W - lo, lo - E) for lo, la in c["g"])
             for c in cam + agua)
ok = salida < 0.15
print(f"  {'ok  ' if ok else 'FALLA'} el que más se sale llega a "
      f"{salida:.3f} grados afuera, y el mapa lo corta")
if not ok:
    fails.append(f"un trazo se sale {salida:.3f} grados del cuadro")
fuera = [l["n"] for l in lug if not (S <= l["la"] <= N and W <= l["lo"] <= E)]
print(f"  {'ok  ' if not fuera else 'FALLA'} los {len(lug)} lugares caen dentro "
      "del cuadro")
if fuera:
    fails.append(f"lugares fuera del cuadro: {fuera}")

html = PAGE.read_text(encoding="utf-8")
print("--- la página ---")
cuerpo = re.sub(r"<script[\s\S]*?</script>", "", html)
if "\u2014" in cuerpo.replace("&mdash;", ""):
    fails.append("hay una raya larga en el texto de la página")
for want in ("El valle del Santa María", "library.html", "ALTAZOR", "Referencias",
             "OpenStreetMap", "2020"):
    ok = want in html
    print(f"  {'ok  ' if ok else 'FALLA'} la página trae {want!r}")
    if not ok:
        fails.append(f"a la página le falta {want!r}")
for n, (_alt, pob) in PUBLICADO.items():
    if n in ("Namiquipa", "El Terrero"):
        ok = f"{pob:,}" in html
        print(f"  {'ok  ' if ok else 'FALLA'} la página trae los {pob:,} "
              f"habitantes de {n}")
        if not ok:
            fails.append(f"la página no trae la población de {n}")

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("\nplaywright no está instalado")
    sys.exit(1)

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1280, "height": 1100})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.resolve().as_uri())
    pg.wait_for_function("() => !!window.__valle", timeout=15000)
    st = pg.evaluate("()=>{const v=window.__valle(); return {lugares:v.lugares,"
                     "caminos:v.caminos,agua:v.agua,curvas:v.curvas,rio:v.rio}}")
    print("--- lo que dibujó la página ---")
    for k, want in (("lugares", len(lug)), ("caminos", len(cam)), ("agua", len(agua))):
        ok = st[k] == want
        print(f"  {'ok  ' if ok else 'FALLA'} {k}: {st[k]}, esperados {want}")
        if not ok:
            fails.append(f"la página dibujó {st[k]} {k}, esperados {want}")
    print(f"  ok   {st['curvas']} curvas de nivel")
    ok = abs(st["rio"]["km"] - acc) < 0.5 and st["rio"]["n"] == len(rio)
    print(f"  {'ok  ' if ok else 'FALLA'} el río de la página mide "
          f"{st['rio']['km']:.1f} km en {st['rio']['n']} puntos")
    if not ok:
        fails.append(f"el río de la página mide {st['rio']['km']:.1f} km")

    # la malla que lee el cursor contra la malla completa
    peor = 0
    for l in lug[:12]:
        v = pg.evaluate("([la,lo])=>window.__valle().altura(la,lo)", [l["la"], l["lo"]])
        peor = max(peor, abs(v - altura(l["la"], l["lo"])))
    ok = peor < 40
    print(f"  {'ok  ' if ok else 'FALLA'} la malla que lee el cursor se aparta "
          f"de la completa cuando mucho {peor:.0f} m")
    if not ok:
        fails.append(f"la malla del cursor se aparta {peor:.0f} m")

    # el cursor sobre un pueblo llena el tablero
    # el perfil viaja pegado al pie de la pantalla, así que el pueblo se
    # centra antes de poner el cursor encima
    caja = pg.evaluate("()=>{const c=document.querySelector('#lugares circle[data-i]');"
                       "c.scrollIntoView({block:'center'});"
                       "const r=c.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]}")
    pg.mouse.move(caja[0], caja[1])
    pg.wait_for_timeout(150)
    lee = pg.evaluate("()=>[document.getElementById('rAlt').textContent,"
                      "document.getElementById('rLug').textContent,"
                      "document.getElementById('rRio').textContent]")
    ok = lee[0].endswith("m") and lee[1] and lee[2].endswith("m")
    print(f"  {'ok  ' if ok else 'FALLA'} el cursor sobre un pueblo lee "
          f"{lee[0]!r}, {lee[1]!r} y {lee[2]!r}")
    if not ok:
        fails.append(f"el tablero lee {lee}")

    for bid, gid in (("bRel", "relieve"), ("bCur", "curvas"), ("bCam", "caminos"),
                     ("bAgua", "agua"), ("bLug", "lugares")):
        pg.click("#" + bid)
        pg.wait_for_timeout(70)
        d = pg.evaluate(f"()=>getComputedStyle(document.getElementById('{gid}')).display")
        pg.click("#" + bid)
        ok = d == "none"
        print(f"  {'ok  ' if ok else 'FALLA'} {bid} apaga su capa")
        if not ok:
            fails.append(f"{bid} no apaga {gid}")

    print("--- lo que se añadió ---")

    def ok_(cond, msg):
        print(f"  {'ok  ' if cond else 'FALLA'} {msg}")
        if not cond:
            fails.append(msg)

    # los pueblos sobre el río quedan marcados en el perfil
    v = pg.evaluate("()=>__valle()")
    nombres = [x[0] for x in v["pueblosPerfil"]]
    ok_(all(n in nombres for n in ("El Terrero", "El Molino", "Namiquipa")),
        f"el perfil marca a {', '.join(nombres)}")
    kms = dict(v["pueblosPerfil"])
    ok_(kms.get("El Terrero", 99) < kms.get("El Molino", 0) < kms.get("Namiquipa", 0),
        "río abajo van El Terrero, El Molino y Namiquipa, en ese orden")

    # el perfil se arrastra: el punto del mapa cae sobre el río en ese km
    pg.evaluate("()=>document.getElementById('perfil').scrollIntoView({block:'center'})")
    r = pg.evaluate("()=>{const b=document.getElementById('perfil').getBoundingClientRect();"
                    "return [b.x,b.y,b.width,b.height]}")
    x0 = r[0] + r[2] * (46 + 0.5 * (900 - 70)) / 900
    pg.mouse.move(x0, r[1] + r[3] / 2)
    pg.mouse.down()
    pg.mouse.move(x0 + 5, r[1] + r[3] / 2)
    pg.mouse.up()
    v = pg.evaluate("()=>__valle()")
    ok_(v["km"] is not None and abs(v["km"] - 0.5 * v["rio"]["km"]) < 1.5,
        f"el perfil arrastrado a la mitad pone el punto en el km {v['km']:.1f}")
    en = pg.evaluate("""()=>{const p=document.getElementById('rioPunto');
        const x=+p.getAttribute('cx'), y=+p.getAttribute('cy');
        let m=1e9; for(let i=0;i<RIO.x.length;i++) m=Math.min(m,Math.hypot(RIO.x[i]-x,RIO.y[i]-y));
        return m;}""")
    ok_(en < 3, f"el punto del mapa está sobre el río (a {en:.1f} unidades de su trazo)")

    # Río abajo corre y llega al final
    pg.click("#bRio")
    pg.wait_for_timeout(500)
    v1 = pg.evaluate("()=>__valle()")
    ok_(v1["corre"] and pg.evaluate("()=>bRio.textContent") == "Pausa", "Río abajo corre y el botón dice Pausa")
    pg.wait_for_timeout(5200)
    v2 = pg.evaluate("()=>__valle()")
    ok_(not v2["corre"] and abs(v2["km"] - v2["rio"]["km"]) < 0.01,
        f"y se detiene al final, en el km {v2['km']:.1f}")

    # un clic fija un lugar y tira su recta a El Terrero
    i = pg.evaluate("()=>LUG.findIndex(l=>l.n==='Namiquipa')")
    pg.evaluate(f"()=>document.querySelector('#lugares circle[data-i=\"{i}\"]')"
                ".dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    v = pg.evaluate("()=>__valle()")
    a, b = pg.evaluate("()=>[LUG.find(l=>l.n==='Namiquipa'),LUG.find(l=>l.n==='El Terrero')]"
                       ".map(l=>[l.la,l.lo])")
    d = hav(a, b)
    ok_(v["fijo"] == i and v["recta"] == 1 and f"{d:.1f} km en recta" in v["lugSub"],
        f"Namiquipa fijada: {v['lugSub']!r} (a mano: {d:.1f} km)")
    pg.keyboard.press("Escape")
    ok_(pg.evaluate("()=>__valle().fijo") is None, "Escape suelta el lugar")

    # arriba y abajo recorren los lugares por altitud
    pg.focus("#map")
    pg.keyboard.press("ArrowUp")
    a = pg.evaluate("()=>LUG[__valle().fijo].h")
    pg.keyboard.press("ArrowUp")
    b = pg.evaluate("()=>LUG[__valle().fijo].h")
    ok_(b >= a, f"la flecha arriba sube de {a} m a {b} m")
    pg.keyboard.press("Escape")

    # los pisos de altura entran poco a poco
    pg.click("#bPisos")
    pg.wait_for_timeout(300)
    mid = pg.evaluate("()=>__valle().pisos")
    pg.wait_for_timeout(900)
    fin = pg.evaluate("()=>__valle().pisos")
    ok_(0 < mid < 1 and fin == 1, f"los pisos de altura entran de {mid:.2f} a {fin:.0f}")

    ph = br.new_page(viewport={"width": 390, "height": 844})
    ph.goto(PAGE.resolve().as_uri())
    ph.wait_for_timeout(600)
    ov = ph.evaluate("document.documentElement.scrollWidth - innerWidth")
    ok_(ov == 0, f"en un teléfono nada se sale de la pantalla ({ov}px)")
    w = ph.evaluate("document.getElementById('map').getBoundingClientRect().width")
    ok_(w >= 600, f"en un teléfono el mapa guarda {w:.0f}px de ancho y se recorre de lado")

    if errs:
        fails.append(f"errores de javascript: {errs}")
    br.close()

print()
if fails:
    for f in fails:
        print("FALLA", f)
    sys.exit(1)
print("todo cuadra")
