#!/usr/bin/env python3
"""Generate solar-system-2312.html, The Solar System of 2312.

The real solar system under Kim Stanley Robinson's 2312, laid out on
one line by distance from the Sun the way solar-system.html lays out the
planets, so that Swan Er Hong's travel through the book reads as a run
of jumps between stops. Each stop draws the world she lands on, to
scale, with what the novel builds there marked on it.

Distances are JPL/NASA semi-major axes on a logarithmic axis; the disks
are on a separate logarithmic size scale. Nothing here is a picture of
the sky.

Usage: python3 build_2312.py
"""

import json
import math
from pathlib import Path

OUT = Path(__file__).parent.parent / "solar-system-2312.html"

# name, semi-major axis (AU), radius (km), kind
# kind: 'novel' = the novel puts something here, 'quiet' = drawn muted
BODIES = [
    ("Mercury", 0.387, 2439.7, "novel"),
    ("Venus", 0.723, 6051.8, "novel"),
    ("Earth", 1.000, 6371.0, "novel"),
    ("Mars", 1.524, 3389.5, "novel"),
    ("Vesta", 2.36, 262.7, "novel"),
    ("Ceres", 2.77, 469.7, "novel"),
    ("Jupiter", 5.203, 69911.0, "novel"),
    ("Saturn", 9.537, 58232.0, "novel"),
    ("Uranus", 19.19, 25362.0, "quiet"),
    ("Neptune", 30.07, 24622.0, "quiet"),
    ("Pluto", 39.5, 1188.3, "novel"),
]

# body -> (marker title, book text, real text)
PLACES = {
    "Mercury": ("Terminator",
        "The planet's one city rides giant tracks that circle Mercury, "
        "staying just ahead of sunrise; the day side's heat expands the "
        "rails behind it and pushes the city west at walking pace, one lap "
        "every 176 days. Sunwalkers hike ahead of the dawn for the "
        "spectacle. Midway through the book an engineered meteorite swarm "
        "destroys the city, and Swan and Wahram walk out through a utility "
        "tunnel beneath the tracks.",
        "Mercury's slow turn makes the conceit work: its solar day is 176 "
        "Earth days, so at the equator the sunrise line advances at about "
        "3.6 km/h, and slower toward the poles, genuinely outwalkable. No "
        "engineering study of thermal-expansion track propulsion exists, "
        "but a 2026 rover concept proposes permanently tracking the "
        "terminator at just these speeds, citing the novel."),
    "Venus": ("The sunshield",
        "Venus cools behind a great parasol while tented cities rise and a "
        "faction argues for spinning the planet up with asteroid impacts. "
        "The book's climax foils an attack meant to drop the shield.",
        "Venus today runs 467 degrees Celsius under 93 bars of carbon "
        "dioxide. A sunshade at the Sun-Venus L1 point is real literature: "
        "Paul Birch worked out fast terraforming schemes in 1991, and "
        "space-sunshade optics were studied for Earth by Angel in 2006."),
    "Earth": ("The drowned coasts",
        "Eleven billion people on a climate-wracked planet of hundreds of "
        "ministates; Manhattan is a new Venice, boats in the avenues. In "
        "the book's great set piece, thousands of terraria airdrop their "
        "preserved animals back onto the continents, the Reanimation.",
        "The flooded-city premise extends a real curve: satellite "
        "altimetry has watched global mean sea level rise accelerate from "
        "about 2 to more than 4 millimeters a year since 1993."),
    "Mars": ("A finished Mars",
        "The Mars trilogy's project stands complete here: a terraformed, "
        "politically independent world that has retired from everyone "
        "else's quarrels. The book ends with a wedding on Olympus Mons.",
        "Olympus Mons is real and remains the solar system's largest "
        "volcano, about 22 km above the datum. The terraforming itself "
        "stays fiction: Mars holds a thin carbon dioxide atmosphere near "
        "six millibars."),
    "Vesta": ("The terraria",
        "Most large asteroids have been hollowed out, spun up, and lit "
        "inside: thousands of rolling countryside worlds serving as "
        "wilderness arks, farms and ferries. Swan designed them; the "
        "investigation tours the Vesta zone.",
        "Vesta is the belt's second most massive body, a differentiated "
        "protoplanet the Dawn probe orbited in 2011. Real studies of spun "
        "asteroid habitats find the catch the novel skips: many asteroids "
        "are loose rubble piles that would need containment to spin at "
        "living gravity."),
    "Ceres": ("The belt's port",
        "Ceres anchors the asteroid economy the terraria trade through, "
        "part of the loose league of space settlements the book calls the "
        "Mondragon Accord.",
        "Ceres is the belt's one dwarf planet, 476 km in radius and "
        "perhaps a quarter water by mass; Dawn orbited it in 2015 and "
        "found brine deposits in Occator crater."),
    "Jupiter": ("Io's qube lab",
        "On volcanic Io, the researcher Wang Wei runs one of the system's "
        "most powerful qubes, the quantum computers whose humanoid "
        "descendants drive the book's conspiracy; his station is attacked "
        "during the investigation.",
        "Io is the most volcanically active world known, kneaded by tidal "
        "heating from Jupiter and the resonance with Europa and Ganymede; "
        "hundreds of volcanoes resurface it continuously."),
    "Saturn": ("Titan and the league",
        "The Saturn system runs its own politics as the Saturnian League; "
        "Wahram is a Titan diplomat, terraforming has begun under Titan's "
        "haze, and between crises the pair go bodysurfing on ring ice.",
        "Titan really is the one moon with a thick atmosphere, nitrogen "
        "and methane at one and a half Earth pressures, with methane "
        "rain, rivers and cold seas mapped by Cassini. Nearby Iapetus "
        "keeps its real two-tone paint job, one hemisphere dark as coal."),
    "Pluto": ("The exile",
        "The story ends at Pluto and Charon, where the rogue humanoid "
        "qubes and their maker are gathered and expelled from the solar "
        "system aboard a starship named Nix.",
        "Pluto has five known moons, and Nix is really one of them. New "
        "Horizons flew past in 2015 and found a geologically young "
        "nitrogen-ice heart, Sputnik Planitia."),
}

