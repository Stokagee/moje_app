"""
Konfigurace pro Auth Demo aplikaci.
Načítá hodnoty z .env souboru.
"""
import os
from dotenv import load_dotenv

# Načti .env soubor
load_dotenv()

# Databáze
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/moje_app")

# JWT konfigurace
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-production-123!")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Session konfigurace
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "session_id")
SESSION_MAX_AGE = int(os.getenv("SESSION_MAX_AGE", "3600"))

# OAuth2 konfigurace
OAUTH2_CLIENT_ID = os.getenv("OAUTH2_CLIENT_ID", "my-app-client")
OAUTH2_CLIENT_SECRET = os.getenv("OAUTH2_CLIENT_SECRET", "my-app-secret")

# Defaultní admin účet
DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")
