#!/usr/bin/env python3
"""Generate prime-spiral.html, The Prime Spiral, the first Abstraction.

A point sets out from twelve o'clock and walks clockwise, laying down one
faint mark per unit of path. Where the distance walked is prime, the mark is
bright and amber. The first loop is a circle of twenty-four units; when the
loop closes the path steps outside and keeps circling, so the primes pile up
ring on ring, in the spirit of Ulam's spiral. The first twenty primes carry
their numbers; a button lets the walk keep going far past them.

Usage: python3 build_prime_spiral.py
"""

import apa
from pathlib import Path

OUT = Path(__file__).parent.parent / "prime-spiral.html"

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Prime Spiral · Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; --prime:#ffb02e; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
.wrap { max-width:1320px; margin:0 auto; padding:32px 20px 60px; }
header.site { border-top:4px solid var(--accent); padding-top:22px; margin-bottom:26px;
  display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }
.brand { font-weight:700; font-size:20px; letter-spacing:.1em; text-decoration:none; color:var(--text); }
.brand:hover { color:var(--accent); }
nav.site a { color:var(--muted); text-decoration:none; font-size:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 12px; font-size:26px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#stage { flex:1 1 560px; min-width:0; position:relative; }
#stage svg { width:100%; max-width:660px; height:auto; display:block; margin:0 auto;
  user-select:none; touch-action:none; cursor:grab; outline:none; border-radius:12px; }
#stage svg:focus-visible { box-shadow:0 0 0 1px var(--accent); }
#stage svg.zoomed { cursor:move; }
.hov { position:absolute; pointer-events:none; background:#1a1a1a; border:1px solid #3a3a3a;
  border-radius:8px; padding:4px 9px; font-size:12.5px; white-space:nowrap; color:var(--text);
  transform:translate(-50%,-100%); display:none; z-index:2; }
.hov b { color:var(--prime); font-weight:600; }
.side { flex:0 0 320px; min-width:0; position:sticky; top:16px; }
.tiles { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; margin-bottom:10px; }
.tile { background:var(--panel); border:1px solid var(--line); border-radius:10px;
  padding:8px 10px; }
