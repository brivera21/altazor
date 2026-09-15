#!/usr/bin/env python3
"""Generate projections.html, Map Projections: the maps, the stretch, and the
routes.

Three views. The maps: the world in nine projections, drawn from the
coastline raster by inverting each projection pixel by pixel, with the
graticule, Tissot's circles at the crossings, and a circle of a thousand
kilometers' radius that drags anywhere on the map and reads how many times
its true area it appears. The stretch: the area scale of each projection
against latitude, with a marker on the latitude line and the cities that
sit there. The routes: a great circle and the compass course between two
cities, on Mercator's map, where the course is straight, and on the globe,
where the great circle is.

Data: tools/projections_data.py and the coastline raster in
tools/data/plates.json.

Usage: python3 build_projections.py
"""

import json
from pathlib import Path

import apa
from projections_data import R_EARTH, PROJECTIONS, ROBINSON, PLACES, GREENLAND_AFRICA, CITIES, ROUTES, REFS

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "projections.html"
GEO = json.loads((ROOT / "tools" / "data" / "plates.json").read_text())

NOTE1 = ("A sphere will not lie flat. Every map of the world stretches "
         "something, and the choice of what to stretch is the whole art: "
         "Mercator kept every angle and let Greenland swell to the size of "
         "Africa; Peters kept every area and pulled the tropics long; "
         "Robinson kept nothing exactly and everything tolerably. The "
         "first view is nine of these, with the same circle of a thousand "
         "kilometers' radius to drag across each and watch it warp.")

NOTE2 = ("The second view is the stretch itself, the area a map gives to a "
         "place against the area it has, from the Equator to the poles, "
         "with the cities that live along the way. The third is what the "
         "stretch does to a journey: the shortest way between two cities "
         "is a great circle, which looks like a detour on Mercator's map "
         "and a straight line on the globe, while the constant compass "
         "course is the reverse.")

METHOD = ("The maps are drawn by inverting each projection at every pixel "
          "and reading the coastline raster, a 1,080 by 540 mask shared "
          "with the other Earth pages, so small islands are lost; the "
          "Winkel tripel, which has no closed inverse, is solved by "
          "Newton's method. The Earth is a sphere of 6,371 km here, and the "
          "Mercator map is cut at 80 degrees, where it would otherwise "
          "continue upward forever. Tissot's circles are drawn with a "
          "radius of 500 km and the draggable one of 1,000 km, both as "
          "true circles on the sphere projected point by point; the area "
          "ratio in the card is the projected polygon's area against the "
          "cap's true area. Distances are on the sphere; the ellipsoid "
          "changes them by a few tenths of a percent.")


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


projs = [{"k": k, "n": n, "kind": kind, "year": y, "who": who, "b": b} for k, n, kind, y, who, b in PROJECTIONS]
cities = {k: {"n": n, "lon": lon, "lat": lat} for k, (n, lon, lat) in CITIES.items()}

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Map Projections &middot; Altazor</title>
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
.controls { display:flex; align-items:center; gap:12px; flex-wrap:wrap; margin:0 0 12px; min-height:34px; }
.controls label { font-size:13px; color:var(--muted); }
.controls output { font-size:13px; color:var(--text); font-variant-numeric:tabular-nums; }
.presets { display:flex; gap:6px; flex-wrap:wrap; }
.presets button { background:var(--panel); color:var(--muted); border:1px solid var(--line);
  border-radius:8px; padding:4px 10px; font-size:12.5px; cursor:pointer; font-family:inherit; }
