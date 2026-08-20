"""Check the three population pages after any rebuild.

Structure: no paragraph of explanation at the top any more (Brian moved it to
the bottom on 2026-08-17), the title is followed by the snapshot stamp, and the
closing headings run How to read this, Notes, References.

Numbers: ranks run 1..N without a gap, populations fall, every green lead is
exactly the difference to the row below (the last row compares against the
named runner-up where the list is a cut of a longer ranking), the totals row
adds up, and every row carries one inline bar whose colour agrees with its sign.

Flags: one per row, from flagcdn or drawn inline, never with loading="lazy" or
srcset, which stopped them loading at all in Brian's Chrome.

Usage: python3 verify_population_pages.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PAGES = [
    dict(file="us-states.html", title="Every State by Population",
         last_lead=False, diverging=True, explainer=True),
    dict(file="us-cities.html", title="Most Populous Cities in the United States",
         last_lead=True, diverging=True, explainer=True),
    # Earth Right Now lists every country, so nothing follows the last row and
    # Brian dropped its explainer entirely.
    dict(file="populous-countries.html", title="Earth Right Now",
         last_lead=False, diverging=False, explainer=False),
]
fails = []


def num(s):
    return int(s.replace(",", "").replace("+", "").replace("−", "-"))


def check(page):
    name = page["file"]
    h = (ROOT / name).read_text(encoding="utf-8")
    bad = fails.append

    # ---- structure ----
    if 'class="lede"' in h:
        bad(f"{name}: a lede paragraph is still at the top")
    m = re.search(r"<h1>(.*?)</h1>\s*<p class=\"stamp\">", h, re.S)
    if not m:
        bad(f"{name}: the title is not followed directly by the snapshot stamp")
    elif m.group(1).strip() != page["title"]:
        bad(f"{name}: title reads {m.group(1).strip()!r}")
    heads = re.findall(r"<h2>(.*?)</h2>", h)
    tail = (["How to read this"] if page["explainer"] else []) + ["Notes", "References"]
    if heads[-len(tail):] != tail:
        bad(f"{name}: the closing headings are {heads[-len(tail):]}, expected {tail}")
    if "—" in h:
        bad(f"{name}: contains an em dash")

    if page["explainer"]:
        # the explanation must have survived the move, not just vanished
        body = h.split("<h2>How to read this</h2>", 1)
        if len(body) < 2 or len(re.sub(r"<[^>]+>", "", body[1].split("<h2>")[0])) < 200:
            bad(f"{name}: the How to read this block is missing or too short")
    elif "How to read this" in h:
        bad(f"{name}: still carries a How to read this block")

    # ---- ranked rows ----
    rows = re.findall(r"<tr>\s*<td class=\"rank\">(\d+)</td>(.*?)</tr>", h, re.S)
    if not rows:
        bad(f"{name}: no ranked rows found")
        return
    pops, leads = [], []
    for i, (rank, cells) in enumerate(rows, start=1):
        if int(rank) != i:
            bad(f"{name}: rank {rank} found where {i} expected")
        p = re.search(r"<td class=\"num pop\">([\d,]+)", cells)
        if not p:
            bad(f"{name}: row {i} has no population")
            continue
        pops.append(num(p.group(1)))
        g = re.search(r'<span class="gap">\(\+([\d,]+)\)</span>', cells)
        leads.append(num(g.group(1)) if g else None)

        flags = re.findall(r'<img class="flag"[^>]*>', cells) + \
            re.findall(r'<svg class="flag"', cells)
        if len(flags) != 1:
            bad(f"{name}: row {i} carries {len(flags)} flags")
        for f in flags:
            if "loading=" in f or "srcset" in f:
                bad(f"{name}: row {i} flag uses loading or srcset")
            if isinstance(f, str) and f.startswith("<img") and "flagcdn.com" not in f:
                bad(f"{name}: row {i} flag is not from flagcdn")
        if len(re.findall(r"<svg class=\"(?:chg|flow)\"", cells)) != 1:
            bad(f"{name}: row {i} does not have exactly one inline bar")

        if page["diverging"]:
            delta = re.search(r"<td class=\"num\">(−?[\d,]+)</td>\s*$",
                              cells.strip())
            svg = re.search(r"<svg class=\"chg\".*?</svg>", cells, re.S)
            if delta and svg:
                down = "−" in delta.group(1)
                s = svg.group(0)
                if down and "#d55181" not in s:
                    bad(f"{name}: row {i} lost people but is not drawn as a decline")
                if not down and "#3987e5" not in s:
                    bad(f"{name}: row {i} grew but is not drawn as growth")
                xs = [float(x) for x in re.findall(r'<rect x="([\d.]+)"', s)]
                if xs and down and max(xs) > 118.01:
                    bad(f"{name}: row {i} decline bar crosses the zero line")
                if xs and not down and min(xs) < 117.99:
                    bad(f"{name}: row {i} growth bar crosses the zero line")

    for i in range(len(pops) - 1):
        if pops[i] < pops[i + 1]:
            bad(f"{name}: row {i+1} is smaller than row {i+2}")
        if leads[i] is None:
            bad(f"{name}: row {i+1} has no lead figure")
        elif leads[i] != pops[i] - pops[i + 1]:
            bad(f"{name}: row {i+1} lead is {leads[i]:,}, "
                f"expected {pops[i]-pops[i+1]:,}")
    if page["last_lead"] and leads[-1] is None:
        bad(f"{name}: the last row should compare against the runner-up")
    if not page["last_lead"] and leads[-1] is not None:
        bad(f"{name}: the last row should have no lead figure")

    # Totals: a page may be split into blocks of ten, each with its own totals
    # row, but the LAST one has to be the grand total (Brian asked for that
    # explicitly: "at the bottom it should be the total not just the next 10").
    seen, totals = 0, []
    for tbl in re.findall(r"<table.*?</table>", h, re.S):
        block = [num(p) for p in
                 re.findall(r"<td class=\"num pop\">([\d,]+)", tbl)]
        t = re.search(r'<tr class="total">.*?([\d,]{7,}).*?</tr>', tbl, re.S)
        if not block or not t:
            continue
        seen += sum(block)
        val = num(t.group(1))
        totals.append(val)
        if val not in (sum(block), seen):
            bad(f"{name}: a totals row reads {val:,}, which is neither its own "
                f"block ({sum(block):,}) nor the running total ({seen:,})")
    if not totals:
        bad(f"{name}: no totals row found")
    elif totals[-1] != sum(pops):
        bad(f"{name}: the last totals row is {totals[-1]:,}, "
            f"but all rows add to {sum(pops):,}")
    print(f"{name}: {len(rows)} ranked rows, largest {pops[0]:,}, "
          f"total {sum(pops):,}")


for pg in PAGES:
    check(pg)
print()
if fails:
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print("all checks pass")
