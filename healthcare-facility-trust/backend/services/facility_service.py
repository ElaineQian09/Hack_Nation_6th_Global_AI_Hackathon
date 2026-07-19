from __future__ import annotations

import json
import re
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import HTTPException

BASE_DIR = Path(__file__).resolve().parents[2]
FACILITY_DATA_PATH = BASE_DIR / "sample_data" / "demo_facilities.json"
CLEAN_FACILITY_CSV_PATH = BASE_DIR / "sample_data" / "clean_facilities.csv"

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


LIST_FIELDS = {
    "phone_numbers",
    "websites",
    "affiliationTypeIds",
    "specialties",
    "procedure",
    "equipment",
    "capability",
}

INT_FIELDS = {"area", "numberDoctors", "capacity", "yearEstablished"}

FIELD_ALIASES = {
    "id": "facility_id",
    "facilityId": "facility_id",
    "facility_id": "facility_id",
    "name": "name",
    "facilityName": "name",
    "officialName": "name",
    "city": "address_city",
    "state": "address_stateOrRegion",
    "stateOrRegion": "address_stateOrRegion",
    "zip": "address_zipOrPostcode",
    "postcode": "address_zipOrPostcode",
    "pin": "address_zipOrPostcode",
    "pincode": "address_zipOrPostcode",
    "pinCode": "address_zipOrPostcode",
    "country": "address_country",
    "countryCode": "address_countryCode",
    "country_code": "address_countryCode",
    "officialWebsite": "officialWebsite",
    "website": "officialWebsite",
    "websites": "websites",
    "source_urls_json": "websites",
    "description": "description",
    "facilityTypeId": "facilityTypeId",
    "facility_type": "facilityTypeId",
    "operatorTypeId": "operatorTypeId",
    "operator_type": "operatorTypeId",
    "affiliationTypeIds": "affiliationTypeIds",
    "numberDoctors": "numberDoctors",
    "doctor_count": "numberDoctors",
    "capacity": "capacity",
    "yearEstablished": "yearEstablished",
    "specialties": "specialties",
    "specialties_json": "specialties",
    "procedure": "procedure",
    "procedures": "procedure",
    "procedures_json": "procedure",
    "equipment": "equipment",
    "equipment_json": "equipment",
    "capability": "capability",
    "capabilities": "capability",
    "capabilities_json": "capability",
    "data_quality_flags_json": "dataQualityFlags",
}


def load_facilities() -> list[dict[str, Any]]:
    if CLEAN_FACILITY_CSV_PATH.exists():
        return load_facilities_from_csv(CLEAN_FACILITY_CSV_PATH)

    with FACILITY_DATA_PATH.open() as file:
        return json.load(file)


def load_facilities_from_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return [normalize_csv_row(row, index) for index, row in enumerate(reader, start=1)]


def normalize_csv_row(row: dict[str, Any], index: int) -> dict[str, Any]:
    normalized: dict[str, Any] = {}

    for raw_key, value in row.items():
        key = FIELD_ALIASES.get(raw_key, raw_key)
        normalized[key] = normalize_csv_value(key, value)

    normalized.setdefault("facility_id", f"facility-{index:05d}")
    normalized.setdefault("name", f"Facility {index}")
    normalized.setdefault("address_city", "")
    normalized.setdefault("address_stateOrRegion", "")
    normalized.setdefault("address_zipOrPostcode", "")
    normalized.setdefault("address_country", "India")
    normalized.setdefault("address_countryCode", "IN")
    normalized.setdefault("facilityTypeId", "")
    normalized.setdefault("operatorTypeId", "")
    normalized.setdefault("description", "")
    normalized.setdefault("officialWebsite", "")

    for field in LIST_FIELDS:
        normalized[field] = coerce_list(normalized.get(field))

    for field in INT_FIELDS:
        normalized[field] = coerce_int(normalized.get(field))

    if normalized.get("officialWebsite") and not normalized.get("websites"):
        normalized["websites"] = [normalized["officialWebsite"]]

    return normalized


