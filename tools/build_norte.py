#!/usr/bin/env python3
"""Generate norte-mexico.html: the six northern border states, every river the
source layer carries, and the sea around them.

Geometry is built offline from the datasets bundled with basemap-data-hires:
  gshhs_f.dat    GSHHG full-resolution shorelines, so the ocean is the real
                 coastline rather than a drawn approximation
  states_f.dat   WDBII internal boundaries
  countries_f.dat  WDBII national boundaries
  rivers_f.dat   WDBII rivers

The six state polygons do not exist in that data as polygons. They are built
by noding the border arcs against the shoreline and polygonizing, then picking
the face that contains a known interior point of each state. Every face is
checked against the published area before it is used; see verify_norte.py.

WDBII stops the Baja California / Sonora border at 31.97 N, so the Colorado's
own course carries it the rest of the way to the Gulf, which is where the
boundary runs in any case.

The river layer has no names in it. Only rivers whose identity can be checked
against two independent anchors are labelled; see the notes on the page.

Usage: python3 build_norte.py      (needs /home/claude/nmex/*.pkl)
"""

import json
import pickle
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union

OUT = Path(__file__).parent.parent / "norte-mexico.html"
DATA = Path("/home/claude/nmex")

SNAPSHOT = "20 de agosto de 2026"

# frame in degrees
W, E, S, N = -118.4, -96.4, 21.2, 33.3
LAT0 = 27.0
VW = 1000.0                       # svg width
SCALE = VW / ((E - W) * np.cos(np.radians(LAT0)))
VH = (N - S) * SCALE

# INEGI, Marco Geoestadístico. Published areas, km2.
STATES = [
    ("Baja California", 71450, (-114.4, 29.4)),
    ("Sonora", 179355, (-110.4, 29.4)),
    ("Chihuahua", 247455, (-106.2, 28.9)),
    ("Coahuila", 151595, (-102.2, 27.2)),
    ("Nuevo León", 64220, (-99.9, 25.9)),
    ("Tamaulipas", 80249, (-98.6, 24.4)),
]

# Tones chosen so every adjacent pair separates: sea/land 1.59:1,
# land/state 1.63:1, rivers 4.7 to 7.6:1 over either. Sea and state fill are
# close in luminance, so the shoreline is always drawn as its own stroke.
C_SEA = "#24425e"     # water
C_LAND = "#1b1f24"    # land outside the six
C_ST = "#3a424b"      # the six states
C_ST_HI = "#59636e"   # hovered
C_COAST = "#5b6b7a"   # shoreline
C_RIV = "#6fb6f5"     # rivers
C_EDGE = "#96a1ad"
C_ACC = "#f5a623"     # the three rivers whose identity checks out
C_SRA = "#4a4a44"     # rugged ground inside the six states
C_ALT = "#6b6353"     # the roughest ground, the crests
C_SRA_O = "#202225"   # the same, outside the six, as context
C_ALT_O = "#2b2b27"


def px(lon):
    return (lon - W) * np.cos(np.radians(LAT0)) * SCALE


def py(lat):
    return (N - lat) * SCALE


def path(coords, close=False):
    pts = [f"{px(x):.1f},{py(y):.1f}" for x, y in coords]
    return "M" + " ".join(pts) + ("Z" if close else "")


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


def km_len(coords):
    a = np.asarray(coords, float)
    dx = np.diff(a[:, 0]) * 111.32 * np.cos(np.radians(a[:-1, 1]))
    dy = np.diff(a[:, 1]) * 110.57
    return float(np.hypot(dx, dy).sum())


FRAME = box(W, S, E, N)
land = pickle.load(open(DATA / "land.pkl", "rb")).intersection(FRAME)
states = pickle.load(open(DATA / "states.pkl", "rb"))
rivers = pickle.load(open(DATA / "rivers.pkl", "rb"))
sierras = pickle.load(open(DATA / "sierras.pkl", "rb"))

# ---- the named rivers, each checked two ways (see verify_norte.py) ----
border = unary_union([LineString(s) for s in
                      pickle.load(open(DATA / "raw.pkl", "rb"))["countries"]])


