#!/usr/bin/env python3
"""Generate brain.html, The Brain: outside, inside, and over a lifetime.

Three views. The outside: the left hemisphere seen from the side, its four
lobes, the cerebellum and the brainstem, and on top of them the strips and
patches that do one job each: moving, feeling, speaking, hearing, seeing.
The inside: the brain cut down the middle, with the bridge between the
halves, the thalamus, the small regulators under it, the brainstem in its
three parts, and, drawn in their places though they lie off the midline,
the hippocampus, the amygdala and the basal ganglia. The lifetime: the
brain's mass from birth to old age, men and women, with a marker that drags
along the years.

Data: tools/brain_data.py.

Usage: python3 build_brain.py
"""

import json
from pathlib import Path

import apa
from brain_data import WHOLE, OUTSIDE, INSIDE, GROWTH, GROWTH_NOTES, REFS

OUT = Path(__file__).parent.parent / "brain.html"

NOTE1 = ("A kilogram and a half of tissue that is two percent of the body "
         "and takes a fifth of its energy. Seen from the side it is four "
         "lobes, a little brain tucked under the back, and the stalk that "
         "joins it to the spinal cord; each answers under the pointer, and "
         "so do the strips and patches laid over them where one job is done "
         "in one place: moving, feeling, speech, hearing, sight.")

NOTE2 = ("Cut down the middle, the brain shows what the lobes hide: the "
         "bridge of two hundred million fibres between the halves, the "
         "thalamus at the centre through which nearly everything passes, "
         "the small regulators of temperature, hunger and hormones beneath "
         "it, and the brainstem that keeps breathing going. The third view "
         "is the same organ over a lifetime: a quarter of its adult mass at "
         "birth, nine tenths by three, and a slow loss after fifty.")

METHOD = ("The drawings are diagrams of a left hemisphere from the side and "
          "from the midline, not tracings of a particular brain; the lobes "
          "are divided along the central sulcus, the lateral fissure and the "
          "line from the parieto-occipital sulcus to the preoccipital notch, "
          "as anatomy texts do, and the functional patches are placed where "
          "they usually are, on the left. Cell counts are Azevedo and "
          "colleagues' 2009 isotropic-fractionator figures for four adult "
          "men's brains, with the uncertainties they report, about a tenth. "
          "The masses by age are the means of Dekaban and Sadowsky's 4,736 "
          "autopsies, with their age ranges taken at the midpoint and the "
          "curve drawn straight between points; individual brains vary by "
          "some 15 percent around them. The age axis is a square-root "
          "scale, so that the first three years, where most of the growth "
          "is, have room.")


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


outside = [{"k": k, "n": n, "kind": kind, "b": b, "num": num, "s": s} for k, n, kind, b, num, s in OUTSIDE]
inside = [{"k": k, "n": n, "kind": kind, "b": b, "num": num, "s": s} for k, n, kind, b, num, s in INSIDE]
growth = [{"age": a, "m": m, "f": f} for a, m, f in GROWTH]
gnotes = [{"age": a, "t": t} for a, t in GROWTH_NOTES]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Brain &middot; Altazor</title>
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
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; }
#diagram svg { width:100%; height:auto; display:block; user-select:none; }
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
  <nav class="site"><a href="library.html">&larr; Library &middot; Homo Sapiens</a><a href="body.html">The Human Body</a><a href="nervous-systems.html">Nervous Systems</a><a href="cell.html">The Cell</a></nav>
</header>
<h1>The Brain</h1>
<div class="bar" id="views"><button data-v="outside" class="on">The outside</button><button data-v="inside">The inside</button><button data-v="growth">A lifetime</button></div>
<div class="controls" id="ageCtl" hidden><label>the marker</label><output id="ageOut"></output></div>
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
const WHOLE=__WHOLE__, OUTSIDE=__OUTSIDE__, INSIDE=__INSIDE__, GROWTH=__GROWTH__, GNOTES=__GNOTES__;
const W=980;
const el=document.getElementById('diagram');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const fmt=n=>n.toLocaleString('en-US');
let view='outside', hot=null, age=20;

