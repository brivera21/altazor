#!/usr/bin/env python3
"""Generate chinese.html, how far into Chinese a reader has to go.

Three views on one idea. Characters: the cumulative share of running
text that the commonest n characters account for, from Jun Da's count of
193 million characters of written Chinese. Words: the same curve for
words, from 72 million words of film subtitles, which flattens far more
slowly because vocabulary is open where the character set is nearly
closed. Written and spoken: the same characters counted in both corpora,
which puts some of them hundreds of ranks apart.

The curve and the grid share a rank. Moving the mark on the curve dims
the grid past that rank, so the share and the characters it stands for
are the same statement twice.

Data: tools/data/chinese.json, baked by build_chinese_data.py.

Usage: python3 build_chinese.py
"""

import json
from pathlib import Path

import apa

ROOT = Path(__file__).parent.parent
D = json.loads((ROOT / "tools" / "data" / "chinese.json").read_text())

NOTE1 = ("Chinese writes with a set rather than an alphabet; the question "
         "is how far into it a reader has to go. The curve is "
         "cumulative: at each rank, the share of running text that every "
         "character up to there accounts for. The first hundred carry 41.8 "
         "per cent of written Chinese, the first thousand 89.1, the first "
         "2,500 carry 98.5.")

NOTE2 = ("Words do not behave that way. The hundred commonest carry about "
         "half of film dialogue, and then the curve flattens: 20,000 words "
         "are needed for 97 per cent. A writing system can be nearly closed "
         "while the vocabulary written in it stays open. The two counts also "
         "come from different corpora, one written and one spoken, and the "
         "third view sets the same characters against each other in both.")

METHOD = (
    "Where the counts come from, and what they cannot settle. The "
    "character column is Jun Da's frequency list, 193,504,018 characters "
    "of modern written Chinese collected up to 2004, which is the standard "
    "citation for this and is old enough that the internet barely appears "
    "in it. The word column is the Chinese half of the OpenSubtitles 2018 "
    "corpus, 72,175,750 words of film and television dialogue, already "
    "segmented; segmentation is a decision rather than a fact, and a "
    "different segmenter would move the ranks. Glosses are CC-CEDICT, "
    "merged across two vintages because the newer file drops transparent "
    "compounds the older one keeps. A gloss marked as composed is the sum "
    "of the parts and not a dictionary entry. Radicals, stroke counts and "
    "the HSK level are Unihan by way of hanziDB.")

GAPNOTE = (
    "What the comparison is and is not. The spoken count is taken by "
    "adding up the characters inside the words of the subtitle list, so it "
    "is a count of dialogue as written down in subtitles, not of speech "
    "recorded. The two corpora are also forty years apart in places and "
    "were built for different purposes, so a large gap between the two "
    "ranks is a fact about the two corpora before it is a fact about the "
    "language. The gaps that are worth reading are the ones with an "
    "obvious cause, such as the characters of politics and of place names, "
    "which are common in news and rare in dialogue.")

