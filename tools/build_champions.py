#!/usr/bin/env python3
"""Generate world-champions.html, the world chess champions timeline for the
Chess section.

The classical, undisputed lineage from Steinitz to today, each reign drawn as
a span on the axis. Dates cross-checked against the Wikipedia list of world
chess champions and FIDE announcements, August 2026. The 1946-1948 interregnum
is its own hatched span. Portraits are fetched by the page at view time from
Wikipedia's public REST API; none are stored in the repo.

Usage: python3 build_champions.py
"""

import json
from pathlib import Path

OUT = Path(__file__).parent.parent / "world-champions.html"

NOW = 2026  # drawn as the open end of the current reign

# One entry per reign: name, country, start, end (None = current), note on the
# reign ordinal, how it was gained, how it ended, lived, wikipedia title.
R = [
    ("Wilhelm Steinitz", "Austria-Hungary, a US citizen from 1888", 1886, 1894, "",
     "Beat Zukertort in the first official championship match",
     "Lost the title to Lasker in 1894", "1836-1900", "Wilhelm Steinitz"),
    ("Emanuel Lasker", "Germany", 1894, 1921, "",
     "Beat Steinitz in 1894",
     "Lost to Capablanca in 1921, after twenty-seven years, the longest reign",
     "1868-1941", "Emanuel Lasker"),
    ("José Raúl Capablanca", "Cuba", 1921, 1927, "",
     "Beat Lasker in Havana without losing a game",
     "Lost to Alekhine in Buenos Aires in 1927", "1888-1942",
     "José Raúl Capablanca"),
    ("Alexander Alekhine", "France, born in Russia", 1927, 1935, "first reign",
     "Beat Capablanca in 1927",
     "Lost to Euwe in 1935", "1892-1946", "Alexander Alekhine"),
    ("Max Euwe", "Netherlands", 1935, 1937, "",
     "Beat Alekhine in 1935",
     "Lost the rematch in 1937", "1901-1981", "Max Euwe"),
    ("Alexander Alekhine", "France", 1937, 1946, "second reign",
     "Won the rematch against Euwe",
     "Died holding the title in March 1946, the only champion to do so",
     "1892-1946", "Alexander Alekhine"),
    ("Interregnum", "", 1946, 1948, "",
     "The title was vacant after Alekhine's death",
     "FIDE settled the succession with a five-player tournament in "
     "The Hague and Moscow in 1948", "", None),
    ("Mikhail Botvinnik", "Soviet Union", 1948, 1957, "first reign",
     "Won the 1948 championship tournament",
     "Lost to Smyslov in 1957", "1911-1995", "Mikhail Botvinnik"),
    ("Vasily Smyslov", "Soviet Union", 1957, 1958, "",
     "Beat Botvinnik in 1957",
     "Lost the rematch a year later", "1921-2010", "Vasily Smyslov"),
    ("Mikhail Botvinnik", "Soviet Union", 1958, 1960, "second reign",
     "Won the rematch allowed to a defeated champion",
     "Lost to Tal in 1960", "1911-1995", "Mikhail Botvinnik"),
    ("Mikhail Tal", "Soviet Union, Latvia", 1960, 1961, "",
     "Beat Botvinnik at twenty-three, the youngest champion to that date",
     "Lost the rematch a year later", "1936-1992", "Mikhail Tal"),
    ("Mikhail Botvinnik", "Soviet Union", 1961, 1963, "third reign",
     "Won the rematch against Tal",
     "Lost to Petrosian in 1963; the rematch clause had been abolished",
     "1911-1995", "Mikhail Botvinnik"),
    ("Tigran Petrosian", "Soviet Union, Armenia", 1963, 1969, "",
     "Beat Botvinnik in 1963",
     "Lost to Spassky in 1969, after defending against him in 1966",
     "1929-1984", "Tigran Petrosian"),
    ("Boris Spassky", "Soviet Union", 1969, 1972, "",
     "Beat Petrosian in 1969",
     "Lost to Fischer in Reykjavik in 1972", "1937-2025", "Boris Spassky"),
    ("Bobby Fischer", "United States", 1972, 1975, "",
     "Beat Spassky 12.5 to 8.5 in Reykjavik",
     "Forfeited the title in 1975 after refusing FIDE's match conditions",
     "1943-2008", "Bobby Fischer"),
    ("Anatoly Karpov", "Soviet Union", 1975, 1985, "",
     "Declared champion on Fischer's forfeit, the only title gained by default",
     "Lost to Kasparov in 1985; their first match had been terminated "
     "without result", "born 1951", "Anatoly Karpov"),
    ("Garry Kasparov", "Soviet Union, then Russia", 1985, 2000, "",
     "Beat Karpov at twenty-two, then the youngest champion",
     "Left FIDE in 1993 and kept the classical title; lost it to Kramnik "
     "in 2000", "born 1963", "Garry Kasparov"),
    ("Vladimir Kramnik", "Russia", 2000, 2007, "",
     "Beat Kasparov in London in 2000",
     "Reunified the title against Topalov in 2006, then lost it in the 2007 "
     "championship tournament", "born 1975", "Vladimir Kramnik"),
    ("Viswanathan Anand", "India", 2007, 2013, "",
     "Won the 2007 championship tournament in Mexico City",
     "Defended three times, then lost to Carlsen in 2013", "born 1969",
     "Viswanathan Anand"),
    ("Magnus Carlsen", "Norway", 2013, 2023, "",
     "Beat Anand in Chennai in 2013",
     "Declined to defend in 2023, undefeated in title matches", "born 1990",
     "Magnus Carlsen"),
    ("Ding Liren", "China", 2023, 2024, "",
     "Beat Nepomniachtchi in tiebreaks for the vacant title, the first "
     "Chinese champion",
     "Lost to Gukesh in Singapore in December 2024", "born 1992", "Ding Liren"),
    ("Gukesh Dommaraju", "India", 2024, None, "",
     "Beat Ding at eighteen, the youngest world champion",
     "Defends the title in Geneva at the end of 2026", "born 2006",
     "Gukesh Dommaraju"),
]

