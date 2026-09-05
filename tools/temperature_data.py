#!/usr/bin/env python3
"""The figures behind temperature.html, and where each one comes from.

Every temperature is in degrees Celsius. The page converts.

Two things this file is careful about. Body temperature has no single
number: it depends on the site, the hour and the person, so the normal
band comes from a meta-analysis that reports each site separately rather
than from the folk figure of {37}. And the classic heat-loss percentages
are a textbook idealisation for one condition, a nude adult resting in
still air near {21} degrees, so they are labelled as that.
"""

# --- the survivable span, drawn as bands on the column -------------------
# (low, high, key, name, what happens there)
ZONES = [
    (10.0, 24.0, "cold4", "Profound hypothermia",
     "Below {24} degrees the heart may stop and the body can look dead: no "
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
     "of {37.5} at four in the afternoon is ordinary; the same reading at "
     "six in the morning is not."),
    (38.0, 39.0, "warm2", "Fever",
     "The common clinical cut-off is {38.0} degrees, and critical care "
     "often uses {38.3}. The number means nothing without the site it was "
     "taken from."),
    (39.0, 41.0, "warm3", "High fever",
     "Still a raised set point rather than a failure of control. The body "
     "is defending this temperature, not losing to it."),
    (41.0, 48.0, "warm4", "Hyperpyrexia",
     "Above {41} degrees, and into the range where heat damages cells "
     "directly. Sustained above about {41.6} for long enough, proteins "
     "denature and organs fail."),
]

