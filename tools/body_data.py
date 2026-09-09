#!/usr/bin/env python3
"""The systems on body.html, and the figures beside each one.

The outlines come from BodyParts3D, one segmented adult male. The numbers
do not: they come from the literature, and several of the numbers that
circulate for these systems turn out to rest on nothing measured. Where
that is the case the entry says so rather than repeating the figure.

Sources are in REFS, in APA form.
"""

import apa

# key, label, what the button says on the figure, and the note that opens
# when the system is chosen.
SYSTEMS = [
    ("skeletal", "Skeleton",
     "Bone, cartilage, the disks between the vertebrae and a few of the "
     "ligaments. The frame carries load and protects, and it is also where "
     "blood cells are made and where the body banks its calcium. The count "
     "of 206 is a naming convention rather than a measurement: it leaves out "
     "the small bones that only some people have."),
    ("muscular", "Muscles",
     "Skeletal muscle, the tissue under voluntary control. It is the "
     "heaviest tissue in the body and the one that moves the frame. In the "
     "front view the superficial sheets cover almost everything, which is "
     "what the depth control is for."),
    ("nervous", "Nervous system",
     "The brain and the fluid spaces inside it are traced from the model. "
     "Everything else here is drawn: the cord, the thirty-one pairs of "
     "spinal nerves, the twelve cranial pairs and the two autonomic "
     "outflows, laid over the traced skeleton at the measured position of "
     "each vertebra. The buttons above take the system apart."),
    ("cardiovascular", "Heart and vessels",
     "The heart wall and valves, the great vessels, and the named arteries "
     "and veins the model carries. The vessels here stop where the "
     "segmentation stopped, a few branches in. The small vessels, where "
     "almost all the length and all the exchange are, are not in any model "
     "of this kind."),
    ("respiratory", "Lungs",
     "The lobes of the lungs, the trachea and the main bronchi, the "
     "diaphragm under them and the cartilage of the larynx and nose. The "
     "lung is mostly surface: a volume the size of a large bottle holding a "
     "gas-exchange area the size of half a tennis court."),
    ("digestive", "Gut",
     "The tube from the esophagus to the rectum, with the liver, the "
     "gallbladder and the pancreas beside it. The liver is the largest of "
     "the visceral organs and sits high on the right, tucked under the ribs "
     "and the diaphragm."),
    ("urinary", "Kidneys",
     "Two kidneys behind the gut, the ureters that leave them, the bladder "
     "and the urethra. The kidneys sit against the back wall, higher than "
     "most people place them, and the right one rides lower because the "
     "liver is above it."),
    ("endocrine", "Glands",
     "The endocrine organs this model carries: the adrenal glands on top of "
     "the kidneys, the pituitary under the brain and the pineal body inside "
     "it. The thyroid gland is not in the model, though the cartilage named "
     "after it is."),
    ("lymphoid", "Spleen and thymus",
     "The spleen and the two lobes of the thymus, which is all of the "
     "lymphoid tissue this model holds. The vessels and the nodes, which "
     "are the system, are not segmented anywhere in it. The figure would be "
     "empty across the neck, the armpits, the belly and the groin, so the "
     "gap is worth stating rather than drawing."),
    ("reproductive", "Reproductive",
     "The model is one adult male, so this is the male set: the testes and "
     "their ducts, the seminal vesicles, the prostate and the erectile "
     "bodies. There is no female counterpart in the same data."),
    ("integumentary", "Skin",
     "The skin as a single surface, with the hair the model carries. It is "
     "the outline every other system is drawn inside, and on its own it is "
     "the closest thing here to a portrait of the person who was scanned."),
    ("sensory", "Eye and ear",
     "The eyeball and the outer ear, which is as far as the sense organs go "
     "in this model. The inner ear, the three smallest bones in the body "
     "among them, is not segmented."),
]

