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
SHAPES = (Path(__file__).parent / "brain_shapes.json").read_text(encoding="utf-8").strip()

NOTE1 = ("A kilogram and a half of tissue that is two percent of the body "
         "and takes a fifth of its energy. Seen from the side it is four "
         "lobes, a little brain tucked under the back, and the stalk that "
         "joins it to the spinal cord; each answers under the pointer, and "
         "so do the strips and patches laid over them where one job is done "
         "in one place: moving, feeling, speech, hearing, sight.")

NOTE2 = ("Cut down the middle, the brain shows what the lobes hide: the "
         "bridge of two hundred million fibers between the halves, the "
         "thalamus at the center through which nearly everything passes, "
         "the small regulators of temperature, hunger and hormones beneath "
         "it, and the brainstem that keeps breathing going. The third view "
         "is the same organ over a lifetime: a quarter of its adult mass at "
         "birth, nine tenths by three, and a slow loss after fifty.")

METHOD = ("The shapes are traced from real brains, not drawn by hand. The "
          "outside is the left hemisphere of fsaverage, FreeSurfer's average "
          "of forty adult brains, seen from the left; its lobes are the "
          "Desikan-Killiany regions grouped the usual way, its folds are the "
          "places where the surface dips deeper than its surroundings, and "
          "the motor and touch strips are the precentral and postcentral "
          "gyri. Broca's area is the pars opercularis and triangularis, and "
          "Wernicke's area the back of the superior temporal gyrus, as on the "
          "left in most people. The cerebellum and brainstem are not on that "
          "surface and come from the MNI152 template's labels, fitted to the "
          "same frame. The inside is a cut through the MNI152 template 4 mm "
          "right of the midline, with its outline, folds and white matter "
          "traced from the image and the deep parts from its labels; the "
          "brainstem is divided where its front edge bulges into the pons and "
          "falls back to the medulla. The pituitary is outside the template "
          "and is placed below the optic chiasm. Cell counts are Azevedo and "
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
const SHAPES=__SHAPES__, WHOLE=__WHOLE__, OUTSIDE=__OUTSIDE__, INSIDE=__INSIDE__, GROWTH=__GROWTH__, GNOTES=__GNOTES__;
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
  ['fibers','about '+fmt(WHOLE.fibres_km_m)+' km of insulated fiber in a man of twenty, '+fmt(WHOLE.fibres_km_f)+' in a woman'],
  ['blood','about '+fmt(WHOLE.blood_ml_min)+' mL a minute, '+WHOLE.blood_pct+'% of what the heart pumps']],
  'The cortex is a sheet 2 to 4 mm thick and about a quarter of a square meter in all, two thirds of it folded out of sight. Each lobe, strip and patch answers under the pointer.','Azevedo et al. 2009; Marner et al. 2003; Raichle & Gusnard 2002; Toro et al. 2008; Wikipedia, Human brain'); }
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
// every shape is traced from a real brain by tools/brain_geometry.py
const SO=SHAPES.outside, SI=SHAPES.inside, PO=SHAPES.outside_probes, PI=SHAPES.inside_probes, MK=SHAPES.marks;
const LOBE_FILL={frontal:'#34517d',parietal:'#51427d',temporal:'#7d5134',occipital:'#346e51',cerebellum:'#6e3451',brainstem:'#5e5e34'};
const LOBE_HOT={frontal:'#4f79b8',parietal:'#7a64b8',temporal:'#b87a4f',occipital:'#4fa37a',cerebellum:'#a34f7a',brainstem:'#8c8c4f'};
const hotFill=(k,c)=>hot===k?LOBE_HOT[k]:c;
const lab=(x,y,t,c,a)=>'<text x="'+(+x).toFixed(1)+'" y="'+(+y).toFixed(1)+'" font-size="11.5" fill="'+(c||'#e6e6e6')+'" text-anchor="'+(a||'middle')+'" pointer-events="none">'+t+'</text>';
const lead=(x1,y1,x2,y2)=>'<line x1="'+(+x1).toFixed(1)+'" y1="'+(+y1).toFixed(1)+'" x2="'+(+x2).toFixed(1)+'" y2="'+(+y2).toFixed(1)+'" stroke="#9a9a9a" stroke-width="1" pointer-events="none"/>';
function outsideView(){
  let s='';
  const r=(k,d)=>'<path data-region="'+k+'" d="'+d+'" fill="'+hotFill(k,LOBE_FILL[k])+'" fill-rule="evenodd" style="cursor:pointer"/>';
  // the stalk and the little brain first, so the big one lies over them
  s+=r('brainstem',SO.brainstem);
  s+='<g data-region="cerebellum" style="cursor:pointer">'+r('cerebellum',SO.cerebellum).replace(' data-region="cerebellum"','')+'<path d="'+SO.folia+'" fill="none" stroke="#121212" stroke-width="1.1" opacity="0.55"/></g>';
  for(const k of ['frontal','parietal','temporal','occipital']) s+=r(k,SO[k]);
  // the strips and patches that sit on the surface
  const patch=(k,c)=>'<path data-region="'+k+'" d="'+SO[k]+'" fill="'+c+'" fill-rule="evenodd" opacity="'+(hot===k?1:0.82)+'" stroke="'+(hot===k?'#ffffff':'none')+'" stroke-width="1.4" style="cursor:pointer"/>';
  s+=patch('motor','#ff8c6a')+patch('sensory','#ffb02e')+patch('broca','#f28cb0')+patch('wernicke','#9be564');
  // the folds: wherever the surface dips into a sulcus
  s+='<path d="'+SO.sulci+'" fill="#0a0e15" fill-rule="evenodd" opacity="0.5" pointer-events="none"/>';
  // two patches mostly out of sight: hearing inside the lateral fissure, sight on the inner face
  const hidden=(k,c)=>'<path data-region="'+k+'" d="'+SO[k]+'" fill="'+c+'" fill-opacity="'+(hot===k?0.55:0.2)+'" stroke="'+(hot===k?'#ffffff':c)+'" stroke-width="1.5" stroke-dasharray="5 3" style="cursor:pointer"/>';
  s+=hidden('auditory','#6ee7f2')+hidden('visual','#c9a6ff');
  s+='<path d="'+SO.outline+'" fill="none" stroke="#e6e6e6" stroke-width="1.3" opacity="0.5" pointer-events="none"/>';
  // labels
  s+=lab(PO.frontal[0],PO.frontal[1]+4,'frontal')+lab(PO.parietal[0],PO.parietal[1]+4,'parietal')+lab(PO.temporal[0],PO.temporal[1]+4,'temporal')+lab(PO.occipital[0],PO.occipital[1]+4,'occipital');
  s+=lab(PO.cerebellum[0],PO.cerebellum[1]+4,'cerebellum')+lead(MK.stem_end[0],MK.stem_end[1]-40,MK.stem_end[0]+38,MK.stem_end[1]-40)+lab(MK.stem_end[0]+42,MK.stem_end[1]-36,'brainstem','#e6e6e6','start');
  s+=lab(PO.broca[0],PO.broca[1]+4,'Broca','#121212')+lab(PO.wernicke[0],PO.wernicke[1]+4,'Wernicke','#121212');
  s+=lead(PO.auditory[0]-6,PO.auditory[1]+6,PO.auditory[0]-34,PO.auditory[1]+36)+lab(PO.auditory[0]-38,PO.auditory[1]+48,'hearing','#6ee7f2')+lab(PO.visual[0],PO.visual[1]-12,'sight','#c9a6ff');
  const t=MK.strip_top; s+=lab(t[0]-8,t[1]-18,'motor  |  touch','#9a9a9a')+lead(t[0]-8,t[1]-14,t[0]-4,t[1]+2);
  s+=lab(112,335,'front','#9a9a9a','end')+lab(858,335,'back','#9a9a9a','start');
  return {svg:s, h:700};
}

