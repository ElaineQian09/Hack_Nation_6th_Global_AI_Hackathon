import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.schemas.review import ReviewRequest


BASE_DIR = Path(__file__).resolve().parents[2]
REVIEW_DATA_PATH = BASE_DIR / ".runtime" / "reviews.json"


def load_reviews() -> list[dict[str, Any]]:
    if not REVIEW_DATA_PATH.exists():
        return []
    with REVIEW_DATA_PATH.open() as file:
        return json.load(file)


def write_reviews(reviews: list[dict[str, Any]]) -> None:
    REVIEW_DATA_PATH.parent.mkdir(exist_ok=True)
    with REVIEW_DATA_PATH.open("w") as file:
        json.dump(reviews, file, indent=2)


def save_review(review: ReviewRequest) -> dict:
    saved_review = review.model_dump()
    saved_review["createdAt"] = datetime.now(timezone.utc).isoformat()

    reviews = load_reviews()
    reviews.append(saved_review)
    write_reviews(reviews)

    return {
        "status": "saved",
        "message": "Review saved.",
        "review": saved_review,
    }