.presets button.on { color:var(--text); border-color:#58a6ff; }
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
  <nav class="site"><a href="library.html">&larr; Library &middot; Earth</a><a href="earth.html">Climate</a><a href="plates.html">Plate Tectonics</a><a href="ocean.html">Ocean Currents</a></nav>
</header>
<h1>Map Projections</h1>
<div class="bar" id="views"><button data-v="maps" class="on">The maps</button><button data-v="stretch">The stretch</button><button data-v="routes">The routes</button></div>
<div class="controls" id="mapCtl"><div class="presets" id="projs"></div></div>
<div class="controls" id="centreCtl" hidden><label>the globe faces</label><div class="presets" id="centers"><button data-c="atl" class="on">the Atlantic</button><button data-c="pac">the Pacific</button><button data-c="np">the North Pole</button><button data-c="sp">the South Pole</button></div></div>
<div class="controls" id="stretchCtl" hidden><label>the marker</label><output id="latOut"></output></div>
<div class="controls" id="routeCtl" hidden><div class="presets" id="routes"></div></div>
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
const PROJS=__PROJS__, ROB=__ROB__, PLACES=__PLACES__, GA=__GA__, CITIES=__CITIES__, ROUTES=__ROUTES__, LAND=__LAND__, LW=__LW__, LH=__LH__, RE=__RE__;
const W=980;
const el=document.getElementById('diagram');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const fmt=(n,d)=>n.toLocaleString('en-US',{maximumFractionDigits:d==null?0:d,minimumFractionDigits:d==null?0:d});
const D2R=Math.PI/180, R2D=180/Math.PI;
let view='maps', proj='mercator', center='atl', hot=null, cap={lon:-40,lat:60}, capR=1000, lat=51.5, route=0, land=null;
const CENTERS={atl:[-30,30],pac:[-160,10],np:[0,90],sp:[0,-90]};

/* ---- the projections: forward and inverse, in units of the Earth's radius; lon, lat in radians ---- */
const sinc=a=>a===0?1:Math.sin(a)/a;
const PHI1=Math.acos(2/Math.PI);
// Robinson's table, interpolated with a Catmull-Rom spline so that the scale is smooth between the 5-degree nodes
function crom(col,a){ const i=Math.min(17,Math.floor(a)), t=a-i; const g=j=>ROB[Math.max(0,Math.min(18,j))][col]; const p0=j=>j<0?2*ROB[0][col]-ROB[-j][col]:g(j); const y0=p0(i-1), y1=g(i), y2=g(i+1), y3=i+2<=18?g(i+2):2*ROB[18][col]-ROB[17][col]; return 0.5*((2*y1)+(-y0+y2)*t+(2*y0-5*y1+4*y2-y3)*t*t+(-y0+3*y1-3*y2+y3)*t*t*t); }
function robTab(phi){ const a=Math.abs(phi)*R2D/5; const p=crom(1,a), y=crom(2,a); return [p, phi<0?-y:y]; }
function robInvY(y){ const s=y<0?-1:1; y=Math.abs(y); for(let i=0;i<18;i++){ if(y<=ROB[i+1][2]){ const t=(y-ROB[i][2])/(ROB[i+1][2]-ROB[i][2]); return s*(ROB[i][0]+5*t)*D2R; } } return s*Math.PI/2; }
const P={
  mercator:{ fwd:(l,p)=>[l, Math.log(Math.tan(Math.PI/4+p/2))], inv:(x,y)=>[x, 2*Math.atan(Math.exp(y))-Math.PI/2], latMax:80*D2R },
  platecarree:{ fwd:(l,p)=>[l,p], inv:(x,y)=>[x,y] },
  gallpeters:{ fwd:(l,p)=>[l*Math.cos(45*D2R), Math.sin(p)/Math.cos(45*D2R)], inv:(x,y)=>{ const s=y*Math.cos(45*D2R); if(Math.abs(s)>1) return null; return [x/Math.cos(45*D2R), Math.asin(s)]; } },
  mollweide:{ fwd:(l,p)=>{ let th=p; for(let i=0;i<12;i++){ const f=2*th+Math.sin(2*th)-Math.PI*Math.sin(p), den=2+2*Math.cos(2*th); if(Math.abs(f)<1e-12||Math.abs(den)<1e-9) break; th-=f/den; } return [2*Math.SQRT2/Math.PI*l*Math.cos(th), Math.SQRT2*Math.sin(th)]; },
    inv:(x,y)=>{ const s=y/Math.SQRT2; if(Math.abs(s)>1) return null; const th=Math.asin(s); const sp=(2*th+Math.sin(2*th))/Math.PI; if(Math.abs(sp)>1) return null; const c=Math.cos(th); if(c<1e-9) return null; const l=Math.PI*x/(2*Math.SQRT2*c); if(Math.abs(l)>Math.PI) return null; return [l, Math.asin(sp)]; } },
  sinusoidal:{ fwd:(l,p)=>[l*Math.cos(p), p], inv:(x,y)=>{ if(Math.abs(y)>Math.PI/2) return null; const c=Math.cos(y); if(c<1e-9) return null; const l=x/c; if(Math.abs(l)>Math.PI) return null; return [l,y]; } },
  robinson:{ fwd:(l,p)=>{ const [pl,y]=robTab(p); return [0.8487*pl*l, 1.3523*y]; }, inv:(x,y)=>{ const yy=y/1.3523; if(Math.abs(yy)>1) return null; const p=robInvY(yy); const [pl]=robTab(p); const l=x/(0.8487*pl); if(Math.abs(l)>Math.PI) return null; return [l,p]; } },
  winkel:{ fwd:(l,p)=>{ const a=Math.acos(Math.cos(p)*Math.cos(l/2)); const s=sinc(a); return [0.5*(l*Math.cos(PHI1)+2*Math.cos(p)*Math.sin(l/2)/s), 0.5*(p+Math.sin(p)/s)]; },
    inv:(x,y)=>{ let l=x/(0.5*(Math.cos(PHI1)+1)), p=y; for(let i=0;i<12;i++){ const [fx,fy]=P.winkel.fwd(l,p); const ex=fx-x, ey=fy-y; if(Math.abs(ex)<1e-7&&Math.abs(ey)<1e-7) break; const h=1e-5; const [fx1,fy1]=P.winkel.fwd(l+h,p), [fx2,fy2]=P.winkel.fwd(l,p+h); const a=(fx1-fx)/h, b=(fx2-fx)/h, c=(fy1-fy)/h, d=(fy2-fy)/h; const det=a*d-b*c; if(Math.abs(det)<1e-12) return null; l-=(d*ex-b*ey)/det; p-=(-c*ex+a*ey)/det; if(Math.abs(p)>Math.PI/2+0.01||Math.abs(l)>Math.PI+0.01) return null; } if(Math.abs(p)>Math.PI/2||Math.abs(l)>Math.PI) return null; return [l,p]; } },
  ortho:{ fwd:(l,p)=>{ const [l0,p0]=CENTERS[center].map(v=>v*D2R); const c=Math.sin(p0)*Math.sin(p)+Math.cos(p0)*Math.cos(p)*Math.cos(l-l0); if(c<0) return null; return [Math.cos(p)*Math.sin(l-l0), Math.cos(p0)*Math.sin(p)-Math.sin(p0)*Math.cos(p)*Math.cos(l-l0)]; },
    inv:(x,y)=>{ const [l0,p0]=CENTERS[center].map(v=>v*D2R); const r=Math.hypot(x,y); if(r>1) return null; const c=Math.asin(r); if(r<1e-9) return [l0,p0]; const p=Math.asin(Math.cos(c)*Math.sin(p0)+y*Math.sin(c)*Math.cos(p0)/r); const l=l0+Math.atan2(x*Math.sin(c), r*Math.cos(c)*Math.cos(p0)-y*Math.sin(c)*Math.sin(p0)); return [l,p]; } },
  azeq:{ fwd:(l,p)=>{ const rho=Math.PI/2-p; return [rho*Math.sin(l), rho*Math.cos(l)]; }, inv:(x,y)=>{ const rho=Math.hypot(x,y); if(rho>Math.PI) return null; return [Math.atan2(x,y), Math.PI/2-rho]; } },
};
function fwd(l,p){ const q=P[proj]; if(q.latMax){ p=Math.max(-q.latMax,Math.min(q.latMax,p)); } return q.fwd(l,p); }
function bbox(){ let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9; const q=P[proj]; const lm=q.latMax||Math.PI/2; for(let l=-180;l<=180;l+=2) for(let p=-90;p<=90;p+=2){ const pp=Math.max(-lm,Math.min(lm,p*D2R)); const r=q.fwd(l*D2R,pp); if(!r) continue; x0=Math.min(x0,r[0]); x1=Math.max(x1,r[0]); y0=Math.min(y0,r[1]); y1=Math.max(y1,r[1]); } return {x0,x1,y0,y1}; }
let M=null; // the fit of the current projection into the canvas
function fitMap(){ const b=bbox(); const H=560, pad=30; const s=Math.min((W-2*pad)/(b.x1-b.x0),(H-2*pad)/(b.y1-b.y0)); const cx=(b.x0+b.x1)/2, cy=(b.y0+b.y1)/2; M={s,cx,cy,H,ox:W/2,oy:H/2}; }
const toPx=r=>r?[M.ox+(r[0]-M.cx)*M.s, M.oy-(r[1]-M.cy)*M.s]:null;
const fromPx=(px,py)=>[(px-M.ox)/M.s+M.cx, M.cy-(py-M.oy)/M.s];
const isLand=(lon,lat)=>{ if(!land) return false; let lx=Math.floor(((lon*R2D+540)%360)/360*LW), ly=Math.floor((90-lat*R2D)/180*LH); lx=Math.max(0,Math.min(LW-1,lx)); ly=Math.max(0,Math.min(LH-1,ly)); return land[ly*LW+lx]>0; };
let cache={};
function paintMap(ctx){ const key=proj+':'+center; if(land&&cache[key]){ ctx.putImageData(cache[key],0,0); return; } const im=ctx.createImageData(W,M.H), d=im.data; const q=P[proj];
  for(let py=0;py<M.H;py++) for(let px=0;px<W;px++){ const [x,y]=fromPx(px+0.5,py+0.5); const r=q.inv(x,y); const i=(py*W+px)*4; let c=[18,18,18];
    if(r&&Math.abs(r[1])<=Math.PI/2+1e-9&&Math.abs(r[0])<=Math.PI+1e-9&&!(q.latMax&&Math.abs(r[1])>q.latMax)) c=isLand(r[0],r[1])?[70,74,78]:[16,28,46];
    d[i]=c[0]; d[i+1]=c[1]; d[i+2]=c[2]; d[i+3]=255; }
  if(land) cache[key]=im; ctx.putImageData(im,0,0); }
function line(ctx,pts){ let up=true, last=null; ctx.beginPath(); for(const p of pts){ const q=toPx(p); if(!q){ up=true; continue; } if(last&&Math.hypot(q[0]-last[0],q[1]-last[1])>60) up=true; if(up){ ctx.moveTo(q[0],q[1]); up=false; } else ctx.lineTo(q[0],q[1]); last=q; } ctx.stroke(); }
function graticule(ctx){ ctx.strokeStyle='rgba(230,230,230,0.22)'; ctx.lineWidth=1; const lm=P[proj].latMax||Math.PI/2;
  for(let l=-180;l<=180;l+=30){ const pts=[]; for(let p=-90;p<=90;p+=1){ const pp=Math.max(-lm,Math.min(lm,p*D2R)); pts.push(fwd(l*D2R,pp)); } line(ctx,pts); }
  for(let p=-60;p<=60;p+=30){ const pts=[]; for(let l=-180;l<=180;l+=1) pts.push(fwd(l*D2R,p*D2R)); line(ctx,pts); } }
function capPts(lon,lat,rkm,n){ const d=rkm/RE; const pts=[]; for(let i=0;i<=n;i++){ const b=i/n*2*Math.PI; const p2=Math.asin(Math.sin(lat)*Math.cos(d)+Math.cos(lat)*Math.sin(d)*Math.cos(b)); const l2=lon+Math.atan2(Math.sin(b)*Math.sin(d)*Math.cos(lat), Math.cos(d)-Math.sin(lat)*Math.sin(p2)); pts.push([((l2+3*Math.PI)%(2*Math.PI))-Math.PI, p2]); } return pts; }
function polyArea(pts){ let a=0; for(let i=0;i<pts.length-1;i++) a+=pts[i][0]*pts[i+1][1]-pts[i+1][0]*pts[i][1]; return Math.abs(a)/2; }
function capRatio(lon,lat,rkm){ const pts=capPts(lon,lat,rkm,72).map(p=>fwd(p[0],p[1])); if(pts.some(p=>!p)) return null; // the projected ring, in units of R squared, against the cap's true area
  let bad=false; for(let i=0;i<pts.length-1;i++) if(Math.hypot(pts[i][0]-pts[i+1][0],pts[i][1]-pts[i+1][1])>1) bad=true; if(bad) return null;
  const d=rkm/RE, n=72, poly=(2*Math.PI/n)/Math.sin(2*Math.PI/n); return polyArea(pts)*poly/(2*Math.PI*(1-Math.cos(d))); }
function drawCap(ctx,lon,lat,rkm,fill,stroke,w){ const pts=capPts(lon,lat,rkm,72).map(p=>toPx(fwd(p[0],p[1]))); if(pts.some(p=>!p)) return false; for(let i=0;i<pts.length-1;i++) if(Math.hypot(pts[i][0]-pts[i+1][0],pts[i][1]-pts[i+1][1])>120) return false;
  ctx.beginPath(); pts.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1])); ctx.closePath(); ctx.fillStyle=fill; ctx.fill(); ctx.strokeStyle=stroke; ctx.lineWidth=w; ctx.stroke(); return true; }
