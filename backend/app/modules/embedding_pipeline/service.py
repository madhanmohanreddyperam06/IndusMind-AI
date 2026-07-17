"""Service layer for embedding pipeline operations."""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.modules.embedding_pipeline.chunker import DocumentChunker
from app.modules.embedding_pipeline.embedding_generator import get_embedding_generator
from app.modules.embedding_pipeline.qdrant_repository import QdrantRepository
from app.modules.embedding_pipeline.sync import EmbeddingSynchronizationService
from app.modules.embedding_pipeline.search import SemanticSearchEngine
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
from app.modules.embedding_pipeline.enums import ChunkingStrategy, EmbeddingStatus
from app.modules.embedding_pipeline.exceptions import (
    EmbeddingGenerationError,
    ChunkingError,
    VectorStorageError
)
from app.config.qdrant import check_qdrant_health
from app.config.settings import settings
from app.core.logging import setup_logging
import time

logger = setup_logging()


class EmbeddingService:
    """Service for embedding pipeline operations."""
    
    def __init__(self, db: Session):
        """Initialize embedding service.
        
        Args:
            db: MySQL database session
        """
        self.db = db
        self.chunker = None
        self.embedding_generator = get_embedding_generator()
        self.qdrant_repo = QdrantRepository()
        self.sync_service = EmbeddingSynchronizationService(db)
        self.search_engine = SemanticSearchEngine()
    
    # ============================================================================
    # Health Check
    # ============================================================================
    
    def check_health(self) -> HealthCheckResponse:
        """Check embedding pipeline health status.
        
        Returns:
            HealthCheckResponse
        """
        try:
            qdrant_healthy = check_qdrant_health()
            model_loaded = self.embedding_generator._model is not None
            collection_exists = self.qdrant_repo.collection_exists()
            
            # Get model info
            model_info = None
            if model_loaded:
                model_info_dict = self.embedding_generator.get_model_info()
                model_info = EmbeddingModelInfo(**model_info_dict)
            
            # Get collection info
            collection_info = None
            if collection_exists:
                collection_stats = self.qdrant_repo.get_collection_stats()
                collection_info = CollectionResponse(
                    name=settings.qdrant_collection_name,
                    exists=collection_stats["exists"],
                    vector_count=collection_stats.get("vector_count", 0),
                    indexed_vector_count=collection_stats.get("indexed_vector_count", 0),
                    status=collection_stats.get("status"),
                    config=collection_stats.get("config")
                )
            
            overall_healthy = qdrant_healthy and model_loaded and collection_exists
            
            return HealthCheckResponse(
                healthy=overall_healthy,
                qdrant_connected=qdrant_healthy,
                embedding_model_loaded=model_loaded,
                collection_exists=collection_exists,
                embedding_model_info=model_info,
                collection_info=collection_info,
                message="Embedding pipeline is healthy" if overall_healthy else "Embedding pipeline has issues"
            )
            
        except Exception as e:
            logger.error(f"Error checking health: {e}")
            return HealthCheckResponse(
                healthy=False,
                qdrant_connected=False,
                embedding_model_loaded=False,
                collection_exists=False,
                message=f"Health check failed: {str(e)}"
            )
    
    # ============================================================================
    # Chunking
    # ============================================================================
    
    def chunk_document(self, request: ChunkingRequest) -> ChunkingResponse:
        """Chunk a document into semantic chunks.
        
        Args:
            request: Chunking request
            
        Returns:
            ChunkingResponse
        """
        start_time = time.time()
        
        try:
            # Get processed document
            from app.modules.document_processing.repository import ProcessedDocumentRepository
            from app.modules.knowledge_extraction.repository import KnowledgeExtractionRepository
            
            doc_repo = ProcessedDocumentRepository(self.db)
            knowledge_repo = KnowledgeExtractionRepository(self.db)
            
            processed_doc = doc_repo.get_processed_document_by_document_id(request.document_id)
            if not processed_doc:
                raise ChunkingError(f"Processed document not found: {request.document_id}")
            
            entities = knowledge_repo.get_entities_by_document(request.document_id)
            relationships = knowledge_repo.get_relationships_by_document(request.document_id)
            
            # Initialize chunker
            strategy = request.chunking_strategy or ChunkingStrategy(settings.default_chunking_strategy)
            self.chunker = DocumentChunker(
                chunk_size=request.chunk_size,
                chunk_overlap=request.chunk_overlap,
                strategy=strategy
            )
            
            # Chunk document
            chunks = self.chunker.chunk_document(
                processed_document=processed_doc.to_dict(),
                entities=[e.to_dict() for e in entities],
                relationships=[r.to_dict() for r in relationships]
            )
            
            duration = time.time() - start_time
            
            return ChunkingResponse(
                document_id=request.document_id,
                chunks=[chunk.to_dict() for chunk in chunks],
                total_chunks=len(chunks),
                chunking_strategy=strategy,
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Error chunking document: {e}")
            raise ChunkingError(f"Failed to chunk document: {str(e)}", request.document_id)
    
    # ============================================================================
    # Embedding Generation
    # ============================================================================
    
    def generate_embedding(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embedding for text.
        
        Args:
            request: Embedding request
            
        Returns:
            EmbeddingResponse
        """
        start_time = time.time()
        
        try:
            embedding = self.embedding_generator.generate_embeddings_with_cache(
                request.text,
                use_cache=request.use_cache
            )
            
            duration = time.time() - start_time
            
            return EmbeddingResponse(
                embedding=embedding,
                dimension=len(embedding),
                text_length=len(request.text),
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise EmbeddingGenerationError(f"Failed to generate embedding: {str(e)}")
    
    def generate_embeddings_batch(self, request: BatchEmbeddingRequest) -> BatchEmbeddingResponse:
        """Generate embeddings for multiple texts.
        
        Args:
            request: Batch embedding request
            
        Returns:
            BatchEmbeddingResponse
        """
        start_time = time.time()
        
        try:
            embeddings = self.embedding_generator.generate_embeddings_batch(
                texts=request.texts,
                batch_size=request.batch_size,
                show_progress=request.show_progress
            )
            
            duration = time.time() - start_time
            dimension = len(embeddings[0]) if embeddings else 0
            
            return BatchEmbeddingResponse(
                embeddings=embeddings,
                dimension=dimension,
                total_texts=len(request.texts),
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise EmbeddingGenerationError(f"Failed to generate batch embeddings: {str(e)}")
    
    def get_model_info(self) -> EmbeddingModelInfo:
        """Get embedding model information.
        
        Returns:
            EmbeddingModelInfo
        """
        model_info_dict = self.embedding_generator.get_model_info()
        return EmbeddingModelInfo(**model_info_dict)
    
    # ============================================================================
    # Collection Management
    # ============================================================================
    
    def create_collection(self, request: CollectionCreateRequest) -> CollectionResponse:
        """Create or recreate Qdrant collection.
        
        Args:
            request: Collection creation request
            
        Returns:
            CollectionResponse
        """
        try:
            collection_name = request.collection_name or settings.qdrant_collection_name
            
            # Temporarily update repo collection name
            original_collection = self.qdrant_repo.collection_name
            self.qdrant_repo.collection_name = collection_name
            
            self.qdrant_repo.create_collection(recreate=request.recreate)
            
            # Restore original collection name
            self.qdrant_repo.collection_name = original_collection
            
            # Get collection info
            self.qdrant_repo.collection_name = collection_name
            stats = self.qdrant_repo.get_collection_stats()
            self.qdrant_repo.collection_name = original_collection
            
            return CollectionResponse(
                name=collection_name,
                exists=True,
                vector_count=stats.get("vector_count", 0),
                indexed_vector_count=stats.get("indexed_vector_count", 0),
                status=stats.get("status"),
                config=stats.get("config")
            )
            
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise VectorStorageError(f"Failed to create collection: {str(e)}", request.collection_name)
    
    def list_collections(self) -> CollectionListResponse:
        """List all Qdrant collections.
        
        Returns:
            CollectionListResponse
        """
        try:
            from app.config.qdrant import get_qdrant
            client = get_qdrant()
            collections = client.get_collections()
            
            collection_names = [c.name for c in collections.collections]
            
            return CollectionListResponse(
                collections=collection_names,
                total_collections=len(collection_names)
            )
            
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            raise VectorStorageError(f"Failed to list collections: {str(e)}")
    
    def delete_collection(self, collection_name: str = None) -> bool:
        """Delete a Qdrant collection.
        
        Args:
            collection_name: Collection name (uses default if not provided)
            
        Returns:
            True if successful
        """
        try:
            original_collection = self.qdrant_repo.collection_name
            if collection_name:
                self.qdrant_repo.collection_name = collection_name
            
            self.qdrant_repo.delete_collection()
            
            self.qdrant_repo.collection_name = original_collection
            return True
            
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise VectorStorageError(f"Failed to delete collection: {str(e)}", collection_name)
    
    # ============================================================================
    # Synchronization
    # ============================================================================
    
    def index_document(self, request: IndexRequest) -> IndexResponse:
        """Index a document into Qdrant.
        
        Args:
            request: Index request
            
        Returns:
            IndexResponse
        """
        return self.sync_service.index_document(
            document_id=request.document_id,
            chunking_strategy=request.chunking_strategy,
            force_reindex=request.force_reindex,
            background=request.background
        )
    
    def index_all_documents(self, request: BulkIndexRequest) -> BulkIndexResponse:
        """Index all documents into Qdrant.
        
        Args:
            request: Bulk index request
            
        Returns:
            BulkIndexResponse
        """
        return self.sync_service.index_all_documents(
            force_reindex=request.force_reindex,
            background=request.background
        )
    
    def reindex_document(self, request: ReindexRequest) -> ReindexResponse:
        """Re-index a document with new chunking strategy.
        
        Args:
            request: Reindex request
            
        Returns:
            ReindexResponse
        """
        result = self.sync_service.reindex_document(
            document_id=request.document_id,
            chunking_strategy=request.chunking_strategy
        )
        
        return ReindexResponse(
            document_id=request.document_id,
            success=result.success,
            old_vectors_deleted=result.vectors_stored if result.success else 0,
            new_vectors_created=result.vectors_stored if result.success else 0,
            duration_seconds=result.duration_seconds
        )
    
    def delete_document_vectors(self, document_id: str) -> bool:
        """Delete all vectors for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if successful
        """
        return self.sync_service.delete_document_vectors(document_id)
    
    def get_sync_status(self, document_id: str) -> SyncStatusSchema:
        """Get synchronization status for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            SyncStatusSchema
        """
        return self.sync_service.get_sync_status(document_id)
    
    def get_all_sync_status(self) -> Dict[str, SyncStatusSchema]:
        """Get synchronization status for all documents.
        
        Returns:
            Dictionary of sync statuses
        """
        return self.sync_service.get_all_sync_status()
    
    # ============================================================================
    # Search
    # ============================================================================
    
    def search(self, request: SearchRequest) -> SearchResponse:
        """Perform semantic search.
        
        Args:
            request: Search request
            
        Returns:
            SearchResponse
        """
        return self.search_engine.search(request)
    
    def recommend(self, request: RecommendRequest) -> RecommendResponse:
        """Recommend similar chunks.
        
        Args:
            request: Recommendation request
            
        Returns:
            RecommendResponse
        """
        return self.search_engine.recommend(request)
    
    # ============================================================================
    # Statistics
    # ============================================================================
    
    def get_statistics(self) -> EmbeddingStatistics:
        """Get embedding pipeline statistics.
        
        Returns:
            EmbeddingStatistics
        """
        try:
            sync_stats = self.sync_service.get_indexing_statistics()
            collection_stats = self.qdrant_repo.get_collection_stats()
            model_info = self.embedding_generator.get_model_info()
            
            # Calculate average chunks per document
            avg_chunks = 0.0
            if sync_stats.get("indexed_documents", 0) > 0:
                avg_chunks = sync_stats["total_vectors"] / sync_stats["indexed_documents"]
            
            return EmbeddingStatistics(
                documents_indexed=sync_stats.get("indexed_documents", 0),
                total_chunks=sync_stats.get("total_vectors", 0),
                total_vectors=sync_stats.get("total_vectors", 0),
                average_chunks_per_document=avg_chunks,
                embedding_model=model_info["model_name"],
                embedding_dimension=model_info["dimension"],
                collection_size_mb=None,  # Would need to calculate from Qdrant
                average_search_latency_ms=None,  # Would need to track
                total_indexing_time_seconds=0.0  # Would need to track
            )
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            raise VectorStorageError(f"Failed to get statistics: {str(e)}")
    
    # ============================================================================
    # Utility
    # ============================================================================
    
    def clear_all_vectors(self) -> bool:
        """Clear all vectors from the collection.
        
        Returns:
            True if successful
        """
        return self.sync_service.clear_all_vectors()
    
    def clear_embedding_cache(self) -> bool:
        """Clear the embedding cache.
        
        Returns:
            True if successful
        """
        self.embedding_generator.clear_cache()
        return True
