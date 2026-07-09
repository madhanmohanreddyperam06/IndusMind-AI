"""Database models for document processing module."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.config.database import Base
from app.modules.document_processing.enums import ProcessingStage, DocumentLanguage, FileType


class ProcessedDocument(Base):
    """Processed document model."""
    __tablename__ = "processed_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, unique=True)
    
    # Document metadata
    title = Column(String(500), nullable=True)
    language = Column(String(50), default=DocumentLanguage.UNKNOWN)
    page_count = Column(Integer, nullable=True)
    file_type = Column(String(20), nullable=True)
    
    # Content statistics
    word_count = Column(Integer, nullable=True)
    character_count = Column(Integer, nullable=True)
    paragraph_count = Column(Integer, nullable=True)
    table_count = Column(Integer, nullable=True)
    image_count = Column(Integer, nullable=True)
    section_count = Column(Integer, nullable=True)
    
    # Text content
    raw_text = Column(Text, nullable=True)
    normalized_text = Column(Text, nullable=True)
    
    # Processing information
    processing_stage = Column(String(50), default=ProcessingStage.UPLOADED)
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    processing_duration_seconds = Column(Float, nullable=True)
    parser_used = Column(String(100), nullable=True)
    ocr_used = Column(Boolean, default=False)
    ocr_provider = Column(String(50), nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_stage = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sections = relationship("DocumentSection", back_populates="document", cascade="all, delete-orphan")
    paragraphs = relationship("DocumentParagraph", back_populates="document", cascade="all, delete-orphan")
    tables = relationship("DocumentTable", back_populates="document", cascade="all, delete-orphan")
    images = relationship("DocumentImage", back_populates="document", cascade="all, delete-orphan")
    doc_metadata = relationship("DocumentMetadata", back_populates="document", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ProcessedDocument(id={self.id}, document_id={self.document_id}, title={self.title})>"


class DocumentSection(Base):
    """Document section model."""
    __tablename__ = "document_sections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    processed_document_id = Column(String(36), ForeignKey("processed_documents.id"), nullable=False)
    
    title = Column(String(500), nullable=True)
    level = Column(Integer, nullable=True)  # Heading level (1, 2, 3, etc.)
    page_number = Column(Integer, nullable=True)
    content = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=True)  # Order within document
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("ProcessedDocument", back_populates="sections")
    
    def __repr__(self):
        return f"<DocumentSection(id={self.id}, title={self.title}, level={self.level})>"


class DocumentParagraph(Base):
    """Document paragraph model."""
    __tablename__ = "document_paragraphs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    processed_document_id = Column(String(36), ForeignKey("processed_documents.id"), nullable=False)
    section_id = Column(String(36), ForeignKey("document_sections.id"), nullable=True)
    
    text = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    
    # Position information
    bbox_x0 = Column(Float, nullable=True)
    bbox_y0 = Column(Float, nullable=True)
    bbox_x1 = Column(Float, nullable=True)
    bbox_y1 = Column(Float, nullable=True)
    
    # Paragraph metadata
    font_size = Column(Float, nullable=True)
    font_name = Column(String(100), nullable=True)
    is_heading = Column(Boolean, default=False)
    heading_level = Column(Integer, nullable=True)
    
    order_index = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("ProcessedDocument", back_populates="paragraphs")
    
    def __repr__(self):
        return f"<DocumentParagraph(id={self.id}, page={self.page_number})>"


class DocumentTable(Base):
    """Document table model."""
    __tablename__ = "document_tables"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    processed_document_id = Column(String(36), ForeignKey("processed_documents.id"), nullable=False)
    
    page_number = Column(Integer, nullable=True)
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    
    # Table content
    headers = Column(JSON, nullable=True)  # List of header strings
    rows = Column(JSON, nullable=True)  # List of row lists
    raw_html = Column(Text, nullable=True)
    csv_representation = Column(Text, nullable=True)
    
    # Position information
    bbox_x0 = Column(Float, nullable=True)
    bbox_y0 = Column(Float, nullable=True)
    bbox_x1 = Column(Float, nullable=True)
    bbox_y1 = Column(Float, nullable=True)
    
    order_index = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("ProcessedDocument", back_populates="tables")
    
    def __repr__(self):
        return f"<DocumentTable(id={self.id}, page={self.page_number}, rows={self.row_count})>"


class DocumentImage(Base):
    """Document image model."""
    __tablename__ = "document_images"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    processed_document_id = Column(String(36), ForeignKey("processed_documents.id"), nullable=False)
    
    page_number = Column(Integer, nullable=True)
    caption = Column(Text, nullable=True)
    image_path = Column(String(500), nullable=True)  # Path to extracted image
    
    # Image metadata
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    format = Column(String(10), nullable=True)  # PNG, JPEG, etc.
    
    # Position information
    bbox_x0 = Column(Float, nullable=True)
    bbox_y0 = Column(Float, nullable=True)
    bbox_x1 = Column(Float, nullable=True)
    bbox_y1 = Column(Float, nullable=True)
    
    order_index = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("ProcessedDocument", back_populates="images")
    
    def __repr__(self):
        return f"<DocumentImage(id={self.id}, page={self.page_number})>"


class DocumentMetadata(Base):
    """Document metadata model."""
    __tablename__ = "document_metadata"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    processed_document_id = Column(String(36), ForeignKey("processed_documents.id"), nullable=False, unique=True)
    
    # Author information
    author = Column(String(500), nullable=True)
    
    # Date information
    creation_date = Column(DateTime, nullable=True)
    modification_date = Column(DateTime, nullable=True)
    
    # Document properties
    document_version = Column(String(100), nullable=True)
    subject = Column(String(500), nullable=True)
    keywords = Column(Text, nullable=True)  # Comma-separated
    
    # Additional metadata (flexible JSON for extra fields)
    additional_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    document = relationship("ProcessedDocument", back_populates="doc_metadata")
    
    def __repr__(self):
        return f"<DocumentMetadata(id={self.id}, author={self.author})>"
