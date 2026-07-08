from fastapi import Depends
from sqlalchemy.orm import Session
from app.config.database import get_db


def get_db_session() -> Session:
    """Dependency to get database session. Placeholder for future implementation."""
    return next(get_db())