import math

import math

VB_W, VB_H = 340, 240
CX, CY, RPX = 118, 96, 60
GX = 252                    # where Earth is drawn at the same scale
BAR_Y = 180
CAP_Y = 198


def _scale(r_km):
    """km per pixel, so the body's radius is RPX on screen."""
    return r_km / RPX


def _bar(kmpx, y=BAR_Y, x=16):
    """A scale bar of a round number of kilometres, about 100 px long."""
    raw = 100 * kmpx
    step = 10 ** math.floor(math.log10(raw))
    km = min([m * step for m in (1, 2, 5, 10)], key=lambda v: abs(v - raw))
    w = km / kmpx
    return (f'<g stroke="#6b7280" stroke-width="1.2">'
            f'<path d="M{x},{y} h{w:.1f}"/><path d="M{x},{y - 4} v8"/>'
            f'<path d="M{x + w:.1f},{y - 4} v8"/></g>'
            f'<text x="{x + w / 2:.1f}" y="{y - 8}" text-anchor="middle" '
            f'font-size="10" fill="#6b7280">{km:,.0f} km</text>')


def _ghost(kmpx):
    """Earth at the same scale: drawn when it fits, told in words when not."""
    r = 6371 / kmpx
    if r <= RPX * 1.4 and r >= 5:
        # near the body's own size, so a dashed circle around it reads best
        if r <= RPX * 1.4 and r >= RPX * 0.7:
            return (f'<circle cx="{CX}" cy="{CY}" r="{r:.1f}" fill="none" '
                    f'stroke="#58a6ff" stroke-width="1.1" '
                    f'stroke-dasharray="3 3"/>'
                    f'<text x="{CX + r + 7:.1f}" y="{CY + 4}" '
                    f'font-size="9.5" fill="#58a6ff">Earth, same scale</text>'), None
        return (f'<circle cx="{GX}" cy="{CY}" r="{r:.1f}" fill="none" '
                f'stroke="#58a6ff" stroke-width="1.1" stroke-dasharray="3 3"/>'
                f'<text x="{GX}" y="{CY + r + 13:.1f}" text-anchor="middle" '
                f'font-size="9.5" fill="#58a6ff">Earth, same scale</text>'), None
    ratio = 6371 / (RPX * kmpx)
    return "", f"Earth is {ratio:.1f} times wider."


def _wrap(inner, caption):
    return (f'<svg viewBox="0 0 {VB_W} {VB_H}" '
            f'xmlns="http://www.w3.org/2000/svg" class="dia">'
            f'<rect width="{VB_W}" height="{VB_H}" fill="#131313"/>'
            f'{inner}{caption}</svg>')


def _cap(lines):
    return "".join(f'<text x="16" y="{CAP_Y + i * 14}" font-size="10.5" '
                   f'fill="#9a9a9a">{t}</text>'
                   for i, t in enumerate(lines) if t)


def _arrow_defs():
    return ('<defs><marker id="dA" viewBox="0 0 10 10" refX="8" refY="5" '
            'markerWidth="4.5" markerHeight="4.5" orient="auto-start-reverse">'
            '<path d="M0,1 L9,5 L0,9 z" fill="#ffb02e"/></marker></defs>')


def mercury():
    kmpx = _scale(2439.7)
    g, note = _ghost(kmpx)
    s = (_arrow_defs()
         + f'<clipPath id="mday"><rect x="{CX - RPX}" y="{CY - RPX}" '
         f'width="{RPX}" height="{2 * RPX}"/></clipPath>'
         f'<circle cx="{CX}" cy="{CY}" r="{RPX}" fill="#2b2b2b"/>'
         f'<circle cx="{CX}" cy="{CY}" r="{RPX}" fill="#9a917f" '
         f'clip-path="url(#mday)"/>'
         f'<path d="M{CX},{CY - RPX} V{CY + RPX}" stroke="#e6e6e6" '
         f'stroke-width="1" stroke-dasharray="2 3"/>'
         f'<ellipse cx="{CX}" cy="{CY}" rx="{RPX}" ry="8" fill="none" '
         f'stroke="#ffb02e" stroke-width="1.2" stroke-dasharray="4 3"/>'
         f'<rect x="{CX - 4}" y="{CY - 4}" width="8" height="8" '
         f'fill="#ffb02e" stroke="#131313" stroke-width="1"/>'
         f'<path d="M{CX + 9},{CY} h26" stroke="#ffb02e" stroke-width="1.4" '
         f'marker-end="url(#dA)"/>'
         f'<text x="{CX + 10}" y="{CY - 11}" font-size="10" fill="#ffb02e" '
         f'stroke="#131313" stroke-width="2.4" paint-order="stroke">'
         f'Terminator, on the track</text>'
         f'<text x="16" y="22" font-size="10.5" fill="#9a9a9a">sunlit</text>'
         f'<text x="{VB_W - 16}" y="22" text-anchor="end" font-size="10.5" '
         f'fill="#9a9a9a">night</text>' + g + _bar(kmpx))
    return _wrap(s, _cap([
        f"Mercury, radius 2,440 km. {note or ''}",
        "Its solar day runs 176 Earth days, so the sunrise line crosses",
        "the equator at about 3.6 km/h, slower toward the poles.",
    ]))


