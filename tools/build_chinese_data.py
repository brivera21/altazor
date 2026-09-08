#!/usr/bin/env python3
"""Bake tools/data/chinese.json for chinese.html.

Three sources, fetched once and then checked in, so the page builds
offline:

  Jun Da (2004), Modern Chinese Character Frequency List. 258 million
  characters of written modern Chinese. Rank, raw count and the running
  cumulative share, which is what the coverage curve is drawn from.

  CC-CEDICT, the community Chinese-English dictionary, for glosses and
  pinyin.

  hanziDB, which carries the Unihan radical, stroke count and the HSK
  level for each character, keyed to Jun Da's rank.

  Hermit Dave's FrequencyWords, word counts from the OpenSubtitles 2018
  corpus, for the word list and for a second character count taken from
  speech rather than from writing.

The two character counts are the point of the comparison view: one is
written Chinese and one is film dialogue, and the same character can sit
far apart in the two.

Usage: python3 build_chinese_data.py [srcdir]
"""

import csv
import json
import re
import sys
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/zh")
OUT = Path(__file__).parent / "data" / "chinese.json"

NCHAR = 1200        # characters carried in the grid
NWORD = 1200        # words carried in the grid
CURVE = 400         # points on each coverage curve

TONE = {"a": "āáǎà", "e": "ēéěè", "i": "īíǐì", "o": "ōóǒò",
        "u": "ūúǔù", "v": "ǖǘǚǜ", "A": "ĀÁǍÀ", "E": "ĒÉĚÈ",
        "I": "ĪÍǏÌ", "O": "ŌÓǑÒ", "U": "ŪÚǓÙ"}


def mark(syl):
    """cao3 to cǎo. The tone goes on a, o or e, else the last vowel."""
    m = re.fullmatch(r"([A-Za-zü:]+)([1-5])", syl)
    if not m:
        return syl.replace("u:", "ü")
    body, t = m.group(1).replace("u:", "v"), int(m.group(2))
    if t == 5:
        return body.replace("v", "ü")
    for v in "aoe":
        if v in body.lower():
            i = body.lower().index(v)
            break
    else:
        i = max((body.lower().rfind(c) for c in "iuv"), default=-1)
        if i < 0:
            return body.replace("v", "ü")
    ch = body[i]
    low = ch.lower()
    key = "v" if low == "v" else low
    row = TONE.get(ch) or TONE.get(key)
    out = body[:i] + (row[t - 1] if row else ch) + body[i + 1:]
    return out.replace("v", "ü")


def pinyin(s):
    return " ".join(mark(x) for x in s.split())


