"""PERFORMED_BY relationship extractor."""
from typing import List
from app.modules.knowledge_extraction.relationship_extraction.base_relationship_extractor import BaseRelationshipExtractor
from app.modules.knowledge_extraction.schemas import ExtractedRelationship, ExtractionContext
from app.modules.knowledge_extraction.enums import RelationshipType, EntityType, ExtractionMethod


class PerformedByExtractor(BaseRelationshipExtractor):
    """Extractor for PERFORMED_BY relationships (Maintenance -> Person)."""
    
    def get_relationship_type(self) -> RelationshipType:
        return RelationshipType.PERFORMED_BY
    
    def get_extraction_method(self) -> ExtractionMethod:
        return ExtractionMethod.RULE_BASED
    
    def extract(self, context: ExtractionContext, entities: List) -> List[ExtractedRelationship]:
        """Extract PERFORMED_BY relationships."""
        relationships = []
        text = context.text.lower()
        
        # Get maintenance and person entities
        maintenance_entities = [e for e in entities if e.entity_type == EntityType.MAINTENANCE_ACTIVITY]
        person_entities = [e for e in entities if e.entity_type == EntityType.PERSON]
        
        for maintenance in maintenance_entities:
            for person in person_entities:
                if self._are_related(maintenance, person, text, context):
                    relationship = ExtractedRelationship(
                        source_entity_name=maintenance.name,
                        target_entity_name=person.name,
                        source_entity_type=maintenance.entity_type,
                        target_entity_type=person.entity_type,
                        relationship_type=RelationshipType.PERFORMED_BY,
                        confidence_score=0.7,
                        page_number=maintenance.page_number,
                        paragraph=maintenance.paragraph,
                        evidence_text=self._get_evidence_text(context, maintenance, person),
                        extraction_method=self.get_extraction_method()
                    )
                    
                    if self.validate_relationship(relationship):
                        relationships.append(relationship)
        
        return relationships
    
    def _are_related(self, maintenance, person, text: str, context: ExtractionContext) -> bool:
        """Check if maintenance and person are related."""
        if hasattr(maintenance, 'start_offset') and hasattr(person, 'start_offset'):
            distance = abs(maintenance.start_offset - person.start_offset)
            if distance > 500:
                return False
        
        window = self._get_window_text(text, maintenance, person)
        relationship_keywords = ['performed by', 'carried out by', 'done by', 'conducted by']
        if any(keyword in window for keyword in relationship_keywords):
            return True
        
        return True
    
    def _get_window_text(self, text: str, maintenance, person, window_size: int = 200) -> str:
        """Get text window around entities."""
        if not hasattr(maintenance, 'start_offset') or not hasattr(person, 'start_offset'):
            return ""
        start = min(maintenance.start_offset, person.start_offset)
        end = max(maintenance.start_offset, person.start_offset)
        start = max(0, start - window_size)
        end = min(len(text), end + window_size)
        return text[start:end]
    
    def _get_evidence_text(self, context: ExtractionContext, maintenance, person) -> str:
        """Get evidence text for the relationship."""
        if hasattr(maintenance, 'context') and maintenance.context:
            return maintenance.context
        if hasattr(person, 'context') and person.context:
            return person.context
        return ""
