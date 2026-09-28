#!/usr/bin/env python3
"""Trace the shapes for brain.html from real brains, and write them to
tools/brain_shapes.json for build_brain.py.

The outside view is the left hemisphere of fsaverage, FreeSurfer's average of
forty brains, seen from the left: its pial surface is projected with a depth
buffer, each visible point takes the Desikan-Killiany region of the nearest
vertex, and the lobes, strips and patches are traced from that. The folds are
the surface's sulcal depth: where a point lies deeper than its surroundings it
is inside a sulcus, and those areas are drawn dark. The cerebellum and the
brainstem are not on the cortical surface, so they come from the MNI152
template's Neuromorphometrics labels, projected from the same side and fitted
to the surface's frame by its bounding box.

The inside view is a cut through the MNI152 template (ICBM 2009c) 4 mm to the
right of the midline. The outline, the folds of the inner face and the white
matter (the corpus callosum, the tree in the cerebellum) are traced from the
image itself; the thalamus, the brainstem, the cerebellum, the cingulate gyrus
and the ventral diencephalon come from the Neuromorphometrics labels in the
same space. The hippocampus, the amygdala and the basal ganglia lie off to the
side, so their whole outlines are projected onto the cut and drawn dashed. The
pituitary is not in the template, which ends at the brain; it is placed below
the optic chiasm, where it hangs.

Sources, all fetched the first time this runs:
  fsaverage5 pial surface and sulcal depth   bundled with nilearn (pip)
  Desikan-Killiany labels on fsaverage5      ENIGMA Toolbox, raw GitHub
  MNI152 2009c template, Neuromorphometrics  bundled with atlasreader (pip)

Usage: python3 brain_geometry.py
"""

import json
import os
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
CACHE = Path(os.environ.get("BRAIN_CACHE", "/tmp/brain_cache"))
OUT = HERE / "brain_shapes.json"
ENIGMA = ("https://raw.githubusercontent.com/MICA-MNI/ENIGMA/master/"
          "enigmatoolbox/datasets/parcellations/aparc_fsa5.csv")

# SVG frame: millimeters of MNI space to the 980-wide viewBox, front on the left
S = 3.9                      # px per mm
X0, Y0 = 470.0, 330.0        # where y = -18 mm, z = 12 mm lands
YC, ZC = -18.0, 12.0
def to_svg(y, z):
    return X0 - S * (y - YC), Y0 - S * (z - ZC)

DK = ("unknown bankssts caudalanteriorcingulate caudalmiddlefrontal corpuscallosum cuneus "
      "entorhinal fusiform inferiorparietal inferiortemporal isthmuscingulate lateraloccipital "
      "lateralorbitofrontal lingual medialorbitofrontal middletemporal parahippocampal paracentral "
      "parsopercularis parsorbitalis parstriangularis pericalcarine postcentral posteriorcingulate "
      "precentral precuneus rostralanteriorcingulate rostralmiddlefrontal superiorfrontal "
      "superiorparietal superiortemporal supramarginal frontalpole temporalpole transversetemporal "
      "insula").split()
LOBE = {}
for n in ("caudalmiddlefrontal lateralorbitofrontal medialorbitofrontal paracentral parsopercularis "
          "parsorbitalis parstriangularis precentral rostralmiddlefrontal superiorfrontal frontalpole").split():
    LOBE[DK.index(n)] = "frontal"
for n in "inferiorparietal postcentral precuneus superiorparietal supramarginal".split():
    LOBE[DK.index(n)] = "parietal"
for n in ("bankssts entorhinal fusiform inferiortemporal middletemporal parahippocampal "
          "superiortemporal temporalpole transversetemporal").split():
    LOBE[DK.index(n)] = "temporal"
for n in "cuneus lateraloccipital lingual pericalcarine".split():
    LOBE[DK.index(n)] = "occipital"


# ---------- data ----------
def fetch():
    CACHE.mkdir(parents=True, exist_ok=True)
    csv = CACHE / "aparc_fsa5.csv"
    if not csv.exists():
        urllib.request.urlretrieve(ENIGMA, csv)
    ar = CACHE / "atlasreader"
    if not ar.exists():
        subprocess.run([sys.executable, "-m", "pip", "download", "atlasreader==0.3.2", "--no-deps",
                        "-d", str(CACHE), "-q"], check=True)
        whl = next(CACHE.glob("atlasreader-*.whl"))
        with zipfile.ZipFile(whl) as z:
            z.extractall(CACHE)
    return csv, ar / "data"


