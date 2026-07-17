"""Knowledge extraction module for entity and relationship extraction."""
from app.modules.knowledge_extraction.enums import EntityType, RelationshipType, ConfidenceLevel, ExtractionMethod
from app.modules.knowledge_extraction.constants import (
    ENTITY_TYPE_LABELS,
    RELATIONSHIP_TYPE_LABELS,
    CONFIDENCE_THRESHOLD_HIGH,
    CONFIDENCE_THRESHOLD_MEDIUM,
    CONFIDENCE_THRESHOLD_LOW,
    DEFAULT_CONFIDENCE_SCORE
)
from app.modules.knowledge_extraction.exceptions import (
    KnowledgeExtractionException,
    EntityExtractionException,
    RelationshipExtractionException,
    NormalizationException,
    DeduplicationException,
    OrchestratorException,
    ExtractorLoadException,
    ExtractorExecutionException,
    ModelLoadException,
    DictionaryLoadException,
    PatternCompilationException,
    ConfidenceScoreException,
    DocumentNotFoundException,
    ProcessedDocumentNotFoundException
)
from app.modules.knowledge_extraction.models import (
    Entity,
    EntityAlias,
    EntityOccurrence,
    Relationship,
    RelationshipEvidence
)
from app.modules.knowledge_extraction.schemas import (
    EntitySchema,
    EntityAliasSchema,
    EntityOccurrenceSchema,
    RelationshipSchema,
    RelationshipEvidenceSchema,
    ExtractEntitiesRequest,
    ExtractRelationshipsRequest,
    ProcessKnowledgeExtractionRequest,
    EntityExtractionResult,
    RelationshipExtractionResult,
    KnowledgeExtractionStatistics,
    ExtractionStatusResponse,
    EntityCreate,
    EntityUpdate,
    EntityAliasCreate,
    EntityOccurrenceCreate,
    RelationshipCreate,
    RelationshipUpdate,
    RelationshipEvidenceCreate,
    ExtractedEntity,
    ExtractedRelationship,
    ExtractionContext,
    ExtractionResult
)
from app.modules.knowledge_extraction.orchestrator.entity_orchestrator import EntityExtractionOrchestrator
from app.modules.knowledge_extraction.orchestrator.relationship_orchestrator import RelationshipExtractionOrchestrator
from app.modules.knowledge_extraction.repository import KnowledgeExtractionRepository
from app.modules.knowledge_extraction.service import KnowledgeExtractionService

__all__ = [
    # Enums
    'EntityType',
    'RelationshipType',
    'ConfidenceLevel',
    'ExtractionMethod',
    
    # Constants
    'ENTITY_TYPE_LABELS',
    'RELATIONSHIP_TYPE_LABELS',
    'CONFIDENCE_THRESHOLD_HIGH',
    'CONFIDENCE_THRESHOLD_MEDIUM',
    'CONFIDENCE_THRESHOLD_LOW',
    'DEFAULT_CONFIDENCE_SCORE',
    
    # Exceptions
    'KnowledgeExtractionException',
    'EntityExtractionException',
    'RelationshipExtractionException',
    'NormalizationException',
    'DeduplicationException',
    'OrchestratorException',
    'ExtractorLoadException',
    'ExtractorExecutionException',
    'ModelLoadException',
    'DictionaryLoadException',
    'PatternCompilationException',
    'ConfidenceScoreException',
    'DocumentNotFoundException',
    'ProcessedDocumentNotFoundException',
    
    # Models
    'Entity',
    'EntityAlias',
    'EntityOccurrence',
    'Relationship',
    'RelationshipEvidence',
    
    # Schemas
    'EntitySchema',
    'EntityAliasSchema',
    'EntityOccurrenceSchema',
    'RelationshipSchema',
    'RelationshipEvidenceSchema',
    'ExtractEntitiesRequest',
    'ExtractRelationshipsRequest',
    'ProcessKnowledgeExtractionRequest',
    'EntityExtractionResult',
    'RelationshipExtractionResult',
    'KnowledgeExtractionStatistics',
    'ExtractionStatusResponse',
    'EntityCreate',
    'EntityUpdate',
    'EntityAliasCreate',
    'EntityOccurrenceCreate',
    'RelationshipCreate',
    'RelationshipUpdate',
    'RelationshipEvidenceCreate',
    'ExtractedEntity',
    'ExtractedRelationship',
    'ExtractionContext',
    'ExtractionResult',
    
    # Orchestrators
    'EntityExtractionOrchestrator',
    'RelationshipExtractionOrchestrator',
    
    # Repository
    'KnowledgeExtractionRepository',
    
    # Service
    'KnowledgeExtractionService',
]