# ---- hanziDB: radical, strokes, HSK -------------------------------------
HZ = {}
with open(SRC / "hanzidb.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        # a few rows carry two stroke counts, as "8 9"; take the first
        st = (row["stroke_count"] or "").split()
        hsk = (row["hsk_level"] or "").split()
        HZ[row["charcter"]] = dict(
            rad=row["radical"], py=row["pinyin"].split("/")[0].strip(),
            st=int(st[0]) if st else 0,
            hsk=int(hsk[0]) if hsk else None)

# ---- CC-CEDICT ----------------------------------------------------------
# Two vintages, because neither alone covers the everyday compounds: the
# 2013 file is much larger but drops transparent combinations such as
# yi1 ge4 and hen3 duo1 that the 2007 file still carries. The newer file
# wins wherever both have an entry.
CED, TRAD, SIMPCH = {}, set(), set()
LINE = re.compile(r"^(\S+) (\S+) \[([^\]]*)\] /(.*)/$")
for src in ("cedict.u8", "cedict2.u8"):
    seen = set()
    for line in (SRC / src).read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            continue
        m = LINE.match(line)
        if not m:
            continue
        trad, simp, py, gloss = m.group(1), m.group(2), m.group(3), m.group(4)
        # a character with several readings gets several entries, in
        # order, so the first one is the everyday reading and the ones
        # after it are the rare ones. Keep the first within a file, and
        # let the newer file replace the older file's whole entry.
        if simp not in seen:
            seen.add(simp)
            CED.setdefault(simp, []).insert(0, (pinyin(py), gloss.split("/")))
        else:
            CED[simp].append((pinyin(py), gloss.split("/")))
        SIMPCH.update(simp)
        if trad != simp:
            TRAD.add(trad)


def clean(s):
    """A sense with its bracketed asides taken out, or, when that would
    leave nothing, the aside itself with the brackets removed."""
    t = re.sub(r"\s*\(.*?\)\s*", " ", s).strip(" ;,")
    t = re.sub(r"\bCL:.*", "", t).strip()
    if t:
        return t
    return s.strip("()").strip()


DULL = ("surname ", "old variant of", "variant of", "see ",
        "used in given names", "Japanese variant")


def pick(w):
    """The everyday entry for a word. A character with several readings
    gets one dictionary entry per reading, in alphabetical order of
    pinyin rather than in order of use, so the reading Unihan records as
    the common one wins where there is one. Failing that, an entry that
    is only a surname or a note about a variant loses to one that is not."""
    ent = CED.get(w)
    if not ent:
        return None
    if len(w) == 1:
        want = (HZ.get(w) or {}).get("py", "")
        if want:
            for e in ent:
                if e[0] == want:
                    return e
    for e in ent:
        if not any(e[1][0].startswith(d) for d in DULL):
            return e
    return ent[0]


def look(w, limit=64):
    """One pinyin and one short gloss for a word, from CC-CEDICT. A word
    the dictionary does not carry is glossed from its characters, and the
    caller is told, since a composed gloss is a guess at the sum and not
    a dictionary meaning."""
    ent = pick(w)
    if not ent:
        if len(w) < 2:
            return "", "", 0
        # split into the longest pieces the dictionary knows, so hen3
        # piao4liang5 reads very + pretty and not very + float + bright
        pieces, i = [], 0
        while i < len(w):
            for j in range(len(w), i, -1):
                if pick(w[i:j]):
                    pieces.append(w[i:j])
                    i = j
                    break
            else:
                return "", "", 0
        parts = [look(x, 26) for x in pieces]
        if not all(p[1] for p in parts):
            return "", "", 0
        py = " ".join(p[0] for p in parts)
        g = " + ".join(p[1].split(";")[0].strip() for p in parts)
        return py, (g[:limit] if len(g) <= limit
                    else g[:limit].rsplit(" ", 1)[0] + "..."), 1
    py, senses = ent
    out = []
    for s in senses:
        s = clean(s)
        if s and not s.startswith("variant of") and not s.startswith("see "):
            out.append(s)
        if len("; ".join(out)) > limit:
            break
    g = "; ".join(out)
    if len(g) > limit:
        g = g[:limit].rsplit(" ", 1)[0] + "..."
    return py, g or clean(senses[0] if senses else ""), 0


# ---- Jun Da: written Chinese --------------------------------------------
chars, cum = [], []
for line in (SRC / "junda.txt").read_text(encoding="utf-8").splitlines():
    p = line.split("\t")
    if len(p) < 4 or not p[0].strip().isdigit():
        continue
    rank, ch, n, c = int(p[0]), p[1], int(p[2]), float(p[3])
    chars.append((rank, ch, n, c))
TOTAL = sum(n for _, _, n, _ in chars)

# ---- OpenSubtitles: words, and characters as spoken ---------------------
words, chcount = [], {}
for line in (SRC / "zh50k.txt").read_text(encoding="utf-8").splitlines():
    p = line.split()
    if len(p) != 2:
        continue
    w, n = p[0], int(p[1])
    if not re.fullmatch(r"[一-鿿]+", w):
        continue
    # the subtitle list carries some traditional spelling and some rare
    # characters that are not simplified Chinese at all. A character that
    # never appears on the simplified side of any dictionary entry is one
    # or the other. This keeps the characters that are simplified in
    # their own right while also being somebody else's traditional form,
    # such as the me of shen2me.
    if any(c not in SIMPCH for c in w):
        continue
    # a word neither dictionary knows, and whose characters cannot be
    # glossed either, is subtitle noise rather than a word
    if not look(w)[1]:
        continue
    words.append((w, n))
    for ch in w:
        chcount[ch] = chcount.get(ch, 0) + n
WTOT = sum(n for _, n in words)
STOT = sum(chcount.values())
spoken = sorted(chcount.items(), key=lambda t: -t[1])
SRANK = {ch: i + 1 for i, (ch, _) in enumerate(spoken)}


def curve(pairs, n=CURVE):
    """(rank, cumulative share) sampled evenly in log rank."""
    import math
    out, N = [], len(pairs)
    seen = set()
    for i in range(n):
        r = min(N, max(1, round(10 ** (math.log10(N) * i / (n - 1)))))
        if r in seen:
            continue
        seen.add(r)
        out.append([r, round(pairs[r - 1], 4)])
    return out


ccum = [c for _, _, _, c in chars]
run, wcum = 0, []
for _, n in words:
    run += n
    wcum.append(run / WTOT * 100)
run, scum = 0, []
for _, n in spoken:
    run += n
    scum.append(run / STOT * 100)

CH = []
for rank, ch, n, c in chars[:NCHAR]:
    py, g, _ = look(ch)
    h = HZ.get(ch, {})
    CH.append([ch, py, g, round(n / TOTAL * 100, 4), round(c, 3),
               h.get("st") or 0, h.get("rad") or "", h.get("hsk"),
               SRANK.get(ch, 0)])

WD = []
for i, (w, n) in enumerate(words[:NWORD]):
    py, g, made = look(w)
    WD.append([w, py, g, round(n / WTOT * 100, 4), round(wcum[i], 3), made])

data = dict(
    chars=CH, words=WD,
    ccurve=curve(ccum), wcurve=curve(wcum), scurve=curve(scum),
    nchar=len(chars), nword=len(words),
    ctotal=TOTAL, wtotal=WTOT, stotal=STOT,
    marks={
        "c": [[r, round(ccum[r - 1], 1)] for r in
              (10, 100, 250, 500, 1000, 1500, 2000, 2500, 3000, 3500)],
        "w": [[r, round(wcum[r - 1], 1)] for r in
              (10, 100, 250, 500, 1000, 2000, 5000, 10000, 20000, 50000)
              if r <= len(wcum)],
    },
)
OUT.write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=False))
print(f"{len(chars)} characters ({TOTAL:,} tokens), "
      f"{len(words)} words ({WTOT:,} tokens)")
print(f"grid: {len(CH)} characters, {len(WD)} words")
print("written coverage:", ", ".join(f"{r}:{c}%" for r, c in data["marks"]["c"]))
print("   word coverage:", ", ".join(f"{r}:{c}%" for r, c in data["marks"]["w"]))
print(f"{OUT.stat().st_size/1024:.0f} KB")
