"""Settings for dds_glossary package."""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for dds_glossary package."""

    API_KEY: SecretStr
    DATABASE_URL: SecretStr
    SENTRY_DSN: SecretStr = SecretStr("")

    HOST_IP: str = "127.0.0.1"


@lru_cache()
def get_settings():
    """Returns settings object."""
    return Settings()