# What each system is worth knowing in numbers. (value, label, note)
# A note beginning with "no" flags a figure that circulates without a
# measurement behind it.
FACTS = {
    "skeletal": [
        ("206", "bones, by convention",
         "A naming convention, not a count. It excludes the bones only some "
         "people have."),
        ("about a third", "of knees carry a fabella",
         "A sesamoid bone in the tendon behind the knee, present in 31 per "
         "cent of knees in a review of 21,676, up from about 8 per cent a "
         "century ago."),
        ("10.5 kg", "skeleton, reference adult male",
         "From the reference values pooled for radiological protection, not "
         "from one body."),
    ],
    "muscular": [
        ("no agreed count", "of skeletal muscles",
         "Published figures run from about 600 to about 840, and the "
         "difference is bookkeeping: whether the two heads of the biceps "
         "are one muscle or two, whether the layers of multifidus are "
         "counted apart. Terminologia Anatomica gives no total."),
        ("29 kg", "skeletal muscle, reference adult male",
         "The heaviest tissue in the body, and about eight times the mass "
         "of the skin."),
        ("1 in 5", "people lack palmaris longus",
         "Absent in 20.3 per cent across 22,408 people, and the rate runs "
         "from 4.5 per cent to 41.7 per cent between populations."),
    ],
    "nervous": [
        ("86.1 billion", "neurons in the brain",
         "Counted by dissolving the tissue and counting nuclei, in four "
         "brains. The old figure of 100 billion never had a source."),
        ("69 billion", "of them in the cerebellum",
         "Four fifths of the neurons in about a tenth of the mass. The "
         "cerebral cortex has 16.3 billion in 82 per cent of the mass."),
        ("about 1 to 1", "glia to neurons",
         "Not the ten to one that textbooks carried for decades."),
    ],
    "cardiovascular": [
        ("5.6 L", "blood, reference adult male",
         "4.1 litres in the reference adult female, near 70 millilitres per "
         "kilogram in both."),
        ("about 106,000", "heartbeats a day",
         "From a mean 24 hour heart rate of 74 in healthy adults. The round "
         "100,000 comes from multiplying a resting rate by the whole day."),
        ("no measured length", "of the vessels",
         "The familiar 100,000 kilometres traces back to an extrapolation "
         "from capillary counts made in 1929. Working from measured "
         "capillary density gives something nearer 10,000 to 20,000, and no "
         "one has measured it."),
    ],
    "respiratory": [
        ("about 480 million", "alveoli",
         "Counted by design-based stereology in six lungs, and ranging from "
         "274 to 790 million. Larger lungs hold more alveoli rather than "
         "larger ones."),
        ("about 130 m2", "gas-exchange surface",
         "Roughly half a tennis court, not the whole court the comparison "
         "usually claims."),
    ],
    "digestive": [
        ("about 5.1 m", "small intestine, in a living person",
         "Measured during surgery in 287 people. A fresh cadaver measures "
         "longer because the muscle has no tone, and a fixed one shorter "
         "because it shrinks."),
        ("about 1.5 m", "colon",
         "Pooled across 5,741 adults."),
        ("1.8 kg", "liver, reference adult male",
         "The largest of the visceral organs, and about half again the mass "
         "of the brain."),
    ],
    "urinary": [
        ("200,000 to 2.5 million", "nephrons in one kidney",
         "A thirteenfold spread between people, settled before birth. The "
         "million that gets quoted is the middle of that range presented as "
         "though it were a constant."),
        ("about 180 L", "plasma filtered a day",
         "Arithmetic from the filtration rate rather than a separate "
         "measurement. About 1.5 litres leaves as urine."),
    ],
    "endocrine": [
        ("3", "endocrine organs in this model",
         "The adrenal glands, the pituitary and the pineal body. The "
         "thyroid, the parathyroids and the pancreatic islets are not "
         "segmented as endocrine tissue here."),
    ],
    "lymphoid": [
        ("2", "lymphoid organs in this model",
         "The spleen and the thymus. The nodes and the vessels are absent, "
         "so the system cannot be drawn from this data."),
        ("unsettled", "number of lymph nodes",
         "Three figures circulate, about 450, 500 to 600, and about 1,000, "
         "and none has a measurement behind it. The one systematic count, "
         "made by segmenting a single body, found about 1,200."),
    ],
    "reproductive": [],
    "integumentary": [
        ("1.90 m2", "skin surface, reference adult male",
         "1.66 square metres in the reference adult female. The two square "
         "metres usually quoted is the male figure rounded up."),
        ("3.3 kg", "skin, reference adult male",
         "About 4.5 per cent of body mass, and nearly twice the liver. It "
         "is the largest organ only if the skeleton at 10.5 kilograms and "
         "the muscle at 29 are counted as systems rather than organs."),
    ],
    "sensory": [],
}

WHOLE = [
    ("30 trillion", "human cells",
     "Five sixths of them red blood cells, which carry no nucleus and "
     "little mass."),
    ("38 trillion", "bacterial cells",
     "About 1.3 bacteria to every human cell. The ten to one ratio came "
     "from a single back of the envelope estimate in 1972 and was repeated "
     "for forty years."),
]

