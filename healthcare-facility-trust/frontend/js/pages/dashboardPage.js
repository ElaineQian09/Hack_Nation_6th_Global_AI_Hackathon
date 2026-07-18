import {
  getFacility,
  getFilters,
  getHealth,
  getSummary,
  saveReview,
  searchFacilities,
} from "../services/apiService.js";
import { renderFacilityCard } from "../components/facilityCard.js";
import { escapeHtml } from "../utils/html.js";

const filterForm = document.querySelector("#filter-form");
const capabilityFilter = document.querySelector("#capability-filter");
const stateFilter = document.querySelector("#state-filter");
const cityFilter = document.querySelector("#city-filter");
const refreshButton = document.querySelector("#refresh-button");
const summaryGrid = document.querySelector("#summary-grid");
const facilityList = document.querySelector("#facility-list");
const facilityDetail = document.querySelector("#facility-detail");
const resultCount = document.querySelector("#result-count");
const selectedStatus = document.querySelector("#selected-status");
const apiHealth = document.querySelector("#api-health");

const appState = {
  filters: null,
  results: [],
  totalFacilities: 0,
  selectedFacilityId: null,
};

async function initializeDashboard() {
  try {
    const [health, filters] = await Promise.all([getHealth(), getFilters()]);
    apiHealth.textContent = health;
    apiHealth.classList.add("ready");
    appState.filters = filters;
    renderFilterOptions(filters);
    await loadFacilities();
  } catch (error) {
    renderError(error.message);
  }
}

function currentFilters() {
  return {
    capability: capabilityFilter.value || "ICU",
    state: stateFilter.value,
    city: cityFilter.value,
  };
}

function renderFilterOptions(filters) {
  capabilityFilter.innerHTML = renderOptions(null, filters.capabilities);
  stateFilter.innerHTML = renderOptions("All states", filters.states);
  cityFilter.innerHTML = renderOptions("All cities", filters.cities);
}

