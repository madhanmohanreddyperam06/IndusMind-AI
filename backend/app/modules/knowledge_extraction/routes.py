"""REST API routes for knowledge extraction."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.api.dependencies import get_current_active_user
from app.modules.knowledge_extraction.service import KnowledgeExtractionService
from app.models.user import User
from app.modules.knowledge_extraction.schemas import (
    ExtractEntitiesRequest,
    ExtractRelationshipsRequest,
    ProcessKnowledgeExtractionRequest,
    EntityExtractionResult,
    RelationshipExtractionResult,
    KnowledgeExtractionStatistics,
    ExtractionStatusResponse
)
from app.modules.knowledge_extraction.exceptions import (
    DocumentNotFoundException,
    ProcessedDocumentNotFoundException,
    KnowledgeExtractionException
)
from app.core.logging import setup_logging

logger = setup_logging()

router = APIRouter()


@router.post("/entities/{document_id}", response_model=EntityExtractionResult)
async def extract_entities(
    document_id: str,
    request: ExtractEntitiesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Extract entities from a document.
    
    Args:
        document_id: Document ID
        request: Extraction request
        db: Database session
        
    Returns:
        Entity extraction result
    """
    try:
        service = KnowledgeExtractionService(db)
        result = service.extract_entities(
            document_id=document_id,
            force_reextract=request.force_reextract,
            extractors=request.extractors
        )
        return result
    except DocumentNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProcessedDocumentNotFoundException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KnowledgeExtractionException as e:
        logger.error(f"Entity extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/relationships/{document_id}", response_model=RelationshipExtractionResult)
async def extract_relationships(
    document_id: str,
    request: ExtractRelationshipsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Extract relationships from a document.
    
    Args:
        document_id: Document ID
        request: Extraction request
        db: Database session
        
    Returns:
        Relationship extraction result
    """
    try:
        service = KnowledgeExtractionService(db)
        result = service.extract_relationships(
            document_id=document_id,
            force_reextract=request.force_reextract,
            relationship_types=request.relationship_types
        )
        return result
    except DocumentNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProcessedDocumentNotFoundException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KnowledgeExtractionException as e:
        logger.error(f"Relationship extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process/{document_id}")
async def process_document(
    document_id: str,
    request: ProcessKnowledgeExtractionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Run full knowledge extraction pipeline.
    
    Args:
        document_id: Document ID
        request: Processing request
        db: Database session
        
    Returns:
        Processing result
    """
    try:
        service = KnowledgeExtractionService(db)
        result = service.process_document(
            document_id=document_id,
            force_reextract=request.force_reextract
        )
        return result
    except DocumentNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProcessedDocumentNotFoundException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KnowledgeExtractionException as e:
        logger.error(f"Knowledge extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities/{document_id}")
async def get_entities(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all entities for a document.
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        List of entities
    """
    try:
        service = KnowledgeExtractionService(db)
        entities = service.get_entities(document_id)
        return {
            "document_id": document_id,
            "entities": entities,
            "total_count": len(entities)
        }
    except DocumentNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/relationships/{document_id}")
async def get_relationships(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all relationships for a document.
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        List of relationships
    """
    try:
        service = KnowledgeExtractionService(db)
        relationships = service.get_relationships(document_id)
        return {
            "document_id": document_id,
            "relationships": relationships,
            "total_count": len(relationships)
        }
    except DocumentNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting relationships: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/{document_id}", response_model=KnowledgeExtractionStatistics)
async def get_statistics(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get extraction statistics for a document.
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        Extraction statistics
    """
    try:
        service = KnowledgeExtractionService(db)
        stats = service.get_statistics(document_id)
        return stats
    except DocumentNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{document_id}", response_model=ExtractionStatusResponse)
async def get_extraction_status(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get extraction status for a document.
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        Extraction status
    """
    try:
        service = KnowledgeExtractionService(db)
        status = service.get_extraction_status(document_id)
        return status
    except DocumentNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting extraction status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}")
async def delete_extraction(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete all extraction data for a document.
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        Deletion result
    """
    try:
        service = KnowledgeExtractionService(db)
        service.delete_extraction(document_id)
        return {
            "message": "Extraction data deleted successfully",
            "document_id": document_id
        }
    except DocumentNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting extraction: {e}")
        raise HTTPException(status_code=500, detail=str(e))
