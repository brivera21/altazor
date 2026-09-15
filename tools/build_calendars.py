#!/usr/bin/env python3
"""Generate calendars.html, Calendars: the sky, the calendars, and one day.

Three views. The sky: the solar year as a ring with the twelve lunar months
inside it, eleven days short; dragging round the ring runs the years on,
and the lunar year slides backwards through the seasons, or, with a
thirteenth month added seven times in nineteen years, is held in place.
The calendars: eleven calendars as bars of their months, aligned at new
year, so that the lengths and the leap rules can be compared. One day: a
year and a day of the year, dragged along two lines, written in the
Gregorian, Julian, Hebrew, Islamic and Maya calendars, with its Julian day
number and its weekday.

Data: tools/calendars_data.py.

Usage: python3 build_calendars.py
"""

import json
from pathlib import Path

import apa
from calendars_data import SKY, CALENDARS, TZOLKIN, HAAB, HEBREW_MONTHS, ISLAMIC_MONTHS, MAYA_CORRELATION, REFS

OUT = Path(__file__).parent.parent / "calendars.html"

NOTE1 = ("The sky keeps two clocks that do not agree. The year is "
         "365.2422 days, the month 29.5306, and twelve months come to "
         "354.37 days, eleven short of a year; no whole number of either "
         "fits the other. Every calendar is a way of living with that: "
         "follow the moon and let the months wander through the seasons, "
         "follow the sun and let the months lose the moon, or follow both "
         "and add a thirteenth month now and then.")

NOTE2 = ("The first view is the mismatch itself, with the years running "
         "on under the pointer. The second is eleven calendars laid side "
         "by side, their months and their rules for the leftover fraction "
         "of a day. The third takes one day and writes it in six of them, "
         "from the Julian day number that astronomers use to the Maya Long "
         "Count.")

METHOD = ("The year and the month are the mean values for 2000: the "
          "tropical year is shortening by about half a second a century "
          "and the month varies by hours around its mean. The lunar rings "
          "use the mean month, so they show the arithmetic, not any one "
          "year's moon. The Hebrew and Islamic dates are those of the fixed "
          "calendars, the Hebrew one as set out in the fourth century and "
          "the tabular Islamic one with eleven leap years in thirty, which "
          "can differ by a day from the dates announced by observation. "
          "Julian and Gregorian dates are extended backwards before the "
          "calendars existed, the Gregorian one proleptically, and years "
          "before 1 AD are counted with no year zero. The Maya Long Count "
          "uses the 584,283 correlation, which most Mayanists accept; the "
          "day names and months are given in their modern orthography.")


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


cals = [{"k": k, "n": n, "kind": kind, "months": m, "leap": leap, "mean": mean, "rule": rule, "epoch": epoch, "b": b, "alive": alive} for k, n, kind, m, leap, mean, rule, epoch, b, alive in CALENDARS]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Calendars &middot; Altazor</title>
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
.presets { display:flex; gap:8px; flex-wrap:wrap; }
.presets button { background:var(--panel); color:var(--muted); border:1px solid var(--line);
  border-radius:8px; padding:4px 10px; font-size:12.5px; cursor:pointer; font-family:inherit; }
