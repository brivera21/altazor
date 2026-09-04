#!/usr/bin/env python3
"""Genera cabalgata-villista.html: el corredor de la Cabalgata Binacional
Villista, de Bachíniva a Columbus, Nuevo México.

La geometría del fondo sale de los mismos datos que norte-mexico.html:

  states.pkl   los seis estados del norte, cortados de los arcos de la WDBII
  rivers.pkl   la capa de ríos de la WDBII, con su longitud
  sierras.pkl  terreno escarpado medido sobre la imagen de relieve sombreado

Del lado de Estados Unidos se usan los polígonos de us.html, que salen del
mapa de condados del Censo.

La traza y las paradas vienen de villista_data.py; ahí está de dónde salió
cada cosa.

Uso: python3 build_villista.py
"""

import json
import pickle
import apa
from pathlib import Path

import numpy as np
from shapely.geometry import box
from shapely.ops import unary_union

import villista_data as V

OUT = Path(__file__).parent.parent / "cabalgata-villista.html"
NMEX = Path("/home/claude/nmex")
USA = Path("/home/claude/us")

W, E, S, N = -110.2, -105.6, 28.25, 32.15
LAT0 = 30.2
VW = 980.0
SCALE = VW / ((E - W) * np.cos(np.radians(LAT0)))
VH = (N - S) * SCALE

C_LAND = "#1b1f24"      # tierra de contexto
C_MX = "#333b44"        # Chihuahua y Sonora
C_US = "#2a3138"        # el lado de Estados Unidos
C_EDGE = "#8d98a4"      # límites estatales
C_LINE = "#c3ccd6"      # la línea internacional
C_RIV = "#6fb6f5"
C_SRA = "#414139"       # terreno escarpado
C_ALT = "#5c5749"       # lo más quebrado
C_RUTA = "#f5a623"      # el corredor
C_HITO = "#e2725b"      # 1916


def px(lon):
    return (lon - W) * np.cos(np.radians(LAT0)) * SCALE


def py(lat):
    return (N - lat) * SCALE


def path(coords, close=False):
    return "M" + " ".join(f"{px(x):.1f},{py(y):.1f}" for x, y in coords) + \
        ("Z" if close else "")


def poly_path(geom, tol):
    out = []
    for g in (geom.geoms if hasattr(geom, "geoms") else [geom]):
        g = g.simplify(tol)
        if g.is_empty:
            continue
        out.append(path(g.exterior.coords, True))
        for r in g.interiors:
            out.append(path(r.coords, True))
    return "".join(out)


def track_points():
    """TRACK viene en diferencias de 1e-5 grados: lat, lon, lat, lon."""
    v = [int(x) for x in "".join(V.TRACK).split(",")]
    lat, lon = v[0], v[1]
    pts = [(lat / 1e5, lon / 1e5)]
    for i in range(2, len(v), 2):
        lat += v[i]
        lon += v[i + 1]
        pts.append((lat / 1e5, lon / 1e5))
    return pts


def km_between(a, b):
    return float(np.hypot((b[1] - a[1]) * 111.32 * np.cos(np.radians(a[0])),
                          (b[0] - a[0]) * 110.57))


def vertex_km(pts):
    """Kilómetro de cada vértice, amarrado al kilometraje de las paradas.

    La traza dibujada está simplificada y mide algo menos que el camino que
    se ruteó, así que entre parada y parada se estira para que cada cabecera
    caiga en su kilómetro."""
    cum = [0.0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + km_between(pts[i - 1], pts[i]))
    out = [0.0] * len(pts)
    for (n0, k0), (n1, k1) in zip(
            [(s[6], s[7]) for s in V.STOPS][:-1],
            [(s[6], s[7]) for s in V.STOPS][1:]):
        span = cum[n1] - cum[n0]
        for i in range(n0, n1 + 1):
            f = (cum[i] - cum[n0]) / span if span else 0.0
            out[i] = k0 + f * (k1 - k0)
    return out


