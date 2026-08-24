# -*- coding: utf-8 -*-
"""
International Chronostratigraphic Chart (ICS) + major-events reference data.

CHART VERSION IN USE
--------------------
    v2026/06   (June 2026)  -- the current chart as of 2026-08-23
    PDF: https://stratigraphy.org/ICSchart/ChronostratChart2026-06.pdf

CITATION
--------
NOTE: the chart's recommended citation CHANGED. The familiar
"Cohen, Finney, Gibbard & Fan (2013)" reference is the LEGACY one; since 2025
the ICS asks you to cite the new documenting paper plus the version string.

CURRENT (APA 7):
    Cohen, K. M., Harper, D. A. T., Gibbard, P. L., & Car, N. (2025). The ICS
    international chronostratigraphic chart this decade. Episodes, 48(1),
    105-115. https://doi.org/10.18814/epiiugs/2025/025001

    In-text, ICS asks you to also name the version, e.g.:
    "ICS International Chronostratigraphic Chart v2026/06 (Cohen et al., 2025)".

LEGACY (APA 7) -- still widely seen, cite only for pre-2025 chart versions:
    Cohen, K. M., Finney, S. C., Gibbard, P. L., & Fan, J.-X. (2013; updated).
    The ICS International Chronostratigraphic Chart. Episodes, 36(3), 199-204.
    https://doi.org/10.18814/epiiugs/2013/v36i3/002

WHAT CHANGED IN v2026/06 (per ICS news item 156):
    base Anisian       247.0    Ma  (was 246.7)
    base Olenekian     250.8    Ma  (was 249.9)
    base Wuchiapingian 259.857 +/-0.084 Ma (was 259.51 +/-0.21)
ICS states the next release is anticipated for 2026/12.

CHART TUPLE FORMAT
------------------
    (name, rank, parent, start_ma, end_ma, start_unc, start_approx)

    name         : str   -- the chart's own name for the unit
    rank         : str   -- 'eon' | 'era' | 'period' | 'epoch' | 'age'
    parent       : str|None
    start_ma     : float -- age of the BASE of the unit, in Ma (older bound)
    end_ma       : float -- age of the TOP of the unit, in Ma (younger bound)
    start_unc    : float|None -- the +/- printed on the chart for the base, or
                                 None where the chart prints no uncertainty
                                 (GSSA-defined Precambrian bases, astronomically
                                 tuned Cenozoic bases, etc.)
    start_approx : bool  -- True where the chart prints "~" before the number
                            (age estimated, boundary not yet radiometrically
                            pinned or not yet GSSP-defined)

    Every start_ma/end_ma below was cross-validated two ways: (a) the ordered
    numeric token sequence transcribed from the v2026/06 PDF, and (b) the
    Macrostrat "international ages/epochs/periods/eras/eons" timescale API.
    The two agree everywhere except the three v2026/06 revisions above, which
    Macrostrat had not yet ingested; those use the ICS values.
    A contiguity/containment check over this list passes (see validate() below).
"""

# ---------------------------------------------------------------------------
# Source for ALL of CHART:
#   ICS International Chronostratigraphic Chart v2026/06,
#   https://stratigraphy.org/ICSchart/ChronostratChart2026-06.pdf
#   cross-checked against https://macrostrat.org/api/v2/defs/intervals
# ---------------------------------------------------------------------------
CHART_VERSION = "v2026/06"
CITATION = ("Cohen, K. M., Harper, D. A. T., Gibbard, P. L., &amp; Car, N. (2025). "
            "The ICS international chronostratigraphic chart this decade. "
            "<i>Episodes, 48</i>(1), 105-115. "
            "<a href=\"https://doi.org/10.18814/epiiugs/2025/025001\">"
            "https://doi.org/10.18814/epiiugs/2025/025001</a>")

