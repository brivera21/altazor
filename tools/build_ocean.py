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
         "drift to the right north of the equator and to the left south of "
         "it, and the continents get in the way. The result is five great "
         "rings of current, clockwise in the north and counterclockwise in "
         "the south, each with a fast, narrow, warm current on its western "
         "side and a slow, cool one on its eastern, and one current with "
         "no land to stop it circling the Antarctic.")

NOTE2 = ("Under the surface there is a slower circulation. Water that "
         "reaches the far North Atlantic is cold and salty enough to sink, "
         "and it creeps along the ocean floor for centuries before rising "
         "in the Indian and Pacific oceans and returning at the surface. "
         "The second view follows it round. A current under the pointer "
         "says how much water it moves, in sverdrups: a million cubic "
         "meters a second, about five Amazons.")

METHOD = ("The currents are drawn by hand from the standard maps as a few "
          "points each and are schematic; the real ones meander, shed "
          "eddies, and shift with the seasons, and the northern Indian "
          "Ocean reverses with the monsoon and is left out. Transports are "
          "those the cited articles give, so most currents have none. The "
          "animation moves the dashes at one speed for all currents and "
          "says nothing about how fast each one flows. The conveyor is "
          "Broecker's cartoon, with the Southern Ocean return that later "
          "work added; the true circulation is a tangle of many paths, and "
          "this is the one that survives the averaging. The map is "
          "equirectangular, so high latitudes are stretched.")


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
@media (max-width:900px){ .stage{flex-direction:column;} .side{position:static; width:100%;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library &middot; Earth</a><a href="atmosphere.html">The Atmosphere</a><a href="earth.html">Climate</a><a href="plates.html">Tectonic Plates</a></nav>
</header>
<h1>Ocean Currents</h1>
<div class="bar" id="views"><button data-v="surface" class="on">The surface</button><button data-v="conveyor">The conveyor</button></div>
<div class="controls" id="gyreCtl">
  <label>the gyres</label>
  <span class="presets" id="gyres"></span>
</div>
<div class="stage">
  <div id="diagram">
    <canvas id="map" width="980" height="490"></canvas>
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
<p class="note" style="border-top:none; padding-top:0;">__NOTE2__</p>
<div class="method"><p>__METHOD__</p></div>
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</div>
<script>
const CUR=__CUR__, GYRES=__GYRES__, CONV=__CONV__, CONVNOTE=__CONVNOTE__, LAND=__LAND__, LW=__LW__, LH=__LH__;
const W=980, H=490, WARM='#f28cb0', COLD='#58a6ff';
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const cv=document.getElementById('map'), ctx=cv.getContext('2d');
let view='surface', land=null, base=null, hot=null, gyre=null, t0=performance.now(), anim=true;
const X=lon=>(lon+180)/360*W, Y=lat=>(90-lat)/180*H;

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
  for(let y=0;y<H;y++) for(let x=0;x<W;x++){ const lx=Math.floor(x/W*LW), ly=Math.floor(y/H*LH), isLand=land[ly*LW+lx]>0; const p=(y*W+x)*4;
    if(isLand){ d[p]=58; d[p+1]=62; d[p+2]=66; } else { d[p]=14; d[p+1]=24; d[p+2]=38; } d[p+3]=255; }
  base=im; }
const isSea=(lon,lat)=>{ if(!land) return true; const lx=Math.floor((lon+180)/360*LW), ly=Math.floor((90-lat)/180*LH); return land[ly*LW+lx]===0; };

/* ---- drawing ---- */
function strokePath(pts,col,width,dash,off,alpha){ ctx.strokeStyle=col; ctx.lineWidth=width; ctx.globalAlpha=alpha; ctx.setLineDash(dash||[]); ctx.lineDashOffset=off||0; ctx.lineCap='round'; ctx.lineJoin='round';
  ctx.beginPath(); let up=true; for(const q of pts){ if(!q){ up=true; continue; } if(up){ ctx.moveTo(q[0],q[1]); up=false; } else ctx.lineTo(q[0],q[1]); } ctx.stroke(); ctx.setLineDash([]); ctx.globalAlpha=1; }
function arrowHead(pts,col,size,alpha){ let b=pts[pts.length-1], a=null; for(let i=pts.length-2;i>=0;i--){ if(pts[i]){ a=pts[i]; break; } } if(!a) return;
  const ang=Math.atan2(b[1]-a[1],b[0]-a[0]); ctx.fillStyle=col; ctx.globalAlpha=alpha; ctx.beginPath(); ctx.moveTo(b[0],b[1]); ctx.lineTo(b[0]-size*Math.cos(ang-0.5),b[1]-size*Math.sin(ang-0.5)); ctx.lineTo(b[0]-size*Math.cos(ang+0.5),b[1]-size*Math.sin(ang+0.5)); ctx.closePath(); ctx.fill(); ctx.globalAlpha=1; }
function label(text,x,y,col,alpha){ ctx.font='10.5px -apple-system,Helvetica,Arial,sans-serif'; ctx.globalAlpha=alpha; ctx.fillStyle='rgba(18,18,18,0.6)'; const w=ctx.measureText(text).width; ctx.fillRect(x-w/2-3,y-9,w+6,13); ctx.fillStyle=col; ctx.textAlign='center'; ctx.fillText(text,x,y+1); ctx.textAlign='start'; ctx.globalAlpha=1; }
function paint(now){
  if(!base) return; ctx.putImageData(base,0,0);
  ctx.strokeStyle='rgba(255,255,255,0.05)'; ctx.lineWidth=1;
  for(let lon=-150;lon<=150;lon+=30){ ctx.beginPath(); ctx.moveTo(X(lon),0); ctx.lineTo(X(lon),H); ctx.stroke(); }
  for(let lat=-60;lat<=60;lat+=30){ ctx.beginPath(); ctx.moveTo(0,Y(lat)); ctx.lineTo(W,Y(lat)); ctx.stroke(); }
  const off=-((now-t0)/40)%24;
  if(view==='surface'){
    CUR.forEach((c,i)=>{ const col=c.w==='warm'?WARM:COLD; const lit=hot?hot===c.k:gyre?c.g===gyre:true; const a=lit?1:0.22;
      strokePath(PATHS[i],col,lit&&(hot||gyre)?4:2.6,[],0,a*0.55); strokePath(PATHS[i],'#f4efe2',lit&&(hot||gyre)?2:1.4,[6,18],off,a*0.9); arrowHead(PATHS[i],col,lit&&(hot||gyre)?11:8,a); });
    CUR.forEach((c,i)=>{ const lit=hot?hot===c.k:gyre?c.g===gyre:true; if(!lit&&(hot||gyre)) return; const m=PATHS[i][Math.floor(PATHS[i].length/2)]||PATHS[i][0]; if(m) label(c.n.replace(/^the /,''),m[0],m[1]-10,c.w==='warm'?'#ffd0e0':'#bcd8ff',lit?0.95:0.3); });
    if(gyre){ const g=GYRES.find(x=>x.k===gyre); ctx.strokeStyle='#ffb02e'; ctx.setLineDash([4,4]); ctx.lineWidth=1.2; ctx.beginPath(); ctx.ellipse(X(g.c[0]),Y(g.c[1]),18,12,0,0,Math.PI*2); ctx.stroke(); ctx.setLineDash([]);
      const cw=g.sense==='clockwise'; ctx.fillStyle='#ffb02e'; ctx.font='16px sans-serif'; ctx.textAlign='center'; ctx.fillText(cw?'\\u21bb':'\\u21ba',X(g.c[0]),Y(g.c[1])+6); ctx.textAlign='start'; }
  } else {
    strokePath(CPATHS.deep,COLD,7,[],0,0.35); strokePath(CPATHS.deep,COLD,3,[8,14],off,0.95); arrowHead(CPATHS.deep,COLD,12,1);
    strokePath(CPATHS.deep_indian,COLD,7,[],0,0.35); strokePath(CPATHS.deep_indian,COLD,3,[8,14],off,0.95); arrowHead(CPATHS.deep_indian,COLD,12,1);
    strokePath(CPATHS.surface,WARM,7,[],0,0.35); strokePath(CPATHS.surface,WARM,3,[8,14],off,0.95); arrowHead(CPATHS.surface,WARM,12,1);
    strokePath(CPATHS.surface_indian,WARM,7,[],0,0.35); strokePath(CPATHS.surface_indian,WARM,3,[8,14],off,0.95); arrowHead(CPATHS.surface_indian,WARM,12,1);
    for(const [lon,lat,txt] of [[-35,62,'sinks'],[2,70,'sinks'],[-160,40,'rises'],[68,5,'rises']]){ ctx.fillStyle=txt==='sinks'?COLD:WARM; ctx.beginPath(); ctx.arc(X(lon),Y(lat),7,0,Math.PI*2); ctx.fill(); label(txt,X(lon),Y(lat)-14,txt==='sinks'?'#bcd8ff':'#ffd0e0',1); }
    label('cold and deep',X(-25),Y(-20)+16,'#bcd8ff',1); label('warm, at the surface',X(-20),Y(-2)-12,'#ffd0e0',1); label('about a thousand years round',X(-120),Y(-70),'#9a9a9a',1);
  }
}
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
cv.addEventListener('pointermove',e=>{ if(view!=='surface') return; const r=cv.getBoundingClientRect(); const k=nearest((e.clientX-r.left)/r.width*W,(e.clientY-r.top)/r.height*H); if(k!==hot){ hot=k; if(k) showCurrent(k); else if(gyre) showGyre(gyre); else showSurface(); } });
cv.addEventListener('pointerleave',()=>{ hot=null; });
document.getElementById('gyres').innerHTML=GYRES.map(g=>'<button type="button" data-g="'+g.k+'">'+esc(g.n.replace(/^the /,''))+'</button>').join('');
document.getElementById('gyres').addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; gyre=gyre===b.dataset.g?null:b.dataset.g; for(const x of document.querySelectorAll('#gyres button')) x.classList.toggle('on',x.dataset.g===gyre); if(gyre) showGyre(gyre); else showSurface(); });
document.getElementById('legend').innerHTML='<span><i style="background:'+WARM+'"></i>warm</span><span><i style="background:'+COLD+'"></i>cold</span><span>the dashes move the way the water goes</span>';
function setView(v){ view=v; hot=null; for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on',b.dataset.v===v); document.getElementById('gyreCtl').hidden=v!=='surface';
  document.getElementById('legend').innerHTML=v==='surface'?'<span><i style="background:'+WARM+'"></i>warm</span><span><i style="background:'+COLD+'"></i>cold</span><span>the dashes move the way the water goes</span>':'<span><i style="background:'+COLD+'"></i>deep, cold</span><span><i style="background:'+WARM+'"></i>surface, warm</span>';
  if(v==='surface') showSurface(); else showConveyor(); }
document.getElementById('views').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setView(b.dataset.v); });

showSurface();
decode(LAND,LW,LH,a=>{ land=a; paintBase(); requestAnimationFrame(loop); });
window.__ocean=(q)=>{ const o={view,hot,gyre,ready:!!base,n:CUR.length,card:document.getElementById('numTxt').innerText,name:document.getElementById('nameTxt').innerText};
  if(q&&q.at){ o.near=nearest(X(q.at[0]),Y(q.at[1])); } if(q&&q.sea){ o.sea=q.sea.map(([lo,la])=>isSea(lo,la)); }
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
