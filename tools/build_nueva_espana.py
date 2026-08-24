#!/usr/bin/env python3
"""Genera nueva-espana.html: la Nueva España de 1519 a 1853, año por año.

La geometría del fondo:
  gshhs_f.dat   la costa, de Panamá a Oregón, a resolución completa
  states.pkl    los treinta y dos estados de México, de make_mx_data.py
  states.pkl    los estados de Estados Unidos, de make_us_data.py

Con esos dos juegos de estados se arman las entidades de 1824 y lo que se
perdió en 1836, 1848 y 1853: son moldes de hoy puestos sobre líneas de ayer,
así que sus orillas son aproximadas y la página lo dice.

Los hechos, los caminos y las villas están en nueva_espana_data.py, cada uno
con su fecha y su nota.

Uso: python3 build_nueva_espana.py
"""

import json
import math
import pickle
from pathlib import Path

import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

import nueva_espana_data as D

OUT = Path(__file__).parent.parent / "nueva-espana.html"
LAND = Path("/home/claude/ne_land.pkl")
MX = Path("/home/claude/mx/states.pkl")
US = Path("/home/claude/us/states.pkl")

W, E, S, N = -128.5, -76.5, 6.0, 50.5
VW = 1000.0
# cónica de Albers, con los paralelos de referencia adentro del cuadro
PH1, PH2, PH0, LA0 = 12.0, 42.0, 25.0, -101.0

C_MAR = "#0d1a26"
C_TIERRA = "#39424c"
C_FUERA = "#242b33"        # tierra que nunca fue de la corona
C_ESTADO = "#7c5f8f"       # las entidades de 1824
C_TERR = "#4d7a8c"
C_PERDIDO = "#5a4340"
C_RUTA = "#f5a623"
C_LLEGADA = "#e2725b"
C_VILLA = "#7fd4c1"
C_LINEA = "#e8dcc0"


def albers():
    r = math.radians
    n = (math.sin(r(PH1)) + math.sin(r(PH2))) / 2
    C = math.cos(r(PH1)) ** 2 + 2 * n * math.sin(r(PH1))
    rho0 = math.sqrt(C - 2 * n * math.sin(r(PH0))) / n

    def f(lon, lat):
        rho = math.sqrt(max(0.0, C - 2 * n * math.sin(r(lat)))) / n
        th = n * r(lon - LA0)
        return rho * math.sin(th), rho0 - rho * math.cos(th)
    return f


PROJ = albers()


def fit():
    """El cuadro, ajustado a la ventana. Albers cuenta la y hacia el norte y
    el svg hacia abajo, así que el eje se voltea."""
    pts = []
    for lo in np.linspace(W, E, 40):
        for la in (S, N):
            pts.append(PROJ(lo, la))
    for la in np.linspace(S, N, 40):
        for lo in (W, E):
            pts.append(PROJ(lo, la))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    k = VW / (max(xs) - min(xs))
    vh = (max(ys) - min(ys)) * k
    x0, y1 = min(xs), max(ys)

    def T(lon, lat):
        x, y = PROJ(lon, lat)
        return (x - x0) * k, (y1 - y) * k
    return T, vh


T, VH = fit()


def path_of(g, tol=0.02):
    out = []
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        q = p.simplify(tol)
        if q.is_empty:
            continue
        for ring in [q.exterior] + list(q.interiors):
            c = list(ring.coords)
            if len(c) < 4:
                continue
            out.append("M" + " ".join(f"{T(x, y)[0]:.1f},{T(x, y)[1]:.1f}"
                                     for x, y in c) + "Z")
    return "".join(out)


def line_of(pts):
    return "M" + " ".join(f"{T(lo, la)[0]:.1f},{T(lo, la)[1]:.1f}"
                          for la, lo in pts)


FRAME = box(W, S, E, N)
land = pickle.load(open(LAND, "rb"))
mx = pickle.load(open(MX, "rb"))
us = pickle.load(open(US, "rb"))
print(f"tierra: {len(land.geoms)} piezas; {len(mx)} estados de México y "
      f"{len(us)} de Estados Unidos")

