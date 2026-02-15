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

    # Keep env_file configured for cases where .env should be read directly
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }


settings = Settings()