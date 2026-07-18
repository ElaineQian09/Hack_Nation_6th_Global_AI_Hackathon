from pydantic import BaseModel


class FacilityMapResponse(BaseModel):
    facilityId: str
    name: str
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    source: str
    confidence: str
    placeName: str | None = None
    warning: str | None = None
