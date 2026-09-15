#!/usr/bin/env python3
"""The data behind ocean.html: the surface currents as polylines, the five
gyres they make, and the great conveyor.

The current paths are drawn by hand from the standard maps and are
schematic: real currents meander, shed eddies and shift with the seasons.
Transports are in sverdrups, a million cubic meters a second, and are the
figures the cited articles give; where an article gives a range the range
is kept.
"""

import apa

# a current: k, name, warm or cold, points [(lon, lat), ...] in the direction of
# flow, gyre it belongs to (or None), transport (text, Sv), speed (text),
# a line, source
CURRENTS = [
    # the North Atlantic gyre, clockwise
    ("gulf", "the Gulf Stream", "warm", [(-81, 24.5), (-80, 28), (-78, 32), (-74, 35.5), (-68, 38), (-60, 40.5), (-50, 43)], "natl",
     "30 Sv through the Florida Strait, 150 Sv off Newfoundland", "up to 2.5 m/s",
     "The strongest current in the Atlantic, a river of warm water a hundred kilometers wide that leaves Florida at walking pace and carries more water than all the rivers of the world a hundred times over.", "Wikipedia, Gulf Stream"),
    ("nad", "the North Atlantic Drift", "warm", [(-50, 43), (-38, 47), (-25, 51), (-12, 55), (-2, 60), (8, 66), (14, 71)], "natl",
     "", "",
     "The Gulf Stream's continuation, spreading and slowing across the ocean and on past Norway. It keeps northwestern Europe ten degrees warmer in winter than its latitude deserves.", "Wikipedia, North Atlantic Current"),
    ("canary", "the Canary Current", "cold", [(-10, 42), (-12, 36), (-15, 30), (-18, 24), (-20, 18)], "natl",
     "", "",
     "The eastern side of the gyre, flowing south past Iberia and Morocco: cool water and upwelling, which is why the Canaries are mild and the fishing is rich.", "Wikipedia, Canary Current"),
    ("naeq", "the North Equatorial Current", "warm", [(-22, 14), (-32, 13), (-42, 12.5), (-52, 12), (-60, 12.5)], "natl",
     "", "",
     "The trade winds push the surface west along the tropics, and this is the water that crosses to the Caribbean and feeds the Gulf Stream.", "Wikipedia, North Equatorial Current"),
    ("carib", "the Caribbean and Loop Currents", "warm", [(-61, 13), (-68, 15), (-75, 16), (-82, 19), (-86, 22), (-87, 25.5), (-84, 25), (-81, 24.5)], "natl",
     "", "",
     "Through the Antilles, across the Caribbean, up into the Gulf of Mexico in a loop, and out through the Florida Strait as the Gulf Stream.", "Wikipedia, Loop Current"),
    ("labrador", "the Labrador Current", "cold", [(-57, 61), (-53, 56), (-50, 51), (-51, 47), (-54, 43)], None,
     "", "",
     "Cold water and icebergs from Baffin Bay flowing south past Newfoundland to meet the Gulf Stream, which is where the Titanic sank and the fog on the Grand Banks comes from.", "Wikipedia, Labrador Current"),
    # the South Atlantic gyre, counterclockwise
    ("brazil", "the Brazil Current", "warm", [(-34, -12), (-37, -20), (-42, -26), (-48, -32), (-53, -38)], "satl",
     "", "",
     "The South Atlantic's western boundary current, weaker than its northern twin, flowing south along Brazil to meet the cold Malvinas water off Argentina.", "Wikipedia, Brazil Current"),
    ("saeq", "the South Equatorial Current", "warm", [(2, -6), (-10, -8), (-20, -9), (-30, -9), (-34, -10)], "satl",
     "", "",
     "The trade-wind current of the southern tropics, flowing west to Brazil, where the coast splits it north and south.", "Wikipedia, South Equatorial Current"),
    ("benguela", "the Benguela Current", "cold", [(17, -34), (14, -28), (12, -22), (10, -16), (6, -10)], "satl",
     "", "",
     "Cold water flowing north along Namibia and Angola, with upwelling from below that makes the Namib coast foggy and the sea full of fish.", "Wikipedia, Benguela Current"),
    ("satlc", "the South Atlantic Current", "cold", [(-52, -42), (-38, -42), (-24, -41), (-8, -40), (8, -38)], "satl",
     "", "",
     "The southern side of the gyre, flowing east with the westerlies just north of the circumpolar current.", "Wikipedia, South Atlantic Current"),
    # the circumpolar current
    ("acc", "the Antarctic Circumpolar Current", "cold", [(-180, -56), (-150, -58), (-120, -60), (-90, -60), (-65, -58), (-40, -54), (-10, -52), (20, -52), (50, -54), (80, -56), (110, -58), (140, -60), (170, -60), (180, -58)], None,
     "about 135 Sv through the Drake Passage, 147 south of Tasmania", "",
     "The only current that goes all the way round the world, driven by the westerlies with no land to stop it. It carries more water than any other, and it walls the Antarctic off from warmer seas.", "Wikipedia, Antarctic Circumpolar Current"),
    # the Indian Ocean gyre, counterclockwise
    ("agulhas", "the Agulhas Current", "warm", [(38, -23), (35.5, -28), (31, -33), (26, -36), (20, -38)], "ind",
     "about 70 Sv", "1.4 m/s at the core, up to 2.5",
     "The Indian Ocean's western boundary current, as strong as the Gulf Stream, running down the coast of Mozambique and South Africa; at the Cape it turns back on itself and sheds rings of warm water into the Atlantic.", "Wikipedia, Agulhas Current"),
    ("waust", "the West Australian Current", "cold", [(108, -34), (107, -27), (106, -20), (104, -14)], "ind",
     "", "",
     "Cool water moving north off Western Australia, the eastern side of the Indian Ocean gyre.", "Wikipedia, West Australian Current"),
    ("indeq", "the South Equatorial Current", "warm", [(100, -12), (85, -12), (70, -12), (55, -13), (45, -15)], "ind",
     "", "",
     "Flowing west across the Indian Ocean under the trade winds, to Madagascar and Africa, where it feeds the Agulhas.", "Wikipedia, Indian Ocean Gyre"),
    ("indsouth", "the South Indian Current", "cold", [(20, -40), (40, -40), (60, -40), (80, -39), (100, -38)], "ind",
     "", "",
     "The gyre's southern side, flowing east with the westerlies.", "Wikipedia, Indian Ocean Gyre"),
    ("leeuwin", "the Leeuwin Current", "warm", [(112.5, -22), (112.5, -28), (114.5, -33), (117, -35.5)], None,
     "", "",
     "Odd among eastern boundary currents: warm water flowing south along Western Australia, which is why there is coral at Rottnest Island.", "Wikipedia, Leeuwin Current"),
    # the North Pacific gyre, clockwise
    ("kuroshio", "the Kuroshio", "warm", [(122, 22), (125, 27), (131, 30), (138, 34), (147, 36), (158, 38), (170, 40)], "npac",
     "65 Sv southeast of Japan", "",
     "The Black Current, the Pacific's Gulf Stream, dark blue and warm, flowing past Taiwan and Japan and out into the ocean.", "Wikipedia, Kuroshio Current"),
    ("npc", "the North Pacific Current", "warm", [(170, 40), (-175, 42), (-160, 44), (-145, 45), (-132, 46)], "npac",
     "", "",
     "The Kuroshio's water spreading east across the whole Pacific to the coast of North America, where it splits north and south.", "Wikipedia, North Pacific Current"),
    ("california", "the California Current", "cold", [(-130, 46), (-127, 40), (-123, 34), (-118, 28), (-114, 23)], "npac",
     "", "",
     "Cold water and upwelling along the coast from Washington to Baja California: the reason the sea at San Francisco is cold in August and the coast is foggy.", "Wikipedia, California Current"),
    ("npeq", "the North Equatorial Current", "warm", [(-112, 14), (-135, 13), (-160, 12), (175, 12), (150, 12), (132, 13)], "npac",
     "", "",
     "The trade-wind current of the northern tropics, west across the Pacific to the Philippines, where it feeds the Kuroshio.", "Wikipedia, North Equatorial Current"),
    ("oyashio", "the Oyashio", "cold", [(162, 55), (157, 50), (150, 45), (145, 41)], None,
     "", "",
     "Cold, rich water from the Bering Sea down the Kuril Islands to meet the Kuroshio off Japan, one of the richest fishing grounds on the planet.", "Wikipedia, Oyashio Current"),
    ("alaska", "the Alaska Current", "warm", [(-132, 48), (-138, 53), (-146, 58), (-155, 57), (-165, 53)], None,
     "", "",
     "The northern branch of the North Pacific Current, curving counterclockwise round the Gulf of Alaska and keeping its coast milder than Siberia's.", "Wikipedia, Alaska Current"),
    ("pcc", "the Equatorial Counter Current", "warm", [(140, 6), (165, 6), (-170, 6), (-140, 6), (-110, 6)], None,
     "", "",
     "A narrow eastward flow between the two westward trade-wind currents, returning some of the water piled up in the west.", "Wikipedia, Equatorial Counter Current"),
    # the South Pacific gyre, counterclockwise
    ("eac", "the East Australian Current", "warm", [(152, -18), (154, -25), (153, -31), (151, -36), (149, -41)], "spac",
     "up to 35 Sv at 30\u00b0S", "0.9 m/s at most",
     "Warm water down the coast of Queensland and New South Wales, breaking into eddies off Sydney; the current the turtles ride.", "Wikipedia, East Australian Current"),
    ("humboldt", "the Humboldt Current", "cold", [(-76, -42), (-75, -32), (-78, -22), (-81, -12), (-84, -4)], "spac",
     "", "",
     "Cold water up the coast of Chile and Peru, with upwelling that feeds the largest fishery in the world; in an El Niño year it falters and the anchovies vanish.", "Wikipedia, Humboldt Current"),
    ("speq", "the South Equatorial Current", "warm", [(-88, -6), (-115, -8), (-145, -10), (-175, -12), (160, -14), (155, -16)], "spac",
     "", "",
     "The Pacific's trade-wind current south of the equator, west across the widest ocean to the Coral Sea.", "Wikipedia, South Equatorial Current"),
    ("spacs", "the South Pacific Current", "cold", [(150, -46), (170, -46), (-170, -45), (-140, -44), (-110, -43), (-85, -44)], "spac",
     "", "",
     "The gyre's southern side, east with the westerlies toward Chile.", "Wikipedia, South Pacific Gyre"),
]

