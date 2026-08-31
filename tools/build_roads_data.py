#!/usr/bin/env python3
"""Bake per-state highway geometry for the state pages.

Reads Natural Earth 10m roads (cached at /tmp/geo/roads.geojson), clips
each state's view box, groups segments by route (level + number), and
writes tools/data/states/<st>_roads.json:
  [{"n": "I-80", "lv": "i"|"us"|"sr", "y": year|null, "s": [[[x,y],...]]}]
Opening years come from tools/data/road_years.json (route -> year, from
each route's Wikipedia article) when present.

Usage: python3 build_roads_data.py
"""

import json
from pathlib import Path

from shapely.geometry import shape, box
from shapely.ops import unary_union

HERE = Path(__file__).parent
DATA = HERE / "data" / "states"
ROADS = json.loads(Path("/tmp/geo/roads.geojson").read_text())

STATES = ["ca", "az", "pa", "ma", "al", "ne", "mn", "mx08"]
FIPS = {"ca": "06", "az": "04", "pa": "42", "ma": "25", "al": "01",
        "ne": "31", "mn": "27"}
LV = {"Interstate": "i", "Federal": "us", "State": "sr"}


def state_outline(st):
    """The state's own shape in lon/lat, so only its roads are kept."""
    if st.startswith("mx"):
        fc = json.loads(Path("/tmp/geo/chihuahua.json").read_text())
        return unary_union([shape(f["geometry"]).buffer(0)
                            for f in fc["features"]]).buffer(0.03)
    fc = json.loads(Path("/tmp/geo/geojson-counties-fips.json").read_text())
    return unary_union([shape(f["geometry"]).buffer(0)
                        for f in fc["features"]
                        if f["id"].startswith(FIPS[st])]).buffer(0.03)


def lines(geom):
    geoms = geom.geoms if geom.geom_type == "MultiLineString" else [geom]
    return [list(g.coords) for g in geoms if len(g.coords) >= 2]


def main():
    years_p = HERE / "data" / "road_years.json"
    years = json.loads(years_p.read_text()) if years_p.exists() else {}
    feats = []
    for f in ROADS["features"]:
        p = f["properties"]
        if p.get("sov_a3") not in ("USA", "MEX"):
            continue
        lv = LV.get(p.get("level"))
        if not lv or not p.get("name") or not f.get("geometry"):
            continue
        feats.append((p["sov_a3"], lv, str(p["name"]), shape(f["geometry"])))

    for st in STATES:
        d = json.loads((DATA / f"{st}.json").read_text())
        lo, la0, hi, la1 = d["ll"]
        W, H = d["W"], d["H"]
        mx0, my0, mx1, my1 = d["m"]
        import math
        R = 6378137.0

        def XY(lon, lat):
            mx = R * math.radians(lon)
            my = R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
            return (round((mx - mx0) / (mx1 - mx0) * W, 1),
                    round((my1 - my) / (my1 - my0) * H, 1))

        clip = state_outline(st).intersection(box(lo, la0, hi, la1))
        want = "MEX" if st.startswith("mx") else "USA"
        routes = {}
        for sov, lv, name, g in feats:
            if sov != want:
                continue
            if not g.intersects(clip):
                continue
            inter = g.intersection(clip)
            if inter.is_empty:
                continue
            key = (lv, name)
            routes.setdefault(key, []).extend(lines(inter.simplify(0.01)))
        out = []
        pre = {"i": "I-", "us": "US ", "sr": "SR "}
        if st.startswith("mx"):
            pre = {"i": "MEX ", "us": "MEX ", "sr": "CHIH "}
        yst = years.get(st, {})
        # a number cannot predate its system: the US Numbered Highway
        # System dates from 1926 and the Interstates from the 1956 act
        FLOOR = {"i": 1956, "us": 1926, "sr": 0}
        for (lv, name), segs in sorted(routes.items()):
            label = pre[lv] + name
            y = yst.get(label)
            if y is not None:
                y = max(y, FLOOR[lv])
            out.append({"n": label, "lv": lv, "y": y,
                        "s": [[XY(x, y2) for x, y2 in seg] for seg in segs]})
        outp = DATA / f"{st}_roads.json"
        outp.write_text(json.dumps(out, separators=(",", ":")))
        ny = sum(1 for r in out if r["y"])
        print(f"{st}: {len(out)} routes ({ny} with years) "
              f"-> {outp.name} ({outp.stat().st_size:,} B)")


if __name__ == "__main__":
    main()