/* ---- the card ---- */
function card(kind,name,rows,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').innerHTML=name;
  document.getElementById('numTxt').innerHTML=rows.filter(r=>r[1]).map(([k,v])=>'<b>'+esc(k)+'</b> '+v).join('<br>');
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').textContent=src;
}
function showRegion(list,k){ const p=list.find(x=>x.k===k); card(p.kind, esc(p.n), [['one number',esc(p.num)]], p.b, p.s); }
function showWhole(){ card('The whole organ','A human brain, from the left',[
  ['mass','about '+fmt(WHOLE.mass_g)+' g, '+WHOLE.body_pct+'% of the body'],
  ['energy','about '+WHOLE.energy_pct+'% of the body\\u2019s at rest, near '+WHOLE.watts+' watts'],
  ['neurons','86 billion, and about as many other cells'],
  ['where they are','16 billion in the cortex, 69 billion in the cerebellum, under 1 billion in all the rest'],
  ['fibres','about '+fmt(WHOLE.fibres_km_m)+' km of insulated fibre in a man of twenty, '+fmt(WHOLE.fibres_km_f)+' in a woman'],
  ['blood','about '+fmt(WHOLE.blood_ml_min)+' mL a minute, '+WHOLE.blood_pct+'% of what the heart pumps']],
  'The cortex is a sheet 2 to 4 mm thick and about a quarter of a square metre in all, two thirds of it folded out of sight. Each lobe, strip and patch answers under the pointer.','Azevedo et al. 2009; Marner et al. 2003; Raichle & Gusnard 2002; Toro et al. 2008; Wikipedia, Human brain'); }
function showInside(){ card('The inside','Cut down the middle',[
  ['the cortex','82% of the mass, 16 billion neurons'],
  ['the cerebellum','10% of the mass, 69 billion neurons'],
  ['everything else','8% of the mass, under a billion neurons: the thalamus, the brainstem and all the deep nuclei']],
  'The midline cut shows the corpus callosum, the thalamus and the brainstem in place. The hippocampus, the amygdala and the basal ganglia lie off to the side inside each hemisphere and are drawn dashed where they would project onto the cut.','Azevedo et al. 2009; Wikipedia, Human brain'); }
function interp(a,key){ for(let i=0;i<GROWTH.length-1;i++){ const p=GROWTH[i], q=GROWTH[i+1]; if(a>=p.age&&a<=q.age) return p[key]+(q[key]-p[key])*(a-p.age)/(q.age-p.age); } return GROWTH[GROWTH.length-1][key]; }
function showAge(a){ const m=interp(a,'m'), f=interp(a,'f'); const pm=Math.max(...GROWTH.map(g=>g.m)), pf=Math.max(...GROWTH.map(g=>g.f));
  let note=GNOTES[0]; for(const n of GNOTES) if(Math.abs(n.age-a)<=Math.abs(note.age-a)) note=n;
  card('At age', a===0?'birth':a+(a===1?' year':' years'), [['a man\\u2019s brain','about '+fmt(Math.round(m))+' g, '+(m/pm*100).toFixed(0)+'% of its peak'],['a woman\\u2019s','about '+fmt(Math.round(f))+' g, '+(f/pf*100).toFixed(0)+'% of its peak'],['neurons','the same 86 billion or so throughout; what changes is their branches, their insulation and the connections between them']], note.t, 'Dekaban & Sadowsky 1978; Marner et al. 2003'); }

