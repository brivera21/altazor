#!/usr/bin/env python3
"""Generate the Science Fiction timelines:

    hugo-nebula.html   every Hugo and Nebula Best Novel winner, one timeline
    scifi-canon.html   the books that built the genre, from Frankenstein on

Same interaction model as cine-cronologia.html: decade bands to click into,
lane-stacked labeled entries, Ctrl+wheel zoom, drag pan, hover for the book
cover in a side card. Covers come from a prebuilt Open Library manifest
(tools/scifi_covers.json, "Title|Year" -> cover id); anything missing is
looked up live from the Open Library search API in the reader's browser.

Usage: python3 build_scifi.py
"""

import json
from pathlib import Path

from scifi_data import AWARDS, CANON, CANON_ERAS

HERE = Path(__file__).parent
COVERS_PATH = HERE / "scifi_covers.json"
COVERS = (json.loads(COVERS_PATH.read_text(encoding="utf-8"))
          if COVERS_PATH.exists() else {})

CANON_COLORS = ["#8b93a7", "#b48cf2", "#ffb02e", "#ff5c4d", "#31d67a",
                "#d1548e", "#2fc6a6", "#58a6ff", "#e6c86e"]
AWARD_CATS = [
    {"n": "Hugo", "c": "#ffb02e"},
    {"n": "Nebula", "c": "#b48cf2"},
    {"n": "Both awards", "c": "#31d67a"},
]


def canon_era(year):
    for i, (a, b, _) in enumerate(CANON_ERAS):
        if year < b:
            return i
    return len(CANON_ERAS) - 1


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ · Altazor</title>
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
#cover { width:100%; aspect-ratio:2/3; object-fit:contain; background:#101010;
  border-radius:6px; display:block; }
