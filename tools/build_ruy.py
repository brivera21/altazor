#!/usr/bin/env python3
"""Generate ruy-lopez.html from the static Ruy Lopez wheel SVG.

The SVG is the data source: the tree is reconstructed from arc geometry
(ring = ply, angular containment = parentage, angular span = share of
Ruy Lopez games) and the labels are re-attached to arcs by position,
fill color, or marker dot.

Usage: python3 build_ruy.py <data_dir>   (data_dir holds 05_ruy_lopez_wheel.svg)
"""

import math
import re
import sys
from pathlib import Path

from sanboard import board_for_line
from explorer_page import render_page

DATA_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
OUT = Path(__file__).parent.parent / "ruy-lopez.html"

SVG = (DATA_DIR / "05_ruy_lopez_wheel.svg").read_text(encoding="utf-8")
CX, CY = 3200.0, 3200.0
ROOT_LINE = "1.e4 e5 2.Nf3 Nc6 3.Bb5"
RUY_GAMES = 179_626
TWO_PI = 2 * math.pi


def ang(x, y):
    """Angle from center, 0 at 12 o'clock, clockwise."""
    return math.atan2(x - CX, CY - y) % TWO_PI


# ---- arcs ----
arc_re = re.compile(
    r'<path d="M([\d.]+),([\d.]+) A([\d.]+),[\d.]+ 0 \d \d ([\d.]+),([\d.]+) '
    r'L[\d.]+,[\d.]+ A([\d.]+)[^"]*" fill="(#[0-9a-f]+)"')
arcs = []
for m in arc_re.finditer(SVG):
    x0, y0, r_out, x1, y1, r_in, fill = *map(float, m.groups()[:6]), m.group(7)
    if fill == "#ffffff":
        continue  # below-cut strips
    a0, a1 = ang(x0, y0), ang(x1, y1)
    span = (a1 - a0) % TWO_PI
    RIN = [330, 670, 988, 1284, 1558, 1810, 2040, 2248, 2434, 2604, 2774, 2944, 3114]
    ring = 1 + min(range(len(RIN)), key=lambda i: abs(RIN[i] - r_in))
    arcs.append({"ring": ring, "a0": a0, "span": span, "fill": fill,
                 "r_in": r_in, "r_out": r_out, "tok": None, "n": "", "pct": None})


def mid(a):
    return (a["a0"] + a["span"] / 2) % TWO_PI


def contains(a, angle):
    return (angle - a["a0"]) % TWO_PI <= a["span"]


def arc_at(radius, angle):
    """Best arc for a point: ring containing (or nearest to) radius, angle inside."""
    best, bestscore = None, None
    for a in arcs:
        if not contains(a, angle):
            dang = min((angle - (a["a0"] + a["span"])) % TWO_PI,
                       (a["a0"] - angle) % TWO_PI)
        else:
            dang = 0.0
        if a["r_in"] - 5 <= radius <= a["r_out"] + 5:
            drad = 0.0
        else:
            drad = min(abs(radius - a["r_in"]), abs(radius - a["r_out"]))
        score = dang * 600 + drad
        if bestscore is None or score < bestscore:
            best, bestscore = a, score
    return best


# ---- interior label groups (share an x coordinate) ----
text_re = re.compile(
    r'<text x="([\d.]+)" y="([\d.]+)"[^>]*font-style="(normal|italic)"[^>]*'
    r'opacity="([\d.]+)">([^<]+)</text>')
groups = []
for x, y, style, _, content in text_re.findall(SVG):
    x, y = float(x), float(y)
    if groups and abs(groups[-1]["x"] - x) < 0.5:
        groups[-1]["items"].append((style, content.strip()))
    else:
        groups.append({"x": x, "y": y, "items": [(style, content.strip())]})