CHART = [
    # ---------------- EONS / EONOTHEMS ----------------
    # Hadean: the chart prints 4567 with no uncertainty. It is an informal /
    # not-GSSA-defined eon; 4567 Ma is the CAI age of the Solar System.
    ("Hadean",         "eon", None, 4567.0,   4031.0,   None,  False),
    # Base of the Archean was redefined as a GSSA at 4031 +/-3 Ma (age of the
    # Acasta Gneiss) in chart v2023/09; it is the one Precambrian base with a
    # printed uncertainty.
    ("Archean",        "eon", None, 4031.0,   2500.0,   3.0,   False),
    ("Proterozoic",    "eon", None, 2500.0,    538.8,   None,  False),
    ("Phanerozoic",    "eon", None,  538.8,      0.0,   0.6,   False),

    # ---------------- ERAS / ERATHEMS ----------------
    # The Hadean has no ICS-recognised eras.
    ("Eoarchean",         "era", "Archean",     4031.0, 3600.0, 3.0,  False),
    ("Paleoarchean",      "era", "Archean",     3600.0, 3200.0, None, False),
    ("Mesoarchean",       "era", "Archean",     3200.0, 2800.0, None, False),
    ("Neoarchean",        "era", "Archean",     2800.0, 2500.0, None, False),

    ("Paleoproterozoic",  "era", "Proterozoic", 2500.0, 1600.0, None, False),
    ("Mesoproterozoic",   "era", "Proterozoic", 1600.0, 1000.0, None, False),
    ("Neoproterozoic",    "era", "Proterozoic", 1000.0,  538.8, None, False),

    ("Paleozoic",         "era", "Phanerozoic",  538.8,  251.902, 0.6,   False),
    ("Mesozoic",          "era", "Phanerozoic",  251.902,  66.0,  0.024, False),
    ("Cenozoic",          "era", "Phanerozoic",   66.0,     0.0,  None,  False),

    # ---------------- PERIODS / SYSTEMS ----------------
    # Archean eras have no ICS periods.
    # Proterozoic period bases are all GSSAs (round numbers, no uncertainty)
    # EXCEPT the Cryogenian (~720) and Ediacaran (~635), which are estimated /
    # GSSP-defined.
    ("Siderian",       "period", "Paleoproterozoic", 2500.0, 2300.0, None, False),
    ("Rhyacian",       "period", "Paleoproterozoic", 2300.0, 2050.0, None, False),
    ("Orosirian",      "period", "Paleoproterozoic", 2050.0, 1800.0, None, False),
    ("Statherian",     "period", "Paleoproterozoic", 1800.0, 1600.0, None, False),

    ("Calymmian",      "period", "Mesoproterozoic",  1600.0, 1400.0, None, False),
    ("Ectasian",       "period", "Mesoproterozoic",  1400.0, 1200.0, None, False),
    ("Stenian",        "period", "Mesoproterozoic",  1200.0, 1000.0, None, False),

    ("Tonian",         "period", "Neoproterozoic",   1000.0,  720.0, None, False),
    ("Cryogenian",     "period", "Neoproterozoic",    720.0,  635.0, None, True),
    ("Ediacaran",      "period", "Neoproterozoic",    635.0,  538.8, None, True),

    ("Cambrian",       "period", "Paleozoic",  538.8,   486.85,  0.6,   False),
    ("Ordovician",     "period", "Paleozoic",  486.85,  443.1,   1.5,   False),
    ("Silurian",       "period", "Paleozoic",  443.1,   419.62,  0.9,   False),
    ("Devonian",       "period", "Paleozoic",  419.62,  358.86,  1.36,  False),
    ("Carboniferous",  "period", "Paleozoic",  358.86,  298.9,   0.19,  False),
    ("Permian",        "period", "Paleozoic",  298.9,   251.902, 0.15,  False),

    ("Triassic",       "period", "Mesozoic",   251.902, 201.4,   0.024, False),
    ("Jurassic",       "period", "Mesozoic",   201.4,   143.1,   0.2,   False),
    ("Cretaceous",     "period", "Mesozoic",   143.1,    66.0,   0.6,   False),

    ("Paleogene",      "period", "Cenozoic",    66.0,    23.04,  None,  False),
    ("Neogene",        "period", "Cenozoic",    23.04,    2.58,  None,  False),
    ("Quaternary",     "period", "Cenozoic",     2.58,     0.0,  None,  False),

    # ---------------- EPOCHS / SERIES ----------------
    # Naming note: the chart prints Lower/Middle/Upper for SERIES (rock) and
    # Early/Middle/Late for EPOCHS (time). Rank here is 'epoch', so the
    # Early/Middle/Late forms are used.
    # Cambrian uses formal series names instead; "Series 2" is still unnamed.
    ("Terreneuvian",        "epoch", "Cambrian", 538.8,  521.0,  0.6,  False),
    ("Series 2",            "epoch", "Cambrian", 521.0,  506.5,  None, True),
    ("Miaolingian",         "epoch", "Cambrian", 506.5,  497.0,  None, True),
    ("Furongian",           "epoch", "Cambrian", 497.0,  486.85, None, True),

    ("Early Ordovician",    "epoch", "Ordovician", 486.85, 471.3, 1.5, False),
    ("Middle Ordovician",   "epoch", "Ordovician", 471.3,  458.2, 1.4, False),
    ("Late Ordovician",     "epoch", "Ordovician", 458.2,  443.1, 0.7, False),

    ("Llandovery",          "epoch", "Silurian", 443.1,  432.9,  0.9, False),
    ("Wenlock",             "epoch", "Silurian", 432.9,  426.7,  1.2, False),
    ("Ludlow",              "epoch", "Silurian", 426.7,  422.7,  1.5, False),
    ("Pridoli",             "epoch", "Silurian", 422.7,  419.62, 1.6, False),

    ("Early Devonian",      "epoch", "Devonian", 419.62, 393.47, 1.36, False),
    ("Middle Devonian",     "epoch", "Devonian", 393.47, 382.31, 0.99, False),
    ("Late Devonian",       "epoch", "Devonian", 382.31, 358.86, 1.36, False),

    # On the chart Mississippian/Pennsylvanian are formally SUBSYSTEMS, each
    # further split into Lower/Middle/Upper series. They are given epoch rank
    # here (the usual convention, and what Macrostrat does) so the hierarchy
    # stays five-deep; the Lower/Middle/Upper sub-series are omitted.
    ("Mississippian",       "epoch", "Carboniferous", 358.86, 323.4, 0.19, False),
    ("Pennsylvanian",       "epoch", "Carboniferous", 323.4,  298.9, 0.4,  False),

    ("Cisuralian",          "epoch", "Permian", 298.9,   274.4,   0.15,  False),
    ("Guadalupian",         "epoch", "Permian", 274.4,   259.857, 0.4,   False),
    ("Lopingian",           "epoch", "Permian", 259.857, 251.902, 0.084, False),

    ("Early Triassic",      "epoch", "Triassic", 251.902, 247.0, 0.024, False),
    ("Middle Triassic",     "epoch", "Triassic", 247.0,   237.0, None,  False),
    ("Late Triassic",       "epoch", "Triassic", 237.0,   201.4, None,  True),

    ("Early Jurassic",      "epoch", "Jurassic", 201.4, 174.7, 0.2, False),
    ("Middle Jurassic",     "epoch", "Jurassic", 174.7, 161.5, 0.8, False),
    ("Late Jurassic",       "epoch", "Jurassic", 161.5, 143.1, 1.0, False),

    ("Early Cretaceous",    "epoch", "Cretaceous", 143.1, 100.5, 0.6, False),
    ("Late Cretaceous",     "epoch", "Cretaceous", 100.5,  66.0, 0.1, False),

    ("Paleocene",           "epoch", "Paleogene", 66.0,  56.0,  None, False),
    ("Eocene",              "epoch", "Paleogene", 56.0,  33.9,  None, False),
    ("Oligocene",           "epoch", "Paleogene", 33.9,  23.04, None, False),

    ("Miocene",             "epoch", "Neogene", 23.04, 5.333, None, False),
    ("Pliocene",            "epoch", "Neogene",  5.333, 2.58, None, False),

    ("Pleistocene",         "epoch", "Quaternary", 2.58, 0.0117, None, False),
    ("Holocene",            "epoch", "Quaternary", 0.0117, 0.0,  None, False),

    # ---------------- AGES / STAGES ----------------
    # Complete for the whole Phanerozoic.
    # Cambrian stage bases are all "~" (estimated); several stages are still
    # unnamed ("Stage 2", "Stage 3", "Stage 4", "Stage 10").
    ("Fortunian",      "age", "Terreneuvian", 538.8, 529.0, 0.6,  False),
    ("Stage 2",        "age", "Terreneuvian", 529.0, 521.0, None, True),
    ("Stage 3",        "age", "Series 2",     521.0, 514.5, None, True),
    ("Stage 4",        "age", "Series 2",     514.5, 506.5, None, True),
    ("Wuliuan",        "age", "Miaolingian",  506.5, 504.5, None, True),
    ("Drumian",        "age", "Miaolingian",  504.5, 500.5, None, True),
    ("Guzhangian",     "age", "Miaolingian",  500.5, 497.0, None, True),
    ("Paibian",        "age", "Furongian",    497.0, 494.2, None, True),
    ("Jiangshanian",   "age", "Furongian",    494.2, 491.0, None, True),
    ("Stage 10",       "age", "Furongian",    491.0, 486.85, None, True),

    ("Tremadocian",    "age", "Early Ordovician",  486.85, 477.1, 1.5, False),
    ("Floian",         "age", "Early Ordovician",  477.1,  471.3, 1.2, False),
    ("Dapingian",      "age", "Middle Ordovician", 471.3,  469.4, 1.4, False),
    ("Darriwilian",    "age", "Middle Ordovician", 469.4,  458.2, 0.9, False),
    ("Sandbian",       "age", "Late Ordovician",   458.2,  452.8, 0.7, False),
    ("Katian",         "age", "Late Ordovician",   452.8,  445.2, 0.7, False),
    ("Hirnantian",     "age", "Late Ordovician",   445.2,  443.1, 0.9, False),

    ("Rhuddanian",     "age", "Llandovery", 443.1, 440.5, 0.9, False),
    ("Aeronian",       "age", "Llandovery", 440.5, 438.6, 1.0, False),
    ("Telychian",      "age", "Llandovery", 438.6, 432.9, 1.0, False),
    ("Sheinwoodian",   "age", "Wenlock",    432.9, 430.6, 1.2, False),
    ("Homerian",       "age", "Wenlock",    430.6, 426.7, 1.3, False),
    ("Gorstian",       "age", "Ludlow",     426.7, 425.0, 1.5, False),
    ("Ludfordian",     "age", "Ludlow",     425.0, 422.7, 1.5, False),
    # The Pridoli Series carries no formally named stage; the chart leaves the
    # stage box blank. No 'age' rows are emitted for it.

    ("Lochkovian",     "age", "Early Devonian",  419.62, 413.02, 1.36, False),
    ("Pragian",        "age", "Early Devonian",  413.02, 410.62, 1.91, False),
    ("Emsian",         "age", "Early Devonian",  410.62, 393.47, 1.95, False),
    ("Eifelian",       "age", "Middle Devonian", 393.47, 387.95, 0.99, False),
    ("Givetian",       "age", "Middle Devonian", 387.95, 382.31, 1.04, False),
    ("Frasnian",       "age", "Late Devonian",   382.31, 372.15, 1.36, False),
    ("Famennian",      "age", "Late Devonian",   372.15, 358.86, 0.46, False),

    ("Tournaisian",    "age", "Mississippian", 358.86, 346.7, 0.19, False),
    ("Visean",         "age", "Mississippian", 346.7,  330.3, 0.4,  False),
    ("Serpukhovian",   "age", "Mississippian", 330.3,  323.4, 0.4,  False),
    ("Bashkirian",     "age", "Pennsylvanian", 323.4,  315.2, 0.4,  False),
    ("Moscovian",      "age", "Pennsylvanian", 315.2,  307.0, 0.2,  False),
    ("Kasimovian",     "age", "Pennsylvanian", 307.0,  303.7, 0.1,  False),
    ("Gzhelian",       "age", "Pennsylvanian", 303.7,  298.9, 0.1,  False),

    ("Asselian",       "age", "Cisuralian",  298.9,   293.52,  0.15,  False),
    ("Sakmarian",      "age", "Cisuralian",  293.52,  290.1,   0.17,  False),
    ("Artinskian",     "age", "Cisuralian",  290.1,   283.3,   0.26,  False),
    ("Kungurian",      "age", "Cisuralian",  283.3,   274.4,   0.4,   False),
    ("Roadian",        "age", "Guadalupian", 274.4,   266.9,   0.4,   False),
    ("Wordian",        "age", "Guadalupian", 266.9,   264.28,  0.4,   False),
    ("Capitanian",     "age", "Guadalupian", 264.28,  259.857, 0.16,  False),
    ("Wuchiapingian",  "age", "Lopingian",   259.857, 254.14,  0.084, False),  # revised in v2026/06
    ("Changhsingian",  "age", "Lopingian",   254.14,  251.902, 0.07,  False),

    ("Induan",         "age", "Early Triassic",  251.902, 250.8,   0.024, False),
    ("Olenekian",      "age", "Early Triassic",  250.8,   247.0,   None,  False),  # revised in v2026/06
    ("Anisian",        "age", "Middle Triassic", 247.0,   241.464, None,  False),  # revised in v2026/06
    ("Ladinian",       "age", "Middle Triassic", 241.464, 237.0,   0.28,  False),
    ("Carnian",        "age", "Late Triassic",   237.0,   227.3,   None,  True),
    ("Norian",         "age", "Late Triassic",   227.3,   205.7,   None,  True),
    ("Rhaetian",       "age", "Late Triassic",   205.7,   201.4,   None,  True),

    ("Hettangian",     "age", "Early Jurassic",  201.4, 199.5, 0.2, False),
    ("Sinemurian",     "age", "Early Jurassic",  199.5, 192.9, 0.3, False),
    ("Pliensbachian",  "age", "Early Jurassic",  192.9, 184.2, 0.3, False),
    ("Toarcian",       "age", "Early Jurassic",  184.2, 174.7, 0.3, False),
    ("Aalenian",       "age", "Middle Jurassic", 174.7, 170.9, 0.8, False),
    ("Bajocian",       "age", "Middle Jurassic", 170.9, 168.2, 0.8, False),
    ("Bathonian",      "age", "Middle Jurassic", 168.2, 165.3, 1.2, False),
    ("Callovian",      "age", "Middle Jurassic", 165.3, 161.5, 1.1, False),
    ("Oxfordian",      "age", "Late Jurassic",   161.5, 154.8, 1.0, False),
    ("Kimmeridgian",   "age", "Late Jurassic",   154.8, 149.2, 0.8, False),
    ("Tithonian",      "age", "Late Jurassic",   149.2, 143.1, 0.7, False),

    ("Berriasian",     "age", "Early Cretaceous", 143.1,  137.05, 0.6, False),
    ("Valanginian",    "age", "Early Cretaceous", 137.05, 132.6,  0.2, False),
    ("Hauterivian",    "age", "Early Cretaceous", 132.6,  125.77, 0.6, False),
    ("Barremian",      "age", "Early Cretaceous", 125.77, 121.4,  None, False),
    ("Aptian",         "age", "Early Cretaceous", 121.4,  113.2,  0.6, False),
    ("Albian",         "age", "Early Cretaceous", 113.2,  100.5,  0.3, False),
    ("Cenomanian",     "age", "Late Cretaceous",  100.5,   93.9,  0.1, False),
    ("Turonian",       "age", "Late Cretaceous",   93.9,   89.8,  0.2, False),
    ("Coniacian",      "age", "Late Cretaceous",   89.8,   85.7,  0.3, False),
    ("Santonian",      "age", "Late Cretaceous",   85.7,   83.6,  0.2, False),
    ("Campanian",      "age", "Late Cretaceous",   83.6,   72.2,  0.2, False),
    ("Maastrichtian",  "age", "Late Cretaceous",   72.2,   66.0,  0.2, False),

    ("Danian",         "age", "Paleocene", 66.0,  61.66, None, False),
    ("Selandian",      "age", "Paleocene", 61.66, 59.24, None, False),
    ("Thanetian",      "age", "Paleocene", 59.24, 56.0,  None, False),
    ("Ypresian",       "age", "Eocene",    56.0,  48.07, None, False),
    ("Lutetian",       "age", "Eocene",    48.07, 41.03, None, False),
    ("Bartonian",      "age", "Eocene",    41.03, 37.71, None, False),
    ("Priabonian",     "age", "Eocene",    37.71, 33.9,  None, False),
    ("Rupelian",       "age", "Oligocene", 33.9,  27.30, None, False),
    ("Chattian",       "age", "Oligocene", 27.30, 23.04, None, False),

    ("Aquitanian",     "age", "Miocene",  23.04, 20.45, None, False),
    ("Burdigalian",    "age", "Miocene",  20.45, 15.98, None, False),
    ("Langhian",       "age", "Miocene",  15.98, 13.82, None, False),
    ("Serravallian",   "age", "Miocene",  13.82, 11.63, None, False),
    ("Tortonian",      "age", "Miocene",  11.63,  7.246, None, False),
    ("Messinian",      "age", "Miocene",   7.246, 5.333, None, False),
    ("Zanclean",       "age", "Pliocene",  5.333, 3.600, None, False),
    ("Piacenzian",     "age", "Pliocene",  3.600, 2.58,  None, False),

    ("Gelasian",       "age", "Pleistocene", 2.58,   1.80,   None, False),
    ("Calabrian",      "age", "Pleistocene", 1.80,   0.774,  None, False),
    ("Chibanian",      "age", "Pleistocene", 0.774,  0.129,  None, False),
    # "Upper/Late Pleistocene" is shown on the chart but is NOT yet a formally
    # ratified named stage (no GSSP; the chart shades it differently).
    ("Late Pleistocene", "age", "Pleistocene", 0.129, 0.0117, None, False),
    ("Greenlandian",   "age", "Holocene", 0.0117, 0.0082, None, False),
    ("Northgrippian",  "age", "Holocene", 0.0082, 0.0042, None, False),
    ("Meghalayan",     "age", "Holocene", 0.0042, 0.0,    None, False),
]


