"""Pydantic schemas for RAG Engine module."""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProviderType(str, Enum):
    """Available LLM provider types."""
    GEMINI = "gemini"
    OPENAI = "openai"
    OLLAMA = "ollama"
    MOCK = "mock"


class GenerationRequest(BaseModel):
    """Request schema for RAG generation."""
    
    question: str = Field(..., description="User question")
    context_package: Dict[str, Any] = Field(..., description="Context package from hybrid retrieval")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for multi-turn")
    provider: Optional[str] = Field(None, description="LLM provider to use")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Temperature for generation")
    max_tokens: Optional[int] = Field(2000, gt=0, description="Maximum tokens in response")
    stream: Optional[bool] = Field(False, description="Enable streaming response")
    
    @validator('question')
    def question_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Question cannot be empty")
        return v.strip()


class SummarizeRequest(BaseModel):
    """Request schema for text summarization."""
    
    text: str = Field(..., description="Text to summarize")
    max_length: Optional[int] = Field(200, gt=0, description="Maximum summary length")
    style: Optional[str] = Field("concise", description="Summary style")


class StructuredOutputRequest(BaseModel):
    """Request schema for structured output generation."""
    
    question: str = Field(..., description="User question")
    context_package: Dict[str, Any] = Field(..., description="Context package")
    schema_definition: Dict[str, Any] = Field(..., description="Output schema definition")
    provider: Optional[str] = Field(None, description="LLM provider")


class Citation(BaseModel):
    """Citation model."""
    
    document_id: str = Field(..., description="Document ID")
    chunk_id: str = Field(..., description="Chunk ID")
    page_number: Optional[int] = Field(None, description="Page number")
    section: Optional[str] = Field(None, description="Section name")
    evidence_id: Optional[str] = Field(None, description="Evidence ID")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Citation confidence")
    text: Optional[str] = Field(None, description="Cited text snippet")


class ConfidenceScores(BaseModel):
    """Confidence score breakdown."""
    
    overall: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")
    evidence: float = Field(..., ge=0.0, le=1.0, description="Evidence confidence")
    retrieval: float = Field(..., ge=0.0, le=1.0, description="Retrieval confidence")
    reasoning: float = Field(..., ge=0.0, le=1.0, description="Reasoning confidence")


class GenerationStatistics(BaseModel):
    """Generation statistics."""
    
    processing_time_ms: float = Field(..., description="Total processing time")
    prompt_tokens: int = Field(..., description="Prompt token count")
    completion_tokens: int = Field(..., description="Completion token count")
    total_tokens: int = Field(..., description="Total token count")
    context_size: int = Field(..., description="Context size in characters")
    evidence_count: int = Field(..., description="Number of evidence items")
    citation_count: int = Field(..., description="Number of citations")
    provider: str = Field(..., description="LLM provider used")


class GenerationResponse(BaseModel):
    """Response schema for RAG generation."""
    
    answer: str = Field(..., description="Generated answer")
    summary: Optional[str] = Field(None, description="Answer summary")
    citations: List[Citation] = Field(default_factory=list, description="Citations")
    supporting_documents: List[str] = Field(default_factory=list, description="Supporting document IDs")
    related_entities: List[Dict[str, Any]] = Field(default_factory=list, description="Related entities")
    related_relationships: List[Dict[str, Any]] = Field(default_factory=list, description="Related relationships")
    confidence: ConfidenceScores = Field(..., description="Confidence scores")
    follow_up_questions: List[str] = Field(default_factory=list, description="Suggested follow-up questions")
    statistics: GenerationStatistics = Field(..., description="Generation statistics")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")


class ConversationCreate(BaseModel):
    """Request schema for creating a conversation."""
    
    user_id: Optional[int] = Field(None, description="User ID")
    title: Optional[str] = Field(None, description="Conversation title")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ConversationResponse(BaseModel):
    """Response schema for conversation."""
    
    conversation_id: str = Field(..., description="Conversation ID")
    user_id: Optional[int] = Field(None, description="User ID")
    title: Optional[str] = Field(None, description="Conversation title")
    status: str = Field(..., description="Conversation status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    message_count: int = Field(..., description="Number of messages")


class MessageCreate(BaseModel):
    """Request schema for adding a message to conversation."""
    
    role: str = Field(..., description="Message role (user/assistant/system)")
    content: str = Field(..., description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MessageResponse(BaseModel):
    """Response schema for conversation message."""
    
    id: int = Field(..., description="Message ID")
    conversation_id: str = Field(..., description="Conversation ID")
    role: str = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    tokens: Optional[int] = Field(None, description="Token count")
    created_at: datetime = Field(..., description="Creation timestamp")


class ProviderConfig(BaseModel):
    """Provider configuration."""
    
    provider: str = Field(..., description="Provider name")
    api_key: Optional[str] = Field(None, description="API key")
    model: Optional[str] = Field(None, description="Model name")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature")
    max_tokens: int = Field(2000, gt=0, description="Max tokens")
    top_p: float = Field(0.9, ge=0.0, le=1.0, description="Top-p sampling")
    additional_params: Optional[Dict[str, Any]] = Field(None, description="Additional parameters")


class ProviderInfo(BaseModel):
    """Provider information."""
    
    name: str = Field(..., description="Provider name")
    type: str = Field(..., description="Provider type")
    available: bool = Field(..., description="Availability status")
    model: Optional[str] = Field(None, description="Default model")
    capabilities: List[str] = Field(default_factory=list, description="Provider capabilities")


class HealthCheckResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Overall status")
    providers: Dict[str, bool] = Field(..., description="Provider availability")
    database: bool = Field(..., description="Database connection status")
    timestamp: datetime = Field(..., description="Check timestamp")


class DebugResponse(BaseModel):
    """Debug information response."""
    
    question: str = Field(..., description="Original question")
    context_package: Dict[str, Any] = Field(..., description="Context package")
    prompt: str = Field(..., description="Generated prompt")
    provider: str = Field(..., description="Provider used")
    raw_response: Optional[str] = Field(None, description="Raw LLM response")
    processing_steps: List[Dict[str, Any]] = Field(default_factory=list, description="Processing steps")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
