"""Mock LLM provider for testing."""

import asyncio
import time
from typing import Dict, Any, Optional, AsyncGenerator

from .base_provider import LLMProvider, GenerationConfig, GenerationResult


class MockProvider(LLMProvider):
    """Mock LLM provider for testing purposes."""
    
    DEFAULT_MODEL = "mock-model-v1"
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize mock provider.
        
        Args:
            api_key: Not used for mock
            model: Model name (defaults to mock-model-v1)
        """
        super().__init__(api_key=api_key, model=model)
        self.model = model or self.DEFAULT_MODEL
        self._call_count = 0
    
    async def initialize(self) -> None:
        """Initialize mock provider."""
        await asyncio.sleep(0.1)  # Simulate initialization delay
        self._is_initialized = True
    
    async def generate_answer(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> GenerationResult:
        """Generate mock answer.
        
        Args:
            prompt: Input prompt
            config: Generation configuration
            
        Returns:
            GenerationResult with mock text
        """
        self._ensure_initialized()
        config = self._validate_config(config)
        self._call_count += 1
        
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # Generate mock response
        mock_response = self._generate_mock_response(prompt)
        
        # Estimate tokens (rough approximation: 4 chars per token)
        prompt_tokens = len(prompt) // 4
        completion_tokens = len(mock_response) // 4
        
        return GenerationResult(
            text=mock_response,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            model=self.model,
            finish_reason="stop",
            metadata={
                "call_count": self._call_count,
                "mock": True
            }
        )
    
    async def generate_answer_stream(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> AsyncGenerator[str, None]:
        """Generate mock answer with streaming.
        
        Args:
            prompt: Input prompt
            config: Generation configuration
            
        Yields:
            Chunks of generated text
        """
        self._ensure_initialized()
        config = self._validate_config(config)
        self._call_count += 1
        
        mock_response = self._generate_mock_response(prompt)
        chunk_size = 10
        
        for i in range(0, len(mock_response), chunk_size):
            chunk = mock_response[i:i + chunk_size]
            await asyncio.sleep(0.05)  # Simulate streaming delay
            yield chunk
    
    async def summarize(
        self,
        text: str,
        max_length: int = 200,
        style: str = "concise"
    ) -> GenerationResult:
        """Generate mock summary.
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length
            style: Summary style
            
        Returns:
            GenerationResult with mock summary
        """
        self._ensure_initialized()
        
        await asyncio.sleep(0.3)
        
        summary = f"[MOCK SUMMARY - {style}]: This is a simulated summary of the provided text. "
        summary += f"The original text was {len(text)} characters long. "
        summary += "Key points would be extracted and summarized here in a real implementation."
        
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return GenerationResult(
            text=summary,
            prompt_tokens=len(text) // 4,
            completion_tokens=len(summary) // 4,
            total_tokens=(len(text) + len(summary)) // 4,
            model=self.model,
            finish_reason="stop",
            metadata={"mock": True, "style": style}
        )
    
    async def generate_structured_output(
        self,
        prompt: str,
        schema_definition: Dict[str, Any],
        config: Optional[GenerationConfig] = None
    ) -> Dict[str, Any]:
        """Generate mock structured output.
        
        Args:
            prompt: Input prompt
            schema_definition: JSON schema for output
            config: Generation configuration
            
        Returns:
            Mock structured output
        """
        self._ensure_initialized()
        
        await asyncio.sleep(0.4)
        
        # Generate mock structured data based on schema
        result = {}
        
        if "properties" in schema_definition:
            for prop_name, prop_def in schema_definition["properties"].items():
                prop_type = prop_def.get("type", "string")
                
                if prop_type == "string":
                    result[prop_name] = f"mock_{prop_name}_value"
                elif prop_type == "number":
                    result[prop_name] = 42.0
                elif prop_type == "integer":
                    result[prop_name] = 42
                elif prop_type == "boolean":
                    result[prop_name] = True
                elif prop_type == "array":
                    result[prop_name] = ["item1", "item2"]
                elif prop_type == "object":
                    result[prop_name] = {"nested": "value"}
        
        return result
    
    async def health_check(self) -> bool:
        """Check if mock provider is healthy.
        
        Returns:
            Always True for mock
        """
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get mock model information.
        
        Returns:
            Model information dictionary
        """
        return {
            "provider": "mock",
            "model": self.model,
            "api_version": "mock-v1",
            "capabilities": [
                "text_generation",
                "streaming",
                "summarization",
                "structured_output"
            ],
            "initialized": self._is_initialized,
            "call_count": self._call_count,
            "status": "mock"
        }
    
    def _generate_mock_response(self, prompt: str) -> str:
        """Generate a mock response based on prompt.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Mock response text
        """
        responses = [
            "This is a mock response generated for testing purposes. In a real implementation, "
            "this would be replaced with actual LLM-generated content.",
            
            "Based on the context provided, here is a simulated answer. The RAG engine would "
            "normally process the retrieved context and generate a grounded response with citations.",
            
            "[MOCK RESPONSE]: This demonstrates the structure of a typical AI response. "
            "Real responses would be more detailed and contextually relevant."
        ]
        
        # Select response based on prompt length
        index = len(prompt) % len(responses)
        return responses[index]
