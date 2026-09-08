#!/usr/bin/env python3
"""Pack the traced BodyParts3D outlines into tools/data/body_paths.json.

Run once, from /tmp/bp3d/traced, after trace_all.py. The result is checked
in so the page builds without the network and without the 1.3 GB of meshes.

Each ring is a polyline-encoded string: signed deltas on a quarter
millimetre grid, five bits to a character, the same scheme Google uses for
map polylines. It costs about a fifth of what a list of numbers would.

Usage: python3 pack_body.py [traced_dir]
"""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = sys.argv[1] if len(sys.argv) > 1 else "/tmp/bp3d/traced"
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


parts = []
for f in sorted(glob.glob(f"{SRC}/*.json")):
    d = json.load(open(f))
    rings = [r for r in d["p"] if len(r) >= 4]
    if not rings:
        continue
    parts.append([d["fma"][3:], d["name"], d["sys"], round(d["d"], 1),
                  round(d["f"], 1), round(d["a"], 1),
                  [encode(r) for r in rings]])

xs = [p for _ in () for p in ()]
# bounds, read back from the encoded rings so they match what the page draws
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


X = [x for p in parts for r in p[6] for x, y in decode(r)]
Y = [y for p in parts for r in p[6] for x, y in decode(r)]
box = [round(min(X), 1), round(min(Y), 1), round(max(X), 1), round(max(Y), 1)]

out = ROOT / "tools" / "data" / "body_paths.json"
out.write_text(json.dumps(dict(scale=SCALE, box=box, parts=parts),
                          separators=(",", ":")))
print(f"{len(parts)} parts, box {box}, {out.stat().st_size/1024:.0f} KB")