# --- points marked on the column ----------------------------------------
# (temperature, label, side, the story)
MARKS = [
    (11.8, "The coldest survival on record", "l",
     "A 27-month-old boy left home in winter near Krakow wearing pyjama "
     "tops, barefoot, in air at minus 7. He was found two hours later "
     "with no signs of life and fixed pupils. His core read {11.8} degrees "
     "ten minutes into rewarming on ECMO. He went home after 64 days and "
     "was neurologically well five years on."),
    (13.7, "Anna Bagenholm", "l",
     "The best known adult case: a skier trapped under ice in Norway for "
     "about 80 minutes in 1999, rewarmed from {13.7} degrees and recovered. "
     "Deliberate surgical cooling has gone lower still, below {10} degrees, "
     "but that is a different thing from an accident."),
    (36.6, "The modern mean", "l",
     "{36.6} degrees, from 243,506 measurements of 35,488 outpatients. A "
     "later series of 618,306 oral readings agrees: {36.6}, with a normal "
     "range of {36.3} to {36.8}."),
    (37.0, "Wunderlich's 37", "l",
     "Carl Wunderlich set the figure in 1868 from about a million "
     "readings, taken in the armpit. Converting his round 37 gives 98.6 "
     "in Fahrenheit, which looks like a measurement to three figures and "
     "is nothing of the kind. The precision is an artefact of the "
     "arithmetic."),
    (40.0, "Heat stroke", "r",
     "Core above {40} degrees with the nervous system failing: confusion, "
     "seizures, coma. Well trained athletes reach {41.5} in a race without "
     "harm, so the time spent above the line matters more than the peak."),
    (46.5, "The hottest survival on record", "r",
     "A 52-year-old man admitted to Grady Memorial Hospital in Atlanta on "
     "10 July 1980 with heat stroke, at {46.5} degrees. He was discharged "
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
         "itself upward. Nothing has warmed yet: core is still {36.8}, and "
         "the brain now reads that as too cold."),
        (2.0, 6.0, "Chills, and the climb",
         "The body does exactly what it would do out in the cold. Skin "
         "vessels clamp shut, the hands go cold and pale, hairs stand up, "
         "and shivering starts. The chill is the climb, not the fever. "
         "Every degree costs a tenth again of the metabolic rate."),
        (6.0, 14.0, "The plateau",
         "Core has caught the set point. The shivering stops and the "
         "person stops feeling cold, while sitting at {39} degrees."),
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


# =========================================================================
# Degree by degree, and what to do when someone collapses
# =========================================================================

# What a degree costs. Both figures are central estimates from small studies
# with wide variance, so the page draws the band as well as the line.
COST = dict(
    met=10, met_lo=7, met_hi=13,     # per cent of resting metabolic rate, per C
    hr=8, hr_lo=7, hr_hi=8.4,        # beats a minute per C, adults
    hr_child=12, hr_child_lo=9, hr_child_hi=14,
    hr_base=70, base=37.0,
    shiver=6,                        # shivering multiplies resting output
    met_note="Cooling a febrile patient by one degree Celsius lowers oxygen use by "
             "about 7 to 13 per cent, so the page draws the band rather than "
             "a line. Every figure comes from small studies of sedated "
             "patients, and the variance is wide.",
    hr_note="Liebermeister's rule, from the nineteenth century, put the rise "
            "at 8 beats a minute per degree Celsius. Modern series find 7 to 8.4 in "
            "adults and 9 to 14 in children, so the old convention holds up "
            "better than most of its age.")

# The lines that matter on the fine scale, and why each one is there.
LINES = [
    (38.0, "The usual fever cut-off", "#ffd24d",
     "The common clinical threshold, written for a rectal reading. Critical "
     "care often uses {38.3} instead. The number moves with the site: an "
     "armpit reading of {38.0} is a rectal reading nearer {38.6}."),
    (38.6, "Where cooling stops", "#31d67a",
     "The experimental stopping point for cooling a heat stroke patient, "
     "from a study that immersed volunteers and watched what happened after "
     "they came out. Stopping at {37.5} overshot to {35.7} in the oesophagus; "
     "stopping at {38.6} did not overshoot at all. Authorities put the line "
     "anywhere from {38.0} to {39.4}, so the spread is wider than it looks."),
    (40.0, "The heat stroke line", "#e0673f",
     "Above {40} with the nervous system failing is the definition of heat "
     "stroke. The definition needs both halves, and the brain half is the "
     "one a bystander can actually judge."),
    (41.6, "The critical thermal maximum", "#c02f2f",
     "The temperature at which human tissue starts to fail, from a single "
     "small 1978 study that heated sedated volunteers. The original finding "
     "was {41.6} to {42} degrees held for anywhere from 45 minutes to 8 hours, "
     "and the eight hours usually gets dropped in the retelling. People die "
     "below this line and survive above it."),
]

# The bands of the fine scale, with what each means for someone who is awake
# and answering. For someone who is not, see UNRESPONSIVE.
FINE = [
    (36.0, 37.5, "Ordinary", "#31d67a",
     "Inside the daily swing, or just above it. Nothing here needs doing."),
    (37.5, 38.3, "Low-grade", "#ffd24d",
     "A fever by most definitions, and by itself not an emergency in someone "
     "alert. What matters is how the person is, not the reading."),
    (38.3, 39.5, "A solid fever", "#f0a04b",
     "Uncomfortable, metabolically expensive, and still not in itself "
     "dangerous in a healthy adult who is alert and drinking."),
    (39.5, 40.0, "High", "#e0673f",
     "The territory where fever and heat illness start to look alike from "
     "the outside. The context and the mental state separate them."),
    (40.0, 43.0, "Over the line", "#c02f2f",
     "Above the heat stroke threshold. In someone alert this still calls for "
     "medical help; in someone confused or unresponsive it is heat stroke "
     "until proved otherwise."),
]

UNRESPONSIVE = (
    "An emergency at every temperature on this scale, and at temperatures "
    "below it. Unresponsiveness has many causes and none of them wait. What "
    "the thermometer changes is not the urgency but the guess: a high "
    "reading in a hot place points at heat stroke, a low one points "
    "somewhere else. Nothing on the scale downgrades the call.")

# Cooling rates, in degrees per minute, and how long each takes to bring a
# core of 41.5 down to the 38.6 stopping point.
COOLING = [
    ("Cold or ice water immersion", 0.20, "#58a6ff", "strong",
     "The fastest method there is, and about double any realistic "
     "alternative. Real patients at the Falmouth road race cooled at 0.22 "
     "degrees Celsius a minute in water near {10}. Guidelines put the useful "
     "water range anywhere from {1} to {26} degrees, which is an envelope around "
     "the evidence rather than a target."),
    ("A tarp, ice and water", 0.15, "#4a87d6", "moderate",
     "The person lies on a tarp with the sides held up, in ice and water. It "
     "cools nearly as fast as a tub, needs far less water, and is much safer "
     "for someone unresponsive: they are lying on their back in shallow "
     "water with the airway clear and reachable."),
    ("Cold water poured on, and hard fanning", 0.11, "#7fb4e8", "contested",
     "The sports medicine literature puts this at about half the rate of "
     "immersion. A formal review of the same evidence could not tell it "
     "apart from doing nothing. Both figures are in current guidelines, and "
     "the page shows the more generous one."),
    ("Ice packs to the neck, armpits and groin", 0.05, "#9fb6c4", "weak",
     "Popular, and close to useless on its own: the surface area is too "
     "small. It is worth doing alongside something else, not instead of it."),
    ("Shade and rest, and nothing else", 0.047, "#6b7280", "strong",
     "What the body manages by itself once the heat load stops. It is the "
     "line everything else has to beat."),
]

COOL_FROM, COOL_TO, COOL_TARGET = 41.5, 38.6, 30   # degrees, degrees, minutes

# What a bystander does, in the order it is done.
ACTIONS = [
    ("Call", "#58a6ff",
     "Emergency services first, and the two words that matter to the call "
     "handler are heat and unresponsive. Cooling starts at the same time if "
     "anyone else is there to start it. Waiting for the ambulance before "
     "cooling is the mistake the guidelines were written to stop."),
    ("Breathing", "#31d67a",
     "Not breathing normally means CPR, and the cooling carries on "
     "alongside it: one person compresses, another pours water. Breathing "
     "normally means the recovery position, on the side, in the shade, "
     "because vomiting is common and the airway comes first."),
    ("Cool", "#e0673f",
     "Clothes off, and cold water on the whole body, continuously, with "
     "hard fanning. Immersion is faster if there are enough people to hold "
     "the head and airway clear of the water, and a tarp with ice and water "
     "is nearly as fast and much safer. One person alone does not put an "
     "unresponsive body into a bathtub."),
    ("Stop", "#ffd24d",
     "Cooling stops near {38.6} degrees, or in the field when the person comes "
     "round or starts shivering hard, and then they are dried and covered. "
     "The stopping point exists because a body cooled to normal keeps "
     "falling: volunteers taken to {37.5} dropped to {35.7} afterwards."),
    ("Never", "#c02f2f",
     "Nothing by mouth to anyone who is not fully alert. No aspirin and no "
     "paracetamol: they lower a set point, and in heat stroke the set point "
     "is already normal, while both drugs land on the liver and the clotting "
     "the illness is attacking. No alcohol rubs, which poison through the "
     "skin. And nobody is left alone."),
]

# Telling a fever from heat stroke, and what to do when it cannot be told.
TELL = [
    ("The story", "Days of illness, a cough or a rash",
     "Hours in heat, a hot car, a hot job, or hard exertion"),
    ("The mind", "Rousable and making sense",
     "Confused, fighting, unsteady, seizing or not answering"),
    ("The skin", "Often shivering, with cold hands",
     "Very hot, sweaty after exertion, sometimes dry in the elderly"),
    ("The pace", "Rising and falling over days",
     "Getting worse over minutes"),
]
TELL_NOTE = (
    "Dry skin is the classic teaching and it is not reliable: most exertional "
    "heat stroke patients are soaked. When the two cannot be told apart the "
    "safe reading is heat stroke, because the harm is lopsided. Cooling "
    "someone with an infection wastes effort and makes them shiver. Not "
    "cooling someone with heat stroke for half an hour can kill them. And "
    "the first things done are the same either way.")


# =========================================================================
# What has actually been measured
# =========================================================================
# Whole-body metabolic rate against core temperature, as a percentage of the
# resting rate at 37 degrees. These are points, not a curve, and the page
# draws them as points on purpose. No published figure spans this range,
# because the two halves come from incompatible states: the shivering peak
# needs an awake person defending their temperature, and every measurement
# below about 33 degrees comes from someone anaesthetised, paralysed or on
# bypass, which is the only reason those temperatures were reachable at all.
#
# (core temperature, per cent of resting, source key, awake?)
MEASURED = [
    (41.8, 131, "zhu", False),
    (41.0, 128, "zhu", False),
    (40.0, 123, "zhu", False),
    (39.0, 118, "zhu", False),
    (37.0, 100, "base", True),
    (35.2, 490, "eyolfson", True),
    (33.0, 79, "flick", True),
    (32.0, 83, "shara", False),
    (27.0, 51, "shara", False),
    (25.4, 55, "hickey", False),
    (18.0, 38, "diop", False),
]

MSRC = {
    "base": ("Resting", "The rate every other figure on this panel is a "
             "percentage of."),
    "zhu": ("Zhu, 2003", "Twenty anaesthetised and paralysed patients heated "
            "to {41.8} degrees, with a catheter in the pulmonary artery. The "
            "climb decelerates: about 9 per cent a degree Celsius over the first "
            "two, "
            "then 5, then 4. Anaesthesia removes shivering and the work of "
            "breathing, so this is close to the pure effect of heat on "
            "tissue and probably understates an intact person."),
    "eyolfson": ("Eyolfson, 2001", "Peak shivering in fifteen people put in "
                 "eight degree water and then rewarmed to twenty, which "
                 "maximises the cold signal from the skin. Peak output was "
                 "4.9 times the resting rate, about 500 watts, at a core of "
                 "{35.2} degrees. Shivering is driven mostly by skin rather "
                 "than core, so a person at {35} degrees can sit anywhere "
                 "between resting and five times it depending on how cold "
                 "their skin is. Plotting this against core alone is a "
                 "simplification."),
    "flick": ("Flickinger, 2023", "Nine sedated volunteers cooled from {37} to "
              "33 with indirect calorimetry, the best controlled human data "
              "near normal. The fall is not linear: the largest single step "
              "was the first degree. When a participant began to shiver, "
              "their temperature stopped falling, which is why the "
              "experiment could go no further."),
    "shara": ("Sharabiani, 2025", "Two hundred and ninety-three children on "
              "cardiopulmonary bypass, twenty thousand minutes of "
              "measurement. The ratio of change per ten degrees is not "
              "constant: it is shallow near normal and steepens sharply "
              "below about {28}."),
    "hickey": ("Hickey, 1983", "Twelve men cooled to {25.4} degrees on bypass. "
               "Oxygen use fell by 45 per cent."),
    "diop": ("Diop, 2024", "Twenty-four adults cooled to {18} degrees for "
             "pulmonary thromboendarterectomy. This is the coldest whole-body "
             "measurement in a human that exists."),
}

# The regions of the scale, by what kind of person the numbers came from.
REGIMES = [
    (33.0, 43.0, "An awake person, or a sedated one", "#31d67a",
     "Above about {33} degrees the measurements come from people who are "
     "awake, or sedated but still their own thermostat. This is also the "
     "only part of the range where a person defends their temperature, which "
     "is why the shivering peak sits here and nowhere below."),
    (18.0, 33.0, "Anaesthetised, paralysed, or on bypass", "#58a6ff",
     "Every whole-body measurement below about {33} degrees was taken from a "
     "patient whose thermoregulation had been switched off by drugs or by a "
     "bypass machine. That is not a detail: it is the only reason anyone has "
     "ever been measured this cold. The two halves of this panel are two "
     "different physiological states, not two ends of one curve."),
    (10.0, 18.0, "Never measured in a person", "#6b7280",
     "No whole-body measurement of a human exists below {18} degrees. The "
     "figures that circulate for {15} and {10} degrees trace back to dogs cooled "
     "in 1950 and to a review from 1983 that cited papers it could not "
     "reach. They are extrapolations, and because the rate of change "
     "steepens as it gets colder, they are probably too high."),
]

# Heart rate the other way, from pooled measurements rather than convention.
HR_COLD = dict(slope=2.54, lo=19.3, hi=34.9, n=216,
               note="Two hundred and sixteen people brought in with "
                    "accidental hypothermia, cores from {19.3} to {34.9} "
                    "degrees. The pulse falls 2.54 beats a minute per "
                    "degree, a straight line. The textbook figure of half "
                    "the normal pulse at {28} degrees comes from the same "
                    "1950s lineage as the metabolic table and sits well "
                    "below what was actually counted.")


# =========================================================================
# The whole span, one degree at a time
# =========================================================================
# What is worth saying at each whole degree. Degrees not listed here take
# the line from the band they fall in. Every claim traces to something
# already cited above; nothing new is asserted here.
PER_DEGREE = {
    48: "The top of the drawing. No one has been recorded here.",
    47: "Above the record. No one is known to have come back from here.",
    46: "A man of 52 survived {46.5} with heat stroke in Atlanta in 1980 and "
        "went home after 24 days.",
    45: "The only documented survival above this line is that {46.5} record.",
    44: "Above the critical thermal maximum. Damage here is a question of how "
        "long, not whether.",
    43: "Past every metabolic measurement. Nothing has been measured in a "
        "person above {41.8}.",
    42: "The critical thermal maximum, from one 1978 study: {41.6} to {42} "
        "held for 45 minutes to 8 hours.",
    41: "28 per cent above resting. The climb decelerates: 9 per cent a "
        "degree Celsius at first, then 5, then 4.",
    40: "Above here with the nervous system failing is heat stroke. Athletes "
        "reach {41.5} in a race without harm.",
    39: "Measured 18 per cent above resting in anaesthetised patients heated "
        "deliberately. A raised set point.",
    38: "The usual fever cut-off, written for a rectal reading. Cooling a "
        "heat stroke patient stops at {38.6}.",
    37: "Wunderlich set this in 1868 from a million armpit readings. His "
        "round {37} converts to the false precision of 98.6.",
    36: "Shivering begins near {36.8} in someone whose skin is not cold. The "
        "modern mean is {36.6}.",
    35: "Peak shivering sits near here, almost five times resting. Reaching "
        "it depends on how cold the skin is.",
    34: "Judgement and coordination are already going, before the person "
        "feels in any danger.",
    33: "The coldest a sedated volunteer has been taken with the metabolism "
        "measured: 79 per cent of resting.",
    32: "Shivering stops, the marker of this stage. Consciousness fades and "
        "atrial fibrillation is common.",
    31: "Just below where shivering fails. Above this the body is still "
        "fighting the cold; below it, it has stopped.",
    30: "The middle of moderate hypothermia. Every metabolic figure here "
        "comes from patients on a bypass machine.",
    29: "Consciousness is gone or going, the pulse is near fifty, and the "
        "rhythm is unreliable.",
    28: "Ventricular fibrillation becomes the danger. Rough handling alone "
        "can set it off, so this patient is moved gently.",
    27: "Half the resting rate, from 293 children on bypass. The rate of "
        "change steepens below about here.",
    26: "Between the two bypass measurements either side. Nothing was "
        "measured at this degree itself.",
    25: "Oxygen use is a little over half of normal, measured in twelve men "
        "cooled on bypass.",
    24: "Below here a person can have no pulse, no breathing and fixed "
        "pupils and still be brought back.",
    23: "Approaching the top of profound hypothermia, where vital signs can "
        "be absent and recovery still possible.",
    22: "Someone has been recorded conscious and shivering at {22.9}. The "
        "stages are conventions, not guarantees.",
    21: "Just above where the pulse series stops, and far below where "
        "anything else has been counted.",
    20: "Surgical cooling has gone below here on purpose. Accidental "
        "survival this deep always needs a rewarming circuit.",
    19: "The bottom of the range in which anyone's pulse has been counted. "
        "Below it the falling line is extrapolation.",
    18: "The coldest measurement of a living person: 38 per cent of resting, "
        "in adults cooled for lung surgery.",
    17: "Inside the gap. The nearest real measurement is a degree warmer, "
        "and there is nothing below it.",
    16: "Deep enough that the heart is unlikely to be beating, and cold "
        "enough that the brain may not mind for a while.",
    15: "The figures quoted for this depth come from dogs cooled in 1950, "
        "not from people.",
    14: "Rewarming from this depth needs a bypass or an ECMO circuit, not "
        "blankets.",
    13: "Anna Bagenholm came back from {13.7} after 80 minutes under ice. "
        "Surgical cooling has gone lower still.",
    12: "Colder than any adult has been rewarmed from. Only that child sits "
        "below this line.",
    11: "A boy of 27 months, found at minus seven in Poland with no signs of "
        "life, read {11.8} and went home well.",
    10: "The bottom of the drawing, and past anything measured. Nothing in a "
        "living person has been recorded this cold.",
}

# Where the pulse figures hold. Below 19.3 and above 42 there is nothing.
PULSE = dict(cold_lo=19.3, cold_hi=34.9, cold_slope=2.54,
             warm_lo=37.0, warm_hi=42.0, warm_slope=8.0, base=70.0,
             gap_note="between {35} and {37} no series covers it")
