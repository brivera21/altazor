#!/usr/bin/env python3
"""Three futures Kim Stanley Robinson wrote for the same centuries.

Robinson has said these books are not one continuity. Asked about it by
Andrew Liptak for Reactor on 6 May 2020, he said the Ministry for the
Future, New York 2140 and 2312 "are not from the same future history, but
there's a fair bit of congruence to the thinking." So the three run as
separate tracks here and the page never merges them.

The 2312 entries are quoted from the Orbit edition by page, read through
the Internet Archive's full text search of its scan. Charlotte Shortback's
periodization is on pages 255 to 257. The Mars trilogy and New York 2140
entries come from secondary sources, which is weaker, and every date that
the sources dispute is carried here as a dispute rather than resolved.

Each entry is (start, end, key, title, gloss, source). end is None for a
point event. A gloss is a plain statement of what the source says, not the
book's wording, except where quoting is unavoidable and short.
"""

# ---- the 2312 periodization: Charlotte Shortback's scheme ----
# Robinson, K. S. (2012). 2312. Orbit. Pages as marked.
PERIODS = [
    (2005, 2060, "dithering", "The Dithering",
     "From the end of the postmodern, a date Shortback takes from the UN "
     "announcement of climate change, to the fall into crisis. The novel's "
     "verdict on these fifty five years is that they were wasted.",
     "2312, p. 255"),
    (2060, 2130, "crisis", "The Crisis",
     "Arctic summer ice disappears, permafrost melts past recovery and "
     "releases its methane, and major sea rise becomes unavoidable. Average "
     "global temperature rises five kelvin and sea level five meters. In the "
     "2120s the bill arrives as food shortages, mass riots and death on every "
     "continent.",
     "2312, p. 255"),
    (2130, 2160, "turnaround", "The Turnaround",
     "Verteswandel, Shortback's mutation of values, and then revolutions. "
     "Strong AI and self replicating factories arrive together. Fusion power, "
     "synthetic biology, space elevators on Earth and Mars, fast propulsion, "
     "the beginning of the space diaspora and of the terraforming of Mars. "
     "The Mondragon Accord is signed. Climate modification is tried and one "
     "attempt goes badly wrong.",
     "2312, p. 255"),
    (2160, 2220, "accelerando", "The Accelerando",
     "Every new power applied at once, human longevity among them. The novel "
     "puts the largest jump in the longevity graphs at the start of this "
     "period and says many think that was no coincidence.",
     "2312, pp. 98, 255"),
    (2220, 2270, "ritard", "The Ritard",
     "Historians argue about why the Accelerando slowed. The reasons offered "
     "are that Mars finished its terraforming and withdrew from the Mondragon "
     "into isolation, that every good terrarium candidate was taken, and that "
     "the system's easily reached helium, nitrogen, rare earths, fossil fuels "
     "and photosynthesis had almost all been spoken for.",
     "2312, p. 256"),
    (2270, 2320, "balkanization", "The Balkanization",
     "Cold war between Mars and Earth for control of the solar system. Mars "
     "keeps to itself, Venus fights with itself, the Jovian moons decide to "
     "terraform their big three. Unaffiliated terraria multiply and whole "
     "populations vanish behind event horizons. Qubes are listed among the "
     "causes. Shortages turn to hoarding and then to tribalism.",
     "2312, p. 256"),
]

# what Shortback says could follow if the Balkanization goes badly
AFTER = ("Shortback leaves the next period unnamed but offers two candidates "
         "for it, the Atomization or the Dissolution, either of which she "
         "expects to be worse than the Ritard and possibly worse than the "
         "Crisis. The novel opens in 2312, eight years before her last "
         "period is due to end.", "2312, pp. 2, 257")

# ---- point events inside 2312 ----
EVENTS_2312 = [
    (2076, None, "quito", "The first space elevator",
     "Built at Quito. The novel says traffic between Earth and space rose by "
     "a factor of a hundred million once the elevators were up, and that this "
     "is the moment the solar system became reachable.",
     "2312, p. 134"),
    (2142, 2154, "iceage", "The Little Ice Age",
     "Twelve years, and the novel calls it disastrous. It is filed under "
     "climate modification efforts, which is to say it was something people "
     "did on purpose and then could not undo.",
     "2312, p. 255"),
    (2312, None, "now", "The novel's present",
     "Earth stands eleven meters above its old sea level, ice free but for "
     "Antarctica and Greenland, and the flooded coastline is named as one of "
     "the main drivers of the human disaster there.",
     "2312, pp. 2, 100"),
]

# ---- the qube thread, which is what the periodization is carrying ----
QUBES = [
    (2130, 2160, "Strong AI appears",
     "Listed in the Turnaround beside self replicating factories and fusion "
     "power, as one item in a burst of arrivals rather than an event of its "
     "own.", "2312, p. 255"),
    (2160, 2220, "The first generation ages",
     "Swan's qube Pauline is described as one of the first and weakest of "
     "them, which places her line near the beginning.", "2312, p. 58"),
    (2270, 2320, "Influence of qubes",
     "By the Balkanization they are named among the causes of the period, "
     "alongside cold war and shortage. The book's plot turns on qubes that "
     "have begun programming themselves.", "2312, pp. 256, 464"),
]

