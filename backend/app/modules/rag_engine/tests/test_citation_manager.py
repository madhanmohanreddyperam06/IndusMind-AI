"""Unit tests for Citation Manager."""

import pytest
from app.modules.rag_engine.citation_manager import CitationManager
from app.modules.rag_engine.schemas import Citation


class TestCitationManager:
    """Test suite for CitationManager."""
    
    @pytest.fixture
    def citation_manager(self):
        """Create a CitationManager instance."""
        return CitationManager()
    
    @pytest.fixture
    def sample_context_package(self):
        """Create a sample context package."""
        return {
            'retrieved_chunks': [
                {
                    'chunk_id': 'chunk_1',
                    'document_id': 'doc_1',
                    'text': 'Sample text from chunk 1',
                    'score': 0.85,
                    'page_number': 1,
                    'section': 'Introduction'
                },
                {
                    'chunk_id': 'chunk_2',
                    'document_id': 'doc_2',
                    'text': 'Sample text from chunk 2',
                    'score': 0.78,
                    'page_number': 2,
                    'section': 'Methods'
                }
            ]
        }
    
    def test_extract_citations_from_response(self, citation_manager, sample_context_package):
        """Test citation extraction from response."""
        response_text = "According to [doc_1:chunk_1], the equipment requires maintenance."
        
        citations = citation_manager.extract_citations_from_response(response_text, sample_context_package)
        
        assert len(citations) > 0
        assert citations[0].document_id == 'doc_1'
        assert citations[0].chunk_id == 'chunk_1'
    
    def test_extract_citations_no_citations(self, citation_manager, sample_context_package):
        """Test extraction when no citations present."""
        response_text = "This response has no citations."
        
        citations = citation_manager.extract_citations_from_response(response_text, sample_context_package)
        
        assert len(citations) == 0
    
    def test_deduplicate_citations(self, citation_manager):
        """Test citation deduplication."""
        citations = [
            Citation(document_id='doc_1', chunk_id='chunk_1', confidence=0.8),
            Citation(document_id='doc_1', chunk_id='chunk_1', confidence=0.8),
            Citation(document_id='doc_2', chunk_id='chunk_2', confidence=0.7)
        ]
        
        unique = citation_manager._deduplicate_citations(citations)
        
        assert len(unique) == 2
    
    def test_format_citations(self, citation_manager):
        """Test citation formatting."""
        citations = [
            Citation(document_id='doc_1', chunk_id='chunk_1', confidence=0.8)
        ]
        
        formatted = citation_manager.format_citations(citations)
        
        assert '[doc_1:chunk_1]' in formatted
    
    def test_validate_citations(self, citation_manager, sample_context_package):
        """Test citation validation."""
        citations = [
            Citation(document_id='doc_1', chunk_id='chunk_1', confidence=0.8)
        ]
        
        validation = citation_manager.validate_citations(citations, sample_context_package)
        
        assert validation['total'] == 1
        assert len(validation['valid']) == 1
    
    def test_get_citation_statistics(self, citation_manager):
        """Test citation statistics."""
        citations = [
            Citation(document_id='doc_1', chunk_id='chunk_1', confidence=0.8),
            Citation(document_id='doc_2', chunk_id='chunk_2', confidence=0.7)
        ]
        
        stats = citation_manager.get_citation_statistics(citations)
        
        assert stats['total'] == 2
        assert stats['unique_documents'] == 2
        assert stats['unique_chunks'] == 2
