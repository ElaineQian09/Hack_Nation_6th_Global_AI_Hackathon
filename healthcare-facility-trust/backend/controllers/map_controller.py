from backend.services.mapbox_service import get_facility_map


def read_facility_map(facility_id: str) -> dict:
    return get_facility_map(facility_id)
