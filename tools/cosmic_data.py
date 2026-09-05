#!/usr/bin/env python3
"""The events on cosmic-timeline.html, each with the source that dates it.

Ages are years before the present. Where a claim is disputed the card
says so and gives the firmer, later date beside it.
"""

# t: years before now
# u: the uncertainty to draw, in years, or None
# k: kind, for colour: cosmos, galaxy, star, world, life, mind, us
EVENTS = [
    dict(n="The Big Bang", t=13.8e9, u=None, k="cos",
         b="The expansion begins. Every later date on this line is measured "
           "back from it.",
         r="Planck's 2018 release puts the age at 13.8 billion years; its "
           "2015 release printed 13.813 plus or minus 0.038 billion, which "
           "is the scale of the uncertainty.",
         s="Planck 2018 results VI, cosmological parameters",
         u2="https://en.wikipedia.org/wiki/Age_of_the_universe"),
    dict(n="The first light", t=13.8e9 - 370e3, u=80e3, k="cos",
         b="Atoms form, the fog clears, and the light released then is still "
           "arriving as the microwave background.",
         r="Recombination runs from about 290,000 to 370,000 years after the "
           "Big Bang, at redshift 1090 to 1270.",
         s="Chronology of the universe",
         u2="https://en.wikipedia.org/wiki/Chronology_of_the_universe"),
    dict(n="The first stars", t=13.8e9 - 200e6, u=100e6, k="cos",
         b="The first generation of stars lights up a few hundred million "
           "years in, and no one has seen one yet.",
         r="The earliest galaxy confirmed so far, MoM z14, sits at redshift "
           "14.44, some 280 million years after the Big Bang, announced in "
           "2025. Population III stars themselves remain undetected.",
         s="The earliest known galaxy, announced May 2025",
         u2="https://www.space.com/astronomy/cosmic-miracle-james-webb-space-telescope-discovers-the-earliest-galaxy-ever-seen"),
    dict(n="The Milky Way", t=13.5e9, u=300e6, k="cos",
         b="Our own galaxy starts as an overdensity and grows by swallowing "
           "smaller ones, a habit it has not given up.",
         r="Its oldest stars are nearly as old as the universe itself, and "
           "the galaxy began forming shortly after the Big Bang. The disk "
           "came later, and this date overlaps the first stars rather than "
           "following them.",
         s="The Milky Way",
         u2="https://en.wikipedia.org/wiki/Milky_Way"),
    dict(n="The Sun", t=4.5682e9, u=None, k="sol",
         b="A cloud collapses and the Sun lights. The planets take shape in "
           "the disk left spinning around it.",
         r="The oldest inclusions in meteorites, rich in calcium and "
           "aluminium, are 4,568.2 million years old, and that is one "
           "definition of the age of the solar system.",
         s="Formation and evolution of the Solar System",
         u2="https://en.wikipedia.org/wiki/Formation_and_evolution_of_the_Solar_System"),
    dict(n="The Earth", t=4.54e9, u=0.05e9, k="ear",
         b="The planet finishes accreting, and something the size of Mars "
           "hits it hard enough to make the Moon.",
         r="4.54 plus or minus 0.05 billion years, from lead isotopes in "
           "meteorites, the work Clair Patterson did in 1956.",
         s="Age of the Earth",
         u2="https://en.wikipedia.org/wiki/Age_of_the_Earth"),
    dict(n="Life", t=3.48e9, u=None, k="lif",
         b="Something starts copying itself, and has not stopped.",
         r="The firmest early evidence is the 3.48 billion year old "
           "stromatolites of the Dresser Formation in Western Australia. "
           "Older claims exist, at 3.7 billion in Greenland and 4.28 billion "
           "in Quebec, and both are disputed as possibly abiotic.",
         s="Earliest known life forms",
         u2="https://en.wikipedia.org/wiki/Earliest_known_life_forms"),
    dict(n="Many cells", t=2.1e9, u=None, k="lif",
         b="Cells stop living alone. Being large becomes possible, and then "
           "being an organism.",
         r="Large colonial fossils from the Francevillian rocks of Gabon are "
           "2.1 billion years old. The oldest multicellular organism placed "
           "in a living group is Bangiomorpha, a red alga of 1,047 million "
           "years, which also carries the oldest evidence of sex.",
         s="Multicellular organisms, and Bangiomorpha",
         u2="https://en.wikipedia.org/wiki/Bangiomorpha"),
    dict(n="The first nervous systems", t=575e6, u=25e6, k="ani",
         b="Nets of nerve cells appear in the early animals, and an animal "
           "can act on what it senses.",
         r="Nervous tissue emerges roughly 550 to 600 million years ago; the "
           "diffuse nerve nets of comb jellies and cnidarians are its "
           "simplest living form, and the bilaterian plan dates from the "
           "Ediacaran, over 550 million years ago.",
         s="Nervous system",
         u2="https://en.wikipedia.org/wiki/Nervous_system"),
    dict(n="Mammals", t=205e6, u=None, k="mam",
         b="Small, warm and nocturnal, they spend their first hundred and "
           "forty million years out of the way of the dinosaurs.",
         r="The Morganucodontidae appear in the late Triassic about 205 "
           "million years ago; Hadrocodium, from the early Jurassic, shows "
           "the first fully mammalian jaw joint and middle ear.",
         s="Evolution of mammals",
         u2="https://en.wikipedia.org/wiki/Evolution_of_mammals"),
    dict(n="Primates", t=66e6, u=None, k="pri",
         b="Hands that grip, eyes that face forward, and a long childhood.",
         r="Purgatorius, the earliest possible primate, dates to the early "
           "Paleocene about 66 million years ago, right after the asteroid. "
           "The oldest firm primate fossils are about 57 to 55 million years "
           "old, and molecular clocks push the branch back toward 85 million.",
         s="Primate",
         u2="https://en.wikipedia.org/wiki/Primate"),
    dict(n="Homo sapiens", t=315e3, u=34e3, k="sap",
         b="Us, across Africa, long before anyone wrote anything down.",
         r="The Jebel Irhoud fossils in Morocco are dated to 315 plus or "
           "minus 34 thousand years by thermoluminescence on burnt flint, "
           "which moved the origin of the species from one region to a "
           "continent.",
         s="Jebel Irhoud",
         u2="https://en.wikipedia.org/wiki/Jebel_Irhoud"),
    dict(n="Christianity", t=1993, u=None, k="art",
         b="A movement starts in Jerusalem and is a state religion within "
           "three centuries.",
         r="Scholarship dates the crucifixion to about AD 33, the letters of "
           "Paul to the 50s, and takes early Christianity up to the Council "
           "of Nicaea in 325.",
         s="Early Christianity",
         u2="https://en.wikipedia.org/wiki/Early_Christianity"),
]

