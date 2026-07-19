import {
  generateAiSummary,
  getConfig,
  getFacility,
  getFacilityMap,
  getFilters,
  getSummary,
  saveReview,
  searchFacilities,
} from "../services/apiService.js";
import { renderFacilityCard } from "../components/facilityCard.js";
import { escapeHtml } from "../utils/html.js";

const filterForm = document.querySelector("#filter-form");
const capabilityFilter = document.querySelector("#capability-filter");
const capabilityCards = document.querySelectorAll(".capability-card");
const stateFilter = document.querySelector("#state-filter");
const cityFilter = document.querySelector("#city-filter");
const stateCombobox = document.querySelector('[data-combobox="state"]');
const cityCombobox = document.querySelector('[data-combobox="city"]');
const stateComboboxInput = document.querySelector("#state-combobox-input");
const cityComboboxInput = document.querySelector("#city-combobox-input");
const stateComboboxMenu = document.querySelector("#state-combobox-list");
const cityComboboxMenu = document.querySelector("#city-combobox-list");
const stateComboboxToggle = stateCombobox?.querySelector(".combobox-toggle");
const cityComboboxToggle = cityCombobox?.querySelector(".combobox-toggle");
const refreshButton = document.querySelector("#refresh-button");
const summaryGrid = document.querySelector("#summary-grid");
const facilityList = document.querySelector("#facility-list");
const facilityDetail = document.querySelector("#facility-detail");
const detailScroll = document.querySelector(".detail-scroll");
const resultCount = document.querySelector("#result-count");
const selectedStatus = document.querySelector("#selected-status");
const facilityNameSearch = document.querySelector("#facility-name-search");
const sortBySelect = document.querySelector("#sort-by");
const sortOrderSelect = document.querySelector("#sort-order");
const previousPageButton = document.querySelector("#previous-page-button");
const nextPageButton = document.querySelector("#next-page-button");
const pageStatus = document.querySelector("#page-status");
const paginationLoading = document.querySelector("#pagination-loading");
const searchButton = filterForm.querySelector('button[type="submit"]');

let activeMap = null;

const appState = {
  filters: null,
  allResults: [],
  totalFacilities: 0,
  selectedFacilityId: null,
  currentPage: 1,
  pageSize: 10,
  backendBatchSize: 20,
  nextOffset: 0,
  totalMatching: 0,
  hasMore: false,
  nameQuery: "",
  sortBy: "trust_score",
  sortOrder: "desc",
  mapboxToken: window.MAPBOX_TOKEN || "",
  selectedState: "",
  selectedCity: "",
  stateQuery: "",
  cityQuery: "",
  openCombobox: null,
  highlightedComboboxIndex: {
    state: 0,
    city: 0,
  },
  isLoadingList: false,
  isLoadingNextBatch: false,
};

async function initializeDashboard() {
  try {
    const [config, filters] = await Promise.all([
      loadPublicConfig(),
      getFilters(),
    ]);
    appState.mapboxToken = config.mapboxToken || window.MAPBOX_TOKEN || "";
    appState.filters = filters;
    renderFilterOptions(filters);
    await loadFacilities();
  } catch (error) {
    renderError(error.message);
  }
}

async function loadPublicConfig() {
  try {
    return await getConfig();
  } catch (error) {
    return { mapboxToken: "" };
  }
}

function currentFilters() {
  return {
    capability: capabilityFilter.value || "ICU",
    state: stateFilter.value,
    city: stateFilter.value ? cityFilter.value : "",
  };
}

function renderFilterOptions(filters) {
  const defaultCapability =
    filters.capabilities?.find((capability) => {
      const value = typeof capability === "object" ? capability.value : capability;
      return value === "ICU";
    }) ?? "ICU";
  capabilityFilter.value =
    typeof defaultCapability === "object" ? defaultCapability.value : defaultCapability;
  appState.selectedState = stateFilter.value || "";
  appState.selectedCity = cityFilter.value || "";
  updateHiddenFilterValues();
  updateCapabilityCards();
  renderCityOptions();
  syncComboboxDisplay("state");
  syncComboboxDisplay("city");
  renderComboboxOptions("state");
  renderComboboxOptions("city");
}

