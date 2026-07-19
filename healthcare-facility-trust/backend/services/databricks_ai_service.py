from __future__ import annotations

import json
import os
import re
from typing import Any, Literal

from pydantic import BaseModel
from pydantic import ValidationError

from backend.services.facility_service import get_facility_detail


ReviewVerdict = Literal[
    "supported",
    "partially_supported",
    "inconsistent",
    "insufficient_data",
]
ReviewConfidence = Literal["high", "medium", "low"]
CitationField = Literal[
    "description",
    "capability",
    "equipment",
    "procedure",
    "specialties",
]
CitationRelation = Literal["supports", "contradicts"]

DISCLAIMER = (
    "This review evaluates support in the available dataset. It is not a "
    "clinical certification of the facility."
)

AI_UNAVAILABLE_MESSAGE = (
    "AI Evidence Review is unavailable because SERVING_ENDPOINT is not configured."
)
AI_FAILURE_MESSAGE = "AI Evidence Review is unavailable right now."


class AICitation(BaseModel):
    source_field: CitationField
    exact_quote: str
    relation: CitationRelation


class AIReviewModel(BaseModel):
    verdict: ReviewVerdict
    confidence: ReviewConfidence
    explanation: str
    citations: list[AICitation]
    missing_information: list[str]
    warnings: list[str]


class ValidatedAIReviewModel(AIReviewModel):
    rejected_citations: list[AICitation]


class AIReviewResponse(BaseModel):
    facilityId: str
    capability: str
    available: bool
    disclaimer: str
    verdict: ReviewVerdict
    confidence: ReviewConfidence
    explanation: str
    citations: list[AICitation]
    rejected_citations: list[AICitation]
    missing_information: list[str]
    warnings: list[str]


SYSTEM_PROMPT = """
You are validating evidence inside one healthcare facility record.

Rules:
- Treat every field as an unverified claim, not ground truth.
- Do not use external knowledge.
- Do not infer missing facts.
- Missing information is not negative evidence.
- Every citation must be copied exactly from one supplied source field.
- Distinguish current capability from negation, historical information, future plans, and referrals elsewhere.
- Do not certify that the facility actually possesses the medical capability.
- Return one JSON object only, with no Markdown.
""".strip()


def generate_ai_summary(
    facility_id: str,
    capability: str | None = None,
) -> dict[str, Any]:
    detail = get_facility_detail(facility_id, capability=capability)
    assessment = detail["assessment"]
    selected_capability = assessment["selected_capability"]
    endpoint_name = get_serving_endpoint()

    if not endpoint_name:
        return build_unavailable_response(
            facility_id=facility_id,
            capability=selected_capability,
            message=AI_UNAVAILABLE_MESSAGE,
        )

    model_input = build_model_input(detail)

    try:
        raw_content = query_databricks_endpoint(endpoint_name, model_input)
        review = parse_model_response(raw_content)
        validated_review = validate_ai_review(review, model_input["source_fields"])
    except AIReviewError as error:
        return build_unavailable_response(
            facility_id=facility_id,
            capability=selected_capability,
            message=str(error),
        )
    except Exception:
        return build_unavailable_response(
            facility_id=facility_id,
            capability=selected_capability,
            message=AI_FAILURE_MESSAGE,
        )

    return AIReviewResponse(
        facilityId=facility_id,
        capability=selected_capability,
        available=True,
        disclaimer=DISCLAIMER,
        **validated_review.model_dump(),
    ).model_dump()


def get_serving_endpoint() -> str:
    return os.getenv("SERVING_ENDPOINT", "").strip()


def build_unavailable_response(
    facility_id: str,
    capability: str,
    message: str,
) -> dict[str, Any]:
    return AIReviewResponse(
        facilityId=facility_id,
        capability=capability,
        available=False,
        disclaimer=DISCLAIMER,
        verdict="insufficient_data",
        confidence="low",
        explanation=message,
        citations=[],
        rejected_citations=[],
        missing_information=[],
        warnings=[message],
    ).model_dump()


