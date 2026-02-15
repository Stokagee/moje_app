# Refresh Token Demo Configuration

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings for Refresh Token Demo"""

    # Database
    DATABASE_URL: str = "sqlite:///./auth_refresh.db"

    # JWT Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Auth Refresh Token Demo"

    class Config:
        env_file = ".env"


settings = Settings()