/* ---- the outside ---- */
const OUTLINE='M160,330 C160,215 265,118 425,110 C585,102 742,150 792,262 C822,332 802,402 742,432 C690,455 630,450 580,466 C500,482 380,470 300,434 C270,420 258,398 268,382 C230,374 178,386 160,330 Z';
const CS='M515,104 C495,170 475,235 455,300';
const LF='M268,382 C340,352 430,338 520,322 C570,313 610,300 645,272';
const LOBE_FILL={frontal:'#34517d',parietal:'#51427d',temporal:'#7d5134',occipital:'#346e51',cerebellum:'#6e3451',brainstem:'#5e5e34'};
const LOBE_HOT={frontal:'#4f79b8',parietal:'#7a64b8',temporal:'#b87a4f',occipital:'#4fa37a',cerebellum:'#a34f7a',brainstem:'#8c8c4f'};
const hotFill=(k,c)=>hot===k?LOBE_HOT[k]:c;
function outsideView(){
  let s='<defs><clipPath id="cb"><path d="'+OUTLINE+'"/></clipPath></defs>';
  const r=(k,d)=>'<path data-region="'+k+'" d="'+d+'" fill="'+hotFill(k,LOBE_FILL[k])+'" style="cursor:pointer"/>';
  // the stalk and the little brain first, so the big one lies over them
  s+='<path data-region="brainstem" d="M546,430 C542,470 552,520 560,580 L600,580 C608,520 618,470 614,430 Z" fill="'+hotFill('brainstem',LOBE_FILL.brainstem)+'" style="cursor:pointer"/>';
  s+='<g data-region="cerebellum" style="cursor:pointer"><ellipse cx="688" cy="478" rx="92" ry="52" fill="'+hotFill('cerebellum',LOBE_FILL.cerebellum)+'"/>';
  for(let i=-3;i<=3;i++){ const y=478+i*13, hw=Math.sqrt(1-(i*13/52)**2)*92-6; s+='<path d="M'+(688-hw).toFixed(1)+','+y+' Q688,'+(y+9)+' '+(688+hw).toFixed(1)+','+y+'" fill="none" stroke="#121212" stroke-width="1.2" opacity="0.6"/>'; }
  s+='</g>';
  s+='<g clip-path="url(#cb)">';
  s+=r('frontal','M0,0 L515,104 C495,170 475,235 455,300 L455,700 L0,700 Z');
  s+=r('parietal','M515,0 L515,104 C495,170 475,235 455,300 L455,700 L698,700 L712,140 L712,0 Z');
  s+=r('occipital','M712,0 L712,140 L698,700 L980,700 L980,0 Z');
  s+=r('temporal','M268,382 C340,352 430,338 520,322 C570,313 610,300 645,272 L704,330 L698,480 L698,700 L268,700 Z');
  // the sulci
  s+='<path d="'+CS+'" fill="none" stroke="#121212" stroke-width="3"/><path d="'+LF+'" fill="none" stroke="#121212" stroke-width="3"/>';
  s+='<path d="M712,140 L700,440" fill="none" stroke="#121212" stroke-width="2" stroke-dasharray="5 4"/><path d="M645,272 L704,330" fill="none" stroke="#121212" stroke-width="2" stroke-dasharray="5 4"/>';
  s+='</g>';
  s+='<path d="'+OUTLINE+'" fill="none" stroke="#e6e6e6" stroke-width="1.5" opacity="0.5"/>';
  // the strips and patches, over the lobes
  const patch=(k,d,c)=>'<path data-region="'+k+'" d="'+d+'" fill="'+c+'" opacity="'+(hot===k?1:0.85)+'" stroke="'+(hot===k?'#ffffff':'#121212')+'" stroke-width="1.2" style="cursor:pointer"/>';
  s+='<g clip-path="url(#cb)">';
  s+=patch('motor','M489,106 C469,172 449,237 429,302 L455,300 C475,235 495,170 515,104 Z','#ff8c6a');
  s+=patch('sensory','M515,104 C495,170 475,235 455,300 L481,302 C501,237 521,172 541,106 Z','#ffb02e');
  s+='</g>';
  const ell=(k,cx,cy,rx,ry,c)=>'<ellipse data-region="'+k+'" cx="'+cx+'" cy="'+cy+'" rx="'+rx+'" ry="'+ry+'" fill="'+c+'" opacity="'+(hot===k?1:0.85)+'" stroke="'+(hot===k?'#ffffff':'#121212')+'" stroke-width="1.2" style="cursor:pointer"/>';
  s+=ell('broca',355,318,34,20,'#f28cb0')+ell('wernicke',600,340,40,18,'#9be564')+ell('auditory',470,356,42,13,'#6ee7f2')+ell('visual',762,340,34,44,'#c9a6ff');
  // labels
  const lab=(x,y,t,c,a)=>'<text x="'+x+'" y="'+y+'" font-size="11.5" fill="'+(c||'#e6e6e6')+'" text-anchor="'+(a||'middle')+'" pointer-events="none">'+t+'</text>';
  s+=lab(300,215,'frontal')+lab(605,175,'parietal')+lab(430,430,'temporal')+lab(770,240,'occipital')+lab(700,555,'cerebellum','#e6e6e6')+lab(580,602,'brainstem')+lab(355,322,'Broca','#121212')+lab(600,344,'Wernicke','#121212')+lab(470,360,'hearing','#121212')+lab(762,344,'sight','#121212');
  s+=lab(470,92,'motor  |  touch','#9a9a9a')+'<line x1="460" y1="96" x2="470" y2="110" stroke="#9a9a9a" stroke-width="1"/>';
  s+=lab(125,335,'front','#9a9a9a','end')+lab(840,335,'back','#9a9a9a','start');
  return {svg:s, h:650};
}

