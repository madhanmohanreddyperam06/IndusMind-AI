"""Service layer for knowledge extraction."""
import time
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.modules.knowledge_extraction.orchestrator.entity_orchestrator import EntityExtractionOrchestrator
from app.modules.knowledge_extraction.orchestrator.relationship_orchestrator import RelationshipExtractionOrchestrator
from app.modules.knowledge_extraction.repository import KnowledgeExtractionRepository
from app.modules.knowledge_extraction.schemas import (
    ExtractedEntity,
    ExtractedRelationship,
    ExtractionContext,
    EntityCreate,
    RelationshipCreate,
    EntityExtractionResult,
    RelationshipExtractionResult,
    KnowledgeExtractionStatistics,
    ExtractionStatusResponse
)
from app.modules.knowledge_extraction.exceptions import (
    DocumentNotFoundException,
    ProcessedDocumentNotFoundException,
    KnowledgeExtractionException
)
from app.modules.document.repository import DocumentRepository
from app.modules.document_processing.repository import ProcessedDocumentRepository
from app.core.logging import setup_logging

logger = setup_logging()


class KnowledgeExtractionService:
    """Service for knowledge extraction operations."""
    
    def __init__(self, db: Session):
        """Initialize the service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.repository = KnowledgeExtractionRepository(db)
        self.document_repository = DocumentRepository(db)
        self.processed_document_repository = ProcessedDocumentRepository(db)
        self.entity_orchestrator = EntityExtractionOrchestrator()
        self.relationship_orchestrator = RelationshipExtractionOrchestrator()
    
    def _get_processed_document(self, document_id: str):
        """Get processed document for extraction.
        
        Args:
            document_id: Document ID
            
        Returns:
            Processed document
            
        Raises:
            DocumentNotFoundException: If document not found
            ProcessedDocumentNotFoundException: If processed document not found
        """
        # Check if document exists
        document = self.document_repository.get_document_by_id(document_id)
        if not document:
            raise DocumentNotFoundException(f"Document {document_id} not found")
        
        # Get processed document
        processed_doc = self.processed_document_repository.get_by_document_id(document_id)
        if not processed_doc:
            raise ProcessedDocumentNotFoundException(
                f"Processed document for {document_id} not found. "
                "Please process the document first."
            )
        
        return processed_doc
    
    def _create_extraction_context(self, document_id: str, processed_doc) -> ExtractionContext:
        """Create extraction context from processed document.
        
        Args:
            document_id: Document ID
            processed_doc: Processed document
            
        Returns:
            Extraction context
        """
        # Build paragraphs list
        paragraphs = []
        if processed_doc.paragraphs:
            for para in processed_doc.paragraphs:
                paragraphs.append({
                    "text": para.text,
                    "page_number": para.page_number,
                    "start_offset": para.start_offset,
                    "end_offset": para.end_offset
                })
        
        # Build sections list
        sections = []
        if processed_doc.sections:
            for section in processed_doc.sections:
                sections.append({
                    "title": section.title,
                    "level": section.level,
                    "start_offset": section.start_offset,
                    "end_offset": section.end_offset
                })
        
        return ExtractionContext(
            document_id=document_id,
            text=processed_doc.normalized_text or processed_doc.raw_text or "",
            paragraphs=paragraphs,
            sections=sections,
            metadata={
                "file_type": processed_doc.file_type,
                "page_count": processed_doc.page_count
            }
        )
    
    def _persist_entities(
        self,
        document_id: str,
        extracted_entities: List[ExtractedEntity]
    ) -> List[str]:
        """Persist extracted entities to database.
        
        Args:
            document_id: Document ID
            extracted_entities: List of extracted entities
            
        Returns:
            List of entity IDs
        """
        entity_ids = []
        
        for extracted in extracted_entities:
            # Check if entity already exists
            existing = self.repository.get_entity_by_name_and_type(
                extracted.normalized_name,
                extracted.entity_type
            )
            
            if existing:
                # Add occurrence
                self.repository.create_entity_occurrence(
                    EntityOccurrenceCreate(
                        entity_id=existing.entity_id,
                        source_document_id=document_id,
                        page_number=extracted.page_number,
                        section=extracted.section,
                        paragraph=extracted.paragraph,
                        start_offset=extracted.start_offset,
                        end_offset=extracted.end_offset,
                        context_text=extracted.context
                    )
                )
                entity_ids.append(existing.entity_id)
            else:
                # Create new entity
                entity_id = str(uuid.uuid4())
                entity = EntityCreate(
                    entity_id=entity_id,
                    entity_type=extracted.entity_type,
                    name=extracted.name,
                    normalized_name=extracted.normalized_name,
                    confidence_score=extracted.confidence_score,
                    source_document_id=document_id,
                    page_number=extracted.page_number,
                    section=extracted.section,
                    paragraph=extracted.paragraph,
                    start_offset=extracted.start_offset,
                    end_offset=extracted.end_offset,
                    entity_metadata=extracted.metadata
                )
                
                self.repository.create_entity(entity)
                
                # Add occurrence
                self.repository.create_entity_occurrence(
                    EntityOccurrenceCreate(
                        entity_id=entity_id,
                        source_document_id=document_id,
                        page_number=extracted.page_number,
                        section=extracted.section,
                        paragraph=extracted.paragraph,
                        start_offset=extracted.start_offset,
                        end_offset=extracted.end_offset,
                        context_text=extracted.context
                    )
                )
                
                entity_ids.append(entity_id)
        
        return entity_ids
    
    def _persist_relationships(
        self,
        document_id: str,
        extracted_relationships: List[ExtractedRelationship],
        entity_name_to_id: Dict[str, str]
    ) -> List[str]:
        """Persist extracted relationships to database.
        
        Args:
            document_id: Document ID
            extracted_relationships: List of extracted relationships
            entity_name_to_id: Mapping of entity names to IDs
            
        Returns:
            List of relationship IDs
        """
        relationship_ids = []
        
        for extracted in extracted_relationships:
            # Get source and target entity IDs
            source_id = entity_name_to_id.get(extracted.source_entity_name.lower())
            target_id = entity_name_to_id.get(extracted.target_entity_name.lower())
            
            if not source_id or not target_id:
                logger.warning(
                    f"Could not find entity IDs for relationship: "
                    f"{extracted.source_entity_name} -> {extracted.target_entity_name}"
                )
                continue
            
            # Create relationship
            relationship_id = str(uuid.uuid4())
            relationship = RelationshipCreate(
                relationship_id=relationship_id,
                source_entity_id=source_id,
                target_entity_id=target_id,
                relationship_type=extracted.relationship_type,
                confidence_score=extracted.confidence_score,
                source_document_id=document_id,
                page_number=extracted.page_number,
                paragraph=extracted.paragraph,
                evidence_text=extracted.evidence_text
            )
            
            self.repository.create_relationship(relationship)
            relationship_ids.append(relationship_id)
        
        return relationship_ids
    
    def extract_entities(
        self,
        document_id: str,
        force_reextract: bool = False,
        extractors: Optional[List[str]] = None
    ) -> EntityExtractionResult:
        """Extract entities from a document.
        
        Args:
            document_id: Document ID
            force_reextract: Whether to force re-extraction
            extractors: Specific extractors to run
            
        Returns:
            Entity extraction result
        """
        start_time = time.time()
        
        # Get processed document
        processed_doc = self._get_processed_document(document_id)
        
        # Check if already extracted
        if not force_reextract:
            existing_entities = self.repository.get_entities_by_document(document_id)
            if existing_entities:
                logger.info(f"Document {document_id} already has {len(existing_entities)} entities")
                # Convert to schema format
                from app.modules.knowledge_extraction.schemas import EntitySchema
                entity_schemas = [EntitySchema.model_validate(e) for e in existing_entities]
                return EntityExtractionResult(
                    document_id=document_id,
                    entities=entity_schemas,
                    total_count=len(existing_entities),
                    extraction_time_seconds=0.0,
                    extractors_used=[]
                )
        
        # Create extraction context
        context = self._create_extraction_context(document_id, processed_doc)
        
        # Run entity extraction
        extracted_entities = self.entity_orchestrator.extract(context)
        
        # Persist entities
        entity_ids = self._persist_entities(document_id, extracted_entities)
        
        extraction_time = time.time() - start_time
        
        logger.info(
            f"Entity extraction completed for {document_id}: "
            f"{len(extracted_entities)} entities extracted, {len(entity_ids)} persisted"
        )
        
        # Convert to schema format for response
        from app.modules.knowledge_extraction.schemas import EntitySchema
        entity_schemas = []
        for entity in extracted_entities:
            entity_schema = EntitySchema(
                entity_id=str(uuid.uuid4()),  # Will be replaced by actual ID from DB
                entity_type=entity.entity_type,
                name=entity.name,
                normalized_name=entity.normalized_name,
                confidence_score=entity.confidence_score,
                source_document_id=document_id,
                page_number=entity.page_number,
                section=entity.section,
                paragraph=entity.paragraph,
                start_offset=entity.start_offset,
                end_offset=entity.end_offset,
                entity_metadata=entity.metadata,
                created_at=datetime.utcnow(),
                aliases=[]
            )
            entity_schemas.append(entity_schema)
        
        return EntityExtractionResult(
            document_id=document_id,
            entities=entity_schemas,
            total_count=len(extracted_entities),
            extraction_time_seconds=extraction_time,
            extractors_used=[e.extractor_name for e in self.entity_orchestrator.get_all_extractors()]
        )
    
    def extract_relationships(
        self,
        document_id: str,
        force_reextract: bool = False,
        relationship_types: Optional[List[str]] = None
    ) -> RelationshipExtractionResult:
        """Extract relationships from a document.
        
        Args:
            document_id: Document ID
            force_reextract: Whether to force re-extraction
            relationship_types: Specific relationship types to extract
            
        Returns:
            Relationship extraction result
        """
        start_time = time.time()
        
        # Get processed document
        processed_doc = self._get_processed_document(document_id)
        
        # Get existing entities
        entities = self.repository.get_entities_by_document(document_id)
        if not entities:
            raise KnowledgeExtractionException(
                f"No entities found for document {document_id}. "
                "Please extract entities first."
            )
        
        # Check if already extracted
        if not force_reextract:
            existing_relationships = self.repository.get_relationships_by_document(document_id)
            if existing_relationships:
                logger.info(f"Document {document_id} already has {len(existing_relationships)} relationships")
                # Convert to schema format
                from app.modules.knowledge_extraction.schemas import RelationshipSchema
                relationship_schemas = [RelationshipSchema.model_validate(r) for r in existing_relationships]
                return RelationshipExtractionResult(
                    document_id=document_id,
                    relationships=relationship_schemas,
                    total_count=len(existing_relationships),
                    extraction_time_seconds=0.0,
                    extractors_used=[]
                )
        
        # Create extraction context
        context = self._create_extraction_context(document_id, processed_doc)
        
        # Run relationship extraction
        extracted_relationships = self.relationship_orchestrator.extract(context, entities)
        
        # Build entity name to ID mapping
        entity_name_to_id = {e.normalized_name.lower(): e.entity_id for e in entities}
        
        # Persist relationships
        relationship_ids = self._persist_relationships(
            document_id,
            extracted_relationships,
            entity_name_to_id
        )
        
        extraction_time = time.time() - start_time
        
        logger.info(
            f"Relationship extraction completed for {document_id}: "
            f"{len(extracted_relationships)} relationships extracted, {len(relationship_ids)} persisted"
        )
        
        # Convert to schema format for response
        from app.modules.knowledge_extraction.schemas import RelationshipSchema
        relationship_schemas = []
        for rel in extracted_relationships:
            relationship_schema = RelationshipSchema(
                relationship_id=str(uuid.uuid4()),  # Will be replaced by actual ID from DB
                source_entity_id=entity_name_to_id.get(rel.source_entity_name.lower(), ""),
                target_entity_id=entity_name_to_id.get(rel.target_entity_name.lower(), ""),
                relationship_type=rel.relationship_type,
                confidence_score=rel.confidence_score,
                source_document_id=document_id,
                page_number=rel.page_number,
                paragraph=rel.paragraph,
                evidence_text=rel.evidence_text,
                created_at=datetime.utcnow()
            )
            relationship_schemas.append(relationship_schema)
        
        return RelationshipExtractionResult(
            document_id=document_id,
            relationships=relationship_schemas,
            total_count=len(extracted_relationships),
            extraction_time_seconds=extraction_time,
            extractors_used=[e.extractor_name for e in self.relationship_orchestrator.get_all_extractors()]
        )
    
    def process_document(
        self,
        document_id: str,
        force_reextract: bool = False
    ) -> Dict[str, Any]:
        """Run full knowledge extraction pipeline.
        
        Args:
            document_id: Document ID
            force_reextract: Whether to force re-extraction
            
        Returns:
            Dictionary with extraction results
        """
        start_time = time.time()
        
        # Extract entities
        entity_result = self.extract_entities(document_id, force_reextract)
        
        # Extract relationships
        relationship_result = self.extract_relationships(document_id, force_reextract)
        
        total_time = time.time() - start_time
        
        logger.info(
            f"Full knowledge extraction completed for {document_id}: "
            f"{entity_result.total_count} entities, {relationship_result.total_count} relationships"
        )
        
        return {
            "document_id": document_id,
            "entities_extracted": entity_result.total_count,
            "relationships_extracted": relationship_result.total_count,
            "entity_extraction_time": entity_result.extraction_time_seconds,
            "relationship_extraction_time": relationship_result.extraction_time_seconds,
            "total_extraction_time": total_time
        }
    
    def get_entities(self, document_id: str) -> List:
        """Get all entities for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            List of entities in schema format
        """
        entities = self.repository.get_entities_by_document(document_id)
        from app.modules.knowledge_extraction.schemas import EntitySchema
        return [EntitySchema.model_validate(e) for e in entities]
    
    def get_relationships(self, document_id: str) -> List:
        """Get all relationships for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            List of relationships in schema format
        """
        relationships = self.repository.get_relationships_by_document(document_id)
        from app.modules.knowledge_extraction.schemas import RelationshipSchema
        return [RelationshipSchema.model_validate(r) for r in relationships]
    
    def get_statistics(self, document_id: str) -> KnowledgeExtractionStatistics:
        """Get extraction statistics for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            Extraction statistics
        """
        entity_stats = self.repository.get_entity_statistics(document_id)
        relationship_stats = self.repository.get_relationship_statistics(document_id)
        
        return KnowledgeExtractionStatistics(
            document_id=document_id,
            entity_count=entity_stats["total_entities"],
            unique_entity_count=entity_stats["unique_entities"],
            relationship_count=relationship_stats["total_relationships"],
            entity_types=entity_stats["entity_types"],
            relationship_types=relationship_stats["relationship_types"],
            confidence_distribution={
                "entities": entity_stats["confidence_distribution"],
                "relationships": relationship_stats["confidence_distribution"]
            },
            duplicate_count=entity_stats["total_entities"] - entity_stats["unique_entities"],
            extraction_time_seconds=0.0
        )
    
    def get_extraction_status(self, document_id: str) -> ExtractionStatusResponse:
        """Get extraction status for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            Extraction status
        """
        entities = self.repository.get_entities_by_document(document_id)
        relationships = self.repository.get_relationships_by_document(document_id)
        
        return ExtractionStatusResponse(
            document_id=document_id,
            entities_extracted=len(entities) > 0,
            relationships_extracted=len(relationships) > 0,
            entity_count=len(entities),
            relationship_count=len(relationships),
            last_extraction_time=None,
            extraction_duration_seconds=None
        )
    
    def delete_extraction(self, document_id: str) -> bool:
        """Delete all extraction data for a document.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if deleted
        """
        # Delete relationships
        self.repository.delete_relationships_by_document(document_id)
        
        # Delete entities
        self.repository.delete_entities_by_document(document_id)
        
        logger.info(f"Deleted extraction data for document {document_id}")
        return True
