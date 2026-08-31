#!/usr/bin/env python3
"""The hundred most cited science fiction novels, with their citation share.

The ranking is the Classics of Science Fiction database, which counts how
many published best-of lists, polls, award rosters and retrospective
anthologies name each book, and ranks by the share of the lists a book
was eligible for: a novel from 2013 cannot appear on a poll taken in
1988, so its denominator is smaller. Ranks 1 to 100 of their 139 are
taken here, as published.

Row: (rank, title, author, year, percent, cited, eligible, language)
The year is the one the database lists, which for a translated novel is
its first English edition; ORIGINAL below carries the first publication
where the two differ.
"""

BOOKS = [
    (1, "Dune", "Frank Herbert", 1965, 95, 39, 41, "en"),
    (2, "A Canticle for Leibowitz", "Walter M. Miller Jr.", 1959, 95, 37, 39, "en"),
    (3, "The Left Hand of Darkness", "Ursula K. Le Guin", 1969, 90, 43, 48, "en"),
    (4, "Childhood's End", "Arthur C. Clarke", 1953, 85, 33, 39, "en"),
    (5, "Nineteen Eighty-Four", "George Orwell", 1949, 83, 34, 41, "en"),
    (6, "The Martian Chronicles", "Ray Bradbury", 1950, 83, 33, 40, "en"),
    (7, "The Foundation Trilogy", "Isaac Asimov", 1951, 80, 32, 40, "en"),
    (8, "Neuromancer", "William Gibson", 1984, 79, 27, 34, "en"),
    (9, "The Stars My Destination", "Alfred Bester", 1957, 79, 30, 38, "en"),
    (10, "The Dispossessed", "Ursula K. Le Guin", 1974, 79, 37, 47, "en"),
    (11, "The Demolished Man", "Alfred Bester", 1953, 78, 31, 40, "en"),
    (12, "Ringworld", "Larry Niven", 1970, 78, 31, 40, "en"),
    (13, "Hyperion", "Dan Simmons", 1989, 77, 23, 30, "en"),
    (14, "The Man in the High Castle", "Philip K. Dick", 1962, 74, 29, 39, "en"),
    (15, "Ender's Game", "Orson Scott Card", 1985, 73, 24, 33, "en"),
    (16, "Stranger in a Strange Land", "Robert A. Heinlein", 1961, 73, 29, 40, "en"),
    (17, "Flowers for Algernon", "Daniel Keyes", 1966, 72, 28, 39, "en"),
    (18, "The Forever War", "Joe Haldeman", 1975, 72, 28, 39, "en"),
    (19, "Rendezvous with Rama", "Arthur C. Clarke", 1973, 71, 30, 42, "en"),
    (20, "Fahrenheit 451", "Ray Bradbury", 1953, 70, 28, 40, "en"),
    (21, "Red Mars", "Kim Stanley Robinson", 1992, 70, 21, 30, "en"),
    (22, "The Time Machine", "H. G. Wells", 1895, 70, 28, 40, "en"),
    (23, "Doomsday Book", "Connie Willis", 1992, 69, 27, 39, "en"),
    (24, "The Hitchhiker's Guide to the Galaxy", "Douglas Adams", 1979, 69, 22, 32, "en"),
    (25, "Gateway", "Frederik Pohl", 1977, 68, 26, 38, "en"),
    (26, "The Road", "Cormac McCarthy", 2006, 68, 13, 19, "en"),
    (27, "Brave New World", "Aldous Huxley", 1932, 68, 28, 41, "en"),
    (28, "Stand on Zanzibar", "John Brunner", 1968, 68, 27, 40, "en"),
    (29, "The War of the Worlds", "H. G. Wells", 1898, 68, 27, 40, "en"),
    (30, "More Than Human", "Theodore Sturgeon", 1953, 67, 26, 39, "en"),
    (31, "Snow Crash", "Neal Stephenson", 1992, 67, 18, 27, "en"),
    (32, "Lord of Light", "Roger Zelazny", 1967, 66, 25, 38, "en"),
    (33, "The Book of the New Sun", "Gene Wolfe", 1980, 66, 23, 35, "en"),
    (34, "A Fire Upon the Deep", "Vernor Vinge", 1992, 66, 19, 29, "en"),
    (35, "The Handmaid's Tale", "Margaret Atwood", 1985, 65, 26, 40, "en"),
    (36, "The Moon Is a Harsh Mistress", "Robert A. Heinlein", 1966, 65, 26, 40, "en"),
    (37, "Starship Troopers", "Robert A. Heinlein", 1959, 64, 25, 39, "en"),
    (38, "The Windup Girl", "Paolo Bacigalupi", 2009, 64, 14, 22, "en"),
    (39, "Frankenstein", "Mary Shelley", 1818, 62, 28, 45, "en"),
    (40, "Solaris", "Stanisław Lem", 1970, 62, 23, 37, "pl"),
    (41, "Do Androids Dream of Electric Sheep?", "Philip K. Dick", 1968, 59, 22, 37, "en"),
    (42, "The Diamond Age", "Neal Stephenson", 1995, 59, 17, 29, "en"),
    (43, "A Clockwork Orange", "Anthony Burgess", 1962, 58, 22, 38, "en"),
    (44, "Way Station", "Clifford D. Simak", 1963, 56, 22, 39, "en"),
    (45, "Earth Abides", "George R. Stewart", 1949, 56, 23, 41, "en"),
    (46, "Timescape", "Gregory Benford", 1980, 54, 19, 35, "en"),
    (47, "The Hunger Games", "Suzanne Collins", 2008, 54, 13, 24, "en"),
    (48, "Mission of Gravity", "Hal Clement", 1954, 54, 21, 39, "en"),
    (49, "The Female Man", "Joanna Russ", 1975, 53, 23, 43, "en"),
    (50, "Old Man's War", "John Scalzi", 2005, 53, 10, 19, "en"),
    (51, "City", "Clifford D. Simak", 1952, 53, 21, 40, "en"),
    (52, "Startide Rising", "David Brin", 1983, 51, 18, 35, "en"),
    (53, "Ubik", "Philip K. Dick", 1969, 51, 19, 37, "en"),
    (54, "The City and the Stars", "Arthur C. Clarke", 1956, 51, 20, 39, "en"),
    (55, "Last and First Men", "Olaf Stapledon", 1930, 51, 21, 41, "en"),
    (56, "Ancillary Justice", "Ann Leckie", 2013, 50, 11, 22, "en"),
    (57, "The Sparrow", "Mary Doria Russell", 1996, 50, 19, 38, "en"),
    (58, "To Your Scattered Bodies Go", "Philip José Farmer", 1971, 50, 19, 38, "en"),
    (59, "A Case of Conscience", "James Blish", 1958, 49, 19, 39, "en"),
    (60, "The Space Merchants", "Frederik Pohl and C. M. Kornbluth", 1953, 49, 19, 39, "en"),
    (61, "The Day of the Triffids", "John Wyndham", 1951, 48, 19, 40, "en"),
    (62, "The Gods Themselves", "Isaac Asimov", 1972, 48, 19, 40, "en"),
    (63, "I, Robot", "Isaac Asimov", 1950, 48, 19, 40, "en"),
    (64, "Cat's Cradle", "Kurt Vonnegut", 1963, 47, 18, 38, "en"),
    (65, "The Sirens of Titan", "Kurt Vonnegut", 1959, 47, 18, 38, "en"),
    (66, "A Deepness in the Sky", "Vernor Vinge", 1999, 46, 12, 26, "en"),
    (67, "2001: A Space Odyssey", "Arthur C. Clarke", 1968, 46, 17, 37, "en"),
    (68, "Slaughterhouse-Five", "Kurt Vonnegut", 1969, 46, 17, 37, "en"),
    (69, "Speaker for the Dead", "Orson Scott Card", 1986, 45, 15, 33, "en"),
    (70, "A Princess of Mars", "Edgar Rice Burroughs", 1917, 44, 18, 41, "en"),
    (71, "Star Maker", "Olaf Stapledon", 1937, 44, 18, 41, "en"),
    (72, "The Caves of Steel", "Isaac Asimov", 1954, 44, 17, 39, "en"),
    (73, "Dying Inside", "Robert Silverberg", 1972, 43, 16, 37, "en"),
    (74, "Cyteen", "C. J. Cherryh", 1988, 42, 16, 38, "en"),
    (75, "Altered Carbon", "Richard K. Morgan", 2002, 42, 10, 24, "en"),
    (76, "Dhalgren", "Samuel R. Delany", 1975, 42, 15, 36, "en"),
    (77, "The Player of Games", "Iain M. Banks", 1988, 41, 11, 27, "en"),
    (78, "The Mote in God's Eye", "Larry Niven and Jerry Pournelle", 1974, 41, 15, 37, "en"),
    (79, "Blood Music", "Greg Bear", 1985, 40, 12, 30, "en"),
    (80, "The Fall of Hyperion", "Dan Simmons", 1990, 40, 12, 30, "en"),
    (81, "Twenty Thousand Leagues Under the Seas", "Jules Verne", 1870, 40, 16, 40, "fr"),
    (82, "A Wrinkle in Time", "Madeleine L'Engle", 1962, 39, 17, 44, "en"),
    (83, "Babel-17", "Samuel R. Delany", 1966, 38, 15, 39, "en"),
    (84, "Consider Phlebas", "Iain M. Banks", 1987, 38, 11, 29, "en"),
    (85, "The Drowned World", "J. G. Ballard", 1962, 37, 14, 38, "en"),
    (86, "We", "Yevgeny Zamyatin", 1924, 37, 15, 41, "ru"),
    (87, "Downbelow Station", "C. J. Cherryh", 1981, 36, 14, 39, "en"),
    (88, "Slan", "A. E. van Vogt", 1946, 36, 15, 42, "en"),
    (89, "The Time Traveler's Wife", "Audrey Niffenegger", 2003, 36, 10, 28, "en"),
    (90, "Grass", "Sheri S. Tepper", 1989, 35, 12, 34, "en"),
    (91, "China Mountain Zhang", "Maureen F. McHugh", 1992, 35, 13, 37, "en"),
    (92, "Roadside Picnic", "Arkady and Boris Strugatsky", 1972, 35, 13, 37, "ru"),
    (93, "Tau Zero", "Poul Anderson", 1970, 35, 13, 37, "en"),
    (94, "Barrayar", "Lois McMaster Bujold", 1991, 34, 13, 38, "en"),
    (95, "The Snow Queen", "Joan D. Vinge", 1980, 34, 14, 41, "en"),
    (96, "No Enemy But Time", "Michael Bishop", 1982, 33, 11, 33, "en"),
    (97, "Double Star", "Robert A. Heinlein", 1956, 33, 13, 40, "en"),
    (98, "The Island of Doctor Moreau", "H. G. Wells", 1896, 33, 13, 40, "en"),
    (99, "Journey to the Centre of the Earth", "Jules Verne", 1864, 33, 13, 40, "fr"),
    (100, "Ammonite", "Nicola Griffith", 1993, 32, 12, 37, "en"),
]

