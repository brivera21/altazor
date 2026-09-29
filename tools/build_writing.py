#!/usr/bin/env python3
"""Generate writing.html, Writing: the scripts, five letters, and the signs.

Three views. The scripts: thirty-odd writing systems on a line of time,
each joined to the one it came from, so that the four or five independent
inventions and the one great family that grew from the Egyptian signs can
be seen at once; each answers under the pointer. The letters: A, B, M, N
and O followed from the Egyptian picture through the Canaanite, Phoenician
and Greek letters to the Latin ones. The signs: how many a writer of each
kind of script has to learn, on a log scale.

Data: tools/writing_data.py.

Usage: python3 build_writing.py
"""

import json
from pathlib import Path

import apa
from writing_data import TYPES, SCRIPTS, LETTERS, COUNTS, REFS

OUT = Path(__file__).parent.parent / "writing.html"

NOTE1 = ("Writing was invented from nothing perhaps four times: in Sumer "
         "and Egypt around 3200 BC, in China by 1250 BC, in Mexico and "
         "Guatemala by 300 BC. Almost everything else descends from one "
         "event, when Canaanite workers in Egypt around 1800 BC took a few "
         "dozen hieroglyphs and used each for the first sound of its name.")

NOTE1B = ("The first view is that family tree on a line of time; each script "
          "answers under the pointer.")

MOTION = ("A script clicked stays lit with its whole line, back to the "
          "sign it came from and down to everything made from it, until a "
          "second click or Escape lets it go; a kind in the key lights every "
          "script of that kind, under the pointer or clicked. The year runs "
          "the tree through time, each script appearing at its first "
          "inscription, and Play runs it from 3400 BC to now. In Five letters "
          "the column on the right draws each letter between its stages: "
          "every stroke of every stage is resampled to the same number of "
          "points, so a stroke can be carried point by point into the next "
          "stage's, and a stroke that has no partner fades in or out.")

NOTE2 = ("The second view follows five letters through it: the ox, the "
         "house, the water, the snake and the eye that became A, B, M, N "
         "and O, the pictures turning on their sides, losing their faces and "
         "straightening into strokes. The third view is what each kind of "
         "writing asks of a reader: a few dozen signs for an alphabet, a "
         "few hundred for a syllabary, and thousands for a script that "
         "writes words.")

METHOD = ("Dates are the earliest surviving inscriptions, rounded, and can "
          "only move earlier; the descent is the usual account in Daniels "
          "and Bright, with the two disputed links, Brahmi from Aramaic and "
          "the Canaanite letters from Egyptian, drawn like the rest and "
          "flagged in their cards. The letter shapes are drawn here from the "
          "published sign tables, one typical form for each stage, where "
          "the originals vary from inscription to inscription; the "
          "Egyptian signs are the ones the Proto-Sinaitic letters are "
          "usually matched with. Sign counts depend on how one counts: a "
          "script's basic inventory is given, without ligatures, positional "
          "forms or diacritics.")


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


