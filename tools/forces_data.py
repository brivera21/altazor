#!/usr/bin/env python3
"""The data behind forces.html: the four interactions between two protons,
and a line of forces in newtons from gravity inside an atom to the Planck
force.

Couplings and masses are CODATA 2018 and the Particle Data Group; the
everyday forces carry the article or paper each comes from.
"""

import apa

# the four, as forces between two protons: k, name, color, coupling alpha,
# range lambda (m, None for infinite), a line, source
# gravity: alpha_G = G m_p^2 / (hbar c); the rest as dimensionless couplings
# at the femtometer scale; the strong and weak forces are drawn as Yukawa
# forces with the pion's and the W's reach.
FOUR = [
    ("strong", "the strong force", "#f28cb0", 1.0, 1.4138e-15,
     "Between two nucleons it is the leftover of the color force that binds quarks, carried by pions, and it fades past the pion's reach of 1.4 fm. Inside that, it beats electromagnetism a hundred times over, which is why nuclei hold.",
     "PDG 2024; Yukawa 1935"),
    ("em", "electromagnetism", "#ffb02e", 7.2973525693e-3, None,
     "Infinite in reach, falling as the inverse square, with a coupling of 1/137. Every push, pull, bond and friction in daily life is this force between electrons.",
     "CODATA 2018"),
    ("weak", "the weak force", "#9be564", 3.16e-2, 2.455e-18,
     "Not weak at all up close: its coupling is a thirtieth, stronger than electromagnetism's. It is feeble at any distance because its carriers, the W and Z, are heavy and reach only 0.002 fm. It changes one kind of quark into another; the Sun burns by it.",
     "PDG 2024"),
    ("gravity", "gravity", "#58a6ff", 5.906e-39, None,
     "Infinite in reach and thirty-six decades below electromagnetism between two protons. It wins on the large scale only because it never cancels: there is no negative mass.",
     "CODATA 2018"),
]

# places on the distance axis: k, name, meters, a line
PLACES = [
    ("w", "the W's reach", 2.455e-18, "hbar over the W mass times c: the distance a weak interaction spans"),
    ("proton", "a proton's radius", 8.41e-16, "the charge radius, CODATA 2018"),
    ("pion", "the pion's reach", 1.4138e-15, "hbar over the pion mass times c: the range of the strong force between nucleons"),
    ("nucleus", "a nucleus", 7e-15, "about the diameter of a lead nucleus"),
    ("bohr", "the Bohr radius", 5.29177e-11, "how far the electron sits from the proton in hydrogen"),
]

# forces in newtons: k, name, newtons, which of the four, what it is, a line, source
FORCES = [
    ("hgrav", "gravity inside a hydrogen atom", 3.63e-47, "gravity", "the proton pulling the electron by mass alone",
     "G times the two masses over the Bohr radius squared. Thirty-nine decades below the electric pull in the same atom, which is why chemistry can ignore gravity entirely.", "CODATA 2018"),
    ("tweezers", "optical tweezers", 1e-12, "em", "light holding a bead",
     "A focused laser beam pushes a micron-sized bead with piconewtons, enough to stretch a single DNA molecule or stall a motor protein and measure it.", "Wikipedia, Optical tweezers"),
    ("kinesin", "a motor protein", 6e-12, "em", "kinesin's stall force",
     "The molecular motor that walks cargo along microtubules stops when pulled back with about six piconewtons. Muscle is many millions of these in parallel.", "Milo and Phillips 2015"),
    ("bond", "breaking a covalent bond", 2.0e-9, "em", "a silicon-carbon bond pulled apart",
     "Two nanonewtons, measured by pulling a single polymer chain until a bond gave. Electromagnetism between a handful of electrons.", "Grandbois et al. 1999"),
    ("hydrogen", "the electric pull inside a hydrogen atom", 8.24e-8, "em", "proton on electron at the Bohr radius",
     "Coulomb's law at 53 picometers: a twelfth of a microneutron, on a particle so light it holds the electron at a speed of 2,200 km per second.", "CODATA 2018"),
    ("twopeople", "two people a meter apart", 3.3e-7, "gravity", "70 kg each, center to center",
     "A third of a microneutron. A hair weighs a million times more. Gravity between everyday things is real, measured by Cavendish in 1798, and never felt.", "CODATA 2018"),
    ("mosquito", "a mosquito's weight", 2.5e-5, "gravity", "2.5 milligrams",
     "Twenty-five micronewtons. The lightest thing on this line that a person can feel land.", "Wikipedia, Mosquito"),
    ("apple", "an apple's weight", 1.0, "gravity", "about 100 grams",
     "The newton itself, near enough: the force the Earth exerts on an apple, and the apple on the Earth.", "Wikipedia, Newton (unit)"),
    ("person", "a person's weight", 690, "gravity", "70 kg",
     "Seven hundred newtons, matched every moment by the floor pushing back, which is electromagnetism between the atoms of the shoes and the atoms of the ground.", "Wikipedia, Human body weight"),
    ("car", "a car's weight", 1.5e4, "gravity", "1,500 kg",
     "Fifteen kilonewtons, carried by four patches of rubber the size of a hand each.", "Wikipedia, Curb weight"),
    ("croc", "a crocodile's bite", 1.64e4, "em", "a saltwater crocodile",
     "Sixteen kilonewtons, the strongest bite measured in a living animal, muscle and lever arm doing the work.", "Erickson et al. 2012"),
    ("quarks", "the pull between two quarks", 1.6e5, "strong", "the color string's tension, about 1 GeV per femtometer",
     "Sixteen metric tons of force, constant with distance: stretching the string between two quarks costs energy without limit, until a new pair pops out of the vacuum. That is why no quark is ever alone.", "Wikipedia, Color confinement"),
    ("saturn", "a Saturn V at lift-off", 3.5e7, "em", "five F-1 engines",
     "Thirty-five meganewtons, gas pushed out the back: momentum, which is to say atoms colliding, which is to say electromagnetism.", "Wikipedia, Saturn V"),
    ("moon", "the Earth holding the Moon", 1.98e20, "gravity", "the two masses at 384,400 km",
     "Two hundred quintillion newtons. Gravity finally shows on this line, once the masses are worlds.", "CODATA 2018"),
    ("sun", "the Sun holding the Earth", 3.54e22, "gravity", "the two masses at one astronomical unit",
     "Thirty-five sextillion newtons, the force that bends the Earth's path into a circle each year.", "CODATA 2018"),
    ("planck", "the Planck force", 1.21e44, "gravity", "c to the fourth over G",
     "The force scale at which gravity itself goes quantum. Also, oddly, the force that would appear between any two black holes touching. Nothing is measured near it.", "CODATA 2018"),
]

