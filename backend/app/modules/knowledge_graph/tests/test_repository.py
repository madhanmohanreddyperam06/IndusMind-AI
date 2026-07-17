"""Unit tests for graph repository."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from uuid import uuid4
from app.modules.knowledge_graph.repository import GraphRepository
from app.modules.knowledge_graph.schemas import (
    GraphNodeCreate,
    GraphNodeUpdate,
    GraphRelationshipCreate,
    GraphRelationshipUpdate
)
from app.modules.knowledge_graph.enums import GraphEntityType, GraphRelationshipType
from app.modules.knowledge_graph.exceptions import (
    GraphConnectionError,
    NodeNotFoundError,
    GraphQueryError
)


@pytest.fixture
def mock_driver():
    """Mock Neo4j driver."""
    driver = Mock()
    session = Mock()
    driver.session.return_value.__enter__.return_value = session
    driver.session.return_value.__exit__.return_value = None
    return driver


@pytest.fixture
def repository(mock_driver):
    """Create repository instance with mocked driver."""
    with patch('app.modules.knowledge_graph.repository.get_neo4j', return_value=mock_driver):
        repo = GraphRepository()
        return repo


@pytest.fixture
def sample_node_data():
    """Sample node creation data."""
    return GraphNodeCreate(
        entity_id="test-entity-123",
        entity_type=GraphEntityType.EQUIPMENT,
        normalized_name="pump-101",
        original_name="Pump-101",
        confidence_score=0.9,
        extraction_method="RULE_BASED",
        metadata={"tag": "P-101"}
    )


@pytest.fixture
def sample_relationship_data():
    """Sample relationship creation data."""
    return GraphRelationshipCreate(
        source_entity_id="source-123",
        target_entity_id="target-456",
        relationship_type=GraphRelationshipType.HAS_COMPONENT,
        confidence_score=0.85,
        evidence="Pump-101 has component Motor-202"
    )


class TestGraphRepository:
    """Test cases for GraphRepository."""
    
    def test_create_node(self, repository, mock_driver, sample_node_data):
        """Test creating a new node."""
        # Mock the session and result
        session = mock_driver.session.return_value.__enter__.return_value
        result = Mock()
        result.single.return_value = Mock()
        result.single.return_value.__getitem__ = Mock(side_effect=lambda x: {
            "uuid": sample_node_data.uuid,
            "entity_id": sample_node_data.entity_id,
            "entity_type": sample_node_data.entity_type,
            "normalized_name": sample_node_data.normalized_name,
            "original_name": sample_node_data.original_name,
            "confidence_score": sample_node_data.confidence_score,
            "extraction_method": sample_node_data.extraction_method,
            "metadata": sample_node_data.metadata,
            "created_at": datetime.utcnow()
        }.get(x))
        session.run.return_value = result
        
        # Create node
        node = repository.create_node(sample_node_data)
        
        # Verify
        assert node is not None
        assert node.entity_id == sample_node_data.entity_id
        assert node.entity_type == sample_node_data.entity_type
        session.run.assert_called_once()
    
    def test_get_node_by_id(self, repository, mock_driver, sample_node_data):
        """Test getting a node by ID."""
        session = mock_driver.session.return_value.__enter__.return_value
        result = Mock()
        result.single.return_value = Mock()
        result.single.return_value.__getitem__ = Mock(side_effect=lambda x: {
            "uuid": sample_node_data.uuid,
            "entity_id": sample_node_data.entity_id,
            "entity_type": sample_node_data.entity_type,
            "normalized_name": sample_node_data.normalized_name,
            "original_name": sample_node_data.original_name,
            "confidence_score": sample_node_data.confidence_score,
            "extraction_method": sample_node_data.extraction_method,
            "metadata": sample_node_data.metadata,
            "created_at": datetime.utcnow()
        }.get(x))
        session.run.return_value = result
        
        node = repository.get_node_by_id(sample_node_data.entity_id)
        
        assert node is not None
        assert node.entity_id == sample_node_data.entity_id
    
    def test_get_node_by_id_not_found(self, repository, mock_driver):
        """Test getting a non-existent node."""
        session = mock_driver.session.return_value.__enter__.return_value
        result = Mock()
        result.single.return_value = None
        session.run.return_value = result
        
        node = repository.get_node_by_id("non-existent")
        
        assert node is None
    
    def test_update_node(self, repository, mock_driver, sample_node_data):
        """Test updating a node."""
        session = mock_driver.session.return_value.__enter__.return_value
        result = Mock()
        result.single.return_value = Mock()
        result.single.return_value.__getitem__ = Mock(side_effect=lambda x: {
            "uuid": sample_node_data.uuid,
            "entity_id": sample_node_data.entity_id,
            "entity_type": sample_node_data.entity_type,
            "normalized_name": "updated-name",
            "original_name": sample_node_data.original_name,
            "confidence_score": 0.95,
            "extraction_method": sample_node_data.extraction_method,
            "metadata": sample_node_data.metadata,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }.get(x))
        session.run.return_value = result
        
        update_data = GraphNodeUpdate(
            normalized_name="updated-name",
            confidence_score=0.95
        )
        
        node = repository.update_node(sample_node_data.entity_id, update_data)
        
        assert node is not None
        assert node.normalized_name == "updated-name"
        assert node.confidence_score == 0.95
    
    def test_delete_node(self, repository, mock_driver):
        """Test deleting a node."""
        session = mock_driver.session.return_value.__enter__.return_value
        result = Mock()
        result.single.return_value = Mock()
        result.single.return_value.__getitem__ = Mock(return_value=1)
        session.run.return_value = result
        
        deleted = repository.delete_node("test-entity-123")
        
        assert deleted is True
    
    def test_delete_node_not_found(self, repository, mock_driver):
        """Test deleting a non-existent node."""
        session = mock_driver.session.return_value.__enter__.return_value
        result = Mock()
        result.single.return_value = Mock()
        result.single.return_value.__getitem__ = Mock(return_value=0)
        session.run.return_value = result
        
        deleted = repository.delete_node("non-existent")
        
        assert deleted is False
    
    def test_create_relationship(self, repository, mock_driver, sample_relationship_data):
        """Test creating a relationship."""
        session = mock_driver.session.return_value.__enter__.return_value
        result = Mock()
        result.single.return_value = Mock()
        result.single.return_value.__getitem__ = Mock(side_effect=lambda x: {
            "r": Mock(),
            "source_id": sample_relationship_data.source_entity_id,
            "target_id": sample_relationship_data.target_entity_id
        }.get(x))
        session.run.return_value = result
        
        rel = repository.create_relationship(sample_relationship_data)
        
        assert rel is not None
        session.run.assert_called_once()
    
    def test_get_relationship_by_id(self, repository, mock_driver, sample_relationship_data):
        """Test getting a relationship by ID."""
        session = mock_driver.session.return_value.__enter__.return_value
        result = Mock()
        result.single.return_value = Mock()
        result.single.return_value.__getitem__ = Mock(side_effect=lambda x: {
            "r": Mock(),
            "source_id": sample_relationship_data.source_entity_id,
            "target_id": sample_relationship_data.target_entity_id
        }.get(x))
        session.run.return_value = result
        
        rel = repository.get_relationship_by_id("test-rel-123")
        
        assert rel is not None
    
    def test_get_neighbors(self, repository, mock_driver):
        """Test getting neighbors of a node."""
        session = mock_driver.session.return_value.__enter__.return_value
        result = Mock()
        
        # Mock multiple records
        records = []
        for i in range(3):
            record = Mock()
            record.__getitem__ = Mock(side_effect=lambda x: {
                "uuid": str(uuid4()),
                "entity_id": f"neighbor-{i}",
                "entity_type": GraphEntityType.COMPONENT,
                "normalized_name": f"component-{i}",
                "original_name": f"Component-{i}",
                "confidence_score": 0.8,
                "relationship_type": GraphRelationshipType.HAS_COMPONENT,
                "relationship_confidence": 0.85
            }.get(x))
            records.append(record)
        
        result.__iter__ = Mock(return_value=iter(records))
        session.run.return_value = result
        
        neighbors = repository.get_neighbors("test-entity-123")
        
        assert len(neighbors) == 3
    
    def test_find_shortest_path(self, repository, mock_driver):
        """Test finding shortest path between nodes."""
        session = mock_driver.session.return_value.__enter__.return_value
        result = Mock()
        result.single.return_value = None  # No path found
        session.run.return_value = result
        
        path = repository.find_shortest_path("source-123", "target-456")
        
        assert path is None
    
    def test_get_graph_statistics(self, repository, mock_driver):
        """Test getting graph statistics."""
        session = mock_driver.session.return_value.__enter__.return_value
        
        # Mock node statistics
        node_result = Mock()
        node_records = [
            Mock(__getitem__=Mock(side_effect=lambda x: {"Equipment": 10}.get(x))),
            Mock(__getitem__=Mock(side_effect=lambda x: {"Component": 20}.get(x)))
        ]
        node_result.__iter__ = Mock(return_value=iter(node_records))
        
        # Mock relationship statistics
        rel_result = Mock()
        rel_records = [
            Mock(__getitem__=Mock(side_effect=lambda x: {"HAS_COMPONENT": 15}.get(x)))
        ]
        rel_result.__iter__ = Mock(return_value=iter(rel_records))
        
        # Mock degree statistics
        degree_result = Mock()
        degree_result.single.return_value = Mock()
        degree_result.single.return_value.__getitem__ = Mock(return_value=2.5)
        
        # Mock connected entities
        connected_result = Mock()
        connected_records = [
            Mock(__getitem__=Mock(side_effect=lambda x: {
                "entity_id": "test-1",
                "entity_type": GraphEntityType.EQUIPMENT,
                "normalized_name": "pump-101",
                "degree": 5
            }.get(x)))
        ]
        connected_result.__iter__ = Mock(return_value=iter(connected_records))
        
        # Set up session.run to return different results based on query
        def run_side_effect(query, **kwargs):
            if "MATCH (n)" in query and "count(n)" in query:
                return node_result
            elif "MATCH ()-[r]->()" in query and "count(r)" in query:
                return rel_result
            elif "avg(degree)" in query:
                return degree_result
            elif "ORDER BY degree DESC" in query:
                return connected_result
            return Mock()
        
        session.run = Mock(side_effect=run_side_effect)
        
        stats = repository.get_graph_statistics()
        
        assert stats["total_nodes"] > 0
        assert stats["total_relationships"] > 0
        assert "nodes_by_type" in stats
        assert "relationships_by_type" in stats
    
    def test_get_node_degree(self, repository, mock_driver):
        """Test getting node degree statistics."""
        session = mock_driver.session.return_value.__enter__.return_value
        result = Mock()
        result.single.return_value = Mock()
        result.single.return_value.__getitem__ = Mock(side_effect=lambda x: {
            "in_degree": 2,
            "out_degree": 3,
            "total_degree": 5
        }.get(x))
        session.run.return_value = result
        
        degree = repository.get_node_degree("test-entity-123")
        
        assert degree["in_degree"] == 2
        assert degree["out_degree"] == 3
        assert degree["total_degree"] == 5
    
    def test_connection_error(self, repository, mock_driver):
        """Test handling of connection errors."""
        session = mock_driver.session.return_value.__enter__.return_value
        session.run.side_effect = Exception("Connection failed")
        
        with pytest.raises(GraphConnectionError):
            repository.create_node(GraphNodeCreate(
                entity_id="test",
                entity_type=GraphEntityType.EQUIPMENT,
                normalized_name="test",
                original_name="Test"
            ))
