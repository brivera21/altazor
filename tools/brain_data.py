#!/usr/bin/env python3
"""The data behind brain.html: the human brain from outside, from inside,
and over a lifetime.

The cell counts are Azevedo and colleagues' 2009 isotropic-fractionator
figures; the masses by age are Dekaban and Sadowsky's 1978 autopsy series;
the fibre lengths are Marner and colleagues' 2003 stereology; the energy
share is Raichle and Gusnard's 2002 appraisal.
"""

import apa

# the whole organ
WHOLE = {
    "mass_g": 1400, "body_pct": 2, "energy_pct": 20, "watts": 20,
    "neurons": 86e9, "glia": 85e9, "synapses": "a hundred trillion or more",
    "cortex_neurons": 16e9, "cerebellum_neurons": 69e9, "rest_neurons": 0.7e9,
    "cortex_mass_pct": 82, "cerebellum_mass_pct": 10, "rest_mass_pct": 8,
    "cortex_mm": "2 to 4", "cortex_m2": 0.24, "folded": "two thirds",
    "fibres_km_m": 176000, "fibres_km_f": 149000,
    "blood_ml_min": 750, "blood_pct": 15,
}

# the outside: k, name, kind, a line, a number, source
OUTSIDE = [
    ("frontal", "the frontal lobe", "A lobe", "The front third of the cortex, and the last part to finish wiring, in the mid twenties. Planning, holding a goal in mind, deciding not to act, working memory, and at its back edge the strip that moves the body.",
     "about a third of the cortex; a person's is no larger, for their brain, than a chimpanzee's", "Wikipedia, Frontal lobe; Semendeferi et al. 2002"),
    ("parietal", "the parietal lobe", "A lobe", "Behind the central sulcus. Its front strip feels the body: touch, pressure, heat, the position of the limbs. Behind that it builds the sense of space, where things are and where the hand must go to reach them, and handles numbers and reading.",
     "the body's touch map here gives the fingertips and lips more cortex than the whole trunk", "Wikipedia, Parietal lobe"),
    ("temporal", "the temporal lobe", "A lobe", "The lobe behind the temples, under the lateral fissure. Hearing arrives at its upper surface; the recognition of faces, objects and words happens along it; tucked inside its inner wall is the hippocampus, where new memories are made.",
     "damage on the left side can take away the understanding of speech and leave hearing intact", "Wikipedia, Temporal lobe"),
    ("occipital", "the occipital lobe", "A lobe", "The back of the brain, and almost entirely about seeing. The image from the eyes lands here upside down and mirrored, the left half of the world on the right, and is taken apart into edges, colours, motion and depth before being sent forward.",
     "the smallest lobe, and the fovea, the eye's central pin-point, gets a large share of it", "Wikipedia, Occipital lobe"),
    ("cerebellum", "the cerebellum", "A part", "The little brain under the back of the big one, folded so finely that unrolled it would be nearly as wide as the cortex. It times and smooths movement, learns skills like riding a bicycle, and holds four fifths of all the brain's neurons in a tenth of its mass.",
     "69 billion neurons in about 150 grams", "Azevedo et al. 2009"),
    ("brainstem", "the brainstem", "A part", "The stalk joining the brain to the spinal cord: midbrain, pons and medulla. Breathing, heart rate, blood pressure, swallowing, sleep and waking are run from here, below the reach of choice; every nerve to and from the body passes through it.",
     "ten of the twelve cranial nerves leave the brain from here", "Wikipedia, Brainstem"),
    ("motor", "the motor cortex", "A strip", "The strip just in front of the central sulcus. Each point on it moves one part of the opposite side of the body, laid out from the toes at the top to the face at the bottom, with the hands and mouth given far more room than their size.",
     "a signal from here reaches a foot in about 30 milliseconds", "Wikipedia, Primary motor cortex"),
    ("sensory", "the somatosensory cortex", "A strip", "The strip just behind the central sulcus, the body's touch map, in the same order as the motor strip beside it: the opposite side of the body, feet at the top, face at the bottom, and hands and lips enlarged.",
     "two points on a fingertip 2 mm apart are felt as two; on the back, 40 mm apart", "Wikipedia, Postcentral gyrus; Wikipedia, Two-point discrimination"),
    ("broca", "Broca's area", "A patch", "In the lower frontal lobe, on the left side in most people. Damage here leaves understanding intact but speech halting and stripped of grammar, as Paul Broca found in 1861 in a patient who could say only one syllable.",
     "described in 1861, the first function pinned to a place", "Wikipedia, Broca's area"),
    ("wernicke", "Wernicke's area", "A patch", "At the back of the upper temporal lobe, on the left. Damage here leaves speech fluent and grammatical but empty of sense, and understanding of others' speech gone, as Carl Wernicke described in 1874.",
     "described in 1874; Broca's area and this one are joined by a bundle of fibres, the arcuate fasciculus", "Wikipedia, Wernicke's area"),
    ("auditory", "the auditory cortex", "A patch", "On the upper surface of the temporal lobe, mostly hidden inside the lateral fissure. Sound arrives here laid out by pitch, low tones at one end and high at the other, like the keyboard it came from in the ear.",
     "pitch is mapped from about 20 to 20,000 hertz, low at the front", "Wikipedia, Auditory cortex"),
    ("visual", "the visual cortex", "A patch", "The tip of the occipital lobe, where the optic nerves' signal first reaches the cortex. It holds a map of the visual field, the centre of gaze taking up most of it, and is the first of some thirty areas that see.",
     "the central 10 degrees of view take about half of the map", "Wikipedia, Visual cortex"),
]