# Parts worth a sentence when they are chosen.
NOTES = {
    "femur": "The longest and heaviest bone. It carries the whole weight of "
             "the body above it and slants inward from hip to knee.",
    "mandible": "The only bone of the skull that moves.",
    "hyoid bone": "The one bone in the body that touches no other bone. It "
                  "hangs in the neck from muscle and ligament alone.",
    "patella": "A sesamoid bone: it formed inside a tendon rather than at a "
               "joint, and it holds the quadriceps tendon away from the "
               "knee so the muscle pulls at a better angle.",
    "atlas": "The first vertebra. It has no body, and the skull rocks on it "
             "for the nodding movement.",
    "axis": "The second vertebra. Its peg stands up into the atlas, and the "
            "head turns around that peg.",
    "sacrum": "Five vertebrae fused into one wedge, which is what carries "
              "the spine into the pelvis.",
    "diaphragm": "The muscle that does most of the work of breathing. It "
                 "domes up into the chest at rest and flattens to pull air "
                 "in.",
    "gluteus maximus": "The largest muscle by volume, and the one that "
                       "straightens the hip in climbing and rising.",
    "soleus": "Under the calf muscle, and worked hard in standing. Its "
              "squeeze on the deep veins is part of what returns blood from "
              "the leg.",
    "sartorius": "The longest muscle, running from the hip bone across the "
                 "thigh to the inside of the knee.",
    "cerebellum": "A tenth of the mass of the brain and four fifths of its "
                  "neurons.",
    "hippocampus": "Curved into the floor of each temporal lobe, and needed "
                   "for laying down new memories of events.",
    "thalamus": "Almost everything on its way to the cortex is relayed here "
                "first, smell excepted.",
    "medulla oblongata": "Where the brain meets the cord. Breathing and "
                         "blood pressure are regulated from here.",
    "corpus callosum": "About two hundred million fibres joining the two "
                       "hemispheres.",
    "optic nerve": "Not really a nerve but a tract of the brain, pushed out "
                   "to the eye during development.",
    "wall of heart": "Muscle that never rests. It has its own blood supply, "
                     "the coronary arteries, because the blood inside the "
                     "chambers is too far away to reach it.",
    "ascending aorta": "Everything the left ventricle pumps leaves through "
                       "here, at about five litres a minute at rest.",
    "inferior vena cava": "The return line from everything below the "
                          "diaphragm.",
    "liver": "The largest visceral organ. It receives blood twice over, "
             "from the heart and again from the gut, so what is absorbed "
             "passes it before it reaches the rest of the body.",
    "spleen": "A filter on the blood rather than the lymph. It culls old "
              "red cells and holds a reserve of white ones.",
    "lobe of thymus": "Where T cells learn not to attack the body. It is "
                      "largest in childhood and mostly fat by middle age.",
    "kidney": "It filters about 180 litres of plasma a day and gives back "
              "more than 99 per cent of it.",
    "urinary bladder": "Smooth muscle that stretches. The urge is a stretch "
                       "signal, not a full one.",
    "stomach": "It stores and grinds rather than absorbs. Almost all "
               "absorption happens further along.",
    "trachea": "Held open by cartilage rings that are open at the back, so "
               "the esophagus behind can bulge into the gap.",
    "skin": "The outline every other system is drawn inside.",
    "eyeball": "About 24 millimetres across, and almost the same size in a "
               "newborn as in an adult.",
    "prostate": "It sits around the urethra just below the bladder, which "
                "is why it is felt when it grows.",
    "pituitary gland": "The size of a pea, in a socket in the skull base, "
                       "and it sets the output of most of the other glands.",
    "adrenal gland": "A cap on each kidney. Its outer layer makes steroid "
                     "hormones and its core makes adrenaline.",
}

# What the model does not hold. Stated on the page rather than drawn.
GAPS = [
    "no lymph vessels and no lymph nodes",
    "no spinal cord, and no nerves outside the brain but the optic pair, "
    "which is why the nervous system on this page is drawn rather than "
    "traced",
    "no blood vessels smaller than the named branches",
    "no thyroid or parathyroid glands",
    "no female reproductive organs, since the model is one adult male",
    "no inner ear, and no bones of the middle ear",
]