def io():
    kmpx = _scale(1821.6)
    g, note = _ghost(kmpx)
    s = (_arrow_defs()
         + f'<circle cx="{CX}" cy="{CY}" r="{RPX}" fill="#c9b558"/>'
         f'<circle cx="{CX - 20}" cy="{CY - 16}" r="8" fill="#8e7b2f" '
         f'opacity="0.7"/>'
         f'<circle cx="{CX + 16}" cy="{CY + 22}" r="11" fill="#8e7b2f" '
         f'opacity="0.55"/>'
         f'<circle cx="{CX + 5}" cy="{CY - 31}" r="5" fill="#8e7b2f" '
         f'opacity="0.6"/>')
    for ang in (-64, 6, 132):
        a = math.radians(ang)
        x0, y0 = CX + RPX * math.cos(a), CY + RPX * math.sin(a)
        x1, y1 = CX + (RPX + 9) * math.cos(a), CY + (RPX + 9) * math.sin(a)
        s += (f'<path d="M{x0:.1f},{y0:.1f} L{x1:.1f},{y1:.1f}" '
              f'stroke="#ffb02e" stroke-width="1.2" opacity="0.8"/>'
              f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="5" fill="#ffb02e" '
              f'opacity="0.35"/>')
    s += (f'<rect x="{CX - 24}" y="{CY + 10}" width="8" height="8" '
          f'transform="rotate(45 {CX - 20} {CY + 14})" fill="#ffb02e" '
          f'stroke="#131313" stroke-width="1"/>'
          f'<path d="M{CX - 16},{CY + 14} h34" stroke="#ffb02e" '
          f'stroke-width="1" stroke-dasharray="3 3"/>'
          f'<text x="{CX + 22}" y="{CY + 18}" font-size="10" fill="#ffb02e" '
          f'stroke="#131313" stroke-width="2.4" paint-order="stroke">'
          f'the qube lab</text>'
          f'<text x="{VB_W - 16}" y="22" text-anchor="end" font-size="10.5" '
          f'fill="#9a9a9a">plumes on the limb</text>' + g + _bar(kmpx))
    return _wrap(s, _cap([
        f"Io, radius 1,822 km, orbits Jupiter at 422,000 km. {note or ''}",
        "Tidal heating from Jupiter and the resonance with Europa and",
        "Ganymede keep hundreds of volcanoes resurfacing it.",
    ]))


def earth():
    kmpx = _scale(6371.0)
    s = (_arrow_defs()
         + f'<circle cx="{CX}" cy="{CY}" r="{RPX}" fill="#22507e"/>'
         f'<clipPath id="eclip"><circle cx="{CX}" cy="{CY}" r="{RPX}"/>'
         f'</clipPath><g clip-path="url(#eclip)" stroke="#2f6ba8" '
         f'stroke-width="1" fill="none">')
    for k in (-40, -20, 0, 20, 40):
        s += f'<path d="M{CX - RPX},{CY + k} h{2 * RPX}"/>'
    for rx in (22, 44):
        s += f'<ellipse cx="{CX}" cy="{CY}" rx="{rx}" ry="{RPX}"/>'
    s += (f'</g><circle cx="{CX}" cy="{CY}" r="{RPX}" fill="none" '
          f'stroke="#4d90d0" stroke-width="1.2"/>')
    for dx in (-40, -14, 14, 40):
        s += (f'<rect x="{CX + dx - 4}" y="16" width="8" height="8" '
              f'fill="#ffb02e" stroke="#131313" stroke-width="1"/>'
              f'<path d="M{CX + dx},{26} V{CY - RPX - 4}" stroke="#ffb02e" '
              f'stroke-width="1.2" marker-end="url(#dA)"/>')
    s += (f'<text x="{GX + 20}" y="24" text-anchor="end" font-size="10" '
          f'fill="#ffb02e">the terraria let</text>'
          f'<text x="{GX + 20}" y="36" text-anchor="end" font-size="10" '
          f'fill="#ffb02e">their animals down</text>' + _bar(kmpx))
    return _wrap(s, _cap([
        "Earth, radius 6,371 km, holds eleven billion people in the novel.",
        "Satellite altimetry has watched global mean sea level rise go",
        "from about 2 to more than 4 millimetres a year since 1993.",
    ]))


def venus():
    kmpx = _scale(6051.8)
    g, note = _ghost(kmpx)
    s = (f'<circle cx="{CX}" cy="{CY}" r="{RPX}" fill="#c2a067"/>'
         f'<clipPath id="vclip"><circle cx="{CX}" cy="{CY}" r="{RPX}"/>'
         f'</clipPath><g clip-path="url(#vclip)" stroke="#d8bd8a" '
         f'stroke-width="6" opacity="0.55">')
    for k in (-36, -16, 6, 28, 48):
        s += f'<path d="M{CX - RPX},{CY + k} h{2 * RPX}"/>'
    s += ('</g>'
          f'<path d="M12,{CY - 34} V{CY + 34}" stroke="#ffb02e" '
          f'stroke-width="4" stroke-linecap="round"/>'
          f'<path d="M18,{CY} H{CX - RPX - 4}" stroke="#ffb02e" '
          f'stroke-width="1" stroke-dasharray="3 4"/>'
          f'<text x="16" y="22" font-size="10" fill="#ffb02e">the sunshield: '
          f'L1 lies about a million km</text>'
          f'<text x="16" y="34" font-size="10" fill="#9a9a9a">sunward, far '
          f'off the left of this frame</text>' + g + _bar(kmpx))
    return _wrap(s, _cap([
        "Venus, radius 6,052 km, is Earth's near twin in size.",
        "Its surface runs 467 degrees Celsius under 93 bars of carbon",
        "dioxide, which is what the novel's parasol is there to end.",
    ]))


