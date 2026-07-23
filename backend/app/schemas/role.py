"""Pydantic schemas for Role model."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RoleBase(BaseModel):
    """Base role schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class RoleCreate(RoleBase):
    """Schema for creating a role."""
    pass


class RoleUpdate(BaseModel):
    """Schema for updating a role."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    """Schema for role response."""
    id: str
    is_system: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RoleWithPermissions(RoleResponse):
    """Schema for role with its permissions."""
    permissions: list = []
    
    class Config:
        from_attributes = True
