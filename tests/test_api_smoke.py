"""API duman testleri — FastAPI TestClient; startup ile DB tabloları oluşur."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


def test_healthz(client: TestClient) -> None:
    r = client.get("/healthz")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"
    assert "server_stt" in data


def test_post_text_parses_sugar(client: TestClient) -> None:
    r = client.post(
        "/text",
        data={"text": "Şekerim yüz kırk", "patient_id": "pytest"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("detected") is True
    assert body.get("measurement") is not None
    assert body["measurement"]["type"] == "sugar"


def test_report_json_returns_summary(client: TestClient) -> None:
    r = client.get("/report.json", params={"patient_id": "demo", "days": 7})
    assert r.status_code == 200
    body = r.json()
    assert "patient_id" in body
    assert "metrics" in body or "series" in body
