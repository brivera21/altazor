#!/usr/bin/env python3
"""The words behind plates.html. The geometry is tools/data/plates.json,
made by tools/make_plates.py from Bird's PB2002 model.

Plate areas are measured from the model's polygons on a 1/6 degree grid and
agree with Bird's table to a fraction of a percent. Relative velocities along
the boundaries are Bird's, from NUVEL-1A and later local models.
"""

import apa

# the kinds of boundary, in the order of the data file's class codes
# code, name, colour, a line
CLASSES = [
    ("OSR", "a spreading ridge", "#f28cb0", "Two plates pulling apart under the ocean. Mantle rises to fill the gap, melts, and freezes into new sea floor; the ridge stands high because the young rock is hot."),
    ("CRB", "a continental rift", "#f2a0c0", "A continent being pulled apart: a valley with faults on both sides and volcanoes down the middle. Given time it becomes a spreading ridge with an ocean in it."),
    ("SUB", "a subduction zone", "#58a6ff", "One plate dives beneath another and sinks into the mantle, bending down along a trench. The deepest earthquakes, the biggest ones, and most of the volcanoes on land are here."),
    ("OTF", "an oceanic transform", "#ffb02e", "Two plates sliding past each other, offsetting a ridge. No crust is made or lost; the fault is a strike-slip seam across the sea floor."),
    ("CTF", "a continental transform", "#ffc85e", "Two plates sliding past each other on land: the San Andreas, the Alpine Fault, the North Anatolian. Shallow earthquakes, no volcanoes."),
    ("CCB", "a continental collision", "#b48cf2", "Two continents meeting. Neither will sink, so the crust crumples and thickens into mountains: the Himalaya, the Alps, the Zagros."),
    ("OCB", "an oceanic convergence", "#9d7ae0", "Convergence with no clear trench, where the crust shortens and thickens without one plate diving cleanly under the other."),
]

# plates with something to say: code, a line, source
NOTES = {
    "PA": ("The largest plate, all ocean, and shrinking: trenches ring it on the north and west, and it is heading northwest at about seven centimetres a year, leaving the Hawaiian chain behind it as it passes over a hot spot.", "Bird 2003; Wikipedia, Pacific plate"),
    "AF": ("Africa in the middle, ridges on three sides, so the plate is growing at its edges and moving slowly. The East African Rift is tearing the Somali side off it.", "Bird 2003; Wikipedia, African plate"),
    "AN": ("Ringed almost entirely by spreading ridges, with no trench, so the plate hardly moves and grows on every side.", "Bird 2003; Wikipedia, Antarctic plate"),
    "NA": ("The Atlantic half is growing at the Mid-Atlantic Ridge; the Pacific edge slides past the Pacific plate along the San Andreas and dives under it in Alaska.", "Bird 2003; Wikipedia, North American plate"),
    "EU": ("From the Mid-Atlantic Ridge to Japan. India has been pushing into its southern edge for fifty million years, building the Himalaya; Bird splits its eastern parts into the Amur, Okhotsk and Yangtze plates.", "Bird 2003; Wikipedia, Eurasian plate"),
    "AU": ("Moving north at seven centimetres a year, among the fastest of the large plates, and colliding with Eurasia and the Pacific along a line from Sumatra to New Zealand.", "Bird 2003; Wikipedia, Australian plate"),
    "SA": ("The Nazca plate dives beneath its western edge along the Peru-Chile trench, and the Andes stand on top of the subduction.", "Bird 2003; Wikipedia, South American plate"),
    "NZ": ("A piece of ocean floor between the East Pacific Rise and South America, being consumed under the Andes at eight centimetres a year, one of the fastest convergences there is.", "Bird 2003; Wikipedia, Nazca plate"),
    "IN": ("Broke away from Gondwana, crossed the Tethys Ocean at up to twenty centimetres a year, and hit Eurasia; still pushing north at five, which is why the Himalaya keep rising.", "Bird 2003; Wikipedia, Indian plate"),
    "AR": ("Splitting from Africa along the Red Sea, one of the youngest oceans, and pushing into Iran to raise the Zagros.", "Bird 2003; Wikipedia, Arabian plate"),
    "CO": ("A small oceanic plate diving under Central America and making its volcanoes.", "Bird 2003; Wikipedia, Cocos plate"),
    "JF": ("The remnant of a plate that once filled the eastern Pacific, now a small slab going under Oregon and Washington and feeding the Cascade volcanoes.", "Bird 2003; Wikipedia, Juan de Fuca plate"),
    "PS": ("A plate of ocean floor with a trench on almost every side, including the Mariana Trench, the deepest place on the Earth, where the Pacific goes under it.", "Bird 2003; Wikipedia, Philippine Sea plate"),
    "CA": ("A plate of ocean floor and islands squeezed between the Americas, with the Lesser Antilles volcanoes along the trench on its eastern side.", "Bird 2003; Wikipedia, Caribbean plate"),
    "SC": ("A small plate at the tip of South America, drawn out by the trench on its eastern side and carrying the South Sandwich Islands.", "Bird 2003; Wikipedia, Scotia plate"),
    "SO": ("The eastern part of Africa, separated from the rest along the East African Rift; the split is only a few million years old and the ocean that will fill it has not yet opened.", "Bird 2003; Wikipedia, Somali plate"),
}
GENERIC = ("One of the smaller plates in Bird's model, most of them slivers along the boundaries of the large ones where the motion does not fit a single rigid block.", "Bird 2003")