/* ---- the inside ---- */
const IN_FILL={callosum:'#e6e6e6',thalamus:'#c9a6ff',hypothalamus:'#f28cb0',pituitary:'#ffb02e',cingulate:'#5a4a8a',hippocampus:'#9be564',amygdala:'#ff8c6a',basal:'#6ee7f2',midbrain:'#8a8a4a',pons:'#7a7a3a',medulla:'#6a6a3a',cerebellum:'#7a3a5a',cord:'#5a5a2a'};
function insideView(){
  let s='';
  s+='<path d="'+OUTLINE+'" fill="#2a3444" stroke="#e6e6e6" stroke-opacity="0.5" stroke-width="1.5"/>';
  const on=k=>hot===k;
  const P=(k,d,extra)=>'<path data-region="'+k+'" d="'+d+'" fill="'+(on(k)?'#ffffff':IN_FILL[k])+'" '+(extra||'')+' style="cursor:pointer"/>';
  // the belt of cingulate cortex above the bridge
  s+='<path data-region="cingulate" d="M330,338 C315,232 410,178 500,178 C610,178 690,235 682,312" fill="none" stroke="'+(on('cingulate')?'#ffffff':IN_FILL.cingulate)+'" stroke-width="30" stroke-linecap="round" opacity="0.9" style="cursor:pointer"/>';
  // the corpus callosum
  s+='<path data-region="callosum" d="M352,318 C345,250 420,212 500,212 C590,212 655,250 650,300" fill="none" stroke="'+(on('callosum')?'#ffffff':IN_FILL.callosum)+'" stroke-width="22" stroke-linecap="round" style="cursor:pointer"/>';
  // the basal ganglia, dashed, in front of the thalamus
  s+='<ellipse data-region="basal" cx="436" cy="292" rx="34" ry="46" fill="'+IN_FILL.basal+'" fill-opacity="'+(on('basal')?0.7:0.3)+'" stroke="'+(on('basal')?'#ffffff':IN_FILL.basal)+'" stroke-dasharray="5 4" stroke-width="1.5" style="cursor:pointer"/>';
  // the thalamus
  s+='<ellipse data-region="thalamus" cx="515" cy="300" rx="58" ry="36" fill="'+(on('thalamus')?'#ffffff':IN_FILL.thalamus)+'" style="cursor:pointer"/>';
  // hypothalamus, pituitary
  s+='<ellipse data-region="hypothalamus" cx="500" cy="352" rx="32" ry="15" fill="'+(on('hypothalamus')?'#ffffff':IN_FILL.hypothalamus)+'" style="cursor:pointer"/>';
  s+='<g data-region="pituitary" style="cursor:pointer"><line x1="494" y1="366" x2="492" y2="388" stroke="'+IN_FILL.pituitary+'" stroke-width="3"/><circle cx="492" cy="398" r="10" fill="'+(on('pituitary')?'#ffffff':IN_FILL.pituitary)+'"/></g>';
  // the brainstem in three parts, and the cord
  s+=P('midbrain','M542,336 L592,336 L596,392 L546,392 Z');
  s+=P('pons','M546,392 L596,392 C600,420 600,445 598,460 L552,460 C534,440 534,410 546,392 Z');
  s+=P('medulla','M552,460 L598,460 C600,490 598,520 596,540 L560,540 C556,515 552,490 552,460 Z');
  s+=P('cord','M560,540 L596,540 L600,630 L566,630 Z');
  // hippocampus and amygdala, dashed, deep in the temporal lobe
  s+='<path data-region="hippocampus" d="M582,334 C598,384 570,428 505,430" fill="none" stroke="'+(on('hippocampus')?'#ffffff':IN_FILL.hippocampus)+'" stroke-width="16" stroke-linecap="round" opacity="'+(on('hippocampus')?0.95:0.6)+'" style="cursor:pointer"/>';
  s+='<circle data-region="amygdala" cx="474" cy="430" r="13" fill="'+IN_FILL.amygdala+'" fill-opacity="'+(on('amygdala')?0.9:0.45)+'" stroke="'+(on('amygdala')?'#ffffff':IN_FILL.amygdala)+'" stroke-dasharray="4 3" stroke-width="1.5" style="cursor:pointer"/>';
  // the cerebellum, with its tree
  s+='<g data-region="cerebellum" style="cursor:pointer"><ellipse cx="722" cy="470" rx="70" ry="50" fill="'+(on('cerebellum')?'#ffffff':IN_FILL.cerebellum)+'"/>';
  const tree=(x,y,ang,len,depth)=>{ if(depth===0||len<6) return ''; const x2=x+Math.cos(ang)*len, y2=y+Math.sin(ang)*len; let t='<line x1="'+x.toFixed(1)+'" y1="'+y.toFixed(1)+'" x2="'+x2.toFixed(1)+'" y2="'+y2.toFixed(1)+'" stroke="#e6e6e6" stroke-width="'+(depth*0.5).toFixed(1)+'" opacity="0.8"/>'; t+=tree(x2,y2,ang-0.6,len*0.62,depth-1)+tree(x2,y2,ang+0.6,len*0.62,depth-1); return t; };
  s+=tree(668,470,0,30,5)+tree(668,470,-1.1,22,4)+tree(668,470,1.1,22,4)+'</g>';
  // labels with leaders
  const lab=(x,y,t,a)=>'<text x="'+x+'" y="'+y+'" font-size="11.5" fill="#e6e6e6" text-anchor="'+(a||'start')+'" pointer-events="none">'+t+'</text>';
  const lead=(x1,y1,x2,y2)=>'<line x1="'+x1+'" y1="'+y1+'" x2="'+x2+'" y2="'+y2+'" stroke="#9a9a9a" stroke-width="1" pointer-events="none"/>';
  s+=lab(500,170,'cingulate cortex','middle')+lab(500,222,'corpus callosum','middle');
  s+=lab(515,304,'thalamus','middle')+lab(436,296,'basal','middle')+lab(436,310,'ganglia','middle');
  s+=lead(468,352,400,352)+lab(396,356,'hypothalamus','end');
  s+=lead(481,398,402,398)+lab(398,402,'pituitary','end');
  s+=lead(468,440,420,480)+lab(416,484,'amygdala','end');
  s+=lead(545,434,510,500)+lab(506,504,'hippocampus','end');
  s+=lab(606,368,'midbrain')+lab(606,432,'pons')+lab(606,505,'medulla')+lab(606,600,'spinal cord');
  s+=lab(740,545,'cerebellum','middle');
  s+=lab(125,335,'front','end')+lab(840,335,'back');
  return {svg:s, h:650};
}