# ---- las entidades de 1824, armadas con los moldes de hoy
ent = []
for nombre, clase, kmx, kus in D.ENTIDADES_1824:
    piezas = [mx[k] for k in kmx if k in mx] + [us[k] for k in kus if k in us]
    g = unary_union([p.buffer(0) for p in piezas]).intersection(FRAME)
    if g.is_empty:
        raise SystemExit(f"{nombre} quedó vacía")
    c = g.representative_point()
    ent.append(dict(n=nombre, k=clase, d=path_of(g, 0.03),
                    x=round(T(c.x, c.y)[0], 1), y=round(T(c.x, c.y)[1], 1),
                    km2=round(sum(1 for _ in [0]) * 0, 1)))
mexico_1821 = unary_union([mx[k].buffer(0) for k in mx]
                          + [us[k].buffer(0) for k in ["TX", "CA", "NV", "UT",
                                                       "AZ", "NM", "CO"]]).intersection(FRAME)

# ---- lo que se perdió
perd = []
for año, nombre, kmx, kus, nota in D.PERDIDO:
    piezas = [mx[k] for k in kmx if k in mx] + [us[k] for k in kus if k in us]
    g = unary_union([p.buffer(0) for p in piezas]).intersection(FRAME)
    c = g.representative_point()
    perd.append(dict(a=año, n=nombre, nota=nota, d=path_of(g, 0.03),
                     x=round(T(c.x, c.y)[0], 1), y=round(T(c.x, c.y)[1], 1)))
# la Mesilla: lo que queda entre la línea de 1848 y la de 1853
mesilla = Polygon([(lo, la) for la, lo in D.LINEA_1848[5:]]
                  + [(lo, la) for la, lo in reversed(D.LINEA_1853[5:])]).buffer(0)
perd.append(dict(a=1853, n="La Mesilla", nota="Setenta y seis mil ochocientos "
                 "kilómetros cuadrados, vendidos para el paso del ferrocarril",
                 d=path_of(mesilla, 0.02),
                 x=round(T(-110.0, 31.6)[0], 1), y=round(T(-110.0, 31.6)[1], 1)))

# ---- centroamérica, como bloque: la tierra al sur de México
cen = land.intersection(box(-93.5, 6.0, -77.1, 18.7)).difference(
    unary_union([mx[k].buffer(0.01) for k in mx]))
cen = unary_union([p for p in (cen.geoms if hasattr(cen, "geoms") else [cen])
                   if p.area > 0.02 and not (p.bounds[0] > -78.6 and p.bounds[1] > 17.2)])
print(f"centroamérica: {cen.area:.1f} grados cuadrados")

# ---- los caminos
def camino(nombres):
    return [[round(v, 1) for v in T(D.LUGARES[n][1], D.LUGARES[n][0])]
            for n in nombres]


entradas = [dict(n=n, q=quien, a=a0, b=a1, p=camino(ruta), nota=nota,
                 sitios=[dict(n=x, e=D.LUGARES[x][2]) for x in ruta])
            for n, quien, a0, a1, ruta, nota in D.ENTRADAS]
llegada = dict(p=camino([n for n, _ in D.LLEGADA]),
               sitios=[dict(n=n, a=a, e=D.LUGARES[n][2]) for n, a in D.LLEGADA])
villas = [dict(n=n, a=a, nota=nota,
               x=round(T(D.LUGARES[n][1], D.LUGARES[n][0])[0], 1),
               y=round(T(D.LUGARES[n][1], D.LUGARES[n][0])[1], 1),
               e=D.LUGARES[n][2])
          for n, a, nota in D.VILLAS]

