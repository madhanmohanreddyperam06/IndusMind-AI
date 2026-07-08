"""Document schemas for API requests and responses."""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from app.modules.document.enums import DocumentCategory, ProcessingStatus


class DocumentBase(BaseModel):
    """Base document schema."""
    document_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    tags: Optional[List[str]] = None
    document_category: DocumentCategory = DocumentCategory.UNKNOWN


class DocumentCreate(DocumentBase):
    """Schema for document creation (upload)."""
    original_filename: str = Field(..., min_length=1, max_length=255)
    mime_type: str = Field(..., min_length=1, max_length=100)
    extension: str = Field(..., min_length=1, max_length=10)
    file_size: int = Field(..., gt=0)
    checksum: str = Field(..., min_length=64, max_length=64)
    storage_path: str = Field(..., min_length=1, max_length=500)
    uploaded_by: Optional[str] = None


class DocumentUpdate(BaseModel):
    """Schema for document metadata update."""
    document_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    tags: Optional[List[str]] = None
    document_category: Optional[DocumentCategory] = None


class DocumentResponse(BaseModel):
    """Schema for document response."""
    id: str
    document_name: str
    original_filename: str
    mime_type: str
    extension: str
    file_size: int
    checksum: str
    storage_path: str
    document_category: DocumentCategory
    processing_status: ProcessingStatus
    version: int
    description: Optional[str]
    tags: Optional[List[str]]
    uploaded_by: Optional[str]
    uploaded_at: datetime
    updated_at: Optional[datetime]
    is_deleted: bool
    processing_started_at: Optional[datetime]
    processing_completed_at: Optional[datetime]
    last_accessed: Optional[datetime]
    future_metadata: Optional[dict]
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for document list response."""
    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class UploadResponse(BaseModel):
    """Schema for upload response."""
    document: DocumentResponse
    message: str


class DocumentSearchFilters(BaseModel):
    """Schema for document search filters."""
    filename: Optional[str] = None
    category: Optional[DocumentCategory] = None
    status: Optional[ProcessingStatus] = None
    uploaded_by: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class DocumentDeleteResponse(BaseModel):
    """Schema for document delete response."""
    message: str
    document_id: str