def fsaverage(hemi):
    import nibabel as nib
    import nilearn
    d = Path(nilearn.__file__).parent / "datasets" / "data" / "fsaverage5"
    v, f = [a.data for a in nib.load(d / f"pial_{hemi}.gii.gz").darrays]
    sulc = nib.load(d / f"sulc_{hemi}.gii.gz").darrays[0].data
    return v.astype(float), f.astype(int), sulc.astype(float)


# ---------- raster and trace ----------
RES = 0.25                   # mm per raster pixel
SULC = 0.30                  # sulcal depth past which a point is drawn as inside a fold
YMIN, YMAX, ZMIN, ZMAX = -112.0, 78.0, -80.0, 86.0
NU, NV = int((YMAX - YMIN) / RES), int((ZMAX - ZMIN) / RES)
def uv(y, z):                # raster column (front on the left) and row (top first)
    return (YMAX - y) / RES, (ZMAX - z) / RES
def rc_to_mm(r, c):
    return YMAX - c * RES, ZMAX - r * RES


def rasterize(v, f, depth_sign):
    """Depth-buffered projection along x. depth_sign +1 sees the smallest x
    first (a viewer on the left). Returns the index of the triangle seen at
    each pixel (-1 where none) and the barycentric weights there."""
    u, w = uv(v[:, 1], v[:, 2])
    d = depth_sign * v[:, 0]
    zbuf = np.full((NV, NU), np.inf)
    tri = np.full((NV, NU), -1, int)
    bary = np.zeros((NV, NU, 3))
    for t, (a, b, c) in enumerate(f):
        xs, ys = np.array([u[a], u[b], u[c]]), np.array([w[a], w[b], w[c]])
        c0, c1 = int(np.floor(xs.min())), int(np.ceil(xs.max()))
        r0, r1 = int(np.floor(ys.min())), int(np.ceil(ys.max()))
        if c1 < 0 or r1 < 0 or c0 >= NU or r0 >= NV:
            continue
        c0, r0, c1, r1 = max(c0, 0), max(r0, 0), min(c1, NU - 1), min(r1, NV - 1)
        cc, rr = np.meshgrid(np.arange(c0, c1 + 1) + 0.5, np.arange(r0, r1 + 1) + 0.5)
        den = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
        if abs(den) < 1e-12:
            continue
        l0 = ((ys[1] - ys[2]) * (cc - xs[2]) + (xs[2] - xs[1]) * (rr - ys[2])) / den
        l1 = ((ys[2] - ys[0]) * (cc - xs[2]) + (xs[0] - xs[2]) * (rr - ys[2])) / den
        l2 = 1 - l0 - l1
        inside = (l0 >= -1e-9) & (l1 >= -1e-9) & (l2 >= -1e-9)
        if not inside.any():
            continue
        dd = l0 * d[a] + l1 * d[b] + l2 * d[c]
        sub = zbuf[r0:r1 + 1, c0:c1 + 1]
        win = inside & (dd < sub)
        sub[win] = dd[win]
        tri[r0:r1 + 1, c0:c1 + 1][win] = t
        bary[r0:r1 + 1, c0:c1 + 1][win] = np.stack([l0, l1, l2], -1)[win]
    return tri, bary


def trace(mask, tol=0.7, min_area=0.0):
    """SVG path data for a raster mask, in viewBox units, holes kept."""
    from skimage import measure
    m = np.pad(mask.astype(float), 1)
    out = []
    for cnt in measure.find_contours(m, 0.5):
        cnt = cnt - 1                                    # undo the pad
        if len(cnt) < 4:
            continue
        cnt = measure.approximate_polygon(cnt, tolerance=tol / (S * RES))
        pts = [to_svg(*rc_to_mm(r + 0.5, c + 0.5)) for r, c in cnt]
        xs, ys = np.array([p[0] for p in pts]), np.array([p[1] for p in pts])
        area = 0.5 * abs(np.dot(xs, np.roll(ys, 1)) - np.dot(ys, np.roll(xs, 1)))
        if area < min_area:
            continue
        out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts[:-1]) + "Z")
    return "".join(out)


