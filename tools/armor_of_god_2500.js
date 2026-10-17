//@@ BODIES
  // Two more bodies in the belt for the Armor of God diagram, drawn like
  // Ceres and Vesta. Figures: Wikipedia's summaries of the published
  // measurements (Psyche's shape from radar and adaptive optics; Hygiea's
  // from VLT/SPHERE, Vernazza and others, 2019); the Psyche mission's
  // schedule from NASA.
  const PSYCHE = {
    name: "Psyche", type: "Asteroid, the largest metal-rich one known", au: 2.924, rKm: 111,
    lenR: 4 * 111 / 469.7, small: true, flat: 171 / 278,
    day: "4 h 12 min",
    year: "5.0 Earth years",
    diam: "About 222 km on average: 278 by 238 by 171 km, lumpy and flattened",
    area: "About 1.6 × 10<sup>5</sup> km², about the area of Tunisia",
    mass: "2.29 × 10<sup>19</sup> kg, 0.03% of the Moon and about a hundredth of the whole belt",
    moons: "0",
    made: "Rock rich in metal. Its density, about 4 g/cm³, and the way it reflects radar point to iron-nickel mixed with silicate rock. It may be part of the core of a planet that broke apart early, which is what the Psyche spacecraft is going to test",
    disc: "Annibale de Gasparis, March 17, 1852, at Naples. The sixteenth asteroid found",
    probe: "NASA's Psyche, launched October 13, 2023. It passed Mars on May 15, 2026 and is due to reach Psyche in August 2029"
  };
  const HYGIEA = {
    name: "Hygiea", type: "Asteroid, the fourth largest in the belt", au: 3.142, rKm: 216.5,
    lenR: 4 * 216.5 / 469.7, small: true, flat: 424 / 450,
    labels: { extra: "Why it may be a dwarf planet" },
    day: "13 h 50 min",
    year: "5.6 Earth years",
    diam: "About 433 km on average: 450 by 430 by 424 km, nearly round",
    area: "About 5.9 × 10<sup>5</sup> km², about the area of Madagascar",
    mass: "8.7 × 10<sup>19</sup> kg, 0.12% of the Moon and about 4% of the whole belt",
    moons: "0",
    made: "Dark rock rich in carbon and water-bearing minerals, like the carbonaceous chondrite meteorites",
    extra: "Images from the Very Large Telescope showed it nearly round, which would make it the smallest dwarf planet. It has not been classified as one",
    disc: "Annibale de Gasparis, April 12, 1849, at Naples. The tenth asteroid found",
    probe: "None. No spacecraft has visited it"
  };