COLORS = {
    "Wilhelm Steinitz": "#8b93a7", "Emanuel Lasker": "#58a6ff",
    "José Raúl Capablanca": "#ffb02e", "Alexander Alekhine": "#ff5c4d",
    "Max Euwe": "#b48cf2", "Interregnum": "#4a4f5a",
    "Mikhail Botvinnik": "#31d67a", "Vasily Smyslov": "#2fc6a6",
    "Mikhail Tal": "#d1548e", "Tigran Petrosian": "#c9814b",
    "Boris Spassky": "#e6c86e", "Bobby Fischer": "#6ee7f2",
    "Anatoly Karpov": "#f28cb0", "Garry Kasparov": "#ff8a3d",
    "Vladimir Kramnik": "#7fd1ff", "Viswanathan Anand": "#9be564",
    "Magnus Carlsen": "#ffd75e", "Ding Liren": "#66d9c2",
    "Gukesh Dommaraju": "#ff6e7e",
}

ERAS = [
    (1886, 1946, "Matches arranged by the champion", "#8b93a7"),
    (1946, 1948, "Interregnum", "#4a4f5a"),
    (1948, 1993, "The FIDE cycle", "#58a6ff"),
    (1993, 2006, "Rival titles, classical line shown", "#ff8a3d"),
    (2006, 2028, "The reunified title", "#31d67a"),
]

SHORT = {"Wilhelm Steinitz": "Steinitz", "Emanuel Lasker": "Lasker",
         "José Raúl Capablanca": "Capablanca", "Alexander Alekhine": "Alekhine",
         "Max Euwe": "Euwe", "Interregnum": "Interregnum",
         "Mikhail Botvinnik": "Botvinnik", "Vasily Smyslov": "Smyslov",
         "Mikhail Tal": "Tal", "Tigran Petrosian": "Petrosian",
         "Boris Spassky": "Spassky", "Bobby Fischer": "Fischer",
         "Anatoly Karpov": "Karpov", "Garry Kasparov": "Kasparov",
         "Vladimir Kramnik": "Kramnik", "Viswanathan Anand": "Anand",
         "Magnus Carlsen": "Carlsen", "Ding Liren": "Ding",
         "Gukesh Dommaraju": "Gukesh"}

reigns_js = json.dumps(
    [{"n": n, "s": SHORT[n], "co": co, "a": a, "b": b if b else NOW,
      "open": b is None, "ord": o, "won": won, "lost": lost, "lived": lived,
      "w": wiki, "c": COLORS[n], "gap": wiki is None}
     for n, co, a, b, o, won, lost, lived, wiki in R],
    separators=(",", ":"), ensure_ascii=False)
eras_js = json.dumps(
    [{"a": a, "b": b, "n": n, "c": c} for a, b, n, c in ERAS],
    separators=(",", ":"), ensure_ascii=False)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>World Chess Champions · Altazor</title>
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
#portrait { width:100%; aspect-ratio:3/4; object-fit:contain; background:#101010;
  border-radius:6px; display:block; }
