#!/usr/bin/env python3
"""The Expanse, by milestone year, up to the opening of the Ring.

Content comes from Brian's build brief (September 2026). Where the brief's
sources contradicted it, the text was corrected and the correction is listed
in CORRECTIONS below, so every change from the brief can be traced:

  - the wiki says no chronology is confirmed "save for only one" date
  - 2307 is the show's gin label, "since 2307" (S2E5), not a novel's vintage
  - Epstein's design survived on his home computer, not through telemetry
  - the Caliban's War hybrids were launched at Mars, not Earth
  - the Anderson Station strikers had tried to surrender
  - the Y Que was slowed at close to a hundred g, not stopped outright
  - only 2025 has been overtaken by the calendar; 2050 has not
  - the first gap is about 160 years, not 140
  - Ganymede's field gives its surface some shelter, not full shielding
  - the intro no longer tells the reader how to treat the figures

A milestone's source badge says what its YEAR rests on. Its note says where
the event is told and, where the two differ, where the year comes from.

Markup in text: *Title* is set in italics. Everything else is plain.
"""

# the six source types, from most to least solid, with the marker each gets
SOURCES = [
    ("Novels",            "fill"),
    ("Show",              "fill"),
    ("Show design guide", "fill"),
    ("Wiki chronology",   "ring"),
    ("Fan chronology",    "ring"),
    ("Extrapolated",      "dash"),
]

# segments of the broken axis: key, label, first year, last year
SEGMENTS = [
    ("deep",  "Deep time",             None, None),
    ("early", "2025 to 2150",          2025, 2150),
    ("mid",   "2213 to 2341",          2213, 2341),
    ("story", "2342 to 2353, expanded", 2342, 2353),
]

ERAS = [
    dict(key="builders", name="Ring builders", title="The ring builders",
         span="About 2 billion years ago", seg="deep", text=[]),
    dict(key="offearth", name="Off Earth", title="Off Earth, then stuck there",
         span="2025 to about 2150", seg="early", text=[]),
    dict(key="epstein", name="Epstein Drive", title="The Epstein Drive",
         span="About 2213", seg="mid", text=[], extra="transfer"),
    dict(key="belt", name="The Belt", title="The Belt becomes somewhere people are from",
         span="2250 to 2350", seg="mid", text=[
             "Over these hundred years what accumulates is biology and grievance. "
             "Belters grow up in a third of a g or less. They are tall and thin with "
             "low bone density, and many cannot survive a trip down a gravity well. "
             "They speak a creole built from the languages of everyone who shipped "
             "out. By 2350 there is a whole population physiologically specialized "
             "for a place the inner planets treat as a labor pool and a water tap."]),
    dict(key="threebody", name="Three-body problem", title="A three-body problem",
         span="2320 to 2349", seg="mid", extra="powers", text=[
             "By the eve of the story the solar system is a standoff between two "
             "states and one population that is not a state.",
             "The standoff holds because nobody can win, so nobody starts. The plot "
             "of the series is somebody finding a way to change that."]),
    dict(key="phoebe", name="Phoebe to Eros", title="Phoebe, the *Canterbury*, Eros",
         span="2342 to 2350", seg="story", text=[]),
    dict(key="ganymede", name="Ganymede, Io, Venus", title="Ganymede, Io, and Venus",
         span="2351", seg="story", text=[
             "*Caliban's War*, two threads that turn out to be one."]),
    dict(key="ring", name="The Ring", title="The Ring opens",
         span="2352 to 2353", seg="story", text=[]),
]

POWERS = [
    ("Earth",
     "United Nations, a parliamentary republic under a Secretary-General",
     "31 billion people across Earth and its colonies, the largest fleet by hull "
     "count, the only working biosphere",
     "Over half the population on Basic, an aging navy, dependent on Belt volatiles"),
    ("Mars",
     "Martian Congressional Republic, independent since about 2214",
     "The best shipyards and the most capable warships in the system",
     "A small population and a national purpose staked on terraforming, which "
     "takes centuries"),
    ("The Belt",
     "No government. The OPA is an umbrella for factions that do not agree with "
     "each other",
     "Controls the water, air, and ore the inner planets run on",
     "No navy, no unity, no legal standing, and bodies that cannot take a gravity "
     "well"),
]

M = []


def ms(year, sort, era, label, source, body, note=""):
    M.append(dict(year=year, sort=sort, era=era, label=label, source=source,
                  note=note, body=body))


