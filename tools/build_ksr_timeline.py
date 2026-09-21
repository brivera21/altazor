#!/usr/bin/env python3
"""Builds ksr-2312-timeline.html: three futures on one axis.

The page draws Charlotte Shortback's periodization from 2312 as the spine,
with the Mars trilogy and New York 2140 on tracks of their own beneath it.
It never merges them, because Robinson says they are not one continuity,
and the page says so where a reader will see it.
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import apa
from ksr_timeline_data import (PERIODS, AFTER, EVENTS_2312, QUBES, MARS, NY,
                               CONFLICTS)

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "ksr-2312-timeline.html"

T0, T1 = 2000, 2330

BAND = ["#7a5c2e", "#8f4b3a", "#3f6b52", "#2f5d80", "#4a4a7a", "#7a3f62"]


def payload():
    return {
        "t0": T0, "t1": T1,
        "periods": [dict(a=a, b=b, k=k, n=n, g=g, s=s, c=BAND[i])
                    for i, (a, b, k, n, g, s) in enumerate(PERIODS)],
        "events": [dict(a=a, b=b, k=k, n=n, g=g, s=s) for a, b, k, n, g, s in EVENTS_2312],
        "qubes": [dict(a=a, b=b, n=n, g=g, s=s) for a, b, n, g, s in QUBES],
        "mars": [dict(a=a, b=b, n=n, g=g, s=s, d=d) for a, b, n, g, s, d in MARS],
        "ny": [dict(a=a, b=b, n=n, g=g, s=s, d=d) for a, b, n, g, s, d in NY],
        "conflicts": [dict(n=n, g=g) for n, g in CONFLICTS],
        "after": {"g": AFTER[0], "s": AFTER[1]},
    }


REFS = apa.render([
    (apa.book("Robinson, K. S.", 2012, "2312", "Orbit"),
     "Charlotte Shortback's periodization, pages 255 to 257; the first space "
     "elevator at Quito, page 134; sea level at eleven meters, page 100; "
     "Pauline among the first qubes, page 58. Read through the Internet "
     "Archive's full text search of the scanned Orbit edition."),
    (apa.web("Liptak, A.", 2020,
             "Kim Stanley Robinson on climate change and The Ministry for the Future",
             "Reactor",
             "https://reactormag.com/kim-stanley-robinson-the-ministry-for-the-future-climate-change-interview/"),
     "Robinson saying the books are not from the same future history, which is "
     "why this page draws them apart."),
    (apa.book("Robinson, K. S.", 1992, "Red Mars", "Bantam Spectra"),
     "With <i>Green Mars</i> (1993) and <i>Blue Mars</i> (1996), the second track."),
    (apa.book("Robinson, K. S.", 2017, "New York 2140", "Orbit"),
     "The third track."),
    (apa.web("KimStanleyRobinson.info", None, "Mars trilogy timeline", None,
             "https://www.kimstanleyrobinson.info/content/mars-trilogy-timeline",
             retrieved=True),
     "Most of the Mars dates. A fan reference, and it contradicts itself on "
     "several of them, which is why the disputed ones are drawn as disputed."),
    (apa.wiki("https://en.wikipedia.org/wiki/Mars_trilogy"),
     "Cross check on the 2026, 2061, 2127 and 2212 dates."),
    (apa.web("Sherwood, S., & Vicars, K.", 2017,
             "New York 2140: a novelist's vision of a drowned city that still never sleeps",
             "The Conversation",
             "https://theconversation.com/new-york-2140-a-novelists-vision-of-a-drowned-city-that-still-never-sleeps-73718"),
     "The two Pulses and their sea level figures, written by climate scientists."),
    (apa.web("Robinson, K. S.", 2017, "Making it in a futuristic flooded New York",
             "Science Friday", "https://www.sciencefriday.com/articles/making-it-in-a-futuristic-flooded-new-york/"),
     "An authorized excerpt: each Pulse a decade, and the drowned line at "
     "about Fortieth Street."),
])

METHOD = ("The 2312 dates are the novel's own, quoted by page from the Orbit "
          "edition. The Mars and New York dates come from secondary sources, "
          "which is weaker, and where those sources disagree the entry is "
          "drawn with a dashed edge and says so rather than picking a winner. "
          "Three of them disagree: the Dorsa Brevia conference, the Great "
          "Flood, and the years of the Second Pulse. The three books are kept "
          "on separate tracks because Robinson has said they are not one "
          "future history.")

CSS = """
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; --mars:#6fbf73; --ny:#58a6ff;
        --book:#ffb02e; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
.wrap { max-width:1320px; margin:0 auto; padding:32px 20px 60px; }
header.site { border-top:4px solid var(--accent); padding-top:22px; margin-bottom:26px;
  display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }
