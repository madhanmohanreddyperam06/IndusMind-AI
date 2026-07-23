"""Repository for RolePermission model."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.role_permission import RolePermission


class RolePermissionRepository:
    """Repository for RolePermission data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, role_permission_id: str) -> Optional[RolePermission]:
        """Get role permission by ID."""
        return self.db.query(RolePermission).filter(RolePermission.id == role_permission_id).first()
    
    def get_role_permissions(self, role_id: str) -> List[RolePermission]:
        """Get all permissions for a role."""
        return self.db.query(RolePermission).filter(RolePermission.role_id == role_id).all()
    
    def get_permission_roles(self, permission_id: str) -> List[RolePermission]:
        """Get all roles with a specific permission."""
        return self.db.query(RolePermission).filter(RolePermission.permission_id == permission_id).all()
    
    def create(self, role_permission: RolePermission) -> RolePermission:
        """Create a new role permission assignment."""
        self.db.add(role_permission)
        self.db.commit()
        self.db.refresh(role_permission)
        return role_permission
    
    def delete(self, role_permission_id: str) -> bool:
        """Delete a role permission assignment."""
        role_permission = self.get_by_id(role_permission_id)
        if role_permission:
            self.db.delete(role_permission)
            self.db.commit()
            return True
        return False
    
    def delete_role_permissions(self, role_id: str) -> int:
        """Delete all permission assignments for a role."""
        count = self.db.query(RolePermission).filter(RolePermission.role_id == role_id).count()
        self.db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
        self.db.commit()
        return count
    
    def delete_permission_roles(self, permission_id: str) -> int:
        """Delete all role assignments for a permission."""
        count = self.db.query(RolePermission).filter(RolePermission.permission_id == permission_id).count()
        self.db.query(RolePermission).filter(RolePermission.permission_id == permission_id).delete()
        self.db.commit()
        return count