function mapsView(){ const cv=document.createElement('canvas'); fitMap(); cv.width=W; cv.height=M.H; cv.id='mcanvas'; const ctx=cv.getContext('2d'); paintMap(ctx); graticule(ctx);
  for(let l=-150;l<=150;l+=30) for(let p=-60;p<=60;p+=30) drawCap(ctx,l*D2R,p*D2R,500,'rgba(255,176,46,0.28)','rgba(255,176,46,0.8)',1);
  drawCap(ctx,cap.lon*D2R,cap.lat*D2R,capR,'rgba(255,140,106,0.45)','#ffffff',2);
  const c=toPx(fwd(cap.lon*D2R,cap.lat*D2R)); if(c){ ctx.fillStyle='#ffffff'; ctx.beginPath(); ctx.arc(c[0],c[1],3,0,7); ctx.fill(); }
  ctx.fillStyle='#9a9a9a'; ctx.font='11px sans-serif'; ctx.textAlign='left'; ctx.fillText(PROJS.find(p=>p.k===proj).n+': the small circles are 500 km in radius on the globe, the white one 1,000 km, and it drags',12,M.H-10);
  return cv; }

/* ---- the card ---- */
function card(kind,name,rows,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').innerHTML=name;
  document.getElementById('numTxt').innerHTML=rows.filter(r=>r[1]).map(([k,v])=>'<b>'+esc(k)+'</b> '+v).join('<br>');
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').textContent=src;
}
const yr=y=>y<0?(-y)+' BC':y<1000?'about '+y+' AD':String(y);
function showMap(){ const p=PROJS.find(x=>x.k===proj); const r=capRatio(cap.lon*D2R,cap.lat*D2R,capR); const ll=Math.abs(cap.lat).toFixed(1)+'\\u00b0 '+(cap.lat>=0?'N':'S')+', '+Math.abs(cap.lon).toFixed(1)+'\\u00b0 '+(cap.lon>=0?'E':'W');
  card(p.kind+', '+yr(p.year), esc(p.n), [['by',p.who],['the white circle',ll+', '+fmt(capR)+' km in radius, '+fmt(Math.PI*capR*capR/1e6,2)+' million km\\u00b2'],['it appears',r==null?'cut by the edge of the map':fmt(r,2)+' times its true area'+(Math.abs(r-1)<0.02?', which is right':r>1?', swollen':', shrunk')]], p.b, 'Snyder 1987; Snyder 1993; Wikipedia, '+p.n.replace(' tripel',' tripel')+' projection'); }
