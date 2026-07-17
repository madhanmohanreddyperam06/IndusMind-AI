"""Unit tests for Mock Provider."""

import pytest
from app.modules.rag_engine.llm.mock_provider import MockProvider
from app.modules.rag_engine.llm.base_provider import GenerationConfig


class TestMockProvider:
    """Test suite for MockProvider."""
    
    @pytest.fixture
    async def provider(self):
        """Create and initialize a MockProvider instance."""
        provider = MockProvider()
        await provider.initialize()
        return provider
    
    @pytest.mark.asyncio
    async def test_initialize(self, provider):
        """Test provider initialization."""
        assert provider.is_initialized is True
    
    @pytest.mark.asyncio
    async def test_generate_answer(self, provider):
        """Test answer generation."""
        prompt = "What is the capital of France?"
        config = GenerationConfig(temperature=0.7, max_tokens=100)
        
        result = await provider.generate_answer(prompt, config)
        
        assert result.text is not None
        assert len(result.text) > 0
        assert result.prompt_tokens >= 0
        assert result.completion_tokens >= 0
        assert result.total_tokens > 0
        assert result.model == 'mock-model-v1'
    
    @pytest.mark.asyncio
    async def test_generate_answer_stream(self, provider):
        """Test streaming answer generation."""
        prompt = "Test streaming"
        config = GenerationConfig()
        
        chunks = []
        async for chunk in provider.generate_answer_stream(prompt, config):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        assert all(len(chunk) > 0 for chunk in chunks)
    
    @pytest.mark.asyncio
    async def test_summarize(self, provider):
        """Test text summarization."""
        text = "This is a long text that needs to be summarized. " * 10
        
        result = await provider.summarize(text, max_length=50, style='concise')
        
        assert result.text is not None
        assert len(result.text) <= 100  # Allow some margin
        assert 'MOCK SUMMARY' in result.text
    
    @pytest.mark.asyncio
    async def test_generate_structured_output(self, provider):
        """Test structured output generation."""
        prompt = "Generate structured data"
        schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'value': {'type': 'number'}
            }
        }
        
        result = await provider.generate_structured_output(prompt, schema)
        
        assert isinstance(result, dict)
        assert 'name' in result
        assert 'value' in result
    
    @pytest.mark.asyncio
    async def test_health_check(self, provider):
        """Test health check."""
        is_healthy = await provider.health_check()
        
        assert is_healthy is True
    
    def test_get_model_info(self, provider):
        """Test model information retrieval."""
        info = provider.get_model_info()
        
        assert info['provider'] == 'mock'
        assert info['model'] == 'mock-model-v1'
        assert 'capabilities' in info
        assert 'initialized' in info
    
    def test_validate_config(self, provider):
        """Test configuration validation."""
        valid_config = GenerationConfig(temperature=0.7, max_tokens=100)
        validated = provider._validate_config(valid_config)
        
        assert validated.temperature == 0.7
        assert validated.max_tokens == 100
    
    def test_validate_config_invalid(self, provider):
        """Test configuration validation with invalid values."""
        invalid_config = GenerationConfig(temperature=3.0, max_tokens=-1)
        
        with pytest.raises(ValueError):
            provider._validate_config(invalid_config)
