#!/usr/bin/env python3
"""The data behind nervous-systems.html: the body plans of nervous systems across
the animals, and how many neurons each animal has.

Neuron counts are the published whole-brain counts for vertebrates (the
isotropic fractionator, Herculano-Houzel and colleagues) and whole-nervous-
system counts for the invertebrates, as the Wikipedia list collects them.
Body masses are typical adults, from the same sources or the species'
articles, and are the roughest numbers here.
"""

import apa

# the plans: k, name, examples, a line on the plan, where the neurons sit, source
PLANS = [
    ("none", "no neurons", "sponges, placozoans",
     "Sponges have no nerve cells at all. Cells signal one another slowly with chemicals, and a sponge can close its openings over a minute or so; that is the whole repertoire.",
     "nowhere: the genes for synapses are there, the cells are not", "Wikipedia, Sponge"),
    ("net", "a nerve net", "hydras, jellyfish, sea anemones",
     "Neurons scattered through the body wall and joined into a mesh with no center. A touch anywhere spreads in every direction, which is enough to close a tentacle round prey or pulse a bell.",
     "everywhere, thinly; a hydra has a few thousand", "Wikipedia, Nerve net"),
    ("ladder", "a ladder", "flatworms",
     "The first head: a pair of ganglia at the front, next to the eyespots, with two nerve cords running back joined by rungs. Sensing is concentrated where the animal meets the world first.",
     "in the front ganglia and two cords", "Wikipedia, Planarian"),
    ("cord", "a ventral cord with ganglia", "earthworms, insects, crabs",
     "A brain above the gut at the front, a ring round the gut, and a chain of ganglia along the belly, one or a few per segment, each running its own legs. A headless insect can still walk.",
     "a brain at the front and a knot in every segment", "Wikipedia, Ventral nerve cord"),
    ("octopus", "a brain and eight half-brains", "octopuses, squid",
     "A large central brain between the eyes, two enormous optic lobes, and in each arm a cord with more neurons than the brain has, so that an arm can taste, grip and reach with little instruction from the center.",
     "two thirds of them in the arms", "Wikipedia, Cephalopod intelligence"),
    ("dorsal", "a dorsal cord and a brain", "fish to mammals",
     "One hollow cord along the back, inside a spine, swelling at the front into a brain that grows across the vertebrates from a few million cells to a hundred billion. Everything the animal does passes through it.",
     "nearly all in the brain, the rest in the cord", "Wikipedia, Central nervous system"),
]