# ---------------------------------------------------------------------------
# EVENTS
#
# Tuple format:
#   (name, age_ma, range_ma, description, source)
#
#   age_ma   : float -- best single point value, in Ma (so 0.0117 = 11.7 ka)
#   range_ma : (older_ma, younger_ma) tuple, or None.
#              Given wherever the event has real duration OR the date is
#              genuinely uncertain/disputed. When in doubt, USE THE RANGE.
#   source   : the specific study or reference page that states the number.
#
# These are NOT ICS chart values (the chart carries no events). They are
# current-consensus literature values; several are actively disputed and the
# description says so explicitly.
# ---------------------------------------------------------------------------
EVENTS = [
    # ---- Hadean ----
    ("Formation of the Solar System (CAIs)", 4567.3, (4567.5, 4567.1),
     "Calcium-aluminium-rich inclusions in chondrites, the oldest solids in the "
     "Solar System, date to 4567.3 +/- 0.16 Ma; the ICS chart uses 4567 Ma as the base of the Hadean.",
     "Wikipedia 'Age of Earth' (citing Bouvier & Wadhwa 2010); ICS chart v2026/06"),

    ("Formation of the Earth", 4540.0, (4590.0, 4490.0),
     "Earth accreted over roughly 30-100 Myr after CAI formation; the canonical "
     "figure is 4.54 +/- 0.05 Ga, derived from Pb-Pb dating of meteorites.",
     "Wikipedia 'Age of Earth' (Patterson 1956, 4.55 +/- 0.07 Ga; Dalrymple)"),

    ("Moon-forming giant impact", 4510.0, (4530.0, 4420.0),
     "A Mars-sized impactor ('Theia') struck the proto-Earth and formed the Moon; "
     "DISPUTED - Hf-W and U-Pb of lunar zircons give 4.51 Ga, other studies argue 4.42-4.45 Ga.",
     "Barboni et al. 2017, Science Advances 3:e1602365 'Early formation of the "
     "Moon 4.51 billion years ago'; cf. Thiemens et al. 2019, Nature Geoscience"),

    ("Jack Hills zircons (oldest known minerals)", 4404.0, (4412.0, 4396.0),
     "Detrital zircon grains from the Jack Hills, Western Australia, dated 4404 "
     "+/- 8 Ma - the oldest dated material of terrestrial origin.",
     "Wilde et al. 2001, Nature 409:175-178; Wikipedia 'Oldest dated rocks'"),

    ("Oldest widely accepted intact rock (Acasta Gneiss)", 4031.0, (4034.0, 4028.0),
     "Felsic orthogneiss from the Slave Craton, NW Canada, at 4031 +/- 3 Ma; "
     "this age now defines the GSSA base of the Archean Eon on the ICS chart.",
     "Wikipedia 'Oldest dated rocks'; ICS chart v2026/06 (base Archean 4031 +/-3 Ma)"),

    ("Nuvvuagittuq greenstone belt (disputed older rock)", 4280.0, (4280.0, 3800.0),
     "DISPUTED - a 4.28 Ga Sm-Nd mantle-extraction model age from Quebec; the "
     "true crystallisation age may be closer to 3.8 Ga, so it is not accepted as the oldest rock.",
     "Wikipedia 'Oldest dated rocks' (O'Neil et al. 2008 and rebuttals)"),

    # ---- Earliest life ----
    ("Oldest claimed biogenic carbon (Jack Hills zircon graphite)", 4100.0, None,
     "HIGHLY DISPUTED - isotopically light graphite enclosed in a single 4.1 Ga "
     "zircon, argued to be biogenic; no consensus.",
     "Bell et al. 2015, PNAS 112:14518; Wikipedia 'Earliest known life forms'"),

    ("Isua graphite - earliest chemical evidence of life", 3700.0, (3800.0, 3700.0),
     "Isotopically fractionated graphite in metasedimentary rocks of the Isua "
     "belt, Greenland; broadly (not universally) accepted as biogenic.",
     "Wikipedia 'Earliest known life forms' (Rosing 1999; Ohtomo et al. 2014)"),

    ("Dresser Formation stromatolites - earliest widely accepted fossil life", 3480.0, (3495.0, 3430.0),
     "Stromatolites in 3.480 Ga geyserite of the Pilbara Craton, Western Australia; "
     "the oldest fossils most researchers accept as biological.",
     "Wikipedia 'Earliest known life forms'; Djokic et al. 2017, Nature Communications"),

    # ---- Oxygenation & Paleoproterozoic ----
    ("Great Oxidation Event (onset)", 2430.0, (2460.0, 2426.0),
     "Atmospheric free oxygen rose irreversibly, marked by the loss of "
     "mass-independent sulphur fractionation; onset constrained to 2460-2426 Ma.",
     "Gumsley et al. 2017, PNAS 114:1811-1816 'Timing and tempo of the Great Oxidation Event'"),

    ("Great Oxidation Event (end of the oxygen overshoot / stabilisation)", 2060.0, (2220.0, 2060.0),
     "The GOE interval closes around 2.06 Ga; NOTE published onset estimates "
     "2016-2022 differ by ~500 Myr (2.7-2.3 Ga), so the event's timing is genuinely contested.",
     "Wikipedia 'Great Oxidation Event' (Poulton et al. 2021, Nature; Gumsley et al. 2017)"),

    ("Huronian glaciation (Paleoproterozoic 'Snowball Earth')", 2350.0, (2450.0, 2100.0),
     "Three glacial episodes (Ramsay Lake, Bruce, Gowganda formations) spanning "
     "~2.4-2.1 Ga, plausibly triggered by methane collapse during the GOE; the exact bounds are loose.",
     "Wikipedia 'Huronian glaciation' (Bekker 2020; Kopp et al. 2005, PNAS; Tang & Chen 2013)"),

    # ---- Eukaryotes ----
    ("First eukaryotes (oldest accepted body fossils)", 1650.0, (1800.0, 1600.0),
     "Ornamented acritarchs (Tappania, Shuiyousphaeridium) from North China at "
     "~1.65 Ga; Ruyang Group forms at 1.8-1.6 Ga may be older but are disputed, "
     "and the oldest secure eukaryotic biomarkers are only ~800 Ma.",
     "Wikipedia 'Eukaryote' (Miao et al. 2019; Javaux & Lepot 2018)"),

    # ---- Cryogenian Snowball Earth ----
    ("Sturtian glaciation (Snowball Earth)", 688.0, (717.0, 660.0),
     "The longer of the two Cryogenian global glaciations, ~717 to ~660 Ma; its "
     "onset coincides with the Franklin large igneous province.",
     "Wikipedia 'Cryogenian' (Rooney et al. 2015, Geology; MacLennan et al. 2018)"),

    ("Marinoan glaciation (Snowball Earth)", 640.0, (654.5, 632.3),
     "The end-Cryogenian glaciation; its END is well dated at 632.3 +/- 5.9 Ma, "
     "but its START is poorly constrained - no earlier than ~654.5 Ma. The ICS "
     "places the base of the Ediacaran (~635 Ma) at the Marinoan cap carbonate.",
     "Wikipedia 'Marinoan glaciation' (Rooney et al. 2015, Geology; Ma et al. 2023, Global and Planetary Change)"),

    # ---- Ediacaran / Cambrian ----
    ("Ediacaran biota", 570.0, (600.0, 538.8),
     "Soft-bodied macroscopic multicellular organisms; they appear ~600 Ma "
     "(classic Avalon assemblage ~575 Ma) and the characteristic communities "
     "vanish at the Cambrian boundary, 538.8 Ma.",
     "Wikipedia 'Ediacaran biota'; base-Cambrian age from ICS chart v2026/06"),

    ("Cambrian explosion", 530.0, (538.8, 515.0),
     "Rapid appearance of most animal phyla in the fossil record over ~13-25 Myr "
     "from the base of the Cambrian (538.8 Ma); trilobites appear at the base of "
     "Series 2, ~521 Ma.",
     "Wikipedia 'Cambrian explosion'; stage ages from ICS chart v2026/06"),

    # ---- The Big Five mass extinctions ----
    # Percentages: species-level estimates are model-dependent; genus-level
    # figures are the directly counted ones. Both are given.
    ("End-Ordovician mass extinction", 444.0, (445.2, 443.1),
     "Two pulses across the Hirnantian glaciation killed ~85% of species (~57% of "
     "genera); the second-largest extinction by genus loss.",
     "Wikipedia 'Extinction event' (Bambach 2006, Annu. Rev. Earth Planet. Sci.); "
     "Hirnantian bounds from ICS chart v2026/06"),

    ("Late Devonian mass extinction (Kellwasser event)", 372.15, (382.31, 372.15),
     "A protracted crisis peaking at the Frasnian-Famennian boundary (372.15 Ma); "
     "at least ~70-75% of species and ~50% of genera lost, with reef ecosystems hit hardest.",
     "Wikipedia 'Extinction event' (Bambach 2006; McGhee 1996); boundary age from ICS chart v2026/06"),

    ("End-Devonian (Hangenberg) event", 358.86, None,
     "A second Devonian crisis at the Devonian-Carboniferous boundary, often "
     "counted with the Late Devonian extinction; severely hit early vertebrates.",
     "Wikipedia 'Extinction event'; boundary age from ICS chart v2026/06"),

    ("End-Permian mass extinction ('the Great Dying')", 251.9, (251.941, 251.880),
     "The most severe extinction known: ~81% of marine species and ~70% of "
     "terrestrial vertebrate species lost in 60 +/- 48 kyr. NOTE the often-quoted "
     "'96% of marine species' (Raup 1979) is now regarded as too high.",
     "Wikipedia 'Permian-Triassic extinction event' (Burgess et al. 2014, PNAS "
     "for the 251.941-251.880 Ma interval; Stanley 2016, PNAS for 81%)"),

    ("End-Triassic mass extinction", 201.4, None,
     "At the Triassic-Jurassic boundary; ~70-75% of species and ~48% of genera "
     "lost, plausibly driven by the Central Atlantic Magmatic Province.",
     "Wikipedia 'Extinction event' (UCR/Bambach compilations); boundary age 201.4 "
     "+/-0.2 Ma from ICS chart v2026/06"),

    ("End-Cretaceous (K-Pg) mass extinction", 66.0, None,
     "~75% of species and ~50% of genera lost, including all non-avian dinosaurs; "
     "coincides with the Chicxulub impact and Deccan Traps volcanism.",
     "Wikipedia 'Extinction event' (Raup & Sepkoski 1982); boundary age 66.0 Ma "
     "from ICS chart v2026/06"),

    ("Chicxulub impact", 66.043, (66.054, 66.032),
     "A ~10 km bolide struck the Yucatan Peninsula; 40Ar/39Ar dating of Haitian "
     "tektites gives 66.043 +/- 0.011 Ma (+/- 0.043 Ma including systematic error).",
     "Renne et al. 2013, Science 339:684-687; Wikipedia 'Chicxulub crater'"),

    # ---- Terrestrialisation and major clades ----
    ("First land plants", 470.0, (473.0, 465.0),
     "Cryptospores (monads, dyads, tetrads) from the Middle Ordovician of Turkey, "
     "Saudi Arabia and Argentina - the earliest evidence of plants on land.",
     "Wikipedia 'Timeline of plant evolution' (Rubinstein et al. 2010, New Phytologist)"),

    ("First vascular plants", 425.0, (433.0, 420.0),
     "Cooksonia and relatives, the first land plants with conducting tissue, "
     "appear in the Silurian (Wenlock-Pridoli).",
     "Wikipedia 'Timeline of plant evolution'; Silurian series ages from ICS chart v2026/06"),

    ("First forests", 385.0, (390.0, 380.0),
     "Cladoxylopsid and Archaeopteris trees form the world's first forests in the "
     "Middle-Late Devonian (e.g. the Gilboa fossil forest).",
     "Wikipedia 'Timeline of plant evolution'; Stein et al. 2012, Nature"),

    ("First tetrapods (trackways)", 390.0, (393.0, 385.0),
     "Trackways from Zachelmie, Poland, in the Eifelian (Middle Devonian), ~390 "
     "Ma; second-oldest are Valentia Island, Ireland, ~385 Ma.",
     "Wikipedia 'Tetrapod' (Niedzwiedzki et al. 2010, Nature)"),

    ("First tetrapods (body fossils)", 370.0, (380.0, 360.0),
     "Fragmentary Frasnian forms (Elginerpeton, Obruchevichthys) at ~380 Ma; the "
     "oldest near-complete tetrapods, Acanthostega and Ichthyostega, are late Famennian (~365 Ma).",
     "Wikipedia 'Tetrapod'"),

    ("First amniotes", 318.0, (355.0, 315.0),
     "Hylonomus and Asaphestera from Nova Scotia, Bashkirian (~318 Ma), are the "
     "oldest crown amniotes from body fossils; DISPUTED 2025 Australian trackways "
     "would push the origin back to ~355 Ma.",
     "Wikipedia 'Amniote' (Hylonomus/Asaphestera); Long et al. 2025, Nature (disputed trackways)"),

    ("First dinosaurs", 233.0, (243.0, 230.0),
     "Gnathovorax and Staurikosaurus from the Santa Maria Formation (233.23 Ma) "
     "and Eoraptor/herrerasaurids from Ischigualasto (231-230 Ma); the ~243 Ma "
     "Nyasasaurus is too fragmentary to confirm.",
     "Wikipedia 'Dinosaur' (Langer et al.; Nesbitt et al. 2013 for Nyasasaurus)"),

    ("First mammaliaforms", 225.0, (230.0, 205.0),
     "Late Triassic mammal-like forms (Adelobasileus, Morganucodon grade) at "
     "~225 Ma under the traditional jaw-joint definition of 'mammal'.",
     "Wikipedia 'Mammal' (Kemp 2005)"),

    ("First crown-group mammals", 167.0, (180.0, 160.0),
     "Ambondro, Amphilestes and Amphitherium, all ~167 Ma (Middle Jurassic), "
     "bracket the monotreme-therian split and so date the mammal crown group.",
     "Wikipedia 'Mammal'"),

    ("First birds (Archaeopteryx)", 150.0, (160.0, 148.5),
     "Archaeopteryx from the Solnhofen limestone, 150.8-148.5 Ma; NOTE it is no "
     "longer regarded as the oldest bird - older avialans (Anchiornis, Aurornis, "
     "Baminornis) reach ~160 Ma, and Archaeopteryx's placement is itself debated.",
     "Wikipedia 'Archaeopteryx'"),

    ("First flowering plants (angiosperms)", 130.0, (135.0, 125.0),
     "Unequivocal angiosperm pollen and fossils appear suddenly and diversely in "
     "the Early Cretaceous, ~130 Ma; DISPUTED - molecular clocks imply a much "
     "older origin and pre-Cretaceous fossil claims (e.g. Nanjinganthus) are not accepted.",
     "Wikipedia 'Flowering plant'"),

    # ---- Cenozoic ----
    ("Paleocene-Eocene Thermal Maximum (PETM)", 56.0, (56.0, 55.8),
     "A 5-8 degC global warming spike lasting ~200 kyr; its carbon isotope "
     "excursion onset DEFINES the Paleocene/Eocene GSSP, so the ICS age of the "
     "boundary, 56.0 Ma, is the PETM onset.",
     "ICS chart v2026/06 (base Ypresian 56.0 Ma); Britannica 'Paleocene-Eocene "
     "Thermal Maximum'; Zeebe & Lourens 2019, Science"),

    ("First hominins (Sahelanthropus tchadensis)", 7.0, (7.2, 6.8),
     "Cranial material from Chad radiometrically constrained to 7.2-6.8 Ma; "
     "DISPUTED - its hominin status and bipedality are both contested, with some "
     "analyses placing it on the gorilla lineage or outside Hominini.",
     "Wikipedia 'Sahelanthropus' (Brunet et al. 2002, Nature; Lebatard et al. "
     "2008, PNAS; Meyer et al. 2023)"),

    ("First Homo (LD 350-1)", 2.8, (2.8, 2.75),
     "A mandible from Ledi-Geraru, Ethiopia, dated to ~2.8 Ma, combining "
     "Australopithecus-like and derived Homo traits; the oldest attributed to genus Homo.",
     "Villmoare et al. 2015, Science 347:1352-1355; Wikipedia 'LD 350-1'"),

    ("First Homo sapiens (Jebel Irhoud)", 0.315, (0.35, 0.28),
     "Hominin remains from Jebel Irhoud, Morocco, thermoluminescence-dated to "
     "~315 +/- 34 ka - the earliest fossils attributed to H. sapiens, pushing back "
     "the previous ~200 ka estimate.",
     "Richter et al. 2017, Nature 546:293-296; Hublin et al. 2017, Nature 546:289-292"),

    ("Last Glacial Maximum", 0.0225, (0.0265, 0.019),
     "Peak global ice volume of the last glacial cycle; Clark et al. give 26.5-19 "
     "ka, while other compilations give 26-20 ka and peak ice area at 25.2-23.1 ka.",
     "Clark et al. 2009, Science 325:710-714; Wikipedia 'Last Glacial Maximum' "
     "(Armstrong, Hopcroft & Valdes 2019)"),

    ("Start of the Holocene", 0.0117, None,
     "GSSP at the end of the Younger Dryas in the NGRIP2 Greenland ice core, "
     "11,700 calendar yr before 2000 CE (b2k); ratified 2008.",
     "Walker et al. 2009, J. Quaternary Science 24:3-17; ICS chart v2026/06 "
     "(base Holocene 0.0117 Ma)"),

    ("Proposed Anthropocene - REJECTED", 0.00005, None,
     "A proposed epoch with a GSSP at Crawford Lake, Ontario, and a base at ~1952 "
     "CE. REJECTED: the ICS Subcommission on Quaternary Stratigraphy voted it "
     "down in Feb 2024, and ICS and IUGS ratified the rejection on 20 March 2024. "
     "It is NOT part of the ICS chart; we remain in the Meghalayan Age of the "
     "Holocene. The term stays in informal use in Earth-system science.",
     "IUGS/ICS joint statement, 20 March 2024; ICS Subcommission on Quaternary "
     "Stratigraphy, Anthropocene Working Group page "
     "(https://quaternary.stratigraphy.org/working-groups/anthropocene)"),
]


