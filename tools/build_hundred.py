#!/usr/bin/env python3
"""Generate scifi-hundred.html, the hundred most cited science fiction novels.

A ranked bar chart: each novel's bar is the share of the source lists it
was eligible for that named it, coloured by the language it was written
in. Hugo and Nebula wins come from the site's own award data, so the page
carries a second, independent signal beside the citation count. Hovering
a bar fills the card with the book's cover, from Open Library.

Data: tools/scifi_hundred.py (the ranking), tools/scifi_data.py (awards),
tools/scifi_covers.json (cover ids).

Usage: python3 build_hundred.py
"""

import json
import re
import apa
from pathlib import Path

from scifi_hundred import BOOKS, LANGS, ORIGINAL
from scifi_data import AWARDS

HERE = Path(__file__).parent
ROOT = HERE.parent
COVERS = json.loads((HERE / "scifi_covers.json").read_text(encoding="utf-8"))


def norm(s):
    s = s.lower().replace("\u2019", "'")
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return re.sub(r"^(the|a|an) ", "", s)


def awards():
    out = {}
    for _y, title, _a, hugo, nebula in AWARDS:
        d = out.setdefault(norm(title), {})
        if hugo:
            d["h"] = hugo
        if nebula:
            d["n"] = nebula
    return out


AW = awards()

rows = []
for rank, title, author, year, pct, cited, elig, lang in BOOKS:
    d = {"r": rank, "n": title, "a": author, "y": year, "p": pct,
         "c": cited, "e": elig, "l": lang}
    a = AW.get(norm(title), {})
    if a.get("h"):
        d["hu"] = a["h"]
    if a.get("n"):
        d["ne"] = a["n"]
    if title in ORIGINAL:
        d["o"] = ORIGINAL[title]
    rows.append(d)

covers_js = json.dumps(
    {f"{b['n']}|{b['y']}": COVERS[f"{b['n']}|{b['y']}"]
     for b in rows if f"{b['n']}|{b['y']}" in COVERS},
    separators=(",", ":"))
books_js = json.dumps(rows, separators=(",", ":"), ensure_ascii=False)
langs_js = json.dumps(LANGS, separators=(",", ":"), ensure_ascii=False)

NOTE1 = ("Rank is the share of the source lists a novel was eligible for "
         "that named it, from the Classics of Science Fiction database, "
         "which counts appearances across best-of lists, polls, award "
         "rosters and retrospective anthologies. A book from 2013 cannot "
         "appear on a poll taken in 1988, so its denominator is smaller "
         "and the share, not the raw count, does the ranking.")

NOTE2 = ("Colour is the language the novel was written in, and ninety-five "
         "of the hundred were written in English. The sources are "
         "Anglophone, so the list measures what that world has kept "
         "reading rather than what the world wrote. Amber and violet pips "
         "mark a Hugo or a Nebula for best novel, an independent signal "
         "beside the count: forty of the hundred hold one.")

REFS = [
    ("https://classicsofsciencefiction.com/classics-of-science-fiction-list/by-rank/",
     "The ranking, and the citation counts behind it."),
    ("https://classicsofsciencefiction.com/essays/statistics-and-math/",
     "How a citation is counted, and why the denominator changes with the "
     "book."),
    ("https://classicsofsciencefiction.com/citations-bibliography/",
     "The lists, polls and anthologies the count is taken over."),
    ("https://www.thehugoawards.org/hugo-history/",
     "Hugo best novel winners, for the amber pips."),
    ("https://nebulas.sfwa.org/",
     "Nebula best novel winners, for the violet pips."),
    ("https://openlibrary.org", "The covers, fetched at view time."),
    ("https://en.wikipedia.org/wiki/Solaris_(novel)",
     "First published in Polish in 1961 and in English through a French "
     "translation in 1970."),
    ("https://en.wikipedia.org/wiki/We_(novel)",
     "Written in Russian in 1920 and 1921, published in English in 1924 and "
     "in Russian in 1952."),
]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>A Hundred Science Fiction Novels · Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; --hugo:#ffb02e; --neb:#b48cf2; }
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
h1 { margin:0 0 10px; font-size:26px; }
.bar { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-bottom:10px; }
.bar input { background:#0d0d0d; color:var(--text); border:1px solid var(--line);
  border-radius:999px; padding:7px 14px; font-size:13.5px; width:220px; }
