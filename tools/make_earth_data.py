#!/usr/bin/env python3
"""Build the two raster layers earth.html is drawn from.

Continents come from GSHHG, the shoreline data distributed with
basemap-data-hires. Level 1 is land, 2 lakes, 3 islands inside lakes, 5 the
Antarctic ice front. The useful thing about that data is that Africa, Eurasia,
the two Americas and Australia are already separate polygons, so no isthmus has
to be found and cut; the Suez Canal and the Panama Canal are in the data.

Three things still have to be decided rather than read:

  Europe and Asia are one landmass. They are parted along the Urals, down the
  Ural river to the Caspian, across the Kuma-Manych depression to the Black Sea,
  and through the Bosphorus.

  GSHHG cuts the Americas at the Panama Canal, but the conventional boundary is
  the Colombia border, 200 km further east. The strip between the two is moved
  back to North America.

  Islands belong to whichever continent convention puts them in, not to whatever
  is nearest. Named ones are listed; the Indonesian archipelago and the Pacific
  are covered by a box each; anything still unplaced goes to the nearest land.

Climates come from the Koppen-Geiger present-day map of Beck et al. 2018 at
1 km, as redistributed in the kgcpy package, reduced to the five main groups by
first letter. Downsampling is a majority vote over land classes only, so a
coastal block keeps a real climate instead of being outvoted by the sea.

Usage: pip install kgcpy basemap-data-hires pyshp scipy pillow
       python3 make_earth_data.py     (writes /home/claude/earth/*.npy, mix.json)
"""

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

GSHHG = Path("/usr/local/lib/python3.11/dist-packages/mpl_toolkits/basemap_data")
OUT = Path("/home/claude/earth")
W, H = 2160, 1080                      # a sixth of a degree
SRC = 6                                # Koppen is 1/36 deg, so 6x6 blocks

CONT = ["Africa", "Asia", "Europe", "North America", "South America",
        "Antarctica", "Australia and Oceania"]
IDX = {n: i + 1 for i, n in enumerate(CONT)}

# GSHHG polygon ids that are a continent on their own
MAJOR = {"0-E": "Eurasia", "0-W": "Eurasia", "1": "Africa",
         "2": "North America", "3": "South America",
         "6": "Australia and Oceania"}

# Europe stops here. Latitude to the longitude of the divide, north of 46.
URAL = [(46, 47.5), (47, 51.8), (49, 54), (51.5, 58), (55, 59), (58, 59.5),
        (61, 59), (64, 59.5), (66, 62), (68.3, 66.5), (71, 66.5)]

# The Panama and Colombia border, Caribbean end to Pacific end
DARIEN = [(8.67, -77.36), (7.22, -77.90)]

ISLANDS = {
    "Africa": [(-19, 47), (-20.3, 57.6), (-12.2, 44.4), (-4.6, 55.5)],
    "Asia": [(0, 114), (-0.5, 101.5), (-7.3, 110), (-2, 120), (12, 122),
             (-9, 125.5), (23.7, 121), (36, 138), (43, 142), (7.5, 80.7),
             (-3, 129), (1, 127.5), (-8.5, 120.5), (35, 33), (11.7, 92.7)],
    "Europe": [(54, -2), (53, -8), (64.9, -18.5), (40, 9), (37.5, 14.5),
               (35, 25), (78, 16), (39.5, 3), (62, -6.8)],
    "North America": [(72, -42), (21.8, -79), (19, -71), (48.5, -56),
                      (79, -80), (18.2, -66.5), (13.2, -59.5), (24.2, -77.9)],
    "South America": [(-0.5, -90.5), (-51.7, -59), (-54, -68.3)],
    "Australia and Oceania": [(-5, 141), (-43.5, 172), (-36.9, 174.8),
                              (-42, 146.5), (19.6, -155.5), (-17.8, 178),
                              (-6, 155), (9.5, 138), (-21, 165), (-13.8, -172)],
}
# Anything left in one of these boxes follows the usual grouping
BOXES = [(-12, 8, 94, 140, "Asia"),                  # the Indonesian archipelago
         (-50, 30, 140, 180, "Australia and Oceania"),
         (-50, 30, -180, -130, "Australia and Oceania")]


def px(lat, lon):
    return (int(round((90 - lat) * H / 180 - 0.5)),
            int(round((lon + 180) * W / 360 - 0.5)))


