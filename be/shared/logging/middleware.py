"""
FastAPI middleware for request logging and tracing.

Provides automatic request tracking with:
- Request ID generation (UUID)
- Request timing (duration_ms)
- Request/response logging
- Context binding for all logs in request scope
"""

import time
import uuid
from typing import Callable, Awaitable, Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses.

    Adds request_id to context for log correlation and logs
    request/response details with timing information.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.app = app

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request and log details."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]

        # Bind request_id to logger context for all logs in this request
        logger_context = logger.bind(request_id=request_id)

        # Start timing
        start_time = time.time()

        # Extract client info
        client_host = request.client.host if request.client else "unknown"

        # Log incoming request
        logger_context.debug(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                "event_type": "http_request",
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_host": client_host,
                "user_agent": request.headers.get("user-agent", "unknown"),
            },
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log response
            log_level = "warning" if response.status_code >= 400 else "info"
            log_level = "error" if response.status_code >= 500 else log_level

            getattr(logger_context, log_level)(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "event_type": "http_response",
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                    "success": response.status_code < 400,
                },
            )

            # Add request_id to response header for debugging
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Calculate duration even for errors
            duration_ms = (time.time() - start_time) * 1000

            logger_context.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "event_type": "http_error",
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
                exc_info=True,
            )
            raise


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Lightweight middleware that only adds request_id to context.

    Use this if you want request tracking but less verbose logging.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Add request_id to logger context."""
        request_id = str(uuid.uuid4())[:8]

        # Context with request_id
        with logger.contextualize(request_id=request_id):
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