# ---------------------------------------------------------------------------
# URLs actually used to build this file
# ---------------------------------------------------------------------------
SOURCE_URLS = [
    # The chart itself
    "https://stratigraphy.org/ICSchart/ChronostratChart2026-06.pdf",
    "https://stratigraphy.org/news/156",          # v2026/06 change list
    "https://stratigraphy.org/chart",
    # Documenting paper / citation
    "https://www.e-episodes.org/journal/view.html?doi=10.18814%2Fepiiugs%2F2025%2F025001",
    "https://research-portal.uu.nl/ws/files/255633872/IUGS2411.pdf",
    # Independent cross-check of every boundary age
    "https://macrostrat.org/api/v2/defs/intervals?timescale_id=1&format=csv",
    "https://macrostrat.org/api/v2/defs/intervals?timescale=international%20epochs&format=csv",
    "https://macrostrat.org/api/v2/defs/intervals?timescale=international%20periods&format=csv",
    "https://macrostrat.org/api/v2/defs/intervals?timescale=international%20eras&format=csv",
    "https://macrostrat.org/api/v2/defs/intervals?timescale=international%20eons&format=csv",
    # Events
    "https://quaternary.stratigraphy.org/working-groups/anthropocene",
    "https://en.wikipedia.org/wiki/Age_of_Earth",
    "https://en.wikipedia.org/wiki/Oldest_dated_rocks",
    "https://en.wikipedia.org/wiki/Earliest_known_life_forms",
    "https://en.wikipedia.org/wiki/Great_Oxidation_Event",
    "https://en.wikipedia.org/wiki/Huronian_glaciation",
    "https://en.wikipedia.org/wiki/Cryogenian",
    "https://en.wikipedia.org/wiki/Marinoan_glaciation",
    "https://en.wikipedia.org/wiki/Eukaryote",
    "https://en.wikipedia.org/wiki/Ediacaran_biota",
    "https://en.wikipedia.org/wiki/Cambrian_explosion",
    "https://en.wikipedia.org/wiki/Extinction_event",
    "https://en.wikipedia.org/wiki/Permian%E2%80%93Triassic_extinction_event",
    "https://en.wikipedia.org/wiki/Chicxulub_crater",
    "https://en.wikipedia.org/wiki/Timeline_of_plant_evolution",
    "https://en.wikipedia.org/wiki/Tetrapod",
    "https://en.wikipedia.org/wiki/Amniote",
    "https://en.wikipedia.org/wiki/Dinosaur",
    "https://en.wikipedia.org/wiki/Mammal",
    "https://en.wikipedia.org/wiki/Archaeopteryx",
    "https://en.wikipedia.org/wiki/Flowering_plant",
    "https://en.wikipedia.org/wiki/Sahelanthropus",
    "https://en.wikipedia.org/wiki/Homo",
    "https://en.wikipedia.org/wiki/Last_Glacial_Maximum",
    "https://en.wikipedia.org/wiki/Holocene",
    "https://en.wikipedia.org/wiki/Cambrian",
    "https://en.wikipedia.org/wiki/Permian",
]


