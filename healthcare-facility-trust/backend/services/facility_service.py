from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import HTTPException

BASE_DIR = Path(__file__).resolve().parents[2]
FACILITY_DATA_PATH = BASE_DIR / "sample_data" / "demo_facilities.json"

CAPABILITY_RULES: dict[str, dict[str, list[str]]] = {
    "ICU": {
        "claim_terms": ["icu", "intensive care"],
        "support_terms": [
            "icu",
            "intensive care",
            "critical care",
            "ventilator",
            "oxygen",
            "monitor",
            "high dependency",
        ],
        "equipment_terms": ["ventilator", "oxygen", "monitor", "icu"],
        "specialty_terms": ["internalmedicine", "emergencymedicine", "anesthesia"],
    },
    "Emergency": {
        "claim_terms": ["emergency", "trauma", "casualty"],
        "support_terms": [
            "emergency",
            "trauma",
            "casualty",
            "ambulance",
            "24x7",
            "24/7",
            "urgent",
        ],
        "equipment_terms": ["ambulance", "oxygen", "monitor", "defibrillator"],
        "specialty_terms": ["emergencymedicine", "generalsurgery", "orthopedicsurgery"],
    },
    "NICU": {
        "claim_terms": ["nicu", "neonatal"],
        "support_terms": [
            "nicu",
            "neonatal",
            "incubator",
            "warmer",
            "pediatric",
            "newborn",
            "ventilator",
        ],
        "equipment_terms": ["incubator", "warmer", "ventilator", "oxygen"],
        "specialty_terms": ["pediatrics", "gynecologyandobstetrics"],
    },
    "Maternity": {
        "claim_terms": ["maternity", "delivery", "obstetric", "labor"],
        "support_terms": [
            "maternity",
            "delivery",
            "labor",
            "obstetric",
            "gynecology",
            "antenatal",
            "cesarean",
        ],
        "equipment_terms": ["labor", "ultrasound", "operation theatre", "oxygen"],
        "specialty_terms": ["gynecologyandobstetrics", "pediatrics"],
    },
}


def load_facilities() -> list[dict[str, Any]]:
    with FACILITY_DATA_PATH.open() as file:
        return json.load(file)


