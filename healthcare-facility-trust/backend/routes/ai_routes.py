from fastapi import APIRouter

from backend.controllers.ai_controller import read_ai_health


router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/health")
def ai_health() -> dict:
    return read_ai_health()
