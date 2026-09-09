#!/usr/bin/env python3
"""The nervous system on body.html, built as 3D lines over the real body.

BodyParts3D carries the brain and the two optic nerves and nothing else
of the nervous system: no spinal cord, no spinal nerves, no autonomic
chain, no cranial nerves but the second. So everything in this file is
drawn rather than scanned, and the page says so.

Drawn does not mean freehand. Every path here is written against
tools/data/body_landmarks.json, which holds the measured 3D position of
each vertebra, each limb bone and each target organ of the same body the
outlines are traced from. A spinal level is that vertebra's real
centroid; the arm nerves run at real fractions along the real humerus;
the vagus ends on the real heart and the real stomach. The course
follows standard descriptions in Gray's Anatomy and Moore.

What that buys is registration: the nerves land where they should
against the bones on screen. What it does not buy is a claim of
millimetre accuracy for any individual nerve, and the page does not make
one.

Everything is in millimetres, x to the subject's left, y from front to
back, z up, the frame the meshes come in.
"""

import json
from pathlib import Path

L = json.loads((Path(__file__).parent / "data" / "body_landmarks.json")
               .read_text())


def c(name):
    return L[name]["c"]


def lo(name):
    return L[name]["lo"]


def hi(name):
    return L[name]["hi"]


# ---- the spine, level by level, from the real vertebrae ----------------
ORDINAL = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh",
           "eighth", "ninth", "tenth", "eleventh", "twelfth"]

LEVELS = []                      # (label, [x, y, z]) head to tail
LEVELS.append(("C1", c("atlas")))
LEVELS.append(("C2", c("axis")))
for i, o in enumerate(ORDINAL[2:7], start=3):
    LEVELS.append((f"C{i}", c(f"{o} cervical vertebra")))
for i, o in enumerate(ORDINAL, start=1):
    LEVELS.append((f"T{i}", c(f"{o} thoracic vertebra")))
for i, o in enumerate(ORDINAL[:5], start=1):
    LEVELS.append((f"L{i}", c(f"{o} lumbar vertebra")))

# the sacrum is one mesh, so its five levels are spread down its own height
SLO, SHI = lo("sacrum"), hi("sacrum")
for i in range(1, 6):
    t = (i - 0.5) / 5
    LEVELS.append((f"S{i}", [SLO[0] + (SHI[0] - SLO[0]) * 0.5,
                             SLO[1] + (SHI[1] - SLO[1]) * 0.45,
                             SHI[2] + (SLO[2] - SHI[2]) * t]))
LEVELS.append(("Co", [SLO[0] + (SHI[0] - SLO[0]) * 0.5,
                      SLO[1] + (SHI[1] - SLO[1]) * 0.3, SLO[2] - 8]))

LV = dict(LEVELS)
ORDER = [k for k, _ in LEVELS]

# the canal sits behind the middle of the vertebra
CANAL_BACK = 5.0


def canal(level, t=0.0):
    """A point in the vertebral canal at a level, t levels below it."""
    i = ORDER.index(level)
    j = min(len(ORDER) - 1, max(0, i + int(t)))
    frac = t - int(t)
    a, b = LV[ORDER[j]], LV[ORDER[min(len(ORDER) - 1, j + 1)]]
    p = [a[k] + (b[k] - a[k]) * frac for k in range(3)]
    return [p[0], p[1] + CANAL_BACK, p[2]]


# ---- landmarks the paths are written against ---------------------------
MEDULLA, PONS = c("medulla oblongata"), c("pons")
CEREB, EYE = c("cerebellum"), c("eyeball")
MAND, EAR = c("mandible"), c("ear")
# the cord begins at the foramen magnum, which sits above the atlas
FORAMEN = [0.0, MEDULLA[1] + 4,
           max(lo("medulla oblongata")[2], LV["C1"][2] + 8)]
CONUS = canal("L1", 0.55)                                        # cord ends
DURAL_END = canal("S2", 0.0)                                     # sac ends

HUM, RAD, ULN = "left humerus", "left radius", "left ulna"
FEM, TIB, FIB = "left femur", "left tibia", "left fibula"
CLAV, HIP = "left clavicle", "left hip bone"


def along(name, t, dx=0.0, dy=0.0):
    """A point a fraction t down a bone, nudged off its axis."""
    a, b = hi(name), lo(name)
    z = a[2] + (b[2] - a[2]) * t
    x = c(name)[0] + (b[0] - a[0]) * 0.0 + dx
    y = c(name)[1] + dy
    return [x, y, z]


NERVES = []