function renderOptions(defaultLabel, values) {
  return [
    defaultLabel ? `<option value="">${escapeHtml(defaultLabel)}</option>` : "",
    ...values.map((option) => {
      const value = typeof option === "object" ? option.value : option;
      const label = typeof option === "object" ? option.label : option;
      return `<option value="${escapeHtml(value)}">${escapeHtml(label)}</option>`;
    }),
  ].join("");
}

function renderSummary(summary) {
  appState.totalFacilities = summary.facility_count;
  summaryGrid.innerHTML = `
    ${renderSummaryCard("Matching Facilities", summary.facility_count, "Facilities matching this scope")}
    ${renderSummaryCard("Trusted Facilities", summary.trust_buckets.Trusted, "Strong evidence-backed records")}
    ${renderSummaryCard("Mixed Facilities", summary.trust_buckets.Mixed, "Some support, but gaps remain")}
    ${renderSummaryCard("Warning Signals", summary.warning_count, "Review warnings found")}
    ${renderSummaryCard("Missing Evidence Signals", summary.missing_signal_count, "Missing context signals")}
  `;
}

function renderSummaryCard(label, value, description) {
  return `
    <article class="summary-card">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
      <p>${escapeHtml(description)}</p>
    </article>
  `;
}

async function loadFacilities() {
  appState.isLoadingList = true;
  appState.isLoadingNextBatch = false;
  appState.allResults = [];
  appState.currentPage = 1;
  appState.nextOffset = 0;
  appState.totalMatching = 0;
  appState.hasMore = false;
  renderListLoading();
  renderDetailLoading();

  const filters = currentFilters();
  const [searchResponse, summaryResponse] = await Promise.all([
    searchFacilities({
      ...filters,
      name: appState.nameQuery,
      sortBy: appState.sortBy,
      sortOrder: appState.sortOrder,
      offset: 0,
      limit: appState.backendBatchSize,
    }),
    getSummary(filters),
  ]);

  appState.allResults = searchResponse.results ?? [];
  appState.totalMatching = searchResponse.total ?? appState.allResults.length;
  appState.nextOffset = searchResponse.nextOffset ?? appState.allResults.length;
  appState.hasMore = Boolean(searchResponse.hasMore);
  appState.isLoadingList = false;
  setSearchControlsLoading(false);
  renderSummary(summaryResponse);
  renderCityOptions();
  appState.selectedFacilityId = appState.allResults[0]?.facility_id ?? null;
  renderFacilities();

  if (appState.selectedFacilityId) {
    await selectFacility(appState.selectedFacilityId);
  } else {
    facilityDetail.innerHTML = `<div class="empty-state">No facility selected.</div>`;
    selectedStatus.textContent = "No result selected.";
  }
}

function renderFacilities() {
  const total = appState.totalMatching || appState.allResults.length;
  const start = (appState.currentPage - 1) * appState.pageSize;
  const end = start + appState.pageSize;
  const visibleItems = appState.allResults.slice(start, end);

  resultCount.textContent = total
    ? `Showing ${start + 1}-${Math.min(end, total)} of ${total.toLocaleString()} matching facilities`
    : "No matches found";

  facilityList.innerHTML = visibleItems.length
    ? visibleItems
        .map((facility, index) =>
          renderFacilityCard(
            facility,
            appState.selectedFacilityId,
            start + index
          )
        )
        .join("")
    : `<div class="empty-state">No facilities match the selected filters.</div>`;

  document.querySelectorAll("[data-facility-id]").forEach((button) => {
    button.addEventListener("click", () => selectFacility(button.dataset.facilityId));
  });

  renderPaginationControls();
}

async function selectFacility(facilityId) {
  appState.selectedFacilityId = facilityId;
  renderFacilities();
  removeActiveMap();
  renderDetailLoading();

  const detail = await getFacility(facilityId, {
    capability: currentFilters().capability,
  });
  renderFacilityDetail(detail);
  resetDetailScroll();
  await loadFacilityMap(facilityId);
}

