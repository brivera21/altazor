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
             "Belters grow up in a third of a g or less, tall, thin, and fragile in a "
             "gravity well, speaking a creole of everyone who shipped out. By 2350 the "
             "inner planets treat them as a labor pool and a water tap."]),
    dict(key="threebody", name="Three-body problem", title="A three-body problem",
         span="2320 to 2349", seg="mid", extra="powers", text=[
             "Two states and one population that is not a state.",
             "Nobody can win, so nobody starts."]),
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
       "A civilization with gates to over a thousand star systems fired the "
       "protomolecule at Earth, to consume its single-celled life and build a gate. "
       "Saturn caught it on the way in, and it sat frozen in Phoebe for two billion "
       "years."],
   "Never stated")

ms("2025", 2025, "offearth", "First permanent colony on Luna", "Show design guide", [
    "The show's design guide puts the first permanent colony on Luna here. The real "
    "calendar has already passed it."])

ms("2050", 2050, "offearth", "First permanent colony on Mars", "Show design guide", [
    "Chemical rockets and weak fusion torches mean transits of months and launch "
    "windows years apart. Mars can be settled but not resupplied on demand, so it "
    "learns self-sufficiency and takes up terraforming as a project for generations."])

ms("c. 2150", 2150, "offearth",
   "Mars past 100 million people; independence movement begins", "Fan chronology", [
       "Earth runs tens of billions under the UN, most on basic assistance, and "
       "emigration is a lottery prize. Mars passes 100 million people and starts "
       "talking independence. The Belt is still barely touched."],
   "Screen Rant. The wiki cites the design guide for Mars resisting Earth rule by 2150")

ms("c. 2200 to 2214", 2213, "epstein", "Solomon Epstein's flight and the Epstein Drive",
   "Show", [
       "Solomon Epstein, a Martian engineer, took his rebuilt fusion drive out for a "
       "test. It lit and never stopped, and the acceleration pinned him out of reach "
       "of the cutoff and killed him. His plans were on his home computer, where his "
       "wife found them."],
   "S2E6 puts it 137 years before season 2, which is 2214; the design guide says "
   "2200; the wiki's drive entry says about 2213")

ms("2214", 2214, "epstein", "Martian Congressional Republic founded", "Wiki chronology", [
    "Mars founds the Martian Congressional Republic the same year, and has the drive "
    "first."])

ms("2250", 2250, "belt", "Ceres established as the port city of the Belt",
   "Show design guide", [
       "Ceres becomes the Belt's port. The outer system runs on water, air, and metal: "
       "ice from Ceres and Saturn's rings, food from Ganymede, whose own magnetic "
       "field gives it some shelter from Jupiter's radiation, and heavy construction "
       "from Tycho."])

ms("2307", 2307, "belt", "Ganymede gin, \u201csince 2307,\u201d the one certain date in the series",
   "Show", [
       "The one certain date in the series is a Ganymede gin label that reads "
       "\u201csince 2307,\u201d seen in season 2."],
   "S2E5, \u201cHome.\u201d The wiki calls it the only certain date in the series")

ms("2320", 2320, "threebody", "Josephus Miller starts with Star Helix Security on Ceres",
   "Novels", ["Josephus Miller starts work for Star Helix Security on Ceres."],
   "*Leviathan Wakes*: thirty years before the story")

ms("2336", 2336, "threebody", "Anderson Station massacre; Fred Johnson defects", "Novels", [
    "UN Colonel Fred Johnson breaks a Belter strike after the strikers have tried to "
    "surrender. He earns the name Butcher of Anderson Station, defects, and later "
    "runs Tycho Station for the OPA."],
   "*Leviathan Wakes*. The show puts it in 2339 (S1E5)")

ms("2339", 2339, "threebody", "Avasarala becomes UN Deputy Under-Secretary",
   "Fan chronology", ["Chrisjen Avasarala becomes UN Deputy Under-Secretary."],
   "Screen Rant. No canonical source gives the year")

ms("2342", 2342, "phoebe", "Protomolecule found on Phoebe; Protogen kills the Martian team",
   "Novels", [
       "A research team on Phoebe finds something in the ice that is two billion "
       "years old and not dead. Protogen kills the Martian scientists and keeps the "
       "sample."],
   "*The Vital Abyss*: eight years before *Leviathan Wakes*")

ms("2345", 2345, "phoebe", "Phoebe base established; Holden joins the *Canterbury*", "Show", [
    "Mars, working with Protogen, puts a small base on Phoebe. James Holden signs "
    "on to the ice hauler *Canterbury*."],
   "Holden: S1E1. The Phoebe base: the design guide; in the novella the joint "
   "station is already there, and destroyed, in 2342")

ms("2350", 2350, "phoebe", "*Scopuli*, *Canterbury*, *Donnager*, Eros, and Eros into Venus",
   "Novels", [
       "Protogen destroys the *Canterbury* and the *Donnager* to push Earth and Mars "
       "toward war, and makes Eros, 1.5 million people, its test. The protomolecule "
       "takes the station, and Miller rides it into Venus. The *Canterbury* "
       "survivors keep a stolen Martian corvette and name it *Rocinante*."],
   "*Leviathan Wakes*; seasons 1 and 2. The year itself is the show's (S1E9); "
   "the novels never print it")

ms("2351", 2351, "ganymede", "Ganymede falls, Io hybrid program, the Venus structure departs",
   "Novels", [
       {"dl": [
           ("Ganymede", "A protomolecule hybrid kills UN and Martian marines alike. "
            "Bobbie Draper is the only Martian left, and the outer planets' "
            "breadbasket fails."),
           ("Io", "Mao's people grow the hybrids from children, and Prax Meng is "
            "looking for his daughter. Rockets carrying hybrids are launched at Mars."),
           ("Venus", "The structure lifts off Venus and heads out past Jupiter.")]}],
   "*Caliban's War*. The year is counted from 2350")

ms("2352", 2352, "ring", "The Ring forms beyond the orbit of Uranus", "Wiki chronology", [
    "The object parks beyond Uranus and builds a ring about a thousand kilometers "
    "across. Three navies come to watch."],
   "The wiki cites *Caliban's War*, chapter 54")

ms("2353", 2353, "ring", "The *Y Que* transit, the slow zone, 1,373 gates", "Novels", [
    "A Belter flies the *Y Que* through the Ring as a stunt. It slows at close to a "
    "hundred g, and he dies. Behind it are a station, a speed limit, and 1,373 gates "
    "to other stars, left by builders two billion years dead."],
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
    "Each mark is a year in the story, shaded by what that year rests on, brightest "
    "for the novels and dimmest for the one never stated. The axis breaks three "
    "times, and the last stretch, 2342 to 2353, is drawn twelve times larger. The "
    "only certain date in the series is on a gin label.",
]

# the gap bar makes the brief's closing point; it keeps no paragraph of its own
CLOSING = ""

# The page was cut to captions in September 2026, when Brian asked for the
# diagram to do the teaching. The brief's full text, with the corrections
# below, is in the first published version (commit 92d07d3).

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
