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
         "dozen hieroglyphs and used each for the first sound of its name. "
         "The first view is that family tree on a line of time; each script "
         "answers under the pointer.")

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
.legend span::before { content:""; display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:6px; background:var(--c); vertical-align:-1px; }
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
  <nav class="site"><a href="library.html">&larr; Library &middot; Abstractions</a><a href="numbers.html">Numbers</a><a href="languages.html">Languages</a><a href="chinese.html">The Most Used Chinese</a></nav>
</header>
<h1>Writing</h1>
<div class="bar" id="views"><button data-v="tree" class="on">The scripts</button><button data-v="letters">Five letters</button><button data-v="counts">The signs</button></div>
<div class="legend" id="legend"></div>
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
const TYPES=__TYPES__, SCRIPTS=__SCRIPTS__, LETTERS=__LETTERS__, COUNTS=__COUNTS__;
const W=980;
const el=document.getElementById('diagram');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const fmt=n=>n.toLocaleString('en-US');
const yr=y=>y<0?(-y)+' BC':y+' AD';
let view='tree', hot=null;

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
function showTree(){ const roots=SCRIPTS.filter(s=>!s.p); card('The scripts','Where writing came from',[['scripts drawn',SCRIPTS.length],['invented from nothing',roots.length+' of them: '+roots.map(r=>r.n).join(', ')],['from the Egyptian signs',descendants('hieroglyphs')+' of the rest'],['still in use',SCRIPTS.filter(s=>s.alive).length]],'Each dot is a script at the date of its first surviving inscription, joined by a line to the script it was made from; a filled dot is still written. The colour is the kind of system it is.','Daniels & Bright 1996; Wikipedia, History of writing'); }
function showStage(lk,i){ const L=LETTERS.find(x=>x.k===lk), st=L.stages[i]; card(st.n+', '+(i===0?'by ':'')+yr(st.y), esc(st.name), [['the letter',L.L],['stage',(i+1)+' of 5']], st.b+(i===1?' Each Canaanite letter was named for the thing it drew and stood for the first sound of that name.':''), 'Wikipedia, Proto-Sinaitic script; Wikipedia, '+(i<2?'Egyptian hieroglyphs':i===2?'Phoenician alphabet':i===3?'Greek alphabet':'Latin alphabet')); }
function showLetter(lk){ const L=LETTERS.find(x=>x.k===lk); card('A letter', L.L+', '+L.thing, [['began as',L.stages[0].name],['named',L.stages[1].name.split(',')[0]+' in Canaanite, '+L.stages[2].name+' in Phoenician, '+L.stages[3].name+' in Greek'],['sound',L.k==='a'||L.k==='o'?'a consonant Greek lacked, so the Greeks made it a vowel':'the same sound all the way']], 'The picture became a letter by standing for the first sound of its name, and then kept being copied, turned, and simplified for three thousand years.', 'Wikipedia, Proto-Sinaitic script'); }
function showLetters(){ card('Five letters','From picture to alphabet',[['the pictures','an ox, a house, water, a snake, an eye'],['the letters','A, B, M, N, O'],['the time','about 3,800 years, from the turquoise mines of Sinai to this page']],'Each row follows one sign left to right through five stages; each cell answers under the pointer.','Wikipedia, Proto-Sinaitic script'); }
function showCount(k){ const c=COUNTS.find(x=>x.k===k); card(TYPES[c.t].n, esc(c.n), [['signs','about '+fmt(c.signs)],['the kind',TYPES[c.t].b]], c.b, c.s); }
function showCounts(){ card('The signs','How many a reader has to learn',[['alphabets and abjads','two or three dozen'],['syllabaries','fifty to several hundred'],['scripts that write words','hundreds to thousands, and tens of thousands exist']],'Each bar is one script\\u2019s basic inventory on a log scale, coloured by its kind.','Wikipedia, Writing system'); }

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
  const h=T.y+20+n*T.lane+40; const fam=hot?family(hot):null;
  for(const y of [-3000,-2000,-1000,0,1000,2000]){ const x=TX(y); s+='<line x1="'+x.toFixed(1)+'" y1="'+T.y+'" x2="'+x.toFixed(1)+'" y2="'+(h-34)+'" stroke="#2b2b2b"/><text x="'+x.toFixed(1)+'" y="'+(h-18)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+(y===0?'AD 1':yr(y))+'</text>'; }
  // the lines of descent
  const edges=[];
  for(const c of SCRIPTS){ if(!c.p) continue; const a=pos[c.p], b=pos[c.k]; const x1=a.x, y1=LY(a.lane), x2=b.x, y2=LY(b.lane); const on=fam&&fam.has(c.k)&&fam.has(c.p);
    edges.push([on?1:0,'<path d="M'+x1.toFixed(1)+','+y1+' C'+((x1+x2)/2).toFixed(1)+','+y1+' '+((x1+x2)/2).toFixed(1)+','+y2+' '+x2.toFixed(1)+','+y2+'" fill="none" stroke="'+(on?'#e6e6e6':'#3d444d')+'" stroke-width="'+(on?1.8:1.2)+'" opacity="'+(fam&&!on?0.35:1)+'"'+(c.k==='brahmi'||c.k==='protosinaitic'?' stroke-dasharray="4 3"':'')+'/>']); }
  edges.sort((a,b)=>a[0]-b[0]); s+=edges.map(e=>e[1]).join('');
  for(const c of SCRIPTS){ const p=pos[c.k], x=p.x, y=LY(p.lane), col=TYPES[c.t].c, on=hot===c.k, dim=fam&&!fam.has(c.k);
    s+='<g data-script="'+c.k+'" style="cursor:pointer" opacity="'+(dim?0.4:1)+'"><circle cx="'+x.toFixed(1)+'" cy="'+y+'" r="'+(on?7:5.5)+'" fill="'+(c.alive?col:'#121212')+'" stroke="'+(on?'#ffffff':col)+'" stroke-width="2"/>';
    s+='<text x="'+(x+10).toFixed(1)+'" y="'+(y+4)+'" font-size="11.5" fill="'+(on?'#ffffff':'#c8c8c8')+'"'+(c.p?'':' font-weight="700"')+' stroke="#121212" stroke-width="4" paint-order="stroke" stroke-linejoin="round">'+esc(c.n)+'</text></g>'; }
  s+='<text x="'+T.x+'" y="'+(T.y-14)+'" font-size="11" fill="#9a9a9a">a filled dot is still written; a name in bold was invented from nothing; a dashed line is a disputed descent</text>';
  return {svg:s, h}; }