def probe(mask):
    """A point well inside the mask, in viewBox units: its deepest pixel."""
    from scipy import ndimage
    dist = ndimage.distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]
    r, c = np.unravel_index(np.argmax(dist), dist.shape)
    x, y = to_svg(*rc_to_mm(r + 0.5, c + 0.5))
    return [round(x, 1), round(y, 1)]


def smooth(mask, sigma_mm=0.6):
    from scipy import ndimage
    return ndimage.gaussian_filter(mask.astype(float), sigma_mm / RES) > 0.5


# ---------- volumes ----------
def volume_to_raster(vol, affine, xsel, reduce="any"):
    """Project a labeled volume along x onto the raster. xsel(x_mm) picks the
    slabs; 'any' keeps a voxel if any selected slab has it."""
    inv = np.linalg.inv(affine)
    rows, cols = np.mgrid[0:NV, 0:NU]
    ymm, zmm = rc_to_mm(rows + 0.5, cols + 0.5)
    nx = vol.shape[0]
    xs_mm = np.array([(affine @ [i, 0, 0, 1])[0] for i in range(nx)])
    keep = [i for i in range(nx) if xsel(xs_mm[i])]
    out = np.zeros((NV, NU), bool)
    for i in keep:
        x = xs_mm[i]
        ijk = inv @ np.stack([np.full(ymm.size, x), ymm.ravel(), zmm.ravel(), np.ones(ymm.size)])
        jj, kk = np.rint(ijk[1]).astype(int), np.rint(ijk[2]).astype(int)
        ok = (jj >= 0) & (jj < vol.shape[1]) & (kk >= 0) & (kk < vol.shape[2])
        val = np.zeros(ymm.size, bool)
        val[ok] = vol[i, jj[ok], kk[ok]]
        out |= val.reshape(NV, NU)
    return out


def slice_to_raster(img, affine, x_mm):
    """The image on the plane x = x_mm, sampled linearly onto the raster."""
    from scipy import ndimage
    inv = np.linalg.inv(affine)
    rows, cols = np.mgrid[0:NV, 0:NU]
    ymm, zmm = rc_to_mm(rows + 0.5, cols + 0.5)
    ijk = inv @ np.stack([np.full(ymm.size, x_mm), ymm.ravel(), zmm.ravel(), np.ones(ymm.size)])
    return ndimage.map_coordinates(img, ijk[:3], order=1, cval=0.0).reshape(NV, NU)


def fit_frame(src_mask, dst_mask):
    """Scale and shift, per axis, that carry src's bounding box onto dst's."""
    def box(m):
        r, c = np.nonzero(m)
        return r.min(), r.max(), c.min(), c.max()
    a, b = box(src_mask), box(dst_mask)
    sr = (b[1] - b[0]) / (a[1] - a[0]); sc = (b[3] - b[2]) / (a[3] - a[2])
    return sr, b[0] - a[0] * sr, sc, b[2] - a[2] * sc


def warp(mask, fr):
    from scipy import ndimage
    sr, tr, sc, tc = fr
    return ndimage.affine_transform(mask.astype(float), [1 / sr, 1 / sc],
                                    offset=[-tr / sr, -tc / sc], order=1) > 0.5


