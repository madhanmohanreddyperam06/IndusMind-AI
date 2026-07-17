"""CAUSED_BY relationship extractor."""
from typing import List
from app.modules.knowledge_extraction.relationship_extraction.base_relationship_extractor import BaseRelationshipExtractor
from app.modules.knowledge_extraction.schemas import ExtractedRelationship, ExtractionContext
from app.modules.knowledge_extraction.enums import RelationshipType, EntityType, ExtractionMethod


class CausedByExtractor(BaseRelationshipExtractor):
    """Extractor for CAUSED_BY relationships (Failure -> Cause)."""
    
    def get_relationship_type(self) -> RelationshipType:
        return RelationshipType.CAUSED_BY
    
    def get_extraction_method(self) -> ExtractionMethod:
        return ExtractionMethod.RULE_BASED
    
    def extract(self, context: ExtractionContext, entities: List) -> List[ExtractedRelationship]:
        """Extract CAUSED_BY relationships."""
        relationships = []
        text = context.text.lower()
        
        # Get failure and cause entities
        failure_entities = [e for e in entities if e.entity_type == EntityType.FAILURE]
        cause_entities = [e for e in entities if e.entity_type == EntityType.CAUSE]
        
        for failure in failure_entities:
            for cause in cause_entities:
                if self._are_related(failure, cause, text, context):
                    relationship = ExtractedRelationship(
                        source_entity_name=failure.name,
                        target_entity_name=cause.name,
                        source_entity_type=failure.entity_type,
                        target_entity_type=cause.entity_type,
                        relationship_type=RelationshipType.CAUSED_BY,
                        confidence_score=0.7,
                        page_number=failure.page_number,
                        paragraph=failure.paragraph,
                        evidence_text=self._get_evidence_text(context, failure, cause),
                        extraction_method=self.get_extraction_method()
                    )
                    
                    if self.validate_relationship(relationship):
                        relationships.append(relationship)
        
        return relationships
    
    def _are_related(self, failure, cause, text: str, context: ExtractionContext) -> bool:
        """Check if failure and cause are related."""
        if hasattr(failure, 'start_offset') and hasattr(cause, 'start_offset'):
            distance = abs(failure.start_offset - cause.start_offset)
            if distance > 500:
                return False
        
        window = self._get_window_text(text, failure, cause)
        relationship_keywords = ['caused by', 'due to', 'because of', 'result of']
        if any(keyword in window for keyword in relationship_keywords):
            return True
        
        return True
    
    def _get_window_text(self, text: str, failure, cause, window_size: int = 200) -> str:
        """Get text window around entities."""
        if not hasattr(failure, 'start_offset') or not hasattr(cause, 'start_offset'):
            return ""
        start = min(failure.start_offset, cause.start_offset)
        end = max(failure.start_offset, cause.start_offset)
        start = max(0, start - window_size)
        end = min(len(text), end + window_size)
        return text[start:end]
    
    def _get_evidence_text(self, context: ExtractionContext, failure, cause) -> str:
        """Get evidence text for the relationship."""
        if hasattr(failure, 'context') and failure.context:
            return failure.context
        if hasattr(cause, 'context') and cause.context:
            return cause.context
        return ""
