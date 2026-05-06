"""ORM modelleri. Hackathon demosu için tek tablo yeterli."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[str] = mapped_column(String(64), index=True)
    # sugar | bp | pulse | weight
    type: Mapped[str] = mapped_column(String(16), index=True)
    # şeker mg/dL, sistolik, nabız bpm, kilo kg
    value1: Mapped[float] = mapped_column(Float)
    # bp için diyastolik; diğerlerinde NULL
    value2: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(String(512), nullable=True)
    ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), index=True
    )
