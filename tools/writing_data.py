#!/usr/bin/env python3
"""The data behind writing.html: the scripts of the world and where they came
from, five letters followed from picture to alphabet, and how many signs
each kind of writing needs.

Dates are first attestations, rounded, negative for BC; the descent is the
usual one in the handbooks, with the arguable links noted.
"""

import apa

# the kinds of writing system
TYPES = {
    "logo": ("logographic", "#ffb02e", "one sign for one word or part of a word, with sound signs mixed in; thousands are needed"),
    "syll": ("syllabary", "#f28cb0", "one sign for one syllable; usually fifty to a few hundred"),
    "abjad": ("abjad", "#9be564", "one sign for one consonant, the vowels left for the reader; two or three dozen"),
    "alpha": ("alphabet", "#58a6ff", "one sign for one consonant or vowel; two or three dozen"),
    "abugida": ("abugida", "#6ee7f2", "one sign for a consonant with a vowel built in, and marks to change the vowel; a few dozen"),
    "feat": ("featural", "#c9a6ff", "the shape of the sign shows how the sound is made in the mouth"),
    "unk": ("undeciphered", "#9a9a9a", "nobody can read it"),
}

# the scripts: k, name, year (negative BC), parent, type, where, a line, still in use
SCRIPTS = [
    ("cuneiform", "Cuneiform", -3200, None, "logo", "Sumer, southern Iraq", "The first writing, or tied for it: wedges pressed into wet clay with a reed, first for counting grain and sheep in the temples of Uruk. It went on to write Sumerian, Akkadian, Hittite and Persian, and died out in the first century AD.", False),
    ("hieroglyphs", "Egyptian hieroglyphs", -3200, None, "logo", "Egypt", "Pictures that stand for words, for sounds, and for the kind of thing a word is, all at once. Read for three and a half thousand years; the last inscription was carved at Philae in 394 AD, and the key was lost until the Rosetta Stone.", False),
    ("indus", "Indus script", -2600, None, "unk", "Indus valley, Pakistan and India", "Short strings of signs on seals from the cities of the Indus, some 400 signs in all; whether it is writing at all is argued, and nobody can read it.", False),
    ("lineara", "Linear A", -1800, None, "unk", "Crete", "The script of the Minoan palaces, on clay tablets and pots. Its signs were borrowed for Linear B, so their sounds are roughly known, but the language is not, and it stays unread.", False),
    ("linearb", "Linear B", -1450, "lineara", "syll", "Crete and Greece", "The Mycenaean Greeks' script, some 87 syllable signs plus signs for things, used for palace accounts and deciphered in 1952 by Michael Ventris, an architect. It died with the palaces, and Greece was without writing for four centuries.", False),
    ("chinese", "Chinese characters", -1250, None, "logo", "China", "First seen scratched on ox bones and turtle shells for divination at Anyang, and never interrupted since: the oldest script still in use, and the parent of the writing of Japan, Korea and Vietnam.", True),
    ("maya", "Maya script", -300, None, "logo", "Guatemala, Mexico, Belize", "The most complete of the Mesoamerican scripts, and the New World's own invention: signs for words and for syllables, carved on stone and painted in books, of which four survived the Spanish. Zapotec writing came earlier, around 500 BC, and is not read.", False),
    ("protosinaitic", "Proto-Sinaitic", -1800, "hieroglyphs", "abjad", "Sinai and Egypt", "Canaanite workers in Egypt took two dozen hieroglyphs and used each for the first sound of its Semitic name: the ox, alp, for the sound a, the house, bayt, for b. Nearly every alphabet on Earth descends from these scratches at a turquoise mine.", False),
    ("ugaritic", "Ugaritic", -1300, "protosinaitic", "abjad", "Ugarit, Syria", "The Canaanite abjad written in wedges on clay, in the cuneiform manner, with thirty letters. A tablet from Ugarit lists them in nearly the order that a, b, c still follow.", False),
    ("phoenician", "Phoenician", -1050, "protosinaitic", "abjad", "Lebanon", "Twenty-two consonants, no vowels, carried by traders around the Mediterranean. The Greeks, the Aramaeans and the Hebrews all took their letters from it.", False),
    ("paleohebrew", "Paleo-Hebrew", -1000, "phoenician", "abjad", "Israel and Judah", "The script of the kings of Israel and Judah and of the earliest Bible texts, nearly the same as Phoenician. After the Babylonian exile it was replaced by the Aramaic-derived square letters, and it survives only among the Samaritans.", False),
    ("aramaic", "Aramaic", -900, "phoenician", "abjad", "Syria, then the Persian Empire", "The script of the language of trade and government from Egypt to India under the Persians. It is the parent of the Hebrew square script, of Arabic, of Syriac, and, by the usual account, of Brahmi and so of every script of India and South-East Asia.", False),
    ("southarabian", "South Arabian", -900, "protosinaitic", "abjad", "Yemen", "A separate branch from the Canaanite letters, with 29 consonants in a different order, used for the kingdoms of Saba and its neighbours. It crossed the Red Sea to become the script of Ethiopia.", False),
    ("greek", "Greek", -800, "phoenician", "alpha", "Greece", "The Phoenician letters with a change that made the first alphabet: the signs for consonants Greek did not have, aleph among them, were used for vowels. Written at first right to left, then both ways, then left to right.", True),
    ("etruscan", "Etruscan", -700, "greek", "alpha", "Tuscany", "The Etruscans took the Greek letters from the colony at Cumae; the Romans took theirs from the Etruscans. The language is only partly understood, but the letters are read easily, and one of them explains why C stands for both k and g.", False),
    ("latin", "Latin", -650, "etruscan", "alpha", "Rome, then the world", "Twenty-one letters at first, G added in the third century BC and Y and Z from Greek in the first. The lowercase letters are Charlemagne's scribes' hand of about 800 AD. Now the script of more people than any other.", True),
    ("hebrew", "Hebrew", -300, "aramaic", "abjad", "Judaea", "The square script, taken from Aramaic after the exile and used for Hebrew since, with dots and dashes for vowels added by the Masoretes around 800 AD. Also the script of Yiddish and Ladino.", True),
    ("brahmi", "Brahmi", -300, "aramaic", "abugida", "India", "The script of Ashoka's edicts, and the ancestor of nearly every script of India, Tibet and South-East Asia. Its descent from Aramaic is the usual view but not a settled one; some hold it an Indian invention.", False),
    ("nabataean", "Nabataean", -150, "aramaic", "abjad", "Petra, Jordan", "The Aramaic script as written by the Arab traders of Petra, its letters joining up into a running hand. That hand became Arabic.", False),
    ("syriac", "Syriac", 50, "aramaic", "abjad", "Edessa, Turkey", "The Aramaic script of the Christian East, carried by missionaries along the Silk Road; from it came the Sogdian, Uyghur and Mongolian scripts.", True),
    ("runes", "Runes", 150, "etruscan", "alpha", "Denmark and Germany", "The Germanic letters, from one of the alphabets of northern Italy, shaped to be cut into wood with straight strokes. Used in Scandinavia until the Middle Ages; the futhark is named from its first six letters.", False),
    ("coptic", "Coptic", 200, "greek", "alpha", "Egypt", "The last stage of the Egyptian language written in Greek letters with a few added from demotic for sounds Greek lacked. Still read in the liturgy of the Coptic church.", True),
    ("geez", "Ge'ez", 300, "southarabian", "abugida", "Ethiopia and Eritrea", "The South Arabian letters, turned into an abugida in the fourth century by marking the vowel on each consonant. The script of Amharic and Tigrinya today.", True),
    ("armenian", "Armenian", 405, "greek", "alpha", "Armenia", "Invented in 405 by the monk Mesrop Mashtots, on the Greek model with the order and much of the shape his own; 36 letters then, 39 now.", True),
    ("arabic", "Arabic", 400, "nabataean", "abjad", "Arabia, then the Islamic world", "The Nabataean running hand, made the script of the Quran and carried from Spain to Indonesia. Its 28 letters change shape by position in the word; the vowel marks are optional.", True),
    ("tibetan", "Tibetan", 650, "brahmi", "abugida", "Tibet", "Made from an Indian script in the seventh century for the translation of Buddhist texts; its spelling has not changed since the ninth, while the spoken language has.", True),
    ("devanagari", "Devanagari", 700, "brahmi", "abugida", "northern India", "The script of Sanskrit, Hindi, Marathi and Nepali, with the horizontal bar the letters hang from. Forty-seven basic signs, each consonant carrying an a unless marked otherwise.", True),
    ("khmer", "Khmer", 611, "brahmi", "abugida", "Cambodia", "An Indian script adapted for Khmer in the seventh century, and the parent of Thai and Lao. It has the most letters of any alphabet in use, and the largest, thirty-three consonants each in two series.", True),
    ("kana", "Japanese kana", 800, "chinese", "syll", "Japan", "Chinese characters cut down to their sound and simplified into two sets of about 46 signs, one syllable each, hiragana and katakana, used alongside the characters themselves.", True),
    ("cyrillic", "Cyrillic", 893, "greek", "alpha", "Bulgaria, then Russia and the Slavic world", "Greek uncials with letters added for Slavic sounds, made at the school of Preslav and named for Saint Cyril, whose own alphabet, Glagolitic, it replaced. Now the script of Russian, Ukrainian, Serbian, Bulgarian, Kazakh and more.", True),
    ("mongolian", "Mongolian", 1204, "syriac", "abjad", "Mongolia", "Taken from the Uyghurs, who had it from the Sogdians, who had it from Syriac, and turned to run top to bottom in columns. Restored to official use in Mongolia alongside Cyrillic.", True),
    ("hangul", "Hangul", 1443, None, "feat", "Korea", "Made by King Sejong and announced in 1446 so that ordinary people could write: 24 letters whose shapes draw the tongue, lips and throat making the sound, grouped into syllable blocks. The one script whose inventor and date are known exactly.", True),
    ("cherokee", "Cherokee", 1821, None, "syll", "the Cherokee Nation", "Invented by Sequoyah, who could not read English but had seen its letters; 85 signs for syllables, some shaped like Latin letters with unrelated sounds. Within a few years most of the Cherokee could read it.", True),
]

