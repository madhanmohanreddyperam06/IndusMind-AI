"""Audit Log model for tracking system events."""
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from datetime import datetime
import uuid
from app.config.database import Base


class AuditLog(Base):
    """Audit Log model for tracking system events."""
    
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, nullable=True, index=True)  # Nullable for system events
    user_email = Column(String(255), nullable=True)
    action = Column(String(100), nullable=False, index=True)  # e.g., login, create, update, delete
    resource_type = Column(String(50), nullable=False, index=True)  # e.g., user, document, role
    resource_id = Column(String(255), nullable=True, index=True)
    details = Column(JSON, nullable=True)  # Additional context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="success")  # success, failure
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, resource_type={self.resource_type}, user_id={self.user_id})>"
