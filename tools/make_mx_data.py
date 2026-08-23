#!/usr/bin/env python3
"""Build the layers mexico.html is drawn from.

The states are not polygons in any dataset available here. They are built the
way build_norte.py builds the six northern ones, for all thirty two:

  1. take the GSHHG shoreline for the country, and the WDBII national and
     internal boundary arcs inside its box
  2. node them all against each other and polygonize, which turns the pile of
     arcs into faces
  3. give each state the face that contains a known point inside it, usually
     its capital
  4. check every face against the area INEGI publishes for that state

Rivers come from WDBII, and the sierras from the roughness of Natural Earth's
relief raster, the measure make_sierras.py uses: broken ground is high
frequency texture in that image and plains are smooth. It marks rugged country,
not any named range.

Usage: python3 make_mx_data.py     (writes /home/claude/mx/*.pkl)
"""

import pickle
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.ops import linemerge, polygonize, unary_union
from shapely.validation import make_valid

import make_us_data as U

OUT = Path("/home/claude/mx")
BOX = (-118.6, 14.2, -86.4, 32.9)          # the whole country and a margin
BOX_FRAME = (BOX[0], BOX[2], BOX[1], BOX[3])   # west, east, south, north
TIERS = [("sierra", 15.5, 700.0), ("alta", 24.0, 400.0)]

# INEGI, Marco Geoestadistico: surface area of each state, km2, and a point
# inside it, which is its capital unless the capital sits on a border.
STATES = [
    ("Chihuahua", 247460, (28.63, -106.08)),
    ("Sonora", 179355, (29.07, -110.96)),
    ("Coahuila", 151563, (25.42, -101.00)),
    ("Durango", 123451, (24.02, -104.65)),
    ("Oaxaca", 93793, (17.06, -96.72)),
    ("Tamaulipas", 80175, (23.74, -99.14)),
    ("Jalisco", 78588, (20.67, -103.35)),
    ("Zacatecas", 75275, (22.77, -102.58)),
    ("Baja California Sur", 73909, (24.14, -110.31)),
    ("Chiapas", 73311, (16.75, -93.12)),
    ("Veracruz", 71820, (19.54, -96.91)),
    ("Baja California", 71450, (32.63, -115.45)),
    ("Nuevo Leon", 64156, (25.67, -100.31)),
    ("Guerrero", 63596, (17.55, -99.50)),
    ("San Luis Potosi", 60983, (22.15, -100.98)),
    ("Michoacan", 58599, (19.70, -101.19)),
    ("Campeche", 57485, (19.84, -90.53)),
    ("Sinaloa", 57377, (24.81, -107.39)),
    ("Quintana Roo", 42361, (18.50, -88.30)),
    ("Yucatan", 39612, (20.97, -89.62)),
    ("Puebla", 34309, (19.04, -98.20)),
    ("Guanajuato", 30607, (21.02, -101.26)),
    ("Nayarit", 27857, (21.51, -104.89)),
    ("Tabasco", 24731, (17.99, -92.93)),
    ("Mexico", 22357, (19.29, -99.66)),
    ("Hidalgo", 20846, (20.12, -98.73)),
    ("Queretaro", 11684, (20.59, -100.39)),
    ("Colima", 5627, (19.24, -103.73)),
    ("Aguascalientes", 5616, (21.88, -102.30)),
    ("Morelos", 4879, (18.92, -99.23)),
    ("Tlaxcala", 3997, (19.32, -98.24)),
    ("Ciudad de Mexico", 1495, (19.43, -99.13)),
]

# Twenty places picked as clear cases before the threshold was set, ten broken
# and ten flat, and none of them used to set it. Two first drafts had to go:
# the Altar desert has the Pinacate lava field in it and the llanos de Apan sit
# inside the volcanic belt, so neither is flat ground.
ROUGH_REF = [
    ("la Sierra Madre Occidental", 26.50, -107.20),
    ("la Sierra Tarahumara", 27.60, -107.80),
    ("la Sierra Madre Oriental", 24.20, -99.70),
    ("el Eje Neovolcanico", 19.30, -99.90),
    ("la Sierra Madre del Sur", 17.20, -100.30),
    ("la Sierra de Juarez", 32.00, -115.90),
    ("la Sierra de la Laguna", 23.55, -109.95),
    ("los Altos de Chiapas", 16.75, -92.60),
    ("la Sierra Norte de Puebla", 20.05, -97.80),
    ("la Sierra Gorda", 21.30, -99.40),
]
SMOOTH_REF = [
    ("la peninsula de Yucatan", 20.20, -89.20),
    ("la llanura de Tabasco", 18.20, -92.90),
    ("el Bajio", 20.60, -101.30),
    ("el valle de Mexicali", 32.40, -115.30),
    ("la llanura costera del Golfo", 22.60, -98.10),
    ("el delta del Colorado", 32.00, -114.90),
    ("la laguna de Terminos", 18.60, -91.60),
    ("la laguna Madre", 24.60, -97.90),
    ("la costa de Sinaloa", 25.20, -108.40),
    ("la llanura de Campeche", 19.10, -90.20),
]


