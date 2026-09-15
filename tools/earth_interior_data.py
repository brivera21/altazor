#!/usr/bin/env python3
"""The data behind earth-interior.html: the Preliminary Reference Earth Model
of Dziewonski and Anderson (1981), a geotherm, the layers and some places.

PREM gives density and the two seismic wave speeds as polynomials in
r/6371 km over each shell; mass, gravity and pressure follow from the
density by integration. Temperatures are not part of PREM and come from
Katsura (2022) for the mantle adiabat and Anzellini et al. (2013) for the
inner core boundary, with the core-mantle boundary from the Wikipedia
article; they are uncertain by hundreds of kelvin.
"""

import apa

R_EARTH = 6371.0   # km

# PREM, isotropic: (inner radius km, outer radius km, [a, b, c, d]) with
# value = a + b x + c x^2 + d x^3, x = r / 6371. Density in g/cm^3, speeds in km/s.
PREM_RHO = [
    (0, 1221.5, [13.0885, 0, -8.8381, 0]),
    (1221.5, 3480, [12.5815, -1.2638, -3.6426, -5.5281]),
    (3480, 5701, [7.9565, -6.4761, 5.5283, -3.0807]),
    (5701, 5771, [5.3197, -1.4836, 0, 0]),
    (5771, 5971, [11.2494, -8.0298, 0, 0]),
    (5971, 6151, [7.1089, -3.8045, 0, 0]),
    (6151, 6346.6, [2.6910, 0.6924, 0, 0]),
    (6346.6, 6356, [2.900, 0, 0, 0]),
    (6356, 6368, [2.600, 0, 0, 0]),
    (6368, 6371, [1.020, 0, 0, 0]),
]
PREM_VP = [
    (0, 1221.5, [11.2622, 0, -6.3640, 0]),
    (1221.5, 3480, [11.0487, -4.0362, 4.8023, -13.5732]),
    (3480, 3630, [15.3891, -5.3181, 5.5242, -2.5514]),
    (3630, 5600, [24.9520, -40.4673, 51.4832, -26.6419]),
    (5600, 5701, [29.2766, -23.6027, 5.5242, -2.5514]),
    (5701, 5771, [19.0957, -9.8672, 0, 0]),
    (5771, 5971, [39.7027, -32.6166, 0, 0]),
    (5971, 6151, [20.3926, -12.2569, 0, 0]),
    (6151, 6346.6, [4.1875, 3.9382, 0, 0]),
    (6346.6, 6356, [6.800, 0, 0, 0]),
    (6356, 6368, [5.800, 0, 0, 0]),
    (6368, 6371, [1.450, 0, 0, 0]),
]
PREM_VS = [
    (0, 1221.5, [3.6678, 0, -4.4475, 0]),
    (1221.5, 3480, [0, 0, 0, 0]),
    (3480, 3630, [6.9254, 1.4672, -2.0834, 0.9783]),
    (3630, 5600, [11.1671, -13.7818, 17.4575, -9.2777]),
    (5600, 5701, [22.3459, -17.2473, -2.0834, 0.9783]),
    (5701, 5771, [9.9839, -4.9324, 0, 0]),
    (5771, 5971, [22.3512, -18.5856, 0, 0]),
    (5971, 6151, [8.9496, -4.4597, 0, 0]),
    (6151, 6346.6, [2.1519, 2.3481, 0, 0]),
    (6346.6, 6356, [3.900, 0, 0, 0]),
    (6356, 6368, [3.200, 0, 0, 0]),
    (6368, 6371, [0, 0, 0, 0]),
]

# a geotherm, depth km to kelvin, joined by straight lines; the mantle
# points are Katsura's adiabat, the inner core boundary is Anzellini's
GEOTHERM = [
    (0, 288), (24.4, 800), (100, 1550), (220, 1720), (400, 1839), (670, 1994),
    (671, 1960), (2741, 2580), (2891, 4000), (2892, 4100), (5149.5, 6230), (6371, 6300),
]