# ---- the Mars trilogy ----
# Secondary sources. KSR = kimstanleyrobinson.info, WP = Wikipedia,
# AHA = the American Historical Association article. Contested dates say so.
MARS = [
    (2020, None, "First feet on Mars", "John Boone lands on Chryse Planitia.",
     "KSR.info; Wikipedia", False),
    (2026, None, "The Ares departs",
     "21 December, carrying the First Hundred on a nine month crossing.",
     "KSR.info", False),
    (2027, None, "Underhill", "The First Hundred land and build the first settlement.",
     "KSR.info", False),
    (2040, 2049, "The longevity treatment",
     "Developed at Acheron by Vlad Taneev's group. The decade is as close as "
     "the sources get.", "KSR.info", False),
    (2061, None, "The First Martian Revolution",
     "It fails. Aquifers are broken and flood the surface, the space elevator "
     "is brought down, Phobos is driven out of orbit. World War Three runs on "
     "Earth at the same time.", "KSR.info; Wikipedia; AHA", False),
    (2100, None, "The second elevator", "Anchored at Sheffield.",
     "KSR.info", False),
    (2101, None, "The soletta", "Moved into position. The firmest terraforming date.",
     "KSR.info", False),
    (2104, None, "Dorsa Brevia",
     "The underground's conference, and the declaration that becomes the basis "
     "of the constitution. One page of the same source dates it to about 2107.",
     "KSR.info", True),
    (2127, None, "The Great Flood",
     "The West Antarctic ice sheet collapses and sea level rises about seven "
     "meters, much of it fast. One source says 2126.",
     "KSR.info", True),
    (2127, None, "The Second Martian Revolution",
     "It succeeds while Earth is busy drowning. Mars becomes independent and "
     "Burroughs is deliberately flooded.", "KSR.info; AHA", False),
    (2128, None, "The Martian constitution",
     "Voted on 27 February, local year M-52, and passed with 78 percent. "
     "Nadia Cherneshevsky serves as first president to 2134.",
     "KSR.info", False),
    (2160, 2169, "Pulsed fusion",
     "Fast propulsion arrives and the outer system opens.", "KSR.info", False),
    (2212, None, "The end of Blue Mars",
     "A cable crisis and a third revolution. One source runs the novel's span "
     "on to about 2225.", "KSR.info; Wikipedia", True),
]

# ---- New York 2140 ----
NY = [
    (2050, 2059, "The First Pulse",
     "About ten feet of sea level rise in about ten years, as the ice sheets "
     "let go. The novel calls each Pulse a complete psychodrama decade.",
     "The Conversation; Science Friday excerpt", False),
    (2060, 2069, "The great depression",
     "The novel says the people of the 2060s staggered on through it. The "
     "wealthy came out of it well and prescribed austerity for everyone else.",
     "quoted in reviews", False),
    (2085, 2100, "The Second Pulse",
     "Another forty feet, beginning with the Aurora Basin. The refugee crisis "
     "is rated at ten thousand katrinas. The exact years are one reviewer's "
     "reading, not the novel's.", "The Conversation; reviews", True),
    (2140, None, "The novel opens",
     "Fifty feet of rise in total. Manhattan below about Fortieth Street is "
     "drowned to the second or third floor and the streets are canals. The "
     "band between wet and dry is the intertidal.",
     "Science Friday excerpt; Wikipedia", False),
    (2142, None, "The storm",
     "A superstorm leaves much of the city homeless and the Householders' "
     "Union demands the uptown towers be requisitioned.",
     "Progress in Political Economy", False),
    (2143, None, "The strike",
     "A universal debt strike breaks the banks, and the Treasury nationalizes "
     "them rather than bailing them out.",
     "Progress in Political Economy; reviews", False),
]

# ---- where the three disagree, which is the point of drawing them apart ----
CONFLICTS = [
    ("Sea level",
     "2312 puts Earth five meters up by 2130 and eleven meters up by 2312. "
     "New York 2140 reaches about fifteen meters by 2140, a year when 2312 "
     "has only just entered its Turnaround. The two figures cannot both hold."),
    ("Mars",
     "2312 lists the terraforming of Mars as beginning in the Turnaround, "
     "between 2130 and 2160. In the trilogy it was approved around 2030 and "
     "Mars is an independent republic by 2128. 2312's Mars runs a century "
     "behind the trilogy's."),
    ("The author",
     "Robinson told Reactor in May 2020 that these books are not from the "
     "same future history, while allowing a fair bit of congruence to the "
     "thinking. The congruence is easy to see. All three put a catastrophe "
     "and a turn between about 2050 and 2140."),
]
