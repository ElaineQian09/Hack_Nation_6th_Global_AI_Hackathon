from __future__ import annotations

import os
from typing import Any

from backend.services.facility_service import get_facility_detail


AI_UNAVAILABLE_MESSAGE = (
    "AI summary is unavailable because no Databricks AI endpoint is configured."
)
AI_FAILURE_MESSAGE = "AI summary is unavailable right now."


def generate_ai_summary(
    facility_id: str,
    capability: str | None = None,
) -> dict[str, Any]:
    detail = get_facility_detail(facility_id, capability=capability)
    assessment = detail["assessment"]
    selected_capability = assessment["selected_capability"]
    endpoint_name = os.getenv("DATABRICKS_AI_ENDPOINT", "").strip()

    if not endpoint_name:
        return build_response(
            facility_id=facility_id,
            capability=selected_capability,
            summary=AI_UNAVAILABLE_MESSAGE,
            available=False,
        )

    try:
        summary = query_databricks_endpoint(endpoint_name, build_prompt(assessment))
    except Exception:
        return build_response(
            facility_id=facility_id,
            capability=selected_capability,
            summary=AI_FAILURE_MESSAGE,
            available=False,
        )

    return build_response(
        facility_id=facility_id,
        capability=selected_capability,
        summary=summary or AI_FAILURE_MESSAGE,
        available=bool(summary),
    )


def build_response(
    facility_id: str,
    capability: str,
    summary: str,
    available: bool,
) -> dict[str, Any]:
    return {
        "facilityId": facility_id,
        "capability": capability,
        "summary": summary,
        "available": available,
    }


def build_prompt(assessment: dict[str, Any]) -> str:
    evidence = assessment.get("evidence_snippets", [])[:6]
    evidence_lines = [
        f"- {item.get('source_field')}: {item.get('snippet_text')} ({item.get('explanation')})"
        for item in evidence
    ]
    support_lines = [f"- {item}" for item in assessment.get("support_signals", [])[:5]]
    warning_lines = [f"- {item}" for item in assessment.get("warning_signals", [])[:5]]
    missing_lines = [f"- {item}" for item in assessment.get("missing_signals", [])[:5]]

    return f"""
You are writing an evidence-grounded facility capability summary for public-health planners.

Rules:
- Write 3-5 sentences.
- Explain why the facility is ranked this way.
- Mention uncertainty honestly.
- Do not invent facts.
- Only use evidence provided below.

Facility: {assessment.get("facility_name")}
Selected capability: {assessment.get("selected_capability")}
Trust score: {assessment.get("trust_score")} / 100
Trust label: {assessment.get("trust_label")}
Confidence: {assessment.get("confidence_level")}
Claim present: {"Yes" if assessment.get("claim_present") else "No"}
Reason summary: {assessment.get("reason_summary")}

Supporting signals:
{chr(10).join(support_lines) if support_lines else "- None provided"}

Warning signals:
{chr(10).join(warning_lines) if warning_lines else "- None provided"}

Missing context:
{chr(10).join(missing_lines) if missing_lines else "- None provided"}

Evidence snippets:
{chr(10).join(evidence_lines) if evidence_lines else "- None provided"}
""".strip()


def query_databricks_endpoint(endpoint_name: str, prompt: str) -> str:
    from databricks.sdk import WorkspaceClient
    from databricks.sdk.service.serving import ChatMessage
    from databricks.sdk.service.serving import ChatMessageRole

    workspace = WorkspaceClient()
    response = workspace.serving_endpoints.query(
        name=endpoint_name,
        messages=[
            ChatMessage(
                role=ChatMessageRole.SYSTEM,
                content=(
                    "You summarize healthcare facility evidence. Stay grounded "
                    "in the provided facts and do not invent details."
                ),
            ),
            ChatMessage(role=ChatMessageRole.USER, content=prompt),
        ],
        max_tokens=220,
        temperature=0.2,
    )
    return extract_summary_text(response)


def extract_summary_text(response: Any) -> str:
    if hasattr(response, "as_dict"):
        payload = response.as_dict()
    elif isinstance(response, dict):
        payload = response
    else:
        payload = getattr(response, "__dict__", {})

    choices = payload.get("choices") or []
    if choices:
        first_choice = choices[0]
        message = first_choice.get("message") if isinstance(first_choice, dict) else None
        if isinstance(message, dict):
            return str(message.get("content") or "").strip()
        if isinstance(first_choice, dict):
            return str(first_choice.get("text") or "").strip()

    if payload.get("predictions"):
        first_prediction = payload["predictions"][0]
        if isinstance(first_prediction, dict):
            return str(
                first_prediction.get("content")
                or first_prediction.get("text")
                or first_prediction.get("summary")
                or ""
            ).strip()
        return str(first_prediction).strip()

    return str(payload.get("output") or payload.get("text") or "").strip()
