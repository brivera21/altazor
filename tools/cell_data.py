#!/usr/bin/env python3
"""The data behind cell.html: three cells and their parts, with the figures.

Sizes and counts are the round numbers of Milo and Phillips (2015), Cell
Biology by the Numbers, and its BioNumbers database, with Alberts and others
(2022) for what each part does. A typical animal cell is taken as 15 microns
across, a leaf mesophyll cell as 40 by 20, E. coli as 2 by 0.8; real cells of
each kind vary by a factor of two or more around these.
"""

import apa

# k, name, long axis in microns, short axis, what it is
CELLS = [
    ("animal", "An animal cell", 15, 15,
     "A typical human cell, a fibroblast or a liver cell, fifteen microns across: three thousand cubic microns holding some ten billion protein molecules and two metres of DNA."),
    ("plant", "A plant cell", 40, 20,
     "A leaf mesophyll cell, forty microns by twenty, boxed in a wall and mostly a water-filled vacuole, with the chloroplasts pressed against the edge where the light is."),
    ("bacterium", "A bacterium", 2.0, 0.8,
     "Escherichia coli, two microns long: a two thousandth of the animal cell's volume, no nucleus, no compartments, and a division every twenty minutes when fed."),
]

# the parts, per cell: k, cell, name, size text, count text, share, role, source
PARTS = [
    # ---- animal ----
    ("a_membrane", "animal", "Plasma membrane", "about 7 nm thick, 4 nm of lipid", "one, 700 square microns", "a thousandth of the cell's width",
     "A double layer of lipids with proteins studded through it, the boundary of the cell. Drawn here as a line because at true thickness it would be a fifth of a pixel.", "Milo and Phillips 2015; Alberts 2022"),
    ("a_nucleus", "animal", "Nucleus", "about 6 microns across", "one", "about a tenth of the volume",
     "The DNA, two metres of it in 46 chromosomes, wound onto proteins and wrapped in a double membrane with pores. Every gene the cell will ever read is in here.", "Milo and Phillips 2015"),
    ("a_nucleolus", "animal", "Nucleolus", "1 to 2 microns", "one to a few", "",
     "Where ribosomes are built, from RNA copied off hundreds of repeated genes. The densest thing in the nucleus.", "Alberts 2022"),
    ("a_mito", "animal", "Mitochondrion", "0.5 to 1 micron wide, 1 to 4 long", "1,000 to 2,000 in a liver cell", "about a fifth of the volume",
     "Where sugar and oxygen become ATP, the cell's energy currency. A bacterium taken in two billion years ago, with its own small genome still. Only a few are drawn.", "Milo and Phillips 2015"),
    ("a_er", "animal", "Endoplasmic reticulum", "sheets and tubes, 50 nm across", "one continuous network", "about half the cell's membrane",
     "A folded membrane running from the nucleus through the cell. The rough part, studded with ribosomes, makes proteins for export and the membrane; the smooth part makes lipids.", "Alberts 2022"),
    ("a_golgi", "animal", "Golgi apparatus", "a stack about 1 micron across", "one, of four to eight cisternae", "",
     "Where proteins from the ER are finished, sorted and packed into vesicles for the membrane, for export, or for the lysosomes.", "Alberts 2022"),
    ("a_lyso", "animal", "Lysosome", "0.1 to 1 micron", "a few hundred", "",
     "Acid bags of enzymes that break down worn-out parts and what the cell swallows. The cell's recycling.", "Alberts 2022"),
    ("a_ribo", "animal", "Ribosomes", "25 nm", "about 10 million", "",
     "The machines that read RNA and build proteins, a hundred amino acids a minute each. Drawn as a stipple: each is a third of a pixel here.", "Milo and Phillips 2015"),
    ("a_cyto", "animal", "Cytoskeleton", "microtubules 25 nm, actin 7 nm", "thousands of filaments", "",
     "The scaffolding: microtubules from the centre out, actin under the membrane. It holds the shape, moves the organelles and pulls the chromosomes apart at division.", "Alberts 2022"),
    ("a_centro", "animal", "Centrosome", "two rods, 0.4 microns long", "one", "",
     "The point the microtubules grow from, two barrels at right angles beside the nucleus; it doubles before the cell divides.", "Alberts 2022"),
    ("a_vesicle", "animal", "Vesicles", "50 to 100 nm", "thousands", "",
     "Membrane bubbles carrying cargo between the ER, the Golgi, the membrane and the lysosomes.", "Alberts 2022"),
    ("a_cytosol", "animal", "Cytosol", "the space between", "", "about half the volume",
     "Water with a protein in every few nanometres: a fifth of the mass is protein, crowded enough that diffusion is slow.", "Milo and Phillips 2015"),
    # ---- plant ----
    ("p_wall", "plant", "Cell wall", "0.1 to 1 micron thick", "one", "",
     "Cellulose fibres in a matrix, outside the membrane, which is why plants stand up without a skeleton and why cells cannot move.", "Alberts 2022"),
    ("p_membrane", "plant", "Plasma membrane", "about 7 nm", "one", "",
     "Pressed against the wall from inside by the pressure of the vacuole.", "Alberts 2022"),
    ("p_vacuole", "plant", "Central vacuole", "most of the cell", "one", "30 to 90 percent of the volume",
     "A bag of water and salts under pressure, which is what makes a leaf stiff and a wilted plant limp. Cheap volume: growing large without making more cytoplasm.", "Milo and Phillips 2015"),
    ("p_chloro", "plant", "Chloroplast", "5 microns by 2", "50 to 100 in a leaf cell", "",
     "Where light becomes sugar. Another captured bacterium, a cyanobacterium, with its own genome; its stacked membranes hold the chlorophyll.", "Milo and Phillips 2015"),
    ("p_nucleus", "plant", "Nucleus", "about 5 microns", "one", "",
     "Pushed to one side by the vacuole, otherwise as in the animal cell.", "Alberts 2022"),
    ("p_mito", "plant", "Mitochondria", "about 1 micron", "a few hundred", "",
     "Present in plants too: chloroplasts make the sugar, mitochondria burn it, day and night.", "Alberts 2022"),
    ("p_er", "plant", "Endoplasmic reticulum and Golgi", "as in the animal cell", "", "",
     "The same protein and membrane factories, in the thin layer of cytoplasm between vacuole and wall.", "Alberts 2022"),
    ("p_plasmo", "plant", "Plasmodesmata", "channels 50 nm across", "thousands per cell", "",
     "Pores through the wall joining neighbouring cells' cytoplasm, so a plant is in a sense one connected cell.", "Alberts 2022"),
    # ---- bacterium ----
    ("b_envelope", "bacterium", "Envelope", "about 30 nm: two membranes and a wall between", "one", "",
     "An inner membrane, a thin wall of peptidoglycan, and an outer membrane. Gram-negative; the wall is what penicillin attacks.", "Milo and Phillips 2015"),
    ("b_nucleoid", "bacterium", "Nucleoid", "fills the middle", "one chromosome, 4.6 million bases", "",
     "The DNA, a single loop 1.6 millimetres long folded a thousandfold into a cell two microns long, with no membrane around it.", "Milo and Phillips 2015"),
    ("b_ribo", "bacterium", "Ribosomes", "20 nm", "20,000 to 70,000", "about a quarter of the dry mass",
     "The faster the bacterium grows, the more of it is ribosome. Each is drawn here, roughly to scale.", "Milo and Phillips 2015"),
    ("b_flagellum", "bacterium", "Flagellum", "20 nm thick, 5 to 10 microns long", "four to ten", "",
     "A rotating helix driven by a motor in the membrane, spinning a hundred times a second. Several times longer than the cell; drawn cut off.", "Milo and Phillips 2015"),
    ("b_pili", "bacterium", "Pili", "a few nanometres thick, up to a micron long", "hundreds", "",
     "Hairs for gripping surfaces and other cells, and for passing DNA.", "Alberts 2022"),
    ("b_plasmid", "bacterium", "Plasmid", "a few thousand bases", "none to dozens", "",
     "Small extra loops of DNA, traded between bacteria; how antibiotic resistance travels.", "Alberts 2022"),
    ("b_cytoplasm", "bacterium", "Cytoplasm", "the rest", "about 3 million protein molecules", "",
     "Everything happens in one compartment: no nucleus, no organelles, and a protein density about the same as in our cells.", "Milo 2013"),
]

