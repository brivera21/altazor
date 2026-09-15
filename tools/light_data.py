#!/usr/bin/env python3
"""The data behind light.html: the electromagnetic spectrum, the marks on it,
the windows the air leaves open, and the hot bodies whose glow the page draws.

Constants are the 2019 SI exact values and CODATA 2018 (Wien's constant).
The Sun's temperature is the IAU 2015 nominal value; the microwave
background is Fixsen (2009). Everything else carries the Wikipedia article
it comes from.
"""

import apa

# the bands, longest wavelength first is not how a reader thinks, so shortest first
# k, name, from (m), to (m), color, a line
BANDS = [
    ("gamma", "gamma rays", 1e-14, 1e-11, "#f28cb0",
     "From nuclei and from antimatter meeting matter. A photon here carries more than a hundred thousand electron volts, enough to break any chemical bond many times over."),
    ("xray", "X-rays", 1e-11, 1e-8, "#d99cf5",
     "Wavelengths the size of an atom, which is why they pass through flesh and stop in bone, and why crystals diffract them."),
    ("uv", "ultraviolet", 1e-8, 3.8e-7, "#a98cf2",
     "Beyond violet. Ozone stops most of it above 300 nm and nothing stops it below; what gets through tans and burns."),
    ("visible", "visible light", 3.8e-7, 7.5e-7, "#f4efe2",
     "Less than one octave, 380 to 750 nanometers, where the Sun's output peaks and the air is clear. Eyes evolved into this gap."),
    ("ir", "infrared", 7.5e-7, 1e-3, "#ffb02e",
     "Heat radiation. Everything at room temperature glows here, peaking near ten microns; water vapor absorbs most of it."),
    ("micro", "microwaves", 1e-3, 1e-1, "#e0a458",
     "Millimeters to a decimetre: radar, ovens, Wi-Fi, and the afterglow of the Big Bang, which peaks at a millimeter."),
    ("radio", "radio waves", 1e-1, 1e4, "#58a6ff",
     "From a decimetre up. Broadcasting, and the 21 cm line of hydrogen that maps the galaxy. Above ten meters or so the ionosphere reflects it back."),
]

