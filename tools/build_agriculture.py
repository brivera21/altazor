#!/usr/bin/env python3
"""Generate agriculture.html, Agriculture: the origins, the harvest, and the
land and the animals.

Three views. The origins: the world map with the dozen places where
plants and animals were domesticated, each answering under the pointer
with its crops, its animals and its date, and a line of time beneath
running from twelve thousand years ago to now. The harvest: the world's
largest crops as bars, tonnes a year, with who grows them and what for.
The land and the animals: what farming takes of the habitable land, what
share of it feeds livestock and what the livestock give back, and the
mass of the farm animals against the mass of every wild mammal and bird.

Data: tools/agriculture_data.py and the coastline raster in
tools/data/plates.json.

Usage: python3 build_agriculture.py
"""

import json
from pathlib import Path

import apa
from agriculture_data import CENTRES, CROPS, LAND, BIOMASS, REFS

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "agriculture.html"
GEO = json.loads((ROOT / "tools" / "data" / "plates.json").read_text())

NOTE1 = ("Farming was invented at least a dozen times, by people who had "
         "never heard of one another, within a few thousand years of the "
         "ice retreating: wheat in the Levant, rice on the Yangtze, millet "
         "on the Yellow River, taro in New Guinea, maize in Mexico, "
         "potatoes in the Andes, sorghum in the Sahel. The first view is "
         "the map of those places, each answering with what it gave the "
         "world and when.")

NOTE2 = ("The second view is what those beginnings became: the harvest of "
         "one year, a dozen crops that between them weigh more than "
         "everything else people grow, three of them grasses that feed "
         "most of humanity and one, sugarcane, that outweighs them all. "
         "The third is the bill: nearly half the habitable land, four "
         "fifths of it given to animals, and a planet on which the farm "
         "animals outweigh every wild mammal fourteen times over.")

METHOD = ("The dates of domestication are round figures from the "
          "archaeological and genetic literature and move with every dig; "
          "each is the usual estimate for when a crop or animal was clearly "
          "domesticated, not when it was first gathered or tamed, which is "
          "earlier. The Ethiopian centre has no agreed date. The harvests "
          "are FAO figures as reported per crop, each with its own year, "
          "so the bars are not all from the same season; palm oil is the "
          "oil, not the fruit. The land figures are Ritchie and Roser's "
          "reading of FAO data, in which cropland grown for animal feed is "
          "counted with the pastures as land for livestock. Biomass is "
          "carbon, after Bar-On and colleagues, whose estimates carry "
          "uncertainties of about a factor of two for the wild animals.")


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


centres = [{"k": k, "n": n, "lon": lon, "lat": lat, "ya": ya, "plants": pl, "animals": an, "b": b} for k, n, lon, lat, ya, pl, an, b in CENTRES]
crops = [{"k": k, "n": n, "mt": mt, "year": y, "top": top, "use": use, "s": s} for k, n, mt, y, top, use, s in CROPS]
biomass = [{"k": k, "n": n, "gtc": g, "b": b} for k, n, g, b in BIOMASS]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agriculture &middot; Altazor</title>
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
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; }
#diagram svg, #diagram canvas { width:100%; height:auto; display:block; user-select:none; touch-action:none; }
.side { flex:0 0 300px; min-width:0; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:16px; overflow-wrap:anywhere; }
#kindTxt { font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
#nameTxt { font-weight:700; font-size:17px; margin:2px 0 6px; }
#numTxt { font-size:13.5px; line-height:1.55; font-variant-numeric:tabular-nums; }
#numTxt b { color:var(--muted); font-weight:400; }
#bodyTxt { color:var(--muted); font-size:13.5px; line-height:1.55; margin-top:9px; }
#srcTxt { color:var(--muted); font-size:12px; margin-top:10px; border-top:1px solid var(--line); padding-top:8px; }
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
  <nav class="site"><a href="library.html">&larr; Library &middot; Homo Sapiens</a><a href="plants.html">Plants</a><a href="populous-countries.html">Population</a><a href="migration.html">Homo Sapiens Migration</a></nav>
