#!/usr/bin/env python3
"""Generate galaxies.html, Galaxies: what they are, and the Milky Way as one.

One stage, four views. Kinds is Hubble's tuning fork, every class drawn
from its definition, with the Milky Way's place on it marked. Sizes sets a
dozen galaxies beside ours on one scale, the Sun marked in the Milky Way.
The Milky Way is the anatomy of our own, face-on and edge-on, its parts
answering when touched. Neighbors is the Local Group seen from above the
galactic pole, on a log radius so the satellites and Andromeda share the
map. A part under the cursor fills the card.

Data: tools/galaxies_data.py.

Usage: python3 build_galaxies.py
"""

import json
from pathlib import Path

import apa
from galaxies_data import KINDS, SIZES, PARTS, NEIGHBORS, SUN_R, REFS

OUT = Path(__file__).parent.parent / "galaxies.html"

NOTE1 = ("Four views of one stage. Kinds is Hubble's fork: ellipticals by "
         "how flattened they look, then spirals by how tightly wound and "
         "how large the bulge, in two rows for those with a bar across the "
         "middle and those without, with the irregulars off the end. The "
         "Milky Way sits on the barred row between b and c.")

NOTE2 = ("Sizes sets other galaxies beside ours on one scale, with the Sun "
         "marked where it is, a little past halfway out. The Milky Way is "
         "our own galaxy drawn from the measurements, face-on and edge-on, "
         "and each part answers when touched. Neighbors is the Local Group "
         "from above the galactic pole, on a log radius, so the satellites "
         "within a hundred thousand parsecs and Andromeda at three quarters "
         "of a million share one map.")

CAPTION = ("Four views of galaxies, drawn from their measurements rather than "
           "photographed. Kinds is Hubble's fork of shapes, Sizes sets a dozen "
           "beside ours on one scale, The Milky Way is our own galaxy face-on "
           "and edge-on, and Neighbors is the Local Group seen from above. The "
           "Milky Way is marked in each.")

NOTE3 = ("Each view moves. On the fork one galaxy slides along the classes, "
         "flattening from E0 to E7 and then opening its arms from a to c as "
         "its bulge shrinks. Sizes can set every galaxy to one diameter and "
         "back, and a galaxy under the pointer carries a ghost of the Milky "
         "Way at the same scale. The Milky Way tips from face-on to edge-on, "
         "and the Sun runs one orbit of about 230 million years; the arms "
         "and bar are held as they are drawn, since their own pattern speeds "
         "differ from the Sun's. Neighbors slides between the log radius and "
         "the true one, where the satellites collapse onto the Milky Way.")

METHOD = ("Every galaxy here is a drawing from its class and its measured "
          "diameter, not a photograph. Diameters are the D25 isophote where "
          "one is published, which is where the light falls to a quarter of "
          "a percent of the dark sky, so a real disc fades on past the edge "
          "drawn; the Milky Way's 26.8 kiloparsecs is a stellar disc measured "
          "the same way. Dwarf galaxy sizes are rounded, since a dwarf has no "
          "edge to speak of. Distances and positions in the Local Group are "
          "McConnachie's 2012 compilation, plotted by galactic longitude with "
          "the radius on a log scale from 15 to 1,500 kiloparsecs. The Milky "
          "Way's parts follow Bland-Hawthorn and Gerhard's 2016 review, the "
          "Sun's distance to the center the GRAVITY measurement, the arms "
          "Reid and others' 2019 parallaxes. In the edge-on view the disc is "
          "drawn at its true thickness against its width, which is why it is "
          "a line.")


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Galaxies &middot; Altazor</title>
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
nav.site a { color:var(--muted); text-decoration:none; font-size:14px; margin-right:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 12px; font-size:26px; }
.bar { display:flex; gap:6px; flex-wrap:wrap; margin:0 0 8px; }
.bar button { background:var(--panel); color:var(--muted); border:1px solid var(--line);
  border-radius:999px; padding:6px 14px; font-size:13.5px; cursor:pointer; font-family:inherit; }
