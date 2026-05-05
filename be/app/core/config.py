from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # Prefer explicit environment variables (os.getenv) to avoid edge cases
    # with reload subprocesses not picking up .env. Defaults are fallbacks.
    # Výchozí fallback na Postgres; skutečná hodnota se bere z env/.env
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE: str = os.getenv("LOG_FILE", "app.log")
    # Volitelně: seznam tajných jmen/slov pro mini hru, oddělený čárkami
    SECRET_TOKENS: str = os.getenv("SECRET_TOKENS", "")
    # Loki logging configuration
    LOKI_URL: str = os.getenv("LOKI_URL", "")
    APP_NAME: str = os.getenv("APP_NAME", "moje-app-backend")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # OAuth2 JWT Configuration (PKCE)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production-123!")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # CSRF Protection
    CSRF_SECRET_KEY: str = os.getenv("CSRF_SECRET_KEY", "csrf-secret-key-change-in-production!")

    # mTLS Configuration
    FORCE_HTTPS: bool = os.getenv("FORCE_HTTPS", "false").lower() == "true"
    TRUSTED_PROXIES: str = os.getenv("TRUSTED_PROXIES", "")

    # Keep env_file configured for cases where .env should be read directly
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }


settings = Settings()