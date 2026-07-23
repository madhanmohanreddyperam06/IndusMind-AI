"""Pydantic schemas for Notification."""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class NotificationCreate(BaseModel):
    """Schema for creating a notification."""
    user_id: int
    type: str  # success, warning, error, info
    title: str
    message: Optional[str] = None
    action_url: Optional[str] = None
    is_background: bool = False
    meta_data: Optional[Dict[str, Any]] = None


class NotificationResponse(BaseModel):
    """Schema for notification response."""
    id: str
    user_id: int
    type: str
    title: str
    message: Optional[str] = None
    action_url: Optional[str] = None
    is_read: bool
    is_background: bool
    meta_data: Optional[str] = None
    created_at: datetime
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class NotificationCountResponse(BaseModel):
    """Schema for notification count response."""
    total: int
    unread: int


class BulkNotificationCreate(BaseModel):
    """Schema for creating bulk notifications."""
    user_ids: list[int]
    type: str
    title: str
    message: Optional[str] = None
    action_url: Optional[str] = None
    is_background: bool = False
    meta_data: Optional[Dict[str, Any]] = None
