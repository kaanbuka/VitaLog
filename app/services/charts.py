"""Matplotlib trend grafikleri ve doktor paneli için JSON özet.

Skills Agent (şartname §5.2): çok metrikli zaman serisi ve referans bantları.
"""
from __future__ import annotations

from collections import defaultdict
from io import BytesIO
from statistics import mean
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

# Türkçe etiketler (Şeker, Nabız, …) için Unicode uyumlu font
plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "DejaVu Sans Mono", "sans-serif"],
        "axes.unicode_minus": False,
    }
)

from app.models import Measurement

_LABELS = {
    "sugar": ("Şeker (mg/dL)", "tab:red"),
    "bp": ("Tansiyon (mmHg)", "tab:blue"),
    "pulse": ("Nabız (bpm)", "tab:green"),
    "weight": ("Kilo (kg)", "tab:purple"),
}

_RANGES = {
    "sugar": (70, 140),
    "bp": (90, 130),
    "pulse": (60, 100),
    "weight": None,
}


def summarize(rows: Iterable[Measurement], days: int, patient_id: str) -> dict:
    by_type: dict[str, list[Measurement]] = defaultdict(list)
    for r in rows:
        by_type[r.type].append(r)

    summary = {
        "patient_id": patient_id,
        "days": days,
        "total": sum(len(v) for v in by_type.values()),
        "metrics": {},
        "series": {},
    }
    for t, items in by_type.items():
        v1 = [i.value1 for i in items]
        summary["metrics"][t] = {
            "count": len(items),
            "min": min(v1) if v1 else None,
            "max": max(v1) if v1 else None,
            "avg": round(mean(v1), 1) if v1 else None,
        }
        summary["series"][t] = [
            {
                "ts": i.ts.isoformat(),
                "value1": i.value1,
                "value2": i.value2,
            }
            for i in items
        ]
    return summary


def render_trend_png(rows: list[Measurement], buf: BytesIO) -> None:
    """2x2 trend ızgarası; boş tiplerde 'Veri yok' yazar."""
    by_type: dict[str, list[Measurement]] = defaultdict(list)
    for r in rows:
        by_type[r.type].append(r)

    fig, axes = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
    fig.suptitle("VitaLog — Trend raporu", fontsize=14, fontweight="bold")

    for ax, (t, (label, color)) in zip(axes.ravel(), _LABELS.items()):
        items = sorted(by_type.get(t, []), key=lambda r: r.ts)
        ax.set_title(label)
        ax.grid(True, alpha=0.3)

        rng = _RANGES.get(t)
        if rng is not None:
            ax.axhspan(
                rng[0],
                rng[1],
                alpha=0.08,
                color="green",
                label=f"Hedef: {rng[0]}–{rng[1]}",
            )

        if not items:
            ax.text(
                0.5,
                0.5,
                "Veri yok",
                ha="center",
                va="center",
                transform=ax.transAxes,
                color="gray",
            )
            ax.set_xticks([])
            ax.set_yticks([])
            continue

        xs = [i.ts for i in items]
        ax.plot(
            xs,
            [i.value1 for i in items],
            "o-",
            color=color,
            label="Sistolik" if t == "bp" else label.split(" ")[0],
        )
        if t == "bp":
            ax.plot(
                xs,
                [i.value2 or 0 for i in items],
                "o--",
                color="tab:cyan",
                label="Diyastolik",
            )

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
        ax.tick_params(axis="x", rotation=30, labelsize=8)
        ax.legend(loc="best", fontsize=8)

    fig.savefig(buf, format="png", dpi=130)
    plt.close(fig)
    buf.seek(0)
