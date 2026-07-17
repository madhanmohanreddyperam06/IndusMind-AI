"""Unit tests for ranking engine."""

import pytest
from app.modules.hybrid_retrieval.ranking_engine import RankingEngine
from app.modules.hybrid_retrieval.schemas import EvidenceItem
from app.modules.hybrid_retrieval.enums import EvidenceSource, EvidenceType, RankingMethod
from app.modules.hybrid_retrieval.exceptions import RankingException


class TestRankingEngine:
    """Test cases for RankingEngine."""
    
    def test_initialization(self):
        """Test engine initialization."""
        engine = RankingEngine()
        assert engine is not None
        assert engine.default_weights is not None
    
    def test_rank_weighted_score(self):
        """Test weighted score ranking."""
        engine = RankingEngine()
        
        evidence_items = [
            EvidenceItem(
                evidence_id="1",
                evidence_type=EvidenceType.CHUNK,
                source=EvidenceSource.VECTOR,
                score=0.9,
                confidence=0.8,
                content="Test content 1",
                chunk_text="Test content 1",
                document_id="doc-1",
                chunk_id="chunk-1",
                metadata={}
            ),
            EvidenceItem(
                evidence_id="2",
                evidence_type=EvidenceType.CHUNK,
                source=EvidenceSource.KEYWORD,
                score=0.7,
                confidence=0.6,
                content="Test content 2",
                chunk_text="Test content 2",
                document_id="doc-2",
                chunk_id="chunk-2",
                metadata={}
            )
        ]
        
        ranked = engine.rank(evidence_items, RankingMethod.WEIGHTED_SCORE)
        
        assert len(ranked) == 2
        assert ranked[0].score >= ranked[1].score
        assert ranked[0].ranking_position == 1
        assert ranked[1].ranking_position == 2
    
    def test_rank_rrf(self):
        """Test Reciprocal Rank Fusion ranking."""
        engine = RankingEngine()
        
        evidence_items = [
            EvidenceItem(
                evidence_id="1",
                evidence_type=EvidenceType.CHUNK,
                source=EvidenceSource.VECTOR,
                score=0.9,
                confidence=0.8,
                content="Test content 1",
                chunk_text="Test content 1",
                document_id="doc-1",
                chunk_id="chunk-1",
                metadata={}
            ),
            EvidenceItem(
                evidence_id="2",
                evidence_type=EvidenceType.CHUNK,
                source=EvidenceSource.GRAPH,
                score=0.8,
                confidence=0.7,
                content="Test content 2",
                chunk_text="Test content 2",
                document_id="doc-2",
                chunk_id="chunk-2",
                metadata={}
            )
        ]
        
        ranked = engine.rank(evidence_items, RankingMethod.RECIPROCAL_RANK_FUSION)
        
        assert len(ranked) == 2
        assert ranked[0].ranking_position == 1
    
    def test_rank_hybrid(self):
        """Test hybrid ranking."""
        engine = RankingEngine()
        
        evidence_items = [
            EvidenceItem(
                evidence_id="1",
                evidence_type=EvidenceType.CHUNK,
                source=EvidenceSource.VECTOR,
                score=0.9,
                confidence=0.8,
                content="Test content 1",
                chunk_text="Test content 1",
                document_id="doc-1",
                chunk_id="chunk-1",
                metadata={}
            )
        ]
        
        ranked = engine.rank(evidence_items, RankingMethod.HYBRID)
        
        assert len(ranked) == 1
    
    def test_rank_with_custom_weights(self):
        """Test ranking with custom weights."""
        engine = RankingEngine()
        
        evidence_items = [
            EvidenceItem(
                evidence_id="1",
                evidence_type=EvidenceType.CHUNK,
                source=EvidenceSource.VECTOR,
                score=0.9,
                confidence=0.8,
                content="Test content 1",
                chunk_text="Test content 1",
                document_id="doc-1",
                chunk_id="chunk-1",
                metadata={}
            )
        ]
        
        custom_weights = {
            'vector_similarity': 0.5,
            'graph_proximity': 0.3,
            'keyword_relevance': 0.2
        }
        
        ranked = engine.rank(evidence_items, RankingMethod.WEIGHTED_SCORE, weights=custom_weights)
        
        assert len(ranked) == 1
    
    def test_rank_empty_list(self):
        """Test ranking empty list."""
        engine = RankingEngine()
        
        ranked = engine.rank([], RankingMethod.WEIGHTED_SCORE)
        
        assert len(ranked) == 0
    
    def test_calculate_vector_score(self):
        """Test vector score calculation."""
        engine = RankingEngine()
        
        item = EvidenceItem(
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
        
        score = engine._get_vector_score(item)
        
        assert score == 0.9
    
    def test_calculate_graph_score(self):
        """Test graph score calculation."""
        engine = RankingEngine()
        
        item = EvidenceItem(
            evidence_id="1",
            evidence_type=EvidenceType.GRAPH_NODE,
            source=EvidenceSource.GRAPH,
            score=0.8,
            confidence=0.7,
            content="Test",
            chunk_text=None,
            document_id=None,
            chunk_id=None,
            entity_id="entity-1",
            graph_node_id="entity-1",
            metadata={}
        )
        
        score = engine._get_graph_score(item)
        
        assert score == 0.8
    
    def test_calculate_keyword_score(self):
        """Test keyword score calculation."""
        engine = RankingEngine()
        
        item = EvidenceItem(
            evidence_id="1",
            evidence_type=EvidenceType.CHUNK,
            source=EvidenceSource.KEYWORD,
            score=0.7,
            confidence=0.6,
            content="Test",
            chunk_text="Test",
            document_id="doc-1",
            chunk_id="chunk-1",
            metadata={}
        )
        
        score = engine._get_keyword_score(item)
        
        assert score == 0.7
    
    def test_calculate_entity_overlap_score(self):
        """Test entity overlap score calculation."""
        engine = RankingEngine()
        
        item = EvidenceItem(
            evidence_id="1",
            evidence_type=EvidenceType.CHUNK,
            source=EvidenceSource.VECTOR,
            score=0.9,
            confidence=0.8,
            content="Test",
            chunk_text="Test",
            document_id="doc-1",
            chunk_id="chunk-1",
            metadata={'entity_ids': ['entity-1', 'entity-2', 'entity-3']}
        )
        
        score = engine._get_entity_overlap_score(item)
        
        assert 0 <= score <= 1
    
    def test_calculate_relationship_overlap_score(self):
        """Test relationship overlap score calculation."""
        engine = RankingEngine()
        
        item = EvidenceItem(
            evidence_id="1",
            evidence_type=EvidenceType.CHUNK,
            source=EvidenceSource.VECTOR,
            score=0.9,
            confidence=0.8,
            content="Test",
            chunk_text="Test",
            document_id="doc-1",
            chunk_id="chunk-1",
            metadata={'relationship_ids': ['rel-1', 'rel-2']}
        )
        
        score = engine._get_relationship_overlap_score(item)
        
        assert 0 <= score <= 1
    
    def test_calculate_freshness_score(self):
        """Test freshness score calculation."""
        engine = RankingEngine()
        
        item = EvidenceItem(
            evidence_id="1",
            evidence_type=EvidenceType.CHUNK,
            source=EvidenceSource.VECTOR,
            score=0.9,
            confidence=0.8,
            content="Test",
            chunk_text="Test",
            document_id="doc-1",
            chunk_id="chunk-1",
            metadata={'created_at': '2024-01-01T00:00:00'}
        )
        
        score = engine._get_freshness_score(item)
        
        assert 0 <= score <= 1
    
    def test_rank_by_source(self):
        """Test ranking grouped by source."""
        engine = RankingEngine()
        
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
                source=EvidenceSource.KEYWORD,
                score=0.7,
                confidence=0.6,
                content="Test",
                chunk_text="Test",
                document_id="doc-2",
                chunk_id="chunk-2",
                metadata={}
            )
        ]
        
        ranked_by_source = engine.rank_by_source(evidence_items)
        
        assert EvidenceSource.VECTOR in ranked_by_source
        assert EvidenceSource.KEYWORD in ranked_by_source
    
    def test_get_ranking_statistics(self):
        """Test ranking statistics."""
        engine = RankingEngine()
        
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
                source=EvidenceSource.KEYWORD,
                score=0.7,
                confidence=0.6,
                content="Test",
                chunk_text="Test",
                document_id="doc-2",
                chunk_id="chunk-2",
                metadata={}
            )
        ]
        
        stats = engine.get_ranking_statistics(evidence_items)
        
        assert stats['total_items'] == 2
        assert stats['average_score'] > 0
        assert 'score_distribution' in stats
