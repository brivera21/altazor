#!/usr/bin/env python3
"""Generate tree-of-life.html, animals.html, mammals.html, primates.html.

Four cladograms sharing one renderer: the whole tree of life at the level
of domains and supergroups, the main divisions of the animals, the main
divisions of the mammals, and the branches that lead to and through the
primates. Root at the left, living groups at the right; every living tip
carries the Wikipedia article's photograph, fetched at view time from the
REST summary endpoint (the same pattern as the chess champions page), and
a node under the cursor fills the side card with the photo, what the
group is, and where its placement comes from.

Sources are pinned per node: Woese 1990 and Hug 2016 for the domains,
Burki 2020 for the eukaryote supergroups, Schultz 2023 and Dunn 2014 for
the animal phyla with Zhang 2013 for the counts, the Mammal Diversity
Database and Upham 2019 for the mammals, Perelman 2011 for the primates.
Species counts are approximate and dated in the cards.

Usage: python3 build_life.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent

# A node: name, blurb, source; optional count (display string), hl
# (highlight as a familiar group), kids, and w: Wikipedia article titles
# to try, in order, for a representative photo (the first with a summary
# thumbnail wins; no thumbnail anywhere means no photo, never a stand-in).
def N(name, blurb, source, count=None, hl=False, kids=None, w=None):
    d = {"n": name, "b": blurb, "s": source}
    if count: d["c"] = count
    if hl: d["hl"] = True
    if kids: d["k"] = kids
    if w: d["w"] = w
    return d


TREE_OF_LIFE = N(
    "Life", "The last universal common ancestor of everything alive. Its two "
    "deepest branches are Bacteria and Archaea; the eukaryotes arise later, "
    "from within the archaeal side.", "Woese and others 1990; Hug and others 2016",
    w=["Last universal common ancestor"],
    kids=[
        N("Bacteria",
          "The larger share of the tree's genetic diversity, most of it "
          "microbial and much of it never cultivated, including the vast "
          "Candidate Phyla Radiation mapped in 2016.",
          "Hug and others 2016", w=["Bacteria"]),
        N("Archaea",
          "Microbes with distinct membranes and machinery, first recognized "
          "as a separate domain by Carl Woese in 1990.",
          "Woese and others 1990", w=["Archaea"], kids=[
            N("DPANN", "A radiation of tiny archaea with reduced genomes, "
              "many living attached to other microbes.", "Hug and others 2016",
              w=["DPANN", "Nanoarchaeum"]),
            N("Euryarchaeota", "Methane makers, salt lovers and heat lovers: "
              "the classic archaea of swamps, salterns and hot springs.",
              "Hug and others 2016", w=["Euryarchaeota", "Halobacterium"]),
            N("TACK", "The superphylum closest to the root of the eukaryote "
              "story, named for its first four phyla.", "Hug and others 2016",
              w=["TACK", "Sulfolobus"]),
            N("Asgard archaea",
              "Seafloor archaea carrying genes once thought exclusive to "
              "eukaryotes. Current evidence places the eukaryotes as their "
              "closest relatives, which folds the old three-domain picture "
              "into two.", "Zaremba-Niedzwiedzka and others 2017",
              w=["Asgard (Archaea)", "Prometheoarchaeum"], kids=[
                N("Eukarya",
                  "Cells with a nucleus and mitochondria, born of an archaeal "
                  "host and a bacterial partner. Everything visible to the "
                  "naked eye lives on this one twig.",
                  "Burki and others 2020", w=["Eukaryote"], kids=[
                    N("Amorphea", "The supergroup holding animals, fungi and "
                      "the amoebae.", "Burki and others 2020",
                      w=["Amorphea"], kids=[
                        N("Animals", "Multicellular eaters, from sponges to "
                          "vertebrates: one branch of the opisthokonts. The "
                          "Animals diagram opens this tip.",
                          "Burki and others 2020", hl=True, w=["Animal"]),
                        N("Fungi", "The other great opisthokont branch: "
                          "molds, yeasts and mushrooms, closer to animals "
                          "than to plants.", "Burki and others 2020",
                          hl=True, w=["Fungus"]),
                        N("Amoebozoa", "Lobed amoebae and slime molds.",
                          "Burki and others 2020", w=["Amoebozoa"]),
                      ]),
                    N("Diaphoretickes", "The supergroup holding the plants "
                      "and most of the algae.", "Burki and others 2020",
                      w=["Diaphoretickes"], kids=[
                        N("Land plants and green algae",
                          "The green lineage of the Archaeplastida, whose "
                          "chloroplasts descend from one ancient captured "
                          "cyanobacterium.", "Burki and others 2020",
                          hl=True, w=["Viridiplantae", "Embryophyte"]),
                        N("Red algae", "The other big archaeplastid branch, "
                          "source of the chloroplasts many other algae later "
                          "borrowed.", "Burki and others 2020",
                          w=["Red algae"]),
                        N("SAR", "Stramenopiles, alveolates and Rhizaria: "
                          "kelps, diatoms, ciliates, dinoflagellates and the "
                          "malaria parasite, most of the ocean's unseen "
                          "diversity.", "Burki and others 2020",
                          w=["SAR supergroup", "Diatom"]),
                      ]),
                    N("Discoba", "Euglenas and trypanosomes, once filed "
                      "under the now-abandoned supergroup Excavata.",
                      "Burki and others 2020", w=["Discoba", "Euglena"]),
                  ]),
              ]),
          ]),
    ])

ANIMALS = N(
    "Animalia",
    "The animals: multicellular eaters descended from one flagellated "
    "ancestor, about 1.6 million described species and counting.",
    "Zhang 2013; Dunn and others 2014", count="~1.6 million species",
    w=["Animal"],
    kids=[
        N("Ctenophora", "The comb jellies, rowing with plates of fused "
          "cilia. Chromosome-scale genomes in 2023 placed them, not the "
          "sponges, as the sister of all other animals.",
          "Schultz and others 2023", count="~200 species",
          w=["Ctenophora"]),
        N("All other animals", "Everything after the comb jellies parted.",
          "Schultz and others 2023", kids=[
            N("Porifera", "The sponges: no nerves, no muscles, a body built "
              "for filtering water.", "Schultz and others 2023",
              count="~9,000 species", w=["Sponge"]),
            N("ParaHoxozoa", "The animals with developmental Hox-class "
              "genes.", "Schultz and others 2023", kids=[
                N("Placozoa", "Flat crawling sheets of cells, the simplest "
                  "animal body plan known.", "Schultz and others 2023",
                  count="a handful of species", w=["Placozoa", "Trichoplax"]),
                N("Cnidaria", "Jellyfish, corals and anemones, armed with "
                  "stinging cells.", "Dunn and others 2014",
                  count="~11,000 species", w=["Cnidaria", "Jellyfish"]),
                N("Bilateria", "Animals with a head end and a mirror-image "
                  "left and right: nearly everything else.",
                  "Dunn and others 2014", kids=[
                    N("Protostomia", "The larger bilaterian branch.",
                      "Dunn and others 2014", kids=[
                        N("Ecdysozoa", "The molting animals.",
                          "Dunn and others 2014", kids=[
                            N("Arthropoda", "Insects, spiders, crustaceans "
                              "and their kin: the majority of all described "
                              "animal species.", "Zhang 2013", hl=True,
                              count="~1.2 million species",
                              w=["Arthropod", "Insect"]),
                            N("Nematoda", "The roundworms, in soil, sea and "
                              "nearly every host.", "Zhang 2013",
                              count="~25,000 described species",
                              w=["Nematode"]),
                            N("Tardigrada", "The water bears, famous for "
                              "surviving vacuum, radiation and drying.",
                              "Zhang 2013", count="~1,300 species",
                              w=["Tardigrade"]),
                          ]),
                        N("Spiralia", "Animals with spiral cleavage in the "
                          "egg.", "Dunn and others 2014", kids=[
                            N("Mollusca", "Snails, clams, octopuses: the "
                              "second largest phylum.", "Zhang 2013",
                              count="~85,000 species",
                              w=["Mollusca", "Octopus"]),
                            N("Annelida", "The segmented worms, from "
                              "earthworms to reef fanworms.", "Zhang 2013",
                              count="~17,000 species", w=["Annelid"]),
                            N("Platyhelminthes", "The flatworms, free-living "
                              "and parasitic.", "Zhang 2013",
                              count="~29,000 species", w=["Flatworm"]),
                          ]),
                      ]),
                    N("Deuterostomia", "The branch whose embryonic mouth "
                      "forms second.", "Dunn and others 2014", kids=[
                        N("Echinodermata", "Sea stars, urchins and sea "
                          "cucumbers, five-fold symmetric as adults.",
                          "Zhang 2013", count="~7,000 species",
                          w=["Echinoderm", "Starfish"]),
                        N("Chordata", "Animals with a notochord.",
                          "Dunn and others 2014", hl=True, kids=[
                            N("Tunicata", "The sea squirts: swimming "
                              "chordate larvae that settle down and filter.",
                              "Zhang 2013", count="~3,000 species",
                              w=["Tunicate"]),
                            N("Cephalochordata", "The lancelets, the "
                              "chordate body plan at its plainest.",
                              "Zhang 2013", count="~30 species",
                              w=["Lancelet"]),
                            N("Vertebrata", "Animals with a backbone.",
                              "Zhang 2013", hl=True, kids=[
                                N("Fishes", "The finned vertebrates, a "
                                  "grade of several branches: jawless "
                                  "lampreys and hagfish, sharks and rays, "
                                  "and the vast ray-finned majority.",
                                  "Zhang 2013", count="~35,000 species",
                                  w=["Fish"]),
                                N("Amphibia", "Frogs, salamanders and "
                                  "caecilians, tied to water to breed.",
                                  "Zhang 2013", count="~8,000 species",
                                  w=["Amphibian", "Frog"]),
                                N("Sauropsida", "The reptile line: "
                                  "lizards, snakes, turtles, crocodilians, "
                                  "and the birds nested within it.",
                                  "Zhang 2013",
                                  count="~22,000 species, birds included",
                                  w=["Sauropsida", "Reptile"]),
                                N("Mammalia", "Hair and milk; the Mammals "
                                  "diagram opens this tip.",
                                  "Mammal Diversity Database 2025", hl=True,
                                  count="~6,800 species", w=["Mammal"]),
                              ]),
                          ]),
                      ]),
                  ]),
              ]),
          ]),
    ])

MAMMALS = N(
    "Mammalia",
    "Warm-blooded vertebrates with hair and milk: about 6,800 living "
    "species in 27 orders as counted by the Mammal Diversity Database.",
    "Mammal Diversity Database 2025", count="~6,800 species", w=["Mammal"],
    kids=[
        N("Monotremata", "The egg-laying mammals: the platypus and the "
          "echidnas, sole survivors of the deepest split.",
          "Burgin and others 2018", count="5 species",
          w=["Monotreme", "Platypus"]),
        N("Theria", "The live-bearing mammals, split between marsupials and "
          "placentals.", "Upham and others 2019", w=["Theria"], kids=[
            N("Marsupialia", "Mammals whose young finish developing in a "
              "pouch. Seven orders, most of them Australasian.",
              "Burgin and others 2018", count="~380 species",
              w=["Marsupial"], kids=[
                N("Didelphimorphia", "The opossums of the Americas.",
                  "Burgin and others 2018", count="~111 species",
                  w=["Opossum"]),
                N("Diprotodontia", "Kangaroos, wombats, possums and the "
                  "koala: the big Australian radiation.",
                  "Burgin and others 2018", count="~155 species",
                  w=["Diprotodontia", "Kangaroo"]),
                N("Dasyuromorphia and others",
                  "The carnivorous marsupials, bandicoots, the marsupial "
                  "mole and the monito del monte: five smaller orders.",
                  "Burgin and others 2018", count="~113 species",
                  w=["Dasyuromorphia", "Tasmanian devil"]),
              ]),
            N("Placentalia", "Mammals carried to term inside the mother: "
              "four great superorders that split as the continents did.",
              "Murphy and others 2001", count="~6,400 species",
              w=["Placentalia"], kids=[
                N("Afrotheria", "The African root stock: elephants, "
                  "manatees, hyraxes, aardvark, sengis and tenrecs.",
                  "Murphy and others 2001",
                  w=["Afrotheria", "African bush elephant"]),
                N("Xenarthra", "The South American originals: armadillos, "
                  "sloths and anteaters.", "Murphy and others 2001",
                  w=["Xenarthra", "Nine-banded armadillo"]),
                N("Euarchontoglires", "The rodents, rabbits, treeshrews, "
                  "colugos and primates, humankind included.",
                  "Murphy and others 2001", hl=True,
                  w=["Euarchontoglires"], kids=[
                    N("Rodentia", "Two in every five mammal species are "
                      "rodents.", "Mammal Diversity Database 2025",
                      count="~2,750 species", w=["Rodent"]),
                    N("Primates", "Lemurs to humans; the Primates diagram "
                      "opens this branch.", "Mammal Diversity Database 2025",
                      count="~520 species", hl=True, w=["Primate"]),
                    N("Lagomorpha and others", "Rabbits and hares, plus the "
                      "treeshrews and colugos nearest the primates.",
                      "Mammal Diversity Database 2025",
                      w=["Lagomorpha", "European rabbit"]),
                  ]),
                N("Laurasiatheria", "The northern radiation: shrews, bats, "
                  "carnivorans, pangolins, horses, and the even-toed "
                  "ungulates including the whales.",
                  "Murphy and others 2001", w=["Laurasiatheria"], kids=[
                    N("Chiroptera", "The bats, the only mammals with "
                      "powered flight.", "Mammal Diversity Database 2025",
                      count="~1,490 species", w=["Bat"]),
                    N("Carnivora", "Cats, dogs, bears, seals and their kin.",
                      "Mammal Diversity Database 2025", count="~320 species",
                      w=["Carnivora", "Lion"]),
                    N("Artiodactyla", "The even-toed ungulates, with the "
                      "whales and dolphins nested inside them.",
                      "Mammal Diversity Database 2025", count="~370 species",
                      w=["Even-toed ungulate", "Giraffe"]),
                    N("Eulipotyphla and others", "Shrews, moles and "
                      "hedgehogs, plus pangolins and the horses, rhinos and "
                      "tapirs.", "Mammal Diversity Database 2025",
                      w=["Eulipotyphla", "European hedgehog"]),
                  ]),
              ]),
          ]),
    ])

PRIMATES = N(
    "Euarchontoglires",
    "The mammal superorder holding rodents, rabbits and the primate "
    "lineage. The path to the primates runs through it.",
    "Murphy and others 2001", w=["Euarchontoglires"],
    kids=[
        N("Glires", "Rodents and lagomorphs: the sister group to everything "
          "below.", "Murphy and others 2001", w=["Glires", "Rodent"]),
        N("Primatomorpha", "Primates plus their closest living relatives.",
          "Janecka and others 2007", w=["Primatomorpha"], kids=[
            N("Dermoptera", "The colugos of Southeast Asia, gliding leaf "
              "eaters and the primates' nearest kin.",
              "Janecka and others 2007", count="2 species",
              w=["Colugo"]),
            N("Primates", "Grasping hands, forward eyes and big brains: "
              "about 520 living species.",
              "Mammal Diversity Database 2025", count="~520 species",
              w=["Primate"], kids=[
                N("Strepsirrhini", "The wet-nosed primates: the lemurs of "
                  "Madagascar and the lorises and galagos of Africa and "
                  "Asia.", "Perelman and others 2011",
                  w=["Strepsirrhini", "Ring-tailed lemur"]),
                N("Haplorhini", "The dry-nosed primates.",
                  "Perelman and others 2011", w=["Haplorhini"], kids=[
                    N("Tarsiers", "Tiny nocturnal leapers of island "
                      "Southeast Asia, the monkeys' deepest cousins.",
                      "Perelman and others 2011", w=["Tarsier"]),
                    N("Simiiformes", "The monkeys and apes.",
                      "Perelman and others 2011", w=["Simian"], kids=[
                        N("Platyrrhini", "The New World monkeys: capuchins, "
                          "howlers, marmosets and spider monkeys, many with "
                          "grasping tails.", "Perelman and others 2011",
                          w=["New World monkey", "Capuchin monkey"]),
                        N("Catarrhini", "The Old World monkeys and the "
                          "apes.", "Perelman and others 2011",
                          w=["Catarrhini"], kids=[
                            N("Cercopithecidae", "The Old World monkeys: "
                              "macaques, baboons, langurs and colobus "
                              "monkeys.", "Perelman and others 2011",
                              w=["Old World monkey", "Rhesus macaque"]),
                            N("Hominoidea", "The tailless apes.",
                              "Perelman and others 2011", w=["Ape"], kids=[
                                N("Hylobatidae", "The gibbons, small "
                                  "brachiating apes of Asian forests.",
                                  "Perelman and others 2011",
                                  w=["Gibbon"]),
                                N("Hominidae", "The great apes.",
                                  "Perelman and others 2011",
                                  w=["Hominidae"], kids=[
                                    N("Orangutans", "The Asian great apes, "
                                      "genus Pongo.",
                                      "Perelman and others 2011",
                                      w=["Orangutan"]),
                                    N("Gorillas", "The largest living "
                                      "primates.", "Perelman and others 2011",
                                      w=["Gorilla"]),
                                    N("Chimpanzees and bonobos",
                                      "Genus Pan, our closest living "
                                      "relatives; the human line parted "
                                      "from theirs roughly six to eight "
                                      "million years ago.",
                                      "Langergraber and others 2012",
                                      w=["Chimpanzee"]),
                                    N("Humans", "Homo sapiens, the one "
                                      "surviving species of its genus.",
                                      "Perelman and others 2011", hl=True,
                                      w=["Human"]),
                                  ]),
                              ]),
                          ]),
                      ]),
                  ]),
              ]),
          ]),
    ])


HOMININS = N(
    "Hominini",
    "The human tribe: every species closer to us than to the chimpanzees, "
    "from the split with the Pan line roughly seven million years ago. "
    "Polytomies mark relationships the fossils leave unresolved.",
    "Smithsonian Human Origins; Wood and Boyle 2016",
    w=["Hominini"],
    kids=[
        N("Sahelanthropus tchadensis",
          "A skull from Chad near the age of the chimpanzee split, with a "
          "forward-placed foramen magnum hinting at upright posture: the "
          "oldest candidate hominin, and a contested one.",
          "Brunet and others 2002", count="~7 to 6 Ma",
          w=["Sahelanthropus"]),
        N("Ardipithecus ramidus",
          "Ardi: a woodland biped that still gripped branches with an "
          "opposable big toe, described from a remarkable partial skeleton.",
          "White and others 2009", count="~4.4 Ma",
          w=["Ardipithecus"]),
        N("Australopithecus",
          "The small-brained committed bipeds of Africa, the grade from "
          "which both Paranthropus and Homo arise; which species is our "
          "actual ancestor stays unresolved.",
          "Smithsonian Human Origins", kids=[
            N("Australopithecus anamensis",
              "The earliest australopith, shin bones built for walking.",
              "Smithsonian Human Origins", count="~4.2 to 3.8 Ma",
              w=["Australopithecus anamensis"]),
            N("Australopithecus afarensis",
              "Lucy's species, walking upright at Laetoli while keeping a "
              "chimp-sized brain.",
              "Smithsonian Human Origins", count="~3.85 to 2.95 Ma",
              w=["Australopithecus afarensis", "Lucy (Australopithecus)"]),
            N("Australopithecus africanus",
              "The Taung Child's species, southern Africa's gracile "
              "australopith.",
              "Smithsonian Human Origins", count="~3.3 to 2.1 Ma",
              w=["Australopithecus africanus"]),
            N("Australopithecus sediba",
              "A late South African species mixing australopith and "
              "Homo-like traits, proposed and disputed as close to our "
              "genus's root.",
              "Berger and others 2010", count="~1.98 Ma",
              w=["Australopithecus sediba"]),
            N("Paranthropus",
              "The robust side branch: massive jaws and grinding teeth for "
              "hard and fibrous food. A long-lived experiment that left no "
              "descendants.",
              "Wood and Boyle 2016", w=["Paranthropus"], kids=[
                N("Paranthropus aethiopicus",
                  "The earliest robust form, known best from the Black "
                  "Skull.", "Smithsonian Human Origins",
                  count="~2.7 to 2.3 Ma", w=["Paranthropus aethiopicus"]),
                N("Paranthropus boisei",
                  "Nutcracker Man of East Africa, the most extreme chewing "
                  "apparatus of any hominin.", "Smithsonian Human Origins",
                  count="~2.3 to 1.2 Ma", w=["Paranthropus boisei"]),
                N("Paranthropus robustus",
                  "The South African robust species.",
                  "Smithsonian Human Origins", count="~1.8 to 1.2 Ma",
                  w=["Paranthropus robustus"]),
              ]),
            N("Homo",
              "The large-brained, tool-dependent genus. Its root among the "
              "australopiths and the rank of its earliest species remain "
              "argued.", "Wood and Boyle 2016", w=["Homo"], kids=[
                N("Homo habilis",
                  "Handy Man, named for the Oldowan tools found with it; "
                  "small-bodied, and by some accounts still an "
                  "australopith.", "Smithsonian Human Origins",
                  count="~2.4 to 1.4 Ma", w=["Homo habilis"]),
                N("Homo rudolfensis",
                  "A larger, flatter-faced early Homo known from Lake "
                  "Turkana; one skull, many arguments.",
                  "Smithsonian Human Origins", count="~1.9 to 1.8 Ma",
                  w=["Homo rudolfensis"]),
                N("Later Homo",
                  "The long-legged striders that left Africa.",
                  "Smithsonian Human Origins", kids=[
                    N("Homo erectus",
                      "The first world traveler: modern body proportions, "
                      "fire and handaxes, from Africa to Java over nearly "
                      "two million years.", "Smithsonian Human Origins",
                      count="~1.89 Ma to 110 ka", w=["Homo erectus"]),
                    N("Homo floresiensis",
                      "The hobbit of Flores, a meter tall with a tiny "
                      "brain, likely an isolated dwarfed offshoot of early "
                      "Homo.", "Brown and others 2004",
                      count="~100 to 50 ka", w=["Homo floresiensis"]),
                    N("Homo luzonensis",
                      "A second island species, from Callao Cave in the "
                      "Philippines, mixing modern and australopith-like "
                      "traits.", "Detroit and others 2019",
                      count="~67 to 50 ka", w=["Homo luzonensis"]),
                    N("Homo naledi",
                      "A small-brained species from the Rising Star cave "
                      "system, surprisingly young for its anatomy.",
                      "Berger and others 2015; Dirks and others 2017",
                      count="~335 to 236 ka", w=["Homo naledi"]),
                    N("The heidelbergensis grade",
                      "The big-brained middle Pleistocene humans from whom "
                      "the last three species descend.",
                      "Smithsonian Human Origins", kids=[
                        N("Homo antecessor",
                          "Pioneer of Atapuerca, Spain, with a "
                          "surprisingly modern face; close to the last "
                          "common ancestor of the final three.",
                          "Smithsonian Human Origins",
                          count="~1.2 to 0.8 Ma", w=["Homo antecessor"]),
                        N("Homo heidelbergensis",
                          "The likely ancestor grade of Neanderthals, "
                          "Denisovans and us: hearths, wooden spears and "
                          "big-game hunting.", "Smithsonian Human Origins",
                          count="~700 to 200 ka",
                          w=["Homo heidelbergensis"]),
                        N("Us and our closest kin",
                          "Three species so close they interbred; a tree "
                          "cannot draw those crossings, but living human "
                          "genomes record them.",
                          "Green and others 2010; Reich and others 2010",
                          kids=[
                            N("Neanderthals and Denisovans",
                              "The Eurasian sister pair.",
                              "Reich and others 2010", kids=[
                                N("Homo neanderthalensis",
                                  "Cold-adapted Eurasians with brains as "
                                  "large as ours, burying their dead; one "
                                  "to two percent of most living genomes "
                                  "outside Africa is theirs.",
                                  "Green and others 2010",
                                  count="~400 to 40 ka", w=["Neanderthal"]),
                                N("Denisovans",
                                  "Known mostly from DNA in a Siberian "
                                  "cave and a Tibetan jaw; their genes "
                                  "help Tibetans live at altitude.",
                                  "Reich and others 2010",
                                  count="~200 to 30 ka", w=["Denisovan"]),
                              ]),
                            N("Homo sapiens",
                              "The one survivor, in Africa by about "
                              "300,000 years ago at Jebel Irhoud and "
                              "everywhere since.",
                              "Hublin and others 2017", hl=True,
                              count="~300 ka to now",
                              w=["Homo sapiens", "Human"]),
                          ]),
                      ]),
                  ]),
              ]),
          ]),
    ])


IMG_NOTE = (" Each living tip carries the photograph from its group's "
            "Wikipedia article, fetched at view time.")
HOM_IMG_NOTE = (" Each species carries the photograph from its Wikipedia "
                "article, fetched at view time.")

PAGES = [
    ("tree-of-life.html", "Tree of Life", TREE_OF_LIFE,
     "The tree runs from the last universal common ancestor at the left to "
     "living groups at the right; branch lengths carry no time information. "
     "The eukaryotes are drawn where current evidence places them, beside "
     "the Asgard archaea inside the archaeal branch, which turns Woese's "
     "three domains into two. A node under the cursor fills the card; "
     "a click pins it, and a second click lets go."
     + IMG_NOTE,
     [("Woese, C. R., Kandler, O., & Wheelis, M. L. (1990). Towards a "
       "natural system of organisms: Proposal for the domains Archaea, "
       "Bacteria, and Eucarya. <i>Proceedings of the National Academy of "
       "Sciences, 87</i>(12), 4576-4579.",
       "https://doi.org/10.1073/pnas.87.12.4576"),
      ("Hug, L. A., Baker, B. J., Anantharaman, K., Brown, C. T., Probst, "
       "A. J., Castelle, C. J., Butterfield, C. N., Hernsdorf, A. W., "
       "Amano, Y., Ise, K., Suzuki, Y., Dudek, N., Relman, D. A., "
       "Finstad, K. M., Amundson, R., Thomas, B. C., & Banfield, J. F. "
       "(2016). A new view of the tree of life. <i>Nature Microbiology, "
       "1</i>, 16048.", "https://doi.org/10.1038/nmicrobiol.2016.48"),
      ("Zaremba-Niedzwiedzka, K., Caceres, E. F., Saw, J. H., Backstrom, "
       "D., Juzokaite, L., Vancaester, E., Seitz, K. W., Anantharaman, K., "
       "Starnawski, P., Kjeldsen, K. U., Stott, M. B., Nunoura, T., "
       "Banfield, J. F., Schramm, A., Baker, B. J., Spang, A., & Ettema, "
       "T. J. G. (2017). Asgard archaea illuminate the origin of eukaryotic "
       "cellular complexity. <i>Nature, 541</i>, 353-358.",
       "https://doi.org/10.1038/nature21031"),
      ("Burki, F., Roger, A. J., Brown, M. W., & Simpson, A. G. B. (2020). "
       "The new tree of eukaryotes. <i>Trends in Ecology &amp; Evolution, "
       "35</i>(1), 43-55.", "https://doi.org/10.1016/j.tree.2019.08.008"),
      ("Images: the linked group's Wikipedia article thumbnail, fetched at "
       "view time; each is credited on its article page.",
       "https://en.wikipedia.org/")]),
    ("animals.html", "Animals", ANIMALS,
     "The main divisions of the animals, from the one ancestor at the left "
     "to living phyla and, inside the chordates, the vertebrate classes; "
     "branch lengths carry no time information, and counts are described "
     "species from Zhang's 2013 census. The comb jellies branch first, a "
     "placement settled by chromosome-scale genomes in 2023, and the fishes "
     "are drawn as one grade of several branches. A node under the cursor "
     "fills the card; a click pins it, and a second click lets go." + IMG_NOTE,
     [("Schultz, D. T., Haddock, S. H. D., Bredeson, J. V., Green, R. E., "
       "Simakov, O., & Rokhsar, D. S. (2023). Ancient gene linkages support "
       "ctenophores as sister to other animals. <i>Nature, 618</i>, "
       "110-117.", "https://doi.org/10.1038/s41586-023-05936-6"),
      ("Dunn, C. W., Giribet, G., Edgecombe, G. D., & Hejnol, A. (2014). "
       "Animal phylogeny and its evolutionary implications. <i>Annual "
       "Review of Ecology, Evolution, and Systematics, 45</i>, 371-395.",
       "https://doi.org/10.1146/annurev-ecolsys-120213-091627"),
      ("Zhang, Z.-Q. (2013). Animal biodiversity: An update of "
       "classification and diversity in 2013. <i>Zootaxa, 3703</i>(1), "
       "5-11.", "https://doi.org/10.11646/zootaxa.3703.1.3"),
      ("Laumer, C. E., Fernandez, R., Lemer, S., Combosch, D., Kocot, "
       "K. M., Riesgo, A., Andrade, S. C. S., Sterrer, W., Sorensen, M. V., "
       "& Giribet, G. (2019). Revisiting metazoan phylogeny with genomic "
       "sampling of all phyla. <i>Proceedings of the Royal Society B, "
       "286</i>(1906), 20190831.", "https://doi.org/10.1098/rspb.2019.0831"),
      ("Images: the linked group's Wikipedia article thumbnail, fetched at "
       "view time; each is credited on its article page.",
       "https://en.wikipedia.org/")]),
    ("mammals.html", "Mammals", MAMMALS,
     "The main divisions of the living mammals, from the deepest split at "
     "the left to orders at the right; branch lengths carry no time "
     "information, and species counts are the Mammal Diversity Database's, "
     "rounded. The root inside the placentals is drawn with Afrotheria "
     "branching first, one of two arrangements the genomes still allow. A "
     "node under the cursor fills the card; a click pins it, and a second "
     "click lets go." + IMG_NOTE,
     [("Burgin, C. J., Colella, J. P., Kahn, P. L., & Upham, N. S. (2018). "
       "How many species of mammals are there? <i>Journal of Mammalogy, "
       "99</i>(1), 1-14.", "https://doi.org/10.1093/jmammal/gyx147"),
      ("Murphy, W. J., Eizirik, E., O'Brien, S. J., Madsen, O., Scally, M., "
       "Douady, C. J., Teeling, E., Ryder, O. A., Stanhope, M. J., de Jong, "
       "W. W., & Springer, M. S. (2001). Resolution of the early placental "
       "mammal radiation using Bayesian phylogenetics. <i>Science, "
       "294</i>(5550), 2348-2351.", "https://doi.org/10.1126/science.1067179"),
      ("Upham, N. S., Esselstyn, J. A., & Jetz, W. (2019). Inferring the "
       "mammal tree: Species-level sets of phylogenies for questions in "
       "ecology, evolution, and conservation. <i>PLOS Biology, 17</i>(12), "
       "e3000494.", "https://doi.org/10.1371/journal.pbio.3000494"),
      ("Mammal Diversity Database, American Society of Mammalogists. "
       "(2025).", "https://www.mammaldiversity.org/"),
      ("Foley, N. M., et al. (2023). A genomic timescale for placental "
       "mammal evolution. <i>Science, 380</i>(6643), eabl8189.",
       "https://doi.org/10.1126/science.abl8189"),
      ("Images: the linked group's Wikipedia article thumbnail, fetched at "
       "view time; each is credited on its article page.",
       "https://en.wikipedia.org/")]),
    ("primates.html", "Primates", PRIMATES,
     "The branches of the tree of life that lead to and through the "
     "primates, from the mammal superorder at the left to the living "
     "great apes at the right; branch lengths carry no time information. "
     "The human line sits beside the chimpanzees and bonobos, from whom it "
     "parted roughly six to eight million years ago. A node under the "
     "cursor fills the card; a click pins it, and a second click lets go."
     + IMG_NOTE,
     [("Perelman, P., Johnson, W. E., Roos, C., Seuanez, H. N., Horvath, "
       "J. E., Moreira, M. A. M., Kessing, B., Pontius, J., Roelke, M., "
       "Rumpler, Y., Schneider, M. P. C., Silva, A., O'Brien, S. J., & "
       "Pecon-Slattery, J. (2011). A molecular phylogeny of living "
       "primates. <i>PLOS Genetics, 7</i>(3), e1001342.",
       "https://doi.org/10.1371/journal.pgen.1001342"),
      ("Janecka, J. E., Miller, W., Pringle, T. H., Wiens, F., Zitzmann, "
       "A., Helgen, K. M., Springer, M. S., & Murphy, W. J. (2007). "
       "Molecular and genomic data identify the closest living relative "
       "of primates. <i>Science, 318</i>(5851), 792-794.",
       "https://doi.org/10.1126/science.1147555"),
      ("Langergraber, K. E., et al. (2012). Generation times in wild "
       "chimpanzees and gorillas suggest earlier divergence times in "
       "great ape and human evolution. <i>Proceedings of the National "
       "Academy of Sciences, 109</i>(39), 15716-15721.",
       "https://doi.org/10.1073/pnas.1211740109"),
      ("Mammal Diversity Database, American Society of Mammalogists. "
       "(2025).", "https://www.mammaldiversity.org/"),
      ("Images: the linked group's Wikipedia article thumbnail, fetched at "
       "view time; each is credited on its article page.",
       "https://en.wikipedia.org/")]),
    ("hominins.html", "Hominins", HOMININS,
     "The human tribe from the chimpanzee split to the present: the "
     "australopiths, the robust Paranthropus side branch, and every named "
     "branch of Homo down to the three that overlapped last, with fossil "
     "date ranges beside each species (Ma, millions of years ago; ka, "
     "thousands). Polytomies mark relationships the fossils leave "
     "unresolved. A node "
     "under the cursor fills the card; a click pins it, and a second click "
     "lets go." + HOM_IMG_NOTE,
     [("Smithsonian National Museum of Natural History. (n.d.). Human "
       "origins: Species. Human Origins Program.",
       "https://humanorigins.si.edu/evidence/human-fossils/species"),
      ("Wood, B., & Boyle, E. K. (2016). Hominin taxic diversity: Fact or "
       "fantasy? <i>American Journal of Physical Anthropology, 159</i>"
       "(S61), 37-78.", "https://doi.org/10.1002/ajpa.22902"),
      ("Brunet, M., et al. (2002). A new hominid from the Upper Miocene of "
       "Chad, Central Africa. <i>Nature, 418</i>, 145-151.",
       "https://doi.org/10.1038/nature00879"),
      ("White, T. D., Asfaw, B., Beyene, Y., Haile-Selassie, Y., Lovejoy, "
       "C. O., Suwa, G., & WoldeGabriel, G. (2009). Ardipithecus ramidus "
       "and the paleobiology of early hominids. <i>Science, 326</i>(5949), "
       "64-86.", "https://doi.org/10.1126/science.1175802"),
      ("Berger, L. R., de Ruiter, D. J., Churchill, S. E., Schmid, P., "
       "Carlson, K. J., Dirks, P. H. G. M., & Kibii, J. M. (2010). "
       "Australopithecus sediba: A new species of Homo-like australopith "
       "from South Africa. <i>Science, 328</i>(5975), 195-204.",
       "https://doi.org/10.1126/science.1184944"),
      ("Brown, P., Sutikna, T., Morwood, M. J., Soejono, R. P., Jatmiko, "
       "Saptomo, E. W., & Due, R. A. (2004). A new small-bodied hominin "
       "from the Late Pleistocene of Flores, Indonesia. <i>Nature, "
       "431</i>, 1055-1061.", "https://doi.org/10.1038/nature02999"),
      ("Detroit, F., Mijares, A. S., Corny, J., Daver, G., Zanolli, C., "
       "Dizon, E., Robles, E., Grun, R., & Piper, P. J. (2019). A new "
       "species of Homo from the Late Pleistocene of the Philippines. "
       "<i>Nature, 568</i>, 181-186.",
       "https://doi.org/10.1038/s41586-019-1067-9"),
      ("Berger, L. R., et al. (2015). Homo naledi, a new species of the "
       "genus Homo from the Dinaledi Chamber, South Africa. <i>eLife, "
       "4</i>, e09560.", "https://doi.org/10.7554/eLife.09560"),
      ("Dirks, P. H. G. M., et al. (2017). The age of Homo naledi and "
       "associated sediments in the Rising Star Cave, South Africa. "
       "<i>eLife, 6</i>, e24231.", "https://doi.org/10.7554/eLife.24231"),
      ("Green, R. E., et al. (2010). A draft sequence of the Neandertal "
       "genome. <i>Science, 328</i>(5979), 710-722.",
       "https://doi.org/10.1126/science.1188021"),
      ("Reich, D., et al. (2010). Genetic history of an archaic hominin "
       "group from Denisova Cave in Siberia. <i>Nature, 468</i>, "
       "1053-1060.", "https://doi.org/10.1038/nature09710"),
      ("Hublin, J.-J., et al. (2017). New fossils from Jebel Irhoud, "
       "Morocco and the pan-African origin of Homo sapiens. <i>Nature, "
       "546</i>, 289-292.", "https://doi.org/10.1038/nature22336"),
      ("Images: the linked species' Wikipedia article thumbnail, fetched "
       "at view time; each is credited on its article page.",
       "https://en.wikipedia.org/")]),
]


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ · Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; --hl:#31d67a; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
.wrap { max-width:1320px; margin:0 auto; padding:32px 20px 60px; }
header.site { border-top:4px solid var(--accent); padding-top:22px; margin-bottom:26px;
  display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }
.brand { font-weight:700; font-size:20px; letter-spacing:.1em; text-decoration:none; color:var(--text); }
.brand:hover { color:var(--accent); }
nav.site a { color:var(--muted); text-decoration:none; font-size:14px; margin-right:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 6px; font-size:26px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; }
#diagram svg { width:100%; height:auto; display:block; user-select:none; }
.side { flex:0 0 300px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:16px; }
#cardImg { width:100%; height:170px; object-fit:cover; object-position:top; border-radius:8px;
  border:1px solid var(--line); margin-bottom:10px; display:none; background:#0d0d0d; }
#nameTxt { font-weight:700; font-size:17px; }
#cntTxt { color:var(--hl); font-size:13px; margin-top:2px; }
#bodyTxt { color:var(--muted); font-size:13.5px; line-height:1.55; margin-top:8px; }
#srcTxt { color:var(--muted); font-size:12px; margin-top:10px;
  border-top:1px solid var(--line); padding-top:8px; }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.refs { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.refs p { margin:0 0 8px; overflow-wrap:anywhere; }
.refs a { color:var(--accent); }
h2.refh { font-size:15px; margin:26px 0 8px; }
@media (max-width:900px){ .stage{flex-direction:column;} .side{position:static; width:100%;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library &middot; Life</a>__XNAV__</nav>
</header>
<h1>__TITLE__</h1>
<div class="stage">
  <div id="diagram"></div>
  <div class="side"><div class="card">
    <img id="cardImg" alt="">
    <div id="nameTxt">A group under the cursor lands here</div>
    <div id="cntTxt"></div>
    <div id="bodyTxt"></div>
    <div id="srcTxt"></div>
  </div></div>
</div>
<p class="note">__NOTE__</p>
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</div>
<script>
const ROOT=__DATA__, UP=__UP__;
const el=document.getElementById('diagram');
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');

// layout: tips evenly spaced down the right, parents at the mean of their
// children, x by depth
const tips=[]; let maxd=0;
(function walk(n,d){ n.depth=d; maxd=Math.max(maxd,d);
  if(n.k) n.k.forEach(c=>walk(c,d+1)); else tips.push(n); })(ROOT,0);
const RS=42, PADT=UP?62:28, PADB=16, PADL=16, PADR=300, TH=34;
const W=1010, H=PADT+PADB+RS*tips.length;
tips.forEach((t,i)=>{ t.y=PADT+RS*(i+0.5); });
(function place(n){ if(n.k){ n.k.forEach(place);
  n.y=n.k.reduce((a,c)=>a+c.y,0)/n.k.length; } })(ROOT);
const X=d=>PADL+ (W-PADL-PADR) * d/maxd;

const IMG={};      // node name -> thumbnail url, filled at view time
let idc=0; const byId={};
function draw(n){
  if(!n.id){ n.id='n'+(idc++); byId[n.id]=n; }
  const x=X(n.depth), col=n.hl?'var(--hl)':'#c9d1d9';
  let s='';
  if(n.k){
    const x1=X(n.depth+1);
    for(const c of n.k)
      s+=`<path d="M${x},${n.y} V${c.y} H${x1}" fill="none"
        stroke="#3d444d" stroke-width="1.6"/>`;
    for(const c of n.k) s+=draw(c);
  }
  let lab;
  if(n.k){
    lab = n.depth===0
      ? `<text x="${x+7}" y="${n.y-7}" font-size="12.5"
          fill="${n.hl?'var(--hl)':'#9a9a9a'}">${esc(n.n)}</text>`
      : `<text x="${x-8}" y="${n.y+4}" text-anchor="end" font-size="12.5"
          fill="${n.hl?'var(--hl)':'#9a9a9a'}" stroke="#121212"
          stroke-width="3" paint-order="stroke">${esc(n.n)}</text>`;
  } else {
    const u=IMG[n.n], tx=u?x+16+TH:x+9;
    lab=(u?`<image href="${u}" x="${x+10}" y="${n.y-TH/2}" width="${TH}"
        height="${TH}" preserveAspectRatio="xMidYMin slice"/>
      <rect x="${x+10}" y="${n.y-TH/2}" width="${TH}" height="${TH}"
        fill="none" stroke="#2b2b2b" stroke-width="1"/>`:'')
      +`<text x="${tx}" y="${n.y+4.5}" font-size="13.5" font-weight="${n.hl?700:400}"
      fill="${col}">${esc(n.n)}${n.c?` <tspan fill="#6b7280" font-size="11.5" font-weight="400">${esc(n.c)}</tspan>`:''}</text>`;
  }
  s+=`<g data-id="${n.id}" style="cursor:pointer">
    ${n.id===pinned?`<circle cx="${x}" cy="${n.y}" r="9.5" fill="none"
      stroke="${n.hl?'var(--hl)':'var(--accent)'}" stroke-width="1.6"
      opacity="0.9"/>`:''}
    <circle cx="${x}" cy="${n.y}" r="${n.k?4:4.5}"
      fill="${n.hl?'var(--hl)':(n.k?'#121212':'#58a6ff')}"
      stroke="${n.hl?'var(--hl)':'#58a6ff'}" stroke-width="1.6"/>
    <rect x="${x-10}" y="${n.y-Math.max(12,TH/2)}" width="${n.k?Math.min(200,n.n.length*7+24):290}" height="${n.k?24:TH}" fill="transparent"/>
    ${lab}</g>`;
  return s;
}
function upNode(){
  if(!UP) return '';
  const x=X(0), y=20;
  return `<path d="M${x},${ROOT.y} L${x},${y+8}" fill="none" stroke="#3d444d"
      stroke-width="1.6" stroke-dasharray="4 4"/>
    <g data-href="${UP.href}" style="cursor:pointer">
      <rect x="${x-10}" y="${y-11}" width="${UP.label.length*8+40}" height="24"
        fill="transparent"/>
      <circle cx="${x}" cy="${y}" r="4.5" fill="var(--accent)"/>
      <text x="${x+10}" y="${y+4.5}" font-size="13" fill="var(--accent)"
        >\u2191 ${UP.label}</text></g>`;
}
function render(){
  el.innerHTML=`<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg"
    id="treesvg">`+draw(ROOT)+upNode()+'</svg>';
}
let current='n0', pinned=null;
function show(id){
  const n=byId[id]; if(!n) return;
  current=id;
  document.getElementById('nameTxt').textContent=n.n;
  document.getElementById('cntTxt').textContent=n.c||'';
  document.getElementById('bodyTxt').textContent=n.b;
  document.getElementById('srcTxt').textContent=n.s;
  const img=document.getElementById('cardImg');
  if(IMG[n.n]){ img.src=IMG[n.n]; img.style.display='block'; }
  else img.style.display='none';
}
el.addEventListener('pointerover',e=>{
  if(pinned) return;
  const g=e.target.closest('[data-id]');
  if(g) show(g.getAttribute('data-id'));
});
el.addEventListener('click',e=>{
  const up=e.target.closest('[data-href]');
  if(up){ location.href=up.getAttribute('data-href'); return; }
  const g=e.target.closest('[data-id]');
  if(g){
    const id=g.getAttribute('data-id');
    pinned = pinned===id ? null : id;
    show(id);
  } else pinned=null;
  render();
});

// photos: each node's Wikipedia article summary thumbnail, first
// candidate with a thumbnail wins; no thumbnail means no photo. The
// thumbnail URL is used exactly as served: rewriting its size breaks it.
async function thumb(titles){
  for(const t of titles){
    try{
      const r=await fetch('https://en.wikipedia.org/api/rest_v1/page/summary/'
        +encodeURIComponent(t.replace(/ /g,'_')));
      if(!r.ok) continue;
      const j=await r.json();
      if(j.thumbnail) return j.thumbnail.source;
    }catch(e){}
  }
  return null;
}
async function loadImages(){
  const all=[];
  (function walk(n){ if(n.w) all.push(n); if(n.k) n.k.forEach(walk); })(ROOT);
  await Promise.all(all.map(async n=>{
    const u=await thumb(n.w);
    if(u) IMG[n.n]=u;
  }));
  render();
  show(current);
}

render();
show('n0');
loadImages();
window.__tree=()=>({tips:tips.length, depth:maxd,
  nodes:Object.keys(byId).length, h:H, imgs:Object.keys(IMG).length,
  tipImgs:tips.filter(t=>IMG[t.n]).length, pinned, current});
</script>
</body>
</html>
"""


