"""Deduplicator for removing duplicate evidence items."""

import time
from typing import List, Dict, Any, Set
from difflib import SequenceMatcher
from app.modules.hybrid_retrieval.schemas import EvidenceItem
from app.modules.hybrid_retrieval.enums import EvidenceType, DeduplicationMethod
from app.modules.hybrid_retrieval.exceptions import DeduplicationException
from app.modules.hybrid_retrieval.constants import (
    CHUNK_SIMILARITY_THRESHOLD,
    ENTITY_SIMILARITY_THRESHOLD,
    RELATIONSHIP_SIMILARITY_THRESHOLD
)
from app.core.logging import setup_logging

logger = setup_logging()


class Deduplicator:
    """Deduplicator for removing duplicate evidence items."""
    
    def __init__(self):
        """Initialize deduplicator."""
        pass
    
    def deduplicate(
        self,
        evidence_items: List[EvidenceItem],
        method: DeduplicationMethod = DeduplicationMethod.SIMILARITY_THRESHOLD,
        chunk_threshold: float = CHUNK_SIMILARITY_THRESHOLD,
        entity_threshold: float = ENTITY_SIMILARITY_THRESHOLD,
        relationship_threshold: float = RELATIONSHIP_SIMILARITY_THRESHOLD
    ) -> List[EvidenceItem]:
        """Remove duplicate evidence items.
        
        Args:
            evidence_items: List of evidence items to deduplicate
            method: Deduplication method
            chunk_threshold: Similarity threshold for chunks
            entity_threshold: Similarity threshold for entities
            relationship_threshold: Similarity threshold for relationships
            
        Returns:
            Deduplicated list of evidence items
            
        Raises:
            DeduplicationException: If deduplication fails
        """
        try:
            if method == DeduplicationMethod.EXACT_MATCH:
                return self._deduplicate_exact_match(evidence_items)
            elif method == DeduplicationMethod.SIMILARITY_THRESHOLD:
                return self._deduplicate_similarity_threshold(
                    evidence_items,
                    chunk_threshold,
                    entity_threshold,
                    relationship_threshold
                )
            elif method == DeduplicationMethod.SEMANTIC:
                return self._deduplicate_semantic(evidence_items)
            elif method == DeduplicationMethod.HYBRID:
                return self._deduplicate_hybrid(
                    evidence_items,
                    chunk_threshold,
                    entity_threshold,
                    relationship_threshold
                )
            else:
                return self._deduplicate_exact_match(evidence_items)
                
        except Exception as e:
            logger.error(f"Deduplication failed: {e}")
            raise DeduplicationException(f"Failed to deduplicate evidence: {str(e)}")
    
    def _deduplicate_exact_match(self, evidence_items: List[EvidenceItem]) -> List[EvidenceItem]:
        """Deduplicate using exact match.
        
        Args:
            evidence_items: List of evidence items
            
        Returns:
            Deduplicated evidence items
        """
        seen = set()
        deduplicated = []
        
        for item in evidence_items:
            # Create unique key based on type and identifiers
            if item.evidence_type == EvidenceType.CHUNK:
                key = f"{item.evidence_type.value}:{item.chunk_id}:{item.document_id}"
            elif item.evidence_type == EvidenceType.ENTITY:
                key = f"{item.evidence_type.value}:{item.entity_id}"
            elif item.evidence_type == EvidenceType.RELATIONSHIP:
                key = f"{item.evidence_type.value}:{item.relationship_id}"
            elif item.evidence_type == EvidenceType.GRAPH_NODE:
                key = f"{item.evidence_type.value}:{item.graph_node_id}"
            elif item.evidence_type == EvidenceType.GRAPH_EDGE:
                key = f"{item.evidence_type.value}:{item.relationship_id}"
            else:
                key = f"{item.evidence_type.value}:{item.evidence_id}"
            
            if key not in seen:
                seen.add(key)
                deduplicated.append(item)
            else:
                # Keep the item with higher score/confidence
                existing_item = next((i for i in deduplicated if self._get_key(i) == key), None)
                if existing_item and self._is_better_item(item, existing_item):
                    deduplicated.remove(existing_item)
                    deduplicated.append(item)
        
        removed_count = len(evidence_items) - len(deduplicated)
        logger.info(f"Exact match deduplication: removed {removed_count} duplicates")
        
        return deduplicated
    
    def _deduplicate_similarity_threshold(
        self,
        evidence_items: List[EvidenceItem],
        chunk_threshold: float,
        entity_threshold: float,
        relationship_threshold: float
    ) -> List[EvidenceItem]:
        """Deduplicate using similarity threshold.
        
        Args:
            evidence_items: List of evidence items
            chunk_threshold: Chunk similarity threshold
            entity_threshold: Entity similarity threshold
            relationship_threshold: Relationship similarity threshold
            
        Returns:
            Deduplicated evidence items
        """
        deduplicated = []
        seen_contents = []
        
        for item in evidence_items:
            is_duplicate = False
            
            if item.evidence_type == EvidenceType.CHUNK:
                content = item.chunk_text or item.content
                if content:
                    for seen_content in seen_contents:
                        similarity = self._calculate_similarity(content, seen_content)
                        if similarity >= chunk_threshold:
                            is_duplicate = True
                            break
                    if not is_duplicate:
                        seen_contents.append(content)
            
            elif item.evidence_type == EvidenceType.ENTITY:
                content = item.content
                if content:
                    for seen_content in seen_contents:
                        similarity = self._calculate_similarity(content, seen_content)
                        if similarity >= entity_threshold:
                            is_duplicate = True
                            break
                    if not is_duplicate:
                        seen_contents.append(content)
            
            elif item.evidence_type == EvidenceType.RELATIONSHIP:
                content = item.content
                if content:
                    for seen_content in seen_contents:
                        similarity = self._calculate_similarity(content, seen_content)
                        if similarity >= relationship_threshold:
                            is_duplicate = True
                            break
                    if not is_duplicate:
                        seen_contents.append(content)
            
            if not is_duplicate:
                deduplicated.append(item)
        
        removed_count = len(evidence_items) - len(deduplicated)
        logger.info(f"Similarity threshold deduplication: removed {removed_count} duplicates")
        
        return deduplicated
    
    def _deduplicate_semantic(self, evidence_items: List[EvidenceItem]) -> List[EvidenceItem]:
        """Deduplicate using semantic similarity.
        
        Args:
            evidence_items: List of evidence items
            
        Returns:
            Deduplicated evidence items
        """
        # For semantic deduplication, we would use embeddings
        # For now, use similarity threshold as a proxy
        return self._deduplicate_similarity_threshold(
            evidence_items,
            CHUNK_SIMILARITY_THRESHOLD,
            ENTITY_SIMILARITY_THRESHOLD,
            RELATIONSHIP_SIMILARITY_THRESHOLD
        )
    
    def _deduplicate_hybrid(
        self,
        evidence_items: List[EvidenceItem],
        chunk_threshold: float,
        entity_threshold: float,
        relationship_threshold: float
    ) -> List[EvidenceItem]:
        """Deduplicate using hybrid method (exact + similarity).
        
        Args:
            evidence_items: List of evidence items
            chunk_threshold: Chunk similarity threshold
            entity_threshold: Entity similarity threshold
            relationship_threshold: Relationship similarity threshold
            
        Returns:
            Deduplicated evidence items
        """
        # First pass: exact match
        deduplicated = self._deduplicate_exact_match(evidence_items)
        
        # Second pass: similarity threshold
        deduplicated = self._deduplicate_similarity_threshold(
            deduplicated,
            chunk_threshold,
            entity_threshold,
            relationship_threshold
        )
        
        return deduplicated
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _get_key(self, item: EvidenceItem) -> str:
        """Get unique key for an evidence item.
        
        Args:
            item: Evidence item
            
        Returns:
            Unique key
        """
        if item.evidence_type == EvidenceType.CHUNK:
            return f"{item.evidence_type.value}:{item.chunk_id}:{item.document_id}"
        elif item.evidence_type == EvidenceType.ENTITY:
            return f"{item.evidence_type.value}:{item.entity_id}"
        elif item.evidence_type == EvidenceType.RELATIONSHIP:
            return f"{item.evidence_type.value}:{item.relationship_id}"
        elif item.evidence_type == EvidenceType.GRAPH_NODE:
            return f"{item.evidence_type.value}:{item.graph_node_id}"
        elif item.evidence_type == EvidenceType.GRAPH_EDGE:
            return f"{item.evidence_type.value}:{item.relationship_id}"
        else:
            return f"{item.evidence_type.value}:{item.evidence_id}"
    
    def _is_better_item(self, new_item: EvidenceItem, existing_item: EvidenceItem) -> bool:
        """Check if new item is better than existing item.
        
        Args:
            new_item: New evidence item
            existing_item: Existing evidence item
            
        Returns:
            True if new item is better
        """
        # Compare scores
        new_score = new_item.score or new_item.confidence or 0
        existing_score = existing_item.score or existing_item.confidence or 0
        
        if new_score > existing_score:
            return True
        
        # If scores are equal, prefer items from more reliable sources
        source_priority = {
            'vector': 4,
            'graph': 3,
            'keyword': 2,
            'metadata': 1
        }
        
        new_priority = source_priority.get(new_item.source.value, 0)
        existing_priority = source_priority.get(existing_item.source.value, 0)
        
        return new_priority > existing_priority
    
    def deduplicate_by_document(self, evidence_items: List[EvidenceItem]) -> List[EvidenceItem]:
        """Deduplicate keeping only best evidence per document.
        
        Args:
            evidence_items: List of evidence items
            
        Returns:
            Deduplicated evidence items
        """
        document_groups = {}
        
        for item in evidence_items:
            doc_id = item.document_id or 'unknown'
            if doc_id not in document_groups:
                document_groups[doc_id] = []
            document_groups[doc_id].append(item)
        
        deduplicated = []
        for doc_id, items in document_groups.items():
            # Keep the item with highest score
            best_item = max(items, key=lambda x: x.score or x.confidence or 0)
            deduplicated.append(best_item)
        
        removed_count = len(evidence_items) - len(deduplicated)
        logger.info(f"Document-based deduplication: removed {removed_count} duplicates")
        
        return deduplicated
    
    def get_deduplication_statistics(
        self,
        original_count: int,
        deduplicated_count: int
    ) -> Dict[str, Any]:
        """Get deduplication statistics.
        
        Args:
            original_count: Original number of items
            deduplicated_count: Number of items after deduplication
            
        Returns:
            Deduplication statistics
        """
        removed_count = original_count - deduplicated_count
        removal_rate = (removed_count / original_count) if original_count > 0 else 0
        
        return {
            'original_count': original_count,
            'deduplicated_count': deduplicated_count,
            'removed_count': removed_count,
            'removal_rate': removal_rate
        }
