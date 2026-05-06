"""Doktor raporu: JSON özet, PNG trend, PDF."""
from __future__ import annotations

from datetime import datetime, timedelta
from io import BytesIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Measurement
from app.services.charts import render_trend_png, summarize
from app.services.pdf import build_report_pdf

router = APIRouter(tags=["reports"])


def _load(db: Session, patient_id: str, days: int) -> list[Measurement]:
    since = datetime.utcnow() - timedelta(days=days)
    stmt = (
        select(Measurement)
        .where(Measurement.patient_id == patient_id)
        .where(Measurement.ts >= since)
        .order_by(Measurement.ts.asc())
    )
    return list(db.execute(stmt).scalars().all())


@router.get("/report.json")
def report_json(
    patient_id: str = Query("demo"),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
) -> dict:
    rows = _load(db, patient_id, days)
    return summarize(rows, days=days, patient_id=patient_id)


@router.get("/report.png")
def report_png(
    patient_id: str = Query("demo"),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
) -> Response:
    rows = _load(db, patient_id, days)
    buf = BytesIO()
    render_trend_png(rows, buf)
    return Response(content=buf.getvalue(), media_type="image/png")


@router.get("/report.pdf")
def report_pdf(
    patient_id: str = Query("demo"),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
) -> Response:
    rows = _load(db, patient_id, days)
    buf = BytesIO()
    build_report_pdf(rows, buf, patient_id=patient_id, days=days)
    headers = {
        "Content-Disposition": f'attachment; filename="vitalog_{patient_id}_{days}g.pdf"'
    }
    return Response(
        content=buf.getvalue(),
        media_type="application/pdf",
        headers=headers,
    )
