#!/usr/bin/env python3
"""Generate timeline.html, the interactive 50 Greatest Chess Games timeline.

Data below was extracted from Brian's Mathematica notebook (Chess Timeline.nb,
TimelinePlot source). Pre-1800 entries there were pinned to fake 1800 dates so
the plot would render; here they sit at their true years and the zoomable axis
handles the range.

Usage: python3 build_timeline.py
"""

from pathlib import Path

OUT = Path(__file__).parent.parent / "timeline.html"

PRE = [
    (900, "Shatranj Era (900-1400)", "era"),
    (950, "As-Suli vs Al-Lajlaj", "game"),
    (1475, "Castellvi vs Vinyoles", "game"),
    (1475, "Birth of Modern Chess (1475-1500)", "era"),
    (1623, "Greco vs NN", "game"),
    (1788, "Bowdler vs Conway", "game"),
]

GAMES = [
    (1834, "Labourdonnais vs McDonnell"), (1851, "The Immortal Game"),
    (1852, "The Evergreen Game"), (1858, "Morphy vs Allies (Opera Game)"),
    (1895, "Steinitz vs Von Bardeleben"), (1895, "Pillsbury vs Gunsberg"),
    (1904, "Lasker vs Napier"), (1907, "Rotlewi vs Rubinstein"),
    (1909, "Capablanca vs Marshall"), (1912, "Marshall vs Levitsky"),
    (1914, "Bernstein vs Capablanca"), (1920, "Adams vs Torre"),
    (1924, "Capablanca vs Tartakower"), (1925, "Réti vs Alekhine"),
    (1927, "Alekhine vs Capablanca Game 34"), (1934, "Canal vs Amateur"),
    (1935, "Botvinnik vs Chekhover"), (1938, "Botvinnik vs Capablanca"),
    (1953, "Reshevsky vs Petrosian"), (1956, "Byrne vs Fischer (Game of Century)"),
    (1960, "Tal vs Botvinnik Game 6"), (1966, "Petrosian vs Spassky"),
    (1972, "Fischer vs Spassky Game 6"), (1973, "Bronstein vs Ljubojevic"),
    (1974, "Karpov vs Unzicker"), (1984, "Karpov vs Kasparov Game 16"),
    (1985, "Kasparov vs Karpov Game 24"), (1991, "Short vs Timman"),
    (1991, "Ivanchuk vs Yusupov"), (1994, "Shirov vs Polgar"),
    (1997, "Kasparov vs Deep Blue Game 2"), (1998, "Topalov vs Shirov"),
    (1998, "Shirov vs Topalov"), (1999, "Kasparov vs Topalov"),
    (2000, "Kramnik vs Kasparov Game 2"), (2007, "Aronian vs Anand"),
    (2008, "Anand vs Kramnik Game 10"), (2013, "Carlsen vs Anand Game 6"),
    (2015, "Carlsen vs So"), (2015, "Wei Yi vs Bruzon Batista"),
    (2016, "Carlsen vs Karjakin Game 10"), (2018, "Dubov vs Karjakin"),
    (2021, "Carlsen vs Nepomniachtchi Game 6"), (2021, "Rapport vs Karjakin"),
    (2021, "Duda vs Carlsen"), (2023, "Ding vs Nepomniachtchi Game 12"),
    (2024, "Gukesh vs Ding (World Championship)"),
]

CHAMPIONS = [
    (1886, "Wilhelm Steinitz", "First Official Champion"),
    (1894, "Emanuel Lasker", ""), (1921, "José Raúl Capablanca", ""),
    (1927, "Alexander Alekhine", "First Reign"), (1935, "Max Euwe", ""),
    (1937, "Alexander Alekhine", "Second Reign"),
    (1948, "Mikhail Botvinnik", "First Reign"), (1957, "Vasily Smyslov", ""),
    (1958, "Mikhail Botvinnik", "Second Reign"), (1960, "Mikhail Tal", ""),
    (1961, "Mikhail Botvinnik", "Third Reign"), (1963, "Tigran Petrosian", ""),
    (1969, "Boris Spassky", ""), (1972, "Bobby Fischer", ""),
    (1975, "Anatoly Karpov", ""), (1985, "Garry Kasparov", ""),
    (2000, "Vladimir Kramnik", ""), (2007, "Viswanathan Anand", ""),
    (2013, "Magnus Carlsen", ""), (2023, "Ding Liren", ""),
    (2024, "Gukesh Dommaraju", "Youngest Champion"),
]

