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
import apa
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
    "early": [[1790, 1000, "Gente de raz\u00f3n"],
              [1821, 3270, "Gente de raz\u00f3n"],
              [1845, 7300, "Non-Native count, Mexican era"]],
    "census": [[1850, 92597], [1860, 379994], [1870, 560247], [1880, 864694],
               [1890, 1213398], [1900, 1485053], [1910, 2377549], [1920, 3426861],
               [1930, 5677251], [1940, 6907387], [1950, 10586223], [1960, 15717204],
               [1970, 19953134], [1980, 23667902], [1990, 29760021], [2000, 33871648],
               [2010, 37253956], [2020, 39538223]],
    "native": [[1769, 310000, "Cook's estimate"], [1848, 150000, "Madley"],
               [1870, 30000, "Madley"],
               [1900, 16000, "Madley; other sources ~25,000"],
               [2020, 631016, "2020 census, self-identified"]],
    "geo": {"hp": {"n": "Mount Whitney", "el": "4,421 m", "lat": 36.58, "lon": -118.29}},
    "refs": [
        ["Population of Native California; the estimates of Cook, Kroeber and others.", "https://en.wikipedia.org/wiki/Population_of_Native_California"],
        ["Madley, B. (2016). An American Genocide: The United States and the California Indian Catastrophe. Yale University Press.", "https://en.wikipedia.org/wiki/California_genocide"],
    
        ["Nation homelands and histories: each nation's Wikipedia article (Yurok, Pomo, Wintu, Maidu, Miwok, Ohlone, Yokuts, Chumash, Tongva, Kumeyaay, Mojave).",
         "https://en.wikipedia.org/wiki/Category:Native_American_tribes_in_California"],],
}

HIST["az"] = {
    "eras": [
        {"y0": 1492, "y1": 1691, "l": "O'odham, Hopi, Diné, Pai and Apache homelands", "f": None},
        {"y0": 1691, "y1": 1821, "l": "Spain (the Sonora and Nuevo México frontier)", "f": {"a": "Cross of Burgundy"}},
        {"y0": 1821, "y1": 1848, "l": "Mexico (Sonora and Nuevo México)", "f": {"a": "Flag of Mexico"}},
        {"y0": 1848, "y1": 1863, "l": "United States (Mexican Cession; Gadsden Purchase 1853)", "f": US},
        {"y0": 1863, "y1": 1912, "l": "Arizona Territory, 1863", "f": US},
        {"y0": 1912, "y1": 1917, "l": "Statehood, February 14, 1912", "f": US},
        {"y0": 1917, "y1": 2026, "l": "State flag adopted 1917", "f": {"a": "Flag of Arizona"}},
    ],
    "marks": [{"y": 1853, "l": "Gadsden Purchase"},
              {"y": 1912, "l": "Statehood, February 14, 1912, 48th state"}],
    "border": 1866,
    "nb": [
        {"n": "California", "lat": 34.3, "lon": -114.95},
        {"n": "Nevada", "lat": 36.6, "lon": -114.6},
        {"n": "Utah", "lat": 37.35, "lon": -112.3},
        {"n": "New Mexico", "lat": 34.2, "lon": -108.75, "v": True},
        {"n": "Sonora, México", "lat": 30.95, "lon": -111.6},
    ],
    "pre": "No count survives from before Spain arrived; the O'odham, Hopi, "
           "Diné, Pai and Apache peoples numbered many tens of thousands.",
    "nations": [
        {"n": "Diné (Navajo)", "src": "en.wikipedia.org/wiki/Navajo", "poly": [[-111.5, 35.8], [-109.1, 35.7], [-109.05, 37.0], [-111.3, 37.0]], "lat": 36.35, "lon": -110.2, "note": "The Navajo Nation is today the largest reservation in the country."},
        {"n": "Hopi", "src": "en.wikipedia.org/wiki/Hopi", "poly": [[-111.0, 35.5], [-110.0, 35.4], [-110.0, 36.3], [-111.1, 36.2]], "lat": 35.85, "lon": -110.55, "note": "Mesa-top villages; Oraibi has been lived in since about 1100."},
        {"n": "Hualapai and Havasupai", "src": "en.wikipedia.org/wiki/Hualapai", "poly": [[-114.0, 35.0], [-112.4, 35.3], [-112.6, 36.3], [-113.9, 36.0]], "lat": 35.6, "lon": -113.2, "note": "Pai peoples of the plateaus and canyons south of the Colorado."},
        {"n": "Yavapai", "src": "en.wikipedia.org/wiki/Yavapai", "poly": [[-113.3, 33.9], [-111.9, 34.0], [-112.0, 35.0], [-113.2, 34.9]], "lat": 34.45, "lon": -112.6, "note": "Central highlands, from the Verde Valley to the desert rivers.", "after": {"y": 1875, "t": "marched to San Carlos"}},
        {"n": "Ndee (Western Apache)", "src": "en.wikipedia.org/wiki/Western_Apache_people", "poly": [[-111.5, 33.2], [-109.5, 33.3], [-109.8, 34.7], [-111.3, 34.5]], "lat": 33.95, "lon": -110.4, "note": "White Mountain, San Carlos, Tonto and Cibecue bands."},
        {"n": "Chiricahua", "src": "en.wikipedia.org/wiki/Chiricahua", "poly": [[-110.2, 31.35], [-108.9, 31.45], [-109.0, 32.6], [-110.0, 32.5]], "lat": 31.95, "lon": -109.5, "note": "Cochise and Geronimo's people, in the mountains along the border.", "after": {"y": 1886, "t": "deported to Florida"}},
        {"n": "Tohono O'odham", "src": "en.wikipedia.org/wiki/Tohono_O%CA%BCodham", "poly": [[-113.3, 31.4], [-111.3, 31.5], [-111.5, 32.6], [-113.0, 32.5]], "lat": 32.0, "lon": -112.2, "note": "The desert people; their lands run deep into Sonora."},
        {"n": "Akimel O'odham and Piipaash", "src": "en.wikipedia.org/wiki/Akimel_O%27odham", "poly": [[-112.6, 32.9], [-111.3, 32.9], [-111.5, 33.6], [-112.5, 33.5]], "lat": 33.15, "lon": -111.9, "note": "River people of the Gila and Salt; Hohokam canals run under Phoenix."},
        {"n": "Quechan and Mojave", "src": "en.wikipedia.org/wiki/Quechan", "poly": [[-115.0, 32.5], [-114.2, 32.7], [-114.4, 35.0], [-115.1, 34.9]], "lat": 33.9, "lon": -114.55, "note": "Colorado River peoples, farming the floodplain."},
    ],
    "events": [
        {"y": 1691, "t": "set", "n": "Tumacácori", "lat": 31.57, "lon": -111.05, "note": "Father Kino's mission chain reaches the Santa Cruz valley.", "src": "en.wikipedia.org/wiki/Eusebio_Kino"},
        {"y": 1752, "t": "set", "n": "Tubac", "lat": 31.61, "lon": -111.05, "note": "Spanish presidio built after the O'odham uprising of 1751.", "src": "en.wikipedia.org/wiki/Tubac,_Arizona"},
        {"y": 1775, "t": "set", "n": "Tucson", "lat": 32.22, "lon": -110.97, "note": "Presidio San Agustín del Tucsón; capital of the territory 1867 to 1877.", "src": "en.wikipedia.org/wiki/Tucson,_Arizona"},
        {"y": 1854, "t": "set", "n": "Yuma", "lat": 32.69, "lon": -114.62, "note": "Colorado City at the river crossing.", "src": "en.wikipedia.org/wiki/Yuma,_Arizona"},
        {"y": 1864, "t": "cap", "n": "Prescott", "pp": [[1900, 3559], [1950, 6764], [1980, 20055], [2000, 33938], [2020, 45827]], "lat": 34.54, "lon": -112.47, "note": "Territorial capital 1864 to 1867 and 1877 to 1889.", "src": "en.wikipedia.org/wiki/Prescott,_Arizona"},
        {"y": 1864, "t": "rem", "n": "The Long Walk", "lat": 36.15, "lon": -109.55, "note": "Thousands of Diné force-marched to Bosque Redondo; the treaty of 1868 lets them return.", "src": "en.wikipedia.org/wiki/Long_Walk_of_the_Navajo"},
        {"y": 1868, "t": "cap", "n": "Phoenix", "lat": 33.45, "lon": -112.07, "note": "Founded 1868 on reopened Hohokam canals; the capital since 1889.", "src": "en.wikipedia.org/wiki/Phoenix,_Arizona"},
        {"y": 1871, "t": "rem", "n": "Camp Grant massacre", "lat": 32.85, "lon": -110.75, "note": "April 30, 1871: raiders from Tucson kill more than a hundred Apache, nearly all women and children.", "src": "en.wikipedia.org/wiki/Camp_Grant_massacre"},
        {"y": 1872, "t": "rem", "n": "Skeleton Cave", "lat": 33.62, "lon": -111.55, "note": "Salt River Canyon, December 1872: cavalry kill 76 Yavapai in a cave.", "src": "en.wikipedia.org/wiki/Battle_of_Salt_River_Canyon"},
        {"y": 1875, "t": "rem", "n": "March to San Carlos", "lat": 34.56, "lon": -111.85, "note": "February 1875: 1,400 Yavapai and Dilzhe'e marched from Camp Verde; well over a hundred die on the way.", "src": "en.wikipedia.org/wiki/Yavapai_Wars"},
        {"y": 1876, "t": "set", "n": "Flagstaff", "lat": 35.2, "lon": -111.65, "note": "Railroad and lumber town under the San Francisco Peaks.", "src": "en.wikipedia.org/wiki/Flagstaff,_Arizona"},
        {"y": 1878, "t": "set", "n": "Mesa", "lat": 33.42, "lon": -111.83, "note": "Latter-day Saint settlers reuse Hohokam canals.", "src": "en.wikipedia.org/wiki/Mesa,_Arizona"},
        {"y": 1879, "t": "set", "n": "Tombstone", "lat": 31.71, "lon": -110.07, "note": "Silver boom town of 1879.", "src": "en.wikipedia.org/wiki/Tombstone,_Arizona"},
        {"y": 1886, "t": "rem", "n": "Geronimo's surrender", "lat": 31.58, "lon": -109.06, "note": "September 1886, Skeleton Canyon: the Chiricahua, army scouts included, are deported to Florida.", "src": "en.wikipedia.org/wiki/Geronimo"},
    ],
    "early": [[1860, 6482, "Federal count, Arizona County"]],
    "census": [[1870, 9658], [1880, 40440], [1890, 88243], [1900, 122931],
               [1910, 204354], [1920, 334162], [1930, 435573], [1940, 499261],
               [1950, 749587], [1960, 1302161], [1970, 1770900], [1980, 2718215],
               [1990, 3665228], [2000, 5130632], [2010, 6392017], [2020, 7151502]],
    "native": [[1900, 26480, "census"], [1950, 65761, "census"],
               [2000, 255879, "census"], [2020, 319712, "census"]],
    "geo": {"hp": {"n": "Humphreys Peak", "el": "3,852 m", "lat": 35.35, "lon": -111.68}},
    "refs": [
        ["The Long Walk of the Navajo, 1864 to 1868.", "https://en.wikipedia.org/wiki/Long_Walk_of_the_Navajo"],
        ["Camp Grant massacre, April 30, 1871.", "https://en.wikipedia.org/wiki/Camp_Grant_massacre"],
        ["Nation homelands and histories: each nation's Wikipedia article (Diné, Hopi, Hualapai, Havasupai, Yavapai, Ndee, Chiricahua, Tohono O'odham, Akimel O'odham, Quechan, Mojave).",
         "https://en.wikipedia.org/wiki/Category:Native_American_tribes_in_Arizona"],
        ["Arizona's censuses, 1870 to 2020, and its American Indian counts.", "https://en.wikipedia.org/wiki/Arizona"],
    ],
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
        {"y": 1643, "t": "set", "n": "Tinicum Island", "lat": 39.87, "lon": -75.29, "note": "The Printzhof, seat of New Sweden.", "src": "en.wikipedia.org/wiki/The_Printzhof"},
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
    "early": [[1700, 17950, "Colonial estimate"],
              [1750, 119666, "Colonial estimate"],
              [1780, 327305, "Colonial estimate"]],
    "native": [[1600, 13000, "Lenape and Susquehannock combined, low bound"],
               [1670, 8000, "after the 1650s wars"],
               [1763, 20, "Conestoga, the last Susquehannock community"],
               [2020, 31052, "2020 census, self-identified"]],
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
    "early": [[1700, 55941, "Colonial estimate"],
              [1750, 188000, "Colonial estimate"],
              [1780, 268627, "Colonial estimate"]],
    "native": [[1600, 100000, "New England-wide"], [1620, 30000, "after the Great Dying, order of magnitude"],
               [1680, 10000, "after King Philip's War, order of magnitude"],
               [2020, 24018, "2020 census, self-identified"]],
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
    "marks": [{"y": 1819,
               "l": "Statehood, December 14, 1819, 22nd state"}],
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
        {"n": "Moundville", "kind": "A Mississippian center", "src": "en.wikipedia.org/wiki/Moundville_Archaeological_Site", "poly": [[-87.8, 32.85], [-87.4, 32.85], [-87.45, 33.15], [-87.8, 33.1]], "lat": 33.0, "lon": -87.63, "note": "Mississippian mound center, about 1000 to 1450 CE."},
        {"n": "Yuchi (Euchee)", "src": "en.wikipedia.org/wiki/Yuchi", "poly": [[-85.4, 32.7], [-84.92, 32.62], [-84.95, 31.95], [-85.35, 31.98], [-85.45, 32.35]], "lat": 32.35, "lon": -85.15, "note": "Yuchi Town on the Chattahoochee was the principal settlement from the mid 1700s until removal, with other Yuchis living among the Upper Creek towns."},
        {"n": "Shawnee", "src": "en.wikipedia.org/wiki/Shawnee", "poly": [[-86.5, 33.6], [-85.9, 33.3], [-85.5, 32.5], [-86.0, 32.2], [-86.5, 32.8]], "lat": 32.9, "lon": -86.1, "note": "Peter Chartier led more than 400 Shawnee to the Coosa valley in 1748 and founded Chalakagay; others lived at Sawanogi on the Tallapoosa."},
        {"n": "Apalachee", "src": "en.wikipedia.org/wiki/Apalachee", "poly": [[-88.15, 31.2], [-87.8, 31.15], [-87.75, 30.65], [-88.05, 30.6], [-88.2, 30.9]], "lat": 30.95, "lon": -87.95, "note": "Survivors of the 1704 massacre in Florida settled near French Mobile. A refugee community from 1704 to 1763 rather than a long homeland; the nation is seated in Louisiana today."},
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
    "early": [[1818, 68000, "Alabama Territory census"]],
    "census": [[1800, 1250], [1810, 9046], [1820, 127901], [1830, 309527],
               [1840, 590756], [1850, 771623], [1860, 964201], [1870, 996992],
               [1880, 1262505], [1890, 1513401], [1900, 1828697], [1910, 2138093],
               [1920, 2348174], [1930, 2646248], [1940, 2832961], [1950, 3061743],
               [1960, 3266740], [1970, 3444165], [1980, 3893888], [1990, 4040587],
               [2000, 4447100], [2010, 4779736], [2020, 5024279]],
    "native": [[1685, 9000, "Muscogee (Creek) alone, Braund; no state-wide "
                            "figure exists for this date"],
               [1830, 60000,
                "the four nations across their homelands, at removal"],
               [1840, 5000,
                "remaining after the removals, order of magnitude"],
               [2020, 33625, "2020 census, self-identified"]],
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
    "marks": [{"y": 1867, "l": "Statehood, March 1, 1867, 37th state"}],
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
        {"n": "Ho-Chunk (Winnebago Tribe of Nebraska)", "src": "en.wikipedia.org/wiki/Winnebago_Tribe_of_Nebraska", "poly": [[-96.6, 42.4], [-96.1, 42.4], [-96.06, 42.05], [-96.55, 42.05]], "lat": 42.23, "lon": -96.35, "note": "Removed from Wisconsin and then from Minnesota, and settled in Thurston County in 1865. A homeland made by removal, and a continuous one since."},
        {"n": "Isanyathi (Santee Dakota)", "src": "en.wikipedia.org/wiki/Santee_Sioux_Reservation", "poly": [[-98.0, 42.87], [-97.4, 42.85], [-97.38, 42.62], [-97.95, 42.63]], "lat": 42.75, "lon": -97.68, "note": "Expelled from Minnesota after the 1862 war and settled on the south bank of the Missouri in Knox County, where the Santee Sioux Nation is seated today."},
        {"n": "Ioway (Iowa Tribe of Kansas and Nebraska)", "src": "en.wikipedia.org/wiki/Iowa_Tribe_of_Kansas_and_Nebraska", "poly": [[-96.1, 40.0], [-95.31, 40.0], [-95.35, 40.45], [-95.95, 40.55], [-96.2, 40.3]], "lat": 40.2, "lon": -95.75, "note": "The lower Missouri valley, including the southeastern corner, and a reservation straddling the Kansas line in Richardson County."},
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
    "early": [[1854, 2732, "Nebraska Territory census"]],
    "census": [[1860, 28841], [1870, 122993], [1880, 452402], [1890, 1062656],
               [1900, 1066300], [1910, 1192214], [1920, 1296372], [1930, 1377963],
               [1940, 1315834], [1950, 1325510], [1960, 1411330], [1970, 1483493],
               [1980, 1569825], [1990, 1578385], [2000, 1711263], [2010, 1826341],
               [2020, 1961504]],
    "native": [[1800, 17000, "Pawnee, Omaha, Ponca, Otoe-Missouria combined, rough"],
               [1859, 3400, "Pawnee alone, on the Nance County "
                            "reservation after smallpox and cholera"],
               [1900, 1700,
                "after removals and epidemics, order of magnitude"],
               [2020, 23102, "2020 census, self-identified"]],
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
    "marks": [{"y": 1858, "l": "Statehood, May 11, 1858, 32nd state"}],
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
        {"n": "Assiniboine (Nakoda)", "src": "en.wikipedia.org/wiki/Assiniboine", "poly": [[-96.9, 48.7], [-95.3, 49.2], [-94.2, 48.8], [-94.6, 47.9], [-96.2, 47.9], [-96.95, 48.2]], "lat": 48.45, "lon": -95.6, "note": "Separated from their Dakota relatives near the headwaters of the Mississippi and held the Lake of the Woods country before drifting northwest. Seventeenth century; their later territory is in Montana and the prairies."},
        {"n": "Cree (N\u0113hiyawak)", "src": "en.wikipedia.org/wiki/Cree", "poly": [[-94.6, 49.0], [-92.4, 48.7], [-90.4, 48.25], [-90.7, 47.85], [-92.6, 48.2], [-94.5, 48.5]], "lat": 48.5, "lon": -92.6, "note": "Rainy Lake and the border lakes during the fur trade, allied with the Assiniboine, before Ojibwe expansion and their own move northwest."},
        {"n": "Ih\u00e1\u014bkt\u021fu\u014bwa\u014b (Yankton) and Yanktonai", "src": "en.wikipedia.org/wiki/Yankton_Sioux_Tribe", "poly": [[-96.6, 45.7], [-95.2, 45.2], [-94.5, 44.1], [-95.3, 43.5], [-96.45, 43.5], [-96.75, 44.8]], "lat": 44.4, "lon": -95.9, "note": "Divisions of the O\u010dh\u00e9thi \u0160ak\u00f3wi\u014b distinct from the Santee Dakota. They held the southwestern prairie, and the 1858 treaty reserved the pipestone quarries to them."},
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
    "early": [[1849, 5000, "Minnesota Territory census"],
              [1857, 150037, "Minnesota Territory census"]],
    "census": [[1850, 6077], [1860, 172023], [1870, 439706], [1880, 780773],
               [1890, 1310283], [1900, 1751394], [1910, 2075708], [1920, 2387125],
               [1930, 2563953], [1940, 2792300], [1950, 2982483], [1960, 3413864],
               [1970, 3804971], [1980, 4075970], [1990, 4375099], [2000, 4919479],
               [2010, 5303925], [2020, 5706494]],
    "native": [[1850, 31700, "Dakota and Ojibwe together, "
                         "Minnesota Historical Society"],
               [1860, 19600,
                "the same series, across the treaty decade"],
               [1862, 7000, "eastern Dakota, Wingerd's estimate; Ojibwe uncounted"],
               [1863, 300, "Dakota remaining lawfully in Minnesota after the exile, order of magnitude"],
               [2020, 68641, "2020 census, self-identified"]],
    "geo": {"hp": {"n": "Eagle Mountain", "el": "701 m", "lat": 47.90, "lon": -90.56}},
    "refs": [
        ["US-Dakota War of 1862: the war, the executions, the exile.", "https://en.wikipedia.org/wiki/Dakota_War_of_1862"],
        ["Treaty of Traverse des Sioux, 1851.", "https://en.wikipedia.org/wiki/Treaty_of_Traverse_des_Sioux"],
    
        ["Nation homelands: the Minnesota Historical Society on the Ojibwe and Dakota, and the treaty records.",
         "https://www.mnhs.org/fortsnelling/learn/native-americans"],],
}

