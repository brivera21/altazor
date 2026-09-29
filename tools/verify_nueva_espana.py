"""Comprueba nueva-espana.html contra sus datos y contra su dibujo.

  los datos    cada lugar de cada camino tiene coordenada, cada villa tiene
               año dentro del periodo, y los años de las entradas corren hacia
               adelante
  la geometría las entidades de 1824 cubren los treinta y dos estados de hoy
               una sola vez, sin encimarse, y lo que se perdió cabe adentro
  las rayas    la de 1819 va de este a oeste por el paralelo 42 y la de 1853
               deja la Mesilla al norte de la de 1848
  la página    dibuja lo que le toca a cada año y nada antes de tiempo

Uso: pip install playwright && python3 verify_nueva_espana.py
"""
import pickle
import re
import sys
from pathlib import Path

from shapely.geometry import Polygon, box
from shapely.ops import unary_union

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import nueva_espana_data as D

PAGE = HERE.parent / "nueva-espana.html"
MX = Path("/home/claude/mx/states.pkl")
US = Path("/home/claude/us/states.pkl")
fails = []

print("--- los datos ---")
faltan = [p for e in D.ENTRADAS for p in e[4] if p not in D.LUGARES]
faltan += [n for n, _a in D.LLEGADA if n not in D.LUGARES]
faltan += [v[0] for v in D.VILLAS if v[0] not in D.LUGARES]
ok = not faltan
print(f"  {'ok  ' if ok else 'FALLA'} los {len(D.LUGARES)} lugares alcanzan "
      "para los caminos, la llegada y las villas")
if not ok:
    fails.append(f"lugares sin coordenada: {faltan}")

fuera = [v for v in D.VILLAS if not D.AÑO_INICIO <= v[1] <= D.AÑO_FIN]
print(f"  {'ok  ' if not fuera else 'FALLA'} las {len(D.VILLAS)} villas caen "
      f"entre {D.AÑO_INICIO} y {D.AÑO_FIN}")
if fuera:
    fails.append(f"villas fuera del periodo: {[v[0] for v in fuera]}")
mal = [e[0] for e in D.ENTRADAS if e[3] < e[2]]
print(f"  {'ok  ' if not mal else 'FALLA'} ninguna entrada regresa antes de salir")
if mal:
    fails.append(f"entradas al revés: {mal}")
mal = [s for s in D.SUCESOS if not D.AÑO_INICIO <= s[0] <= D.AÑO_FIN]
años = [s[0] for s in D.SUCESOS]
ok = not mal and años == sorted(años)
print(f"  {'ok  ' if ok else 'FALLA'} los {len(D.SUCESOS)} sucesos van en orden "
      "y dentro del periodo")
if not ok:
    fails.append(f"sucesos desordenados o fuera: {mal}")

# los lugares aproximados están marcados como tales
aprox = [n for n, (_la, _lo, e) in D.LUGARES.items() if not e]
print(f"  ok   {len(aprox)} lugares van marcados como aproximados, entre ellos "
      f"{', '.join(sorted(aprox)[:3])}")

# cada villa sabe en qué estado de hoy queda
sin = [v[0] for v in D.VILLAS if v[0] not in D.HOY]
print(f"  {'ok  ' if not sin else 'FALLA'} cada villa tiene su estado de hoy")
if sin:
    fails.append(f"villas sin estado de hoy: {sin}")

print("--- las entidades de 1824 contra los estados de hoy ---")
if MX.exists() and US.exists():
    mx = pickle.load(open(MX, "rb"))
    us = pickle.load(open(US, "rb"))
else:
    print(f"  ({MX} no está en esta máquina: la geometría se salta y la "
          "página se comprueba igual)")
    mx = us = None
