"""Repository for knowledge extraction data access."""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import uuid
from datetime import datetime
from app.modules.knowledge_extraction.models import (
    Entity,
    EntityAlias,
    EntityOccurrence,
    Relationship,
    RelationshipEvidence
)
from app.modules.knowledge_extraction.schemas import (
    EntityCreate,
    EntityUpdate,
    EntityAliasCreate,
    EntityOccurrenceCreate,
    RelationshipCreate,
    RelationshipUpdate,
    RelationshipEvidenceCreate
)
from app.modules.knowledge_extraction.enums import EntityType, RelationshipType


class KnowledgeExtractionRepository:
    """Repository for knowledge extraction data access."""
    
    def __init__(self, db: Session):
        """Initialize repository.
        
        Args:
            db: Database session
        """
        self.db = db
    
    # ============================================================================
    # Entity Operations
    # ============================================================================
    
    def create_entity(self, entity_data: EntityCreate) -> Entity:
        """Create a new entity.
        
        Args:
            entity_data: Entity creation data
            
        Returns:
            Created entity
        """
        entity = Entity(**entity_data.model_dump())
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    def get_entity_by_id(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Entity if found, None otherwise
        """
        return self.db.query(Entity).filter(Entity.entity_id == entity_id).first()
    
    def get_entity_by_name_and_type(
        self,
        name: str,
        entity_type: EntityType
    ) -> Optional[Entity]:
        """Get entity by normalized name and type.
        
        Args:
            name: Entity name
            entity_type: Entity type
            
        Returns:
            Entity if found, None otherwise
        """
        return self.db.query(Entity).filter(
            and_(
                Entity.normalized_name == name,
                Entity.entity_type == entity_type
            )
        ).first()
    
    def get_entities_by_document(self, document_id: str) -> List[Entity]:
        """Get all entities for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            List of entities
        """
        return self.db.query(Entity).filter(
            Entity.source_document_id == document_id
        ).all()
    
    def get_entities_by_type(
        self,
        entity_type: EntityType,
        document_id: Optional[str] = None
    ) -> List[Entity]:
        """Get entities by type.
        
        Args:
            entity_type: Entity type
            document_id: Optional document ID filter
            
        Returns:
            List of entities
        """
        query = self.db.query(Entity).filter(Entity.entity_type == entity_type)
        
        if document_id:
            query = query.filter(Entity.source_document_id == document_id)
        
        return query.all()
    
    def update_entity(self, entity_id: str, update_data: EntityUpdate) -> Optional[Entity]:
        """Update an entity.
        
        Args:
            entity_id: Entity ID
            update_data: Update data
            
        Returns:
            Updated entity if found, None otherwise
        """
        entity = self.get_entity_by_id(entity_id)
        if not entity:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(entity, field, value)
        
        entity.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            True if deleted, False otherwise
        """
        entity = self.get_entity_by_id(entity_id)
        if not entity:
            return False
        
        self.db.delete(entity)
        self.db.commit()
        return True
    
    def delete_entities_by_document(self, document_id: str) -> int:
        """Delete all entities for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            Number of entities deleted
        """
        count = self.db.query(Entity).filter(
            Entity.source_document_id == document_id
        ).delete()
        self.db.commit()
        return count
    
    # ============================================================================
    # Entity Alias Operations
    # ============================================================================
    
    def create_entity_alias(self, alias_data: EntityAliasCreate) -> EntityAlias:
        """Create an entity alias.
        
        Args:
            alias_data: Alias creation data
            
        Returns:
            Created alias
        """
        alias = EntityAlias(**alias_data.model_dump())
        self.db.add(alias)
        self.db.commit()
        self.db.refresh(alias)
        return alias
    
    def get_entity_aliases(self, entity_id: str) -> List[EntityAlias]:
        """Get all aliases for an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of aliases
        """
        return self.db.query(EntityAlias).filter(
            EntityAlias.entity_id == entity_id
        ).all()
    
    def delete_entity_aliases(self, entity_id: str) -> int:
        """Delete all aliases for an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Number of aliases deleted
        """
        count = self.db.query(EntityAlias).filter(
            EntityAlias.entity_id == entity_id
        ).delete()
        self.db.commit()
        return count
    
    # ============================================================================
    # Entity Occurrence Operations
    # ============================================================================
    
    def create_entity_occurrence(self, occurrence_data: EntityOccurrenceCreate) -> EntityOccurrence:
        """Create an entity occurrence.
        
        Args:
            occurrence_data: Occurrence creation data
            
        Returns:
            Created occurrence
        """
        occurrence = EntityOccurrence(**occurrence_data.model_dump())
        self.db.add(occurrence)
        self.db.commit()
        self.db.refresh(occurrence)
        return occurrence
    
    def get_entity_occurrences(self, entity_id: str) -> List[EntityOccurrence]:
        """Get all occurrences for an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of occurrences
        """
        return self.db.query(EntityOccurrence).filter(
            EntityOccurrence.entity_id == entity_id
        ).all()
    
    def get_document_occurrences(self, document_id: str) -> List[EntityOccurrence]:
        """Get all entity occurrences for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            List of occurrences
        """
        return self.db.query(EntityOccurrence).filter(
            EntityOccurrence.source_document_id == document_id
        ).all()
    
    def delete_entity_occurrences(self, entity_id: str) -> int:
        """Delete all occurrences for an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Number of occurrences deleted
        """
        count = self.db.query(EntityOccurrence).filter(
            EntityOccurrence.entity_id == entity_id
        ).delete()
        self.db.commit()
        return count
    
    # ============================================================================
    # Relationship Operations
    # ============================================================================
    
    def create_relationship(self, relationship_data: RelationshipCreate) -> Relationship:
        """Create a new relationship.
        
        Args:
            relationship_data: Relationship creation data
            
        Returns:
            Created relationship
        """
        relationship = Relationship(**relationship_data.model_dump())
        self.db.add(relationship)
        self.db.commit()
        self.db.refresh(relationship)
        return relationship
    
    def get_relationship_by_id(self, relationship_id: str) -> Optional[Relationship]:
        """Get relationship by ID.
        
        Args:
            relationship_id: Relationship ID
            
        Returns:
            Relationship if found, None otherwise
        """
        return self.db.query(Relationship).filter(
            Relationship.relationship_id == relationship_id
        ).first()
    
    def get_relationships_by_document(self, document_id: str) -> List[Relationship]:
        """Get all relationships for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            List of relationships
        """
        return self.db.query(Relationship).filter(
            Relationship.source_document_id == document_id
        ).all()
    
    def get_relationships_by_type(
        self,
        relationship_type: RelationshipType,
        document_id: Optional[str] = None
    ) -> List[Relationship]:
        """Get relationships by type.
        
        Args:
            relationship_type: Relationship type
            document_id: Optional document ID filter
            
        Returns:
            List of relationships
        """
        query = self.db.query(Relationship).filter(
            Relationship.relationship_type == relationship_type
        )
        
        if document_id:
            query = query.filter(Relationship.source_document_id == document_id)
        
        return query.all()
    
    def get_relationships_by_entity(self, entity_id: str) -> List[Relationship]:
        """Get all relationships for an entity (as source or target).
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of relationships
        """
        return self.db.query(Relationship).filter(
            or_(
                Relationship.source_entity_id == entity_id,
                Relationship.target_entity_id == entity_id
            )
        ).all()
    
    def update_relationship(
        self,
        relationship_id: str,
        update_data: RelationshipUpdate
    ) -> Optional[Relationship]:
        """Update a relationship.
        
        Args:
            relationship_id: Relationship ID
            update_data: Update data
            
        Returns:
            Updated relationship if found, None otherwise
        """
        relationship = self.get_relationship_by_id(relationship_id)
        if not relationship:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(relationship, field, value)
        
        self.db.commit()
        self.db.refresh(relationship)
        return relationship
    
    def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship.
        
        Args:
            relationship_id: Relationship ID
            
        Returns:
            True if deleted, False otherwise
        """
        relationship = self.get_relationship_by_id(relationship_id)
        if not relationship:
            return False
        
        self.db.delete(relationship)
        self.db.commit()
        return True
    
    def delete_relationships_by_document(self, document_id: str) -> int:
        """Delete all relationships for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            Number of relationships deleted
        """
        count = self.db.query(Relationship).filter(
            Relationship.source_document_id == document_id
        ).delete()
        self.db.commit()
        return count
    
    # ============================================================================
    # Relationship Evidence Operations
    # ============================================================================
    
    def create_relationship_evidence(self, evidence_data: RelationshipEvidenceCreate) -> RelationshipEvidence:
        """Create relationship evidence.
        
        Args:
            evidence_data: Evidence creation data
            
        Returns:
            Created evidence
        """
        evidence = RelationshipEvidence(**evidence_data.model_dump())
        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)
        return evidence
    
    def get_relationship_evidence(self, relationship_id: str) -> List[RelationshipEvidence]:
        """Get all evidence for a relationship.
        
        Args:
            relationship_id: Relationship ID
            
        Returns:
            List of evidence
        """
        return self.db.query(RelationshipEvidence).filter(
            RelationshipEvidence.relationship_id == relationship_id
        ).all()
    
    def delete_relationship_evidence(self, relationship_id: str) -> int:
        """Delete all evidence for a relationship.
        
        Args:
            relationship_id: Relationship ID
            
        Returns:
            Number of evidence deleted
        """
        count = self.db.query(RelationshipEvidence).filter(
            RelationshipEvidence.relationship_id == relationship_id
        ).delete()
        self.db.commit()
        return count
    
    # ============================================================================
    # Statistics Operations
    # ============================================================================
    
    def get_entity_statistics(self, document_id: str) -> Dict[str, Any]:
        """Get entity statistics for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            Dictionary with statistics
        """
        entities = self.get_entities_by_document(document_id)
        
        # Count by type
        type_counts = {}
        for entity in entities:
            entity_type = entity.entity_type
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        
        # Confidence distribution
        confidence_distribution = {"high": 0, "medium": 0, "low": 0}
        for entity in entities:
            if entity.confidence_score >= 0.8:
                confidence_distribution["high"] += 1
            elif entity.confidence_score >= 0.5:
                confidence_distribution["medium"] += 1
            else:
                confidence_distribution["low"] += 1
        
        return {
            "total_entities": len(entities),
            "unique_entities": len(set(e.normalized_name.lower() for e in entities)),
            "entity_types": type_counts,
            "confidence_distribution": confidence_distribution
        }
    
    def get_relationship_statistics(self, document_id: str) -> Dict[str, Any]:
        """Get relationship statistics for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            Dictionary with statistics
        """
        relationships = self.get_relationships_by_document(document_id)
        
        # Count by type
        type_counts = {}
        for rel in relationships:
            rel_type = rel.relationship_type
            type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
        
        # Confidence distribution
        confidence_distribution = {"high": 0, "medium": 0, "low": 0}
        for rel in relationships:
            if rel.confidence_score >= 0.8:
                confidence_distribution["high"] += 1
            elif rel.confidence_score >= 0.5:
                confidence_distribution["medium"] += 1
            else:
                confidence_distribution["low"] += 1
        
        return {
            "total_relationships": len(relationships),
            "relationship_types": type_counts,
            "confidence_distribution": confidence_distribution
        }
