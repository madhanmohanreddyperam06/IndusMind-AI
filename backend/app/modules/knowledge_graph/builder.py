"""Graph builder for converting MySQL entities/relationships to Neo4j."""

from typing import List, Dict, Any
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from app.modules.knowledge_extraction.repository import KnowledgeExtractionRepository
from app.modules.knowledge_graph.repository import GraphRepository
from app.modules.knowledge_graph.schemas import (
    GraphNodeCreate,
    GraphRelationshipCreate
)
from app.modules.knowledge_graph.constants import ENTITY_LABELS, RELATIONSHIP_TYPES
from app.modules.knowledge_graph.exceptions import GraphBuilderError
from app.core.logging import setup_logging

logger = setup_logging()


class GraphBuilder:
    """Builder for converting MySQL data to Neo4j graph."""
    
    def __init__(self, mysql_db: Session):
        """Initialize the graph builder.
        
        Args:
            mysql_db: MySQL database session
        """
        self.mysql_db = mysql_db
        self.mysql_repo = KnowledgeExtractionRepository(mysql_db)
        self.graph_repo = GraphRepository()
    
    def build_from_document(self, document_id: str) -> Dict[str, Any]:
        """Build graph from a single document's extracted data.
        
        Args:
            document_id: Document ID
            
        Returns:
            Dictionary with build statistics
        """
        try:
            logger.info(f"Building graph for document {document_id}")
            
            # Get entities from MySQL
            entities = self.mysql_repo.get_entities_by_document(document_id)
            logger.info(f"Found {len(entities)} entities in MySQL")
            
            # Get relationships from MySQL
            relationships = self.mysql_repo.get_relationships_by_document(document_id)
            logger.info(f"Found {len(relationships)} relationships in MySQL")
            
            # Build entity name to ID mapping
            entity_name_to_id = {e.normalized_name.lower(): e.entity_id for e in entities}
            
            # Convert entities to graph nodes
            nodes_created = 0
            nodes_updated = 0
            for entity in entities:
                node_data = self._entity_to_node_create(entity)
                existing_node = self.graph_repo.get_node_by_id(entity.entity_id)
                
                if existing_node:
                    # Node exists, update it
                    self.graph_repo.update_node(entity.entity_id, node_data)
                    nodes_updated += 1
                else:
                    # Create new node
                    self.graph_repo.create_node(node_data)
                    nodes_created += 1
            
            logger.info(f"Created {nodes_created} nodes, updated {nodes_updated} nodes")
            
            # Convert relationships to graph relationships
            relationships_created = 0
            relationships_skipped = 0
            for relationship in relationships:
                rel_data = self._relationship_to_rel_create(relationship, entity_name_to_id)
                
                if rel_data:
                    existing_rel = self.graph_repo.get_relationship_by_id(relationship.relationship_id)
                    
                    if not existing_rel:
                        self.graph_repo.create_relationship(rel_data)
                        relationships_created += 1
                    else:
                        relationships_skipped += 1
                else:
                    relationships_skipped += 1
            
            logger.info(f"Created {relationships_created} relationships, skipped {relationships_skipped}")
            
            return {
                "document_id": document_id,
                "entities_processed": len(entities),
                "relationships_processed": len(relationships),
                "nodes_created": nodes_created,
                "nodes_updated": nodes_updated,
                "relationships_created": relationships_created,
                "relationships_skipped": relationships_skipped
            }
            
        except Exception as e:
            logger.error(f"Error building graph for document {document_id}: {e}")
            raise GraphBuilderError(f"Failed to build graph: {str(e)}")
    
    def build_from_all_documents(self) -> Dict[str, Any]:
        """Build graph from all documents in MySQL.
        
        Returns:
            Dictionary with build statistics
        """
        try:
            logger.info("Building graph from all documents")
            
            # Get all unique document IDs from entities
            from app.modules.knowledge_extraction.models import Entity
            from sqlalchemy import distinct
            
            document_ids = self.mysql_db.query(
                distinct(Entity.source_document_id)
            ).all()
            
            document_ids = [doc_id[0] for doc_id in document_ids]
            logger.info(f"Found {len(document_ids)} documents to process")
            
            total_stats = {
                "documents_processed": 0,
                "total_entities": 0,
                "total_relationships": 0,
                "total_nodes_created": 0,
                "total_nodes_updated": 0,
                "total_relationships_created": 0,
                "total_relationships_skipped": 0
            }
            
            for document_id in document_ids:
                try:
                    stats = self.build_from_document(document_id)
                    total_stats["documents_processed"] += 1
                    total_stats["total_entities"] += stats["entities_processed"]
                    total_stats["total_relationships"] += stats["relationships_processed"]
                    total_stats["total_nodes_created"] += stats["nodes_created"]
                    total_stats["total_nodes_updated"] += stats["nodes_updated"]
                    total_stats["total_relationships_created"] += stats["relationships_created"]
                    total_stats["total_relationships_skipped"] += stats["relationships_skipped"]
                except Exception as e:
                    logger.error(f"Error processing document {document_id}: {e}")
                    continue
            
            logger.info(f"Graph build completed: {total_stats}")
            return total_stats
            
        except Exception as e:
            logger.error(f"Error building graph from all documents: {e}")
            raise GraphBuilderError(f"Failed to build graph from all documents: {str(e)}")
    
    def rebuild_graph(self) -> Dict[str, Any]:
        """Rebuild the entire graph (delete all and recreate).
        
        Returns:
            Dictionary with rebuild statistics
        """
        try:
            logger.info("Rebuilding entire graph")
            
            # Delete all nodes and relationships
            with self.graph_repo._get_session() as session:
                session.run("MATCH (n) DETACH DELETE n")
                logger.info("Deleted all nodes and relationships")
            
            # Rebuild from all documents
            stats = self.build_from_all_documents()
            stats["rebuild"] = True
            
            return stats
            
        except Exception as e:
            logger.error(f"Error rebuilding graph: {e}")
            raise GraphBuilderError(f"Failed to rebuild graph: {str(e)}")
    
    def _entity_to_node_create(self, entity) -> GraphNodeCreate:
        """Convert MySQL entity to graph node create schema.
        
        Args:
            entity: MySQL entity model
            
        Returns:
            GraphNodeCreate schema
        """
        # Map entity type to graph label
        entity_type = ENTITY_LABELS.get(entity.entity_type, entity.entity_type)
        
        # Convert metadata dict if needed
        metadata = entity.entity_metadata if hasattr(entity, 'entity_metadata') else entity.metadata
        if metadata and isinstance(metadata, str):
            import json
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {"raw": metadata}
        
        return GraphNodeCreate(
            entity_id=entity.entity_id,
            entity_type=entity_type,
            normalized_name=entity.normalized_name,
            original_name=entity.name,
            confidence_score=entity.confidence_score,
            extraction_method=getattr(entity, 'extraction_method', 'RULE_BASED'),
            metadata=metadata
        )
    
    def _relationship_to_rel_create(
        self,
        relationship,
        entity_name_to_id: Dict[str, str]
    ) -> GraphRelationshipCreate:
        """Convert MySQL relationship to graph relationship create schema.
        
        Args:
            relationship: MySQL relationship model
            entity_name_to_id: Mapping of entity names to IDs
            
        Returns:
            GraphRelationshipCreate schema or None if invalid
        """
        # Map relationship type
        rel_type = RELATIONSHIP_TYPES.get(relationship.relationship_type, relationship.relationship_type)
        
        # Get source and target entity IDs
        # Note: MySQL relationships store entity names, we need to map to IDs
        # This is a simplification - in production, you'd want to store entity IDs directly
        source_id = relationship.source_entity_id
        target_id = relationship.target_entity_id
        
        if not source_id or not target_id:
            logger.warning(f"Relationship missing entity IDs: {relationship.relationship_id}")
            return None
        
        return GraphRelationshipCreate(
            source_entity_id=source_id,
            target_entity_id=target_id,
            relationship_type=rel_type,
            confidence_score=relationship.confidence_score,
            evidence=relationship.evidence_text,
            relationship_id=relationship.relationship_id
        )
    
    def create_document_node(self, document_id: str, document_name: str) -> str:
        """Create a document node in the graph.
        
        Args:
            document_id: Document ID
            document_name: Document name
            
        Returns:
            Entity ID of the created node
        """
        from app.modules.knowledge_graph.enums import GraphEntityType
        
        node_data = GraphNodeCreate(
            entity_id=document_id,
            entity_type=GraphEntityType.DOCUMENT,
            normalized_name=document_name.lower(),
            original_name=document_name,
            confidence_score=1.0,
            extraction_method="SYSTEM",
            metadata={"type": "document"}
        )
        
        self.graph_repo.create_node(node_data)
        return document_id
    
    def link_entities_to_document(self, document_id: str, entity_ids: List[str]):
        """Link entities to their source document.
        
        Args:
            document_id: Document ID
            entity_ids: List of entity IDs to link
        """
        from app.modules.knowledge_graph.enums import GraphRelationshipType
        
        for entity_id in entity_ids:
            rel_data = GraphRelationshipCreate(
                source_entity_id=document_id,
                target_entity_id=entity_id,
                relationship_type=GraphRelationshipType.RECORDED_IN,
                confidence_score=1.0,
                evidence="Document source"
            )
            self.graph_repo.create_relationship(rel_data)
