#!/usr/bin/env python3
"""Build the rugged-ground layer for norte-mexico.html.

There is no elevation grid in the datasets available here, and no mountain
range polygon in any of them either. What there is, bundled with basemap-data,
is Natural Earth's shaded relief raster at two arc minutes. Rugged ground shows
up in it as high-frequency light and dark texture, while basins and plains are
smooth, so the local variation of that raster is a usable measure of how broken
the ground is.

The procedure:
  1. crop the raster to the map frame and take its luminance
  2. compute the standard deviation of luminance in a 5 by 5 window, counting
     land pixels only. A window that touches the sea is dropped: the shoreline
     is a brightness step in the image and would read as a mountain
  3. smooth, threshold, contour, and keep the areas above a floor size

The threshold was chosen against twenty reference locations that were not used
to build the layer: ten sierras that must be inside it and ten basins, plains
and deltas that must not. At 14 all ten sierras are captured and nine of the
ten flats are excluded. verify_norte.py re-runs that test on every build.

Two tiers come out of it: "sierra" at 14, and "alta" at 24 for the crests.

This is a measure of terrain, not a published boundary of any named range. The
page says so, and only ranges whose position can be checked twice are labelled.

Usage: python3 make_sierras.py      (writes /home/claude/nmex/sierras.pkl)
"""

import pickle
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
from shapely.geometry import Point, Polygon, box  # noqa: E402
from shapely.ops import unary_union  # noqa: E402
from shapely.prepared import prep  # noqa: E402
from shapely.validation import make_valid  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
RELIEF = Path("/usr/local/lib/python3.11/dist-packages/mpl_toolkits"
              "/basemap_data/shadedrelief.jpg")
DATA = Path("/home/claude/nmex")

W, E, S, N = -118.4, -96.4, 21.2, 33.3      # same frame as build_norte.py
WIN = 5                                      # roughness window, ~9 km
TIERS = [("sierra", 14.0, 900.0), ("alta", 24.0, 500.0)]   # name, floor, min km2

im = Image.open(RELIEF)
ppd = im.size[0] / 360.0
crop = im.crop((int((W + 180) * ppd), int((90 - N) * ppd),
                int((E + 180) * ppd), int((90 - S) * ppd)))
a = np.asarray(crop).astype(float)
lum = 0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]
H, Wd = lum.shape
print(f"relief {im.size} -> {Wd} by {H} px at {60/ppd:.0f} arc minutes")

land = pickle.load(open(DATA / "land.pkl", "rb")).intersection(box(W, S, E, N))
pl = prep(land)
lons = W + (np.arange(Wd) + 0.5) / ppd
lats = N - (np.arange(H) + 0.5) / ppd
mask = np.array([[pl.contains(Point(lo, la)) for lo in lons] for la in lats])
print(f"{mask.sum():,} land pixels of {mask.size:,}")

h = WIN // 2
Lp = np.pad(lum, h, mode="edge")
Mp = np.pad(mask.astype(float), h, mode="edge")
s1 = np.zeros((H, Wd)); s2 = np.zeros((H, Wd))
n = np.zeros((H, Wd)); allland = np.ones((H, Wd), bool)
for dy in range(WIN):
    for dx in range(WIN):
        v = Lp[dy:dy + H, dx:dx + Wd]
        m = Mp[dy:dy + H, dx:dx + Wd] > 0
        s1 += np.where(m, v, 0); s2 += np.where(m, v * v, 0)
        n += m; allland &= m
n = np.maximum(n, 1)
rough = np.sqrt(np.maximum(s2 / n - (s1 / n) ** 2, 0))
rough[~allland] = 0.0          # a window touching the shore is not evidence
rough[~mask] = 0.0


def box_blur(x, k):
    p = np.pad(x, k // 2, mode="edge")
    out = np.zeros_like(x)
    for dy in range(k):
        for dx in range(k):
            out += p[dy:dy + x.shape[0], dx:dx + x.shape[1]]
    return out / (k * k)


rs = box_blur(rough, 5)


def km2(g):
    b = g.bounds
    return g.area * (111.32 ** 2) * np.cos(np.radians((b[1] + b[3]) / 2))


out = {}
for name, floor, min_km2 in TIERS:
    fig = plt.figure(); ax = fig.add_subplot(111)
    cs = ax.contourf(lons, lats, rs, levels=[floor, 1e9])
    polys = []
    for path in cs.get_paths():
        for ring in path.to_polygons(closed_only=True):
            if len(ring) > 3:
                g = Polygon(ring)
                if not g.is_valid:
                    g = make_valid(g)
                if g.geom_type in ("Polygon", "MultiPolygon"):
                    polys.append(g)
    plt.close(fig)
    g = unary_union(polys).intersection(land)
    parts = [q for q in (g.geoms if hasattr(g, "geoms") else [g])
             if q.geom_type == "Polygon"]
    keep = [q.simplify(0.012) for q in parts if km2(q) >= min_km2]
    out[name] = unary_union(keep)
    print(f"{name:7} floor {floor:4}  {len(keep):3} areas kept of {len(parts):3},"
          f" {sum(km2(q) for q in keep):>9,.0f} km2 in the frame")

DATA.mkdir(exist_ok=True)
pickle.dump(out, open(DATA / "sierras.pkl", "wb"))
print(f"wrote {DATA / 'sierras.pkl'}")
