"""API routes for System Monitoring."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.api.dependencies import get_current_active_user
from app.api.authorization import require_superuser
from app.models.user import User
from app.services.monitoring import MonitoringService
from app.schemas.monitoring import (
    SystemMetrics,
    DatabaseMetrics,
    Neo4jMetrics,
    QdrantMetrics,
    AIProviderMetrics,
    StorageMetrics,
    APIMetrics,
    MonitoringDashboard
)
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()


def get_monitoring_service(db: Session = Depends(get_db)) -> MonitoringService:
    """Dependency to get monitoring service."""
    return MonitoringService(db)


@router.get("/dashboard", response_model=MonitoringDashboard)
def get_monitoring_dashboard(
    service: MonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(require_superuser())
):
    """Get comprehensive monitoring dashboard (superuser only)."""
    try:
        return service.get_monitoring_dashboard()
    except Exception as e:
        logger.error(f"Error getting monitoring dashboard: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get monitoring dashboard")


@router.get("/system", response_model=SystemMetrics)
def get_system_metrics(
    service: MonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(require_superuser())
):
    """Get system metrics (superuser only)."""
    try:
        return service.get_system_metrics()
    except Exception as e:
        logger.error(f"Error getting system metrics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get system metrics")


@router.get("/database", response_model=DatabaseMetrics)
def get_database_metrics(
    service: MonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(require_superuser())
):
    """Get database metrics (superuser only)."""
    try:
        return service.get_database_metrics()
    except Exception as e:
        logger.error(f"Error getting database metrics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get database metrics")


@router.get("/neo4j", response_model=Neo4jMetrics)
def get_neo4j_metrics(
    service: MonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(require_superuser())
):
    """Get Neo4j metrics (superuser only)."""
    try:
        metrics = service.get_neo4j_metrics()
        if metrics is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Neo4j is not configured")
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Neo4j metrics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get Neo4j metrics")


@router.get("/qdrant", response_model=QdrantMetrics)
def get_qdrant_metrics(
    service: MonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(require_superuser())
):
    """Get Qdrant metrics (superuser only)."""
    try:
        metrics = service.get_qdrant_metrics()
        if metrics is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Qdrant is not configured")
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Qdrant metrics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get Qdrant metrics")


@router.get("/ai-provider", response_model=AIProviderMetrics)
def get_ai_provider_metrics(
    service: MonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(require_superuser())
):
    """Get AI provider metrics (superuser only)."""
    try:
        return service.get_ai_provider_metrics()
    except Exception as e:
        logger.error(f"Error getting AI provider metrics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get AI provider metrics")


@router.get("/storage", response_model=StorageMetrics)
def get_storage_metrics(
    service: MonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(require_superuser())
):
    """Get storage metrics (superuser only)."""
    try:
        return service.get_storage_metrics()
    except Exception as e:
        logger.error(f"Error getting storage metrics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get storage metrics")


@router.get("/api", response_model=list[APIMetrics])
def get_api_metrics(
    service: MonitoringService = Depends(get_monitoring_service),
    current_user: User = Depends(require_superuser())
):
    """Get API metrics (superuser only)."""
    try:
        return service.get_api_metrics()
    except Exception as e:
        logger.error(f"Error getting API metrics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get API metrics")
