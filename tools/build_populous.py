#!/usr/bin/env python3
"""Generate populous-countries.html, Earth's Population Right Now: every country
and area the United Nations counts, its share of world population, and how
many people are born and die in it per day.

Each row carries its own paired bars, births above deaths, on one scale shared
by every country, so the balance between the two is visible in place rather
than in a separate chart. One shared scale across 237 rows means most bars are
short: that is the point, and the figure beside each bar carries the value.

Figures live in world_data.py. See its docstring for the retrieval route.

Usage: python3 build_populous.py
"""

import sys
import apa
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from world_data import ROWS as SRC, WORLD, FLAG, NOT_SOVEREIGN  # noqa: E402

OUT = Path(__file__).parent.parent / "populous-countries.html"

SNAPSHOT = "August 20, 2026"

DAYS = 365.25
C_BIRTH = "#3987e5"   # categorical slot 1, dark step
C_DEATH = "#d55181"   # categorical slot 5, dark step
C_SHARE = "#8a93a3"   # neutral meter fill, not a series hue
C_GAP = "#0ca30c"     # delta text token, not a series hue


def per_day(annual):
    return round(annual / DAYS)


def commas(n):
    return f"{n:,}"


def day_txt(n):
    """A country can average less than one a day. Say so rather than zero."""
    return commas(n) if n else "&lt;1"


def pct_txt(s):
    if s >= 0.1:
        return f"{s:.1f}%"
    if s >= 0.01:
        return f"{s:.2f}%"
    return "&lt;0.01%"


rows = []
for code, name, pop, births, deaths in SRC:
    rows.append(dict(
        code=code, name=name, cc=FLAG[code], pop=pop,
        share=pop / WORLD["pop"] * 100,
        b=per_day(births), d=per_day(deaths),
        net=per_day(births) - per_day(deaths),
        by=births, dy=deaths,
    ))

# how many more people than the country one rank below; the last has none
for i, r in enumerate(rows):
    r["gap"] = r["pop"] - rows[i + 1]["pop"] if i + 1 < len(rows) else None

listed = sum(r["pop"] for r in rows)
share_listed = listed / WORLD["pop"] * 100
w_b, w_d = per_day(WORLD["births"]), per_day(WORLD["deaths"])
max_share = max(r["share"] for r in rows)
max_flow = max(max(r["b"], r["d"]) for r in rows)
shrinking = [r for r in rows if r["net"] < 0]
top10 = sum(r["pop"] for r in rows[:10]) / WORLD["pop"] * 100

# A day's births, deaths and net growth are each larger than whole countries.
# The comparison counts sovereign states, which is what a reader hears in
# "countries", rather than all 237 rows of the table, most of the smallest of
# which are dependencies and overseas departments.
SOV = sorted(r["pop"] for r in rows if r["code"] not in NOT_SOVEREIGN)
assert len(SOV) == 194, len(SOV)   # the 193 UN members and the Vatican


def smaller_than(n):
    return sum(1 for p in SOV if p < n)


n_b, n_d, n_g = (smaller_than(w_b), smaller_than(w_d),
                 smaller_than(w_b - w_d))

# ---- the paired bars that live inside each row ----
VW, PLOT = 250, 150      # viewBox width, bar plot width
BH, GAP = 10, 3          # bar height, gap between the pair
VH = 2 + BH + GAP + BH + 2


def flow_svg(r):
    parts = [f'<svg class="flow" viewBox="0 0 {VW} {VH}" xmlns="http://www.w3.org/2000/svg" '
             f'role="img" aria-label="{r["name"]}: {commas(r["b"])} births and '
             f'{commas(r["d"])} deaths per day">']
    for j, (val, color, label) in enumerate(
            ((r["b"], C_BIRTH, "births"), (r["d"], C_DEATH, "deaths"))):
        w = max(2.0, val / max_flow * PLOT)
        y = 2 + j * (BH + GAP)
        parts.append(
            f'<g><title>{commas(val)} {label} per day</title>'
            f'<rect x="0" y="{y}" width="{w:.1f}" height="{BH}" rx="3" fill="{color}"/>'
            f'<rect x="0" y="{y}" width="3" height="{BH}" fill="{color}"/></g>')
        parts.append(f'<text x="{w + 6:.1f}" y="{y + BH - 1.5}" font-size="10.5" '
                     f'fill="#c3c2b7" font-variant-numeric="tabular-nums">{day_txt(val)}</text>')
    parts.append('</svg>')
    return "".join(parts)


