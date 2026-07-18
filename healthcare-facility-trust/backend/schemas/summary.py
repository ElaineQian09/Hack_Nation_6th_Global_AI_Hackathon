from pydantic import BaseModel


class SummaryResponse(BaseModel):
    candidateCount: int
    highTrustCount: int
    mediumTrustCount: int
    lowTrustCount: int
    dataQualityFlagCount: int
