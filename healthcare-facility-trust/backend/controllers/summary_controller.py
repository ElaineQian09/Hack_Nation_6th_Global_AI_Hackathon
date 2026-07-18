from backend.services.summary_service import get_summary


def read_summary(
    capability: str = "ICU",
    state: str | None = None,
    city: str | None = None,
) -> dict:
    return get_summary(capability=capability, state=state, city=city)