# every head sorts the table; births and deaths sort by the ratio of the two
HEAD = """<thead><tr>
  <th class="l" colspan="2"><button class="sort" data-k="name">Country or area</button></th>
  <th><button class="sort" data-k="pop" aria-pressed="true">Population</button></th>
  <th class="l"><button class="sort" data-k="pop">Share of world</button></th>
  <th class="l"><button class="sort" data-k="ratio">Births and deaths per day</button></th>
  <th><button class="sort" data-k="net">Net / day</button></th>
</tr></thead>"""


def tr(i, r):
    bar_w = r["share"] / max_share * 100
    net_txt = ("+" if r["net"] > 0 else "−" if r["net"] < 0 else "") + commas(abs(r["net"]))
    lead = (f' <span class="gap">(+{commas(r["gap"])})</span>'
            if r["gap"] is not None else "")
    return f"""<tr data-i="{i - 1}">
  <td class="rank">{i}</td>
  <td class="ct"><span class="cw"><img class="flag" src="https://flagcdn.com/w80/{r['cc']}.png"
      width="30" height="20" alt="" onerror="this.style.visibility='hidden'"><span>{r['name']}</span></span></td>
  <td class="num pop">{commas(r['pop'])}{lead}</td>
  <td class="share"><span class="track"><span class="fill" style="width:{bar_w:.1f}%"></span></span><span class="pct">{pct_txt(r['share'])}</span></td>
  <td class="flow">{flow_svg(r)}</td>
  <td class="num">{net_txt}</td>
</tr>"""


def totals(label, block):
    p = sum(r["pop"] for r in block)
    b = sum(r["b"] for r in block)
    d = sum(r["d"] for r in block)
    n = b - d
    sign = "+" if n > 0 else "−"
    return (f'<tr class="total"><td></td><td>{label}</td>'
            f'<td class="num">{commas(p)}</td>'
            f'<td>{p / WORLD["pop"] * 100:.2f}% of the world</td>'
            f'<td>{commas(b)} births, {commas(d)} deaths</td>'
            f'<td class="num">{sign}{commas(abs(n))}</td></tr>')


body = "\n".join(tr(i + 1, r) for i, r in enumerate(rows))
table_all = (f'<div class="tscroll"><table id="tbl">\n{HEAD}\n<tbody>\n{body}\n'
             f'{totals("All " + str(len(rows)) + " together", rows)}\n'
             f'</tbody>\n</table></div>')

import json  # noqa: E402

