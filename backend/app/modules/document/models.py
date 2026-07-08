"""Document database model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, Boolean, DateTime, JSON, Text
from sqlalchemy.dialects.mysql import CHAR
from app.database.base import Base
from app.modules.document.enums import DocumentCategory, ProcessingStatus


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
    document_category = Column(String(50), nullable=False, default=DocumentCategory.UNKNOWN, index=True)
    processing_status = Column(String(50), nullable=False, default=ProcessingStatus.UPLOADED, index=True)
    version = Column(Integer, nullable=False, default=1)
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    uploaded_by = Column(String(255), nullable=True, index=True)
    uploaded_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    future_metadata = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<Document(id={self.id}, name={self.document_name}, category={self.document_category})>"
