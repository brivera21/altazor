#!/usr/bin/env python3
"""Generate music.html, Music: the notes, the intervals, and the scales.

Three views. The notes: the range of hearing on a log scale with the
piano's 88 keys laid along it at their frequencies, the voices and the
instruments as bars beneath, and a marker that drags along the line and
reads the note, its frequency and wavelength, and its harmonics. The
intervals: the twelve steps of the octave on a ring, with the pure ratio
of each set against the tempered one, and a spiral of twelve pure fifths
that misses seven octaves by a quarter of a semitone. The scales: sixteen
scales on a two-octave keyboard.

Data: tools/music_data.py.

Usage: python3 build_music.py
"""

import json
from pathlib import Path

import apa
from music_data import A4, SPEED_OF_SOUND, HEARING, PIANO, NOTE_NAMES, RANGES, INTERVALS, SCALES, REFS

OUT = Path(__file__).parent.parent / "music.html"

NOTE1 = ("Music is arithmetic the ear does without being asked. A string "
         "half as long sounds the same note higher, and every culture "
         "hears it so; a string two thirds as long sounds a fifth, and "
         "from those two ratios, 2:1 and 3:2, most of the world's scales "
         "were built. The first view is the whole range of hearing with "
         "the piano laid along it and the voices and instruments beneath; "
         "the marker reads any pitch and its overtones.")

NOTE2 = ("The second view is the catch: twelve pure fifths do not quite "
         "make seven octaves, and pure thirds do not fit twelve equal steps, "
         "so every keyboard is a compromise, and the piano's thirds are "
         "fourteen cents wide. The third view is what is done with the "
         "twelve notes: the major and minor scales, the old church modes, "
         "the five-note scale found on every continent, and the symmetrical "
         "scales that go nowhere on purpose.")

METHOD = ("Frequencies are twelve-tone equal temperament on A4 = 440 Hz, "
          "the ISO standard since 1975; orchestras tune anywhere from 440 "
          "to 443. Wavelengths use 343 meters a second, the speed of sound "
          "in air at 20 degrees. The ranges of voices and instruments are "
          "the usual textbook ones and are stretched by particular singers "
          "and players. The just ratios are the five-limit ones, built from "
          "2, 3 and 5; other choices exist for the tritone and the sevenths. "
          "A cent is a hundredth of an equal-tempered semitone, 1200 to the "
          "octave. The scales are given from C; each starts on the same "
          "root so that the patterns can be compared.")


def _js(o):
    return json.dumps(o, separators=(",", ":"), ensure_ascii=False)


ranges = [{"k": k, "n": n, "kind": kind, "lo": lo, "hi": hi, "b": b} for k, n, kind, lo, hi, b in RANGES]
intervals = [{"s": s, "n": n, "r": r, "b": b} for s, n, r, b in INTERVALS]
scales = [{"k": k, "n": n, "fam": fam, "steps": st, "b": b} for k, n, fam, st, b in SCALES]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Music &middot; Altazor</title>
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
.presets { display:flex; gap:6px; flex-wrap:wrap; }
.presets button { background:var(--panel); color:var(--muted); border:1px solid var(--line);
  border-radius:8px; padding:4px 10px; font-size:12.5px; cursor:pointer; font-family:inherit; }