#chTxt { font-weight:700; margin:10px 0 2px; font-size:15px; }
#reignTxt { font-size:13px; min-height:1.2em; }
#livedTxt { color:var(--muted); font-size:13px; margin-top:2px; }
#wonTxt, #lostTxt { color:var(--muted); font-size:12.5px; margin-top:6px; line-height:1.45; }
.legend { display:flex; gap:14px; flex-wrap:wrap; margin-top:10px; font-size:12.5px; color:var(--muted); }
.legend span.sw { width:11px; height:11px; border-radius:3px; display:inline-block; margin-right:5px; }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.note a { color:var(--accent); }
@media (max-width:900px){ .stage{flex-direction:column;} .side{position:static; width:100%;}
  #portrait{max-width:200px; margin:0 auto;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="chess.html">&larr; Chess</a></nav>
</header>
<h1>World Chess Champions</h1>
<div class="controls">
  <button id="reset">Reset view</button>
  <span class="info" id="info"></span>
</div>
<div class="stage">
  <div id="tl"></div>
  <div class="side"><div class="card">
    <img id="portrait" alt="Champion portrait">
    <div id="chTxt">Hover a reign</div>
    <div id="reignTxt"></div>
    <div id="livedTxt"></div>
    <div id="wonTxt"></div>
    <div id="lostTxt"></div>
  </div></div>
</div>
<div class="legend" id="legend"></div>
<p class="note">Every world champion in the classical lineage, from Steinitz
to today, each reign drawn to its length. The wheel zooms, dragging pans, a
click on a band below the axis zooms into that period, and the reign under
the cursor fills the card.</p>
<p class="note">The 1886 match between Steinitz and Zukertort counts as the
first official championship. Alekhine died holding the title, and the 1948
five-player tournament settled the succession. Botvinnik's two returns came
through the rematch clause of his day, and Fischer forfeited in 1975 without
a move played.</p>
<p class="note">From 1993 to 2006 two rival titles existed after Kasparov
left FIDE. This page draws the classical line, reunified when Kramnik beat
the FIDE champion Topalov in 2006. Carlsen declined to defend in 2023. The
reigns can be checked against the
<a href="https://en.wikipedia.org/wiki/World_Chess_Championship">list of
world chess champions</a>, and the next match is set out in
<a href="https://www.fide.com/geneva-to-host-fide-world-championship-match-2026/">FIDE's
announcement</a>. Portraits load at view time from Wikipedia's public API for
identification and are not stored on this site.</p>
</div>
<script>
const REIGNS=__REIGNS__, ERAS=__ERAS__;
const W=980,H=560,CY=270,MINY=1882,MAXY=2030;
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
  s+=`<defs><pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse"
    patternTransform="rotate(45)"><rect width="7" height="7" fill="#1a1a1a"/>
    <line x1="0" y1="0" x2="0" y2="7" stroke="#4a4f5a" stroke-width="2"/></pattern></defs>`;
  for(const y of ticks()){
    const x=X(y);
    s+=`<line x1="${x}" y1="26" x2="${x}" y2="${H-26}" stroke="#242424"/>`;
    s+=`<text x="${x}" y="${CY+48}" text-anchor="middle" font-size="12.5" font-weight="700"
      fill="#9a9a9a">${y}</text>`;
  }
  ERAS.forEach((p,i)=>{
    if(p.b<view.a||p.a>view.b) return;
    const x0=Math.max(0,X(p.a)), x1=Math.min(W,X(p.b));
    s+=`<rect x="${x0}" y="${CY+58}" width="${Math.max(2,x1-x0)}" height="22" rx="6"
      fill="${p.c}22" stroke="${p.c}" stroke-width="1" data-era="${i}" style="cursor:pointer"/>`;
    if(x1-x0>190) s+=`<text x="${(x0+x1)/2}" y="${CY+73}" text-anchor="middle" font-size="11.5"
      fill="${p.c}" pointer-events="none">${esc(p.n)} (${p.a}-${p.b})</text>`;
  });
  // the reign bar
  const rs=REIGNS.map((r,i)=>({...r,ri:i}))
                 .filter(r=>r.b>=view.a&&r.a<=view.b);
  for(const r of rs){
    const x0=Math.max(-8,X(r.a)), x1=Math.min(W+8,X(r.b));
    const fill=r.gap?'url(#hatch)':r.c;
    const dash=r.open?' stroke-dasharray="5 4"':'';
    s+=`<rect x="${x0}" y="${CY-22}" width="${Math.max(1.5,x1-x0)}" height="44" rx="5"
      fill="${fill}" fill-opacity="${r.gap?1:0.82}" stroke="#121212" stroke-width="1.6"${dash}
      data-ch="${r.ri}" style="cursor:default"/>`;
  }
  // labels as pills above and below, alternating, collision-avoiding
  const ls=rs.map(r=>({...r}));
  ls.forEach((r,i)=>{
    const short=r.s;
    const yrs=`${r.a}-${r.open?'':r.b}`;
    r.label=`${short} ${yrs}`;
    const w=Math.min(200,(r.label.length)*6.6)+16;
    const mid=(Math.max(0,X(r.a))+Math.min(W,X(r.b)))/2;
    r.w=w; r.cx=Math.min(W-w/2-4,Math.max(w/2+4,mid)); r.mid=mid; r.up=(i%2===0);
  });
  const ups=ls.filter(r=>r.up), dns=ls.filter(r=>!r.up);
  lanes(ups,r=>r.w-14); lanes(dns,r=>r.w-14);
  for(const r of ls){
    const c=r.gap?'#6b7280':r.c;
    const ly=r.up ? CY-64-r.lane*26 : CY+104+r.lane*26;
    const tipY=r.up ? ly+9 : ly-9;
    const edgeY=r.up ? CY-22 : CY+22;
    s+=`<g data-ch="${r.ri}" style="cursor:default">
      <line x1="${r.mid}" y1="${edgeY}" x2="${r.mid}" y2="${tipY}" stroke="${c}" stroke-width="1.1" opacity="0.7"/>
      <rect x="${r.cx-r.w/2}" y="${ly-8}" width="${r.w}" height="20" rx="7"
        fill="#1a1a1a" stroke="${c}" stroke-width="1.1"/>
      <text x="${r.cx}" y="${ly+6}" text-anchor="middle" font-size="11.3" font-weight="600"
        fill="#e6e6e6" pointer-events="none">${esc(r.label)}</text></g>`;
  }
  s+='</svg>';
  el.innerHTML=s;
  document.getElementById('info').textContent=
    `${Math.round(view.a)} to ${Math.round(view.b)}`;
}
function clampView(a,b){
  const span=Math.min(MAXY-MINY,Math.max(4,b-a));
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
    const g=e.target.closest('[data-ch]');
    if(g){ showChamp(+g.getAttribute('data-ch')); return; }
    const b=e.target.closest('[data-era]');
    if(b){ const p=ERAS[+b.getAttribute('data-era')];
      document.getElementById('info').textContent=p.n+' ('+p.a+'-'+p.b+') \\u00b7 click to zoom'; }
  });
}

