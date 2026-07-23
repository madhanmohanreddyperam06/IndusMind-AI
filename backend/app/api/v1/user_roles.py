"""API routes for User Role management."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.services.user_role import UserRoleService
from app.schemas.user_role import UserRoleCreate, UserRoleResponse, RoleAssignmentResponse
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()


def get_user_role_service(db: Session = Depends(get_db)) -> UserRoleService:
    """Dependency to get user role service."""
    return UserRoleService(db)


@router.post("", response_model=RoleAssignmentResponse, status_code=status.HTTP_201_CREATED)
def assign_role_to_user(
    assignment: UserRoleCreate,
    service: UserRoleService = Depends(get_user_role_service),
    current_user: User = Depends(get_current_active_user)
):
    """Assign a role to a user with validation for single admin/superuser."""
    try:
        user_role = service.assign_role(
            assignment.user_id, 
            assignment.role_id, 
            assigned_by=current_user.id
        )
        return RoleAssignmentResponse(
            message="Role assigned successfully",
            user_role=UserRoleResponse.model_validate(user_role)
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error assigning role: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to assign role")


@router.get("/user/{user_id}", response_model=List[UserRoleResponse])
def get_user_roles(
    user_id: int,
    service: UserRoleService = Depends(get_user_role_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get all roles for a user."""
    try:
        user_roles = service.get_user_roles(user_id)
        return [UserRoleResponse.model_validate(ur) for ur in user_roles]
    except Exception as e:
        logger.error(f"Error getting user roles: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get user roles")


@router.get("/role/{role_id}", response_model=List[UserRoleResponse])
def get_role_users(
    role_id: str,
    service: UserRoleService = Depends(get_user_role_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get all users with a specific role."""
    try:
        role_users = service.get_role_users(role_id)
        return [UserRoleResponse.model_validate(ru) for ru in role_users]
    except Exception as e:
        logger.error(f"Error getting role users: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get role users")


@router.delete("/user/{user_id}/role/{role_id}")
def remove_role_from_user(
    user_id: int,
    role_id: str,
    service: UserRoleService = Depends(get_user_role_service),
    current_user: User = Depends(get_current_active_user)
):
    """Remove a role from a user."""
    try:
        success = service.remove_role(user_id, role_id)
        if success:
            return {"message": "Role removed successfully"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role assignment not found")
    except Exception as e:
        logger.error(f"Error removing role: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove role")


@router.delete("/user/{user_id}")
def remove_all_user_roles(
    user_id: int,
    service: UserRoleService = Depends(get_user_role_service),
    current_user: User = Depends(get_current_active_user)
):
    """Remove all roles from a user."""
    try:
        count = service.remove_all_user_roles(user_id)
        return {"message": f"Removed {count} role assignments"}
    except Exception as e:
        logger.error(f"Error removing user roles: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove user roles")