.presets button.on { color:var(--text); border-color:#58a6ff; }
.presets .fam { font-size:11.5px; color:#6b7280; align-self:center; margin:0 4px 0 8px; }
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
  <nav class="site"><a href="library.html">&larr; Library &middot; Abstractions</a><a href="numbers.html">Numbers</a><a href="light.html">Light</a><a href="body.html">The Human Body</a></nav>
</header>
<h1>Music</h1>
<div class="bar" id="views"><button data-v="notes" class="on">The notes</button><button data-v="intervals">The intervals</button><button data-v="scales">The scales</button></div>
<div class="controls" id="notesCtl"><label>the marker</label><output id="freqOut"></output></div>
<div class="controls" id="intCtl" hidden><div class="presets" id="imodes"><button data-m="just" class="on">pure against tempered</button><button data-m="fifths">twelve fifths</button></div></div>
<div class="controls" id="scaleCtl" hidden><div class="presets" id="scales"></div></div>
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
const A4=__A4__, C_AIR=__CAIR__, HEAR=__HEAR__, PIANO=__PIANO__, NAMES=__NAMES__, RANGES=__RANGES__, INTERVALS=__INTERVALS__, SCALES=__SCALES__;
const W=980;
const el=document.getElementById('diagram');
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const fmt=(n,d)=>n.toLocaleString('en-US',{maximumFractionDigits:d==null?0:d,minimumFractionDigits:d==null?0:d});
let view='notes', hot=null, freq=A4, imode='just', scale='major';
const midiFreq=m=>A4*Math.pow(2,(m-69)/12);
const freqMidi=f=>69+12*Math.log2(f/A4);
const noteName=m=>NAMES[((m%12)+12)%12]+(Math.floor(m/12)-1);
const isBlack=m=>[1,3,6,8,10].includes(((m%12)+12)%12);
const cents=r=>1200*Math.log2(r);

/* ---- the card ---- */
function card(kind,name,rows,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').innerHTML=name;
  document.getElementById('numTxt').innerHTML=rows.filter(r=>r[1]).map(([k,v])=>'<b>'+esc(k)+'</b> '+v).join('<br>');
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').textContent=src;
}
function showFreq(f){ const m=freqMidi(f), n=Math.round(m), off=Math.round((m-n)*100); const lam=C_AIR/f;
  const harm=[2,3,4,5,6,7,8].filter(k=>k*f<=HEAR[1]).map(k=>{ const hm=freqMidi(k*f), hn=Math.round(hm); return k+'\\u00d7 '+fmt(k*f,0)+' Hz, '+noteName(hn)+(Math.abs(Math.round((hm-hn)*100))>=10?' ('+(Math.round((hm-hn)*100)>0?'+':'')+Math.round((hm-hn)*100)+'\\u00a2)':''); });
  const within=RANGES.filter(r=>n>=r.lo&&n<=r.hi&&r.k!=='piano').map(r=>r.n);
  card('A pitch', fmt(f,f<100?1:0)+' Hz, '+(off?noteName(n)+' '+(off>0?'+':'')+off+' cents':noteName(n)), [['wavelength in air',lam>=1?fmt(lam,2)+' m':fmt(lam*100,1)+' cm'],['period',f<1000?fmt(1000/f,2)+' ms':fmt(1e6/f,0)+' \\u00b5s'],['on the piano',n>=PIANO[0]&&n<=PIANO[1]?'key '+(n-PIANO[0]+1)+' of 88':n<PIANO[0]?'below the lowest key':'above the highest key'],['harmonics',harm.join('; ')],['within the range of',within.length?within.join(', '):'no voice or instrument listed here']],
    'A string or a column of air sounding this pitch also sounds its whole-number multiples, fainter: the octave, then the fifth above it, then the second octave, then the major third above that. The ear hears them as one note with a color.', 'Wikipedia, Harmonic series (music); Wikipedia, Piano key frequencies'); }
function showRange(k){ const r=RANGES.find(x=>x.k===k); card(r.kind, esc(r.n), [['range',noteName(r.lo)+' to '+noteName(r.hi)+', '+fmt(midiFreq(r.lo),1)+' to '+fmt(midiFreq(r.hi),0)+' Hz'],['span',((r.hi-r.lo)/12).toFixed(1)+' octaves']], r.b, 'Wikipedia, Vocal range; Wikipedia, '+r.n.replace(' voice','')); }
function showInterval(s){ const iv=INTERVALS.find(x=>x.s===s); const c=cents(iv.r[0]/iv.r[1]), d=c-100*s;
  card('An interval', esc(iv.n)+', '+s+' semitone'+(s===1?'':'s'), [['pure ratio',iv.r[0]+':'+iv.r[1]+', '+c.toFixed(1)+' cents'],['on the piano',100*s+' cents'],['the piano is',Math.abs(d)<0.5?'as good as pure':fmt(Math.abs(d),1)+' cents '+(d>0?'flat':'sharp')+' of pure']], iv.b, 'Wikipedia, Just intonation; Wikipedia, Equal temperament'); }
function showJust(){ card('The intervals','Pure against tempered',[['a fifth, pure','3:2, 701.96 cents'],['a fifth, on the piano','700 cents, 2 short'],['a major third, pure','5:4, 386.31 cents'],['a major third, on the piano','400 cents, 14 wide']],'Each gray dot is one of the piano\\u2019s twelve equal steps; the colored dot beside it is the pure ratio, and the little line between them is how far the piano is out. The fifths are nearly perfect; the thirds are not.','Wikipedia, Just intonation; Wikipedia, Equal temperament'); }
function showFifths(){ const comma=12*cents(1.5)-8400; card('Twelve fifths','The Pythagorean comma',[['twelve pure fifths',fmt(12*cents(1.5),2)+' cents'],['seven octaves','8,400 cents'],['the difference',fmt(comma,2)+' cents, about a quarter of a semitone']],'Going up by pure fifths from C, C G D A E B F sharp C sharp G sharp D sharp A sharp F, the twelfth fifth lands on a B sharp that is not quite the C it should be. Equal temperament shares the comma out, two cents off each fifth, so that the circle closes.','Wikipedia, Pythagorean comma; Benson 2006'); }
function showFifth(i){ const names=['C','G','D','A','E','B','F\\u266f','C\\u266f','G\\u266f','D\\u266f','A\\u266f','F','B\\u266f']; const c=i*cents(1.5), oct=Math.floor(c/1200), within=c-1200*oct; const eq=(7*i)%12*100;
  card('A fifth up', names[i]+(i===12?', which should be C':''), [['fifths from C',i],['cents above C',fmt(c,2)+', '+oct+' octave'+(oct===1?'':'s')+' and '+fmt(within,2)],['on the piano',eq+' cents in the octave'],['the difference',fmt(within-eq,2)+' cents sharp']], i===12?'The spiral has gone round seven octaves and come back 23.46 cents above where it started. No number of pure fifths ever lands on an octave, because no power of 3 is a power of 2.':'Each pure fifth adds 701.955 cents, 1.955 more than the piano\\u2019s, and the excess piles up.', 'Wikipedia, Pythagorean comma'); }
function showScale(k){ const s=SCALES.find(x=>x.k===k); const steps=s.steps.map((v,i)=>i?v-s.steps[i-1]:null).slice(1).concat([12-s.steps[s.steps.length-1]]);
  card(s.fam, esc(s.n)+' on C', [['notes',s.steps.map(v=>NAMES[v]).join(' ')+' ('+s.steps.length+')'],['steps in semitones',steps.join(' ')],['pattern',steps.map(v=>v===1?'H':v===2?'W':v===3?'W+H':v).join(' ')]], s.b, 'Wikipedia, Scale (music); Wikipedia, Mode (music)'); }

/* ---- the notes ---- */
const N={x:70,y:40,w:850,f0:HEAR[0],f1:HEAR[1]};
const FX=f=>N.x+Math.log(f/N.f0)/Math.log(N.f1/N.f0)*N.w;
function notesView(){ let s=''; const ky=120, kh=70;
  for(const f of [20,50,100,200,500,1000,2000,5000,10000,20000]){ const x=FX(f); s+='<line x1="'+x.toFixed(1)+'" y1="'+N.y+'" x2="'+x.toFixed(1)+'" y2="'+(N.y+6)+'" stroke="#8a94a6"/><text x="'+x.toFixed(1)+'" y="'+(N.y-8)+'" text-anchor="middle" font-size="10.5" fill="#9a9a9a">'+(f>=1000?f/1000+' kHz':f+' Hz')+'</text>'; }
  s+='<line x1="'+N.x+'" y1="'+N.y+'" x2="'+(N.x+N.w)+'" y2="'+N.y+'" stroke="#8a94a6"/><text x="'+(N.x+N.w)+'" y="'+(N.y+22)+'" text-anchor="end" font-size="11" fill="#9a9a9a">the range of hearing, 20 Hz to 20 kHz, on a log scale</text>';
  // the piano, key by key at its frequency
  for(let m=PIANO[0];m<=PIANO[1];m++){ if(isBlack(m)) continue; const x0=FX(midiFreq(m-0.5)), x1=FX(midiFreq(m+0.5)); s+='<rect data-key="'+m+'" x="'+x0.toFixed(1)+'" y="'+ky+'" width="'+(x1-x0).toFixed(1)+'" height="'+kh+'" fill="#e6e6e6" stroke="#121212" stroke-width="0.8"/>'; if(m%12===0) s+='<text x="'+((x0+x1)/2).toFixed(1)+'" y="'+(ky+kh-6)+'" text-anchor="middle" font-size="8" fill="#555">C'+(m/12-1)+'</text>'; }
  for(let m=PIANO[0];m<=PIANO[1];m++){ if(!isBlack(m)) continue; const x0=FX(midiFreq(m-0.3)), x1=FX(midiFreq(m+0.3)); s+='<rect data-key="'+m+'" x="'+x0.toFixed(1)+'" y="'+ky+'" width="'+(x1-x0).toFixed(1)+'" height="'+(kh*0.6)+'" fill="#1a1a1a" stroke="#121212" stroke-width="0.8"/>'; }
  s+='<text x="'+FX(midiFreq(PIANO[0])).toFixed(1)+'" y="'+(ky-8)+'" font-size="10.5" fill="#9a9a9a">the piano, A0 to C8</text>';
  // the ranges
  const kinds={voice:'#f28cb0',strings:'#ffb02e',winds:'#6ee7f2',keys:'#9a9a9a'}; let ry=ky+kh+30;
  RANGES.filter(r=>r.k!=='piano').forEach((r,i)=>{ const y=ry+i*22, x0=FX(midiFreq(r.lo)), x1=FX(midiFreq(r.hi)), on=hot===r.k; s+='<g data-range="'+r.k+'" style="cursor:pointer"><rect x="'+x0.toFixed(1)+'" y="'+y+'" width="'+(x1-x0).toFixed(1)+'" height="14" rx="3" fill="'+kinds[r.kind]+'" opacity="'+(on?1:0.75)+'"/><text x="'+(x0-8).toFixed(1)+'" y="'+(y+11)+'" text-anchor="end" font-size="10.5" fill="'+(on?'#ffffff':'#c8c8c8')+'">'+esc(r.n)+'</text></g>'; });
  const H=ry+(RANGES.length-1)*22+30;
  // the marker and its harmonics
  const mx=FX(freq); s+='<g id="marker" style="cursor:ew-resize"><line x1="'+mx.toFixed(1)+'" y1="'+(N.y-2)+'" x2="'+mx.toFixed(1)+'" y2="'+H+'" stroke="#ff8c6a" stroke-width="1.5"/><circle cx="'+mx.toFixed(1)+'" cy="'+(N.y+38)+'" r="6" fill="#ff8c6a" stroke="#121212" stroke-width="1.5"/></g>';
  for(let k=2;k<=16;k++){ const f=k*freq; if(f>HEAR[1]) break; const x=FX(f); s+='<line x1="'+x.toFixed(1)+'" y1="'+(N.y+26)+'" x2="'+x.toFixed(1)+'" y2="'+(N.y+50)+'" stroke="#ff8c6a" stroke-width="'+(k<=4?1.5:1)+'" opacity="'+(k<=8?0.9:0.5)+'"/>'+(k<=8?'<text x="'+x.toFixed(1)+'" y="'+(N.y+62)+'" text-anchor="middle" font-size="9" fill="#ff8c6a">'+k+'</text>':''); }
  s+='<text x="'+N.x+'" y="'+(N.y+22)+'" font-size="11" fill="#ff8c6a">the marker, '+fmt(freq,freq<100?1:0)+' Hz; the ticks to its right are its harmonics, 2 to 16</text>';
  return {svg:s, h:H+10}; }

/* ---- the intervals ---- */
const R={cx:470,cy:330,r:230};
const angC=c=>c/1200*2*Math.PI-Math.PI/2;
const ptC=(r,c)=>[R.cx+r*Math.cos(angC(c)),R.cy+r*Math.sin(angC(c))];
function intervalsView(){ let s='';
  if(imode==='just'){ s+='<circle cx="'+R.cx+'" cy="'+R.cy+'" r="'+R.r+'" fill="none" stroke="#2b2b2b" stroke-width="1.5"/>';
    for(const iv of INTERVALS){ if(iv.s===12) continue; const c=cents(iv.r[0]/iv.r[1]), d=c-100*iv.s, on=hot==='i'+iv.s; const [ex,ey]=ptC(R.r,100*iv.s), [jx,jy]=ptC(R.r+30,c), [lx,ly]=ptC(R.r+62,100*iv.s), [nx,ny]=ptC(R.r-40,100*iv.s);
      s+='<g data-interval="'+iv.s+'" style="cursor:pointer"><line x1="'+ex.toFixed(1)+'" y1="'+ey.toFixed(1)+'" x2="'+jx.toFixed(1)+'" y2="'+jy.toFixed(1)+'" stroke="'+(Math.abs(d)>8?'#ff8c6a':'#9be564')+'" stroke-width="1.5"/>';
      s+='<circle cx="'+ex.toFixed(1)+'" cy="'+ey.toFixed(1)+'" r="'+(on?8:6)+'" fill="#9a9a9a" stroke="'+(on?'#ffffff':'#121212')+'" stroke-width="1.5"/><circle cx="'+jx.toFixed(1)+'" cy="'+jy.toFixed(1)+'" r="'+(on?8:6)+'" fill="'+(Math.abs(d)>8?'#ff8c6a':'#9be564')+'" stroke="'+(on?'#ffffff':'#121212')+'" stroke-width="1.5"/>';
      s+='<text x="'+lx.toFixed(1)+'" y="'+(ly+4).toFixed(1)+'" text-anchor="middle" font-size="10.5" fill="'+(on?'#ffffff':'#c8c8c8')+'">'+esc(iv.n)+'</text><text x="'+nx.toFixed(1)+'" y="'+(ny+4).toFixed(1)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">'+NAMES[iv.s]+(Math.abs(d)>=0.5?' '+(d>0?'\\u2212':'+')+Math.abs(d).toFixed(0)+'\\u00a2':'')+'</text></g>'; }
    s+='<text x="'+R.cx+'" y="'+(R.cy-8)+'" text-anchor="middle" font-size="12" fill="#e6e6e6">the octave as a ring, 1,200 cents</text><text x="'+R.cx+'" y="'+(R.cy+12)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">gray: the piano\\u2019s twelve equal steps</text><text x="'+R.cx+'" y="'+(R.cy+30)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">green and orange: the pure ratios, within and beyond 8 cents</text><text x="'+R.cx+'" y="'+(R.cy+48)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">inside: how far the piano is from pure</text>'; }
  else { const names=['C','G','D','A','E','B','F\\u266f','C\\u266f','G\\u266f','D\\u266f','A\\u266f','F','B\\u266f']; const r0=90, dr=11; let d='';
    for(let i=0;i<=12;i++){ const c=i*cents(1.5); const [x,y]=ptC(r0+i*dr,c); d+=(i?'L':'M')+x.toFixed(1)+','+y.toFixed(1); }
    // a smooth spiral: many small steps
    d=''; for(let t=0;t<=12;t+=0.05){ const c=t*cents(1.5); const [x,y]=ptC(r0+t*dr,c); d+=(t?'L':'M')+x.toFixed(1)+','+y.toFixed(1); }
    s+='<path d="'+d+'" fill="none" stroke="#3d444d" stroke-width="1.5"/>';
    for(let i=0;i<=12;i++){ const c=i*cents(1.5); const [x,y]=ptC(r0+i*dr,c), on=hot==='f'+i; const [lx,ly]=ptC(r0+i*dr+18,c); s+='<g data-fifth="'+i+'" style="cursor:pointer"><circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="'+(on?8:6)+'" fill="'+(i===12?'#ff8c6a':i===0?'#9be564':'#58a6ff')+'" stroke="'+(on?'#ffffff':'#121212')+'" stroke-width="1.5"/><text x="'+lx.toFixed(1)+'" y="'+(ly+4).toFixed(1)+'" text-anchor="middle" font-size="11" fill="'+(on?'#ffffff':'#c8c8c8')+'">'+names[i]+'</text></g>'; }
    const [cx0,cy0]=ptC(r0+12*dr+30,0), [cx1,cy1]=ptC(r0+12*dr+30,12*cents(1.5)); s+='<path d="M'+cx0.toFixed(1)+','+cy0.toFixed(1)+' A'+(r0+12*dr+30)+','+(r0+12*dr+30)+' 0 0 1 '+cx1.toFixed(1)+','+cy1.toFixed(1)+'" fill="none" stroke="#ff8c6a" stroke-width="3"/>';
    s+='<text x="'+(R.cx+8)+'" y="'+(R.cy-r0-12*dr-40)+'" font-size="11" fill="#ff8c6a">the comma, 23.46 cents</text>';
    s+='<text x="'+R.cx+'" y="'+(R.cy+R.r+40)+'" text-anchor="middle" font-size="11" fill="#9a9a9a">twelve pure fifths from C, each 701.955 cents, a turn of 7/12 and a little more; the twelfth misses the start</text>'; }
  return {svg:s, h:R.cy+R.r+80}; }

/* ---- the scales ---- */
function scalesView(){ let s=''; const sc=SCALES.find(x=>x.k===scale); const set=new Set(sc.steps); const x0=60, kw=(W-120)/15, ky=60, kh=220;
  let wi=0; for(let m=60;m<=84;m++){ if(isBlack(m)) continue; const x=x0+wi*kw, on=set.has((m-60)%12)&&m<84||(m===84&&set.has(0)); s+='<rect data-note="'+m+'" x="'+x.toFixed(1)+'" y="'+ky+'" width="'+kw.toFixed(1)+'" height="'+kh+'" fill="'+(on?'#58a6ff':'#e6e6e6')+'" stroke="#121212" stroke-width="1.5"/>'; s+='<text x="'+(x+kw/2).toFixed(1)+'" y="'+(ky+kh-12)+'" text-anchor="middle" font-size="11" fill="'+(on?'#0b1a2b':'#555')+'">'+NAMES[m%12]+(m===60||m===72||m===84?Math.floor(m/12)-1:'')+'</text>'; if(on){ const deg=sc.steps.indexOf((m-60)%12); s+='<text x="'+(x+kw/2).toFixed(1)+'" y="'+(ky+kh-30)+'" text-anchor="middle" font-size="10" fill="#0b1a2b">'+(m===84?1:deg+1)+'</text>'; } wi++; }
  wi=0; for(let m=60;m<84;m++){ if(!isBlack(m)){ wi++; continue; } const x=x0+wi*kw-kw*0.3, on=set.has((m-60)%12); s+='<rect data-note="'+m+'" x="'+x.toFixed(1)+'" y="'+ky+'" width="'+(kw*0.6).toFixed(1)+'" height="'+(kh*0.62)+'" fill="'+(on?'#58a6ff':'#1a1a1a')+'" stroke="#121212" stroke-width="1.5"/>'; s+='<text x="'+(x+kw*0.3).toFixed(1)+'" y="'+(ky+kh*0.62-10)+'" text-anchor="middle" font-size="9.5" fill="'+(on?'#0b1a2b':'#777')+'">'+NAMES[m%12]+'</text>'; }
  s+='<text x="'+x0+'" y="'+(ky-16)+'" font-size="12" fill="#e6e6e6">'+esc(sc.n)+' on C: '+sc.steps.map(v=>NAMES[v]).join(' ')+'</text>';
  const steps=sc.steps.map((v,i)=>i?v-sc.steps[i-1]:null).slice(1).concat([12-sc.steps[sc.steps.length-1]]);
  s+='<text x="'+x0+'" y="'+(ky+kh+30)+'" font-size="11.5" fill="#9a9a9a">steps: '+steps.map(v=>v===1?'half':v===2?'whole':v===3?'three semitones':v+' semitones').join(', ')+'</text>';
  return {svg:s, h:ky+kh+50}; }

/* ---- render and wiring ---- */
function render(){ const q=view==='notes'?notesView():view==='intervals'?intervalsView():scalesView(); el.innerHTML='<svg viewBox="0 0 '+W+' '+q.h+'" xmlns="http://www.w3.org/2000/svg" id="msvg"><rect width="'+W+'" height="'+q.h+'" fill="#121212"/>'+q.svg+'</svg>';
  document.getElementById('notesCtl').hidden=view!=='notes'; document.getElementById('intCtl').hidden=view!=='intervals'; document.getElementById('scaleCtl').hidden=view!=='scales'; document.getElementById('freqOut').textContent=fmt(freq,freq<100?1:0)+' Hz'; }
function home(){ if(view==='notes') showFreq(freq); else if(view==='intervals'){ if(imode==='just') showJust(); else showFifths(); } else showScale(scale); }
function setView(v){ view=v; hot=null; for(const b of document.querySelectorAll('#views button')) b.classList.toggle('on',b.dataset.v===v); render(); home(); }
document.getElementById('views').addEventListener('click',e=>{ const b=e.target.closest('button'); if(b) setView(b.dataset.v); });
document.getElementById('imodes').addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; imode=b.dataset.m; hot=null; for(const x of document.querySelectorAll('#imodes button')) x.classList.toggle('on',x===b); render(); home(); });
(function(){ const box=document.getElementById('scales'); let fam=''; let h=''; for(const s of SCALES){ if(s.fam!==fam){ fam=s.fam; h+='<span class="fam">'+esc(fam)+'</span>'; } h+='<button data-s="'+s.k+'"'+(s.k===scale?' class="on"':'')+'>'+esc(s.n)+'</button>'; } box.innerHTML=h;
  box.addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; scale=b.dataset.s; for(const x of box.querySelectorAll('button')) x.classList.toggle('on',x===b); render(); showScale(scale); }); })();
