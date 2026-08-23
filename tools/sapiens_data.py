#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sapiens_data.py
===============

Datasets for an interactive map of the peopling of the world by Homo sapiens,
with a logarithmic time slider from 300,000 years before present to today.

Contents
--------
    ARRIVALS                  first secure attestation of H. sapiens per region
    ARRIVAL_RANGES            published date span (min/max) for each region
    CONTESTED                 why a given arrival date is disputed
    POPULATION                world population through time (one point per date)
    POPULATION_RANGES         published low/high span where sources give one
    SOURCE_DISAGREEMENTS      places where recognised sources differ by >2x
    POPULATION_BY_CONTINENT   {continent: population} snapshots through time
    DEEP_PAST_GENETICS        effective-population-size / bottleneck claims
    SOURCES                   every URL actually consulted while building this
    CAVEATS                   what could not be verified

Time convention
---------------
All `ybp` values are YEARS BEFORE PRESENT with PRESENT = AD 1950, the standard
"cal BP" datum used by every archaeological source quoted here.  Calendar years
convert as  ybp = 1950 - year_AD,  so AD 2026 is ybp = -76.  For a log slider,
shift by BP_TO_2026_OFFSET (= 76) to get "years before 2026", which keeps every
value positive; on a 300,000-year log axis the shift is invisible before the
Holocene and only matters for the last few entries.

Honesty rules applied throughout
--------------------------------
* No number in this file was invented.  Every figure traces to the URL named in
  the comment above its block, all of which were fetched while building this.
* Where the literature offers a range rather than a point, the range is given.
* Where two recognised sources disagree by more than a factor of two, both are
  given and the pair is listed in SOURCE_DISAGREEMENTS.
* Where a figure is a modelled guess rather than a measurement, the comment
  says so.
* Things that could not be verified are listed in CAVEATS, not silently fixed.

