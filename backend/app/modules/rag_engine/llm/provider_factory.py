"""Factory for creating LLM provider instances."""

from typing import Optional, Dict, Any
from app.config.settings import settings
from app.core.logging import setup_logging

from .base_provider import LLMProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider
from .mock_provider import MockProvider
from app.modules.rag_engine.constants import (
    PROVIDER_GEMINI,
    PROVIDER_OPENAI,
    PROVIDER_OLLAMA,
    PROVIDER_MOCK
)
from app.modules.rag_engine.exceptions import ProviderException

logger = setup_logging()


class ProviderFactory:
    """Factory for creating LLM provider instances."""
    
    _providers: Dict[str, LLMProvider] = {}
    _provider_configs: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def get_provider(
        cls,
        provider_name: Optional[str] = None,
        **kwargs
    ) -> LLMProvider:
        """Get or create a provider instance.
        
        Args:
            provider_name: Name of the provider (defaults to settings)
            **kwargs: Additional provider configuration
            
        Returns:
            LLMProvider instance
        """
        provider_name = provider_name or settings.llm_provider or PROVIDER_GEMINI
        
        # Check if provider already exists
        if provider_name in cls._providers:
            return cls._providers[provider_name]
        
        # Create new provider
        provider = cls._create_provider(provider_name, **kwargs)
        cls._providers[provider_name] = provider
        cls._provider_configs[provider_name] = kwargs
        
        logger.info(f"Created {provider_name} provider")
        return provider
    
    @classmethod
    def _create_provider(cls, provider_name: str, **kwargs) -> LLMProvider:
        """Create a provider instance.
        
        Args:
            provider_name: Name of the provider
            **kwargs: Provider configuration
            
        Returns:
            LLMProvider instance
        """
        if provider_name == PROVIDER_GEMINI:
            api_key = kwargs.get('api_key') or settings.google_api_key
            model = kwargs.get('model') or settings.gemini_model
            return GeminiProvider(api_key=api_key, model=model)
        
        elif provider_name == PROVIDER_OPENAI:
            api_key = kwargs.get('api_key') or settings.openai_api_key
            model = kwargs.get('model') or settings.openai_model
            return OpenAIProvider(api_key=api_key, model=model)
        
        elif provider_name == PROVIDER_OLLAMA:
            model = kwargs.get('model') or settings.ollama_model
            url = kwargs.get('url') or settings.ollama_url
            return OllamaProvider(model=model, url=url)
        
        elif provider_name == PROVIDER_MOCK:
            model = kwargs.get('model') or 'mock-model-v1'
            return MockProvider(model=model)
        
        else:
            raise ProviderException(f"Unknown provider: {provider_name}")
    
    @classmethod
    async def initialize_provider(cls, provider_name: Optional[str] = None) -> LLMProvider:
        """Get and initialize a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Initialized LLMProvider instance
        """
        provider = cls.get_provider(provider_name)
        
        if not provider.is_initialized:
            await provider.initialize()
            logger.info(f"Initialized {provider_name or settings.llm_provider} provider")
        
        return provider
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear the provider cache."""
        cls._providers.clear()
        cls._provider_configs.clear()
        logger.info("Cleared provider cache")
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available provider names.
        
        Returns:
            List of provider names
        """
        return [PROVIDER_GEMINI, PROVIDER_OPENAI, PROVIDER_OLLAMA, PROVIDER_MOCK]
    
    @classmethod
    def get_provider_info(cls, provider_name: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Provider information dictionary
        """
        provider_name = provider_name or settings.llm_provider or PROVIDER_GEMINI
        
        if provider_name in cls._providers:
            return cls._providers[provider_name].get_model_info()
        
        # Create temporary instance to get info
        try:
            temp_provider = cls._create_provider(provider_name)
            return temp_provider.get_model_info()
        except Exception as e:
            logger.error(f"Failed to get provider info for {provider_name}: {e}")
            return {
                "provider": provider_name,
                "error": str(e),
                "available": False
            }
