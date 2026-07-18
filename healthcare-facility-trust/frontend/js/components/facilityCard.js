import { escapeHtml } from "../utils/html.js";

export function renderFacilityCard(facility, selectedFacilityId, index) {
  const trustClass = `trust-${facility.trust_label.toLowerCase()}`;
  const confidenceClass = `trust-${facility.confidence_level.toLowerCase()}`;
  const activeClass = facility.facility_id === selectedFacilityId ? "active" : "";

  return `
    <button
      type="button"
      class="facility-card selectable ${activeClass}"
      data-facility-id="${escapeHtml(facility.facility_id)}"
    >
      <div>
        <div class="facility-rank">#${index + 1}</div>
        <h3>${escapeHtml(facility.facility_name)}</h3>
        <div class="facility-meta">
          <span>${escapeHtml(facility.city)}, ${escapeHtml(facility.state)}</span>
          <span>${escapeHtml(facility.number_doctors ?? "Unknown")} doctors</span>
          <span>${escapeHtml(facility.capacity ?? "Unknown")} beds</span>
        </div>
        <p>${escapeHtml(facility.reason_summary)}</p>
        <div class="tag-row">
          <span class="tag ${trustClass}">${escapeHtml(facility.trust_label)}</span>
          <span class="tag ${confidenceClass}">${escapeHtml(facility.confidence_level)}</span>
          <span class="tag">${escapeHtml(facility.support_signal_count)} evidence</span>
          <span class="flag">${escapeHtml(facility.warning_signal_count)} warnings</span>
        </div>
      </div>

      <aside class="score-box">
        <span class="score-number">${escapeHtml(facility.trust_score)}</span>
        <strong class="${trustClass}">Trust</strong>
      </aside>
    </button>
  `;
}
