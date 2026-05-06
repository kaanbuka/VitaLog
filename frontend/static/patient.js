// Patient page — uses the browser's built-in Web Speech API (Turkish).
// Free, zero install, zero API keys. Recognized text is POSTed to /text.
// Falls back to manual typing on browsers without SpeechRecognition.
const micBtn = document.getElementById("micBtn");
const statusEl = document.getElementById("status");
const transcriptEl = document.getElementById("transcript");
const detectedEl = document.getElementById("detected");
const patientIdEl = document.getElementById("patientId");
const recentTbody = document.getElementById("recent");
const sttBanner = document.getElementById("sttBanner");
const textForm = document.getElementById("textForm");
const textInput = document.getElementById("textInput");

const TYPE_LABEL = { sugar: "Şeker", bp: "Tansiyon", pulse: "Nabız", weight: "Kilo" };
const TYPE_UNIT = { sugar: "mg/dL", bp: "mmHg", pulse: "bpm", weight: "kg" };

const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let recording = false;
let finalTranscript = "";

function applyResult(data) {
  transcriptEl.textContent = data.transcript || "(boş)";
  if (data.detected && data.measurement) {
    detectedEl.innerHTML = `<span class="detected">✓ ${data.message}</span>`;
  } else {
    detectedEl.innerHTML = `<span class="error">✗ ${data.message || "Anlaşılamadı"}</span>`;
  }
}

async function submitText(text) {
  const fd = new FormData();
  fd.append("text", text);
  fd.append("patient_id", patientIdEl.value || "demo");
  const res = await fetch("/text", { method: "POST", body: fd });
  if (!res.ok) throw new Error(`Sunucu ${res.status}`);
  return await res.json();
}

function setRecordingUI(on) {
  recording = on;
  micBtn.classList.toggle("recording", on);
  micBtn.textContent = on ? "Bitir" : "Kaydet";
  statusEl.textContent = on ? "Dinliyorum..." : "Hazır.";
}

if (SR) {
  recognition = new SR();
  recognition.lang = "tr-TR";
  recognition.interimResults = true;
  recognition.continuous = false;
  recognition.maxAlternatives = 1;

  recognition.onresult = (event) => {
    let interim = "";
    let final = "";
    for (let i = 0; i < event.results.length; i++) {
      const t = event.results[i][0].transcript;
      if (event.results[i].isFinal) final += t;
      else interim += t;
    }
    finalTranscript = final.trim();
    transcriptEl.textContent = (final + interim).trim() || "...";
  };

  recognition.onerror = (e) => {
    setRecordingUI(false);
    const msg =
      e.error === "not-allowed" ? "Mikrofon izni reddedildi."
      : e.error === "no-speech" ? "Ses algılanmadı, tekrar dene."
      : `Ses tanıma hatası: ${e.error}`;
    detectedEl.innerHTML = `<span class="error">✗ ${msg}</span>`;
  };

  recognition.onend = async () => {
    setRecordingUI(false);
    const text = finalTranscript.trim();
    if (!text) {
      if (!detectedEl.textContent) {
        detectedEl.innerHTML =
          `<span class="error">✗ Ses algılanmadı. Tekrar dene veya yazarak gir.</span>`;
      }
      return;
    }
    statusEl.textContent = "Kaydediliyor...";
    try {
      const data = await submitText(text);
      applyResult(data);
      statusEl.textContent = "Hazır.";
      await loadRecent();
    } catch (err) {
      detectedEl.innerHTML = `<span class="error">✗ ${err.message}</span>`;
    }
  };
} else {
  // Browser doesn't support Web Speech API — Firefox/Safari without flag.
  sttBanner.style.display = "block";
  sttBanner.innerHTML =
    "<b>Bu tarayıcı sesli girişi desteklemiyor.</b> En iyi sonuç için " +
    "<b>Chrome</b> veya <b>Edge</b> kullan, ya da aşağıdaki <em>Yazarak gir</em> alanını kullan.";
  micBtn.disabled = true;
  micBtn.style.opacity = "0.5";
  micBtn.title = "Tarayıcı desteklemiyor";
}

micBtn.addEventListener("click", () => {
  if (!recognition) return;
  if (recording) {
    recognition.stop();
    return;
  }
  finalTranscript = "";
  transcriptEl.textContent = "";
  detectedEl.innerHTML = "";
  try {
    recognition.start();
    setRecordingUI(true);
  } catch (err) {
    detectedEl.innerHTML = `<span class="error">✗ ${err.message}</span>`;
  }
});

async function loadRecent() {
  const pid = encodeURIComponent(patientIdEl.value || "demo");
  const res = await fetch(`/measurements?patient_id=${pid}&days=7`);
  const items = await res.json();
  recentTbody.innerHTML = items
    .slice(-10)
    .reverse()
    .map((m) => {
      const ts = new Date(m.ts).toLocaleString("tr-TR");
      const val =
        m.type === "bp" && m.value2
          ? `${m.value1}/${m.value2} mmHg`
          : `${m.value1} ${TYPE_UNIT[m.type] || ""}`;
      return `<tr>
        <td>${ts}</td>
        <td>${TYPE_LABEL[m.type] || m.type}</td>
        <td><b>${val}</b></td>
        <td class="muted">${m.raw_text || ""}</td>
      </tr>`;
    })
    .join("");
}

patientIdEl.addEventListener("change", loadRecent);
loadRecent();

// Always-available manual fallback (works on any browser, with or without STT).
textForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = (textInput.value || "").trim();
  if (!text) return;
  try {
    const data = await submitText(text);
    applyResult(data);
    if (data.detected) textInput.value = "";
    await loadRecent();
  } catch (err) {
    detectedEl.innerHTML = `<span class="error">✗ ${err.message}</span>`;
  }
});
