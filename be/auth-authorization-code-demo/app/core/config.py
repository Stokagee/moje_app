# Authorization Code Demo Configuration

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings for Authorization Code Demo"""

    # Database
    DATABASE_URL: str = "sqlite:///./auth_auth_code.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT Settings
    SECRET_KEY: str = "your-auth-code-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # OAuth2 Settings
    AUTH_CODE_EXPIRE_SECONDS: int = 600  # 10 minutes

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Auth Authorization Code Demo"

    # Allowed redirect URIs
    ALLOWED_REDIRECT_URIS: list[str] = [
        "http://localhost:3000/callback",
        "http://localhost:8080/callback",
        "http://localhost:3001/callback"
    ]

    class Config:
        env_file = ".env"


settings = Settings()
