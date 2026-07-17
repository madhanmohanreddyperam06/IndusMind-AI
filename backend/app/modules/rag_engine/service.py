"""Service layer for RAG Engine module."""

import time
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.core.logging import setup_logging
from app.config.settings import settings
from app.modules.rag_engine.llm.provider_factory import ProviderFactory
from app.modules.rag_engine.llm.base_provider import GenerationConfig
from app.modules.rag_engine.prompt_builder import PromptBuilder
from app.modules.rag_engine.context_formatter import ContextFormatter
from app.modules.rag_engine.citation_manager import CitationManager
from app.modules.rag_engine.confidence_estimator import ConfidenceEstimator
from app.modules.rag_engine.hallucination_guard import HallucinationGuard
from app.modules.rag_engine.response_formatter import ResponseFormatter
from app.modules.rag_engine.repository import RAGRepository
from app.modules.rag_engine.schemas import (
    GenerationRequest,
    GenerationResponse,
    ConfidenceScores,
    GenerationStatistics,
    ConversationResponse,
    MessageResponse,
    ProviderInfo,
    HealthCheckResponse,
    DebugResponse
)
from app.modules.rag_engine.exceptions import (
    GenerationException,
    InsufficientEvidenceException,
    HallucinationException
)

logger = setup_logging()


