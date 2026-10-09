#!/usr/bin/env python3
"""Builds future-films.html: stories set in the future, placed at the years
they are set, with the year each came out marked on the same row.

The data, and where it came from, is in tools/future_films_data.py. The
scale is linear in years; a second view zooms to the years before 2100,
where most of the stories crowd together.
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from future_films_data import FUTURES  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "future-films.html"
NOW = 2026


def payload():
    rows = []
    for title, medium, a, b, made, note, flags in FUTURES:
        f = flags.split()
        alt = next((x[4:] for x in f if x.startswith("alt=")), None)
        rows.append({"t": title, "m": medium, "a": a, "b": b, "made": made, "n": note,
                     "approx": "~" in f, "endApprox": "~end" in f, "on": "on" in f,
                     "span": "span" in f,
                     "alt": [int(v) for v in alt.split("-")] if alt else None})
    rows.sort(key=lambda r: (r["a"], r["b"] or r["a"]))
    return {"rows": rows, "now": NOW}


HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Films of the Future &middot; Altazor</title>
<meta name="description" content="Stories set in the future, placed at the years they are set, with the year each came out.">
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a; --line:#2b2b2b;
        --accent:#58a6ff; --film:#e9b949; --series:#3fb6ad; --book:#9b8cf0; --game:#e0684b; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
.wrap { max-width:1320px; margin:0 auto; padding:32px 16px 60px; }
header.site { border-top:4px solid var(--accent); padding-top:22px; margin-bottom:22px;
  display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }
.brand { font-weight:700; font-size:20px; letter-spacing:.1em; text-decoration:none; color:var(--text); }
.brand:hover { color:var(--accent); }
nav.site a { color:var(--muted); text-decoration:none; font-size:14px; margin-right:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 12px; font-size:26px; }
.bar { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-bottom:10px; }
button { font:inherit; font-size:13.5px; padding:6px 14px; border-radius:999px;
  border:1px solid var(--line); background:#1a1a1a; color:var(--text); cursor:pointer; }
button:hover { border-color:var(--accent); }
button.on { background:var(--accent); border-color:var(--accent); color:#0b1a2b; font-weight:600; }
.legend { display:flex; gap:6px 16px; flex-wrap:wrap; color:var(--muted); font-size:12.5px; margin:0 0 12px; }
.legend span { display:inline-flex; align-items:center; gap:6px; }
.legend i { display:inline-block; width:10px; height:10px; border-radius:50%; }
.legend i.tick { width:2px; height:11px; border-radius:0; background:#8a8a8a; }
.stage { display:grid; grid-template-columns:minmax(0,1fr) 320px; gap:20px; align-items:start; }
@media (max-width:1000px){ .stage { grid-template-columns:1fr; } }
#diagram > svg { width:100%; height:auto; display:block; background:#0d0d0d;
  border:1px solid #333; border-radius:6px; }
.row { cursor:pointer; }
.row:focus { outline:none; }
.row:focus .hl, .row.sel .hl { fill:rgba(88,166,255,0.12); }
.row:hover .hl { fill:rgba(255,255,255,0.05); }
.card { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:16px 18px;
  position:sticky; top:16px; }
#cTitle { font-size:19px; font-weight:650; font-style:italic; margin:0 0 2px; line-height:1.3; }
#cMeta { color:var(--muted); font-size:13px; margin-bottom:8px; }
#cSet { font-size:15px; margin-bottom:6px; }
#cNote { font-size:14.5px; color:#d4d4d4; margin:0; }
.caption { color:#c9c9c9; font-size:14.5px; max-width:75ch; margin:14px 0 8px; }
details.sources { font-size:13px; color:var(--muted); max-width:75ch; }
details.sources summary { cursor:pointer; }
footer.site { margin-top:40px; padding-top:16px; border-top:1px solid var(--line); font-size:13px; color:var(--muted); }
footer.site a { color:var(--muted); }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="film.html">&larr; Film</a></nav>
</header>
<h1>Films of the Future</h1>
<div class="bar" id="views">
  <button data-v="all" class="on">1950 to 2600</button>
  <button data-v="near">1950 to 2100</button>
</div>
<div class="legend">
  <span><i style="background:var(--film)"></i>Film</span>
  <span><i style="background:var(--series)"></i>Series</span>
  <span><i style="background:var(--book)"></i>Book</span>
  <span><i style="background:var(--game)"></i>Game</span>
  <span><i class="tick"></i>The year it came out</span>
</div>
<div class="stage">
  <div id="diagram"></div>
  <aside class="card diagram-text" aria-live="polite">
    <div id="cTitle"></div>
    <div id="cMeta"></div>
    <div id="cSet"></div>
    <p id="cNote"></p>
  </aside>
</div>
<p class="caption">Each row is a story at the years it is set. The gray tick is the year it came out, so the faint line from tick to story is how far ahead it looked. Hollow marks and dashed spans are estimates, and an arrow means the story runs on past what is drawn. The blue line is 2026.</p>
<details class="sources"><summary>Sources</summary>
The story years and the notes on how each is dated were compiled for this page from the works themselves, their tie-in material and their authors, as each row says. Release years are the first theatrical release, broadcast, game release or publication in book form.
</details>
<footer class="site"><a href="index.html">Altazor</a> &middot; <a href="film.html">Film</a></footer>
</div>
<script>
const DATA = __DATA__;
(() => {
  "use strict";
  const COLOR = { film: "#e9b949", series: "#3fb6ad", book: "#9b8cf0", game: "#e0684b" };
  const NAME = { film: "Film", series: "Series", book: "Book", game: "Game" };
  const VIEWS = { all: [1945, 2600, 50], near: [1945, 2100, 10] };
  const rows = DATA.rows;
  let view = "all", sel = -1;
  const box = document.getElementById("diagram");
  const NS = "http://www.w3.org/2000/svg";
  function el(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function setText(r) {
    const card = (id, t) => { document.getElementById(id).textContent = t; };
    if (!r) {
      card("cTitle", rows.length + " stories");
      card("cMeta", "Set from " + rows[0].a + " to " + rows[rows.length - 1].a);
      card("cSet", "A row's details show here."); card("cNote", "");
      return;
    }
    card("cTitle", r.t);
    card("cMeta", NAME[r.m] + ", " + r.made);
    let set;
    const ord = n => n + ({ 1: "st", 2: "nd", 3: "rd" }[n % 10] || "th");
    if (r.span) set = "Set in the " + (r.b - r.a > 20 ? ord(Math.floor(r.a / 100) + 1) + " century" : r.a + "s") + ", at a guess";
    else if (r.b) set = "Set " + (r.approx ? "from about " : "from ") + r.a + " to " + (r.endApprox ? "about " : "") + r.b;
    else set = "Set " + (r.approx ? "about " : "in ") + r.a;
    const ahead = r.a - r.made;
    const yrs = n => n + (n === 1 ? " year" : " years");
    if (ahead > 0) set += ", " + yrs(ahead) + " after it came out";
    else if (ahead < 0) set += ", " + yrs(-ahead) + " before it came out";
    else set += ", the year it came out";
    card("cSet", set);
    card("cNote", r.n);
  }
  function render() {
    const W = Math.max(320, box.clientWidth);
    const small = W < 640;
    const L = small ? 132 : 230, R = 18, T = 30, RH = small ? 20 : 22;
    const H = T + rows.length * RH + 14;
    const [v0, v1, step] = VIEWS[view];
    const x = y => L + (y - v0) / (v1 - v0) * (W - L - R);
    box.textContent = "";
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img",
      "aria-label": "Stories set in the future, by the years they are set" }, box);
    // the years
    for (let y = Math.ceil(v0 / step) * step; y <= v1; y += step) {
      const big = y % (step * 2) === 0 || step === 50;
      el("line", { x1: x(y), x2: x(y), y1: T - 6, y2: H - 8, stroke: "#222", "stroke-width": 1 }, svg);
      if (big && (!small || y % (step * 4) === 0 || step === 10 && y % 50 === 0)) {
        const t = el("text", { x: x(y), y: T - 12, "text-anchor": "middle", fill: "#8a8a8a",
          "font-size": 11 }, svg);
        t.textContent = y;
      }
    }
    // now
    el("line", { x1: x(DATA.now), x2: x(DATA.now), y1: T - 6, y2: H - 8, stroke: "#58a6ff",
      "stroke-width": 1.2, "stroke-dasharray": "3 3", opacity: 0.8 }, svg);
    rows.forEach((r, i) => {
      const yc = T + i * RH + RH / 2, c = COLOR[r.m];
      const g = el("g", { class: "row" + (i === sel ? " sel" : ""), tabindex: 0,
        "data-i": i, role: "button", "aria-label": r.t }, svg);
      el("rect", { class: "hl", x: 0, y: yc - RH / 2, width: W, height: RH, fill: "transparent" }, g);
      const lab = el("text", { x: L - 8, y: yc + 4, "text-anchor": "end", fill: "#dcdcdc",
        "font-size": small ? 11 : 12.5 }, g);
      lab.textContent = small && r.t.length > 20 ? r.t.slice(0, 19) + "…" : r.t;
      const clip = (y) => Math.max(L, Math.min(W - R, x(y)));
      // how far ahead it looked: the release tick, a faint line to the story
      const xm = clip(r.made), xa = clip(r.a);
      el("line", { x1: xm, x2: xa, y1: yc, y2: yc, stroke: c, "stroke-width": 1, opacity: 0.28 }, g);
      el("line", { x1: xm, x2: xm, y1: yc - 6, y2: yc + 6, stroke: "#9a9a9a", "stroke-width": 2 }, g);
      // a second dating the work itself gives
      if (r.alt) el("rect", { x: clip(r.alt[0]), y: yc - 4, width: Math.max(clip(r.alt[1]) - clip(r.alt[0]), 2),
        height: 8, rx: 3, fill: "none", stroke: c, "stroke-width": 1, opacity: 0.45 }, g);
      const past = r.a >= v1;
      if (past) {
        // beyond this view: an arrow at the edge, with the year
        const p = el("path", { d: `M${W - R - 9},${yc - 5} L${W - R},${yc} L${W - R - 9},${yc + 5} Z`, fill: c }, g);
        const t = el("text", { x: W - R - 13, y: yc + 4, "text-anchor": "end", fill: c, "font-size": 11 }, g);
        t.textContent = r.a;
        return;
      }
      if (r.b) {
        const x0 = x(r.a), x1 = clip(r.b);
        if (r.span) {
          el("rect", { x: x0, y: yc - 4.5, width: Math.max(x1 - x0, 3), height: 9, rx: 4,
            fill: c, "fill-opacity": 0.15, stroke: c, "stroke-width": 1.2, "stroke-dasharray": "3 2" }, g);
        } else if (r.endApprox) {
          const xf = clip(r.b - 25);
          el("rect", { x: x0, y: yc - 4.5, width: Math.max(xf - x0, 3), height: 9, rx: 4, fill: c }, g);
          el("rect", { x: xf, y: yc - 4.5, width: Math.max(x1 - xf, 2), height: 9, rx: 4,
            fill: c, "fill-opacity": 0.15, stroke: c, "stroke-width": 1.2, "stroke-dasharray": "3 2" }, g);
        } else {
          el("rect", { x: x0, y: yc - 4.5, width: Math.max(x1 - x0, 4), height: 9, rx: 4, fill: c }, g);
        }
      } else {
        el("circle", { cx: x(r.a), cy: yc, r: 5, fill: r.approx ? "#0d0d0d" : c, stroke: c,
          "stroke-width": r.approx ? 2 : 1 }, g);
      }
      if (r.b && r.b > v1)   // runs past the edge of this view
        el("path", { d: `M${W - R - 9},${yc - 5} L${W - R},${yc} L${W - R - 9},${yc + 5} Z`, fill: c }, g);
      if (r.on) {
        const xe = r.b ? clip(r.b) : x(r.a) + 6;
        if (xe < W - R - 14)
          el("path", { d: `M${xe + 4},${yc} L${xe + 22},${yc} M${xe + 16},${yc - 4} L${xe + 22},${yc} L${xe + 16},${yc + 4}`,
            stroke: c, "stroke-width": 1.6, fill: "none" }, g);
      }
    });
    svg.querySelectorAll(".row").forEach(g => {
      const pick = () => { sel = +g.dataset.i; setText(rows[sel]);
        svg.querySelectorAll(".row").forEach(o => o.classList.toggle("sel", o === g)); };
      g.addEventListener("click", pick);
      g.addEventListener("mouseenter", () => setText(rows[+g.dataset.i]));
      g.addEventListener("mouseleave", () => setText(sel >= 0 ? rows[sel] : null));
      g.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(); } });
      g.addEventListener("focus", () => setText(rows[+g.dataset.i]));
    });
    window.__dbg = { W, L, view, x: rows.map(r => r.a >= v1 ? null : x(r.a)), now: x(DATA.now), n: rows.length };
  }
  document.querySelectorAll("#views button").forEach(b => b.addEventListener("click", () => {
    view = b.dataset.v;
    document.querySelectorAll("#views button").forEach(o => o.classList.toggle("on", o === b));
    render();
  }));
  window.addEventListener("resize", render);
  setText(null);
  render();
})();
</script>
</body>
</html>
"""


def main():
    html = HTML.replace("__DATA__", json.dumps(payload(), ensure_ascii=False))
    if "—" in html:
        raise SystemExit("an em dash got in")
    OUT.write_text(html, encoding="utf-8")
    print(f"  future-films.html  {len(html):,} B  {len(FUTURES)} stories")


if __name__ == "__main__":
    main()
