"""Service for User Management business logic."""
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_, and_
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.repositories.user import get_user_by_email
from app.schemas.user_management import UserUpdate, UserSearchQuery, UserListResponse, UserDetailResponse


class UserManagementService:
    """Service for User Management operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_users(self, skip: int = 0, limit: int = 20) -> List[UserListResponse]:
        """List all users with pagination."""
        users = self.db.query(User).offset(skip).limit(limit).all()
        return [self._to_list_response(user) for user in users]
    
    def search_users(self, query: UserSearchQuery) -> List[UserListResponse]:
        """Search users with filters."""
        q = self.db.query(User)
        
        if query.search:
            search_pattern = f"%{query.search}%"
            q = q.filter(
                or_(
                    User.email.ilike(search_pattern),
                    User.full_name.ilike(search_pattern)
                )
            )
        
        if query.is_active is not None:
            q = q.filter(User.is_active == query.is_active)
        
        if query.is_superuser is not None:
            q = q.filter(User.is_superuser == query.is_superuser)
        
        users = q.offset(query.skip).limit(query.limit).all()
        return [self._to_list_response(user) for user in users]
    
    def get_user_detail(self, user_id: int) -> UserDetailResponse:
        """Get detailed user information."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        return self._to_detail_response(user)
    
    def update_user(self, user_id: int, update_data: UserUpdate) -> UserDetailResponse:
        """Update user information."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        return self._to_detail_response(user)
    
    def enable_user(self, user_id: int) -> UserDetailResponse:
        """Enable a user account."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        user.is_active = True
        self.db.commit()
        self.db.refresh(user)
        
        return self._to_detail_response(user)
    
    def disable_user(self, user_id: int) -> UserDetailResponse:
        """Disable a user account."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        
        return self._to_detail_response(user)
    
    def get_user_roles(self, user_id: int) -> List[dict]:
        """Get all roles for a user."""
        user_roles = self.db.query(UserRole).filter(UserRole.user_id == user_id).all()
        roles = []
        for ur in user_roles:
            role = self.db.query(Role).filter(Role.id == ur.role_id).first()
            if role:
                roles.append({
                    "id": role.id,
                    "name": role.name,
                    "description": role.description,
                    "is_system": role.is_system,
                    "assigned_at": ur.assigned_at
                })
        return roles
    
    def _to_list_response(self, user: User) -> UserListResponse:
        """Convert User model to UserListResponse."""
        role_count = self.db.query(UserRole).filter(UserRole.user_id == user.id).count()
        return UserListResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
            role_count=role_count
        )
    
    def _to_detail_response(self, user: User) -> UserDetailResponse:
        """Convert User model to UserDetailResponse."""
        roles = self.get_user_roles(user.id)
        role_count = len(roles)
        return UserDetailResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
            role_count=role_count,
            roles=roles
        )
