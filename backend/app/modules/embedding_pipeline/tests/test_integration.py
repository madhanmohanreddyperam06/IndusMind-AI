"""Integration tests for embedding pipeline APIs."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import create_app
from app.modules.embedding_pipeline.schemas import (
    HealthCheckResponse,
    EmbeddingResponse,
    SearchResponse,
    EmbeddingStatistics
)


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Mock database session."""
    return Mock()


class TestEmbeddingAPIIntegration:
    """Integration tests for embedding pipeline API endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        with patch('app.modules.embedding_pipeline.service.check_qdrant_health', return_value=True), \
             patch('app.modules.embedding_pipeline.service.get_embedding_generator') as mock_gen:
            mock_model = Mock()
            mock_model._model = Mock()
            mock_model.get_model_info.return_value = {
                "model_name": "test-model",
                "device": "cpu",
                "dimension": 384,
                "max_seq_length": 512,
                "cache_enabled": True,
                "batch_size": 32
            }
            mock_gen.return_value = mock_model
            
            response = client.get("/api/v1/embeddings/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "healthy" in data
            assert "qdrant_connected" in data
            assert "embedding_model_loaded" in data
    
    def test_generate_embedding(self, client):
        """Test embedding generation endpoint."""
        with patch('app.modules.embedding_pipeline.service.get_embedding_generator') as mock_gen:
            mock_model = Mock()
            mock_model.generate_embeddings_with_cache.return_value = [0.1, 0.2, 0.3]
            mock_gen.return_value = mock_model
            
            response = client.post(
                "/api/v1/embeddings/generate",
                json={"text": "Test text", "use_cache": True}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "embedding" in data
            assert "dimension" in data
            assert len(data["embedding"]) == 3
    
    def test_generate_embedding_empty_text(self, client):
        """Test embedding generation with empty text."""
        response = client.post(
            "/api/v1/embeddings/generate",
            json={"text": "", "use_cache": True}
        )
        
        assert response.status_code == 400
    
    def test_generate_embeddings_batch(self, client):
        """Test batch embedding generation endpoint."""
        with patch('app.modules.embedding_pipeline.service.get_embedding_generator') as mock_gen:
            mock_model = Mock()
            mock_model.generate_embeddings_batch.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            mock_gen.return_value = mock_model
            
            response = client.post(
                "/api/v1/embeddings/generate/batch",
                json={"texts": ["Text 1", "Text 2"], "batch_size": 32, "show_progress": False}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "embeddings" in data
            assert len(data["embeddings"]) == 2
    
    def test_get_model_info(self, client):
        """Test getting model information endpoint."""
        with patch('app.modules.embedding_pipeline.service.get_embedding_generator') as mock_gen:
            mock_model = Mock()
            mock_model.get_model_info.return_value = {
                "model_name": "test-model",
                "device": "cpu",
                "dimension": 384,
                "max_seq_length": 512,
                "cache_enabled": True,
                "batch_size": 32
            }
            mock_gen.return_value = mock_model
            
            response = client.get("/api/v1/embeddings/model/info")
            
            assert response.status_code == 200
            data = response.json()
            assert data["model_name"] == "test-model"
            assert data["dimension"] == 384
    
    def test_create_collection(self, client):
        """Test collection creation endpoint."""
        with patch('app.modules.embedding_pipeline.service.QdrantRepository') as mock_repo:
            mock_instance = Mock()
            mock_instance.create_collection.return_value = True
            mock_instance.get_collection_stats.return_value = {
                "exists": True,
                "vector_count": 0,
                "indexed_vector_count": 0
            }
            mock_repo.return_value = mock_instance
            
            response = client.post(
                "/api/v1/embeddings/collections",
                json={"collection_name": "test_collection", "recreate": False}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["exists"] is True
    
    def test_list_collections(self, client):
        """Test listing collections endpoint."""
        with patch('app.config.qdrant.get_qdrant') as mock_qdrant:
            mock_collections = Mock()
            mock_collections.collections = [Mock(name="collection1"), Mock(name="collection2")]
            mock_qdrant.return_value.get_collections.return_value = mock_collections
            
            response = client.get("/api/v1/embeddings/collections")
            
            assert response.status_code == 200
            data = response.json()
            assert "collections" in data
            assert data["total_collections"] == 2
    
    def test_delete_collection(self, client):
        """Test collection deletion endpoint."""
        with patch('app.modules.embedding_pipeline.service.QdrantRepository') as mock_repo:
            mock_instance = Mock()
            mock_instance.delete_collection.return_value = True
            mock_repo.return_value = mock_instance
            
            response = client.delete("/api/v1/embeddings/collections/test_collection")
            
            assert response.status_code == 200
            data = response.json()
            assert "deleted successfully" in data["message"]
    
    def test_index_document(self, client):
        """Test document indexing endpoint."""
        with patch('app.modules.embedding_pipeline.service.EmbeddingSynchronizationService') as mock_sync:
            mock_instance = Mock()
            mock_instance.index_document.return_value = {
                "document_id": "doc-123",
                "success": True,
                "chunks_created": 5,
                "embeddings_generated": 5,
                "vectors_stored": 5,
                "duration_seconds": 1.0,
                "status": "completed",
                "error_message": None
            }
            mock_sync.return_value = mock_instance
            
            response = client.post("/api/v1/embeddings/index/document/doc-123")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["chunks_created"] == 5
    
    def test_index_all_documents(self, client):
        """Test bulk document indexing endpoint."""
        with patch('app.modules.embedding_pipeline.service.EmbeddingSynchronizationService') as mock_sync:
            mock_instance = Mock()
            mock_instance.index_all_documents.return_value = {
                "success": True,
                "documents_processed": 10,
                "total_chunks": 50,
                "total_embeddings": 50,
                "total_vectors": 50,
                "duration_seconds": 10.0,
                "failed_documents": []
            }
            mock_sync.return_value = mock_instance
            
            response = client.post("/api/v1/embeddings/index/all")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["documents_processed"] == 10
    
    def test_delete_document_vectors(self, client):
        """Test deleting document vectors endpoint."""
        with patch('app.modules.embedding_pipeline.service.EmbeddingSynchronizationService') as mock_sync:
            mock_instance = Mock()
            mock_instance.delete_document_vectors.return_value = True
            mock_sync.return_value = mock_instance
            
            response = client.delete("/api/v1/embeddings/document/doc-123")
            
            assert response.status_code == 200
            data = response.json()
            assert "deleted successfully" in data["message"]
    
    def test_get_sync_status(self, client):
        """Test getting sync status endpoint."""
        with patch('app.modules.embedding_pipeline.service.EmbeddingSynchronizationService') as mock_sync:
            mock_instance = Mock()
            mock_instance.get_sync_status.return_value = {
                "document_id": "doc-123",
                "status": "completed",
                "chunks_indexed": 5,
                "embeddings_generated": 5,
                "vectors_stored": 5,
                "error_message": None,
                "last_updated": "2024-01-01T00:00:00"
            }
            mock_sync.return_value = mock_instance
            
            response = client.get("/api/v1/embeddings/sync/status/doc-123")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"
            assert data["chunks_indexed"] == 5
    
    def test_search(self, client):
        """Test semantic search endpoint."""
        with patch('app.modules.embedding_pipeline.service.SemanticSearchEngine') as mock_search:
            mock_instance = Mock()
            mock_instance.search.return_value = {
                "query": "test query",
                "results": [
                    {
                        "chunk_id": "chunk-1",
                        "document_id": "doc-123",
                        "chunk_text": "Test chunk",
                        "score": 0.9,
                        "page_number": 1,
                        "section_title": "Test Section",
                        "document_type": "manual",
                        "equipment_entities": [],
                        "component_entities": [],
                        "entity_ids": [],
                        "relationship_ids": [],
                        "metadata": {}
                    }
                ],
                "total_results": 1,
                "duration_seconds": 0.1,
                "ranking_applied": False
            }
            mock_search.return_value = mock_instance
            
            response = client.post(
                "/api/v1/embeddings/search",
                json={"query": "test query", "limit": 10}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["query"] == "test query"
            assert len(data["results"]) == 1
    
    def test_search_with_filters(self, client):
        """Test semantic search with metadata filters."""
        with patch('app.modules.embedding_pipeline.service.SemanticSearchEngine') as mock_search:
            mock_instance = Mock()
            mock_instance.search.return_value = {
                "query": "pump maintenance",
                "results": [],
                "total_results": 0,
                "duration_seconds": 0.1,
                "ranking_applied": False
            }
            mock_search.return_value = mock_instance
            
            response = client.post(
                "/api/v1/embeddings/search",
                json={
                    "query": "pump maintenance",
                    "limit": 10,
                    "document_type": "manual",
                    "equipment": "pump-101",
                    "score_threshold": 0.7
                }
            )
            
            assert response.status_code == 200
    
    def test_recommend(self, client):
        """Test recommendation endpoint."""
        with patch('app.modules.embedding_pipeline.service.SemanticSearchEngine') as mock_search:
            mock_instance = Mock()
            mock_instance.recommend.return_value = {
                "results": [],
                "total_results": 0,
                "duration_seconds": 0.1
            }
            mock_search.return_value = mock_instance
            
            response = client.post(
                "/api/v1/embeddings/recommend",
                json={"positive_ids": ["id1", "id2"], "limit": 10}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "results" in data
    
    def test_get_statistics(self, client):
        """Test getting statistics endpoint."""
        with patch('app.modules.embedding_pipeline.service.EmbeddingService') as mock_service:
            mock_instance = Mock()
            mock_instance.get_statistics.return_value = {
                "documents_indexed": 10,
                "total_chunks": 50,
                "total_vectors": 50,
                "average_chunks_per_document": 5.0,
                "embedding_model": "test-model",
                "embedding_dimension": 384,
                "collection_size_mb": None,
                "average_search_latency_ms": None,
                "total_indexing_time_seconds": 0.0
            }
            mock_service.return_value = mock_instance
            
            response = client.get("/api/v1/embeddings/statistics")
            
            assert response.status_code == 200
            data = response.json()
            assert data["documents_indexed"] == 10
            assert data["total_vectors"] == 50
    
    def test_clear_all_vectors(self, client):
        """Test clearing all vectors endpoint."""
        with patch('app.modules.embedding_pipeline.service.EmbeddingSynchronizationService') as mock_sync:
            mock_instance = Mock()
            mock_instance.clear_all_vectors.return_value = True
            mock_sync.return_value = mock_instance
            
            response = client.delete("/api/v1/embeddings/clear")
            
            assert response.status_code == 200
            data = response.json()
            assert "cleared successfully" in data["message"]
    
    def test_clear_embedding_cache(self, client):
        """Test clearing embedding cache endpoint."""
        with patch('app.modules.embedding_pipeline.service.get_embedding_generator') as mock_gen:
            mock_model = Mock()
            mock_model.clear_cache.return_value = None
            mock_gen.return_value = mock_model
            
            response = client.post("/api/v1/embeddings/cache/clear")
            
            assert response.status_code == 200
            data = response.json()
            assert "cleared successfully" in data["message"]
    
    def test_chunk_document(self, client):
        """Test document chunking endpoint."""
        with patch('app.modules.embedding_pipeline.service.DocumentChunker') as mock_chunker, \
             patch('app.modules.document_processing.repository.DocumentProcessingRepository') as mock_doc_repo, \
             patch('app.modules.knowledge_extraction.repository.KnowledgeExtractionRepository') as mock_knowledge_repo:
            
            mock_chunker_instance = Mock()
            mock_chunker_instance.chunk_document.return_value = []
            mock_chunker.return_value = mock_chunker_instance
            
            mock_doc_repo_instance = Mock()
            mock_doc_repo_instance.get_processed_document_by_document_id.return_value = Mock(
                document_id="doc-123",
                to_dict=lambda: {
                    "document_id": "doc-123",
                    "id": "proc-doc-123",
                    "text_content": "Test content",
                    "document_type": "manual",
                    "pages": []
                }
            )
            mock_doc_repo.return_value = mock_doc_repo_instance
            
            mock_knowledge_repo_instance = Mock()
            mock_knowledge_repo_instance.get_entities_by_document.return_value = []
            mock_knowledge_repo_instance.get_relationships_by_document.return_value = []
            mock_knowledge_repo.return_value = mock_knowledge_repo_instance
            
            response = client.post(
                "/api/v1/embeddings/chunk",
                json={"document_id": "doc-123", "chunking_strategy": "hierarchical"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "chunks" in data
            assert "total_chunks" in data
