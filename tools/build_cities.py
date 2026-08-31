#!/usr/bin/env python3
"""Generate the seven city pages: los-angeles, lancaster, amherst,
tuscaloosa, omaha, northfield and new-york.

Each is the state page at city scale, on the same template: terrain and
land cover under a county grid, the peoples whose ground it was, the
city's own census series, the migration waves that filled it, and every
college with the year it opened.

Data: tools/data/cities/<key>.json (build_cities_data.py),
tools/data/city_pop.json, tools/data/universities.json,
tools/data/cities/<key>_roads.json (build_roads_data.py).

Usage: python3 build_cities.py   (after build_states.py)
"""

import json
from pathlib import Path

from build_states import HTML, refs_html

ROOT = Path(__file__).parent.parent
DATA = Path(__file__).parent / "data"
CITY = DATA / "cities"

US = {"a": "Flag of the United States"}

PAGES = {
    "la": ("los-angeles.html", "Los Angeles", "california.html", "California"),
    "lancaster": ("lancaster.html", "Lancaster", "pennsylvania.html", "Pennsylvania"),
    "amherst": ("amherst.html", "Amherst", "massachusetts.html", "Massachusetts"),
    "tuscaloosa": ("tuscaloosa.html", "Tuscaloosa", "alabama.html", "Alabama"),
    "omaha": ("omaha.html", "Omaha", "nebraska.html", "Nebraska"),
    "northfield": ("northfield.html", "Northfield", "minnesota.html", "Minnesota"),
    "nyc": ("new-york.html", "New York City", "us-cities.html", "US Cities"),
}

# which state's college list each city draws from
UNI_STATE = {"la": "ca", "lancaster": "pa", "amherst": "ma",
             "tuscaloosa": "al", "omaha": "ne", "northfield": "mn",
             "nyc": "ny"}

HIST = {}

HIST["la"] = {
    "eras": [
        {"y0": 1492, "y1": 1771, "l": "Tovaangar, the Tongva world", "f": None},
        {"y0": 1771, "y1": 1821, "l": "Spain: mission and pueblo", "f": {"a": "Cross of Burgundy"}},
        {"y0": 1821, "y1": 1848, "l": "Mexico: the rancho years", "f": {"a": "Flag of Mexico"}},
        {"y0": 1848, "y1": 1876, "l": "United States: the cattle and vigilante town", "f": US},
        {"y0": 1876, "y1": 1913, "l": "The railroads and the first boom", "f": US},
        {"y0": 1913, "y1": 1965, "l": "Aqueduct, oil, aircraft and film", "f": US},
        {"y0": 1965, "y1": 2026, "l": "The immigrant metropolis", "f": US},
    ],
    "marks": [{"y": 1781, "l": "The pueblo founded"},
              {"y": 1850, "l": "Incorporated as a US city"},
              {"y": 1913, "l": "The aqueduct opens"},
              {"y": 1992, "l": "The uprising"}],
    "border": 1850,
    "nb": [
        {"n": "San Fernando Valley", "lat": 34.20, "lon": -118.45},
        {"n": "San Gabriel Mountains", "lat": 34.30, "lon": -117.95},
        {"n": "Pacific Ocean", "lat": 33.85, "lon": -118.60, "sea": True},
        {"n": "Orange County", "lat": 33.72, "lon": -117.85},
    ],
    "pre": "the Los Angeles basin held dozens of Tongva towns; Yaanga stood "
           "where the civic center is now.",
    "nations": [
        {"n": "Tongva", "src": "en.wikipedia.org/wiki/Tongva", "poly": [[-118.70, 33.75], [-117.75, 33.72], [-117.80, 34.30], [-118.65, 34.32]], "lat": 34.02, "lon": -118.20, "note": "Their homeland, Tovaangar, ran from the Santa Monica Mountains to the Santa Ana River and out to the Channel Islands.", "after": {"y": 1852, "t": "left without a reservation when the California treaties went unratified"}},
        {"n": "Chumash", "src": "en.wikipedia.org/wiki/Chumash_people", "poly": [[-119.05, 34.02], [-118.62, 34.02], [-118.68, 34.35], [-119.05, 34.35]], "lat": 34.20, "lon": -118.85, "note": "The western edge of the basin, toward Malibu, which keeps its Chumash name.", "after": {"y": 1901, "t": "only the Santa Ynez band holds a reservation, well north of here"}},
        {"n": "Tataviam", "src": "en.wikipedia.org/wiki/Tataviam", "poly": [[-118.75, 34.35], [-118.25, 34.33], [-118.30, 34.60], [-118.72, 34.60]], "lat": 34.47, "lon": -118.50, "note": "The upper Santa Clara River, north of the Valley.", "after": {"y": 1797, "t": "taken into Mission San Fernando"}},
    ],
    "events": [
        {"y": 1769, "t": "set", "n": "The Portolá expedition", "lat": 34.07, "lon": -118.22, "note": "The first Spanish party crosses the river the Tongva called Paayme Paxaayt and camps at Yaanga.", "src": "en.wikipedia.org/wiki/Portol%C3%A1_expedition"},
        {"y": 1771, "t": "set", "n": "Mission San Gabriel", "lat": 34.10, "lon": -118.10, "note": "The mission that gave the basin's people the name Gabrieleño, and took their labor.", "src": "en.wikipedia.org/wiki/Mission_San_Gabriel_Arc%C3%A1ngel"},
        {"y": 1781, "t": "cap", "n": "El Pueblo de Los Ángeles", "lat": 34.057, "lon": -118.239, "note": "Forty-four settlers, most of them of African and Indigenous descent, found the pueblo on September 4.", "src": "en.wikipedia.org/wiki/Pobladores"},
        {"y": 1850, "t": "rem", "n": "State law and the labor of the jailed", "lat": 34.05, "lon": -118.24, "note": "California's 1850 Indian act lets the city auction the labor of Native people arrested for vagrancy, in the plaza itself.", "src": "en.wikipedia.org/wiki/Act_for_the_Government_and_Protection_of_Indians"},
        {"y": 1871, "t": "rem", "n": "The Chinese massacre", "lat": 34.056, "lon": -118.238, "note": "A mob kills eighteen Chinese residents on Calle de los Negros, one of the largest lynchings in the country's history.", "src": "en.wikipedia.org/wiki/Chinese_massacre_of_1871"},
        {"y": 1876, "t": "set", "n": "The Southern Pacific arrives", "lat": 34.056, "lon": -118.234, "note": "The rail link north, and in 1885 the Santa Fe, set off the land boom that made the modern city.", "src": "en.wikipedia.org/wiki/History_of_Los_Angeles"},
        {"y": 1892, "t": "set", "n": "Oil on Colton Street", "lat": 34.065, "lon": -118.255, "note": "Edward Doheny's strike near Westlake opens the field that made Los Angeles an oil town.", "src": "en.wikipedia.org/wiki/Los_Angeles_City_Oil_Field"},
        {"y": 1913, "t": "set", "n": "The Los Angeles Aqueduct", "lat": 34.31, "lon": -118.50, "note": "Water from the Owens Valley reaches the San Fernando Valley; the city annexes the Valley the next year.", "src": "en.wikipedia.org/wiki/Los_Angeles_Aqueduct"},
        {"y": 1932, "t": "set", "n": "The Olympics", "lat": 34.014, "lon": -118.288, "note": "The Coliseum games, and again in 1984, remake the city's picture of itself.", "src": "en.wikipedia.org/wiki/1932_Summer_Olympics"},
        {"y": 1942, "t": "rem", "n": "Japanese American incarceration", "lat": 34.050, "lon": -118.239, "note": "Little Tokyo is emptied by Executive Order 9066; some 37,000 people from the county are removed to camps.", "src": "en.wikipedia.org/wiki/Internment_of_Japanese_Americans"},
        {"y": 1965, "t": "rem", "n": "Watts", "lat": 33.940, "lon": -118.242, "note": "Six days in August after a traffic stop; 34 people die and the Kerner and McCone reports follow.", "src": "en.wikipedia.org/wiki/Watts_riots"},
        {"y": 1992, "t": "rem", "n": "The uprising", "lat": 34.010, "lon": -118.300, "note": "The acquittals in the beating of Rodney King set off six days that kill 63 people.", "src": "en.wikipedia.org/wiki/1992_Los_Angeles_riots"},
    ],
    "census": [],
    "native": [[1770, 5000, "Tongva, basin estimate"], [1850, 1000, "after the missions"]],
    "geo": {"hp": {"n": "Mount Lukens", "el": "1,548 m", "lat": 34.283, "lon": -118.234}},
    "mig": [
        dict(y0=1885, y1=1930, n="The Midwest boom", p=1200000, f=[41.5, -93.0], t=[34.05, -118.24], b=0.16,
             note="Rail fares and orange-grove advertising bring Iowans, Kansans and Ohioans; the city goes from 11,000 to over a million.",
             src="en.wikipedia.org/wiki/History_of_Los_Angeles"),
        dict(y0=1910, y1=1930, n="The Mexican Revolution", p=250000, f=[25.0, -105.0], t=[34.05, -118.23], b=-0.14,
             note="Families leaving the revolution settle around the plaza and in East Los Angeles.",
             src="en.wikipedia.org/wiki/Mexican_Revolution"),
        dict(y0=1930, y1=1940, n="The Dust Bowl", p=250000, f=[35.4, -100.5], t=[34.05, -118.30], b=0.13,
             note="Plains families arrive by highway; many go on to the valleys, many stay.",
             src="en.wikipedia.org/wiki/Dust_Bowl"),
        dict(y0=1942, y1=1970, n="The Second Great Migration", p=500000, f=[31.5, -92.0], t=[34.00, -118.28], b=-0.16,
             note="Shipyard and aircraft work draws Black families from Louisiana and Texas to Central Avenue and Watts.",
             src="en.wikipedia.org/wiki/Second_Great_Migration_(African_American)"),
        dict(y0=1965, y1=2010, n="The immigrant city", p=3000000, f=[19.4, -99.1], t=[34.05, -118.25], b=0.18,
             note="After 1965 the city takes in Mexican, Salvadoran, Guatemalan, Korean, Filipino, Iranian and Armenian communities; by 2000 four in ten residents are foreign-born.",
             src="en.wikipedia.org/wiki/Demographics_of_Los_Angeles"),
    ],
    "refs": [
        ["Tovaangar and the Tongva of the Los Angeles basin.", "https://en.wikipedia.org/wiki/Tongva"],
        ["The Chinese massacre of 1871.", "https://en.wikipedia.org/wiki/Chinese_massacre_of_1871"],
        ["The Los Angeles Aqueduct and the Owens Valley.", "https://en.wikipedia.org/wiki/Los_Angeles_Aqueduct"],
    ],
}