</header>
<h1>Agriculture</h1>
<div class="bar" id="views"><button data-v="origins" class="on">The origins</button><button data-v="harvest">The harvest</button><button data-v="land">The land and the animals</button></div>
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
const CENTRES=__CENTRES__, CROPS=__CROPS__, LAND=__LAND__, BIOMASS=__BIOMASS__, LANDPNG=__LANDPNG__, LW=__LW__, LH=__LH__;
const W=980;
const el=document.getElementById('diagram');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const fmt=(n,d)=>n.toLocaleString('en-US',{maximumFractionDigits:d==null?0:d,minimumFractionDigits:d==null?0:d});
let view='origins', hot=null, land=null;

/* ---- the card ---- */
function card(kind,name,rows,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').innerHTML=name;
  document.getElementById('numTxt').innerHTML=rows.filter(r=>r[1]).map(([k,v])=>'<b>'+esc(k)+'</b> '+v).join('<br>');
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').textContent=src;
}
const ago=ya=>ya==null?'no agreed date':'about '+fmt(ya)+' years ago';
function showCentre(k){ const c=CENTRES.find(x=>x.k===k); card('A centre of domestication', esc(c.n), [['when',ago(c.ya)],['plants',c.plants==='none'?'':c.plants],['animals',c.animals==='none'?'':c.animals]], c.b, 'Larson et al. 2014; Wikipedia, Neolithic Revolution'); }
function showOrigins(){ const dated=CENTRES.filter(c=>c.ya!=null); card('The origins','Farming, invented many times',[['places drawn',CENTRES.length],['the oldest',dated.sort((a,b)=>b.ya-a.ya)[0].n+', '+ago(Math.max(...dated.map(c=>c.ya)))],['the span','from the end of the ice age to about 4,000 years ago']],'Each dot is a place where people turned wild plants or animals into crops or livestock without learning it from anyone else; the colour runs from the oldest, in orange, to the latest, in blue. Each answers under the pointer, and so does its mark on the line of time.','Larson et al. 2014; Wikipedia, Neolithic Revolution'); }
function showCrop(k){ const c=CROPS.find(x=>x.k===k); const tot=CROPS.reduce((a,x)=>a+x.mt,0); card('A crop, '+c.year, esc(c.n), [['the harvest',fmt(c.mt)+' million tonnes'],['the largest grower',c.top],['what for',c.use],['a share',fmt(c.mt/8.1,0)+' kg for every person on Earth']], 'One year\\u2019s world harvest of this crop, as the FAO counts it, fresh weight; the tonnage says nothing about calories, which is why sugarcane, mostly water, tops the list and wheat, dry grain, feeds more people.', c.s+'; FAOSTAT'); }
function showHarvest(){ const tot=CROPS.reduce((a,x)=>a+x.mt,0); const grasses=CROPS.filter(c=>['sugarcane','maize','rice','wheat','barley'].includes(c.k)).reduce((a,x)=>a+x.mt,0); card('The harvest','Twelve crops, one year each',[['together','about '+fmt(tot/1000,1)+' billion tonnes'],['the grasses','sugarcane, maize, rice, wheat and barley: '+fmt(grasses/tot*100,0)+'% of it'],['the three staples','rice, wheat and maize, which between them supply most of the calories people eat']],'Each bar is one crop\\u2019s world harvest in the latest year reported for it; each answers under the pointer.','FAOSTAT; Wikipedia, per crop'); }
function showLand(){ card('The land','Nearly half the habitable Earth',[['farmland',fmt(LAND.agri_km2/1e6)+' million km\\u00b2, '+LAND.agri_share_habitable+'% of the habitable land'],['for livestock',LAND.livestock_pct+'% of it, pasture and feed crops together'],['for crops people eat',LAND.crops_people_pct+'%'],['for fibre and fuel',LAND.crops_other_pct+'%'],['what the animals give back',LAND.animal_calories_pct+'% of the world\\u2019s calories and '+LAND.animal_protein_pct+'% of its protein']],'Habitable land is the land that is not ice, desert or bare rock, about a fifth of the planet\\u2019s surface; farming has nearly half of it, and most of that is for the animals, which return a sixth of the food.','Ritchie & Roser 2024; Poore & Nemecek 2018'); }
function showBio(k){ const b=BIOMASS.find(x=>x.k===k); const ref=k==='wildbirds'||k==='poultry'?BIOMASS.find(x=>x.k==='wildbirds'):BIOMASS.find(x=>x.k==='wildmammals'); card('Biomass', esc(b.n), [['carbon',b.gtc+' gigatonnes'],['against the wild',k==='wildmammals'||k==='wildbirds'?'this is the wild':fmt(b.gtc/ref.gtc,1)+' times all '+ref.n]], b.b+'. Carbon is about a sixth of a living animal\\u2019s wet weight, so the livestock come to some 600 million tonnes of animal, and the wild mammals of the whole planet, whales included, to about 40.', 'Bar-On, Phillips & Milo 2018'); }
function showAnimals(){ card('The animals','The farm outweighs the wild',[['livestock','0.1 gigatonnes of carbon, '+fmt(0.1/0.007,0)+' times every wild mammal'],['humans','0.06, nine times the wild mammals by ourselves'],['poultry','0.005, two and a half times every wild bird']],'The mass of the mammals and birds on Earth, as carbon, on a log scale: the farm animals, the people, and the wild that is left. Each bar answers under the pointer.','Bar-On, Phillips & Milo 2018'); }