#bookTxt { font-weight:700; margin:10px 0 2px; font-size:15px; }
#authTxt { color:var(--muted); font-size:13px; }
#badgeTxt { font-size:13px; min-height:1.2em; }
#yearTxt { color:var(--muted); font-size:13px; margin-top:4px; }
.legend { display:flex; gap:14px; flex-wrap:wrap; margin-top:10px; font-size:12.5px; color:var(--muted); }
.legend span.sw { width:11px; height:11px; border-radius:3px; display:inline-block; margin-right:5px; }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
@media (max-width:900px){ .stage{flex-direction:column;} .side{position:static; width:100%;}
  #cover{max-width:220px; margin:0 auto;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="science-fiction.html">&larr; Science Fiction</a>__XNAV__</nav>
</header>
<h1>__H1__</h1>
<div class="controls" id="decnav">
  <button id="reset">Full view</button>
  <span class="info" id="info"></span>
</div>
<div class="stage">
  <div id="tl"></div>
  <div class="side"><div class="card">
    <img id="cover" alt="Cover">
    <div id="bookTxt">Hover over a book</div>
    <div id="authTxt"></div>
    <div id="badgeTxt"></div>
    <div id="yearTxt"></div>
  </div></div>
</div>
<div class="legend" id="legend"></div>
<p class="note">__LEDE__</p>
<p class="note">Covers come from <a href="https://openlibrary.org"
style="color:var(--accent)">Open Library</a> and are loaded from its
servers for identification only.__XNOTE__</p>
</div>
<script>
const BOOKS=__BOOKS__, CATS=__CATS__, COVERS=__COVERS__;
const MINY=__MINY__,MAXY=__MAXY__,W=980,LABEL_CAP=460;
let view={a:MINY,b:MAXY};

const el=document.getElementById('tl');
const X=y=>(y-view.a)/(view.b-view.a)*W;
const YR=x=>view.a+x/W*(view.b-view.a);
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
const DECS=[];
{ const ys=BOOKS.map(f=>f.y);
  for(let d=Math.floor(Math.min(...ys)/10)*10; d<=Math.max(...ys); d+=10)
    if(BOOKS.some(f=>f.y>=d&&f.y<d+10)) DECS.push(d); }

function ticks(){
  const span=view.b-view.a;
  const step=span>120?20:span>60?10:span>25?5:span>12?2:1;
  const out=[];
  for(let y=Math.ceil(view.a/step)*step;y<=view.b;y+=step) out.push(y);
  return out;
}
let laneData=null, laneSpanKey=0;
function layoutForSpan(){
  const span=view.b-view.a;
  if(laneData && Math.abs(span-laneSpanKey)<1e-6) return laneData;
  const pxY=W/span;
  const items=BOOKS.map((f,i)=>({y:f.y,n:f.n,e:f.e,fi:i}));
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
  const vis=BOOKS.map((f,i)=>({...f,fi:i})).filter(f=>f.y+1>=view.a&&f.y<=view.b);
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
    const n=BOOKS.filter(f=>f.y>=d&&f.y<d+10).length;
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
      s+=`<circle cx="${x}" cy="${yy}" r="1.9" fill="${CATS[f.e].c}" opacity="0.9"
        data-dot="${f.fi}" data-dec="${Math.floor(f.y/10)*10}"/>`;
    }
  } else {
    for(const f of fs){
      const c=CATS[f.e].c;
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
    `${Math.round(view.a)} to ${Math.round(view.b)} · ${n} book${n===1?'':'s'} in view`;
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
      showBook(i); setFocus(+g.getAttribute('data-dec')); return; }
    const db=e.target.closest('[data-dec-band]');
    if(db){ const d=+db.getAttribute('data-dec-band');
      document.getElementById('info').textContent=
        d+'s · click to enter the decade';
      setFocus(d); return; }
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

// ---- cover panel: manifest first, Open Library search as fallback ----
const cache={};
let current=-1;
async function coverFor(f){
  const k=f.n+'|'+f.y;
  if(k in COVERS && COVERS[k]) return 'https://covers.openlibrary.org/b/id/'+COVERS[k]+'-L.jpg';
  if(k in cache) return cache[k];
  try{
    const q='https://openlibrary.org/search.json?limit=8&fields=cover_i,first_publish_year,title'+
      '&title='+encodeURIComponent(f.n)+'&author='+encodeURIComponent(f.a.split(' and ')[0]);
    const r=await fetch(q); const j=await r.json();
    let best=null;
    for(const d of (j.docs||[])){
      if(!d.cover_i) continue;
      if(d.first_publish_year && Math.abs(d.first_publish_year-f.y)<=2){ best=d; break; }
      if(!best) best=d;
    }
    const u=best?('https://covers.openlibrary.org/b/id/'+best.cover_i+'-L.jpg'):null;
    cache[k]=u; return u;
  }catch(e){ cache[k]=null; return null; }
}
async function showBook(i){
  const f=BOOKS[i]; current=i;
  document.getElementById('bookTxt').textContent=f.n;
  document.getElementById('authTxt').textContent=f.a;
  const bt=document.getElementById('badgeTxt');
  bt.textContent=f.b; bt.style.color=CATS[f.e].c;
  document.getElementById('yearTxt').textContent=String(f.y);
  const img=document.getElementById('cover');
  img.removeAttribute('src'); img.alt='Loading cover';
  const u=await coverFor(f);
  if(current!==i) return;
  if(u){ img.src=u; img.alt='Cover of '+f.n; }
  else { img.alt='No cover found'; }
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
lg.innerHTML=CATS.map(p=>
  `<span><span class="sw" style="background:${p.c}"></span>${esc(p.n)}</span>`).join('');
render();
hook();
</script>
</body>
</html>
"""


def emit(outname, title, h1, lede, books, cats, miny, maxy, xnav, xnote):
    books_js = json.dumps(books, separators=(",", ":"), ensure_ascii=False)
    cats_js = json.dumps(cats, separators=(",", ":"), ensure_ascii=False)
    covers_js = json.dumps(
        {k: v for k, v in COVERS.items()
         if any(b["n"] + "|" + str(b["y"]) == k for b in books)},
        separators=(",", ":"), ensure_ascii=False)
    html = (HTML.replace("__TITLE__", title).replace("__H1__", h1)
            .replace("__LEDE__", lede).replace("__BOOKS__", books_js)
            .replace("__CATS__", cats_js).replace("__COVERS__", covers_js)
            .replace("__MINY__", str(miny)).replace("__MAXY__", str(maxy))
            .replace("__XNAV__", xnav).replace("__XNOTE__", xnote))
    out = HERE.parent / outname
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({len(html)} bytes): {len(books)} books")


# ---- awards page ----
award_books = []
for y, n, a, h, nb in AWARDS:
    cat = 2 if (h and nb) else (0 if h else 1)
    badge = (" · ".join(x for x in
             [f"Hugo {h}" if h else "", f"Nebula {nb}" if nb else ""] if x))
    award_books.append({"y": y, "n": n, "a": a, "e": cat, "b": badge})

emit(
    "hugo-nebula.html",
    "Hugo and Nebula Winners",
    "Hugo and Nebula Winners",
    "Every Best Novel winner of both awards on one timeline. A book that "
    "won both appears once, in green. Click the band of a decade to enter "
    "it and see each book with its year; hover over a book to see its "
    "cover. Ctrl (or ⌘) + wheel zooms; the wheel alone scrolls "
    "inside the frame and dragging pans the view.",
    award_books, AWARD_CATS, 1948, 2028,
    ' &nbsp;·&nbsp; <a href="scifi-canon.html">The canon</a>',
    " The Hugo year is the year the award was presented; the Nebula year "
    "is the award's own label. The 2026 Hugo is presented on August 30, "
    "2026.",
)

# ---- canon page ----
canon_books = [{"y": y, "n": n, "a": a, "e": canon_era(y),
                "b": CANON_ERAS[canon_era(y)][2]}
               for y, n, a in CANON]
canon_cats = [{"n": n, "c": CANON_COLORS[i]}
              for i, (a, b, n) in enumerate(CANON_ERAS)]

emit(
    "scifi-canon.html",
    "A Canon of Science Fiction",
    "A Canon of Science Fiction",
    "The books that built the genre, from Frankenstein forward, colored "
    "by era. Click the band of a decade to enter it; hover over a book "
    "to see its cover. Ctrl (or ⌘) + wheel zooms; the wheel alone "
    "scrolls inside the frame and dragging pans the view.",
    canon_books, canon_cats, 1810, 2028,
    ' &nbsp;·&nbsp; <a href="hugo-nebula.html">Hugo and Nebula</a>',
    " The list is editorial: the books here are the ones that defined "
    "what science fiction could do, not a complete history.",
)
