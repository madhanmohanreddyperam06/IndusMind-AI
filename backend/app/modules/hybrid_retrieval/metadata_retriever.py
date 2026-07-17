"""Metadata retriever for filtering by document metadata."""

import time
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.modules.hybrid_retrieval.schemas import (
    EvidenceItem,
    EvidenceSet,
    RetrievalStatus
)
from app.modules.hybrid_retrieval.enums import EvidenceSource, EvidenceType
from app.modules.hybrid_retrieval.exceptions import MetadataRetrievalException, SearchTimeoutException
from app.modules.hybrid_retrieval.constants import (
    DEFAULT_METADATA_LIMIT,
    MAX_METADATA_LIMIT,
    METADATA_RETRIEVAL_TIMEOUT,
    SOURCE_METADATA,
    LOG_METADATA_RETRIEVAL
)
from app.core.logging import setup_logging

logger = setup_logging()


class MetadataRetriever:
    """Retriever for metadata-based filtering."""
    
    def __init__(self, db: Session = None):
        """Initialize metadata retriever.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def retrieve(
        self,
        filters: Dict[str, Any],
        limit: int = DEFAULT_METADATA_LIMIT,
        timeout: float = METADATA_RETRIEVAL_TIMEOUT
    ) -> EvidenceSet:
        """Retrieve documents/chunks by metadata filters.
        
        Args:
            filters: Metadata filter criteria
            limit: Maximum results
            timeout: Retrieval timeout in seconds
            
        Returns:
            Evidence set with metadata-filtered results
            
        Raises:
            MetadataRetrievalException: If retrieval fails
            SearchTimeoutException: If retrieval times out
        """
        start_time = time.time()
        
        try:
            # Validate parameters
            limit = min(max(limit, 1), MAX_METADATA_LIMIT)
            
            # Perform metadata search with timeout
            results = self._search_with_timeout(filters, limit, timeout)
            
            # Convert to evidence items
            evidence_items = self._convert_to_evidence(results, start_time)
            
            retrieval_time_ms = (time.time() - start_time) * 1000
            
            evidence_set = EvidenceSet(
                source=EvidenceSource.METADATA,
                evidence_items=evidence_items,
                total_count=len(evidence_items),
                retrieval_time_ms=retrieval_time_ms,
                status=RetrievalStatus.COMPLETED,
                error_message=None
            )
            
            logger.info(
                f"Metadata retrieval completed: {len(evidence_items)} results in {retrieval_time_ms:.2f}ms "
                f"with filters: {list(filters.keys())}"
            )
            
            return evidence_set
            
        except SearchTimeoutException:
            raise
        except Exception as e:
            logger.error(f"Metadata retrieval failed: {e}")
            retrieval_time_ms = (time.time() - start_time) * 1000
            
            return EvidenceSet(
                source=EvidenceSource.METADATA,
                evidence_items=[],
                total_count=0,
                retrieval_time_ms=retrieval_time_ms,
                status=RetrievalStatus.FAILED,
                error_message=str(e)
            )
    
    def retrieve_by_equipment(
        self,
        equipment_name: str,
        limit: int = DEFAULT_METADATA_LIMIT,
        timeout: float = METADATA_RETRIEVAL_TIMEOUT
    ) -> EvidenceSet:
        """Retrieve documents by equipment reference.
        
        Args:
            equipment_name: Equipment name
            limit: Maximum results
            timeout: Retrieval timeout
            
        Returns:
            Evidence set with equipment-related results
        """
        filters = {'equipment': equipment_name}
        return self.retrieve(filters, limit, timeout)
    
    def retrieve_by_document_type(
        self,
        document_type: str,
        limit: int = DEFAULT_METADATA_LIMIT,
        timeout: float = METADATA_RETRIEVAL_TIMEOUT
    ) -> EvidenceSet:
        """Retrieve documents by type.
        
        Args:
            document_type: Document type
            limit: Maximum results
            timeout: Retrieval timeout
            
        Returns:
            Evidence set with document type results
        """
        filters = {'document_type': document_type}
        return self.retrieve(filters, limit, timeout)
    
    def retrieve_by_department(
        self,
        department: str,
        limit: int = DEFAULT_METADATA_LIMIT,
        timeout: float = METADATA_RETRIEVAL_TIMEOUT
    ) -> EvidenceSet:
        """Retrieve documents by department.
        
        Args:
            department: Department name
            limit: Maximum results
            timeout: Retrieval timeout
            
        Returns:
            Evidence set with department-related results
        """
        filters = {'department': department}
        return self.retrieve(filters, limit, timeout)
    
    def retrieve_by_date_range(
        self,
        start_date: str,
        end_date: str,
        limit: int = DEFAULT_METADATA_LIMIT,
        timeout: float = METADATA_RETRIEVAL_TIMEOUT
    ) -> EvidenceSet:
        """Retrieve documents by date range.
        
        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            limit: Maximum results
            timeout: Retrieval timeout
            
        Returns:
            Evidence set with date-filtered results
        """
        filters = {'start_date': start_date, 'end_date': end_date}
        return self.retrieve(filters, limit, timeout)
    
    def retrieve_by_confidence(
        self,
        min_confidence: float,
        limit: int = DEFAULT_METADATA_LIMIT,
        timeout: float = METADATA_RETRIEVAL_TIMEOUT
    ) -> EvidenceSet:
        """Retrieve documents by minimum confidence.
        
        Args:
            min_confidence: Minimum confidence threshold
            limit: Maximum results
            timeout: Retrieval timeout
            
        Returns:
            Evidence set with confidence-filtered results
        """
        filters = {'min_confidence': min_confidence}
        return self.retrieve(filters, limit, timeout)
    
    def _search_with_timeout(
        self,
        filters: Dict[str, Any],
        limit: int,
        timeout: float
    ) -> List[Dict[str, Any]]:
        """Perform metadata search with timeout.
        
        Args:
            filters: Filter criteria
            limit: Maximum results
            timeout: Timeout in seconds
            
        Returns:
            List of search results
            
        Raises:
            SearchTimeoutException: If search times out
        """
        import signal
        
        def timeout_handler(signum, frame):
            raise SearchTimeoutException(
                f"Metadata retrieval timeout after {timeout}s",
                source=SOURCE_METADATA,
                timeout=timeout
            )
        
        # Set timeout signal
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout))
        
        try:
            results = self._metadata_search(filters, limit)
            signal.alarm(0)  # Cancel alarm
            return results
        except Exception as e:
            signal.alarm(0)  # Cancel alarm
            if isinstance(e, SearchTimeoutException):
                raise
            raise MetadataRetrievalException(f"Metadata search failed: {str(e)}")
    
    def _metadata_search(self, filters: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Perform metadata search.
        
        Args:
            filters: Filter criteria
            limit: Maximum results
            
        Returns:
            List of search results
        """
        results = []
        
        if not self.db:
            return results
        
        try:
            from app.modules.document_processing.repository import ProcessedDocumentRepository
            from app.modules.knowledge_extraction.repository import KnowledgeExtractionRepository
            
            doc_repo = ProcessedDocumentRepository(self.db)
            knowledge_repo = KnowledgeExtractionRepository(self.db)
            
            # Get processed documents
            processed_docs = doc_repo.get_all_processed_documents()
            
            # Apply filters
            for doc in processed_docs:
                if self._apply_filters(doc, filters):
                    # Get entities for this document
                    entities = knowledge_repo.get_entities_by_document(doc.document_id)
                    
                    results.append({
                        'document_id': doc.document_id,
                        'processed_document_id': doc.id,
                        'text_content': doc.text_content,
                        'document_type': doc.document_type,
                        'created_at': doc.created_at.isoformat() if doc.created_at else None,
                        'entities': [e.to_dict() for e in entities],
                        'score': 1.0  # All metadata matches get full score
                    })
            
            # Limit results
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error in metadata search: {e}")
            raise MetadataRetrievalException(f"Database query failed: {str(e)}")
    
    def _apply_filters(self, doc: Any, filters: Dict[str, Any]) -> bool:
        """Apply metadata filters to a document.
        
        Args:
            doc: Document object
            filters: Filter criteria
            
        Returns:
            True if document passes all filters
        """
        # Document type filter
        if 'document_type' in filters:
            if doc.document_type != filters['document_type']:
                return False
        
        # Equipment filter (would need to check entities)
        if 'equipment' in filters:
            # This would require checking if the document references the equipment
            # For now, skip this check
            pass
        
        # Department filter
        if 'department' in filters:
            # This would require department metadata on documents
            # For now, skip this check
            pass
        
        # Date range filter
        if 'start_date' in filters or 'end_date' in filters:
            if not doc.created_at:
                return False
            
            from datetime import datetime
            doc_date = doc.created_at
            
            if 'start_date' in filters:
                start_date = datetime.fromisoformat(filters['start_date'])
                if doc_date < start_date:
                    return False
            
            if 'end_date' in filters:
                end_date = datetime.fromisoformat(filters['end_date'])
                if doc_date > end_date:
                    return False
        
        # Confidence filter
        if 'min_confidence' in filters:
            # This would require confidence metadata on documents
            # For now, skip this check
            pass
        
        return True
    
    def _convert_to_evidence(self, results: List[Dict[str, Any]], start_time: float) -> List[EvidenceItem]:
        """Convert search results to evidence items.
        
        Args:
            results: Search results
            start_time: Start time for retrieval
            
        Returns:
            List of evidence items
        """
        evidence_items = []
        
        for i, result in enumerate(results):
            evidence_id = str(uuid.uuid4())
            
            # Extract entity IDs
            entity_ids = [e.get('entity_id') for e in result.get('entities', [])]
            
            evidence_item = EvidenceItem(
                evidence_id=evidence_id,
                evidence_type=EvidenceType.CHUNK,
                source=EvidenceSource.METADATA,
                score=result['score'],
                confidence=None,
                content=result.get('text_content', ''),
                chunk_text=result.get('text_content', ''),
                document_id=result['document_id'],
                chunk_id=result.get('processed_document_id'),
                entity_id=None,
                relationship_id=None,
                graph_node_id=None,
                metadata={
                    'document_type': result.get('document_type'),
                    'created_at': result.get('created_at'),
                    'entity_ids': entity_ids,
                    'entity_count': len(entity_ids),
                    'ranking_position': i + 1
                },
                retrieval_time_ms=None,
                ranking_position=i + 1
            )
            
            evidence_items.append(evidence_item)
        
        return evidence_items
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get metadata retriever statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'source': SOURCE_METADATA,
            'engine': 'MetadataFilter',
            'status': 'operational'
        }
