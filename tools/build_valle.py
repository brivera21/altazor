#!/usr/bin/env python3
"""Genera valle-santa-maria.html: el valle del río Santa María en Namiquipa,
de El Pacífico a Rancho de Gracia, con el relieve debajo.

Los datos están en data/:
  valle_dem.txt   malla de altitudes de unos ciento cincuenta metros de paso,
                  armada con las teselas terrarium de Mapzen sobre AWS Open Data
  valle_osm.txt   lugares, caminos y corrientes de agua de OpenStreetMap,
                  simplificados a tres diezmilésimas de grado

La población es del censo de 2020 y solo se pone donde la hay publicada por
localidad; las cifras son las mismas que usa el-terrero.html.

Uso: python3 build_valle.py
"""

import base64
import io
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

OUT = Path(__file__).parent.parent / "valle-santa-maria.html"
DEM = Path(__file__).parent / "data" / "valle_dem.txt"
OSM = Path(__file__).parent / "data" / "valle_osm.txt"

W, E, S, N = -107.58, -107.22, 29.05, 29.40
NX, NY, DX = 241, 234, 0.0015
LAT0 = 29.22
VW = 900.0
SCALE = VW / ((E - W) * np.cos(np.radians(LAT0)))
VH = (N - S) * SCALE

C_RIO = "#6fb6f5"
C_ARR = "#4d7fa6"
C_CARR = "#e8c07d"
C_BRE = "#a3927a"
C_CALLE = "#8d99a6"
C_PUEBLO = "#7fd4c1"

# INEGI, Censo de Población y Vivienda 2020, cifras por localidad. Son las
# mismas que lleva el-terrero.html, y solo las de las localidades publicadas.
POB2020 = {
    "El Terrero": 2752,
    "El Molino": 2272,
    "Namiquipa": 1723,
    "Independencia (Cologachi)": 920,
}
MUNICIPIO_2020 = 22712      # habitantes del municipio de Namiquipa en 2020

RADIO = {"town": 6.5, "village": 5.0, "hamlet": 3.6, "farm": 3.0,
         "isolated_dwelling": 2.6}


def px(lon):
    return (lon - W) * np.cos(np.radians(LAT0)) * SCALE


def py(lat):
    return (N - lat) * SCALE


def malla():
    txt = DEM.read_text().splitlines()
    b64 = "".join(l for l in txt if not l.startswith("#"))
    return np.frombuffer(base64.b64decode(b64), dtype="<i2").astype(float).reshape(NY, NX)


def leer_osm():
    lugares, caminos, aguas = [], [], []
    for line in OSM.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        campos = line.split("\t")
        if campos[0] == "L":
            lugares.append(dict(n=campos[1], t=campos[2],
                                la=float(campos[3]), lo=float(campos[4])))
        else:
            v = [int(x) for x in campos[3].split(",")]
            lon, lat = v[0], v[1]
            pts = [(lon / 1e5, lat / 1e5)]
            for i in range(2, len(v), 2):
                lon += v[i]
                lat += v[i + 1]
                pts.append((lon / 1e5, lat / 1e5))
            (caminos if campos[0] == "C" else aguas).append(
                dict(c=campos[1], n=campos[2] or None, g=pts))
    return lugares, caminos, aguas


def relieve(g, w=880):
    h = int(round(w * (N - S) / ((E - W) * np.cos(np.radians(LAT0)))))
    fine = np.asarray(Image.fromarray(g.astype("float32"), "F")
                      .resize((w, h), Image.BICUBIC), dtype=float)
    dy_m = (N - S) * 110570.0 / h
    dx_m = (E - W) * 111320.0 * np.cos(np.radians(LAT0)) / w
    gy, gx = np.gradient(fine, dy_m, dx_m)
    slope = np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    az, alt = np.radians(315.0), np.radians(45.0)
    shade = np.clip(np.sin(alt) * np.cos(slope)
                    + np.cos(alt) * np.sin(slope) * np.cos(az - aspect), 0, 1)
    lo, hi = fine.min(), fine.max()
    t = np.clip((fine - lo) / (hi - lo), 0, 1)[..., None]
    bajo = np.array([46.0, 54.0, 48.0])
    medio = np.array([76.0, 74.0, 58.0])
    alto = np.array([120.0, 112.0, 96.0])
    col = np.where(t < 0.45, bajo + (medio - bajo) * (t / 0.45),
                   medio + (alto - medio) * ((t - 0.45) / 0.55))
    rgb = col * (0.45 + 0.75 * shade[..., None])
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB")
    buf = io.BytesIO()
    # el sombreado es una foto, no un dibujo: en jpeg pesa una quinta parte
    im.save(buf, format="JPEG", quality=82, optimize=True, progressive=True)
    return base64.b64encode(buf.getvalue()).decode(), fine


