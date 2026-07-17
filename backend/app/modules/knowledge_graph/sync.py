"""Graph synchronization service for syncing MySQL data to Neo4j."""

import time
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.modules.knowledge_graph.builder import GraphBuilder
from app.modules.knowledge_graph.schemas import SyncResult, SyncStatus
from app.modules.knowledge_graph.exceptions import GraphSynchronizationError
from app.core.logging import setup_logging

logger = setup_logging()


class GraphSynchronizationService:
    """Service for synchronizing MySQL data to Neo4j graph."""
    
    def __init__(self, mysql_db: Session):
        """Initialize the synchronization service.
        
        Args:
            mysql_db: MySQL database session
        """
        self.mysql_db = mysql_db
        self.builder = GraphBuilder(mysql_db)
    
    def sync_document(self, document_id: str, force_rebuild: bool = False) -> SyncResult:
        """Synchronize a single document to the graph.
        
        Args:
            document_id: Document ID to sync
            force_rebuild: Whether to force rebuild of graph data
            
        Returns:
            SyncResult with synchronization statistics
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting synchronization for document {document_id}")
            
            if force_rebuild:
                # Delete existing graph data for this document
                self._delete_document_data(document_id)
                logger.info(f"Deleted existing graph data for document {document_id}")
            
            # Build graph from document
            stats = self.builder.build_from_document(document_id)
            
            duration = time.time() - start_time
            
            result = SyncResult(
                document_id=document_id,
                entities_synced=stats["entities_processed"],
                relationships_synced=stats["relationships_processed"],
                nodes_created=stats["nodes_created"],
                nodes_updated=stats["nodes_updated"],
                relationships_created=stats["relationships_created"],
                duration_seconds=duration,
                success=True
            )
            
            logger.info(f"Synchronization completed for document {document_id}: {result}")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Synchronization failed for document {document_id}: {e}")
            
            return SyncResult(
                document_id=document_id,
                entities_synced=0,
                relationships_synced=0,
                nodes_created=0,
                nodes_updated=0,
                relationships_created=0,
                duration_seconds=duration,
                success=False,
                error_message=str(e)
            )
    
    def sync_all_documents(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """Synchronize all documents to the graph.
        
        Args:
            force_rebuild: Whether to force rebuild of entire graph
            
        Returns:
            Dictionary with overall synchronization statistics
        """
        start_time = time.time()
        
        try:
            logger.info("Starting full graph synchronization")
            
            if force_rebuild:
                # Rebuild entire graph
                stats = self.builder.rebuild_graph()
            else:
                # Build from all documents (incremental)
                stats = self.builder.build_from_all_documents()
            
            duration = time.time() - start_time
            
            result = {
                "documents_processed": stats.get("documents_processed", 0),
                "total_entities": stats.get("total_entities", 0),
                "total_relationships": stats.get("total_relationships", 0),
                "total_nodes_created": stats.get("total_nodes_created", 0),
                "total_nodes_updated": stats.get("total_nodes_updated", 0),
                "total_relationships_created": stats.get("total_relationships_created", 0),
                "total_relationships_skipped": stats.get("total_relationships_skipped", 0),
                "duration_seconds": duration,
                "success": True,
                "rebuild": force_rebuild
            }
            
            logger.info(f"Full synchronization completed: {result}")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Full synchronization failed: {e}")
            
            return {
                "documents_processed": 0,
                "total_entities": 0,
                "total_relationships": 0,
                "total_nodes_created": 0,
                "total_nodes_updated": 0,
                "total_relationships_created": 0,
                "total_relationships_skipped": 0,
                "duration_seconds": duration,
                "success": False,
                "error_message": str(e),
                "rebuild": force_rebuild
            }
    
    def incremental_sync(self, document_id: str) -> SyncResult:
        """Perform incremental synchronization for a document.
        
        Only syncs new/changed entities and relationships.
        
        Args:
            document_id: Document ID to sync
            
        Returns:
            SyncResult with synchronization statistics
        """
        return self.sync_document(document_id, force_rebuild=False)
    
    def get_sync_status(self, document_id: str) -> SyncStatus:
        """Get synchronization status for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            SyncStatus with current status
        """
        try:
            from app.modules.knowledge_extraction.repository import KnowledgeExtractionRepository
            
            mysql_repo = KnowledgeExtractionRepository(self.mysql_db)
            
            # Check if entities exist in MySQL
            entities = mysql_repo.get_entities_by_document(document_id)
            relationships = mysql_repo.get_relationships_by_document(document_id)
            
            # Check if synced to graph
            from app.modules.knowledge_graph.repository import GraphRepository
            graph_repo = GraphRepository()
            
            # Check if document node exists
            doc_node = graph_repo.get_node_by_id(document_id)
            
            if not doc_node:
                return SyncStatus(
                    document_id=document_id,
                    status="pending",
                    entities_synced=0,
                    relationships_synced=0
                )
            
            # Count synced entities
            synced_count = 0
            for entity in entities:
                if graph_repo.get_node_by_id(entity.entity_id):
                    synced_count += 1
            
            # Count synced relationships
            synced_rels = 0
            for rel in relationships:
                if graph_repo.get_relationship_by_id(rel.relationship_id):
                    synced_rels += 1
            
            # Determine status
            if synced_count == len(entities) and synced_rels == len(relationships):
                status = "completed"
            elif synced_count > 0 or synced_rels > 0:
                status = "in_progress"
            else:
                status = "pending"
            
            return SyncStatus(
                document_id=document_id,
                status=status,
                entities_synced=synced_count,
                relationships_synced=synced_rels
            )
            
        except Exception as e:
            logger.error(f"Error getting sync status for document {document_id}: {e}")
            return SyncStatus(
                document_id=document_id,
                status="failed",
                entities_synced=0,
                relationships_synced=0,
                error_message=str(e)
            )
    
    def _delete_document_data(self, document_id: str):
        """Delete graph data for a specific document.
        
        Args:
            document_id: Document ID
        """
        try:
            from app.modules.knowledge_graph.repository import GraphRepository
            graph_repo = GraphRepository()
            
            # Get all entities for this document
            from app.modules.knowledge_extraction.repository import KnowledgeExtractionRepository
            mysql_repo = KnowledgeExtractionRepository(self.mysql_db)
            entities = mysql_repo.get_entities_by_document(document_id)
            
            # Delete each entity (which will cascade delete relationships)
            for entity in entities:
                graph_repo.delete_node(entity.entity_id)
            
            # Delete document node if exists
            graph_repo.delete_node(document_id)
            
            logger.info(f"Deleted graph data for document {document_id}")
            
        except Exception as e:
            logger.error(f"Error deleting document data: {e}")
            raise GraphSynchronizationError(f"Failed to delete document data: {str(e)}")
    
    def retry_failed_sync(self, document_id: str, max_retries: int = 3) -> SyncResult:
        """Retry synchronization for a failed document.
        
        Args:
            document_id: Document ID to retry
            max_retries: Maximum number of retry attempts
            
        Returns:
            SyncResult with synchronization statistics
        """
        from app.modules.knowledge_graph.constants import GRAPH_CONFIG
        
        retry_delay = GRAPH_CONFIG.get("retry_delay", 1.0)
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Retry attempt {attempt + 1}/{max_retries} for document {document_id}")
                
                result = self.sync_document(document_id, force_rebuild=True)
                
                if result.success:
                    logger.info(f"Retry successful for document {document_id}")
                    return result
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    
            except Exception as e:
                logger.error(f"Retry attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        
        # All retries failed
        return SyncResult(
            document_id=document_id,
            entities_synced=0,
            relationships_synced=0,
            nodes_created=0,
            nodes_updated=0,
            relationships_created=0,
            duration_seconds=0,
            success=False,
            error_message=f"Failed after {max_retries} retry attempts"
        )