# the page's script: the counters, the live card, the sorting, the areas
SCRIPT = r"""const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const $=id=>document.getElementById(id);
const fmt=n=>Math.floor(n).toLocaleString('en-US');
const SEC=365.25*86400;
const t0=performance.now();
const secs=()=>(performance.now()-t0)/1000;
const tbody=document.querySelector('#tbl tbody');
const TR=[...tbody.querySelectorAll('tr[data-i]')];
const TOTAL=tbody.querySelector('tr.total');
let hov=-1, pin=-1, home=-1;

/* ---- the counters: each place's average second, from the moment the page opened */
function ticks(){
  const s=secs(), W=D.world;
  $('tPop').textContent=fmt(W.pop+(W.by-W.dy)/SEC*s)+' now, counting the average second';
  $('tBirths').textContent=fmt(W.by/SEC*s)+' born since this page opened';
  $('tDeaths').textContent=fmt(W.dy/SEC*s)+' died since this page opened';
  $('tNet').textContent='+'+fmt((W.by-W.dy)/SEC*s)+' since this page opened';
}
function row(i){
  const r=D.rows[i], s=secs(), g=(r.by-r.dy)/SEC*s;
  return {r, born:r.by/SEC*s, died:r.dy/SEC*s, now:r.p+g};
}
function shareTxt(v){ return v>=0.1?v.toFixed(1)+'%':v>=0.01?v.toFixed(2)+'%':'under 0.01%'; }
function perSec(v){
  // a place with less than one a second is given the wait between them
  const x=v/SEC;
  if(x>=1) return x.toFixed(1)+' a second';
  const w=1/x;
  return w<60?'one every '+Math.round(w)+' s':w<3600?'one every '+Math.round(w/60)+' min'
    :w<86400?'one every '+(w/3600).toFixed(1)+' h':'one every '+Math.round(w/86400)+' days';
}
function card(){
  const i=pin>=0?pin:hov, c=$('card');
  let h='';
  if(i<0){
    const W=D.world, s=secs();
    h='<span class="nm">The world</span><span class="n">'+fmt(W.pop+(W.by-W.dy)/SEC*s)
      +'</span> people, counting the average second since this page opened: <span class="n b">'
      +fmt(W.by/SEC*s)+'</span> born and <span class="n d">'+fmt(W.dy/SEC*s)
      +'</span> died. A row or an area answers the pointer, and a click keeps it here.';
  } else {
    const q=row(i), r=q.r;
    h=(i===pin?'<span class="pin">pinned</span>':'')
      +'<span class="nm">'+r.n+'</span><span class="n">'+fmt(q.now)+'</span> people, '
      +shareTxt(r.s)+' of the world. Since this page opened: <span class="n b">'+fmt(q.born)
      +'</span> born, <span class="n d">'+fmt(q.died)+'</span> died. A birth '
      +perSec(r.by)+', a death '+perSec(r.dy)+'.';
  }
  if(home>=0 && home!==i){
    const H=D.rows[home], q=row(home), me=i<0?null:D.rows[i];
    let ratio='';
    if(me){
      const k=me.p/H.p, big=k>=1?me:H, small=k>=1?H:me, m=k>=1?k:1/k;
      ratio=' '+big.n+' has '+(m>=10?fmt(Math.round(m)):m.toFixed(1))
        +' times as many people as '+small.n+'.';
    }
    h+='<div class="cmp">Beside it, '+H.n+': '+fmt(q.now)+' people, '+shareTxt(H.s)
      +', '+fmt(q.born)+' born and '+fmt(q.died)+' died since the page opened.'+ratio+'</div>';
  }
  c.innerHTML=h;
}
let lastT=0;
function loop(now){
  if(now-lastT>120){ lastT=now; ticks(); card(); }
  requestAnimationFrame(loop);
}

/* ---- the rows answer the pointer; a click pins, a second click or Escape lets go */
function light(){
  TR.forEach(t=>{ const i=+t.dataset.i;
    t.classList.toggle('on', i===pin||(pin<0&&i===hov));
    t.classList.toggle('home', i===home); });
  document.querySelectorAll('#tree rect[data-i]').forEach(e=>{
    const i=+e.dataset.i, on=i===pin||(pin<0&&i===hov)||i===home;
    e.setAttribute('stroke',on?'#ffffff':'#121212');
    e.setAttribute('stroke-width',on?2:1);
  });
}
function hover(i){ if(i===hov) return; hov=i; light(); card(); }
function click(i){ pin=(pin===i)?-1:i; light(); card(); }
tbody.addEventListener('mouseover',e=>{ const t=e.target.closest('tr[data-i]'); if(t) hover(+t.dataset.i); });
tbody.addEventListener('mouseleave',()=>hover(-1));
tbody.addEventListener('click',e=>{ const t=e.target.closest('tr[data-i]'); if(t) click(+t.dataset.i); });
document.addEventListener('keydown',e=>{
  const tag=(e.target.tagName||'').toLowerCase();
  if(tag==='input'||tag==='select') return;
  if(e.key==='Escape'&&pin>=0){ pin=-1; light(); card(); }
});

/* ---- the chosen country stays in the card for comparison */
const sel=$('home');
[...D.rows.keys()].sort((a,b)=>D.rows[a].n.localeCompare(D.rows[b].n)).forEach(i=>{
  const o=document.createElement('option'); o.value=i; o.textContent=D.rows[i].n; sel.appendChild(o); });
sel.addEventListener('change',()=>{ home=+sel.value; light(); card(); });

/* ---- the heads sort the table, and the rows slide to their new places */
let sortK='pop', flip=false;
const KEY={
  name:(a,b)=>D.rows[a].n.localeCompare(D.rows[b].n),
  pop:(a,b)=>D.rows[b].p-D.rows[a].p,
  // deaths over births, the places that shrink without migration first
  ratio:(a,b)=>(D.rows[b].dy/D.rows[b].by)-(D.rows[a].dy/D.rows[a].by),
  net:(a,b)=>(D.rows[b].by-D.rows[b].dy)-(D.rows[a].by-D.rows[a].dy),
};
let slide=null;
// the name sort starts at A and every other at the largest; a second click
// on the same head turns the order round
function sortBy(k){
  if(k===sortK) flip=!flip; else { sortK=k; flip=false; }
  document.querySelectorAll('button.sort').forEach(b=>{
    b.setAttribute('aria-pressed', b.dataset.k===sortK);
    b.classList.toggle('up', b.dataset.k===sortK && flip); });
  const idx=TR.map(t=>+t.dataset.i).sort(KEY[k]);
  if(flip) idx.reverse();
  const before=new Map(TR.map(t=>[t,t.getBoundingClientRect().top]));
  idx.forEach(i=>tbody.appendChild(TR[i]));
  tbody.appendChild(TOTAL);
  $('tbl').classList.toggle('resorted', !(sortK==='pop' && !flip));
  if(slide) cancelAnimationFrame(slide.raf);
  TR.forEach(t=>{ t.style.transform=''; });
  if(reduced) return;
  const vh=innerHeight, moves=[];
  TR.forEach(t=>{ const a=before.get(t), b=t.getBoundingClientRect().top;
    // only the rows that start or land on the screen are animated
    if((a>-60&&a<vh+60)||(b>-60&&b<vh+60)) moves.push([t,a-b]); });
  const s0=performance.now(), ms=800;
  const step=now=>{ const k=Math.min(1,(now-s0)/ms), e=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2;
    for(const [t,d] of moves) t.style.transform=k<1?'translateY('+(d*(1-e)).toFixed(1)+'px)':'';
    if(k<1) slide.raf=requestAnimationFrame(step); else slide=null; };
  slide={raf:requestAnimationFrame(step)};
}
document.querySelectorAll('button.sort').forEach(b=>b.addEventListener('click',()=>sortBy(b.dataset.k)));

/* ---- the shares as areas: the stacked bar of every share folds into a treemap */
const TW=1000, TH=560;
function squarify(vals,x,y,w,h){
  // squarified treemap (Bruls, Huizing and van Wijk 2000) over values already sorted large to small
  const out=new Array(vals.length), total=vals.reduce((a,v)=>a+v.v,0);
  let items=vals.map(v=>({i:v.i,a:v.v/total*w*h}));
  let X=x,Y=y,Wd=w,Ht=h;
  const worst=(rowA,side)=>{ const s=rowA.reduce((a,b)=>a+b,0), mx=Math.max(...rowA), mn=Math.min(...rowA);
    return Math.max(side*side*mx/(s*s), s*s/(side*side*mn)); };
  while(items.length){
    const side=Math.min(Wd,Ht); let rowI=[items[0]], k=1;
    while(k<items.length){ const nx=rowI.concat([items[k]]);
      if(worst(nx.map(q=>q.a),side)<=worst(rowI.map(q=>q.a),side)){ rowI=nx; k++; } else break; }
    const s=rowI.reduce((a,q)=>a+q.a,0);
    if(Wd>=Ht){ const cw=s/Ht; let yy=Y;
      for(const q of rowI){ const ch=q.a/cw; out[q.i]=[X,yy,cw,ch]; yy+=ch; } X+=cw; Wd-=cw; }
    else { const ch=s/Wd; let xx=X;
      for(const q of rowI){ const cw=q.a/ch; out[q.i]=[xx,Y,cw,ch]; xx+=cw; } Y+=ch; Ht-=ch; }
    items=items.slice(k);
  }
  return out;
}
const TREE=squarify(D.rows.map((r,i)=>({i,v:r.p})),0,0,TW,TH);
// the same shares as one stacked bar across the top, where the fold starts
const STRIP=(()=>{ const tot=D.rows.reduce((a,r)=>a+r.p,0); let x=0;
  return D.rows.map(r=>{ const w=r.p/tot*TW, q=[x,0,w,34]; x+=w; return q; }); })();
let treeOn=false, fold=0, foldRaf=null;
function drawTree(){
  const box=$('tree'), NS='http://www.w3.org/2000/svg';
  let s='<svg viewBox="0 0 '+TW+' '+TH+'" xmlns="'+NS+'" role="img" aria-label="Every country as an area, sized by population">';
  D.rows.forEach((r,i)=>{
    const c=r.by>=r.dy?'#3987e5':'#d55181';
    s+='<rect data-i="'+i+'" fill="'+c+'" fill-opacity="'+(0.35+0.4*Math.min(1,r.s/3))
      +'" stroke="#121212" stroke-width="1"><title>'+r.n+'</title></rect>';
  });
  s+='<g id="tlab" pointer-events="none"></g></svg>'
    +'<p class="tk">Each area is a population. Blue where births outnumber deaths, pink where deaths do.</p>';
  box.innerHTML=s;
  box.querySelector('svg').addEventListener('mouseover',e=>{ const t=e.target.closest('rect[data-i]'); if(t) hover(+t.dataset.i); });
  box.querySelector('svg').addEventListener('mouseleave',()=>hover(-1));
  box.querySelector('svg').addEventListener('click',e=>{ const t=e.target.closest('rect[data-i]'); if(t) click(+t.dataset.i); });
  place(fold); light();
}
function place(k){
  const R=$('tree').querySelectorAll('rect[data-i]');
  R.forEach(e=>{ const i=+e.dataset.i, a=STRIP[i], b=TREE[i];
    const v=[0,1,2,3].map(j=>a[j]+(b[j]-a[j])*k);
    e.setAttribute('x',v[0].toFixed(2)); e.setAttribute('y',v[1].toFixed(2));
    e.setAttribute('width',Math.max(0,v[2]).toFixed(2)); e.setAttribute('height',Math.max(0,v[3]).toFixed(2)); });
  // the names come in once the fold is done, on the areas big enough to hold them
  const L=$('tlab'); let t='';
  if(k>=1) D.rows.forEach((r,i)=>{ const [x,y,w,h]=TREE[i];
    if(w>64&&h>22){ const fs=Math.max(11,Math.min(22,Math.sqrt(w*h)/9));
      if(r.n.length*fs*0.56<w-10){
        t+='<text x="'+(x+6).toFixed(1)+'" y="'+(y+fs+4).toFixed(1)+'" font-size="'+fs.toFixed(1)+'" fill="#f0f0f0">'+r.n+'</text>';
        const f2=Math.max(11,fs*0.72);
        if(h>fs+f2+16) t+='<text x="'+(x+6).toFixed(1)+'" y="'+(y+fs+f2+8).toFixed(1)+'" font-size="'+f2.toFixed(1)+'" fill="#c3c2b7">'+shareTxt(r.s)+'</text>'; } } });
  L.innerHTML=t;
}
function foldTo(target,done){
  if(foldRaf) cancelAnimationFrame(foldRaf);
  if(reduced){ fold=target; place(fold); if(done) done(); return; }
  const f0=fold, s0=performance.now(), ms=1100;
  const step=now=>{ const k=Math.min(1,(now-s0)/ms), e=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2;
    fold=f0+(target-f0)*e; place(fold);
    if(k<1) foldRaf=requestAnimationFrame(step); else { foldRaf=null; if(done) done(); } };
  foldRaf=requestAnimationFrame(step);
}
$('bTree').addEventListener('click',()=>{
  treeOn=!treeOn; $('bTree').setAttribute('aria-pressed',treeOn);
  if(treeOn){ if(!$('tree').firstChild) drawTree(); $('tree').hidden=false; fold=0; place(0); foldTo(1); }
  else foldTo(0,()=>{ $('tree').hidden=true; });
});

ticks(); card(); requestAnimationFrame(loop);
window.__pop=()=>({hov,pin,home,sortK,flip,treeOn,fold,
  order:[...tbody.querySelectorAll('tr[data-i]')].map(t=>+t.dataset.i),
  lastIsTotal:tbody.lastElementChild===TOTAL, secs:secs(),
  rects:document.querySelectorAll('#tree rect[data-i]').length});
window.__tree=TREE;
"""