def vesta():
    kmpx = _scale(286.3)
    g, note = _ghost(kmpx)
    rx, ry = RPX, RPX * 446.4 / 572.6
    cy = CY - 4
    s = (_arrow_defs()
         + f'<ellipse cx="{CX}" cy="{cy}" rx="{rx}" ry="{ry:.1f}" '
         f'fill="#8d8a82" stroke="#a9a69c" stroke-width="1.2"/>'
         f'<path d="M{CX - rx * 0.95:.1f},{cy + ry * 0.3:.1f} '
         f'A{rx * 0.95:.1f},{ry * 0.85:.1f} 0 0 0 {CX + rx * 0.95:.1f},'
         f'{cy + ry * 0.3:.1f}" fill="none" stroke="#ffb02e" '
         f'stroke-width="1.4" stroke-dasharray="4 3"/>'
         f'<text x="{CX}" y="{cy + ry + 18:.1f}" text-anchor="middle" '
         f'font-size="10" fill="#ffb02e">Rheasilvia, 500 km across</text>'
         f'<g transform="translate(200,34)">'
         f'<rect x="0" y="0" width="62" height="22" rx="11" fill="none" '
         f'stroke="#ffb02e" stroke-width="1.3"/>'
         f'<path d="M0,11 h62" stroke="#ffb02e" stroke-width="0.8" '
         f'stroke-dasharray="2 3"/>'
         f'<path d="M70,2 a9,9 0 1 1 -3,6" fill="none" stroke="#ffb02e" '
         f'stroke-width="1.2" marker-end="url(#dA)"/>'
         f'<text x="0" y="36" font-size="9.5" fill="#ffb02e">a terrarium, '
         f'spun</text>'
         f'<text x="0" y="47" font-size="9.5" fill="#ffb02e">and lit inside'
         f'</text>'
         f'<text x="0" y="60" font-size="9.5" fill="#9a9a9a">kilometres long,'
         f'</text>'
         f'<text x="0" y="71" font-size="9.5" fill="#9a9a9a">not to this scale'
         f'</text></g>' + _bar(kmpx))
    return _wrap(s, _cap([
        f"Vesta is about 526 km across. {note or ''}",
        "Rheasilvia takes up almost all of it. Dawn orbited Vesta in 2011",
        "and found a differentiated protoplanet, not a rubble pile.",
    ]))


def iapetus():
    kmpx = _scale(734.5)
    g, note = _ghost(kmpx)
    s = (f'<clipPath id="ilead"><rect x="{CX - RPX}" y="{CY - RPX}" '
         f'width="{RPX}" height="{2 * RPX}"/></clipPath>'
         f'<circle cx="{CX}" cy="{CY}" r="{RPX}" fill="#ceccc2"/>'
         f'<circle cx="{CX}" cy="{CY}" r="{RPX}" fill="#1f1c19" '
         f'clip-path="url(#ilead)"/>'
         f'<circle cx="{CX}" cy="{CY}" r="{RPX}" fill="none" '
         f'stroke="#8b949e" stroke-width="1"/>'
         f'<path d="M{CX - RPX},{CY} h{2 * RPX}" stroke="#ffb02e" '
         f'stroke-width="2.4"/>'
         f'<text x="{CX + RPX + 7}" y="{CY + 4}" font-size="10" '
         f'fill="#ffb02e">the equatorial ridge</text>'
         f'<text x="16" y="22" font-size="10.5" fill="#9a9a9a">leading side, '
         f'dark as coal</text>'
         f'<text x="{VB_W - 16}" y="22" text-anchor="end" '
         f'font-size="10.5" fill="#9a9a9a">trailing side, bright</text>'
         + _bar(kmpx))
    return _wrap(s, _cap([
        f"Iapetus, radius 736 km. {note or ''}",
        "A chain of mountains 10 km high girdles its equator, and its",
        "leading hemisphere reflects a twentieth of the light of the other.",
    ]))


