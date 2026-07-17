"""Unit tests for Confidence Estimator."""

import pytest
from app.modules.rag_engine.confidence_estimator import ConfidenceEstimator
from app.modules.rag_engine.schemas import ConfidenceScores


class TestConfidenceEstimator:
    """Test suite for ConfidenceEstimator."""
    
    @pytest.fixture
    def estimator(self):
        """Create a ConfidenceEstimator instance."""
        return ConfidenceEstimator()
    
    @pytest.fixture
    def sample_context_package(self):
        """Create a sample context package."""
        return {
            'retrieved_chunks': [
                {'chunk_id': 'chunk_1', 'score': 0.85},
                {'chunk_id': 'chunk_2', 'score': 0.78}
            ],
            'entities': [
                {'name': 'Entity1', 'confidence': 0.9},
                {'name': 'Entity2', 'confidence': 0.8}
            ],
            'relationships': [
                {'source': 'A', 'target': 'B', 'confidence': 0.75}
            ]
        }
    
    def test_estimate_confidence(self, estimator, sample_context_package):
        """Test confidence estimation."""
        response_text = "Based on the context, the answer is clear."
        citations = []
        
        confidence = estimator.estimate_confidence(
            sample_context_package,
            response_text,
            citations
        )
        
        assert isinstance(confidence, ConfidenceScores)
        assert 0.0 <= confidence.overall <= 1.0
        assert 0.0 <= confidence.evidence <= 1.0
        assert 0.0 <= confidence.retrieval <= 1.0
        assert 0.0 <= confidence.reasoning <= 1.0
    
    def test_estimate_retrieval_confidence(self, estimator, sample_context_package):
        """Test retrieval confidence estimation."""
        confidence = estimator._estimate_retrieval_confidence(sample_context_package)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.0  # Should have some confidence with chunks
    
    def test_estimate_evidence_confidence(self, estimator, sample_context_package):
        """Test evidence confidence estimation."""
        citations = []
        confidence = estimator._estimate_evidence_confidence(sample_context_package, citations)
        
        assert 0.0 <= confidence <= 1.0
    
    def test_estimate_entity_confidence(self, estimator, sample_context_package):
        """Test entity confidence estimation."""
        confidence = estimator._estimate_entity_confidence(sample_context_package)
        
        assert 0.0 <= confidence <= 1.0
    
    def test_estimate_relationship_confidence(self, estimator, sample_context_package):
        """Test relationship confidence estimation."""
        confidence = estimator._estimate_relationship_confidence(sample_context_package)
        
        assert 0.0 <= confidence <= 1.0
    
    def test_estimate_reasoning_confidence(self, estimator):
        """Test reasoning confidence estimation."""
        confident_text = "Based on the evidence, the data clearly shows"
        uncertain_text = "I'm not sure, but I think possibly"
        
        confident_score = estimator._estimate_reasoning_confidence(confident_text, {})
        uncertain_score = estimator._estimate_reasoning_confidence(uncertain_text, {})
        
        assert confident_score > uncertain_score
    
    def test_get_confidence_level(self, estimator):
        """Test confidence level labeling."""
        assert estimator.get_confidence_level(0.9) == "high"
        assert estimator.get_confidence_level(0.6) == "medium"
        assert estimator.get_confidence_level(0.4) == "low"
        assert estimator.get_confidence_level(0.2) == "very_low"
    
    def test_is_confidence_sufficient(self, estimator):
        """Test confidence sufficiency check."""
        assert estimator.is_confidence_sufficient(0.8, threshold=0.5) is True
        assert estimator.is_confidence_sufficient(0.3, threshold=0.5) is False