function areaScale(k,latDeg){ const q=P[k]; const p=latDeg*D2R, l=0, h=1e-4; if(q.latMax&&Math.abs(p)>q.latMax) return null; const a=q.fwd(l,p), b=q.fwd(l+h,p), c=q.fwd(l,p+h); if(!a||!b||!c) return null; const ax=(b[0]-a[0])/h, ay=(b[1]-a[1])/h, bx=(c[0]-a[0])/h, by=(c[1]-a[1])/h; return Math.abs(ax*by-ay*bx)/Math.cos(p); }
function showStretch(){ const rows=[]; for(const k of ['mercator','platecarree','gallpeters','mollweide','robinson','winkel']){ const v=areaScale(k,lat); rows.push([PROJS.find(p=>p.k===k).n, v==null?'off the map':fmt(v,2)+'\\u00d7']); }
  const near=PLACES.filter(p=>Math.abs(p[1]-lat)<2.5).map(p=>p[0]);
  card('At latitude', Math.abs(lat).toFixed(1)+'\\u00b0 '+(lat>=0?'north':'south')+(near.length?', '+near.join(', '):''), rows, 'How many times its true area the map gives a small patch at this latitude, along the central meridian; the equal-area maps give 1 everywhere, Mercator sec\\u00b2 of the latitude, which at 60\\u00b0 is 4 and at 80\\u00b0 is 33. Greenland at 72\\u00b0 north comes out '+fmt(1/Math.cos(GA.greenland_lat*D2R)**2,1)+' times too big on Mercator, and looks the size of Africa, which is '+fmt(GA.africa_km2/GA.greenland_km2,0)+' times larger.', 'Snyder 1987; Wikipedia, Tissot\\u2019s indicatrix'); }
