"""Unit tests for context builder."""

import pytest
from datetime import datetime
from app.modules.hybrid_retrieval.context_builder import ContextBuilder
from app.modules.hybrid_retrieval.schemas import (
    EvidenceItem,
    QueryAnalysis,
    QueryExpansion,
    ContextPackageStatus
)
from app.modules.hybrid_retrieval.enums import EvidenceSource, EvidenceType, QuestionType, IntentType
from app.modules.hybrid_retrieval.exceptions import ContextBuildException


class TestContextBuilder:
    """Test cases for ContextBuilder."""
    
    def test_initialization(self):
        """Test builder initialization."""
        builder = ContextBuilder()
        assert builder is not None
    
    def test_build_context_package(self):
        """Test building a context package."""
        builder = ContextBuilder()
        
        query_analysis = QueryAnalysis(
            original_query="Test query",
            question_type=QuestionType.GENERAL,
            intent=IntentType.INFORMATION,
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
        
        query_expansion = QueryExpansion(
            original_query="Test query",
            expanded_query="Test query expanded",
            expanded_terms=[],
            expansion_strategy="related",
            expansion_time_ms=5.0
        )
        
        evidence_items = [
            EvidenceItem(
                evidence_id="1",
                evidence_type=EvidenceType.CHUNK,
                source=EvidenceSource.VECTOR,
                score=0.9,
                confidence=0.8,
                content="Test content",
                chunk_text="Test content",
                document_id="doc-1",
                chunk_id="chunk-1",
                metadata={}
            )
        ]
        
        retrieval_times = {
            'query_analysis': 10.0,
            'query_expansion': 5.0,
            'vector': 100.0,
            'graph': 50.0,
            'keyword': 30.0,
            'metadata': 20.0,
            'ranking': 15.0,
            'deduplication': 5.0
        }
        
        context_package = builder.build(
            question="Test query",
            query_analysis=query_analysis,
            query_expansion=query_expansion,
            evidence_items=evidence_items,
            retrieval_times=retrieval_times
        )
        
        assert context_package.question == "Test query"
        assert context_package.expanded_query == "Test query expanded"
        assert len(context_package.relevant_chunks) == 1
        assert context_package.status == ContextPackageStatus.SUCCESS
    
    def test_build_with_empty_evidence(self):
        """Test building context with no evidence."""
        builder = ContextBuilder()
        
        query_analysis = QueryAnalysis(
            original_query="Test query",
            question_type=QuestionType.GENERAL,
            intent=IntentType.INFORMATION,
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
        
        retrieval_times = {}
        
        context_package = builder.build(
            question="Test query",
            query_analysis=query_analysis,
            query_expansion=None,
            evidence_items=[],
            retrieval_times=retrieval_times
        )
        
        assert context_package.status == ContextPackageStatus.FAILED
        assert len(context_package.relevant_chunks) == 0
    
    def test_extract_chunks(self):
        """Test chunk extraction."""
        builder = ContextBuilder()
        
        evidence_items = [
            EvidenceItem(
                evidence_id="1",
                evidence_type=EvidenceType.CHUNK,
                source=EvidenceSource.VECTOR,
                score=0.9,
                confidence=0.8,
                content="Test chunk",
                chunk_text="Test chunk",
                document_id="doc-1",
                chunk_id="chunk-1",
                metadata={}
            ),
            EvidenceItem(
                evidence_id="2",
                evidence_type=EvidenceType.ENTITY,
                source=EvidenceSource.GRAPH,
                score=0.8,
                confidence=0.7,
                content="Test entity",
                chunk_text=None,
                document_id=None,
                chunk_id=None,
                entity_id="entity-1",
                metadata={}
            )
        ]
        
        chunks = builder._extract_chunks(evidence_items)
        
        assert len(chunks) == 1
        assert chunks[0].evidence_type == EvidenceType.CHUNK
    
    def test_extract_entities(self):
        """Test entity extraction."""
        builder = ContextBuilder()
        
        evidence_items = [
            EvidenceItem(
                evidence_id="1",
                evidence_type=EvidenceType.ENTITY,
                source=EvidenceSource.GRAPH,
                score=0.8,
                confidence=0.7,
                content="Pump",
                chunk_text=None,
                document_id=None,
                chunk_id=None,
                entity_id="entity-1",
                graph_node_id="entity-1",
                metadata={'entity_type': 'Equipment', 'normalized_name': 'Pump'}
            )
        ]
        
        entities = builder._extract_entities(evidence_items)
        
        assert len(entities) == 1
        assert entities[0].entity_id == "entity-1"
        assert entities[0].entity_type == "Equipment"
    
    def test_extract_relationships(self):
        """Test relationship extraction."""
        builder = ContextBuilder()
        
        evidence_items = [
            EvidenceItem(
                evidence_id="1",
                evidence_type=EvidenceType.RELATIONSHIP,
                source=EvidenceSource.GRAPH,
                score=0.8,
                confidence=0.7,
                content="Entity1 -> Entity2",
                chunk_text=None,
                document_id=None,
                chunk_id=None,
                relationship_id="rel-1",
                metadata={
                    'relationship_type': 'CONNECTED_TO',
                    'source_entity_id': 'entity-1',
                    'target_entity_id': 'entity-2'
                }
            )
        ]
        
        relationships = builder._extract_relationships(evidence_items)
        
        assert len(relationships) == 1
        assert relationships[0].relationship_id == "rel-1"
        assert relationships[0].relationship_type == "CONNECTED_TO"
    
    def test_build_document_references(self):
        """Test document reference building."""
        builder = ContextBuilder()
        
        chunks = [
            EvidenceItem(
                evidence_id="1",
                evidence_type=EvidenceType.CHUNK,
                source=EvidenceSource.VECTOR,
                score=0.9,
                confidence=0.8,
                content="Test chunk 1",
                chunk_text="Test chunk 1",
                document_id="doc-1",
                chunk_id="chunk-1",
                metadata={'document_title': 'Document 1', 'document_type': 'manual'}
            ),
            EvidenceItem(
                evidence_id="2",
                evidence_type=EvidenceType.CHUNK,
                source=EvidenceSource.VECTOR,
                score=0.8,
                confidence=0.7,
                content="Test chunk 2",
                chunk_text="Test chunk 2",
                document_id="doc-1",
                chunk_id="chunk-2",
                metadata={'document_title': 'Document 1', 'document_type': 'manual'}
            )
        ]
        
        doc_refs = builder._build_document_references(chunks)
        
        assert len(doc_refs) == 1
        assert doc_refs[0].document_id == "doc-1"
        assert doc_refs[0].chunk_count == 2
    
    def test_calculate_confidence_metrics(self):
        """Test confidence metrics calculation."""
        builder = ContextBuilder()
        
        evidence_items = [
            EvidenceItem(
                evidence_id="1",
                evidence_type=EvidenceType.CHUNK,
                source=EvidenceSource.VECTOR,
                score=0.9,
                confidence=0.8,
                content="Test",
                chunk_text="Test",
                document_id="doc-1",
                chunk_id="chunk-1",
                metadata={}
            ),
            EvidenceItem(
                evidence_id="2",
                evidence_type=EvidenceType.CHUNK,
                source=EvidenceSource.GRAPH,
                score=0.7,
                confidence=0.6,
                content="Test",
                chunk_text="Test",
                document_id="doc-2",
                chunk_id="chunk-2",
                metadata={}
            )
        ]
        
        confidence = builder._calculate_confidence_metrics(evidence_items)
        
        assert confidence.overall_confidence > 0
        assert confidence.overall_confidence <= 1
        assert confidence.vector_confidence > 0
        assert confidence.graph_confidence > 0
    
    def test_estimate_token_count(self):
        """Test token count estimation."""
        builder = ContextBuilder()
        
        evidence_items = [
            EvidenceItem(
                evidence_id="1",
                evidence_type=EvidenceType.CHUNK,
                source=EvidenceSource.VECTOR,
                score=0.9,
                confidence=0.8,
                content="This is a test content with approximately 100 characters to estimate token count.",
                chunk_text="This is a test content with approximately 100 characters to estimate token count.",
                document_id="doc-1",
                chunk_id="chunk-1",
                metadata={}
            )
        ]
        
        token_count = builder._estimate_token_count(evidence_items)
        
        assert token_count > 0
        assert token_count < 100  # Should be roughly characters / 4
    
    def test_build_metadata_summary(self):
        """Test metadata summary building."""
        builder = ContextBuilder()
        
        evidence_items = [
            EvidenceItem(
                evidence_id="1",
                evidence_type=EvidenceType.CHUNK,
                source=EvidenceSource.VECTOR,
                score=0.9,
                confidence=0.8,
                content="Test",
                chunk_text="Test",
                document_id="doc-1",
                chunk_id="chunk-1",
                metadata={'document_type': 'manual', 'entity_type': 'Equipment'}
            )
        ]
        
        summary = builder._build_metadata_summary(evidence_items)
        
        assert 'document_types' in summary
        assert 'entity_types' in summary
        assert 'sources' in summary
        assert 'average_confidence' in summary
    
    def test_determine_status_success(self):
        """Test status determination for success."""
        builder = ContextBuilder()
        
        evidence_items = [
            EvidenceItem(
                evidence_id="1",
                evidence_type=EvidenceType.CHUNK,
                source=EvidenceSource.VECTOR,
                score=0.9,
                confidence=0.8,
                content="Test",
                chunk_text="Test",
                document_id="doc-1",
                chunk_id="chunk-1",
                metadata={}
            )
        ]
        
        from app.modules.hybrid_retrieval.schemas import RetrievalStatistics
        stats = RetrievalStatistics(
            total_retrieval_time_ms=1000,
            query_analysis_time_ms=10,
            query_expansion_time_ms=5,
            vector_retrieval_time_ms=100,
            graph_retrieval_time_ms=50,
            keyword_retrieval_time_ms=30,
            metadata_retrieval_time_ms=20,
            ranking_time_ms=15,
            deduplication_time_ms=5,
            context_build_time_ms=10,
            total_chunks=1,
            total_entities=0,
            total_relationships=0,
            total_graph_nodes=0,
            total_evidence_items=1,
            source_distribution={'vector': 1},
            context_size_tokens=100
        )
        
        status = builder._determine_status(evidence_items, stats)
        
        assert status == ContextPackageStatus.SUCCESS
    
    def test_determine_status_failed(self):
        """Test status determination for failure."""
        builder = ContextBuilder()
        
        from app.modules.hybrid_retrieval.schemas import RetrievalStatistics
        stats = RetrievalStatistics(
            total_retrieval_time_ms=1000,
            query_analysis_time_ms=10,
            query_expansion_time_ms=5,
            vector_retrieval_time_ms=100,
            graph_retrieval_time_ms=50,
            keyword_retrieval_time_ms=30,
            metadata_retrieval_time_ms=20,
            ranking_time_ms=15,
            deduplication_time_ms=5,
            context_build_time_ms=10,
            total_chunks=0,
            total_entities=0,
            total_relationships=0,
            total_graph_nodes=0,
            total_evidence_items=0,
            source_distribution={},
            context_size_tokens=0
        )
        
        status = builder._determine_status([], stats)
        
        assert status == ContextPackageStatus.FAILED
