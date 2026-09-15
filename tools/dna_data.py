#!/usr/bin/env python3
"""The data behind dna.html: the double helix's dimensions, the four bases,
the genetic code, a real gene to read, and the human genome's chromosomes.

The helix is B-DNA as Watson and Crick described it and Franklin measured
it: 2 nm across, 0.34 nm a base pair, 10.5 pairs and so 3.6 nm a turn in the cell
(Watson and Crick's model had ten pairs and 3.4 nm). The genetic code is the
standard one. The gene is the start of beta-globin, HBB, with the sickle
cell mutation as a preset. Chromosome lengths are GRCh38 and gene counts
are the protein-coding counts the Wikipedia article carries from Ensembl.
"""

import apa

HELIX = {"width_nm": 2.0, "pitch_nm": 3.57, "bp_per_turn": 10.5, "rise_nm": 0.34, "major_nm": 2.2, "minor_nm": 1.2}

# the bases: letter, name, partner, hydrogen bonds, color, kind
BASES = [
    ("A", "adenine", "T", 2, "#58a6ff", "purine"),
    ("T", "thymine", "A", 2, "#ffb02e", "pyrimidine"),
    ("G", "guanine", "C", 3, "#9be564", "purine"),
    ("C", "cytosine", "G", 3, "#f28cb0", "pyrimidine"),
]

# the standard genetic code, codon (DNA, coding strand) to amino acid
_AA = {
    "F": ("Phe", "phenylalanine"), "L": ("Leu", "leucine"), "S": ("Ser", "serine"), "Y": ("Tyr", "tyrosine"),
    "C": ("Cys", "cysteine"), "W": ("Trp", "tryptophan"), "P": ("Pro", "proline"), "H": ("His", "histidine"),
    "Q": ("Gln", "glutamine"), "R": ("Arg", "arginine"), "I": ("Ile", "isoleucine"), "M": ("Met", "methionine"),
    "T": ("Thr", "threonine"), "N": ("Asn", "asparagine"), "K": ("Lys", "lysine"), "V": ("Val", "valine"),
    "A": ("Ala", "alanine"), "D": ("Asp", "aspartic acid"), "E": ("Glu", "glutamic acid"), "G": ("Gly", "glycine"),
    "*": ("Stop", "stop"),
}
CODE = {}
for b1, row in zip("TCAG", [
    [("TTT", "F"), ("TTC", "F"), ("TTA", "L"), ("TTG", "L"), ("TCT", "S"), ("TCC", "S"), ("TCA", "S"), ("TCG", "S"), ("TAT", "Y"), ("TAC", "Y"), ("TAA", "*"), ("TAG", "*"), ("TGT", "C"), ("TGC", "C"), ("TGA", "*"), ("TGG", "W")],
    [("CTT", "L"), ("CTC", "L"), ("CTA", "L"), ("CTG", "L"), ("CCT", "P"), ("CCC", "P"), ("CCA", "P"), ("CCG", "P"), ("CAT", "H"), ("CAC", "H"), ("CAA", "Q"), ("CAG", "Q"), ("CGT", "R"), ("CGC", "R"), ("CGA", "R"), ("CGG", "R")],
    [("ATT", "I"), ("ATC", "I"), ("ATA", "I"), ("ATG", "M"), ("ACT", "T"), ("ACC", "T"), ("ACA", "T"), ("ACG", "T"), ("AAT", "N"), ("AAC", "N"), ("AAA", "K"), ("AAG", "K"), ("AGT", "S"), ("AGC", "S"), ("AGA", "R"), ("AGG", "R")],
    [("GTT", "V"), ("GTC", "V"), ("GTA", "V"), ("GTG", "V"), ("GCT", "A"), ("GCC", "A"), ("GCA", "A"), ("GCG", "A"), ("GAT", "D"), ("GAC", "D"), ("GAA", "E"), ("GAG", "E"), ("GGT", "G"), ("GGC", "G"), ("GGA", "G"), ("GGG", "G")],
]):
    for codon, aa in row:
        CODE[codon] = aa
AMINO = {k: {"abbr": v[0], "name": v[1]} for k, v in _AA.items()}

# the start of human beta-globin, HBB, coding strand, 30 codons
GENE = ("ATGGTGCATCTGACTCCTGAGGAGAAGTCTGCCGTTACTGCCCTGTGGGGCAAGGTGAACGTGGATGAAGTTGGTGGTGAGGCCCTGGGC")
GENE_NOTE = ("The first thirty codons of the gene for beta-globin, half of the hemoglobin that carries oxygen in blood. "
             "The methionine at the front is the start signal and is cut off later; the protein goes on for 146 amino acids.")
MUTATIONS = [
    ("sickle", "the sickle cell mutation", 19, "T", "One base, an A to a T in the seventh codon, turns glutamic acid into valine. The changed protein sticks to itself when it gives up its oxygen, the red cells bend into sickles, and they jam in small vessels. One copy of the gene protects against malaria, which is why the mutation is common where malaria is.", "Wikipedia, Sickle cell disease"),
    ("silent", "a silent change", 8, "C", "The third base of a codon often does not matter: CAT and CAC both mean histidine, so this change makes no difference to the protein. Most of the code's redundancy sits in the third position.", "Wikipedia, Synonymous substitution"),
    ("stop", "a stop", 21, "T", "A G to a T in the eighth codon turns glutamic acid into a stop signal, and the protein ends after seven amino acids. A change like this in beta-globin gives a form of thalassaemia.", "Wikipedia, Nonsense mutation"),
    ("frame", "a lost base", 4, "", "Take one base out and every codon after it is read in the wrong frame: a different protein altogether, until a stop turns up by chance. This is what makes the code's three-letter rhythm so fragile to insertions and deletions.", "Wikipedia, Frameshift mutation"),
]