def mars():
    kmpx = _scale(3389.5)
    g, note = _ghost(kmpx)
    s = (f'<circle cx="{CX}" cy="{CY}" r="{RPX}" fill="#a4553a"/>'
         f'<circle cx="{CX - 18}" cy="{CY - 20}" r="13" fill="#8d452f" '
         f'opacity="0.6"/>'
         f'<circle cx="{CX + 24}" cy="{CY + 16}" r="16" fill="#b96a4a" '
         f'opacity="0.5"/>'
         f'<circle cx="{CX}" cy="{CY}" r="{RPX}" fill="none" '
         f'stroke="#c47a5c" stroke-width="1"/>'
         # Olympus Mons at its own scale, in true proportion
         f'<g transform="translate(192,120)">'
         f'<text x="0" y="-42" font-size="10" fill="#ffb02e">Olympus Mons,</text>'
         f'<text x="0" y="-30" font-size="10" fill="#ffb02e">drawn true</text>'
         f'<path d="M0,0 L40,-1.9 L66,-2.6 L92,-1.9 L132,0 Z" '
         f'fill="#ffb02e" fill-opacity="0.3" stroke="#ffb02e" '
         f'stroke-width="1.2"/>'
         f'<path d="M0,0 h132" stroke="#6b7280" stroke-width="1"/>'
         f'<text x="0" y="14" font-size="9.5" fill="#9a9a9a">600 km across,'
         f'</text>'
         f'<text x="0" y="25" font-size="9.5" fill="#9a9a9a">22 km high: the'
         f'</text>'
         f'<text x="0" y="36" font-size="9.5" fill="#9a9a9a">flanks rise under'
         f'</text>'
         f'<text x="0" y="47" font-size="9.5" fill="#9a9a9a">five degrees</text>'
         f'</g>' + _bar(kmpx))
    return _wrap(s, _cap([
        f"Mars, radius 3,390 km. {note or ''}",
        "Olympus Mons is the largest volcano in the solar system and the",
        "novel ends with a wedding on it. Terraforming stays fiction.",
    ]))


DIAGRAMS = {"Mercury": mercury, "Jupiter": io, "Earth": earth,
            "Venus": venus, "Vesta": vesta, "Saturn": iapetus, "Mars": mars}


# Swan's journey through the book, in order, following the synopsis on the
# author's own site: body, where on it, and what the leg is for.
JOURNEY = [
    ("Mercury", "Terminator",
     "The book opens on Mercury, in the rolling city, after the death of "
     "Swan's grandmother Alex."),
    ("Jupiter", "Callisto, then Io",
     "She taxis out on two terraria, meets Wahram on Callisto, and calls on "
     "Wang at his qube lab on Io, where an attack fails."),
    ("Earth", "New York",
     "To New York, a city in the water, where she meets Kiran and is nearly "
     "taken."),
    ("Venus", "under the shield",
     "She leaves Kiran with a contact on Venus, under the parasol and among "
     "the tented cities."),
    ("Mercury", "the tunnel under the tracks",
     "Back on Mercury as the meteorite swarm destroys Terminator. She and "
     "Wahram walk the utility tunnel under the tracks for forty-five days."),
    ("Vesta", "the Vesta Zone",
     "Across the system with Wahram through the Vesta Zone of terraria, the "
     "hollowed asteroids Swan spent her life designing."),
    ("Saturn", "Iapetus",
     "On with Genette and Wahram to the Saturn system, tracing the swarm "
     "back to whoever launched it."),
    ("Earth", "Chad, China, Greenland",
     "Back to Earth for the Reanimation: twelve thousand terraria let their "
     "animals down at once, and she goes along with them."),
    ("Venus", "the ETH Mobile",
     "To Venus again, aboard the mobile city, where a pebble attack meant "
     "to drop the sunshield nearly kills her."),
    ("Mars", "Olympus Mons",
     "It ends on the one world that stayed out of it, with a wedding on "
     "Olympus Mons."),
]

# log distance axis, log size scale
AMIN, AMAX = 0.387, 39.5
XL, XR = 96, 930
RKMIN, RKMAX = 250.0, 70000.0
AXIS_Y = 200


def X(a):
    t = (math.log10(a) - math.log10(AMIN)) / (math.log10(AMAX) - math.log10(AMIN))
    return round(XL + t * (XR - XL), 1)


def RD(r_km):
    t = (math.log10(r_km) - math.log10(RKMIN)) / (math.log10(RKMAX) - math.log10(RKMIN))
    return round(5 + max(0.0, min(1.0, t)) * 15, 1)


TICKS = [0.4, 1, 2, 5, 10, 20, 40]

bodies_js = json.dumps([
    {"n": n, "a": a, "x": X(a), "rd": RD(rk), "rkm": rk, "kind": kind,
     **({"place": PLACES[n][0], "book": PLACES[n][1], "real": PLACES[n][2]}
        if n in PLACES else {})}
    for n, a, rk, kind in BODIES], separators=(",", ":"))
journey_js = json.dumps([{"n": n, "w": w, "t": t} for n, w, t in JOURNEY],
                        separators=(",", ":"))
ticks_js = json.dumps([{"a": t, "x": X(t)} for t in TICKS],
                      separators=(",", ":"))
dia_js = json.dumps({k: f() for k, f in DIAGRAMS.items()},
                    separators=(",", ":"))

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Solar System of 2312 · Altazor</title>
<style>
:root { --bg:#121212; --panel:#1a1a1a; --text:#e6e6e6; --muted:#9a9a9a;
        --line:#2b2b2b; --accent:#58a6ff; --site:#ffb02e; --hop:#b48cf2; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }
.wrap { max-width:1320px; margin:0 auto; padding:32px 20px 60px; }
header.site { border-top:4px solid var(--accent); padding-top:22px; margin-bottom:26px;
  display:flex; align-items:baseline; gap:18px; flex-wrap:wrap; }
.brand { font-weight:700; font-size:20px; letter-spacing:.1em; text-decoration:none; color:var(--text); }
.brand:hover { color:var(--accent); }
nav.site a { color:var(--muted); text-decoration:none; font-size:14px; margin-right:14px; }
nav.site a:hover { color:var(--accent); }
h1 { margin:0 0 10px; font-size:26px; }
.bar { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin-bottom:10px; }
button { font:inherit; font-size:13.5px; padding:6px 14px; border-radius:999px;
  border:1px solid var(--line); background:#1a1a1a; color:var(--text); cursor:pointer; }
button:hover { border-color:var(--accent); }
button.on { background:var(--accent); border-color:var(--accent); color:#0b0b0b; }
button.step { padding:6px 12px; }
#legTxt { color:var(--muted); font-size:12.5px; }
.stage { display:flex; gap:22px; align-items:flex-start; }
#map { flex:1 1 640px; min-width:0; }
#map svg { width:100%; height:auto; display:block; user-select:none; }
.side { flex:0 0 340px; position:sticky; top:16px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:12px;
  padding:16px; }
#kindTxt { color:var(--muted); font-size:11.5px; letter-spacing:.09em;
  text-transform:uppercase; }
#nameTxt { font-weight:700; font-size:17px; margin:2px 0 8px; }
#bookTxt { font-size:13.5px; line-height:1.55; }
#realTxt { color:var(--muted); font-size:13.5px; line-height:1.55; margin-top:10px;
  border-top:1px solid var(--line); padding-top:10px; }
#dia { margin-top:12px; }
#dia svg { width:100%; height:auto; display:block; border:1px solid var(--line);
  border-radius:10px; }