.tile .k { font-size:10.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
.tile .v { font-size:20px; font-weight:700; margin-top:2px; }
.tile .s { font-size:11.5px; color:var(--muted); margin-top:1px; min-height:1.2em; }
.controls { display:flex; gap:8px; flex-wrap:wrap; align-items:center; margin-bottom:10px; }
.controls button { background:var(--panel); border:1px solid var(--line); color:var(--text);
  padding:6px 12px; border-radius:8px; cursor:pointer; font-size:13px; font-family:inherit; }
.controls button:hover { border-color:var(--accent); }
.controls button.on { border-color:var(--accent); color:var(--accent); }
.controls label { font-size:12.5px; color:var(--muted); }
.controls input[type=range] { vertical-align:middle; accent-color:var(--accent); }
.controls .row { display:flex; gap:8px; align-items:center; flex-wrap:nowrap; width:100%; }
.controls .row label { flex:0 0 96px; }
.controls .row input[type=range] { flex:1 1 120px; min-width:80px; }
.status { font-size:12.5px; color:var(--muted); min-height:1.6em; margin-bottom:8px; }
.status b { color:var(--text); font-weight:600; }
.info { font-size:12.5px; color:var(--muted); }
.caption { color:var(--muted); font-size:12.5px; margin-top:12px; line-height:1.55; }
details.sources { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
details.sources summary { cursor:pointer; color:var(--accent); }
details.sources p { margin:9px 0 0; }
details.sources .refs { margin-top:12px; }
.refs p { margin:0 0 8px; }
.refs a { color:var(--accent); }
@media (max-width:900px){ .stage{flex-direction:column;} #stage{flex:none; width:100%;} .side{position:static; width:100%; flex:none;} }
@media (max-width:600px){ .tiles{grid-template-columns:repeat(3,1fr);} .tile .v{font-size:17px;} }
@media (prefers-reduced-motion:reduce){ * { transition:none !important; } }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html#abstractions">&larr; Library</a></nav>
</header>
<h1>The Prime Spiral</h1>
<div class="stage">
<div id="stage"><div class="hov" id="hov"></div></div>
<div class="side">
<div class="tiles">
  <div class="tile"><div class="k">Along the path</div>
    <div class="v" id="tLen">0</div><div class="s">units walked</div></div>
  <div class="tile"><div class="k">Primes marked</div>
    <div class="v" id="tN">0</div><div class="s" id="tNs"></div></div>
  <div class="tile"><div class="k">Last prime</div>
    <div class="v" id="tP">&ndash;</div><div class="s" id="tPs"></div></div>
</div>
<div class="controls">
  <button id="bPlay">Pause</button>
  <button id="bRestart">Restart</button>
  <button id="bMore">Keep building</button>
  <button id="bUlam" title="the same numbers on Ulam's square spiral">Square spiral</button>
  <div class="row"><label for="spd">Speed</label>
  <input type="range" id="spd" min="1" max="40" step="1" value="6"></div>
  <div class="row"><label for="scrub">Along the path</label>
  <input type="range" id="scrub" min="0" max="72" step="1" value="0"></div>
</div>
<div class="status" id="status"></div>
<div class="info" id="hover"></div>
<p class="caption">The point sets out from twelve o'clock and walks clockwise,
one mark per unit of path; where the count is prime the mark is amber and,
through 71, numbered. Each prime wears a thin ring of its own color and every
multiple of it wears the same ring, so the sieve of Eratosthenes is in the
picture. Keep building runs the walk to a thousand.</p>
</div>
</div>
<details class="sources"><summary>Sources</summary>
<p>The first loop is a circle twenty-four units around; when it closes, the
path steps outside and keeps circling, so the primes stack ring on ring the
way they do on Ulam's spiral. The color of 2 lands on every second mark, the
color of 3 on every third, and a mark with several rings is a number with
several prime factors. A mark under the cursor gives its factorization, and
a prime, clicked, lights every multiple of it along the whole spiral; a second
click, or Escape, lets go. The walk stops at 71, the twentieth prime, until
Keep building sends it on to a thousand. Dragging across the drawing, or the
slider, runs the walk back and forth; the wheel zooms, a double click fits the
view again, and the arrow keys step one unit at a time once the drawing has
focus. Square spiral lays the same numbers on Ulam's square, where the primes
gather on diagonals.</p>
<div class="refs">
<p>Stein, M. L., Ulam, S. M., &amp; Wells, M. B. (1964). A visual display of
some properties of the distribution of primes. <i>The American Mathematical
Monthly, 71</i>(5), 516-520.
<a href="https://doi.org/10.2307/2312588">https://doi.org/10.2307/2312588</a></p>
<p>Sacks, R. (2003). <i>Number spiral</i>, where the integers ride an
Archimedean spiral instead of Ulam's square one.
<a href="https://numberspiral.com/">https://numberspiral.com/</a></p>
</div>
</details>
</div>
<script>
const W=820,H=820,CX=410,CY=410;
const UNIT=9;                 // pixels per unit of path
const R0=24*UNIT/(2*Math.PI); // the first loop is a circle of 24 units
const PITCH=3.4*UNIT;         // how far the path steps out per loop
const FIRST=71;               // the twentieth prime
const TAU=2*Math.PI;
// the first loop is a true circle; the step outward begins once it closes
const RADIUS=phi=>phi<TAU ? R0 : R0+PITCH*(phi-TAU)/TAU;
const CAP=1000;
const CELL=13;                // the side of a cell on Ulam's square
const REDUCED=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const ease=t=>t<0.5?2*t*t:1-Math.pow(-2*t+2,2)/2;

function isPrime(n){
  if(n<2) return false;
  for(let d=2;d*d<=n;d++) if(n%d===0) return false;
  return true;
}
function factors(n){          // distinct prime factors, in order
  const out=[]; let m=n;
  for(let d=2;d*d<=m;d++) if(m%d===0){ out.push(d); while(m%d===0) m/=d; }
  if(m>1) out.push(m);
  return out;
}
function factorization(n){    // 12 -> '2² × 3'
  const sup={0:'⁰',1:'¹',2:'²',3:'³',4:'⁴',
    5:'⁵',6:'⁶',7:'⁷',8:'⁸',9:'⁹'};
  const parts=[]; let m=n;
  for(let d=2;d*d<=m||m>1;d++){
    if(d*d>m&&m>1){ parts.push(String(m)); break; }
    if(m%d===0){ let e=0; while(m%d===0){m/=d;e++;}
      parts.push(d+(e>1?String(e).split('').map(c=>sup[+c]).join(''):'')); }
  }
  return parts.join(' × ');
}
// each prime, in the order the walk meets them, wears its own color, spread
// around the wheel by the golden angle
const primeColor={};
let primeIdx=0;
function colorOf(p){
  if(!(p in primeColor))
    primeColor[p]=`hsl(${(primeIdx++*137.508)%360},65%,62%)`;
  return primeColor[p];
}
// walk the spiral by arc length, numerically
const P=[{x:CX,y:CY-R0}];     // P[n] = position after n units
{
  let phi=0, r=R0, need=UNIT;
  const dphi=0.0005;
  while(P.length<=CAP+2){
    const r2=RADIUS(phi+dphi);
    const ds=Math.sqrt(((r2-r)/dphi)**2+((r+r2)/2)**2)*dphi;
    need-=ds; phi+=dphi; r=r2;
    if(need<=0){
      P.push({x:CX+r*Math.sin(phi), y:CY-r*Math.cos(phi)});
      need+=UNIT;
    }
  }
}
// the same numbers on Ulam's square: 1 at the center, 2 to its right, then
// up, left, down, each side one cell longer every second turn
const U=[];
{
  let x=0, y=0, dir=0, run=1, left=1, legs=0;
  const D=[[1,0],[0,-1],[-1,0],[0,1]];
  U[0]={x:CX-CELL, y:CY};    // the step before 1, coming in from the left
  for(let n=1;n<=CAP+2;n++){
    U[n]={x:CX+x*CELL, y:CY+y*CELL};
    x+=D[dir][0]; y+=D[dir][1]; left--;
    if(left===0){ dir=(dir+1)%4; legs++; if(legs%2===0) run++; left=run; }
  }
}
const FINE=[];                // the moving point's path, finely sampled
{
  let phi=0, r=R0, len=0;
  const dphi=0.004;
  while(len<=CAP+1){
    FINE.push({x:CX+r*Math.sin(phi), y:CY-r*Math.cos(phi), len});
    const r2=RADIUS(phi+dphi);
    len+=Math.sqrt(((r2-r)/dphi)**2+((r+r2)/2)**2)*dphi/UNIT;
    phi+=dphi; r=r2;
  }
}
const FINE_S=FINE.map(p=>'L'+p.x.toFixed(1)+','+p.y.toFixed(1));
function atRound(len){
  // binary search the fine path
  let lo=0, hi=FINE.length-1;
  while(hi-lo>1){ const m=(lo+hi)>>1; if(FINE[m].len<=len) lo=m; else hi=m; }
  const a=FINE[lo], b=FINE[Math.min(hi,FINE.length-1)];
  const t=(len-a.len)/Math.max(1e-9,b.len-a.len);
  return {x:a.x+(b.x-a.x)*t, y:a.y+(b.y-a.y)*t};
}
let mix=0;                    // 0 the round spiral, 1 Ulam's square
function pos(n){
  const a=P[n], b=U[n];
  return mix===0?a:mix===1?b:{x:a.x+(b.x-a.x)*mix, y:a.y+(b.y-a.y)*mix};
}
function at(len){
  if(mix===0) return atRound(len);
  const k=Math.floor(len), t=len-k, a=pos(k), b=pos(Math.min(k+1,CAP+1));
  return {x:a.x+(b.x-a.x)*t, y:a.y+(b.y-a.y)*t};
}

const stage=document.getElementById('stage');
stage.insertAdjacentHTML('afterbegin',`<svg viewBox="0 0 ${W} ${H}" id="psvg" tabindex="0" role="img" aria-label="The prime spiral">
  <circle cx="${CX}" cy="${CY}" r="2.4" fill="#3a3a3a"/>
  <path id="trail" fill="none" stroke="#2b2b2b" stroke-width="1.4"/>
  <g id="marks"></g><g id="labels"></g>
  <circle id="tip" r="3.6" fill="#e6e6e6"/>
</svg>`);
const trail=document.getElementById('trail'), marks=document.getElementById('marks'),
      labels=document.getElementById('labels'), tip=document.getElementById('tip'),
      svg=document.getElementById('psvg'), hov=document.getElementById('hov');

let LEN=0, TARGET=FIRST+1, playing=true, speed=6, marked=0, lastPrime=null;
let lit=null;                 // the prime whose multiples are lit
const NTH=['first','second','third','fourth','fifth','sixth','seventh','eighth',
  'ninth','tenth','eleventh','twelfth','thirteenth','fourteenth','fifteenth',
  'sixteenth','seventeenth','eighteenth','nineteenth','twentieth'];

function reset(){
  LEN=0; marked=0; lastPrime=null;
  marks.innerHTML=''; labels.innerHTML=''; trail.setAttribute('d','');
  nextMark=1; fineDrawn=0; d='M'+FINE[0].x.toFixed(1)+','+FINE[0].y.toFixed(1);
  tiles(); status();
}
let nextMark=1;
const GROUPS=[];              // the mark of each n, for moving them about
function place(n){
  const p=pos(n), prime=isPrime(n);
  const g=document.createElementNS('http://www.w3.org/2000/svg','g');
  g.setAttribute('data-n',n);
  g.setAttribute('transform',`translate(${p.x.toFixed(1)},${p.y.toFixed(1)})`);
  const c=document.createElementNS('http://www.w3.org/2000/svg','circle');
  c.setAttribute('r',prime?3.4:1.3);
  c.setAttribute('fill',prime?'var(--prime)':'#3f434c');
  c.setAttribute('data-n',n);
  g.appendChild(c);
  // the rings: a prime wears its own color, and every multiple wears the
  // ring of each prime that divides it
  factors(n).forEach((f,i)=>{
    const ring=document.createElementNS('http://www.w3.org/2000/svg','circle');
    ring.setAttribute('r',(prime?4.9:2.8)+i*1.6);
    ring.setAttribute('fill','none');
    ring.setAttribute('stroke',colorOf(f));
    ring.setAttribute('stroke-width','1.4');
    ring.setAttribute('data-n',n);
    g.appendChild(ring);
  });
  // a wider target for the pointer than the mark itself
  const hit=document.createElementNS('http://www.w3.org/2000/svg','circle');
  hit.setAttribute('r',prime?7:5); hit.setAttribute('fill','transparent');
  hit.setAttribute('data-n',n); hit.setAttribute('class','hit');
  g.appendChild(hit);
  marks.appendChild(g); GROUPS[n]=g;
  if(lit!==null) light(g,n);
  if(prime){
    marked++; lastPrime=n;
    if(marked<=20){
      const t=document.createElementNS('http://www.w3.org/2000/svg','text');
      const lp=labelPos(n);
      t.setAttribute('x',lp.x);
      t.setAttribute('y',lp.y);
      t.setAttribute('text-anchor','middle');
      t.setAttribute('font-size','9'); t.setAttribute('fill','var(--prime)');
      t.setAttribute('data-n',n);
      t.setAttribute('opacity',labelOpacity(n));
      t.textContent=n;
      labels.appendChild(t);
    }
  }
}
// the numbers fade on the square, where the cells leave no room for them
const labelOpacity=n=>(1-mix)*(lit===null||n%lit===0?1:0.25);
function labelPos(n){         // a prime's number sits just outside its mark
  const p=pos(n), away=Math.hypot(p.x-CX,p.y-CY)||1;
  return {x:(p.x+(p.x-CX)/away*11*(1-mix)).toFixed(1), y:(p.y+(p.y-CY)/away*11*(1-mix)+3-11*mix).toFixed(1)};
}
function unplace(n){          // the walk runs backwards: the mark comes off
  const g=GROUPS[n]; if(!g) return;
  g.remove(); GROUPS[n]=null;
  if(isPrime(n)){
    marked--; lastPrime=null;
    for(let m=n-1;m>=2;m--) if(isPrime(m)){ lastPrime=m; break; }
    const t=labels.querySelector(`text[data-n="${n}"]`); if(t) t.remove();
  }
}
function light(g,n){          // dim or brighten a mark while a prime is lit
  if(lit===null){ g.removeAttribute('opacity'); g.classList.remove('lit'); return; }
  const on=n%lit===0;
  g.setAttribute('opacity',on?1:0.18);
  g.classList.toggle('lit',on);
}
function setLit(p){
  lit=p;
  for(let n=1;n<nextMark;n++) if(GROUPS[n]) light(GROUPS[n],n);
  for(const t of labels.children) t.setAttribute('opacity',labelOpacity(+t.getAttribute('data-n')));
  document.getElementById('hover').textContent = lit===null?'':
    `the multiples of ${lit} are lit, every ${NTH[Math.min(lit-1,19)]}${lit>20?' (every '+lit+'th)':''} mark; a second click, or Escape, lets go`;
}
function tiles(){
  document.getElementById('tLen').textContent=Math.floor(LEN);
  document.getElementById('tN').textContent=marked;
  document.getElementById('tNs').textContent=
    marked===0?'':marked<=20?`the ${NTH[marked-1]} prime just passed`:'past the first twenty';
  document.getElementById('tP').textContent=lastPrime===null?'\\u2013':lastPrime;
  document.getElementById('tPs').textContent=lastPrime===null?'':'units from the start';
  const sc=document.getElementById('scrub'); sc.max=TARGET; sc.value=Math.floor(LEN);
}
function status(){
  const s=document.getElementById('status');
  if(LEN>=TARGET) s.innerHTML = TARGET===CAP
    ? 'The walk ends at <b>1,000</b>.'
    : 'The walk stops at <b>71</b>, the twentieth prime. Keep building runs it on to 1,000.';
  else s.innerHTML = playing ? `walking, ${Math.floor(LEN)} of ${TARGET.toLocaleString('en-US')} units` : `paused at ${Math.floor(LEN)} of ${TARGET.toLocaleString('en-US')} units`;
}
let d='M'+FINE[0].x.toFixed(1)+','+FINE[0].y.toFixed(1), fineDrawn=0;
function drawTrail(){
  if(mix===0){
    while(fineDrawn<FINE.length-1 && FINE[fineDrawn+1].len<=LEN){
      fineDrawn++; d+=FINE_S[fineDrawn];
    }
    trail.setAttribute('d',d);
  } else {
    let s=''; const k=Math.floor(LEN);
    for(let n=0;n<=k;n++){ const p=pos(n); s+=(n?'L':'M')+p.x.toFixed(1)+','+p.y.toFixed(1); }
    const p=at(LEN); s+='L'+p.x.toFixed(1)+','+p.y.toFixed(1);
    trail.setAttribute('d',s);
  }
}
function setLen(v, keepView){
  v=Math.max(0,Math.min(TARGET,v));
  if(v<LEN){                  // backwards: marks come off and the trail is cut
    const k=Math.floor(v);
    while(nextMark-1>k){ nextMark--; unplace(nextMark); }
    LEN=v;
    if(mix===0){
      while(fineDrawn>0 && FINE[fineDrawn].len>LEN) fineDrawn--;
      d='M'+FINE[0].x.toFixed(1)+','+FINE[0].y.toFixed(1)+FINE_S.slice(1,fineDrawn+1).join('');
    }
  } else LEN=v;
  drawTrail();
  while(nextMark<=Math.floor(LEN)){ place(nextMark); nextMark++; }
  const p=at(LEN);
  tip.setAttribute('cx',p.x); tip.setAttribute('cy',p.y);
  if(!keepView) frame(p);
  tiles(); status();
}
function step(dt){ setLen(LEN+dt*speed); if(LEN>=TARGET){ playing=false; document.getElementById('bPlay').textContent='Play'; status(); } }
// the view starts tight on the first circle and opens as the rings build,
// until the wheel takes it over
// (a jump along the path, from the slider or a drag, is followed over a few frames)
let half=null, manual=false, view={x:CX,y:CY}, wantHalf=null;
function frame(p){
  if(manual) return;
  let r=Math.hypot(p.x-CX,p.y-CY);
  for(let n=1;n<=Math.min(Math.floor(LEN),nextMark-1);n++){ const q=pos(n); r=Math.max(r,Math.hypot(q.x-CX,q.y-CY)); }
  wantHalf=Math.max(R0+PITCH+26, r+26);
  if(half===null || REDUCED) half=wantHalf;
  view={x:CX,y:CY};
  viewBox();
}
function follow(dt){
  if(manual || half===null || wantHalf===null || Math.abs(wantHalf-half)<0.05) return;
  half += (wantHalf-half)*(1-Math.exp(-dt/0.18)); viewBox();
}
function viewBox(){
  svg.setAttribute('viewBox',
    `${(view.x-half).toFixed(1)} ${(view.y-half).toFixed(1)} ${(2*half).toFixed(1)} ${(2*half).toFixed(1)}`);
}
let last=null;
function loop(ts){
  if(last!==null && playing && !dragging) { step(Math.min(0.1,(ts-last)/1000)); }
  if(last!==null) follow(Math.min(0.25,(ts-last)/1000)); last=ts;
  requestAnimationFrame(loop);
}
document.getElementById('bPlay').onclick=e=>{
  if(!playing && LEN>=TARGET){ reset(); half=null; }
  playing=!playing; e.target.textContent=playing?'Pause':'Play'; status();};
document.getElementById('bRestart').onclick=()=>{
  half=null; manual=false; svg.classList.remove('zoomed');
  TARGET=FIRST+1; document.getElementById('bMore').classList.remove('on');
  reset(); setLit(null); playing=true; document.getElementById('bPlay').textContent='Pause'; status();};
document.getElementById('bMore').onclick=e=>{
  TARGET=CAP; e.target.classList.add('on'); if(!playing){playing=true;
    document.getElementById('bPlay').textContent='Pause';} tiles(); status();};
document.getElementById('spd').oninput=e=>{speed=+e.target.value;};
document.getElementById('scrub').oninput=e=>{ if(playing){ playing=false; document.getElementById('bPlay').textContent='Play'; } setLen(+e.target.value); };
// round to square and back, the marks gliding to their new places
let tween=null;
function relayout(){
  for(let n=1;n<nextMark;n++){ const g=GROUPS[n]; if(!g) continue; const p=pos(n);
    g.setAttribute('transform',`translate(${p.x.toFixed(1)},${p.y.toFixed(1)})`); }
  for(const t of labels.children){ const n=+t.getAttribute('data-n'), lp=labelPos(n);
    t.setAttribute('x',lp.x); t.setAttribute('y',lp.y); t.setAttribute('opacity',labelOpacity(n)); }
  if(mix===0){ fineDrawn=0; d='M'+FINE[0].x.toFixed(1)+','+FINE[0].y.toFixed(1); }
  drawTrail();
  const p=at(LEN); tip.setAttribute('cx',p.x); tip.setAttribute('cy',p.y);
}
function setMix(target){
  const from=mix, t0=performance.now(), dur=REDUCED?0:900;
  if(tween) cancelAnimationFrame(tween);
  const run=now=>{ const t=dur?Math.min(1,(now-t0)/dur):1; mix=from+(target-from)*ease(t); if(t>=1) mix=target;
    relayout(); if(t<1) tween=requestAnimationFrame(run); else tween=null; };
  run(t0);
}
document.getElementById('bUlam').onclick=e=>{ const to=mix<0.5?1:0; e.target.classList.toggle('on',to===1); setMix(to); };
// drag to scrub, wheel to zoom, double click to fit again
let dragging=false, drag0=null;
svg.addEventListener('pointerdown',e=>{ if(e.button!==0) return; drag0={x:e.clientX,len:LEN,moved:false}; svg.setPointerCapture(e.pointerId); });
svg.addEventListener('pointermove',e=>{
  if(!drag0) return;
  const dx=e.clientX-drag0.x;
  if(!dragging && Math.abs(dx)<4) return;
  if(!dragging){ dragging=true; drag0.moved=true; svg.style.cursor='ew-resize'; }
  setLen(drag0.len+dx*0.3, true);
});
let justDragged=false;
const endDrag=e=>{ if(drag0&&dragging&&playing){ playing=false; document.getElementById('bPlay').textContent='Play'; status(); } justDragged=dragging; dragging=false; drag0=null; svg.style.cursor=''; };
svg.addEventListener('pointerup',endDrag); svg.addEventListener('pointercancel',endDrag);
svg.addEventListener('wheel',e=>{
  e.preventDefault();
  const r=svg.getBoundingClientRect();
  const px=view.x-half+(e.clientX-r.left)/r.width*2*half, py=view.y-half+(e.clientY-r.top)/r.height*2*half;
  const f=Math.exp(e.deltaY*0.0015), h2=Math.max(40,Math.min(700,half*f));
  view={x:px+(view.x-px)*h2/half, y:py+(view.y-py)*h2/half}; half=h2; manual=true; svg.classList.add('zoomed');
  viewBox();
},{passive:false});
svg.addEventListener('dblclick',()=>{ manual=false; half=null; wantHalf=null; svg.classList.remove('zoomed'); frame(at(LEN)); });
svg.addEventListener('keydown',e=>{
  if(e.key==='ArrowRight'||e.key==='ArrowLeft'){ e.preventDefault(); if(playing){ playing=false; document.getElementById('bPlay').textContent='Play'; }
    setLen(Math.floor(LEN)+(e.key==='ArrowRight'?1:-1)*(e.shiftKey?10:1)); }
  else if(e.key===' '){ e.preventDefault(); document.getElementById('bPlay').click(); }
  else if(e.key==='Escape'){ setLit(null); hov.style.display='none'; pinned=null; }
});
// a mark under the cursor gives its factorization, at the mark
let pinned=null;
function showMark(c){
  const n=+c.getAttribute('data-n');
  const txt=n<2?String(n):n+(isPrime(n)?', prime':' = '+factorization(n));
  const r=c.getBoundingClientRect(), s=stage.getBoundingClientRect();
  hov.innerHTML=isPrime(n)?'<b>'+txt+'</b>':txt;
  hov.style.left=(r.left+r.width/2-s.left)+'px'; hov.style.top=(r.top-s.top-8)+'px';
  hov.style.display='block';
}
svg.addEventListener('pointerover',e=>{
  if(dragging) return;
  const c=e.target.closest('[data-n]');
  if(c) showMark(c); else if(!pinned) hov.style.display='none';
});
svg.addEventListener('pointerleave',()=>{ if(!pinned) hov.style.display='none'; });
svg.addEventListener('click',e=>{
  if(justDragged){ justDragged=false; return; }
  const c=e.target.closest('[data-n]');
  if(!c){ pinned=null; hov.style.display='none'; setLit(null); return; }
  const n=+c.getAttribute('data-n');
  if(isPrime(n)){ setLit(lit===n?null:n); }
  pinned=c; showMark(c);
});
document.addEventListener('keydown',e=>{ if(e.key==='Escape'&&document.activeElement!==svg){ setLit(null); pinned=null; hov.style.display='none'; } });
reset();
requestAnimationFrame(loop);
window.__spiral=()=>({len:LEN,marked,lastPrime,target:TARGET,mix,lit,playing,manual,half,
  first:{x:P[1].x,y:P[1].y},start:{x:P[0].x,y:P[0].y},cx:CX,cy:CY,
  loop24:{x:P[24].x,y:P[24].y},ulam:{u1:U[1],u2:U[2],u3:U[3],u9:U[9],u10:U[10],u25:U[25]},
  groups:[...marks.children].map(g=>({n:+g.getAttribute('data-n'),t:g.getAttribute('transform'),o:g.getAttribute('opacity')}))});
</script>
</body>
</html>
"""

HTML = apa.css_pass(HTML)
OUT.write_text(HTML, encoding="utf-8")
print(f"wrote {OUT} ({len(HTML):,} bytes)")