class RAGService:
    """Service for RAG generation operations."""
    
    def __init__(self, db: Session):
        """Initialize RAG service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.repository = RAGRepository(db)
        
        # Initialize components
        self.prompt_builder = PromptBuilder()
        self.context_formatter = ContextFormatter()
        self.citation_manager = CitationManager()
        self.confidence_estimator = ConfidenceEstimator()
        self.hallucination_guard = HallucinationGuard()
        self.response_formatter = ResponseFormatter()
        
        # Processing steps tracking
        self.processing_steps = []
    
    async def generate_answer(
        self,
        request: GenerationRequest
    ) -> GenerationResponse:
        """Generate an answer using RAG.
        
        Args:
            request: Generation request
            
        Returns:
            Generation response
        """
        start_time = time.time()
        processing_steps = []
        errors = []
        
        try:
            # Step 1: Validate context
            processing_steps.append({"step": "validation", "status": "started"})
            if not self.hallucination_guard.validate_before_generation(request.context_package):
                raise InsufficientEvidenceException("Insufficient context for generation")
            processing_steps.append({"step": "validation", "status": "completed"})
            
            # Step 2: Build prompt
            processing_steps.append({"step": "prompt_building", "status": "started"})
            conversation_history = None
            if request.conversation_id:
                conversation_history = self.repository.get_conversation_history(request.conversation_id)
            
            prompt = self.prompt_builder.build_prompt(
                question=request.question,
                context_package=request.context_package,
                conversation_history=conversation_history
            )
            
            # Log prompt
            self.repository.log_prompt(
                conversation_id=request.conversation_id,
                question=request.question,
                system_prompt=self.prompt_builder.system_prompt,
                user_prompt=prompt,
                context_sections=self.context_formatter.get_context_summary(request.context_package),
                prompt_length=len(prompt),
                estimated_tokens=self.context_formatter.estimate_tokens(prompt)
            )
            processing_steps.append({"step": "prompt_building", "status": "completed"})
            
            # Step 3: Get provider
            processing_steps.append({"step": "provider_initialization", "status": "started"})
            provider = await ProviderFactory.initialize_provider(request.provider)
            processing_steps.append({"step": "provider_initialization", "status": "completed"})
            
            # Step 4: Generate response
            processing_steps.append({"step": "generation", "status": "started"})
            config = GenerationConfig(
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            result = await provider.generate_answer(prompt, config)
            answer = result.text
            processing_steps.append({"step": "generation", "status": "completed"})
            
            # Step 5: Extract citations
            processing_steps.append({"step": "citation_extraction", "status": "started"})
            citations = self.citation_manager.extract_citations_from_response(
                answer,
                request.context_package
            )
            processing_steps.append({"step": "citation_extraction", "status": "completed"})
            
            # Step 6: Estimate confidence
            processing_steps.append({"step": "confidence_estimation", "status": "started"})
            confidence_scores = self.confidence_estimator.estimate_confidence(
                request.context_package,
                answer,
                citations
            )
            processing_steps.append({"step": "confidence_estimation", "status": "completed"})
            
            # Step 7: Check for hallucinations
            processing_steps.append({"step": "hallucination_check", "status": "started"})
            hallucination_check = self.hallucination_guard.check_response(
                answer,
                request.context_package,
                {
                    'overall': confidence_scores.overall,
                    'evidence': confidence_scores.evidence,
                    'retrieval': confidence_scores.retrieval,
                    'reasoning': confidence_scores.reasoning
                }
            )
            
            if self.hallucination_guard.should_block_response(hallucination_check):
                fallback = self.hallucination_guard.get_fallback_response(hallucination_check)
                logger.warning(f"Response blocked: {hallucination_check['issues']}")
                answer = fallback
            processing_steps.append({"step": "hallucination_check", "status": "completed"})
            
            # Step 8: Format response
            processing_steps.append({"step": "response_formatting", "status": "started"})
            processing_time_ms = (time.time() - start_time) * 1000
            
            statistics = GenerationStatistics(
                processing_time_ms=processing_time_ms,
                prompt_tokens=result.prompt_tokens,
                completion_tokens=result.completion_tokens,
                total_tokens=result.total_tokens,
                context_size=len(str(request.context_package)),
                evidence_count=len(request.context_package.get('retrieved_chunks', [])),
                citation_count=len(citations),
                provider=provider.provider_name
            )
            
            response = self.response_formatter.format_response(
                answer=answer,
                context_package=request.context_package,
                citations=citations,
                confidence_scores=confidence_scores,
                statistics=statistics,
                conversation_id=request.conversation_id
            )
            processing_steps.append({"step": "response_formatting", "status": "completed"})
            
            # Step 9: Log generation
            self.repository.log_generation(
                conversation_id=request.conversation_id,
                question=request.question,
                context_size=statistics.context_size,
                evidence_count=statistics.evidence_count,
                provider=statistics.provider,
                prompt_tokens=statistics.prompt_tokens,
                completion_tokens=statistics.completion_tokens,
                total_tokens=statistics.total_tokens,
                latency_ms=statistics.processing_time_ms,
                confidence=confidence_scores.overall,
                citations_count=statistics.citation_count,
                success=True
            )
            
            # Step 10: Add to conversation if provided
            if request.conversation_id:
                self.repository.add_message(
                    conversation_id=request.conversation_id,
                    role='user',
                    content=request.question
                )
                self.repository.add_message(
                    conversation_id=request.conversation_id,
                    role='assistant',
                    content=answer,
                    tokens=statistics.completion_tokens
                )
            
            logger.info(f"Generated answer in {processing_time_ms:.2f}ms with confidence {confidence_scores.overall:.3f}")
            
            return response
            
        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000
            errors.append(str(e))
            
            # Log failed generation
            self.repository.log_generation(
                conversation_id=request.conversation_id,
                question=request.question,
                context_size=len(str(request.context_package)),
                evidence_count=len(request.context_package.get('retrieved_chunks', [])),
                provider=request.provider or 'unknown',
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                latency_ms=processing_time_ms,
                confidence=0.0,
                citations_count=0,
                success=False,
                error_message=str(e)
            )
            
            logger.error(f"Generation failed: {e}")
            raise GenerationException(f"Failed to generate answer: {str(e)}")
    
    async def generate_answer_stream(
        self,
        request: GenerationRequest
    ):
        """Generate an answer with streaming.
        
        Args:
            request: Generation request
            
        Yields:
            Streaming response chunks
        """
        start_time = time.time()
        
        try:
            # Validate context
            if not self.hallucination_guard.validate_before_generation(request.context_package):
                yield self.response_formatter.format_streaming_chunk(
                    "I could not find sufficient supporting information.",
                    is_final=True
                )
                return
            
            # Build prompt
            conversation_history = None
            if request.conversation_id:
                conversation_history = self.repository.get_conversation_history(request.conversation_id)
            
            prompt = self.prompt_builder.build_prompt(
                question=request.question,
                context_package=request.context_package,
                conversation_history=conversation_history
            )
            
            # Get provider
            provider = await ProviderFactory.initialize_provider(request.provider)
            config = GenerationConfig(
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            # Stream response
            full_response = ""
            async for chunk in provider.generate_answer_stream(prompt, config):
                full_response += chunk
                yield self.response_formatter.format_streaming_chunk(chunk, is_final=False)
            
            # Final chunk
            yield self.response_formatter.format_streaming_chunk("", is_final=True)
            
            # Post-processing (citations, confidence, etc.)
            citations = self.citation_manager.extract_citations_from_response(
                full_response,
                request.context_package
            )
            
            confidence_scores = self.confidence_estimator.estimate_confidence(
                request.context_package,
                full_response,
                citations
            )
            
            # Log generation
            processing_time_ms = (time.time() - start_time) * 1000
            self.repository.log_generation(
                conversation_id=request.conversation_id,
                question=request.question,
                context_size=len(str(request.context_package)),
                evidence_count=len(request.context_package.get('retrieved_chunks', [])),
                provider=provider.provider_name,
                prompt_tokens=self.context_formatter.estimate_tokens(prompt),
                completion_tokens=self.context_formatter.estimate_tokens(full_response),
                total_tokens=self.context_formatter.estimate_tokens(prompt + full_response),
                latency_ms=processing_time_ms,
                confidence=confidence_scores.overall,
                citations_count=len(citations),
                success=True
            )
            
        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            yield self.response_formatter.format_streaming_chunk(
                f"Error: {str(e)}",
                is_final=True
            )
    
    async def summarize(self, text: str, max_length: int = 200, style: str = "concise") -> str:
        """Summarize text.
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length
            style: Summary style
            
        Returns:
            Summary text
        """
        provider = await ProviderFactory.initialize_provider()
        result = await provider.summarize(text, max_length, style)
        return result.text
    
    async def generate_structured_output(
        self,
        question: str,
        context_package: Dict[str, Any],
        schema_definition: Dict[str, Any],
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate structured output.
        
        Args:
            question: User question
            context_package: Context package
            schema_definition: Output schema
            provider: Provider to use
            
        Returns:
            Structured output
        """
        prompt = self.prompt_builder.build_structured_output_prompt(
            question,
            context_package,
            schema_definition
        )
        
        provider_instance = await ProviderFactory.initialize_provider(provider)
        return await provider_instance.generate_structured_output(prompt, schema_definition)
    
    # Conversation Operations
    
    def create_conversation(
        self,
        user_id: Optional[int] = None,
        title: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> ConversationResponse:
        """Create a new conversation.
        
        Args:
            user_id: User ID
            title: Conversation title
            metadata: Additional metadata
            
        Returns:
            Conversation response
        """
        conversation = self.repository.create_conversation(user_id, title, metadata)
        
        return ConversationResponse(
            conversation_id=conversation.conversation_id,
            user_id=conversation.user_id,
            title=conversation.title,
            status=conversation.status,
            metadata=conversation.metadata,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=0
        )
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationResponse]:
        """Get conversation by ID.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation response or None
        """
        conversation = self.repository.get_conversation(conversation_id)
        
        if not conversation:
            return None
        
        messages = self.repository.get_conversation_messages(conversation_id)
        
        return ConversationResponse(
            conversation_id=conversation.conversation_id,
            user_id=conversation.user_id,
            title=conversation.title,
            status=conversation.status,
            metadata=conversation.metadata,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=len(messages)
        )
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[dict] = None
    ) -> MessageResponse:
        """Add a message to conversation.
        
        Args:
            conversation_id: Conversation ID
            role: Message role
            content: Message content
            metadata: Additional metadata
            
        Returns:
            Message response
        """
        message = self.repository.add_message(conversation_id, role, content, metadata)
        
        return MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content,
            metadata=message.metadata,
            tokens=message.tokens,
            created_at=message.created_at
        )
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if deleted
        """
        return self.repository.delete_conversation(conversation_id)
    
    # Provider Operations
    
    async def get_providers(self) -> List[ProviderInfo]:
        """Get available providers.
        
        Returns:
            List of provider information
        """
        providers = []
        
        for provider_name in ProviderFactory.get_available_providers():
            try:
                info = ProviderFactory.get_provider_info(provider_name)
                providers.append(ProviderInfo(
                    name=info.get('provider', provider_name),
                    type=info.get('provider', provider_name),
                    available=info.get('status') != 'placeholder',
                    model=info.get('model'),
                    capabilities=info.get('capabilities', [])
                ))
            except Exception as e:
                logger.warning(f"Failed to get info for {provider_name}: {e}")
        
        return providers
    
    async def health_check(self) -> HealthCheckResponse:
        """Perform health check.
        
        Returns:
            Health check response
        """
        provider_status = {}
        
        for provider_name in ProviderFactory.get_available_providers():
            try:
                provider = await ProviderFactory.initialize_provider(provider_name)
                is_healthy = await provider.health_check()
                provider_status[provider_name] = is_healthy
            except Exception:
                provider_status[provider_name] = False
        
        return HealthCheckResponse(
            status="healthy" if any(provider_status.values()) else "unhealthy",
            providers=provider_status,
            database=True,  # Assuming DB is healthy if we got here
            timestamp=time.time()
        )
    
    async def debug_generation(
        self,
        request: GenerationRequest
    ) -> DebugResponse:
        """Generate with debug information.
        
        Args:
            request: Generation request
            
        Returns:
            Debug response
        """
        processing_steps = []
        errors = []
        
        try:
            # Build prompt
            prompt = self.prompt_builder.build_prompt(
                question=request.question,
                context_package=request.context_package
            )
            processing_steps.append({"step": "prompt_building", "status": "completed"})
            
            # Get provider
            provider = await ProviderFactory.initialize_provider(request.provider)
            processing_steps.append({"step": "provider_initialization", "status": "completed"})
            
            # Generate
            config = GenerationConfig(
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            result = await provider.generate_answer(prompt, config)
            processing_steps.append({"step": "generation", "status": "completed"})
            
            return DebugResponse(
                question=request.question,
                context_package=request.context_package,
                prompt=prompt,
                provider=provider.provider_name,
                raw_response=result.text,
                processing_steps=processing_steps,
                errors=errors
            )
            
        except Exception as e:
            errors.append(str(e))
            logger.error(f"Debug generation failed: {e}")
            
            return DebugResponse(
                question=request.question,
                context_package=request.context_package,
                prompt=prompt if 'prompt' in locals() else "",
                provider=request.provider or 'unknown',
                raw_response=None,
                processing_steps=processing_steps,
                errors=errors
            )
