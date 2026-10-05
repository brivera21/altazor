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
  // ---------- Armor of God, 2500 ----------
  // How things stand in the novel's solar system in the year 2500: who holds
  // each place, who lives there, and who controls what it yields. Everything
  // in this block belongs to the book, not to the real solar system.
  const AOG_HOLD = {
    l5:    { name: "The L5 nation", color: "#e9b949" },
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
      held: [["l5", "Presidio, Lowell, the Academy and the biomass stations in high orbit; L5, with the Pearl"],
             ["ind", "L4, with Yongle"],
             ["none", "The elevator and Cumbre, by treaty"],
             ["earth", "Low orbit, under a dozen flags; the Earth below"]],
      people: "About 6 billion on Earth, and falling; about 195 million in the space between Earth and the Moon",
      places: [["The Roads", "low orbit, about 60 small stations", "300,000", "Shipyards, repair, orbital manufacturing, transit between Earth and everything above", "Room, safety from debris"],
               ["Cumbre", "geostationary orbit, the top of the elevator", "200,000", "Cargo transfer, customs, tolls, warehousing; a week's climb from the ground"],
               ["Presidio", "high orbit; the capital of the L5 nation", "8 million", "Government, courts, the military and its headset pilot school, finance, the largest rectenna array in the system", "Housing on the upper decks"],
               ["Lowell", "high orbit", "4 million", "Aluminum rolling mills, steel fabrication, chemicals, shipyards, suit factories, League food", "Daylight on the lower decks, wires, union rights"],
               ["Lancaster Station, the Academy", "in Presidio's orbit", "About 2,500", "Teaching, the Net", "Students"],
               ["Arcadia and the Terraria", "six stations near L5 and Presidio", "About 50,000 each", "Meat, grain, fruit, clones, new species", "Phosphorus, nitrogen"],
               ["The Pearl", "L5, 60° behind the Moon", "180 million", "Everything: medicine, food, banking, shipbuilding, the Net's largest market, the arts", "Room on the best decks; the deep decks are crowded and dim"],
               ["Lagrange", "L5, beside the Pearl", "900,000", "Old money, shipwrights"],
               ["Yongle", "L4, 60° ahead of the Moon", "1.2 million", "Shipyards, Belt trade finance, government", "Water, nitrogen, allies"],
               ["Quito", "on the ground, on the equator", "", "The elevator's capital and the richest city on Earth's surface"]],
      res: [["Power", "the Current, caught by rectenna arrays in orbit"],
            ["Xenon", "Earth's Xenon Council, Earth's strongest lever over space"],
            ["Food", "League farms up the elevator, and more every year from the biomass stations (Meridian Foods, L5 nation)"],
            ["Medicine", "Rhine Orbital (EU) in low orbit; Halcyon (L5 nation) on the Pearl"],
            ["Banking", "Wexley Express (L5 nation)"],
            ["The elevator", "owned by treaty; the Latin American League owns its ground half"],
            ["What the machines left", "the Agency, a government body, licenses all salvage"]]
    },
    "Mars": {
      held: [["l5", "The L5 nation, Phobos included"]],
      people: "3.5 million",
      places: [["Gateway", "Mars orbit; the largest city at Mars", "2 million", "Outfitting for the Belt, the Lines, shipyards, propellant works"],
               ["Mangala", "Hellas basin, domed and buried", "300,000", "Farming under glass, argon from the air, water ice", "Shielding, nitrogen, full gravity"],
               ["Dwarka", "Phobos, hollowed out", "400,000", "Port, customs, fuel from Martian water, the Lines' Mars junction", "Gravity, room"]],
      res: [["Propellant", "Delmont Chemical (L5 nation), at Gateway"]]
    },
    "Asteroid Belt": {
      held: [["l5", "Ceres, Psyche and the inner Belt"], ["ind", "Vesta"], ["tied", "The outer Belt"]],
      people: "About 11 million",
      places: [["Piazzi", "Ceres; the capital of the Belt", "2.5 million"],
               ["Kaap", "Vesta", "1.8 million"],
               ["Tianfu", "Ceres", "600,000"],
               ["Albion", "Hygiea; the capital of the outer Belt", "500,000"],
               ["Ironton", "Psyche", "150,000"],
               ["The outer Belt", "about a hundred settled rocks", "3 million"]],
      res: [["Precious metals", "Consolidated Platinum (L5 nation and Belt investors), losing its grip"],
            ["Steel", "United Belt Steel (L5 nation), still big, no longer dominant"],
            ["Water", "Ceres"],
            ["Uranium", "Hygiea Mining (outer Belt), privately owned"],
            ["Routes", "the Lines, ending at Piazzi"]]
    },
    "Ceres": {
      held: [["l5", "The L5 nation"]],
      people: "3.1 million",
      places: [["Piazzi", "in orbit and on the surface; the capital of the Belt", "2.5 million", "Belt finance, the precious-metal selling office, the Lines' Belt terminus, shipyards, water", "Housing"],
               ["Tianfu", "buried in the icy crust", "600,000", "Water and fuel, the Belt's oldest shipyard", "Sunlight, metal, warmth"]]
    },
    "Vesta": {
      held: [["ind", "An independent republic"]],
      people: "1.8 million",
      places: [["Kaap", "a buried city and a cored station", "1.8 million", "Refueling, repair and food for the Jupiter run, the uranium trade, the Belt's best hospitals", "Water, shipped from Ceres; justice between its two peoples"]]
    },
    "Psyche": {
      held: [["l5", "The L5 nation"]],
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
      held: [["l5", "The L5 nation"]],
      people: "900,000",
      places: [["Hektor", "624 Hektor, the largest Trojan", "700,000", "Ice, rare volatiles, the outer Lines, gambling", "Sunlight, law, warmth"],
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
      res: [["Hydrocarbons", "the pieces of Titan Standard (L5 nation), and Shell-Titan (EU and the US-led bloc)"],
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
    "The Moon": ["ind", "Guanghan, Yinshan, Peary", "4 million; the Moon republics, and Peary on its own"],
    "Phobos":   ["l5", "Dwarka", "400,000; the L5 nation"],
    "Io":       ["ind", "Loki", "40,000 on rotation; the Jupiter republic"],
    "Europa":   ["ind", "Conamara", "1.5 million; independent"],
    "Ganymede": ["ind", "Yongning", "2.2 million; independent"],
    "Callisto": ["ind", "Valhalla", "6 million; the Jupiter republic's capital"],
    "Mimas":    ["l5", "Mimas Station", "5,000; the L5 nation's Ring Wardens"],
    "Enceladus":["none", "six stations", "about 2,000; owned by no one"],
    "Titan":    ["tied", "Port Kraken, Ligeia, Huygens", "7.4 million; federated Titan"],
    "Phoebe":   ["earth", "Refuge", "60; the US-led bloc"],
    "Titania":  ["ind", "New Arden", "900,000; the Titania state"],
    "Triton":   ["none", "Far Station", "300; unclaimed"]
  };
  AOG["The Moon"] = {
    held: [["ind", "The Moon republics"], ["ind", "Peary, a republic of its own, close to the L5 nation"]],
    people: "4 million",
    places: [["Guanghan", "the south pole, along Shackleton's rim; the capital", "2.5 million", "Ice, oxygen, mass drivers, aluminum smelting, launch rails", "Nitrogen, carbon, full gravity, sunlight below ground"],
             ["Yinshan", "a south-polar crater in permanent shadow", "600,000", "Machine-core maintenance, salvage; the ice is mostly gone", "Ice, work"],
             ["Peary", "Peary crater, the north pole", "600,000", "Ice, construction, a mass driver", "Nitrogen, carbon"]],
    res: [["Ice and oxygen", "the Moon republics"],
          ["Construction", "Lunar Works, owned by the Moon republics; Moonstone Consortium (US–EU bloc) at Peary"],
          ["Aluminum", "Procellarum Aluminum (L5 nation), smelting at Guanghan"]]
  };

  // The places that are not bodies: the Sun zone, the Gate, the Lines.
  const SUNZONE = {
    name: "The Sun Zone", type: "Sails, Lighthouses and collector stations inside Mercury's orbit", aogOnly: true, auIn: 0.1, auOut: 0.35,
    aog: {
      held: [["ind", "Azadi, Shuixing and the other Sun-zone states"], ["l5", "Taeyang; the Lighthouses by treaty and contract"], ["earth", "Hinode (EU) and India's small stations"]],
      people: "About 2 million",
      places: [["The Sails", "0.1 au, in loose swarms", "", "Thousands of collectors of film microns thick, hundreds to thousands of kilometers wide, circling the Sun every 11.5 days"],
               ["The Lighthouses", "0.1 au, about 40 stations inside the swarms", "About 12,000 Keepers, on rotations of six to twelve months", "The Current: beams that carry the Sun's power across the system; drone repair", "Everything: shielding, time outside, songs"],
               ["Azadi", "0.3 au", "1.5 million", "Solar collection sold into the Current, collector repair; poor", "Water, food, shielding, everything but power"],
               ["Taeyang", "0.3 au", "120,000", "Collectors; where the rich of the Pearl come to see the Sun up close", "Water, shade"],
               ["Hinode", "0.35 au", "80,000", "Collectors, precision optics", "Water, people"]],
      notes: ["The Sun is slightly dimmer than it used to be, behind the Sails"],
      res: [["Power", "General Current (L5 nation) runs most of the Current and holds most Lighthouse contracts; Ashworth Electric (L5 nation) is up for sale"]]
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
      held: [["l5", "One great line company, chartered by the L5 nation"]],
      places: [["Freight", "pods on fixed arcs", "", "Cheap and slow, unmanned: metal, ice, goods. Easy to find, and robbed"],
               ["Express", "crewed ships", "", "Fast and expensive, on solar propulsion"],
               ["Stations", "launchers, catchers, relays", "", "Gateway at Mars, Piazzi at the Belt end"]],
      res: [["Security", "patrols, private guards and old feuds; the Academy's patrols among them"]]
    }
  };
  const PSYCHE_REF = PSYCHE, EARTH_P = PLANETS.find(q => q.name === "Earth"), MARS_P = PLANETS.find(q => q.name === "Mars");

  // the five kinds of holder, each a panel of its own
  const AOG_POWERS = {
    l5: { held: [["l5", "L5: the Pearl and Lagrange"], ["l5", "High Earth orbit: Presidio, the capital; Lowell; the Academy; the biomass stations"],
                 ["l5", "Mars and Phobos"], ["l5", "Ceres, Psyche and the inner Belt"], ["l5", "The Jupiter Trojans"],
                 ["l5", "Taeyang and Caloris; the Lighthouses by treaty and contract"], ["l5", "Saturn's rings, protected"]],
          res: [["Power", "General Current; Ashworth Electric, up for sale"], ["Metals", "Procellarum Aluminum, United Belt Steel, Consolidated Platinum (with Belt investors)"],
                ["Chemicals", "Delmont Chemical"], ["Medicine", "Halcyon"], ["Food", "Meridian Foods; United Harvest, diminished"],
                ["Hydrocarbons", "the pieces of Titan Standard"], ["Banking", "Wexley Express"], ["Routes", "the Lines"]],
          notes: ["The dominant power in space"] },
    ind: { held: [["ind", "The Moon republics, and Peary"], ["ind", "L4 (Yongle)"], ["ind", "Venus"], ["ind", "Azadi, Shuixing and the other Sun-zone states"],
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
    return [...new Set(d.held.map(h => h[0]))];
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
    for (const [k, t] of d.held) {
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

  // ----- drawing -----
  // the Sun zone: on the lenient line it fills the gap between the Sun's
  // edge and Mercury; at true scale it is at its real distance
  function zoneX(au) {
    const mq = PLANETS[0];
    const len = LEN_SUN_R + (au / mq.au) * (mq.xLen - mq.lenR - LEN_SUN_R);
    return mix(len, au * AU * KM2U, ease(m));
  }
  const AOG_SAILS = (() => {
    let st = 2500;
    const rnd = () => (st = (st * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
    return Array.from({ length: 150 }, () => ({ v: rnd() * 2 - 1, dx: (rnd() - 0.5) * 2, w: 0.6 + rnd() * 1.6, lit: rnd() < 0.06 }));
  })();
  const ZONE_STATIONS = [["Azadi", 0.3, "ind", -1], ["Taeyang", 0.3, "l5", 1], ["Hinode", 0.35, "earth", -1]];
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
  // under the planets: the Sun zone, the Gate, the Lines
  function aogDraw() {
    if (orbDays > 0) return;
    const hh = beltHalfHeight(), crowd = crowded();
    // the Sails, a curtain at 0.1 au, with the Lighthouses lit among them
    const xs = sx(zoneX(0.1)), hotZ = selected === SUNZONE;
    if (xs > -40 && xs < W + 40 && (!crowd || hotZ)) {
      for (const s of AOG_SAILS) {
        ctx.fillStyle = s.lit ? "#fff1c2" : "rgba(255,196,110,0.5)";
        ctx.globalAlpha = (s.lit ? 0.95 : 0.55) * (selected && selected.aogPower ? aogAlpha(s.lit ? "l5" : "none") : 1);
        ctx.fillRect(xs + s.dx * 3, y0 + s.v * hh, s.lit ? 2.2 : s.w, s.lit ? 2.2 : 0.8);
      }
      ctx.globalAlpha = 1;
      ctx.font = "11px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
      ctx.textAlign = "center";
      ctx.fillStyle = hotZ ? "#58a6ff" : "rgba(190,205,235,0.85)";
      ctx.fillText("the Sails", xs, y0 - hh - 8);
      // the collector stations, off the line on either side
      const x3 = sx(zoneX(0.3)), x35 = sx(zoneX(0.35));
      if (x35 - xs > 24 || hotZ) {
        for (const [n, au, k, side] of ZONE_STATIONS) {
          const x = sx(zoneX(au)), y = y0 + side * (n === "Hinode" ? 30 : 16);
          ctx.globalAlpha = aogAlpha(k);
          ctx.fillStyle = AOG_HOLD[k].color;
          ctx.beginPath(); ctx.moveTo(x, y - 3.5); ctx.lineTo(x + 3.5, y); ctx.lineTo(x, y + 3.5); ctx.lineTo(x - 3.5, y); ctx.fill();
          ctx.globalAlpha = 1;
          if (x35 - xs > 70 || hotZ) {
            ctx.font = "10px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
            ctx.textAlign = "left"; ctx.fillStyle = "rgba(200,210,230,0.8)";
            ctx.fillText(n, x + 6, y + 3);
          }
        }
      }
    }
    // the Gate, under the Sun, since it is on the Sun's far side
    if (!crowd || selected === GATE) {
      const [gx, gy] = aogGatePos();
      if (gx > -40 && gx < W + 40) {
        const g = ctx.createRadialGradient(gx, gy, 3, gx, gy, 12);
        g.addColorStop(0, "rgba(255,140,100,0.35)"); g.addColorStop(1, "rgba(255,140,100,0)");
        ctx.fillStyle = g; circle(gx, gy, 12); ctx.fill();
        ctx.fillStyle = "#000"; circle(gx, gy, 6); ctx.fill();
        ctx.strokeStyle = selected === GATE ? "#58a6ff" : "rgba(255,170,130,0.6)"; ctx.lineWidth = 1;
        circle(gx, gy, 6.5); ctx.stroke();
        ctx.font = "10.5px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
        ctx.textAlign = "center"; ctx.fillStyle = selected === GATE ? "#58a6ff" : "rgba(190,205,235,0.8)";
        ctx.fillText("the Gate", gx, gy + 22);
        ctx.font = "10px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
        ctx.fillStyle = "rgba(150,165,195,0.8)";
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
          ctx.font = "10.5px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
          ctx.textAlign = "left"; ctx.fillStyle = hot ? "#58a6ff" : "rgba(220,200,150,0.85)";
          ctx.fillText("the Lines", a + 6, y - 7);
        }
      }
    }
  }
  // over the planets: who holds each body, and what is on each moon
  let aogLegendFor;
  function aogDrawTop() {
    if (aogLegendFor !== selected) {
      aogLegendFor = selected;
      for (const b of aogLegend.querySelectorAll("button"))
        b.classList.toggle("on", !!(selected && selected.aogPower === b.dataset.k));
    }
    const crowd = crowded();
    for (const p of PLANETS) {
      if (crowd && p !== selected) continue;
      const [x, y] = ppos(p);
      if (x < -60 || x > W + 60) continue;
      const r = Math.max(pr(p) * cam.z, 0.9);
      aogRing(x, y, p.name === "Saturn" && r > 3.5 ? r * 2.1 : r, aogCats(p.name));
    }
    if (orbDays === 0) {
      for (const b of [CERES, VESTA, PSYCHE, HYGIEA]) {
        if (crowd && b !== selected) continue;
        const x = sx(px(b)); if (x < -40 || x > W + 40) continue;
        const r = Math.max(pr(b) * cam.z, 1.1);
        aogRing(x, y0 + smallDy(b), r < 3.5 ? r + 3.5 : r, aogCats(b.name));
      }
      for (const t of trojanSpots()) if (!crowd) aogRing(t.x, t.y, t.r * 1.5, ["l5"]);
    }
    if (!moonState) return;
    // the settlement on each moon, above it; neighbors that would touch step up
    let lastRight = -1e9, lift = 0;
    ctx.font = "10px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
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
    // L4 and L5 share the Moon's orbit, 60 degrees ahead of it and 60 behind;
    // on this line they are drawn above and below the Moon, like the Trojans
    if (moonState.of === "Earth" && moonState.moons.length) {
      const mo = moonState.moons[0];
      for (const [lab, sub, k, side] of [["L4 · Yongle", "60° ahead of the Moon", "ind", -1], ["L5 · the Pearl", "60° behind the Moon", "l5", 1]]) {
        const y = y0 + side * (mo.r + (side < 0 ? 46 : 74));
        ctx.globalAlpha = aogAlpha(k);
        ctx.fillStyle = AOG_HOLD[k].color;
        ctx.beginPath(); ctx.moveTo(mo.x, y - 5); ctx.lineTo(mo.x + 5, y); ctx.lineTo(mo.x, y + 5); ctx.lineTo(mo.x - 5, y); ctx.fill();
        ctx.globalAlpha = 1;
        ctx.font = "11px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
        ctx.textAlign = "left"; ctx.fillStyle = "rgba(220,228,245,0.9)";
        ctx.fillText(lab, mo.x + 10, y + 1);
        ctx.font = "10px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
        ctx.fillStyle = "rgba(150,165,195,0.85)";
        ctx.fillText(sub, mo.x + 10, y + 13);
      }
    }
  }
  // the moon hover card gets a line for who is there
  function aogMoonLines(n) {
    const d = AOG_MOONS[n];
    return d ? ["In 2500: " + d[1] + ", " + d[2]] : [];
  }
  // clicks on the Sun zone, the Gate and the Lines
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
    return hit;
  }
  function aogDbg() {
    const [gx, gy] = aogGatePos();
    return { sails: sx(zoneX(0.1)), zone: [sx(zoneX(0.3)), sx(zoneX(0.35))], gate: [gx, gy],
             lines: { y: aogLinesY(), a: sx(px(EARTH_P)), b: sx(px(PSYCHE_REF)) },
             psyche: sx(px(PSYCHE)), hygiea: sx(px(HYGIEA)), mercury: sx(px(PLANETS[0])),
             sunEdge: sx(sunR()), shown: !aogBox.hidden, legend: aogLegend.children.length };
  }