# --- the official living symbols ----------------------------------------
# k: what the statute calls it. n: the everyday name. b: the accepted
# binomial. s: the name the statute uses, when the taxonomy has moved
# since. y: year adopted. a: the English Wikipedia article, which is where
# the photograph comes from at view time.
SYMBOLS = {
"ca": [
 {"k": "Bird", "n": "California quail", "b": "Callipepla californica",
  "s": "Lophortyx californica, the California valley quail", "y": 1931,
  "a": "California quail",
  "t": "The plume over the bill looks like one curved feather and is six "
       "overlapping black ones."},
 {"k": "Flower", "n": "California poppy", "b": "Eschscholzia californica",
  "y": 1903, "a": "Eschscholzia californica",
  "t": "A separate section of the penal code makes picking one on state "
       "or private land an offense."},
 {"k": "Tree", "n": "California redwood", "b": "Sequoia sempervirens and "
  "Sequoiadendron giganteum", "s": "Sequoia sempervirens, Sequoia gigantea",
  "y": 1937, "a": "Sequoia sempervirens",
  "t": "One symbol covering two species. The 1937 act named the redwood "
       "without saying which, and a 1953 amendment settled it by adding "
       "the giant sequoia rather than choosing."},
 {"k": "Grass", "n": "Purple needlegrass", "b": "Stipa pulchra",
  "s": "Nassella pulchra", "y": 2004, "a": "Stipa pulchra",
  "t": "A bunchgrass whose roots reach several meters down, which is how "
       "it survives the dry season."},
],
"az": [
 {"k": "Bird", "n": "Cactus wren", "b": "Campylorhynchus brunneicapillus",
  "s": "Heleodytes brunneicapillus couesi", "y": 1931, "a": "Cactus wren",
  "t": "The largest wren in the country. It builds several nests in cholla "
       "and spare ones are used for roosting."},
 {"k": "Flower", "n": "Saguaro blossom", "b": "Carnegiea gigantea",
  "s": "the white waxy flower of Cereus giganteus", "y": 1931, "a": "Saguaro",
  "t": "The symbol is the blossom rather than the cactus. It opens after "
       "sunset, closes by mid afternoon, and cannot pollinate itself."},
 {"k": "Tree", "n": "Palo verde", "b": "Parkinsonia florida and "
  "Parkinsonia microphylla", "s": "the genus Cercidium", "y": 1954,
  "a": "Parkinsonia florida",
  "t": "The statute names a genus and not a species. Palo verde is green "
       "stick: the bark photosynthesises, so the tree keeps feeding itself "
       "after it drops its leaves."},
],
"pa": [
 {"k": "Bird", "n": "Ruffed grouse", "b": "Bonasa umbellus", "y": 1931,
  "a": "Ruffed grouse",
  "t": "The male's drumming is not a call. He beats his wings against the "
       "air, and the thump carries a quarter of a mile."},
 {"k": "Flower", "n": "Mountain laurel", "b": "Kalmia latifolia", "y": 1933,
  "a": "Kalmia latifolia",
  "t": "The genus is named for Pehr Kalm, a student of Linnaeus who "
       "collected the plant in North America in the 1740s."},
 {"k": "Tree", "n": "Eastern hemlock", "b": "Tsuga canadensis", "y": 1931,
  "a": "Tsuga canadensis",
  "t": "Hemlock bark was the tannin of the state's leather industry. Whole "
       "stands were stripped for bark and the wood left where it fell."},
 {"k": "Conservation plant", "n": "Penngift crownvetch",
  "b": "Securigera varia", "s": "Coronilla varia, the Penngift variety",
  "y": 1982, "a": "Securigera varia",
  "t": "Bred at Penn State to hold highway embankments, adopted as a "
       "symbol, and now widely treated as invasive."},
],
"ma": [
 {"k": "Bird", "n": "Black-capped chickadee", "b": "Poecile atricapillus",
  "s": "Penthestes atricapillus", "y": 1941, "a": "Black-capped chickadee",
  "t": "It hides food in thousands of separate places and grows new "
       "hippocampal neurons each autumn to keep track of them."},
 {"k": "Flower", "n": "Mayflower, or trailing arbutus", "b": "Epigaea repens",
  "y": 1918, "a": "Epigaea repens",
  "t": "The same statute makes digging one up an offense, at fifty dollars, "
       "doubled for doing it at night or in disguise."},
 {"k": "Tree", "n": "American elm", "b": "Ulmus americana", "y": 1941,
  "a": "Ulmus americana",
  "t": "Chosen for the Cambridge elm under which Washington was said to "
       "have taken command of the Continental Army in 1775."},
 {"k": "Berry", "n": "Cranberry", "b": "Vaccinium macrocarpon", "y": 1994,
  "a": "Vaccinium macrocarpon",
  "t": "One of a very few fruits farmed commercially that is native to "
       "North America."},
],
"al": [
 {"k": "Bird", "n": "Yellowhammer, the northern flicker",
  "b": "Colaptes auratus", "s": "the bird commonly called the yellow-hammer",
  "y": 1927, "a": "Northern flicker",
  "t": "Yellowhammer in Britain is a different bird entirely. The Alabama "
       "usage is said to come from Civil War troops whose butternut "
       "uniforms had yellow trim."},
 {"k": "Flower", "n": "Camellia", "b": "Camellia japonica", "y": 1959,
  "a": "Camellia japonica",
  "t": "Not native. It replaced goldenrod in 1959, and the statute did not "
       "say which camellia until 1999, which is why the state later added "
       "a native wildflower as well."},
 {"k": "Wildflower", "n": "Oak-leaf hydrangea", "b": "Hydrangea quercifolia",
  "y": 1999, "a": "Hydrangea quercifolia",
  "t": "Native, described by William Bartram, and the only hydrangea whose "
       "lobed leaves turn red in autumn."},
 {"k": "Tree", "n": "Southern longleaf pine", "b": "Pinus palustris",
  "y": 1997, "a": "Longleaf pine",
  "t": "The 1949 act said only southern pine. Seedlings spend years in a "
       "grass stage, looking like a tuft while they push a taproot down, "
       "before they shoot up."},
 {"k": "Native grass", "n": "Little bluestem", "b": "Schizachyrium scoparium",
  "y": 2024, "a": "Schizachyrium scoparium",
  "t": "The grass of the longleaf pine understory, and the newest of the "
       "state's living symbols."},
],
"ne": [
 {"k": "Bird", "n": "Western meadowlark", "b": "Sturnella neglecta", "y": 1929,
  "a": "Western meadowlark",
  "t": "Audubon named it neglecta because earlier naturalists, the Lewis "
       "and Clark expedition among them, had passed it over as an eastern "
       "meadowlark."},
 {"k": "Flower", "n": "Goldenrod", "b": "Solidago gigantea", "y": 1895,
  "a": "Solidago gigantea",
  "t": "The 1895 act names no species, and it was never written into the "
       "codified statutes, so the binomial here is convention rather than "
       "law. The senate floor fight was against the violet, and goldenrod "
       "won partly on being native."},
 {"k": "Tree", "n": "Eastern cottonwood", "b": "Populus deltoides", "y": 1972,
  "a": "Populus deltoides",
  "t": "It replaced the American elm, which had been the state tree since "
       "1937 and which Dutch elm disease had killed."},
 {"k": "Grass", "n": "Little bluestem", "b": "Schizachyrium scoparium",
  "s": "Andropogon scoparius", "y": 1969, "a": "Schizachyrium scoparium",
  "t": "One of the four grasses of the tallgrass prairie, and the one that "
       "turns copper in autumn."},
],
"mn": [
 {"k": "Bird", "n": "Common loon", "b": "Gavia immer", "y": 1961,
  "a": "Common loon",
  "t": "The state holds about six thousand nesting pairs, more than any "
       "other except Alaska."},
 {"k": "Flower", "n": "Showy lady's slipper", "b": "Cypripedium reginae",
  "y": 1902, "a": "Cypripedium reginae",
  "t": "The 1893 legislature named a species that does not grow in the "
       "state, and the 1902 one corrected it. A plant can take sixteen "
       "years to flower and live about fifty."},
 {"k": "Tree", "n": "Red pine, called Norway pine", "b": "Pinus resinosa",
  "y": 1953, "a": "Pinus resinosa",
  "t": "Norway pine is a misnomer. The species is North American and grows "
       "nowhere near Norway."},
 {"k": "Grain", "n": "Wild rice", "b": "Zizania palustris", "y": 1977,
  "a": "Zizania palustris",
  "t": "Manoomin, a grass of shallow lakes rather than a rice, and central "
       "to Ojibwe treaty rights in the state."},
],
}

PAGES = {
    "ca": "california.html", "az": "arizona.html",
    "pa": "pennsylvania.html",
    "ma": "massachusetts.html", "al": "alabama.html",
    "ne": "nebraska.html", "mn": "minnesota.html",
}
SIBLINGS = [("california.html", "California"), ("arizona.html", "Arizona"),
            ("pennsylvania.html", "Pennsylvania"),
            ("massachusetts.html", "Massachusetts"), ("alabama.html", "Alabama"),
            ("nebraska.html", "Nebraska"), ("minnesota.html", "Minnesota")]

