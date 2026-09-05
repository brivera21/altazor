#!/usr/bin/env python3
"""The figures behind temperature.html, and where each one comes from.

Every temperature is in degrees Celsius. The page converts.

Two things this file is careful about. Body temperature has no single
number: it depends on the site, the hour and the person, so the normal
band comes from a meta-analysis that reports each site separately rather
than from the folk figure of 37. And the classic heat-loss percentages
are a textbook idealisation for one condition, a nude adult resting in
still air near 21 degrees, so they are labelled as that.
"""

# --- the survivable span, drawn as bands on the column -------------------
# (low, high, key, name, what happens there)
ZONES = [
    (10.0, 24.0, "cold4", "Profound hypothermia",
     "Below 24 degrees the heart may stop and the body can look dead: no "
     "pulse, no breathing, fixed pupils. It is also where the cold itself "
     "protects the brain, which is why resuscitation is attempted from "
     "temperatures that would otherwise be hopeless."),
    (24.0, 28.0, "cold3", "Severe hypothermia",
     "The heart muscle turns irritable and ventricular fibrillation "
     "becomes likely. Rough handling alone can set it off, so a patient "
     "this cold is moved gently."),
    (28.0, 32.0, "cold2", "Moderate hypothermia",
     "Shivering stops, which is the clinical marker of this stage, and "
     "consciousness fades. Atrial fibrillation is common. Some people "
     "undress, a confused response called paradoxical undressing."),
    (32.0, 35.0, "cold1", "Mild hypothermia",
     "Shivering is at its hardest and the metabolic rate climbs. "
     "Judgement and coordination go first, before the person feels in "
     "any danger."),
    (35.0, 36.16, "low", "Below the normal band",
     "Colder than the pooled normal range for a healthy adult, though a "
     "reading here from the armpit is unremarkable: the axilla averages "
     "35.97 degrees."),
    (36.16, 37.02, "norm", "The normal band",
     "The pooled range across sites in a meta-analysis of 7,636 healthy "
     "adults. The band is wide because it holds every site, every hour of "
     "the day and every person in those studies."),
    (37.02, 38.0, "warm1", "Warm, and not yet a fever",
     "Above the pooled band but under the usual cut-off. An oral reading "
     "of 37.5 at four in the afternoon is ordinary; the same reading at "
     "six in the morning is not."),
    (38.0, 39.0, "warm2", "Fever",
     "The common clinical cut-off is 38.0 degrees, and critical care "
     "often uses 38.3. The number means nothing without the site it was "
     "taken from."),
    (39.0, 41.0, "warm3", "High fever",
     "Still a raised set point rather than a failure of control. The body "
     "is defending this temperature, not losing to it."),
    (41.0, 48.0, "warm4", "Hyperpyrexia",
     "Above 41 degrees, and into the range where heat damages cells "
     "directly. Sustained above about 41.6 for long enough, proteins "
     "denature and organs fail."),
]

# --- points marked on the column ----------------------------------------
# (temperature, label, side, the story)
MARKS = [
    (11.8, "The coldest survival on record", "l",
     "A 27-month-old boy left home in winter near Krakow wearing pyjama "
     "tops, barefoot, in air at minus 7. He was found two hours later "
     "with no signs of life and fixed pupils. His core read 11.8 degrees "
     "ten minutes into rewarming on ECMO. He went home after 64 days and "
     "was neurologically well five years on."),
    (13.7, "Anna Bagenholm", "l",
     "The best known adult case: a skier trapped under ice in Norway for "
     "about 80 minutes in 1999, rewarmed from 13.7 degrees and recovered. "
     "Deliberate surgical cooling has gone lower still, below 10 degrees, "
     "but that is a different thing from an accident."),
    (36.6, "The modern mean", "l",
     "36.6 degrees, from 243,506 measurements of 35,488 outpatients. A "
     "later series of 618,306 oral readings agrees: 36.6, with a normal "
     "range of 36.3 to 36.8."),
    (37.0, "Wunderlich's 37", "l",
     "Carl Wunderlich set the figure in 1868 from about a million "
     "readings, taken in the armpit. Converting his round 37 gives 98.6 "
     "in Fahrenheit, which looks like a measurement to three figures and "
     "is nothing of the kind. The precision is an artefact of the "
     "arithmetic."),
    (40.0, "Heat stroke", "r",
     "Core above 40 degrees with the nervous system failing: confusion, "
     "seizures, coma. Well trained athletes reach 41.5 in a race without "
     "harm, so the time spent above the line matters more than the peak."),
    (46.5, "The hottest survival on record", "r",
     "A 52-year-old man admitted to Grady Memorial Hospital in Atlanta on "
     "10 July 1980 with heat stroke, at 46.5 degrees. He was discharged "
     "after 24 days. The case is a Guinness record rather than a "
     "published case report."),
]

# --- the daily rhythm ----------------------------------------------------
# oral, healthy young adults: mean 36.8, amplitude about 0.5 peak to trough
DAY = dict(mean=36.8, amp=0.25, nadir=6.0, zenith=17.0,
           cut_am=37.2, cut_pm=37.7)

