#!/usr/bin/env python3
"""Where the Planet Earth rows were filmed, as coordinates.

Keyed by the location string exactly as it appears in Brian's table. Each
entry is (lat, lon, precision, wikipedia_place, note).

precision is his: "site" where the location names a place a pin can sit
on, and "region" where it names only a region, a biome or a habitat, in
which case the coordinates are a representative centroid and the note
says what was chosen and why. Every region row carries a note; site rows
carry one only where the name needs explaining.

wikipedia_place is the article the coordinates were taken from. Where it
is set, the pair below is the coordinate that article carries, rounded,
checked on September 19, 2026. Where it is None the coordinates are this
file's own and the note says how they were chosen: either the article has
no coordinates, or its coordinate is somewhere the row does not mean.

The coordinates follow the location field, never the species' range: a
row filmed in "Mountain streams, Japan" is placed in the mountain country
of Japan, not where that salamander happens to live.
"""

PLACES = {
    # named places: a cave, a bay, a delta, a river, an island, a park
    "African Rift lakes (Malawi)": (-12, 34.5, "site", "Lake Malawi", "Lake Malawi, the Rift lake the episode names"),
    "Ascension Island, Atlantic": (-7.93, -14.37, "site", "Ascension Island", None),
    "Augrabies Falls, South Africa": (-28.59, 20.34, "site", "Augrabies Falls", None),
    "Azores, North Atlantic": (38.66, -27.82, "site", "Azores", "the archipelago and the water around it, about 2,300 km2 of land"),
    "Bahrain, Persian Gulf": (26.08, 50.55, "site", "Bahrain", None),
    "Cueva de Villa Luz, Mexico": (17.44, -92.78, "site", None, "the cave at Tapijulapa, Tabasco"),
    "Cueva de Villa Luz, Tabasco, Mexico": (17.44, -92.78, "site", None, "the cave at Tapijulapa, Tabasco"),
    "Deer Cave, Borneo, Malaysia": (4.13, 114.92, "site", "Deer Cave", None),
    "Deer Cave exodus, Borneo": (4.13, 114.92, "site", "Deer Cave", "the mouth of Deer Cave, where the hawks wait"),
    "Edwards Aquifer, Texas": (29.7, -98.6, "site", None, "the aquifer's span across the Balcones escarpment; the article carries no coordinates"),
    "False Bay, South Africa": (-34.23, 18.65, "site", "False Bay", None),
    "Gomantong Cave, Borneo": (5.52, 118.07, "site", "Gomantong Caves", None),
    "Mara River, Kenya and Tanzania": (-1.5, 35.0, "site", None, "the reach through the Masai Mara; Wikipedia's article coordinate is the river's mouth on Lake Victoria, 120 km downstream"),
    "Mara River crossing, East Africa": (-1.5, 35.0, "site", None, "the crossing reach in the Masai Mara, upstream of the article's coordinate"),
    "Marion Island, Indian Ocean": (-46.88, 37.75, "site", "Marion Island", None),
    "Ngogo, Kibale, Uganda": (0.5, 30.4, "site", "Kibale National Park", "the Ngogo study area in Kibale"),
    "Okavango Delta, Botswana": (-19.4, 22.9, "site", "Okavango Delta", None),
    "Pantanal, Brazil": (-17.4, -57.5, "site", "Pantanal", None),
    "Savuti, Botswana": (-18.57, 24.07, "site", None, "the Savuti marsh and channel; the article carries no coordinates"),
    "Shark Bay, Western Australia": (-25.5, 113.25, "site", "Shark Bay", "the bay itself; the article's coordinate falls on the peninsula"),
    "Simien Mountains, Ethiopia": (13.27, 38.08, "site", "Simien Mountains", None),
    "Svalbard, Norway": (78.22, 15.65, "site", "Svalbard", None),
    "Svalbard, Norway (high Arctic)": (78.22, 15.65, "site", "Svalbard", None),

    # regions, biomes and habitats: the coordinates are a representative centroid
    "Alaskan salmon rivers": (58.6, -155.0, "region", None, "the salmon rivers of the Alaska Peninsula"),
    "Amazon basin": (-3, -60, "region", "Amazon basin", "the middle of the basin"),
    "Andes, Patagonia": (-48.0, -72.5, "region", None, "the southern Patagonian Andes"),
    "Antarctic nunataks": (-71.5, 11.0, "region", None, "the nunatak country inland of Queen Maud Land"),
    "Antarctic sea ice and inland colonies": (-75.0, 0.0, "region", None, "the coast and hinterland of Queen Maud Land"),
    "Antarctica": (-82.0, 0.0, "region", None, "the continental interior; Wikipedia's article coordinate is the South Pole itself, which a flat map cannot place"),
    "Arctic Canada and Greenland": (74.0, -75.0, "region", None, "between the Canadian Arctic Archipelago and north Greenland"),
    "Arctic tundra": (69.0, -100.0, "region", None, "the North American tundra; the biome article carries no coordinates"),
    "Arctic tundra breeding grounds": (69.0, -100.0, "region", None, "the North American tundra"),
    "Arctic tundra, North America": (68.0, -105.0, "region", None, "the mainland tundra west of Hudson Bay"),
    "Arctic tundra, northern Canada": (68.0, -105.0, "region", None, "the mainland tundra west of Hudson Bay"),
    "Australian outback": (-25, 130, "region", "Outback", "the center of the continent"),
    "Boreal forest, North America": (57.0, -102.0, "region", None, "the middle of the North American boreal belt"),
    "Borneo": (0, 114, "region", "Borneo", "the island, 743,000 km2, too large for a single pin"),
    "Borneo and Sumatra": (0.0, 109.0, "region", None, "between the two islands, on the west coast of Borneo"),
    "Borneo caves": (4.05, 114.85, "region", None, "the limestone cave country of northern Borneo"),
    "Caves of northern Thailand": (19.0, 98.2, "region", None, "the limestone caves of Mae Hong Son and Chiang Mai"),
    "Central American rainforest": (10.4, -84.0, "region", None, "the Caribbean-slope rainforest of Costa Rica"),
    "Congo Basin forest clearings": (0, 22, "region", "Congo Basin", "the middle of the basin"),
    "Coral reefs, Indonesia": (-5.0, 120.5, "region", None, "the reefs of the central Indonesian archipelago, on the water rather than on Sulawesi"),
    "Deep seafloor": (0.0, -160.0, "region", None, "no geography given; the deep Pacific basin"),
    "Deep seamount cliffs": (0.0, -160.0, "region", None, "no geography given; the seamounts of the deep Pacific"),
    "Deserts of the Middle East": (27.0, 42.0, "region", None, "the Arabian desert belt"),
    "Eastern North America": (39.0, -82.0, "region", None, "the eastern deciduous forest"),
    "Eastern steppe, Mongolia": (47.5, 114.0, "region", None, "the eastern Mongolian steppe"),
    "Ethiopian highlands": (10.71, 37.85, "region", "Ethiopian Highlands", "the middle of the highlands"),
    "Gobi Desert, Mongolia": (42.59, 103.43, "region", "Gobi Desert", "the middle of the desert"),
    "High Arctic": (78.0, -90.0, "region", None, "the Queen Elizabeth Islands"),
    "Himalaya": (27.98, 86.92, "region", "Himalayas", "the central Himalaya, the range being 2,400 km long"),
    "Himalaya (migration crossing)": (28.0, 84.0, "region", None, "the central Himalaya, where the cranes cross"),
    "India": (21.0, 78.0, "region", "India", "the center of the country"),
    "Kalahari to Okavango, Botswana": (-21.5, 23.0, "region", None, "between the Kalahari sands and the delta"),
    "Karakoram, Pakistan": (36, 76, "region", "Karakoram", "the middle of the range"),
    "Madagascar": (-20, 47, "region", "Madagascar", "the island, 587,000 km2"),
    "Mangroves, Bay of Bengal": (21.75, 88.75, "region", "Sundarbans", "the Sundarbans, the great mangrove of the bay"),
    "Mid-Atlantic Ridge vents": (30.0, -42.0, "region", None, "the ridge between the Azores fields and TAG"),
    "Mountain streams, Japan": (35.5, 136.0, "region", None, "the mountain country of central Honshu"),
    "Namib Desert, Namibia": (-24.75, 15.28, "region", "Namib", "the middle of the desert"),
    "New Guinea": (-6, 142, "region", "New Guinea", "the island, 786,000 km2"),
    "North American flyways": (45.0, -97.0, "region", None, "the Central and Mississippi flyways"),
    "North American prairie": (44.0, -101.0, "region", None, "the northern prairie; the article carries no coordinates"),
    "Off the Pacific coast of Mexico": (15.5, -96.5, "region", None, "the Pacific off Oaxaca"),
    "Open ocean": (0.0, -30.0, "region", None, "no geography given; the open Atlantic"),
    "Pacific Northwest and Alaska": (55.0, -133.0, "region", None, "the coast from British Columbia to southeast Alaska"),
    "Pacific coast conifer forest": (44.0, -123.5, "region", None, "the coastal conifer forest of Oregon"),
    "Pacific coast, California": (41.0, -124.0, "region", None, "the redwood coast of northern California"),
    "Patagonian coast, Argentina": (-43.0, -64.3, "region", None, "the water off the Valdes coast"),
    "Qinling Mountains, China": (33.96, 107.62, "region", "Qinling", "the middle of the range"),
    "Rocky Mountains, North America": (44.15, -113.8, "region", "Rocky Mountains", "the middle of the range"),
    "Russian Far East": (44.5, 135.0, "region", None, "the Primorye forests; the article carries no coordinates"),
    "Sahara": (23, 13, "region", "Sahara", "the middle of the desert"),
    "Savanna, southern Africa": (-20.0, 28.0, "region", None, "the southern African savanna"),
    "South African coast": (-34.0, 22.0, "region", None, "the Cape and Agulhas coast"),
    "Southern Ocean": (-60.0, 0.0, "region", None, "the Atlantic sector; the ocean article carries no coordinates"),
    "Subarctic taiga": (62.0, -130.0, "region", None, "the North American taiga; the biome article carries no coordinates"),
    "Sumatra, Indonesia": (0, 102, "region", "Sumatra", "the island, 473,000 km2"),
    "Tall grasslands, Assam, India": (26.4, 92.5, "region", None, "the tall grasslands of the Brahmaputra valley"),
    "Teak forests, India": (22.0, 79.5, "region", None, "the teak forests of central India"),
    "Temperate broadleaf forest, Europe (species native to East Asia)": (51.0, 7.0, "region", None, "the broadleaf forest of western Europe"),
    "Tibetan Plateau": (33.0, 88.0, "region", "Tibetan Plateau", "the middle of the plateau"),
    "Tropical breeding grounds": (10.0, -150.0, "region", None, "no place given; the tropical Pacific"),
    "Tropical open ocean": (5.0, -140.0, "region", None, "no place given; the tropical Pacific"),
    "Tropical rainforest canopy": (0.0, -62.0, "region", None, "no place given; the equatorial rainforest belt, centered on Amazonia"),
    "Tropical rainforest floor": (0.0, -62.0, "region", None, "no place given; the equatorial rainforest belt, centered on Amazonia"),
    "Valdivian forest, Chile": (-41.33, -73.66, "region", "Valdivian temperate rainforest", "the middle of the ecoregion"),
    "Wintering grounds, South Korea": (36.5, 126.8, "region", None, "the west-coast reservoirs and rice fields"),
}
