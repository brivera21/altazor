#!/usr/bin/env python3
"""Bake the world's language classification into tools/data/languages.json.

Source: Glottolog 5.2.1 as CLDF (CC-BY 4.0). Each top-level family
carries a Newick string under the 'subclassification' parameter that
encodes its whole internal tree by glottocode; languages.csv gives every
glottocode a name, a level, a macroarea and an ISO 639-3 code.

Dialects are pruned, so a tip is a language in Glottolog's sense.
Glottolog's non-genealogical top-level nodes (sign languages, pidgins,
mixed and artificial languages, speech registers, the unclassifiable)
are gathered under one heading rather than shown as families; its
bookkeeping and unattested entries, which are retired or undocumented
codes rather than languages, are left out. Node:
  {"n": name, "g": glottocode, "a": macroarea, "e": iso639-3, "k": [...]}

Inputs, cached in /tmp/glot (fetched from raw.githubusercontent.com):
  glot_lang.csv    glottolog-cldf/cldf/languages.csv
  glot_values.csv  glottolog-cldf/cldf/values.csv

Usage: python3 build_languages_data.py
"""

import csv
import json
from pathlib import Path

csv.field_size_limit(10 ** 8)

SRC = Path("/tmp")
OUT = Path(__file__).parent / "data" / "languages.json"
# a line for the families a reader is most likely to open first
BLURB = {
    "atla1278": "West and central Africa and, through Bantu, most of the "
                "continent south of the equator.",
    "aust1307": "From Taiwan across the islands to Madagascar, Hawaii and "
                "New Zealand, the widest spread before the colonial era.",
    "indo1319": "From the Atlantic to Bengal by the iron age, and to the "
                "Americas and Australia after 1500.",
    "sino1245": "Chinese, Burmese, Tibetan and the languages of the "
                "Himalayan valleys.",
    "afro1255": "Arabic, Hebrew, Amharic, Somali, Hausa and the Berber "
                "languages, across north Africa and the Near East.",
    "nucl1709": "The New Guinea highlands, where farming began "
                "independently and the valleys kept their own tongues.",
    "pama1250": "Most of Australia, spread late and fast over a continent "
                "settled for tens of thousands of years.",
    "otom1299": "The languages of central and southern Mexico, Zapotec and "
                "Mixtec among them.",
    "aust1305": "Vietnamese and Khmer, and the hill languages from eastern "
                "India to the Mekong.",
    "taik1256": "Thai and Lao, and the Kra-Dai languages of southern China.",
    "drav1251": "Tamil, Telugu, Kannada and Malayalam, spoken in south "
                "India before Indo-European reached it.",
    "turk1311": "From Turkey to Siberia, the languages of the steppe "
                "corridor.",
    "ural1272": "Finnish, Estonian, Hungarian, Saami and the languages of "
                "the Ob and the Volga.",
    "araw1281": "The Amazon and the Caribbean, the first American family "
                "Europeans met.",
    "tupi1275": "The Amazon and the Brazilian coast; Tupi words travelled "
                "into Portuguese and out to the world.",
    "utoa1244": "From the Great Basin to central Mexico, Nahuatl and "
                "Shoshone at its ends.",
    "sign1238": "Sign languages have families of their own, by school and "
                "community rather than by spoken parent.",
    "pidg1258": "Contact languages without a single parent, born of trade, "
                "plantation and port.",
    "arti1236": "Languages designed rather than inherited, Esperanto and "
                "Klingon among them.",
    "uncl1493": "Attested too thinly to place, often from a word list and "
                "nothing else.",
}


def parse_newick(s):
    """Newick with glottocodes as labels -> (code, [children])."""
    pos = 0

    def node():
        nonlocal pos
        kids = []
        if s[pos] == "(":
            pos += 1
            while True:
                kids.append(node())
                if s[pos] == ",":
                    pos += 1
                    continue
                break
            assert s[pos] == ")", s[pos]
            pos += 1
        start = pos
        while pos < len(s) and s[pos] not in "(),:;":
            pos += 1
        label = s[start:pos]
        if pos < len(s) and s[pos] == ":":
            pos += 1
            while pos < len(s) and s[pos] not in "(),;":
                pos += 1
        return (label, kids)

    return node()


def main():
    langs = {}
    with open(SRC / "glot_lang.csv", newline="") as f:
        for r in csv.DictReader(f):
            langs[r["Glottocode"]] = r
    subs = {}
    with open(SRC / "glot_values.csv", newline="") as f:
        for r in csv.DictReader(f):
            if r["Parameter_ID"] == "subclassification":
                subs[r["Language_ID"]] = r["Value"]

    def build(code):
        """The pruned subtree under one glottocode, or None for a dialect."""
        row = langs.get(code)
        if row is None or row["Level"] == "dialect":
            return None
        n = {"n": row["Name"], "g": code}
        if row["Macroarea"]:
            n["a"] = row["Macroarea"]
        if row["ISO639P3code"]:
            n["e"] = row["ISO639P3code"]
        return n

    def walk(nw):
        code, kids = nw
        n = build(code)
        if n is None:
            return None
        out = [k for k in (walk(c) for c in kids) if k]
        if out:
            out.sort(key=lambda x: (-count(x), x["n"]))
            n["k"] = out
        return n

    def count(n):
        if "k" not in n:
            return 1
        return sum(count(c) for c in n["k"])

    # Glottolog's own non-genealogical headings
    ASIDE = {"sign1238", "pidg1258", "mixe1287", "arti1236", "spee1234",
             "uncl1493"}
    DROP = {"book1242", "unat1236"}  # retired codes and undocumented entries

    families, isolates, aside = [], [], []
    for code, row in langs.items():
        if row["Family_ID"] or row["Level"] == "dialect":
            continue
        if row["Level"] == "family":
            if code in DROP:
                continue
            nw = subs.get(code)
            if not nw:
                continue
            t = walk(parse_newick(nw))
            if t:
                (aside if code in ASIDE else families).append(t)
        elif row["Level"] == "language":
            n = build(code)
            if n:
                isolates.append(n)

    families.sort(key=lambda x: (-count(x), x["n"]))
    isolates.sort(key=lambda x: x["n"])
    aside.sort(key=lambda x: (-count(x), x["n"]))
    for n in families + aside:
        if n["g"] in BLURB:
            n["b"] = BLURB[n["g"]]
    iso_node = {"n": "Isolates", "g": "", "k": isolates,
                "b": "Languages with no demonstrated relative. Some are the "
                     "last of a family; for others the evidence for a "
                     "relative has not held up."}
    aside_node = {"n": "Outside the family tree", "g": "", "k": aside,
                  "b": "Glottolog's non-genealogical headings: languages "
                       "whose history is not descent from a parent language, "
                       "and entries it cannot place."}

    root = {"n": "The languages of the world", "g": "",
            "b": "Every language Glottolog classifies, by descent. A family "
                 "opens into its branches and they into languages.",
            "k": families + [iso_node, aside_node]}
    tot = count(root) - count(aside_node)
    OUT.write_text(json.dumps(root, separators=(",", ":"),
                              ensure_ascii=False), encoding="utf-8")
    print(f"{len(families)} families, {len(isolates)} isolates, "
          f"{tot:,} languages -> {OUT.name} ({OUT.stat().st_size:,} B)")
    for t in families[:8]:
        print(f"  {t['n']}: {count(t):,}")


if __name__ == "__main__":
    main()
