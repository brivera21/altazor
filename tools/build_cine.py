#!/usr/bin/env python3
"""Generate cine-mexicano.html, a density timeline of the Mexican cinema
master list (1,712 films, 1896-2025) for the Film section.

The chart shows films per year; clicking a year or an era band reveals the
films for that period in a side panel. Data lives in cine_films.json (built
from the master list compiled from Brian's lists plus the 1001 Mexican Films
Letterboxd list, with original titles restored via Letterboxd).

Usage: python3 build_cine.py
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE.parent / "cine-mexicano.html"

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


films_js = json.dumps([{"y": y, "n": n, "d": posters[i][1]}
                       for i, (y, n) in enumerate(films)],
                      separators=(",", ":"), ensure_ascii=False)
eras_js = json.dumps([{"a": a, "b": b, "n": n, "c": ERA_COLORS[i]}
                      for i, (a, b, n) in enumerate(ERAS)],
                     separators=(",", ":"), ensure_ascii=False)

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cine Mexicano · Altazor</title>
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
.side { flex:0 0 320px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:14px; }
#selTitle { font-weight:700; font-size:15px; margin:0 0 2px; }
#selSub { font-size:13px; min-height:1.2em; margin-bottom:8px; }
#filmList { list-style:none; margin:0; padding:0; max-height:560px; overflow:auto;
  font-size:13.5px; }
#filmList li { padding:3px 4px; border-bottom:1px solid #222; }
#filmList li:last-child { border-bottom:none; }
#filmList a { color:var(--text); text-decoration:none; }
#filmList a:hover { color:var(--accent); }
#filmList .yr { color:var(--muted); font-size:12px; margin-left:6px; }
#filmList .dir { color:var(--muted); font-size:11.5px; line-height:1.3; }
.legend { display:flex; gap:14px; flex-wrap:wrap; margin-top:10px; font-size:12.5px; color:var(--muted); }
.legend span.sw { width:11px; height:11px; border-radius:3px; display:inline-block; margin-right:5px; }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
@media (max-width:900px){ .stage{flex-direction:column;} .side{position:static; width:100%;}
  #filmList{max-height:300px;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="film.html">&larr; Film</a></nav>
</header>
<h1>Cine Mexicano</h1>
<div class="controls">
  <button id="reset">Restablecer vista</button>
  <span class="info" id="info"></span>
</div>
<div class="stage">
  <div id="tl"></div>
  <div class="side"><div class="card">
    <div id="selTitle">Un año o una era, sin seleccionar</div>
    <div id="selSub"></div>
    <ul id="filmList"></ul>
  </div></div>
</div>
<div class="legend" id="legend"></div>
<p class="note">Una lista maestra del cine mexicano: 1,712 películas de 1896
a 2025, mostradas como películas por año. Ctrl (o &#8984;) + rueda para
acercar; arrastrar desplaza. Un clic en la barra de un año lista sus
películas, y uno en la banda de una era acerca a ella y la lista. El auge de la Época de
Oro y el repunte posterior al 2000 saltan a la vista.</p>
<p class="note">Compilada a partir de Letterboxd, Cine Mexicano, Su
Historia, Somos Cine y las películas enviadas por México al premio Óscar;
títulos originales en español, conservando el inglés o el francés cuando esa es
la lengua original. Algunas entradas son producciones internacionales
estrechamente ligadas al cine mexicano.</p>
</div>
<script>
const FILMS=__FILMS__, ERAS=__ERAS__;
const MINY=1893,MAXY=2028;
const W=980,H=560,BASE=440;
let view={a:MINY,b:MAXY};

const COUNTS={};
for(const f of FILMS) COUNTS[f.y]=(COUNTS[f.y]||0)+1;
const MAXC=Math.max(...Object.values(COUNTS));

const el=document.getElementById('tl');
const X=y=>(y-view.a)/(view.b-view.a)*W;
const YR=x=>view.a+x/W*(view.b-view.a);
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
const eraOf=y=>{for(let i=0;i<ERAS.length;i++) if(y<ERAS[i].b) return i; return ERAS.length-1;};

function ticks(){
  const span=view.b-view.a;
  const step=span>60?10:span>25?5:span>12?2:1;
  const out=[];
  for(let y=Math.ceil(view.a/step)*step;y<=view.b;y+=step) out.push(y);
  return out;
}
function render(){
  let s=`<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" id="tlsvg">`;
  s+=`<rect width="${W}" height="${H}" fill="#121212"/>`;
  const scaleH=c=>c/MAXC*(BASE-70);
  for(const y of ticks()){
    const x=X(y);
    s+=`<line x1="${x}" y1="26" x2="${x}" y2="${BASE}" stroke="#242424"/>`;
    s+=`<text x="${x}" y="${BASE+18}" text-anchor="middle" font-size="12.5" font-weight="700"
      fill="#9a9a9a">${y}</text>`;
  }
  for(const c of [10,20,30,40]){
    const gy=BASE-scaleH(c);
    s+=`<line x1="0" y1="${gy}" x2="${W}" y2="${gy}" stroke="#1e1e1e"/>`;
    s+=`<text x="4" y="${gy-3}" font-size="10.5" fill="#555">${c}</text>`;
  }
  for(let d=Math.floor(view.a/10)*10; d<view.b; d+=10){
    const x0=Math.max(0,X(d)), x1=Math.min(W,X(d+10));
    if(x1-x0<2) continue;
    s+=`<rect x="${x0}" y="26" width="${x1-x0}" height="${BASE-26}" fill="transparent"
      data-dec-band="${d}"/>`;
  }
  s+=`<line x1="0" y1="${BASE}" x2="${W}" y2="${BASE}" stroke="#3a3a3a" stroke-width="2"/>`;
  const yw=W/(view.b-view.a);
  for(let y=Math.floor(view.a);y<=Math.ceil(view.b);y++){
    const c=COUNTS[y]; if(!c) continue;
    const col=ERAS[eraOf(y)].c;
    const bw=Math.max(1.6,yw*0.72), x=X(y+0.5)-bw/2, h=Math.max(2,scaleH(c));
    s+=`<g data-yr="${y}" data-dec="${Math.floor(y/10)*10}" style="cursor:pointer">
      <rect x="${x}" y="${BASE-h}" width="${bw}" height="${h}" rx="${Math.min(3,bw/3)}"
        fill="${col}" opacity="0.85"/></g>`;
    if(yw>26) s+=`<text x="${X(y+0.5)}" y="${BASE-h-5}" text-anchor="middle" font-size="10.5"
      fill="#777" pointer-events="none">${c}</text>`;
  }
  ERAS.forEach((p,i)=>{
    if(p.b<view.a||p.a>view.b) return;
    const x0=Math.max(0,X(p.a)), x1=Math.min(W,X(p.b));
    s+=`<rect x="${x0}" y="${BASE+30}" width="${Math.max(2,x1-x0)}" height="22" rx="6"
      fill="${p.c}22" stroke="${p.c}" stroke-width="1" data-era="${i}" style="cursor:pointer"/>`;
    if(x1-x0>140) s+=`<text x="${(x0+x1)/2}" y="${BASE+45}" text-anchor="middle" font-size="11.5"
      fill="${p.c}" pointer-events="none">${esc(p.n)} (${p.a}–${p.b===2026?2025:p.b})</text>`;
  });
  s+='</svg>';
  el.innerHTML=s;
  document.getElementById('info').textContent=
    `${Math.round(view.a)} a ${Math.round(view.b)} · ${FILMS.length} películas en total`;
}
function clampView(a,b){
  const span=Math.min(MAXY-MINY,Math.max(6,b-a));
  a=Math.max(MINY,Math.min(a,MAXY-span));
  return {a,b:a+span};
}
function lbUrl(f){
  return 'https://letterboxd.com/search/films/'+encodeURIComponent(f.n+' '+f.y)+'/';
}
function showRange(a,b,title,sub,color){
  const list=FILMS.filter(f=>f.y>=a&&f.y<b);
  document.getElementById('selTitle').textContent=title;
  const ss=document.getElementById('selSub');
  ss.textContent=sub+' · '+list.length+' película'+(list.length===1?'':'s');
  ss.style.color=color||'var(--muted)';
  document.getElementById('filmList').innerHTML=list.map(f=>
    `<li><a href="${lbUrl(f)}" target="_blank" rel="noopener">${esc(f.n)}</a>`+
    (b-a>1?`<span class="yr">${f.y}</span>`:'')+
    (f.d?`<div class="dir">${esc(f.d)}</div>`:'')+'</li>').join('');
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
    const yg=e.target.closest('[data-yr]');
    if(yg){const y=+yg.getAttribute('data-yr');
      showRange(y,y+1,String(y),ERAS[eraOf(y)].n,ERAS[eraOf(y)].c);return;}
    const g=e.target.closest('[data-era]');
    if(g){const i=+g.getAttribute('data-era'), p=ERAS[i];
      view=clampView(p.a-2,p.b+2);render();
      showRange(p.a,p.b,p.n,(p.a)+'–'+(p.b===2026?2025:p.b),p.c);return;}
    const db=e.target.closest('[data-dec-band]');
    if(db){const d=+db.getAttribute('data-dec-band');
      showRange(d,d+10,'Década de '+d,'década',null);}
  });
  el.addEventListener('pointerover',e=>{
    const yg=e.target.closest('[data-yr]');
    if(yg){const y=+yg.getAttribute('data-yr');
      document.getElementById('info').textContent=
        y+' · '+COUNTS[y]+' película'+(COUNTS[y]===1?'':'s')+' · clic para listar';
      setFocus(Math.floor(y/10)*10);return;}
    const b=e.target.closest('[data-era]');
    if(b){const p=ERAS[+b.getAttribute('data-era')];
      document.getElementById('info').textContent=
        p.n+' · clic para acercar y listar';
      setFocus(null);return;}
    const db=e.target.closest('[data-dec-band]');
    setFocus(db ? +db.getAttribute('data-dec-band') : null);
  });
  el.addEventListener('pointerleave',()=>setFocus(null));
}
function setFocus(d){
  document.querySelectorAll('#tlsvg g[data-dec]').forEach(g=>{
    g.setAttribute('opacity', d===null||+g.getAttribute('data-dec')===d ? 1 : 0.25);
  });
  document.querySelectorAll('#tlsvg rect[data-dec-band]').forEach(r=>{
    r.setAttribute('fill', d!==null&&+r.getAttribute('data-dec-band')===d
      ? 'rgba(255,255,255,0.03)' : 'transparent');
  });
}
document.getElementById('reset').onclick=()=>{view={a:MINY,b:MAXY};render();};
const lg=document.getElementById('legend');
lg.innerHTML=ERAS.map(p=>
  `<span><span class="sw" style="background:${p.c}"></span>${esc(p.n)}</span>`).join('');
render();
hook();
</script>
</body>
</html>
"""

html = HTML.replace("__FILMS__", films_js).replace("__ERAS__", eras_js)
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html)} bytes): {len(films)} films, {len(ERAS)} eras")