LANGS = {"en": ("English", "#58a6ff"), "fr": ("French", "#31d67a"),
         "pl": ("Polish", "#ffb02e"), "ru": ("Russian", "#ef5350")}

# where the database's year is a later edition or a translation
ORIGINAL = {
    "Solaris": "First published in Polish in 1961; the 1970 English text "
               "came through a French translation, and a direct one waited "
               "until 2011.",
    "We": "Written in Russian in 1920 and 1921, first published in this "
          "English translation in New York in 1924. The Russian text "
          "appeared in New York in 1952 and in the Soviet Union in 1988.",
    "A Princess of Mars": "Serialized in 1912 as Under the Moons of Mars; "
                          "the book followed in 1917.",
    "The Foundation Trilogy": "The three books came out between 1951 and "
                              "1953, from stories written in the 1940s.",
    "The Book of the New Sun": "Four volumes between 1980 and 1983, with a "
                               "coda in 1987.",
    "Twenty Thousand Leagues Under the Seas": "Serialized in French from "
                                              "1869; the book followed in "
                                              "1870.",
    "Roadside Picnic": "Published in Russian in 1972; the first English "
                       "translation came in 1977.",
    "Journey to the Centre of the Earth": "Published in French in 1864 and "
                                          "revised by Verne in 1867.",
}
