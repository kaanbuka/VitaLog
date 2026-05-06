"""FastAPI giriş noktası: voice (/text), ölçümler, raporlar, statik hasta/doktor sayfaları."""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routes import measurements, reports, voice

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="VitaLog", version="0.1.0", lifespan=lifespan)

app.include_router(voice.router)
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
def healthz() -> dict[str, object]:
    """Varsayılan akışta tarayıcı Web Speech yeterli; server_stt isteğe bağlı /voice içindir."""
    server_stt = bool(os.getenv("OPENAI_API_KEY"))
    if not server_stt:
        try:
            import faster_whisper  # noqa: F401

            server_stt = True
        except ImportError:
            pass
    return {"status": "ok", "server_stt": server_stt}