JS_DATA = json.dumps(dict(
    world=dict(pop=WORLD["pop"], by=WORLD["births"], dy=WORLD["deaths"]),
    rows=[dict(n=r["name"], p=r["pop"], by=r["by"], dy=r["dy"],
               b=r["b"], d=r["d"], s=round(r["share"], 4)) for r in rows],
), separators=(",", ":"), ensure_ascii=False)

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Earth's Population Right Now · Altazor</title>
<style>
:root {{ --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff;
        --ink-2:#c3c2b7; --ink-3:#898781;
        --births:{C_BIRTH}; --deaths:{C_DEATH}; --share:{C_SHARE}; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }}
.wrap {{ max-width:1040px; margin:0 auto; padding:32px 20px 70px; }}
header.site {{ border-top:4px solid var(--accent); padding-top:22px; margin-bottom:26px;
  display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }}
.brand {{ font-weight:700; font-size:20px; letter-spacing:.1em; text-decoration:none; color:var(--text); }}
.brand:hover {{ color:var(--accent); }}
nav.site a {{ color:var(--muted); text-decoration:none; font-size:14px; }}
nav.site a:hover {{ color:var(--accent); }}
h1 {{ margin:0 0 6px; font-size:26px; }}
h2 {{ font-size:16px; margin:34px 0 10px; letter-spacing:.02em; }}
.stamp {{ color:var(--ink-3); font-size:12.5px; margin:0 0 22px; }}

.tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:14px; }}
.tile {{ background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:14px 16px; }}
.tile .lab {{ color:var(--muted); font-size:12.5px; }}
.tile .val {{ font-size:26px; font-weight:600; margin-top:2px; line-height:1.2; }}
.tile .sub {{ color:var(--ink-3); font-size:12px; margin-top:2px; }}
.method {{ color:var(--muted); font-size:12.5px; max-width:760px; }}

.legend {{ display:flex; gap:18px; font-size:12.5px; color:var(--ink-2);
  margin:26px 0 0; }}
.legend .sw {{ width:11px; height:11px; border-radius:3px; display:inline-block; margin-right:6px; }}

table {{ width:100%; border-collapse:collapse; margin-top:4px; }}
th {{ text-align:right; font-size:11.5px; letter-spacing:.06em; text-transform:uppercase;
  color:var(--ink-3); font-weight:600; padding:0 10px 8px; border-bottom:1px solid var(--line); }}
th.l {{ text-align:left; }}
td {{ padding:8px 10px; border-bottom:1px solid var(--line); font-size:14px; }}
td.num {{ text-align:right; font-variant-numeric:tabular-nums; color:var(--ink-2); }}
td.rank {{ color:var(--ink-3); width:34px; font-variant-numeric:tabular-nums; }}
td.pop {{ white-space:nowrap; }}
.gap {{ color:{C_GAP}; font-size:12.5px; font-variant-numeric:tabular-nums;
  margin-left:7px; }}