function renderFacilityDetail(payload) {
  const { assessment, facility, reviews } = payload;
  const pincode = facility.address_zipOrPostcode ?? facility.pin_code ?? "Not listed";
  const website = facility.officialWebsite ?? facility.official_website ?? "";
  const facilityType = facility.facilityTypeId ?? facility.facility_type ?? "Facility";
  selectedStatus.textContent = `${assessment.selected_capability} assessment`;

  facilityDetail.innerHTML = `
    <section class="evidence-section">
      <span class="section-kicker">Assessment</span>
      <h3>${escapeHtml(assessment.facility_name)}</h3>
      <p>${escapeHtml(assessment.reason_summary)}</p>
      <div class="facility-meta">
        <span>${escapeHtml(facilityType)}</span>
        <span>${escapeHtml(assessment.city)}, ${escapeHtml(assessment.state)}</span>
        <span>${escapeHtml(website || "No website listed")}</span>
      </div>
    </section>

    <section class="clinic-info-grid" aria-label="Facility review summary">
      <article class="clinic-info-column">
        <span class="section-kicker">Location</span>
        <h3>${escapeHtml(assessment.city)}, ${escapeHtml(assessment.state)}</h3>
        <p>${escapeHtml(facilityType)}</p>
        <p>Pincode: ${escapeHtml(pincode)}</p>
      </article>
      <article class="clinic-info-column">
        <span class="section-kicker">Evidence Summary</span>
        <h3>${escapeHtml(assessment.trust_score)} / 100</h3>
        <p><span class="tag trust-${assessment.trust_label.toLowerCase()}">${escapeHtml(assessment.trust_label)}</span></p>
        <p>Confidence: ${escapeHtml(assessment.confidence_level)}</p>
        <p>Claim present: ${assessment.claim_present ? "Yes" : "No"}</p>
      </article>
      <article class="clinic-info-column">
        <span class="section-kicker">Source / Context</span>
        <h3>${escapeHtml(assessment.capacity ?? "Unknown")} beds</h3>
        <p>${escapeHtml(assessment.number_doctors ?? "Unknown")} doctors</p>
        <p>${website ? "Website/source available" : "No website listed"}</p>
      </article>
    </section>

    ${renderFacilityLocationSection()}
    ${renderAiSummarySection()}
    ${renderEvidenceSection("Evidence Receipts", assessment.evidence_snippets)}
    ${renderSignalSection("Warnings", assessment.warning_signals, "No warning signals found.")}
    ${renderSignalSection("Missing Context", assessment.missing_signals, "No critical context gaps found.")}
    ${renderReviewForm()}
    ${renderSavedReviews(reviews)}
  `;

  document.querySelector("#review-form").addEventListener("submit", handleSaveReview);
  document.querySelector("#generate-ai-summary-button")?.addEventListener("click", handleGenerateAiSummary);
}

function renderFacilityLocationSection() {
  return `
    <section class="evidence-section map-card">
      <span class="section-kicker">Location</span>
      <h3>Facility Location</h3>
      <div id="facility-map-content">
        <p class="empty-state">Loading location...</p>
      </div>
    </section>
  `;
}

function renderAiSummarySection() {
  return `
    <section class="evidence-section ai-summary-section">
      <span class="section-kicker">Databricks AI</span>
      <h3>AI Evidence Summary</h3>
      <p class="ai-summary-copy">
        Generate a short evidence-grounded summary for this facility and selected capability.
      </p>
      <button id="generate-ai-summary-button" type="button" class="secondary-button ai-summary-button">
        Generate AI Summary
      </button>
      <div id="ai-summary-result" class="ai-summary-result" aria-live="polite"></div>
    </section>
  `;
}

async function loadFacilityMap(facilityId) {
  const container = document.querySelector("#facility-map-content");
  if (!container) {
    return;
  }

  try {
    const mapPayload = await getFacilityMap(facilityId);
    if (appState.selectedFacilityId !== facilityId) {
      return;
    }
    renderFacilityMap(mapPayload);
  } catch (error) {
    if (appState.selectedFacilityId !== facilityId) {
      return;
    }
    container.innerHTML = `<p class="empty-state">No reliable map location available.</p>`;
  }
}

