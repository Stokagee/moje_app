"""
Konfigurace pro Auth Demo aplikaci.
"""
import os

# JWT konfigurace
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-production-123!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Session konfigurace
SESSION_COOKIE_NAME = "session_id"
SESSION_MAX_AGE = 3600  # 1 hodina v sekundách