.presets button.on { color:var(--text); border-color:#58a6ff; }
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
  <nav class="site"><a href="library.html">&larr; Library &middot; Abstractions</a><a href="orbit-sine.html">Rotation</a><a href="moon.html">Lunar Cycle</a><a href="numbers.html">Numbers</a></nav>
</header>
<h1>Calendars</h1>
<div class="bar" id="views"><button data-v="sky" class="on">The sky</button><button data-v="cals">The calendars</button><button data-v="day">One day</button></div>
<div class="controls" id="skyCtl"><div class="presets" id="modes"><button data-m="moon" class="on">the Moon alone</button><button data-m="both">the Moon held to the Sun</button></div><label>years run on</label><output id="yrOut"></output></div>
<div class="controls" id="dayCtl" hidden><label>the markers</label><output id="dayOut"></output></div>
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
const SKY=__SKY__, CALS=__CALS__, TZOLKIN=__TZOLKIN__, HAAB=__HAAB__, HEB_M=__HEBM__, ISL_M=__ISLM__, MAYA0=__MAYA0__;
const W=980;
const el=document.getElementById('diagram');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const fmt=n=>n.toLocaleString('en-US');
const YEAR=SKY.tropical_year, MONTH=SKY.synodic_month, LUNAR=12*MONTH, SHORT=YEAR-LUNAR;
const GMONTHS=['January','February','March','April','May','June','July','August','September','October','November','December'];
const DOW=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
let view='sky', hot=null, years=0, mode='moon';
const today=new Date();
let year=today.getFullYear(), doy=Math.floor((Date.UTC(today.getFullYear(),today.getMonth(),today.getDate())-Date.UTC(today.getFullYear(),0,1))/86400000)+1;

/* ---- the card ---- */
function card(kind,name,rows,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').innerHTML=name;
  document.getElementById('numTxt').innerHTML=rows.filter(r=>r[1]).map(([k,v])=>'<b>'+esc(k)+'</b> '+v).join('<br>');
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').textContent=src;
}

/* ---- the sky ---- */
const isLeapMetonic=n=>[3,6,8,11,14,17,0].includes(((n%19)+19)%19); // year n of the cycle, 1-based, gets a 13th month
function lunarState(n){ // after n years: where the (n+1)th lunar year begins, in days from the solar new year, and its months
  let start=0, leaps=0; for(let i=1;i<=n;i++){ const m=mode==='both'&&isLeapMetonic(i)?13:12; if(mode==='both'&&m===13) leaps++; start+=m*MONTH-YEAR; }
  const months=mode==='both'&&isLeapMetonic(n+1)?13:12;
  const s=((start%YEAR)+YEAR)%YEAR; return {start:s, raw:start, months, leaps}; }
const SC={cx:470,cy:330,r1:262,r2:298,r3:196,r4:236};
const ang=d=>d/YEAR*2*Math.PI-Math.PI/2; // clockwise from the top
const pt=(r,d)=>[SC.cx+r*Math.cos(ang(d)),SC.cy+r*Math.sin(ang(d))];
function arc(r1,r2,d0,d1){ if(d1-d0>=YEAR-1e-9) d1=d0+YEAR-1e-6; const [ax,ay]=pt(r2,d0),[bx,by]=pt(r2,d1),[cx2,cy2]=pt(r1,d1),[dx,dy]=pt(r1,d0); const big=(d1-d0)/YEAR>0.5?1:0;
  return 'M'+ax.toFixed(1)+','+ay.toFixed(1)+' A'+r2+','+r2+' 0 '+big+' 1 '+bx.toFixed(1)+','+by.toFixed(1)+' L'+cx2.toFixed(1)+','+cy2.toFixed(1)+' A'+r1+','+r1+' 0 '+big+' 0 '+dx.toFixed(1)+','+dy.toFixed(1)+' Z'; }
function skyView(){ let s=''; const G=CALS[0].months; let d=0;
  G.forEach((m,i)=>{ const [tx,ty]=pt((SC.r1+SC.r2)/2,d+m[1]/2); s+='<path d="'+arc(SC.r1,SC.r2,d,d+m[1])+'" fill="'+(i%2?'#2a3a55':'#233047')+'" stroke="#121212" stroke-width="1"/><text x="'+tx.toFixed(1)+'" y="'+(ty+4).toFixed(1)+'" text-anchor="middle" font-size="11" fill="#c8c8c8">'+m[0]+'</text>'; d+=m[1]; });
  s+='<path d="'+arc(SC.r1,SC.r2,365,YEAR)+'" fill="#58a6ff"/>';
  for(const [dd,name] of SKY.seasons){ const [x1,y1]=pt(SC.r2,dd),[x2,y2]=pt(SC.r2+14,dd),[tx,ty]=pt(SC.r2+30,dd); s+='<line x1="'+x1.toFixed(1)+'" y1="'+y1.toFixed(1)+'" x2="'+x2.toFixed(1)+'" y2="'+y2.toFixed(1)+'" stroke="#ffb02e" stroke-width="2"/><text x="'+tx.toFixed(1)+'" y="'+(ty+4).toFixed(1)+'" text-anchor="middle" font-size="10.5" fill="#ffb02e">'+name.split(' ')[0]+'</text><text x="'+tx.toFixed(1)+'" y="'+(ty+16).toFixed(1)+'" text-anchor="middle" font-size="10.5" fill="#ffb02e">'+name.split(' ')[1]+'</text>'; }
  const L=lunarState(years); let dl=L.start;
  for(let i=0;i<L.months;i++){ const thirteenth=L.months===13&&i===12; s+='<path data-moon="'+i+'" d="'+arc(SC.r3,SC.r4,dl,dl+MONTH)+'" fill="'+(thirteenth?'#c9a6ff':i%2?'#cfcfcf':'#9a9a9a')+'" stroke="#121212" stroke-width="1"/>'; dl+=MONTH; }
  const gap=L.start+YEAR-dl; // days left in the solar year after the lunar one
  if(gap>0) s+='<path data-gap="short" d="'+arc(SC.r3,SC.r4,dl,dl+gap)+'" fill="#ff8c6a" style="cursor:pointer"/>';
  else s+='<path data-gap="long" d="'+arc(SC.r3-6,SC.r4+6,dl+gap,dl)+'" fill="none" stroke="#c9a6ff" stroke-width="1.5" stroke-dasharray="4 3"/>';
  const [sx,sy]=pt(SC.r3-8,L.start),[sx2,sy2]=pt(SC.r4+8,L.start); s+='<line x1="'+sx.toFixed(1)+'" y1="'+sy.toFixed(1)+'" x2="'+sx2.toFixed(1)+'" y2="'+sy2.toFixed(1)+'" stroke="#ffffff" stroke-width="2"/>';
  const [nx,ny]=pt(SC.r2+6,0),[nx2,ny2]=pt(SC.r1-6,0); s+='<line x1="'+nx.toFixed(1)+'" y1="'+ny.toFixed(1)+'" x2="'+nx2.toFixed(1)+'" y2="'+ny2.toFixed(1)+'" stroke="#ffffff" stroke-width="2"/>';
  s+='<text x="'+SC.cx+'" y="'+(SC.cy-22)+'" text-anchor="middle" font-size="13" fill="#e6e6e6">the Sun\\u2019s year, '+YEAR.toFixed(4)+' days</text><text x="'+SC.cx+'" y="'+(SC.cy)+'" text-anchor="middle" font-size="13" fill="#e6e6e6">the Moon\\u2019s twelve months, '+LUNAR.toFixed(2)+'</text>';
  s+='<text x="'+SC.cx+'" y="'+(SC.cy+24)+'" text-anchor="middle" font-size="12" fill="#ff8c6a">'+SHORT.toFixed(2)+' days short</text><text x="'+SC.cx+'" y="'+(SC.cy+48)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">'+(years?years+' year'+(years>1?'s':'')+' on':'year one')+'</text>';
  s+='<text x="'+SC.cx+'" y="'+(SC.cy+SC.r2+70)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">time runs clockwise from the top, the first of January; the white marks are the two new years; dragging round the ring runs the years on</text>';
  return {svg:s, h:SC.cy+SC.r2+86}; }
function showSky(){ const L=lunarState(years); const startDay=Math.round(L.start); let m=0, dd=startDay; while(dd>=CALS[0].months[m][1]&&m<11){ dd-=CALS[0].months[m][1]; m++; }
  const rows=[['after',years?years+' year'+(years>1?'s':''):'no time'],['the lunar year begins','about '+(dd+1)+' '+GMONTHS[m]+(years?', '+Math.abs(L.raw).toFixed(1)+' days '+(L.raw<0?'earlier':'later')+' than the solar one':'')]];
  if(mode==='moon') rows.push(['it comes round','every '+(YEAR/SHORT).toFixed(1)+' years']); else rows.push(['thirteenth months so far',L.leaps+' of 7 in each 19 years'],['after 19 years','235 months miss 19 years by only '+((235*MONTH-19*YEAR)*24).toFixed(1)+' hours']);
  card(mode==='moon'?'The Moon alone':'The Moon held to the Sun', mode==='moon'?'The months go round the seasons':'A thirteenth month now and then', rows,
    mode==='moon'?'Twelve lunar months are '+SHORT.toFixed(2)+' days short of a year, so a purely lunar calendar begins its year eleven days earlier each time, and its months visit every season in a third of a century. This is the Islamic calendar.':'When the lunar year has fallen a month behind, a thirteenth month is added: seven times in nineteen years, after which the Moon and the Sun are back in step to within two hours. This is the Hebrew and Chinese calendars, and it was Babylon\\u2019s and Athens\\u2019.',
    'Wikipedia, Tropical year; Wikipedia, Lunar month; Wikipedia, Metonic cycle'); }
function showGap(k){ if(k==='short') card('The gap','Eleven days',[['the year',YEAR.toFixed(5)+' days'],['twelve months',LUNAR.toFixed(3)+' days'],['short by',SHORT.toFixed(3)+' days, about 10 days 21 hours']],'The orange arc is the part of the solar year left over after twelve lunar months. No calendar can make it vanish; it can only be carried forward or paid off with a thirteenth month.','Wikipedia, Lunisolar calendar'); else card('The overlap','A long year',[['thirteen months',(13*MONTH).toFixed(2)+' days'],['over by',(13*MONTH-YEAR).toFixed(2)+' days']],'A year with a thirteenth month runs eighteen days past the solar year, paying back the eleven-day shortfalls of the years before it.','Wikipedia, Metonic cycle'); }

/* ---- the calendars ---- */
const CB={x:150,y:40,w:700,bar:26,gap:9,dmax:390};
const CX=d=>CB.x+d/CB.dmax*CB.w;
function calsView(){ let s=''; const h=CB.y+CALS.length*(CB.bar+CB.gap)+50;
  for(const d of [0,100,200,300]){ s+='<line x1="'+CX(d).toFixed(1)+'" y1="'+CB.y+'" x2="'+CX(d).toFixed(1)+'" y2="'+(h-40)+'" stroke="#2b2b2b"/><text x="'+CX(d).toFixed(1)+'" y="'+(h-24)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+d+'</text>'; }
  s+='<line x1="'+CX(YEAR).toFixed(1)+'" y1="'+(CB.y-14)+'" x2="'+CX(YEAR).toFixed(1)+'" y2="'+(h-40)+'" stroke="#ffb02e" stroke-dasharray="4 3"/><text x="'+CX(YEAR).toFixed(1)+'" y="'+(CB.y-18)+'" text-anchor="middle" font-size="10.5" fill="#ffb02e">the Sun, '+YEAR.toFixed(2)+'</text>';
  s+='<line x1="'+CX(LUNAR).toFixed(1)+'" y1="'+(CB.y-4)+'" x2="'+CX(LUNAR).toFixed(1)+'" y2="'+(h-40)+'" stroke="#cfcfcf" stroke-dasharray="4 3"/><text x="'+CX(LUNAR).toFixed(1)+'" y="'+(CB.y-6)+'" text-anchor="end" font-size="10.5" fill="#cfcfcf">12 moons, '+LUNAR.toFixed(2)+'</text>';
  s+='<text x="'+(CB.x+CB.w/2)+'" y="'+(h-8)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">days from new year, a common year of each calendar</text>';
  CALS.forEach((c,i)=>{ const y=CB.y+i*(CB.bar+CB.gap), on=hot===c.k||(hot&&hot.startsWith(c.k+':')); let d=0; const col=c.kind.startsWith('lunar')?'#cfcfcf':c.kind==='lunisolar'?'#c9a6ff':c.kind.startsWith('ritual')?'#f28cb0':'#58a6ff';
    s+='<g data-cal="'+c.k+'"><text x="'+(CB.x-10)+'" y="'+(y+CB.bar/2+4)+'" text-anchor="end" font-size="11.5" fill="'+(on?'#ffffff':'#e6e6e6')+'" style="cursor:pointer">'+esc(c.n)+'</text>';
    c.months.forEach((m,j)=>{ const x0=CX(d), w=CX(d+m[1])-x0, k=c.k+':'+j, mo=hot===k; s+='<g data-month="'+k+'" style="cursor:pointer"><rect x="'+x0.toFixed(1)+'" y="'+y+'" width="'+w.toFixed(1)+'" height="'+CB.bar+'" fill="'+col+'" opacity="'+(mo?1:on?0.85:j%2?0.55:0.7)+'" stroke="#121212" stroke-width="1"/>';
      const label=m[0].length*6.2<w-4?m[0]:(m[0].slice(0,3).length*6.2<w-4?m[0].slice(0,3):''); if(label) s+='<text x="'+(x0+w/2).toFixed(1)+'" y="'+(y+CB.bar/2+4)+'" text-anchor="middle" font-size="10" fill="#0b1a2b" pointer-events="none">'+esc(label)+'</text>'; s+='</g>'; d+=m[1]; });
    s+='<text x="'+(CB.x+CB.w+12)+'" y="'+(y+CB.bar/2+4)+'" font-size="10.5" fill="#9a9a9a">'+d+' days</text></g>'; });
  return {svg:s, h}; }
function showCal(k){ const c=CALS.find(x=>x.k===k); const days=c.months.reduce((a,m)=>a+m[1],0);
  card(c.kind+(c.alive?'':', no longer used'), esc(c.n), [['a common year',days+' days in '+c.months.length+' months'],['the leap rule',c.leap],['mean year',c.mean.toFixed(c.mean%1?4:0)+' days'+(c.mean>300?', '+(c.mean-YEAR>=0?'+':'')+((c.mean-YEAR)*1440).toFixed(0)+' minutes on the Sun':'')],['the count',c.epoch]], c.b, 'Reingold & Dershowitz 2018; Wikipedia, '+c.n+' calendar'); }
function showMonth(k){ const [ck,j]=k.split(':'); const c=CALS.find(x=>x.k===ck); const m=c.months[+j]; const before=c.months.slice(0,+j).reduce((a,x)=>a+x[1],0);
  card(esc(c.n)+', month '+(+j+1)+' of '+c.months.length, esc(m[0]), [['days',m[1]],['begins on day',before+1+' of the year'],['the rule',c.rule]], c.b, 'Wikipedia, '+c.n+' calendar'); }
function showCals(){ card('The calendars','Eleven ways of cutting up the year',[['solar',CALS.filter(c=>c.kind.startsWith('solar')).length+', of which two wander'],['lunisolar',CALS.filter(c=>c.kind==='lunisolar').length],['lunar','1, the Islamic'],['neither','1, the 260-day count']],'Each bar is one common year, month by month, from its new year; the dashed lines are the Sun\\u2019s year and twelve moons. Each calendar and each month answers under the pointer.','Reingold & Dershowitz 2018'); }

/* ---- one day: the arithmetic ---- */
const fl=Math.floor, mod=(a,b)=>((a%b)+b)%b;
function g2jdn(y,m,d){ const a=fl((14-m)/12), yy=y+4800-a, mm=m+12*a-3; return d+fl((153*mm+2)/5)+365*yy+fl(yy/4)-fl(yy/100)+fl(yy/400)-32045; }
function j2jdn(y,m,d){ const a=fl((14-m)/12), yy=y+4800-a, mm=m+12*a-3; return d+fl((153*mm+2)/5)+365*yy+fl(yy/4)-32083; }
function jdn2g(J){ const a=J+32044, b=fl((4*a+3)/146097), c=a-fl(146097*b/4), d=fl((4*c+3)/1461), e=c-fl(1461*d/4), m=fl((5*e+2)/153); return [100*b+d-4800+fl(m/10), m+3-12*fl(m/10), e-fl((153*m+2)/5)+1]; }
function jdn2j(J){ const c=J+32082, d=fl((4*c+3)/1461), e=c-fl(1461*d/4), m=fl((5*e+2)/153); return [d-4800+fl(m/10), m+3-12*fl(m/10), e-fl((153*m+2)/5)+1]; }
const gleap=y=>(y%4===0&&y%100!==0)||y%400===0;
const ISL0=1948440; // 1 Muharram 1 AH, 16 July 622 Julian
function isl2jdn(y,m,d){ return d+Math.ceil(29.5*(m-1))+(y-1)*354+fl((3+11*y)/30)+ISL0-1; }
function jdn2isl(J){ const y=fl((30*(J-ISL0)+10646)/10631); const m=Math.min(12,Math.ceil((J-(29+isl2jdn(y,1,1)))/29.5)+1); return [y,m,J-isl2jdn(y,m,1)+1]; }
const HEB0=347996; // the Hebrew epoch as a Julian day number
const hleap=y=>mod(7*y+1,19)<7;
function hdelay1(y){ const months=fl((235*y-234)/19), parts=12084+13753*months; let day=months*29+fl(parts/25920); if(mod(3*(day+1),7)<3) day++; return day; }
function hdelay2(y){ const last=hdelay1(y-1), now=hdelay1(y), next=hdelay1(y+1); return next-now===356?2:now-last===382?1:0; }
function h2jdn(y,m,d){ const months=hleap(y)?13:12; let jd=HEB0+hdelay1(y)+hdelay2(y)+d+1; if(m<7){ for(let mon=7;mon<=months;mon++) jd+=hmdays(y,mon); for(let mon=1;mon<m;mon++) jd+=hmdays(y,mon); } else { for(let mon=7;mon<m;mon++) jd+=hmdays(y,mon); } return jd; }
function hydays(y){ return h2jdn(y+1,7,1)-h2jdn(y,7,1); }
function hmdays(y,m){ if(m>13) return 0; if(m===2||m===4||m===6||m===10||m===13) return 29; if(m===12&&!hleap(y)) return 29; if(m===8&&mod(hydays(y),10)!==5) return 29; if(m===9&&mod(hydays(y),10)===3) return 29; return 30; }
function jdn2h(J){ const count=fl(((J-0.5-(HEB0-0.5))*98496)/35975351); let y=count-1; for(let i=count; J>=h2jdn(i,7,1); i++) y++; const first=J<h2jdn(y,1,1)?7:1; let m=first; for(let i=first; J>h2jdn(y,i,hmdays(y,i)); i++) m++; return [y,m,J-h2jdn(y,m,1)+1]; }
function maya(J){ let d=J-MAYA0; const lc=[]; for(const u of [144000,7200,360,20,1]){ lc.push(fl(d/u)); d=mod(d,u); } const dd=J-MAYA0; return {lc, tz:[mod(dd+3,13)+1, TZOLKIN[mod(dd+19,20)]], haab:[mod(dd+348,365)%20, HAAB[fl(mod(dd+348,365)/20)]]}; }
const yname=y=>y>0?y:(1-y)+' BC';
function hebName(y,m){ return hleap(y)&&m===12?'Adar I':HEB_M[m-1]; }
function convert(J){ const g=jdn2g(J), j=jdn2j(J), isl=jdn2isl(J), h=jdn2h(J), my=maya(J);
  return {jdn:J, dow:DOW[mod(J+1,7)], g, j, isl, h, my,
    text:{greg:g[2]+' '+GMONTHS[g[1]-1]+' '+yname(g[0]), jul:j[2]+' '+GMONTHS[j[1]-1]+' '+yname(j[0]), isl:isl[2]+' '+ISL_M[isl[1]-1]+' '+isl[0]+' AH', heb:h[2]+' '+hebName(h[0],h[1])+' '+h[0]+' AM', lc:my.lc.join('.'), cr:my.tz[0]+' '+my.tz[1]+' '+my.haab[0]+' '+my.haab[1]}}; }

/* ---- one day: the drawing ---- */
const DY={x:80,w:820,y:70,y0:-3000,y1:2300};
const DD={x:80,w:820,y:170};
const YX=y=>DY.x+(y-DY.y0)/(DY.y1-DY.y0)*DY.w;
const DX=d=>DD.x+(d-1)/365*DD.w;
function dayView(){ let s=''; const J=g2jdn(year,1,1)+doy-1; const c=convert(J);
  s+='<line x1="'+DY.x+'" y1="'+DY.y+'" x2="'+(DY.x+DY.w)+'" y2="'+DY.y+'" stroke="#8a94a6"/>';
  for(const y of [-2999,-1999,-999,1,1000,2000]){ const x=YX(y); s+='<line x1="'+x.toFixed(1)+'" y1="'+DY.y+'" x2="'+x.toFixed(1)+'" y2="'+(DY.y+6)+'" stroke="#8a94a6"/><text x="'+x.toFixed(1)+'" y="'+(DY.y+20)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+(y<=0?(1-y)+' BC':y+' AD')+'</text>'; }
  s+='<text x="'+DY.x+'" y="'+(DY.y-48)+'" font-size="11" fill="#9a9a9a">the year</text>';
  s+='<g id="ymark" style="cursor:ew-resize"><line x1="'+YX(year).toFixed(1)+'" y1="'+(DY.y-16)+'" x2="'+YX(year).toFixed(1)+'" y2="'+(DY.y+8)+'" stroke="#ffb02e" stroke-width="2"/><circle cx="'+YX(year).toFixed(1)+'" cy="'+DY.y+'" r="6" fill="#ffb02e" stroke="#121212" stroke-width="1.5"/><text x="'+YX(year).toFixed(1)+'" y="'+(DY.y-22)+'" text-anchor="middle" font-size="11.5" font-weight="700" fill="#ffb02e">'+yname(year)+'</text></g>';
  s+='<line x1="'+DD.x+'" y1="'+DD.y+'" x2="'+(DD.x+DD.w)+'" y2="'+DD.y+'" stroke="#8a94a6"/>';
  let d=0; CALS[0].months.forEach((m,i)=>{ const x=DX(d+1); s+='<line x1="'+x.toFixed(1)+'" y1="'+DD.y+'" x2="'+x.toFixed(1)+'" y2="'+(DD.y+6)+'" stroke="#8a94a6"/><text x="'+DX(d+m[1]/2).toFixed(1)+'" y="'+(DD.y+20)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+m[0]+'</text>'; d+=m[1]; });
  s+='<text x="'+DD.x+'" y="'+(DD.y-48)+'" font-size="11" fill="#9a9a9a">the day of the year, in the Gregorian calendar</text>';
  s+='<g id="dmark" style="cursor:ew-resize"><line x1="'+DX(doy).toFixed(1)+'" y1="'+(DD.y-16)+'" x2="'+DX(doy).toFixed(1)+'" y2="'+(DD.y+8)+'" stroke="#ffb02e" stroke-width="2"/><circle cx="'+DX(doy).toFixed(1)+'" cy="'+DD.y+'" r="6" fill="#ffb02e" stroke="#121212" stroke-width="1.5"/><text x="'+DX(doy).toFixed(1)+'" y="'+(DD.y-22)+'" text-anchor="middle" font-size="11.5" font-weight="700" fill="#ffb02e">'+c.g[2]+' '+GMONTHS[c.g[1]-1].slice(0,3)+'</text></g>';
  const rows=[['Gregorian',c.dow+', '+c.text.greg],['Julian',c.text.jul],['Julian day number',fmt(c.jdn)],['Hebrew',c.text.heb],['Islamic, tabular',c.text.isl],['Maya Long Count',c.text.lc],['Maya Calendar Round',c.text.cr]];
  rows.forEach(([k,v],i)=>{ const y=DD.y+70+i*34; s+='<text x="'+(W/2-14)+'" y="'+y+'" text-anchor="end" font-size="12.5" fill="#9a9a9a">'+k+'</text><text x="'+(W/2+14)+'" y="'+y+'" font-size="15" fill="#e6e6e6" font-variant-numeric="tabular-nums">'+esc(v)+'</text>'; });
  return {svg:s, h:DD.y+70+rows.length*34+10}; }
function showDay(){ const J=g2jdn(year,1,1)+doy-1; const c=convert(J);
  card('One day', c.dow+', '+esc(c.text.greg), [['Julian day number',fmt(c.jdn)+', the days since 1 January 4713 BC'],['in the Julian calendar',esc(c.text.jul)+(c.j[0]<-45?', long before it existed':'')],['in the Hebrew calendar',esc(c.text.heb)+(J<HEB0?'':', years from the creation')],['in the Islamic calendar',esc(c.text.isl)+(J<ISL0?', before the Hijra':'')],['in the Maya count',esc(c.text.lc)+', '+esc(c.text.cr)]],
    'The Julian day number is the plain count of days astronomers use so that no calendar gets in the way; every other date is a way of naming that number. The two markers set the year and the day.', 'Reingold & Dershowitz 2018; Walker 2015'); }

/* ---- render and wiring ---- */
function render(){ const q=view==='sky'?skyView():view==='cals'?calsView():dayView(); el.innerHTML='<svg viewBox="0 0 '+W+' '+q.h+'" xmlns="http://www.w3.org/2000/svg" id="csvg"><rect width="'+W+'" height="'+q.h+'" fill="#121212"/>'+q.svg+'</svg>';
  document.getElementById('skyCtl').hidden=view!=='sky'; document.getElementById('dayCtl').hidden=view!=='day'; document.getElementById('yrOut').textContent=years; const J=g2jdn(year,1,1)+doy-1; document.getElementById('dayOut').textContent=convert(J).text.greg; }
function home(){ if(view==='sky') showSky(); else if(view==='cals') showCals(); else showDay(); }
function setView(v){ view=v; hot=null; for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on',b.dataset.v===v); render(); home(); }
document.getElementById('views').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setView(b.dataset.v); });
document.getElementById('modes').addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; mode=b.dataset.m; for(const x of document.querySelectorAll('#modes button')) x.classList.toggle('on',x===b); render(); showSky(); });
let drag=null;
const svgPt=e=>{ const svg=document.getElementById('csvg'), b=svg.getBoundingClientRect(); return [(e.clientX-b.left)/b.width*W,(e.clientY-b.top)/b.height*svg.viewBox.baseVal.height]; };
function setYearsFromAngle(x,y){ const a=Math.atan2(y-SC.cy,x-SC.cx)+Math.PI/2; const t=mod(a,2*Math.PI)/(2*Math.PI); years=Math.round(t*(mode==='moon'?YEAR/SHORT:19)); if(mode==='moon'&&years>=Math.round(YEAR/SHORT)) years=0; render(); showSky(); }
el.addEventListener('pointerdown',e=>{ const [x,y]=svgPt(e);
  if(view==='sky'){ const r=Math.hypot(x-SC.cx,y-SC.cy); if(r>SC.r3-30&&r<SC.r2+40){ drag='sky'; setYearsFromAngle(x,y); e.preventDefault(); } }
  if(view==='day'){ if(Math.abs(y-DY.y)<26){ drag='year'; setYear(x); e.preventDefault(); } else if(Math.abs(y-DD.y)<26){ drag='day'; setDoy(x); e.preventDefault(); } } });
