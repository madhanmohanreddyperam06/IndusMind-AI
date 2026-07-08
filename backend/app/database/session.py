from sqlalchemy.orm import Session
from app.config.database import engine, SessionLocal


def get_session() -> Session:
    """Get database session. Placeholder for future implementation."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
