#!/usr/bin/env python3
"""The data behind music.html: the notes and their frequencies, the pure
intervals against the tempered ones, and the scales.

Frequencies are twelve-tone equal temperament on A4 = 440 Hz; the just
ratios are the five-limit ones of the textbooks; the scales are given as
semitone steps from the root.
"""

import apa

A4 = 440.0
SPEED_OF_SOUND = 343.0   # m/s in air at 20 C
HEARING = (20, 20000)    # Hz, a young adult
PIANO = (21, 108)        # MIDI numbers of A0 and C8
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# ranges: k, name, kind, lowest and highest MIDI note, a line
RANGES = [
    ("bass", "bass voice", "voice", 40, 64, "E2 to E4 in the usual reckoning; the lowest voice, and the choir's foundation."),
    ("tenor", "tenor voice", "voice", 48, 69, "C3 to A4; the top of the male voice."),
    ("alto", "alto voice", "voice", 53, 77, "F3 to F5; the lower of the women's parts, and the boy alto's."),
    ("soprano", "soprano voice", "voice", 60, 84, "C4 to C6; the high C of opera is the top of this range, the C two octaves above middle C."),
    ("contrabass", "double bass", "strings", 28, 67, "E1 to about G4; the lowest of the orchestra's strings, tuned in fourths."),
    ("cello", "cello", "strings", 36, 84, "C2 to about C6, and higher in the hands of a soloist."),
    ("viola", "viola", "strings", 48, 91, "C3 to about G6."),
    ("violin", "violin", "strings", 55, 100, "G3 to about E7; four strings, G, D, A, E, tuned in fifths."),
    ("guitar", "guitar", "strings", 40, 88, "E2 to about E6 on a classical guitar; written an octave higher than it sounds."),
    ("tuba", "tuba", "winds", 26, 65, "D1 to about F4."),
    ("trumpet", "trumpet", "winds", 52, 86, "E3 to about D6."),
    ("flute", "flute", "winds", 60, 96, "C4 to C7."),
    ("piccolo", "piccolo", "winds", 74, 108, "D5 to C8, the top of the piano; the highest instrument of the orchestra."),
    ("piano", "piano", "keys", 21, 108, "A0 to C8, 88 keys, seven and a quarter octaves, 27.5 to 4,186 Hz."),
]

# the intervals of the octave: semitones, name, just ratio as (num, den), a line
INTERVALS = [
    (0, "unison", (1, 1), "The same note."),
    (1, "minor second", (16, 15), "The smallest step of the scale, E to F or B to C; the tightest dissonance in common use."),
    (2, "major second", (9, 8), "A whole tone, C to D; two of them make a Pythagorean major third, 81:64, sharper than the pure one."),
    (3, "minor third", (6, 5), "C to E flat; the sad third."),
    (4, "major third", (5, 4), "C to E; the pure third is 14 cents flatter than the piano's, which is why an equal-tempered major chord beats slowly."),
    (5, "perfect fourth", (4, 3), "C to F; the fifth turned upside down."),
    (6, "tritone", (45, 32), "C to F sharp, three whole tones, exactly half an octave in equal temperament; the interval that divides the octave in two and has no simple ratio."),
    (7, "perfect fifth", (3, 2), "C to G; the strongest consonance after the octave, and the interval every tuning is built from. The tempered fifth is only two cents flat of pure."),
    (8, "minor sixth", (8, 5), "C to A flat; the major third turned over."),
    (9, "major sixth", (5, 3), "C to A."),
    (10, "minor seventh", (16, 9), "C to B flat; the seventh of the dominant chord. The natural seventh harmonic, 7:4, is 31 cents flatter still."),
    (11, "major seventh", (15, 8), "C to B; a semitone short of the octave, and pulling toward it."),
    (12, "octave", (2, 1), "Double the frequency, and heard everywhere as the same note again; the one interval every musical culture agrees on."),
]