# the human chromosomes, GRCh38: name, length in base pairs, protein-coding genes
CHROMOSOMES = [
    ("1", 248956422, 2058), ("2", 242193529, 1309), ("3", 198295559, 1078), ("4", 190214555, 752), ("5", 181538259, 876),
    ("6", 170805979, 1048), ("7", 159345973, 989), ("8", 145138636, 677), ("9", 138394717, 786), ("10", 133797422, 733),
    ("11", 135086622, 1298), ("12", 133275309, 1034), ("13", 114364328, 327), ("14", 107043718, 830), ("15", 101991189, 613),
    ("16", 90338345, 873), ("17", 83257441, 1197), ("18", 80373285, 270), ("19", 58617616, 1472), ("20", 64444167, 544),
    ("21", 46709983, 234), ("22", 50818468, 488), ("X", 156040895, 842), ("Y", 57227415, 71), ("MT", 16569, 13),
]
CHROMOSOME_NOTES = {
    "1": "The largest, with a twelfth of the genome and the most genes.",
    "13": "One of the three whose extra copy a person can survive, with Patau syndrome; 18 and 21 are the others.",
    "19": "Small but the densest in genes, more than a thousand of them in 59 million bases.",
    "21": "The smallest, and the one whose extra copy causes Down syndrome.",
    "X": "One copy in men, two in women, one of which is switched off in every cell.",
    "Y": "Small, mostly repetitive, carrying the gene that starts a male body and little else; it is passed from father to son unchanged, apart from mutations, which is how paternal lines are traced.",
    "MT": "The mitochondrion's own ring of DNA, 16,569 bases, 37 genes, passed only from the mother, and the last relic of the bacterium the mitochondrion once was.",
}
GENOME = {"cells": 3.7e13, "coding_share": 0.015, "genes": 20000, "note": "About 3.1 billion base pairs in one set, 6.2 billion in the two sets each cell carries; two meters of it, coiled into a nucleus six microns across, in almost every one of the body's thirty-seven trillion cells. Only about one and a half percent of it codes for protein."}

REFS = [
    (apa.article("Watson, J. D., &amp; Crick, F. H. C.", 1953, "Molecular structure of nucleic acids: A structure for deoxyribose nucleic acid",
                 "Nature", 171, 4356, "737-738", "https://doi.org/10.1038/171737a0"),
     "The double helix: two chains, the bases paired inside, 3.4 &Aring; a base and ten bases a turn."),
    (apa.article("Franklin, R. E., &amp; Gosling, R. G.", 1953, "Molecular configuration in sodium thymonucleate",
                 "Nature", 171, 4356, "740-741", "https://doi.org/10.1038/171740a0"),
     "The X-ray evidence for the helix and its dimensions."),
    (apa.article("Nirenberg, M. W., &amp; Matthaei, J. H.", 1961, "The dependence of cell-free protein synthesis in E. coli upon naturally occurring or synthetic polyribonucleotides",
                 "Proceedings of the National Academy of Sciences", 47, 10, "1588-1602", "https://doi.org/10.1073/pnas.47.10.1588"),
     "The first word of the code: UUU is phenylalanine."),
    (apa.article("International Human Genome Sequencing Consortium", 2004, "Finishing the euchromatic sequence of the human genome",
                 "Nature", 431, 7011, "931-945", "https://doi.org/10.1038/nature03001"),
     "The finished sequence, and the count of 20,000 to 25,000 genes."),
    (apa.article("Nurk, S., Koren, S., Rhie, A., Rautiainen, M., Bzikadze, A. V., Mikheenko, A., Vollger, M. R., Altemose, N., Uralsky, L., Gershman, A., Aganezov, S., Hoyt, S. J., Diekhans, M., Logsdon, G. A., Alonge, M., Antonarakis, S. E., Borchers, M., Bouffard, G. G., Brooks, S. Y., ... Phillippy, A. M.", 2022,
                 "The complete sequence of a human genome", "Science", 376, 6588, "44-53", "https://doi.org/10.1126/science.abj6987"),
     "The gapless sequence, 3.055 billion base pairs."),
    (apa.article("Sender, R., Fuchs, S., &amp; Milo, R.", 2016, "Revised estimates for the number of human and bacteria cells in the body",
                 "PLOS Biology", 14, 8, "e1002533", "https://doi.org/10.1371/journal.pbio.1002533"),
     "Thirty-seven trillion cells."),
]
REFS += [(apa.wiki(f"https://en.wikipedia.org/wiki/{p}"), a) for p, a in [
    ("Nucleic_acid_double_helix", "The helix's width, pitch and grooves."),
    ("Genetic_code", "The table of sixty-four codons."),
    ("Human_genome", "The chromosomes, their lengths in GRCh38 and their gene counts."),
    ("HBB", "The beta-globin gene."),
    ("Sickle_cell_disease", None), ("Synonymous_substitution", None), ("Nonsense_mutation", None), ("Frameshift_mutation", None),
    ("Chromosome_1", None), ("Chromosome_19", None), ("Chromosome_21", None), ("X_chromosome", None), ("Y_chromosome", None), ("Mitochondrial_DNA", None),
]]