.bar input:focus { outline:none; border-color:var(--accent); }
button { font:inherit; font-size:13.5px; padding:6px 14px; border-radius:999px;
  border:1px solid var(--line); background:#1a1a1a; color:var(--text); cursor:pointer; }
button:hover { border-color:var(--accent); }
button.on { background:var(--accent); border-color:var(--accent); color:#0b0b0b; }
#legend { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:10px;
  color:var(--muted); font-size:12px; align-items:center; }
#legend span { display:flex; gap:5px; align-items:center; cursor:pointer; }
#legend span.off { opacity:0.35; }
#legend i { width:9px; height:9px; border-radius:2px; display:inline-block; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#chart { flex:1 1 640px; min-width:0; max-height:78vh; overflow-y:auto;
  border:1px solid var(--line); border-radius:12px; background:#151515; }
#chart svg { width:100%; height:auto; display:block; user-select:none; }
.side { flex:0 0 300px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:16px; }
#cover { width:100%; height:250px; object-fit:contain; border-radius:8px;
  border:1px solid var(--line); margin-bottom:10px; display:none;
  background:#0d0d0d; }
#rankTxt { color:var(--muted); font-size:11.5px; letter-spacing:.09em;
  text-transform:uppercase; }
#bookTxt { font-weight:700; font-size:17px; margin:2px 0 2px; }
#authTxt { color:var(--muted); font-size:13.5px; }
#shareTxt { font-size:13.5px; margin-top:10px; }
#awTxt { font-size:13px; margin-top:6px; }
#origTxt { color:var(--muted); font-size:12.5px; margin-top:10px;
  border-top:1px solid var(--line); padding-top:8px; }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
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
  <nav class="site"><a href="science-fiction.html">&larr; Science Fiction</a><a href="scifi-canon.html">A Canon of Science Fiction</a><a href="hugo-nebula.html">Hugo and Nebula Winners</a></nav>
</header>
<h1>A Hundred Science Fiction Novels</h1>
<div class="bar">
  <input id="q" type="search" placeholder="Find a book or author" autocomplete="off">
  <button id="bRank" class="on">By rank</button>
  <button id="bYear">By year</button>
  <button id="bAward">Hugo or Nebula only</button>
</div>
<div id="legend"></div>
<div class="stage">
  <div id="chart"></div>
  <div class="side"><div class="card">
    <img id="cover" alt="">
    <div id="rankTxt"></div>
    <div id="bookTxt">A book under the cursor lands here</div>
    <div id="authTxt"></div>
    <div id="shareTxt"></div>
    <div id="awTxt"></div>
    <div id="origTxt"></div>
  </div></div>
</div>
<p class="note">__NOTE1__</p>
<p class="note" style="border-top:none; padding-top:0;">__NOTE2__</p>
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</div>
<script>
const BOOKS=__BOOKS__, LANGS=__LANGS__, COVERS=__COVERS__;
const el=document.getElementById('chart');
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
const fold=s=>s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();

const off=new Set();            // languages switched off in the legend
let sort='rank', awardOnly=false, query='', cur=0;

document.getElementById('legend').innerHTML=
  Object.entries(LANGS).map(([k,v])=>
    '<span data-l="'+k+'"><i style="background:'+v[1]+'"></i>'+v[0]+' '
    +BOOKS.filter(b=>b.l===k).length+'</span>').join('')
  +'<span style="cursor:default"><i style="background:var(--hugo)"></i>Hugo</span>'
  +'<span style="cursor:default"><i style="background:var(--neb)"></i>Nebula</span>';
