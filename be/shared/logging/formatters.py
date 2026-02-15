"""
Custom formatters for Loguru logging.

Provides:
- JSON formatter for Loki ingestion
- Console formatters with colors
- Structured log helpers
"""

import json
import sys
from datetime import datetime
from typing import Any, Dict

from loguru import logger


class LokiFormatter:
    """
    Formatter that creates Loki-compatible JSON logs.

    Loki expects a specific JSON structure with stream labels
    and line contents.
    """

    def __init__(self):
        self.service = None
        self.environment = None

    def __call__(self, record: Dict[str, Any]) -> str:
        """Format log record as Loki JSON."""
        # Get stream labels from record (set by logger.py)
        stream_labels = record["extra"].get("stream_labels", {})

        # Build log entry for Loki
        log_entry = {
            "streams": [
                {
                    "stream": stream_labels,
                    "values": [
                        [
                            str(int(record["time"].timestamp() * 1_000_000_000)),  # Nanoseconds
                            self._format_message(record),
                        ]
                    ],
                }
            ]
        }

        return json.dumps(log_entry)

    def _format_message(self, record: Dict[str, Any]) -> str:
        """Format the actual log message with structured data."""
        # Extract important fields
        message_data = {
            "message": record["message"],
            "level": record["level"].name,
            "timestamp": record["time"].isoformat(),
        }

        # Add extra context (excluding stream_labels and Loki internals)
        extra = record["extra"].copy()
        extra.pop("stream_labels", None)

        # Add important context fields
        if "request_id" in extra:
            message_data["request_id"] = extra.pop("request_id")

        if "event_type" in extra:
            message_data["event_type"] = extra.pop("event_type")

        if "logger_name" in extra:
            message_data["logger"] = extra.pop("logger_name")

        # Add any remaining extra fields as structured data
        if extra:
            # Sanitize extra fields (remove sensitive data)
            sanitized = self._sanitize_extra(extra)
            if sanitized:
                message_data["data"] = sanitized

        # Add exception info if present
        if record["exception"]:
            message_data["exception"] = {
                "type": record["exception"].type.__name__,
                "value": str(record["exception"].value),
                "traceback": record["exception"].traceback,
            }

        return json.dumps(message_data)

    def _sanitize_extra(self, extra: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize extra fields to remove sensitive data."""
        sensitive_keys = {
            "password",
            "token",
            "secret",
            "authorization_code",
            "code_verifier",
            "refresh_token",
            "access_token",
            "client_secret",
            "api_key",
        }

        sanitized = {}
        for key, value in extra.items():
            # Check if key contains sensitive keywords
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                # Replace with placeholder
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, str):
                # Check if value looks like a token
                if self._looks_like_token(value):
                    sanitized[key] = self._truncate_token(value)
                else:
                    sanitized[key] = value
            else:
                sanitized[key] = value

        return sanitized

    def _looks_like_token(self, value: str) -> bool:
        """Check if string looks like a JWT token or similar."""
        # JWT tokens have 3 parts separated by dots
        if value.count(".") == 2 and len(value) > 50:
            return True
        # Long hexadecimal strings
        if len(value) > 32 and all(c in "0123456789abcdefABCDEF" for c in value):
            return True
        return False

    def _truncate_token(self, token: str) -> str:
        """Truncate token for logging (first 8 chars + ...)."""
        if len(token) <= 12:
            return "***REDACTED***"
        return token[:8] + "...***"


def sanitize_for_log(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize dictionary before logging to remove sensitive data.

    Safe to log: user_id, client_id, scopes, event_type
    Redacted: passwords, tokens, secrets, codes

    Args:
        data: Dictionary to sanitize

    Returns:
        Sanitized dictionary with sensitive data redacted
    """
    sensitive_keys = {
        "password",
        "token",
        "secret",
        "authorization_code",
        "code_verifier",
        "code_challenge",
        "refresh_token",
        "access_token",
        "client_secret",
        "api_key",
        "bearer",
    }

    result = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            result[key] = "***REDACTED***"
        elif isinstance(value, dict):
            result[key] = sanitize_for_log(value)
        elif isinstance(value, list):
            result[key] = [sanitize_for_log(item) if isinstance(item, dict) else item for item in value]
        elif isinstance(value, str):
            result[key] = _truncate_if_token(value)
        else:
            result[key] = value

    return result


def _truncate_if_token(value: str) -> str:
    """Truncate token-like strings for safe logging."""
    if len(value) > 50 and "." in value and value.count(".") >= 2:
        # Looks like JWT
        return value[:8] + "...***"
    if len(value) > 32 and all(c in "0123456789abcdefABCDEF-_" for c in value):
        # Looks like hex token
        return value[:8] + "...***"
    return value


# OAuth2 specific logging helpers
def log_auth_event(
    event_type: str,
    success: bool,
    auth_flow: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create structured log data for OAuth2 events.

    Args:
        event_type: Type of event (login, token_issued, auth_failed, etc.)
        success: Whether the operation succeeded
        auth_flow: OAuth2 flow type (refresh_token, client_credentials, etc.)
        **kwargs: Additional event-specific fields

    Returns:
        Dictionary ready for logging with extra=
    """
    log_data = {
        "event_type": event_type,
        "auth_flow": auth_flow,
        "success": success,
    }

    # Add optional fields
    safe_fields = [
        "client_id", "user_id", "scope", "scopes", "redirect_uri",
        "state", "response_type", "grant_type", "error", "error_description",
        "ip_address", "endpoint", "method", "status_code", "duration_ms"
    ]

    for field in safe_fields:
        if field in kwargs:
            if field in ("scope", "scopes"):
                # Scopes are safe to log
                log_data[field] = kwargs[field]
            elif field == "client_id":
                # Client IDs are safe to log
                log_data[field] = kwargs[field]
            elif field == "user_id":
                # User IDs are safe to log
                log_data[field] = kwargs[field]
            elif field == "error":
                # Error descriptions are safe
                log_data[field] = kwargs[field]
            elif field == "ip_address":
                # Per user preference, IP addresses are safe to log
                log_data[field] = kwargs[field]
            else:
                log_data[field] = kwargs[field]

    return log_data


def log_token_issued(
    token_type: str,
    auth_flow: str,
    expires_in: int,
    **kwargs
) -> Dict[str, Any]:
    """
    Create structured log data for token issuance.

    Note: Never logs actual tokens, only metadata.

    Args:
        token_type: Type of token (access, refresh, id_token)
        auth_flow: OAuth2 flow type
        expires_in: Token expiration in seconds
        **kwargs: Additional fields (client_id, user_id, scopes, etc.)

    Returns:
        Dictionary ready for logging with extra=
    """
    log_data = {
        "event_type": "token_issued",
        "token_type": token_type,
        "auth_flow": auth_flow,
        "expires_in": expires_in,
        "success": True,
    }

    # Add safe metadata
    if "client_id" in kwargs:
        log_data["client_id"] = kwargs["client_id"]
    if "user_id" in kwargs:
        log_data["user_id"] = kwargs["user_id"]
    if "scopes" in kwargs or "scope" in kwargs:
        log_data["scopes"] = kwargs.get("scopes", kwargs.get("scope"))

    return log_data
