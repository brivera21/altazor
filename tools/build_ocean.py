#!/usr/bin/env python3
"""Generate ocean.html, Ocean Currents: the surface currents and the gyres
they make, and the great conveyor beneath.

Two views. The surface: the major currents on an equirectangular map, warm
in red and cold in blue, moving as animated dashes in the direction of flow,
grouped into the five gyres; a current under the pointer gives its
transport, speed and story, and a gyre button lights its currents and says
which way it turns and why. The conveyor: the deep, cold return of the
overturning circulation and the warm surface path that closes it, with the
sinking and the rising marked.

Data: tools/ocean_data.py, and the land mask in tools/data/plates.json.

Usage: python3 build_ocean.py
"""

import json
from pathlib import Path

import apa
from ocean_data import CURRENTS, GYRES, CONVEYOR, CONVEYOR_NOTE, REFS

ROOT = Path(__file__).parent.parent
OUT = ROOT / "ocean.html"
GEO = json.loads((ROOT / "tools" / "data" / "plates.json").read_text())

NOTE1 = ("The wind drags the sea's surface, the Earth's turning bends the "
         "drift right in the north and left in the south, and the continents"
         " block it. The result is five great rings, clockwise in the north "
         "and counterclockwise in the south, each fast and warm on its "
         "western side, slow and cool on its eastern. A click drops a float.")

NOTE2 = ("Under the surface there is a slower circulation. Water that "
         "reaches the far North Atlantic is cold and salty enough to sink, "
         "and it creeps along the ocean floor for centuries before rising "
         "in the Indian and Pacific oceans and returning at the surface. "
         "The second view follows it round. The big currents say how much "
         "water they move, in sverdrups: a million cubic meters a second, "
         "about five Amazons.")

METHOD = ("The currents are drawn by hand from the standard maps as a few "
          "points each and are schematic; the real ones meander, shed "
          "eddies, and shift with the seasons, and the northern Indian "
          "Ocean reverses with the monsoon and is left out. Transports are "
          "those the cited articles give, so most currents have none. The "
          "animation moves the dashes at one speed for all currents and "
          "says nothing about how fast each one flows. The float rides the "
          "drawn path at that one speed too, and joins whichever current "
          "begins within about 1,500 km of where its current ends, so the "
          "kilometers it counts are along the drawn paths and the days "
          "are not counted at all. The conveyor is "
          "Broecker's cartoon, with the Southern Ocean return that later "
          "work added; the true circulation is a tangle of many paths, and "
          "this is the one that survives the averaging. The map is "
          "equirectangular, cut at 85 north and 78 south, so high "
          "latitudes are stretched.")


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


currents = [{"k": k, "n": n, "w": w, "p": p, "g": g, "sv": sv, "v": v, "b": b, "s": s} for k, n, w, p, g, sv, v, b, s in CURRENTS]
gyres = [{"k": k, "n": n, "sense": sense, "c": c, "b": b} for k, n, sense, c, b in GYRES]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ocean Currents &middot; Altazor</title>
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
.bar button, .presets button { background:var(--panel); color:var(--muted); border:1px solid var(--line);
  border-radius:999px; padding:6px 14px; font-size:13px; cursor:pointer; font-family:inherit; }