HIST["lancaster"] = {
    "eras": [
        {"y0": 1492, "y1": 1681, "l": "Susquehannock country", "f": None},
        {"y0": 1681, "y1": 1707, "l": "Penn's charter", "f": {"a": "Flag of England"}},
        {"y0": 1707, "y1": 1776, "l": "Great Britain: the inland capital", "f": {"a": "Flag of Great Britain"}},
        {"y0": 1776, "y1": 1812, "l": "United States; capital of Pennsylvania 1799 to 1812", "f": US},
        {"y0": 1812, "y1": 1900, "l": "The county seat and the iron trade", "f": US},
        {"y0": 1900, "y1": 2026, "l": "Manufacturing, then the refugee city", "f": US},
    ],
    "marks": [{"y": 1730, "l": "Laid out as a town"},
              {"y": 1799, "l": "State capital"},
              {"y": 1818, "l": "Incorporated as a city"}],
    "border": 1729,
    "nb": [
        {"n": "Susquehanna River", "lat": 40.05, "lon": -76.55, "sea": True},
        {"n": "York County", "lat": 39.90, "lon": -76.52},
        {"n": "Chester County", "lat": 40.05, "lon": -76.03},
        {"n": "Berks County", "lat": 40.29, "lon": -76.10},
    ],
    "pre": "the Susquehannock held the lower river; smallpox and the Iroquois "
           "wars had emptied much of the valley before Penn's surveyors came.",
    "nations": [
        {"n": "Susquehannock", "src": "en.wikipedia.org/wiki/Susquehannock", "poly": [[-76.62, 39.90], [-76.10, 39.92], [-76.15, 40.35], [-76.60, 40.33]], "lat": 40.10, "lon": -76.45, "note": "Palisaded towns on the lower Susquehanna; by 1675 war and disease had broken them.", "after": {"y": 1763, "t": "the Conestoga survivors murdered"}},
        {"n": "Lenape", "src": "en.wikipedia.org/wiki/Lenape", "poly": [[-76.20, 39.95], [-75.85, 39.97], [-75.90, 40.40], [-76.22, 40.38]], "lat": 40.18, "lon": -76.02, "note": "The eastern county, along the creeks toward the Schuylkill.", "after": {"y": 1737, "t": "driven from the Delaware valley by the Walking Purchase"}},
    ],
    "events": [
        {"y": 1690, "t": "set", "n": "Conestoga Town", "lat": 39.98, "lon": -76.36, "note": "The last Susquehannock community, living under Pennsylvania's protection.", "src": "en.wikipedia.org/wiki/Conestoga_people"},
        {"y": 1710, "t": "set", "n": "Mennonite settlement", "lat": 40.09, "lon": -76.22, "note": "Swiss Mennonite families take up land along Pequea Creek, the first of the Plain communities.", "src": "en.wikipedia.org/wiki/Pennsylvania_Dutch"},
        {"y": 1730, "t": "cap", "n": "Lancaster laid out", "lat": 40.038, "lon": -76.305, "note": "Andrew Hamilton lays out the town; it becomes the county seat and the largest inland town in the colonies.", "src": "en.wikipedia.org/wiki/Lancaster,_Pennsylvania"},
        {"y": 1744, "t": "set", "n": "The Treaty of Lancaster", "lat": 40.038, "lon": -76.305, "note": "Virginia, Maryland and Pennsylvania meet the Six Nations here; the colonies read the result as a cession of the Ohio country.", "src": "en.wikipedia.org/wiki/Treaty_of_Lancaster"},
        {"y": 1763, "t": "rem", "n": "The Conestoga massacre", "lat": 40.038, "lon": -76.303, "note": "The Paxton Boys kill six Conestoga at Conestoga Town, then fourteen more sheltering in the Lancaster workhouse.", "src": "en.wikipedia.org/wiki/Conestoga_massacre"},
        {"y": 1777, "t": "cap", "n": "Capital for a day", "lat": 40.038, "lon": -76.305, "note": "Congress meets here on September 27, 1777, fleeing Philadelphia.", "src": "en.wikipedia.org/wiki/Lancaster,_Pennsylvania"},
        {"y": 1787, "t": "set", "n": "Franklin College", "lat": 40.047, "lon": -76.321, "note": "Founded with Benjamin Franklin's gift and taught in German as well as English; merged with Marshall College in 1853.", "src": "en.wikipedia.org/wiki/Franklin_%26_Marshall_College"},
        {"y": 1799, "t": "cap", "n": "State capital", "lat": 40.038, "lon": -76.305, "note": "The seat of Pennsylvania's government until Harrisburg takes it in 1812.", "src": "en.wikipedia.org/wiki/Lancaster,_Pennsylvania"},
        {"y": 1856, "t": "set", "n": "Wheatland", "lat": 40.038, "lon": -76.336, "note": "James Buchanan runs his campaign from his house west of town.", "src": "en.wikipedia.org/wiki/Wheatland_(James_Buchanan_House)"},
        {"y": 1985, "t": "set", "n": "The refugee city", "lat": 40.038, "lon": -76.305, "note": "Church World Service resettlement makes Lancaster one of the largest per-head refugee destinations in the country.", "src": "en.wikipedia.org/wiki/Lancaster,_Pennsylvania"},
    ],
    "census": [],
    "native": [],
    "geo": {"hp": {"n": "Welsh Mountain", "el": "323 m", "lat": 40.12, "lon": -76.00}},
    "mig": [
        dict(y0=1710, y1=1775, n="Germans and the Plain sects", p=70000, f=[41.2, -76.9], t=[40.05, -76.28], b=0.15,
             note="Mennonites, Amish, Lutherans and Reformed from the Rhineland take the limestone soils, making Lancaster the richest farm county in the colonies.",
             src="en.wikipedia.org/wiki/Pennsylvania_Dutch"),
        dict(y0=1717, y1=1775, n="The Scots-Irish", p=40000, f=[40.6, -75.5], t=[40.10, -76.42], b=-0.14,
             note="Ulster families pass through toward the frontier; some settle the western townships.",
             src="en.wikipedia.org/wiki/Scotch-Irish_Americans"),
        dict(y0=1950, y1=1990, n="Puerto Rican migration", p=25000, f=[39.6, -75.9], t=[40.04, -76.30], b=0.17,
             note="Farm and factory recruitment builds a Puerto Rican community that is now near a fifth of the city.",
             src="en.wikipedia.org/wiki/Puerto_Ricans_in_the_United_States"),
        dict(y0=1990, y1=2020, n="Refugee resettlement", p=8000, f=[41.5, -76.9], t=[40.038, -76.31], b=-0.16,
             note="Bhutanese, Somali, Congolese, Iraqi and Syrian families arrive through the local resettlement office.",
             src="en.wikipedia.org/wiki/Lancaster,_Pennsylvania"),
    ],
    "refs": [
        ["The Conestoga massacre and the Paxton Boys, 1763.", "https://en.wikipedia.org/wiki/Conestoga_massacre"],
        ["Franklin and Marshall College.", "https://en.wikipedia.org/wiki/Franklin_%26_Marshall_College"],
    ],
}

