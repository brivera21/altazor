#!/usr/bin/env python3
"""Generate planet-earth-species.html, the species of Planet Earth (2006).

Three views. The map: one mark for every appearance, 137 of them, placed
where the episode filmed it, colored and shaped by group, filled for a
species and open for anything broader. The episodes: eleven panels, each
listing what it filmed. The repeats: the fourteen taxa that appear in
more than one episode, which is the only thread the series leaves
between them.

Data: tools/data/planet-earth-species.json, built by
build_planet_earth_json.py from Brian's table and enriched by
enrich_planet_earth.py. The coastline raster is the one the Earth pages
share, in tools/data/plates.json.

Usage: python3 build_planet_earth.py
"""

import json
from collections import Counter
from pathlib import Path

import apa

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "planet-earth-species.html"
DATA = json.loads((ROOT / "tools" / "data" / "planet-earth-species.json").read_text())
GEO = json.loads((ROOT / "tools" / "data" / "plates.json").read_text())

ROWS = DATA["rows"]
EPS = DATA["episodes"]

GROUPS = [
    ("mammal", "mammals", "#f2a03d", "circle"),
    ("bird", "birds", "#6fb2f0", "triangle"),
    ("fish", "fish", "#35b8a8", "diamond"),
    ("reptile", "reptiles", "#a8d84a", "square"),
    ("amphibian", "amphibians", "#8f7bf0", "rounded"),
    ("invertebrate", "invertebrates", "#ef7fa8", "hexagon"),
    ("plant", "plants", "#4f9d5d", "leaf"),
    ("fungus", "fungi", "#f5e050", "cap"),
    ("bacteria", "bacteria", "#9a9a9a", "dots"),
]

NOTE1 = ("Every animal, plant, fungus and bacterium named in the eleven episodes "
         "of Planet Earth, one mark for each appearance: 137 marks over 121 "
         "taxa. Color and shape give the group. A solid mark is a species or a "
         "subspecies, an open one something broader, a genus or a family, or "
         "one of the three that are not taxa. A soft halo means the episode "
         "named a region rather than a place, so the mark is a centroid.")

NOTE2 = ("Fourteen taxa turn up in more than one episode, and two of them, the "
         "wolf and the African bush elephant, in three. Those repeats are the "
         "only structure the series itself leaves behind linking one episode "
         "to another, and the third view is made of them.")

METHOD = ("The episodes are numbered as the BBC broadcast them, which is how IMDb, "
          "Metacritic and TV Guide list them too. Some streaming apps move three: "
          "Seasonal Forests to 8, Jungles to 9 and Shallow Seas to 10. Every "
          "episode panel and every card gives both numbers. "
          "Coordinates follow the filming location rather than the animal's range. "
          "Thirty-seven rows name a place a pin can sit on; the other hundred name "
          "a region, a biome or a habitat, and there the mark is a representative "
          "centroid, with the card saying which one was chosen and why. Every pin "
          "was checked against the coastline raster the Earth pages share, so that "
          "nothing marine sits on dry land. "
          "Conservation status is set only where a row resolves to a species or a "
          "subspecies: a genus or a family has no Red List category, and none is "
          "guessed from a member species. Where the Red List assesses an animal "
          "under a name the series did not use, or covers a subspecies only "
          "through its parent species, the card says so.")

REFS = [
    (apa.web("British Broadcasting Corporation", 2006,
             "Planet Earth [Television series]", "BBC Natural History Unit",
             "https://www.bbc.co.uk/programmes/b006mywy"),
     "The eleven episodes. The species, the names and the filming locations are "
     "Brian Rivera's own record of them."),
    (apa.web("International Union for Conservation of Nature", 2026,
             "The IUCN Red List of Threatened Species (Version 2026-1)", None,
             "https://www.iucnredlist.org"),
     "The conservation status of every row that resolves to a species or a "
     "subspecies, checked September 19, 2026."),
    (apa.data("International Union for Conservation of Nature", 2026,
              "The IUCN Red List of Threatened Species", None, "GBIF",
              "https://www.gbif.org/dataset/19491596-35ae-4a91-9a98-85cf505f1bd3"),
     "The Red List as GBIF distributes it, published July 28, 2026, which is how "
     "the categories here were read in bulk."),
    (apa.wiki("https://en.wikipedia.org/wiki/Chess_endgame") if False else
     apa.web("Wikipedia contributors", 2026, "Wikipedia", None,
             "https://en.wikipedia.org"),
     "The coordinates of the named places, taken from each place's own article "
     "where it carries one; 62 of the 137 rows are placed this way, and the rest "
     "carry a centroid chosen here and described in the card."),
]


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


