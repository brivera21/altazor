#!/usr/bin/env python3
"""The species of BBC Planet Earth (2006), as Brian recorded them.

One row per appearance: 137 rows over eleven episodes, 121 distinct taxa,
fourteen of which appear in more than one episode. The names, the
scientific names and the filming locations are his table, transcribed
without addition: nothing here was looked up to fill a gap, and no
species has been added that is not in it.

The numbering is the BBC broadcast order, which is also the order IMDb,
Metacritic and TV Guide list. Some streaming apps reorder three of them,
putting Seasonal Forests at 8, Jungles at 9 and Shallow Seas at 10; that
alternative is the third number in EPISODES. ROWS is keyed by title so
neither numbering can drift into it.

Each row is (name, scientific, rank, group, subgroup, location, wiki),
where wiki is the Wikipedia article title. rank is one of species,
subspecies, genus, family, order, tribe, phylum, informal or non-taxon;
the rows above species level are the ones that carry no conservation
status, and the three that are not taxa at all (snottites, vent
bacteria, corals) carry no scientific name in the ordinary sense either.

Coordinates and IUCN categories are added by enrich_planet_earth.py and
live in tools/data/planet-earth-species.json.
"""

# number, title, and the number some streaming apps give it
EPISODES = [
    (1, "From Pole to Pole", 1),
    (2, "Mountains", 2),
    (3, "Fresh Water", 3),
    (4, "Caves", 4),
    (5, "Deserts", 5),
    (6, "Ice Worlds", 6),
    (7, "Great Plains", 7),
    (8, "Jungles", 9),
    (9, "Shallow Seas", 10),
    (10, "Seasonal Forests", 8),
    (11, "Ocean Deep", 11),
]