HIST["amherst"] = {
    "eras": [
        {"y0": 1492, "y1": 1653, "l": "Norwottuck and Pocumtuc country", "f": None},
        {"y0": 1653, "y1": 1707, "l": "England: the Hadley grant", "f": {"a": "Flag of England"}},
        {"y0": 1707, "y1": 1776, "l": "Great Britain", "f": {"a": "Flag of Great Britain"}},
        {"y0": 1776, "y1": 1863, "l": "United States: a farming town with a college", "f": US},
        {"y0": 1863, "y1": 1947, "l": "The land-grant college town", "f": US},
        {"y0": 1947, "y1": 2026, "l": "The university town", "f": US},
    ],
    "marks": [{"y": 1759, "l": "Incorporated as Amherst"},
              {"y": 1821, "l": "Amherst College"},
              {"y": 1863, "l": "The land-grant college"}],
    "border": 1759,
    "nb": [
        {"n": "Connecticut River", "lat": 42.38, "lon": -72.62, "sea": True},
        {"n": "Holyoke Range", "lat": 42.30, "lon": -72.55},
        {"n": "Pelham Hills", "lat": 42.40, "lon": -72.42},
        {"n": "Northampton", "lat": 42.33, "lon": -72.66},
    ],
    "pre": "the Norwottuck lived on this side of the Connecticut, with fields "
           "on the meadows and fishing places at the falls.",
    "nations": [
        {"n": "Norwottuck", "src": "en.wikipedia.org/wiki/Pocumtuc", "poly": [[-72.66, 42.28], [-72.42, 42.28], [-72.44, 42.47], [-72.66, 42.47]], "lat": 42.37, "lon": -72.55, "note": "A Pocumtuc community whose planting grounds became Hadley and Amherst.", "after": {"y": 1676, "t": "driven north after King Philip's War"}},
        {"n": "Pocumtuc", "src": "en.wikipedia.org/wiki/Pocumtuc", "poly": [[-72.72, 42.45], [-72.48, 42.45], [-72.50, 42.68], [-72.74, 42.68]], "lat": 42.58, "lon": -72.60, "note": "The valley confederation centred at Deerfield, north of here.", "after": {"y": 1676, "t": "survivors withdrew north after King Philip's War"}},
        {"n": "Nipmuc", "src": "en.wikipedia.org/wiki/Nipmuc", "poly": [[-72.35, 42.22], [-72.10, 42.22], [-72.12, 42.45], [-72.36, 42.45]], "lat": 42.33, "lon": -72.22, "note": "The uplands east of the river.", "after": {"y": 1676, "t": "interned on Deer Island, then scattered"}},
    ],
    "events": [
        {"y": 1659, "t": "set", "n": "Hadley granted", "lat": 42.34, "lon": -72.59, "note": "The General Court grants land on the Norwottuck meadows; Amherst is its eastern precinct.", "src": "en.wikipedia.org/wiki/Hadley,_Massachusetts"},
        {"y": 1675, "t": "rem", "n": "King Philip's War", "lat": 42.44, "lon": -72.60, "note": "The valley burns; the Norwottuck and Pocumtuc leave for Canada and the Hudson, and the land is taken as forfeit.", "src": "en.wikipedia.org/wiki/King_Philip%27s_War"},
        {"y": 1759, "t": "cap", "n": "Amherst incorporated", "lat": 42.375, "lon": -72.519, "note": "Named for Jeffery Amherst, the general who had written of spreading smallpox among Native nations.", "src": "en.wikipedia.org/wiki/Amherst,_Massachusetts"},
        {"y": 1786, "t": "rem", "n": "Shays's Rebellion", "lat": 42.38, "lon": -72.52, "note": "Indebted farmers close the courts across the valley; the rising is put down the next winter.", "src": "en.wikipedia.org/wiki/Shays%27_Rebellion"},
        {"y": 1821, "t": "set", "n": "Amherst College", "lat": 42.371, "lon": -72.517, "note": "Founded to train ministers, from the charity fund of Amherst Academy.", "src": "en.wikipedia.org/wiki/Amherst_College"},
        {"y": 1830, "t": "set", "n": "The Dickinson Homestead", "lat": 42.376, "lon": -72.514, "note": "Emily Dickinson is born in the brick house on Main Street and writes nearly all of her poems there.", "src": "en.wikipedia.org/wiki/Emily_Dickinson_Museum"},
        {"y": 1863, "t": "set", "n": "Massachusetts Agricultural College", "lat": 42.389, "lon": -72.528, "note": "The state's Morrill land-grant college opens here; it becomes the University of Massachusetts in 1947.", "src": "en.wikipedia.org/wiki/University_of_Massachusetts_Amherst"},
        {"y": 1970, "t": "set", "n": "Hampshire College", "lat": 42.325, "lon": -72.529, "note": "Founded by the four older colleges as an experiment without departments or grades.", "src": "en.wikipedia.org/wiki/Hampshire_College"},
    ],
    "census": [],
    "native": [],
    "geo": {"hp": {"n": "Mount Norwottuck", "el": "340 m", "lat": 42.315, "lon": -72.531}},
    "mig": [
        dict(y0=1659, y1=1750, n="The valley settlers", p=6000, f=[42.35, -71.10], t=[42.37, -72.52], b=0.15,
             note="Families from the Bay towns take the meadow land the war had emptied.",
             src="en.wikipedia.org/wiki/Hadley,_Massachusetts"),
        dict(y0=1860, y1=1920, n="Irish and Polish farm labor", p=9000, f=[42.10, -72.60], t=[42.37, -72.53], b=-0.15,
             note="Irish, then Polish families work the onion and tobacco fields of the Connecticut valley.",
             src="en.wikipedia.org/wiki/Connecticut_River_Valley"),
        dict(y0=1947, y1=1975, n="The university boom", p=25000, f=[42.36, -71.06], t=[42.389, -72.528], b=0.14,
             note="The GI Bill and the state's expansion turn a farm town of six thousand into a campus town of thirty.",
             src="en.wikipedia.org/wiki/University_of_Massachusetts_Amherst"),
    ],
    "refs": [
        ["King Philip's War in the Connecticut valley.", "https://en.wikipedia.org/wiki/King_Philip%27s_War"],
        ["The Emily Dickinson Museum, the Homestead and the Evergreens.", "https://en.wikipedia.org/wiki/Emily_Dickinson_Museum"],
    ],
}

