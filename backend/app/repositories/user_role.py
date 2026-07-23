"""Repository for UserRole model."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.user_role import UserRole


class UserRoleRepository:
    """Repository for UserRole data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_role_id: str) -> Optional[UserRole]:
        """Get user role by ID."""
        return self.db.query(UserRole).filter(UserRole.id == user_role_id).first()
    
    def get_user_roles(self, user_id: int) -> List[UserRole]:
        """Get all roles for a user."""
        return self.db.query(UserRole).filter(UserRole.user_id == user_id).all()
    
    def get_role_users(self, role_id: str) -> List[UserRole]:
        """Get all users with a specific role."""
        return self.db.query(UserRole).filter(UserRole.role_id == role_id).all()
    
    def create(self, user_role: UserRole) -> UserRole:
        """Create a new user role assignment."""
        self.db.add(user_role)
        self.db.commit()
        self.db.refresh(user_role)
        return user_role
    
    def delete(self, user_role_id: str) -> bool:
        """Delete a user role assignment."""
        user_role = self.get_by_id(user_role_id)
        if user_role:
            self.db.delete(user_role)
            self.db.commit()
            return True
        return False
    
    def delete_user_role(self, user_id: int, role_id: str) -> bool:
        """Delete a specific user role assignment."""
        user_role = self.db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        ).first()
        if user_role:
            self.db.delete(user_role)
            self.db.commit()
            return True
        return False
    
    def delete_user_roles(self, user_id: int) -> int:
        """Delete all role assignments for a user."""
        count = self.db.query(UserRole).filter(UserRole.user_id == user_id).count()
        self.db.query(UserRole).filter(UserRole.user_id == user_id).delete()
        self.db.commit()
        return count