def normalize(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(str(item) for item in value).lower()
    return str(value).lower()


def field_values(facility: dict[str, Any], field: str) -> list[str]:
    value = facility.get(field)
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if str(value).strip():
        return [str(value)]
    return []


def has_term(text: str, term: str) -> bool:
    pattern = r"(?<![a-z0-9])" + re.escape(term.lower()) + r"(?![a-z0-9])"
    return re.search(pattern, text.lower()) is not None


def extract_evidence(facility: dict[str, Any], capability: str) -> list[dict[str, str]]:
    rules = CAPABILITY_RULES[capability]
    evidence: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for field in ["description", "capability", "procedure", "equipment", "specialties"]:
        for value in field_values(facility, field):
            normalized = normalize(value)
            matched_terms = [
                term
                for term in rules["support_terms"] + rules["specialty_terms"]
                if has_term(normalized, term)
            ]
            if not matched_terms:
                continue

            key = (field, value)
            if key in seen:
                continue

            seen.add(key)
            evidence.append(
                {
                    "evidence_id": f"{facility['facility_id']}-{capability}-{len(evidence) + 1}",
                    "evidence_type": "support",
                    "source_field": field,
                    "snippet_text": value,
                    "signal_direction": "positive",
                    "signal_strength": "strong" if field in {"equipment", "procedure"} else "medium",
                    "explanation": f"Matches {capability} evidence terms: {', '.join(matched_terms[:3])}",
                }
            )

    return evidence


def score_facility(facility: dict[str, Any], capability: str) -> dict[str, Any]:
    rules = CAPABILITY_RULES[capability]
    capability_text = normalize(facility.get("capability", []))
    claim_present = any(has_term(capability_text, term) for term in rules["claim_terms"])
    evidence = extract_evidence(facility, capability)
    support_fields = {item["source_field"] for item in evidence}
    non_claim_support_fields = support_fields - {"capability"}
    equipment_text = normalize(facility.get("equipment", []))
    equipment_support = any(has_term(equipment_text, term) for term in rules["equipment_terms"])

    support_signals = [
        f"{item['source_field']}: {item['snippet_text']}"
        for item in evidence
        if item["source_field"] != "capability"
    ]
    warning_signals: list[str] = []
    missing_signals: list[str] = []

    if claim_present and not non_claim_support_fields:
        warning_signals.append(
            "Capability appears as a claim but no supporting description, procedure, or equipment evidence was found."
        )
    if claim_present and not equipment_support:
        warning_signals.append(f"No equipment evidence was found for {capability}.")
    if not claim_present and non_claim_support_fields:
        warning_signals.append(
            "Evidence hints at this capability, but the capability field does not explicitly claim it."
        )
    if not facility.get("numberDoctors"):
        missing_signals.append("numberDoctors is missing.")
    if not facility.get("capacity"):
        missing_signals.append("capacity is missing.")
    if not facility.get("officialWebsite") and not facility.get("websites"):
        missing_signals.append("No official website or source website is available.")

    score = 0
    score += 20 if claim_present else 0
    score += min(len(evidence) * 8, 40)
    score += min(len(non_claim_support_fields) * 10, 30)
    score += 6 if facility.get("numberDoctors") else 0
    score += 6 if facility.get("capacity") else 0
    score += 4 if facility.get("officialWebsite") or facility.get("websites") else 0
    score -= 18 if claim_present and not non_claim_support_fields else 0
    score -= 10 if claim_present and not equipment_support else 0
    score -= min(len(missing_signals) * 4, 12)
    trust_score = max(0, min(100, score))

    if trust_score >= 75:
        trust_label = "Trusted"
    elif trust_score >= 50:
        trust_label = "Mixed"
    elif trust_score >= 25:
        trust_label = "Weak"
    else:
        trust_label = "Unverified"

    completeness = sum(
        1
        for key in ["numberDoctors", "capacity", "yearEstablished", "officialWebsite"]
        if facility.get(key)
    )
    if len(non_claim_support_fields) >= 3 and completeness >= 3:
        confidence_level = "High"
    elif len(non_claim_support_fields) >= 2 or completeness >= 2:
        confidence_level = "Medium"
    else:
        confidence_level = "Low"

    if not support_signals and claim_present:
        reason_summary = f"{capability} is claimed, but the supporting fields are sparse."
    elif support_signals and warning_signals:
        reason_summary = f"{capability} has supporting evidence, but important gaps remain."
    elif support_signals:
        reason_summary = f"{capability} is supported across {len(non_claim_support_fields)} non-claim field(s)."
    else:
        reason_summary = f"No clear {capability} claim or supporting evidence was found."

    return {
        "facility_id": facility["facility_id"],
        "facility_name": facility["name"],
        "state": facility["address_stateOrRegion"],
        "city": facility["address_city"],
        "district": facility.get("district"),
        "pin_code": facility.get("address_zipOrPostcode"),
        "selected_capability": capability,
        "claim_present": claim_present,
        "trust_score": trust_score,
        "trust_label": trust_label,
        "confidence_level": confidence_level,
        "support_signal_count": len(support_signals),
        "warning_signal_count": len(warning_signals),
        "missing_signal_count": len(missing_signals),
        "support_signals": support_signals[:5],
        "warning_signals": warning_signals,
        "missing_signals": missing_signals,
        "reason_summary": reason_summary,
        "evidence_snippets": evidence,
        "description_text": facility.get("description"),
        "capability_text": facility.get("capability", []),
        "procedure_text": facility.get("procedure", []),
        "equipment_text": facility.get("equipment", []),
        "specialties": facility.get("specialties", []),
        "number_doctors": facility.get("numberDoctors"),
        "capacity": facility.get("capacity"),
        "year_established": facility.get("yearEstablished"),
        "official_website": facility.get("officialWebsite"),
        "last_scored_at": datetime.now(timezone.utc).isoformat(),
    }


def filter_facilities(
    facilities: list[dict[str, Any]],
    state: str | None,
    city: str | None,
) -> list[dict[str, Any]]:
    filtered = facilities
    if state:
        filtered = [
            item for item in filtered if item["address_stateOrRegion"].lower() == state.lower()
        ]
    if city:
        filtered = [item for item in filtered if item["address_city"].lower() == city.lower()]
    return filtered


def score_results(
    capability: str = "ICU",
    state: str | None = None,
    city: str | None = None,
) -> list[dict[str, Any]]:
    if capability not in CAPABILITY_RULES:
        raise HTTPException(status_code=400, detail=f"Unsupported capability: {capability}")

    facilities = filter_facilities(load_facilities(), state, city)
    results = [score_facility(facility, capability) for facility in facilities]
    return sorted(results, key=lambda item: item["trust_score"], reverse=True)


def search_facilities(
    capability: str | None = None,
    state: str | None = None,
    city: str | None = None,
) -> dict[str, Any]:
    selected_capability = capability or "ICU"
    return {
        "capability": selected_capability,
        "state": state,
        "city": city,
        "results": score_results(selected_capability, state, city),
    }


def get_facility_detail(facility_id: str, capability: str | None = None) -> dict[str, Any]:
    selected_capability = capability or "ICU"
    facility = next((item for item in load_facilities() if item["facility_id"] == facility_id), None)
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")

    from backend.services.review_service import load_reviews

    return {
        "facility": facility,
        "assessment": score_facility(facility, selected_capability),
        "reviews": [
            review
            for review in load_reviews()
            if review["facilityId"] == facility_id and review["capability"] == selected_capability
        ],
    }
