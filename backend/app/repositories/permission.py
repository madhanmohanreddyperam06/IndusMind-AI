"""Repository for Permission model."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.permission import Permission


class PermissionRepository:
    """Repository for Permission data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, permission_id: str) -> Optional[Permission]:
        """Get permission by ID."""
        return self.db.query(Permission).filter(Permission.id == permission_id).first()
    
    def get_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name."""
        return self.db.query(Permission).filter(Permission.name == name).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Permission]:
        """Get all permissions."""
        return self.db.query(Permission).offset(skip).limit(limit).all()
    
    def get_by_resource(self, resource: str, skip: int = 0, limit: int = 100) -> List[Permission]:
        """Get permissions by resource."""
        return self.db.query(Permission).filter(Permission.resource == resource).offset(skip).limit(limit).all()
    
    def create(self, permission: Permission) -> Permission:
        """Create a new permission."""
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        return permission
    
    def update(self, permission: Permission) -> Permission:
        """Update an existing permission."""
        self.db.commit()
        self.db.refresh(permission)
        return permission
    
    def delete(self, permission_id: str) -> bool:
        """Delete a permission."""
        permission = self.get_by_id(permission_id)
        if permission:
            self.db.delete(permission)
            self.db.commit()
            return True
        return False
