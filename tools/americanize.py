#!/usr/bin/env python3
"""Turn British spellings and words into American ones across the site's
English text: the page builders and their data, the section sources, and
the built pages themselves.

The Spanish pages are left alone, as are proper names, URLs, and the
titles of cited works, which keep the spelling they were published with.

Usage: python3 americanize.py [--check]   (--check only reports)
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SPANISH = {"mexico", "chihuahua", "el-terrero", "norte-mexico", "nueva-espana", "valle-santa-maria", "ruta-namiquipa", "cabalgata-villista", "linea-misiones", "cine-cronologia", "cine-mexicano", "premios-ariel"}
DATA_PAGES = {"chinese", "languages"}   # third-party glosses and names, left as they are

PAIRS = {
    "colour": "color", "colours": "colors", "coloured": "colored", "colouring": "coloring", "colourless": "colorless", "colourful": "colorful",
    "centre": "center", "centres": "centers", "centred": "centered", "centring": "centering",
    "metre": "meter", "metres": "meters", "kilometre": "kilometer", "kilometres": "kilometers", "centimetre": "centimeter", "centimetres": "centimeters",
    "millimetre": "millimeter", "millimetres": "millimeters", "nanometre": "nanometer", "nanometres": "nanometers", "micrometre": "micrometer", "micrometres": "micrometers",
    "femtometre": "femtometer", "femtometres": "femtometers", "picometre": "picometer", "picometres": "picometers",
    "litre": "liter", "litres": "liters", "millilitre": "milliliter", "millilitres": "milliliters",
    "grey": "gray", "greys": "grays", "greyer": "grayer", "greyish": "grayish",
    "fibre": "fiber", "fibres": "fibers",
    "tonne": "metric ton", "tonnes": "metric tons",
    "defence": "defense", "defences": "defenses", "licence": "license", "catalogue": "catalog", "catalogued": "cataloged", "catalogues": "catalogs", "programme": "program", "programmes": "programs",
    "labelled": "labeled", "labelling": "labeling", "travelled": "traveled", "traveller": "traveler", "travellers": "travelers", "travelling": "traveling",
    "modelled": "modeled", "modelling": "modeling", "cancelled": "canceled", "judgement": "judgment", "judgements": "judgments",
    "artefact": "artifact", "artefacts": "artifacts", "haemoglobin": "hemoglobin", "oesophagus": "esophagus", "anaesthetised": "anesthetized", "anaesthesia": "anesthesia", "anaesthetic": "anesthetic",
    "paralysed": "paralyzed", "paralyse": "paralyze", "sceptic": "skeptic", "sceptics": "skeptics", "scepticism": "skepticism", "sceptical": "skeptical",
    "civilisation": "civilization", "civilisations": "civilizations", "ionisation": "ionization", "sterilise": "sterilize", "sterilised": "sterilized", "rasterised": "rasterized", "digitised": "digitized",
    "colonisation": "colonization", "colonised": "colonized", "colonise": "colonize", "crystallisation": "crystallization", "crystallise": "crystallize", "stabilisation": "stabilization",
    "normalise": "normalize", "normalised": "normalized", "recognised": "recognized", "recognise": "recognize", "randomised": "randomized", "standardised": "standardized", "summarised": "summarized", "summarise": "summarize",
    "organised": "organized", "organise": "organize", "realise": "realize", "realised": "realized", "characterised": "characterized", "minimise": "minimize", "maximise": "maximize", "optimise": "optimize", "optimised": "optimized",
    "emphasise": "emphasize", "emphasised": "emphasized", "specialised": "specialized", "visualise": "visualize", "neutralise": "neutralize", "oxidise": "oxidize", "oxidised": "oxidized", "synthesise": "synthesize", "synthesised": "synthesized",
    "magnetised": "magnetized", "polarised": "polarized", "polarisation": "polarization", "vaporise": "vaporize", "vaporised": "vaporized", "fertilise": "fertilize", "fertilised": "fertilized", "utilise": "utilize", "criticised": "criticized",
    "symbolise": "symbolize", "stabilise": "stabilize", "stabilised": "stabilized", "localised": "localized", "generalised": "generalized", "idealised": "idealized", "industrialised": "industrialized", "categorised": "categorized",
    "favourite": "favorite", "favourites": "favorites", "favour": "favor", "favours": "favors", "favoured": "favored", "favourable": "favorable",
    "behaviour": "behavior", "behaviours": "behaviors", "behavioural": "behavioral", "vapour": "vapor", "vapours": "vapors",
    "neighbour": "neighbor", "neighbours": "neighbors", "neighbouring": "neighboring", "neighbourhood": "neighborhood", "neighbourhoods": "neighborhoods",
    "armoured": "armored", "armour": "armor", "aluminium": "aluminum", "sulphur": "sulfur", "sulphuric": "sulfuric", "sulphide": "sulfide", "sulphate": "sulfate",
    "petrol": "gasoline", "maths": "math", "anticlockwise": "counterclockwise", "towards": "toward", "whilst": "while", "amongst": "among",
    "honour": "honor", "honours": "honors", "honoured": "honored", "harbour": "harbor", "harbours": "harbors", "flavour": "flavor", "flavours": "flavors", "labour": "labor", "labours": "labors",
    "humour": "humor", "odour": "odor", "odours": "odors", "rumour": "rumor", "rumours": "rumors", "savour": "savor", "endeavour": "endeavor", "tumour": "tumor", "tumours": "tumors",
    "analyse": "analyze", "analysed": "analyzed", "analysing": "analyzing", "encyclopaedia": "encyclopedia", "encyclopaedias": "encyclopedias", "mould": "mold", "moulds": "molds", "moulded": "molded",
    "plough": "plow", "ploughs": "plows", "ploughed": "plowed", "practise": "practice", "practised": "practiced", "enrol": "enroll", "fulfil": "fulfill", "skilful": "skillful", "learnt": "learned",
    "ageing": "aging", "manoeuvre": "maneuver", "manoeuvres": "maneuvers", "smoulder": "smolder", "smouldering": "smoldering", "aeroplane": "airplane", "aeroplanes": "airplanes", "cosy": "cozy", "yoghurt": "yogurt",
    "speciality": "specialty", "mediaeval": "medieval", "orthopaedic": "orthopedic", "paediatric": "pediatric", "anaemia": "anemia", "anaemic": "anemic", "diarrhoea": "diarrhea", "oestrogen": "estrogen", "foetus": "fetus",
    "gaol": "jail", "instalment": "installment", "wilful": "willful", "lorry": "truck", "lorries": "trucks", "kerb": "curb", "storeys": "stories", "pyjamas": "pajamas", "cheque": "check", "jewellery": "jewelry",
    "draughts": "drafts", "mum": "mom", "caesium": "cesium",
}
# phrases and names that keep their spelling
# Phrases that must keep a British spelling: place names, the titles of cited
# works, and Wikipedia article titles, whose spelling is part of the address.
KEEP = ["Grey Range", "Greylock", "Sama Mum", "Mum\"", "Tyre", "Third reference catalogue of bright galaxies", "Towards a natural system of organisms", "colour_", "Colour_", "_colour", "Labourdonnais", "Great grey owl", "Great_grey_owl"]

WORD = re.compile(r"\b(" + "|".join(sorted(PAIRS, key=len, reverse=True)) + r")\b", re.I)


def fix_case(src, dst):
    if src.isupper():
        return dst.upper()
    if src[0].isupper():
        return dst[0].upper() + dst[1:]
    return dst


def americanize(text):
    # shield the kept phrases, URLs, and the titles of cited works
    shields = []

    def shield(m):
        shields.append(m.group(0))
        return f"\x00{len(shields) - 1}\x00"

    text = re.sub(r"https?://[^\s\"'<>)]+", shield, text)
    text = re.sub(r"<i>[^<]*</i>", shield, text)                           # titles in rendered references
    text = re.sub(r"apa\.(?:article|book|web)\([^\n]*", shield, text)      # titles in the data
    for k in KEEP:
        text = text.replace(k, shield(re.match(re.escape(k), k)))
    text = WORD.sub(lambda m: fix_case(m.group(0), PAIRS[m.group(0).lower()]), text)
    while "\x00" in text:   # shields can nest, a URL inside a citation line, so restore until none are left
        text = re.sub(r"\x00(\d+)\x00", lambda m: shields[int(m.group(1))], text)
    return text


def targets():
    out = []
    for p in sorted(ROOT.glob("*.html")):
        if p.stem in SPANISH or p.stem in DATA_PAGES:
            continue
        out.append(p)
    out += sorted(ROOT.glob("sections/*.md")) + sorted(ROOT.glob("posts/*")) + sorted(ROOT.glob("tools/*.py")) + [ROOT / "tools" / "periodic_table.json"]
    return [p for p in out if p.is_file() and p.name not in ("americanize.py", "rotations.py")]


if __name__ == "__main__":
    check = "--check" in sys.argv
    changed = 0
    for p in targets():
        s = p.read_text(encoding="utf-8")
        t = americanize(s)
        if t != s:
            changed += 1
            n = sum(1 for _ in WORD.finditer(s))
            print(f"{p.relative_to(ROOT)}: {n} words")
            if not check:
                p.write_text(t, encoding="utf-8")
    print(f"{changed} files {'would change' if check else 'changed'}")
