// Doctor panel: /report.json + /measurements → KPI, Chart.js, tablo, PDF linki.
const params = new URLSearchParams(location.search);
const patientIdEl = document.getElementById("patientId");
const daysEl = document.getElementById("days");
patientIdEl.value = params.get("patient") || "demo";

const TYPE_LABEL = { sugar: "Şeker", bp: "Tansiyon", pulse: "Nabız", weight: "Kilo" };
const TYPE_UNIT = { sugar: "mg/dL", bp: "mmHg", pulse: "bpm", weight: "kg" };

const charts = {};

function makeChart(id, label, color, data2 = null) {
  const ctx = document.getElementById(id).getContext("2d");
  if (charts[id]) charts[id].destroy();
  const datasets = [
    {
      label,
      data: [],
      borderColor: color,
      backgroundColor: color + "33",
      tension: 0.25,
      pointRadius: 3,
    },
  ];
  if (data2) datasets.push(data2);
  charts[id] = new Chart(ctx, {
    type: "line",
    data: { labels: [], datasets },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: "#0b1220" } } },
      scales: {
        x: { ticks: { color: "#475569" } },
        y: { ticks: { color: "#475569" } },
      },
    },
  });
  return charts[id];
}

function fmtTs(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString("tr-TR", { day: "2-digit", month: "2-digit" });
}

function renderKpis(metrics) {
  const cards = Object.entries(metrics).map(([t, m]) => {
    const unit = TYPE_UNIT[t] || "";
    return `<div class="card" style="margin:0;">
      <div class="muted">${TYPE_LABEL[t] || t}</div>
      <div class="metric">${m.avg ?? "-"} <small>ort. ${unit}</small></div>
      <div class="muted">min ${m.min ?? "-"} • max ${m.max ?? "-"} • ${m.count} ölçüm</div>
    </div>`;
  });
  document.getElementById("kpis").innerHTML = cards.length
    ? cards.join("")
    : `<div class="muted">Bu dönemde kayıt yok.</div>`;
}

function renderCharts(series) {
  const sugar = series.sugar || [];
  charts.chartSugar.data.labels = sugar.map((p) => fmtTs(p.ts));
  charts.chartSugar.data.datasets[0].data = sugar.map((p) => p.value1);
  charts.chartSugar.update();

  const bp = series.bp || [];
  charts.chartBp.data.labels = bp.map((p) => fmtTs(p.ts));
  charts.chartBp.data.datasets[0].data = bp.map((p) => p.value1);
  charts.chartBp.data.datasets[1].data = bp.map((p) => p.value2);
  charts.chartBp.update();

  const pulse = series.pulse || [];
  charts.chartPulse.data.labels = pulse.map((p) => fmtTs(p.ts));
  charts.chartPulse.data.datasets[0].data = pulse.map((p) => p.value1);
  charts.chartPulse.update();

  const weight = series.weight || [];
  charts.chartWeight.data.labels = weight.map((p) => fmtTs(p.ts));
  charts.chartWeight.data.datasets[0].data = weight.map((p) => p.value1);
  charts.chartWeight.update();
}

function showLoadError(err) {
  document.getElementById("kpis").innerHTML = `<div class="muted">Veri alınamadı. Sunucuda <code>/report.json</code> ve <code>/measurements</code> hazır mı? (${String(err.message || err)})</div>`;
  document.getElementById("all").innerHTML = "";
}

async function load() {
  const pid = encodeURIComponent(patientIdEl.value || "demo");
  const days = +daysEl.value || 30;

  try {
    const [r1, r2] = await Promise.all([
      fetch(`/report.json?patient_id=${pid}&days=${days}`),
      fetch(`/measurements?patient_id=${pid}&days=${days}`),
    ]);
    if (!r1.ok || !r2.ok) {
      throw new Error(`HTTP ${r1.status} / ${r2.status}`);
    }
    const report = await r1.json();
    const all = await r2.json();

    renderKpis(report.metrics || {});
    renderCharts(report.series || {});

    document.getElementById("all").innerHTML = all
      .slice()
      .reverse()
      .map((m) => {
        const ts = new Date(m.ts).toLocaleString("tr-TR");
        const val =
          m.type === "bp" && m.value2 != null
            ? `${m.value1}/${m.value2} mmHg`
            : `${m.value1} ${TYPE_UNIT[m.type] || ""}`;
        return `<tr><td>${ts}</td><td>${TYPE_LABEL[m.type] || m.type}</td><td><b>${val}</b></td><td class="muted">${m.raw_text || ""}</td></tr>`;
      })
      .join("");

    document.getElementById("pdfBtn").href = `/report.pdf?patient_id=${pid}&days=${days}`;
  } catch (e) {
    showLoadError(e);
  }
}

makeChart("chartSugar", "Şeker", "#ef4444");
makeChart("chartBp", "Sistolik", "#3b82f6", {
  label: "Diyastolik",
  data: [],
  borderColor: "#06b6d4",
  backgroundColor: "#06b6d433",
  tension: 0.25,
  pointRadius: 3,
});
makeChart("chartPulse", "Nabız", "#22c55e");
makeChart("chartWeight", "Kilo", "#a855f7");

document.getElementById("loadBtn").addEventListener("click", load);
load();
