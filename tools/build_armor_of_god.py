#!/usr/bin/env python3
"""Builds armor-of-god.html: the Library's solar-system.html with the novel's
solar system in 2500 laid over it.

The real solar system stays exactly as the Library page has it, so the page
is rebuilt from solar-system.html every time and picks up whatever that page
gains. On top of it go:

  * a title, a back link to Science Fiction, and a heading of its own;
  * Psyche and Hygiea, drawn in the belt like Ceres and Vesta;
  * the 2500 layer from tools/armor_of_god_2500.js: who holds each body (a
    colored ring, and a legend of five kinds of holder), the places and
    who controls what in each panel, the Sun zone with its Sails, the Gate,
    and the Lines.

Every insertion is made at an anchor that must occur exactly once in
solar-system.html, so a change there that moves an anchor stops the build
instead of producing a half-patched page.
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "solar-system.html"
OUT = ROOT / "armor-of-god.html"
LAYER = ROOT / "tools" / "armor_of_god_2500.js"

CSS = """
  /* the novel's solar system in 2500 */
  .aog-legend { display: flex; flex-wrap: wrap; justify-content: center; gap: 4px 14px; margin-bottom: 8px;
    font-size: 12px; }
  .aog-legend button.on { color: var(--text); text-decoration: underline; text-underline-offset: 3px; }
  .aog-legend .aog-yr { color: var(--dim); }
  .aog-legend button { background: none; border: 0; color: var(--dim); cursor: pointer; font: inherit;
    display: inline-flex; align-items: center; gap: 6px; padding: 0; }
  .aog-legend button:hover { color: var(--text); }
  .aog-legend i, #aog i { width: 9px; height: 9px; border-radius: 50%; display: inline-block; flex: none; }
  #aog { margin-top: 12px; padding: 10px 12px 12px; border-radius: 8px;
    background: rgba(233,185,73,0.07); border: 1px solid rgba(233,185,73,0.25); }
  #aog .aog-head { font-size: 10.5px; letter-spacing: 0.1em; text-transform: uppercase; color: #e9b949; margin-bottom: 6px; }
  #aog .aog-held { display: flex; gap: 8px; align-items: baseline; font-size: 13px; line-height: 1.4; margin-top: 3px; }
  #aog .aog-dt { font-size: 10.5px; color: var(--dim); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 10px; }
  #aog .aog-dd, #aog .aog-res, #aog .aog-note { font-size: 13px; line-height: 1.45; margin-top: 3px; }
  #aog .aog-note { color: var(--dim); }
  #aog .aog-place { font-size: 13px; line-height: 1.4; margin-top: 7px; }
  #aog .aog-pn { display: flex; justify-content: space-between; gap: 10px; }
  #aog .aog-pop { color: #e9b949; text-align: right; max-width: 58%; }
  #aog .aog-where, #aog .aog-short { color: var(--dim); font-size: 12px; }