# the layers, by depth (km): k, name, top, bottom, color, state, what it is, a line, source
LAYERS = [
    ("crust", "the crust", 0, 24.4, "#9be564", "solid rock",
     "granite and basalt, with PREM's 3 km ocean on top",
     "Thinner on the Earth than the skin on an apple: 7 km under the oceans, 35 under the continents, 24 in this average model. Everything ever dug or drilled is in the top half of it.",
     "PREM; Wikipedia, Crust (geology)"),
    ("upper", "the upper mantle", 24.4, 400, "#e0a458", "solid, and slowly flowing",
     "peridotite: olivine and pyroxene",
     "Rock hot enough to creep over millions of years, which is what moves the plates. The top 80 km or so is stiff and rides along with the crust as the lithosphere; below it a softer zone lets the plates slide.",
     "PREM; Wikipedia, Upper mantle"),
    ("transition", "the transition zone", 400, 670, "#f2c94c", "solid",
     "olivine squeezed into denser crystal forms",
     "Two jumps in density and wave speed, at 410 and 660 km, where the pressure forces olivine into new, tighter structures. The deepest earthquakes stop here.",
     "PREM; Wikipedia, Transition zone (Earth)"),
    ("lower", "the lower mantle", 670, 2741, "#d9822b", "solid, and slowly flowing",
     "bridgmanite and ferropericlase",
     "More than half of the Earth by volume, made largely of a mineral, bridgmanite, that exists nowhere at the surface. Density climbs from 4.4 to 5.5 g per cubic centimeter across it.",
     "PREM; Wikipedia, Lower mantle"),
    ("dpp", "the D&Prime; layer", 2741, 2891, "#b55d2a", "solid, uneven",
     "the bottom 150 km of the mantle",
     "A lumpy boundary layer against the core, with temperature rising by something like a thousand kelvin across it, continent-sized piles of dense rock, and the roots of mantle plumes.",
     "PREM; Wikipedia, D″ layer"),
    ("outer", "the outer core", 2891, 5149.5, "#f28cb0", "liquid metal",
     "iron and nickel with some lighter elements",
     "Molten iron, as hot as the surface of the Sun, stirred by heat and by the settling of the inner core. Its currents make the magnetic field. Shear waves cannot cross it: Oldham found the core in 1906 and Jeffreys showed it liquid in 1926.",
     "PREM; Wikipedia, Earth's outer core"),
    ("inner", "the inner core", 5149.5, 6371, "#f4efe2", "solid metal",
     "iron-nickel crystal",
     "Solid because the pressure of 330 gigapascals raises iron's melting point above the temperature there. It grows a millimeter a year as the core cools, and was found by Inge Lehmann in 1936.",
     "PREM; Wikipedia, Earth's inner core"),
]

# places at a depth: k, name, depth km, a line, source
PLACES = [
    ("mine", "the deepest mine", 4.0, "Mponeng, in South Africa, 4 km down, where the rock face is 66 degrees Celsius and has to be cooled with ice.", "Wikipedia, Mponeng Gold Mine"),
    ("trench", "the deepest ocean", 10.9, "The Challenger Deep in the Mariana Trench, 10.9 km below the surface, under 1,100 atmospheres of water.", "Wikipedia, Challenger Deep"),
    ("kola", "the deepest hole", 12.3, "The Kola Superdeep Borehole, 12.3 km, drilled over twenty years and stopped by rock at 180 degrees Celsius. A fifth of the way through the crust.", "Wikipedia, Kola Superdeep Borehole"),
    ("moho", "the Moho", 24.4, "The base of the crust, where wave speed jumps to 8 km per second; found by Mohorovičić in 1909 from earthquake arrivals.", "Wikipedia, Mohorovičić discontinuity"),
    ("diamond", "where diamonds form", 175, "Most diamonds crystallize between 150 and 200 km down, in the roots of old continents, and ride up in volcanic eruptions.", "Wikipedia, Diamond"),
    ("quake", "the deepest earthquakes", 700, "Earthquakes stop at about 700 km, where the sinking slabs reach the bottom of the transition zone.", "Wikipedia, Deep-focus earthquake"),
    ("cmb", "the core-mantle boundary", 2891, "The sharpest boundary inside the planet: rock above, liquid metal below, density nearly doubling in a step.", "PREM"),
    ("icb", "the inner core boundary", 5149.5, "Where the iron freezes. The solid inner core grows outward from here as the planet cools.", "PREM; Anzellini et al. 2013"),
    ("center", "the center", 6371, "364 gigapascals, 3.6 million atmospheres, and gravity at zero: every direction is up.", "PREM"),
]

REFS = [
    (apa.article("Dziewonski, A. M., &amp; Anderson, D. L.", 1981, "Preliminary reference Earth model",
                 "Physics of the Earth and Planetary Interiors", 25, 4, "297-356", "https://doi.org/10.1016/0031-9201(81)90046-7"),
     "PREM: the density and wave-speed polynomials, and the depths of the boundaries, from which mass, gravity and pressure are integrated here."),
    (apa.article("Katsura, T.", 2022, "A revised adiabatic temperature profile for the mantle",
                 "Journal of Geophysical Research: Solid Earth", 127, None, "e2021JB023562", "https://doi.org/10.1029/2021JB023562"),
     "The mantle temperatures: 1839 K at 410 km, 1994 K above 660, 2587 K at 2800 km."),
    (apa.article("Anzellini, S., Dewaele, A., Mezouar, M., Loubeyre, P., &amp; Morard, G.", 2013,
                 "Melting of iron at Earth's inner core boundary based on fast X-ray diffraction",
                 "Science", 340, 6131, "464-466", "https://doi.org/10.1126/science.1233514"),
     "The inner core boundary at 6230 &plusmn; 500 K."),
]
REFS += [(apa.wiki(f"https://en.wikipedia.org/wiki/{p}"), a) for p, a in [
    ("Structure_of_Earth", "The layers and their states."),
    ("Core%E2%80%93mantle_boundary", "About 4,000 K at the top of the core."),
    ("Crust_(geology)", None), ("Upper_mantle", None), ("Transition_zone_(Earth)", None), ("Lower_mantle", None),
    ("D%E2%80%B3_layer", None), ("Earth%27s_outer_core", None), ("Earth%27s_inner_core", None),
    ("Mponeng_Gold_Mine", None), ("Challenger_Deep", None), ("Kola_Superdeep_Borehole", None),
    ("Mohorovi%C4%8Di%C4%87_discontinuity", None), ("Diamond", None), ("Deep-focus_earthquake", None),
]]