const hav=(a,b)=>{ const [l1,p1]=[a.lon*D2R,a.lat*D2R],[l2,p2]=[b.lon*D2R,b.lat*D2R]; const h=Math.sin((p2-p1)/2)**2+Math.cos(p1)*Math.cos(p2)*Math.sin((l2-l1)/2)**2; return 2*RE*Math.asin(Math.sqrt(h)); };
function rhumb(a,b){ const p1=a.lat*D2R,p2=b.lat*D2R; let dl=(b.lon-a.lon)*D2R; if(Math.abs(dl)>Math.PI) dl=dl>0?dl-2*Math.PI:dl+2*Math.PI; const dpsi=Math.log(Math.tan(Math.PI/4+p2/2)/Math.tan(Math.PI/4+p1/2)); const q=Math.abs(dpsi)>1e-12?(p2-p1)/dpsi:Math.cos(p1); return {d:RE*Math.sqrt((p2-p1)**2+q*q*dl*dl), brg:(Math.atan2(dl,dpsi)*R2D+360)%360}; }
function bearing(a,b){ const [l1,p1]=[a.lon*D2R,a.lat*D2R],[l2,p2]=[b.lon*D2R,b.lat*D2R]; const y=Math.sin(l2-l1)*Math.cos(p2), x=Math.cos(p1)*Math.sin(p2)-Math.sin(p1)*Math.cos(p2)*Math.cos(l2-l1); return (Math.atan2(y,x)*R2D+360)%360; }
function gcPts(a,b,n){ const [l1,p1]=[a.lon*D2R,a.lat*D2R],[l2,p2]=[b.lon*D2R,b.lat*D2R]; const v=[[Math.cos(p1)*Math.cos(l1),Math.cos(p1)*Math.sin(l1),Math.sin(p1)],[Math.cos(p2)*Math.cos(l2),Math.cos(p2)*Math.sin(l2),Math.sin(p2)]]; const w=Math.acos(v[0][0]*v[1][0]+v[0][1]*v[1][1]+v[0][2]*v[1][2]); const out=[]; for(let i=0;i<=n;i++){ const t=i/n, A=Math.sin((1-t)*w)/Math.sin(w), B=Math.sin(t*w)/Math.sin(w); const x=A*v[0][0]+B*v[1][0], y=A*v[0][1]+B*v[1][1], z=A*v[0][2]+B*v[1][2]; out.push([Math.atan2(y,x), Math.atan2(z,Math.hypot(x,y))]); } return out; }
function rhumbPts(a,b,n){ const p1=a.lat*D2R,p2=b.lat*D2R; let dl=(b.lon-a.lon)*D2R; if(Math.abs(dl)>Math.PI) dl=dl>0?dl-2*Math.PI:dl+2*Math.PI; const y1=Math.log(Math.tan(Math.PI/4+p1/2)), y2=Math.log(Math.tan(Math.PI/4+p2/2)); const out=[]; for(let i=0;i<=n;i++){ const t=i/n; const l=a.lon*D2R+dl*t, y=y1+(y2-y1)*t; let ll=l; while(ll>Math.PI) ll-=2*Math.PI; while(ll<-Math.PI) ll+=2*Math.PI; out.push([ll, 2*Math.atan(Math.exp(y))-Math.PI/2]); } return out; }
function showRoute(){ const [ka,kb]=ROUTES[route]; const a=CITIES[ka], b=CITIES[kb]; const g=hav(a,b), r=rhumb(a,b);
  card('A route', esc(a.n)+' to '+esc(b.n), [['the great circle',fmt(g)+' km, setting out on a bearing of '+fmt(bearing(a,b))+'\\u00b0 and turning all the way'],['the compass course',fmt(r.d)+' km, a constant '+fmt(r.brg)+'\\u00b0'],['the detour',fmt(r.d-g)+' km, '+fmt((r.d/g-1)*100,1)+'% longer']], 'The great circle is the shortest path on the sphere, and on Mercator\\u2019s map it bows toward the pole; the rhumb line holds one compass bearing and is straight on Mercator, which is why navigators liked the map and why aircraft do not fly along it.', 'Wikipedia, Great-circle distance; Wikipedia, Rhumb line'); }