# ---------- the outside ----------
def outside(csv, data):
    import nibabel as nib
    v, f, sulc = fsaverage("left")
    lab = np.loadtxt(csv).astype(int)[:len(v)]
    tri, bary = rasterize(v, f, +1)                     # seen from the left
    seen = tri >= 0
    corner = np.argmax(bary, -1)
    vert = np.where(seen, f[np.maximum(tri, 0), corner], -1)
    L = np.where(seen, lab[np.maximum(vert, 0)], -1)
    sd = np.where(seen, (bary * sulc[f[np.maximum(tri, 0)]]).sum(-1), 0)

    cerebrum = smooth(seen)
    lobes = {}
    for k in ("frontal", "parietal", "temporal", "occipital"):
        ids = [i for i, n in LOBE.items() if n == k]
        lobes[k] = smooth(np.isin(L, ids)) & cerebrum
    # what the parcellation leaves unassigned on this face (the insula's rim)
    # goes to whichever lobe is nearest
    from scipy import ndimage
    lab_img = np.zeros(L.shape, int)
    for i, k in enumerate(lobes, 1):
        lab_img[lobes[k]] = i
    idx = ndimage.distance_transform_edt(lab_img == 0, return_distances=False, return_indices=True)
    filled = lab_img[idx[0], idx[1]] * cerebrum
    lobes = {k: filled == i for i, k in enumerate(lobes, 1)}

    sulci = smooth((sd > SULC) & cerebrum, 0.5)
    part = lambda *names: smooth(np.isin(L, [DK.index(n) for n in names]) & cerebrum, 0.5)
    motor, sensory = part("precentral"), part("postcentral")
    broca = part("parsopercularis", "parstriangularis")
    rows, cols = np.mgrid[0:NV, 0:NU]
    ymm = YMAX - (cols + 0.5) * RES
    wernicke = smooth((L == DK.index("superiortemporal")) & (ymm < -22) & cerebrum, 0.5)
    # hidden patches: the whole region projected, ignoring what covers it
    def projected(name):
        keep = np.isin(lab[f].max(1), [DK.index(name)]) & (lab[f] == DK.index(name)).all(1)
        t2, _ = rasterize(v, f[keep], +1)
        return smooth(t2 >= 0, 0.8)
    auditory, visual = projected("transversetemporal"), projected("pericalcarine")

    # cerebellum and brainstem from the template, fitted to this frame
    nm = nib.load(data / "atlases" / "atlas_neuromorphometrics.nii.gz")
    A, lv = nm.affine, np.rint(nm.get_fdata()).astype(int)
    left_cerebrum_ids = [45] + [int(r.split(",")[0]) for r in (data / "atlases" / "labels_neuromorphometrics.csv").read_text().splitlines()[1:]
                               if r.split(",")[1].startswith("Left_") and int(r.split(",")[0]) >= 100]
    vol_cerebrum = volume_to_raster(np.isin(lv, left_cerebrum_ids), A, lambda x: x < 0)
    fr = fit_frame(smooth(vol_cerebrum, 1.0), cerebrum)
    cb = warp(smooth(volume_to_raster(np.isin(lv, [38, 39, 40, 41, 71, 72, 73]), A, lambda x: True), 1.0), fr)
    bs = warp(smooth(volume_to_raster(lv == 35, A, lambda x: True), 1.0), fr)
    # the stalk runs on below the template's last slice, as the cord does
    bs_rows = np.nonzero(bs.any(1))[0]
    last = bs[bs_rows.max() - 2]
    bs[bs_rows.max() - 2:, :] |= last[None, :]
    bs &= rows < uv(0, -84)[1]

    # folia: lines across the cerebellum, bowed like its fissures
    r_, c_ = np.nonzero(cb)
    cy, cx = r_.mean(), c_.mean()
    folia = []
    for i in range(-5, 7):
        pts = []
        for t in np.linspace(-1.2, 1.2, 60):
            rr = cy + i * 3.2 / RES * 1.0 + (t ** 2) * 6 / RES
            cc = cx + t * 40 / RES
            pts.append((rr, cc))
        folia.append(pts)
    fol = []
    for pts in folia:
        seg, cur = [], []
        for rr, cc in pts:
            ri, ci = int(rr), int(cc)
            ok = 0 <= ri < NV and 0 <= ci < NU and cb[ri, ci] and not cerebrum[ri, ci]
            if ok:
                cur.append(to_svg(*rc_to_mm(rr, cc)))
            elif cur:
                seg.append(cur); cur = []
        if cur:
            seg.append(cur)
        for s in seg:
            if len(s) > 3:
                fol.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in s))

    shapes = {
        "outline": trace(cerebrum), "sulci": trace(sulci, 0.6, 6),
        "cerebellum": trace(cb), "brainstem": trace(bs), "folia": "".join(fol),
        **{k: trace(m) for k, m in lobes.items()},
        "motor": trace(motor), "sensory": trace(sensory), "broca": trace(broca),
        "wernicke": trace(wernicke), "auditory": trace(auditory), "visual": trace(visual),
    }
    hid = auditory | visual                              # drawn last, on top
    visible = {"frontal": lobes["frontal"] & ~motor & ~broca & ~hid, "parietal": lobes["parietal"] & ~sensory & ~hid,
               "temporal": lobes["temporal"] & ~wernicke & ~hid, "occipital": lobes["occipital"] & ~hid,
               "cerebellum": cb & ~cerebrum, "brainstem": bs & ~cerebrum & ~cb,
               "motor": motor & ~hid, "sensory": sensory & ~hid, "broca": broca & ~hid, "wernicke": wernicke & ~hid,
               "auditory": auditory, "visual": visual}
    probes = {k: probe(m) for k, m in visible.items()}
    r, c = np.nonzero(motor | sensory)
    i = np.argmin(r)
    top = [round(v, 1) for v in to_svg(*rc_to_mm(r[i], c[i]))]
    rb, cb_ = np.nonzero(bs)
    j = np.argmax(rb)
    stem_end = [round(v, 1) for v in to_svg(*rc_to_mm(rb[j], cb_[j]))]
    return shapes, probes, {"strip_top": top, "stem_end": stem_end}


