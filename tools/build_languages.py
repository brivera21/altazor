#!/usr/bin/env python3
"""Generate languages.html: the tree of the world's languages.

One collapsible cladogram over Glottolog's classification, from the root
through 238 families to every language it lists. A family opens into its
branches; a search box finds a language and opens the path down to it.

Data: tools/data/languages.json (build_languages_data.py).

Usage: python3 build_languages.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = Path(__file__).parent / "data"

NOTE1 = ("The tree is Glottolog's classification, which admits a relation "
         "only where the regular sound correspondences have been shown. "
         "Deeper groupings that circulate in the literature, Altaic, "
         "Nostratic, Amerind among them, are not in it.")

NOTE2 = ("A node holding branches opens and closes when clicked, and the "
         "one under the cursor fills the card. Tips are languages, not "
         "dialects, and a language here is a lineage rather than a state "
         "or a script: Hindi and Urdu part, Chinese does not hold together. "
         "A tip's color is Glottolog's endangerment status, green through "
         "red to the gray of a language no longer spoken. Sign languages, "
         "pidgins, mixed and designed languages sit apart, since their "
         "history is not descent from a parent.")

REFS = [
    ("Hammarström, H., Forkel, R., Haspelmath, M., & Bank, S. 2025. "
     "Glottolog 5.2.1. Leipzig: Max Planck Institute for Evolutionary "
     "Anthropology.", "https://glottolog.org"),
    ("The classification, names, macroareas and codes come from the "
     "Glottolog CLDF release, CC-BY 4.0.",
     "https://github.com/glottolog/glottolog-cldf"),
    ("Language codes are ISO 639-3, maintained by SIL International.",
     "https://iso639-3.sil.org/"),
]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Languages · Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; --hl:#31d67a; }
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
.bar { display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-bottom:12px; }
.bar input { background:#0d0d0d; color:var(--text); border:1px solid var(--line);
  border-radius:999px; padding:7px 14px; font-size:13.5px; width:250px; }
.bar input:focus { outline:none; border-color:var(--accent); }
.bar button { background:transparent; color:var(--text); border:1px solid var(--line);
  border-radius:999px; padding:6px 14px; font-size:13px; cursor:pointer; }
.bar button:hover { border-color:var(--accent); color:var(--accent); }
#legend { display:flex; gap:14px; flex-wrap:wrap; margin-bottom:10px;
  color:var(--muted); font-size:12px; align-items:center; }
#legend span { display:flex; gap:5px; align-items:center; }
#legend i { width:9px; height:9px; border-radius:50%; display:inline-block; }
#hits { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:10px; }
#hits button { background:#0d0d0d; color:var(--accent); border:1px solid var(--line);
  border-radius:999px; padding:4px 11px; font-size:12.5px; cursor:pointer; }
#hits button:hover { border-color:var(--accent); }
#hits .none { color:var(--muted); font-size:12.5px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; max-height:78vh; overflow-y:auto;
  border:1px solid var(--line); border-radius:12px; background:#151515; }
#diagram svg { width:100%; height:auto; display:block; user-select:none; }
.side { flex:0 0 300px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:16px; }
#nameTxt { font-weight:700; font-size:17px; }
#cntTxt { color:var(--hl); font-size:13px; margin-top:2px; }
#bodyTxt { color:var(--muted); font-size:13.5px; line-height:1.55; margin-top:8px; }
#pathTxt { color:var(--muted); font-size:12.5px; margin-top:10px; }
#srcTxt { color:var(--muted); font-size:12px; margin-top:10px;
  border-top:1px solid var(--line); padding-top:8px; }
#srcTxt a { color:var(--accent); }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.refs { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.refs p { margin:0 0 8px; overflow-wrap:anywhere; }
.refs a { color:var(--accent); }
h2.refh { font-size:15px; margin:26px 0 8px; }
@media (max-width:900px){ .stage{flex-direction:column;} .side{position:static; width:100%;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library &middot; Homo Sapiens</a> <a href="migration.html">Homo Sapiens Migration</a> <a href="hominins.html">Hominins</a></nav>
</header>
<h1>Languages</h1>
<div class="bar">
  <input id="q" type="search" placeholder="Find a language or family" autocomplete="off">
  <button id="bTop">Families only</button>
  <button id="bBig">Open the ten largest</button>
</div>
<div id="legend"></div>
<div id="hits"></div>
<div class="stage">
  <div id="diagram"></div>
  <div class="side"><div class="card">
    <div id="nameTxt">A group under the cursor lands here</div>
    <div id="cntTxt"></div>
    <div id="bodyTxt"></div>
    <div id="pathTxt"></div>
    <div id="srcTxt"></div>
  </div></div>
</div>
<p class="note">__NOTE1__</p>
<p class="note" style="border-top:none; padding-top:0;">__NOTE2__</p>
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</div>
<script>
const ROOT=__DATA__;
const el=document.getElementById('diagram');
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
const fmt=x=>x.toLocaleString('en-US');
// Glottolog's Agglomerated Endangerment Status, 1 to 6
const AES=['not endangered','threatened','shifting','moribund',
  'nearly extinct','no longer spoken'];
const AESC=['#31d67a','#ffd24d','#ff9440','#f4713f','#ef5350','#6b7280'];
const vc=n=>n.v?AESC[n.v-1]:'#58a6ff';
document.getElementById('legend').innerHTML=
  AES.map((t,i)=>'<span><i style="background:'+AESC[i]+'"></i>'+t+'</span>').join('')
  +'<span><i style="background:#58a6ff"></i>not assessed</span>';

// every node gets an id, a parent and the number of languages under it
let idc=0; const byId={}, ALL=[];
(function prep(n,parent){
  n.id='n'+(idc++); n.p=parent; byId[n.id]=n; ALL.push(n);
  if(n.k){ n.k.forEach(c=>prep(c,n)); n.t=n.k.reduce((a,c)=>a+c.t,0); }
  else n.t=1;
})(ROOT,null);

// closed nodes keep their branches folded away; the root and its
// children start open so the families are the first thing on screen
const open=new Set([ROOT.id]);

// an indented tree: every open node keeps its own row, its branches
// below it and one step to the right
const RS=23, PADT=16, PADB=16, PADL=16, PADR=340, IND=20, W=1010;
let rows=[], maxd=0;
function layout(){
  rows=[]; maxd=0;
  (function walk(n,d){
    n.depth=d; n.y=PADT+RS*(rows.length+0.5); rows.push(n);
    maxd=Math.max(maxd,d);
    if(n.k&&open.has(n.id)) n.k.forEach(c=>walk(c,d+1));
  })(ROOT,0);
  return PADT+PADB+RS*rows.length;
}
const X=d=>PADL+d*IND;

function draw(n){
  const x=X(n.depth), isOpen=n.k&&open.has(n.id), leaf=!n.k;
  let s='';
  if(isOpen){
    const x1=X(n.depth+1), last=n.k[n.k.length-1];
    s+='<path d="M'+x+','+(n.y+7)+' V'+last.y+'" fill="none" stroke="#3d444d" stroke-width="1.3"/>';
    for(const c of n.k)
      s+='<path d="M'+x+','+c.y+' H'+(x1-6)+'" fill="none" stroke="#3d444d" stroke-width="1.3"/>';
  }
  const col=leaf?'#c9d1d9':(isOpen?'#9a9a9a':'#e6e6e6');
  s+='<g data-id="'+n.id+'" style="cursor:'+(leaf?'default':'pointer')+'">'
    +(n.id===pinned?'<circle cx="'+x+'" cy="'+n.y+'" r="9" fill="none" stroke="var(--accent)" stroke-width="1.5"/>':'')
    +'<rect x="'+(x-10)+'" y="'+(n.y-11)+'" width="'+(W-PADL-x)+'" height="'+RS+'" fill="'+(n.id===pinned?'#1d2126':'transparent')+'"/>'
    // a branch is a square, a language a circle, so the vitality
    // colours below belong to the tips alone
    +(leaf
      ? '<circle cx="'+x+'" cy="'+n.y+'" r="4" fill="'+vc(n)+'" stroke="'+vc(n)+'" stroke-width="1.5"/>'
      : '<rect x="'+(x-4.5)+'" y="'+(n.y-4.5)+'" width="9" height="9" rx="1.5" fill="'+(isOpen?'#151515':'#8b949e')+'" stroke="#8b949e" stroke-width="1.5"/>')
    +'<text x="'+(x+11)+'" y="'+(n.y+4.5)+'" font-size="'+(leaf?12.5:13)+'" font-weight="'+(leaf?400:600)+'" fill="'+col+'">'+esc(n.n)
    +(leaf?(n.e?' <tspan fill="#6b7280" font-size="10.5">'+esc(n.e)+'</tspan>':'')
          :' <tspan fill="#6b7280" font-size="11" font-weight="400">'+fmt(n.t)+'</tspan>')
    +'</text></g>';
  if(isOpen) for(const c of n.k) s+=draw(c);
  return s;
}
function render(){
  const H=layout();
  el.innerHTML='<svg viewBox="0 0 '+W+' '+H+'" xmlns="http://www.w3.org/2000/svg" id="treesvg">'+draw(ROOT)+'</svg>';
}

let current=ROOT.id, pinned=null;
function pathOf(n){ const out=[]; let p=n.p; while(p){ out.unshift(p.n); p=p.p; } return out; }
function show(id){
  const n=byId[id]; if(!n) return;
  current=id;
  document.getElementById('nameTxt').textContent=n.n;
  let cnt;
  if(n.k){
    let gone=0;(function w(x){ if(x.k) x.k.forEach(w); else if(x.v===6) gone++; })(n);
    cnt=fmt(n.t)+(n.t===1?' language':' languages')
      +(gone?', '+fmt(gone)+' no longer spoken':'');
  } else cnt=n.v?AES[n.v-1]:'vitality not assessed';
  const ct=document.getElementById('cntTxt');
  ct.textContent=cnt; ct.style.color=n.k?'var(--hl)':vc(n);
  document.getElementById('bodyTxt').textContent=n.b||'';
  const path=pathOf(n);
  document.getElementById('pathTxt').textContent=path.length?path.join(' \\u203a '):'';
  const src=document.getElementById('srcTxt');
  const bits=[];
  if(!n.k&&n.a) bits.push(n.a);
  if(n.e) bits.push('ISO 639-3: '+n.e);
  src.innerHTML=(bits.length?esc(bits.join(' \\u00b7 '))+'<br>':'')
    +(n.g?'<a href="https://glottolog.org/resource/languoid/id/'+n.g+'">Glottolog '+n.g+'</a>':'Glottolog 5.2.1');
}
function openTo(n){ let p=n.p; while(p){ open.add(p.id); p=p.p; } }

el.addEventListener('pointerover',e=>{
  if(pinned) return;
  const g=e.target.closest('[data-id]');
  if(g) show(g.getAttribute('data-id'));
});
el.addEventListener('click',e=>{
  const g=e.target.closest('[data-id]');
  if(!g){ pinned=null; render(); return; }
  const id=g.getAttribute('data-id'), n=byId[id];
  pinned=id; show(id);
  if(n.k){ if(open.has(id)) open.delete(id); else open.add(id); }
  render();
});

// search: the matching languages and families, each opening its own path
const hits=document.getElementById('hits'), q=document.getElementById('q');
const fold=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
function search(){
  const v=fold(q.value.trim());
  hits.innerHTML='';
  if(v.length<2) return;
  const found=ALL.filter(n=>fold(n.n).includes(v)
    ||(n.e&&n.e.toLowerCase()===v)).slice(0,40);
  if(!found.length){ hits.innerHTML='<span class="none">nothing by that name</span>'; return; }
  for(const n of found){
    const b=document.createElement('button');
    b.textContent=n.n+(n.k?' ('+fmt(n.t)+')':'');
    b.onclick=()=>{
      openTo(n); if(n.k) open.add(n.id);
      pinned=n.id; show(n.id); render();
      const c=el.querySelector('[data-id="'+n.id+'"] circle');
      if(c) c.scrollIntoView({block:'center'});
    };
    hits.appendChild(b);
  }
}
q.addEventListener('input',search);
document.getElementById('bTop').onclick=()=>{
  open.clear(); open.add(ROOT.id); pinned=null; render(); el.scrollTop=0;
};
document.getElementById('bBig').onclick=()=>{
  open.clear(); open.add(ROOT.id);
  ROOT.k.slice(0,10).forEach(n=>open.add(n.id));
  pinned=null; render(); el.scrollTop=0;
};

render();
show(ROOT.id);
window.__lang=()=>({nodes:ALL.length, langs:ROOT.t, families:ROOT.k.length,
  rows:rows.length, depth:maxd, open:open.size, pinned, current});
</script>
</body>
</html>
"""


def main():
    data = json.loads((DATA / "languages.json").read_text(encoding="utf-8"))
    refs = "\n".join(f'<p>{t}\n<a href="{u}">{u}</a></p>' for t, u in REFS)
    html = (HTML.replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2)
            .replace("__REFS__", refs)
            .replace("__DATA__", json.dumps(data, separators=(",", ":"),
                                            ensure_ascii=False)))
    p = ROOT / "languages.html"
    p.write_text(html, encoding="utf-8")

    def count(n):
        return 1 if "k" not in n else sum(count(c) for c in n["k"])
    print(f"wrote {p} ({len(html):,} B): {len(data['k'])} top nodes, "
          f"{count(data):,} languages")


if __name__ == "__main__":
    main()
