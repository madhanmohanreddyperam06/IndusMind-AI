from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class RootResponse(BaseModel):
    """Root endpoint response model."""
    message: str
    version: str
    service: str
    documentation: str


@router.get("/", response_model=RootResponse)
async def root():
    """Root endpoint."""
    from app.config.settings import settings
    
    return RootResponse(
        message="Welcome to IndusMind AI - Industrial Knowledge Intelligence Platform",
        version=settings.app_version,
        service=settings.app_name,
        documentation="/docs"
    )