function renderFacilityMap(mapPayload) {
  removeActiveMap();
  const container = document.querySelector("#facility-map-content");
  if (!container) {
    return;
  }

  if (mapPayload.latitude === null || mapPayload.longitude === null) {
    container.innerHTML = `
      <p class="empty-state">No reliable map location available.</p>
      ${mapPayload.warning ? `<p class="map-warning">${escapeHtml(mapPayload.warning)}</p>` : ""}
    `;
    return;
  }

  const safeMapId = String(mapPayload.facilityId).replace(/[^a-zA-Z0-9_-]/g, "-");
  const mapId = `facility-map-${safeMapId}`;
  const sourceLabel = mapPayload.source === "existing_coordinates"
    ? "existing coordinates"
    : "Mapbox geocoded";

  container.innerHTML = `
    <div id="${mapId}" class="facility-map" role="img" aria-label="Map for ${escapeHtml(mapPayload.name)}"></div>
    <p class="map-meta">
      Location source: ${escapeHtml(sourceLabel)}
      ${mapPayload.placeName ? ` · ${escapeHtml(mapPayload.placeName)}` : ""}
    </p>
    ${mapPayload.warning ? `<p class="map-warning">${escapeHtml(mapPayload.warning)}</p>` : ""}
  `;

  if (!appState.mapboxToken || !window.mapboxgl) {
    container.querySelector(".facility-map").innerHTML = `
      <div class="map-token-empty">Map is unavailable because Mapbox public token is not configured.</div>
    `;
    return;
  }

  try {
    // Mapbox GL JS expects [longitude, latitude], not [latitude, longitude].
    const center = [mapPayload.longitude, mapPayload.latitude];
    activeMap = new mapboxgl.Map({
      accessToken: appState.mapboxToken,
      container: mapId,
      style: "mapbox://styles/mapbox/streets-v12",
      center,
      zoom: 13,
    });

    activeMap.addControl(new mapboxgl.NavigationControl({ showCompass: false }), "top-right");
    activeMap.scrollZoom.disable();

    const popup = new mapboxgl.Popup({
      closeButton: true,
      closeOnClick: false,
      offset: 26,
    }).setHTML(renderMapPopupHtml(mapPayload));

    new mapboxgl.Marker({ color: "#145a4a" })
      .setLngLat(center)
      .setPopup(popup)
      .addTo(activeMap);
  } catch (error) {
    container.querySelector(".facility-map").innerHTML = `
      <div class="map-token-empty">Map preview is unavailable in this browser.</div>
    `;
  }
}

function renderMapPopupHtml(mapPayload) {
  const googleMapsUrl = buildGoogleMapsUrl(mapPayload);

  return `
    <div class="map-popup">
      <strong>${escapeHtml(mapPayload.name)}</strong>
      ${
        googleMapsUrl
          ? `
            <button
              type="button"
              class="google-map-link"
              data-google-map-url="${escapeHtml(googleMapsUrl)}"
            >
              Open in Google Maps
            </button>
          `
          : ""
      }
    </div>
  `;
}