for grp in groups:
    move = name = pct = None
    for style, content in grp["items"]:
        if content.endswith("%"):
            pct = float(content.rstrip("%"))
        elif style == "italic":
            name = content
        else:
            move = content
    if move is None:
        continue
    radius = math.hypot(grp["x"] - CX, grp["y"] - CY)
    a = arc_at(radius, ang(grp["x"], grp["y"]))
    a["tok"], a["pct"] = move, pct
    a["lab"] = (grp["x"], grp["y"])
    if name:
        a["n"] = name

# ---- exterior color-coded labels (minor third moves) ----
ext_re = re.compile(
    r'<text x="([\d.]+)" y="([\d.]+)" text-anchor="(?:end|start)" font-size="\d+" '
    r'font-weight="700" fill="(#[0-9a-f]+)"(?: opacity="[^"]*")?>([^<]+)</text>')
ext = [(float(x), float(y), fill, c.strip()) for x, y, fill, c in ext_re.findall(SVG)]

by_fill = {}
for x, y, fill, content in ext:
    if fill == "#ffffff" or fill in ("#f5f6f8", "#8b93a7", "#6b7280"):
        continue
    by_fill.setdefault(fill, []).append(content)
for fill, contents in by_fill.items():
    cands = [a for a in arcs if a["fill"] == fill and a["tok"] is None]
    if len(cands) == 1:
        a = cands[0]
        for content in contents:
            if re.match(r"^\d", content):
                a["tok"] = content
            else:
                a["n"] = content

# ---- white exterior labels: bind through the nearest red marker dot ----
dots = [(float(x), float(y)) for x, y, r, fill in re.findall(
    r'<circle cx="([\d.]+)" cy="([\d.]+)" r="(1[02])" fill="(#ff5c4d)"', SVG)]
white_moves = [(x, y, c) for x, y, fill, c in ext
               if fill == "#ffffff" and re.match(r"^\d", c)]
for x, y, content in white_moves:
    dot = min(dots, key=lambda d: math.hypot(d[0] - x, d[1] - y))
    radius = math.hypot(dot[0] - CX, dot[1] - CY)
    a = arc_at(radius, ang(*dot))
    if a["tok"] is None:
        a["tok"] = content
        a["lab"] = (x, y)

# ---- big white variation names on the outer rim ----
big_names = [(float(x), float(y), c.strip()) for x, y, c in re.findall(
    r'<text x="([\d.]+)" y="([\d.]+)" text-anchor="start" font-size="92" '
    r'font-weight="700" fill="#ffffff">([^<]+)</text>', SVG)]
outer = [a for a in arcs if a["ring"] == max(x["ring"] for x in arcs)]
for x, y, content in big_names:
    # nearest by the arc's own label position (falls back to arc midpoint)
    def dist(a):
        if "lab" in a:
            return math.hypot(a["lab"][0] - x, a["lab"][1] - y)
        m = mid(a)
        r = (a["r_in"] + a["r_out"]) / 2
        return math.hypot(CX + r * math.sin(m) - x, CY - r * math.cos(m) - y)
    a = min(outer, key=dist)
    if not a["n"]:
        a["n"] = content

# ---- tree ----
arcs.sort(key=lambda a: (a["ring"], a["a0"]))
for a in arcs:
    if a["ring"] == 1:
        a["par"] = None
    else:
        def overlap(p):
            # overlap of [a0, a0+span] with p, on the circle
            start = (a["a0"] - p["a0"]) % TWO_PI
            return max(0.0, min(p["span"], start + a["span"]) - start) if start < p["span"] \
                else max(0.0, min(a["span"], (p["a0"] + p["span"] - a["a0"]) % TWO_PI)
                         if (p["a0"] - a["a0"]) % TWO_PI < a["span"] else 0.0)
        ring_up = [p for p in arcs if p["ring"] == a["ring"] - 1]
        cands = [p for p in ring_up if overlap(p) > 0]
        # prefer parents whose percentage can contain the child's (thin arcs
        # are drawn wider than their true share, so geometry alone misleads)
        eff = lambda p: p["pct"] if p["pct"] is not None else p["span"] / TWO_PI * 100
        if a["pct"] is not None:
            ok = [p for p in cands if eff(p) >= a["pct"] - 0.05]
            if ok:
                cands = ok
            elif cands:
                # no overlapping parent is large enough: fall back to the
                # nearest large-enough arc in the ring by angular distance
                big = [p for p in ring_up if eff(p) >= a["pct"] - 0.05]
                if big:
                    m = mid(a)
                    cands = [min(big, key=lambda p:
                                 min((m - (p["a0"] + p["span"])) % TWO_PI,
                                     (p["a0"] - m) % TWO_PI) if not contains(p, m) else 0.0)]
        if not cands:
            raise SystemExit(f"parent problem for arc ring {a['ring']} tok {a['tok']}")
        a["par"] = max(cands, key=overlap)

