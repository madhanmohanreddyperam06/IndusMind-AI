"""Pydantic schemas for document processing module."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.modules.document_processing.enums import ProcessingStage, DocumentLanguage, FileType


# ============================================================================
# Canonical Document Model Schemas
# ============================================================================

class BoundingBox(BaseModel):
    """Bounding box for positioning information."""
    x0: Optional[float] = None
    y0: Optional[float] = None
    x1: Optional[float] = None
    y1: Optional[float] = None


class ParagraphSchema(BaseModel):
    """Paragraph schema."""
    paragraph_id: str
    page: Optional[int] = None
    text: str
    position: Optional[BoundingBox] = None
    section: Optional[str] = None  # Section title or ID
    font_size: Optional[float] = None
    font_name: Optional[str] = None
    is_heading: bool = False
    heading_level: Optional[int] = None
    order_index: Optional[int] = None


class SectionSchema(BaseModel):
    """Section schema."""
    title: Optional[str] = None
    level: Optional[int] = None  # Heading level (1, 2, 3, etc.)
    page_number: Optional[int] = None
    content: Optional[str] = None
    paragraph_ids: List[str] = Field(default_factory=list)
    order_index: Optional[int] = None


class TableSchema(BaseModel):
    """Table schema."""
    table_id: str
    page: Optional[int] = None
    headers: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)
    raw_html: Optional[str] = None
    csv_representation: Optional[str] = None
    position: Optional[BoundingBox] = None
    order_index: Optional[int] = None


class ImageSchema(BaseModel):
    """Image schema."""
    image_id: str
    page: Optional[int] = None
    caption: Optional[str] = None
    path: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None  # PNG, JPEG, etc.
    position: Optional[BoundingBox] = None
    order_index: Optional[int] = None


class DocumentMetadataSchema(BaseModel):
    """Document metadata schema."""
    title: Optional[str] = None
    author: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    language: DocumentLanguage = DocumentLanguage.UNKNOWN
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    character_count: Optional[int] = None
    estimated_reading_time: Optional[int] = None  # in minutes
    document_version: Optional[str] = None
    subject: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    additional_metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentStatistics(BaseModel):
    """Document statistics schema."""
    pages: int
    words: int
    characters: int
    paragraphs: int
    tables: int
    images: int
    sections: int


class ProcessingInformation(BaseModel):
    """Processing information schema."""
    parser_used: Optional[str] = None
    ocr_used: bool = False
    ocr_provider: Optional[str] = None
    processing_duration_seconds: Optional[float] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None


class CanonicalDocument(BaseModel):
    """Canonical document model - the output of every parser."""
    id: str
    document_id: str  # Reference to original document
    title: Optional[str] = None
    language: DocumentLanguage = DocumentLanguage.UNKNOWN
    page_count: Optional[int] = None
    
    # Structured content
    sections: List[SectionSchema] = Field(default_factory=list)
    paragraphs: List[ParagraphSchema] = Field(default_factory=list)
    tables: List[TableSchema] = Field(default_factory=list)
    images: List[ImageSchema] = Field(default_factory=list)
    
    # Metadata
    metadata: DocumentMetadataSchema = Field(default_factory=DocumentMetadataSchema)
    statistics: Optional[DocumentStatistics] = None
    
    # Text content
    raw_text: Optional[str] = None
    normalized_text: Optional[str] = None
    
    # Processing information
    processing_information: ProcessingInformation = Field(default_factory=ProcessingInformation)


# ============================================================================
# API Request/Response Schemas
# ============================================================================

class ProcessDocumentRequest(BaseModel):
    """Request to process a document."""
    force_reprocess: bool = False


class ProcessAllRequest(BaseModel):
    """Request to process all documents."""
    force_reprocess: bool = False


class ProcessingStatusResponse(BaseModel):
    """Processing status response."""
    document_id: str
    processing_stage: ProcessingStage
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_duration_seconds: Optional[float] = None
    parser_used: Optional[str] = None
    ocr_used: bool = False
    ocr_provider: Optional[str] = None
    error_message: Optional[str] = None
    error_stage: Optional[str] = None


class DocumentStatisticsResponse(BaseModel):
    """Document statistics response."""
    document_id: str
    page_count: int
    word_count: int
    character_count: int
    paragraph_count: int
    table_count: int
    image_count: int
    section_count: int
    language: DocumentLanguage
    estimated_reading_time: Optional[int] = None


class ProcessedDocumentResponse(BaseModel):
    """Processed document response."""
    id: str
    document_id: str
    title: Optional[str] = None
    language: DocumentLanguage
    page_count: Optional[int] = None
    raw_text: Optional[str] = None
    normalized_text: Optional[str] = None
    sections: List[SectionSchema] = Field(default_factory=list)
    paragraphs: List[ParagraphSchema] = Field(default_factory=list)
    tables: List[TableSchema] = Field(default_factory=list)
    images: List[ImageSchema] = Field(default_factory=list)
    metadata: DocumentMetadataSchema
    statistics: Optional[DocumentStatistics] = None
    processing_information: ProcessingInformation
    created_at: datetime
    updated_at: datetime


class ProcessingQueueItem(BaseModel):
    """Processing queue item."""
    document_id: str
    status: ProcessingStage
    queued_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


# ============================================================================
# Database Model Schemas (for CRUD operations)
# ============================================================================

class ProcessedDocumentCreate(BaseModel):
    """Schema for creating processed document."""
    document_id: str
    title: Optional[str] = None
    language: DocumentLanguage = DocumentLanguage.UNKNOWN
    page_count: Optional[int] = None
    file_type: Optional[str] = None
    raw_text: Optional[str] = None
    normalized_text: Optional[str] = None
    processing_stage: ProcessingStage = ProcessingStage.UPLOADED


class ProcessedDocumentUpdate(BaseModel):
    """Schema for updating processed document."""
    title: Optional[str] = None
    language: Optional[DocumentLanguage] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    character_count: Optional[int] = None
    paragraph_count: Optional[int] = None
    table_count: Optional[int] = None
    image_count: Optional[int] = None
    section_count: Optional[int] = None
    raw_text: Optional[str] = None
    normalized_text: Optional[str] = None
    processing_stage: Optional[ProcessingStage] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_duration_seconds: Optional[float] = None
    parser_used: Optional[str] = None
    ocr_used: Optional[bool] = None
    ocr_provider: Optional[str] = None
    error_message: Optional[str] = None
    error_stage: Optional[str] = None


class DocumentSectionCreate(BaseModel):
    """Schema for creating document section."""
    processed_document_id: str
    title: Optional[str] = None
    level: Optional[int] = None
    page_number: Optional[int] = None
    content: Optional[str] = None
    order_index: Optional[int] = None


class DocumentParagraphCreate(BaseModel):
    """Schema for creating document paragraph."""
    processed_document_id: str
    section_id: Optional[str] = None
    text: str
    page_number: Optional[int] = None
    bbox_x0: Optional[float] = None
    bbox_y0: Optional[float] = None
    bbox_x1: Optional[float] = None
    bbox_y1: Optional[float] = None
    font_size: Optional[float] = None
    font_name: Optional[str] = None
    is_heading: bool = False
    heading_level: Optional[int] = None
    order_index: Optional[int] = None


class DocumentTableCreate(BaseModel):
    """Schema for creating document table."""
    processed_document_id: str
    page_number: Optional[int] = None
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    headers: Optional[List[str]] = None
    rows: Optional[List[List[str]]] = None
    raw_html: Optional[str] = None
    csv_representation: Optional[str] = None
    bbox_x0: Optional[float] = None
    bbox_y0: Optional[float] = None
    bbox_x1: Optional[float] = None
    bbox_y1: Optional[float] = None
    order_index: Optional[int] = None


class DocumentImageCreate(BaseModel):
    """Schema for creating document image."""
    processed_document_id: str
    page_number: Optional[int] = None
    caption: Optional[str] = None
    image_path: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    bbox_x0: Optional[float] = None
    bbox_y0: Optional[float] = None
    bbox_x1: Optional[float] = None
    bbox_y1: Optional[float] = None
    order_index: Optional[int] = None


class DocumentMetadataCreate(BaseModel):
    """Schema for creating document metadata."""
    processed_document_id: str
    author: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    document_version: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[str] = None
    additional_metadata: Optional[Dict[str, Any]] = None


class DocumentMetadataUpdate(BaseModel):
    """Schema for updating document metadata."""
    author: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    document_version: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[str] = None
    additional_metadata: Optional[Dict[str, Any]] = None
