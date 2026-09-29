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
import apa
from pathlib import Path

ROOT = Path(__file__).parent.parent

# A node: name, blurb, source; optional count (display string), hl
# (highlight as a familiar group), kids, and w: Wikipedia article titles
# to try, in order, for a representative photo (the first with a summary
# thumbnail wins; no thumbnail anywhere means no photo, never a stand-in).
# href names the diagram a click on that tip opens, p gives a plain name
# to print beside a Latin one, and t is a fossil span in Ma for the time
# layout (hominins). The branching points of the mammals and primates get
# their divergence ages from DIVERGE below.
def N(name, blurb, source, count=None, hl=False, kids=None, w=None,
      href=None, p=None, t=None):
    d = {"n": name, "b": blurb, "s": source}
    if count: d["c"] = count
    if hl: d["hl"] = True
    if kids: d["k"] = kids
    if w: d["w"] = w
    if href: d["href"] = href      # the diagram a click on this tip opens
    if p: d["p"] = p               # a plain name beside a Latin one
    if t: d["t"] = t               # fossil span, oldest to youngest, in Ma
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
                      w=["Amorphea"], p="animals, fungi, amoebae", kids=[
                        N("Animals", "Multicellular eaters, from sponges to "
                          "vertebrates: one branch of the opisthokonts. The "
                          "Animals diagram opens this tip.",
                          "Burki and others 2020", hl=True, w=["Animal"],
                          href="animals.html"),
                        N("Fungi", "The other great opisthokont branch: "
                          "molds, yeasts and mushrooms, closer to animals "
                          "than to plants.", "Burki and others 2020",
                          hl=True, w=["Fungus"]),
                        N("Amoebozoa", "Lobed amoebae and slime molds.",
                          "Burki and others 2020", w=["Amoebozoa"]),
                      ]),
                    N("Diaphoretickes", "The supergroup holding the plants "
                      "and most of the algae.", "Burki and others 2020",
                      w=["Diaphoretickes"], p="plants and most algae", kids=[
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
                                  count="~6,800 species", w=["Mammal"],
                                  href="mammals.html"),
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
                  w=["Afrotheria", "African bush elephant"],
                  p="elephants, manatees, tenrecs"),
                N("Xenarthra", "The South American originals: armadillos, "
                  "sloths and anteaters.", "Murphy and others 2001",
                  w=["Xenarthra", "Nine-banded armadillo"],
                  p="armadillos, sloths, anteaters"),
                N("Euarchontoglires", "The rodents, rabbits, treeshrews, "
                  "colugos and primates, humankind included.",
                  "Murphy and others 2001", hl=True,
                  w=["Euarchontoglires"], kids=[
                    N("Rodentia", "Two in every five mammal species are "
                      "rodents.", "Mammal Diversity Database 2025",
                      count="~2,750 species", w=["Rodent"]),
                    N("Primates", "Lemurs to humans; the Primates diagram "
                      "opens this branch.", "Mammal Diversity Database 2025",
                      count="~520 species", hl=True, w=["Primate"],
                      href="primates.html"),
                    N("Lagomorpha and others", "Rabbits and hares, plus the "
                      "treeshrews and colugos nearest the primates.",
                      "Mammal Diversity Database 2025",
                      w=["Lagomorpha", "European rabbit"],
                      p="rabbits, treeshrews, colugos"),
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
                      w=["Eulipotyphla", "European hedgehog"],
                      p="shrews, pangolins, horses"),
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
          "below.", "Murphy and others 2001", w=["Glires", "Rodent"],
          p="rodents and rabbits"),
        N("Primatomorpha", "Primates plus their closest living relatives.",
          "Janecka and others 2007", w=["Primatomorpha"],
          p="primates and colugos", kids=[
            N("Dermoptera", "The two colugos of Southeast Asia, gliding leaf "
              "eaters and the primates' nearest kin.",
              "Janecka and others 2007", p="colugos",
              w=["Colugo"]),
            N("Primates", "Grasping hands, forward eyes and big brains: "
              "about 520 living species.",
              "Mammal Diversity Database 2025", count="~520 species",
              w=["Primate"], kids=[
                N("Strepsirrhini", "The wet-nosed primates: the lemurs of "
                  "Madagascar and the lorises and galagos of Africa and "
                  "Asia.", "Perelman and others 2011",
                  w=["Strepsirrhini", "Ring-tailed lemur"],
                  p="lemurs and lorises"),
                N("Haplorhini", "The dry-nosed primates.",
                  "Perelman and others 2011", w=["Haplorhini"],
                  p="dry-nosed primates", kids=[
                    N("Tarsiers", "Tiny nocturnal leapers of island "
                      "Southeast Asia, the monkeys' deepest cousins.",
                      "Perelman and others 2011", w=["Tarsier"]),
                    N("Simiiformes", "The monkeys and apes.",
                      "Perelman and others 2011", w=["Simian"],
                      p="monkeys and apes", kids=[
                        N("Platyrrhini", "The New World monkeys: capuchins, "
                          "howlers, marmosets and spider monkeys, many with "
                          "grasping tails.", "Perelman and others 2011",
                          w=["New World monkey", "Capuchin monkey"],
                          p="New World monkeys"),
                        N("Catarrhini", "The Old World monkeys and the "
                          "apes.", "Perelman and others 2011",
                          w=["Catarrhini"], p="Old World monkeys and apes",
                          kids=[
                            N("Cercopithecidae", "The Old World monkeys: "
                              "macaques, baboons, langurs and colobus "
                              "monkeys.", "Perelman and others 2011",
                              w=["Old World monkey", "Rhesus macaque"],
                              p="Old World monkeys"),
                            N("Hominoidea", "The tailless apes.",
                              "Perelman and others 2011", w=["Ape"],
                              p="apes", kids=[
                                N("Hylobatidae", "The gibbons, small "
                                  "brachiating apes of Asian forests.",
                                  "Perelman and others 2011",
                                  w=["Gibbon"], p="gibbons"),
                                N("Hominidae", "The great apes.",
                                  "Perelman and others 2011",
                                  w=["Hominidae"], p="great apes", kids=[
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
                                      "surviving species of its genus; the "
                                      "Hominins diagram opens its tribe.",
                                      "Perelman and others 2011", hl=True,
                                      w=["Human"], href="hominins.html"),
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
    "Where several branches leave one point, the fossils leave their "
    "order unresolved.",
    "Smithsonian Human Origins; Wood and Boyle 2016",
    w=["Hominini"],
    kids=[
        N("Sahelanthropus tchadensis",
          "A skull from Chad near the age of the chimpanzee split, with a "
          "forward-placed foramen magnum hinting at upright posture: the "
          "oldest candidate hominin, and a contested one.",
          "Brunet and others 2002", count="~7 to 6 Ma",
          w=["Sahelanthropus"], t=(7, 6)),
        N("Ardipithecus ramidus",
          "Ardi: a woodland biped that still gripped branches with an "
          "opposable big toe, described from a remarkable partial skeleton.",
          "White and others 2009", count="~4.4 Ma",
          w=["Ardipithecus"], t=(4.4, 4.4)),
        N("Australopithecus",
          "The small-brained committed bipeds of Africa, the grade from "
          "which both Paranthropus and Homo arise; which species is our "
          "actual ancestor stays unresolved.",
          "Smithsonian Human Origins", kids=[
            N("Australopithecus anamensis",
              "The earliest australopith, shin bones built for walking.",
              "Smithsonian Human Origins", count="~4.2 to 3.8 Ma",
              w=["Australopithecus anamensis"], t=(4.2, 3.8)),
            N("Australopithecus afarensis",
              "Lucy's species, walking upright at Laetoli while keeping a "
              "chimp-sized brain.",
              "Smithsonian Human Origins", count="~3.85 to 2.95 Ma",
              w=["Australopithecus afarensis", "Lucy (Australopithecus)"], t=(3.85, 2.95)),
            N("Australopithecus africanus",
              "The Taung Child's species, southern Africa's gracile "
              "australopith.",
              "Smithsonian Human Origins", count="~3.3 to 2.1 Ma",
              w=["Australopithecus africanus"], t=(3.3, 2.1)),
            N("Australopithecus sediba",
              "A late South African species mixing australopith and "
              "Homo-like traits, proposed and disputed as close to our "
              "genus's root.",
              "Berger and others 2010", count="~1.98 Ma",
              w=["Australopithecus sediba"], t=(1.98, 1.98)),
            N("Paranthropus",
              "The robust side branch: massive jaws and grinding teeth for "
              "hard and fibrous food. A long-lived experiment that left no "
              "descendants.",
              "Wood and Boyle 2016", w=["Paranthropus"], kids=[
                N("Paranthropus aethiopicus",
                  "The earliest robust form, known best from the Black "
                  "Skull.", "Smithsonian Human Origins",
                  count="~2.7 to 2.3 Ma", w=["Paranthropus aethiopicus"], t=(2.7, 2.3)),
                N("Paranthropus boisei",
                  "Nutcracker Man of East Africa, the most extreme chewing "
                  "apparatus of any hominin.", "Smithsonian Human Origins",
                  count="~2.3 to 1.2 Ma", w=["Paranthropus boisei"], t=(2.3, 1.2)),
                N("Paranthropus robustus",
                  "The South African robust species.",
                  "Smithsonian Human Origins", count="~1.8 to 1.2 Ma",
                  w=["Paranthropus robustus"], t=(1.8, 1.2)),
              ]),
            N("Homo",
              "The large-brained, tool-dependent genus. Its root among the "
              "australopiths and the rank of its earliest species remain "
              "argued.", "Wood and Boyle 2016", w=["Homo"], kids=[
                N("Homo habilis",
                  "Handy Man, named for the Oldowan tools found with it; "
                  "small-bodied, and by some accounts still an "
                  "australopith.", "Smithsonian Human Origins",
                  count="~2.4 to 1.4 Ma", w=["Homo habilis"], t=(2.4, 1.4)),
                N("Homo rudolfensis",
                  "A larger, flatter-faced early Homo known from Lake "
                  "Turkana; one skull, many arguments.",
                  "Smithsonian Human Origins", count="~1.9 to 1.8 Ma",
                  w=["Homo rudolfensis"], t=(1.9, 1.8)),
                N("Later Homo",
                  "The long-legged striders that left Africa.",
                  "Smithsonian Human Origins", kids=[
                    N("Homo erectus",
                      "The first world traveler: modern body proportions, "
                      "fire and handaxes, from Africa to Java over nearly "
                      "two million years.", "Smithsonian Human Origins",
                      count="~1.89 Ma to 110 ka", w=["Homo erectus"], t=(1.89, 0.11)),
                    N("Homo floresiensis",
                      "The hobbit of Flores, a meter tall with a tiny "
                      "brain, likely an isolated dwarfed offshoot of early "
                      "Homo.", "Brown and others 2004",
                      count="~100 to 50 ka", w=["Homo floresiensis"], t=(0.1, 0.05)),
                    N("Homo luzonensis",
                      "A second island species, from Callao Cave in the "
                      "Philippines, mixing modern and australopith-like "
                      "traits.", "Detroit and others 2019",
                      count="~67 to 50 ka", w=["Homo luzonensis"], t=(0.067, 0.05)),
                    N("Homo naledi",
                      "A small-brained species from the Rising Star cave "
                      "system, surprisingly young for its anatomy.",
                      "Berger and others 2015; Dirks and others 2017",
                      count="~335 to 236 ka", w=["Homo naledi"], t=(0.335, 0.236)),
                    N("Heidelbergensis grade",
                      "The big-brained middle Pleistocene humans from whom "
                      "the last three species descend.",
                      "Smithsonian Human Origins", kids=[
                        N("Homo antecessor",
                          "Pioneer of Atapuerca, Spain, with a "
                          "surprisingly modern face; close to the last "
                          "common ancestor of the final three.",
                          "Smithsonian Human Origins",
                          count="~1.2 to 0.8 Ma", w=["Homo antecessor"], t=(1.2, 0.8)),
                        N("Homo heidelbergensis",
                          "The likely ancestor grade of Neanderthals, "
                          "Denisovans and us: hearths, wooden spears and "
                          "big-game hunting.", "Smithsonian Human Origins",
                          count="~700 to 200 ka",
                          w=["Homo heidelbergensis"], t=(0.7, 0.2)),
                        N("Sapiens and kin",
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
                                  count="~400 to 40 ka", w=["Neanderthal"], t=(0.4, 0.04)),
                                N("Denisovans",
                                  "Known mostly from DNA in a Siberian "
                                  "cave and a Tibetan jaw; their genes "
                                  "help Tibetans live at altitude.",
                                  "Reich and others 2010",
                                  count="~200 to 30 ka", w=["Denisovan"], t=(0.2, 0.03)),
                              ]),
                            N("Homo sapiens",
                              "The one survivor, in Africa by about "
                              "300,000 years ago at Jebel Irhoud and "
                              "everywhere since.",
                              "Hublin and others 2017", hl=True,
                              count="~300 ka to now",
                              w=["Homo sapiens", "Human"], t=(0.3, 0)),
                          ]),
                      ]),
                  ]),
              ]),
          ]),
    ])


PAGES = [
    ("tree-of-life.html", "Tree of Life", TREE_OF_LIFE,
     "From the last universal common ancestor at the left to living groups "
     "at the right; branch lengths carry no time. The eukaryotes sit where "
     "current evidence places them, beside the Asgard archaea inside the "
     "archaeal branch, which turns Woese's three domains into two.",
     [("Woese, C. R., Kandler, O., & Wheelis, M. L. (1990). Toward a "
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
     "From the one ancestor at the left to living phyla and, inside the "
     "chordates, the vertebrate classes; branch lengths carry no time, and "
     "counts are described species from Zhang's 2013 census. The comb "
     "jellies branch first, as gene order in chromosome-scale genomes "
     "indicated in 2023, and the fishes are one grade of several branches.",
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
     "From the deepest split at the left to orders at the right. Branch "
     "lengths carry no time until To time moves each branching point to "
     "its median divergence age; species counts are the Mammal Diversity "
     "Database's, rounded. The four placental superorders leave from one "
     "point, since the genomes still allow three ways to root them.",
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
      ("Kumar, S., Suleski, M., Craig, J. M., Kasprowicz, A. E., Sanderford, "
       "M., Li, M., Stecher, G., & Hedges, S. B. (2022). TimeTree 5: An "
       "expanded resource for species divergence times. <i>Molecular Biology "
       "and Evolution, 39</i>(8), msac174. Divergence ages read from "
       "timetree.org, data version 20260820, on 29 September 2026.",
       "https://doi.org/10.1093/molbev/msac174"),
      ("Foley, N. M., et al. (2023). A genomic timescale for placental "
       "mammal evolution. <i>Science, 380</i>(6643), eabl8189.",
       "https://doi.org/10.1126/science.abl8189"),
      ("Images: the linked group's Wikipedia article thumbnail, fetched at "
       "view time; each is credited on its article page.",
       "https://en.wikipedia.org/")]),
    ("primates.html", "Primates", PRIMATES,
     "From the mammal superorder at the left to the living great apes at "
     "the right. Branch lengths carry no time until To time moves each "
     "branching point to its median divergence age. The human line sits beside "
     "the chimpanzees and bonobos, from whom it parted roughly six to eight "
     "million years ago.",
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
      ("Kumar, S., Suleski, M., Craig, J. M., Kasprowicz, A. E., Sanderford, "
       "M., Li, M., Stecher, G., & Hedges, S. B. (2022). TimeTree 5: An "
       "expanded resource for species divergence times. <i>Molecular Biology "
       "and Evolution, 39</i>(8), msac174. Divergence ages read from "
       "timetree.org, data version 20260820, on 29 September 2026.",
       "https://doi.org/10.1093/molbev/msac174"),
      ("Mammal Diversity Database, American Society of Mammalogists. "
       "(2025).", "https://www.mammaldiversity.org/"),
      ("Images: the linked group's Wikipedia article thumbnail, fetched at "
       "view time; each is credited on its article page.",
       "https://en.wikipedia.org/")]),
    ("hominins.html", "Hominins", HOMININS,
     "The human tribe from the chimpanzee split to the present: the "
     "australopiths, the robust Paranthropus side branch and every named "
     "branch of Homo, with fossil dates beside each species (Ma, millions "
     "of years ago; ka, thousands). To time lays each species out as a bar "
     "from first to last fossil; a date on the slider lights the species "
     "alive then.",
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
[hidden] { display:none !important; }
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
.bar { display:flex; gap:8px; flex-wrap:wrap; align-items:center; margin:0 0 8px; min-height:32px; }
.bar button { background:var(--panel); color:var(--muted); border:1px solid var(--line);
  border-radius:999px; padding:6px 14px; font-size:13px; cursor:pointer; font-family:inherit; }
.bar button:hover { color:var(--text); border-color:#3d3d3d; }
.bar button.on { background:var(--accent); color:#0b1a2b; border-color:var(--accent); font-weight:600; }
.bar button.on:hover { color:#0b1a2b; }
.bar label { font-size:13px; color:var(--muted); display:flex; align-items:center; gap:8px; }
.bar input[type=range] { width:200px; accent-color:var(--accent); direction:rtl; }
.bar output { font-size:13px; color:var(--text); font-variant-numeric:tabular-nums; min-width:70px; }
.bar .hint { font-size:12px; color:#7d7d7d; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#diagram { flex:1 1 640px; min-width:0; border-radius:8px; }
#diagram:focus-visible { outline:1px solid var(--accent); outline-offset:4px; }
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
.method { color:var(--muted); font-size:12.5px; margin:0 0 12px; max-width:760px; }
.refs { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.refs p { margin:0 0 8px; overflow-wrap:anywhere; }
.refs a { color:var(--accent); }
__APACSS__
h2.refh { font-size:15px; margin:26px 0 8px; }
details.sources { margin-top:22px; border-top:1px solid var(--line); padding-top:10px; max-width:760px; }
details.sources > summary { cursor:pointer; color:var(--muted); font-size:12.5px; letter-spacing:.06em; text-transform:uppercase; }
details.sources > summary:hover { color:var(--accent); }
@media (max-width:900px){ .stage{flex-direction:column;} #diagram{width:100%; flex-basis:auto;} .side{position:static; width:100%; flex-basis:auto; order:-1;} }
@media (max-width:600px){ #diagram{overflow-x:auto; -webkit-overflow-scrolling:touch;} #diagram svg{min-width:680px;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library &middot; Life</a>__XNAV__</nav>
</header>
<h1>__TITLE__</h1>
<div class="bar" id="ctl">
  <button type="button" id="timeBtn" hidden>Make to time</button>
  <label id="scrubLab" hidden>at <input type="range" id="scrub" min="0" max="__SCRUBMAX__" step="10" value="__SCRUBMAX__"><output id="scrubOut">any date</output></label>
  <button type="button" id="scrubOff" hidden>any date</button>
  <button type="button" id="sizeBtn" hidden>Size by species</button>
  <button type="button" id="unfoldBtn" hidden>Unfold all</button>
  <span class="hint">a branch point folds with a click; the arrow keys travel the tree</span>
</div>
<div class="stage">
  <div id="diagram" tabindex="0" aria-label="__TITLE__, a tree; the arrow keys travel it"></div>
  <div class="side"><div class="card">
    <img id="cardImg" alt="">
    <div id="nameTxt">A group under the cursor lands here</div>
    <div id="cntTxt"></div>
    <div id="bodyTxt"></div>
    <div id="srcTxt"></div>
  </div></div>
</div>
<p class="note">__NOTE__</p>
<details class="sources"><summary>Sources</summary>
__METHOD__<div class="refs">__REFS__</div>
</details>
</div>
<script>
const ROOT=__DATA__, UP=__UP__, TIME=__TIME__, SIZED=__SIZED__, START=__START__;
// two kinds of time layout: fossil spans (each tip a bar from first to last
// fossil) and divergence ages (each branching point at its split, living
// tips at the present)
const FOSSIL=!!TIME && TIME.kind==='fossil', DIV=!!TIME && TIME.kind==='div';
const el=document.getElementById('diagram');
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
const REDUCED=matchMedia('(prefers-reduced-motion: reduce)').matches;
const ease=t=>t<0.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
const mix=(a,b,t)=>a+(b-a)*t;

// every node gets an id and its parent; tips are counted once for the size scale
let idc=0; const byId={}, allTips=[];
(function walk(n,p){ n.id='n'+(idc++); byId[n.id]=n; n.parent=p;
  if(n.k) n.k.forEach(c=>walk(c,n)); else allTips.push(n); })(ROOT,null);
// the species count as a number, read off the count string ("~1.2 million
// species", "~9,000 species"); a count with no figure gives null
function countNum(s){ if(!s) return null; const m=s.match(/(\\d[\\d,]*(?:\\.\\d+)?)\\s*(million)?/);
  if(!m) return null; let v=parseFloat(m[1].replace(/,/g,'')); if(m[2]) v*=1e6; return v; }
const CTOT=countNum(ROOT.c), CMAX=Math.max(...allTips.map(t=>countNum(t.c)||0));
// the fossil span of a node: a tip's own, or the oldest to youngest of its
// clade; with divergence ages, a branching point's age and a living tip's now
function span(n){ if(n.t) return n.t;
  if(DIV){ if(n.d!=null) return [n.d,n.d]; if(!n.k) return [0,0]; }
  if(!n.k) return null; let a=-1, b=1e9;
  for(const c of n.k){ const s=span(c); if(s){ a=Math.max(a,s[0]); b=Math.min(b,s[1]); } }
  return a<0?null:[a,b]; }
function alive(n,d){ if(n.k && !folded.has(n.id)) return n.k.some(c=>alive(c,d));
  const s=span(n); return !!s && s[0]>=d && s[1]<=d; }
const fmtMa=d=>d===0?'now':d>=1?(Math.round(d*100)/100)+' Ma':Math.round(d*1000)+' ka';

// state
const folded=new Set();
let mTarget=0, mCur=0;      // 0 a cladogram, 1 the time layout
let sized=false;            // tip dots scaled by species count
let scrub=null;             // a date in Ma, time layout only
let current='n0', pinned=null;

// layout: tips evenly spaced down the right, parents at the mean of their
// children, x by depth; in the time layout x is the fossil date, each tip a
// bar from its oldest to its youngest fossil and a clade at its oldest
const RS=allTips.length>16?36:42, PADT=UP?62:28, PADB=TIME?34:16, PADL=16, PADR=300, TH=34;
const W=1010; let H=0, hCur=0;
const tips=[]; let maxd=0;
const XT=ma=>PADL+(W-PADL-PADR)*(1-ma/TIME.max);
function layout(){
  tips.length=0; maxd=0;
  (function walk(n,d){ n.depth=d; n.vis=true; maxd=Math.max(maxd,d);
    if(n.k && !folded.has(n.id)) n.k.forEach(c=>walk(c,d+1));
    else { tips.push(n); (function hide(m){ if(m.k) m.k.forEach(c=>{ c.vis=false; hide(c); }); })(n); } })(ROOT,0);
  H=PADT+PADB+RS*tips.length;
  tips.forEach((t,i)=>{ t.ty=PADT+RS*(i+0.5); });
  (function place(n){ if(n.k && !folded.has(n.id)){ n.k.forEach(place);
    n.ty=n.k.reduce((a,c)=>a+c.ty,0)/n.k.length; } })(ROOT);
  const XC=d=>PADL+(W-PADL-PADR)*d/Math.max(1,maxd);
  for(const id in byId){ const n=byId[id]; if(!n.vis) continue;
    const xc=XC(n.depth); n.tx=[xc,xc,xc];
    if(TIME){ const s=span(n), leaf=!n.k||folded.has(n.id);
      const x0=s?XT(s[0]):xc, x1=s?XT(s[1]):xc;
      n.tt=[x0,x0,leaf?(DIV?XT(0):x1):x0]; }
    else n.tt=n.tx; }
}
const rad=n=>{ const leaf=!n.k||folded.has(n.id); if(!leaf) return 4;
  if(!sized||!SIZED) return 4.5; const c=countNum(n.c); if(!c) return 2;
  return Math.max(2, 2+12*(Math.log10(c)-1)/(Math.log10(CMAX)-1)); };
const target=n=>({x:mix(n.tx[0],n.tt[0],mTarget), b:mix(n.tx[1],n.tt[1],mTarget),
  e:mix(n.tx[2],n.tt[2],mTarget), y:n.ty, r:rad(n)});

// every change of layout tweens from where things are to where they go
let anim=null, t0=0; const DUR=700;
function retarget(){
  const wasVis={}; for(const id in byId) wasVis[id]=!!byId[id].vis;
  for(const id in byId){ const n=byId[id]; n.sx=n.px; n.sy=n.py; n.sb=n.pb; n.se=n.pe; n.sr=n.pr; }
  const hSnap=hCur, mSnap=mCur;
  layout();
  for(const id in byId){ const n=byId[id]; if(!n.vis||wasVis[id]) continue;
    let a=n.parent; while(a && !wasVis[a.id]) a=a.parent;   // a node just unfolded grows out of its ancestor
    if(a){ n.sx=a.sx; n.sy=a.sy; n.sb=a.sb; n.se=a.se; n.sr=a.sr; }
    else { const g=target(n); n.sx=g.x; n.sy=g.y; n.sb=g.b; n.se=g.e; n.sr=g.r; } }
  const step=k=>{ const e=ease(k);
    for(const id in byId){ const n=byId[id]; if(!n.vis) continue; const g=target(n);
      n.px=mix(n.sx,g.x,e); n.py=mix(n.sy,g.y,e); n.pb=mix(n.sb,g.b,e); n.pe=mix(n.se,g.e,e); n.pr=mix(n.sr,g.r,e); }
    hCur=mix(hSnap,H,e); mCur=mix(mSnap,mTarget,e); render(); };
  if(REDUCED){ anim=null; step(1); return; }
  t0=performance.now();
  const frame=now=>{ const k=Math.min(1,(now-t0)/DUR); step(k); if(k<1) anim=requestAnimationFrame(frame); else anim=null; };
  if(anim) cancelAnimationFrame(anim); anim=requestAnimationFrame(frame);
}

const IMG={};      // node name -> thumbnail url, filled at view time
function draw(n){
  const leaf=!n.k||folded.has(n.id);
  const x=n.px, y=n.py, col=n.hl?'var(--hl)':'#c9d1d9';
  const dim=scrub!=null && mCur>0.5 && !alive(n,scrub);
  let s='';
  if(!leaf){
    for(const c of n.k)
      s+=`<path d="M${x.toFixed(1)},${y.toFixed(1)} V${c.py.toFixed(1)} H${c.pb.toFixed(1)}" fill="none"
        stroke="#3d444d" stroke-width="1.6"/>`;
    for(const c of n.k) s+=draw(c);
  }
  const plain=n.p?` <tspan fill="#8b949e" font-size="11.5" font-weight="400">${esc(n.p)}</tspan>`:'';
  let lab;
  if(!leaf){
    const lw=Math.max(n.n.length*7, n.p?n.p.length*6.2:0);
    // no room to the left: the label sits above the node, or below it when
    // a branch leaves just above
    const ly=n.k.some(c=>c.py<y-0.5 && y-c.py<16)?y+16:y-7;
    lab = (n.depth===0 || x-9-lw<2)
      ? `<text x="${x+7}" y="${ly}" font-size="12.5"
          fill="${n.hl?'var(--hl)':'#9a9a9a'}" stroke="#121212"
          stroke-width="3" paint-order="stroke">${esc(n.n)}${plain}</text>`
      : `<text x="${x-9}" y="${y+(n.p?-1:4)}" text-anchor="end" font-size="12.5"
          fill="${n.hl?'var(--hl)':'#9a9a9a'}" stroke="#121212"
          stroke-width="3" paint-order="stroke">${esc(n.n)}</text>`
        +(n.p?`<text x="${x-9}" y="${y+12}" text-anchor="end" font-size="11" fill="#8b949e"
          stroke="#121212" stroke-width="3" paint-order="stroke">${esc(n.p)}</text>`:'');
  } else {
    const u=IMG[n.n], bar=n.pe-n.pb, x1=n.pe, tx=u?x1+16+TH:x1+9+(n.pr>4.5?n.pr-4.5:0);
    const cnt=n.k?`${countTips(n)} tips folded`:n.c;
    lab=(bar>1||(FOSSIL&&mCur>0.02)?`<rect x="${n.pb.toFixed(1)}" y="${(y-5).toFixed(1)}" width="${Math.max(4,bar).toFixed(1)}" height="10" rx="3"
        fill="${n.hl?'var(--hl)':'#58a6ff'}" opacity="0.55"/>`:'')
      +(u?`<image href="${u}" x="${x1+10}" y="${y-TH/2}" width="${TH}"
        height="${TH}" preserveAspectRatio="xMidYMin slice"/>
      <rect x="${x1+10}" y="${y-TH/2}" width="${TH}" height="${TH}"
        fill="none" stroke="#2b2b2b" stroke-width="1"/>`:'')
      +`<text x="${tx.toFixed(1)}" y="${y+4.5}" font-size="13.5" font-weight="${n.hl?700:400}"
      fill="${col}" stroke="#121212" stroke-width="3" paint-order="stroke">${esc(n.n)}${plain}${cnt?` <tspan fill="#8b949e" font-size="11.5" font-weight="400">${esc(cnt)}</tspan>`:''}${n.href?` <tspan fill="var(--accent)" font-weight="400">→</tspan>`:''}</text>`;
  }
  const hit=!leaf?Math.min(200,n.n.length*7+24):290;
  s+=`<g data-id="${n.id}"${n.href?` data-href="${n.href}"`:''} style="cursor:pointer"${dim?' opacity="0.28"':''}>
    ${n.id===pinned?`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${(n.pr+5).toFixed(1)}" fill="none"
      stroke="${n.hl?'var(--hl)':'var(--accent)'}" stroke-width="1.6"
      opacity="0.9"/>`:''}
    <rect x="${x-10}" y="${y-Math.max(12,TH/2)}" width="${hit}" height="${!leaf?24:TH}" fill="transparent"/>
    ${lab}
    ${n.k?`<g data-fold="${n.id}"><title>${folded.has(n.id)?'unfolds':'folds'} ${esc(n.n)}</title>
      <circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="10" fill="transparent"/>
      <circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="5.5"
        fill="${n.hl?'var(--hl)':'#121212'}" stroke="${n.hl?'var(--hl)':'#58a6ff'}" stroke-width="1.6"/>
      <path d="M${(x-2.8).toFixed(1)},${y.toFixed(1)} h5.6${folded.has(n.id)?` M${x.toFixed(1)},${(y-2.8).toFixed(1)} v5.6`:''}"
        stroke="${n.hl?'#0b1a2b':'#c9d1d9'}" stroke-width="1.4"/></g>`
      :`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${n.pr.toFixed(1)}"
      fill="${n.hl?'var(--hl)':'#58a6ff'}" stroke="${n.hl?'var(--hl)':'#58a6ff'}" stroke-width="1.6"/>`}</g>`;
  return s;
}
function countTips(n){ return n.k?n.k.reduce((a,c)=>a+countTips(c),0):1; }
function upNode(){
  if(!UP) return '';
  const x=ROOT.px, y=20;
  return `<path d="M${x},${ROOT.py.toFixed(1)} L${x},${y+8}" fill="none" stroke="#3d444d"
      stroke-width="1.6" stroke-dasharray="4 4"/>
    <g data-href="${UP.href}" style="cursor:pointer">
      <rect x="${x-10}" y="${y-11}" width="${UP.label.length*8+40}" height="24"
        fill="transparent"/>
      <circle cx="${x}" cy="${y}" r="4.5" fill="var(--accent)"/>
      <text x="${x+10}" y="${y+4.5}" font-size="13" fill="var(--accent)"
        >↑ ${UP.label}</text></g>`;
}
function axis(){
  if(!TIME || mCur<0.02) return '';
  const y=hCur-12; let s=`<g opacity="${mCur.toFixed(2)}">`;
  for(let ma=0; ma<=TIME.max; ma+=TIME.step){ const x=XT(ma);
    s+=`<line x1="${x.toFixed(1)}" y1="${PADT-4}" x2="${x.toFixed(1)}" y2="${(y-8).toFixed(1)}" stroke="#2b2b2b"/>
      <text x="${x.toFixed(1)}" y="${(y+4).toFixed(1)}" text-anchor="middle" font-size="11" fill="#9a9a9a">${ma?ma+' Ma':'now'}</text>`; }
  s+=`<line x1="${XT(TIME.max)}" y1="${(y-8).toFixed(1)}" x2="${XT(0)}" y2="${(y-8).toFixed(1)}" stroke="#8a94a6"/>`;
  if(scrub!=null){ const x=XT(scrub);
    s+=`<g data-scrub="1" style="cursor:ew-resize"><line x1="${x.toFixed(1)}" y1="${PADT-8}" x2="${x.toFixed(1)}" y2="${(y-8).toFixed(1)}" stroke="#ffb02e" stroke-width="1.5" stroke-dasharray="4 3"/>
      <circle cx="${x.toFixed(1)}" cy="${(y-8).toFixed(1)}" r="6" fill="#ffb02e" stroke="#121212" stroke-width="1.5"/>
      <rect x="${(x-14).toFixed(1)}" y="${PADT-8}" width="28" height="${(y-PADT+8).toFixed(1)}" fill="transparent"/>
      <text x="${x.toFixed(1)}" y="${PADT-12}" text-anchor="middle" font-size="11.5" font-weight="700" fill="#ffb02e">${fmtMa(scrub)}</text></g>`; }
  return s+'</g>';
}
function render(){
  el.innerHTML=`<svg viewBox="0 0 ${W} ${hCur.toFixed(1)}" xmlns="http://www.w3.org/2000/svg"
    id="treesvg">`+axis()+draw(ROOT)+upNode()+'</svg>';
  document.getElementById('unfoldBtn').hidden=folded.size===0;
}
function show(id){
  const n=byId[id]; if(!n) return;
  current=id;
  document.getElementById('nameTxt').textContent=n.n+(n.p?', '+n.p:'');
  let cnt=n.c||'';
  if(SIZED && CTOT && !n.k && countNum(n.c)) cnt+=', '+share(countNum(n.c)/CTOT)+' of described animal species';
  if(n.k && folded.has(n.id)) cnt=(cnt?cnt+'; ':'')+countTips(n)+' tips folded in';
  if(n.d!=null) cnt=(cnt?cnt+'; ':'')+'its branches split ~'+n.d+' Ma';
  document.getElementById('cntTxt').textContent=cnt;
  document.getElementById('bodyTxt').textContent=n.b+(n.href?' A click opens it.':'');
  document.getElementById('srcTxt').textContent=n.s+(n.d!=null?'; age: TimeTree median, '+n.dp:'');
  const img=document.getElementById('cardImg');
  if(IMG[n.n]){ img.src=IMG[n.n]; img.style.display='block'; }
  else img.style.display='none';
}
const share=f=>f>=0.1?Math.round(f*100)+'%':f>=0.01?(f*100).toFixed(1)+'%':f>=0.001?(f*100).toFixed(2)+'%':'under a tenth of a percent';
function showScrub(){
  const list=allTips.filter(t=>t.t && t.t[0]>=scrub && t.t[1]<=scrub).map(t=>t.n);
  document.getElementById('nameTxt').textContent='At '+fmtMa(scrub);
  document.getElementById('cntTxt').textContent=list.length+(list.length===1?' species':' species')+' known from then';
  document.getElementById('bodyTxt').textContent=list.length?list.join('; ')+'.':'No named hominin fossil falls on this date.';
  document.getElementById('srcTxt').textContent='The fossil ranges beside each species';
  document.getElementById('cardImg').style.display='none';
}
function fold(id){ if(folded.has(id)) folded.delete(id); else folded.add(id);
  if(pinned && !byId[pinned].vis) pinned=null; if(!byId[current].vis) current=id;
  retarget(); show(current); }

el.addEventListener('pointerover',e=>{
  if(pinned) return;
  const g=e.target.closest('[data-id]');
  if(g) show(g.getAttribute('data-id'));
});
el.addEventListener('click',e=>{
  if(dragged){ dragged=false; return; }
  const f=e.target.closest('[data-fold]');
  if(f){ fold(f.getAttribute('data-fold')); return; }
  if(e.target.closest('[data-scrub]')) return;
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
// a drag on the date marker, or along the axis, moves the date
let dragging=false, dragged=false;
const svgX=e=>{ const b=el.querySelector('svg').getBoundingClientRect(); return (e.clientX-b.left)/b.width*W; };
const svgY=e=>{ const b=el.querySelector('svg').getBoundingClientRect(); return (e.clientY-b.top)/b.height*hCur; };
function setScrub(d,fromInput){ scrub=d==null?null:Math.max(0,Math.min(TIME.max,d));
  const inp=document.getElementById('scrub'), out=document.getElementById('scrubOut');
  if(!fromInput) inp.value=scrub==null?TIME.max*1000:Math.round(scrub*1000);
  out.textContent=scrub==null?'any date':fmtMa(scrub);
  document.getElementById('scrubOff').hidden=scrub==null;
  render(); if(!pinned){ if(scrub==null) show(current); else showScrub(); } }
el.addEventListener('pointerdown',e=>{
  if(!FOSSIL || mTarget!==1) return;
  const onMarker=e.target.closest('[data-scrub]'), y=svgY(e);
  if(!onMarker && y<hCur-30) return;
  dragging=true; el.setPointerCapture(e.pointerId); e.preventDefault();
  setScrub(TIME.max*(1-(svgX(e)-PADL)/(W-PADL-PADR)));
});
el.addEventListener('pointermove',e=>{ if(!dragging) return; dragged=true;
  setScrub(TIME.max*(1-(svgX(e)-PADL)/(W-PADL-PADR))); });
window.addEventListener('pointerup',()=>{ dragging=false; });

// the controls
const timeBtn=document.getElementById('timeBtn'), sizeBtn=document.getElementById('sizeBtn');
if(TIME){ timeBtn.hidden=false;
  timeBtn.addEventListener('click',()=>{ mTarget=mTarget?0:1;
    timeBtn.classList.toggle('on',mTarget===1); timeBtn.textContent=mTarget?'To time \\u2713':'Make to time';
    document.getElementById('scrubLab').hidden=!(mTarget&&FOSSIL);
    if(!mTarget) setScrub(null); retarget(); });
  document.getElementById('scrub').addEventListener('input',e=>setScrub(+e.target.value/1000,true));
  document.getElementById('scrubOff').addEventListener('click',()=>setScrub(null)); }
if(SIZED){ sizeBtn.hidden=false;
  sizeBtn.addEventListener('click',()=>{ sized=!sized; sizeBtn.classList.toggle('on',sized);
    sizeBtn.textContent=sized?'By species \\u2713':'Size by species'; retarget(); }); }
document.getElementById('unfoldBtn').addEventListener('click',()=>{ folded.clear(); retarget(); show(current); });

// the arrow keys travel the tree while the diagram has focus: up and down
// along the rows, right into a branch, left out to its parent; Enter folds
// a branch or opens a linked tip, space pins, Escape lets go
el.addEventListener('keydown',e=>{
  const tag=(document.activeElement||{}).tagName; if(tag==='INPUT'||tag==='TEXTAREA') return;
  const n=byId[current]; if(!n) return;
  const vis=Object.values(byId).filter(m=>m.vis).sort((a,b)=>a.ty-b.ty||a.depth-b.depth);
  let next=null;
  if(e.key==='ArrowDown'){ next=vis.filter(m=>m.ty>n.ty+0.5)[0]||null; }
  else if(e.key==='ArrowUp'){ const above=vis.filter(m=>m.ty<n.ty-0.5); next=above[above.length-1]||null; }
  else if(e.key==='ArrowRight'){ if(n.k){ if(folded.has(n.id)) fold(n.id); next=n.k[0]; } }
  else if(e.key==='ArrowLeft'){ next=n.parent; }
  else if(e.key==='Enter'){ if(n.href) location.href=n.href; else if(n.k) fold(n.id); }
  else if(e.key===' '){ pinned=pinned===n.id?null:n.id; render(); }
  else if(e.key==='Escape'){ pinned=null; render(); }
  else return;
  e.preventDefault();
  if(next){ pinned=next.id; show(next.id); render(); }
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
  if(!(TIME && scrub!=null && !pinned)) show(current);
}

layout();
for(const id in byId){ const n=byId[id]; if(!n.vis) continue; const g=target(n);
  n.px=g.x; n.py=g.y; n.pb=g.b; n.pe=g.e; n.pr=g.r; }
hCur=H;
render();
{ const s=START?Object.values(byId).find(m=>m.n===START):null; show(s?s.id:'n0'); }
loadImages();
window.__tree=()=>({tips:tips.length, depth:maxd,
  nodes:Object.keys(byId).length, h:H, imgs:Object.keys(IMG).length,
  tipImgs:tips.filter(t=>IMG[t.n]).length, pinned, current, folded:[...folded],
  mode:mTarget, sized, scrub, anim:!!anim,
  pos:Object.fromEntries(Object.values(byId).filter(n=>n.vis).map(n=>[n.n,{x:n.px,y:n.py,b:n.pb,e:n.pe,r:n.pr}]))});
</script>
</body>
</html>
"""


def refs_html(refs):
    return apa.render([apa.entry(t, u) for t, u in refs])


# the time layout. The hominins carry fossil spans ("fossil": each species a
# bar from first to last fossil, a date slider). The mammals and primates
# carry divergence ages ("div": each branching point at the TimeTree median
# for its split, the living tips at now). The tree of life and the animals
# stay undated: TimeTree's medians for the earliest animal splits run
# against the order drawn here (sponge and human 750 Ma, comb jelly and
# human 721 Ma, though the comb jellies branch first), and it has no age
# for the Asgard archaea and the eukaryotes.
TIMEAXIS = {"hominins.html": {"max": 7, "step": 1, "kind": "fossil"},
            "mammals.html": {"max": 190, "step": 20, "kind": "div"},
            "primates.html": {"max": 90, "step": 10, "kind": "div"}}

# Divergence ages, Ma: the TimeTree median (precomputed age) for a pair of
# living species whose last common ancestor is the branching point, read
# from the TimeTree 5 pairwise and MRCA service (data version 20260820) on
# 29 September 2026. Name: (age, species pair).
DIVERGE = {
    "mammals.html": {
        "Mammalia": (181.2, "platypus and human"),
        "Theria": (159.2, "gray short-tailed opossum and human"),
        "Marsupialia": (73.8, "gray short-tailed opossum and Tasmanian devil"),
        "Placentalia": (97.0, "elephant, armadillo, cow and human"),
        "Euarchontoglires": (83.5, "house mouse and human"),
        "Laurasiatheria": (82.1, "European hedgehog and cow"),
    },
    "primates.html": {
        "Euarchontoglires": (83.5, "house mouse and human"),
        "Primatomorpha": (72.8, "Sunda colugo and human"),
        "Primates": (71.6, "ring-tailed lemur and human"),
        "Haplorhini": (64.9, "Philippine tarsier and human"),
        "Simiiformes": (42.4, "common marmoset and human"),
        "Catarrhini": (28.9, "rhesus macaque and human"),
        "Hominoidea": (19.6, "white-cheeked gibbon and human"),
        "Hominidae": (15.6, "Sumatran orangutan and human"),
    },
}


def put_dates(tree, ages):
    """Copy each branching point's age into its node as d (Ma) and dp
    (the species pair it was read from)."""
    if tree["n"] in ages:
        a, pair = ages[tree["n"]]
        tree["d"], tree["dp"] = a, pair
    for k in tree.get("k", []):
        put_dates(k, ages)


def div_method(fname):
    rows = "; ".join(f"{n}, {a:g} Ma ({pair})"
                     for n, (a, pair) in DIVERGE[fname].items())
    return ("In the time layout each branching point moves to the median "
            "age TimeTree gives for the split, read from a pair of living "
            "species whose last common ancestor it is, and every living "
            "group ends at the present: " + rows + ". A median across "
            "published studies, not a single study's estimate; the ranges "
            "behind them run several million years either way.")
# the pages whose tips can be sized by species count (every tip needs a count)
SIZED = {"animals.html"}
# the node the card opens on, where it is not the root
START = {"primates.html": "Primates"}
# method notes that go inside the details, under the summary
METHOD = {
    "hominins.html": (
        "Where several branches leave one point, the fossils leave their "
        "order unresolved. In the time layout each species is a bar from its "
        "oldest to its youngest fossil, the dates given beside it; a "
        "branching point sits at the oldest fossil of its clade, which is a "
        "minimum age for that clade and not a divergence date. The mammals "
        "and primates trees move their branching points to TimeTree "
        "divergence ages instead; the tree of life and the animals keep "
        "their branch lengths equal."),
}
for _f in DIVERGE:
    METHOD[_f] = div_method(_f)

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
    if fname in DIVERGE:
        put_dates(data, DIVERGE[fname])
    html = (HTML.replace("__APACSS__", apa.CSS)
            .replace("__TITLE__", title)
            .replace("__XNAV__", XNAV[fname])
            .replace("__NOTE__", note)
            .replace("__REFS__", refs_html(refs))
            .replace("__METHOD__", (f'<p class="method">{METHOD[fname]}</p>\n'
                                    if fname in METHOD else ""))
            .replace("__DATA__", json.dumps(data, separators=(",", ":")))
            .replace("__UP__", json.dumps(UPLINK[fname]))
            .replace("__TIME__", json.dumps(TIMEAXIS.get(fname)))
            .replace("__SCRUBMAX__", str(TIMEAXIS.get(fname, {}).get("max", 7) * 1000))
            .replace("__SIZED__", json.dumps(fname in SIZED))
            .replace("__START__", json.dumps(START.get(fname))))
    (ROOT / fname).write_text(html, encoding="utf-8")
    print(f"wrote {ROOT / fname} ({len(html):,} bytes)")
