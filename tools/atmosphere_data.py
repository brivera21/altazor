#!/usr/bin/env python3
"""The data behind atmosphere.html: the US Standard Atmosphere of 1976 up to
86 km, tabulated anchors above it, the layers, the marks up the column, and
what the air is made of.

The standard atmosphere is a set of seven layers with a linear temperature
lapse in each; pressure follows by hydrostatics. Above 86 km the model's
tables are used at a few anchors and interpolated in the log. The
composition is CIPM-2007 dry air with carbon dioxide at its 2024 Mauna Loa mean.
"""

import apa

# US Standard Atmosphere 1976: base geopotential height (km), base temperature
# (K), lapse rate (K per km) for each layer up to 86 km; the base pressure is
# derived. Sea level pressure 101325 Pa.
LAYERS_76 = [
    (0.0, 288.15, -6.5),
    (11.0, 216.65, 0.0),
    (20.0, 216.65, 1.0),
    (32.0, 228.65, 2.8),
    (47.0, 270.65, 0.0),
    (51.0, 270.65, -2.8),
    (71.0, 214.65, -2.0),
    (84.852, 186.946, 0.0),
]
P0, G0, R_AIR, M_AIR, R_GAS = 101325.0, 9.80665, 287.05287, 28.9644e-3, 8.31432

# above 86 km: geometric altitude km, temperature K, pressure Pa, density kg/m3,
# mean molecular mass g/mol, from the 1976 tables (rounded)
UPPER = [
    (86, 186.9, 3.73e-1, 6.96e-6, 28.95),
    (100, 195.1, 3.20e-2, 5.60e-7, 28.40),
    (120, 360.0, 2.54e-3, 2.22e-8, 26.20),
    (150, 634.4, 4.54e-4, 2.08e-9, 24.10),
    (200, 854.6, 8.47e-5, 2.54e-10, 21.30),
    (300, 976.0, 8.77e-6, 1.92e-11, 17.73),
    (400, 995.8, 1.45e-6, 2.80e-12, 15.98),
    (500, 999.2, 3.02e-7, 5.22e-13, 14.33),
    (600, 999.9, 8.21e-8, 1.14e-13, 11.51),
]

# the layers of the air: k, name, from km, to km, colour, a line
LAYERS = [
    ("tropo", "the troposphere", 0, 11, "#58a6ff", "All the weather, three quarters of the air and nearly all the water vapour. Warmed from below, so it cools with height, six and a half degrees a kilometre, and convects. The top is higher at the equator, 17 km, and lower at the poles, 9."),
    ("strato", "the stratosphere", 11, 47, "#9be564", "Warms with height because ozone here absorbs the Sun's ultraviolet, so it does not convect: the air is layered and still, which is why airliners cruise at its bottom edge. The ozone layer peaks around 25 km."),
    ("meso", "the mesosphere", 47, 86, "#ffb02e", "Cools with height again to the coldest air on the planet, about minus 90 degrees at its top. Meteors burn up here, and the highest clouds, noctilucent, form at 80 km from ice on meteor dust."),
    ("thermo", "the thermosphere", 86, 600, "#f28cb0", "The Sun's far ultraviolet and X-rays are absorbed here and the thin gas heats to a thousand kelvin, though it would not feel warm: there are too few molecules to carry heat. The aurora, the ionosphere and the space station are all in it."),
]

# marks up the column: k, name, altitude km, a line, source
MARKS = [
    ("burj", "the Burj Khalifa", 0.83, "The tallest building, 830 m. The air at the top is 8% thinner than at the door.", "Wikipedia, Burj Khalifa"),
    ("lapaz", "La Paz", 3.64, "The highest seat of government, where the pressure is two thirds of sea level and visitors gasp on the stairs for a week.", "Wikipedia, La Paz"),
    ("everest", "the summit of Everest", 8.85, "A third of the sea-level pressure; the highest a person can climb, and only just. Above 8,000 m the body dies faster than it acclimatises.", "Wikipedia, Mount Everest"),
    ("airliner", "an airliner cruising", 11, "At the top of the troposphere, in still, cold air at minus 56 degrees, with a quarter of the pressure outside the window.", "Wikipedia, Cruise (aeronautics)"),
    ("vulture", "the highest bird", 11.3, "A Rüppell's vulture struck an aircraft at 11,300 m in 1973, the highest any bird has been found.", "Wikipedia, Rüppell's vulture"),
    ("armstrong", "the Armstrong limit", 19, "Where the pressure falls to 6.3 kPa and water boils at body temperature. Above this a person needs a pressure suit, not just oxygen.", "Wikipedia, Armstrong limit"),
    ("ozone", "the ozone layer", 25, "Ozone is thickest here, a few parts per million, enough to stop the ultraviolet that would otherwise sterilise the surface.", "Wikipedia, Ozone layer"),
    ("balloon", "a weather balloon bursting", 35, "Twice a day from hundreds of stations, a balloon rises until it swells to the size of a house and bursts, around 35 km.", "Wikipedia, Weather balloon"),
    ("jump", "Baumgartner's jump", 39, "The highest parachute jump from a balloon, in 2012, from 39 km; he broke the sound barrier on the way down.", "Wikipedia, Red Bull Stratos"),
    ("stratopause", "the stratopause", 47, "The warm top of the stratosphere, about minus 3 degrees, heated by ozone from below and the Sun above.", "US Standard Atmosphere 1976"),
    ("noctilucent", "noctilucent clouds", 83, "The highest clouds, ice on meteor dust in the coldest air there is, seen glowing after sunset in summer at high latitudes.", "Wikipedia, Noctilucent cloud"),
    ("meteor", "a meteor burning up", 90, "Shooting stars flare between 75 and 120 km, where the air first becomes thick enough to heat a grain of dust to incandescence.", "Wikipedia, Meteor"),
    ("karman", "the Kármán line", 100, "The conventional edge of space: above this the air is too thin for wings to lift at any speed below orbital.", "Wikipedia, Kármán line"),
    ("aurora", "the aurora", 110, "The green of the aurora is oxygen glowing at 100 to 150 km, hit by electrons coming down the magnetic field; the red is higher, at 200 to 300.", "Wikipedia, Aurora"),
    ("iss", "the space station", 420, "Still inside the atmosphere: the thin air at 400 km drags the station down two kilometres a month, and it has to be boosted.", "Wikipedia, International Space Station"),
    ("hubble", "the Hubble telescope", 540, "High enough to stay up for decades; low enough that the drag finally brings it down in the 2030s.", "Wikipedia, Hubble Space Telescope"),
]

