from pydantic import BaseModel


class DataQualityIssue(BaseModel):
    facilityId: str
    facilityName: str
    issue: str
    severity: str


class DataQualityResponse(BaseModel):
    issues: list[DataQualityIssue]
