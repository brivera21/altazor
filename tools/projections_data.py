#!/usr/bin/env python3
"""The data behind projections.html: nine ways of flattening the globe,
the places whose latitudes show how much each stretches, and the routes
that look bent on one map and straight on another.

The projections are the textbook formulas; Robinson's is his table; the
coastline raster is the one shared with the Earth pages; distances use a
sphere of 6,371 km.
"""

import apa

R_EARTH = 6371.0  # km, the mean radius

# the projections: k, name, kind, year, who, a line
PROJECTIONS = [
    ("mercator", "Mercator", "conformal", 1569, "Gerardus Mercator", "Every compass course is a straight line, which is what a sailor needs, and every small shape is right; the price is that area swells without limit toward the poles. Greenland looks the size of Africa and is a fourteenth of it. The map of the internet, because a square tile stays square when zoomed."),
    ("platecarree", "Plate carrée", "equidistant along meridians", 100, "Marinus of Tyre", "Longitude straight across, latitude straight up, one degree the same length everywhere: the simplest map there is, and the way most satellite data are stored. Shapes squash toward the poles, where a single point becomes the whole top edge."),
    ("gallpeters", "Gall-Peters", "equal-area", 1855, "James Gall; Arno Peters, 1973", "A cylinder that keeps every area right by squashing shapes: the tropics are stretched tall and the high latitudes flattened. Promoted in the 1970s as the fair map, against Mercator's swollen north; cartographers found it as distorted in its own way, and just as old."),
    ("mollweide", "Mollweide", "equal-area", 1805, "Karl Mollweide", "The whole globe in an ellipse twice as wide as it is tall, with area kept true everywhere. Shapes are good near the middle and shear toward the edges; the standard map of the sky and of the cosmic microwave background."),
    ("sinusoidal", "Sinusoidal", "equal-area", 1570, "Jean Cossin, and earlier", "Parallels straight and evenly spaced, each meridian a sine curve, and every area true; the central meridian and the parallels are also at true scale. Ugly at the edges, which is why it is usually cut into lobes, one per continent."),
    ("robinson", "Robinson", "compromise", 1963, "Arthur Robinson", "Made by eye rather than by formula, from a table of what looked right, to be neither equal-area nor conformal but tolerable everywhere. The National Geographic Society's world map from 1988 to 1998."),
    ("winkel", "Winkel tripel", "compromise", 1921, "Oswald Winkel", "The average of two older projections, chosen to keep area, angle and distance all moderately wrong instead of any of them badly. The National Geographic's map since 1998, and by most measures the least distorted of the whole-world maps."),
    ("ortho", "Orthographic", "perspective", -200, "known to Hipparchus", "The globe as seen from far away: half the world at a time, the middle true and the edges foreshortened to nothing. The only map that looks like the thing itself, which is why it is the one that fools nobody."),
    ("azeq", "Azimuthal equidistant", "equidistant from the centre", 1500, "Guillaume Postel, and older", "Every distance and direction from the centre is right; everything else is wrong, more so toward the rim, where the point opposite the centre is smeared into the whole outer circle. Centred on the North Pole it is the emblem of the United Nations; centred on a city it is the map of where its flights go."),
]

# Robinson's table: latitude, PLEN (the length of the parallel), PDFE (the distance from the equator)
ROBINSON = [
    (0, 1.0000, 0.0000), (5, 0.9986, 0.0620), (10, 0.9954, 0.1240), (15, 0.9900, 0.1860), (20, 0.9822, 0.2480), (25, 0.9730, 0.3100), (30, 0.9600, 0.3720),
    (35, 0.9427, 0.4340), (40, 0.9216, 0.4958), (45, 0.8962, 0.5571), (50, 0.8679, 0.6176), (55, 0.8350, 0.6769), (60, 0.7986, 0.7346), (65, 0.7597, 0.7903),
    (70, 0.7186, 0.8435), (75, 0.6732, 0.8936), (80, 0.6213, 0.9394), (85, 0.5722, 0.9761), (90, 0.5322, 1.0000),
]

# places by latitude, for the stretch: name, latitude
PLACES = [
    ("the Equator", 0.0), ("Mexico City", 19.4), ("Cairo", 30.0), ("Madrid", 40.4), ("London", 51.5), ("Moscow", 55.8), ("Oslo", 59.9), ("Reykjavik", 64.1),
    ("Tromsø", 69.6), ("Longyearbyen, Svalbard", 78.2), ("Alert, Nunavut", 82.5),
]
GREENLAND_AFRICA = {"greenland_km2": 2166086, "africa_km2": 30370000, "greenland_lat": 72}

# the cities of the routes: k, name, lon, lat
CITIES = {
    "london": ("London", -0.13, 51.51), "tokyo": ("Tokyo", 139.69, 35.68), "newyork": ("New York", -74.01, 40.71), "madrid": ("Madrid", -3.70, 40.42),
    "santiago": ("Santiago", -70.67, -33.45), "sydney": ("Sydney", 151.21, -33.87), "mexico": ("Mexico City", -99.13, 19.43), "beijing": ("Beijing", 116.40, 39.90),
    "capetown": ("Cape Town", 18.42, -33.93), "buenosaires": ("Buenos Aires", -58.38, -34.60), "anchorage": ("Anchorage", -149.90, 61.22), "dubai": ("Dubai", 55.27, 25.20),
}
ROUTES = [
    ("london", "tokyo"), ("newyork", "madrid"), ("mexico", "beijing"), ("santiago", "sydney"), ("capetown", "buenosaires"), ("anchorage", "dubai"),
]

REFS = [
    (apa.book("Snyder, J. P.", 1987, "Map projections: A working manual (U.S. Geological Survey Professional Paper 1395)", "U.S. Government Printing Office", "https://doi.org/10.3133/pp1395"),
     "The formulas for every projection here, forward and inverse, and Tissot's indicatrix."),
    (apa.book("Snyder, J. P.", 1993, "Flattening the Earth: Two thousand years of map projections", "University of Chicago Press"),
     "The history: who made each projection and when, and what it was for."),
    (apa.article("Robinson, A. H.", 1974, "A new map projection: Its development and characteristics", "International Yearbook of Cartography", 14, None, "145-155", None),
     "The table the Robinson projection is drawn from."),
    (apa.article("Goldberg, D. M., &amp; Gott, J. R., III", 2007, "Flexion and skewness in map projections of the Earth", "Cartographica", 42, 4, "297-318", "https://doi.org/10.3138/carto.42.4.297"),
     "The scoring that puts the Winkel tripel ahead of the other whole-world maps."),
]
REFS += [(apa.wiki(f"https://en.wikipedia.org/wiki/{p}"), a) for p, a in [
    ("Map_projection", "The kinds of projection and what each preserves."),
    ("Tissot%27s_indicatrix", "The circles that show the stretch."),
    ("Mercator_projection", "The 1569 map, the formula, and the swelling of the poles."),
    ("Equirectangular_projection", None), ("Gall%E2%80%93Peters_projection", None), ("Mollweide_projection", None), ("Sinusoidal_projection", None),
    ("Robinson_projection", "The table."), ("Winkel_tripel_projection", None), ("Orthographic_map_projection", None), ("Azimuthal_equidistant_projection", None),
    ("Great-circle_distance", "The haversine formula."), ("Rhumb_line", "The loxodrome and its length."),
    ("Greenland", "2,166,086 square kilometres."), ("Africa", "About 30.4 million square kilometres."),
]]
