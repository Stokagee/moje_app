# Redis client for Authorization Code Demo

import redis
from app.core.config import settings

# Create Redis client
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)


def save_authorization_code(code: str, data: dict, expire_seconds: int = None):
    """Save authorization code to Redis with expiration"""
    import json

    if expire_seconds is None:
        expire_seconds = settings.AUTH_CODE_EXPIRE_SECONDS

    key = f"auth_code:{code}"
    value = json.dumps(data)

    redis_client.setex(key, expire_seconds, value)


def get_authorization_code(code: str) -> dict | None:
    """Get authorization code data from Redis"""
    import json

    key = f"auth_code:{code}"
    value = redis_client.get(key)

    if value:
        return json.loads(value)
    return None


def delete_authorization_code(code: str):
    """Delete authorization code from Redis (single use)"""
    key = f"auth_code:{code}"
    redis_client.delete(key)


def save_state(state: str, data: dict, expire_seconds: int = 600):
    """Save state parameter to Redis for CSRF protection"""
    import json

    key = f"state:{state}"
    value = json.dumps(data)

    redis_client.setex(key, expire_seconds, value)


def validate_state(state: str) -> bool:
    """Validate state parameter"""
    key = f"state:{state}"
    exists = redis_client.exists(key)
    redis_client.delete(key)  # Single use
    return exists
