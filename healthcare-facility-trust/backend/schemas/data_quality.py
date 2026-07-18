from typing import Any

from pydantic import BaseModel


class DataQualityResponse(BaseModel):
    capability: str
    high_leverage_review_queue: list[dict[str, Any]]
    sparse_records: list[dict[str, Any]]
    message: str
