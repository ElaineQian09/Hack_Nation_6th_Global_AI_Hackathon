from backend.schemas.review import ReviewRequest
from backend.services.review_service import save_review


def create_review(review: ReviewRequest) -> dict:
    return save_review(review)
