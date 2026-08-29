#!/usr/bin/env python3
"""Show each page's Library column in its topbar.

The Library groups its Digital Concepts pages into columns (The Universe,
Earth, Life, Homo Sapiens, USA, Mexico) and an Abstractions row, but a
page's topbar only said "Library". This rewrites the Library anchor of
every mapped page to carry its column, so matter.html reads
"Library · The Universe", and the Science Fiction Concepts pages read
"Science Fiction · Concepts". The whole crumb stays one link.

Idempotent: pages already carrying their crumb are left alone. Run it
after any page rebuild (the builders write the plain anchor).

The Life column's five tree pages are not touched here: build_life.py
writes their crumb itself.

Usage: python3 add_crumbs.py
"""

from pathlib import Path

ROOT = Path(__file__).parent.parent

# Library column per page
COLUMNS = {
    "The Universe": ["energy.html", "matter.html", "universe.html",
                     "solar-system.html"],
    "Earth": ["earth-history.html", "earth.html", "orbit-sine.html",
              "moon.html", "day-night.html"],
    "Homo Sapiens": ["migration.html", "populous-countries.html"],
    "USA": ["us.html", "us-states.html", "us-cities.html"],
    "M&eacute;xico": ["mexico.html", "nueva-espana.html",
                      "norte-mexico.html", "el-terrero.html",
                      "valle-santa-maria.html", "ruta-namiquipa.html",
                      "cabalgata-villista.html", "linea-misiones.html"],
    "Abstractions": ["prime-spiral.html"],
}

# Science Fiction Concepts pages: the section anchor gains the group name
CONCEPTS = ["red-mars.html", "solar-system-2312.html", "space-elevator.html",
            "oneill-ring.html", "generation-starship.html"]

changed, skipped, missing = [], [], []

for column, pages in COLUMNS.items():
    for name in pages:
        f = ROOT / name
        if not f.exists():
            missing.append(name)
            continue
        html = f.read_text(encoding="utf-8")
        crumb = f"&larr; Library &middot; {column}"
        if crumb in html:
            skipped.append(name)
            continue
        done = False
        for plain in ("&larr; Library</a>", "← Library</a>"):
            if plain in html:
                html = html.replace(
                    plain, f"&larr; Library &middot; {column}</a>", 1)
                done = True
                break
        if done:
            f.write_text(html, encoding="utf-8")
            changed.append(name)
        else:
            missing.append(name + " (no plain Library anchor)")

for name in CONCEPTS:
    f = ROOT / name
    if not f.exists():
        missing.append(name)
        continue
    html = f.read_text(encoding="utf-8")
    if "Science Fiction &middot; Concepts" in html:
        skipped.append(name)
        continue
    done = False
    for plain in ("&larr; Science Fiction</a>", "← Science Fiction</a>"):
        if plain in html:
            html = html.replace(
                plain, "&larr; Science Fiction &middot; Concepts</a>", 1)
            done = True
            break
    if done:
        f.write_text(html, encoding="utf-8")
        changed.append(name)
    else:
        missing.append(name + " (no plain Science Fiction anchor)")

print(f"crumbed {len(changed)}: {', '.join(changed)}")
if skipped:
    print(f"already done {len(skipped)}: {', '.join(skipped)}")
if missing:
    print("ATTENTION " + "; ".join(missing))
