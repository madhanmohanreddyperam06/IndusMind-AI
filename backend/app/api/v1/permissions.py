"""API routes for Permission management."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.services.permission import PermissionService
from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionResponse
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()


def get_permission_service(db: Session = Depends(get_db)) -> PermissionService:
    """Dependency to get permission service."""
    return PermissionService(db)


@router.post("", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(
    permission_data: PermissionCreate,
    service: PermissionService = Depends(get_permission_service),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new permission."""
    try:
        return service.create_permission(permission_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating permission: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create permission")


@router.get("", response_model=List[PermissionResponse])
def get_permissions(
    skip: int = 0,
    limit: int = 100,
    service: PermissionService = Depends(get_permission_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get all permissions."""
    try:
        return service.get_all_permissions(skip, limit)
    except Exception as e:
        logger.error(f"Error getting permissions: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get permissions")


@router.get("/resource/{resource}", response_model=List[PermissionResponse])
def get_permissions_by_resource(
    resource: str,
    skip: int = 0,
    limit: int = 100,
    service: PermissionService = Depends(get_permission_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get permissions by resource."""
    try:
        return service.get_permissions_by_resource(resource, skip, limit)
    except Exception as e:
        logger.error(f"Error getting permissions by resource: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get permissions by resource")


@router.get("/{permission_id}", response_model=PermissionResponse)
def get_permission(
    permission_id: str,
    service: PermissionService = Depends(get_permission_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get permission by ID."""
    try:
        return service.get_permission(permission_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting permission: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get permission")


@router.patch("/{permission_id}", response_model=PermissionResponse)
def update_permission(
    permission_id: str,
    permission_data: PermissionUpdate,
    service: PermissionService = Depends(get_permission_service),
    current_user: User = Depends(get_current_active_user)
):
    """Update a permission."""
    try:
        return service.update_permission(permission_id, permission_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating permission: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update permission")


@router.delete("/{permission_id}")
def delete_permission(
    permission_id: str,
    service: PermissionService = Depends(get_permission_service),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a permission."""
    try:
        success = service.delete_permission(permission_id)
        if success:
            return {"message": "Permission deleted successfully"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    except Exception as e:
        logger.error(f"Error deleting permission: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete permission")
