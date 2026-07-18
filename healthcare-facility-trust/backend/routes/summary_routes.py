from fastapi import APIRouter

from backend.controllers.summary_controller import read_summary
from backend.schemas.summary import SummaryResponse


router = APIRouter(prefix="/api", tags=["summary"])


@router.get("/summary", response_model=SummaryResponse)
def summary(
    capability: str = "ICU",
    state: str | None = None,
    city: str | None = None,
) -> dict:
    return read_summary(capability=capability, state=state, city=city)
