"""Repository for Notification model."""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.notification import Notification


class NotificationRepository:
    """Repository for Notification data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, notification: Notification) -> Notification:
        """Create a new notification."""
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    def get_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID."""
        return self.db.query(Notification).filter(Notification.id == notification_id).first()
    
    def get_user_notifications(self, user_id: int, skip: int = 0, limit: int = 50) -> List[Notification]:
        """Get all notifications for a user."""
        return self.db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_unread_notifications(self, user_id: int, skip: int = 0, limit: int = 50) -> List[Notification]:
        """Get unread notifications for a user."""
        return self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_type(self, user_id: int, notification_type: str, skip: int = 0, limit: int = 50) -> List[Notification]:
        """Get notifications by type for a user."""
        return self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.type == notification_type
        ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Mark a notification as read."""
        notification = self.get_by_id(notification_id)
        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications for a user as read."""
        count = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
        
        self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        self.db.commit()
        return count
    
    def delete(self, notification_id: str) -> bool:
        """Delete a notification."""
        notification = self.get_by_id(notification_id)
        if notification:
            self.db.delete(notification)
            self.db.commit()
            return True
        return False
    
    def delete_old_notifications(self, days: int = 30) -> int:
        """Delete notifications older than N days."""
        cutoff_date = datetime.utcnow() - datetime.timedelta(days=days)
        count = self.db.query(Notification).filter(Notification.created_at < cutoff_date).count()
        self.db.query(Notification).filter(Notification.created_at < cutoff_date).delete()
        self.db.commit()
        return count
