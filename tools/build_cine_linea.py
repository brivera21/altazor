#!/usr/bin/env python3
"""Generate cine-cronologia.html: an Oscars-style timeline of the full Mexican
cinema master list (1,712 films) with individual entries and posters.

Top level shows dots plus clickable decade bands; clicking a decade zooms into
it and renders each film as a labeled entry (alternating above/below the axis,
lane-stacked, SVG height grows as needed). Hovering an entry loads its poster
from Wikipedia's REST API (Spanish Wikipedia first, then English). Page copy is
in Spanish, matching cine-mexicano.html (the histogram view of the same data).

Usage: python3 build_cine_linea.py
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE.parent / "cine-cronologia.html"

films = json.loads((HERE / "cine_films.json").read_text(encoding="utf-8"))
posters = json.loads((HERE / "cine_posters.json").read_text(encoding="utf-8"))
assert len(posters) == len(films)

ERAS = [
    (1896, 1931, "Cine mudo"),
    (1931, 1936, "Inicios del sonoro"),
    (1936, 1959, "Época de Oro"),
    (1959, 1970, "Años de transición"),
    (1970, 1980, "Nuevo Cine / años de Echeverría"),
    (1980, 1990, "Crisis y video"),
    (1990, 2000, "Nuevo Cine Mexicano"),
    (2000, 2013, "Proyección internacional"),
    (2013, 2026, "Era global y de streaming"),
]
ERA_COLORS = ["#8b93a7", "#b48cf2", "#ffb02e", "#ff5c4d", "#31d67a",
              "#d1548e", "#2fc6a6", "#58a6ff", "#e6c86e"]


def era_index(year):
    for i, (a, b, _) in enumerate(ERAS):
        if year < b:
            return i
    return len(ERAS) - 1


films_js = json.dumps([{"y": y, "n": n, "e": era_index(y)} for y, n in films],
                      separators=(",", ":"), ensure_ascii=False)
eras_js = json.dumps([{"a": a, "b": b, "n": n, "c": ERA_COLORS[i]}
                      for i, (a, b, n) in enumerate(ERAS)],
                     separators=(",", ":"), ensure_ascii=False)
posters_js = json.dumps(posters, separators=(",", ":"), ensure_ascii=False)

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cine Mexicano: Cronología · Altazor</title>
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
.controls button.dec { padding:5px 10px; font-size:12.5px; color:var(--muted); }
.controls button.dec:hover { color:var(--text); }
.controls .info { color:var(--muted); font-size:13px; margin-left:6px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#tl { flex:1 1 640px; min-width:0; max-height:78vh; overflow-y:auto;
  border:1px solid var(--line); border-radius:12px; background:#121212; }
#tl svg { width:100%; height:auto; display:block; cursor:grab; user-select:none; }
#tl.panning, #tl.panning * { cursor:grabbing !important; }
.side { flex:0 0 260px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:14px; }
#poster { width:100%; aspect-ratio:2/3; object-fit:contain; background:#101010;
  border-radius:6px; display:block; }
#filmTxt { font-weight:700; margin:10px 0 2px; font-size:15px; }
#dirTxt { color:var(--muted); font-size:13px; }
#eraTxt { font-size:13px; min-height:1.2em; }
#yearTxt { color:var(--muted); font-size:13px; margin-top:4px; }
.legend { display:flex; gap:14px; flex-wrap:wrap; margin-top:10px; font-size:12.5px; color:var(--muted); }
.legend span.sw { width:11px; height:11px; border-radius:3px; display:inline-block; margin-right:5px; }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
@media (max-width:900px){ .stage{flex-direction:column;} .side{position:static; width:100%;}
  #poster{max-width:220px; margin:0 auto;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="film.html">&larr; Film</a> &nbsp;·&nbsp;
    <a href="cine-mexicano.html">Histograma</a></nav>
</header>
<h1>Cine Mexicano: Cronología</h1>
<div class="controls" id="decnav">
  <button id="reset">Vista completa</button>
  <span class="info" id="info"></span>
</div>
<div class="stage">
  <div id="tl"></div>
  <div class="side"><div class="card">
    <img id="poster" alt="Póster">
    <div id="filmTxt">Ninguna película bajo el cursor</div>
    <div id="dirTxt"></div>
    <div id="eraTxt"></div>
    <div id="yearTxt"></div>
  </div></div>
</div>
<div class="legend" id="legend"></div>
<p class="note">Las 1,712 películas de la lista maestra, ahora una por una. Un
clic en la banda de una década entra a ella y muestra cada entrada con su
año; una película bajo el cursor muestra su póster. Ctrl (o &#8984;) +
rueda para acercar; la rueda sola sube y baja dentro del recuadro y arrastrar
mueve la vista en ambas direcciones. Con la vista completa solo se muestran puntos; las fichas
aparecen al entrar a una década.</p>
<p class="note">Pósters y directores provienen de
<a href="https://www.themoviedb.org" style="color:var(--accent)">TMDB</a>
(este sitio usa la API de TMDB pero no está avalado ni certificado por TMDB);
las imágenes se cargan desde su CDN solo para identificación y no se almacenan
aquí. Para los pocos títulos sin ficha en TMDB se consulta Wikipedia al
momento. Misma base de datos que el <a href="cine-mexicano.html"
style="color:var(--accent)">histograma</a>.</p>
</div>
<script>
const FILMS=__FILMS__, ERAS=__ERAS__, PD=__POSTERS__;
const MINY=1893,MAXY=2028,W=980,LABEL_CAP=460;
let view={a:MINY,b:MAXY};

const el=document.getElementById('tl');
const X=y=>(y-view.a)/(view.b-view.a)*W;
const YR=x=>view.a+x/W*(view.b-view.a);
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
const DECS=[];
{ const ys=FILMS.map(f=>f.y);
  for(let d=Math.floor(Math.min(...ys)/10)*10; d<=Math.max(...ys); d+=10)
    if(FILMS.some(f=>f.y>=d&&f.y<d+10)) DECS.push(d); }

function ticks(){
  const span=view.b-view.a;
  const step=span>60?10:span>25?5:span>12?2:1;
  const out=[];
  for(let y=Math.ceil(view.a/step)*step;y<=view.b;y+=step) out.push(y);
  return out;
}
let laneData=null, laneSpanKey=0;
function layoutForSpan(){
  const span=view.b-view.a;
  if(laneData && Math.abs(span-laneSpanKey)<1e-6) return laneData;
  const pxY=W/span;
  const items=FILMS.map((f,i)=>({y:f.y,n:f.n,e:f.e,fi:i}));
  items.sort((a,b)=>a.y-b.y||a.n.localeCompare(b.n));
  items.forEach((f,i)=>{ f.w=Math.min(215,(f.n.length+7)*6.2)+14; f.up=(i%2===0); });
  const assign=arr=>{ const ends=[]; let mx=0;
    for(const it of arr){
      const x0=(it.y+0.5)-((it.w-14)/2)/pxY;
      let l=0; while(l<ends.length && ends[l]>x0) l++;
      it.lane=l; ends[l]=(it.y+0.5)+(((it.w-14)/2)+8)/pxY; mx=Math.max(mx,l);
    }
    return mx; };
  const upMax=assign(items.filter(f=>f.up));
  const dnMax=assign(items.filter(f=>!f.up));
  laneData={items,upMax,dnMax}; laneSpanKey=span;
  return laneData;
}
function render(){
  const vis=FILMS.map((f,i)=>({...f,fi:i})).filter(f=>f.y+1>=view.a&&f.y<=view.b);
  const labelMode=vis.length<=LABEL_CAP;
  let upMax=0,dnMax=0,fs=[];
  if(labelMode){
    const L=layoutForSpan();
    upMax=L.upMax; dnMax=L.dnMax;
    fs=L.items.filter(f=>f.y+1>=view.a-1&&f.y<=view.b+1)
      .map(f=>({...f,x:X(f.y+0.5),cx:X(f.y+0.5)}));
  }
  const CY=labelMode?70+(upMax+1)*26+20:230;
  const H=labelMode?CY+120+(dnMax+1)*26+40:400;
  let s=`<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" id="tlsvg">`;
  s+=`<rect width="${W}" height="${H}" fill="#121212"/>`;
  for(const y of ticks()){
    const x=X(y);
    s+=`<line x1="${x}" y1="26" x2="${x}" y2="${H-26}" stroke="#242424"/>`;
    s+=`<text x="${x}" y="${CY+20}" text-anchor="middle" font-size="12.5" font-weight="700"
      fill="#9a9a9a">${y}</text>`;
  }
  s+=`<line x1="0" y1="${CY}" x2="${W}" y2="${CY}" stroke="#3a3a3a" stroke-width="2"/>`;
  for(const d of DECS){
    if(d+10<view.a||d>view.b) continue;
    const x0=Math.max(0,X(d)), x1=Math.min(W,X(d+10));
    if(x1-x0<2) continue;
    const n=FILMS.filter(f=>f.y>=d&&f.y<d+10).length;
    s+=`<rect x="${x0}" y="${CY+30}" width="${Math.max(2,x1-x0)}" height="22" rx="6"
      fill="#58a6ff18" stroke="#3d5a80" stroke-width="1" data-dec-band="${d}" style="cursor:pointer"/>`;
    if(x1-x0>60) s+=`<text x="${(x0+x1)/2}" y="${CY+45}" text-anchor="middle" font-size="11.5"
      fill="#9ec3ef" pointer-events="none">${d}s · ${n}</text>`;
  }
  if(!labelMode){
    const seen={};
    for(const f of vis){
      const k=f.y; seen[k]=(seen[k]||0)+1;
      const x=X(f.y+0.5), stack=seen[k];
      const yy=CY-8-(stack-1)*4.6;
      if(yy<40) continue;
      s+=`<circle cx="${x}" cy="${yy}" r="1.9" fill="${ERAS[f.e].c}" opacity="0.9"
        data-dot="${f.fi}" data-dec="${Math.floor(f.y/10)*10}"/>`;
    }
    s+=`<text x="${W/2}" y="${H-40}" text-anchor="middle" font-size="13"
      fill="#777">Un clic en una década muestra sus fichas</text>`;
  } else {
    for(const f of fs){
      const c=ERAS[f.e].c;
      const ly=f.up ? CY-42-f.lane*26 : CY+108+f.lane*26;
      const dotY=f.up ? CY-6 : CY+6;
      const tipY=f.up ? ly+9 : ly-9;
      const label=`${f.n} (${f.y})`;
      s+=`<g data-f="${f.fi}" data-dec="${Math.floor(f.y/10)*10}" style="cursor:default">
        <line x1="${f.x}" y1="${dotY}" x2="${f.x}" y2="${tipY}" stroke="${c}" stroke-width="1" opacity="0.55"/>
        <circle cx="${f.x}" cy="${dotY}" r="2.8" fill="${c}"/>
        <rect x="${f.cx-f.w/2}" y="${ly-8}" width="${f.w}" height="20" rx="7"
          fill="#1a1a1a" stroke="${c}" stroke-width="1"/>
        <text x="${f.cx}" y="${ly+6}" text-anchor="middle" font-size="11.3" font-weight="600"
          fill="#e6e6e6" pointer-events="none">${esc(label).slice(0,40)}</text></g>`;
    }
  }
  s+='</svg>';
  el.innerHTML=s;
  const n=vis.length;
  document.getElementById('info').textContent=
    `${Math.round(view.a)} a ${Math.round(view.b)} · ${n} película${n===1?'':'s'} a la vista`;
}
function clampView(a,b){
  const span=Math.min(MAXY-MINY,Math.max(4,b-a));
  a=Math.max(MINY,Math.min(a,MAXY-span));
  return {a,b:a+span};
}
function gotoDecade(d){
  view=clampView(d-0.6,d+10.6);
  render();
}
function hook(){
  const px=e=>{const r=el.getBoundingClientRect();return (e.clientX-r.left)/r.width*W;};
  el.addEventListener('wheel',e=>{
    if(e.ctrlKey||e.metaKey){
      e.preventDefault();
      const mag=Math.min(Math.abs(e.deltaY),50);
      const k=Math.exp((e.deltaY>0?1:-1)*mag*0.002);
      const yr=YR(px(e));
      view=clampView(yr-(yr-view.a)*k, yr+(view.b-yr)*k);
      render();
    }else if(Math.abs(e.deltaX)>Math.abs(e.deltaY)){
      e.preventDefault();
      const dyr=Math.max(-60,Math.min(60,e.deltaX))/W*(view.b-view.a)*0.45;
      view=clampView(view.a+dyr,view.b+dyr);
      render();
    }
    // rueda vertical sin modificador: la página se desplaza normalmente
  },{passive:false});
  let drag=null, dragged=false;
  el.addEventListener('pointerdown',e=>{drag={x:px(e),y:e.clientY,a:view.a,b:view.b};dragged=false;el.classList.add('panning');el.setPointerCapture(e.pointerId);});
  el.addEventListener('pointermove',e=>{
    if(!drag) return;
    const dx=px(e)-drag.x, dy=e.clientY-drag.y;
    if(Math.abs(dx)>2||Math.abs(dy)>2) dragged=true;
    const dyr=dx/W*(drag.b-drag.a);
    view=clampView(drag.a-dyr, drag.b-dyr);
    if(dy){ el.scrollTop-=dy; drag.y=e.clientY; }
    render();
  });
  el.addEventListener('pointerup',()=>{drag=null;el.classList.remove('panning');});
  el.addEventListener('pointercancel',()=>{drag=null;el.classList.remove('panning');});
  el.addEventListener('click',e=>{
    if(dragged){dragged=false;return;}
    const db=e.target.closest('[data-dec-band]');
    if(db){gotoDecade(+db.getAttribute('data-dec-band'));}
  });
  el.addEventListener('pointerover',e=>{
    const g=e.target.closest('[data-f]')||e.target.closest('[data-dot]');
    if(g){ const i=+(g.getAttribute('data-f')??g.getAttribute('data-dot'));
      showFilm(i); setFocus(+g.getAttribute('data-dec')); return; }
    const db=e.target.closest('[data-dec-band]');
    if(db){ const d=+db.getAttribute('data-dec-band');
      document.getElementById('info').textContent=
        d+'s · clic para entrar a la década';
      setFocus(d); return; }
    // huecos entre fichas: se conserva el enfoque actual (sin parpadeo)
  });
  el.addEventListener('pointerleave',()=>setFocus(null));
}
let focusD=null;
function setFocus(d){
  if(d===focusD) return;
  focusD=d;
  document.querySelectorAll('#tlsvg [data-dec]').forEach(g=>{
    g.setAttribute('opacity', d===null||+g.getAttribute('data-dec')===d ? 1 : 0.22);
  });
}

// ---- panel de pósters: API REST de Wikipedia (es primero, luego en) ----
const cache={};
let current=-1;
function candidates(f){
  return [
    ['es', f.n], ['es', `${f.n} (película)`], ['es', `${f.n} (película de ${f.y})`],
    ['en', f.n], ['en', `${f.n} (film)`], ['en', `${f.n} (${f.y} film)`],
  ];
}
async function lookup(lang,title,year){
  const r=await fetch(`https://${lang}.wikipedia.org/api/rest_v1/page/summary/`+
    encodeURIComponent(title.replace(/ /g,'_')));
  if(!r.ok) throw 0;
  const j=await r.json();
  if(j.type!=='standard') throw 0;
  const d=((j.description||'')+' '+(j.extract||'')).toLowerCase();
  if(!/pel\\u00edcula|film|cine|documental/.test(d.normalize('NFC'))) throw 0;
  if(!new RegExp('\\\\b('+(year-1)+'|'+year+'|'+(year+1)+')\\\\b').test(d)) throw 0;
  if(!j.thumbnail) throw 0;
  return j.thumbnail.source;
}
async function posterFor(f){
  const k=f.n+'|'+f.y;
  if(k in cache) return cache[k];
  for(const [lang,t] of candidates(f)){
    try{ const u=await lookup(lang,t,f.y); cache[k]=u; return u; }catch(e){}
  }
  cache[k]=null; return null;
}
async function showFilm(i){
  const f=FILMS[i]; current=i;
  document.getElementById('filmTxt').textContent=f.n;
  const [pp,dd]=PD[i]||['',''];
  document.getElementById('dirTxt').textContent=dd?('Dir. '+dd):'';
  const et=document.getElementById('eraTxt');
  et.textContent=ERAS[f.e].n; et.style.color=ERAS[f.e].c;
  document.getElementById('yearTxt').textContent=String(f.y);
  const img=document.getElementById('poster');
  if(pp){ img.src='https://image.tmdb.org/t/p/w342'+pp; img.alt='P\u00f3ster de '+f.n; return; }
  img.removeAttribute('src'); img.alt='Cargando p\\u00f3ster\\u2026';
  const u=await posterFor(f);
  if(current!==i) return;
  if(u){ img.src=u; img.alt=`P\\u00f3ster de ${f.n}`; }
  else { img.alt='Sin p\\u00f3ster'; }
}
document.getElementById('reset').onclick=()=>{view={a:MINY,b:MAXY};render();};
const nav=document.getElementById('decnav');
for(const d of DECS){
  const b=document.createElement('button');
  b.className='dec'; b.textContent=d+'s';
  b.onclick=()=>gotoDecade(d);
  nav.insertBefore(b, document.getElementById('info'));
}
const lg=document.getElementById('legend');
lg.innerHTML=ERAS.map(p=>
  `<span><span class="sw" style="background:${p.c}"></span>${esc(p.n)}</span>`).join('');
render();
hook();
</script>
</body>
</html>
"""

html = (HTML.replace("__FILMS__", films_js).replace("__ERAS__", eras_js)
        .replace("__POSTERS__", posters_js))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html)} bytes): {len(films)} films")
