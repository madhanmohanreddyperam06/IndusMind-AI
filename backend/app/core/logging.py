import logging
import sys
import time
import uuid
from pathlib import Path
from typing import Optional
from app.config.settings import settings


def setup_logging():
    """Configure application logging with structured format."""
    # Create logs directory if it doesn't exist
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging with structured format
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(settings.log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)


class RequestLogger:
    """Context manager for logging request processing time and details."""
    
    def __init__(self, logger: logging.Logger, request_id: Optional[str] = None):
        self.logger = logger
        self.request_id = request_id or str(uuid.uuid4())
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Request started - Request ID: {self.request_id}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type is None:
            self.logger.info(
                f"Request completed - Request ID: {self.request_id} - Duration: {duration:.3f}s"
            )
        else:
            self.logger.error(
                f"Request failed - Request ID: {self.request_id} - Duration: {duration:.3f}s - Error: {exc_val}"
            )
        return False


def log_request(logger: logging.Logger, method: str, path: str, request_id: Optional[str] = None):
    """Log incoming request details."""
    logger.info(f"{method} {path} - Request ID: {request_id or 'N/A'}")


def log_response(
    logger: logging.Logger,
    status_code: int,
    path: str,
    request_id: Optional[str] = None,
    duration: Optional[float] = None
):
    """Log response details."""
    duration_str = f"{duration:.3f}s" if duration else "N/A"
    log_level = logger.warning if status_code >= 400 else logger.info
    log_level(
        f"Response: {status_code} - Path: {path} - Request ID: {request_id or 'N/A'} - Duration: {duration_str}"
    )


def log_error(logger: logging.Logger, error: Exception, request_id: Optional[str] = None, context: Optional[dict] = None):
    """Log error with context."""
    context_str = f" - Context: {context}" if context else ""
    logger.error(
        f"Error: {type(error).__name__} - {str(error)} - Request ID: {request_id or 'N/A'}{context_str}",
        exc_info=True
    )


def log_warning(logger: logging.Logger, message: str, request_id: Optional[str] = None, context: Optional[dict] = None):
    """Log warning with context."""
    context_str = f" - Context: {context}" if context else ""
    logger.warning(
        f"Warning: {message} - Request ID: {request_id or 'N/A'}{context_str}"
    )


def log_startup(logger: logging.Logger, app_name: str, app_version: str):
    """Log application startup."""
    logger.info(f"Starting {app_name} v{app_version}")


def log_shutdown(logger: logging.Logger, app_name: str):
    """Log application shutdown."""
    logger.info(f"Shutting down {app_name}")


def log_database_operation(
    logger: logging.Logger,
    operation: str,
    table: str,
    request_id: Optional[str] = None,
    duration: Optional[float] = None
):
    """Log database operation."""
    duration_str = f"{duration:.3f}s" if duration else "N/A"
    logger.debug(
        f"DB Operation: {operation} on {table} - Request ID: {request_id or 'N/A'} - Duration: {duration_str}"
    )


def log_external_service_call(
    logger: logging.Logger,
    service: str,
    operation: str,
    request_id: Optional[str] = None,
    duration: Optional[float] = None,
    success: bool = True
):
    """Log external service call."""
    duration_str = f"{duration:.3f}s" if duration else "N/A"
    status = "SUCCESS" if success else "FAILED"
    log_level = logger.info if success else logger.warning
    log_level(
        f"External Service: {service} - {operation} - Status: {status} - Request ID: {request_id or 'N/A'} - Duration: {duration_str}"
    )

