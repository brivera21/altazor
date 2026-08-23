#!/usr/bin/env python3
"""Genera ruta-namiquipa.html: un recorrido grabado en la sierra de Namiquipa,
de la altura al llano de Bavícora.

La traza y el perfil vienen de namiquipa_data.py. El relieve del fondo sale de
data/namiquipa_dem.txt, una malla de altitudes de unos trescientos metros de
paso armada con las teselas terrarium de Mapzen sobre AWS Open Data.

El mapa chico de la esquina usa el polígono de Chihuahua de norte-mexico.py.

Uso: python3 build_namiquipa.py
"""

import base64
import io
import json
import pickle
from pathlib import Path

import numpy as np
from PIL import Image

import namiquipa_data as D

OUT = Path(__file__).parent.parent / "ruta-namiquipa.html"
DEM = Path(__file__).parent / "data" / "namiquipa_dem.txt"
MUN = Path(__file__).parent / "data" / "chihuahua_municipios.txt"
NMEX = Path("/home/claude/nmex")

# la malla, y con ella el cuadro del mapa
NX, NY, DX = 87, 31, 0.003
W, N = -107.70, 29.095
E, S = W + (NX - 1) * DX, N - (NY - 1) * DX
LAT0 = 29.05
VW = 1000.0
SCALE = VW / ((E - W) * np.cos(np.radians(LAT0)))
VH = (N - S) * SCALE

C_TRAZA = "#f5a623"
C_HECHO = "#fff0cf"
C_PUEBLO = "#7fd4c1"


def px(lon):
    return (lon - W) * np.cos(np.radians(LAT0)) * SCALE


def py(lat):
    return (N - lat) * SCALE


def grid():
    txt = DEM.read_text().splitlines()
    b64 = "".join(l for l in txt if not l.startswith("#"))
    a = np.frombuffer(base64.b64decode(b64), dtype="<i2").astype(float)
    return a.reshape(NY, NX)


def relieve(g, w=900, h=None):
    """Sombra de relieve sobre la malla, remuestreada a algo que se pueda ver.

    La malla tiene un paso de unos trescientos metros, así que esto es un
    fondo suave, no una carta topográfica."""
    h = h or int(round(w * (N - S) / ((E - W) * np.cos(np.radians(LAT0)))))
    fine = np.asarray(Image.fromarray(g.astype("float32"), "F")
                      .resize((w, h), Image.BICUBIC), dtype=float)
    dy_m = (N - S) * 110570.0 / h
    dx_m = (E - W) * 111320.0 * np.cos(np.radians(LAT0)) / w
    gy, gx = np.gradient(fine, dy_m, dx_m)
    slope = np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    az, alt = np.radians(315.0), np.radians(45.0)
    shade = (np.sin(alt) * np.cos(slope)
             + np.cos(alt) * np.sin(slope) * np.cos(az - aspect))
    shade = np.clip(shade, 0, 1)

    lo, hi = fine.min(), fine.max()
    t = np.clip((fine - lo) / (hi - lo), 0, 1)[..., None]
    bajo = np.array([44.0, 52.0, 46.0])       # el llano
    medio = np.array([74.0, 72.0, 56.0])
    alto = np.array([116.0, 108.0, 92.0])     # los filos
    col = np.where(t < 0.5, bajo + (medio - bajo) * (t / 0.5),
                   medio + (alto - medio) * ((t - 0.5) / 0.5))
    rgb = col * (0.45 + 0.75 * shade[..., None])
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB")
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode(), fine


