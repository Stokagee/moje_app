# Configuration settings for PKCE Demo

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings for PKCE Demo"""

    # Database
    DATABASE_URL: str = "sqlite:///./data/auth_pkce.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "auth-pkce-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    AUTH_CODE_EXPIRE_SECONDS: int = 600  # 10 minutes

    # OAuth2 Settings
    ALLOWED_REDIRECT_URIS: list = [
        "http://localhost:3000/callback",
        "http://localhost:4000/callback",
    ]

    # CORS
    CORS_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
