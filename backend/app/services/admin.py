"""Service for Admin Dashboard business logic."""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from datetime import datetime, timedelta
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission
from app.repositories.user import get_user_by_email
from app.schemas.admin import DashboardStats, SystemHealth, UserSummary, RoleSummary


class AdminService:
    """Service for Admin Dashboard operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_stats(self) -> DashboardStats:
        """Get dashboard statistics."""
        # User stats
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        
        # Document stats (placeholder - will be updated when document model is available)
        total_documents = 0
        processed_documents = 0
        
        # RBAC stats
        total_roles = self.db.query(Role).filter(Role.is_active == True).count()
        total_permissions = self.db.query(Permission).count()
        
        # Graph stats (placeholder - will be updated with Neo4j integration)
        graph_nodes = 0
        graph_relationships = 0
        
        # Embedding stats (placeholder)
        indexed_documents = 0
        
        # RAG stats (placeholder)
        total_conversations = 0
        
        return DashboardStats(
            total_users=total_users,
            active_users=active_users,
            total_documents=total_documents,
            processed_documents=processed_documents,
            total_roles=total_roles,
            total_permissions=total_permissions,
            graph_nodes=graph_nodes,
            graph_relationships=graph_relationships,
            indexed_documents=indexed_documents,
            total_conversations=total_conversations
        )
    
    def get_system_health(self) -> SystemHealth:
        """Get system health status."""
        # Database health
        db_health = self._check_database_health()
        
        # Neo4j health
        neo4j_health = self._check_neo4j_health()
        
        # Qdrant health
        qdrant_health = self._check_qdrant_health()
        
        # AI Provider health
        ai_health = self._check_ai_provider_health()
        
        # Storage health
        storage_health = self._check_storage_health()
        
        # Overall status
        all_healthy = all([
            db_health.get("status") == "healthy",
            neo4j_health.get("status") in ["healthy", "disabled"],
            qdrant_health.get("status") in ["healthy", "disabled"],
            ai_health.get("status") == "healthy",
            storage_health.get("status") == "healthy"
        ])
        
        overall_status = "healthy" if all_healthy else "degraded"
        
        return SystemHealth(
            database=db_health,
            neo4j=neo4j_health,
            qdrant=qdrant_health,
            ai_provider=ai_health,
            storage=storage_health,
            overall_status=overall_status
        )
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database health."""
        try:
            # Simple query to check connection
            self.db.execute(func.text("SELECT 1"))
            return {
                "status": "healthy",
                "message": "Database connection successful",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _check_neo4j_health(self) -> Dict[str, Any]:
        """Check Neo4j health."""
        try:
            from app.config.neo4j import get_neo4j_driver
            driver = get_neo4j_driver()
            if driver is None:
                return {
                    "status": "disabled",
                    "message": "Neo4j is not configured",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            with driver.session() as session:
                session.run("RETURN 1")
                return {
                    "status": "healthy",
                    "message": "Neo4j connection successful",
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Neo4j connection failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _check_qdrant_health(self) -> Dict[str, Any]:
        """Check Qdrant health."""
        try:
            from app.config.qdrant import get_qdrant_client
            client = get_qdrant_client()
            if client is None:
                return {
                    "status": "disabled",
                    "message": "Qdrant is not configured",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Simple health check
            client.get_collections()
            return {
                "status": "healthy",
                "message": "Qdrant connection successful",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Qdrant connection failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _check_ai_provider_health(self) -> Dict[str, Any]:
        """Check AI Provider health."""
        try:
            from app.config.settings import settings
            if not settings.gemini_api_key:
                return {
                    "status": "unhealthy",
                    "message": "AI provider API key not configured",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return {
                "status": "healthy",
                "message": "AI provider configured",
                "provider": "Google Gemini",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"AI provider check failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _check_storage_health(self) -> Dict[str, Any]:
        """Check storage health."""
        try:
            from app.config.settings import settings
            import os
            
            storage_path = settings.storage_path
            if not os.path.exists(storage_path):
                return {
                    "status": "unhealthy",
                    "message": f"Storage path does not exist: {storage_path}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Check if writable
            test_file = os.path.join(storage_path, ".health_check")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
            except Exception:
                return {
                    "status": "unhealthy",
                    "message": "Storage path is not writable",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return {
                "status": "healthy",
                "message": "Storage is accessible and writable",
                "path": storage_path,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Storage check failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_user_summaries(self, skip: int = 0, limit: int = 10) -> List[UserSummary]:
        """Get user summaries for dashboard."""
        users = self.db.query(User).offset(skip).limit(limit).all()
        summaries = []
        
        for user in users:
            role_count = self.db.query(UserRole).filter(UserRole.user_id == user.id).count()
            summaries.append(UserSummary(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                role_count=role_count,
                created_at=user.created_at
            ))
        
        return summaries
    
    def get_role_summaries(self, skip: int = 0, limit: int = 10) -> List[RoleSummary]:
        """Get role summaries for dashboard."""
        roles = self.db.query(Role).filter(Role.is_active == True).offset(skip).limit(limit).all()
        summaries = []
        
        for role in roles:
            user_count = self.db.query(UserRole).filter(UserRole.role_id == role.id).count()
            permission_count = self.db.query(RolePermission).filter(RolePermission.role_id == role.id).count()
            summaries.append(RoleSummary(
                id=role.id,
                name=role.name,
                description=role.description,
                is_active=role.is_active,
                is_system=role.is_system,
                user_count=user_count,
                permission_count=permission_count
            ))
        
        return summaries