/* ---- a lifetime ---- */
const G={x:90,y:40,w:820,h:480,amax:90,mmax:1600};
const GX=a=>G.x+Math.sqrt(a/G.amax)*G.w;
const GY=m=>G.y+G.h-m/G.mmax*G.h;
function growthView(){
  let s='';
  for(const m of [0,400,800,1200,1600]){ const y=GY(m); s+='<line x1="'+G.x+'" y1="'+y.toFixed(1)+'" x2="'+(G.x+G.w)+'" y2="'+y.toFixed(1)+'" stroke="#2b2b2b"/><text x="'+(G.x-8)+'" y="'+(y+4).toFixed(1)+'" text-anchor="end" font-size="10.5" fill="#9a9a9a">'+fmt(m)+'</text>'; }
  for(const a of [0,1,2,3,5,10,20,30,50,70,90]){ const x=GX(a); s+='<line x1="'+x.toFixed(1)+'" y1="'+(G.y+G.h)+'" x2="'+x.toFixed(1)+'" y2="'+(G.y+G.h+6)+'" stroke="#8a94a6"/><text x="'+x.toFixed(1)+'" y="'+(G.y+G.h+22)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+(a===0?'birth':a)+'</text>'; }
  s+='<line x1="'+G.x+'" y1="'+(G.y+G.h)+'" x2="'+(G.x+G.w)+'" y2="'+(G.y+G.h)+'" stroke="#8a94a6"/>';
  s+='<text x="'+(G.x+G.w/2)+'" y="'+(G.y+G.h+44)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">age, years, on a square-root scale</text>';
  s+='<text transform="translate(18,'+(G.y+G.h/2)+') rotate(-90)" text-anchor="middle" font-size="11" fill="#9a9a9a">brain mass, grams</text>';
  for(const [key,c,lbl] of [['m','#58a6ff','men'],['f','#f28cb0','women']]){ let d=''; GROWTH.forEach((g,i)=>{ d+=(i?'L':'M')+GX(g.age).toFixed(1)+','+GY(g[key]).toFixed(1); }); s+='<path d="'+d+'" fill="none" stroke="'+c+'" stroke-width="2.2"/>';
    for(const g of GROWTH) s+='<circle cx="'+GX(g.age).toFixed(1)+'" cy="'+GY(g[key]).toFixed(1)+'" r="4" fill="'+c+'" stroke="#121212" stroke-width="1.2"/>';
    const last=GROWTH[GROWTH.length-1]; s+='<text x="'+(GX(last.age)+10).toFixed(1)+'" y="'+(GY(last[key])+4).toFixed(1)+'" font-size="11.5" fill="'+c+'">'+lbl+'</text>'; }
  // the marker
  const mx=GX(age);
  s+='<g id="marker" style="cursor:ew-resize"><line x1="'+mx.toFixed(1)+'" y1="'+G.y+'" x2="'+mx.toFixed(1)+'" y2="'+(G.y+G.h)+'" stroke="#ffb02e" stroke-width="1.5"/>';
  s+='<circle cx="'+mx.toFixed(1)+'" cy="'+GY(interp(age,'m')).toFixed(1)+'" r="5.5" fill="#ffb02e" stroke="#121212" stroke-width="1.5"/><circle cx="'+mx.toFixed(1)+'" cy="'+GY(interp(age,'f')).toFixed(1)+'" r="5.5" fill="#ffb02e" stroke="#121212" stroke-width="1.5"/>';
  s+='<text x="'+mx.toFixed(1)+'" y="'+(G.y-10)+'" text-anchor="middle" font-size="11.5" font-weight="700" fill="#ffb02e">'+(age===0?'birth':age+(age===1?' year':' years'))+'</text></g>';
  s+='<text x="'+(G.x+G.w)+'" y="'+(G.y+14)+'" text-anchor="end" font-size="11" fill="#9a9a9a">the same 86 billion neurons from the first point to the last</text>';
  return {svg:s, h:G.y+G.h+60};
}