def normalize_csv_value(key: str, value: Any) -> Any:
    if value is None:
        return None

    value = str(value).strip()
    if not value or value.lower() in {"nan", "none", "null", "n/a", "na"}:
        return None

    if key in LIST_FIELDS:
        return coerce_list(value)
    if key in INT_FIELDS:
        return coerce_int(value)
    return value


def coerce_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    text = str(value).strip()
    if not text:
        return []

    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except json.JSONDecodeError:
            try:
                parsed = json.loads(text.replace("'", '"'))
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except json.JSONDecodeError:
                pass

    parts = re.split(r"\s*\|\s*|\s*;\s*", text)
    return [part.strip() for part in parts if part.strip()]


def coerce_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(str(value).replace(",", "")))
    except ValueError:
        return None


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
    limit: int | None = None,
) -> list[dict[str, Any]]:
    if capability not in CAPABILITY_RULES:
        raise HTTPException(status_code=400, detail=f"Unsupported capability: {capability}")

    facilities = filter_facilities(load_facilities(), state, city)
    results = [score_facility(facility, capability) for facility in facilities]
    sorted_results = sorted(results, key=lambda item: item["trust_score"], reverse=True)
    return sorted_results[:limit] if limit else sorted_results


def sort_results(
    results: list[dict[str, Any]],
    sort_by: str = "trust_score",
    sort_order: str = "desc",
) -> list[dict[str, Any]]:
    normalized_sort_by = sort_by or "trust_score"
    reverse = (sort_order or "desc").lower() != "asc"
    numeric_fields = {
        "trust_score",
        "support_signal_count",
        "warning_signal_count",
        "missing_signal_count",
        "number_doctors",
        "capacity",
        "year_established",
    }
    trust_order = {
        "Unverified": 0,
        "Weak": 1,
        "Mixed": 2,
        "Trusted": 3,
    }

    def sort_key(item: dict[str, Any]) -> Any:
        value = item.get(normalized_sort_by)
        if normalized_sort_by == "trust_label":
            return trust_order.get(str(value), -1)
        if normalized_sort_by in numeric_fields:
            return value or 0
        return str(value or "").lower()

    return sorted(results, key=sort_key, reverse=reverse)


def compact_assessment(assessment: dict[str, Any]) -> dict[str, Any]:
    compact = assessment.copy()
    compact["evidence_snippets"] = []
    compact["description_text"] = None
    compact["capability_text"] = []
    compact["procedure_text"] = []
    compact["equipment_text"] = []
    compact["specialties"] = []
    compact["support_signals"] = compact["support_signals"][:2]
    return compact


def search_facilities(
    capability: str | None = None,
    state: str | None = None,
    city: str | None = None,
    name: str | None = None,
    trustLevel: str | None = None,
    sortBy: str = "trust_score",
    sortOrder: str = "desc",
    offset: int = 0,
    limit: int = 20,
) -> dict[str, Any]:
    selected_capability = capability or "ICU"
    normalized_offset = max(0, offset)
    normalized_limit = max(1, min(limit, 50))
    normalized_sort_by = sortBy or "trust_score"
    normalized_sort_order = "asc" if (sortOrder or "desc").lower() == "asc" else "desc"

    results = score_results(selected_capability, state, city)

    if name:
        normalized_name = name.lower()
        results = [
            result
            for result in results
            if normalized_name in result["facility_name"].lower()
        ]

    if trustLevel:
        normalized_trust_level = trustLevel.lower()
        results = [
            result
            for result in results
            if result["trust_label"].lower() == normalized_trust_level
        ]

    results = sort_results(results, normalized_sort_by, normalized_sort_order)
    total = len(results)
    paged_results = results[normalized_offset : normalized_offset + normalized_limit]
    next_offset = normalized_offset + len(paged_results)

    return {
        "capability": selected_capability,
        "state": state,
        "city": city,
        "name": name,
        "trustLevel": trustLevel,
        "sortBy": normalized_sort_by,
        "sortOrder": normalized_sort_order,
        "offset": normalized_offset,
        "limit": normalized_limit,
        "total": total,
        "returned": len(paged_results),
        "nextOffset": next_offset,
        "hasMore": next_offset < total,
        "results": [compact_assessment(result) for result in paged_results],
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
