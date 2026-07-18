from fastapi import APIRouter

from backend.controllers.facility_controller import list_facilities
from backend.controllers.facility_controller import read_facility
from backend.schemas.facility import FacilityDetail
from backend.schemas.facility import FacilityListItem


router = APIRouter(prefix="/api/facilities", tags=["facilities"])


@router.get("/search", response_model=list[FacilityListItem])
def search(capability: str | None = None, state: str | None = None) -> list[dict]:
    return list_facilities(capability=capability, state=state)


@router.get("/{facility_id}", response_model=FacilityDetail)
def detail(facility_id: str) -> dict:
    return read_facility(facility_id)