/* ---- render and wiring ---- */
function render(){ const q=view==='outside'?outsideView():view==='inside'?insideView():growthView(); el.innerHTML='<svg viewBox="0 0 '+W+' '+q.h+'" xmlns="http://www.w3.org/2000/svg" id="bsvg"><rect width="'+W+'" height="'+q.h+'" fill="#121212"/>'+q.svg+'</svg>'; document.getElementById('ageCtl').hidden=view!=='growth'; document.getElementById('ageOut').textContent=age===0?'birth':age+(age===1?' year':' years'); }
function home(){ if(view==='outside') showWhole(); else if(view==='inside') showInside(); else showAge(age); }
function setView(v){ view=v; hot=null; for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on',b.dataset.v===v); render(); home(); }
document.getElementById('views').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setView(b.dataset.v); });
let dragging=false;
const svgPt=e=>{ const svg=document.getElementById('bsvg'), b=svg.getBoundingClientRect(); return [(e.clientX-b.left)/b.width*W,(e.clientY-b.top)/b.height*svg.viewBox.baseVal.height]; };
function setAge(x){ const t=Math.max(0,Math.min(1,(x-G.x)/G.w)); age=Math.round(t*t*G.amax); render(); showAge(age); }
el.addEventListener('pointerdown',e=>{ if(view!=='growth') return; const [x,y]=svgPt(e); if(y>=G.y-20&&y<=G.y+G.h+30&&x>=G.x-6&&x<=G.x+G.w+6){ dragging=true; setAge(x); e.preventDefault(); } });
el.addEventListener('pointermove',e=>{ if(!dragging) return; const [x]=svgPt(e); setAge(x); });
window.addEventListener('pointerup',()=>{ dragging=false; });
el.addEventListener('pointerover',e=>{ if(dragging||view==='growth') return; const p=e.target.closest('[data-region]'); if(!p){ return; } const k=p.getAttribute('data-region'); if(k===hot) return; hot=k; render(); showRegion(view==='outside'?OUTSIDE:INSIDE,k); });
el.addEventListener('pointerleave',()=>{ if(hot){ hot=null; render(); home(); } });

