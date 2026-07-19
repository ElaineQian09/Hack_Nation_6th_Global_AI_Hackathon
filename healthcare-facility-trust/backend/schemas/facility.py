from typing import Any

from pydantic import BaseModel


class EvidenceSnippet(BaseModel):
    evidence_id: str
    evidence_type: str
    source_field: str
    snippet_text: str
    signal_direction: str
    signal_strength: str
    explanation: str


class FacilityAssessment(BaseModel):
    facility_id: str
    facility_name: str
    state: str
    city: str
    district: str | None = None
    pin_code: str | None = None
    selected_capability: str
    claim_present: bool
    trust_score: int
    trust_label: str
    confidence_level: str
    support_signal_count: int
    warning_signal_count: int
    missing_signal_count: int
    support_signals: list[str]
    warning_signals: list[str]
    missing_signals: list[str]
    reason_summary: str
    evidence_snippets: list[EvidenceSnippet]
    description_text: str | None = None
    capability_text: list[str]
    procedure_text: list[str]
    equipment_text: list[str]
    specialties: list[str]
    number_doctors: int | None = None
    capacity: int | None = None
    year_established: int | None = None
    official_website: str | None = None
    last_scored_at: str


class FacilitySearchResponse(BaseModel):
    capability: str
    state: str | None = None
    city: str | None = None
    name: str | None = None
    trustLevel: str | None = None
    sortBy: str
    sortOrder: str
    offset: int
    limit: int
    total: int
    returned: int
    nextOffset: int
    hasMore: bool
    results: list[FacilityAssessment]


class FacilityDetailResponse(BaseModel):
    facility: dict[str, Any]
    assessment: FacilityAssessment
    reviews: list[dict[str, Any]]


class AiSummaryRequest(BaseModel):
    capability: str | None = None


class AiSummaryResponse(BaseModel):
    facilityId: str
    capability: str
    available: bool
    disclaimer: str
    verdict: str
    confidence: str
    explanation: str
    citations: list[dict[str, Any]]
    rejected_citations: list[dict[str, Any]]
    missing_information: list[str]
    warnings: list[str]
