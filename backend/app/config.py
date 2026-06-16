"""Application configuration settings."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@db:5432/finn_db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # Application
    APP_NAME: str = "Finn Investment Tracker"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Currency
    BASE_CURRENCY: str = "MYR"

    # CORS
    CORS_ORIGINS: list = ["http://localhost:5000", "http://127.0.0.1:5000"]

    # Broker API keys (all optional — app works without them)
    LUNO_API_KEY_ID: str = ""
    LUNO_API_KEY_SECRET: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