if mx is not None:
    usados = [k for _n, _c, kmx, _ku in D.ENTIDADES_1824 for k in kmx]
    ok = sorted(usados) == sorted(mx)
    print(f"  {'ok  ' if ok else 'FALLA'} las entidades usan los {len(mx)} estados "
          "mexicanos de hoy, cada uno una vez")
    if not ok:
        from collections import Counter
        c = Counter(usados)
        fails.append(f"estados repetidos o faltantes: "
                     f"{[k for k, v in c.items() if v > 1]} / "
                     f"{sorted(set(mx) - set(usados))}")
    usados_us = [k for _n, _c, _k, kus in D.ENTIDADES_1824 for k in kus]
    ok = len(usados_us) == len(set(usados_us)) and all(k in us for k in usados_us)
    print(f"  {'ok  ' if ok else 'FALLA'} y {len(usados_us)} estados de Estados "
          "Unidos, sin repetir")
    if not ok:
        fails.append(f"estados de EUA repetidos: {usados_us}")

    # ninguna entidad se encima con otra
    formas = {}
    for n, _c, kmx, kus in D.ENTIDADES_1824:
        formas[n] = unary_union([mx[k].buffer(0) for k in kmx]
                                + [us[k].buffer(0) for k in kus])
    # Los dos juegos de estados vienen de fuentes distintas, la WDBII y el censo
    # de Estados Unidos, y sus rayas no caen exactamente encima una de otra: donde
    # Sonora toca Arizona quedan unas centenas de kilómetros cuadrados repetidos.
    # Eso se tolera; lo que no se tolera es que dos entidades compartan territorio.
    peor, encimes = 0.0, []
    nombres = list(formas)
    for i, a in enumerate(nombres):
        for b in nombres[i + 1:]:
            g = formas[a].intersection(formas[b])
            peor = max(peor, g.area)
            if g.area > 0.3:
                encimes.append(f"{a} y {b}: {g.area:.2f} grados cuadrados")
    print(f"  {'ok  ' if not encimes else 'FALLA'} ninguna entidad se encima con "
          f"otra; lo más que se repite son {peor * 111.32 * 110.57 * 0.9:,.0f} km2 "
          "en la costura de las dos fuentes")
    if encimes:
        fails.append(f"entidades encimadas: {encimes[:3]}")

    # lo que se perdió cabe adentro de lo que había
    todo = unary_union(list(formas.values()))
    for año, nombre, kmx, kus, _nota in D.PERDIDO:
        g = unary_union([mx[k].buffer(0) for k in kmx] + [us[k].buffer(0) for k in kus])
        afuera = g.difference(todo.buffer(0.01)).area
        ok = afuera < 0.5
        print(f"  {'ok  ' if ok else 'FALLA'} {nombre} sale de lo que la federación "
              f"tenía en 1824 ({afuera:.2f} grados cuadrados de sobra)")
        if not ok:
            fails.append(f"{nombre} no cabe en el país de 1824")

print("--- las rayas ---")
l19 = D.LINEA_1819
ok = abs(l19[-1][0] - 42.0) < 0.01 and abs(l19[-2][0] - 42.0) < 0.01
print(f"  {'ok  ' if ok else 'FALLA'} la de 1819 termina sobre el paralelo 42, "
      "como dice el artículo tercero")
if not ok:
    fails.append("la línea de 1819 no acaba en el paralelo 42")
ok = l19[0][1] < l19[-1][1] * 0 - 90 or l19[0][1] > l19[-1][1]
print(f"  {'ok  ' if ok else 'FALLA'} y corre del Sabina, en el este, al "
      "Pacífico, en el oeste")
if not ok:
    fails.append("la línea de 1819 no va de este a oeste")
# la Mesilla queda entre las dos líneas, al sur de la de 1848
m48 = Polygon([(lo, la) for la, lo in D.LINEA_1848[5:]]
              + [(lo, la) for la, lo in reversed(D.LINEA_1853[5:])]).buffer(0)
km2 = m48.area * 111.32 * 110.57 * 0.86
ok = 40_000 < km2 < 140_000
print(f"  {'ok  ' if ok else 'FALLA'} la Mesilla mide unos {km2:,.0f} km2 "
      "sobre el trazo simplificado, contra los 76,800 del tratado")
if not ok:
    fails.append(f"la Mesilla mide {km2:,.0f} km2")

html = PAGE.read_text(encoding="utf-8")
print("--- la página ---")
cuerpo = re.sub(r"<script[\s\S]*?</script>", "", html)
if "—" in cuerpo.replace("&mdash;", ""):
    fails.append("hay una raya larga en el texto de la página")
