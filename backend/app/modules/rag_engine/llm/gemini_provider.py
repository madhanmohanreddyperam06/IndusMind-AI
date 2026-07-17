"""Gemini LLM provider implementation."""

import asyncio
from typing import Dict, Any, Optional, AsyncGenerator
import google.generativeai as genai
from google.generativeai.types import GenerateConfig

from .base_provider import LLMProvider, GenerationConfig, GenerationResult
from app.modules.rag_engine.exceptions import ProviderException, ProviderUnavailableException


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider."""
    
    DEFAULT_MODEL = "gemini-pro"
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize Gemini provider.
        
        Args:
            api_key: Google API key
            model: Model name (defaults to gemini-pro)
        """
        super().__init__(api_key=api_key, model=model)
        self.model = model or self.DEFAULT_MODEL
        self._client: Optional[genai.GenerativeModel] = None
    
    async def initialize(self) -> None:
        """Initialize Gemini client."""
        if not self.api_key:
            raise ProviderException("Gemini API key is required")
        
        try:
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self.model)
            self._is_initialized = True
        except Exception as e:
            raise ProviderException(f"Failed to initialize Gemini: {str(e)}")
    
    async def generate_answer(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> GenerationResult:
        """Generate answer using Gemini.
        
        Args:
            prompt: Input prompt
            config: Generation configuration
            
        Returns:
            GenerationResult with generated text
        """
        self._ensure_initialized()
        config = self._validate_config(config)
        
        try:
            gemini_config = GenerateConfig(
                temperature=config.temperature,
                max_output_tokens=config.max_tokens,
                top_p=config.top_p
            )
            
            if config.additional_params:
                for key, value in config.additional_params.items():
                    setattr(gemini_config, key, value)
            
            response = await asyncio.to_thread(
                self._client.generate_content,
                prompt,
                generation_config=gemini_config
            )
            
            text = response.text
            usage = response.usage_metadata
            
            return GenerationResult(
                text=text,
                prompt_tokens=usage.prompt_token_count if usage else 0,
                completion_tokens=usage.candidates_token_count if usage else 0,
                total_tokens=usage.total_token_count if usage else 0,
                model=self.model,
                finish_reason=response.candidates[0].finish_reason.name if response.candidates else None,
                metadata={
                    "safety_ratings": [
                        {"category": rating.category.name, "probability": rating.probability.name}
                        for rating in response.candidates[0].safety_ratings
                    ] if response.candidates else []
                }
            )
        except Exception as e:
            raise ProviderException(f"Gemini generation failed: {str(e)}")
    
    async def generate_answer_stream(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> AsyncGenerator[str, None]:
        """Generate answer with streaming using Gemini.
        
        Args:
            prompt: Input prompt
            config: Generation configuration
            
        Yields:
            Chunks of generated text
        """
        self._ensure_initialized()
        config = self._validate_config(config)
        
        try:
            gemini_config = GenerateConfig(
                temperature=config.temperature,
                max_output_tokens=config.max_tokens,
                top_p=config.top_p
            )
            
            if config.additional_params:
                for key, value in config.additional_params.items():
                    setattr(gemini_config, key, value)
            
            response = await asyncio.to_thread(
                self._client.generate_content,
                prompt,
                generation_config=gemini_config,
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            raise ProviderException(f"Gemini streaming failed: {str(e)}")
    
    async def summarize(
        self,
        text: str,
        max_length: int = 200,
        style: str = "concise"
    ) -> GenerationResult:
        """Summarize text using Gemini.
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length
            style: Summary style
            
        Returns:
            GenerationResult with summary
        """
        self._ensure_initialized()
        
        style_instructions = {
            "concise": "Provide a very brief summary in 2-3 sentences.",
            "detailed": "Provide a comprehensive summary covering all key points.",
            "bullet": "Provide a summary in bullet points.",
            "executive": "Provide an executive summary suitable for business stakeholders."
        }
        
        instruction = style_instructions.get(style, style_instructions["concise"])
        prompt = f"""Summarize the following text. {instruction}

Text:
{text}

Summary:"""
        
        config = GenerationConfig(max_tokens=max_length, temperature=0.3)
        return await self.generate_answer(prompt, config)
    
    async def generate_structured_output(
        self,
        prompt: str,
        schema_definition: Dict[str, Any],
        config: Optional[GenerationConfig] = None
    ) -> Dict[str, Any]:
        """Generate structured output using Gemini.
        
        Args:
            prompt: Input prompt
            schema_definition: JSON schema for output
            config: Generation configuration
            
        Returns:
            Structured output matching schema
        """
        self._ensure_initialized()
        config = self._validate_config(config)
        
        schema_prompt = f"""Generate a response following this JSON schema:
{schema_definition}

Question:
{prompt}

Provide only the JSON response:"""
        
        result = await self.generate_answer(schema_prompt, config)
        
        try:
            import json
            return json.loads(result.text)
        except json.JSONDecodeError:
            raise ProviderException("Failed to parse structured output as JSON")
    
    async def health_check(self) -> bool:
        """Check if Gemini is available.
        
        Returns:
            True if healthy
        """
        try:
            if not self._is_initialized:
                await self.initialize()
            
            # Simple test generation
            test_response = await asyncio.to_thread(
                self._client.generate_content,
                "Hello",
                generation_config=GenerateConfig(max_output_tokens=10)
            )
            return bool(test_response.text)
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Gemini model information.
        
        Returns:
            Model information dictionary
        """
        return {
            "provider": "gemini",
            "model": self.model,
            "api_version": "v1",
            "capabilities": [
                "text_generation",
                "streaming",
                "summarization",
                "structured_output",
                "safety_filtering"
            ],
            "initialized": self._is_initialized
        }