def on_border(g, tol_km=4):
    c = np.asarray(g.coords)
    tol = tol_km / 111.0
    return sum(1 for p in c if border.distance(Point(p)) < tol) / len(c)


def passes(g, pt, kmtol):
    c = np.asarray(g.coords)
    d = np.hypot((c[:, 0] - pt[0]) * 111.32 * np.cos(np.radians(c[:, 1])),
                 (c[:, 1] - pt[1]) * 110.57)
    return d.min() < kmtol


named = {}
for i, (L, g) in enumerate(rivers):
    if on_border(g) > 0.9 and L > 100:
        named[i] = "Río Bravo"                       # runs on the border itself
    elif passes(g, (-104.42, 29.57), 5) and passes(g, (-105.47, 28.19), 20):
        named[i] = "Río Conchos"                     # mouth at Ojinaga, past Delicias
    elif L > 30 and passes(g, (-115.0, 32.0), 10) and passes(g, (-114.8, 31.9), 25):
        named[i] = "Río Colorado"                    # the delta reach

state_paths, state_js = [], []
for nm, area_km2, (lo, la) in STATES:
    g = states[nm]
    rk = 0.0
    n_riv = 0
    for L, riv in rivers:
        inside = riv.intersection(g)
        if inside.is_empty:
            continue
        n_riv += 1
        for part in (inside.geoms if hasattr(inside, "geoms") else [inside]):
            if part.geom_type == "LineString" and len(part.coords) > 1:
                rk += km_len(part.coords)
    state_paths.append(poly_path(g.intersection(FRAME), 0.006))
    state_js.append(dict(n=nm, a=area_km2, rk=round(rk), nr=n_riv,
                         x=round(px(lo), 1), y=round(py(la), 1)))

river_js = []
for i, (L, g) in enumerate(rivers):
    c = g.intersection(FRAME)
    for part in (c.geoms if hasattr(c, "geoms") else [c]):
        if part.geom_type != "LineString" or len(part.coords) < 2:
            continue
        s = part.simplify(0.004)
        thru = [nm for nm, _, _ in STATES if states[nm].intersects(part)]
        river_js.append(dict(d=path(s.coords), k=round(km_len(part.coords)),
                             n=named.get(i, ""), s=thru))
river_js.sort(key=lambda r: r["k"])

land_path = poly_path(land, 0.008)

# ---- rugged ground -------------------------------------------------------
# Terrain roughness, computed as the local variation of the Natural Earth
# shaded relief at two arc minutes, then thresholded. It is a measure of how
# broken the ground is, not a published range boundary. The threshold was set
# against twenty reference points: ten known sierras all clear it, nine of ten
# known basins and plains fall below it. See verify_norte.py.
six = unary_union(list(states.values()))
sierra_in = sierras["sierra"].intersection(six)
alta_in = sierras["alta"].intersection(six)
sierra_out = sierras["sierra"].difference(six)
alta_out = sierras["alta"].difference(six)

# The two belts and the two named Baja ranges. Each anchor is checked against
# the rugged layer and against the state it is claimed to sit in.
def belt_center(geom):
    pts = []
    for q in (geom.geoms if hasattr(geom, "geoms") else [geom]):
        if q.geom_type == "Polygon":
            pts.extend(q.exterior.coords)
    a = np.asarray(pts)
    return a[:, 0].mean(), a[:, 1].mean()


occ = alta_in.intersection(unary_union([states["Sonora"], states["Chihuahua"]]))
ori = alta_in.intersection(unary_union([states["Coahuila"], states["Nuevo León"],
                                        states["Tamaulipas"]]))
# Only ranges whose position can be checked against the rugged layer and the
# state they sit in are labelled. The Sierra de Juárez sits just north of San
# Pedro Mártir, but the peninsula has no room for both names at this scale.
RANGES = [("Sierra Madre Occidental", belt_center(occ), 13, 0),
          ("Sierra Madre Oriental", belt_center(ori), 13, 0),
          ("Sierra de San Pedro Mártir", (-115.25, 30.75), 9.5, 63)]