# five letters followed from picture to alphabet: k, the Latin letter, the sound, and the stages
# each stage: (name of stage, date, the sign's name, what it shows, a line, an SVG path in a 60 by 60 box)
LETTERS = [
    ("a", "A", "the ox", [
        ("Egyptian hieroglyph", -2000, "an ox's head", "F1, the head of an ox, used in Egyptian for the word for ox", "M30,52 C18,52 13,42 14,30 C16,32 44,32 46,30 C47,42 42,52 30,52 Z M14,30 L8,8 M46,30 L52,8"),
        ("Proto-Sinaitic", -1800, "'alp, ox", "the same head, now standing for the first sound of the Canaanite word for ox, a glottal stop", "M16,38 L30,54 L44,38 Z M16,38 L10,10 M44,38 L50,10"),
        ("Phoenician", -1000, "'aleph", "the head has turned on its side and lost its face; the horns are the two strokes", "M48,12 L14,30 L48,48 M26,6 L26,54"),
        ("Greek", -700, "alpha", "turned upright by the Greeks, who had no glottal stop and used the letter for the vowel a", "M12,52 L30,8 L48,52 M19,36 L41,36"),
        ("Latin", -600, "A", "unchanged since; the horns of the ox are its two legs, and its face is the crossbar", "M12,52 L30,8 L48,52 M19,36 L41,36"),
    ]),
    ("b", "B", "the house", [
        ("Egyptian hieroglyph", -2000, "a house", "O1, the plan of a house seen from above, with its doorway", "M26,46 L12,46 L12,14 L48,14 L48,46 L36,46"),
        ("Proto-Sinaitic", -1800, "bayt, house", "the plan of a house, for the first sound of the Canaanite word for house, b", "M30,14 L14,14 L14,46 L46,46 L46,14 L30,14 L30,30 L14,30"),
        ("Phoenician", -1000, "bet", "the house has closed into a loop with a stroke trailing to the left", "M34,36 L34,10 C52,10 52,32 34,32 M34,36 L18,54"),
        ("Greek", -700, "beta", "the Greeks doubled the loop and dropped the tail", "M16,10 L16,52 M16,10 L32,10 C50,10 50,30 32,30 L16,30 M32,30 C52,30 52,52 32,52 L16,52"),
        ("Latin", -600, "B", "the two rooms of a house, still: bayt is the word behind Bethlehem, the house of bread", "M16,10 L16,52 M16,10 L32,10 C50,10 50,30 32,30 L16,30 M32,30 C52,30 52,52 32,52 L16,52"),
    ]),
    ("m", "M", "the water", [
        ("Egyptian hieroglyph", -2000, "a ripple of water", "N35, a ripple, the sign for the sound n in Egyptian and the word for water", "M6,30 L12,22 L18,38 L24,22 L30,38 L36,22 L42,38 L48,22 L54,30"),
        ("Proto-Sinaitic", -1800, "maym, water", "the ripple stood on end, for the first sound of the Canaanite word for water, m", "M30,6 L38,14 L22,22 L38,30 L22,38 L38,46 L30,54"),
        ("Phoenician", -1000, "mem", "the ripple shrank to a zigzag with a long stroke down", "M16,52 L16,14 L24,26 L32,14 L40,26 L48,14"),
        ("Greek", -700, "mu", "the zigzag opened out and stood on two legs", "M12,52 L12,10 L30,34 L48,10 L48,52"),
        ("Latin", -600, "M", "the waves are still there, in the two peaks", "M12,52 L12,10 L30,34 L48,10 L48,52"),
    ]),
    ("n", "N", "the snake", [
        ("Egyptian hieroglyph", -2000, "a snake", "I10, a cobra, or the horned viper I9, both of them signs for sounds in Egyptian", "M6,44 C14,30 20,50 28,38 C36,26 42,48 50,36 L52,22 L46,16"),
        ("Proto-Sinaitic", -1800, "nahsh, snake", "a snake, for the first sound of the Canaanite word for snake, n", "M30,6 C44,14 16,26 30,34 C44,42 16,50 30,56"),
        ("Phoenician", -1000, "nun", "the snake reduced to a hook and a long tail; the letter's name had changed to nun, fish", "M16,12 L26,24 L16,36 L36,54"),
        ("Greek", -700, "nu", "straightened into three strokes", "M14,52 L14,10 L46,52 L46,10"),
        ("Latin", -600, "N", "the snake's wriggle is the diagonal", "M14,52 L14,10 L46,52 L46,10"),
    ]),
    ("o", "O", "the eye", [
        ("Egyptian hieroglyph", -2000, "an eye", "D4, an eye, the sign for the word for eye and for seeing", "M6,30 C18,12 42,12 54,30 C42,48 18,48 6,30 Z M30,30 m-6,0 a6,6 0 1,0 12,0 a6,6 0 1,0 -12,0"),
        ("Proto-Sinaitic", -1800, "'ayn, eye", "an eye with its pupil, for the first sound of the Canaanite word for eye, a consonant from the throat that English does not have", "M8,30 C20,16 40,16 52,30 C40,44 20,44 8,30 Z M30,30 m-4,0 a4,4 0 1,0 8,0 a4,4 0 1,0 -8,0"),
        ("Phoenician", -1000, "'ayin", "the eye closed to a circle", "M30,30 m-16,0 a16,16 0 1,0 32,0 a16,16 0 1,0 -32,0"),
        ("Greek", -700, "omicron", "the Greeks had no such consonant and gave the circle to the vowel o", "M30,30 m-18,0 a18,18 0 1,0 36,0 a18,18 0 1,0 -36,0"),
        ("Latin", -600, "O", "an eye, round, looking back", "M30,30 m-17,0 a17,21 0 1,0 34,0 a17,21 0 1,0 -34,0"),
    ]),
]

