from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from backend.controllers.health_controller import get_health


router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_class=PlainTextResponse)
def health() -> str:
    return get_health()
