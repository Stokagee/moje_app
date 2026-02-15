# Client Credentials Demo Configuration

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings for Client Credentials Demo"""

    # Database
    DATABASE_URL: str = "sqlite:///./auth_client_credentials.db"

    # JWT Settings
    SECRET_KEY: str = "your-client-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    M2M_TOKEN_EXPIRE_HOURS: int = 1

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Auth Client Credentials Demo (M2M)"

    class Config:
        env_file = ".env"


settings = Settings()
