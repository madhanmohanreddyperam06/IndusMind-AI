"""Pydantic schemas for Admin Dashboard."""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class DashboardStats(BaseModel):
    """Schema for dashboard statistics."""
    total_users: int
    active_users: int
    total_documents: int
    processed_documents: int
    total_roles: int
    total_permissions: int
    graph_nodes: int
    graph_relationships: int
    indexed_documents: int
    total_conversations: int


class SystemHealth(BaseModel):
    """Schema for system health status."""
    database: Dict[str, Any]
    neo4j: Dict[str, Any]
    qdrant: Dict[str, Any]
    ai_provider: Dict[str, Any]
    storage: Dict[str, Any]
    overall_status: str


class RecentActivity(BaseModel):
    """Schema for recent activity."""
    id: str
    user_id: int
    user_email: str
    action: str
    resource: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


class UserSummary(BaseModel):
    """Schema for user summary in dashboard."""
    id: int
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    role_count: int
    created_at: datetime


class RoleSummary(BaseModel):
    """Schema for role summary in dashboard."""
    id: str
    name: str
    description: Optional[str]
    is_active: bool
    is_system: bool
    user_count: int
    permission_count: int
