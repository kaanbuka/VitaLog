"""POST /voice — ses dosyası; POST /text — yazılı ifade (tarayıcı STT buraya bağlanır)."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Measurement
from app.schemas import MeasurementOut, VoiceResult
from app.services.parser import parse_measurement
from app.services.transcribe import transcribe_audio

router = APIRouter(tags=["voice"])
AUDIO_DIR = Path("data/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def _persist(db: Session, *, patient_id: str, transcript: str) -> VoiceResult:
    parsed = parse_measurement(transcript)
    if parsed is None:
        return VoiceResult(
            transcript=transcript,
            detected=False,
            message=(
                "Ölçüm anlaşılamadı. Örnek: 'Şekerim 135', "
                "'Tansiyon on iki sekiz', 'Nabız yetmiş iki'."
            ),
        )
    row = Measurement(
        patient_id=patient_id,
        type=parsed.type,
        value1=parsed.value1,
        value2=parsed.value2,
        raw_text=transcript,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return VoiceResult(
        transcript=transcript,
        measurement=MeasurementOut.model_validate(row),
        detected=True,
        message=parsed.summary(),
    )


@router.post("/voice", response_model=VoiceResult)
async def upload_voice(
    audio: UploadFile = File(..., description="webm/ogg/wav kayıt"),
    patient_id: str = Form("demo"),
    db: Session = Depends(get_db),
) -> VoiceResult:
    original = audio.filename or "rec.webm"
    suffix = Path(original).suffix or ".webm"
    path = AUDIO_DIR / f"{datetime.utcnow():%Y%m%d_%H%M%S}_{uuid4().hex[:8]}{suffix}"
    path.write_bytes(await audio.read())

    transcript = transcribe_audio(path, hint_filename=original)
    return _persist(db, patient_id=patient_id, transcript=transcript)


@router.post("/text", response_model=VoiceResult)
def submit_text(
    text: str = Form(..., description='Örn. "Şekerim 135"'),
    patient_id: str = Form("demo"),
    db: Session = Depends(get_db),
) -> VoiceResult:
    """STT olmadan /voice ile aynı parser yolu (Web Speech → burası)."""
    return _persist(db, patient_id=patient_id, transcript=text.strip())
