#!/usr/bin/env python3
"""Bake per-city map data for the city pages.

Same shape as the state data (tools/data/states/<st>.json) so the state
page template can draw it: a view box around the city, the county lines
that fall inside it, and the rivers and lakes of that ground.

Sources: Census cartographic county boundaries via Plotly's mirror, and
Natural Earth 10m rivers and lakes, both cached in /tmp/geo.

Usage: python3 build_cities_data.py
"""

import json
import math
from pathlib import Path

from shapely.geometry import shape, box
from shapely.ops import unary_union

GEO = Path("/tmp/geo")
OUT = Path(__file__).parent / "data" / "cities"
OUT.mkdir(parents=True, exist_ok=True)

W = 1000
R = 6378137.0

# key: (name, lat, lon, half-width in degrees of longitude, home county)
CITIES = {
    "la":         ("Los Angeles", 34.05, -118.24, 0.62, "06037"),
    "lancaster":  ("Lancaster", 40.038, -76.305, 0.30, "42071"),
    "amherst":    ("Amherst", 42.375, -72.519, 0.28, "25015"),
    "tuscaloosa": ("Tuscaloosa", 33.207, -87.535, 0.34, "01125"),
    "omaha":      ("Omaha", 41.257, -95.995, 0.40, "31055"),
    "northfield": ("Northfield", 44.458, -93.161, 0.28, "27131"),
    "nyc":        ("New York City", 40.712, -74.006, 0.46, "36061"),
}


def merc(lon, lat):
    lat = max(-85, min(85, lat))
    return (R * math.radians(lon),
            R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)))


def rings(geom):
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
    counties_fc = json.loads((GEO / "geojson-counties-fips.json").read_text())
    pops = json.loads((GEO / "counties_pop.json").read_text())
    pop_by_fips = {v["fips"]: v for v in pops.values()}
    years = json.loads(
        (Path(__file__).parent / "data" / "county_years.json").read_text())
    rivers_fc = json.loads((GEO / "rivers.geojson").read_text())
    rivers_na_fc = json.loads((GEO / "rivers_na.geojson").read_text())
    lakes_fc = json.loads((GEO / "lakes.geojson").read_text())

    for key, (name, lat, lon, pad, home) in CITIES.items():
        # a view box wider than tall, in the page's usual proportion
        latpad = pad * 0.72
        lo, la0, hi, la1 = lon - pad, lat - latpad, lon + pad, lat + latpad
        vbox = box(lo, la0, hi, la1)
        mx0, my0 = merc(lo, la0)
        mx1, my1 = merc(hi, la1)
        H = round(W * (my1 - my0) / (mx1 - mx0), 1)

        def XY(x, y):
            mx, my = merc(x, y)
            return (round((mx - mx0) / (mx1 - mx0) * W, 1),
                    round((my1 - my) / (my1 - my0) * H, 1))

        def enc(geom, tol):
            return [[XY(x, y) for x, y in r]
                    for r in rings(geom.simplify(tol))]

        cos = []
        for f in counties_fc["features"]:
            g = shape(f["geometry"]).buffer(0)
            if not g.intersects(vbox):
                continue
            cos.append((f["id"], f["properties"]["NAME"], g))
        outline = unary_union([g for _, _, g in cos]).buffer(0)

        data = {"name": name, "fips": key, "W": W, "H": H,
                "m": [mx0, my0, mx1, my1], "ll": [lo, la0, hi, la1],
                "home": home,
                "outline": enc(outline.intersection(vbox), 0.004),
                "counties": []}
        for cid, cname, g in sorted(cos):
            info = pop_by_fips.get(cid, {})
            data["counties"].append({
                "n": cname, "fips": cid, "p": info.get("population"),
                "y": years.get(cid),
                "r": enc(g.intersection(vbox), 0.0015)})

        seen = {}
        for fc in (rivers_fc, rivers_na_fc):
            for f in fc["features"]:
                if not f.get("geometry"):
                    continue
                nm = (f["properties"].get("name") or "").strip()
                g = shape(f["geometry"])
                if not g.intersects(vbox):
                    continue
                clipped = g.intersection(vbox)
                if clipped.is_empty:
                    continue
                k = nm or f"~{round(clipped.length, 5)}"
                seen[k] = seen[k].union(clipped) if k in seen else clipped
        data["rivers"] = [
            {"n": "" if k.startswith("~") else k,
             "s": [[XY(x, y) for x, y in seg]
                   for seg in lines(g.simplify(0.002))]}
            for k, g in seen.items()]
        lakes = []
        for f in lakes_fc["features"]:
            if not f.get("geometry"):
                continue
            nm = (f["properties"].get("name") or "").strip()
            g = shape(f["geometry"]).buffer(0)
            if not g.intersects(vbox):
                continue
            inter = g.intersection(vbox)
            if inter.is_empty:
                continue
            lakes.append({"n": nm, "r": enc(inter, 0.001)})
        data["lakes"] = lakes

        p = OUT / f"{key}.json"
        p.write_text(json.dumps(data, separators=(",", ":")))
        print(f"{key}: {len(data['counties'])} counties, "
              f"{len(data['rivers'])} rivers, {len(lakes)} lakes "
              f"-> {p.name} ({p.stat().st_size:,} B)")


if __name__ == "__main__":
    main()