ms("c. 2 billion years ago", -2_000_000_000, "builders",
   "Ring builders launch the protomolecule; Saturn captures it on Phoebe",
   "Extrapolated", [
       "A civilization that had solved wormhole physics built a network of gates "
       "linking well over a thousand star systems. The novels never name them. "
       "Readers call them the ring builders.",
       "That civilization fired the protomolecule at the Sol system as a colonizing "
       "spore. It was aimed at whatever biomass it found, which at the time was "
       "single-celled life on Earth, and its job was to consume that biomass and "
       "build a gate here. It never arrived. Saturn's gravity captured it on the "
       "way in and it froze into the moon later named Phoebe, where it sat inert "
       "for two billion years.",
       "The builders were already gone by then. What killed them is the question "
       "the rest of the series is about."],
   "Never stated")

ms("2025", 2025, "offearth", "First permanent colony on Luna", "Show design guide", [
    "The show's design guide puts the first permanent Luna colony at 2025 and the "
    "first permanent Mars colony at 2050. (The first has since been overtaken by "
    "the real calendar.)"])

ms("2050", 2050, "offearth", "First permanent colony on Mars", "Show design guide", [
    "This period runs on chemical rockets and inefficient fusion torches, so "
    "transits take months and launch windows close for years at a time. Mars can "
    "be settled but not resupplied on demand, which forces self-sufficiency early "
    "and gives Martian culture its founding project: a terraforming program "
    "measured in generations."])

ms("c. 2150", 2150, "offearth",
   "Mars past 100 million people; independence movement begins", "Fan chronology", [
       "Earth consolidates under the United Nations, runs a population in the tens "
       "of billions, and puts most of it on basic assistance. That makes emigration "
       "a lottery prize rather than an ordinary choice. By roughly 2150 Mars is past "
       "100 million people and an independence movement is running. The Belt is "
       "still barely touched."],
   "Screen Rant. The wiki cites the design guide for Mars resisting Earth rule by 2150")

ms("c. 2200 to 2214", 2213, "epstein", "Solomon Epstein's flight and the Epstein Drive",
   "Show", [
       "The hinge of the setting. Sources place it between 2200 and 2214: the show's "
       "design guide says 2200, a line in season 2 puts it 137 years back, which is "
       "2214, and the wiki's drive entry says about 2213.",
       "Solomon Epstein, a Martian engineer, rebuilt the fusion drive on his own "
       "yacht and took it out for a test. It lit and did not stop. The acceleration "
       "pinned him in his couch, out of reach of the cutoff, and killed him. The "
       "yacht is still leaving the solar system. The design made it home anyway: "
       "he had left the plans on his home computer, where his wife found them.",
       "Before Epstein, interplanetary travel means Hohmann transfers: two short "
       "burns, a long coast, launch windows every couple of years, months in "
       "freefall. The Epstein Drive is efficient enough to burn continuously, so "
       "ships fly brachistochrone trajectories: accelerate to the midpoint, flip, "
       "decelerate. Three consequences follow:",
       {"ol": [
           "Travel times collapse from months to days or weeks, and launch windows "
           "stop mattering.",
           "Thrust gravity is available for most of a voyage, so crews arrive in "
           "working condition.",
           "The Belt and the outer moons become economically reachable, so people "
           "go, and then people are born there."]}],
   "S2E6 puts it 137 years before season 2, which is 2214; the design guide says "
   "2200; the wiki's drive entry says about 2213")

ms("2214", 2214, "epstein", "Martian Congressional Republic founded", "Wiki chronology", [
    "The wiki dates the founding of the Martian Congressional Republic to 2214, "
    "alongside the drive. Martians have the drive first."])

ms("2250", 2250, "belt", "Ceres established as the port city of the Belt",
   "Show design guide", [
       "The design guide dates Ceres as the established port city of the Belt to "
       "2250. The outer-system economy is water, air, and metal. Ceres and Saturn's "
       "rings supply ice. Ganymede supplies food: it is the only moon in the solar "
       "system with its own magnetic field, which gives its surface some shelter "
       "from Jupiter's radiation belts. Tycho Manufacturing does the heavy "
       "construction, including spinning up Eros and later building the Mormon "
       "generation ship *Nauvoo*."])

ms("2307", 2307, "belt", "Ganymede gin, “since 2307,” the one certain date in the series",
   "Show", [
       "The one date the series itself nails down is on a bottle label: Ganymede "
       "gin, “since 2307,” in season 2."],
   "S2E5, “Home.” The wiki calls it the only certain date in the series")

ms("2320", 2320, "threebody", "Josephus Miller starts with Star Helix Security on Ceres",
   "Novels", ["Josephus Miller starts work for Star Helix Security on Ceres."],
   "*Leviathan Wakes*: thirty years before the story")