/* ---- the inside ---- */
const IN_FILL={callosum:'#e6e6e6',thalamus:'#c9a6ff',hypothalamus:'#f28cb0',pituitary:'#ffb02e',cingulate:'#5a4a8a',hippocampus:'#9be564',amygdala:'#ff8c6a',basal:'#6ee7f2',midbrain:'#8a8a4a',pons:'#7a7a3a',medulla:'#6a6a3a',cerebellum:'#7a3a5a',cord:'#5a5a2a'};
function insideView(){
  let s='';
  const on=k=>hot===k;
  s+='<path d="'+SI.outline+'" fill="#2a3444" fill-rule="evenodd" stroke="#e6e6e6" stroke-opacity="0.5" stroke-width="1.3"/>';
  s+='<path d="'+SI.sulci+'" fill="#0d1118" fill-rule="evenodd" opacity="0.85" pointer-events="none"/>';
  const P=(k,extra)=>'<path data-region="'+k+'" d="'+SI[k]+'" fill="'+(on(k)?'#ffffff':IN_FILL[k])+'" fill-rule="evenodd" '+(extra||'')+' style="cursor:pointer"/>';
  // off the midline, projected onto the cut: drawn dashed and see-through
  const D=(k,op)=>'<path data-region="'+k+'" d="'+SI[k]+'" fill="'+IN_FILL[k]+'" fill-opacity="'+(on(k)?0.75:op)+'" stroke="'+(on(k)?'#ffffff':IN_FILL[k])+'" stroke-width="1.5" stroke-dasharray="5 4" style="cursor:pointer"/>';
  s+=P('cingulate','opacity="0.92"')+P('callosum');
  s+=D('basal',0.16);
  s+=P('thalamus')+P('hypothalamus');
  s+='<g data-region="pituitary" style="cursor:pointer"><path d="'+SI.stalk+'" stroke="'+IN_FILL.pituitary+'" stroke-width="3"/><path d="'+SI.pituitary+'" fill="'+(on('pituitary')?'#ffffff':IN_FILL.pituitary)+'"/></g>';
  s+=P('midbrain')+P('pons')+P('medulla')+P('cord');
  s+='<g data-region="cerebellum" style="cursor:pointer"><path d="'+SI.cerebellum+'" fill="'+(on('cerebellum')?'#b0668a':IN_FILL.cerebellum)+'" fill-rule="evenodd"/><path d="'+SI.arbor+'" fill="#e6e6e6" fill-rule="evenodd" opacity="0.85"/></g>';
  s+=D('hippocampus',0.3)+D('amygdala',0.4);
  // labels
  const L=(k,t,dx,dy,a)=>lab(PI[k][0]+(dx||0),PI[k][1]+(dy||0)+4,t,'#e6e6e6',a);
  s+=L('cingulate','cingulate cortex')+lab(MK.callosum_label[0],MK.callosum_label[1]+4,'corpus callosum','#121212');
  s+=L('thalamus','thalamus')+L('basal','basal ganglia')+L('pons','pons')+lab(690,630,'cerebellum');
  const side=(k,t,y)=>lead(PI[k][0],PI[k][1],344,y)+lab(340,y+4,t,'#e6e6e6','end');
  s+=side('hypothalamus','hypothalamus',405)+side('amygdala','amygdala',445)+side('pituitary','pituitary',503)+side('hippocampus','hippocampus',545);
  const right=(k,t,x,y)=>lead(PI[k][0],PI[k][1],x-4,y-4)+lab(x,y,t,'#e6e6e6','start');
  s+=right('midbrain','midbrain',600,352);
  s+=lead(PI.medulla[0],PI.medulla[1],468,600)+lab(464,604,'medulla','#e6e6e6','end');
  s+=lead(PI.cord[0],PI.cord[1],600,650)+lab(604,654,'spinal cord','#e6e6e6','start');
  s+=lab(112,335,'front','#e6e6e6','end')+lab(858,335,'back','#e6e6e6','start');
  return {svg:s, h:700};
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
        .replace("__SHAPES__", SHAPES).replace("__WHOLE__", _js(WHOLE)).replace("__OUTSIDE__", _js(outside)).replace("__INSIDE__", _js(inside)).replace("__GROWTH__", _js(growth)).replace("__GNOTES__", _js(gnotes))
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(OUTSIDE)} outside, {len(INSIDE)} inside, {len(GROWTH)} ages")