CSS = """
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
  --line:#2b2b2b; --accent:#58a6ff; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica,
  Arial, sans-serif; }
.wrap { max-width:1180px; margin:0 auto; padding:26px 20px 60px; }
header.site { display:flex; justify-content:space-between; align-items:baseline;
  gap:16px; flex-wrap:wrap; margin-bottom:18px; }
.brand { font-weight:700; letter-spacing:.14em; color:var(--text);
  text-decoration:none; font-size:14px; }
.brand:hover { color:var(--accent); }
nav.site a { color:var(--muted); text-decoration:none; font-size:14px;
  margin-right:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 10px; font-size:26px; }
.bar { display:flex; gap:8px; align-items:center; flex-wrap:wrap;
  margin-bottom:10px; }
button { font:inherit; font-size:13.5px; padding:6px 14px; border-radius:999px;
  border:1px solid var(--line); background:#1a1a1a; color:var(--text);
  cursor:pointer; }
button:hover { border-color:var(--accent); }
button.on { background:var(--accent); border-color:var(--accent);
  color:#0b0b0b; }
.bar2 { display:flex; gap:16px; align-items:center; flex-wrap:wrap;
  margin-bottom:12px; color:var(--muted); font-size:12.5px; }
.bar2 label { display:flex; gap:8px; align-items:center; }
.bar2 label[hidden] { display:none; }
#rankLbl { min-width:11.5em; color:var(--text); }
@media (max-width:600px){ #rankWrap { flex-wrap:wrap; } #rankLbl { min-width:0; width:100%; } }
.bar2 input[type=range] { width:220px; accent-color:var(--accent); }
.bar2 button { padding:4px 11px; font-size:12.5px; }
.bar2 .hsk { display:flex; gap:4px; align-items:center; }
.bar2 .hsk span { margin-right:4px; }
.bar2 .hsk button { padding:3px 9px; font-size:12px; min-width:30px; }
.bar2 input[type=search] { font:inherit; font-size:12.5px; padding:4px 10px;
  border-radius:999px; border:1px solid var(--line); background:#151515;
  color:var(--text); width:170px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
.col { flex:1 1 620px; min-width:0; }
#curve svg { width:100%; height:auto; display:block; }
#grid { margin-top:14px; display:flex; flex-wrap:wrap; gap:4px; outline:none; border-radius:8px; }
#grid:focus-visible { box-shadow:0 0 0 1px var(--accent); }
#grid .gh { flex:1 0 100%; color:var(--muted); font-size:11.5px;
  letter-spacing:.06em; text-transform:uppercase; margin:8px 0 2px; }
#grid .gr { flex:1 0 100%; display:flex; flex-wrap:wrap; gap:4px; }
.t { border:1px solid var(--line); border-radius:7px; padding:5px 6px 4px;
  text-align:center; cursor:pointer; background:#171717; min-width:44px; }
.t .h { font-size:20px; line-height:1.15;
  font-family:"Noto Sans SC","Source Han Sans SC","PingFang SC",
  "Hiragino Sans GB","Microsoft YaHei",sans-serif; }
.t .p { font-size:10px; color:var(--muted); line-height:1.3;
  white-space:nowrap; }
.t.past { opacity:.22; }
.t.out { opacity:.12; }
.t.on { border-color:#fff; background:#222c38; }
.t.pin { border-color:var(--accent); box-shadow:0 0 0 1px var(--accent); }
.t.w .h { font-size:17px; }
.side { flex:0 0 320px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line);
  border-radius:12px; padding:16px; }
#kindTxt { color:var(--muted); font-size:11.5px; letter-spacing:.09em;
  text-transform:uppercase; }
#bigTxt { font-size:44px; line-height:1.1; margin:4px 0 2px;
  font-family:"Noto Sans SC","Source Han Sans SC","PingFang SC",
  "Hiragino Sans GB","Microsoft YaHei",sans-serif; }
#pyTxt { font-size:17px; color:var(--accent); }
#glTxt { font-size:13.5px; line-height:1.5; margin-top:6px; }
.rows { margin-top:12px; border-top:1px solid var(--line); padding-top:10px;
  font-size:12.5px; }
.rows div { display:flex; justify-content:space-between; gap:12px;
  padding:2px 0; }
.rows span.k { color:var(--muted); }
.rows span.v { font-variant-numeric:tabular-nums; }
.made { color:var(--muted); font-size:11.5px; margin-top:8px; }
.note { color:var(--muted); font-size:12.5px; margin-top:22px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
details.sources { color:var(--muted); font-size:12.5px; margin-top:14px;
  max-width:760px; border-top:1px solid var(--line); padding-top:12px; }
details.sources summary { cursor:pointer; color:var(--accent); }
details.sources p { margin:9px 0 0; }
details.sources .refs { margin-top:12px; }
.refs { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.refs p { margin:0 0 8px; overflow-wrap:anywhere; }
.refs a { color:var(--accent); }
__APACSS__
h2.refh { font-size:15px; margin:26px 0 8px; }
@media (max-width:900px){ .stage{flex-direction:column;}
  .col{flex:none; width:100%;}
  .side{position:static; width:100%; flex:none; order:-1;} }
@media (max-width:600px){ #curve{overflow-x:auto;} #curve svg{min-width:600px;} }
"""

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Most Used Chinese &middot; Altazor</title>
<meta name="description" content="How far into the Chinese character set a
reader has to go, and how much further the vocabulary runs.">
<style>__CSS__</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html#abstractions">&larr; Library
  &middot; Abstractions</a> <a href="prime-spiral.html">The Prime
  Spiral</a> <a href="languages.html">Languages</a></nav>
