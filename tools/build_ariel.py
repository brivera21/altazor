#!/usr/bin/env python3
"""Generate premios-ariel.html, the Ariel Best Film winners timeline (Spanish)
for the Film section.

Winners cross-checked against the AMACC official historical list
(amacc.org.mx/mejor-pelicula-historico), the es.wikipedia Anexo and the
en.wikipedia per-edition pages, August 2026. Years are ceremony years; the
first two editions were both presented in 1947. The award was suspended from
1959 to 1971, was declared void in 1953 and 1983, and tied in 1972, 1975 and
1978, with a triple tie in 1973. Posters are fetched by the page at view time
from Wikipedia's public REST API (Spanish first, then English); none are
stored in the repo.

Usage: python3 build_ariel.py
"""

import json
from pathlib import Path

OUT = Path(__file__).parent.parent / "premios-ariel.html"

# (ceremony year, edition, title, directors)
FILMS = [
    (1947, "I", "La barraca", "Roberto Gavaldón"),
    (1947, "II", "Enamorada", "Emilio Fernández"),
    (1948, "III", "La perla", "Emilio Fernández"),
    (1949, "IV", "Río Escondido", "Emilio Fernández"),
    (1950, "V", "Una familia de tantas", "Alejandro Galindo"),
    (1951, "VI", "Los olvidados", "Luis Buñuel"),
    (1952, "VII", "En la palma de tu mano", "Roberto Gavaldón"),
    (1954, "IX", "El niño y la niebla", "Roberto Gavaldón"),
    (1955, "X", "Los Fernández de Peralvillo", "Alejandro Galindo"),
    (1956, "XI", "Las aventuras de Robinson Crusoe", "Luis Buñuel"),
    (1957, "XII", "El camino de la vida", "Alfonso Corona Blake"),
    (1958, "XIII", "Tizoc", "Ismael Rodríguez"),
    (1972, "XIV", "El águila descalza", "Alfonso Arau"),
    (1972, "XIV", "Las puertas del paraíso", "Salomón Laiter"),
    (1973, "XV", "El castillo de la pureza", "Arturo Ripstein"),
    (1973, "XV", "Mecánica nacional", "Luis Alcoriza"),
    (1973, "XV", "Reed, México insurgente", "Paul Leduc"),
    (1974, "XVI", "El principio", "Gonzalo Martínez Ortega"),
    (1975, "XVII", "La otra virginidad", "Juan Manuel Torres"),
    (1975, "XVII", "La choca", "Emilio Fernández"),
    (1976, "XVIII", "Actas de Marusia", "Miguel Littín"),
    (1977, "XIX", "La pasión según Berenice", "Jaime Humberto Hermosillo"),
    (1978, "XX", "Naufragio", "Jaime Humberto Hermosillo"),
    (1978, "XX", "El lugar sin límites", "Arturo Ripstein"),
    (1979, "XXI", "Cadena perpetua", "Arturo Ripstein"),
    (1980, "XXII", "El año de la peste", "Felipe Cazals"),
    (1981, "XXIII", "Las grandes aguas", "Servando González"),
    (1982, "XXIV", "¡Ora sí tenemos que ganar!", "Raúl Kamffer"),
    (1984, "XXVI", "Bajo la metralla", "Felipe Cazals"),
    (1985, "XXVII", "Frida, naturaleza viva", "Paul Leduc"),
    (1986, "XXVIII", "Veneno para las hadas", "Carlos Enrique Taboada"),
    (1987, "XXIX", "El imperio de la fortuna", "Arturo Ripstein"),
    (1988, "XXX", "Mariana, Mariana", "Alberto Isaac"),
    (1989, "XXXI", "Esperanza", "Sergio Olhovich"),
    (1990, "XXXII", "Goitia, un dios para sí mismo", "Diego López Rivera"),
    (1991, "XXXIII", "Rojo amanecer", "Jorge Fons"),
    (1992, "XXXIV", "Como agua para chocolate", "Alfonso Arau"),
    (1993, "XXXV", "Cronos", "Guillermo del Toro"),
    (1994, "XXXVI", "Principio y fin", "Arturo Ripstein"),
    (1995, "XXXVII", "El callejón de los milagros", "Jorge Fons"),
    (1996, "XXXVIII", "Sin remitente", "Carlos Carrera"),
    (1997, "XXXIX", "Cilantro y perejil", "Rafael Montero"),
    (1998, "XL", "Por si no te vuelvo a ver", "Juan Pablo Villaseñor"),
    (1999, "XLI", "Bajo California: el límite del tiempo", "Carlos Bolado"),
    (2000, "XLII", "La ley de Herodes", "Luis Estrada"),
    (2001, "XLIII", "Amores perros", "Alejandro González Iñárritu"),
    (2002, "XLIV", "Cuento de hadas para dormir cocodrilos", "Ignacio Ortiz"),
    (2003, "XLV", "El crimen del padre Amaro", "Carlos Carrera"),
    (2004, "XLVI", "El misterio del Trinidad", "José Luis García Agraz"),
    (2005, "XLVII", "Temporada de patos", "Fernando Eimbcke"),
    (2006, "XLVIII", "Mezcal", "Ignacio Ortiz"),
    (2007, "XLIX", "El laberinto del fauno", "Guillermo del Toro"),
    (2008, "L", "Luz silenciosa", "Carlos Reygadas"),
    (2009, "LI", "Lake Tahoe", "Fernando Eimbcke"),
    (2010, "LII", "Cinco días sin Nora", "Mariana Chenillo"),
    (2011, "LIII", "El infierno", "Luis Estrada"),
    (2012, "LIV", "Pastorela", "Emilio Portes"),
    (2013, "LV", "El premio", "Paula Markovitch"),
    (2014, "LVI", "La jaula de oro", "Diego Quemada-Díez"),
    (2015, "LVII", "Güeros", "Alonso Ruizpalacios"),
    (2016, "LVIII", "Las elegidas", "David Pablos"),
    (2017, "LIX", "La 4ª compañía", "Amir Galván Cervera y Mitzi Vanessa Arreola"),
    (2018, "LX", "Sueño en otro idioma", "Ernesto Contreras"),
    (2019, "LXI", "Roma", "Alfonso Cuarón"),
    (2020, "LXII", "Ya no estoy aquí", "Fernando Frías de la Parra"),
    (2021, "LXIII", "Sin señas particulares", "Fernanda Valadez"),
    (2022, "LXIV", "Noche de fuego", "Tatiana Huezo"),
    (2023, "LXV", "El norte sobre el vacío", "Alejandra Márquez Abella"),
    (2024, "LXVI", "Tótem", "Lila Avilés"),
    (2025, "LXVII", "Sujo", "Astrid Rondero y Fernanda Valadez"),
]

