#!/usr/bin/env python3
"""Generate the six state pages: california, pennsylvania, massachusetts,
alabama, nebraska, minnesota (.html).

Each page draws the state in Web Mercator from tools/data/states/<st>.json
(build_states_data.py bakes counties with populations, rivers, lakes) with
five toggleable layers: terrain (AWS Terrain Tiles, shaded and tinted at
view time), woods (USGS NLCD 2021 land cover, forest classes only, fetched
from the MRLC WMS at view time), rivers, lakes, and counties (population
choropleth with hover cards). A playable timeline runs 1492 to the
present: the nations who lived there with population estimates, the
settlements and capitals as they are founded, the removals, and a flag
panel that shows the sovereign of the moment (Wikipedia flag images at
view time) until the official state flag.

Population figures are decennial census values interpolated between
decades; everything earlier, and all Native figures, are scholarly
estimates carried with their ranges. Sources sit on every card and in
the references.

Usage: python3 build_states.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = Path(__file__).parent / "data" / "states"

# flag: {"a": wikipedia article} or {"c": commons filename}; None = nations
US = {"a": "Flag of the United States"}

HIST = {}

HIST["ca"] = {
    "eras": [
        {"y0": 1492, "y1": 1769, "l": "Indigenous California, unceded", "f": None},
        {"y0": 1769, "y1": 1821, "l": "Spain (Alta California)", "f": {"a": "Cross of Burgundy"}},
        {"y0": 1821, "y1": 1848, "l": "Mexico (Alta California)", "f": {"a": "Flag of Mexico"}},
        {"y0": 1848, "y1": 1911, "l": "United States (statehood 1850)", "f": US},
        {"y0": 1911, "y1": 2026, "l": "State flag adopted 1911", "f": {"a": "Flag of California"}},
    ],
    "marks": [{"y": 1850, "l": "Statehood, 31st state"}],
    "border": 1850,
    "nb": [
        {"n": "Oregon", "lat": 42.18, "lon": -120.5},
        {"n": "Nevada", "lat": 39.2, "lon": -116.9},
        {"n": "Arizona", "lat": 34.3, "lon": -114.02, "v": True},
        {"n": "Baja California", "lat": 32.32, "lon": -115.9},
        {"n": "Pacific Ocean", "lat": 35.6, "lon": -123.4, "sea": True},
    ],
    "pre": "Pre-contact population of the California area: about 310,000 "
           "(Cook), with scholarly estimates from 133,000 (Kroeber) to "
           "well above 300,000.",
    "nations": [
        {"n": "Yurok", "src": "en.wikipedia.org/wiki/Yurok", "poly": [[-124.6, 41.0], [-123.7, 41.2], [-123.5, 41.6], [-124.1, 42.0], [-124.5, 41.7]], "lat": 41.3, "lon": -124.0, "note": "Lower Klamath River and the redwood coast."},
        {"n": "Pomo", "src": "en.wikipedia.org/wiki/Pomo", "poly": [[-123.9, 38.6], [-122.7, 38.8], [-122.5, 39.3], [-123.3, 39.6], [-124.0, 39.3]], "lat": 39.0, "lon": -123.1, "note": "Clear Lake and the Mendocino and Sonoma coast."},
        {"n": "Wintu", "src": "en.wikipedia.org/wiki/Wintu", "poly": [[-122.9, 40.0], [-121.9, 40.2], [-122.0, 41.1], [-122.9, 41.0]], "lat": 40.6, "lon": -122.4, "note": "Upper Sacramento Valley."},
        {"n": "Maidu", "src": "en.wikipedia.org/wiki/Maidu", "poly": [[-121.7, 39.0], [-120.5, 39.3], [-120.4, 40.3], [-121.5, 40.2]], "lat": 39.7, "lon": -121.2, "note": "Feather and American rivers, northern Sierra foothills."},
        {"n": "Miwok", "src": "en.wikipedia.org/wiki/Miwok", "poly": [[-121.6, 37.6], [-120.0, 37.7], [-119.8, 38.6], [-121.0, 38.7], [-121.7, 38.2]], "lat": 38.0, "lon": -120.4, "note": "Central Sierra foothills and the Delta."},
        {"n": "Ohlone", "src": "en.wikipedia.org/wiki/Ohlone", "poly": [[-122.6, 36.5], [-121.3, 36.7], [-121.5, 37.6], [-122.5, 37.8]], "lat": 37.0, "lon": -121.9, "note": "San Francisco Bay to Monterey."},
        {"n": "Yokuts", "src": "en.wikipedia.org/wiki/Yokuts", "poly": [[-121.0, 35.0], [-118.9, 35.2], [-119.3, 37.0], [-120.9, 37.3]], "lat": 36.5, "lon": -119.8, "note": "San Joaquin Valley."},
        {"n": "Chumash", "src": "en.wikipedia.org/wiki/Chumash_people", "poly": [[-120.7, 34.3], [-118.9, 33.9], [-118.9, 34.5], [-120.6, 34.9]], "lat": 34.45, "lon": -119.8, "note": "Santa Barbara Channel coast."},
        {"n": "Tongva", "src": "en.wikipedia.org/wiki/Tongva", "poly": [[-118.7, 33.6], [-117.6, 33.5], [-117.7, 34.2], [-118.6, 34.3]], "lat": 34.05, "lon": -118.2, "note": "Los Angeles Basin."},
        {"n": "Kumeyaay", "src": "en.wikipedia.org/wiki/Kumeyaay", "poly": [[-117.4, 32.5], [-116.0, 32.5], [-116.1, 33.2], [-117.3, 33.2]], "lat": 32.8, "lon": -116.8, "note": "San Diego country."},
        {"n": "Mojave", "src": "en.wikipedia.org/wiki/Mohave_people", "poly": [[-114.9, 34.0], [-114.1, 34.0], [-114.3, 35.3], [-115.0, 35.2]], "lat": 34.8, "lon": -114.6, "note": "Colorado River."},
    ],
    "events": [
        {"y": 1769, "t": "set", "n": "San Diego", "pp": [[1850, 650], [1900, 17700], [1930, 147995], [1960, 573224], [1990, 1110549], [2020, 1386932]], "lat": 32.72, "lon": -117.16, "note": "First presidio and mission.", "src": "en.wikipedia.org/wiki/History_of_San_Diego"},
        {"y": 1769, "t": "rem", "n": "The mission system", "lat": 35.4, "lon": -120.8, "note": "1769 to 1833: forced congregation and disease bring high mortality among coastal peoples.", "src": "en.wikipedia.org/wiki/Spanish_missions_in_California"},
        {"y": 1770, "t": "set", "n": "Monterey", "lat": 36.60, "lon": -121.89, "note": "Spanish and Mexican capital of Alta California.", "src": "en.wikipedia.org/wiki/Monterey,_California"},
        {"y": 1776, "t": "set", "n": "San Francisco", "pp": [[1852, 34776], [1870, 149473], [1900, 342782], [1950, 775357], [2020, 873965]], "lat": 37.77, "lon": -122.42, "note": "Presidio and Mission Dolores.", "src": "en.wikipedia.org/wiki/History_of_San_Francisco"},
        {"y": 1777, "t": "set", "n": "San Jose", "pp": [[1900, 21500], [1950, 95280], [1970, 445779], [2000, 894943], [2020, 1013240]], "lat": 37.34, "lon": -121.89, "note": "First civilian pueblo; first state capital in 1850.", "src": "en.wikipedia.org/wiki/San_Jose,_California"},
        {"y": 1781, "t": "set", "n": "Los Angeles", "pp": [[1850, 1610], [1880, 11183], [1900, 102479], [1930, 1238048], [1970, 2816061], [2020, 3898747]], "lat": 34.05, "lon": -118.24, "note": "Pueblo founded September 4, 1781.", "src": "en.wikipedia.org/wiki/History_of_Los_Angeles"},
        {"y": 1782, "t": "set", "n": "Santa Barbara", "lat": 34.42, "lon": -119.70, "note": "Presidio of 1782.", "src": "en.wikipedia.org/wiki/Santa_Barbara,_California"},
        {"y": 1823, "t": "set", "n": "Sonoma", "lat": 38.29, "lon": -122.46, "note": "The last and northernmost mission.", "src": "en.wikipedia.org/wiki/Sonoma,_California"},
        {"y": 1848, "t": "cap", "n": "Sacramento", "pp": [[1860, 13785], [1900, 29282], [1950, 137572], [2000, 407018], [2020, 524943]], "lat": 38.58, "lon": -121.49, "note": "Laid out in 1848 by Sutter's Fort; permanent state capital from 1854.", "src": "en.wikipedia.org/wiki/Sacramento,_California"},
        {"y": 1850, "t": "rem", "n": "Act for the Government and Protection of Indians", "lat": 38.9, "lon": -120.0, "note": "State law enabling forced labor and the seizure of Native children.", "src": "en.wikipedia.org/wiki/Act_for_the_Government_and_Protection_of_Indians"},
        {"y": 1850, "t": "rem", "n": "Bloody Island massacre", "lat": 39.05, "lon": -122.83, "note": "US cavalry kill Pomo people at Clear Lake, May 15, 1850.", "src": "en.wikipedia.org/wiki/Bloody_Island_massacre"},
        {"y": 1851, "t": "rem", "n": "Eighteen unratified treaties", "lat": 37.5, "lon": -119.2, "note": "1851 and 1852: treaties signed with California nations; the Senate ratifies none.", "src": "en.wikipedia.org/wiki/California_genocide"},
        {"y": 1852, "t": "set", "n": "Oakland", "pp": [[1870, 10500], [1900, 66960], [1930, 284063], [2020, 440646]], "lat": 37.80, "lon": -122.27, "note": "Incorporated 1852.", "src": "en.wikipedia.org/wiki/Oakland,_California"},
        {"y": 1856, "t": "rem", "n": "Round Valley", "lat": 39.80, "lon": -123.25, "note": "Reservation era begins amid massacres; Madley counts 9,500 to 16,000 Native people killed statewide, 1846 to 1873.", "src": "en.wikipedia.org/wiki/California_genocide"},
        {"y": 1872, "t": "set", "n": "Fresno", "pp": [[1900, 12470], [1950, 91669], [1980, 217129], [2020, 542107]], "lat": 36.74, "lon": -119.79, "note": "Central Pacific railroad town.", "src": "en.wikipedia.org/wiki/Fresno,_California"},
    ],
    "census": [[1850, 92597], [1860, 379994], [1870, 560247], [1880, 864694],
               [1890, 1213398], [1900, 1485053], [1910, 2377549], [1920, 3426861],
               [1930, 5677251], [1940, 6907387], [1950, 10586223], [1960, 15717204],
               [1970, 19953134], [1980, 23667902], [1990, 29760021], [2000, 33871648],
               [2010, 37253956], [2020, 39538223]],
    "native": [[1769, 310000, "Cook's estimate"], [1848, 150000, "Madley"],
               [1870, 30000, "Madley"], [1900, 16000, "Madley; other sources ~25,000"]],
    "geo": {"hp": {"n": "Mount Whitney", "el": "4,421 m", "lat": 36.58, "lon": -118.29}},
    "refs": [
        ["Population of Native California; the estimates of Cook, Kroeber and others.", "https://en.wikipedia.org/wiki/Population_of_Native_California"],
        ["Madley, B. (2016). An American Genocide: The United States and the California Indian Catastrophe. Yale University Press.", "https://en.wikipedia.org/wiki/California_genocide"],
    
        ["Nation homelands and histories: each nation's Wikipedia article (Yurok, Pomo, Wintu, Maidu, Miwok, Ohlone, Yokuts, Chumash, Tongva, Kumeyaay, Mojave).",
         "https://en.wikipedia.org/wiki/Category:Native_American_tribes_in_California"],],
}

HIST["pa"] = {
    "eras": [
        {"y0": 1492, "y1": 1638, "l": "Lenapehoking and the Susquehannock", "f": None},
        {"y0": 1638, "y1": 1655, "l": "New Sweden", "f": {"a": "Flag of Sweden"}},
        {"y0": 1655, "y1": 1664, "l": "New Netherland", "f": {"a": "Flag of the Netherlands"}},
        {"y0": 1664, "y1": 1707, "l": "England (Penn's charter 1681)", "f": {"a": "Flag of England"}},
        {"y0": 1707, "y1": 1776, "l": "Great Britain", "f": {"a": "Flag of Great Britain"}},
        {"y0": 1776, "y1": 1907, "l": "United States (2nd state, 1787)", "f": US},
        {"y0": 1907, "y1": 2026, "l": "State flag standardized 1907", "f": {"a": "Flag of Pennsylvania"}},
    ],
    "marks": [{"y": 1787, "l": "Statehood, 2nd state"}],
    "border": 1792,
    "nb": [
        {"n": "New York", "lat": 42.45, "lon": -76.6},
        {"n": "New Jersey", "lat": 40.55, "lon": -74.5, "v": True},
        {"n": "Delaware", "lat": 39.55, "lon": -75.55},
        {"n": "Maryland", "lat": 39.52, "lon": -77.3},
        {"n": "West Virginia", "lat": 39.52, "lon": -79.62},
        {"n": "Ohio", "lat": 41.0, "lon": -80.72, "v": True},
        {"n": "Lake Erie", "lat": 42.45, "lon": -80.15, "sea": True},
    ],
    "pre": "No single scholarly total exists for the Pennsylvania area: the "
           "Susquehannock are put at 5,000 to 8,000 around 1600, and all of "
           "Lenapehoking (Pennsylvania to New York) at 7,500 to 15,000.",
    "nations": [
        {"n": "Lenape", "src": "philadelphiaencyclopedia.org/essays/native-peoples-to-1680/", "poly": [[-75.9, 39.8], [-74.8, 40.0], [-75.0, 40.9], [-75.9, 40.6]], "lat": 40.2, "lon": -75.3, "note": "Delaware Valley; about 7,500 to 15,000 across Lenapehoking around 1600.", "after": {"y": 1737, "t": "dispossessed from 1737; diaspora west to Ohio, Kansas, Indian Territory"}},
        {"n": "Munsee", "src": "en.wikipedia.org/wiki/Munsee", "poly": [[-75.8, 40.8], [-74.8, 41.0], [-75.0, 41.9], [-75.9, 41.6]], "lat": 41.1, "lon": -75.1, "note": "Northern Lenape of the upper Delaware."},
        {"n": "Susquehannock", "src": "digitalprojects.scranton.edu/s/native-history-wyoming-valley/page/susquehannocks", "poly": [[-77.2, 39.8], [-76.0, 40.0], [-76.0, 41.4], [-77.1, 41.3]], "lat": 40.6, "lon": -76.6, "note": "Susquehanna Valley; 5,000 to 8,000 around 1600.", "after": {"y": 1763, "t": "last twenty murdered at Conestoga, 1763"}},
        {"n": "Erie", "src": "en.wikipedia.org/wiki/Erie_people", "poly": [[-80.6, 41.7], [-79.5, 41.8], [-79.6, 42.3], [-80.6, 42.4]], "lat": 42.0, "lon": -80.2, "note": "Lake Erie shore; dispersed in the 1650s wars."},
        {"n": "Monongahela", "src": "en.wikipedia.org/wiki/Monongahela_culture", "poly": [[-80.6, 39.7], [-79.2, 39.8], [-79.3, 40.4], [-80.5, 40.4]], "lat": 40.0, "lon": -79.9, "note": "Monongahela Valley; gone by the 1630s."},
        {"n": "Seneca", "src": "en.wikipedia.org/wiki/Seneca_people", "poly": [[-79.6, 41.4], [-77.6, 41.6], [-77.8, 42.1], [-79.7, 42.1]], "lat": 41.9, "lon": -78.7, "note": "Haudenosaunee of the northern tier."},
        {"n": "Shawnee", "src": "en.wikipedia.org/wiki/Shawnee", "poly": [[-77.8, 40.0], [-76.6, 40.2], [-76.8, 40.9], [-77.9, 40.7]], "lat": 40.3, "lon": -77.0, "note": "Arrived in the 1690s; Susquehanna and Ohio valleys."},
    ],
    "events": [
        {"y": 1643, "t": "set", "n": "Tinicum Island", "lat": 39.87, "lon": -75.29, "note": "The Printzhof, seat of New Sweden.", "src": "en.wikipedia.org/wiki/Printzhof"},
        {"y": 1682, "t": "set", "n": "Philadelphia", "pp": [[1790, 28522], [1850, 121376], [1890, 1046964], [1950, 2071605], [2020, 1603797]], "lat": 39.95, "lon": -75.16, "note": "Founded by William Penn.", "src": "en.wikipedia.org/wiki/Philadelphia"},
        {"y": 1734, "t": "set", "n": "Lancaster", "lat": 40.04, "lon": -76.31, "note": "State capital 1799 to 1812.", "src": "en.wikipedia.org/wiki/Lancaster,_Pennsylvania"},
        {"y": 1737, "t": "rem", "n": "Walking Purchase", "lat": 40.9, "lon": -75.2, "note": "Penn's heirs take about 1.2 million acres of Lenape land by a rigged walk.", "src": "en.wikipedia.org/wiki/Walking_Purchase"},
        {"y": 1741, "t": "set", "n": "Bethlehem", "lat": 40.62, "lon": -75.37, "note": "Moravian settlement.", "src": "en.wikipedia.org/wiki/Bethlehem,_Pennsylvania"},
        {"y": 1748, "t": "set", "n": "Reading", "pp": [[1870, 33930], [1900, 78961], [1930, 111171], [2020, 95112]], "lat": 40.34, "lon": -75.93, "note": "", "src": "en.wikipedia.org/wiki/Reading,_Pennsylvania"},
        {"y": 1758, "t": "set", "n": "Pittsburgh", "pp": [[1850, 46601], [1880, 156389], [1910, 533905], [1950, 676806], [2020, 302971]], "lat": 40.44, "lon": -80.00, "note": "The Forks of the Ohio, named after Fort Duquesne fell.", "src": "en.wikipedia.org/wiki/History_of_Pittsburgh"},
        {"y": 1758, "t": "rem", "n": "Treaty of Easton", "lat": 40.69, "lon": -75.22, "note": "Ohio-country nations leave the French alliance on western-land promises.", "src": "en.wikipedia.org/wiki/Treaty_of_Easton"},
        {"y": 1763, "t": "rem", "n": "Conestoga massacre", "lat": 40.05, "lon": -76.28, "note": "The Paxton Boys murder the last twenty Conestoga Susquehannock.", "src": "en.wikipedia.org/wiki/Paxton_Boys"},
        {"y": 1768, "t": "rem", "n": "Fort Stanwix cession", "lat": 41.5, "lon": -78.0, "note": "Iroquois cede trans-Allegheny Pennsylvania without the resident nations' consent.", "src": "en.wikipedia.org/wiki/Treaty_of_Fort_Stanwix_(1768)"},
        {"y": 1785, "t": "cap", "n": "Harrisburg", "pp": [[1860, 13405], [1900, 50167], [1950, 89544], [2020, 50099]], "lat": 40.26, "lon": -76.88, "note": "Laid out 1785; state capital from 1812.", "src": "en.wikipedia.org/wiki/Harrisburg,_Pennsylvania"},
        {"y": 1795, "t": "set", "n": "Erie", "pp": [[1900, 52733], [1960, 138440], [2020, 94831]], "lat": 42.13, "lon": -80.09, "note": "", "src": "en.wikipedia.org/wiki/Erie,_Pennsylvania"},
        {"y": 1856, "t": "set", "n": "Scranton", "pp": [[1880, 45850], [1900, 102026], [1930, 143433], [2020, 76328]], "lat": 41.41, "lon": -75.66, "note": "Borough 1856, city 1866.", "src": "en.wikipedia.org/wiki/Scranton,_Pennsylvania"},
    ],
    "census": [[1790, 434373], [1800, 602365], [1810, 810091], [1820, 1049458],
               [1830, 1348233], [1840, 1724033], [1850, 2311786], [1860, 2906215],
               [1870, 3521951], [1880, 4282891], [1890, 5258014], [1900, 6302115],
               [1910, 7665111], [1920, 8720017], [1930, 9631350], [1940, 9900180],
               [1950, 10498012], [1960, 11319366], [1970, 11793909], [1980, 11863895],
               [1990, 11881643], [2000, 12281054], [2010, 12702379], [2020, 13002700]],
    "colonial": [[1700, 17950], [1750, 119666], [1780, 327305]],
    "native": [[1600, 13000, "Lenape and Susquehannock combined, low bound"],
               [1670, 8000, "after the 1650s wars"],
               [1763, 20, "Conestoga, the last Susquehannock community"]],
    "geo": {"hp": {"n": "Mount Davis", "el": "979 m", "lat": 39.79, "lon": -79.18}},
    "refs": [
        ["Native peoples to 1680, Encyclopedia of Greater Philadelphia.", "https://philadelphiaencyclopedia.org/essays/native-peoples-to-1680/"],
        ["The Susquehannock, University of Scranton digital history.", "https://digitalprojects.scranton.edu/s/native-history-wyoming-valley/page/susquehannocks"],
    
        ["Nation homelands: the Encyclopedia of Greater Philadelphia, the University of Scranton's Susquehannock project, and each nation's Wikipedia article.",
         "https://en.wikipedia.org/wiki/Category:Native_American_tribes_in_Pennsylvania"],],
}

HIST["ma"] = {
    "eras": [
        {"y0": 1492, "y1": 1620, "l": "The Dawnland: Wampanoag, Massachusett and their neighbors", "f": None},
        {"y0": 1620, "y1": 1707, "l": "England (Plymouth 1620, Massachusetts Bay 1630)", "f": {"a": "Flag of England"}},
        {"y0": 1707, "y1": 1776, "l": "Great Britain", "f": {"a": "Flag of Great Britain"}},
        {"y0": 1776, "y1": 1908, "l": "United States (6th state, 1788)", "f": US},
        {"y0": 1908, "y1": 2026, "l": "State flag adopted 1908", "f": {"a": "Flag of Massachusetts"}},
    ],
    "marks": [{"y": 1788, "l": "Statehood, 6th state"}],
    "border": 1820,
    "nb": [
        {"n": "Vermont", "lat": 43.05, "lon": -72.9},
        {"n": "New Hampshire", "lat": 43.05, "lon": -71.4},
        {"n": "New York", "lat": 42.2, "lon": -73.68, "v": True},
        {"n": "Connecticut", "lat": 41.75, "lon": -72.7},
        {"n": "Rhode Island", "lat": 41.62, "lon": -71.5},
        {"n": "Atlantic Ocean", "lat": 41.15, "lon": -69.95, "sea": True},
    ],
    "pre": "Around 1600 New England held on the order of 100,000 Native "
           "people; the Wampanoag alone are put as high as 40,000 before "
           "the epidemics, with older tribal estimates far lower.",
    "nations": [
        {"n": "Massachusett", "src": "en.wikipedia.org/wiki/Massachusett", "poly": [[-71.4, 42.0], [-70.7, 42.1], [-70.8, 42.7], [-71.4, 42.6]], "lat": 42.30, "lon": -71.05, "note": "Massachusetts Bay coast.", "after": {"y": 1616, "t": "the 1616-19 epidemic kills a third to nine tenths of the coastal people"}},
        {"n": "Wampanoag", "src": "en.wikipedia.org/wiki/Wampanoag", "poly": [[-71.3, 41.5], [-70.5, 41.6], [-70.7, 42.1], [-71.3, 42.0]], "lat": 41.80, "lon": -70.95, "note": "Southeast Massachusetts; as many as 40,000 across 67 villages before the epidemics.", "after": {"y": 1676, "t": "left effectively landless after King Philip's War; the nation remains, at Mashpee and Aquinnah"}},
        {"n": "Nauset", "src": "historyofmassachusetts.org/native-american-tribes/", "poly": [[-70.3, 41.6], [-69.9, 41.7], [-70.0, 42.1], [-70.4, 41.9]], "lat": 41.80, "lon": -69.98, "note": "Outer Cape Cod."},
        {"n": "Nipmuc", "src": "historyofmassachusetts.org/native-american-tribes/", "poly": [[-72.3, 42.0], [-71.5, 42.0], [-71.6, 42.7], [-72.3, 42.6]], "lat": 42.15, "lon": -71.90, "note": "Central uplands and lakes."},
        {"n": "Pocumtuck", "src": "historyofmassachusetts.org/native-american-tribes/", "poly": [[-72.8, 42.1], [-72.3, 42.1], [-72.4, 42.75], [-72.8, 42.7]], "lat": 42.54, "lon": -72.60, "note": "Middle Connecticut Valley."},
        {"n": "Mahican", "src": "en.wikipedia.org/wiki/Mohicans", "poly": [[-73.5, 42.05], [-72.9, 42.1], [-73.0, 42.75], [-73.5, 42.7]], "lat": 42.40, "lon": -73.25, "note": "Berkshires and Housatonic Valley."},
        {"n": "Pennacook", "src": "en.wikipedia.org/wiki/Pennacook", "poly": [[-71.6, 42.5], [-70.9, 42.6], [-71.1, 42.87], [-71.6, 42.8]], "lat": 42.70, "lon": -71.20, "note": "Merrimack Valley."},
    ],
    "events": [
        {"y": 1616, "t": "rem", "n": "The Great Dying", "lat": 42.2, "lon": -70.8, "note": "1616 to 1619: epidemic kills between a third and nine tenths of coastal Native New England.", "src": "en.wikipedia.org/wiki/Massachusett"},
        {"y": 1620, "t": "set", "n": "Plymouth", "pp": [[1900, 9592], [2020, 61217]], "lat": 41.96, "lon": -70.67, "note": "The Mayflower colony, on the emptied village of Patuxet.", "src": "en.wikipedia.org/wiki/Plymouth,_Massachusetts"},
        {"y": 1626, "t": "set", "n": "Salem", "pp": [[1850, 20264], [1900, 35956], [2020, 44480]], "lat": 42.52, "lon": -70.90, "note": "Naumkeag.", "src": "en.wikipedia.org/wiki/Salem,_Massachusetts"},
        {"y": 1630, "t": "cap", "n": "Boston", "pp": [[1790, 18320], [1850, 136881], [1900, 560892], [1950, 801444], [2020, 675647]], "lat": 42.36, "lon": -71.06, "note": "The Winthrop fleet; capital ever since.", "src": "en.wikipedia.org/wiki/Boston"},
        {"y": 1636, "t": "set", "n": "Springfield", "pp": [[1850, 11766], [1900, 62059], [1930, 149900], [2020, 155929]], "lat": 42.10, "lon": -72.59, "note": "Pynchon's Connecticut Valley trading post.", "src": "en.wikipedia.org/wiki/Springfield,_Massachusetts"},
        {"y": 1651, "t": "rem", "n": "Praying towns", "lat": 42.28, "lon": -71.35, "note": "Eliot's Christian Indian towns, Natick first.", "src": "en.wikipedia.org/wiki/Praying_town"},
        {"y": 1673, "t": "set", "n": "Deerfield", "lat": 42.54, "lon": -72.61, "note": "Frontier town on Pocumtuck land.", "src": "en.wikipedia.org/wiki/Deerfield,_Massachusetts"},
        {"y": 1675, "t": "rem", "n": "King Philip's War", "lat": 41.9, "lon": -71.0, "note": "1675 to 1678: some 5,000 Native dead; captives sold into Caribbean slavery; a thousand interned on Deer Island.", "src": "en.wikipedia.org/wiki/King_Philip%27s_War"},
        {"y": 1722, "t": "set", "n": "Worcester", "pp": [[1850, 17049], [1900, 118421], [1950, 203486], [2020, 206518]], "lat": 42.26, "lon": -71.80, "note": "Town incorporated 1722.", "src": "en.wikipedia.org/wiki/Worcester,_Massachusetts"},
        {"y": 1787, "t": "set", "n": "New Bedford", "pp": [[1850, 16443], [1900, 62442], [1920, 121217], [2020, 101079]], "lat": 41.64, "lon": -70.93, "note": "Whaling port.", "src": "en.wikipedia.org/wiki/New_Bedford,_Massachusetts"},
        {"y": 1826, "t": "set", "n": "Lowell", "pp": [[1840, 20796], [1900, 94969], [1920, 112759], [2020, 115554]], "lat": 42.63, "lon": -71.31, "note": "Planned textile mill town.", "src": "en.wikipedia.org/wiki/Lowell,_Massachusetts"},
    ],
    "census": [[1790, 378787], [1800, 422845], [1810, 472040], [1820, 523287],
               [1830, 610408], [1840, 737699], [1850, 994514], [1860, 1231066],
               [1870, 1457351], [1880, 1783085], [1890, 2238943], [1900, 2805346],
               [1910, 3366416], [1920, 3852356], [1930, 4249614], [1940, 4316721],
               [1950, 4690514], [1960, 5148578], [1970, 5689170], [1980, 5737037],
               [1990, 6016425], [2000, 6349097], [2010, 6547629], [2020, 7029917]],
    "colonial": [[1700, 55941], [1750, 188000], [1780, 268627]],
    "native": [[1600, 100000, "New England-wide"], [1620, 30000, "after the Great Dying, order of magnitude"],
               [1680, 10000, "after King Philip's War, order of magnitude"]],
    "geo": {"hp": {"n": "Mount Greylock", "el": "1,064 m", "lat": 42.64, "lon": -73.17}},
    "refs": [
        ["Bragdon, K. (1996). Native People of Southern New England, 1500-1650. University of Oklahoma Press.", "https://www.oupress.com/9780806131269/native-people-of-southern-new-england-15001650/"],
        ["Snow, D., & Lanphear, K. (1988). European contact and Indian depopulation in the Northeast. Ethnohistory 35(1).", "https://www.jstor.org/stable/482431"],
    
        ["Nation homelands: History of Massachusetts Blog's tribes survey and each nation's Wikipedia article.",
         "https://historyofmassachusetts.org/native-american-tribes/"],],
}

HIST["al"] = {
    "eras": [
        {"y0": 1492, "y1": 1702, "l": "Muscogee, Cherokee, Choctaw and Chickasaw homelands", "f": None},
        {"y0": 1702, "y1": 1763, "l": "French Louisiane (Mobile, 1702)", "f": {"a": "Flag of the Kingdom of France"}},
        {"y0": 1763, "y1": 1783, "l": "British West Florida; the interior stays Creek", "f": {"a": "Flag of Great Britain"}},
        {"y0": 1783, "y1": 1813, "l": "Spanish coast, Native interior, US territory from 1798", "f": {"a": "Cross of Burgundy"}},
        {"y0": 1813, "y1": 1819, "l": "United States (Alabama Territory 1817)", "f": US},
        {"y0": 1819, "y1": 1895, "l": "State of Alabama, 1819", "f": US},
        {"y0": 1895, "y1": 2026, "l": "State flag adopted 1895", "f": {"a": "Flag of Alabama"}},
    ],
    "border": 1819,
    "nb": [
        {"n": "Tennessee", "lat": 35.25, "lon": -86.7},
        {"n": "Georgia", "lat": 33.2, "lon": -84.75},
        {"n": "Florida", "lat": 30.55, "lon": -85.9},
        {"n": "Mississippi", "lat": 32.6, "lon": -88.62, "v": True},
        {"n": "Gulf of Mexico", "lat": 30.02, "lon": -87.9, "sea": True},
    ],
    "pre": "The Mississippian center at Moundville held 1,000 to 3,000 "
           "people with some 10,000 in its valley around 1300. At removal "
           "the four nations counted together over 60,000 people across "
           "their wider homelands.",
    "nations": [
        {"n": "Muscogee (Creek)", "src": "encyclopediaofalabama.org/article/creeks-in-alabama/", "poly": [[-86.8, 31.8], [-85.1, 32.0], [-85.3, 33.7], [-86.6, 33.5]], "lat": 32.6, "lon": -85.8, "note": "East-central Alabama, the Coosa, Tallapoosa and Alabama valleys.", "after": {"y": 1836, "t": "about 23,000 removed to Indian Territory, 1836-37"}},
        {"n": "Cherokee", "src": "encyclopediaofalabama.org/article/cherokees-in-alabama/", "poly": [[-86.6, 33.8], [-85.3, 33.9], [-85.4, 35.0], [-86.5, 34.9]], "lat": 34.5, "lon": -85.8, "note": "Northeast Alabama.", "after": {"y": 1838, "t": "Trail of Tears, 1838; 4,000 to 8,000 died"}},
        {"n": "Choctaw", "src": "encyclopediaofalabama.org/article/choctaws-in-alabama/", "poly": [[-88.5, 31.0], [-87.4, 31.2], [-87.6, 32.8], [-88.4, 32.7]], "lat": 31.9, "lon": -88.2, "note": "Southwest Alabama, Tombigbee basin.", "after": {"y": 1831, "t": "removed 1831-33 under Dancing Rabbit Creek"}},
        {"n": "Chickasaw", "src": "encyclopediaofalabama.org/article/chickasaws-in-alabama/", "poly": [[-88.2, 33.9], [-87.0, 34.0], [-87.2, 35.0], [-88.2, 34.95]], "lat": 34.7, "lon": -88.0, "note": "Northwest Alabama.", "after": {"y": 1837, "t": "removed 1837"}},
        {"n": "Alabama-Coushatta", "src": "encyclopediaofalabama.org/article/alabama-coushattas-in-alabama/", "poly": [[-87.0, 32.0], [-86.2, 32.1], [-86.3, 32.9], [-87.0, 32.8]], "lat": 32.5, "lon": -86.4, "note": "Upper Alabama River."},
        {"n": "Moundville", "src": "en.wikipedia.org/wiki/Moundville_Archaeological_Site", "poly": [[-87.8, 32.85], [-87.4, 32.85], [-87.45, 33.15], [-87.8, 33.1]], "lat": 33.0, "lon": -87.63, "note": "Mississippian mound center, about 1000 to 1450 CE."},
    ],
    "events": [
        {"y": 1540, "t": "rem", "n": "Mabila", "lat": 32.2, "lon": -87.5, "note": "De Soto's entrada fights Tuskaloosa's people; the site is still unknown.", "src": "en.wikipedia.org/wiki/Mabila"},
        {"y": 1702, "t": "set", "n": "Mobile", "pp": [[1830, 3194], [1860, 29258], [1900, 38469], [1960, 202779], [2020, 187041]], "lat": 30.69, "lon": -88.04, "note": "French capital of Louisiane, 1702 to 1711.", "src": "en.wikipedia.org/wiki/Mobile,_Alabama"},
        {"y": 1717, "t": "set", "n": "Fort Toulouse", "lat": 32.50, "lon": -86.25, "note": "French post trading with the Creeks.", "src": "en.wikipedia.org/wiki/Fort_Toulouse"},
        {"y": 1805, "t": "set", "n": "Huntsville", "pp": [[1900, 8068], [1950, 16437], [1970, 139282], [2020, 215006]], "lat": 34.73, "lon": -86.59, "note": "Site of the 1819 constitutional convention.", "src": "en.wikipedia.org/wiki/Huntsville,_Alabama"},
        {"y": 1814, "t": "rem", "n": "Horseshoe Bend and Fort Jackson", "lat": 32.97, "lon": -85.74, "note": "About 800 Red Sticks killed; the Creek Nation forced to cede 23 million acres.", "src": "en.wikipedia.org/wiki/Treaty_of_Fort_Jackson"},
        {"y": 1817, "t": "set", "n": "St. Stephens", "lat": 31.56, "lon": -88.04, "note": "The only territorial capital.", "src": "en.wikipedia.org/wiki/Alabama_Territory"},
        {"y": 1819, "t": "set", "n": "Tuscaloosa", "pp": [[1900, 5094], [1970, 65773], [2020, 99600]], "lat": 33.21, "lon": -87.57, "note": "Capital 1826 to 1846.", "src": "en.wikipedia.org/wiki/Tuscaloosa,_Alabama"},
        {"y": 1820, "t": "set", "n": "Cahawba", "lat": 32.32, "lon": -87.10, "note": "First permanent capital, 1820 to 1826, lost to floods.", "src": "en.wikipedia.org/wiki/Cahaba,_Alabama"},
        {"y": 1830, "t": "rem", "n": "Indian Removal Act; Dancing Rabbit Creek", "lat": 32.2, "lon": -88.0, "note": "Choctaw removal follows, 1831-33: about 15,000 removed, thousands died.", "src": "en.wikipedia.org/wiki/Trail_of_Tears"},
        {"y": 1832, "t": "rem", "n": "Treaty of Cusseta", "lat": 32.5, "lon": -85.5, "note": "Creeks cede all land east of the Mississippi; the allotments are swindled away.", "src": "en.wikipedia.org/wiki/Treaty_of_Cusseta"},
        {"y": 1836, "t": "rem", "n": "Creek removal", "lat": 32.6, "lon": -85.8, "note": "About 23,000 Creeks removed by 1837; thousands died.", "src": "encyclopediaofalabama.org/article/creek-indian-removal/"},
        {"y": 1838, "t": "rem", "n": "Trail of Tears", "lat": 34.6, "lon": -86.0, "note": "Cherokee removal through northeast Alabama.", "src": "en.wikipedia.org/wiki/Trail_of_Tears"},
        {"y": 1846, "t": "cap", "n": "Montgomery", "pp": [[1860, 8843], [1900, 30346], [1970, 133386], [2020, 200603]], "lat": 32.38, "lon": -86.31, "note": "Capital from 1846.", "src": "en.wikipedia.org/wiki/Montgomery,_Alabama"},
        {"y": 1871, "t": "set", "n": "Birmingham", "pp": [[1880, 3086], [1900, 38415], [1930, 259678], [2020, 200733]], "lat": 33.52, "lon": -86.81, "note": "Planned rail and iron city.", "src": "en.wikipedia.org/wiki/Birmingham,_Alabama"},
    ],
    "census": [[1800, 1250], [1810, 9046], [1820, 127901], [1830, 309527],
               [1840, 590756], [1850, 771623], [1860, 964201], [1870, 996992],
               [1880, 1262505], [1890, 1513401], [1900, 1828697], [1910, 2138093],
               [1920, 2348174], [1930, 2646248], [1940, 2832961], [1950, 3061743],
               [1960, 3266740], [1970, 3444165], [1980, 3893888], [1990, 4040587],
               [2000, 4447100], [2010, 4779736], [2020, 5024279]],
    "native": [[1830, 60000, "the four nations across their homelands, at removal"],
               [1840, 5000, "remaining after the removals, order of magnitude"]],
    "geo": {"hp": {"n": "Cheaha Mountain", "el": "735 m", "lat": 33.49, "lon": -85.81}},
    "refs": [
        ["Trail of Tears: removal counts and mortality ranges by nation.", "https://en.wikipedia.org/wiki/Trail_of_Tears"],
        ["Encyclopedia of Alabama: Creek removal; forest regions.", "https://encyclopediaofalabama.org/article/creek-indian-removal/"],
    
        ["Nation homelands: the Encyclopedia of Alabama's articles on the Creeks, Cherokees, Choctaws, Chickasaws and Alabama-Coushattas.",
         "https://encyclopediaofalabama.org/"],],
}

HIST["ne"] = {
    "eras": [
        {"y0": 1492, "y1": 1682, "l": "Pawnee, Omaha, Ponca, Otoe-Missouria and Lakota lands", "f": None},
        {"y0": 1682, "y1": 1762, "l": "France (La Salle's claim, 1682)", "f": {"a": "Flag of the Kingdom of France"}},
        {"y0": 1762, "y1": 1800, "l": "Spain (Treaty of Fontainebleau)", "f": {"a": "Cross of Burgundy"}},
        {"y0": 1800, "y1": 1803, "l": "France again (San Ildefonso)", "f": {"a": "Flag of France"}},
        {"y0": 1803, "y1": 1867, "l": "United States (Louisiana Purchase; Territory 1854)", "f": US},
        {"y0": 1867, "y1": 1925, "l": "State of Nebraska, 1867", "f": US},
        {"y0": 1925, "y1": 2026, "l": "State banner 1925, official flag 1963", "f": {"a": "Flag of Nebraska"}},
    ],
    "border": 1867,
    "nb": [
        {"n": "South Dakota", "lat": 43.18, "lon": -100.0},
        {"n": "Iowa", "lat": 41.9, "lon": -95.45},
        {"n": "Missouri", "lat": 40.05, "lon": -95.12, "v": True},
        {"n": "Kansas", "lat": 39.8, "lon": -98.5},
        {"n": "Colorado", "lat": 40.55, "lon": -103.3},
        {"n": "Wyoming", "lat": 42.1, "lon": -104.24, "v": True},
    ],
    "pre": "Around 1800 the Pawnee alone counted roughly 10,000 to 20,000 "
           "people, the Omaha about 4,000 before the 1800 smallpox, the "
           "Ponca and Otoe-Missouria in the hundreds each.",
    "nations": [
        {"n": "Pawnee", "src": "en.wikipedia.org/wiki/Pawnee_people", "poly": [[-100.3, 40.4], [-97.5, 40.7], [-97.8, 41.9], [-100.2, 41.7]], "lat": 41.3, "lon": -98.5, "note": "Loup, Republican and Platte valleys; roughly 12,000 around 1800, 633 by 1900.", "after": {"y": 1874, "t": "removed to Indian Territory, 1873-75"}},
        {"n": "Omaha", "src": "en.wikipedia.org/wiki/Omaha_people", "poly": [[-97.2, 41.6], [-95.9, 41.8], [-96.2, 42.9], [-97.4, 42.7]], "lat": 42.2, "lon": -96.5, "note": "Missouri River; about 4,000 in 1700.", "after": {"y": 1854, "t": "ceded east-central Nebraska, 1854; the nation keeps its reservation"}},
        {"n": "Ponca", "src": "en.wikipedia.org/wiki/Ponca", "poly": [[-98.9, 42.4], [-97.8, 42.5], [-98.0, 43.0], [-98.9, 42.95]], "lat": 42.7, "lon": -98.2, "note": "Mouth of the Niobrara.", "after": {"y": 1877, "t": "forced to Indian Territory; a third died by 1878"}},
        {"n": "Otoe-Missouria", "src": "en.wikipedia.org/wiki/Otoe-Missouria_Tribe_of_Indians", "poly": [[-97.0, 40.0], [-95.4, 40.1], [-95.7, 41.2], [-97.0, 41.0]], "lat": 40.4, "lon": -96.2, "note": "Lower Platte.", "after": {"y": 1881, "t": "moved to Indian Territory, 1881"}},
        {"n": "Lakota", "src": "en.wikipedia.org/wiki/Nebraska", "poly": [[-104.05, 42.2], [-101.5, 42.4], [-101.8, 43.0], [-104.05, 43.0]], "lat": 42.8, "lon": -103.0, "note": "Panhandle and northern plains."},
        {"n": "Cheyenne and Arapaho", "src": "en.wikipedia.org/wiki/Treaty_of_Fort_Laramie_(1868)", "poly": [[-104.05, 40.99], [-101.7, 41.1], [-102.0, 42.2], [-104.05, 42.1]], "lat": 41.3, "lon": -102.8, "note": "Western plains, per the 1851 Fort Laramie lines."},
    ],
    "events": [
        {"y": 1822, "t": "set", "n": "Bellevue", "pp": [[1950, 3858], [2020, 64176]], "lat": 41.15, "lon": -95.92, "note": "Fur post from about 1822; the oldest continuous town.", "src": "history.nebraska.gov/bellevue-the-first-twenty-years/"},
        {"y": 1848, "t": "set", "n": "Fort Kearny", "lat": 40.64, "lon": -99.00, "note": "Anchor of the Platte River Road.", "src": "en.wikipedia.org/wiki/Fort_Kearny"},
        {"y": 1851, "t": "rem", "n": "Fort Laramie treaty lines", "lat": 42.2, "lon": -103.5, "note": "1851 defines tribal territories; violated almost immediately. The 1868 treaty follows, then the Black Hills seizure of 1877.", "src": "en.wikipedia.org/wiki/Treaty_of_Fort_Laramie_(1868)"},
        {"y": 1854, "t": "set", "n": "Omaha", "pp": [[1860, 1883], [1870, 16083], [1890, 140452], [1950, 251117], [2020, 486051]], "lat": 41.26, "lon": -95.94, "note": "Territorial capital 1854 to 1867, founded on the Omaha cession of the same year.", "src": "en.wikipedia.org/wiki/Omaha,_Nebraska"},
        {"y": 1854, "t": "rem", "n": "The 1854 cessions", "lat": 41.5, "lon": -96.5, "note": "Omaha and Otoe-Missouria treaties open eastern Nebraska; annuities cut from 1.2 million to 84 thousand dollars.", "src": "en.wikipedia.org/wiki/Omaha_people"},
        {"y": 1856, "t": "set", "n": "Nebraska City", "pp": [[1900, 7380], [2020, 7222]], "lat": 40.68, "lon": -95.86, "note": "First incorporated town, 1855.", "src": "en.wikipedia.org/wiki/Nebraska_City,_Nebraska"},
        {"y": 1857, "t": "set", "n": "Grand Island", "pp": [[1900, 7554], [1960, 25742], [2020, 53131]], "lat": 40.92, "lon": -98.34, "note": "German settlers of 1857.", "src": "en.wikipedia.org/wiki/Grand_Island,_Nebraska"},
        {"y": 1866, "t": "set", "n": "North Platte", "pp": [[1900, 3640], [2020, 23390]], "lat": 41.12, "lon": -100.77, "note": "Union Pacific railhead, 1866.", "src": "en.wikipedia.org/wiki/North_Platte,_Nebraska"},
        {"y": 1867, "t": "cap", "n": "Lincoln", "pp": [[1870, 2441], [1890, 55154], [1950, 98884], [2020, 291082]], "lat": 40.81, "lon": -96.70, "note": "Lancaster of 1856, renamed and made capital at statehood, 1867.", "src": "en.wikipedia.org/wiki/Lincoln,_Nebraska"},
        {"y": 1873, "t": "rem", "n": "Massacre Canyon and Pawnee removal", "lat": 40.13, "lon": -101.0, "note": "After the 1873 attack most Pawnee moved to Indian Territory by 1875.", "src": "en.wikipedia.org/wiki/Pawnee_people"},
        {"y": 1877, "t": "rem", "n": "Ponca removal", "lat": 42.7, "lon": -98.2, "note": "Forced march to Indian Territory; about a third died by spring 1878.", "src": "en.wikipedia.org/wiki/Standing_Bear"},
        {"y": 1879, "t": "rem", "n": "Standing Bear v. Crook", "lat": 41.26, "lon": -95.94, "note": "A federal judge in Omaha rules that an Indian is a person under the law.", "src": "en.wikipedia.org/wiki/Standing_Bear"},
    ],
    "census": [[1860, 28841], [1870, 122993], [1880, 452402], [1890, 1062656],
               [1900, 1066300], [1910, 1192214], [1920, 1296372], [1930, 1377963],
               [1940, 1315834], [1950, 1325510], [1960, 1411330], [1970, 1483493],
               [1980, 1569825], [1990, 1578385], [2000, 1711263], [2010, 1826341],
               [2020, 1961504]],
    "native": [[1800, 17000, "Pawnee, Omaha, Ponca, Otoe-Missouria combined, rough"],
               [1900, 1700, "after removals and epidemics, order of magnitude"]],
    "geo": {"hp": {"n": "Panorama Point", "el": "1,653 m", "lat": 41.00, "lon": -104.03}},
    "refs": [
        ["Pawnee people: population and removal.", "https://en.wikipedia.org/wiki/Pawnee_people"],
        ["Standing Bear and the Ponca removal.", "https://en.wikipedia.org/wiki/Standing_Bear"],
    
        ["Nation homelands and populations: each nation's Wikipedia article (Pawnee, Omaha, Ponca, Otoe-Missouria) and the Fort Laramie treaty lines.",
         "https://en.wikipedia.org/wiki/Pawnee_people"],],
}

HIST["mn"] = {
    "eras": [
        {"y0": 1492, "y1": 1671, "l": "Dakota homelands; Ojibwe arriving from the east by the 1700s", "f": None},
        {"y0": 1671, "y1": 1763, "l": "France (claims of 1671 and 1679)", "f": {"a": "Flag of the Kingdom of France"}},
        {"y0": 1763, "y1": 1783, "l": "Britain east of the Mississippi, Spain west", "f": {"a": "Flag of Great Britain"}},
        {"y0": 1783, "y1": 1858, "l": "United States (east 1783, west 1803, north 1818; Territory 1849)", "f": US},
        {"y0": 1858, "y1": 1957, "l": "State of Minnesota, 1858", "f": US},
        {"y0": 1957, "y1": 2024, "l": "State flag of 1957, revised 1983", "f": {"c": "Flag of Minnesota (1957-1983).svg"}},
        {"y0": 2024, "y1": 2026, "l": "New state flag adopted May 11, 2024", "f": {"a": "Flag of Minnesota"}},
    ],
    "border": 1858,
    "nb": [
        {"n": "Canada", "lat": 49.55, "lon": -95.3},
        {"n": "North Dakota", "lat": 47.5, "lon": -97.42, "v": True},
        {"n": "South Dakota", "lat": 44.6, "lon": -96.98},
        {"n": "Iowa", "lat": 43.32, "lon": -94.3},
        {"n": "Wisconsin", "lat": 44.9, "lon": -91.2},
        {"n": "Lake Superior", "lat": 47.6, "lon": -90.2, "sea": True},
    ],
    "pre": "The eastern Dakota alone counted more than 7,000 people in "
           "1862; no reliable statewide early figure exists, and the "
           "Ojibwe expansion from the east through the 1700s reshaped the "
           "north before any census.",
    "nations": [
        {"n": "Dakota", "src": "en.wikipedia.org/wiki/Fort_Snelling", "poly": [[-96.5, 43.5], [-92.9, 43.6], [-93.3, 45.6], [-96.3, 45.4]], "lat": 44.6, "lon": -94.3, "note": "Minnesota River valley, Mille Lacs origin country, and Bdote, the sacred confluence.", "after": {"y": 1863, "t": "exiled from Minnesota by the Act of 1863 after the US-Dakota War"}},
        {"n": "Ojibwe", "src": "mnhs.org/fortsnelling/learn/native-americans/ojibwe-people", "poly": [[-96.3, 46.3], [-90.2, 46.6], [-91.0, 48.7], [-96.2, 48.9]], "lat": 47.4, "lon": -93.5, "note": "Arrived from Lake Superior in the early 1700s; the northern lake country. The bands remain on seven reservations today."},
        {"n": "Ioway", "src": "mnhs.org/usdakotawar/glossary/iowa", "poly": [[-94.3, 43.5], [-92.3, 43.5], [-92.6, 44.3], [-94.3, 44.1]], "lat": 43.9, "lon": -93.8, "note": "Southern Minnesota, earlier era."},
        {"n": "Cheyenne", "src": "accessgenealogy.com/minnesota/minnesota-indian-tribes.htm", "poly": [[-96.8, 44.8], [-95.6, 44.9], [-95.9, 46.0], [-96.8, 45.9]], "lat": 45.3, "lon": -96.0, "note": "Western Minnesota before moving to the plains."},
        {"n": "Ho-Chunk", "src": "en.wikipedia.org/wiki/Blue_Earth_Reservation", "poly": [[-94.7, 43.7], [-93.7, 43.8], [-93.9, 44.4], [-94.7, 44.3]], "lat": 43.9, "lon": -94.2, "note": "Relocated into southern Minnesota in the 1840s.", "after": {"y": 1863, "t": "expelled 1863 despite taking no part in the war"}},
    ],
    "events": [
        {"y": 1778, "t": "set", "n": "Grand Portage", "lat": 47.96, "lon": -89.68, "note": "North West Company depot on the Ojibwe carrying place.", "src": "en.wikipedia.org/wiki/Grand_Portage_National_Monument"},
        {"y": 1819, "t": "set", "n": "Fort Snelling", "lat": 44.89, "lon": -93.18, "note": "Begun 1819 at Bdote, the rivers' confluence.", "src": "en.wikipedia.org/wiki/Fort_Snelling"},
        {"y": 1837, "t": "rem", "n": "The 1837 cessions", "lat": 45.4, "lon": -92.9, "note": "Ojibwe pine lands and Dakota lands east of the Mississippi ceded.", "src": "treatiesmatter.org/treaties/land/1837-ojibwe-dakota"},
        {"y": 1843, "t": "set", "n": "Stillwater", "pp": [[1900, 12318], [2020, 19394]], "lat": 45.06, "lon": -92.81, "note": "Lumber town; the 1848 convention that asked for a territory.", "src": "en.wikipedia.org/wiki/Stillwater,_Minnesota"},
        {"y": 1849, "t": "cap", "n": "St. Paul", "pp": [[1860, 10401], [1900, 163065], [1950, 311349], [2020, 311527]], "lat": 44.95, "lon": -93.09, "note": "Territorial capital 1849, state capital since.", "src": "en.wikipedia.org/wiki/Saint_Paul,_Minnesota"},
        {"y": 1851, "t": "rem", "n": "Traverse des Sioux and Mendota", "lat": 44.4, "lon": -94.0, "note": "Dakota bands cede about 24 million acres for roughly seven cents an acre.", "src": "en.wikipedia.org/wiki/Treaty_of_Traverse_des_Sioux"},
        {"y": 1852, "t": "set", "n": "Mankato", "pp": [[1900, 10599], [2020, 44488]], "lat": 44.16, "lon": -94.00, "note": "Settled 1852.", "src": "en.wikipedia.org/wiki/Mankato,_Minnesota"},
        {"y": 1854, "t": "rem", "n": "La Pointe and the 1855 treaty", "lat": 47.3, "lon": -91.5, "note": "Ojibwe cede the Arrowhead and north-central Minnesota; reservations at Fond du Lac, Grand Portage, Leech Lake, Mille Lacs.", "src": "en.wikipedia.org/wiki/Treaty_of_La_Pointe"},
        {"y": 1855, "t": "set", "n": "Minneapolis", "pp": [[1870, 13066], [1900, 202718], [1950, 521718], [2020, 429954]], "lat": 44.98, "lon": -93.27, "note": "Milling at St. Anthony Falls; merged with St. Anthony 1872.", "src": "en.wikipedia.org/wiki/Minneapolis"},
        {"y": 1856, "t": "set", "n": "Duluth", "pp": [[1880, 3483], [1900, 52969], [1930, 101463], [2020, 86697]], "lat": 46.79, "lon": -92.10, "note": "Platted 1856, named for the explorer of 1679.", "src": "en.wikipedia.org/wiki/Duluth,_Minnesota"},
        {"y": 1862, "t": "rem", "n": "US-Dakota War", "lat": 44.31, "lon": -94.46, "note": "August and September 1862 along the Minnesota River; New Ulm twice attacked.", "src": "en.wikipedia.org/wiki/Dakota_War_of_1862"},
        {"y": 1862, "t": "rem", "n": "Mankato executions", "lat": 44.16, "lon": -94.00, "note": "December 26, 1862: 38 Dakota hanged, the largest one-day mass execution in US history.", "src": "en.wikipedia.org/wiki/Dakota_War_of_1862"},
        {"y": 1863, "t": "rem", "n": "Exile and bounties", "lat": 44.89, "lon": -93.18, "note": "Congress abolishes the Dakota and Ho-Chunk reservations; exile follows internment at Fort Snelling, where 102 to 300 died.", "src": "en.wikipedia.org/wiki/Dakota_War_of_1862"},
    ],
    "census": [[1850, 6077], [1860, 172023], [1870, 439706], [1880, 780773],
               [1890, 1310283], [1900, 1751394], [1910, 2075708], [1920, 2387125],
               [1930, 2563953], [1940, 2792300], [1950, 2982483], [1960, 3413864],
               [1970, 3804971], [1980, 4075970], [1990, 4375099], [2000, 4919479],
               [2010, 5303925], [2020, 5706494]],
    "native": [[1862, 7000, "eastern Dakota, Wingerd's estimate; Ojibwe uncounted"],
               [1863, 300, "Dakota remaining lawfully in Minnesota after the exile, order of magnitude"]],
    "geo": {"hp": {"n": "Eagle Mountain", "el": "701 m", "lat": 47.90, "lon": -90.56}},
    "refs": [
        ["US-Dakota War of 1862: the war, the executions, the exile.", "https://en.wikipedia.org/wiki/Dakota_War_of_1862"],
        ["Treaty of Traverse des Sioux, 1851.", "https://en.wikipedia.org/wiki/Treaty_of_Traverse_des_Sioux"],
    
        ["Nation homelands: the Minnesota Historical Society on the Ojibwe and Dakota, and the treaty records.",
         "https://www.mnhs.org/fortsnelling/learn/native-americans"],],
}

PAGES = {
    "ca": "california.html", "pa": "pennsylvania.html",
    "ma": "massachusetts.html", "al": "alabama.html",
    "ne": "nebraska.html", "mn": "minnesota.html",
}
SIBLINGS = [("california.html", "California"), ("pennsylvania.html", "Pennsylvania"),
            ("massachusetts.html", "Massachusetts"), ("alabama.html", "Alabama"),
            ("nebraska.html", "Nebraska"), ("minnesota.html", "Minnesota")]

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ · Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
  --line:#2b2b2b; --accent:#58a6ff; --water:#3d9bd6; --nation:#ffb02e;
  --rem:#e0684b; --set:#7fb8ff; --cap:#ffd24d; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
.wrap { max-width:1320px; margin:0 auto; padding:32px 20px 60px; }
header.site { border-top:4px solid var(--accent); padding-top:22px; margin-bottom:20px;
  display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }
.brand { font-weight:700; font-size:20px; letter-spacing:.1em; text-decoration:none; color:var(--text); }
.brand:hover { color:var(--accent); }
nav.site a { color:var(--muted); text-decoration:none; font-size:14px; margin-right:12px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 10px; font-size:26px; }
.chips { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:10px; align-items:center; }
.chips button { font:inherit; font-size:13px; padding:5px 13px; border-radius:999px;
  border:1px solid var(--line); background:#1a1a1a; color:var(--muted); cursor:pointer; }
.chips button.on { color:var(--text); border-color:var(--accent); background:#1c2733; }
.chips button:hover { border-color:var(--accent); }
.stage { display:flex; gap:20px; align-items:flex-start; }
#mapwrap { flex:1 1 640px; min-width:0; position:relative; background:#151719;
  border:1px solid var(--line); border-radius:12px; overflow:hidden; }
#mapwrap canvas, #mapwrap svg { position:absolute; inset:0; width:100%; height:100%; display:block; }
#mapwrap svg { position:relative; }
.side { flex:0 0 320px; position:sticky; top:16px; display:flex;
  flex-direction:column; gap:14px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:14px 16px; }
#flagImg { width:100%; max-height:130px; object-fit:contain; background:#0d0d0d;
  border:1px solid var(--line); border-radius:8px; display:none; }
#flagNone { color:var(--muted); font-size:13px; padding:20px 0; text-align:center;
  border:1px dashed var(--line); border-radius:8px; }
#eraTxt { font-size:13.5px; margin-top:8px; }
#yearBig { font-size:30px; font-weight:700; }
#popTxt { color:var(--muted); font-size:13px; line-height:1.55; margin-top:4px; }
#kindTxt { color:var(--muted); font-size:11.5px; letter-spacing:.09em; text-transform:uppercase; }
#nameTxt { font-weight:700; font-size:16px; margin:2px 0 6px; }
#bodyTxt { color:var(--muted); font-size:13px; line-height:1.5; }
#srcTxt { color:var(--muted); font-size:11.5px; margin-top:8px; border-top:1px solid var(--line);
  padding-top:6px; overflow-wrap:anywhere; }
.tl { margin-top:14px; }
.tlticks { position:relative; height:40px; margin:0 62px 2px 84px; }
.tlticks button { position:absolute; transform:translateX(-50%); font:inherit; font-size:11px;
  font-family:ui-monospace,Menlo,monospace; color:var(--muted); background:none; border:none;
  padding:1px 3px; cursor:pointer; line-height:1.1; }
.tlticks button::after { content:""; display:block; margin:2px auto 0; width:0; height:0;
  border-left:4px solid transparent; border-right:4px solid transparent;
  border-top:5px solid var(--muted); }
.tlticks button:hover, .tlticks button.here { color:var(--accent); }
.tlticks button:hover::after, .tlticks button.here::after { border-top-color:var(--accent); }
.tlticks button.row2 { top:0; } .tlticks button.row1 { top:21px; }
.tlrow { display:flex; gap:10px; align-items:center; }
.tlrow button { font:inherit; font-size:13.5px; padding:6px 14px; border-radius:999px;
  border:1px solid var(--line); background:#1a1a1a; color:var(--text); cursor:pointer; }
.tlrow button:hover { border-color:var(--accent); }
.tlrow input[type=range] { flex:1; accent-color:var(--accent); }
#yearTxt { font-family:ui-monospace,Menlo,monospace; font-size:15px; width:52px; text-align:right; }
.eraband { position:relative; height:14px; margin:6px 62px 0 84px; border-radius:4px;
  overflow:hidden; border:1px solid var(--line); }
.eraband div { position:absolute; top:0; bottom:0; }
.eraband span { position:absolute; top:-2px; width:2px; bottom:-2px; }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.refs { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.refs p { margin:0 0 8px; overflow-wrap:anywhere; }
.refs a { color:var(--accent); }
h2.refh { font-size:15px; margin:26px 0 8px; }
@media (max-width:900px){ .stage{flex-direction:column;} .side{position:static; width:100%;
  flex-direction:row; flex-wrap:wrap;} .side .card{flex:1 1 260px;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="library.html">&larr; Library &middot; USA</a>__SIBS__</nav>
</header>
<h1>__TITLE__</h1>
<div class="chips">
  <button id="cTer" class="on">Terrain</button>
  <button id="cWoo" class="on">Woods</button>
  <button id="cRiv" class="on">Rivers</button>
  <button id="cLak" class="on">Lakes</button>
  <button id="cCou">Counties</button>
  <button id="cNat" class="on">Nations</button>
  <button id="cTow" class="on">Towns</button>
  <span id="loadTxt" style="color:var(--muted);font-size:12px"></span>
</div>
<div class="stage">
  <div id="mapwrap">
    <canvas id="terC"></canvas>
    <canvas id="wooC"></canvas>
    <svg id="map"></svg>
  </div>
  <div class="side">
    <div class="card">
      <img id="flagImg" alt="">
      <div id="flagNone" hidden></div>
      <div id="eraTxt"></div>
    </div>
    <div class="card">
      <div id="yearBig"></div>
      <div id="popTxt"></div>
    </div>
    <div class="card">
      <div id="kindTxt"></div>
      <div id="nameTxt">A mark under the cursor lands here</div>
      <div id="bodyTxt"></div>
      <div id="srcTxt"></div>
    </div>
  </div>
</div>
<div class="tl">
  <div class="tlticks" id="ticks"></div>
  <div class="tlrow">
    <button id="bPlay">Play</button>
    <input type="range" id="yr" min="1492" max="2025" value="1492" step="1">
    <div id="yearTxt"></div>
  </div>
  <div class="eraband" id="eband"></div>
</div>
<p class="note">__NOTE1__</p>
<p class="note">__NOTE2__</p>
<h2 class="refh">References</h2>
<div class="refs">__REFS__</div>
</div>
<script>
const ST=__ST__, HIST=__HIST__;
const W=ST.W, H=ST.H;
const [MX0,MY0,MX1,MY1]=ST.m;
const R=6378137, RAD=Math.PI/180;
function XY(lat,lon){
  const mx=R*lon*RAD, my=R*Math.log(Math.tan(Math.PI/4+lat*RAD/2));
  return [ (mx-MX0)/(MX1-MX0)*W, (MY1-my)/(MY1-MY0)*H ];
}
const wrap=document.getElementById('mapwrap');
wrap.style.aspectRatio=W+' / '+H;
const svg=document.getElementById('map');
svg.setAttribute('viewBox','0 0 '+W+' '+H);
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const layers={ter:true,woo:true,riv:true,lak:true,cou:false,nat:true,tow:true};
let year=1492, playing=false, pinned=null;

function ringsPath(rr){ return rr.map(r=>'M'+r.map(p=>p[0]+','+p[1]).join('L')+'Z').join(''); }
const outlineD=ringsPath(ST.outline);

function fmt(x){ return x==null?'?':x.toLocaleString('en-US'); }
// growing city circle: 0 below 10,000, then log-scaled to 20 million
function cityR(p){ if(!p||p<1e4) return 0;
  return 4+4.5*(Math.log10(Math.min(p,2e7))-4); }
// tier color: green 10 thousand, yellow 100 thousand, orange one
// million, red ten million
function cityC(p){ if(p>=1e7) return '#ef5350'; if(p>=1e6) return '#ff9440';
  if(p>=1e5) return '#ffd24d'; return '#66bb6a'; }

function render(){
  let s='';
  s+='<defs><clipPath id="stclip"><path d="'+outlineD+'"/></clipPath></defs>';
  s+='<path d="'+outlineD+'" fill="'+(layers.ter||layers.woo?'none':'#1d2126')+'" stroke="none"/>';
  if(layers.cou){
    ST.counties.forEach((c,i)=>{
      s+='<g data-cty="'+i+'"><path d="'+ringsPath(c.r)+'" fill="rgba(0,0,0,0)" stroke="#e6e6e6" stroke-opacity="0.75" stroke-width="0.8"/></g>';
    });
  }
  if(layers.lak) for(const l of ST.lakes)
    s+='<path d="'+ringsPath(l.r)+'" fill="var(--water)" fill-opacity="0.85" stroke="none"/>';
  if(layers.riv) for(const r of ST.rivers){
    const wdt=r.n?1.6:0.9;
    for(const seg of r.s)
      s+='<path d="M'+seg.map(p=>p[0]+','+p[1]).join('L')+'" fill="none" stroke="var(--water)" stroke-width="'+wdt+'" stroke-opacity="'+(r.n?0.95:0.55)+'"/>';
  }
  // the state border is drawn only once it existed
  if(year>=HIST.border)
    s+='<path d="'+outlineD+'" fill="none" stroke="#121212" stroke-width="3.4" stroke-opacity="0.75"/>'
      +'<path d="'+outlineD+'" fill="none" stroke="#e6e6e6" stroke-width="1.7"/>';
  for(const nb of (HIST.nb||[])){
    if(!nb.sea&&year<HIST.border) continue;
    const [x,y]=XY(nb.lat,nb.lon);
    const rot=nb.v?' transform="rotate(-90 '+x.toFixed(1)+' '+y.toFixed(1)+')"':'';
    s+= nb.sea
      ?'<text x="'+x+'" y="'+y+'" text-anchor="middle" font-size="12.5" font-style="italic" fill="var(--water)" fill-opacity="0.9" stroke="#121212" stroke-width="2.6" paint-order="stroke">'+esc(nb.n)+'</text>'
      :'<text x="'+x+'" y="'+y+'" text-anchor="middle" font-size="11.5" letter-spacing="2"'+rot+' fill="#9aa4ad" stroke="#121212" stroke-width="2.6" paint-order="stroke">'+esc(nb.n.toUpperCase())+'</text>';
  }
  if(layers.ter&&HIST.geo&&HIST.geo.hp){
    const hp=HIST.geo.hp, [x,y]=XY(hp.lat,hp.lon);
    s+='<g data-hp="1"><path d="M'+x+','+(y-7)+' L'+(x-6)+','+(y+4)+' L'+(x+6)+','+(y+4)+' Z" fill="#e6e6e6" stroke="#121212" stroke-width="1"/>'
      +'<text x="'+(x+9)+'" y="'+(y+4)+'" font-size="11" fill="#c9d1d9" stroke="#121212" stroke-width="2.4" paint-order="stroke">'+esc(hp.n)+' '+esc(hp.el)+'</text></g>';
  }
  if(layers.nat) HIST.nations.forEach((n,i)=>{
    const gone=n.after&&year>=n.after.y;
    const hue=(i*137.508+40)%360;
    const [x,y]=XY(n.lat,n.lon);
    s+='<g data-nat="'+i+'" style="cursor:pointer">';
    if(n.poly)
      s+='<path d="'+blob(n.poly)+'" clip-path="url(#stclip)"'
        +' fill="hsl('+hue+',62%,55%)" fill-opacity="'+(gone?0.10:0.30)+'"'
        +' stroke="hsl('+hue+',62%,62%)" stroke-opacity="'+(gone?0.3:0.8)+'" stroke-width="1.3"/>';
    s+='<g opacity="'+(gone?0.5:1)+'">'
      +'<text x="'+x+'" y="'+y+'" text-anchor="middle" font-size="13" font-style="italic" fill="var(--nation)" stroke="#121212" stroke-width="3" paint-order="stroke">'+esc(n.n)+'</text>'
      +(gone?'<text x="'+x+'" y="'+(y+13)+'" text-anchor="middle" font-size="9.5" fill="var(--rem)" stroke="#121212" stroke-width="2.4" paint-order="stroke">'+n.after.y+'</text>':'')
      +'</g></g>';
  });
  if(layers.tow) HIST.events.forEach((e,i)=>{
    if(e.y>year) return;
    const [x,y]=XY(e.lat,e.lon);
    if(e.t==='rem'){
      s+='<g data-ev="'+i+'" style="cursor:pointer"><rect x="'+(x-4)+'" y="'+(y-4)+'" width="8" height="8" transform="rotate(45 '+x+' '+y+')" fill="var(--rem)" stroke="#121212" stroke-width="1"/></g>';
    } else {
      const cap=e.t==='cap';
      const p=e.pp?interp(e.pp,year):null;
      const R=cityR(p), C=cityC(p);
      s+='<g data-ev="'+i+'" style="cursor:pointer">'
        +(R?'<circle cx="'+x+'" cy="'+y+'" r="'+R.toFixed(1)+'" fill="'+C+'" fill-opacity="0.62" stroke="'+C+'" stroke-opacity="0.95" stroke-width="1.2"/>':'')
        +(cap?'<path d="'+star(x,y,6)+'" fill="var(--cap)" stroke="#121212" stroke-width="1"/>'
             :'<circle cx="'+x+'" cy="'+y+'" r="3.6" fill="var(--set)" stroke="#121212" stroke-width="1"/>')
        +'<text x="'+x+'" y="'+(y-8-(R||0))+'" text-anchor="middle" font-size="10.5" fill="'+(cap?'var(--cap)':'#c9d1d9')+'" stroke="#121212" stroke-width="2.4" paint-order="stroke">'+esc(e.n)+'</text></g>';
    }
  });
  if(layers.tow){
    const tiers=[[1e4,'10,000'],[1e5,'100,000'],[1e6,'1,000,000'],[1e7,'10,000,000']];
    const Rmax=cityR(1e7), cx=16+Rmax, by=H-14;
    s+='<g pointer-events="none">';
    s+='<text x="16" y="'+(by-2*Rmax-10)+'" font-size="10" fill="#8b949e" stroke="#121212" stroke-width="2.4" paint-order="stroke">City population</text>';
    // filled disks, largest painted first so each tier stays visible
    for(const [p] of [...tiers].reverse()){
      const r=cityR(p), C=cityC(p);
      s+='<circle cx="'+cx+'" cy="'+(by-r)+'" r="'+r.toFixed(1)+'" fill="'+C+'" fill-opacity="0.62" stroke="'+C+'" stroke-opacity="0.95" stroke-width="1"/>';
    }
    for(const [p,lab] of tiers){
      const r=cityR(p), ty=by-2*r, C=cityC(p);
      s+='<line x1="'+cx+'" y1="'+ty+'" x2="'+(cx+Rmax+8)+'" y2="'+ty+'" stroke="#8b949e" stroke-opacity="0.55" stroke-width="0.7"/>'
        +'<text x="'+(cx+Rmax+11)+'" y="'+(ty+3)+'" font-size="9" fill="'+C+'" stroke="#121212" stroke-width="2.2" paint-order="stroke">'+lab+'</text>';
    }
    s+='</g>';
  }
  svg.innerHTML=s;
}
// a smooth closed blob through lon/lat vertices (Catmull-Rom to bezier)
function blob(ll){
  const P=ll.map(([lon,lat])=>XY(lat,lon)), n=P.length;
  let d='M'+P[0][0].toFixed(1)+','+P[0][1].toFixed(1);
  for(let i=0;i<n;i++){
    const p0=P[(i-1+n)%n], p1=P[i], p2=P[(i+1)%n], p3=P[(i+2)%n];
    const c1=[p1[0]+(p2[0]-p0[0])/6, p1[1]+(p2[1]-p0[1])/6];
    const c2=[p2[0]-(p3[0]-p1[0])/6, p2[1]-(p3[1]-p1[1])/6];
    d+='C'+c1[0].toFixed(1)+','+c1[1].toFixed(1)+' '+c2[0].toFixed(1)+','+c2[1].toFixed(1)+' '+p2[0].toFixed(1)+','+p2[1].toFixed(1);
  }
  return d+'Z';
}
function star(x,y,r){
  let d='';
  for(let i=0;i<10;i++){
    const a=-Math.PI/2+i*Math.PI/5, rr=i%2?r*0.45:r;
    d+=(i?'L':'M')+(x+rr*Math.cos(a)).toFixed(1)+','+(y+rr*Math.sin(a)).toFixed(1);
  }
  return d+'Z';
}

// ---- population and era readouts ----
const CEN=(HIST.colonial||[]).concat(HIST.census);
function interp(pts,y){
  if(!pts.length||y<pts[0][0]) return null;
  if(y>=pts[pts.length-1][0]) return pts[pts.length-1][1];
  for(let i=0;i<pts.length-1;i++){
    const [a,pa]=pts[i], [b,pb]=pts[i+1];
    if(y>=a&&y<b) return Math.round(pa+(pb-pa)*(y-a)/(b-a));
  }
  return null;
}
const flagCache={};
async function flagUrl(f){
  if(!f) return null;
  const key=f.a||f.c;
  if(flagCache[key]!==undefined) return flagCache[key];
  let u=null;
  if(f.c) u='https://commons.wikimedia.org/wiki/Special:FilePath/'+encodeURIComponent(f.c)+'?width=320';
  else{
    try{
      const r=await fetch('https://en.wikipedia.org/api/rest_v1/page/summary/'+encodeURIComponent(f.a.replace(/ /g,'_')));
      if(r.ok){ const j=await r.json(); if(j.thumbnail) u=j.thumbnail.source; }
    }catch(e){}
  }
  flagCache[key]=u; return u;
}
async function setYear(y){
  year=y;
  document.getElementById('yr').value=y;
  document.getElementById('yearTxt').textContent=y;
  document.getElementById('yearBig').textContent=y;
  const era=HIST.eras.find(e=>y>=e.y0&&y<e.y1)||HIST.eras[HIST.eras.length-1];
  document.getElementById('eraTxt').textContent=era.l;
  const img=document.getElementById('flagImg'), none=document.getElementById('flagNone');
  const u=await flagUrl(era.f);
  if(y!==year) return;
  if(u){ img.src=u; img.style.display='block'; none.hidden=true; }
  else{ img.style.display='none'; none.hidden=false;
    none.textContent=era.f?'flag unavailable':'No flag: the nations\\u2019 own land'; }
  const cen=interp(CEN,y);
  const natLast=HIST.native.length?HIST.native[HIST.native.length-1][0]:0;
  const nat=y<=natLast?interp(HIST.native,y):null;
  let t=[];
  if(cen!=null) t.push((y>=(HIST.census[0][0])?'Census (interpolated): ':'Colonial estimate: ')+fmt(cen));
  else t.push('Before the counts: '+HIST.pre);
  if(nat!=null) t.push('Native population (estimate): '+fmt(nat));
  document.getElementById('popTxt').innerHTML=t.map(esc).join('<br>');
  render();
}

// ---- cards ----
function show(kind,name,body,src){
  document.getElementById('kindTxt').textContent=kind;
  document.getElementById('nameTxt').textContent=name;
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').textContent=src||'';
}
function target(e){
  const g=e.target.closest('[data-nat],[data-ev],[data-cty],[data-hp]');
  if(!g) return null;
  if(g.dataset.nat!==undefined){ const n=HIST.nations[+g.dataset.nat];
    return ['A nation of this land',n.n,
      n.note+(n.after?' '+n.after.t.charAt(0).toUpperCase()+n.after.t.slice(1)+'.':'')
      +' The patch is an approximate homeland, drawn for orientation.',
      n.src||'']; }
  if(g.dataset.ev!==undefined){ const ev=HIST.events[+g.dataset.ev];
    const k=ev.t==='rem'?'Removal and dispossession':ev.t==='cap'?'Capital \\u00b7 '+ev.y:'Settlement \\u00b7 '+ev.y;
    let body=ev.note;
    if(ev.pp){ const p=interp(ev.pp,year);
      if(p) body+=' Population around '+year+': '+fmt(p)+' (census, interpolated).'; }
    return [k,ev.n,body,ev.src]; }
  if(g.dataset.cty!==undefined){ const c=ST.counties[+g.dataset.cty];
    return ['County \\u00b7 recent population',c.n,'Population about '+fmt(c.p)+'.','Census figures via the Balsama county dataset, 2025']; }
  if(g.dataset.hp!==undefined){ const hp=HIST.geo.hp;
    return ['Highest point',hp.n,'Elevation '+hp.el+'.','']; }
  return null;
}
svg.addEventListener('pointerover',e=>{ if(pinned) return;
  const t=target(e); if(t) show(...t); });
svg.addEventListener('click',e=>{
  const g=e.target.closest('[data-nat],[data-ev],[data-cty],[data-hp]');
  if(!g){ pinned=null; return; }
  const id=g.dataset.nat!==undefined?'n'+g.dataset.nat:g.dataset.ev!==undefined?'e'+g.dataset.ev:g.dataset.cty!==undefined?'c'+g.dataset.cty:'hp';
  pinned = pinned===id?null:id;
  const t=target(e); if(t) show(...t);
});

// ---- timeline ----
document.getElementById('yr').addEventListener('input',e=>{ stop(); setYear(+e.target.value); });
let timer=null;
function stop(){ playing=false; document.getElementById('bPlay').textContent='Play';
  if(timer){ clearInterval(timer); timer=null; } }
document.getElementById('bPlay').onclick=()=>{
  if(playing){ stop(); return; }
  playing=true; document.getElementById('bPlay').textContent='Pause';
  if(year>=2025) setYear(1492);
  timer=setInterval(()=>{ if(year>=2025){ stop(); return; } setYear(year+1); },45);
};
(function eband(){
  const eb=document.getElementById('eband'), span=2025-1492;
  const cols=['#3a3a3a','#7a6a2f','#2f5d7a','#7a2f2f','#2f7a4f','#50407a','#7a5a2f'];
  HIST.eras.forEach((e,i)=>{
    const d=document.createElement('div');
    d.style.left=((e.y0-1492)/span*100)+'%';
    d.style.width=((Math.min(e.y1,2025)-e.y0)/span*100)+'%';
    d.style.background=cols[i%cols.length]; d.title=e.y0+' \\u00b7 '+e.l;
    eb.appendChild(d);
  });
  HIST.events.forEach(ev=>{
    const m=document.createElement('span');
    m.style.left=((ev.y-1492)/span*100)+'%';
    m.style.background=ev.t==='rem'?'var(--rem)':ev.t==='cap'?'var(--cap)':'var(--set)';
    m.title=ev.y+' \\u00b7 '+ev.n;
    eb.appendChild(m);
  });
})();
// jump markers: each era boundary (statehood, transfers of power) is a
// clickable year above the slider
(function ticks(){
  const tk=document.getElementById('ticks'), span=2025-1492;
  const pts=HIST.eras.map(e=>({y:e.y0,l:e.l}))
    .concat(HIST.marks||[])
    .filter(p=>p.y>1492).sort((a,b)=>a.y-b.y);
  let lastX={1:-99,2:-99};
  pts.forEach(p=>{
    const x=(p.y-1492)/span*100;
    const row=(x-lastX[1]<5.5&&x-lastX[2]>=5.5)?2:1; lastX[row]=x;
    const b=document.createElement('button');
    b.className='row'+row;
    b.style.left=x+'%';
    b.textContent=p.y;
    b.title=p.y+' \\u00b7 '+p.l;
    b.onclick=()=>{ stop(); setYear(p.y); };
    tk.appendChild(b);
  });
})();

// ---- chips ----
const CH={cTer:'ter',cWoo:'woo',cRiv:'riv',cLak:'lak',cCou:'cou',cNat:'nat',cTow:'tow'};
for(const id in CH) document.getElementById(id).onclick=e=>{
  const k=CH[id]; layers[k]=!layers[k];
  e.target.classList.toggle('on',layers[k]);
  if(k==='ter'){ document.getElementById('terC').style.display=layers.ter?'':'none'; if(layers.ter) terrain(); }
  if(k==='woo'){ document.getElementById('wooC').style.display=layers.woo?'':'none'; if(layers.woo) woods(); }
  render();
};

// ---- terrain: AWS Terrain Tiles (terrarium), shaded and tinted ----
let terDone=false, wooDone=false;
const loadTxt=document.getElementById('loadTxt');
async function terrain(){
  if(terDone) return; terDone=true;
  const cv=document.getElementById('terC'); const SC=2;
  cv.width=W*SC; cv.height=Math.round(H*SC);
  const ctx=cv.getContext('2d');
  loadTxt.textContent='loading terrain\\u2026';
  try{
    const world=2*Math.PI*R;
    let z=Math.round(Math.log2(world/(MX1-MX0)*(W*SC)/256)); z=Math.max(5,Math.min(11,z));
    let ts,tx0,tx1,ty0,ty1;
    for(;;){
      ts=world/(1<<z);
      tx0=Math.floor((MX0+world/2)/ts); tx1=Math.floor((MX1+world/2)/ts);
      ty0=Math.floor((world/2-MY1)/ts); ty1=Math.floor((world/2-MY0)/ts);
      if((tx1-tx0+1)*(ty1-ty0+1)<=80||z<=5) break;
      z--;
    }
    const px=Math.ceil((tx1-tx0+1)*256), py=Math.ceil((ty1-ty0+1)*256);
    const off=new OffscreenCanvas(px,py), octx=off.getContext('2d');
    await Promise.all([...Array((tx1-tx0+1)*(ty1-ty0+1))].map(async(_,i)=>{
      const x=tx0+i%(tx1-tx0+1), y2=ty0+Math.floor(i/(tx1-tx0+1));
      const r=await fetch('https://s3.amazonaws.com/elevation-tiles-prod/terrarium/'+z+'/'+x+'/'+y2+'.png');
      const b=await createImageBitmap(await r.blob());
      octx.drawImage(b,(x-tx0)*256,(y2-ty0)*256);
    }));
    const img=octx.getImageData(0,0,px,py), d=img.data;
    const elev=new Float32Array(px*py);
    let emin=1e9, emax=-1e9;
    for(let i=0;i<px*py;i++){
      const e=d[i*4]*256+d[i*4+1]+d[i*4+2]/256-32768;
      elev[i]=e; if(e>emax)emax=e; if(e<emin)emin=e;
    }
    emin=Math.max(emin,-5);
    // the sea: below-zero cells connected to the map edge, so a below-sea
    // valley inland (Death Valley) stays land
    const water=new Uint8Array(px*py), stk=[];
    const seed=i=>{ if(elev[i]<=0&&!water[i]){ water[i]=1; stk.push(i); } };
    for(let x=0;x<px;x++){ seed(x); seed((py-1)*px+x); }
    for(let y2=0;y2<py;y2++){ seed(y2*px); seed(y2*px+px-1); }
    while(stk.length){
      const i=stk.pop(), x=i%px, y2=(i-x)/px;
      if(x>0) seed(i-1); if(x<px-1) seed(i+1);
      if(y2>0) seed(i-px); if(y2<py-1) seed(i+px);
    }
    const out=octx.createImageData(px,py), o=out.data;
    for(let y2=0;y2<py;y2++)for(let x=0;x<px;x++){
      const i=y2*px+x, e=elev[i];
      if(water[i]){ o[i*4]=30; o[i*4+1]=68; o[i*4+2]=98; o[i*4+3]=235; continue; }
      const t=Math.max(0,Math.min(1,(e-emin)/Math.max(1,emax-emin)));
      const ex=elev[y2*px+Math.min(px-1,x+1)], ey=elev[Math.min(py-1,y2+1)*px+x];
      const sh=Math.max(0,Math.min(1,0.5+((ex-e)+(e-ey))*0.012));
      let r0,g0,b0;
      if(t<0.5){ const u=t/0.5; r0=40+u*120; g0=80+u*70; b0=45+u*45; }
      else{ const u=(t-0.5)/0.5; r0=160+u*80; g0=150+u*90; b0=90+u*140; }
      o[i*4]=r0*(0.55+0.65*sh); o[i*4+1]=g0*(0.55+0.65*sh); o[i*4+2]=b0*(0.55+0.65*sh); o[i*4+3]=235;
    }
    octx.putImageData(out,0,0);
    const sx=(MX0+world/2)/ts-tx0, sy=(world/2-MY1)/ts-ty0;
    ctx.drawImage(off, sx*256, sy*256, (MX1-MX0)/ts*256, (MY1-MY0)/ts*256,
      0, 0, W*SC, Math.round(H*SC));
    loadTxt.textContent='';
  }catch(e){ loadTxt.textContent='terrain unavailable'; }
}
// ---- woods: USGS NLCD 2021 forest classes via the MRLC WMS ----
async function woods(){
  if(wooDone) return; wooDone=true;
  const cv=document.getElementById('wooC'); const SC=2;
  cv.width=W*SC; cv.height=Math.round(H*SC);
  const ctx=cv.getContext('2d');
  loadTxt.textContent='loading land cover\\u2026';
  try{
    const u='https://www.mrlc.gov/geoserver/mrlc_display/NLCD_2021_Land_Cover_L48/wms'
      +'?service=WMS&version=1.1.1&request=GetMap&layers=NLCD_2021_Land_Cover_L48&styles='
      +'&bbox='+MX0+','+MY0+','+MX1+','+MY1+'&width='+(W*SC)+'&height='+Math.round(H*SC)
      +'&srs=EPSG:3857&format=image/png';
    const b=await createImageBitmap(await (await fetch(u)).blob());
    const off=new OffscreenCanvas(W*SC,Math.round(H*SC)), octx=off.getContext('2d');
    octx.drawImage(b,0,0);
    const img=octx.getImageData(0,0,off.width,off.height), d=img.data;
    const F=[[104,171,99],[28,99,48],[181,202,143]];
    for(let i=0;i<d.length;i+=4){
      let keep=false;
      for(const [r0,g0,b0] of F)
        if(Math.abs(d[i]-r0)<14&&Math.abs(d[i+1]-g0)<14&&Math.abs(d[i+2]-b0)<14){ keep=true; break; }
      if(keep){ d[i]=46; d[i+1]=140; d[i+2]=70; d[i+3]=185; }
      else d[i+3]=0;
    }
    octx.putImageData(img,0,0);
    ctx.drawImage(off,0,0);
    loadTxt.textContent='';
  }catch(e){ loadTxt.textContent='land cover unavailable'; }
}

setYear(1492);
terrain(); woods();
window.__state=()=>({year, layers:{...layers}, counties:ST.counties.length,
  rivers:ST.rivers.length, lakes:ST.lakes.length, nations:HIST.nations.length,
  events:HIST.events.length, eras:HIST.eras.length,
  visEvents:HIST.events.filter(e=>e.y<=year).length, pinned, terDone, wooDone});
</script>
</body>
</html>
"""

