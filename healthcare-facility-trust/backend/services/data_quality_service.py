from typing import Any

from backend.services.facility_service import score_results


def get_data_quality_issues(capability: str = "ICU") -> dict[str, Any]:
    results = score_results(capability)
    high_leverage = [
        result
        for result in results
        if result["claim_present"] and result["trust_label"] in {"Weak", "Unverified"}
    ]
    sparse = [result for result in results if result["confidence_level"] == "Low"]

    return {
        "capability": capability,
        "high_leverage_review_queue": high_leverage[:5],
        "sparse_records": sparse[:5],
        "message": "High-leverage records claim an important capability but have weak or sparse supporting evidence.",
    }
