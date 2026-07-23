"""REST API routes for embedding pipeline operations."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.api.dependencies import get_current_active_user
from app.modules.embedding_pipeline.service import EmbeddingService
from app.models.user import User
from app.modules.embedding_pipeline.schemas import (
    ChunkingRequest,
    ChunkingResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    BatchEmbeddingRequest,
    BatchEmbeddingResponse,
    IndexRequest,
    IndexResponse,
    BulkIndexRequest,
    BulkIndexResponse,
    ReindexRequest,
    ReindexResponse,
    SearchRequest,
    SearchResponse,
    RecommendRequest,
    RecommendResponse,
    EmbeddingStatistics,
    HealthCheckResponse,
    CollectionCreateRequest,
    CollectionResponse,
    CollectionListResponse,
    SyncStatusSchema,
    EmbeddingModelInfo
)
from app.modules.embedding_pipeline.exceptions import (
    EmbeddingGenerationError,
    ChunkingError,
    VectorStorageError,
    SearchError,
    SynchronizationError
)
from app.core.logging import setup_logging

logger = setup_logging()

router = APIRouter()


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health", response_model=HealthCheckResponse)
async def get_health(db: Session = Depends(get_db)):
    """Get embedding pipeline health status."""
    try:
        service = EmbeddingService(db)
        return service.check_health()
    except Exception as e:
        logger.error(f"Error checking health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Chunking
# ============================================================================

@router.post("/chunk", response_model=ChunkingResponse)
async def chunk_document(request: ChunkingRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Chunk a document into semantic chunks."""
    try:
        service = EmbeddingService(db)
        return service.chunk_document(request)
    except ChunkingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error chunking document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Embedding Generation
# ============================================================================

@router.post("/generate", response_model=EmbeddingResponse)
async def generate_embedding(request: EmbeddingRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Generate embedding for text."""
    try:
        service = EmbeddingService(db)
        return service.generate_embedding(request)
    except EmbeddingGenerationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/batch", response_model=BatchEmbeddingResponse)
async def generate_embeddings_batch(request: BatchEmbeddingRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Generate embeddings for multiple texts."""
    try:
        service = EmbeddingService(db)
        return service.generate_embeddings_batch(request)
    except EmbeddingGenerationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating batch embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model/info", response_model=EmbeddingModelInfo)
async def get_model_info(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get embedding model information."""
    try:
        service = EmbeddingService(db)
        return service.get_model_info()
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Collection Management
# ============================================================================

@router.post("/collections", response_model=CollectionResponse)
async def create_collection(request: CollectionCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Create or recreate Qdrant collection."""
    try:
        service = EmbeddingService(db)
        return service.create_collection(request)
    except VectorStorageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections", response_model=CollectionListResponse)
async def list_collections(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """List all Qdrant collections."""
    try:
        service = EmbeddingService(db)
        return service.list_collections()
    except VectorStorageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing collections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Delete a Qdrant collection."""
    try:
        service = EmbeddingService(db)
        service.delete_collection(collection_name)
        return {"message": f"Collection {collection_name} deleted successfully"}
    except VectorStorageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Synchronization / Indexing
# ============================================================================

@router.post("/index/document/{document_id}", response_model=IndexResponse)
async def index_document(document_id: str, force_reindex: bool = False, background: bool = False, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Index a document into Qdrant."""
    try:
        service = EmbeddingService(db)
        request = IndexRequest(document_id=document_id, force_reindex=force_reindex, background=background)
        return service.index_document(request)
    except SynchronizationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error indexing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/all", response_model=BulkIndexResponse)
async def index_all_documents(force_reindex: bool = False, background: bool = False, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Index all documents into Qdrant."""
    try:
        service = EmbeddingService(db)
        request = BulkIndexRequest(force_reindex=force_reindex, background=background)
        return service.index_all_documents(request)
    except SynchronizationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error indexing all documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reindex/{document_id}", response_model=ReindexResponse)
async def reindex_document(document_id: str, request: ReindexRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Re-index a document with new chunking strategy."""
    try:
        service = EmbeddingService(db)
        request.document_id = document_id
        return service.reindex_document(request)
    except SynchronizationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error reindexing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/document/{document_id}")
async def delete_document_vectors(document_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Delete all vectors for a document."""
    try:
        service = EmbeddingService(db)
        service.delete_document_vectors(document_id)
        return {"message": f"Vectors for document {document_id} deleted successfully"}
    except SynchronizationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting document vectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync/status/{document_id}", response_model=SyncStatusSchema)
async def get_sync_status(document_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get synchronization status for a document."""
    try:
        service = EmbeddingService(db)
        return service.get_sync_status(document_id)
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync/status/all")
async def get_all_sync_status(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get synchronization status for all documents."""
    try:
        service = EmbeddingService(db)
        return service.get_all_sync_status()
    except Exception as e:
        logger.error(f"Error getting all sync status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Search
# ============================================================================

@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Perform semantic search."""
    try:
        service = EmbeddingService(db)
        return service.search(request)
    except SearchError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error performing search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Recommend similar chunks."""
    try:
        service = EmbeddingService(db)
        return service.recommend(request)
    except SearchError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error performing recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Statistics
# ============================================================================

@router.get("/statistics", response_model=EmbeddingStatistics)
async def get_statistics(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get embedding pipeline statistics."""
    try:
        service = EmbeddingService(db)
        return service.get_statistics()
    except VectorStorageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Utility
# ============================================================================

@router.delete("/clear")
async def clear_all_vectors(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Clear all vectors from the collection."""
    try:
        service = EmbeddingService(db)
        service.clear_all_vectors()
        return {"message": "All vectors cleared successfully"}
    except VectorStorageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error clearing vectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear")
async def clear_embedding_cache(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Clear the embedding cache."""
    try:
        service = EmbeddingService(db)
        service.clear_embedding_cache()
        return {"message": "Embedding cache cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))
