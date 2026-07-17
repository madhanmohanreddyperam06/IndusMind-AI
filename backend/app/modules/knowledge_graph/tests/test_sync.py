"""Unit tests for graph synchronization service."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from app.modules.knowledge_graph.sync import GraphSynchronizationService
from app.modules.knowledge_graph.schemas import SyncResult, SyncStatus
from app.modules.knowledge_graph.exceptions import GraphSynchronizationError


@pytest.fixture
def mock_mysql_db():
    """Mock MySQL database session."""
    db = Mock()
    return db


@pytest.fixture
def mock_builder():
    """Mock graph builder."""
    builder = Mock()
    return builder


@pytest.fixture
def sync_service(mock_mysql_db, mock_builder):
    """Create synchronization service with mocked dependencies."""
    with patch('app.modules.knowledge_graph.sync.GraphBuilder', return_value=mock_builder):
        return GraphSynchronizationService(mock_mysql_db)


class TestGraphSynchronizationService:
    """Test cases for GraphSynchronizationService."""
    
    def test_sync_document_success(self, sync_service, mock_builder):
        """Test successful document synchronization."""
        mock_builder.build_from_document.return_value = {
            "document_id": "doc-123",
            "entities_processed": 5,
            "relationships_processed": 3,
            "nodes_created": 5,
            "nodes_updated": 0,
            "relationships_created": 3,
            "relationships_skipped": 0
        }
        
        result = sync_service.sync_document("doc-123", force_rebuild=False)
        
        assert result.success is True
        assert result.document_id == "doc-123"
        assert result.entities_synced == 5
        assert result.relationships_synced == 3
        assert result.nodes_created == 5
        assert result.relationships_created == 3
    
    def test_sync_document_with_force_rebuild(self, sync_service, mock_builder):
        """Test document synchronization with force rebuild."""
        mock_builder.build_from_document.return_value = {
            "document_id": "doc-123",
            "entities_processed": 5,
            "relationships_processed": 3,
            "nodes_created": 5,
            "nodes_updated": 0,
            "relationships_created": 3,
            "relationships_skipped": 0
        }
        
        result = sync_service.sync_document("doc-123", force_rebuild=True)
        
        assert result.success is True
        mock_builder.build_from_document.assert_called_once()
    
    def test_sync_document_error(self, sync_service, mock_builder):
        """Test document synchronization with error."""
        mock_builder.build_from_document.side_effect = Exception("Build failed")
        
        result = sync_service.sync_document("doc-123", force_rebuild=False)
        
        assert result.success is False
        assert result.error_message == "Build failed"
        assert result.entities_synced == 0
    
    def test_sync_all_documents_incremental(self, sync_service, mock_builder):
        """Test syncing all documents incrementally."""
        mock_builder.build_from_all_documents.return_value = {
            "documents_processed": 3,
            "total_entities": 15,
            "total_relationships": 8,
            "total_nodes_created": 10,
            "total_nodes_updated": 5,
            "total_relationships_created": 8,
            "total_relationships_skipped": 0
        }
        
        result = sync_service.sync_all_documents(force_rebuild=False)
        
        assert result["success"] is True
        assert result["documents_processed"] == 3
        assert result["total_entities"] == 15
        assert result["rebuild"] is False
    
    def test_sync_all_documents_with_rebuild(self, sync_service, mock_builder):
        """Test syncing all documents with full rebuild."""
        mock_builder.rebuild_graph.return_value = {
            "documents_processed": 3,
            "total_entities": 15,
            "total_relationships": 8,
            "total_nodes_created": 15,
            "total_nodes_updated": 0,
            "total_relationships_created": 8,
            "total_relationships_skipped": 0,
            "rebuild": True
        }
        
        result = sync_service.sync_all_documents(force_rebuild=True)
        
        assert result["success"] is True
        assert result["rebuild"] is True
        mock_builder.rebuild_graph.assert_called_once()
    
    def test_sync_all_documents_error(self, sync_service, mock_builder):
        """Test syncing all documents with error."""
        mock_builder.build_from_all_documents.side_effect = Exception("Sync failed")
        
        result = sync_service.sync_all_documents(force_rebuild=False)
        
        assert result["success"] is False
        assert result["error_message"] == "Sync failed"
    
    def test_incremental_sync(self, sync_service, mock_builder):
        """Test incremental synchronization."""
        mock_builder.build_from_document.return_value = {
            "document_id": "doc-123",
            "entities_processed": 2,
            "relationships_processed": 1,
            "nodes_created": 1,
            "nodes_updated": 1,
            "relationships_created": 1,
            "relationships_skipped": 0
        }
        
        result = sync_service.incremental_sync("doc-123")
        
        assert result.success is True
        assert result.nodes_created == 1
        assert result.nodes_updated == 1
    
    def test_get_sync_status_pending(self, sync_service):
        """Test getting sync status for pending document."""
        with patch('app.modules.knowledge_graph.sync.KnowledgeExtractionRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo.get_entities_by_document.return_value = []
            mock_repo.get_relationships_by_document.return_value = []
            mock_repo_class.return_value = mock_repo
            
            with patch('app.modules.knowledge_graph.sync.GraphRepository') as mock_graph_repo_class:
                mock_graph_repo = Mock()
                mock_graph_repo.get_node_by_id.return_value = None
                mock_graph_repo_class.return_value = mock_graph_repo
                
                status = sync_service.get_sync_status("doc-123")
                
                assert status.status == "pending"
                assert status.entities_synced == 0
                assert status.relationships_synced == 0
    
    def test_get_sync_status_completed(self, sync_service):
        """Test getting sync status for completed document."""
        with patch('app.modules.knowledge_graph.sync.KnowledgeExtractionRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_entity = Mock()
            mock_entity.entity_id = "entity-1"
            mock_relationship = Mock()
            mock_relationship.relationship_id = "rel-1"
            mock_repo.get_entities_by_document.return_value = [mock_entity]
            mock_repo.get_relationships_by_document.return_value = [mock_relationship]
            mock_repo_class.return_value = mock_repo
            
            with patch('app.modules.knowledge_graph.sync.GraphRepository') as mock_graph_repo_class:
                mock_graph_repo = Mock()
                mock_graph_repo.get_node_by_id.return_value = Mock()  # Node exists
                mock_graph_repo.get_relationship_by_id.return_value = Mock()  # Relationship exists
                mock_graph_repo_class.return_value = mock_graph_repo
                
                status = sync_service.get_sync_status("doc-123")
                
                assert status.status == "completed"
                assert status.entities_synced == 1
                assert status.relationships_synced == 1
    
    def test_get_sync_status_in_progress(self, sync_service):
        """Test getting sync status for partially synced document."""
        with patch('app.modules.knowledge_graph.sync.KnowledgeExtractionRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_entity1 = Mock()
            mock_entity1.entity_id = "entity-1"
            mock_entity2 = Mock()
            mock_entity2.entity_id = "entity-2"
            mock_relationship = Mock()
            mock_relationship.relationship_id = "rel-1"
            mock_repo.get_entities_by_document.return_value = [mock_entity1, mock_entity2]
            mock_repo.get_relationships_by_document.return_value = [mock_relationship]
            mock_repo_class.return_value = mock_repo
            
            with patch('app.modules.knowledge_graph.sync.GraphRepository') as mock_graph_repo_class:
                mock_graph_repo = Mock()
                # Only first entity synced
                mock_graph_repo.get_node_by_id.side_effect = [Mock(), None]
                mock_graph_repo.get_relationship_by_id.return_value = Mock()
                mock_graph_repo_class.return_value = mock_graph_repo
                
                status = sync_service.get_sync_status("doc-123")
                
                assert status.status == "in_progress"
                assert status.entities_synced == 1
    
    def test_get_sync_status_error(self, sync_service):
        """Test getting sync status with error."""
        with patch('app.modules.knowledge_graph.sync.KnowledgeExtractionRepository') as mock_repo_class:
            mock_repo_class.return_value.get_entities_by_document.side_effect = Exception("DB error")
            
            status = sync_service.get_sync_status("doc-123")
            
            assert status.status == "failed"
            assert status.error_message == "DB error"
    
    def test_retry_failed_sync_success(self, sync_service, mock_builder):
        """Test retrying failed synchronization successfully."""
        mock_builder.build_from_document.return_value = {
            "document_id": "doc-123",
            "entities_processed": 5,
            "relationships_processed": 3,
            "nodes_created": 5,
            "nodes_updated": 0,
            "relationships_created": 3,
            "relationships_skipped": 0
        }
        
        result = sync_service.retry_failed_sync("doc-123", max_retries=3)
        
        assert result.success is True
        assert result.entities_synced == 5
    
    def test_retry_failed_sync_all_retries_failed(self, sync_service, mock_builder):
        """Test retrying failed synchronization when all retries fail."""
        mock_builder.build_from_document.side_effect = Exception("Build failed")
        
        result = sync_service.retry_failed_sync("doc-123", max_retries=2)
        
        assert result.success is False
        assert "Failed after 2 retry attempts" in result.error_message
    
    def test_delete_document_data(self, sync_service):
        """Test deleting document data from graph."""
        with patch('app.modules.knowledge_graph.sync.GraphRepository') as mock_graph_repo_class:
            mock_graph_repo = Mock()
            mock_graph_repo.delete_node.return_value = True
            mock_graph_repo_class.return_value = mock_graph_repo
            
            with patch('app.modules.knowledge_graph.sync.KnowledgeExtractionRepository') as mock_repo_class:
                mock_repo = Mock()
                mock_entity = Mock()
                mock_entity.entity_id = "entity-1"
                mock_repo.get_entities_by_document.return_value = [mock_entity]
                mock_repo_class.return_value = mock_repo
                
                sync_service._delete_document_data("doc-123")
                
                assert mock_graph_repo.delete_node.call_count >= 1  # At least entity and document node deleted
