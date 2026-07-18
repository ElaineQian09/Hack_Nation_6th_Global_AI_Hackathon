from fastapi import APIRouter

from backend.controllers.review_controller import create_review
from backend.schemas.review import ReviewRequest
from backend.schemas.review import ReviewResponse


router = APIRouter(prefix="/api", tags=["reviews"])


@router.post("/reviews", response_model=ReviewResponse)
def reviews(review: ReviewRequest) -> dict:
    return create_review(review)
