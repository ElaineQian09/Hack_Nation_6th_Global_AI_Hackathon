from backend.data.mock_facilities import MOCK_FACILITIES


def get_summary() -> dict:
    # TODO: Replace mock aggregation with real facility and quality metrics later.
    return {
        "candidateCount": len(MOCK_FACILITIES),
        "highTrustCount": _count_by_trust_level("High"),
        "mediumTrustCount": _count_by_trust_level("Medium"),
        "lowTrustCount": _count_by_trust_level("Low"),
        "dataQualityFlagCount": sum(
            len(facility["dataQualityFlags"]) for facility in MOCK_FACILITIES
        ),
    }


def _count_by_trust_level(level: str) -> int:
    return sum(1 for facility in MOCK_FACILITIES if facility["trustLevel"] == level)
