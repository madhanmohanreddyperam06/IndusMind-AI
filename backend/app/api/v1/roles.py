"""API routes for Role management."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.services.role import RoleService
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, RoleWithPermissions
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()


def get_role_service(db: Session = Depends(get_db)) -> RoleService:
    """Dependency to get role service."""
    return RoleService(db)


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_data: RoleCreate,
    service: RoleService = Depends(get_role_service),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new role."""
    try:
        return service.create_role(role_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating role: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create role")


@router.get("", response_model=List[RoleResponse])
def get_roles(
    skip: int = 0,
    limit: int = 100,
    service: RoleService = Depends(get_role_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get all roles."""
    try:
        return service.get_all_roles(skip, limit)
    except Exception as e:
        logger.error(f"Error getting roles: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get roles")


@router.get("/active", response_model=List[RoleResponse])
def get_active_roles(
    skip: int = 0,
    limit: int = 100,
    service: RoleService = Depends(get_role_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get active roles."""
    try:
        return service.get_active_roles(skip, limit)
    except Exception as e:
        logger.error(f"Error getting active roles: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get active roles")


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: str,
    service: RoleService = Depends(get_role_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get role by ID."""
    try:
        return service.get_role(role_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting role: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get role")


@router.patch("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: str,
    role_data: RoleUpdate,
    service: RoleService = Depends(get_role_service),
    current_user: User = Depends(get_current_active_user)
):
    """Update a role."""
    try:
        return service.update_role(role_id, role_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating role: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update role")


@router.delete("/{role_id}")
def delete_role(
    role_id: str,
    service: RoleService = Depends(get_role_service),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a role (soft delete)."""
    try:
        success = service.delete_role(role_id)
        if success:
            return {"message": "Role deleted successfully"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting role: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete role")