HIST["tuscaloosa"] = {
    "eras": [
        {"y0": 1492, "y1": 1540, "l": "The Mississippian chiefdoms of the Black Warrior", "f": None},
        {"y0": 1540, "y1": 1763, "l": "Spanish and French claims; Choctaw and Creek ground", "f": {"a": "Cross of Burgundy"}},
        {"y0": 1763, "y1": 1783, "l": "British West Florida", "f": {"a": "Flag of Great Britain"}},
        {"y0": 1783, "y1": 1819, "l": "United States: Mississippi and Alabama territories", "f": US},
        {"y0": 1819, "y1": 1846, "l": "State of Alabama; capital from 1826", "f": US},
        {"y0": 1846, "y1": 1900, "l": "The river town and the university", "f": US},
        {"y0": 1900, "y1": 2026, "l": "Mills, steel and the campus city", "f": US},
    ],
    "marks": [{"y": 1819, "l": "Incorporated"},
              {"y": 1826, "l": "State capital"},
              {"y": 1831, "l": "The University opens"},
              {"y": 1963, "l": "The schoolhouse door"}],
    "border": 1818,
    "nb": [
        {"n": "Black Warrior River", "lat": 33.30, "lon": -87.70, "sea": True},
        {"n": "Birmingham", "lat": 33.42, "lon": -87.22},
        {"n": "Moundville", "lat": 32.99, "lon": -87.63},
    ],
    "pre": "the Black Warrior valley held one of the largest towns north of "
           "Mexico at Moundville; by 1540 its people had dispersed into the "
           "Choctaw and Creek nations.",
    "nations": [
        {"n": "Choctaw", "src": "en.wikipedia.org/wiki/Choctaw", "poly": [[-87.90, 33.00], [-87.45, 33.02], [-87.50, 33.35], [-87.92, 33.33]], "lat": 33.10, "lon": -87.75, "note": "West of the river; their treaty cessions opened this land in 1816.", "after": {"y": 1831, "t": "removed under the Treaty of Dancing Rabbit Creek"}},
        {"n": "Muscogee (Creek)", "src": "en.wikipedia.org/wiki/Muscogee", "poly": [[-87.50, 33.05], [-87.10, 33.08], [-87.15, 33.45], [-87.55, 33.42]], "lat": 33.28, "lon": -87.30, "note": "East of the Black Warrior, to the Coosa.", "after": {"y": 1836, "t": "removed to Indian Territory"}},
    ],
    "events": [
        {"y": 1540, "t": "rem", "n": "De Soto and Mabila", "lat": 33.05, "lon": -87.60, "note": "The Spanish entrada passes through the chiefdoms; the battle at Mabila and the diseases that follow break them.", "src": "en.wikipedia.org/wiki/Mabila"},
        {"y": 1816, "t": "set", "n": "The first cabins at the falls", "lat": 33.207, "lon": -87.535, "note": "Settlers build at the head of navigation on the Black Warrior, on land ceded by the Choctaw.", "src": "en.wikipedia.org/wiki/Tuscaloosa,_Alabama"},
        {"y": 1819, "t": "set", "n": "Tuscaloosa incorporated", "lat": 33.207, "lon": -87.535, "note": "Named for Tuskaloosa, the chief who fought de Soto at Mabila.", "src": "en.wikipedia.org/wiki/Tuscaloosa,_Alabama"},
        {"y": 1826, "t": "cap", "n": "State capital", "lat": 33.209, "lon": -87.569, "note": "The capital moves here from Cahaba and stays until Montgomery takes it in 1846.", "src": "en.wikipedia.org/wiki/Tuscaloosa,_Alabama"},
        {"y": 1831, "t": "set", "n": "The University of Alabama", "lat": 33.211, "lon": -87.546, "note": "Opens with a president, a faculty of four and fifty-two students.", "src": "en.wikipedia.org/wiki/University_of_Alabama"},
        {"y": 1865, "t": "rem", "n": "Croxton's raid", "lat": 33.211, "lon": -87.546, "note": "Union cavalry burn the campus on April 4; only four buildings survive.", "src": "en.wikipedia.org/wiki/Battle_of_Tuscaloosa"},
        {"y": 1956, "t": "rem", "n": "Autherine Lucy", "lat": 33.214, "lon": -87.545, "note": "The first Black student enrolls, is met by mobs, and is expelled three days later on the pretext of her own safety.", "src": "en.wikipedia.org/wiki/Autherine_Lucy"},
        {"y": 1963, "t": "rem", "n": "The stand in the schoolhouse door", "lat": 33.212, "lon": -87.546, "note": "George Wallace blocks Foster Auditorium until federalized Guard troops make him stand aside; Vivian Malone and James Hood register.", "src": "en.wikipedia.org/wiki/Stand_in_the_Schoolhouse_Door"},
        {"y": 2011, "t": "rem", "n": "The April 27 tornado", "lat": 33.196, "lon": -87.516, "note": "An EF4 crosses the city, killing 53 people here and cutting a mile-wide track.", "src": "en.wikipedia.org/wiki/2011_Tuscaloosa%E2%80%93Birmingham_tornado"},
    ],
    "census": [],
    "native": [],
    "geo": {"hp": {"n": "Ridges north of the river", "el": "150 m", "lat": 33.30, "lon": -87.50}},
    "mig": [
        dict(y0=1816, y1=1840, n="Alabama Fever", p=120000, f=[34.5, -82.0], t=[33.21, -87.53], b=0.15,
             note="Planters from the Carolinas and Georgia move onto the ceded land, bringing enslaved people with them.",
             src="en.wikipedia.org/wiki/History_of_Alabama"),
        dict(y0=1820, y1=1860, n="The domestic slave trade", p=60000, f=[36.8, -78.5], t=[33.15, -87.60], b=-0.17,
             note="People sold from Virginia and the Carolinas are marched into the Black Belt and the river counties.",
             src="en.wikipedia.org/wiki/Slave_trade_in_the_United_States"),
        dict(y0=1916, y1=1970, n="The Great Migration out", p=90000, f=[33.21, -87.53], t=[38.6, -87.0], b=0.16,
             note="Black families leave for the industrial North; Tuscaloosa County's Black share falls through the century.",
             src="en.wikipedia.org/wiki/Great_Migration_(African_American)"),
        dict(y0=1945, y1=2000, n="The campus town", p=60000, f=[32.4, -86.3], t=[33.211, -87.546], b=-0.13,
             note="The university grows from 5,000 students after the war to over 20,000, and the city grows with it.",
             src="en.wikipedia.org/wiki/University_of_Alabama"),
    ],
    "refs": [
        ["Moundville and the Black Warrior chiefdom.", "https://en.wikipedia.org/wiki/Moundville_Archaeological_Site"],
        ["The stand in the schoolhouse door, June 11, 1963.", "https://en.wikipedia.org/wiki/Stand_in_the_Schoolhouse_Door"],
    ],
}