def sided(name, s):
    """Left or right in front of a name, without wrecking a numeral. A
    plain word drops its capital; C1 and V2 and IX keep theirs."""
    body = (name[0].lower() + name[1:]
            if len(name) > 1 and name[0].isupper() and name[1].islower()
            else name)
    return ("Left " if s > 0 else "Right ") + body


def add(g, name, pts, note, k="nerve", w=1.8, sides="both"):
    """Add a path. sides='both' mirrors it across the midline."""
    for s in ((1, -1) if sides == "both" else (1,)):
        NERVES.append(dict(
            g=g, n=(name if sides != "both" else sided(name, s)),
            t=note, k=k, w=w,
            p=[[round(p[0] * s, 1), round(p[1], 1), round(p[2], 1)] for p in pts]))


def one(g, name, pts, note, k="nerve", w=1.8):
    add(g, name, pts, note, k, w, sides="one")


# ---- central: the cord, the cauda equina, the meninges -----------------
cord = [FORAMEN]
for lev in ORDER[:ORDER.index("L1") + 1]:
    cord.append(canal(lev))
cord.append(CONUS)
one("cns", "Spinal cord", cord,
    "It leaves the skull at the foramen magnum and ends at the first or "
    "second lumbar vertebra, well short of the bottom of the spine. The "
    "column keeps growing after the cord stops, which is why the two do "
    "not end together and why a lumbar puncture below that level meets "
    "loose roots rather than cord.", k="cord", w=7)

one("cns", "Conus medullaris", [CONUS, [CONUS[0], CONUS[1], CONUS[2] - 6]],
    "The tapered end of the cord, at the first or second lumbar vertebra.",
    k="ganglion", w=5)

one("cns", "Filum terminale",
    [CONUS, canal("L3"), canal("L5"), DURAL_END,
     [LV["Co"][0], LV["Co"][1] + CANAL_BACK, LV["Co"][2]]],
    "A thread of pia that anchors the end of the cord to the coccyx.",
    w=1.2)

# the cauda equina: roots that still have to reach their own exit
for i, lev in enumerate(ORDER[ORDER.index("L2"):ORDER.index("S5") + 1]):
    for s in (1, -1):
        start = [CONUS[0] + s * (1.5 + i * 0.7), CONUS[1], CONUS[2]]
        exit_ = canal(lev)
        NERVES.append(dict(
            g="cns",
            n=("Left" if s > 0 else "Right") + f" cauda equina, {lev} root",
            t="Below the end of the cord the remaining roots run down inside "
              "the dural sac to their own exits, in a bundle named for a "
              "horse's tail.",
            k="root", w=1.0,
            p=[[round(v, 1) for v in start],
               [round(exit_[0] + s * 6, 1), round(exit_[1] - 2, 1),
                round(exit_[2] + 4, 1)],
               [round(exit_[0] + s * 13, 1), round(exit_[1] - 4, 1),
                round(exit_[2], 1)]]))


# ---- the thirty-one pairs of spinal nerves -----------------------------
# The cord is shorter than the column, so a nerve's segment of cord sits
# above the gap it leaves by. The offsets are the standard ones.
SEGMENT_AT = {}
for i, k in enumerate(ORDER):
    if k.startswith("C"):
        SEGMENT_AT[k] = k
for i in range(1, 13):
    j = i - (2 if i <= 6 else 3)
    SEGMENT_AT[f"T{i}"] = f"T{max(1, j)}" if j >= 1 else "C7"
for i in range(1, 6):
    SEGMENT_AT[f"L{i}"] = "T11" if i <= 3 else "T12"
for i in range(1, 6):
    SEGMENT_AT[f"S{i}"] = "T12" if i <= 2 else "L1"
SEGMENT_AT["Co"] = "L1"

# C1 to C7 leave above their vertebra, C8 leaves below C7, and from T1
# down every nerve leaves below the vertebra it is named for
SPINAL = ([f"C{i}" for i in range(1, 9)] + [f"T{i}" for i in range(1, 13)]
          + [f"L{i}" for i in range(1, 6)] + [f"S{i}" for i in range(1, 6)]
          + ["Co"])

ROOT_NOTE = {
    "C": "A cervical nerve. The first seven leave above the vertebra they "
         "are named for, which is why there are eight cervical nerves and "
         "only seven cervical vertebrae.",
    "T": "A thoracic nerve. It leaves below its own vertebra and runs "
         "forward along the rib as an intercostal nerve.",
    "L": "A lumbar nerve. Its segment of cord sits up at the eleventh or "
         "twelfth thoracic vertebra, so the root runs a long way down "
         "inside the sac before it leaves.",
    "S": "A sacral nerve. It leaves through a hole in the front or back of "
         "the sacrum rather than between two vertebrae.",
    "C1": "",
}