# places to jump to: k, name, lon, lat, a line, source
PLACES = [
    ("atlantic", "the Mid-Atlantic Ridge", -45.1, 15.3, "The seam down the middle of the Atlantic, where the ocean has been opening at about two and a half centimetres a year for 180 million years. Iceland is the ridge above water.", "Wikipedia, Mid-Atlantic Ridge"),
    ("epr", "the East Pacific Rise", -113.6, -19.8, "The fastest spreading ridge, opening at up to fifteen centimetres a year, making the Pacific and Nazca plates.", "Wikipedia, East Pacific Rise"),
    ("andes", "the Peru-Chile Trench", -73, -22, "The Nazca plate going under South America. The Andes, the Atacama and the largest earthquake ever recorded, Valdivia in 1960, are all this boundary.", "Wikipedia, Peru-Chile Trench"),
    ("japan", "the Japan Trench", 143, 38, "The Pacific plate diving under Japan at eight centimetres a year. The 2011 earthquake moved the sea floor fifty metres in minutes.", "Wikipedia, Japan Trench"),
    ("mariana", "the Mariana Trench", 143, 12, "The Pacific plate going under the Philippine Sea plate, the oldest and coldest ocean floor on the planet sinking into the deepest trench.", "Wikipedia, Mariana Trench"),
    ("andreas", "the San Andreas Fault", -122.4, 37.6, "The Pacific and North American plates sliding past each other at four and a half centimetres a year. Los Angeles and San Francisco are on opposite sides.", "Wikipedia, San Andreas Fault"),
    ("himalaya", "the Himalaya", 84, 28, "India driving into Eurasia. The crust here is twice its normal thickness, and the mountains rise about half a centimetre a year, worn down nearly as fast.", "Wikipedia, Himalayas"),
    ("rift", "the East African Rift", 36, 0, "Africa splitting in two from the Afar triangle to Mozambique: a valley with volcanoes and lakes along it, and a new plate boundary a few million years old.", "Wikipedia, East African Rift"),
    ("redsea", "the Red Sea", 38, 20, "An ocean at birth: Arabia and Africa parted along it about thirty million years ago and it has been widening at a centimetre a year since.", "Wikipedia, Red Sea Rift"),
    ("iceland", "Iceland", -19, 65, "The Mid-Atlantic Ridge above sea level, with a hot spot underneath; the island grows two centimetres wider a year.", "Wikipedia, Iceland hotspot"),
]

REFS = [
    (apa.article("Bird, P.", 2003, "An updated digital model of plate boundaries",
                 "Geochemistry, Geophysics, Geosystems", 4, 3, "1027", "https://doi.org/10.1029/2001GC000252"),
     "PB2002: the 52 plates, their boundaries in 5,824 steps, each classed and given a relative velocity."),
    (apa.web("Ahlenius, H.", 2014, "Tectonic plates: PB2002 boundaries, plates and orogens as GeoJSON", "GitHub, fraxen/tectonicplates",
             "https://github.com/fraxen/tectonicplates"),
     "The digitised model as it is read here."),
    (apa.article("DeMets, C., Gordon, R. G., Argus, D. F., &amp; Stein, S.", 1994,
                 "Effect of recent revisions to the geomagnetic reversal time scale on estimates of current plate motions",
                 "Geophysical Research Letters", 21, 20, "2191-2194", "https://doi.org/10.1029/94GL02118"),
     "NUVEL-1A, the velocities Bird's model rests on for the large plates."),
    (apa.article("Wessel, P., &amp; Smith, W. H. F.", 1996, "A global, self-consistent, hierarchical, high-resolution shoreline database",
                 "Journal of Geophysical Research: Solid Earth", 101, "B4", "8741-8743", "https://doi.org/10.1029/96JB00104"),
     "The coastlines, as rasterised for this site's Climate page."),
]
REFS += [(apa.wiki(f"https://en.wikipedia.org/wiki/{p}"), a) for p, a in [
    ("Plate_tectonics", "The theory, and the kinds of boundary."),
    ("List_of_tectonic_plates", "The plates by area, for comparison."),
    ("Pacific_plate", None), ("African_plate", None), ("Antarctic_plate", None), ("North_American_plate", None),
    ("Eurasian_plate", None), ("Australian_plate", None), ("South_American_plate", None), ("Nazca_plate", None),
    ("Indian_plate", None), ("Arabian_plate", None), ("Cocos_plate", None), ("Juan_de_Fuca_plate", None),
    ("Philippine_Sea_plate", None), ("Caribbean_plate", None), ("Scotia_plate", None), ("Somali_plate", None),
    ("Mid-Atlantic_Ridge", None), ("East_Pacific_Rise", None), ("Peru%E2%80%93Chile_Trench", None), ("Japan_Trench", None),
    ("Mariana_Trench", None), ("San_Andreas_Fault", None), ("Himalayas", None), ("East_African_Rift", None),
    ("Red_Sea_Rift", None), ("Iceland_hotspot", None),
]]