# marks on the line: k, name, wavelength (m), what it is, a line, source
MARKS = [
    ("annih", "electron and positron annihilating", 2.426e-12, "511 keV gamma rays",
     "When an electron meets its antiparticle, both vanish into two photons of exactly this energy, the electron's mass as light. PET scanners watch for the pair.", "Wikipedia, Electron-positron annihilation"),
    ("medx", "a medical X-ray", 2.0e-11, "about 60 keV",
     "The energy a chest X-ray uses; bone stops it, soft tissue barely does. The image is a shadow.", "Wikipedia, X-ray"),
    ("cuka", "copper K-alpha", 1.5406e-10, "the crystallographer's X-ray, 0.154 nm",
     "Close to the spacing of atoms in a crystal, so a crystal scatters it into a pattern that gives the atoms away. DNA's helix was seen this way.", "Wikipedia, Siegbahn notation"),
    ("uvc", "germicidal ultraviolet", 2.54e-7, "the 254 nm mercury line",
     "Breaks DNA, which is why lamps at this wavelength sterilize, and why the ozone layer, which stops it, matters.", "Wikipedia, Ultraviolet germicidal irradiation"),
    ("violet", "the violet edge of sight", 3.8e-7, "380 nm",
     "The shortest wavelength most eyes register. The lens of the eye absorbs what lies beyond; people who have had it removed see a little further.", "Wikipedia, Visible spectrum"),
    ("sunpeak", "the Sun's peak", 5.02e-7, "502 nm, blue-green",
     "Wien's law for 5772 K. The Sun looks white, not green, because it is bright across the whole visible band and the eye sums it.", "IAU 2015; CODATA 2018"),
    ("sodium", "the sodium D line", 5.893e-7, "589 nm, orange",
     "The yellow-orange of old street lamps and of salt in a flame: two lines a fraction of a nanometer apart, the strongest in the Sun's spectrum after hydrogen.", "Wikipedia, Sodium-vapor lamp"),
    ("halpha", "hydrogen alpha", 6.563e-7, "656 nm, red",
     "The red of nebulae and of the Sun's prominences: hydrogen's electron dropping from its third orbit to its second.", "Wikipedia, H-alpha"),
    ("red", "the red edge of sight", 7.5e-7, "750 nm",
     "Where the eye gives up. The Sun still shines strongly here; nearly half its energy arrives beyond this edge, as infrared.", "Wikipedia, Visible spectrum"),
    ("remote", "a television remote", 9.4e-7, "940 nm, near infrared",
     "Just past red, invisible to the eye and plain to a phone camera, which is the quickest way to see whether a remote's battery is dead.", "Wikipedia, Remote control"),
    ("fiber", "light in an optical fiber", 1.55e-6, "1550 nm",
     "The wavelength glass is clearest at, so undersea cables use it: a pulse goes a hundred kilometers before it needs boosting.", "Wikipedia, Optical fiber"),
    ("body", "a person's glow", 9.4e-6, "the peak at body temperature, 310 K",
     "Everyone shines here, at a few hundred watts, which is what a thermal camera sees and what a snake's pit organ senses.", "Wikipedia, Thermography"),
    ("co2", "carbon dioxide's absorption", 1.5e-5, "15 microns",
     "The wavelength CO2 catches and re-emits, in the middle of where the Earth radiates its heat to space. The greenhouse effect is largely this line.", "Wikipedia, Greenhouse gas"),
    ("cmb", "the cosmic microwave background", 1.063e-3, "its peak, at 2.725 K",
     "The oldest light there is, released 380,000 years after the Big Bang and stretched a thousandfold since, arriving from every direction at once.", "Fixsen 2009"),
    ("wifi", "Wi-Fi", 6.0e-2, "5 GHz, 6 cm",
     "The higher of the two common bands. A wavelength of centimeters passes doors and reflects off walls; the router's antennas are a quarter of it long.", "Wikipedia, Wi-Fi"),
    ("oven", "a microwave oven", 1.224e-1, "2.45 GHz, 12.2 cm",
     "Water molecules turn to follow the field and heat by friction. The holes in the door's mesh are far smaller than the wave, so it stays in.", "Wikipedia, Microwave oven"),
    ("h21", "the hydrogen line", 2.11e-1, "1420 MHz, 21 cm",
     "Cold hydrogen flips its electron's spin once in ten million years and emits this. The galaxy's spiral arms were first mapped by it.", "Wikipedia, Hydrogen line"),
    ("fm", "FM radio", 3.0, "100 MHz, 3 m",
     "A wavelength of three meters, which is why a car aerial is about 75 cm, a quarter wave. Goes to the horizon and little further.", "Wikipedia, FM broadcasting"),
    ("am", "AM radio", 3.0e2, "1 MHz, 300 m",
     "Long enough to bend around hills and, at night, to bounce off the ionosphere and cross a continent.", "Wikipedia, AM broadcasting"),
]

# what reaches the ground: the windows, from (m) to (m), simplified from the
# atmospheric opacity curve
WINDOWS = [
    (3.0e-7, 1.1e-6, "the optical window, ozone at one end, water at the other"),
    (1.5e-6, 1.8e-6, "an infrared window between water bands"),
    (2.0e-6, 2.4e-6, "an infrared window between water bands"),
    (3.4e-6, 4.1e-6, "an infrared window"),
    (4.6e-6, 5.0e-6, "an infrared window"),
    (8.0e-6, 1.4e-5, "the thermal infrared window, where the Earth cools to space"),
    (1.0e-2, 1.5e1, "the radio window, water at the short end, the ionosphere at the long"),
]

# hot bodies: k, name, kelvin, a line, source
BODIES = [
    ("cmb", "the microwave background", 2.72548, "The whole sky, at the coldest temperature in nature that fills a space. Its curve is the most perfect black body ever measured.", "Fixsen 2009"),
    ("person", "a person", 310, "Body temperature. The glow peaks at nine microns, far below the visible, so people are dark in a dark room and bright to a thermal camera.", "Wikipedia, Human body temperature"),
    ("candle", "a candle flame", 1850, "Soot particles glowing. Almost all the energy is infrared; the fraction that is light is what makes a candle so dim for its heat.", "Wikipedia, Color temperature"),
    ("bulb", "a tungsten bulb", 2700, "The filament of an incandescent lamp. Seven percent of the power comes out as visible light, the rest as heat, which is why they were phased out.", "Wikipedia, Color temperature"),
    ("betelgeuse", "Betelgeuse", 3600, "A red supergiant. Cooler than a bulb's filament, and red for the same reason a dying ember is.", "Wikipedia, Betelgeuse"),
    ("sun", "the Sun", 5772, "The IAU nominal value. Peaks in the green and is bright across the whole visible band, which the eye reads as white.", "IAU 2015"),
    ("sirius", "Sirius", 9940, "The brightest star in the night sky, blue-white: the peak has moved into the ultraviolet.", "Wikipedia, Sirius"),
    ("rigel", "Rigel", 12100, "A blue supergiant. Most of its light is ultraviolet; what reaches the eye is the long tail.", "Wikipedia, Rigel"),
    ("zetapup", "Zeta Puppis", 40000, "One of the hottest naked-eye stars. The visible band catches a sliver of the total; the color has stopped changing, a saturated blue-white.", "Wikipedia, Zeta Puppis"),
]

