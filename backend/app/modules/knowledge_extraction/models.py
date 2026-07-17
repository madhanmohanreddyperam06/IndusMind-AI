"""SQLAlchemy models for knowledge extraction module."""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON
import uuid
from app.config.database import Base
from app.modules.knowledge_extraction.enums import EntityType, RelationshipType


class Entity(Base):
    """Entity model for extracted industrial entities."""
    __tablename__ = "entities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = Column(String(36), unique=True, nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    name = Column(String(500), nullable=False, index=True)
    normalized_name = Column(String(500), nullable=False, index=True)
    confidence_score = Column(Float, default=0.7, index=True)
    source_document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    page_number = Column(Integer, nullable=True)
    section = Column(String(500), nullable=True)
    paragraph = Column(Integer, nullable=True)
    start_offset = Column(Integer, nullable=True)
    end_offset = Column(Integer, nullable=True)
    entity_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    aliases = relationship("EntityAlias", back_populates="entity", cascade="all, delete-orphan")
    occurrences = relationship("EntityOccurrence", back_populates="entity", cascade="all, delete-orphan")
    source_relationships = relationship(
        "Relationship",
        foreign_keys="Relationship.source_entity_id",
        back_populates="source_entity",
        cascade="all, delete-orphan"
    )
    target_relationships = relationship(
        "Relationship",
        foreign_keys="Relationship.target_entity_id",
        back_populates="target_entity",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Entity(entity_id={self.entity_id}, entity_type={self.entity_type}, name={self.name})>"


class EntityAlias(Base):
    """Entity alias model for storing alternative names."""
    __tablename__ = "entity_aliases"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = Column(String(36), ForeignKey("entities.entity_id"), nullable=False, index=True)
    alias = Column(String(500), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    entity = relationship("Entity", back_populates="aliases")

    def __repr__(self):
        return f"<EntityAlias(entity_id={self.entity_id}, alias={self.alias})>"


class EntityOccurrence(Base):
    """Entity occurrence model for tracking entity mentions in documents."""
    __tablename__ = "entity_occurrences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = Column(String(36), ForeignKey("entities.entity_id"), nullable=False, index=True)
    source_document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    page_number = Column(Integer, nullable=True)
    section = Column(String(500), nullable=True)
    paragraph = Column(Integer, nullable=True)
    start_offset = Column(Integer, nullable=True)
    end_offset = Column(Integer, nullable=True)
    context_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    entity = relationship("Entity", back_populates="occurrences")

    def __repr__(self):
        return f"<EntityOccurrence(entity_id={self.entity_id}, document_id={self.source_document_id})>"


class Relationship(Base):
    """Relationship model for extracted entity relationships."""
    __tablename__ = "relationships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    relationship_id = Column(String(36), unique=True, nullable=False, index=True)
    source_entity_id = Column(String(36), ForeignKey("entities.entity_id"), nullable=False, index=True)
    target_entity_id = Column(String(36), ForeignKey("entities.entity_id"), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False, index=True)
    confidence_score = Column(Float, default=0.7, index=True)
    source_document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    page_number = Column(Integer, nullable=True)
    paragraph = Column(Integer, nullable=True)
    evidence_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    source_entity = relationship(
        "Entity",
        foreign_keys=[source_entity_id],
        back_populates="source_relationships"
    )
    target_entity = relationship(
        "Entity",
        foreign_keys=[target_entity_id],
        back_populates="target_relationships"
    )
    evidence = relationship("RelationshipEvidence", back_populates="relationship", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Relationship(relationship_id={self.relationship_id}, type={self.relationship_type})>"


class RelationshipEvidence(Base):
    """Relationship evidence model for storing supporting evidence."""
    __tablename__ = "relationship_evidence"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    relationship_id = Column(String(36), ForeignKey("relationships.relationship_id"), nullable=False, index=True)
    source_document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    page_number = Column(Integer, nullable=True)
    paragraph = Column(Integer, nullable=True)
    sentence = Column(Integer, nullable=True)
    evidence_text = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.7)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    relationship = relationship("Relationship", back_populates="evidence")

    def __repr__(self):
        return f"<RelationshipEvidence(relationship_id={self.relationship_id})>"


# Create indexes for better query performance
Index('idx_entity_type_name', Entity.entity_type, Entity.name)
Index('idx_entity_document', Entity.source_document_id, Entity.entity_type)
Index('idx_relationship_type_source_target', Relationship.relationship_type, Relationship.source_entity_id, Relationship.target_entity_id)
Index('idx_relationship_document', Relationship.source_document_id, Relationship.relationship_type)
