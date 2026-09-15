#!/usr/bin/env python3
"""Generate stars.html, Stars: the Hertzsprung-Russell diagram and a life on it.

Luminosity against surface temperature, hot on the left as Russell drew it,
with the spectral classes as bands, lines of equal radius, and thirty-six
named stars placed from their published values. A mass slider sets a star,
and a life slider carries it along its track: the main sequence, the giant
stages, and the end its mass allows. The Sun's track is the default.

Data: tools/stars_data.py.

Usage: python3 build_stars.py
"""

import json
from pathlib import Path

import apa
from stars_data import CLASSES, MAIN_SEQUENCE, STARS, REFS

OUT = Path(__file__).parent.parent / "stars.html"

NOTE1 = ("Every star is a point on this diagram: how much light it gives "
         "against how hot its surface is, with the hot end on the left, the "
         "way Russell drew it in 1914. Most stars fall on the diagonal band, "
         "the main sequence, where hydrogen burns in the core and mass alone "
         "sets the place: heavier is hotter and brighter. The dashed lines are "
         "equal radius, since the same temperature at more light means a "
         "bigger surface.")

NOTE2 = ("The sliders set a star's mass and carry it through its life. The "
         "main sequence lasts about ten billion years for the Sun and a "
         "million for the heaviest; then the core runs out of hydrogen, the "
         "star swells into the giants at the upper right, and ends as the "
         "white dwarfs at the lower left, or as a supernova and a neutron "
         "star or black hole, off the diagram, if it began with more than "
         "about eight suns.")

METHOD = ("The named stars carry the temperature, luminosity, mass and "
          "distance their Wikipedia article gives, cited one by one; the "
          "radius on the card is worked from the first two, since luminosity "
          "goes as the radius squared and the temperature to the fourth. The "
          "main sequence is the dwarf table of Pecaut and Mamajek. The life "
          "track is a sketch in the right places: the main sequence lifetime "
          "is ten billion years times mass over luminosity; the giant and "
          "supergiant stages take the last tenth of the life, at the "
          "luminosities and temperatures stars of that mass reach; the white "
          "dwarf then cools for longer than the diagram can hold. The track "
          "is not a model run, and a real star wanders more than a line. The "
          "class bands follow the dwarf table, moved a few hundred kelvin "
          "where a named giant or supergiant would otherwise fall on the "
          "wrong side of its published letter.")


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


stars = [{"n": n, "T": T, "L": L, "c": c, "M": M, "d": d, "r": r, "b": b}
         for n, T, L, c, M, d, r, b in STARS]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Stars &middot; Altazor</title>
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
.controls { display:grid; grid-template-columns:auto 1fr auto; gap:8px 14px; align-items:center;
  margin:0 0 12px; max-width:760px; font-size:13px; color:var(--muted); }
.controls input[type=range] { width:100%; accent-color:var(--accent); }
.controls output { color:var(--text); font-variant-numeric:tabular-nums; white-space:nowrap; }
.presets { display:flex; gap:6px; flex-wrap:wrap; margin:0 0 12px; }
.presets button { background:var(--panel); color:var(--muted); border:1px solid var(--line);
  border-radius:999px; padding:5px 11px; font-size:12.5px; cursor:pointer; font-family:inherit; }
