#!/usr/bin/env python3
"""The words behind plates.html. The geometry is tools/data/plates.json,
made by tools/make_plates.py from Bird's PB2002 model.

Plate areas are measured from the model's polygons on a 1/6 degree grid and
agree with Bird's table to a fraction of a percent. Relative velocities along
the boundaries are Bird's, from NUVEL-1A and later local models.
"""

import apa

# the kinds of boundary, in the order of the data file's class codes
# code, name, color, a line
CLASSES = [
    ("OSR", "a spreading ridge", "#f28cb0", "Two plates pulling apart under the ocean. Mantle rises to fill the gap, melts, and freezes into new sea floor; the ridge stands high because the young rock is hot."),
    ("CRB", "a continental rift", "#f2a0c0", "A continent being pulled apart: a valley with faults on both sides and volcanoes down the middle. Given time it becomes a spreading ridge with an ocean in it."),
    ("SUB", "a subduction zone", "#58a6ff", "One plate dives beneath another and sinks into the mantle, bending down along a trench. The deepest earthquakes, the biggest ones, and most of the volcanoes on land are here."),
    ("OTF", "an oceanic transform", "#ffb02e", "Two plates sliding past each other, offsetting a ridge. No crust is made or lost; the fault is a strike-slip seam across the sea floor."),
    ("CTF", "a continental transform", "#ffc85e", "Two plates sliding past each other on land: the San Andreas, the Alpine Fault, the North Anatolian. Shallow earthquakes, no volcanoes."),
    ("CCB", "a continental collision", "#9ec5ff", "Two continents meeting. Neither will sink, so the crust crumples and thickens into mountains: the Himalaya, the Alps, the Zagros."),
    ("OCB", "an oceanic convergence", "#3d7bd6", "Convergence with no clear trench, where the crust shortens and thickens without one plate diving cleanly under the other."),
]

