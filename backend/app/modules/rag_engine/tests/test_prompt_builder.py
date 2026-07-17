"""Unit tests for Prompt Builder."""

import pytest
from app.modules.rag_engine.prompt_builder import PromptBuilder


class TestPromptBuilder:
    """Test suite for PromptBuilder."""
    
    @pytest.fixture
    def prompt_builder(self):
        """Create a PromptBuilder instance."""
        return PromptBuilder()
    
    @pytest.fixture
    def sample_context_package(self):
        """Create a sample context package."""
        return {
            'question': 'What is the maintenance schedule?',
            'retrieved_chunks': [
                {
                    'chunk_id': 'chunk_1',
                    'document_id': 'doc_1',
                    'text': 'Monthly maintenance is required.',
                    'score': 0.85
                }
            ],
            'entities': [
                {'name': 'Equipment', 'type': 'Asset', 'confidence': 0.9}
            ]
        }
    
    def test_build_prompt_basic(self, prompt_builder, sample_context_package):
        """Test basic prompt building."""
        prompt = prompt_builder.build_prompt(
            question='What is the maintenance schedule?',
            context_package=sample_context_package
        )
        
        assert prompt is not None
        assert len(prompt) > 0
        assert 'maintenance schedule' in prompt.lower()
        assert 'Monthly maintenance' in prompt
    
    def test_build_prompt_with_history(self, prompt_builder, sample_context_package):
        """Test prompt building with conversation history."""
        history = [
            {'role': 'user', 'content': 'Previous question'},
            {'role': 'assistant', 'content': 'Previous answer'}
        ]
        
        prompt = prompt_builder.build_prompt(
            question='What is the maintenance schedule?',
            context_package=sample_context_package,
            conversation_history=history
        )
        
        assert 'Conversation History' in prompt
        assert 'Previous question' in prompt
    
    def test_build_summarization_prompt(self, prompt_builder):
        """Test summarization prompt building."""
        prompt = prompt_builder.build_summarization_prompt(
            text='This is a long text that needs to be summarized.',
            max_length=100,
            style='concise'
        )
        
        assert prompt is not None
        assert 'summarize' in prompt.lower()
        assert 'concise' in prompt.lower()
    
    def test_build_structured_output_prompt(self, prompt_builder, sample_context_package):
        """Test structured output prompt building."""
        schema = {
            'type': 'object',
            'properties': {
                'answer': {'type': 'string'},
                'confidence': {'type': 'number'}
            }
        }
        
        prompt = prompt_builder.build_structured_output_prompt(
            question='Test question',
            context_package=sample_context_package,
            schema_definition=schema
        )
        
        assert prompt is not None
        assert 'JSON schema' in prompt
    
    def test_get_prompt_statistics(self, prompt_builder):
        """Test prompt statistics."""
        prompt = "This is a test prompt for statistics."
        
        stats = prompt_builder.get_prompt_statistics(prompt)
        
        assert stats['length'] == len(prompt)
        assert stats['estimated_tokens'] > 0
        assert stats['word_count'] > 0
    
    def test_update_system_prompt(self, prompt_builder):
        """Test system prompt update."""
        new_system_prompt = "New system prompt"
        prompt_builder.update_system_prompt(new_system_prompt)
        
        assert prompt_builder.system_prompt == new_system_prompt
