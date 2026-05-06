# VitaLog — Mimari ve Süreç Dokümanı

**SolveX AI Hackathon 2026 — Teknik Uygulama Şartnamesi uyumu**

Bu dosya şartnamede istenen **Plan Agent** çıktısıdır: geliştirme başlamadan önce hazırlanan mimari plan repoda `ARCHITECTURE.md` olarak saklanır; görev **alt görevlere (sub-tasks)** ayrılmıştır ve GitHub **Issues** ile eşleştirilir.

---

## 1. Şartname ile hizalama

| Şartname beklentisi | VitaLog tarafında karşılığı |
|---------------------|-----------------------------|
| AI-Augmented Development; süreç mühendislik disiplini içinde | GitHub Flow, Issue/PR, kod standardı, AI ile planlama ve Skills kullanımı |
| Web / mobil / masaüstü veya uçtan uca iş akışı | **Web platformu** (FastAPI + tarayıcı istemcisi) |
| Manuel emeği azaltma; AI otomasyon verimliliğini kanıtlama | Ses/yazı ile ölçüm kaydı; otomatik metin ayrıştırma; doktor için tek tık PDF/trend |
| 3 kişilik takım ve roller | Aşağıdaki [Takım ve roller](#3-takım-ve-roller-şartname-madde-3) bölümü |
| GitHub Flow; `main`’e doğrudan push yok; PR + code review | [Sürüm kontrolü](#4-sürüm-kontrolü-github--şartname-madde-4) |
| Plan Agent + Skills Agent | Bu belge = Plan; karmaşık modüllerde Skills — [AI süreci](#5-ai-augmented-development-şartname-madde-5) |
| Her görev Issue; izlenebilirlik; teslim öncesi AI refactor | [İş takibi ve teslim](#6-iş-takibi-dokümantasyon-ve-teslim-şartname-madde-6) |

---

## 2. Problem ve ürün özeti (şartname madde 2)

**Problem (yarışma bağlamı):** Sağlık takibinde günlük ölçümlerin sık ve düşük sürtünmesiz kaydı; doktor tarafında özet görünürlük.

**Çözüm — VitaLog:** Kronik hastaların şeker, tansiyon, nabız ve kilo ölçümlerini **konuşarak veya yazarak** kaydetmesi; doktorun aynı platformdan **trend grafikleri** ve **PDF rapor** alması.

**Manuel emeğin azaltılması:** Tek tek form doldurma yerine doğal dil veya kısa yazı; sunucuda yapılandırılmış ölçüm çıkarımı (parser) ve otomatik rapor üretimi.

**AI verimliliği iddiası:** Planlama ve karmaşık dil/ses işleme adımlarında AI destekli geliştirme (Plan/Skills); ürün içinde varsayılan olarak tarayıcı STT (Web Speech API) ile sunucu maliyeti olmadan ses-metin otomasyonu.

---

## 3. Takım ve roller (şartname madde 3)

| Rol | Şartname tanımı | VitaLog’ta sorumluluk |
|-----|-----------------|------------------------|
| **Lead Developer / Maintainer** (1 kişi) | Ana repo, kod standardı, PR onayı | Branch/PR düzeni; `main` kalitesi; çekirdek API/DB/CI; mimari doküman güncelliği |
| **Feature Developer** (2 kişi) | Issue’lara göre modül, birim testi, depoya iletim | Biri: Türkçe parser, hasta arayüzü, `tests`. Diğeri: raporlar, grafik/PDF, doktor arayüzü |

---

## 4. Sürüm kontrolü (GitHub — şartname madde 4)

- **Model:** GitHub Flow.
- **`main`:** Dağıtıma hazır, stabil sürüm; **doğrudan push yok** (repo ayarı + iş kuralı).
- **Dallar:** `feature/görev-adi` veya `fix/hata-adi` (ör. `feature/parser-tests`, `fix/pdf-encoding`).
- **Commit mesajları:** Şimdiki zaman, teknik özet; şartname örneğiyle uyumlu — `feat: ...`, `fix: ...`, `test: ...`, `docs: ...`.
- **Merge:** Yalnızca **Pull Request**; PR’lar **en az bir** takım üyesinin **code review** onayından geçer.

---

## 5. AI-Augmented Development (şartname madde 5)

**Seçilen araçlar (örnek):** Cursor (veya şartnamede sayılan eşdeğer IDE/ajan araçları).

**Plan Agent**

- Çıktı: Bu `ARCHITECTURE.md` dosyası + Issues’taki alt görevler.
- Alt görevler jüriye GitHub Issue numaraları ve PR referansları ile izlenebilir.

**Skills Agent**

- **Türkçe doğal sayı ve ölçüm anahtar kelimeleri** ayrıştırması (`parser`): kenar durumlar ve sayı sözcükleri için uzmanlaştırılmış taslak ve gözden geçirme.
- **İsteğe bağlı sunucu STT** (`transcribe`): API veya yerel Whisper seçimi, hata ve geri dönüş davranışı.
- Şartname gereği: Bu etkileşimlerden gelen tasarım kararları ilgili **kod yorumlarında** kısaca belirtilir.

---

## 6. İş takibi, dokümantasyon ve teslim (şartname madde 6)

- **GitHub Issues:** Her görev bir Issue; geliştiriciye **assign**.
- **AI traceability:** İlgili dosya başları veya PR açıklamalarında Plan/Skills ile şekillenen bölümler kısaca işaretlenir.
- **Final review:** Teslim önce kodun tamamı seçilen AI aracıyla **refactoring ve optimization** taramasından geçirilir (işlev korunarak).

---

## 7. Teknik mimari (ürün)

### 7.1 Bileşenler

| Katman | Teknoloji | Not |
|--------|-----------|-----|
| API | FastAPI | REST, `/docs` ile sözleşme |
| Veri | SQLite + SQLAlchemy | Tek dosya DB; demo ve taşınabilirlik |
| Hasta STT (varsayılan) | Web Speech API → metin | Anahtarsız; sonuç `POST /text` |
| Sunucu STT (opsiyonel) | Whisper API veya `faster-whisper` | `POST /voice` ses dosyası |
| Ölçüm çıkarımı | Python parser | Türkçe metin → yapılandırılmış ölçüm |
| Doktor görünümü | Chart.js + `/report.json` | İstemci grafikleri |
| PDF / görüntü | matplotlib, ReportLab | `/report.pdf`, `/report.png` |

### 7.2 Veri modeli (özet)

`measurements`: `patient_id`, `type` (`sugar` | `bp` | `pulse` | `weight`), `value1`, `value2` (tansiyon için diyastolik), `raw_text`, `ts`.

### 7.3 İstek akışı

```
Hasta → (ses veya yazı) → POST /text veya POST /voice → parser → SQLite
Doktor → GET /report.json | /report.pdf | /measurements → grafik / PDF
```

### 7.4 Şartname sözlüğü ile eşleştirme (özet)

- **Repository / Main / Feature branch / PR / Code review / Merge:** §4 ile uyumlu süreç.
- **Traceability:** Issue → branch → commit → PR zinciri.
- **Refactoring:** Teslim öncesi AI yardımlı temizlik turu.

---

## 8. Plan Agent — alt görev listesi (sub-tasks → Issues)

Aşağıdaki maddeler ayrı **GitHub Issue** olarak açılmalı ve numaraları bu dokümanda veya `ROADMAP.md` içinde referanslanabilir.

| ID | Alt görev | Tipik assignee |
|----|-----------|----------------|
| ST-1 | Repo iskeleti: FastAPI giriş, DB kurulumu, `healthz`, statik dosyalar | Lead |
| ST-2 | `measurements` API ve seed/demo veri | Lead veya Feature |
| ST-3 | Parser + birim testler (`tests/`) | Feature (NLP) |
| ST-4 | Hasta sayfası (Web Speech + yazılı fallback) | Feature (NLP) |
| ST-5 | Rapor özeti JSON, matplotlib PNG, ReportLab PDF | Feature (rapor) |
| ST-6 | Doktor paneli (Chart.js, tablo, PDF indir) | Feature (rapor) |
| ST-7 | Dokümantasyon (`README`), demo senaryosu, son AI refactor | Takım |

---

## 9. Riskler ve kısıtlar

- Web Speech: Chrome/Edge önerisi; `localhost` veya HTTPS.
- Safari/Firefox: ses kısıtlı olabilir; yazılı giriş yolu şart.
- Şartname uyumu sürekli süreçtir: dal adları, PR, review ve Issue disiplini korunur.

---

## 10. Hakem değerlendirme formu ile çapraz kontrol

Resmi puanlama maddeleri ve depodaki kanıtların eşlemesi: **`HAKEM_UYUMU.md`**.  
AI izlenebilirlik özeti: **`AI_TRACEABILITY.md`**.

---

*Bu dosya SolveX AI Hackathon 2026 Teknik Uygulama Şartnamesi’nde tanımlanan **Plan Agent** rolü kapsamında üretilmiş ve repoda saklanmıştır.*
