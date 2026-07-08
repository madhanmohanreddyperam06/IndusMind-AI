from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.core.logging import setup_logging
from app.middleware.cors import add_cors_middleware
from app.middleware.logging import log_requests
from app.api.v1 import health, root, auth
from app.modules.document.routes import router as document_router
from app.config.database import init_db

def create_app() -> FastAPI:
    """Application factory to create FastAPI application."""
    
    # Setup logging
    logger = setup_logging()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Create FastAPI application
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Industrial Knowledge Intelligence Platform",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Add CORS middleware
    add_cors_middleware(app)
    
    # Add logging middleware
    app.middleware("http")(log_requests)
    
    # Include routers
    app.include_router(health.router)
    app.include_router(root.router)
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
    app.include_router(document_router, prefix="/api/v1/documents", tags=["documents"])
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        logger.info("Application startup")
        # Initialize database and create tables
        try:
            init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Application shutdown")
    
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
