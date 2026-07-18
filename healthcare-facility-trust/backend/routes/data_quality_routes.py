from fastapi import APIRouter

from backend.controllers.data_quality_controller import read_data_quality
from backend.schemas.data_quality import DataQualityResponse


router = APIRouter(prefix="/api", tags=["data-quality"])


@router.get("/data-quality", response_model=DataQualityResponse)
def data_quality() -> dict:
    return read_data_quality()