for name in SPINAL:
    grp = name[0]
    n = int(name[1:]) if name != "Co" else 1
    if grp == "C":
        vert = "C1" if n == 1 else f"C{min(7, n - 1)}"
        exitz = LV[vert][2] + (6 if n == 1 else 0)
    elif name == "Co":
        vert, exitz = "S5", LV["S5"][2] - 6
    else:
        vert = name
        exitz = LV[vert][2] - (LV[vert][2] - LV[ORDER[min(len(ORDER) - 1,
                               ORDER.index(vert) + 1)]][2]) * 0.5
    seg = LV[SEGMENT_AT.get(name, vert)]
    v = LV[vert]
    start = [0, seg[1] + CANAL_BACK, min(seg[2], CONUS[2] + 400)]
    if start[2] < CONUS[2]:
        start = [0, CONUS[1], CONUS[2]]
    out = 26 if grp in "CT" else 30
    add("periph", f"{name} spinal nerve",
        [[start[0], start[1], start[2]],
         [8, v[1] + CANAL_BACK - 1, exitz + 2],
         [out * 0.6, v[1] + 1, exitz],
         [out, v[1] - 4, exitz - 2]],
        ROOT_NOTE[grp] if grp in ROOT_NOTE else "", k="root", w=1.3)

# ---- the plexuses and the named nerves of the limbs --------------------
CL, SHO = c(CLAV), hi(HUM)
AX = [c(HUM)[0] * 0.62, CL[1] + 14, SHO[2] - 22]          # the axilla

add("periph", "Cervical plexus",
    [[LV["C2"][0] + 16, LV["C2"][1] - 14, LV["C2"][2]],
     [26, LV["C3"][1] - 22, LV["C3"][2] - 4],
     [30, LV["C4"][1] - 26, LV["C4"][2] - 8]],
    "The first four cervical nerves, supplying the skin of the neck and "
    "the muscles that hold the head.", w=1.6)

add("periph", "Phrenic nerve",
    [[28, LV["C4"][1] - 26, LV["C4"][2] - 6],
     [34, CL[1] - 4, CL[2] + 30],
     [30, CL[1] - 10, CL[2] - 40],
     [26, c("wall of heart")[1] - 6, c("wall of heart")[2] + 20],
     [24, c("wall of heart")[1] - 4, c("wall of heart")[2] - 40],
     [20, c("diaphragm")[1] - 6, hi("diaphragm")[2] - 20]],
    "Three, four and five keep the diaphragm alive. It comes off the neck "
    "and runs the whole length of the chest, because the diaphragm formed "
    "up in the neck and descended, taking its nerve with it. A broken neck "
    "above the fourth cervical nerve stops breathing.", w=2.0)

add("periph", "Brachial plexus",
    [[14, LV["C5"][1] - 4, LV["C5"][2]],
     [40, LV["C6"][1] - 16, LV["C6"][2] - 6],
     [62, CL[1] - 2, CL[2] + 16],
     [AX[0] * 0.85, CL[1] + 6, CL[2] - 6],
     AX],
    "The fifth cervical to the first thoracic nerve, rearranged through "
    "trunks, divisions and cords into the nerves of the arm. It passes "
    "between the scalene muscles, under the clavicle and into the armpit.",
    w=2.6)

add("periph", "Musculocutaneous nerve",
    [AX, along(HUM, 0.25, dx=-16, dy=-16), along(HUM, 0.6, dx=-10, dy=-20),
     along(HUM, 0.95, dx=6, dy=-22), along(RAD, 0.35, dx=14, dy=-16)],
    "It pierces coracobrachialis, runs between biceps and brachialis and "
    "ends as the sensory nerve of the lateral forearm.", w=1.6)

add("periph", "Axillary nerve",
    [AX, [AX[0] + 18, AX[1] + 6, AX[2] - 6],
     [c(HUM)[0] + 6, c(HUM)[1] + 8, SHO[2] - 34]],
    "Around the surgical neck of the humerus to deltoid. A break there, or "
    "a dislocated shoulder, can take the nerve with it.", w=1.5)

add("periph", "Radial nerve",
    [AX, along(HUM, 0.2, dx=-6, dy=6), along(HUM, 0.45, dx=2, dy=16),
     along(HUM, 0.72, dx=12, dy=8), along(HUM, 0.95, dx=18, dy=-8),
     along(RAD, 0.3, dx=16, dy=6), along(RAD, 0.75, dx=12, dy=8),
     along(RAD, 1.0, dx=8, dy=6)],
    "It spirals behind the humerus in the radial groove, which is why a "
    "mid-shaft break of that bone drops the wrist. It supplies every "
    "muscle that extends the elbow, wrist and fingers.", w=1.9)

