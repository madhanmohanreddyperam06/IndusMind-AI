"""Service for System Monitoring."""
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import psutil
import os
from app.schemas.monitoring import (
    SystemMetrics,
    DatabaseMetrics,
    Neo4jMetrics,
    QdrantMetrics,
    AIProviderMetrics,
    StorageMetrics,
    APIMetrics,
    MonitoringDashboard
)


class MonitoringService:
    """Service for System Monitoring operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get system metrics (CPU, memory, disk, network)."""
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        network_io = None
        try:
            net_io = psutil.net_io_counters()
            network_io = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        except:
            pass
        
        return SystemMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            network_io=network_io,
            timestamp=datetime.utcnow()
        )
    
    def get_database_metrics(self) -> DatabaseMetrics:
        """Get database metrics."""
        try:
            from sqlalchemy import text
            # Get connection count
            result = self.db.execute(text("SELECT count(*) FROM pg_stat_activity"))
            connection_count = result.scalar()
            
            # Get active connections
            result = self.db.execute(text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"))
            active_connections = result.scalar()
            
            # Get database size
            result = self.db.execute(text("SELECT pg_database_size(current_database())"))
            database_size_mb = result.scalar() / (1024 * 1024)
            
            # Simulate query latency (in production, this would be measured)
            query_latency_ms = 5.0
            
            return DatabaseMetrics(
                status="healthy",
                connection_count=connection_count,
                query_latency_ms=query_latency_ms,
                active_connections=active_connections,
                database_size_mb=database_size_mb,
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            return DatabaseMetrics(
                status="unhealthy",
                connection_count=0,
                query_latency_ms=0,
                active_connections=0,
                database_size_mb=0,
                timestamp=datetime.utcnow()
            )
    
    def get_neo4j_metrics(self) -> Optional[Neo4jMetrics]:
        """Get Neo4j metrics."""
        try:
            from app.config.neo4j import get_neo4j_driver
            driver = get_neo4j_driver()
            if driver is None:
                return None
            
            with driver.session() as session:
                # Get node count
                result = session.run("MATCH (n) RETURN count(n) as count")
                node_count = result.single()["count"]
                
                # Get relationship count
                result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
                relationship_count = result.single()["count"]
                
                # Simulate query latency
                query_latency_ms = 10.0
                
                # Simulate memory usage
                memory_usage_mb = 256.0
                
                return Neo4jMetrics(
                    status="healthy",
                    node_count=node_count,
                    relationship_count=relationship_count,
                    query_latency_ms=query_latency_ms,
                    memory_usage_mb=memory_usage_mb,
                    timestamp=datetime.utcnow()
                )
        except Exception as e:
            return Neo4jMetrics(
                status="unhealthy",
                node_count=0,
                relationship_count=0,
                query_latency_ms=0,
                memory_usage_mb=0,
                timestamp=datetime.utcnow()
            )
    
    def get_qdrant_metrics(self) -> Optional[QdrantMetrics]:
        """Get Qdrant metrics."""
        try:
            from app.config.qdrant import get_qdrant_client
            client = get_qdrant_client()
            if client is None:
                return None
            
            # Get collections
            collections = client.get_collections()
            collection_count = len(collections.collections)
            
            # Get total vectors (sum across all collections)
            total_vectors = 0
            for collection in collections.collections:
                collection_info = client.get_collection(collection.name)
                total_vectors += collection_info.points_count
            
            # Simulate memory and disk usage
            memory_usage_mb = 128.0
            disk_usage_mb = 512.0
            
            return QdrantMetrics(
                status="healthy",
                collection_count=collection_count,
                total_vectors=total_vectors,
                memory_usage_mb=memory_usage_mb,
                disk_usage_mb=disk_usage_mb,
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            return QdrantMetrics(
                status="unhealthy",
                collection_count=0,
                total_vectors=0,
                memory_usage_mb=0,
                disk_usage_mb=0,
                timestamp=datetime.utcnow()
            )
    
    def get_ai_provider_metrics(self) -> AIProviderMetrics:
        """Get AI provider metrics."""
        try:
            from app.config.settings import settings
            
            if not settings.gemini_api_key:
                return AIProviderMetrics(
                    status="unconfigured",
                    provider="Google Gemini",
                    api_latency_ms=0,
                    request_count=0,
                    error_count=0,
                    timestamp=datetime.utcnow()
                )
            
            # Simulate metrics (in production, these would be tracked)
            return AIProviderMetrics(
                status="healthy",
                provider="Google Gemini",
                api_latency_ms=150.0,
                request_count=100,
                error_count=2,
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            return AIProviderMetrics(
                status="unhealthy",
                provider="Google Gemini",
                api_latency_ms=0,
                request_count=0,
                error_count=0,
                timestamp=datetime.utcnow()
            )
    
    def get_storage_metrics(self) -> StorageMetrics:
        """Get storage metrics."""
        try:
            from app.config.settings import settings
            storage_path = settings.storage_path
            
            disk = psutil.disk_usage(storage_path)
            total_space_gb = disk.total / (1024**3)
            used_space_gb = disk.used / (1024**3)
            available_space_gb = disk.free / (1024**3)
            usage_percentage = disk.percent
            
            return StorageMetrics(
                status="healthy",
                total_space_gb=total_space_gb,
                used_space_gb=used_space_gb,
                available_space_gb=available_space_gb,
                usage_percentage=usage_percentage,
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            return StorageMetrics(
                status="unhealthy",
                total_space_gb=0,
                used_space_gb=0,
                available_space_gb=0,
                usage_percentage=0,
                timestamp=datetime.utcnow()
            )
    
    def get_api_metrics(self) -> List[APIMetrics]:
        """Get API metrics (placeholder - would be tracked in production)."""
        # In production, this would query an API metrics table
        # For now, return placeholder data
        endpoints = [
            "/api/v1/auth/login",
            "/api/v1/documents",
            "/api/v1/knowledge-extraction",
            "/api/v1/graph",
            "/api/v1/rag/generate"
        ]
        
        metrics = []
        for endpoint in endpoints:
            metrics.append(APIMetrics(
                endpoint=endpoint,
                request_count=50,
                success_count=48,
                error_count=2,
                avg_latency_ms=45.0,
                p95_latency_ms=120.0,
                p99_latency_ms=250.0,
                timestamp=datetime.utcnow()
            ))
        
        return metrics
    
    def get_monitoring_dashboard(self) -> MonitoringDashboard:
        """Get comprehensive monitoring dashboard."""
        system = self.get_system_metrics()
        database = self.get_database_metrics()
        neo4j = self.get_neo4j_metrics()
        qdrant = self.get_qdrant_metrics()
        ai_provider = self.get_ai_provider_metrics()
        storage = self.get_storage_metrics()
        api_metrics = self.get_api_metrics()
        
        # Calculate overall health
        all_healthy = all([
            database.status == "healthy",
            neo4j is None or neo4j.status == "healthy",
            qdrant is None or qdrant.status == "healthy",
            ai_provider.status in ["healthy", "unconfigured"],
            storage.status == "healthy"
        ])
        
        overall_health = "healthy" if all_healthy else "degraded"
        
        return MonitoringDashboard(
            system=system,
            database=database,
            neo4j=neo4j,
            qdrant=qdrant,
            ai_provider=ai_provider,
            storage=storage,
            api_metrics=api_metrics,
            overall_health=overall_health,
            timestamp=datetime.utcnow()
        )