el.addEventListener('pointermove',e=>{ if(!drag) return; const [x,y]=svgPt(e); if(drag==='sky') setYearsFromAngle(x,y); else if(drag==='year') setYear(x); else setDoy(x); });
window.addEventListener('pointerup',()=>{ drag=null; });
function setYear(x){ year=Math.round(DY.y0+Math.max(0,Math.min(1,(x-DY.x)/DY.w))*(DY.y1-DY.y0)); if(doy===366&&!gleap(year)) doy=365; render(); showDay(); }
function setDoy(x){ doy=Math.round(1+Math.max(0,Math.min(1,(x-DD.x)/DD.w))*(gleap(year)?365:364)); render(); showDay(); }
el.addEventListener('pointerover',e=>{ if(drag) return; const g=e.target.closest('[data-gap],[data-cal],[data-month]'); if(!g) return;
  if(g.hasAttribute('data-gap')){ showGap(g.getAttribute('data-gap')); return; }
  const k=g.hasAttribute('data-month')?g.getAttribute('data-month'):g.getAttribute('data-cal'); if(k===hot) return; hot=k; render(); if(g.hasAttribute('data-month')) showMonth(k); else showCal(k); });
el.addEventListener('pointerleave',()=>{ if(view==='cals'&&hot){ hot=null; render(); showCals(); } if(view==='sky') showSky(); });

