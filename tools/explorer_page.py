"""Shared page template for the Altazor chess explorers.

render_page(config, nodes) -> html string.

Node fields: l line, g weight (games or pct share), a pct of all,
n name, par parent index (-1 root child), b 64-char board, c fill color.
Config: title, heading, lede, note, mode ('games'|'pct'),
total (weight denominator at virtual root), rootLabel, rootSub,
rootBoard, rootStat, startCrumb, legend [{i,label,color,right}], out.
"""

import json

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
.wrap { max-width:1200px; margin:0 auto; padding:32px 20px 60px; }
header.site { border-top:4px solid var(--accent); padding-top:22px; margin-bottom:26px;
  display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }
.brand { font-weight:700; font-size:20px; letter-spacing:.1em; text-decoration:none; color:var(--text); }
.brand:hover { color:var(--accent); }
nav.site a { color:var(--muted); text-decoration:none; font-size:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 6px; font-size:26px; }
.lede { color:var(--muted); font-size:14.5px; margin:0 0 20px; max-width:720px; }
.stage { display:flex; gap:24px; align-items:flex-start; flex-wrap:wrap; }
#sun { flex:1 1 520px; max-width:760px; }
#sun svg { width:100%; height:auto; display:block; cursor:pointer; }
.side { flex:1 1 280px; max-width:380px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:16px; margin-bottom:16px; }
#board { width:100%; height:auto; display:block; border-radius:6px; }
#lineTxt { font-weight:700; margin:12px 0 2px; font-size:15px; }
#nameTxt { color:var(--accent); font-size:13.5px; min-height:1.2em; }
#statTxt { color:var(--muted); font-size:13px; margin-top:6px; }
.legend { display:flex; flex-direction:column; gap:8px; }
.lgi { display:flex; align-items:center; gap:9px; font-size:13.5px; cursor:pointer;
  color:var(--muted); }
.lgi:hover { color:var(--text); }
.lgi span.sw { width:13px; height:13px; border-radius:3px; display:inline-block; flex:none; }
.crumbs { font-size:13px; color:var(--muted); margin-bottom:14px; }
.crumbs a { color:var(--accent); text-decoration:none; cursor:pointer; }
.note { color:var(--muted); font-size:12.5px; margin-top:22px; max-width:720px;
  border-top:1px solid var(--line); padding-top:12px; }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="chess.html">&larr; Chess</a></nav>
</header>
<h1>__HEADING__</h1>
<div class="stage">
  <div id="sun"></div>
  <div class="side">
    <div class="card">
      <svg id="board" viewBox="0 0 8 8"></svg>
      <div id="lineTxt"></div>
      <div id="nameTxt"></div>
      <div id="statTxt"></div>
    </div>
    <div class="card">
      <div class="crumbs" id="crumbs"></div>
      <div class="legend" id="legend"></div>
    </div>
  </div>
</div>
<p class="note">__LEDE__</p>
<p class="note">__NOTE__</p>
</div>
<script>
const DATA = __DATA__;
const CFG = __CFG__;
const BG = '#121212';

DATA.forEach((d,i)=>{ d.i=i; d.kids=[]; });
DATA.forEach(d=>{ if(d.par>=0) DATA[d.par].kids.push(d.i); });
DATA.forEach(d=>{ d.kids.sort((x,y)=>DATA[y].g-DATA[x].g); });
const ROOTKIDS = DATA.map((d,i)=>i).filter(i=>DATA[i].par<0).sort((x,y)=>DATA[y].g-DATA[x].g);
const fmt = n => Math.round(n).toLocaleString('en-US');

const GLYPH = {K:'\\u265A',Q:'\\u265B',R:'\\u265C',B:'\\u265D',N:'\\u265E',P:'\\u265F'};
function drawBoard(b){
  let s='';
  for(let r=0;r<8;r++) for(let c=0;c<8;c++){
    s+=`<rect x="${c}" y="${r}" width="1" height="1" fill="${(r+c)%2?'#8a6a4f':'#c9ab8a'}"/>`;
  }
  for(let r=0;r<8;r++) for(let c=0;c<8;c++){
    const p=b[r*8+c]; if(p==='.') continue;
    const white = p===p.toUpperCase();
    s+=`<text x="${c+0.5}" y="${r+0.86}" text-anchor="middle" font-size="0.9"
      fill="${white?'#f7f3ec':'#141210'}" stroke="${white?'#3a3a3a':'#c9ab8a'}"
      stroke-width="0.022">${GLYPH[p.toUpperCase()]}</text>`;
  }
  document.getElementById('board').innerHTML = s;
}

