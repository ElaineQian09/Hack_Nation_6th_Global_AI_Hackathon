from fastapi import HTTPException

from backend.data.mock_facilities import MOCK_FACILITIES


def search_facilities(
    capability: str | None = None,
    state: str | None = None,
) -> list[dict]:
    # TODO: Replace mock filtering with real ranked search logic later.
    facilities = MOCK_FACILITIES

    if capability:
        facilities = [
            facility
            for facility in facilities
            if capability in facility["claimedCapabilities"]
        ]

    if state:
        facilities = [
            facility
            for facility in facilities
            if facility["state"].lower() == state.lower()
        ]

    return sorted(facilities, key=lambda facility: facility["trustScore"], reverse=True)


def get_facility_detail(facility_id: str) -> dict:
    # TODO: Replace mock lookup with database-backed facility detail retrieval later.
    for facility in MOCK_FACILITIES:
        if facility["id"] == facility_id:
            return facility

    raise HTTPException(status_code=404, detail="Facility not found")
