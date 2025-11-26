"""
Loguru logging s přímým posíláním do Loki.

Použití:
    from app.core.logging import logger

    logger.info("Zpráva")
    logger.warning("Varování")
    logger.error("Chyba")
"""
import sys
import os
from loguru import logger

# Odeber defaultní handler
logger.remove()

# === Console handler (vždy) ===
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=os.getenv("LOG_LEVEL", "INFO"),
    colorize=True,
)

# === Loki handler (pokud je URL nastavena) ===
LOKI_URL = os.getenv("LOKI_URL")

if LOKI_URL:
    from loki_logger_handler.loki_logger_handler import LokiLoggerHandler
    from loki_logger_handler.formatters.loguru_formatter import LoguruFormatter

    loki_handler = LokiLoggerHandler(
        url=LOKI_URL,
        labels={
            "application": os.getenv("APP_NAME", "moje-app"),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "service": "backend",
        },
        label_keys={},
        timeout=10,
        default_formatter=LoguruFormatter(),
    )

    logger.add(
        loki_handler,
        serialize=True,
        level=os.getenv("LOG_LEVEL", "INFO"),
    )
    logger.info("Loki logging enabled", loki_url=LOKI_URL)
else:
    logger.warning("LOKI_URL not set - logging only to console")


def setup_logging():
    """Dummy funkce pro zpětnou kompatibilitu s main.py."""
    pass


def get_logger(name: str = None):
    """Získej logger s kontextem."""
    if name:
        return logger.bind(module=name)
    return logger