function renderOptions(defaultLabel, values) {
  return [
    defaultLabel ? `<option value="">${escapeHtml(defaultLabel)}</option>` : "",
    ...values.map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`),
  ].join("");
}

function renderSummary(summary) {
  appState.totalFacilities = summary.facility_count;
  summaryGrid.innerHTML = `
    ${renderSummaryCard("Facilities", summary.facility_count)}
    ${renderSummaryCard("Trusted", summary.trust_buckets.Trusted)}
    ${renderSummaryCard("Mixed", summary.trust_buckets.Mixed)}
    ${renderSummaryCard("Warnings", summary.warning_count)}
    ${renderSummaryCard("Sparse Signals", summary.missing_signal_count)}
  `;
}

function renderSummaryCard(label, value) {
  return `
    <article class="summary-card">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
    </article>
  `;
}

async function loadFacilities() {
  facilityList.innerHTML = `<div class="empty-state">Loading ranked facilities...</div>`;
  facilityDetail.innerHTML = `<div class="empty-state">Loading evidence...</div>`;

  const filters = currentFilters();
  const [searchResponse, summaryResponse] = await Promise.all([
    searchFacilities(filters),
    getSummary(filters),
  ]);

  appState.results = searchResponse.results;
  appState.selectedFacilityId = appState.results[0]?.facility_id ?? null;
  renderSummary(summaryResponse);
  renderFacilities();

  if (appState.selectedFacilityId) {
    await selectFacility(appState.selectedFacilityId);
  } else {
    facilityDetail.innerHTML = `<div class="empty-state">No facility selected.</div>`;
    selectedStatus.textContent = "No result selected.";
  }
}

function renderFacilities() {
  resultCount.textContent = `Showing top ${appState.results.length} of ${appState.totalFacilities} facilities, ranked by ${currentFilters().capability} trust score`;
  facilityList.innerHTML = appState.results.length
    ? appState.results
        .map((facility, index) => renderFacilityCard(facility, appState.selectedFacilityId, index))
        .join("")
    : `<div class="empty-state">No facilities match the selected filters.</div>`;

  document.querySelectorAll("[data-facility-id]").forEach((button) => {
    button.addEventListener("click", () => selectFacility(button.dataset.facilityId));
  });
}

async function selectFacility(facilityId) {
  appState.selectedFacilityId = facilityId;
  renderFacilities();
  facilityDetail.innerHTML = `<div class="empty-state">Loading evidence...</div>`;

  const detail = await getFacility(facilityId, {
    capability: currentFilters().capability,
  });
  renderFacilityDetail(detail);
}

function renderFacilityDetail(payload) {
  const { assessment, facility, reviews } = payload;
  selectedStatus.textContent = `${assessment.selected_capability} assessment`;

  facilityDetail.innerHTML = `
    <div class="detail-grid">
      <article class="mini-card">
        <span>Trust</span>
        <strong>${escapeHtml(assessment.trust_score)} / 100</strong>
        <em class="tag trust-${assessment.trust_label.toLowerCase()}">${escapeHtml(assessment.trust_label)}</em>
      </article>
      <article class="mini-card">
        <span>Confidence</span>
        <strong>${escapeHtml(assessment.confidence_level)}</strong>
        <em>Claim present: ${assessment.claim_present ? "Yes" : "No"}</em>
      </article>
      <article class="mini-card">
        <span>Operating Context</span>
        <strong>${escapeHtml(assessment.capacity ?? "Unknown")} beds</strong>
        <em>${escapeHtml(assessment.number_doctors ?? "Unknown")} doctors</em>
      </article>
    </div>

    <section class="evidence-section">
      <span class="section-kicker">Assessment</span>
      <h3>${escapeHtml(assessment.facility_name)}</h3>
      <p>${escapeHtml(assessment.reason_summary)}</p>
      <div class="facility-meta">
        <span>${escapeHtml(facility.facilityTypeId)}</span>
        <span>${escapeHtml(assessment.city)}, ${escapeHtml(assessment.state)}</span>
        <span>${escapeHtml(facility.officialWebsite || "No website")}</span>
      </div>
    </section>

    ${renderEvidenceSection("Evidence Receipts", assessment.evidence_snippets)}
    ${renderSignalSection("Warnings", assessment.warning_signals, "No warning signals found.")}
    ${renderSignalSection("Missing Context", assessment.missing_signals, "No critical context gaps found.")}
    ${renderReviewForm()}
    ${renderSavedReviews(reviews)}
  `;

  document.querySelector("#review-form").addEventListener("submit", handleSaveReview);
}

function renderEvidenceSection(title, evidence) {
  return `
    <section class="evidence-section">
      <span class="section-kicker">Receipts</span>
      <h3>${escapeHtml(title)}</h3>
      ${
        evidence.length
          ? evidence
              .map(
                (item) => `
                  <article class="evidence-item">
                    <span class="source">${escapeHtml(item.source_field)} - ${escapeHtml(item.signal_strength)}</span>
                    <p>${escapeHtml(item.snippet_text)}</p>
                    <em>${escapeHtml(item.explanation)}</em>
                  </article>
                `
              )
              .join("")
          : `<p class="empty-state">No matching evidence snippets found.</p>`
      }
    </section>
  `;
}

function renderSignalSection(title, signals, emptyText) {
  return `
    <section class="evidence-section">
      <span class="section-kicker">Review Signals</span>
      <h3>${escapeHtml(title)}</h3>
      ${
        signals.length
          ? signals.map((signal) => `<article class="signal-item">${escapeHtml(signal)}</article>`).join("")
          : `<p class="empty-state">${escapeHtml(emptyText)}</p>`
      }
    </section>
  `;
}

function renderReviewForm() {
  const decisions = appState.filters?.decisions ?? ["Needs Review"];

  return `
    <section class="evidence-section">
      <span class="section-kicker">Human Override</span>
      <h3>Planner Review</h3>
      <form id="review-form" class="review-form">
        <label>
          Decision
          <select id="review-decision">
            ${decisions
              .map((decision) => `<option value="${escapeHtml(decision)}">${escapeHtml(decision)}</option>`)
              .join("")}
          </select>
        </label>
        <label>
          Note
          <textarea id="review-note" placeholder="Add a short review note"></textarea>
        </label>
        <button type="submit">Save Review</button>
        <p id="review-result" class="empty-state"></p>
      </form>
    </section>
  `;
}

function renderSavedReviews(reviews) {
  return `
    <section class="evidence-section">
      <span class="section-kicker">Memory</span>
      <h3>Saved Reviews</h3>
      ${
        reviews.length
          ? reviews
              .map(
                (review) => `
                  <article class="review-item">
                    <strong>${escapeHtml(review.decision)}</strong>
                    <p>${escapeHtml(review.note)}</p>
                    <em>${escapeHtml(review.createdAt)}</em>
                  </article>
                `
              )
              .join("")
          : `<p class="empty-state">No saved reviews for this facility and capability.</p>`
      }
    </section>
  `;
}

async function handleSaveReview(event) {
  event.preventDefault();
  const result = document.querySelector("#review-result");
  result.textContent = "Saving review...";

  try {
    await saveReview({
      facilityId: appState.selectedFacilityId,
      capability: currentFilters().capability,
      decision: document.querySelector("#review-decision").value,
      note: document.querySelector("#review-note").value.trim(),
    });
    result.textContent = "Saved.";
    await selectFacility(appState.selectedFacilityId);
  } catch (error) {
    result.textContent = error.message;
  }
}

function renderError(message) {
  facilityList.innerHTML = `<div class="error-state">${escapeHtml(message)}</div>`;
  facilityDetail.innerHTML = `<div class="error-state">${escapeHtml(message)}</div>`;
}

filterForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await loadFacilities();
  } catch (error) {
    renderError(error.message);
  }
});

[capabilityFilter, stateFilter, cityFilter].forEach((filter) => {
  filter.addEventListener("change", async () => {
    try {
      await loadFacilities();
    } catch (error) {
      renderError(error.message);
    }
  });
});

refreshButton.addEventListener("click", async () => {
  try {
    await loadFacilities();
  } catch (error) {
    renderError(error.message);
  }
});

initializeDashboard();
