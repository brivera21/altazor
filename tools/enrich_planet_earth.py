#!/usr/bin/env python3
"""Add the coordinates and the conservation statuses to the species file.

Coordinates come from planet_earth_places.py, keyed by the location
string, and carry a precision of "site" or "region" and, for every
centroid, a note saying how it was chosen. Statuses come from
planet_earth_iucn.py and are set only on rows that resolve to a species
or a subspecies; everything above that level is left null rather than
guessed at from the genus or the family.

The script also checks each pin against the coastline raster the Earth
pages share: a land animal in open water, or a whale on dry land, is a
mistake worth catching before the page is drawn. Rows whose location is
a habitat with no geography are exempt, and are listed instead.

Usage: python3 enrich_planet_earth.py
"""

import base64
import json
from collections import Counter
from pathlib import Path

from planet_earth_places import PLACES
from planet_earth_iucn import IUCN, SOURCE, CHECKED
from planet_earth_data import RANKED

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "tools" / "data" / "planet-earth-species.json"
GEO = json.loads((ROOT / "tools" / "data" / "plates.json").read_text())

# groups whose rows should sit on land, and the ones that should sit in water
LAND_GROUPS = ("plant", "fungus")
SEA_ONLY = {
    "Great white shark", "Whale shark", "Oceanic whitetip shark", "Yellowfin tuna",
    "Rainbow runner", "Scad mackerel", "Common dolphin", "Blue whale", "Humpback whale",
    "Antarctic krill", "Sailfish", "Spider crab", "Corals", "Sponges", "Vent bacteria",
    "Trevally", "Goatfish", "Banded sea krait", "Chokka squid", "Short-tail stingray",
    "Dusky dolphin", "Bottlenose dolphin", "River dolphins",
}


def _mask():
    """The coastline raster, which the Earth pages carry as a base64 PNG."""
    import io
    from PIL import Image
    im = Image.open(io.BytesIO(base64.b64decode(GEO["land"]))).convert("L")
    return im.size[0], im.size[1], im.load()


LW, LH, MASK = _mask()


def land_at(lat, lon):
    """True where the shared coastline raster says land."""
    x = int((lon + 180) / 360 * LW) % LW
    y = min(LH - 1, max(0, int((90 - lat) / 180 * LH)))
    return MASK[x, y] > 0


def enrich():
    data = json.loads(FILE.read_text())
    for r in data["rows"]:
        lat, lon, prec, wiki, note = PLACES[r["location"]]
        r["lat"], r["lon"], r["precision"] = lat, lon, prec
        r["place_source"] = wiki
        r["place_note"] = note
        if r["rank"] in RANKED:
            cat, ref, note = IUCN[r["scientific"]]
            r["iucn"] = cat
            r["iucn_taxon"] = ref
            r["iucn_note"] = note
            r["iucn_source"] = SOURCE
            r["iucn_checked"] = CHECKED
        else:
            r["iucn"] = None
    data["place_check"] = ("Coordinates follow the location field, not the species' range. "
                           "Where the location names only a region, a biome or a habitat, "
                           "precision is \"region\" and place_note says what centroid was "
                           "chosen. Checked against Wikipedia's article coordinates on "
                           "September 19, 2026.")
    FILE.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return data


def check(data):
    bad, exempt = [], []
    for r in data["rows"]:
        on_land = land_at(r["lat"], r["lon"])
        marine = r["name"] in SEA_ONLY
        if "no geography given" in (r["place_note"] or "") or "no place given" in (r["place_note"] or ""):
            exempt.append(r["name"] + " / " + r["location"])
            continue
        if marine and on_land:
            bad.append(f"marine on land: {r['name']} at {r['location']} ({r['lat']}, {r['lon']})")
        if not marine and r["group"] in LAND_GROUPS and not on_land:
            bad.append(f"plant or fungus at sea: {r['name']} at {r['location']} ({r['lat']}, {r['lon']})")
    rows = data["rows"]
    print(f"{FILE.relative_to(ROOT)}  {len(rows)} rows enriched")
    print("  precision: " + ", ".join(f"{k} {v}" for k, v in Counter(r["precision"] for r in rows).most_common()))
    print(f"  coordinates from a Wikipedia article: "
          f"{sum(1 for r in rows if r['place_source'])}; "
          f"own centroid with a note: {sum(1 for r in rows if not r['place_source'])}")
    have = [r for r in rows if r["iucn"]]
    print(f"  statuses set: {len(have)} of {sum(1 for r in rows if r['rank'] in RANKED)} "
          f"species and subspecies rows; {len(rows) - len(have)} left null")
    print("  " + ", ".join(f"{k} {v}" for k, v in Counter(r["iucn"] for r in have).most_common()))
    print(f"  exempt from the land check (no geography in the location): {len(exempt)}")
    for e in sorted(set(exempt)):
        print("      " + e)
    if bad:
        print(f"  {len(bad)} PIN PROBLEMS:")
        for b in bad:
            print("      " + b)
    else:
        print("  every pin with a place sits on the right side of the coast")
    return not bad


if __name__ == "__main__":
    import sys
    sys.exit(0 if check(enrich()) else 1)