pts = track_points()
kms = vertex_km(pts)
total_km = V.STOPS[-1][7]
drawn_km = sum(km_between(pts[i - 1], pts[i]) for i in range(1, len(pts)))
print(f"traza: {len(pts)} puntos, {drawn_km:.0f} km dibujados sobre "
      f"{total_km:.0f} km ruteados")

FRAME = box(W, S, E, N)
states = pickle.load(open(NMEX / "states.pkl", "rb"))
rivers = pickle.load(open(NMEX / "rivers.pkl", "rb"))
sierras = pickle.load(open(NMEX / "sierras.pkl", "rb"))
us_states = pickle.load(open(USA / "states.pkl", "rb"))
land = pickle.load(open(NMEX / "land.pkl", "rb")).intersection(FRAME)

mx = [states[n].intersection(FRAME) for n in ("Chihuahua", "Sonora")]
us = [us_states[c].intersection(FRAME) for c in ("NM", "AZ", "TX")]
mx_path = "".join(poly_path(g, 0.004) for g in mx if not g.is_empty)
us_path = "".join(poly_path(g, 0.004) for g in us if not g.is_empty)
land_path = poly_path(land, 0.01)

mx_union = unary_union([g for g in mx if not g.is_empty])
us_union = unary_union([g for g in us if not g.is_empty])
frontera = mx_union.boundary.intersection(us_union.buffer(0.015))
frontera_d = "".join(path(g.simplify(0.004).coords)
                     for g in (frontera.geoms if hasattr(frontera, "geoms") else [frontera])
                     if g.geom_type == "LineString" and len(g.coords) > 1)
print(f"línea internacional: {frontera.length * 96:.0f} km en el cuadro")

sra = sierras["sierra"].intersection(FRAME)
alt = sierras["alta"].intersection(FRAME)
sra_path = poly_path(sra, 0.012)
alt_path = poly_path(alt, 0.012)

riv_paths = []
for length, line in rivers:
    g = line.intersection(FRAME)
    if g.is_empty or length < 60:
        continue
    for part in (g.geoms if hasattr(g, "geoms") else [g]):
        if part.geom_type != "LineString" or len(part.coords) < 2:
            continue
        riv_paths.append((length, path(part.simplify(0.004).coords)))
riv_html = "\n".join(
    f'<path class="riv" style="stroke-width:{min(2.6, 0.7 + l / 420):.2f}" d="{d}"/>'
    for l, d in riv_paths)
print(f"ríos en el cuadro: {len(riv_paths)}")

ruta_d = path([(lo, la) for la, lo in pts])
# dónde va la etiqueta de cada parada cuando dos caen encima
LAB = {"Columbus": (10, -3, "start"), "Puerto Palomas": (10, 13, "start"),
       "Nuevo Casas Grandes": (10, -3, "start"), "Casas Grandes": (-10, 11, "end"),
       "Matachí": (-10, 2, "end"), "Temósachic": (10, -4, "start"),
       "Bachíniva": (10, 4, "start"), "Ciudad Guerrero": (-10, 4, "end")}

stops_js = [dict(n=s[0], m=s[1], la=s[2], lo=s[3], el=s[4], p=s[5],
                 i=s[6], km=s[7], x=round(px(s[3]), 1), y=round(py(s[2]), 1),
                 lab=LAB.get(s[0]))
            for s in V.STOPS]
track_js = [[round(px(lo), 1), round(py(la), 1), round(k, 2)]
            for (la, lo), k in zip(pts, kms)]
prof_js = [int(x) for x in "".join(V.PROF).split(",")]

# los cuatro pueblos de donde salieron los hombres en 1916, y los dos extremos
RECLUTA = [("Cuauhtémoc", 28.4053, -106.8667), ("Bachíniva", 28.7650, -107.2540),
           ("Namiquipa", 29.2507, -107.4151), ("Ignacio Zaragoza", 29.6427, -107.7637)]
hitos_js = [dict(n=n, x=round(px(lo), 1), y=round(py(la), 1), t=t)
            for n, la, lo, t in V.HITOS]