add("periph", "Median nerve",
    [AX, along(HUM, 0.3, dx=-14, dy=-8), along(HUM, 0.7, dx=-12, dy=-12),
     along(HUM, 1.0, dx=-4, dy=-16), along(ULN, 0.3, dx=6, dy=-16),
     along(ULN, 0.8, dx=8, dy=-18), along(ULN, 1.0, dx=8, dy=-18),
     [c(ULN)[0] + 8, c(ULN)[1] - 20, lo(ULN)[2] - 30]],
    "Down the front of the arm and through the carpal tunnel at the wrist, "
    "where it is the nerve that is squeezed in carpal tunnel syndrome.",
    w=1.9)

add("periph", "Ulnar nerve",
    [AX, along(HUM, 0.35, dx=-18, dy=-2), along(HUM, 0.75, dx=-16, dy=4),
     along(HUM, 0.99, dx=-14, dy=10), along(ULN, 0.25, dx=-8, dy=-4),
     along(ULN, 0.8, dx=-4, dy=-12), along(ULN, 1.0, dx=-2, dy=-14),
     [c(ULN)[0] - 2, c(ULN)[1] - 16, lo(ULN)[2] - 30]],
    "It passes behind the medial epicondyle, where it lies against bone "
    "under the skin. That is the funny bone, and the tingling is the nerve "
    "itself being struck.", w=1.9)

for i in range(1, 13):
    v = LV[f"T{i}"]
    reach = 1.0 - abs(i - 6) / 14.0
    add("periph", (f"T{i} intercostal nerve" if i < 12
                   else "Subcostal nerve"),
        [[18, v[1] - 2, v[2] - 4],
         [62 * reach + 24, v[1] - 46, v[2] - 14],
         [86 * reach + 14, v[1] - 108, v[2] - 30],
         [44 * reach + 10, v[1] - 158, v[2] - 46]],
        "Each thoracic nerve runs forward in the groove under its own rib. "
        "That is why the skin of the chest and belly is supplied in neat "
        "bands, one nerve to a stripe, and why shingles appears as a band.",
        w=1.3)

# ---- the lower limb ----------------------------------------------------
PSOAS = c("left psoas major")
GSF = [c(HIP)[0] * 0.55, c(HIP)[1] + 26, LV["S1"][2] - 6]   # sciatic foramen
KNEE = [c(FEM)[0], c(FEM)[1] + 10, lo(FEM)[2] + 16]

add("periph", "Lumbar plexus",
    [[10, LV["L1"][1] - 2, LV["L1"][2]],
     [PSOAS[0] * 0.7, LV["L2"][1] - 12, LV["L2"][2]],
     [PSOAS[0], LV["L4"][1] - 16, LV["L4"][2]]],
    "The first four lumbar nerves, woven together inside the psoas muscle "
    "on the back wall of the abdomen.", w=2.2)

add("periph", "Femoral nerve",
    [[PSOAS[0], LV["L3"][1] - 14, LV["L3"][2]],
     [PSOAS[0] + 8, LV["L5"][1] - 30, LV["L5"][2] - 20],
     [c(HIP)[0] * 0.7, c(HIP)[1] - 46, lo(HIP)[2] + 10],
     [c(FEM)[0] + 6, c(FEM)[1] - 40, hi(FEM)[2] - 60],
     [c(FEM)[0] + 2, c(FEM)[1] - 34, c(FEM)[2] + 40]],
    "Second to fourth lumbar. It passes under the inguinal ligament into "
    "the front of the thigh and works the quadriceps, so it is the nerve "
    "of the knee jerk.", w=2.0)

add("periph", "Saphenous nerve",
    [[c(FEM)[0] + 2, c(FEM)[1] - 34, c(FEM)[2] + 40],
     [c(FEM)[0] - 16, c(FEM)[1] - 20, c(FEM)[2] - 60],
     [c(TIB)[0] - 20, c(TIB)[1] - 20, c(TIB)[2] + 60],
     [c(TIB)[0] - 22, c(TIB)[1] - 16, lo(TIB)[2] + 10],
     [c(TIB)[0] - 16, c(TIB)[1] - 42, lo(TIB)[2] - 26]],
    "The femoral nerve's long sensory branch, down the inside of the leg "
    "to the arch of the foot. The only part of the leg below the knee not "
    "supplied by the sciatic nerve.", w=1.3)

add("periph", "Obturator nerve",
    [[PSOAS[0] * 0.8, LV["L3"][1] - 10, LV["L3"][2] - 10],
     [c(HIP)[0] * 0.5, c(HIP)[1] - 20, c(HIP)[2] - 50],
     [c(FEM)[0] - 22, c(FEM)[1] - 16, hi(FEM)[2] - 90],
     [c(FEM)[0] - 26, c(FEM)[1] - 8, c(FEM)[2] + 20]],
    "Through the obturator foramen to the muscles that pull the thigh "
    "inward.", w=1.5)