/* ---- the stretch ---- */
const S={x:80,y:40,w:820,h:480,lo:0.5,hi:100};
const SX=l=>S.x+Math.abs(l)/90*S.w, SY=v=>S.y+S.h-Math.log(v/S.lo)/Math.log(S.hi/S.lo)*S.h;
const COLS={mercator:'#ff8c6a',platecarree:'#ffb02e',gallpeters:'#9be564',mollweide:'#6ee7f2',robinson:'#c9a6ff',winkel:'#58a6ff'};
function stretchView(){ let s='';
  for(const v of [0.5,1,2,5,10,20,50,100]){ const y=SY(v); s+='<line x1="'+S.x+'" y1="'+y.toFixed(1)+'" x2="'+(S.x+S.w)+'" y2="'+y.toFixed(1)+'" stroke="'+(v===1?'#3d444d':'#2b2b2b')+'"/><text x="'+(S.x-8)+'" y="'+(y+4).toFixed(1)+'" text-anchor="end" font-size="10.5" fill="#9a9a9a">'+v+'\\u00d7</text>'; }
  for(const l of [0,15,30,45,60,75,90]){ const x=SX(l); s+='<line x1="'+x.toFixed(1)+'" y1="'+(S.y+S.h)+'" x2="'+x.toFixed(1)+'" y2="'+(S.y+S.h+6)+'" stroke="#8a94a6"/><text x="'+x.toFixed(1)+'" y="'+(S.y+S.h+22)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+l+'\\u00b0</text>'; }
  s+='<text x="'+(S.x+S.w/2)+'" y="'+(S.y+S.h+44)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">latitude, north or south</text><text transform="translate(18,'+(S.y+S.h/2)+') rotate(-90)" text-anchor="middle" font-size="11" fill="#9a9a9a">area on the map against area on the globe, log scale</text>';
  for(const k of Object.keys(COLS)){ let d=''; let lastx=null; for(let l=0;l<=89.5;l+=0.5){ const v=areaScale(k,l); if(v==null||v>S.hi||v<S.lo){ continue; } d+=(d?'L':'M')+SX(l).toFixed(1)+','+SY(v).toFixed(1); lastx=l; } const on=hot===k; s+='<path data-proj="'+k+'" d="'+d+'" fill="none" stroke="'+COLS[k]+'" stroke-width="'+(on?3.4:2)+'" style="cursor:pointer"/>';
    const lv=areaScale(k,lastx); const lx=SX(lastx), ly=SY(Math.min(S.hi,lv)); s+='<text data-lbl="'+k+'" x="'+(lx+6).toFixed(1)+'" y="'+(ly+4).toFixed(1)+'" font-size="10.5" fill="'+COLS[k]+'">'+esc(PROJS.find(p=>p.k===k).n)+'</text>'; }
  for(const [n,l] of PLACES){ const x=SX(l); s+='<line x1="'+x.toFixed(1)+'" y1="'+(S.y+S.h)+'" x2="'+x.toFixed(1)+'" y2="'+(S.y+S.h-8)+'" stroke="#e6e6e6"/><text transform="translate('+(x+4).toFixed(1)+','+(S.y+S.h-12)+') rotate(-90)" font-size="9.5" fill="#c8c8c8">'+esc(n)+'</text>'; }
  const mx=SX(lat); s+='<g id="marker" style="cursor:ew-resize"><line x1="'+mx.toFixed(1)+'" y1="'+S.y+'" x2="'+mx.toFixed(1)+'" y2="'+(S.y+S.h)+'" stroke="#ffffff" stroke-width="1.5"/>';
  for(const k of Object.keys(COLS)){ const v=areaScale(k,lat); if(v!=null&&v<=S.hi) s+='<circle cx="'+mx.toFixed(1)+'" cy="'+SY(v).toFixed(1)+'" r="5" fill="'+COLS[k]+'" stroke="#121212" stroke-width="1.5"/>'; }
  s+='<text x="'+mx.toFixed(1)+'" y="'+(S.y-10)+'" text-anchor="middle" font-size="11.5" font-weight="700" fill="#ffffff">'+Math.abs(lat).toFixed(1)+'\\u00b0</text></g>';
  return {svg:s, h:S.y+S.h+60}; }
function fixLabels(){ const ts=[...document.querySelectorAll('#psvg text[data-lbl]')].map(t=>({t,b:t.getBBox()})).sort((a,b)=>a.b.y-b.b.y); for(let i=1;i<ts.length;i++){ const prev=ts[i-1].b, cur=ts[i]; if(cur.b.x<prev.x+prev.width&&cur.b.y<prev.y+prev.height+2){ const ny=prev.y+prev.height+3; cur.t.setAttribute('y',(ny+cur.b.height-3).toFixed(1)); cur.b=cur.t.getBBox(); } } }

