"""Hallucination guard for RAG Engine."""

from typing import Dict, Any, List
from app.core.logging import setup_logging
from app.modules.rag_engine.constants import (
    HALLUCINATION_THRESHOLD,
    MIN_SOURCE_COVERAGE,
    ERROR_INSUFFICIENT_EVIDENCE,
    ERROR_CONFLICTING_EVIDENCE
)
from app.modules.rag_engine.exceptions import HallucinationException, InsufficientEvidenceException

logger = setup_logging()


class HallucinationGuard:
    """Guard against hallucinations in LLM responses."""
    
    def __init__(
        self,
        hallucination_threshold: float = HALLUCINATION_THRESHOLD,
        min_source_coverage: float = MIN_SOURCE_COVERAGE
    ):
        """Initialize hallucination guard.
        
        Args:
            hallucination_threshold: Threshold for hallucination detection
            min_source_coverage: Minimum source coverage required
        """
        self.hallucination_threshold = hallucination_threshold
        self.min_source_coverage = min_source_coverage
    
    def check_response(
        self,
        response_text: str,
        context_package: Dict[str, Any],
        confidence_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """Check response for potential hallucinations.
        
        Args:
            response_text: Generated response
            context_package: Context package
            confidence_scores: Confidence scores
            
        Returns:
            Check results with potential issues
        """
        issues = []
        warnings = []
        
        # Check for insufficient evidence
        evidence_check = self._check_evidence_sufficiency(context_package, confidence_scores)
        if not evidence_check['sufficient']:
            issues.append(evidence_check['message'])
        
        # Check for conflicting evidence
        conflict_check = self._check_evidence_conflict(context_package)
        if conflict_check['has_conflict']:
            warnings.append(conflict_check['message'])
        
        # Check for source coverage
        coverage_check = self._check_source_coverage(response_text, context_package)
        if coverage_check['coverage'] < self.min_source_coverage:
            warnings.append(f"Low source coverage: {coverage_check['coverage']:.2%}")
        
        # Check for unsupported claims
        unsupported_check = self._check_unsupported_claims(response_text, context_package)
        if unsupported_check['has_unsupported']:
            warnings.append(f"Potential unsupported claims detected: {unsupported_check['count']}")
        
        # Check for confidence
        overall_confidence = confidence_scores.get('overall', 0.0)
        if overall_confidence < self.hallucination_threshold:
            warnings.append(f"Low confidence: {overall_confidence:.3f}")
        
        return {
            'passed': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'should_block': len(issues) > 0
        }
    
    def _check_evidence_sufficiency(
        self,
        context_package: Dict[str, Any],
        confidence_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """Check if there's sufficient evidence.
        
        Args:
            context_package: Context package
            confidence_scores: Confidence scores
            
        Returns:
            Evidence sufficiency check result
        """
        chunks = context_package.get('retrieved_chunks', [])
        
        # Check minimum chunk count
        if len(chunks) < 1:
            return {
                'sufficient': False,
                'message': ERROR_INSUFFICIENT_EVIDENCE,
                'reason': 'no_chunks'
            }
        
        # Check chunk quality
        avg_score = sum(chunk.get('score', 0.0) for chunk in chunks) / len(chunks)
        if avg_score < 0.3:
            return {
                'sufficient': False,
                'message': ERROR_INSUFFICIENT_EVIDENCE,
                'reason': 'low_chunk_quality'
            }
        
        # Check evidence confidence
        evidence_confidence = confidence_scores.get('evidence', 0.0)
        if evidence_confidence < 0.3:
            return {
                'sufficient': False,
                'message': ERROR_INSUFFICIENT_EVIDENCE,
                'reason': 'low_evidence_confidence'
            }
        
        return {
            'sufficient': True,
            'message': 'Evidence is sufficient',
            'reason': 'passed'
        }
    
    def _check_evidence_conflict(self, context_package: Dict[str, Any]) -> Dict[str, Any]:
        """Check for conflicting evidence.
        
        Args:
            context_package: Context package
            
        Returns:
            Conflict check result
        """
        chunks = context_package.get('retrieved_chunks', [])
        
        if len(chunks) < 2:
            return {'has_conflict': False, 'message': 'No conflict possible with single chunk'}
        
        # Simple heuristic: check for score variance
        scores = [chunk.get('score', 0.0) for chunk in chunks]
        avg_score = sum(scores) / len(scores)
        
        # Check for outliers
        outliers = [s for s in scores if abs(s - avg_score) > 0.3]
        
        if len(outliers) > len(scores) / 2:
            return {
                'has_conflict': True,
                'message': ERROR_CONFLICTING_EVIDENCE,
                'outlier_count': len(outliers)
            }
        
        return {
            'has_conflict': False,
            'message': 'No significant conflicts detected'
        }
    
    def _check_source_coverage(
        self,
        response_text: str,
        context_package: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check how much of the response is covered by sources.
        
        Args:
            response_text: Generated response
            context_package: Context package
            
        Returns:
            Coverage check result
        """
        if not response_text:
            return {'coverage': 0.0, 'covered_words': 0, 'total_words': 0}
        
        chunks = context_package.get('retrieved_chunks', [])
        if not chunks:
            return {'coverage': 0.0, 'covered_words': 0, 'total_words': 0}
        
        # Get all source text
        source_text = ' '.join(chunk.get('text', '') for chunk in chunks)
        source_words = set(source_text.lower().split())
        
        # Get response words
        response_words = response_text.lower().split()
        
        # Calculate coverage
        covered_words = sum(1 for word in response_words if word in source_words)
        coverage = covered_words / len(response_words) if response_words else 0.0
        
        return {
            'coverage': coverage,
            'covered_words': covered_words,
            'total_words': len(response_words)
        }
    
    def _check_unsupported_claims(
        self,
        response_text: str,
        context_package: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check for unsupported claims in response.
        
        Args:
            response_text: Generated response
            context_package: Context package
            
        Returns:
            Unsupported claims check result
        """
        # This is a simplified check - in production, use more sophisticated NLP
        unsupported_indicators = [
            'i believe', 'i think', 'probably', 'likely', 'possibly',
            'might be', 'could be', 'seems like', 'appears to be'
        ]
        
        response_lower = response_text.lower()
        unsupported_count = sum(1 for indicator in unsupported_indicators if indicator in response_lower)
        
        return {
            'has_unsupported': unsupported_count > 0,
            'count': unsupported_count
        }
    
    def should_block_response(self, check_result: Dict[str, Any]) -> bool:
        """Determine if response should be blocked.
        
        Args:
            check_result: Result from check_response
            
        Returns:
            True if should block
        """
        return check_result.get('should_block', False)
    
    def get_fallback_response(self, check_result: Dict[str, Any]) -> str:
        """Get fallback response when blocking.
        
        Args:
            check_result: Result from check_response
            
        Returns:
            Fallback response text
        """
        if 'insufficient evidence' in ' '.join(check_result.get('issues', [])):
            return ERROR_INSUFFICIENT_EVIDENCE
        
        if 'conflicting evidence' in ' '.join(check_result.get('issues', [])):
            return ERROR_CONFLICTING_EVIDENCE
        
        return "I could not generate a reliable response based on the available information."
    
    def validate_before_generation(self, context_package: Dict[str, Any]) -> bool:
        """Validate context before generation.
        
        Args:
            context_package: Context package
            
        Returns:
            True if validation passes
        """
        chunks = context_package.get('retrieved_chunks', [])
        
        if not chunks:
            logger.warning("No chunks in context package")
            return False
        
        if len(chunks) < 1:
            logger.warning("Insufficient chunks for generation")
            return False
        
        return True