range_js = [dict(n=n, x=round(px(lo), 1), y=round(py(la), 1), s=sz, r=rot)
            for n, (lo, la), sz, rot in RANGES]

html_states = "\n".join(
    f'<path class="st" data-i="{i}" d="{p}"/>' for i, p in enumerate(state_paths))

DOC = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>El norte de México · Altazor</title>
<style>
:root{{color-scheme:dark;
--ink:#e6e6e6; --ink2:#9a9a9a; --ink3:#7d7d7d;
--bg:#121212; --panel:#1a1a1a; --line:#2b2b2b; --accent:#58a6ff;
--sea:{C_SEA}; --land:{C_LAND}; --st:{C_ST}; --sthi:{C_ST_HI}; --coast:{C_COAST};
--riv:{C_RIV}; --edge:{C_EDGE}; --acc:{C_ACC};
--sra:{C_SRA}; --alt:{C_ALT}; --sra-o:{C_SRA_O}; --alt-o:{C_ALT_O};}}
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
h1{{font-size:1.6rem;font-weight:400;margin:2.2rem 0 .9rem}}
h2{{font-size:1.05rem;font-weight:400;color:var(--ink);margin:2rem 0 .6rem}}
.sub{{color:var(--ink2);font-size:.95rem;margin:0 0 1.5rem;max-width:70ch}}
figure{{margin:0}}
svg#map{{width:100%;height:auto;display:block;background:var(--sea);border-radius:8px;border:1px solid var(--line)}}
.controls{{display:flex;align-items:center;gap:.85rem;margin:1rem 0 0;flex-wrap:wrap;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;font-size:.9rem}}
input[type=range]{{flex:1;min-width:200px;accent-color:var(--riv);height:22px}}
#kmout{{font-variant-numeric:tabular-nums;min-width:6.5em;text-align:right}}
.readout{{display:flex;gap:.75rem;margin-top:.85rem;flex-wrap:wrap}}
.box{{background:var(--panel);border-radius:8px;padding:.7rem .95rem;min-width:150px}}
.box .lab{{font-size:.78rem;color:var(--ink2)}}
.box .val{{font-size:1.35rem;line-height:1.2;font-variant-numeric:tabular-nums}}
.box .sub2{{font-size:.8rem;color:var(--ink3)}}
.wide{{flex:1;min-width:250px}}
.notes{{margin-top:2.5rem;border-top:1px solid var(--line);padding-top:1.5rem;
color:var(--ink2);font-size:.95rem}}
.notes h2{{font-size:1.05rem;font-weight:400;color:var(--ink);margin:0 0 .6rem}}
.notes p{{margin:0 0 1rem}}
.method{{margin-top:1.5rem;color:var(--ink3);font-size:.88rem}}
.method h2{{font-size:.95rem;font-weight:400;color:var(--ink2);margin:0 0 .6rem}}
.method p{{margin:0 0 .9rem}}
.refs{{font-size:.82rem;color:var(--ink3);max-width:74ch}}
.refs p{{padding-left:2.2em;text-indent:-2.2em;margin:0 0 .8em}}
.refs a{{color:var(--accent);word-break:break-word}}
path.st{{fill:var(--st);stroke:var(--edge);stroke-width:.8;cursor:pointer}}
path.st.hi{{fill:var(--sthi)}}
path.riv{{fill:none;stroke:var(--riv);stroke-linecap:round;stroke-linejoin:round;cursor:pointer}}
path.riv.ctx{{opacity:.4}}
path.riv.named{{stroke:var(--acc)}}
path.riv.hi{{stroke-width:3.2}}
.lbl{{font:400 13px/1 system-ui,sans-serif;fill:#cfd4da;pointer-events:none}}
.leg{{font:400 12px/1 system-ui,sans-serif;fill:var(--ink2)}}
.rng{{font:400 11px/1 system-ui,sans-serif;fill:#b9a882;letter-spacing:.13em;
text-transform:uppercase;pointer-events:none}}
</style>
</head>
<body>
<main>
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Digital Concepts</a></nav>
</header>

<h1>El norte de México</h1>

<figure>
<svg id="map" viewBox="0 0 {VW:.0f} {VH:.0f}" role="img"
  aria-label="Mapa de los seis estados del norte de México, sus ríos y el mar.">
<title>El norte de México: los seis estados fronterizos, sus ríos y el mar</title>
<path d="{land_path}" fill="var(--land)" stroke="var(--coast)" stroke-width="0.9"/>
<g id="sierras-out" style="pointer-events:none">
  <path d="{poly_path(sierra_out, 0.012)}" fill="var(--sra-o)"/>
  <path d="{poly_path(alta_out, 0.012)}" fill="var(--alt-o)"/>
</g>
<g id="states">
{html_states}
</g>
<g id="sierras" style="pointer-events:none">
  <path d="{poly_path(sierra_in, 0.012)}" fill="var(--sra)"/>
  <path d="{poly_path(alta_in, 0.012)}" fill="var(--alt)"/>
</g>
<g id="rivers"></g>
<g id="ranges"></g>
<g id="labels"></g>
<g id="legend">
  <rect x="18" y="{VH-122:.0f}" width="16" height="4" rx="2" fill="var(--riv)"/>
  <text class="leg" x="42" y="{VH-115:.0f}">río</text>
  <rect x="18" y="{VH-98:.0f}" width="16" height="4" rx="2" fill="var(--acc)"/>
  <text class="leg" x="42" y="{VH-91:.0f}">río identificado</text>
  <rect x="18" y="{VH-76:.0f}" width="16" height="10" rx="2" fill="var(--st)" stroke="var(--edge)"/>
  <text class="leg" x="42" y="{VH-67:.0f}">los seis estados</text>
  <rect x="18" y="{VH-52:.0f}" width="16" height="10" rx="2" fill="var(--alt)"/>
  <text class="leg" x="42" y="{VH-43:.0f}">terreno escarpado</text>
  <rect x="18" y="{VH-28:.0f}" width="16" height="10" rx="2" fill="var(--land)"/>
  <text class="leg" x="42" y="{VH-19:.0f}">tierra alrededor</text>
</g>
</svg>
</figure>

<div class="controls">
  <span>Ríos de al menos</span>
  <input type="range" id="minkm" min="0" max="300" step="5" value="0" aria-label="Longitud mínima del río">
  <span id="kmout">0 km</span>
</div>

<div class="readout">
  <div class="box"><div class="lab">ríos en el cuadro</div>
    <div class="val" id="nriv"></div><div class="sub2" id="krivs"></div></div>
  <div class="box wide"><div class="lab" id="hovlab">nada bajo el cursor</div>
    <div class="val" id="hovname" style="font-size:1.05rem"></div>
    <div class="sub2" id="hovsub"></div></div>
</div>

<div class="notes">
<h2>Sobre el mapa</h2>
<p class="sub">Baja California, Sonora, Chihuahua, Coahuila, Nuevo León y
Tamaulipas. Instantánea del {SNAPSHOT}.</p>
<p>La barra va quitando los ríos cortos hasta dejar solo el esqueleto de los
grandes drenajes. Un estado bajo el cursor muestra su superficie y cuántos
kilómetros de río lo cruzan; un río, su longitud dentro del cuadro y los
estados por los que pasa.</p>
<p>La costa es la línea real y no un trazo aproximado, así que el Golfo de
California, el Pacífico y el Golfo de México quedan donde están.</p>
<p>El terreno escarpado mide qué tan quebrado está el suelo; no es el límite
publicado de cada sierra. De ahí salen las dos Sierras Madre: la Occidental
por el oriente de Sonora y el poniente de Chihuahua, la Oriental por Coahuila,
Nuevo León y Tamaulipas.</p>
</div>

<h2>Referencias</h2>
<div class="refs">
<p>Instituto Nacional de Estadística y Geografía. (2023). <em>Marco
geoestadístico, diciembre 2023</em> [Conjunto de datos]. INEGI.
<a href="https://www.inegi.org.mx/temas/mg/">https://www.inegi.org.mx/temas/mg/</a></p>
<p>Natural Earth. (2022). <em>Natural Earth II with shaded relief</em>
(1:10m, versión 5.1) [Conjunto de datos]. North American Cartographic
Information Society.
<a href="https://www.naturalearthdata.com/">https://www.naturalearthdata.com/</a></p>
<p>Soluri, E. A., &amp; Woodson, V. A. (1990). World Vector Shoreline.
<em>International Hydrographic Review, 67</em>(1), 27-35.</p>
<p>Wessel, P., &amp; Smith, W. H. F. (1996). A global, self-consistent,
hierarchical, high-resolution shoreline database. <em>Journal of Geophysical
Research: Solid Earth, 101</em>(B4), 8741-8743.
<a href="https://doi.org/10.1029/96JB00104">https://doi.org/10.1029/96JB00104</a></p>
</div>
</main>
<script>
var ST={json.dumps(state_js, ensure_ascii=False)};
var RV={json.dumps(river_js, ensure_ascii=False)};
var RG={json.dumps(range_js, ensure_ascii=False)};
var NS="http://www.w3.org/2000/svg";
var rg=document.getElementById("rivers"), lg=document.getElementById("labels");
var gg=document.getElementById("ranges");

RG.forEach(function(r){{
  var t=document.createElementNS(NS,"text");
  t.setAttribute("class","rng"); t.setAttribute("x",r.x); t.setAttribute("y",r.y);
  t.setAttribute("text-anchor","middle");
  t.setAttribute("style","font-size:"+r.s+"px");
  if (r.r) t.setAttribute("transform","rotate("+r.r+" "+r.x+" "+r.y+")");
  t.textContent=r.n; gg.appendChild(t);
}});
var hl=document.getElementById("hovlab"), hn=document.getElementById("hovname"),
    hs=document.getElementById("hovsub");
function fmt(n){{return n.toLocaleString("es-MX");}}
function hov(lab,a,b){{hl.textContent=lab;hn.textContent=a;hs.textContent=b;}}

var rEls=[];
RV.forEach(function(r,i){{
  var p=document.createElementNS(NS,"path");
  p.setAttribute("d",r.d); p.setAttribute("class","riv"+(r.n?" named":"")+(r.s.length?"":" ctx"));
  p.setAttribute("stroke-width", r.k>250?2.0:r.k>100?1.4:r.k>40?1.0:0.7);
  p.addEventListener("mouseenter",function(){{
    p.classList.add("hi");
    hov("río", r.n||"sin nombre en la capa",
        fmt(r.k)+" km en el cuadro"+(r.s.length?" · "+r.s.join(", "):""));
  }});
  p.addEventListener("mouseleave",function(){{p.classList.remove("hi");}});
  rg.appendChild(p); rEls.push(p);
}});

document.querySelectorAll("path.st").forEach(function(p){{
  var s=ST[+p.dataset.i];
  p.addEventListener("mouseenter",function(){{
    p.classList.add("hi");
    hov("estado", s.n, fmt(s.a)+" km² · "+fmt(s.rk)+" km de río en "+s.nr+" cauces");
  }});
  p.addEventListener("mouseleave",function(){{p.classList.remove("hi");}});
}});
ST.forEach(function(s){{
  var t=document.createElementNS(NS,"text");
  t.setAttribute("class","lbl"); t.setAttribute("x",s.x); t.setAttribute("y",s.y);
  t.setAttribute("text-anchor","middle"); t.textContent=s.n;
  lg.appendChild(t);
}});

var sl=document.getElementById("minkm");
function draw(){{
  var m=+sl.value, n=0, tot=0;
  RV.forEach(function(r,i){{
    var on=r.k>=m;
    rEls[i].style.display=on?"":"none";
    if(on){{n++; tot+=r.k;}}
  }});
  document.getElementById("nriv").textContent=n;
  document.getElementById("krivs").textContent=fmt(tot)+" km en total";
  document.getElementById("kmout").textContent=m+" km";
}}
sl.addEventListener("input",draw);
draw();
</script>
</body>
</html>
"""

OUT.write_text(DOC, encoding="utf-8")
print(f"wrote {OUT} ({len(DOC):,} bytes): {len(state_js)} states, "
      f"{len(river_js)} river lines, {sum(r['k'] for r in river_js):,} km, "
      f"{len(set(named.values()))} named")
