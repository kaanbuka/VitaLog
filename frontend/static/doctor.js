/**
 * Doktor paneli — yer tutucu (ST-3).
 * Bir sonraki adımda /report.json ve /measurements ile doldurulacak.
 */
function showPlaceholder() {
  const kpis = document.getElementById("kpis");
  if (kpis) {
    kpis.innerHTML =
      '<div class="muted">Rapor verisi: API bağlantısı bir sonraki committe eklenecek.</div>';
  }
  const tbody = document.getElementById("all");
  if (tbody) {
    tbody.innerHTML = "";
  }
}

document.getElementById("loadBtn")?.addEventListener("click", showPlaceholder);
showPlaceholder();