td.ct {{ white-space:nowrap; }}
.cw {{ display:flex; align-items:center; gap:10px; }}
img.flag {{ width:30px; height:20px; object-fit:cover; border-radius:2px;
  box-shadow:0 0 0 1px rgba(255,255,255,.14); display:block; flex:none; }}
td.share {{ width:190px; white-space:nowrap; }}
.track {{ display:inline-block; width:104px; height:9px; background:#242424; border-radius:5px;
  vertical-align:middle; overflow:hidden; }}
.fill {{ display:block; height:100%; background:var(--share); border-radius:0 4px 4px 0; }}
.pct {{ display:inline-block; width:60px; text-align:right; font-variant-numeric:tabular-nums;
  color:var(--ink-2); font-size:13px; margin-left:8px; }}
td.flow {{ width:266px; padding-top:6px; padding-bottom:6px; }}
svg.flow {{ display:block; width:100%; height:auto; }}
svg.flow rect {{ transition:opacity .12s; }}
svg.flow g:hover rect {{ opacity:.72; }}
tr.total td {{ border-bottom:none; color:var(--muted); font-size:13px; padding-top:12px; }}

.note {{ color:var(--muted); font-size:12.5px; max-width:760px; }}
.refs {{ font-size:13px; color:var(--ink-2); max-width:760px; }}
.refs p {{ padding-left:2.2em; text-indent:-2.2em; margin:0 0 .8em; }}
.refs a {{ color:var(--accent); }}
/* the heads sort the table */
button.sort {{ font:inherit; font-size:11.5px; letter-spacing:.06em; text-transform:uppercase;
  color:var(--ink-3); font-weight:600; background:none; border:none; padding:0; cursor:pointer; }}
