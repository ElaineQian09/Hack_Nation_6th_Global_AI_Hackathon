from backend.data.mock_facilities import MOCK_DATA_QUALITY_ISSUES


def get_data_quality_issues() -> dict:
    # TODO: Replace mock issues with real suspicious coordinate, capacity, claim, and conflict checks later.
    return {"issues": MOCK_DATA_QUALITY_ISSUES}