# the scales: k, name, family, semitone steps from the root, a line
SCALES = [
    ("major", "major", "the seven-note scales", [0, 2, 4, 5, 7, 9, 11], "Do re mi fa sol la ti: whole, whole, half, whole, whole, whole, half. The white keys from C. The scale of most of the music the West has written since 1600."),
    ("minor", "natural minor", "the seven-note scales", [0, 2, 3, 5, 7, 8, 10], "The white keys from A, the Aeolian mode: the same notes as the major scale, started from its sixth degree, and darker for it."),
    ("harmonic", "harmonic minor", "the seven-note scales", [0, 2, 3, 5, 7, 8, 11], "The minor scale with its seventh raised to lead back to the root, which leaves a gap of three semitones between the sixth and seventh, the sound of the East to Western ears."),
    ("melodic", "melodic minor", "the seven-note scales", [0, 2, 3, 5, 7, 9, 11], "Going up, the minor scale with both its sixth and seventh raised, to smooth the harmonic minor's gap; coming down, the natural minor again. Jazz uses the ascending form both ways."),
    ("dorian", "Dorian", "the seven-note scales", [0, 2, 3, 5, 7, 9, 10], "The white keys from D: minor with a raised sixth. The mode of Scarborough Fair and of much folk and jazz."),
    ("phrygian", "Phrygian", "the seven-note scales", [0, 1, 3, 5, 7, 8, 10], "The white keys from E: minor with a flattened second, the half step at the bottom that flamenco is built on."),
    ("lydian", "Lydian", "the seven-note scales", [0, 2, 4, 6, 7, 9, 11], "The white keys from F: major with a raised fourth, bright and floating."),
    ("mixolydian", "Mixolydian", "the seven-note scales", [0, 2, 4, 5, 7, 9, 10], "The white keys from G: major with a flattened seventh, the scale of bagpipes, of much blues and rock."),
    ("locrian", "Locrian", "the seven-note scales", [0, 1, 3, 5, 6, 8, 10], "The white keys from B: a flattened second and a flattened fifth, so the root chord itself is diminished; the mode almost nobody writes in."),
    ("doubleharm", "double harmonic", "the seven-note scales", [0, 1, 4, 5, 7, 8, 11], "Two gaps of three semitones, between the second and third and the sixth and seventh: the Byzantine scale, the Hijaz Kar of Arabic music, and the sound of a film's idea of the Middle East."),
    ("pentamaj", "major pentatonic", "the five-note scales", [0, 2, 4, 7, 9], "The black keys from F sharp: the major scale without its two half steps, so no two notes clash. Found in China, Scotland, West Africa, Japan, the Andes and the blues, apparently invented separately many times."),
    ("pentamin", "minor pentatonic", "the five-note scales", [0, 3, 5, 7, 10], "The black keys from D sharp: the same five notes started from a different one. The scale of the blues guitar solo."),
    ("blues", "blues", "the five-note scales", [0, 3, 5, 6, 7, 10], "The minor pentatonic with a flattened fifth added between the fourth and the fifth, the blue note."),
    ("wholetone", "whole tone", "the symmetrical scales", [0, 2, 4, 6, 8, 10], "Six whole steps, dividing the octave evenly, so every note sounds like every other and nothing feels like home; Debussy's scale."),
    ("octatonic", "octatonic", "the symmetrical scales", [0, 2, 3, 5, 6, 8, 9, 11], "Whole step, half step, repeated four times; the diminished scale of Stravinsky, Bartók and jazz."),
    ("chromatic", "chromatic", "the symmetrical scales", list(range(12)), "All twelve notes, every half step; not so much a scale as the whole keyboard."),
]

REFS = [
    (apa.book("Helmholtz, H. L. F.", 1954, "On the sensations of tone as a physiological basis for the theory of music (A. J. Ellis, Trans.; 2nd ed.)", "Dover"),
     "The harmonic series, consonance and the just ratios, first laid out in 1863."),
    (apa.book("Benson, D. J.", 2006, "Music: A mathematical offering", "Cambridge University Press", "https://doi.org/10.1017/CBO9780511811722"),
     "Temperaments, cents, the Pythagorean comma, and the scales as arithmetic."),
    (apa.web("International Organization for Standardization", 1975, "ISO 16:1975, Acoustics: Standard tuning frequency (standard musical pitch)", "ISO", "https://www.iso.org/standard/3601.html"),
     "A4 = 440 Hz."),
]
REFS += [(apa.wiki(f"https://en.wikipedia.org/wiki/{p}"), a) for p, a in [
    ("Piano_key_frequencies", "The 88 keys from A0 at 27.5 Hz to C8 at 4,186 Hz in equal temperament."),
    ("Equal_temperament", "The twelfth root of two and the cents scale."),
    ("Just_intonation", "The five-limit ratios of the intervals."),
    ("Pythagorean_comma", "Twelve fifths against seven octaves: 23.46 cents."),
    ("Harmonic_series_(music)", "The overtones of a string and the intervals between them."),
    ("Hearing_range", "About 20 Hz to 20 kHz in a young adult, the top falling with age."),
    ("Vocal_range", "The ranges of the four voices."),
    ("Scale_(music)", None), ("Mode_(music)", None), ("Pentatonic_scale", None), ("Blues_scale", None), ("Whole-tone_scale", None), ("Octatonic_scale", None), ("Double_harmonic_scale", None),
    ("Speed_of_sound", "343 metres a second in air at 20 degrees."),
]]
