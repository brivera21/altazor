#!/usr/bin/env python3
"""Generate numbers.html, Numbers: one number, seven ways to write it, and the line.

Written takes a number from 1 to 9999 and draws it in tally marks, Egyptian
hieroglyphs, Babylonian base sixty, Roman numerals, Chinese numerals, Maya base
twenty and Hindu-Arabic digits, each system's glyphs drawn from its rules, so a
change to the number changes all seven at once. The line takes the same number
and places it on a line from 0 to 100 read logarithmically, as young children
and people without number words do, or linearly, as schooled adults do, with a
slider between.

Data: tools/numbers_data.py.

Usage: python3 build_numbers.py
"""

import json
from pathlib import Path

import apa
from numbers_data import SYSTEMS, PRESETS, LINE, REFS

OUT = Path(__file__).parent.parent / "numbers.html"

NOTE1 = ("One number, written seven ways, each from its own rules. Tally and "
         "the Egyptian signs add: a mark for each unit, a sign for each power "
         "of ten, repeated. Roman adds and subtracts. Chinese names the place "
         "beside the digit, as the number is spoken. Babylonian, Maya and our "
         "own digits let the place carry the value, which is what makes a "
         "sign for nothing necessary, and arithmetic on paper possible.")

NOTE2 = ("The line asks where a number goes between 0 and 100. Second graders "
         "and adults without number words past five put ten near the middle: "
         "each step right is a multiplication, a logarithmic line. Schooled "
         "adults put ten a tenth of the way: equal steps for equal differences. "
         "The slider runs between the two readings, and the chosen number "
         "rides it.")

METHOD = ("Babylonian numbers are written in the older manner, an empty place "
          "left as a gap, since the placeholder sign came late; a number "
          "ending in an empty place was ambiguous, and is here too, as it was "
          "for them. Roman numerals above 3,999 use the bar that multiplies by "
          "a thousand. Chinese follows the modern written rule: one sign for "
          "any run of empty places, none at the end, and ten to nineteen "
          "without a leading one. Maya is pure base twenty, without the "
          "calendar's eighteen. The tally stops drawing past two hundred "
          "marks and says how many are left. The logarithmic line places a "
          "number n at log n over log 100; the blend is a straight mix of the "
          "two positions, which is how Siegler and Opfer fitted their "
          "intermediate cases.")


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


systems = [{"k": k, "n": n, "base": b, "place": p, "zero": z, "when": w, "reach": r, "b": note, "s": s}
           for k, n, b, p, z, w, r, note, s in SYSTEMS]
line = [{"k": k, "n": n, "b": b, "s": s} for k, n, b, s in LINE]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Numbers &middot; Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; }
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
h1 { margin:0 0 12px; font-size:26px; }
.controls { display:flex; align-items:center; gap:12px; flex-wrap:wrap; margin:0 0 12px; }
.controls label { font-size:13px; color:var(--muted); }
.controls input[type=number] { background:var(--panel); color:var(--text); border:1px solid var(--line);
  border-radius:8px; padding:6px 9px; width:110px; font:inherit; font-size:16px; font-variant-numeric:tabular-nums; }
.controls input[type=range] { width:200px; accent-color:var(--accent); }
.presets { display:flex; gap:6px; flex-wrap:wrap; }
.presets button, .bar button { background:var(--panel); color:var(--muted); border:1px solid var(--line);
  border-radius:999px; padding:5px 11px; font-size:12.5px; cursor:pointer; font-family:inherit; }