def main():
    meta = [l.split() for l in open(GSHHG / "gshhsmeta_h.dat")]
    recs = [dict(level=int(m[0]), n=int(m[2]), off=int(m[5]), id=m[7]) for m in meta]
    raw = open(GSHHG / "gshhs_h.dat", "rb").read()

    def rings(r):
        a = np.frombuffer(raw, "<f4", count=2 * r["n"],
                          offset=r["off"]).reshape(-1, 2).astype(float)
        lon = a[:, 0].copy()
        lon[lon > 180] -= 360
        pts = np.column_stack([lon, a[:, 1]])
        return np.split(pts, np.where(np.abs(np.diff(lon)) > 180)[0] + 1)

    def paint(sel, val, into):
        im = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(im)
        for r in sel:
            for part in rings(r):
                if len(part) >= 3:
                    d.polygon(list(zip((part[:, 0] + 180) * W / 360,
                                       (90 - part[:, 1]) * H / 180)), fill=255)
        into[np.asarray(im) > 0] = val
        return into

    cid = np.zeros((H, W), np.uint8)
    for pid, name in MAJOR.items():
        paint([r for r in recs if r["id"] == pid],
              99 if name == "Eurasia" else IDX[name], cid)
    paint([r for r in recs if r["level"] == 5], IDX["Antarctica"], cid)
    paint([r for r in recs if r["level"] == 1 and r["id"] not in MAJOR], 200, cid)
    lakes = paint([r for r in recs if r["level"] == 2], 1, np.zeros((H, W), np.uint8))
    inlake = paint([r for r in recs if r["level"] == 3], 1, np.zeros((H, W), np.uint8))
    cid[(lakes > 0) & (inlake == 0)] = 0
    print(f"painted: land is {(cid > 0).mean() * 100:.1f}% of the grid")

    lat2d = np.repeat((90 - (np.arange(H) + 0.5) * 180 / H)[:, None], W, 1)
    lon2d = np.repeat((-180 + (np.arange(W) + 0.5) * 360 / W)[None, :], H, 0)

    ul = np.array([p[0] for p in URAL])
    uo = np.array([p[1] for p in URAL])
    eu = np.zeros((H, W), bool)
    hi = lat2d >= 46
    eu[hi] = lon2d[hi] <= np.interp(lat2d[hi], ul, uo)
    band = (lat2d >= 45.8) & (lat2d < 46)
    eu[band] = lon2d[band] <= 47.5
    low = lat2d < 45.8
    eu[low] = lon2d[low] < 29.5
    euro = (cid == 99) & eu
    cid[cid == 99] = IDX["Asia"]
    cid[euro] = IDX["Europe"]
    print(f"Europe: {int(euro.sum()):,} pixels west of the divide")

    # GSHHG parts the Americas at the canal; the convention is the Darien
    (la1, lo1), (la2, lo2) = DARIEN
    border = lo2 + (lat2d - la2) * (lo1 - lo2) / (la1 - la2)
    strip = ((cid == IDX["South America"]) & (lat2d > 6.6) & (lat2d < 9.9)
             & (lon2d > -79.9) & (lon2d < np.clip(border, -79.9, -77.0)))
    cid[strip] = IDX["North America"]
    print(f"Darien: {int(strip.sum()):,} pixels moved to North America")

    isl = cid == 200
    ilab, ni = ndi.label(isl, structure=np.ones((3, 3)))
    for name, pts in ISLANDS.items():
        for la, lo in pts:
            r, c = px(la, lo)
            k = ilab[r, c]
            if k:
                cid[ilab == k] = IDX[name]
            else:
                print(f"  ! the seed for {name} at {la},{lo} is not on an island")
    ctr = ndi.center_of_mass(cid == 200, ilab, range(1, ni + 1))
    for k, (r, c) in enumerate(ctr, 1):
        if np.isnan(r):
            continue
        la, lo = 90 - (r + 0.5) * 180 / H, -180 + (c + 0.5) * 360 / W
        for s, n, w, e, name in BOXES:
            if s <= la <= n and w <= lo <= e:
                cid[(ilab == k) & (cid == 200)] = IDX[name]
                break
    known = (cid > 0) & (cid != 200)
    _, idx = ndi.distance_transform_edt(~known, return_indices=True)
    rest = cid == 200
    print(f"islands: {int(rest.sum()):,} pixels fall back to the nearest land")
    cid[rest] = cid[idx[0][rest], idx[1][rest]]

    # ---- climates ----
    import kgcpy
    a = np.asarray(kgcpy.img)
    grp = np.zeros(33, np.uint8)
    grp[1:5], grp[5:9], grp[9:18], grp[18:30], grp[30:32] = 1, 2, 3, 4, 5
    g = grp[a]
    blocks = g.reshape(H, SRC, W, SRC).transpose(0, 2, 1, 3).reshape(H, W, SRC * SRC)
    counts = np.stack([(blocks == v).sum(2) for v in range(1, 6)], axis=2)
    clim = (counts.argmax(2) + 1).astype(np.uint8)
    clim[counts.max(2) == 0] = 0
    clim = np.where(cid > 0, clim, 0).astype(np.uint8)
    gap = (cid > 0) & (clim == 0)
    if gap.any():
        have = clim > 0
        _, idx = ndi.distance_transform_edt(~have, return_indices=True)
        clim[gap] = clim[idx[0][gap], idx[1][gap]]
        print(f"climate: {int(gap.sum()):,} land pixels filled from the nearest classified land")

    wt = np.repeat(np.cos(np.radians(90 - (np.arange(H) + 0.5) * 180 / H))[:, None], W, 1)
    mix = {}
    for i, nm in enumerate(CONT, 1):
        m = cid == i
        t = wt[m].sum()
        mix[nm] = {"mix": [round(float(wt[m & (clim == k)].sum() / t * 100), 1)
                           for k in range(1, 6)],
                   "measured_share_of_land": round(float(t / wt[cid > 0].sum() * 100), 2)}
    m = cid > 0
    t = wt[m].sum()
    mix["_all land"] = {"mix": [round(float(wt[m & (clim == k)].sum() / t * 100), 1)
                                for k in range(1, 6)]}

    OUT.mkdir(exist_ok=True)
    np.save(OUT / "cid.npy", cid)
    np.save(OUT / "clim.npy", clim)
    json.dump(mix, open(OUT / "mix.json", "w"), indent=1)
    print(f"wrote {OUT}/cid.npy, clim.npy, mix.json")


if __name__ == "__main__":
    main()
