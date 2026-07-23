from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.settings import settings
from app.core.logging import setup_logging
from app.core.exceptions import register_exception_handlers
from app.middleware.cors import add_cors_middleware
from app.middleware.logging import log_requests
from app.api.v1 import health, root, auth, roles, permissions, user_roles, role_permissions, admin, users, profile, password_reset, audit_logs, monitoring, notifications
from app.modules.document.routes import router as document_router
from app.modules.document_processing.routes import router as document_processing_router
from app.modules.knowledge_extraction.routes import router as knowledge_extraction_router
from app.modules.knowledge_graph.routes import router as knowledge_graph_router
from app.modules.embedding_pipeline.routes import router as embedding_pipeline_router
from app.modules.hybrid_retrieval.routes import router as hybrid_retrieval_router
from app.modules.rag_engine.routes import router as rag_engine_router
from app.config.database import init_db
from app.config.neo4j import init_neo4j, close_neo4j
from app.config.qdrant import init_qdrant, close_qdrant

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown events."""
    logger = setup_logging()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Startup
    logger.info("Application startup")
    # Initialize database and create tables
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    # Initialize Neo4j connection
    try:
        init_neo4j()
        logger.info("Neo4j initialized successfully")
    except Exception as e:
        logger.warning(f"Neo4j initialization failed - some features may be unavailable: {e}")
    
    # Initialize Qdrant connection
    try:
        init_qdrant()
        logger.info("Qdrant initialized successfully")
    except Exception as e:
        logger.warning(f"Qdrant initialization failed - some features may be unavailable: {e}")
    
    yield
    
    # Shutdown
    logger.info("Application shutdown")
    # Close Neo4j connection
    try:
        close_neo4j()
        logger.info("Neo4j connection closed")
    except Exception as e:
        logger.error(f"Error closing Neo4j connection: {e}")
    
    # Close Qdrant connection
    try:
        close_qdrant()
        logger.info("Qdrant connection closed")
    except Exception as e:
        logger.error(f"Error closing Qdrant connection: {e}")

def create_app() -> FastAPI:
    """Application factory to create FastAPI application."""
    
    # Setup logging
    logger = setup_logging()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Create FastAPI application with lifespan
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Industrial Knowledge Intelligence Platform",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    add_cors_middleware(app)
    
    # Add logging middleware
    app.middleware("http")(log_requests)
    
    # Register exception handlers
    register_exception_handlers(app)
    
    # Include routers with consistent prefixes and tags
    app.include_router(health.router)
    app.include_router(root.router)
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(password_reset.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(profile.router, prefix="/api/v1/profile", tags=["Profile"])
    app.include_router(roles.router, prefix="/api/v1/roles", tags=["Roles"])
    app.include_router(permissions.router, prefix="/api/v1/permissions", tags=["Permissions"])
    app.include_router(user_roles.router, prefix="/api/v1/user-roles", tags=["User Roles"])
    app.include_router(role_permissions.router, prefix="/api/v1/role-permissions", tags=["Role Permissions"])
    app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(audit_logs.router, prefix="/api/v1/audit-logs", tags=["Audit Logs"])
    app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["Monitoring"])
    app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
    app.include_router(document_router, prefix="/api/v1/documents", tags=["Documents"])
    app.include_router(document_processing_router, prefix="/api/v1/document-processing", tags=["Document Processing"])
    app.include_router(knowledge_extraction_router, prefix="/api/v1/knowledge-extraction", tags=["Knowledge Extraction"])
    app.include_router(knowledge_graph_router, prefix="/api/v1/graph", tags=["Knowledge Graph"])
    app.include_router(embedding_pipeline_router, prefix="/api/v1/embeddings", tags=["Embeddings"])
    app.include_router(hybrid_retrieval_router, prefix="/api/v1/retrieval", tags=["Hybrid Retrieval"])
    app.include_router(rag_engine_router, prefix="/api/v1/rag", tags=["RAG Engine"])
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
