#!/usr/bin/env python3
"""The data behind calendars.html: the two clocks in the sky that no
calendar can reconcile, the calendars people built anyway, and the same
day written in six of them.

The astronomical constants are the mean tropical year and mean synodic
month at 2000; the calendar rules are the arithmetic ones, the tabular
Islamic calendar and the fixed Hebrew calendar rather than the observed
moon; the Maya correlation is the GMT one, 584283.
"""

import apa

SKY = {
    "tropical_year": 365.24219,     # mean, 2000, days
    "synodic_month": 29.530589,     # mean, days
    "gregorian_year": 365.2425,     # 146097 / 400
    "julian_year": 365.25,
    "islamic_year": 354.36667,      # 10631 / 30, the tabular calendar
    "hebrew_year": 365.24682,       # 235 lunations of 29d 12h 793p over 19 years
    "seasons": [(79, "March equinox"), (172, "June solstice"), (265, "September equinox"), (355, "December solstice")],  # day of a common year, 0-based
}

# the calendars: k, name, kind, months of a common year as (name, days), the leap change, mean year, the rule, epoch and era, a line, in use
CALENDARS = [
    ("gregorian", "Gregorian", "solar", [("Jan", 31), ("Feb", 28), ("Mar", 31), ("Apr", 30), ("May", 31), ("Jun", 30), ("Jul", 31), ("Aug", 31), ("Sep", 30), ("Oct", 31), ("Nov", 30), ("Dec", 31)],
     "February takes a 29th day in years divisible by 4, except centuries not divisible by 400", 365.2425, "97 leap days in 400 years", "counted from the traditional year of the birth of Jesus; 15 October 1582 followed 4 October",
     "Pope Gregory XIII's correction of the Julian calendar: the same months, but three leap days dropped every four centuries. It gains a day on the seasons in about 3,200 years, which is why it is the world's civil calendar.", True),
    ("julian", "Julian", "solar", [("Jan", 31), ("Feb", 28), ("Mar", 31), ("Apr", 30), ("May", 31), ("Jun", 30), ("Jul", 31), ("Aug", 31), ("Sep", 30), ("Oct", 31), ("Nov", 30), ("Dec", 31)],
     "a 29th of February every fourth year, without exception", 365.25, "one leap day every 4 years", "from 1 January 45 BC, the year Julius Caesar set it going",
     "Caesar's calendar, made with the help of the Alexandrian astronomer Sosigenes: 365 days and a leap day every four years, which is 11 minutes a year too long. By 1582 it had drifted ten days from the sun; the Orthodox churches still keep it, now thirteen days behind.", True),
    ("persian", "Solar Hijri", "solar", [("Farvardin", 31), ("Ordibehesht", 31), ("Khordad", 31), ("Tir", 31), ("Mordad", 31), ("Shahrivar", 31), ("Mehr", 30), ("Aban", 30), ("Azar", 30), ("Dey", 30), ("Bahman", 30), ("Esfand", 29)],
     "Esfand takes a 30th day when the next equinox falls after noon in Tehran", 365.2422, "the year begins on the day of the March equinox, observed, so it never drifts", "years counted from Muhammad's journey to Medina in 622, in solar years",
     "The calendar of Iran and Afghanistan, and the most accurate in use: its new year, Nowruz, is fixed to the moment of the March equinox by astronomy rather than by rule, so it cannot drift. The first six months have 31 days, the next five 30, the last 29 or 30.", True),
    ("ethiopian", "Ethiopian", "solar", [("Mäskäräm", 30), ("Ṭəqəmt", 30), ("Ḫədar", 30), ("Taḫśaś", 30), ("Ṭərr", 30), ("Yäkatit", 30), ("Mägabit", 30), ("Miyazya", 30), ("Gənbot", 30), ("Säne", 30), ("Ḥamle", 30), ("Nähase", 30), ("Ṗagume", 5)],
     "the thirteenth month takes a sixth day every fourth year", 365.25, "one leap day every 4 years, as in the Julian calendar", "years counted from an Annunciation seven or eight years later than the Gregorian one; the year begins on 11 or 12 September",
     "The Egyptian year of twelve 30-day months and five days over, as reformed under Augustus with a leap day every four years, and kept in Ethiopia and Eritrea to this day, with the Coptic church in Egypt. Ethiopia is seven years behind the Gregorian count.", True),
    ("egyptian", "Egyptian civil", "solar, wandering", [("Thoth", 30), ("Phaophi", 30), ("Athyr", 30), ("Choiak", 30), ("Tybi", 30), ("Mechir", 30), ("Phamenoth", 30), ("Pharmuthi", 30), ("Pachons", 30), ("Payni", 30), ("Epiphi", 30), ("Mesore", 30), ("five days", 5)],
     "no leap day at all", 365.0, "none: the year is 365 days exactly, and slips a day against the sun every four years", "years counted from the accession of each king",
     "Twelve months of thirty days and five days over, with no correction, so the new year wandered through all the seasons and back once every 1,460 years or so, the Sothic cycle. Astronomers loved it, and Copernicus still used it, because every year was the same length.", False),
    ("republican", "French Republican", "solar", [("Vendémiaire", 30), ("Brumaire", 30), ("Frimaire", 30), ("Nivôse", 30), ("Pluviôse", 30), ("Ventôse", 30), ("Germinal", 30), ("Floréal", 30), ("Prairial", 30), ("Messidor", 30), ("Thermidor", 30), ("Fructidor", 30), ("the extra days", 5)],
     "a sixth extra day in years 3, 7 and 11, set so that the next year began on the equinox", 365.2422, "the year began on the day of the September equinox in Paris", "year 1 began 22 September 1792, the day after the Republic was proclaimed",
     "The Revolution's calendar: twelve months of thirty days named for the weather and the harvest, weeks of ten days, and five or six festival days to fill the year. Napoleon abolished it at the end of 1805, after twelve years.", False),
    ("haab", "Maya Haab", "solar, wandering", [("Pop", 20), ("Wo'", 20), ("Sip", 20), ("Sotz'", 20), ("Sek", 20), ("Xul", 20), ("Yaxk'in", 20), ("Mol", 20), ("Ch'en", 20), ("Yax", 20), ("Sak'", 20), ("Keh", 20), ("Mak", 20), ("K'ank'in", 20), ("Muwan", 20), ("Pax", 20), ("K'ayab", 20), ("Kumk'u", 20), ("Wayeb'", 5)],
     "no leap day", 365.0, "none: 365 days exactly, like the Egyptian year", "no year count; the Haab date repeats every 365 days, and with the Tzolk'in every 52 years",
     "Eighteen months of twenty days, named, plus five unlucky days, the Wayeb. It ran alongside the 260-day count, and the two together named each day uniquely within a round of 52 years; longer spans were counted in days from a fixed epoch, the Long Count.", False),
    ("tzolkin", "Maya Tzolk'in", "ritual, 260 days", [(f"{i + 1}", 20) for i in range(13)],
     "none", 260.0, "thirteen numbers and twenty names run together, so each of the 260 pairs comes round once", "no year count",
     "The 260-day count, older than the Maya themselves and still kept in the highlands of Guatemala: each day has a number from 1 to 13 and one of twenty names, both advancing together, so that 1 Imix is followed by 2 Ik' and 13 B'en by 1 Ix. Every day's pair is its character, and a child's name.", True),
    ("hebrew", "Hebrew", "lunisolar", [("Tishrei", 30), ("Cheshvan", 29), ("Kislev", 30), ("Tevet", 29), ("Shevat", 30), ("Adar", 29), ("Nisan", 30), ("Iyar", 29), ("Sivan", 30), ("Tammuz", 29), ("Av", 30), ("Elul", 29)],
     "a thirteenth month, Adar I of 30 days, in 7 years of every 19; Cheshvan and Kislev vary by a day to keep holidays off certain weekdays", 365.24682, "7 leap months in 19 years, the Metonic cycle; years of 353, 354, 355, 383, 384 or 385 days", "years counted from the creation as reckoned in the Middle Ages, 3761 BC; the year begins in September or October",
     "The calendar fixed by Hillel II in the fourth century from the older observed one: months follow the moon, and a thirteenth month is added seven times in nineteen years to hold Passover in spring. Its mean year is nearly seven minutes longer than the sun's, a day in about 216 years.", True),
    ("islamic", "Islamic", "lunar", [("Muharram", 30), ("Safar", 29), ("Rabi I", 30), ("Rabi II", 29), ("Jumada I", 30), ("Jumada II", 29), ("Rajab", 30), ("Sha'ban", 29), ("Ramadan", 30), ("Shawwal", 29), ("Dhu al-Qi'dah", 30), ("Dhu al-Hijjah", 29)],
     "the last month takes a 30th day in 11 years of every 30, in the tabular calendar; in practice each month begins with the sighting of the crescent", 354.36667, "no leap month, ever: the Quran forbids it, so the year is eleven days shorter than the sun's and the months go round the seasons in 33 years", "years counted from Muhammad's journey to Medina in 622, in lunar years; 1 Muharram 1 AH was 16 July 622",
     "The one purely lunar calendar in wide use: twelve months of the moon and nothing to hold them to the seasons, so Ramadan falls eleven days earlier each year and comes round the whole year in a third of a century. The tabular version drawn here is the arithmetic one used for planning; religious dates wait for the moon to be seen.", True),
    ("chinese", "Chinese", "lunisolar", [(f"{i + 1}", 30 if i % 2 == 0 else 29) for i in range(12)],
     "a thirteenth month in 7 years of every 19, placed by the position of the sun; months are 29 or 30 days by the actual new moons", 365.2422, "months begin at the astronomical new moon, in Beijing time; a month without a solar term is doubled", "years counted in cycles of sixty, named by ten stems and twelve branches; the year begins at the second new moon after the December solstice, in January or February",
     "The traditional calendar of China and its neighbors, now used for festivals: months begin at the new moon, computed rather than seen, and a leap month is added when a month contains no principal solar term, seven times in nineteen years. Each year takes an animal from a cycle of twelve and a stem from a cycle of ten.", True),
]

