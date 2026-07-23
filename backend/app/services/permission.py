"""Service for Permission business logic."""
from sqlalchemy.orm import Session
from typing import List
from app.models.permission import Permission
from app.repositories.permission import PermissionRepository
from app.schemas.permission import PermissionCreate, PermissionUpdate


class PermissionService:
    """Service for Permission business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = PermissionRepository(db)
    
    def create_permission(self, permission_data: PermissionCreate) -> Permission:
        """Create a new permission."""
        # Check if permission name already exists
        existing = self.repository.get_by_name(permission_data.name)
        if existing:
            raise ValueError(f"Permission with name '{permission_data.name}' already exists")
        
        permission = Permission(**permission_data.model_dump())
        return self.repository.create(permission)
    
    def get_permission(self, permission_id: str) -> Permission:
        """Get permission by ID."""
        permission = self.repository.get_by_id(permission_id)
        if not permission:
            raise ValueError(f"Permission with ID '{permission_id}' not found")
        return permission
    
    def get_all_permissions(self, skip: int = 0, limit: int = 100) -> List[Permission]:
        """Get all permissions."""
        return self.repository.get_all(skip, limit)
    
    def get_permissions_by_resource(self, resource: str, skip: int = 0, limit: int = 100) -> List[Permission]:
        """Get permissions by resource."""
        return self.repository.get_by_resource(resource, skip, limit)
    
    def update_permission(self, permission_id: str, permission_data: PermissionUpdate) -> Permission:
        """Update an existing permission."""
        permission = self.get_permission(permission_id)
        
        # Check if new name conflicts with existing permission
        if permission_data.name and permission_data.name != permission.name:
            existing = self.repository.get_by_name(permission_data.name)
            if existing:
                raise ValueError(f"Permission with name '{permission_data.name}' already exists")
        
        # Update fields
        update_data = permission_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(permission, field, value)
        
        return self.repository.update(permission)
    
    def delete_permission(self, permission_id: str) -> bool:
        """Delete a permission."""
        return self.repository.delete(permission_id)
