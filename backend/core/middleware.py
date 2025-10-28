"""
Security middleware for the Comment Widget API
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
import time
import logging
from typing import Callable
from collections import defaultdict
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window"""

    def __init__(self, app, requests_per_window: int = 1000, window_seconds: int = 3600):
        super().__init__(app)
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)  # IP -> list of timestamps

    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)

        # Clean old requests
        current_time = time.time()
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < self.window_seconds
        ]

        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_window:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"error": "Too many requests", "retry_after": self.window_seconds}
            )

        # Add current request
        self.requests[client_ip].append(current_time)

        response = await call_next(request)
        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address, checking for proxies"""
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            # Take the first IP if multiple are present
            return x_forwarded_for.split(",")[0].strip()
        return request.client.host


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Content Security Policy for API
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Enhanced request logging middleware"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger.info(
            "Request started",
            extra={
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host,
                "user_agent": request.headers.get("user-agent", ""),
                "request_id": request.headers.get("x-request-id", "")
            }
        )

        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log response
            logger.info(
                "Request completed",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "process_time": f"{process_time:.3f}s",
                    "client_ip": request.client.host
                }
            )

            # Add processing time header
            response.headers["X-Process-Time"] = f"{process_time:.3f}s"

            return response

        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                "Request failed",
                extra={
                    "method": request.method,
                    "url": str(request.url),
                    "error": str(e),
                    "process_time": f"{process_time:.3f}s",
                    "client_ip": request.client.host
                },
                exc_info=True
            )
            raise


class HealthCheckMiddleware(BaseHTTPMiddleware):
    """Health check middleware that bypasses other middleware"""

    def __init__(self, app, health_check_path: str = "/health"):
        super().__init__(app)
        self.health_check_path = health_check_path

    async def dispatch(self, request: Request, call_next):
        if request.url.path == self.health_check_path:
            # Simple health check response
            return JSONResponse(
                content={
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "service": "comment-widget-api"
                }
            )

        return await call_next(request)


def setup_middleware(app, settings):
    """Setup all middleware for the FastAPI application"""

    # Health check (must be first)
    app.add_middleware(HealthCheckMiddleware)

    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Rate limiting
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_window=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window
    )

    # Request logging
    app.add_middleware(RequestLoggingMiddleware)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        max_age=86400  # 24 hours
    )

    # Trusted hosts (only in production)
    if settings.environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts
        )

    logger.info("Security middleware configured", extra={
        "rate_limit": f"{settings.rate_limit_requests}/{settings.rate_limit_window}s",
        "cors_origins": len(settings.allowed_origins),
        "environment": settings.environment
    })