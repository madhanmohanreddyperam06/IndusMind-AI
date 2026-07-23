"""RolePermission model for RBAC system."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.config.database import Base


class RolePermission(Base):
    """RolePermission model for mapping roles to permissions."""
    
    __tablename__ = "role_permissions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_id = Column(String(36), ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False, index=True)
    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # User who granted this permission
    
    # Relationships
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")
    granter = relationship("User", foreign_keys=[granted_by])
    
    # Unique constraint to prevent duplicate permission assignments
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='unique_role_permission'),
    )
    
    def __repr__(self):
        return f"<RolePermission(id={self.id}, role_id={self.role_id}, permission_id={self.permission_id})>"