# neuron counts: k, animal, neurons, body mass in grams, group, plan, note, source
ANIMALS = [
    ("sponge", "a sponge", 0, 100, "other", "none", "No neurons, and no need: it filters water and has nowhere to go.", "Wikipedia, Sponge"),
    ("hydra", "a hydra", 5600, 0.01, "other", "net", "A nerve net of a few thousand cells in an animal a centimeter long.", "Wikipedia, List of animals by number of neurons"),
    ("celegans", "a roundworm, C. elegans", 302, 1e-6, "other", "cord", "Every one of its 302 neurons is known by name, and every connection between them: the first complete wiring diagram of any animal.", "White et al. 1986"),
    ("leech", "a leech", 10000, 2, "other", "cord", "Ten thousand, in 21 nearly identical ganglia, which is why neuroscientists like it.", "Wikipedia, List of animals by number of neurons"),
    ("aplysia", "a sea slug, Aplysia", 18000, 300, "molluscs", "cord", "Eighteen thousand neurons, some of them so large they can be seen without a microscope; learning and memory were first watched at the level of single cells in it.", "Wikipedia, Aplysia californica"),
    ("fly", "a fruit fly", 139255, 0.0007, "insects", "cord", "The whole adult brain, every neuron and every synapse, was mapped in 2024: 139,255 cells.", "Dorkenwald et al. 2024"),
    ("ant", "an ant", 250000, 0.003, "insects", "cord", "A quarter of a million, in a head the size of a pinhead, enough to find its way home by the sky and the smell of the ground.", "Wikipedia, List of animals by number of neurons"),
    ("bee", "a honeybee", 960000, 0.1, "insects", "cord", "Nearly a million. A bee learns flowers, tells the hive where they are with a dance, and can count to four.", "Wikipedia, List of animals by number of neurons"),
    ("frog", "a frog", 16e6, 30, "vertebrates", "dorsal", "Sixteen million in the brain.", "Wikipedia, List of animals by number of neurons"),
    ("mouse", "a mouse", 71e6, 20, "mammals", "dorsal", "Seventy-one million, the most studied brain there is.", "Herculano-Houzel et al. 2006"),
    ("zebrafinch", "a zebra finch", 131e6, 15, "birds", "dorsal", "More neurons than a mouse in a brain half the size: birds pack them small and dense.", "Olkowicz et al. 2016"),
    ("rat", "a rat", 200e6, 300, "mammals", "dorsal", "Two hundred million.", "Herculano-Houzel et al. 2006"),
    ("pigeon", "a pigeon", 310e6, 400, "birds", "dorsal", "Three hundred million; a pigeon can learn to tell a Monet from a Picasso.", "Olkowicz et al. 2016"),
    ("octopus", "an octopus", 500e6, 3000, "molluscs", "octopus", "Half a billion, on a par with a dog's brain, but two thirds of them are in the arms.", "Young 1963"),
    ("cat", "a cat", 760e6, 4000, "mammals", "dorsal", "Three quarters of a billion.", "Jardim-Messeder et al. 2017"),
    ("raven", "a raven", 2.17e9, 1200, "birds", "dorsal", "Over two billion in a brain the size of a walnut, more than a dog, and the tool use and planning to match.", "Olkowicz et al. 2016"),
    ("dog", "a dog", 2.25e9, 15000, "mammals", "dorsal", "Two and a quarter billion, three times a cat's, though the counts were made on a few animals each.", "Jardim-Messeder et al. 2017"),
    ("macaque", "a macaque", 6.4e9, 6000, "primates", "dorsal", "Six billion, in a monkey the weight of a cat.", "Herculano-Houzel et al. 2007"),
    ("chimp", "a chimpanzee", 28e9, 45000, "primates", "dorsal", "Twenty-eight billion, a third of a human's, in a body two thirds the mass.", "Herculano-Houzel and Kaas 2011"),
    ("human", "a person", 86e9, 70000, "primates", "dorsal", "Eighty-six billion, sixteen billion of them in the cortex, more cortical neurons than any other animal.", "Azevedo et al. 2009"),
    ("elephant", "an African elephant", 257e9, 4e6, "mammals", "dorsal", "Three times a human's count, but 251 billion of them are in the cerebellum, running the trunk; the cortex has a third of ours.", "Herculano-Houzel et al. 2014"),
]

GROUPS = {"other": "#9a9a9a", "molluscs": "#f28cb0", "insects": "#ffb02e", "vertebrates": "#9be564", "birds": "#6ee7f2", "mammals": "#58a6ff", "primates": "#b48cf2"}

