"""Database models for RAG Engine module."""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config.database import Base


class Conversation(Base):
    """Conversation model for multi-turn interactions."""
    
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String(255), nullable=True)
    status = Column(String(50), default="active")  # active, archived, deleted
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")


class ConversationMessage(Base):
    """Message model for conversation history."""
    
    __tablename__ = "conversation_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(100), ForeignKey("conversations.conversation_id"), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    meta = Column(JSON, nullable=True)
    tokens = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class GenerationLog(Base):
    """Log for RAG generation operations."""
    
    __tablename__ = "generation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(100), ForeignKey("conversations.conversation_id"), nullable=True)
    question = Column(Text, nullable=False)
    context_size = Column(Integer, nullable=True)
    evidence_count = Column(Integer, nullable=True)
    provider = Column(String(50), nullable=False)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    latency_ms = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    citations_count = Column(Integer, nullable=True)
    success = Column(Integer, default=1)  # 1 for success, 0 for failure
    error_message = Column(Text, nullable=True)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PromptLog(Base):
    """Log for prompt generation operations."""
    
    __tablename__ = "prompt_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(100), ForeignKey("conversations.conversation_id"), nullable=True)
    question = Column(Text, nullable=False)
    system_prompt = Column(Text, nullable=True)
    user_prompt = Column(Text, nullable=False)
    context_sections = Column(JSON, nullable=True)
    prompt_length = Column(Integer, nullable=True)
    estimated_tokens = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
