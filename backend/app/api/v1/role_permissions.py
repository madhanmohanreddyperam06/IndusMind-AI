"""API routes for Role Permission management."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.services.authorization import AuthorizationService
from app.schemas.role_permission import RolePermissionCreate, RolePermissionResponse, PermissionAssignmentResponse
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()


def get_authorization_service(db: Session = Depends(get_db)) -> AuthorizationService:
    """Dependency to get authorization service."""
    return AuthorizationService(db)


@router.post("", response_model=PermissionAssignmentResponse, status_code=status.HTTP_201_CREATED)
def grant_permission_to_role(
    assignment: RolePermissionCreate,
    service: AuthorizationService = Depends(get_authorization_service),
    current_user: User = Depends(get_current_active_user)
):
    """Grant a permission to a role."""
    try:
        success = service.grant_permission_to_role(
            assignment.role_id, 
            assignment.permission_id, 
            granted_by=current_user.id
        )
        if success:
            role_permission = service.role_permission_repo.get_role_permissions(assignment.role_id)[-1]
            return PermissionAssignmentResponse(
                message="Permission granted successfully",
                role_permission=RolePermissionResponse.model_validate(role_permission)
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Permission already granted to role")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error granting permission: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to grant permission")


@router.get("/role/{role_id}", response_model=List[RolePermissionResponse])
def get_role_permissions(
    role_id: str,
    service: AuthorizationService = Depends(get_authorization_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get all permissions for a role."""
    try:
        role_permissions = service.role_permission_repo.get_role_permissions(role_id)
        return [RolePermissionResponse.model_validate(rp) for rp in role_permissions]
    except Exception as e:
        logger.error(f"Error getting role permissions: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get role permissions")


@router.get("/permission/{permission_id}", response_model=List[RolePermissionResponse])
def get_permission_roles(
    permission_id: str,
    service: AuthorizationService = Depends(get_authorization_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get all roles with a specific permission."""
    try:
        permission_roles = service.role_permission_repo.get_permission_roles(permission_id)
        return [RolePermissionResponse.model_validate(pr) for pr in permission_roles]
    except Exception as e:
        logger.error(f"Error getting permission roles: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get permission roles")


@router.delete("/role/{role_id}/permission/{permission_id}")
def revoke_permission_from_role(
    role_id: str,
    permission_id: str,
    service: AuthorizationService = Depends(get_authorization_service),
    current_user: User = Depends(get_current_active_user)
):
    """Revoke a permission from a role."""
    try:
        success = service.revoke_permission_from_role(role_id, permission_id)
        if success:
            return {"message": "Permission revoked successfully"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission assignment not found")
    except Exception as e:
        logger.error(f"Error revoking permission: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to revoke permission")


@router.delete("/role/{role_id}")
def remove_all_role_permissions(
    role_id: str,
    service: AuthorizationService = Depends(get_authorization_service),
    current_user: User = Depends(get_current_active_user)
):
    """Remove all permissions from a role."""
    try:
        count = service.role_permission_repo.delete_role_permissions(role_id)
        return {"message": f"Removed {count} permission assignments"}
    except Exception as e:
        logger.error(f"Error removing role permissions: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove role permissions")
