#!/usr/bin/env python3
"""The data behind stars.html.

Named stars carry the effective temperature, luminosity, class, mass and
distance their Wikipedia article gives, cited one by one; a luminosity marked
variable is the article's quoted value. The main sequence is the dwarf table of
Pecaut and Mamajek (2013). The shape of a life after the main sequence follows
Iben (1967) and the textbook account; its numbers are the order of magnitude a
star of that mass reaches, not a model run.
"""

import apa

# temperature bounds of the spectral classes, kelvin: the dwarf table of
# Pecaut and Mamajek (2013), set so that every named star here falls on the
# side its published letter says, which for giants and supergiants shifts the
# line a few hundred kelvin from the dwarf value
CLASSES = [("O", 29000, 200000, "#9bb0ff"), ("B", 10000, 29000, "#aabfff"),
           ("A", 7300, 10000, "#cad7ff"), ("F", 5900, 7300, "#f8f7ff"),
           ("G", 5300, 5900, "#fff4ea"), ("K", 3850, 5300, "#ffd2a1"),
           ("M", 2300, 3850, "#ffcc6f")]

# the main sequence at birth: mass, temperature, luminosity (solar units)
MAIN_SEQUENCE = [
    (0.10, 2900, 0.0008), (0.20, 3200, 0.004), (0.30, 3400, 0.010),
    (0.50, 3800, 0.040), (0.70, 4700, 0.20), (0.80, 5100, 0.35),
    (1.00, 5772, 1.0), (1.30, 6400, 2.5), (1.60, 7200, 6.0),
    (2.00, 8400, 16.0), (2.90, 9600, 40.0), (3.50, 11000, 100.0),
    (5.00, 15500, 500.0), (10.0, 24000, 6000.0), (20.0, 33000, 60000.0),
    (40.0, 42000, 400000.0),
]

# name, temperature K, luminosity Lsun, class, mass Msun (None if unknown),
# distance ly, region, one line
STARS = [
    ("the Sun", 5772, 1.0, "G2V", 1.0, 0.0000158, "main",
     "The reference for everything on this diagram: one solar luminosity, one solar mass, one solar radius."),
    ("Sirius A", 9940, 25.4, "A1V", 2.06, 8.6, "main",
     "The brightest star in the night sky, twice the Sun's mass and twenty-five times its light, eight light years off."),
    ("Sirius B", 25200, 0.056, "DA2", 1.02, 8.6, "wd",
     "Sirius's companion, a white dwarf the size of the Earth carrying the mass of the Sun. Hotter than Sirius A, and ten thousand times fainter."),
    ("Proxima Centauri", 3042, 0.0017, "M5.5V", 0.12, 4.25, "main",
     "The nearest star to the Sun, a red dwarf too faint to see without a telescope, which will burn for trillions of years."),
    ("Alpha Centauri A", 5790, 1.52, "G2V", 1.08, 4.37, "main",
     "The Sun's near twin, a little heavier and brighter, in the nearest star system."),
    ("Alpha Centauri B", 5260, 0.50, "K1V", 0.91, 4.37, "main",
     "Its orange companion, a little lighter and dimmer than the Sun."),
    ("Barnard's Star", 3134, 0.0035, "M4V", 0.16, 5.96, "main",
     "The fastest moving star in the sky, an old red dwarf of the galactic halo passing through."),
    ("Wolf 359", 2749, 0.0011, "M6V", 0.11, 7.86, "main",
     "Near the bottom of the main sequence: a tenth of the Sun's mass and a thousandth of its light."),
    ("TRAPPIST-1", 2566, 0.000553, "M8V", 0.0898, 40.7, "main",
     "Barely a star at all, just over the line where hydrogen fuses, with seven Earth-sized planets."),
    ("Vega", 9602, 40.1, "A0V", 2.1, 25, "main",
     "The zero point of the magnitude scale for a century, spinning so fast it is flattened at the poles."),
    ("Altair", 7550, 10.6, "A7V", 1.8, 16.7, "main",
     "A fast spinner too, seen nearly pole-on, one of the first stars ever imaged as a disc."),
    ("Fomalhaut", 8590, 16.6, "A3V", 1.92, 25, "main",
     "A young A star with a ring of debris around it, imaged directly."),
    ("Procyon A", 6530, 6.93, "F5IV-V", 1.5, 11.5, "main",
     "Leaving the main sequence: its core hydrogen is nearly spent and it has begun to swell."),
    ("Procyon B", 7740, 0.00049, "DQZ", 0.6, 11.5, "wd",
     "A faint white dwarf beside Procyon, the cooled core of a star that finished long ago."),
    ("Epsilon Eridani", 5084, 0.34, "K2V", 0.82, 10.5, "main",
     "A young orange dwarf with a planet and a dust disc, a favourite of science fiction."),
    ("Tau Ceti", 5344, 0.52, "G8V", 0.78, 11.9, "main",
     "The nearest single star like the Sun, a little cooler and older."),
    ("61 Cygni A", 4526, 0.153, "K5V", 0.70, 11.4, "main",
     "The first star whose distance was measured by parallax, by Bessel in 1838."),
    ("Gliese 581", 3480, 0.013, "M3V", 0.31, 20.5, "main",
     "A red dwarf with a planetary system, a third of the Sun's mass."),
    ("Arcturus", 4286, 170, "K1.5III", 1.08, 36.7, "giant",
     "A red giant of about the Sun's mass, which is what the Sun will look like in five billion years: twenty-five times wider and 170 times brighter."),
    ("Aldebaran", 3900, 439, "K5III", 1.16, 65, "giant",
     "The eye of the Bull, a red giant forty-four times the Sun's radius."),
    ("Capella Aa", 4970, 78.7, "K0III", 2.57, 42.9, "giant",
     "A giant burning helium in its core, the red clump stage, paired with a near twin."),
    ("Pollux", 4586, 32.7, "K0III", 1.9, 33.8, "giant",
     "The nearest giant star to the Sun, with a planet."),
    ("Mira", 3000, 8400, "M7III", 1.2, 300, "giant",
     "The first variable star recognised, swelling and shrinking over 332 days on the asymptotic giant branch, near its end. Its luminosity varies."),
    ("Regulus A", 12460, 288, "B8IVn", 3.8, 79, "main",
     "Spinning at 96 percent of the speed that would tear it apart, and egg-shaped for it."),
    ("Achernar", 15000, 3150, "B6Vep", 6.7, 139, "main",
     "The flattest star known, its equator half again as wide as its poles, for the same reason."),
    ("Bellatrix", 22000, 9211, "B2III", 8.6, 250, "main",
     "Orion's shoulder, a hot blue giant at the top of the main sequence."),
    ("Spica A", 25300, 20500, "B1III-IV", 11.4, 250, "main",
     "A blue giant of eleven solar masses that will end as a supernova, part of a tight binary."),
    ("Alnitak Aa", 29500, 250000, "O9.5Iab", 33, 1260, "super",
     "The easternmost star of Orion's belt, a blue supergiant a quarter of a million times the Sun's light."),
    ("Zeta Puppis", 40000, 800000, "O4If", 56, 1080, "super",
     "One of the hottest stars visible to the eye, losing mass in a wind a million times the Sun's. Its luminosity is uncertain by a factor of two."),
    ("Rigel", 12100, 120000, "B8Ia", 21, 860, "super",
     "A blue supergiant, Orion's foot, seventy-nine times the Sun's radius and a supernova to come."),
    ("Deneb", 8525, 196000, "A2Ia", 19, 2600, "super",
     "A white supergiant among the most luminous stars known, visible to the eye from two and a half thousand light years."),
    ("Polaris", 6015, 1260, "F7Ib", 5.4, 448, "super",
     "The pole star, a Cepheid variable pulsing every four days, the kind of star that calibrates cosmic distances."),
    ("Canopus", 7400, 10700, "A9II", 8, 310, "super",
     "The second brightest star in the sky, a bright giant on its way to becoming a red supergiant."),
    ("Betelgeuse", 3600, 126000, "M1-2Ia", 17, 550, "super",
     "A red supergiant so wide it would reach past the orbit of Mars in the Sun's place, and due to explode within the next hundred thousand years."),
    ("Antares", 3660, 75900, "M1.5Iab", 12, 550, "super",
     "The heart of the Scorpion, another red supergiant near its end."),
    ("Van Maanen 2", 6130, 0.00017, "DZ8", 0.68, 14.1, "wd",
     "The nearest single white dwarf, cooled over three billion years to about the Sun's temperature at a ten thousandth of its light."),
]