add("periph", "Sacral plexus",
    [[16, LV["L5"][1] + 2, LV["L5"][2] - 6],
     [c(HIP)[0] * 0.35, LV["S1"][1] + 12, LV["S1"][2]],
     GSF],
    "The fourth lumbar to the fourth sacral nerve, on the back wall of the "
    "pelvis, gathering into the largest nerve in the body.", w=2.4)

add("periph", "Sciatic nerve",
    [GSF,
     [c(FEM)[0] + 4, c(FEM)[1] + 34, hi(FEM)[2] - 40],
     [c(FEM)[0] + 2, c(FEM)[1] + 30, c(FEM)[2] + 30],
     [c(FEM)[0], c(FEM)[1] + 24, c(FEM)[2] - 60],
     KNEE],
    "The thickest nerve in the body, about as wide as a finger where it "
    "leaves the pelvis. It runs down the back of the thigh and splits "
    "above the knee.", w=3.2)

add("periph", "Tibial nerve",
    [KNEE,
     [c(TIB)[0] + 4, c(TIB)[1] + 26, c(TIB)[2] + 80],
     [c(TIB)[0] - 2, c(TIB)[1] + 16, c(TIB)[2] - 40],
     [c(TIB)[0] - 12, c(TIB)[1] + 4, lo(TIB)[2] + 12],
     [c(TIB)[0] - 8, c(TIB)[1] - 10, lo(TIB)[2] - 20],
     [c(TIB)[0] - 2, c(TIB)[1] - 46, lo(TIB)[2] - 34]],
    "Down the back of the calf and behind the inner ankle into the sole of "
    "the foot.", w=2.0)

add("periph", "Common fibular nerve",
    [KNEE,
     [c(FIB)[0] + 8, c(FIB)[1] + 10, hi(FIB)[2] - 6],
     [c(FIB)[0] + 10, c(FIB)[1] - 6, hi(FIB)[2] - 26],
     [c(FIB)[0] - 2, c(FIB)[1] - 16, c(FIB)[2] - 20],
     [c(FIB)[0] - 10, c(FIB)[1] - 18, lo(FIB)[2] + 6],
     [c(FIB)[0] - 16, c(FIB)[1] - 44, lo(FIB)[2] - 30]],
    "It winds around the neck of the fibula, where it lies on bare bone "
    "just under the skin. It is the most commonly injured nerve in the "
    "leg, and losing it drops the foot.", w=1.9)

add("periph", "Pudendal nerve",
    [[c(HIP)[0] * 0.4, LV["S3"][1] + 6, LV["S3"][2]],
     [c(HIP)[0] * 0.45, LV["S4"][1] + 16, LV["S4"][2] - 8],
     [c(HIP)[0] * 0.3, LV["S4"][1] - 20, LV["S4"][2] - 30]],
    "Second to fourth sacral, to the perineum and the muscles that hold "
    "the bladder and bowel closed.", w=1.4)

# ---- the twelve cranial nerves -----------------------------------------
FRONT_LOBE = [0, EYE[1] + 24, EYE[2] + 26]

add("cranial", "I Olfactory nerve",
    [[7, EYE[1] + 10, EYE[2] + 20], [7, EYE[1] - 14, EYE[2] + 4],
     [6, EYE[1] - 22, EYE[2] - 10]],
    "Not one nerve but a spray of filaments through the sieve plate of the "
    "ethmoid, straight from the nasal lining into the brain. The only "
    "sense that does not relay through the thalamus first.", w=1.4)

add("cranial", "II Optic nerve",
    [[3, PONS[1] - 24, PONS[2] + 6], [10, EYE[1] + 24, EYE[2] + 8],
     [EYE[0] + 22, EYE[1] - 4, EYE[2]]],
    "A tract of brain pushed out to the eye during development rather than "
    "a true peripheral nerve. Its fibres from the inner half of each retina "
    "cross at the chiasm, so each side of the brain sees the opposite half "
    "of the world.", w=2.4)

add("cranial", "III Oculomotor nerve",
    [[5, PONS[1] - 6, PONS[2] + 14], [14, EYE[1] + 20, EYE[2] + 6],
     [EYE[0] + 16, EYE[1] + 2, EYE[2] + 4]],
    "Four of the six muscles that move the eye, the lid, and the pupil. "
    "Pressure on it from a swelling brain blows the pupil on that side, "
    "which is why the pupils are checked after a head injury.", w=1.6)

