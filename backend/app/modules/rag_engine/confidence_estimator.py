"""Confidence estimator for RAG Engine."""

from typing import Dict, Any, List
from app.core.logging import setup_logging
from app.modules.rag_engine.constants import (
    CONFIDENCE_THRESHOLD_HIGH,
    CONFIDENCE_THRESHOLD_MEDIUM,
    CONFIDENCE_THRESHOLD_LOW
)
from app.modules.rag_engine.exceptions import ConfidenceException
from app.modules.rag_engine.schemas import ConfidenceScores

logger = setup_logging()


class ConfidenceEstimator:
    """Estimate confidence scores for RAG responses."""
    
    def __init__(self):
        """Initialize confidence estimator."""
        self.weights = {
            'retrieval': 0.4,
            'evidence': 0.3,
            'entity': 0.15,
            'relationship': 0.15
        }
    
    def estimate_confidence(
        self,
        context_package: Dict[str, Any],
        response_text: str,
        citations: List[Any]
    ) -> ConfidenceScores:
        """Estimate overall confidence for the response.
        
        Args:
            context_package: Context package from hybrid retrieval
            response_text: Generated response text
            citations: List of citations
            
        Returns:
            ConfidenceScores object
        """
        try:
            # Calculate individual confidence components
            retrieval_confidence = self._estimate_retrieval_confidence(context_package)
            evidence_confidence = self._estimate_evidence_confidence(context_package, citations)
            entity_confidence = self._estimate_entity_confidence(context_package)
            relationship_confidence = self._estimate_relationship_confidence(context_package)
            
            # Calculate reasoning confidence based on response characteristics
            reasoning_confidence = self._estimate_reasoning_confidence(response_text, context_package)
            
            # Calculate overall confidence
            overall_confidence = (
                retrieval_confidence * self.weights['retrieval'] +
                evidence_confidence * self.weights['evidence'] +
                entity_confidence * self.weights['entity'] +
                relationship_confidence * self.weights['relationship']
            )
            
            # Adjust overall confidence based on reasoning
            overall_confidence = (overall_confidence + reasoning_confidence) / 2
            
            return ConfidenceScores(
                overall=round(overall_confidence, 3),
                evidence=round(evidence_confidence, 3),
                retrieval=round(retrieval_confidence, 3),
                reasoning=round(reasoning_confidence, 3)
            )
            
        except Exception as e:
            logger.error(f"Confidence estimation failed: {e}")
            raise ConfidenceException(f"Failed to estimate confidence: {str(e)}")
    
    def _estimate_retrieval_confidence(self, context_package: Dict[str, Any]) -> float:
        """Estimate confidence based on retrieval quality.
        
        Args:
            context_package: Context package
            
        Returns:
            Retrieval confidence score (0-1)
        """
        chunks = context_package.get('retrieved_chunks', [])
        
        if not chunks:
            return 0.0
        
        # Average chunk scores
        scores = [chunk.get('score', 0.0) for chunk in chunks]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        # Adjust based on number of chunks (more chunks = better coverage)
        chunk_count_factor = min(len(chunks) / 5.0, 1.0)  # Cap at 5 chunks
        
        return avg_score * 0.7 + chunk_count_factor * 0.3
    
    def _estimate_evidence_confidence(
        self,
        context_package: Dict[str, Any],
        citations: List[Any]
    ) -> float:
        """Estimate confidence based on evidence quality.
        
        Args:
            context_package: Context package
            citations: List of citations
            
        Returns:
            Evidence confidence score (0-1)
        """
        chunks = context_package.get('retrieved_chunks', [])
        
        if not chunks:
            return 0.0
        
        # Base confidence from chunk scores
        chunk_scores = [chunk.get('score', 0.0) for chunk in chunks]
        avg_chunk_score = sum(chunk_scores) / len(chunk_scores) if chunk_scores else 0.0
        
        # Boost if citations are present
        citation_boost = min(len(citations) / 3.0, 1.0) * 0.2
        
        # Check for evidence agreement
        evidence_agreement = self._check_evidence_agreement(chunks)
        
        return avg_chunk_score * 0.6 + citation_boost + evidence_agreement * 0.2
    
    def _estimate_entity_confidence(self, context_package: Dict[str, Any]) -> float:
        """Estimate confidence based on entity extraction quality.
        
        Args:
            context_package: Context package
            
        Returns:
            Entity confidence score (0-1)
        """
        entities = context_package.get('entities', [])
        
        if not entities:
            return 0.5  # Neutral if no entities
        
        # Average entity confidence
        entity_confidences = [entity.get('confidence', 0.0) for entity in entities]
        avg_entity_confidence = sum(entity_confidences) / len(entity_confidences) if entity_confidences else 0.0
        
        # Adjust based on entity count (more entities = more context)
        entity_count_factor = min(len(entities) / 10.0, 1.0) * 0.3
        
        return avg_entity_confidence * 0.7 + entity_count_factor
    
    def _estimate_relationship_confidence(self, context_package: Dict[str, Any]) -> float:
        """Estimate confidence based on relationship extraction quality.
        
        Args:
            context_package: Context package
            
        Returns:
            Relationship confidence score (0-1)
        """
        relationships = context_package.get('relationships', [])
        
        if not relationships:
            return 0.5  # Neutral if no relationships
        
        # Average relationship confidence
        rel_confidences = [rel.get('confidence', 0.0) for rel in relationships]
        avg_rel_confidence = sum(rel_confidences) / len(rel_confidences) if rel_confidences else 0.0
        
        # Adjust based on relationship count
        rel_count_factor = min(len(relationships) / 5.0, 1.0) * 0.3
        
        return avg_rel_confidence * 0.7 + rel_count_factor
    
    def _estimate_reasoning_confidence(self, response_text: str, context_package: Dict[str, Any]) -> float:
        """Estimate confidence based on reasoning quality.
        
        Args:
            response_text: Generated response
            context_package: Context package
            
        Returns:
            Reasoning confidence score (0-1)
        """
        if not response_text:
            return 0.0
        
        confidence = 0.5  # Base confidence
        
        # Check for uncertainty indicators
        uncertainty_phrases = [
            "i don't know", "not sure", "unclear", "insufficient information",
            "cannot determine", "not available", "unknown"
        ]
        
        response_lower = response_text.lower()
        for phrase in uncertainty_phrases:
            if phrase in response_lower:
                confidence -= 0.2
        
        # Check for confident language
        confident_phrases = [
            "based on", "according to", "the data shows", "evidence indicates",
            "clearly", "definitely", "certainly"
        ]
        
        for phrase in confident_phrases:
            if phrase in response_lower:
                confidence += 0.1
        
        # Check for citations
        if '[' in response_text and ']' in response_text:
            confidence += 0.15
        
        # Check response length (too short = less confident)
        if len(response_text) < 50:
            confidence -= 0.1
        elif len(response_text) > 200:
            confidence += 0.1
        
        # Clamp to valid range
        return max(0.0, min(1.0, confidence))
    
    def _check_evidence_agreement(self, chunks: List[Dict[str, Any]]) -> float:
        """Check if evidence from different chunks agrees.
        
        Args:
            chunks: List of chunks
            
        Returns:
            Agreement score (0-1)
        """
        if len(chunks) < 2:
            return 1.0  # No disagreement possible with single chunk
        
        # Simple heuristic: check if scores are consistent
        scores = [chunk.get('score', 0.0) for chunk in chunks]
        
        if not scores:
            return 0.5
        
        # Calculate variance
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        
        # Lower variance = higher agreement
        agreement = max(0.0, 1.0 - variance)
        
        return agreement
    
    def get_confidence_level(self, confidence: float) -> str:
        """Get confidence level label.
        
        Args:
            confidence: Confidence score (0-1)
            
        Returns:
            Confidence level label
        """
        if confidence >= CONFIDENCE_THRESHOLD_HIGH:
            return "high"
        elif confidence >= CONFIDENCE_THRESHOLD_MEDIUM:
            return "medium"
        elif confidence >= CONFIDENCE_THRESHOLD_LOW:
            return "low"
        else:
            return "very_low"
    
    def is_confidence_sufficient(self, confidence: float, threshold: float = 0.5) -> bool:
        """Check if confidence is sufficient.
        
        Args:
            confidence: Confidence score
            threshold: Minimum threshold
            
        Returns:
            True if sufficient
        """
        return confidence >= threshold
