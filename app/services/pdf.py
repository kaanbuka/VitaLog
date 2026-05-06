"""Tek sayfalık doktor PDF'i: başlık, özet tablo, gömülü trend grafiği."""
from __future__ import annotations

from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models import Measurement
from app.services.charts import render_trend_png, summarize

_LABEL = {"sugar": "Şeker", "bp": "Tansiyon", "pulse": "Nabız", "weight": "Kilo"}


def build_report_pdf(
    rows: list[Measurement],
    out: BytesIO,
    *,
    patient_id: str,
    days: int,
) -> None:
    summary = summarize(rows, days=days, patient_id=patient_id)
    chart_buf = BytesIO()
    render_trend_png(rows, chart_buf)

    doc = SimpleDocTemplate(
        out,
        pagesize=A4,
        leftMargin=1.6 * cm,
        rightMargin=1.6 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.4 * cm,
    )
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>VitaLog — Doktor Raporu</b>", styles["Title"]))
    story.append(
        Paragraph(
            f"Hasta: <b>{patient_id}</b> &nbsp;&nbsp; "
            f"Dönem: son <b>{days}</b> gün &nbsp;&nbsp; "
            f"Oluşturulma: {datetime.now():%d/%m/%Y %H:%M}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 0.4 * cm))

    table_data = [["Ölçüm", "Adet", "Min", "Ort", "Max"]]
    for t, m in summary["metrics"].items():
        table_data.append(
            [
                _LABEL.get(t, t),
                m["count"],
                f"{m['min']:g}" if m["min"] is not None else "-",
                f"{m['avg']:g}" if m["avg"] is not None else "-",
                f"{m['max']:g}" if m["max"] is not None else "-",
            ]
        )
    if len(table_data) == 1:
        table_data.append(["(kayıt yok)", "-", "-", "-", "-"])

    table = Table(
        table_data,
        hAlign="LEFT",
        colWidths=[3.5 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Image(chart_buf, width=17 * cm, height=11 * cm))
    story.append(Spacer(1, 0.3 * cm))
    story.append(
        Paragraph(
            "<i>Bu rapor VitaLog tarafından otomatik üretilmiştir. "
            "Klinik karar için lütfen ham verileri inceleyin.</i>",
            styles["Italic"],
        )
    )

    doc.build(story)
    out.seek(0)
