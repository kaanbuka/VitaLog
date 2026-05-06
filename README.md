# VitaLog — Sesli vücut günlüğü ve otomatik raporlayıcı

Kronik hastaların günlük ölçümlerini **konuşarak veya yazarak** kaydettiği, doktorun **trend grafikleri ve PDF rapor** aldığı web demosu.

> Akış: Hasta → (tarayıcı STT veya yazı) → metin → parser → SQLite → doktor paneli.

## Hızlı başlangıç

```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # isteğe bağlı; varsayılan SQLite yolu yeterli
python -m scripts.seed  # demo veri (opsiyonel)
uvicorn app.main:app --reload
```

| Adres | Açıklama |
|--------|-----------|
| http://localhost:8000/docs | OpenAPI |
| http://localhost:8000/healthz | Sağlık kontrolü |
| http://localhost:8000/measurements | Ölçüm listesi API |
| http://localhost:8000/ | Hasta arayüzü (ST-2 tamamlanınca) |
| http://localhost:8000/doctor | Doktor paneli (ST-3 ile tam özellik) |

Tarayıcıda ses için **Chrome/Edge** ve adres olarak **`http://localhost:8000`** kullanın (`127.0.0.1` değil).

## Takım ve dosya sorumluluğu

| Alan | Kişi | Dosyalar |
|------|------|----------|
| Backend omurga, API, seed | Lead | `app/main.py`, `database.py`, `models.py`, `schemas.py`, `routes/voice.py`, `routes/measurements.py`, `scripts/seed.py`, `requirements.txt`, `.env.example` |
| Ses/NLP, hasta UI, test | Ömer | `app/services/parser.py`, `transcribe.py`, `frontend/patient.*`, `tests/` |
| Rapor, doktor UI | Yiğit | `app/services/charts.py`, `pdf.py`, `routes/reports.py`, `frontend/doctor.*` |

`main.py`, önceki modüller hazır olana kadar **voice** ve **reports** route’larını otomatik devreye alır (bağımlılık yoksa atlanır).

## Opsiyonel: sunucu tarafı STT (`/voice`)

Hasta sayfası varsayılan olarak tarayıcı STT kullanır. Ses dosyası yüklemek için:

| Seçenek | Not |
|---------|-----|
| OpenAI Whisper | `.env` içinde `OPENAI_API_KEY` |
| `faster-whisper` | `pip install faster-whisper`, `.env` ile model |

## Mimari (özet)

```
Tarayıcı → Web Speech / yazı → POST /text
                    → FastAPI → parser → SQLite
Doktor → GET /report.json | /report.pdf | /measurements
```

## Jüri demosu (hedef ~60 sn)

1. `/` — ölçüm söyle veya yaz.
2. `/doctor?patient=demo` — grafikler (ST-3).
3. PDF indir (ST-3).

## Şartname / süreç

- GitHub Flow, `main` korumalı, küçük PR’lar, kod incelemesi.
- Plan: `ARCHITECTURE.md`.
