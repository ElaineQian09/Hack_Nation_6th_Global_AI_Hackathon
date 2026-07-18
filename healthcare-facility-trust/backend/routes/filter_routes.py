from fastapi import APIRouter

from backend.controllers.filter_controller import list_filters
from backend.schemas.filters import FilterOptions


router = APIRouter(prefix="/api", tags=["filters"])


@router.get("/filters", response_model=FilterOptions)
def filters() -> dict:
    return list_filters()
