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
from app.services.parser import parse_all_measurements
from app.services.transcribe import transcribe_audio

router = APIRouter(tags=["voice"])
AUDIO_DIR = Path("data/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def _persist(db: Session, *, patient_id: str, transcript: str) -> VoiceResult:
    parsed_list = parse_all_measurements(transcript)
    if not parsed_list:
        return VoiceResult(
            transcript=transcript,
            detected=False,
            message=(
                "Ölçüm anlaşılamadı. Örnek: 'Şekerim 135', "
                "'Tansiyon on iki sekiz', veya birden fazlasını bir arada."
            ),
        )

    rows: list[Measurement] = []
    for parsed in parsed_list:
        row = Measurement(
            patient_id=patient_id,
            type=parsed.type,
            value1=parsed.value1,
            value2=parsed.value2,
            raw_text=transcript,
        )
        db.add(row)
        rows.append(row)
    db.commit()
    outs: list[MeasurementOut] = []
    for row in rows:
        db.refresh(row)
        outs.append(MeasurementOut.model_validate(row))

    msgs = [p.summary() for p in parsed_list]
    combined = " • ".join(msgs) if len(msgs) > 1 else msgs[0]

    return VoiceResult(
        transcript=transcript,
        measurement=outs[-1],
        measurements=outs,
        detected=True,
        message=combined,
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
    text: str = Form(..., description='Örn. "Şekerim 135" veya çoklu ölçüm'),
    patient_id: str = Form("demo"),
    db: Session = Depends(get_db),
) -> VoiceResult:
    """STT olmadan /voice ile aynı parser yolu (Web Speech → burası)."""
    return _persist(db, patient_id=patient_id, transcript=text.strip())