document.getElementById('legend').addEventListener('click',e=>{
  const s=e.target.closest('[data-l]'); if(!s) return;
  const k=s.getAttribute('data-l');
  if(off.has(k)) off.delete(k); else off.add(k);
  s.classList.toggle('off',off.has(k));
  render();
});

function shown(){
  let out=BOOKS.filter(b=>!off.has(b.l));
  if(awardOnly) out=out.filter(b=>b.hu||b.ne);
  if(query.length>1) out=out.filter(b=>fold(b.n).includes(query)
    ||fold(b.a).includes(query));
  return sort==='year' ? out.slice().sort((a,b)=>a.y-b.y||a.r-b.r) : out;
}

const W=1000, RS=24, PADT=14, PADB=14, LEFT=250, RIGHT=76;
function render(){
  const list=shown();
  const H=PADT+PADB+RS*Math.max(1,list.length);
  const full=W-LEFT-RIGHT;
  let s='<svg viewBox="0 0 '+W+' '+H+'" xmlns="http://www.w3.org/2000/svg" id="csvg">';
  // the axis: a line every 25 per cent
  for(let p=25;p<=100;p+=25){
    const x=LEFT+full*p/100;
    s+='<path d="M'+x+','+PADT+' V'+(H-PADB)+'" stroke="#242424" stroke-width="1"/>';
  }
  list.forEach((b,i)=>{
    const y=PADT+RS*i, mid=y+RS/2;
    const col=LANGS[b.l][1], w=full*b.p/100;
    s+='<g data-i="'+BOOKS.indexOf(b)+'" style="cursor:pointer">'
      +'<rect x="0" y="'+y+'" width="'+W+'" height="'+RS+'" fill="'
      +(BOOKS.indexOf(b)===cur?'#1d2126':'transparent')+'"/>'
      +'<text x="30" y="'+(mid+4)+'" text-anchor="end" font-size="11" '
      +'fill="#6b7280">'+b.r+'</text>'
      +'<text x="38" y="'+(mid+4)+'" font-size="12.5" fill="#e6e6e6">'
      +esc(b.n.length>30?b.n.slice(0,29)+'\\u2026':b.n)+'</text>'
      +'<text x="'+(LEFT-8)+'" y="'+(mid+4)+'" text-anchor="end" font-size="11" '
      +'fill="#6b7280">'+b.y+'</text>'
      +'<rect x="'+LEFT+'" y="'+(y+5)+'" width="'+w.toFixed(1)+'" height="'
      +(RS-10)+'" rx="2" fill="'+col+'" fill-opacity="0.85"/>'
      +'<text x="'+(LEFT+w+7).toFixed(1)+'" y="'+(mid+4)+'" font-size="11" '
      +'fill="#9a9a9a">'+b.p+'%</text>';
    let px=LEFT+w+34;
    if(b.hu){ s+='<circle cx="'+px+'" cy="'+mid+'" r="3.6" fill="var(--hugo)"/>'; px+=10; }
    if(b.ne){ s+='<circle cx="'+px+'" cy="'+mid+'" r="3.6" fill="var(--neb)"/>'; }
    s+='</g>';
  });
  if(!list.length)
    s+='<text x="'+LEFT+'" y="40" font-size="13" fill="#9a9a9a">nothing left '
      +'under those filters</text>';
  s+='</svg>';
  el.innerHTML=s;
}

const cache={};
async function coverFor(b){
  const k=b.n+'|'+b.y;
  if(k in COVERS && COVERS[k])
    return 'https://covers.openlibrary.org/b/id/'+COVERS[k]+'-L.jpg';
  if(k in cache) return cache[k];
  try{
    const q='https://openlibrary.org/search.json?limit=8&fields=cover_i,first_publish_year,title'
      +'&title='+encodeURIComponent(b.n)
      +'&author='+encodeURIComponent(b.a.split(' and ')[0]);
    const j=await (await fetch(q)).json();
    let best=null;
    for(const d of (j.docs||[])){
      if(!d.cover_i) continue;
      if(d.first_publish_year && Math.abs(d.first_publish_year-b.y)<=3){ best=d; break; }
      if(!best) best=d;
    }
    const u=best?('https://covers.openlibrary.org/b/id/'+best.cover_i+'-L.jpg'):null;
    cache[k]=u; return u;
  }catch(e){ cache[k]=null; return null; }
}

