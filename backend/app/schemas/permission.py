"""Pydantic schemas for Permission model."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PermissionBase(BaseModel):
    """Base permission schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    resource: str = Field(..., min_length=1, max_length=50)
    action: str = Field(..., min_length=1, max_length=50)


class PermissionCreate(PermissionBase):
    """Schema for creating a permission."""
    pass


class PermissionUpdate(BaseModel):
    """Schema for updating a permission."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    resource: Optional[str] = Field(None, min_length=1, max_length=50)
    action: Optional[str] = Field(None, min_length=1, max_length=50)


class PermissionResponse(PermissionBase):
    """Schema for permission response."""
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
