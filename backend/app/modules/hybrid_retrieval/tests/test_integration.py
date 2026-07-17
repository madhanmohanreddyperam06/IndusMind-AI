"""Integration tests for hybrid retrieval APIs."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import create_app
from app.modules.hybrid_retrieval.schemas import (
    RetrievalRequest,
    ContextRequest,
    QueryAnalysisRequest,
    QueryExpansionRequest,
    RetrievalConfig,
    RankingMethod
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


class TestHybridRetrievalAPIIntegration:
    """Integration tests for hybrid retrieval API endpoints."""
    
    def test_query_endpoint(self, client):
        """Test hybrid retrieval query endpoint."""
        with patch('app.modules.hybrid_retrieval.service.QueryAnalyzer') as mock_analyzer, \
             patch('app.modules.hybrid_retrieval.service.QueryExpander') as mock_expander, \
             patch('app.modules.hybrid_retrieval.service.VectorRetriever') as mock_vector, \
             patch('app.modules.hybrid_retrieval.service.GraphRetriever') as mock_graph, \
             patch('app.modules.hybrid_retrieval.service.BM25Retriever') as mock_keyword, \
             patch('app.modules.hybrid_retrieval.service.MetadataRetriever') as mock_metadata:
            
            # Mock query analysis
            mock_analyzer_instance = Mock()
            mock_analyzer_instance.analyze.return_value = Mock(
                analysis=Mock(
                    original_query="test query",
                    question_type="general",
                    intent="information",
                    detected_entities=[],
                    detected_equipment=[],
                    detected_components=[],
                    detected_activities=[],
                    detected_dates=[],
                    detected_regulations=[],
                    detected_standards=[],
                    detected_departments=[],
                    keywords=["test"],
                    confidence=0.8,
                    analysis_time_ms=10.0
                )
            )
            mock_analyzer.return_value = mock_analyzer_instance
            
            # Mock query expansion
            mock_expander_instance = Mock()
            mock_expander_instance.expand.return_value = Mock(
                expansion=Mock(
                    original_query="test query",
                    expanded_query="test query expanded",
                    expanded_terms=[],
                    expansion_strategy="related",
                    expansion_time_ms=5.0
                )
            )
            mock_expander.return_value = mock_expander_instance
            
            # Mock vector retriever
            mock_vector_instance = Mock()
            mock_vector_instance.retrieve.return_value = Mock(
                source="vector",
                evidence_items=[],
                total_count=0,
                retrieval_time_ms=100.0,
                status="completed",
                error_message=None
            )
            mock_vector.return_value = mock_vector_instance
            
            # Mock graph retriever
            mock_graph_instance = Mock()
            mock_graph_instance.retrieve.return_value = Mock(
                source="graph",
                evidence_items=[],
                total_count=0,
                retrieval_time_ms=50.0,
                status="completed",
                error_message=None
            )
            mock_graph.return_value = mock_graph_instance
            
            # Mock keyword retriever
            mock_keyword_instance = Mock()
            mock_keyword_instance.retrieve.return_value = Mock(
                source="keyword",
                evidence_items=[],
                total_count=0,
                retrieval_time_ms=30.0,
                status="completed",
                error_message=None
            )
            mock_keyword.return_value = mock_keyword_instance
            
            # Mock metadata retriever
            mock_metadata_instance = Mock()
            mock_metadata_instance.retrieve.return_value = Mock(
                source="metadata",
                evidence_items=[],
                total_count=0,
                retrieval_time_ms=20.0,
                status="completed",
                error_message=None
            )
            mock_metadata.return_value = mock_metadata_instance
            
            response = client.post(
                "/api/v1/retrieval/query",
                json={"query": "test query"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "query" in data
            assert "success" in data
    
    def test_context_endpoint(self, client):
        """Test context generation endpoint."""
        with patch('app.modules.hybrid_retrieval.service.HybridRetrievalService.query') as mock_query:
            mock_query.return_value = Mock(
                query="test query",
                query_analysis=None,
                query_expansion=None,
                evidence_sets=[],
                merged_evidence=[],
                total_retrieval_time_ms=200.0,
                ranking_time_ms=15.0,
                deduplication_time_ms=5.0,
                status="completed",
                success=True,
                error_message=None
            )
            
            response = client.post(
                "/api/v1/retrieval/context",
                json={"query": "test query"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "context_package" in data
            assert "success" in data
    
    def test_analyze_endpoint(self, client):
        """Test query analysis endpoint."""
        with patch('app.modules.hybrid_retrieval.service.QueryAnalyzer') as mock_analyzer:
            mock_analyzer_instance = Mock()
            mock_analyzer_instance.analyze.return_value = Mock(
                analysis=Mock(
                    original_query="test query",
                    question_type="general",
                    intent="information",
                    detected_entities=[],
                    detected_equipment=[],
                    detected_components=[],
                    detected_activities=[],
                    detected_dates=[],
                    detected_regulations=[],
                    detected_standards=[],
                    detected_departments=[],
                    keywords=["test"],
                    confidence=0.8,
                    analysis_time_ms=10.0
                ),
                success=True
            )
            mock_analyzer.return_value = mock_analyzer_instance
            
            response = client.post(
                "/api/v1/retrieval/analyze",
                json={"query": "test query"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "analysis" in data
            assert data["success"] is True
    
    def test_expand_endpoint(self, client):
        """Test query expansion endpoint."""
        with patch('app.modules.hybrid_retrieval.service.QueryExpander') as mock_expander:
            mock_expander_instance = Mock()
            mock_expander_instance.expand.return_value = Mock(
                expansion=Mock(
                    original_query="test query",
                    expanded_query="test query expanded",
                    expanded_terms=[],
                    expansion_strategy="related",
                    expansion_time_ms=5.0
                ),
                success=True
            )
            mock_expander.return_value = mock_expander_instance
            
            response = client.post(
                "/api/v1/retrieval/expand",
                json={"query": "test query"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "expansion" in data
            assert data["success"] is True
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint."""
        with patch('app.config.qdrant.check_qdrant_health', return_value=True), \
             patch('app.config.neo4j.check_neo4j_health', return_value=True):
            
            response = client.get("/api/v1/retrieval/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "healthy" in data
            assert "vector_retrieval_healthy" in data
            assert "graph_retrieval_healthy" in data
    
    def test_statistics_endpoint(self, client):
        """Test statistics endpoint."""
        with patch('app.modules.hybrid_retrieval.service.HybridRetrievalService') as mock_service:
            mock_instance = Mock()
            mock_instance.get_statistics.return_value = {
                "total_queries": 100,
                "successful_queries": 95,
                "failed_queries": 5,
                "average_retrieval_time_ms": 500.0,
                "average_context_size_tokens": 2000,
                "source_usage": {"vector": 80, "graph": 60, "keyword": 40, "metadata": 30}
            }
            mock_service.return_value = mock_instance
            
            response = client.get("/api/v1/retrieval/statistics")
            
            assert response.status_code == 200
            data = response.json()
            assert "total_queries" in data
            assert data["total_queries"] == 100
    
    def test_config_endpoint(self, client):
        """Test configuration endpoint."""
        response = client.get("/api/v1/retrieval/config")
        
        assert response.status_code == 200
        data = response.json()
        assert "default_config" in data
        assert "ranking_weights" in data
        assert "available_sources" in data
    
    def test_test_endpoint(self, client):
        """Test retrieval test endpoint."""
        with patch('app.modules.hybrid_retrieval.service.HybridRetrievalService.query') as mock_query:
            mock_query.return_value = Mock(
                query="test query",
                query_analysis=None,
                query_expansion=None,
                evidence_sets=[],
                merged_evidence=[],
                total_retrieval_time_ms=200.0,
                ranking_time_ms=15.0,
                deduplication_time_ms=5.0,
                status="completed",
                success=True,
                error_message=None
            )
            
            response = client.post(
                "/api/v1/retrieval/test",
                json={"query": "test query"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "query" in data
            assert "source_results" in data
    
    def test_debug_endpoint(self, client):
        """Test debug endpoint."""
        with patch('app.modules.hybrid_retrieval.service.QueryAnalyzer') as mock_analyzer, \
             patch('app.modules.hybrid_retrieval.service.QueryExpander') as mock_expander, \
             patch('app.modules.hybrid_retrieval.service.HybridRetrievalService.query') as mock_query:
            
            mock_analyzer_instance = Mock()
            mock_analyzer_instance.analyze.return_value = Mock(
                analysis=Mock(
                    original_query="test query",
                    question_type="general",
                    intent="information",
                    detected_entities=[],
                    detected_equipment=[],
                    detected_components=[],
                    detected_activities=[],
                    detected_dates=[],
                    detected_regulations=[],
                    detected_standards=[],
                    detected_departments=[],
                    keywords=["test"],
                    confidence=0.8,
                    analysis_time_ms=10.0
                ),
                success=True
            )
            mock_analyzer.return_value = mock_analyzer_instance
            
            mock_expander_instance = Mock()
            mock_expander_instance.expand.return_value = Mock(
                expansion=Mock(
                    original_query="test query",
                    expanded_query="test query expanded",
                    expanded_terms=[],
                    expansion_strategy="related",
                    expansion_time_ms=5.0
                ),
                success=True
            )
            mock_expander.return_value = mock_expander_instance
            
            mock_query.return_value = Mock(
                query="test query",
                query_analysis=None,
                query_expansion=None,
                evidence_sets=[],
                merged_evidence=[],
                total_retrieval_time_ms=200.0,
                ranking_time_ms=15.0,
                deduplication_time_ms=5.0,
                status="completed",
                success=True,
                error_message=None
            )
            
            response = client.post(
                "/api/v1/retrieval/debug",
                json={"query": "test query", "include_intermediate": True}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "query" in data
            assert "retrieval_steps" in data
    
    def test_query_with_config(self, client):
        """Test query with custom configuration."""
        with patch('app.modules.hybrid_retrieval.service.QueryAnalyzer') as mock_analyzer, \
             patch('app.modules.hybrid_retrieval.service.QueryExpander') as mock_expander, \
             patch('app.modules.hybrid_retrieval.service.VectorRetriever') as mock_vector:
            
            mock_analyzer_instance = Mock()
            mock_analyzer_instance.analyze.return_value = Mock(
                analysis=Mock(
                    original_query="test query",
                    question_type="general",
                    intent="information",
                    detected_entities=[],
                    detected_equipment=[],
                    detected_components=[],
                    detected_activities=[],
                    detected_dates=[],
                    detected_regulations=[],
                    detected_standards=[],
                    detected_departments=[],
                    keywords=["test"],
                    confidence=0.8,
                    analysis_time_ms=10.0
                )
            )
            mock_analyzer.return_value = mock_analyzer_instance
            
            mock_expander_instance = Mock()
            mock_expander_instance.expand.return_value = Mock(
                expansion=Mock(
                    original_query="test query",
                    expanded_query="test query expanded",
                    expanded_terms=[],
                    expansion_strategy="related",
                    expansion_time_ms=5.0
                )
            )
            mock_expander.return_value = mock_expander_instance
            
            mock_vector_instance = Mock()
            mock_vector_instance.retrieve.return_value = Mock(
                source="vector",
                evidence_items=[],
                total_count=0,
                retrieval_time_ms=100.0,
                status="completed",
                error_message=None
            )
            mock_vector.return_value = mock_vector_instance
            
            response = client.post(
                "/api/v1/retrieval/query",
                json={
                    "query": "test query",
                    "config": {
                        "vector_top_k": 20,
                        "vector_score_threshold": 0.8,
                        "ranking_method": "weighted_score"
                    }
                }
            )
            
            assert response.status_code == 200
    
    def test_query_skip_analysis(self, client):
        """Test query with skip analysis."""
        with patch('app.modules.hybrid_retrieval.service.QueryExpander') as mock_expander, \
             patch('app.modules.hybrid_retrieval.service.VectorRetriever') as mock_vector:
            
            mock_expander_instance = Mock()
            mock_expander_instance.expand.return_value = Mock(
                expansion=Mock(
                    original_query="test query",
                    expanded_query="test query",
                    expanded_terms=[],
                    expansion_strategy="related",
                    expansion_time_ms=5.0
                )
            )
            mock_expander.return_value = mock_expander_instance
            
            mock_vector_instance = Mock()
            mock_vector_instance.retrieve.return_value = Mock(
                source="vector",
                evidence_items=[],
                total_count=0,
                retrieval_time_ms=100.0,
                status="completed",
                error_message=None
            )
            mock_vector.return_value = mock_vector_instance
            
            response = client.post(
                "/api/v1/retrieval/query",
                json={"query": "test query", "skip_analysis": True}
            )
            
            assert response.status_code == 200
    
    def test_query_skip_expansion(self, client):
        """Test query with skip expansion."""
        with patch('app.modules.hybrid_retrieval.service.QueryAnalyzer') as mock_analyzer, \
             patch('app.modules.hybrid_retrieval.service.VectorRetriever') as mock_vector:
            
            mock_analyzer_instance = Mock()
            mock_analyzer_instance.analyze.return_value = Mock(
                analysis=Mock(
                    original_query="test query",
                    question_type="general",
                    intent="information",
                    detected_entities=[],
                    detected_equipment=[],
                    detected_components=[],
                    detected_activities=[],
                    detected_dates=[],
                    detected_regulations=[],
                    detected_standards=[],
                    detected_departments=[],
                    keywords=["test"],
                    confidence=0.8,
                    analysis_time_ms=10.0
                )
            )
            mock_analyzer.return_value = mock_analyzer_instance
            
            mock_vector_instance = Mock()
            mock_vector_instance.retrieve.return_value = Mock(
                source="vector",
                evidence_items=[],
                total_count=0,
                retrieval_time_ms=100.0,
                status="completed",
                error_message=None
            )
            mock_vector.return_value = mock_vector_instance
            
            response = client.post(
                "/api/v1/retrieval/query",
                json={"query": "test query", "skip_expansion": True}
            )
            
            assert response.status_code == 200