# ---------- the inside ----------
def inside(data):
    import nibabel as nib
    from scipy import ndimage
    t1 = nib.load(data / "templates" / "mni_icbm152_t1_tal_nlin_asym_09c_brain.nii.gz")
    img = t1.get_fdata()
    XCUT = 4.0
    sl = slice_to_raster(img, t1.affine, XCUT)
    top = np.percentile(img[img > 0], 99.5)
    sl = sl / top
    tissue = smooth(sl > 0.28, 0.4)
    lab_ = ndimage.label(tissue)[0]
    tissue = lab_ == np.argmax(np.bincount(lab_.ravel())[1:]) + 1       # the brain, not stray voxels
    tissue = ndimage.binary_fill_holes(tissue)
    white = smooth(sl > 0.80, 0.3) & tissue
    # the folds: the template is an average, so a sulcus is a valley of
    # darker signal rather than a clean gap; a black top-hat finds valleys
    valley = ndimage.grey_closing(sl, size=int(4 / RES)) - sl
    csf = smooth((valley > 0.10) | (sl < 0.42), 0.35) & tissue

    nm = nib.load(data / "atlases" / "atlas_neuromorphometrics.nii.gz")
    A, lv = nm.affine, np.rint(nm.get_fdata()).astype(int)
    near = lambda ids, lo=XCUT - 1.5, hi=XCUT + 1.5: smooth(volume_to_raster(np.isin(lv, ids), A, lambda x: lo <= x <= hi), 0.8)
    whole = lambda ids: smooth(volume_to_raster(np.isin(lv, ids), A, lambda x: x > 0), 0.9)

    rows, cols = np.mgrid[0:NV, 0:NU]
    ymm, zmm = rc_to_mm(rows + 0.5, cols + 0.5)

    cerebellum = near([38, 40, 71, 72, 73], XCUT - 3, XCUT + 3) & tissue
    stem = near([35], XCUT - 4, XCUT + 4) & tissue
    thal = whole([59]) & tissue
    # the hypothalamus is the part of the ventral diencephalon that lines the
    # third ventricle: near the midline, in front of the mammillary bodies
    vdc = smooth(near([61], 0.0, 7.5) & (ymm > -16), 1.0) & tissue & ~thal
    # the corpus callosum: the white band above the thalamus, the largest
    # piece of white matter between the cingulate and the ventricles
    cc_zone = (zmm > 0) & (zmm < 36) & (ymm > -48) & (ymm < 42)
    wl = ndimage.label(white & cc_zone & ~cerebellum & ~stem)[0]
    sizes = np.bincount(wl.ravel()); sizes[0] = 0
    callosum = smooth(wl == np.argmax(sizes), 0.3)
    # the cingulate gyrus: the labeled band, cut at the sulcus that bounds it,
    # keeping only the pieces that sit on the corpus callosum
    band = near([100, 138, 166], XCUT - 2, XCUT + 2) & tissue & ~callosum & ~csf
    bl = ndimage.label(band)[0]
    touch = ndimage.binary_dilation(callosum, iterations=int(3 / RES))
    keep = [i for i in np.unique(bl[touch & (bl > 0)])]
    cing = smooth(np.isin(bl, keep), 1.0) & ~callosum
    # the brainstem split where anatomy splits it: the pons is the bulge in
    # front, from the notch under the midbrain to the notch above the medulla
    front = np.array([ymm[r][stem[r]].max() if stem[r].any() else np.nan for r in range(NV)])
    zrow = ZMAX - (np.arange(NV) + 0.5) * RES
    ok = ~np.isnan(front)
    fz = np.interp(np.arange(NV), np.nonzero(ok)[0], ndimage.gaussian_filter1d(front[ok], 1.5 / RES))
    step = np.gradient(fz)                       # per row, going down
    def edge(zlo, zhi, sign):
        rr = np.nonzero((zrow > zlo) & (zrow < zhi) & ok)[0]
        return zrow[rr[np.argmax(sign * step[rr])]]
    z_mid = edge(-32, -10, +1)                   # where the front jumps forward: the top of the pons
    z_med = edge(-58, -34, -1)                   # where it falls back: the top of the medulla
    midbrain = stem & (zmm >= z_mid)
    pons = stem & (zmm < z_mid) & (zmm >= z_med)
    medulla = stem & (zmm < z_med)
    # below the template: the cord, carried on at the medulla's width
    rr = np.nonzero(medulla.any(1))[0]
    base = medulla[rr.max() - 3]
    cord = np.zeros_like(medulla); cord[rr.max() - 3:, :] = base[None, :]
    cord &= zmm > -96
    medulla &= ~cord

    chiasm = whole([69])
    cr, cc = np.nonzero(chiasm)
    cy_, cz_ = rc_to_mm(cr.mean(), cc.mean())
    py, pz = cy_ - 5.0, cz_ - 13.0                                         # the pituitary's seat
    pit = ((ymm - py) / 6.0) ** 2 + ((zmm - pz) / 4.5) ** 2 <= 1
    stalk = [to_svg(cy_ - 3.0, cz_ - 2.0), to_svg(py + 0.5, pz + 4.2)]

    hippo, amyg = whole([47]), whole([31])
    basal = whole([36, 57, 55])

    arbor = smooth(sl > 0.80, 0.25) & cerebellum
    outline = tissue | stem | cord
    sulci = csf & ~cerebellum & ~stem & ~thal & outline
    sulci = ndimage.binary_opening(sulci, iterations=1)

    shapes = {
        "outline": trace(outline), "sulci": trace(sulci, 0.6, 5), 
        "cingulate": trace(cing), "callosum": trace(callosum),
        "thalamus": trace(thal), "hypothalamus": trace(vdc), "pituitary": trace(pit),
        "stalk": "M%.1f,%.1fL%.1f,%.1f" % (*stalk[0], *stalk[1]),
        "midbrain": trace(midbrain), "pons": trace(pons), "medulla": trace(medulla), "cord": trace(cord),
        "cerebellum": trace(cerebellum), "arbor": trace(arbor, 0.5, 2),
        "hippocampus": trace(hippo), "amygdala": trace(amyg), "basal": trace(basal),
    }
    probes = {k: probe(m) for k, m in {
        "cingulate": cing, "callosum": callosum, "thalamus": thal & ~basal & ~hippo, "hypothalamus": vdc & ~amyg,
        "pituitary": pit, "midbrain": midbrain & ~hippo, "pons": pons, "medulla": medulla, "cord": cord,
        "cerebellum": cerebellum & ~arbor, "hippocampus": hippo & ~thal & ~stem & ~amyg, "amygdala": amyg & ~hippo & ~basal,
        "basal": basal & ~thal & ~callosum & ~amyg}.items()}
    col = int(uv(-2.0, 0)[0])                      # the body of the callosum, above the thalamus
    rr = np.nonzero(callosum[:, col])[0]
    cl = [round(float(v), 1) for v in to_svg(*rc_to_mm((rr.min() + rr.max()) / 2 + 0.5, col + 0.5))]
    marks = {"callosum_label": cl, "z_mid": round(float(z_mid), 1), "z_med": round(float(z_med), 1), "pit": [round(float(py), 1), round(float(pz), 1)]}
    return shapes, probes, marks


if __name__ == "__main__":
    csv, data = fetch()
    o_shapes, o_probes, o_marks = outside(csv, data)
    i_shapes, i_probes, marks = inside(data)
    marks.update(o_marks)
    OUT.write_text(json.dumps({"scale_px_per_mm": S, "outside": o_shapes, "outside_probes": o_probes,
                               "inside": i_shapes, "inside_probes": i_probes, "marks": marks},
                              separators=(",", ":")))
    print(f"wrote {OUT} ({OUT.stat().st_size:,} B)", marks)
