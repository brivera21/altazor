#!/usr/bin/env python3
"""Bake per-city map data for the city pages.

Same shape as the state data (tools/data/states/<st>.json) so the state
page template can draw it: a view box around the city, the county lines
that fall inside it, and the rivers and lakes of that ground.

Each city also carries its municipal boundary, from the Census TIGER
place files, so the map can draw the city limits; Northfield carries in
addition a half-mile square standing for the quarter section John W.
North bought in 1855, placed approximately on the town plat.

Sources: Census cartographic county boundaries via Plotly's mirror,
Natural Earth 10m rivers and lakes, and the TIGER place boundaries
mirrored at github.com/generalpiston/geojson-us-city-boundaries, all
cached in /tmp/geo.

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

# key: (name, lat, lon, half-width in degrees of longitude, home county,
#        the TIGER place file, the name to put on the boundary)
CITIES = {
    "la":         ("Los Angeles", 34.045, -118.32, 0.34, "06037",
                   "ca_los-angeles", "Los Angeles city limits"),
    "lancaster":  ("Lancaster", 40.040, -76.302, 0.10, "42071",
                   "pa_lancaster", "Lancaster city limits"),
    "amherst":    ("Amherst", 42.376, -72.518, 0.075, "25015",
                   "ma_amherst", "Amherst Center, the census place"),
    "tuscaloosa": ("Tuscaloosa", 33.220, -87.545, 0.20, "01125",
                   "al_tuscaloosa", "Tuscaloosa city limits"),
    "omaha":      ("Omaha", 41.275, -96.040, 0.24, "31055",
                   "ne_omaha", "Omaha city limits"),
    "northfield": ("Northfield", 44.457, -93.170, 0.055, "27131",
                   "mn_northfield", "Northfield city limits"),
    "nyc":        ("New York City", 40.775, -73.965, 0.19, "36061",
                   "ny_new-york", "New York City limits"),
}

# what John W. North bought on 17 August 1855: a quarter section, 160
# acres, half a mile on a side. Placed on the town plat, not surveyed.
FOUNDED = {
    "northfield": (44.4575, -93.1615, 1855,
                   "The 1855 claim, 160 acres",
                   "North bought 160 acres from each of the two other "
                   "pre-emptors on 17 August 1855. The square is one "
                   "quarter section at the map's scale, set on the town "
                   "plat rather than surveyed, to show how small the "
                   "founding town was against the modern limits."),
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

    for key, (name, lat, lon, pad, home, place, plabel) in CITIES.items():
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

        # the city limits, from the Census place file, clipped to the view
        limits = json.loads((GEO / "limits" / f"{place}.json").read_text())
        lg = unary_union([shape(f["geometry"]).buffer(0)
                          for f in limits["features"]]).buffer(0)
        data["limits"] = enc(lg.intersection(vbox), 0.0004)
        data["limitsName"] = plabel

        # the founding footprint, where one is documented
        if key in FOUNDED:
            flat, flon, fy, flabel, fnote = FOUNDED[key]
            half = 804.672 / 2          # half a mile, in metres
            dlat = half / 111320.0
            dlon = half / (111320.0 * math.cos(math.radians(flat)))
            ring = [[flon - dlon, flat - dlat], [flon + dlon, flat - dlat],
                    [flon + dlon, flat + dlat], [flon - dlon, flat + dlat],
                    [flon - dlon, flat - dlat]]
            data["founded"] = {"y": fy, "n": flabel, "note": fnote,
                               "r": [[XY(x, y) for x, y in ring]]}

        p = OUT / f"{key}.json"
        p.write_text(json.dumps(data, separators=(",", ":")))
        print(f"{key}: {len(data['counties'])} counties, "
              f"{len(data['rivers'])} rivers, {len(lakes)} lakes, "
              f"{len(data['limits'])} limit rings"
              f"{', founded' if 'founded' in data else ''} "
              f"-> {p.name} ({p.stat().st_size:,} B)")


if __name__ == "__main__":
    main()
