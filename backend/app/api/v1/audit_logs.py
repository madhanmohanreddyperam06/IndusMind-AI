"""API routes for Audit Logs."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.api.dependencies import get_current_active_user
from app.api.authorization import require_permission
from app.models.user import User
from app.services.audit_log import AuditLogService
from app.schemas.audit_log import AuditLogResponse, AuditLogSearchFilters
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()


def get_audit_log_service(db: Session = Depends(get_db)) -> AuditLogService:
    """Dependency to get audit log service."""
    return AuditLogService(db)


@router.get("", response_model=List[AuditLogResponse])
def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    service: AuditLogService = Depends(get_audit_log_service),
    current_user: User = Depends(require_permission("audit", "read"))
):
    """Get all audit logs (requires audit:read permission)."""
    try:
        return service.get_audit_logs(skip, limit)
    except Exception as e:
        logger.error(f"Error getting audit logs: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get audit logs")


@router.get("/recent", response_model=List[AuditLogResponse])
def get_recent_logs(
    hours: int = 24,
    limit: int = 100,
    service: AuditLogService = Depends(get_audit_log_service),
    current_user: User = Depends(require_permission("audit", "read"))
):
    """Get recent audit logs (requires audit:read permission)."""
    try:
        return service.get_recent_logs(hours, limit)
    except Exception as e:
        logger.error(f"Error getting recent logs: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get recent logs")


@router.get("/user/{user_id}", response_model=List[AuditLogResponse])
def get_user_audit_logs(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    service: AuditLogService = Depends(get_audit_log_service),
    current_user: User = Depends(require_permission("audit", "read"))
):
    """Get audit logs for a specific user (requires audit:read permission)."""
    try:
        return service.get_user_audit_logs(user_id, skip, limit)
    except Exception as e:
        logger.error(f"Error getting user audit logs: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get user audit logs")


@router.post("/search", response_model=List[AuditLogResponse])
def search_audit_logs(
    filters: AuditLogSearchFilters,
    service: AuditLogService = Depends(get_audit_log_service),
    current_user: User = Depends(require_permission("audit", "read"))
):
    """Search audit logs with filters (requires audit:read permission)."""
    try:
        filter_dict = filters.model_dump(exclude_unset=True)
        return service.search_audit_logs(filter_dict, filters.skip, filters.limit)
    except Exception as e:
        logger.error(f"Error searching audit logs: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to search audit logs")