NOTE1 = ("The map is the real state in Web Mercator: rivers and lakes from "
         "Natural Earth, county lines and recent populations from the "
         "Census Bureau's cartographic files, terrain shaded at view time "
         "from the AWS Terrain Tiles, and the woods layer drawn from the "
         "USGS National Land Cover Database, forest classes only. Each "
         "chip turns one layer on or off; a mark under the cursor fills "
         "the card, a click pins it. The border and neighbor names appear "
         "once the border was drawn.")
NOTE2 = ("The slider runs from 1492: the nations who lived here first as "
         "colored patches, approximate homelands for orientation, their "
         "population figures scholarly estimates, "
         "then settlements, capitals and removals year by year, while "
         "the flag panel shows whose claim covered the land until the "
         "official state flag. City circles grow green, then yellow, "
         "orange, red as census counts pass "
         "10 thousand, 100 thousand, one million, and the years above the "
         "slider jump to the turning points. "
         "These nations still exist today; "
         "Native Land Digital maps their territories fully, with "
         "community input, and is the place to see them properly.")


def refs_html(hist):
    rows = [
        ("Natural Earth, 10m rivers and lakes.", "https://www.naturalearthdata.com/"),
        ("US county geometry: Census cartographic boundaries via Plotly's dataset mirror.", "https://github.com/plotly/datasets"),
        ("County populations: Balsama US county dataset (Census figures via Wikipedia), 2025.", "https://github.com/balsama/us_counties_data"),
        ("Terrain: Mapzen/AWS Terrain Tiles (Open Data).", "https://registry.opendata.aws/terrain-tiles/"),
        ("Woods: USGS National Land Cover Database 2021, forest classes, via the MRLC WMS.", "https://www.mrlc.gov/"),
        ("Decennial census populations, state and city; city figures via each city's Wikipedia article.", "https://www.census.gov/data/tables/time-series/dec/popchange-data-text.html"),
        ("Flags: each era's Wikipedia article image, fetched at view time.", "https://en.wikipedia.org/"),
        ("Native Land Digital: the community-sourced map of Indigenous territories; the patches here are rough approximations of the documented homelands, not their data.", "https://native-land.ca/"),
    ] + hist["refs"]
    return "\n".join(f'<p>{t}\n<a href="{u}">{u}</a></p>' for t, u in rows)


for st, fname in PAGES.items():
    data = json.loads((DATA / f"{st}.json").read_text())
    hist = HIST[st]
    sibs = "".join(f' <a href="{f}">{n}</a>' for f, n in SIBLINGS if f != fname)
    html = (HTML.replace("__TITLE__", data["name"])
            .replace("__SIBS__", sibs)
            .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2)
            .replace("__REFS__", refs_html(hist))
            .replace("__ST__", json.dumps(data, separators=(",", ":")))
            .replace("__HIST__", json.dumps(hist, separators=(",", ":"))))
    (ROOT / fname).write_text(html, encoding="utf-8")
    print(f"wrote {ROOT / fname} ({len(html):,} B): "
          f"{len(hist['nations'])} nations, {len(hist['events'])} events, "
          f"{len(hist['eras'])} eras")