def curvas(fine, step=100):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    h, w = fine.shape
    xs = np.linspace(px(W), px(E), w)
    ys = np.linspace(py(N), py(S), h)
    lo = int(np.ceil(fine.min() / step) * step)
    hi = int(np.floor(fine.max() / step) * step)
    fig = plt.figure()
    cs = plt.contour(xs, ys, fine, levels=list(range(lo, hi + 1, step)))
    out = []
    for level, seg in zip(cs.levels, cs.allsegs):
        for s in seg:
            if len(s) < 12:
                continue
            q = s[::3]
            if len(q) < 6:
                continue
            out.append((int(level),
                        "M" + " ".join(f"{x:.0f},{y:.0f}" for x, y in q)))
    plt.close(fig)
    return out


def hav(a, b):
    R = 6371.0088
    r = math.radians
    q = (math.sin(r(b[0] - a[0]) / 2) ** 2 + math.cos(r(a[0])) * math.cos(r(b[0]))
         * math.sin(r(b[1] - a[1]) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(q))


g = malla()
png, fine = relieve(g)
cur = curvas(fine)
lugares, caminos, aguas = leer_osm()
print(f"malla {g.shape}, de {g.min():.0f} a {g.max():.0f} m; "
      f"{len(lugares)} lugares, {len(caminos)} caminos, {len(aguas)} corrientes, "
      f"{len(cur)} curvas")


def altura(la, lo):
    c = float(np.clip((lo - W) / DX, 0, NX - 1.001))
    r = float(np.clip((N - la) / DX, 0, NY - 1.001))
    c0, r0 = int(c), int(r)
    fx, fy = c - c0, r - r0
    return (g[r0, c0] * (1 - fx) * (1 - fy) + g[r0, c0 + 1] * fx * (1 - fy)
            + g[r0 + 1, c0] * (1 - fx) * fy + g[r0 + 1, c0 + 1] * fx * fy)


# el río, armado de sus dos tramos y recortado al cuadro
rio_pts = []
for a in sorted([a for a in aguas if a["c"] == "river"],
                key=lambda a: a["g"][0][1]):
    for p in a["g"]:
        if not rio_pts or p != rio_pts[-1]:
            rio_pts.append(p)
rio_pts = [(lo, la) for lo, la in rio_pts if S <= la <= N and W <= lo <= E]
rio_km, acc = [0.0], 0.0
for i in range(1, len(rio_pts)):
    acc += hav((rio_pts[i - 1][1], rio_pts[i - 1][0]), (rio_pts[i][1], rio_pts[i][0]))
    rio_km.append(acc)
rio_alt = [round(float(altura(la, lo))) for lo, la in rio_pts]
print(f"el río dentro del cuadro: {acc:.1f} km, de {rio_alt[0]} a {rio_alt[-1]} m")

def ancho(texto, tam):
    return len(texto) * tam * 0.55


def colocar(items, cajas):
    """Pone cada letrero donde no le caiga encima a otro.

    Se prueba a la derecha, a la izquierda, arriba y abajo del punto, en ese
    orden, y se toma la primera que quede libre. Si ninguna queda libre el
    letrero va a la derecha de todos modos: se prefiere un encime a un pueblo
    sin nombre."""
    puestos = []
    for it in items:
        tam = it["tam"]
        w, h = ancho(it["n"], tam), tam + 2
        r = it.get("r", 3)
        opciones = [(it["x"] + r + 5, it["y"] + 4, "start"),
                    (it["x"] - r - 5, it["y"] + 4, "end"),
                    (it["x"], it["y"] - r - 6, "middle"),
                    (it["x"], it["y"] + r + tam + 2, "middle")]
        for x, y, anc in opciones:
            x0 = x if anc == "start" else (x - w if anc == "end" else x - w / 2)
            caja = (x0 - 2, y - h, x0 + w + 2, y + 3)
            if caja[0] < 6 or caja[2] > VW - 6 or caja[1] < 6 or caja[3] > VH - 6:
                continue
            if any(not (caja[2] < c[0] or caja[0] > c[2]
                        or caja[3] < c[1] or caja[1] > c[3]) for c in cajas + puestos):
                continue
            it.update(lx=round(x, 1), ly=round(y, 1), anc=anc)
            puestos.append(caja)
            break
        else:
            # ninguna quedó libre: se prefiere el lado que no se sale del cuadro
            izq = it["x"] > VW * 0.7
            it.update(lx=round(it["x"] + (-r - 5 if izq else r + 5), 1),
                      ly=round(it["y"] + 4, 1), anc="end" if izq else "start")
    return puestos


# la leyenda y el punto mismo ocupan lugar
CAJAS = [(6, 6, 236, 150)]
for l in lugares:
    x, y = px(l["lo"]), py(l["la"])
    CAJAS.append((x - 7, y - 7, x + 7, y + 7))

lug_js = []
for l in sorted(lugares, key=lambda l: -RADIO.get(l["t"], 2.6)):
    lug_js.append(dict(n=l["n"], t=l["t"], la=l["la"], lo=l["lo"],
                       x=round(px(l["lo"]), 1), y=round(py(l["la"]), 1),
                       r=RADIO.get(l["t"], 2.6), h=int(round(altura(l["la"], l["lo"]))),
                       p=POB2020.get(l["n"]),
                       tam=12 if RADIO.get(l["t"], 2.6) >= 4.5 else 10.5))
CAJAS += colocar(lug_js, CAJAS)

ORDEN = {"carretera": 0, "brecha": 1, "calle": 2}


def d_de(pts):
    return "M" + " ".join(f"{px(x):.0f},{py(y):.0f}" for x, y in pts)


cam_html = "\n".join(
    f'<path class="cam {c["c"]}" d="{d_de(c["g"])}"/>'
    for c in sorted(caminos, key=lambda c: -ORDEN[c["c"]]))
agua_html = "\n".join(
    f'<path class="agua {a["c"]}" d="{d_de(a["g"])}"/>'
    for a in sorted(aguas, key=lambda a: a["c"] == "river"))
cur_html = "\n".join(
    f'<path class="cur{" mil" if lv % 500 == 0 else ""}" d="{d}"/>' for lv, d in cur)

# los arroyos con nombre, etiquetados en su punto medio
arr_js = []
vistos = set()
for a in aguas:
    if not a["n"] or a["n"] in vistos or a["c"] == "river":
        continue
    vistos.add(a["n"])
    m = a["g"][len(a["g"]) // 2]
    arr_js.append(dict(n=a["n"], x=round(px(m[0]), 1), y=round(py(m[1]), 1),
                       r=0, tam=10.5))
colocar(arr_js, CAJAS)
print(f"letreros: {len(lug_js)} lugares y {len(arr_js)} arroyos con nombre")

rio_js = dict(d=d_de(rio_pts),
              km=[round(k, 2) for k in rio_km],
              alt=rio_alt,
              x=[round(px(lo), 1) for lo, la in rio_pts],
              y=[round(py(la), 1) for lo, la in rio_pts])

# la malla que lee el cursor va a la mitad de resolución
chica = g[::2, ::2].astype("<i2")
malla_b64 = base64.b64encode(chica.tobytes()).decode()
CNX, CNY = chica.shape[1], chica.shape[0]
print(f"malla del cursor: {CNX} por {CNY}, {len(malla_b64):,} caracteres")

PW, PH = 900.0, 170.0
alto_max = int(g.max())
bajo_min = int(g.min())

DOC = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>El valle del Santa María · Altazor</title>
<style>
:root{{color-scheme:dark;
--ink:#e6e6e6; --ink2:#9a9a9a; --ink3:#7d7d7d;
--bg:#121212; --panel:#1a1a1a; --line:#2b2b2b; --accent:#58a6ff;
--rio:{C_RIO}; --arr:{C_ARR}; --carr:{C_CARR}; --bre:{C_BRE}; --calle:{C_CALLE};
--pueblo:{C_PUEBLO};}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);
font:400 16px/1.65 "Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;}}
main{{max-width:1060px;margin:0 auto;padding:2rem 1.25rem 4rem}}
header.site{{border-top:4px solid var(--accent);padding-top:22px;margin-bottom:26px;
display:flex;align-items:baseline;gap:18px;flex-wrap:wrap;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;}}
.brand{{font-weight:700;font-size:20px;letter-spacing:.1em;text-decoration:none;color:var(--ink);}}
.brand:hover{{color:var(--accent);}}
nav.site a{{color:var(--ink2);text-decoration:none;font-size:14px;}}
nav.site a:hover{{color:var(--accent);}}
h1{{font-size:1.6rem;font-weight:400;margin:1.6rem 0 .9rem}}
h2{{font-size:1.05rem;font-weight:400;color:var(--ink);margin:2rem 0 .6rem}}
.tiles{{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 1.1rem;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
.tile{{background:var(--panel);border:1px solid var(--line);border-radius:12px;
padding:10px 16px;min-width:190px;flex:1}}
.tile .k{{font-size:11.5px;color:var(--ink2)}}
.tile .v{{font-size:20px;font-weight:650;margin-top:2px}}
.tile .g{{font-size:12.5px;color:var(--ink3);margin-top:2px}}
figure{{margin:0}}
svg#map,svg#perfil{{width:100%;height:auto;display:block;background:#0f1216;
border-radius:8px;border:1px solid var(--line)}}
svg#perfil{{margin-top:10px}}
.controls{{display:flex;align-items:center;gap:.7rem;margin:1rem 0 0;flex-wrap:wrap;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;font-size:.9rem}}
button.ctl{{font:inherit;font-size:13px;background:var(--panel);color:var(--ink2);
border:1px solid var(--line);border-radius:8px;padding:6px 12px;cursor:pointer}}
button.ctl:hover{{color:var(--ink);border-color:#8d98a4}}
button.ctl[aria-pressed="true"]{{color:#12161a;background:var(--ink2);border-color:var(--ink2)}}
.readout{{display:flex;gap:.75rem;margin-top:.85rem;flex-wrap:wrap;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
.box{{background:var(--panel);border-radius:8px;padding:.7rem .95rem;min-width:150px}}
.box .lab{{font-size:.78rem;color:var(--ink2)}}
.box .val{{font-size:1.35rem;line-height:1.2;font-variant-numeric:tabular-nums}}
.box .sub2{{font-size:.8rem;color:var(--ink3)}}
.wide{{flex:1;min-width:240px}}
.notes{{margin-top:2.5rem;border-top:1px solid var(--line);padding-top:1.5rem;
color:var(--ink2);font-size:.95rem}}
.notes p{{margin:0 0 1rem;max-width:74ch}}
.method{{margin-top:1.5rem;color:var(--ink3);font-size:.88rem}}
.method p{{margin:0 0 .9rem;max-width:74ch}}
.refs{{font-size:.82rem;color:var(--ink3);max-width:74ch}}
.refs p{{padding-left:2.2em;text-indent:-2.2em;margin:0 0 .8em}}
.refs a{{color:var(--accent);word-break:break-word}}
path.cur{{fill:none;stroke:#cfd6dd;stroke-opacity:.14;stroke-width:.7}}
path.cur.mil{{stroke-opacity:.32;stroke-width:1.1}}
path.agua{{fill:none;stroke:var(--arr);stroke-opacity:.75;stroke-width:1;
stroke-linecap:round;stroke-linejoin:round}}
path.agua.river{{stroke:var(--rio);stroke-opacity:1;stroke-width:2.6}}
path.cam{{fill:none;stroke-linecap:round;stroke-linejoin:round}}
path.cam.carretera{{stroke:var(--carr);stroke-width:2}}
path.cam.brecha{{stroke:var(--bre);stroke-width:1;stroke-opacity:.85}}
path.cam.calle{{stroke:var(--calle);stroke-width:.6;stroke-opacity:.6}}
circle.lug{{fill:var(--pueblo);stroke:#10141a;stroke-width:1.2;cursor:pointer}}
circle.lug.on{{fill:#fff3d6}}
.lbl{{font:400 12px/1 system-ui,sans-serif;fill:#e4e9ee;pointer-events:none;
paint-order:stroke;stroke:#10141a;stroke-width:2.6}}
.lbl.chico{{font-size:10.5px;fill:#c2cbd3}}
.lbl.arr{{font-size:10.5px;fill:#9dc0dd;font-style:italic}}
.leg{{font:400 12px/1 system-ui,sans-serif;fill:#c3ccd6}}
.ax{{font:400 11px/1 system-ui,sans-serif;fill:var(--ink3)}}
</style>
</head>
<body>
<main>
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library</a></nav>
</header>

<h1>El valle del Santa María</h1>

<div class="tiles">
  <div class="tile"><div class="k">el río</div><div class="v">{acc:.0f} km en el cuadro</div>
    <div class="g">corre al norte, de {rio_alt[0]:,} a {rio_alt[-1]:,} m</div></div>
  <div class="tile"><div class="k">El Terrero</div><div class="v">{POB2020["El Terrero"]:,}</div>
    <div class="g">habitantes en 2020, más que la cabecera</div></div>
  <div class="tile"><div class="k">Namiquipa</div><div class="v">{POB2020["Namiquipa"]:,}</div>
    <div class="g">la cabecera del municipio, censo de 2020</div></div>
  <div class="tile"><div class="k">del río a la sierra</div><div class="v">{alto_max - bajo_min:,} m</div>
    <div class="g">del punto más bajo del cuadro al más alto</div></div>
</div>

<figure>
<svg id="map" viewBox="0 0 {VW:.0f} {VH:.0f}" role="img"
  aria-label="Mapa del valle del río Santa María en Namiquipa, con el relieve, los caminos y los pueblos.">
<title>El valle del Santa María</title>
<image id="relieve" href="data:image/jpeg;base64,{png}" x="0" y="0"
  width="{VW:.0f}" height="{VH:.0f}" preserveAspectRatio="none"/>
<g id="curvas">
{cur_html}
</g>
<g id="agua">
{agua_html}
</g>
<g id="caminos">
{cam_html}
</g>
<g id="arroyos"></g>
<g id="lugares"></g>
<circle id="marca" r="6.5" fill="none" stroke="#fff3d6" stroke-width="2" style="display:none"/>
<g id="legend">
  <rect x="8" y="8" width="224" height="126" rx="8" fill="#0f1216" fill-opacity=".78"/>
  <line x1="18" y1="28" x2="34" y2="28" stroke="{C_RIO}" stroke-width="2.6"/>
  <text class="leg" x="42" y="32">el río Santa María</text>
  <line x1="18" y1="48" x2="34" y2="48" stroke="{C_ARR}" stroke-width="1"/>
  <text class="leg" x="42" y="52">arroyo</text>
  <line x1="18" y1="68" x2="34" y2="68" stroke="{C_CARR}" stroke-width="2"/>
  <text class="leg" x="42" y="72">carretera</text>
  <line x1="18" y1="88" x2="34" y2="88" stroke="{C_BRE}" stroke-width="1"/>
  <text class="leg" x="42" y="92">brecha</text>
  <circle cx="26" cy="108" r="5" fill="{C_PUEBLO}"/>
  <text class="leg" x="42" y="112">pueblo o rancho</text>
  <line x1="18" y1="126" x2="34" y2="126" stroke="#cfd6dd" stroke-opacity=".32"/>
  <text class="leg" x="42" y="130">curva de nivel, cada 100 m</text>
</g>
</svg>

<svg id="perfil" viewBox="0 0 {PW:.0f} {PH:.0f}" role="img"
  aria-label="Altitud del río a lo largo del valle.">
<title>El río, de sur a norte</title>
<path id="perfilArea" d="" fill="#22303a"/>
<path id="perfilLinea" d="" fill="none" stroke="var(--rio)" stroke-width="1.6"/>
<g id="perfilEjes"></g>
<line id="perfilMarca" x1="0" y1="14" x2="0" y2="{PH - 26:.0f}" stroke="#fff3d6"
  stroke-width="1.4" style="display:none"/>
</svg>
</figure>

<div class="controls">
  <button class="ctl" id="bRel" aria-pressed="true">Relieve</button>
  <button class="ctl" id="bCur" aria-pressed="true">Curvas</button>
  <button class="ctl" id="bCam" aria-pressed="true">Caminos</button>
  <button class="ctl" id="bAgua" aria-pressed="true">Agua</button>
  <button class="ctl" id="bLug" aria-pressed="true">Pueblos</button>
</div>

<div class="readout">
  <div class="box"><div class="lab">altitud bajo el cursor</div>
    <div class="val" id="rAlt">&mdash;</div><div class="sub2" id="rCoord"></div></div>
  <div class="box wide"><div class="lab" id="rLab">el lugar más cercano</div>
    <div class="val" id="rLug" style="font-size:1.05rem">&mdash;</div>
    <div class="sub2" id="rLugSub"></div></div>
  <div class="box"><div class="lab">el río</div>
    <div class="val" id="rRio">&mdash;</div><div class="sub2" id="rRioSub"></div></div>
</div>

<div class="notes">
<p>El río Santa María baja de la sierra y da vuelta al norte por el valle;
sobre él están la cabecera, El Molino y El Terrero, uno tras otro, y en las
lomas de los lados quedan los ranchos. El agua va perdiendo altura hacia el
norte, y el perfil de abajo lleva esa cuenta.</p>
<p>Las cifras de población son del censo de 2020 y solo las hay para cuatro de
estos lugares; los demás salen en el mapa por su nombre y por lo que
OpenStreetMap dice que son. El cursor sobre el mapa da la altitud del terreno
y el lugar más cercano.</p>
</div>

<div class="method">
<p>El relieve viene de una malla de unos ciento cincuenta metros de paso,
armada con las teselas de elevación de Mapzen, y las curvas de nivel están
calculadas sobre esa misma malla remuestreada: sirven para leer la forma del
terreno, no para medir alturas exactas. En Namiquipa la malla marca
{int(round(altura(29.25056, -107.41278)))} m y el censo publica 1,842 m, y en
El Terrero marca {int(round(altura(29.18107, -107.38657)))} m contra 1,854 m.
Los caminos, las corrientes de agua y los nombres de los lugares son de
OpenStreetMap, simplificados a unos treinta metros; la clase de cada camino
sale de sus etiquetas, así que una brecha bien trazada puede aparecer como
carretera y al revés. La población es del INEGI, censo de 2020, por localidad:
el municipio entero tenía {MUNICIPIO_2020:,} habitantes ese año.</p>
</div>

<h2>Referencias</h2>
<div class="refs">
<p>Instituto Nacional de Estadística y Geografía. (2021). <em>Censo de
Población y Vivienda 2020</em> [Conjunto de datos]. INEGI.
<a href="https://www.inegi.org.mx/programas/ccpv/2020/">https://www.inegi.org.mx/programas/ccpv/2020/</a></p>
<p>Mapzen. (2026). <em>Terrain tiles</em> [Conjunto de datos]. Registry of Open
Data on AWS.
<a href="https://registry.opendata.aws/terrain-tiles/">https://registry.opendata.aws/terrain-tiles/</a></p>
<p>OpenStreetMap contributors. (2026). <em>OpenStreetMap</em> [Conjunto de
datos]. <a href="https://www.openstreetmap.org/copyright">https://www.openstreetmap.org/copyright</a></p>
</div>
</main>
<script>
const LUG={json.dumps(lug_js, ensure_ascii=False)};
const ARR={json.dumps(arr_js, ensure_ascii=False)};
const RIO={json.dumps(rio_js)};
const MALLA="{malla_b64}";
const CNX={CNX}, CNY={CNY}, CDX={DX * 2};
const W={W}, E={E}, S={S}, N={N}, VW={VW}, VH={VH:.0f};
const PW={PW}, PH={PH};
const el=id=>document.getElementById(id);
const SVGNS='http://www.w3.org/2000/svg';
function make(t,a,p){{const e=document.createElementNS(SVGNS,t);
  for(const k in a) e.setAttribute(k,a[k]); if(p) p.appendChild(e); return e;}}

// la malla del cursor, int16 little endian
const bin=atob(MALLA);
const alturas=new Int16Array(CNX*CNY);
for(let i=0;i<alturas.length;i++) alturas[i]=(bin.charCodeAt(i*2)|(bin.charCodeAt(i*2+1)<<8))<<16>>16;
function alturaEn(la,lo){{
  const c=Math.max(0,Math.min(CNX-1,Math.round((lo-W)/CDX)));
  const r=Math.max(0,Math.min(CNY-1,Math.round((N-la)/CDX)));
  return alturas[r*CNX+c];
}}

const gl=el('lugares');
LUG.forEach((l,i)=>{{
  const c=make('circle',{{class:'lug',cx:l.x,cy:l.y,r:l.r,'data-i':i}},gl);
  c.addEventListener('mouseenter',()=>mostrar(i));
  const t=make('text',{{class:'lbl'+(l.tam<12?' chico':''),x:l.lx,y:l.ly,
    'text-anchor':l.anc}},gl);
  t.textContent=l.n;
}});
const ga=el('arroyos');
ARR.forEach(a=>{{
  const t=make('text',{{class:'lbl arr',x:a.lx,y:a.ly,'text-anchor':a.anc}},ga);
  t.textContent=a.n;
}});

// el perfil del río
el('perfilLinea').setAttribute('d','');
const rMin=Math.min(...RIO.alt), rMax=Math.max(...RIO.alt);
const total=RIO.km[RIO.km.length-1];
const pxKm=k=>46+(k/total)*(PW-70);
const pyEl=e=>PH-26-((e-rMin)/(rMax-rMin))*(PH-52);
{{
  let d='';
  RIO.km.forEach((k,i)=>{{d+=(i?'L':'M')+pxKm(k).toFixed(1)+','+pyEl(RIO.alt[i]).toFixed(1);}});
  el('perfilLinea').setAttribute('d',d);
  el('perfilArea').setAttribute('d',d+`L${{pxKm(total).toFixed(1)}},${{PH-26}}L${{pxKm(0).toFixed(1)}},${{PH-26}}Z`);
  const ax=el('perfilEjes');
  [rMin,Math.round((rMin+rMax)/2/10)*10,rMax].forEach(v=>{{
    make('line',{{x1:46,y1:pyEl(v),x2:PW-24,y2:pyEl(v),stroke:'#23262a','stroke-width':1}},ax);
    const t=make('text',{{class:'ax',x:6,y:pyEl(v)+4}},ax); t.textContent=v+' m';}});
  for(let k=0;k<=total;k+=10){{
    make('line',{{x1:pxKm(k),y1:PH-26,x2:pxKm(k),y2:PH-20,stroke:'#4d5359','stroke-width':1}},ax);
    const t=make('text',{{class:'ax',x:pxKm(k),y:PH-8,'text-anchor':'middle'}},ax);
    t.textContent=k+' km';}}
  const t=make('text',{{class:'ax',x:PW-24,y:14,'text-anchor':'end'}},ax);
  t.textContent='aguas abajo, hacia el norte';
}}

function mostrar(i){{
  [...gl.children].forEach(c=>{{if(c.tagName==='circle') c.classList.remove('on')}});
  const l=LUG[i];
  const c=gl.querySelector(`circle[data-i="${{i}}"]`);
  if(c) c.classList.add('on');
  el('rLab').textContent='el lugar';
  el('rLug').textContent=l.n;
  el('rLugSub').textContent=(l.p?l.p.toLocaleString('es-MX')+' habitantes en 2020, ':'')
    +l.h+' m de altitud';
}}

const svg=el('map');
function alCursor(ev){{
  const pt=svg.createSVGPoint(); pt.x=ev.clientX; pt.y=ev.clientY;
  const p=pt.matrixTransform(svg.getScreenCTM().inverse());
  const lo=W+(p.x/VW)*(E-W), la=N-(p.y/VH)*(N-S);
  if(lo<W||lo>E||la<S||la>N) return;
  el('rAlt').textContent=alturaEn(la,lo)+' m';
  el('rCoord').textContent=la.toFixed(4)+', '+lo.toFixed(4);
  let mejor=null;
  LUG.forEach((l,i)=>{{const d=Math.hypot(l.x-p.x,l.y-p.y); if(!mejor||d<mejor[1]) mejor=[i,d];}});
  const kmPorPx=({(E - W) * 111.32 * np.cos(np.radians(LAT0)):.4f})/VW;
  const l=LUG[mejor[0]];
  el('rLab').textContent='el lugar más cercano';
  el('rLug').textContent=l.n;
  el('rLugSub').textContent=(l.p?l.p.toLocaleString('es-MX')+' habitantes en 2020, ':'')
    +'a '+(mejor[1]*kmPorPx).toFixed(1)+' km';
  // el punto del río más cercano
  let br=null;
  for(let i=0;i<RIO.x.length;i++){{const d=Math.hypot(RIO.x[i]-p.x,RIO.y[i]-p.y);
    if(!br||d<br[1]) br=[i,d];}}
  el('rRio').textContent=RIO.alt[br[0]]+' m';
  el('rRioSub').textContent='km '+RIO.km[br[0]].toFixed(1)+' del río, a '
    +(br[1]*kmPorPx).toFixed(1)+' km';
  el('perfilMarca').style.display='';
  el('perfilMarca').setAttribute('x1',pxKm(RIO.km[br[0]]));
  el('perfilMarca').setAttribute('x2',pxKm(RIO.km[br[0]]));
  el('marca').style.display='';
  el('marca').setAttribute('cx',RIO.x[br[0]]);
  el('marca').setAttribute('cy',RIO.y[br[0]]);
}}
svg.addEventListener('mousemove',alCursor);
svg.addEventListener('mouseleave',()=>{{
  el('perfilMarca').style.display='none'; el('marca').style.display='none';
}});

function toggle(id,gid){{
  el(id).addEventListener('click',()=>{{
    const v=el(id).getAttribute('aria-pressed')!=='true';
    el(id).setAttribute('aria-pressed',v);
    el(gid).style.display=v?'':'none';
    if(gid==='lugares') el('arroyos').style.display=v?'':'none';
  }});
}}
toggle('bRel','relieve'); toggle('bCur','curvas'); toggle('bCam','caminos');
toggle('bAgua','agua'); toggle('bLug','lugares');

window.__valle=()=>({{lugares:LUG.length,caminos:document.querySelectorAll('#caminos path').length,
  agua:document.querySelectorAll('#agua path').length,curvas:document.querySelectorAll('#curvas path').length,
  rio:{{km:RIO.km[RIO.km.length-1],alto:Math.max(...RIO.alt),bajo:Math.min(...RIO.alt),n:RIO.alt.length}},
  alt:el('rAlt').textContent,lugar:el('rLug').textContent,
  altura:(la,lo)=>alturaEn(la,lo)}});
</script>
</body>
</html>
"""

OUT.write_text(DOC, encoding="utf-8")
print(f"escrito {OUT} ({len(DOC):,} bytes)")
