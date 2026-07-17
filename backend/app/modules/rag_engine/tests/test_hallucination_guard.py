"""Unit tests for Hallucination Guard."""

import pytest
from app.modules.rag_engine.hallucination_guard import HallucinationGuard


class TestHallucinationGuard:
    """Test suite for HallucinationGuard."""
    
    @pytest.fixture
    def guard(self):
        """Create a HallucinationGuard instance."""
        return HallucinationGuard()
    
    @pytest.fixture
    def sample_context_package(self):
        """Create a sample context package."""
        return {
            'retrieved_chunks': [
                {'chunk_id': 'chunk_1', 'score': 0.85, 'text': 'Sample text'},
                {'chunk_id': 'chunk_2', 'score': 0.78, 'text': 'More text'}
            ]
        }
    
    def test_check_response_sufficient_evidence(self, guard, sample_context_package):
        """Test response check with sufficient evidence."""
        response_text = "Based on the documents, the answer is clear."
        confidence_scores = {
            'overall': 0.8,
            'evidence': 0.75,
            'retrieval': 0.85,
            'reasoning': 0.8
        }
        
        result = guard.check_response(response_text, sample_context_package, confidence_scores)
        
        assert result['passed'] is True
        assert len(result['issues']) == 0
    
    def test_check_response_insufficient_evidence(self, guard):
        """Test response check with insufficient evidence."""
        context_package = {'retrieved_chunks': []}
        response_text = "Some answer"
        confidence_scores = {
            'overall': 0.3,
            'evidence': 0.2,
            'retrieval': 0.1,
            'reasoning': 0.3
        }
        
        result = guard.check_response(response_text, context_package, confidence_scores)
        
        assert result['passed'] is False
        assert len(result['issues']) > 0
    
    def test_check_evidence_sufficiency(self, guard, sample_context_package):
        """Test evidence sufficiency check."""
        confidence_scores = {'evidence': 0.8}
        
        result = guard._check_evidence_sufficiency(sample_context_package, confidence_scores)
        
        assert result['sufficient'] is True
    
    def test_check_evidence_conflict(self, guard):
        """Test evidence conflict detection."""
        context_package = {
            'retrieved_chunks': [
                {'chunk_id': 'chunk_1', 'score': 0.9},
                {'chunk_id': 'chunk_2', 'score': 0.1}  # Outlier
            ]
        }
        
        result = guard._check_evidence_conflict(context_package)
        
        # Should detect potential conflict due to score variance
        assert 'has_conflict' in result
    
    def test_check_source_coverage(self, guard, sample_context_package):
        """Test source coverage check."""
        response_text = "Sample text from documents"
        
        coverage = guard._check_source_coverage(response_text, sample_context_package)
        
        assert 'coverage' in coverage
        assert 0.0 <= coverage['coverage'] <= 1.0
    
    def test_should_block_response(self, guard):
        """Test response blocking decision."""
        check_result = {'passed': False, 'should_block': True, 'issues': ['Insufficient evidence']}
        
        should_block = guard.should_block_response(check_result)
        
        assert should_block is True
    
    def test_get_fallback_response(self, guard):
        """Test fallback response generation."""
        check_result = {'issues': ['insufficient evidence']}
        
        fallback = guard.get_fallback_response(check_result)
        
        assert fallback is not None
        assert len(fallback) > 0
    
    def test_validate_before_generation(self, guard, sample_context_package):
        """Test pre-generation validation."""
        is_valid = guard.validate_before_generation(sample_context_package)
        
        assert is_valid is True
    
    def test_validate_before_generation_no_chunks(self, guard):
        """Test pre-generation validation with no chunks."""
        context_package = {'retrieved_chunks': []}
        
        is_valid = guard.validate_before_generation(context_package)
        
        assert is_valid is False