HIST["omaha"] = {
    "eras": [
        {"y0": 1492, "y1": 1803, "l": "Umoⁿhoⁿ and Otoe country; France and Spain on paper", "f": None},
        {"y0": 1803, "y1": 1854, "l": "United States: the Louisiana Purchase", "f": US},
        {"y0": 1854, "y1": 1867, "l": "Nebraska Territory; capital at Omaha", "f": US},
        {"y0": 1867, "y1": 1900, "l": "The Union Pacific town", "f": US},
        {"y0": 1900, "y1": 1960, "l": "Stockyards and packing houses", "f": US},
        {"y0": 1960, "y1": 2026, "l": "Insurance, rail and the refugee city", "f": US},
    ],
    "marks": [{"y": 1854, "l": "The town founded"},
              {"y": 1863, "l": "The Union Pacific starts here"},
              {"y": 1898, "l": "The Trans-Mississippi Exposition"}],
    "border": 1854,
    "nb": [
        {"n": "Missouri River", "lat": 41.10, "lon": -95.88, "sea": True},
        {"n": "Council Bluffs, Iowa", "lat": 41.26, "lon": -95.82},
        {"n": "Platte River", "lat": 41.05, "lon": -96.15, "sea": True},
    ],
    "pre": "the Umoⁿhoⁿ, the people this city is named for, farmed and hunted "
           "from villages upriver; the Otoe-Missouria held the ground south.",
    "nations": [
        {"n": "Umoⁿhoⁿ (Omaha)", "src": "en.wikipedia.org/wiki/Omaha_people", "poly": [[-96.30, 41.20], [-95.85, 41.22], [-95.90, 41.75], [-96.35, 41.72]], "lat": 41.55, "lon": -96.10, "note": "Earth-lodge villages on the west bank; their 1854 treaty ceded this ground and moved them north.", "after": {"y": 1854, "t": "ceded and moved to the reservation"}},
        {"n": "Otoe-Missouria", "src": "en.wikipedia.org/wiki/Otoe-Missouria_Tribe_of_Indians", "poly": [[-96.35, 40.75], [-95.85, 40.77], [-95.90, 41.20], [-96.38, 41.18]], "lat": 40.95, "lon": -96.12, "note": "The Platte country south of the city.", "after": {"y": 1881, "t": "removed to Indian Territory"}},
        {"n": "Ponca", "src": "en.wikipedia.org/wiki/Ponca", "poly": [[-96.45, 41.75], [-96.05, 41.77], [-96.10, 42.05], [-96.48, 42.03]], "lat": 41.90, "lon": -96.25, "note": "Upriver relatives of the Omaha; Standing Bear's 1879 trial in this city established that a Native person is a person before the law.", "after": {"y": 1877, "t": "removed to Indian Territory; Standing Bear walked back"}},
    ],
    "events": [
        {"y": 1804, "t": "set", "n": "Lewis and Clark at Council Bluff", "lat": 41.32, "lon": -95.92, "note": "The expedition's council with the Otoe and Missouria on August 3, upriver from the future city.", "src": "en.wikipedia.org/wiki/Lewis_and_Clark_Expedition"},
        {"y": 1846, "t": "set", "n": "Winter Quarters", "lat": 41.30, "lon": -95.95, "note": "Some 3,000 Latter-day Saints winter here on Omaha land; hundreds die and are buried on the bluff.", "src": "en.wikipedia.org/wiki/Winter_Quarters,_Nebraska"},
        {"y": 1854, "t": "cap", "n": "Omaha founded", "lat": 41.257, "lon": -95.938, "note": "Laid out days after the Kansas-Nebraska Act, on land the Omaha had ceded that spring; territorial capital until 1867.", "src": "en.wikipedia.org/wiki/Omaha,_Nebraska"},
        {"y": 1863, "t": "set", "n": "The Union Pacific", "lat": 41.259, "lon": -95.926, "note": "Lincoln names Omaha the eastern terminus; ground is broken on December 2.", "src": "en.wikipedia.org/wiki/Union_Pacific_Railroad"},
        {"y": 1879, "t": "set", "n": "Standing Bear v. Crook", "lat": 41.263, "lon": -95.933, "note": "In the federal courthouse here, Judge Dundy rules that a Native person is a person within the meaning of the law.", "src": "en.wikipedia.org/wiki/Standing_Bear"},
        {"y": 1883, "t": "set", "n": "The stockyards", "lat": 41.211, "lon": -95.947, "note": "South Omaha's yards grow into the largest livestock market in the world by 1955.", "src": "en.wikipedia.org/wiki/Union_Stock_Yards_(Omaha)"},
        {"y": 1898, "t": "set", "n": "The Trans-Mississippi Exposition", "lat": 41.283, "lon": -95.955, "note": "Two and a half million visitors; the Indian Congress held alongside it put 500 Native people on display.", "src": "en.wikipedia.org/wiki/Trans-Mississippi_Exposition"},
        {"y": 1919, "t": "rem", "n": "The lynching of Will Brown", "lat": 41.259, "lon": -95.938, "note": "A mob burns the courthouse and murders Will Brown during the Red Summer; troops occupy the city.", "src": "en.wikipedia.org/wiki/Omaha_race_riot_of_1919"},
        {"y": 1975, "t": "set", "n": "Resettlement begins", "lat": 41.24, "lon": -96.00, "note": "Vietnamese, then Sudanese, Somali, Karen and Yazidi families are resettled; Omaha holds one of the largest Sudanese communities in the country.", "src": "en.wikipedia.org/wiki/Omaha,_Nebraska"},
    ],
    "census": [],
    "native": [],
    "geo": {"hp": {"n": "The western bluffs", "el": "400 m", "lat": 41.29, "lon": -96.18}},
    "mig": [
        dict(y0=1865, y1=1900, n="The railroad town", p=140000, f=[41.9, -93.0], t=[41.26, -95.94], b=0.15,
             note="Irish, then Czech, German, Danish and Swedish workers come for the shops and the yards.",
             src="en.wikipedia.org/wiki/History_of_Omaha"),
        dict(y0=1900, y1=1920, n="The packing houses", p=60000, f=[46.0, -95.0], t=[41.21, -95.95], b=-0.16,
             note="Poles, Lithuanians, Croatians and Greeks fill South Omaha around the stockyards.",
             src="en.wikipedia.org/wiki/South_Omaha,_Nebraska"),
        dict(y0=1916, y1=1970, n="The Great Migration", p=40000, f=[33.5, -90.5], t=[41.29, -95.95], b=0.14,
             note="Black families from Mississippi, Alabama and Louisiana settle North Omaha and work the packing plants.",
             src="en.wikipedia.org/wiki/Great_Migration_(African_American)"),
        dict(y0=1975, y1=2020, n="Refugee resettlement", p=30000, f=[15.0, -60.0], t=[41.25, -96.00], b=-0.15,
             note="Vietnamese, Sudanese, Somali, Karen, Bhutanese and Yazidi communities arrive through the resettlement agencies.",
             src="en.wikipedia.org/wiki/Omaha,_Nebraska"),
    ],
    "refs": [
        ["Standing Bear v. Crook, 1879.", "https://en.wikipedia.org/wiki/Standing_Bear"],
        ["The Omaha race riot of 1919 and the lynching of Will Brown.", "https://en.wikipedia.org/wiki/Omaha_race_riot_of_1919"],
    ],
}