# the Maya day names and months, for the converter
TZOLKIN = ["Imix", "Ik'", "Ak'b'al", "K'an", "Chikchan", "Kimi", "Manik'", "Lamat", "Muluk", "Ok", "Chuwen", "Eb'", "B'en", "Ix", "Men", "Kib'", "Kab'an", "Etz'nab'", "Kawak", "Ajaw"]
HAAB = [m for m, _ in CALENDARS[6][3]]
HEBREW_MONTHS = ["Nisan", "Iyar", "Sivan", "Tammuz", "Av", "Elul", "Tishrei", "Cheshvan", "Kislev", "Tevet", "Shevat", "Adar", "Adar II"]
ISLAMIC_MONTHS = [m for m, _ in CALENDARS[9][3]]
MAYA_CORRELATION = 584283  # the GMT correlation: Julian day number of 0.0.0.0.0, 11 August 3114 BC (proleptic Gregorian)

REFS = [
    (apa.book("Reingold, E. M., &amp; Dershowitz, N.", 2018, "Calendrical calculations: The ultimate edition (4th ed.)", "Cambridge University Press", "https://doi.org/10.1017/9781107415058"),
     "The arithmetic of every calendar here: the tabular Islamic and fixed Hebrew rules, the Maya counts, the Julian and Gregorian conversions, and the epochs."),
    (apa.book("Richards, E. G.", 1998, "Mapping time: The calendar and its history", "Oxford University Press"),
     "The calendars' histories and their mean years."),
    (apa.book("Urban, S. E., &amp; Seidelmann, P. K. (Eds.)", 2013, "Explanatory supplement to the Astronomical Almanac (3rd ed.)", "University Science Books"),
     "The tropical year and synodic month, and the calendar chapter."),
    (apa.web("Walker, J.", 2015, "Calendar converter", "Fourmilab", "https://www.fourmilab.ch/documents/calendar/"),
     "The conversion algorithms as implemented here, checked against the converter."),
    (apa.wiki("https://en.wikipedia.org/wiki/Tropical_year"), "The mean tropical year at 2000, 365.24219 days, shortening by about half a second a century."),
    (apa.wiki("https://en.wikipedia.org/wiki/Lunar_month"), "The mean synodic month, 29.530589 days."),
    (apa.wiki("https://en.wikipedia.org/wiki/Hebrew_calendar"), "The molad of 29 days, 12 hours and 793 parts; the 19-year cycle; the postponement rules; the epoch."),
    (apa.wiki("https://en.wikipedia.org/wiki/Tabular_Islamic_calendar"), "The 30-year cycle with 11 leap years."),
    (apa.wiki("https://en.wikipedia.org/wiki/Maya_calendar"), "The Haab, the Tzolk'in, the Calendar Round and the Long Count, with the GMT correlation."),
]
REFS += [(apa.wiki(f"https://en.wikipedia.org/wiki/{p}"), None) for p in [
    "Gregorian_calendar", "Julian_calendar", "Solar_Hijri_calendar", "Ethiopian_calendar", "Egyptian_calendar", "French_Republican_calendar", "Islamic_calendar", "Chinese_calendar", "Metonic_cycle", "Julian_day",
]]
