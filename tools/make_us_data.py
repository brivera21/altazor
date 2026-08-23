#!/usr/bin/env python3
"""Build the layers us.html is drawn from.

Everything here is offline, from what basemap-data-hires bundles:

  UScounties.shp   a county shapefile. Dissolving it by state code gives real
                   state polygons, which is better than polygonising border
                   arcs: the counties already carry the coastline and every
                   inland water body the census counts.
  rivers_f.dat     WDBII rivers at full resolution. The layer has no names in
                   it, so a river is labelled only when the same segment is the
                   nearest one to two independent points on that river, far
                   apart; see verify_us.py.
  shadedrelief.jpg Natural Earth's relief raster at two arc minutes. There is
                   no elevation grid available here, so rugged ground is found
                   the way make_sierras.py finds it for northern Mexico: broken
                   country shows up as high frequency light and dark texture in
                   that image while plains are smooth, so the local standard
                   deviation of luminance measures how broken the ground is.
                   Windows that touch the sea are dropped, since a shoreline is
                   a brightness step and would read as a mountain.

The roughness threshold is set against reference places that are not used to
build the layer: ranges that must be inside it and plains, basins and deltas
that must not. verify_us.py re-runs that test on every build.

Usage: python3 make_us_data.py     (writes /home/claude/us/*.pkl)
"""

import collections
import math
import pickle
from pathlib import Path

import numpy as np
import shapefile
from PIL import Image
from scipy import ndimage as ndi
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box, shape
from shapely.ops import unary_union
from shapely.validation import make_valid

Image.MAX_IMAGE_PIXELS = None
BM = Path("/usr/local/lib/python3.11/dist-packages/mpl_toolkits/basemap_data")
OUT = Path("/home/claude/us")

# the three frames the page draws, in degrees
FRAMES = {
    "conus": (-125.0, -66.5, 24.3, 49.5),
    "ak": (-173.0, -129.0, 51.0, 71.5),
    "hi": (-160.5, -154.6, 18.8, 22.4),
}

WIN = 5                   # roughness window, about nine kilometres
TIERS = [("rough", 13.0, 1200.0), ("high", 22.0, 700.0)]   # name, floor, min km2


def read_wdb(stem):
    meta = [l.split() for l in open(BM / f"{stem}meta_f.dat")]
    raw = open(BM / f"{stem}_f.dat", "rb").read()
    out = []
    for m in meta:
        n, off = int(m[2]), int(m[5])
        a = np.frombuffer(raw, "<f4", count=2 * n, offset=off).reshape(-1, 2)
        a = a.astype(float)
        lon = a[:, 0].copy()
        lon[lon > 180] -= 360
        out.append(np.column_stack([lon, a[:, 1]]))
    return out


def sph_area_km2(g):
    """Area of a lon/lat polygon on the sphere, by spherical excess."""
    R = 6371.0088
    tot = 0.0
    polys = g.geoms if isinstance(g, MultiPolygon) else [g]
    for p in polys:
        for ring, sign in [(p.exterior, 1)] + [(r, -1) for r in p.interiors]:
            xy = np.asarray(ring.coords)
            lam = np.radians(xy[:, 0])
            phi = np.radians(xy[:, 1])
            s = np.sum((lam[1:] - lam[:-1]) * (2 + np.sin(phi[:-1]) + np.sin(phi[1:])))
            tot += sign * abs(s) * R * R / 2
    return tot


def states():
    r = shapefile.Reader(str(BM / "UScounties"), encoding="latin-1")
    byst = collections.defaultdict(list)
    for sr in r.shapeRecords():
        byst[sr.record[3]].append(make_valid(shape(sr.shape.__geo_interface__)))
    out = {}
    for st, gs in byst.items():
        u = make_valid(unary_union(gs))
        # the Aleutians cross the antimeridian; shift the far side west so the
        # state is one connected shape in the projection rather than two
        if st == "AK":
            polys = []
            for p in (u.geoms if isinstance(u, MultiPolygon) else [u]):
                if p.centroid.x > 0:
                    p = Polygon([(x - 360, y) for x, y in p.exterior.coords])
                polys.append(p)
            u = MultiPolygon([p for p in polys if p.area > 0])
        out[st] = u
    return out


def rivers(land):
    """The river layer, merged into whole courses before it is clipped.

    WDBII draws a river as a string of separate arcs. Left that way, no single
    piece runs the length of the Mississippi, and a river cannot be identified
    by finding the piece nearest to two points far apart on it. Merging the
    arcs that share endpoints rebuilds the courses first.
    """
    from shapely.ops import linemerge
    # a cheap box filter first: intersecting thousands of arcs against a
    # coastline with a hundred thousand vertices is far slower than it needs
    # to be, and the boxes throw away every arc on another continent
    boxes = [box(f[0], f[1], f[2], f[3]) for f in
             [(-125.5, 24.0, -66.0, 50.0), (-180.0, 50.0, -128.0, 72.0),
              (-161.0, 18.0, -154.0, 23.0)]]
    segs = []
    for s in read_wdb("rivers"):
        if len(s) < 2:
            continue
        lo, la = s[:, 0], s[:, 1]
        if not any(b.bounds[0] < lo.max() and b.bounds[2] > lo.min()
                   and b.bounds[1] < la.max() and b.bounds[3] > la.min()
                   for b in boxes):
            continue
        segs.append(LineString(s))
    near = segs
    merged = linemerge(near)
    chains = list(merged.geoms) if merged.geom_type == "MultiLineString" else [merged]
    print(f"  {len(near)} arcs merged into {len(chains)} courses")
    keep = []
    for L in chains:
        if not L.intersects(land):
            continue
        c = L.intersection(land)
        for g in (c.geoms if c.geom_type.startswith("Multi") else [c]):
            if g.geom_type == "LineString" and len(g.coords) > 1:
                keep.append(g)
    return keep, chains


