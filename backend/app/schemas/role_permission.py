"""Pydantic schemas for RolePermission model."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RolePermissionCreate(BaseModel):
    """Schema for assigning a permission to a role."""
    role_id: str
    permission_id: str


class RolePermissionResponse(BaseModel):
    """Schema for role permission response."""
    id: str
    role_id: str
    permission_id: str
    granted_at: datetime
    granted_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class PermissionAssignmentResponse(BaseModel):
    """Schema for permission assignment response."""
    message: str
    role_permission: RolePermissionResponse
