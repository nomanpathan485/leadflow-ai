from groq import Groq

from app.config import get_settings


def create_groq_client() -> Groq:
    settings = get_settings()

    if (
        settings.groq_api_key is None
        or not settings.groq_api_key.get_secret_value().strip()
    ):
        raise RuntimeError("Groq API key is not configured.")

    return Groq(
        api_key=settings.groq_api_key.get_secret_value(),
        timeout=20.0,
        max_retries=0,
    )