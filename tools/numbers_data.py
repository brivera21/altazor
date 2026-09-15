#!/usr/bin/env python3
"""The data behind numbers.html: seven ways of writing a number, and the line.

Systems follow Chrisomalis (2010) and Ifrah (2000); the number line studies are
Siegler and Opfer (2003) and Dehaene, Izard, Spelke and Pica (2008).
"""

import apa

# k, name, base, place value, zero, when and where, reach, note, source
SYSTEMS = [
    ("tally", "Tally marks", "grouped in fives", "no", "no",
     "the oldest way, and everywhere: the notched Ishango bone from the Congo is some 20,000 years old",
     "as far as patience goes; the marks grow with the number",
     "One mark for each thing counted, a fifth mark struck across to close a group. Every other system here began as a way to stop doing this.",
     "Chrisomalis 2010"),
    ("egypt", "Egyptian hieroglyphs", "10", "no", "no",
     "Egypt, from about 3200 BCE",
     "a million, which had its own sign, a kneeling god",
     "One sign for each power of ten, repeated as often as needed: a stroke, a heel bone, a coil of rope, a lotus. Additive, so 999 takes twenty-seven signs and order does not matter.",
     "Ifrah 2000; Chrisomalis 2010"),
    ("babylon", "Babylonian cuneiform", "60", "yes", "a placeholder, late",
     "Mesopotamia, from about 2000 BCE; the placeholder for an empty place appears around 300 BCE",
     "unbounded, the first system where a sign's value depended on its place",
     "Two signs only, a wedge for one and a chevron for ten, and the place a group stands in multiplies it by sixty. Sixty survives in our minutes, seconds and degrees.",
     "Chrisomalis 2010"),
    ("roman", "Roman numerals", "10, with a sign at each 5", "no", "no",
     "Rome, from about 500 BCE, and still on clocks, kings and film credits",
     "a few thousand in common use; a bar over a numeral multiplied it by a thousand",
     "Signs for 1, 5, 10, 50, 100, 500 and 1000, added up, with a smaller sign before a larger one subtracted. Fine for recording, hopeless for arithmetic, which Romans did on an abacus.",
     "Ifrah 2000"),
    ("chinese", "Chinese numerals", "10", "spoken, not written", "a sign for an empty place, medieval",
     "China, from the oracle bones of about 1300 BCE; the forms have barely changed",
     "unbounded, with a word for each power up to ten thousand and beyond",
     "A digit followed by the word for its power: two thousand, zero, two tens, four. The place is named rather than implied, so the system reads as the number is spoken, and needs no fixed columns.",
     "Chrisomalis 2010"),
    ("maya", "Maya numerals", "20", "yes", "yes, a shell",
     "Mesoamerica; the earliest zero on a dated monument is from 36 BCE",
     "unbounded; dates on the monuments run to millions of days",
     "A dot for one, a bar for five, a shell for nothing, stacked with the units at the bottom and each level worth twenty times the one below. For the calendar the third level counted eighteen, so a year of 360 days came out even; here the count is pure twenties.",
     "Chrisomalis 2010"),
    ("arabic", "Hindu-Arabic numerals", "10", "yes", "yes",
     "India, by the fifth century CE; through al-Khwarizmi's Baghdad in the ninth; into Europe with Fibonacci's Liber Abaci in 1202",
     "unbounded, ten signs for any number at all",
     "Ten signs, a place for each power of ten, and a sign for an empty place, so that the same nine digits and a zero write everything. The shapes differ by region; the system is one.",
     "Ifrah 2000; Chrisomalis 2010"),
]

PRESETS = [7, 12, 60, 365, 1999, 2026, 4096, 9999]

LINE = [
    ("log", "read logarithmically",
     "Where a child in second grade, or an adult with no number words past five, puts the numbers on a line from 0 to 100: ten lands near the middle, and the high numbers crowd the right end. Each step to the right is a multiplication, not an addition.",
     "Siegler and Opfer 2003; Dehaene, Izard, Spelke and Pica 2008"),
    ("lin", "read linearly",
     "Where a schooled adult puts them: equal steps for equal differences, ten a tenth of the way along. The linear line has to be learned, and in Siegler and Opfer's second graders it was not yet.",
     "Siegler and Opfer 2003"),
]

REFS = [
    (apa.book("Chrisomalis, S.", 2010, "Numerical notation: A comparative history", "Cambridge University Press",
              "https://doi.org/10.1017/CBO9780511676062"),
     "The systems, their structure and their dates."),
    (apa.book("Ifrah, G.", 2000, "The universal history of numbers: From prehistory to the invention of the computer", "John Wiley"),
     "The Egyptian, Roman and Hindu-Arabic histories."),
    (apa.article("Siegler, R. S., &amp; Opfer, J. E.", 2003,
                 "The development of numerical estimation: Evidence for multiple representations of numerical quantity",
                 "Psychological Science", 14, 3, "237-243", "https://doi.org/10.1111/1467-9280.02438"),
     "Second graders place numbers on a 0 to 100 line logarithmically; sixth graders linearly."),
    (apa.article("Dehaene, S., Izard, V., Spelke, E., &amp; Pica, P.", 2008,
                 "Log or linear? Distinct intuitions of the number scale in Western and Amazonian indigene cultures",
                 "Science", 320, 5880, "1217-1220", "https://doi.org/10.1126/science.1156540"),
     "Mundurucu adults, with few number words, map numbers to space logarithmically."),
    (apa.article("Blume, A., &amp; Stuart, D.", 2011, "Maya concepts of zero", "Proceedings of the American Philosophical Society", 155, 1, "51-88",
                 "https://www.jstor.org/stable/23056849"),
     "The shell and the early dates."),
    (apa.wiki("https://en.wikipedia.org/wiki/Egyptian_numerals"), "The signs and their values."),
    (apa.wiki("https://en.wikipedia.org/wiki/Babylonian_cuneiform_numerals"), "The wedge and the chevron, and the placeholder."),
    (apa.wiki("https://en.wikipedia.org/wiki/Roman_numerals"), "The rules and the bar for thousands."),
    (apa.wiki("https://en.wikipedia.org/wiki/Chinese_numerals"), "The characters and the rule for an empty place."),
    (apa.wiki("https://en.wikipedia.org/wiki/Maya_numerals"), "Dots, bars and the shell."),
    (apa.wiki("https://en.wikipedia.org/wiki/Ishango_bone"), "The tally, twenty thousand years old."),
]
