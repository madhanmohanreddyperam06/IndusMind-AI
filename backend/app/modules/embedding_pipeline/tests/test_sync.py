"""Unit tests for embedding synchronization service."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from app.modules.embedding_pipeline.sync import EmbeddingSynchronizationService
from app.modules.embedding_pipeline.schemas import IndexResponse, BulkIndexResponse, SyncStatusSchema
from app.modules.embedding_pipeline.enums import SyncStatus, ChunkingStrategy
from app.modules.embedding_pipeline.exceptions import SynchronizationError


@pytest.fixture
def mock_db():
    """Mock database session."""
    return Mock()


@pytest.fixture
def mock_chunker():
    """Mock document chunker."""
    chunker = Mock()
    chunker.chunk_document.return_value = []
    return chunker


@pytest.fixture
def mock_embedding_generator():
    """Mock embedding generator."""
    generator = Mock()
    generator.generate_embeddings_batch.return_value = []
    return generator


@pytest.fixture
def mock_qdrant_repo():
    """Mock Qdrant repository."""
    repo = Mock()
    repo.count_points.return_value = 0
    repo.upsert_vectors.return_value = True
    repo.delete_document_vectors.return_value = True
    return repo


@pytest.fixture
def mock_doc_processing_repo():
    """Mock document processing repository."""
    repo = Mock()
    return repo


@pytest.fixture
def mock_knowledge_repo():
    """Mock knowledge extraction repository."""
    repo = Mock()
    repo.get_entities_by_document.return_value = []
    repo.get_relationships_by_document.return_value = []
    return repo


@pytest.fixture
def sync_service(mock_db, mock_chunker, mock_embedding_generator, mock_qdrant_repo, 
                 mock_doc_processing_repo, mock_knowledge_repo):
    """Create synchronization service with mocked dependencies."""
    with patch('app.modules.embedding_pipeline.sync.DocumentChunker', return_value=mock_chunker), \
         patch('app.modules.embedding_pipeline.sync.get_embedding_generator', return_value=mock_embedding_generator), \
         patch('app.modules.embedding_pipeline.sync.QdrantRepository', return_value=mock_qdrant_repo), \
         patch('app.modules.embedding_pipeline.sync.DocumentProcessingRepository', return_value=mock_doc_processing_repo), \
         patch('app.modules.embedding_pipeline.sync.KnowledgeExtractionRepository', return_value=mock_knowledge_repo):
        return EmbeddingSynchronizationService(mock_db)


class TestEmbeddingSynchronizationService:
    """Test cases for EmbeddingSynchronizationService."""
    
    def test_index_document_success(self, sync_service, mock_doc_processing_repo, mock_chunker, 
                                   mock_embedding_generator, mock_qdrant_repo):
        """Test successful document indexing."""
        # Mock processed document
        processed_doc = Mock()
        processed_doc.document_id = "doc-123"
        processed_doc.to_dict.return_value = {
            "document_id": "doc-123",
            "id": "proc-doc-123",
            "text_content": "Test content",
            "document_type": "manual",
            "pages": []
        }
        mock_doc_processing_repo.get_processed_document_by_document_id.return_value = processed_doc
        
        # Mock chunk
        mock_chunk = Mock()
        mock_chunk.chunk_id = "chunk-1"
        mock_chunk.chunk_text = "Test chunk"
        mock_chunk.token_count = 10
        mock_chunk.character_count = 50
        mock_chunk.equipment_entities = []
        mock_chunk.component_entities = []
        mock_chunk.relationship_ids = []
        mock_chunk.entity_ids = []
        mock_chunk.page_number = 1
        mock_chunk.section_title = "Test Section"
        mock_chunk.paragraph_numbers = [0]
        mock_chunk.document_type = "manual"
        mock_chunk.metadata = {}
        mock_chunk.chunker.chunk_document.return_value = [mock_chunk]
        
        # Mock embedding
        mock_embedding_generator.generate_embeddings_batch.return_value = [[0.1, 0.2, 0.3]]
        
        # Mock Qdrant
        mock_qdrant_repo.count_points.return_value = 0
        
        result = sync_service.index_document("doc-123")
        
        assert result.success is True
        assert result.document_id == "doc-123"
        assert result.chunks_created == 1
        assert result.embeddings_generated == 1
        assert result.vectors_stored == 1
    
    def test_index_document_already_indexed(self, sync_service, mock_qdrant_repo):
        """Test indexing already indexed document."""
        mock_qdrant_repo.count_points.return_value = 5
        
        result = sync_service.index_document("doc-123", force_reindex=False)
        
        assert result.success is True
        assert result.chunks_created == 0
        assert result.vectors_stored == 5
    
    def test_index_document_not_found(self, sync_service, mock_doc_processing_repo):
        """Test indexing non-existent document."""
        mock_doc_processing_repo.get_processed_document_by_document_id.return_value = None
        
        result = sync_service.index_document("doc-123")
        
        assert result.success is False
        assert result.error_message is not None
    
    def test_index_document_with_reindex(self, sync_service, mock_qdrant_repo):
        """Test document re-indexing."""
        mock_qdrant_repo.count_points.return_value = 5
        mock_qdrant_repo.delete_document_vectors.return_value = True
        mock_qdrant_repo.upsert_vectors.return_value = True
        
        result = sync_service.index_document("doc-123", force_reindex=True)
        
        assert result.success is True
    
    def test_index_all_documents(self, sync_service, mock_doc_processing_repo):
        """Test indexing all documents."""
        # Mock processed documents
        processed_docs = [Mock(document_id=f"doc-{i}") for i in range(3)]
        mock_doc_processing_repo.get_all_processed_documents.return_value = processed_docs
        
        # Mock individual indexing
        sync_service.index_document = Mock(side_effect=[
            IndexResponse(
                document_id="doc-0",
                success=True,
                chunks_created=5,
                embeddings_generated=5,
                vectors_stored=5,
                duration_seconds=1.0,
                status="completed"
            ),
            IndexResponse(
                document_id="doc-1",
                success=True,
                chunks_created=3,
                embeddings_generated=3,
                vectors_stored=3,
                duration_seconds=0.5,
                status="completed"
            ),
            IndexResponse(
                document_id="doc-2",
                success=True,
                chunks_created=4,
                embeddings_generated=4,
                vectors_stored=4,
                duration_seconds=0.7,
                status="completed"
            )
        ])
        
        result = sync_service.index_all_documents(force_reindex=False)
        
        assert result.success is True
        assert result.documents_processed == 3
        assert result.total_chunks == 12
        assert result.total_embeddings == 12
        assert result.total_vectors == 12
    
    def test_index_all_documents_with_failures(self, sync_service, mock_doc_processing_repo):
        """Test indexing all documents with some failures."""
        processed_docs = [Mock(document_id=f"doc-{i}") for i in range(3)]
        mock_doc_processing_repo.get_all_processed_documents.return_value = processed_docs
        
        sync_service.index_document = Mock(side_effect=[
            IndexResponse(
                document_id="doc-0",
                success=True,
                chunks_created=5,
                embeddings_generated=5,
                vectors_stored=5,
                duration_seconds=1.0,
                status="completed"
            ),
            IndexResponse(
                document_id="doc-1",
                success=False,
                chunks_created=0,
                embeddings_generated=0,
                vectors_stored=0,
                duration_seconds=0.5,
                status="failed",
                error_message="Failed"
            ),
            IndexResponse(
                document_id="doc-2",
                success=True,
                chunks_created=4,
                embeddings_generated=4,
                vectors_stored=4,
                duration_seconds=0.7,
                status="completed"
            )
        ])
        
        result = sync_service.index_all_documents(force_reindex=False)
        
        assert result.success is False
        assert result.failed_documents == ["doc-1"]
    
    def test_delete_document_vectors(self, sync_service, mock_qdrant_repo):
        """Test deleting document vectors."""
        mock_qdrant_repo.delete_document_vectors.return_value = True
        
        result = sync_service.delete_document_vectors("doc-123")
        
        assert result is True
        mock_qdrant_repo.delete_document_vectors.assert_called_once_with("doc-123")
    
    def test_reindex_document(self, sync_service):
        """Test re-indexing document."""
        sync_service.index_document = Mock(return_value=IndexResponse(
            document_id="doc-123",
            success=True,
            chunks_created=5,
            embeddings_generated=5,
            vectors_stored=5,
            duration_seconds=1.0,
            status="completed"
        ))
        
        result = sync_service.reindex_document("doc-123", ChunkingStrategy.PARAGRAPH)
        
        assert result.success is True
        sync_service.index_document.assert_called_once()
    
    def test_get_sync_status_indexed(self, sync_service, mock_qdrant_repo):
        """Test getting sync status for indexed document."""
        mock_qdrant_repo.count_points.return_value = 10
        
        status = sync_service.get_sync_status("doc-123")
        
        assert status.status == SyncStatus.COMPLETED
        assert status.chunks_indexed == 10
        assert status.embeddings_generated == 10
        assert status.vectors_stored == 10
    
    def test_get_sync_status_pending(self, sync_service, mock_qdrant_repo):
        """Test getting sync status for pending document."""
        mock_qdrant_repo.count_points.return_value = 0
        
        status = sync_service.get_sync_status("doc-123")
        
        assert status.status == SyncStatus.PENDING
        assert status.chunks_indexed == 0
    
    def test_get_sync_status_in_progress(self, sync_service):
        """Test getting sync status for document in progress."""
        sync_service._sync_status["doc-123"] = {
            "status": SyncStatus.IN_PROGRESS,
            "chunks_indexed": 5,
            "embeddings_generated": 3,
            "vectors_stored": 0,
            "error_message": None,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        status = sync_service.get_sync_status("doc-123")
        
        assert status.status == SyncStatus.IN_PROGRESS
        assert status.chunks_indexed == 5
    
    def test_get_all_sync_status(self, sync_service, mock_doc_processing_repo, mock_qdrant_repo):
        """Test getting sync status for all documents."""
        processed_docs = [Mock(document_id=f"doc-{i}") for i in range(3)]
        mock_doc_processing_repo.get_all_processed_documents.return_value = processed_docs
        mock_qdrant_repo.count_points.return_value = 5
        
        status_dict = sync_service.get_all_sync_status()
        
        assert len(status_dict) == 3
        assert all(status.status == SyncStatus.COMPLETED for status in status_dict.values())
    
    def test_retry_failed_indexing_success(self, sync_service):
        """Test retrying failed indexing successfully."""
        sync_service.index_document = Mock(return_value=IndexResponse(
            document_id="doc-123",
            success=True,
            chunks_created=5,
            embeddings_generated=5,
            vectors_stored=5,
            duration_seconds=1.0,
            status="completed"
        ))
        
        result = sync_service.retry_failed_indexing("doc-123", max_retries=2)
        
        assert result.success is True
    
    def test_retry_failed_indexing_all_fail(self, sync_service):
        """Test retrying when all attempts fail."""
        sync_service.index_document = Mock(return_value=IndexResponse(
            document_id="doc-123",
            success=False,
            chunks_created=0,
            embeddings_generated=0,
            vectors_stored=0,
            duration_seconds=0.5,
            status="failed",
            error_message="Failed"
        ))
        
        result = sync_service.retry_failed_indexing("doc-123", max_retries=2)
        
        assert result.success is False
        assert "Failed after 2 retry attempts" in result.error_message
    
    def test_clear_all_vectors(self, sync_service, mock_qdrant_repo):
        """Test clearing all vectors."""
        mock_qdrant_repo.delete_collection.return_value = True
        mock_qdrant_repo.create_collection.return_value = True
        
        result = sync_service.clear_all_vectors()
        
        assert result is True
        assert len(sync_service._sync_status) == 0
    
    def test_get_indexing_statistics(self, sync_service, mock_doc_processing_repo, mock_qdrant_repo):
        """Test getting indexing statistics."""
        processed_docs = [Mock(document_id=f"doc-{i}") for i in range(5)]
        mock_doc_processing_repo.get_all_processed_documents.return_value = processed_docs
        mock_qdrant_repo.get_collection_stats.return_value = {
            "exists": True,
            "vector_count": 50,
            "indexed_vector_count": 50
        }
        mock_qdrant_repo.count_points.return_value = 10
        
        stats = sync_service.get_indexing_statistics()
        
        assert stats["total_documents"] == 5
        assert stats["total_vectors"] == 50
