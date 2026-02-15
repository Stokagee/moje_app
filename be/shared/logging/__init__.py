"""
Shared logging module for all services.

Provides centralized logging configuration with Loguru and Loki integration.

IMPORTANT: Import functions directly from submodules:
- from shared.logging.logger import get_logger, setup_logging
- from shared.logging.middleware import LoggingMiddleware

Do NOT import from this __init__.py directly to avoid circular import issues.
"""
