"""API routes for Admin Dashboard."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.api.dependencies import get_current_active_user
from app.api.authorization import require_superuser
from app.models.user import User
from app.services.admin import AdminService
from app.schemas.admin import DashboardStats, SystemHealth, UserSummary, RoleSummary
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()


def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    """Dependency to get admin service."""
    return AdminService(db)


@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(
    service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(require_superuser())
):
    """Get dashboard statistics (superuser only)."""
    try:
        return service.get_dashboard_stats()
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get dashboard stats")


@router.get("/system/health", response_model=SystemHealth)
def get_system_health(
    service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(require_superuser())
):
    """Get system health status (superuser only)."""
    try:
        return service.get_system_health()
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get system health")


@router.get("/users/summary", response_model=List[UserSummary])
def get_user_summaries(
    skip: int = 0,
    limit: int = 10,
    service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(require_superuser())
):
    """Get user summaries for dashboard (superuser only)."""
    try:
        return service.get_user_summaries(skip, limit)
    except Exception as e:
        logger.error(f"Error getting user summaries: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get user summaries")


@router.get("/roles/summary", response_model=List[RoleSummary])
def get_role_summaries(
    skip: int = 0,
    limit: int = 10,
    service: AdminService = Depends(get_admin_service),
    current_user: User = Depends(require_superuser())
):
    """Get role summaries for dashboard (superuser only)."""
    try:
        return service.get_role_summaries(skip, limit)
    except Exception as e:
        logger.error(f"Error getting role summaries: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get role summaries")