.note { color:var(--muted); font-size:12.5px; margin-top:20px; max-width:760px;
  border-top:1px solid var(--line); padding-top:12px; }
.refs { color:var(--muted); font-size:12.5px; margin-top:14px; max-width:760px; }
.refs p { margin:0 0 8px; overflow-wrap:anywhere; }
.refs a { color:var(--accent); }
h2.refh { font-size:15px; margin:26px 0 8px; }
@media (max-width:900px){ .stage{flex-direction:column;} .side{position:static; width:100%;} }
</style>
</head>
<body>
<div class="wrap">
<header class="site">
  <a class="brand" href="index.html">ALTAZOR</a>
  <nav class="site"><a href="science-fiction.html">&larr; Science Fiction</a><a href="red-mars.html">The Mars of Red Mars</a><a href="solar-system.html">The Solar System</a></nav>
</header>
<h1>The Solar System of 2312</h1>
<div class="bar">
  <button id="bJourney" class="on">Swan's jumps</button>
  <button id="bPrev" class="step">&#8592;</button>
  <button id="bNext" class="step">&#8594;</button>
  <span id="legTxt"></span>
</div>
<div class="stage">
  <div id="map"></div>
  <div class="side"><div class="card">
    <div id="kindTxt"></div>
    <div id="nameTxt">A world under the cursor lands here</div>
    <div id="bookTxt"></div>
    <div id="realTxt"></div>
    <div id="dia"></div>
  </div></div>
</div>
<p class="note">__NOTE1__</p>
<p class="note" style="border-top:none; padding-top:0;">__NOTE2__</p>
<h2 class="refh">References</h2>
<div class="refs">
__REFS__
</div>
</div>
<script>
const BODIES=__BODIES__, JOURNEY=__JOURNEY__, TICKS=__TICKS__, DIA=__DIA__;
const W=1000,H=320,AXIS=__AXIS__,XL=__XL__,XR=__XR__;
const el=document.getElementById('map');
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
let jumps=true, leg=-1, cur='Mercury';

const at={};
for(const b of BODIES) at[b.n]=b;
// each jump is an arc over the line; the height stands off by leg so
// that legs sharing a stop stay apart
JOURNEY.forEach((j,i)=>{ j.h = 32 + 13*(i%5); });

function arcPath(i){
  const a=at[JOURNEY[i].n], b=at[JOURNEY[i+1].n];
  const x1=a.x, x2=b.x, y1=AXIS-a.rd-4, y2=AXIS-b.rd-4;
  const h=JOURNEY[i+1].h;
  const mx=(x1+x2)/2;
  return {d:`M${x1},${y1} C${x1},${y1-h} ${x2},${y2-h} ${x2},${y2}`,
          mx, my:(y1+y2)/2 - h*0.75};
}

