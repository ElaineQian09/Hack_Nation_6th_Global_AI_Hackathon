from pydantic import BaseModel


class ScoreReason(BaseModel):
    label: str
    description: str
    impact: str


class FacilityCheck(BaseModel):
    name: str
    isPresent: bool
    evidence: str


class FacilityListItem(BaseModel):
    id: str
    name: str
    type: str
    state: str
    city: str
    address: str
    claimedCapabilities: list[str]
    trustScore: int
    trustLevel: str
    bedCount: int | None
    summary: str
    dataQualityFlags: list[str]
    scoreReasons: list[ScoreReason]


class FacilityDetail(FacilityListItem):
    facilityChecks: list[FacilityCheck]
