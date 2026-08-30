#!/usr/bin/env python3
"""Prepare per-state map data for the six state pages.

Reads public sources (cached in /tmp/geo; see fetch() for URLs), clips
them to each state, projects to Web Mercator, and writes compact JSON to
tools/data/states/<st>.json. Committed output, re-runnable input.

Sources:
- County geometry: Plotly's mirror of the US Census cartographic county
  file, geojson-counties-fips.json (github.com/plotly/datasets).
- County populations: Balsama US county dataset (Wikipedia-scraped
  Census figures, updated 2025; github.com/balsama/us_counties_data).
- Rivers and lakes: Natural Earth 10m (rivers_lake_centerlines, the
  North America rivers supplement, and lakes) from
  github.com/nvkelso/natural-earth-vector.

Usage: python3 build_states_data.py
"""

import json
import math
import urllib.request
from pathlib import Path

from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union

GEO = Path("/tmp/geo")
OUT = Path(__file__).parent / "data" / "states"
OUT.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "geojson-counties-fips.json":
        "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
    "counties_pop.json":
        "https://raw.githubusercontent.com/balsama/us_counties_data/main/data/counties.json",
    "rivers.geojson":
        "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_rivers_lake_centerlines.geojson",
    "rivers_na.geojson":
        "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_rivers_north_america.geojson",
    "lakes.geojson":
        "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_lakes.geojson",
}

STATES = {
    "ca": ("California", "06"),
    "pa": ("Pennsylvania", "42"),
    "ma": ("Massachusetts", "25"),
    "al": ("Alabama", "01"),
    "ne": ("Nebraska", "31"),
    "mn": ("Minnesota", "27"),
    "az": ("Arizona", "04"),
}

W = 1000  # view width; height follows the state's mercator aspect

R = 6378137.0
def merc(lon, lat):
    lat = max(-85, min(85, lat))
    return (R * math.radians(lon),
            R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)))


def fetch():
    GEO.mkdir(exist_ok=True)
    for name, url in SOURCES.items():
        p = GEO / name
        if not p.exists():
            print("fetch", name)
            urllib.request.urlretrieve(url, p)


def rings(geom):
    """Exterior+interior rings of a (Multi)Polygon as coordinate lists."""
    geoms = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    out = []
    for g in geoms:
        out.append(list(g.exterior.coords))
        for i in g.interiors:
            out.append(list(i.coords))
    return out


def lines(geom):
    geoms = geom.geoms if geom.geom_type == "MultiLineString" else [geom]
    return [list(g.coords) for g in geoms if len(g.coords) >= 2]


def main():
    fetch()
    # county founding years, keyed by FIPS; from each state's Wikipedia
    # "List of counties" table (the Est./Created column)
    county_years = json.loads(
        (Path(__file__).parent / "data" / "county_years.json").read_text())
    counties_fc = json.loads((GEO / "geojson-counties-fips.json").read_text())
    pops = json.loads((GEO / "counties_pop.json").read_text())
    pop_by_fips = {v["fips"]: v for v in pops.values()}
    rivers_fc = json.loads((GEO / "rivers.geojson").read_text())
    rivers_na_fc = json.loads((GEO / "rivers_na.geojson").read_text())
    lakes_fc = json.loads((GEO / "lakes.geojson").read_text())

    for st, (state_name, fips) in STATES.items():
        feats = [f for f in counties_fc["features"]
                 if f["id"].startswith(fips)]
        print(f"{state_name}: {len(feats)} counties")
        shapes = {}
        for f in feats:
            g = shape(f["geometry"]).buffer(0)
            shapes[f["id"]] = (f["properties"]["NAME"], g)
        outline = unary_union([g for _, g in shapes.values()]).buffer(0)
        minx, miny, maxx, maxy = outline.bounds
        # the view keeps a wide margin so the surrounding terrain, ocean
        # and neighbor states show around the outline
        VP = 0.55
        pad = 0.90
        clipbox = box(minx - pad, miny - pad, maxx + pad, maxy + pad)

        # mercator view transform
        mx0, my0 = merc(minx - VP, miny - VP)
        mx1, my1 = merc(maxx + VP, maxy + VP)
        H = round(W * (my1 - my0) / (mx1 - mx0), 1)

        def XY(lon, lat):
            mx, my = merc(lon, lat)
            return (round((mx - mx0) / (mx1 - mx0) * W, 1),
                    round((my1 - my) / (my1 - my0) * H, 1))

        def enc_rings(geom, tol):
            return [[XY(x, y) for x, y in ring]
                    for ring in rings(geom.simplify(tol))]

        data = {
            "name": state_name, "fips": fips, "W": W, "H": H,
            # mercator bbox for the client's terrain and land cover
            # overlays (EPSG:3857 metres), aligned 1:1 with the view
            "m": [mx0, my0, mx1, my1],
            "ll": [minx - VP, miny - VP, maxx + VP, maxy + VP],
        }
        data["outline"] = enc_rings(outline, 0.008)
        data["counties"] = []
        for cid, (name, g) in sorted(shapes.items()):
            info = pop_by_fips.get(cid, {})
            data["counties"].append({
                "n": name, "fips": cid,
                "p": info.get("population"),
                "y": county_years.get(cid),
                "r": enc_rings(g, 0.004),
            })

        # rivers: union of both NE layers, clipped; prefer named features
        seen = {}
        for fc in (rivers_fc, rivers_na_fc):
            for f in fc["features"]:
                if not f.get("geometry"):
                    continue
                name = (f["properties"].get("name") or "").strip()
                g = shape(f["geometry"])
                if not g.intersects(clipbox):
                    continue
                clipped = g.intersection(clipbox)
                if clipped.is_empty:
                    continue
                key = name or f"~{round(clipped.length,4)}"
                if key in seen:
                    seen[key] = seen[key].union(clipped)
                else:
                    seen[key] = clipped
        rivers = []
        for name, g in seen.items():
            if name.startswith("~") and g.length < 0.35:
                continue  # short unnamed fragments
            segs = lines(g.simplify(0.006))
            rivers.append({"n": "" if name.startswith("~") else name,
                           "s": [[XY(x, y) for x, y in seg] for seg in segs]})
        data["rivers"] = rivers

        # lakes: anything intersecting the state, big or named
        lakes = []
        for f in lakes_fc["features"]:
            if not f.get("geometry"):
                continue
            name = (f["properties"].get("name") or "").strip()
            g = shape(f["geometry"]).buffer(0)
            if not g.intersects(clipbox):
                continue
            inter = g.intersection(clipbox)
            if inter.is_empty:
                continue
            if inter.area < 0.0015 and not name:
                continue
            lakes.append({"n": name, "r": enc_rings(inter, 0.004)})
        data["lakes"] = lakes

        out = OUT / f"{st}.json"
        out.write_text(json.dumps(data, separators=(",", ":")),
                       encoding="utf-8")
        print(f"  wrote {out} ({out.stat().st_size:,} B): "
              f"{len(rivers)} rivers, {len(lakes)} lakes")


if __name__ == "__main__":
    main()
