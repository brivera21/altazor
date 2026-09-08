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

NOTE1 = ("Chinese writes with a set rather than an alphabet, and the "
         "question this asks is how far into the set a reader has to go. "
         "The curve is cumulative: at each rank it gives the share of "
         "running text that every character up to there accounts for. The "
         "first hundred characters carry 41.8 per cent of written Chinese, "
         "the first thousand carry 89.1, and the first 2,500 carry 98.5.")

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
.bar2 input[type=range] { width:260px; accent-color:var(--accent); }
.bar2 input[type=search] { font:inherit; font-size:12.5px; padding:4px 10px;
  border-radius:999px; border:1px solid var(--line); background:#151515;
  color:var(--text); width:170px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
.col { flex:1 1 620px; min-width:0; }
#curve svg { width:100%; height:auto; display:block; }
#grid { margin-top:14px; display:flex; flex-wrap:wrap; gap:4px; }
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
.t.on { border-color:#fff; background:#222c38; }
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
.method { color:var(--muted); font-size:12.5px; margin-top:14px;
  max-width:760px; }
.method summary { cursor:pointer; color:var(--accent); }
.method p { margin:9px 0 0; }
.refs { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.refs p { margin:0 0 8px; overflow-wrap:anywhere; }
.refs a { color:var(--accent); }
__APACSS__
h2.refh { font-size:15px; margin:26px 0 8px; }
@media (max-width:900px){ .stage{flex-direction:column;}
  .side{position:static; width:100%; flex:none;} }
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
  <label id="rankWrap">First <input type="range" id="rank" min="1" max="1200"
  value="1200"> <span id="rankTxt"></span></label>
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
<p class="note" style="border-top:none; padding-top:0;">__NOTE2__</p>
<div class="method"><details><summary>Where the counts come from</summary>
<p>__METHOD__</p><p>__GAPNOTE__</p></details></div>
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</div>
<script>
const D=__DATA__;
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const fmt=n=>n.toLocaleString('en-US');
let view='char', cut=1200, hot=null, firstI=1;

// [glyph, pinyin, gloss, share of text, cumulative share, ...]
const CH=D.chars, WD=D.words;
function rows(){ return view==='word'?WD:CH; }
function curves(){
  if(view==='word') return [{p:D.wcurve,c:'#e0a458',l:'words, subtitles'}];
  if(view==='both') return [
    {p:D.ccurve,c:'#58a6ff',l:'characters, written'},
    {p:D.scurve,c:'#7ee081',l:'characters, spoken'}];
  return [{p:D.ccurve,c:'#58a6ff',l:'characters, written'}];
}

const W=760, H=250, ML=44, MR=14, MT=12, MB=30;
const lg=Math.log10;
function drawCurve(){
  const cs=curves();
  const maxr=Math.max(...cs.map(c=>c.p[c.p.length-1][0]));
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
    s+='<path fill="none" stroke="'+c.c+'" stroke-width="2" d="'
      +c.p.map((q,i)=>(i?'L':'M')+X(q[0]).toFixed(1)+' '+Y(q[1]).toFixed(1))
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
  let ly=MT+14;
  for(const c of cs){
    s+='<text x="'+(ML+10)+'" y="'+ly+'" font-size="11.5" fill="'+c.c+'">'
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

function drawGrid(){
  const g=document.getElementById('grid');
  const q=document.getElementById('q').value.trim().toLowerCase();
  const keep=x=>!q || x.r[0].indexOf(q)>=0
    || x.r[1].toLowerCase().indexOf(q)>=0
    || x.r[2].toLowerCase().indexOf(q)>=0;
  const tile=x=>'<div class="t'+(view==='word'?' w':'')
    +(view!=='both'&&x.i>cut?' past':'')+'" data-i="'+x.i+'">'
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
  g.querySelectorAll('.t').forEach(e=>{
    e.addEventListener('pointerenter',()=>sel(+e.dataset.i));
    e.addEventListener('click',()=>sel(+e.dataset.i));
  });
}

function sel(i){
  hot=i;
  document.querySelectorAll('#grid .t').forEach(e=>
    e.classList.toggle('on', +e.dataset.i===i));
  const r=rows()[i-1];
  if(!r) return;
  document.getElementById('kindTxt').textContent = view==='both'
    ? 'Character, written rank '+fmt(i)
    : (view==='word'?'Word':'Character')+' number '+fmt(i);
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

function setRank(v){
  cut=v;
  const cov=at(curves()[0].p,cut);
  document.getElementById('rankTxt').textContent =
    fmt(cut)+' cover '+cov.toFixed(1)+'% of running '
      +(view==='word'?'dialogue':'text');
  drawCurve(); drawGrid(); if(hot) sel(hot);
}

function pick(v){
  view=v; hot=null;
  for(const [k,id] of [['char','vChar'],['word','vWord'],['both','vBoth']])
    document.getElementById(id).classList.toggle('on', k===v);
  const sl=document.getElementById('rank');
  document.getElementById('rankWrap').hidden = (v==='both');
  sl.max=rows().length; if(cut>rows().length) cut=rows().length;
  sl.value=cut;
  setRank(cut);
  sel(firstI);
}
document.getElementById('vChar').addEventListener('click',()=>pick('char'));
document.getElementById('vWord').addEventListener('click',()=>pick('word'));
document.getElementById('vBoth').addEventListener('click',()=>pick('both'));
document.getElementById('rank').addEventListener('input',e=>
  setRank(+e.target.value));
document.getElementById('q').addEventListener('input',drawGrid);
pick('char');
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
