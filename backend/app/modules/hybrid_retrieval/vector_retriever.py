"""Vector retriever using Qdrant for semantic search."""

import time
import uuid
from typing import List, Dict, Any, Optional
from app.modules.hybrid_retrieval.schemas import (
    EvidenceItem,
    EvidenceSet,
    RetrievalStatus
)
from app.modules.hybrid_retrieval.enums import EvidenceSource, EvidenceType
from app.modules.hybrid_retrieval.exceptions import VectorRetrievalException, SearchTimeoutException
from app.modules.hybrid_retrieval.constants import (
    DEFAULT_VECTOR_TOP_K,
    DEFAULT_VECTOR_SCORE_THRESHOLD,
    MAX_VECTOR_TOP_K,
    VECTOR_RETRIEVAL_TIMEOUT,
    SOURCE_VECTOR,
    LOG_VECTOR_RETRIEVAL
)
from app.modules.embedding_pipeline.search import SemanticSearchEngine
from app.modules.embedding_pipeline.schemas import SearchRequest
from app.core.logging import setup_logging

logger = setup_logging()


class VectorRetriever:
    """Retriever for vector-based semantic search using Qdrant."""
    
    def __init__(self):
        """Initialize vector retriever."""
        self.search_engine = SemanticSearchEngine()
    
    def retrieve(
        self,
        query: str,
        top_k: int = DEFAULT_VECTOR_TOP_K,
        score_threshold: float = DEFAULT_VECTOR_SCORE_THRESHOLD,
        filters: Optional[Dict[str, Any]] = None,
        timeout: float = VECTOR_RETRIEVAL_TIMEOUT
    ) -> EvidenceSet:
        """Retrieve relevant chunks using vector search.
        
        Args:
            query: Search query
            top_k: Number of results to retrieve
            score_threshold: Minimum similarity score
            filters: Metadata filters
            timeout: Retrieval timeout in seconds
            
        Returns:
            Evidence set with vector search results
            
        Raises:
            VectorRetrievalException: If retrieval fails
            SearchTimeoutException: If retrieval times out
        """
        start_time = time.time()
        
        try:
            # Validate parameters
            top_k = min(max(top_k, 1), MAX_VECTOR_TOP_K)
            score_threshold = max(min(score_threshold, 1.0), 0.0)
            
            # Build search request
            search_request = SearchRequest(
                query=query,
                limit=top_k,
                score_threshold=score_threshold
            )
            
            # Apply filters if provided
            if filters:
                self._apply_filters(search_request, filters)
            
            # Perform search with timeout
            search_results = self._search_with_timeout(search_request, timeout)
            
            # Convert to evidence items
            evidence_items = self._convert_to_evidence(search_results, start_time)
            
            retrieval_time_ms = (time.time() - start_time) * 1000
            
            evidence_set = EvidenceSet(
                source=EvidenceSource.VECTOR,
                evidence_items=evidence_items,
                total_count=len(evidence_items),
                retrieval_time_ms=retrieval_time_ms,
                status=RetrievalStatus.COMPLETED,
                error_message=None
            )
            
            logger.info(
                f"Vector retrieval completed: {len(evidence_items)} results in {retrieval_time_ms:.2f}ms "
                f"for query: {query[:50]}..."
            )
            
            return evidence_set
            
        except SearchTimeoutException:
            raise
        except Exception as e:
            logger.error(f"Vector retrieval failed: {e}")
            retrieval_time_ms = (time.time() - start_time) * 1000
            
            return EvidenceSet(
                source=EvidenceSource.VECTOR,
                evidence_items=[],
                total_count=0,
                retrieval_time_ms=retrieval_time_ms,
                status=RetrievalStatus.FAILED,
                error_message=str(e)
            )
    
    def _apply_filters(self, search_request: SearchRequest, filters: Dict[str, Any]):
        """Apply metadata filters to search request.
        
        Args:
            search_request: Search request to modify
            filters: Filter parameters
        """
        if 'document_id' in filters:
            search_request.document_id = filters['document_id']
        
        if 'document_type' in filters:
            from app.modules.hybrid_retrieval.enums import DocumentType
            search_request.document_type = DocumentType(filters['document_type'])
        
        if 'equipment' in filters:
            search_request.equipment = filters['equipment']
        
        if 'entity_type' in filters:
            from app.modules.hybrid_retrieval.enums import EntityType
            search_request.entity_type = EntityType(filters['entity_type'])
        
        if 'relationship_type' in filters:
            from app.modules.hybrid_retrieval.enums import RelationshipType
            search_request.relationship_type = RelationshipType(filters['relationship_type'])
        
        if 'section' in filters:
            search_request.section = filters['section']
        
        if 'confidence_min' in filters:
            search_request.confidence_min = filters['confidence_min']
    
    def _search_with_timeout(self, search_request: SearchRequest, timeout: float) -> Any:
        """Perform search with timeout.
        
        Args:
            search_request: Search request
            timeout: Timeout in seconds
            
        Returns:
            Search results
            
        Raises:
            SearchTimeoutException: If search times out
        """
        import signal
        
        def timeout_handler(signum, frame):
            raise SearchTimeoutException(
                f"Vector retrieval timeout after {timeout}s",
                source=SOURCE_VECTOR,
                timeout=timeout
            )
        
        # Set timeout signal
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout))
        
        try:
            results = self.search_engine.search(search_request)
            signal.alarm(0)  # Cancel alarm
            return results
        except Exception as e:
            signal.alarm(0)  # Cancel alarm
            if isinstance(e, SearchTimeoutException):
                raise
            raise VectorRetrievalException(f"Search failed: {str(e)}")
    
    def _convert_to_evidence(self, search_results: Any, start_time: float) -> List[EvidenceItem]:
        """Convert search results to evidence items.
        
        Args:
            search_results: Search results from engine
            start_time: Start time for retrieval
            
        Returns:
            List of evidence items
        """
        evidence_items = []
        
        for i, result in enumerate(search_results.results):
            evidence_id = str(uuid.uuid4())
            
            evidence_item = EvidenceItem(
                evidence_id=evidence_id,
                evidence_type=EvidenceType.CHUNK,
                source=EvidenceSource.VECTOR,
                score=result.score,
                confidence=None,
                content=result.chunk_text,
                chunk_text=result.chunk_text,
                document_id=result.document_id,
                chunk_id=result.chunk_id,
                entity_id=None,
                relationship_id=None,
                graph_node_id=None,
                metadata={
                    'page_number': result.page_number,
                    'section_title': result.section_title,
                    'document_type': result.document_type,
                    'equipment_entities': result.equipment_entities,
                    'component_entities': result.component_entities,
                    'entity_ids': result.entity_ids,
                    'relationship_ids': result.relationship_ids,
                    'ranking_position': i + 1
                },
                retrieval_time_ms=None,
                ranking_position=i + 1
            )
            
            evidence_items.append(evidence_item)
        
        return evidence_items
    
    def retrieve_by_document(
        self,
        document_id: str,
        query: str,
        top_k: int = DEFAULT_VECTOR_TOP_K,
        score_threshold: float = DEFAULT_VECTOR_SCORE_THRESHOLD
    ) -> EvidenceSet:
        """Retrieve chunks from a specific document.
        
        Args:
            document_id: Document ID to search within
            query: Search query
            top_k: Number of results
            score_threshold: Minimum similarity score
            
        Returns:
            Evidence set with document-specific results
        """
        filters = {'document_id': document_id}
        return self.retrieve(query, top_k, score_threshold, filters)
    
    def retrieve_by_entity(
        self,
        entity_id: str,
        query: str,
        top_k: int = DEFAULT_VECTOR_TOP_K
    ) -> EvidenceSet:
        """Retrieve chunks containing a specific entity.
        
        Args:
            entity_id: Entity ID to filter by
            query: Search query
            top_k: Number of results
            
        Returns:
            Evidence set with entity-specific results
        """
        filters = {'entity_id': entity_id}
        return self.retrieve(query, top_k, filters=filters)
    
    def retrieve_hybrid(
        self,
        query: str,
        entity_ids: List[str] = None,
        document_ids: List[str] = None,
        top_k: int = DEFAULT_VECTOR_TOP_K,
        score_threshold: float = DEFAULT_VECTOR_SCORE_THRESHOLD
    ) -> EvidenceSet:
        """Retrieve with hybrid filters (entities + documents).
        
        Args:
            query: Search query
            entity_ids: Entity IDs to filter by
            document_ids: Document IDs to filter by
            top_k: Number of results
            score_threshold: Minimum similarity score
            
        Returns:
            Evidence set with hybrid filtered results
        """
        filters = {}
        if entity_ids:
            filters['entity_ids'] = entity_ids
        if document_ids:
            filters['document_ids'] = document_ids
        
        return self.retrieve(query, top_k, score_threshold, filters)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get vector retriever statistics.
        
        Returns:
            Statistics dictionary
        """
        # This would return statistics about the vector retriever
        # For now, return basic info
        return {
            'source': SOURCE_VECTOR,
            'engine': 'SemanticSearchEngine',
            'status': 'operational'
        }