let dragging=false;
const svgPt=e=>{ const svg=document.getElementById('msvg'), b=svg.getBoundingClientRect(); return [(e.clientX-b.left)/b.width*W,(e.clientY-b.top)/b.height*svg.viewBox.baseVal.height]; };
function setFreq(x){ const t=Math.max(0,Math.min(1,(x-N.x)/N.w)); freq=N.f0*Math.pow(N.f1/N.f0,t); freq=+freq.toPrecision(4); render(); showFreq(freq); }
el.addEventListener('pointerdown',e=>{ if(view!=='notes') return; const [x,y]=svgPt(e); if(e.target.closest('[data-range]')) return; if(y>=N.y-20&&y<=N.y+200){ dragging=true; setFreq(x); e.preventDefault(); } });
el.addEventListener('pointermove',e=>{ if(!dragging) return; const [x]=svgPt(e); setFreq(x); });
window.addEventListener('pointerup',()=>{ dragging=false; });
el.addEventListener('pointerover',e=>{ if(dragging) return; const g=e.target.closest('[data-range],[data-interval],[data-fifth]'); if(!g) return;
  const k=g.hasAttribute('data-range')?g.getAttribute('data-range'):g.hasAttribute('data-interval')?'i'+g.getAttribute('data-interval'):'f'+g.getAttribute('data-fifth'); if(k===hot) return; hot=k; render();
  if(g.hasAttribute('data-range')) showRange(k); else if(g.hasAttribute('data-interval')) showInterval(+g.getAttribute('data-interval')); else showFifth(+g.getAttribute('data-fifth')); });
