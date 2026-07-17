"""Repository layer for hybrid retrieval data access."""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.modules.hybrid_retrieval.schemas import (
    QueryAnalysis,
    QueryExpansion,
    EvidenceItem,
    EvidenceSet
)
from app.modules.hybrid_retrieval.exceptions import HybridRetrievalError


class HybridRetrievalRepository:
    """Repository for hybrid retrieval data access operations."""
    
    def __init__(self, db: Session):
        """Initialize repository.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_entity_by_name(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """Get entity by name from database.
        
        Args:
            entity_name: Entity name
            
        Returns:
            Entity data or None
        """
        try:
            from app.modules.knowledge_extraction.repository import KnowledgeExtractionRepository
            knowledge_repo = KnowledgeExtractionRepository(self.db)
            
            # Search for entity by normalized name
            entities = knowledge_repo.search_entities(entity_name, limit=1)
            
            if entities:
                return entities[0].to_dict()
            
            return None
            
        except Exception as e:
            raise HybridRetrievalError(f"Failed to get entity by name: {str(e)}")
    
    def get_entities_by_type(self, entity_type: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get entities by type from database.
        
        Args:
            entity_type: Entity type
            limit: Maximum results
            
        Returns:
            List of entity data
        """
        try:
            from app.modules.knowledge_extraction.repository import KnowledgeExtractionRepository
            knowledge_repo = KnowledgeExtractionRepository(self.db)
            
            entities = knowledge_repo.get_entities_by_type(entity_type, limit=limit)
            
            return [entity.to_dict() for entity in entities]
            
        except Exception as e:
            raise HybridRetrievalError(f"Failed to get entities by type: {str(e)}")
    
    def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID from database.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document data or None
        """
        try:
            from app.modules.document_processing.repository import ProcessedDocumentRepository
            doc_repo = ProcessedDocumentRepository(self.db)
            
            processed_doc = doc_repo.get_processed_document_by_document_id(document_id)
            
            if processed_doc:
                return processed_doc.to_dict()
            
            return None
            
        except Exception as e:
            raise HybridRetrievalError(f"Failed to get document by ID: {str(e)}")
    
    def get_documents_by_type(self, document_type: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get documents by type from database.
        
        Args:
            document_type: Document type
            limit: Maximum results
            
        Returns:
            List of document data
        """
        try:
            from app.modules.document_processing.repository import ProcessedDocumentRepository
            doc_repo = ProcessedDocumentRepository(self.db)
            
            # Get all processed documents and filter by type
            all_docs = doc_repo.get_all_processed_documents()
            filtered_docs = [doc for doc in all_docs if doc.document_type == document_type]
            
            return [doc.to_dict() for doc in filtered_docs[:limit]]
            
        except Exception as e:
            raise HybridRetrievalError(f"Failed to get documents by type: {str(e)}")
    
    def get_entity_relationships(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get relationships for an entity from database.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of relationship data
        """
        try:
            from app.modules.knowledge_extraction.repository import KnowledgeExtractionRepository
            knowledge_repo = KnowledgeExtractionRepository(self.db)
            
            relationships = knowledge_repo.get_relationships_by_entity(entity_id)
            
            return [rel.to_dict() for rel in relationships]
            
        except Exception as e:
            raise HybridRetrievalError(f"Failed to get entity relationships: {str(e)}")
    
    def search_documents(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search documents by text content.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of document data
        """
        try:
            from app.modules.document_processing.repository import ProcessedDocumentRepository
            doc_repo = ProcessedDocumentRepository(self.db)
            
            # Get all processed documents and filter by content
            all_docs = doc_repo.get_all_processed_documents()
            query_lower = query.lower()
            
            filtered_docs = [
                doc for doc in all_docs
                if query_lower in doc.text_content.lower()
            ]
            
            return [doc.to_dict() for doc in filtered_docs[:limit]]
            
        except Exception as e:
            raise HybridRetrievalError(f"Failed to search documents: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            from app.modules.document_processing.repository import ProcessedDocumentRepository
            from app.modules.knowledge_extraction.repository import KnowledgeExtractionRepository
            
            doc_repo = ProcessedDocumentRepository(self.db)
            knowledge_repo = KnowledgeExtractionRepository(self.db)
            
            # Get counts
            processed_docs = doc_repo.get_all_processed_documents()
            entities = knowledge_repo.get_all_entities()
            relationships = knowledge_repo.get_all_relationships()
            
            return {
                'total_documents': len(processed_docs),
                'total_entities': len(entities),
                'total_relationships': len(relationships),
                'document_types': self._get_document_type_distribution(processed_docs),
                'entity_types': self._get_entity_type_distribution(entities)
            }
            
        except Exception as e:
            raise HybridRetrievalError(f"Failed to get statistics: {str(e)}")
    
    def _get_document_type_distribution(self, documents: List[Any]) -> Dict[str, int]:
        """Get document type distribution.
        
        Args:
            documents: List of documents
            
        Returns:
            Type distribution
        """
        distribution = {}
        for doc in documents:
            doc_type = doc.document_type
            distribution[doc_type] = distribution.get(doc_type, 0) + 1
        return distribution
    
    def _get_entity_type_distribution(self, entities: List[Any]) -> Dict[str, int]:
        """Get entity type distribution.
        
        Args:
            entities: List of entities
            
        Returns:
            Type distribution
        """
        distribution = {}
        for entity in entities:
            entity_type = entity.entity_type
            distribution[entity_type] = distribution.get(entity_type, 0) + 1
        return distribution