REFS = [
    (apa.article("Tiesinga, E., Mohr, P. J., Newell, D. B., &amp; Taylor, B. N.", 2021,
                 "CODATA recommended values of the fundamental physical constants: 2018",
                 "Reviews of Modern Physics", 93, 2, "025010", "https://doi.org/10.1103/RevModPhys.93.025010"),
     "The speed of light, Planck's and Boltzmann's constants, Wien's constant and the electron volt."),
    (apa.article("Planck, M.", 1901, "Ueber das Gesetz der Energieverteilung im Normalspectrum",
                 "Annalen der Physik", 309, 3, "553-563", "https://doi.org/10.1002/andp.19013090310"),
     "The law the hot-body curves are drawn from."),
    (apa.article("Pr&scaron;a, A., Harmanec, P., Torres, G., Mamajek, E., Asplund, M., Capitaine, N., Christensen-Dalsgaard, J., Depagne, &Eacute;., Haberreiter, M., Hekker, S., Hilton, J., Kopp, G., Kostov, V., Kurtz, D. W., Laskar, J., Mason, B. D., Milone, E. F., Montgomery, M., Richards, M., ... Stewart, S. G.", 2016,
                 "Nominal values for selected solar and planetary quantities: IAU 2015 Resolution B3",
                 "The Astronomical Journal", 152, 2, "41", "https://doi.org/10.3847/0004-6256/152/2/41"),
     "The Sun's effective temperature, 5772 K."),
    (apa.article("Fixsen, D. J.", 2009, "The temperature of the cosmic microwave background",
                 "The Astrophysical Journal", 707, 2, "916-920", "https://doi.org/10.1088/0004-637X/707/2/916"),
     "2.72548 K."),
    (apa.article("Wyman, C., Sloan, P.-P., &amp; Shirley, P.", 2013,
                 "Simple analytic approximations to the CIE XYZ color matching functions",
                 "Journal of Computer Graphics Techniques", 2, 2, "1-11", "https://jcgt.org/published/0002/02/01/"),
     "The color of each wavelength and of each hot body, from the eye's three matching functions."),
]
REFS += [(apa.wiki(f"https://en.wikipedia.org/wiki/{p}"), a) for p, a in [
    ("Electromagnetic_spectrum", "The bands and their edges."),
    ("Visible_spectrum", "380 to 750 nanometers."),
    ("Black-body_radiation", "The curves, and the share of a hot body's power that is light."),
    ("Wien%27s_displacement_law", "Where each curve peaks."),
    ("Atmospheric_window", "What the air lets through."),
    ("Radio_window", "The radio window's edges."),
    ("Color_temperature", "The candle and the bulb."),
    ("Draper_point", "Where a body starts to glow visibly, about 798 K."),
    ("SRGB", "Turning the eye's three responses into a color on the screen."),
    ("Electron%E2%80%93positron_annihilation", None), ("X-ray", None), ("Siegbahn_notation", None),
    ("Ultraviolet_germicidal_irradiation", None), ("Sodium-vapor_lamp", None), ("H-alpha", None),
    ("Remote_control", None), ("Optical_fiber", None), ("Thermography", None), ("Greenhouse_gas", None),
    ("Wi-Fi", None), ("Microwave_oven", None), ("Hydrogen_line", None), ("FM_broadcasting", None),
    ("AM_broadcasting", None), ("Human_body_temperature", None), ("Betelgeuse", None), ("Sirius", None),
    ("Rigel", None), ("Zeta_Puppis", None),
]]