add("cranial", "IV Trochlear nerve",
    [[6, PONS[1] + 12, PONS[2] + 10], [16, EYE[1] + 26, EYE[2] + 14],
     [EYE[0] + 12, EYE[1] + 2, EYE[2] + 10]],
    "The thinnest cranial nerve and the only one to leave the back of the "
    "brainstem, which gives it the longest course inside the skull. It "
    "works one muscle.", w=1.1)

add("cranial", "V Trigeminal nerve",
    [[10, PONS[1] - 6, PONS[2] - 4], [26, PONS[1] - 30, PONS[2] - 8],
     [40, MAND[1] + 10, MAND[2] + 34]],
    "Sensation for the whole face in three divisions, and the muscles of "
    "chewing. Its neuralgia is described as among the worst pain in "
    "medicine.", w=2.4)

add("cranial", "V1 Ophthalmic division",
    [[40, MAND[1] + 10, MAND[2] + 34], [EYE[0] + 26, EYE[1] + 6, EYE[2] + 12]],
    "Forehead, upper eyelid and the surface of the eye.", w=1.3)
add("cranial", "V2 Maxillary division",
    [[40, MAND[1] + 10, MAND[2] + 34], [34, MAND[1] - 30, MAND[2] + 8]],
    "Cheek, upper lip and upper teeth.", w=1.3)
add("cranial", "V3 Mandibular division",
    [[40, MAND[1] + 10, MAND[2] + 34], [36, MAND[1] - 16, MAND[2] - 24]],
    "Lower jaw, lower teeth, and the muscles of chewing. The only division "
    "that carries motor fibres.", w=1.3)

add("cranial", "VI Abducens nerve",
    [[5, PONS[1] - 12, PONS[2] - 14], [16, EYE[1] + 22, EYE[2] - 2],
     [EYE[0] + 24, EYE[1] + 4, EYE[2] - 2]],
    "One muscle, the one that turns the eye outward. Its long course "
    "inside the skull makes it the first to fail when pressure rises.",
    w=1.1)

add("cranial", "VII Facial nerve",
    [[9, PONS[1] - 4, PONS[2] - 18], [EAR[0] + 26, EAR[1] + 4, EAR[2] - 14],
     [34, MAND[1] - 26, MAND[2] + 14], [26, MAND[1] - 48, MAND[2] + 2]],
    "Every muscle of facial expression, taste from the front of the "
    "tongue, and the tear and saliva glands. Bell's palsy is this nerve.",
    w=1.9)

add("cranial", "VIII Vestibulocochlear nerve",
    [[8, PONS[1] - 2, PONS[2] - 20], [EAR[0] * 0.55, EAR[1] + 2, EAR[2] - 12]],
    "Hearing and balance, from the inner ear, which this model does not "
    "carry.", w=1.5)

add("cranial", "IX Glossopharyngeal nerve",
    [[8, MEDULLA[1] - 4, MEDULLA[2] + 6], [24, MEDULLA[1] - 34, MEDULLA[2] - 14],
     [22, MAND[1] - 8, MAND[2] - 26]],
    "Taste and sensation from the back of the tongue and the throat, and "
    "the gag reflex. It also reports blood pressure from the carotid.",
    w=1.4)

add("cranial", "XI Accessory nerve",
    [[10, LV["C4"][1] + 4, LV["C4"][2]], [8, LV["C2"][1] + 6, LV["C2"][2]],
     [10, MEDULLA[1] + 4, MEDULLA[2] - 8], [26, MEDULLA[1] - 16, MEDULLA[2] - 22],
     [44, LV["C4"][1] - 18, LV["C4"][2] - 10]],
    "The only cranial nerve that comes from the spinal cord. Its roots run "
    "up through the foramen magnum, out again, and down to the "
    "sternocleidomastoid and trapezius.", w=1.5)

add("cranial", "XII Hypoglossal nerve",
    [[6, MEDULLA[1] - 8, MEDULLA[2] - 4], [20, MAND[1] + 20, MAND[2] - 16],
     [12, MAND[1] - 30, MAND[2] - 14]],
    "Every muscle of the tongue. Damage on one side pushes the tongue "
    "toward the bad side when it is stuck out.", w=1.4)

# ---- the sympathetic chain --------------------------------------------
# Two chains of ganglia beside the vertebral bodies, from the base of the
# skull to the coccyx. The fibres that feed them leave the cord only
# between the first thoracic and the second lumbar nerve, which is the
# whole of the sympathetic outflow.
CHAIN_X, CHAIN_Y = 13.0, -9.0
chain = []
for lev in ORDER:
    v = LV[lev]
    chain.append([CHAIN_X, v[1] + CHAIN_Y, v[2]])
