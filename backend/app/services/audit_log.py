"""Service for Audit Log business logic."""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.audit_log import AuditLog
from app.repositories.audit_log import AuditLogRepository


class AuditLogService:
    """Service for Audit Log operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = AuditLogRepository(db)
    
    def log_event(
        self,
        user_id: Optional[int],
        user_email: Optional[str],
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Log an audit event."""
        audit_log = AuditLog(
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            error_message=error_message,
            timestamp=datetime.utcnow()
        )
        return self.repository.create(audit_log)
    
    def log_auth_event(
        self,
        user_id: Optional[int],
        user_email: Optional[str],
        action: str,  # login, logout, failed_login, password_change, password_reset
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Log an authentication event."""
        return self.log_event(
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type="auth",
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            error_message=error_message
        )
    
    def log_authorization_event(
        self,
        user_id: int,
        user_email: str,
        action: str,  # permission_check, role_assign, role_revoke
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Log an authorization event."""
        return self.log_event(
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            status=status,
            error_message=error_message
        )
    
    def log_document_event(
        self,
        user_id: int,
        user_email: str,
        action: str,  # upload, download, delete, update
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Log a document event."""
        return self.log_event(
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type="document",
            resource_id=resource_id,
            details=details,
            status=status,
            error_message=error_message
        )
    
    def log_admin_event(
        self,
        user_id: int,
        user_email: str,
        action: str,  # user_create, user_update, user_delete, role_create, etc.
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Log an admin event."""
        return self.log_event(
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            status=status,
            error_message=error_message
        )
    
    def log_ai_event(
        self,
        user_id: int,
        user_email: str,
        action: str,  # rag_query, extraction, graph_query
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Log an AI-related event."""
        return self.log_event(
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            status=status,
            error_message=error_message
        )
    
    def log_config_event(
        self,
        user_id: Optional[int],
        user_email: Optional[str],
        action: str,  # config_update, config_view
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Log a configuration event."""
        return self.log_event(
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            status=status,
            error_message=error_message
        )
    
    def log_security_event(
        self,
        user_id: Optional[int],
        user_email: Optional[str],
        action: str,  # suspicious_activity, rate_limit, blocked_request
        resource_type: str = "security",
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Log a security event."""
        return self.log_event(
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            status=status,
            error_message=error_message
        )
    
    def get_audit_logs(self, skip: int = 0, limit: int = 100):
        """Get all audit logs."""
        return self.repository.get_all(skip, limit)
    
    def get_user_audit_logs(self, user_id: int, skip: int = 0, limit: int = 100):
        """Get audit logs for a specific user."""
        return self.repository.get_by_user(user_id, skip, limit)
    
    def search_audit_logs(self, filters: dict, skip: int = 0, limit: int = 100):
        """Search audit logs with filters."""
        return self.repository.search(filters, skip, limit)
    
    def get_recent_logs(self, hours: int = 24, limit: int = 100):
        """Get recent audit logs."""
        return self.repository.get_recent(hours, limit)