</header>
<h1>The Most Used Chinese</h1>
<div class="bar">
  <button id="vChar" class="on">Characters</button>
  <button id="vWord">Words</button>
  <button id="vBoth">Written and spoken</button>
</div>
<div class="bar2">
  <label id="rankWrap"><span id="rankLbl">The first 1,200 characters</span> <input type="range" id="rank" min="1" max="1200"
  value="1200"> <span id="rankTxt"></span></label>
  <button id="run" type="button" title="the mark runs up the curve from 1">Run</button>
  <button id="vCmp" type="button" hidden>Words over it</button>
  <span class="hsk" id="hsk" hidden><span>HSK</span></span>
  <label><input type="search" id="q" placeholder="Find one"></label>
</div>
<div class="stage">
  <div class="col">
    <div id="curve"></div>
    <div id="grid"></div>
  </div>
  <div class="side"><div class="card">
    <div id="kindTxt"></div>
    <div id="bigTxt"></div>
    <div id="pyTxt"></div>
    <div id="glTxt"></div>
    <div class="rows" id="rowsTxt"></div>
    <div class="made" id="madeTxt"></div>
  </div></div>
</div>
<p class="note">__NOTE1__</p>
<details class="sources"><summary>Sources</summary>
<p>__NOTE2__</p>
<p>The mark runs up the curve when the page opens and again from Run, the
grid lighting in order behind it. Words over it draws the word curve on the
same axis as the character curve, so that the one flattening and the other
not is one picture. The HSK chips light only the characters of that level
and below, and set the slider to the same number of characters by rank, so
the two coverages can be compared; the levels are those of the 1,200
characters here, and HSK 6 reaches past them. A character clicked stays on
the card, and the arrow keys then walk the grid by rank; Escape lets go.</p>
<p>__METHOD__</p><p>__GAPNOTE__</p>
<div class="refs">__REFS__</div>
</details>
</div>
<script>
const D=__DATA__;
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const fmt=n=>n.toLocaleString('en-US');
let view='char', cut=1200, hot=null, firstI=1, pinned=null, level=0, cmp=false, cmpT=0;
const REDUCED=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const ease=t=>t<0.5?2*t*t:1-Math.pow(-2*t+2,2)/2;

// [glyph, pinyin, gloss, share of text, cumulative share, ...]
const CH=D.chars, WD=D.words;
function rows(){ return view==='word'?WD:CH; }
function curves(){
  if(view==='word') return [{p:D.wcurve,c:'#e0a458',l:'words, subtitles'}];
  if(view==='both') return [
    {p:D.ccurve,c:'#58a6ff',l:'characters, written'},
    {p:D.scurve,c:'#7ee081',l:'characters, spoken'}];
  const out=[{p:D.ccurve,c:'#58a6ff',l:'characters, written'}];
  if(cmpT>0) out.push({p:D.wcurve,c:'#e0a458',l:'words, subtitles',o:cmpT});
  return out;
}
// the HSK levels of the characters here: how many at or below each level,
// and what share of running text they carry between them
function levelSet(lv){ return CH.map((r,i)=>[r,i+1]).filter(([r])=>r[7]&&r[7]<=lv); }
function levelCover(lv){ return levelSet(lv).reduce((a,[r])=>a+r[3],0); }