.bar button.on, .presets button.on { background:var(--accent); color:#0b1a2b; border-color:var(--accent); font-weight:600; }
.bar button:hover, .presets button:hover { color:var(--text); border-color:#3d3d3d; }
.bar button.on:hover, .presets button.on:hover { color:#0b1a2b; }
.controls { display:flex; align-items:center; gap:12px; flex-wrap:wrap; margin:0 0 12px; min-height:34px; }
.controls label { font-size:13px; color:var(--muted); }
.presets { display:flex; gap:6px; flex-wrap:wrap; }
.presets button { padding:5px 11px; font-size:12.5px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; }
#diagram canvas { width:100%; height:auto; display:block; user-select:none; cursor:crosshair; border-radius:6px; }
.legend { display:flex; gap:14px; flex-wrap:wrap; margin-top:8px; font-size:12px; color:var(--muted); }
.legend span { display:inline-flex; align-items:center; gap:6px; }
.legend i { display:inline-block; width:18px; height:3px; border-radius:2px; }
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
details.sources { margin-top:14px; max-width:760px; color:var(--muted); font-size:12.5px; }
details.sources > summary { cursor:pointer; font-size:12px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }
details.sources > summary:hover { color:var(--accent); }
details.sources .note { border-top:none; padding-top:0; margin-top:10px; }
#floatBtn { display:none; }
#floatBtn.show { display:inline-block; }
@media (max-width:900px){ .stage{flex-direction:column;} #diagram{flex:0 0 auto; width:100%;} .side{position:static; width:100%;} }
@media (max-width:600px){ .stage{flex-direction:column-reverse;} #diagram{overflow-x:auto;} #diagram canvas{min-width:700px;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library &middot; Earth</a><a href="atmosphere.html">The Atmosphere</a><a href="earth.html">Climate</a><a href="plates.html">Tectonic Plates</a></nav>
</header>
<h1>Ocean Currents</h1>
<div class="bar" id="views"><button data-v="surface" class="on">The surface</button><button data-v="conveyor">The conveyor</button><button type="button" id="floatBtn">Take the float out</button></div>
<div class="controls" id="gyreCtl">
  <label>the gyres</label>
  <span class="presets" id="gyres"></span>
</div>
<div class="stage">
  <div id="diagram">
    <canvas id="map" width="980" height="444" aria-label="the surface currents; a click on the sea drops a float that rides them"></canvas>
    <div class="legend" id="legend"></div>
  </div>
  <div class="side"><div class="card">
    <div id="kindTxt"></div>
    <div id="nameTxt"></div>
    <div id="numTxt"></div>
    <div id="bodyTxt"></div>
    <div id="srcTxt"></div>
  </div></div>
</div>
<p class="note">__NOTE1__</p>
<details class="sources"><summary>Sources</summary>
<p class="note">__NOTE2__</p>
<div class="method"><p>__METHOD__</p></div>
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</details>
</div>
<script>
const CUR=__CUR__, GYRES=__GYRES__, CONV=__CONV__, CONVNOTE=__CONVNOTE__, LAND=__LAND__, LW=__LW__, LH=__LH__;
const W=980, LAT_TOP=85, LAT_BOT=-78, H=Math.round(W*(LAT_TOP-LAT_BOT)/360), WARM='#f28cb0', COLD='#7cc4ff';
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const RM=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const ease=t=>t<0.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
const cv=document.getElementById('map'), ctx=cv.getContext('2d');
let view='surface', quiet=null, land=null, base=null, hot=null, gyre=null, t0=performance.now(), anim=true;
let tv=0, tvFrom=0, tvTo=0, tvT0=0, tvDur=1400;                 // 0: the surface; 1: the conveyor, drawn as the view changes
const X=lon=>(lon+180)/360*W, Y=lat=>(LAT_TOP-lat)/(LAT_TOP-LAT_BOT)*H;
const LON=x=>x/W*360-180, LAT=y=>LAT_TOP-y/H*(LAT_TOP-LAT_BOT);

/* ---- a smooth path through the points: Catmull-Rom, sampled ---- */
function smooth(pts,n){ const out=[]; const P=pts.map(([lo,la])=>[X(lo),Y(la)]);
  for(let i=0;i<P.length-1;i++){ const p0=P[Math.max(0,i-1)], p1=P[i], p2=P[i+1], p3=P[Math.min(P.length-1,i+2)];
    if(Math.abs(p2[0]-p1[0])>W/2){ out.push(null); continue; }         // the dateline: break the path
    for(let k=0;k<(n||8);k++){ const t=k/(n||8), t2=t*t, t3=t2*t;
      out.push([0.5*((2*p1[0])+(-p0[0]+p2[0])*t+(2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2+(-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3),
                0.5*((2*p1[1])+(-p0[1]+p2[1])*t+(2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2+(-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)]); } }
  out.push(P[P.length-1]); return out; }
const PATHS=CUR.map(c=>smooth(c.p));
const CPATHS={}; for(const k in CONV) CPATHS[k]=smooth(CONV[k],10);

/* ---- the land ---- */
function decode(b64,w,h,cb){ const img=new Image(); img.onload=()=>{ const off=document.createElement('canvas'); off.width=w; off.height=h; const o=off.getContext('2d'); o.drawImage(img,0,0); const d=o.getImageData(0,0,w,h).data; const a=new Uint8Array(w*h); for(let i=0,p=0;i<d.length;i+=4,p++) a[p]=d[i]; cb(a); }; img.src='data:image/png;base64,'+b64; }
function paintBase(){ const im=ctx.createImageData(W,H), d=im.data;
  for(let y=0;y<H;y++) for(let x=0;x<W;x++){ const lx=Math.floor(x/W*LW), ly=Math.floor((90-LAT(y+0.5))/180*LH), isLand=land[ly*LW+lx]>0; const p=(y*W+x)*4;
    if(isLand){ d[p]=58; d[p+1]=62; d[p+2]=66; } else { d[p]=14; d[p+1]=24; d[p+2]=38; } d[p+3]=255; }
  base=im; }
const isSea=(lon,lat)=>{ if(!land) return true; const lx=Math.floor((lon+180)/360*LW), ly=Math.floor((90-lat)/180*LH); return land[ly*LW+lx]===0; };

/* ---- drawing ---- */
function strokePath(pts,col,width,dash,off,alpha){ ctx.strokeStyle=col; ctx.lineWidth=width; ctx.globalAlpha=alpha; ctx.setLineDash(dash||[]); ctx.lineDashOffset=off||0; ctx.lineCap='round'; ctx.lineJoin='round';
  ctx.beginPath(); let up=true; for(const q of pts){ if(!q){ up=true; continue; } if(up){ ctx.moveTo(q[0],q[1]); up=false; } else ctx.lineTo(q[0],q[1]); } ctx.stroke(); ctx.setLineDash([]); ctx.globalAlpha=1; }
function arrowHead(pts,col,size,alpha){ let b=pts[pts.length-1], a=null; for(let i=pts.length-2;i>=0;i--){ if(pts[i]){ a=pts[i]; break; } } if(!a) return;
  const ang=Math.atan2(b[1]-a[1],b[0]-a[0]); ctx.fillStyle=col; ctx.globalAlpha=alpha; ctx.beginPath(); ctx.moveTo(b[0],b[1]); ctx.lineTo(b[0]-size*Math.cos(ang-0.5),b[1]-size*Math.sin(ang-0.5)); ctx.lineTo(b[0]-size*Math.cos(ang+0.5),b[1]-size*Math.sin(ang+0.5)); ctx.closePath(); ctx.fill(); ctx.globalAlpha=1; }
function label(text,x,y,col,alpha){ ctx.font='10.5px -apple-system,Helvetica,Arial,sans-serif'; ctx.globalAlpha=alpha; ctx.fillStyle='rgba(18,18,18,0.6)'; const w=ctx.measureText(text).width; x=Math.max(w/2+4,Math.min(W-w/2-4,x)); ctx.fillRect(x-w/2-3,y-9,w+6,13); ctx.fillStyle=col; ctx.textAlign='center'; ctx.fillText(text,x,y+1); ctx.textAlign='start'; ctx.globalAlpha=1; }
function paint(now){
  if(!base) return; ctx.putImageData(base,0,0);
  ctx.strokeStyle='rgba(255,255,255,0.05)'; ctx.lineWidth=1;
  for(let lon=-150;lon<=150;lon+=30){ ctx.beginPath(); ctx.moveTo(X(lon),0); ctx.lineTo(X(lon),H); ctx.stroke(); }
  for(let lat=-60;lat<=60;lat+=30){ ctx.beginPath(); ctx.moveTo(0,Y(lat)); ctx.lineTo(W,Y(lat)); ctx.stroke(); }
  const off=-((now-t0)/40)%24;
  if(tvT0){ const u=Math.min(1,(now-tvT0)/tvDur); tv=tvFrom+(tvTo-tvFrom)*ease(u); if(u>=1) tvT0=0; }
  const sa=1-tv, cp=tv;                                          // surface alpha, conveyor progress
  if(sa>0){ ctx.save(); ctx.globalAlpha=1;
    CUR.forEach((c,i)=>{ const col=c.w==='warm'?WARM:COLD; const lit=hot?hot===c.k:gyre?c.g===gyre:true; const a=(lit?1:0.22)*sa;
      strokePath(PATHS[i],col,lit&&(hot||gyre)?4:2.6,[],0,a*0.55); strokePath(PATHS[i],'#f4efe2',lit&&(hot||gyre)?2:1.4,[6,18],off,a*0.9); arrowHead(PATHS[i],col,lit&&(hot||gyre)?11:8,a); });
    CUR.forEach((c,i)=>{ const lit=hot?hot===c.k:gyre?c.g===gyre:true; if(!lit&&(hot||gyre)) return; const m=PATHS[i][Math.floor(PATHS[i].length/2)]||PATHS[i][0]; if(m) label(c.n.replace(/^the /,''),m[0],m[1]-13,c.w==='warm'?'#ffd0e0':'#bcd8ff',sa); });
    if(gyre){ const g=GYRES.find(x=>x.k===gyre); ctx.globalAlpha=sa; ctx.strokeStyle='#ffb02e'; ctx.setLineDash([4,4]); ctx.lineWidth=1.2; ctx.beginPath(); ctx.ellipse(X(g.c[0]),Y(g.c[1]),18,12,0,0,Math.PI*2); ctx.stroke(); ctx.setLineDash([]);
      const cw=g.sense==='clockwise'; ctx.fillStyle='#ffb02e'; ctx.font='16px sans-serif'; ctx.textAlign='center'; ctx.fillText(cw?'\u21bb':'\u21ba',X(g.c[0]),Y(g.c[1])+6); ctx.textAlign='start'; ctx.globalAlpha=1; }
    if(F.on) paintFloat(now,sa);
    ctx.restore(); }
  if(cp>0){
    const part=(pts,a,b)=>{ const u=Math.max(0,Math.min(1,(cp-a)/(b-a))); return u>=1?pts:pts.slice(0,Math.max(2,Math.round(pts.length*u))); };
    const seg=(k,col,a,b)=>{ const pts=part(CPATHS[k],a,b); strokePath(pts,col,7,[],0,0.35); strokePath(pts,col,3,[8,14],off,0.95); if(pts.length===CPATHS[k].length) arrowHead(pts,col,12,1); };
    seg('deep',COLD,0,0.5); seg('deep_indian',COLD,0.3,0.5); seg('surface',WARM,0.5,1); seg('surface_indian',WARM,0.5,0.7);
    for(const [lon,lat,txt,at] of [[-35,62,'sinks',0],[2,70,'sinks',0],[-160,40,'rises',0.5],[68,5,'rises',0.5]]){ if(cp<at) continue; ctx.fillStyle=txt==='sinks'?COLD:WARM; ctx.beginPath(); ctx.arc(X(lon),Y(lat),7,0,Math.PI*2); ctx.fill(); label(txt,X(lon),Y(lat)-14,'#e6e6e6',1); }
    if(cp>=0.5) label('cold and deep',X(-25),Y(-20)+16,'#bcd8ff',1); if(cp>=0.7) label('warm, at the surface',X(-20),Y(-2)-12,'#ffd0e0',1);
    label(cp<1?'year '+Math.round(cp*1000).toLocaleString('en-US')+' of about a thousand':'about a thousand years round',X(-120),Y(-70),'#9a9a9a',1);
  }
}
/* ---- the float: dropped by a click, it rides the drawn currents at the animation's one speed ---- */
const F={on:false,i:-1,j:0,f:0,x:0,y:0,km:0,ridden:[],start:-1,done:'',last:0,speed:45};   // speed in map pixels per second
const R_E=6371;
function hav(lo1,la1,lo2,la2){ const r=Math.PI/180, a=Math.sin((la2-la1)*r/2)**2+Math.cos(la1*r)*Math.cos(la2*r)*Math.sin((lo2-lo1)*r/2)**2; return 2*R_E*Math.asin(Math.sqrt(a)); }
function nearestPoint(px,py,maxd){ let best=null, bd=maxd; PATHS.forEach((pts,i)=>{ for(let j=1;j<pts.length;j++){ const a=pts[j-1], b=pts[j]; if(!a||!b) continue; const dx=b[0]-a[0], dy=b[1]-a[1], l2=dx*dx+dy*dy||1; let t=((px-a[0])*dx+(py-a[1])*dy)/l2; t=Math.max(0,Math.min(1,t)); const d=Math.hypot(px-(a[0]+t*dx),py-(a[1]+t*dy)); if(d<bd){ bd=d; best={i,j,f:t}; } } }); return best; }
function dropFloat(px,py){ const n=nearestPoint(px,py,40); if(!n) return false; const a=PATHS[n.i][n.j-1], b=PATHS[n.i][n.j];
  Object.assign(F,{on:true,i:n.i,j:n.j,f:n.f,x:a[0]+(b[0]-a[0])*n.f,y:a[1]+(b[1]-a[1])*n.f,km:0,ridden:[CUR[n.i].k],start:n.i,done:'',last:performance.now()});
  document.getElementById('floatBtn').classList.add('show'); if(RM){ while(!F.done) stepFloat(1); } refreshCard(); return true; }
function clearFloat(){ F.on=false; F.done=''; document.getElementById('floatBtn').classList.remove('show'); refreshCard(); }
const firstPt=pts=>pts.find(q=>q), lastPt=pts=>{ for(let j=pts.length-1;j>=0;j--) if(pts[j]) return pts[j]; return null; };
function nextCurrent(i){ const e=lastPt(PATHS[i]); let best=-1, bd=40; if(!e) return best;
  CUR.forEach((c,k)=>{ const s0=firstPt(PATHS[k]); if(!s0) return; let dx=Math.abs(s0[0]-e[0]); dx=Math.min(dx,W-dx); const d=Math.hypot(dx,s0[1]-e[1]) - (c.g&&c.g===CUR[i].g?6:0); if(d<bd&&!(k===i&&dx>1)){ bd=d; best=k; } });
  return best; }
function stepFloat(dt){ if(!F.on||F.done) return; let left=F.speed*dt; const pts=PATHS[F.i];
  while(left>0){ let a=pts[F.j-1], b=pts[F.j];
    if(!a||!b){ // the dateline break: hop to the next drawn segment
      F.j++; while(F.j<pts.length&&(!pts[F.j-1]||!pts[F.j])) F.j++; if(F.j>=pts.length){ if(!endOfPath()) return; continue; } F.f=0; a=pts[F.j-1]; b=pts[F.j]; F.x=a[0]; F.y=a[1]; }
    const L=Math.hypot(b[0]-a[0],b[1]-a[1])||1e-6, rem=(1-F.f)*L;
    if(left<rem){ const f2=F.f+left/L, nx=a[0]+(b[0]-a[0])*f2, ny=a[1]+(b[1]-a[1])*f2; F.km+=hav(LON(F.x),LAT(F.y),LON(nx),LAT(ny)); F.f=f2; F.x=nx; F.y=ny; left=0; }
    else { F.km+=hav(LON(F.x),LAT(F.y),LON(b[0]),LAT(b[1])); F.x=b[0]; F.y=b[1]; left-=rem; F.j++; F.f=0; if(F.j>=pts.length){ if(!endOfPath()) return; } } } }
function endOfPath(){ const k=nextCurrent(F.i);
  if(k<0){ F.done='ends'; refreshCard(); return false; }
  if(k===F.start||F.ridden.length>=12){ F.done='lap'; F.ridden.push(CUR[k].k); refreshCard(); return false; }
  F.i=k; F.j=1; F.f=0; const s0=firstPt(PATHS[k]); F.x=s0[0]; F.y=s0[1]; F.ridden.push(CUR[k].k); refreshCard(); return true; }
function paintFloat(now,alpha){ if(!F.done&&!RM){ const dt=Math.min(0.1,(now-F.last)/1000); F.last=now; stepFloat(dt); if(!F.done) refreshCard(true); }
  ctx.globalAlpha=alpha; ctx.strokeStyle='#ffb02e'; ctx.lineWidth=2; ctx.beginPath(); ctx.arc(F.x,F.y,7,0,Math.PI*2); ctx.stroke();
  ctx.fillStyle='#fff4d6'; ctx.beginPath(); ctx.arc(F.x,F.y,3,0,Math.PI*2); ctx.fill();
  label(Math.round(F.km).toLocaleString('en-US')+' km',F.x,F.y-16,'#ffb02e',alpha); ctx.globalAlpha=1; }
function showFloat(){ const c=CUR[F.i], names=F.ridden.map(k=>CUR.find(x=>x.k===k).n.replace(/^the /,'')).join(', ');
  const st=F.done==='lap'?'a lap of the ring, back where it started':F.done==='ends'?'stranded: no drawn current begins where this one ends':'riding '+c.n;
  card('A float', st, [['traveled',Math.round(F.km).toLocaleString('en-US')+' km along the drawn paths'],['currents ridden',names]],
    'The float follows the currents as drawn, at the animation\\'s one speed, and joins whichever current begins within about 1,500 km of where its current ends. Another click drops it elsewhere.', c.s); }
function refreshCard(light){ if(view!=='surface') return; if(hot) { if(!light) showCurrent(hot); return; } if(F.on){ showFloat(); return; } if(light) return; if(gyre) showGyre(gyre); else showCurrent('gulf'); }
function loop(now){ if(anim) paint(now); requestAnimationFrame(loop); }

/* ---- the card ---- */
function card(kind,name,rows,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').innerHTML=name;
  document.getElementById('numTxt').innerHTML=rows.filter(r=>r[1]).map(([k,v])=>'<b>'+esc(k)+'</b> '+v).join('<br>');
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').textContent=src;
}
function showCurrent(k){ const c=CUR.find(x=>x.k===k); const g=GYRES.find(x=>x.k===c.g); const [a,b]=[c.p[0],c.p[c.p.length-1]];
  const mlat=c.p.reduce((s,p)=>s+p[1],0)/c.p.length, cosl=Math.cos(mlat*Math.PI/180);
  const dlat=b[1]-a[1], dlon=(((b[0]-a[0]+540)%360)-180)*cosl;
  const ang=Math.atan2(dlat,dlon)*180/Math.PI, dir=['east','northeast','north','northwest','west','southwest','south','southeast'][((Math.round(ang/45)%8)+8)%8];
  let side=''; if(g){ const mlon=c.p.reduce((s,p)=>s+(((p[0]-g.c[0]+540)%360)-180),0)/c.p.length*cosl, dy=mlat-g.c[1]; side=Math.abs(mlon)>Math.abs(dy)?(mlon<0?'western':'eastern'):(dy>0?'northern':'southern'); }
  card('A current', esc(c.n), [['water',c.w],['flows',dir+(g?', the '+side+' side of '+g.n:'')],['carries',c.sv],['speed',c.v]], c.b, c.s); }
function showGyre(k){ const g=GYRES.find(x=>x.k===k); const cs=CUR.filter(c=>c.g===k);
  card('A gyre', esc(g.n), [['turns',g.sense],['its currents',cs.map(c=>c.n.replace(/^the /,'')).join(', ')]], g.b, 'Wikipedia, Ocean gyre'); }
function showConveyor(){ card('The conveyor','The overturning circulation',[['sinks','in the Nordic and Labrador seas, about 15 Sv'],['rises','in the Indian and Pacific oceans'],['one lap','about a thousand years']], CONVNOTE, 'Broecker 1991; Rahmstorf 2002; Talley 2013'); }
function showSurface(){ card('The surface','The currents and the gyres',[['currents',CUR.length],['warm',CUR.filter(c=>c.w==='warm').length],['cold',CUR.filter(c=>c.w==='cold').length]],'A current under the pointer, or a gyre from the row above, lands here.','Wikipedia, Ocean current'); }

/* ---- the pointer ---- */
function nearest(px,py){ let best=null, bd=8; PATHS.forEach((pts,i)=>{ for(let j=1;j<pts.length;j++){ const a=pts[j-1], b=pts[j]; if(!a||!b) continue; const dx=b[0]-a[0], dy=b[1]-a[1], l2=dx*dx+dy*dy||1; let t=((px-a[0])*dx+(py-a[1])*dy)/l2; t=Math.max(0,Math.min(1,t)); const d=Math.hypot(px-(a[0]+t*dx),py-(a[1]+t*dy)); if(d<bd){ bd=d; best=CUR[i].k; } } }); return best; }
cv.addEventListener('pointermove',e=>{ if(view!=='surface') return; const r=cv.getBoundingClientRect(); const k=nearest((e.clientX-r.left)/r.width*W,(e.clientY-r.top)/r.height*H); if(quiet){ if(k===quiet) return; quiet=null; } if(k!==hot){ hot=k; refreshCard(); } });
cv.addEventListener('pointerleave',()=>{ hot=null; refreshCard(); });
cv.addEventListener('click',e=>{ if(view!=='surface') return; const r=cv.getBoundingClientRect(); const px=(e.clientX-r.left)/r.width*W, py=(e.clientY-r.top)/r.height*H;
  if(!isSea(LON(px),LAT(py))){ return; } quiet=hot; hot=null; if(!dropFloat(px,py)&&F.on) clearFloat(); });
document.getElementById('floatBtn').addEventListener('click',clearFloat);
window.addEventListener('keydown',e=>{ if(e.key==='Escape'&&F.on) clearFloat(); });
document.getElementById('gyres').innerHTML=GYRES.map(g=>'<button type="button" data-g="'+g.k+'">'+esc(g.n.replace(/^the /,''))+'</button>').join('');
document.getElementById('gyres').addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; gyre=gyre===b.dataset.g?null:b.dataset.g; for(const x of document.querySelectorAll('#gyres button')) x.classList.toggle('on',x.dataset.g===gyre); if(gyre) showGyre(gyre); else refreshCard(); });
document.getElementById('legend').innerHTML='<span><i style="background:'+WARM+'"></i>warm</span><span><i style="background:'+COLD+'"></i>cold</span><span>the dashes move the way the water goes</span>';
function setView(v){ if(v===view) return; view=v; hot=null; for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on',b.dataset.v===v); document.getElementById('gyreCtl').hidden=v!=='surface';
  tvFrom=tv; tvTo=v==='conveyor'?1:0; if(RM){ tv=tvTo; tvT0=0; } else { tvT0=performance.now(); tvDur=v==='conveyor'?2400:900; }
  document.getElementById('floatBtn').classList.toggle('show',v==='surface'&&F.on);
  document.getElementById('legend').innerHTML=v==='surface'?'<span><i style="background:'+WARM+'"></i>warm</span><span><i style="background:'+COLD+'"></i>cold</span><span>the dashes move the way the water goes</span>':'<span><i style="background:'+COLD+'"></i>deep, cold</span><span><i style="background:'+WARM+'"></i>surface, warm</span>';
  if(v==='surface') refreshCard(); else showConveyor(); }
document.getElementById('views').addEventListener('click',e=>{ const b=e.target.closest('button[data-v]'); if(b) setView(b.dataset.v); });

showCurrent('gulf');
decode(LAND,LW,LH,a=>{ land=a; paintBase(); requestAnimationFrame(loop); });
window.__ocean=(q)=>{ const o={view,hot,gyre,tv,ready:!!base,n:CUR.length,H,card:document.getElementById('numTxt').innerText,name:document.getElementById('nameTxt').innerText,
  float:{on:F.on,cur:F.i>=0?CUR[F.i].k:null,km:F.km,ridden:F.ridden.slice(),done:F.done,x:F.x,y:F.y}};
  if(q&&q.at){ o.near=nearest(X(q.at[0]),Y(q.at[1])); } if(q&&q.sea){ o.sea=q.sea.map(([lo,la])=>isSea(lo,la)); } if(q&&q.xy){ o.xy=[X(q.xy[0]),Y(q.xy[1])]; }
  if(q&&q.drop){ dropFloat(X(q.drop[0]),Y(q.drop[1])); o.float={on:F.on,cur:F.i>=0?CUR[F.i].k:null,km:F.km,ridden:F.ridden.slice(),done:F.done}; }
  if(q&&q.ride){ let n=0; while(!F.done&&n++<100000) stepFloat(0.05); o.float={on:F.on,cur:F.i>=0?CUR[F.i].k:null,km:F.km,ridden:F.ridden.slice(),done:F.done}; }
  if(q&&q.tv!=null){ tv=q.tv; tvT0=0; }
  if(q&&q.pixel){ anim=false; paint(performance.now()); const d=ctx.getImageData(q.pixel[0],q.pixel[1],1,1).data; o.rgb=[d[0],d[1],d[2]]; anim=true; } return o; };
</script>
</body>
</html>
"""

html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__CUR__", _js(currents)).replace("__GYRES__", _js(gyres)).replace("__CONV__", _js(CONVEYOR)).replace("__CONVNOTE__", _js(CONVEYOR_NOTE))
        .replace("__LAND__", _js(GEO["land"])).replace("__LW__", str(GEO["landW"])).replace("__LH__", str(GEO["landH"]))
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(CURRENTS)} currents, {len(GYRES)} gyres")
