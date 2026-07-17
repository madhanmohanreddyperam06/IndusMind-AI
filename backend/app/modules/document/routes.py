"""Document API routes."""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from app.config.database import get_db
from app.modules.document.service import DocumentService
from app.modules.document.schemas import (
    DocumentResponse,
    DocumentListResponse,
    DocumentUpdate,
    DocumentSearchFilters,
    UploadResponse,
    DocumentDeleteResponse
)
from app.modules.document.enums import ProcessingStatus
from app.modules.document.exceptions import (
    DocumentException,
    FileValidationException,
    DuplicateFileException,
    DocumentNotFoundException,
    StorageException
)
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()


def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    """Dependency to get document service."""
    return DocumentService(db)


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    document_name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[str] = None,
    category: Optional[str] = None,
    service: DocumentService = Depends(get_document_service)
):
    """Upload a single document.
    
    Args:
        file: Uploaded file
        document_name: Display name for document
        description: Document description
        tags: Comma-separated tags
        category: Document category
        service: Document service
        
    Returns:
        Upload response with document metadata
    """
    try:
        content = await file.read()
        
        # Parse tags
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
        
        document = await service.upload_document(
            filename=file.filename or "unknown",
            content=content,
            mime_type=file.content_type or "application/octet-stream",
            document_name=document_name,
            description=description,
            tags=tag_list,
            category=category
        )
        
        logger.info(f"Document uploaded successfully: {document.id}")
        return UploadResponse(document=document, message="Document uploaded successfully")
        
    except DuplicateFileException as e:
        logger.warning(f"Duplicate file upload attempt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except FileValidationException as e:
        logger.warning(f"File validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except StorageException as e:
        logger.error(f"Storage error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )


@router.post("/upload/multiple", response_model=List[UploadResponse])
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    service: DocumentService = Depends(get_document_service)
):
    """Upload multiple documents.
    
    Args:
        files: List of uploaded files
        service: Document service
        
    Returns:
        List of upload responses
    """
    try:
        file_data = []
        for file in files:
            content = await file.read()
            file_data.append((file.filename or "unknown", content, file.content_type or "application/octet-stream"))
        
        documents = await service.upload_multiple_documents(file_data)
        
        logger.info(f"Multiple documents uploaded: {len(documents)} files")
        return [UploadResponse(document=doc, message="Document uploaded successfully") for doc in documents]
        
    except FileValidationException as e:
        logger.warning(f"File validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except StorageException as e:
        logger.error(f"Storage error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload documents"
        )


@router.get("", response_model=DocumentListResponse)
def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    filename: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[ProcessingStatus] = Query(None),
    uploaded_by: Optional[str] = Query(None),
    sort_by: str = Query("uploaded_at"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    service: DocumentService = Depends(get_document_service)
):
    """List documents with pagination, filtering, and sorting.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        filename: Filter by filename
        category: Filter by category
        status: Filter by processing status
        uploaded_by: Filter by uploader
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        service: Document service
        
    Returns:
        Document list response
    """
    try:
        filters = DocumentSearchFilters(
            filename=filename,
            category=category,
            status=status,
            uploaded_by=uploaded_by
        )
        return service.list_documents(page, page_size, filters, sort_by, sort_order)
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list documents"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service)
):
    """Get document by ID.
    
    Args:
        document_id: Document UUID
        service: Document service
        
    Returns:
        Document response
    """
    try:
        return service.get_document(document_id)
    except DocumentNotFoundException as e:
        logger.warning(f"Document not found: {document_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get document"
        )


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service)
):
    """Download document file.
    
    Args:
        document_id: Document UUID
        service: Document service
        
    Returns:
        File response
    """
    try:
        content, filename, mime_type = await service.download_document(document_id)
        
        from app.modules.document.storage import LocalStorageProvider
        from app.modules.document.constants import DOCUMENTS_STORAGE_DIR
        storage = LocalStorageProvider(DOCUMENTS_STORAGE_DIR)
        document = service.repository.get_by_id(document_id)
        
        file_path = storage.get_path(document.storage_path)
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type=mime_type
        )
    except DocumentNotFoundException as e:
        logger.warning(f"Document not found for download: {document_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except StorageException as e:
        logger.error(f"Storage error during download: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error downloading document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download document"
        )


@router.patch("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: str,
    update_data: DocumentUpdate,
    service: DocumentService = Depends(get_document_service)
):
    """Update document metadata.
    
    Args:
        document_id: Document UUID
        update_data: Update data
        service: Document service
        
    Returns:
        Updated document response
    """
    try:
        return service.update_document(document_id, update_data)
    except DocumentNotFoundException as e:
        logger.warning(f"Document not found for update: {document_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update document"
        )


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
def delete_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service)
):
    """Soft delete a document.
    
    Args:
        document_id: Document UUID
        service: Document service
        
    Returns:
        Delete response
    """
    try:
        message = service.delete_document(document_id)
        logger.info(f"Document deleted: {document_id}")
        return DocumentDeleteResponse(message=message, document_id=document_id)
    except DocumentNotFoundException as e:
        logger.warning(f"Document not found for deletion: {document_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )


@router.get("/search/query")
def search_documents(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: DocumentService = Depends(get_document_service)
):
    """Search documents by filename.
    
    Args:
        query: Search query
        page: Page number
        page_size: Number of items per page
        service: Document service
        
    Returns:
        Document list response
    """
    try:
        return service.search_documents(query, page, page_size)
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search documents"
        )
