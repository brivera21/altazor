#!/usr/bin/env python3
"""Bake a small US map (one SVG path per state) for us-states.html.

Reads Natural Earth 50m admin-1 states (cached in /tmp/geo/admin1.geojson,
from github.com/nvkelso/natural-earth-vector), projects the lower 48 in
Web Mercator and tucks Alaska and Hawaii into insets, and writes
tools/data/usmap.json: {"w":W,"h":H,"paths":{"CA":"M...Z",...}}.

Usage: python3 build_usmap_data.py
"""

import json
import math
from pathlib import Path

from shapely.geometry import shape

GEO = Path("/tmp/geo/admin1.geojson")
OUT = Path(__file__).parent / "data" / "usmap.json"

W, H = 460, 300
R = 6378137.0


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


def fit(feats, box, tol):
    """Project features' rings into box=(x0,y0,w,h), preserving aspect."""
    pts = []
    ring_sets = {}
    for postal, geom in feats:
        rs = rings(geom.simplify(tol))
        ring_sets[postal] = rs
        for r in rs:
            pts += [merc(x, y) for x, y in r]
    mx0 = min(p[0] for p in pts); mx1 = max(p[0] for p in pts)
    my0 = min(p[1] for p in pts); my1 = max(p[1] for p in pts)
    x0, y0, bw, bh = box
    s = min(bw / (mx1 - mx0), bh / (my1 - my0))
    ox = x0 + (bw - (mx1 - mx0) * s) / 2
    oy = y0 + (bh - (my1 - my0) * s) / 2
    out = {}
    for postal, rs in ring_sets.items():
        d = ""
        for r in rs:
            seg = [(ox + (merc(x, y)[0] - mx0) * s,
                    oy + (my1 - merc(x, y)[1]) * s) for x, y in r]
            d += "M" + "L".join(f"{px:.1f},{py:.1f}" for px, py in seg) + "Z"
        out[postal] = d
    return out


def main():
    d = json.loads(GEO.read_text())
    feats = {}
    for f in d["features"]:
        if f["properties"].get("iso_a2") != "US":
            continue
        postal = f["properties"]["postal"]
        g = shape(f["geometry"]).buffer(0)
        feats[postal] = g

    # Alaska crosses the antimeridian; keep only the western-hemisphere part
    ak = feats["AK"]
    from shapely.geometry import box as sbox
    ak = ak.intersection(sbox(-180, 50, -125, 72))
    feats["AK"] = ak

    lower48 = [(p, g) for p, g in feats.items() if p not in ("AK", "HI")]
    paths = fit(lower48, (86, 4, 370, 240), 0.05)
    paths.update(fit([("AK", feats["AK"])], (4, 196, 130, 100), 0.1))
    paths.update(fit([("HI", feats["HI"])], (150, 244, 80, 52), 0.02))

    OUT.write_text(json.dumps({"w": W, "h": H, "paths": paths},
                              separators=(",", ":")))
    print(f"wrote {OUT} ({OUT.stat().st_size:,} B): {len(paths)} states")


if __name__ == "__main__":
    main()