REFS = [
    (apa.article("White, J. G., Southgate, E., Thomson, J. N., &amp; Brenner, S.", 1986, "The structure of the nervous system of the nematode Caenorhabditis elegans",
                 "Philosophical Transactions of the Royal Society of London. B, Biological Sciences", 314, 1165, "1-340", "https://doi.org/10.1098/rstb.1986.0056"),
     "The 302 neurons of C. elegans and their wiring."),
    (apa.article("Dorkenwald, S., Matsliah, A., Sterling, A. R., Schlegel, P., Yu, S.-C., McKellar, C. E., Lin, A., Costa, M., Eichler, K., Yin, Y., Silversmith, W., Schneider-Mizell, C., Jordan, C. S., Brittain, D., Halageri, A., Kuehner, K., Ogedengbe, O., Morey, R., Gager, J., ... Murthy, M.", 2024,
                 "Neuronal wiring diagram of an adult brain", "Nature", 634, 8032, "124-138", "https://doi.org/10.1038/s41586-024-07558-y"),
     "The fruit fly's 139,255 neurons."),
    (apa.article("Young, J. Z.", 1963, "The number and sizes of nerve cells in Octopus",
                 "Proceedings of the Zoological Society of London", 140, 2, "229-254", "https://doi.org/10.1111/j.1469-7998.1963.tb01862.x"),
     "The octopus's half billion, two thirds of them in the arms."),
    (apa.article("Herculano-Houzel, S., Mota, B., &amp; Lent, R.", 2006, "Cellular scaling rules for rodent brains",
                 "Proceedings of the National Academy of Sciences", 103, 32, "12138-12143", "https://doi.org/10.1073/pnas.0604911103"),
     "The mouse and the rat."),
    (apa.article("Herculano-Houzel, S., Collins, C. E., Wong, P., &amp; Kaas, J. H.", 2007, "Cellular scaling rules for primate brains",
                 "Proceedings of the National Academy of Sciences", 104, 9, "3562-3567", "https://doi.org/10.1073/pnas.0611396104"),
     "The macaque."),
    (apa.article("Azevedo, F. A. C., Carvalho, L. R. B., Grinberg, L. T., Farfel, J. M., Ferretti, R. E. L., Leite, R. E. P., Jacob Filho, W., Lent, R., &amp; Herculano-Houzel, S.", 2009,
                 "Equal numbers of neuronal and nonneuronal cells make the human brain an isometrically scaled-up primate brain",
                 "Journal of Comparative Neurology", 513, 5, "532-541", "https://doi.org/10.1002/cne.21974"),
     "Eighty-six billion neurons in a human brain."),
    (apa.article("Herculano-Houzel, S., &amp; Kaas, J. H.", 2011, "Gorilla and orangutan brains conform to the primate cellular scaling rules: Implications for human evolution",
                 "Brain, Behavior and Evolution", 77, 1, "33-44", "https://doi.org/10.1159/000322729"),
     "The great apes, the chimpanzee among them."),
    (apa.article("Herculano-Houzel, S., Avelino-de-Souza, K., Neves, K., Porf&iacute;rio, J., Messeder, D., Mattos Feij&oacute;, L., Maldonado, J., &amp; Manger, P. R.", 2014,
                 "The elephant brain in numbers", "Frontiers in Neuroanatomy", 8, None, "46", "https://doi.org/10.3389/fnana.2014.00046"),
     "The elephant's 257 billion, 251 of them in the cerebellum."),
    (apa.article("Olkowicz, S., Kocourek, M., Lu&ccaron;an, R. K., Porte&scaron;, M., Fitch, W. T., Herculano-Houzel, S., &amp; N&#283;mec, P.", 2016,
                 "Birds have primate-like numbers of neurons in the forebrain", "Proceedings of the National Academy of Sciences", 113, 26, "7255-7260", "https://doi.org/10.1073/pnas.1517131113"),
     "The zebra finch, the pigeon and the raven."),
    (apa.article("Jardim-Messeder, D., Lambert, K., Noctor, S., Pestana, F. M., de Castro Leal, M. E., Bertelsen, M. F., Alagaili, A. N., Mohammad, O. B., Manger, P. R., &amp; Herculano-Houzel, S.", 2017,
                 "Dogs have the most neurons, though not the largest brain: Trade-off between body mass and number of neurons in the cerebral cortex of large carnivoran species",
                 "Frontiers in Neuroanatomy", 11, None, "118", "https://doi.org/10.3389/fnana.2017.00118"),
     "The cat and the dog."),
]
REFS += [(apa.wiki(f"https://en.wikipedia.org/wiki/{p}"), a) for p, a in [
    ("List_of_animals_by_number_of_neurons", "The counts collected, and the hydra, leech, ant, bee and frog."),
    ("Nervous_system", "The plans, from nets to cords."),
    ("Sponge", None), ("Nerve_net", None), ("Planarian", None), ("Ventral_nerve_cord", None), ("Cephalopod_intelligence", None),
    ("Central_nervous_system", None), ("Aplysia_californica", None),
]]