recluta_js = [dict(n=n, x=round(px(lo), 1), y=round(py(la), 1)) for n, la, lo in RECLUTA]

# ciudades de referencia, para saber dónde cae el mapa
REF = [("Chihuahua", 28.6353, -106.0889), ("Ciudad Juárez", 31.7333, -106.4869),
       ("Cuauhtémoc", 28.4053, -106.8667), ("Namiquipa", 29.2507, -107.4151)]
ref_js = [dict(n=n, x=round(px(lo), 1), y=round(py(la), 1))
          for n, la, lo in REF if S < la < N and W < lo < E]

PW, PH = 980.0, 168.0     # el perfil

DOC = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cabalgata Binacional Villista · Altazor</title>
<style>
:root{{color-scheme:dark;
--ink:#e6e6e6; --ink2:#9a9a9a; --ink3:#7d7d7d;
--bg:#121212; --panel:#1a1a1a; --line:#2b2b2b; --accent:#58a6ff;
--land:{C_LAND}; --mx:{C_MX}; --us:{C_US}; --edge:{C_EDGE}; --border:{C_LINE};
--riv:{C_RIV}; --sra:{C_SRA}; --alt:{C_ALT}; --ruta:{C_RUTA}; --hito:{C_HITO};}}
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
button.ctl:hover{{color:var(--ink);border-color:var(--edge)}}
button.ctl[aria-pressed="true"]{{color:#12161a;background:var(--ink2);border-color:var(--ink2)}}
input[type=range]{{flex:1;min-width:220px;accent-color:var(--ruta);height:22px}}
.readout{{display:flex;gap:.75rem;margin-top:.85rem;flex-wrap:wrap;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
.box{{background:var(--panel);border-radius:8px;padding:.7rem .95rem;min-width:150px}}
.box .lab{{font-size:.78rem;color:var(--ink2)}}
.box .val{{font-size:1.35rem;line-height:1.2;font-variant-numeric:tabular-nums}}
.box .sub2{{font-size:.8rem;color:var(--ink3)}}
.wide{{flex:1;min-width:260px}}
.notes{{margin-top:2.5rem;border-top:1px solid var(--line);padding-top:1.5rem;
color:var(--ink2);font-size:.95rem}}
.notes p{{margin:0 0 1rem;max-width:74ch}}
.method{{margin-top:1.5rem;color:var(--ink3);font-size:.88rem}}
.method p{{margin:0 0 .9rem;max-width:74ch}}
.refs{{font-size:.82rem;color:var(--ink3);max-width:74ch}}
.refs p{{padding-left:2.2em;text-indent:-2.2em;margin:0 0 .8em}}
.refs a{{color:var(--accent);word-break:break-word}}
path.riv{{fill:none;stroke:var(--riv);stroke-opacity:.55;stroke-linecap:round}}
#ruta path{{fill:none;stroke:var(--ruta);stroke-width:2.6;stroke-linejoin:round;
stroke-linecap:round}}
#hecho{{fill:none;stroke:#ffd48a;stroke-width:4.2;stroke-linejoin:round;stroke-linecap:round}}
circle.stop{{fill:#0f1216;stroke:var(--ruta);stroke-width:2;cursor:pointer}}
circle.stop.on{{fill:var(--ruta)}}
.lbl{{font:400 12px/1 system-ui,sans-serif;fill:#cdd3da;pointer-events:none}}
.lbl.ref{{fill:#79828c;font-size:11.5px}}
.lbl.hito{{fill:#f0a894;font-size:11.5px}}
.leg{{font:400 12px/1 system-ui,sans-serif;fill:var(--ink2)}}
.ax{{font:400 11px/1 system-ui,sans-serif;fill:var(--ink3)}}
</style>
</head>
<body>
<main>
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library</a></nav>
</header>

<h1>Cabalgata Binacional Villista</h1>

<div class="tiles">
  <div class="tile"><div class="k">salida</div><div class="v">Bachíniva</div>
    <div class="g">de la hacienda de San Gerónimo salió la columna en 1916</div></div>
  <div class="tile"><div class="k">llegada</div><div class="v">Columbus</div>
    <div class="g">Nuevo México, cruzando la línea en Puerto Palomas</div></div>
  <div class="tile"><div class="k">corredor</div><div class="v">{total_km:.0f} km</div>
    <div class="g">medidos sobre la traza de caminos entre cabeceras</div></div>
  <div class="tile"><div class="k">primera edición</div><div class="v">1999</div>
    <div class="g">aquella vez se juntaron más de 125 jinetes</div></div>
</div>

<figure>
<svg id="map" viewBox="0 0 {VW:.0f} {VH:.0f}" role="img"
  aria-label="Mapa del noroeste de Chihuahua y el sur de Nuevo México con el corredor de la cabalgata.">
<title>El corredor de la Cabalgata Binacional Villista</title>
<path d="{land_path}" fill="var(--land)"/>
<path d="{us_path}" fill="var(--us)" stroke="var(--edge)" stroke-width="0.7"/>
<path d="{mx_path}" fill="var(--mx)" stroke="var(--edge)" stroke-width="0.7"/>
<path id="frontera" d="{frontera_d}" fill="none" stroke="var(--border)" stroke-width="1.5"/>
<g id="relieve">
  <path d="{sra_path}" fill="var(--sra)" fill-opacity=".85"/>
  <path d="{alt_path}" fill="var(--alt)" fill-opacity=".85"/>
</g>
<g id="rios">
{riv_html}
</g>
<g id="ruta"><path d="{ruta_d}"/></g>
<path id="hecho" d=""/>
<g id="paradas"></g>
<g id="hitos" style="display:none"></g>
<g id="etiquetas"></g>
<circle id="jinete" r="5.5" fill="#fff3d6" stroke="#8a5a12" stroke-width="1.5"/>
<g id="legend">
  <rect x="8" y="{VH-118:.0f}" width="212" height="112" rx="8" fill="#0f1216" fill-opacity=".72"/>
  <rect x="18" y="{VH-104:.0f}" width="16" height="4" rx="2" fill="var(--ruta)"/>
  <text class="leg" x="42" y="{VH-97:.0f}">corredor de la cabalgata</text>
  <rect x="18" y="{VH-82:.0f}" width="16" height="4" rx="2" fill="var(--riv)"/>
  <text class="leg" x="42" y="{VH-75:.0f}">río</text>
  <rect x="18" y="{VH-60:.0f}" width="16" height="10" rx="2" fill="var(--alt)"/>
  <text class="leg" x="42" y="{VH-51:.0f}">terreno escarpado</text>
  <rect x="18" y="{VH-36:.0f}" width="16" height="10" rx="2" fill="var(--mx)" stroke="var(--edge)"/>
  <text class="leg" x="42" y="{VH-27:.0f}">Chihuahua y Sonora</text>
</g>
</svg>

<svg id="perfil" viewBox="0 0 {PW:.0f} {PH:.0f}" role="img"
  aria-label="Altitud del corredor, de la sierra al desierto.">
<title>Altitud del corredor</title>
<path id="perfilArea" d="" fill="#2a2a22"/>
<path id="perfilLinea" d="" fill="none" stroke="var(--ruta)" stroke-width="1.6"/>
<g id="perfilEjes"></g>
<line id="perfilMarca" x1="0" y1="14" x2="0" y2="{PH-26:.0f}" stroke="#fff3d6" stroke-width="1.4"/>
</svg>
</figure>

<div class="controls">
  <button class="ctl" id="bPlay" aria-pressed="false">Recorrer</button>
  <input type="range" id="km" min="0" max="{total_km:.1f}" step="0.5" value="0"
    aria-label="Kilómetro del corredor">
  <button class="ctl" id="bRel" aria-pressed="true">Relieve</button>
  <button class="ctl" id="bRio" aria-pressed="true">Ríos</button>
  <button class="ctl" id="b1916" aria-pressed="false">1916</button>
</div>

<div class="readout">
  <div class="box"><div class="lab">kilómetro</div>
    <div class="val" id="rKm">0</div><div class="sub2" id="rFalta"></div></div>
  <div class="box"><div class="lab">altitud</div>
    <div class="val" id="rAlt"></div><div class="sub2">sobre el nivel del mar</div></div>
  <div class="box wide"><div class="lab" id="rLab">tramo</div>
    <div class="val" id="rTramo" style="font-size:1.05rem"></div>
    <div class="sub2" id="rSub"></div></div>
</div>

<div class="notes">
<p>La cabalgata sale de Bachíniva a finales de febrero y llega a Columbus el
sábado más cercano al 9 de marzo, el día del ataque de 1916. La edición de 2026
se hizo en dieciocho días con más de doscientos jinetes, por los municipios que
van marcados aquí.</p>
<p>Nadie publica los campamentos de cada noche, solo los municipios, así que la
línea une las cabeceras por caminos que existen. El perfil lleva la misma
cuenta: se sale de la sierra alta y se llega al desierto ochocientos metros
más abajo, y la parte más pesada queda entre Madera y Ignacio Zaragoza.</p>
</div>

<div class="method">
<p>La traza se armó tramo por tramo sobre la red de caminos de OpenStreetMap
con BRouter, con el perfil de caminos vecinales, salvo tres tramos donde ese
perfil se alargaba más de una cuarta parte sobre la carretera y ahí se tomó la
carretera. No es el itinerario oficial de la cabalgata y no pretende serlo: es
el corredor por donde va, medido sobre caminos reales. El terreno escarpado es
una medida de qué tan quebrado está el suelo, sacada de la imagen de relieve
sombreado, no el límite publicado de ninguna sierra. De 1916 se marcan
solamente los dos extremos y los pueblos de donde salieron los hombres, porque
el camino que siguió la columna entre una fecha y otra no aparece en las
fuentes consultadas.</p>
</div>

<h2>Referencias</h2>
<div class="refs">
<p>Gobierno del Estado de Chihuahua. (2026, 27 de febrero). <em>Arranca en
Bachíniva la tradicional Cabalgata Binacional Villista</em>.
<a href="https://www.chihuahua.gob.mx/prensa/arranca-en-bachiniva-la-tradicional-cabalgata-binacional-villista">https://www.chihuahua.gob.mx/prensa/arranca-en-bachiniva-la-tradicional-cabalgata-binacional-villista</a></p>
<p>Crónica de Chihuahua. (2016, 17 de febrero). <em>Se cumplen 100 años de la
partida de Villa a Columbus</em>.
<a href="https://www.cronicadechihuahua.com/Se-cumplen-100-anos-de-la-partida.html">https://www.cronicadechihuahua.com/Se-cumplen-100-anos-de-la-partida.html</a></p>
<p>Village of Columbus, New Mexico. (2025). <em>A historic celebration:
Cabalgata Fiesta de Amistad 2025</em>.
<a href="https://villageofcolumbusnm.com/a-historic-celebration-cabalgata-fiesta-de-amistad-2025/">https://villageofcolumbusnm.com/a-historic-celebration-cabalgata-fiesta-de-amistad-2025/</a></p>
<p>OpenStreetMap contributors. (2026). <em>OpenStreetMap</em> [Conjunto de
datos]. <a href="https://www.openstreetmap.org/copyright">https://www.openstreetmap.org/copyright</a></p>
<p>Wessel, P., &amp; Smith, W. H. F. (1996). A global, self-consistent,
hierarchical, high-resolution shoreline database. <em>Journal of Geophysical
Research: Solid Earth, 101</em>(B4), 8741-8743.
<a href="https://doi.org/10.1029/96JB00104">https://doi.org/10.1029/96JB00104</a></p>
<p>Natural Earth. (2022). <em>Natural Earth II with shaded relief</em>
(1:10m, versión 5.1) [Conjunto de datos]. North American Cartographic
Information Society.
<a href="https://www.naturalearthdata.com/downloads/10m-raster-data/10m-natural-earth-2/">https://www.naturalearthdata.com/downloads/10m-raster-data/10m-natural-earth-2/</a></p>
</div>
</main>
<script>
const TRACK={json.dumps(track_js)};
const STOPS={json.dumps(stops_js, ensure_ascii=False)};
const PROF={json.dumps(prof_js)};
const HITOS={json.dumps(hitos_js, ensure_ascii=False)};
const RECLUTA={json.dumps(recluta_js, ensure_ascii=False)};
const REF={json.dumps(ref_js, ensure_ascii=False)};
const STEP={V.STEP_KM};
const TOTAL={total_km};
const PW={PW}, PH={PH};
const el=id=>document.getElementById(id);
const SVGNS='http://www.w3.org/2000/svg';
function make(t,a,p){{const e=document.createElementNS(SVGNS,t);
  for(const k in a) e.setAttribute(k,a[k]); if(p) p.appendChild(e); return e;}}

// paradas y etiquetas
const gp=el('paradas'), gl=el('etiquetas');
STOPS.forEach((s,i)=>{{
  const c=make('circle',{{class:'stop',cx:s.x,cy:s.y,r:i===0||i===STOPS.length-1?5.5:4,
    'data-i':i}},gp);
  c.addEventListener('mouseenter',()=>marcar(i));
  c.addEventListener('click',()=>{{el('km').value=s.km;ver(s.km);}});
  const der=s.x<VWmid();
  const L=s.lab||[der?9:-9,4,der?'start':'end'];
  const t=make('text',{{class:'lbl',x:s.x+L[0],y:s.y+L[1],'text-anchor':L[2]}},gl);
  t.textContent=s.n;
}});
function VWmid(){{return {VW/2:.0f};}}
REF.forEach(r=>{{
  make('circle',{{cx:r.x,cy:r.y,r:2.4,fill:'#79828c'}},gl);
  const t=make('text',{{class:'lbl ref',x:r.x+7,y:r.y+3.5}},gl); t.textContent=r.n;
}});

// 1916
const gh=el('hitos');
RECLUTA.forEach(r=>{{
  make('circle',{{cx:r.x,cy:r.y,r:3.4,fill:'none',stroke:'{C_HITO}','stroke-width':1.4}},gh);
  const t=make('text',{{class:'lbl hito',x:r.x+7,y:r.y+11}},gh); t.textContent=r.n;
}});
HITOS.forEach(h=>{{
  make('path',{{d:`M${{h.x-6}},${{h.y}}h12M${{h.x}},${{h.y-6}}v12`,
    stroke:'{C_HITO}','stroke-width':2}},gh);
  const t=make('text',{{class:'lbl hito',x:h.x+9,y:h.y-6}},gh); t.textContent=h.t;
}});

// perfil
const elMin=Math.min(...PROF), elMax=Math.max(...PROF);
const pxKm=k=>46+(k/TOTAL)*(PW-70);
const pyEl=e=>PH-26-((e-elMin)/(elMax-elMin))*(PH-52);
{{
  let d='';
  PROF.forEach((e,i)=>{{const k=Math.min(i*STEP,TOTAL);
    d+=(i?'L':'M')+pxKm(k).toFixed(1)+','+pyEl(e).toFixed(1);}});
  el('perfilLinea').setAttribute('d',d);
  el('perfilArea').setAttribute('d',d+`L${{pxKm(TOTAL).toFixed(1)}},${{PH-26}}L${{pxKm(0).toFixed(1)}},${{PH-26}}Z`);
  const ax=el('perfilEjes');
  [elMin,Math.round((elMin+elMax)/2/50)*50,elMax].forEach(v=>{{
    make('line',{{x1:46,y1:pyEl(v),x2:PW-24,y2:pyEl(v),stroke:'#23262a','stroke-width':1}},ax);
    const t=make('text',{{class:'ax',x:6,y:pyEl(v)+4}},ax); t.textContent=v+' m';}});
  STOPS.forEach((s,i)=>{{
    make('line',{{x1:pxKm(s.km),y1:PH-26,x2:pxKm(s.km),y2:PH-20,stroke:'#4d5359','stroke-width':1}},ax);
    if(i%2===0||i===STOPS.length-1){{
      const t=make('text',{{class:'ax',x:pxKm(s.km),y:PH-8,'text-anchor':'middle'}},ax);
      t.textContent=s.km.toFixed(0);}}
  }});
}}

function puntoEn(km){{
  let i=1;
  while(i<TRACK.length-1&&TRACK[i][2]<km) i++;
  const a=TRACK[i-1], b=TRACK[i];
  const f=b[2]>a[2]?(km-a[2])/(b[2]-a[2]):0;
  return [a[0]+(b[0]-a[0])*f, a[1]+(b[1]-a[1])*f, i];
}}
function alturaEn(km){{
  const t=km/STEP, i=Math.min(PROF.length-1,Math.floor(t));
  const j=Math.min(PROF.length-1,i+1), f=t-i;
  return PROF[i]+(PROF[j]-PROF[i])*f;
}}
function marcar(i){{
  [...gp.children].forEach((c,k)=>c.classList.toggle('on',k===i));
}}
function ver(km){{
  km=Math.max(0,Math.min(TOTAL,km));
  const [x,y,i]=puntoEn(km);
  el('jinete').setAttribute('cx',x); el('jinete').setAttribute('cy',y);
  let d='M'+TRACK[0][0]+','+TRACK[0][1];
  for(let k=1;k<i;k++) d+='L'+TRACK[k][0]+','+TRACK[k][1];
  d+='L'+x.toFixed(1)+','+y.toFixed(1);
  el('hecho').setAttribute('d',d);
  el('perfilMarca').setAttribute('x1',pxKm(km)); el('perfilMarca').setAttribute('x2',pxKm(km));
  el('rKm').textContent=km.toFixed(0)+' km';
  el('rFalta').textContent='faltan '+(TOTAL-km).toFixed(0)+' km';
  el('rAlt').textContent=Math.round(alturaEn(km))+' m';
  let j=0; while(j<STOPS.length-1&&STOPS[j+1].km<=km) j++;
  const a=STOPS[j], b=STOPS[Math.min(STOPS.length-1,j+1)];
  marcar(km-a.km<b.km-km?j:Math.min(STOPS.length-1,j+1));
  el('rLab').textContent = km>=TOTAL?'llegada':'tramo';
  el('rTramo').textContent = km>=TOTAL? b.n+', '+b.m : a.n+' a '+b.n;
  const pob=b.p?b.p.toLocaleString('es-MX')+' habitantes':'sin población en el padrón';
  el('rSub').textContent = km>=TOTAL
    ? 'del otro lado de la línea, '+pob
    : 'municipio de '+b.m+', '+b.el+' m, '+pob;
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
    let km=+el('km').value+dt*45;
    if(km>=TOTAL){{km=TOTAL;el('km').value=km;ver(km);parar();return;}}
    el('km').value=km; ver(km);
    anim=requestAnimationFrame(paso);
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
toggle('bRel','relieve'); toggle('bRio','rios'); toggle('b1916','hitos');

ver(0);
window.__villista=()=>({{puntos:TRACK.length,paradas:STOPS.length,
  km:+el('km').value,total:TOTAL,alt:el('rAlt').textContent,
  tramo:el('rTramo').textContent,rios:document.querySelectorAll('#rios path').length,
  hitos:getComputedStyle(el('hitos')).display,
  jinete:[+el('jinete').getAttribute('cx'),+el('jinete').getAttribute('cy')]}});
</script>
</body>
</html>
"""

DOC = apa.css_pass(DOC)
OUT.write_text(DOC, encoding="utf-8")
print(f"escrito {OUT} ({len(DOC):,} bytes): {len(V.STOPS)} paradas, "
      f"{len(riv_paths)} ríos, {len(pts)} puntos de traza")
