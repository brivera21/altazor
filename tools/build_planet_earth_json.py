#!/usr/bin/env python3
"""Turn Brian's Planet Earth table into tools/data/planet-earth-species.json.

One record per row, in the table's own order, with the schema he set. lat, lon,
precision and iucn are left null here and filled by
enrich_planet_earth.py, which keeps whatever is already in the file, so
this can be re-run without losing the enrichment.

Usage: python3 build_planet_earth_json.py
"""

import json
from collections import Counter
from pathlib import Path

from planet_earth_data import EPISODES, ROWS, ABOVE, NON_TAXON

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tools" / "data" / "planet-earth-species.json"

WIKI = "https://en.wikipedia.org/wiki/"

KEEP = ("lat", "lon", "precision", "iucn", "iucn_source", "iucn_checked")


def build():
    old = {}
    if OUT.exists():
        for r in json.loads(OUT.read_text())["rows"]:
            old[(r["episode"], r["name"], r["location"])] = r

    rows = []
    for n, title, alt in EPISODES:
        for name, sci, rank, group, sub, loc, wiki in ROWS[title]:
            r = {
                "episode": n,
                "episode_title": title,
                "name": name,
                "scientific": sci,
                "rank": rank,
                "group": group,
                "subgroup": sub,
                "location": loc,
                "lat": None,
                "lon": None,
                "precision": None,
                "iucn": None,
                "wikipedia": WIKI + wiki.replace(" ", "_"),
            }
            was = old.get((n, name, loc))
            if was:
                for k in KEEP:
                    if was.get(k) is not None:
                        r[k] = was[k]
            rows.append(r)

    data = {
        "source": "BBC Planet Earth (2006), eleven episodes, as recorded by Brian Rivera",
        "order": ("Episodes are numbered in the BBC broadcast order, the order IMDb, "
                  "Metacritic and TV Guide list. Some streaming apps reorder three of "
                  "them: Seasonal Forests 8, Jungles 9, Shallow Seas 10."),
        "episodes": [{"episode": n, "title": t, "streaming_episode": b} for n, t, b in EPISODES],
        "rows": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return data


def report(data):
    rows = data["rows"]
    taxa = Counter(r["scientific"] for r in rows)
    repeats = {s: n for s, n in taxa.items() if n > 1}
    above = [r for r in rows if r["rank"] in ABOVE]
    non = [r for r in rows if r["rank"] in NON_TAXON]
    print(f"{OUT.relative_to(ROOT)}  {len(rows)} rows, {len(taxa)} distinct taxa")
    print(f"  per episode: " + ", ".join(f"{n}:{sum(1 for r in rows if r['episode'] == n)}"
                                         for n, _, _ in EPISODES))
    print(f"  {len(repeats)} taxa in more than one episode; "
          f"{sum(1 for n in repeats.values() if n == 3)} in three "
          f"({', '.join(sorted(s for s, n in repeats.items() if n == 3))})")
    print(f"  above species level: {len(above)}   not taxa at all: {len(non)}   "
          f"together {len(above) + len(non)}")
    print(f"  groups: " + ", ".join(f"{g} {n}" for g, n in
                                    Counter(r["group"] for r in rows).most_common()))
    print(f"  ranks: " + ", ".join(f"{k} {n}" for k, n in
                                   Counter(r["rank"] for r in rows).most_common()))


if __name__ == "__main__":
    report(build())
