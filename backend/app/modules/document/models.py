"""Document database model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, Boolean, DateTime, JSON, Text
from sqlalchemy.dialects.mysql import CHAR
from app.database.base import Base
from app.modules.document.enums import DocumentCategory, ProcessingStatus, FileCategory, ProcessingCapability


class Document(Base):
    """Document model for document management."""
    
    __tablename__ = "documents"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_name = Column(String(255), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    extension = Column(String(10), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    checksum = Column(String(64), nullable=False, unique=True, index=True)
    storage_path = Column(String(500), nullable=False)
    
    # New fields for enhanced file type support
    file_category = Column(String(50), nullable=True, index=True)  # New file category (DOCUMENT, SPREADSHEET, etc.)
    detected_mime_type = Column(String(100), nullable=True)  # MIME type detected from magic bytes
    original_extension = Column(String(10), nullable=True)  # Original extension before sanitization
    parser_used = Column(String(100), nullable=True)  # Parser used for processing
    processing_capability = Column(String(50), nullable=False, default='FULL')  # Processing capability level
    preview_available = Column(Boolean, nullable=False, default=False)  # Whether preview is available
    
    # Extraction statistics
    extracted_pages = Column(Integer, nullable=True)
    extracted_tables = Column(Integer, nullable=True)
    extracted_images = Column(Integer, nullable=True)
    extracted_sheets = Column(Integer, nullable=True)
    
    # Legacy fields (for backward compatibility)
    document_category = Column(String(50), nullable=False, default=DocumentCategory.UNKNOWN, index=True)
    processing_status = Column(String(50), nullable=False, default=ProcessingStatus.UPLOADED, index=True)
    version = Column(Integer, nullable=False, default=1)
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    uploaded_by = Column(String(255), nullable=True, index=True)
    upload_source = Column(String(50), nullable=True)  # Source of upload (web, api, etc.)
    uploaded_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    future_metadata = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<Document(id={self.id}, name={self.document_name}, file_category={self.file_category})>"