const W=760, H=250, ML=44, MR=14, MT=12, MB=30;
const lg=Math.log10;
function drawCurve(){
  const cs=curves();
  let maxr=Math.max(...cs.filter(c=>c.o==null).map(c=>c.p[c.p.length-1][0]));
  if(view==='char'&&cmpT>0){ const a=lg(D.ccurve[D.ccurve.length-1][0]), b=lg(D.wcurve[D.wcurve.length-1][0]); maxr=Math.pow(10,a+(b-a)*cmpT); }
  const X=r=>ML+lg(Math.max(1,r))/lg(maxr)*(W-ML-MR);
  const Y=v=>H-MB-v/100*(H-MT-MB);
  let s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Cumulative '
    +'share of running text against rank">';
  for(let v=0;v<=100;v+=25){
    s+='<line x1="'+ML+'" y1="'+Y(v)+'" x2="'+(W-MR)+'" y2="'+Y(v)
      +'" stroke="#242424"/>'
      +'<text x="'+(ML-7)+'" y="'+(Y(v)+4)+'" text-anchor="end" font-size="11" '
      +'fill="#7d7d7d">'+v+'%</text>';
  }
  for(const r of [1,10,100,1000,10000]){
    if(r>maxr) continue;
    s+='<line x1="'+X(r)+'" y1="'+MT+'" x2="'+X(r)+'" y2="'+(H-MB)
      +'" stroke="#1e1e1e"/>'
      +'<text x="'+X(r)+'" y="'+(H-MB+15)+'" text-anchor="middle" '
      +'font-size="11" fill="#7d7d7d">'+fmt(r)+'</text>';
  }
  s+='<text x="'+((ML+W-MR)/2)+'" y="'+(H-2)+'" text-anchor="middle" '
    +'font-size="11" fill="#7d7d7d">rank, on a log scale</text>';
  for(const c of cs){
    s+='<path fill="none" stroke="'+c.c+'" stroke-width="2"'+(c.o!=null?' opacity="'+c.o.toFixed(2)+'"':'')+' d="'
      +c.p.filter(q=>q[0]<=maxr*1.0001).map((q,i)=>(i?'L':'M')+X(q[0]).toFixed(1)+' '+Y(q[1]).toFixed(1))
        .join('')+'"/>';
  }
  // the mark ties the curve to the grid: one rank, read two ways. With
  // two curves up there is no single rank to mark, so it comes off.
  if(view==='both'){
    let ly2=MT+14;
    for(const c of cs){
      s+='<text x="'+(ML+10)+'" y="'+ly2+'" font-size="11.5" fill="'+c.c+'">'
        +esc(c.l)+'</text>';
      ly2+=15;
    }
    s+='</svg>';
    document.getElementById('curve').innerHTML=s;
    return;
  }
  const cur=cs[0].p;
  const cov=at(cur,cut);
  s+='<line x1="'+X(cut)+'" y1="'+MT+'" x2="'+X(cut)+'" y2="'+(H-MB)
    +'" stroke="#fff" stroke-dasharray="3 3"/>'
    +'<circle cx="'+X(cut)+'" cy="'+Y(cov)+'" r="4" fill="#fff"/>';
  let lx=X(cut)+8, anc='start';
  if(lx>W-190){ lx=X(cut)-8; anc='end'; }
  s+='<text x="'+lx+'" y="'+(Y(cov)-9)+'" text-anchor="'+anc+'" font-size="12.5" '
    +'fill="#fff">'+fmt(cut)+' cover '+cov.toFixed(1)+'%</text>';
  // an HSK level: its characters' share, as a level line across the curve
  if(level&&view==='char'){
    const set=levelSet(level), lc=levelCover(level);
    s+='<line x1="'+ML+'" y1="'+Y(lc)+'" x2="'+(W-MR)+'" y2="'+Y(lc)+'" stroke="#f2c11a" stroke-dasharray="4 3"/>'
      +'<text x="'+(W-MR-4)+'" y="'+(Y(lc)+(lc>cov?-6:14))+'" text-anchor="end" font-size="11.5" fill="#f2c11a">HSK 1 to '+level+': '+fmt(set.length)+' of these characters cover '+lc.toFixed(1)+'%</text>';
  }
  let ly=MT+14;
  for(const c of cs){
    s+='<text x="'+(ML+10)+'" y="'+ly+'" font-size="11.5" fill="'+c.c+'"'+(c.o!=null?' opacity="'+c.o.toFixed(2)+'"':'')+'>'
      +esc(c.l)+'</text>';
    ly+=15;
  }
  s+='</svg>';
  document.getElementById('curve').innerHTML=s;
}
// the curve is sampled, so a rank between two samples is read across
function at(p,r){
  let lo=p[0];
  for(const q of p){ if(q[0]<=r) lo=q; else {
    const t=(lg(r)-lg(lo[0]))/(lg(q[0])-lg(lo[0])||1);
    return lo[1]+t*(q[1]-lo[1]); } }
  return lo[1];
}