def roughness(frame):
    W, E, S, N = frame
    im = Image.open(BM / "shadedrelief.jpg")
    ppd = im.size[0] / 360.0
    crop = im.crop((int((W + 180) * ppd), int((90 - N) * ppd),
                    int((E + 180) * ppd), int((90 - S) * ppd)))
    a = np.asarray(crop).astype(float)
    lum = 0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]
    return lum, ppd


def main():
    OUT.mkdir(exist_ok=True)
    st = states()
    print(f"states: {len(st)} dissolved from counties")
    for k in ("TX", "CA", "AK", "HI", "RI"):
        print(f"  {k} {sph_area_km2(st[k]):,.0f} km2")
    pickle.dump(st, open(OUT / "states.pkl", "wb"))

    land = make_valid(unary_union([g for k, g in st.items() if k != "PR"]))
    pickle.dump(land, open(OUT / "land.pkl", "wb"))
    riv, chains = rivers(land)
    riv.sort(key=lambda g: -g.length)
    chains.sort(key=lambda g: -g.length)
    print(f"rivers: {len(riv)} pieces inside the country, "
          f"{len(chains)} whole courses")
    pickle.dump(riv, open(OUT / "rivers.pkl", "wb"))
    pickle.dump(chains, open(OUT / "courses.pkl", "wb"))

    np.save(OUT / "conus_lum.npy", roughness(FRAMES["conus"])[0])
    print("relief cropped for the lower 48")


if __name__ == "__main__":
    main()


# ---------- rugged ground ----------
# Reference places, chosen before the threshold was set and not used to set it.
# Ten that have to come out rough and ten that have to come out smooth.
ROUGH_REF = [
    ("the Rockies at Leadville", 39.25, -106.29),
    ("the Sierra Nevada", 37.00, -118.60),
    ("the Cascades at Rainier", 46.85, -121.76),
    ("the Blue Ridge at Mount Mitchell", 35.76, -82.26),
    ("the Great Smokies", 35.56, -83.50),
    ("the Wasatch", 40.60, -111.60),
    ("the Bitterroots", 45.90, -114.40),
    ("the Sangre de Cristo", 37.60, -105.50),
    ("the Adirondacks", 44.11, -73.92),
    ("the Black Hills", 44.00, -103.50),
]
SMOOTH_REF = [
    ("the Central Valley", 36.70, -119.80),
    ("the Sacramento Valley", 39.00, -121.90),
    ("the Kansas plains", 38.50, -98.50),
    ("central Illinois", 40.00, -89.00),
    ("the Mississippi delta", 32.50, -90.80),
    ("central Florida", 28.00, -81.50),
    ("the Red River valley", 47.50, -97.00),
    ("the Nebraska plains", 41.00, -99.00),
    ("the Carolina coastal plain", 35.30, -77.50),
    ("the Texas gulf coast", 29.80, -95.40),
]


def rugged(frame, lum, land, tiers=TIERS):
    """Contour the ground that is broken, and say how broken."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.path import Path as MPath

    W, E, S, N = frame
    H, Wd = lum.shape
    # rasterise the land so windows touching the sea can be dropped
    fig = plt.figure(figsize=(Wd / 100, H / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(W, E)
    ax.set_ylim(S, N)
    ax.axis("off")
    polys = land.geoms if land.geom_type == "MultiPolygon" else [land]
    for p in polys:
        ax.fill(*p.exterior.xy, color="k")
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())[:, :, 0]
    plt.close(fig)
    onland = buf < 128
    if onland.shape != lum.shape:
        onland = np.array(Image.fromarray(onland.astype(np.uint8) * 255)
                          .resize((Wd, H))) > 128

    k = np.ones((WIN, WIN))
    n = ndi.convolve(onland.astype(float), k, mode="nearest")
    s1 = ndi.convolve(np.where(onland, lum, 0.0), k, mode="nearest")
    s2 = ndi.convolve(np.where(onland, lum * lum, 0.0), k, mode="nearest")
    full = n >= WIN * WIN - 0.5          # every cell in the window is land
    var = np.where(full, s2 / np.maximum(n, 1) - (s1 / np.maximum(n, 1)) ** 2, 0)
    rough = np.sqrt(np.maximum(var, 0))
    rough = ndi.gaussian_filter(rough, 1.6)
    rough = np.where(onland, rough, 0)
    # A contour that runs off the edge of the grid gets closed by a straight
    # line across it, which puts a huge wedge of false mountain on the map. A
    # border of zeros means every contour closes inside the grid instead.
    rough = np.pad(rough, 1)
    H, Wd = rough.shape
    dx, dy = (E - W) / (Wd - 2), (N - S) / (H - 2)
    W, E, S, N = W - dx, E + dx, S - dy, N + dy

    def at(lat, lon):
        r = int((N - lat) / (N - S) * H)
        c = int((lon - W) / (E - W) * Wd)
        return rough[max(0, min(H - 1, r)), max(0, min(Wd - 1, c))]

    out = {}
    for name, floor, minkm2 in tiers:
        cs = plt.contour(np.linspace(W, E, Wd), np.linspace(N, S, H),
                         rough, levels=[floor])
        got = []
        for seg in cs.allsegs[0]:
            if len(seg) < 4:
                continue
            p = Polygon(seg)
            if not p.is_valid:
                p = make_valid(p)
            if p.geom_type != "Polygon" or sph_area_km2(p) < minkm2:
                continue
            got.append(p)
        plt.close("all")
        out[name] = got
        print(f"  {name}: {len(got)} areas above {floor}")
    return out, at
