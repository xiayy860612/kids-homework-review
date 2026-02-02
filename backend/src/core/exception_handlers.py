"""Global exception handlers for the FastAPI application."""

import logging
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from src.core.exceptions import AppException

# Configure logger
logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions.

    Args:
        request: The incoming request
        exc: The application exception

    Returns:
        JSONResponse: Formatted error response
    """
    # Log the error with context
    logger.error(
        "AppException: %s - Path: %s - Details: %s",
        exc.message,
        request.url.path,
        exc.details,
        exc_info=True,
    )

    # Build error response
    error_content: dict[str, Any] = {
        "error": {
            "message": exc.message,
            "type": exc.__class__.__name__,
        }
    }

    # Add details if present (only in non-production)
    if exc.details:
        error_content["error"]["details"] = exc.details

    return JSONResponse(
        status_code=exc.status_code,
        content=error_content,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTPException.

    Args:
        request: The incoming request
        exc: The HTTP exception

    Returns:
        JSONResponse: Formatted error response
    """
    # Log HTTP errors (4xx client errors, 5xx server errors)
    log_level = logging.WARNING if exc.status_code < 500 else logging.ERROR
    logger.error(
        log_level,
        "HTTPException: %s - Path: %s - Status: %s",
        exc.detail,
        request.url.path,
        exc.status_code,
        exc_info=True
    )

    # Build error response
    error_content: dict[str, Any] = {
        "error": {
            "message": str(exc.detail),
            "type": "HTTPException",
        }
    }

    return JSONResponse(
        status_code=exc.status_code,
        content=error_content,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors.

    Args:
        request: The incoming request
        exc: The validation error

    Returns:
        JSONResponse: Formatted error response with validation details
    """
    # Log validation errors
    logger.warning(
        "Validation error - Path: %s - Errors: %s",
        request.url.path,
        exc.errors(),
    )

    # Format validation errors for better readability
    formatted_errors: list[dict[str, Any]] = []
    for error in exc.errors():
        formatted_errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })

    error_content: dict[str, Any] = {
        "error": {
            "message": "Validation failed",
            "type": "ValidationError",
            "details": formatted_errors,
        }
    }

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_content,
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Handle SQLAlchemy database integrity errors.

    Args:
        request: The incoming request
        exc: The integrity error

    Returns:
        JSONResponse: Formatted error response
    """
    # Log database integrity errors
    logger.error(
        "Database integrity error - Path: %s - Error: %s",
        request.url.path,
        str(exc.orig),
        exc_info=True,
    )

    # Extract useful information from the error message
    error_message = "Database integrity constraint violated"
    error_detail = str(exc.orig) if exc.orig else "Unknown constraint violation"

    error_content: dict[str, Any] = {
        "error": {
            "message": error_message,
            "type": "DatabaseIntegrityError",
            "details": {"constraint": error_detail},
        }
    }

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=error_content,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions.

    This is the catch-all handler for any exception not explicitly handled.

    Args:
        request: The incoming request
        exc: The unhandled exception

    Returns:
        JSONResponse: Generic error response
    """
    # Log all details for debugging
    logger.exception(
        "Unhandled exception: %s - Path: %s - Type: %s",
        str(exc),
        request.url.path,
        type(exc).__name__,
    )

    # Generic error message (don't expose internal details)
    error_content: dict[str, Any] = {
        "error": {
            "message": "An unexpected error occurred",
            "type": "InternalServerError",
        }
    }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_content,
    )


def register_exception_handlers(app) -> None:
    """Register all exception handlers with the FastAPI application.

    Args:
        app: The FastAPI application instance
    """
    # Custom application exceptions
    app.add_exception_handler(AppException, app_exception_handler)

    # FastAPI HTTPException (for consistent error format)
    app.add_exception_handler(HTTPException, http_exception_handler)

    # Pydantic validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # SQLAlchemy integrity errors
    app.add_exception_handler(IntegrityError, integrity_error_handler)

    # Catch-all for any unhandled exceptions
    app.add_exception_handler(Exception, generic_exception_handler)
