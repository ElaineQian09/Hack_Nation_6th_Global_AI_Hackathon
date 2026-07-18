from pydantic import BaseModel


class ReviewRequest(BaseModel):
    facilityId: str
    capability: str
    decision: str
    note: str


class ReviewResponse(BaseModel):
    status: str
    message: str
    review: ReviewRequest