function gaps(){
  // characters furthest apart in the two counts, both ways
  const out=CH.map((r,i)=>({r,i:i+1,g:r[8]?r[8]-(i+1):0}))
    .filter(x=>x.r[8]);
  out.sort((a,b)=>b.g-a.g);
  return out;
}

let TILES=[];   // the tiles in the grid, by index, so dimming need not rebuild them
function drawGrid(){
  const g=document.getElementById('grid');
  const q=document.getElementById('q').value.trim().toLowerCase();
  const keep=x=>!q || x.r[0].indexOf(q)>=0
    || x.r[1].toLowerCase().indexOf(q)>=0
    || x.r[2].toLowerCase().indexOf(q)>=0;
  const tile=x=>'<div class="t'+(view==='word'?' w':'')+'" data-i="'+x.i+'">'
    +'<div class="h">'+esc(x.r[0])+'</div>'
    +'<div class="p">'+esc(x.r[1])+'</div></div>';
  let html='';
  if(view==='both'){
    const gp=gaps();
    const groups=[
      ['Far commoner in writing than in dialogue', gp.slice(0,60)],
      ['Far commoner in dialogue than in writing', gp.slice(-60).reverse()]];
    for(const [label,set] of groups){
      const on=set.filter(keep);
      if(!on.length) continue;
      html+='<div class="gh">'+esc(label)+'</div>'
        +'<div class="gr">'+on.map(tile).join('')+'</div>';
    }
    firstI = gaps().length?gaps()[0].i:1;
  } else {
    html=rows().map((r,i)=>({r,i:i+1})).filter(keep).map(tile).join('');
    firstI=1;
  }
  g.innerHTML=html;
  TILES=[...g.querySelectorAll('.t')];
  TILES.forEach(e=>{
    e.addEventListener('pointerenter',()=>{ if(!pinned) sel(+e.dataset.i); });
    e.addEventListener('click',()=>{ pin(pinned===+e.dataset.i?null:+e.dataset.i); });
  });
  dimGrid();
}
// past the mark the grid goes dim; outside an HSK level, dimmer still
function dimGrid(){
  if(view==='both') return;
  const rs=rows();
  for(const e of TILES){ const i=+e.dataset.i;
    e.classList.toggle('past', i>cut);
    e.classList.toggle('out', view==='char'&&level>0&&!(rs[i-1][7]&&rs[i-1][7]<=level)); }
}

function sel(i){
  hot=i;
  document.querySelectorAll('#grid .t').forEach(e=>
    e.classList.toggle('on', +e.dataset.i===i));
  const r=rows()[i-1];
  if(!r) return;
  document.getElementById('kindTxt').textContent = view==='both'
    ? 'Character, written rank '+fmt(i)
    : (view==='word'?'Word':'Character')+' number '+fmt(i)+(pinned===i?', pinned':'');
  document.getElementById('bigTxt').textContent=r[0];
  document.getElementById('pyTxt').textContent=r[1];
  document.getElementById('glTxt').textContent=r[2];
  const out=[];
  const add=(k,v)=>out.push('<div><span class="k">'+esc(k)
    +'</span><span class="v">'+esc(v)+'</span></div>');
  add('Share of running '+(view==='word'?'dialogue':'text'),
      r[3].toFixed(r[3]<0.01?4:3)+'%');
  add('Cumulative to here', r[4].toFixed(2)+'%');
  if(view==='word'){
    add('Characters', String(r[0].length));
  } else {
    if(r[5]) add('Strokes', String(r[5]));
    if(r[6]) add('Radical', r[6]);
    if(r[7]) add('HSK level', String(r[7]));
    if(r[8]){
      add('Rank in writing', fmt(i));
      add('Rank in dialogue', fmt(r[8]));
    }
  }
  document.getElementById('rowsTxt').innerHTML=out.join('');
  document.getElementById('madeTxt').textContent =
    (view==='word'&&r[5]) ? 'This gloss is composed from the parts. Neither '
      +'dictionary carries the whole word.' : '';
}
// a click pins a character to the card; the arrow keys then walk the grid
function pin(i){
  pinned=i;
  document.querySelectorAll('#grid .t').forEach(e=>e.classList.toggle('pin', +e.dataset.i===i));
  if(i){ sel(i); document.getElementById('grid').focus({preventScroll:true}); }
  else if(hot) sel(hot);
}
document.getElementById('grid').setAttribute('tabindex','0');
document.getElementById('grid').addEventListener('keydown',e=>{
  if(e.target.tagName==='INPUT') return;
  if(e.key==='Escape'){ pin(null); return; }
  if(view==='both') return;
  const step={ArrowRight:1,ArrowLeft:-1,ArrowDown:7,ArrowUp:-7}[e.key]; if(!step) return;
  e.preventDefault();
  const i=Math.max(1,Math.min(rows().length,(pinned||hot||1)+step));
  pin(i);
  const t=document.querySelector('#grid .t[data-i="'+i+'"]'); if(t) t.scrollIntoView({block:'nearest'});
});

