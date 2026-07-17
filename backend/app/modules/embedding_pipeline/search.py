"""Semantic search engine with ranking."""

from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny
from app.modules.embedding_pipeline.embedding_generator import get_embedding_generator
from app.modules.embedding_pipeline.qdrant_repository import QdrantRepository
from app.modules.embedding_pipeline.schemas import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    RecommendRequest,
    RecommendResponse
)
from app.modules.embedding_pipeline.constants import RANKING_WEIGHTS
from app.modules.embedding_pipeline.exceptions import SearchError
from app.config.settings import settings
from app.core.logging import setup_logging
import time

logger = setup_logging()


class SemanticSearchEngine:
    """Semantic search engine with advanced ranking."""
    
    def __init__(self):
        """Initialize semantic search engine."""
        self.embedding_generator = get_embedding_generator()
        self.qdrant_repo = QdrantRepository()
        self.default_weights = RANKING_WEIGHTS.copy()
    
    def search(self, request: SearchRequest) -> SearchResponse:
        """Perform semantic search with ranking.
        
        Args:
            request: Search request
            
        Returns:
            SearchResponse
        """
        start_time = time.time()
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_generator.generate_embedding(request.query)
            
            # Build filter from request
            filter = self._build_filter(request)
            
            # Perform search in Qdrant
            raw_results = self.qdrant_repo.search(
                query_vector=query_embedding,
                limit=request.limit,
                score_threshold=request.score_threshold,
                filter=filter
            )
            
            # Apply ranking if weights are provided
            if any([
                request.weight_cosine_similarity is not None,
                request.weight_metadata_relevance is not None,
                request.weight_entity_overlap is not None,
                request.weight_relationship_overlap is not None,
                request.weight_document_freshness is not None
            ]):
                weights = {
                    "cosine_similarity": request.weight_cosine_similarity or self.default_weights["cosine_similarity"],
                    "metadata_relevance": request.weight_metadata_relevance or self.default_weights["metadata_relevance"],
                    "entity_overlap": request.weight_entity_overlap or self.default_weights["entity_overlap"],
                    "relationship_overlap": request.weight_relationship_overlap or self.default_weights["relationship_overlap"],
                    "document_freshness": request.weight_document_freshness or self.default_weights["document_freshness"]
                }
                ranked_results = self._rank_results(raw_results, request.query, weights)
                ranking_applied = True
            else:
                ranked_results = raw_results
                ranking_applied = False
            
            # Format results
            formatted_results = []
            for result in ranked_results:
                formatted_results.append(self._format_search_result(result))
            
            # Sort by score (descending)
            formatted_results.sort(key=lambda x: x.score, reverse=True)
            
            duration = time.time() - start_time
            logger.info(f"Search completed: {len(formatted_results)} results in {duration:.3f}s")
            
            return SearchResponse(
                query=request.query,
                results=formatted_results[:request.limit],
                total_results=len(formatted_results),
                duration_seconds=duration,
                ranking_applied=ranking_applied
            )
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise SearchError(f"Search failed: {str(e)}", request.query)
    
    def _build_filter(self, request: SearchRequest) -> Optional[Filter]:
        """Build Qdrant filter from search request.
        
        Args:
            request: Search request
            
        Returns:
            Qdrant Filter or None
        """
        conditions = []
        
        if request.document_id:
            conditions.append(
                FieldCondition(key="document_id", match=MatchValue(value=request.document_id))
            )
        
        if request.document_type:
            conditions.append(
                FieldCondition(key="document_type", match=MatchValue(value=request.document_type.value))
            )
        
        if request.equipment:
            conditions.append(
                FieldCondition(key="equipment_entities", match=MatchAny(any=[request.equipment]))
            )
        
        if request.section:
            conditions.append(
                FieldCondition(key="section_title", match=MatchValue(value=request.section))
            )
        
        if request.confidence_min is not None:
            # Note: Qdrant doesn't support range filters on all fields, this is a placeholder
            # In production, you might need to use a different approach
            pass
        
        if conditions:
            return Filter(must=conditions)
        
        return None
    
    def _rank_results(
        self,
        raw_results: List[Dict[str, Any]],
        query: str,
        weights: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Apply ranking to search results.
        
        Args:
            raw_results: Raw search results from Qdrant
            query: Original query text
            weights: Ranking weights
            
        Returns:
            Ranked results
        """
        ranked_results = []
        
        for result in raw_results:
            payload = result.get("payload", {})
            original_score = result.get("score", 0.0)
            
            # Calculate ranking scores
            cosine_score = original_score
            metadata_score = self._calculate_metadata_relevance(payload, query)
            entity_score = self._calculate_entity_overlap(payload, query)
            relationship_score = self._calculate_relationship_overlap(payload, query)
            freshness_score = self._calculate_document_freshness(payload)
            
            # Combine scores with weights
            final_score = (
                weights["cosine_similarity"] * cosine_score +
                weights["metadata_relevance"] * metadata_score +
                weights["entity_overlap"] * entity_score +
                weights["relationship_overlap"] * relationship_score +
                weights["document_freshness"] * freshness_score
            )
            
            # Update result with final score
            result["score"] = final_score
            result["ranking_components"] = {
                "cosine_similarity": cosine_score,
                "metadata_relevance": metadata_score,
                "entity_overlap": entity_score,
                "relationship_overlap": relationship_score,
                "document_freshness": freshness_score
            }
            
            ranked_results.append(result)
        
        return ranked_results
    
    def _calculate_metadata_relevance(self, payload: Dict[str, Any], query: str) -> float:
        """Calculate metadata relevance score.
        
        Args:
            payload: Result payload
            query: Query text
            
        Returns:
            Relevance score (0-1)
        """
        score = 0.0
        
        # Check if query terms appear in section title
        section_title = payload.get("section_title", "").lower()
        query_terms = set(query.lower().split())
        
        if section_title:
            matching_terms = len(query_terms.intersection(set(section_title.split())))
            score += (matching_terms / len(query_terms)) if query_terms else 0
        
        # Check document type relevance
        document_type = payload.get("document_type", "")
        if document_type and "manual" in document_type.lower():
            score += 0.2  # Manuals are often more relevant
        
        return min(score, 1.0)
    
    def _calculate_entity_overlap(self, payload: Dict[str, Any], query: str) -> float:
        """Calculate entity overlap score.
        
        Args:
            payload: Result payload
            query: Query text
            
        Returns:
            Entity overlap score (0-1)
        """
        entity_ids = payload.get("entity_ids", [])
        equipment_entities = payload.get("equipment_entities", [])
        
        # Simple heuristic: more entities = higher relevance
        total_entities = len(entity_ids)
        if total_entities == 0:
            return 0.0
        
        # Normalize to 0-1 range (assuming max 10 entities is high relevance)
        return min(total_entities / 10.0, 1.0)
    
    def _calculate_relationship_overlap(self, payload: Dict[str, Any], query: str) -> float:
        """Calculate relationship overlap score.
        
        Args:
            payload: Result payload
            query: Query text
            
        Returns:
            Relationship overlap score (0-1)
        """
        relationship_ids = payload.get("relationship_ids", [])
        
        # Simple heuristic: more relationships = higher relevance
        total_relationships = len(relationship_ids)
        if total_relationships == 0:
            return 0.0
        
        # Normalize to 0-1 range (assuming max 5 relationships is high relevance)
        return min(total_relationships / 5.0, 1.0)
    
    def _calculate_document_freshness(self, payload: Dict[str, Any]) -> float:
        """Calculate document freshness score.
        
        Args:
            payload: Result payload
            
        Returns:
            Freshness score (0-1)
        """
        created_at = payload.get("created_at")
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
    
    def _format_search_result(self, result: Dict[str, Any]) -> SearchResult:
        """Format raw Qdrant result as SearchResult.
        
        Args:
            result: Raw result from Qdrant
            
        Returns:
            SearchResult
        """
        payload = result.get("payload", {})
        
        return SearchResult(
            chunk_id=payload.get("chunk_id", ""),
            document_id=payload.get("document_id", ""),
            chunk_text=payload.get("chunk_text", ""),
            score=result.get("score", 0.0),
            page_number=payload.get("page_number"),
            section_title=payload.get("section_title"),
            document_type=payload.get("document_type"),
            equipment_entities=payload.get("equipment_entities", []),
            component_entities=payload.get("component_entities", []),
            entity_ids=payload.get("entity_ids", []),
            relationship_ids=payload.get("relationship_ids", []),
            metadata={
                "ranking_components": result.get("ranking_components", {}),
                "token_count": payload.get("token_count"),
                "character_count": payload.get("character_count")
            }
        )
    
    def recommend(self, request: RecommendRequest) -> RecommendResponse:
        """Recommend similar chunks based on positive/negative examples.
        
        Args:
            request: Recommendation request
            
        Returns:
            RecommendResponse
        """
        start_time = time.time()
        
        try:
            # Build filter if provided
            filter = None
            if request.filter:
                # Convert dict filter to Qdrant Filter
                conditions = []
                for key, value in request.filter.items():
                    conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=value))
                    )
                if conditions:
                    filter = Filter(must=conditions)
            
            # Perform recommendation
            raw_results = self.qdrant_repo.recommend(
                positive_ids=request.positive_ids,
                negative_ids=request.negative_ids,
                limit=request.limit,
                filter=filter
            )
            
            # Format results
            formatted_results = []
            for result in raw_results:
                formatted_results.append(self._format_search_result(result))
            
            duration = time.time() - start_time
            logger.info(f"Recommendation completed: {len(formatted_results)} results in {duration:.3f}s")
            
            return RecommendResponse(
                results=formatted_results,
                total_results=len(formatted_results),
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Recommendation error: {e}")
            raise SearchError(f"Recommendation failed: {str(e)}")
    
    def search_by_document(
        self,
        document_id: str,
        query: str,
        limit: int = 10
    ) -> SearchResponse:
        """Search within a specific document.
        
        Args:
            document_id: Document ID to search within
            query: Search query
            limit: Maximum results
            
        Returns:
            SearchResponse
        """
        request = SearchRequest(
            query=query,
            limit=limit,
            document_id=document_id
        )
        return self.search(request)
    
    def search_by_entity(
        self,
        entity_id: str,
        query: str,
        limit: int = 10
    ) -> SearchResponse:
        """Search for chunks containing a specific entity.
        
        Args:
            entity_id: Entity ID to filter by
            query: Search query
            limit: Maximum results
            
        Returns:
            SearchResponse
        """
        # Build custom filter for entity
        filter = Filter(
            must=[
                FieldCondition(key="entity_ids", match=MatchAny(any=[entity_id]))
            ]
        )
        
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        # Perform search
        raw_results = self.qdrant_repo.search(
            query_vector=query_embedding,
            limit=limit,
            filter=filter
        )
        
        # Format results
        formatted_results = []
        for result in raw_results:
            formatted_results.append(self._format_search_result(result))
        
        return SearchResponse(
            query=query,
            results=formatted_results,
            total_results=len(formatted_results),
            duration_seconds=0.0,
            ranking_applied=False
        )
    
    def hybrid_search(
        self,
        query: str,
        entity_ids: List[str] = None,
        document_ids: List[str] = None,
        limit: int = 10
    ) -> SearchResponse:
        """Hybrid search combining semantic and entity filters.
        
        Args:
            query: Search query
            entity_ids: Entity IDs to filter by
            document_ids: Document IDs to filter by
            limit: Maximum results
            
        Returns:
            SearchResponse
        """
        conditions = []
        
        if entity_ids:
            conditions.append(
                FieldCondition(key="entity_ids", match=MatchAny(any=entity_ids))
            )
        
        if document_ids:
            conditions.append(
                FieldCondition(key="document_id", match=MatchAny(any=document_ids))
            )
        
        filter = Filter(must=conditions) if conditions else None
        
        request = SearchRequest(
            query=query,
            limit=limit
        )
        
        start_time = time.time()
        
        try:
            query_embedding = self.embedding_generator.generate_embedding(query)
            
            raw_results = self.qdrant_repo.search(
                query_vector=query_embedding,
                limit=limit,
                filter=filter
            )
            
            formatted_results = []
            for result in raw_results:
                formatted_results.append(self._format_search_result(result))
            
            duration = time.time() - start_time
            
            return SearchResponse(
                query=query,
                results=formatted_results,
                total_results=len(formatted_results),
                duration_seconds=duration,
                ranking_applied=False
            )
            
        except Exception as e:
            logger.error(f"Hybrid search error: {e}")
            raise SearchError(f"Hybrid search failed: {str(e)}", query)
