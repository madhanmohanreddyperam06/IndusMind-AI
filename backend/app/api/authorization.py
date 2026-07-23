"""Authorization dependencies and decorators for RBAC."""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.config.database import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.services.authorization import AuthorizationService


def get_authorization_service(db: Session = Depends(get_db)) -> AuthorizationService:
    """Dependency to get authorization service."""
    return AuthorizationService(db)


def require_permission(resource: str, action: str):
    """Dependency to require a specific permission."""
    def permission_checker(
        current_user: User = Depends(get_current_active_user),
        auth_service: AuthorizationService = Depends(get_authorization_service)
    ):
        if auth_service.has_permission(current_user.id, resource, action):
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have permission: {resource}:{action}"
        )
    return permission_checker


def require_any_permission(resource: str, actions: List[str]):
    """Dependency to require any of the specified permissions for a resource."""
    def permission_checker(
        current_user: User = Depends(get_current_active_user),
        auth_service: AuthorizationService = Depends(get_authorization_service)
    ):
        if auth_service.has_any_permission(current_user.id, resource, actions):
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have any of the required permissions for {resource}: {actions}"
        )
    return permission_checker


def require_all_permissions(resource: str, actions: List[str]):
    """Dependency to require all of the specified permissions for a resource."""
    def permission_checker(
        current_user: User = Depends(get_current_active_user),
        auth_service: AuthorizationService = Depends(get_authorization_service)
    ):
        if auth_service.has_all_permissions(current_user.id, resource, actions):
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have all required permissions for {resource}: {actions}"
        )
    return permission_checker


def require_role(role_name: str):
    """Dependency to require a specific role."""
    def role_checker(
        current_user: User = Depends(get_current_active_user),
        auth_service: AuthorizationService = Depends(get_authorization_service)
    ):
        roles = auth_service.get_user_roles(current_user.id)
        role_names = [role.name for role in roles]
        if role_name in role_names:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have required role: {role_name}"
        )
    return role_checker


def require_any_role(role_names: List[str]):
    """Dependency to require any of the specified roles."""
    def role_checker(
        current_user: User = Depends(get_current_active_user),
        auth_service: AuthorizationService = Depends(get_authorization_service)
    ):
        roles = auth_service.get_user_roles(current_user.id)
        user_role_names = [role.name for role in roles]
        if any(role in user_role_names for role in role_names):
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have any of the required roles: {role_names}"
        )
    return role_checker


def require_superuser():
    """Dependency to require superuser status."""
    def superuser_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.is_superuser:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have superuser privileges"
        )
    return superuser_checker