imperio = unary_union([mexico_1821, cen])
js = dict(
    land=path_of(land, 0.02),
    imperio=path_of(imperio, 0.03),
    cen=path_of(cen, 0.02),
    ent=ent, perd=perd,
    l1819=line_of(D.LINEA_1819), l1848=line_of(D.LINEA_1848),
    l1853=line_of(D.LINEA_1853),
    nota1819=D.LINEA_1819_NOTA,
    llegada=llegada, entradas=entradas, villas=villas, corto=D.CORTO,
    tenoch=[round(T(D.LUGARES["México-Tenochtitlan"][1],
                    D.LUGARES["México-Tenochtitlan"][0])[0], 1),
            round(T(D.LUGARES["México-Tenochtitlan"][1],
                    D.LUGARES["México-Tenochtitlan"][0])[1], 1)],
    sucesos=[dict(a=a, t=t, d=d) for a, t, d in D.SUCESOS],
    vw=VW, vh=round(VH, 1), a0=D.AÑO_INICIO, a1=D.AÑO_FIN,
)
blob = json.dumps(js, separators=(",", ":"), ensure_ascii=False)
print(f"traza: {len(entradas)} entradas, {len(villas)} villas, "
      f"{len(ent)} entidades, {len(js['land']):,} caracteres de costa")

refs = "\n".join(f'<p>{t}. <a href="{u}">{u}</a></p>' for t, u in D.FUENTES)

