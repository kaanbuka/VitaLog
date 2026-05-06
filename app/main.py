"""FastAPI giriş noktası: raporlar, ölçümler, statik doktor/hasta sayfaları."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routes import measurements, reports

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"

app = FastAPI(title="VitaLog", version="0.1.0")


@app.on_event("startup")
def _startup() -> None:
    init_db()


app.include_router(measurements.router)
app.include_router(reports.router)

app.mount("/static", StaticFiles(directory=FRONTEND / "static"), name="static")


@app.get("/", include_in_schema=False)
def patient_page() -> FileResponse:
    return FileResponse(FRONTEND / "patient.html")


@app.get("/doctor", include_in_schema=False)
def doctor_page() -> FileResponse:
    return FileResponse(FRONTEND / "doctor.html")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