function setRank(v){
  cut=v;
  const cov=at(curves()[0].p,cut);
  document.getElementById('rankLbl').textContent =
    'The first '+fmt(cut)+' '+(view==='word'?'words':'characters');
  document.getElementById('rankTxt').textContent =
    'cover '+cov.toFixed(1)+'% of running '+(view==='word'?'dialogue':'text');
  document.getElementById('rank').value=cut;
  drawCurve(); dimGrid();
}
// the mark runs up the curve from 1, the grid lighting in order behind it
let runId=null;
function run(){
  const n=rows().length, t0=performance.now(), dur=REDUCED?0:3200;
  const btn=document.getElementById('run');
  if(runId){ cancelAnimationFrame(runId); runId=null; btn.textContent='Run'; return; }
  btn.textContent='Pause';
  const go=now=>{ const t=dur?Math.min(1,(now-t0)/dur):1;
    setRank(Math.max(1,Math.round(Math.pow(n,ease(t)))));
    if(t<1) runId=requestAnimationFrame(go); else { runId=null; btn.textContent='Run'; } };
  go(t0);
}
document.getElementById('run').addEventListener('click',run);
// the word curve drawn over the character curve, the axis stretching to fit it
let cmpId=null;
function setCmp(on){
  cmp=on; document.getElementById('vCmp').classList.toggle('on',on);
  const from=cmpT, to=on?1:0, t0=performance.now(), dur=REDUCED?0:900;
  if(cmpId) cancelAnimationFrame(cmpId);
  const go=now=>{ const t=dur?Math.min(1,(now-t0)/dur):1; cmpT=from+(to-from)*ease(t); drawCurve(); if(t<1) cmpId=requestAnimationFrame(go); else cmpId=null; };
  go(t0);
}
document.getElementById('vCmp').addEventListener('click',()=>setCmp(!cmp));
// the HSK chips: the characters of a level and below, against the same count by rank
(function(){ const box=document.getElementById('hsk');
  for(let lv=1;lv<=6;lv++){ const b=document.createElement('button'); b.type='button'; b.dataset.lv=lv; b.textContent=lv; box.appendChild(b); }
  box.addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; setLevel(level===+b.dataset.lv?0:+b.dataset.lv); }); })();
function setLevel(lv){
  level=lv;
  document.querySelectorAll('#hsk button').forEach(b=>b.classList.toggle('on',+b.dataset.lv===lv));
  if(lv) setRank(levelSet(lv).length); else { setRank(cut); }
  if(hot) sel(hot);
}

