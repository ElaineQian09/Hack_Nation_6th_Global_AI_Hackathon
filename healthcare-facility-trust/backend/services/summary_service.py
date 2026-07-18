from typing import Any

from backend.services.facility_service import score_results


def get_summary(
    capability: str = "ICU",
    state: str | None = None,
    city: str | None = None,
) -> dict[str, Any]:
    results = score_results(capability, state, city)
    trust_buckets = {label: 0 for label in ["Trusted", "Mixed", "Weak", "Unverified"]}
    confidence_buckets = {label: 0 for label in ["High", "Medium", "Low"]}

    for result in results:
        trust_buckets[result["trust_label"]] += 1
        confidence_buckets[result["confidence_level"]] += 1

    return {
        "capability": capability,
        "facility_count": len(results),
        "trust_buckets": trust_buckets,
        "confidence_buckets": confidence_buckets,
        "warning_count": sum(result["warning_signal_count"] for result in results),
        "missing_signal_count": sum(result["missing_signal_count"] for result in results),
    }
