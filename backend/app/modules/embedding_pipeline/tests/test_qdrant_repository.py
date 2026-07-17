"""Unit tests for Qdrant repository."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from qdrant_client.models import Distance, VectorParams
from app.modules.embedding_pipeline.qdrant_repository import QdrantRepository
from app.modules.embedding_pipeline.exceptions import (
    VectorStorageError,
    CollectionNotFoundError,
    QdrantConnectionError
)


@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client."""
    client = Mock()
    client.get_collections.return_value = Mock(collections=[])
    return client


@pytest.fixture
def repository(mock_qdrant_client):
    """Create repository instance with mocked client."""
    with patch('app.modules.embedding_pipeline.qdrant_repository.get_qdrant', return_value=mock_qdrant_client):
        return QdrantRepository()


class TestQdrantRepository:
    """Test cases for QdrantRepository."""
    
    def test_initialization(self, mock_qdrant_client):
        """Test repository initialization."""
        with patch('app.modules.embedding_pipeline.qdrant_repository.get_qdrant', return_value=mock_qdrant_client):
            repo = QdrantRepository()
            assert repo.collection_name is not None
            assert repo.client is not None
    
    def test_connection_error(self):
        """Test connection error handling."""
        with patch('app.modules.embedding_pipeline.qdrant_repository.get_qdrant', side_effect=Exception("Connection failed")):
            with pytest.raises(QdrantConnectionError):
                QdrantRepository()
    
    def test_create_collection(self, repository, mock_qdrant_client):
        """Test collection creation."""
        mock_qdrant_client.collection_exists.return_value = False
        mock_qdrant_client.create_collection.return_value = None
        
        result = repository.create_collection()
        
        assert result is True
        mock_qdrant_client.create_collection.assert_called_once()
    
    def test_create_collection_recreate(self, repository, mock_qdrant_client):
        """Test collection recreation."""
        mock_qdrant_client.collection_exists.return_value = True
        mock_qdrant_client.delete_collection.return_value = None
        mock_qdrant_client.create_collection.return_value = None
        
        result = repository.create_collection(recreate=True)
        
        assert result is True
        mock_qdrant_client.delete_collection.assert_called_once()
        mock_qdrant_client.create_collection.assert_called_once()
    
    def test_delete_collection(self, repository, mock_qdrant_client):
        """Test collection deletion."""
        mock_qdrant_client.collection_exists.return_value = True
        mock_qdrant_client.delete_collection.return_value = None
        
        result = repository.delete_collection()
        
        assert result is True
        mock_qdrant_client.delete_collection.assert_called_once()
    
    def test_delete_collection_not_exists(self, repository, mock_qdrant_client):
        """Test deleting non-existent collection."""
        mock_qdrant_client.collection_exists.return_value = False
        
        result = repository.delete_collection()
        
        assert result is True
    
    def test_collection_exists(self, repository, mock_qdrant_client):
        """Test checking if collection exists."""
        mock_collections = Mock()
        mock_collections.collections = [Mock(name="test_collection")]
        mock_qdrant_client.get_collections.return_value = mock_collections
        
        repository.collection_name = "test_collection"
        exists = repository.collection_exists()
        
        assert exists is True
    
    def test_collection_not_exists(self, repository, mock_qdrant_client):
        """Test checking if collection doesn't exist."""
        mock_collections = Mock()
        mock_collections.collections = [Mock(name="other_collection")]
        mock_qdrant_client.get_collections.return_value = mock_collections
        
        repository.collection_name = "test_collection"
        exists = repository.collection_exists()
        
        assert exists is False
    
    def test_upsert_vectors(self, repository, mock_qdrant_client):
        """Test upserting vectors."""
        mock_qdrant_client.collection_exists.return_value = True
        mock_qdrant_client.upsert.return_value = None
        
        vectors = [[0.1, 0.2, 0.3]]
        payloads = [{"test": "payload"}]
        
        result = repository.upsert_vectors(vectors, payloads)
        
        assert result is True
        mock_qdrant_client.upsert.assert_called_once()
    
    def test_upsert_vectors_create_collection(self, repository, mock_qdrant_client):
        """Test upserting vectors when collection doesn't exist."""
        mock_qdrant_client.collection_exists.return_value = False
        mock_qdrant_client.create_collection.return_value = None
        mock_qdrant_client.upsert.return_value = None
        
        vectors = [[0.1, 0.2, 0.3]]
        payloads = [{"test": "payload"}]
        
        result = repository.upsert_vectors(vectors, payloads)
        
        assert result is True
        mock_qdrant_client.create_collection.assert_called_once()
    
    def test_insert_vectors(self, repository, mock_qdrant_client):
        """Test inserting vectors."""
        mock_qdrant_client.collection_exists.return_value = True
        mock_qdrant_client.insert.return_value = None
        
        vectors = [[0.1, 0.2, 0.3]]
        payloads = [{"test": "payload"}]
        
        result = repository.insert_vectors(vectors, payloads)
        
        assert result is True
        mock_qdrant_client.insert.assert_called_once()
    
    def test_delete_vectors(self, repository, mock_qdrant_client):
        """Test deleting vectors by IDs."""
        mock_qdrant_client.collection_exists.return_value = True
        mock_qdrant_client.delete.return_value = None
        
        result = repository.delete_vectors(["id1", "id2"])
        
        assert result is True
        mock_qdrant_client.delete.assert_called_once()
    
    def test_delete_document_vectors(self, repository, mock_qdrant_client):
        """Test deleting vectors for a document."""
        mock_qdrant_client.collection_exists.return_value = True
        mock_qdrant_client.delete.return_value = None
        
        result = repository.delete_document_vectors("doc-123")
        
        assert result is True
    
    def test_search(self, repository, mock_qdrant_client):
        """Test vector search."""
        mock_qdrant_client.collection_exists.return_value = True
        mock_result = Mock()
        mock_result.id = "test-id"
        mock_result.score = 0.9
        mock_result.payload = {"test": "payload"}
        mock_result.vector = [0.1, 0.2, 0.3]
        mock_qdrant_client.search.return_value = [mock_result]
        
        query_vector = [0.1, 0.2, 0.3]
        results = repository.search(query_vector, limit=10)
        
        assert len(results) == 1
        assert results[0]["id"] == "test-id"
        assert results[0]["score"] == 0.9
    
    def test_search_not_exists(self, repository, mock_qdrant_client):
        """Test search when collection doesn't exist."""
        mock_qdrant_client.collection_exists.return_value = False
        
        with pytest.raises(CollectionNotFoundError):
            repository.search([0.1, 0.2, 0.3])
    
    def test_search_with_threshold(self, repository, mock_qdrant_client):
        """Test search with score threshold."""
        mock_qdrant_client.collection_exists.return_value = True
        mock_result1 = Mock(id="id1", score=0.8, payload={}, vector=[])
        mock_result2 = Mock(id="id2", score=0.5, payload={}, vector=[])
        mock_qdrant_client.search.return_value = [mock_result1, mock_result2]
        
        results = repository.search([0.1, 0.2, 0.3], limit=10, score_threshold=0.7)
        
        assert len(results) == 1
        assert results[0]["id"] == "id1"
    
    def test_search_batch(self, repository, mock_qdrant_client):
        """Test batch search."""
        mock_qdrant_client.collection_exists.return_value = True
        mock_result = Mock(id="test-id", score=0.9, payload={}, vector=[])
        mock_qdrant_client.search_batch.return_value = [[mock_result]]
        
        query_vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        results = repository.search_batch(query_vectors, limit=10)
        
        assert len(results) == 2
    
    def test_recommend(self, repository, mock_qdrant_client):
        """Test recommendation."""
        mock_qdrant_client.collection_exists.return_value = True
        mock_result = Mock(id="test-id", score=0.9, payload={}, vector=[])
        mock_qdrant_client.recommend.return_value = [mock_result]
        
        results = repository.recommend(positive_ids=["id1"], limit=10)
        
        assert len(results) == 1
        assert results[0]["id"] == "test-id"
    
    def test_get_point(self, repository, mock_qdrant_client):
        """Test getting a point by ID."""
        mock_qdrant_client.collection_exists.return_value = True
        mock_point = Mock(id="test-id", payload={"test": "payload"}, vector=[0.1, 0.2, 0.3])
        mock_qdrant_client.retrieve.return_value = [mock_point]
        
        point = repository.get_point("test-id")
        
        assert point is not None
        assert point["id"] == "test-id"
    
    def test_get_point_not_found(self, repository, mock_qdrant_client):
        """Test getting non-existent point."""
        mock_qdrant_client.collection_exists.return_value = True
        mock_qdrant_client.retrieve.return_value = []
        
        point = repository.get_point("non-existent")
        
        assert point is None
    
    def test_count_points(self, repository, mock_qdrant_client):
        """Test counting points."""
        mock_qdrant_client.collection_exists.return_value = True
        mock_count = Mock(count=100)
        mock_qdrant_client.count.return_value = mock_count
        
        count = repository.count_points()
        
        assert count == 100
    
    def test_count_points_with_filter(self, repository, mock_qdrant_client):
        """Test counting points with filter."""
        mock_qdrant_client.collection_exists.return_value = True
        mock_count = Mock(count=50)
        mock_qdrant_client.count.return_value = mock_count
        
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        filter = Filter(must=[FieldCondition(key="document_id", match=MatchValue(value="doc-123"))])
        
        count = repository.count_points(filter=filter)
        
        assert count == 50
    
    def test_get_collection_info(self, repository, mock_qdrant_client):
        """Test getting collection info."""
        mock_qdrant_client.collection_exists.return_value = True
        mock_info = Mock()
        mock_info.config.params.vectors.size = 384
        mock_info.points_count = 100
        mock_info.indexed_vector_count = 100
        mock_info.status = "green"
        mock_info.optimizer_status = "ok"
        mock_info.config.params.dict.return_value = {}
        mock_qdrant_client.get_collection.return_value = mock_info
        
        info = repository.get_collection_info()
        
        assert info["vector_count"] == 100
        assert info["indexed_vector_count"] == 100
    
    def test_get_collection_info_not_exists(self, repository, mock_qdrant_client):
        """Test getting collection info when collection doesn't exist."""
        mock_qdrant_client.collection_exists.return_value = False
        
        with pytest.raises(CollectionNotFoundError):
            repository.get_collection_info()
    
    def test_get_collection_stats(self, repository, mock_qdrant_client):
        """Test getting collection statistics."""
        mock_qdrant_client.collection_exists.return_value = True
        mock_info = Mock()
        mock_info.config.params.vectors.size = 384
        mock_info.points_count = 100
        mock_info.indexed_vector_count = 100
        mock_info.status = "green"
        mock_info.optimizer_status = "ok"
        mock_info.config.params.dict.return_value = {}
        mock_qdrant_client.get_collection.return_value = mock_info
        
        stats = repository.get_collection_stats()
        
        assert stats["exists"] is True
        assert stats["vector_count"] == 100
    
    def test_get_collection_stats_not_exists(self, repository, mock_qdrant_client):
        """Test getting collection stats when collection doesn't exist."""
        mock_qdrant_client.collection_exists.return_value = False
        
        stats = repository.get_collection_stats()
        
        assert stats["exists"] is False
        assert stats["vector_count"] == 0
    
    def test_scroll(self, repository, mock_qdrant_client):
        """Test scrolling through points."""
        mock_qdrant_client.collection_exists.return_value = True
        mock_point = Mock(id="test-id", payload={"test": "payload"})
        mock_qdrant_client.scroll.return_value = ([mock_point], None)
        
        points, next_offset = repository.scroll(limit=10)
        
        assert len(points) == 1
        assert points[0]["id"] == "test-id"
