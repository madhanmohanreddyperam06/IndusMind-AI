"""Unit tests for Context Formatter."""

import pytest
from app.modules.rag_engine.context_formatter import ContextFormatter


class TestContextFormatter:
    """Test suite for ContextFormatter."""
    
    @pytest.fixture
    def formatter(self):
        """Create a ContextFormatter instance."""
        return ContextFormatter()
    
    @pytest.fixture
    def sample_context_package(self):
        """Create a sample context package."""
        return {
            'question': 'What is the maintenance schedule for equipment X?',
            'retrieved_chunks': [
                {
                    'chunk_id': 'chunk_1',
                    'document_id': 'doc_1',
                    'text': 'Equipment X requires monthly maintenance.',
                    'score': 0.85,
                    'page_number': 1
                },
                {
                    'chunk_id': 'chunk_2',
                    'document_id': 'doc_2',
                    'text': 'Maintenance includes oil changes and filter replacements.',
                    'score': 0.78,
                    'page_number': 2
                }
            ],
            'entities': [
                {'name': 'Equipment X', 'type': 'Equipment', 'confidence': 0.9},
                {'name': 'oil', 'type': 'Material', 'confidence': 0.8}
            ],
            'relationships': [
                {'source': 'Equipment X', 'target': 'oil', 'type': 'requires', 'confidence': 0.7}
            ],
            'graph_context': {
                'graph_density': 0.5,
                'node_count': 10,
                'edge_count': 15
            }
        }
    
    def test_format_context_basic(self, formatter, sample_context_package):
        """Test basic context formatting."""
        result = formatter.format_context(sample_context_package)
        
        assert result is not None
        assert len(result) > 0
        assert 'Equipment X' in result
        assert 'maintenance' in result.lower()
    
    def test_format_context_with_empty_chunks(self, formatter):
        """Test formatting with empty chunks."""
        context = {
            'question': 'Test question',
            'retrieved_chunks': []
        }
        
        result = formatter.format_context(context)
        
        assert result is not None
        assert 'Test question' in result
    
    def test_estimate_tokens(self, formatter):
        """Test token estimation."""
        text = "This is a test text for token estimation."
        
        tokens = formatter.estimate_tokens(text)
        
        assert tokens > 0
        assert isinstance(tokens, int)
    
    def test_get_context_summary(self, formatter, sample_context_package):
        """Test context summary generation."""
        summary = formatter.get_context_summary(sample_context_package)
        
        assert summary['total_chunks'] == 2
        assert summary['total_entities'] == 2
        assert summary['total_relationships'] == 1
        assert summary['has_graph_context'] is True
        assert summary['estimated_tokens'] > 0
    
    def test_truncate_to_tokens(self, formatter):
        """Test context truncation."""
        long_text = "This is a test. " * 1000  # Create long text
        
        truncated = formatter._truncate_to_tokens(long_text, max_tokens=100)
        
        assert len(truncated) < len(long_text)
        assert 'truncated' in truncated.lower()