def build_model_input(detail: dict[str, Any]) -> dict[str, Any]:
    facility = detail["facility"]
    assessment = detail["assessment"]

    source_fields = {
        "description": facility.get("description") or assessment.get("description_text") or "",
        "capability": facility.get("capability") or assessment.get("capability_text") or [],
        "equipment": facility.get("equipment") or assessment.get("equipment_text") or [],
        "procedure": facility.get("procedure") or assessment.get("procedure_text") or [],
        "specialties": facility.get("specialties") or assessment.get("specialties") or [],
    }

    return {
        "facility": {
            "name": facility.get("name") or assessment.get("facility_name"),
            "facilityTypeId": facility.get("facilityTypeId"),
            "capacity": facility.get("capacity") or assessment.get("capacity"),
            "numberDoctors": facility.get("numberDoctors") or assessment.get("number_doctors"),
        },
        "selected_capability": assessment.get("selected_capability"),
        "deterministic_assessment": {
            "trust_score": assessment.get("trust_score"),
            "trust_label": assessment.get("trust_label"),
            "confidence_level": assessment.get("confidence_level"),
            "claim_present": assessment.get("claim_present"),
            "support_signals": assessment.get("support_signals", []),
            "warning_signals": assessment.get("warning_signals", []),
            "missing_signals": assessment.get("missing_signals", []),
            "reason_summary": assessment.get("reason_summary"),
        },
        "source_fields": source_fields,
    }


def build_user_prompt(model_input: dict[str, Any]) -> str:
    response_schema = {
        "verdict": "supported | partially_supported | inconsistent | insufficient_data",
        "confidence": "high | medium | low",
        "explanation": "Brief explanation grounded only in the supplied record",
        "citations": [
            {
                "source_field": "description | capability | equipment | procedure | specialties",
                "exact_quote": "Exact substring copied from that field",
                "relation": "supports | contradicts",
            }
        ],
        "missing_information": ["..."],
        "warnings": ["..."],
    }

    return json.dumps(
        {
            "task": "Validate whether the selected capability is supported by the supplied facility fields.",
            "required_response_schema": response_schema,
            "record": model_input,
        },
        ensure_ascii=False,
    )


def query_databricks_endpoint(endpoint_name: str, model_input: dict[str, Any]) -> str:
    from databricks_openai import DatabricksOpenAI

    client = DatabricksOpenAI()
    response = client.chat.completions.create(
        model=endpoint_name,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(model_input)},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    return response.choices[0].message.content or ""


def parse_model_response(raw_content: str) -> AIReviewModel:
    try:
        payload = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        raise AIReviewError("AI returned malformed JSON.") from exc

    try:
        return AIReviewModel.model_validate(payload)
    except ValidationError as exc:
        raise AIReviewError("AI response did not match the expected review schema.") from exc


def validate_ai_review(
    review: AIReviewModel,
    source_fields: dict[str, Any],
) -> ValidatedAIReviewModel:
    valid_citations: list[AICitation] = []
    rejected_citations: list[AICitation] = []

    for citation in review.citations:
        if citation_exists_in_source(citation, source_fields):
            valid_citations.append(citation)
        else:
            rejected_citations.append(citation)

    warnings = list(review.warnings)
    verdict = review.verdict
    confidence = review.confidence

    if verdict in {"supported", "partially_supported", "inconsistent"} and not valid_citations:
        verdict = "insufficient_data"
        confidence = "low"
        warnings.append(
            "AI verdict was downgraded after deterministic citation validation because no cited quote was found in the supplied fields."
        )

    return ValidatedAIReviewModel(
        verdict=verdict,
        confidence=confidence,
        explanation=review.explanation,
        citations=valid_citations,
        rejected_citations=rejected_citations,
        missing_information=review.missing_information,
        warnings=warnings,
    )


def citation_exists_in_source(
    citation: AICitation,
    source_fields: dict[str, Any],
) -> bool:
    source_value = source_fields.get(citation.source_field)
    quote = normalize_for_match(citation.exact_quote)

    if not quote:
        return False

    if isinstance(source_value, list):
        return any(quote in normalize_for_match(item) for item in source_value)

    return quote in normalize_for_match(source_value)


def normalize_for_match(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().casefold()


class AIReviewError(Exception):
    pass