REFS = [
    (apa.article("Russell, H. N.", 1914, "Relations between the spectra and other characteristics of the stars",
                 "Popular Astronomy", 22, None, "275-294", "https://ui.adsabs.harvard.edu/abs/1914PA.....22..275R"),
     "The diagram, as Russell first drew it."),
    (apa.article("Pecaut, M. J., &amp; Mamajek, E. E.", 2013,
                 "Intrinsic colors, temperatures, and bolometric corrections of pre-main-sequence stars",
                 "The Astrophysical Journal Supplement Series", 208, 1, "9", "https://doi.org/10.1088/0067-0049/208/1/9"),
     "The dwarf sequence of temperatures and luminosities, and the class boundaries."),
    (apa.article("Iben, I.", 1967, "Stellar evolution within and off the main sequence",
                 "Annual Review of Astronomy and Astrophysics", 5, None, "571-626",
                 "https://doi.org/10.1146/annurev.aa.05.090167.003103"),
     "The shape of a star's track after the main sequence."),
    (apa.book("Kippenhahn, R., Weigert, A., &amp; Weiss, A.", 2012, "Stellar structure and evolution", "Springer",
              "https://doi.org/10.1007/978-3-642-30304-3"),
     "The lifetime scaling and the fates by mass."),
    (apa.article("Heger, A., Fryer, C. L., Woosley, S. E., Langer, N., &amp; Hartmann, D. H.", 2003,
                 "How massive single stars end their life", "The Astrophysical Journal", 591, 1, "288-300",
                 "https://doi.org/10.1086/375341"),
     "Which masses leave a white dwarf, a neutron star or a black hole."),
]
for n in ["Sun", "Sirius", "Proxima Centauri", "Alpha Centauri", "Barnard's Star", "Wolf 359", "TRAPPIST-1",
          "Vega", "Altair", "Fomalhaut", "Procyon", "Epsilon Eridani", "Tau Ceti", "61 Cygni", "Gliese 581",
          "Arcturus", "Aldebaran", "Capella", "Pollux", "Mira", "Regulus", "Achernar", "Bellatrix", "Spica",
          "Alnitak", "Zeta Puppis", "Rigel", "Deneb", "Polaris", "Canopus", "Betelgeuse", "Antares", "Van Maanen 2"]:
    REFS.append(apa.wiki("https://en.wikipedia.org/wiki/" + n.replace(" ", "_").replace("'", "%27")))
