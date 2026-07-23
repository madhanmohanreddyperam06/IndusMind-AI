"""Service for Notification business logic."""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from app.models.notification import Notification
from app.repositories.notification import NotificationRepository


class NotificationService:
    """Service for Notification operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = NotificationRepository(db)
    
    def create_notification(
        self,
        user_id: int,
        notification_type: str,  # success, warning, error, info
        title: str,
        message: Optional[str] = None,
        action_url: Optional[str] = None,
        is_background: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Create a new notification."""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            action_url=action_url,
            is_background=is_background,
            meta_data=json.dumps(metadata) if metadata else None,
            created_at=datetime.utcnow()
        )
        return self.repository.create(notification)
    
    def create_success_notification(
        self,
        user_id: int,
        title: str,
        message: Optional[str] = None,
        action_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Create a success notification."""
        return self.create_notification(
            user_id=user_id,
            notification_type="success",
            title=title,
            message=message,
            action_url=action_url,
            is_background=False,
            metadata=metadata
        )
    
    def create_warning_notification(
        self,
        user_id: int,
        title: str,
        message: Optional[str] = None,
        action_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Create a warning notification."""
        return self.create_notification(
            user_id=user_id,
            notification_type="warning",
            title=title,
            message=message,
            action_url=action_url,
            is_background=False,
            metadata=metadata
        )
    
    def create_error_notification(
        self,
        user_id: int,
        title: str,
        message: Optional[str] = None,
        action_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Create an error notification."""
        return self.create_notification(
            user_id=user_id,
            notification_type="error",
            title=title,
            message=message,
            action_url=action_url,
            is_background=False,
            metadata=metadata
        )
    
    def create_info_notification(
        self,
        user_id: int,
        title: str,
        message: Optional[str] = None,
        action_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Create an info notification."""
        return self.create_notification(
            user_id=user_id,
            notification_type="info",
            title=title,
            message=message,
            action_url=action_url,
            is_background=False,
            metadata=metadata
        )
    
    def create_background_notification(
        self,
        user_id: int,
        title: str,
        message: Optional[str] = None,
        action_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Create a background notification (for async task completion)."""
        return self.create_notification(
            user_id=user_id,
            notification_type="info",
            title=title,
            message=message,
            action_url=action_url,
            is_background=True,
            metadata=metadata
        )
    
    def get_user_notifications(self, user_id: int, skip: int = 0, limit: int = 50) -> List[Notification]:
        """Get all notifications for a user."""
        return self.repository.get_user_notifications(user_id, skip, limit)
    
    def get_unread_notifications(self, user_id: int, skip: int = 0, limit: int = 50) -> List[Notification]:
        """Get unread notifications for a user."""
        return self.repository.get_unread_notifications(user_id, skip, limit)
    
    def get_notifications_by_type(self, user_id: int, notification_type: str, skip: int = 0, limit: int = 50) -> List[Notification]:
        """Get notifications by type for a user."""
        return self.repository.get_by_type(user_id, notification_type, skip, limit)
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Mark a notification as read."""
        return self.repository.mark_as_read(notification_id)
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications for a user as read."""
        return self.repository.mark_all_as_read(user_id)
    
    def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification."""
        return self.repository.delete(notification_id)
    
    def get_notification_count(self, user_id: int) -> Dict[str, int]:
        """Get notification counts for a user."""
        total = self.db.query(Notification).filter(Notification.user_id == user_id).count()
        unread = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
        
        return {
            "total": total,
            "unread": unread
        }
