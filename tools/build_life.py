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


IMG_NOTE = (" Each living tip carries the photograph from its group's "
            "Wikipedia article, fetched at view time.")

PAGES = [
    ("tree-of-life.html", "Tree of Life", TREE_OF_LIFE,
     "The tree runs from the last universal common ancestor at the left to "
     "living groups at the right; branch lengths carry no time information. "
     "The eukaryotes are drawn where current evidence places them, beside "
     "the Asgard archaea inside the archaeal branch, which turns Woese's "
     "three domains into two. A node under the cursor fills the card."
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
     "species from Zhang's 2013 census. The comb jellies branch first, the "
     "placement chromosome-scale genomes settled in 2023, and the fishes "
     "are drawn as one grade of several branches. A node under the cursor "
     "fills the card." + IMG_NOTE,
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
     "node under the cursor fills the card." + IMG_NOTE,
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
     "cursor fills the card." + IMG_NOTE,
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
#cardImg { width:100%; height:170px; object-fit:cover; border-radius:8px;
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
  <nav class="site"><a href="library.html">&larr; Library</a>__XNAV__</nav>
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
const ROOT=__DATA__;
const el=document.getElementById('diagram');
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');

// layout: tips evenly spaced down the right, parents at the mean of their
// children, x by depth
const tips=[]; let maxd=0;
(function walk(n,d){ n.depth=d; maxd=Math.max(maxd,d);
  if(n.k) n.k.forEach(c=>walk(c,d+1)); else tips.push(n); })(ROOT,0);
const RS=42, PADT=28, PADB=16, PADL=16, PADR=300, TH=34;
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
    lab=`<text x="${x+7}" y="${n.y-7}" font-size="12.5"
      fill="${n.hl?'var(--hl)':'#9a9a9a'}">${esc(n.n)}</text>`;
  } else {
    const u=IMG[n.n], tx=u?x+16+TH:x+9;
    lab=(u?`<image href="${u}" x="${x+10}" y="${n.y-TH/2}" width="${TH}"
        height="${TH}" preserveAspectRatio="xMidYMid slice"/>
      <rect x="${x+10}" y="${n.y-TH/2}" width="${TH}" height="${TH}"
        fill="none" stroke="#2b2b2b" stroke-width="1"/>`:'')
      +`<text x="${tx}" y="${n.y+4.5}" font-size="13.5" font-weight="${n.hl?700:400}"
      fill="${col}">${esc(n.n)}${n.c?` <tspan fill="#6b7280" font-size="11.5" font-weight="400">${esc(n.c)}</tspan>`:''}</text>`;
  }
  s+=`<g data-id="${n.id}" style="cursor:default">
    <circle cx="${x}" cy="${n.y}" r="${n.k?4:4.5}"
      fill="${n.hl?'var(--hl)':(n.k?'#121212':'#58a6ff')}"
      stroke="${n.hl?'var(--hl)':'#58a6ff'}" stroke-width="1.6"/>
    <rect x="${x-10}" y="${n.y-Math.max(12,TH/2)}" width="${n.k?Math.min(200,n.n.length*7+24):290}" height="${n.k?24:TH}" fill="transparent"/>
    ${lab}</g>`;
  return s;
}
function render(){
  el.innerHTML=`<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg"
    id="treesvg">`+draw(ROOT)+'</svg>';
}
let current='n0';
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
  const g=e.target.closest('[data-id]');
  if(g) show(g.getAttribute('data-id'));
});

// photos: each node's Wikipedia article summary thumbnail, first
// candidate with a thumbnail wins; no thumbnail means no photo
async function thumb(titles,big){
  for(const t of titles){
    try{
      const r=await fetch('https://en.wikipedia.org/api/rest_v1/page/summary/'
        +encodeURIComponent(t.replace(/ /g,'_')));
      if(!r.ok) continue;
      const j=await r.json();
      if(!j.thumbnail) continue;
      return big&&j.originalimage&&j.originalimage.width>=480
        ?j.thumbnail.source.replace(/\\/(\\d+)px-/,'/480px-')
        :j.thumbnail.source;
    }catch(e){}
  }
  return null;
}
async function loadImages(){
  const all=[];
  (function walk(n){ if(n.w) all.push(n); if(n.k) n.k.forEach(walk); })(ROOT);
  await Promise.all(all.map(async n=>{
    const u=await thumb(n.w,true);
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
  tipImgs:tips.filter(t=>IMG[t.n]).length});
</script>
</body>
</html>
"""


def refs_html(refs):
    out = []
    for text, url in refs:
        out.append(f'<p>{text}\n<a href="{url}">{url}</a></p>')
    return "\n".join(out)


XNAV = {
    "tree-of-life.html": ' <a href="animals.html">Animals</a>',
    "animals.html": (' <a href="tree-of-life.html">Tree of Life</a>'
                     ' <a href="mammals.html">Mammals</a>'),
    "mammals.html": (' <a href="animals.html">Animals</a>'
                     ' <a href="primates.html">Primates</a>'),
    "primates.html": ' <a href="mammals.html">Mammals</a>',
}

for fname, title, data, note, refs in PAGES:
    html = (HTML.replace("__TITLE__", title)
            .replace("__XNAV__", XNAV[fname])
            .replace("__NOTE__", note)
            .replace("__REFS__", refs_html(refs))
            .replace("__DATA__", json.dumps(data, separators=(",", ":"))))
    (ROOT / fname).write_text(html, encoding="utf-8")
    print(f"wrote {ROOT / fname} ({len(html):,} bytes)")
