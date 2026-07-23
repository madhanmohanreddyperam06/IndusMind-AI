"""Authorization service for RBAC."""
from sqlalchemy.orm import Session
from typing import List, Set
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.repositories.user_role import UserRoleRepository
from app.repositories.role_permission import RolePermissionRepository
from app.repositories.role import RoleRepository


class AuthorizationService:
    """Service for authorization checks."""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_role_repo = UserRoleRepository(db)
        self.role_permission_repo = RolePermissionRepository(db)
        self.role_repo = RoleRepository(db)
    
    def get_user_roles(self, user_id: int) -> List[Role]:
        """Get all roles for a user."""
        user_roles = self.user_role_repo.get_user_roles(user_id)
        roles = []
        for ur in user_roles:
            role = self.role_repo.get_by_id(ur.role_id)
            if role and role.is_active:
                roles.append(role)
        return roles
    
    def get_user_permissions(self, user_id: int) -> Set[str]:
        """Get all permissions for a user (from all their roles)."""
        user_roles = self.user_role_repo.get_user_roles(user_id)
        permissions = set()
        
        for ur in user_roles:
            role_permissions = self.role_permission_repo.get_role_permissions(ur.role_id)
            for rp in role_permissions:
                # Store permission as "resource:action" format
                permissions.add(f"{rp.permission.resource}:{rp.permission.action}")
        
        return permissions
    
    def has_permission(self, user_id: int, resource: str, action: str) -> bool:
        """Check if user has a specific permission."""
        # Superusers have all permissions
        user = self.db.query(User).filter(User.id == user_id).first()
        if user and user.is_superuser:
            return True
        
        # Check user's permissions
        permissions = self.get_user_permissions(user_id)
        required_permission = f"{resource}:{action}"
        return required_permission in permissions
    
    def has_any_permission(self, user_id: int, resource: str, actions: List[str]) -> bool:
        """Check if user has any of the specified permissions for a resource."""
        for action in actions:
            if self.has_permission(user_id, resource, action):
                return True
        return False
    
    def has_all_permissions(self, user_id: int, resource: str, actions: List[str]) -> bool:
        """Check if user has all of the specified permissions for a resource."""
        for action in actions:
            if not self.has_permission(user_id, resource, action):
                return False
        return True
    
    def assign_role_to_user(self, user_id: int, role_id: str, assigned_by: int = None) -> bool:
        """Assign a role to a user."""
        # Check if role exists and is active
        role = self.role_repo.get_by_id(role_id)
        if not role or not role.is_active:
            raise ValueError("Role not found or inactive")
        
        # Check if user already has this role
        from app.models.user_role import UserRole
        existing = self.db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        ).first()
        
        if existing:
            return False  # Already assigned
        
        user_role = UserRole(user_id=user_id, role_id=role_id, assigned_by=assigned_by)
        self.user_role_repo.create(user_role)
        return True
    
    def remove_role_from_user(self, user_id: int, role_id: str) -> bool:
        """Remove a role from a user."""
        return self.user_role_repo.delete_user_role(user_id, role_id)
    
    def grant_permission_to_role(self, role_id: str, permission_id: str, granted_by: int = None) -> bool:
        """Grant a permission to a role."""
        # Check if role exists and is active
        role = self.role_repo.get_by_id(role_id)
        if not role or not role.is_active:
            raise ValueError("Role not found or inactive")
        
        # Check if role already has this permission
        from app.models.role_permission import RolePermission
        existing = self.db.query(RolePermission).filter(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id
        ).first()
        
        if existing:
            return False  # Already granted
        
        role_permission = RolePermission(role_id=role_id, permission_id=permission_id, granted_by=granted_by)
        self.role_permission_repo.create(role_permission)
        return True
    
    def revoke_permission_from_role(self, role_id: str, permission_id: str) -> bool:
        """Revoke a permission from a role."""
        # Find and delete the role permission
        from app.models.role_permission import RolePermission
        role_permission = self.db.query(RolePermission).filter(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id
        ).first()
        
        if role_permission:
            self.db.delete(role_permission)
            self.db.commit()
            return True
        return False
