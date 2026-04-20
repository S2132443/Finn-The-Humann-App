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
    
    # CORS (comma-separated). Production is same-origin, so this matters only in dev.
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

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
