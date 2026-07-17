"""Evidence merger for combining results from multiple sources."""

import time
from typing import List, Dict, Any
from app.modules.hybrid_retrieval.schemas import (
    EvidenceItem,
    EvidenceSet,
    RetrievalStatus
)
from app.modules.hybrid_retrieval.enums import EvidenceSource
from app.modules.hybrid_retrieval.exceptions import EvidenceMergeException
from app.modules.hybrid_retrieval.constants import LOG_EVIDENCE_MERGE
from app.core.logging import setup_logging

logger = setup_logging()


class EvidenceMerger:
    """Merger for combining evidence from multiple retrieval sources."""
    
    def __init__(self):
        """Initialize evidence merger."""
        pass
    
    def merge(self, evidence_sets: List[EvidenceSet]) -> List[EvidenceItem]:
        """Merge evidence from multiple sources.
        
        Args:
            evidence_sets: List of evidence sets from different sources
            
        Returns:
            Merged list of evidence items
            
        Raises:
            EvidenceMergeException: If merge fails
        """
        try:
            merged_evidence = []
            source_counts = {}
            
            for evidence_set in evidence_sets:
                source = evidence_set.source
                source_counts[source] = len(evidence_set.evidence_items)
                
                # Add source metadata to each evidence item
                for evidence_item in evidence_set.evidence_items:
                    # Add provenance information
                    evidence_item.metadata['retrieval_source'] = source
                    evidence_item.metadata['retrieval_time_ms'] = evidence_set.retrieval_time_ms
                    evidence_item.metadata['retrieval_status'] = evidence_set.status.value
                    
                    merged_evidence.append(evidence_item)
            
            logger.info(
                f"Merged evidence from {len(evidence_sets)} sources: "
                f"{source_counts}, total items: {len(merged_evidence)}"
            )
            
            return merged_evidence
            
        except Exception as e:
            logger.error(f"Evidence merge failed: {e}")
            raise EvidenceMergeException(f"Failed to merge evidence: {str(e)}")
    
    def merge_with_provenance(self, evidence_sets: List[EvidenceSet]) -> List[EvidenceItem]:
        """Merge evidence with detailed provenance tracking.
        
        Args:
            evidence_sets: List of evidence sets
            
        Returns:
            Merged evidence items with provenance
        """
        merged_evidence = self.merge(evidence_sets)
        
        # Add additional provenance metadata
        for i, evidence_item in enumerate(merged_evidence):
            evidence_item.metadata['merge_position'] = i
            evidence_item.metadata['total_merged_items'] = len(merged_evidence)
            evidence_item.metadata['source_count'] = len(evidence_sets)
        
        return merged_evidence
    
    def merge_by_type(self, evidence_sets: List[EvidenceSet]) -> Dict[str, List[EvidenceItem]]:
        """Merge evidence grouped by type.
        
        Args:
            evidence_sets: List of evidence sets
            
        Returns:
            Dictionary mapping evidence types to evidence lists
        """
        merged_evidence = self.merge(evidence_sets)
        
        grouped = {}
        for evidence_item in merged_evidence:
            evidence_type = evidence_item.evidence_type.value
            if evidence_type not in grouped:
                grouped[evidence_type] = []
            grouped[evidence_type].append(evidence_item)
        
        return grouped
    
    def merge_by_source(self, evidence_sets: List[EvidenceSet]) -> Dict[EvidenceSource, List[EvidenceItem]]:
        """Merge evidence grouped by source.
        
        Args:
            evidence_sets: List of evidence sets
            
        Returns:
            Dictionary mapping sources to evidence lists
        """
        grouped = {}
        for evidence_set in evidence_sets:
            grouped[evidence_set.source] = evidence_set.evidence_items
        
        return grouped
    
    def merge_with_confidence(self, evidence_sets: List[EvidenceSet]) -> List[EvidenceItem]:
        """Merge evidence and calculate combined confidence.
        
        Args:
            evidence_sets: List of evidence sets
            
        Returns:
            Merged evidence with combined confidence scores
        """
        merged_evidence = self.merge(evidence_sets)
        
        # Group by document_id or entity_id to combine confidences
        confidence_groups = {}
        
        for evidence_item in merged_evidence:
            # Use document_id or entity_id as grouping key
            key = evidence_item.document_id or evidence_item.entity_id or evidence_item.chunk_id
            
            if key not in confidence_groups:
                confidence_groups[key] = []
            confidence_groups[key].append(evidence_item)
        
        # Calculate combined confidence for each group
        for key, items in confidence_groups.items():
            if len(items) > 1:
                # Average confidence across sources
                confidences = [item.confidence or item.score for item in items]
                combined_confidence = sum(confidences) / len(confidences)
                
                # Update all items in group with combined confidence
                for item in items:
                    item.metadata['combined_confidence'] = combined_confidence
                    item.metadata['confidence_sources'] = len(items)
        
        return merged_evidence
    
    def get_merge_statistics(self, evidence_sets: List[EvidenceSet]) -> Dict[str, Any]:
        """Get statistics about the merge operation.
        
        Args:
            evidence_sets: List of evidence sets
            
        Returns:
            Merge statistics
        """
        total_items = sum(len(es.evidence_items) for es in evidence_sets)
        source_stats = {}
        
        for evidence_set in evidence_sets:
            source_stats[evidence_set.source.value] = {
                'count': len(evidence_set.evidence_items),
                'retrieval_time_ms': evidence_set.retrieval_time_ms,
                'status': evidence_set.status.value
            }
        
        return {
            'total_sources': len(evidence_sets),
            'total_items': total_items,
            'source_statistics': source_stats,
            'average_items_per_source': total_items / len(evidence_sets) if evidence_sets else 0
        }
