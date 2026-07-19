from backend.services.databricks_ai_service import get_ai_health


def read_ai_health() -> dict:
    return get_ai_health()