# the six dark-red rim dots mark the endpoints of the 9.h3 fan
fan_dots = [(float(x), float(y)) for x, y in re.findall(
    r'<circle cx="([\d.]+)" cy="([\d.]+)" r="12" fill="#923a34"', SVG)]
h3_arcs = [p for p in arcs if p["tok"] == "9.h3"]
if h3_arcs:
    last_ring = max(x["ring"] for x in arcs)
    for x, y in fan_dots:
        target = min((a for a in arcs if a["ring"] == last_ring),
                     key=lambda a: abs((ang(x, y) - mid(a) + math.pi) % TWO_PI - math.pi))
        target["par"] = h3_arcs[0]

missing = [a for a in arcs if a["tok"] is None]
if missing:
    raise SystemExit(f"{len(missing)} arcs without a move token")

nodes = []
index = {}
for a in arcs:
    line = (ROOT_LINE if a["par"] is None else index[id(a["par"])]["l"]) + " " + a["tok"]
    pct = a["pct"] if a["pct"] is not None else a["span"] / TWO_PI * 100
    nd = {"l": line, "g": a["span"], "a": pct, "n": a["n"],
          "par": -1 if a["par"] is None else nodes.index(index[id(a["par"])]),
          "b": board_for_line(line), "c": a["fill"]}
    nodes.append(nd)
    index[id(a)] = nd

roots = sorted([nd for nd in nodes if nd["par"] < 0], key=lambda d: -d["g"])
legend = [{"i": nodes.index(nd), "label": nd["l"].split(" ")[-1] +
           (f" · {nd['n']}" if nd["n"] else ""),
           "color": nd["c"], "right": f"{nd['a']:.1f}%"} for nd in roots]

config = {
    "title": "The Ruy Lopez · Altazor",
    "heading": "The Ruy Lopez",
    "lede": "Every branch of the Ruy Lopez from move 3 to move 9, following the "
            "Closed main line outward. Arc size is how often the line is played "
            "among 179,626 Ruy Lopez games. A click on an arc zooms into that "
            "line, a click on the center backs out, and the arc under the cursor "
            "shows its position.",
    "note": "The tree is thirteen plies deep and rings stop where a line was not "
            "followed further; gaps are moves below the cut. Counts are from the "
            "365chess.com Big Database, 3,902,072 games, accessed August 2026. "
            "Percentages are the share of the Ruy Lopez.",
    "mode": "pct",
    "total": TWO_PI,
    "allName": "Ruy Lopez games",
    "rootLabel": "3.Bb5",
    "rootSub": "Ruy Lopez",
    "rootLine": ROOT_LINE,
    "rootBoard": board_for_line(ROOT_LINE),
    "rootStat": "179,626 games · 4.6% of all games",
    "startCrumb": "3.Bb5",
    "legend": legend,
}
html = render_page(config, nodes)
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html)} bytes), {len(nodes)} nodes, "
      f"{sum(1 for n in nodes if n['n'])} named")
for nd in nodes:
    if nd["par"] < 0:
        print(f"  ring1: {nd['l'].split()[-1]:8s} {nd['a']:5.1f}%  {nd['n']}")
