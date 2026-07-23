"""Repository for Audit Log model."""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.audit_log import AuditLog


class AuditLogRepository:
    """Repository for Audit Log data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, audit_log: AuditLog) -> AuditLog:
        """Create a new audit log entry."""
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        return audit_log
    
    def get_by_id(self, log_id: str) -> Optional[AuditLog]:
        """Get audit log by ID."""
        return self.db.query(AuditLog).filter(AuditLog.id == log_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get all audit logs with pagination."""
        return self.db.query(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a specific user."""
        return self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    def get_by_action(self, action: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs by action type."""
        return self.db.query(AuditLog).filter(
            AuditLog.action == action
        ).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    def get_by_resource_type(self, resource_type: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs by resource type."""
        return self.db.query(AuditLog).filter(
            AuditLog.resource_type == resource_type
        ).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs within a date range."""
        return self.db.query(AuditLog).filter(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date
        ).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    def get_recent(self, hours: int = 24, limit: int = 100) -> List[AuditLog]:
        """Get audit logs from the last N hours."""
        start_date = datetime.utcnow() - timedelta(hours=hours)
        return self.db.query(AuditLog).filter(
            AuditLog.timestamp >= start_date
        ).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    def search(self, filters: dict, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Search audit logs with multiple filters."""
        query = self.db.query(AuditLog)
        
        if filters.get("user_id"):
            query = query.filter(AuditLog.user_id == filters["user_id"])
        
        if filters.get("action"):
            query = query.filter(AuditLog.action == filters["action"])
        
        if filters.get("resource_type"):
            query = query.filter(AuditLog.resource_type == filters["resource_type"])
        
        if filters.get("resource_id"):
            query = query.filter(AuditLog.resource_id == filters["resource_id"])
        
        if filters.get("status"):
            query = query.filter(AuditLog.status == filters["status"])
        
        if filters.get("start_date"):
            query = query.filter(AuditLog.timestamp >= filters["start_date"])
        
        if filters.get("end_date"):
            query = query.filter(AuditLog.timestamp <= filters["end_date"])
        
        return query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    def delete_old_logs(self, days: int = 90) -> int:
        """Delete audit logs older than N days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        count = self.db.query(AuditLog).filter(AuditLog.timestamp < cutoff_date).count()
        self.db.query(AuditLog).filter(AuditLog.timestamp < cutoff_date).delete()
        self.db.commit()
        return count
