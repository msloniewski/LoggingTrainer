"""Plausible amateur-radio callsign generation and normalization.

This is intentionally a training generator, not a licensing authority database.
The templates cover common worldwide shapes and use real amateur prefixes.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
import re


PHONETIC = {
    "A": "Alpha", "B": "Bravo", "C": "Charlie", "D": "Delta",
    "E": "Echo", "F": "Foxtrot", "G": "Golf", "H": "Hotel",
    "I": "India", "J": "Juliett", "K": "Kilo", "L": "Lima",
    "M": "Mike", "N": "November", "O": "Oscar", "P": "Papa",
    "Q": "Quebec", "R": "Romeo", "S": "Sierra", "T": "Tango",
    "U": "Uniform", "V": "Victor", "W": "Whiskey", "X": "X-ray",
    "Y": "Yankee", "Z": "Zulu",
    "0": "Zero", "1": "One", "2": "Two", "3": "Three", "4": "Four",
    "5": "Five", "6": "Six", "7": "Seven", "8": "Eight", "9": "Nine",
    "/": "stroke",
}

ALTERNATIVE_PHONETICS = {
    "A": ("America",), "B": ("Boston",), "C": ("Canada",),
    "D": ("Denmark",), "E": ("England",), "F": ("France",),
    "G": ("Germany",), "H": ("Honolulu",), "I": ("Italy",),
    "J": ("Japan",), "K": ("Kilowatt",), "L": ("London",),
    "M": ("Mexico",), "N": ("Norway",), "O": ("Ontario",),
    "P": ("Portugal",), "Q": ("Queen",), "R": ("Radio",),
    "S": ("Santiago",), "T": ("Tokyo",), "U": ("United",),
    "V": ("Victoria",), "W": ("Washington",), "X": ("Xylophone",),
    "Y": ("Yokohama",), "Z": ("Zanzibar",),
}

PHONETICS = {
    character: (word, *ALTERNATIVE_PHONETICS.get(character, ()))
    for character, word in PHONETIC.items()
}


@dataclass(frozen=True)
class CallPattern:
    region: str
    prefixes: tuple[str, ...]
    suffix_lengths: tuple[int, ...] = (2, 3)
    district_digits: str = "0123456789"


# Representative, commonly heard contest prefixes. The digit is generated where
# it is part of the district, unless already present in the prefix.
PATTERNS = (
    CallPattern("Poland", ("SP", "SQ", "SN", "SO", "HF", "3Z"), (2, 3)),
    CallPattern("Germany", ("DL", "DJ", "DK", "DM", "DO"), (1, 2, 3)),
    CallPattern("United Kingdom", ("G", "M"), (2, 3), "012345678"),
    CallPattern("Italy", ("I", "IK", "IZ", "IU"), (2, 3)),
    CallPattern("Spain", ("EA", "EB", "EC"), (2, 3)),
    CallPattern("France", ("F",), (2, 3, 4)),
    CallPattern("Czechia", ("OK", "OL"), (2, 3)),
    CallPattern("Slovakia", ("OM",), (2, 3)),
    CallPattern("Netherlands", ("PA", "PB", "PD", "PE", "PH"), (2, 3)),
    CallPattern("Belgium", ("ON", "OO", "OP", "OQ", "OR", "OS", "OT"), (2, 3)),
    CallPattern("Sweden", ("SM", "SA", "SK"), (2, 3)),
    CallPattern("Norway", ("LA", "LB", "LC"), (2, 3)),
    CallPattern("Finland", ("OH",), (2, 3)),
    CallPattern("Japan", ("JA", "JE", "JF", "JG", "JH", "JI", "JJ", "JK", "JL", "JM", "JN", "JO", "JP", "JQ", "JR"), (2, 3)),
    CallPattern("USA", ("K", "N", "W", "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AI"), (1, 2, 3, 4)),
    CallPattern("Canada", ("VE", "VA"), (2, 3)),
    CallPattern("Brazil", ("PY", "PP", "PR", "PS", "PT", "PU", "PV", "PW", "PX", "ZV", "ZW", "ZX", "ZY", "ZZ"), (2, 3)),
    CallPattern("Australia", ("VK",), (2, 3, 4)),
    CallPattern("New Zealand", ("ZL",), (2, 3, 4)),
    CallPattern("South Africa", ("ZS",), (2, 3)),
)

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def normalize_callsign(value: str) -> str:
    """Normalize user input for comparison without hiding real mistakes."""
    return re.sub(r"[\s-]+", "", value).upper()


def callsign_to_phonetics(callsign: str) -> str:
    return " ".join(PHONETIC.get(char, char) for char in callsign.upper())


def generate_callsign(rng: random.Random | None = None) -> tuple[str, str]:
    """Return (callsign, region) using a representative regional template."""
    rng = rng or random
    pattern = rng.choice(PATTERNS)
    prefix = rng.choice(pattern.prefixes)
    digit = "" if prefix[-1].isdigit() else rng.choice(pattern.district_digits)
    suffix = "".join(rng.choice(LETTERS) for _ in range(rng.choice(pattern.suffix_lengths)))
    return prefix + digit + suffix, pattern.region