# the extras on the shared scale: name, long axis microns, short axis, kind of drawing
EXTRAS = [
    ("rbc", "a red blood cell", 7.8, 2.0, "disc",
     "A disc with no nucleus at all, made to bend through capillaries."),
    ("yeast", "a yeast cell", 4.0, 4.0, "round",
     "Baker's yeast, a eukaryote as small as cells of our kind get."),
    ("egg", "a human egg cell", 120, 120, "arc",
     "The largest human cell, a hundred and twenty microns: its edge alone fits on this stage."),
    ("virus", "a coronavirus", 0.1, 0.1, "dot",
     "A hundred nanometres, which at this scale is one pixel."),
]

FACTS = [
    ("cells in a body", "about 30 trillion", "Sender, Fuchs and Milo 2016"),
    ("bacteria in and on it", "about as many again", "Sender, Fuchs and Milo 2016"),
    ("protein molecules in one animal cell", "about 10 billion", "Milo 2013"),
    ("DNA in one animal cell, unwound", "about 2 metres", "Milo and Phillips 2015"),
]

REFS = [
    (apa.book("Milo, R., &amp; Phillips, R.", 2015, "Cell biology by the numbers", "Garland Science",
              "http://book.bionumbers.org/"),
     "The sizes, counts and shares, and the database behind them."),
    (apa.book("Alberts, B., Heald, R., Johnson, A., Morgan, D., Raff, M., Roberts, K., &amp; Walter, P.", 2022,
              "Molecular biology of the cell (7th ed.)", "W. W. Norton"),
     "What each part does."),
    (apa.article("Sender, R., Fuchs, S., &amp; Milo, R.", 2016,
                 "Revised estimates for the number of human and bacteria cells in the body",
                 "PLOS Biology", 14, 8, "e1002533", "https://doi.org/10.1371/journal.pbio.1002533"),
     "Thirty trillion cells, and about as many bacteria."),
    (apa.article("Milo, R.", 2013, "What is the total number of protein molecules per cell volume? A call to rethink some published values",
                 "BioEssays", 35, 12, "1050-1055", "https://doi.org/10.1002/bies.201300066"),
     "Two to four million protein molecules per cubic micron."),
    (apa.article("Milo, R., Jorgensen, P., Moran, U., Weber, G., &amp; Springer, M.", 2010,
                 "BioNumbers: The database of key numbers in molecular and cell biology",
                 "Nucleic Acids Research", 38, "suppl_1", "D750-D753", "https://doi.org/10.1093/nar/gkp889"),
     "The database the round numbers are drawn from."),
]