// ---- portrait panel: Wikipedia REST API ----
const cache={};
let current=-1;
async function portraitFor(r){
  if(!r.w) return null;
  if(r.w in cache) return cache[r.w];
  try{
    const q=await fetch('https://en.wikipedia.org/api/rest_v1/page/summary/'+
      encodeURIComponent(r.w.replace(/ /g,'_')));
    if(!q.ok) throw 0;
    const j=await q.json();
    const u=j.thumbnail?j.thumbnail.source:null;
    cache[r.w]=u; return u;
  }catch(e){ cache[r.w]=null; return null; }
}
async function showChamp(i){
  const r=REIGNS[i]; current=i;
  document.getElementById('chTxt').textContent=r.n;
  const rt=document.getElementById('reignTxt');
  rt.textContent=r.gap?'The title was vacant, 1946 to 1948'
    :`World Champion, ${r.a} to ${r.open?'today':r.b}`+(r.ord?` (${r.ord})`:'');
  rt.style.color=r.gap?'#9a9a9a':r.c;
  document.getElementById('livedTxt').textContent=
    r.gap?'':`${r.lived} \\u00b7 ${r.co}`;
  document.getElementById('wonTxt').textContent=r.won+'.';
  document.getElementById('lostTxt').textContent=r.lost+'.';
  const img=document.getElementById('portrait');
  img.removeAttribute('src'); img.alt=r.gap?'':'Loading portrait\\u2026';
  const u=await portraitFor(r);
  if(current!==i) return;
  if(u){ img.src=u; img.alt=`${r.n}`; }
  else { img.alt=r.gap?'No portrait: the title was vacant':'No portrait found'; }
}
document.getElementById('reset').onclick=()=>{view={a:MINY,b:MAXY};render();};
const seen=new Set();
document.getElementById('legend').innerHTML=REIGNS
  .filter(r=>!r.gap&&!seen.has(r.n)&&seen.add(r.n))
  .map(r=>`<span><span class="sw" style="background:${r.c}"></span>${esc(r.s)}</span>`)
  .join('');
render();
showChamp(REIGNS.length-1);
hook();
</script>
</body>
</html>
"""

html = HTML.replace("__REIGNS__", reigns_js).replace("__ERAS__", eras_js)
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} bytes): {len(R)} reigns, "
      f"{len(set(n for n,*_ in R))-1} champions")