render(); showWhole();
window.__brain=(q)=>{ const o={view,hot,age,card:document.getElementById('numTxt').innerText,name:document.getElementById('nameTxt').innerText,body:document.getElementById('bodyTxt').innerText,regions:[...new Set([...document.querySelectorAll('#bsvg [data-region]')].map(x=>x.getAttribute('data-region')))],
  marker:(()=>{ const c=document.querySelector('#marker line'); return c?+c.getAttribute('x1'):null; })()};
  if(q&&q.age!=null){ o.m=interp(q.age,'m'); o.f=interp(q.age,'f'); o.gx=GX(q.age); }
  if(q&&q.probe){ const svg=document.getElementById('bsvg'), b=svg.getBoundingClientRect(); const [px,py]=q.probe; const e=document.elementFromPoint(b.left+px/W*b.width, b.top+py/svg.viewBox.baseVal.height*b.height); const r=e&&e.closest?e.closest('[data-region]'):null; o.at=r?r.getAttribute('data-region'):null; }
  return o; };
</script>
</body>
</html>
"""

html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__WHOLE__", _js(WHOLE)).replace("__OUTSIDE__", _js(outside)).replace("__INSIDE__", _js(inside)).replace("__GROWTH__", _js(growth)).replace("__GNOTES__", _js(gnotes))
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(OUTSIDE)} outside, {len(INSIDE)} inside, {len(GROWTH)} ages")
