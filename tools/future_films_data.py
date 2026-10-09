"""Stories set in the future, placed at the years they are set.

Each entry: (title, medium, start, end, made, note, flags)

  medium  film, series, book or game
  start   the first story year; end the last, or None for a single year
  made    year of first release or first publication
  note    how the date is known, kept short
  flags   "~" the start is an estimate; "~end" the end is an estimate;
          "on" the story runs on past the last year drawn;
          "span" an estimate that covers a whole decade or century, drawn
          dashed from start to end; "alt=a-b" a second dating the work
          itself gives, drawn faint

The list of works, their story years and the notes on dating were supplied
with the request for this page. Release and publication years are the first
theatrical release, first broadcast, first game release or first publication
in book form.
"""

FUTURES = [
    ("The Martian Chronicles", "book", 1999, 2026, 1950,
     "Dated 1999 to 2026 in the original 1950 edition; the 1997 edition moved it to 2030 to 2057.",
     "alt=2030-2057"),
    ("The Three-Body Problem", "book", 2007, None, 2008,
     "The Crisis Era begins; the trilogy then runs centuries ahead and beyond.", "~ on"),
    ("District 9", "film", 2010, None, 2009,
     "The ship arrived over Johannesburg in 1982.", ""),
    ("Chappie", "film", 2016, None, 2015, "", ""),
    ("Blade Runner", "film", 2019, None, 1982, "November 2019, Los Angeles.", ""),
    ("Akira", "film", 2019, None, 1988, "Neo-Tokyo, 31 years after the 1988 blast.", "~"),
    ("Edge of Tomorrow", "film", 2020, None, 2014,
     "Estimated; the invasion began five years earlier.", "~"),
    ("Red Mars", "book", 2026, 2061, 1992,
     "The First Hundred launch in 2026; it ends with the first revolution.", ""),
    ("Children of Men", "film", 2027, None, 2006, "", ""),
    ("Ghost in the Shell", "film", 2029, None, 1995, "The 1995 film.", ""),
    ("The Martian", "film", 2035, None, 2015,
     "The Ares III mission, by the book's timeline; the film gives no year.", ""),
    ("Moon", "film", 2035, None, 2009, "Estimated; the film gives no year.", "~"),
    ("Blade Runner 2049", "film", 2049, None, 2017, "", ""),
    ("Ad Astra", "film", 2050, 2059, 2019,
     "The 2050s at a guess: the opening card says only “the near future.”", "~ span"),
    ("Sunshine", "film", 2057, None, 2007, "", ""),
    ("Green Mars", "book", 2061, 2127, 1993, "It ends with the second revolution.", ""),
    ("Cowboy Bebop", "series", 2071, None, 1998, "The Gate accident was in 2021.", ""),
    ("The Moon Is a Harsh Mistress", "book", 2075, 2076, 1966, "The lunar revolution.", ""),
    ("Memories: Magnetic Rose", "film", 2092, None, 1995, "", ""),
    ("Prometheus", "film", 2093, None, 2012,
     "Launched in 2091, it reaches LV-223 in December 2093.", ""),
    ("Ender's Game", "film", 2100, 2199, 2013,
     "The 22nd century, by the series material; the film gives no year.", "~ span"),
    ("Alien: Covenant", "film", 2104, None, 2017, "", ""),
    ("Alien", "film", 2122, None, 1979, "", ""),
    ("Blue Mars", "book", 2127, 2212, 1996, "", "~end"),
    ("Cloud Atlas: Neo Seoul", "film", 2144, None, 2012,
     "The Sonmi section, by the film's dating.", "~"),
    ("Elysium", "film", 2154, None, 2013, "", ""),
    ("Blue Remembered Earth", "book", 2162, None, 2012,
     "Reynolds: an Africa-led solar system, a post-scarcity society under surveillance.", ""),
    ("Aliens", "film", 2179, None, 1986, "57 years after Alien.", ""),
    ("Mass Effect", "game", 2183, 2186, 2007, "The trilogy.", ""),
    ("Mars Express", "film", 2200, None, 2023, "", ""),
    ("Starship Troopers", "film", 2200, 2299, 1997,
     "The 23rd century, by tie-in material; the film gives no year.", "~ span"),
    ("Scavengers Reign", "series", 2300, 2399, 2023,
     "A guess: interstellar freight and cryosleep, and nothing on screen dates it.", "~ span on"),
    ("2312", "book", 2312, None, 2012,
     "Robinson: a fully settled solar system, Terminator rolling around Mercury, hollowed-asteroid terraria.", ""),
    ("Cloud Atlas: Sloosha's Crossin'", "film", 2321, None, 2012,
     "Hawaii after the Fall, by the film's dating.", "~"),
    ("The Expanse", "series", 2350, None, 2015,
     "The authors' estimate; never stated on screen.", "~"),
    ("Dead Space", "game", 2508, None, 2008, "The USG Ishimura incident.", ""),
    ("Alita: Battle Angel", "film", 2563, None, 2019, "The Fall was in 2263.", ""),
]
