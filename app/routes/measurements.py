"""GET /measurements — hasta + gün filtresi (doktor tablosu için)."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Measurement
from app.schemas import MeasurementOut

router = APIRouter(tags=["measurements"])


@router.get("/measurements", response_model=List[MeasurementOut])
def list_measurements(
    patient_id: str = Query("demo"),
    days: int = Query(30, ge=1, le=365),
    type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> List[MeasurementOut]:
    since = datetime.utcnow() - timedelta(days=days)
    stmt = (
        select(Measurement)
        .where(Measurement.patient_id == patient_id)
        .where(Measurement.ts >= since)
        .order_by(Measurement.ts.asc())
    )
    if type:
        stmt = stmt.where(Measurement.type == type)
    rows = db.execute(stmt).scalars().all()
    return [MeasurementOut.model_validate(r) for r in rows]


@router.delete("/measurements/{mid}")
def delete_measurement(mid: int, db: Session = Depends(get_db)) -> dict[str, bool]:
    row = db.get(Measurement, mid)
    if row is None:
        return {"deleted": False}
    db.delete(row)
    db.commit()
    return {"deleted": True}