function render(){
  let s=`<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" id="ssvg">`;
  s+=`<defs><marker id="hopArrow" viewBox="0 0 10 10" refX="8" refY="5"
      markerWidth="4" markerHeight="4" orient="auto-start-reverse">
      <path d="M0,1 L9,5 L0,9 z" fill="var(--hop)"/></marker></defs>`;
  s+=`<rect width="${W}" height="${H}" fill="#121212"/>`;
  s+=`<text x="16" y="20" font-size="10.5" fill="#6b7280">distance from the
      Sun, in astronomical units</text>`;
  s+=`<path d="M40,${AXIS} H${XR+16}" stroke="#2e3742" stroke-width="1.4"/>`;
  for(const t of TICKS){
    s+=`<path d="M${t.x},${AXIS-5} v10" stroke="#2e3742" stroke-width="1.2"/>`;
    // a number under a disk reads as part of it, so those are left off
    if(BODIES.some(b=>Math.abs(b.x-t.x)<20)) continue;
    s+=`<text x="${t.x}" y="${AXIS+21}" text-anchor="middle" font-size="10.5"
        fill="#6b7280">${t.a}</text>`;
  }
  s+=`<circle cx="40" cy="${AXIS}" r="16" fill="#ffd24d"/>
    <text x="40" y="${AXIS+32}" text-anchor="middle" font-size="11.5"
      fill="#9a9a9a">Sun</text>`;
  s+=`<rect x="${at['Vesta'].x-10}" y="${AXIS-13}"
      width="${at['Ceres'].x-at['Vesta'].x+20}" height="26" fill="#8b93a7"
      fill-opacity="0.13"/>`;
  if(jumps){
    for(let i=0;i<JOURNEY.length-1;i++){
      const p=arcPath(i), on=(leg===i+1);
      s+=`<g data-leg="${i+1}" style="cursor:pointer">
        <path d="${p.d}" fill="none" stroke="#121212" stroke-width="6"
          stroke-opacity="0.01"/>
        <path d="${p.d}" fill="none" stroke="var(--hop)"
          stroke-width="${on?2.6:1.3}" stroke-opacity="${on?1:0.3}"
          stroke-dasharray="7 5" marker-end="url(#hopArrow)"/>
        <circle cx="${p.mx}" cy="${p.my}" r="9"
          fill="${on?'var(--hop)':'#121212'}" stroke="var(--hop)"
          stroke-width="1.2" stroke-opacity="${on?1:0.5}"/>
        <text x="${p.mx}" y="${p.my+3.6}" text-anchor="middle" font-size="10"
          fill="${on?'#121212':'var(--hop)'}"
          fill-opacity="${on?1:0.6}">${i+2}</text></g>`;
    }
    const st=at[JOURNEY[0].n], on0=(leg===0);
    s+=`<g data-leg="0" style="cursor:pointer">
      <circle cx="${st.x}" cy="${AXIS-st.rd-24}" r="9"
        fill="${on0?'var(--hop)':'#121212'}" stroke="var(--hop)"
        stroke-width="1.2"/>
      <text x="${st.x}" y="${AXIS-st.rd-20.4}" text-anchor="middle"
        font-size="10" fill="${on0?'#121212':'var(--hop)'}">1</text></g>`;
  }
  // labels stagger where the log axis crowds the inner worlds
  const ordered=[...BODIES].sort((a,b)=>a.x-b.x);
  let row=0, lastx=-999;
  for(const b of ordered){
    row = (b.x-lastx < 78) ? 1-row : 0;
    lastx=b.x; b.row=row;
  }
  for(const b of BODIES){
    const quiet=b.kind==='quiet';
    const col=quiet?'#4b5563':'#8fa4bd';
    const ly=AXIS+b.rd+30+b.row*30;
    s+=`<g data-n="${esc(b.n)}" style="cursor:pointer">
      <rect x="${b.x-26}" y="${AXIS-b.rd-6}" width="52"
        height="${b.rd+6+ly-AXIS+18}" fill="transparent"/>
      <path d="M${b.x},${AXIS+b.rd+3} V${ly-11}" stroke="#3d444d"
        stroke-width="1" stroke-opacity="${b.row?0.8:0}"/>
      <circle cx="${b.x}" cy="${AXIS}" r="${b.rd}" fill="${col}"
        stroke="${b.n===cur?'#e6e6e6':'#121212'}" stroke-width="1.4"/>`;
    if(!quiet)
      s+=`<rect x="${b.x-4.2}" y="${ly-24}" width="8.4" height="8.4"
        transform="rotate(45 ${b.x} ${ly-19.8})" fill="var(--site)"
        stroke="#121212" stroke-width="1"/>`;
    s+=`<text x="${b.x}" y="${ly}" text-anchor="middle"
      font-size="12.5" font-weight="${quiet?400:700}"
      fill="${quiet?'#6b7280':'#e6e6e6'}">${esc(b.n)}</text>`;
    if(!quiet)
      s+=`<text x="${b.x}" y="${ly+14}" text-anchor="middle"
        font-size="10.5" fill="var(--site)">${esc(b.place)}</text>`;
    s+='</g>';
  }
  s+='</svg>';
  el.innerHTML=s;
}

function diagram(n){
  document.getElementById('dia').innerHTML=DIA[n]||'';
}
function showBody(n){
  const b=at[n]; if(!b) return;
  cur=n; leg=-1;
  const quiet=b.kind==='quiet';
  document.getElementById('kindTxt').textContent=
    quiet?'Off the book\\u2019s map':'In the novel \\u00b7 '+b.a+' AU';
  document.getElementById('nameTxt').textContent=quiet?b.n:b.place;
  document.getElementById('bookTxt').textContent=
    quiet?'The novel passes this world by.':b.book;
  document.getElementById('realTxt').textContent=quiet?'':b.real;
  document.getElementById('legTxt').textContent='';
  diagram(n);
  render();
}
function showLeg(i){
  if(i<0||i>=JOURNEY.length) return;
  leg=i; jumps=true;
  document.getElementById('bJourney').classList.add('on');
  const j=JOURNEY[i], from=i?JOURNEY[i-1]:null;
  cur=j.n;
  document.getElementById('kindTxt').textContent=
    'Stop '+(i+1)+' of '+JOURNEY.length+(from?' \\u00b7 from '+from.n:'');
  document.getElementById('nameTxt').textContent=j.n+' \\u00b7 '+j.w;
  document.getElementById('bookTxt').textContent=j.t;
  document.getElementById('realTxt').textContent=at[j.n].real||'';
  document.getElementById('legTxt').textContent=
    'stop '+(i+1)+' of '+JOURNEY.length;
  diagram(j.n);
  render();
}
el.addEventListener('pointerover',e=>{
  const g=e.target.closest('[data-leg]');
  if(g){ showLeg(+g.getAttribute('data-leg')); return; }
  const b=e.target.closest('[data-n]');
  if(b) showBody(b.getAttribute('data-n'));
});
el.addEventListener('click',e=>{
  const g=e.target.closest('[data-leg]');
  if(g) showLeg(+g.getAttribute('data-leg'));
});
document.getElementById('bJourney').onclick=e=>{
  jumps=!jumps; e.target.classList.toggle('on',jumps); render();
};
document.getElementById('bPrev').onclick=()=>
  showLeg((leg<=0?JOURNEY.length:leg)-1);