REFS = [
    (apa.article(
        "Azevedo, F. A. C., Carvalho, L. R. B., Grinberg, L. T., Farfel, "
        "J. M., Ferretti, R. E. L., Leite, R. E. P., Jacob Filho, W., Lent, "
        "R., &amp; Herculano-Houzel, S.", 2009,
        "Equal numbers of neuronal and nonneuronal cells make the human "
        "brain an isometrically scaled-up primate brain",
        "Journal of Comparative Neurology", 517, 4, "532-541",
        "https://doi.org/10.1002/cne.21974"),
     "The neuron counts, from four brains."),
    (apa.article(
        "Berthaume, M. A., Di Federico, E., &amp; Bull, A. M. J.", 2019,
        "Fabella prevalence rate increases over 150 years, and rates of "
        "other sesamoid bones remain constant: A systematic review",
        "Journal of Anatomy", 235, 4, "731-740",
        "https://doi.org/10.1111/joa.12994"),
     "Why the count of 206 bones is a convention."),
    (apa.article(
        "Bertram, J. F., Douglas-Denton, R. N., Diouf, B., Hughson, M. D., "
        "&amp; Hoy, W. E.", 2011,
        "Human nephron number: Implications for health and disease",
        "Pediatric Nephrology", 26, 9, "1529-1533",
        "https://doi.org/10.1007/s00467-011-1843-8"),
     "The thirteenfold spread in nephron number."),
    (apa.article(
        "Bjerregaard, P.", 1983,
        "Mean 24 hour heart rate, minimal heart rate and pauses in healthy "
        "subjects 40-79 years of age", "European Heart Journal", 4, 1,
        "44-51",
        "https://doi.org/10.1093/oxfordjournals.eurheartj.a061370"),
     "Heartbeats over a whole day rather than at rest."),
    (apa.article(
        "Hounnou, G., Destrieux, C., Desme, J., Bertrand, P., &amp; Velut, "
        "S.", 2002, "Anatomical study of the length of the human intestine",
        "Surgical and Radiologic Anatomy", 24, 5, "290-294",
        "https://doi.org/10.1007/s00276-002-0057-y"),
     "Intestine length in 200 fresh cadavers."),
    (apa.article(
        "International Commission on Radiological Protection", 2002,
        "Basic anatomical and physiological data for use in radiological "
        "protection: Reference values (ICRP Publication 89)",
        "Annals of the ICRP", 32, "3-4", None,
        "https://doi.org/10.1016/S0146-6453(03)00002-2"),
     "The reference masses, volumes and surface areas."),
    (apa.article(
        "Mitsuhashi, N., Fujieda, K., Tamura, T., Kawamoto, S., Takagi, T., "
        "&amp; Okubo, K.", 2009,
        "BodyParts3D: 3D structure database for anatomical concepts",
        "Nucleic Acids Research", 37, "Database issue", "D782-D785",
        "https://doi.org/10.1093/nar/gkn613"),
     "The model every outline on this page is traced from."),
    (apa.article(
        "Ochs, M., Nyengaard, J. R., Jung, A., Knudsen, L., Voigt, M., "
        "Wahlers, T., Richter, J., &amp; Gundersen, H. J. G.", 2004,
        "The number of alveoli in the human lung",
        "American Journal of Respiratory and Critical Care Medicine", 169, 1,
        "120-124", "https://doi.org/10.1164/rccm.200308-1107OC"),
     "The alveolar count, by design-based stereology."),
    (apa.article(
        "Poole, D. C., Kano, Y., Koga, S., &amp; Musch, T. I.", 2021,
        "August Krogh: Muscle capillary function and oxygen delivery",
        "Comparative Biochemistry and Physiology Part A", 253, None,
        "110852", "https://doi.org/10.1016/j.cbpa.2020.110852"),
     "Where the figure for vessel length came from."),
    (apa.article(
        "Qatarneh, S. M., Kiricuta, I.-C., Brahme, A., Tiede, U., &amp; "
        "Lind, B. K.", 2006,
        "Three-dimensional atlas of lymph node topography based on the "
        "Visible Human data set", "The Anatomical Record Part B", "289B", 3,
        "98-111", "https://doi.org/10.1002/ar.b.20102"),
     "The one systematic count of lymph nodes in a body."),
    (apa.article(
        "Sender, R., Fuchs, S., &amp; Milo, R.", 2016,
        "Revised estimates for the number of human and bacteria cells in "
        "the body", "PLOS Biology", 14, 8, "e1002533",
        "https://doi.org/10.1371/journal.pbio.1002533"),
     "The cell counts, and the end of the ten to one ratio."),
    (apa.book(
        "Moore, K. L., Dalley, A. F., &amp; Agur, A. M. R.", 2018,
        "Clinically oriented anatomy (8th ed.)", "Wolters Kluwer"),
     "The courses of the spinal, cranial and autonomic nerves, with "
     "Standring, which the drawn nervous system follows."),
    (apa.book(
        "Standring, S. (Ed.)", 2020,
        "Gray's anatomy: The anatomical basis of clinical practice "
        "(42nd ed.)", "Elsevier"),
     "The anatomy the part names follow, the nerve courses, and a work "
     "that gives no total for the muscles."),
    (apa.article(
        "Yammine, K.", 2013,
        "Clinical prevalence of palmaris longus agenesis: A systematic "
        "review and meta-analysis", "Clinical Anatomy", 26, 6, "709-718",
        "https://doi.org/10.1002/ca.22289"),
     "How much the muscles vary between people."),
    (apa.article(
        "Zhou, R., Orkin, B. A., Williams, J. M., Serici, A., &amp; Poirier, "
        "J.", 2020,
        "In vivo small bowel length is longer than in formalin-fixed "
        "cadavers",
        "International Journal of Surgery Research and Practice", 6, None,
        "107", "https://doi.org/10.23937/2378-3397/1410107"),
     "Intestine length measured in living people."),
]
