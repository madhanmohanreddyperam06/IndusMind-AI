"""Centralized exception handling for the application.

This module provides a consistent error response format across all endpoints.
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from typing import Any, Dict, Optional
import uuid
import logging

logger = logging.getLogger(__name__)


class ErrorResponse:
    """Standard error response format."""
    
    def __init__(
        self,
        success: bool = False,
        error_code: str = "INTERNAL_ERROR",
        message: str = "An unexpected error occurred",
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        self.success = success
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.timestamp = timestamp
        self.request_id = request_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
            "request_id": self.request_id
        }


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent format."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    error_code = "HTTP_ERROR"
    if exc.status_code == status.HTTP_400_BAD_REQUEST:
        error_code = "BAD_REQUEST"
    elif exc.status_code == status.HTTP_401_UNAUTHORIZED:
        error_code = "UNAUTHORIZED"
    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        error_code = "FORBIDDEN"
    elif exc.status_code == status.HTTP_404_NOT_FOUND:
        error_code = "NOT_FOUND"
    elif exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        error_code = "VALIDATION_ERROR"
    elif exc.status_code >= 500:
        error_code = "SERVER_ERROR"
    
    error_response = ErrorResponse(
        error_code=error_code,
        message=exc.detail,
        request_id=request_id
    )
    
    logger.error(
        f"HTTP Exception: {error_code} - {exc.detail} - Request ID: {request_id} - Path: {request.url.path}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.to_dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation exceptions."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    # Format validation errors
    validation_details = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        validation_details[field] = error["msg"]
    
    error_response = ErrorResponse(
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        details={"validation_errors": validation_details},
        request_id=request_id
    )
    
    logger.warning(
        f"Validation Error: Request ID: {request_id} - Path: {request.url.path} - Errors: {validation_details}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.to_dict()
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation exceptions."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    error_response = ErrorResponse(
        error_code="VALIDATION_ERROR",
        message="Data validation failed",
        details={"validation_errors": exc.errors()},
        request_id=request_id
    )
    
    logger.warning(
        f"Pydantic Validation Error: Request ID: {request_id} - Path: {request.url.path}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.to_dict()
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database exceptions."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    error_response = ErrorResponse(
        error_code="DATABASE_ERROR",
        message="A database error occurred",
        details={"error_type": type(exc).__name__},
        request_id=request_id
    )
    
    logger.error(
        f"Database Exception: {type(exc).__name__} - Request ID: {request_id} - Path: {request.url.path}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.to_dict()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other unexpected exceptions."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    error_response = ErrorResponse(
        error_code="INTERNAL_ERROR",
        message="An unexpected error occurred",
        details={"error_type": type(exc).__name__},
        request_id=request_id
    )
    
    logger.error(
        f"Unhandled Exception: {type(exc).__name__} - {str(exc)} - Request ID: {request_id} - Path: {request.url.path}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.to_dict()
    )


def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI application."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
