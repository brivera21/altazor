#!/usr/bin/env python3
"""Build the continent outlines the reconstruction rotates.

The plate model moves rigid plates, so every piece of land has to be given a
plate to ride on. The seven continents already rasterised for Earth's Climate
are used, with two edits that matter for deep time:

  India is cut out of Asia and given plate 501. It spent most of the last
  billion years attached to Gondwana, not to Eurasia, and leaving it on the
  Eurasian plate would hide the whole journey.

  Arabia is cut out of Asia and given Africa's plate 701. The Red Sea only
  opened in the last twenty five million years; before that it was Africa.

Both cuts are boxes rather than sutures, which is coarse. They are drawn as
boxes on purpose: a real suture line would imply a precision the rest of this
has no claim to.

The outlines are contoured off the raster and simplified hard. At the size the
page draws them, three hundred pixels across a whole world, a degree and a half
is well under a pixel.

Usage: python3 make_paleo.py      (writes /home/claude/paleo/outlines.json)
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from rotations import CONTINENT_TO_PLATE, PLATE_NAMES  # noqa: E402

DATA = Path("/home/claude/earth")
OUT = Path("/home/claude/paleo")

CONT = ["Africa", "Asia", "Europe", "North America", "South America",
        "Antarctica", "Australia and Oceania"]
# the raster's own numbering, from make_earth_data.py
IDX = {n: i + 1 for i, n in enumerate(CONT)}

# south, north, west, east
INDIA = (5.0, 33.0, 67.0, 92.0)
ARABIA = (11.0, 33.0, 33.0, 60.0)

SIMPLIFY = 1.5          # degrees
MIN_AREA = 12.0         # square degrees, which drops the small islands


def main():
    OUT.mkdir(exist_ok=True)
    cid = np.load(DATA / "cid.npy")
    H, W = cid.shape
    lat = 90 - (np.arange(H) + 0.5) * 180 / H
    lon = -180 + (np.arange(W) + 0.5) * 360 / W
    la2 = np.repeat(lat[:, None], W, 1)
    lo2 = np.repeat(lon[None, :], H, 0)

    plate = np.zeros((H, W), np.int32)
    for name, i in IDX.items():
        key = "Australia" if name.startswith("Australia") else name
        plate[cid == i] = CONTINENT_TO_PLATE[key]
    for box, pid in [(INDIA, 501), (ARABIA, 701)]:
        s, n, w, e = box
        m = (cid == IDX["Asia"]) & (la2 >= s) & (la2 <= n) & (lo2 >= w) & (lo2 <= e)
        plate[m] = pid
        print(f"  {int(m.sum()):,} pixels moved to plate {pid} "
              f"({PLATE_NAMES[pid].split(' (')[0]})")

    # contour each plate's land at half a step, on a coarser grid
    step = 3
    small = plate[::step, ::step]
    slat = lat[::step]
    slon = lon[::step]
    out = {}
    for pid in sorted(set(plate.ravel()) - {0}):
        mask = (small == pid).astype(float)
        # a border of zeros so every contour closes inside the grid
        m = np.pad(mask, 1)
        xs = np.concatenate([[slon[0] - step * 360 / W], slon,
                             [slon[-1] + step * 360 / W]])
        ys = np.concatenate([[slat[0] + step * 180 / H], slat,
                             [slat[-1] - step * 180 / H]])
        cs = plt.contour(xs, ys, m, levels=[0.5])
        rings = []
        for seg in cs.allsegs[0]:
            if len(seg) < 4:
                continue
            a = abs(np.sum(seg[:-1, 0] * seg[1:, 1] - seg[1:, 0] * seg[:-1, 1])) / 2
            if a < MIN_AREA:
                continue
            rings.append(simplify(seg, SIMPLIFY))
        plt.close("all")
        rings.sort(key=len, reverse=True)
        out[str(pid)] = [[[round(x, 2), round(y, 2)] for x, y in r]
                         for r in rings]
        pts = sum(len(r) for r in rings)
        print(f"  plate {pid}: {len(rings)} rings, {pts} points "
              f"({PLATE_NAMES[pid].split(' (')[0]})")

    json.dump(out, open(OUT / "outlines.json", "w"))
    total = sum(sum(len(r) for r in v) for v in out.values())
    print(f"wrote {OUT}/outlines.json: {len(out)} plates, {total} points")


def simplify(pts, tol):
    """Douglas-Peucker, so the outline keeps its shape and loses its vertices."""
    pts = np.asarray(pts)
    keep = np.zeros(len(pts), bool)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        a, b = pts[i], pts[j]
        d = b - a
        n = np.hypot(*d)
        if n < 1e-9:
            dist = np.hypot(*(pts[i + 1:j] - a).T)
        else:
            dist = np.abs(np.cross(d, pts[i + 1:j] - a)) / n
        k = int(np.argmax(dist))
        if dist[k] > tol:
            keep[i + 1 + k] = True
            stack.append((i, i + 1 + k))
            stack.append((i + 1 + k, j))
    return pts[keep]


if __name__ == "__main__":
    main()
