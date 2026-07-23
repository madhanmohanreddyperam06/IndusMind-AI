"""Permission model for RBAC system."""
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.config.database import Base


class Permission(Base):
    """Permission model for RBAC."""
    
    __tablename__ = "permissions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    resource = Column(String(50), nullable=False, index=True)  # e.g., documents, users, roles
    action = Column(String(50), nullable=False, index=True)  # e.g., create, read, update, delete
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Permission(id={self.id}, name={self.name}, resource={self.resource}, action={self.action})>"
