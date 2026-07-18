from fastapi import APIRouter

from backend.controllers.facility_controller import list_facilities
from backend.controllers.facility_controller import read_facility
from backend.schemas.facility import FacilityDetailResponse
from backend.schemas.facility import FacilitySearchResponse


router = APIRouter(prefix="/api/facilities", tags=["facilities"])


@router.get("/search", response_model=FacilitySearchResponse)
def search(
    capability: str | None = None,
    state: str | None = None,
    city: str | None = None,
    limit: int = 100,
) -> dict:
    return list_facilities(capability=capability, state=state, city=city, limit=limit)


@router.get("/{facility_id}", response_model=FacilityDetailResponse)
def detail(facility_id: str, capability: str | None = None) -> dict:
    return read_facility(facility_id, capability=capability)
