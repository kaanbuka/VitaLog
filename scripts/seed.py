"""Demo ölçümler — doktor panelinin ilk açılışta dolu görünmesi için.

Kullanım:
    python -m scripts.seed              # patient_id=demo, 30 gün
    python -m scripts.seed alice 14
"""
from __future__ import annotations

import random
import sys
from datetime import datetime, timedelta

from sqlalchemy import delete

from app.database import SessionLocal, init_db
from app.models import Measurement


def seed(patient_id: str = "demo", days: int = 30) -> None:
    init_db()
    rng = random.Random(42)
    db = SessionLocal()
    try:
        db.execute(delete(Measurement).where(Measurement.patient_id == patient_id))

        now = datetime.utcnow()
        for d in range(days, 0, -1):
            day = now - timedelta(days=d)
            morning = day.replace(hour=8, minute=rng.randint(0, 30))
            evening = day.replace(hour=20, minute=rng.randint(0, 30))

            sugar_morning = round(rng.gauss(110, 18))
            sugar_evening = round(rng.gauss(140, 22))
            sys_, dia = round(rng.gauss(128, 8)), round(rng.gauss(82, 6))
            pulse = round(rng.gauss(76, 6))

            db.add_all(
                [
                    Measurement(
                        patient_id=patient_id,
                        type="sugar",
                        value1=max(70, sugar_morning),
                        ts=morning,
                        raw_text="(seed) sabah şeker",
                    ),
                    Measurement(
                        patient_id=patient_id,
                        type="sugar",
                        value1=max(70, sugar_evening),
                        ts=evening,
                        raw_text="(seed) akşam şeker",
                    ),
                    Measurement(
                        patient_id=patient_id,
                        type="bp",
                        value1=max(95, sys_),
                        value2=max(55, dia),
                        ts=morning,
                        raw_text="(seed) tansiyon",
                    ),
                    Measurement(
                        patient_id=patient_id,
                        type="pulse",
                        value1=max(55, pulse),
                        ts=morning,
                        raw_text="(seed) nabız",
                    ),
                ]
            )
            if d % 3 == 0:
                db.add(
                    Measurement(
                        patient_id=patient_id,
                        type="weight",
                        value1=round(74 + rng.gauss(0, 0.6), 1),
                        ts=morning,
                        raw_text="(seed) kilo",
                    )
                )

        db.commit()
    finally:
        db.close()

    print(f"Seeded {days} days for patient_id={patient_id!r}")


if __name__ == "__main__":
    pid = sys.argv[1] if len(sys.argv) > 1 else "demo"
    days_ = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    seed(pid, days_)