# keyed by episode title. name, scientific, rank, group, subgroup, location, wiki
ROWS = {
    "From Pole to Pole": [
        ("Emperor penguin", "Aptenodytes forsteri", "species", "bird", None, "Antarctica", "Emperor penguin"),
        ("Polar bear", "Ursus maritimus", "species", "mammal", None, "Svalbard, Norway (high Arctic)", "Polar bear"),
        ("Caribou / reindeer", "Rangifer tarandus", "species", "mammal", None, "Arctic tundra, northern Canada", "Reindeer"),
        ("Wolf", "Canis lupus", "species", "mammal", None, "Arctic tundra, northern Canada", "Wolf"),
        ("Amur leopard", "Panthera pardus orientalis", "subspecies", "mammal", None, "Russian Far East", "Amur leopard"),
        ("Birds-of-paradise", "Paradisaeidae", "family", "bird", None, "New Guinea", "Bird-of-paradise"),
        ("African wild dog", "Lycaon pictus", "species", "mammal", None, "Okavango Delta, Botswana", "African wild dog"),
        ("Impala", "Aepyceros melampus", "species", "mammal", None, "Okavango Delta, Botswana", "Impala"),
        ("African bush elephant", "Loxodonta africana", "species", "mammal", None, "Kalahari to Okavango, Botswana", "African bush elephant"),
        ("Chacma baboon", "Papio ursinus", "species", "mammal", None, "Okavango Delta, Botswana", "Chacma baboon"),
        ("Baikal teal", "Sibirionetta formosa", "species", "bird", None, "Wintering grounds, South Korea", "Baikal teal"),
        ("Great white shark", "Carcharodon carcharias", "species", "fish", "cartilaginous", "False Bay, South Africa", "Great white shark"),
        ("Cape fur seal", "Arctocephalus pusillus pusillus", "subspecies", "mammal", None, "False Bay, South Africa", "Arctocephalus pusillus"),
    ],
    "Mountains": [
        ("Gelada", "Theropithecus gelada", "species", "mammal", None, "Simien Mountains, Ethiopia", "Gelada"),
        ("Walia ibex", "Capra walie", "species", "mammal", None, "Simien Mountains, Ethiopia", "Walia ibex"),
        ("Ethiopian wolf", "Canis simensis", "species", "mammal", None, "Ethiopian highlands", "Ethiopian wolf"),
        ("Guanaco", "Lama guanicoe", "species", "mammal", None, "Andes, Patagonia", "Guanaco"),
        ("Puma", "Puma concolor", "species", "mammal", None, "Andes, Patagonia", "Cougar"),
        ("Grizzly bear", "Ursus arctos horribilis", "subspecies", "mammal", None, "Rocky Mountains, North America", "Grizzly bear"),
        ("Markhor", "Capra falconeri", "species", "mammal", None, "Karakoram, Pakistan", "Markhor"),
        ("Golden eagle", "Aquila chrysaetos", "species", "bird", None, "Himalaya", "Golden eagle"),
        ("Demoiselle crane", "Grus virgo", "species", "bird", None, "Himalaya (migration crossing)", "Demoiselle crane"),
        ("Snow leopard", "Panthera uncia", "species", "mammal", None, "Karakoram, Pakistan", "Snow leopard"),
        ("Giant panda", "Ailuropoda melanoleuca", "species", "mammal", None, "Qinling Mountains, China", "Giant panda"),
        ("Golden snub-nosed monkey", "Rhinopithecus roxellana", "species", "mammal", None, "Qinling Mountains, China", "Golden snub-nosed monkey"),
    ],
    "Fresh Water": [
        ("Japanese giant salamander", "Andrias japonicus", "species", "amphibian", None, "Mountain streams, Japan", "Japanese giant salamander"),
        ("Salmon", "Salmonidae (in part)", "family", "fish", "bony", "Pacific Northwest and Alaska", "Salmon"),
        ("Grizzly bear", "Ursus arctos horribilis", "subspecies", "mammal", None, "Alaskan salmon rivers", "Grizzly bear"),
        ("Smooth-coated otter", "Lutrogale perspicillata", "species", "mammal", None, "India", "Smooth-coated otter"),
        ("Mugger crocodile", "Crocodylus palustris", "species", "reptile", None, "India", "Mugger crocodile"),
        ("Nile crocodile", "Crocodylus niloticus", "species", "reptile", None, "Mara River, Kenya and Tanzania", "Nile crocodile"),
        ("Wildebeest", "Connochaetes", "genus", "mammal", None, "Mara River crossing, East Africa", "Wildebeest"),
        ("Roseate spoonbill", "Platalea ajaja", "species", "bird", None, "Pantanal, Brazil", "Roseate spoonbill"),
        ("Spectacled caiman", "Caiman crocodilus", "species", "reptile", None, "Pantanal, Brazil", "Spectacled caiman"),
        ("Cichlids", "Cichlidae", "family", "fish", "bony", "African Rift lakes (Malawi)", "Cichlid"),
        ("Piranhas", "Serrasalmidae (in part)", "family", "fish", "bony", "Pantanal, Brazil", "Piranha"),
        ("River dolphins", "Odontoceti (in part)", "informal", "mammal", None, "Amazon basin", "River dolphin"),
        ("Crab-eating macaque", "Macaca fascicularis", "species", "mammal", None, "Mangroves, Bay of Bengal", "Macaca fascicularis"),
        ("Snow goose", "Anser caerulescens", "species", "bird", None, "North American flyways", "Snow goose"),
    ],
    "Caves": [
        ("Wrinkle-lipped bat", "Chaerephon plicatus", "species", "mammal", None, "Deer Cave, Borneo, Malaysia", "Wrinkle-lipped free-tailed bat"),
        ("Cave swiftlets", "Collocaliini", "tribe", "bird", None, "Gomantong Cave, Borneo", "Swiftlet"),
        ("Cave racer", "Orthriophis taeniurus ridleyi", "subspecies", "reptile", None, "Borneo caves", "Beauty rat snake"),
        ("Rufous-bellied eagle", "Lophotriorchis kienerii", "species", "bird", None, "Deer Cave exodus, Borneo", "Rufous-bellied eagle"),
        ("Bat hawk", "Macheiramphus alcinus", "species", "bird", None, "Deer Cave exodus, Borneo", "Bat hawk"),
        ("Cockroaches", "Blattodea (in part)", "order", "invertebrate", "insect", "Gomantong Cave, Borneo", "Cockroach"),
        ("Texas blind salamander", "Eurycea rathbuni", "species", "amphibian", None, "Edwards Aquifer, Texas", "Texas blind salamander"),
        ("Cave angel fish", "Cryptotora thamicola", "species", "fish", "bony", "Caves of northern Thailand", "Waterfall climbing cave fish"),
        ("Shortfin molly", "Poecilia mexicana", "species", "fish", "bony", "Cueva de Villa Luz, Tabasco, Mexico", "Poecilia mexicana"),
        ("Snottites", "Mixed sulfur-oxidizing bacteria", "non-taxon", "bacteria", None, "Cueva de Villa Luz, Mexico", "Snottite"),
    ],
    "Deserts": [
        ("Bactrian camel", "Camelus ferus", "species", "mammal", None, "Gobi Desert, Mongolia", "Wild Bactrian camel"),
        ("Dromedary", "Camelus dromedarius", "species", "mammal", None, "Sahara", "Dromedary"),
        ("African bush elephant", "Loxodonta africana", "species", "mammal", None, "Namib Desert, Namibia", "African bush elephant"),
        ("Lion", "Panthera leo", "species", "mammal", None, "Namib Desert, Namibia", "Lion"),
        ("Gemsbok (oryx)", "Oryx gazella", "species", "mammal", None, "Namib Desert, Namibia", "Gemsbok"),
        ("Red kangaroo", "Osphranter rufus", "species", "mammal", None, "Australian outback", "Red kangaroo"),
        ("Fennec fox", "Vulpes zerda", "species", "mammal", None, "Sahara", "Fennec fox"),
        ("Flat lizard", "Platysaurus broadleyi", "species", "reptile", None, "Augrabies Falls, South Africa", "Broadley's flat lizard"),
        ("Black flies", "Simuliidae", "family", "invertebrate", "insect", "Augrabies Falls, South Africa", "Black fly"),
        ("Nubian ibex", "Capra nubiana", "species", "mammal", None, "Deserts of the Middle East", "Nubian ibex"),
    ],
    "Ice Worlds": [
        ("Snow petrel", "Pagodroma nivea", "species", "bird", None, "Antarctic nunataks", "Snow petrel"),
        ("South polar skua", "Stercorarius maccormicki", "species", "bird", None, "Antarctica", "South polar skua"),
        ("Humpback whale", "Megaptera novaeangliae", "species", "mammal", None, "Southern Ocean", "Humpback whale"),
        ("Antarctic krill", "Euphausia superba", "species", "invertebrate", "crustacean", "Southern Ocean", "Antarctic krill"),
        ("Emperor penguin", "Aptenodytes forsteri", "species", "bird", None, "Antarctic sea ice and inland colonies", "Emperor penguin"),
        ("Muskox", "Ovibos moschatus", "species", "mammal", None, "Arctic Canada and Greenland", "Muskox"),
        ("Arctic fox", "Vulpes lagopus", "species", "mammal", None, "High Arctic", "Arctic fox"),
        ("Wolf", "Canis lupus", "species", "mammal", None, "High Arctic", "Wolf"),
        ("Polar bear", "Ursus maritimus", "species", "mammal", None, "Svalbard, Norway", "Polar bear"),
        ("Walrus", "Odobenus rosmarus", "species", "mammal", None, "Svalbard, Norway", "Walrus"),
    ],
    "Great Plains": [
        ("Red-billed quelea", "Quelea quelea", "species", "bird", None, "Savanna, southern Africa", "Red-billed quelea"),
        ("Mongolian gazelle", "Procapra gutturosa", "species", "mammal", None, "Eastern steppe, Mongolia", "Mongolian gazelle"),
        ("Snow goose", "Anser caerulescens", "species", "bird", None, "Arctic tundra breeding grounds", "Snow goose"),
        ("Arctic fox", "Vulpes lagopus", "species", "mammal", None, "Arctic tundra", "Arctic fox"),
        ("Caribou", "Rangifer tarandus", "species", "mammal", None, "Arctic tundra, North America", "Reindeer"),
        ("Wolf", "Canis lupus", "species", "mammal", None, "Arctic tundra, North America", "Wolf"),
        ("American bison", "Bison bison", "species", "mammal", None, "North American prairie", "American bison"),
        ("Wild yak", "Bos mutus", "species", "mammal", None, "Tibetan Plateau", "Wild yak"),
        ("Wild ass (kiang)", "Equus kiang", "species", "mammal", None, "Tibetan Plateau", "Kiang"),
        ("Pika", "Ochotona curzoniae", "species", "mammal", None, "Tibetan Plateau", "Plateau pika"),
        ("Tibetan fox", "Vulpes ferrilata", "species", "mammal", None, "Tibetan Plateau", "Tibetan fox"),
        ("Pygmy hog", "Porcula salvania", "species", "mammal", None, "Tall grasslands, Assam, India", "Pygmy hog"),
        ("African bush elephant", "Loxodonta africana", "species", "mammal", None, "Savuti, Botswana", "African bush elephant"),
        ("Lion", "Panthera leo", "species", "mammal", None, "Savuti, Botswana", "Lion"),
    ],
    "Seasonal Forests": [
        ("Moose", "Alces alces", "species", "mammal", None, "Subarctic taiga", "Moose"),
        ("Wolverine", "Gulo gulo", "species", "mammal", None, "Subarctic taiga", "Wolverine"),
        ("Coast redwood", "Sequoia sempervirens", "species", "plant", "conifer", "Pacific coast, California", "Sequoia sempervirens"),
        ("Pine marten", "Martes", "genus", "mammal", None, "Pacific coast conifer forest", "Marten"),
        ("Squirrel", "Sciuridae", "family", "mammal", None, "Pacific coast conifer forest", "Squirrel"),
        ("Great gray owl", "Strix nebulosa", "species", "bird", None, "Boreal forest, North America", "Great grey owl"),
        ("Pudú", "Pudu puda", "species", "mammal", None, "Valdivian forest, Chile", "Southern pudu"),
        ("Kodkod", "Leopardus guigna", "species", "mammal", None, "Valdivian forest, Chile", "Kodkod"),
        ("Mandarin duck", "Aix galericulata", "species", "bird", None, "Temperate broadleaf forest, Europe (species native to East Asia)", "Mandarin duck"),
        ("Periodical cicadas", "Magicicada", "genus", "invertebrate", "insect", "Eastern North America", "Periodical cicadas"),
        ("Amur leopard", "Panthera pardus orientalis", "subspecies", "mammal", None, "Russian Far East", "Amur leopard"),
        ("Langur", "Semnopithecus", "genus", "mammal", None, "Teak forests, India", "Semnopithecus"),
        ("Chital", "Axis axis", "species", "mammal", None, "Teak forests, India", "Chital"),
        ("Tiger", "Panthera tigris tigris", "subspecies", "mammal", None, "Teak forests, India", "Bengal tiger"),
        ("Mouse lemur", "Microcebus", "genus", "mammal", None, "Madagascar", "Mouse lemur"),
        ("Baobab", "Adansonia", "genus", "plant", None, "Madagascar", "Adansonia"),
    ],
    "Jungles": [
        ("Birds-of-paradise", "Paradisaeidae", "family", "bird", None, "New Guinea", "Bird-of-paradise"),
        ("Siamang", "Symphalangus syndactylus", "species", "mammal", None, "Sumatra, Indonesia", "Siamang"),
        ("Orangutan", "Pongo", "genus", "mammal", None, "Borneo and Sumatra", "Orangutan"),
        ("Tree frogs", "Hylidae and others", "informal", "amphibian", None, "Central American rainforest", "Tree frog"),
        ("Figs", "Ficus", "genus", "plant", None, "Tropical rainforest canopy", "Ficus"),
        ("Cordyceps", "Cordyceps", "genus", "fungus", None, "Tropical rainforest floor", "Cordyceps"),
        ("Pitcher plants", "Nepenthes", "genus", "plant", None, "Borneo", "Nepenthes"),
        ("Red crab spider", "Misumenops nepenthicola", "species", "invertebrate", "arachnid", "Borneo", "Henriksenia nepenthicola"),
        ("African forest elephant", "Loxodonta cyclotis", "species", "mammal", None, "Congo Basin forest clearings", "African forest elephant"),
        ("Chimpanzee", "Pan troglodytes", "species", "mammal", None, "Ngogo, Kibale, Uganda", "Chimpanzee"),
    ],
    "Shallow Seas": [
        ("Humpback whale", "Megaptera novaeangliae", "species", "mammal", None, "Tropical breeding grounds", "Humpback whale"),
        ("Banded sea krait", "Laticauda colubrina", "species", "reptile", None, "Coral reefs, Indonesia", "Yellow-lipped sea krait"),
        ("Goatfish", "Mullidae", "family", "fish", "bony", "Coral reefs, Indonesia", "Goatfish"),
        ("Trevally", "Carangidae", "family", "fish", "bony", "Coral reefs, Indonesia", "Carangidae"),
        ("Bottlenose dolphin", "Tursiops aduncus", "species", "mammal", None, "Shark Bay, Western Australia", "Indo-Pacific bottlenose dolphin"),
        ("Socotra cormorant", "Phalacrocorax nigrogularis", "species", "bird", None, "Bahrain, Persian Gulf", "Socotra cormorant"),
        ("South American sea lion", "Otaria flavescens", "species", "mammal", None, "Patagonian coast, Argentina", "South American sea lion"),
        ("Dusky dolphin", "Lagenorhynchus obscurus", "species", "mammal", None, "Patagonian coast, Argentina", "Dusky dolphin"),
        ("Chokka squid", "Loligo reynaudii", "species", "invertebrate", "mollusc", "South African coast", "Loligo reynaudii"),
        ("Short-tail stingray", "Bathytoshia brevicaudata", "species", "fish", "cartilaginous", "South African coast", "Short-tail stingray"),
        ("Cape fur seal", "Arctocephalus pusillus pusillus", "subspecies", "mammal", None, "South African coast", "Arctocephalus pusillus"),
        ("Great white shark", "Carcharodon carcharias", "species", "fish", "cartilaginous", "South African coast", "Great white shark"),
        ("King penguin", "Aptenodytes patagonicus", "species", "bird", None, "Marion Island, Indian Ocean", "King penguin"),
    ],
    "Ocean Deep": [
        ("Whale shark", "Rhincodon typus", "species", "fish", "cartilaginous", "Tropical open ocean", "Whale shark"),
        ("Yellowfin tuna", "Thunnus albacares", "species", "fish", "bony", "Tropical open ocean", "Yellowfin tuna"),
        ("Oceanic whitetip shark", "Carcharhinus longimanus", "species", "fish", "cartilaginous", "Open ocean", "Oceanic whitetip shark"),
        ("Rainbow runner", "Elagatis bipinnulata", "species", "fish", "bony", "Open ocean", "Rainbow runner"),
        ("Common dolphin", "Delphinus delphis", "species", "mammal", None, "Azores, North Atlantic", "Common dolphin"),
        ("Scad mackerel", "Trachurus", "genus", "fish", "bony", "Azores, North Atlantic", "Trachurus"),
        ("Shearwater", "Calonectris borealis", "species", "bird", None, "Azores, North Atlantic", "Cory's shearwater"),
        ("Spider crab", "Macrocheira kaempferi", "species", "invertebrate", "crustacean", "Deep seafloor", "Japanese spider crab"),
        ("Vent bacteria", "Chemosynthetic prokaryotes", "non-taxon", "bacteria", None, "Mid-Atlantic Ridge vents", "Hydrothermal vent"),
        ("Corals", "Anthozoa (in part)", "non-taxon", "invertebrate", "cnidarian", "Deep seamount cliffs", "Coral"),
        ("Sponges", "Porifera", "phylum", "invertebrate", "sponge", "Deep seamount cliffs", "Sponge"),
        ("Frigatebird", "Fregata aquila", "species", "bird", None, "Ascension Island, Atlantic", "Ascension frigatebird"),
        ("Green turtle", "Chelonia mydas", "species", "reptile", None, "Ascension Island, Atlantic", "Green sea turtle"),
        ("Sailfish", "Istiophorus", "genus", "fish", "bony", "Off the Pacific coast of Mexico", "Sailfish"),
        ("Blue whale", "Balaenoptera musculus", "species", "mammal", None, "Open ocean", "Blue whale"),
    ],
}

# the ranks that carry a conservation status; everything else is left null
RANKED = ("species", "subspecies")
ABOVE = ("genus", "family", "order", "tribe", "phylum", "informal")
NON_TAXON = ("non-taxon",)