function buildGoogleMapsUrl(mapPayload) {
  if (mapPayload.latitude !== null && mapPayload.longitude !== null) {
    const query = `${mapPayload.latitude},${mapPayload.longitude}`;
    return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`;
  }

  const query = [mapPayload.name, mapPayload.address, mapPayload.placeName]
    .filter(Boolean)
    .join(", ");

  if (!query) {
    return "";
  }

  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`;
}

function removeActiveMap() {
  if (activeMap) {
    activeMap.remove();
    activeMap = null;
  }
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

function renderCityOptions() {
  if (!appState.selectedState) {
    appState.selectedCity = "";
    appState.cityQuery = "";
    updateHiddenFilterValues();
    updateCityDisabledState();
    syncComboboxDisplay("city");
    renderComboboxOptions("city");
    return;
  }

  const cities = getCitiesForState(appState.selectedState);
  if (appState.selectedCity && !cities.includes(appState.selectedCity)) {
    appState.selectedCity = "";
  }

  updateHiddenFilterValues();
  updateCityDisabledState();
  syncComboboxDisplay("city");
  renderComboboxOptions("city");
}

function getCitiesForState(state) {
  if (appState.filters?.citiesByState?.[state]) {
    return appState.filters.citiesByState[state];
  }

  if (appState.filters?.citiesByState && Array.isArray(appState.filters.citiesByState)) {
    return appState.filters.citiesByState
      .filter((item) => item.state === state)
      .map((item) => item.city);
  }

  const resultCities = appState.allResults
    .filter((facility) => facility.state === state)
    .map((facility) => facility.city)
    .filter(Boolean);

  if (resultCities.length) {
    return uniqueSorted(resultCities);
  }

  if (appState.filters?.cities?.length) {
    return appState.filters.cities;
  }

  return [];
}

function getStateOptions() {
  return [
    { value: "", label: "All states" },
    ...(appState.filters?.states ?? []).map((state) => ({
      value: typeof state === "object" ? state.value : state,
      label: typeof state === "object" ? state.label : state,
    })),
  ];
}

function getCityOptions() {
  if (!appState.selectedState) {
    return [];
  }

  return [
    { value: "", label: "All cities" },
    ...getCitiesForState(appState.selectedState).map((city) => ({
      value: city,
      label: city,
    })),
  ];
}

function getComboboxElements(type) {
  return type === "state"
    ? {
        root: stateCombobox,
        input: stateComboboxInput,
        menu: stateComboboxMenu,
        toggle: stateComboboxToggle,
      }
    : {
        root: cityCombobox,
        input: cityComboboxInput,
        menu: cityComboboxMenu,
        toggle: cityComboboxToggle,
      };
}

function getComboboxOptions(type) {
  return type === "state" ? getStateOptions() : getCityOptions();
}

function getFilteredComboboxOptions(type) {
  const query = (type === "state" ? appState.stateQuery : appState.cityQuery)
    .trim()
    .toLowerCase();
  const options = getComboboxOptions(type);

  if (!query) {
    return options;
  }

  return options.filter((option) => option.label.toLowerCase().includes(query));
}

function renderComboboxOptions(type) {
  const { menu } = getComboboxElements(type);
  if (!menu) {
    return;
  }

  const options = getFilteredComboboxOptions(type);
  const selectedValue = type === "state" ? appState.selectedState : appState.selectedCity;
  const highlightedIndex = Math.min(
    appState.highlightedComboboxIndex[type],
    Math.max(options.length - 1, 0)
  );
  appState.highlightedComboboxIndex[type] = highlightedIndex;

  menu.innerHTML = options.length
    ? options
        .map((option, index) => {
          const isSelected = option.value === selectedValue;
          const isActive = index === highlightedIndex;
          return `
            <button
              type="button"
              class="combobox-option ${isSelected ? "selected" : ""} ${isActive ? "active" : ""}"
              role="option"
              aria-selected="${isSelected}"
              data-combobox-value="${escapeHtml(option.value)}"
              data-combobox-label="${escapeHtml(option.label)}"
            >
              <span>${escapeHtml(option.label)}</span>
              ${isSelected ? `<span class="combobox-check" aria-hidden="true">✓</span>` : ""}
            </button>
          `;
        })
        .join("")
    : `<div class="combobox-empty">No matching options</div>`;

  menu.querySelectorAll(".combobox-option").forEach((option) => {
    option.addEventListener("click", () => {
      selectComboboxOption(type, option.dataset.comboboxValue, option.dataset.comboboxLabel);
    });
  });
}

function openCombobox(type) {
  if (type === "city" && !appState.selectedState) {
    return;
  }

  closeAllComboboxes(type);

  const { root, input, menu } = getComboboxElements(type);
  if (!root || !input || !menu) {
    return;
  }

  appState.openCombobox = type;
  appState.highlightedComboboxIndex[type] = 0;
  root.classList.add("open");
  root.querySelector(".combobox-shell")?.setAttribute("aria-expanded", "true");
  menu.hidden = false;
  renderComboboxOptions(type);
  input.focus();
}

function closeCombobox(type) {
  const { root, menu } = getComboboxElements(type);
  if (!root || !menu) {
    return;
  }

  root.classList.remove("open");
  root.querySelector(".combobox-shell")?.setAttribute("aria-expanded", "false");
  menu.hidden = true;

  if (appState.openCombobox === type) {
    appState.openCombobox = null;
  }

  syncComboboxDisplay(type);
}

function closeAllComboboxes(exceptType = null) {
  ["state", "city"].forEach((type) => {
    if (type !== exceptType) {
      closeCombobox(type);
    }
  });
}

function selectComboboxOption(type, value, label) {
  if (type === "state") {
    appState.selectedState = value;
    appState.stateQuery = "";
    appState.selectedCity = "";
    appState.cityQuery = "";
    syncComboboxDisplay("state", label);
    syncComboboxDisplay("city");
    updateHiddenFilterValues();
    updateCityDisabledState();
    renderComboboxOptions("city");
    closeCombobox("state");
    stateFilter.dispatchEvent(new Event("change", { bubbles: true }));
    return;
  }

  appState.selectedCity = value;
  appState.cityQuery = "";
  syncComboboxDisplay("city", label);
  updateHiddenFilterValues();
  closeCombobox("city");
  cityFilter.dispatchEvent(new Event("change", { bubbles: true }));
}

function syncComboboxDisplay(type, selectedLabel = null) {
  const { input } = getComboboxElements(type);
  if (!input) {
    return;
  }

  if (type === "state") {
    input.value = appState.selectedState
      ? selectedLabel ?? findOptionLabel(getStateOptions(), appState.selectedState)
      : "";
    input.placeholder = "All states";
    return;
  }

  input.value = appState.selectedCity
    ? selectedLabel ?? findOptionLabel(getCityOptions(), appState.selectedCity)
    : "";
  input.placeholder = appState.selectedState ? "All cities" : "Select a state first";
}

function findOptionLabel(options, value) {
  return options.find((option) => option.value === value)?.label ?? value;
}

function updateHiddenFilterValues() {
  stateFilter.value = appState.selectedState;
  cityFilter.value = appState.selectedCity;
}

function updateCityDisabledState() {
  const isDisabled = !appState.selectedState;
  cityFilter.disabled = isDisabled;
  cityCombobox?.classList.toggle("combobox-disabled", isDisabled);
  cityCombobox?.querySelector(".combobox-shell")?.setAttribute("aria-disabled", String(isDisabled));
  cityComboboxInput.disabled = isDisabled;
  cityComboboxToggle.disabled = isDisabled;
}

function handleComboboxInput(type, value) {
  if (type === "state") {
    appState.stateQuery = value;
  } else {
    appState.cityQuery = value;
  }

  appState.highlightedComboboxIndex[type] = 0;
  openCombobox(type);
  renderComboboxOptions(type);
}

function handleComboboxKeydown(type, event) {
  const options = getFilteredComboboxOptions(type);

  if (event.key === "Escape") {
    closeCombobox(type);
    return;
  }

  if (event.key === "ArrowDown") {
    event.preventDefault();
    openCombobox(type);
    appState.highlightedComboboxIndex[type] = Math.min(
      appState.highlightedComboboxIndex[type] + 1,
      Math.max(options.length - 1, 0)
    );
    renderComboboxOptions(type);
    return;
  }

  if (event.key === "ArrowUp") {
    event.preventDefault();
    appState.highlightedComboboxIndex[type] = Math.max(
      appState.highlightedComboboxIndex[type] - 1,
      0
    );
    renderComboboxOptions(type);
    return;
  }

  if (event.key === "Enter" && appState.openCombobox === type) {
    event.preventDefault();
    const option = options[appState.highlightedComboboxIndex[type]];
    if (option) {
      selectComboboxOption(type, option.value, option.label);
    }
  }
}

function uniqueSorted(values) {
  return [...new Set(values)].sort((a, b) => a.localeCompare(b));
}

function renderPaginationControls() {
  const total = appState.totalMatching || appState.allResults.length;
  const loadedPages = Math.max(1, Math.ceil(appState.allResults.length / appState.pageSize));
  const totalPages = Math.max(1, Math.ceil(total / appState.pageSize));
  const nextPageStart = appState.currentPage * appState.pageSize;
  const canGoPrevious = appState.currentPage > 1;
  const canGoNext = nextPageStart < appState.allResults.length || appState.hasMore;

  previousPageButton.disabled = appState.isLoadingList || appState.isLoadingNextBatch || !canGoPrevious;
  nextPageButton.disabled = appState.isLoadingList || appState.isLoadingNextBatch || !canGoNext;
  pageStatus.textContent = total
    ? `Page ${appState.currentPage} of ${totalPages}`
    : "Page 1";
  pageStatus.title = `Loaded ${loadedPages} page${loadedPages === 1 ? "" : "s"}`;
  paginationLoading.hidden = !appState.isLoadingNextBatch;
}

async function fetchNextResultsBatch() {
  appState.isLoadingNextBatch = true;
  renderPaginationControls();

  try {
    const response = await searchFacilities({
      ...currentFilters(),
      name: appState.nameQuery,
      sortBy: appState.sortBy,
      sortOrder: appState.sortOrder,
      offset: appState.nextOffset,
      limit: appState.backendBatchSize,
    });

    appState.allResults = [...appState.allResults, ...(response.results ?? [])];
    appState.totalMatching = response.total ?? appState.totalMatching;
    appState.nextOffset = response.nextOffset ?? appState.allResults.length;
    appState.hasMore = Boolean(response.hasMore);
  } finally {
    appState.isLoadingNextBatch = false;
    renderPaginationControls();
  }
}

async function goToNextPage() {
  const nextPageStart = appState.currentPage * appState.pageSize;

  if (nextPageStart >= appState.allResults.length) {
    if (!appState.hasMore) {
      return;
    }

    try {
      await fetchNextResultsBatch();
    } catch (error) {
      appState.isLoadingNextBatch = false;
      renderError(error.message);
      return;
    }
  }

  if (nextPageStart < appState.allResults.length) {
    appState.currentPage += 1;
    renderFacilities();
  } else {
    renderPaginationControls();
  }
}

function goToPreviousPage() {
  if (appState.currentPage <= 1) {
    return;
  }

  appState.currentPage -= 1;
  renderFacilities();
}

function updateCapabilityCards() {
  capabilityCards.forEach((card) => {
    const isSelected = card.dataset.capability === capabilityFilter.value;
    card.classList.toggle("active", isSelected);
    card.setAttribute("aria-pressed", String(isSelected));
  });
}

function renderListLoading() {
  resultCount.textContent = "Loading matches...";
  setSearchControlsLoading(true);
  previousPageButton.disabled = true;
  nextPageButton.disabled = true;
  pageStatus.textContent = "Loading results";
  paginationLoading.hidden = true;
  facilityList.innerHTML = `
    ${renderScoringLoading()}
    ${Array.from({ length: 3 })
    .map(
      () => `
        <article class="skeleton-card">
          <div>
            <div class="skeleton-line short"></div>
            <div class="skeleton-line title"></div>
            <div class="skeleton-line"></div>
            <div class="skeleton-line medium"></div>
          </div>
          <div class="skeleton-score"></div>
        </article>
      `
    )
    .join("")}
  `;
}

function renderScoringLoading() {
  return `
    <div class="search-scoring-loading" role="status" aria-live="polite">
      <div class="loading-spinner" aria-hidden="true"></div>
      <div>
        <strong>Scoring all sources in the selected range. This may take a moment.</strong>
        <p>Scoring evidence sources for the selected filters. This may take a moment.</p>
      </div>
    </div>
  `;
}

function setSearchControlsLoading(isLoading) {
  searchButton.disabled = isLoading;
  refreshButton.disabled = isLoading;
  capabilityCards.forEach((card) => {
    card.disabled = isLoading;
  });
  searchButton.textContent = isLoading ? "Scoring..." : "Search Facilities";
}

function renderDetailLoading() {
  removeActiveMap();
  selectedStatus.textContent = "Loading evidence...";
  facilityDetail.innerHTML = `
    <div class="detail-grid">
      <article class="skeleton-card compact"></article>
      <article class="skeleton-card compact"></article>
      <article class="skeleton-card compact"></article>
    </div>
    <section class="evidence-section">
      <div class="skeleton-line title"></div>
      <div class="skeleton-line"></div>
      <div class="skeleton-line medium"></div>
    </section>
  `;
  resetDetailScroll();
}

function resetDetailScroll() {
  const scrollContainer = detailScroll || facilityDetail.parentElement;
  if (!scrollContainer) {
    return;
  }

  requestAnimationFrame(() => {
    scrollContainer.scrollTop = 0;
  });
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

async function handleGenerateAiSummary() {
  const button = document.querySelector("#generate-ai-summary-button");
  const result = document.querySelector("#ai-summary-result");
  if (!button || !result || !appState.selectedFacilityId) {
    return;
  }

  button.disabled = true;
  button.textContent = "Generating...";
  result.classList.remove("error-state");
  result.classList.add("loading");
  result.textContent = "Generating Databricks AI summary...";

  try {
    const payload = await generateAiSummary(appState.selectedFacilityId, {
      capability: currentFilters().capability,
    });
    result.classList.remove("loading");
    result.textContent = payload.summary || "AI summary is unavailable right now.";
  } catch (error) {
    result.classList.remove("loading");
    result.classList.add("error-state");
    result.textContent = "AI summary is unavailable right now.";
  } finally {
    button.disabled = false;
    button.textContent = "Generate AI Summary";
  }
}

function renderError(message) {
  appState.isLoadingList = false;
  appState.isLoadingNextBatch = false;
  setSearchControlsLoading(false);
  facilityList.innerHTML = `<div class="error-state">${escapeHtml(message)}</div>`;
  facilityDetail.innerHTML = `<div class="error-state">${escapeHtml(message)}</div>`;
  renderPaginationControls();
}

async function handleListQueryChange() {
  appState.nameQuery = facilityNameSearch.value;
  appState.sortBy = sortBySelect.value;
  appState.sortOrder = sortOrderSelect.value;

  try {
    await loadFacilities();
  } catch (error) {
    appState.isLoadingList = false;
    renderError(error.message);
  }
}

filterForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await loadFacilities();
  } catch (error) {
    renderError(error.message);
  }
});

