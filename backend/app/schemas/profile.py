"""Pydantic schemas for User Profile."""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime


class ProfileResponse(BaseModel):
    """Schema for user profile response."""
    id: int
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    roles: list = []
    
    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    """Schema for password change."""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=10, max_length=100)
    confirm_password: str = Field(..., min_length=10, max_length=100)


class UserPreferences(BaseModel):
    """Schema for user preferences."""
    theme: Optional[str] = "light"
    language: Optional[str] = "en"
    notifications_enabled: Optional[bool] = True
    email_notifications: Optional[bool] = True
    default_page: Optional[str] = "dashboard"
    items_per_page: Optional[int] = 20


class PreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""
    preferences: Dict[str, Any]


class PreferencesResponse(BaseModel):
    """Schema for preferences response."""
    user_id: int
    preferences: Dict[str, Any]
    updated_at: datetime