button.sort:hover {{ color:var(--accent); }}
button.sort[aria-pressed="true"] {{ color:var(--text); }}
button.sort[aria-pressed="true"]::after {{ content:" \\2193"; color:var(--accent); }}
button.sort.up[aria-pressed="true"]::after {{ content:" \\2191"; }}
#tbl.resorted .gap {{ display:none; }}
#tbl tbody tr[data-i] {{ cursor:pointer; }}
#tbl tbody tr[data-i]:hover td {{ background:#171717; }}
#tbl tbody tr.on td {{ background:#1b2230; }}
#tbl tbody tr.home td {{ box-shadow:inset 0 1px 0 #3d4b60, inset 0 -1px 0 #3d4b60; }}
.tile .tick {{ font-variant-numeric:tabular-nums; color:var(--ink-2); }}

/* the controls: the chips of this page are the same pills as the site's */
.bar {{ display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin:22px 0 0;
  font-size:12.5px; color:var(--ink-2); }}
.bar .legend {{ margin:0 8px 0 0; }}
.bar .sp {{ flex:1 1 auto; }}
.chip {{ font:inherit; font-size:13px; padding:5px 13px; border-radius:999px;
  border:1px solid var(--line); background:var(--panel); color:var(--text); cursor:pointer; }}
.chip:hover {{ border-color:var(--accent); }}
.chip[aria-pressed="true"] {{ border-color:var(--accent); color:var(--accent); }}
select.chip {{ padding-right:10px; max-width:220px; }}

/* the live card: sticky above the table, so the counts stay in view */
.live {{ position:sticky; top:0; z-index:4; background:var(--bg); padding:10px 0 8px;
  margin-top:14px; }}
.live .card {{ background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:10px 14px; font-size:13.5px; line-height:1.5; min-height:68px; }}
.live .nm {{ font-weight:650; font-size:15px; margin-right:8px; }}
.live .pin {{ float:right; font-size:10.5px; letter-spacing:.07em; text-transform:uppercase;
  color:var(--accent); }}