/* ---- five letters ---- */
function lettersView(){ const x0=120, y0=70, cw=160, ch=100, box=64; let s='';
  const heads=['Egyptian sign','Proto-Sinaitic','Phoenician','Greek','Latin'];
  heads.forEach((hd,i)=>{ const x=x0+i*cw+cw/2; s+='<text x="'+x+'" y="'+(y0-36)+'" text-anchor="middle" font-size="12" font-weight="700" fill="#e6e6e6">'+hd+'</text><text x="'+x+'" y="'+(y0-20)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+(i===0?'by 2000 BC':yr(LETTERS[0].stages[i].y))+'</text>'; if(i) s+='<text x="'+(x0+i*cw)+'" y="'+(y0-28)+'" text-anchor="middle" font-size="14" fill="#3d444d">\\u2192</text>'; });
  LETTERS.forEach((L,r)=>{ const y=y0+r*ch; s+='<g data-letter="'+L.k+'" style="cursor:pointer"><text x="'+(x0-40)+'" y="'+(y+ch/2+10)+'" text-anchor="middle" font-size="28" font-weight="700" fill="'+(hot===L.k?'#ffffff':'#58a6ff')+'">'+L.L+'</text><text x="'+(x0-40)+'" y="'+(y+ch/2+28)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+L.thing+'</text></g>';
    L.stages.forEach((st,i)=>{ const cx=x0+i*cw+cw/2, cy=y+ch/2, k=L.k+':'+i, on=hot===k; const sc=box/60;
      s+='<g data-cell="'+k+'" style="cursor:pointer"><rect x="'+(cx-box/2-8)+'" y="'+(cy-box/2-4)+'" width="'+(box+16)+'" height="'+(box+8)+'" rx="8" fill="'+(on?'#26303d':'#1a1a1a')+'" stroke="'+(on?'#58a6ff':'#2b2b2b')+'"/>';
      s+='<g transform="translate('+(cx-box/2)+','+(cy-box/2)+') scale('+sc.toFixed(3)+')"><path d="'+st.d+'" fill="none" stroke="'+(on?'#ffffff':'#e6e6e6')+'" stroke-width="'+(i<2?3.2:3.6)+'" stroke-linecap="round" stroke-linejoin="round"/></g>';
      s+='<text x="'+cx+'" y="'+(cy+box/2+18)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+esc(st.name.split(',')[0])+'</text></g>'; }); });
  return {svg:s, h:y0+LETTERS.length*ch+10}; }