# plates with something to say: code, a line, source
NOTES = {
    "PA": ("The largest plate, all ocean, and shrinking: trenches ring it on the north and west, and it is heading northwest at about seven centimeters a year, leaving the Hawaiian chain behind it as it passes over a hot spot.", "Bird 2003; Wikipedia, Pacific plate"),
    "AF": ("Africa in the middle, ridges on three sides, so the plate is growing at its edges and moving slowly. The East African Rift is tearing the Somali side off it.", "Bird 2003; Wikipedia, African plate"),
    "AN": ("Ringed almost entirely by spreading ridges, with no trench, so the plate hardly moves and grows on every side.", "Bird 2003; Wikipedia, Antarctic plate"),
    "NA": ("The Atlantic half is growing at the Mid-Atlantic Ridge; the Pacific edge slides past the Pacific plate along the San Andreas and dives under it in Alaska.", "Bird 2003; Wikipedia, North American plate"),
    "EU": ("From the Mid-Atlantic Ridge to Japan. India has been pushing into its southern edge for fifty million years, building the Himalaya; Bird splits its eastern parts into the Amur, Okhotsk and Yangtze plates.", "Bird 2003; Wikipedia, Eurasian plate"),
    "AU": ("Moving north at seven centimeters a year, among the fastest of the large plates, and colliding with Eurasia and the Pacific along a line from Sumatra to New Zealand.", "Bird 2003; Wikipedia, Australian plate"),
    "SA": ("The Nazca plate dives beneath its western edge along the Peru-Chile trench, and the Andes stand on top of the subduction.", "Bird 2003; Wikipedia, South American plate"),
    "NZ": ("A piece of ocean floor between the East Pacific Rise and South America, being consumed under the Andes at eight centimeters a year, one of the fastest convergences there is.", "Bird 2003; Wikipedia, Nazca plate"),
    "IN": ("Broke away from Gondwana, crossed the Tethys Ocean at up to twenty centimeters a year, and hit Eurasia; still pushing north at five, which is why the Himalaya keep rising.", "Bird 2003; Wikipedia, Indian plate"),
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
    ("atlantic", "the Mid-Atlantic Ridge", -45.1, 15.3, "The seam down the middle of the Atlantic, where the ocean has been opening at about two and a half centimeters a year for 180 million years. Iceland is the ridge above water.", "Wikipedia, Mid-Atlantic Ridge"),
    ("epr", "the East Pacific Rise", -113.6, -19.8, "The fastest spreading ridge, opening at up to fifteen centimeters a year, making the Pacific and Nazca plates.", "Wikipedia, East Pacific Rise"),
    ("andes", "the Peru-Chile Trench", -73, -22, "The Nazca plate going under South America. The Andes, the Atacama and the largest earthquake ever recorded, Valdivia in 1960, are all this boundary.", "Wikipedia, Peru-Chile Trench"),
    ("japan", "the Japan Trench", 143, 38, "The Pacific plate diving under Japan at eight centimeters a year. The 2011 earthquake moved the sea floor fifty meters in minutes.", "Wikipedia, Japan Trench"),
    ("mariana", "the Mariana Trench", 143, 12, "The Pacific plate going under the Philippine Sea plate, the oldest and coldest ocean floor on the planet sinking into the deepest trench.", "Wikipedia, Mariana Trench"),
    ("andreas", "the San Andreas Fault", -122.4, 37.6, "The Pacific and North American plates sliding past each other at four and a half centimeters a year. Los Angeles and San Francisco are on opposite sides.", "Wikipedia, San Andreas Fault"),
    ("himalaya", "the Himalaya", 84, 28, "India driving into Eurasia. The crust here is twice its normal thickness, and the mountains rise about half a centimeter a year, worn down nearly as fast.", "Wikipedia, Himalayas"),
    ("rift", "the East African Rift", 36, 0, "Africa splitting in two from the Afar triangle to Mozambique: a valley with volcanoes and lakes along it, and a new plate boundary a few million years old.", "Wikipedia, East African Rift"),
    ("redsea", "the Red Sea", 38, 20, "An ocean at birth: Arabia and Africa parted along it about thirty million years ago and it has been widening at a centimeter a year since.", "Wikipedia, Red Sea Rift"),
    ("iceland", "Iceland", -19, 65, "The Mid-Atlantic Ridge above sea level, with a hot spot underneath; the island grows two centimeters wider a year.", "Wikipedia, Iceland hotspot"),
]