document.getElementById('bNext').onclick=()=>
  showLeg((leg+1)%JOURNEY.length);
render();
showLeg(0);
window.__ss2312=()=>({bodies:BODIES.length,
  novel:BODIES.filter(b=>b.kind==='novel').length, jumps,
  legs:JOURNEY.length, leg, cur,
  diagrams:Object.keys(DIA).length,
  drawn:!!document.querySelector('#dia svg')});
</script>
</body>
</html>
"""

NOTE1 = ("The worlds sit on one line by distance from the Sun, logarithmic "
         "so that Mercury and Pluto share it, and the disks run on a "
         "separate logarithmic size scale. Nothing here is a picture of the "
         "sky. Amber marks where Kim Stanley Robinson's 2312 puts its "
         "story, and each card pairs what the book says with what is "
         "actually there.")

NOTE2 = ("The violet arcs are Swan Er Hong's travel through the novel in "
         "order, following the synopsis on the author's own site, and each "
         "stop draws the world she lands on to scale, with the novel's "
         "structures in amber. Pluto is on the map and off her route: that "
         "is where the qubes are gathered at the end.")

REFS = """<p>Robinson, K. S. (2012). <i>2312</i>. Orbit. Synopsis, and the order of
Swan's journey followed here:
<a href="https://www.kimstanleyrobinson.info/content/2312">https://www.kimstanleyrobinson.info/content/2312</a></p>
<p>Orbital elements: Jet Propulsion Laboratory, Approximate positions of the
planets.
<a href="https://ssd.jpl.nasa.gov/planets/approx_pos.html">https://ssd.jpl.nasa.gov/planets/approx_pos.html</a>;
small bodies via the JPL Small-Body Database,
<a href="https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html">https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html</a></p>
<p>Body radii: JPL Solar System Dynamics, planetary and satellite physical
parameters.
<a href="https://ssd.jpl.nasa.gov/planets/phys_par.html">https://ssd.jpl.nasa.gov/planets/phys_par.html</a></p>
<p>NASA planetary science pages for each world:
<a href="https://science.nasa.gov/mercury/facts/">Mercury</a>,
<a href="https://science.nasa.gov/venus/venus-facts/">Venus</a>,
<a href="https://science.nasa.gov/mars/facts/">Mars</a>,
<a href="https://science.nasa.gov/dwarf-planets/ceres/facts/">Ceres</a>,
<a href="https://science.nasa.gov/solar-system/asteroids/4-vesta/">Vesta</a>,
<a href="https://science.nasa.gov/jupiter/moons/io/facts/">Io</a>,
<a href="https://science.nasa.gov/saturn/moons/titan/facts/">Titan</a>,
<a href="https://science.nasa.gov/saturn/moons/iapetus/">Iapetus</a>,
<a href="https://science.nasa.gov/dwarf-planets/pluto/facts/">Pluto</a></p>
<p>Sea level: NASA global mean sea level indicator.
<a href="https://sealevel.nasa.gov/understanding-sea-level/key-indicators/global-mean-sea-level/">https://sealevel.nasa.gov/understanding-sea-level/key-indicators/global-mean-sea-level/</a></p>
<p>Birch, P. (1991). Terraforming Venus quickly. <i>Journal of the British
Interplanetary Society, 44</i>, 157-167.
<a href="https://ui.adsabs.harvard.edu/abs/1991JBIS...44..157B">https://ui.adsabs.harvard.edu/abs/1991JBIS...44..157B</a></p>
<p>Angel, R. (2006). Feasibility of cooling the Earth with a cloud of small
spacecraft near the inner Lagrange point (L1). <i>Proceedings of the
National Academy of Sciences, 103</i>(46), 17184-17189.
<a href="https://doi.org/10.1073/pnas.0608163103">https://doi.org/10.1073/pnas.0608163103</a></p>
<p>Miklav&#269;i&#269;, P. M., et al. (2022). Habitat Bennu: Design concepts
for spinning habitats constructed from rubble pile near-Earth asteroids.
<i>Frontiers in Astronomy and Space Sciences, 8</i>, 645363.
<a href="https://doi.org/10.3389/fspas.2021.645363">https://doi.org/10.3389/fspas.2021.645363</a></p>
<p>A Mercury rover on the terminator: Universe Today on the 2026 LPSC
concept.
<a href="https://www.universetoday.com/articles/a-mercury-rover-could-explore-the-planet-by-sticking-to-the-terminator">https://www.universetoday.com/articles/a-mercury-rover-could-explore-the-planet-by-sticking-to-the-terminator</a></p>"""

html = (HTML.replace("__BODIES__", bodies_js)
        .replace("__JOURNEY__", journey_js)
        .replace("__TICKS__", ticks_js)
        .replace("__DIA__", dia_js)
        .replace("__AXIS__", str(AXIS_Y))
        .replace("__XL__", str(XL)).replace("__XR__", str(XR))
        .replace("__NOTE1__", NOTE1).replace("__NOTE2__", NOTE2)
        .replace("__REFS__", REFS))
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({len(html):,} bytes): {len(BODIES)} bodies, "
      f"{len(PLACES)} novel places, {len(JOURNEY)} stops, "
      f"{len(DIAGRAMS)} diagrams")
