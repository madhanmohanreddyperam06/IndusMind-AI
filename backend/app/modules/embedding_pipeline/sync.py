"""Embedding synchronization service for document indexing."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.modules.embedding_pipeline.chunker import DocumentChunker
from app.modules.embedding_pipeline.embedding_generator import get_embedding_generator
from app.modules.embedding_pipeline.qdrant_repository import QdrantRepository
from app.modules.embedding_pipeline.schemas import (
    IndexResponse,
    BulkIndexResponse,
    SyncStatusSchema,
    VectorPayload
)
from app.modules.embedding_pipeline.enums import EmbeddingStatus, SyncStatus, ChunkingStrategy
from app.modules.embedding_pipeline.exceptions import SynchronizationError
from app.modules.document_processing.repository import ProcessedDocumentRepository
from app.modules.knowledge_extraction.repository import KnowledgeExtractionRepository
from app.config.settings import settings
from app.core.logging import setup_logging
import time

logger = setup_logging()


class EmbeddingSynchronizationService:
    """Service for synchronizing documents to Qdrant vector store."""
    
    def __init__(self, db: Session):
        """Initialize synchronization service.
        
        Args:
            db: MySQL database session
        """
        self.db = db
        self.chunker = None
        self.embedding_generator = get_embedding_generator()
        self.qdrant_repo = QdrantRepository()
        self.doc_processing_repo = DocumentProcessingRepository(db)
        self.knowledge_repo = KnowledgeExtractionRepository(db)
        
        # In-memory sync status tracking
        self._sync_status: Dict[str, Dict[str, Any]] = {}
    
    def index_document(
        self,
        document_id: str,
        chunking_strategy: ChunkingStrategy = None,
        force_reindex: bool = False,
        background: bool = False
    ) -> IndexResponse:
        """Index a single document into Qdrant.
        
        Args:
            document_id: Document ID to index
            chunking_strategy: Chunking strategy to use
            force_reindex: Force re-indexing even if already indexed
            background: Process in background
            
        Returns:
            IndexResponse
        """
        start_time = time.time()
        
        try:
            # Initialize sync status
            self._sync_status[document_id] = {
                "status": SyncStatus.IN_PROGRESS,
                "chunks_indexed": 0,
                "embeddings_generated": 0,
                "vectors_stored": 0,
                "error_message": None,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Check if already indexed
            if not force_reindex:
                existing_count = self.qdrant_repo.count_points(
                    filter={"must": [{"key": "document_id", "match": {"value": document_id}}]}
                )
                if existing_count > 0:
                    logger.info(f"Document {document_id} already indexed with {existing_count} vectors")
                    return IndexResponse(
                        document_id=document_id,
                        success=True,
                        chunks_created=0,
                        embeddings_generated=0,
                        vectors_stored=existing_count,
                        duration_seconds=time.time() - start_time,
                        status=EmbeddingStatus.COMPLETED
                    )
            
            # Get processed document
            processed_doc = self.doc_processing_repo.get_processed_document_by_document_id(document_id)
            if not processed_doc:
                raise SynchronizationError(f"Processed document not found for document_id: {document_id}", document_id)
            
            # Get extracted entities and relationships
            entities = self.knowledge_repo.get_entities_by_document(document_id)
            relationships = self.knowledge_repo.get_relationships_by_document(document_id)
            
            # Initialize chunker with specified strategy
            strategy = chunking_strategy or ChunkingStrategy(settings.default_chunking_strategy)
            self.chunker = DocumentChunker(strategy=strategy)
            
            # Chunk document
            chunks = self.chunker.chunk_document(
                processed_document=processed_doc.to_dict(),
                entities=[e.to_dict() for e in entities],
                relationships=[r.to_dict() for r in relationships]
            )
            
            self._sync_status[document_id]["chunks_indexed"] = len(chunks)
            
            # Generate embeddings
            chunk_texts = [chunk.chunk_text for chunk in chunks]
            embeddings = self.embedding_generator.generate_embeddings_batch(
                texts=chunk_texts,
                batch_size=settings.embedding_batch_size,
                show_progress=False
            )
            
            self._sync_status[document_id]["embeddings_generated"] = len(embeddings)
            
            # Prepare vectors and payloads
            vectors = embeddings
            payloads = []
            vector_ids = []
            
            for chunk in chunks:
                payload = VectorPayload(
                    document_id=chunk.document_id,
                    chunk_id=chunk.chunk_id,
                    processed_document_id=chunk.processed_document_id,
                    page_number=chunk.page_number,
                    section_title=chunk.section_title,
                    paragraph_numbers=chunk.paragraph_numbers,
                    document_type=chunk.document_type,
                    equipment_entities=chunk.equipment_entities,
                    component_entities=chunk.component_entities,
                    relationship_ids=chunk.relationship_ids,
                    entity_ids=chunk.entity_ids,
                    confidence=None,
                    token_count=chunk.token_count,
                    character_count=chunk.character_count,
                    created_at=datetime.utcnow().isoformat(),
                    updated_at=None
                )
                payloads.append(payload.model_dump())
                vector_ids.append(chunk.chunk_id)
            
            # Delete existing vectors if reindexing
            if force_reindex:
                self.qdrant_repo.delete_document_vectors(document_id)
            
            # Store vectors in Qdrant
            self.qdrant_repo.upsert_vectors(
                vectors=vectors,
                payloads=payloads,
                ids=vector_ids
            )
            
            self._sync_status[document_id]["vectors_stored"] = len(vectors)
            self._sync_status[document_id]["status"] = SyncStatus.COMPLETED
            self._sync_status[document_id]["last_updated"] = datetime.utcnow().isoformat()
            
            duration = time.time() - start_time
            logger.info(f"Successfully indexed document {document_id} with {len(chunks)} chunks in {duration:.2f}s")
            
            return IndexResponse(
                document_id=document_id,
                success=True,
                chunks_created=len(chunks),
                embeddings_generated=len(embeddings),
                vectors_stored=len(vectors),
                duration_seconds=duration,
                status=EmbeddingStatus.COMPLETED
            )
            
        except Exception as e:
            logger.error(f"Error indexing document {document_id}: {e}")
            self._sync_status[document_id]["status"] = SyncStatus.FAILED
            self._sync_status[document_id]["error_message"] = str(e)
            self._sync_status[document_id]["last_updated"] = datetime.utcnow().isoformat()
            
            return IndexResponse(
                document_id=document_id,
                success=False,
                chunks_created=0,
                embeddings_generated=0,
                vectors_stored=0,
                duration_seconds=time.time() - start_time,
                status=EmbeddingStatus.FAILED,
                error_message=str(e)
            )
    
    def index_all_documents(
        self,
        force_reindex: bool = False,
        background: bool = False
    ) -> BulkIndexResponse:
        """Index all documents into Qdrant.
        
        Args:
            force_reindex: Force re-indexing all documents
            background: Process in background
            
        Returns:
            BulkIndexResponse
        """
        start_time = time.time()
        
        try:
            # Get all processed documents
            processed_docs = self.doc_processing_repo.get_all_processed_documents()
            
            total_chunks = 0
            total_embeddings = 0
            total_vectors = 0
            failed_documents = []
            
            for processed_doc in processed_docs:
                document_id = processed_doc.document_id
                
                try:
                    result = self.index_document(
                        document_id=document_id,
                        force_reindex=force_reindex,
                        background=False
                    )
                    
                    if result.success:
                        total_chunks += result.chunks_created
                        total_embeddings += result.embeddings_generated
                        total_vectors += result.vectors_stored
                    else:
                        failed_documents.append(document_id)
                        
                except Exception as e:
                    logger.error(f"Failed to index document {document_id}: {e}")
                    failed_documents.append(document_id)
            
            duration = time.time() - start_time
            logger.info(f"Bulk indexing completed: {len(processed_docs)} documents, {failed_documents} failed")
            
            return BulkIndexResponse(
                success=len(failed_documents) == 0,
                documents_processed=len(processed_docs),
                total_chunks=total_chunks,
                total_embeddings=total_embeddings,
                total_vectors=total_vectors,
                duration_seconds=duration,
                failed_documents=failed_documents
            )
            
        except Exception as e:
            logger.error(f"Error in bulk indexing: {e}")
            raise SynchronizationError(f"Bulk indexing failed: {str(e)}")
    
    def delete_document_vectors(self, document_id: str) -> bool:
        """Delete all vectors for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if successful
        """
        try:
            self.qdrant_repo.delete_document_vectors(document_id)
            
            # Update sync status
            if document_id in self._sync_status:
                del self._sync_status[document_id]
            
            logger.info(f"Deleted vectors for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors for document {document_id}: {e}")
            raise SynchronizationError(f"Failed to delete vectors: {str(e)}", document_id)
    
    def reindex_document(
        self,
        document_id: str,
        chunking_strategy: ChunkingStrategy = None
    ) -> IndexResponse:
        """Re-index a document with new chunking strategy.
        
        Args:
            document_id: Document ID to reindex
            chunking_strategy: New chunking strategy
            
        Returns:
            IndexResponse
        """
        return self.index_document(
            document_id=document_id,
            chunking_strategy=chunking_strategy,
            force_reindex=True
        )
    
    def get_sync_status(self, document_id: str) -> SyncStatusSchema:
        """Get synchronization status for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            SyncStatusSchema
        """
        if document_id in self._sync_status:
            status_data = self._sync_status[document_id]
            return SyncStatusSchema(
                document_id=document_id,
                status=status_data["status"],
                chunks_indexed=status_data["chunks_indexed"],
                embeddings_generated=status_data["embeddings_generated"],
                vectors_stored=status_data["vectors_stored"],
                error_message=status_data["error_message"],
                last_updated=status_data["last_updated"]
            )
        
        # Check if document is indexed in Qdrant
        vector_count = self.qdrant_repo.count_points(
            filter={"must": [{"key": "document_id", "match": {"value": document_id}}]}
        )
        
        if vector_count > 0:
            return SyncStatusSchema(
                document_id=document_id,
                status=SyncStatus.COMPLETED,
                chunks_indexed=vector_count,
                embeddings_generated=vector_count,
                vectors_stored=vector_count,
                error_message=None,
                last_updated=datetime.utcnow().isoformat()
            )
        
        return SyncStatusSchema(
            document_id=document_id,
            status=SyncStatus.PENDING,
            chunks_indexed=0,
            embeddings_generated=0,
            vectors_stored=0,
            error_message=None,
            last_updated=datetime.utcnow().isoformat()
        )
    
    def get_all_sync_status(self) -> Dict[str, SyncStatusSchema]:
        """Get synchronization status for all documents.
        
        Returns:
            Dictionary of document IDs to sync status
        """
        # Get all processed documents
        processed_docs = self.doc_processing_repo.get_all_processed_documents()
        
        status_dict = {}
        for doc in processed_docs:
            status_dict[doc.document_id] = self.get_sync_status(doc.document_id)
        
        return status_dict
    
    def retry_failed_indexing(self, document_id: str, max_retries: int = 3) -> IndexResponse:
        """Retry failed indexing for a document.
        
        Args:
            document_id: Document ID
            max_retries: Maximum number of retry attempts
            
        Returns:
            IndexResponse
        """
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                result = self.index_document(
                    document_id=document_id,
                    force_reindex=True
                )
                
                if result.success:
                    logger.info(f"Successfully indexed document {document_id} after {retry_count + 1} retries")
                    return result
                
                last_error = result.error_message
                retry_count += 1
                
            except Exception as e:
                last_error = str(e)
                retry_count += 1
        
        logger.error(f"Failed to index document {document_id} after {max_retries} retries")
        
        return IndexResponse(
            document_id=document_id,
            success=False,
            chunks_created=0,
            embeddings_generated=0,
            vectors_stored=0,
            duration_seconds=0,
            status=EmbeddingStatus.FAILED,
            error_message=f"Failed after {max_retries} retry attempts. Last error: {last_error}"
        )
    
    def clear_all_vectors(self) -> bool:
        """Clear all vectors from the collection.
        
        Returns:
            True if successful
        """
        try:
            self.qdrant_repo.delete_collection()
            self.qdrant_repo.create_collection()
            
            # Clear sync status
            self._sync_status.clear()
            
            logger.info("Cleared all vectors from collection")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing vectors: {e}")
            raise SynchronizationError(f"Failed to clear vectors: {str(e)}")
    
    def get_indexing_statistics(self) -> Dict[str, Any]:
        """Get indexing statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            collection_stats = self.qdrant_repo.get_collection_stats()
            
            # Get document-level statistics
            processed_docs = self.doc_processing_repo.get_all_processed_documents()
            total_documents = len(processed_docs)
            
            indexed_documents = 0
            for doc in processed_docs:
                vector_count = self.qdrant_repo.count_points(
                    filter={"must": [{"key": "document_id", "match": {"value": doc.document_id}}]}
                )
                if vector_count > 0:
                    indexed_documents += 1
            
            return {
                "total_documents": total_documents,
                "indexed_documents": indexed_documents,
                "unindexed_documents": total_documents - indexed_documents,
                "total_vectors": collection_stats.get("vector_count", 0),
                "indexed_vectors": collection_stats.get("indexed_vector_count", 0),
                "collection_exists": collection_stats.get("exists", False),
                "sync_status": self._sync_status
            }
            
        except Exception as e:
            logger.error(f"Error getting indexing statistics: {e}")
            return {
                "error": str(e)
            }
