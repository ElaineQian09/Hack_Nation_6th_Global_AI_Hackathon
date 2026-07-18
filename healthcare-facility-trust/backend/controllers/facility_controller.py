from backend.services.facility_service import get_facility_detail
from backend.services.facility_service import search_facilities


def list_facilities(
    capability: str | None = None,
    state: str | None = None,
    city: str | None = None,
    limit: int = 100,
) -> dict:
    return search_facilities(capability=capability, state=state, city=city, limit=limit)


def read_facility(facility_id: str, capability: str | None = None) -> dict:
    return get_facility_detail(facility_id, capability=capability)
