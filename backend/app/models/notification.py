"""Notification model for user notifications."""
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean
from datetime import datetime
import uuid
from app.config.database import Base


class Notification(Base):
    """Notification model for user notifications."""
    
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, nullable=False, index=True)
    type = Column(String(20), nullable=False, index=True)  # success, warning, error, info
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    action_url = Column(String(500), nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    is_background = Column(Boolean, default=False, nullable=False)
    meta_data = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type}, title={self.title})>"
