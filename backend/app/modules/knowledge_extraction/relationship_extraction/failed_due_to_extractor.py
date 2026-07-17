"""FAILED_DUE_TO relationship extractor."""
from typing import List
from app.modules.knowledge_extraction.relationship_extraction.base_relationship_extractor import BaseRelationshipExtractor
from app.modules.knowledge_extraction.schemas import ExtractedRelationship, ExtractionContext
from app.modules.knowledge_extraction.enums import RelationshipType, EntityType, ExtractionMethod


class FailedDueToExtractor(BaseRelationshipExtractor):
    """Extractor for FAILED_DUE_TO relationships (Equipment -> Failure)."""
    
    def get_relationship_type(self) -> RelationshipType:
        return RelationshipType.FAILED_DUE_TO
    
    def get_extraction_method(self) -> ExtractionMethod:
        return ExtractionMethod.RULE_BASED
    
    def extract(self, context: ExtractionContext, entities: List) -> List[ExtractedRelationship]:
        """Extract FAILED_DUE_TO relationships."""
        relationships = []
        text = context.text.lower()
        
        # Get equipment and failure entities
        equipment_entities = [e for e in entities if e.entity_type == EntityType.EQUIPMENT]
        failure_entities = [e for e in entities if e.entity_type == EntityType.FAILURE]
        
        for equipment in equipment_entities:
            for failure in failure_entities:
                if self._are_related(equipment, failure, text, context):
                    relationship = ExtractedRelationship(
                        source_entity_name=equipment.name,
                        target_entity_name=failure.name,
                        source_entity_type=equipment.entity_type,
                        target_entity_type=failure.entity_type,
                        relationship_type=RelationshipType.FAILED_DUE_TO,
                        confidence_score=0.7,
                        page_number=equipment.page_number,
                        paragraph=equipment.paragraph,
                        evidence_text=self._get_evidence_text(context, equipment, failure),
                        extraction_method=self.get_extraction_method()
                    )
                    
                    if self.validate_relationship(relationship):
                        relationships.append(relationship)
        
        return relationships
    
    def _are_related(self, equipment, failure, text: str, context: ExtractionContext) -> bool:
        """Check if equipment and failure are related."""
        if hasattr(equipment, 'start_offset') and hasattr(failure, 'start_offset'):
            distance = abs(equipment.start_offset - failure.start_offset)
            if distance > 500:
                return False
        
        window = self._get_window_text(text, equipment, failure)
        relationship_keywords = ['failed due to', 'failure due to', 'because of', 'caused by']
        if any(keyword in window for keyword in relationship_keywords):
            return True
        
        return True
    
    def _get_window_text(self, text: str, equipment, failure, window_size: int = 200) -> str:
        """Get text window around entities."""
        if not hasattr(equipment, 'start_offset') or not hasattr(failure, 'start_offset'):
            return ""
        start = min(equipment.start_offset, failure.start_offset)
        end = max(equipment.start_offset, failure.start_offset)
        start = max(0, start - window_size)
        end = min(len(text), end + window_size)
        return text[start:end]
    
    def _get_evidence_text(self, context: ExtractionContext, equipment, failure) -> str:
        """Get evidence text for the relationship."""
        if hasattr(equipment, 'context') and equipment.context:
            return equipment.context
        if hasattr(failure, 'context') and failure.context:
            return failure.context
        return ""