REFS = [
    (apa.article("Bird, P.", 2003, "An updated digital model of plate boundaries",
                 "Geochemistry, Geophysics, Geosystems", 4, 3, "1027", "https://doi.org/10.1029/2001GC000252"),
     "PB2002: the 52 plates, their boundaries in 5,824 steps, each classed and given a relative velocity."),
    (apa.web("Ahlenius, H.", 2014, "Tectonic plates: PB2002 boundaries, plates and orogens as GeoJSON", "GitHub, fraxen/tectonicplates",
             "https://github.com/fraxen/tectonicplates"),
     "The digitized model as it is read here."),
    (apa.article("DeMets, C., Gordon, R. G., Argus, D. F., &amp; Stein, S.", 1994,
                 "Effect of recent revisions to the geomagnetic reversal time scale on estimates of current plate motions",
                 "Geophysical Research Letters", 21, 20, "2191-2194", "https://doi.org/10.1029/94GL02118"),
     "NUVEL-1A, the velocities Bird's model rests on for the large plates."),
    (apa.article("Wessel, P., &amp; Smith, W. H. F.", 1996, "A global, self-consistent, hierarchical, high-resolution shoreline database",
                 "Journal of Geophysical Research: Solid Earth", 101, "B4", "8741-8743", "https://doi.org/10.1029/96JB00104"),
     "The coastlines, as rasterized for this site's Climate page."),
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

# Where each plate is heading: NNR-MORVEL56 angular velocities in the
# no-net-rotation frame (Argus, Gordon and DeMets 2011, Table S4): pole
# latitude and longitude in degrees, rate in degrees per million years.
# MORVEL's Nubia stands for Bird's Africa, Somalia for Somalia and Yangtze
# for Yangtze; Bird's other plates carry his own poles, as in the table.
POLES = {
    "PA": (-63.5756, 114.6975, 0.6509), "AM": (63.1704, -122.8242, 0.2973),
    "AN": (65.4235, -118.1053, 0.2500), "AR": (48.8807, -8.4909, 0.5588),
    "AU": (33.8612, 37.9414, 0.6316), "CA": (35.1956, -92.6236, 0.2862),
    "CO": (26.9346, -124.3074, 1.1978), "EU": (48.8509, -106.5007, 0.2227),
    "IN": (50.3722, -3.2898, 0.5438), "JF": (-38.3086, 60.0379, 0.9513),
    "AF": (47.6763, -68.4377, 0.2921), "NA": (-4.8548, -80.6447, 0.2087),
    "NZ": (46.2348, -101.0564, 0.6957), "PS": (-46.0242, -31.3615, 0.9098),
    "RI": (20.2450, -107.2861, 4.5359), "SA": (-22.6179, -112.8327, 0.1090),
    "SC": (22.5244, -106.1485, 0.1464), "SO": (49.9506, -84.5154, 0.3393),
    "SU": (50.0558, -95.0218, 0.3368), "SW": (-29.9420, -36.8671, 1.3616),
    "YA": (63.0285, -116.6180, 0.3335), "SL": (50.7058, -143.4675, 0.2677),
    "BH": (-39.9983, 100.4994, 0.7988), "MO": (14.2480, 92.6656, 0.7742),
    "SS": (-2.8685, 130.6236, 1.7029), "WL": (0.1050, 128.5186, 1.7444),
    "CR": (-20.3985, 170.5303, 3.9232), "FT": (-16.3322, 178.0679, 5.1006),
    "KE": (39.9929, 6.4584, 2.3474), "NI": (-3.2883, -174.4882, 3.3136),
    "TO": (25.8737, 4.4767, 8.9417), "PM": (31.3510, -113.9038, 0.3171),
    "AS": (19.4251, 122.8665, 0.1239), "AT": (40.1121, 26.6585, 1.2105),
    "GP": (2.5287, 81.1806, 5.4868), "EA": (24.9729, 67.5269, 11.3343),
    "JZ": (34.2507, 70.7429, 22.3676), "OK": (30.3022, -92.2813, 0.2290),
    "NB": (-45.0406, 127.6370, 0.8563), "SB": (6.8767, -31.8883, 8.1107),
    "MN": (-3.6699, 150.2676, 51.5690), "NH": (0.5684, -6.6018, 2.4688),
    "BR": (-63.7420, 142.0636, 0.4898), "CL": (-72.7849, 72.0525, 0.6066),
    "MA": (11.0533, 137.8404, 1.3061), "ND": (17.7331, -122.6815, 0.1162),
    "AP": (-6.5763, -83.9776, 0.4881), "BU": (-6.1254, -78.1008, 2.2287),
    "MS": (2.1477, -56.0916, 3.5655), "BS": (-1.4855, 121.6413, 2.4753),
    "TI": (-4.4363, 113.4976, 1.8639), "ON": (36.1163, 137.9182, 2.5391),
}
POLES_REF = (apa.article("Argus, D. F., Gordon, R. G., &amp; DeMets, C.", 2011,
                         "Geologically current motion of 56 plates relative to the no-net-rotation reference frame",
                         "Geochemistry, Geophysics, Geosystems", 12, 11, "Q11001", "https://doi.org/10.1029/2011GC003751"),
             "Where each plate is heading and how fast: the NNR-MORVEL56 angular velocities, Table S4, behind the arrows and the run forward.")
