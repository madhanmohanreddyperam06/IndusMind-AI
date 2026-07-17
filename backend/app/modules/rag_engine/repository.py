"""Repository layer for RAG Engine module."""

from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import uuid

from app.modules.rag_engine.models import (
    Conversation,
    ConversationMessage,
    GenerationLog,
    PromptLog
)
from app.core.logging import setup_logging

logger = setup_logging()


class RAGRepository:
    """Repository for RAG Engine operations."""
    
    def __init__(self, db: Session):
        """Initialize repository.
        
        Args:
            db: Database session
        """
        self.db = db
    
    # Conversation Operations
    
    def create_conversation(
        self,
        user_id: Optional[int] = None,
        title: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Conversation:
        """Create a new conversation.
        
        Args:
            user_id: User ID
            title: Conversation title
            metadata: Additional metadata
            
        Returns:
            Created conversation
        """
        conversation_id = str(uuid.uuid4())
        
        conversation = Conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            title=title,
            status="active",
            metadata=metadata
        )
        
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        logger.info(f"Created conversation {conversation_id}")
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation or None
        """
        return self.db.query(Conversation).filter(
            Conversation.conversation_id == conversation_id
        ).first()
    
    def get_user_conversations(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Conversation]:
        """Get conversations for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of conversations
            offset: Offset for pagination
            
        Returns:
            List of conversations
        """
        return self.db.query(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.status != "deleted"
            )
        ).order_by(Conversation.updated_at.desc()).limit(limit).offset(offset).all()
    
    def update_conversation(
        self,
        conversation_id: str,
        title: Optional[str] = None,
        status: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Optional[Conversation]:
        """Update conversation.
        
        Args:
            conversation_id: Conversation ID
            title: New title
            status: New status
            metadata: New metadata
            
        Returns:
            Updated conversation or None
        """
        conversation = self.get_conversation(conversation_id)
        
        if not conversation:
            return None
        
        if title is not None:
            conversation.title = title
        if status is not None:
            conversation.status = status
        if metadata is not None:
            conversation.metadata = metadata
        
        conversation.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(conversation)
        
        logger.info(f"Updated conversation {conversation_id}")
        return conversation
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Soft delete conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if deleted
        """
        conversation = self.get_conversation(conversation_id)
        
        if not conversation:
            return False
        
        conversation.status = "deleted"
        conversation.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        logger.info(f"Deleted conversation {conversation_id}")
        return True
    
    # Message Operations
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[dict] = None,
        tokens: Optional[int] = None
    ) -> ConversationMessage:
        """Add a message to conversation.
        
        Args:
            conversation_id: Conversation ID
            role: Message role (user/assistant/system)
            content: Message content
            metadata: Additional metadata
            tokens: Token count
            
        Returns:
            Created message
        """
        message = ConversationMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata=metadata,
            tokens=tokens
        )
        
        self.db.add(message)
        
        # Update conversation timestamp
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> List[ConversationMessage]:
        """Get messages for a conversation.
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages
            
        Returns:
            List of messages
        """
        return self.db.query(ConversationMessage).filter(
            ConversationMessage.conversation_id == conversation_id
        ).order_by(ConversationMessage.created_at.asc()).limit(limit).all()
    
    def get_conversation_history(
        self,
        conversation_id: str,
        max_messages: int = 10
    ) -> List[dict]:
        """Get conversation history for prompt building.
        
        Args:
            conversation_id: Conversation ID
            max_messages: Maximum messages to include
            
        Returns:
            List of message dictionaries
        """
        messages = self.get_conversation_messages(conversation_id, max_messages)
        
        return [
            {
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.created_at.isoformat()
            }
            for msg in messages
        ]
    
    # Generation Log Operations
    
    def log_generation(
        self,
        conversation_id: Optional[str],
        question: str,
        context_size: int,
        evidence_count: int,
        provider: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        latency_ms: float,
        confidence: float,
        citations_count: int,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> GenerationLog:
        """Log a generation operation.
        
        Args:
            conversation_id: Conversation ID
            question: User question
            context_size: Context size in characters
            evidence_count: Number of evidence items
            provider: LLM provider used
            prompt_tokens: Prompt token count
            completion_tokens: Completion token count
            total_tokens: Total token count
            latency_ms: Processing time in milliseconds
            confidence: Overall confidence score
            citations_count: Number of citations
            success: Whether generation succeeded
            error_message: Error message if failed
            metadata: Additional metadata
            
        Returns:
            Created generation log
        """
        log = GenerationLog(
            conversation_id=conversation_id,
            question=question,
            context_size=context_size,
            evidence_count=evidence_count,
            provider=provider,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            confidence=confidence,
            citations_count=citations_count,
            success=1 if success else 0,
            error_message=error_message,
            metadata=metadata
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return log
    
    def get_generation_logs(
        self,
        conversation_id: Optional[str] = None,
        limit: int = 100
    ) -> List[GenerationLog]:
        """Get generation logs.
        
        Args:
            conversation_id: Optional conversation ID filter
            limit: Maximum number of logs
            
        Returns:
            List of generation logs
        """
        query = self.db.query(GenerationLog)
        
        if conversation_id:
            query = query.filter(GenerationLog.conversation_id == conversation_id)
        
        return query.order_by(GenerationLog.created_at.desc()).limit(limit).all()
    
    # Prompt Log Operations
    
    def log_prompt(
        self,
        conversation_id: Optional[str],
        question: str,
        system_prompt: Optional[str],
        user_prompt: str,
        context_sections: Optional[dict] = None,
        prompt_length: Optional[int] = None,
        estimated_tokens: Optional[int] = None
    ) -> PromptLog:
        """Log a prompt generation.
        
        Args:
            conversation_id: Conversation ID
            question: User question
            system_prompt: System prompt
            user_prompt: User prompt
            context_sections: Context sections used
            prompt_length: Prompt length in characters
            estimated_tokens: Estimated token count
            
        Returns:
            Created prompt log
        """
        log = PromptLog(
            conversation_id=conversation_id,
            question=question,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context_sections=context_sections,
            prompt_length=prompt_length,
            estimated_tokens=estimated_tokens
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return log
    
    def get_prompt_logs(
        self,
        conversation_id: Optional[str] = None,
        limit: int = 100
    ) -> List[PromptLog]:
        """Get prompt logs.
        
        Args:
            conversation_id: Optional conversation ID filter
            limit: Maximum number of logs
            
        Returns:
            List of prompt logs
        """
        query = self.db.query(PromptLog)
        
        if conversation_id:
            query = query.filter(PromptLog.conversation_id == conversation_id)
        
        return query.order_by(PromptLog.created_at.desc()).limit(limit).all()
    
    # Statistics Operations
    
    def get_generation_statistics(
        self,
        conversation_id: Optional[str] = None,
        days: int = 7
    ) -> dict:
        """Get generation statistics.
        
        Args:
            conversation_id: Optional conversation ID filter
            days: Number of days to look back
            
        Returns:
            Statistics dictionary
        """
        since_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(GenerationLog).filter(
            GenerationLog.created_at >= since_date
        )
        
        if conversation_id:
            query = query.filter(GenerationLog.conversation_id == conversation_id)
        
        logs = query.all()
        
        if not logs:
            return {
                'total_generations': 0,
                'successful_generations': 0,
                'failed_generations': 0,
                'average_latency_ms': 0,
                'average_confidence': 0,
                'total_tokens': 0,
                'provider_usage': {}
            }
        
        successful = [log for log in logs if log.success == 1]
        failed = [log for log in logs if log.success == 0]
        
        provider_usage = {}
        for log in logs:
            provider = log.provider
            provider_usage[provider] = provider_usage.get(provider, 0) + 1
        
        return {
            'total_generations': len(logs),
            'successful_generations': len(successful),
            'failed_generations': len(failed),
            'average_latency_ms': sum(log.latency_ms or 0 for log in successful) / len(successful) if successful else 0,
            'average_confidence': sum(log.confidence or 0 for log in successful) / len(successful) if successful else 0,
            'total_tokens': sum(log.total_tokens or 0 for log in logs),
            'provider_usage': provider_usage
        }
