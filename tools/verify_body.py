#!/usr/bin/env python3
"""Check body.html: the data, the drawing and the anatomy.

The interesting checks are the anatomical ones. A projection can be built
from the wrong axes and still look plausible, so the page is asked
questions with known answers: the skull sits above the pelvis, the left
femur is on the viewer's right in an anterior view, the sternum is in
front of the thoracic spine, the heart sits left of the midline and the
liver right of it. If the axes were swapped or a sign flipped, those fail.

Usage: python3 verify_body.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "body.html"
DATA = json.loads((ROOT / "tools" / "data" / "body_paths.json").read_text())

fails, notes = [], []


def ck(cond, msg):
    (notes if cond else fails).append(msg)


def decode(s, scale):
    out, i, px, py = [], 0, 0, 0
    while i < len(s):
        v = []
        for _ in range(2):
            sh = res = 0
            while True:
                b = ord(s[i]) - 63
                i += 1
                res |= (b & 0x1f) << sh
                sh += 5
                if b < 0x20:
                    break
            v.append(~(res >> 1) if res & 1 else res >> 1)
        px += v[0]
        py += v[1]
        out.append((px / scale, py / scale))
    return out


SC, BOX = DATA["scale"], DATA["box"]
parts = {p[0]: dict(fma=p[0], name=p[1], sys=p[2], d=p[3], f=p[4], a=p[5],
                    rings=[decode(r, SC) for r in p[6]]) for p in DATA["parts"]}

print(f"  {len(parts)} parts, box {BOX}")

# --- the data ------------------------------------------------------------
ck(len(parts) == len(DATA["parts"]), "every FMA id is unique")
bad = [p["name"] for p in parts.values()
       if any(len(r) < 4 for r in p["rings"])]
ck(not bad, f"every ring has at least four points ({len(bad)} short)")
out = [p["name"] for p in parts.values() for r in p["rings"]
       for x, y in r
       if not (BOX[0] - .3 <= x <= BOX[2] + .3
               and BOX[1] - .3 <= y <= BOX[3] + .3)]
ck(not out, f"every point lies inside the stated box ({len(out)} outside)")
ck(all(p["f"] <= p["d"] + 0.05 for p in parts.values()),
   "the frontmost point of a part is never behind its median")

# --- the anatomy ---------------------------------------------------------
def one(name):
    hits = [p for p in parts.values() if p["name"] == name]
    if len(hits) != 1:
        fails.append(f"expected exactly one {name!r}, found {len(hits)}")
        return None
    return hits[0]


def cx(p):
    pts = [q for r in p["rings"] for q in r]
    return sum(x for x, _ in pts) / len(pts)


def cy(p):
    pts = [q for r in p["rings"] for q in r]
    return sum(y for _, y in pts) / len(pts)


skull = one("frontal bone")
pelvis = one("sacrum")
lfem, rfem = one("left femur"), one("right femur")
stern, t8 = one("body of sternum"), one("eighth thoracic vertebra")
heart, liver = one("wall of heart"), one("liver")
skin = one("skin")
spleen, appendix = one("spleen"), one("appendix")
lkid, rkid = one("left kidney"), one("right kidney")
if all(x is not None for x in (skull, pelvis, lfem, rfem, stern, t8, heart,
                               liver, skin, spleen, appendix, lkid, rkid)):
    # y runs down the page, so a smaller y is higher up the body
    ck(cy(skull) < cy(pelvis), "the skull is above the pelvis")
    ck(cy(pelvis) < cy(lfem), "the pelvis is above the femur")
    # an anterior view: the subject faces the reader, so the subject's
    # left is on the reader's right, which is the +x side
    ck(cx(lfem) > 0 > cx(rfem),
       "the left femur is on the reader's right, as in an anterior view")
    ck(abs(cx(lfem) + cx(rfem)) < 25, "the two femurs are near mirror images")
    # depth: a smaller f is nearer the front
    ck(stern["f"] < t8["f"], "the sternum is in front of the thoracic spine")
    ck(heart["f"] < t8["f"], "the heart is in front of the thoracic spine")
    # the subject faces the reader, so the subject's right organs sit on
    # the reader's left, which is the negative side of x
    ck(cx(heart) > cx(liver), "the heart sits to the subject's left "
       "of the liver")
    ck(cx(liver) < 0, "the liver is on the subject's right")
    ck(cx(spleen) > 0, "the spleen is on the subject's left")
    ck(cx(appendix) < 0, "the appendix is on the subject's right")
    ck(cy(rkid) > cy(lkid), "the right kidney rides lower than the left, "
       "which is where the liver pushes it")
    ck(skin["f"] <= min(p["f"] for p in parts.values()) + .05,
       "nothing is in front of the skin")
    h = max(cy(p) for p in parts.values()) - min(cy(p) for p in parts.values())
    ck(1400 < BOX[3] - BOX[1] < 1900,
       f"the figure is a human height, {(BOX[3]-BOX[1])/10:.0f} cm")

# --- the page ------------------------------------------------------------
html = PAGE.read_text(encoding="utf-8")
ck("—" not in re.sub(r"<script[\s\S]*?</script>", "", html),
   "no em dash in the page copy")
for word in ("BodyParts3D", "Attribution-Share Alike", "Database Center"):
    ck(word in html, f"the page carries the attribution: {word}")

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("playwright is required for the rendering checks")
    sys.exit(2)

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1240, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(PAGE.as_uri())
    pg.wait_for_timeout(700)
    buttons = pg.eval_on_selector_all("#bar button", "es=>es.map(e=>e.dataset.k)")
    ck(len(buttons) >= 12, f"{len(buttons)} system buttons")
    counts = {}
    for k in buttons:
        pg.click(f"#bar button[data-k='{k}']")
        pg.wait_for_timeout(260)
        n = pg.eval_on_selector_all("#fig svg path[data-fma]", "es=>es.length")
        counts[k] = n
        ck(n > 0, f"{k}: {n} parts drawn")
        # stacked back to front, so the frontmost part is painted last
        fs = pg.evaluate("()=>[...document.querySelectorAll("
                         "'#fig svg path[data-fma]')].map(e=>"
                         "PARTS.find(p=>p.fma===e.dataset.fma).f)")
        ck(all(a >= b - .001 for a, b in zip(fs, fs[1:])),
           f"{k}: drawn back to front")
        said = pg.inner_text("#depthTxt")
        ck(said.startswith(f"{n} of "), f"{k}: the readout matches the figure")
    ck(counts.get("all") == len(parts),
       f"every part is on the Everything view ({counts.get('all')})")
    ck(sum(v for k, v in counts.items() if k != "all") == len(parts),
       "the systems partition the parts")

    # the cut takes parts away from the front and never adds any
    pg.click("#bar button[data-k='muscular']")
    pg.wait_for_timeout(250)
    seq = []
    for v in (100, 80, 60, 40, 20, 0):
        pg.eval_on_selector(
            "#depth",
            "e=>{e.value=%d;e.dispatchEvent(new Event('input'))}" % v)
        pg.wait_for_timeout(180)
        seq.append(pg.eval_on_selector_all(
            "#fig svg path[data-fma]", "es=>es.length"))
    ck(all(a >= b for a, b in zip(seq, seq[1:])),
       f"the cut only ever removes parts {seq}")
    gone = pg.evaluate("()=>{const on=new Set([...document.querySelectorAll("
                       "'#fig svg path[data-fma]')].map(e=>e.dataset.fma));"
                       "const ps=PARTS.filter(p=>p.sys==='muscular');"
                       "const off=ps.filter(p=>!on.has(p.fma));"
                       "const inn=ps.filter(p=>on.has(p.fma));"
                       "return [Math.max(...off.map(p=>p.f)),"
                       "Math.min(...inn.map(p=>p.f))];}")
    ck(gone[0] <= gone[1] + .001,
       "what the cut removes is in front of what it leaves")

    # naming a part, from the figure and from the list
    pg.eval_on_selector("#depth", "e=>{e.value=100;"
                        "e.dispatchEvent(new Event('input'))}")
    pg.click("#bar button[data-k='skeletal']")
    pg.wait_for_timeout(250)
    pg.fill("#q", "left femur")
    pg.wait_for_timeout(200)
    pg.hover("#list div[data-fma]")
    pg.wait_for_timeout(200)
    ck(pg.inner_text("#nameTxt").lower() == "left femur",
       "hovering the list names the part")
    d = pg.get_attribute("#hl", "d")
    ck(d and len(d) > 40, "the highlight traces the named part")
    ck("FMA24475" in pg.inner_text("#bodyTxt"),
       "the card carries the anatomy id")

    # the wheel zooms about the pointer
    before = pg.get_attribute("#fig svg", "viewBox")
    pg.mouse.move(400, 500)
    pg.mouse.wheel(0, -600)
    pg.wait_for_timeout(200)
    after = pg.get_attribute("#fig svg", "viewBox")
    ck(before != after, "the wheel changes the view")
    w0 = float(before.split()[2])
    w1 = float(after.split()[2])
    ck(w1 < w0, f"the wheel zooms in, {w0:.0f} to {w1:.0f} mm across")
    pg.click("#home")
    pg.wait_for_timeout(200)
    ck(pg.get_attribute("#fig svg", "viewBox") == before,
       "the whole body button restores the view")

    ck(not errs, f"no script errors ({errs[:1]})")
    br.close()

for n in notes:
    print("  ok  ", n)
if fails:
    print()
    for f in fails:
        print("FAIL", f)
    sys.exit(1)
print(f"\n{len(notes)} checks passed")
