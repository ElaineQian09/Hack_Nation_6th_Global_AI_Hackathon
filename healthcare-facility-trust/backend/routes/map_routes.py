from fastapi import APIRouter

from backend.controllers.map_controller import read_facility_map
from backend.schemas.map import FacilityMapResponse


router = APIRouter(prefix="/api/facilities", tags=["facility-map"])


@router.get("/{facility_id}/map", response_model=FacilityMapResponse)
def map_detail(facility_id: str) -> dict:
    return read_facility_map(facility_id)