async function show(i){
  const b=BOOKS[i]; if(!b) return;
  cur=i; render();
  document.getElementById('rankTxt').textContent=
    'No. '+b.r+' \\u00b7 '+LANGS[b.l][0];
  document.getElementById('bookTxt').textContent=b.n;
  document.getElementById('authTxt').textContent=b.a+', '+b.y;
  document.getElementById('shareTxt').textContent=
    'Named by '+b.c+' of the '+b.e+' lists it could have been on, '+b.p+' per cent.';
  const aw=[];
  if(b.hu) aw.push('Hugo '+b.hu);
  if(b.ne) aw.push('Nebula '+b.ne);
  const a=document.getElementById('awTxt');
  a.textContent=aw.length?aw.join(' \\u00b7 '):'No Hugo or Nebula for best novel.';
  a.style.color=aw.length?'var(--hugo)':'var(--muted)';
  document.getElementById('origTxt').textContent=b.o||'';
  const img=document.getElementById('cover');
  img.style.display='none'; img.removeAttribute('src');
  img.onerror=()=>{ img.style.display='none'; };
  const u=await coverFor(b);
  if(cur!==i) return;
  if(u){ img.src=u; img.style.display='block'; }
}

el.addEventListener('pointerover',e=>{
  const g=e.target.closest('[data-i]');
  if(g) show(+g.getAttribute('data-i'));
});
document.getElementById('q').addEventListener('input',e=>{
  query=fold(e.target.value.trim()); render(); el.scrollTop=0;
});
function mode(m){
  sort=m;
  document.getElementById('bRank').classList.toggle('on',m==='rank');
  document.getElementById('bYear').classList.toggle('on',m==='year');
  render(); el.scrollTop=0;
}
document.getElementById('bRank').onclick=()=>mode('rank');
document.getElementById('bYear').onclick=()=>mode('year');
document.getElementById('bAward').onclick=e=>{
  awardOnly=!awardOnly; e.target.classList.toggle('on',awardOnly);
  render(); el.scrollTop=0;
};

render();
show(0);
window.__hundred=()=>({books:BOOKS.length, rows:shown().length, sort,
  awardOnly, cur, langs:Object.keys(LANGS).length,
  english:BOOKS.filter(b=>b.l==='en').length,
  awarded:BOOKS.filter(b=>b.hu||b.ne).length,
  ranked:BOOKS.every((b,i)=>b.r===i+1),
  ordered:BOOKS.every((b,i)=>!i||b.p<=BOOKS[i-1].p)});
</script>
</body>
</html>
"""

ENGLISH = sum(1 for b in rows if b["l"] == "en")
AWARDED = sum(1 for b in rows if b.get("hu") or b.get("ne"))
assert (ENGLISH, AWARDED) == (95, 40), (
    f"the note says ninety-five English and forty awarded; the data says "
    f"{ENGLISH} and {AWARDED}")

html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__BOOKS__", books_js).replace("__LANGS__", langs_js)
        .replace("__COVERS__", covers_js)
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2)
        .replace("__REFS__", apa.render([apa.auto(u, a) for u, a in REFS])))
out = ROOT / "scifi-hundred.html"
out.write_text(html, encoding="utf-8")
print(f"wrote {out} ({len(html):,} B): {len(rows)} books, "
      f"{sum(1 for b in rows if b.get('hu') or b.get('ne'))} with a Hugo or "
      f"Nebula, {sum(1 for b in rows if b['l'] != 'en')} not in English, "
      f"{len(json.loads(covers_js))} covers baked in")
