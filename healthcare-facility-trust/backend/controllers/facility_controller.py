from backend.services.databricks_ai_service import generate_ai_summary
from backend.services.facility_service import get_facility_detail
from backend.services.facility_service import search_facilities


def list_facilities(
    capability: str | None = None,
    state: str | None = None,
    city: str | None = None,
    name: str | None = None,
    trustLevel: str | None = None,
    sortBy: str = "trust_score",
    sortOrder: str = "desc",
    offset: int = 0,
    limit: int = 20,
) -> dict:
    return search_facilities(
        capability=capability,
        state=state,
        city=city,
        name=name,
        trustLevel=trustLevel,
        sortBy=sortBy,
        sortOrder=sortOrder,
        offset=offset,
        limit=limit,
    )


def read_facility(facility_id: str, capability: str | None = None) -> dict:
    return get_facility_detail(facility_id, capability=capability)


def read_ai_summary(facility_id: str, capability: str | None = None) -> dict:
    return generate_ai_summary(facility_id, capability=capability)
