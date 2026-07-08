"""Document service for business logic."""
import uuid
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from app.modules.document.repository import DocumentRepository
from app.modules.document.schemas import (
    DocumentCreate,
    DocumentUpdate,
    DocumentSearchFilters,
    DocumentResponse,
    DocumentListResponse
)
from app.modules.document.storage import LocalStorageProvider, StorageProvider
from app.modules.document.validators import FileValidator
from app.modules.document.enums import ProcessingStatus
from app.modules.document.exceptions import (
    DocumentNotFoundException,
    DuplicateFileException,
    StorageException
)
from app.modules.document.constants import DOCUMENTS_STORAGE_DIR


class DocumentService:
    """Service for document business logic."""
    
    def __init__(self, db: Session, storage_provider: Optional[StorageProvider] = None):
        """Initialize document service.
        
        Args:
            db: Database session
            storage_provider: Storage provider (defaults to LocalStorageProvider)
        """
        self.db = db
        self.repository = DocumentRepository(db)
        self.storage = storage_provider or LocalStorageProvider(DOCUMENTS_STORAGE_DIR)
    
    async def upload_document(
        self,
        filename: str,
        content: bytes,
        mime_type: str,
        document_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        uploaded_by: Optional[str] = None
    ) -> DocumentResponse:
        """Upload a new document.
        
        Args:
            filename: Original filename
            content: File content as bytes
            mime_type: MIME type
            document_name: Display name for document
            description: Document description
            tags: Document tags
            category: Document category
            uploaded_by: User who uploaded the document
            
        Returns:
            Created document response
            
        Raises:
            FileSizeExceededException: If file size exceeds limit
            InvalidFileTypeException: If file type is not allowed
            DuplicateFileException: If document with same checksum exists
            StorageException: If storage operation fails
        """
        # Validate file
        sanitized_filename, extension, checksum = FileValidator.validate_file(
            filename, content, mime_type
        )
        
        # Generate storage path using UUID
        file_uuid = str(uuid.uuid4())
        storage_path = f"{file_uuid[:2]}/{file_uuid[2:4]}/{file_uuid}.{extension}"
        
        # Save to storage
        await self.storage.save(storage_path, content)
        
        # Create document record
        document_data = DocumentCreate(
            document_name=document_name or sanitized_filename,
            original_filename=sanitized_filename,
            mime_type=mime_type,
            extension=extension,
            file_size=len(content),
            checksum=checksum,
            storage_path=storage_path,
            description=description,
            tags=tags,
            document_category=category or "UNKNOWN",
            uploaded_by=uploaded_by
        )
        
        document = self.repository.create(document_data)
        return DocumentResponse.model_validate(document)
    
    async def upload_multiple_documents(
        self,
        files: List[Tuple[str, bytes, str]],
        uploaded_by: Optional[str] = None
    ) -> List[DocumentResponse]:
        """Upload multiple documents.
        
        Args:
            files: List of (filename, content, mime_type) tuples
            uploaded_by: User who uploaded the documents
            
        Returns:
            List of created document responses
        """
        documents = []
        for filename, content, mime_type in files:
            document = await self.upload_document(
                filename=filename,
                content=content,
                mime_type=mime_type,
                uploaded_by=uploaded_by
            )
            documents.append(document)
        return documents
    
    def get_document(self, document_id: str) -> DocumentResponse:
        """Get document by ID.
        
        Args:
            document_id: Document UUID
            
        Returns:
            Document response
            
        Raises:
            DocumentNotFoundException: If document not found
        """
        document = self.repository.get_by_id(document_id)
        if not document:
            raise DocumentNotFoundException(f"Document with ID {document_id} not found")
        
        # Update last accessed
        self.repository.update_last_accessed(document_id)
        
        return DocumentResponse.model_validate(document)
    
    def list_documents(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[DocumentSearchFilters] = None,
        sort_by: str = "uploaded_at",
        sort_order: str = "desc"
    ) -> DocumentListResponse:
        """List documents with pagination, filtering, and sorting.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            filters: Search filters
            sort_by: Field to sort by
            sort_order: Sort order (asc or desc)
            
        Returns:
            Document list response
        """
        skip = (page - 1) * page_size
        documents, total = self.repository.get_all(
            skip=skip,
            limit=page_size,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        total_pages = (total + page_size - 1) // page_size
        
        return DocumentListResponse(
            documents=[DocumentResponse.model_validate(doc) for doc in documents],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    
    async def download_document(self, document_id: str) -> Tuple[bytes, str, str]:
        """Download document content.
        
        Args:
            document_id: Document UUID
            
        Returns:
            Tuple of (content, filename, mime_type)
            
        Raises:
            DocumentNotFoundException: If document not found
            StorageException: If storage operation fails
        """
        document = self.repository.get_by_id(document_id)
        if not document:
            raise DocumentNotFoundException(f"Document with ID {document_id} not found")
        
        content = await self.storage.download(document.storage_path)
        
        # Update last accessed
        self.repository.update_last_accessed(document_id)
        
        return content, document.original_filename, document.mime_type
    
    def update_document(
        self,
        document_id: str,
        update_data: DocumentUpdate
    ) -> DocumentResponse:
        """Update document metadata.
        
        Args:
            document_id: Document UUID
            update_data: Update data
            
        Returns:
            Updated document response
            
        Raises:
            DocumentNotFoundException: If document not found
        """
        document = self.repository.update(document_id, update_data)
        return DocumentResponse.model_validate(document)
    
    def delete_document(self, document_id: str) -> str:
        """Soft delete a document.
        
        Args:
            document_id: Document UUID
            
        Returns:
            Success message
            
        Raises:
            DocumentNotFoundException: If document not found
        """
        self.repository.soft_delete(document_id)
        return f"Document {document_id} deleted successfully"
    
    async def delete_document_file(self, document_id: str) -> str:
        """Delete document file from storage and soft delete record.
        
        Args:
            document_id: Document UUID
            
        Returns:
            Success message
            
        Raises:
            DocumentNotFoundException: If document not found
            StorageException: If storage operation fails
        """
        document = self.repository.get_by_id(document_id)
        if not document:
            raise DocumentNotFoundException(f"Document with ID {document_id} not found")
        
        # Delete from storage
        await self.storage.delete(document.storage_path)
        
        # Soft delete record
        self.repository.soft_delete(document_id)
        
        return f"Document {document_id} and its file deleted successfully"
    
    def update_processing_status(
        self,
        document_id: str,
        status: ProcessingStatus,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ) -> DocumentResponse:
        """Update document processing status.
        
        Args:
            document_id: Document UUID
            status: New processing status
            started_at: Processing start time
            completed_at: Processing completion time
            
        Returns:
            Updated document response
            
        Raises:
            DocumentNotFoundException: If document not found
        """
        document = self.repository.update_processing_status(
            document_id, status, started_at, completed_at
        )
        return DocumentResponse.model_validate(document)
    
    def search_documents(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20
    ) -> DocumentListResponse:
        """Search documents by filename.
        
        Args:
            query: Search query
            page: Page number
            page_size: Number of items per page
            
        Returns:
            Document list response
        """
        filters = DocumentSearchFilters(filename=query)
        return self.list_documents(page, page_size, filters)