# how many signs each needs: k, name, signs, type, a line, source
COUNTS = [
    ("chinese", "Chinese", 3000, "logo", "About 3,000 characters for everyday literacy; a large dictionary lists over 50,000, most never used.", "Wikipedia, Chinese characters"),
    ("hieroglyphs", "Egyptian hieroglyphs", 900, "logo", "About 900 signs in the Middle Kingdom, the classical period of the language, and more than 5,000 by Greek and Roman times.", "Wikipedia, Egyptian hieroglyphs"),
    ("cuneiform", "Cuneiform", 600, "logo", "Some 1,500 signs at the start, cut to about 600 as the script leaned more on sounds.", "Wikipedia, Cuneiform"),
    ("yi", "Yi", 756, "syll", "The Yi syllabary of Sichuan as standardized in 1974, one sign a syllable.", "Wikipedia, Yi script"),
    ("linearb", "Linear B", 87, "syll", "About 87 syllable signs, plus over a hundred signs for things counted.", "Wikipedia, Linear B"),
    ("cherokee", "Cherokee", 85, "syll", "Sequoyah's 85 syllables.", "Wikipedia, Cherokee syllabary"),
    ("kana", "Hiragana", 46, "syll", "The 46 basic signs of hiragana; katakana has the same 46 again.", "Wikipedia, Hiragana"),
    ("devanagari", "Devanagari", 47, "abugida", "Forty-seven primary signs, 14 vowels and 33 consonants, plus the marks that change a consonant's vowel.", "Wikipedia, Devanagari"),
    ("arabic", "Arabic", 28, "abjad", "Twenty-eight consonants; each takes up to four shapes by its place in the word.", "Wikipedia, Arabic alphabet"),
    ("hebrew", "Hebrew", 22, "abjad", "Twenty-two consonants, five of them with a second shape at the end of a word.", "Wikipedia, Hebrew alphabet"),
    ("phoenician", "Phoenician", 22, "abjad", "Twenty-two consonants, the set nearly every alphabet began from.", "Wikipedia, Phoenician alphabet"),
    ("russian", "Cyrillic, Russian", 33, "alpha", "Thirty-three letters in Russian; other languages add or drop a few.", "Wikipedia, Russian alphabet"),
    ("latin", "Latin, English", 26, "alpha", "Twenty-six letters in English; the Latin script runs from 21 letters in Italian to over 40 with accents in some languages.", "Wikipedia, Latin alphabet"),
    ("greek", "Greek", 24, "alpha", "Twenty-four letters since about 400 BC.", "Wikipedia, Greek alphabet"),
    ("hangul", "Hangul", 24, "feat", "Fourteen consonants and ten vowels, combined into blocks that stand for syllables.", "Wikipedia, Hangul"),
]

