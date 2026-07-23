"""REST API routes for RAG Engine module."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.config.database import get_db
from app.api.dependencies import get_current_active_user
from app.modules.rag_engine.service import RAGService
from app.models.user import User
from app.modules.rag_engine.schemas import (
    GenerationRequest,
    GenerationResponse,
    SummarizeRequest,
    StructuredOutputRequest,
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    ProviderInfo,
    HealthCheckResponse,
    DebugResponse
)
from app.core.logging import setup_logging

logger = setup_logging()

router = APIRouter(prefix="/rag", tags=["RAG Engine"])


def get_rag_service(db: Session = Depends(get_db)) -> RAGService:
    """Dependency to get RAG service instance.
    
    Args:
        db: Database session
        
    Returns:
        RAGService instance
    """
    return RAGService(db)


# Generation Endpoints

@router.post("/generate", response_model=GenerationResponse, status_code=status.HTTP_200_OK)
async def generate_answer(
    request: GenerationRequest,
    service: RAGService = Depends(get_rag_service),
    current_user: User = Depends(get_current_active_user)
):
    """Generate an answer using RAG.
    
    Args:
        request: Generation request
        service: RAG service
        
    Returns:
        Generation response
    """
    try:
        return await service.generate_answer(request)
    except Exception as e:
        logger.error(f"Generation endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/generate/stream")
async def generate_answer_stream(
    request: GenerationRequest,
    service: RAGService = Depends(get_rag_service),
    current_user: User = Depends(get_current_active_user)
):
    """Generate an answer with streaming.
    
    Args:
        request: Generation request
        service: RAG service
        
    Returns:
        Streaming response
    """
    async def stream_generator():
        try:
            async for chunk in service.generate_answer_stream(request):
                yield f"data: {chunk.model_dump_json()}\n\n"
        except Exception as e:
            logger.error(f"Streaming generation error: {e}")
            yield f"data: {{\"error\": \"{str(e)}\", \"done\": true}}\n\n"
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/summarize")
async def summarize_text(
    request: SummarizeRequest,
    service: RAGService = Depends(get_rag_service),
    current_user: User = Depends(get_current_active_user)
):
    """Summarize text.
    
    Args:
        request: Summarization request
        service: RAG service
        
    Returns:
        Summary text
    """
    try:
        summary = await service.summarize(request.text, request.max_length, request.style)
        return {"summary": summary}
    except Exception as e:
        logger.error(f"Summarization endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/structured")
async def generate_structured_output(
    request: StructuredOutputRequest,
    service: RAGService = Depends(get_rag_service),
    current_user: User = Depends(get_current_active_user)
):
    """Generate structured output.
    
    Args:
        request: Structured output request
        service: RAG service
        
    Returns:
        Structured output
    """
    try:
        output = await service.generate_structured_output(
            request.question,
            request.context_package,
            request.schema_definition,
            request.provider
        )
        return {"output": output}
    except Exception as e:
        logger.error(f"Structured output endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Conversation Endpoints

@router.post("/conversation/start", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def start_conversation(
    request: ConversationCreate,
    service: RAGService = Depends(get_rag_service),
    current_user: User = Depends(get_current_active_user)
):
    """Start a new conversation.
    
    Args:
        request: Conversation creation request
        service: RAG service
        
    Returns:
        Conversation response
    """
    try:
        return service.create_conversation(
            user_id=request.user_id,
            title=request.title,
            metadata=request.metadata
        )
    except Exception as e:
        logger.error(f"Conversation creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/conversation/message", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_conversation_message(
    conversation_id: str,
    request: MessageCreate,
    service: RAGService = Depends(get_rag_service),
    current_user: User = Depends(get_current_active_user)
):
    """Add a message to a conversation.
    
    Args:
        conversation_id: Conversation ID
        request: Message creation request
        service: RAG service
        
    Returns:
        Message response
    """
    try:
        return service.add_message(
            conversation_id=conversation_id,
            role=request.role,
            content=request.content,
            metadata=request.metadata
        )
    except Exception as e:
        logger.error(f"Message addition error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/conversation/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    service: RAGService = Depends(get_rag_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get conversation by ID.
    
    Args:
        conversation_id: Conversation ID
        service: RAG service
        
    Returns:
        Conversation response
    """
    conversation = service.get_conversation(conversation_id)
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return conversation


@router.delete("/conversation/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    service: RAGService = Depends(get_rag_service),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a conversation.
    
    Args:
        conversation_id: Conversation ID
        service: RAG service
        
    Returns:
        No content
    """
    success = service.delete_conversation(conversation_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )


# Provider and Configuration Endpoints

@router.get("/providers", response_model=list[ProviderInfo])
async def get_providers(service: RAGService = Depends(get_rag_service), current_user: User = Depends(get_current_active_user)):
    """Get available LLM providers.
    
    Args:
        service: RAG service
        
    Returns:
        List of provider information
    """
    try:
        return await service.get_providers()
    except Exception as e:
        logger.error(f"Providers endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/config")
async def get_config():
    """Get RAG engine configuration.
    
    Returns:
        Configuration dictionary
    """
    from app.config.settings import settings
    
    return {
        "llm_provider": settings.llm_provider,
        "max_context_tokens": settings.max_context_tokens,
        "max_response_tokens": settings.max_response_tokens,
        "temperature": settings.temperature,
        "top_p": settings.top_p,
        "gemini_model": settings.gemini_model,
        "openai_model": settings.openai_model,
        "ollama_model": settings.ollama_model,
        "ollama_url": settings.ollama_url
    }


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(service: RAGService = Depends(get_rag_service)):
    """Perform health check on RAG engine.
    
    Args:
        service: RAG service
        
    Returns:
        Health check response
    """
    try:
        return await service.health_check()
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Debug Endpoint

@router.post("/debug", response_model=DebugResponse)
async def debug_generation(
    request: GenerationRequest,
    service: RAGService = Depends(get_rag_service),
    current_user: User = Depends(get_current_active_user)
):
    """Generate with debug information.
    
    Args:
        request: Generation request
        service: RAG service
        
    Returns:
        Debug response
    """
    try:
        return await service.debug_generation(request)
    except Exception as e:
        logger.error(f"Debug generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