render(); showSky();
window.__cal=(q)=>{ const o={view,hot,years,mode,year,doy,card:document.getElementById('numTxt').innerText,name:document.getElementById('nameTxt').innerText,body:document.getElementById('bodyTxt').innerText};
  if(q&&q.jdn!=null) o.conv=convert(q.jdn);
  if(q&&q.g) o.jdn=g2jdn(q.g[0],q.g[1],q.g[2]);
  if(q&&q.h) o.hjdn=h2jdn(q.h[0],q.h[1],q.h[2]);
  if(q&&q.years!=null){ const save=years, sm=mode; years=q.years; if(q.mode) mode=q.mode; o.lunar=lunarState(years); years=save; mode=sm; }
  if(view==='sky'){ const m=document.querySelector('#csvg path[data-moon="0"]'); o.moon0=m?m.getAttribute('d'):null; o.arc0=arc(SC.r3,SC.r4,lunarState(years).start,lunarState(years).start+MONTH); }
  if(view==='cals'){ o.bars=document.querySelectorAll('#csvg g[data-cal]').length; o.cells=document.querySelectorAll('#csvg g[data-month]').length; if(q&&q.cal){ const r=[...document.querySelectorAll('#csvg g[data-cal="'+q.cal+'"] g[data-month] rect')]; o.barEnd=Math.max(...r.map(x=>+x.getAttribute('x')+ +x.getAttribute('width'))); o.cx=CX; o.expect=CX(CALS.find(c=>c.k===q.cal).months.reduce((a,m)=>a+m[1],0)); } }
  if(view==='day'){ const ym=document.querySelector('#ymark circle'), dm=document.querySelector('#dmark circle'); o.ymark=ym?+ym.getAttribute('cx'):null; o.dmark=dm?+dm.getAttribute('cx'):null; o.yx=YX(year); o.dx=DX(doy); }
  return o; };
</script>
</body>
</html>
"""

html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__SKY__", _js(SKY)).replace("__CALS__", _js(cals)).replace("__TZOLKIN__", _js(TZOLKIN)).replace("__HAAB__", _js(HAAB)).replace("__HEBM__", _js(HEBREW_MONTHS)).replace("__ISLM__", _js(ISLAMIC_MONTHS)).replace("__MAYA0__", str(MAYA_CORRELATION))
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(CALENDARS)} calendars")
