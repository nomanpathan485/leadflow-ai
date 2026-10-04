from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "LeadFlow AI"
    database_url: SecretStr = Field(min_length=1)
    groq_api_key: SecretStr | None = None
    groq_model: str = "llama-3.1-8b-instant"
    n8n_webhook_url: str = (
        "http://n8n:5678/webhook/leadflow-new-enquiry"
    )
    n8n_webhook_secret: SecretStr


@lru_cache
def get_settings() -> Settings:
    return Settings()