ms("2336", 2336, "threebody", "Anderson Station massacre; Fred Johnson defects", "Novels", [
    "The Anderson Station massacre. UN Colonel Fred Johnson breaks a Belter strike "
    "after the strikers have tried to surrender, earns the name Butcher of Anderson "
    "Station, and defects. He later runs Tycho Station for the OPA."],
   "*Leviathan Wakes*. The show puts it in 2339 (S1E5)")

ms("2339", 2339, "threebody", "Avasarala becomes UN Deputy Under-Secretary",
   "Fan chronology", ["Chrisjen Avasarala becomes UN Deputy Under-Secretary."],
   "Screen Rant. No canonical source gives the year")

ms("2342", 2342, "phoebe", "Protomolecule found on Phoebe; Protogen kills the Martian team",
   "Novels", [
       "A research team on Phoebe finds something in the ice that is two billion "
       "years old and not dead. Protogen, the Earth corporation attached to the "
       "project, kills the Martian scientists and keeps the sample. (The novella "
       "*The Vital Abyss*.)"],
   "*The Vital Abyss*: eight years before *Leviathan Wakes*")

ms("2345", 2345, "phoebe", "Phoebe base established; Holden joins the *Canterbury*", "Show", [
    "Mars, working with Protogen, puts a small base on Phoebe. James Holden signs "
    "on to the ice hauler *Canterbury*."],
   "Holden: S1E1. The Phoebe base: the design guide; in the novella the joint "
   "station is already there, and destroyed, in 2342")

ms("2350", 2350, "phoebe", "*Scopuli*, *Canterbury*, *Donnager*, Eros, and Eros into Venus",
   "Novels", [
       "The main story of *Leviathan Wakes*, about seven weeks. Protogen picks Eros "
       "Station, 1.5 million Belters, as its test population. It uses the *Scopuli* "
       "crew as bait and destroys the *Canterbury* with a stealth ship carrying "
       "Martian parts, pushing Earth and Mars toward war. The Martian flagship "
       "*Donnager* is destroyed by the same stealth ships.",
       "On Ceres, Miller is assigned to find Julie Mao and finds her dead on Eros, "
       "patient zero. Eros is sealed and irradiated. The protomolecule takes its "
       "people apart and starts using the station as a body, then accelerates "
       "toward Earth and dodges everything, including an attempt to ram it with "
       "the *Nauvoo*. Miller lands with a nuclear device and talks to what is left "
       "of Julie. Eros turns and goes into Venus. Miller does not leave.",
       "The *Canterbury* survivors end up with a stolen Martian corvette, the "
       "*Tachi*, renamed *Rocinante*."],
   "*Leviathan Wakes*; seasons 1 and 2. The year itself is the show's (S1E9); "
   "the novels never print it")

ms("2351", 2351, "ganymede", "Ganymede falls, Io hybrid program, the Venus structure departs",
   "Novels", [
       {"dl": [
           ("Ganymede", "A figure with no vacuum suit walks into a standoff between "
            "UN and Martian marines and destroys both squads. Gunnery Sergeant Bobbie "
            "Draper is the only Martian left. The fighting wrecks the mirror array "
            "and the farms, and the breadbasket of the outer planets stops working "
            "within weeks."),
           ("Io", "The creature was a protomolecule hybrid, built on purpose. "
            "Jules-Pierre Mao's people have been taking children with compromised "
            "immune systems, who can be infected without their bodies fighting it, "
            "and growing weapons from them. Botanist Prax Meng is looking for his "
            "daughter Mei, taken for that reason. Before the year is out, rockets "
            "carrying hybrids are launched at Mars."),
           ("Venus", "The protomolecule has 1.5 million people, an entire station, "
            "and a planet's worth of energy, and it is building something. At the "
            "end of the year the structure lifts off and flies out past Jupiter on "
            "a course nobody can match.")]}],
   "*Caliban's War*. The year is counted from 2350")

ms("2352", 2352, "ring", "The Ring forms beyond the orbit of Uranus", "Wiki chronology", [
    "The object parks beyond the orbit of Uranus and builds a ring about a thousand "
    "kilometers across, then sits there. Three navies arrive to watch."],
   "The wiki cites *Caliban's War*, chapter 54")

