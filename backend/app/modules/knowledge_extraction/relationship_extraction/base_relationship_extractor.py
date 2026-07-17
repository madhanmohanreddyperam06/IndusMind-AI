"""Base relationship extractor for plugin architecture."""
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import time
from app.modules.knowledge_extraction.schemas import (
    ExtractedRelationship,
    ExtractionContext,
    ExtractionResult
)
from app.modules.knowledge_extraction.enums import RelationshipType, ExtractionMethod
from app.modules.knowledge_extraction.exceptions import RelationshipExtractionException


class BaseRelationshipExtractor(ABC):
    """Abstract base class for relationship extractors.
    
    All relationship extractors must inherit from this class and implement
    the extract method. This enables the plugin architecture.
    """
    
    def __init__(self):
        """Initialize the extractor."""
        self.extractor_name = self.__class__.__name__
        self.enabled = True
    
    @abstractmethod
    def get_relationship_type(self) -> RelationshipType:
        """Return the relationship type this extractor handles.
        
        Returns:
            RelationshipType: The relationship type
        """
        pass
    
    @abstractmethod
    def extract(self, context: ExtractionContext, entities: List) -> List[ExtractedRelationship]:
        """Extract relationships from the given context.
        
        Args:
            context: Extraction context containing document text and metadata
            entities: List of extracted entities to find relationships between
            
        Returns:
            List of extracted relationships
            
        Raises:
            RelationshipExtractionException: If extraction fails
        """
        pass
    
    def get_extraction_method(self) -> ExtractionMethod:
        """Return the extraction method used by this extractor.
        
        Returns:
            ExtractionMethod: The extraction method
        """
        return ExtractionMethod.RULE_BASED
    
    def extract_with_result(
        self,
        context: ExtractionContext,
        entities: List
    ) -> ExtractionResult:
        """Extract relationships and return a structured result.
        
        Args:
            context: Extraction context
            entities: List of extracted entities
            
        Returns:
            ExtractionResult with relationships and metadata
        """
        start_time = time.time()
        relationships = []
        success = True
        error_message = None
        
        try:
            if not self.enabled:
                return ExtractionResult(
                    entities=[],
                    extraction_time_seconds=0.0,
                    extractor_name=self.extractor_name,
                    success=True,
                    error_message="Extractor is disabled"
                )
            
            relationships = self.extract(context, entities)
            
        except Exception as e:
            success = False
            error_message = str(e)
            # Log error but don't raise - allow other extractors to continue
            print(f"Error in {self.extractor_name}: {error_message}")
            
        extraction_time = time.time() - start_time
        
        return ExtractionResult(
            entities=relationships,  # Relationships stored in entities field for compatibility
            extraction_time_seconds=extraction_time,
            extractor_name=self.extractor_name,
            success=success,
            error_message=error_message
        )
    
    def validate_relationship(self, relationship: ExtractedRelationship) -> bool:
        """Validate an extracted relationship.
        
        Args:
            relationship: The relationship to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not relationship.source_entity_name or not relationship.source_entity_name.strip():
            return False
        
        if not relationship.target_entity_name or not relationship.target_entity_name.strip():
            return False
        
        if not relationship.relationship_type:
            return False
        
        if relationship.confidence_score < 0.0 or relationship.confidence_score > 1.0:
            return False
        
        return True
    
    def find_entity_by_name(
        self,
        name: str,
        entities: List,
        entity_type: Optional = None
    ) -> Optional:
        """Find an entity by name.
        
        Args:
            name: Entity name to search for
            entities: List of entities to search
            entity_type: Optional entity type filter
            
        Returns:
            Entity if found, None otherwise
        """
        for entity in entities:
            if entity_type and entity.entity_type != entity_type:
                continue
            
            if entity.name.lower() == name.lower():
                return entity
            
            # Check normalized name
            if hasattr(entity, 'normalized_name') and entity.normalized_name.lower() == name.lower():
                return entity
        
        return None
    
    def find_entities_in_window(
        self,
        offset: int,
        window_size: int,
        entities: List
    ) -> List:
        """Find entities within a text window.
        
        Args:
            offset: Text offset
            window_size: Window size in characters
            entities: List of entities
            
        Returns:
            List of entities within the window
        """
        window_entities = []
        
        for entity in entities:
            if not hasattr(entity, 'start_offset') or not hasattr(entity, 'end_offset'):
                continue
            
            if abs(entity.start_offset - offset) <= window_size:
                window_entities.append(entity)
        
        return window_entities
    
    def calculate_confidence(
        self,
        relationship: ExtractedRelationship,
        context: str
    ) -> float:
        """Calculate confidence score for a relationship.
        
        Args:
            relationship: The extracted relationship
            context: Context text
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Default confidence - can be overridden by subclasses
        return relationship.confidence_score
    
    def enable(self):
        """Enable this extractor."""
        self.enabled = True
    
    def disable(self):
        """Disable this extractor."""
        self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if this extractor is enabled.
        
        Returns:
            True if enabled, False otherwise
        """
        return self.enabled
    
    def __repr__(self):
        return f"<{self.extractor_name}(relationship_type={self.get_relationship_type()}, enabled={self.enabled})>"
