"""Custom exception classes for the application."""

from typing import Any


class AppException(Exception):
    """Base exception class for all application errors.

    Attributes:
        message: Human-readable error message
        status_code: HTTP status code to return
        details: Additional error details for debugging
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            status_code: HTTP status code to return
            details: Additional error details for debugging
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class AuthenticationException(AppException):
    """Exception raised for authentication failures.

    Used when user credentials are invalid or authentication fails.
    """

    def __init__(self, message: str = "Authentication failed", details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            details: Additional error details for debugging
        """
        super().__init__(message, status_code=401, details=details)


class AuthorizationException(AppException):
    """Exception raised for authorization failures.

    Used when user lacks permission to perform an action.
    """

    def __init__(self, message: str = "Insufficient permissions", details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            details: Additional error details for debugging
        """
        super().__init__(message, status_code=403, details=details)


class NotFoundException(AppException):
    """Exception raised when a resource is not found.

    Used when requested resource does not exist.
    """

    def __init__(self, message: str = "Resource not found", details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            details: Additional error details for debugging
        """
        super().__init__(message, status_code=404, details=details)


class ConflictException(AppException):
    """Exception raised when a conflict occurs.

    Used when creating a resource that conflicts with existing data,
    such as duplicate username or email.
    """

    def __init__(self, message: str = "Resource conflict", details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            details: Additional error details for debugging
        """
        super().__init__(message, status_code=409, details=details)


class BadRequestException(AppException):
    """Exception raised for bad requests.

    Used when the request is malformed or contains invalid data.
    """

    def __init__(self, message: str = "Bad request", details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            details: Additional error details for debugging
        """
        super().__init__(message, status_code=400, details=details)


class ValidationException(AppException):
    """Exception raised for validation errors.

    Used when input data fails validation rules.
    """

    def __init__(self, message: str = "Validation failed", details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            details: Additional error details for debugging
        """
        super().__init__(message, status_code=422, details=details)


class ExternalServiceException(AppException):
    """Exception raised when external service calls fail.

    Used when AI API or other external services are unavailable or return errors.
    """

    def __init__(self, message: str = "External service error", details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            details: Additional error details for debugging
        """
        super().__init__(message, status_code=502, details=details)


class DatabaseException(AppException):
    """Exception raised for database operation failures.

    Used when database operations fail unexpectedly.
    """

    def __init__(self, message: str = "Database error", details: dict[str, Any] | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            details: Additional error details for debugging
        """
        super().__init__(message, status_code=500, details=details)