# the gyres: k, name, sense, center lon lat, a line
GYRES = [
    ("natl", "the North Atlantic gyre", "clockwise", (-45, 30), "Wind and the Earth's spin pile the warm water into a mound in the middle, the Sargasso Sea, and the currents circle it clockwise, strongest on the western side."),
    ("satl", "the South Atlantic gyre", "counterclockwise", (-15, -25), "The mirror of the northern gyre: counterclockwise, because the Coriolis turn is the other way south of the equator."),
    ("ind", "the Indian Ocean gyre", "counterclockwise", (75, -27), "Only a southern gyre, since Asia closes the ocean at the top; the northern Indian Ocean reverses with the monsoon instead."),
    ("npac", "the North Pacific gyre", "clockwise", (-160, 30), "The largest, and the one where floating plastic collects in the calm center."),
    ("spac", "the South Pacific gyre", "counterclockwise", (-120, -30), "The largest expanse of open ocean, and the clearest, poorest water on the planet at its center."),
]

# the conveyor: two paths, deep and cold, surface and warm, each a list of (lon, lat)
CONVEYOR = {
    "deep": [(-35, 62), (-40, 50), (-35, 35), (-28, 15), (-25, -5), (-20, -25), (-10, -42), (5, -52), (30, -55), (60, -55), (90, -55), (120, -55), (150, -55), (175, -50), (-175, -30), (-170, -5), (-165, 20), (-160, 40)],
    "deep_indian": [(60, -55), (68, -40), (72, -25), (70, -8), (68, 5)],
    "surface": [(-160, 40), (-175, 25), (165, 15), (140, 8), (127, 2), (119, -5), (116, -9), (105, -11), (90, -12), (80, -12), (60, -14), (42, -20), (35, -30), (25, -38), (15, -35), (0, -25), (-15, -12), (-30, 0), (-45, 12), (-60, 14), (-77, 20), (-75, 33), (-60, 40), (-45, 47), (-30, 55), (-25, 62), (-35, 62)],
    "surface_indian": [(68, 5), (62, -8), (60, -14)],
    "sink": [(-35, 62), (-45, 58), (2, 70)],
    "up": [(-160, 40), (68, 5)],
}
CONVEYOR_NOTE = ("In the far North Atlantic the water that came up from the tropics is cold, salty and heavy enough to sink to the "
                 "bottom, some 15 million cubic meters a second. It creeps south along the floor of the Atlantic, joins the "
                 "circumpolar current, and spreads into the Indian and Pacific oceans, where over centuries it warms and rises. "
                 "The surface flow that returns it runs through Indonesia, round the Cape of Good Hope, and back up the Atlantic. "
                 "One lap takes about a thousand years.")

