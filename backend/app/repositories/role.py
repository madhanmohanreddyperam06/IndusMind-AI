"""Repository for Role model."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.role import Role


class RoleRepository:
    """Repository for Role data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        return self.db.query(Role).filter(Role.id == role_id).first()
    
    def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        return self.db.query(Role).filter(Role.name == name).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """Get all roles."""
        return self.db.query(Role).offset(skip).limit(limit).all()
    
    def get_active(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """Get active roles."""
        return self.db.query(Role).filter(Role.is_active == True).offset(skip).limit(limit).all()
    
    def create(self, role: Role) -> Role:
        """Create a new role."""
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role
    
    def update(self, role: Role) -> Role:
        """Update an existing role."""
        self.db.commit()
        self.db.refresh(role)
        return role
    
    def delete(self, role_id: str) -> bool:
        """Delete a role (soft delete by setting is_active=False)."""
        role = self.get_by_id(role_id)
        if role and not role.is_system:
            role.is_active = False
            self.db.commit()
            return True
        return False
    
    def hard_delete(self, role_id: str) -> bool:
        """Hard delete a role (only for non-system roles)."""
        role = self.get_by_id(role_id)
        if role and not role.is_system:
            self.db.delete(role)
            self.db.commit()
            return True
        return False
