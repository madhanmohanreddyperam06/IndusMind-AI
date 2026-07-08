"""Document repository for database operations."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.modules.document.models import Document
from app.modules.document.schemas import DocumentCreate, DocumentUpdate, DocumentSearchFilters
from app.modules.document.enums import ProcessingStatus
from app.modules.document.exceptions import DocumentNotFoundException, DuplicateFileException


class DocumentRepository:
    """Repository for document database operations."""
    
    def __init__(self, db: Session):
        """Initialize document repository.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create(self, document_data: DocumentCreate) -> Document:
        """Create a new document.
        
        Args:
            document_data: Document creation data
            
        Returns:
            Created document
            
        Raises:
            DuplicateFileException: If document with same checksum exists
        """
        # Check for duplicate checksum
        existing = self.get_by_checksum(document_data.checksum)
        if existing and not existing.is_deleted:
            raise DuplicateFileException(
                f"Document with checksum {document_data.checksum} already exists"
            )
        
        db_document = Document(**document_data.model_dump())
        self.db.add(db_document)
        self.db.commit()
        self.db.refresh(db_document)
        return db_document
    
    def get_by_id(self, document_id: str) -> Optional[Document]:
        """Get document by ID.
        
        Args:
            document_id: Document UUID
            
        Returns:
            Document if found, None otherwise
        """
        return self.db.query(Document).filter(
            and_(Document.id == document_id, Document.is_deleted == False)
        ).first()
    
    def get_by_checksum(self, checksum: str) -> Optional[Document]:
        """Get document by checksum.
        
        Args:
            checksum: File checksum
            
        Returns:
            Document if found, None otherwise
        """
        return self.db.query(Document).filter(
            Document.checksum == checksum
        ).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[DocumentSearchFilters] = None,
        sort_by: str = "uploaded_at",
        sort_order: str = "desc"
    ) -> tuple[List[Document], int]:
        """Get all documents with pagination, filtering, and sorting.
        
        Args:
            skip: Number of records to skip
            limit: Number of records to return
            filters: Search filters
            sort_by: Field to sort by
            sort_order: Sort order (asc or desc)
            
        Returns:
            Tuple of (documents list, total count)
        """
        query = self.db.query(Document).filter(Document.is_deleted == False)
        
        # Apply filters
        if filters:
            if filters.filename:
                query = query.filter(Document.document_name.ilike(f"%{filters.filename}%"))
            if filters.category:
                query = query.filter(Document.document_category == filters.category)
            if filters.status:
                query = query.filter(Document.processing_status == filters.status)
            if filters.uploaded_by:
                query = query.filter(Document.uploaded_by == filters.uploaded_by)
            if filters.date_from:
                query = query.filter(Document.uploaded_at >= filters.date_from)
            if filters.date_to:
                query = query.filter(Document.uploaded_at <= filters.date_to)
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(Document, sort_by, Document.uploaded_at)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        documents = query.offset(skip).limit(limit).all()
        
        return documents, total
    
    def update(self, document_id: str, update_data: DocumentUpdate) -> Document:
        """Update document metadata.
        
        Args:
            document_id: Document UUID
            update_data: Update data
            
        Returns:
            Updated document
            
        Raises:
            DocumentNotFoundException: If document not found
        """
        document = self.get_by_id(document_id)
        if not document:
            raise DocumentNotFoundException(f"Document with ID {document_id} not found")
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(document, field, value)
        
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def soft_delete(self, document_id: str) -> Document:
        """Soft delete a document.
        
        Args:
            document_id: Document UUID
            
        Returns:
            Deleted document
            
        Raises:
            DocumentNotFoundException: If document not found
        """
        document = self.get_by_id(document_id)
        if not document:
            raise DocumentNotFoundException(f"Document with ID {document_id} not found")
        
        document.is_deleted = True
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def update_last_accessed(self, document_id: str) -> None:
        """Update last accessed timestamp.
        
        Args:
            document_id: Document UUID
        """
        document = self.get_by_id(document_id)
        if document:
            document.last_accessed = datetime.utcnow()
            self.db.commit()
    
    def update_processing_status(
        self,
        document_id: str,
        status: ProcessingStatus,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ) -> Document:
        """Update document processing status.
        
        Args:
            document_id: Document UUID
            status: New processing status
            started_at: Processing start time
            completed_at: Processing completion time
            
        Returns:
            Updated document
            
        Raises:
            DocumentNotFoundException: If document not found
        """
        document = self.get_by_id(document_id)
        if not document:
            raise DocumentNotFoundException(f"Document with ID {document_id} not found")
        
        document.processing_status = status
        if started_at:
            document.processing_started_at = started_at
        if completed_at:
            document.processing_completed_at = completed_at
        
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def get_by_category(self, category: str, skip: int = 0, limit: int = 20) -> List[Document]:
        """Get documents by category.
        
        Args:
            category: Document category
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of documents
        """
        return self.db.query(Document).filter(
            and_(
                Document.document_category == category,
                Document.is_deleted == False
            )
        ).offset(skip).limit(limit).all()
    
    def get_by_status(self, status: ProcessingStatus, skip: int = 0, limit: int = 20) -> List[Document]:
        """Get documents by processing status.
        
        Args:
            status: Processing status
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of documents
        """
        return self.db.query(Document).filter(
            and_(
                Document.processing_status == status,
                Document.is_deleted == False
            )
        ).offset(skip).limit(limit).all()
