"""
Shared logger configuration using Loguru with Loki integration.

Provides structured logging with:
- Colored console output for development
- JSON logging to Loki for production
- Automatic context binding (request_id, user_id, etc.)
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger

from .formatters import LokiFormatter

# Environment configuration
LOKI_URL = os.getenv("LOKI_URL", "http://loki:3100/loki/api/v1/push")
APP_NAME = os.getenv("APP_NAME", "unknown-service")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def get_logger(name: Optional[str] = None) -> Any:
    """
    Get a configured logger instance.

    Args:
        name: Optional logger name (defaults to module name)

    Returns:
        Loguru logger with context binding
    """
    if name:
        return logger.bind(logger_name=name)
    return logger


def setup_logging() -> None:
    """
    Configure Loguru with console and Loki handlers.

    Should be called once at application startup.
    """
    # Remove default handler
    logger.remove()

    # Common labels for all logs
    common_labels = {
        "service": APP_NAME,
        "environment": ENVIRONMENT,
    }

    # Console handler - colored, human-readable for development
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[service]}</cyan>:<cyan>{extra[logger_name]}</cyan> | "
            "<yellow>{extra[request_id]}</yellow> | "
            "<level>{message}</level>"
        ),
        level=LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True,
        enqueue=True,  # Thread-safe
        **{"filter": lambda record: _update_record(record, common_labels)},
    )

    # Loki handler - JSON structured logs for Grafana
    # Use a custom sink function to send logs to Loki via HTTP
    def loki_sink(message):
        """Custom sink that sends log records to Loki via HTTP."""
        import httpx
        import json

        # Parse the log record
        record = message.record
        _update_record_loki(record, common_labels)

        # Build Loki payload
        stream = record["extra"].get("stream_labels", {
            "service": APP_NAME,
            "environment": ENVIRONMENT,
            "level": record["level"].name,
        })

        # Loki expects nanosecond timestamps
        timestamp_ns = int(record["time"].timestamp() * 1_000_000_000)

        payload = {
            "streams": [
                {
                    "stream": stream,
                    "values": [
                        [str(timestamp_ns), str(message).strip()]
                    ]
                }
            ]
        }

        # Send to Loki (fire and forget, non-blocking)
        try:
            import threading
            threading.Thread(
                target=_send_to_loki,
                args=(payload,),
                daemon=True
            ).start()
        except Exception:
            pass  # Silently fail to avoid breaking the app

    logger.add(
        loki_sink,
        format="{message}",  # We'll format in the sink
        level=LOG_LEVEL,
        serialize=False,  # We'll handle JSON in the sink
        backtrace=True,
        diagnose=True,
        enqueue=True,
        catch=True,  # Don't break if Loki fails
    )

    logger.info(f"Logging initialized: {APP_NAME} in {ENVIRONMENT} environment")


def _update_record(record: Dict[str, Any], labels: Dict[str, str]) -> bool:
    """Add common labels to console records."""
    record["extra"].update(labels)
    if "request_id" not in record["extra"]:
        record["extra"]["request_id"] = "N/A"
    if "logger_name" not in record["extra"]:
        record["extra"]["logger_name"] = "root"
    return True


def _update_record_loki(record: Dict[str, Any], labels: Dict[str, str]) -> bool:
    """
    Prepare record for Loki with proper JSON structure.

    Loki expects structured logs with labels at the root level.
    """
    # Add common labels
    record["extra"].update(labels)

    # Ensure request_id exists
    if "request_id" not in record["extra"]:
        record["extra"]["request_id"] = "N/A"

    # Ensure logger_name exists
    if "logger_name" not in record["extra"]:
        record["extra"]["logger_name"] = "root"

    # Move important fields to Loki stream labels
    # These become queryable filters in Grafana
    stream_labels = {
        "service": labels["service"],
        "environment": labels["environment"],
        "level": record["level"].name,
    }

    # Add optional labels if present
    if "event_type" in record["extra"]:
        stream_labels["event_type"] = str(record["extra"]["event_type"])

    if "auth_flow" in record["extra"]:
        stream_labels["auth_flow"] = str(record["extra"]["auth_flow"])

    if "endpoint" in record["extra"]:
        stream_labels["endpoint"] = str(record["extra"]["endpoint"])

    if "client_id" in record["extra"]:
        stream_labels["client_id"] = str(record["extra"]["client_id"])

    # Store stream labels for Loki formatter
    record["extra"]["stream_labels"] = stream_labels

    return True


def _send_to_loki(payload: Dict[str, Any]) -> None:
    """Send log payload to Loki via HTTP."""
    import httpx

    try:
        response = httpx.post(
            LOKI_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5.0,
        )
        response.raise_for_status()
    except Exception:
        # Silently fail to avoid breaking the app
        pass


class InterceptHandler(logging.Handler):
    """
    Intercept standard logging messages and redirect to Loguru.

    This allows all existing code using `logging.getLogger()` to work
    with Loguru without modification.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to Loguru."""
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def intercept_standard_logging() -> None:
    """
    Intercept all standard Python logging and redirect to Loguru.

    Call this after setup_logging() to capture logs from libraries
    that use standard logging (SQLAlchemy, FastAPI, etc.).
    """
    # Configure standard logging to use our intercept handler
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Intercept specific loggers
    for name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi", "sqlalchemy"]:
        logging_logger = logging.getLogger(name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False

    logger.info("Standard logging intercepted and redirected to Loguru")
