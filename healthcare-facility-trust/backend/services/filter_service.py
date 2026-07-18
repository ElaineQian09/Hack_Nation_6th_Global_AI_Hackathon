from backend.services.facility_service import CAPABILITY_RULES
from backend.services.facility_service import load_facilities


def get_filter_options() -> dict:
    facilities = load_facilities()

    return {
        "capabilities": list(CAPABILITY_RULES.keys()),
        "states": sorted({facility["address_stateOrRegion"] for facility in facilities}),
        "cities": sorted({facility["address_city"] for facility in facilities}),
        "trustLevels": ["Trusted", "Mixed", "Weak", "Unverified"],
        "decisions": ["Accept", "Needs Review", "Reject Claim", "Override as Trusted"],
    }