add("symp", "Sympathetic chain", chain,
    "A string of ganglia running the length of the spine just in front of "
    "the vertebrae. A fibre entering it can go up, go down or pass "
    "straight through, which is how an outflow confined to the middle of "
    "the back reaches the eye at the top and the leg at the bottom.",
    w=2.4)

GANG = [("Superior cervical ganglion", "C2",
         "The top of the chain. It supplies the eye, the eyelid and the "
         "blood vessels of the face. Losing it gives a drooping lid, a "
         "small pupil and a dry face on that side."),
        ("Middle cervical ganglion", "C6", "Small, and often absent."),
        ("Cervicothoracic ganglion", "T1",
         "Also called the stellate ganglion, formed where the lowest "
         "cervical and first thoracic ganglia fuse. It supplies the arm "
         "and much of the heart.")]
for name, lev, note in GANG:
    v = LV[lev]
    add("symp", name, [[CHAIN_X, v[1] + CHAIN_Y, v[2]],
                       [CHAIN_X, v[1] + CHAIN_Y, v[2] - 3]],
        note, k="ganglion", w=9)

for lev in ORDER[ORDER.index("T2"):-1]:
    v = LV[lev]
    add("symp", f"{lev} sympathetic ganglion",
        [[CHAIN_X, v[1] + CHAIN_Y, v[2]], [CHAIN_X, v[1] + CHAIN_Y, v[2] - 2]],
        "One of the paired ganglia of the chain.", k="ganglion", w=5.5)

CO = LV["Co"]
one("symp", "Ganglion impar", [[0, CO[1] + CHAIN_Y, CO[2]],
                               [0, CO[1] + CHAIN_Y, CO[2] - 3]],
    "The bottom of both chains, where the left and right sides meet as a "
    "single midline ganglion in front of the coccyx.", k="ganglion", w=9)

# the outflow: only T1 to L2 carries fibres out of the cord
for lev in [f"T{i}" for i in range(1, 13)] + ["L1", "L2"]:
    v = LV[lev]
    add("symp", f"{lev} white ramus",
        [[6, v[1] + CANAL_BACK, v[2]], [CHAIN_X, v[1] + CHAIN_Y, v[2]]],
        "The sympathetic outflow leaves the cord only between the first "
        "thoracic and the second lumbar nerve. Every sympathetic effect in "
        "the body starts in this stretch.", k="root", w=1.2)

CELIAC = [0, c("stomach")[1] + 34, LV["T12"][2] + 6]
SMG = [0, LV["L1"][1] - 34, LV["L1"][2] - 6]
IMG = [0, LV["L3"][1] - 30, LV["L3"][2] - 6]

for name, top, bot, target, note in [
    ("Greater splanchnic nerve", "T5", "T9", CELIAC,
     "It passes straight through the chain without stopping and reaches "
     "the celiac ganglion, which is why the adrenal gland can be reached "
     "in one hop and answers in seconds."),
    ("Lesser splanchnic nerve", "T10", "T11", SMG,
     "To the aorticorenal and superior mesenteric ganglia."),
    ("Least splanchnic nerve", "T12", "T12", [0, LV["L1"][1] - 20,
                                              c("left kidney")[2] - 10],
     "To the renal plexus.")]:
    a, b = LV[top], LV[bot]
    add("symp", name,
        [[CHAIN_X, a[1] + CHAIN_Y, a[2]],
         [CHAIN_X - 1, (a[1] + b[1]) / 2 + CHAIN_Y - 14,
          (a[2] + b[2]) / 2],
         [CHAIN_X - 4, b[1] + CHAIN_Y - 26, b[2] - 8],
         [max(4.0, target[0] + 5), target[1], target[2]]], note, w=2.0)

for name, p, note in [
    ("Celiac ganglion", CELIAC,
     "The largest autonomic ganglion, around the artery to the stomach, "
     "liver and spleen. The solar plexus of common speech."),
    ("Superior mesenteric ganglion", SMG, "For the small intestine and the "
     "first part of the colon."),
    ("Inferior mesenteric ganglion", IMG, "For the last part of the colon "
     "and the rectum.")]:
    one("symp", name, [[p[0], p[1], p[2]], [p[0], p[1], p[2] - 3]],
        note, k="ganglion", w=11)

AD = c("left adrenal gland")
add("symp", "Adrenal medulla", [[AD[0], AD[1], AD[2]], [AD[0], AD[1], AD[2] - 3]],
    "A sympathetic ganglion that lost its axons and pours its transmitter "
    "into the blood instead. That is why fright reaches the whole body at "
    "once and takes half a minute to fade.", k="ganglion", w=11)

