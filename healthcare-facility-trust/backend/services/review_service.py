from backend.schemas.review import ReviewRequest


def save_review(review: ReviewRequest) -> dict:
    # TODO: Persist reviewer decision, override, and note to a database later.
    return {
        "status": "accepted",
        "message": "Demo review received. Persistence will be implemented later.",
        "review": review,
    }
