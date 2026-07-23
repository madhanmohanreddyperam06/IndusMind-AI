"""Service for User Profile business logic."""
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.repositories.user import get_user_by_email, authenticate_user
from app.services.auth import get_password_hash
from app.schemas.profile import ProfileUpdate, PasswordChange, UserPreferences


class ProfileService:
    """Service for User Profile operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_profile(self, user_id: int) -> dict:
        """Get user profile."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Get user roles
        user_roles = self.db.query(UserRole).filter(UserRole.user_id == user_id).all()
        roles = []
        for ur in user_roles:
            role = self.db.query(Role).filter(Role.id == ur.role_id).first()
            if role:
                roles.append({
                    "id": role.id,
                    "name": role.name,
                    "description": role.description
                })
        
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "roles": roles
        }
    
    def update_profile(self, user_id: int, update_data: ProfileUpdate) -> dict:
        """Update user profile."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Check if email is being changed and if it's already taken
        if update_data.email and update_data.email != user.email:
            existing = get_user_by_email(self.db, email=update_data.email)
            if existing:
                raise ValueError("Email already in use")
            user.email = update_data.email
        
        if update_data.full_name:
            user.full_name = update_data.full_name
        
        self.db.commit()
        self.db.refresh(user)
        
        return self.get_profile(user_id)
    
    def change_password(self, user_id: int, password_data: PasswordChange) -> bool:
        """Change user password."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        from app.services.auth import verify_password
        if not verify_password(password_data.current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")
        
        # Verify new passwords match
        if password_data.new_password != password_data.confirm_password:
            raise ValueError("New passwords do not match")
        
        # Update password
        user.hashed_password = get_password_hash(password_data.new_password)
        self.db.commit()
        
        return True
    
    def get_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get user preferences (placeholder - stored in a separate table in production)."""
        # For now, return default preferences
        # In production, this would query a user_preferences table
        return {
            "theme": "light",
            "language": "en",
            "notifications_enabled": True,
            "email_notifications": True,
            "default_page": "dashboard",
            "items_per_page": 20
        }
    
    def update_preferences(self, user_id: int, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences (placeholder - stored in a separate table in production)."""
        # For now, just return the preferences
        # In production, this would update a user_preferences table
        return preferences
