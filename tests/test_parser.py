"""Türkçe ölçüm parser birim testleri — hakem: test edilebilir MVP."""
from __future__ import annotations

import pytest

from app.services.parser import ParsedMeasurement, parse_all_measurements, parse_measurement


@pytest.mark.parametrize(
    "phrase,expected_type,expected_v1,expected_v2",
    [
        ("Şekerim yüz otuz beş", "sugar", 135.0, None),
        ("şeker 140", "sugar", 140.0, None),
        ("şeker 200", "sugar", 200.0, None),
        ("Tansiyon on iki sekiz", "bp", 120.0, 80.0),
        ("tansiyon 130 85", "bp", 130.0, 85.0),
        ("Nabız yetmiş iki", "pulse", 72.0, None),
        ("nabız 88", "pulse", 88.0, None),
        ("Kilo yetmiş beş buçuk", "weight", 75.5, None),
        ("kilom 80", "weight", 80.0, None),
        ("glikoz yüz on", "sugar", 110.0, None),
    ],
)
def test_parse_measurement_ok(
    phrase: str,
    expected_type: str,
    expected_v1: float,
    expected_v2: float | None,
) -> None:
    result = parse_measurement(phrase)
    assert result is not None
    assert isinstance(result, ParsedMeasurement)
    assert result.type == expected_type
    assert result.value1 == pytest.approx(expected_v1)
    if expected_v2 is None:
        assert result.value2 is None
    else:
        assert result.value2 == pytest.approx(expected_v2)


@pytest.mark.parametrize(
    "phrase",
    [
        "",
        "merhaba dünya",
        "şeker",
        "bugün hava güzel",
    ],
)
def test_parse_measurement_rejects(phrase: str) -> None:
    assert parse_measurement(phrase) is None


def test_parse_all_in_one_sentence() -> None:
    phrase = "şekerim 140 Tansiyonum 13'e 9 nabzım 75 kilom 58"
    parts = parse_all_measurements(phrase)
    assert len(parts) == 4
    assert parts[0].type == "sugar" and parts[0].value1 == 140
    assert parts[1].type == "bp" and parts[1].value1 == 130 and parts[1].value2 == 90
    assert parts[2].type == "pulse" and parts[2].value1 == 75
    assert parts[3].type == "weight" and parts[3].value1 == 58