HIST["northfield"] = {
    "eras": [
        {"y0": 1492, "y1": 1851, "l": "Wahpekute Dakota country", "f": None},
        {"y0": 1851, "y1": 1858, "l": "Minnesota Territory after the Traverse des Sioux treaty", "f": US},
        {"y0": 1858, "y1": 1900, "l": "State of Minnesota: the milling town", "f": US},
        {"y0": 1900, "y1": 2026, "l": "Two colleges and a farm town", "f": US},
    ],
    "marks": [{"y": 1855, "l": "The town platted"},
              {"y": 1866, "l": "Carleton College"},
              {"y": 1874, "l": "St. Olaf College"},
              {"y": 1876, "l": "The raid"}],
    "border": 1855,
    "nb": [
        {"n": "Cannon River", "lat": 44.44, "lon": -93.26, "sea": True},
        {"n": "Faribault", "lat": 44.30, "lon": -93.27},
        {"n": "Twin Cities", "lat": 44.68, "lon": -93.24},
    ],
    "pre": "the Wahpekute band of the Dakota wintered along the Cannon River, "
           "which they called Iŋyaŋ Bosdata, the standing rock river.",
    "nations": [
        {"n": "Wahpekute Dakota", "src": "en.wikipedia.org/wiki/Wahpekute", "poly": [[-93.45, 44.28], [-92.95, 44.30], [-93.00, 44.65], [-93.48, 44.63]], "lat": 44.45, "lon": -93.22, "note": "One of the four Dakota bands of the eastern woodlands; the 1851 treaties took this land for twelve and a half cents an acre.", "after": {"y": 1863, "t": "expelled from Minnesota by act of Congress"}},
        {"n": "Mdewakanton Dakota", "src": "en.wikipedia.org/wiki/Mdewakanton", "poly": [[-93.45, 44.65], [-92.95, 44.67], [-93.00, 44.90], [-93.48, 44.88]], "lat": 44.78, "lon": -93.22, "note": "Their villages lay downriver toward the confluence at Bdote.", "after": {"y": 1863, "t": "expelled from Minnesota by act of Congress"}},
    ],
    "events": [
        {"y": 1851, "t": "rem", "n": "Traverse des Sioux", "lat": 44.33, "lon": -93.98, "note": "The Dakota cede most of southern Minnesota, including this valley; much of the payment never reaches them.", "src": "en.wikipedia.org/wiki/Treaty_of_Traverse_des_Sioux"},
        {"y": 1855, "t": "cap", "n": "Northfield platted", "lat": 44.458, "lon": -93.161, "note": "John W. North lays out a town at a dam site on the Cannon River.", "src": "en.wikipedia.org/wiki/Northfield,_Minnesota"},
        {"y": 1863, "t": "rem", "n": "The Dakota expelled", "lat": 44.46, "lon": -93.16, "note": "After the 1862 war Congress abrogates the treaties and expels the Dakota from the state; the Wahpekute lose the last of this ground.", "src": "en.wikipedia.org/wiki/Dakota_War_of_1862"},
        {"y": 1866, "t": "set", "n": "Carleton College", "lat": 44.462, "lon": -93.154, "note": "Founded as Northfield College by Minnesota Congregationalists.", "src": "en.wikipedia.org/wiki/Carleton_College"},
        {"y": 1874, "t": "set", "n": "St. Olaf College", "lat": 44.459, "lon": -93.181, "note": "Founded by Norwegian Lutheran immigrants as St. Olaf's School, on the hill west of the river.", "src": "en.wikipedia.org/wiki/St._Olaf_College"},
        {"y": 1876, "t": "set", "n": "The First National Bank raid", "lat": 44.458, "lon": -93.160, "note": "Townspeople shoot it out with the James-Younger gang on September 7; the raid ends the gang.", "src": "en.wikipedia.org/wiki/Northfield_Bank_Raid"},
        {"y": 1912, "t": "set", "n": "The St. Olaf Choir", "lat": 44.459, "lon": -93.181, "note": "F. Melius Christiansen's a cappella choir tours and sets the model for American choral singing.", "src": "en.wikipedia.org/wiki/St._Olaf_Choir"},
        {"y": 1974, "t": "set", "n": "Malt-O-Meal expands", "lat": 44.452, "lon": -93.166, "note": "The cereal mill on the river keeps the town's other trade going beside the colleges.", "src": "en.wikipedia.org/wiki/Post_Consumer_Brands"},
    ],
    "census": [],
    "native": [],
    "geo": {"hp": {"n": "The St. Olaf hill", "el": "340 m", "lat": 44.461, "lon": -93.184}},
    "mig": [
        dict(y0=1855, y1=1900, n="Norwegians and Germans", p=30000, f=[45.6, -92.2], t=[44.458, -93.17], b=0.16,
             note="Norwegian and German farm families take Rice County; the Norwegian community founds St. Olaf.",
             src="en.wikipedia.org/wiki/History_of_Minnesota"),
        dict(y0=1855, y1=1890, n="New Englanders", p=8000, f=[44.9, -92.6], t=[44.462, -93.154], b=-0.16,
             note="Yankee settlers, John North among them, bring the mills, the churches and Carleton.",
             src="en.wikipedia.org/wiki/Northfield,_Minnesota"),
        dict(y0=1990, y1=2020, n="Latino families", p=3000, f=[42.0, -94.0], t=[44.452, -93.161], b=0.15,
             note="Mexican and Central American families come for food processing and farm work; Northfield's schools are now near a fifth Latino.",
             src="en.wikipedia.org/wiki/Northfield,_Minnesota"),
    ],
    "refs": [
        ["The Treaty of Traverse des Sioux, 1851.", "https://en.wikipedia.org/wiki/Treaty_of_Traverse_des_Sioux"],
        ["The Northfield bank raid, September 7, 1876.", "https://en.wikipedia.org/wiki/Northfield_Bank_Raid"],
    ],
}

