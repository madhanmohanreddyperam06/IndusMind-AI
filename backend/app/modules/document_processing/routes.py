"""REST API routes for document processing."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.modules.document_processing.service import DocumentProcessingService
from app.modules.document_processing.schemas import (
    ProcessDocumentRequest,
    ProcessAllRequest,
    ProcessingStatusResponse,
    DocumentStatisticsResponse,
    ProcessedDocumentResponse
)
from app.modules.document_processing.exceptions import DocumentProcessingException
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()


def get_document_processing_service(db: Session = Depends(get_db)) -> DocumentProcessingService:
    """Dependency to get document processing service."""
    return DocumentProcessingService(db)


@router.post("/process/{document_id}", response_model=ProcessingStatusResponse)
async def process_document(
    document_id: str,
    request: ProcessDocumentRequest,
    service: DocumentProcessingService = Depends(get_document_processing_service)
):
    """Process a document.
    
    Args:
        document_id: Document ID
        request: Process request with force_reprocess flag
        service: Document processing service
        
    Returns:
        Processing status response
    """
    try:
        return await service.process_document(document_id, request.force_reprocess)
    except DocumentProcessingException as e:
        logger.error(f"Processing failed for document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error processing document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process document"
        )


@router.post("/process-all")
async def process_all(
    request: ProcessAllRequest,
    service: DocumentProcessingService = Depends(get_document_processing_service)
):
    """Process all uploaded documents.
    
    Args:
        request: Process request with force_reprocess flag
        service: Document processing service
        
    Returns:
        Processing results
    """
    try:
        return await service.process_all(request.force_reprocess)
    except Exception as e:
        logger.error(f"Unexpected error processing all documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process documents"
        )


@router.get("/status/{document_id}", response_model=ProcessingStatusResponse)
def get_processing_status(
    document_id: str,
    service: DocumentProcessingService = Depends(get_document_processing_service)
):
    """Get processing status for a document.
    
    Args:
        document_id: Document ID
        service: Document processing service
        
    Returns:
        Processing status response
    """
    try:
        return service.get_processing_status(document_id)
    except Exception as e:
        logger.error(f"Error getting processing status for {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get processing status"
        )


@router.get("/result/{document_id}", response_model=ProcessedDocumentResponse)
def get_processed_document(
    document_id: str,
    service: DocumentProcessingService = Depends(get_document_processing_service)
):
    """Get processed document result.
    
    Args:
        document_id: Document ID
        service: Document processing service
        
    Returns:
        Processed document response
    """
    try:
        result = service.get_processed_document(document_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Processed document not found for {document_id}"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting processed document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get processed document"
        )


@router.get("/statistics/{document_id}", response_model=DocumentStatisticsResponse)
def get_document_statistics(
    document_id: str,
    service: DocumentProcessingService = Depends(get_document_processing_service)
):
    """Get document statistics.
    
    Args:
        document_id: Document ID
        service: Document processing service
        
    Returns:
        Document statistics response
    """
    try:
        result = service.get_document_statistics(document_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Statistics not found for {document_id}"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting statistics for {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get document statistics"
        )
