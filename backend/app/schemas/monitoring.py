"""Pydantic schemas for System Monitoring."""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class MetricData(BaseModel):
    """Schema for metric data point."""
    timestamp: datetime
    value: float
    metadata: Optional[Dict[str, Any]] = None


class SystemMetrics(BaseModel):
    """Schema for system metrics."""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Optional[Dict[str, float]] = None
    timestamp: datetime


class DatabaseMetrics(BaseModel):
    """Schema for database metrics."""
    status: str
    connection_count: int
    query_latency_ms: float
    active_connections: int
    database_size_mb: float
    timestamp: datetime


class Neo4jMetrics(BaseModel):
    """Schema for Neo4j metrics."""
    status: str
    node_count: int
    relationship_count: int
    query_latency_ms: float
    memory_usage_mb: float
    timestamp: datetime


class QdrantMetrics(BaseModel):
    """Schema for Qdrant metrics."""
    status: str
    collection_count: int
    total_vectors: int
    memory_usage_mb: float
    disk_usage_mb: float
    timestamp: datetime


class AIProviderMetrics(BaseModel):
    """Schema for AI provider metrics."""
    status: str
    provider: str
    api_latency_ms: float
    request_count: int
    error_count: int
    timestamp: datetime


class StorageMetrics(BaseModel):
    """Schema for storage metrics."""
    status: str
    total_space_gb: float
    used_space_gb: float
    available_space_gb: float
    usage_percentage: float
    timestamp: datetime


class APIMetrics(BaseModel):
    """Schema for API metrics."""
    endpoint: str
    request_count: int
    success_count: int
    error_count: int
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    timestamp: datetime


class MonitoringDashboard(BaseModel):
    """Schema for monitoring dashboard."""
    system: SystemMetrics
    database: DatabaseMetrics
    neo4j: Optional[Neo4jMetrics] = None
    qdrant: Optional[QdrantMetrics] = None
    ai_provider: AIProviderMetrics
    storage: StorageMetrics
    api_metrics: List[APIMetrics] = []
    overall_health: str
    timestamp: datetime
