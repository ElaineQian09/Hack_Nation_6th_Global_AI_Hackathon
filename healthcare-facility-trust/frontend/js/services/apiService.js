const API_BASE_URL = "http://localhost:8000";

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

export function getFilters() {
  return request("/api/filters");
}

export function getSummary() {
  return request("/api/summary");
}

export function searchFacilities({ capability, state } = {}) {
  const params = new URLSearchParams();

  if (capability) {
    params.set("capability", capability);
  }

  if (state) {
    params.set("state", state);
  }

  const query = params.toString();
  return request(`/api/facilities/search${query ? `?${query}` : ""}`);
}

export function getFacility(facilityId) {
  return request(`/api/facilities/${facilityId}`);
}

export function getDataQuality() {
  return request("/api/data-quality");
}

export function saveReview(review) {
  return request("/api/reviews", {
    method: "POST",
    body: JSON.stringify(review),
  });
}