const R0=88, RW=74, RINGS=4, CX=420, CY=420, SZ=840, GAP=0.004;
let root=-1, hover=-1;

function tok(d){ return d.l.split(' ').pop(); }
function visibleWeight(){ return root<0 ? CFG.total : DATA[root].g; }
function arcPath(r0,r1,a0,a1){
  const p=(r,a)=>[CX+r*Math.sin(a), CY-r*Math.cos(a)];
  const large=(a1-a0)>Math.PI?1:0;
  const [x0,y0]=p(r0,a0),[x1,y1]=p(r1,a0),[x2,y2]=p(r1,a1),[x3,y3]=p(r0,a1);
  return `M${x1.toFixed(1)},${y1.toFixed(1)}A${r1},${r1} 0 ${large} 1 ${x2.toFixed(1)},${y2.toFixed(1)}`+
         `L${x3.toFixed(1)},${y3.toFixed(1)}A${r0},${r0} 0 ${large} 0 ${x0.toFixed(1)},${y0.toFixed(1)}Z`;
}
function layout(){
  const segs=[], denom=visibleWeight();
  const kids0 = root<0 ? ROOTKIDS : DATA[root].kids;
  function place(ids, a0, span, depth, parentW){
    if(depth>RINGS) return;
    let a=a0;
    for(const id of ids){
      const d=DATA[id];
      const s=span*d.g/parentW;
      if(s>0.006){
        segs.push({id, depth, a0:a, a1:a+s});
        place(d.kids, a, s, depth+1, d.g);
      }
      a+=s;
    }
  }
  place(kids0, 0, 2*Math.PI, 1, denom);
  return segs;
}
function pathSet(){
  const set=new Set();
  if(hover>=0){ let n=DATA[hover]; while(true){ set.add(n.i); if(n.par<0||n.i===root) break; n=DATA[n.par]; } }
  return set;
}
function render(){
  const segs=layout();
  let s=`<svg viewBox="0 0 ${SZ} ${SZ}" xmlns="http://www.w3.org/2000/svg">`;
  s+=`<rect width="${SZ}" height="${SZ}" fill="${BG}"/>`;
  const hp=pathSet();
  for(const g of segs){
    const d=DATA[g.id];
    const r0=R0+(g.depth-1)*RW, r1=r0+RW-3;
    const dim = hover>=0 && !hp.has(g.id);
    s+=`<path d="${arcPath(r0,r1,g.a0+GAP,g.a1-GAP)}" fill="${d.c}"
       opacity="${dim?0.35:1}" data-id="${g.id}"/>`;
    const span=g.a1-g.a0;
    if(span>0.10){
      const mid=(g.a0+g.a1)/2, rm=(r0+r1)/2;
      const x=CX+rm*Math.sin(mid), y=CY-rm*Math.cos(mid);
      const fs=Math.min(19, 8+span*26);
      s+=`<text x="${x.toFixed(1)}" y="${y.toFixed(1)}" text-anchor="middle"
        font-size="${fs.toFixed(1)}" font-weight="700" fill="#fff" pointer-events="none">${tok(d)}</text>`;
      if(span>0.22 && d.n) s+=`<text x="${x.toFixed(1)}" y="${(y+15).toFixed(1)}" text-anchor="middle"
        font-size="${(fs*0.62).toFixed(1)}" font-style="italic" fill="#fff" opacity="0.85"
        pointer-events="none">${d.n}</text>`;
    }
  }
  s+=`<circle cx="${CX}" cy="${CY}" r="${R0-6}" fill="#1a1a1a" stroke="#2b2b2b" data-center="1"/>`;
  const cl = root<0 ? CFG.rootLabel : tok(DATA[root]);
  const cn = root<0 ? CFG.rootSub : (DATA[root].n||'');
  s+=`<text x="${CX}" y="${CY-4}" text-anchor="middle" font-size="21" font-weight="700"
     fill="#e6e6e6" pointer-events="none">${cl}</text>`;
  s+=`<text x="${CX}" y="${CY+18}" text-anchor="middle" font-size="12" font-style="italic"
     fill="#9a9a9a" pointer-events="none">${cn}</text>`;
  s+='</svg>';
  document.getElementById('sun').innerHTML=s;
  drawCrumbs();

  const svg=document.querySelector('#sun svg');
  svg.addEventListener('pointerover',e=>{
    if(e.target.getAttribute('data-center')!==null){
      hover=-1; paintHover(); showRoot(); return;
    }
    const id=e.target.getAttribute('data-id');
    if(id!==null){ hover=+id; paintHover(); showNode(DATA[+id]); }
  });
  svg.addEventListener('pointerleave',()=>{ hover=-1; paintHover(); showRoot(); });
  svg.addEventListener('click',e=>{
    if(e.target.getAttribute('data-center')!==null){
      if(root>=0){ root=DATA[root].par; hover=-1; render(); showRoot(); }
      return;
    }
    const id=e.target.getAttribute('data-id');
    if(id!==null && DATA[+id].kids.length){ root=+id; hover=-1; render(); showRoot(); }
  });
}
function paintHover(){
  const hp=pathSet();
  document.querySelectorAll('#sun path[data-id]').forEach(p=>{
    p.setAttribute('opacity', hover>=0 && !hp.has(+p.getAttribute('data-id')) ? 0.35 : 1);
  });
}
function showNode(d){
  drawBoard(d.b);
  document.getElementById('lineTxt').textContent=d.l;
  const nt=document.getElementById('nameTxt');
  nt.textContent=d.n||'';
  nt.style.color=d.c;
  const parW = d.par<0 ? CFG.total : DATA[d.par].g;
  const after = d.par<0 ? CFG.startCrumb : tok(DATA[d.par]);
  const share = `${(100*d.g/parW).toFixed(1)}% after ${after}`;
  document.getElementById('statTxt').textContent = CFG.mode==='games'
    ? `${fmt(d.g)} games \\u00b7 ${d.a.toFixed(1)}% of all \\u00b7 ${share}`
    : `${d.a.toFixed(1)}% of ${CFG.allName} \\u00b7 ${share}`;
}
function showRoot(){
  if(root<0){ drawBoard(CFG.rootBoard);
    document.getElementById('lineTxt').textContent=CFG.rootLine;
    const nt=document.getElementById('nameTxt');
    nt.textContent=CFG.rootSub;
    nt.style.color='';
    document.getElementById('statTxt').textContent=CFG.rootStat;
  } else showNode(DATA[root]);
}
function drawCrumbs(){
  const el=document.getElementById('crumbs');
  const parts=[`<a data-r="-1">${CFG.startCrumb}</a>`];
  if(root>=0){
    const chain=[]; let n=DATA[root];
    while(true){ chain.unshift(n); if(n.par<0) break; n=DATA[n.par]; }
    for(const c of chain) parts.push(`<a data-r="${c.i}">${tok(c)}</a>`);
  }
  el.innerHTML=parts.join(' <span style="opacity:.5">/</span> ');
  el.querySelectorAll('a').forEach(a=>a.onclick=()=>{ root=+a.getAttribute('data-r'); hover=-1; render(); showRoot(); });
}
const lg=document.getElementById('legend');
for(const item of CFG.legend){
  const div=document.createElement('div'); div.className='lgi';
  div.innerHTML=`<span class="sw" style="background:${item.color}"></span>${item.label}`+
    `<span style="margin-left:auto">${item.right}</span>`;
  div.onclick=()=>{ root=item.i; hover=-1; render(); showRoot(); };
  lg.appendChild(div);
}
render(); showRoot();
</script>
</body>
</html>
"""


def render_page(config, nodes):
    data_json = json.dumps(
        [{k: nd[k] for k in ("l", "g", "a", "n", "par", "b", "c")} for nd in nodes],
        separators=(",", ":"),
    )
    cfg_json = json.dumps(
        {k: config[k] for k in ("mode", "total", "allName", "rootLabel", "rootSub",
                                "rootLine", "rootBoard", "rootStat", "startCrumb", "legend")},
        separators=(",", ":"),
    )
    return (
        TEMPLATE.replace("__TITLE__", config["title"])
        .replace("__HEADING__", config["heading"])
        .replace("__LEDE__", config["lede"])
        .replace("__NOTE__", config["note"])
        .replace("__DATA__", data_json)
        .replace("__CFG__", cfg_json)
    )
