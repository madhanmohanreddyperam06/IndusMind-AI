"""Base LLM provider abstraction."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass


@dataclass
class GenerationConfig:
    """Configuration for LLM generation."""
    
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 0.9
    top_k: Optional[int] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    additional_params: Optional[Dict[str, Any]] = None


@dataclass
class GenerationResult:
    """Result from LLM generation."""
    
    text: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize provider.
        
        Args:
            api_key: API key for authentication
            model: Model name to use
        """
        self.api_key = api_key
        self.model = model
        self._is_initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider (authenticate, load model, etc.)."""
        pass
    
    @abstractmethod
    async def generate_answer(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> GenerationResult:
        """Generate an answer for the given prompt.
        
        Args:
            prompt: The input prompt
            config: Generation configuration
            
        Returns:
            GenerationResult with the generated text and metadata
        """
        pass
    
    @abstractmethod
    async def generate_answer_stream(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> AsyncGenerator[str, None]:
        """Generate an answer with streaming.
        
        Args:
            prompt: The input prompt
            config: Generation configuration
            
        Yields:
            Chunks of generated text
        """
        pass
    
    @abstractmethod
    async def summarize(
        self,
        text: str,
        max_length: int = 200,
        style: str = "concise"
    ) -> GenerationResult:
        """Summarize the given text.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            style: Summary style (concise, detailed, etc.)
            
        Returns:
            GenerationResult with the summary
        """
        pass
    
    @abstractmethod
    async def generate_structured_output(
        self,
        prompt: str,
        schema_definition: Dict[str, Any],
        config: Optional[GenerationConfig] = None
    ) -> Dict[str, Any]:
        """Generate structured output following a schema.
        
        Args:
            prompt: The input prompt
            schema_definition: JSON schema for output structure
            config: Generation configuration
            
        Returns:
            Structured output matching the schema
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy and available.
        
        Returns:
            True if healthy, False otherwise
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        pass
    
    @property
    def is_initialized(self) -> bool:
        """Check if provider is initialized."""
        return self._is_initialized
    
    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return self.__class__.__name__
    
    def _validate_config(self, config: Optional[GenerationConfig]) -> GenerationConfig:
        """Validate and return config with defaults.
        
        Args:
            config: Input config or None
            
        Returns:
            Validated GenerationConfig
        """
        if config is None:
            config = GenerationConfig()
        
        # Validate temperature
        if not 0.0 <= config.temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        
        # Validate max_tokens
        if config.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        
        # Validate top_p
        if not 0.0 <= config.top_p <= 1.0:
            raise ValueError("top_p must be between 0.0 and 1.0")
        
        return config
    
    def _ensure_initialized(self) -> None:
        """Ensure provider is initialized."""
        if not self._is_initialized:
            raise RuntimeError(f"{self.provider_name} is not initialized. Call initialize() first.")