/* ---- the origins ---- */
const MAPH=460, TL={y:520,x:60,w:860,a:12000,b:0};
const TX=ya=>TL.x+(TL.a-ya)/(TL.a-TL.b)*TL.w;
const MX=lon=>(lon+180)/360*W, MY=lat=>(90-lat)/180*MAPH;
const ageCol=ya=>{ if(ya==null) return '#9a9a9a'; const t=Math.max(0,Math.min(1,(ya-4000)/(10500-4000))); const r=Math.round(88+(255-88)*t), g=Math.round(166+(176-166)*t), b=Math.round(255+(46-255)*t); return 'rgb('+r+','+g+','+b+')'; };
function originsView(){ const cv=document.createElement('canvas'); cv.width=W; cv.height=TL.y+60; cv.id='ocanvas'; const ctx=cv.getContext('2d');
  const im=ctx.createImageData(W,MAPH), d=im.data; for(let py=0;py<MAPH;py++) for(let px=0;px<W;px++){ const lx=Math.floor(px/W*LW), ly=Math.floor(py/MAPH*LH); const isLand=land&&land[ly*LW+lx]>0; const i=(py*W+px)*4; const c=isLand?[70,74,78]:[16,28,46]; d[i]=c[0]; d[i+1]=c[1]; d[i+2]=c[2]; d[i+3]=255; } ctx.putImageData(im,0,0);
  ctx.strokeStyle='rgba(230,230,230,0.15)'; ctx.lineWidth=1; for(let l=-150;l<=150;l+=30){ ctx.beginPath(); ctx.moveTo(MX(l),0); ctx.lineTo(MX(l),MAPH); ctx.stroke(); } for(let p=-60;p<=60;p+=30){ ctx.beginPath(); ctx.moveTo(0,MY(p)); ctx.lineTo(W,MY(p)); ctx.stroke(); }
  ctx.font='11px sans-serif'; const halo=(t,x,y)=>{ ctx.save(); ctx.lineJoin='round'; ctx.strokeStyle='#121212'; ctx.lineWidth=3.5; ctx.strokeText(t,x,y); ctx.restore(); ctx.fillText(t,x,y); };
  const OFF={crescent:[10,-10],yangtze:[10,14],yellow:[10,-8],newguinea:[-10,14],mesoamerica:[-10,-10],andes:[-10,4],amazonia:[10,14],sahel:[10,-8],ethiopia:[10,14],westafrica:[-10,16],eastern:[-10,-10],steppe:[10,-8]};
  for(const c of CENTRES){ const x=MX(c.lon), y=MY(c.lat), on=hot===c.k; ctx.fillStyle=ageCol(c.ya); ctx.beginPath(); ctx.arc(x,y,on?9:7,0,7); ctx.fill(); ctx.strokeStyle=on?'#ffffff':'#121212'; ctx.lineWidth=1.5; ctx.stroke(); const [dx,dy]=OFF[c.k]||[10,-8]; ctx.textAlign=dx<0?'right':'left'; ctx.fillStyle=on?'#ffffff':'#e6e6e6'; halo(c.n.replace(/^the /,''),x+dx,y+dy); }
  // the line of time
  ctx.strokeStyle='#8a94a6'; ctx.beginPath(); ctx.moveTo(TL.x,TL.y); ctx.lineTo(TL.x+TL.w,TL.y); ctx.stroke(); ctx.fillStyle='#9a9a9a'; ctx.textAlign='center';
  for(const ya of [12000,10000,8000,6000,4000,2000,0]){ ctx.beginPath(); ctx.moveTo(TX(ya),TL.y); ctx.lineTo(TX(ya),TL.y+6); ctx.stroke(); ctx.fillText(ya?fmt(ya)+' years ago':'now',TX(ya),TL.y+20); }
  for(const c of CENTRES){ if(c.ya==null) continue; const [x,y]=tlPos(c), on=hot===c.k; ctx.fillStyle=ageCol(c.ya); ctx.beginPath(); ctx.arc(x,y,on?7:5,0,7); ctx.fill(); ctx.strokeStyle=on?'#ffffff':'#121212'; ctx.lineWidth=1.5; ctx.stroke(); }
  ctx.fillStyle='#9a9a9a'; ctx.textAlign='left'; ctx.fillText('the same places on a line of time, from the end of the ice age; the ice age ended about 11,700 years ago',TL.x,TL.y+40);
  return cv; }