HIST["nyc"] = {
    "eras": [
        {"y0": 1492, "y1": 1624, "l": "Lenapehoking", "f": None},
        {"y0": 1624, "y1": 1664, "l": "New Netherland", "f": {"a": "Flag of the Netherlands"}},
        {"y0": 1664, "y1": 1707, "l": "England: New York", "f": {"a": "Flag of England"}},
        {"y0": 1707, "y1": 1783, "l": "Great Britain", "f": {"a": "Flag of Great Britain"}},
        {"y0": 1783, "y1": 1898, "l": "United States; capital 1785 to 1790", "f": US},
        {"y0": 1898, "y1": 1965, "l": "The consolidated city", "f": US},
        {"y0": 1965, "y1": 2026, "l": "The city after the 1965 immigration act", "f": US},
    ],
    "marks": [{"y": 1626, "l": "The purchase of Manhattan"},
              {"y": 1664, "l": "The English take it"},
              {"y": 1827, "l": "Slavery ends in New York"},
              {"y": 1898, "l": "The five boroughs join"}],
    "border": 1898,
    "nb": [
        {"n": "Hudson River", "lat": 40.85, "lon": -74.02, "sea": True},
        {"n": "Long Island Sound", "lat": 40.90, "lon": -73.72, "sea": True},
        {"n": "Atlantic Ocean", "lat": 40.45, "lon": -73.85, "sea": True},
        {"n": "New Jersey", "lat": 40.75, "lon": -74.30},
    ],
    "pre": "Lenapehoking: Munsee-speaking Lenape villages, planting grounds "
           "and oyster beds across the islands and the mainland.",
    "nations": [
        {"n": "Lenape", "src": "en.wikipedia.org/wiki/Lenape", "poly": [[-74.20, 40.55], [-73.72, 40.55], [-73.75, 40.95], [-74.22, 40.93]], "lat": 40.78, "lon": -73.95, "note": "Manhattan, the Bronx and the western Island; the name Manhattan is theirs.", "after": {"y": 1750, "t": "pushed west and north out of the region"}},
        {"n": "Canarsee", "src": "en.wikipedia.org/wiki/Canarsee", "poly": [[-74.05, 40.55], [-73.75, 40.56], [-73.78, 40.72], [-74.06, 40.71]], "lat": 40.63, "lon": -73.92, "note": "The Lenape band of western Long Island, whose name survives in Canarsie."},
        {"n": "Matinecock", "src": "en.wikipedia.org/wiki/Matinecock", "poly": [[-73.85, 40.70], [-73.55, 40.72], [-73.58, 40.90], [-73.87, 40.88]], "lat": 40.80, "lon": -73.70, "note": "Northern Queens and the Sound shore."},
    ],
    "events": [
        {"y": 1609, "t": "set", "n": "Hudson in the harbor", "lat": 40.70, "lon": -74.02, "note": "The Halve Maen enters the river; the Dutch claim follows.", "src": "en.wikipedia.org/wiki/Henry_Hudson"},
        {"y": 1624, "t": "set", "n": "New Amsterdam", "lat": 40.704, "lon": -74.013, "note": "A company post at the tip of Manhattan; by 1643 eighteen languages are spoken in it.", "src": "en.wikipedia.org/wiki/New_Amsterdam"},
        {"y": 1643, "t": "rem", "n": "Kieft's War", "lat": 40.73, "lon": -74.03, "note": "Director Kieft's raids kill hundreds of Lenape, including the massacre at Pavonia.", "src": "en.wikipedia.org/wiki/Kieft%27s_War"},
        {"y": 1664, "t": "cap", "n": "New York", "lat": 40.704, "lon": -74.011, "note": "An English fleet takes the town without a shot; Stuyvesant surrenders it in August.", "src": "en.wikipedia.org/wiki/History_of_New_York_City"},
        {"y": 1712, "t": "rem", "n": "The slave revolt of 1712", "lat": 40.712, "lon": -74.006, "note": "One in five people in the city is enslaved; the rising and its punishments harden the slave codes.", "src": "en.wikipedia.org/wiki/New_York_Slave_Revolt_of_1712"},
        {"y": 1754, "t": "set", "n": "King's College", "lat": 40.807, "lon": -73.962, "note": "Chartered by George II; renamed Columbia after the Revolution.", "src": "en.wikipedia.org/wiki/Columbia_University"},
        {"y": 1785, "t": "cap", "n": "Capital of the United States", "lat": 40.707, "lon": -74.010, "note": "Congress meets at Federal Hall; Washington is inaugurated there in 1789.", "src": "en.wikipedia.org/wiki/Federal_Hall"},
        {"y": 1811, "t": "set", "n": "The Commissioners' Plan", "lat": 40.75, "lon": -73.98, "note": "The grid is laid over Manhattan above Houston Street, before the city reaches it.", "src": "en.wikipedia.org/wiki/Commissioners%27_Plan_of_1811"},
        {"y": 1827, "t": "set", "n": "Emancipation in New York", "lat": 40.712, "lon": -74.006, "note": "State law frees the last enslaved New Yorkers on July 4.", "src": "en.wikipedia.org/wiki/Slavery_in_New_York"},
        {"y": 1863, "t": "rem", "n": "The draft riots", "lat": 40.735, "lon": -73.99, "note": "Four days of violence aimed at Black New Yorkers; the Colored Orphan Asylum is burned.", "src": "en.wikipedia.org/wiki/New_York_City_draft_riots"},
        {"y": 1892, "t": "set", "n": "Ellis Island opens", "lat": 40.699, "lon": -74.039, "note": "Twelve million people pass through before it closes in 1954.", "src": "en.wikipedia.org/wiki/Ellis_Island"},
        {"y": 1898, "t": "cap", "n": "The five boroughs", "lat": 40.712, "lon": -74.006, "note": "Manhattan, Brooklyn, Queens, the Bronx and Staten Island consolidate on January 1.", "src": "en.wikipedia.org/wiki/City_of_Greater_New_York"},
        {"y": 1904, "t": "set", "n": "The subway", "lat": 40.751, "lon": -73.977, "note": "The IRT opens and the city's growth follows the lines out into the boroughs.", "src": "en.wikipedia.org/wiki/New_York_City_Subway"},
        {"y": 1969, "t": "set", "n": "Stonewall", "lat": 40.734, "lon": -74.002, "note": "Six nights of resistance to a police raid on Christopher Street.", "src": "en.wikipedia.org/wiki/Stonewall_riots"},
        {"y": 2001, "t": "rem", "n": "September 11", "lat": 40.711, "lon": -74.013, "note": "2,753 people are killed at the World Trade Center.", "src": "en.wikipedia.org/wiki/September_11_attacks"},
    ],
    "census": [],
    "native": [],
    "geo": {"hp": {"n": "Todt Hill", "el": "125 m", "lat": 40.598, "lon": -74.099}},
    "mig": [
        dict(y0=1845, y1=1860, n="The Irish famine", p=900000, f=[41.8, -74.6], t=[40.71, -74.00], b=0.15,
             note="By 1855 the Irish-born are more than a quarter of the city.",
             src="en.wikipedia.org/wiki/Irish_Americans_in_New_York_City"),
        dict(y0=1880, y1=1924, n="Ellis Island", p=4000000, f=[41.3, -73.3], t=[40.699, -74.039], b=-0.13,
             note="Italians, Eastern European Jews, Poles, Greeks and Hungarians land at Castle Garden and then Ellis Island, until the 1924 quotas close the door.",
             src="en.wikipedia.org/wiki/Ellis_Island"),
        dict(y0=1916, y1=1970, n="The Great Migration", p=800000, f=[33.5, -80.0], t=[40.81, -73.94], b=0.17,
             note="Black southerners come north to Harlem and Bedford-Stuyvesant.",
             src="en.wikipedia.org/wiki/Great_Migration_(African_American)"),
        dict(y0=1945, y1=1970, n="The Puerto Rican migration", p=700000, f=[39.6, -73.4], t=[40.80, -73.93], b=-0.18,
             note="Air travel and citizenship bring some 700,000 people to East Harlem and the South Bronx.",
             src="en.wikipedia.org/wiki/Puerto_Ricans_in_New_York_City"),
        dict(y0=1965, y1=2020, n="After the 1965 act", p=3000000, f=[40.2, -73.1], t=[40.73, -73.87], b=0.12,
             note="Dominican, Chinese, Jamaican, Guyanese, Mexican, Bangladeshi and West African communities remake Queens and the Bronx; over a third of the city is foreign-born.",
             src="en.wikipedia.org/wiki/Immigration_Nationality_Act_of_1965"),
    ],
    "refs": [
        ["Lenapehoking and the Lenape of the harbor.", "https://en.wikipedia.org/wiki/Lenape"],
        ["The consolidation of Greater New York, 1898.", "https://en.wikipedia.org/wiki/City_of_Greater_New_York"],
        ["Ellis Island and the years of the great arrival.", "https://en.wikipedia.org/wiki/Ellis_Island"],
    ],
}

