#!/usr/bin/env python3
"""The data behind agriculture.html: where farming was invented, what the
world grows now, and what the land and the animals add up to.

The centres and dates follow the domestication literature as summarised
in Larson and colleagues' 2014 review and the encyclopaedias, rounded;
the harvests are FAO figures as reported per crop, each with its year;
the land and biomass figures are Ritchie and Roser's and Bar-On, Phillips
and Milo's.
"""

import apa

# the centres of domestication: k, name, lon, lat, years ago (a round figure), plants, animals, a line
CENTRES = [
    ("crescent", "the Fertile Crescent", 38, 36, 10500, "einkorn and emmer wheat, barley, lentils, peas, chickpeas, flax", "sheep, goats, cattle, pigs", "The first, or tied for it: grain farming on the hills of the Levant and the Zagros about 10,500 years ago, with the four barnyard animals domesticated in the same region within the next two thousand. Wheat, barley and bread all begin here, and so does the village."),
    ("yangtze", "the Yangtze valley", 112, 30, 9000, "rice", "pigs, later chickens", "Rice gathered wild from 13,000 years ago and fully domesticated by about 8,000; the paddy field, with its standing water, followed. Half the world now eats from this one grass."),
    ("yellow", "the Yellow River", 110, 36, 8000, "foxtail and broomcorn millet, later soybean", "pigs, chickens, silkworms", "The dry north of China domesticated two millets about 8,000 years ago, and later the soybean; the two Chinese centres, rice in the south and millet in the north, fed the longest continuous civilisation there is."),
    ("newguinea", "the New Guinea highlands", 144, -6, 9000, "taro, bananas, yams, sugarcane", "none", "At Kuk Swamp, ditches and mounds for taro and banana from about 9,000 years ago, and perhaps earlier: farming invented on an island without grain, from roots and fruit, and the banana that the world eats is descended from these."),
    ("mesoamerica", "Mesoamerica", -100, 18, 9000, "maize, squash, beans, chili, avocado, cacao", "turkeys, dogs", "Maize was bred from teosinte, a grass with a dozen hard kernels, in the Balsas valley about 9,000 years ago, squash earlier, and beans by 6,000; the three sisters planted together fed every civilisation from the Olmec to the Aztec, and now feed the world's cattle."),
    ("andes", "the Andes", -72, -14, 8000, "potatoes, quinoa, oca", "llamas, alpacas, guinea pigs", "The potato, domesticated on the high plateau by Lake Titicaca about 8,000 years ago, and the llama, the New World's only beast of burden. Thousands of potato varieties still grow there; Europe took a handful, and Ireland leaned on one."),
    ("amazonia", "south-western Amazonia", -63, -12, 8000, "manioc, peanuts, sweet potatoes, cacao", "none", "The forest's own centre: manioc, a root that has to be grated and squeezed of its cyanide before it can be eaten, from about 8,000 years ago, and the peanut. Manioc is now the staple of half a billion people in Africa."),
    ("sahel", "the Sahel", 0, 14, 5000, "sorghum, pearl millet, cowpeas", "cattle, perhaps a second time", "Sorghum and pearl millet, grasses that stand drought, domesticated on the southern edge of the Sahara about 5,000 years ago as it dried; cattle herding there may be older than the crops."),
    ("ethiopia", "the Ethiopian highlands", 38, 9, None, "teff, coffee, ensete, finger millet", "none", "A centre of its own with crops grown almost nowhere else: teff, the smallest grain in cultivation, the false banana ensete, and coffee, which left for Yemen and the world only in the fifteenth century."),
    ("westafrica", "West Africa", -5, 8, 4000, "yams, African rice, oil palm, kola", "guinea fowl", "Yams from the forest edge and a rice of Africa's own, Oryza glaberrima, domesticated in the Niger delta about 3,000 years ago; the oil palm, now the world's largest source of vegetable oil, is native here."),
    ("eastern", "eastern North America", -88, 37, 4500, "sunflower, squash, goosefoot, sumpweed", "none", "Sunflower and a local squash, with two seed plants nobody grows any more, in the river valleys of the Mississippi and Ohio about 4,500 years ago; maize arrived from Mexico much later and took over."),
    ("steppe", "the Pontic steppe", 40, 48, 5000, "none", "horses", "Not a farming centre but the horse's: tamed on the grasslands north of the Black Sea and the Caspian about five thousand years ago, the date still argued over, and with it came the cart, the chariot, the cavalry and half of the history since."),
]

