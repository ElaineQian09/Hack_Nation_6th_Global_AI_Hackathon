from pydantic import BaseModel


class SummaryResponse(BaseModel):
    capability: str
    facility_count: int
    trust_buckets: dict[str, int]
    confidence_buckets: dict[str, int]
    warning_count: int
    missing_signal_count: int
