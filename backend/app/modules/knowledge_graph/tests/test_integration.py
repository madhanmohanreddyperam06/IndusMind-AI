"""Integration tests for knowledge graph APIs."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import create_app
from app.modules.knowledge_graph.schemas import (
    GraphHealth,
    GraphStatistics,
    NeighborsQuery,
    PathQuery,
    SubgraphQuery,
    EntitySearchQuery,
    SyncRequest
)
from app.modules.knowledge_graph.enums import GraphEntityType


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Mock database session."""
    return Mock()


class TestGraphAPIIntegration:
    """Integration tests for graph API endpoints."""
    
    def test_health_check(self, client):
        """Test graph health check endpoint."""
        with patch('app.modules.knowledge_graph.service.check_neo4j_health', return_value=True):
            response = client.get("/api/v1/graph/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "healthy" in data
            assert "neo4j_connected" in data
    
    def test_health_check_unhealthy(self, client):
        """Test graph health check when unhealthy."""
        with patch('app.modules.knowledge_graph.service.check_neo4j_health', return_value=False):
            response = client.get("/api/v1/graph/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["healthy"] is False
    
    def test_get_statistics(self, client):
        """Test getting graph statistics."""
        mock_stats = {
            "total_nodes": 100,
            "total_relationships": 50,
            "nodes_by_type": {"Equipment": 30, "Component": 20},
            "relationships_by_type": {"HAS_COMPONENT": 25},
            "average_node_degree": 1.0,
            "most_connected_entities": [],
            "largest_component_size": 50
        }
        
        with patch('app.modules.knowledge_graph.repository.GraphRepository.get_graph_statistics', return_value=mock_stats):
            response = client.get("/api/v1/graph/statistics")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_nodes"] == 100
            assert data["total_relationships"] == 50
    
    def test_get_node(self, client):
        """Test getting a node by ID."""
        mock_node = {
            "uuid": "test-uuid",
            "entity_id": "entity-123",
            "entity_type": "Equipment",
            "normalized_name": "pump-101",
            "original_name": "Pump-101",
            "confidence_score": 0.9,
            "extraction_method": "RULE_BASED",
            "metadata": {},
            "created_at": "2024-01-01T00:00:00",
            "updated_at": None
        }
        
        with patch('app.modules.knowledge_graph.repository.GraphRepository.get_node_by_id', return_value=mock_node):
            response = client.get("/api/v1/graph/node/entity-123")
            
            assert response.status_code == 200
            data = response.json()
            assert data["entity_id"] == "entity-123"
    
    def test_get_node_not_found(self, client):
        """Test getting a non-existent node."""
        with patch('app.modules.knowledge_graph.repository.GraphRepository.get_node_by_id', return_value=None):
            response = client.get("/api/v1/graph/node/non-existent")
            
            assert response.status_code == 404
    
    def test_search_nodes(self, client):
        """Test searching for nodes."""
        mock_nodes = [
            {
                "uuid": "test-uuid-1",
                "entity_id": "entity-1",
                "entity_type": "Equipment",
                "normalized_name": "pump-101",
                "original_name": "Pump-101",
                "confidence_score": 0.9,
                "extraction_method": "RULE_BASED",
                "metadata": {},
                "created_at": "2024-01-01T00:00:00",
                "updated_at": None
            }
        ]
        
        with patch('app.modules.knowledge_graph.graph_queries.GraphQueryEngine.search_entities', return_value=mock_nodes):
            query = EntitySearchQuery(name="pump", fuzzy=False)
            response = client.post("/api/v1/graph/search", json=query.model_dump())
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
    
    def test_get_neighbors(self, client):
        """Test getting neighbors of a node."""
        mock_neighbors = [
            {
                "uuid": "neighbor-uuid",
                "entity_id": "neighbor-123",
                "entity_type": "Component",
                "normalized_name": "motor-202",
                "original_name": "Motor-202",
                "confidence_score": 0.85,
                "relationship_type": "HAS_COMPONENT",
                "relationship_confidence": 0.9
            }
        ]
        
        with patch('app.modules.knowledge_graph.repository.GraphRepository.get_neighbors', return_value=mock_neighbors):
            query = NeighborsQuery(entity_id="entity-123", max_depth=1)
            response = client.post("/api/v1/graph/neighbors", json=query.model_dump())
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
    
    def test_find_path(self, client):
        """Test finding path between nodes."""
        mock_path = {
            "nodes": [],
            "relationships": [],
            "length": 0
        }
        
        with patch('app.modules.knowledge_graph.repository.GraphRepository.find_shortest_path', return_value=mock_path):
            query = PathQuery(source_entity_id="source-123", target_entity_id="target-456")
            response = client.post("/api/v1/graph/path", json=query.model_dump())
            
            assert response.status_code == 200
    
    def test_find_path_not_found(self, client):
        """Test finding path when no path exists."""
        with patch('app.modules.knowledge_graph.repository.GraphRepository.find_shortest_path', return_value=None):
            query = PathQuery(source_entity_id="source-123", target_entity_id="target-456")
            response = client.post("/api/v1/graph/path", json=query.model_dump())
            
            assert response.status_code == 404
    
    def test_get_subgraph(self, client):
        """Test getting subgraph."""
        mock_subgraph = {
            "nodes": [],
            "relationships": [],
            "center_node": {
                "uuid": "center-uuid",
                "entity_id": "center-123",
                "entity_type": "Equipment",
                "normalized_name": "pump-101",
                "original_name": "Pump-101",
                "confidence_score": 0.9,
                "extraction_method": "RULE_BASED",
                "metadata": {},
                "created_at": "2024-01-01T00:00:00",
                "updated_at": None
            }
        }
        
        with patch('app.modules.knowledge_graph.repository.GraphRepository.get_subgraph', return_value=mock_subgraph):
            query = SubgraphQuery(entity_id="center-123", radius=2)
            response = client.post("/api/v1/graph/subgraph", json=query.model_dump())
            
            assert response.status_code == 200
    
    def test_sync_document(self, client):
        """Test synchronizing a document."""
        mock_result = {
            "document_id": "doc-123",
            "entities_synced": 5,
            "relationships_synced": 3,
            "nodes_created": 5,
            "nodes_updated": 0,
            "relationships_created": 3,
            "duration_seconds": 1.5,
            "success": True
        }
        
        with patch('app.modules.knowledge_graph.sync.GraphSynchronizationService.sync_document', return_value=mock_result):
            response = client.post("/api/v1/graph/sync/document/doc-123?force_rebuild=false")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["entities_synced"] == 5
    
    def test_sync_all_documents(self, client):
        """Test synchronizing all documents."""
        mock_result = {
            "documents_processed": 3,
            "total_entities": 15,
            "total_relationships": 8,
            "total_nodes_created": 15,
            "total_nodes_updated": 0,
            "total_relationships_created": 8,
            "total_relationships_skipped": 0,
            "duration_seconds": 5.0,
            "success": True,
            "rebuild": False
        }
        
        with patch('app.modules.knowledge_graph.sync.GraphSynchronizationService.sync_all_documents', return_value=mock_result):
            response = client.post("/api/v1/graph/sync/all?force_rebuild=false")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["documents_processed"] == 3
    
    def test_rebuild_graph(self, client):
        """Test rebuilding entire graph."""
        mock_result = {
            "documents_processed": 5,
            "total_entities": 25,
            "total_relationships": 12,
            "total_nodes_created": 25,
            "total_nodes_updated": 0,
            "total_relationships_created": 12,
            "total_relationships_skipped": 0,
            "duration_seconds": 10.0,
            "success": True,
            "rebuild": True
        }
        
        with patch('app.modules.knowledge_graph.sync.GraphSynchronizationService.sync_all_documents', return_value=mock_result):
            response = client.post("/api/v1/graph/rebuild")
            
            assert response.status_code == 200
            data = response.json()
            assert data["rebuild"] is True
    
    def test_get_sync_status(self, client):
        """Test getting sync status for a document."""
        mock_status = {
            "document_id": "doc-123",
            "status": "completed",
            "entities_synced": 5,
            "relationships_synced": 3,
            "error_message": None
        }
        
        with patch('app.modules.knowledge_graph.sync.GraphSynchronizationService.get_sync_status', return_value=mock_status):
            response = client.get("/api/v1/graph/sync/status/doc-123")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"
    
    def test_get_equipment_connections(self, client):
        """Test getting equipment connections."""
        mock_neighbors = [
            {
                "uuid": "neighbor-uuid",
                "entity_id": "neighbor-123",
                "entity_type": "Component",
                "normalized_name": "motor-202",
                "original_name": "Motor-202",
                "confidence_score": 0.85,
                "relationship_type": "HAS_COMPONENT",
                "relationship_confidence": 0.9
            }
        ]
        
        with patch('app.modules.knowledge_graph.graph_queries.GraphQueryEngine.get_equipment_connections', return_value=mock_neighbors):
            response = client.get("/api/v1/graph/equipment/entity-123/connections")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
    
    def test_get_maintenance_history(self, client):
        """Test getting maintenance history."""
        mock_maintenance = [
            {
                "uuid": "maint-uuid",
                "entity_id": "maint-123",
                "entity_type": "MaintenanceActivity",
                "normalized_name": "maintenance-001",
                "original_name": "Maintenance-001",
                "confidence_score": 0.9,
                "extraction_method": "RULE_BASED",
                "metadata": {},
                "created_at": "2024-01-01T00:00:00",
                "updated_at": None
            }
        ]
        
        with patch('app.modules.knowledge_graph.graph_queries.GraphQueryEngine.get_maintenance_history', return_value=mock_maintenance):
            response = client.get("/api/v1/graph/entity/entity-123/maintenance")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
    
    def test_get_failures(self, client):
        """Test getting failures."""
        with patch('app.modules.knowledge_graph.graph_queries.GraphQueryEngine.get_failures', return_value=[]):
            response = client.get("/api/v1/graph/entity/entity-123/failures")
            
            assert response.status_code == 200
    
    def test_get_inspections(self, client):
        """Test getting inspections."""
        with patch('app.modules.knowledge_graph.graph_queries.GraphQueryEngine.get_inspections', return_value=[]):
            response = client.get("/api/v1/graph/entity/entity-123/inspections")
            
            assert response.status_code == 200
    
    def test_get_vendors(self, client):
        """Test getting vendors."""
        with patch('app.modules.knowledge_graph.graph_queries.GraphQueryEngine.get_vendors', return_value=[]):
            response = client.get("/api/v1/graph/entity/entity-123/vendors")
            
            assert response.status_code == 200
    
    def test_get_standards(self, client):
        """Test getting standards."""
        with patch('app.modules.knowledge_graph.graph_queries.GraphQueryEngine.get_standards', return_value=[]):
            response = client.get("/api/v1/graph/entity/entity-123/standards")
            
            assert response.status_code == 200
    
    def test_get_connected_documents(self, client):
        """Test getting connected documents."""
        with patch('app.modules.knowledge_graph.graph_queries.GraphQueryEngine.get_connected_documents', return_value=[]):
            response = client.get("/api/v1/graph/entity/entity-123/documents")
            
            assert response.status_code == 200
    
    def test_get_connected_personnel(self, client):
        """Test getting connected personnel."""
        with patch('app.modules.knowledge_graph.graph_queries.GraphQueryEngine.get_connected_personnel', return_value=[]):
            response = client.get("/api/v1/graph/entity/entity-123/personnel")
            
            assert response.status_code == 200
    
    def test_initialize_graph(self, client):
        """Test initializing graph indexes and constraints."""
        with patch('app.modules.knowledge_graph.repository.GraphRepository.create_indexes_and_constraints'):
            response = client.post("/api/v1/graph/initialize")
            
            assert response.status_code == 200
            data = response.json()
            assert "initialized successfully" in data["message"]
    
    def test_clear_graph(self, client):
        """Test clearing graph."""
        with patch('app.modules.knowledge_graph.repository.GraphRepository._get_session'):
            response = client.delete("/api/v1/graph/clear")
            
            assert response.status_code == 200
            data = response.json()
            assert "cleared successfully" in data["message"]
    
    def test_get_nodes_by_type(self, client):
        """Test getting nodes by type."""
        mock_nodes = [
            {
                "uuid": "node-uuid",
                "entity_id": "entity-123",
                "entity_type": "Equipment",
                "normalized_name": "pump-101",
                "original_name": "Pump-101",
                "confidence_score": 0.9,
                "extraction_method": "RULE_BASED",
                "metadata": {},
                "created_at": "2024-01-01T00:00:00",
                "updated_at": None
            }
        ]
        
        with patch('app.modules.knowledge_graph.graph_queries.GraphQueryEngine.get_entity_by_type', return_value=mock_nodes):
            response = client.get("/api/v1/graph/nodes/Equipment?limit=10")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
