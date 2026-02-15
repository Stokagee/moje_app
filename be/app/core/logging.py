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
            "service": os.getenv("APP_NAME", "moje-app"),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "application": os.getenv("APP_NAME", "moje-app"),
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
    """
    Setup logging including interception of standard logging.

    Redirects all standard logging (logging.getLogger) to Loguru
    so that existing code works with Loki without modification.
    """
    import logging

    class InterceptHandler(logging.Handler):
        """Intercept standard logging and send to Loguru."""

        def emit(self, record):
            # Get corresponding Loguru level
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    # Configure standard logging to use intercept handler
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Intercept specific loggers
    for name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi", "sqlalchemy"]:
        logging_logger = logging.getLogger(name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False

    logger.info("Standard logging intercepted and redirected to Loguru")


def get_logger(name: str = None):
    """Získej logger s kontextem."""
    if name:
        return logger.bind(module=name)
    return logger
