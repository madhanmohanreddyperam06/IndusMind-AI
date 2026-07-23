"""Service for Role business logic."""
from sqlalchemy.orm import Session
from typing import List
from app.models.role import Role
from app.repositories.role import RoleRepository
from app.schemas.role import RoleCreate, RoleUpdate


class RoleService:
    """Service for Role business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = RoleRepository(db)
    
    def create_role(self, role_data: RoleCreate) -> Role:
        """Create a new role."""
        # Check if role name already exists
        existing = self.repository.get_by_name(role_data.name)
        if existing:
            raise ValueError(f"Role with name '{role_data.name}' already exists")
        
        role = Role(**role_data.model_dump())
        return self.repository.create(role)
    
    def get_role(self, role_id: str) -> Role:
        """Get role by ID."""
        role = self.repository.get_by_id(role_id)
        if not role:
            raise ValueError(f"Role with ID '{role_id}' not found")
        return role
    
    def get_all_roles(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """Get all roles."""
        return self.repository.get_all(skip, limit)
    
    def get_active_roles(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """Get active roles."""
        return self.repository.get_active(skip, limit)
    
    def update_role(self, role_id: str, role_data: RoleUpdate) -> Role:
        """Update an existing role."""
        role = self.get_role(role_id)
        
        # Check if new name conflicts with existing role
        if role_data.name and role_data.name != role.name:
            existing = self.repository.get_by_name(role_data.name)
            if existing:
                raise ValueError(f"Role with name '{role_data.name}' already exists")
        
        # Update fields
        update_data = role_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(role, field, value)
        
        return self.repository.update(role)
    
    def delete_role(self, role_id: str) -> bool:
        """Delete a role (soft delete)."""
        role = self.get_role(role_id)
        if role.is_system:
            raise ValueError("Cannot delete system roles")
        return self.repository.delete(role_id)
    
    def hard_delete_role(self, role_id: str) -> bool:
        """Hard delete a role."""
        role = self.get_role(role_id)
        if role.is_system:
            raise ValueError("Cannot delete system roles")
        return self.repository.hard_delete(role_id)