# the event that stands for the city itself: its circle carries the
# census series, so the subject of the page grows on its own map
SEAT = {"la": "El Pueblo de Los Ángeles",
        "lancaster": "Lancaster laid out",
        "amherst": "Amherst incorporated",
        "tuscaloosa": "Tuscaloosa incorporated",
        "omaha": "Omaha founded",
        "northfield": "Northfield platted",
        "nyc": "New Amsterdam"}

# the author's own campuses, gold on the city maps; Lincoln lies
# outside the Omaha view, so that one is on the Nebraska page alone
MINE = {
    "lancaster": ("Franklin and Marshall College", "F&M"),
    "amherst": ("University of Massachusetts Amherst", "UMass"),
    "tuscaloosa": ("University of Alabama", "UA"),
    "northfield": ("St. Olaf College", "St. Olaf"),
}

NOTE1 = ("The ground itself: relief shaded live from the AWS Terrain Tiles, "
         "woods and water from the USGS land cover, county lines from the "
         "Census files. Each chip turns a layer on or off; a mark under the "
         "cursor fills the card and a click pins it.")
NOTE2 = ("The slider runs from 1492: first the peoples whose ground this "
         "was, as colored patches approximating documented homelands, then "
         "the founding, the turns and the losses year by year. The city's "
         "circle grows with its census once it passes ten thousand, green "
         "through yellow and orange to red. Golden arrows are the "
         "migrations that filled it, joining "
         "regions rather than exact places. Mortarboards are colleges, each "
         "from the year it opened.")


def densify(poly, n=4):
    """Split every edge, so the map's curve smoothing hugs the outline.

    At state scale a four-corner homeland smooths into a pleasant blob;
    at city scale that overshoot swallows the whole view.
    """
    out = []
    for i, (x0, y0) in enumerate(poly):
        x1, y1 = poly[(i + 1) % len(poly)]
        for k in range(n):
            t = k / n
            out.append([round(x0 + (x1 - x0) * t, 4),
                        round(y0 + (y1 - y0) * t, 4)])
    return out


def refs_for(key, hist):
    rows = [
        ("County lines and recent populations: Census cartographic files via Plotly's mirror.", "https://github.com/plotly/datasets"),
        ("Relief: Mapzen and AWS Terrain Tiles (Open Data).", "https://registry.opendata.aws/terrain-tiles/"),
        ("Woods and water: USGS National Land Cover Database 2021, forest and water classes, via the MRLC service.", "https://www.mrlc.gov/"),
        ("The city's census series, from its Wikipedia article's decennial table.", "https://en.wikipedia.org/"),
        ("Colleges and their founding years: the state's Wikipedia list, and each institution's own article.", "https://en.wikipedia.org/"),
        ("Highways: Natural Earth 10m roads; a route appears in the earliest year its Wikipedia infobox gives for that number.", "https://www.naturalearthdata.com/"),
        ("Migration waves: each wave's Wikipedia article; figures are the orders of magnitude those sources give.", "https://en.wikipedia.org/"),
        ("Flags: each era's Wikipedia article image, fetched at view time.", "https://en.wikipedia.org/"),
        ("Native Land Digital: the community map of Indigenous territories; the patches here are approximations, not their data.", "https://native-land.ca/"),
    ] + hist["refs"]
    return "\n".join(f'<p>{t}\n<a href="{u}">{u}</a></p>' for t, u in rows)


def main():
    pops = json.loads((DATA / "city_pop.json").read_text())
    unis_all = json.loads((DATA / "universities.json").read_text())
    sibs_all = [(f, n) for f, (n, _, _, _) in
                ((v[0], (v[1], 0, 0, 0)) for v in PAGES.values())]

    for key, (fname, title, up_href, up_name) in PAGES.items():
        data = json.loads((CITY / f"{key}.json").read_text())
        hist = dict(HIST[key])
        hist["census"] = pops[key]
        seat = SEAT[key]
        hist["events"] = [dict(e, pp=pops[key]) if e["n"] == seat else e
                          for e in hist["events"]]
        if not any(e.get("pp") for e in hist["events"]):
            raise SystemExit(f"{key}: no event named {seat!r}")

        # every college inside the view box, in the year it opened
        lo, la0, hi, la1 = data["ll"]
        unis = []
        mine = MINE.get(key)
        for u in sorted(unis_all.get(UNI_STATE[key], []),
                        key=lambda x: (x["y"], x["n"])):
            if not (lo <= u["lon"] <= hi and la0 <= u["lat"] <= la1):
                continue
            u = dict(u)
            if mine and u["n"] == mine[0]:
                u["mine"] = mine[1]
            unis.append(u)
        # one county can fill a city view, so its gold is lighter here
        data["homeFill"] = 0.07
        # a homeland can cover a whole city view, so it is lighter here
        data["natFill"] = 0.17
        data["migGap"] = 24
        hist["nations"] = [dict(n, poly=densify(n["poly"]))
                           for n in hist["nations"]]
        hist["unis"] = unis
        hist["cities"] = []

        roads_p = CITY / f"{key}_roads.json"
        roads = json.loads(roads_p.read_text()) if roads_p.exists() else []
        roads = [r for r in roads if r.get("y")]
        roads.sort(key=lambda r: (r["y"], r["n"]))

        sibs = (f' <a href="{up_href}">{up_name}</a>'
                + "".join(f' <a href="{f}">{n}</a>'
                          for f, n in sibs_all if f != fname))
        html = (HTML.replace("__TITLE__", title)
                .replace("&larr; Library &middot; USA",
                         "&larr; Library &middot; USA &middot; Cities")
                .replace("__SIBS__", sibs)
                .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2)
                .replace("__REFS__", refs_for(key, hist))
                .replace("__ST__", json.dumps(data, separators=(",", ":")))
                .replace("__HIST__", json.dumps(hist, separators=(",", ":")))
                .replace("__ROADS__", json.dumps(roads, separators=(",", ":"))))
        (ROOT / fname).write_text(html, encoding="utf-8")
        print(f"wrote {ROOT / fname} ({len(html):,} B): "
              f"{len(hist['nations'])} peoples, {len(hist['events'])} events, "
              f"{len(unis)} colleges, {len(roads)} routes")


if __name__ == "__main__":
    main()