.brand { font-weight:700; font-size:20px; letter-spacing:.1em; text-decoration:none; color:var(--text); }
.brand:hover { color:var(--accent); }
nav.site a { color:var(--muted); text-decoration:none; font-size:14px; margin-right:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 6px; font-size:26px; }
.sub { color:var(--muted); margin:0 0 16px; font-size:15px; }
.bar { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-bottom:12px; }
button { font:inherit; font-size:13.5px; padding:6px 14px; border-radius:999px;
  border:1px solid var(--line); background:#1a1a1a; color:var(--text); cursor:pointer; }
button:hover { border-color:var(--accent); }
button.on { background:var(--accent); border-color:var(--accent); color:#0b1a2b; font-weight:600; }
.stage { display:grid; grid-template-columns:minmax(0,1fr) 330px; gap:22px; align-items:start; }
@media (max-width:1000px){ .stage { grid-template-columns:1fr; } }
#diagram > svg { width:100%; height:auto; display:block; background:#0d0d0d;
  border:1px solid #333; border-radius:6px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:16px 18px; }
#kindTxt { color:var(--muted); font-size:12px; letter-spacing:.08em; text-transform:uppercase; }
#nameTxt { font-size:19px; font-weight:650; margin:4px 0 2px; }
#numTxt { color:var(--book); font-size:14px; margin-bottom:10px; }
#bodyTxt { font-size:14.5px; color:#d4d4d4; }
#srcTxt { color:var(--muted); font-size:12px; margin-top:12px; border-top:1px solid var(--line); padding-top:8px; }
.legend { display:flex; gap:16px; flex-wrap:wrap; color:var(--muted); font-size:12.5px; margin:10px 0 14px; }
.legend i { display:inline-block; width:22px; height:9px; border-radius:2px; margin-right:6px; vertical-align:middle; }
.note { color:#c9c9c9; font-size:15px; max-width:70ch; }
.method, .refs { color:var(--muted); font-size:13.5px; max-width:78ch; }
.method { border-top:1px solid var(--line); margin-top:34px; padding-top:14px; }
.refh { font-size:14px; color:var(--muted); margin:26px 0 8px; letter-spacing:.06em; text-transform:uppercase; }
hr.sep { border:0; border-top:1px solid var(--line); margin:30px 0 18px; }
__APACSS__
[hidden] { display:none !important; }
"""

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Centuries Before 2312 &middot; Altazor</title>
<style>__CSS__</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site">
    <a href="science-fiction.html">&larr; Science Fiction</a>
    <a href="solar-system-2312.html">The Solar System of 2312</a>
    <a href="red-mars.html">The Mars of Red Mars</a>
  </nav>
</header>

<h1>The Centuries Before 2312</h1>
<p class="sub">Three futures Robinson wrote for the same three hundred years.</p>

<div class="bar" id="views">
  <button data-v="all" class="on">The three books</button>
  <button data-v="periods">Shortback's periods</button>
  <button data-v="qubes">The qube thread</button>
  <button data-v="clash">Where they disagree</button>
</div>

<div class="legend" id="legend"></div>

<div class="stage">
  <div id="diagram"></div>
  <div class="side">
    <div class="card">
      <div id="kindTxt"></div>
      <div id="nameTxt"></div>
      <div id="numTxt"></div>
      <div id="bodyTxt"></div>
      <div id="srcTxt"></div>
    </div>
  </div>
</div>

<hr class="sep">
<p class="note">Charlotte Shortback is a historian inside 2312 who cuts the
long postmodern into six named stretches, from the Dithering to the
Balkanization. Her scheme is the top track. The Mars trilogy and New York 2140
run beneath it on the same axis.</p>
<p class="note">Robinson says the three are not one future history. They are
kept apart here for that reason, and the places where their numbers contradict
each other are drawn rather than smoothed.</p>

<div class="method"><p>__METHOD__</p></div>
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</div>
<script>
const D = __DATA__;
__SCRIPT__
</script>
</body>
</html>
"""

SCRIPT = r"""
const W=1120, M={l:20,r:20,t:26,b:34};
const IW=W-M.l-M.r;
const x = y => M.l + (y-D.t0)/(D.t1-D.t0)*IW;
const esc = s => String(s).replace(/[&<>]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
let view='all', sel=null;

function card(kind,name,num,body,src){
  document.getElementById('kindTxt').textContent=kind||'';
  document.getElementById('nameTxt').textContent=name||'';
  document.getElementById('numTxt').textContent=num||'';
  document.getElementById('bodyTxt').textContent=body||'';
  document.getElementById('srcTxt').textContent=src?('Source: '+src):'';
}
const span = (a,b) => b? (a+' to '+b) : String(a);

function axis(yy){
  let s='';
  for(let y=2000;y<=D.t1;y+=20){
    const X=x(y), major=(y%100===0);
    s+='<line x1="'+X+'" y1="'+(yy-5)+'" x2="'+X+'" y2="'+(yy+(major?7:3))+'" stroke="'+(major?'#666':'#3a3a3a')+'"/>';
    if(y%40===0) s+='<text x="'+X+'" y="'+(yy+22)+'" text-anchor="middle" font-size="11" fill="#7c7c7c">'+y+'</text>';
  }
  s+='<line x1="'+M.l+'" y1="'+yy+'" x2="'+(W-M.r)+'" y2="'+yy+'" stroke="#3a3a3a"/>';
  return s;
}

function band(o,yy,h,fill,id,dash){
  const X=x(o.a), X2=x(o.b||o.a), w=Math.max(X2-X,3);
  const on = sel===id;
  let s='<g class="hit" data-id="'+id+'" style="cursor:pointer">';
  s+='<rect x="'+X+'" y="'+yy+'" width="'+w+'" height="'+h+'" rx="3" fill="'+fill+'"'
   + ' stroke="'+(on?'#fff':'rgba(255,255,255,.22)')+'" stroke-width="'+(on?2:1)+'"'
   + (dash?' stroke-dasharray="5 3"':'')+'/>';
  if(w>62) s+='<text x="'+(X+7)+'" y="'+(yy+h/2+4)+'" font-size="11.5" fill="#f0f0f0">'+esc(o.n)+'</text>';
  s+='</g>';
  return s;
}

function mark(o,yy,color,id,dash){
  const X=x(o.a), on=sel===id;
  let s='<g class="hit" data-id="'+id+'" style="cursor:pointer">';
  if(o.b){ const w=Math.max(x(o.b)-X,3);
    s+='<rect x="'+X+'" y="'+(yy-5)+'" width="'+w+'" height="10" rx="2" fill="'+color+'" opacity="'+(on?1:.75)+'"'
     +(dash?' stroke="'+color+'" stroke-dasharray="4 3" fill-opacity=".3"':'')+'/>';
  } else {
    s+='<circle cx="'+X+'" cy="'+yy+'" r="'+(on?6:4.5)+'" fill="'+color+'"'
     +(dash?' stroke="#0d0d0d" stroke-width="1.5"':'')+'/>';
  }
  s+='<rect x="'+(X-9)+'" y="'+(yy-11)+'" width="18" height="22" fill="transparent"/></g>';
  return s;
}

function draw(){
  let s='<svg viewBox="0 0 '+W+' '+height()+'" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Three Robinson futures on one time axis">';
  let y=M.t;

  if(view==='clash'){
    s+='<text x="'+M.l+'" y="'+(y+2)+'" font-size="12.5" fill="#9a9a9a">Three points where the books cannot both be right</text>';
    y+=26;
    D.conflicts.forEach((c,i)=>{
      const on=sel===('clash'+i);
      s+='<g class="hit" data-id="clash'+i+'" style="cursor:pointer">';
      s+='<rect x="'+M.l+'" y="'+y+'" width="'+IW+'" height="44" rx="5" fill="'+(on?'#23262b':'#17191d')+'" stroke="'+(on?'#fff':'#333')+'"/>';
      s+='<text x="'+(M.l+14)+'" y="'+(y+27)+'" font-size="14" fill="#e6e6e6">'+esc(c.n)+'</text></g>';
      y+=54;
    });
    y+=6;
  }

  if(view==='all'||view==='periods'||view==='clash'){
    s+='<text x="'+M.l+'" y="'+(y+2)+'" font-size="12.5" fill="#ffb02e">2312</text>';
    y+=10;
    const h = (view==='periods')?52:30;
    D.periods.forEach(p=>{ s+=band(p,y,h,p.c,'p:'+p.k,false); });
    y+=h+8;
    if(view==='periods'){
      D.events.forEach(e=>{ s+=mark(e,y+6,'#ffb02e','e:'+e.k,false); });
      y+=22;
    }
  }

  if(view==='qubes'){
    s+='<text x="'+M.l+'" y="'+(y+2)+'" font-size="12.5" fill="#9a9a9a">The six periods, with the qube entries lit</text>';
    y+=12;
    D.periods.forEach(p=>{
      const lit = D.qubes.some(q=>q.a===p.a);
      s+=band(p,y,34, lit?p.c:'#1d1d1d','p:'+p.k,false);
    });
    y+=50;
    s+='<text x="'+M.l+'" y="'+(y+6)+'" font-size="12.5" fill="#ffb02e">What the book says about qubes, in order</text>';
    D.qubes.forEach((q,i)=>{ s+=band(q,y+16,26,'#6b5326','q:'+i,false); });
    y+=50;
  }

  if(view==='all'){
    s+='<text x="'+M.l+'" y="'+(y+12)+'" font-size="12.5" fill="#6fbf73">Mars trilogy</text>';
    y+=22;
    D.mars.forEach((m,i)=>{ s+=mark(m,y,'#6fbf73','m:'+i,m.d); });
    y+=26;
    s+='<text x="'+M.l+'" y="'+(y+8)+'" font-size="12.5" fill="#58a6ff">New York 2140</text>';
    y+=20;
    D.ny.forEach((n,i)=>{ s+=mark(n,y,'#58a6ff','n:'+i,n.d); });
    y+=24;
  }

  s+=axis(y+6);
  return s+'</svg>';
}

function height(){
  if(view==='clash') return 330;
  if(view==='periods') return 170;
  if(view==='qubes') return 210;
  return 230;
}

function find(id){
  const [t,k]=[id.slice(0,id.indexOf(':')), id.slice(id.indexOf(':')+1)];
  if(id.startsWith('clash')) return ['Disagreement', D.conflicts[+id.slice(5)], null];
  if(t==='p'){ const o=D.periods.find(p=>p.k===k); return ['Period · 2312', o, o]; }
  if(t==='e'){ const o=D.events.find(p=>p.k===k); return ['Event · 2312', o, o]; }
  if(t==='q'){ const o=D.qubes[+k]; return ['Qubes · 2312', o, o]; }
  if(t==='m'){ const o=D.mars[+k]; return ['Mars trilogy', o, o]; }
  if(t==='n'){ const o=D.ny[+k]; return ['New York 2140', o, o]; }
  return [null,null,null];
}

function show(id){
  sel=id;
  if(!id){ intro(); render(); return; }
  const [kind,o] = find(id);
  if(!o){ intro(); render(); return; }
  if(id.startsWith('clash')) card(kind, o.n, '', o.g, '');
  else card(kind, o.n, span(o.a,o.b), o.g + (o.d?'  The sources disagree about this date.':''), o.s);
  render();
}

function intro(){
  if(view==='clash') card('Three books','Where they disagree','','Robinson has said these are not one future history. Each row below is a place where reading them as one breaks something.','');
  else if(view==='qubes') card('2312','The qube thread','2130 to 2320','Strong AI arrives in the Turnaround, in a list with fusion power and self replicating factories. A hundred and forty years later the Balkanization names qubes among its causes.','2312, pp. 255, 256');
  else if(view==='periods') card('2312','Shortback’s periods','2005 to 2320', D.after.g, D.after.s);
  else card('Three books','The same three centuries','2000 to 2320','Charlotte Shortback’s six periods on top, the Mars trilogy and New York 2140 beneath. Every band and mark carries the source its date came from.','');
}

function render(){
  document.getElementById('diagram').innerHTML=draw();
  const L=[['#ffb02e','2312'],['#6fbf73','Mars trilogy'],['#58a6ff','New York 2140']];
  document.getElementById('legend').innerHTML =
    L.map(([c,n])=>'<span><i style="background:'+c+'"></i>'+n+'</span>').join('')
    + '<span><i style="background:transparent;border:1px dashed #888"></i>sources disagree</span>';
  for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on', b.dataset.v===view);
}

document.getElementById('diagram').addEventListener('click', ev=>{
  const g=ev.target.closest('.hit');
  if(g) show(g.dataset.id);
});
document.getElementById('views').addEventListener('click', ev=>{
  const b=ev.target.closest('button'); if(!b) return;
  view=b.dataset.v; sel=null; intro(); render();
});

window.__ksr = function(q){
  q=q||{};
  if(q.view){ view=q.view; sel=null; intro(); render(); }
  if(q.pick){ show(q.pick); }
  return {view, sel,
    periods: D.periods.length, mars: D.mars.length, ny: D.ny.length,
    qubes: D.qubes.length, conflicts: D.conflicts.length,
    bands: document.querySelectorAll('#diagram .hit').length,
    name: document.getElementById('nameTxt').textContent,
    num: document.getElementById('numTxt').textContent,
    body: document.getElementById('bodyTxt').textContent,
    src: document.getElementById('srcTxt').textContent,
    svgH: height()};
};

intro(); render();
"""


def main():
    css = CSS.replace("__APACSS__", apa.CSS)
    html = (HTML.replace("__CSS__", css)
                .replace("__DATA__", json.dumps(payload(), ensure_ascii=False))
                .replace("__SCRIPT__", SCRIPT)
                .replace("__METHOD__", METHOD)
                .replace("__REFS__", REFS))
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT.name} ({len(html):,} B): {len(PERIODS)} periods, "
          f"{len(MARS)} Mars entries, {len(NY)} New York entries, "
          f"{len(CONFLICTS)} conflicts")


if __name__ == "__main__":
    main()
