"""Unit tests for embedding generator."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from app.modules.embedding_pipeline.embedding_generator import EmbeddingGenerator, get_embedding_generator
from app.modules.embedding_pipeline.exceptions import (
    EmbeddingGenerationError,
    ModelLoadError,
    EmbeddingValidationError
)


@pytest.fixture
def mock_sentence_transformer():
    """Mock SentenceTransformer model."""
    model = Mock()
    model.get_sentence_embedding_dimension.return_value = 384
    model.max_seq_length = 512
    model.encode = Mock(return_value=np.random.rand(384))
    return model


class TestEmbeddingGenerator:
    """Test cases for EmbeddingGenerator."""
    
    @patch('app.modules.embedding_pipeline.embedding_generator.SentenceTransformer')
    @patch('torch.cuda.is_available')
    def test_initialization_cpu(self, mock_cuda, mock_st, mock_sentence_transformer):
        """Test initialization with CPU."""
        mock_cuda.return_value = False
        mock_st.return_value = mock_sentence_transformer
        
        generator = EmbeddingGenerator()
        
        assert generator._model is not None
        mock_st.assert_called_once()
    
    @patch('app.modules.embedding_pipeline.embedding_generator.SentenceTransformer')
    @patch('torch.cuda.is_available')
    def test_initialization_gpu(self, mock_cuda, mock_st, mock_sentence_transformer):
        """Test initialization with GPU auto-detection."""
        mock_cuda.return_value = True
        mock_st.return_value = mock_sentence_transformer
        
        generator = EmbeddingGenerator()
        
        assert generator._model is not None
    
    @patch('app.modules.embedding_pipeline.embedding_generator.SentenceTransformer')
    def test_model_load_error(self, mock_st):
        """Test model load error handling."""
        mock_st.side_effect = Exception("Model load failed")
        
        with pytest.raises(ModelLoadError):
            EmbeddingGenerator()
    
    @patch('app.modules.embedding_pipeline.embedding_generator.SentenceTransformer')
    def test_generate_embedding(self, mock_st, mock_sentence_transformer):
        """Test single embedding generation."""
        mock_st.return_value = mock_sentence_transformer
        
        generator = EmbeddingGenerator()
        embedding = generator.generate_embedding("Test text")
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384
        assert all(isinstance(x, float) for x in embedding)
    
    @patch('app.modules.embedding_pipeline.embedding_generator.SentenceTransformer')
    def test_generate_embedding_empty_text(self, mock_st, mock_sentence_transformer):
        """Test embedding generation with empty text."""
        mock_st.return_value = mock_sentence_transformer
        
        generator = EmbeddingGenerator()
        
        with pytest.raises(EmbeddingGenerationError):
            generator.generate_embedding("")
    
    @patch('app.modules.embedding_pipeline.embedding_generator.SentenceTransformer')
    def test_generate_embeddings_batch(self, mock_st, mock_sentence_transformer):
        """Test batch embedding generation."""
        mock_sentence_transformer.encode.return_value = np.random.rand(3, 384)
        mock_st.return_value = mock_sentence_transformer
        
        generator = EmbeddingGenerator()
        embeddings = generator.generate_embeddings_batch(["Text 1", "Text 2", "Text 3"])
        
        assert len(embeddings) == 3
        assert all(len(emb) == 384 for emb in embeddings)
    
    @patch('app.modules.embedding_pipeline.embedding_generator.SentenceTransformer')
    def test_generate_embeddings_batch_empty(self, mock_st, mock_sentence_transformer):
        """Test batch embedding generation with empty list."""
        mock_st.return_value = mock_sentence_transformer
        
        generator = EmbeddingGenerator()
        embeddings = generator.generate_embeddings_batch([])
        
        assert embeddings == []
    
    @patch('app.modules.embedding_pipeline.embedding_generator.SentenceTransformer')
    def test_embedding_validation_error(self, mock_st, mock_sentence_transformer):
        """Test embedding validation error."""
        mock_sentence_transformer.get_sentence_embedding_dimension.return_value = 384
        mock_sentence_transformer.encode.return_value = np.random.rand(256)  # Wrong dimension
        mock_st.return_value = mock_sentence_transformer
        
        generator = EmbeddingGenerator()
        
        with pytest.raises(EmbeddingValidationError):
            generator.generate_embedding("Test text")
    
    @patch('app.modules.embedding_pipeline.embedding_generator.SentenceTransformer')
    def test_generate_with_cache(self, mock_st, mock_sentence_transformer):
        """Test embedding generation with cache."""
        mock_st.return_value = mock_sentence_transformer
        
        generator = EmbeddingGenerator()
        
        # First call
        emb1 = generator.generate_embeddings_with_cache("Test text", use_cache=True)
        # Second call (should use cache)
        emb2 = generator.generate_embeddings_with_cache("Test text", use_cache=True)
        
        assert emb1 == emb2
    
    @patch('app.modules.embedding_pipeline.embedding_generator.SentenceTransformer')
    def test_get_embedding_dimension(self, mock_st, mock_sentence_transformer):
        """Test getting embedding dimension."""
        mock_sentence_transformer.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_sentence_transformer
        
        generator = EmbeddingGenerator()
        dimension = generator.get_embedding_dimension()
        
        assert dimension == 384
    
    @patch('app.modules.embedding_pipeline.embedding_generator.SentenceTransformer')
    def test_get_model_info(self, mock_st, mock_sentence_transformer):
        """Test getting model information."""
        mock_sentence_transformer.get_sentence_embedding_dimension.return_value = 384
        mock_sentence_transformer.max_seq_length = 512
        mock_st.return_value = mock_sentence_transformer
        
        generator = EmbeddingGenerator()
        info = generator.get_model_info()
        
        assert "model_name" in info
        assert "device" in info
        assert "dimension" in info
        assert info["dimension"] == 384
    
    @patch('app.modules.embedding_pipeline.embedding_generator.SentenceTransformer')
    def test_validate_embedding(self, mock_st, mock_sentence_transformer):
        """Test embedding validation."""
        mock_sentence_transformer.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_sentence_transformer
        
        generator = EmbeddingGenerator()
        
        # Valid embedding
        valid_emb = [0.1] * 384
        assert generator.validate_embedding(valid_emb) is True
        
        # Invalid dimension
        invalid_dim = [0.1] * 256
        assert generator.validate_embedding(invalid_dim) is False
        
        # Invalid type
        invalid_type = ["not"] * 384
        assert generator.validate_embedding(invalid_type) is False
        
        # Contains NaN
        nan_emb = [0.1] * 383 + [float('nan')]
        assert generator.validate_embedding(nan_emb) is False
    
    @patch('app.modules.embedding_pipeline.embedding_generator.SentenceTransformer')
    def test_clear_cache(self, mock_st, mock_sentence_transformer):
        """Test clearing embedding cache."""
        mock_st.return_value = mock_sentence_transformer
        
        generator = EmbeddingGenerator()
        generator.clear_cache()
        
        assert generator._generate_with_cache.cache_info().currsize == 0
    
    @patch('app.modules.embedding_pipeline.embedding_generator.SentenceTransformer')
    def test_singleton_pattern(self, mock_st, mock_sentence_transformer):
        """Test singleton pattern."""
        mock_st.return_value = mock_sentence_transformer
        
        gen1 = EmbeddingGenerator()
        gen2 = EmbeddingGenerator()
        
        assert gen1 is gen2


class TestGetEmbeddingGenerator:
    """Test cases for get_embedding_generator function."""
    
    @patch('app.modules.embedding_pipeline.embedding_generator.SentenceTransformer')
    def test_get_singleton(self, mock_st, mock_sentence_transformer):
        """Test getting singleton instance."""
        mock_st.return_value = mock_sentence_transformer
        
        gen1 = get_embedding_generator()
        gen2 = get_embedding_generator()
        
        assert gen1 is gen2
