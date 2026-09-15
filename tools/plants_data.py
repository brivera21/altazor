#!/usr/bin/env python3
"""The data behind plants.html: the parts of a flowering plant, the light it
takes in, and the kinds of plant there are.

The absorption curves are chlorophyll a and b at their measured peaks, drawn
as sums of Gaussians; the photosynthesis figures are the textbook equation
and the global production estimates of Field and colleagues; the kinds and
their species counts are Kew's.
"""

import apa

# the parts of a plant: k, name, a line on what it does, a number, source
PARTS = [
    ("root", "the roots", "Anchor the plant and draw up water and minerals through hairs a tenth of a millimetre across, of which a single rye plant was found to have fourteen billion. Nothing green happens here; roots are fed sugar from above.",
     "a rye plant's root hairs, laid end to end: 10,000 km", "Dittmer 1937; Wikipedia, Root"),
    ("stem", "the stem", "Holds the leaves up to the light and carries traffic both ways: water and minerals up through the xylem, dead tubes pulled by evaporation at the leaves, and sugar down through the phloem, living tubes pushed by pressure.",
     "water rises in a tall tree at up to a metre a minute, and the pull at the top of the tallest reaches twenty or thirty atmospheres", "Wikipedia, Xylem; Wikipedia, Phloem"),
    ("leaf", "the leaf", "A flat solar panel. Light is caught in chloroplasts in the cells beneath the surface; carbon dioxide enters through pores, the stomata, and water leaves through them, some 97 percent of all the water the roots take up.",
     "stomata: a hundred to a thousand on every square millimetre", "Wikipedia, Leaf; Wikipedia, Stoma"),
    ("flower", "the flower", "The organ of sex, built to be visited. Petals advertise; stamens make pollen; the pistil at the centre receives it and grows the seeds. Most flowering plants have both sexes in one flower.",
     "about nine tenths of flowering plants are pollinated by animals", "Ollerton et al. 2011; Wikipedia, Flower"),
    ("fruit", "the fruit and seed", "A seed is an embryo packed with food and sealed against drought; the fruit around it is the ovary grown up, sweet to be eaten and carried away, or winged, hooked or buoyant to travel some other way.",
     "the smallest seeds, orchids', weigh a millionth of a gram; the largest, the coco de mer's, twenty kilograms", "Wikipedia, Seed"),
    ("chloroplast", "the chloroplasts", "Green bodies a few microns across inside the leaf cells, descended from a bacterium swallowed a billion and a half years ago and never digested. Each holds stacks of membranes studded with chlorophyll.",
     "a leaf cell holds tens to a hundred of them", "Wikipedia, Chloroplast"),
]

# chlorophyll absorption peaks (nm) and widths for the drawn curves; peaks are the measured maxima in ether
CHLOROPHYLL = {
    "a": {"peaks": [(430, 22, 1.0), (662, 14, 0.8)], "colour": "#9be564"},
    "b": {"peaks": [(453, 20, 0.85), (642, 16, 0.4)], "colour": "#6ee7f2"},
}

# photosynthesis
PHOTO = {
    "equation": "6 CO₂ + 6 H₂O + light → C₆H₁₂O₆ + 6 O₂",
    "energy_kj": 2870,          # per mole of glucose
    "npp_pg": 104.9, "npp_land": 56.4, "npp_ocean": 48.5,   # Field et al. 1998, petagrams of carbon a year
    "efficiency": "one to two percent of the sunlight that falls on a field ends up as plant, against a theoretical ceiling near five",
}

# the kinds of plant: k, name, species (Kew 2016 and standard counts), first appeared (million years ago), a line, source
KINDS = [
    ("moss", "mosses and liverworts", 20000, 470, "The first plants on land, and still without roots or veins: they soak up water where they sit and cannot grow tall. A moss needs a film of water for its sperm to swim to the egg.", "Wikipedia, Bryophyte"),
    ("fern", "ferns and horsetails", 12000, 420, "The first plants with veins, xylem and phloem, and so the first to stand up; the coal forests were made of their giant relatives. They still spread by spores and still need water to breed.", "Wikipedia, Fern"),
    ("conifer", "conifers and their kin", 1100, 385, "The first seeds: an embryo sealed with food, so a plant could breed without standing water and colonise the dry interior. Pines, firs, cypresses, ginkgo and the cycads, few in species but vast in numbers and size.", "Wikipedia, Gymnosperm"),
    ("flower", "flowering plants", 369000, 135, "The latest and the most: nine of every ten plant species. Flowers recruited insects to carry pollen and fruits recruited animals to carry seeds, and in a hundred million years they took over the land.", "Wikipedia, Flowering plant"),
]

REFS = [
    (apa.article("Field, C. B., Behrenfeld, M. J., Randerson, J. T., &amp; Falkowski, P.", 1998, "Primary production of the biosphere: Integrating terrestrial and oceanic components",
                 "Science", 281, 5374, "237-240", "https://doi.org/10.1126/science.281.5374.237"),
     "The biosphere's production, 105 billion tonnes of carbon a year, split near evenly between land and sea."),
    (apa.article("Dittmer, H. J.", 1937, "A quantitative study of the roots and root hairs of a winter rye plant (Secale cereale)",
                 "American Journal of Botany", 24, 7, "417-420", "https://doi.org/10.1002/j.1537-2197.1937.tb09121.x"),
     "One rye plant's fourteen billion root hairs, 10,000 km of them."),
    (apa.article("Ollerton, J., Winfree, R., &amp; Tarrant, S.", 2011, "How many flowering plants are pollinated by animals?",
                 "Oikos", 120, 3, "321-326", "https://doi.org/10.1111/j.1600-0706.2010.18644.x"),
     "About 87.5 percent of flowering plant species are pollinated by animals."),
    (apa.article("Zhu, X.-G., Long, S. P., &amp; Ort, D. R.", 2008, "What is the maximum efficiency with which photosynthesis can convert solar energy into biomass?",
                 "Current Opinion in Biotechnology", 19, 2, "153-159", "https://doi.org/10.1016/j.copbio.2008.02.004"),
     "The efficiency of photosynthesis: a ceiling near 4.6 percent for most plants, 6 for maize and its kind, and one or two in the field."),
    (apa.web("Royal Botanic Gardens, Kew", 2016, "State of the world's plants 2016", "Royal Botanic Gardens, Kew", "https://stateoftheworldsplants.org/2016/"),
     "391,000 vascular plant species, 369,000 of them flowering."),
]
REFS += [(apa.wiki(f"https://en.wikipedia.org/wiki/{p}"), a) for p, a in [
    ("Photosynthesis", "The equation and its energy, 2,870 kJ a mole of glucose."),
    ("Chlorophyll", "The absorption peaks: chlorophyll a at 430 and 662 nm, b at 453 and 642, in ether."),
    ("Plant", "The kinds and when they appeared."),
    ("Root", None), ("Xylem", None), ("Phloem", None), ("Leaf", None), ("Stoma", None), ("Flower", None), ("Seed", None), ("Chloroplast", None),
    ("Bryophyte", None), ("Fern", None), ("Gymnosperm", None), ("Flowering_plant", None),
]]