// dots that share a date stack upward on the line of time
function tlPos(c){ const same=CENTRES.filter(x=>x.ya!=null&&Math.abs(x.ya-c.ya)<150); const i=same.findIndex(x=>x.k===c.k); return [TX(c.ya), TL.y-12-i*13]; }
function originHit(x,y){ for(const c of CENTRES){ if(Math.hypot(x-MX(c.lon),y-MY(c.lat))<=12) return c.k; } for(const c of CENTRES){ if(c.ya==null) continue; const [tx,ty]=tlPos(c); if(Math.hypot(x-tx,y-ty)<=8) return c.k; } return null; }

/* ---- the harvest ---- */
const HB={x:190,y:30,w:700,bar:30};
const HX=mt=>HB.x+mt/2000*HB.w;
function harvestView(){ const rows=[...CROPS].sort((a,b)=>b.mt-a.mt); let s=''; const h=HB.y+rows.length*HB.bar+60;
  for(const v of [0,500,1000,1500,2000]){ s+='<line x1="'+HX(v).toFixed(1)+'" y1="'+HB.y+'" x2="'+HX(v).toFixed(1)+'" y2="'+(HB.y+rows.length*HB.bar)+'" stroke="#2b2b2b"/><text x="'+HX(v).toFixed(1)+'" y="'+(HB.y+rows.length*HB.bar+18)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+fmt(v)+'</text>'; }
  s+='<text x="'+(HB.x+HB.w/2)+'" y="'+(HB.y+rows.length*HB.bar+40)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">million tonnes in one year</text>';
  rows.forEach((c,i)=>{ const y=HB.y+i*HB.bar, on=hot===c.k; const col=['sugarcane','maize','rice','wheat','barley'].includes(c.k)?'#ffb02e':['potato','cassava','sugarbeet'].includes(c.k)?'#c9a6ff':c.k==='palmoil'||c.k==='soy'?'#9be564':'#f28cb0';
    s+='<g data-crop="'+c.k+'" style="cursor:pointer"><rect x="'+HB.x+'" y="'+(y+5)+'" width="'+(HX(c.mt)-HB.x).toFixed(1)+'" height="'+(HB.bar-10)+'" rx="3" fill="'+col+'" opacity="'+(on?1:0.8)+'"/><text x="'+(HB.x-8)+'" y="'+(y+HB.bar/2+4)+'" text-anchor="end" font-size="11.5" fill="'+(on?'#ffffff':'#c8c8c8')+'">'+esc(c.n)+'</text><text x="'+(HX(c.mt)+6).toFixed(1)+'" y="'+(y+HB.bar/2+4)+'" font-size="10.5" fill="#9a9a9a">'+fmt(c.mt)+', '+c.year+'</text></g>'; });
  s+='<text x="'+HB.x+'" y="'+(HB.y-10)+'" font-size="11" fill="#9a9a9a">orange: grasses; violet: roots; green: oil and protein crops; pink: fruit and vegetables</text>';
  return {svg:s, h}; }