.bar button:hover { color:var(--text); border-color:#3d3d3d; }
.bar button.on { color:#0b0b0b; background:var(--accent); border-color:var(--accent); font-weight:700; }
.bar2 { display:flex; gap:6px; flex-wrap:wrap; margin:0 0 12px; min-height:30px; }
.bar2 button { background:transparent; color:var(--muted); border:1px solid var(--line);
  border-radius:8px; padding:4px 11px; font-size:12.5px; cursor:pointer; font-family:inherit; }
.bar2 button:hover { color:var(--text); }
.bar2 button.on { color:var(--text); border-color:var(--accent); }
.bar2[hidden] { display:none; }
.toprow { display:flex; flex-wrap:wrap; align-items:center; gap:8px 22px; margin:0 0 12px; }
.toprow .bar, .toprow .bar2 { margin:0; }
.bar2 { align-items:center; }
.bar2 .lab { font-size:12.5px; color:var(--muted); margin:0 2px 0 4px; }
.bar2 input[type=range] { width:200px; accent-color:var(--accent); }
.bar2 button.play { color:var(--text); border-color:#3d3d3d; min-width:64px; }
.bar2 button.play[aria-pressed=true] { background:var(--accent); color:#0b0b0b; border-color:var(--accent); font-weight:700; }
#diagram { border-radius:12px; outline:none; }
#diagram text.halo { paint-order:stroke; stroke:#121212; stroke-width:3.5px; stroke-linejoin:round; }
details.sources { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
details.sources summary { cursor:pointer; }
details.sources summary:hover { color:var(--text); }
details.sources .note { border-top:none; padding-top:0; margin-top:10px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; }
#diagram svg { width:100%; height:auto; display:block; user-select:none; }
.side { flex:0 0 300px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:16px; }
#kindTxt { font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
#nameTxt { font-weight:700; font-size:17px; margin:2px 0 6px; }
#numTxt { font-size:13px; line-height:1.55; font-variant-numeric:tabular-nums; }
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
@media (max-width:900px){ .stage{flex-direction:column;} .side{position:static; width:100%; order:-1;}
  #diagram{width:100%; flex-basis:auto;} }
@media (max-width:600px){ #diagram{overflow-x:auto; -webkit-overflow-scrolling:touch;} #diagram svg{min-width:680px;}
  .bar2 input[type=range]{width:150px;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library &middot; The Universe</a><a href="universe.html">The Universe</a><a href="solar-system.html">The Solar System</a></nav>
</header>
<h1>Galaxies</h1>
<div class="toprow"><div class="bar" id="views">
  <button data-v="kinds" class="on">Kinds</button>
  <button data-v="sizes">Sizes</button>
  <button data-v="ours">The Milky Way</button>
  <button data-v="near">Neighbors</button>
</div>
<div class="bar2" id="sub"></div></div>
<div class="stage">
  <div id="diagram" tabindex="0" aria-label="galaxies: their kinds, sizes, our own, and our neighbors"></div>
  <div class="side"><div class="card">
    <div id="kindTxt"></div>
    <div id="nameTxt"></div>
    <div id="numTxt"></div>
    <div id="bodyTxt"></div>
    <div id="srcTxt"></div>
  </div></div>
</div>
<p class="note">__CAPTION__</p>
<details class="sources"><summary>Sources</summary>
<p class="note">__NOTE1__</p>
<p class="note">__NOTE2__</p>
<p class="note">__NOTE3__</p>
<div class="method"><p>__METHOD__</p></div>
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</details>
</div>
<script>
const KINDS=__KINDS__, SIZES=__SIZES__, PARTS=__PARTS__, NEAR=__NEAR__, SUN_R=__SUNR__;
const W=980, H=720;
const el=document.getElementById('diagram');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
let view='kinds', side='face', sel=null, seed=7;
// the moving parts: a galaxy sliding along the fork, the sizes set to one,
// the Milky Way's tilt and the Sun's time on its orbit, and the neighbors' radius
let morph=0.72, mbar=false, same=0, tilt=0, orbitT=0, rlin=0;
const RM=matchMedia('(prefers-reduced-motion: reduce)').matches;
const ease=u=>u<.5?2*u*u:1-Math.pow(-2*u+2,2)/2;
const tws={};
function tween(name,from,to,D,set,done,frame){
  if(tws[name]) cancelAnimationFrame(tws[name]);
  if(RM||from===to){ set(to); render(); tws[name]=0; if(done) done(); return; }
  const t0=performance.now();
  const tick=now=>{ const u=Math.min(1,(now-t0)/D); set(from+(to-from)*ease(u));
    if(u<1){ (frame||render)(); tws[name]=requestAnimationFrame(tick); } else { render(); tws[name]=0; if(done) done(); } };
  tws[name]=requestAnimationFrame(tick);
}

/* ---- deterministic noise, so a drawing is the same on every visit ---- */
function rnd(){ seed=(seed*1103515245+12345)&0x7fffffff; return seed/0x7fffffff; }

/* ---- galaxies drawn from their class ----
   E<n>: an ellipsoid of old stars, axis ratio 1 - n/10.
   S0: a disc with a big bulge and no arms.  Sa/Sb/Sc: arms wound at a pitch
   that opens from a to c while the bulge shrinks.  SB: the same with a bar
   the arms leave from.  Irr: no symmetry to speak of. */
const GLOW={E:['#f2d9c4','#8a5a3a'], S0:['#f0dcc4','#7a5a40'], S:['#dfe8ff','#5a6fb0'],
            SB:['#e6ecff','#5f6fb0'], Irr:['#cfe6ff','#4a6fa0'], MW:['#e6ecff','#5f6fb0']};
let gid=0;
function grad(defs,c0,c1,r0){
  const id='g'+(gid++);
  defs.push('<radialGradient id="'+id+'" cx="50%" cy="50%" r="'+(r0||50)+'%">'+
    '<stop offset="0" stop-color="'+c0+'" stop-opacity="0.95"/>'+
    '<stop offset="0.45" stop-color="'+c1+'" stop-opacity="0.55"/>'+
    '<stop offset="1" stop-color="'+c1+'" stop-opacity="0"/></radialGradient>');
  return 'url(#'+id+')';
}
function spiralArm(cx,cy,r0,r1,pitch,phase,wind,width,col,op){
  // a logarithmic spiral r = r0 e^(k th), k = tan(pitch); the band thins outward
  const k=Math.tan(pitch), n=90; let s='';
  const thEnd=Math.log(r1/r0)/k;
  for(let i=0;i<n;i++){
    const t0=thEnd*i/n, t1=thEnd*(i+1)/n;
    const ra=r0*Math.exp(k*t0), rb=r0*Math.exp(k*t1);
    const a0=phase+wind*t0, a1=phase+wind*t1;
    const w=width*(1-0.75*i/n);
    s+='<line x1="'+(cx+ra*Math.cos(a0)).toFixed(1)+'" y1="'+(cy+ra*Math.sin(a0)).toFixed(1)+
       '" x2="'+(cx+rb*Math.cos(a1)).toFixed(1)+'" y2="'+(cy+rb*Math.sin(a1)).toFixed(1)+
       '" stroke="'+col+'" stroke-width="'+w.toFixed(1)+'" stroke-linecap="round" stroke-opacity="'+
       (op*(1-0.5*i/n)).toFixed(2)+'"/>';
  }
  return s;
}
function galaxy(defs,cls,cx,cy,R,opts){
  // cls: E0..E7, S0, Sa, Sb, Sc, SBa, SBb, SBc, Irr, MW. R: the drawn radius.
  opts=opts||{};
  const tilt=opts.tilt||0, incl=opts.incl===undefined?0:opts.incl;   // inclination: 0 face-on
  const q=Math.cos(incl);
  let s='<g transform="translate('+cx+','+cy+') rotate('+tilt+')">';
  if(cls[0]==='E'){
    const n=opts.n!==undefined?opts.n:+cls[1], ratio=1-n/10;
    s+='<ellipse cx="0" cy="0" rx="'+R+'" ry="'+(R*ratio).toFixed(1)+'" fill="'+grad(defs,GLOW.E[0],GLOW.E[1],60)+'"/>';
    s+='<ellipse cx="0" cy="0" rx="'+(R*0.35).toFixed(1)+'" ry="'+(R*0.35*ratio).toFixed(1)+'" fill="'+GLOW.E[0]+'" fill-opacity="0.55"/>';
  } else if(cls==='Irr'){
    seed=opts.seed||11;
    s+='<ellipse cx="0" cy="0" rx="'+R+'" ry="'+(R*0.7).toFixed(1)+'" fill="'+grad(defs,GLOW.Irr[0],GLOW.Irr[1],55)+'" fill-opacity="0.6"/>';
    for(let i=0;i<22;i++){
      const a=rnd()*6.283, d=Math.pow(rnd(),0.6)*R*0.85, rr=R*(0.06+0.16*rnd());
      s+='<circle cx="'+(d*Math.cos(a)).toFixed(1)+'" cy="'+(d*Math.sin(a)*0.75).toFixed(1)+'" r="'+rr.toFixed(1)+
         '" fill="'+(rnd()<0.4?'#b7d8ff':'#ecf2ff')+'" fill-opacity="'+(0.35+0.4*rnd()).toFixed(2)+'"/>';
    }
  } else {
    const barred=cls.startsWith('SB')||cls==='MW';
    const sub=cls==='S0'?'0':cls==='MW'?'bc':cls.slice(barred?2:1);
    const pitch=opts.pitch!==undefined?opts.pitch:{ '0':0, a:0.17, b:0.23, bc:0.26, c:0.36 }[sub];
    const bulge=opts.bulge!==undefined?opts.bulge:{ '0':0.42, a:0.36, b:0.24, bc:0.19, c:0.12 }[sub];
    const col=barred?GLOW.SB:GLOW.S;
    // the disc, seen at the inclination asked for
    s+='<ellipse cx="0" cy="0" rx="'+R+'" ry="'+(R*q).toFixed(1)+'" fill="'+grad(defs,col[0],col[1],52)+'" fill-opacity="0.7"/>';
    s+='<ellipse cx="0" cy="0" rx="'+(R*0.96).toFixed(1)+'" ry="'+(R*q*0.96).toFixed(1)+'" fill="none" stroke="'+col[0]+'" stroke-opacity="0.22" stroke-width="1"/>';
    if(sub!=='0'){
      const arms=opts.arms||2, r0=barred?R*0.42:R*bulge*1.1;
      s+='<g transform="scale(1,'+q.toFixed(3)+')">';
      for(let i=0;i<arms;i++){
        const ph=(opts.phase||0)+i*6.283/arms;
        s+=spiralArm(0,0,r0,R*0.98,pitch,ph,1,Math.max(1.6,R*0.13),'#f4f7ff',0.55);
        s+=spiralArm(0,0,r0*1.02,R*0.95,pitch,ph+0.06,1,Math.max(0.8,R*0.05),'#9fc4ff',0.5);
      }
      s+='</g>';
    }
    if(barred){
      s+='<g transform="scale(1,'+q.toFixed(3)+') rotate('+(opts.barAngle||0)+')">'+
         '<ellipse cx="0" cy="0" rx="'+(R*0.42).toFixed(1)+'" ry="'+(R*0.11).toFixed(1)+
         '" fill="#f6e7cf" fill-opacity="0.75"/></g>';
    }
    // the bulge, which stays round whatever the tilt
    s+='<ellipse cx="0" cy="0" rx="'+(R*bulge).toFixed(1)+'" ry="'+(R*bulge*(0.6+0.4*q)).toFixed(1)+
       '" fill="'+grad(defs,'#fff1dc','#c9925a',60)+'"/>';
  }
  s+='</g>';
  return s;
}

/* ---- the card ---- */
function card(kind,name,nums,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').textContent=name;
  document.getElementById('numTxt').innerHTML=(nums||[]).map(([k,v])=>'<b>'+esc(k)+'</b> '+esc(v)).join('<br>');
  document.getElementById('bodyTxt').textContent=body||'';
  document.getElementById('srcTxt').textContent=src||'';
}

/* ---- view: Kinds, the tuning fork ---- */
function drawKinds(defs){
  let s='';
  const y0=360, yU=205, yL=515, R=44;
  const cols=[120,240,360];              // E0 E3 E7
  const xS0=480, xs=[610,730,850], xIrr=935;
  // the fork itself
  s+='<path d="M'+(cols[0]-50)+','+y0+' H'+xS0+' M'+xS0+','+y0+' C'+(xS0+50)+','+y0+' '+(xS0+50)+','+yU+' '+(xs[0]-40)+','+yU+
     ' H'+(xs[2]+50)+' M'+xS0+','+y0+' C'+(xS0+50)+','+y0+' '+(xS0+50)+','+yL+' '+(xs[0]-40)+','+yL+' H'+(xs[2]+50)+
     '" fill="none" stroke="#2b2b2b" stroke-width="2"/>';
  s+='<text x="'+(cols[1])+'" y="'+(y0-78)+'" text-anchor="middle" font-size="13" fill="#8a94a6">ellipticals, by how flattened they look</text>';
  s+='<text x="'+xs[1]+'" y="'+(yU-78)+'" text-anchor="middle" font-size="13" fill="#8a94a6">spirals without a bar, arms opening a to c</text>';
  s+='<text x="'+xs[1]+'" y="'+(yL-78)+'" text-anchor="middle" font-size="13" fill="#8a94a6">spirals with a bar</text>';
  // one galaxy slid along the fork: flattened E0 to E7, then an S0 disc,
  // then arms opening from a to c while the bulge shrinks
  const mx0=250;
  s+='<text x="'+mx0+'" y="42" text-anchor="middle" font-size="13" fill="#8a94a6">one galaxy, slid along the fork</text>';
  s+='<g data-k="morph" id="morphG" style="cursor:pointer">'+morphSVG()+'</g>';
  const place={E0:[cols[0],y0],E3:[cols[1],y0],E7:[cols[2],y0],S0:[xS0,y0],
    Sa:[xs[0],yU],Sb:[xs[1],yU],Sc:[xs[2],yU],SBa:[xs[0],yL],SBb:[xs[1],yL],SBc:[xs[2],yL],Irr:[xIrr,y0]};
  for(const k of KINDS){
    const [x,y]=place[k.k];
    const hot=sel===k.k;
    s+='<g data-k="'+k.k+'" style="cursor:pointer">';
    if(hot) s+='<circle cx="'+x+'" cy="'+y+'" r="'+(R+10)+'" fill="none" stroke="#58a6ff" stroke-width="1.4"/>';
    s+=galaxy(defs,k.k,x,y,R,{tilt:k.k[0]==='E'?-20:0,incl:0.35,phase:0.6,barAngle:-25,seed:11});
    s+='<circle cx="'+x+'" cy="'+y+'" r="'+(R+8)+'" fill="transparent"/>';
    s+='<text x="'+x+'" y="'+(y+R+22)+'" text-anchor="middle" font-size="13" font-weight="700" fill="'+(hot?'#58a6ff':'#e6e6e6')+'">'+k.k+'</text>';
    s+='</g>';
  }
  // the Milky Way, between SBb and SBc
  const mx=(xs[1]+xs[2])/2, my=yL+86;
  const hot=sel==='MW';
  s+='<g data-k="MW" style="cursor:pointer">';
  s+='<line x1="'+mx+'" y1="'+(yL+3)+'" x2="'+mx+'" y2="'+(my-9)+'" stroke="#ffb02e" stroke-width="1.2" stroke-dasharray="3 3"/>';
  s+='<circle cx="'+mx+'" cy="'+my+'" r="'+(hot?9:6.5)+'" fill="#ffb02e" stroke="#121212" stroke-width="1.5"/>';
  s+='<text x="'+mx+'" y="'+(my+24)+'" text-anchor="middle" font-size="12.5" font-weight="700" fill="#ffb02e">the Milky Way, SBbc</text>';
  s+='<circle cx="'+mx+'" cy="'+my+'" r="16" fill="transparent"/></g>';
  return s;
}
// the sliding galaxy, with its own gradients, so a move of the slider
// redraws it alone and not the whole fork
function morphSVG(){
  const mx0=250, my0=150, MR=70, mc=morphClass(morph), d=[], keep=gid; gid=100000;
  let s='';
  if(morph<0.35) s+=galaxy(d,'E0',mx0,my0,MR,{tilt:-20,n:morph/0.35*7});
  else if(morph<0.45) s+=galaxy(d,'S0',mx0,my0,MR,{incl:0.35});
  else { const u=(morph-0.45)/0.55;
    s+=galaxy(d,mbar?'SBb':'Sb',mx0,my0,MR,{incl:0.35,phase:0.6,barAngle:-25,pitch:0.17+0.19*u,bulge:0.36-0.24*u}); }
  gid=keep;
  return '<defs>'+d.join('')+'</defs>'+s+'<circle cx="'+mx0+'" cy="'+my0+'" r="'+(MR+8)+'" fill="transparent"/>'+
    '<text x="'+mx0+'" y="'+(my0+MR+26)+'" text-anchor="middle" font-size="15" font-weight="700" fill="#58a6ff">'+mc+'</text>';
}
function setMorph(v){
  morph=v; const k=nearestKind(morph), m=document.getElementById('morph'); if(m) m.value=Math.round(morph*1000);
  showKind('morph');
  const g=document.getElementById('morphG');
  if(k!==sel||!g){ sel=k; render(); } else g.innerHTML=morphSVG();
}
function morphClass(t){
  if(t<0.35) return 'E'+Math.round(t/0.35*7);
  if(t<0.45) return 'S0';
  return (mbar?'SB':'S')+['a','ab','b','bc','c'][Math.round((t-0.45)/0.55*4)];
}
function nearestKind(t){
  if(t<0.35){ const n=t/0.35*7; return n<1.5?'E0':n<5?'E3':'E7'; }
  if(t<0.45) return 'S0';
  const u=(t-0.45)/0.55; return (mbar?'SB':'S')+(u<0.33?'a':u<0.67?'b':'c');
}
function showKind(k){
  if(k==='morph') k=nearestKind(morph);
  const d=KINDS.find(x=>x.k===k);
  if(k==='MW'){ const m=PARTS.find(p=>p.k==='whole');
    card('Our galaxy on the fork','The Milky Way, an SBbc',[['class','barred spiral, arms between b and c'],
      ['bar','about 5 kpc half-length, seen end-on from here at 28 degrees'],['arms','two major, two minor, pitch 9 to 14 degrees']],
      m.mw,'Bland-Hawthorn and Gerhard 2016; Reid and others 2019'); return; }
  if(!d) return;
  card(d.g,d.n,[['defined by',d.def],['examples',d.ex],['the Milky Way',d.mw]],d.b,d.s);
}

/* ---- view: Sizes ---- */
// the packing for a given radius per galaxy, largest first, wrapped into rows
function packSizes(Rof){
  const order=[...SIZES].sort((a,b)=>b.d-a.d);
  let x=24, rowTop=34, rowMaxR=0, row=[]; const out={};
  const flush=()=>{ for(const p of row){ p.y=rowTop+rowMaxR+6; p.labY=rowTop+2*rowMaxR+26; out[p.g.k]=p; }
    row=[]; rowTop+=2*rowMaxR+62; rowMaxR=0; };
  for(const g of order){
    // a slot as wide as the galaxy or its name, whichever is more
    const R=Rof(g), w=Math.max(2*R+36, g.n.length*6.6+18);
    if(x+w>W-10){ flush(); x=24; }
    row.push({g,x:x+w/2,R}); rowMaxR=Math.max(rowMaxR,Math.max(R,10));
    x+=w;
  }
  flush();
  return out;
}
const SIZE_K=300/Math.max(...SIZES.map(g=>g.d));   // px per kpc: the largest is 300 across
const LAY_SCALE=packSizes(g=>Math.max(g.d*SIZE_K/2,3)), LAY_SAME=packSizes(()=>34);
// during the tween to one size, the drawn galaxies are moved and scaled in place
function placeSizes(){
  const u=same, svg=document.getElementById('gsvg'); if(!svg) return;
  for(const gh of svg.querySelectorAll('.ghost')) gh.remove();
  for(const g of SIZES){ const a=LAY_SCALE[g.k], b=LAY_SAME[g.k], grp=svg.querySelector('g[data-k="'+g.k+'"]'); if(!grp) continue;
    const x=a.x+(b.x-a.x)*u, y=a.y+(b.y-a.y)*u, R=a.R+(b.R-a.R)*u, ly=a.labY+(b.labY-a.labY)*u;
    const gx=grp.querySelector('g'), R0=+grp.dataset.r, rot=(gx.getAttribute('transform').match(/rotate\(([-\d.]+)\)/)||[0,0])[1];
    gx.setAttribute('transform','translate('+x.toFixed(1)+','+y.toFixed(1)+') scale('+(Math.max(R,3)/Math.max(R0,3)).toFixed(4)+') rotate('+rot+')');
    for(const c of grp.querySelectorAll(':scope > circle')){ c.setAttribute('cx',x.toFixed(1)); c.setAttribute('cy',y.toFixed(1)); }
    const hit=grp.querySelector(':scope > circle[fill="transparent"]'); if(hit) hit.setAttribute('r',Math.max(R+6,14));
    const t=grp.querySelector(':scope > text.name'); if(t){ t.setAttribute('x',x.toFixed(1)); t.setAttribute('y',ly.toFixed(1)); }
    if(g.k==='mw'){ const sy=y+SUN_R*SIZE_K*(R/a.R)*Math.cos(0.25);
      const sc=grp.querySelector(':scope > circle.sun'), st=grp.querySelector(':scope > text.sun');
      if(sc){ sc.setAttribute('cx',x.toFixed(1)); sc.setAttribute('cy',sy.toFixed(1)); }
      if(st){ st.setAttribute('x',(x+9).toFixed(1)); st.setAttribute('y',(sy+12).toFixed(1)); } }
  }
  const note=svg.querySelector('.samenote'); if(note) note.setAttribute('opacity',u.toFixed(2));
  const bar=svg.querySelector('.scalebar'); if(bar) bar.setAttribute('opacity',(1-u).toFixed(2));
}
function drawSizes(defs){
  const k=SIZE_K, u=same;
  const placed=SIZES.map(g=>{ const a=LAY_SCALE[g.k], b=LAY_SAME[g.k];
    return {g, x:a.x+(b.x-a.x)*u, y:a.y+(b.y-a.y)*u, labY:a.labY+(b.labY-a.labY)*u, R:a.R+(b.R-a.R)*u, R0:a.R}; });
  let s='';
  s+='<text class="samenote" x="24" y="22" font-size="12" fill="#8a94a6" opacity="'+u.toFixed(2)+'">every galaxy drawn at one diameter; the scale bar no longer applies</text>';
  const mw=placed.find(p=>p.g.k==='mw');
  for(const p of placed){
    const hot=sel===p.g.k, g=p.g;
    s+='<g data-k="'+g.k+'" data-r="'+p.R.toFixed(3)+'" style="cursor:pointer">';
    s+=galaxy(defs,g.c,p.x,p.y,Math.max(p.R,3),{incl:g.k==='m104'?1.25:0.25,tilt:g.tilt||0,phase:0.4,barAngle:-30,seed:5+g.k.length});
    if(hot) s+='<circle cx="'+p.x+'" cy="'+p.y+'" r="'+(p.R+8)+'" fill="none" stroke="#58a6ff" stroke-width="1.4"/>';
    if(g.k==='mw'){
      // the Sun, at its measured radius from the center, a little below the plane on this map
      const sx=p.x, sy=p.y+SUN_R*k*(p.R/p.R0)*Math.cos(0.25);
      s+='<circle class="sun" cx="'+sx.toFixed(1)+'" cy="'+sy.toFixed(1)+'" r="3" fill="#ffb02e" stroke="#121212" stroke-width="1"/>';
      s+='<text class="halo sun" x="'+(sx+9)+'" y="'+(sy+12)+'" font-size="10.5" fill="#ffb02e">the Sun</text>';
    }
    s+='<circle cx="'+p.x+'" cy="'+p.y+'" r="'+Math.max(p.R+6,14)+'" fill="transparent"/>';
    s+='<text class="name" x="'+p.x+'" y="'+p.labY+'" text-anchor="middle" font-size="11.5" fill="'+(g.k==='mw'?'#ffb02e':hot?'#58a6ff':'#cfd6e6')+'">'+esc(g.n)+'</text>';
    s+='</g>';
  }
  // a ghost of the Milky Way over the galaxy under the pointer, at that galaxy's scale
  const h=placed.find(p=>p.g.k===sel);
  if(h&&h.g.k!=='mw'){
    const gr=mw.R0*(h.R/h.R0);
    s+='<g class="ghost" pointer-events="none"><circle cx="'+h.x+'" cy="'+h.y+'" r="'+gr.toFixed(1)+'" fill="#ffb02e" fill-opacity="0.05" stroke="#ffb02e" stroke-width="1.3" stroke-dasharray="5 4"/>'+
       '<text class="halo" x="'+h.x+'" y="'+(h.y-gr-6).toFixed(1)+'" text-anchor="middle" font-size="11" fill="#ffb02e">the Milky Way, at the same scale</text></g>';
  }
  // the scale bar: 100,000 light years
  const ly=30.66;   // kpc in 100,000 ly
  s+='<g class="scalebar" opacity="'+(1-u).toFixed(2)+'"><line x1="30" y1="'+(H-28)+'" x2="'+(30+ly*k).toFixed(1)+'" y2="'+(H-28)+'" stroke="#cfd6e6" stroke-width="2"/>';
  s+='<text x="30" y="'+(H-36)+'" font-size="12.5" fill="#cfd6e6">scale: 100,000 light years, '+ly.toFixed(1)+' kpc</text></g>';
  return s;
}
function showSize(k){
  const g=SIZES.find(x=>x.k===k); if(!g) return;
  card(g.t,g.n,[['diameter',g.dTxt],['distance',g.dist],['class',g.c==='MW'?'SBbc':g.c]],g.b,g.s);
}

/* ---- view: The Milky Way ---- */
const K=22;                                 // px per kpc
function drawOurs(defs){
  const cx=W/2, cy=H/2-10, u=tilt;
  let s='';
  // face-on to edge-on: the disc turns a quarter so the Sun comes to the
  // left of the center, as the edge-on view has it, and tips over while
  // the edge-on parts fade in
  const faceOp=u<0.85?1:Math.max(0,1-(u-0.85)/0.15), edgeOp=u<0.7?0:Math.min(1,(u-0.7)/0.3);
  if(faceOp>0){
    let f='';
    { let s='';
    // the disc, then the bar and arms, the Sun at its radius straight below the center
    s+='<circle cx="'+cx+'" cy="'+cy+'" r="'+(15*K)+'" fill="'+grad(defs,'#dfe8ff','#3b4c80',50)+'" fill-opacity="0.55" data-k="thin"/>';
    s+='<circle cx="'+cx+'" cy="'+cy+'" r="'+(15*K)+'" fill="none" stroke="#3d444d" stroke-dasharray="4 4"/>';
    // arms: r = r0 e^(k th), with the four crossing the Sun's line at their measured radii
    const arms=PARTS.filter(p=>p.arm);
    for(const a of arms){
      const hot=sel===a.k, k=Math.tan(a.pitch*Math.PI/180);
      // the arm passes radius a.rSun at the Sun's azimuth (straight down, +90 deg)
      const th0=Math.PI/2, rs=a.rSun*K;
      let pts='';
      for(let t=-3.6;t<=3.2;t+=0.02){
        const r=rs*Math.exp(k*t); if(r<3.2*K||r>15*K) continue;
        const ang=th0-t;     // winding clockwise seen from the north pole
        pts+=(cx+r*Math.cos(ang)).toFixed(1)+','+(cy+r*Math.sin(ang)).toFixed(1)+' ';
      }
      s+='<g data-k="'+a.k+'" style="cursor:pointer"><polyline points="'+pts+'" fill="none" stroke="'+(hot?'#58a6ff':a.c)+
         '" stroke-width="'+(a.major?9:6)+'" stroke-opacity="'+(hot?0.9:0.55)+'" stroke-linecap="round"/>'+
         '<polyline points="'+pts+'" fill="none" stroke="transparent" stroke-width="18"/></g>';
    }
    // the local spur, a short arm segment through the Sun
    const sp=PARTS.find(p=>p.k==='spur'), hotS=sel==='spur';
    s+='<g data-k="spur" style="cursor:pointer"><path d="M'+(cx+1.6*K)+','+(cy+SUN_R*K+0.9*K)+' Q'+(cx)+','+(cy+SUN_R*K)+' '+(cx-2.4*K)+','+(cy+SUN_R*K-1.5*K)+
       '" fill="none" stroke="'+(hotS?'#58a6ff':sp.c)+'" stroke-width="5" stroke-opacity="0.7" stroke-linecap="round"/>'+
       '<path d="M'+(cx+1.6*K)+','+(cy+SUN_R*K+0.9*K)+' Q'+(cx)+','+(cy+SUN_R*K)+' '+(cx-2.4*K)+','+(cy+SUN_R*K-1.5*K)+'" fill="none" stroke="transparent" stroke-width="16"/></g>';
    // the bar, 5 kpc half-length, 28 degrees off the Sun's line
    const hotB=sel==='bar';
    // the near end of the bar lies at positive longitude, to the left on this view
    s+='<g data-k="bar" style="cursor:pointer" transform="translate('+cx+','+cy+') rotate('+(90+28)+')">'+
       '<ellipse cx="0" cy="0" rx="'+(5*K)+'" ry="'+(1.2*K)+'" fill="#f6e7cf" fill-opacity="'+(hotB?0.9:0.7)+'"'+(hotB?' stroke="#58a6ff" stroke-width="1.5"':'')+'/></g>';
    // the bulge
    const hotG=sel==='bulge';
    s+='<g data-k="bulge" style="cursor:pointer"><circle cx="'+cx+'" cy="'+cy+'" r="'+(1.5*K)+'" fill="'+grad(defs,'#fff1dc','#c9925a',60)+'"'+(hotG?' stroke="#58a6ff" stroke-width="1.5"':'')+'/></g>';
    // Sgr A*
    const hotA=sel==='sgra';
    s+='<g data-k="sgra" style="cursor:pointer"><circle cx="'+cx+'" cy="'+cy+'" r="'+(hotA?5:3)+'" fill="#121212" stroke="#ffb02e" stroke-width="1.4"/><circle cx="'+cx+'" cy="'+cy+'" r="10" fill="transparent"/></g>';
    // the Sun
    // the Sun, on its orbit: straight below the center now, and clockwise
    // round from there as the orbit plays
    const hotSun=sel==='sun', sa=Math.PI/2+2*Math.PI*orbitT/230, sx=cx+SUN_R*K*Math.cos(sa), sy=cy+SUN_R*K*Math.sin(sa);
    if(orbitT>0) s+='<circle cx="'+cx+'" cy="'+cy+'" r="'+(SUN_R*K)+'" fill="none" stroke="#ffb02e" stroke-opacity="0.3" stroke-dasharray="2 5"/>';
    s+='<g data-k="sun" style="cursor:pointer"><line x1="'+cx+'" y1="'+cy+'" x2="'+sx.toFixed(1)+'" y2="'+sy.toFixed(1)+'" stroke="#ffb02e" stroke-opacity="0.35" stroke-dasharray="3 4"/>'+
       '<circle cx="'+sx.toFixed(1)+'" cy="'+sy.toFixed(1)+'" r="'+(hotSun?6:4.5)+'" fill="#ffb02e" stroke="#121212" stroke-width="1.5"/>'+
       '<circle cx="'+sx.toFixed(1)+'" cy="'+sy.toFixed(1)+'" r="12" fill="transparent"/></g>';
      f=s; }
    const q=Math.cos(u*Math.PI/2);
    s+=u===0?f:'<g opacity="'+faceOp.toFixed(2)+'" transform="translate('+cx+','+cy+') scale(1,'+q.toFixed(4)+') rotate('+(90*u).toFixed(2)+') translate('+(-cx)+','+(-cy)+')">'+f+'</g>';
    if(u===0){
      const sp=PARTS.find(p=>p.k==='spur'), arms=PARTS.filter(p=>p.arm);
    // arm names, out along each
    for(const a of arms){
      const k=Math.tan(a.pitch*Math.PI/180), t=a.labelT, r=a.rSun*K*Math.exp(k*t), ang=Math.PI/2-t;
      s+='<text x="'+(cx+r*Math.cos(ang)).toFixed(1)+'" y="'+(cy+r*Math.sin(ang)).toFixed(1)+'" text-anchor="middle" font-size="11.5" fill="'+a.c+'" class="halo" pointer-events="none">'+esc(a.n)+'</text>';
    }
    s+='<text class="halo" x="'+(cx-2.8*K)+'" y="'+(cy+SUN_R*K-0.9*K)+'" text-anchor="end" font-size="11.5" fill="'+sp.c+'" pointer-events="none">'+esc(sp.n)+'</text>';
    { const sa=Math.PI/2+2*Math.PI*orbitT/230, sx=cx+SUN_R*K*Math.cos(sa), sy=cy+SUN_R*K*Math.sin(sa);
      s+='<text class="halo" x="'+(sx+12).toFixed(1)+'" y="'+(sy+18).toFixed(1)+'" font-size="12" fill="#ffb02e" pointer-events="none">the Sun, '+SUN_R+' kpc out</text>'; }
    // scale and orientation
    s+='<line x1="30" y1="'+(H-28)+'" x2="'+(30+5*K)+'" y2="'+(H-28)+'" stroke="#9a9a9a" stroke-width="2"/>';
    s+='<text x="30" y="'+(H-36)+'" font-size="11" fill="#9a9a9a">5 kpc, 16,300 light years</text>';
    s+='<text x="'+(W-20)+'" y="'+(H-32)+'" text-anchor="end" font-size="11" fill="#6b7280">seen from the north galactic pole, the center above the Sun; the disc turns clockwise</text>';
    }
  }
  if(edgeOp>0){
    let e='';
    { let s='';
    // edge-on: everything at its true proportion, which makes the disc a line
    const thin=PARTS.find(p=>p.k==='thin'), thick=PARTS.find(p=>p.k==='thick');
    const hotH=sel==='halo', hotGC=sel==='gcs';
    s+='<g data-k="halo" style="cursor:pointer"><circle cx="'+cx+'" cy="'+cy+'" r="'+(15*K)+'" fill="'+grad(defs,'#c9d4ee','#3b4c80',50)+'" fill-opacity="'+(hotH?0.5:0.3)+'"/>'+
       '<circle cx="'+cx+'" cy="'+cy+'" r="'+(15*K)+'" fill="none" stroke="'+(hotH?'#58a6ff':'#3d444d')+'" stroke-dasharray="4 4"/></g>';
    s+='<text x="'+(W-20)+'" y="'+(H-32)+'" text-anchor="end" font-size="11" fill="#6b7280">the dark matter halo goes on to some 200 kpc, fourteen times this circle</text>';
    // globular clusters, mostly within 10 kpc, a few far out
    seed=3;
    let gc='';
    for(let i=0;i<150;i++){
      const r=Math.pow(rnd(),1.6)*14*K+0.3*K, a=rnd()*6.283, z=Math.cos(a)*r*0.9;
      gc+='<circle cx="'+(cx+r*Math.sin(a)).toFixed(1)+'" cy="'+(cy+z).toFixed(1)+'" r="1.6" fill="'+(hotGC?'#58a6ff':'#f4efe2')+'" fill-opacity="0.8"/>';
    }
    s+='<g data-k="gcs" style="cursor:pointer">'+gc+'</g>';
    // thick and thin discs at their scale heights, twice the scale height each way
    const hotK=sel==='thick', hotT=sel==='thin';
    s+='<g data-k="thick" style="cursor:pointer"><ellipse cx="'+cx+'" cy="'+cy+'" rx="'+(15*K)+'" ry="'+(2*thick.h*K).toFixed(1)+'" fill="#b9c6ea" fill-opacity="'+(hotK?0.6:0.28)+'"/></g>';
    s+='<g data-k="thin" style="cursor:pointer"><ellipse cx="'+cx+'" cy="'+cy+'" rx="'+(15*K)+'" ry="'+(2*thin.h*K).toFixed(1)+'" fill="'+(hotT?'#58a6ff':'#eef3ff')+'" fill-opacity="0.9"/>'+
       '<rect x="'+(cx-15*K)+'" y="'+(cy-12)+'" width="'+(30*K)+'" height="24" fill="transparent"/></g>';
    // the bulge, a boxy peanut about 3 kpc across
    const hotG=sel==='bulge';
    s+='<g data-k="bulge" style="cursor:pointer"><ellipse cx="'+cx+'" cy="'+cy+'" rx="'+(1.6*K)+'" ry="'+(1.0*K)+'" fill="'+grad(defs,'#fff1dc','#c9925a',60)+'"'+(hotG?' stroke="#58a6ff" stroke-width="1.5"':'')+'/></g>';
    const hotA=sel==='sgra';
    s+='<g data-k="sgra" style="cursor:pointer"><circle cx="'+cx+'" cy="'+cy+'" r="'+(hotA?5:3)+'" fill="#121212" stroke="#ffb02e" stroke-width="1.4"/><circle cx="'+cx+'" cy="'+cy+'" r="10" fill="transparent"/></g>';
    // the Sun, 8.2 kpc out and 25 pc above the plane, which is half a pixel here
    const hotSun=sel==='sun', sx=cx-SUN_R*K*Math.sin(Math.PI/2+2*Math.PI*orbitT/230);
    s+='<g data-k="sun" style="cursor:pointer"><circle cx="'+sx+'" cy="'+(cy-0.5)+'" r="'+(hotSun?6:4.5)+'" fill="#ffb02e" stroke="#121212" stroke-width="1.5"/>'+
       '<circle cx="'+sx+'" cy="'+cy+'" r="12" fill="transparent"/>'+
       '<text x="'+sx+'" y="'+(cy-14)+'" text-anchor="middle" font-size="12" fill="#ffb02e">the Sun</text></g>';
    s+='<text x="'+(cx+15*K)+'" y="'+(cy+2*thick.h*K+18)+'" text-anchor="end" font-size="11" fill="#9a9a9a">thin disc '+thin.h*1000+' pc, thick disc '+thick.h*1000+' pc scale height; the disc is 30 kpc across</text>';
    s+='<text x="'+(cx)+'" y="'+(cy-15*K+22)+'" text-anchor="middle" font-size="11" fill="#6b7280">the stellar halo, with about 150 globular clusters</text>';
    s+='<line x1="30" y1="'+(H-28)+'" x2="'+(30+5*K)+'" y2="'+(H-28)+'" stroke="#9a9a9a" stroke-width="2"/>';
    s+='<text x="30" y="'+(H-36)+'" font-size="11" fill="#9a9a9a">5 kpc, 16,300 light years</text>';
      e=s; }
    s+=edgeOp>=1?e:'<g opacity="'+edgeOp.toFixed(2)+'">'+e+'</g>';
  }
  if(orbitT>0) s+='<text x="30" y="30" font-size="13" fill="#ffb02e">'+Math.round(orbitT)+' million years on, '+(orbitT>=229.5?'one full orbit':Math.round(orbitT/230*100)+'% of an orbit')+'</text>';
  return s;
}
function showPart(k){
  const p=PARTS.find(x=>x.k===k); if(!p) return;
  card('A part of the Milky Way',p.n,p.nums,p.b,p.s);
}

/* ---- view: Neighbors ---- */
const LOG0=Math.log10(15), LOG1=Math.log10(1500);
function drawNear(defs){
  const cx=W/2, cy=H/2-6, Rmax=300;
  // the log radius, or the true one, where 1,500 kpc is the same outer circle
  const RL=d=>Math.max(0,(Math.log10(d)-LOG0)/(LOG1-LOG0)*Rmax), RT=d=>d/1500*Rmax;
  const R=d=>RL(d)*(1-rlin)+RT(d)*rlin;
  let s='';
  let lastR=-1e9;
  for(const d of [30,100,300,1000]){
    s+='<circle cx="'+cx+'" cy="'+cy+'" r="'+R(d).toFixed(1)+'" fill="none" stroke="#2b2b2b"/>';
    if(R(d)-lastR>13){ s+='<text x="'+(cx+4)+'" y="'+(cy-R(d)-4).toFixed(1)+'" font-size="10.5" fill="#6b7280">'+d.toLocaleString('en-US')+' kpc</text>'; lastR=R(d); }
  }
  // the Milky Way at the center, and the direction of its center marked
  s+='<line x1="'+cx+'" y1="'+cy+'" x2="'+cx+'" y2="'+(cy-Rmax-14)+'" stroke="#3d444d" stroke-dasharray="3 4"/>';
  s+='<text x="'+cx+'" y="'+(cy-Rmax-20)+'" text-anchor="middle" font-size="10.5" fill="#6b7280">toward the galactic center, l = 0</text>';
  s+='<text x="'+(cx-Rmax-10)+'" y="'+(cy+4)+'" text-anchor="end" font-size="10.5" fill="#6b7280">l = 90</text>';
  const COL={spiral:'#58a6ff',irregular:'#9be564',spheroidal:'#e0a458',elliptical:'#f28cb0'};
  const hotMW=sel==='mw';
  s+='<g data-k="mw" style="cursor:pointer"><circle cx="'+cx+'" cy="'+cy+'" r="'+(hotMW?12:9)+'" fill="'+COL.spiral+'" stroke="#121212" stroke-width="1.5"/>'+
     '<text x="'+cx+'" y="'+(cy+24)+'" text-anchor="middle" font-size="12" font-weight="700" fill="#ffb02e">the Milky Way</text></g>';
  const pts=NEAR.map(g=>{
    const l=g.l*Math.PI/180, b=g.lat*Math.PI/180;
    const dproj=Math.max(15.5,g.d*Math.cos(b));            // its distance in the plane
    const r=R(dproj);
    // from the north pole, with the center up, longitude runs to the left
    return {g, x:cx-r*Math.sin(l), y:cy-r*Math.cos(l), rr:3+8*Math.log10(Math.max(g.size,0.5)/0.5)};
  });
  // names: the big ones first, then every member whose name finds a clear
  // place beside its dot, clear of the other names, dots and the center
  const boxes=[[cx-50,cy-12,cx+50,cy+30]], names={};
  const dots=pts.map(p=>[p.x,p.y,p.rr]).concat([[cx,cy,12]]);
  const free=b=>boxes.every(q=>!(b[0]<q[2]&&b[2]>q[0]&&b[1]<q[3]&&b[3]>q[1]))&&
    dots.every(([x,y,r])=>{ const qx=Math.max(b[0],Math.min(x,b[2])), qy=Math.max(b[1],Math.min(y,b[3])); return Math.hypot(qx-x,qy-y)>r+1; })&&b[0]>4&&b[2]<W-4;
  for(const p of [...pts].sort((a,b)=>(b.g.big?1:0)-(a.g.big?1:0)||b.rr-a.rr)){
    const fs=p.g.big?11.5:10.5, w=p.g.n.length*fs*0.53, left=p.x<cx;
    const C=left?[['end',p.x-p.rr-5,p.y+4],['start',p.x+p.rr+5,p.y+4]]:[['start',p.x+p.rr+5,p.y+4],['end',p.x-p.rr-5,p.y+4]];
    C.push(['middle',p.x,p.y-p.rr-5],['middle',p.x,p.y+p.rr+13],[C[0][0],C[0][1]+(C[0][0]==='end'?-2:2),p.y-8],[C[0][0],C[0][1]+(C[0][0]==='end'?-2:2),p.y+16]);
    for(const [a,x,y] of C){ const x0=a==='end'?x-w:a==='middle'?x-w/2:x, b=[x0,y-fs+1,x0+w,y+2];
      if(free(b)){ boxes.push(b); names[p.g.k]=[a,x,y,fs]; break; } }
  }
  for(const p of pts){
    const hot=sel===p.g.k, c=COL[p.g.type];
    s+='<g data-k="'+p.g.k+'" style="cursor:pointer">';
    if(hot) s+='<circle cx="'+p.x.toFixed(1)+'" cy="'+p.y.toFixed(1)+'" r="'+(p.rr+6)+'" fill="none" stroke="#58a6ff" stroke-width="1.4"/>';
    s+='<circle cx="'+p.x.toFixed(1)+'" cy="'+p.y.toFixed(1)+'" r="'+p.rr.toFixed(1)+'" fill="'+c+'" fill-opacity="0.85" stroke="#121212" stroke-width="1"/>';
    s+='<circle cx="'+p.x.toFixed(1)+'" cy="'+p.y.toFixed(1)+'" r="'+Math.max(p.rr+4,9)+'" fill="transparent"/>';
    const nm=names[p.g.k];
    if(nm) s+='<text class="halo" x="'+nm[1].toFixed(1)+'" y="'+nm[2].toFixed(1)+'" text-anchor="'+nm[0]+'" font-size="'+nm[3]+'" fill="'+(hot?'#58a6ff':c)+'"'+(p.g.big?'':' fill-opacity="0.85"')+'>'+esc(p.g.n)+'</text>';
    s+='</g>';
  }
  // legend
  let lx=30, ly=H-30;
  for(const [k,lab] of [['spiral','spiral'],['irregular','irregular'],['spheroidal','dwarf spheroidal'],['elliptical','dwarf elliptical']]){
    s+='<circle cx="'+lx+'" cy="'+ly+'" r="4.5" fill="'+COL[k]+'"/><text x="'+(lx+10)+'" y="'+(ly+4)+'" font-size="11" fill="#9a9a9a">'+lab+'</text>';
    lx+=lab.length*6.4+34;
  }
  s+='<text x="'+(W-20)+'" y="'+(H-26)+'" text-anchor="end" font-size="11" fill="#6b7280">seen from above the north galactic pole; radius '+(rlin>0.5?'to true scale':'on a log scale')+'</text>';
  return s;
}
function showNear(k){
  if(k==='mw'){ const m=PARTS.find(p=>p.k==='whole'); card('The Local Group',m.n,m.nums,m.b,m.s); return; }
  const g=NEAR.find(x=>x.k===k); if(!g) return;
  const kly=(g.d*3.2616).toFixed(0);
  card(g.tTxt,g.n,[['distance',g.d.toLocaleString('en-US')+' kpc, '+Number(kly).toLocaleString('en-US')+',000 light years'],
    ['size',g.sizeTxt],['sits in',g.group]],g.b,'McConnachie 2012');
}

/* ---- render ---- */
function render(){
  gid=0;
  const defs=[];
  let body= view==='kinds'?drawKinds(defs) : view==='sizes'?drawSizes(defs)
          : view==='ours'?drawOurs(defs) : drawNear(defs);
  el.innerHTML='<svg viewBox="0 0 '+W+' '+H+'" xmlns="http://www.w3.org/2000/svg" id="gsvg">'+
    '<rect width="'+W+'" height="'+H+'" fill="#121212"/><defs>'+defs.join('')+'</defs>'+body+'</svg>';
}
function show(k){
  sel=k;
  if(view==='kinds') showKind(k); else if(view==='sizes') showSize(k);
  else if(view==='ours') showPart(k); else showNear(k);
  render();
}
el.addEventListener('pointerover',e=>{ const g=e.target.closest('[data-k]'); if(g) show(g.getAttribute('data-k')); });
el.addEventListener('click',e=>{ const g=e.target.closest('[data-k]'); if(g) show(g.getAttribute('data-k')); });

function subHTML(v){
  if(v==='kinds') return '<span class="lab">one galaxy along the fork</span><input type="range" id="morph" min="0" max="1000" value="'+Math.round(morph*1000)+'" aria-label="one galaxy slid along the fork, E0 to Sc">'+
    '<button type="button" data-bar'+(mbar?' class="on"':'')+'>with a bar</button>';
  if(v==='sizes') return '<button type="button" data-same'+(same>0.5?' class="on"':'')+'>all one size</button>';
  if(v==='ours') return '<button type="button" data-s="face"'+(tilt<0.5?' class="on"':'')+'>Face-on</button><button type="button" data-s="edge"'+(tilt>=0.5?' class="on"':'')+'>Edge-on</button>'+
    '<span class="lab">tilt</span><input type="range" id="tilt" min="0" max="900" value="'+Math.round(tilt*900)+'" aria-label="tilt, face-on to edge-on">'+
    '<button type="button" class="play" data-play aria-pressed="false">Play an orbit</button>';
  return '<button type="button" data-r="0"'+(rlin<0.5?' class="on"':'')+'>log radius</button><button type="button" data-r="1"'+(rlin>=0.5?' class="on"':'')+'>true radius</button>';
}
function setView(v){
  view=v; sel=null;
  for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on',b.dataset.v===v);
  stopOrbit();
  const sub=document.getElementById('sub');
  sub.hidden=false; sub.innerHTML=subHTML(v);
  render();
  // each view opens on the Milky Way
  show(v==='kinds'?'MW':v==='sizes'?'mw':v==='ours'?'whole':'mw');
}
document.getElementById('views').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setView(b.dataset.v); });
function onSub(b,on){ for(const x of document.querySelectorAll('#sub button:not(.play)')) x.classList.toggle('on',x===b||(on&&x.matches(on))); }
document.getElementById('sub').addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return;
  if(b.dataset.s!==undefined){ side=b.dataset.s; onSub(b); const to=side==='edge'?1:0;
    tween('tilt',tilt,to,1100,v=>{ tilt=v; const t=document.getElementById('tilt'); if(t) t.value=Math.round(v*900); }); return; }
  if(b.hasAttribute('data-bar')){ mbar=!mbar; b.classList.toggle('on',mbar); sel=null; setMorph(morph); return; }
  if(b.hasAttribute('data-same')){ const to=same>0.5?0:1; b.classList.toggle('on',to===1); render(); tween('same',same,to,1000,v=>{ same=v; },null,placeSizes); return; }
  if(b.dataset.r!==undefined){ onSub(b); tween('rlin',rlin,+b.dataset.r,1100,v=>{ rlin=v; }); return; }
  if(b.hasAttribute('data-play')) playOrbit(b);
});
document.getElementById('sub').addEventListener('input',e=>{
  if(e.target.id==='morph') setMorph(+e.target.value/1000);
  if(e.target.id==='tilt'){ if(tws.tilt) cancelAnimationFrame(tws.tilt); tilt=+e.target.value/900; side=tilt>=0.5?'edge':'face';
    onSub(null, side==='edge'?'[data-s=edge]':'[data-s=face]'); render(); }
});
/* ---- one orbit of the Sun, 230 million years in about nine seconds ---- */
let orbit=null;
function stopOrbit(){ if(!orbit) return; cancelAnimationFrame(orbit.raf); clearTimeout(orbit.t); orbit=null;
  const b=document.querySelector('#sub [data-play]'); if(b){ b.textContent='Play an orbit'; b.setAttribute('aria-pressed','false'); } }
function playOrbit(b){
  if(orbit){ stopOrbit(); return; }
  if(orbitT>=229.5) orbitT=0;
  orbit={raf:0,t:0}; b.textContent='Pause'; b.setAttribute('aria-pressed','true');
  if(RM){ const step=()=>{ orbitT=Math.min(230,Math.floor(orbitT/57.5+1e-9)*57.5+57.5); render(); if(orbitT>=230) stopOrbit(); else orbit.t=setTimeout(step,900); }; orbit.t=setTimeout(step,300); return; }
  const T0=performance.now()-orbitT/230*9000;
  const tick=now=>{ orbitT=Math.min(230,(now-T0)/9000*230); render(); if(orbitT<230) orbit.raf=requestAnimationFrame(tick); else stopOrbit(); };
  orbit.raf=requestAnimationFrame(tick);
}
el.addEventListener('keydown',e=>{
  const d={ArrowRight:1,ArrowUp:1,ArrowLeft:-1,ArrowDown:-1}[e.key]; if(d===undefined) return;
  if(view==='kinds'){ e.preventDefault(); setMorph(Math.max(0,Math.min(1,morph+d*0.05))); }
  else if(view==='ours'){ e.preventDefault(); if(tws.tilt) cancelAnimationFrame(tws.tilt); tilt=Math.max(0,Math.min(1,tilt+d/18)); const t=document.getElementById('tilt'); if(t) t.value=Math.round(tilt*900); side=tilt>=0.5?'edge':'face'; render(); }
});
setView('kinds');
window.__gal=()=>({view,side,sel,morph,mbar,same,tilt,orbitT,rlin,playing:!!orbit,kinds:KINDS.length,sizes:SIZES.length,parts:PARTS.length,near:NEAR.length,
  marks:document.querySelectorAll('#gsvg [data-k]').length});
</script>
</body>
</html>
"""

html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__KINDS__", _js(KINDS)).replace("__SIZES__", _js(SIZES))
        .replace("__PARTS__", _js(PARTS)).replace("__NEAR__", _js(NEIGHBORS))
        .replace("__SUNR__", str(SUN_R))
        .replace("__CAPTION__", CAPTION).replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__NOTE3__", NOTE3)
        .replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(KINDS)} kinds, {len(SIZES)} galaxies to "
      f"scale, {len(PARTS)} parts of the Milky Way, {len(NEIGHBORS)} neighbors")