REFS = [
    (apa.article("Tiesinga, E., Mohr, P. J., Newell, D. B., &amp; Taylor, B. N.", 2021,
                 "CODATA recommended values of the fundamental physical constants: 2018",
                 "Reviews of Modern Physics", 93, 2, "025010", "https://doi.org/10.1103/RevModPhys.93.025010"),
     "G, hbar, c, the elementary charge, the fine-structure constant, the proton's mass and radius, the Bohr radius."),
    (apa.article("Particle Data Group", 2024,
                 "Review of particle physics", "Physical Review D", 110, 3, "030001", "https://doi.org/10.1103/PhysRevD.110.030001"),
     "The W and pion masses, the weak mixing angle and the strong coupling."),
    (apa.article("Yukawa, H.", 1935, "On the interaction of elementary particles. I",
                 "Proceedings of the Physico-Mathematical Society of Japan. 3rd Series", 17, None, "48-57",
                 "https://doi.org/10.11429/ppmsj1919.17.0_48"),
     "The potential with a reach set by the carrier's mass, used here for the strong and weak forces."),
    (apa.article("Grandbois, M., Beyer, M., Rief, M., Clausen-Schaumann, H., &amp; Gaub, H. E.", 1999,
                 "How strong is a covalent bond?", "Science", 283, 5408, "1727-1730", "https://doi.org/10.1126/science.283.5408.1727"),
     "Two nanonewtons to break a silicon-carbon bond."),
    (apa.article("Erickson, G. M., Gignac, P. M., Steppan, S. J., Lappin, A. K., Vliet, K. A., Brueggen, J. D., Inouye, B. D., Kledzik, D., &amp; Webb, G. J. W.", 2012,
                 "Insights into the ecology and evolutionary success of crocodilians revealed through bite-force and tooth-pressure experimentation",
                 "PLoS ONE", 7, 3, "e31781", "https://doi.org/10.1371/journal.pone.0031781"),
     "The saltwater crocodile's 16,414 N."),
    (apa.book("Milo, R., &amp; Phillips, R.", 2015, "Cell biology by the numbers", "Garland Science", "http://book.bionumbers.org/"),
     "The forces of molecular motors."),
]
REFS += [(apa.wiki(f"https://en.wikipedia.org/wiki/{p}"), a) for p, a in [
    ("Fundamental_interaction", "The four, their carriers and their reach."),
    ("Yukawa_potential", "The force law drawn for the strong and weak forces."),
    ("Color_confinement", "The string tension, about a gigaelectronvolt per femtometer."),
    ("Optical_tweezers", None), ("Mosquito", None), ("Newton_(unit)", None), ("Human_body_weight", None),
    ("Curb_weight", None), ("Saturn_V", None), ("Cavendish_experiment", "Gravity between everyday masses, measured."),
]]