def validate(chart=CHART):
    """Check containment, contiguity and rank nesting. Returns a list of problems."""
    RANK_ORDER = {"eon": 0, "era": 1, "period": 2, "epoch": 3, "age": 4}
    by_name = {}
    problems = []
    for row in chart:
        name, rank = row[0], row[1]
        if rank not in RANK_ORDER:
            problems.append("bad rank %r for %s" % (rank, name))
        if name in by_name:
            problems.append("duplicate unit name: %s" % name)
        by_name[name] = row

    children = {}
    for row in chart:
        name, rank, parent, start, end = row[0], row[1], row[2], row[3], row[4]
        if start <= end:
            problems.append("%s: start (%s) must be older than end (%s)" % (name, start, end))
        if parent is None:
            continue
        if parent not in by_name:
            problems.append("%s: unknown parent %r" % (name, parent))
            continue
        p = by_name[parent]
        if RANK_ORDER[rank] <= RANK_ORDER[p[1]]:
            problems.append("%s (%s) not nested below %s (%s)" % (name, rank, parent, p[1]))
        if start > p[3] or end < p[4]:
            problems.append("%s [%s, %s] escapes parent %s [%s, %s]"
                            % (name, start, end, parent, p[3], p[4]))
        children.setdefault(parent, []).append(row)

    for parent, kids in children.items():
        kids.sort(key=lambda r: -r[3])
        p = by_name[parent]
        # child ranks must all match
        if len(set(k[1] for k in kids)) != 1:
            problems.append("%s: children have mixed ranks" % parent)
        if kids[0][3] != p[3]:
            problems.append("%s: first child %s starts at %s, parent starts at %s"
                            % (parent, kids[0][0], kids[0][3], p[3]))
        if kids[-1][4] != p[4]:
            problems.append("%s: last child %s ends at %s, parent ends at %s"
                            % (parent, kids[-1][0], kids[-1][4], p[4]))
        for a, b in zip(kids, kids[1:]):
            if a[4] != b[3]:
                problems.append("gap/overlap in %s: %s ends %s but %s starts %s"
                                % (parent, a[0], a[4], b[0], b[3]))
    return problems


if __name__ == "__main__":
    issues = validate()
    print("CHART units: %d   EVENTS: %d" % (len(CHART), len(EVENTS)))
    if issues:
        print("PROBLEMS (%d):" % len(issues))
        for i in issues:
            print("  -", i)
    else:
        print("Chart validates: contiguous, nested, no gaps or overlaps.")