def refs_html(refs):
    out = []
    for text, url in refs:
        out.append(f'<p>{text}\n<a href="{url}">{url}</a></p>')
    return "\n".join(out)


# the tree each page's root grows out of, drawn as a clickable node
UPLINK = {
    "tree-of-life.html": None,
    "animals.html": {"href": "tree-of-life.html", "label": "Tree of Life"},
    "mammals.html": {"href": "animals.html", "label": "Animals"},
    "primates.html": {"href": "mammals.html", "label": "Mammals"},
    "hominins.html": {"href": "primates.html", "label": "Primates"},
}

XNAV = {
    "tree-of-life.html": ' <a href="animals.html">Animals</a>',
    "animals.html": (' <a href="tree-of-life.html">Tree of Life</a>'
                     ' <a href="mammals.html">Mammals</a>'),
    "mammals.html": (' <a href="animals.html">Animals</a>'
                     ' <a href="primates.html">Primates</a>'),
    "primates.html": (' <a href="mammals.html">Mammals</a>'
                      ' <a href="hominins.html">Hominins</a>'),
    "hominins.html": ' <a href="primates.html">Primates</a>',
}

for fname, title, data, note, refs in PAGES:
    html = (HTML.replace("__TITLE__", title)
            .replace("__XNAV__", XNAV[fname])
            .replace("__NOTE__", note)
            .replace("__REFS__", refs_html(refs))
            .replace("__DATA__", json.dumps(data, separators=(",", ":")))
            .replace("__UP__", json.dumps(UPLINK[fname])))
    (ROOT / fname).write_text(html, encoding="utf-8")
    print(f"wrote {ROOT / fname} ({len(html):,} bytes)")
