"""Check every page against the site copy rule.

The rule, as agreed: a page opens with the thing itself. Descriptive prose goes
underneath it, and stays short.

  1. Nothing above the diagram reads as description. A heading, a date stamp,
     navigation and controls are fine; a sentence of prose is not.
  2. Each descriptive paragraph below the diagram runs 100 words or fewer, and
     the description as a whole runs 180 words or fewer. The comfortable target
     is 40 to 80 words per paragraph.
  3. The copy does not give orders. It says what the page does, not what the
     reader should do: "the wheel zooms", not "scroll to zoom". Third person
     for the whole site, English and Spanish alike.
  4. No em dashes anywhere.

Sources, citations and method notes are a different kind of text: they are
reference material, not description, so they sit below the description in a
.refs or .method block and are not counted against its budget. They still may
not appear above the diagram. Pages that are prose rather than diagrams, and
pages that are lists of links, are exempt from the length budget.

The check runs in a headless browser so it sees document order after any
scripted layout, not the order of the source file.

Usage: python3 verify_copy_rule.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Pages that are lists of links rather than diagrams. Their short standfirst is
# a landing tagline, not a description of a diagram, so rule 1 does not apply.
INDEXES = {"index.html", "library.html", "chess.html", "film.html",
           "science-fiction.html", "elsewhere.html", "notes.html"}

# Pages that are writing rather than a diagram with a caption.
PROSE = {"hello.html", "good-of-the-internet.html"}

# Reference material: cited below the description, outside its word budget.
# It may not appear above the diagram.
REFERENCE = (".refs", ".method", "#footnote")

# Furniture rather than prose: a date stamp, a legend, a control readout. These
# are allowed above the diagram and are never counted as description.
FURNITURE = (".stamp", ".legend", ".sub2", ".controls", "figcaption")

MAX_PARA = 100      # words in any single paragraph below the diagram
MAX_TAIL = 180      # words in the whole tail
MAX_ABOVE = 12      # words allowed in any text above the diagram
TARGET = (40, 80)   # comfortable band, reported but not enforced

# the first of these in the document is treated as "the diagram"
CONTENT = ("svg", "canvas", "table", "#tl", ".board", ".chessboard", ".grid",
           ".diagram", ".chart", "#map", ".map", ".cols", ".rows", ".poster",
           ".card", "#stage", ".stage", ".bars", ".timeline")

# Verbs that are giving the reader an order when they open a sentence or a
# clause. These have no plausible third-person reading in this site's copy, so
# a hit is a failure.
ORDERS = ("click", "hover", "scroll", "drag", "pinch", "tap", "press",
          "haz", "arrastra", "mueve", "presiona", "oprime", "desliza",
          "fíjate", "fijate", "acércate", "acercate", "pasa el", "pasa la")

# Verbs that are usually orders but have a legitimate third-person or noun
# reading, so a hit is reported for a human to read rather than failed. In
# Spanish the third-person singular and the informal imperative are the same
# word, which is why "acerca" and "ve" cannot be decided by pattern alone.
WATCH = ("use", "pick", "choose", "select", "zoom", "keep", "prefer", "put",
         "take", "avoid", "notice", "remember", "imagine", "watch", "look",
         "try", "elige", "escoge", "selecciona", "observa", "mira",
         "acerca", "aleja", "prueba", "recuerda", "toca", "abre", "busca")


def order_re(words):
    """Match one of `words` opening a sentence or a coordinated clause."""
    return re.compile(
        r"(?:(?<=^)|(?<=[.;:!?]\s)|(?<=[.;:!?]\s\s)|(?<=,\sy\s)|"
        r"(?<=,\sand\s)|(?<=;\s))(" + "|".join(words) + r")\b\s+\w+",
        re.IGNORECASE)


ORDER_RE, WATCH_RE = order_re(ORDERS), order_re(WATCH)

JS = """([sel, ref, furn]) => {
  let diagram = null;
  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
  while (walk.nextNode()) {
    const el = walk.currentNode;
    if (sel.some(s => el.matches(s))) { diagram = el; break; }
  }
  const words = t => (t || '').trim().split(/\\s+/).filter(Boolean).length;
  const out = {diagram: diagram ? diagram.tagName + (diagram.className
      ? '.' + String(diagram.className).split(' ')[0] : '') : null,
    above: [], below: [], reference: 0};
  for (const p of document.querySelectorAll('p')) {
    const t = p.innerText.trim();
    if (!t) continue;
    if (diagram && diagram.contains(p)) continue;
    const n = words(t);
    if (furn.some(s => p.matches(s) || p.closest(s))) continue;
    const isRef = ref.some(s => p.matches(s) || p.closest(s));
    const above = diagram && (diagram.compareDocumentPosition(p) & 2);
    if (isRef && !above) { out.reference += n; continue; }
    out[above ? 'above' : 'below'].push({n, t: t.slice(0, 90), cls: p.className});
  }
  return out;
}"""

# All visible copy, including labels, legends and hint text, but not the data
# itself: a table of country names is not prose and cannot give an order.
COPY_JS = """() => {
  const skip = new Set(['SCRIPT', 'STYLE', 'TABLE']);
  const out = [];
  const walk = el => {
    for (const c of el.childNodes) {
      if (c.nodeType === 3) { const t = c.textContent.trim(); if (t) out.push(t); }
      else if (c.nodeType === 1 && !skip.has(c.tagName)
               && c.id !== 'filmList' && !c.closest('table')) walk(c);
    }
  };
  walk(document.body);
  return out;
}"""

# Pages ported whole from the lab site's Digital Concepts keep that
# library's fuller notes and are not held to the Altazor copy rule.
PORTED = {"oneill-ring.html", "generation-starship.html",
          "hard-scifi-timeline.html"}
pages = sorted(p.name for p in ROOT.glob("*.html") if p.name not in PORTED)
fails, notes = [], []

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("playwright is required for this check")
    sys.exit(2)

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1200, "height": 1400})
    for name in pages:
        f = ROOT / name
        html = f.read_text(encoding="utf-8")
        if "—" in html:
            body = re.sub(r"<script[\s\S]*?</script>", "", html)
            if "—" in body:
                fails.append(f"{name}: em dash in page copy")
        pg.goto(f.as_uri())
        pg.wait_for_timeout(450)
        for frag in pg.evaluate(COPY_JS):
            if len(frag.split()) < 3:
                continue
            for m in ORDER_RE.finditer(frag):
                fails.append(f"{name}: the copy gives an order: "
                             f"{frag[max(0, m.start() - 25):m.end() + 30]!r}")
            for m in WATCH_RE.finditer(frag):
                notes.append(f"{name}: reads like an order, check it: "
                             f"{frag[max(0, m.start() - 25):m.end() + 30]!r}")

        got = pg.evaluate(JS, [list(CONTENT), list(REFERENCE), list(FURNITURE)])
        above = [a for a in got["above"] if a["n"] > MAX_ABOVE]
        tail = sum(b["n"] for b in got["below"])
        longest = max((b["n"] for b in got["below"]), default=0)
        exempt = name in INDEXES or name in PROSE

        if name not in INDEXES:
            for a in above:
                fails.append(f"{name}: {a['n']} words above the diagram: "
                             f"{a['t'][:60]!r}")
            if got["diagram"] is None and name not in PROSE:
                notes.append(f"{name}: no diagram element found, rule 1 skipped")
        if not exempt:
            for b in got["below"]:
                if b["n"] > MAX_PARA:
                    fails.append(f"{name}: a descriptive paragraph runs "
                                 f"{b['n']} words (limit {MAX_PARA}): "
                                 f"{b['t'][:60]!r}")
            if tail > MAX_TAIL:
                fails.append(f"{name}: the description runs {tail} words "
                             f"(limit {MAX_TAIL})")

        # short is never a problem; only flag paragraphs above the band
        band = "*" if not exempt and longest > TARGET[1] else " "
        print(f"  {name:26} diagram {str(got['diagram'] or '-'):14} "
              f"above {len(got['above']):2}  description {tail:4}w in "
              f"{len(got['below']):2} para, longest {longest:3}{band} "
              f" reference {got['reference']:4}w"
              + ("   (exempt)" if exempt else ""))
    br.close()

print()
for n in notes:
    print("note", n)
if fails:
    print()
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print(f"all pages pass: nothing over {MAX_ABOVE} words above the diagram, "
      f"no descriptive paragraph over {MAX_PARA} words, no description "
      f"over {MAX_TAIL}")
print(f"(* marks a page with a paragraph over {TARGET[1]} words, the top of "
      f"the {TARGET[0]} to {TARGET[1]} word comfort band)")