REFS = [
    (apa.book("Daniels, P. T., &amp; Bright, W. (Eds.)", 1996, "The world's writing systems", "Oxford University Press"),
     "The standard reference on every script here, its origin, its signs and its kind."),
    (apa.book("Coulmas, F.", 1996, "The Blackwell encyclopedia of writing systems", "Blackwell"),
     "The scripts' dates, sign counts and descent."),
    (apa.article("Goldwasser, O.", 2006, "Canaanites reading hieroglyphs. Horus is Hathor? The invention of the alphabet in Sinai",
                 "&Auml;gypten und Levante", 16, None, "121-160", "https://doi.org/10.1553/AEundL16s121"),
     "The alphabet invented at the turquoise mines of Serabit el-Khadim by Canaanites who could not read Egyptian."),
    (apa.article("Darnell, J. C., Dobbs-Allsopp, F. W., Lundberg, M. J., McCarter, P. K., &amp; Zuckerman, B.", 2005, "Two early alphabetic inscriptions from the Wadi el-H&ocirc;l: New evidence for the origin of the alphabet from the western desert of Egypt",
                 "The Annual of the American Schools of Oriental Research", 59, None, "63-124", "https://www.jstor.org/stable/3768583"),
     "The oldest alphabetic inscriptions, from about 1900 to 1800 BC, in Egypt itself."),
]
REFS += [(apa.wiki(f"https://en.wikipedia.org/wiki/{p}"), a) for p, a in [
    ("History_of_writing", "The four independent inventions and the dates of the scripts."),
    ("Proto-Sinaitic_script", "The letters and the hieroglyphs they came from: ox, house, water, snake, eye."),
    ("Writing_system", "The kinds of writing system and how many signs each uses."),
    ("Cuneiform", None), ("Egyptian_hieroglyphs", None), ("Indus_script", None), ("Linear_A", None), ("Linear_B", None), ("Chinese_characters", None), ("Maya_script", None),
    ("Ugaritic_alphabet", None), ("Phoenician_alphabet", None), ("Paleo-Hebrew_alphabet", None), ("Aramaic_alphabet", None), ("Ancient_South_Arabian_script", None),
    ("Greek_alphabet", None), ("Etruscan_alphabet", None), ("Latin_alphabet", None), ("Hebrew_alphabet", None), ("Brahmi_script", None), ("Nabataean_alphabet", None), ("Syriac_alphabet", None),
    ("Runes", None), ("Coptic_alphabet", None), ("Ge%CA%BDez_script", None), ("Armenian_alphabet", None), ("Arabic_alphabet", None), ("Tibetan_script", None), ("Devanagari", None), ("Khmer_script", None),
    ("Kana", None), ("Cyrillic_script", None), ("Mongolian_script", None), ("Hangul", None), ("Cherokee_syllabary", None), ("Yi_script", None), ("Russian_alphabet", None), ("Hiragana", None),
]]
