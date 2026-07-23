"""UserRole model for RBAC system."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.config.database import Base


class UserRole(Base):
    """UserRole model for mapping users to roles."""
    
    __tablename__ = "user_roles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # User who assigned this role
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
    assigner = relationship("User", foreign_keys=[assigned_by])
    
    # Unique constraint to prevent duplicate role assignments
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='unique_user_role'),
    )
    
    def __repr__(self):
        return f"<UserRole(id={self.id}, user_id={self.user_id}, role_id={self.role_id})>"
