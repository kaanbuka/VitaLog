# VitaLog — AI izlenebilirlik (Plan / Skills)

SolveX şartnamesi ve hakem formu **“hangi kısım AI ile şekillendi?”** sorusuna yanıt verir. PR ve kod yorumlarında kısaca atıf yapılır.

## Plan Agent

| Çıktı | Konum |
|--------|--------|
| Mimari ve süreç | `ARCHITECTURE.md` |
| Hakem kriterleri ile çapraz kontrol | `HAKEM_UYUMU.md` |

## Skills Agent (örnek modüller)

| Alan | Dosya | Not |
|------|--------|-----|
| Türkçe doğal dil ölçüm çıkarımı | `app/services/parser.py` | Sözcük sayıları, anahtar kelimeler |
| İsteğe bağlı sunucu STT | `app/services/transcribe.py` | Whisper / yerel model / geri dönüş |
| Trend grafikleri | `app/services/charts.py` | matplotlib, başlık düzeni |
| PDF rapor | `app/services/pdf.py` | ReportLab birleşimi |

## Manuel / ekip

- GitHub Issues, PR incelemesi, seed veri senaryosu, UI metinleri.
- **Son kontrol:** teslim öncesi Cursor (veya seçilen araç) ile refactor/tarama — PR şablonunda onaylanır.