PERIODS = [
    (1820, 1880, "Romantic Period"), (1880, 1945, "Classical Period"),
    (1945, 1990, "Modern Period"), (1990, 2000, "Computer Era"),
    (2000, 2025, "Contemporary Era"),
]

THEMES = [
    (1850, 1880, "Golden Age of Tactics"), (1880, 1920, "Rise of Positional Play"),
    (1886, 2023, "World Championship Era"), (1990, 2010, "Computer Chess Revolution"),
]


def era_key(year):
    if year < 1800:
        return "early"
    if year < 1880:
        return "romantic"
    if year < 1945:
        return "classical"
    if year < 1990:
        return "modern"
    return "contemporary"


import json

games_js = json.dumps([{"y": y, "n": n, "e": era_key(y)} for y, n in GAMES],
                      separators=(",", ":"))
pre_js = json.dumps([{"y": y, "n": n, "k": k} for y, n, k in PRE],
                    separators=(",", ":"))
champs_js = json.dumps([{"y": y, "n": n, "s": s} for y, n, s in CHAMPIONS],
                       separators=(",", ":"))
periods_js = json.dumps([{"a": a, "b": b, "n": n} for a, b, n in PERIODS],
                        separators=(",", ":"))
themes_js = json.dumps([{"a": a, "b": b, "n": n} for a, b, n in THEMES],
                       separators=(",", ":"))

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>50 Greatest Games · Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
.wrap { max-width:1250px; margin:0 auto; padding:32px 20px 60px; }
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
#tl { width:100%; }
#tl svg { width:100%; height:auto; display:block; cursor:grab; user-select:none; }
#tl.panning, #tl.panning * { cursor:grabbing !important; }
.legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:10px; font-size:13px; color:var(--muted); }
.legend span.sw { width:11px; height:11px; border-radius:3px; display:inline-block; margin-right:6px; }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="chess.html">&larr; Chess</a></nav>
</header>
<h1>50 Greatest Games</h1>
<div class="controls">
  <button id="reset">Reset view</button>
  <span class="info" id="info"></span>
</div>
<div id="tl"></div>
<div class="legend" id="legend"></div>
<p class="note">The fifty games worth knowing, the world champions, and the eras
they belong to, from As-Suli in 950 to Gukesh in 2024. The wheel or a pinch zooms,
dragging pans, a click on an era band zooms into it, and anything under the
cursor shows its details.</p>
<p class="note">Games are placed at the year they were played and colored by
era; champions sit below the axis at the start of each reign. The game list is
a personal selection. The axis starts at 1800; the medieval and early games
live in the Before 1800 box so a thousand mostly empty years do not stretch
the canvas.</p>
</div>
<script>
const GAMES=__GAMES__, CHAMPS=__CHAMPS__, PERIODS=__PERIODS__, THEMES=__THEMES__, PRE=__PRE__;
const ERAC={early:'#8b93a7',romantic:'#31d67a',classical:'#ff5c4d',
            modern:'#b48cf2',contemporary:'#ffb02e'};
const ERAN={early:'Pre-1800',romantic:'Romantic (1820-1880)',
            classical:'Classical (1880-1945)',modern:'Modern (1945-1990)',
            contemporary:'Contemporary (1990-2025)'};
const CHAMPC='#d1548e';
const W=1250,H=1000,CY=630,MINY=1800,MAXY=2030;
let view={a:1800,b:2030};

const el=document.getElementById('tl');
const X=y=>(y-view.a)/(view.b-view.a)*W;
const YR=x=>view.a+x/W*(view.b-view.a);
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');