# the world's harvest: k, name, million tonnes, year, top producer and share, what it is for, source
CROPS = [
    ("sugarcane", "sugarcane", 1920, 2022, "Brazil, 38%", "sugar, and in Brazil ethanol for cars; four fifths of it is water and fibre", "Wikipedia, Sugarcane"),
    ("maize", "maize", 1160, 2020, "the United States, 31%", "mostly animal feed and ethanol; the grain people eat directly is a small share outside Africa and Latin America", "Wikipedia, Maize"),
    ("rice", "rice", 800, 2023, "China and India, 52% together", "food, almost all of it: the staple of more than half of humanity", "Wikipedia, Rice"),
    ("wheat", "wheat", 799, 2024, "China, 18%", "bread, noodles, pasta: the staple of the other half", "Wikipedia, Wheat"),
    ("potato", "potatoes", 383, 2023, "China, 25%", "food; the largest crop that is not a grass", "Wikipedia, Potato"),
    ("soy", "soybeans", 353, 2020, "Brazil and the United States, 66% together", "four fifths of it feeds livestock, as meal; the oil is pressed off first", "Wikipedia, Soybean"),
    ("cassava", "cassava", 330, 2022, "Nigeria, 18%", "food, for half a billion people in the tropics, and starch", "Wikipedia, Cassava"),
    ("sugarbeet", "sugar beet", 294, 2024, "Russia, 16%", "the temperate world's sugar", "Wikipedia, Sugar beet"),
    ("tomato", "tomatoes", 192, 2023, "China, 36%", "food; the largest vegetable crop, and botanically a fruit", "Wikipedia, Tomato"),
    ("banana", "bananas and plantains", 179, 2022, "India and China, 26% together", "food; nearly all the export bananas are one clone, the Cavendish", "Wikipedia, Banana"),
    ("barley", "barley", 142, 2024, "Russia, 12%", "seven tenths animal feed, three tenths malt for beer and whisky", "Wikipedia, Barley"),
    ("palmoil", "palm oil", 77, 2024, "Indonesia, 57%", "cooking oil, processed food, soap and biodiesel; the oil alone, pressed from about five times its weight of fruit", "Wikipedia, Palm oil"),
]

# the land, after Ritchie and Roser 2024, from FAO and Poore and Nemecek 2018
LAND = {
    "agri_km2": 48e6, "agri_share_habitable": 44,
    "livestock_pct": 80, "crops_people_pct": 16, "crops_other_pct": 4,
    "animal_calories_pct": 17, "animal_protein_pct": 38,
}
# the animals, after Bar-On, Phillips and Milo 2018, gigatonnes of carbon
BIOMASS = [
    ("livestock", "livestock", 0.1, "cattle and pigs above all"),
    ("humans", "humans", 0.06, "eight billion of us"),
    ("wildmammals", "wild mammals", 0.007, "on land and at sea together"),
    ("poultry", "poultry", 0.005, "chickens, mostly"),
    ("wildbirds", "wild birds", 0.002, "every wild bird on Earth"),
]

REFS = [
    (apa.article("Larson, G., Piperno, D. R., Allaby, R. G., Purugganan, M. D., Andersson, L., Arroyo-Kalin, M., Barton, L., Climer Vigueira, C., Denham, T., Dobney, K., Doust, A. N., Gepts, P., Gilbert, M. T. P., Gremillion, K. J., Lucas, L., Lukens, L., Marshall, F. B., Olsen, K. M., Pires, J. C., ... Fuller, D. Q.", 2014,
                 "Current perspectives and the future of domestication studies", "Proceedings of the National Academy of Sciences", 111, 17, "6139-6146", "https://doi.org/10.1073/pnas.1323964111"),
     "The centres of domestication and their dates, as the field saw them in 2014."),
    (apa.article("Bar-On, Y. M., Phillips, R., &amp; Milo, R.", 2018, "The biomass distribution on Earth", "Proceedings of the National Academy of Sciences", 115, 25, "6506-6511", "https://doi.org/10.1073/pnas.1711842115"),
     "Livestock 0.1 gigatonnes of carbon, humans 0.06, wild mammals 0.007; poultry 0.005 against wild birds 0.002."),
    (apa.article("Poore, J., &amp; Nemecek, T.", 2018, "Reducing food's environmental impacts through producers and consumers", "Science", 360, 6392, "987-992", "https://doi.org/10.1126/science.aaq0216"),
     "Animal foods on most of the farmland for a sixth of the calories and a third of the protein."),
    (apa.web("Ritchie, H., &amp; Roser, M.", 2024, "Half of the world's habitable land is used for agriculture", "Our World in Data", "https://ourworldindata.org/global-land-for-agriculture"),
     "48 million square kilometres of farmland, 44 percent of the habitable land; four fifths of it for livestock; 17 percent of calories and 38 percent of protein from animals."),
    (apa.web("Food and Agriculture Organization of the United Nations", 2025, "FAOSTAT: Crops and livestock products", "FAO", "https://www.fao.org/faostat/en/#data/QCL"),
     "The harvests, as reported for each crop with its year."),
]
REFS += [(apa.wiki(f"https://en.wikipedia.org/wiki/{p}"), a) for p, a in [
    ("Neolithic_Revolution", "The centres, crops and dates."),
    ("Domestication_of_animals", None), ("Kuk_Early_Agricultural_Site", None), ("Maize", "Teosinte and the Balsas valley; 1.16 billion tonnes in 2020."), ("Potato", None), ("Domestication_of_the_horse", None),
    ("Sugarcane", None), ("Rice", None), ("Wheat", None), ("Soybean", None), ("Cassava", None), ("Sugar_beet", None), ("Tomato", None), ("Banana", None), ("Barley", None), ("Palm_oil", None),
]]
