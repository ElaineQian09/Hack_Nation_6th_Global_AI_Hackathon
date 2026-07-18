export function renderFacilityCard(facility) {
  const trustClass = `trust-${facility.trustLevel.toLowerCase()}`;
  const capabilityTags = facility.claimedCapabilities
    .map((capability) => `<span class="tag">${capability}</span>`)
    .join("");
  const flags = facility.dataQualityFlags.length
    ? facility.dataQualityFlags.map((flag) => `<span class="flag">${flag}</span>`).join("")
    : `<span class="tag">No active flags</span>`;

  return `
    <article class="facility-card">
      <div>
        <h3>${facility.name}</h3>
        <div class="facility-meta">
          <span>${facility.type}</span>
          <span>${facility.city}, ${facility.state}</span>
          <span>${facility.bedCount ?? "Unknown"} beds</span>
        </div>
        <p>${facility.summary}</p>
        <div class="tag-row">${capabilityTags}</div>
        <div class="flag-list">${flags}</div>
      </div>

      <aside class="score-box">
        <span class="score-number">${facility.trustScore}</span>
        <strong class="${trustClass}">${facility.trustLevel} Trust</strong>
        <a class="button-link" href="./detail.html?id=${facility.id}">Open Detail</a>
      </aside>
    </article>
  `;
}