scripts = [{"k": k, "n": n, "y": y, "p": p, "t": t, "w": w, "b": b, "alive": a} for k, n, y, p, t, w, b, a in SCRIPTS]
letters = [{"k": k, "L": L, "thing": th, "stages": [{"n": n, "y": y, "name": nm, "b": b, "d": d} for n, y, nm, b, d in st]} for k, L, th, st in LETTERS]
counts = [{"k": k, "n": n, "signs": s, "t": t, "b": b, "s": src} for k, n, s, t, b, src in COUNTS]
types = {k: {"n": n, "c": c, "b": b} for k, (n, c, b) in TYPES.items()}

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Writing &middot; Altazor</title>
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
.legend { display:flex; gap:14px; flex-wrap:wrap; margin:0 0 12px; font-size:12.5px; color:var(--muted); min-height:24px; }
.legend span { cursor:pointer; border-radius:999px; padding:0 6px; margin:0 -6px; }
.legend span.on { color:var(--text); background:#1f2630; }
.legend span::before { content:""; display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:6px; background:var(--c); vertical-align:-1px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; }
#diagram svg { width:100%; height:auto; display:block; user-select:none; }
#diagram { outline:none; border-radius:10px; }
.controls { display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin:0 0 10px; }
.controls label { font-size:13px; color:var(--muted); }
.controls input[type=range] { width:260px; max-width:48vw; accent-color:var(--accent); }
.controls output { font-size:13px; color:var(--text); font-variant-numeric:tabular-nums; min-width:9em; }
.controls button { background:var(--panel); color:var(--text); border:1px solid var(--line); border-radius:8px;
  padding:4px 12px; font-size:13px; cursor:pointer; font-family:inherit; }
.controls button:hover { border-color:var(--accent); }
.controls button.on { border-color:var(--accent); color:var(--accent); }
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
details.sources { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
details.sources summary { cursor:pointer; color:var(--accent); }
details.sources p { margin:9px 0 0; }
.refs { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.refs p { margin:0 0 8px; overflow-wrap:anywhere; }
.refs a { color:var(--accent); }
__APACSS__
h2.refh { font-size:15px; margin:26px 0 8px; }
@media (max-width:900px){ .stage{flex-direction:column;} #diagram{flex:none; width:100%;} .side{position:static; width:100%; flex:none; order:-1;} }
@media (max-width:600px){ #diagram{overflow-x:auto;} #diagram svg{min-width:760px;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library &middot; Abstractions</a><a href="numbers.html">Numbers</a><a href="languages.html">Languages</a><a href="chinese.html">The Most Used Chinese</a></nav>
</header>
<h1>Writing</h1>
<div class="bar" id="views"><button data-v="tree" class="on">The scripts</button><button data-v="letters">Five letters</button><button data-v="counts">The signs</button></div>
<div class="legend" id="legend"></div>
<div class="controls" id="treeCtl"><button type="button" id="yPlay">Play</button><label for="year">the year</label><input type="range" id="year" min="-3400" max="2030" step="10" value="2030"><output id="yearOut">today</output></div>
<div class="controls" id="letterCtl" hidden><button type="button" id="mPlay">Play</button><label for="morph">the stage</label><input type="range" id="morph" min="0" max="400" step="1" value="0"><output id="morphOut"></output></div>
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
<details class="sources"><summary>Sources</summary>
<p>__NOTE1B__</p>
<p>__NOTE2__</p>
<p>__MOTION__</p>
<p>__METHOD__</p>
<div class="refs">__REFS__</div>
</details>
<svg width="0" height="0" style="position:absolute;visibility:hidden" aria-hidden="true"><path id="measure" d="M0,0"/></svg>
</div>
<script>
const TYPES=__TYPES__, SCRIPTS=__SCRIPTS__, LETTERS=__LETTERS__, COUNTS=__COUNTS__;
const W=980;
const el=document.getElementById('diagram');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const fmt=n=>n.toLocaleString('en-US');
const yr=y=>y<0?(-y)+' BC':y+' AD';
let view='tree', hot=null, pinned=null, kindHover=null, kindPin=null, year=2030, morph=0;
const REDUCED=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const ease=t=>t<0.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
const kindOn=()=>kindHover||kindPin;

/* ---- the card ---- */
function card(kind,name,rows,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').innerHTML=name;
  document.getElementById('numTxt').innerHTML=rows.filter(r=>r[1]).map(([k,v])=>'<b>'+esc(k)+'</b> '+v).join('<br>');
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').textContent=src;
}
const byK=Object.fromEntries(SCRIPTS.map(s=>[s.k,s]));
const kids=k=>SCRIPTS.filter(s=>s.p===k);
function descendants(k){ let n=0; for(const c of kids(k)) n+=1+descendants(c.k); return n; }
function lineage(k){ const out=[]; let s=byK[k]; while(s.p){ s=byK[s.p]; out.push(s.n); } return out; }
function showScript(k){ const s=byK[k]; const d=descendants(k), lin=lineage(k);
  card(TYPES[s.t].n+(s.p?'':', invented from nothing'), esc(s.n), [['first seen','about '+yr(s.y)],['where',s.w],['comes from',lin.length?lin.join(', which came from ')+(lin.length>1?'':'')+'':'no earlier script'],['descendants here',d?d+' script'+(d>1?'s':''):'none'],['today',s.alive?'still in use':'no longer used']], s.b, 'Daniels & Bright 1996; Wikipedia, '+s.n); }
function showTree(){ const roots=SCRIPTS.filter(s=>!s.p); card('The scripts','Where writing came from',[['scripts drawn',SCRIPTS.length],['invented from nothing',roots.length+' of them: '+roots.map(r=>r.n).join(', ')],['from the Egyptian signs',descendants('hieroglyphs')+' of the rest'],['still in use',SCRIPTS.filter(s=>s.alive).length]],'Each dot is a script at the date of its first surviving inscription, joined by a line to the script it was made from; a filled dot is still written. The color is the kind of system it is.','Daniels & Bright 1996; Wikipedia, History of writing'); }
function showStage(lk,i){ const L=LETTERS.find(x=>x.k===lk), st=L.stages[i]; card(st.n+', '+(i===0?'by ':'')+yr(st.y), esc(st.name), [['the letter',L.L],['stage',(i+1)+' of 5']], st.b+(i===1?' Each Canaanite letter was named for the thing it drew and stood for the first sound of that name.':''), 'Wikipedia, Proto-Sinaitic script; Wikipedia, '+(i<2?'Egyptian hieroglyphs':i===2?'Phoenician alphabet':i===3?'Greek alphabet':'Latin alphabet')); }
function showLetter(lk){ const L=LETTERS.find(x=>x.k===lk); card('A letter', L.L+', '+L.thing, [['began as',L.stages[0].name],['named',L.stages[1].name.split(',')[0]+' in Canaanite, '+L.stages[2].name+' in Phoenician, '+L.stages[3].name+' in Greek'],['sound',L.k==='a'||L.k==='o'?'a consonant Greek lacked, so the Greeks made it a vowel':'the same sound all the way']], 'The picture became a letter by standing for the first sound of its name, and then kept being copied, turned, and simplified for three thousand years.', 'Wikipedia, Proto-Sinaitic script'); }
function showLetters(){ card('Five letters','From picture to alphabet',[['the pictures','an ox, a house, water, a snake, an eye'],['the letters','A, B, M, N, O'],['the time','about 3,800 years, from the turquoise mines of Sinai to this page']],'Each row follows one sign left to right through five stages; each cell answers under the pointer.','Wikipedia, Proto-Sinaitic script'); }
function showCount(k){ const c=COUNTS.find(x=>x.k===k); card(TYPES[c.t].n, esc(c.n), [['signs','about '+fmt(c.signs)],['the kind',TYPES[c.t].b]], c.b, c.s); }
function showCounts(){ card('The signs','How many a reader has to learn',[['alphabets and abjads','two or three dozen'],['syllabaries','fifty to several hundred'],['scripts that write words','hundreds to thousands, and tens of thousands exist']],'Each bar is one script\\u2019s basic inventory on a log scale, colored by its kind.','Wikipedia, Writing system'); }

/* ---- the scripts on a line of time ---- */
const T={x:40,y:36,w:900,y0:-3400,y1:2030,lane:34};
const TX=y=>T.x+(y-T.y0)/(T.y1-T.y0)*T.w;
const PXY=T.w/(T.y1-T.y0);
const need=s=>(s.n.length*7+30)/PXY; // years a label takes up in its lane
function layout(){ const order=[...SCRIPTS].sort((a,b)=>a.y-b.y||a.n.localeCompare(b.n)); const lanes=[]; const pos={};
  const free=(i,s)=>lanes[i]===undefined||lanes[i]<=s.y;
  for(const s of order){ let lane=-1; const pl=s.p&&pos[s.p]?pos[s.p].lane:null;
    if(pl!=null){ for(let d=0; d<lanes.length+1&&lane<0; d++){ for(const i of [pl+d,pl-d]){ if(i>=0&&i<lanes.length&&free(i,s)){ lane=i; break; } } } }
    else { for(let i=0;i<lanes.length;i++){ if(free(i,s)){ lane=i; break; } } }
    if(lane<0){ lane=lanes.length; }
    lanes[lane]=s.y+need(s); pos[s.k]={lane,x:TX(s.y)}; }
  return {pos, n:lanes.length}; }
function ancestors(k){ const out=new Set(); let s=byK[k]; while(s.p){ out.add(s.p); s=byK[s.p]; } return out; }
function family(k){ const out=new Set([k]); const walk=x=>{ for(const c of kids(x)){ out.add(c.k); walk(c.k); } }; walk(k); for(const a of ancestors(k)) out.add(a); return out; }
function treeView(){ const {pos,n}=layout(); const LY=l=>T.y+20+l*T.lane; let s='';
  const h=T.y+20+n*T.lane+40; const fam=hot?family(hot):null, kd=kindOn(), seen=c=>c.y<=year;
  for(const y of [-3000,-2000,-1000,0,1000,2000]){ const x=TX(y); s+='<line x1="'+x.toFixed(1)+'" y1="'+T.y+'" x2="'+x.toFixed(1)+'" y2="'+(h-34)+'" stroke="#2b2b2b"/><text x="'+x.toFixed(1)+'" y="'+(h-18)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+(y===0?'AD 1':yr(y))+'</text>'; }
  // the lines of descent
  const edges=[];
  for(const c of SCRIPTS){ if(!c.p||!seen(c)) continue; const a=pos[c.p], b=pos[c.k]; const x1=a.x, y1=LY(a.lane), x2=b.x, y2=LY(b.lane); const on=fam&&fam.has(c.k)&&fam.has(c.p), disp=c.k==='brahmi'||c.k==='protosinaitic';
    const faded=(fam&&!on)||(kd&&!(c.t===kd&&byK[c.p].t===kd));
    // a disputed descent is dotted and lighter, so it reads apart from the solid lines
    edges.push([on?1:0,'<path d="M'+x1.toFixed(1)+','+y1+' C'+((x1+x2)/2).toFixed(1)+','+y1+' '+((x1+x2)/2).toFixed(1)+','+y2+' '+x2.toFixed(1)+','+y2+'" fill="none" stroke="'+(on?'#e6e6e6':disp?'#9aa4b4':'#3d444d')+'" stroke-width="'+(on?1.8:disp?1.6:1.2)+'" opacity="'+(faded?0.3:1)+'"'+(disp?' stroke-dasharray="2 5" stroke-linecap="round" data-disputed="1"':'')+'/>']); }
  edges.sort((a,b)=>a[0]-b[0]); s+=edges.map(e=>e[1]).join('');
  for(const c of SCRIPTS){ if(!seen(c)) continue; const p=pos[c.k], x=p.x, y=LY(p.lane), col=TYPES[c.t].c, on=hot===c.k||pinned===c.k, dim=(fam&&!fam.has(c.k))||(kd&&c.t!==kd), kindLit=kd&&c.t===kd;
    s+='<g data-script="'+c.k+'" style="cursor:pointer" opacity="'+(dim?(kd&&!fam?0.22:0.4):1)+'">'+(kindLit?'<circle cx="'+x.toFixed(1)+'" cy="'+y+'" r="10" fill="none" stroke="'+col+'" stroke-opacity="0.45" stroke-width="1.5"/>':'')+'<circle cx="'+x.toFixed(1)+'" cy="'+y+'" r="'+(on?7:5.5)+'" fill="'+(c.alive?col:'#121212')+'" stroke="'+(on?'#ffffff':col)+'" stroke-width="2"/>';
    s+='<text x="'+(x+10).toFixed(1)+'" y="'+(y+4)+'" font-size="11.5" fill="'+(on?'#ffffff':'#c8c8c8')+'"'+(c.p?'':' font-weight="700"')+' stroke="#121212" stroke-width="4" paint-order="stroke" stroke-linejoin="round">'+esc(c.n)+'</text></g>'; }
  s+='<text x="'+T.x+'" y="'+(T.y-14)+'" font-size="11" fill="#9a9a9a">a filled dot is still written; a name in bold was invented from nothing; a dotted line is a disputed descent</text>';
  if(year<T.y1-20){ const x=TX(year); s+='<line id="yearLine" x1="'+x.toFixed(1)+'" y1="'+T.y+'" x2="'+x.toFixed(1)+'" y2="'+(h-34)+'" stroke="#58a6ff" stroke-width="1.2" opacity="0.8"/><text x="'+(x+5).toFixed(1)+'" y="'+(h-38)+'" font-size="10.5" fill="#58a6ff">'+yr(year)+'</text>'; }
  return {svg:s, h}; }

/* ---- five letters ---- */
function lettersView(){ const x0=100, y0=70, cw=140, ch=100, box=64; let s='';
  const bi=Math.round(morph); s+='<rect id="mband" x="'+(x0+bi*cw+6)+'" y="'+(y0-6)+'" width="'+(cw-12)+'" height="'+(LETTERS.length*ch+2)+'" rx="10" fill="#161d27"/>';
  const mx=x0+5*cw+(W-x0-5*cw)/2; s+='<text x="'+mx+'" y="'+(y0-36)+'" text-anchor="middle" font-size="12" font-weight="700" fill="#58a6ff">in between</text><text x="'+mx+'" y="'+(y0-20)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">stage '+(morph/1+1).toFixed(1)+'</text>';
  const heads=['Egyptian sign','Proto-Sinaitic','Phoenician','Greek','Latin'];
  heads.forEach((hd,i)=>{ const x=x0+i*cw+cw/2; s+='<text x="'+x+'" y="'+(y0-36)+'" text-anchor="middle" font-size="12" font-weight="700" fill="#e6e6e6">'+hd+'</text><text x="'+x+'" y="'+(y0-20)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+(i===0?'by 2000 BC':yr(LETTERS[0].stages[i].y))+'</text>'; if(i) s+='<text x="'+(x0+i*cw)+'" y="'+(y0-28)+'" text-anchor="middle" font-size="14" fill="#3d444d">\\u2192</text>'; });
  LETTERS.forEach((L,r)=>{ const y=y0+r*ch; s+='<g data-letter="'+L.k+'" style="cursor:pointer"><text x="'+(x0-40)+'" y="'+(y+ch/2+10)+'" text-anchor="middle" font-size="28" font-weight="700" fill="'+(hot===L.k?'#ffffff':'#58a6ff')+'">'+L.L+'</text><text x="'+(x0-40)+'" y="'+(y+ch/2+28)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+L.thing+'</text></g>';
    L.stages.forEach((st,i)=>{ const cx=x0+i*cw+cw/2, cy=y+ch/2, k=L.k+':'+i, on=hot===k; const sc=box/60;
      s+='<g data-cell="'+k+'" style="cursor:pointer"><rect x="'+(cx-box/2-8)+'" y="'+(cy-box/2-4)+'" width="'+(box+16)+'" height="'+(box+8)+'" rx="8" fill="'+(on?'#26303d':'#1a1a1a')+'" stroke="'+(on?'#58a6ff':'#2b2b2b')+'"/>';
      s+='<g transform="translate('+(cx-box/2)+','+(cy-box/2)+') scale('+sc.toFixed(3)+')"><path d="'+st.d+'" fill="none" stroke="'+(on?'#ffffff':'#e6e6e6')+'" stroke-width="'+(i<2?3.2:3.6)+'" stroke-linecap="round" stroke-linejoin="round"/></g>';
      s+='<text x="'+cx+'" y="'+(cy+box/2+18)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+esc(st.name.split(',')[0])+'</text></g>'; });
    const cy=y+ch/2; s+='<g data-letter="'+L.k+'" style="cursor:pointer"><rect x="'+(mx-box/2-8)+'" y="'+(cy-box/2-4)+'" width="'+(box+16)+'" height="'+(box+8)+'" rx="8" fill="#1a1a1a" stroke="#58a6ff" stroke-opacity="0.6"/>';
    s+='<g class="mg" data-morph="'+L.k+'" transform="translate('+(mx-box/2)+','+(cy-box/2)+') scale('+(box/60).toFixed(3)+')">'+morphSvg(L.k)+'</g></g>'; });
  return {svg:s, h:y0+LETTERS.length*ch+10}; }

/* ---- the letters in between: every stage's strokes resampled to one point count, then carried point to point ---- */
const NP=48; let STROKES=null;
function subpaths(d){ return d.match(/M[^M]*/g).map(sd=>{ const m=sd.match(/^M\s*([-\d.]+)[ ,]([-\d.]+)\s*m\s*([-\d.]+)[ ,]([-\d.]+)/);
  return m?sd.replace(m[0],'M'+(+m[1]+ +m[3])+','+(+m[2]+ +m[4])):sd; }); }
function resample(sd){ const ms=document.getElementById('measure'); ms.setAttribute('d',sd); const L=ms.getTotalLength(), pts=[];
  for(let i=0;i<NP;i++){ const p=ms.getPointAtLength(L*i/(NP-1)); pts.push([p.x,p.y]); } return {pts,L,closed:/z\s*$/i.test(sd.trim())||/a[^a]*a/i.test(sd)}; }
function strokes(){ if(STROKES) return STROKES; STROKES={};
  for(const L of LETTERS) STROKES[L.k]=L.stages.map(st=>subpaths(st.d).map(resample).sort((a,b)=>b.L-a.L));
  return STROKES; }
// each stroke is carried to its partner in the next stage by a turn about its center and a change of shape:
// the turn is the one that best lays the partner over it (a least-squares fit), so a picture turning on
// its side turns rather than folding through itself; of the partner's two directions (and, for two closed
// strokes, its starting points) the one that needs the least change of shape is used
const center=P=>{ let x=0,y=0; for(const p of P){ x+=p[0]; y+=p[1]; } return [x/P.length,y/P.length]; };
function fit(a,b){ const ca=center(a), cb=center(b); let num=0, den=0;
  for(let i=0;i<a.length;i++){ const ax=a[i][0]-ca[0], ay=a[i][1]-ca[1], bx=b[i][0]-cb[0], by=b[i][1]-cb[1]; num+=bx*ay-by*ax; den+=bx*ax+by*ay; }
  const th=Math.atan2(num,den), c=Math.cos(th), s=Math.sin(th); let cost=0; const rb=[];
  for(let i=0;i<a.length;i++){ const bx=b[i][0]-cb[0], by=b[i][1]-cb[1], rx=c*bx-s*by, ry=s*bx+c*by; rb.push([rx,ry]); cost+=Math.hypot(a[i][0]-ca[0]-rx,a[i][1]-ca[1]-ry); }
  return {th,ca,cb,rb,cost}; }
function partner(a,b){ const cand=[b.pts, b.pts.slice().reverse()];
  if(a.closed&&b.closed){ const ring=b.pts.slice(0,NP-1); for(let k=1;k<NP-1;k++){ const r=ring.slice(k).concat(ring.slice(0,k)); r.push(r[0]); cand.push(r, r.slice().reverse()); } }
  let best=null; for(const c of cand){ const f=fit(a.pts,c); f.cost+=20*Math.abs(f.th); if(!best||f.cost<best.cost-1e-6) best=f; } return best; }   // a small charge per radian keeps a shape from turning when it need not
const PAIRS={};
function pairs(k,i){ const key=k+i; if(PAIRS[key]) return PAIRS[key]; const S=strokes()[k], A=S[i], B=S[i+1], out=[];
  for(let j=0;j<Math.max(A.length,B.length);j++){ const a=A[j], b=B[j]; out.push(a&&b?{a,f:partner(a,b)}:a?{a}:{b}); }
  return PAIRS[key]=out; }
function morphStrokes(k,m){ const i=Math.min(3,Math.floor(m)), t=m-i, out=[];
  for(const q of pairs(k,i)){
    if(q.f){ const {th,ca,cb,rb}=q.f, c=Math.cos(-t*th), s=Math.sin(-t*th), ox=ca[0]+(cb[0]-ca[0])*t, oy=ca[1]+(cb[1]-ca[1])*t;
      out.push({pts:q.a.pts.map((p,n)=>{ const x=(p[0]-ca[0])*(1-t)+rb[n][0]*t, y=(p[1]-ca[1])*(1-t)+rb[n][1]*t; return [ox+c*x-s*y, oy+s*x+c*y]; }),o:1}); }
    else if(q.a) out.push({pts:q.a.pts,o:1-t}); else out.push({pts:q.b.pts,o:t}); }
  return {strokes:out, w:3.2+(i+t>=2?0.4:Math.max(0,i+t-1)*0.4)}; }
function morphSvg(k){ const r=morphStrokes(k,morph);
  return r.strokes.filter(x=>x.o>0.01).map(x=>'<path class="mp" d="M'+x.pts.map(p=>p[0].toFixed(2)+','+p[1].toFixed(2)).join('L')+'" fill="none" stroke="#e6e6e6" stroke-width="'+r.w.toFixed(2)+'" stroke-linecap="round" stroke-linejoin="round" opacity="'+x.o.toFixed(2)+'"/>').join(''); }
const STAGES=['Egyptian sign','Proto-Sinaitic','Phoenician','Greek','Latin'];
function morphLabel(){ const i=Math.round(morph); return Math.abs(morph-i)<0.02?STAGES[i]:STAGES[Math.floor(morph)]+' to '+STAGES[Math.floor(morph)+1]; }
function setMorph(v){ morph=Math.max(0,Math.min(4,v)); document.getElementById('morph').value=Math.round(morph*100); document.getElementById('morphOut').textContent=morphLabel();
  if(view!=='letters') return; for(const g of document.querySelectorAll('#wsvg g.mg')) g.innerHTML=morphSvg(g.getAttribute('data-morph'));
  const band=document.getElementById('mband'); if(band) band.setAttribute('x',100+Math.round(morph)*140+6);
  const lab=[...document.querySelectorAll('#wsvg text')].find(t=>/^stage /.test(t.textContent)); if(lab) lab.textContent='stage '+(morph+1).toFixed(1); }

/* ---- the signs ---- */
const C={x:190,y:30,w:720,bar:26,lo:10,hi:10000};
const CX=n=>C.x+Math.log10(n/C.lo)/Math.log10(C.hi/C.lo)*C.w;
function countsView(){ const rows=[...COUNTS].sort((a,b)=>b.signs-a.signs||a.n.localeCompare(b.n)); let s='';
  const h=C.y+rows.length*C.bar+50;
  for(const n of [10,100,1000,10000]){ const x=CX(n); s+='<line x1="'+x.toFixed(1)+'" y1="'+C.y+'" x2="'+x.toFixed(1)+'" y2="'+(C.y+rows.length*C.bar)+'" stroke="#2b2b2b"/><text x="'+x.toFixed(1)+'" y="'+(C.y+rows.length*C.bar+18)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+fmt(n)+'</text>'; }
  s+='<text x="'+(C.x+C.w/2)+'" y="'+(C.y+rows.length*C.bar+38)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">signs to learn, on a log scale</text>';
  const kd=kindOn();
  rows.forEach((c,i)=>{ const y=C.y+i*C.bar, on=hot===c.k; s+='<g data-count="'+c.k+'" style="cursor:pointer"'+(kd&&c.t!==kd?' opacity="0.25"':'')+'><rect x="'+C.x+'" y="'+(y+5)+'" width="'+(CX(c.signs)-C.x).toFixed(1)+'" height="'+(C.bar-10)+'" rx="3" fill="'+TYPES[c.t].c+'" opacity="'+(on?1:0.8)+'"/>';
    s+='<text x="'+(C.x-8)+'" y="'+(y+C.bar/2+4)+'" text-anchor="end" font-size="11.5" fill="'+(on?'#ffffff':'#c8c8c8')+'">'+esc(c.n)+'</text><text x="'+(CX(c.signs)+6).toFixed(1)+'" y="'+(y+C.bar/2+4)+'" font-size="10.5" fill="#9a9a9a">'+fmt(c.signs)+'</text></g>'; });
  return {svg:s, h}; }

/* ---- render and wiring ---- */
function legend(){ const keys=view==='letters'?[]:view==='tree'?Object.keys(TYPES):[...new Set(COUNTS.map(c=>c.t))]; const kd=kindOn(), lgd=document.getElementById('legend');
  // rebuilt only when the view's kinds change, so the key under the pointer is never swapped out from under it
  if(lgd.dataset.keys!==keys.join()){ lgd.dataset.keys=keys.join(); lgd.innerHTML=keys.map(k=>'<span data-t="'+k+'" style="--c:'+TYPES[k].c+'">'+TYPES[k].n+'</span>').join(''); }
  for(const sp of lgd.querySelectorAll('span[data-t]')) sp.classList.toggle('on',kd===sp.dataset.t);
  document.getElementById('treeCtl').hidden=view!=='tree'; document.getElementById('letterCtl').hidden=view!=='letters'; }
function render(){ const q=view==='tree'?treeView():view==='letters'?lettersView():countsView(); el.innerHTML='<svg viewBox="0 0 '+W+' '+q.h+'" xmlns="http://www.w3.org/2000/svg" id="wsvg"><rect width="'+W+'" height="'+q.h+'" fill="#121212"/>'+q.svg+'</svg>'; legend(); }
function home(){ if(view==='tree') showTree(); else if(view==='letters') showLetters(); else showCounts(); }
function setView(v){ stopPlays(); view=v; hot=null; pinned=null; kindHover=null; kindPin=null; for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on',b.dataset.v===v); render(); home(); }
document.getElementById('views').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setView(b.dataset.v); });
el.addEventListener('pointerover',e=>{ const g=e.target.closest('[data-script],[data-cell],[data-letter],[data-count]'); if(!g) return;
  const k=g.getAttribute('data-script')||g.getAttribute('data-cell')||g.getAttribute('data-letter')||g.getAttribute('data-count'); if(k===hot) return; hot=k; render();
  if(g.hasAttribute('data-script')) showScript(k); else if(g.hasAttribute('data-cell')){ const [lk,i]=k.split(':'); showStage(lk,+i); } else if(g.hasAttribute('data-letter')) showLetter(k); else showCount(k); });
el.addEventListener('pointerleave',()=>{ if(pinned){ if(hot!==pinned){ hot=pinned; render(); showScript(pinned); } return; } if(hot){ hot=null; render(); home(); } });
/* ---- a script clicked stays lit with its line; a second click or Escape lets go ---- */
el.addEventListener('click',e=>{ if(view!=='tree') return; const g=e.target.closest('[data-script]');
  if(!g){ if(pinned){ pinned=null; hot=null; render(); home(); } return; }
  const k=g.getAttribute('data-script'); pinned=pinned===k?null:k; hot=pinned; render(); if(pinned) showScript(k); else home(); });
document.addEventListener('keydown',e=>{ if(e.key!=='Escape') return; if(pinned||kindPin){ pinned=null; kindPin=null; hot=null; render(); home(); } });
/* ---- a kind in the key lights every script of that kind ---- */
const lg=document.getElementById('legend');
lg.addEventListener('pointerover',e=>{ const sp=e.target.closest('span[data-t]'); if(!sp||kindHover===sp.dataset.t) return; kindHover=sp.dataset.t; render(); });
lg.addEventListener('pointerleave',()=>{ if(kindHover){ kindHover=null; render(); } });
lg.addEventListener('click',e=>{ const sp=e.target.closest('span[data-t]'); if(!sp) return; kindPin=kindPin===sp.dataset.t?null:sp.dataset.t; kindHover=null; render(); });
/* ---- the year: scripts appear at their first inscription ---- */
const fmtYear=y=>y>=2030-5?'today':yr(Math.round(y/10)*10);
function setYear(v){ year=Math.max(-3400,Math.min(2030,v)); document.getElementById('year').value=Math.round(year); document.getElementById('yearOut').textContent=fmtYear(year)+', '+SCRIPTS.filter(c=>c.y<=year).length+' scripts'; if(view==='tree') render(); }
let yId=null, mId=null;
function playBtn(id,on){ const b=document.getElementById(id); b.textContent=on?'Pause':'Play'; b.classList.toggle('on',on); }
function stopPlays(){ if(yId){ cancelAnimationFrame(yId); clearTimeout(yId); yId=null; playBtn('yPlay',false); } if(mId){ cancelAnimationFrame(mId); clearTimeout(mId); mId=null; playBtn('mPlay',false); } }
document.getElementById('year').addEventListener('input',e=>{ stopPlays(); setYear(+e.target.value); });
document.getElementById('yPlay').addEventListener('click',()=>{ if(yId){ stopPlays(); return; } if(year>=2030) setYear(-3400);
  playBtn('yPlay',true); const from=year, dur=9000*(2030-from)/5430;
  if(REDUCED){ const step=()=>{ const nx=SCRIPTS.map(c=>c.y).filter(y=>y>year).sort((a,b)=>a-b)[0]; if(nx==null){ setYear(2030); yId=null; playBtn('yPlay',false); return; } setYear(nx); yId=setTimeout(step,500); }; step(); return; }
  const t0=performance.now(); const run=now=>{ const t=Math.min(1,(now-t0)/dur); setYear(from+(2030-from)*t); if(t<1) yId=requestAnimationFrame(run); else { yId=null; playBtn('yPlay',false); } }; yId=requestAnimationFrame(run); });
/* ---- the stage: the letters drawn in between ---- */
document.getElementById('morph').addEventListener('input',e=>{ stopPlays(); setMorph(+e.target.value/100); });
document.getElementById('mPlay').addEventListener('click',()=>{ if(mId){ stopPlays(); return; } if(morph>=4) setMorph(0);
  playBtn('mPlay',true); const SEG=1250, MOVE=900, start=Math.floor(morph), frac=morph-start;
  if(REDUCED){ const step=()=>{ if(morph>=4){ mId=null; playBtn('mPlay',false); return; } setMorph(Math.floor(morph)+1); mId=setTimeout(step,800); }; mId=setTimeout(step,300); return; }
  const t0=performance.now()-frac*MOVE; const run=now=>{ const tau=now-t0, seg=Math.floor(tau/SEG), loc=Math.min(1,(tau-seg*SEG)/MOVE), m=start+seg+ease(loc);
    if(m>=4){ setMorph(4); mId=null; playBtn('mPlay',false); return; } setMorph(m); mId=requestAnimationFrame(run); }; mId=requestAnimationFrame(run); });

render(); showTree(); setYear(2030); setMorph(0);
window.__writing=(q)=>{ const {pos,n}=layout(); const o={view,hot,lanes:n,card:document.getElementById('numTxt').innerText,name:document.getElementById('nameTxt').innerText,body:document.getElementById('bodyTxt').innerText,
  dots:document.querySelectorAll('#wsvg g[data-script]').length, year, morph, pinned, kind:kindOn(), playing:{year:!!yId,morph:!!mId}, cells:document.querySelectorAll('#wsvg g[data-cell]').length, bars:document.querySelectorAll('#wsvg g[data-count]').length};
  if(q&&q.script){ const c=document.querySelector('#wsvg g[data-script="'+q.script+'"] circle'); o.dot=c?[+c.getAttribute('cx'),+c.getAttribute('cy')]:null; o.tx=TX(byK[q.script].y); o.lane=pos[q.script].lane; }
  if(q&&q.count){ const r=document.querySelector('#wsvg g[data-count="'+q.count+'"] rect'); o.barw=r?+r.getAttribute('width'):null; o.cx=CX(COUNTS.find(c=>c.k===q.count).signs)-C.x; }
  if(q&&q.edges){ o.edges=[...document.querySelectorAll('#wsvg path[d^="M"]')].filter(p=>p.getAttribute('fill')==='none'&&/ C/.test(p.getAttribute('d'))).map(p=>p.getAttribute('d')); }
  return o; };
</script>
</body>
</html>
"""

html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__TYPES__", _js(types)).replace("__SCRIPTS__", _js(scripts)).replace("__LETTERS__", _js(letters)).replace("__COUNTS__", _js(counts))
        .replace("__NOTE1__", NOTE1).replace("__NOTE1B__", NOTE1B).replace("__MOTION__", MOTION).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(SCRIPTS)} scripts, {len(LETTERS)} letters, {len(COUNTS)} counts")