# Total area, land and water, km2: US Census Bureau, 2020 gazetteer files.
# The ghost of another state is drawn from these, and from that state's
# own outline in tools/data/states.
AREA_KM2 = {"ca": 423967, "az": 295234, "pa": 119280, "ma": 27336,
            "al": 135767, "ne": 200330, "mn": 225163}


def ghosts(me):
    """The other states' outlines, thinned, for the Compare chips."""
    out = {}
    for st in PAGES:
        if st == me:
            continue
        d = json.loads((DATA / f"{st}.json").read_text())
        rings = []
        for r in d["outline"]:
            if len(r) < 12:
                continue
            step = 1 if len(r) < 80 else 2
            rings.append([[round(x, 1), round(y, 1)] for x, y in r[::step]])
        out[st] = {"n": d["name"], "km2": AREA_KM2[st], "W": d["W"],
                   "H": d["H"], "m": d["m"], "o": rings}
    return out


def ghost_chips(me):
    return ('<span class="sep"></span><span class="grp">'
            '<span class="gl">Ghost of</span>'
            + "".join(f'<button data-ghost="{st}">{n}</button>'
                      for st, n in [(k, json.loads((DATA / f"{k}.json").read_text())["name"])
                                    for k in PAGES] if st != me)
            + '</span>')


# each state's city page, built by build_cities.py
CITY_PAGE = {"ca": ("los-angeles.html", "Los Angeles"),
             "pa": ("lancaster.html", "Lancaster"),
             "ma": ("amherst.html", "Amherst"),
             "al": ("tuscaloosa.html", "Tuscaloosa"),
             "ne": ("omaha.html", "Omaha"),
             "mn": ("northfield.html", "Northfield")}
# the data file behind each city page, for the middle of its frame
CITY_FILE = {"los-angeles.html": "la.json", "lancaster.html": "lancaster.json",
             "amherst.html": "amherst.json", "tuscaloosa.html": "tuscaloosa.json",
             "omaha.html": "omaha.json", "northfield.html": "northfield.json"}

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
/* the chips sit in three groups: the ground, the lines drawn on it, and
   the layers that move with the year */
.chips .grp { display:inline-flex; gap:8px; align-items:center; flex-wrap:wrap; }
.chips .gl { color:var(--muted); font-size:10.5px; letter-spacing:.09em;
  text-transform:uppercase; margin-right:2px; }
.chips .sep { width:1px; height:22px; background:var(--line); margin:0 4px; }
.stage { display:flex; gap:20px; align-items:flex-start; }
.mapcol { flex:1 1 640px; min-width:0; }
#mapwrap { position:relative; background:#151719;
  border:1px solid var(--line); border-radius:12px; overflow:hidden; }
#mapwrap canvas, #mapwrap svg { position:absolute; inset:0; width:100%; height:100%; display:block; }
#mapwrap svg { position:relative; outline:none; }
#mapwrap svg:focus-visible { box-shadow:inset 0 0 0 2px var(--accent); }
#loadTxt { position:absolute; right:10px; top:8px; z-index:2; pointer-events:none;
  color:var(--muted); font-size:11.5px; padding:2px 9px; border-radius:999px;
  background:rgba(18,18,18,.72); }
#loadTxt:empty { display:none; }
/* zoom: two buttons in the corner, the wheel, a drag to pan; lines keep
   their width on screen and marks and names keep their size */
#map path, #map line, #map circle, #map rect, #map polyline { vector-effect:non-scaling-stroke; }
#map [data-mig] path { vector-effect:none; }
#map.zoomed { cursor:grab; touch-action:none; }
#map.zoomed.panning { cursor:grabbing; }
#mapwrap canvas { transform-origin:0 0; }
.zoomctl { position:absolute; left:10px; top:10px; z-index:2; display:flex; flex-direction:column; gap:4px; }
.zoomctl button { width:28px; height:28px; border-radius:8px; border:1px solid var(--line);
  background:rgba(18,18,18,.82); color:var(--text); font:inherit; font-size:16px; line-height:1;
  cursor:pointer; padding:0; }
.zoomctl button:hover { border-color:var(--accent); }
.zoomctl button:disabled { opacity:.35; cursor:default; border-color:var(--line); }
.zcity { position:absolute; right:10px; bottom:10px; z-index:2; font-size:12.5px; padding:4px 11px;
  border-radius:999px; border:1px solid var(--accent); background:rgba(18,18,18,.86);
  color:var(--text); text-decoration:none; }
.zcity:hover { color:var(--accent); }
.zcity[hidden] { display:none; }
.side { flex:0 0 320px; position:sticky; top:16px; display:flex;
  flex-direction:column; gap:14px; max-height:calc(100vh - 32px);
  overflow-y:auto; scrollbar-width:thin; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:14px 16px; flex:none; }
.symh { color:var(--muted); font-size:11px; letter-spacing:.09em;
  text-transform:uppercase; margin-bottom:8px; }
.sym { display:flex; gap:10px; align-items:flex-start; padding:7px 0;
  border-top:1px solid var(--line); }
.sym:first-child { border-top:none; padding-top:0; }
.sym img { width:54px; height:54px; object-fit:cover; border-radius:7px;
  background:#0d0d0d; flex:0 0 54px; }
.sym .noimg { width:54px; height:54px; border-radius:7px; background:#202020;
  border:1px solid var(--line); flex:0 0 54px; }
.sym .b { min-width:0; }
.sym .k { color:var(--muted); font-size:10.5px; letter-spacing:.07em;
  text-transform:uppercase; }
.sym .n { font-size:13.5px; font-weight:600; line-height:1.3; }
.sym .sci { font-size:12px; font-style:italic; color:#9fb6c4;
  overflow-wrap:anywhere; }
.sym .y { font-size:11.5px; color:var(--muted); }
.sym .t { font-size:12px; color:#b0b0b0; line-height:1.45; margin-top:3px; }
.sym .st { font-size:11.5px; color:var(--muted); margin-top:3px; }
#flagImg { width:100%; max-height:130px; object-fit:contain; background:#0d0d0d;
  border:1px solid var(--line); border-radius:8px; display:none; }
#flagNone { color:var(--muted); font-size:13px; padding:20px 0; text-align:center;
  border:1px dashed var(--line); border-radius:8px; }
#eraTxt { font-size:13.5px; margin-top:8px; }
#yearBig { font-size:30px; font-weight:700; }
#popTxt { color:var(--muted); font-size:13px; line-height:1.55; margin-top:4px; }
#popTxt .totG { color:#0ca30c; }
#kindTxt { color:var(--muted); font-size:11.5px; letter-spacing:.09em; text-transform:uppercase; }
#nameTxt { font-weight:700; font-size:16px; margin:2px 0 6px; }
#nameTxt.empty { font-weight:400; font-size:13px; color:var(--muted); }
#bodyTxt { color:var(--muted); font-size:13px; line-height:1.5; }
#srcTxt { color:var(--muted); font-size:11.5px; margin-top:8px; border-top:1px solid var(--line);
  padding-top:6px; overflow-wrap:anywhere; }