REFS = [
    (apa.article("Broecker, W. S.", 1991, "The great ocean conveyor", "Oceanography", 4, 2, "79-89", "https://doi.org/10.5670/oceanog.1991.07"),
     "The conveyor, as first drawn."),
    (apa.article("Rahmstorf, S.", 2002, "Ocean circulation and climate during the past 120,000 years", "Nature", 419, 6903, "207-214", "https://doi.org/10.1038/nature01090"),
     "The overturning circulation and its 15 Sv or so of sinking."),
    (apa.article("Talley, L. D.", 2013, "Closure of the global overturning circulation through the Indian, Pacific, and Southern Oceans: Schematics and transports",
                 "Oceanography", 26, 1, "80-97", "https://doi.org/10.5670/oceanog.2013.07"),
     "The modern picture of the conveyor, with its return through the Southern Ocean."),
    (apa.article("Wessel, P., &amp; Smith, W. H. F.", 1996, "A global, self-consistent, hierarchical, high-resolution shoreline database",
                 "Journal of Geophysical Research: Solid Earth", 101, "B4", "8741-8743", "https://doi.org/10.1029/96JB00104"),
     "The coastlines."),
]
REFS += [(apa.wiki(f"https://en.wikipedia.org/wiki/{p}"), a) for p, a in [
    ("Ocean_current", "The currents and the gyres."),
    ("Ocean_gyre", "The five gyres and why they turn as they do."),
    ("Thermohaline_circulation", "The conveyor's route and its thousand-year lap."),
    ("Sverdrup", "The unit: a million cubic meters a second."),
    ("Gulf_Stream", None), ("North_Atlantic_Current", None), ("Canary_Current", None), ("North_Equatorial_Current", None),
    ("Loop_Current", None), ("Labrador_Current", None), ("Brazil_Current", None), ("South_Equatorial_Current", None),
    ("Benguela_Current", None), ("South_Atlantic_Current", None), ("Antarctic_Circumpolar_Current", None),
    ("Agulhas_Current", None), ("West_Australian_Current", None), ("Indian_Ocean_Gyre", None), ("Leeuwin_Current", None),
    ("Kuroshio_Current", None), ("North_Pacific_Current", None), ("California_Current", None), ("Oyashio_Current", None),
    ("Alaska_Current", None), ("Equatorial_Counter_Current", None), ("East_Australian_Current", None),
    ("Humboldt_Current", None), ("South_Pacific_Gyre", None),
]]