# Eras follow the boundaries of cine-mexicano.html, cut to the years the
# award has run. The suspension is its own band and holds no films.
ERAS = [
    (1946, 1958, "Época de Oro", "#ffb02e", False),
    (1959, 1971, "Suspensión del premio", "#6b7280", True),
    (1972, 1980, "Nuevo Cine / años de Echeverría", "#31d67a", False),
    (1981, 1991, "Crisis y video", "#d1548e", False),
    (1992, 2000, "Nuevo Cine Mexicano", "#2fc6a6", False),
    (2001, 2013, "Proyección internacional", "#58a6ff", False),
    (2014, 2026, "Era global y de streaming", "#e6c86e", False),
]


def era_index(year):
    for i, (a, b, _n, _c, _h) in enumerate(ERAS):
        if year <= b:
            return i
    return len(ERAS) - 1


for y, *_ in FILMS:
    assert not ERAS[era_index(y)][4], f"film in the hiatus band: {y}"

films_js = json.dumps(
    [{"y": y, "n": n, "d": d, "ed": ed, "e": era_index(y)}
     for y, ed, n, d in FILMS],
    separators=(",", ":"), ensure_ascii=False)
eras_js = json.dumps(
    [{"a": a, "b": b, "n": n, "c": c, "h": h}
     for a, b, n, c, h in ERAS],
    separators=(",", ":"), ensure_ascii=False)

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>El Ariel a Mejor Película · Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
.wrap { max-width:1320px; margin:0 auto; padding:32px 20px 60px; }
header.site { border-top:4px solid var(--accent); padding-top:22px; margin-bottom:26px;
  display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }
.brand { font-weight:700; font-size:20px; letter-spacing:.1em; text-decoration:none; color:var(--text); }
.brand:hover { color:var(--accent); }
nav.site a { color:var(--muted); text-decoration:none; font-size:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 6px; font-size:26px; }
.lede { color:var(--muted); font-size:14.5px; margin:0 0 14px; max-width:760px; }
.controls { display:flex; gap:8px; flex-wrap:wrap; align-items:center; margin-bottom:10px; }
.controls button { background:var(--panel); border:1px solid var(--line); color:var(--text);
  padding:7px 13px; border-radius:8px; cursor:pointer; font-size:13.5px; }
