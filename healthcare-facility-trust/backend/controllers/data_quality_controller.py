from backend.services.data_quality_service import get_data_quality_issues


def read_data_quality(capability: str = "ICU") -> dict:
    return get_data_quality_issues(capability=capability)