/* ---- the signs ---- */
const C={x:190,y:30,w:720,bar:26,lo:10,hi:10000};
const CX=n=>C.x+Math.log10(n/C.lo)/Math.log10(C.hi/C.lo)*C.w;
function countsView(){ const rows=[...COUNTS].sort((a,b)=>b.signs-a.signs||a.n.localeCompare(b.n)); let s='';
  const h=C.y+rows.length*C.bar+50;
  for(const n of [10,100,1000,10000]){ const x=CX(n); s+='<line x1="'+x.toFixed(1)+'" y1="'+C.y+'" x2="'+x.toFixed(1)+'" y2="'+(C.y+rows.length*C.bar)+'" stroke="#2b2b2b"/><text x="'+x.toFixed(1)+'" y="'+(C.y+rows.length*C.bar+18)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+fmt(n)+'</text>'; }
  s+='<text x="'+(C.x+C.w/2)+'" y="'+(C.y+rows.length*C.bar+38)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">signs to learn, on a log scale</text>';
  rows.forEach((c,i)=>{ const y=C.y+i*C.bar, on=hot===c.k; s+='<g data-count="'+c.k+'" style="cursor:pointer"><rect x="'+C.x+'" y="'+(y+5)+'" width="'+(CX(c.signs)-C.x).toFixed(1)+'" height="'+(C.bar-10)+'" rx="3" fill="'+TYPES[c.t].c+'" opacity="'+(on?1:0.8)+'"/>';
    s+='<text x="'+(C.x-8)+'" y="'+(y+C.bar/2+4)+'" text-anchor="end" font-size="11.5" fill="'+(on?'#ffffff':'#c8c8c8')+'">'+esc(c.n)+'</text><text x="'+(CX(c.signs)+6).toFixed(1)+'" y="'+(y+C.bar/2+4)+'" font-size="10.5" fill="#9a9a9a">'+fmt(c.signs)+'</text></g>'; });
  return {svg:s, h}; }

/* ---- render and wiring ---- */
function legend(){ const keys=view==='letters'?[]:view==='tree'?Object.keys(TYPES):[...new Set(COUNTS.map(c=>c.t))]; document.getElementById('legend').innerHTML=keys.map(k=>'<span style="--c:'+TYPES[k].c+'">'+TYPES[k].n+'</span>').join(''); }
function render(){ const q=view==='tree'?treeView():view==='letters'?lettersView():countsView(); el.innerHTML='<svg viewBox="0 0 '+W+' '+q.h+'" xmlns="http://www.w3.org/2000/svg" id="wsvg"><rect width="'+W+'" height="'+q.h+'" fill="#121212"/>'+q.svg+'</svg>'; legend(); }
function home(){ if(view==='tree') showTree(); else if(view==='letters') showLetters(); else showCounts(); }
function setView(v){ view=v; hot=null; for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on',b.dataset.v===v); render(); home(); }
document.getElementById('views').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setView(b.dataset.v); });
el.addEventListener('pointerover',e=>{ const g=e.target.closest('[data-script],[data-cell],[data-letter],[data-count]'); if(!g) return;
  const k=g.getAttribute('data-script')||g.getAttribute('data-cell')||g.getAttribute('data-letter')||g.getAttribute('data-count'); if(k===hot) return; hot=k; render();
  if(g.hasAttribute('data-script')) showScript(k); else if(g.hasAttribute('data-cell')){ const [lk,i]=k.split(':'); showStage(lk,+i); } else if(g.hasAttribute('data-letter')) showLetter(k); else showCount(k); });
el.addEventListener('pointerleave',()=>{ if(hot){ hot=null; render(); home(); } });

render(); showTree();
window.__writing=(q)=>{ const {pos,n}=layout(); const o={view,hot,lanes:n,card:document.getElementById('numTxt').innerText,name:document.getElementById('nameTxt').innerText,body:document.getElementById('bodyTxt').innerText,
  dots:document.querySelectorAll('#wsvg g[data-script]').length, cells:document.querySelectorAll('#wsvg g[data-cell]').length, bars:document.querySelectorAll('#wsvg g[data-count]').length};
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
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(SCRIPTS)} scripts, {len(LETTERS)} letters, {len(COUNTS)} counts")
