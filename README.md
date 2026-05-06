# VitaLog — Sesli vücut günlüğü ve otomatik raporlayıcı

Kronik hastaların günlük ölçümlerini **konuşarak veya yazarak** kaydettiği, doktorun **trend grafikleri ve PDF rapor** aldığı web demosu.

> Akış: Hasta → Web Speech veya yazı → `POST /text` → parser → SQLite → doktor paneli (`/doctor`).

## Hızlı başlangıç

```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # isteğe bağlı
python -m scripts.seed  # demo veri (önerilir)
uvicorn app.main:app --reload
```

## Testler (hakem: test edilebilir MVP)

```bash
pytest
```

## Önemli URL’ler

| Adres | Açıklama |
|--------|-----------|
| http://localhost:8000/docs | OpenAPI |
| http://localhost:8000/healthz | Sağlık + `server_stt` bayrağı |
| http://localhost:8000/text | Form: hasta metni (Web Speech buraya bağlanır) |
| http://localhost:8000/measurements | Ölçüm listesi |
| http://localhost:8000/report.json | Doktor özeti |
| http://localhost:8000/report.pdf | PDF indir |
| http://localhost:8000/ | Hasta arayüzü |
| http://localhost:8000/doctor | Doktor paneli |

Ses için **Chrome/Edge** kullanın; adres **`http://localhost:8000`** olsun (`127.0.0.1` değil).

## Hakem / şartname dokümanları

- `ARCHITECTURE.md` — Plan Agent mimarisi  
- `AI_TRACEABILITY.md` — Plan/Skills izlenebilirliği  
- `HAKEM_UYUMU.md` — Hakem formu maddeleri ile depo karşılığı  
- `.github/pull_request_template.md` — PR’da review ve AI son kontrol kutuları  

## Opsiyonel: sunucu tarafı STT (`/voice`)

| Seçenek | Not |
|---------|-----|
| OpenAI Whisper | `.env` → `OPENAI_API_KEY` |
| faster-whisper | `pip install faster-whisper` |

## Mimari (özet)

```
Tarayıcı → Web Speech / yazı → POST /text → FastAPI → parser → SQLite
Doktor → /report.json | /report.pdf | Chart.js
```

## Takım dosya sorumluluğu (özet)

| Alan | Sorumlu |
|------|---------|
| Backend omurga, `voice`/`measurements`, seed | Lead |
| Parser, `transcribe`, hasta UI, `tests` | Ömer |
| Grafik, PDF, `reports`, doktor UI | Yiğit |