.controls button:hover { border-color:var(--accent); }
.controls .info { color:var(--muted); font-size:13px; margin-left:6px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#tl { flex:1 1 640px; min-width:0; }
#tl svg { width:100%; height:auto; display:block; cursor:grab; user-select:none; }
#tl.panning, #tl.panning * { cursor:grabbing !important; }
.side { flex:0 0 260px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:14px; }
#poster { width:100%; aspect-ratio:2/3; object-fit:contain; background:#101010;
  border-radius:6px; display:block; }
#filmTxt { font-weight:700; margin:10px 0 2px; font-size:15px; }
#dirTxt { color:var(--muted); font-size:13px; }
#eraTxt { font-size:13px; min-height:1.2em; margin-top:2px; }
#yearTxt { color:var(--muted); font-size:13px; margin-top:4px; }
.legend { display:flex; gap:14px; flex-wrap:wrap; margin-top:10px; font-size:12.5px; color:var(--muted); }
.legend span.sw { width:11px; height:11px; border-radius:3px; display:inline-block; margin-right:5px; }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.note a { color:var(--accent); }
@media (max-width:900px){ .stage{flex-direction:column;} .side{position:static; width:100%;}
  #poster{max-width:220px; margin:0 auto;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="film.html">&larr; Film</a></nav>
</header>
<h1>El Ariel a Mejor Película</h1>
<div class="controls">
  <button id="reset">Vista completa</button>
  <span class="info" id="info"></span>
</div>
<div class="stage">
  <div id="tl"></div>
  <div class="side"><div class="card">
    <img id="poster" alt="Póster de la película">
    <div id="filmTxt">La película bajo el cursor aparece aquí</div>
    <div id="dirTxt"></div>
    <div id="eraTxt"></div>
    <div id="yearTxt"></div>
  </div></div>
</div>
<div class="legend" id="legend"></div>
<p class="note">Cada punto es una ganadora del Ariel a Mejor Película, de
La barraca en la primera entrega de 1947 a la más reciente. La rueda acerca,
arrastrar recorre, un clic en una época entra en ella y la película bajo el
cursor muestra su póster.</p>
<p class="note">Los años son los de cada ceremonia. Las dos primeras ediciones
se entregaron en 1947; el premio se declaró desierto en 1953 y en 1983, y la
Academia lo suspendió de 1959 a 1971. Hubo empates en 1972, 1975 y 1978, y un
triple empate en 1973. La edición LXVIII está anunciada para octubre de 2026.
Los ganadores se pueden cotejar con la
<a href="https://www.amacc.org.mx/mejor-pelicula-historico">lista histórica de
la AMACC</a>. Los pósters se cargan al momento desde la API pública de
Wikipedia solo para identificación y no se guardan en este sitio; alguno puede
no aparecer.</p>
</div>
<script>
const FILMS=__FILMS__, ERAS=__ERAS__;
const W=980,H=780,CY=385,MINY=1944,MAXY=2028;
let view={a:MINY,b:MAXY};

const el=document.getElementById('tl');
const X=y=>(y-view.a)/(view.b-view.a)*W;
const YR=x=>view.a+x/W*(view.b-view.a);
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');

function ticks(){
  const span=view.b-view.a;
  const step=span>60?10:span>25?5:span>12?2:1;
  const out=[];
  for(let y=Math.ceil(view.a/step)*step;y<=view.b;y+=step) out.push(y);
  return out;
}
function lanes(items,estw){
  const ends=[];
  for(const it of items){
    const w=estw(it), x0=it.cx-w/2;
    let l=0;
    while(l<ends.length && ends[l]>x0) l++;
    it.lane=l; ends[l]=it.cx+w/2+8;
  }
}
function render(){
  let s=`<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" id="tlsvg">`;
  s+=`<rect width="${W}" height="${H}" fill="#121212"/>`;
  for(const y of ticks()){
    const x=X(y);
    s+=`<line x1="${x}" y1="26" x2="${x}" y2="${H-26}" stroke="#242424"/>`;
    s+=`<text x="${x}" y="${CY+20}" text-anchor="middle" font-size="12.5" font-weight="700"
      fill="#9a9a9a">${y}</text>`;
  }
  s+=`<line x1="0" y1="${CY}" x2="${W}" y2="${CY}" stroke="#3a3a3a" stroke-width="2"/>`;
  for(let d=Math.floor(view.a/10)*10; d<view.b; d+=10){
    const x0=Math.max(0,X(d)), x1=Math.min(W,X(d+10));
    if(x1-x0<2) continue;
    s+=`<rect x="${x0}" y="26" width="${x1-x0}" height="${H-52}" fill="transparent"
      data-dec-band="${d}"/>`;
  }
  ERAS.forEach((p,i)=>{
    if(p.b<view.a||p.a>view.b) return;
    const x0=Math.max(0,X(p.a)), x1=Math.min(W,X(p.b));
    const dash=p.h?' stroke-dasharray="4 3"':'';
    s+=`<rect x="${x0}" y="${CY+30}" width="${Math.max(2,x1-x0)}" height="22" rx="6"
      fill="${p.c}${p.h?'11':'22'}" stroke="${p.c}" stroke-width="1"${dash}
      data-era="${i}" style="cursor:pointer"/>`;
    if(x1-x0>150) s+=`<text x="${(x0+x1)/2}" y="${CY+45}" text-anchor="middle" font-size="11.5"
      fill="${p.c}" pointer-events="none">${esc(p.n)} (${p.a}-${p.b})</text>`;
  });
  const fs=FILMS.filter(f=>f.y>=view.a-30&&f.y<=view.b+30)
                .map(f=>({...f,x:X(f.y),fi:FILMS.indexOf(f)}))
                .sort((a,b)=>a.x-b.x);
  fs.forEach((f,i)=>{const w=Math.min(215,(f.n.length+7)*6.2)+14;
    f.w=w; f.cx=Math.min(W-w/2-4,Math.max(w/2+4,f.x)); f.up=(i%2===0);});
  const ups=fs.filter(f=>f.up), dns=fs.filter(f=>!f.up);
  lanes(ups,f=>f.w-14); lanes(dns,f=>f.w-14);
  for(const f of fs){
    const c=ERAS[f.e].c;
    const ly=f.up ? CY-42-f.lane*26 : CY+108+f.lane*26;
    const dotY=f.up ? CY-6 : CY+6;
    const tipY=f.up ? ly+9 : ly-9;
    const label=`${f.n} (${f.y})`;
    s+=`<g data-f="${f.fi}" data-dec="${Math.floor(f.y/10)*10}" style="cursor:default">
      <line x1="${f.x}" y1="${dotY}" x2="${f.x}" y2="${tipY}" stroke="${c}" stroke-width="1.1" opacity="0.7"/>
      <circle cx="${f.x}" cy="${dotY}" r="3.2" fill="${c}"/>
      <rect x="${f.cx-f.w/2}" y="${ly-8}" width="${f.w}" height="20" rx="7"
        fill="#1a1a1a" stroke="${c}" stroke-width="1.1"/>
      <text x="${f.cx}" y="${ly+6}" text-anchor="middle" font-size="11.3" font-weight="600"
        fill="#e6e6e6" pointer-events="none">${esc(label).slice(0,40)}</text></g>`;
  }
  s+='</svg>';
  el.innerHTML=s;
  document.getElementById('info').textContent=
    `${Math.round(view.a)} a ${Math.round(view.b)}`;
}
function clampView(a,b){
  const span=Math.min(MAXY-MINY,Math.max(6,b-a));
  a=Math.max(MINY,Math.min(a,MAXY-span));
  return {a,b:a+span};
}
function hook(){
  const px=e=>{const r=el.getBoundingClientRect();return (e.clientX-r.left)/r.width*W;};
  el.addEventListener('wheel',e=>{
    e.preventDefault();
    const f=e.deltaY>0?1.18:1/1.18, yr=YR(px(e));
    view=clampView(yr-(yr-view.a)*f, yr+(view.b-yr)*f);
    render();
  },{passive:false});
  let drag=null, dragged=false;
  el.addEventListener('pointerdown',e=>{drag={x:px(e),a:view.a,b:view.b};dragged=false;el.classList.add('panning');el.setPointerCapture(e.pointerId);});
  el.addEventListener('pointermove',e=>{
    if(!drag) return;
    const dx=px(e)-drag.x;
    if(Math.abs(dx)>2) dragged=true;
    const dyr=dx/W*(drag.b-drag.a);
    view=clampView(drag.a-dyr, drag.b-dyr);
    render();
  });
  el.addEventListener('pointerup',()=>{drag=null;el.classList.remove('panning');});
  el.addEventListener('pointercancel',()=>{drag=null;el.classList.remove('panning');});
  el.addEventListener('click',e=>{
    if(dragged){dragged=false;return;}
    const g=e.target.closest('[data-era]');
    if(g){const p=ERAS[+g.getAttribute('data-era')];
      view=clampView(p.a-2,p.b+2);render();}
  });
  el.addEventListener('pointerover',e=>{
    const g=e.target.closest('[data-f]');
    if(g){ showFilm(+g.getAttribute('data-f')); setFocus(+g.getAttribute('data-dec')); return; }
    const b=e.target.closest('[data-era]');
    if(b){ const p=ERAS[+b.getAttribute('data-era')];
      document.getElementById('info').textContent=p.n+' ('+p.a+'-'+p.b+') · clic para acercar';
      setFocus(null); return; }
    const db=e.target.closest('[data-dec-band]');
    setFocus(db ? +db.getAttribute('data-dec-band') : null);
  });
  el.addEventListener('pointerleave',()=>setFocus(null));
}

function setFocus(d){
  document.querySelectorAll('#tlsvg g[data-dec]').forEach(g=>{
    g.setAttribute('opacity', d===null||+g.getAttribute('data-dec')===d ? 1 : 0.22);
  });
  document.querySelectorAll('#tlsvg rect[data-dec-band]').forEach(r=>{
    r.setAttribute('fill', d!==null&&+r.getAttribute('data-dec-band')===d
      ? 'rgba(255,255,255,0.03)' : 'transparent');
  });
}

// ---- póster: API REST de Wikipedia, es primero y en como respaldo ----
const cache={};
let current=-1;
function candidates(f){
  return [
    ['es', f.n], ['es', `${f.n} (película)`],
    ['es', `${f.n} (película de ${f.y})`], ['es', `${f.n} (película de ${f.y-1})`],
    ['en', f.n], ['en', `${f.n} (film)`], ['en', `${f.n} (${f.y-1} film)`],
  ];
}
async function lookup(lang,title){
  const r=await fetch(`https://${lang}.wikipedia.org/api/rest_v1/page/summary/`+
    encodeURIComponent(title.replace(/ /g,'_')));
  if(!r.ok) throw 0;
  const j=await r.json();
  if(j.type!=='standard') throw 0;
  const d=((j.description||'')+' '+(j.extract||'')).toLowerCase();
  if(!/película|film|cinta/.test(d)) throw 0;
  return j.thumbnail?j.thumbnail.source:null;
}
async function posterFor(f){
  if(f.n in cache) return cache[f.n];
  for(const [lg,t] of candidates(f)){
    try{ const u=await lookup(lg,t); cache[f.n]=u; return u; }catch(e){}
  }
  cache[f.n]=null; return null;
}
async function showFilm(i){
  const f=FILMS[i]; current=i;
  document.getElementById('filmTxt').textContent=f.n;
  document.getElementById('dirTxt').textContent=f.d;
  const et=document.getElementById('eraTxt');
  et.textContent=ERAS[f.e].n; et.style.color=ERAS[f.e].c;
  document.getElementById('yearTxt').textContent=
    `Ariel a Mejor Película · ${f.y} (edición ${f.ed})`;
  const img=document.getElementById('poster');
  img.removeAttribute('src'); img.alt='Cargando póster…';
  const u=await posterFor(f);
  if(current!==i) return;
  if(u){ img.src=u; img.alt=`Póster de ${f.n}`; }
  else { img.alt='Sin póster'; }
}
document.getElementById('reset').onclick=()=>{view={a:MINY,b:MAXY};render();};
const lg=document.getElementById('legend');
lg.innerHTML=ERAS.map(p=>
  `<span><span class="sw" style="background:${p.c}"></span>${esc(p.n)}</span>`).join('');
render();
showFilm(FILMS.length-1);
hook();
</script>
</body>
</html>
"""

html = HTML.replace("__FILMS__", films_js).replace("__ERAS__", eras_js)
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} bytes): {len(FILMS)} winning films, "
      f"{len(ERAS)} bands")