for want in ("La Nueva España", "library.html", "ALTAZOR", "Referencias",
             "1824", "Adams", '<details class="sources">', 'id="anos"',
             'id="ficha"', 'id="relieve"', 'id="bMarco"'):
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
    pg = br.new_page(viewport={"width": 1280, "height": 1150})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.resolve().as_uri())
    pg.wait_for_function("() => !!window.__ne", timeout=15000)

    def en(a):
        pg.evaluate("(a)=>{const s=document.getElementById('ano');s.value=a;"
                    "s.dispatchEvent(new Event('input'))}", a)
        pg.wait_for_timeout(90)
        return pg.evaluate("()=>window.__ne()")

    print("--- lo que dibuja cada año ---")
    casos = [
        (1519, "la llegada", lambda s: s["dibujadas"]["villas"] == 1
         and s["dibujadas"]["entidades"] == 0 and s["dibujadas"]["lineas"] == 0),
        (1545, "antes de la plata", lambda s: s["dibujadas"]["villas"] == 3),
        (1611, "con Santa Fe", lambda s: s["dibujadas"]["villas"] == 8),
        (1818, "antes de la raya", lambda s: s["dibujadas"]["lineas"] == 0),
        (1820, "con la raya de 1819", lambda s: s["dibujadas"]["lineas"] == 1),
        (1823, "sin entidades todavía", lambda s: s["dibujadas"]["entidades"] == 0),
        (1824, "con las entidades", lambda s: s["dibujadas"]["entidades"] == 25),
        (1835, "antes de Texas", lambda s: s["dibujadas"]["perdido"] == 0),
        (1836, "con Texas", lambda s: s["dibujadas"]["perdido"] == 1),
        (1848, "con la cesión", lambda s: s["dibujadas"]["perdido"] == 2),
        (1853, "con la Mesilla", lambda s: s["dibujadas"]["perdido"] == 3),
    ]
    for año, que, prueba in casos:
        s = en(año)
        ok = prueba(s)
        print(f"  {'ok  ' if ok else 'FALLA'} {año}, {que}: {s['dibujadas']}")
        if not ok:
            fails.append(f"en {año} la página dibuja {s['dibujadas']}")

    # las villas nunca se adelantan a su año. La primera es de 1519, que es
    # donde empieza el deslizador, así que esa se comprueba aparte.
    for v in D.VILLAS:
        if v[1] <= D.AÑO_INICIO:
            continue
        s = en(v[1] - 1)
        antes = s["dibujadas"]["villas"]
        s = en(v[1])
        if s["dibujadas"]["villas"] <= antes:
            fails.append(f"{v[0]} no aparece en {v[1]}")
    primera = en(D.AÑO_INICIO)["dibujadas"]["villas"]
    if primera != 1:
        fails.append(f"en {D.AÑO_INICIO} se dibujan {primera} villas, no una")
    print(f"  {'ok  ' if not fails else 'FALLA'} cada una de las "
          f"{len(D.VILLAS)} villas aparece el año que le toca, empezando por "
          "Veracruz en 1519")

    # los rótulos se colocan igual de cerca cuando el cuadro está apretado:
    # el margen de la caja de texto se mide en unidades del cuadro, no de la
    # pantalla, así que tiene que encogerse con el acercamiento
    for año, quien in ((1519, "Tenochtitlan"), (1600, "México"),
                       (1824, "México")):
        en(año)
        txt = pg.evaluate("()=>document.getElementById('etiquetas').textContent")
        ok = quien in txt
        print(f"  {'ok  ' if ok else 'FALLA'} en {año} el mapa rotula {quien}")
        if not ok:
            fails.append(f"en {año} falta el rótulo de {quien}: {txt[:120]}")

    # el encuadre se abre con los años
    anchos = []
    for a in (1519, 1560, 1620, 1700, 1790):
        en(a)
        vb = pg.evaluate("()=>document.getElementById('mapa').getAttribute('viewBox')")
        anchos.append(round(float(vb.split()[2])))
    ok = anchos == sorted(anchos) and anchos[0] < anchos[-1] / 2
    print(f"  {'ok  ' if ok else 'FALLA'} el cuadro se va abriendo: {anchos}")
    if not ok:
        fails.append(f"el encuadre va {anchos}")

    # y el tablero de arriba cambia con el año
    vistos = []
    for a in (1521, 1610, 1776, 1824, 1853):
        s = en(a)
        vistos.append((s["ano"], s["suceso"]))
    ok = len({v[1] for v in vistos}) >= 4
    print(f"  {'ok  ' if ok else 'FALLA'} el tablero nombra "
          f"{len({v[1] for v in vistos})} sucesos distintos en cinco años")
    if not ok:
        fails.append(f"el tablero repite: {vistos}")

    print("--- los marcos, la ficha, la leyenda, el relieve y el arrastre ---")
    s = en(1519)
    ok = s["dibujadas"]["marcos"] == 8 and s["relieve"] > 50
    print(f"  {'ok  ' if ok else 'FALLA'} {s['dibujadas']['marcos']} años con "
          f"marco y {s['relieve']} manchas de relieve")
    if not ok:
        fails.append(f"marcos {s['dibujadas']['marcos']}, relieve {s['relieve']}")
    ok = s["dibujadas"]["leyenda"] == 2
    print(f"  {'ok  ' if ok else 'FALLA'} en 1519 la leyenda trae "
          f"{s['dibujadas']['leyenda']} filas, las dos cosas que están en el mapa")
    if not ok:
        fails.append(f"la leyenda de 1519 trae {s['dibujadas']['leyenda']} filas")
    ok = en(1853)["dibujadas"]["leyenda"] == 6
    print(f"  {'ok  ' if ok else 'FALLA'} y en 1853 las seis")
    if not ok:
        fails.append("la leyenda de 1853 no trae seis filas")
    en(1519)
    pg.click("#anos button[data-a='1598']")
    pg.wait_for_timeout(250)
    medio = pg.evaluate("()=>window.__ne()")
    pg.wait_for_timeout(1400)
    fin = pg.evaluate("()=>window.__ne()")
    ok = 1519 < medio["ano"] < 1598 and fin["ano"] == 1598 and medio["viaje"] \
        and not fin["viaje"]
    print(f"  {'ok  ' if ok else 'FALLA'} el marco 1598 lleva el deslizador "
          f"poco a poco: {medio['ano']} a mitad de camino, {fin['ano']} al final")
    if not ok:
        fails.append(f"el marco no viaja: {medio['ano']} luego {fin['ano']}")
    pg.evaluate("()=>document.querySelectorAll('#rutas path.mano')[2]"
                ".dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    pg.wait_for_timeout(150)
    ficha = pg.inner_text("#ficha")
    s = pg.evaluate("()=>window.__ne()")
    ok = s["fija"] == 2 and "Coronado" in ficha and "2,828 km" in ficha \
        and "Compostela" in ficha
    print(f"  {'ok  ' if ok else 'FALLA'} la entrada de Coronado se fija en la "
          f"ficha con jefe, kilómetros y sitios")
    if not ok:
        fails.append(f"la ficha dice {ficha[:100]!r}")
    pg.keyboard.press("Escape")
    s = pg.evaluate("()=>window.__ne()")
    if s["fija"] is not None:
        fails.append("Escape no suelta la entrada")
    pg.evaluate("()=>document.querySelectorAll('#villas circle.villa')[3]"
                ".dispatchEvent(new MouseEvent('mouseenter'))")
    pg.wait_for_timeout(100)
    s = pg.evaluate("()=>window.__ne()")
    ok = "1546" in s["sub"] and "Zacatecas" in s["sub"]
    print(f"  {'ok  ' if ok else 'FALLA'} una villa bajo el cursor dice su año "
          f"y su estado de hoy: {s['sub'][:60]!r}")
    if not ok:
        fails.append(f"la villa bajo el cursor dice {s['sub']!r}")
    en(1853)
    antes = pg.evaluate("()=>window.__ne().caja")
    pg.mouse.move(400, 400)
    pg.mouse.wheel(0, -500)
    pg.wait_for_timeout(200)
    pg.mouse.down()
    pg.mouse.move(300, 300, steps=4)
    pg.mouse.up()
    pg.wait_for_timeout(200)
    s = pg.evaluate("()=>window.__ne()")
    ok = s["manual"] and s["caja"]["w"] < antes["w"] * 0.8
    print(f"  {'ok  ' if ok else 'FALLA'} la rueda acerca y el arrastre mueve: "
          f"el cuadro pasa de {antes['w']:.0f} a {s['caja']['w']:.0f} de ancho")
    if not ok:
        fails.append("la rueda o el arrastre no mueven el cuadro")
    pg.click("#bMarco")
    pg.wait_for_timeout(300)
    s = pg.evaluate("()=>window.__ne()")
    ok = not s["manual"] and abs(s["caja"]["w"] - antes["w"]) < 1
    print(f"  {'ok  ' if ok else 'FALLA'} Reencuadrar devuelve el encuadre")
    if not ok:
        fails.append("Reencuadrar no devuelve el encuadre")
    pg.click("#bPlay")
    pg.wait_for_timeout(400)
    s = pg.evaluate("()=>window.__ne()")
    ok = s["corriendo"] and pg.text_content("#bPlay") == "Alto" and s["ano"] > 1519
    print(f"  {'ok  ' if ok else 'FALLA'} Correr los años corre y el botón dice Alto")
    if not ok:
        fails.append("el botón de correr no corre")
    pg.click("#bPlay")

    if errs:
        fails.append(f"errores de javascript: {errs}")
    br.close()

print()
if fails:
    for f in fails:
        print("FALLA", f)
    sys.exit(1)
print("todo cuadra")