//@@ LAYER
  // This page ends at the Kuiper belt. The far bodies keep their places in the
  // layout, which the Library diagram's code uses, but leave the lists that
  // are drawn, clicked and named.
  for (const b of [ERIS, SEDNA]) SMALL.splice(SMALL.indexOf(b), 1);
  REGIONS.splice(REGIONS.indexOf(OORT), 1);

  // ---------- Armor of God, 2500 ----------
  // How things stand in the novel's solar system in the year 2500: who holds
  // each place, who lives there, and who controls what it yields. Everything
  // in this block belongs to the book, not to the real solar system.
  const AOG_HOLD = {
    l5:    { name: "The United Reaches", color: "#e9b949" },
    ind:   { name: "Independent", color: "#5fcf8f" },
    tied:  { name: "Tied to the US-led bloc", color: "#b493ff" },
    earth: { name: "Held from Earth", color: "#ef7a6d" },
    none:  { name: "No one, or a treaty", color: "#cfd6e0" }
  };
  // place: [name, where, people, what it does, what it is short of]
  const AOG = {
    "Mercury": {
      held: [["ind", "Shuixing, with the Sun-zone states"], ["l5", "Caloris"]],
      people: "About 8,000",
      places: [["Shuixing", "the north pole, in the ice of the polar craters", "3,000", "Ice, science, radiation research"],
               ["Caloris", "the south pole", "5,000", "Ice, science, radiation research"]],
      notes: ["The rest of Mercury is untouched"]
    },
    "Venus": {
      held: [["ind", "Independent Venus"]],
      people: "12 million, in cities that float in the clouds",
      places: [["Vostok", "53 km up, a raft 20 km across; the capital", "5 million", "Government, finance, the Venus Net, chemicals", "Metal, ground"],
               ["Zarya", "52 km up, a raft 9 km across", "3 million", "Carbon from the air, sulfuric acid, chemicals, cloud farming under sunlight twice Earth's", "Metal, water, ground"],
               ["Mirny", "51 km up", "800,000", "Acid, salvage; the fiber barons' palaces are museums", "Work"]],
      res: [["Carbon and acid", "the Cloud Houses, old Venus families"],
            ["Carbon fiber", "undercut by Jupiter's; the barons are ruined"]]
    },
    "Earth": {
      held: [["l5", "Armstrong, the capital, and its Prairie pair in high orbit; L5: the Pearl, Lagrange and two Prairie pairs"],
             ["ind", "L4: Penglai and Yongle, the Yongle Republic"],
             ["none", "The elevator and Cumbre, by treaty"],
             ["earth", "The Roads in low orbit, under a dozen flags; the Earth below"]],
      people: "About 6 billion on Earth, and falling; more than 200 million in the space between Earth and the Moon",
      places: [["The Roads", "low orbit, 400 to 600 km up; about 60 spin stations", "300,000", "Shipyards, repair, orbital manufacturing, transit between Earth and everything above", "Room, safety from debris"],
               ["The elevator", "from the equator at Quito to the Counterweight, 100,000 km up", "", "Cumbre, its dock, at 35,786 km"],
               ["Cumbre", "the elevator's geostationary dock, 35,786 km up", "200,000", "Cargo transfer, customs, tolls, warehousing; a week's climb from the ground"],
               ["Armstrong", "a cored world 116,000 km out, above the Counterweight, going round six times a lunar month; the capital of the United Reaches", "12 million", "10 km across, 24 decks, 6,700 km² of ground. Government, courts, finance, the largest rectenna array in the system", "Housing on the upper decks"],
               ["Lowell", "Armstrong's Decks 1 to 10", "", "Aluminum rolling mills, steel fabrication, chemicals, shipyards, suit factories, League food", "Daylight, wires, union rights"],
               ["The Kranz Flight Academy", "a district on Armstrong's Decks 22 to 24", "", "Flight training"],
               ["The Garrison", "Armstrong's far side", "", "The Navy"],
               ["The Pearl", "a cored world at L5, 60° behind the Moon; the mother world", "180 million", "15 km across, 36 decks, 22,300 km² of ground. The seat of the Assembly of Worlds, on the Common. Everything: medicine, food, banking, shipbuilding, the Net's largest market, the arts", "Room on the best decks; the deep decks are crowded and dim"],
               ["Lagrange", "the old spin stations at L5, beside the Pearl", "900,000", "The oldest families: old money, shipwrights"],
               ["Penglai", "a cored world at L4, 60° ahead of the Moon; the Yongle Republic's world", "14 million", "7 km across, 17 decks, 2,300 km² of ground: the smallest world and the best used. Shipyards, Belt trade finance, government", "Water, nitrogen, allies"],
               ["Yongle", "L4, beside Penglai", "", "China's first great spin station"],
               ["The Prairies", "six farm cylinders in three pairs: one pair near Armstrong, two near the Pearl", "50,000 each", "Each 8 km wide and 32 km long, with about 400 km² of land. Four grow crops at half a gravity; two raise flocks at one", "Phosphorus, nitrogen"],
               ["Quito", "on the ground, on the equator", "", "The elevator's capital and the richest city on Earth's surface"]],
      res: [["Power", "the Current, caught by rectenna arrays in orbit"],
            ["Xenon", "Earth's Xenon Council, Earth's strongest lever over space"],
            ["Food", "League farms up the elevator, and more every year from the Prairies (Meridian Foods, United Reaches)"],
            ["Medicine", "Rhine Orbital (EU) in low orbit; Halcyon (United Reaches) on the Pearl"],
            ["Banking", "Wexley Express (United Reaches)"],
            ["The elevator", "owned by treaty; the Latin American League owns its ground half"],
            ["What the machines left", "the Agency, a government body, licenses all salvage"]],
      notes: ["The Moon, L4 and L5 go round Earth together once a month",
              "The three cored worlds, Armstrong, Penglai and the Pearl, have 77 decks and 31,300 km² of ground near one gravity. Their cores weigh 3.2, 1.6 and 7.2 × 10¹⁸ kg, together about half the mass of Psyche"]
    },
    "Mars": {
      held: [["l5", "The United Reaches, Phobos included"]],
      people: "3.5 million",
      places: [["Gateway", "Mars orbit: spin stations, with the Gateway Preparatory School; the largest city at Mars", "2 million", "Outfitting for the Belt, the Lines, shipyards, propellant works"],
               ["Mangala", "Hellas basin, domed and buried", "300,000", "Farming under glass, argon from the air, water ice", "Shielding, nitrogen, full gravity"],
               ["Dwarka", "inside Phobos, which is hollowed out", "400,000", "Port, customs, fuel from Martian water, the Lines' Mars junction", "Room"]],
      res: [["Propellant", "Delmont Chemical (United Reaches), at Gateway"]]
    },
    "Asteroid Belt": {
      held: [["l5", "Ceres, Psyche and the inner Belt"], ["ind", "Vesta"], ["tied", "The outer Belt"]],
      people: "About 11 million",
      places: [["Piazzi", "Ceres; the capital of the Belt", "2.5 million"],
               ["Kaap", "Vesta", "1.8 million"],
               ["Tianfu", "Ceres", "600,000"],
               ["Albion", "Hygiea; the capital of the outer Belt", "500,000"],
               ["Ironton", "Psyche", "150,000"],
               ["The outer Belt", "the Hollows: about 100 settled asteroids, each hollowed out with a spinning drum inside", "3 million"]],
      res: [["Precious metals", "Consolidated Platinum (United Reaches and Belt investors), losing its grip"],
            ["Steel", "United Belt Steel (United Reaches), still big, no longer dominant"],
            ["Water", "Ceres"],
            ["Uranium", "Hygiea Mining (outer Belt), privately owned"],
            ["Routes", "the Lines, ending at Piazzi"]]
    },
    "Ceres": {
      held: [["l5", "The United Reaches"]],
      people: "3.1 million",
      places: [["Piazzi", "spin stations in orbit, and on the surface; the capital of the Belt", "2.5 million", "Belt finance, the precious-metal selling office, the Lines' Belt terminus, shipyards, water", "Housing"],
               ["Tianfu", "buried in the icy crust", "600,000", "Water and fuel, the Belt's oldest shipyard", "Sunlight, metal, warmth"]]
    },
    "Vesta": {
      held: [["ind", "An independent republic"]],
      people: "1.8 million",
      places: [["Kaap", "a buried city and a spin station", "1.8 million", "Refueling, repair and food for the Jupiter run, the uranium trade, the Belt's best hospitals", "Water, shipped from Ceres; justice between its two peoples"]]
    },
    "Psyche": {
      held: [["l5", "The United Reaches"]],
      people: "150,000",
      places: [["Ironton", "tunnels in the metal, beside the Foundry", "150,000", "Foundry maintenance, salvage, the Lines", "Everything organic, nitrogen, a future"]],
      notes: ["Half of Psyche is gone. The Foundry, hundreds of rails tens of kilometers long, stands silent", "The heart of Belt resentment"]
    },
    "Hygiea": {
      held: [["tied", "The outer Belt, self-governing"]],
      people: "500,000; 3 million across the outer Belt",
      places: [["Albion", "a buried city; the capital of the outer Belt", "500,000", "Uranium, ice, outfitting for Jupiter and Saturn", "Sunlight, warmth, people"]],
      res: [["Uranium", "Hygiea Mining, privately owned: fuel for the reactors at Jupiter and Saturn"]]
    },
    "Jupiter Trojans": {
      held: [["l5", "The United Reaches"]],
      people: "900,000",
      places: [["Hektor", "624 Hektor, the largest Trojan, in the swarm ahead of Jupiter", "700,000", "Ice, rare volatiles, the outer Lines, gambling", "Sunlight, law, warmth"],
               ["Ife", "a large Trojan in the swarm ahead of Jupiter", "200,000", "Ice, volatiles, the outer Lines' depot, music", "Sunlight, metal, attention from the Pearl"]]
    },
    "Jupiter": {
      held: [["ind", "The Jupiter republic: Callisto and Io"], ["ind", "Ganymede"], ["ind", "Europa"], ["l5", "The Trojans, in Jupiter's orbit"]],
      people: "About 10 million",
      places: [["Valhalla", "Callisto, in the Valhalla basin; the republic's capital", "6 million", "Port of the outer system, water works, shipbuilding, the waystation to Saturn", "Sunlight, nitrogen, news from the inner system"],
               ["Yongning", "Ganymede, under 2 km of ice", "2.2 million", "Ice, buried farms that feed Jupiter, ships", "Sunlight, nitrogen, metal"],
               ["Conamara", "Europa, carved into the ice above the ocean", "1.5 million", "Ocean science, biotech, precision manufacturing; the strictest environmental law in the system", "Metal, sunlight, trust in outsiders"],
               ["Loki", "Io, buried and heavily shielded", "40,000 on rotation", "Jupiter's electrical link, volcanic heat, sulfur", "Safety: a day outside kills"]],
      res: [["Power", "the Io Power Authority, public, of the Jupiter republic"],
            ["Water and fuel", "Callisto Water Works, state-owned"],
            ["Food", "Ganymede's buried farms"]],
      notes: ["Sunlight here is about 4% of Earth's, so the outer colonies run on Io's power, Titan's hydrocarbons and uranium"]
    },
    "Saturn": {
      held: [["tied", "Titan, federated and self-governing"], ["l5", "The rings, protected, and Mimas Station"], ["none", "Enceladus, science only"], ["earth", "Phoebe (the US-led bloc)"]],
      people: "About 9 million",
      places: [["Port Kraken", "Titan, on Kraken Mare, under domes", "4 million", "Hydrocarbons, plastics, air for the system, shipping", "Sunlight, warmth, metal, full gravity"],
               ["Ligeia", "Titan, on Ligeia Mare", "3 million", "Hydrocarbons, the Titan Net, Titan's universities", "Work"],
               ["Huygens", "Titan's highlands; the capital", "400,000", "Government"],
               ["Mimas Station", "Mimas, at the edge of the rings", "5,000", "The Ring Wardens, science, pilgrims who come to see the rings"],
               ["The Enceladus stations", "six bases over the south-pole geysers", "About 2,000 on rotation", "Science only: the ocean and whatever lives in it"],
               ["Refuge", "Phoebe, one sealed habitat", "60", "Subsistence, a research grant"]],
      res: [["Hydrocarbons", "the pieces of Titan Standard (United Reaches), and Shell-Titan (EU and the US-led bloc)"],
            ["Nitrogen", "Titan, cheap now that it is recycled (Rhine Chemical, EU)"],
            ["Air", "Prana Gases (India), at Port Kraken"],
            ["Water", "the rings, about 15 quadrillion metric tons of ice, protected"]]
    },
    "Uranus": {
      held: [["ind", "The Titania state"]],
      people: "900,000",
      places: [["New Arden", "Titania, a buried city", "900,000, a third of them citizens", "Hydrogen and deuterium scooped from Uranus, fuel for the outer system", "Everything but gas and money"]],
      res: [["Outer-system fuel", "Titania National Gas, the richest company in the outer system, run by a few families"]]
    },
    "Neptune": {
      held: [["none", "Unclaimed"]],
      people: "300",
      places: [["Far Station", "Triton", "300", "Science, nitrogen ice surveys"]],
      notes: ["The farthest place people live"]
    }
  };
  // what is on each moon, for the moon rows and their hover cards
  const AOG_MOONS = {
    "The Moon": ["ind", "Guanghan, Yinshan, Peary, the Quarry", "4 million; the Moon republics, and Peary on its own"],
    "Phobos":   ["l5", "Dwarka", "400,000; the United Reaches"],
    "Io":       ["ind", "Loki", "40,000 on rotation; the Jupiter republic"],
    "Europa":   ["ind", "Conamara", "1.5 million; independent"],
    "Ganymede": ["ind", "Yongning", "2.2 million; independent"],
    "Callisto": ["ind", "Valhalla", "6 million; the Jupiter republic's capital"],
    "Mimas":    ["l5", "Mimas Station", "5,000; the United Reaches' Ring Wardens"],
    "Enceladus":["none", "six stations", "about 2,000; owned by no one"],
    "Titan":    ["tied", "Port Kraken, Ligeia, Huygens", "7.4 million; federated Titan"],
    "Phoebe":   ["earth", "Refuge", "60; the US-led bloc"],
    "Titania":  ["ind", "New Arden", "900,000; the Titania state"],
    "Triton":   ["none", "Far Station", "300; unclaimed"]
  };
  AOG["The Moon"] = {
    held: [["ind", "The Moon republics"], ["ind", "Peary, a republic of its own, close to the United Reaches"]],
    people: "4 million",
    places: [["Guanghan", "the south pole, along Shackleton's rim; the capital", "2.5 million", "Ice, oxygen, mass drivers, aluminum smelting, launch rails", "Nitrogen, carbon, full gravity, sunlight below ground"],
             ["Yinshan", "a south-polar crater in permanent shadow", "600,000", "Salvage; the ice is mostly gone", "Ice, work"],
             ["Peary", "Peary crater, the north pole", "600,000", "Ice, construction, a mass driver", "Nitrogen, carbon"],
             ["The Quarry", "the far side"]],
    res: [["Ice and oxygen", "the Moon republics"],
          ["Construction", "Lunar Works, owned by the Moon republics; Moonstone Consortium (US–EU bloc) at Peary"],
          ["Aluminum", "Procellarum Aluminum (United Reaches), smelting at Guanghan"]]
  };

  // The places that are not bodies: the Sun zone, the Gate, the Lines.
  const SUNZONE = {
    name: "The Sun Zone", type: "Sails, Lighthouses and collector stations inside Mercury's orbit", aogOnly: true, auIn: 0.1, auOut: 0.35,
    aog: {
      held: [["ind", "Azadi, Shuixing and the other Sun-zone states"], ["l5", "Taeyang; the Lighthouses by treaty and contract"], ["earth", "Hinode (EU) and India's small stations"]],
      people: "About 2 million",
      places: [["The Sails", "0.1 au, in loose swarms", "", "Thousands of collectors of film microns thick, hundreds to thousands of kilometers wide, circling the Sun every 11.5 days"],
               ["The Lighthouses", "0.1 au, 40 stations inside the swarms, spinning or in free fall", "About 12,000 Keepers, on rotations of six to twelve months", "The Current: beams that carry the Sun's power across the system; drone repair", "Everything: shielding, time outside, songs"],
               ["Azadi", "0.3 au, a spin station", "1.5 million", "Solar collection sold into the Current, collector repair; poor", "Water, food, shielding, everything but power"],
               ["Taeyang", "0.3 au", "120,000", "Collectors; where the rich of the Pearl come to see the Sun up close", "Water, shade"],
               ["Hinode", "0.35 au", "80,000", "Collectors, precision optics", "Water, people"]],
      notes: ["The Sun is slightly dimmer than it used to be, behind the Sails"],
      res: [["Power", "General Current (United Reaches) runs most of the Current and holds most Lighthouse contracts; Ashworth Electric (United Reaches) is up for sale"]]
    }
  };
  const GATE = {
    name: "The Gate", type: "At L3, on the far side of the Sun", aogOnly: true,
    aog: {
      held: [["none", "No one"]],
      notes: ["A sphere about 200 meters across that absorbs all light and stays at 37 °C", "Drawn under the Sun: it sits opposite Earth, 1 au beyond the Sun"]
    }
  };
  const LINES = {
    name: "The Lines", type: "Cargo routes from Earth orbit to Mars and the Belt", aogOnly: true,
    aog: {
      held: [["l5", "One great line company, chartered by the United Reaches"]],
      places: [["Freight", "pods on fixed arcs", "", "Cheap and slow, unmanned: metal, ice, goods. Easy to find, and robbed"],
               ["Express", "crewed ships", "", "Fast and expensive, on solar propulsion"],
               ["Stations", "launchers, catchers, relays", "", "Gateway at Mars, Piazzi at the Belt end"]],
      res: [["Security", "patrols, private guards and old feuds; the Academy's patrols among them"]]
    }
  };
  const CYCLERS = {
    name: "The Cyclers", type: "Three hollowed asteroids on one loop between Earth and Mars", aogOnly: true,
    aog: {
      places: [["Ellis", "a hollowed asteroid"], ["Galveston", "a hollowed asteroid"], ["Angel", "a hollowed asteroid"]],
      notes: ["One looping orbit crosses Earth's orbit and Mars's: 5 months on the fast leg, 21 on the slow one. They meet Earth every 26 months"]
    }
  };
  const HOLLOWS = {
    name: "The Hollows", type: "Settled asteroids across the Belt", aogOnly: true,
    aog: {
      held: [["tied", "The outer Belt, self-governing, from Albion on Hygiea"]],
      people: "About 3 million",
      notes: ["About 100 settled asteroids, each hollowed out with a spinning drum inside"]
    }
  };
  const PSYCHE_REF = PSYCHE, EARTH_P = PLANETS.find(q => q.name === "Earth"), MARS_P = PLANETS.find(q => q.name === "Mars");

  // the five kinds of holder, each a panel of its own
  const AOG_POWERS = {
    l5: { held: [["l5", "Armstrong, the capital, in high Earth orbit, with Lowell, the Kranz Flight Academy and the Navy's Garrison"],
                 ["l5", "L5: the Pearl, the mother world, and Lagrange"], ["l5", "The Prairies: all six farm cylinders"],
                 ["l5", "Mars and Phobos"], ["l5", "Ceres, Psyche and the inner Belt"], ["l5", "The Jupiter Trojans"],
                 ["l5", "Taeyang and Caloris; the Lighthouses by treaty and contract"], ["l5", "Saturn's rings, protected"]],
          res: [["Power", "General Current; Ashworth Electric, up for sale"], ["Metals", "Procellarum Aluminum, United Belt Steel, Consolidated Platinum (with Belt investors)"],
                ["Chemicals", "Delmont Chemical"], ["Medicine", "Halcyon"], ["Food", "Meridian Foods, from the Prairies; United Harvest, diminished"],
                ["Hydrocarbons", "the pieces of Titan Standard"], ["Banking", "Wexley Express"], ["Routes", "the Lines"]],
          notes: ["The dominant power in space"] },
    ind: { held: [["ind", "The Moon republics, and Peary"], ["ind", "L4: Penglai and Yongle, the Yongle Republic"], ["ind", "Venus"], ["ind", "Azadi, Shuixing and the other Sun-zone states"],
                  ["ind", "Vesta (Kaap)"], ["ind", "The Jupiter republic: Callisto and Io"], ["ind", "Ganymede"], ["ind", "Europa, a power of its own"], ["ind", "The Titania state, at Uranus"]],
           res: [["Ice and construction", "the Moon republics, Lunar Works"], ["Carbon and acid", "Venus's Cloud Houses"],
                 ["Power and water at Jupiter", "the Io Power Authority, Callisto Water Works"], ["Outer-system fuel", "Titania National Gas"]] },
    tied: { held: [["tied", "Titan, federated"], ["tied", "The outer Belt, from Albion on Hygiea"]],
            res: [["Uranium", "Hygiea Mining, privately owned"], ["Hydrocarbons", "Titan's fields, worked by Shell-Titan and the pieces of Titan Standard"]],
            notes: ["Self-governing, and sharing a head of state with the US-led bloc"] },
    earth: { held: [["earth", "The EU: Hinode, in the Sun zone"], ["earth", "India: a few small Sun-zone stations"], ["earth", "The US-led bloc: Phoebe"],
                    ["earth", "The Latin American League: the elevator's ground half"]],
             res: [["Medicine and chemicals", "Rhine Orbital and Rhine Chemical (EU)"], ["Air", "Prana Gases (India), India's most valuable company"],
                   ["Xenon", "Earth's Xenon Council"], ["Banking", "the Weller House (EU)"]],
             notes: ["About 6 billion people on Earth, and falling"] },
    none: { held: [["none", "Enceladus, science only"], ["none", "Triton, outposts only"], ["none", "The elevator and Cumbre, by treaty"], ["none", "The Gate"]],
            notes: ["The elevator is the one place nobody fights over: a cut cable would wrap around the equator"] }
  };
  const AOG_POWER_OBJ = {};
  for (const k in AOG_HOLD)
    AOG_POWER_OBJ[k] = { name: AOG_HOLD[k].name, type: "Who holds what in 2500", aogOnly: true, aogPower: k, aog: AOG_POWERS[k] };

  // the holders of a body, for the colored ring around it
  function aogCats(name) {
    const d = AOG[name];
    if (!d) return null;
    return [...new Set((d.held || []).map(h => h[0]))];
  }

  // ----- the panel -----
  const aogBox = document.getElementById("aog");
  const aogLegend = document.getElementById("aogLegend");
  function aogEl(parent, tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    parent.appendChild(e);
    return e;
  }
  function aogFill(d) {
    aogBox.textContent = "";
    aogBox.hidden = !d;
    if (!d) return;
    aogEl(aogBox, "div", "aog-head", "In 2500, in the novel");
    for (const [k, t] of d.held || []) {
      const row = aogEl(aogBox, "div", "aog-held");
      aogEl(row, "i").style.background = AOG_HOLD[k].color;
      aogEl(row, "span", "", t);
    }
    if (d.people) { aogEl(aogBox, "div", "aog-dt", "People"); aogEl(aogBox, "div", "aog-dd", d.people); }
    if (d.places && d.places.length) {
      aogEl(aogBox, "div", "aog-dt", "Places");
      for (const [n, w, pop, does, short] of d.places) {
        const p = aogEl(aogBox, "div", "aog-place");
        const top = aogEl(p, "div", "aog-pn");
        aogEl(top, "b", "", n);
        if (pop) aogEl(top, "span", "aog-pop", pop);
        if (w) aogEl(p, "div", "aog-where", w);
        if (does) aogEl(p, "div", "", does);
        if (short) aogEl(p, "div", "aog-short", "Short of: " + short);
      }
    }
    if (d.res && d.res.length) {
      aogEl(aogBox, "div", "aog-dt", "Who controls what");
      for (const [what, who] of d.res) {
        const r = aogEl(aogBox, "div", "aog-res");
        aogEl(r, "b", "", what + ": ");
        aogEl(r, "span", "", who);
      }
    }
    if (d.notes) for (const n of d.notes) aogEl(aogBox, "div", "aog-note", n);
  }
  function aogPanel(o) {
    document.querySelector("#info dl").style.display = "";
    aogFill(AOG[o.name] || null);
    if (o !== EARTH_P) { emClose(); return; }
    // Earth: the Earth-Moon panel opens beside it on a wide window; on a
    // narrow one this button opens it
    const b = document.createElement("button");
    b.type = "button"; b.className = "aog-em"; b.textContent = "The Earth–Moon panel";
    b.addEventListener("click", () => { if (em.hidden) emOpen(); else emClose(); });
    aogBox.insertBefore(b, aogBox.children[1]);
    if (W >= 900) emOpen(); else emClose();
  }
  function aogShowOnly(o) {
    el("iName").textContent = o.name;
    el("iType").textContent = o.type;
    document.querySelector("#info dl").style.display = "none";
    aogFill(o.aog);
    info.classList.add("show");
    fitPanel();
    info.scrollTop = 0;
  }
  // a panel-only place: frame it, or for a holder, the whole system
  function aogFocus(o) {
    if (o.aogPower || o === LINES) { fitAll(); return; }
    if (o === CYCLERS) {
      const a = auX(0.9), b = auX(2.35);
      camT.c = (a + b) / 2; camT.z = Math.min(W * 0.5, beltHalfHeight() * 1.8) / Math.max(b - a, 1e-9); return;
    }
    if (o === HOLLOWS) {
      const a = BELT.edgeIn(), b = BELT.edgeOut();
      camT.c = (a + b) / 2; camT.z = Math.min(W * 0.42, beltHalfHeight() * 1.6) / Math.max(b - a, 1e-9); return;
    }
    if (o === GATE) { camT.c = 0; camT.z = Math.min(H, W) * 0.18 / sunR(); return; }
    if (o === SUNZONE) {
      const a = 0, b = px(PLANETS[0]) + pr(PLANETS[0]) * 2;
      camT.c = (a + b) / 2; camT.z = Math.min(W * 0.55, beltHalfHeight() * 1.6) / Math.max(b - a, 1e-9);
    }
  }

  // ----- the legend -----
  for (const k in AOG_HOLD) {
    const b = document.createElement("button");
    b.type = "button"; b.dataset.k = k;
    const sw = document.createElement("i"); sw.style.background = AOG_HOLD[k].color;
    b.appendChild(sw); b.appendChild(document.createTextNode(AOG_HOLD[k].name));
    b.addEventListener("click", () => select(selected === AOG_POWER_OBJ[k] ? null : AOG_POWER_OBJ[k]));
    aogLegend.appendChild(b);
  }


  // ----- the made objects: four icons, drawn the same in every view -----
  // a cored world: a gold sphere with its decks, a wedge cut away at lower
  // right to show the dark interior and the core glowing at the center
  function icoCored(c, x, y, r) {
    c.save();
    const g = c.createRadialGradient(x - r * 0.35, y - r * 0.4, r * 0.08, x, y, r);
    g.addColorStop(0, "#fff4cf"); g.addColorStop(0.45, "#e9b949"); g.addColorStop(1, "#7a4f12");
    c.beginPath(); c.moveTo(x, y); c.arc(x, y, r, Math.PI / 2, 2 * Math.PI); c.closePath();
    c.fillStyle = g; c.fill();
    c.save(); c.clip();
    c.strokeStyle = "rgba(95,58,10,0.38)"; c.lineWidth = Math.max(0.5, r * 0.06);
    for (const f of [-0.6, -0.25, 0.1, 0.45]) {
      const w = r * Math.sqrt(1 - f * f);
      c.beginPath(); c.ellipse(x, y + f * r, w, w * 0.2, 0, 0, 2 * Math.PI); c.stroke();
    }
    c.restore();
    c.beginPath(); c.moveTo(x, y); c.arc(x, y, r, 0, Math.PI / 2); c.closePath();
    c.fillStyle = "#170f05"; c.fill();
    if (r >= 6) {
      c.strokeStyle = "rgba(233,185,73,0.5)"; c.lineWidth = Math.max(0.4, r * 0.04);
      for (const f of [0.93, 0.84]) { c.beginPath(); c.arc(x, y, r * f, 0, Math.PI / 2); c.stroke(); }
    }
    const cr = Math.max(1.4, r * 0.2);
    const cg = c.createRadialGradient(x + cr * 0.3, y + cr * 0.3, 0, x + cr * 0.3, y + cr * 0.3, cr);
    cg.addColorStop(0, "rgba(255,255,255,1)"); cg.addColorStop(0.3, "rgba(255,255,255,0.85)"); cg.addColorStop(1, "rgba(255,255,255,0)");
    c.fillStyle = cg; c.beginPath(); c.arc(x + cr * 0.3, y + cr * 0.3, cr, 0, 2 * Math.PI); c.fill();
    c.restore();
  }
  function capsulePath(c, x, y, w, h) {
    const r = w / 2;
    c.beginPath(); c.moveTo(x - r, y - h / 2 + r); c.arc(x, y - h / 2 + r, r, Math.PI, 0);
    c.lineTo(x + r, y + h / 2 - r); c.arc(x, y + h / 2 - r, r, 0, Math.PI); c.closePath();
  }
  // a Prairie pair: two farm cylinders side by side, striped window, land,
  // window along their length, with grey end caps and a thin silver
  // reflector angled out from the sunward (upper) end of each
  function icoPair(c, x, y, s) {
    const h = 2 * s, w = s * 0.62, gap = s * 0.22;
    for (const side of [-1, 1]) {
      const cx = x + side * (gap / 2 + w / 2);
      c.save();
      capsulePath(c, cx, y, w, h);
      c.save(); c.clip();
      c.fillStyle = "#8d949e"; c.fillRect(cx - w / 2, y - h / 2, w, h);
      const top = y - h / 2 + w * 0.45, len = h - w * 0.9;
      [["#a8dcff", 0], ["#58a94f", 1], ["#a8dcff", 2]].forEach(([col, k]) => {
        c.fillStyle = col; c.fillRect(cx - w / 2 + k * w / 3, top, w / 3 + 0.3, len);
      });
      c.restore();
      c.strokeStyle = "rgba(15,20,30,0.7)"; c.lineWidth = 0.6; capsulePath(c, cx, y, w, h); c.stroke();
      c.strokeStyle = "#e8ebf0"; c.lineWidth = Math.max(0.8, s * 0.09);
      const ox = cx + side * w / 2, oy = y - h / 2 + w * 0.5;
      c.beginPath(); c.moveTo(ox, oy); c.lineTo(ox + side * s * 0.62, oy - s * 0.62); c.stroke();
      c.restore();
    }
  }
  // a spin station: a tilted wheel, three spokes, a hub and a short axle
  function icoSpin(c, x, y, r) {
    c.save();
    const ry = r * 0.42;
    c.strokeStyle = "#9aa1ab"; c.lineWidth = Math.max(0.8, r * 0.1);
    c.beginPath(); c.moveTo(x, y - r * 0.68); c.lineTo(x, y + r * 0.68); c.stroke();
    c.strokeStyle = "#b8bec7"; c.lineWidth = Math.max(0.6, r * 0.08);
    for (let k = 0; k < 3; k++) {
      const a = Math.PI / 2 + k * 2 * Math.PI / 3;
      c.beginPath(); c.moveTo(x, y); c.lineTo(x + r * Math.cos(a), y + ry * Math.sin(a)); c.stroke();
    }
    const g = c.createLinearGradient(x - r, y - ry, x + r, y + ry);
    g.addColorStop(0, "#eef1f5"); g.addColorStop(0.5, "#858c96"); g.addColorStop(1, "#d3d8df");
    c.strokeStyle = g; c.lineWidth = Math.max(1.2, r * 0.26);
    c.beginPath(); c.ellipse(x, y, r, ry, 0, 0, 2 * Math.PI); c.stroke();
    c.fillStyle = "#dfe3e9"; c.beginPath(); c.arc(x, y, Math.max(1, r * 0.17), 0, 2 * Math.PI); c.fill();
    c.restore();
  }
  // a Hollow or a Cycler: a rough brown rock, cut away to show the spinning
  // drum glowing inside
  const ROCK = [1, 0.84, 0.97, 0.78, 0.93, 1.06, 0.83, 0.96, 0.88, 1.02];
  function icoHollow(c, x, y, r) {
    c.save();
    c.beginPath();
    ROCK.forEach((k, i) => {
      const a = i / ROCK.length * 2 * Math.PI, qx = x + r * k * Math.cos(a), qy = y + r * 0.82 * k * Math.sin(a);
      if (i) c.lineTo(qx, qy); else c.moveTo(qx, qy);
    });
    c.closePath();
    const g = c.createRadialGradient(x - r * 0.3, y - r * 0.35, r * 0.1, x, y, r * 1.1);
    g.addColorStop(0, "#a8815a"); g.addColorStop(1, "#4a3220");
    c.fillStyle = g; c.fill();
    c.strokeStyle = "rgba(30,18,8,0.75)"; c.lineWidth = 0.6; c.stroke();
    if (r >= 3.2) {
      const dx = x + r * 0.12, dy = y + r * 0.08;
      c.fillStyle = "#120b05"; c.beginPath(); c.ellipse(dx, dy, r * 0.58, r * 0.38, 0, 0, 2 * Math.PI); c.fill();
      const dw = r * 0.4, dh = r * 0.2;
      const dg = c.createLinearGradient(0, dy - dh, 0, dy + dh);
      dg.addColorStop(0, "#fff3c2"); dg.addColorStop(0.5, "#ffc861"); dg.addColorStop(1, "#c27a1e");
      c.fillStyle = dg; c.fillRect(dx - dw, dy - dh, 2 * dw, 2 * dh);
      c.strokeStyle = "rgba(110,60,10,0.85)"; c.lineWidth = Math.max(0.4, r * 0.05);
      for (const f of [-0.45, 0.05, 0.55]) { c.beginPath(); c.moveTo(dx + f * dw, dy - dh); c.lineTo(dx + f * dw, dy + dh); c.stroke(); }
    } else {
      c.fillStyle = "#ffd27a"; c.fillRect(x - 0.6, y - 0.6, 1.2, 1.2);
    }
    c.restore();
  }
  // a town or a post, in its holder's color
  function icoTown(c, x, y, r, col) {
    c.fillStyle = col;
    c.beginPath(); c.moveTo(x, y - r); c.lineTo(x + r, y); c.lineTo(x, y + r); c.lineTo(x - r, y); c.fill();
  }

  // ----- the second legend: the made objects -----
  const aogIcons = document.getElementById("aogIcons");
  for (const [name, draw] of [["Cored world", c => icoCored(c, 11, 9, 7.5)],
                              ["Prairie pair, two farm cylinders", c => icoPair(c, 10, 10, 6.5)],
                              ["Spin station", c => icoSpin(c, 11, 9, 8.5)],
                              ["Hollow or Cycler", c => icoHollow(c, 11, 9, 7.5)],
                              ["Town or post", c => icoTown(c, 11, 9, 4, "#cfd6e0")]]) {
    const sp = document.createElement("span"), cv = document.createElement("canvas"), dpr = window.devicePixelRatio || 1;
    cv.width = 22 * dpr; cv.height = 19 * dpr; cv.style.width = "22px"; cv.style.height = "19px";
    const c = cv.getContext("2d"); c.setTransform(dpr, 0, 0, dpr, 0, 0); draw(c);
    sp.appendChild(cv); sp.appendChild(document.createTextNode(name));
    aogIcons.appendChild(sp);
  }

  // ----- the Earth-Moon panel -----
  // Seen from above Earth's north pole. Distances are to scale in both views,
  // the whole system above and the elevator enlarged below; the objects are
  // drawn larger than they are.
  const em = document.getElementById("em"), emCv = document.getElementById("emCv"), emTip = document.getElementById("emTip");
  const emX = emCv.getContext("2d");
  const EM_KM = { re: 6371, roadsIn: 6771, roadsOut: 6971, geo: 42164, cw: 106371, arm: 116000, moon: 384400 };
  const EM_TIP = {
    roads: "The Roads, 400 to 600 km up: low-orbit spin stations",
    elevator: "The elevator; Cumbre (dock) at 35,786 km; Counterweight at 100,000 km",
    cumbre: "Cumbre, the elevator's geostationary dock, 35,786 km up",
    cw: "The Counterweight, at the elevator's top, 100,000 km up",
    armstrong: "Armstrong, a cored world, 116,000 km out: six orbits each lunar month. Capital of the United Reaches. 10 km across, 24 decks, 6,700 km², 12 million people. Lowell is Decks 1–10; the Kranz Flight Academy is a district on Decks 22–24; the Navy's Garrison is on the far side. Core: 3.2 × 10¹⁸ kg",
    pairA: "A Prairie pair in Armstrong's orbit: two farm cylinders, each 8 km wide and 32 km long",
    moon: "The Moon, 384,400 km out: the Moon republics; the far-side Quarry",
    quarry: "The Quarry, on the Moon's far side",
    penglai: "Penglai, a cored world at L4, 60° ahead of the Moon. The Yongle Republic's world. 7 km across, 17 decks, 2,300 km², 14 million: the smallest world and the best used. Beside the old Yongle spin station. Core: 1.6 × 10¹⁸ kg",
    yongle: "Yongle, China's first great spin station",
    pearl: "The Pearl, a cored world at L5, 60° behind the Moon. The mother world. 15 km across, 36 decks, 22,300 km², 180 million. Seat of the Assembly of Worlds, on the Common. Core: 7.2 × 10¹⁸ kg",
    lagrange: "Lagrange: the old L5 spin stations, the oldest families",
    pairsL5: "Two Prairie pairs near the Pearl: four farm cylinders, each 8 km wide and 32 km long"
  };
  let emItems = [], emGeo = null;
  function emPlace() {
    const above = document.getElementById("hud").getBoundingClientRect().bottom;
    const bar = document.getElementById("controls").getBoundingClientRect().top;
    em.style.top = (above + 10) + "px";
    em.style.maxHeight = Math.max(150, (bar > 0 ? bar : window.innerHeight) - above - 24) + "px";
  }
  function emOpen() { em.hidden = false; emPlace(); emDraw(); }
  function emClose() { em.hidden = true; emTip.hidden = true; }
  document.getElementById("emClose").addEventListener("click", emClose);
  window.addEventListener("resize", () => { if (!em.hidden) { emPlace(); emDraw(); } });
  function emLabel(c, t, x, y, o) {
    o = o || {};
    c.font = (o.bold ? "600 " : "") + (o.size || 11) + "px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
    c.textAlign = o.align || "left";
    c.fillStyle = o.color || "rgba(220,228,245,0.92)";
    c.fillText(t, x, y);
  }
  function emDraw() {
    const dpr = window.devicePixelRatio || 1, cw = Math.max(260, emCv.clientWidth || 380);
    const mainH = Math.round(cw * 0.84), stripTop = mainH + 10, stripH = 112, ch = stripTop + stripH;
    emCv.style.height = ch + "px"; emCv.width = Math.round(cw * dpr); emCv.height = Math.round(ch * dpr);
    const c = emX; c.setTransform(dpr, 0, 0, dpr, 0, 0); c.clearRect(0, 0, cw, ch);
    emItems = [];
    const dim = "rgba(150,165,195,0.85)", gold = "#e9b949";
    // --- the whole system, to scale ---
    const cx = cw / 2 + 6, cy = mainH / 2 + 4;
    const R = Math.min(cw / 2 - 34, (mainH / 2 - 34) / Math.sin(Math.PI / 3));
    const s = R / EM_KM.moon;
    const P = (deg, km) => [cx + km * s * Math.cos(deg * Math.PI / 180), cy - km * s * Math.sin(deg * Math.PI / 180)];
    c.strokeStyle = "rgba(170,190,230,0.35)"; c.lineWidth = 1; c.setLineDash([3, 4]);
    c.beginPath(); c.arc(cx, cy, R, 0, 2 * Math.PI); c.stroke(); c.setLineDash([]);
    // the way round: counterclockwise, seen from the north
    c.strokeStyle = "rgba(170,190,230,0.6)"; c.lineWidth = 1.2;
    c.beginPath(); c.arc(cx, cy, R, -0.42, -0.22); c.stroke();
    const [ax, ay] = P(24, EM_KM.moon);
    c.fillStyle = "rgba(170,190,230,0.7)"; c.beginPath();
    c.moveTo(ax, ay - 5); c.lineTo(ax - 4.5, ay + 2); c.lineTo(ax + 4.5, ay + 2); c.fill();
    // Armstrong's orbit
    c.strokeStyle = "rgba(233,185,73,0.4)"; c.beginPath(); c.arc(cx, cy, EM_KM.arm * s, 0, 2 * Math.PI); c.stroke();
    // the box enlarged below
    const bx0 = cx - EM_KM.re * s - 2, bx1 = cx + 125000 * s, bh = 20;
    c.strokeStyle = "rgba(170,190,230,0.45)"; c.setLineDash([2, 3]);
    c.strokeRect(bx0, cy - bh / 2, bx1 - bx0, bh); c.setLineDash([]);
    // Earth and the elevator
    c.fillStyle = "#3b7dd8"; c.beginPath(); c.arc(cx, cy, Math.max(2.6, EM_KM.re * s), 0, 2 * Math.PI); c.fill();
    c.strokeStyle = "#d9dee6"; c.lineWidth = 0.9;
    c.beginPath(); c.moveTo(cx + EM_KM.re * s, cy); c.lineTo(cx + EM_KM.cw * s, cy); c.stroke();
    emLabel(c, "Earth", cx - 7, cy + 3, { align: "right", size: 10, color: dim });
    emLabel(c, "enlarged below", bx1, cy + bh / 2 + 11, { align: "right", size: 9.5, color: dim });
    // Armstrong and its Prairie pair, in Armstrong's orbit
    const [arx, ary] = P(-52, EM_KM.arm), [pax, pay] = P(-92, EM_KM.arm);
    icoCored(c, arx, ary, 7.5);
    emLabel(c, "Armstrong", arx + 11, ary + 4, { bold: true });
    icoPair(c, pax, pay, 5.5);
    emLabel(c, "Prairie pair", pax - 10, pay + 4, { align: "right", size: 10, color: dim });
    emItems.push({ x: arx, y: ary, r: 10, t: EM_TIP.armstrong }, { x: pax, y: pay, r: 9, t: EM_TIP.pairA });
    // the Moon, with the Quarry on its far side
    const [mx, my] = P(180, EM_KM.moon);
    const mg = c.createRadialGradient(mx - 2, my - 2, 0.5, mx, my, 6);
    mg.addColorStop(0, "#e6e6e6"); mg.addColorStop(1, "#6a6a6a");
    c.fillStyle = mg; c.beginPath(); c.arc(mx, my, 6, 0, 2 * Math.PI); c.fill();
    emLabel(c, "the Moon", mx + 10, my + 4, { bold: true });
    icoTown(c, mx - 9, my + 4, 2.6, AOG_HOLD.ind.color);
    emLabel(c, "the Quarry", mx - 3, my + 18, { size: 9.5, color: dim });
    emItems.push({ x: mx, y: my, r: 8, t: EM_TIP.moon }, { x: mx - 9, y: my + 4, r: 5, t: EM_TIP.quarry });
    // L5: the Pearl, Lagrange and two Prairie pairs
    const [lx, ly] = P(120, EM_KM.moon);
    icoCored(c, lx, ly, 11);
    emLabel(c, "the Pearl", lx + 15, ly + 1, { bold: true, size: 12 });
    emLabel(c, "L5, 60° behind the Moon", lx + 15, ly + 14, { size: 9.5, color: dim });
    icoSpin(c, lx - 20, ly + 17, 5.5); icoSpin(c, lx - 9, ly + 25, 4.5);
    emLabel(c, "Lagrange", lx - 14, ly + 41, { size: 10, align: "center", color: dim });
    icoPair(c, lx - 14, ly - 22, 5.5); icoPair(c, lx + 4, ly - 25, 5.5);
    emLabel(c, "two Prairie pairs", lx + 14, ly - 23, { size: 10, color: dim });
    emItems.push({ x: lx, y: ly, r: 13, t: EM_TIP.pearl }, { x: lx - 15, y: ly + 21, r: 10, t: EM_TIP.lagrange },
                 { x: lx - 5, y: ly - 23, r: 13, t: EM_TIP.pairsL5 });
    // L4: Penglai beside the old Yongle station
    const [qx, qy] = P(240, EM_KM.moon);
    icoCored(c, qx, qy, 6);
    emLabel(c, "Penglai", qx + 11, qy + 1, { bold: true });
    emLabel(c, "L4, 60° ahead of the Moon", qx + 11, qy + 14, { size: 9.5, color: dim });
    icoSpin(c, qx - 15, qy - 11, 5);
    emLabel(c, "Yongle", qx - 15, qy - 21, { size: 10, align: "center", color: dim });
    emItems.push({ x: qx, y: qy, r: 9, t: EM_TIP.penglai }, { x: qx - 15, y: qy - 11, r: 8, t: EM_TIP.yongle });
    // scale bar
    const sb = 100000 * s, sbx = cw - 12 - sb, sby = mainH - 8;
    c.strokeStyle = dim; c.lineWidth = 1;
    c.beginPath(); c.moveTo(sbx, sby - 3); c.lineTo(sbx, sby); c.lineTo(sbx + sb, sby); c.lineTo(sbx + sb, sby - 3); c.stroke();
    emLabel(c, "100,000 km", sbx + sb / 2, sby - 6, { size: 9.5, align: "center", color: dim });
    // --- the elevator, enlarged, to scale ---
    c.fillStyle = "rgba(255,255,255,0.03)"; c.strokeStyle = "rgba(170,190,230,0.25)";
    c.beginPath(); c.rect(0.5, stripTop + 0.5, cw - 1, stripH - 1); c.fill(); c.stroke();
    c.save(); c.beginPath(); c.rect(1, stripTop + 1, cw - 2, stripH - 2); c.clip();
    const s2 = (cw - 22) / (122000 + EM_KM.re), ex = 10 + EM_KM.re * s2, ey = stripTop + stripH / 2 + 6;
    const eg = c.createRadialGradient(ex - 6, ey - 6, 2, ex, ey, EM_KM.re * s2);
    eg.addColorStop(0, "#6fb0ff"); eg.addColorStop(1, "#1d4f9a");
    c.fillStyle = eg; c.beginPath(); c.arc(ex, ey, EM_KM.re * s2, 0, 2 * Math.PI); c.fill();
    // the Roads: a band 400 to 600 km up, thicker here than to scale
    c.strokeStyle = "rgba(200,210,225,0.85)"; c.lineWidth = Math.max(1.5, (EM_KM.roadsOut - EM_KM.roadsIn) * s2);
    c.beginPath(); c.arc(ex, ey, (EM_KM.roadsIn + EM_KM.roadsOut) / 2 * s2 + 0.6, 0, 2 * Math.PI); c.stroke();
    const rgy = ey - EM_KM.roadsOut * s2;
    icoSpin(c, ex + 4, rgy - 3, 4);
    emLabel(c, "the Roads, 400 to 600 km up", ex + 12, rgy - 6, { size: 10, color: dim });
    emItems.push({ x: ex, y: rgy, r: 9, t: EM_TIP.roads });
    // the cable, Cumbre and the Counterweight
    const xS = ex + EM_KM.re * s2, xG = ex + EM_KM.geo * s2, xC = ex + EM_KM.cw * s2;
    c.strokeStyle = "#d9dee6"; c.lineWidth = 1.2;
    c.beginPath(); c.moveTo(xS, ey); c.lineTo(xC, ey); c.stroke();
    c.fillStyle = "#cfd6e0"; c.fillRect(xG - 4, ey - 3, 8, 6);
    emLabel(c, "Cumbre", xG, ey - 8, { bold: true, align: "center" });
    emLabel(c, "the dock, 35,786 km", xG, ey + 17, { size: 9.5, align: "center", color: dim });
    c.fillStyle = "#9aa1ab"; c.fillRect(xC - 3, ey - 5, 6, 10);
    emLabel(c, "Counterweight", xC - 6, ey + 18, { size: 10, align: "right", color: dim });
    emLabel(c, "100,000 km", xC - 6, ey + 30, { size: 9.5, align: "right", color: dim });
    emLabel(c, "the elevator", (xG + xC) / 2, ey - 6, { size: 9.5, align: "center", color: dim });
    emItems.push({ x: xG, y: ey, r: 8, t: EM_TIP.cumbre }, { x: xC, y: ey, r: 8, t: EM_TIP.cw },
                 { x: (xS + xG) / 2, y: ey, r: 7, t: EM_TIP.elevator }, { x: (xG + xC) / 2, y: ey, r: 7, t: EM_TIP.elevator });
    // Armstrong's orbit, just beyond, with Armstrong and the Prairie pair on it
    const RA = EM_KM.arm * s2;
    c.strokeStyle = "rgba(233,185,73,0.45)"; c.lineWidth = 1;
    c.beginPath(); c.arc(ex, ey, RA, -0.3, 0.3); c.stroke();
    const a1 = -0.1, a2 = 0.095;
    const [p1x, p1y] = [ex + RA * Math.cos(a1), ey + RA * Math.sin(a1)], [p2x, p2y] = [ex + RA * Math.cos(a2), ey + RA * Math.sin(a2)];
    icoCored(c, p1x, p1y, 7.5);
    emLabel(c, "Armstrong", p1x - 11, p1y - 4, { bold: true, align: "right" });
    emLabel(c, "116,000 km", p1x - 11, p1y + 8, { size: 9.5, align: "right", color: dim });
    icoPair(c, p2x, p2y, 5.5);
    emItems.push({ x: p1x, y: p1y, r: 10, t: EM_TIP.armstrong }, { x: p2x, y: p2y, r: 9, t: EM_TIP.pairA });
    // for the checker: where things landed, in canvas pixels
    emGeo = { earth: [cx, cy], moon: [mx, my], l4: [qx, qy], l5: [lx, ly], arm: [arx, ary],
              strip: { earth: ex, re: EM_KM.re * s2, cumbre: xG, cw: xC, arm: Math.hypot(p1x - ex, p1y - ey) } };
    // scale bar
    const sb2 = 50000 * s2, sx2 = ex + EM_KM.re * s2 + 14, sy2 = stripTop + stripH - 9;
    c.strokeStyle = dim; c.lineWidth = 1;
    c.beginPath(); c.moveTo(sx2, sy2 - 3); c.lineTo(sx2, sy2); c.lineTo(sx2 + sb2, sy2); c.lineTo(sx2 + sb2, sy2 - 3); c.stroke();
    emLabel(c, "50,000 km", sx2 + sb2 / 2, sy2 - 5, { size: 9.5, align: "center", color: dim });
    c.restore();
  }
  function emAt(e) {
    const b = emCv.getBoundingClientRect(), x = e.clientX - b.left, y = e.clientY - b.top;
    let best = null, bd = 1e9;
    for (const it of emItems) {
      const d = Math.hypot(it.x - x, it.y - y);
      if (d < it.r + 4 && d < bd) { best = it; bd = d; }
    }
    if (!best) { emTip.hidden = true; emCv.style.cursor = ""; return; }
    emCv.style.cursor = "pointer";
    emTip.textContent = best.t; emTip.hidden = false;
    const eb = em.getBoundingClientRect(), tw = emTip.offsetWidth, th = emTip.offsetHeight;
    let tx = e.clientX - eb.left + 12, ty = e.clientY - eb.top + em.scrollTop + 14;
    if (tx + tw > eb.width - 8) tx = Math.max(8, e.clientX - eb.left - tw - 12);
    if (e.clientY + 14 + th > window.innerHeight - 8) ty = e.clientY - eb.top + em.scrollTop - th - 10;
    emTip.style.left = tx + "px"; emTip.style.top = ty + "px";
  }
  emCv.addEventListener("pointermove", emAt);
  emCv.addEventListener("pointerdown", emAt);
  emCv.addEventListener("pointerleave", () => { emTip.hidden = true; });

  // ----- drawing on the main diagram -----
  // the Sun zone: on the lenient line it fills the gap between the Sun's
  // edge and Mercury; at true scale it is at its real distance
  function zoneX(au) {
    const mq = PLANETS[0];
    const len = LEN_SUN_R + (au / mq.au) * (mq.xLen - mq.lenR - LEN_SUN_R);
    return mix(len, au * AU * KM2U, ease(m));
  }
  // any distance from the Sun out to Jupiter, placed between the bodies and
  // belt edges around it, so it sits right on either scale
  function auX(au) {
    const pts = [[0, 0]].concat(PLANETS.slice(0, 4).map(q => [q.au, px(q)]),
      [[BELT.auIn, BELT.edgeIn()], [BELT.auOut, BELT.edgeOut()], [JUPITER.au, px(JUPITER)]]);
    for (let i = 1; i < pts.length; i++)
      if (au <= pts[i][0]) { const [a0, x0] = pts[i - 1], [a1, x1] = pts[i]; return x0 + (x1 - x0) * (au - a0) / (a1 - a0); }
    return pts[pts.length - 1][1];
  }
  function seeded(n, seed, f) {
    let st = seed;
    const rnd = () => (st = (st * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
    return Array.from({ length: n }, () => f(rnd));
  }
  const AOG_SAILS = seeded(150, 2500, r => ({ v: r() * 2 - 1, dx: (r() - 0.5) * 2, w: 0.6 + r() * 1.6 }));
  const AOG_LIGHTS = seeded(40, 4040, r => ({ v: r() * 1.9 - 0.95, dx: (r() - 0.5) * 2 }));
  const AOG_HOLLOWS = seeded(100, 100, r => ({ u: 0.04 + r() * 0.92, v: r() * 1.84 - 0.92, s: 0.75 + r() * 0.5 }));
  const ZONE_STATIONS = [["Azadi", 0.3, "ind", -1], ["Taeyang", 0.3, "l5", 1], ["Hinode", 0.35, "earth", -1]];
  // where each Cycler sits on the loop, as an angle round it
  const AOG_CYCLERS = [["Ellis", 2.25], ["Galveston", 4.6], ["Angel", 5.55]];
  const AOG_TAGS = {
    Venus: ["cloud cities,|rafts 52 km up", "cloud cities, rafts 52 km up"],
    Mars: ["Gateway", "Gateway: spin stations in orbit, with the Gateway Preparatory School; Dwarka inside Phobos; surface towns"],
    Jupiter: ["Valhalla on Callisto", "Valhalla on Callisto"],
    Saturn: ["Titan's towns;|the Rings, protected", "Titan's towns; the Rings, protected"]
  };
  const AOG_BELT_TAGS = { Ceres: ["Piazzi,|the Belt's capital", 0], Vesta: ["Kaap", 0], Psyche: ["half gone;|the silent Foundry", 26, 14] };
  const FONT = px => px + "px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
  function aogAlpha(k) { return selected && selected.aogPower ? (selected.aogPower === k ? 1 : 0.18) : 0.9; }
  function aogRing(x, y, r, cats) {
    if (!cats || !cats.length) return;
    const R = r + 4, n = cats.length;
    ctx.lineWidth = selected && selected.aogPower && cats.includes(selected.aogPower) ? 3 : 2;
    cats.forEach((k, i) => {
      ctx.strokeStyle = AOG_HOLD[k].color; ctx.globalAlpha = aogAlpha(k);
      const a0 = -Math.PI / 2 + i * 2 * Math.PI / n, a1 = a0 + 2 * Math.PI / n - (n > 1 ? 0.25 : 0);
      ctx.beginPath(); ctx.arc(x, y, R, a0, a1); ctx.stroke();
    });
    ctx.globalAlpha = 1;
  }
  function aogLinesY() { return y0 + beltHalfHeight() * 0.45; }
  function aogGatePos() { return [sx(0), y0 + Math.max(sunR() * cam.z, 3) + 52]; }
  function cyclerGeom() {
    const a = sx(auX(0.98)), b = sx(auX(2.23));
    return { a, b, cx: (a + b) / 2, rx: (b - a) / 2, ry: Math.min(beltHalfHeight() * 0.2, Math.max(8, (b - a) * 0.4)) };
  }
  function cyclerPos(g, t) { return [g.cx + g.rx * Math.cos(t), y0 - g.ry * Math.sin(t)]; }
  function hollowR() {
    const w = sx(BELT.edgeOut()) - sx(BELT.edgeIn());
    return Math.max(1.6, Math.min(5, w / 70));
  }
  function hollowPos(h) {
    const a = sx(BELT.edgeIn()), b = sx(BELT.edgeOut());
    return [a + h.u * (b - a), y0 + h.v * beltHalfHeight()];
  }
  function hollowsLabelPos() { return [sx(BELT.edgeOut()) + 8, y0 + beltHalfHeight() * 0.5]; }
  // the Earth tag: the three worlds, and the way to their panel
  function earthTagPos() { const [x, y] = ppos(EARTH_P), r = Math.max(pr(EARTH_P) * cam.z, 0.9); return [x, y + r + 52]; }
  // under the planets: the Sun zone, the Gate, the Lines, the Cyclers, the Hollows
  function aogDraw() {
    if (orbDays > 0) return;
    const hh = beltHalfHeight(), crowd = crowded();
    // the Sails, a curtain at 0.1 au, and the 40 Lighthouses among them
    const xs = sx(zoneX(0.1)), hotZ = selected === SUNZONE;
    if (xs > -40 && xs < W + 40 && (!crowd || hotZ)) {
      const x35 = sx(zoneX(0.35)), near = x35 - xs > 70 || hotZ;
      ctx.fillStyle = "rgba(255,196,110,0.5)";
      ctx.globalAlpha = 0.55 * (selected && selected.aogPower ? aogAlpha("none") : 1);
      for (const s of AOG_SAILS) ctx.fillRect(xs + s.dx * 3, y0 + s.v * hh, s.w, 0.8);
      ctx.globalAlpha = selected && selected.aogPower ? aogAlpha("l5") : 1;
      for (const s of AOG_LIGHTS) {
        if (near) icoSpin(ctx, xs + s.dx * 6, y0 + s.v * hh, 3.4);
        else { ctx.fillStyle = "#fff1c2"; ctx.fillRect(xs + s.dx * 3 - 1, y0 + s.v * hh - 1, 2.2, 2.2); }
      }
      ctx.globalAlpha = 1;
      ctx.font = FONT(11); ctx.textAlign = "center";
      ctx.fillStyle = hotZ ? "#58a6ff" : "rgba(190,205,235,0.85)";
      ctx.fillText("the Sails", xs, y0 - hh - 8);
      if (near) {
        ctx.font = FONT(10); ctx.fillStyle = "rgba(190,205,235,0.75)";
        ctx.fillText("and the 40 Lighthouses", xs, y0 - hh + 5);
      }
      // the collector stations, off the line on either side; Azadi spins
      if (x35 - xs > 24 || hotZ) {
        for (const [n, au, k, side] of ZONE_STATIONS) {
          const x = sx(zoneX(au)), y = y0 + side * (n === "Hinode" ? 30 : 16);
          ctx.globalAlpha = aogAlpha(k);
          if (n === "Azadi") icoSpin(ctx, x, y - 2, near ? 6 : 3.5);
          else icoTown(ctx, x, y, 3.5, AOG_HOLD[k].color);
          ctx.globalAlpha = 1;
          if (near) {
            ctx.font = FONT(10); ctx.textAlign = "left"; ctx.fillStyle = "rgba(200,210,230,0.8)";
            ctx.fillText(n, x + (n === "Azadi" ? 9 : 6), y + 3);
          }
        }
      }
    }
    // the Gate, under the Sun, since it is on the Sun's far side
    if (!crowd || selected === GATE) {
      const [gx, gy] = aogGatePos();
      if (gx > -40 && gx < W + 40) {
        const g = ctx.createRadialGradient(gx, gy, 4, gx, gy, 14);
        g.addColorStop(0, "rgba(230,60,60,0.4)"); g.addColorStop(1, "rgba(230,60,60,0)");
        ctx.fillStyle = g; circle(gx, gy, 14); ctx.fill();
        ctx.fillStyle = "#000"; circle(gx, gy, 6.5); ctx.fill();
        ctx.strokeStyle = selected === GATE ? "#58a6ff" : "#e5484d"; ctx.lineWidth = 1.6;
        circle(gx, gy, 6.5); ctx.stroke();
        ctx.font = FONT(10.5); ctx.textAlign = "center"; ctx.fillStyle = selected === GATE ? "#58a6ff" : "rgba(190,205,235,0.85)";
        ctx.fillText("the Gate", gx, gy + 22);
        ctx.font = FONT(10); ctx.fillStyle = "rgba(150,165,195,0.8)";
        ctx.fillText("at L3, behind the Sun", gx, gy + 34);
      }
    }
    // the Lines, from Earth orbit to Mars and on to the Belt
    if ((!crowd && !moonState) || selected === LINES) {
      const y = aogLinesY(), a = sx(px(EARTH_P)), b = sx(px(PSYCHE_REF)), hot = selected === LINES;
      if (b > -20 && a < W + 20) {
        ctx.strokeStyle = AOG_HOLD.l5.color; ctx.globalAlpha = hot ? 1 : 0.55 * aogAlpha("l5");
        ctx.lineWidth = hot ? 1.6 : 1.1; ctx.setLineDash([5, 4]);
        ctx.beginPath(); ctx.moveTo(a, y); ctx.lineTo(b, y); ctx.stroke(); ctx.setLineDash([]);
        for (const q of [EARTH_P, MARS_P, CERES, PSYCHE_REF]) {
          const x = sx(px(q)); ctx.beginPath(); ctx.moveTo(x, y - 4); ctx.lineTo(x, y + 4); ctx.stroke();
        }
        ctx.globalAlpha = 1;
        if (b - a > 90 || hot) {
          ctx.font = FONT(10.5); ctx.textAlign = "left"; ctx.fillStyle = hot ? "#58a6ff" : "rgba(220,200,150,0.85)";
          ctx.fillText("the Lines", a + 6, y - 7);
        }
      }
    }
    // the Hollows, scattered through the belt
    const hotH = selected === HOLLOWS || selected === BELT;
    if ((!crowd && !moonState) || hotH) {
      const r = hollowR();
      ctx.globalAlpha = selected && selected.aogPower ? aogAlpha("tied") : 1;
      for (const h of AOG_HOLLOWS) {
        const [x, y] = hollowPos(h);
        if (x > -10 && x < W + 10) icoHollow(ctx, x, y, r * h.s);
      }
      ctx.globalAlpha = 1;
      const [lx, ly] = hollowsLabelPos();
      if (ease(m) < 0.5 || hotH) {
      ctx.font = FONT(10.5); ctx.textAlign = "left";
      ctx.fillStyle = selected === HOLLOWS ? "#58a6ff" : "rgba(220,190,150,0.9)";
      ctx.fillText("the Hollows", lx, ly);
      ctx.font = FONT(9.5); ctx.fillStyle = "rgba(150,165,195,0.8)";
      ctx.fillText("about 100", lx, ly + 12);
      }
    }
    // the Cyclers, on one loop that crosses Earth's orbit and Mars's
    const hotC = selected === CYCLERS;
    if ((!crowd && !moonState) || hotC) {
      const g = cyclerGeom();
      if (g.b > -20 && g.a < W + 20) {
        ctx.strokeStyle = hotC ? "#58a6ff" : "rgba(214,160,110,0.6)"; ctx.lineWidth = hotC ? 1.5 : 1.1;
        ctx.globalAlpha = selected && selected.aogPower ? 0.2 : 1;
        ctx.beginPath(); ctx.ellipse(g.cx, y0, g.rx, g.ry, 0, 0, 2 * Math.PI); ctx.stroke();
        // the direction of travel, counterclockwise as drawn
        const [tx, ty] = cyclerPos(g, Math.PI / 2);
        ctx.fillStyle = ctx.strokeStyle;
        ctx.beginPath(); ctx.moveTo(tx - 5, ty); ctx.lineTo(tx + 2, ty - 3.5); ctx.lineTo(tx + 2, ty + 3.5); ctx.fill();
        const rr = Math.max(3, Math.min(5.5, g.rx / 18));
        for (const [n, t] of AOG_CYCLERS) {
          const [x, y] = cyclerPos(g, t);
          icoHollow(ctx, x, y, rr);
          if (g.rx > 45 || hotC) {
            ctx.font = FONT(10); ctx.fillStyle = "rgba(220,200,175,0.9)";
            const below = Math.sin(t) < 0;
            ctx.textAlign = "center";
            ctx.fillText(n, x, below ? y + rr + 11 : y - rr - 5);
          }
        }
        ctx.globalAlpha = 1;
        if (g.rx > 45 || hotC) {
          ctx.font = FONT(10.5); ctx.textAlign = "center"; ctx.fillStyle = hotC ? "#58a6ff" : "rgba(220,190,150,0.9)";
          ctx.fillText("the Cyclers", g.cx + g.rx * 0.35, y0 - g.ry - 6);
        }
      }
    }
  }
  // over the planets: who holds each body, the tags, and what is on each moon
  let aogLegendFor, aogTagBoxes = [];
  function aogTag(x, y, text, maxW, color, size) {
    ctx.font = FONT(size || 10);
    const lines = [].concat(...text.split("|").map(t => wrapText(t, maxW)));
    ctx.textAlign = "center"; ctx.fillStyle = color || "rgba(200,212,232,0.85)";
    lines.forEach((l, i) => ctx.fillText(l, x, y + i * ((size || 10) + 2)));
    return lines.length;
  }
  function aogDrawTop() {
    if (aogLegendFor !== selected) {
      aogLegendFor = selected;
      for (const b of aogLegend.querySelectorAll("button"))
        b.classList.toggle("on", !!(selected && selected.aogPower === b.dataset.k));
    }
    if (!em.hidden && selected !== EARTH_P) emClose();
    aogTagBoxes = [];
    const crowd = crowded();
    for (const p of PLANETS) {
      if (crowd && p !== selected) continue;
      const [x, y] = ppos(p);
      if (x < -60 || x > W + 60) continue;
      const r = Math.max(pr(p) * cam.z, 0.9);
      const rr = p.name === "Saturn" && r > 3.5 ? r * 2.1 : r;
      aogRing(x, y, rr, aogCats(p.name));
      if (orbDays > 0 || moonState && moonState.of !== p.name) continue;
      // the tags under Venus, Mars, Jupiter and Saturn
      const tag = AOG_TAGS[p.name];
      const i = PLANETS.indexOf(p), nb = [PLANETS[i - 1], PLANETS[i + 1]].filter(Boolean).map(q => Math.abs(sx(px(q)) - x));
      // on the lenient line only, where there is room; up close, always
      const gap = Math.min(...nb), zoomed = selected === p, lenient = ease(m) < 0.5;
      if (tag && (zoomed || (lenient && gap > 70))) {
        const big = zoomed && r > 30;
        const ty = y + (p.name === "Saturn" ? r * 1.1 : rr) + (big ? 26 : 18);
        if (p.name === "Mars" && !big) {
          icoSpin(ctx, x - 22, ty - 4, 5.5);
          aogTag(x + 8, ty, tag[0], 90);
        } else if (p.name === "Saturn" && !big) {
          ctx.font = FONT(10);
          tag[0].split("|").forEach((l, k) => { ctx.textAlign = "left"; ctx.fillStyle = "rgba(200,212,232,0.85)"; ctx.fillText(l, x + 8, y + rr + 14 + k * 12); });
        } else {
          if (p.name === "Mars") icoSpin(ctx, x, ty - 10, 8);
          aogTag(x, ty + (p.name === "Mars" && big ? 14 : 0), big ? tag[1] : tag[0], big ? 260 : Math.min(150, gap * 0.9), null, big ? 12 : 10);
        }
      }
      // Earth: the three cored worlds, and the panel that shows them
      if (p === EARTH_P && (zoomed || (lenient && gap > 60)) && !(zoomed && !em.hidden)) {
        let [ex, ey] = earthTagPos();
        if (zoomed) ey = y + r + 30;
        ctx.globalAlpha = aogAlpha("l5");
        icoCored(ctx, ex - 17, ey, 6.5); icoCored(ctx, ex, ey, 5);
        ctx.globalAlpha = aogAlpha("ind"); icoCored(ctx, ex + 14, ey, 4);
        ctx.globalAlpha = 1;
        ctx.font = FONT(10); ctx.textAlign = "center"; ctx.fillStyle = "#58a6ff";
        ctx.fillText("three worlds:", ex, ey + 18);
        ctx.fillText("the Earth–Moon panel", ex, ey + 30);
        const w = ctx.measureText("the Earth–Moon panel").width;
        aogTagBoxes.push({ x0: ex - w / 2 - 4, x1: ex + w / 2 + 4, y0: ey - 8, y1: ey + 34, o: "em" });
      }
    }
    if (orbDays === 0) {
      const beltW = sx(BELT.edgeOut()) - sx(BELT.edgeIn());
      for (const b of [CERES, VESTA, PSYCHE, HYGIEA]) {
        if (crowd && b !== selected) continue;
        const x = sx(px(b)); if (x < -40 || x > W + 40) continue;
        const r = Math.max(pr(b) * cam.z, 1.1);
        aogRing(x, y0 + smallDy(b), r < 3.5 ? r + 3.5 : r, aogCats(b.name));
        const t = AOG_BELT_TAGS[b.name];
        if (t && ((beltW > 300 && ease(m) < 0.5) || selected === b)) aogTag(x + (t[2] || 0), y0 + smallDy(b) + Math.max(r, 4) + 20 + t[1], t[0], 120, "rgba(225,205,160,0.9)");
      }
      for (const t of trojanSpots()) {
        if (crowd) continue;
        aogRing(t.x, t.y, t.r * 1.5, ["l5"]);
        if (t.ahead && (t.r >= 9 || selected === TROJANS)) {
          icoTown(ctx, t.x - t.r * 0.2, t.y - t.r * 0.1, 3, AOG_HOLD.l5.color);
          ctx.font = FONT(10); ctx.textAlign = "left"; ctx.fillStyle = "rgba(190,205,235,0.7)";
          ctx.fillText("Hektor, in the L4 swarm", t.x + t.r * 1.6 + 4, t.y + 16);
        }
      }
    }
    if (!moonState) return;
    // the settlement on each moon, above it; neighbors that would touch step up
    let lastRight = -1e9, lift = 0;
    ctx.font = FONT(10);
    for (const mo of moonState.moons) {
      const d = AOG_MOONS[mo.n];
      if (!d || mo.x < -40 || mo.x > W + 40) continue;
      aogRing(mo.x, y0, mo.r, [d[0]]);
      const w = ctx.measureText(d[1]).width;
      lift = mo.x - w / 2 < lastRight + 6 ? lift + 12 : 0;
      lastRight = mo.x + w / 2;
      ctx.textAlign = "center"; ctx.globalAlpha = aogAlpha(d[0]);
      ctx.fillStyle = AOG_HOLD[d[0]].color;
      ctx.fillText(d[1], mo.x, y0 - mo.r - 9 - lift);
      ctx.globalAlpha = 1;
    }
  }
  // the moon hover card gets a line for who is there
  function aogMoonLines(n) {
    const d = AOG_MOONS[n];
    return d ? ["In 2500: " + d[1] + ", " + d[2]] : [];
  }
  // the right edge of the room left for Earth and its Moon when the panel is open
  function aogPadRight(obj) { return obj === EARTH_P && !em.hidden ? em.offsetWidth + 250 : 0; }
  // clicks on the Sun zone, the Gate, the Lines, the Hollows, the Cyclers
  // and the Earth tag
  function aogHit(mx, my, hit) {
    if (orbDays > 0) return hit;
    const hh = beltHalfHeight();
    const xs = sx(zoneX(0.1));
    if (Math.abs(xs - mx) < 7 && Math.abs(my - y0) < hh) hit = SUNZONE;
    for (const [, au, , side] of ZONE_STATIONS) {
      const x = sx(zoneX(au)), y = y0 + side * 16;
      if (Math.hypot(x - mx, y - my) < 8) hit = SUNZONE;
    }
    const [gx, gy] = aogGatePos();
    if (Math.hypot(gx - mx, gy - my) < 12) hit = GATE;
    const ly = aogLinesY();
    if (Math.abs(my - ly) < 6 && mx > sx(px(EARTH_P)) && mx < sx(px(PSYCHE_REF))) hit = LINES;
    if (!crowded() && !moonState) {
      const r = hollowR();
      // the Hollows and the Cyclers give way to any body under the pointer
      if (!hit || hit === BELT) {
        for (const h of AOG_HOLLOWS) { const [x, y] = hollowPos(h); if (Math.hypot(x - mx, y - my) < r * h.s + 2) hit = HOLLOWS; }
      }
      const [hx, hy] = hollowsLabelPos();
      if (mx > hx - 2 && mx < hx + 62 && my > hy - 11 && my < hy + 15) hit = HOLLOWS;
      if (!hit) {
        const g = cyclerGeom();
        const e = Math.hypot((mx - g.cx) / g.rx, (my - y0) / g.ry);
        if (Math.abs(e - 1) * Math.min(g.rx, g.ry) < 5) hit = CYCLERS;
        for (const [, t] of AOG_CYCLERS) { const [x, y] = cyclerPos(g, t); if (Math.hypot(x - mx, y - my) < 8) hit = CYCLERS; }
      }
    }
    for (const b of aogTagBoxes) if (mx > b.x0 && mx < b.x1 && my > b.y0 && my < b.y1) hit = EARTH_P;
    return hit;
  }
  function aogDbg() {
    const [gx, gy] = aogGatePos(), g = cyclerGeom();
    return { sails: sx(zoneX(0.1)), zone: [sx(zoneX(0.3)), sx(zoneX(0.35))], gate: [gx, gy],
             lines: { y: aogLinesY(), a: sx(px(EARTH_P)), b: sx(px(PSYCHE_REF)) },
             psyche: sx(px(PSYCHE)), hygiea: sx(px(HYGIEA)), mercury: sx(px(PLANETS[0])),
             sunEdge: sx(sunR()), shown: !aogBox.hidden, legend: aogLegend.children.length,
             icons: aogIcons.children.length, lights: AOG_LIGHTS.length,
             hollows: AOG_HOLLOWS.map(hollowPos), hollowsLabel: hollowsLabelPos(),
             belt: [sx(BELT.edgeIn()), sx(BELT.edgeOut())],
             cyclers: { a: g.a, b: g.b, earth: sx(px(EARTH_P)), mars: sx(px(MARS_P)), ry: g.ry,
                        at: AOG_CYCLERS.map(([n, t]) => [n].concat(cyclerPos(g, t))) },
             earthTag: aogTagBoxes.map(b => [(b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2]),
             em: em.hidden ? null : emItems.map(it => it.t.split(/[,:;.]/)[0]), emGeo,
             emTips: Object.values(EM_TIP) };
  }
