"""API routes for User Management."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.api.dependencies import get_current_active_user
from app.api.authorization import require_permission
from app.models.user import User
from app.services.user_management import UserManagementService
from app.services.authorization import AuthorizationService
from app.schemas.user_management import (
    UserListResponse, 
    UserDetailResponse, 
    UserUpdate, 
    UserSearchQuery,
    UserEnableResponse,
    UserRoleAssignmentResponse
)
from app.schemas.user_role import UserRoleCreate
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()


def get_user_management_service(db: Session = Depends(get_db)) -> UserManagementService:
    """Dependency to get user management service."""
    return UserManagementService(db)


def get_authorization_service(db: Session = Depends(get_db)) -> AuthorizationService:
    """Dependency to get authorization service."""
    return AuthorizationService(db)


@router.get("", response_model=List[UserListResponse])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: UserManagementService = Depends(get_user_management_service),
    current_user: User = Depends(require_permission("users", "read"))
):
    """List all users (requires users:read permission)."""
    try:
        return service.list_users(skip, limit)
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list users")


@router.post("/search", response_model=List[UserListResponse])
def search_users(
    query: UserSearchQuery,
    service: UserManagementService = Depends(get_user_management_service),
    current_user: User = Depends(require_permission("users", "read"))
):
    """Search users with filters (requires users:read permission)."""
    try:
        return service.search_users(query)
    except Exception as e:
        logger.error(f"Error searching users: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to search users")


@router.get("/{user_id}", response_model=UserDetailResponse)
def get_user(
    user_id: int,
    service: UserManagementService = Depends(get_user_management_service),
    current_user: User = Depends(require_permission("users", "read"))
):
    """Get user details (requires users:read permission)."""
    try:
        return service.get_user_detail(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get user")


@router.patch("/{user_id}", response_model=UserDetailResponse)
def update_user(
    user_id: int,
    update_data: UserUpdate,
    service: UserManagementService = Depends(get_user_management_service),
    current_user: User = Depends(require_permission("users", "update"))
):
    """Update user information (requires users:update permission)."""
    try:
        return service.update_user(user_id, update_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user")


@router.post("/{user_id}/enable", response_model=UserDetailResponse)
def enable_user(
    user_id: int,
    service: UserManagementService = Depends(get_user_management_service),
    current_user: User = Depends(require_permission("users", "update"))
):
    """Enable a user account (requires users:update permission)."""
    try:
        return service.enable_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error enabling user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to enable user")


@router.post("/{user_id}/disable", response_model=UserDetailResponse)
def disable_user(
    user_id: int,
    service: UserManagementService = Depends(get_user_management_service),
    current_user: User = Depends(require_permission("users", "update"))
):
    """Disable a user account (requires users:update permission)."""
    try:
        return service.disable_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error disabling user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to disable user")


@router.post("/{user_id}/roles", response_model=UserRoleAssignmentResponse)
def assign_role(
    user_id: int,
    assignment: UserRoleCreate,
    auth_service: AuthorizationService = Depends(get_authorization_service),
    current_user: User = Depends(require_permission("users", "update"))
):
    """Assign a role to a user (requires users:update permission)."""
    try:
        success = auth_service.assign_role_to_user(user_id, assignment.role_id, assigned_by=current_user.id)
        if success:
            # Get role name for response
            from app.models.role import Role
            role = auth_service.db.query(Role).filter(Role.id == assignment.role_id).first()
            return UserRoleAssignmentResponse(
                message="Role assigned successfully",
                user_id=user_id,
                role_id=assignment.role_id,
                role_name=role.name if role else "Unknown"
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already assigned to user")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error assigning role: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to assign role")


@router.delete("/{user_id}/roles/{role_id}")
def remove_role(
    user_id: int,
    role_id: str,
    auth_service: AuthorizationService = Depends(get_authorization_service),
    current_user: User = Depends(require_permission("users", "update"))
):
    """Remove a role from a user (requires users:update permission)."""
    try:
        success = auth_service.remove_role_from_user(user_id, role_id)
        if success:
            return {"message": "Role removed successfully"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role assignment not found")
    except Exception as e:
        logger.error(f"Error removing role: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove role")


@router.get("/{user_id}/roles")
def get_user_roles(
    user_id: int,
    service: UserManagementService = Depends(get_user_management_service),
    current_user: User = Depends(require_permission("users", "read"))
):
    """Get all roles for a user (requires users:read permission)."""
    try:
        return service.get_user_roles(user_id)
    except Exception as e:
        logger.error(f"Error getting user roles: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get user roles")
