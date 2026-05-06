"""API için Pydantic şemaları."""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

MeasurementType = Literal["sugar", "bp", "pulse", "weight"]


class MeasurementOut(BaseModel):
    id: int
    patient_id: str
    type: MeasurementType
    value1: float
    value2: Optional[float] = None
    raw_text: Optional[str] = None
    ts: datetime

    class Config:
        from_attributes = True


class VoiceResult(BaseModel):
    transcript: str
    measurement: Optional[MeasurementOut] = None
    detected: bool = Field(
        default=False,
        description="Parser metinden ölçüm çıkardıysa True.",
    )
    message: str = ""