"""

# (anchor, replacement); each anchor must appear exactly once
PATCHES = [
    ("<title>The Solar System · Altazor</title>", "<title>The Solar System of Armor of God · Altazor</title>"),
    ('<a href="library.html">&larr; Library &middot; The Universe</a>',
     '<a href="science-fiction.html">&larr; Science Fiction &middot; Armor of God</a>'),
    ("<h1>The Solar System</h1>",
     "<h1>The Solar System of Armor of God</h1>"),
    ('<div id="controls">\n  <div id="chips"></div>',
     '<div id="controls">\n  <div class="aog-legend legend" id="aogLegend"><span class="aog-yr">In 2500:</span></div>\n  <div id="chips"></div>'),
    ('  <div class="type" id="iType"></div>\n  <dl>', '  <div class="type" id="iType"></div>\n  <div id="aog" hidden></div>\n  <dl>'),
    ("</style>", CSS + "</style>"),
    # Psyche and Hygiea, in the belt
    ("  VESTA.region = BELT; CERES.region = BELT; PALLAS.region = BELT;",
     "__BODIES__\n  VESTA.region = BELT; CERES.region = BELT; PALLAS.region = BELT; PSYCHE.region = BELT; HYGIEA.region = BELT;"),
    ("const SMALL = [VESTA, CERES, PALLAS, PLUTO,", "const SMALL = [VESTA, CERES, PALLAS, PSYCHE, HYGIEA, PLUTO,"),
    ('Eris: ["#f4f3ef", "#8a8884"], Sedna: ["#b9573d", "#4a1c12"] };',
     'Eris: ["#f4f3ef", "#8a8884"], Sedna: ["#b9573d", "#4a1c12"],\n'
     '                       Psyche: ["#a9a59c", "#3b3833"], Hygiea: ["#77726a", "#26231f"] };'),
    ("      } else {\n        // Rheasilvia", "      } else if (b.name === \"Vesta\") {\n        // Rheasilvia"),
    # the panel: panel-only places, and the 2500 block under every body
    ("  function showInfo(o) {\n", "  function showInfo(o) {\n    if (o.aogOnly) { aogShowOnly(o); return; }\n"),
    ('    info.classList.add("show");\n    fitPanel();\n    info.scrollTop = 0;\n  }\n  function select(o) {',
     '    aogPanel(o);\n    info.classList.add("show");\n    fitPanel();\n    info.scrollTop = 0;\n  }\n  function select(o) {'),
    ("  function focusOn(obj) {\n    tracking = true;\n",
     "  function focusOn(obj) {\n    tracking = true;\n    if (obj.aogOnly) { aogFocus(obj); return; }\n"),
    ('      const lines = [mo.n + ", " + Math.round(2 * mo.r).toLocaleString("en-US") + " km across · " + mo.d]\n        .concat(wrapText(mo.t, 250));',
     '      const lines = [mo.n + ", " + Math.round(2 * mo.r).toLocaleString("en-US") + " km across · " + mo.d]\n        .concat(wrapText(mo.t, 250)).concat(aogMoonLines(mo.n));'),
    ("      if (orbDays > 0) hit = null;", "      hit = aogHit(mx, e.clientY, hit);\n      if (orbDays > 0) hit = null;"),
    ("    drawTrojans();\n    for (const p of PLANETS) drawPlanet(p);\n    drawCrowdLabel();\n    drawMoons();\n",
     "    aogDraw();\n    drawTrojans();\n    for (const p of PLANETS) drawPlanet(p);\n    drawCrowdLabel();\n    drawMoons();\n    aogDrawTop();\n"),
    ("      moons: moonState,", "      moons: moonState, aog: aogDbg(),"),
    ("  baseNote = modeNote.textContent;\n  resize();", "__LAYER__\n  baseNote = modeNote.textContent;\n  resize();"),
    ("Halley's Comet: JPL's orbital elements,",
     "Psyche and Hygiea: the published measurements as Wikipedia summarizes them, and NASA's schedule for the Psyche "
     "mission. Halley's Comet: JPL's orbital elements,"),
]


def main():
    html = SRC.read_text(encoding="utf-8")
    layer = LAYER.read_text(encoding="utf-8")
    bodies, rest = layer.split("//@@ LAYER\n")
    bodies = bodies.replace("//@@ BODIES\n", "").rstrip("\n")
    for a, b in PATCHES:
        n = html.count(a)
        if n != 1:
            raise SystemExit(f"anchor found {n} times, expected once: {a[:70]!r}")
        html = html.replace(a, b)
    html = html.replace("__BODIES__", bodies).replace("__LAYER__", rest.rstrip("\n"))
    if "—" in html:
        raise SystemExit("an em dash got in")
    OUT.write_text(html, encoding="utf-8")
    print(f"  armor-of-god.html  {len(html):,} B")


if __name__ == "__main__":
    main()
