"""Unit tests for graph builder."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from uuid import uuid4
from app.modules.knowledge_graph.builder import GraphBuilder
from app.modules.knowledge_graph.schemas import GraphNodeCreate
from app.modules.knowledge_graph.enums import GraphEntityType
from app.modules.knowledge_graph.exceptions import GraphBuilderError


@pytest.fixture
def mock_mysql_db():
    """Mock MySQL database session."""
    db = Mock()
    return db


@pytest.fixture
def mock_mysql_repo():
    """Mock MySQL knowledge extraction repository."""
    repo = Mock()
    return repo


@pytest.fixture
def mock_graph_repo():
    """Mock graph repository."""
    repo = Mock()
    return repo


@pytest.fixture
def builder(mock_mysql_db, mock_mysql_repo, mock_graph_repo):
    """Create graph builder with mocked dependencies."""
    with patch('app.modules.knowledge_graph.builder.KnowledgeExtractionRepository', return_value=mock_mysql_repo), \
         patch('app.modules.knowledge_graph.builder.GraphRepository', return_value=mock_graph_repo):
        return GraphBuilder(mock_mysql_db)


@pytest.fixture
def sample_mysql_entity():
    """Sample MySQL entity."""
    entity = Mock()
    entity.entity_id = "entity-123"
    entity.entity_type = "EQUIPMENT"
    entity.normalized_name = "pump-101"
    entity.name = "Pump-101"
    entity.confidence_score = 0.9
    entity.extraction_method = "RULE_BASED"
    entity.entity_metadata = {"tag": "P-101"}
    return entity


@pytest.fixture
def sample_mysql_relationship():
    """Sample MySQL relationship."""
    rel = Mock()
    rel.relationship_id = "rel-123"
    rel.source_entity_id = "source-123"
    rel.target_entity_id = "target-456"
    rel.relationship_type = "HAS_COMPONENT"
    rel.confidence_score = 0.85
    rel.evidence_text = "Pump-101 has component Motor-202"
    return rel


class TestGraphBuilder:
    """Test cases for GraphBuilder."""
    
    def test_entity_to_node_create(self, builder, sample_mysql_entity):
        """Test converting MySQL entity to graph node create schema."""
        node_data = builder._entity_to_node_create(sample_mysql_entity)
        
        assert isinstance(node_data, GraphNodeCreate)
        assert node_data.entity_id == sample_mysql_entity.entity_id
        assert node_data.entity_type == GraphEntityType.EQUIPMENT
        assert node_data.normalized_name == sample_mysql_entity.normalized_name
        assert node_data.original_name == sample_mysql_entity.name
        assert node_data.confidence_score == sample_mysql_entity.confidence_score
    
    def test_relationship_to_rel_create(self, builder, sample_mysql_relationship):
        """Test converting MySQL relationship to graph relationship create schema."""
        entity_name_to_id = {
            "source-123": "source-123",
            "target-456": "target-456"
        }
        
        rel_data = builder._relationship_to_rel_create(
            sample_mysql_relationship,
            entity_name_to_id
        )
        
        assert rel_data is not None
        assert rel_data.source_entity_id == sample_mysql_relationship.source_entity_id
        assert rel_data.target_entity_id == sample_mysql_relationship.target_entity_id
        assert rel_data.relationship_id == sample_mysql_relationship.relationship_id
    
    def test_relationship_to_rel_create_missing_ids(self, builder, sample_mysql_relationship):
        """Test relationship conversion with missing entity IDs."""
        entity_name_to_id = {}
        
        rel_data = builder._relationship_to_rel_create(
            sample_mysql_relationship,
            entity_name_to_id
        )
        
        assert rel_data is None
    
    def test_build_from_document(self, builder, mock_mysql_repo, mock_graph_repo, 
                                 sample_mysql_entity, sample_mysql_relationship):
        """Test building graph from a single document."""
        # Mock MySQL repository
        mock_mysql_repo.get_entities_by_document.return_value = [sample_mysql_entity]
        mock_mysql_repo.get_relationships_by_document.return_value = [sample_mysql_relationship]
        
        # Mock graph repository
        mock_graph_repo.get_node_by_id.return_value = None  # Node doesn't exist
        mock_graph_repo.create_node.return_value = Mock()
        mock_graph_repo.get_relationship_by_id.return_value = None  # Relationship doesn't exist
        mock_graph_repo.create_relationship.return_value = Mock()
        
        stats = builder.build_from_document("doc-123")
        
        assert stats["document_id"] == "doc-123"
        assert stats["entities_processed"] == 1
        assert stats["relationships_processed"] == 1
        assert stats["nodes_created"] == 1
        assert stats["relationships_created"] == 1
    
    def test_build_from_document_existing_nodes(self, builder, mock_mysql_repo, mock_graph_repo,
                                               sample_mysql_entity, sample_mysql_relationship):
        """Test building graph when nodes already exist."""
        # Mock MySQL repository
        mock_mysql_repo.get_entities_by_document.return_value = [sample_mysql_entity]
        mock_mysql_repo.get_relationships_by_document.return_value = [sample_mysql_relationship]
        
        # Mock graph repository - node exists
        mock_graph_repo.get_node_by_id.return_value = Mock()
        mock_graph_repo.update_node.return_value = Mock()
        mock_graph_repo.get_relationship_by_id.return_value = None
        mock_graph_repo.create_relationship.return_value = Mock()
        
        stats = builder.build_from_document("doc-123")
        
        assert stats["nodes_updated"] == 1
        assert stats["nodes_created"] == 0
    
    def test_build_from_all_documents(self, builder, mock_mysql_repo, mock_graph_repo):
        """Test building graph from all documents."""
        # Mock distinct document IDs
        mock_mysql_db = Mock()
        mock_mysql_db.query.return_value.distinct.return_value.all.return_value = [
            ("doc-123",), ("doc-456",)
        ]
        
        # Mock individual document build
        builder.build_from_document = Mock(side_effect=[
            {
                "document_id": "doc-123",
                "entities_processed": 5,
                "relationships_processed": 3,
                "nodes_created": 5,
                "nodes_updated": 0,
                "relationships_created": 3,
                "relationships_skipped": 0
            },
            {
                "document_id": "doc-456",
                "entities_processed": 3,
                "relationships_processed": 2,
                "nodes_created": 3,
                "nodes_updated": 0,
                "relationships_created": 2,
                "relationships_skipped": 0
            }
        ])
        
        with patch.object(builder, 'mysql_db', mock_mysql_db):
            stats = builder.build_from_all_documents()
        
        assert stats["documents_processed"] == 2
        assert stats["total_entities"] == 8
        assert stats["total_relationships"] == 5
    
    def test_rebuild_graph(self, builder, mock_graph_repo):
        """Test rebuilding entire graph."""
        # Mock delete all
        mock_graph_repo._get_session.return_value.__enter__.return_value.run.return_value = None
        
        # Mock build from all documents
        builder.build_from_all_documents = Mock(return_value={
            "documents_processed": 2,
            "total_entities": 10,
            "total_relationships": 5,
            "total_nodes_created": 10,
            "total_nodes_updated": 0,
            "total_relationships_created": 5,
            "total_relationships_skipped": 0
        })
        
        stats = builder.rebuild_graph()
        
        assert stats["rebuild"] is True
        assert stats["total_nodes_created"] == 10
    
    def test_create_document_node(self, builder, mock_graph_repo):
        """Test creating a document node."""
        mock_graph_repo.create_node.return_value = Mock()
        
        entity_id = builder.create_document_node("doc-123", "Test Document")
        
        assert entity_id == "doc-123"
        mock_graph_repo.create_node.assert_called_once()
    
    def test_link_entities_to_document(self, builder, mock_graph_repo):
        """Test linking entities to document."""
        mock_graph_repo.create_relationship.return_value = Mock()
        
        entity_ids = ["entity-1", "entity-2", "entity-3"]
        builder.link_entities_to_document("doc-123", entity_ids)
        
        assert mock_graph_repo.create_relationship.call_count == 3
    
    def test_entity_to_node_with_string_metadata(self, builder):
        """Test entity conversion with string metadata."""
        entity = Mock()
        entity.entity_id = "entity-123"
        entity.entity_type = "EQUIPMENT"
        entity.normalized_name = "pump-101"
        entity.name = "Pump-101"
        entity.confidence_score = 0.9
        entity.extraction_method = "RULE_BASED"
        entity.entity_metadata = '{"tag": "P-101"}'  # JSON string
        
        node_data = builder._entity_to_node_create(entity)
        
        assert node_data.metadata is not None
        assert isinstance(node_data.metadata, dict)
    
    def test_build_from_document_error_handling(self, builder, mock_mysql_repo):
        """Test error handling during document build."""
        mock_mysql_repo.get_entities_by_document.side_effect = Exception("Database error")
        
        with pytest.raises(GraphBuilderError):
            builder.build_from_document("doc-123")
