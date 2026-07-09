from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings
from urllib.parse import quote_plus

# URL-encode the password to handle special characters
encoded_password = quote_plus(settings.mysql_password if hasattr(settings, 'mysql_password') else 'Madhanreddy@123')

# Construct connection URL from individual components
mysql_url = f"mysql+pymysql://{settings.mysql_user if hasattr(settings, 'mysql_user') else 'root'}:{encoded_password}@{settings.mysql_host if hasattr(settings, 'mysql_host') else 'localhost'}:{settings.mysql_port if hasattr(settings, 'mysql_port') else 3306}/{settings.mysql_database if hasattr(settings, 'mysql_database') else 'indusmind'}"

# SQLAlchemy engine
engine = create_engine(
    mysql_url,
    pool_pre_ping=True,
    echo=settings.debug
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def init_db():
    """Initialize database connection and create tables."""
    from app.models import user  # Import models to ensure they're registered
    from app.modules.document import models  # Import document models
    from app.modules.document_processing import models as processing_models  # Import document processing models
    
    # Create tables if they don't exist (preserves existing data)
    Base.metadata.create_all(bind=engine)


def reset_users_table():
    """Drop and recreate the users table with new schema."""
    from app.models import user
    from sqlalchemy import text
    
    # Drop the users table if it exists
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS users"))
        conn.commit()
    
    # Recreate with new schema
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
