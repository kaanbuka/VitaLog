"""Tek sayfalık doktor PDF'i: başlık, özet tablo, gömülü trend grafiği.

Skills Agent (şartname §5.2): ReportLab düzeni ve grafik gömme.
Türkçe karakterler için DejaVu Sans TTF (Helvetica yerine).
"""
from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path

import matplotlib
from reportlab.lib import colors
from reportlab.lib.fonts import addMapping
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
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

_FONT_FAMILY = "VitaDejaVu"
_FONT_REGISTERED = False


def _ensure_turkish_pdf_font() -> None:
    """ReportLab Helvetica Türkçe desteklemez; Matplotlib ile gelen DejaVu Sans kullanılır."""
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return
    ttf_dir = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    regular = ttf_dir / "DejaVuSans.ttf"
    bold = ttf_dir / "DejaVuSans-Bold.ttf"
    italic = ttf_dir / "DejaVuSans-Oblique.ttf"
    if not regular.is_file():
        raise FileNotFoundError(
            f"Türkçe PDF fontu bulunamadı (DejaVu Sans): {regular}"
        )
    if not bold.is_file():
        bold = regular
    pdfmetrics.registerFont(TTFont(f"{_FONT_FAMILY}", str(regular)))
    pdfmetrics.registerFont(TTFont(f"{_FONT_FAMILY}-Bold", str(bold)))
    italic_font_path = italic if italic.is_file() else regular
    pdfmetrics.registerFont(TTFont(f"{_FONT_FAMILY}-Italic", str(italic_font_path)))
    addMapping(_FONT_FAMILY, 0, 0, _FONT_FAMILY)
    addMapping(_FONT_FAMILY, 1, 0, f"{_FONT_FAMILY}-Bold")
    addMapping(_FONT_FAMILY, 0, 1, f"{_FONT_FAMILY}-Italic")
    bi = ttf_dir / "DejaVuSans-BoldOblique.ttf"
    if bi.is_file():
        pdfmetrics.registerFont(TTFont(f"{_FONT_FAMILY}-BoldItalic", str(bi)))
        addMapping(_FONT_FAMILY, 1, 1, f"{_FONT_FAMILY}-BoldItalic")
    else:
        addMapping(_FONT_FAMILY, 1, 1, f"{_FONT_FAMILY}-Bold")
    _FONT_REGISTERED = True


def build_report_pdf(
    rows: list[Measurement],
    out: BytesIO,
    *,
    patient_id: str,
    days: int,
) -> None:
    _ensure_turkish_pdf_font()

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

    title_style = ParagraphStyle(
        "TitleTR",
        parent=styles["Title"],
        fontName=_FONT_FAMILY,
    )
    normal_style = ParagraphStyle(
        "NormalTR",
        parent=styles["Normal"],
        fontName=_FONT_FAMILY,
    )
    italic_style = ParagraphStyle(
        "ItalicTR",
        parent=styles["Italic"],
        fontName=f"{_FONT_FAMILY}-Italic",
    )

    story = []

    story.append(Paragraph("<b>VitaLog — Doktor Raporu</b>", title_style))
    story.append(
        Paragraph(
            f"Hasta: <b>{patient_id}</b> &nbsp;&nbsp; "
            f"Dönem: son <b>{days}</b> gün &nbsp;&nbsp; "
            f"Oluşturulma: {datetime.now():%d/%m/%Y %H:%M}",
            normal_style,
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
                ("FONTNAME", (0, 0), (-1, 0), f"{_FONT_FAMILY}-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), _FONT_FAMILY),
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
            italic_style,
        )
    )

    doc.build(story)
    out.seek(0)
