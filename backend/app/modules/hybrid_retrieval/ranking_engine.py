"""Ranking engine for scoring and ranking evidence items."""

import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.modules.hybrid_retrieval.schemas import EvidenceItem
from app.modules.hybrid_retrieval.enums import RankingMethod, EvidenceSource
from app.modules.hybrid_retrieval.exceptions import RankingException
from app.modules.hybrid_retrieval.constants import DEFAULT_RANKING_WEIGHTS
from app.core.logging import setup_logging

logger = setup_logging()


class RankingEngine:
    """Engine for ranking evidence items using multiple signals."""
    
    def __init__(self):
        """Initialize ranking engine."""
        self.default_weights = DEFAULT_RANKING_WEIGHTS.copy()
    
    def rank(
        self,
        evidence_items: List[EvidenceItem],
        method: RankingMethod = RankingMethod.WEIGHTED_SCORE,
        weights: Optional[Dict[str, float]] = None,
        query: Optional[str] = None
    ) -> List[EvidenceItem]:
        """Rank evidence items using specified method.
        
        Args:
            evidence_items: List of evidence items to rank
            method: Ranking method
            weights: Custom ranking weights
            query: Original query for relevance calculation
            
        Returns:
            Ranked evidence items
            
        Raises:
            RankingException: If ranking fails
        """
        try:
            if method == RankingMethod.WEIGHTED_SCORE:
                return self._rank_weighted_score(evidence_items, weights, query)
            elif method == RankingMethod.RECIPROCAL_RANK_FUSION:
                return self._rank_rrf(evidence_items)
            elif method == RankingMethod.LEARNING_TO_RANK:
                return self._rank_ltr(evidence_items)
            elif method == RankingMethod.HYBRID:
                return self._rank_hybrid(evidence_items, weights, query)
            else:
                return self._rank_weighted_score(evidence_items, weights, query)
                
        except Exception as e:
            logger.error(f"Ranking failed: {e}")
            raise RankingException(f"Failed to rank evidence: {str(e)}")
    
    def _rank_weighted_score(
        self,
        evidence_items: List[EvidenceItem],
        weights: Optional[Dict[str, float]],
        query: Optional[str]
    ) -> List[EvidenceItem]:
        """Rank using weighted score combination.
        
        Args:
            evidence_items: List of evidence items
            weights: Custom weights
            query: Query for relevance calculation
            
        Returns:
            Ranked evidence items
        """
        # Use custom weights or defaults
        ranking_weights = weights or self.default_weights
        
        # Normalize weights to sum to 1.0
        total_weight = sum(ranking_weights.values())
        if total_weight > 0:
            ranking_weights = {k: v / total_weight for k, v in ranking_weights.items()}
        
        # Calculate combined scores
        for item in evidence_items:
            combined_score = self._calculate_combined_score(
                item,
                ranking_weights,
                query
            )
            item.metadata['combined_score'] = combined_score
            item.metadata['ranking_components'] = self._get_ranking_components(
                item,
                ranking_weights,
                query
            )
            # Update the main score
            item.score = combined_score
        
        # Sort by combined score (descending)
        ranked = sorted(evidence_items, key=lambda x: x.score, reverse=True)
        
        # Update ranking positions
        for i, item in enumerate(ranked):
            item.ranking_position = i + 1
        
        logger.info(f"Weighted score ranking completed for {len(ranked)} items")
        
        return ranked
    
    def _calculate_combined_score(
        self,
        item: EvidenceItem,
        weights: Dict[str, float],
        query: Optional[str]
    ) -> float:
        """Calculate combined score for an evidence item.
        
        Args:
            item: Evidence item
            weights: Ranking weights
            query: Query for relevance
            
        Returns:
            Combined score
        """
        # Get individual component scores
        vector_score = self._get_vector_score(item)
        graph_score = self._get_graph_score(item)
        keyword_score = self._get_keyword_score(item)
        metadata_score = self._get_metadata_score(item)
        entity_overlap_score = self._get_entity_overlap_score(item)
        relationship_overlap_score = self._get_relationship_overlap_score(item)
        freshness_score = self._get_freshness_score(item)
        
        # Calculate weighted combination
        combined = (
            weights.get('vector_similarity', 0) * vector_score +
            weights.get('graph_proximity', 0) * graph_score +
            weights.get('keyword_relevance', 0) * keyword_score +
            weights.get('metadata_relevance', 0) * metadata_score +
            weights.get('entity_overlap', 0) * entity_overlap_score +
            weights.get('relationship_overlap', 0) * relationship_overlap_score +
            weights.get('document_freshness', 0) * freshness_score
        )
        
        return combined
    
    def _get_vector_score(self, item: EvidenceItem) -> float:
        """Get vector similarity score.
        
        Args:
            item: Evidence item
            
        Returns:
            Vector score (0-1)
        """
        if item.source == EvidenceSource.VECTOR:
            return item.score
        return 0.0
    
    def _get_graph_score(self, item: EvidenceItem) -> float:
        """Get graph proximity score.
        
        Args:
            item: Evidence item
            
        Returns:
            Graph score (0-1)
        """
        if item.source == EvidenceSource.GRAPH:
            return item.score
        return 0.0
    
    def _get_keyword_score(self, item: EvidenceItem) -> float:
        """Get keyword relevance score.
        
        Args:
            item: Evidence item
            
        Returns:
            Keyword score (0-1)
        """
        if item.source == EvidenceSource.KEYWORD:
            return item.score
        return 0.0
    
    def _get_metadata_score(self, item: EvidenceItem) -> float:
        """Get metadata relevance score.
        
        Args:
            item: Evidence item
            
        Returns:
            Metadata score (0-1)
        """
        if item.source == EvidenceSource.METADATA:
            return item.score
        return 0.0
    
    def _get_entity_overlap_score(self, item: EvidenceItem) -> float:
        """Calculate entity overlap score.
        
        Args:
            item: Evidence item
            
        Returns:
            Entity overlap score (0-1)
        """
        entity_ids = item.metadata.get('entity_ids', [])
        if not entity_ids:
            return 0.0
        
        # Normalize based on number of entities (assuming max 10 is high relevance)
        return min(len(entity_ids) / 10.0, 1.0)
    
    def _get_relationship_overlap_score(self, item: EvidenceItem) -> float:
        """Calculate relationship overlap score.
        
        Args:
            item: Evidence item
            
        Returns:
            Relationship overlap score (0-1)
        """
        relationship_ids = item.metadata.get('relationship_ids', [])
        if not relationship_ids:
            return 0.0
        
        # Normalize based on number of relationships (assuming max 5 is high relevance)
        return min(len(relationship_ids) / 5.0, 1.0)
    
    def _get_freshness_score(self, item: EvidenceItem) -> float:
        """Calculate document freshness score.
        
        Args:
            item: Evidence item
            
        Returns:
            Freshness score (0-1)
        """
        created_at = item.metadata.get('created_at')
        if not created_at:
            return 0.5  # Neutral score if no timestamp
        
        try:
            created_date = datetime.fromisoformat(created_at)
            days_old = (datetime.utcnow() - created_date).days
            
            # Fresher documents get higher scores
            # 0 days = 1.0, 365 days = 0.0
            freshness = max(0, 1 - (days_old / 365))
            return freshness
        except:
            return 0.5
    
    def _get_ranking_components(
        self,
        item: EvidenceItem,
        weights: Dict[str, float],
        query: Optional[str]
    ) -> Dict[str, float]:
        """Get individual ranking component scores.
        
        Args:
            item: Evidence item
            weights: Ranking weights
            query: Query
            
        Returns:
            Dictionary of component scores
        """
        return {
            'vector_similarity': self._get_vector_score(item),
            'graph_proximity': self._get_graph_score(item),
            'keyword_relevance': self._get_keyword_score(item),
            'metadata_relevance': self._get_metadata_score(item),
            'entity_overlap': self._get_entity_overlap_score(item),
            'relationship_overlap': self._get_relationship_overlap_score(item),
            'document_freshness': self._get_freshness_score(item)
        }
    
    def _rank_rrf(self, evidence_items: List[EvidenceItem]) -> List[EvidenceItem]:
        """Rank using Reciprocal Rank Fusion.
        
        Args:
            evidence_items: List of evidence items
            
        Returns:
            Ranked evidence items
        """
        # Group by source
        source_rankings = {}
        for item in evidence_items:
            source = item.source.value
            if source not in source_rankings:
                source_rankings[source] = []
            source_rankings[source].append(item)
        
        # Calculate RRF scores
        k = 60  # RRF constant
        rrf_scores = {}
        
        for source, items in source_rankings.items():
            # Sort by original score within source
            sorted_items = sorted(items, key=lambda x: x.score, reverse=True)
            
            for rank, item in enumerate(sorted_items):
                item_id = item.evidence_id
                if item_id not in rrf_scores:
                    rrf_scores[item_id] = 0
                rrf_scores[item_id] += 1.0 / (k + rank + 1)
        
        # Apply RRF scores
        for item in evidence_items:
            item.score = rrf_scores.get(item.evidence_id, 0.0)
        
        # Sort by RRF score
        ranked = sorted(evidence_items, key=lambda x: x.score, reverse=True)
        
        # Update ranking positions
        for i, item in enumerate(ranked):
            item.ranking_position = i + 1
        
        logger.info(f"RRF ranking completed for {len(ranked)} items")
        
        return ranked
    
    def _rank_ltr(self, evidence_items: List[EvidenceItem]) -> List[EvidenceItem]:
        """Rank using Learning to Rank (placeholder).
        
        Args:
            evidence_items: List of evidence items
            
        Returns:
            Ranked evidence items
        """
        # LTR would require a trained model
        # For now, fall back to weighted score
        logger.warning("LTR not implemented, falling back to weighted score")
        return self._rank_weighted_score(evidence_items, None, None)
    
    def _rank_hybrid(
        self,
        evidence_items: List[EvidenceItem],
        weights: Optional[Dict[str, float]],
        query: Optional[str]
    ) -> List[EvidenceItem]:
        """Rank using hybrid method (weighted + RRF).
        
        Args:
            evidence_items: List of evidence items
            weights: Custom weights
            query: Query
            
        Returns:
            Ranked evidence items
        """
        # First pass: weighted score
        weighted_ranked = self._rank_weighted_score(evidence_items, weights, query)
        
        # Second pass: RRF
        rrf_ranked = self._rank_rrf(evidence_items)
        
        # Combine scores (average)
        weighted_scores = {item.evidence_id: item.score for item in weighted_ranked}
        rrf_scores = {item.evidence_id: item.score for item in rrf_ranked}
        
        combined_scores = {}
        for item_id in set(weighted_scores.keys()) | set(rrf_scores.keys()):
            w_score = weighted_scores.get(item_id, 0)
            r_score = rrf_scores.get(item_id, 0)
            combined_scores[item_id] = (w_score + r_score) / 2
        
        # Apply combined scores
        for item in evidence_items:
            item.score = combined_scores.get(item.evidence_id, 0.0)
        
        # Sort by combined score
        ranked = sorted(evidence_items, key=lambda x: x.score, reverse=True)
        
        # Update ranking positions
        for i, item in enumerate(ranked):
            item.ranking_position = i + 1
        
        logger.info(f"Hybrid ranking completed for {len(ranked)} items")
        
        return ranked
    
    def rank_by_source(self, evidence_items: List[EvidenceItem]) -> Dict[EvidenceSource, List[EvidenceItem]]:
        """Rank evidence items grouped by source.
        
        Args:
            evidence_items: List of evidence items
            
        Returns:
            Dictionary mapping sources to ranked items
        """
        # Group by source
        source_groups = {}
        for item in evidence_items:
            source = item.source
            if source not in source_groups:
                source_groups[source] = []
            source_groups[source].append(item)
        
        # Rank each group
        ranked_groups = {}
        for source, items in source_groups.items():
            ranked_groups[source] = self._rank(items, RankingMethod.WEIGHTED_SCORE)
        
        return ranked_groups
    
    def get_ranking_statistics(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Get ranking statistics.
        
        Args:
            evidence_items: Ranked evidence items
            
        Returns:
            Ranking statistics
        """
        if not evidence_items:
            return {
                'total_items': 0,
                'average_score': 0,
                'score_distribution': {}
            }
        
        scores = [item.score for item in evidence_items]
        
        return {
            'total_items': len(evidence_items),
            'average_score': sum(scores) / len(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'score_distribution': {
                'high': len([s for s in scores if s >= 0.8]),
                'medium': len([s for s in scores if 0.5 <= s < 0.8]),
                'low': len([s for s in scores if s < 0.5])
            }
        }
