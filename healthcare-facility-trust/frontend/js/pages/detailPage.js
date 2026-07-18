import {
  getDataQuality,
  getFacility,
  saveReview,
} from "../services/apiService.js";

const facilityTitle = document.querySelector("#facility-title");
const facilitySubtitle = document.querySelector("#facility-subtitle");
const detailRoot = document.querySelector("#detail-root");

async function initializeDetailPage() {
  const facilityId = new URLSearchParams(window.location.search).get("id");

  if (!facilityId) {
    renderError("Missing facility id.");
    return;
  }

  try {
    const [facility, dataQuality] = await Promise.all([
      getFacility(facilityId),
      getDataQuality(),
    ]);

    renderFacilityDetail(facility, dataQuality.issues);
  } catch (error) {
    renderError(error.message);
  }
}

function renderFacilityDetail(facility, allIssues) {
  facilityTitle.textContent = facility.name;
  facilitySubtitle.textContent = `${facility.type} · ${facility.address}`;

  const facilityIssues = allIssues.filter((issue) => issue.facilityId === facility.id);

  detailRoot.innerHTML = `
    <div class="detail-main">
      <section class="detail-card">
        <h2>Facility Capabilities</h2>
        <p>Green means mock evidence supports the capability. Red means support is missing.</p>
        <div class="check-list">
          ${facility.facilityChecks.map(renderFacilityCheck).join("")}
        </div>
      </section>

      <section class="detail-card">
        <h2>Data Quality Flags</h2>
        ${
          facilityIssues.length
            ? facilityIssues.map(renderQualityIssue).join("")
            : `<p>No mock data quality issues for this facility.</p>`
        }
      </section>
    </div>

    <aside class="detail-card">
      <div class="score-box">
        <span class="score-number">${facility.trustScore}</span>
        <strong class="trust-${facility.trustLevel.toLowerCase()}">
          ${facility.trustLevel} Trust
        </strong>
      </div>

      <h2>Why this score?</h2>
      <div class="reason-list">
        ${facility.scoreReasons.map(renderScoreReason).join("")}
      </div>

      <h2>Reviewer Action</h2>
      <p>This posts a dummy review body to the backend for wiring only.</p>
      <textarea id="review-note">Demo reviewer note</textarea>
      <button id="save-review-button" type="button">Save Demo Review</button>
      <p id="review-result" class="empty-state"></p>
    </aside>
  `;

  document
    .querySelector("#save-review-button")
    .addEventListener("click", () => handleSaveReview(facility));
}

function renderFacilityCheck(check) {
  const statusClass = check.isPresent ? "present" : "missing";
  const icon = check.isPresent ? "✓" : "!";

  return `
    <article class="check-item ${statusClass}">
      <span class="check-icon">${icon}</span>
      <div>
        <h3>${check.name}</h3>
        <p>${check.evidence}</p>
      </div>
    </article>
  `;
}

function renderQualityIssue(issue) {
  return `
    <article class="reason-item">
      <strong>${issue.issue}</strong>
      <p>Severity: ${issue.severity}</p>
    </article>
  `;
}

function renderScoreReason(reason) {
  return `
    <article class="reason-item">
      <strong>${reason.label}</strong>
      <span class="impact">${reason.impact}</span>
      <p>${reason.description}</p>
    </article>
  `;
}

async function handleSaveReview(facility) {
  const result = document.querySelector("#review-result");
  const note = document.querySelector("#review-note").value;
  result.textContent = "Saving review...";

  try {
    // TODO: Replace this demo payload with a real reviewer form later.
    const response = await saveReview({
      facilityId: facility.id,
      capability: "ICU",
      decision: "needs_review",
      note,
    });

    result.textContent = response.message;
  } catch (error) {
    result.textContent = error.message;
  }
}

function renderError(message) {
  detailRoot.innerHTML = `<div class="error-state">${message}</div>`;
}

initializeDetailPage();
