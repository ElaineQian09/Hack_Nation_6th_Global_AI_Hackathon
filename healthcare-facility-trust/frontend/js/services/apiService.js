const isLocalFrontendServer =
  ["localhost", "127.0.0.1"].includes(window.location.hostname) &&
  window.location.port &&
  window.location.port !== "8000";

const API_BASE_URL = isLocalFrontendServer ? "http://localhost:8000" : "";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  const contentType = response.headers.get("content-type") ?? "";
  return contentType.includes("application/json")
    ? response.json()
    : response.text();
}

function buildParams(params) {
  const query = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value) {
      query.set(key, value);
    }
  });

  return query.toString();
}

export function getHealth() {
  return request("/api/health");
}

export function getConfig() {
  return request("/api/config");
}

export function getFilters() {
  return request("/api/filters");
}

export function getSummary({ capability, state, city } = {}) {
  const query = buildParams({ capability, state, city });
  return request(`/api/summary${query ? `?${query}` : ""}`);
}

export function searchFacilities({
  capability,
  state,
  city,
  name,
  trustLevel,
  sortBy,
  sortOrder,
  offset,
  limit,
} = {}) {
  const query = buildParams({
    capability,
    state,
    city,
    name,
    trustLevel,
    sortBy,
    sortOrder,
    offset,
    limit,
  });
  return request(`/api/facilities/search${query ? `?${query}` : ""}`);
}

export function getFacility(facilityId, { capability } = {}) {
  const query = buildParams({ capability });
  return request(`/api/facilities/${facilityId}${query ? `?${query}` : ""}`);
}

export function getFacilityMap(facilityId) {
  return request(`/api/facilities/${facilityId}/map`);
}

export function generateAiSummary(facilityId, { capability } = {}) {
  return request(`/api/facilities/${facilityId}/ai-summary`, {
    method: "POST",
    body: JSON.stringify({ capability }),
  });
}

export function getDataQuality({ capability } = {}) {
  const query = buildParams({ capability });
  return request(`/api/data-quality${query ? `?${query}` : ""}`);
}

export function saveReview(review) {
  return request("/api/reviews", {
    method: "POST",
    body: JSON.stringify(review),
  });
}