capabilityCards.forEach((card) => {
  card.addEventListener("click", async () => {
    capabilityFilter.value = card.dataset.capability;
    updateCapabilityCards();

    try {
      await loadFacilities();
    } catch (error) {
      renderError(error.message);
    }
  });
});

stateFilter.addEventListener("change", async () => {
  appState.selectedState = stateFilter.value;
  appState.selectedCity = "";
  appState.cityQuery = "";
  updateHiddenFilterValues();
  updateCityDisabledState();
  syncComboboxDisplay("state");
  syncComboboxDisplay("city");
  renderComboboxOptions("city");

  try {
    await loadFacilities();
  } catch (error) {
    renderError(error.message);
  }
});

cityFilter.addEventListener("change", async () => {
  appState.selectedCity = cityFilter.value;
  syncComboboxDisplay("city");

  try {
    await loadFacilities();
  } catch (error) {
    renderError(error.message);
  }
});

stateComboboxInput.addEventListener("focus", () => openCombobox("state"));
stateComboboxInput.addEventListener("click", () => openCombobox("state"));
stateComboboxInput.addEventListener("input", (event) =>
  handleComboboxInput("state", event.target.value)
);
stateComboboxInput.addEventListener("keydown", (event) =>
  handleComboboxKeydown("state", event)
);
stateComboboxToggle.addEventListener("click", () => openCombobox("state"));

