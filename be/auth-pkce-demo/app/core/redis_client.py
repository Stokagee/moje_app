# Redis client for storing authorization codes

import redis
import json
from app.core.config import settings


# Initialize Redis client
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def save_authorization_code(code: str, data: dict, expire_seconds: int = None):
    """
    Save authorization code to Redis with expiration.

    Args:
        code: Authorization code
        data: Data to store (user_id, client_id, scopes, code_challenge)
        expire_seconds: Expiration time in seconds (default from settings)
    """
    if expire_seconds is None:
        expire_seconds = settings.AUTH_CODE_EXPIRE_SECONDS

    redis_client.setex(
        f"auth_code:{code}",
        expire_seconds,
        json.dumps(data)
    )


def get_authorization_code(code: str) -> dict | None:
    """
    Get authorization code data from Redis.

    Args:
        code: Authorization code

    Returns:
        Data dict if found, None otherwise
    """
    data = redis_client.get(f"auth_code:{code}")
    if data:
        return json.loads(data)
    return None


def delete_authorization_code(code: str):
    """
    Delete authorization code from Redis (single use).

    Args:
        code: Authorization code
    """
    redis_client.delete(f"auth_code:{code}")


def check_redis_connection() -> bool:
    """
    Check if Redis connection is alive.

    Returns:
        True if connected, False otherwise
    """
    try:
        redis_client.ping()
        return True
    except redis.ConnectionError:
        return False
