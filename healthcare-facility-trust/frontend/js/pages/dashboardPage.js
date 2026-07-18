import {
  getFilters,
  getSummary,
  searchFacilities,
} from "../services/apiService.js";
import { renderFacilityCard } from "../components/facilityCard.js";

const filterForm = document.querySelector("#filter-form");
const capabilityFilter = document.querySelector("#capability-filter");
const stateFilter = document.querySelector("#state-filter");
const refreshButton = document.querySelector("#refresh-button");
const summaryGrid = document.querySelector("#summary-grid");
const facilityList = document.querySelector("#facility-list");

async function initializeDashboard() {
  try {
    const [filters, summary] = await Promise.all([getFilters(), getSummary()]);
    renderFilterOptions(filters);
    renderSummary(summary);
    await loadFacilities();
  } catch (error) {
    renderError(error.message);
  }
}

function renderFilterOptions(filters) {
  capabilityFilter.innerHTML = renderOptions("All capabilities", filters.capabilities);
  stateFilter.innerHTML = renderOptions("All states", filters.states);
}

function renderOptions(defaultLabel, values) {
  return [
    `<option value="">${defaultLabel}</option>`,
    ...values.map((value) => `<option value="${value}">${value}</option>`),
  ].join("");
}

function renderSummary(summary) {
  summaryGrid.innerHTML = `
    ${renderSummaryCard("Candidates", summary.candidateCount)}
    ${renderSummaryCard("High Trust", summary.highTrustCount)}
    ${renderSummaryCard("Medium Trust", summary.mediumTrustCount)}
    ${renderSummaryCard("Low Trust", summary.lowTrustCount)}
    ${renderSummaryCard("Quality Flags", summary.dataQualityFlagCount)}
  `;
}

function renderSummaryCard(label, value) {
  return `
    <article class="summary-card">
      <span>${label}</span>
      <strong>${value}</strong>
    </article>
  `;
}

async function loadFacilities() {
  facilityList.innerHTML = `<div class="empty-state">Loading facilities...</div>`;

  const facilities = await searchFacilities({
    capability: capabilityFilter.value,
    state: stateFilter.value,
  });

  facilityList.innerHTML = facilities.length
    ? facilities.map(renderFacilityCard).join("")
    : `<div class="empty-state">No facilities match the selected filters.</div>`;
}

function renderError(message) {
  facilityList.innerHTML = `<div class="error-state">${message}</div>`;
}

filterForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await loadFacilities();
  } catch (error) {
    renderError(error.message);
  }
});

refreshButton.addEventListener("click", async () => {
  try {
    await loadFacilities();
  } catch (error) {
    renderError(error.message);
  }
});

initializeDashboard();
