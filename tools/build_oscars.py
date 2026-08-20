#!/usr/bin/env python3
"""Generate oscars.html, the Best Picture winners timeline for the Film section.

Winners and eras extracted from Brian's Mathematica notebook (Best Picture
Winners.nb); years are ceremony years. Anora (2025 ceremony) appended.
Posters are fetched by the page at view time from Wikipedia's public REST API
(candidate titles tried in order); none are stored in the repo.

Usage: python3 build_oscars.py
"""

import json
from pathlib import Path

OUT = Path(__file__).parent.parent / "oscars.html"

FILMS = [
    (1929, "Wings"), (1930, "The Broadway Melody"),
    (1931, "All Quiet on the Western Front"), (1932, "Grand Hotel"),
    (1933, "Cavalcade"), (1935, "It Happened One Night"),
    (1936, "Mutiny on the Bounty"), (1937, "The Great Ziegfeld"),
    (1938, "The Life of Emile Zola"), (1939, "You Can't Take It with You"),
    (1940, "Gone with the Wind"), (1941, "Rebecca"),
    (1942, "How Green Was My Valley"), (1943, "Mrs. Miniver"),
    (1944, "Casablanca"), (1945, "Going My Way"), (1946, "The Lost Weekend"),
    (1947, "The Best Years of Our Lives"), (1948, "Gentleman's Agreement"),
    (1949, "Hamlet"), (1950, "All the King's Men"), (1951, "All About Eve"),
    (1952, "An American in Paris"), (1953, "The Greatest Show on Earth"),
    (1954, "From Here to Eternity"), (1955, "On the Waterfront"),
    (1956, "Marty"), (1957, "Around the World in 80 Days"),
    (1958, "The Bridge on the River Kwai"), (1959, "Gigi"), (1960, "Ben-Hur"),
    (1961, "The Apartment"), (1962, "West Side Story"),
    (1963, "Lawrence of Arabia"), (1964, "Tom Jones"), (1965, "My Fair Lady"),
    (1966, "The Sound of Music"), (1967, "A Man for All Seasons"),
    (1968, "In the Heat of the Night"), (1969, "Oliver!"),
    (1970, "Midnight Cowboy"), (1971, "Patton"),
    (1972, "The French Connection"), (1973, "The Godfather"),
    (1974, "The Sting"), (1975, "The Godfather Part II"),
    (1976, "One Flew Over the Cuckoo's Nest"), (1977, "Rocky"),
    (1978, "Annie Hall"), (1979, "The Deer Hunter"),
    (1980, "Kramer vs. Kramer"), (1981, "Ordinary People"),
    (1982, "Chariots of Fire"), (1983, "Gandhi"),
    (1984, "Terms of Endearment"), (1985, "Amadeus"), (1986, "Out of Africa"),
    (1987, "Platoon"), (1988, "The Last Emperor"), (1989, "Rain Man"),
    (1990, "Driving Miss Daisy"), (1991, "Dances with Wolves"),
    (1992, "The Silence of the Lambs"), (1993, "Unforgiven"),
    (1994, "Schindler's List"), (1995, "Forrest Gump"), (1996, "Braveheart"),
    (1997, "The English Patient"), (1998, "Titanic"),
    (1999, "Shakespeare in Love"), (2000, "American Beauty"),
    (2001, "Gladiator"), (2002, "A Beautiful Mind"), (2003, "Chicago"),
    (2004, "The Lord of the Rings: The Return of the King"),
    (2005, "Million Dollar Baby"), (2006, "Crash"), (2007, "The Departed"),
    (2008, "No Country for Old Men"), (2009, "Slumdog Millionaire"),
    (2010, "The Hurt Locker"), (2011, "The King's Speech"),
    (2012, "The Artist"), (2013, "Argo"), (2014, "12 Years a Slave"),
    (2015, "Birdman"), (2016, "Spotlight"), (2017, "Moonlight"),
    (2018, "The Shape of Water"), (2019, "Green Book"), (2020, "Parasite"),
    (2021, "Nomadland"), (2022, "CODA"),
    (2023, "Everything Everywhere All at Once"), (2024, "Oppenheimer"),
    (2025, "Anora"),
]

ERAS = [
    (1929, 1939, "Early Academy Awards"),
    (1939, 1954, "Golden Age of Hollywood"),
    (1954, 1966, "Studio System Transition"),
    (1966, 1980, "New Hollywood Era"),
    (1980, 1993, "Blockbuster & Auteur Era"),
    (1993, 2005, "Independent Film Renaissance"),
    (2005, 2015, "Global Cinema Recognition"),
    (2015, 2025, "Streaming & Diversity Era"),
]

