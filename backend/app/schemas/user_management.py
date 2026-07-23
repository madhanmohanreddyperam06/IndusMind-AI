"""Pydantic schemas for User Management."""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class UserListResponse(BaseModel):
    """Schema for user list response."""
    id: int
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    role_count: int
    
    class Config:
        from_attributes = True


class UserDetailResponse(UserListResponse):
    """Schema for user detail response."""
    roles: List[dict] = []
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserSearchQuery(BaseModel):
    """Schema for user search query."""
    search: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    skip: int = 0
    limit: int = 20


class UserEnableResponse(BaseModel):
    """Schema for user enable/disable response."""
    message: str
    user_id: int
    is_active: bool


class UserRoleAssignmentResponse(BaseModel):
    """Schema for user role assignment response."""
    message: str
    user_id: int
    role_id: str
    role_name: str
