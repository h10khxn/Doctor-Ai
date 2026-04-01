function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}

async function sendPrediction(payload) {
  const resultsDiv = document.getElementById("results");
  resultsDiv.hidden = false;
  resultsDiv.innerHTML = `
    <div class="loading-spinner">
      <div class="spinner"></div>
      <p style="margin-top:0.75rem">Analyzing symptoms...</p>
    </div>`;

  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok || data.error) {
      resultsDiv.innerHTML = `<div class="alert alert-danger">${escapeHtml(data.error || "Something went wrong.")}</div>`;
      return;
    }
    renderResults(data, resultsDiv);
  } catch {
    resultsDiv.innerHTML = `<div class="alert alert-danger">Network error. Please try again.</div>`;
  }
}

function renderResults(data, container) {
  const modeLabel = data.image_label
    ? ` &nbsp;<span class="badge badge-info">Camera: ${escapeHtml(data.image_label)} ${data.image_confidence}%</span>`
    : "";

  let html = `
    <div class="matched-symptoms animate-fade-in">
      Symptoms: <strong>${escapeHtml(data.matched_symptoms)}</strong>${modeLabel}
    </div>
    <div class="results-list stagger">`;

  data.results.forEach((r, i) => {
    const isTop = i === 0;
    html += `
      <article class="result-card ${isTop ? "result-card--top" : ""}" aria-label="${escapeHtml(r.disease)} prediction">
        <div class="result-card-stripe"></div>
        <div class="result-card-body">
          <div class="result-header">
            <h3 class="disease-name">${isTop ? "&#x1F4CB; " : ""}${escapeHtml(r.disease)}</h3>
            <span class="confidence-badge">${r.confidence}%</span>
          </div>
          <div class="confidence-bar" role="progressbar" aria-valuenow="${r.confidence}" aria-valuemin="0" aria-valuemax="100">
            <div class="confidence-fill" style="width:${r.confidence}%"></div>
          </div>
          ${r.description ? `<p class="description">${escapeHtml(r.description)}</p>` : ""}
          ${r.precautions.length ? `
            <div class="precautions">
              <h4>Precautions</h4>
              <ul>${r.precautions.map(p => `<li>${escapeHtml(p)}</li>`).join("")}</ul>
            </div>` : ""}
        </div>
      </article>`;
  });

  html += `</div>`;
  container.innerHTML = html;
}

// Checkbox tab
function submitCheckbox() {
  const checked = [...document.querySelectorAll("#symptom-grid input:checked")].map(c => c.value);
  if (!checked.length) return;
  sendPrediction({ mode: "checkbox", symptoms: checked });
}

// NLP tab
function submitNLP() {
  const text = document.getElementById("nlp-input").value.trim();
  if (!text) return;
  sendPrediction({ mode: "nlp", text });
}

function filterSymptoms(query) {
  document.querySelectorAll(".symptom-item").forEach(item => {
    item.classList.toggle("hidden", !item.dataset.label.includes(query.toLowerCase()));
  });
}

function updateCount() {
  const n = document.querySelectorAll("#symptom-grid input:checked").length;
  const el = document.getElementById("selected-count");
  if (el) el.textContent = `${n} symptom${n !== 1 ? "s" : ""} selected`;
}