def rows_for_js():
    out = []
    for r in ROWS:
        out.append({
            "e": r["episode"], "n": r["name"], "s": r["scientific"], "r": r["rank"],
            "g": r["group"], "sg": r["subgroup"], "l": r["location"],
            "la": r["lat"], "lo": r["lon"], "p": r["precision"],
            "pn": r["place_note"], "ps": r["place_source"],
            "i": r.get("iucn"), "it": r.get("iucn_taxon"), "inote": r.get("iucn_note"),
            "w": r["wikipedia"],
        })
    return out


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Planet Earth (2006) &middot; Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; }
* { box-sizing:border-box; }
[hidden] { display:none !important; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
.wrap { max-width:1320px; margin:0 auto; padding:32px 20px 60px; }
header.site { border-top:4px solid var(--accent); padding-top:22px; margin-bottom:26px;
  display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }
.brand { font-weight:700; font-size:20px; letter-spacing:.1em; text-decoration:none; color:var(--text); }
.brand:hover { color:var(--accent); }
nav.site a { color:var(--muted); text-decoration:none; font-size:14px; margin-right:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 12px; font-size:26px; }
.bar { display:flex; gap:8px; flex-wrap:wrap; margin:0 0 12px; }
.bar button { background:var(--panel); color:var(--muted); border:1px solid var(--line);
  border-radius:999px; padding:6px 14px; font-size:13px; cursor:pointer; font-family:inherit; }
.bar button.on { background:var(--accent); color:#0b1a2b; border-color:var(--accent); font-weight:600; }
.bar button:hover { color:var(--text); border-color:#3d3d3d; }
.bar button.on:hover { color:#0b1a2b; }
.controls { display:flex; gap:6px; flex-wrap:wrap; align-items:center; margin:0 0 10px; }
.controls .lab { font-size:11.5px; letter-spacing:.08em; text-transform:uppercase;
  color:var(--muted); margin-right:2px; }
.controls button { background:none; color:var(--muted); border:1px solid var(--line);
  border-radius:6px; padding:3px 9px; font-size:12.5px; cursor:pointer; font-family:inherit; }
.controls button.on { background:#26313f; color:var(--text); border-color:#3f5169; }
.controls button:hover { color:var(--text); }
.legend { display:flex; gap:4px; flex-wrap:wrap; align-items:center; margin:0 0 10px; }
.legend button { display:flex; align-items:center; gap:6px; background:none; border:1px solid var(--line);
  border-radius:6px; padding:3px 9px 3px 6px; font-size:12.5px; color:var(--muted);
  cursor:pointer; font-family:inherit; }
.legend button.on { border-color:#3f5169; background:#26313f; color:var(--text); }
.legend button:hover { color:var(--text); }
.legend svg { display:block; }
.key { display:flex; gap:16px; flex-wrap:wrap; align-items:center; color:var(--muted);
  font-size:12px; margin:0 0 12px; }
.key span { display:flex; align-items:center; gap:6px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; }
#diagram > svg, #diagram > canvas { width:100%; height:auto; display:block; user-select:none; touch-action:none; }
#diagram .ep li svg { width:14px; height:14px; flex:0 0 14px; }
#map { cursor:pointer; }
.side { flex:0 0 300px; min-width:0; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:16px; overflow-wrap:anywhere; }
#kindTxt { font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
#nameTxt { font-weight:700; font-size:17px; margin:2px 0 6px; }
#numTxt { font-size:13.5px; line-height:1.55; font-variant-numeric:tabular-nums; }
#numTxt b { color:var(--muted); font-weight:400; }
#bodyTxt { color:var(--muted); font-size:13.5px; line-height:1.55; margin-top:9px; }
#srcTxt { color:var(--muted); font-size:12px; margin-top:10px; border-top:1px solid var(--line); padding-top:8px; }
#srcTxt a { color:var(--accent); }
.grid { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; }
@media (max-width:1100px){ .grid{ grid-template-columns:repeat(3,1fr);} }
@media (max-width:820px){ .grid{ grid-template-columns:repeat(2,1fr);} }
.ep { background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:11px 12px 12px; }
.ep h3 { margin:0 0 2px; font-size:14px; font-weight:600; }
.ep h3 i { color:var(--muted); font-style:normal; font-weight:400; }
.ep .alt { color:var(--muted); font-size:11px; margin:0 0 7px; }
.ep ul { list-style:none; margin:0; padding:0; }
.ep li { display:flex; align-items:center; gap:7px; font-size:12.5px; padding:1.5px 0;
  color:#c8c8c8; cursor:pointer; }
.ep li:hover, .ep li.on { color:#ffffff; }
.ep li svg { flex:0 0 auto; }
.ep li.open span { opacity:.72; }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.method { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.refs { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.refs p { margin:0 0 8px; overflow-wrap:anywhere; }
.refs a { color:var(--accent); }
__APACSS__
h2.refh { font-size:15px; margin:26px 0 8px; }
@media (max-width:900px){ .stage{flex-direction:column;} .side{position:static; width:100%;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library &middot; Life</a><a href="tree-of-life.html">Tree of Life</a><a href="animals.html">Animals</a><a href="plants.html">Plants</a></nav>
</header>
<h1>Planet Earth (2006)</h1>
<div class="bar" id="views"><button data-v="map" class="on">The map</button><button data-v="episodes">The episodes</button><button data-v="repeats">The repeats</button></div>
<div class="controls" id="epCtl"><span class="lab">Episode</span></div>
<div class="legend" id="grpCtl"></div>
<div class="key" id="keyCtl"></div>
<div class="stage">
  <div id="diagram"></div>
  <div class="side"><div class="card">
    <div id="kindTxt"></div>
    <div id="nameTxt"></div>
    <div id="numTxt"></div>
    <div id="bodyTxt"></div>
    <div id="srcTxt"></div>
  </div></div>
</div>
<p class="note">__NOTE1__</p>
<p class="note" style="border-top:none; padding-top:0;">__NOTE2__</p>
<div class="method"><p>__METHOD__</p></div>
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</div>
<script>
const ROWS=__ROWS__, EPS=__EPS__, GROUPS=__GROUPS__, LANDPNG=__LANDPNG__, LW=__LW__, LH=__LH__;
const W=980, MAPH=490;
const el=document.getElementById('diagram');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const GC={}, GSH={}, GN={};
for(const [k,n,c,sh] of GROUPS){ GC[k]=c; GSH[k]=sh; GN[k]=n; }
const RANKN={species:'species',subspecies:'subspecies',genus:'genus',family:'family',
  order:'order',tribe:'tribe',phylum:'phylum',informal:'an informal group','non-taxon':'not a taxon'};
const CATN={LC:'Least Concern',NT:'Near Threatened',VU:'Vulnerable',EN:'Endangered',
  CR:'Critically Endangered',NE:'Not Evaluated'};
const CATC={LC:'#4f9d5d',NT:'#a8d84a',VU:'#f5e050',EN:'#f2a03d',CR:'#e0684b',NE:'#9a9a9a'};
const solid=r=>r==='species'||r==='subspecies';
const open=r=>!solid(r)&&r!=='non-taxon';

let view='map', ep=0, grp=null, showOpen=true, hot=null, land=null;

/* ---- marks ---- */
// one path per group, drawn the same on the canvas and in the panels
function glyphPath(sh,x,y,r){
  const p=new Path2D();
  if(sh==='circle') p.arc(x,y,r,0,7);
  else if(sh==='triangle'){ p.moveTo(x,y-r*1.15); p.lineTo(x+r,y+r*0.8); p.lineTo(x-r,y+r*0.8); p.closePath(); }
  else if(sh==='diamond'){ p.moveTo(x,y-r*1.2); p.lineTo(x+r,y); p.lineTo(x,y+r*1.2); p.lineTo(x-r,y); p.closePath(); }
  else if(sh==='square'){ p.rect(x-r*0.88,y-r*0.88,r*1.76,r*1.76); }
  else if(sh==='rounded'){ p.roundRect(x-r*0.95,y-r*0.7,r*1.9,r*1.4,r*0.7); }
  else if(sh==='hexagon'){ for(let i=0;i<6;i++){ const a=Math.PI/6+i*Math.PI/3, px=x+r*Math.cos(a), py=y+r*Math.sin(a); i?p.lineTo(px,py):p.moveTo(px,py); } p.closePath(); }
  else if(sh==='leaf'){ p.moveTo(x,y-r*1.2); p.quadraticCurveTo(x+r*1.1,y,x,y+r*1.2); p.quadraticCurveTo(x-r*1.1,y,x,y-r*1.2); p.closePath(); }
  else if(sh==='cap'){ p.arc(x,y+r*0.35,r,Math.PI,0); p.closePath(); }
  else if(sh==='dots'){ for(const [dx,dy] of [[-r*0.55,-r*0.3],[r*0.55,-r*0.3],[0,r*0.6]]){ p.moveTo(x+dx+r*0.42,y+dy); p.arc(x+dx,y+dy,r*0.42,0,7); } }
  return p;
}
function glyphSvg(sh,r,col,style){
  const s=r+2, c=s;
  let d='';
  if(sh==='circle') d='<circle cx="'+c+'" cy="'+c+'" r="'+r+'"/>';
  else if(sh==='triangle') d='<polygon points="'+c+','+(c-r*1.15)+' '+(c+r)+','+(c+r*0.8)+' '+(c-r)+','+(c+r*0.8)+'"/>';
  else if(sh==='diamond') d='<polygon points="'+c+','+(c-r*1.2)+' '+(c+r)+','+c+' '+c+','+(c+r*1.2)+' '+(c-r)+','+c+'"/>';
  else if(sh==='square') d='<rect x="'+(c-r*0.88)+'" y="'+(c-r*0.88)+'" width="'+(r*1.76)+'" height="'+(r*1.76)+'"/>';
  else if(sh==='rounded') d='<rect x="'+(c-r*0.95)+'" y="'+(c-r*0.7)+'" width="'+(r*1.9)+'" height="'+(r*1.4)+'" rx="'+(r*0.7)+'"/>';
  else if(sh==='hexagon'){ let p=[]; for(let i=0;i<6;i++){ const a=Math.PI/6+i*Math.PI/3; p.push((c+r*Math.cos(a)).toFixed(2)+','+(c+r*Math.sin(a)).toFixed(2)); } d='<polygon points="'+p.join(' ')+'"/>'; }
  else if(sh==='leaf') d='<path d="M '+c+' '+(c-r*1.2)+' Q '+(c+r*1.1)+' '+c+' '+c+' '+(c+r*1.2)+' Q '+(c-r*1.1)+' '+c+' '+c+' '+(c-r*1.2)+' Z"/>';
  else if(sh==='cap') d='<path d="M '+(c-r)+' '+(c+r*0.35)+' A '+r+' '+r+' 0 0 1 '+(c+r)+' '+(c+r*0.35)+' Z"/>';
  else if(sh==='dots') d=[[-r*0.55,-r*0.3],[r*0.55,-r*0.3],[0,r*0.6]].map(([dx,dy])=>'<circle cx="'+(c+dx)+'" cy="'+(c+dy)+'" r="'+(r*0.42)+'"/>').join('');
  const fill = style==='solid' ? 'fill="'+col+'"' : 'fill="none" stroke="'+col+'" stroke-width="1.6"'+(style==='dashed'?' stroke-dasharray="2.2 1.8"':'');
  return '<svg width="'+(s*2)+'" height="'+(s*2)+'" viewBox="0 0 '+(s*2)+' '+(s*2)+'" aria-hidden="true"><g '+fill+'>'+d+'</g></svg>';
}
function markStyle(r){ return solid(r.r)?'solid':(r.r==='non-taxon'?'dashed':'hollow'); }

/* ---- where each mark sits ---- */
const MX=lon=>(lon+180)/360*W, MY=lat=>(90-lat)/180*MAPH;
// rows that share a location fan out around it, so none hides another
const OFF=(function(){
  const by={}, off=new Array(ROWS.length);
  ROWS.forEach((r,i)=>{ const k=r.la+','+r.lo; (by[k]=by[k]||[]).push(i); });
  for(const k in by){ const g=by[k];
    if(g.length===1){ off[g[0]]=[0,0]; continue; }
    const rad=6+g.length*0.9;
    g.forEach((i,j)=>{ const a=j/g.length*Math.PI*2-Math.PI/2; off[i]=[rad*Math.cos(a),rad*Math.sin(a)]; });
  }
  return off;
})();
const PX=i=>[MX(ROWS[i].lo)+OFF[i][0], MY(ROWS[i].la)+OFF[i][1]];
const passes=i=>{ const r=ROWS[i];
  if(ep && r.e!==ep) return false;
  if(grp && r.g!==grp) return false;
  if(!showOpen && !solid(r.r)) return false;
  return true; };

/* ---- the card ---- */
function card(kind,name,rows,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').innerHTML=name;
  document.getElementById('numTxt').innerHTML=rows.filter(r=>r[1]).map(([k,v])=>'<b>'+esc(k)+'</b> '+v).join('<br>');
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').innerHTML=src;
}
const epOf=n=>EPS.find(x=>x.episode===n);
function alsoIn(s,e){ return [...new Set(ROWS.filter(r=>r.s===s&&r.e!==e).map(r=>r.e))].sort((a,b)=>a-b); }
function statusLine(r){
  if(!r.i) return RANKN[r.r]+' level, which the Red List does not assess';
  let t='<span style="color:'+CATC[r.i]+'">'+CATN[r.i]+'</span>';
  if(r.inote) t+=' <span style="color:#7d7d7d">('+esc(r.inote)+')</span>';
  return t;
}
function whereLine(r){
  return (r.p==='site'?'a place':'a region')+', '+r.la.toFixed(2)+'&deg;, '+r.lo.toFixed(2)+'&deg;'
    + (r.pn?' <span style="color:#7d7d7d">('+esc(r.pn)+')</span>':'');
}
function showRow(i){
  const r=ROWS[i], e=epOf(r.e), also=alsoIn(r.s,r.e);
  card('Episode '+r.e+' \u00b7 '+e.title,
    esc(r.n),
    [['name in the series','<i>'+esc(r.s)+'</i>, '+RANKN[r.r]],
     ['group',GN[r.g]+(r.sg?', '+esc(r.sg):'')],
     ['filmed',esc(r.l)],
     ['placed',whereLine(r)],
     ['Red List',statusLine(r)],
     ['also in',also.length?also.map(n=>n+' '+epOf(n).title).join(', '):''],
     ['this episode is',e.streaming_episode!==e.episode?'numbered '+e.streaming_episode+' on some streaming apps':'']],
    r.i?'':'A conservation status belongs to a species or a subspecies. This row is '+RANKN[r.r]+', so it carries none.',
    '<a href="'+r.w+'">Wikipedia</a>'+(r.i?' &middot; IUCN Red List 2026-1':'')+(r.ps?' &middot; place: '+esc(r.ps):''));
}
function showMap(){
  const n=ROWS.filter((_,i)=>passes(i)).length;
  const gs=Object.entries(ROWS.filter((_,i)=>passes(i)).reduce((a,r)=>(a[r.g]=(a[r.g]||0)+1,a),{}))
    .sort((a,b)=>b[1]-a[1]).map(([k,v])=>GN[k]+' '+v).join(', ');
  card('The map', ep?('Episode '+ep+', '+esc(epOf(ep).title)):(grp?esc(GN[grp][0].toUpperCase()+GN[grp].slice(1)):'All eleven episodes'),
    [['marks drawn',n+(n===1?' appearance':' appearances')],
     ['groups',gs],
     ['solid marks',ROWS.filter((_,i)=>passes(i)).filter(r=>solid(r.r)).length+' at species or subspecies level'],
     ['open marks',ROWS.filter((_,i)=>passes(i)).filter(r=>!solid(r.r)).length+' broader, or not a taxon'],
     ['centroids',ROWS.filter((_,i)=>passes(i)).filter(r=>r.p==='region').length+' of them stand for a region rather than a place']],
    'Each mark answers under the pointer with what it is, where the episode filmed it, and what the Red List makes of it.',
    'Brian Rivera\\u2019s record of the series; IUCN Red List 2026-1');
}
function showEpisode(n){
  const e=epOf(n), rs=ROWS.filter(r=>r.e===n);
  const gs=Object.entries(rs.reduce((a,r)=>(a[r.g]=(a[r.g]||0)+1,a),{})).sort((a,b)=>b[1]-a[1]).map(([k,v])=>GN[k]+' '+v).join(', ');
  const rep=rs.filter(r=>alsoIn(r.s,n).length).length;
  card('Episode '+n, esc(e.title),
    [['named in it',rs.length+' appearances'],
     ['groups',gs],
     ['shared with other episodes',rep?rep+' of them turn up elsewhere in the series':'none; everything here is filmed once'],
     ['on some streaming apps',e.streaming_episode!==e.episode?'numbered '+e.streaming_episode:'numbered '+n+' as well']],
    '', 'Brian Rivera\\u2019s record of the series');
}
function showRepeat(s){
  const rs=ROWS.filter(r=>r.s===s), r0=rs[0];
  card(rs.length+' episodes', esc(r0.n),
    [['name in the series','<i>'+esc(s)+'</i>, '+RANKN[r0.r]],
     ['group',GN[r0.g]],
     ['episodes',rs.map(r=>r.e+' '+epOf(r.e).title).join(', ')],
     ['filmed',[...new Set(rs.map(r=>r.l))].join('; ')],
     ['Red List',statusLine(r0)]],
    '', '<a href="'+r0.w+'">Wikipedia</a>'+(r0.i?' &middot; IUCN Red List 2026-1':''));
}
function showRepeats(){
  card('The repeats','Fourteen taxa, twice or more',
    [['taxa drawn',REPEATS.length],
     ['in three episodes',REPEATS.filter(r=>r.eps.length===3).map(r=>r.n).join(' and ')],
     ['the rest','appear in two'],
     ['everything else','121 distinct taxa in all, so 107 are filmed once']],
    'The only thread the series leaves between its episodes is what it filmed twice.',
    'Brian Rivera\\u2019s record of the series');
}

/* ---- the map ---- */
function mapView(){
  const cv=document.createElement('canvas'); cv.width=W; cv.height=MAPH; cv.id='map';
  const ctx=cv.getContext('2d');
  const im=ctx.createImageData(W,MAPH), d=im.data;
  for(let py=0;py<MAPH;py++) for(let px=0;px<W;px++){
    const lx=Math.floor(px/W*LW), ly=Math.floor(py/MAPH*LH);
    const isLand=land&&land[ly*LW+lx]>0; const i=(py*W+px)*4;
    const c=isLand?[58,62,66]:[14,24,40]; d[i]=c[0]; d[i+1]=c[1]; d[i+2]=c[2]; d[i+3]=255;
  }
  ctx.putImageData(im,0,0);
  ctx.strokeStyle='rgba(230,230,230,0.10)'; ctx.lineWidth=1;
  for(let l=-150;l<=150;l+=30){ ctx.beginPath(); ctx.moveTo(MX(l),0); ctx.lineTo(MX(l),MAPH); ctx.stroke(); }
  for(let p=-60;p<=60;p+=30){ ctx.beginPath(); ctx.moveTo(0,MY(p)); ctx.lineTo(W,MY(p)); ctx.stroke(); }
  const order=ROWS.map((_,i)=>i).filter(passes).sort((a,b)=>(a===hot?1:0)-(b===hot?1:0));
  for(const i of order){
    const r=ROWS[i], [x,y]=PX(i), on=hot===i, rad=on?8:6, col=GC[r.g], st=markStyle(r);
    if(r.p==='region'){ ctx.beginPath(); ctx.arc(x,y,rad+5,0,7); ctx.fillStyle=col+'26'; ctx.fill(); }
    const p=glyphPath(GSH[r.g],x,y,rad);
    if(st==='solid'){ ctx.fillStyle=col; ctx.fill(p); ctx.lineWidth=1.2; ctx.strokeStyle=on?'#ffffff':'#121212'; ctx.stroke(p); }
    else { ctx.lineWidth=on?2.4:1.8; ctx.strokeStyle=on?'#ffffff':col; ctx.setLineDash(st==='dashed'?[2.6,2.2]:[]); ctx.stroke(p); ctx.setLineDash([]); }
  }
  return cv;
}
function mapHit(x,y){
  let best=null, bd=13;
  for(const i of ROWS.map((_,i)=>i).filter(passes)){ const [mx,my]=PX(i); const d=Math.hypot(x-mx,y-my); if(d<bd){ bd=d; best=i; } }
  return best;
}

/* ---- the episodes ---- */
function episodesView(){
  const g=document.createElement('div'); g.className='grid'; g.id='eps';
  let s='';
  for(const e of EPS){
    const rs=ROWS.map((r,i)=>[r,i]).filter(([r])=>r.e===e.episode);
    s+='<div class="ep" data-ep="'+e.episode+'"><h3><i>'+e.episode+'</i> '+esc(e.title)+'</h3>'
      +'<p class="alt">'+rs.length+' named'+(e.streaming_episode!==e.episode?' &middot; episode '+e.streaming_episode+' on some apps':'')+'</p><ul>';
    for(const [r,i] of rs){
      s+='<li data-row="'+i+'" class="'+(solid(r.r)?'':'open')+'">'+glyphSvg(GSH[r.g],5,GC[r.g],markStyle(r))
        +'<span>'+esc(r.n)+'</span></li>';
    }
    s+='</ul></div>';
  }
  g.innerHTML=s;
  return g;
}

/* ---- the repeats ---- */
const REPEATS=(function(){
  const by={};
  ROWS.forEach(r=>{ (by[r.s]=by[r.s]||[]).push(r); });
  return Object.entries(by).filter(([,v])=>v.length>1)
    .map(([s,v])=>({s, n:v[0].n, g:v[0].g, r:v[0].r, eps:[...new Set(v.map(x=>x.e))].sort((a,b)=>a-b)}))
    .sort((a,b)=>b.eps.length-a.eps.length || a.eps[0]-b.eps[0] || a.n.localeCompare(b.n));
})();
const RP={x:250, w:700, y:118, row:27};
const RX=e=>RP.x+(e-1)/10*RP.w;
function repeatsView(){
  const h=RP.y+REPEATS.length*RP.row+34;
  let s='<svg id="rsvg" viewBox="0 0 '+W+' '+h+'" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The taxa that appear in more than one episode">';
  for(const e of EPS){
    const x=RX(e.episode);
    s+='<line x1="'+x.toFixed(1)+'" y1="'+(RP.y-10)+'" x2="'+x.toFixed(1)+'" y2="'+(RP.y+REPEATS.length*RP.row-8)+'" stroke="#242424"/>';
    s+='<text x="'+x.toFixed(1)+'" y="'+(RP.y-16)+'" text-anchor="middle" font-size="12.5" fill="#c8c8c8">'+e.episode+'</text>';
    s+='<text x="'+x.toFixed(1)+'" y="'+(RP.y-94)+'" text-anchor="end" font-size="10.5" fill="#9a9a9a" transform="rotate(-42 '+x.toFixed(1)+' '+(RP.y-94)+')">'+esc(e.title)+'</text>';
  }
  REPEATS.forEach((t,i)=>{
    const y=RP.y+i*RP.row, on=hot===t.s, col=GC[t.g];
    s+='<g data-rep="'+esc(t.s)+'" style="cursor:pointer">';
    s+='<rect x="0" y="'+(y-11)+'" width="'+W+'" height="'+RP.row+'" fill="'+(on?'#1d2531':'transparent')+'"/>';
    s+='<text x="'+(RP.x-16)+'" y="'+(y+4)+'" text-anchor="end" font-size="12.5" fill="'+(on?'#ffffff':'#c8c8c8')+'">'+esc(t.n)+'</text>';
    s+='<line x1="'+RX(t.eps[0]).toFixed(1)+'" y1="'+y+'" x2="'+RX(t.eps[t.eps.length-1]).toFixed(1)+'" y2="'+y+'" stroke="'+col+'" stroke-width="'+(on?2.4:1.5)+'" opacity="'+(on?1:0.75)+'"/>';
    for(const e of t.eps){
      s+='<circle cx="'+RX(e).toFixed(1)+'" cy="'+y+'" r="'+(on?5.5:4.5)+'" fill="'+col+'" stroke="#121212" stroke-width="1"/>';
    }
    s+='<text x="'+(RX(t.eps[t.eps.length-1])+14).toFixed(1)+'" y="'+(y+4)+'" font-size="10.5" fill="#7d7d7d">'+t.eps.length+'</text>';
    s+='</g>';
  });
  s+='<text x="0" y="'+(h-10)+'" font-size="11" fill="#9a9a9a">each line is one taxon, its dots the episodes it appears in</text>';
  return s+'</svg>';
}

/* ---- the controls ---- */
function buildControls(){
  const e=document.getElementById('epCtl');
  e.innerHTML='<span class="lab">Episode</span><button data-e="0" class="on">All</button>'
    +EPS.map(x=>'<button data-e="'+x.episode+'" title="'+esc(x.title)+'">'+x.episode+'</button>').join('');
  const g=document.getElementById('grpCtl');
  g.innerHTML='<button data-g="" class="on">Every group</button>'
    +GROUPS.map(([k,n,c,sh])=>'<button data-g="'+k+'">'+glyphSvg(sh,5,c,'solid')+n+'</button>').join('');
  document.getElementById('keyCtl').innerHTML=
    '<span>'+glyphSvg('circle',5,'#c8c8c8','solid')+'species or subspecies</span>'
    +'<span>'+glyphSvg('circle',5,'#c8c8c8','hollow')+'genus, family or broader</span>'
    +'<span>'+glyphSvg('circle',5,'#c8c8c8','dashed')+'not a taxon</span>'
    +'<span><svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="7" fill="#c8c8c826"/><circle cx="8" cy="8" r="4" fill="#c8c8c8"/></svg>a region, not a place</span>'
    +'<button id="openBtn" class="on" style="background:none;color:var(--muted);border:1px solid var(--line);border-radius:6px;padding:3px 9px;font-size:12.5px;cursor:pointer;font-family:inherit">29 above species level, shown</button>';
}

/* ---- render ---- */
function render(){
  el.innerHTML='';
  const ctl=document.getElementById('epCtl'), leg=document.getElementById('grpCtl'), key=document.getElementById('keyCtl');
  ctl.hidden=leg.hidden=key.hidden=(view!=='map');
  if(view==='map'){ el.appendChild(mapView()); }
  else if(view==='episodes'){ el.appendChild(episodesView()); }
  else { el.innerHTML=repeatsView(); }
}
function home(){ if(view==='map') showMap(); else if(view==='episodes') showEpisode(1); else showRepeats(); }

document.getElementById('views').addEventListener('click',ev=>{
  const b=ev.target.closest('button'); if(!b) return;
  view=b.dataset.v; hot=null;
  for(const x of document.querySelectorAll('#views button')) x.classList.toggle('on',x===b);
  render(); home();
});
document.getElementById('epCtl').addEventListener('click',ev=>{
  const b=ev.target.closest('button'); if(!b) return;
  ep=+b.dataset.e; hot=null;
  for(const x of document.querySelectorAll('#epCtl button')) x.classList.toggle('on',x===b);
  render(); showMap();
});
document.getElementById('grpCtl').addEventListener('click',ev=>{
  const b=ev.target.closest('button'); if(!b) return;
  grp=b.dataset.g||null; hot=null;
  for(const x of document.querySelectorAll('#grpCtl button')) x.classList.toggle('on',x===b);
  render(); showMap();
});
document.getElementById('keyCtl').addEventListener('click',ev=>{
  const b=ev.target.closest('#openBtn'); if(!b) return;
  showOpen=!showOpen; hot=null;
  b.classList.toggle('on',showOpen);
  b.textContent=showOpen?'29 above species level, shown':'29 above species level, hidden';
  render(); showMap();
});
el.addEventListener('pointermove',ev=>{
  if(view==='map'){
    const c=document.getElementById('map'); if(!c) return;
    const b=c.getBoundingClientRect();
    const i=mapHit((ev.clientX-b.left)/b.width*W,(ev.clientY-b.top)/b.height*MAPH);
    if(i===hot) return; hot=i; render(); if(i==null) showMap(); else showRow(i);
  } else if(view==='episodes'){
    const li=ev.target.closest('li[data-row]'); const k=li?+li.dataset.row:null;
    if(k===hot) return; hot=k;
    for(const x of document.querySelectorAll('#eps li')) x.classList.toggle('on',x===li);
    if(k==null) return; showRow(k);
  } else {
    const g=ev.target.closest('g[data-rep]'); const k=g?g.dataset.rep:null;
    if(k===hot) return; hot=k; render(); if(k==null) showRepeats(); else showRepeat(k);
  }
});
el.addEventListener('click',ev=>{
  if(view==='map'){
    const c=document.getElementById('map'); if(!c) return;
    const b=c.getBoundingClientRect();
    const i=mapHit((ev.clientX-b.left)/b.width*W,(ev.clientY-b.top)/b.height*MAPH);
    hot=i; render(); if(i==null) showMap(); else showRow(i);
  } else if(view==='episodes'){
    const h=ev.target.closest('.ep h3'); if(h){ showEpisode(+h.parentElement.dataset.ep); return; }
    const li=ev.target.closest('li[data-row]'); if(li) showRow(+li.dataset.row);
  } else {
    const g=ev.target.closest('g[data-rep]'); if(g) showRepeat(g.dataset.rep);
  }
});
el.addEventListener('pointerleave',()=>{ if(hot!=null){ hot=null; render(); home(); } });

function decode(b64,w,h,cb){ const img=new Image(); img.onload=()=>{ const off=document.createElement('canvas'); off.width=w; off.height=h; const o=off.getContext('2d'); o.drawImage(img,0,0); const d=o.getImageData(0,0,w,h).data; const a=new Uint8Array(w*h); for(let i=0,p=0;i<d.length;i+=4,p++) a[p]=d[i]; cb(a); }; img.src='data:image/png;base64,'+b64; }
buildControls();
decode(LANDPNG,LW,LH,a=>{ land=a; render(); home(); });

window.__pe=function(q){
  const o={view, ep, grp, showOpen, hot, land:!!land,
    drawn:ROWS.map((_,i)=>i).filter(passes).length,
    repeats:REPEATS.length,
    card:document.getElementById('numTxt').textContent,
    kind:document.getElementById('kindTxt').textContent,
    name:document.getElementById('nameTxt').textContent,
    body:document.getElementById('bodyTxt').textContent,
    src:document.getElementById('srcTxt').textContent,
    panels:document.querySelectorAll('#eps .ep').length,
    entries:document.querySelectorAll('#eps li[data-row]').length,
    reprows:document.querySelectorAll('#rsvg g[data-rep]').length};
  if(q&&q.px!=null){ const i=mapHit(q.px[0],q.px[1]); o.hit=i; o.hitName=i==null?null:ROWS[i].n; }
  if(q&&q.row!=null){ o.at=PX(q.row); o.base=[MX(ROWS[q.row].lo),MY(ROWS[q.row].la)]; }
  if(q&&q.pixel){ const c=document.getElementById('map'); if(c){ const d=c.getContext('2d').getImageData(q.pixel[0],q.pixel[1],1,1).data; o.rgb=[d[0],d[1],d[2]]; } }
  if(q&&q.show!=null){ showRow(q.show); }
  return o;
};
</script>
</body>
</html>
"""

html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__ROWS__", _js(rows_for_js()))
        .replace("__EPS__", _js(EPS))
        .replace("__GROUPS__", _js(GROUPS))
        .replace("__LANDPNG__", _js(GEO["land"]))
        .replace("__LW__", str(GEO["landW"])).replace("__LH__", str(GEO["landH"]))
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")

reps = Counter(r["scientific"] for r in ROWS)
print(f"wrote {OUT.name} ({len(html):,} B): {len(ROWS)} rows, {len(reps)} taxa, "
      f"{sum(1 for v in reps.values() if v > 1)} repeats, {len(EPS)} episodes")