def build_states(land, arcs):
    """Cut the country into faces and hand each state the face it sits in.

    WDBII draws the internal boundaries as loose arcs: they stop short of each
    other and short of the coast, so on their own they close nothing and
    polygonising gives one face for the whole mainland. Every loose end is run
    out to whatever is nearest, another arc or the shoreline, and then the pile
    closes into faces.
    """
    from shapely.ops import nearest_points, polygonize
    from shapely import STRtree

    polys = sorted((land.geoms if land.geom_type == "MultiPolygon" else [land]),
                   key=lambda p: -p.area)
    big = unary_union(polys[:6])            # the mainland, Baja and the big isles
    b = big.simplify(0.002, preserve_topology=True).boundary

    tree = STRtree(arcs)
    bridges = []
    for i, a in enumerate(arcs):
        for e in (0, -1):
            p = Point(a.coords[e])
            best = (9e9, None)
            for j in tree.query(p.buffer(0.4)):
                if j == i:
                    continue
                q = nearest_points(arcs[j], p)[0]
                d = p.distance(q)
                if d < best[0]:
                    best = (d, q)
            q1 = nearest_points(b, p)[0]
            d1 = p.distance(q1)
            if d1 < best[0]:
                best = (d1, q1)
            d, q = best
            if q is not None and 0 < d < 0.35:
                bridges.append(LineString([(p.x, p.y), (q.x, q.y)]))
    print(f"  {len(bridges)} loose ends run out to the nearest line")

    faces = list(polygonize(unary_union([b] + arcs + bridges)))
    print(f"  {len(faces)} faces")
    out = {}
    for name, km2, (la, lo) in STATES:
        p = Point(lo, la)
        got = [f for f in faces if f.contains(p)]
        if got:
            out[name] = min(got, key=lambda f: f.area)
    return out, big


def main():
    OUT.mkdir(exist_ok=True)
    frame = box(*BOX)

    meta = [l.split() for l in open(U.BM / "gshhsmeta_f.dat")]
    raw = open(U.BM / "gshhs_f.dat", "rb").read()
    land = []
    for m in meta:
        lvl, n, off = int(m[0]), int(m[2]), int(m[5])
        if lvl != 1:
            continue
        if not (float(m[3]) < BOX[3] and float(m[4]) > BOX[1]):
            continue
        a = np.frombuffer(raw, "<f4", count=2 * n, offset=off).reshape(-1, 2).astype(float)
        lon = a[:, 0].copy()
        lon[lon > 180] -= 360
        if lon.max() < BOX[0] or lon.min() > BOX[2]:
            continue
        p = Polygon(np.column_stack([lon, a[:, 1]]))
        if p.is_valid or (p := make_valid(p)).geom_type in ("Polygon", "MultiPolygon"):
            land.append(p)
    land = make_valid(unary_union(land)).intersection(frame)
    print(f"shoreline: {len(land.geoms) if land.geom_type == 'MultiPolygon' else 1} "
          f"land polygons in the frame")

    arcs = []
    for stem in ("countries", "states"):
        for s in U.read_wdb(stem):
            if len(s) < 2:
                continue
            L = LineString(s)
            if L.intersects(frame):
                c = L.intersection(frame)
                for g in (c.geoms if c.geom_type.startswith("Multi") else [c]):
                    if g.geom_type == "LineString" and len(g.coords) > 1:
                        arcs.append(g)
    print(f"boundaries: {len(arcs)} arcs inside the frame")

    out, big = build_states(land, arcs)
    bad = []
    for name, km2, _ in STATES:
        if name not in out:
            bad.append(f"{name}: no face")
            continue
        e = abs(U.sph_area_km2(out[name]) - km2) / km2 * 100
        if e > 8:
            bad.append(f"{name}: {e:.0f}% off INEGI")
    print(f"states: {len(out)} of {len(STATES)} found; "
          f"{len(STATES) - len(bad)} within 8% of the published area")
    for m in bad:
        print(f"  {m}")
    pickle.dump(out, open(OUT / "states.pkl", "wb"))
    pickle.dump(big, open(OUT / "land.pkl", "wb"))

    riv = []
    for s in U.read_wdb("rivers"):
        if len(s) < 2:
            continue
        lo, la = s[:, 0], s[:, 1]
        if lo.max() < BOX[0] or lo.min() > BOX[2] or la.max() < BOX[1] or la.min() > BOX[3]:
            continue
        riv.append(LineString(s))
    merged = linemerge(riv)
    courses = list(merged.geoms) if merged.geom_type == "MultiLineString" else [merged]
    inside = []
    for L in courses:
        if not L.intersects(big):
            continue
        c = L.intersection(big)
        for g in (c.geoms if c.geom_type.startswith("Multi") else [c]):
            if g.geom_type == "LineString" and len(g.coords) > 1:
                inside.append(g)
    print(f"rivers: {len(inside)} pieces inside the country, {len(courses)} courses")
    pickle.dump(inside, open(OUT / "rivers.pkl", "wb"))
    pickle.dump(courses, open(OUT / "courses.pkl", "wb"))

    lum, _ = U.roughness(BOX_FRAME)
    np.save(OUT / "lum.npy", lum)
    tiers, at = U.rugged(BOX_FRAME, lum, big, TIERS)
    missed = [n for n, la, lo in ROUGH_REF if at(la, lo) < TIERS[0][1]]
    caught = [n for n, la, lo in SMOOTH_REF if at(la, lo) >= TIERS[0][1]]
    print(f"sierras: {len(missed)} rugged references missed, "
          f"{len(caught)} flat ones wrongly caught")
    pickle.dump(tiers, open(OUT / "sierras.pkl", "wb"))
    return out, big


if __name__ == "__main__":
    main()
