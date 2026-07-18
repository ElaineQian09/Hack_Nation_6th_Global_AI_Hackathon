from backend.services.filter_service import get_filter_options


def list_filters() -> dict:
    return get_filter_options()