/* ---- the land and the animals ---- */
function landView(){ let s=''; const x0=80, w=820;
  s+='<text x="'+x0+'" y="30" font-size="12" fill="#e6e6e6">the habitable land</text>';
  const y1=44, hb=44; const agri=LAND.agri_share_habitable/100;
  s+='<g data-land="all" style="cursor:pointer"><rect x="'+x0+'" y="'+y1+'" width="'+w+'" height="'+hb+'" rx="6" fill="#2a3444"/><rect x="'+x0+'" y="'+y1+'" width="'+(w*agri).toFixed(1)+'" height="'+hb+'" rx="6" fill="#8a6a3a"/>';
  s+='<text x="'+(x0+w*agri/2).toFixed(1)+'" y="'+(y1+hb/2+4)+'" text-anchor="middle" font-size="11.5" fill="#ffffff">farmland, '+LAND.agri_share_habitable+'%: '+fmt(LAND.agri_km2/1e6)+' million km\\u00b2</text><text x="'+(x0+w*agri+(w-w*agri)/2).toFixed(1)+'" y="'+(y1+hb/2+4)+'" text-anchor="middle" font-size="11.5" fill="#c8c8c8">forest, shrub, cities, rivers and lakes, '+(100-LAND.agri_share_habitable)+'%</text></g>';
  const y2=110; s+='<text x="'+x0+'" y="'+(y2-10)+'" font-size="12" fill="#e6e6e6">the farmland</text>';
  const parts=[['livestock','for livestock, pasture and feed crops',LAND.livestock_pct,'#a3583a'],['people','crops people eat',LAND.crops_people_pct,'#9be564'],['other','fibre and fuel',LAND.crops_other_pct,'#6ee7f2']]; let px=x0;
  for(const [k,n,pct,col] of parts){ const ww=w*pct/100; s+='<g data-land="'+k+'" style="cursor:pointer"><rect x="'+px.toFixed(1)+'" y="'+y2+'" width="'+ww.toFixed(1)+'" height="'+hb+'" fill="'+col+'" stroke="#121212"/>'+(ww>60?'<text x="'+(px+ww/2).toFixed(1)+'" y="'+(y2+hb/2+4)+'" text-anchor="middle" font-size="11.5" fill="#0b1a2b">'+esc(n)+', '+pct+'%</text>':'')+'</g>'; px+=ww; }
  s+='<text x="'+(x0+w)+'" y="'+(y2+hb+16)+'" text-anchor="end" font-size="10.5" fill="#9a9a9a">the sliver at the right, 4%, is fibre and fuel</text>';
  const y3=200; s+='<text x="'+x0+'" y="'+(y3-10)+'" font-size="12" fill="#e6e6e6">what the animals give back</text>';
  for(const [i,[n,pct]] of [['of the calories people eat',LAND.animal_calories_pct],['of the protein',LAND.animal_protein_pct]].entries()){ const y=y3+i*34; s+='<g data-land="back" style="cursor:pointer"><rect x="'+x0+'" y="'+y+'" width="'+w+'" height="24" rx="4" fill="#2a3444"/><rect x="'+x0+'" y="'+y+'" width="'+(w*pct/100).toFixed(1)+'" height="24" rx="4" fill="#a3583a"/><text x="'+(x0+8)+'" y="'+(y+16)+'" font-size="11.5" fill="#ffffff">'+pct+'% '+n+'</text></g>'; }
  const y4=310; s+='<text x="'+x0+'" y="'+(y4-10)+'" font-size="12" fill="#e6e6e6">the mammals and the birds, by mass of carbon, on a log scale</text>';
  const lo=0.001, hi=0.2, bw=w; const BX=v=>x0+Math.log10(v/lo)/Math.log10(hi/lo)*bw;
  for(const v of [0.001,0.01,0.1]){ s+='<line x1="'+BX(v).toFixed(1)+'" y1="'+y4+'" x2="'+BX(v).toFixed(1)+'" y2="'+(y4+BIOMASS.length*30)+'" stroke="#2b2b2b"/><text x="'+BX(v).toFixed(1)+'" y="'+(y4+BIOMASS.length*30+16)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+v+' Gt C</text>'; }
  BIOMASS.forEach((b,i)=>{ const y=y4+i*30, on=hot===b.k; const col=b.k.startsWith('wild')?'#9be564':b.k==='humans'?'#58a6ff':'#a3583a'; s+='<g data-bio="'+b.k+'" style="cursor:pointer"><rect x="'+x0+'" y="'+(y+5)+'" width="'+(BX(b.gtc)-x0).toFixed(1)+'" height="20" rx="3" fill="'+col+'" opacity="'+(on?1:0.85)+'"/><text x="'+(BX(b.gtc)+6).toFixed(1)+'" y="'+(y+19)+'" font-size="11" fill="'+(on?'#ffffff':'#c8c8c8')+'">'+esc(b.n)+', '+b.gtc+'</text></g>'; });
  return {svg:s, h:y4+BIOMASS.length*30+40}; }
