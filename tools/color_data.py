#!/usr/bin/env python3
"""The data behind color.html: the three cones and the rod, the map of
every color the eye can see and the corner of it a screen can show, and
the order in which languages name colors.

The cone peaks are Bowmaker and Dartnall's 1980 measurements on a human
retina; the counts are Curcio and colleagues' 1990; the chromaticity
diagram is computed from the CIE 1931 observer as fitted by Wyman, Sloan
and Shirley; the naming sequence is Berlin and Kay's, as revised by the
World Color Survey.
"""

import apa

# the receptors: k, name, peak nm, a width for the drawn bell (nm, below and above the peak), color, count, a line
RECEPTORS = [
    ("s", "S cones, blue", 420, (22, 32), "#6ea0ff", "roughly a twentieth of the cones, and none at the very center of gaze", "The rarest cone, tuned to violet and blue. There are so few that the eye cannot resolve fine detail in blue alone, which is why blue text on black is hard to read."),
    ("m", "M cones, green", 534, (40, 44), "#7ddc7d", "about a third of the cones", "Tuned to green, though it answers to most of the visible spectrum. Its curve lies almost on top of the L cone's; color vision in the green-to-red range is the small difference between the two."),
    ("l", "L cones, red", 564, (44, 50), "#ff7d6a", "about two thirds of the cones", "Tuned to yellow-green, not red: red is what the brain makes of a strong L and a weak M. The gene for it sits on the X chromosome, which is why one man in twelve has it wrong and confuses red with green."),
    ("rod", "rods", 498, (36, 44), "#9a9a9a", "about 92 million, twenty times the cones", "The night receptors, a hundred times more sensitive than cones and blind to color. At dusk the world goes gray, and, because rods peak in the blue-green, reds go dark first and blues last."),
]
COUNTS = {"cones": 4.6e6, "rods": 92e6, "fovea_per_mm2": 199000, "cone_share": (5, 32, 63)}   # Curcio et al. 1990; the share is the usual approximate ratio S:M:L

# sRGB primaries and the white point, in CIE xy
SRGB = {"r": (0.64, 0.33), "g": (0.30, 0.60), "b": (0.15, 0.06), "w": (0.3127, 0.3290)}

# named points on the diagram: k, name, x, y, a line
POINTS = [
    ("d65", "daylight white, D65", 0.3127, 0.3290, "The white a screen aims for: average noon daylight, and the point of no hue at all. Every color is a direction and a distance from here."),
    ("a", "a tungsten bulb, illuminant A", 0.4476, 0.4074, "The warm white of a filament at 2,856 kelvin; the eye calls it white too, once it has been in the room a minute."),
    ("sun", "the Sun's surface, 5,800 kelvin", 0.3268, 0.3358, "A black body at the Sun's temperature: nearly the same white as daylight, a shade warmer."),
]

# the basic color terms in the order languages acquire them: stage, name, hex, a line
TERMS = [
    (1, "black", "#111111", "Every language has a word for dark and one for light; where there are only two, they split the world into dark-and-cool and light-and-warm."),
    (1, "white", "#f2f2f2", "The other of the first two."),
    (2, "red", "#d62828", "The first hue to get a name, everywhere: the color of blood and ripe fruit."),
    (3, "green", "#2a9d3f", "Green or yellow comes next; which one first depends on the language."),
    (3, "yellow", "#f2c11a", "Yellow or green."),
    (5, "blue", "#2b5cd6", "Blue comes late. Many languages have one word for green and blue together, which linguists call grue; Homer's sea was wine-dark, and Japanese ao covered both until the last century."),
    (6, "brown", "#7a4a1e", "Brown is next, once blue is separate."),
    (7, "purple", "#7b3fa0", "The last four come in no fixed order."),
    (7, "pink", "#f28cb0", "Pink, in English, is red made light; most languages that name it name it late."),
    (7, "orange", "#f26a1b", "Orange, named in English for the fruit, and not before the fruit arrived."),
    (7, "gray", "#8a8a8a", "Gray is last, or near it; some languages acquire it early and out of sequence."),
]
STAGES = {
    1: ("two terms", "dark and light", "the Dani of New Guinea: mili for dark and cool colors, mola for light and warm"),
    2: ("three terms", "black, white and red", "many languages of New Guinea, Africa and the Americas"),
    3: ("four terms", "plus green or yellow", ""),
    4: ("five terms", "plus the other of green and yellow", "Tzeltal, in Chiapas: black, white, red, yellow, and one word, yash, for green and blue together"),
    5: ("six terms", "plus blue", ""),
    6: ("seven terms", "plus brown", ""),
    7: ("eight to eleven terms", "plus purple, pink, orange and gray", "English and most European languages; Russian and Greek have twelve, with two blues, light and dark, as separate basic terms; Hungarian has two reds"),
}

REFS = [
    (apa.article("Bowmaker, J. K., &amp; Dartnall, H. J. A.", 1980, "Visual pigments of rods and cones in a human retina", "The Journal of Physiology", 298, 1, "501-511", "https://doi.org/10.1113/jphysiol.1980.sp013097"),
     "The peaks of the four pigments measured in one human retina: rods 498 nm, cones 420, 534 and 563."),
    (apa.article("Curcio, C. A., Sloan, K. R., Kalina, R. E., &amp; Hendrickson, A. E.", 1990, "Human photoreceptor topography", "Journal of Comparative Neurology", 292, 4, "497-523", "https://doi.org/10.1002/cne.902920402"),
     "4.6 million cones and 92 million rods in the average retina, 199,000 cones a square millimeter at the fovea."),
    (apa.article("Wyman, C., Sloan, P.-P., &amp; Shirley, P.", 2013, "Simple analytic approximations to the CIE XYZ color matching functions", "Journal of Computer Graphics Techniques", 2, 2, "1-11", "https://jcgt.org/published/0002/02/01/"),
     "The fit to the 1931 observer used to draw the spectrum, the horseshoe and the black-body curve."),
    (apa.book("Berlin, B., &amp; Kay, P.", 1969, "Basic color terms: Their universality and evolution", "University of California Press"),
     "The eleven basic terms and the order in which languages acquire them."),
    (apa.book("Kay, P., Berlin, B., Maffi, L., Merrifield, W. R., &amp; Cook, R.", 2009, "The World Color Survey", "CSLI Publications"),
     "The sequence tested and revised on 110 unwritten languages."),
]
REFS += [(apa.wiki(f"https://en.wikipedia.org/wiki/{p}"), a) for p, a in [
    ("Cone_cell", "The three cones, their peaks and their share of the retina."),
    ("Rod_cell", "The rods, their sensitivity and their peak at 498 nm."),
    ("CIE_1931_color_space", "The chromaticity diagram, the spectral locus, the white points and the dominant wavelength."),
    ("SRGB", "The primaries at (0.64, 0.33), (0.30, 0.60), (0.15, 0.06) and the D65 white."),
    ("Planckian_locus", "The black-body curve across the diagram."),
    ("Standard_illuminant", "D65 and illuminant A."),
    ("Color_blindness", "About 8 percent of men and 0.5 percent of women with red-green deficiency."),
    ("Linguistic_relativity_and_the_color_naming_debate", "Grue, Dani, Tzeltal, and the two blues of Russian and Greek."),
    ("Blue%E2%80%93green_distinction_in_language", None),
]]
