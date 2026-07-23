"""Migration: Add enhanced file type support to documents table.

This migration adds new fields to support enterprise file types:
- file_category: New file category (DOCUMENT, SPREADSHEET, etc.)
- detected_mime_type: MIME type detected from magic bytes
- original_extension: Original extension before sanitization
- parser_used: Parser used for processing
- processing_capability: Processing capability level
- preview_available: Whether preview is available
- extracted_pages: Number of extracted pages
- extracted_tables: Number of extracted tables
- extracted_images: Number of extracted images
- extracted_sheets: Number of extracted sheets
- upload_source: Source of upload (web, api, etc.)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.config.database import get_db


def upgrade():
    """Add new columns to documents table."""
    db = next(get_db())
    
    try:
        # Add new columns
        db.execute(text("""
            ALTER TABLE documents 
            ADD COLUMN file_category VARCHAR(50) NULL COMMENT 'New file category (DOCUMENT, SPREADSHEET, etc.)',
            ADD INDEX idx_file_category (file_category)
        """))
        
        db.execute(text("""
            ALTER TABLE documents 
            ADD COLUMN detected_mime_type VARCHAR(100) NULL COMMENT 'MIME type detected from magic bytes'
        """))
        
        db.execute(text("""
            ALTER TABLE documents 
            ADD COLUMN original_extension VARCHAR(10) NULL COMMENT 'Original extension before sanitization'
        """))
        
        db.execute(text("""
            ALTER TABLE documents 
            ADD COLUMN parser_used VARCHAR(100) NULL COMMENT 'Parser used for processing'
        """))
        
        db.execute(text("""
            ALTER TABLE documents 
            ADD COLUMN processing_capability VARCHAR(50) NOT NULL DEFAULT 'FULL' COMMENT 'Processing capability level'
        """))
        
        db.execute(text("""
            ALTER TABLE documents 
            ADD COLUMN preview_available BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Whether preview is available'
        """))
        
        db.execute(text("""
            ALTER TABLE documents 
            ADD COLUMN extracted_pages INT NULL COMMENT 'Number of extracted pages'
        """))
        
        db.execute(text("""
            ALTER TABLE documents 
            ADD COLUMN extracted_tables INT NULL COMMENT 'Number of extracted tables'
        """))
        
        db.execute(text("""
            ALTER TABLE documents 
            ADD COLUMN extracted_images INT NULL COMMENT 'Number of extracted images'
        """))
        
        db.execute(text("""
            ALTER TABLE documents 
            ADD COLUMN extracted_sheets INT NULL COMMENT 'Number of extracted sheets'
        """))
        
        db.execute(text("""
            ALTER TABLE documents 
            ADD COLUMN upload_source VARCHAR(50) NULL COMMENT 'Source of upload (web, api, etc.)'
        """))
        
        db.commit()
        print("Migration completed successfully: Added enhanced file type support fields")
        
    except Exception as e:
        db.rollback()
        print(f"Migration failed: {str(e)}")
        raise
    finally:
        db.close()


def downgrade():
    """Remove new columns from documents table."""
    db = next(get_db())
    
    try:
        # Drop new columns
        db.execute(text("ALTER TABLE documents DROP COLUMN file_category"))
        db.execute(text("ALTER TABLE documents DROP COLUMN detected_mime_type"))
        db.execute(text("ALTER TABLE documents DROP COLUMN original_extension"))
        db.execute(text("ALTER TABLE documents DROP COLUMN parser_used"))
        db.execute(text("ALTER TABLE documents DROP COLUMN processing_capability"))
        db.execute(text("ALTER TABLE documents DROP COLUMN preview_available"))
        db.execute(text("ALTER TABLE documents DROP COLUMN extracted_pages"))
        db.execute(text("ALTER TABLE documents DROP COLUMN extracted_tables"))
        db.execute(text("ALTER TABLE documents DROP COLUMN extracted_images"))
        db.execute(text("ALTER TABLE documents DROP COLUMN extracted_sheets"))
        db.execute(text("ALTER TABLE documents DROP COLUMN upload_source"))
        
        db.commit()
        print("Rollback completed successfully: Removed enhanced file type support fields")
        
    except Exception as e:
        db.rollback()
        print(f"Rollback failed: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Running migration: Add enhanced file type support")
    upgrade()
