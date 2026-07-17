"""Unit tests for Response Formatter."""

import pytest
from app.modules.rag_engine.response_formatter import ResponseFormatter
from app.modules.rag_engine.schemas import (
    Citation,
    ConfidenceScores,
    GenerationStatistics
)


class TestResponseFormatter:
    """Test suite for ResponseFormatter."""
    
    @pytest.fixture
    def formatter(self):
        """Create a ResponseFormatter instance."""
        return ResponseFormatter()
    
    @pytest.fixture
    def sample_citations(self):
        """Create sample citations."""
        return [
            Citation(
                document_id='doc_1',
                chunk_id='chunk_1',
                confidence=0.85,
                text='Sample text from document'
            )
        ]
    
    @pytest.fixture
    def sample_confidence_scores(self):
        """Create sample confidence scores."""
        return ConfidenceScores(
            overall=0.8,
            evidence=0.75,
            retrieval=0.85,
            reasoning=0.8
        )
    
    @pytest.fixture
    def sample_statistics(self):
        """Create sample generation statistics."""
        return GenerationStatistics(
            processing_time_ms=1500.0,
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=300,
            context_size=5000,
            evidence_count=2,
            citation_count=1,
            provider='gemini'
        )
    
    def test_format_response(self, formatter, sample_citations, sample_confidence_scores, sample_statistics):
        """Test response formatting."""
        answer = "This is the generated answer."
        context_package = {
            'question': 'Test question',
            'entities': [{'name': 'Entity1', 'type': 'Type1'}],
            'relationships': [{'source': 'A', 'target': 'B', 'type': 'rel'}]
        }
        
        response = formatter.format_response(
            answer=answer,
            context_package=context_package,
            citations=sample_citations,
            confidence_scores=sample_confidence_scores,
            statistics=sample_statistics
        )
        
        assert response.answer == answer
        assert response.confidence.overall == 0.8
        assert response.statistics.provider == 'gemini'
        assert len(response.citations) == 1
    
    def test_generate_summary(self, formatter):
        """Test summary generation."""
        long_answer = "This is a long answer. It has multiple sentences. Each sentence should be included in the summary."
        
        summary = formatter._generate_summary(long_answer, max_length=50)
        
        assert summary is not None
        assert len(summary) <= 60  # Allow some margin for ellipsis
    
    def test_extract_supporting_documents(self, formatter, sample_citations):
        """Test supporting document extraction."""
        doc_ids = formatter._extract_supporting_documents(sample_citations)
        
        assert len(doc_ids) == 1
        assert 'doc_1' in doc_ids
    
    def test_generate_follow_up_questions(self, formatter):
        """Test follow-up question generation."""
        context_package = {
            'question': 'What is the maintenance schedule?',
            'entities': [
                {'name': 'Equipment X', 'type': 'Equipment'}
            ],
            'relationships': [
                {'source': 'Equipment X', 'target': 'Oil', 'type': 'requires'}
            ]
        }
        
        questions = formatter._generate_follow_up_questions('Test question', context_package)
        
        assert len(questions) > 0
        assert len(questions) <= 5  # Should be limited
    
    def test_format_error_response(self, formatter):
        """Test error response formatting."""
        error_response = formatter.format_error_response("Test error", "generation_error")
        
        assert error_response['error'] is True
        assert error_response['message'] == "Test error"
        assert error_response['confidence']['overall'] == 0.0
    
    def test_format_streaming_chunk(self, formatter):
        """Test streaming chunk formatting."""
        chunk = formatter.format_streaming_chunk("Test chunk", is_final=False)
        
        assert chunk['chunk'] == "Test chunk"
        assert chunk['is_final'] is False
        assert chunk['done'] is False
    
    def test_format_streaming_chunk_final(self, formatter):
        """Test final streaming chunk formatting."""
        chunk = formatter.format_streaming_chunk("", is_final=True)
        
        assert chunk['is_final'] is True
        assert chunk['done'] is True
    
    def test_validate_response_structure(self, formatter):
        """Test response structure validation."""
        valid_response = {
            'answer': 'Test answer',
            'confidence': {'overall': 0.8},
            'statistics': {'processing_time_ms': 1000}
        }
        
        is_valid = formatter.validate_response_structure(valid_response)
        
        assert is_valid is True
    
    def test_validate_response_structure_invalid(self, formatter):
        """Test response structure validation with invalid structure."""
        invalid_response = {
            'answer': 'Test answer'
            # Missing confidence and statistics
        }
        
        is_valid = formatter.validate_response_structure(invalid_response)
        
        assert is_valid is False