function ticks(){
  const span=view.b-view.a;
  const step=span>700?100:span>250?50:span>120?20:span>50?10:span>25?5:1;
  const out=[];
  for(let y=Math.ceil(view.a/step)*step;y<=view.b;y+=step) out.push(y);
  return out;
}
function lanes(items,estw){
  // greedy stacking: items sorted by x, place in first free lane
  const ends=[];
  for(const it of items){
    const w=estw(it), x0=it.x-w/2;
    let l=0;
    while(l<ends.length && ends[l]>x0) l++;
    it.lane=l; ends[l]=it.x+w/2+8;
  }
  return ends.length;
}
function render(){
  let s=`<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" id="tlsvg">`;
  s+=`<rect width="${W}" height="${H}" fill="#121212"/>`;
  // grid + axis
  for(const y of ticks()){
    const x=X(y);
    s+=`<line x1="${x}" y1="30" x2="${x}" y2="${H-24}" stroke="#242424"/>`;
    s+=`<text x="${x}" y="${CY+20}" text-anchor="middle" font-size="13" font-weight="700"
      fill="#9a9a9a">${y}</text>`;
  }
  s+=`<line x1="0" y1="${CY}" x2="${W}" y2="${CY}" stroke="#3a3a3a" stroke-width="2"/>`;
  // period bands (clickable), just below the year labels
  PERIODS.forEach((p,i)=>{
    if(p.b<view.a||p.a>view.b) return;
    const x0=Math.max(0,X(p.a)), x1=Math.min(W,X(p.b));
    s+=`<rect x="${x0}" y="${CY+30}" width="${Math.max(2,x1-x0)}" height="20" rx="6"
      fill="rgba(88,166,255,0.13)" stroke="#58a6ff" stroke-width="1" data-per="${i}" style="cursor:pointer"/>`;
    if(x1-x0>90) s+=`<text x="${(x0+x1)/2}" y="${CY+44}" text-anchor="middle" font-size="11.5"
      fill="#58a6ff" pointer-events="none">${esc(p.n)}</text>`;
  });
  THEMES.forEach((t,i)=>{
    if(t.b<view.a||t.a>view.b) return;
    const x0=Math.max(0,X(t.a)), x1=Math.min(W,X(t.b));
    s+=`<rect x="${x0}" y="${CY+56}" width="${Math.max(2,x1-x0)}" height="14" rx="6"
      fill="rgba(255,176,46,0.10)" stroke="#8a6a1f" stroke-width="1" data-th="${i}"/>`;
    if(x1-x0>120) s+=`<text x="${(x0+x1)/2}" y="${CY+67}" text-anchor="middle" font-size="10.5"
      fill="#c9a04b" pointer-events="none">${esc(t.n)}</text>`;
  });
  // games above the axis
  const gs=GAMES.filter(g=>g.y>=view.a-40&&g.y<=view.b+40)
                .map((g,i)=>({...g,x:X(g.y),gi:GAMES.indexOf(g)}))
                .sort((a,b)=>a.x-b.x);
  gs.forEach(g=>{const w=Math.min(230,(g.n.length+7)*6.4)+14;
    g.cx=Math.min(W-w/2-4,Math.max(w/2+4,g.x));});
  lanes(gs.map(g=>({...g,x:g.cx,ref:g})).map(o=>(o.ref.laneSrc=o,o)),g=>Math.min(230,(g.n.length+7)*6.4));
  gs.forEach(g=>g.lane=g.laneSrc.lane);
  for(const g of gs){
    const ly=CY-46-g.lane*27, c=ERAC[g.e];
    s+=`<line x1="${g.x}" y1="${CY-4}" x2="${g.x}" y2="${ly+9}" stroke="${c}" stroke-width="1.2" opacity="0.75"/>`;
    s+=`<circle cx="${g.x}" cy="${CY-6}" r="3.4" fill="${c}"/>`;
    const label=`${g.n} (${g.y})`, w=Math.min(230,(label.length)*6.4)+14;
    const cx=g.cx;
    s+=`<g data-g="${g.gi}" style="cursor:default">
      <rect x="${cx-w/2}" y="${ly-8}" width="${w}" height="21" rx="7"
        fill="#1a1a1a" stroke="${c}" stroke-width="1.2"/>
      <text x="${cx}" y="${ly+7}" text-anchor="middle" font-size="11.8" font-weight="600"
        fill="#e6e6e6" pointer-events="none">${esc(label).slice(0,42)}</text></g>`;
  }
  // champions below the bands
  const cs=CHAMPS.filter(c=>c.y>=view.a-40&&c.y<=view.b+40)
                 .map(c=>({...c,x:X(c.y),ci:CHAMPS.indexOf(c)}))
                 .sort((a,b)=>a.x-b.x);
  cs.forEach(c=>{const w=Math.min(215,(c.n.length+8)*6.4)+14;
    c.cx=Math.min(W-w/2-4,Math.max(w/2+4,c.x));});
  lanes(cs.map(c=>({...c,x:c.cx,ref:c})).map(o=>(o.ref.laneSrc=o,o)),c=>Math.min(215,(c.n.length+8)*6.4));
  cs.forEach(c=>c.lane=c.laneSrc.lane);
  for(const c of cs){
    const ly=CY+96+c.lane*27;
    s+=`<line x1="${c.x}" y1="${CY+74}" x2="${c.x}" y2="${ly-8}" stroke="${CHAMPC}" stroke-width="1.2" opacity="0.75"/>`;
    s+=`<circle cx="${c.x}" cy="${CY+76}" r="3.4" fill="${CHAMPC}"/>`;
    const label=`\\u2654 ${c.n} (${c.y})`, w=Math.min(215,label.length*6.4)+14;
    const cx=c.cx;
    s+=`<g data-c="${c.ci}" style="cursor:default">
      <rect x="${cx-w/2}" y="${ly-8}" width="${w}" height="21" rx="7"
        fill="#1a1a1a" stroke="${CHAMPC}" stroke-width="1.2"/>
      <text x="${cx}" y="${ly+7}" text-anchor="middle" font-size="11.8" font-weight="600"
        fill="#e6e6e6" pointer-events="none">${esc(label)}</text></g>`;
  }
  if(view.a<=1815){
    const bw=252, bx=14, by=44, rh=24;
    s+=`<rect x="${bx}" y="${by}" width="${bw}" height="${34+PRE.length*rh}" rx="10"
      fill="#1a1a1a" stroke="#2b2b2b"/>`;
    s+=`<text x="${bx+12}" y="${by+22}" font-size="12.5" font-weight="700" letter-spacing="1"
      fill="#8b93a7">\u23EA BEFORE 1800</text>`;
    PRE.forEach((e,i)=>{
      const ry=by+40+i*rh;
      s+=`<g data-pre="${i}" style="cursor:default">
        <rect x="${bx+6}" y="${ry-13}" width="${bw-12}" height="${rh-4}" rx="6" fill="transparent"/>
        <circle cx="${bx+16}" cy="${ry-2}" r="3" fill="${e.k==='era'?'#58a6ff':'#8b93a7'}"/>
        <text x="${bx+28}" y="${ry+2}" font-size="11.8" fill="${e.k==='era'?'#9db8d8':'#c9c9c9'}">${e.n.includes('(')?esc(e.n):esc(e.n)+' ('+e.y+')'}</text></g>`;
    });
    // break marks between the box and the axis start
    s+=`<text x="${bx+10}" y="${CY+4}" font-size="15" fill="#5a5a5a">\u2248\u2248</text>`;
  }
  s+='</svg>';
  el.innerHTML=s;
  document.getElementById('info').textContent=
    `${Math.round(view.a)} to ${Math.round(view.b)}`;
}
function clampView(a,b){
  const span=Math.min(MAXY-MINY,Math.max(8,b-a));
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
    const g=e.target.closest('[data-per]');
    if(g){const p=PERIODS[+g.getAttribute('data-per')];
      view=clampView(p.a-3,p.b+3);render();}
  });
  const tip=(name,year,extra)=>{
    document.getElementById('info').textContent=`${name} (${year})${extra?' \\u00b7 '+extra:''}`;
  };
  el.addEventListener('pointerover',e=>{
    const gg=e.target.closest('[data-g]');
    if(gg){const g=GAMES[+gg.getAttribute('data-g')];tip(g.n,g.y,ERAN[g.e]);return;}
    const cc=e.target.closest('[data-c]');
    if(cc){const c=CHAMPS[+cc.getAttribute('data-c')];
      tip('\\u2654 '+c.n,c.y,c.s||'World Champion');return;}
    const pp=e.target.closest('[data-pre]');
    if(pp){const q=PRE[+pp.getAttribute('data-pre')];
      tip(q.n,q.y,q.k==='era'?'Early era':'Early game');return;}
  });
}
document.getElementById('reset').onclick=()=>{view={a:1800,b:2030};render();};
const lg=document.getElementById('legend');
lg.innerHTML=Object.keys(ERAC).map(k=>
  `<span><span class="sw" style="background:${ERAC[k]}"></span>${ERAN[k]}</span>`).join('')+
  `<span><span class="sw" style="background:${CHAMPC}"></span>World Champions</span>`;
render();
hook();
</script>
</body>
</html>
"""

html = (HTML.replace("__GAMES__", games_js).replace("__CHAMPS__", champs_js)
        .replace("__PERIODS__", periods_js).replace("__THEMES__", themes_js).replace("__PRE__", pre_js))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html)} bytes): {len(GAMES)} games, "
      f"{len(CHAMPIONS)} champions, {len(PERIODS)} periods, {len(THEMES)} themes")