function showLandPart(k){ if(k==='livestock') card('The farmland','For livestock',[['share',LAND.livestock_pct+'% of all farmland'],['what it is','pasture and rangeland, plus the cropland whose harvest is fed to animals, soybeans and maize above all'],['it returns',LAND.animal_calories_pct+'% of calories and '+LAND.animal_protein_pct+'% of protein']],'Grazing land is most of it, much of it dry country that would grow no crop; but the feed crops alone take more land than all the vegetables, fruit, roots and pulses people eat.','Ritchie & Roser 2024; Poore & Nemecek 2018');
  else if(k==='people') card('The farmland','Crops people eat',[['share',LAND.crops_people_pct+'% of all farmland'],['it returns',(100-LAND.animal_calories_pct)+'% of calories and '+(100-LAND.animal_protein_pct)+'% of protein']],'A sixth of the farmland grows five sixths of the food, counted in calories: the grains, the roots, the pulses, the oils, the fruit and vegetables.','Ritchie & Roser 2024');
  else if(k==='other') card('The farmland','Fibre and fuel',[['share',LAND.crops_other_pct+'% of all farmland']],'Cotton, rubber, tobacco, and the maize and sugarcane and oil palm grown for ethanol and biodiesel rather than for food.','Ritchie & Roser 2024');
  else if(k==='back') card('What the animals give back','A sixth of the food',[['calories',LAND.animal_calories_pct+'% of the world\\u2019s, from meat, dairy, eggs and farmed fish'],['protein',LAND.animal_protein_pct+'%'],['on',LAND.livestock_pct+'% of the farmland']],'The gap between the land the animals take and the food they return is the largest single fact about the world\\u2019s farming; it is the difference between grass and grain, and between an animal and a plant.','Poore & Nemecek 2018; Ritchie & Roser 2024');
  else showLand(); }