# ---- the parasympathetic outflow --------------------------------------
add("para", "Vagus nerve",
    [[9, MEDULLA[1] - 6, MEDULLA[2] - 10],
     [24, LV["C3"][1] - 40, LV["C3"][2] - 10],
     [26, LV["C7"][1] - 46, LV["C7"][2] - 10],
     [22, c("wall of heart")[1] - 4, c("wall of heart")[2] + 40],
     [14, c("wall of heart")[1] + 10, c("wall of heart")[2] - 30],
     [8, c("stomach")[1] + 20, c("stomach")[2] + 20],
     [4, c("stomach")[1] + 10, c("stomach")[2] - 40],
     [0, LV["L2"][1] - 40, LV["L2"][2] - 10]],
    "The tenth cranial nerve, and the one that leaves the head. It slows "
    "the heart, narrows the airways and drives the gut as far as the last "
    "third of the colon, where the sacral outflow takes over. Four fifths "
    "of its fibres carry news up to the brain rather than orders down.",
    w=2.6)

add("para", "Cardiac branches of the vagus",
    [[22, c("wall of heart")[1] - 4, c("wall of heart")[2] + 40],
     [10, c("wall of heart")[1], c("wall of heart")[2] + 6]],
    "Cutting them raises the resting heart rate by about forty beats a "
    "minute, which is the size of the brake the vagus holds on all day.",
    w=1.4)

add("para", "Pulmonary branches of the vagus",
    [[22, c("wall of heart")[1] - 2, c("wall of heart")[2] + 34],
     [58, c("wall of heart")[1] + 16, c("wall of heart")[2] + 10]],
    "They narrow the airways and drive the glands of the bronchi.", w=1.3)

add("para", "Pelvic splanchnic nerves",
    [[12, LV["S2"][1] + 2, LV["S2"][2]],
     [22, LV["S3"][1] - 24, LV["S3"][2] - 6],
     [16, c("urinary bladder")[1] + 14, c("urinary bladder")[2] + 6]],
    "Second to fourth sacral. The only parasympathetic outflow below the "
    "head, and the one that empties the bladder and the bowel.", w=1.8)

for name, lev, target, note in [
    ("Ciliary ganglion", None, [EYE[0] + 12, EYE[1] + 14, EYE[2] + 2],
     "On the third cranial nerve, in the orbit. It constricts the pupil "
     "and thickens the lens for near vision."),
    ("Pterygopalatine ganglion", None, [26, MAND[1] - 22, MAND[2] + 30],
     "On the seventh cranial nerve. It makes tears."),
    ("Submandibular ganglion", None, [30, MAND[1] - 40, MAND[2] - 12],
     "On the seventh cranial nerve, for two of the three salivary glands."),
    ("Otic ganglion", None, [30, MAND[1] + 6, MAND[2] - 4],
     "On the ninth cranial nerve, for the parotid gland.")]:
    add("para", name, [[target[0], target[1], target[2]],
                       [target[0], target[1], target[2] - 3]],
        note, k="ganglion", w=6)

GROUPS = [
    ("all", "The whole system"),
    ("cns", "Central"),
    ("periph", "Peripheral"),
    ("cranial", "Cranial nerves"),
    ("symp", "Sympathetic"),
    ("para", "Parasympathetic"),
]

BLURB = {
 "all": "Brain and cord in the middle, the thirty-one pairs of spinal "
        "nerves leaving between the vertebrae, the twelve cranial pairs "
        "leaving the skull, and the two autonomic outflows that run the "
        "organs without asking.",
 "cns": "The brain and the spinal cord. The cord ends at the first or "
        "second lumbar vertebra, far above the bottom of the spine, "
        "because the column keeps growing after the cord stops. Below "
        "that the roots run on alone as the cauda equina.",
 "periph": "Thirty-one pairs of spinal nerves, each leaving between two "
           "vertebrae and each serving a band of skin and a set of "
           "muscles. Four of them are rewoven into plexuses, which is why "
           "one nerve in the arm carries fibres from four different levels "
           "of the cord.",
 "cranial": "Twelve pairs leaving the brain directly rather than the cord. "
            "Two of them, the first and second, are not really nerves but "
            "outgrowths of the brain itself. One of them, the tenth, "
            "leaves the head entirely and runs to the gut.",
 "symp": "Fight or flight, though it runs all day. The outflow leaves the "
         "cord only between the first thoracic and the second lumbar "
         "nerve, and the chain beside the spine spreads it from the eye to "
         "the foot. Its ganglia sit near the spine and far from the "
         "target, so one fibre in can drive many out.",
 "para": "Rest and digest. The outflow is craniosacral: four cranial "
         "nerves and the second to fourth sacral, with nothing in between. "
         "Its ganglia sit on or in the organ itself, so its effects are "
         "local where the sympathetic ones are general.",
}
