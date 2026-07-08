from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    service: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    from app.config.settings import settings
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        service=settings.app_name
    )