Run `python3 sapiens_data.py` to print a summary and assert internal consistency.
"""

from __future__ import annotations

BP_DATUM_YEAR = 1950          # "present" for all ybp values below
BP_TO_2026_OFFSET = 76        # add this to get years before AD 2026
DATASET_BUILT = "2026-08-23"


def year_ad_to_ybp(year_ad: int) -> int:
    """Calendar year AD -> years before present (present = AD 1950)."""
    return BP_DATUM_YEAR - year_ad


def ybp_to_2026(ybp: float) -> float:
    """Shift a cal-BP-1950 value onto a 'years before 2026' axis (always > 0)."""
    return ybp + BP_TO_2026_OFFSET


# =============================================================================
# 1. ARRIVALS
# =============================================================================
#
# Tuple layout, in the order requested:
#     (region, latitude, longitude, ybp, site, confidence, note)
#
# `confidence` is one of:
#     "secure"        widely accepted; multiple methods or direct dating agree
#     "debated"       the date stands but a substantial minority disputes it
#     "contested"     the date is actively rejected by a large part of the field
#     "refuted"       the original claim has been withdrawn or overturned
#
# COORDINATES: latitude/longitude are approximate site locations in decimal
# degrees, adequate for plotting on a world map (~0.1 deg / ~10 km).  Six were
# read from the sources cited below (Klasies River, Ust'-Ishim, Yana RHS,
# Bluefish Caves, Kilu Cave, Monte Verde); the rest are standard published
# locations that were NOT individually re-verified in this research pass.
# See CAVEATS.

ARRIVALS = [

    # --- AFRICA: origin -------------------------------------------------
    # Jebel Irhoud: thermoluminescence age 315 +/- 34 kyr.
    # Source: Hublin et al. 2017, Nature 546:289-292
    #   https://www.nature.com/articles/nature22336
    ("Northwest Africa (Maghreb)", 31.85, -8.87, 315000,
     "Jebel Irhoud, Morocco", "secure",
     "Oldest fossils assigned to the H. sapiens lineage; TL 315 +/- 34 ka; "
     "modern face, archaic braincase, so 'earliest H. sapiens' is partly a "
     "definitional call."),

    # Omo Kibish (Omo I): revised minimum age 233 +/- 22 kyr from the Shala
    # tephra overlying the Kibish Member I. Supersedes the earlier ~197 ka.
    # Source: Vidal et al. 2022, Nature 601:579-583
    #   https://www.nature.com/articles/s41586-021-04275-8
    ("East Africa (Lower Omo, Ethiopia)", 5.40, 35.93, 233000,
     "Omo Kibish (Omo I)", "secure",
     "Oldest anatomically modern human fossil in eastern Africa; minimum age "
     "233 +/- 22 ka, revised upward in 2022 from ~197 ka."),

    # Herto (Homo sapiens idaltu), Middle Awash: 160-154 ka by Ar/Ar.
    # Source: White et al. 2003, Nature 423:742-747
    #   https://www.nature.com/articles/nature01669
    ("East Africa (Middle Awash, Ethiopia)", 10.27, 40.55, 157000,
     "Herto (BOU-VP-16/1)", "secure",
     "Ar/Ar bracketed to 160-154 ka; near-modern crania, described as the "
     "subspecies H. sapiens idaltu."),

    # Klasies River: modern human remains through MSA I-III; the LBS Member
    # (MSA I) is dated 110-90 ka. Coordinates from the same page.
    # Source: https://en.wikipedia.org/wiki/Klasies_River_Caves
    ("Southern Africa", -34.108, 24.390, 100000,
     "Klasies River Caves, South Africa", "secure",
     "50+ modern human fragments across MSA I-III; the oldest (LBS Member) "
     "layer dates 110-90 ka, so the point value here is a mid-range choice."),

    # --- LEVANT: early excursions out of Africa -------------------------
    # Misliya-1 maxilla: 177-194 ka, with Levallois industry.
    # Source: Hershkovitz et al. 2018, Science 359:456-459
    #   https://pubmed.ncbi.nlm.nih.gov/29371468/
    ("Levant (early excursion)", 32.75, 34.97, 185500,
     "Misliya Cave, Israel", "secure",
     "Oldest H. sapiens outside Africa: maxilla dated 194-177 ka; point value "
     "is the midpoint of that published range."),

    # Skhul layer B: ESR 81-101 ka, TL average ~119 ka.
    # Qafzeh: ESR 96-115 ka, TL ~92 ka.
    # Source: https://en.wikipedia.org/wiki/Skhul_and_Qafzeh_hominins
    ("Levant (Skhul/Qafzeh population)", 32.69, 35.31, 110000,
     "Skhul and Qafzeh Caves, Israel", "secure",
     "Large modern-human burial samples; Qafzeh ESR 96-115 ka / TL ~92 ka, "
     "Skhul ESR 81-101 ka / TL ~119 ka. This population appears not to have "
     "contributed to living non-Africans."),

    # Apidima 1: claimed >210 ka early H. sapiens; Apidima 2 >170 ka Neanderthal.
    # Both the taxonomy and the dating have been challenged since 2019.
    # Source: Harvati et al. 2019, Nature 571:500-504
    #   https://www.nature.com/articles/s41586-019-1376-z
    ("Southeast Europe (early excursion)", 36.66, 22.48, 210000,
     "Apidima Cave, Greece", "contested",
     "Apidima 1 claimed as H. sapiens at >210 ka, which would be the earliest "
     "in Eurasia; the specimen is a distorted partial cranium and both its "
     "taxonomy and its age are disputed."),

    # --- ARABIA, SOUTH ASIA, SOUTHEAST ASIA -----------------------------
    # Al Wusta-1 finger bone, Nefud desert: ~85-90 ka, reported as ~88 ka.
    # Source: Groucutt et al. 2018, Nature Ecol. Evol. 2:800-809; commentary at
    #   https://link.springer.com/article/10.1038/s41559-018-0539-x
    ("Arabia", 27.90, 40.60, 88000,
     "Al Wusta, Nefud Desert, Saudi Arabia", "secure",
     "Directly dated H. sapiens intermediate phalanx, ~85-90 ka; oldest "
     "directly dated H. sapiens fossil outside Africa and the Levant."),

    # Fa-Hien Lena: oldest H. sapiens fossils in South Asia, ~48 ka, with
    # bone points interpreted as arrowheads.
    # Sources: https://www.science.org/doi/full/10.1126/sciadv.aba3831
    #          https://en.wikipedia.org/wiki/Fa_Hien_Cave
    ("South Asia", 6.65, 80.21, 48000,
     "Fa-Hien Lena Cave, Sri Lanka", "secure",
     "Oldest securely dated H. sapiens fossils in South Asia (~48 ka). Older "
     "South Asian claims (e.g. Jwalapuram, ~74 ka) rest on stone tools with "
     "no associated hominin fossils."),

    # Lida Ajer teeth, Sumatra: 73,000-63,000 years ago.
    # Source: Westaway et al. 2017, Nature 548:322-325
    #   https://www.nature.com/articles/nature23452
    ("Island Southeast Asia (Sunda)", -0.70, 100.50, 68000,
     "Lida Ajer, Sumatra, Indonesia", "secure",
     "Two modern human teeth in rainforest context dated 73-63 ka; point "
     "value is the midpoint of the published range."),

    # Leang Karampuang narrative panel: minimum age 51,200 years
    # (U-series 53.5 +/- 2.3 ka on overlying calcite).
    # Source: Oktaviana et al. 2024, Nature 631:814-818
    #   https://www.nature.com/articles/s41586-024-07541-7
    ("Wallacea", -4.98, 119.66, 51200,
     "Leang Karampuang, Sulawesi, Indonesia", "secure",
     "Oldest known representational/narrative cave art; U-series minimum age "
     "51,200 yr (53.5 +/- 2.3 ka). Behavioural, not skeletal, evidence."),

    # --- SAHUL: AUSTRALIA AND NEW GUINEA --------------------------------
    # Madjedbebe: OSL-dated occupation "around 65,000 years ago".
    # Source: Clarkson et al. 2017, Nature 547:306-310
    #   https://www.nature.com/articles/nature22968
    # Dispute: Allen & O'Connell argue arrival cannot predate the single
    # Neanderthal admixture pulse at 50,500-43,500 BP, hence <50 ka.
    #   https://archaeologymag.com/2025/07/dna-challenges-timeline-for-human-arrival-in-australia/
    ("Australia (Sahul, earliest claim)", -12.34, 132.92, 65000,
     "Madjedbebe rock shelter, Northern Territory", "contested",
     "OSL puts occupation at ~65 ka; critics argue sandy sediments allowed "
     "artefact movement, and that genomes date Neanderthal admixture to "
     "50,500-43,500 BP, so arrival must be <50 ka. Disputed range 65,000-50,000."),

    # Lake Mungo (Mungo Man / Mungo Lady): ~42,000 years.
    # Source: Bowler et al. 2003 as reported at
    #   https://www.sciencedaily.com/releases/2003/02/030220082107.htm
    ("Australia (secure minimum)", -33.75, 143.10, 42000,
     "Lake Mungo, Willandra Lakes, New South Wales", "secure",
     "Directly dated human burials at ~42 ka; nobody disputes humans were in "
     "Australia by this date, which is why it anchors the conservative view."),

    # Ivane Valley, Papua New Guinea highlands, 2000 m: 49,000-44,000 BP.
    # Source: Summerhayes et al. 2010, Science 330:78-81
    #   https://www.science.org/doi/10.1126/science.1193130
    ("New Guinea (highlands)", -8.50, 147.40, 49000,
     "Ivane Valley, Papua New Guinea", "secure",
     "High-altitude (2000 m) occupation with plant processing, 49-44 ka; "
     "shows rapid inland/upland spread after landfall on Sahul."),

    # --- NEAR OCEANIA ---------------------------------------------------
    # Bismarck Archipelago first settled ~30,000-40,000 years ago;
    # Buang Merabak (New Ireland) cited as the early radiocarbon evidence.
    # Source: https://en.wikipedia.org/wiki/Bismarck_Archipelago
    ("Near Oceania (Bismarck Archipelago)", -3.70, 152.80, 40000,
     "Buang Merabak / Matenkupkum, New Ireland", "secure",
     "First inhabitants ~40,000-30,000 BP; requires open-water crossings "
     "beyond sight of land. Point value is the older end of that range."),

    # Kilu Cave, Buka Island: earliest occupation ~29,000 BP, Pleistocene
    # occupation ~29,000-20,000 BP. Coordinates from the same page.
    # Source: https://en.wikipedia.org/wiki/Kilu_Cave
    ("Near Oceania (Solomon Islands)", -5.336, 154.687, 29000,
     "Kilu Cave, Buka Island", "secure",
     "Earliest occupation in the Solomons; reaching Buka needed a crossing of "
     "at least 60 km of open sea, the oldest such voyage known."),

    # --- EAST ASIA ------------------------------------------------------
    # Tianyuan Cave, near Beijing: 42,000-39,000 years, with ancient DNA.
    # Source: https://en.wikipedia.org/wiki/Tianyuan_man
    ("East Asia (northern China)", 39.68, 115.92, 40000,
     "Tianyuan Cave, Beijing", "secure",
     "Radiocarbon 42-39 ka; ancient DNA confirms a modern human related to "
     "present-day East Asians. The securest early East Asian anchor."),

    # Fuyan Cave (Daoxian): 47 teeth claimed at 80,000-120,000 BP on
    # stalagmite dating; a 2021 aDNA study instead placed remains in the
    # Holocene and questioned the identification of specimen FY-HT2.
    # Sources: Liu et al. 2015, Nature 526:696-699
    #   https://www.nature.com/articles/nature15696
    #   https://en.wikipedia.org/wiki/Fuyan_Cave
    ("South China (early claim)", 25.53, 111.60, 100000,
     "Fuyan Cave, Daoxian, Hunan", "refuted",
     "Claimed 120-80 ka modern human teeth. Later aDNA work redated material "
     "to the Holocene and challenged the identification; treat as overturned "
     "pending publication. Do NOT use as an arrival date."),

    # Japanese archipelago colonised ~38,000 cal BP (Ishinomoto, Kyushu;
    # Idemaruyama, Honshu).
    # Source: Nature Communications (2026) review of the Japanese Palaeolithic
    #   https://www.nature.com/articles/s41467-026-74116-7
    ("Japan (main islands)", 32.80, 130.70, 38000,
     "Ishinomoto (Kyushu) / Idemaruyama (Honshu)", "secure",
     "Two oldest sites both ~38,000 cal BP; skeletal evidence on the main "
     "islands is very scarce, so this rests on lithic assemblages."),

    # Ryukyus: Yamashita-cho Cave I, Okinawa, infant leg bones in sediments
    # dated ~36,500 cal BP; Okinawa colonised by ~36 ka despite the Kuroshio.
    # Sources: https://www.intechopen.com/chapters/89269
    #          https://www.nature.com/articles/s41467-026-74116-7
    ("Ryukyu Islands", 26.21, 127.69, 36500,
     "Yamashita-cho Cave I, Okinawa", "secure",
     "Infant leg bones at ~36.5 ka; reaching Okinawa required crossing the "
     "Kuroshio current, one of the hardest Palaeolithic sea crossings known."),

    # --- EUROPE ---------------------------------------------------------
    # Bacho Kiro Cave: H. sapiens with Initial Upper Palaeolithic assemblage,
    # "before 45 thousand years ago".
    # Source: Hublin et al. 2020, Nature 581:299-302
    #   https://www.nature.com/articles/s41586-020-2259-z
    ("Europe (southeast)", 42.94, 25.42, 45000,
     "Bacho Kiro Cave, Bulgaria", "secure",
     "H. sapiens remains with Initial Upper Palaeolithic tools dated to before "
     "45 ka; the abstract gives no lower bound, so 45,000 is a minimum."),

    # Grotta del Cavallo: two Uluzzian deciduous molars reattributed to
    # anatomically modern humans, ~45,000-43,000 cal BP.
    # Source: Benazzi et al. 2011, Nature 479:525-528
    #   https://www.nature.com/articles/nature10617
    ("Europe (southern)", 40.15, 17.96, 44000,
     "Grotta del Cavallo, Apulia, Italy", "secure",
     "Uluzzian teeth reclassified from Neanderthal to modern human; "
     "45,000-43,000 cal BP. Point value is the midpoint."),

    # Zlatý kůň: oldest reconstructed modern human genome, skull >45,000 years.
    # Source: Prufer et al. 2021, Nature Ecol. Evol. 5:820-825
    #   https://www.nature.com/articles/s41559-021-01443-x
    ("Europe (central)", 49.92, 14.07, 45000,
     "Zlatý kůň, Czechia", "secure",
     "Oldest reconstructed modern human genome; skull over 45,000 years old. "
     "Her lineage left no descendants among later Europeans."),

    # --- SIBERIA AND BERINGIA -------------------------------------------
    # Ust'-Ishim femur: directly radiocarbon dated to ~45,000 years.
    # Coordinates from the same page.
    # Sources: Fu et al. 2014, Nature 514:445-449
    #   https://www.nature.com/articles/nature13810
    #   https://en.wikipedia.org/wiki/Ust%27-Ishim_man
    ("Western Siberia", 57.744, 71.200, 45000,
     "Ust'-Ishim, Omsk Oblast, Russia", "secure",
     "Directly dated femur, ~45 ka, with a high-coverage genome; shows modern "
     "humans were deep in Siberia at the same time they entered Europe."),

    # Yana Rhinoceros Horn Site, 71 deg N: ~32,000 cal BP; human remains
    # ~31,630 cal BP; source population of the 'Ancient North Siberians'.
    # Coordinates from the same page.
    # Source: https://en.wikipedia.org/wiki/Yana_Rhinoceros_Horn_Site
    ("Arctic Siberia", 70.724, 135.430, 32000,
     "Yana Rhinoceros Horn Site, Yakutia", "secure",
     "Occupation above the Arctic Circle at ~32 ka; the two individuals define "
     "the 'Ancient North Siberian' lineage, ancestral in part to Native Americans."),

    # Bluefish Caves: 24,000 BP claimed on cut-marked fauna; contested.
    # Coordinates from the same page.
    # Sources: Bourgeon et al. 2017, PLOS ONE
    #   https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0169486
    #   https://en.wikipedia.org/wiki/Bluefish_Caves
    ("Eastern Beringia (Yukon)", 67.150, -140.583, 24000,
     "Bluefish Caves, Yukon, Canada", "contested",
     "Cut-marked bone dated to ~24 ka. Disputed because the stratigraphic "
     "relation between the dated fauna and any human activity is uncertain."),

    # Swan Point, Tanana Valley, Alaska: occupied since ca. 14,500 cal BP,
    # charcoal radiocarbon dated to ~14,000 BP.
    # Source: https://en.wikipedia.org/wiki/Swan_Point_Archaeological_Site
    ("Eastern Beringia (Alaska)", 64.06, -146.00, 14200,
     "Swan Point, Tanana Valley, Alaska", "secure",
     "Oldest uncontested site in Alaska, occupied from ca. 14,500 cal BP; "
     "microblade technology linking Siberia and the Americas."),

    # --- THE AMERICAS (see CONTESTED for the full argument) --------------
    # White Sands human footprints: 23,000-21,000 years, now supported by
    # three independent methods (seed 14C, terrestrial conifer pollen 14C,
    # and OSL giving a minimum of ~21,500 yr).
    # Sources: Pigati et al. 2023, Science 382:73-75
    #   https://www.science.org/doi/10.1126/science.adh5007
    #   https://www.usgs.gov/news/national-news-release/study-confirms-age-oldest-fossil-human-footprints-north-america
    ("North America (pre-LGM claim)", 32.78, -106.28, 22000,
     "White Sands National Park, New Mexico", "debated",
     "Human footprints dated 23,000-21,000 BP. The original aquatic-seed 14C "
     "dates were attacked over reservoir effects; 2023 pollen 14C and OSL "
     "independently reproduced the age. Still resisted by some archaeologists "
     "because no tools or bones accompany the tracks."),

    # Chiquihuite Cave: claimed occupation to ~26,500 BP, possibly >30,000 BP.
    # Sources: Ardelean et al. 2020, Nature 584:87-92
    #   https://www.nature.com/articles/s41586-020-2509-0
    #   https://en.wikipedia.org/wiki/Chiquihuite_cave
    ("Mexico (pre-LGM claim)", 25.50, -102.00, 26500,
     "Chiquihuite Cave, Zacatecas, Mexico", "contested",
     "Nearly 2000 claimed artefacts from ~26.5 ka, possibly >30 ka. Critics "
     "(Chatters et al. 2021, Davis, Meltzer) argue the 'tools' are geofacts "
     "from limestone roof-fall; no hearths, no butchery, no human DNA."),

    # Monte Verde II, Chile: the classic pre-Clovis site, ~14,500 cal BP.
    # Coordinates from the same page.
    # Source: https://en.wikipedia.org/wiki/Monte_Verde
    ("South America", -41.505, -73.204, 14500,
     "Monte Verde II, Chile", "debated",
     "For 30 years the site that broke Clovis-First: ~14,500 cal BP (14,800 "
     "cal BP average; seaweed directly dated 14,220-13,980 BP). A 2026 study "
     "by Surovell et al. argues the deposits are mid-Holocene (<8,200 BP) and "
     "the Pleistocene material redeposited; Dillehay's team rejects this."),

    # Clovis: 13,050-12,750 cal yr B.P., a ~300-year window.
    # Source: Waters, Stafford & Carlson 2020, Sci. Adv. 6:eaaz0455
    #   https://www.science.org/doi/10.1126/sciadv.aaz0455
    ("North America (Clovis horizon)", 34.28, -103.32, 12900,
     "Blackwater Draw / Clovis, New Mexico", "secure",
     "Clovis technology is now confined to 13,050-12,750 cal BP, only ~300 "
     "years. Once thought to mark first arrival; now clearly a later horizon."),

    # --- THE PACIFIC ----------------------------------------------------
    # Teouma, Efate, Vanuatu: the type cemetery of Lapita expansion into
    # Remote Oceania, ~3000 BP.
    # Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC3944017/
    ("Remote Oceania (Lapita)", -17.75, 168.31, 3000,
     "Teouma, Efate, Vanuatu", "secure",
     "Lapita colonists crossed the Near/Remote Oceania boundary ~3000 BP and "
     "reached Vanuatu, New Caledonia, Fiji, Tonga and Samoa within a few "
     "centuries - the fastest maritime expansion in prehistory to that point."),

    # East Polynesia, phase 1: central East Polynesia (Society Is.)
    # AD ~1025-1120. ybp = 1950 - 1072 (midpoint) = 878.
    # Source: Wilmshurst et al. 2011, PNAS 108:1815-1820
    #   https://pmc.ncbi.nlm.nih.gov/articles/PMC3033267
    ("Central East Polynesia", -17.53, -149.83, 878,
     "Society Islands", "secure",
     "High-precision 14C chronology: colonised AD ~1025-1120, far later than "
     "older estimates. Point value is the midpoint of that range."),

    # East Polynesia, phase 2: the remote archipelagos, AD ~1190-1290.
    # ybp = 1950 - 1240 = 710.
    # Source: Wilmshurst et al. 2011, PNAS 108:1815-1820
    ("Hawaii", 20.70, -156.30, 710,
     "Hawaiian Islands", "debated",
     "Settled in the AD 1190-1290 pulse per Wilmshurst et al. 2011; other "
     "workers (Athens, Kirch) have argued for AD ~1000-1200. Range 950-660 BP."),

    ("Rapa Nui (Easter Island)", -27.12, -109.37, 750,
     "Rapa Nui", "debated",
     "Part of the same AD 1190-1290 pulse; 'short chronology' work places "
     "settlement at AD ~1200. Earlier claims of AD 400-800 are rejected."),

    # New Zealand: North Island AD 1250-1275, South Island AD 1280-1295.
    # ybp = 1950 - 1262 (NI midpoint) = 688.
    # Source: Bunbury, Petchey & Bickler 2022, PNAS
    #   https://pmc.ncbi.nlm.nih.gov/articles/PMC9674228/
    ("New Zealand (Aotearoa)", -41.00, 174.00, 688,
     "Wairau Bar and other early sites", "secure",
     "1558 reliable 14C dates give North Island AD 1250-1275, South Island "
     "AD 1280-1295. The last large habitable landmass on Earth to be settled."),

    # --- LATE ISLAND AND ARCTIC SETTLEMENT ------------------------------
    # Madagascar: systematic 14C review supports human presence by at least
    # 2000 cal BP; early-Holocene arrival "possible" but contextless.
    # Source: Douglass et al. 2019, Quat. Sci. Rev. 221:105878
    #   https://par.nsf.gov/servlets/purl/10129318
    ("Madagascar", -19.00, 46.50, 2000,
     "Coastal and interior sites (14C review)", "debated",
     "Secure human presence by >=2000 cal BP, substantial settlement after "
     "1000 cal BP. Contested early evidence: cut-marked elephant bird bone at "
     "Christmas River, 11,094-10,432 cal BP, with no archaeological context."),

    # Iceland: landnam tephra 871 +/- 2 AD; traditional settlement AD 874.
    # ybp = 1950 - 871 = 1079.
    # Source: https://grokipedia.com/page/Settlement_of_Iceland
    ("Iceland", 64.15, -21.94, 1079,
     "Reykjavik and the landnam tephra horizon", "secure",
     "Norse landnam pinned by the tephra layer dated AD 871 +/- 2; a longhouse "
     "at Stodvarfjordur may date to ~AD 800 but reads as seasonal, not settled."),

    # North American High Arctic and Greenland: Early Palaeo-Inuit / Arctic
    # Small Tool tradition, ~4500 BP to 2800-2300 BP.
    # Source: https://en.wikipedia.org/wiki/Early_Paleo-Eskimo
    ("High Arctic (Canada and Greenland)", 76.00, -45.00, 4500,
     "Independence I and Saqqaq sites", "secure",
     "Early Palaeo-Inuit expansion across the High Arctic and into Greenland "
     "from ~4500 BP - the last habitable region of the Americas occupied."),
]


# -----------------------------------------------------------------------------
# ARRIVAL_RANGES: published span for each region, keyed by region name.
#   region -> (older_bound_ybp, younger_bound_ybp, source note)
# The point value in ARRIVALS always lies inside this span.
# -----------------------------------------------------------------------------
ARRIVAL_RANGES = {
    "Northwest Africa (Maghreb)":        (349000, 281000, "315 +/- 34 ka TL, Hublin et al. 2017"),
    "East Africa (Lower Omo, Ethiopia)": (255000, 211000, "233 +/- 22 ka minimum, Vidal et al. 2022"),
    "East Africa (Middle Awash, Ethiopia)": (160000, 154000, "Ar/Ar bracket, White et al. 2003"),
    "Southern Africa":                   (110000,  90000, "LBS Member (MSA I), Klasies River"),
    "Levant (early excursion)":          (194000, 177000, "Hershkovitz et al. 2018"),
    "Levant (Skhul/Qafzeh population)":  (119000,  81000, "TL and ESR spread across both caves"),
    "Southeast Europe (early excursion)": (250000, 170000, "Apidima 1 '>210 ka'; upper bound not well constrained"),
    "Arabia":                            ( 95000,  85000, "Groucutt et al. 2018, ~88 ka reported"),
    "South Asia":                        ( 50000,  45000, "Fa-Hien Lena, ~48 ka"),
    "Island Southeast Asia (Sunda)":     ( 73000,  63000, "Westaway et al. 2017"),
    "Wallacea":                          ( 55800,  51200, "U-series 53.5 +/- 2.3 ka, minimum age"),
    "Australia (Sahul, earliest claim)": ( 65000,  50000, "Clarkson 2017 vs Allen & O'Connell 2025"),
    "Australia (secure minimum)":        ( 43000,  40000, "Bowler et al. 2003"),
    "New Guinea (highlands)":            ( 49000,  44000, "Summerhayes et al. 2010"),
    "Near Oceania (Bismarck Archipelago)": (40000, 30000, "range as given by summary sources"),
    "Near Oceania (Solomon Islands)":    ( 31500,  29000, "Kilu Cave earliest 14C, calibrated"),
    "East Asia (northern China)":        ( 42000,  39000, "Tianyuan man radiocarbon"),
    "South China (early claim)":         (120000,  80000, "Liu et al. 2015 claim; REFUTED, see CONTESTED"),
    "Japan (main islands)":              ( 39000,  37000, "two oldest sites both ca. 38 ka cal BP"),
    "Ryukyu Islands":                    ( 37000,  36000, "Yamashita-cho Cave I, ~36.5 ka cal BP"),
    "Europe (southeast)":                ( 47000,  45000, "'before 45 ka'; no lower bound in abstract"),
    "Europe (southern)":                 ( 45000,  43000, "Benazzi et al. 2011"),
    "Europe (central)":                  ( 47000,  45000, "'over 45,000 years old', Prufer et al. 2021"),
    "Western Siberia":                   ( 47000,  43000, "direct 14C on the femur, ~45 ka"),
    "Arctic Siberia":                    ( 32500,  31000, "site ~32 ka cal BP; remains ~31,630 cal BP"),
    "Eastern Beringia (Yukon)":          ( 24000,  12000, "24 ka claimed; sceptics allow only terminal Pleistocene"),
    "Eastern Beringia (Alaska)":         ( 14500,  14000, "Swan Point occupation from ca. 14,500 cal BP"),
    "North America (pre-LGM claim)":     ( 23000,  21000, "Bennett 2021, Pigati 2023"),
    "Mexico (pre-LGM claim)":            ( 33000,  13000, "Ardelean 2020; bulk of artefacts 16,600-13,000"),
    "South America":                     ( 14800,   8200, "14,800 cal BP vs Surovell et al. 2026 mid-Holocene claim"),
    "North America (Clovis horizon)":    ( 13050,  12750, "Waters, Stafford & Carlson 2020"),
    "Remote Oceania (Lapita)":           (  3100,   2800, "Lapita expansion, ~3000 BP"),
    "Central East Polynesia":            (   925,    830, "AD 1025-1120, Wilmshurst et al. 2011"),
    "Hawaii":                            (   950,    660, "AD 1000-1290 across Wilmshurst and Athens/Kirch"),
    "Rapa Nui (Easter Island)":          (   760,    660, "AD 1190-1290 pulse; short chronology"),
    "New Zealand (Aotearoa)":            (   700,    655, "AD 1250-1295, Bunbury et al. 2022"),
    "Madagascar":                        ( 11094,   1000, "secure >=2000 BP; contested early-Holocene claim"),
    "Iceland":                           (  1150,   1076, "possible AD ~800 outpost; landnam AD 871 +/- 2"),
    "High Arctic (Canada and Greenland)":(  4500,   2300, "Early Palaeo-Inuit span"),
}


# -----------------------------------------------------------------------------
# CONTESTED: why the disputed arrivals are disputed. Keyed by region.
# -----------------------------------------------------------------------------
CONTESTED = {

    "Southeast Europe (early excursion)":
        "Apidima 1 is a partial, distorted occipital region. Harvati et al. "
        "(2019) read it as early H. sapiens at >210 ka; others read the same "
        "morphology as archaic/Neanderthal-affine and question whether the "
        "U-series age applies to the specimen rather than the breccia.",

    "Australia (Sahul, earliest claim)":
        "ARCHAEOLOGY says ~65 ka: Clarkson et al. (2017) dated the Madjedbebe "
        "artefact bands by OSL with refits and stratigraphic checks. "
        "GENETICS says <50 ka: all non-Africans carry Neanderthal ancestry "
        "from what looks like a single admixture pulse at 50,500-43,500 BP, "
        "and Indigenous Australians carry it too, so Allen & O'Connell argue "
        "they cannot have left Eurasia before that. "
        "COUNTER-COUNTER: 51,200-year-old figurative art on Sulawesi shows "
        "people were already deep in Wallacea very early. "
        "Neither line is decisive; treat 65 ka and 50 ka as live alternatives.",

    "South China (early claim)":
        "Liu et al. (2015) dated 47 teeth from Fuyan Cave to 120-80 ka using "
        "a stalagmite above the deposit. A 2021 ancient-DNA study instead "
        "placed the material in the Holocene, and challenged whether specimen "
        "FY-HT2 is even human. The claim should be treated as overturned.",

    "Eastern Beringia (Yukon)":
        "Bluefish Caves' 24 ka age rests on cut-marked animal bone. The "
        "objection is that the dated bones and the supposed human "
        "modifications are not demonstrably in the same event: the cave fill "
        "is bioturbated, and carnivore gnawing can mimic butchery marks.",

    "North America (pre-LGM claim)":
        "White Sands: the 2021 dates came from Ruppia cirrhosa seeds, an "
        "aquatic plant that can take up old dissolved carbon and read too "
        "old (a hard-water reservoir effect). In 2023 the team dated ~75,000 "
        "terrestrial conifer pollen grains by 14C and independently ran OSL "
        "on quartz, giving a minimum of ~21,500 yr; all three agree. Residual "
        "scepticism is now less about the dates than about the implication: "
        "if people were in New Mexico at 22 ka, they crossed before the "
        "ice-free corridor opened and left almost no other trace for 8,000 years.",

    "Mexico (pre-LGM claim)":
        "Chiquihuite Cave: the excavators report ~2,000 flaked limestone "
        "objects from levels dated to 33-26.5 ka. Chatters et al. (2021), "
        "Davis and Meltzer argue these are geofacts produced by roof-fall in "
        "a limestone cave, note the absence of blade cores, tertiary flakes, "
        "hearths, storage pits and butchered bone, and note that no human DNA "
        "was recovered from the sediments.",

    "South America":
        "Monte Verde II was the site that ended Clovis-First, at ~14,500 cal "
        "BP, verified by a site visit from sceptics in 1997. In 2026 Surovell "
        "et al. argued from stratigraphy that the deposits are middle "
        "Holocene, no older than 8,200 BP, with Pleistocene organics "
        "redeposited. Dillehay's team replies that the new work extrapolates "
        "from sections away from the site itself. This is unresolved as of "
        "the build date of this file.",

    "Madagascar":
        "Cut marks on elephant bird bone from Christmas River give 11,094-"
        "10,432 cal BP, and other bones give 6,435-6,282 cal BP. There is no "
        "associated settlement, hearth or tool assemblage anywhere near those "
        "dates, and the earliest unambiguous occupation is ~2000 cal BP with "
        "villages only after ~1000 cal BP. Either a very sparse early presence "
        "left almost nothing, or the cut marks are misidentified.",
}

# Summary of the Americas debate, for a map caption.
AMERICAS_DEBATE = (
    "Three positions are live. (1) CLOVIS-FIRST, now a minority view: entry "
    "~13,000 BP, Clovis technology 13,050-12,750 cal BP. (2) PRE-CLOVIS "
    "CONSENSUS: entry by ~15,000-16,000 BP, anchored on Monte Verde "
    "(~14,500 cal BP) and several North American sites; this is the "
    "mainstream position. (3) LAST-GLACIAL-MAXIMUM ENTRY: entry by "
    "~23,000-21,000 BP, anchored on the White Sands footprints, with "
    "Chiquihuite Cave and Bluefish Caves as weaker support. "
    "What is contested and why: the LGM position requires people to have "
    "crossed before the ice-free corridor opened and before the coastal route "
    "was clearly viable, and to have left essentially no genetic or "
    "archaeological signal for the following 8,000 years - whereas every "
    "sequenced ancient American genome descends from a founder population "
    "that split from Siberians around 23,000-20,000 BP and diversified in the "
    "Americas only after ~16,000 BP. So the footprint dates and the genomes "
    "have not been reconciled."
)


# =============================================================================
# 2. POPULATION: world population through time
# =============================================================================
#
# Tuple layout: (ybp, world_population, source)
#
# Two different KINDS of number appear here and must not be confused:
#   * EFFECTIVE population size (Ne) - a genetic parameter, typically an order
#     of magnitude or more BELOW the census population. Marked "[Ne]".
#   * CENSUS population - an actual headcount estimate. Marked "[census]".
# For drawing a headcount curve, use POPULATION_CENSUS below, not POPULATION.

POPULATION = [

    # ---- Deep past: genetic inference, NOT headcounts --------------------
    # Hu et al. 2023: FitCoal analysis of 3,154 genomes infers ~1,280 breeding
    # individuals for ~117,000 years, between ~930,000 and ~813,000 years ago,
    # with ~65.85% of genetic diversity lost. THIS RESULT IS CONTESTED.
    # Source: Hu et al. 2023, Science 381:979-984
    #   https://www.science.org/doi/10.1126/science.abq7487
    #   https://www.sci.news/othersciences/anthropology/pleistocene-human-bottleneck-12232.html
    (930000, 1280,
     "Hu et al. 2023, Science [Ne] CONTESTED - start of claimed bottleneck"),
    (813000, 1280,
     "Hu et al. 2023, Science [Ne] CONTESTED - end of claimed bottleneck"),

    # Long-term human effective population size, 10,000-20,000, from the
    # standard reviews. This is the classic textbook figure and is not
    # controversial - but again, it is Ne, not a headcount.
    # Source: Charlesworth 2009, Nat. Rev. Genet., citing Voight et al. 2005
    # and Wall & Przeworski 2000, via
    #   https://bionumbers.hms.harvard.edu/bionumber.aspx?id=113339
    (300000, 10000,
     "Charlesworth 2009 review (Voight 2005; Wall & Przeworski 2000) [Ne] "
     "long-term human Ne 10,000-20,000; lower bound used here"),
    (100000, 10000,
     "Charlesworth 2009 review [Ne] long-term Ne, same range"),

    # The Toba bottleneck claim: ~10,000 individuals after the ~74 ka
    # eruption. Included ONLY because it is famous. It is unsupported: no
    # genetic analysis finds a bottleneck at that date, the SO2 injection was
    # overestimated by 1-2 orders of magnitude, and the Indian and Sumatran
    # archaeological records show no interruption.
    # Source: https://www.johnhawks.net/p/the-so-called-toba-bottleneck-didnt-happen
    (74000, 10000,
     "Toba bottleneck hypothesis (Ambrose 1998) [Ne] REJECTED - retained for "
     "reference only; do not plot as fact"),

    # An out-of-Africa founder-effect bottleneck around 50 ka IS supported.
    # Source: https://www.johnhawks.net/p/the-so-called-toba-bottleneck-didnt-happen
    (50000, 10000,
     "Out-of-Africa founder effect ~50 ka (Hawks, summarising genetic "
     "literature) [Ne] - the bottleneck that is actually supported"),

    # ---- Last Glacial Maximum: the first real headcount estimate ---------
    # Gautney & Holliday 2015 mapped habitable land at the LGM (22-19 ka;
    # ~77 million km2 for Eurasia + Africa + Australia) and applied two
    # density models. The two models differ by ~4x; both are given.
    # Source: Gautney & Holliday 2015, J. Archaeol. Sci.
    #   https://www.academia.edu/11950956/New_estimations_of_habitable_land_area_and_human_population_size_at_the_Last_Glacial_Maximum
    (21000, 2117000,
     "Gautney & Holliday 2015, J. Archaeol. Sci. [census] carnivore-density "
     "model, low end of 2,117,000-2,955,000; authors prefer this model. "
     "Hunter-gatherer-density model gives 3,046,000-8,307,000. Both are "
     "upper-end estimates assuming all habitable land was occupied."),

    # ---- HYDE 3.3 via Our World in Data ---------------------------------
    # HYDE is the standard gridded historical population reconstruction and is
    # what OWID uses for everything before AD 1800. Its pre-agricultural
    # numbers are back-extrapolations, NOT observations - see CAVEATS.
    # Source: HYDE v3.3 (2023), served by Our World in Data
    #   https://ourworldindata.org/grapher/population
    (11950,    4501152, "HYDE 3.3 via OWID [census] 10,000 BC"),
    (10950,    5687125, "HYDE 3.3 via OWID [census] 9,000 BC"),
    ( 9950,    7314623, "HYDE 3.3 via OWID [census] 8,000 BC"),
    ( 8950,    9651703, "HYDE 3.3 via OWID [census] 7,000 BC"),
    ( 7950,   13278309, "HYDE 3.3 via OWID [census] 6,000 BC"),
    ( 6950,   19155698, "HYDE 3.3 via OWID [census] 5,000 BC"),
    ( 5950,   28859174, "HYDE 3.3 via OWID [census] 4,000 BC"),
    ( 4950,   44577880, "HYDE 3.3 via OWID [census] 3,000 BC"),
    ( 3950,   72685064, "HYDE 3.3 via OWID [census] 2,000 BC"),
    ( 2950,  110530464, "HYDE 3.3 via OWID [census] 1,000 BC"),
    ( 1950,  232268832, "HYDE 3.3 via OWID [census] AD 1"),
    ( 1850,  237052192, "HYDE 3.3 via OWID [census] AD 100"),
    (  950,  323462624, "HYDE 3.3 via OWID [census] AD 1000"),
    (  850,  397889888, "HYDE 3.3 via OWID [census] AD 1100"),
    (  750,  444653984, "HYDE 3.3 via OWID [census] AD 1200"),
    (  650,  456248096, "HYDE 3.3 via OWID [census] AD 1300 - pre-plague peak"),
    (  550,  442309216, "HYDE 3.3 via OWID [census] AD 1400 - after the Black Death"),
    (  450,  503051104, "HYDE 3.3 via OWID [census] AD 1500"),
    (  350,  516147616, "HYDE 3.3 via OWID [census] AD 1600"),
    (  250,  595456896, "HYDE 3.3 via OWID [census] AD 1700"),

    # ---- 1800-1949: Gapminder v7 (2022) via OWID ------------------------
    #   https://ourworldindata.org/grapher/population
    (  150,  983104755, "Gapminder v7 via OWID [census] AD 1800"),
    (   50, 1627273655, "Gapminder v7 via OWID [census] AD 1900"),

    # ---- 1950-2023: UN World Population Prospects 2024 via OWID ---------
    #   https://ourworldindata.org/grapher/population
    (    0, 2493092852, "UN WPP 2024 via OWID [census] AD 1950"),
    (  -25, 4070735279, "UN WPP 2024 via OWID [census] AD 1975"),
    (  -50, 6171702992, "UN WPP 2024 via OWID [census] AD 2000"),
    (  -60, 7021732143, "UN WPP 2024 via OWID [census] AD 2010"),
    (  -70, 7887001289, "UN WPP 2024 via OWID [census] AD 2020"),
    (  -73, 8091734933, "UN WPP 2024 via OWID [census] AD 2023"),

    # ---- Present day -----------------------------------------------------
    # UN WPP 2024 revision, mid-year projections. Read from a secondary
    # aggregator of the UN series, not from the UN site directly - see CAVEATS.
    #   https://statisticstimes.com/demographics/world-population.php
    (  -75, 8231613070, "UN WPP 2024 revision [census] AD 2025"),
    (  -76, 8300678395, "UN WPP 2024 revision [census] AD 2026 (1 July, projected)"),
]

# Headcount-only subset, safe to plot as a population curve.
POPULATION_CENSUS = [row for row in POPULATION if "[census]" in row[2]]


# -----------------------------------------------------------------------------
# POPULATION_RANGES: ybp -> (low, high, source)
# Published low/high spans. Use these for an uncertainty band.
# US Census Bureau "Historical Estimates of World Population" gives a Lower and
# Upper envelope across Biraben, Durand, Haub, McEvedy & Jones, Thomlinson and
# the UN. Where Lower == Upper the table shows a single value.
#   https://www.census.gov/data/tables/time-series/demo/international-programs/historical-est-worldpop.html
# -----------------------------------------------------------------------------
POPULATION_RANGES = {
    930000: (1270,         1300,        "Hu et al. 2023 [Ne], ~1,280 breeding individuals; CONTESTED"),
    300000: (10000,        20000,       "Charlesworth 2009 review [Ne], long-term human Ne"),
     21000: (2117000,      8307000,     "Gautney & Holliday 2015 [census]; carnivore model 2.12-2.96M, "
                                        "hunter-gatherer model 3.05-8.31M - the two models differ ~4x"),
     11950: (1000000,      10000000,    "US Census Bureau envelope for 10,000 BC (1-10 million); "
                                        "the Bureau itself notes uncertainty of up to an order of magnitude"),
      9950: (5000000,      7314623,     "US Census Bureau 8,000 BC = 5 million (single value); HYDE 3.3 = 7.31 million"),
      6950: (5000000,      20000000,    "US Census Bureau 5,000 BC lower 5M / upper 20M; HYDE 3.3 = 19.16 million"),
      5950: (7000000,      28859174,    "US Census Bureau 4,000 BC = 7 million (single value); HYDE 3.3 = 28.86 million"),
      4950: (14000000,     44577880,    "US Census Bureau 3,000 BC = 14 million (single value); HYDE 3.3 = 44.58 million"),
      3950: (27000000,     72685064,    "US Census Bureau 2,000 BC = 27 million (single value); HYDE 3.3 = 72.69 million"),
      2950: (50000000,     110530464,   "US Census Bureau 1,000 BC = 50 million (single value); HYDE 3.3 = 110.53 million"),
      2450: (100000000,    100000000,   "US Census Bureau 500 BC = 100 million (single value); HYDE has no 500 BC step"),
      2150: (150000000,    231000000,   "US Census Bureau 200 BC, lower 150M / upper 231M"),
      1950: (170000000,    400000000,   "US Census Bureau AD 1, lower 170M / upper 400M; Haub 1995 says ~300M; HYDE 3.3 = 232M"),
       950: (254000000,    345000000,   "US Census Bureau AD 1000; HYDE 3.3 = 323M"),
       750: (360000000,    450000000,   "US Census Bureau AD 1200; HYDE 3.3 = 445M"),
       700: (400000000,    416000000,   "US Census Bureau AD 1250"),
       610: (443000000,    443000000,   "US Census Bureau AD 1340 (single value), immediately pre-Black Death"),
       550: (350000000,    442309216,   "US Census Bureau AD 1400 envelope is 350-374M; HYDE 3.3 gives "
                                        "442.3M, ABOVE the Census envelope. Range widened to hold both."),
       450: (425000000,    540000000,   "US Census Bureau AD 1500; HYDE 3.3 = 503M, inside the envelope"),
       350: (516147616,    579000000,   "US Census Bureau AD 1600 envelope is 545-579M; HYDE 3.3 gives "
                                        "516.1M, BELOW the envelope. Range widened to hold both."),
       300: (470000000,    545000000,   "US Census Bureau AD 1650"),
       250: (595456896,    679000000,   "US Census Bureau AD 1700 envelope is 600-679M; HYDE 3.3 gives "
                                        "595.5M, just BELOW the envelope. Range widened to hold both."),
       200: (629000000,    961000000,   "US Census Bureau AD 1750; HYDE 3.3 continent sum = 753M"),
       150: (813000000,    1125000000,  "US Census Bureau AD 1800; Gapminder/OWID = 983M"),
       100: (1128000000,   1402000000,  "US Census Bureau AD 1850; Gapminder/OWID continent sum = 1,276M"),
        50: (1550000000,   1762000000,  "US Census Bureau AD 1900; Gapminder/OWID = 1,627M"),
         0: (2400000000,   2558000000,  "US Census Bureau AD 1950; UN WPP 2024 = 2,493M"),
}


# -----------------------------------------------------------------------------
# SOURCE_DISAGREEMENTS: every place where two recognised sources differ by
# more than a factor of two. Layout:
#   (label, ybp, source_a, value_a, source_b, value_b, comment)
# The ratio is recomputed and re-checked in validate().
# -----------------------------------------------------------------------------
FACTOR_THRESHOLD = 2.0

SOURCE_DISAGREEMENTS = [

    ("Last Glacial Maximum", 21000,
     "Gautney & Holliday 2015, carnivore-density model (low)", 2117000,
     "Gautney & Holliday 2015, hunter-gatherer-density model (high)", 8307000,
     "A ~3.9x spread inside a single paper. The authors prefer the lower "
     "figure, arguing that ethnographic hunter-gatherer densities overestimate "
     "Pleistocene ones because those people lacked comparable technology."),

    ("5000 BC", 6950,
     "US Census Bureau envelope, lower", 5000000,
     "HYDE 3.3 via OWID", 19155698,
     "3.8x. HYDE's Neolithic curve runs well above the McEvedy-and-Jones-style "
     "estimates that set the Census Bureau's lower bound. The Census upper "
     "bound (20M) does contain HYDE."),

    ("4000 BC", 5950,
     "US Census Bureau (single value)", 7000000,
     "HYDE 3.3 via OWID", 28859174,
     "4.1x. Same structural disagreement: HYDE models spatial land use, the "
     "classical demographers extrapolated from later documented populations."),

    ("3000 BC", 4950,
     "US Census Bureau (single value)", 14000000,
     "HYDE 3.3 via OWID", 44577880,
     "3.2x."),

    ("2000 BC", 3950,
     "US Census Bureau (single value)", 27000000,
     "HYDE 3.3 via OWID", 72685064,
     "2.7x."),

    ("1000 BC", 2950,
     "US Census Bureau (single value)", 50000000,
     "HYDE 3.3 via OWID", 110530464,
     "2.2x. This is the last pre-Roman date where the two traditions differ "
     "by more than a factor of two; by AD 1 they overlap."),

    ("10,000 BC", 11950,
     "US Census Bureau envelope, lower", 1000000,
     "US Census Bureau envelope, upper", 10000000,
     "10x, inside a single compilation. The Bureau itself flags 'uncertainty "
     "of up to an order of magnitude' for this date. HYDE 3.3 gives 4.50M, "
     "comfortably inside."),
]

# Disagreements below the 2x threshold that are still worth showing on a map,
# because they are the ones a reader is most likely to notice.
SOURCE_NOTES_SUBTHRESHOLD = [
    ("AD 1400", 550, "US Census Bureau upper", 374000000, "HYDE 3.3", 442309216,
     "1.18x. Both traditions agree the Black Death cut world population; they "
     "disagree on how much of it was recovered by 1400."),
    ("AD 1", 1950, "US Census Bureau lower", 170000000, "US Census Bureau upper", 400000000,
     "2.35x within the Census envelope itself - but this is a spread across "
     "compilations, not two specific sources, so it is listed here rather "
     "than in SOURCE_DISAGREEMENTS."),
]


# =============================================================================
# 3. POPULATION BY CONTINENT
# =============================================================================
#
# Tuple layout: (ybp, {continent: population})
#
# Source: HYDE v3.3 (2023) for -10000 to AD 1799, Gapminder v7 (2022) for
# AD 1800-1949, UN World Population Prospects 2024 for AD 1950 onward,
# all as served by Our World in Data:
#   https://ourworldindata.org/grapher/population
# OWID uses HYDE's own continental aggregates before 1800 rather than summing
# countries, so these are HYDE's regional numbers as published.
#
# CONTINENT DEFINITIONS are OWID's: "North America" includes Central America
# and the Caribbean; "Oceania" includes Australia, New Guinea and the Pacific
# islands; "Asia" includes the Middle East and Russia east of the Urals.
#
# BEFORE AGRICULTURE these numbers are NOT observations. HYDE back-projects
# from later documented populations using land-use models; nobody has counted
# Pleistocene or early-Holocene foragers. In particular HYDE puts ~1.18 million
# people in North America and ~1.10 million in South America at 10,000 BC,
# which is far higher than most archaeologists would accept for a continent
# occupied for at most a few thousand years by then, and it puts only ~229,000
# in Africa, which is far too low relative to the archaeological record. Treat
# the pre-Neolithic continental split as a modelled guess with an uncertainty
# of at least an order of magnitude, and say so on the map.

CONTINENTS = ("Africa", "Asia", "Europe", "North America", "South America", "Oceania")

POPULATION_BY_CONTINENT = [

    # --- HYDE 3.3, 10,000 BC. MODELLED GUESS, see block comment above. ---
    (11950, {"Africa": 228973, "Asia": 1183783, "Europe": 481591,
             "North America": 1184755, "South America": 1097849, "Oceania": 324198}),

    # --- HYDE 3.3, 8,000 BC (~10,000 BP). Early Neolithic. Still modelled. --
    (9950,  {"Africa": 465827, "Asia": 2405903, "Europe": 730273,
             "North America": 1731102, "South America": 1645189, "Oceania": 336328}),

    # --- HYDE 3.3, 5,000 BC (~7,000 BP). ---------------------------------
    (6950,  {"Africa": 1453426, "Asia": 9452731, "Europe": 1609853,
             "North America": 3122403, "South America": 3129050, "Oceania": 388233}),

    # --- HYDE 3.3, 3,000 BC (~5,000 BP). Requested "5000 BP" anchor. ------
    (4950,  {"Africa": 4026815, "Asia": 26806386, "Europe": 3673248,
             "North America": 4686073, "South America": 4904763, "Oceania": 480593}),

    # --- HYDE 3.3, 2,000 BC (~4,000 BP). ---------------------------------
    (3950,  {"Africa": 6093084, "Asia": 46901344, "Europe": 7190463,
             "North America": 5761597, "South America": 6174712, "Oceania": 563863}),

    # --- HYDE 3.3, 1,000 BC (~3,000 BP). Requested "3000 BP" anchor. ------
    (2950,  {"Africa": 9034441, "Asia": 72722528, "Europe": 13127987,
             "North America": 7101145, "South America": 7846103, "Oceania": 698260}),

    # --- HYDE 3.3, AD 1 (~2,000 BP). Requested "2000 BP (year 1)" anchor. -
    (1950,  {"Africa": 14870035, "Asia": 165488624, "Europe": 32221408,
             "North America": 8774224, "South America": 10025976, "Oceania": 888568}),

    # --- HYDE 3.3, AD 1000 (~1,000 BP). ----------------------------------
    (950,   {"Africa": 39869508, "Asia": 209186032, "Europe": 36341940,
             "North America": 18008338, "South America": 18808200, "Oceania": 1248621}),

    # --- HYDE 3.3, AD 1400. Post-Black-Death Europe. ---------------------
    (550,   {"Africa": 54830016, "Asia": 270937184, "Europe": 60722988,
             "North America": 27685150, "South America": 26651362, "Oceania": 1482524}),

    # --- HYDE 3.3, AD 1500 (~500 BP). Eve of European contact. -----------
    (450,   {"Africa": 58613540, "Asia": 303879520, "Europe": 78614656,
             "North America": 30472692, "South America": 29863142, "Oceania": 1607577}),

    # --- HYDE 3.3, AD 1600. The American depopulation, in one step. ------
    # HYDE takes the Americas from ~60.3M in 1500 to ~10.2M in 1600, a fall of
    # about 83%. The 1500 baseline (~60M for both Americas) sits at the high
    # end of the published range; Denevan's widely used figure is ~54M and
    # older estimates run as low as ~13M, so both the pre-contact level and
    # the depth of the collapse carry large uncertainty.
    (350,   {"Africa": 68577456, "Asia": 334114560, "Europe": 101501416,
             "North America": 3834259, "South America": 6380525, "Oceania": 1739404}),

    # --- HYDE 3.3, AD 1700 (~300 BP). ------------------------------------
    (250,   {"Africa": 78557832, "Asia": 386909664, "Europe": 115422248,
             "North America": 6791309, "South America": 5901817, "Oceania": 1873995}),

    # --- HYDE 3.3, AD 1750. ----------------------------------------------
    (200,   {"Africa": 79382032, "Asia": 498699232, "Europe": 154836912,
             "North America": 11430595, "South America": 7012592, "Oceania": 1917932}),

    # --- Gapminder v7, AD 1800 (~200 BP). --------------------------------
    (150,   {"Africa": 81273172, "Asia": 683181540, "Europe": 192912782,
             "North America": 14838618, "South America": 9277957, "Oceania": 1620686}),

    # --- Gapminder v7, AD 1850. ------------------------------------------
    (100,   {"Africa": 112301163, "Asia": 825539753, "Europe": 276591094,
             "North America": 39876476, "South America": 19261504, "Oceania": 2032905}),

    # --- Gapminder v7, AD 1900 (~100 BP). --------------------------------
    (50,    {"Africa": 138755559, "Asia": 931021418, "Europe": 405874841,
             "North America": 104337584, "South America": 41330741, "Oceania": 5953511}),

    # --- UN WPP 2024, AD 1950. -------------------------------------------
    (0,     {"Africa": 227776838, "Asia": 1367581793, "Europe": 549374181,
             "North America": 222818942, "South America": 112973206, "Oceania": 12582453}),

    # --- UN WPP 2024, AD 1975. -------------------------------------------
    (-25,   {"Africa": 418322666, "Asia": 2388510805, "Europe": 677953491,
             "North America": 349224556, "South America": 215072895, "Oceania": 21555937}),

    # --- UN WPP 2024, AD 2000. -------------------------------------------
    (-50,   {"Africa": 830226481, "Asia": 3746832777, "Europe": 729129967,
             "North America": 485805117, "South America": 348018743, "Oceania": 31352968}),

    # --- UN WPP 2024, AD 2023. The most recent continental split available
    # in this dataset; use it as "today". The world total for 2026 is
    # 8,300,678,395 (UN WPP 2024 projection), about 2.6% above the 2023 sum.
    (-73,   {"Africa": 1479690254, "Asia": 4776659631, "Europe": 746966209,
             "North America": 608770547, "South America": 433024223, "Oceania": 45563135}),
]


# =============================================================================
# 4. DEEP-PAST GENETICS: structured version of the bottleneck claims
# =============================================================================
# (label, older_ybp, younger_ybp, ne_estimate, status, source, note)

DEEP_PAST_GENETICS = [

    ("Early-to-Middle Pleistocene bottleneck", 930000, 813000, 1280, "contested",
     "Hu et al. 2023, Science 381:979-984 — https://www.science.org/doi/10.1126/science.abq7487",
     "FitCoal on 3,154 genomes: ~1,280 breeding individuals for ~117,000 "
     "years, ~65.85% of genetic diversity lost. CONTESTED: Cousins & "
     "Durvasula (Mol. Biol. Evol. 2025) show a simpler model (mushi) fits the "
     "data better by 1,084 log-likelihood units; PSMC, Relate and SMC++ do "
     "not detect the bottleneck although simulations say they should; and it "
     "is found in African but not out-of-Africa samples, which is implausible "
     "for a pre-dispersal event. They suggest ancestral population STRUCTURE "
     "misread as a bottleneck. "
     "https://academic.oup.com/mbe/article/42/2/msaf041/8005733"),

    ("Long-term human effective population size", 300000, 20000, 10000, "accepted",
     "Charlesworth 2009, Nat. Rev. Genet., citing Voight et al. 2005 and Wall "
     "& Przeworski 2000 — https://bionumbers.hms.harvard.edu/bionumber.aspx?id=113339",
     "Ne of 10,000-20,000 over the long run. This is a harmonic-mean-like "
     "genetic quantity, well below the census population, and reflects a long "
     "history of small numbers plus recent expansion."),

    ("Toba volcanic bottleneck", 74000, 74000, 10000, "rejected",
     "Ambrose 1998 hypothesis; refutation summarised by John Hawks — "
     "https://www.johnhawks.net/p/the-so-called-toba-bottleneck-didnt-happen",
     "The claim that Toba cut humanity to ~10,000 individuals is unsupported: "
     "no genetic analysis finds a bottleneck at 74 ka, Toba's SO2 injection "
     "was overestimated by one to two orders of magnitude in the original "
     "climate simulations, and Indian and Sumatran archaeological sequences "
     "show no interruption."),

    ("Out-of-Africa founder effect", 60000, 50000, 10000, "accepted",
     "Summarised by John Hawks — "
     "https://www.johnhawks.net/p/the-so-called-toba-bottleneck-didnt-happen",
     "A genuine bottleneck around 50 ka, caused by a founder effect in the "
     "population that left Africa, not by a global catastrophe. Also a "
     "possible earlier bottleneck at 150-130 ka."),
]


# =============================================================================
# 5. SOURCES ACTUALLY USED
# =============================================================================

SOURCES = [
    # Africa
    "https://www.nature.com/articles/nature22336",                       # Jebel Irhoud, Hublin 2017
    "https://www.nature.com/articles/s41586-021-04275-8",                # Omo Kibish, Vidal 2022
    "https://www.nature.com/articles/nature01669",                       # Herto, White 2003
    "https://en.wikipedia.org/wiki/Klasies_River_Caves",                 # Klasies River
    # Levant and early excursions
    "https://pubmed.ncbi.nlm.nih.gov/29371468/",                         # Misliya, Hershkovitz 2018
    "https://en.wikipedia.org/wiki/Skhul_and_Qafzeh_hominins",           # Skhul / Qafzeh
    "https://www.nature.com/articles/s41586-019-1376-z",                 # Apidima, Harvati 2019
    # Arabia, South Asia, SE Asia
    "https://link.springer.com/article/10.1038/s41559-018-0539-x",       # Al Wusta commentary
    "https://en.wikipedia.org/wiki/Fa_Hien_Cave",                        # Fa-Hien Lena
    "https://www.science.org/doi/full/10.1126/sciadv.aba3831",           # Fa-Hien Lena, Langley 2020
    "https://www.nature.com/articles/nature23452",                       # Lida Ajer, Westaway 2017
    "https://www.nature.com/articles/s41586-024-07541-7",                # Leang Karampuang art
    # Sahul and Near Oceania
    "https://www.nature.com/articles/nature22968",                       # Madjedbebe, Clarkson 2017
    "https://archaeologymag.com/2025/07/dna-challenges-timeline-for-human-arrival-in-australia/",
    "https://www.sciencedaily.com/releases/2003/02/030220082107.htm",    # Lake Mungo, Bowler 2003
    "https://www.science.org/doi/10.1126/science.1193130",               # Ivane Valley, Summerhayes 2010
    "https://en.wikipedia.org/wiki/Bismarck_Archipelago",
    "https://en.wikipedia.org/wiki/Kilu_Cave",
    # East Asia
    "https://en.wikipedia.org/wiki/Tianyuan_man",
    "https://www.nature.com/articles/nature15696",                       # Fuyan Cave claim, Liu 2015
    "https://en.wikipedia.org/wiki/Fuyan_Cave",                          # and its refutation
    "https://www.nature.com/articles/s41467-026-74116-7",                # Japanese Palaeolithic review
    "https://www.intechopen.com/chapters/89269",                         # Ryukyu prehistory
    # Europe
    "https://www.nature.com/articles/s41586-020-2259-z",                 # Bacho Kiro, Hublin 2020
    "https://www.nature.com/articles/nature10617",                       # Grotta del Cavallo, Benazzi 2011
    "https://www.nature.com/articles/s41559-021-01443-x",                # Zlatý kůň, Prüfer 2021
    # Siberia and Beringia
    "https://www.nature.com/articles/nature13810",                       # Ust'-Ishim, Fu 2014
    "https://en.wikipedia.org/wiki/Ust%27-Ishim_man",
    "https://en.wikipedia.org/wiki/Yana_Rhinoceros_Horn_Site",
    "https://en.wikipedia.org/wiki/Bluefish_Caves",
    "https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0169486",
    "https://en.wikipedia.org/wiki/Swan_Point_Archaeological_Site",
    # The Americas
    "https://www.science.org/doi/10.1126/science.adh5007",               # White Sands redating 2023
    "https://www.usgs.gov/news/national-news-release/study-confirms-age-oldest-fossil-human-footprints-north-america",
    "https://www.nature.com/articles/s41586-020-2509-0",                 # Chiquihuite, Ardelean 2020
    "https://en.wikipedia.org/wiki/Chiquihuite_cave",
    "https://www.smithsonianmag.com/science-nature/when-did-humans-reach-america-mexican-mountain-cave-artifacts-raise-new-questions-180975385/",
    "https://en.wikipedia.org/wiki/Monte_Verde",
    "https://phys.org/news/2026-03-monte-verde-fieldwork-resets-age.html",
    "https://www.science.org/doi/10.1126/sciadv.aaz0455",                # Age of Clovis, Waters 2020
    # The Pacific
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC3944017/",                 # Teouma, Vanuatu
    "https://www.journals.uchicago.edu/doi/10.1086/662201",              # Lapita colonisation
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC3033267",                  # Wilmshurst 2011 East Polynesia
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC9674228/",                 # NZ chronology, Bunbury 2022
    # Late island and Arctic settlement
    "https://par.nsf.gov/servlets/purl/10129318",                        # Madagascar 14C review
    "https://grokipedia.com/page/Settlement_of_Iceland",
    "https://en.wikipedia.org/wiki/Early_Paleo-Eskimo",
    # Population
    "https://www.science.org/doi/10.1126/science.abq7487",               # Hu et al. 2023 bottleneck
    "https://www.sci.news/othersciences/anthropology/pleistocene-human-bottleneck-12232.html",
    "https://academic.oup.com/mbe/article/42/2/msaf041/8005733",         # Cousins & Durvasula critique
    "https://bionumbers.hms.harvard.edu/bionumber.aspx?id=113339",       # long-term Ne
    "https://www.johnhawks.net/p/the-so-called-toba-bottleneck-didnt-happen",
    "https://www.academia.edu/11950956/New_estimations_of_habitable_land_area_and_human_population_size_at_the_Last_Glacial_Maximum",
    "https://www.census.gov/data/tables/time-series/demo/international-programs/historical-est-worldpop.html",
    "https://ourworldindata.org/grapher/population",
    "https://ourworldindata.org/population-growth-over-time",
    "https://ourworldindata.org/grapher/population-regions-with-projections",
    "https://brilliantmaps.com/world-pop-10000bc/",                      # HYDE 3.3 10,000 BC cross-check
    "https://statisticstimes.com/demographics/world-population.php",     # UN WPP 2024, 2025-2026
]


# =============================================================================
# 6. CAVEATS - what could not be verified
# =============================================================================

CAVEATS = [
    "McEvedy & Jones (1978), 'Atlas of World Population History', could NOT be "
    "consulted directly - it is not online. Their figures are represented here "
    "only inside the US Census Bureau's Lower/Upper envelope, which aggregates "
    "them with Biraben, Durand, Haub, Thomlinson and the UN. Per-source columns "
    "for the Census table were not retrievable; only the envelope was.",

    "HYDE 3.3 values were read from Our World in Data's CSV export via an "
    "automated page reader, because direct HTTP to ourworldindata.org was "
    "blocked by the sandbox proxy. They were cross-checked two ways: the "
    "10,000 BC continental figures match an independent secondary rendering of "
    "the same HYDE release exactly, and at every timepoint the six continental "
    "values sum to the published world total within 0.05%. validate() re-checks "
    "the second condition. Individual figures should still be re-pulled from "
    "HYDE directly before publication.",

    "Site latitudes and longitudes were verified from the cited sources only "
    "for Klasies River, Ust'-Ishim, Yana RHS, Bluefish Caves, Kilu Cave and "
    "Monte Verde. All other coordinates are standard published locations "
    "carried over without independent re-verification. They are accurate "
    "enough to plot but should not be used for anything else.",

    "Bacho Kiro: Hublin et al. 2020 state only 'before 45 thousand years ago' "
    "in the abstract. The associated radiocarbon paper (Fewlass et al. 2020) "
    "gives a fuller range that was not retrieved here, so the value is a "
    "minimum, not a point estimate.",

    "Madjedbebe: the Nature abstract gives 'around 65,000 years ago' with no "
    "stated uncertainty. A Bayesian age model with an uncertainty term is "
    "published in the paper's supplement, which was not retrieved.",

    "Al Wusta: the primary paper (Groucutt et al. 2018, Nature Ecol. Evol.) "
    "was not directly accessible; the ~85-90 ka figure comes from the linked "
    "News & Views commentary and secondary reports.",

    "Hawaii and Rapa Nui: dates derive from Wilmshurst et al. 2011's "
    "AD 1190-1290 East Polynesian pulse. Island-specific chronology papers "
    "(Athens et al. for Hawaii, Mulrooney/Hunt & Lipo for Rapa Nui) were not "
    "fetched, so the per-island uncertainty is wider than stated.",

    "Toba: the '10,000 individuals' figure comes from a secondary summary of "
    "Ambrose (1998), not the original paper. It is included only because the "
    "claim is famous; it is not supported.",

    "Present-day world population (AD 2025-2026) was read from an aggregator "
    "of the UN WPP 2024 revision, not from the UN's own site. The 2023 value "
    "(8,091,734,933) comes from OWID's UN WPP 2024 series and is the more "
    "solid of the two.",

    "The continental split for 'today' is the AD 2023 snapshot; OWID's "
    "continent series ends at 2023 while the world total is projected to 2026. "
    "The 2023 continent sum is about 2.6% below the 2026 world total.",

    "Pre-Neolithic continental populations in HYDE are model back-projections, "
    "not evidence. HYDE's 10,000 BC figures put more people in the Americas "
    "(2.28 million across both) than in Africa (0.23 million), which almost no "
    "archaeologist would accept. Label them clearly on the map.",

    "Tonga (Nukuleka, ~2,840 cal BP) and other individual Lapita landfalls "
    "were not separately verified and are folded into the single Remote "
    "Oceania entry.",

    "Monte Verde is in active dispute as of this file's build date "
    "(2026-08-23). The Surovell et al. 2026 mid-Holocene claim and Dillehay's "
    "rebuttal were read via secondary reporting; the primary papers were "
    "behind a 403. Re-check before relying on either date.",
]


# =============================================================================
# 7. SELF-VALIDATION
# =============================================================================

VALID_CONFIDENCE = {"secure", "debated", "contested", "refuted"}

OLDEST_AFRICAN_YBP = 315000     # Jebel Irhoud


def validate() -> None:
    """Assert internal consistency. Raises AssertionError on any contradiction."""

    # ---- ARRIVALS: shape and field sanity -------------------------------
    seen_regions = set()
    for row in ARRIVALS:
        assert len(row) == 7, f"ARRIVALS row is not a 7-tuple: {row!r}"
        region, lat, lon, ybp, site, conf, note = row
        assert isinstance(region, str) and region, f"bad region: {row!r}"
        assert region not in seen_regions, f"duplicate region: {region!r}"
        seen_regions.add(region)
        assert -90.0 <= lat <= 90.0, f"latitude out of range for {region}: {lat}"
        assert -180.0 <= lon <= 180.0, f"longitude out of range for {region}: {lon}"
        assert isinstance(ybp, (int, float)), f"ybp not numeric for {region}"
        assert 0 < ybp <= 400000, f"ybp implausible for {region}: {ybp}"
        assert isinstance(site, str) and site, f"missing site for {region}"
        assert conf in VALID_CONFIDENCE, f"bad confidence for {region}: {conf!r}"
        assert isinstance(note, str) and len(note) > 20, f"note too thin for {region}"

    # ---- ARRIVALS: chronological / logical ordering ---------------------
    by_region = {r[0]: r[3] for r in ARRIVALS}

    # Nothing predates the oldest African attestation.
    for region, ybp in by_region.items():
        assert ybp <= OLDEST_AFRICAN_YBP, (
            f"{region} at {ybp} BP predates the oldest African fossil "
            f"({OLDEST_AFRICAN_YBP} BP), which would be a contradiction")

    # Africa holds the maximum.
    oldest_region = max(by_region, key=by_region.get)
    assert oldest_region == "Northwest Africa (Maghreb)", (
        f"oldest arrival should be Jebel Irhoud, got {oldest_region}")

    # Ordered pairs that must hold on any coherent reading of the evidence.
    must_be_older = [
        # (earlier region, later region, why)
        ("East Africa (Lower Omo, Ethiopia)", "Levant (early excursion)",
         "H. sapiens must be in Africa before it is outside it"),
        ("Levant (early excursion)", "Arabia",
         "Misliya predates the Nefud finger bone"),
        ("Island Southeast Asia (Sunda)", "Wallacea",
         "Sunda before Wallacea on any southern-route model"),
        ("Wallacea", "Australia (secure minimum)",
         "Wallacea before the securely dated Australian burials"),
        ("Australia (Sahul, earliest claim)", "Australia (secure minimum)",
         "the earliest claim must be older than the conservative minimum"),
        ("Western Siberia", "Arctic Siberia",
         "Ust'-Ishim predates Yana"),
        ("Arctic Siberia", "Eastern Beringia (Alaska)",
         "Siberia before uncontested Alaska"),
        ("North America (pre-LGM claim)", "North America (Clovis horizon)",
         "White Sands predates Clovis"),
        ("Eastern Beringia (Alaska)", "North America (Clovis horizon)",
         "Swan Point predates Clovis"),
        ("South America", "Remote Oceania (Lapita)",
         "Monte Verde predates the Lapita expansion"),
        ("Near Oceania (Bismarck Archipelago)", "Near Oceania (Solomon Islands)",
         "Bismarcks before the Solomons"),
        ("Near Oceania (Solomon Islands)", "Remote Oceania (Lapita)",
         "Near Oceania before Remote Oceania"),
        ("Remote Oceania (Lapita)", "Central East Polynesia",
         "Lapita before East Polynesia"),
        ("Central East Polynesia", "Hawaii",
         "central East Polynesia is the staging area for the remote islands"),
        ("Central East Polynesia", "Rapa Nui (Easter Island)",
         "same"),
        ("Central East Polynesia", "New Zealand (Aotearoa)",
         "same"),
        ("Madagascar", "Iceland",
         "Madagascar settled before Iceland"),
        ("High Arctic (Canada and Greenland)", "Madagascar",
         "Palaeo-Inuit expansion predates secure Madagascar settlement"),
    ]
    for earlier, later, why in must_be_older:
        assert earlier in by_region, f"unknown region in ordering check: {earlier}"
        assert later in by_region, f"unknown region in ordering check: {later}"
        assert by_region[earlier] > by_region[later], (
            f"ordering violated: {earlier} ({by_region[earlier]} BP) must be "
            f"older than {later} ({by_region[later]} BP) - {why}")

    # New Zealand is the youngest arrival in the whole table.
    youngest_region = min(by_region, key=by_region.get)
    assert youngest_region == "New Zealand (Aotearoa)", (
        f"youngest arrival should be New Zealand, got {youngest_region}")

    # ---- ARRIVAL_RANGES: every region covered, point inside range -------
    assert set(ARRIVAL_RANGES) == seen_regions, (
        "ARRIVAL_RANGES and ARRIVALS disagree on regions: "
        f"{set(ARRIVAL_RANGES) ^ seen_regions}")
    for region, (older, younger, src) in ARRIVAL_RANGES.items():
        assert older >= younger, f"range inverted for {region}: {older} < {younger}"
        assert isinstance(src, str) and src, f"missing range source for {region}"
        pt = by_region[region]
        assert younger <= pt <= older, (
            f"point date for {region} ({pt} BP) lies outside its published "
            f"range {younger}-{older} BP")

    # ---- CONTESTED: every non-secure arrival is explained ---------------
    for region, _, _, _, _, conf, _ in ARRIVALS:
        if conf in ("contested", "refuted"):
            assert region in CONTESTED, (
                f"{region} is marked {conf} but has no CONTESTED entry")
    for region in CONTESTED:
        assert region in seen_regions, f"CONTESTED names unknown region: {region}"

    # ---- POPULATION: shape, ordering, positivity ------------------------
    assert len(POPULATION) >= 30, "POPULATION is too sparse for a log-time curve"
    prev = None
    for ybp, pop, src in POPULATION:
        assert isinstance(ybp, (int, float)), f"bad ybp: {ybp!r}"
        assert isinstance(pop, (int, float)) and pop > 0, f"bad population at {ybp}: {pop!r}"
        assert isinstance(src, str) and src, f"missing source at {ybp}"
        assert ("[Ne]" in src) or ("[census]" in src), (
            f"source at {ybp} does not declare [Ne] or [census]: {src!r}")
        if prev is not None:
            assert ybp < prev, (
                f"POPULATION must run strictly from oldest to youngest; "
                f"{ybp} follows {prev}")
        prev = ybp

    # Deep-past points must be Ne, and must be small; late points must be census.
    for ybp, pop, src in POPULATION:
        if "[Ne]" in src:
            assert pop <= 100000, (
                f"an [Ne] value of {pop} at {ybp} BP is too large to be an "
                f"effective population size")
        if ybp <= 21000:
            assert "[census]" in src, (
                f"the point at {ybp} BP should be a census estimate, got: {src!r}")

    # The census curve must be positive, and must grow overall.
    census = [(y, p) for y, p, s in POPULATION if "[census]" in s]
    assert census[0][1] < census[-1][1], "census population must grow over time"
    assert census[-1][1] > 8.0e9, "present-day population should exceed 8 billion"
    assert census[0][0] > census[-1][0], "census series ordering broken"

    # No single step may multiply population by more than 10x, which would
    # signal a units error or a misread figure.
    for (y0, p0), (y1, p1) in zip(census, census[1:]):
        ratio = p1 / p0
        assert 0.5 <= ratio <= 10.0, (
            f"implausible jump between {y0} BP ({p0:,}) and {y1} BP ({p1:,}): "
            f"x{ratio:.2f}")

    # Post-Neolithic growth: population at AD 1 exceeds that at 10,000 BC, and
    # every modern anchor exceeds the one before it.
    lookup = {y: p for y, p in census}
    assert lookup[1950] > lookup[11950], "AD 1 should exceed 10,000 BC"
    for older, younger in [(1950, 950), (950, 450), (450, 250), (250, 150),
                           (150, 50), (50, 0), (0, -50), (-50, -73)]:
        assert lookup[younger] > lookup[older], (
            f"population at {younger} BP should exceed that at {older} BP")

    # The one legitimate decline in the series is the Black Death, 1300 -> 1400.
    assert lookup[550] < lookup[650], (
        "HYDE shows a post-Black-Death decline between AD 1300 and AD 1400; "
        "it is missing")

    # ---- POPULATION_RANGES ----------------------------------------------
    for ybp, (low, high, src) in POPULATION_RANGES.items():
        assert low <= high, f"range inverted at {ybp} BP: {low} > {high}"
        assert low > 0 and isinstance(src, str) and src, f"bad range at {ybp} BP"

    # Every census point must sit inside its own published range where one exists.
    for ybp, pop, src in POPULATION:
        if "[census]" in src and ybp in POPULATION_RANGES:
            low, high, _ = POPULATION_RANGES[ybp]
            assert low <= pop <= high, (
                f"census point at {ybp} BP ({pop:,}) falls outside its stated "
                f"range {low:,}-{high:,}")

    # ---- SOURCE_DISAGREEMENTS: the flagged pairs really do differ >2x ----
    for label, ybp, sa, va, sb, vb, comment in SOURCE_DISAGREEMENTS:
        assert va > 0 and vb > 0, f"non-positive value in disagreement {label}"
        ratio = max(va, vb) / min(va, vb)
        assert ratio > FACTOR_THRESHOLD, (
            f"{label} is listed as a >2x disagreement but the ratio is only "
            f"{ratio:.2f}x ({sa}={va:,} vs {sb}={vb:,})")
        assert isinstance(comment, str) and comment, f"missing comment for {label}"

    # And the sub-threshold notes really are sub-threshold, or explained.
    for label, ybp, sa, va, sb, vb, comment in SOURCE_NOTES_SUBTHRESHOLD:
        ratio = max(va, vb) / min(va, vb)
        assert isinstance(comment, str) and comment
        if ratio > FACTOR_THRESHOLD:
            assert "rather than in SOURCE_DISAGREEMENTS" in comment, (
                f"{label} exceeds the 2x threshold ({ratio:.2f}x) but is filed "
                f"as sub-threshold without an explanation")

    # ---- POPULATION_BY_CONTINENT ----------------------------------------
    assert len(POPULATION_BY_CONTINENT) >= 12, "too few continental snapshots"
    prev = None
    for ybp, dist in POPULATION_BY_CONTINENT:
        assert set(dist) == set(CONTINENTS), (
            f"continent set wrong at {ybp} BP: {set(dist) ^ set(CONTINENTS)}")
        for cont, pop in dist.items():
            assert pop > 0, f"non-positive population for {cont} at {ybp} BP"
        if prev is not None:
            assert ybp < prev, (
                f"POPULATION_BY_CONTINENT must run oldest to youngest; "
                f"{ybp} follows {prev}")
        prev = ybp

    # Continental sums must reconcile with the world series to within 1%,
    # wherever both exist for the same ybp.
    world_lookup = {y: p for y, p, s in POPULATION if "[census]" in s}
    for ybp, dist in POPULATION_BY_CONTINENT:
        if ybp in world_lookup:
            total = sum(dist.values())
            world = world_lookup[ybp]
            rel = abs(total - world) / world
            assert rel < 0.01, (
                f"at {ybp} BP the continents sum to {total:,} but the world "
                f"series says {world:,} ({rel:.2%} apart)")

    # Africa, Asia and Europe must never be empty at any modelled date, and
    # every continent must be non-empty once it is peopled.
    for ybp, dist in POPULATION_BY_CONTINENT:
        for cont in ("Africa", "Asia", "Europe"):
            assert dist[cont] > 0, f"{cont} empty at {ybp} BP"

    # The American depopulation must appear between AD 1500 and AD 1600.
    d1500 = dict(POPULATION_BY_CONTINENT)[450]
    d1600 = dict(POPULATION_BY_CONTINENT)[350]
    americas_1500 = d1500["North America"] + d1500["South America"]
    americas_1600 = d1600["North America"] + d1600["South America"]
    assert americas_1600 < americas_1500 * 0.5, (
        "HYDE shows a >50% fall in the Americas between AD 1500 and AD 1600; "
        "it is missing from the data")

    # Asia must be the largest continent at every date from AD 1 onward.
    for ybp, dist in POPULATION_BY_CONTINENT:
        if ybp <= 1950:
            biggest = max(dist, key=dist.get)
            assert biggest == "Asia", (
                f"at {ybp} BP the largest continent is {biggest}, not Asia")

    # ---- ARRIVALS vs POPULATION_BY_CONTINENT: no anachronism ------------
    # A continent must not be shown as peopled before anyone got there --
    # allowing for the fact that HYDE's grid does exactly that in the deep
    # past. We check only the cases where the arrival evidence is secure and
    # the gap would be a real contradiction rather than a modelling artefact.
    oceania_arrival = by_region["New Guinea (highlands)"]        # 49,000 BP
    assert POPULATION_BY_CONTINENT[0][0] < oceania_arrival, (
        "the earliest continental snapshot postdates the settlement of Sahul, "
        "as it must - otherwise Oceania would be populated before arrival")

    # ---- Metadata --------------------------------------------------------
    assert len(SOURCES) >= 40, "SOURCES list looks incomplete"
    assert all(u.startswith("https://") for u in SOURCES), "non-HTTPS source URL"
    assert len(set(SOURCES)) == len(SOURCES), "duplicate URL in SOURCES"
    assert len(CAVEATS) >= 10, "CAVEATS list looks incomplete"
    assert BP_DATUM_YEAR == 1950
    assert year_ad_to_ybp(1950) == 0 and year_ad_to_ybp(1) == 1949
    assert ybp_to_2026(-76) == 0

    # Every DEEP_PAST_GENETICS entry is well formed.
    for label, older, younger, ne, status, src, note in DEEP_PAST_GENETICS:
        assert older >= younger, f"inverted range in {label}"
        assert ne > 0, f"non-positive Ne in {label}"
        assert status in {"accepted", "contested", "rejected"}, f"bad status in {label}"
        assert src.startswith(("Hu ", "Charlesworth", "Ambrose", "Summarised")), \
            f"unexpected source format in {label}"
        assert "http" in src or "http" in note, f"no URL for {label}"


# =============================================================================
# 8. SUMMARY
# =============================================================================

def _fmt(n: float) -> str:
    if n >= 1e9:
        return f"{n/1e9:.2f} bn"
    if n >= 1e6:
        return f"{n/1e6:.2f} M"
    if n >= 1e3:
        return f"{n/1e3:.1f} k"
    return f"{n:,.0f}"


def _ybp_label(ybp: float) -> str:
    if ybp >= 20000:
        return f"{ybp/1000:.1f} ka BP"
    if ybp > 0:
        return f"{ybp:,.0f} BP"
    return f"AD {BP_DATUM_YEAR - ybp:.0f}"


def summary() -> None:
    print("=" * 78)
    print("PEOPLING OF THE WORLD AND WORLD POPULATION HISTORY")
    print(f"built {DATASET_BUILT}   |   all ybp are cal BP, present = AD {BP_DATUM_YEAR}")
    print("=" * 78)

    # --- Arrivals ---
    print(f"\n1. ARRIVALS  ({len(ARRIVALS)} regions)")
    counts = {}
    for row in ARRIVALS:
        counts[row[5]] = counts.get(row[5], 0) + 1
    print("   confidence: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print(f"   {'region':38} {'ybp':>10}  {'conf':<10} site")
    print("   " + "-" * 73)
    for region, lat, lon, ybp, site, conf, note in sorted(
            ARRIVALS, key=lambda r: -r[3]):
        print(f"   {region[:38]:38} {ybp:>10,}  {conf:<10} {site[:28]}")

    print("\n   Not fully secure (reason in CONTESTED[...] where marked):")
    for row in ARRIVALS:
        if row[5] in ("contested", "refuted", "debated"):
            print(f"     - {row[0]} ({row[5]}): {row[4]}")

    # --- Population ---
    print(f"\n2. POPULATION  ({len(POPULATION)} points, "
          f"{len(POPULATION_CENSUS)} of them headcounts)")
    print(f"   {'when':>14}  {'value':>12}  kind   source")
    print("   " + "-" * 73)
    for ybp, pop, src in POPULATION:
        kind = "Ne " if "[Ne]" in src else "cen"
        short = src.split("[")[0].strip().rstrip(",")
        print(f"   {_ybp_label(ybp):>14}  {_fmt(pop):>12}  {kind}    {short[:36]}")

    print(f"\n   Source disagreements greater than {FACTOR_THRESHOLD:g}x "
          f"({len(SOURCE_DISAGREEMENTS)}):")
    for label, ybp, sa, va, sb, vb, comment in SOURCE_DISAGREEMENTS:
        ratio = max(va, vb) / min(va, vb)
        print(f"     - {label:22} x{ratio:4.1f}   {_fmt(va):>10} vs {_fmt(vb):>10}")

    # --- Continents ---
    print(f"\n3. POPULATION BY CONTINENT  ({len(POPULATION_BY_CONTINENT)} snapshots)")
    header = "   " + f"{'when':>14}" + "".join(f"{c[:9]:>11}" for c in CONTINENTS) + f"{'total':>12}"
    print(header)
    print("   " + "-" * (len(header) - 3))
    for ybp, dist in POPULATION_BY_CONTINENT:
        row = "   " + f"{_ybp_label(ybp):>14}"
        for c in CONTINENTS:
            row += f"{_fmt(dist[c]):>11}"
        row += f"{_fmt(sum(dist.values())):>12}"
        print(row)
    print("   Pre-Neolithic continental splits are HYDE model back-projections,")
    print("   not evidence. See the block comment above POPULATION_BY_CONTINENT.")

    # --- Genetics ---
    print(f"\n4. DEEP-PAST GENETICS  ({len(DEEP_PAST_GENETICS)} claims)")
    for label, older, younger, ne, status, src, note in DEEP_PAST_GENETICS:
        span = (f"{older:,}-{younger:,} BP" if older != younger else f"{older:,} BP")
        print(f"     - {label} [{status.upper()}]: Ne ~{ne:,} at {span}")

    # --- Metadata ---
    print(f"\n5. SOURCES: {len(SOURCES)} URLs consulted.")
    print(f"   CAVEATS: {len(CAVEATS)} items that could not be verified.")
    for c in CAVEATS[:3]:
        print(f"     - {c.split('.')[0]}.")
    print("     ... (see CAVEATS for the rest)")

    print("\n" + "=" * 78)


if __name__ == "__main__":
    validate()
    summary()
    print("validate(): all consistency checks passed.")