# --- measurement sites, mean and the mean plus or minus two SD -----------
SITES = [
    ("Rectal", 37.04, 36.68, 37.40, 13,
     "Closest of the everyday sites to core, and the one the classic "
     "thresholds were written for. Accurate at rest, but it lags while "
     "the temperature is moving."),
    ("Tympanic", 36.64, 36.20, 37.08, 9,
     "Quick and popular, and an unreliable reflection of core: the ear "
     "canal is open to the air and poorly perfused when circulation is "
     "failing."),
    ("Oral", 36.57, 36.15, 36.99, 33,
     "The most studied site, and the source of most quoted figures. "
     "Biased by breathing, smoking, and hot or cold drinks."),
    ("Axillary", 35.97, 35.49, 36.45, 5,
     "About 0.6 degrees below oral, and the least reliable. Wunderlich's "
     "37 came from here, which cuts against the story of a modern "
     "decline rather than for it."),
]

# how far a peripheral thermometer can sit from a central one
PERIPHERAL = dict(lo=-1.44, hi=1.46, sens=64, spec=96,
                  ta_sens_adult=48, nc_sens=70)

# --- fever and hyperthermia, as two traces over hours --------------------
FEVER = dict(
    hours=30, base=36.8, peak=39.4,
    rise=2.0, plateau_end=14.0, fall_end=19.0,
    phases=[
        (0.0, 2.0, "The set point jumps",
         "Pyrogens reach the brain and the preoptic hypothalamus resets "
         "itself upward. Nothing has warmed yet: core is still 36.8, and "
         "the brain now reads that as too cold."),
        (2.0, 6.0, "Chills, and the climb",
         "The body does exactly what it would do out in the cold. Skin "
         "vessels clamp shut, the hands go cold and pale, hairs stand up, "
         "and shivering starts. The chill is the climb, not the fever. "
         "Every degree costs a tenth again of the metabolic rate."),
        (6.0, 14.0, "The plateau",
         "Core has caught the set point. The shivering stops and the "
         "person stops feeling cold, while sitting at 39 degrees."),
        (14.0, 19.0, "The set point drops",
         "The pyrogens clear, or an antipyretic cuts the prostaglandin "
         "that raised the set point. Now core is above the target, and "
         "the body sheds heat the way it sheds any excess: flushing and "
         "sweating."),
    ])

HEAT_ILL = dict(base=36.8, peak=41.5,
                note="In hyperthermia the set point never moves. Control "
                     "is intact and losing: heat is arriving, or being "
                     "made, faster than it can leave. That is why "
                     "aspirin does nothing for heat stroke and cooling "
                     "does everything.")

# --- heat in and heat out ------------------------------------------------
# Guyton and Hall's percentages for a nude adult at rest in still air
ROUTES = [
    ("Radiation", 60, "#e05f5f",
     "Infrared leaving the skin. The largest route at rest, and it "
     "reverses when the surroundings are hotter than the skin."),
    ("Convection", 15, "#e0985f",
     "Air warmed at the skin and carried away. Wind and a fan work here."),
    ("Conduction", 3, "#c9c05f",
     "Heat straight into whatever the body touches. Small, unless that "
     "something is water, which pulls heat about 25 times faster than "
     "air."),
    ("Evaporation", 22, "#58a6ff",
     "Water leaving the skin and the lungs. At rest most of this is "
     "insensible, about 600 to 700 millilitres a day, before any "
     "sweating."),
]

POWER = dict(rest=100, hard=1400, peak=2500,
             sweat_typ=1.0, sweat_max=3.0, sweat_rec=3.71,
             latent=2426,          # kJ per litre
             evap_w_per_lh=674,    # watts removed per litre an hour
             skin=35.0)

# --- the scales ----------------------------------------------------------
KB = 1.380649e-23     # J/K, fixed by definition since 20 May 2019
SCALES = {
    "C": ("Celsius", "&deg;C",
          "Zero at the freezing point of water, a hundred at its boiling "
          "point, though the scale is now defined off the kelvin: a "
          "temperature in kelvin is the Celsius figure plus 273.15."),
    "F": ("Fahrenheit", "&deg;F",
          "Water freezes at 32 and boils at 212, so 180 Fahrenheit "
          "degrees cover what 100 Celsius degrees cover and one "
          "Fahrenheit degree is five ninths of a Celsius one. 37 "
          "converts to exactly 98.6, which is where the false precision "
          "in the folk figure comes from."),
    "K": ("Kelvin", "K",
          "Zero at absolute zero, and since 2019 defined by fixing the "
          "Boltzmann constant at 1.380649 times ten to the minus 23 "
          "joules per kelvin. Temperature is the energy of molecular "
          "motion: at 310.15 kelvin the average molecule carries about "
          "0.040 electronvolts of it, and that number sets which "
          "chemistry can happen in a body."),
}
