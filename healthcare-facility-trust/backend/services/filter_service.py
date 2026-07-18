from backend.data.mock_facilities import MOCK_FACILITIES


def get_filter_options() -> dict:
    # TODO: Replace mock option extraction with real metadata queries later.
    capabilities = sorted(
        {
            capability
            for facility in MOCK_FACILITIES
            for capability in facility["claimedCapabilities"]
        }
    )
    states = sorted({facility["state"] for facility in MOCK_FACILITIES})
    cities = sorted({facility["city"] for facility in MOCK_FACILITIES})
    trust_levels = ["High", "Medium", "Low"]

    return {
        "capabilities": capabilities,
        "states": states,
        "cities": cities,
        "trustLevels": trust_levels,
    }