def curvas(fine, step=100):
    """Curvas de nivel cada cien metros sobre la malla remuestreada."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    h, w = fine.shape
    xs = np.linspace(px(W), px(E), w)
    ys = np.linspace(py(N), py(S), h)
    lo = int(np.ceil(fine.min() / step) * step)
    hi = int(np.floor(fine.max() / step) * step)
    levels = list(range(lo, hi + 1, step))
    fig = plt.figure()
    cs = plt.contour(xs, ys, fine, levels=levels)
    out = []
    for level, seg in zip(cs.levels, cs.allsegs):
        for s in seg:
            if len(s) < 6:
                continue
            d = "M" + " ".join(f"{x:.1f},{y:.1f}" for x, y in s[::2])
            out.append((int(level), d))
    plt.close(fig)
    return out


def track():
    v = [int(x) for x in "".join(D.TRAZA).split(",")]
    lat, lon, m = v[0], v[1], v[2]
    pts = [(lat / 1e5, lon / 1e5, m / 1000.0)]
    km = m / 1000.0
    for i in range(3, len(v), 3):
        lat += v[i]
        lon += v[i + 1]
        km += v[i + 2] / 1000.0
        pts.append((lat / 1e5, lon / 1e5, km))
    return pts


g = grid()
png, fine = relieve(g)
cur = curvas(fine)
pts = track()
prof = [int(x) for x in "".join(D.PERFIL).split(",")]
secs = [int(x) for x in "".join(D.SEGUNDOS).split(",")]
total_km = pts[-1][2]
print(f"traza: {len(pts)} puntos, {total_km:.2f} km; "
      f"perfil: {len(prof)} muestras; curvas: {len(cur)}")

# la altitud del GPS contra la malla, que es la comprobación de la página
def dem_at(la, lo):
    c = np.clip((lo - W) / DX, 0, NX - 1.001)
    r = np.clip((N - la) / DX, 0, NY - 1.001)
    c0, r0 = int(c), int(r)
    fx, fy = c - c0, r - r0
    return (g[r0, c0] * (1 - fx) * (1 - fy) + g[r0, c0 + 1] * fx * (1 - fy)
            + g[r0 + 1, c0] * (1 - fx) * fy + g[r0 + 1, c0 + 1] * fx * fy)


def punto_en(km):
    i = 1
    while i < len(pts) - 1 and pts[i][2] < km:
        i += 1
    a, b = pts[i - 1], pts[i]
    f = (km - a[2]) / (b[2] - a[2]) if b[2] > a[2] else 0.0
    return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f


dif = np.array([prof[i] - dem_at(*punto_en(i * D.PASO_KM))
                for i in range(len(prof))])
cerca = float((np.abs(dif) < 25).mean() * 100)
print(f"altitud del GPS contra la malla: mediana {np.median(dif):.0f} m, "
      f"{cerca:.0f}% dentro de 25 m")

track_js = [[round(px(lo), 1), round(py(la), 1), round(km, 3)] for la, lo, km in pts]
lugares_js = [dict(n=n, x=round(px(lo), 1), y=round(py(la), 1), t=t)
              for n, la, lo, t in D.LUGARES]
cur_html = "\n".join(
    f'<path class="cur{" mil" if lv % 500 == 0 else ""}" d="{d}"/>' for lv, d in cur)

def municipios():
    """Los 67 municipios de Chihuahua, de OpenStreetMap.

    El archivo trae dos versiones de cada límite: una gruesa para dibujar el
    mapa chico y una fina, solo de los municipios de por aquí, para saber en
    cuál cae cada punto de la traza."""
    grueso, fino = {}, {}
    for line in MUN.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        tipo, nombre, *anillos = line.split("\t")
        rings = []
        for a in anillos:
            v = [int(x) for x in a.split(",")]
            lon, lat = v[0], v[1]
            pts = [(lon / 1e5, lat / 1e5)]
            for i in range(2, len(v), 2):
                lon += v[i]
                lat += v[i + 1]
                pts.append((lon / 1e5, lat / 1e5))
            if len(pts) > 3:
                rings.append(pts)
        (grueso if tipo == "G" else fino)[nombre] = rings
    return grueso, fino


def area_de(rings):
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    ps = [Polygon(r).buffer(0) for r in rings if len(r) > 3]
    return unary_union([q for q in ps if q.area > 0])


GRUESO, FINO = municipios()
FORMAS = {n: area_de(r) for n, r in FINO.items()}
print(f"municipios: {len(GRUESO)} en el mapa chico, {len(FINO)} con límite fino")

from shapely.geometry import Point as _Pt
paso, tramos = [], []
for la, lo, km in pts:
    aqui = next((n for n, g in FORMAS.items() if g.contains(_Pt(lo, la))), None)
    paso.append(aqui)
    if not tramos or tramos[-1][0] != aqui:
        tramos.append([aqui, km, km])
    else:
        tramos[-1][2] = km
CRUZADOS = [t[0] for t in tramos]
for n, k0, k1 in tramos:
    print(f"  {n}: del km {k0:.2f} al {k1:.2f}")
if any(n is None for n in CRUZADOS):
    raise SystemExit("hay puntos de la traza fuera de todo municipio")
KM_EN = {}
for n, k0, k1 in tramos:
    KM_EN[n] = KM_EN.get(n, 0.0) + (k1 - k0)

# el mapa chico: Chihuahua por municipios, el cuadro, y el pueblo de Namiquipa
chi = pickle.load(open(NMEX / "states.pkl", "rb"))["Chihuahua"].simplify(0.02)
cw, ch = 150.0, 190.0
bx0, by0, bx1, by1 = chi.bounds
cs = min(cw / ((bx1 - bx0) * np.cos(np.radians(28.5))), ch / (by1 - by0)) * 0.92
def ix(lon):
    return 12 + (lon - bx0) * np.cos(np.radians(28.5)) * cs
def iy(lat):
    return 12 + (by1 - lat) * cs
chi_d = "M" + " ".join(f"{ix(x):.1f},{iy(y):.1f}" for x, y in chi.exterior.coords) + "Z"


def anillos_d(rings, fx, fy):
    return "".join("M" + " ".join(f"{fx(x):.1f},{fy(y):.1f}" for x, y in r) + "Z"
                   for r in rings)


mun_d = "\n".join(
    f'<path class="mun{" cruza" if n in CRUZADOS else ""}" d="{anillos_d(r, ix, iy)}"/>'
    for n, r in GRUESO.items())
# el letrero de cada municipio cruzado, en su centro
etq_mun = []
for n in CRUZADOS:
    c = FORMAS[n].representative_point()
    etq_mun.append(dict(n=n, x=round(ix(c.x), 1), y=round(iy(c.y), 1),
                        km=round(KM_EN[n], 1)))

# el límite entre los municipios cruzados, dentro del cuadro del mapa grande
from shapely.geometry import box as _box
marco = _box(W, S, E, N)
linea = []
for a, b in zip(CRUZADOS, CRUZADOS[1:]):
    comun = FORMAS[a].boundary.intersection(FORMAS[b].boundary).intersection(marco)
    for g in (comun.geoms if hasattr(comun, "geoms") else [comun]):
        if g.geom_type == "LineString" and len(g.coords) > 1:
            linea.append("M" + " ".join(f"{px(x):.1f},{py(y):.1f}" for x, y in g.coords))
raya_d = "".join(linea)
print(f"límite municipal dentro del cuadro: {len(linea)} tramos")
# a esta escala los dos pueblos caen en el mismo punto, así que va uno
inset_pts = [dict(n=D.LEJOS[0][0], x=round(ix(D.LEJOS[0][2]), 1),
                  y=round(iy(D.LEJOS[0][1]), 1))]
inset_box = dict(x=round(ix(W), 1), y=round(iy(N), 1),
                 w=round((E - W) * np.cos(np.radians(28.5)) * cs, 1),
                 h=round((N - S) * cs, 1))

PW, PH = 1000.0, 190.0

DOC = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>La Ruta Namiquipa · Altazor</title>
<style>
:root{{color-scheme:dark;
--ink:#e6e6e6; --ink2:#9a9a9a; --ink3:#7d7d7d;
--bg:#121212; --panel:#1a1a1a; --line:#2b2b2b; --accent:#58a6ff;
--traza:{C_TRAZA}; --hecho:{C_HECHO}; --pueblo:{C_PUEBLO};}}
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
input[type=range]{{flex:1;min-width:220px;accent-color:var(--traza);height:22px}}
.readout{{display:flex;gap:.75rem;margin-top:.85rem;flex-wrap:wrap;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
.box{{background:var(--panel);border-radius:8px;padding:.7rem .95rem;min-width:150px}}
.box .lab{{font-size:.78rem;color:var(--ink2)}}
.box .val{{font-size:1.35rem;line-height:1.2;font-variant-numeric:tabular-nums}}
.box .sub2{{font-size:.8rem;color:var(--ink3)}}
.wide{{flex:1;min-width:230px}}
.notes{{margin-top:2.5rem;border-top:1px solid var(--line);padding-top:1.5rem;
color:var(--ink2);font-size:.95rem}}
.notes p{{margin:0 0 1rem;max-width:74ch}}
.method{{margin-top:1.5rem;color:var(--ink3);font-size:.88rem}}
.method p{{margin:0 0 .9rem;max-width:74ch}}
.refs{{font-size:.82rem;color:var(--ink3);max-width:74ch}}
.refs p{{padding-left:2.2em;text-indent:-2.2em;margin:0 0 .8em}}
.refs a{{color:var(--accent);word-break:break-word}}
path.cur{{fill:none;stroke:#cfd6dd;stroke-opacity:.16;stroke-width:.7}}
path.mun{{fill:none;stroke:#7f8b96;stroke-opacity:.5;stroke-width:.5}}
path.mun.cruza{{fill:var(--traza);fill-opacity:.5;stroke:var(--traza);stroke-opacity:1;stroke-width:.8}}
path.mun.aqui{{fill-opacity:.85}}
#raya path{{fill:none;stroke:#e8dcc0;stroke-opacity:.85;stroke-width:1.6;stroke-dasharray:7 5}}
path.cur.mil{{stroke-opacity:.34;stroke-width:1.1}}
#traza{{fill:none;stroke:var(--traza);stroke-width:2.6;stroke-linejoin:round;stroke-linecap:round}}
#hecho{{fill:none;stroke:var(--hecho);stroke-width:4;stroke-linejoin:round;stroke-linecap:round}}
.lbl{{font:400 12px/1 system-ui,sans-serif;fill:#dfe4e9;pointer-events:none;
paint-order:stroke;stroke:#10141a;stroke-width:2.6}}
.lbl.chico{{font-size:11px;fill:#c9d0d6}}
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

<h1>La Ruta Namiquipa</h1>

<div class="tiles">
  <div class="tile"><div class="k">recorrido</div><div class="v">{total_km:.1f} km</div>
    <div class="g">de la sierra al llano de Bavícora</div></div>
  <div class="tile"><div class="k">punto más alto</div><div class="v">{max(prof):,} m</div>
    <div class="g">en el kilómetro {prof.index(max(prof)) * D.PASO_KM:.1f}</div></div>
  <div class="tile"><div class="k">bajada</div><div class="v">{max(prof) - min(prof)} m</div>
    <div class="g">del filo a Santa Ana de Bavícora</div></div>
  <div class="tile"><div class="k">trazo</div><div class="v">2016</div>
    <div class="g">un recorrido grabado el 24 de septiembre</div></div>
  <div class="tile"><div class="k">municipios</div>
    <div class="v" style="font-size:17px">{" y ".join(CRUZADOS)}</div>
    <div class="g">{KM_EN[CRUZADOS[0]]:.1f} km en el primero, {KM_EN[CRUZADOS[1]]:.1f} en el segundo</div></div>
</div>

<figure>
<svg id="map" viewBox="0 0 {VW:.0f} {VH:.0f}" role="img"
  aria-label="Mapa del recorrido sobre el relieve de la sierra de Namiquipa.">
<title>La Ruta Namiquipa sobre el relieve</title>
<image id="relieve" href="data:image/png;base64,{png}" x="0" y="0"
  width="{VW:.0f}" height="{VH:.0f}" preserveAspectRatio="none"/>
<g id="curvas">
{cur_html}
</g>
<g id="raya"><path d="{raya_d}"/></g>
<path id="traza" d=""/>
<path id="hecho" d=""/>
<g id="pueblos"></g>
<circle id="marca" r="5.5" fill="#fff3d6" stroke="#7a4d0d" stroke-width="1.5"/>
<g id="mapachico" transform="translate({VW - cw - 34:.0f},10)">
  <rect x="0" y="0" width="{cw + 24:.0f}" height="{ch + 54:.0f}" rx="8"
    fill="#0f1216" fill-opacity=".82"/>
  <text class="leg" x="12" y="{ch + 26:.0f}" fill="{C_TRAZA}">{" y ".join(CRUZADOS)}</text>
  <text class="leg" x="12" y="{ch + 44:.0f}">los municipios que cruza</text>
  <path d="{chi_d}" fill="#232a31" stroke="#8d98a4" stroke-width="0.8"/>
  <g id="municipios">
{mun_d}
  </g>
  <path d="{chi_d}" fill="none" stroke="#8d98a4" stroke-width="0.9"/>
  <rect x="{inset_box['x']}" y="{inset_box['y']}" width="{max(inset_box['w'], 6)}"
    height="{max(inset_box['h'], 6)}" fill="none" stroke="{C_TRAZA}" stroke-width="1.4"/>
</g>
<g id="legend">
  <rect x="8" y="{VH - 112:.0f}" width="206" height="104" rx="8" fill="#0f1216" fill-opacity=".72"/>
  <rect x="18" y="{VH - 62:.0f}" width="16" height="4" rx="2" fill="{C_TRAZA}"/>
  <text class="leg" x="42" y="{VH - 55:.0f}">el recorrido</text>
  <circle cx="26" cy="{VH - 38:.0f}" r="4" fill="{C_PUEBLO}"/>
  <text class="leg" x="42" y="{VH - 34:.0f}">pueblo o rancho</text>
  <line x1="18" y1="{VH - 18:.0f}" x2="34" y2="{VH - 18:.0f}" stroke="#cfd6dd" stroke-opacity=".34"/>
  <text class="leg" x="42" y="{VH - 14:.0f}">curva de nivel, cada 100 m</text>
  <line x1="18" y1="{VH - 96:.0f}" x2="34" y2="{VH - 96:.0f}" stroke="#e8dcc0"
    stroke-opacity=".85" stroke-width="1.6" stroke-dasharray="5 4"/>
  <text class="leg" x="42" y="{VH - 92:.0f}">raya entre municipios</text>
</g>
</svg>

<svg id="perfil" viewBox="0 0 {PW:.0f} {PH:.0f}" role="img"
  aria-label="Altitud a lo largo del recorrido.">
<title>Altitud a lo largo del recorrido</title>
<path id="perfilArea" d="" fill="#2a2a22"/>
<path id="perfilLinea" d="" fill="none" stroke="var(--traza)" stroke-width="1.6"/>
<g id="perfilEjes"></g>
<line id="perfilMarca" x1="0" y1="14" x2="0" y2="{PH - 26:.0f}" stroke="#fff3d6" stroke-width="1.4"/>
</svg>
</figure>

<div class="controls">
  <button class="ctl" id="bPlay" aria-pressed="false">Recorrer</button>
  <input type="range" id="km" min="0" max="{total_km:.2f}" step="0.02" value="0"
    aria-label="Kilómetro del recorrido">
  <button class="ctl" id="bRel" aria-pressed="true">Relieve</button>
  <button class="ctl" id="bCur" aria-pressed="true">Curvas</button>
  <button class="ctl" id="bPue" aria-pressed="true">Pueblos</button>
  <button class="ctl" id="bMun" aria-pressed="true">Municipios</button>
</div>

<div class="readout">
  <div class="box"><div class="lab">kilómetro</div>
    <div class="val" id="rKm">0.0</div><div class="sub2" id="rFalta"></div></div>
  <div class="box"><div class="lab">altitud</div>
    <div class="val" id="rAlt"></div><div class="sub2" id="rPend"></div></div>
  <div class="box"><div class="lab">tiempo</div>
    <div class="val" id="rTiempo"></div><div class="sub2" id="rVel"></div></div>
  <div class="box"><div class="lab">municipio</div>
    <div class="val" id="rMun" style="font-size:1.05rem"></div>
    <div class="sub2" id="rMunSub"></div></div>
  <div class="box wide"><div class="lab">cerca</div>
    <div class="val" id="rCerca" style="font-size:1.05rem"></div>
    <div class="sub2" id="rCercaSub"></div></div>
</div>

<div class="notes">
<p>El recorrido empieza arriba, en la sierra al poniente de Santa Ana de
Bavícora, sube al filo en el kilómetro {prof.index(max(prof)) * D.PASO_KM:.1f} y
de ahí se deja ir: novecientos metros de bajada en los últimos veinte
kilómetros, hasta el llano.</p>
<p>Los primeros {KM_EN[CRUZADOS[0]]:.0f} kilómetros van por el municipio de
{CRUZADOS[0]}; la raya municipal queda en el kilómetro {tramos[1][1]:.1f}, ya
en la bajada, y de ahí el camino entra a {CRUZADOS[1]}.</p>
<p>La traza es un solo recorrido grabado con GPS en 2016, no el trazo oficial
de ninguna edición. El relieve del fondo viene de una malla de trescientos
metros, y la altitud que marcó el GPS coincide con ella dentro de veinticinco
metros en cuatro de cada cinco puntos, que para un aparato de mano en la
sierra está bien.</p>
</div>

<div class="method">
<p>La traza va simplificada a seis metros de tolerancia, de {len(track_js)} puntos
en lugar de los dos mil que trae el archivo original; el kilometraje que lleva
cada punto es el del recorrido completo, no el de la línea simplificada. El perfil lleva la altitud del propio
GPS cada cien metros, no la de la malla, y la velocidad sale de las horas
grabadas en el archivo. Las curvas de nivel están calculadas sobre la malla
remuestreada: sirven para leer la forma del terreno, no para medir alturas
exactas. Los pueblos, los ranchos y los límites municipales vienen de
OpenStreetMap: los sesenta y siete municipios del estado juntos miden un dos
por ciento menos que la superficie que se publica de Chihuahua, y el pueblo de
Namiquipa, El Terrero y Santa Ana de Bavícora caen del lado que les toca.</p>
</div>

<h2>Referencias</h2>
<div class="refs">
<p>Leal, M. (2016, 24 de septiembre). <em>Namiquipa</em> [Recorrido con GPS].
Wikiloc.
<a href="{D.FUENTE[3]}">{D.FUENTE[3]}</a></p>
<p>Mapzen. (2026). <em>Terrain tiles</em> [Conjunto de datos]. Registry of Open
Data on AWS.
<a href="https://registry.opendata.aws/terrain-tiles/">https://registry.opendata.aws/terrain-tiles/</a></p>
<p>OpenStreetMap contributors. (2026). <em>OpenStreetMap</em> [Conjunto de
datos]. <a href="https://www.openstreetmap.org/copyright">https://www.openstreetmap.org/copyright</a></p>
<p>Instituto Nacional de Estadística y Geografía. (2023). <em>Marco
geoestadístico, diciembre 2023</em> [Conjunto de datos]. INEGI.
<a href="https://www.inegi.org.mx/temas/mg/">https://www.inegi.org.mx/temas/mg/</a></p>
</div>
</main>
<script>
const TR={json.dumps(track_js)};
const PROF={json.dumps(prof)};
const SEC={json.dumps(secs)};
const LUG={json.dumps(lugares_js, ensure_ascii=False)};
const LEJOS={json.dumps(inset_pts, ensure_ascii=False)};
const PASO_MUN={json.dumps([[round(k, 3), n] for (la, lo, k), n in zip(pts, paso)], ensure_ascii=False)};
const TRAMOS={json.dumps([[n, round(k0, 2), round(k1, 2)] for n, k0, k1 in tramos], ensure_ascii=False)};
const ETQ_MUN={json.dumps(etq_mun, ensure_ascii=False)};
const PASO={D.PASO_KM};
const TOTAL={total_km:.3f};
const PW={PW}, PH={PH};
const el=id=>document.getElementById(id);
const SVGNS='http://www.w3.org/2000/svg';
function make(t,a,p){{const e=document.createElementNS(SVGNS,t);
  for(const k in a) e.setAttribute(k,a[k]); if(p) p.appendChild(e); return e;}}

el('traza').setAttribute('d','M'+TR.map(p=>p[0]+','+p[1]).join('L'));

const gp=el('pueblos');
LUG.forEach(l=>{{
  make('circle',{{cx:l.x,cy:l.y,r:l.t==='pueblo'?5:3.5,fill:'{C_PUEBLO}',
    stroke:'#10141a','stroke-width':1.2}},gp);
  const der=l.x<{VW * 0.62:.0f};
  const bajo=l.x>{VW * 0.72:.0f};      // por debajo del mapa chico
  const t=make('text',{{class:'lbl',x:l.x+(der?9:-9),y:l.y+(bajo?18:4),
    'text-anchor':der?'start':'end'}},gp); t.textContent=l.n;
}});
{{
  const gi=el('mapachico');
  LEJOS.forEach(p=>{{
    make('circle',{{cx:p.x,cy:p.y,r:2.4,fill:'#dfe4e9'}},gi);
  }});
}}
function municipioEn(km){{
  for(const [n,k0,k1] of TRAMOS) if(km>=k0&&km<=k1) return n;
  return TRAMOS[TRAMOS.length-1][0];
}}
const gMun=el('municipios');
function marcarMunicipio(n){{
  [...gMun.children].forEach(p=>p.classList.remove('aqui'));
  const i=ETQ_MUN.findIndex(m=>m.n===n);
  const cruz=[...gMun.children].filter(p=>p.classList.contains('cruza'));
  if(i>=0&&cruz[i]) cruz[i].classList.add('aqui');
}}

const elMin=Math.min(...PROF), elMax=Math.max(...PROF);
const pxKm=k=>46+(k/TOTAL)*(PW-70);
const pyEl=e=>PH-26-((e-elMin)/(elMax-elMin))*(PH-52);
{{
  let d='';
  PROF.forEach((e,i)=>{{const k=Math.min(i*PASO,TOTAL);
    d+=(i?'L':'M')+pxKm(k).toFixed(1)+','+pyEl(e).toFixed(1);}});
  el('perfilLinea').setAttribute('d',d);
  el('perfilArea').setAttribute('d',d+`L${{pxKm(TOTAL).toFixed(1)}},${{PH-26}}L${{pxKm(0).toFixed(1)}},${{PH-26}}Z`);
  const ax=el('perfilEjes');
  [elMin,Math.round((elMin+elMax)/2/50)*50,elMax].forEach(v=>{{
    make('line',{{x1:46,y1:pyEl(v),x2:PW-24,y2:pyEl(v),stroke:'#23262a','stroke-width':1}},ax);
    const t=make('text',{{class:'ax',x:6,y:pyEl(v)+4}},ax); t.textContent=v+' m';}});
  for(let k=0;k<=TOTAL;k+=5){{
    make('line',{{x1:pxKm(k),y1:PH-26,x2:pxKm(k),y2:PH-20,stroke:'#4d5359','stroke-width':1}},ax);
    const t=make('text',{{class:'ax',x:pxKm(k),y:PH-8,'text-anchor':'middle'}},ax);
    t.textContent=k+' km';}}
}}

function puntoEn(km){{
  let i=1; while(i<TR.length-1&&TR[i][2]<km) i++;
  const a=TR[i-1],b=TR[i];
  const f=b[2]>a[2]?(km-a[2])/(b[2]-a[2]):0;
  return [a[0]+(b[0]-a[0])*f, a[1]+(b[1]-a[1])*f, i];
}}
function muestra(km){{
  const t=km/PASO, i=Math.min(PROF.length-1,Math.max(0,Math.floor(t)));
  const j=Math.min(PROF.length-1,i+1), f=t-i;
  return [PROF[i]+(PROF[j]-PROF[i])*f, SEC[i]+(SEC[j]-SEC[i])*f, i];
}}
function reloj(s){{
  const m=Math.floor(s/60), h=Math.floor(m/60);
  return h+':'+String(m%60).padStart(2,'0')+':'+String(Math.floor(s%60)).padStart(2,'0');
}}
function ver(km){{
  km=Math.max(0,Math.min(TOTAL,km));
  const [x,y,i]=puntoEn(km);
  el('marca').setAttribute('cx',x); el('marca').setAttribute('cy',y);
  let d='M'+TR[0][0]+','+TR[0][1];
  for(let k=1;k<i;k++) d+='L'+TR[k][0]+','+TR[k][1];
  el('hecho').setAttribute('d',d+'L'+x.toFixed(1)+','+y.toFixed(1));
  el('perfilMarca').setAttribute('x1',pxKm(km)); el('perfilMarca').setAttribute('x2',pxKm(km));
  const [alt,seg,idx]=muestra(km);
  el('rKm').textContent=km.toFixed(1)+' km';
  el('rFalta').textContent='faltan '+(TOTAL-km).toFixed(1)+' km';
  el('rAlt').textContent=Math.round(alt)+' m';
  const i0=Math.max(0,idx-2), i1=Math.min(PROF.length-1,idx+2);
  const dz=PROF[i1]-PROF[i0], dl=(i1-i0)*PASO*1000;
  el('rPend').textContent=dl?(dz/dl*100).toFixed(1)+'% de pendiente':'';
  el('rTiempo').textContent=reloj(seg);
  const ds=SEC[i1]-SEC[i0];
  el('rVel').textContent=ds>0?(dl/1000/(ds/3600)).toFixed(0)+' km/h':'parado';
  const mun=municipioEn(km);
  marcarMunicipio(mun);
  el('rMun').textContent=mun;
  const tr=TRAMOS.find(t=>t[0]===mun);
  el('rMunSub').textContent = TRAMOS.length>1 && mun===TRAMOS[0][0]
    ? 'hasta el km '+TRAMOS[1][1].toFixed(1)
    : 'desde el km '+tr[1].toFixed(1);
  let best=null;
  LUG.forEach(l=>{{const dd=Math.hypot(l.x-x,l.y-y); if(!best||dd<best[1]) best=[l,dd];}});
  const kmPorPx=({(E - W) * 111.32 * np.cos(np.radians(LAT0)):.4f})/{VW:.0f};
  el('rCerca').textContent=best[0].n;
  el('rCercaSub').textContent='a '+(best[1]*kmPorPx).toFixed(1)+' km en línea recta';
}}
el('km').addEventListener('input',e=>{{parar();ver(+e.target.value);}});

let anim=null;
function parar(){{if(anim){{cancelAnimationFrame(anim);anim=null;
  el('bPlay').setAttribute('aria-pressed','false');el('bPlay').textContent='Recorrer';}}}}
el('bPlay').addEventListener('click',()=>{{
  if(anim){{parar();return;}}
  el('bPlay').setAttribute('aria-pressed','true'); el('bPlay').textContent='Alto';
  let last=null;
  if(+el('km').value>=TOTAL) el('km').value=0;
  const paso=t=>{{
    if(last===null) last=t;
    const dt=Math.min(0.1,(t-last)/1000); last=t;
    let km=+el('km').value+dt*2.4;
    if(km>=TOTAL){{km=TOTAL;el('km').value=km;ver(km);parar();return;}}
    el('km').value=km; ver(km); anim=requestAnimationFrame(paso);
  }};
  anim=requestAnimationFrame(paso);
}});
function toggle(id,g){{
  el(id).addEventListener('click',()=>{{
    const v=el(id).getAttribute('aria-pressed')!=='true';
    el(id).setAttribute('aria-pressed',v);
    el(g).style.display=v?'':'none';
  }});
}}
toggle('bRel','relieve'); toggle('bCur','curvas'); toggle('bPue','pueblos');
toggle('bMun','raya');

ver(0);
window.__ruta=()=>({{puntos:TR.length,total:TOTAL,km:+el('km').value,
  municipio:el('rMun').textContent,cruzados:ETQ_MUN.map(m=>m.n),
  raya:getComputedStyle(el('raya')).display,
  alt:el('rAlt').textContent,vel:el('rVel').textContent,tiempo:el('rTiempo').textContent,
  cerca:el('rCerca').textContent,curvas:document.querySelectorAll('#curvas path').length,
  relieve:getComputedStyle(el('relieve')).display,
  marca:[+el('marca').getAttribute('cx'),+el('marca').getAttribute('cy')]}});
</script>
</body>
</html>
"""

OUT.write_text(DOC, encoding="utf-8")
print(f"escrito {OUT} ({len(DOC):,} bytes)")