.live .n {{ font-variant-numeric:tabular-nums; color:var(--text); }}
.live .b {{ color:#7fb0ef; }} .live .d {{ color:#e58aac; }}
.live .cmp {{ color:var(--ink-3); font-size:12.5px; margin-top:2px; }}
#tree {{ margin-top:6px; }}
#tree svg {{ display:block; width:100%; height:auto; }}
#tree rect {{ cursor:pointer; }}
#tree .tk {{ color:var(--ink-3); font-size:12px; margin:6px 0 0; }}
details.sources {{ margin-top:34px; border-top:1px solid var(--line); padding-top:10px; max-width:760px; }}
details.sources > summary {{ cursor:pointer; color:var(--muted); font-size:12.5px;
  letter-spacing:.06em; text-transform:uppercase; }}
details.sources > summary:hover {{ color:var(--accent); }}
details.sources h2 {{ margin-top:22px; }}
@media (max-width:820px) {{
  td.share, td.flow {{ width:auto; }} .track {{ width:56px; }}
  .tscroll {{ overflow-x:auto; -webkit-overflow-scrolling:touch; }}
  svg.flow {{ min-width:180px; }}
}}
@media (max-width:600px) {{
  .tiles {{ grid-template-columns:1fr 1fr; gap:10px; }}
  .tile {{ padding:10px 12px; }} .tile .val {{ font-size:20px; }}
  .tile .sub {{ font-size:11.5px; line-height:1.4; }}
  .live .card {{ font-size:12.5px; padding:8px 11px; min-height:0; }}
  .live .nm {{ font-size:14px; }}
}}
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library</a></nav>
</header>

<h1>Earth's Population Right Now</h1>
<p class="stamp">Snapshot taken {SNAPSHOT}, using United Nations projections for 2026.</p>

<div class="tiles">
  <div class="tile"><div class="lab">World population</div>
    <div class="val">{WORLD['pop']/1e9:.2f} billion</div>
    <div class="sub">{commas(WORLD['pop'])} in 2026</div>
    <div class="sub tick" id="tPop"></div></div>
  <div class="tile"><div class="lab">Births per day</div>
    <div class="val">{commas(w_b)}</div>
    <div class="sub">worldwide, more than {n_b} countries hold</div>
    <div class="sub tick" id="tBirths"></div></div>
  <div class="tile"><div class="lab">Deaths per day</div>
    <div class="val">{commas(w_d)}</div>
    <div class="sub">worldwide, more than {n_d} countries hold</div>
    <div class="sub tick" id="tDeaths"></div></div>
  <div class="tile"><div class="lab">Net growth per day</div>
    <div class="val">+{commas(w_b - w_d)}</div>
    <div class="sub">births minus deaths, more than {n_g} countries hold</div>
    <div class="sub tick" id="tNet"></div></div>
</div>

<div class="bar">
  <div class="legend">
    <span><span class="sw" style="background:var(--births)"></span>Births per day</span>
    <span><span class="sw" style="background:var(--deaths)"></span>Deaths per day</span>
  </div>
  <span class="sp"></span>
  <button class="chip" id="bTree" aria-pressed="false">Shares as areas</button>
  <select class="chip" id="home" aria-label="A country kept in view for comparison">
    <option value="-1">Compare with a country</option>
  </select>
</div>

<div class="live" id="live"><div class="card" id="card"></div></div>
<div id="tree" hidden></div>

<h2>Every country and area</h2>
{table_all}

<details class="sources"><summary>Sources</summary>
<h2>Notes</h2>
<p class="note">Every country and area the United Nations counts separately,
{len(rows)} of them, from India down to the Vatican. Population figures are
projections for 2026 under the medium variant, the middle of the range the UN
publishes. The ten largest hold {top10:.1f} percent of the world between them.</p>
<p class="note">Daily figures are the projected births and deaths for the whole
year divided by 365.25, so they describe an average day rather than any
particular one. Where that average is below one, the cell says so instead of
showing zero. In {len(shrinking)} of these {len(rows)} places the lower bar is
longer, meaning deaths outnumber births, though all of them can still grow
through migration, which these columns do not count.</p>
<p class="note">The rows add to {commas(listed)}, which is {share_listed:.2f}
percent of the UN's own world figure. The remainder is a gap in the source
rather than a missing country: the UN's world record is larger than the sum of
the places it lists. The running counts start when the page opens and add
each place's average second, the year's births or deaths divided by the
seconds in 365.25 days. Flags are served by
<a href="https://flagcdn.com" style="color:var(--accent)">FlagCDN</a>.</p>

<p class="method">A day's births, deaths and net growth each outrun whole
countries, and the counts beside those three figures say how many. They compare
against the 194 sovereign states among these {len(rows)} rows, the 193 members
of the United Nations and the Vatican, rather than against the whole table:
most of the smallest rows here are dependencies and overseas departments, and
a reader who hears "countries" is not thinking of Tokelau or Gibraltar. The
thresholds fall between real places. Four sovereign states, Samoa, Sao Tome and
Principe, Barbados and Vanuatu, sit between the day's net growth and the day's
births, which is why those two counts differ by four.</p>

<h2>References</h2>
<div class="refs">
<p>Our World in Data. (2024). <em>Population and demography</em> [Data set]. Based on
United Nations World Population Prospects (2024). Retrieved {SNAPSHOT}, from
<a href="https://ourworldindata.org/population-growth">https://ourworldindata.org/population-growth</a></p>
<p>United Nations, Department of Economic and Social Affairs, Population Division.
(2024). <em>World population prospects 2024: Summary of results</em>
(UN DESA/POP/2024/TR/NO. 9). United Nations.
<a href="https://population.un.org/wpp/">https://population.un.org/wpp/</a></p>
</div>
</details>
</div>
<script>
const D=__DATA__;
__SCRIPT__
</script>
</body>
</html>
"""

HTML = apa.apa_pass(HTML)
HTML = HTML.replace("__DATA__", JS_DATA).replace("__SCRIPT__", SCRIPT)
OUT.write_text(HTML, encoding="utf-8")
print(f"wrote {OUT} ({len(HTML)} bytes): {len(rows)} countries and areas, "
      f"{len(shrinking)} shrinking, listed {listed:,} = {share_listed:.2f}% of the world")