# dry air by volume, CIPM-2007 with CO2 at the 2024 Mauna Loa mean: name, formula, fraction, a line
GASES = [
    ("nitrogen", "N₂", 0.78084, "Nearly inert, the bulk of the air, and the reason air is not explosive. Bacteria and lightning are what turn it into something a plant can use."),
    ("oxygen", "O₂", 0.20946, "Put there by photosynthesis over two billion years. Every fire, engine and animal spends it; plants and plankton replace it."),
    ("argon", "Ar", 0.00934, "Almost one percent, and nobody notices: a noble gas, born of potassium decaying in the rocks and leaking out over the ages."),
    ("carbon dioxide", "CO₂", 0.000425, "Four hundred and twenty-five parts per million at Mauna Loa in 2024, up from 280 before coal, and the reason the planet is warming. Plants are built from it."),
    ("neon", "Ne", 18.18e-6, "Eighteen parts per million; a glass tube of it glows red-orange."),
    ("helium", "He", 5.24e-6, "Five parts per million, so light it escapes to space; the helium in balloons is mined from natural gas instead."),
    ("methane", "CH₄", 1.9e-6, "Two parts per million, from wetlands, cattle, rice and leaks, and thirty times as warming as carbon dioxide, molecule for molecule."),
    ("krypton", "Kr", 1.14e-6, "A part per million; the metre was once defined by its light."),
    ("hydrogen", "H₂", 0.5e-6, "Half a part per million, escaping to space as fast as it is made."),
]
WATER = ("water vapour", "H₂O", 0.0025, "Not counted in dry air because it varies from almost none over a desert to four percent in the tropics; a quarter of a percent of the air by mass on average, and the source of every cloud, all the rain, and most of the greenhouse effect.")

# the column: total mass and where it sits
COLUMN = {
    "mass": 5.148e18, "water": 1.27e16,
    "note": "Five million billion tonnes, ten tonnes over every square metre; half of it below 5.5 km, ninety percent below 16, all but a millionth below 100.",
}

REFS = [
    (apa.web("National Oceanic and Atmospheric Administration, National Aeronautics and Space Administration, &amp; United States Air Force", 1976,
             "U.S. Standard Atmosphere, 1976", "NOAA-S/T 76-1562, U.S. Government Printing Office", "https://ntrs.nasa.gov/citations/19770009539"),
     "The temperature layers to 86 km and the tables above."),
    (apa.article("Trenberth, K. E., &amp; Smith, L.", 2005, "The mass of the atmosphere: A constraint on global analyses",
                 "Journal of Climate", 18, 6, "864-875", "https://doi.org/10.1175/JCLI-3299.1"),
     "The mass of the air, 5.148 &times; 10<sup>18</sup> kg, and of the water in it."),
    (apa.article("Picard, A., Davis, R. S., Gl&auml;ser, M., &amp; Fujii, K.", 2008, "Revised formula for the density of moist air (CIPM-2007)",
                 "Metrologia", 45, 2, "149-155", "https://doi.org/10.1088/0026-1394/45/2/004"),
     "The composition of dry air."),
    (apa.web("Lan, X., Tans, P., &amp; Thoning, K. W.", "n.d.", "Trends in atmospheric carbon dioxide (Mauna Loa)",
             "NOAA Global Monitoring Laboratory", "https://gml.noaa.gov/ccgg/trends/", retrieved=True),
     "Carbon dioxide at 425 parts per million, the 2024 annual mean at Mauna Loa."),
]
REFS += [(apa.wiki(f"https://en.wikipedia.org/wiki/{p}"), a) for p, a in [
    ("Atmosphere_of_Earth", "The layers and the composition."),
    ("Barometric_formula", "Pressure from the lapse rates."),
    ("Burj_Khalifa", None), ("La_Paz", None), ("Mount_Everest", None), ("Cruise_(aeronautics)", None),
    ("R%C3%BCppell%27s_vulture", None), ("Armstrong_limit", None), ("Ozone_layer", None), ("Weather_balloon", None),
    ("Red_Bull_Stratos", None), ("Noctilucent_cloud", None), ("Meteor", None), ("K%C3%A1rm%C3%A1n_line", None),
    ("Aurora", None), ("International_Space_Station", None), ("Hubble_Space_Telescope", None),
]]
