"""Embedding generator using SentenceTransformers."""

from typing import List, Dict, Any, Optional
import torch
from sentence_transformers import SentenceTransformer
from app.modules.embedding_pipeline.exceptions import (
    EmbeddingGenerationError,
    ModelLoadError,
    EmbeddingValidationError
)
from app.config.settings import settings
from app.core.logging import setup_logging
from functools import lru_cache

logger = setup_logging()


class EmbeddingGenerator:
    """Singleton embedding generator using SentenceTransformers."""
    
    _instance: Optional['EmbeddingGenerator'] = None
    _model: Optional[SentenceTransformer] = None
    _model_name: str = None
    _device: str = None
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize embedding generator (lazy loading)."""
        if self._model is None:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the embedding model with device auto-detection.
        
        Raises:
            ModelLoadError: If model fails to load
        """
        try:
            model_name = settings.embedding_model_name
            device = settings.embedding_device
            
            # Auto-detect GPU if available
            if device == "cpu" and torch.cuda.is_available():
                device = "cuda"
                logger.info("CUDA detected, using GPU for embeddings")
            
            logger.info(f"Loading embedding model: {model_name} on device: {device}")
            
            self._model = SentenceTransformer(model_name, device=device)
            self._model_name = model_name
            self._device = device
            
            # Warm up the model
            self._model.encode("test", show_progress_bar=False)
            
            logger.info(f"Embedding model loaded successfully. Dimension: {self._model.get_sentence_embedding_dimension()}")
            
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise ModelLoadError(f"Failed to load embedding model: {str(e)}", model_name)
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
            
        Raises:
            EmbeddingGenerationError: If embedding generation fails
            EmbeddingValidationError: If embedding dimension is invalid
        """
        try:
            if not text or not text.strip():
                raise EmbeddingGenerationError("Cannot generate embedding for empty text")
            
            embedding = self._model.encode(
                text,
                convert_to_numpy=True,
                show_progress_bar=False,
                normalize_embeddings=True
            )
            
            # Validate embedding dimension
            expected_dim = self._model.get_sentence_embedding_dimension()
            actual_dim = len(embedding)
            
            if actual_dim != expected_dim:
                raise EmbeddingValidationError(
                    f"Embedding dimension mismatch: expected {expected_dim}, got {actual_dim}",
                    expected_dim=expected_dim,
                    actual_dim=actual_dim
                )
            
            return embedding.tolist()
            
        except EmbeddingValidationError:
            raise
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise EmbeddingGenerationError(f"Failed to generate embedding: {str(e)}")
    
    def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = None,
        show_progress: bool = False
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch.
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            show_progress: Whether to show progress bar
            
        Returns:
            List of embedding vectors
            
        Raises:
            EmbeddingGenerationError: If batch embedding fails
        """
        try:
            if not texts:
                return []
            
            # Filter empty texts
            valid_texts = [t for t in texts if t and t.strip()]
            if not valid_texts:
                return []
            
            batch_size = batch_size or settings.embedding_batch_size
            
            embeddings = self._model.encode(
                valid_texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=show_progress,
                normalize_embeddings=True
            )
            
            # Validate embeddings
            expected_dim = self._model.get_sentence_embedding_dimension()
            for i, embedding in enumerate(embeddings):
                actual_dim = len(embedding)
                if actual_dim != expected_dim:
                    raise EmbeddingValidationError(
                        f"Embedding dimension mismatch at index {i}: expected {expected_dim}, got {actual_dim}",
                        expected_dim=expected_dim,
                        actual_dim=actual_dim
                    )
            
            return [emb.tolist() for emb in embeddings]
            
        except EmbeddingValidationError:
            raise
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise EmbeddingGenerationError(f"Failed to generate batch embeddings: {str(e)}")
    
    def generate_embeddings_with_cache(
        self,
        text: str,
        use_cache: bool = True
    ) -> List[float]:
        """Generate embedding with optional caching.
        
        Args:
            text: Input text
            use_cache: Whether to use cache
            
        Returns:
            Embedding vector
        """
        if use_cache and settings.embedding_cache_enabled:
            return self._generate_with_cache(text)
        return self.generate_embedding(text)
    
    @lru_cache(maxsize=1000)
    def _generate_with_cache(self, text: str) -> List[float]:
        """Generate embedding with LRU cache.
        
        Args:
            text: Input text (must be hashable for cache)
            
        Returns:
            Embedding vector
        """
        return self.generate_embedding(text)
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding model.
        
        Returns:
            Embedding dimension
        """
        return self._model.get_sentence_embedding_dimension()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self._model_name,
            "device": self._device,
            "dimension": self._model.get_sentence_embedding_dimension(),
            "max_seq_length": self._model.max_seq_length,
            "cache_enabled": settings.embedding_cache_enabled,
            "batch_size": settings.embedding_batch_size
        }
    
    def validate_embedding(self, embedding: List[float]) -> bool:
        """Validate an embedding vector.
        
        Args:
            embedding: Embedding vector to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            expected_dim = self._model.get_sentence_embedding_dimension()
            
            if not isinstance(embedding, list):
                return False
            
            if len(embedding) != expected_dim:
                return False
            
            # Check for NaN or Inf values
            for val in embedding:
                if not isinstance(val, (int, float)):
                    return False
                if val != val:  # NaN check
                    return False
                if abs(val) == float('inf'):  # Inf check
                    return False
            
            return True
            
        except Exception:
            return False
    
    def clear_cache(self):
        """Clear the embedding cache."""
        self._generate_with_cache.cache_clear()
        logger.info("Embedding cache cleared")


# Singleton instance
_embedding_generator: Optional[EmbeddingGenerator] = None


def get_embedding_generator() -> EmbeddingGenerator:
    """Get the singleton embedding generator instance.
    
    Returns:
        EmbeddingGenerator instance
    """
    global _embedding_generator
    
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    
    return _embedding_generator