ms("2353", 2353, "ring", "The *Y Que* transit, the slow zone, 1,373 gates", "Novels", [
    "A Belter, Manéo Jung-Espinoza, flies the small ship *Y Que* through the Ring "
    "at speed as a stunt. The ship is slowed almost instantly, at close to a "
    "hundred g, which kills him, and that is how humanity learns the Ring is a door.",
    "Behind it is a bounded volume with a station at the center and a hard speed "
    "limit. Anything moving faster than a few hundred meters per second has its "
    "momentum taken away at once. The fleets go in anyway: Earth, Mars, and an OPA "
    "contingent on the *Behemoth* (the *Nauvoo*, converted into a warship). "
    "Clarissa Mao, posing as Melba Koh, sabotages a UN ship to frame Holden, and "
    "the shooting starts. The station reads every weapon fired as an attack and "
    "tightens the speed limit, and people die of their own inertia. Holden reaches "
    "the station with a reconstruction of Miller that the protomolecule has been "
    "running as an investigator, and the station stands down.",
    "The slow zone is a hub with 1,373 gates, each opening on another star system "
    "with a habitable world. A species that has spent its history in one solar "
    "system has been handed a thousand of them by a machine built by something "
    "that has been dead for two billion years. The question the Ring leaves open "
    "is what killed the people who built it."],
   "*Abaddon's Gate*. The year is the wiki's, from S3E7: 187 days after the Ring formed")

MILESTONES = M

# the three intervals the closing note is about
GAPS = [
    (2050, 2213, "First Mars colony to the Epstein Drive"),
    (2213, 2350, "The drive to the story"),
    (2350, 2353, "The story"),
]

TAGLINE = "Spoiler-safe through *Abaddon's Gate* and season 3. Nothing later appears."

INTRO = [
    "The novels almost never print a year, so most of the hard dates here come from "
    "outside the books: the show's design guide, a line of dialogue here and there, "
    "the tie-in material, and the fan chronology that reconciles all of it. The "
    "Expanse Wiki says plainly that, apart from a single date, no chronology has "
    "ever been confirmed within the series. The deep-history figures are "
    "approximate, and the pre-story years are a widely used convention rather than "
    "something James S. A. Corey signed off on line by line. Each date is marked "
    "with what it rests on.",
    "This timeline stops at the opening of the Ring, the end of *Abaddon's Gate* "
    "and season 3.",
]

CLOSING = (
    "The gaps are not random. About 160 years separate the first Mars colony from "
    "the Epstein Drive, about 140 separate the drive from the story, and then "
    "everything that matters happens in four years. Corey built a setting that sat "
    "in equilibrium for a century and a half and then wrote the years in which it "
    "stopped being stable.")

# every place the text departs from the brief, and what it rests on
CORRECTIONS = [
    ("Intro", "“no chronology has ever been confirmed”",
     "“apart from a single date, no chronology has ever been confirmed”",
     "The wiki: “Save for only one, no certain chronological parameter has "
     "ever been affirmed.”"),
    ("Intro", "“Treat the deep-history figures as approximate”",
     "“The deep-history figures are approximate”",
     "The site's copy does not give the reader orders."),
    ("2025", "“Both dates have since been overtaken by the real calendar”",
     "“The first has since been overtaken”", "2050 has not arrived."),
    ("Epstein", "“The telemetry made it home, and so did the design”",
     "the plans were on his home computer, and his wife found them",
     "The Expanse Wiki, Solomon Epstein (Books), from the short story “Drive.”"),
    ("Epstein", "“the show's dialogue says 2214”",
     "a line in season 2 puts it 137 years back, which is 2214; the design guide says 2200",
     "The wiki timeline: “date given onscreen was 137 years before season 2.”"),
    ("2250", "“so crops there are shielded from Jupiter's radiation belts”",
     "“which gives its surface some shelter”",
     "Ganymede's field deflects part of Jupiter's radiation, not all of it."),
    ("2307", "a Ganymede gin vintage, the only hard date printed in the novels; badge Novels",
     "the show's gin label, “since 2307” (S2E5); badge Show",
     "The wiki calls it the only certain date; the label is a prop from S2E5, "
     "“Home.” No novel prints it."),
    ("2336", "“after the strikers have surrendered”",
     "“after the strikers have tried to surrender”",
     "Their surrenders were never relayed to Johnson."),
    ("2351", "“Hybrids are launched at Earth”",
     "“rockets carrying hybrids are launched at Mars”",
     "Nguyen orders the launch at Mars; Holden has the transponders turned on so "
     "they can be destroyed."),
    ("2353", "“He stops instantly, which kills him”",
     "“The ship is slowed almost instantly, at close to a hundred g”",
     "The book has the *Y Que* decelerate at about 99 g."),
    ("Gaps", "“about 140 years from the first Mars colony (2050) to the Epstein Drive”",
     "about 160 years", "2213 minus 2050 is 163."),
]