/* ---- the routes ---- */
function routesView(){ const cv=document.createElement('canvas'); cv.width=W; cv.height=470; cv.id='rcanvas'; const ctx=cv.getContext('2d'); const [ka,kb]=ROUTES[route]; const a=CITIES[ka], b=CITIES[kb];
  // left: Mercator to 80 degrees
  const save={proj,center}; proj='mercator'; const LM=80*D2R; const mw=520, mh=Math.round(mw/(2*Math.PI)*2*Math.log(Math.tan(Math.PI/4+LM/2))), mx0=20, my0=(470-mh)/2-10;
  const mp=(l,p)=>[mx0+(l+Math.PI)/(2*Math.PI)*mw, my0+mh/2-Math.log(Math.tan(Math.PI/4+Math.max(-LM,Math.min(LM,p))/2))/Math.log(Math.tan(Math.PI/4+LM/2))*mh/2];
  const im=ctx.createImageData(mw,mh), d=im.data; for(let py=0;py<mh;py++) for(let px=0;px<mw;px++){ const l=(px+0.5)/mw*2*Math.PI-Math.PI; const yy=(mh/2-(py+0.5))/(mh/2)*Math.log(Math.tan(Math.PI/4+LM/2)); const p=2*Math.atan(Math.exp(yy))-Math.PI/2; const c=isLand(l,p)?[70,74,78]:[16,28,46]; const i=(py*mw+px)*4; d[i]=c[0]; d[i+1]=c[1]; d[i+2]=c[2]; d[i+3]=255; } ctx.putImageData(im,mx0,my0);
  ctx.strokeStyle='rgba(230,230,230,0.2)'; ctx.lineWidth=1; for(let l=-180;l<=180;l+=30){ const q=mp(l*D2R,0); ctx.beginPath(); ctx.moveTo(q[0],my0); ctx.lineTo(q[0],my0+mh); ctx.stroke(); } for(let p=-60;p<=60;p+=30){ const q=mp(0,p*D2R); ctx.beginPath(); ctx.moveTo(mx0,q[1]); ctx.lineTo(mx0+mw,q[1]); ctx.stroke(); }
  const drawPath=(pts,map,col,w,dash)=>{ ctx.strokeStyle=col; ctx.lineWidth=w; ctx.setLineDash(dash||[]); ctx.beginPath(); let last=null; for(const p of pts){ const q=map(p[0],p[1]); if(!q){ last=null; continue; } if(last&&Math.hypot(q[0]-last[0],q[1]-last[1])>80) last=null; last?ctx.lineTo(q[0],q[1]):ctx.moveTo(q[0],q[1]); last=q; } ctx.stroke(); ctx.setLineDash([]); };
  drawPath(rhumbPts(a,b,100),mp,'#ffb02e',2.2,[6,4]); drawPath(gcPts(a,b,100),mp,'#ff8c6a',2.6);
  // right: the globe centered on the midpoint of the great circle
  const mid=gcPts(a,b,2)[1]; const gx=780, gy=225, gr=185; const l0=mid[0], p0=mid[1];
  const gp=(l,p)=>{ const c=Math.sin(p0)*Math.sin(p)+Math.cos(p0)*Math.cos(p)*Math.cos(l-l0); if(c<0) return null; return [gx+gr*Math.cos(p)*Math.sin(l-l0), gy-gr*(Math.cos(p0)*Math.sin(p)-Math.sin(p0)*Math.cos(p)*Math.cos(l-l0))]; };
  const gim=ctx.createImageData(2*gr,2*gr), gd=gim.data; for(let py=0;py<2*gr;py++) for(let px=0;px<2*gr;px++){ const x=(px+0.5-gr)/gr, y=-(py+0.5-gr)/gr; const r=Math.hypot(x,y); const i=(py*2*gr+px)*4; if(r>1){ gd[i]=18; gd[i+1]=18; gd[i+2]=18; gd[i+3]=255; continue; } const c=Math.asin(r); const p=r<1e-9?p0:Math.asin(Math.cos(c)*Math.sin(p0)+y*Math.sin(c)*Math.cos(p0)/r); const l=r<1e-9?l0:l0+Math.atan2(x*Math.sin(c), r*Math.cos(c)*Math.cos(p0)-y*Math.sin(c)*Math.sin(p0)); const cc=isLand(l,p)?[70,74,78]:[16,28,46]; gd[i]=cc[0]; gd[i+1]=cc[1]; gd[i+2]=cc[2]; gd[i+3]=255; } ctx.putImageData(gim,gx-gr,gy-gr);
  ctx.strokeStyle='rgba(230,230,230,0.2)'; for(let l=-180;l<180;l+=30){ const pts=[]; for(let p=-90;p<=90;p+=2) pts.push([l*D2R,p*D2R]); drawPath(pts,gp,'rgba(230,230,230,0.2)',1); } for(let p=-60;p<=60;p+=30){ const pts=[]; for(let l=-180;l<=180;l+=2) pts.push([l*D2R,p*D2R]); drawPath(pts,gp,'rgba(230,230,230,0.2)',1); }
  ctx.strokeStyle='#e6e6e6'; ctx.lineWidth=1; ctx.beginPath(); ctx.arc(gx,gy,gr,0,7); ctx.stroke();
  drawPath(rhumbPts(a,b,200),gp,'#ffb02e',2.2,[6,4]); drawPath(gcPts(a,b,100),gp,'#ff8c6a',2.6);
  ctx.font='11px sans-serif'; for(const [c,map] of [[a,mp],[b,mp],[a,gp],[b,gp]]){ const q=map(c.lon*D2R,c.lat*D2R); if(!q) continue; ctx.fillStyle='#ffffff'; ctx.beginPath(); ctx.arc(q[0],q[1],3.5,0,7); ctx.fill(); ctx.textAlign='left'; ctx.fillStyle='#e6e6e6'; ctx.fillText(c.n,q[0]+7,q[1]-6); }
  ctx.fillStyle='#9a9a9a'; ctx.textAlign='left'; ctx.fillText('Mercator: the compass course is the straight dashed line; the great circle bows poleward',mx0,my0+mh+18); ctx.textAlign='center'; ctx.fillText('the globe, turned to the route: the great circle is the straight one',gx,gy+gr+22);
  proj=save.proj; center=save.center; return cv; }

/* ---- render and wiring ---- */
function render(){ el.innerHTML=''; if(view==='maps') el.appendChild(mapsView()); else if(view==='routes') el.appendChild(routesView()); else { const q=stretchView(); el.innerHTML='<svg viewBox="0 0 '+W+' '+q.h+'" xmlns="http://www.w3.org/2000/svg" id="psvg"><rect width="'+W+'" height="'+q.h+'" fill="#121212"/>'+q.svg+'</svg>'; fixLabels(); }
  document.getElementById('mapCtl').hidden=view!=='maps'; document.getElementById('centreCtl').hidden=!(view==='maps'&&proj==='ortho'); document.getElementById('stretchCtl').hidden=view!=='stretch'; document.getElementById('routeCtl').hidden=view!=='routes'; document.getElementById('latOut').textContent=Math.abs(lat).toFixed(1)+'\\u00b0'; }
function home(){ if(view==='maps') showMap(); else if(view==='stretch') showStretch(); else showRoute(); }
function setView(v){ view=v; hot=null; for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on',b.dataset.v===v); render(); home(); }
document.getElementById('views').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setView(b.dataset.v); });
(function(){ const box=document.getElementById('projs'); box.innerHTML=PROJS.map(p=>'<button data-p="'+p.k+'"'+(p.k===proj?' class="on"':'')+'>'+esc(p.n)+'</button>').join(''); box.addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; proj=b.dataset.p; for(const x of box.querySelectorAll('button')) x.classList.toggle('on',x===b); render(); showMap(); });
  const rb=document.getElementById('routes'); rb.innerHTML=ROUTES.map((r,i)=>'<button data-r="'+i+'"'+(i===route?' class="on"':'')+'>'+esc(CITIES[r[0]].n)+' to '+esc(CITIES[r[1]].n)+'</button>').join(''); rb.addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; route=+b.dataset.r; for(const x of rb.querySelectorAll('button')) x.classList.toggle('on',x===b); render(); showRoute(); });
  document.getElementById('centers').addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; center=b.dataset.c; for(const x of document.querySelectorAll('#centers button')) x.classList.toggle('on',x===b); render(); showMap(); }); })();
