"""Turkish measurement parser.

Goal: Given a transcript like "Şekerim yüz otuz beş" or "tansiyon 12 8",
return a structured measurement.

Person A — extend this file with more synonyms and edge cases as needed.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Optional

# ---------- Turkish number words ----------------------------------------

_UNITS = {
    "sifir": 0, "bir": 1, "iki": 2, "uc": 3, "dort": 4, "bes": 5,
    "alti": 6, "yedi": 7, "sekiz": 8, "dokuz": 9,
}
_TENS = {
    "on": 10, "yirmi": 20, "otuz": 30, "kirk": 40, "elli": 50,
    "altmis": 60, "yetmis": 70, "seksen": 80, "doksan": 90,
}
_HUNDREDS = {"yuz": 100}
_THOUSANDS = {"bin": 1000}
_HALF = {"bucuk": 0.5, "yarim": 0.5}

# Magnitude tier per word — used to detect when a new number group starts
# (e.g. "on iki sekiz" -> [12, 8], not 20).
_SCALE: dict[str, int] = (
    {w: 1 for w in _UNITS} | {w: 2 for w in _TENS}
    | {w: 3 for w in _HUNDREDS} | {w: 4 for w in _THOUSANDS}
)


def _strip_accents(text: str) -> str:
    norm = unicodedata.normalize("NFKD", text)
    return "".join(c for c in norm if not unicodedata.combining(c))


def _normalize(text: str) -> str:
    text = text.lower()
    # Turkish-specific replacements before generic accent strip
    repl = str.maketrans({"ı": "i", "İ": "i", "ş": "s", "ğ": "g", "ü": "u", "ö": "o", "ç": "c"})
    text = text.translate(repl)
    text = _strip_accents(text)
    text = re.sub(r"[^a-z0-9\s.,/-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _words_to_number(words: list[str]) -> Optional[float]:
    """Convert a sequence of Turkish number words to a float. None if not numeric."""
    total = 0
    current = 0
    half = 0.0
    matched_any = False

    for w in words:
        if w in _HALF:
            half = 0.5
            matched_any = True
            continue
        if w in _UNITS:
            current += _UNITS[w]
            matched_any = True
        elif w in _TENS:
            current += _TENS[w]
            matched_any = True
        elif w in _HUNDREDS:
            current = (current or 1) * 100
            matched_any = True
        elif w in _THOUSANDS:
            total += (current or 1) * 1000
            current = 0
            matched_any = True
        else:
            return None  # unknown word in numeric region

    if not matched_any:
        return None
    return float(total + current) + half


_NUMBER_TOKENS = (
    set(_UNITS) | set(_TENS) | set(_HUNDREDS) | set(_THOUSANDS) | set(_HALF)
)


def _extract_numbers(text: str) -> list[float]:
    """Find every number in the (normalized) text, both digit and Turkish-word form."""
    tokens = text.split()
    numbers: list[float] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        # digit form: 12, 12.5, 12,5
        m = re.fullmatch(r"\d+(?:[.,]\d+)?", tok)
        if m:
            numbers.append(float(tok.replace(",", ".")))
            i += 1
            continue
        # word form: consume tokens, but split into separate numbers when a
        # scale tier repeats (e.g. unit-after-unit means a new number).
        if tok in _NUMBER_TOKENS:
            group: list[str] = []
            seen_scales: set[int] = set()
            j = i
            while j < len(tokens) and tokens[j] in _NUMBER_TOKENS:
                w = tokens[j]
                if w in _HALF:
                    group.append(w)
                    j += 1
                    continue
                scale = _SCALE.get(w, 0)
                if scale in seen_scales:
                    break  # start of next number
                seen_scales.add(scale)
                group.append(w)
                j += 1
                # close greedily after a unit (scale 1) so the next unit starts fresh
                if scale == 1:
                    # but absorb a trailing "buçuk"/"yarım" half-marker
                    if j < len(tokens) and tokens[j] in _HALF:
                        group.append(tokens[j])
                        j += 1
                    break
            val = _words_to_number(group)
            if val is not None:
                numbers.append(val)
            i = j if j > i else i + 1
            continue
        i += 1
    return numbers


# ---------- Measurement type detection ----------------------------------

# All keys are normalized (no diacritics).
_KEYWORDS: dict[str, str] = {
    # sugar / glucose
    "seker": "sugar", "sekerim": "sugar", "glikoz": "sugar", "glukoz": "sugar",
    "kan": "sugar",  # "kan şekerim" → kan + seker
    # blood pressure
    "tansiyon": "bp", "tansiyonum": "bp", "buyuk": "bp",
    # pulse
    "nabiz": "pulse", "nabzim": "pulse", "kalp": "pulse",
    # weight
    "kilo": "weight", "kilom": "weight", "agirlik": "weight",
}


@dataclass
class ParsedMeasurement:
    type: str
    value1: float
    value2: Optional[float] = None

    def summary(self) -> str:
        if self.type == "bp" and self.value2 is not None:
            return f"Tansiyon kaydedildi: {self.value1:.0f}/{self.value2:.0f}"
        labels = {"sugar": "Şeker", "pulse": "Nabız", "weight": "Kilo"}
        unit = {"sugar": "mg/dL", "pulse": "bpm", "weight": "kg"}
        return f"{labels.get(self.type, self.type)} kaydedildi: {self.value1:g} {unit.get(self.type, '')}".strip()


def _detect_type(norm_text: str) -> Optional[str]:
    """Match a keyword as a substring of any token (so 'sekerim', 'glikozum',
    'tansiyonum', 'nabzim', 'kilom' all map to their root)."""
    tokens = norm_text.split()
    # Order matters: more specific keys (e.g. "tansiyon") before shorter ones.
    priority = ["tansiyon", "tansiyonum", "buyuk", "glikoz", "glukoz",
                "seker", "sekerim", "kan", "nabiz", "nabzim", "kalp",
                "kilo", "kilom", "agirlik"]
    for kw in priority:
        if kw not in _KEYWORDS:
            continue
        for tok in tokens:
            if kw in tok:
                return _KEYWORDS[kw]
    return None


def parse_measurement(text: str) -> Optional[ParsedMeasurement]:
    """Parse a Turkish phrase into a measurement record. Returns None on failure."""
    if not text:
        return None
    norm = _normalize(text)
    mtype = _detect_type(norm)
    if mtype is None:
        return None

    nums = _extract_numbers(norm)
    if not nums:
        return None

    if mtype == "bp":
        if len(nums) >= 2:
            sys_, dia = nums[0], nums[1]
        else:
            # "tansiyonum on iki sekiz" might be parsed as a single 128 → split.
            n = nums[0]
            if n > 30 and n < 1000:
                sys_, dia = round(n // 10) * 10 / 10, n % 10  # rare; fallback
                if dia < 5:  # implausible diastolic, give up
                    return None
            else:
                return None
        # Heuristic: if user said "on iki sekiz" the parser yields [12, 8]; multiply.
        if sys_ < 30:
            sys_ *= 10
        if dia < 30 and dia >= 4:  # 4..29 → diastolic in tens (e.g. 8 → 80)
            dia *= 10
        return ParsedMeasurement(type="bp", value1=sys_, value2=dia)

    return ParsedMeasurement(type=mtype, value1=nums[0])
