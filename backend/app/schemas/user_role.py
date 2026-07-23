"""Pydantic schemas for UserRole model."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserRoleCreate(BaseModel):
    """Schema for assigning a role to a user."""
    user_id: int
    role_id: str


class UserRoleResponse(BaseModel):
    """Schema for user role response."""
    id: str
    user_id: int
    role_id: str
    assigned_at: datetime
    assigned_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class RoleAssignmentResponse(BaseModel):
    """Schema for role assignment response."""
    message: str
    user_role: UserRoleResponse