.presets button:hover { color:var(--text); border-color:#3d3d3d; }
.presets button[aria-pressed=true] { color:#0b0b0b; background:var(--accent); border-color:var(--accent); font-weight:700; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; }
#diagram svg { width:100%; height:auto; display:block; user-select:none; }
.side { flex:0 0 300px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:16px; }
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
  <nav class="site"><a href="library.html">&larr; Library &middot; The Universe</a><a href="galaxies.html">Galaxies</a><a href="solar-system.html">The Solar System</a><a href="matter.html">Matter</a></nav>
</header>
<h1>Stars</h1>
<div class="controls">
  <label for="mass">mass</label><input type="range" id="mass" min="-100" max="160" step="1" value="0"><output id="massOut"></output>
  <label for="life">life</label><input type="range" id="life" min="0" max="1150" step="1" value="0"><output id="lifeOut"></output>
</div>
<div class="presets" id="presets"></div>
<div class="stage">
  <div id="diagram"></div>
  <div class="side"><div class="card">
    <div id="kindTxt"></div>
    <div id="nameTxt">A star under the cursor lands here</div>
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
const STARS=__STARS__, CLASSES=__CLASSES__, MS=__MS__;
const W=980, H=720, P={x:88,y:36,w:850,h:610};       // the plot
const LT0=Math.log10(120000), LT1=Math.log10(2300);  // hot on the left
const LL0=-5, LL1=6.5;
const el=document.getElementById('diagram');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const X=T=>P.x+(Math.log10(T)-LT0)/(LT1-LT0)*P.w;
const Y=L=>P.y+P.h-(Math.log10(L)-LL0)/(LL1-LL0)*P.h;
const TSUN=5772;
let mass=1, life=0, hot=null;

/* ---- numbers ---- */
const SUP={'-':'⁻','0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'};
const sup=n=>String(n).split('').map(c=>SUP[c]||c).join('');
function num(v){
  if(v>=1e5||v<0.001){ let e=Math.floor(Math.log10(v)), m=v/Math.pow(10,e); if(m>=9.995){m/=10;e++;} return m.toFixed(1)+'×10'+sup(e); }
  if(v>=100) return Math.round(v).toLocaleString('en-US');
  if(v>=10) return v.toFixed(1);
  if(v>=1) return v.toFixed(2);
  return v.toFixed(3).replace(/0+$/,'');
}
function years(g){            // billions of years
  const y=g*1e9;
  if(y>=1e9) return num(g)+' billion years';
  if(y>=1e6) return num(y/1e6)+' million years';
  if(y>=1e3) return num(y/1e3)+' thousand years';
  return num(y)+' years';
}
const radius=(T,L)=>Math.sqrt(L)*Math.pow(TSUN/T,2);           // solar radii
const cls=T=>(CLASSES.find(c=>T>=c[1]&&T<c[2])||CLASSES[T>=29000?0:6])[0];
// colour of a star by temperature, a blackbody eyeballed onto the classes
function colour(T){ const c=CLASSES.find(c=>T>=c[1]&&T<c[2]); return c?c[3]:(T>=29000?'#9bb0ff':'#ffbb66'); }

/* ---- the main sequence, by mass, from the dwarf table ---- */
function ms(M){
  const lm=Math.log10(M);
  let i=0; while(i<MS.length-2 && Math.log10(MS[i+1][0])<lm) i++;
  const [m0,t0,l0]=MS[i], [m1,t1,l1]=MS[i+1];
  const f=(lm-Math.log10(m0))/(Math.log10(m1)-Math.log10(m0));
  return {T:Math.pow(10,Math.log10(t0)+f*(Math.log10(t1)-Math.log10(t0))),
          L:Math.pow(10,Math.log10(l0)+f*(Math.log10(l1)-Math.log10(l0)))};
}
const lifetime=M=>10*M/ms(M).L;                                 // billions of years on the main sequence

/* ---- a life, as knots of (fraction of the life, T, L, the phase) ---- */
function track(M){
  const z=ms(M), T0=z.T, L0=z.L, k=[];
  k.push([0,T0,L0,'on the main sequence, fusing hydrogen in the core']);
  if(M<0.5){
    k.push([0.9,T0*0.97,L0*1.6,'near the end of the main sequence, still fusing hydrogen']);
    k.push([1.0,15000,0.01,'a helium white dwarf: the core, laid bare, with no fusion left']);
    k.push([1.15,5000,1e-4,'a white dwarf cooling toward the dark']);
  } else if(M<8){
    k.push([0.9,T0*0.93,L0*2.2,'the end of the main sequence; the core is out of hydrogen']);
    k.push([0.93,Math.sqrt(T0*4800),L0*3,'a subgiant: hydrogen burns in a shell and the star swells']);
    k.push([0.97,3100,2500*Math.pow(M,0.5),'the tip of the red giant branch']);
    k.push([0.975,M<2?4800:4000,50*M,'burning helium in the core, the red clump']);
    k.push([0.995,3000,5000*Math.pow(M,0.6),'the asymptotic giant branch, shedding its outer layers']);
    k.push([1.0,80000,3000,'the hot core lit up as a planetary nebula fades around it']);
    k.push([1.05,25000,0.01,'a white dwarf of about 0.6 suns, cooling']);
    k.push([1.15,6000,1e-4,'a white dwarf cooling toward the dark']);
  } else {
    k.push([0.9,T0*0.85,L0*2.0,'the end of the main sequence; the core is out of hydrogen']);
    if(M<30){
      k.push([0.93,8000,L0*2.4,'crossing the gap fast, in a few thousand years']);
      k.push([0.97,3600,L0*(M<12?4:2.5),'a red supergiant, fusing heavier and heavier elements']);
      k.push([1.0,3600,L0*(M<12?4:2.5),'core collapse: a supernova, and a '+(M<25?'neutron star':'black hole')+' left behind']);
    } else {
      k.push([0.95,30000,L0*2.5,'a luminous blue variable, shedding mass in eruptions']);
      k.push([0.98,60000,L0*2,'a Wolf-Rayet star, its hydrogen envelope gone']);
      k.push([1.0,60000,L0*2,'core collapse: a supernova or a direct fall into a black hole']);
    }
  }
  return k;
}
// the star at a fraction f of its life, interpolated in log between knots
function at(M,f){
  const k=track(M);
  if(f>=k[k.length-1][0]) return {T:k[k.length-1][1],L:k[k.length-1][2],phase:k[k.length-1][3],ended:M>=8};
  let i=0; while(k[i+1][0]<=f) i++;
  const [f0,T0,L0,p0]=k[i], [f1,T1,L1]=k[i+1], u=(f-f0)/(f1-f0);
  return {T:Math.pow(10,Math.log10(T0)+u*(Math.log10(T1)-Math.log10(T0))),
          L:Math.pow(10,Math.log10(L0)+u*(Math.log10(L1)-Math.log10(L0))),phase:p0,ended:false};
}

/* ---- the card ---- */
function card(kind,name,rows,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').textContent=name;
  document.getElementById('numTxt').innerHTML=rows.map(([k,v])=>'<b>'+esc(k)+'</b> '+esc(v)).join('<br>');
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').textContent=src;
}
const REGION={main:'On the main sequence',giant:'A giant',super:'A supergiant',wd:'A white dwarf'};
function showStar(s){
  card(REGION[s.r], s.n, [['class',s.c+', a '+cls(s.T)+' star'],['surface',Math.round(s.T).toLocaleString('en-US')+' K'],
    ['luminosity',num(s.L)+' Suns'],['radius',num(radius(s.T,s.L))+' Suns, from the two above'],
    ['mass',s.M?num(s.M)+' Suns':'not well known'],['distance',s.d<0.001?'8 light minutes':num(s.d)+' light years']],
    s.b,'Wikipedia, '+s.n.replace(/ A$| B$| Aa$| A\\b/,''));
}
function showLife(){
  const a=at(mass,life), tl=lifetime(mass), age=life<=1?life*tl:tl*(1+(life-1)*0.3);
  const fate=mass<8?(mass<0.5?'a helium white dwarf, in a time longer than the universe has existed':'a white dwarf')
            :mass<25?'a supernova and a neutron star':'a supernova and a black hole';
  card('A star of '+num(mass)+' solar masses', a.ended?'ended':a.phase,
    [['age',years(age)],['main sequence',years(tl)],['surface',a.ended?'gone':Math.round(a.T).toLocaleString('en-US')+' K, class '+cls(a.T)],
     ['luminosity',a.ended?'the supernova outshone the galaxy for weeks':num(a.L)+' Suns'],
     ['radius',a.ended?'a dozen kilometres, or a horizon':num(radius(a.T,a.L))+' Suns'],['fate',fate]],
    mass<0.5?'A red dwarf burns so slowly that none has yet left the main sequence; the universe is too young. Its whole life, mixed all the way through, ends as a helium white dwarf.'
    :mass<8?'The Sun\\u2019s kind of life: ten billion years of quiet, then a swelling into a red giant that reaches about to the Earth\\u2019s orbit and may swallow it, a brief helium stage, and a slow cooling as a white dwarf the size of the Earth.'
    :'A short and violent life. The heavier the star, the faster it burns: the main sequence is over in millions of years, the end is a core collapse, and the elements it made are thrown out for the next generation.',
    'Pecaut and Mamajek 2013; Iben 1967; Heger and others 2003');
}

/* ---- the drawing ---- */
function render(){
  let s='<svg viewBox="0 0 '+W+' '+H+'" xmlns="http://www.w3.org/2000/svg" id="hsvg">';
  s+='<rect width="'+W+'" height="'+H+'" fill="#121212"/>';
  // class bands
  for(const [c,lo,hi,col] of CLASSES){
    const x0=X(Math.min(hi,120000)), x1=X(Math.max(lo,2300));
    s+='<rect x="'+x0.toFixed(1)+'" y="'+P.y+'" width="'+(x1-x0).toFixed(1)+'" height="'+P.h+'" fill="'+col+'" fill-opacity="0.045"/>';
    s+='<text x="'+((x0+x1)/2).toFixed(1)+'" y="'+(P.y+16)+'" text-anchor="middle" font-size="13" font-weight="700" fill="'+col+'" fill-opacity="0.7">'+c+'</text>';
  }
  s+='<rect x="'+P.x+'" y="'+P.y+'" width="'+P.w+'" height="'+P.h+'" fill="none" stroke="#2b2b2b"/>';
  // radius lines: log L = 2 log R + 4 log(T/Tsun)
  for(const R of [0.001,0.01,0.1,1,10,100,1000]){
    const pts=[]; for(let lt=LT0; lt>=LT1; lt-=0.01){ const T=Math.pow(10,lt), L=R*R*Math.pow(T/TSUN,4);
      const y=Y(L); if(y<P.y||y>P.y+P.h) continue; pts.push(X(T).toFixed(1)+','+y.toFixed(1)); }
    if(pts.length<2) continue;
    s+='<polyline points="'+pts.join(' ')+'" fill="none" stroke="#3d444d" stroke-dasharray="3 5" stroke-width="1"/>';
    const [lx,ly]=pts[pts.length-1].split(',');
    s+='<text x="'+(+lx-4)+'" y="'+(+ly-4)+'" text-anchor="end" font-size="10" fill="#6b7280">'+(R>=1?R:R)+' R☉</text>';
  }
  // axes
  for(const T of [100000,40000,20000,10000,5000,3000]) s+='<text x="'+X(T).toFixed(1)+'" y="'+(P.y+P.h+18)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">'+T.toLocaleString('en-US')+' K</text>';
  for(let e=-4;e<=6;e+=2) s+='<text x="'+(P.x-8)+'" y="'+(Y(Math.pow(10,e))+4).toFixed(1)+'" text-anchor="end" font-size="11" fill="#9a9a9a">10'+sup(e)+'</text>';
  s+='<text x="'+(P.x+P.w/2)+'" y="'+(P.y+P.h+40)+'" text-anchor="middle" font-size="12" fill="#9a9a9a">surface temperature, hotter to the left</text>';
  s+='<text transform="translate(18,'+(P.y+P.h/2)+') rotate(-90)" text-anchor="middle" font-size="12" fill="#9a9a9a">luminosity, in Suns</text>';
  // the main sequence at birth
  s+='<polyline points="'+MS.map(([m,T,L])=>X(T).toFixed(1)+','+Y(L).toFixed(1)).join(' ')+'" fill="none" stroke="#f4efe2" stroke-opacity="0.25" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>';
  // region names
  for(const [x,y,t] of [[X(9000),Y(700),'main sequence'],[X(4200),Y(300)-14,'giants'],[X(6000),Y(1.2e5)-16,'supergiants'],[X(15000),Y(0.003)+22,'white dwarfs']])
    s+='<text x="'+x.toFixed(1)+'" y="'+y.toFixed(1)+'" text-anchor="middle" font-size="12" fill="#6b7280" font-style="italic">'+t+'</text>';
  // the life track of the chosen mass
  const k=track(mass), pts=[];
  for(let f=0; f<=1.15; f+=0.0025){ const a=at(mass,f); if(a.ended) break; pts.push(X(a.T).toFixed(1)+','+Y(a.L).toFixed(1)); }
  s+='<polyline points="'+pts.join(' ')+'" fill="none" stroke="#58a6ff" stroke-width="2" stroke-opacity="0.85" stroke-linejoin="round"/>';
  for(const [f,T,L] of k) s+='<circle cx="'+X(T).toFixed(1)+'" cy="'+Y(L).toFixed(1)+'" r="2.2" fill="#58a6ff" fill-opacity="0.6"/>';
  // the named stars, labels nudged down where two sit on top of each other
  const placed=[];
  for(let i=0;i<STARS.length;i++){
    const st=STARS[i], x=X(st.T), y=Y(st.L), r=Math.max(3,Math.min(9,3+Math.log10(radius(st.T,st.L)+1)*2.2));
    const isHot=hot===i;
    let ly=y+3.5;
    for(const q of placed) if(Math.abs(q.x-x)<70 && Math.abs(q.ly-ly)<11) ly=q.ly+11;
    placed.push({x,ly});
    s+='<g data-i="'+i+'" style="cursor:pointer">'+
       '<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="'+r.toFixed(1)+'" fill="'+colour(st.T)+'" stroke="'+(isHot?'#ffffff':'#121212')+'" stroke-width="'+(isHot?1.8:1)+'"/>'+
       (st.n==='the Sun'?'<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="'+(r+4)+'" fill="none" stroke="#ffb02e" stroke-width="1.3"/>':'')+
       '<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="'+(r+5)+'" fill="transparent"/>'+
       '<text x="'+(x+r+4).toFixed(1)+'" y="'+ly.toFixed(1)+'" font-size="10" fill="'+(isHot?'#ffffff':'#8a94a6')+'">'+esc(st.n)+'</text></g>';
  }
  // the chosen star now
  const a=at(mass,life);
  if(!a.ended){
    const x=X(a.T), y=Y(a.L), r=Math.max(4,Math.min(16,4+Math.log10(radius(a.T,a.L)+1)*3));
    s+='<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="'+(r+5)+'" fill="none" stroke="#58a6ff" stroke-width="1.5"/>';
    s+='<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="'+r.toFixed(1)+'" fill="'+colour(a.T)+'" stroke="#58a6ff" stroke-width="1.5" data-now="1"/>';
  } else {
    s+='<text x="'+(P.x+P.w-12)+'" y="'+(P.y+P.h-14)+'" text-anchor="end" font-size="12" fill="#58a6ff">the star has gone: a supernova, and a remnant off this diagram</text>';
  }
  s+='</svg>';
  el.innerHTML=s;
  document.getElementById('massOut').textContent=num(mass)+' Suns, main sequence '+years(lifetime(mass));
  document.getElementById('lifeOut').textContent=(life<=1?(life*100).toFixed(0)+'% of the main sequence life':'after: '+((life-1)*100).toFixed(0)+'% more');
}
function setMass(m){ mass=m; document.getElementById('mass').value=Math.round(Math.log10(m)*100); render(); showLife();
  for(const b of document.querySelectorAll('#presets button')) b.setAttribute('aria-pressed', Math.abs(+b.dataset.m-m)<1e-9?'true':'false'); }
function setLife(f){ life=f; document.getElementById('life').value=Math.round(f*1000); render(); showLife(); }
document.getElementById('mass').addEventListener('input',e=>setMass(Math.pow(10,+e.target.value/100)));
document.getElementById('life').addEventListener('input',e=>setLife(+e.target.value/1000));
const PRE=[[0.2,'a red dwarf'],[1,'the Sun'],[2,'Sirius A'],[5,'a B star'],[17,'Betelgeuse'],[40,'an O star']];
document.getElementById('presets').innerHTML=PRE.map(([m,l])=>'<button type="button" data-m="'+m+'">'+l+'</button>').join('');
document.getElementById('presets').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setMass(+b.dataset.m); });
el.addEventListener('pointerover',e=>{ const g=e.target.closest('[data-i]'); if(g){ hot=+g.dataset.i; render(); showStar(STARS[hot]); } });
el.addEventListener('pointerleave',()=>{ hot=null; render(); showLife(); });
setMass(1);
window.__stars=()=>({mass,life,n:STARS.length,at:at(mass,life),lifetime:lifetime(mass),ms:ms(mass),track:track(mass)});
</script>
</body>
</html>
"""

html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__STARS__", _js(stars)).replace("__CLASSES__", _js(CLASSES)).replace("__MS__", _js(MAIN_SEQUENCE))
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(STARS)} stars, {len(MAIN_SEQUENCE)} main sequence points")