#srcTxt:empty { display:none; }
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
/* a year that cannot find room on any row keeps its arrow and its title */
.tlticks button.hid { color:transparent; }
.tlticks button.hid:hover { color:var(--accent); background:var(--bg); z-index:2; }
.tlrow { display:flex; gap:10px; align-items:center; }
.tlrow button { font:inherit; font-size:13.5px; padding:6px 14px; border-radius:999px;
  border:1px solid var(--line); background:#1a1a1a; color:var(--text); cursor:pointer; }
.tlrow button:hover { border-color:var(--accent); }
.tlrow input[type=range] { flex:1; accent-color:var(--accent); }
#bPlay { width:74px; }
#yearTxt { font-family:ui-monospace,Menlo,monospace; font-size:15px; width:52px; text-align:right; }
.eraband { position:relative; height:14px; margin:6px 62px 0 84px; border-radius:4px;
  overflow:hidden; border:1px solid var(--line); }
.eraband div { position:absolute; top:0; bottom:0; }
.eraband span { position:absolute; top:-2px; width:2px; bottom:-2px; }
/* the population under the slider: the counted line and the Native
   estimate on one log scale, with a dot riding the year */
.spark { position:relative; height:62px; margin:6px 62px 0 84px; }
.spark svg { position:absolute; inset:0; width:100%; height:100%; display:block; overflow:visible; }
.spark text { font-size:9.5px; fill:var(--muted); }
.tlkey { display:flex; gap:6px 16px; flex-wrap:wrap; align-items:center;
  font-size:11.5px; color:var(--muted); margin:8px 0 0 84px; }
.tlkey i { display:inline-block; width:9px; height:9px; border-radius:2px;
  margin-right:5px; vertical-align:-1px; }
.tlkey i.ln { height:2px; width:14px; border-radius:1px; vertical-align:2px; }
.tlkey .spd { margin-left:auto; display:inline-flex; gap:6px; align-items:center; }
.tlkey .spd button { font:inherit; font-size:11px; padding:2px 9px; border-radius:999px;
  border:1px solid var(--line); background:#1a1a1a; color:var(--muted); cursor:pointer; }
.tlkey .spd button.on { color:var(--text); border-color:var(--accent); }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.method { color:var(--muted); font-size:12.5px; margin-top:14px;
  max-width:820px; }
.method summary { cursor:pointer; color:var(--accent); }
details.sources { margin-top:22px; border-top:1px solid var(--line); padding-top:10px; max-width:760px; }
details.sources > summary { cursor:pointer; color:var(--muted); font-size:12.5px; letter-spacing:.06em; text-transform:uppercase; }
details.sources > summary:hover { color:var(--accent); }
.method p { margin:9px 0 0; }
.refs { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.refs p { margin:0 0 8px; overflow-wrap:anywhere; }
.refs a { color:var(--accent); }
__APACSS__
h2.refh { font-size:15px; margin:26px 0 8px; }
@media (max-width:900px){ .stage{flex-direction:column;} .mapcol{flex-basis:auto; width:100%;} #mapwrap{width:100%;}
  .side{position:static; width:100%; max-height:none; overflow:visible;
  flex-direction:row; flex-wrap:wrap;} .side .card{flex:1 1 260px;} }
/* a phone: the map scrolls sideways at a readable size, the chips lose
   their dividers, and the card that answers a tap sits above the map */
@media (max-width:600px){ .tlticks, .eraband, .spark{ margin-left:0; margin-right:0; }
  .tlkey{ margin-left:0; } .tlrow{ flex-wrap:wrap; } .tlrow input[type=range]{ flex:1 1 100%; order:3; }
  .tlkey .spd{ margin-left:0; }
  .chips{ gap:6px; } .chips .sep{ display:none; } .chips .grp{ gap:6px; }
  .chips button{ padding:4px 10px; font-size:12.5px; }
  .mapscroll{ overflow-x:auto; -webkit-overflow-scrolling:touch; border-radius:12px; }
  #mapwrap{ min-width:640px; }
  .side{ display:contents; } .stage{ gap:14px; align-items:stretch; }
  .side .card{ flex:none; }
  .side .card.hover{ order:-1; } .side .card.hover:has(#nameTxt.empty){ display:none; } }
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
  <span class="grp"><span class="gl">Ground</span>
  <button id="cTer" class="on">Terrain</button>
  <button id="cWoo" class="on">Woods</button>
  <button id="cRiv" class="on">Rivers</button>
  <button id="cLak" class="on">Lakes</button>
  </span><span class="sep"></span><span class="grp"><span class="gl">Lines</span>
  <button id="cCou">Counties</button>
  <button id="cHwy">Highways</button>
  </span><span class="sep"></span><span class="grp"><span class="gl">By the year</span>
  <button id="cNat" class="on">Nations</button>
  <button id="cTow" class="on">Towns</button>
  <button id="cUni">Colleges</button>
  <button id="cMig" class="on">Migrations</button>
  </span>__GHOSTCHIPS__
</div>
<div class="stage">
  <div class="mapcol">
  <div class="mapscroll"><div id="mapwrap">
    <canvas id="terC"></canvas>
    <canvas id="wooC"></canvas>
    <canvas id="watC"></canvas>
    <svg id="map" tabindex="0" aria-label="The map; arrow keys move the year when it has focus"></svg>
    <span id="loadTxt"></span>
    <div class="zoomctl"><button id="zIn" aria-label="Closer">+</button><button id="zOut" aria-label="Farther" disabled>&minus;</button></div>
    <a id="zCity" class="zcity" hidden></a>
  </div></div>
  <div class="tl">
    <div class="tlticks" id="ticks"></div>
    <div class="tlrow">
      <button id="bPlay">Play</button>
      <input type="range" id="yr" min="1492" max="2025" value="1492" step="1" aria-label="Year">
      <div id="yearTxt"></div>
    </div>
    <div class="eraband" id="eband"></div>
    <div class="spark" id="spark"></div>
    <div class="tlkey" id="tlkey"></div>
  </div>
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
    <div class="card hover">
      <div id="kindTxt"></div>
      <div id="nameTxt" class="empty">A mark under the cursor lands here</div>
      <div id="bodyTxt"></div>
      <div id="srcTxt"></div>
    </div>
    <div class="card">
      <div class="symh">The living symbols</div>
      <div id="symList"></div>
    </div>
  </div>
</div>
<p class="note">__NOTE1__</p>
<details class="sources"><summary>Sources</summary>
<div class="method"><details><summary>What the population line is made
of</summary><p>__METHOD__</p></details></div>
<div class="method"><details><summary>About the living symbols</summary>
<p>__SYMNOTE__</p></details></div>
<div class="refs">__REFS__</div>
</details>
</div>
<script>
const ST=__ST__, HIST=__HIST__, ROADS=__ROADS__, SYM=__SYM__, GHOST=__GHOST__;
// the city page inside this map, if there is one; the zoom hands off to it
const CITY=null;
const W=ST.W, H=ST.H;
const [MX0,MY0,MX1,MY1]=ST.m;
const R=6378137, RAD=Math.PI/180;
function MXY(mx,my){ return [ (mx-MX0)/(MX1-MX0)*W, (MY1-my)/(MY1-MY0)*H ]; }
function XY(lat,lon){
  const mx=R*lon*RAD, my=R*Math.log(Math.tan(Math.PI/4+lat*RAD/2));
  return MXY(mx,my);
}
const REDUCED=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const wrap=document.getElementById('mapwrap');
wrap.style.aspectRatio=W+' / '+H;
const svg=document.getElementById('map');
svg.setAttribute('viewBox','0 0 '+W+' '+H);
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');
const layers={ter:true,woo:true,riv:true,lak:true,cou:false,nat:true,tow:true,uni:false,hwy:false,mig:true,lim:false};
let year=1492, playing=false, pinned=null, focusNat=null, ghostSel=null, ghostOp=0;
// the year everything opens on; the rail then runs on its own
const START=1492;

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
// interstate, federal, state route
const RDC={i:'#cfe6ff', us:'#ffe3ab', sr:'#d3b0ee'};
const RDN={i:'Interstate', us:'US route', sr:'State route'};

// labels crowd at city scale, so each one is nudged clear of those
// already placed
let LBL=[];
function lblY(x,y,n,pw,lh){
  // lh, when given, is the line height of a larger label: it is then tried
  // above and below its anchor in turn and kept inside the frame
  const w=n*(pw||5.6), L=lh||13;
  const free=ty=>!LBL.some(b=>Math.abs(b[0]-x)<(b[2]+w)/2+4 && Math.abs(b[1]-ty)<Math.max(b[3]||13,L));
  let ty=y;
  if(lh){
    for(let k=0;k<40;k++){
      const c=y+(k%2?1:-1)*Math.ceil(k/2)*L;
      if(c<L||c>H-6) continue;
      if(free(c)){ ty=c; break; }
    }
  } else {
    for(let k=0;k<26;k++){ if(free(ty)) break; ty-=13; }
  }
  LBL.push([x,ty,w,L]);
  return ty;
}
// a polygon cut to the frame (Sutherland-Hodgman), for the part of a
// homeland that is actually in view
function clipToFrame(P){
  const edges=[[0,0,1],[W,0,-1],[0,1,1],[H,1,-1]];
  let out=P.slice();
  for(const [v,ax,sg] of edges){
    const inp=out; out=[];
    if(!inp.length) break;
    const inside=p=>sg>0?p[ax]>=v:p[ax]<=v;
    for(let i=0;i<inp.length;i++){
      const a=inp[i], b=inp[(i+1)%inp.length], ia=inside(a), ib=inside(b);
      if(ia) out.push(a);
      if(ia!==ib){
        const t=(v-a[ax])/(b[ax]-a[ax]);
        out.push([a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t]);
      }
    }
  }
  return out;
}
function centroid(P){
  let A=0,cx=0,cy=0;
  for(let i=0;i<P.length;i++){
    const a=P[i], b=P[(i+1)%P.length], f=a[0]*b[1]-b[0]*a[1];
    A+=f; cx+=(a[0]+b[0])*f; cy+=(a[1]+b[1])*f;
  }
  if(Math.abs(A)<1e-6) return null;
  return [cx/(3*A), cy/(3*A), Math.abs(A)/2];
}
// where a nation's name goes: its own anchor when that is in the frame,
// otherwise the middle of the part of the patch that is in view; then
// held clear of the edges and of the names already placed
function natLabel(n){
  let [x,y]=XY(n.lat,n.lon);
  const w=n.n.length*7.2;
  if(!(x>=0&&x<=W&&y>=0&&y<=H)){
    if(!n.poly) return null;
    const c=centroid(clipToFrame(n.poly.map(([lon,lat])=>XY(lat,lon))));
    if(!c||c[2]<400) return null;
    x=c[0]; y=c[1];
  }
  x=Math.max(w/2+6, Math.min(W-w/2-6, x));
  y=Math.max(16, Math.min(H-8, y));
  return [x, lblY(x,y,n.n.length,7.2,17)];
}
function render(){
  let s=''; LBL=[];
  s+='<defs><clipPath id="stclip"><path d="'+outlineD+'"/></clipPath>'
    +'<marker id="migArrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="3.6" markerHeight="3.6" orient="auto-start-reverse">'
    +'<path d="M0,1 L9,5 L0,9 z" fill="#ffc247"/></marker></defs>';
  // the ground is painted by the terrain canvas; until it has painted,
  // or if it never does, the state carries a flat fill of its own
  s+='<path d="'+outlineD+'" fill="'+((layers.ter&&terPainted)||(layers.woo&&wooPainted)?'none':'#1d2126')+'" stroke="none"/>';
  if(layers.cou){
    // each county joins the map in its founding year; the one the author
    // lived in is drawn in gold
    ST.counties.forEach((c,i)=>{
      if(c.y&&c.y>year) return;
      const mine=ST.home&&c.fips===ST.home;
      s+='<g data-cty="'+i+'"><path d="'+ringsPath(c.r)+'" fill="'+(mine?'#ffd24d':'rgba(0,0,0,0)')+'" fill-opacity="'+(mine?(ST.homeFill||0.16):1)+'" stroke="'+(mine?'#ffd24d':'#e6e6e6')+'" stroke-opacity="'+(mine?0.95:0.75)+'" stroke-width="'+(mine?2:0.8)+'"/></g>';
    });
  }
  // the city limits, where the map is a city rather than a state
  if(layers.lim&&ST.limits&&ST.limits.length){
    const d=ringsPath(ST.limits);
    s+='<g data-lim="1" style="cursor:pointer">'
      +'<path d="'+d+'" fill="none" stroke="#121212" stroke-width="3.6" stroke-opacity="0.6"/>'
      +'<path d="'+d+'" fill="none" stroke="#7ee0a8" stroke-width="1.8" stroke-dasharray="6 4"/></g>';
    if(ST.founded&&year>=ST.founded.y){
      const f=ringsPath(ST.founded.r);
      s+='<g data-fnd="1" style="cursor:pointer">'
        +'<path d="'+f+'" fill="#ffd24d" fill-opacity="0.10" stroke="#ffd24d" stroke-width="1.6" stroke-dasharray="3 3"/></g>';
    }
  }
  if(layers.lak) for(const l of ST.lakes)
    s+='<path d="'+ringsPath(l.r)+'" fill="var(--water)" fill-opacity="0.85" stroke="none"/>';
  if(layers.riv) for(const r of ST.rivers){
    const wdt=r.n?1.6:0.9;
    for(const seg of r.s)
      s+='<path d="M'+seg.map(p=>p[0]+','+p[1]).join('L')+'" fill="none" stroke="var(--water)" stroke-width="'+wdt+'" stroke-opacity="'+(r.n?0.95:0.55)+'"/>';
  }
  if(layers.hwy) ROADS.forEach((r,i)=>{
    // a route joins the map in the year it was designated; where no
    // year is documented (Mexico) the network is drawn whole instead
    if(r.y==null){ if(!HIST.hwyAll) return; }
    else if(r.y>year) return;
    const C=RDC[r.lv], w=r.lv==='i'?2.8:r.lv==='us'?2.0:1.35;
    let d='';
    for(const seg of r.s) d+='M'+seg.map(p=>p[0]+','+p[1]).join('L');
    s+='<g data-rd="'+i+'" style="cursor:pointer">'
      +'<path d="'+d+'" fill="none" stroke="#121212" stroke-opacity="0.55" stroke-width="'+(w+1.6)+'" stroke-linecap="round" stroke-linejoin="round"/>'
      +'<path d="'+d+'" fill="none" stroke="'+C+'" stroke-opacity="0.92" stroke-width="'+w+'" stroke-linecap="round" stroke-linejoin="round"/>';
    // the route's own number, on the longest run of it that is on screen
    const seg=r.s.reduce((a,b)=>segLen(b)>segLen(a)?b:a, r.s[0]||[]);
    if(seg&&seg.length>1&&segLen(seg)>70){
      const m=seg[Math.floor(seg.length/2)];
      s+='<text x="'+m[0]+'" y="'+(m[1]-5)+'" text-anchor="middle" font-size="9.5" fill="'+C+'" stroke="#121212" stroke-width="2.6" paint-order="stroke">'+esc(r.n)+'</text>';
    }
    s+='</g>';
  });
  // the state border is drawn only once it existed
  if(year>=HIST.border)
    s+='<path d="'+outlineD+'" fill="none" stroke="#121212" stroke-width="3.4" stroke-opacity="0.75"/>'
      +'<path d="'+outlineD+'" fill="none" stroke="#e6e6e6" stroke-width="1.7"/>';
  // another state's outline, at true ground scale, centered on this one
  if(ghostSel&&GHOST[ghostSel]&&ghostOp>0){
    s+='<path d="'+ghostPath(ghostSel)+'" fill="#e6e6e6" fill-opacity="'+(0.10*ghostOp).toFixed(3)+'" stroke="#ffffff" stroke-opacity="'+(0.9*ghostOp).toFixed(3)+'" stroke-width="1.6" stroke-dasharray="7 5" pointer-events="none"/>';
  }
  for(const nb of (HIST.nb||[])){
    if(!nb.sea&&year<HIST.border) continue;
    // a neighbor's name is held inside the frame, whichever way it runs
    let [x,y]=XY(nb.lat,nb.lon);
    const nw=nb.n.length*(nb.sea?7:9.5)/2+6;
    if(nb.v){ x=Math.max(12,Math.min(W-6,x)); y=Math.max(nw,Math.min(H-nw,y)); }
    else { x=Math.max(nw,Math.min(W-nw,x)); y=Math.max(16,Math.min(H-8,y)); }
    const rot=nb.v?' transform="rotate(-90 '+x.toFixed(1)+' '+y.toFixed(1)+')"':'';
    if(nb.sea) LBL.push([x,y,nb.n.length*7]);
    s+= nb.sea
      ?'<text x="'+x+'" y="'+y+'" text-anchor="middle" font-size="12.5" font-style="italic" fill="var(--water)" fill-opacity="0.9" stroke="#121212" stroke-width="2.6" paint-order="stroke">'+esc(nb.n)+'</text>'
      :'<text x="'+x+'" y="'+y+'" text-anchor="middle" font-size="11.5" letter-spacing="2"'+rot+' fill="#9aa4ad" stroke="#121212" stroke-width="2.6" paint-order="stroke">'+esc(nb.n.toUpperCase())+'</text>';
  }
  if(layers.nat) HIST.nations.forEach((n,i)=>{
    const gone=n.after&&year>=n.after.y;
    // one hue for every homeland: the outline says where each one is,
    // and the ground shows through
    const dim=focusNat!=null&&focusNat!==i;
    const lab=natLabel(n);
    s+='<g data-nat="'+i+'" style="cursor:pointer"'+(dim?' opacity="0.22"':'')+'>';
    if(n.poly)
      s+='<path d="'+blob(n.poly)+'"'
        +' fill="var(--nation)" fill-opacity="'+(gone?0.04:(ST.natFill||0.16))+'"'
        +' stroke="var(--nation)" stroke-opacity="'+(gone?0.3:(focusNat===i?1:0.75))+'" stroke-width="'+(focusNat===i?2:1.3)+'"/>';
    if(lab){
      const [x,y]=lab;
      s+='<g opacity="'+(gone?0.5:1)+'">'
        +'<text x="'+x.toFixed(1)+'" y="'+y.toFixed(1)+'" text-anchor="middle" font-size="13" font-style="italic" fill="var(--nation)" stroke="#121212" stroke-width="3" paint-order="stroke">'+esc(n.n)+'</text>'
        +(gone?'<text x="'+x.toFixed(1)+'" y="'+(y+13).toFixed(1)+'" text-anchor="middle" font-size="9.5" fill="var(--rem)" stroke="#121212" stroke-width="2.4" paint-order="stroke">'+n.after.y+'</text>':'')
        +'</g>';
    }
    s+='</g>';
  });
  if(layers.ter&&HIST.geo&&HIST.geo.hp){
    // the highest point, drawn over the homelands so it is never lost
    // in one; on a city map it is a note on the high ground, not a peak
    const hp=HIST.geo.hp, [x,y]=XY(hp.lat,hp.lon);
    const soft=!!hp.soft;
    s+='<g data-hp="1">'
      +(soft?'<circle cx="'+x+'" cy="'+y+'" r="2.6" fill="#c9d1d9" stroke="#121212" stroke-width="1"/>'
            :'<path d="M'+x+','+(y-7)+' L'+(x-6)+','+(y+4)+' L'+(x+6)+','+(y+4)+' Z" fill="#e6e6e6" stroke="#121212" stroke-width="1"/>')
      +'<text x="'+(x+(soft?6:9))+'" y="'+lblY(x+9,y+4,(hp.n+hp.el).length)+'" font-size="'+(soft?10:11)+'" fill="'+(soft?'#9aa4ad':'#c9d1d9')+'"'+(soft?' font-style="italic"':'')+' stroke="#121212" stroke-width="2.4" paint-order="stroke">'+esc(hp.n)+' '+esc(hp.el)+'</text></g>';
  }
  if(layers.mig) (HIST.mig||[]).forEach((m,i)=>{
    // a wave rises over its span, then stays as a faded record
    if(m.y0>year) return;
    const live=year<=m.y1;
    const grow=live?Math.max(0.18,(year-m.y0)/Math.max(1,m.y1-m.y0)):1;
    const [fx,fy]=XY(m.f[0],m.f[1]);
    let [x2,y2]=XY(m.t[0],m.t[1]);
    // the origin is usually far outside the frame, so the arrow enters
    // from that bearing at a readable length instead
    const ang=Math.atan2(fy-y2,fx-x2);
    // on a city map every wave lands on the same dot, so the heads stop
    // short of it and leave the city's own circle clear
    const gap=ST.migGap||0;
    x2+=Math.cos(ang)*gap; y2+=Math.sin(ang)*gap;
    const L=Math.min(Math.hypot(fx-x2,fy-y2), 0.24*Math.min(W,H));
    const cl=(v,hi)=>Math.max(12,Math.min(hi-12,v));
    const x1=cl(x2+Math.cos(ang)*L,W), y1=cl(y2+Math.sin(ang)*L,H);
    const w=(2+5*Math.max(0,Math.min(1,(Math.log10(m.p)-3.5)/3)))*grow;
    // a bowed path so overlapping waves stay apart
    const mx=(x1+x2)/2, my=(y1+y2)/2, dx=x2-x1, dy=y2-y1;
    const len=Math.hypot(dx,dy)||1, bow=(m.b||0.18)*0.6*len;
    const cx=mx-dy/len*bow, cy=my+dx/len*bow;
    const d='M'+x1.toFixed(1)+','+y1.toFixed(1)+' Q'+cx.toFixed(1)+','+cy.toFixed(1)+' '+x2.toFixed(1)+','+y2.toFixed(1);
    const op=live?0.9:0.42;
    s+='<g data-mig="'+i+'" style="cursor:pointer">'
      +'<path d="'+d+'" fill="none" stroke="#121212" stroke-opacity="'+(op*0.6)+'" stroke-width="'+(w+2)+'" stroke-linecap="round"/>'
      +'<path d="'+d+'" fill="none" stroke="#ffc247" stroke-opacity="'+op+'" stroke-width="'+w.toFixed(1)+'" stroke-linecap="round" marker-end="url(#migArrow)"/>'
      // the wave's own name, at the tail where the arrow comes in
      +'<text x="'+x1.toFixed(1)+'" y="'+lblY(x1,y1-7,m.n.length)+'" text-anchor="middle" font-size="9.5" fill="#ffc247" fill-opacity="'+(live?1:0.55)+'" stroke="#121212" stroke-width="2.6" paint-order="stroke">'+esc(m.n)+'</text>'
      +'</g>';
  });
  let anyCity=false;
  if(layers.tow) (HIST.cities||[]).forEach((c,i)=>{
    // bulk cities surface once the census finds 10,000 people
    const p=interp(c.pp,year); const R=cityR(p);
    if(!R) return;
    anyCity=true;
    const [x,y]=XY(c.lat,c.lon); const C=cityC(p);
    s+='<g data-ct="'+i+'" style="cursor:pointer">'
      +'<circle cx="'+x+'" cy="'+y+'" r="'+R.toFixed(1)+'" fill="'+C+'" fill-opacity="0.62" stroke="'+C+'" stroke-opacity="0.95" stroke-width="1"/>'
      +'<circle cx="'+x+'" cy="'+y+'" r="2.2" fill="var(--set)" stroke="#121212" stroke-width="0.8"/>'
      +(p>=25e4?'<text x="'+x+'" y="'+lblY(x,y-6-R,c.n.length)+'" text-anchor="middle" font-size="9.5" fill="#c9d1d9" stroke="#121212" stroke-width="2.2" paint-order="stroke">'+esc(c.n)+'</text>':'')
      +'</g>';
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
      if(R) anyCity=true;
      s+='<g data-ev="'+i+'" style="cursor:pointer">'
        +(R?'<circle cx="'+x+'" cy="'+y+'" r="'+R.toFixed(1)+'" fill="'+C+'" fill-opacity="0.62" stroke="'+C+'" stroke-opacity="0.95" stroke-width="1.2"/>':'')
        +(cap?'<path d="'+star(x,y,6)+'" fill="var(--cap)" stroke="#121212" stroke-width="1"/>'
             :'<circle cx="'+x+'" cy="'+y+'" r="3.6" fill="var(--set)" stroke="#121212" stroke-width="1"/>')
        +'<text x="'+x+'" y="'+lblY(x,y-8-(R||0),e.n.length)+'" text-anchor="middle" font-size="10.5" fill="'+(cap?'var(--cap)':'#c9d1d9')+'" stroke="#121212" stroke-width="2.4" paint-order="stroke">'+esc(e.n)+'</text></g>';
    }
  });
  if(layers.uni) (HIST.unis||[]).forEach((u,i)=>{
    // each institution appears in its founding year, a mortarboard
    if(u.y>year) return;
    const [x,y]=XY(u.lat,u.lon);
    const sc=u.mine?1.7:1, C=u.mine?'#ffd24d':'#c792ea';
    s+='<g data-uni="'+i+'" style="cursor:pointer">'
      +'<rect x="'+(x-3.2*sc).toFixed(1)+'" y="'+(y-3.2*sc).toFixed(1)+'" width="'+(6.4*sc).toFixed(1)+'" height="'+(6.4*sc).toFixed(1)+'" transform="rotate(45 '+x+' '+y+')" fill="'+C+'" stroke="#121212" stroke-width="1"/>'
      +'<line x1="'+(x+3.2*sc).toFixed(1)+'" y1="'+y+'" x2="'+(x+3.2*sc).toFixed(1)+'" y2="'+(y+6.5*sc).toFixed(1)+'" stroke="'+C+'" stroke-width="1.2"/>'
      +(u.mine?'<text x="'+x+'" y="'+lblY(x,y-9,u.mine.length)+'" text-anchor="middle" font-size="10.5" font-weight="700" fill="#ffd24d" stroke="#121212" stroke-width="2.4" paint-order="stroke">'+esc(u.mine)+'</text>':'')
      +'</g>';
  });
  // the key to the circles, once there is a circle to read
  if(layers.tow&&anyCity){
    const tiers=[[1e4,'10,000'],[1e5,'100,000'],[1e6,'1,000,000'],[1e7,'10,000,000']];
    const Rmax=cityR(1e7), cx=16+Rmax, by=H-14;
    s+='<g pointer-events="none" data-fixed="1">';
    s+='<text x="16" y="'+(by-2*Rmax-10)+'" font-size="10" fill="#8b949e" stroke="#121212" stroke-width="2.4" paint-order="stroke">City population</text>';
    // filled disks, largest painted first so each tier stays visible
    for(const [p] of [...tiers].reverse()){
      const r=cityR(p), C=cityC(p);
      s+='<circle cx="'+cx+'" cy="'+(by-r)+'" r="'+r.toFixed(1)+'" fill="'+C+'" fill-opacity="0.62" stroke="'+C+'" stroke-opacity="0.95" stroke-width="1"/>';
    }
    if(layers.hwy){
      const keys=['i','us','sr'], lx=cx+Rmax+96;
      let ly=by-2*Rmax-10;
      for(const k of keys){
        s+='<line x1="'+lx+'" y1="'+ly+'" x2="'+(lx+22)+'" y2="'+ly+'" stroke="'+RDC[k]+'" stroke-width="'+(k==='i'?2.8:k==='us'?2.0:1.35)+'"/>'
          +'<text x="'+(lx+27)+'" y="'+(ly+3)+'" font-size="9" fill="#8b949e" stroke="#121212" stroke-width="2.2" paint-order="stroke">'+RDN[k]+'</text>';
        ly+=12;
      }
    }
    for(const [p,lab] of tiers){
      const r=cityR(p), ty=by-2*r, C=cityC(p);
      s+='<line x1="'+cx+'" y1="'+ty+'" x2="'+(cx+Rmax+8)+'" y2="'+ty+'" stroke="#8b949e" stroke-opacity="0.55" stroke-width="0.7"/>'
        +'<text x="'+(cx+Rmax+11)+'" y="'+(ty+3)+'" font-size="9" fill="'+C+'" stroke="#121212" stroke-width="2.2" paint-order="stroke">'+lab+'</text>';
    }
    s+='</g>';
  }
  svg.innerHTML=s;
  fixZoom();
}
// a smooth closed blob through lon/lat vertices (Catmull-Rom to bezier)
function segLen(seg){
  let d=0;
  for(let i=1;i<seg.length;i++)
    d+=Math.hypot(seg[i][0]-seg[i-1][0], seg[i][1]-seg[i-1][1]);
  return d;
}
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

// ---- zoom: the wheel, the two buttons or the + and - keys close in on a
// point; a drag pans. The ground canvases scale with the view, while the
// names and the marks keep their size on screen. ----
let Z=1, VX=0, VY=0, zoomRaf=null, drag=null, dragged=false;
function fixZoom(){
  svg.classList.toggle('zoomed',Z>1);
  if(Z===1) return;
  const k=1/Z;
  // a point mark and its name shrink back together about the mark
  svg.querySelectorAll('[data-ev],[data-uni],[data-ct],[data-hp]').forEach(g=>{
    const m=g.firstElementChild; if(!m) return;
    const b=m.getBBox(), cx=b.x+b.width/2, cy=b.y+b.height/2;
    g.setAttribute('transform','matrix('+k+' 0 0 '+k+' '+(cx*(1-k)).toFixed(2)+' '+(cy*(1-k)).toFixed(2)+')');
  });
  // every other name keeps its type size
  svg.querySelectorAll('text').forEach(t=>{
    if(t.closest('[data-ev],[data-uni],[data-ct],[data-hp],[data-fixed]')) return;
    for(const a of ['font-size','stroke-width','letter-spacing']){
      const v=parseFloat(t.getAttribute(a)); if(v) t.setAttribute(a,(v*k).toFixed(2));
    }
  });
  // the keys stay where they are on the screen
  svg.querySelectorAll('[data-fixed]').forEach(g=>
    g.setAttribute('transform','translate('+VX.toFixed(1)+' '+VY.toFixed(1)+') scale('+k+')'));
}
function applyView(){
  const vw=W/Z, vh=H/Z;
  VX=Math.max(0,Math.min(W-vw,VX)); VY=Math.max(0,Math.min(H-vh,VY));
  svg.setAttribute('viewBox',VX+' '+VY+' '+vw+' '+vh);
  const tf=Z===1?'':'scale('+Z+') translate('+(-VX/W*100)+'%,'+(-VY/H*100)+'%)';
  for(const id of ['terC','wooC','watC']){ const c=document.getElementById(id); if(c) c.style.transform=tf; }
  render();
  document.getElementById('zOut').disabled=Z<=1.0001;
  document.getElementById('zIn').disabled=Z>=5.999;
  const a=document.getElementById('zCity');
  let near=false;
  if(CITY&&Z>=2.5){ const [x,y]=MXY(CITY.mx,CITY.my); near=x>=VX&&x<=VX+vw&&y>=VY&&y<=VY+vh; }
  if(CITY){ a.href=CITY.href; a.textContent=CITY.n+', up close →'; }
  a.hidden=!near;
}
// fx, fy: where in the view (0 to 1) the zoom is centered
function zoomTo(nz,fx,fy,glide){
  nz=Math.max(1,Math.min(6,nz));
  if(zoomRaf){ cancelAnimationFrame(zoomRaf); zoomRaf=null; }
  const px=VX+fx*W/Z, py=VY+fy*H/Z, z0=Z;
  const set=z=>{ Z=z; VX=px-fx*W/Z; VY=py-fy*H/Z; applyView(); };
  if(!glide||REDUCED){ set(nz); return; }
  const t0=performance.now(), dur=650;
  const step=t=>{ const u=Math.min(1,(t-t0)/dur), e=u<0.5?2*u*u:1-Math.pow(-2*u+2,2)/2;
    set(z0*Math.pow(nz/z0,e)); zoomRaf=u<1?requestAnimationFrame(step):null; };
  zoomRaf=requestAnimationFrame(step);
}
document.getElementById('zIn').onclick=()=>zoomTo(Z*2,0.5,0.5,true);
document.getElementById('zOut').onclick=()=>zoomTo(Z/2,0.5,0.5,true);
svg.addEventListener('wheel',e=>{
  // at the widest view, a scroll down belongs to the page
  if(Z<=1&&e.deltaY>0) return;
  e.preventDefault();
  const r=svg.getBoundingClientRect();
  zoomTo(Z*Math.exp(-e.deltaY*0.0015),(e.clientX-r.left)/r.width,(e.clientY-r.top)/r.height,false);
},{passive:false});
svg.addEventListener('pointerdown',e=>{
  if(Z<=1||e.button!==0) return;
  drag={x:e.clientX,y:e.clientY,vx:VX,vy:VY}; dragged=false;
});
window.addEventListener('pointermove',e=>{
  if(!drag) return;
  const dx=e.clientX-drag.x, dy=e.clientY-drag.y;
  if(!dragged&&Math.hypot(dx,dy)<4) return;
  dragged=true; svg.classList.add('panning');
  const r=svg.getBoundingClientRect();
  VX=drag.vx-dx/r.width*W/Z; VY=drag.vy-dy/r.height*H/Z; applyView();
});
window.addEventListener('pointerup',()=>{ drag=null; svg.classList.remove('panning'); });
// a drag is not a click on whatever it ended over
svg.addEventListener('click',e=>{ if(dragged){ e.stopPropagation(); dragged=false; } },true);
document.addEventListener('keydown',e=>{
  if(document.activeElement!==svg) return;
  if(e.key==='+'||e.key==='='){ zoomTo(Z*2,0.5,0.5,true); e.preventDefault(); }
  if(e.key==='-'||e.key==='_'){ zoomTo(Z/2,0.5,0.5,true); e.preventDefault(); }
  if(e.key==='0'){ zoomTo(1,0.5,0.5,true); e.preventDefault(); }
});

// ---- the ghost of another state ----
// Its outline comes in that page's own frame. It goes back to Mercator
// meters, is scaled by the ratio of the cosines of the two latitudes so
// that a kilometer there is a kilometer here, and is centered on this
// state. Latitude is taken at the middle of each state's frame.
const ghostCache={};
function ghostPath(code){
  if(ghostCache[code]) return ghostCache[code];
  const g=GHOST[code], [bx0,by0,bx1,by1]=g.m;
  const toM=([x,y])=>[bx0+x/g.W*(bx1-bx0), by1-y/g.H*(by1-by0)];
  const latOf=my=>(2*Math.atan(Math.exp(my/R))-Math.PI/2)/RAD;
  const k=Math.cos(latOf((by0+by1)/2)*RAD)/Math.cos(latOf((MY0+MY1)/2)*RAD);
  const bcx=(bx0+bx1)/2, bcy=(by0+by1)/2, acx=(MX0+MX1)/2, acy=(MY0+MY1)/2;
  const d=g.o.map(r=>'M'+r.map(p=>{ const [mx,my]=toM(p);
    const [x,y]=MXY(acx+(mx-bcx)*k, acy+(my-bcy)*k);
    return x.toFixed(1)+','+y.toFixed(1); }).join('L')+'Z').join('');
  ghostCache[code]=d; return d;
}
let ghostAnim=null;
function setGhost(code){
  const same=ghostSel===code;
  const from=ghostOp, to=same?0:1, next=same?null:code;
  if(!same) ghostSel=code;
  document.querySelectorAll('[data-ghost]').forEach(b=>b.classList.toggle('on',b.dataset.ghost===next));
  if(next){
    const g=GHOST[next];
    show('Another state, at the same ground scale', g.n+' over '+ST.name,
      g.n+' covers '+fmt(g.km2)+' km² against '+fmt(ST.km2||0)+' km² for '+ST.name
      +(ST.km2?', '+(g.km2/ST.km2*100).toFixed(g.km2/ST.km2<0.1?1:0)+'% of it.':'.')
      +' The outline is drawn to the same kilometer scale and centered here.',
      'Areas: US Census Bureau, 2020 gazetteer files (land and water)');
  }
  if(ghostAnim) cancelAnimationFrame(ghostAnim);
  if(REDUCED){ ghostOp=to; if(!next) ghostSel=null; render(); return; }
  const t0=performance.now(), dur=700;
  const step=t=>{
    const u=Math.min(1,(t-t0)/dur), e=u<0.5?2*u*u:1-Math.pow(-2*u+2,2)/2;
    ghostOp=from+(to-from)*e;
    render();
    if(u<1) ghostAnim=requestAnimationFrame(step);
    else { ghostAnim=null; if(!next) ghostSel=null; }
  };
  ghostAnim=requestAnimationFrame(step);
}
document.querySelectorAll('[data-ghost]').forEach(b=>b.onclick=()=>setGhost(b.dataset.ghost));

// ---- population and era readouts ----
const CEN=(HIST.early||[]).map(r=>[r[0],r[1],r[2]])
  .concat(HIST.census.map(r=>[r[0],r[1],'Census']))
  .sort((a,b)=>a[0]-b[0]);
// which kind of count the year sits in, so the readout can say so
function kindAt(y){
  let k=CEN.length?CEN[0][2]:'';
  for(const p of CEN){ if(p[0]<=y) k=p[2]; else break; }
  return k;
}
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
async function symbols(){
  const box=document.getElementById('symList');
  box.innerHTML=SYM.map((x,i)=>
    '<div class="sym"><div class="noimg" id="symImg'+i+'"></div>'
    +'<div class="b"><div class="k">'+esc(x.k)+'</div>'
    +'<div class="n">'+esc(x.n)+'</div>'
    +'<div class="sci">'+esc(x.b)+'</div>'
    +'<div class="y">Adopted '+x.y+'</div>'
    +'<div class="t">'+esc(x.t)+'</div>'
    +(x.s?'<div class="st">The statute says '+esc(x.s)+'.</div>':'')
    +'</div></div>').join('');
  for(let i=0;i<SYM.length;i++){
    const u=await flagUrl({a:SYM[i].a});
    const slot=document.getElementById('symImg'+i);
    if(!slot) continue;
    if(u){
      const img=new Image();
      img.alt=SYM[i].n; img.src=u;
      slot.replaceWith(img);
    }
  }
}

// the map and the readouts first; the flag arrives when the network does
let curEra=null;
function setYear(y){
  year=y;
  document.getElementById('yr').value=y;
  document.getElementById('yearTxt').textContent=y;
  document.getElementById('yearBig').textContent=y;
  const era=HIST.eras.find(e=>y>=e.y0&&y<e.y1)||HIST.eras[HIST.eras.length-1];
  document.getElementById('eraTxt').textContent=era.l;
  const cen=interp(CEN,y);
  const natLast=HIST.native.length?HIST.native[HIST.native.length-1][0]:0;
  const nat=y<=natLast?interp(HIST.native,y):null;
  let t=[];
  if(cen!=null) t.push('<span class="totG">'
    +esc(kindAt(y)+' (interpolated): '+fmt(cen))+'</span>');
  else t.push(esc('Before the counts: '+HIST.pre));
  if(nat!=null) t.push(esc('Native population (estimate): '+fmt(nat)));
  document.getElementById('popTxt').innerHTML=t.join('<br>');
  document.querySelectorAll('#ticks button').forEach(b=>b.classList.toggle('here',+b.textContent===y));
  render();
  sparkDot(y);
  if(era!==curEra){ curEra=era; flag(era); }
}
async function flag(era){
  const img=document.getElementById('flagImg'), none=document.getElementById('flagNone');
  const u=await flagUrl(era.f);
  if(era!==curEra) return;
  if(u){ img.src=u; img.style.display='block'; none.hidden=true; }
  else{ img.style.display='none'; none.hidden=false;
    none.textContent=era.f?'flag unavailable':'No flag: the nations’ own land'; }
}

// ---- the population under the slider ----
const SPAN=2025-1492;
function sparkSeries(){
  const cen=CEN.map(r=>[r[0],r[1]]).filter(r=>r[1]>0);
  const nat=(HIST.native||[]).map(r=>[r[0],r[1]]).filter(r=>r[1]>0);
  return {cen,nat};
}
let sparkY=null;
(function spark(){
  const box=document.getElementById('spark'); if(!box) return;
  const {cen,nat}=sparkSeries();
  const all=cen.concat(nat);
  if(all.length<2){ box.style.display='none'; return; }
  const vals=all.map(r=>Math.log10(r[1]));
  let lo=Math.floor(Math.min(...vals)), hi=Math.ceil(Math.max(...vals));
  if(hi-lo<1) hi=lo+1;
  const w=1000, h=62, pad=6;
  const X=y=>(y-1492)/SPAN*w, Y=v=>pad+(h-2*pad)*(1-(Math.log10(v)-lo)/(hi-lo));
  sparkY=Y;
  let s='<svg viewBox="0 0 '+w+' '+h+'" preserveAspectRatio="none">';
  const lab=p=>p>=6?(p===6?'1M':Math.pow(10,p-6)+'M'):p>=3?Math.pow(10,p-3)+'k':String(Math.pow(10,p));
  for(let p=lo;p<=hi;p++){
    const y=Y(Math.pow(10,p));
    s+='<line x1="0" y1="'+y.toFixed(1)+'" x2="'+w+'" y2="'+y.toFixed(1)+'" stroke="#2b2b2b" stroke-width="1" vector-effect="non-scaling-stroke"/>';
  }
  s+='</svg><svg viewBox="0 0 '+w+' '+h+'" preserveAspectRatio="none">';
  const line=(pts,color,dash)=>{
    if(pts.length<2) return '';
    return '<polyline points="'+pts.map(r=>X(r[0]).toFixed(1)+','+Y(r[1]).toFixed(1)).join(' ')+'" fill="none" stroke="'+color+'" stroke-width="1.8"'+(dash?' stroke-dasharray="5 4"':'')+' vector-effect="non-scaling-stroke" stroke-linejoin="round"/>';
  };
  s+=line(nat,'var(--nation)',true)+line(cen,'#0ca30c',false);
  s+='</svg>';
  // labels and the dot live in a third layer that keeps its aspect, so
  // text and the dot stay round and readable
  s+='<svg id="sparkTop" viewBox="0 0 '+w+' '+h+'" preserveAspectRatio="none">';
  s+='<line id="sparkLine" x1="0" y1="0" x2="0" y2="'+h+'" stroke="var(--accent)" stroke-opacity="0.6" stroke-width="1" vector-effect="non-scaling-stroke"/>';
  s+='</svg>';
  s+='<div id="sparkLab" style="position:absolute;left:4px;top:0;font-size:9.5px;color:var(--muted);line-height:1">'+lab(hi)+'</div>'
    +'<div style="position:absolute;left:4px;bottom:0;font-size:9.5px;color:var(--muted);line-height:1">'+lab(lo)+'</div>'
    +'<div id="sparkDot" style="position:absolute;width:9px;height:9px;border-radius:50%;background:#0ca30c;border:2px solid #121212;margin:-4.5px 0 0 -4.5px;display:none"></div>'
    +'<div id="sparkDot2" style="position:absolute;width:9px;height:9px;border-radius:50%;background:var(--nation);border:2px solid #121212;margin:-4.5px 0 0 -4.5px;display:none"></div>';
  box.innerHTML=s;
})();
function sparkDot(y){
  const box=document.getElementById('spark'); if(!box||!sparkY) return;
  const {cen,nat}=sparkSeries();
  const fx=(y-1492)/SPAN*100;
  const ln=document.getElementById('sparkLine');
  if(ln){ ln.setAttribute('x1',fx*10); ln.setAttribute('x2',fx*10); }
  const put=(id,pts)=>{
    const d=document.getElementById(id); if(!d) return;
    const v=(pts.length&&y>=pts[0][0]&&y<=pts[pts.length-1][0])?interp(pts,y):null;
    if(!v){ d.style.display='none'; return; }
    d.style.display='block'; d.style.left=fx+'%'; d.style.top=(sparkY(v)/62*100)+'%';
    d.title=fmt(v);
  };
  put('sparkDot',cen); put('sparkDot2',nat);
}

// ---- cards ----
function show(kind,name,body,src){
  document.getElementById('kindTxt').textContent=kind;
  const nm=document.getElementById('nameTxt');
  nm.textContent=name; nm.classList.remove('empty');
  document.getElementById('bodyTxt').textContent=body;
  document.getElementById('srcTxt').textContent=src||'';
}
function target(e){
  const g=e.target.closest('[data-nat],[data-ev],[data-ct],[data-uni],[data-rd],[data-mig],[data-cty],[data-hp],[data-lim],[data-fnd]');
  if(!g) return null;
  if(g.dataset.nat!==undefined){ const n=HIST.nations[+g.dataset.nat];
    return [n.kind||'A nation of this land',n.n,
      n.note+(n.after?' '+n.after.t.charAt(0).toUpperCase()+n.after.t.slice(1)+'.':'')
      +' The patch is an approximate homeland, drawn for orientation.'
      +(focusNat===+g.dataset.nat?' Pinned: the other homelands are dimmed until the pin is lifted.':''),
      n.src||'']; }
  if(g.dataset.ev!==undefined){ const ev=HIST.events[+g.dataset.ev];
    const k=ev.t==='rem'?'Removal and dispossession':ev.t==='cap'?'Capital · '+ev.y:'Settlement · '+ev.y;
    let body=ev.note;
    if(ev.pp){ const p=interp(ev.pp,year);
      if(p) body+=' Population around '+year+': '+fmt(p)+' (census, interpolated).'; }
    return [k,ev.n,body,ev.src]; }
  if(g.dataset.mig!==undefined){ const m=HIST.mig[+g.dataset.mig];
    return ['Migration · '+m.y0+' to '+m.y1, m.n,
      m.note+' Arrow width follows the size of the wave; the ends are '
      +'regions, not exact places.', m.src]; }
  if(g.dataset.rd!==undefined){ const r=ROADS[+g.dataset.rd];
    return [RDN[r.lv]+(r.y?' · '+r.y:''), r.n,
      (r.y?'First carried this number in '+r.y+'. ':'No designation year is documented for this route. ')
      +'The line is the route as it runs today, not the alignment of that year.',
      'Route history: the route’s Wikipedia article']; }
  if(g.dataset.uni!==undefined){ const u=HIST.unis[+g.dataset.uni];
    return ['College · founded '+u.y, u.n,
      (u.pub?'Public':'Private')+' institution, on the map from its founding year.'
      +(u.mine?' One of the author’s alma maters.':''),
      'en.wikipedia.org/wiki/'+u.n.replace(/ /g,'_')]; }
  if(g.dataset.ct!==undefined){ const c=HIST.cities[+g.dataset.ct];
    const p=interp(c.pp,year);
    return ['City · census', c.n,
      'Population around '+year+': '+fmt(p)+' (census, interpolated). '
      +'On the map from the first census over 10,000.',
      'Census series via the city’s Wikipedia article']; }
  if(g.dataset.cty!==undefined){ const c=ST.counties[+g.dataset.cty];
    return ['County · recent population',c.n,
      (c.y?'Established '+c.y+'. ':'')+'Population about '+fmt(c.p)+'.',
      'Founding year via Wikipedia’s county list; census figures via the Balsama county dataset, 2025']; }
  if(g.dataset.hp!==undefined){ const hp=HIST.geo.hp;
    return [hp.soft?'High ground':'Highest point',hp.n,'Elevation '+hp.el+'.','']; }
  if(g.dataset.lim!==undefined){
    return ['City limits',ST.limitsName||ST.name,'The incorporated city as it stands today, from the Census TIGER place file.','']; }
  if(g.dataset.fnd!==undefined){
    return ['The founding plat · '+ST.founded.y,ST.founded.n||ST.name,ST.founded.note||'The ground the town was first laid out on.',ST.founded.src||'']; }
  return null;
}
svg.addEventListener('pointerover',e=>{ if(pinned) return;
  const t=target(e); if(t) show(...t); });
svg.addEventListener('click',e=>{
  const g=e.target.closest('[data-nat],[data-ev],[data-ct],[data-uni],[data-rd],[data-mig],[data-cty],[data-hp],[data-lim],[data-fnd]');
  if(!g){ unpin(); return; }
  const id=g.dataset.nat!==undefined?'n'+g.dataset.nat:g.dataset.ev!==undefined?'e'+g.dataset.ev:g.dataset.ct!==undefined?'t'+g.dataset.ct:g.dataset.uni!==undefined?'u'+g.dataset.uni:g.dataset.rd!==undefined?'r'+g.dataset.rd:g.dataset.mig!==undefined?'m'+g.dataset.mig:g.dataset.cty!==undefined?'c'+g.dataset.cty:g.dataset.hp!==undefined?'hp':g.dataset.lim!==undefined?'lim':'fnd';
  pinned = pinned===id?null:id;
  // a pinned nation holds the stage: the others dim, and the slider then
  // shows its own patch fading at the year of its removal
  focusNat = (pinned&&g.dataset.nat!==undefined)?+g.dataset.nat:null;
  render();
  const t=target(e); if(t) show(...t);
});
function unpin(){ if(pinned===null&&focusNat===null) return; pinned=null; focusNat=null; render(); }
document.addEventListener('keydown',e=>{
  if(e.key==='Escape'){ unpin(); return; }
  // arrow keys move the year only while the map itself has focus
  if(document.activeElement!==svg) return;
  const st=e.shiftKey?10:1;
  if(e.key==='ArrowRight'||e.key==='ArrowUp'){ stop(); setYear(Math.min(2025,year+st)); e.preventDefault(); }
  if(e.key==='ArrowLeft'||e.key==='ArrowDown'){ stop(); setYear(Math.max(1492,year-st)); e.preventDefault(); }
  if(e.key===' '){ document.getElementById('bPlay').click(); e.preventDefault(); }
});

// ---- timeline ----
document.getElementById('yr').addEventListener('input',e=>{ stop(); setYear(+e.target.value); });
// Play runs on animation frames at a chosen number of years per second,
// and sprints at ten times that through the centuries before the first
// mark on the map, so the empty part of the rail passes in a few seconds
let raf=null, speed=10, lastT=null, acc=0, countiesAuto=false;
const FIRST=Math.min(...HIST.events.map(e=>e.y).concat(HIST.eras.filter(e=>e.y0>1492).map(e=>e.y0)).concat([2025]));
function stop(){ playing=false; document.getElementById('bPlay').textContent='Play';
  if(raf){ cancelAnimationFrame(raf); raf=null; } lastT=null; }
function frame(t){
  if(!playing) return;
  if(lastT==null) lastT=t;
  const dt=Math.min(0.25,(t-lastT)/1000); lastT=t;
  acc+=dt*speed*(year<FIRST?10:1);
  const step=Math.floor(acc);
  if(step>=1){
    acc-=step;
    const y=Math.min(2025, year<FIRST?Math.min(FIRST,year+step):year+step);
    // the county grid filling in by founding year is the best time effect
    // on the page, so the layer comes on by itself once the border exists
    if(!countiesAuto&&y>=HIST.border&&!layers.cou){ countiesAuto=true; document.getElementById('cCou').click(); }
    setYear(y);
    if(y>=2025){ stop(); return; }
  }
  raf=requestAnimationFrame(frame);
}
function play(){
  if(playing) return;
  playing=true; document.getElementById('bPlay').textContent='Pause';
  if(year>=2025){ countiesAuto=false; setYear(1492); }
  acc=0; lastT=null; raf=requestAnimationFrame(frame);
}
document.getElementById('bPlay').onclick=()=>{ if(playing) stop(); else play(); };
// a jump to a marked year glides there
let jumpRaf=null;
function goTo(y){
  stop(); if(jumpRaf){ cancelAnimationFrame(jumpRaf); jumpRaf=null; }
  if(REDUCED||Math.abs(y-year)<3){ setYear(y); return; }
  const y0=year, t0=performance.now(), dur=800;
  const step=t=>{
    const u=Math.min(1,(t-t0)/dur), e=u<0.5?2*u*u:1-Math.pow(-2*u+2,2)/2;
    setYear(Math.round(y0+(y-y0)*e));
    if(u<1) jumpRaf=requestAnimationFrame(step); else jumpRaf=null;
  };
  jumpRaf=requestAnimationFrame(step);
}
(function eband(){
  const eb=document.getElementById('eband'), span=2025-1492;
  const cols=['#3a3a3a','#7a6a2f','#2f5d7a','#7a2f2f','#2f7a4f','#50407a','#7a5a2f'];
  HIST.eras.forEach((e,i)=>{
    const d=document.createElement('div');
    d.style.left=((e.y0-1492)/span*100)+'%';
    d.style.width=((Math.min(e.y1,2025)-e.y0)/span*100)+'%';
    d.style.background=cols[i%cols.length]; d.title=e.y0+' · '+e.l;
    eb.appendChild(d);
  });
  HIST.events.forEach(ev=>{
    const m=document.createElement('span');
    m.style.left=((ev.y-1492)/span*100)+'%';
    m.style.background=ev.t==='rem'?'var(--rem)':ev.t==='cap'?'var(--cap)':'var(--set)';
    m.title=ev.y+' · '+ev.n;
    eb.appendChild(m);
  });
  // the key to the band and the population lines, and the speed of Play
  const key=document.getElementById('tlkey');
  const {cen,nat}=sparkSeries();
  key.innerHTML='<span><i style="background:var(--set)"></i>Settlement</span>'
    +'<span><i style="background:var(--cap)"></i>Capital</span>'
    +'<span><i style="background:var(--rem)"></i>Removal</span>'
    +'<span><i style="background:#555"></i>One color per era</span>'
    +(cen.length>1?'<span><i class="ln" style="background:#0ca30c"></i>Counted population, log scale</span>':'')
    +(nat.length>1?'<span><i class="ln" style="background:var(--nation)"></i>Native estimate</span>':'')
    +'<span class="spd"><span>Play</span>'
    +[10,30,100].map(v=>'<button data-spd="'+v+'"'+(v===10?' class="on"':'')+'>'+v+' yr/s</button>').join('')+'</span>';
  key.querySelectorAll('[data-spd]').forEach(b=>b.onclick=()=>{
    speed=+b.dataset.spd;
    key.querySelectorAll('[data-spd]').forEach(x=>x.classList.toggle('on',x===b));
  });
})();
// jump markers: each era boundary (statehood, transfers of power) is a
// clickable year above the slider
(function ticks(){
  const tk=document.getElementById('ticks'), span=2025-1492;
  // an era can begin in the year a mark falls on, and the two would
  // otherwise stack the same year twice on the rail
  const by=new Map();
  for(const p of HIST.eras.map(e=>({y:e.y0,l:e.l})).concat(HIST.marks||[])){
    if(p.y<=1492) continue;
    if(by.has(p.y)){
      const had=by.get(p.y);
      if(had.l.indexOf(p.l)<0) had.l+=' · '+p.l;
    } else by.set(p.y,{y:p.y,l:p.l});
  }
  const pts=[...by.values()].sort((a,b)=>a.y-b.y);
  const bs=pts.map(p=>{
    const b=document.createElement('button');
    b.style.left=((p.y-1492)/span*100)+'%';
    b.textContent=p.y;
    b.title=p.y+' · '+p.l;
    b.onclick=()=>goTo(p.y);
    tk.appendChild(b);
    return b;
  });
  // rows are assigned in pixels: a year takes the lowest row with room
  // for it, up to three rows, and a year that fits nowhere keeps only
  // its arrow, so nothing is ever printed over anything else
  const ROWS=3, RH=22, GAP=36;
  function layout(){
    const wpx=tk.clientWidth||1000;
    const last=[-1e9,-1e9,-1e9];
    let used=1;
    bs.forEach((b,i)=>{
      const x=(pts[i].y-1492)/span*wpx;
      let row=-1;
      for(let r=0;r<ROWS;r++) if(x-last[r]>=GAP){ row=r; break; }
      b.classList.toggle('hid',row<0);
      if(row<0) row=0; else { last[row]=x; used=Math.max(used,row+1); }
      b.dataset.row=row;
    });
    bs.forEach(b=>{ b.style.top=((used-1-(+b.dataset.row))*RH)+'px'; });
    tk.style.height=(used*RH+6)+'px';
  }
  layout();
  let rt=null;
  window.addEventListener('resize',()=>{ clearTimeout(rt); rt=setTimeout(layout,120); });
  window.__tickLayout=layout;
})();

// ---- chips ----
const CH={cTer:'ter',cWoo:'woo',cRiv:'riv',cLak:'lak',cCou:'cou',cNat:'nat',cTow:'tow',cUni:'uni',cHwy:'hwy',cMig:'mig'};
if(document.getElementById('cLim')) CH.cLim='lim';
for(const id in CH) document.getElementById(id).onclick=e=>{
  const k=CH[id]; layers[k]=!layers[k];
  e.target.classList.toggle('on',layers[k]);
  if(k==='ter'){ document.getElementById('terC').style.display=layers.ter?'':'none'; if(layers.ter) terrain(); }
  if(k==='woo'){ document.getElementById('wooC').style.display=layers.woo?'':'none'; if(layers.woo) woods(); }
  if(k==='lak'){ const w=document.getElementById('watC'); if(w) w.style.display=layers.lak?'':'none'; }
  render();
};

// ---- terrain: AWS Terrain Tiles (terrarium), shaded and tinted ----
// One hypsometric ramp for every map on the site: the color of a pixel
// is its height above the sea, not its rank within this frame.
const HYPS=[[0,47,79,55],[50,74,102,58],[200,122,133,69],
            [500,168,148,88],[1000,156,122,90],[2000,154,148,144],
            [3000,214,214,214],[4500,240,240,240]];
function hyps(e){
  if(e<=HYPS[0][0]) return HYPS[0].slice(1);
  for(let i=1;i<HYPS.length;i++){
    if(e<=HYPS[i][0]){
      const a=HYPS[i-1], b=HYPS[i], u=(e-a[0])/(b[0]-a[0]);
      return [a[1]+u*(b[1]-a[1]), a[2]+u*(b[2]-a[2]), a[3]+u*(b[3]-a[3])];
    }
  }
  return HYPS[HYPS.length-1].slice(1);
}
// done means painted: a fetch that fails leaves the flag down, so the
// chip can ask again
let terDone=false, wooDone=false, terBusy=false, wooBusy=false;
let terPainted=false, wooPainted=false;
const loadTxt=document.getElementById('loadTxt');
async function terrain(){
  if(terDone||terBusy) return; terBusy=true;
  const cv=document.getElementById('terC'); const SC=2;
  cv.width=W*SC; cv.height=Math.round(H*SC);
  const ctx=cv.getContext('2d');
  loadTxt.textContent='loading terrain…';
  try{
    const world=2*Math.PI*R;
    // a phone gets fewer, coarser tiles: the frame is small there anyway
    const cap=(window.innerWidth||1000)<700?36:80;
    let z=Math.round(Math.log2(world/(MX1-MX0)*(W*SC)/256)); z=Math.max(5,Math.min(11,z));
    let ts,tx0,tx1,ty0,ty1;
    for(;;){
      ts=world/(1<<z);
      tx0=Math.floor((MX0+world/2)/ts); tx1=Math.floor((MX1+world/2)/ts);
      ty0=Math.floor((world/2-MY1)/ts); ty1=Math.floor((world/2-MY0)/ts);
      if((tx1-tx0+1)*(ty1-ty0+1)<=cap||z<=5) break;
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
      // an absolute ramp, keyed to meters above the sea, so a flat town
      // and a mountain city are colored on the same scale
      const ex=elev[y2*px+Math.min(px-1,x+1)], ey=elev[Math.min(py-1,y2+1)*px+x];
      // flat ground carries almost no shading, so the relief gain rises
      // as the map's own range falls
      const gain=Math.max(0.012,Math.min(0.30,26/Math.max(20,emax-emin)));
      const sh=Math.max(0,Math.min(1,0.5+((ex-e)+(e-ey))*gain));
      const [r0,g0,b0]=hyps(e);
      o[i*4]=r0*(0.55+0.65*sh); o[i*4+1]=g0*(0.55+0.65*sh); o[i*4+2]=b0*(0.55+0.65*sh); o[i*4+3]=235;
    }
    octx.putImageData(out,0,0);
    const sx=(MX0+world/2)/ts-tx0, sy=(world/2-MY1)/ts-ty0;
    ctx.drawImage(off, sx*256, sy*256, (MX1-MX0)/ts*256, (MY1-MY0)/ts*256,
      0, 0, W*SC, Math.round(H*SC));
    loadTxt.textContent='';
    terDone=true; terPainted=true; render();
  }catch(e){ loadTxt.textContent='terrain unavailable'; }
  terBusy=false;
}
// ---- woods: USGS NLCD 2021 forest classes via the MRLC WMS ----
async function woods(){
  if(wooDone||wooBusy) return; wooBusy=true;
  const cv=document.getElementById('wooC'); const SC=2;
  cv.width=W*SC; cv.height=Math.round(H*SC);
  const ctx=cv.getContext('2d');
  loadTxt.textContent='loading land cover…';
  try{
    const u='https://www.mrlc.gov/geoserver/mrlc_display/NLCD_2021_Land_Cover_L48/wms'
      +'?service=WMS&version=1.1.1&request=GetMap&layers=NLCD_2021_Land_Cover_L48&styles='
      +'&bbox='+MX0+','+MY0+','+MX1+','+MY1+'&width='+(W*SC)+'&height='+Math.round(H*SC)
      +'&srs=EPSG:3857&format=image/png';
    const b=await createImageBitmap(await (await fetch(u)).blob());
    const off=new OffscreenCanvas(W*SC,Math.round(H*SC)), octx=off.getContext('2d');
    octx.drawImage(b,0,0);
    const img=octx.getImageData(0,0,off.width,off.height), d=img.data;
    // the same raster carries the water classes, which is the only
    // hydrography fine enough to show a city's own river
    const wimg=octx.createImageData(off.width,off.height), wd=wimg.data;
    const F=[[104,171,99],[28,99,48],[181,202,143]];
    const WA=[[70,107,159],[187,212,236],[108,159,184]];
    const near=(i,t)=>Math.abs(d[i]-t[0])<14&&Math.abs(d[i+1]-t[1])<14&&Math.abs(d[i+2]-t[2])<14;
    for(let i=0;i<d.length;i+=4){
      let wet=false;
      for(const t of WA) if(near(i,t)){ wet=true; break; }
      if(wet){ wd[i]=61; wd[i+1]=155; wd[i+2]=214; wd[i+3]=210; }
      let keep=false;
      for(const t of F) if(near(i,t)){ keep=true; break; }
      if(keep&&!wet){ d[i]=46; d[i+1]=140; d[i+2]=70; d[i+3]=185; }
      else d[i+3]=0;
    }
    octx.putImageData(img,0,0);
    ctx.drawImage(off,0,0);
    const wcv=document.getElementById('watC');
    if(wcv){
      wcv.width=W*SC; wcv.height=Math.round(H*SC);
      octx.putImageData(wimg,0,0);
      wcv.getContext('2d').drawImage(off,0,0);
      wcv.style.display=layers.lak?'':'none';
    }
    loadTxt.textContent='';
    wooDone=true; wooPainted=true; render();
  }catch(e){ loadTxt.textContent='land cover unavailable'; }
  wooBusy=false;
}

setYear(START);
symbols();
terrain(); woods();
// the page opens with the years already running, unless motion is turned
// down, in which case the slider waits
if(!REDUCED) play();
window.__state=()=>({year, start:START, playing, speed, layers:{...layers}, counties:ST.counties.length,
  rivers:ST.rivers.length, lakes:ST.lakes.length, nations:HIST.nations.length,
  events:HIST.events.length, eras:HIST.eras.length,
  visEvents:HIST.events.filter(e=>e.y<=year).length, pinned, focusNat, ghost:ghostSel, ghostOp,
  terDone, wooDone, terPainted, wooPainted, first:FIRST, zoom:Z, vx:VX, vy:VY,
  zCity:!document.getElementById('zCity').hidden,
  spark:!!document.querySelector('#spark svg'),
  tickRows:new Set([...document.querySelectorAll('#ticks button')].map(b=>b.dataset.row)).size,
  tickHidden:document.querySelectorAll('#ticks button.hid').length});
window.__goto=y=>{ stop(); setYear(y); };
</script>
</body>
</html>
"""

NOTE1 = ("The real state, with its terrain, woods, rivers, counties and roads, "
         "each a layer to switch. The slider runs from 1492: the nations first, "
         "then settlements, capitals and removals, with the flag of whoever "
         "claimed the land. These nations still exist; Native Land Digital maps "
         "their territories with their input.")
# the caption rule (September 2026): one caption; the map and its key carry the rest
NOTE2 = ""



METHOD = ("What the population line is made of, and where it is soft. Every "
          "state carries three series. The counts before the first federal "
          "census of that state are colonial or territorial enumerations, "
          "and each of them left Native people out by design: the "
          "California figures count gente de raz\u00f3n only, the Arizona "
          "figure covers the Gadsden strip and no further, and the "
          "territorial acts said Indians excepted in so many words. Two of "
          "them are known to be bad counts. The Nebraska census of 1854 was "
          "called a floating one at the time, since a number of those "
          "enumerated lived in Kansas. The Minnesota census of 1857 was "
          "taken to reach the population statehood needed, and seven "
          "counties in it were later found to have been filled with invented "
          "names. Both are on the line as published rather than corrected, "
          "because the correction is not known. Between two points the line "
          "is drawn straight, which is wrong wherever the change was sudden: "
          "California between 1845 and 1850 is the clearest case, since the "
          "gold rush happened inside that gap. The Native line is a "
          "different kind of number again. The early points are scholarly "
          "estimates with wide ranges, carried with whose estimate they are; "
          "the 2020 point is census self-identification, which counts a "
          "different thing, and the count of people reporting American "
          "Indian and Alaska Native alone or in combination with another "
          "race is substantially larger than the figure shown.")

SYMNOTE = ("About the living symbols. Each is the current designation, with "
           "the accepted binomial and, where the taxonomy has moved since "
           "adoption, the name the statute itself uses. Three are odder than "
           "they look. The California redwood is one symbol covering two "
           "species, because the 1937 act did not say which redwood and the "
           "1953 amendment settled it by adding the other. The Arizona palo "
           "verde is a genus rather than a species. The Nebraska goldenrod "
           "was adopted by an act of 1895 that names no species and was "
           "never written into the codified statutes, so its binomial is "
           "convention rather than law. The photographs come from Wikipedia "
           "when the page is opened.")


def refs_html(hist):
    rows = [
        ("https://www.naturalearthdata.com/",
         "Rivers, lakes and the road lines."),
        ("https://github.com/plotly/datasets",
         "County geometry, from the Census cartographic boundaries."),
        ("https://github.com/balsama/us_counties_data",
         "County populations."),
        ("https://registry.opendata.aws/terrain-tiles/",
         "The relief, shaded at view time and colored by height above the sea."),
        ("https://www.mrlc.gov/",
         "Woods and water, from the forest and water classes."),
        ("https://www.census.gov/data/tables/time-series/dec/popchange-data-text.html",
         "Decennial populations for the state."),
        ("https://en.wikipedia.org/wiki/List_of_United_States_counties_and_county_equivalents",
         "County founding years, from each state's list of counties."),
        ("https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population",
         "City census series, from each city's article. Every city over "
         "100,000 today is on the map."),
        ("https://en.wikipedia.org/wiki/Lists_of_American_universities_and_colleges",
         "Colleges, four-year public and private, with the founding year each "
         "list gives."),
        ("https://en.wikipedia.org/wiki/List_of_Interstate_Highways",
         "Highways: a route appears in the earliest year its article's infobox "
         "gives for that number, floored at the year its system began, 1926 "
         "for the US routes and 1956 for the Interstates. The line is today's "
         "route, not that year's alignment, and routes with no documented year "
         "are left off."),
        ("https://native-land.ca/",
         "The community map of Indigenous territories. The patches drawn here "
         "are rough approximations of documented homelands, not their data."),
        ("https://en.wikipedia.org/wiki/Native_Americans_in_the_United_States",
         "American Indian and Alaska Native population by state, 1880 to the "
         "2020 census. The 2020 point on the Native line comes from here."),
        ("https://en.wikipedia.org/wiki/Lists_of_United_States_state_symbols",
         "The living symbols, each traced to its own state's code: the "
         "California Government Code, Arizona Revised Statutes title 41, "
         "the Pennsylvania session laws, Massachusetts General Laws chapter "
         "2, the Code of Alabama title 1 chapter 2, Nebraska Revised "
         "Statutes chapter 90, and Minnesota Statutes chapter 1."),
    ]
    out = [apa.auto(u, ann) for u, ann in rows]
    out += [apa.entry(t, u) for t, u in hist.get("refs", [])]
    return apa.render(out)


# every city over 100,000 today, with its decennial census series
# (tools/data/cities.json, from each city's Wikipedia census table)
CITIES_ALL = json.loads((DATA.parent / "cities.json").read_text())


def norm(n):
    return n.lower().replace("saint ", "st. ").strip()


# accredited four-year institutions, public and private, with founding
# years (tools/data/universities.json, from each state's Wikipedia list)
UNIS_ALL = json.loads((DATA.parent / "universities.json").read_text())

# the author's alma maters get the gold mortarboard and a label
def mine_label(st, name):
    n = name.lower().replace("–", "-").replace("—", "-")
    if st == "pa" and ("franklin & marshall" in n or "franklin and marshall" in n):
        return "F&M"
    if st == "ma" and "massachusetts amherst" in n:
        return "UMass"
    if st == "al" and n.strip() == "university of alabama":
        return "UA"
    if st == "ne" and "nebraska-lincoln" in n:
        return "UNL"
    if st == "mn" and "st. olaf" in n:
        return "St. Olaf"
    return None


# migration waves: f and t are [lat, lon] region centers, p an order of
# magnitude for the people who moved, b the bow of the arrow
MIG = {
"ca": [
{
"y0": 1848,
"y1": 1855,
"n": "The Gold Rush",
"p": 300000,
"f": [
39.5,
-124.9
],
"t": [
38.8,
-120.9
],
"b": 0.2,
"note": "About 300,000 people reach California in seven years, by sea around the Horn and overland; San Francisco goes from a village to a city.",
"src": "en.wikipedia.org/wiki/California_gold_rush"
},
{
"y0": 1930,
"y1": 1940,
"n": "The Dust Bowl years",
"p": 400000,
"f": [
35.4,
-100.5
],
"t": [
36.7,
-119.8
],
"b": 0.16,
"note": "Drought and foreclosure push some 400,000 people out of Oklahoma, Texas, Arkansas and Kansas toward the San Joaquin Valley.",
"src": "en.wikipedia.org/wiki/Dust_Bowl"
},
{
"y0": 1940,
"y1": 1970,
"n": "The Second Great Migration",
"p": 1300000,
"f": [
32.3,
-92.0
],
"t": [
34.0,
-118.3
],
"b": -0.14,
"note": "Wartime shipyards and aircraft plants draw Black southerners west; Los Angeles and the Bay Area gain over a million people from the South.",
"src": "en.wikipedia.org/wiki/Second_Great_Migration_(African_American)"
},
{
"y0": 1965,
"y1": 2010,
"n": "Migration from Mexico and Central America",
"p": 4000000,
"f": [
25.5,
-108.5
],
"t": [
33.9,
-117.6
],
"b": 0.13,
"note": "After the 1965 immigration act and the 1980s farm crises, millions settle in California; by 2010 Mexican-born residents alone number above four million.",
"src": "en.wikipedia.org/wiki/Mexican_Americans_in_California"
},
{
"y0": 1975,
"y1": 1995,
"n": "Refugees from Southeast Asia",
"p": 450000,
"f": [
13.5,
-127.0
],
"t": [
37.4,
-121.9
],
"b": 0.2,
"note": "Vietnamese, Hmong, Cambodian and Lao refugees resettle in Orange County, San Jose and the Central Valley.",
"src": "en.wikipedia.org/wiki/Vietnamese_Americans"
}
],
"az": [
{
"y0": 1946,
"y1": 1990,
"n": "The Sun Belt years",
"p": 2500000,
"f": [
41.9,
-95.0
],
"t": [
33.5,
-112.1
],
"b": 0.15,
"note": "Air conditioning, defense plants and retirement draw people from the Midwest and Northeast; Phoenix grows from 65,000 to nearly a million.",
"src": "en.wikipedia.org/wiki/Sun_Belt"
},
{
"y0": 1942,
"y1": 1964,
"n": "The Bracero Program",
"p": 300000,
"f": [
27.5,
-107.0
],
"t": [
33.0,
-112.3
],
"b": -0.16,
"note": "Contract farm labor from Mexico works Arizona cotton and citrus; many families stay after the program ends.",
"src": "en.wikipedia.org/wiki/Bracero_Program"
},
{
"y0": 1990,
"y1": 2010,
"n": "Migration from Mexico",
"p": 500000,
"f": [
29.5,
-110.9
],
"t": [
33.4,
-111.9
],
"b": 0.14,
"note": "Arizona's Mexican-born population grows several times over as Phoenix and Tucson expand.",
"src": "en.wikipedia.org/wiki/Demographics_of_Arizona"
}
],
"pa": [
{
"y0": 1880,
"y1": 1920,
"n": "Southern and Eastern European arrivals",
"p": 1500000,
"f": [
46.5,
-70.0
],
"t": [
40.6,
-78.5
],
"b": 0.16,
"note": "Italians, Poles, Slovaks, Hungarians and Jews from the Russian Empire fill the steel towns, coal patches and Philadelphia wards.",
"src": "en.wikipedia.org/wiki/History_of_Pennsylvania"
},
{
"y0": 1916,
"y1": 1970,
"n": "The Great Migration",
"p": 700000,
"f": [
32.5,
-84.5
],
"t": [
39.95,
-75.16
],
"b": -0.15,
"note": "Black southerners leave the Jim Crow South for Philadelphia and Pittsburgh; Philadelphia's Black population multiplies several times over.",
"src": "en.wikipedia.org/wiki/Great_Migration_(African_American)"
},
{
"y0": 1683,
"y1": 1775,
"n": "Germans and the Scots-Irish",
"p": 110000,
"f": [
47.5,
-71.5
],
"t": [
40.3,
-76.3
],
"b": 0.13,
"note": "Penn's tolerance draws German-speaking sects to Lancaster and Berks and Ulster Scots to the frontier counties.",
"src": "en.wikipedia.org/wiki/Pennsylvania_Dutch"
}
],
"ma": [
{
"y0": 1845,
"y1": 1855,
"n": "The Irish famine years",
"p": 130000,
"f": [
47.5,
-70.5
],
"t": [
42.36,
-71.06
],
"b": 0.18,
"note": "Famine emigration lands tens of thousands in Boston in a decade; by 1855 the Irish-born are more than a quarter of the city.",
"src": "en.wikipedia.org/wiki/Irish_Americans_in_Boston"
},
{
"y0": 1880,
"y1": 1920,
"n": "Italians, Jews and Portuguese",
"p": 500000,
"f": [
45.5,
-69.5
],
"t": [
42.4,
-71.3
],
"b": 0.13,
"note": "The North End, Chelsea and the mill cities of Lowell, Lawrence and Fall River take in Southern and Eastern Europeans and Azorean Portuguese.",
"src": "en.wikipedia.org/wiki/History_of_Massachusetts"
},
{
"y0": 1950,
"y1": 1990,
"n": "Puerto Rican migration",
"p": 150000,
"f": [
24.5,
-70.5
],
"t": [
42.15,
-72.6
],
"b": -0.18,
"note": "Farm recruitment and factory work bring Puerto Rican families to Springfield, Holyoke and Boston.",
"src": "en.wikipedia.org/wiki/Puerto_Ricans_in_the_United_States"
}
],
"al": [
{
"y0": 1916,
"y1": 1970,
"n": "The Great Migration out of Alabama",
"p": 800000,
"f": [
33.0,
-86.8
],
"t": [
36.6,
-84.5
],
"b": 0.16,
"note": "Black Alabamians leave for Detroit, Chicago, Cleveland and the North; the state's Black share falls from 45 percent to 26 percent.",
"src": "en.wikipedia.org/wiki/Great_Migration_(African_American)"
},
{
"y0": 1817,
"y1": 1840,
"n": "Alabama Fever",
"p": 300000,
"f": [
35.5,
-81.0
],
"t": [
32.6,
-86.6
],
"b": -0.15,
"note": "Planters and enslaved people are moved west from the Carolinas, Georgia and Virginia onto land taken from the Muscogee.",
"src": "en.wikipedia.org/wiki/History_of_Alabama"
},
{
"y0": 1810,
"y1": 1860,
"n": "The domestic slave trade",
"p": 250000,
"f": [
37.0,
-78.0
],
"t": [
32.4,
-87.0
],
"b": 0.2,
"note": "Roughly a million people are sold from the Upper South to the cotton states; Alabama's Black Belt is one of the destinations.",
"src": "en.wikipedia.org/wiki/Slave_trade_in_the_United_States"
}
],
"ne": [
{
"y0": 1862,
"y1": 1900,
"n": "The Homestead Act",
"p": 400000,
"f": [
41.5,
-87.0
],
"t": [
41.3,
-99.5
],
"b": 0.15,
"note": "Free land and Union Pacific promotion bring settlers from the eastern states and from Europe onto the plains.",
"src": "en.wikipedia.org/wiki/Homestead_Acts"
},
{
"y0": 1870,
"y1": 1900,
"n": "Germans from Russia and Czechs",
"p": 100000,
"f": [
49.5,
-92.0
],
"t": [
40.9,
-97.6
],
"b": -0.16,
"note": "Volga German, Mennonite and Czech families take the drier western counties, bringing hard winter wheat with them.",
"src": "en.wikipedia.org/wiki/Germans_from_Russia"
},
{
"y0": 1990,
"y1": 2015,
"n": "Meatpacking towns",
"p": 90000,
"f": [
24.0,
-101.5
],
"t": [
41.0,
-97.4
],
"b": 0.14,
"note": "Plants in Lexington, Grand Island and Schuyler recruit workers from Mexico, Central America and later Somalia and Sudan.",
"src": "en.wikipedia.org/wiki/Demographics_of_Nebraska"
}
],
"mn": [
{
"y0": 1860,
"y1": 1900,
"n": "Scandinavians and Germans",
"p": 700000,
"f": [
49.5,
-88.0
],
"t": [
45.3,
-94.5
],
"b": 0.15,
"note": "Swedes, Norwegians and Germans take farms across the state; by 1900 a third of Minnesotans are foreign-born.",
"src": "en.wikipedia.org/wiki/History_of_Minnesota"
},
{
"y0": 1975,
"y1": 2005,
"n": "Hmong resettlement",
"p": 65000,
"f": [
19.0,
-100.0
],
"t": [
44.95,
-93.09
],
"b": -0.17,
"note": "After the war in Laos, Hmong refugees resettle in Saint Paul, now home to one of the largest Hmong communities anywhere.",
"src": "en.wikipedia.org/wiki/Hmong_Americans"
},
{
"y0": 1993,
"y1": 2015,
"n": "Somali arrival",
"p": 80000,
"f": [
22.0,
-88.0
],
"t": [
44.98,
-93.27
],
"b": 0.19,
"note": "Civil war brings Somali families to Minneapolis and later to Rochester and Saint Cloud.",
"src": "en.wikipedia.org/wiki/Somali_Americans"
}
]
}

for _st, _waves in MIG.items():
    HIST[_st]["mig"] = _waves

# the county of the city the author has lived in, drawn in gold
HOME_COUNTY = {
    "ca": "06037",   # Los Angeles
    "pa": "42071",   # Lancaster
    "ma": "25015",   # Hampshire (Amherst)
    "al": "01125",   # Tuscaloosa
    "ne": "31055",   # Douglas (Omaha)
    "mn": "27131",   # Rice (Northfield)
}

for st, fname in PAGES.items():
    data = json.loads((DATA / f"{st}.json").read_text())
    if st in HOME_COUNTY:
        data["home"] = HOME_COUNTY[st]
    data["km2"] = AREA_KM2[st]
    hist = HIST[st]
    bulk = CITIES_ALL.get(st, {})
    ev_by_name = {norm(e["n"]): e for e in hist["events"]}
    cities = []
    for cname, c in sorted(bulk.items()):
        ev = ev_by_name.get(norm(cname))
        if ev is not None:
            ev["pp"] = c["pp"]  # the fuller series replaces the sketch
            continue
        cities.append({"n": cname, "lat": c["lat"], "lon": c["lon"],
                       "pp": c["pp"]})
    hist["cities"] = cities
    unis = []
    for u in sorted(UNIS_ALL.get(st, []), key=lambda x: (x["y"], x["n"])):
        u = dict(u)
        lbl = mine_label(st, u["n"])
        if lbl:
            u["mine"] = lbl
        unis.append(u)
    hist["unis"] = unis
    roads_p = DATA / f"{st}_roads.json"
    roads = json.loads(roads_p.read_text()) if roads_p.exists() else []
    # only routes with a documented designation year take part
    roads = [r for r in roads if r.get("y")]
    roads.sort(key=lambda r: (r["y"], r["n"]))
    hist.pop("hwyAll", None)
    sibs = "".join(f' <a href="{f}">{n}</a>' for f, n in SIBLINGS if f != fname)
    city_js = "null"
    if st in CITY_PAGE:
        cf, cn = CITY_PAGE[st]
        sibs += f' &middot; <a href="{cf}">{cn}</a>'
        # the middle of the city page's own frame, where the zoom hands off
        cm = json.loads((DATA.parent / "cities" / CITY_FILE[cf]).read_text())["m"]
        city_js = json.dumps({"href": cf, "n": cn, "mx": round((cm[0] + cm[2]) / 2, 1),
                              "my": round((cm[1] + cm[3]) / 2, 1)})
    html = (HTML.replace("__APACSS__", apa.CSS)
            .replace("__TITLE__", data["name"])
            .replace("__SIBS__", sibs)
            .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2)
            .replace("__METHOD__", METHOD).replace("__SYMNOTE__", SYMNOTE)
            .replace("__REFS__", refs_html(hist))
            .replace("__ST__", json.dumps(data, separators=(",", ":")))
            .replace("__HIST__", json.dumps(hist, separators=(",", ":")))
            .replace("__ROADS__", json.dumps(roads, separators=(",", ":")))
            .replace("__SYM__", json.dumps(SYMBOLS[st], separators=(",", ":")))
            .replace("__GHOSTCHIPS__", ghost_chips(st))
            .replace("__GHOST__", json.dumps(ghosts(st), separators=(",", ":")))
            .replace("const CITY=null;", f"const CITY={city_js};"))
    (ROOT / fname).write_text(html, encoding="utf-8")
    print(f"wrote {ROOT / fname} ({len(html):,} B): "
          f"{len(hist['nations'])} nations, {len(hist['events'])} events, "
          f"{len(hist['eras'])} eras, {len(roads)} routes")
