"""Pydantic schemas for knowledge extraction module."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.modules.knowledge_extraction.enums import EntityType, RelationshipType, ConfidenceLevel, ExtractionMethod


# ============================================================================
# Entity Schemas
# ============================================================================

class EntitySchema(BaseModel):
    """Base entity schema."""
    entity_id: str
    entity_type: EntityType
    name: str
    normalized_name: str
    confidence_score: float = Field(default=0.7, ge=0.0, le=1.0)
    source_document_id: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    paragraph: Optional[int] = None
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    entity_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    aliases: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


class EntityAliasSchema(BaseModel):
    """Entity alias schema."""
    alias: str
    created_at: datetime

    class Config:
        from_attributes = True


class EntityOccurrenceSchema(BaseModel):
    """Entity occurrence schema."""
    entity_id: str
    source_document_id: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    paragraph: Optional[int] = None
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    context_text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Relationship Schemas
# ============================================================================

class RelationshipSchema(BaseModel):
    """Relationship schema."""
    relationship_id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: RelationshipType
    confidence_score: float = Field(default=0.7, ge=0.0, le=1.0)
    source_document_id: str
    page_number: Optional[int] = None
    paragraph: Optional[int] = None
    evidence_text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RelationshipEvidenceSchema(BaseModel):
    """Relationship evidence schema."""
    relationship_id: str
    source_document_id: str
    page_number: Optional[int] = None
    paragraph: Optional[int] = None
    sentence: Optional[int] = None
    evidence_text: Optional[str] = None
    confidence_score: float = Field(default=0.7, ge=0.0, le=1.0)
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# API Request/Response Schemas
# ============================================================================

class ExtractEntitiesRequest(BaseModel):
    """Request to extract entities from a document."""
    force_reextract: bool = False
    extractors: Optional[List[str]] = None  # Specific extractors to run, None = all


class ExtractRelationshipsRequest(BaseModel):
    """Request to extract relationships from a document."""
    force_reextract: bool = False
    relationship_types: Optional[List[str]] = None  # Specific relationship types to extract, None = all


class ProcessKnowledgeExtractionRequest(BaseModel):
    """Request to run full knowledge extraction pipeline."""
    force_reextract: bool = False


class EntityExtractionResult(BaseModel):
    """Entity extraction result."""
    document_id: str
    entities: List[EntitySchema]
    total_count: int
    extraction_time_seconds: float
    extractors_used: List[str]


class RelationshipExtractionResult(BaseModel):
    """Relationship extraction result."""
    document_id: str
    relationships: List[RelationshipSchema]
    total_count: int
    extraction_time_seconds: float
    extractors_used: List[str]


class KnowledgeExtractionStatistics(BaseModel):
    """Knowledge extraction statistics."""
    document_id: str
    entity_count: int
    unique_entity_count: int
    relationship_count: int
    entity_types: Dict[str, int]
    relationship_types: Dict[str, int]
    confidence_distribution: Dict[str, int]
    duplicate_count: int
    extraction_time_seconds: float


class ExtractionStatusResponse(BaseModel):
    """Extraction status response."""
    document_id: str
    entities_extracted: bool
    relationships_extracted: bool
    entity_count: int
    relationship_count: int
    last_extraction_time: Optional[datetime] = None
    extraction_duration_seconds: Optional[float] = None


# ============================================================================
# Database Model Schemas (for CRUD operations)
# ============================================================================

class EntityCreate(BaseModel):
    """Schema for creating entity."""
    entity_id: str
    entity_type: EntityType
    name: str
    normalized_name: str
    confidence_score: float = 0.7
    source_document_id: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    paragraph: Optional[int] = None
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    entity_metadata: Optional[Dict[str, Any]] = None


class EntityUpdate(BaseModel):
    """Schema for updating entity."""
    normalized_name: Optional[str] = None
    confidence_score: Optional[float] = None
    entity_metadata: Optional[Dict[str, Any]] = None


class EntityAliasCreate(BaseModel):
    """Schema for creating entity alias."""
    entity_id: str
    alias: str


class EntityOccurrenceCreate(BaseModel):
    """Schema for creating entity occurrence."""
    entity_id: str
    source_document_id: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    paragraph: Optional[int] = None
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    context_text: Optional[str] = None


class RelationshipCreate(BaseModel):
    """Schema for creating relationship."""
    relationship_id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: RelationshipType
    confidence_score: float = 0.7
    source_document_id: str
    page_number: Optional[int] = None
    paragraph: Optional[int] = None
    evidence_text: Optional[str] = None


class RelationshipUpdate(BaseModel):
    """Schema for updating relationship."""
    confidence_score: Optional[float] = None
    evidence_text: Optional[str] = None


class RelationshipEvidenceCreate(BaseModel):
    """Schema for creating relationship evidence."""
    relationship_id: str
    source_document_id: str
    page_number: Optional[int] = None
    paragraph: Optional[int] = None
    sentence: Optional[int] = None
    evidence_text: Optional[str] = None
    confidence_score: float = 0.7


# ============================================================================
# Internal Schemas for Extractors
# ============================================================================

class ExtractedEntity(BaseModel):
    """Internal schema for extracted entity before normalization."""
    name: str
    entity_type: EntityType
    confidence_score: float = 0.7
    page_number: Optional[int] = None
    section: Optional[str] = None
    paragraph: Optional[int] = None
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    context: Optional[str] = None
    extraction_method: ExtractionMethod = ExtractionMethod.RULE_BASED
    metadata: Optional[Dict[str, Any]] = None


class ExtractedRelationship(BaseModel):
    """Internal schema for extracted relationship before normalization."""
    source_entity_name: str
    target_entity_name: str
    source_entity_type: EntityType
    target_entity_type: EntityType
    relationship_type: RelationshipType
    confidence_score: float = 0.7
    page_number: Optional[int] = None
    paragraph: Optional[int] = None
    evidence_text: Optional[str] = None
    extraction_method: ExtractionMethod = ExtractionMethod.RULE_BASED
    metadata: Optional[Dict[str, Any]] = None


class ExtractionContext(BaseModel):
    """Context for extraction operations."""
    document_id: str
    text: str
    paragraphs: List[Dict[str, Any]] = Field(default_factory=list)
    sections: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None


class ExtractionResult(BaseModel):
    """Result from an extractor."""
    entities: List[ExtractedEntity] = Field(default_factory=list)
    relationships: List[ExtractedRelationship] = Field(default_factory=list)
    extraction_time_seconds: float
    extractor_name: str
    success: bool
    error_message: Optional[str] = None
