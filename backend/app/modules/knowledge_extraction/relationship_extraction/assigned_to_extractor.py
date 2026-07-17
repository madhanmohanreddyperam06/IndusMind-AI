"""ASSIGNED_TO relationship extractor."""
from typing import List
from app.modules.knowledge_extraction.relationship_extraction.base_relationship_extractor import BaseRelationshipExtractor
from app.modules.knowledge_extraction.schemas import ExtractedRelationship, ExtractionContext
from app.modules.knowledge_extraction.enums import RelationshipType, EntityType, ExtractionMethod


class AssignedToExtractor(BaseRelationshipExtractor):
    """Extractor for ASSIGNED_TO relationships (WorkOrder -> Person)."""
    
    def get_relationship_type(self) -> RelationshipType:
        return RelationshipType.ASSIGNED_TO
    
    def get_extraction_method(self) -> ExtractionMethod:
        return ExtractionMethod.RULE_BASED
    
    def extract(self, context: ExtractionContext, entities: List) -> List[ExtractedRelationship]:
        """Extract ASSIGNED_TO relationships."""
        relationships = []
        text = context.text.lower()
        
        # Get work order and person entities
        work_order_entities = [e for e in entities if e.entity_type == EntityType.WORK_ORDER]
        person_entities = [e for e in entities if e.entity_type == EntityType.PERSON]
        
        for work_order in work_order_entities:
            for person in person_entities:
                if self._are_related(work_order, person, text, context):
                    relationship = ExtractedRelationship(
                        source_entity_name=work_order.name,
                        target_entity_name=person.name,
                        source_entity_type=work_order.entity_type,
                        target_entity_type=person.entity_type,
                        relationship_type=RelationshipType.ASSIGNED_TO,
                        confidence_score=0.7,
                        page_number=work_order.page_number,
                        paragraph=work_order.paragraph,
                        evidence_text=self._get_evidence_text(context, work_order, person),
                        extraction_method=self.get_extraction_method()
                    )
                    
                    if self.validate_relationship(relationship):
                        relationships.append(relationship)
        
        return relationships
    
    def _are_related(self, work_order, person, text: str, context: ExtractionContext) -> bool:
        """Check if work order and person are related."""
        if hasattr(work_order, 'start_offset') and hasattr(person, 'start_offset'):
            distance = abs(work_order.start_offset - person.start_offset)
            if distance > 500:
                return False
        
        window = self._get_window_text(text, work_order, person)
        relationship_keywords = ['assigned to', 'allocated to', 'given to', 'assigned for']
        if any(keyword in window for keyword in relationship_keywords):
            return True
        
        return True
    
    def _get_window_text(self, text: str, work_order, person, window_size: int = 200) -> str:
        """Get text window around entities."""
        if not hasattr(work_order, 'start_offset') or not hasattr(person, 'start_offset'):
            return ""
        start = min(work_order.start_offset, person.start_offset)
        end = max(work_order.start_offset, person.start_offset)
        start = max(0, start - window_size)
        end = min(len(text), end + window_size)
        return text[start:end]
    
    def _get_evidence_text(self, context: ExtractionContext, work_order, person) -> str:
        """Get evidence text for the relationship."""
        if hasattr(work_order, 'context') and work_order.context:
            return work_order.context
        if hasattr(person, 'context') and person.context:
            return person.context
        return ""