ERA_COLORS = ["#8b93a7", "#ffb02e", "#ff5c4d", "#31d67a",
              "#b48cf2", "#58a6ff", "#d1548e", "#2fc6a6"]


def era_index(year):
    for i, (a, b, _) in enumerate(ERAS):
        if year < b or i == len(ERAS) - 1:
            return i
    return len(ERAS) - 1


films_js = json.dumps([{"y": y, "n": n, "e": era_index(y)} for y, n in FILMS],
                      separators=(",", ":"))
eras_js = json.dumps([{"a": a, "b": b, "n": n, "c": ERA_COLORS[i]}
                      for i, (a, b, n) in enumerate(ERAS)],
                     separators=(",", ":"))

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Best Picture Winners · Altazor</title>
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
  <nav class="site"><a href="film.html">&larr; Film</a></nav>
</header>
<h1>Best Picture Winners</h1>
<div class="controls">
  <button id="reset">Reset view</button>
  <span class="info" id="info"></span>
</div>
<div class="stage">
  <div id="tl"></div>
  <div class="side"><div class="card">
    <img id="poster" alt="Film poster">
    <div id="filmTxt">Hover a film</div>
    <div id="eraTxt"></div>
    <div id="yearTxt"></div>
  </div></div>
</div>
<div class="legend" id="legend"></div>
<p class="note">Every Academy Award Best Picture winner, from Wings at the
first ceremony in 1929 to Anora in 2025, grouped into eight Hollywood eras.
The wheel zooms, dragging pans, a click on an era band zooms into it, and a
film under the cursor shows its poster.</p>
<p class="note">Years are ceremony years. Posters are loaded at view time from
Wikipedia's public API for identification and are not stored on this site; a
few may fail to resolve.</p>
</div>
<script>
const FILMS=__FILMS__, ERAS=__ERAS__;
const W=980,H=780,CY=385,MINY=1925,MAXY=2030;
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
    s+=`<rect x="${x0}" y="${CY+30}" width="${Math.max(2,x1-x0)}" height="22" rx="6"
      fill="${p.c}22" stroke="${p.c}" stroke-width="1" data-era="${i}" style="cursor:pointer"/>`;
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
    `${Math.round(view.a)} to ${Math.round(view.b)}`;
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
      document.getElementById('info').textContent=p.n+' ('+p.a+'-'+p.b+') \u00b7 click to zoom';
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

// ---- poster panel: Wikipedia REST API, candidates tried in order ----
const cache={};
let current=-1;
function candidates(f){
  const fy=f.y-1, fy2=f.y-2;
  return [f.n, `${f.n} (film)`, `${f.n} (${fy} film)`, `${f.n} (${fy2} film)`];
}
async function lookup(title){
  const r=await fetch('https://en.wikipedia.org/api/rest_v1/page/summary/'+
    encodeURIComponent(title.replace(/ /g,'_')));
  if(!r.ok) throw 0;
  const j=await r.json();
  if(j.type!=='standard') throw 0;
  const d=((j.description||'')+' '+(j.extract||'')).toLowerCase();
  if(!d.includes('film')) throw 0;
  return j.thumbnail?j.thumbnail.source:null;
}
async function posterFor(f){
  if(f.n in cache) return cache[f.n];
  for(const t of candidates(f)){
    try{ const u=await lookup(t); cache[f.n]=u; return u; }catch(e){}
  }
  cache[f.n]=null; return null;
}
async function showFilm(i){
  const f=FILMS[i]; current=i;
  document.getElementById('filmTxt').textContent=`${f.n}`;
  const et=document.getElementById('eraTxt');
  et.textContent=ERAS[f.e].n; et.style.color=ERAS[f.e].c;
  document.getElementById('yearTxt').textContent=`Best Picture, ${f.y} ceremony`;
  const img=document.getElementById('poster');
  img.removeAttribute('src'); img.alt='Loading poster\\u2026';
  const u=await posterFor(f);
  if(current!==i) return;
  if(u){ img.src=u; img.alt=`${f.n} poster`; }
  else { img.alt='No poster found'; }
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
print(f"wrote {OUT} ({len(html)} bytes): {len(FILMS)} films, {len(ERAS)} eras")