# the inside, a cut down the middle: k, name, kind, a line, a number, source
INSIDE = [
    ("callosum", "the corpus callosum", "A bridge", "The thick band of fibres joining the two hemispheres, the largest white-matter structure in the brain. Cut it, as was once done for severe epilepsy, and the two halves can no longer tell each other what they see.",
     "about 200 million axons", "Wikipedia, Corpus callosum"),
    ("thalamus", "the thalamus", "A relay", "Two eggs of grey matter at the very centre. Nearly everything the cortex receives, sight, hearing, touch, passes through here first, and the cortex talks back to it constantly; it is the switchboard of attention and of sleep.",
     "every sense but smell is routed through it", "Wikipedia, Thalamus"),
    ("hypothalamus", "the hypothalamus", "A regulator", "Below the thalamus, the size of an almond. It holds body temperature, thirst, hunger, the daily clock and the sex hormones steady, and it runs the pituitary below it, and through that most of the body's glands.",
     "about 4 grams, running the body's chemistry", "Wikipedia, Hypothalamus"),
    ("pituitary", "the pituitary", "A gland", "A pea hanging from the hypothalamus on a stalk, seated in a hollow of the skull. It releases the hormones that set growth, milk, the thyroid, the adrenals, the ovaries and testes, and water balance.",
     "about half a gram", "Wikipedia, Pituitary gland"),
    ("cingulate", "the cingulate cortex", "A belt", "The strip of cortex wrapped around the corpus callosum on the inner face of each hemisphere. Its front part is busy in effort, error, pain and choosing between options; its back part in memory and the sense of self.",
     "part of the limbic system, the old ring around the brainstem", "Wikipedia, Cingulate cortex"),
    ("hippocampus", "the hippocampus", "Deep in the temporal lobe", "A curled ridge on the inner wall of each temporal lobe, not on the midline but drawn here in its place. New memories of events and places are made here; without it, as in the patient H. M., nothing after the injury is kept, though old memories and skills stay.",
     "about 3 cubic centimetres each side; London taxi drivers' are larger at the back", "Wikipedia, Hippocampus; Maguire et al. 2000"),
    ("amygdala", "the amygdala", "Deep in the temporal lobe", "An almond in front of each hippocampus, drawn here in its place. It tags what is seen and heard with fear and value, and sets off the body's alarm before the cortex has finished working out what the thing is.",
     "about 1.5 cubic centimetres each side", "Wikipedia, Amygdala"),
    ("basal", "the basal ganglia", "Deep, either side of the thalamus", "Clusters of grey matter around the thalamus, drawn here in their place. They choose and start movements and habits and hold them back; their dopamine supply from the midbrain fails in Parkinson's disease.",
     "the striatum, their largest part, holds most of the brain's dopamine", "Wikipedia, Basal ganglia"),
    ("midbrain", "the midbrain", "The brainstem", "The top of the brainstem. Reflexes of the eyes and ears live here, the pupil, the startle at a loud sound, and so does the substantia nigra, whose dopamine cells feed the basal ganglia.",
     "about 2 centimetres long", "Wikipedia, Midbrain"),
    ("pons", "the pons", "The brainstem", "The bulge below the midbrain, a bridge of fibres between the two halves of the cerebellum and a relay between cortex and cerebellum. It shares the control of breathing with the medulla and generates the dreaming stage of sleep.",
     "about 2.5 centimetres long", "Wikipedia, Pons"),
    ("medulla", "the medulla", "The brainstem", "The last part of the brain before the spinal cord. Breathing, heart rate, blood pressure, swallowing, vomiting and coughing are run from here without any need of thought; the nerve fibres from each side of the cortex cross over here to the other side of the body.",
     "about 3 centimetres long", "Wikipedia, Medulla oblongata"),
    ("cerebellum", "the cerebellum", "A part", "Cut down the middle, the cerebellum shows its tree of white matter, the arbor vitae, branching into leaves of cortex so tightly folded that four fifths of the brain's neurons fit in a tenth of its mass.",
     "69 billion neurons", "Azevedo et al. 2009"),
    ("cord", "the spinal cord", "The way out", "Below the medulla the brain becomes the spinal cord, a finger-thick cable running down the spine, giving off a pair of nerves at each vertebra, and doing some of its own thinking: the reflex that pulls a hand from a flame never reaches the brain first.",
     "about 45 centimetres long, a centimetre across", "Wikipedia, Spinal cord"),
]

