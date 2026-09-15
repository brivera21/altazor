#!/usr/bin/env python3
"""Make tools/data/plates.json from Bird's PB2002 model.

Inputs, from https://github.com/fraxen/tectonicplates (GeoJSON/):
  PB2002_plates.json   the 52 plates as polygons
  PB2002_steps.json    the boundaries in 5,824 steps, each with a class
                       (OSR, CRB, SUB, OTF, CTF, CCB, OCB), a length and a
                       relative velocity in mm/yr
and the land raster embedded in this site's earth.html (GSHHG coastlines at
1/6 degree, made by build_earth.py).

Output: one JSON with
  ids    a 2160x1080 PNG whose pixel value is the plate's index + 1
  land   a 1080x540 PNG land mask
  areas  each plate's name, area in km^2 by the spherical polygon formula,
         and the area of its raster footprint
  lines  the boundary steps chained into polylines of one class, simplified
         to 0.12 degrees, each with its length, mean velocity, divergence
         and elevation

Usage: python3 make_plates.py PB2002_plates.json PB2002_steps.json
"""

import base64
import io
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tools" / "data" / "plates.json"
W, H = 2160, 1080
R = 6371.0088
CL = ["OSR", "CRB", "SUB", "OTF", "CTF", "CCB", "OCB"]


def unwrap(ring):
    """Make longitude continuous along the ring, so a dateline crossing does
    not draw a line across the map."""
    out, prev, off = [], None, 0
    for lon, lat in (pt[:2] for pt in ring):
        if prev is not None:
            d = lon - prev
            if d > 180:
                off -= 360
            elif d < -180:
                off += 360
        out.append((lon + off, lat))
        prev = lon
    return out


def px(lon, lat):
    return ((lon + 180) / 360 * W, (90 - lat) / 180 * H)


def dp(pts, tol):
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy) or 1e-9
    best, bi = 0, 0
    for i in range(1, len(pts) - 1):
        x, y = pts[i]
        dist = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / n
        if dist > best:
            best, bi = dist, i
    if best > tol:
        return dp(pts[:bi + 1], tol)[:-1] + dp(pts[bi:], tol)
    return [pts[0], pts[-1]]


def main(plates_path, steps_path):
    plates = json.load(open(plates_path))
    steps = json.load(open(steps_path))

    # the plates, rasterized; a ring that winds round a pole is closed through it
    ids = np.zeros((H, W), np.uint8)
    lat = np.radians(90 - (np.arange(H) + 0.5) * 180 / H)
    wt = np.cos(lat)[:, None] * np.ones((1, W))
    cell = math.radians(180 / H) ** 2 * R * R
    codes, areas = [], {}
    for f in plates["features"]:                      # two plates come in two pieces
        if f["properties"]["Code"] not in codes:
            codes.append(f["properties"]["Code"])
    for f in plates["features"]:
        code, name = f["properties"]["Code"], f["properties"]["PlateName"]
        i = codes.index(code) + 1
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        m = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(m)
        for poly in polys:
            ring = unwrap(poly[0])
            if abs(ring[-1][0] - ring[0][0]) > 180:
                pole = 90 if np.mean([la for _, la in ring]) > 0 else -90
                ring = ring + [(ring[-1][0], pole), (ring[0][0], pole)]
            for off in (-720, -360, 0, 360, 720):
                pts = [px(lo + off, la) for lo, la in ring]
                if max(x for x, _ in pts) < 0 or min(x for x, _ in pts) > W:
                    continue
                d.polygon(pts, fill=255)
        a = np.array(m) > 0
        ids[a & (ids == 0)] = i
    # areas by the spherical polygon formula, which is exact for the model's
    # polygons; the raster is only for finding the plate under the pointer
    names = {f["properties"]["Code"]: f["properties"]["PlateName"] for f in plates["features"]}
    raster = {code: float((wt * (ids == i)).sum() * cell) for i, code in enumerate(codes, 1)}
    for f in plates["features"]:
        code = f["properties"]["Code"]
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        a = 0.0
        for poly in polys:
            ring = unwrap(poly[0])
            if ring[0] == ring[-1]:
                ring = ring[:-1]
            if abs(ring[-1][0] - ring[0][0]) > 180:
                pole = 90 if np.mean([la for _, la in ring]) > 0 else -90
                ring = ring + [(ring[-1][0], pole), (ring[0][0], pole)]
            tot = 0.0
            for j in range(len(ring)):
                lon1, lat1 = ring[j]
                lon2, lat2 = ring[(j + 1) % len(ring)]
                tot += math.radians(lon2 - lon1) * (2 + math.sin(math.radians(lat1)) + math.sin(math.radians(lat2)))
            a += abs(tot) * R * R / 2
        areas[code] = (names[code], areas.get(code, (None, 0.0))[1] + a)
    areas = {k: (n, a, raster[k]) for k, (n, a) in areas.items()}
    buf = io.BytesIO()
    Image.fromarray(ids, "L").save(buf, "PNG", optimize=True)
    ids_b64 = base64.b64encode(buf.getvalue()).decode()

    # the boundaries, chained by plate pair and class
    lines, cur = [], None
    for f in steps["features"]:
        pr = f["properties"]
        a = (round(pr["STARTLONG"], 2), round(pr["STARTLAT"], 2))
        b = (round(pr["FINALLONG"], 2), round(pr["FINALLAT"], 2))
        key = (pr["PLATEBOUND"], pr["STEPCLASS"])
        if cur and cur["key"] == key and cur["pts"][-1] == a and abs(b[0] - a[0]) < 180:
            cur["pts"].append(b)
            for k, fld in (("L", "STEPLENGTH"), ("V", "VELOCITYLE"), ("D", "VELOCITYDI"), ("E", "ELEVATION")):
                cur[k].append(pr[fld])
        else:
            cur = {"key": key, "pts": [a, b], "L": [pr["STEPLENGTH"]], "V": [pr["VELOCITYLE"]], "D": [pr["VELOCITYDI"]], "E": [pr["ELEVATION"]]}
            lines.append(cur)
    out = []
    for c in lines:
        L = sum(c["L"])
        v = sum(l * x for l, x in zip(c["L"], c["V"])) / L
        dv = sum(l * x for l, x in zip(c["L"], c["D"])) / L
        pts = dp(c["pts"], 0.12)
        out.append([c["key"][0], CL.index(c["key"][1]), round(L), round(v, 1), round(dv, 1), round(sum(c["E"]) / len(c["E"])),
                    [round(v, 1) for pt in pts for v in pt]])

    # the land mask, from the Climate page's raster
    html = (ROOT / "earth.html").read_text()
    m = re.search(r'"png":\s*"([A-Za-z0-9+/=]+)"', html)
    arr = np.array(Image.open(io.BytesIO(base64.b64decode(m.group(1)))))
    land = Image.fromarray(((arr & 7) > 0).astype(np.uint8) * 255, "L").resize((W // 2, H // 2), Image.NEAREST)
    buf = io.BytesIO()
    land.save(buf, "PNG", optimize=True)

    data = {"W": W, "H": H, "landW": W // 2, "landH": H // 2, "classes": CL, "codes": codes, "areas": areas,
            "lines": out, "ids": ids_b64, "land": base64.b64encode(buf.getvalue()).decode()}
    OUT.write_text(json.dumps(data, separators=(",", ":")))
    print(f"wrote {OUT} ({OUT.stat().st_size:,} B): {len(codes)} plates, {len(out)} boundary lines, "
          f"{sum(v[1] for v in areas.values()) / 1e6:.1f} million km2")


if __name__ == "__main__":
    main(*sys.argv[1:3])
