#!/usr/bin/env python3
"""Generate openings.html, the interactive openings-by-frequency explorer.

Usage: python3 build_openings.py <data_dir>
where data_dir holds opening_tree_394_nodes.csv and the four static SVGs
(used only to harvest opening names).
"""

import csv
import re
import sys
from pathlib import Path

from sanboard import board_for_line
from explorer_page import render_page

DATA_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
OUT = Path(__file__).parent.parent / "openings.html"

ALL_GAMES = 3_902_072  # 365chess.com Big Database, accessed August 2026
FAMS = {"e4": "#ff5c4d", "d4": "#3fa9f5", "Nf3": "#31d67a", "c4": "#ffb02e"}
FAMILY_SVGS = {
    "01_e4_kings_pawn.svg": "1.e4",
    "02_d4_queens_pawn.svg": "1.d4",
    "03_Nf3_reti.svg": "1.Nf3",
    "04_c4_english.svg": "1.c4",
}


def shade(hex_color, ply):
    f = max(0.30, 0.76 ** (ply - 1))
    v = int(hex_color[1:], 16)
    mix = lambda x: round(x * f + 18 * (1 - f))
    return f"rgb({mix(v >> 16 & 255)},{mix(v >> 8 & 255)},{mix(v & 255)})"


def main():
    rows = list(csv.DictReader(open(DATA_DIR / "opening_tree_394_nodes.csv")))
    nodes = []
    for r in rows:
        nodes.append({
            "l": r["line"], "p": int(r["ply"]), "g": int(r["games"]),
            "a": float(r["pct_of_all"]), "n": "",
        })
    for nd in nodes:
        if nd["p"] == 1:
            nd["par"] = -1
        else:
            cands = [j for j, m in enumerate(nodes)
                     if m["p"] == nd["p"] - 1 and nd["l"].startswith(m["l"] + " ")]
            if len(cands) != 1:
                raise SystemExit(f"no unique parent for {nd['l']}")
            nd["par"] = cands[0]
        nd["b"] = board_for_line(nd["l"])

    def fam(nd):
        while nd["par"] >= 0:
            nd = nodes[nd["par"]]
        return nd["l"][2:]

    for nd in nodes:
        nd["c"] = shade(FAMS[fam(nd)], nd["p"])

    # names from the static SVGs, matched by pct label + move token
    text_re = re.compile(
        r'<text x="([\d.]+)"[^>]*font-style="(normal|italic)"[^>]*opacity="([\d.]+)">([^<]+)</text>')
    named = 0
    for fname, family in FAMILY_SVGS.items():
        svg = (DATA_DIR / fname).read_text(encoding="utf-8")
        groups = []
        for x, style, _, content in text_re.findall(svg):
            x = float(x)
            if groups and abs(groups[-1]["x"] - x) < 0.5:
                groups[-1]["items"].append((style, content.strip()))
            else:
                groups.append({"x": x, "items": [(style, content.strip())]})
        for grp in groups:
            move = name = pct = None
            for style, content in grp["items"]:
                if content.endswith("%"):
                    pct = float(content.rstrip("%"))
                elif style == "italic":
                    name = content
                else:
                    move = content
            if pct is None or name is None:
                continue
            token = re.sub(r"^\d+\.(\.\.)?", "", move or "")
            cands = [nd for nd in nodes
                     if (nd["l"] == family or nd["l"].startswith(family + " "))
                     and round(nd["a"], 2) == pct
                     and (not token or nd["l"].split()[-1].endswith(token))]
            if len(cands) == 1:
                cands[0]["n"] = name
                named += 1
    print(f"named {named} nodes from the SVGs")

    start_board = "rnbqkbnrpppppppp" + "." * 32 + "PPPPPPPPRNBQKBNR"
    roots = sorted([nd for nd in nodes if nd["par"] < 0], key=lambda d: -d["g"])
    legend = [{"i": nodes.index(nd), "label": nd["l"] + (f" · {nd['n']}" if nd["n"] else ""),
               "color": nd["c"], "right": f"{nd['a']:.1f}%"} for nd in roots]

    config = {
        "title": "Openings by Frequency · Altazor",
        "heading": "Openings by Frequency",
        "lede": "The opening tree of 3.9 million games. Ring position is the move "
                "number, arc size is how often the line is played. A click on an arc "
                "zooms into that line, a click on the center backs out, and the arc "
                "under the cursor shows its position.",
        "note": "Arcs cover only the lines above the frequency cutoff of the 394-node "
                "tree; the gaps are everything rarer. Counts are from the 365chess.com "
                "Big Database, 3,902,072 games, accessed August 2026. Percentages are "
                "the share of all games.",
        "mode": "games",
        "total": ALL_GAMES,
        "allName": "all games",
        "rootLabel": "Start",
        "rootSub": "all openings",
        "rootLine": "Starting position",
        "rootBoard": start_board,
        "rootStat": "3,902,072 games · 365chess.com Big Database",
        "startCrumb": "Start",
        "legend": legend,
    }
    html = render_page(config, nodes)
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT} ({len(html)} bytes), {len(nodes)} nodes")


if __name__ == "__main__":
    main()