# brain mass by age, grams: Dekaban and Sadowsky 1978 (ranges taken at their midpoints)
GROWTH = [
    # age, male, female
    (0, 380, 360),
    (1, 970, 940),
    (2, 1120, 1040),
    (3, 1270, 1090),
    (11, 1440, 1260),
    (20, 1450, 1310),
    (58, 1370, 1250),
    (83, 1310, 1170),
]
GROWTH_NOTES = [
    (0, "At birth the brain is about a quarter of its adult mass, while the body is about a twentieth of its own; the head is why birth is hard."),
    (1, "The first year adds more mass than any other: most of it is not new neurons but their branches, and the fat sheaths growing around their fibres."),
    (3, "By three the brain has quadrupled since birth and is near nine tenths of its adult size; the number of connections between neurons is at its peak and will be pruned back over the next decade."),
    (11, "Growth is nearly done, but the wiring is not: the frontal lobes go on insulating their fibres into the mid twenties."),
    (20, "The peak. From here the mass holds steady for about thirty years, and the myelinated fibres begin their slow loss, about a tenth a decade."),
    (58, "Decline begins around forty-five to fifty, faster in the white matter than the grey."),
    (83, "By the mid eighties the brain has lost about a tenth of its peak mass, and about half its myelinated fibre length."),
]

