from fastapi import Request
import logging

logger = logging.getLogger(__name__)


async def log_requests(request: Request, call_next):
    """Log all requests. Placeholder for future implementation."""
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    logger.info(f"Response: {response.status_code}")
    
    return response