function pick(v){
  view=v; hot=null; pinned=null;
  if(runId){ cancelAnimationFrame(runId); runId=null; document.getElementById('run').textContent='Run'; }
  for(const [k,id] of [['char','vChar'],['word','vWord'],['both','vBoth']])
    document.getElementById(id).classList.toggle('on', k===v);
  const sl=document.getElementById('rank');
  document.getElementById('rankWrap').hidden = (v==='both');
  document.getElementById('run').hidden = (v==='both');
  document.getElementById('vCmp').hidden = (v!=='char');
  document.getElementById('hsk').hidden = (v!=='char');
  if(v!=='char'){ level=0; document.querySelectorAll('#hsk button').forEach(b=>b.classList.remove('on')); }
  sl.max=rows().length; if(cut>rows().length) cut=rows().length;
  sl.value=cut;
  drawGrid();
  setRank(cut);
  sel(firstI);
}
document.getElementById('vChar').addEventListener('click',()=>pick('char'));
document.getElementById('vWord').addEventListener('click',()=>pick('word'));
document.getElementById('vBoth').addEventListener('click',()=>pick('both'));
document.getElementById('rank').addEventListener('input',e=>{
  if(runId){ cancelAnimationFrame(runId); runId=null; document.getElementById('run').textContent='Run'; }
  setRank(+e.target.value); });
document.getElementById('q').addEventListener('input',drawGrid);
pick('char');
run();
window.__chinese=()=>({view,cut,hot,pinned,level,cmp,cmpT,running:!!runId,
  lit:document.querySelectorAll('#grid .t:not(.past)').length,
  inLevel:document.querySelectorAll('#grid .t:not(.out)').length,
  levelCover:level?levelCover(level):null, levelN:level?levelSet(level).length:null,
  curves:document.querySelectorAll('#curve svg path').length});
</script>
</body>
</html>
"""

REFS = [
    (apa.web("Da, J.", 2004,
             "Modern Chinese character frequency list",
             "Chinese text computing, Middle Tennessee State University",
             "https://lingua.mtsu.edu/chinese-computing/statistics/char/"
             "list.php?Which=MO", retrieved=True),
     "The character counts and the cumulative shares, from 193,504,018 "
     "characters of written modern Chinese."),
    (apa.article(
        "Lison, P., &amp; Tiedemann, J.", 2016,
        "OpenSubtitles2016: Extracting large parallel corpora from movie and "
        "TV subtitles", "Proceedings of the 10th International Conference on "
        "Language Resources and Evaluation (LREC 2016)", None, None,
        "923-929", "https://aclanthology.org/L16-1147/"),
     "The subtitle corpus the word counts are taken from."),
    (apa.data("Dave, H.", "n.d.",
              "FrequencyWords: Frequency word lists from the OpenSubtitles "
              "2018 corpus", None, "GitHub",
              "https://github.com/hermitdave/FrequencyWords"),
     "The segmented word counts for Chinese."),
    (apa.data("MDBG", "n.d.", "CC-CEDICT: A public-domain Chinese-English "
              "dictionary", None, "Creative Commons Attribution-ShareAlike "
              "4.0", "https://www.mdbg.net/chinese/dictionary?page=cc-cedict"),
     "Pinyin and glosses, merged across two vintages."),
    (apa.data("Fawcett, R.", "n.d.", "hanziDB: Chinese characters by "
              "frequency rank, with Unihan radical, stroke count and HSK "
              "level", None, "GitHub",
              "https://github.com/ruddfawcett/hanziDB.csv"),
     "Radicals, stroke counts and HSK levels."),
    (apa.web("Unicode Consortium", "n.d.", "Unihan database",
             "Unicode", "https://www.unicode.org/charts/unihan.html",
             retrieved=True),
     "The source hanziDB draws its per-character data from."),
]


def main():
    html = (HTML
            .replace("__CSS__", CSS.replace("__APACSS__", apa.CSS))
            .replace("__NOTE1__", NOTE1)
            .replace("__NOTE2__", NOTE2)
            .replace("__METHOD__", METHOD)
            .replace("__GAPNOTE__", GAPNOTE)
            .replace("__REFS__", apa.render(REFS))
            .replace("__DATA__", json.dumps(D, separators=(",", ":"),
                                            ensure_ascii=False)))
    out = ROOT / "chinese.html"
    out.write_text(html, encoding="utf-8")
    print(f"chinese.html  {len(D['chars'])} characters, {len(D['words'])} "
          f"words, {out.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