REFS = [
    (apa.article("Azevedo, F. A. C., Carvalho, L. R. B., Grinberg, L. T., Farfel, J. M., Ferretti, R. E. L., Leite, R. E. P., Jacob Filho, W., Lent, R., &amp; Herculano-Houzel, S.", 2009,
                 "Equal numbers of neuronal and nonneuronal cells make the human brain an isometrically scaled-up primate brain", "Journal of Comparative Neurology", 513, 5, "532-541", "https://doi.org/10.1002/cne.21974"),
     "86 billion neurons and 85 billion other cells; 16 billion neurons in the cortex, 69 billion in the cerebellum; the masses of the parts."),
    (apa.article("Dekaban, A. S., &amp; Sadowsky, D.", 1978, "Changes in brain weights during the span of human life: Relation of brain weights to body heights and body weights",
                 "Annals of Neurology", 4, 4, "345-356", "https://doi.org/10.1002/ana.410040410"),
     "Brain mass by age from 4,736 autopsies: the quadrupling by three, the peak near twenty, the loss of about a tenth by the mid eighties."),
    (apa.article("Marner, L., Nyengaard, J. R., Tang, Y., &amp; Pakkenberg, B.", 2003, "Marked loss of myelinated nerve fibers in the human brain with age",
                 "Journal of Comparative Neurology", 462, 2, "144-152", "https://doi.org/10.1002/cne.10714"),
     "176,000 km of myelinated fibre in a man of twenty and 149,000 in a woman, falling by about a tenth a decade to 97,200 and 82,000 at eighty."),
    (apa.article("Raichle, M. E., &amp; Gusnard, D. A.", 2002, "Appraising the brain's energy budget",
                 "Proceedings of the National Academy of Sciences", 99, 16, "10237-10239", "https://doi.org/10.1073/pnas.172399499"),
     "The brain is 2 percent of the body's mass and uses 20 percent of its energy at rest."),
    (apa.article("Toro, R., Perron, M., Pike, B., Richer, L., Veillette, S., Pausova, Z., &amp; Paus, T.", 2008, "Brain size and folding of the human cerebral cortex",
                 "Cerebral Cortex", 18, 10, "2352-2357", "https://doi.org/10.1093/cercor/bhm261"),
     "About 0.12 square metres of cortex per hemisphere, unfolded."),
    (apa.article("Semendeferi, K., Lu, A., Schenker, N., &amp; Damasio, H.", 2002, "Humans and great apes share a large frontal cortex",
                 "Nature Neuroscience", 5, 3, "272-276", "https://doi.org/10.1038/nn814"),
     "The human frontal cortex is about the share of the whole that a great ape's is."),
    (apa.article("Maguire, E. A., Gadian, D. G., Johnsrude, I. S., Good, C. D., Ashburner, J., Frackowiak, R. S. J., &amp; Frith, C. D.", 2000, "Navigation-related structural change in the hippocampi of taxi drivers",
                 "Proceedings of the National Academy of Sciences", 97, 8, "4398-4403", "https://doi.org/10.1073/pnas.070039597"),
     "London taxi drivers' posterior hippocampi are larger than controls', and more so with years on the job."),
]
REFS += [(apa.wiki(f"https://en.wikipedia.org/wiki/{p}"), a) for p, a in [
    ("Human_brain", "The organ in general: mass, blood flow, the lobes and what they do."),
    ("Cerebral_cortex", "Thickness 2 to 4 mm; two thirds of the surface hidden in the folds."),
    ("Frontal_lobe", None), ("Parietal_lobe", None), ("Temporal_lobe", None), ("Occipital_lobe", None), ("Brainstem", None),
    ("Primary_motor_cortex", None), ("Postcentral_gyrus", None), ("Two-point_discrimination", None), ("Broca%27s_area", None), ("Wernicke%27s_area", None), ("Auditory_cortex", None), ("Visual_cortex", None),
    ("Corpus_callosum", None), ("Thalamus", None), ("Hypothalamus", None), ("Pituitary_gland", None), ("Cingulate_cortex", None), ("Hippocampus", None), ("Amygdala", None), ("Basal_ganglia", None),
    ("Midbrain", None), ("Pons", None), ("Medulla_oblongata", None), ("Spinal_cord", None),
]]