/* ---- render and wiring ---- */
function render(){ el.innerHTML=''; if(view==='origins') el.appendChild(originsView()); else { const q=view==='harvest'?harvestView():landView(); el.innerHTML='<svg viewBox="0 0 '+W+' '+q.h+'" xmlns="http://www.w3.org/2000/svg" id="asvg"><rect width="'+W+'" height="'+q.h+'" fill="#121212"/>'+q.svg+'</svg>'; } }
function home(){ if(view==='origins') showOrigins(); else if(view==='harvest') showHarvest(); else showLand(); }
function setView(v){ view=v; hot=null; for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on',b.dataset.v===v); render(); home(); }
document.getElementById('views').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setView(b.dataset.v); });
const pt=e=>{ const c=el.firstElementChild, b=c.getBoundingClientRect(); const vh=c.tagName==='CANVAS'?c.height:c.viewBox.baseVal.height; return [(e.clientX-b.left)/b.width*W,(e.clientY-b.top)/b.height*vh]; };
el.addEventListener('pointermove',e=>{ if(view!=='origins') return; const [x,y]=pt(e); const k=originHit(x,y); if(k===hot) return; hot=k; render(); if(k) showCentre(k); else showOrigins(); });
el.addEventListener('pointerover',e=>{ if(view==='origins') return; const g=e.target.closest('[data-crop],[data-land],[data-bio]'); if(!g) return; const k=g.getAttribute('data-crop')||g.getAttribute('data-land')||g.getAttribute('data-bio'); if(k===hot) return; hot=k; render(); if(g.hasAttribute('data-crop')) showCrop(k); else if(g.hasAttribute('data-land')) showLandPart(k); else showBio(k); });
el.addEventListener('pointerleave',()=>{ if(hot){ hot=null; render(); home(); } });

function decode(b64,w,h,cb){ const img=new Image(); img.onload=()=>{ const off=document.createElement('canvas'); off.width=w; off.height=h; const o=off.getContext('2d'); o.drawImage(img,0,0); const d=o.getImageData(0,0,w,h).data; const a=new Uint8Array(w*h); for(let i=0,p=0;i<d.length;i+=4,p++) a[p]=d[i]; cb(a); }; img.src='data:image/png;base64,'+b64; }
decode(LANDPNG,LW,LH,a=>{ land=a; render(); home(); });
render(); showOrigins();
window.__agri=(q)=>{ const o={view,hot,land:!!land,card:document.getElementById('numTxt').innerText,name:document.getElementById('nameTxt').innerText,body:document.getElementById('bodyTxt').innerText,
  bars:document.querySelectorAll('#asvg g[data-crop]').length, bios:document.querySelectorAll('#asvg g[data-bio]').length};
  if(q&&q.centre){ const c=CENTRES.find(x=>x.k===q.centre); o.px=[MX(c.lon),MY(c.lat)]; o.tx=c.ya==null?null:TX(c.ya); }
  if(q&&q.crop){ const r=document.querySelector('#asvg g[data-crop="'+q.crop+'"] rect'); o.barw=r?+r.getAttribute('width'):null; o.expect=HX(CROPS.find(c=>c.k===q.crop).mt)-HB.x; }
  if(q&&q.px){ const c=document.getElementById('ocanvas'); if(c){ const d=c.getContext('2d').getImageData(q.px[0],q.px[1],1,1).data; o.pixel=[d[0],d[1],d[2]]; } }
  return o; };
</script>
</body>
</html>
"""

html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__CENTRES__", _js(centres)).replace("__CROPS__", _js(crops)).replace("__LAND__", _js(LAND)).replace("__BIOMASS__", _js(biomass))
        .replace("__LANDPNG__", _js(GEO["land"])).replace("__LW__", str(GEO["landW"])).replace("__LH__", str(GEO["landH"]))
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(CENTRES)} centres, {len(CROPS)} crops")
