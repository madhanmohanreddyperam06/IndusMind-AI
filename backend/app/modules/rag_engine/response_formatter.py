"""Response formatter for RAG Engine."""

from typing import Dict, Any, List
from app.core.logging import setup_logging
from app.modules.rag_engine.exceptions import ResponseFormatException
from app.modules.rag_engine.schemas import (
    GenerationResponse,
    Citation,
    ConfidenceScores,
    GenerationStatistics
)

logger = setup_logging()


class ResponseFormatter:
    """Format structured responses from RAG generation."""
    
    def __init__(self):
        """Initialize response formatter."""
        pass
    
    def format_response(
        self,
        answer: str,
        context_package: Dict[str, Any],
        citations: List[Citation],
        confidence_scores: ConfidenceScores,
        statistics: GenerationStatistics,
        conversation_id: str = None
    ) -> GenerationResponse:
        """Format a complete structured response.
        
        Args:
            answer: Generated answer text
            context_package: Context package
            citations: List of citations
            confidence_scores: Confidence scores
            statistics: Generation statistics
            conversation_id: Conversation ID
            
        Returns:
            Formatted GenerationResponse
        """
        try:
            # Generate summary
            summary = self._generate_summary(answer)
            
            # Extract supporting documents
            supporting_documents = self._extract_supporting_documents(citations)
            
            # Extract related entities
            related_entities = context_package.get('entities', [])[:10]
            
            # Extract related relationships
            related_relationships = context_package.get('relationships', [])[:10]
            
            # Generate follow-up questions
            follow_up_questions = self._generate_follow_up_questions(
                context_package.get('question', ''),
                context_package
            )
            
            return GenerationResponse(
                answer=answer,
                summary=summary,
                citations=citations,
                supporting_documents=supporting_documents,
                related_entities=related_entities,
                related_relationships=related_relationships,
                confidence=confidence_scores,
                follow_up_questions=follow_up_questions,
                statistics=statistics,
                conversation_id=conversation_id
            )
            
        except Exception as e:
            logger.error(f"Response formatting failed: {e}")
            raise ResponseFormatException(f"Failed to format response: {str(e)}")
    
    def _generate_summary(self, answer: str, max_length: int = 200) -> str:
        """Generate a summary of the answer.
        
        Args:
            answer: Full answer text
            max_length: Maximum summary length
            
        Returns:
            Summary text
        """
        if not answer:
            return ""
        
        # Simple extractive summarization
        sentences = answer.split('. ')
        
        # Take first 2-3 sentences
        summary_sentences = sentences[:3]
        summary = '. '.join(summary_sentences)
        
        # Truncate if too long
        if len(summary) > max_length:
            summary = summary[:max_length - 3] + "..."
        
        return summary.strip()
    
    def _extract_supporting_documents(self, citations: List[Citation]) -> List[str]:
        """Extract unique document IDs from citations.
        
        Args:
            citations: List of citations
            
        Returns:
            List of unique document IDs
        """
        doc_ids = set()
        for citation in citations:
            doc_ids.add(citation.document_id)
        
        return list(doc_ids)
    
    def _generate_follow_up_questions(
        self,
        question: str,
        context_package: Dict[str, Any]
    ) -> List[str]:
        """Generate suggested follow-up questions.
        
        Args:
            question: Original question
            context_package: Context package
            
        Returns:
            List of follow-up questions
        """
        follow_ups = []
        
        # Generate based on entities
        entities = context_package.get('entities', [])[:5]
        for entity in entities[:3]:
            entity_name = entity.get('name', '')
            entity_type = entity.get('type', '')
            if entity_name:
                follow_ups.append(f"What is the role of {entity_name} in this context?")
        
        # Generate based on relationships
        relationships = context_package.get('relationships', [])[:3]
        for rel in relationships[:2]:
            source = rel.get('source', '')
            target = rel.get('target', '')
            rel_type = rel.get('type', '')
            if source and target:
                follow_ups.append(f"How does {source} relate to {target}?")
        
        # Generic follow-ups
        if len(follow_ups) < 3:
            follow_ups.append("Can you provide more details about the key factors?")
            follow_ups.append("What are the implications of these findings?")
        
        return follow_ups[:5]  # Limit to 5 questions
    
    def format_error_response(
        self,
        error_message: str,
        error_type: str = "generation_error"
    ) -> Dict[str, Any]:
        """Format an error response.
        
        Args:
            error_message: Error message
            error_type: Type of error
            
        Returns:
            Error response dictionary
        """
        return {
            "error": True,
            "error_type": error_type,
            "message": error_message,
            "answer": error_message,
            "confidence": {
                "overall": 0.0,
                "evidence": 0.0,
                "retrieval": 0.0,
                "reasoning": 0.0
            },
            "statistics": {
                "processing_time_ms": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "context_size": 0,
                "evidence_count": 0,
                "citation_count": 0,
                "provider": "unknown"
            }
        }
    
    def format_streaming_chunk(self, chunk: str, is_final: bool = False) -> Dict[str, Any]:
        """Format a streaming response chunk.
        
        Args:
            chunk: Text chunk
            is_final: Whether this is the final chunk
            
        Returns:
            Formatted chunk dictionary
        """
        return {
            "chunk": chunk,
            "is_final": is_final,
            "done": is_final
        }
    
    def format_debug_response(
        self,
        question: str,
        context_package: Dict[str, Any],
        prompt: str,
        provider: str,
        raw_response: str,
        processing_steps: List[Dict[str, Any]],
        errors: List[str]
    ) -> Dict[str, Any]:
        """Format a debug response with detailed information.
        
        Args:
            question: Original question
            context_package: Context package
            prompt: Generated prompt
            provider: Provider used
            raw_response: Raw LLM response
            processing_steps: List of processing steps
            errors: List of errors
            
        Returns:
            Debug response dictionary
        """
        return {
            "question": question,
            "context_package": context_package,
            "prompt": prompt,
            "provider": provider,
            "raw_response": raw_response,
            "processing_steps": processing_steps,
            "errors": errors,
            "context_summary": {
                "chunks_count": len(context_package.get('retrieved_chunks', [])),
                "entities_count": len(context_package.get('entities', [])),
                "relationships_count": len(context_package.get('relationships', [])),
                "has_graph": 'graph_context' in context_package
            }
        }
    
    def validate_response_structure(self, response: Dict[str, Any]) -> bool:
        """Validate response structure.
        
        Args:
            response: Response dictionary
            
        Returns:
            True if valid
        """
        required_fields = ['answer', 'confidence', 'statistics']
        
        for field in required_fields:
            if field not in response:
                logger.warning(f"Missing required field in response: {field}")
                return False
        
        return True
