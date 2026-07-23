"""Service for UserRole business logic."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.user_role import UserRole
from app.models.role import Role
from app.repositories.user_role import UserRoleRepository
from datetime import datetime


class UserRoleService:
    """Service for UserRole business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRoleRepository(db)
    
    def assign_role(self, user_id: int, role_id: str, assigned_by: int) -> UserRole:
        """Assign a role to a user with validation for single admin/superuser."""
        # Check if role exists
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError(f"Role with ID {role_id} not found")
        
        # Validate single admin constraint
        if role.name == "admin":
            existing_admin = self.db.query(UserRole).join(Role).filter(
                Role.name == "admin",
                UserRole.user_id != user_id
            ).first()
            if existing_admin:
                raise ValueError("Only one admin account is allowed")
        
        # Validate single superuser constraint
        if role.name == "superuser":
            existing_superuser = self.db.query(UserRole).join(Role).filter(
                Role.name == "superuser",
                UserRole.user_id != user_id
            ).first()
            if existing_superuser:
                raise ValueError("Only one superuser account is allowed")
        
        # Check if user already has this role
        existing_assignment = self.db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        ).first()
        
        if existing_assignment:
            raise ValueError("User already has this role")
        
        # Create role assignment
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            assigned_at=datetime.utcnow(),
            assigned_by=assigned_by
        )
        return self.repository.create(user_role)
    
    def get_user_roles(self, user_id: int) -> List[UserRole]:
        """Get all roles for a user."""
        return self.repository.get_user_roles(user_id)
    
    def get_role_users(self, role_id: str) -> List[UserRole]:
        """Get all users with a specific role."""
        return self.repository.get_role_users(role_id)
    
    def remove_role(self, user_id: int, role_id: str) -> bool:
        """Remove a role from a user."""
        return self.repository.delete_user_role(user_id, role_id)
    
    def remove_all_user_roles(self, user_id: int) -> int:
        """Remove all role assignments for a user."""
        return self.repository.delete_user_roles(user_id)
