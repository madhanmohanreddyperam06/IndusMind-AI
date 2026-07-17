"""Base entity extractor for plugin architecture."""
from abc import ABC, abstractmethod
from typing import List, Optional
import time
import uuid
from app.modules.knowledge_extraction.schemas import (
    ExtractedEntity,
    ExtractionContext,
    ExtractionResult
)
from app.modules.knowledge_extraction.enums import EntityType, ExtractionMethod
from app.modules.knowledge_extraction.exceptions import EntityExtractionException


class BaseEntityExtractor(ABC):
    """Abstract base class for entity extractors.
    
    All entity extractors must inherit from this class and implement
    the extract method. This enables the plugin architecture.
    """
    
    def __init__(self):
        """Initialize the extractor."""
        self.extractor_name = self.__class__.__name__
        self.enabled = True
    
    @abstractmethod
    def get_entity_type(self) -> EntityType:
        """Return the entity type this extractor handles.
        
        Returns:
            EntityType: The entity type
        """
        pass
    
    @abstractmethod
    def extract(self, context: ExtractionContext) -> List[ExtractedEntity]:
        """Extract entities from the given context.
        
        Args:
            context: Extraction context containing document text and metadata
            
        Returns:
            List of extracted entities
            
        Raises:
            EntityExtractionException: If extraction fails
        """
        pass
    
    def get_extraction_method(self) -> ExtractionMethod:
        """Return the extraction method used by this extractor.
        
        Returns:
            ExtractionMethod: The extraction method
        """
        return ExtractionMethod.RULE_BASED
    
    def extract_with_result(self, context: ExtractionContext) -> ExtractionResult:
        """Extract entities and return a structured result.
        
        Args:
            context: Extraction context
            
        Returns:
            ExtractionResult with entities and metadata
        """
        start_time = time.time()
        entities = []
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
            
            entities = self.extract(context)
            
        except Exception as e:
            success = False
            error_message = str(e)
            # Log error but don't raise - allow other extractors to continue
            print(f"Error in {self.extractor_name}: {error_message}")
            
        extraction_time = time.time() - start_time
        
        return ExtractionResult(
            entities=entities,
            extraction_time_seconds=extraction_time,
            extractor_name=self.extractor_name,
            success=success,
            error_message=error_message
        )
    
    def validate_entity(self, entity: ExtractedEntity) -> bool:
        """Validate an extracted entity.
        
        Args:
            entity: The entity to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not entity.name or not entity.name.strip():
            return False
        
        if entity.confidence_score < 0.0 or entity.confidence_score > 1.0:
            return False
        
        if not entity.entity_type:
            return False
        
        return True
    
    def normalize_entity_name(self, name: str) -> str:
        """Normalize entity name.
        
        Args:
            name: The entity name to normalize
            
        Returns:
            Normalized entity name
        """
        # Default normalization - strip whitespace and capitalize
        return name.strip().title()
    
    def calculate_confidence(self, entity: ExtractedEntity, context: ExtractionContext) -> float:
        """Calculate confidence score for an entity.
        
        Args:
            entity: The extracted entity
            context: Extraction context
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Default confidence - can be overridden by subclasses
        return entity.confidence_score
    
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
        return f"<{self.extractor_name}(entity_type={self.get_entity_type()}, enabled={self.enabled})>"
