from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings


def add_cors_middleware(app):
    """Add CORS middleware to the application. Placeholder for future implementation."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