DOC = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>La Nueva España · Altazor</title>
<style>
:root{{color-scheme:dark;
--ink:#e6e6e6; --ink2:#9a9a9a; --ink3:#7d7d7d;
--bg:#121212; --panel:#171a1d; --line:#2b2f34; --accent:#58a6ff;
--mar:{C_MAR}; --tierra:{C_TIERRA}; --fuera:{C_FUERA}; --estado:{C_ESTADO};
--terr:{C_TERR}; --perdido:{C_PERDIDO}; --ruta:{C_RUTA}; --llegada:{C_LLEGADA};
--villa:{C_VILLA}; --linea:{C_LINEA};}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);
font:400 16px/1.65 "Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;}}
main{{max-width:1180px;margin:0 auto;padding:2rem 1.25rem 4rem}}
header.site{{border-top:4px solid var(--accent);padding-top:22px;margin-bottom:26px;
display:flex;align-items:baseline;gap:18px;flex-wrap:wrap;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;}}
.brand{{font-weight:700;font-size:20px;letter-spacing:.1em;text-decoration:none;color:var(--ink);}}
.brand:hover{{color:var(--accent);}}
nav.site a{{color:var(--ink2);text-decoration:none;font-size:14px;}}
nav.site a:hover{{color:var(--accent);}}
h1{{font-size:1.6rem;font-weight:400;margin:1.6rem 0 .9rem}}
h2{{font-size:1.05rem;font-weight:400;color:var(--ink);margin:2rem 0 .6rem}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
gap:10px;margin:0 0 1.1rem;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
.tile{{background:var(--panel);border:1px solid var(--line);border-radius:12px;
padding:10px 16px}}
.tile .k{{font-size:11.5px;color:var(--ink2);text-transform:uppercase;letter-spacing:.07em}}
.tile .v{{font-size:21px;font-weight:650;margin-top:3px;font-variant-numeric:tabular-nums}}
.tile .g{{font-size:12.5px;color:var(--ink3);margin-top:3px;line-height:1.45}}
figure{{margin:0}}
svg#mapa{{width:100%;height:auto;display:block;background:var(--mar);
border-radius:10px;border:1px solid var(--line)}}
.controls{{display:flex;align-items:center;gap:.7rem;margin:1rem 0 0;flex-wrap:wrap;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;font-size:.9rem}}
button{{font:inherit;font-size:.85rem;background:none;color:var(--ink);
border:1px solid var(--line);border-radius:999px;padding:5px 13px;cursor:pointer}}
button:hover{{background:#20242a}}
button[aria-pressed="true"]{{border-color:var(--accent);color:var(--accent)}}
input[type=range]{{flex:1;min-width:240px;accent-color:var(--ruta);height:22px}}
#anoOut{{font-variant-numeric:tabular-nums;color:var(--ink2);min-width:4.5em}}
.notes{{margin-top:2.5rem;border-top:1px solid var(--line);padding-top:1.5rem;
color:var(--ink2);font-size:.95rem}}
.notes p{{margin:0 0 1rem;max-width:74ch}}
.method{{margin-top:1.5rem;color:var(--ink3);font-size:.88rem}}
.method p{{margin:0 0 .9rem;max-width:74ch}}
.refs{{font-size:.82rem;color:var(--ink3);max-width:74ch}}
.refs p{{padding-left:2.2em;text-indent:-2.2em;margin:0 0 .8em}}
.refs a{{color:var(--accent);word-break:break-word}}
path.tierra{{fill:var(--tierra)}}
path.fuera{{fill:var(--fuera)}}
#imperio{{fill:var(--estado);fill-opacity:.55;stroke:#0f1216;stroke-width:.8}}
#entidades path{{stroke:#0f1216;stroke-width:.7;cursor:pointer}}
#entidades path.estado{{fill:var(--estado);fill-opacity:.62}}
#entidades path.territorio{{fill:var(--terr);fill-opacity:.55}}
#entidades path.distrito{{fill:#b0894a;fill-opacity:.7}}
#entidades path.on{{fill-opacity:.92}}
#perdido path{{fill:var(--perdido);fill-opacity:.75;stroke:#0f1216;stroke-width:.7}}
#rutas path{{fill:none;stroke:var(--ruta);vector-effect:non-scaling-stroke;stroke-width:1.8;stroke-linejoin:round;
stroke-linecap:round}}
#rutas path.llegada{{stroke:var(--llegada);stroke-width:2.6}}
#entidades path,#perdido path,#imperio,path.tierra{{vector-effect:non-scaling-stroke}}
#lineas path{{fill:none;stroke:var(--linea);stroke-width:1.8;
vector-effect:non-scaling-stroke;stroke-dasharray:7 5}}
circle.villa{{fill:var(--villa);stroke:#0f1216;stroke-width:1.1}}
circle.punta{{fill:#fff3d6;stroke:#7a4d0d;stroke-width:1.4}}
.lbl{{font:400 11.5px/1 system-ui,sans-serif;fill:#e4e9ee;pointer-events:none;
paint-order:stroke;stroke:#0d1a26;stroke-width:2.6}}
.lbl.ent{{font-size:11px;fill:#dcd3e6;letter-spacing:.04em}}
.lbl.villa{{font-size:10.5px;fill:#cfeee5}}
.leg{{font:400 12px/1 system-ui,sans-serif;fill:#c3ccd6}}
</style>
</head>
<body>
<main>
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library</a></nav>
</header>

<h1>La Nueva España</h1>

<div class="tiles">
  <div class="tile"><div class="k">año</div>
    <div class="v" id="tAno">1519</div><div class="g" id="tAnoSub"></div></div>
  <div class="tile"><div class="k">lo que pasa</div>
    <div class="v" id="tSuceso" style="font-size:15px"></div>
    <div class="g" id="tSucesoSub"></div></div>
  <div class="tile"><div class="k">en camino</div>
    <div class="v" id="tEntradas"></div><div class="g" id="tEntradasSub"></div></div>
  <div class="tile"><div class="k">villas fundadas</div>
    <div class="v" id="tVillas"></div><div class="g" id="tVillasSub"></div></div>
</div>

<figure>
<svg id="mapa" viewBox="0 0 {VW:.0f} {VH:.0f}" role="img"
  aria-label="Mapa de la Nueva España, de Panamá a Oregón, con las entradas, las villas y las fronteras.">
<title>La Nueva España de 1519 a 1853</title>
<path class="tierra" d="{js['land']}"/>
<path id="imperio" d="{js['imperio']}" style="display:none"/>
<g id="entidades"></g>
<g id="perdido"></g>
<path id="centro" class="tierra" d="{js['cen']}"/>
<g id="centroLbl"></g>
<g id="lineas"></g>
<g id="rutas"></g>
<g id="villas"></g>
<g id="etiquetas"></g>
<g id="leyenda"></g>
</svg>
</figure>

<div class="controls">
  <button id="bPlay">Correr los años</button>
  <input type="range" id="ano" min="{D.AÑO_INICIO}" max="{D.AÑO_FIN}" step="1"
    value="{D.AÑO_INICIO}" aria-label="Año">
  <output id="anoOut"></output>
  <button id="bRutas" aria-pressed="true">Entradas</button>
  <button id="bVillas" aria-pressed="true">Villas</button>
  <button id="bEnt" aria-pressed="true">Entidades</button>
</div>

<div class="notes">
<p>El mapa empieza en 1519 con la armada de Cortés frente a Chalchihuecan y
termina en 1853 con la venta de La Mesilla. En medio suben las entradas al
norte, se van fundando las villas por donde pasan, y al final se reparte todo
en estados y se dibujan las rayas que quedaron.</p>
<p>Las entidades de 1824 están armadas con los estados de hoy, así que sus
orillas son aproximadas: sirven para ver el reparto, no para medir. Un nombre
bajo el cursor dice qué era y de qué estados de hoy se compone.</p>
</div>

<div class="method">
<p>Las fechas y los caminos vienen de las fuentes que van abajo. Donde las
fuentes no coinciden, la nota lo dice: la fundación de la Villa Rica, el día de
Laredo, el año de Santa Fe, el sitio de Chichilticalli. El camino de Cabeza de
Vaca se discute hasta hoy y aquí va como corredor, no como ruta levantada. Los
lugares que todavía existen llevan la coordenada de GeoNames; los sitios sin
pueblo encima van puestos a mano y la página los marca como aproximados. La
línea de Adams y Onís es el artículo tercero del tratado de 1819, tramo por
tramo; las de 1848 y 1853 van simplificadas, siguiendo el Bravo y el Gila. La
costa es la de la base GSHHG, a resolución completa.</p>
</div>

<h2>Referencias</h2>
<div class="refs">
{refs}
<p>Wessel, P., &amp; Smith, W. H. F. (1996). A global, self-consistent,
hierarchical, high-resolution shoreline database. <em>Journal of Geophysical
Research: Solid Earth, 101</em>(B4), 8741-8743.
<a href="https://doi.org/10.1029/96JB00104">https://doi.org/10.1029/96JB00104</a></p>
</div>
</main>
<script>
const D={blob};
const el=id=>document.getElementById(id);
const NS='http://www.w3.org/2000/svg';
function make(t,a,p){{const e=document.createElementNS(NS,t);
  for(const k in a) e.setAttribute(k,a[k]); if(p) p.appendChild(e); return e;}}
function clear(g){{while(g.firstChild) g.removeChild(g.firstChild);}}

let ano=D.a0, corriendo=null, verRutas=true, verVillas=true, verEnt=true;
let sobre=null;

// El cuadro sigue a la historia: en 1519 cabe el camino de Veracruz a
// Tenochtitlan y nada más, y se va abriendo conforme las entradas suben al
// norte, hasta que en el siglo XIX cabe todo. Lo que se ve manda el encuadre.
const MIN_ANCHO = D.vw * 0.20;
let caja = null;
function encuadre(){{
  const pts=[D.tenoch.slice()];
  const f0 = ano>=1521 ? 1 : (ano-1519+1)/3;
  if(ano>=1519) D.llegada.p.forEach(p=>pts.push(p));
  D.entradas.forEach(e=>{{
    if(ano<e.a) return;
    const f = e.b>e.a ? Math.min(1,(ano-e.a+1)/(e.b-e.a+1)) : 1;
    const hasta = Math.floor(f*(e.p.length-1));
    for(let i=0;i<=hasta;i++) pts.push(e.p[i]);
  }});
  D.villas.forEach(v=>{{ if(ano>=v.a) pts.push([v.x,v.y]); }});
  if(ano>=1821) return {{x:0,y:0,w:D.vw,h:D.vh}};
  let x0=Math.min(...pts.map(p=>p[0])), x1=Math.max(...pts.map(p=>p[0]));
  let y0=Math.min(...pts.map(p=>p[1])), y1=Math.max(...pts.map(p=>p[1]));
  const pad=Math.max(40,(x1-x0)*0.14);
  x0-=pad; x1+=pad; y0-=pad; y1+=pad;
  let w=Math.max(MIN_ANCHO, x1-x0, (y1-y0)*D.vw/D.vh);
  let h=w*D.vh/D.vw;
  let cx=(x0+x1)/2, cy=(y0+y1)/2;
  w=Math.min(w,D.vw); h=Math.min(h,D.vh);
  cx=Math.max(w/2,Math.min(D.vw-w/2,cx));
  cy=Math.max(h/2,Math.min(D.vh-h/2,cy));
  return {{x:cx-w/2, y:cy-h/2, w, h}};
}}
function acercar(){{
  const t=encuadre();
  if(!caja) caja=t;
  else{{  // se mueve poco a poco, para que al correr los años no dé brincos
    const m=corriendo?0.14:1;
    caja={{x:caja.x+(t.x-caja.x)*m, y:caja.y+(t.y-caja.y)*m,
          w:caja.w+(t.w-caja.w)*m, h:caja.h+(t.h-caja.h)*m}};
  }}
  el('mapa').setAttribute('viewBox',
    `${{caja.x.toFixed(1)}} ${{caja.y.toFixed(1)}} ${{caja.w.toFixed(1)}} ${{caja.h.toFixed(1)}}`);
  return caja.w/D.vw;   // cuánto se agrandó todo
}}

function sucesoDe(a){{
  let s=null; for(const x of D.sucesos) if(x.a<=a) s=x; return s;
}}
function tramo(p, f){{
  // el camino, dibujado hasta la fracción f
  if(f<=0) return '';
  const total=p.length-1, hasta=Math.min(total, f*total);
  let d='M'+p[0][0]+','+p[0][1];
  for(let i=1;i<=Math.floor(hasta);i++) d+='L'+p[i][0]+','+p[i][1];
  const r=hasta-Math.floor(hasta), i=Math.floor(hasta);
  if(r>0 && i+1<p.length)
    d+='L'+(p[i][0]+(p[i+1][0]-p[i][0])*r).toFixed(1)+','
       +(p[i][1]+(p[i+1][1]-p[i][1])*r).toFixed(1);
  return d;
}}

// Los letreros se estorban unos a otros según el año, así que se colocan
// cada vez: primero las villas, que son lo que se mueve, y luego las
// entidades, que se saltan si ya no cabe el nombre.
let cajas=[];
let K=1;                       // escala del encuadre
function pon(g, texto, x, y, clase, r){{
  const ancho=texto.length*(clase.includes('ent')?5.6:5.4)*K, alto=13*K;
  const ops=[[x+r+5*K,y+4*K,'start'],[x-r-5*K,y+4*K,'end'],
             [x,y-r-6*K,'middle'],[x,y+r+alto,'middle']];
  for(const [tx,ty,anc] of ops){{
    const x0 = anc==='start'? tx : anc==='end'? tx-ancho : tx-ancho/2;
    const c=[x0-2*K,ty-alto,x0+ancho+2*K,ty+3*K];
    if(c[0]<caja.x+4||c[2]>caja.x+caja.w-4||c[1]<caja.y+4||c[3]>caja.y+caja.h-4) continue;
    if(cajas.some(o=>!(c[2]<o[0]||c[0]>o[2]||c[3]<o[1]||c[1]>o[3]))) continue;
    const t=make('text',{{class:clase,x:tx,y:ty,'text-anchor':anc,
      style:`font-size:${{(clase.includes('ent')?11:11.5)*K}}px;stroke-width:${{2.6*K}}px`}},g);
    t.textContent=texto; cajas.push(c); return true;
  }}
  return false;
}}
function nombre(n){{ return D.corto[n]||n; }}

function pinta(){{
  K=acercar();
  const gEnt=el('entidades'), gPer=el('perdido'), gLin=el('lineas'),
        gRut=el('rutas'), gVil=el('villas'), gEti=el('etiquetas'),
        gCen=el('centroLbl');
  [gEnt,gPer,gLin,gRut,gVil,gEti,gCen].forEach(clear);
  cajas=[];
  leyenda();

  // de 1821 a 1823 el imperio va de una pieza, con Centroamérica adentro,
  // así que el gris de Centroamérica se quita mientras tanto
  const enImperio = (ano>=1821 && ano<1824 && verEnt);
  el('imperio').style.display = enImperio ? '' : 'none';
  el('centro').style.display = enImperio ? 'none' : '';
  // las entidades, desde 1824, menos lo que ya se había ido
  if(ano>=1824 && verEnt){{
    D.ent.forEach((e,i)=>{{
      const p=make('path',{{d:e.d,class:e.k+(sobre===i?' on':'')}},gEnt);
      p.addEventListener('mouseenter',()=>{{sobre=i;pinta();tablero();}});
      p.addEventListener('mouseleave',()=>{{sobre=null;pinta();tablero();}});
    }});
  }}
  D.perd.forEach(p=>{{ if(ano>=p.a) make('path',{{d:p.d}},gPer); }});

  // las rayas
  if(ano>=1819 && ano<1848) make('path',{{d:D.l1819}},gLin);
  if(ano>=1848 && ano<1853) make('path',{{d:D.l1848}},gLin);
  if(ano>=1853) make('path',{{d:D.l1853}},gLin);

  if(verRutas){{
    // la llegada, en su propio color
    const f0=(ano-1519+1)/1;
    if(ano>=1519) make('path',{{d:tramo(D.llegada.p, ano>=1519?1:0),class:'llegada'}},gRut);
    D.entradas.forEach(e=>{{
      if(ano<e.a) return;
      const f=e.b>e.a ? Math.min(1,(ano-e.a+1)/(e.b-e.a+1)) : 1;
      make('path',{{d:tramo(e.p,f)}},gRut);
      const i=Math.min(e.p.length-1, Math.floor(f*(e.p.length-1)));
      if(f<1) make('circle',{{class:'punta',cx:e.p[i][0],cy:e.p[i][1],r:3.4*K,
        style:`stroke-width:${{1.4*K}}px`}},gRut);
    }});
  }}

  {{
    const c=D.tenoch;
    make('rect',{{x:c[0]-4*K,y:c[1]-4*K,width:8*K,height:8*K,rx:1.5*K,
      fill:'#fff3d6',stroke:'#0d1a26','stroke-width':1.2*K}},gVil);
    cajas.push([c[0]-6*K,c[1]-6*K,c[0]+6*K,c[1]+6*K]);
    pon(gEti, ano<1521?'México-Tenochtitlan':'México', c[0], c[1], 'lbl', 5*K);
  }}
  if(verVillas){{
    const vistas=D.villas.filter(v=>ano>=v.a);
    vistas.forEach(v=>{{
      const nueva=ano-v.a<6;
      make('circle',{{class:'villa',cx:v.x,cy:v.y,r:(nueva?4.8:3.4)*K,
        style:`stroke-width:${{1.1*K}}px`}},gVil);
      cajas.push([v.x-5*K,v.y-5*K,v.x+5*K,v.y+5*K]);
    }});
    // las recién fundadas se rotulan primero: son las que cuentan el año
    vistas.slice().sort((a,b)=>b.a-a.a).forEach(v=>
      pon(gEti, nombre(v.n), v.x, v.y, 'lbl villa', 4));
  }}
  D.perd.forEach(p=>{{
    if(ano<p.a) return;
    pon(gEti, p.n, p.x, p.y, 'lbl', 2);
  }});
  if(ano>=1824 && verEnt){{
    D.ent.forEach(e=>pon(gEti, nombre(e.n), e.x, e.y, 'lbl ent', 2));
  }}
  if(ano>=1823){{
    pon(gCen, 'Provincias Unidas del Centro de América',
        {(lambda t: t)(0) or 0} + {round(T(-86.5, 13.0)[0], 1)},
        {round(T(-86.5, 13.0)[1], 1)}, 'lbl', 2);
  }}
}}

function tablero(){{
  el('tAno').textContent=ano;
  el('anoOut').textContent=ano;
  el('ano').value=ano;
  const s=sucesoDe(ano);
  el('tAnoSub').textContent = ano<1821 ? 'virreinato de la Nueva España'
    : ano<1824 ? 'México independiente' : 'la primera federación';
  el('tSuceso').textContent = s? s.t : '';
  el('tSucesoSub').textContent = s? s.d : '';
  const enCamino=D.entradas.filter(e=>ano>=e.a&&ano<=e.b);
  el('tEntradas').textContent=enCamino.length;
  el('tEntradasSub').textContent = enCamino.length
    ? enCamino.map(e=>e.n).join(', ') : 'ninguna entrada en marcha';
  const v=D.villas.filter(x=>x.a<=ano);
  el('tVillas').textContent=v.length;
  el('tVillasSub').textContent = v.length
    ? 'la última, '+v[v.length-1].n+' en '+v[v.length-1].a
    : 'todavía ninguna';
  if(sobre!==null){{
    const e=D.ent[sobre];
    el('tSuceso').textContent=e.n;
    el('tSucesoSub').textContent=e.k==='estado' ? 'estado de la federación de 1824'
      : e.k==='territorio' ? 'territorio de la federación de 1824'
      : 'el distrito federal, creado en noviembre de 1824';
  }}
}}

el('ano').addEventListener('input',e=>{{parar();ano=+e.target.value;pinta();tablero();}});
function parar(){{if(corriendo){{clearInterval(corriendo);corriendo=null;
  el('bPlay').setAttribute('aria-pressed','false');
  el('bPlay').textContent='Correr los años';}}}}
el('bPlay').addEventListener('click',()=>{{
  if(corriendo){{parar();return;}}
  el('bPlay').setAttribute('aria-pressed','true');
  el('bPlay').textContent='Alto';
  if(ano>=D.a1) ano=D.a0;
  corriendo=setInterval(()=>{{
    ano+=1; if(ano>=D.a1){{ano=D.a1;pinta();tablero();parar();return;}}
    pinta(); tablero();
  }}, 55);
}});
function bota(id,f){{
  el(id).addEventListener('click',()=>{{
    const v=el(id).getAttribute('aria-pressed')!=='true';
    el(id).setAttribute('aria-pressed',v); f(v); pinta();
  }});
}}
bota('bRutas',v=>verRutas=v); bota('bVillas',v=>verVillas=v);
bota('bEnt',v=>verEnt=v);

const FILAS=[['{C_LLEGADA}','la llegada de 1519'],['{C_RUTA}','las entradas al norte'],
  ['{C_VILLA}','villa fundada'],['{C_ESTADO}','el imperio, luego los estados'],
  ['{C_TERR}','territorio de 1824'],['{C_PERDIDO}','lo que se perdió']];
function leyenda(){{
  const g=el('leyenda');
  clear(g);
  const w=238, h=132;
  const x0=caja.x+8*K, y0=caja.y+caja.h-(h+8)*K;
  g.setAttribute('transform', `translate(${{x0}},${{y0}}) scale(${{K}})`);
  make('rect',{{x:0,y:0,width:w,height:h,rx:8,fill:'#0f1216','fill-opacity':.78}},g);
  FILAS.forEach((f,i)=>{{
    make('rect',{{x:10,y:14+i*21,width:16,height:8,rx:2,fill:f[0]}},g);
    const t=make('text',{{class:'leg',x:34,y:22+i*21}},g);
    t.textContent=f[1];
  }});
  cajas.push([x0, y0, x0+w*K, y0+h*K]);
}}

pinta(); tablero();
window.__ne=()=>({{ano, entradas:D.entradas.length, villas:D.villas.length,
  entidades:D.ent.length, dibujadas:{{
    rutas:document.querySelectorAll('#rutas path').length,
    villas:document.querySelectorAll('#villas circle').length,
    entidades:document.querySelectorAll('#entidades path').length,
    perdido:document.querySelectorAll('#perdido path').length,
    lineas:document.querySelectorAll('#lineas path').length}},
  suceso:el('tSuceso').textContent}});
</script>
</body>
</html>
"""

OUT.write_text(DOC, encoding="utf-8")
print(f"escrito {OUT} ({len(DOC):,} bytes), cuadro {VW:.0f} por {VH:.0f}")
