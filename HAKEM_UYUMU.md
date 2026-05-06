# Hakem değerlendirme formu — depodaki karşılıklar

Bu dosya `hakem_degerlendirme.pdf` maddeleri ile **somut artefakt** eşlemesi içindir.

## 1. AI-AUGMENTED DEVELOPMENT (0–45)

| Kriter | Kanıt (repoda) |
|--------|----------------|
| **Plan Agent** | `ARCHITECTURE.md` — mimari ve süreç |
| **Skills Agent** | `AI_TRACEABILITY.md`; `parser.py`, `transcribe.py`, `charts.py`, `pdf.py` dosya başı notları |
| **Araç yetkinliği** | PR açıklamaları; geliştirme Cursor vb. ile yapıldığı beyanı |

## 2. PROFESYONEL ÇALIŞMA VE EKİP RUHU (0–20)

| Kriter | Kanıt |
|--------|--------|
| **Düzenli çalışma** | GitHub Flow; küçük PR’lar; branch kuralları (`ARCHITECTURE.md` §4) |
| **Hata denetimi** | `.github/pull_request_template.md` — review beklenir |

## 3. SÜREÇ ŞEFFAFLIĞI VE KALİTE (0–20)

| Kriter | Kanıt |
|--------|--------|
| **Takip edilebilirlik** | `AI_TRACEABILITY.md`; PR şablonu |
| **Son kontrol** | PR şablonunda “AI ile son tarama” kutusu; teslim öncesi checklist |

## 4. MVP hazırlığı (0–15)

| Kriter | Kanıt |
|--------|--------|
| **Çalışır prototip** | `README.md` kurulum; `pytest`; `/`, `/doctor`, `/text`, `/report.json` |
