#!/usr/bin/env python3
"""IUCN Red List categories for the Planet Earth rows that are a species
or a subspecies. Nothing above that level appears here: a genus or a
family has no Red List category, and guessing one from a member species
would be worse than the blank.

Each entry is (category, assessed_taxon, note). assessed_taxon is set
where the Red List assesses the row's animal under a different name, or,
for the five subspecies, where the assessment that covers it is the
parent species'. The page shows the note so a species-level category is
never passed off as a subspecies' own.

NE means the Red List has not evaluated the taxon at all, which is a
finding rather than a gap: a Japanese spider crab and a Nepenthes crab
spider have never been assessed, and the Red List does not assess
domesticated animals such as the dromedary.

Checked on September 19, 2026 against the GBIF distribution of the Red
List, cross-checked at iucnredlist.org for the green turtle, whose
category has changed since the series was made.
"""

SOURCE = ("IUCN Red List of Threatened Species, version 2026-1, "
          "read through the GBIF checklist published July 28, 2026")
CHECKED = "September 19, 2026"

CATEGORIES = {
    "LC": "Least Concern", "NT": "Near Threatened", "VU": "Vulnerable",
    "EN": "Endangered", "CR": "Critically Endangered", "NE": "Not Evaluated",
}

# scientific name -> (category, assessed taxon if different, note)
IUCN = {
    'Aepyceros melampus': ('LC', None, None),
    'Ailuropoda melanoleuca': ('VU', None, None),
    'Aix galericulata': ('LC', None, None),
    'Alces alces': ('LC', None, None),
    'Andrias japonicus': ('VU', None, None),
    'Anser caerulescens': ('LC', None, None),
    'Aptenodytes forsteri': ('NT', None, None),
    'Aptenodytes patagonicus': ('LC', None, None),
    'Aquila chrysaetos': ('LC', None, None),
    'Arctocephalus pusillus pusillus': ('LC', 'Arctocephalus pusillus', 'assessed for the species Arctocephalus pusillus, not the subspecies'),
    'Axis axis': ('LC', None, None),
    'Balaenoptera musculus': ('EN', None, None),
    'Bathytoshia brevicaudata': ('LC', None, None),
    'Bison bison': ('NT', None, None),
    'Bos mutus': ('VU', None, None),
    'Caiman crocodilus': ('LC', None, None),
    'Calonectris borealis': ('LC', None, None),
    'Camelus dromedarius': ('NE', None, 'the Red List does not assess domesticated animals'),
    'Camelus ferus': ('EN', None, None),
    'Canis lupus': ('LC', None, None),
    'Canis simensis': ('EN', None, None),
    'Capra falconeri': ('NT', None, None),
    'Capra nubiana': ('VU', None, None),
    'Capra walie': ('CR', None, None),
    'Carcharhinus longimanus': ('CR', None, None),
    'Carcharodon carcharias': ('VU', None, None),
    'Chaerephon plicatus': ('LC', 'Mops plicatus', 'assessed under Mops plicatus'),
    'Chelonia mydas': ('LC', None, None),
    'Crocodylus niloticus': ('LC', None, None),
    'Crocodylus palustris': ('VU', None, None),
    'Cryptotora thamicola': ('VU', None, None),
    'Delphinus delphis': ('LC', None, None),
    'Elagatis bipinnulata': ('LC', None, None),
    'Equus kiang': ('LC', None, None),
    'Euphausia superba': ('LC', None, None),
    'Eurycea rathbuni': ('CR', None, None),
    'Fregata aquila': ('VU', None, None),
    'Grus virgo': ('LC', 'Anthropoides virgo', 'assessed under Anthropoides virgo'),
    'Gulo gulo': ('LC', None, None),
    'Lagenorhynchus obscurus': ('LC', 'Aethalodelphis obscurus', 'assessed under Aethalodelphis obscurus'),
    'Lama guanicoe': ('LC', None, None),
    'Laticauda colubrina': ('LC', None, None),
    'Leopardus guigna': ('LC', None, None),
    'Loligo reynaudii': ('LC', None, None),
    'Lophotriorchis kienerii': ('NT', None, None),
    'Loxodonta africana': ('EN', None, None),
    'Loxodonta cyclotis': ('CR', None, None),
    'Lutrogale perspicillata': ('VU', None, None),
    'Lycaon pictus': ('EN', None, None),
    'Macaca fascicularis': ('EN', None, None),
    'Macheiramphus alcinus': ('LC', None, None),
    'Macrocheira kaempferi': ('NE', None, 'no assessment'),
    'Megaptera novaeangliae': ('LC', None, None),
    'Misumenops nepenthicola': ('NE', None, 'no assessment'),
    'Ochotona curzoniae': ('LC', None, None),
    'Odobenus rosmarus': ('VU', None, None),
    'Orthriophis taeniurus ridleyi': ('NE', None, 'no assessment, at subspecies or species level'),
    'Oryx gazella': ('LC', None, None),
    'Osphranter rufus': ('LC', None, None),
    'Otaria flavescens': ('LC', 'Otaria byronia', 'assessed under Otaria byronia'),
    'Ovibos moschatus': ('LC', None, None),
    'Pagodroma nivea': ('LC', None, None),
    'Pan troglodytes': ('EN', None, None),
    'Panthera leo': ('VU', None, None),
    'Panthera pardus orientalis': ('VU', 'Panthera pardus', 'assessed for the species Panthera pardus, not the subspecies'),
    'Panthera tigris tigris': ('EN', 'Panthera tigris', 'assessed for the species Panthera tigris, not the subspecies'),
    'Panthera uncia': ('VU', None, None),
    'Papio ursinus': ('LC', None, None),
    'Phalacrocorax nigrogularis': ('VU', None, None),
    'Platalea ajaja': ('LC', None, None),
    'Platysaurus broadleyi': ('LC', None, None),
    'Poecilia mexicana': ('LC', None, None),
    'Porcula salvania': ('EN', None, None),
    'Procapra gutturosa': ('LC', None, None),
    'Pudu puda': ('NT', None, None),
    'Puma concolor': ('LC', None, None),
    'Quelea quelea': ('LC', None, None),
    'Rangifer tarandus': ('VU', None, None),
    'Rhincodon typus': ('EN', None, None),
    'Rhinopithecus roxellana': ('EN', None, None),
    'Sequoia sempervirens': ('EN', None, None),
    'Sibirionetta formosa': ('LC', None, None),
    'Stercorarius maccormicki': ('LC', 'Catharacta maccormicki', 'assessed under Catharacta maccormicki'),
    'Strix nebulosa': ('LC', None, None),
    'Symphalangus syndactylus': ('EN', None, None),
    'Theropithecus gelada': ('LC', None, None),
    'Thunnus albacares': ('LC', None, None),
    'Tursiops aduncus': ('NT', None, None),
    'Ursus arctos horribilis': ('LC', 'Ursus arctos', 'assessed for the species Ursus arctos, not the subspecies'),
    'Ursus maritimus': ('VU', None, None),
    'Vulpes ferrilata': ('LC', None, None),
    'Vulpes lagopus': ('LC', None, None),
    'Vulpes zerda': ('LC', None, None),
}