let dragging=false;
const pt=e=>{ const c=el.firstElementChild, b=c.getBoundingClientRect(); const vh=c.tagName==='CANVAS'?c.height:c.viewBox.baseVal.height; return [(e.clientX-b.left)/b.width*W,(e.clientY-b.top)/b.height*vh]; };
function setCap(px,py){ const [x,y]=fromPx(px,py); const r=P[proj].inv(x,y); if(!r||Math.abs(r[1])>Math.PI/2||Math.abs(r[0])>Math.PI) return; if(P[proj].latMax&&Math.abs(r[1])>P[proj].latMax) return; cap={lon:r[0]*R2D,lat:r[1]*R2D}; render(); showMap(); }
function setLat(x){ lat=Math.round(Math.max(0,Math.min(89.9,(x-S.x)/S.w*90))*10)/10; render(); showStretch(); }
el.addEventListener('pointerdown',e=>{ const [x,y]=pt(e); if(view==='maps'){ dragging=true; setCap(x,y); e.preventDefault(); } if(view==='stretch'&&x>=S.x-10&&x<=S.x+S.w+10){ dragging=true; setLat(x); e.preventDefault(); } });
el.addEventListener('pointermove',e=>{ if(!dragging) return; const [x,y]=pt(e); if(view==='maps') setCap(x,y); else if(view==='stretch') setLat(x); });
window.addEventListener('pointerup',()=>{ dragging=false; });
el.addEventListener('pointerover',e=>{ if(dragging||view!=='stretch') return; const g=e.target.closest('[data-proj]'); if(!g) return; const k=g.getAttribute('data-proj'); if(k===hot) return; hot=k; render(); const p=PROJS.find(x=>x.k===k); card(p.kind+', '+yr(p.year), esc(p.n), [['at '+Math.abs(lat).toFixed(1)+'\\u00b0',fmt(areaScale(k,lat)||0,2)+' times the true area'],['at 60\\u00b0',fmt(areaScale(k,60),2)+'\\u00d7'],['at 80\\u00b0',(areaScale(k,80)||0)>0?fmt(areaScale(k,80),1)+'\\u00d7':'off the map']], p.b, 'Snyder 1987'); });
el.addEventListener('pointerleave',()=>{ if(hot){ hot=null; render(); home(); } });

function decode(b64,w,h,cb){ const img=new Image(); img.onload=()=>{ const off=document.createElement('canvas'); off.width=w; off.height=h; const o=off.getContext('2d'); o.drawImage(img,0,0); const d=o.getImageData(0,0,w,h).data; const a=new Uint8Array(w*h); for(let i=0,p=0;i<d.length;i+=4,p++) a[p]=d[i]; cb(a); }; img.src='data:image/png;base64,'+b64; }
decode(LAND,LW,LH,a=>{ land=a; cache={}; render(); home(); });
render(); showMap();
window.__proj=(q)=>{ const o={view,proj,center,cap,lat,route,land:!!land,card:document.getElementById('numTxt').innerText,name:document.getElementById('nameTxt').innerText,body:document.getElementById('bodyTxt').innerText};
  if(q&&q.fwd){ const save=proj; if(q.proj) proj=q.proj; o.fwd=P[proj].fwd(q.fwd[0]*D2R,q.fwd[1]*D2R); o.inv=o.fwd?P[proj].inv(o.fwd[0],o.fwd[1]):null; if(o.inv) o.inv=o.inv.map(v=>v*R2D); proj=save; }
  if(q&&q.ratio){ const save=proj; if(q.proj) proj=q.proj; o.ratio=capRatio(q.ratio[0]*D2R,q.ratio[1]*D2R,q.ratio[2]||capR); proj=save; }
  if(q&&q.scale) o.scale=areaScale(q.scale[0],q.scale[1]);
  if(q&&q.route){ const [ka,kb]=q.route; o.gc=hav(CITIES[ka],CITIES[kb]); o.rh=rhumb(CITIES[ka],CITIES[kb]).d; o.brg=bearing(CITIES[ka],CITIES[kb]); }
  if(q&&q.land) o.isLand=q.land.map(([lo,la])=>isLand(lo*D2R,la*D2R));
  if(q&&q.px){ const c=document.getElementById('mcanvas'); if(c){ const d=c.getContext('2d').getImageData(q.px[0],q.px[1],1,1).data; o.pixel=[d[0],d[1],d[2]]; } o.ll=(()=>{ const [x,y]=fromPx(q.px[0],q.px[1]); const r=P[proj].inv(x,y); return r?r.map(v=>v*R2D):null; })(); }
  if(view==='stretch'){ const m=document.querySelector('#marker line'); o.marker=m?+m.getAttribute('x1'):null; o.sx=SX(lat); o.curves=document.querySelectorAll('#psvg path[data-proj]').length; }
  return o; };
</script>
</body>
</html>
"""

html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__PROJS__", _js(projs)).replace("__ROB__", _js(ROBINSON)).replace("__PLACES__", _js(PLACES)).replace("__GA__", _js(GREENLAND_AFRICA)).replace("__CITIES__", _js(cities)).replace("__ROUTES__", _js(ROUTES))
        .replace("__LAND__", _js(GEO["land"])).replace("__LW__", str(GEO["landW"])).replace("__LH__", str(GEO["landH"])).replace("__RE__", str(R_EARTH))
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(PROJECTIONS)} projections, {len(ROUTES)} routes")
