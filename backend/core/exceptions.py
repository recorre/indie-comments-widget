"""
Custom exception classes for consistent error handling across the application.
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException


class CommentWidgetException(Exception):
    """Base exception for Comment Widget application"""

    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(CommentWidgetException):
    """Authentication related errors"""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details)


class AuthorizationError(CommentWidgetException):
    """Authorization related errors"""

    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)


class ValidationError(CommentWidgetException):
    """Data validation errors"""

    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class NotFoundError(CommentWidgetException):
    """Resource not found errors"""

    def __init__(self, resource: str, resource_id: Optional[Any] = None, details: Optional[Dict[str, Any]] = None):
        message = f"{resource} not found"
        if resource_id:
            message += f" with id {resource_id}"
        super().__init__(message, status_code=404, details=details)


class ExternalServiceError(CommentWidgetException):
    """External service (NoCodeBackend) errors"""

    def __init__(self, service: str, message: str, status_code: int = 502, details: Optional[Dict[str, Any]] = None):
        full_message = f"{service} service error: {message}"
        super().__init__(full_message, status_code=status_code, details=details)


class ConfigurationError(CommentWidgetException):
    """Configuration related errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


def create_http_exception(exception: CommentWidgetException) -> HTTPException:
    """Convert custom exception to FastAPI HTTPException"""
    return HTTPException(
        status_code=exception.status_code,
        detail={
            "error": exception.message,
            "details": exception.details
        }
    )