.presets button:hover, .bar button:hover { color:var(--text); border-color:#3d3d3d; }
.bar { display:flex; gap:6px; margin:0 0 10px; }
.bar button { font-size:13.5px; padding:6px 14px; }
.bar button.on { color:#0b0b0b; background:var(--accent); border-color:var(--accent); font-weight:700; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; }
#diagram svg { width:100%; height:auto; display:block; user-select:none; }
.side { flex:0 0 300px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:16px; }
#kindTxt { font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
#nameTxt { font-weight:700; font-size:17px; margin:2px 0 6px; }
#numTxt { font-size:13.5px; line-height:1.55; }
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
  <nav class="site"><a href="library.html">&larr; Library &middot; Abstractions</a><a href="chinese.html">The Most Used Chinese</a><a href="prime-spiral.html">The Prime Spiral</a><a href="scale.html">Scale</a></nav>
</header>
<h1>Numbers</h1>
<div class="bar" id="views"><button data-v="written" class="on">Written</button><button data-v="line">The line</button></div>
<div class="controls">
  <label for="num">the number</label>
  <input type="number" id="num" min="1" max="9999" step="1" value="2026">
  <span class="presets" id="presets"></span>
  <span id="blendWrap" hidden><label for="blend">reading</label> <input type="range" id="blend" min="0" max="100" step="1" value="0"> <span id="blendOut" style="font-size:13px;color:var(--muted)"></span></span>
</div>
<div class="stage">
  <div id="diagram"></div>
  <div class="side"><div class="card">
    <div id="kindTxt"></div>
    <div id="nameTxt">A system under the cursor lands here</div>
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
const SYS=__SYS__, PRESETS=__PRESETS__, LINE=__LINE__;
const W=980, H=760;
const el=document.getElementById('diagram');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
let view='written', n=2026, blend=0, hot=null;

/* ---- the seven writings, each a function of the number giving svg and a reading ---- */
const INK='#e6e6e6', DIM='#8a94a6';
function tally(n){
  // groups of five, four uprights and a bar across
  const groups=Math.floor(n/5), rest=n%5, cap=40;                 // 40 groups is two hundred marks
  let s='', x=0, y=0, drawn=0;
  const show=Math.min(groups,cap);
  for(let g=0; g<show; g++){
    if(x>700){ x=0; y+=34; }
    for(let i=0;i<4;i++) s+='<line x1="'+(x+i*6)+'" y1="'+y+'" x2="'+(x+i*6)+'" y2="'+(y+22)+'" stroke="'+INK+'" stroke-width="2"/>';
    s+='<line x1="'+(x-3)+'" y1="'+(y+20)+'" x2="'+(x+22)+'" y2="'+(y+2)+'" stroke="'+INK+'" stroke-width="2"/>';
    x+=34; drawn+=5;
  }
  if(groups<=cap){ if(x>700){ x=0; y+=34; } for(let i=0;i<rest;i++) s+='<line x1="'+(x+i*6)+'" y1="'+y+'" x2="'+(x+i*6)+'" y2="'+(y+22)+'" stroke="'+INK+'" stroke-width="2"/>'; drawn+=rest; }
  const left=n-drawn;
  const read=groups+' group'+(groups===1?'':'s')+' of five'+(rest?' and '+rest:'')+(left>0?'; '+drawn+' marks drawn, '+left.toLocaleString('en-US')+' more to make':'');
  return {svg:s, h:y+30, read, extra: left>0?'and '+left.toLocaleString('en-US')+' more marks':''};
}
function egypt(n){
  const d=[Math.floor(n/1000), Math.floor(n/100)%10, Math.floor(n/10)%10, n%10];
  const G=[
    (x,y)=>'<path d="M'+(x+9)+','+(y+26)+' V'+(y+14)+' M'+(x+9)+','+(y+14)+' L'+(x+2)+','+(y+3)+' L'+(x+9)+','+(y+9)+' L'+(x+16)+','+(y+3)+' Z" fill="none" stroke="'+INK+'" stroke-width="1.8" stroke-linejoin="round"/>',   // lotus, 1000
    (x,y)=>'<path d="M'+(x+3)+','+(y+22)+' C'+(x+3)+','+(y+8)+' '+(x+17)+','+(y+4)+' '+(x+15)+','+(y+13)+' C'+(x+13)+','+(y+20)+' '+(x+5)+','+(y+18)+' '+(x+7)+','+(y+12)+' C'+(x+8)+','+(y+9)+' '+(x+12)+','+(y+10)+' '+(x+11)+','+(y+13)+' M'+(x+3)+','+(y+22)+' V'+(y+26)+'" fill="none" stroke="'+INK+'" stroke-width="1.8" stroke-linecap="round"/>',   // coil of rope, 100
    (x,y)=>'<path d="M'+(x+2)+','+(y+26)+' V'+(y+12)+' A7,7 0 0 1 '+(x+16)+','+(y+12)+' V'+(y+26)+'" fill="none" stroke="'+INK+'" stroke-width="2.2"/>',   // heel bone, 10
    (x,y)=>'<line x1="'+(x+8)+'" y1="'+(y+4)+'" x2="'+(x+8)+'" y2="'+(y+26)+'" stroke="'+INK+'" stroke-width="2.2"/>',   // stroke, 1
  ];
  let s='', x=0, hmax=0; const words=[];
  const LAY=[[],[1],[2],[3],[4],[3,2],[3,3],[4,3],[4,4],[3,3,3]];   // strokes in rows, as the scribes grouped them
  const names=['lotus flowers','coils of rope','heel bones','strokes'];
  d.forEach((c,i)=>{ if(!c) return; words.push(c+' '+names[i]);
    const rows=LAY[c]; let j=0;
    rows.forEach((cnt,r)=>{ for(let col=0;col<cnt;col++){ s+=G[i](x+col*20, r*30); j++; } });
    hmax=Math.max(hmax, rows.length*30);
    x+=Math.max(...rows)*20+22; });
  return {svg:s, h:Math.max(60,hmax), read: words.join(', ')||'nothing: the Egyptians had no sign for it'};
}
function babylon(n){
  const places=[]; let m=n; do{ places.unshift(m%60); m=Math.floor(m/60); }while(m>0);
  let s='', x=0; const words=[];
  const wedge=(x,y)=>'<path d="M'+x+','+y+' L'+(x+9)+','+y+' L'+(x+4.5)+','+(y+14)+' Z" fill="'+INK+'"/>';
  const chev=(x,y)=>'<path d="M'+(x+12)+','+y+' L'+x+','+(y+6)+' L'+(x+12)+','+(y+12)+' L'+(x+6)+','+(y+6)+' Z" fill="'+INK+'"/>';
  places.forEach((v,i)=>{
    const t=Math.floor(v/10), o=v%10;
    if(v===0){ s+='<rect x="'+x+'" y="6" width="26" height="44" fill="none" stroke="'+DIM+'" stroke-dasharray="3 3"/>'; x+=46; words.push('an empty place'); return; }
    for(let j=0;j<t;j++) s+=chev(x+(j%3)*14, Math.floor(j/3)*16);
    x+=t?Math.min(t,3)*14+6:0;
    for(let j=0;j<o;j++) s+=wedge(x+(j%3)*11, Math.floor(j/3)*17);
    x+=Math.min(o,3)*11+26;
    words.push((t?t+' chevron'+(t>1?'s':''):'')+(t&&o?' and ':'')+(o?o+' wedge'+(o>1?'s':''):'')+' for '+v);
  });
  const read=places.map((v,i)=>v+(i<places.length-1?' × 60'+(places.length-1-i>1?'^'+(places.length-1-i):''):'')).join(' + ')+'  ('+words.join('; ')+')';
  return {svg:s, h:60, read};
}
function roman(n){
  const T=[[1000,'M'],[900,'CM'],[500,'D'],[400,'CD'],[100,'C'],[90,'XC'],[50,'L'],[40,'XL'],[10,'X'],[9,'IX'],[5,'V'],[4,'IV'],[1,'I']];
  let m=n, out='', bar='';
  if(m>=4000){ const th=Math.floor(m/1000); let t=''; let k=th; for(const [v,c] of T){ while(k>=v){ t+=c; k-=v; } } bar=t; m=m%1000; }
  for(const [v,c] of T){ while(m>=v){ out+=c; m-=v; } }
  let s='', x=0;
  if(bar){ s+='<text x="0" y="40" font-size="34" font-family="Georgia,serif" fill="'+INK+'">'+bar+'</text>'; const w=bar.length*24; s+='<line x1="0" y1="8" x2="'+w+'" y2="8" stroke="'+INK+'" stroke-width="2"/>'; x=w+8; }
  s+='<text x="'+x+'" y="40" font-size="34" font-family="Georgia,serif" letter-spacing="2" fill="'+INK+'">'+out+'</text>';
  return {svg:s, h:52, read:(bar?bar+' with a bar, ×1000, then ':'')+(out||'nothing')+(n>=4000?'':'')};
}
function chinese(n){
  const D='零一二三四五六七八九', P=['','十','百','千'];
  const d=[Math.floor(n/1000), Math.floor(n/100)%10, Math.floor(n/10)%10, n%10];
  let out='', zero=false, started=false;
  for(let i=0;i<4;i++){ const c=d[i], p=3-i;
    if(c===0){ if(started) zero=true; continue; }
    if(zero){ out+='零'; zero=false; }
    if(!(c===1 && p===1 && !started)) out+=D[c];      // 十 to 十九 without the leading 一
    out+=P[p]; started=true; }
  const s='<text x="0" y="40" font-size="34" fill="'+INK+'">'+out+'</text>';
  const gloss=[...out].map(ch=>{ const i=D.indexOf(ch); if(i>=0) return i; return {'十':'ten','百':'hundred','千':'thousand'}[ch]; }).join(' ');
  return {svg:s, h:52, read:out+': '+gloss};
}
function maya(n){
  const places=[]; let m=n; do{ places.push(m%20); m=Math.floor(m/20); }while(m>0);   // units first
  let s='', words=[];
  const levels=places.length, rowH=56;
  places.forEach((v,i)=>{
    const y=(levels-1-i)*rowH;             // units at the bottom
    if(v===0){ s+='<ellipse cx="22" cy="'+(y+28)+'" rx="14" ry="8" fill="none" stroke="'+INK+'" stroke-width="2"/><path d="M12,'+(y+30)+' q10,6 20,0" fill="none" stroke="'+INK+'" stroke-width="1.5"/>'; words.push('a shell, nothing'); return; }
    const bars=Math.floor(v/5), dots=v%5;
    for(let j=0;j<dots;j++) s+='<circle cx="'+(22-(dots-1)*7+j*14)+'" cy="'+(y+10)+'" r="4.5" fill="'+INK+'"/>';
    for(let j=0;j<bars;j++) s+='<rect x="0" y="'+(y+20+j*9)+'" width="44" height="6" rx="2" fill="'+INK+'"/>';
    words.push((dots?dots+' dot'+(dots>1?'s':''):'')+(dots&&bars?' and ':'')+(bars?bars+' bar'+(bars>1?'s':''):'')+' for '+v);
  });
  const read=[...places].reverse().map((v,i)=>{ const p=levels-1-i; return v+(p?' × 20'+(p>1?'^'+p:''):''); }).join(' + ')+'  ('+[...words].reverse().join('; ')+', top to bottom)';
  return {svg:s, h:levels*rowH, read};
}
function arabic(n){
  const t=String(n), E='٠١٢٣٤٥٦٧٨٩', D='०१२३४५६७८९';
  let s='<text x="0" y="40" font-size="36" font-variant-numeric="tabular-nums" letter-spacing="28" fill="'+INK+'">'+t+'</text>';
  const names=['thousands','hundreds','tens','ones'].slice(4-t.length);
  [...t].forEach((c,i)=>{ s+='<text x="'+(i*48+10)+'" y="58" text-anchor="middle" font-size="10" fill="'+DIM+'">'+names[i]+'</text>'; });
  s+='<text x="300" y="40" font-size="26" fill="'+DIM+'">'+[...t].map(c=>E[+c]).join('')+'</text><text x="300" y="58" font-size="10" fill="'+DIM+'">the same digits, Eastern Arabic shapes</text>';
  s+='<text x="540" y="40" font-size="26" fill="'+DIM+'">'+[...t].map(c=>D[+c]).join('')+'</text><text x="540" y="58" font-size="10" fill="'+DIM+'">Devanagari shapes</text>';
  return {svg:s, h:66, read:[...t].map((c,i)=>c+' '+names[i]).join(', ')};
}
const WRITE={tally,egypt,babylon,roman,chinese,maya,arabic};

/* ---- the card ---- */
function card(kind,name,rows,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').textContent=name;
  document.getElementById('numTxt').innerHTML=rows.filter(r=>r[1]).map(([k,v])=>'<b>'+esc(k)+'</b> '+esc(v)).join('<br>');
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').textContent=src;
}
function showSys(k){
  const sy=SYS.find(x=>x.k===k); if(!sy) return;
  const r=WRITE[k](n);
  card('A way of writing '+n.toLocaleString('en-US'), sy.n, [['this number',r.read],['base',sy.base],['place value',sy.place],['a sign for zero',sy.zero],['when and where',sy.when],['reach',sy.reach]], sy.b, sy.s);
}
function showLine(){
  const w=blend/100, pl=Math.log10(n)/2, pn=n/100, p=(1-w)*pl+w*pn;
  card('The number line', n.toLocaleString('en-US')+' on a line from 0 to 100',
    [['read logarithmically', (pl*100).toFixed(1)+'% of the way along'],['read linearly', (pn*100).toFixed(1)+'%'],
     ['at this reading', (p*100).toFixed(1)+'%, '+(w===0?'fully logarithmic':w===1?'fully linear':(100-blend)+'% log, '+blend+'% linear')]],
    (w<0.5?LINE[0].b:LINE[1].b), w<0.5?LINE[0].s:LINE[1].s);
}

/* ---- the drawings ---- */
function written(){
  let s='', y=24;
  for(const sy of SYS){
    const r=WRITE[sy.k](n), isHot=hot===sy.k;
    s+='<g data-k="'+sy.k+'" style="cursor:pointer">';
    s+='<rect x="0" y="'+(y-12)+'" width="'+W+'" height="'+(r.h+28)+'" fill="'+(isHot?'#1b2230':'transparent')+'" rx="8"/>';
    s+='<text x="20" y="'+(y+4)+'" font-size="11.5" fill="'+(isHot?'#58a6ff':DIM)+'" letter-spacing="0.06em">'+esc(sy.n.toUpperCase())+'</text>';
    s+='<g transform="translate(200,'+(y-10)+')">'+r.svg+'</g>';
    if(r.extra) s+='<text x="'+(W-20)+'" y="'+(y+r.h-8)+'" text-anchor="end" font-size="11" fill="'+DIM+'">'+esc(r.extra)+'</text>';
    s+='</g>';
    y+=r.h+34;
  }
  return {svg:s, h:y+10};
}
function lineView(){
  const L=70, R=W-70, y0=300, w=blend/100;
  const X=v=>{ const pl=Math.log10(v)/2, pn=v/100; return L+((1-w)*pl+w*pn)*(R-L); };
  let s='<text x="'+L+'" y="40" font-size="14" fill="#9a9a9a">where the numbers 1 to 100 fall, '+(w===0?'read logarithmically':w===1?'read linearly':(100-blend)+'% logarithmic and '+blend+'% linear')+'</text>';
  s+='<line x1="'+L+'" y1="'+y0+'" x2="'+R+'" y2="'+y0+'" stroke="#3d444d" stroke-width="2"/>';
  s+='<text x="'+L+'" y="'+(y0+40)+'" text-anchor="middle" font-size="12" fill="#9a9a9a">0</text><text x="'+R+'" y="'+(y0+40)+'" text-anchor="middle" font-size="12" fill="#9a9a9a">100</text>';
  for(let v=1; v<=100; v++){
    const x=X(v), lab=[1,2,3,5,10,20,30,50,70,100].includes(v);
    s+='<line x1="'+x.toFixed(1)+'" y1="'+(y0-(lab?14:7))+'" x2="'+x.toFixed(1)+'" y2="'+(y0+(lab?14:7))+'" stroke="'+(lab?'#cfd6e6':'#3d444d')+'" stroke-width="'+(lab?1.5:1)+'"/>';
    if(lab) s+='<text x="'+x.toFixed(1)+'" y="'+(y0-22)+'" text-anchor="middle" font-size="11.5" fill="#cfd6e6">'+v+'</text>';
  }
  // the two pure readings, faint, above and below, so the blend is seen against both
  for(const [ww,yy,lab] of [[0,y0-110,'logarithmic'],[1,y0+110,'linear']]){
    s+='<line x1="'+L+'" y1="'+yy+'" x2="'+R+'" y2="'+yy+'" stroke="#2b2b2b"/>';
    for(const v of [1,2,5,10,20,50,100]){ const x=L+((1-ww)*Math.log10(v)/2+ww*v/100)*(R-L); s+='<line x1="'+x.toFixed(1)+'" y1="'+(yy-5)+'" x2="'+x.toFixed(1)+'" y2="'+(yy+5)+'" stroke="#6b7280"/><text x="'+x.toFixed(1)+'" y="'+(yy+(ww?20:-10))+'" text-anchor="middle" font-size="10" fill="#6b7280">'+v+'</text>'; }
    s+='<text x="'+(L-10)+'" y="'+(yy+4)+'" text-anchor="end" font-size="11" fill="#6b7280">'+lab+'</text>';
  }
  // the chosen number, if it fits
  if(n<=100){ const x=X(n);
    s+='<line x1="'+x.toFixed(1)+'" y1="'+(y0-60)+'" x2="'+x.toFixed(1)+'" y2="'+(y0+60)+'" stroke="#ffb02e" stroke-width="1.5"/>';
    s+='<circle cx="'+x.toFixed(1)+'" cy="'+y0+'" r="7" fill="#ffb02e" stroke="#121212" stroke-width="1.5"/>';
    s+='<text x="'+x.toFixed(1)+'" y="'+(y0-68)+'" text-anchor="middle" font-size="13" font-weight="700" fill="#ffb02e">'+n+'</text>';
  } else s+='<text x="'+(W/2)+'" y="'+(y0+70)+'" text-anchor="middle" font-size="12" fill="#ffb02e">'+n.toLocaleString('en-US')+' is off this line; a number up to 100 rides it</text>';
  // where 10 lands, the tell-tale
  const x10=X(10);
  s+='<text x="'+x10.toFixed(1)+'" y="'+(y0+84)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">ten sits '+(((X(10)-L)/(R-L))*100).toFixed(0)+'% of the way along</text>';
  return {svg:s, h:460};
}
function render(){
  const r= view==='written'?written():lineView();
  el.innerHTML='<svg viewBox="0 0 '+W+' '+r.h+'" xmlns="http://www.w3.org/2000/svg" id="nsvg"><rect width="'+W+'" height="'+r.h+'" fill="#121212"/>'+r.svg+'</svg>';
  document.getElementById('blendWrap').hidden = view!=='line';
  document.getElementById('blendOut').textContent = blend===0?'logarithmic':blend===100?'linear':(100-blend)+'% log';
}
function setN(v){ v=Math.max(1,Math.min(9999,Math.round(v)||1)); n=v; document.getElementById('num').value=v; render(); if(view==='written'){ if(hot) showSys(hot); else showSys('arabic'); } else showLine(); }
function setView(v){ view=v; for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on',b.dataset.v===v); render(); if(v==='written') showSys(hot||'arabic'); else showLine(); }
document.getElementById('num').addEventListener('input',e=>setN(+e.target.value));
document.getElementById('presets').innerHTML=PRESETS.map(p=>'<button type="button" data-p="'+p+'">'+p.toLocaleString('en-US')+'</button>').join('');
document.getElementById('presets').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setN(+b.dataset.p); });
document.getElementById('blend').addEventListener('input',e=>{ blend=+e.target.value; render(); showLine(); });
document.getElementById('views').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setView(b.dataset.v); });
el.addEventListener('pointerover',e=>{ const g=e.target.closest('[data-k]'); if(g){ hot=g.getAttribute('data-k'); render(); showSys(hot); } });
setN(2026);
window.__num=(m)=>{ const q=m==null?n:m, cnt=(str,re)=>(str.match(re)||[]).length;
  const out={view,n,blend,hot,write:{},marks:{}};
  for(const k of Object.keys(WRITE)){ const r=WRITE[k](q); out.write[k]=r.read; out.marks[k]={
    lines:cnt(r.svg,/<line /g), circles:cnt(r.svg,/<circle /g), rects:cnt(r.svg,/<rect /g), ellipses:cnt(r.svg,/<ellipse /g),
    paths:cnt(r.svg,/<path /g), chevrons:cnt(r.svg,/<path d="M[^"]* L[^"]* L[^"]* L[^"]* Z"/g), h:r.h}; }
  const c=document.querySelector('#nsvg circle[fill="#ffb02e"]'); out.marker=c?+c.getAttribute('cx'):null;
  return out; };
</script>
</body>
</html>
"""

html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__SYS__", _js(systems)).replace("__PRESETS__", _js(PRESETS)).replace("__LINE__", _js(line))
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(SYSTEMS)} systems")