el.addEventListener('pointerleave',()=>{ if(hot){ hot=null; render(); home(); } });

render(); showFreq(freq);
window.__music=(q)=>{ const o={view,hot,freq,imode,scale,card:document.getElementById('numTxt').innerText,name:document.getElementById('nameTxt').innerText,body:document.getElementById('bodyTxt').innerText,
  keys:document.querySelectorAll('#msvg rect[data-key]').length, ranges:document.querySelectorAll('#msvg g[data-range]').length, lit:[...document.querySelectorAll('#msvg rect[data-note]')].filter(r=>r.getAttribute('fill')==='#58a6ff').map(r=>+r.getAttribute('data-note')),
  marker:(()=>{ const c=document.querySelector('#marker circle'); return c?+c.getAttribute('cx'):null; })()};
  if(q&&q.f!=null){ o.fx=FX(q.f); o.midi=freqMidi(q.f); }
  if(q&&q.midi!=null){ o.hz=midiFreq(q.midi); o.name=noteName(q.midi); const r=document.querySelector('#msvg rect[data-key="'+q.midi+'"]'); o.keyx=r?[+r.getAttribute('x'),+r.getAttribute('x')+ +r.getAttribute('width')]:null; }
  if(q&&q.interval!=null){ const iv=INTERVALS.find(x=>x.s===q.interval); o.cents=cents(iv.r[0]/iv.r[1]); const g=document.querySelector('#msvg g[data-interval="'+q.interval+'"]'); if(g){ const cs=g.querySelectorAll('circle'); o.dots=[...cs].map(c=>[+c.getAttribute('cx'),+c.getAttribute('cy')]); o.ptE=ptC(R.r,100*q.interval); o.ptJ=ptC(R.r+30,o.cents); } }
  return o; };
</script>
</body>
</html>
"""

html = (HTML.replace("__APACSS__", apa.CSS)
        .replace("__A4__", str(A4)).replace("__CAIR__", str(SPEED_OF_SOUND)).replace("__HEAR__", _js(list(HEARING))).replace("__PIANO__", _js(list(PIANO))).replace("__NAMES__", _js(NOTE_NAMES))
        .replace("__RANGES__", _js(ranges)).replace("__INTERVALS__", _js(intervals)).replace("__SCALES__", _js(scales))
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2).replace("__METHOD__", METHOD)
        .replace("__REFS__", apa.render(REFS)))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} B): {len(RANGES)} ranges, {len(INTERVALS)} intervals, {len(SCALES)} scales")
