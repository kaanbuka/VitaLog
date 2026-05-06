"""Person A: extend with more sentences as you add synonyms."""
from __future__ import annotations

import pytest

from app.services.parser import parse_measurement


@pytest.mark.parametrize(
    "phrase, expected_type, expected_v1, expected_v2",
    [
        ("Şekerim yüz otuz beş", "sugar", 135, None),
        ("kan şekerim 140", "sugar", 140, None),
        ("Glikozum 92", "sugar", 92, None),
        ("Tansiyon on iki sekiz", "bp", 120, 80),
        ("tansiyonum 13 9", "bp", 130, 90),
        ("Tansiyonum 130 85", "bp", 130, 85),
        ("Nabız yetmiş iki", "pulse", 72, None),
        ("nabzim 88", "pulse", 88, None),
        ("Kilom yetmiş dört buçuk", "weight", 74.5, None),
        ("kilom 80", "weight", 80, None),
    ],
)
def test_parse(phrase: str, expected_type: str, expected_v1: float, expected_v2):
    m = parse_measurement(phrase)
    assert m is not None, f"Could not parse: {phrase!r}"
    assert m.type == expected_type
    assert m.value1 == pytest.approx(expected_v1)
    if expected_v2 is None:
        assert m.value2 is None
    else:
        assert m.value2 == pytest.approx(expected_v2)


def test_unparseable_returns_none():
    assert parse_measurement("merhaba doktor") is None
    assert parse_measurement("") is None
