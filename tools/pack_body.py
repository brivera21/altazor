#!/usr/bin/env python3
"""Pack the traced BodyParts3D outlines into tools/data/body_paths.json.

Run once, after trace_spin.py, from the traced directory. The result is
checked in so the page builds without the network and without the 1.3 GB
of meshes.

Each part carries one silhouette per traced angle about the vertical
axis. Only half a turn is traced. An orthographic silhouette is the set
of points the surface projects onto, and looking from the far side gives
the same set mirrored left to right, so the view at an angle plus 180
degrees is that view mirrored, with the stacking order reversed. The page
does that, and the file stays half the size.

Each ring is polyline-encoded: signed deltas on a quarter millimetre
grid, five bits to a character, the scheme Google uses for map polylines.
It costs about a fifth of what a list of numbers would.

Usage: python3 pack_body.py [traced_dir]
"""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = sys.argv[1] if len(sys.argv) > 1 else "/tmp/bp3d/spun"
SCALE = 4          # quarter of a millimetre


def enc1(v):
    v = v << 1 if v >= 0 else ~(v << 1)
    out = ""
    while v >= 0x20:
        out += chr((0x20 | (v & 0x1f)) + 63)
        v >>= 5
    return out + chr(v + 63)


def encode(ring):
    out, px, py = [], 0, 0
    for x, y in ring:
        ix, iy = round(x * SCALE), round(y * SCALE)
        out.append(enc1(ix - px))
        out.append(enc1(iy - py))
        px, py = ix, iy
    return "".join(out)


def decode(s):
    out, i, px, py = [], 0, 0, 0
    while i < len(s):
        vals = []
        for _ in range(2):
            sh, res = 0, 0
            while True:
                b = ord(s[i]) - 63
                i += 1
                res |= (b & 0x1f) << sh
                sh += 5
                if b < 0x20:
                    break
            vals.append(~(res >> 1) if res & 1 else (res >> 1))
        px += vals[0]
        py += vals[1]
        out.append((px / SCALE, py / SCALE))
    return out


ANGLES = [0, 45, 90, 135]
parts = []
for f in sorted(glob.glob(f"{SRC}/*.json")):
    d = json.load(open(f))
    views = d["views"]
    if len(views) != len(ANGLES) or not any(v["p"] for v in views):
        continue
    parts.append([
        d["fma"][3:], d["name"], d["sys"],
        [v["f"] for v in views],
        [v["a"] for v in views],
        [[encode(r) for r in v["p"] if len(r) >= 4] for v in views],
    ])

# one box that holds every angle, so the figure does not jump as it turns
X = [x for p in parts for rings in p[5] for r in rings for x, y in decode(r)]
Y = [y for p in parts for rings in p[5] for r in rings for x, y in decode(r)]
box = [round(min(X), 1), round(min(Y), 1), round(max(X), 1), round(max(Y), 1)]

out = ROOT / "tools" / "data" / "body_paths.json"
out.write_text(json.dumps(dict(scale=SCALE, box=box, angles=ANGLES,
                               parts=parts), separators=(",", ":")))
print(f"{len(parts)} parts x {len(ANGLES)} angles, box {box}, "
      f"{out.stat().st_size/1024:.0f} KB")
