from backend.services.summary_service import get_summary


def read_summary() -> dict:
    return get_summary()
