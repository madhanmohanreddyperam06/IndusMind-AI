"""API routes for Notifications."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.services.notification import NotificationService
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationCountResponse,
    BulkNotificationCreate
)
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()


def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    """Dependency to get notification service."""
    return NotificationService(db)


@router.get("", response_model=List[NotificationResponse])
def get_notifications(
    skip: int = 0,
    limit: int = 50,
    service: NotificationService = Depends(get_notification_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's notifications."""
    try:
        return service.get_user_notifications(current_user.id, skip, limit)
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get notifications")


@router.get("/unread", response_model=List[NotificationResponse])
def get_unread_notifications(
    skip: int = 0,
    limit: int = 50,
    service: NotificationService = Depends(get_notification_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's unread notifications."""
    try:
        return service.get_unread_notifications(current_user.id, skip, limit)
    except Exception as e:
        logger.error(f"Error getting unread notifications: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get unread notifications")


@router.get("/count", response_model=NotificationCountResponse)
def get_notification_count(
    service: NotificationService = Depends(get_notification_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's notification count."""
    try:
        return service.get_notification_count(current_user.id)
    except Exception as e:
        logger.error(f"Error getting notification count: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get notification count")


@router.get("/type/{notification_type}", response_model=List[NotificationResponse])
def get_notifications_by_type(
    notification_type: str,
    skip: int = 0,
    limit: int = 50,
    service: NotificationService = Depends(get_notification_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's notifications by type."""
    try:
        return service.get_notifications_by_type(current_user.id, notification_type, skip, limit)
    except Exception as e:
        logger.error(f"Error getting notifications by type: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get notifications by type")


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    notification_data: NotificationCreate,
    service: NotificationService = Depends(get_notification_service),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new notification (for current user or admin for others)."""
    try:
        # Users can only create notifications for themselves
        if notification_data.user_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only create notifications for yourself"
            )
        
        notification = service.create_notification(
            user_id=notification_data.user_id,
            notification_type=notification_data.type,
            title=notification_data.title,
            message=notification_data.message,
            action_url=notification_data.action_url,
            is_background=notification_data.is_background,
            metadata=notification_data.meta_data
        )
        return notification
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create notification")


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
def create_bulk_notifications(
    bulk_data: BulkNotificationCreate,
    service: NotificationService = Depends(get_notification_service),
    current_user: User = Depends(get_current_active_user)
):
    """Create bulk notifications (admin only)."""
    try:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only superusers can create bulk notifications"
            )
        
        created_count = 0
        for user_id in bulk_data.user_ids:
            service.create_notification(
                user_id=user_id,
                notification_type=bulk_data.type,
                title=bulk_data.title,
                message=bulk_data.message,
                action_url=bulk_data.action_url,
                is_background=bulk_data.is_background,
                metadata=bulk_data.meta_data
            )
            created_count += 1
        
        return {"message": f"Created {created_count} notifications"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating bulk notifications: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create bulk notifications")


@router.patch("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: str,
    service: NotificationService = Depends(get_notification_service),
    current_user: User = Depends(get_current_active_user)
):
    """Mark a notification as read."""
    try:
        success = service.mark_as_read(notification_id)
        if success:
            return {"message": "Notification marked as read"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to mark notification as read")


@router.patch("/read-all")
def mark_all_as_read(
    service: NotificationService = Depends(get_notification_service),
    current_user: User = Depends(get_current_active_user)
):
    """Mark all notifications as read for current user."""
    try:
        count = service.mark_all_as_read(current_user.id)
        return {"message": f"Marked {count} notifications as read"}
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to mark all notifications as read")


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: str,
    service: NotificationService = Depends(get_notification_service),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a notification."""
    try:
        success = service.delete_notification(notification_id)
        if success:
            return {"message": "Notification deleted successfully"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete notification")