cityComboboxInput.addEventListener("focus", () => openCombobox("city"));
cityComboboxInput.addEventListener("click", () => openCombobox("city"));
cityComboboxInput.addEventListener("input", (event) =>
  handleComboboxInput("city", event.target.value)
);
cityComboboxInput.addEventListener("keydown", (event) =>
  handleComboboxKeydown("city", event)
);
cityComboboxToggle.addEventListener("click", () => openCombobox("city"));

document.addEventListener("click", (event) => {
  if (!event.target.closest(".custom-combobox")) {
    closeAllComboboxes();
  }
});

document.addEventListener("click", (event) => {
  const googleMapButton = event.target.closest(".google-map-link");
  if (!googleMapButton) {
    return;
  }

  event.preventDefault();
  const url = googleMapButton.dataset.googleMapUrl;
  if (!url) {
    return;
  }

  if (window.confirm("Open this facility in Google Maps?")) {
    window.open(url, "_blank", "noopener,noreferrer");
  }
});

facilityNameSearch.addEventListener("input", handleListQueryChange);
sortBySelect.addEventListener("change", handleListQueryChange);
sortOrderSelect.addEventListener("change", handleListQueryChange);
previousPageButton.addEventListener("click", goToPreviousPage);
nextPageButton.addEventListener("click", goToNextPage);

refreshButton.addEventListener("click", async () => {
  try {
    await loadFacilities();
  } catch (error) {
    renderError(error.message);
  }
});

initializeDashboard();
